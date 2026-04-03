"""
ModelConfig: all tunable structural coefficients in one place.

Every magic number from the ODE system is collected here with a name,
default value, and brief description.  The config can be serialised to
JSON alongside the parameter set so that every simulation run is fully
reproducible.
"""

from dataclasses import dataclass, field, asdict
import json


@dataclass
class ModelConfig:
    """Structural coefficients for the geopolitical ODE model.

    These are *model* constants (shared across regions) as opposed to
    *regional parameters* (per-region data loaded from JSON).
    """

    # --- Numerical constants ---
    eps: float = 1e-8
    log_clip_lo: float = -100.0
    log_clip_hi: float = 100.0
    logit_clip: float = 50.0

    # --- Time scaling ---
    daily_scale: float = 1.0 / 365.25  # convert annual rates to daily

    # --- Resource dynamics ---
    baseline_production: float = 0.5      # fraction of capacity at zero stability
    k_half: float = 1000.0               # Monod half-saturation for trade limits
    trade_scale: float = 0.01            # global dampening of trade flows
    resource_abundance_scale: float = 3.0   # tanh scaling for normalized resource ratio → stability
    initial_stock_days: float = 90.0      # initial stock = max(prod, cons) × this

    # --- Stability dynamics ---
    social_unrest_strength: float = 0.1   # unrest effect on stability
    stability_bound_stiffness: float = 10.0  # restoring force outside [0,1]

    # --- Military dynamics ---
    military_gdp_fraction: float = 0.01   # military grows at this fraction of GDP
    military_decay: float = 0.05          # base decay rate
    military_debt_suppression: float = 0.1  # debt crisis reduces military growth

    # --- Inequality dynamics ---
    inequality_instability_rate: float = 0.01
    inequality_debt_rate: float = 0.005
    inequality_reversion_rate: float = 0.02

    # --- Fiscal / debt dynamics ---
    gov_spending_pct: float = 0.01        # government spending as pct of GDP×military
    tax_rate: float = 0.30                # tax revenue as pct of GDP
    debt_ceiling: float = 2.0             # austerity triggers at this debt/GDP
    austerity_sharpness: float = 10.0     # sigmoid steepness for austerity
    debt_mean_reversion: float = 0.1      # rate of pull toward target debt
    base_growth_rate: float = 0.02        # annual GDP growth at full stability

    # --- Price dynamics ---
    price_response: float = 0.01          # price response to supply-demand imbalance
    price_reversion: float = 0.05         # price mean-reversion toward equilibrium
    scarcity_price_boost: float = 0.1     # water scarcity price effect

    # --- Price-mediated trade (Phase 6 extension) ---
    price_trade_enabled: bool = False
    price_trade_elasticity: float = 0.5   # how strongly price gaps drive trade
    price_trade_max_fraction: float = 0.3  # max fraction of stock tradeable per day
    price_trade_transport_cost: float = 0.1  # cost dampening for distance

    # --- Inflation ---
    inflation_weight_oil: float = 0.3
    inflation_weight_fert: float = 0.3
    inflation_weight_water: float = 0.4

    # --- Interest rate (Taylor rule) ---
    neutral_rate: float = 0.03
    inflation_target: float = 0.02
    taylor_reversion: float = 0.5
    taylor_inflation_coeff: float = 1.5
    taylor_debt_coeff: float = 0.5
    debt_crisis_rate_premium: float = 0.02

    # --- Exchange rate ---
    trade_balance_fx_sensitivity: float = 0.001
    fx_mean_reversion: float = 0.01
    capital_flight_intensity: float = 0.05
    capital_flow_fx_scale: float = 0.001
    interest_coupling_scale: float = 0.01

    # --- Bond yield ---
    bond_yield_adjustment_speed: float = 0.1

    # --- Exchange average ---
    exchange_avg_window: float = 30.0     # days for moving average

    # --- Crisis thresholds ---
    debt_crisis_threshold: float = 1.0    # debt/GDP level
    debt_crisis_sharpness: float = 10.0
    currency_crisis_threshold: float = 0.2  # 20% depreciation
    currency_crisis_sharpness: float = 20.0
    unrest_inequality_threshold: float = 0.6
    unrest_inequality_sharpness: float = 10.0
    unrest_inflation_threshold: float = 0.1
    unrest_inflation_sharpness: float = 20.0
    water_scarcity_fraction: float = 0.1  # 10% of initial
    water_scarcity_sharpness: float = 0.1

    # --- GDP proxy ---
    gdp_normalize_global: bool = True     # normalize GDP by global mean

    # --- Solver defaults ---
    default_method: str = "BDF"
    default_rtol: float = 1e-6
    default_atol: float = 1e-8

    def to_dict(self):
        return asdict(self)

    def to_json(self, path: str):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def from_dict(cls, d: dict):
        # Only pass known fields
        known = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in d.items() if k in known})

    @classmethod
    def from_json(cls, path: str):
        with open(path) as f:
            return cls.from_dict(json.load(f))
