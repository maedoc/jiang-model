"""
Stable ODE model for geopolitical resource dynamics with logarithmic scaling.
No delays, uses scipy.integrate.solve_ivp for robust integration.
"""

import numpy as np
import jax.numpy as jnp
import matplotlib.pyplot as plt
from typing import Dict, Tuple
import json
from scipy.integrate import solve_ivp

# Constants
EPS = 1e-8  # small constant to avoid division by zero
K_HALF = 1000.0  # half-saturation constant for trade limitation


def load_parameters(filename="real_params.json"):
    """Load parameters from JSON and convert to numpy arrays."""
    with open(filename, "r") as f:
        params_dict = json.load(f)
    params = {}
    for key, value in params_dict.items():
        params[key] = np.array(value, dtype=np.float64)
    return params


def log_transform(x):
    """Transform positive variable to log space: L = log(1 + x)."""
    return np.log1p(x)


def exp_transform(L):
    """Inverse transform: x = exp(L) - 1."""
    return np.expm1(L)


class ODEModel:
    def __init__(self, params: Dict):
        self.params = params
        self.n_regions = len(params["oil_production"])
        self.region_names = [
            "North America",
            "Europe",
            "Russia",
            "Middle East",
            "China",
            "India",
            "Japan",
            "Southeast Asia",
            "Australia/New Zealand",
            "Africa (sub-Saharan)",
            "South America",
            "Central Asia/Caucasus",
        ]

    def region_name(self, idx: int) -> str:
        return self.region_names[idx]

    def compute_hormuz_disruption(
        self, t: float, disruption_day: float = 100.0
    ) -> float:
        """Compute Hormuz disruption factor as a function of time."""
        if t < disruption_day:
            return 0.0
        ramp = min(1.0, (t - disruption_day) / 10.0)
        return 0.8 * ramp

    def system(self, t: float, y: np.ndarray) -> np.ndarray:
        """
        ODE system in log-transformed variables.
        y shape: (n_regions * 3,) where for each region: [log_oil, log_fert, stability]
        Returns derivative dy/dt.
        """
        n = self.n_regions
        # Extract state variables
        log_oil = y[0:n]
        log_fert = y[n : 2 * n]
        S = y[2 * n : 3 * n]

        # Convert back to original units
        oil = exp_transform(log_oil)
        fert = exp_transform(log_fert)

        # Ensure non-negativity
        oil = np.maximum(oil, 0.0)
        fert = np.maximum(fert, 0.0)

        # Clip stability to [0,1] for production calculations
        S_clipped = np.clip(S, 0.0, 1.0)

        # Parameters
        oil_prod = self.params["oil_production"]
        oil_cons = self.params["oil_consumption"]
        fert_prod = self.params["fertilizer_production"]
        fert_cons = self.params["fertilizer_consumption"]
        stability_decay = self.params["stability_decay"]
        stability_gain = self.params["stability_gain"]
        oil_trade = self.params["oil_trade_flow"]  # shape (n, n), flow from j to i
        fert_trade = self.params["fertilizer_trade_flow"]
        stability_coupling = self.params["stability_coupling"]

        # Compute Hormuz disruption effect on trade (reduce flows from Middle East)
        disruption = self.compute_hormuz_disruption(t)
        # Middle East index = 3
        me_idx = 3
        oil_trade_disrupted = oil_trade.copy()
        fert_trade_disrupted = fert_trade.copy()
        # Reduce exports from Middle East by disruption factor
        oil_trade_disrupted[:, me_idx] *= 1 - disruption
        fert_trade_disrupted[:, me_idx] *= 1 - disruption

        # Scale down trade flows to prevent excessive fluxes
        trade_scale = 0.01
        oil_trade_disrupted *= trade_scale
        fert_trade_disrupted *= trade_scale

        # Compute derivatives in original units
        dOdt = np.zeros(n)
        dFdt = np.zeros(n)
        dSdt = np.zeros(n)

        for i in range(n):
            # Local production minus consumption
            # Add baseline production (50% of capacity) independent of stability
            baseline = 0.5
            prod_oil = oil_prod[i] * (baseline + (1 - baseline) * S_clipped[i])
            cons_oil = oil_cons[i]
            prod_fert = fert_prod[i] * (baseline + (1 - baseline) * S_clipped[i])
            cons_fert = fert_cons[i]

            dOdt[i] = prod_oil - cons_oil
            dFdt[i] = prod_fert - cons_fert

            # Trade contributions
            for j in range(n):
                if i == j:
                    continue
                # Oil flow from j to i: limited by exporter's available oil
                flow_oil = oil_trade_disrupted[i, j] * S_clipped[j]
                # Limiting factor based on exporter's oil stock
                limit = oil[j] / (oil[j] + K_HALF) if oil[j] > 0 else 0.0
                flow_oil *= limit

                dOdt[i] += flow_oil
                dOdt[j] -= flow_oil  # conservation

                # Fertilizer flow
                flow_fert = fert_trade_disrupted[i, j] * S_clipped[j]
                limit_fert = fert[j] / (fert[j] + K_HALF) if fert[j] > 0 else 0.0
                flow_fert *= limit_fert

                dFdt[i] += flow_fert
                dFdt[j] -= flow_fert

                # Stability coupling (use actual S, not clipped, for gradient)
                dSdt[i] += stability_coupling[i, j] * (S[j] - S[i]) * S[i] * (1 - S[i])

            # Local stability dynamics
            resource_abundance = np.tanh(0.01 * (oil[i] + fert[i]))
            dSdt[i] += -stability_decay[i] * S[i] + stability_gain[
                i
            ] * resource_abundance * (1 - S[i])

            # Soft bounds for stability: push back toward [0,1]
            if S[i] < 0:
                dSdt[i] += -10.0 * S[i]  # positive derivative when S negative
            elif S[i] > 1:
                dSdt[i] += -10.0 * (S[i] - 1)  # negative derivative when S > 1

        # Convert to log-space derivatives
        dlog_oil = dOdt / (1 + oil + EPS)
        dlog_fert = dFdt / (1 + fert + EPS)

        # Assemble full derivative vector
        dydt = np.concatenate([dlog_oil, dlog_fert, dSdt])
        return dydt

    def simulate(
        self, t_span=(0.0, 365.0), y0=None, method="BDF", rtol=1e-8, atol=1e-8
    ):
        """
        Solve ODE system using scipy.integrate.solve_ivp.

        Args:
            t_span: integration interval (days)
            y0: initial state in log-transformed units
            method: integration method
            rtol, atol: solver tolerances

        Returns:
            sol: solution object from solve_ivp
        """
        if y0 is None:
            # Default initial conditions: oil and fertilizer stocks proportional to production
            oil0 = (
                self.params["oil_production"] * 10.0
            )  # 10 days of production as stock
            fert0 = self.params["fertilizer_production"] * 10.0
            S0 = np.clip(
                self.params.get("political_stability", np.ones(self.n_regions) * 0.7),
                0.0,
                1.0,
            )
            # Transform to log space
            log_oil0 = log_transform(oil0)
            log_fert0 = log_transform(fert0)
            y0 = np.concatenate([log_oil0, log_fert0, S0])

        # Solve ODE
        sol = solve_ivp(
            fun=lambda t, y: self.system(t, y),
            t_span=t_span,
            y0=y0,
            method=method,
            rtol=rtol,
            atol=atol,
            dense_output=True,
        )

        return sol

    def plot_results(self, sol, figsize=(14, 10)):
        """Plot simulation results."""
        t = sol.t
        y = sol.y

        n = self.n_regions
        log_oil = y[0:n, :]
        log_fert = y[n : 2 * n, :]
        S = y[2 * n : 3 * n, :]

        # Convert back to original units
        oil = exp_transform(log_oil)
        fert = exp_transform(log_fert)

        fig, axes = plt.subplots(3, 1, figsize=figsize, sharex=True)

        # Oil plot
        ax = axes[0]
        for i in range(n):
            ax.plot(t, oil[i], label=self.region_name(i), linewidth=1.5, alpha=0.8)
        ax.axvline(x=100, color="red", linestyle="--", alpha=0.5, label="Disruption")
        ax.set_ylabel("Oil stock (units)")
        ax.set_title("Oil Stocks Over Time")
        ax.legend(ncol=3, fontsize="small")
        ax.grid(True, alpha=0.3)

        # Fertilizer plot
        ax = axes[1]
        for i in range(n):
            ax.plot(t, fert[i], label=self.region_name(i), linewidth=1.5, alpha=0.8)
        ax.axvline(x=100, color="red", linestyle="--", alpha=0.5)
        ax.set_ylabel("Fertilizer stock (units)")
        ax.legend(ncol=3, fontsize="small")
        ax.grid(True, alpha=0.3)

        # Stability plot
        ax = axes[2]
        for i in range(n):
            ax.plot(t, S[i], label=self.region_name(i), linewidth=1.5, alpha=0.8)
        ax.axvline(x=100, color="red", linestyle="--", alpha=0.5)
        ax.set_ylabel("Political stability (0-1)")
        ax.set_xlabel("Time (days)")
        ax.legend(ncol=3, fontsize="small")
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig("ode_stable_results.png", dpi=150)
        plt.show()

        # Also plot total resources
        fig, axes = plt.subplots(2, 1, figsize=(12, 8))
        ax = axes[0]
        total_oil = oil.sum(axis=0)
        total_fert = fert.sum(axis=0)
        ax.plot(t, total_oil, "b-", label="Total oil", linewidth=2)
        ax.plot(t, total_fert, "g-", label="Total fertilizer", linewidth=2)
        ax.axvline(x=100, color="red", linestyle="--", alpha=0.5)
        ax.set_ylabel("Total resource stock")
        ax.set_title("Global Resource Conservation")
        ax.legend()
        ax.grid(True, alpha=0.3)

        ax = axes[1]
        ax.plot(t, total_oil - total_oil[0], "b--", label="Oil change", linewidth=2)
        ax.plot(
            t, total_fert - total_fert[0], "g--", label="Fertilizer change", linewidth=2
        )
        ax.axhline(y=0, color="black", linestyle="-", alpha=0.3)
        ax.axvline(x=100, color="red", linestyle="--", alpha=0.5)
        ax.set_ylabel("Change from initial")
        ax.set_xlabel("Time (days)")
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig("ode_global_resources.png", dpi=150)
        plt.show()

        return fig


def main():
    print("Loading real-world parameters...")
    params = load_parameters("real_params.json")

    print(f"Number of regions: {len(params['oil_production'])}")

    # Create model
    model = ODEModel(params)

    print("Running simulation with logarithmic scaling and conservation...")
    sol = model.simulate(t_span=(0.0, 100.0), method="BDF", rtol=1e-8, atol=1e-8)

    print(f"Integration successful: {sol.t.size} time points")
    print(f"Final time: {sol.t[-1]:.1f} days")

    # Plot results
    model.plot_results(sol)

    # Print final state summary
    n = model.n_regions
    y_final = sol.y[:, -1]
    log_oil_final = y_final[0:n]
    log_fert_final = y_final[n : 2 * n]
    S_final = y_final[2 * n : 3 * n]

    oil_final = exp_transform(log_oil_final)
    fert_final = exp_transform(log_fert_final)

    print("\nFinal state summary:")
    print(f"{'Region':<25} {'Oil':>10} {'Fert':>10} {'Stability':>10}")
    print("-" * 60)
    for i in range(n):
        print(
            f"{model.region_name(i):<25} {oil_final[i]:>10.2f} {fert_final[i]:>10.2f} {S_final[i]:>10.3f}"
        )

    print(
        f"\nTotal oil change: {oil_final.sum() - exp_transform(log_transform(params['oil_production'] * 10.0)).sum():.2f}"
    )
    print(
        f"Total fertilizer change: {fert_final.sum() - exp_transform(log_transform(params['fertilizer_production'] * 10.0)).sum():.2f}"
    )


if __name__ == "__main__":
    main()
