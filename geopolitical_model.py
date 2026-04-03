"""
Geopolitical Resource Dynamics ODE Model
========================================

12 regions × 15 state variables = 180 coupled ODEs modelling resource
stocks, political stability, fiscal dynamics, commodity prices, and
financial variables with inter-region trade, stability diffusion, and
financial contagion.

Key design choices
------------------
* Log-transform for positive variables, logit for bounded [0,1] variables.
* All structural coefficients live in ``ModelConfig``; regional data in
  the parameter dict loaded from JSON.
* Interventions are injected via a callable that modifies a *copy* of the
  parameter dict at each time step — the ODE system never hard-codes
  disruption logic.
* Optional Numba JIT: when numba is available the RHS function is compiled
  automatically (``use_numba=True``).
"""

import numpy as np
import json
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple
from scipy.integrate import solve_ivp

from model_config import ModelConfig

# ---------------------------------------------------------------------------
# Region definitions
# ---------------------------------------------------------------------------

REGION_NAMES = [
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

N_VARS = 15  # variables per region

# Variable indices within each region block
IDX_LOG_OIL = 0
IDX_LOG_FERT = 1
IDX_LOGIT_STABILITY = 2
IDX_LOG_WATER = 3
IDX_LOG_MILITARY = 4
IDX_LOGIT_INEQUALITY = 5
IDX_LOG_DEBT = 6
IDX_LOG_PRICE_OIL = 7
IDX_LOG_PRICE_FERT = 8
IDX_LOG_PRICE_WATER = 9
IDX_INFLATION = 10
IDX_INTEREST = 11
IDX_LOG_EXCHANGE = 12
IDX_BOND_YIELD = 13
IDX_LOG_EXCHANGE_AVG = 14

VAR_NAMES = [
    "oil_stock", "fertilizer_stock", "stability", "water_stock",
    "military", "inequality", "debt_gdp", "oil_price", "fertilizer_price",
    "water_price", "inflation", "interest_rate", "exchange_rate",
    "bond_yield", "exchange_rate_avg",
]

# Which indices are log-transformed, logit-transformed, or untransformed
LOG_INDICES = [0, 1, 3, 4, 6, 7, 8, 9, 12, 14]
LOGIT_INDICES = [2, 5]
RAW_INDICES = [10, 11, 13]

# ---------------------------------------------------------------------------
# Transform helpers (pure numpy, no objects)
# ---------------------------------------------------------------------------

EPS = 1e-8


def log_transform(x):
    return np.log1p(np.maximum(x, 0.0))


def exp_transform(L):
    return np.expm1(np.clip(L, -100.0, 100.0))


def logit_transform(p):
    p = np.clip(p, EPS, 1.0 - EPS)
    return np.log(p / (1.0 - p))


def inv_logit(L):
    L = np.clip(L, -50.0, 50.0)
    return 1.0 / (1.0 + np.exp(-L))


def sigmoid(x, k=1.0, x0=0.0):
    z = np.clip(-k * (x - x0), -500.0, 500.0)
    return 1.0 / (1.0 + np.exp(z))


# ---------------------------------------------------------------------------
# Parameter loading & validation
# ---------------------------------------------------------------------------

REQUIRED_VECTOR_KEYS = [
    "oil_production", "oil_consumption",
    "fertilizer_production", "fertilizer_consumption",
    "water_availability", "water_consumption",
    "stability_decay", "stability_gain",
    "oil_price", "fertilizer_price", "water_price",
    "inflation", "interest_rate", "exchange_rate", "bond_yield",
    "debt_to_gdp", "military_expenditure", "inequality",
]

REQUIRED_MATRIX_KEYS = [
    "oil_trade_flow", "fertilizer_trade_flow", "water_trade_flow",
    "stability_coupling", "capital_flow", "financial_coupling",
]

OPTIONAL_KEYS = [
    "political_stability",     # per-region initial stability
    "oil_trade", "fertilizer_trade",  # legacy aliases
    "military_production",     # not currently used in ODE
    "gdp_scale_factors",       # per-region GDP scaling (new)
]


def load_parameters(filename: str = "real_params.json") -> Dict[str, np.ndarray]:
    """Load and validate parameter JSON into numpy arrays."""
    with open(filename) as f:
        raw = json.load(f)

    params: Dict[str, np.ndarray] = {}
    for key, value in raw.items():
        params[key] = np.array(value, dtype=np.float64)

    n = len(params["oil_production"])

    # Validate required vectors
    for key in REQUIRED_VECTOR_KEYS:
        if key not in params:
            raise KeyError(f"Missing required parameter: {key}")
        if params[key].shape != (n,):
            raise ValueError(f"{key}: expected shape ({n},), got {params[key].shape}")

    # Validate required matrices
    for key in REQUIRED_MATRIX_KEYS:
        if key not in params:
            raise KeyError(f"Missing required parameter: {key}")
        if params[key].shape != (n, n):
            raise ValueError(f"{key}: expected shape ({n},{n}), got {params[key].shape}")

    # Check for NaN / Inf
    for key, arr in params.items():
        if not np.all(np.isfinite(arr)):
            raise ValueError(f"{key} contains NaN or Inf")

    return params


# ---------------------------------------------------------------------------
# ODE right-hand side (single source — used for both Python and Numba paths)
# ---------------------------------------------------------------------------

def ode_rhs(
    t: float,
    y: np.ndarray,
    n: int,
    cfg: ModelConfig,
    # --- regional parameters (arrays) ---
    oil_prod: np.ndarray,
    oil_cons: np.ndarray,
    fert_prod: np.ndarray,
    fert_cons: np.ndarray,
    water_avail: np.ndarray,
    water_cons: np.ndarray,
    stability_decay: np.ndarray,
    stability_gain: np.ndarray,
    debt_target: np.ndarray,
    initial_water: np.ndarray,
    initial_resource_total: np.ndarray,
    # --- trade / coupling matrices ---
    oil_trade: np.ndarray,
    fert_trade: np.ndarray,
    water_trade: np.ndarray,
    stability_coupling: np.ndarray,
    capital_flow: np.ndarray,
    financial_coupling: np.ndarray,
    # --- optional GDP scale factors ---
    gdp_scale_factors: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Compute dy/dt for the full 180-dimensional ODE system.

    All structural coefficients come from *cfg* (ModelConfig).
    Regional data comes from the explicit array arguments.
    Trade matrices should already incorporate any intervention effects.
    """

    # --- Unpack state ---------------------------------------------------
    def _block(idx):
        return y[idx * n:(idx + 1) * n]

    logit_stab = _block(IDX_LOGIT_STABILITY)
    logit_ineq = _block(IDX_LOGIT_INEQUALITY)
    inflation   = _block(IDX_INFLATION)
    interest    = _block(IDX_INTEREST)
    bond_yield  = _block(IDX_BOND_YIELD)

    # Transform back to physical units
    oil       = exp_transform(_block(IDX_LOG_OIL))
    fert      = exp_transform(_block(IDX_LOG_FERT))
    water     = exp_transform(_block(IDX_LOG_WATER))
    military  = exp_transform(_block(IDX_LOG_MILITARY))
    debt      = exp_transform(_block(IDX_LOG_DEBT))
    price_oil = exp_transform(_block(IDX_LOG_PRICE_OIL))
    price_fert = exp_transform(_block(IDX_LOG_PRICE_FERT))
    price_water = exp_transform(_block(IDX_LOG_PRICE_WATER))
    exchange   = exp_transform(_block(IDX_LOG_EXCHANGE))
    exchange_avg = exp_transform(_block(IDX_LOG_EXCHANGE_AVG))

    stability  = inv_logit(logit_stab)
    inequality = inv_logit(logit_ineq)

    # --- GDP proxy -------------------------------------------------------
    gdp = (oil_prod + fert_prod) * stability
    if gdp_scale_factors is not None:
        gdp = gdp * gdp_scale_factors
    elif cfg.gdp_normalize_global:
        gdp_mean = np.mean(gdp)
        if gdp_mean > 0:
            gdp = gdp / gdp_mean

    # --- Crisis thresholds -----------------------------------------------
    debt_crisis = sigmoid(debt - cfg.debt_crisis_threshold,
                          k=cfg.debt_crisis_sharpness)
    depreciation = (exchange_avg - exchange) / (exchange_avg + cfg.eps)
    currency_crisis = sigmoid(depreciation - cfg.currency_crisis_threshold,
                              k=cfg.currency_crisis_sharpness)
    social_unrest = (
        sigmoid(inequality - cfg.unrest_inequality_threshold,
                k=cfg.unrest_inequality_sharpness)
        * sigmoid(inflation - cfg.unrest_inflation_threshold,
                  k=cfg.unrest_inflation_sharpness)
    )
    water_scarcity = sigmoid(
        cfg.water_scarcity_fraction * initial_water - water,
        k=cfg.water_scarcity_sharpness,
    )

    # --- Initialise derivatives (physical-unit space) --------------------
    dOdt   = np.zeros(n)
    dFdt   = np.zeros(n)
    dWdt   = np.zeros(n)
    dSdt   = np.zeros(n)   # stability
    dMdt   = np.zeros(n)
    dIdt   = np.zeros(n)   # inequality
    dDdt   = np.zeros(n)   # debt
    dPo_dt = np.zeros(n)
    dPf_dt = np.zeros(n)
    dPw_dt = np.zeros(n)
    dInf_dt  = np.zeros(n)
    dInt_dt  = np.zeros(n)
    dEx_dt   = np.zeros(n)
    dBy_dt   = np.zeros(n)
    dExAvg_dt = np.zeros(n)

    # Scale trade matrices
    oil_t   = oil_trade * cfg.trade_scale
    fert_t  = fert_trade * cfg.trade_scale
    water_t = water_trade * cfg.trade_scale

    # === Price-mediated trade extension ===================================
    # When enabled, adds additional trade flows driven by regional price diffs
    if cfg.price_trade_enabled:
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                # Oil: flow from low-price region j to high-price region i
                price_gap_oil = price_oil[i] - price_oil[j]
                if price_gap_oil > 0 and oil[j] > 0:
                    available = oil[j] * cfg.price_trade_max_fraction
                    flow = (cfg.price_trade_elasticity * price_gap_oil
                            / (1.0 + cfg.price_trade_transport_cost)
                            * stability[j])
                    flow = min(flow, available)
                    flow = max(flow, 0.0)
                    dOdt[i] += flow
                    dOdt[j] -= flow

                # Fertilizer
                price_gap_fert = price_fert[i] - price_fert[j]
                if price_gap_fert > 0 and fert[j] > 0:
                    available = fert[j] * cfg.price_trade_max_fraction
                    flow = (cfg.price_trade_elasticity * price_gap_fert
                            / (1.0 + cfg.price_trade_transport_cost)
                            * stability[j])
                    flow = min(flow, available)
                    flow = max(flow, 0.0)
                    dFdt[i] += flow
                    dFdt[j] -= flow

    # === Per-region dynamics =============================================
    for i in range(n):
        # --- Resource production & consumption ---------------------------
        s = stability[i]
        prod_oil   = oil_prod[i]  * (cfg.baseline_production + (1 - cfg.baseline_production) * s)
        prod_fert  = fert_prod[i] * (cfg.baseline_production + (1 - cfg.baseline_production) * s)
        prod_water = water_avail[i] * (cfg.baseline_production + (1 - cfg.baseline_production) * s)

        dOdt[i] += prod_oil  - oil_cons[i]
        dFdt[i] += prod_fert - fert_cons[i]
        dWdt[i] += prod_water - water_cons[i]

        # --- Inter-region coupling (trade, stability, finance) -----------
        for j in range(n):
            if i == j:
                continue

            # Resource trade: flow from j → i, limited by exporter stock
            oj = oil[j]
            flow_oil = oil_t[i, j] * stability[j] * (oj / (oj + cfg.k_half) if oj > 0 else 0.0)
            dOdt[i] += flow_oil
            dOdt[j] -= flow_oil

            fj = fert[j]
            flow_fert = fert_t[i, j] * stability[j] * (fj / (fj + cfg.k_half) if fj > 0 else 0.0)
            dFdt[i] += flow_fert
            dFdt[j] -= flow_fert

            wj = water[j]
            flow_water = water_t[i, j] * stability[j] * (wj / (wj + cfg.k_half) if wj > 0 else 0.0)
            dWdt[i] += flow_water
            dWdt[j] -= flow_water

            # Stability diffusion (logistic coupling in [0,1])
            dSdt[i] += (stability_coupling[i, j]
                        * (stability[j] - stability[i])
                        * stability[i] * (1 - stability[i]))

            # Financial coupling
            dEx_dt[i]  += capital_flow[i, j] * (exchange[j] - exchange[i]) * cfg.capital_flow_fx_scale
            dInt_dt[i] += financial_coupling[i, j] * (interest[j] - interest[i]) * cfg.interest_coupling_scale

        # --- Local stability dynamics ------------------------------------
        # Normalize resource abundance by initial stock so depletion matters
        resource_ratio = (oil[i] + fert[i] + water[i]) / (initial_resource_total[i] + cfg.eps)
        resource_abundance = np.tanh(cfg.resource_abundance_scale * resource_ratio)
        dSdt[i] += (-stability_decay[i] * s
                     + stability_gain[i] * resource_abundance * (1 - s)
                     - social_unrest[i] * cfg.social_unrest_strength * s)

        # --- Military expenditure ----------------------------------------
        dMdt[i] = (cfg.military_gdp_fraction * gdp[i]
                   - cfg.military_decay * military[i]
                   - debt_crisis[i] * cfg.military_debt_suppression * military[i])

        # --- Inequality --------------------------------------------------
        dIdt[i] = (cfg.inequality_instability_rate * (1 - s)
                   + cfg.inequality_debt_rate * debt[i]
                   - cfg.inequality_reversion_rate * inequality[i])

        # --- Debt dynamics -----------------------------------------------
        gov_spending = military[i] * gdp[i] * cfg.gov_spending_pct
        tax_revenue  = gdp[i] * cfg.tax_rate * s
        debt_clipped = np.clip(debt[i], -5.0, 10.0)
        austerity = 1.0 / (1.0 + np.exp(cfg.austerity_sharpness * (debt_clipped - cfg.debt_ceiling)))
        gov_spending *= austerity
        primary_deficit = gov_spending - tax_revenue
        growth_rate = cfg.base_growth_rate * s * cfg.daily_scale
        mean_reversion = cfg.debt_mean_reversion * (debt_target[i] - debt[i])
        dDdt[i] = (primary_deficit
                   + (interest[i] * cfg.daily_scale - growth_rate) * debt[i]
                   + mean_reversion)

        # Debt crisis → interest rate risk premium
        dInt_dt[i] += debt_crisis[i] * cfg.debt_crisis_rate_premium

        # --- Commodity prices (supply–demand imbalance) ------------------
        oil_bal  = (oil_cons[i] - oil_prod[i]) / (oil_cons[i] + oil_prod[i] + cfg.eps)
        fert_bal = (fert_cons[i] - fert_prod[i]) / (fert_cons[i] + fert_prod[i] + cfg.eps)
        water_bal = (water_cons[i] - water_avail[i]) / (water_cons[i] + water_avail[i] + cfg.eps)

        dPo_dt[i] = cfg.price_response * oil_bal  - cfg.price_reversion * (price_oil[i] - 1.0)
        dPf_dt[i] = cfg.price_response * fert_bal - cfg.price_reversion * (price_fert[i] - 1.0)
        dPw_dt[i] = cfg.price_response * water_bal - cfg.price_reversion * (price_water[i] - 1.0)
        dPw_dt[i] += water_scarcity[i] * cfg.scarcity_price_boost

        # --- Inflation (log-price derivative = relative price change) ----
        dInf_dt[i] = (
            cfg.inflation_weight_oil   * dPo_dt[i] / (price_oil[i]   + 1.0)
            + cfg.inflation_weight_fert  * dPf_dt[i] / (price_fert[i]  + 1.0)
            + cfg.inflation_weight_water * dPw_dt[i] / (price_water[i] + 1.0)
        )

        # --- Interest rate (Taylor rule) ---------------------------------
        dInt_dt[i] += (
            cfg.taylor_reversion * (cfg.neutral_rate - interest[i])
            + cfg.taylor_inflation_coeff * (inflation[i] - cfg.inflation_target)
            + cfg.taylor_debt_coeff * (debt[i] - debt_target[i])
        )

        # --- Exchange rate -----------------------------------------------
        trade_balance = ((oil_prod[i] - oil_cons[i])
                         + (fert_prod[i] - fert_cons[i])
                         + (water_avail[i] - water_cons[i]))
        dEx_dt[i] += (cfg.trade_balance_fx_sensitivity * trade_balance
                      - cfg.fx_mean_reversion * (exchange[i] - 1.0)
                      + currency_crisis[i] * cfg.capital_flight_intensity * exchange[i])

        # --- Bond yield --------------------------------------------------
        dBy_dt[i] = cfg.bond_yield_adjustment_speed * (
            interest[i] + debt_crisis[i] * cfg.debt_crisis_rate_premium - bond_yield[i]
        )

        # --- Exchange moving average -------------------------------------
        dExAvg_dt[i] = (exchange[i] - exchange_avg[i]) / cfg.exchange_avg_window

    # === Convert to transformed-space derivatives ========================
    dydt = np.empty_like(y)

    # Log-transformed: d(log(1+x))/dt = dx/dt / (1+x)
    dydt[IDX_LOG_OIL * n:(IDX_LOG_OIL + 1) * n]         = dOdt / (1.0 + oil + cfg.eps)
    dydt[IDX_LOG_FERT * n:(IDX_LOG_FERT + 1) * n]        = dFdt / (1.0 + fert + cfg.eps)
    dydt[IDX_LOG_WATER * n:(IDX_LOG_WATER + 1) * n]      = dWdt / (1.0 + water + cfg.eps)
    dydt[IDX_LOG_MILITARY * n:(IDX_LOG_MILITARY + 1) * n] = dMdt / (1.0 + military + cfg.eps)
    dydt[IDX_LOG_DEBT * n:(IDX_LOG_DEBT + 1) * n]        = dDdt / (1.0 + debt + cfg.eps)
    dydt[IDX_LOG_PRICE_OIL * n:(IDX_LOG_PRICE_OIL + 1) * n]   = dPo_dt / (1.0 + price_oil + cfg.eps)
    dydt[IDX_LOG_PRICE_FERT * n:(IDX_LOG_PRICE_FERT + 1) * n]  = dPf_dt / (1.0 + price_fert + cfg.eps)
    dydt[IDX_LOG_PRICE_WATER * n:(IDX_LOG_PRICE_WATER + 1) * n] = dPw_dt / (1.0 + price_water + cfg.eps)
    dydt[IDX_LOG_EXCHANGE * n:(IDX_LOG_EXCHANGE + 1) * n]     = dEx_dt / (1.0 + exchange + cfg.eps)
    dydt[IDX_LOG_EXCHANGE_AVG * n:(IDX_LOG_EXCHANGE_AVG + 1) * n] = dExAvg_dt / (1.0 + exchange_avg + cfg.eps)

    # Logit-transformed: d(logit(p))/dt = dp/dt / (p*(1-p))
    # stability
    s_safe = np.clip(stability, cfg.eps, 1.0 - cfg.eps)
    dydt[IDX_LOGIT_STABILITY * n:(IDX_LOGIT_STABILITY + 1) * n] = dSdt / (s_safe * (1 - s_safe))
    # inequality
    iq_safe = np.clip(inequality, cfg.eps, 1.0 - cfg.eps)
    dydt[IDX_LOGIT_INEQUALITY * n:(IDX_LOGIT_INEQUALITY + 1) * n] = dIdt / (iq_safe * (1 - iq_safe))

    # Untransformed
    dydt[IDX_INFLATION * n:(IDX_INFLATION + 1) * n]  = dInf_dt
    dydt[IDX_INTEREST * n:(IDX_INTEREST + 1) * n]    = dInt_dt
    dydt[IDX_BOND_YIELD * n:(IDX_BOND_YIELD + 1) * n] = dBy_dt

    return dydt


# ---------------------------------------------------------------------------
# Model class — orchestration, initial conditions, simulation
# ---------------------------------------------------------------------------

class GeopoliticalModel:
    """High-level interface to the 12-region ODE model.

    Parameters
    ----------
    params : dict
        Regional parameters (from ``load_parameters``).
    config : ModelConfig, optional
        Structural coefficients (defaults used if omitted).
    interventions : list of Intervention, optional
        Time-dependent parameter modifications.
    """

    def __init__(
        self,
        params: Dict[str, np.ndarray],
        config: Optional[ModelConfig] = None,
        interventions=None,
    ):
        self.base_params = params
        self.cfg = config or ModelConfig()
        self.n_regions = len(params["oil_production"])
        self.n_vars = N_VARS
        self.interventions = interventions or []
        self.region_names = REGION_NAMES[: self.n_regions]

    # --- Initial conditions ---------------------------------------------

    def default_initial_state(self) -> np.ndarray:
        """Build y0 in transformed space from parameter defaults."""
        n = self.n_regions
        p = self.base_params
        days = self.cfg.initial_stock_days

        # Initial stocks: enough to cover max(prod, cons) for initial_stock_days
        oil0   = np.maximum(p["oil_production"], p["oil_consumption"]) * days
        fert0  = np.maximum(p["fertilizer_production"], p["fertilizer_consumption"]) * days
        water0 = np.maximum(p["water_availability"], p["water_consumption"]) * days

        stab0 = np.clip(p.get("political_stability", np.full(n, 0.7)), EPS, 1.0 - EPS)

        y0 = np.concatenate([
            log_transform(oil0),                          # 0  oil
            log_transform(fert0),                         # 1  fert
            logit_transform(stab0),                       # 2  stability (logit)
            log_transform(water0),                        # 3  water
            log_transform(p["military_expenditure"]),     # 4  military
            logit_transform(np.clip(p["inequality"], EPS, 1.0 - EPS)),  # 5  inequality
            log_transform(p["debt_to_gdp"]),              # 6  debt
            log_transform(p["oil_price"]),                # 7  oil price
            log_transform(p["fertilizer_price"]),         # 8  fert price
            log_transform(p["water_price"]),              # 9  water price
            p["inflation"],                               # 10 inflation
            p["interest_rate"],                            # 11 interest
            log_transform(p["exchange_rate"]),             # 12 exchange
            p["bond_yield"],                              # 13 bond yield
            log_transform(p["exchange_rate"]),             # 14 exchange avg
        ])
        return y0

    # --- RHS wrapper (applies interventions) ----------------------------

    def _make_rhs(self):
        """Return a closure suitable for ``solve_ivp``."""
        p = self.base_params
        n = self.n_regions
        cfg = self.cfg
        interventions = self.interventions

        # Pre-extract immutable parameters
        oil_prod      = p["oil_production"].copy()
        oil_cons      = p["oil_consumption"].copy()
        fert_prod     = p["fertilizer_production"].copy()
        fert_cons     = p["fertilizer_consumption"].copy()
        water_avail   = p["water_availability"].copy()
        water_cons    = p["water_consumption"].copy()
        stab_decay    = p["stability_decay"].copy()
        stab_gain     = p["stability_gain"].copy()
        debt_target   = p["debt_to_gdp"].copy()
        initial_water = np.maximum(water_avail, water_cons) * cfg.initial_stock_days
        # Initial total resource stock for normalization in stability dynamics
        initial_oil_stock = np.maximum(oil_prod, oil_cons) * cfg.initial_stock_days
        initial_fert_stock = np.maximum(fert_prod, fert_cons) * cfg.initial_stock_days
        initial_resource_total = initial_oil_stock + initial_fert_stock + initial_water
        oil_trade     = p["oil_trade_flow"].copy()
        fert_trade    = p["fertilizer_trade_flow"].copy()
        water_trade   = p["water_trade_flow"].copy()
        stab_coupling = p["stability_coupling"].copy()
        cap_flow      = p["capital_flow"].copy()
        fin_coupling  = p["financial_coupling"].copy()
        gdp_sf        = p.get("gdp_scale_factors", None)
        if gdp_sf is not None:
            gdp_sf = gdp_sf.copy()

        def rhs(t, y):
            # Apply interventions to a fresh copy of trade matrices
            ot = oil_trade.copy()
            ft = fert_trade.copy()
            wt = water_trade.copy()
            op = oil_prod.copy()
            fp = fert_prod.copy()

            if interventions:
                # Build a minimal param dict for interventions to modify
                iv_params = {
                    "oil_trade_flow": ot,
                    "fertilizer_trade_flow": ft,
                    "water_trade_flow": wt,
                    "oil_production": op,
                    "fertilizer_production": fp,
                }
                for iv in interventions:
                    iv_params = iv.apply(t, iv_params)
                ot = iv_params["oil_trade_flow"]
                ft = iv_params["fertilizer_trade_flow"]
                wt = iv_params["water_trade_flow"]
                op = iv_params["oil_production"]
                fp = iv_params["fertilizer_production"]

            return ode_rhs(
                t, y, n, cfg,
                op, oil_cons, fp, fert_cons,
                water_avail, water_cons,
                stab_decay, stab_gain, debt_target, initial_water,
                initial_resource_total,
                ot, ft, wt,
                stab_coupling, cap_flow, fin_coupling,
                gdp_sf,
            )

        return rhs

    # --- Simulation ------------------------------------------------------

    def simulate(
        self,
        t_span: Tuple[float, float] = (0.0, 365.0),
        y0: Optional[np.ndarray] = None,
        method: Optional[str] = None,
        rtol: Optional[float] = None,
        atol: Optional[float] = None,
        t_eval: Optional[np.ndarray] = None,
    ):
        """Integrate the ODE system.

        Returns a ``Trajectory`` (see trajectory.py).
        """
        from trajectory import Trajectory

        if y0 is None:
            y0 = self.default_initial_state()
        method = method or self.cfg.default_method
        rtol = rtol if rtol is not None else self.cfg.default_rtol
        atol = atol if atol is not None else self.cfg.default_atol

        rhs = self._make_rhs()
        sol = solve_ivp(
            rhs, t_span, y0,
            method=method, rtol=rtol, atol=atol,
            dense_output=True,
            t_eval=t_eval,
        )
        if sol.status != 0:
            import warnings
            warnings.warn(f"Solver finished with status {sol.status}: {sol.message}")

        return Trajectory(sol.t, sol.y, self.n_regions, self.region_names)
