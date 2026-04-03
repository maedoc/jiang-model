"""
Extended ODE model with numba acceleration.

Provides:
- `system_numba`: Numba-jitted core ODE function (requires all parameters as arrays).
- `ExtendedODEModelNumba`: Subclass of `ExtendedODEModel` that uses the accelerated system.
- `create_numba_system_from_params`: Convenience function returning a callable `f(t, y)`.

Example:
    >>> from ode_model_extended import load_parameters
    >>> from ode_model_extended_numba import ExtendedODEModelNumba
    >>> params = load_parameters("real_params.json")
    >>> model = ExtendedODEModelNumba(params)
    >>> y0 = ...  # initial state
    >>> dydt = model.system(0.0, y0)  # accelerated evaluation
    >>> sol = model.simulate(t_span=(0, 10))  # integration uses accelerated system

If numba is not installed, `ExtendedODEModelNumba` falls back to the original Python system.
"""

import numpy as np

try:
    from numba import njit, prange

    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False

    # Fallback: define dummy decorator
    def njit(*args, **kwargs):
        def decorator(func):
            return func

        return decorator

    prange = range

# Constants
EPS = 1e-8
K_HALF = 1000.0
TRADE_SCALE = 0.01
BASELINE = 0.5
DISRUPTION_DAY = 100.0
ME_IDX = 3  # Middle East index

# ----------------------------------------------------------------------
# Numba-compatible helper functions
# ----------------------------------------------------------------------


@njit(cache=True)
def log_transform(x):
    """Transform positive variable to log space: L = log(1 + x)."""
    return np.log1p(x)


@njit(cache=True)
def exp_transform(L):
    """Inverse transform: x = exp(L) - 1 with overflow protection."""
    # Clip to prevent overflow
    L_clipped = L
    if L_clipped < -100.0:
        L_clipped = -100.0
    elif L_clipped > 100.0:
        L_clipped = 100.0
    return np.expm1(L_clipped)


@njit(cache=True)
def logit_transform(p):
    """Transform bounded variable (0-1) to logit space."""
    # Clip to avoid exact 0 or 1
    if p < EPS:
        p_clipped = EPS
    elif p > 1.0 - EPS:
        p_clipped = 1.0 - EPS
    else:
        p_clipped = p
    return np.log(p_clipped / (1.0 - p_clipped))


@njit(cache=True)
def inv_logit(L):
    """Inverse logit transform with overflow protection."""
    L_clipped = L
    if L_clipped < -50.0:
        L_clipped = -50.0
    elif L_clipped > 50.0:
        L_clipped = 50.0
    return 1.0 / (1.0 + np.exp(-L_clipped))


@njit(cache=True)
def sigmoid(x, k=1.0, x0=0.0):
    """Smooth sigmoid transition: 1/(1 + exp(-k*(x - x0)))"""
    return 1.0 / (1.0 + np.exp(-k * (x - x0)))


@njit(cache=True)
def compute_hormuz_disruption(t, disruption_day=DISRUPTION_DAY):
    """Compute Hormuz disruption factor as a function of time."""
    if t < disruption_day:
        return 0.0
    ramp = (t - disruption_day) / 10.0
    if ramp > 1.0:
        ramp = 1.0
    return 0.8 * ramp


# ----------------------------------------------------------------------
# Core Numba-accelerated ODE system
# ----------------------------------------------------------------------


@njit(cache=True, parallel=False)
def system_numba(
    t,
    y,
    oil_production,
    oil_consumption,
    fertilizer_production,
    fertilizer_consumption,
    water_availability,
    water_consumption,
    stability_decay,
    stability_gain,
    oil_trade_flow,
    fertilizer_trade_flow,
    water_trade_flow,
    stability_coupling,
    capital_flow,
    financial_coupling,
    debt_target,
    n_regions,
    n_vars_per_region,
    K_HALF=K_HALF,
    EPS=EPS,
    trade_scale=TRADE_SCALE,
    baseline=BASELINE,
    disruption_day=DISRUPTION_DAY,
    me_idx=ME_IDX,
):
    """
    Numba-accelerated ODE system for extended model.

    Parameters
    ----------
    t : float
        Time
    y : ndarray, shape (n_regions * n_vars_per_region,)
        Flattened state vector in transformed units.
    All other parameters are numpy arrays as defined in the original model.

    Returns
    -------
    dydt : ndarray, same shape as y
        Derivative vector.
    """
    # Variable indices (must match ExtendedODEModel)
    idx_log_oil = 0
    idx_log_fert = 1
    idx_stability = 2
    idx_log_water = 3
    idx_log_military = 4
    idx_logit_inequality = 5
    idx_log_debt = 6
    idx_log_price_oil = 7
    idx_log_price_fert = 8
    idx_log_price_water = 9
    idx_inflation = 10
    idx_interest = 11
    idx_log_exchange = 12
    idx_bond_yield = 13
    idx_log_exchange_avg = 14
    DAILY_SCALE = 1.0 / 365.25

    # Extract state variables from flattened vector
    log_oil = y[idx_log_oil * n_regions : (idx_log_oil + 1) * n_regions]
    log_fert = y[idx_log_fert * n_regions : (idx_log_fert + 1) * n_regions]
    stability = y[idx_stability * n_regions : (idx_stability + 1) * n_regions]
    log_water = y[idx_log_water * n_regions : (idx_log_water + 1) * n_regions]
    log_military = y[idx_log_military * n_regions : (idx_log_military + 1) * n_regions]
    logit_inequality = y[
        idx_logit_inequality * n_regions : (idx_logit_inequality + 1) * n_regions
    ]
    log_debt = y[idx_log_debt * n_regions : (idx_log_debt + 1) * n_regions]
    log_price_oil = y[
        idx_log_price_oil * n_regions : (idx_log_price_oil + 1) * n_regions
    ]
    log_price_fert = y[
        idx_log_price_fert * n_regions : (idx_log_price_fert + 1) * n_regions
    ]
    log_price_water = y[
        idx_log_price_water * n_regions : (idx_log_price_water + 1) * n_regions
    ]
    inflation = y[idx_inflation * n_regions : (idx_inflation + 1) * n_regions]
    interest = y[idx_interest * n_regions : (idx_interest + 1) * n_regions]
    log_exchange = y[idx_log_exchange * n_regions : (idx_log_exchange + 1) * n_regions]
    bond_yield = y[idx_bond_yield * n_regions : (idx_bond_yield + 1) * n_regions]
    log_exchange_avg = y[
        idx_log_exchange_avg * n_regions : (idx_log_exchange_avg + 1) * n_regions
    ]

    # Convert transformed variables back to original units
    oil = np.empty_like(log_oil)
    fert = np.empty_like(log_fert)
    water = np.empty_like(log_water)
    military = np.empty_like(log_military)
    inequality = np.empty_like(logit_inequality)
    debt = np.empty_like(log_debt)
    price_oil = np.empty_like(log_price_oil)
    price_fert = np.empty_like(log_price_fert)
    price_water = np.empty_like(log_price_water)
    exchange = np.empty_like(log_exchange)
    exchange_avg = np.empty_like(log_exchange_avg)

    for i in range(n_regions):
        oil[i] = exp_transform(log_oil[i])
        fert[i] = exp_transform(log_fert[i])
        water[i] = exp_transform(log_water[i])
        military[i] = exp_transform(log_military[i])
        inequality[i] = inv_logit(logit_inequality[i])
        debt[i] = exp_transform(log_debt[i])
        price_oil[i] = exp_transform(log_price_oil[i])
        price_fert[i] = exp_transform(log_price_fert[i])
        price_water[i] = exp_transform(log_price_water[i])
        exchange[i] = exp_transform(log_exchange[i])
        exchange_avg[i] = exp_transform(log_exchange_avg[i])

    # Clip stability for production calculations
    stability_clipped = np.empty_like(stability)
    for i in range(n_regions):
        s = stability[i]
        if s < 0.0:
            s = 0.0
        elif s > 1.0:
            s = 1.0
        stability_clipped[i] = s

    # Compute Hormuz disruption effect on trade (reduce flows from Middle East)
    disruption = compute_hormuz_disruption(t, disruption_day)

    # Apply disruption and scale trade flows
    oil_trade_disrupted = oil_trade_flow.copy() * trade_scale
    fert_trade_disrupted = fertilizer_trade_flow.copy() * trade_scale
    water_trade_disrupted = water_trade_flow.copy() * trade_scale

    # Reduce exports from Middle East by disruption factor
    for i in range(n_regions):
        oil_trade_disrupted[i, me_idx] *= 1.0 - disruption
        fert_trade_disrupted[i, me_idx] *= 1.0 - disruption
        water_trade_disrupted[i, me_idx] *= 1.0 - disruption

    # Initialize derivatives in original units
    dOdt = np.zeros(n_regions)
    dFdt = np.zeros(n_regions)
    dWdt = np.zeros(n_regions)
    dSdt = np.zeros(n_regions)
    dMdt = np.zeros(n_regions)
    dIdt = np.zeros(n_regions)  # inequality derivative (original units, 0-1)
    dDdt = np.zeros(n_regions)  # debt derivative
    dPo_dt = np.zeros(n_regions)  # oil price
    dPf_dt = np.zeros(n_regions)  # fertilizer price
    dPw_dt = np.zeros(n_regions)  # water price
    dInf_dt = np.zeros(n_regions)  # inflation
    dInt_dt = np.zeros(n_regions)  # interest rate
    dEx_dt = np.zeros(n_regions)  # exchange rate
    dBy_dt = np.zeros(n_regions)  # bond yield
    dExAvg_dt = np.zeros(n_regions)  # exchange average

    # GDP proxy (used for debt dynamics)
    gdp = np.empty(n_regions)
    for i in range(n_regions):
        gdp[i] = (
            oil_production[i] * stability_clipped[i]
            + fertilizer_production[i] * stability_clipped[i]
        )
    gdp_scale = np.mean(gdp) if np.mean(gdp) > 0 else 1.0
    for i in range(n_regions):
        gdp[i] /= gdp_scale

    # Precompute nonlinear thresholds
    debt_crisis = np.empty(n_regions)
    currency_crisis = np.empty(n_regions)
    social_unrest = np.empty(n_regions)
    water_scarcity = np.empty(n_regions)

    initial_water = water_availability * 10.0  # proxy for initial water stock

    for i in range(n_regions):
        debt_crisis[i] = sigmoid(debt[i] - 1.0, k=10.0, x0=0.0)
        # Currency crisis: 30-day depreciation > 20%
        depreciation = (exchange_avg[i] - exchange[i]) / (exchange_avg[i] + EPS)
        currency_crisis[i] = sigmoid(depreciation - 0.2, k=20.0, x0=0.0)
        # Social unrest: inequality > 0.6 AND inflation > 0.1
        social_unrest[i] = sigmoid(inequality[i] - 0.6, k=10.0, x0=0.0) * sigmoid(
            inflation[i] - 0.1, k=20.0, x0=0.0
        )
        # Resource scarcity: water stock < 10% of initial
        water_scarcity[i] = sigmoid(0.1 * initial_water[i] - water[i], k=0.1, x0=0.0)

    # Compute resource derivatives with trade
    for i in range(n_regions):
        # Local production minus consumption
        prod_oil = oil_production[i] * (
            baseline + (1 - baseline) * stability_clipped[i]
        )
        cons_oil = oil_consumption[i]
        prod_fert = fertilizer_production[i] * (
            baseline + (1 - baseline) * stability_clipped[i]
        )
        cons_fert = fertilizer_consumption[i]
        prod_water = water_availability[i] * (
            baseline + (1 - baseline) * stability_clipped[i]
        )
        cons_water = water_consumption[i]

        dOdt[i] = prod_oil - cons_oil
        dFdt[i] = prod_fert - cons_fert
        dWdt[i] = prod_water - cons_water

        # Trade contributions
        for j in range(n_regions):
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
            dInt_dt[i] += financial_coupling[i, j] * (interest[j] - interest[i]) * 0.01

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
            0.01 * (1 - stability_clipped[i]) + 0.005 * debt[i] - 0.02 * inequality[i]
        )

        # Debt dynamics (based on debug_debt.py)
        gov_spending = military[i] * gdp[i] * 0.01
        tax_revenue = gdp[i] * 0.3 * stability_clipped[i]
        debt_ceiling = 2.0
        debt_clipped = debt[i]
        if debt_clipped < -5.0:
            debt_clipped = -5.0
        elif debt_clipped > 10.0:
            debt_clipped = 10.0
        austerity_factor = 1.0 / (1.0 + np.exp(10.0 * (debt_clipped - debt_ceiling)))
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

        # Price dynamics: respond to supply-demand imbalance (stable normalized version)
        oil_balance = (oil_consumption[i] - oil_production[i]) / (
            oil_consumption[i] + oil_production[i] + EPS
        )
        fert_balance = (fertilizer_consumption[i] - fertilizer_production[i]) / (
            fertilizer_consumption[i] + fertilizer_production[i] + EPS
        )
        water_balance = (water_consumption[i] - water_availability[i]) / (
            water_consumption[i] + water_availability[i] + EPS
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
            (oil_production[i] - oil_consumption[i])
            + (fertilizer_production[i] - fertilizer_consumption[i])
            + (water_availability[i] - water_consumption[i])
        )
        dEx_dt[i] += 0.001 * trade_balance - 0.01 * (exchange[i] - 1.0)
        # Currency crisis triggers capital flight (increase outflow)
        dEx_dt[i] += currency_crisis[i] * 0.05 * exchange[i]

        # Bond yield: linked to interest rate plus risk premium
        dBy_dt[i] = 0.1 * (interest[i] + debt_crisis[i] * 0.02 - bond_yield[i])

        # Exchange average: moving average with 30-day time constant
        dExAvg_dt[i] = (exchange[i] - exchange_avg[i]) / 30.0

    # Convert derivatives of log-transformed variables
    dlog_oil = np.empty(n_regions)
    dlog_fert = np.empty(n_regions)
    dlog_water = np.empty(n_regions)
    dlog_military = np.empty(n_regions)
    dlogit_inequality = np.empty(n_regions)
    dlog_debt = np.empty(n_regions)
    dlog_price_oil = np.empty(n_regions)
    dlog_price_fert = np.empty(n_regions)
    dlog_price_water = np.empty(n_regions)
    dlog_exchange = np.empty(n_regions)
    dlog_exchange_avg = np.empty(n_regions)

    for i in range(n_regions):
        dlog_oil[i] = dOdt[i] / (1.0 + oil[i] + EPS)
        dlog_fert[i] = dFdt[i] / (1.0 + fert[i] + EPS)
        dlog_water[i] = dWdt[i] / (1.0 + water[i] + EPS)
        dlog_military[i] = dMdt[i] / (1.0 + military[i] + EPS)
        # Inequality is logit-transformed: d(logit) = dI / (I*(1-I))
        dlogit_inequality[i] = dIdt[i] / (inequality[i] * (1.0 - inequality[i]) + EPS)
        dlog_debt[i] = dDdt[i] / (1.0 + debt[i] + EPS)
        dlog_price_oil[i] = dPo_dt[i] / (1.0 + price_oil[i] + EPS)
        dlog_price_fert[i] = dPf_dt[i] / (1.0 + price_fert[i] + EPS)
        dlog_price_water[i] = dPw_dt[i] / (1.0 + price_water[i] + EPS)
        dlog_exchange[i] = dEx_dt[i] / (1.0 + exchange[i] + EPS)
        dlog_exchange_avg[i] = dExAvg_dt[i] / (1.0 + exchange_avg[i] + EPS)

    # Assemble full derivative vector
    dydt = np.concatenate(
        (
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
        )
    )
    return dydt


# ----------------------------------------------------------------------
# Wrapper class that uses the numba-accelerated system
# ----------------------------------------------------------------------

from ode_model_extended import ExtendedODEModel


class ExtendedODEModelNumba(ExtendedODEModel):
    """
    Extended ODE model with numba acceleration.
    Overrides the system method to use the compiled function.
    """

    def system(self, t: float, y: np.ndarray) -> np.ndarray:
        # If numba is not available, fall back to parent implementation
        if not HAS_NUMBA:
            return super().system(t, y)

        # Extract parameters as numpy arrays
        params = self.params
        n = self.n_regions

        # Call numba function with all needed parameters
        return system_numba(
            t,
            y,
            params["oil_production"],
            params["oil_consumption"],
            params["fertilizer_production"],
            params["fertilizer_consumption"],
            params["water_availability"],
            params["water_consumption"],
            params["stability_decay"],
            params["stability_gain"],
            params["oil_trade_flow"],
            params["fertilizer_trade_flow"],
            params["water_trade_flow"],
            params["stability_coupling"],
            params["capital_flow"],
            params["financial_coupling"],
            params["debt_to_gdp"],
            n,
            self.n_vars_per_region,
            K_HALF=K_HALF,
            EPS=EPS,
            trade_scale=TRADE_SCALE,
            baseline=BASELINE,
            disruption_day=DISRUPTION_DAY,
            me_idx=ME_IDX,
        )


# ----------------------------------------------------------------------
# Convenience function for direct use of numba system
# ----------------------------------------------------------------------


def create_numba_system_from_params(params):
    """
    Create a function f(t, y) that calls system_numba with given parameters.
    Useful for integration with scipy.solve_ivp.
    """
    n_regions = len(params["oil_production"])
    n_vars_per_region = 15

    def f(t, y):
        return system_numba(
            t,
            y,
            params["oil_production"],
            params["oil_consumption"],
            params["fertilizer_production"],
            params["fertilizer_consumption"],
            params["water_availability"],
            params["water_consumption"],
            params["stability_decay"],
            params["stability_gain"],
            params["oil_trade_flow"],
            params["fertilizer_trade_flow"],
            params["water_trade_flow"],
            params["stability_coupling"],
            params["capital_flow"],
            params["financial_coupling"],
            params["debt_to_gdp"],
            n_regions,
            n_vars_per_region,
            K_HALF=K_HALF,
            EPS=EPS,
            trade_scale=TRADE_SCALE,
            baseline=BASELINE,
            disruption_day=DISRUPTION_DAY,
            me_idx=ME_IDX,
        )

    return f
