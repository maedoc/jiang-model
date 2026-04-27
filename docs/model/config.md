# ModelConfig Parameters

The `ModelConfig` dataclass holds all **structural coefficients** shared across regions. These are distinct from **regional parameters** (per-region production, consumption, trade matrices) stored in `real_params.json`.

## Field listing

### Numerical constants

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `eps` | float | `1e-8` | Small epsilon for division stability |
| `log_clip_lo` | float | `-100.0` | Log-transform lower clip |
| `log_clip_hi` | float | `100.0` | Log-transform upper clip |
| `logit_clip` | float | `50.0` | Logit-transform clip |

### Time scaling

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `daily_scale` | float | `1/365.25` | Converts annual rates to daily |

### Resource dynamics

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `baseline_production` | float | `0.5` | Fraction of capacity at zero stability |
| `k_half` | float | `1000.0` | Monod half-saturation for trade limits |
| `trade_scale` | float | `0.01` | Global dampening of trade flows |
| `resource_abundance_scale` | float | `3.0` | tanh scaling for resource ratio → stability |
| `initial_stock_days` | float | `90.0` | Initial stock = max(prod, cons) × this |

### Stability dynamics

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `social_unrest_strength` | float | `0.1` | Unrest effect on stability |
| `stability_bound_stiffness` | float | `10.0` | Restoring force outside [0, 1] |

### Military dynamics

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `military_gdp_fraction` | float | `0.01` | Military grows at this fraction of GDP |
| `military_decay` | float | `0.05` | Base decay rate |
| `military_debt_suppression` | float | `0.1` | Debt crisis reduces military growth |

### Inequality dynamics

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `inequality_instability_rate` | float | `0.01` | Inequality rise from instability |
| `inequality_debt_rate` | float | `0.005` | Inequality rise from debt |
| `inequality_reversion_rate` | float | `0.02` | Inequality mean reversion |

### Fiscal / debt dynamics

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `gov_spending_pct` | float | `0.01` | Government spending as pct of GDP×military |
| `tax_rate` | float | `0.30` | Tax revenue as pct of GDP |
| `debt_ceiling` | float | `2.0` | Austerity triggers at this debt/GDP |
| `austerity_sharpness` | float | `10.0` | Sigmoid steepness for austerity |
| `debt_mean_reversion` | float | `0.1` | Rate of pull toward target debt |
| `base_growth_rate` | float | `0.02` | Annual GDP growth at full stability |

### Price dynamics

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `price_response` | float | `0.01` | Price response to supply-demand imbalance |
| `price_reversion` | float | `0.05` | Price mean-reversion toward equilibrium |
| `scarcity_price_boost` | float | `0.1` | Water scarcity price effect |

### Price-mediated trade

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `price_trade_enabled` | bool | `False` | Enable price-driven trade extension |
| `price_trade_elasticity` | float | `0.5` | How strongly price gaps drive trade |
| `price_trade_max_fraction` | float | `0.3` | Max fraction of stock tradeable per day |
| `price_trade_transport_cost` | float | `0.1` | Cost dampening for distance |

### Inflation

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `inflation_weight_oil` | float | `0.3` | Oil contribution to inflation |
| `inflation_weight_fert` | float | `0.3` | Fertilizer contribution to inflation |
| `inflation_weight_water` | float | `0.4` | Water contribution to inflation |

### Interest rate (Taylor rule)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `neutral_rate` | float | `0.03` | Neutral real interest rate |
| `inflation_target` | float | `0.02` | Central bank inflation target |
| `taylor_reversion` | float | `0.5` | Reversion speed toward neutral rate |
| `taylor_inflation_coeff` | float | `1.5` | Response coefficient to inflation gap |
| `taylor_debt_coeff` | float | `0.5` | Response coefficient to debt gap |
| `debt_crisis_rate_premium` | float | `0.02` | Additional risk premium in debt crisis |

### Exchange rate

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `trade_balance_fx_sensitivity` | float | `0.001` | Trade balance effect on FX |
| `fx_mean_reversion` | float | `0.01` | FX mean reversion |
| `capital_flight_intensity` | float | `0.05` | Currency crisis capital flight |
| `capital_flow_fx_scale` | float | `0.001` | Cross-region capital flow FX effect |
| `interest_coupling_scale` | float | `0.01` | Cross-region interest rate coupling |

### Bond yield

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `bond_yield_adjustment_speed` | float | `0.1` | Speed of convergence to theoretical yield |

### Exchange average

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `exchange_avg_window` | float | `30.0` | Days for moving-average exchange rate |

### Crisis thresholds

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `debt_crisis_threshold` | float | `1.0` | Debt/GDP level triggering debt crisis |
| `debt_crisis_sharpness` | float | `10.0` | Sigmoid sharpness for debt crisis |
| `currency_crisis_threshold` | float | `0.2` | 20% depreciation threshold |
| `currency_crisis_sharpness` | float | `20.0` | Sigmoid sharpness for currency crisis |
| `unrest_inequality_threshold` | float | `0.6` | Inequality threshold for social unrest |
| `unrest_inequality_sharpness` | float | `10.0` | Sigmoid sharpness |
| `unrest_inflation_threshold` | float | `0.1` | Inflation threshold for social unrest |
| `unrest_inflation_sharpness` | float | `20.0` | Sigmoid sharpness |
| `water_scarcity_fraction` | float | `0.1` | 10% of initial stock threshold |
| `water_scarcity_sharpness` | float | `0.1` | Sigmoid sharpness |

### Solver defaults

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `default_method` | str | `"BDF"` | ODE integration method |
| `default_rtol` | float | `1e-6` | Relative tolerance |
| `default_atol` | float | `1e-8` | Absolute tolerance |

## Serialization

```python
from model_config import ModelConfig

cfg = ModelConfig(trade_scale=1.0, k_half=50.0)
cfg.to_json("my_config.json")

# Load later
cfg2 = ModelConfig.from_json("my_config.json")
```

!!! note
    See also the auto-generated API reference for `model_config`: [API — Sensitivity \u0026 Calibration](../api/sensitivity.md).
