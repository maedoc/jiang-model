"""
Extended ODE model for geopolitical resource dynamics with water, military, inequality,
debt, price dynamics, and financial variables.
Uses logarithmic scaling for positive variables, logit for bounded variables.
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
    """Inverse transform: x = exp(L) - 1 with overflow protection."""
    L_clipped = np.clip(L, -100.0, 100.0)  # prevent overflow
    return np.expm1(L_clipped)


def logit_transform(p):
    """Transform bounded variable (0-1) to logit space."""
    # Clip to avoid exact 0 or 1
    p_clipped = np.clip(p, EPS, 1.0 - EPS)
    return np.log(p_clipped / (1.0 - p_clipped))


def inv_logit(L):
    """Inverse logit transform with overflow protection."""
    L_clipped = np.clip(L, -50.0, 50.0)  # exp(-50) ~ 1e-22, exp(50) ~ 5e21
    return 1.0 / (1.0 + np.exp(-L_clipped))


def sigmoid(x, k=1.0, x0=0.0):
    """Smooth sigmoid transition: 1/(1 + exp(-k*(x - x0)))"""
    return 1.0 / (1.0 + np.exp(-k * (x - x0)))


class ExtendedODEModel:
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
        # Define variable indices
        self.n_vars_per_region = 15
        # Map variable names to slice indices
        self.idx_log_oil = 0
        self.idx_log_fert = 1
        self.idx_stability = 2
        self.idx_log_water = 3
        self.idx_log_military = 4
        self.idx_logit_inequality = 5
        self.idx_log_debt = 6
        self.idx_log_price_oil = 7
        self.idx_log_price_fert = 8
        self.idx_log_price_water = 9
        self.idx_inflation = 10
        self.idx_interest = 11
        self.idx_log_exchange = 12
        self.idx_bond_yield = 13
        self.idx_log_exchange_avg = 14

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

    def extract_state(self, y: np.ndarray) -> Tuple:
        """Extract all state variables from flattened vector."""
        n = self.n_regions
        # Each variable block is of length n
        log_oil = y[self.idx_log_oil * n : (self.idx_log_oil + 1) * n]
        log_fert = y[self.idx_log_fert * n : (self.idx_log_fert + 1) * n]
        stability = y[self.idx_stability * n : (self.idx_stability + 1) * n]
        log_water = y[self.idx_log_water * n : (self.idx_log_water + 1) * n]
        log_military = y[self.idx_log_military * n : (self.idx_log_military + 1) * n]
        logit_inequality = y[
            self.idx_logit_inequality * n : (self.idx_logit_inequality + 1) * n
        ]
        log_debt = y[self.idx_log_debt * n : (self.idx_log_debt + 1) * n]
        log_price_oil = y[self.idx_log_price_oil * n : (self.idx_log_price_oil + 1) * n]
        log_price_fert = y[
            self.idx_log_price_fert * n : (self.idx_log_price_fert + 1) * n
        ]
        log_price_water = y[
            self.idx_log_price_water * n : (self.idx_log_price_water + 1) * n
        ]
        inflation = y[self.idx_inflation * n : (self.idx_inflation + 1) * n]
        interest = y[self.idx_interest * n : (self.idx_interest + 1) * n]
        log_exchange = y[self.idx_log_exchange * n : (self.idx_log_exchange + 1) * n]
        bond_yield = y[self.idx_bond_yield * n : (self.idx_bond_yield + 1) * n]
        log_exchange_avg = y[
            self.idx_log_exchange_avg * n : (self.idx_log_exchange_avg + 1) * n
        ]

        return (
            log_oil,
            log_fert,
            stability,
            log_water,
            log_military,
            logit_inequality,
            log_debt,
            log_price_oil,
            log_price_fert,
            log_price_water,
            inflation,
            interest,
            log_exchange,
            bond_yield,
            log_exchange_avg,
        )

    def system(self, t: float, y: np.ndarray) -> np.ndarray:
        """
        ODE system for extended model with nonlinear thresholds and financial coupling.
        y shape: (n_regions * n_vars_per_region,)
        Returns derivative dy/dt.
        """
        n = self.n_regions
        DAILY_SCALE = 1.0 / 365.25
        # Extract state variables
        (
            log_oil,
            log_fert,
            stability,
            log_water,
            log_military,
            logit_inequality,
            log_debt,
            log_price_oil,
            log_price_fert,
            log_price_water,
            inflation,
            interest,
            log_exchange,
            bond_yield,
            log_exchange_avg,
        ) = self.extract_state(y)

        # Convert transformed variables back to original units
        oil = exp_transform(log_oil)
        fert = exp_transform(log_fert)
        water = exp_transform(log_water)
        military = exp_transform(log_military)
        inequality = inv_logit(logit_inequality)
        debt = exp_transform(log_debt)
        price_oil = exp_transform(log_price_oil)
        price_fert = exp_transform(log_price_fert)
        price_water = exp_transform(log_price_water)
        exchange = exp_transform(log_exchange)
        exchange_avg = exp_transform(log_exchange_avg)

        # Clip stability for production calculations
        stability_clipped = np.clip(stability, 0.0, 1.0)

        # Parameters
        oil_prod = self.params["oil_production"]
        oil_cons = self.params["oil_consumption"]
        fert_prod = self.params["fertilizer_production"]
        fert_cons = self.params["fertilizer_consumption"]
        water_avail = self.params["water_availability"]
        water_cons = self.params["water_consumption"]
        stability_decay = self.params["stability_decay"]
        stability_gain = self.params["stability_gain"]
        oil_trade = self.params["oil_trade_flow"]
        fert_trade = self.params["fertilizer_trade_flow"]
        water_trade = self.params["water_trade_flow"]
        stability_coupling = self.params["stability_coupling"]
        capital_flow = self.params["capital_flow"]
        financial_coupling = self.params["financial_coupling"]
        debt_target = self.params["debt_to_gdp"]
        initial_water = water_avail * 10.0  # proxy for initial water stock

        # Compute Hormuz disruption effect on trade (reduce flows from Middle East)
        disruption = self.compute_hormuz_disruption(t)
        me_idx = 3  # Middle East index
        oil_trade_disrupted = oil_trade.copy()
        fert_trade_disrupted = fert_trade.copy()
        water_trade_disrupted = water_trade.copy()
        # Reduce exports from Middle East by disruption factor
        oil_trade_disrupted[:, me_idx] *= 1 - disruption
        fert_trade_disrupted[:, me_idx] *= 1 - disruption
        water_trade_disrupted[:, me_idx] *= 1 - disruption

        # Scale down trade flows to prevent excessive fluxes (as in stable model)
        trade_scale = 0.01
        oil_trade_disrupted *= trade_scale
        fert_trade_disrupted *= trade_scale
        water_trade_disrupted *= trade_scale

        # Initialize derivatives in original units
        dOdt = np.zeros(n)
        dFdt = np.zeros(n)
        dWdt = np.zeros(n)
        dSdt = np.zeros(n)
        dMdt = np.zeros(n)
        dIdt = np.zeros(n)  # inequality derivative (original units, 0-1)
        dDdt = np.zeros(n)  # debt derivative
        dPo_dt = np.zeros(n)  # oil price
        dPf_dt = np.zeros(n)  # fertilizer price
        dPw_dt = np.zeros(n)  # water price
        dInf_dt = np.zeros(n)  # inflation
        dInt_dt = np.zeros(n)  # interest rate
        dEx_dt = np.zeros(n)  # exchange rate
        dBy_dt = np.zeros(n)  # bond yield
        dExAvg_dt = np.zeros(n)  # exchange average

        # GDP proxy (used for debt dynamics)
        gdp = oil_prod * stability_clipped + fert_prod * stability_clipped
        gdp_scale = np.mean(gdp) if np.mean(gdp) > 0 else 1.0
        gdp = gdp / gdp_scale

        # Precompute nonlinear thresholds
        # 1. Debt crisis: debt > 100% GDP (debt > 1.0)
        debt_crisis = sigmoid(debt - 1.0, k=10.0, x0=0.0)  # smooth step
        # 2. Currency crisis: 30-day depreciation > 20%
        # Calculate depreciation relative to moving average
        depreciation = (exchange_avg - exchange) / (exchange_avg + EPS)
        currency_crisis = sigmoid(depreciation - 0.2, k=20.0, x0=0.0)
        # 3. Social unrest: inequality > 0.6 AND inflation > 0.1
        social_unrest = sigmoid(inequality - 0.6, k=10.0, x0=0.0) * sigmoid(
            inflation - 0.1, k=20.0, x0=0.0
        )
        # 4. Resource scarcity: water stock < 10% of initial
        water_scarcity = sigmoid(0.1 * initial_water - water, k=0.1, x0=0.0)

        # Compute resource derivatives with trade (similar to stable model)
        for i in range(n):
            # Local production minus consumption
            baseline = 0.5
            prod_oil = oil_prod[i] * (baseline + (1 - baseline) * stability_clipped[i])
            cons_oil = oil_cons[i]
            prod_fert = fert_prod[i] * (
                baseline + (1 - baseline) * stability_clipped[i]
            )
            cons_fert = fert_cons[i]
            prod_water = water_avail[i] * (
                baseline + (1 - baseline) * stability_clipped[i]
            )
            cons_water = water_cons[i]

            dOdt[i] = prod_oil - cons_oil
            dFdt[i] = prod_fert - cons_fert
            dWdt[i] = prod_water - cons_water

            # Trade contributions
            for j in range(n):
                if i == j:
                    continue
                # Oil flow from j to i: limited by exporter's available oil
                flow_oil = oil_trade_disrupted[i, j] * stability_clipped[j]
                limit = oil[j] / (oil[j] + K_HALF) if oil[j] > 0 else 0.0
                flow_oil *= limit
                dOdt[i] += flow_oil
                dOdt[j] -= flow_oil

                # Fertilizer flow
                flow_fert = fert_trade_disrupted[i, j] * stability_clipped[j]
                limit_fert = fert[j] / (fert[j] + K_HALF) if fert[j] > 0 else 0.0
                flow_fert *= limit_fert
                dFdt[i] += flow_fert
                dFdt[j] -= flow_fert

                # Water flow
                flow_water = water_trade_disrupted[i, j] * stability_clipped[j]
                limit_water = water[j] / (water[j] + K_HALF) if water[j] > 0 else 0.0
                flow_water *= limit_water
                dWdt[i] += flow_water
                dWdt[j] -= flow_water

                # Stability coupling
                dSdt[i] += (
                    stability_coupling[i, j]
                    * (stability[j] - stability[i])
                    * stability[i]
                    * (1 - stability[i])
                )

                # Financial coupling: capital flows affect exchange rates
                # capital_flow[i,j] is flow from j to i (positive means capital inflow to i)
                # Exchange rate increase (depreciation) when capital outflow
                dEx_dt[i] += capital_flow[i, j] * (exchange[j] - exchange[i]) * 0.001
                # Interest rate coupling
                dInt_dt[i] += (
                    financial_coupling[i, j] * (interest[j] - interest[i]) * 0.01
                )

            # Local stability dynamics
            resource_abundance = np.tanh(0.01 * (oil[i] + fert[i] + water[i]))
            dSdt[i] += -stability_decay[i] * stability[i] + stability_gain[
                i
            ] * resource_abundance * (1 - stability[i])
            # Social unrest reduces stability gain
            dSdt[i] -= social_unrest[i] * 0.1 * stability[i]

            # Soft bounds for stability: push back toward [0,1]
            if stability[i] < 0:
                dSdt[i] += -10.0 * stability[i]
            elif stability[i] > 1:
                dSdt[i] += -10.0 * (stability[i] - 1)

            # Military expenditure dynamics
            # Military grows with GDP, decays with stability, reduced by debt crisis
            dMdt[i] = (
                0.01 * gdp[i] - 0.05 * military[i] - debt_crisis[i] * 0.1 * military[i]
            )

            # Inequality dynamics: increases with low stability, high debt
            dIdt[i] = (
                0.01 * (1 - stability_clipped[i])
                + 0.005 * debt[i]
                - 0.02 * inequality[i]
            )

            # Debt dynamics (based on debug_debt.py)
            gov_spending = military[i] * gdp[i] * 0.01
            tax_revenue = gdp[i] * 0.3 * stability_clipped[i]
            debt_ceiling = 2.0
            debt_clipped = np.clip(debt[i], -5.0, 10.0)
            austerity_factor = 1.0 / (
                1.0 + np.exp(10.0 * (debt_clipped - debt_ceiling))
            )
            gov_spending *= austerity_factor
            primary_deficit = gov_spending - tax_revenue
            growth_rate = 0.02 * stability_clipped[i] * DAILY_SCALE
            mean_reversion = 0.1 * (debt_target[i] - debt[i])
            dDdt[i] = (
                primary_deficit
                + (interest[i] * DAILY_SCALE - growth_rate) * debt[i]
                + mean_reversion
            )
            # Debt crisis adds risk premium to interest rate
            dInt_dt[i] += debt_crisis[i] * 0.02

            # Price dynamics: respond to supply-demand imbalance
            oil_balance = (oil_cons[i] - oil_prod[i]) / (
                oil_cons[i] + oil_prod[i] + EPS
            )
            fert_balance = (fert_cons[i] - fert_prod[i]) / (
                fert_cons[i] + fert_prod[i] + EPS
            )
            water_balance = (water_cons[i] - water_avail[i]) / (
                water_cons[i] + water_avail[i] + EPS
            )
            dPo_dt[i] = 0.01 * oil_balance - 0.05 * (price_oil[i] - 1.0)
            dPf_dt[i] = 0.01 * fert_balance - 0.05 * (price_fert[i] - 1.0)
            dPw_dt[i] = 0.01 * water_balance - 0.05 * (price_water[i] - 1.0)
            # Resource scarcity increases water price
            dPw_dt[i] += water_scarcity[i] * 0.1

            # Inflation: weighted average of price changes
            dInf_dt[i] = (
                0.3 * dPo_dt[i] / (price_oil[i] + EPS)
                + 0.3 * dPf_dt[i] / (price_fert[i] + EPS)
                + 0.4 * dPw_dt[i] / (price_water[i] + EPS)
            )

            # Interest rate: Taylor rule with target inflation 0.02
            neutral_rate = 0.03
            inflation_target = 0.02
            dInt_dt[i] += (
                0.5 * (neutral_rate - interest[i])
                + 1.5 * (inflation[i] - inflation_target)
                + 0.5 * (debt[i] - debt_target[i])
            )

            # Exchange rate: influenced by trade balance and capital flows
            trade_balance = (
                (oil_prod[i] - oil_cons[i])
                + (fert_prod[i] - fert_cons[i])
                + (water_avail[i] - water_cons[i])
            )
            dEx_dt[i] += 0.001 * trade_balance - 0.01 * (exchange[i] - 1.0)
            # Currency crisis triggers capital flight (increase outflow)
            dEx_dt[i] += currency_crisis[i] * 0.05 * exchange[i]

            # Bond yield: linked to interest rate plus risk premium
            dBy_dt[i] = 0.1 * (interest[i] + debt_crisis[i] * 0.02 - bond_yield[i])

            # Exchange average: moving average with 30-day time constant
            dExAvg_dt[i] = (exchange[i] - exchange_avg[i]) / 30.0

        # Convert derivatives of log-transformed variables
        dlog_oil = dOdt / (1 + oil + EPS)
        dlog_fert = dFdt / (1 + fert + EPS)
        dlog_water = dWdt / (1 + water + EPS)
        dlog_military = dMdt / (1 + military + EPS)
        # Inequality is logit-transformed: d(logit) = dI / (I*(1-I))
        dlogit_inequality = dIdt / (inequality * (1 - inequality) + EPS)
        dlog_debt = dDdt / (1 + debt + EPS)
        dlog_price_oil = dPo_dt / (1 + price_oil + EPS)
        dlog_price_fert = dPf_dt / (1 + price_fert + EPS)
        dlog_price_water = dPw_dt / (1 + price_water + EPS)
        # Inflation and interest are not transformed
        dlog_exchange = dEx_dt / (1 + exchange + EPS)
        dlog_exchange_avg = dExAvg_dt / (1 + exchange_avg + EPS)

        # Assemble full derivative vector
        dydt = np.concatenate(
            [
                dlog_oil,
                dlog_fert,
                dSdt,
                dlog_water,
                dlog_military,
                dlogit_inequality,
                dlog_debt,
                dlog_price_oil,
                dlog_price_fert,
                dlog_price_water,
                dInf_dt,
                dInt_dt,
                dlog_exchange,
                dBy_dt,
                dlog_exchange_avg,
            ]
        )
        return dydt

    def simulate(
        self, t_span=(0.0, 365.0), y0=None, method="BDF", rtol=1e-8, atol=1e-8
    ):
        """
        Solve ODE system using scipy.integrate.solve_ivp.

        Args:
            t_span: integration interval (days)
            y0: initial state in transformed units
            method: integration method
            rtol, atol: solver tolerances

        Returns:
            sol: solution object from solve_ivp
        """
        n = self.n_regions
        if y0 is None:
            # Default initial conditions
            oil0 = self.params["oil_production"] * 10.0
            fert0 = self.params["fertilizer_production"] * 10.0
            water0 = self.params["water_availability"] * 10.0
            military0 = self.params["military_expenditure"]
            inequality0 = self.params["inequality"]
            debt0 = self.params["debt_to_gdp"]
            price_oil0 = self.params["oil_price"]
            price_fert0 = self.params["fertilizer_price"]
            price_water0 = self.params["water_price"]
            inflation0 = self.params["inflation"]
            interest0 = self.params["interest_rate"]
            exchange0 = self.params["exchange_rate"]
            bond_yield0 = self.params["bond_yield"]
            exchange_avg0 = exchange0  # start equal to exchange

            # Transform to log/logit space
            log_oil0 = log_transform(oil0)
            log_fert0 = log_transform(fert0)
            log_water0 = log_transform(water0)
            log_military0 = log_transform(military0)
            logit_inequality0 = logit_transform(inequality0)
            log_debt0 = log_transform(debt0)
            log_price_oil0 = log_transform(price_oil0)
            log_price_fert0 = log_transform(price_fert0)
            log_price_water0 = log_transform(price_water0)
            log_exchange0 = log_transform(exchange0)
            log_exchange_avg0 = log_transform(exchange_avg0)
            stability0 = np.clip(
                self.params.get("political_stability", np.ones(n) * 0.7), 0.0, 1.0
            )

            y0 = np.concatenate(
                [
                    log_oil0,
                    log_fert0,
                    stability0,
                    log_water0,
                    log_military0,
                    logit_inequality0,
                    log_debt0,
                    log_price_oil0,
                    log_price_fert0,
                    log_price_water0,
                    inflation0,
                    interest0,
                    log_exchange0,
                    bond_yield0,
                    log_exchange_avg0,
                ]
            )

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

        # Extract state variables at each time point
        log_oil = y[self.idx_log_oil * n : (self.idx_log_oil + 1) * n, :]
        log_fert = y[self.idx_log_fert * n : (self.idx_log_fert + 1) * n, :]
        stability = y[self.idx_stability * n : (self.idx_stability + 1) * n, :]
        log_water = y[self.idx_log_water * n : (self.idx_log_water + 1) * n, :]
        log_military = y[self.idx_log_military * n : (self.idx_log_military + 1) * n, :]
        logit_inequality = y[
            self.idx_logit_inequality * n : (self.idx_logit_inequality + 1) * n, :
        ]
        log_debt = y[self.idx_log_debt * n : (self.idx_log_debt + 1) * n, :]
        log_price_oil = y[
            self.idx_log_price_oil * n : (self.idx_log_price_oil + 1) * n, :
        ]
        log_price_fert = y[
            self.idx_log_price_fert * n : (self.idx_log_price_fert + 1) * n, :
        ]
        log_price_water = y[
            self.idx_log_price_water * n : (self.idx_log_price_water + 1) * n, :
        ]
        inflation = y[self.idx_inflation * n : (self.idx_inflation + 1) * n, :]
        interest = y[self.idx_interest * n : (self.idx_interest + 1) * n, :]
        log_exchange = y[self.idx_log_exchange * n : (self.idx_log_exchange + 1) * n, :]
        bond_yield = y[self.idx_bond_yield * n : (self.idx_bond_yield + 1) * n, :]
        log_exchange_avg = y[
            self.idx_log_exchange_avg * n : (self.idx_log_exchange_avg + 1) * n, :
        ]

        # Convert back to original units
        oil = exp_transform(log_oil)
        fert = exp_transform(log_fert)
        water = exp_transform(log_water)
        military = exp_transform(log_military)
        inequality = inv_logit(logit_inequality)
        debt = exp_transform(log_debt)
        price_oil = exp_transform(log_price_oil)
        price_fert = exp_transform(log_price_fert)
        price_water = exp_transform(log_price_water)
        exchange = exp_transform(log_exchange)
        exchange_avg = exp_transform(log_exchange_avg)

        # Create figure with subplots for each variable (similar to original plotting code but without corruption)
        fig, axes = plt.subplots(7, 2, figsize=figsize, sharex=True)
        axes = axes.flatten()
        plot_idx = 0

        # Oil stocks
        ax = axes[plot_idx]
        for i in range(n):
            ax.plot(t, oil[i], label=self.region_name(i), linewidth=1, alpha=0.7)
        ax.axvline(x=100, color="red", linestyle="--", alpha=0.5, label="Disruption")
        ax.set_ylabel("Oil stock")
        ax.set_title("Oil Stocks")
        ax.legend(ncol=2, fontsize="x-small")
        ax.grid(True, alpha=0.3)
        plot_idx += 1

        # Fertilizer stocks
        ax = axes[plot_idx]
        for i in range(n):
            ax.plot(t, fert[i], linewidth=1, alpha=0.7)
        ax.axvline(x=100, color="red", linestyle="--", alpha=0.5)
        ax.set_ylabel("Fertilizer stock")
        ax.set_title("Fertilizer Stocks")
        ax.grid(True, alpha=0.3)
        plot_idx += 1

        # Water stocks
        ax = axes[plot_idx]
        for i in range(n):
            ax.plot(t, water[i], linewidth=1, alpha=0.7)
        ax.axvline(x=100, color="red", linestyle="--", alpha=0.5)
        ax.set_ylabel("Water stock")
        ax.set_title("Water Stocks")
        ax.grid(True, alpha=0.3)
        plot_idx += 1

        # Political stability
        ax = axes[plot_idx]
        for i in range(n):
            ax.plot(t, stability[i], linewidth=1, alpha=0.7)
        ax.axvline(x=100, color="red", linestyle="--", alpha=0.5)
        ax.set_ylabel("Political stability")
        ax.set_title("Political Stability")
        ax.grid(True, alpha=0.3)
        plot_idx += 1

        # Military expenditure
        ax = axes[plot_idx]
        for i in range(n):
            ax.plot(t, military[i], linewidth=1, alpha=0.7)
        ax.axvline(x=100, color="red", linestyle="--", alpha=0.5)
        ax.set_ylabel("Military expenditure")
        ax.set_title("Military Expenditure")
        ax.grid(True, alpha=0.3)
        plot_idx += 1

        # Inequality
        ax = axes[plot_idx]
        for i in range(n):
            ax.plot(t, inequality[i], linewidth=1, alpha=0.7)
        ax.axvline(x=100, color="red", linestyle="--", alpha=0.5)
        ax.set_ylabel("Inequality (Gini)")
        ax.set_title("Inequality")
        ax.grid(True, alpha=0.3)
        plot_idx += 1

        # Sovereign debt
        ax = axes[plot_idx]
        for i in range(n):
            ax.plot(t, debt[i], linewidth=1, alpha=0.7)
        ax.axvline(x=100, color="red", linestyle="--", alpha=0.5)
        ax.set_ylabel("Debt-to-GDP ratio")
        ax.set_title("Sovereign Debt")
        ax.grid(True, alpha=0.3)
        plot_idx += 1

        # Oil price
        ax = axes[plot_idx]
        for i in range(n):
            ax.plot(t, price_oil[i], linewidth=1, alpha=0.7)
        ax.axvline(x=100, color="red", linestyle="--", alpha=0.5)
        ax.set_ylabel("Oil price (USD)")
        ax.set_title("Oil Price")
        ax.grid(True, alpha=0.3)
        plot_idx += 1

        # Inflation
        ax = axes[plot_idx]
        for i in range(n):
            ax.plot(t, inflation[i], linewidth=1, alpha=0.7)
        ax.axvline(x=100, color="red", linestyle="--", alpha=0.5)
        ax.set_ylabel("Inflation rate")
        ax.set_title("Inflation")
        ax.grid(True, alpha=0.3)
        plot_idx += 1

        # Interest rate
        ax = axes[plot_idx]
        for i in range(n):
            ax.plot(t, interest[i], linewidth=1, alpha=0.7)
        ax.axvline(x=100, color="red", linestyle="--", alpha=0.5)
        ax.set_ylabel("Interest rate")
        ax.set_title("Interest Rates")
        ax.grid(True, alpha=0.3)
        plot_idx += 1

        # Exchange rate (relative to USD)
        ax = axes[plot_idx]
        for i in range(n):
            if i != 0:  # skip USD itself
                ax.plot(
                    t, exchange[i], linewidth=1, alpha=0.7, label=self.region_name(i)
                )
        ax.axvline(x=100, color="red", linestyle="--", alpha=0.5)
        ax.set_ylabel("Exchange rate (local per USD)")
        ax.set_title("Exchange Rates")
        ax.legend(ncol=2, fontsize="x-small")
        ax.grid(True, alpha=0.3)
        plot_idx += 1

        # Bond yield
        ax = axes[plot_idx]
        for i in range(n):
            ax.plot(t, bond_yield[i], linewidth=1, alpha=0.7)
        ax.axvline(x=100, color="red", linestyle="--", alpha=0.5)
        ax.set_ylabel("Bond yield")
        ax.set_title("Bond Yields")
        ax.grid(True, alpha=0.3)
        plot_idx += 1

        # Hide unused subplots
        for i in range(plot_idx, len(axes)):
            axes[i].set_visible(False)

        plt.tight_layout()
        plt.savefig("ode_extended_results.png", dpi=150)
        plt.show()

        # Also plot global aggregates
        fig2, axes2 = plt.subplots(2, 2, figsize=(12, 10))
        axes2 = axes2.flatten()

        axes2[0].plot(t, oil.sum(axis=0), "b-", label="Total oil")
        axes2[0].plot(t, fert.sum(axis=0), "g-", label="Total fertilizer")
        axes2[0].plot(t, water.sum(axis=0), "c-", label="Total water")
        axes2[0].axvline(x=100, color="red", linestyle="--", alpha=0.5)
        axes2[0].set_ylabel("Total resource stock")
        axes2[0].set_title("Global Resource Conservation")
        axes2[0].legend()
        axes2[0].grid(True, alpha=0.3)

        axes2[1].plot(t, stability.mean(axis=0), "r-", label="Avg stability")
        axes2[1].plot(t, inequality.mean(axis=0), "m-", label="Avg inequality")
        axes2[1].axvline(x=100, color="red", linestyle="--", alpha=0.5)
        axes2[1].set_ylabel("Index (0-1)")
        axes2[1].set_title("Average Political & Social Indicators")
        axes2[1].legend()
        axes2[1].grid(True, alpha=0.3)

        axes2[2].plot(t, price_oil.mean(axis=0), "b-", label="Avg oil price")
        axes2[2].plot(t, price_fert.mean(axis=0), "g-", label="Avg fertilizer price")
        axes2[2].axvline(x=100, color="red", linestyle="--", alpha=0.5)
        axes2[2].set_ylabel("Price (USD)")
        axes2[2].set_title("Average Commodity Prices")
        axes2[2].legend()
        axes2[2].grid(True, alpha=0.3)

        axes2[3].plot(t, debt.mean(axis=0), "r-", label="Avg debt")
        axes2[3].plot(t, bond_yield.mean(axis=0), "m-", label="Avg bond yield")
        axes2[3].axvline(x=100, color="red", linestyle="--", alpha=0.5)
        axes2[3].set_ylabel("Ratio / Yield")
        axes2[3].set_title("Average Financial Indicators")
        axes2[3].legend()
        axes2[3].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig("ode_extended_aggregates.png", dpi=150)
        plt.show()

        return fig, fig2


def main():
    print("Loading extended real-world parameters...")
    params = load_parameters("real_params.json")

    print(f"Number of regions: {len(params['oil_production'])}")
    print(f"Number of variables per region: 15")
    print(f"Total ODE dimension: {len(params['oil_production']) * 15}")

    # Create model
    model = ExtendedODEModel(params)

    print("Running simulation with extended model...")
    # Shorter time span for testing
    sol = model.simulate(t_span=(0.0, 10.0), method="BDF", rtol=1e-6, atol=1e-8)

    print(f"Integration successful: {sol.t.size} time points")
    print(f"Final time: {sol.t[-1]:.1f} days")

    # Plot results
    model.plot_results(sol)

    # Print final state summary for first few regions
    n = model.n_regions
    y_final = sol.y[:, -1]
    (
        log_oil_final,
        log_fert_final,
        stability_final,
        log_water_final,
        log_military_final,
        logit_inequality_final,
        log_debt_final,
        log_price_oil_final,
        log_price_fert_final,
        log_price_water_final,
        inflation_final,
        interest_final,
        log_exchange_final,
        bond_yield_final,
        log_exchange_avg_final,
    ) = model.extract_state(y_final)

    oil_final = exp_transform(log_oil_final)
    fert_final = exp_transform(log_fert_final)
    water_final = exp_transform(log_water_final)
    military_final = exp_transform(log_military_final)
    inequality_final = inv_logit(logit_inequality_final)
    debt_final = exp_transform(log_debt_final)
    price_oil_final = exp_transform(log_price_oil_final)
    price_fert_final = exp_transform(log_price_fert_final)
    price_water_final = exp_transform(log_price_water_final)
    exchange_final = exp_transform(log_exchange_final)
    exchange_avg_final = exp_transform(log_exchange_avg_final)

    print("\nFinal state summary (first 3 regions):")
    print(
        f"{'Region':<25} {'Oil':>8} {'Fert':>8} {'Water':>8} {'Stability':>10} {'Debt':>8}"
    )
    print("-" * 70)
    for i in range(min(3, n)):
        print(
            f"{model.region_name(i):<25} {oil_final[i]:>8.2f} {fert_final[i]:>8.2f} {water_final[i]:>8.2f} {stability_final[i]:>10.3f} {debt_final[i]:>8.3f}"
        )

    print("\nAverage values across all regions:")
    print(f"Oil price: {price_oil_final.mean():.2f} USD")
    print(f"Inflation: {inflation_final.mean():.4f}")
    print(f"Interest rate: {interest_final.mean():.4f}")
    print(f"Debt/GDP: {debt_final.mean():.3f}")


if __name__ == "__main__":
    main()
