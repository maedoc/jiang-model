"""
Extended DDE model for geopolitical resource dynamics with variable regions.
"""

import jax
import jax.numpy as jnp
from jax import vmap
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List
import json

# Constants (can be overridden)
DT = 1.0  # time step (days)
TOTAL_DAYS = 365
N_STEPS = int(TOTAL_DAYS / DT)


class GeopoliticalDDE:
    def __init__(self, n_regions: int, state_dim: int = 3):
        self.n_regions = n_regions
        self.state_dim = state_dim  # O, F, S per region (can be extended)
        self.params = None

    def set_parameters(self, params: Dict):
        """Set model parameters."""
        # Ensure arrays have correct shape
        required_keys = [
            "oil_production",
            "oil_consumption",
            "fertilizer_production",
            "fertilizer_consumption",
            "stability_decay",
            "stability_gain",
            "oil_trade_flow",
            "fertilizer_trade_flow",
            "stability_coupling",
        ]
        for key in required_keys:
            if key not in params:
                raise ValueError(f"Missing parameter: {key}")
        self.params = params

    def region_name(self, idx: int) -> str:
        """Return region name if available."""
        if hasattr(self, "region_names") and idx < len(self.region_names):
            return self.region_names[idx]
        return f"Region {idx}"

    def base_delay(self) -> float:
        """Base shipping delay in days."""
        return 30.0

    def choke_point_multiplier(self) -> float:
        """Additional days per unit disruption."""
        return 7.0

    def compute_hormuz_disruption(
        self, t: float, disruption_day: float = 100.0
    ) -> float:
        """
        Compute Hormuz disruption factor as a function of time.
        disruption_day: day when disruption event occurs.
        Returns disruption factor between 0 (normal) and 1 (max disruption).
        """
        ramp = jnp.minimum(1.0, (t - disruption_day) / 10.0)
        return jnp.where(t < disruption_day, 0.0, 0.8 * ramp)

    def compute_delay(self, disruption: float) -> float:
        """Compute delay in days given disruption factor."""
        return self.base_delay() + self.choke_point_multiplier() * disruption

    def local_dynamics(self, state: jnp.ndarray, region_idx: int) -> jnp.ndarray:
        """
        Local dynamics F_i(x_i) for region i.
        state: array of length STATE_DIM (O, F, S)
        Returns derivative d(state)/dt.
        """
        O, F, S = state
        # Parameters
        oil_production = self.params["oil_production"][region_idx]
        oil_consumption = self.params["oil_consumption"][region_idx]
        fertilizer_production = self.params["fertilizer_production"][region_idx]
        fertilizer_consumption = self.params["fertilizer_consumption"][region_idx]
        stability_decay = self.params["stability_decay"][region_idx]
        stability_gain = self.params["stability_gain"][region_idx]

        # Oil: production minus consumption, modulated by stability
        dO = oil_production * S - oil_consumption
        # Fertilizer: similar
        dF = fertilizer_production * S - fertilizer_consumption
        # Political stability: decays naturally, gains from resource abundance
        resource_abundance = jnp.tanh(0.01 * (O + F))
        dS = -stability_decay * S + stability_gain * resource_abundance * (1 - S)

        return jnp.array([dO, dF, dS])

    def coupling_term(
        self,
        state_i: jnp.ndarray,
        state_j_delayed: jnp.ndarray,
        region_i: int,
        region_j: int,
    ) -> jnp.ndarray:
        """
        Coupling term G_ij(x_i, x_j(t - τ)).
        Models trade flow from region j to i.
        """
        # Trade flow coefficients (units per day) from exporter j to importer i
        oil_trade_flow = self.params["oil_trade_flow"][region_i, region_j]
        fertilizer_trade_flow = self.params["fertilizer_trade_flow"][region_i, region_j]
        # Stability influence
        stability_coupling = self.params["stability_coupling"][region_i, region_j]

        O_j, F_j, S_j = state_j_delayed
        O_i, F_i, S_i = state_i

        # Oil trade: direct flow modulated by exporter stability
        dO = oil_trade_flow * S_j

        # Fertilizer trade similar
        dF = fertilizer_trade_flow * S_j

        # Stability coupling: influenced by partner's stability
        dS = stability_coupling * (S_j - S_i) * S_i * (1 - S_i)

        return jnp.array([dO, dF, dS])

    def dde_system(
        self,
        state_flat: jnp.ndarray,
        t: float,
        history: jnp.ndarray,
        delay_steps: int,
    ) -> jnp.ndarray:
        """
        Compute derivative of the full system.
        state_flat: flattened array of shape (n_regions * state_dim,)
        t: current time (days)
        history: array of shape (delay_steps, n_regions * state_dim) containing past states
        delay_steps: number of steps corresponding to current delay
        Returns derivative flattened array.
        """
        # Reshape to (n_regions, state_dim)
        state = state_flat.reshape(self.n_regions, self.state_dim)

        # Compute current Hormuz disruption and delay
        disruption = self.compute_hormuz_disruption(t)
        delay_days = self.compute_delay(disruption)
        # Convert delay to steps (rounded down)
        delay_steps_float = delay_days / DT
        delay_steps_int = jnp.floor(delay_steps_float).astype(jnp.int32)
        current_delay_steps = jnp.minimum(delay_steps, delay_steps_int)

        # Retrieve delayed states from history
        delayed_state_flat = history[-current_delay_steps, :]
        delayed_state = delayed_state_flat.reshape(self.n_regions, self.state_dim)

        derivative = jnp.zeros_like(state)

        # For each region, compute local dynamics plus coupling from all others
        for i in range(self.n_regions):
            local = self.local_dynamics(state[i], i)
            derivative = derivative.at[i].add(local)

            for j in range(self.n_regions):
                if i == j:
                    continue
                coupling = self.coupling_term(state[i], delayed_state[j], i, j)
                derivative = derivative.at[i].add(coupling)

        return derivative.flatten()

    def euler_step(
        self,
        state_flat: jnp.ndarray,
        t: float,
        history: jnp.ndarray,
        delay_steps: int,
    ) -> jnp.ndarray:
        """One Euler step."""
        deriv = self.dde_system(state_flat, t, history, delay_steps)
        return state_flat + DT * deriv

    def simulate(
        self, initial_state: jnp.ndarray, disruption_day: float = 100.0
    ) -> Tuple[jnp.ndarray, jnp.ndarray]:
        """
        Run simulation using jax.lax.scan.
        Returns:
            states: array of shape (N_STEPS, n_regions * state_dim)
            times: array of shape (N_STEPS,)
        """
        # Override disruption day
        self.compute_hormuz_disruption = lambda t: self._compute_hormuz_disruption(
            t, disruption_day
        )

        # Maximum possible delay steps (for history buffer size)
        max_delay_days = self.compute_delay(1.0)  # maximum disruption = 1
        max_delay_steps = int(max_delay_days / DT) + 10  # safety margin

        # Initialize history buffer as a rolling window
        # We'll store the last max_delay_steps states
        history_shape = (max_delay_steps, self.n_regions * self.state_dim)
        # Fill history with initial state for t < 0
        history = jnp.tile(initial_state, (max_delay_steps, 1))

        def step(carry, t):
            state_flat, history = carry
            # Update history: shift and add current state
            history = jnp.roll(history, shift=-1, axis=0)
            history = history.at[-1].set(state_flat)

            # Compute next state
            next_state = self.euler_step(state_flat, t, history, max_delay_steps)

            return (next_state, history), next_state

        # Times array
        times = jnp.arange(0, TOTAL_DAYS, DT)

        # Run scan
        (final_state, final_history), states = jax.lax.scan(
            step, (initial_state, history), times
        )

        # Include initial state at time 0
        states = jnp.vstack([initial_state, states[:-1]])

        return states, times

    def _compute_hormuz_disruption(self, t: float, disruption_day: float) -> float:
        """Internal wrapper for disruption day."""
        ramp = jnp.minimum(1.0, (t - disruption_day) / 10.0)
        return jnp.where(t < disruption_day, 0.0, 0.8 * ramp)


def load_parameters_from_json(filename: str) -> Dict:
    """Load parameters from JSON file and convert to JAX arrays."""
    with open(filename, "r") as f:
        params_dict = json.load(f)
    params = {}
    for key, value in params_dict.items():
        params[key] = jnp.array(value)
    return params


def plot_results(
    states: jnp.ndarray,
    times: jnp.ndarray,
    n_regions: int,
    region_names: List[str] = None,
    save_prefix="real_simulation",
):
    """Plot simulation results."""
    states_reshaped = states.reshape(-1, n_regions, 3)

    # Plot oil levels over time
    plt.figure(figsize=(14, 10))

    # Oil subplot
    plt.subplot(3, 1, 1)
    for i in range(n_regions):
        label = region_names[i] if region_names else f"Region {i}"
        plt.plot(times, states_reshaped[:, i, 0], label=label, linewidth=2)
    plt.axvline(x=100, color="red", linestyle="--", alpha=0.5, label="Disruption event")
    plt.ylabel("Oil supply")
    plt.title("Geopolitical Resource Dynamics - Oil Supply Over Time (Real Data)")
    plt.legend(ncol=3, fontsize="small")
    plt.grid(True, alpha=0.3)

    # Fertilizer subplot
    plt.subplot(3, 1, 2)
    for i in range(n_regions):
        plt.plot(times, states_reshaped[:, i, 1], linewidth=2)
    plt.axvline(x=100, color="red", linestyle="--", alpha=0.5)
    plt.ylabel("Fertilizer supply")
    plt.grid(True, alpha=0.3)

    # Political stability subplot
    plt.subplot(3, 1, 3)
    for i in range(n_regions):
        plt.plot(times, states_reshaped[:, i, 2], linewidth=2)
    plt.axvline(x=100, color="red", linestyle="--", alpha=0.5)
    plt.ylabel("Political stability (0-1)")
    plt.xlabel("Time (days)")
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f"{save_prefix}_resources.png", dpi=150)
    plt.close()

    # Plot Hormuz disruption and delay
    disruptions = vmap(
        lambda t: jnp.where(t < 100, 0.0, 0.8 * jnp.minimum(1.0, (t - 100) / 10.0))
    )(times)
    delays = 30.0 + 7.0 * disruptions

    plt.figure(figsize=(10, 6))
    plt.subplot(2, 1, 1)
    plt.plot(times, disruptions, "b-", linewidth=2)
    plt.axvline(x=100, color="red", linestyle="--", alpha=0.5)
    plt.ylabel("Hormuz disruption factor")
    plt.title("Choke Point Dynamics")
    plt.grid(True, alpha=0.3)

    plt.subplot(2, 1, 2)
    plt.plot(times, delays, "g-", linewidth=2)
    plt.axvline(x=100, color="red", linestyle="--", alpha=0.5)
    plt.ylabel("Shipping delay (days)")
    plt.xlabel("Time (days)")
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f"{save_prefix}_choke_point.png", dpi=150)
    plt.close()

    print(
        f"Plots saved as {save_prefix}_resources.png and {save_prefix}_choke_point.png"
    )


def main():
    """Run simulation with real-world parameters."""
    # Load parameters
    params = load_parameters_from_json("real_params.json")
    n_regions = len(params["oil_production"])

    # Create model instance
    model = GeopoliticalDDE(n_regions=n_regions, state_dim=3)
    model.set_parameters(params)

    # Define region names (from data_loader)
    from data_loader import REGIONS

    model.region_names = REGIONS

    # Initial conditions: assume proportional to production
    initial_state = []
    for i in range(n_regions):
        O_init = params["oil_production"][i] * 2.0  # initial stock = 2 days production
        F_init = params["fertilizer_production"][i] * 2.0
        S_init = 0.7  # starting stability
        initial_state.extend([O_init, F_init, S_init])
    initial_state = jnp.array(initial_state)

    print("Running simulation with real-world data...")
    states, times = model.simulate(initial_state, disruption_day=100.0)

    # Plot results
    plot_results(
        states, times, n_regions, region_names=REGIONS, save_prefix="real_simulation"
    )

    # Print final values
    states_reshaped = states.reshape(-1, n_regions, 3)
    print("\nFinal oil levels:")
    for i in range(n_regions):
        final_oil = states_reshaped[-1, i, 0]
        print(f"  {model.region_name(i)}: {final_oil:.1f}")

    print("\nFinal political stability:")
    for i in range(n_regions):
        final_stab = states_reshaped[-1, i, 2]
        print(f"  {model.region_name(i)}: {final_stab:.3f}")


if __name__ == "__main__":
    main()
