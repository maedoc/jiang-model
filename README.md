# Geopolitical Resource Dynamics Model

A nonlinear dynamical systems model simulating resource, economic, and
political interactions across 12 geopolitical regions.  Each region carries
15 state variables (180 coupled ODEs), capturing feedback loops between
resource stocks, political stability, inequality, sovereign debt, commodity
prices, and financial contagion.

The model is designed for **counterfactual analysis**: define a baseline,
layer on interventions (chokepoints, sanctions, supply shocks), and compare
the resulting trajectories.

## Quick Start

```bash
# Create virtual environment and install dependencies
python -m venv env && source env/bin/activate
pip install -r requirements.txt

# Run a baseline simulation
python -c "
from geopolitical_model import GeopoliticalModel, load_parameters
model = GeopoliticalModel(load_parameters())
traj = model.simulate(t_span=(0, 365))
print(traj.summary())
"
```

## Example Scripts

| Script | Description |
|--------|-------------|
| `example_hormuz.py` | Baseline vs Hormuz closure counterfactual |
| `example_sanctions.py` | Russia oil embargo and bilateral sanctions |
| `example_sensitivity.py` | Parameter sweeps and Morris screening |
| `example_price_trade.py` | Price-mediated trade extension |
| `example_multi_chokepoint.py` | Hormuz + Malacca + Panama compound shock |
| `example_naval_blockade.py` | ME→China and ME+RU→China naval blockade |
| `test_empirical_constraints.py` | Verification that updated interventions match empirical bounds |

Each script generates PNG figures and prints summary tables to stdout.

## Architecture

```
geopolitical_model.py    Core ODE system (180 equations)
model_config.py          ~60 structural coefficients (ModelConfig dataclass)
interventions.py         Composable time-resolved interventions
trajectory.py            Structured output with named access & inverse transforms
scenarios.py             Scenario definition and comparison runner
sensitivity.py           Morris screening & parameter sweeps
historical_calibration.py   Calibration framework for crisis periods
data_loader.py           Real-world data loading and aggregation
real_params.json         Regional parameters for 12 regions
```

## Model Overview

### Regions (12)

| Idx | Region | Idx | Region |
|-----|--------|-----|--------|
| 0 | North America | 6 | Japan |
| 1 | Europe | 7 | Southeast Asia |
| 2 | Russia | 8 | Australia / NZ |
| 3 | Middle East | 9 | Africa (sub-Saharan) |
| 4 | China | 10 | South America |
| 5 | India | 11 | Central Asia / Caucasus |

### State Variables (15 per region)

| Idx | Variable | Transform |
|-----|----------|-----------|
| 0–1 | Oil stock, Fertilizer stock | log(1+x) |
| 2 | Political stability [0,1] | logit |
| 3 | Water stock | log(1+x) |
| 4 | Military expenditure | log(1+x) |
| 5 | Inequality (Gini) [0,1] | logit |
| 6 | Sovereign debt / GDP | log(1+x) |
| 7–9 | Oil, Fertilizer, Water price | log(1+x) |
| 10 | Inflation rate | none |
| 11 | Interest rate | none |
| 12 | Exchange rate | log(1+x) |
| 13 | Bond yield | none |
| 14 | Exchange rate 30-day avg | log(1+x) |

### Core Dynamics

- **Resources**: Production (stability-modulated), consumption, bilateral
  trade with Monod half-saturation limits
- **Stability**: Decay, resource-abundance gain, social unrest coupling,
  inter-region diffusion (logistic factor at boundaries)
- **Debt**: Primary deficit, interest–growth differential, mean reversion,
  austerity trigger via sigmoid
- **Prices**: Supply–demand imbalance, mean reversion to equilibrium
- **Inflation**: Weighted log-price derivatives
- **Interest rate**: Modified Taylor rule with debt gap and risk premium
- **Exchange rate**: Trade balance, capital flows, currency crisis dynamics
- **Bond yield**: Tracks interest rate + debt crisis premium

See [MATH_SPEC.md](MATH_SPEC.md) for the complete equation set.

### Nonlinear Thresholds

| Crisis | Trigger | Effect |
|--------|---------|--------|
| Debt crisis | Debt/GDP > 1.0 | Suppresses military, adds risk premium |
| Currency crisis | 30-day depreciation > 20% | Capital flight |
| Social unrest | Inequality > 0.6 AND inflation > 0.1 | Reduces stability |
| Water scarcity | Water < 10% of initial | Water price spike |

## Intervention API

```python
from interventions import hormuz_closure, russia_oil_embargo, bilateral_sanction
from interventions import EUROPE, RUSSIA

# Pre-built chokepoint
iv = hormuz_closure(onset_day=100, severity=0.8)

# Custom bilateral sanction
iv2 = bilateral_sanction("EU-Russia oil", sender=RUSSIA, receiver=EUROPE,
                          severity=0.9, ramp_days=30)
```

Interventions are composable and modify trade matrices / production arrays
at each solver time step.  See `interventions.py` for the full protocol.

## Scenario Comparison

```python
from scenarios import Scenario, compare_scenarios
from interventions import hormuz_closure

baseline = Scenario("Baseline")
hormuz = Scenario("Hormuz", interventions=[hormuz_closure()])

traj_b, traj_h, cmp = compare_scenarios(baseline, hormuz)
print(cmp.max_absolute_impact("oil_stock"))
```

## Configuration

All ~60 structural coefficients live in `ModelConfig`:

```python
from model_config import ModelConfig

cfg = ModelConfig(trade_scale=0.5, price_trade_enabled=True)
cfg.to_json("my_config.json")
cfg2 = ModelConfig.from_json("my_config.json")
```

## Sensitivity Analysis

```python
from sensitivity import parameter_sweep, morris_screening

# Sweep trade_scale from 0.001 to 1.0
vals, metrics = parameter_sweep("trade_scale", np.linspace(0.001, 1.0, 20))

# Morris screening of top parameters
results = morris_screening(["trade_scale", "price_response", "tax_rate"])
```

## Calibration

```python
from historical_calibration import HistoricalCalibrator

cal = HistoricalCalibrator(target_csv="historical_1973.csv")
best_params = cal.calibrate()
```

## Data Sources

- **Energy**: Energy Institute Statistical Review (2023) — oil/fertilizer production & consumption
- **Political**: World Bank Worldwide Governance Indicators — political stability
- **Financial**: Central banks, IMF — interest rates, debt/GDP, exchange rates
- **Trade matrices**: Estimated from production–consumption surpluses

## References and Empirical Grounding

Intervention severities and onset parameters are constrained by empirical data
from official energy and defense sources:

- **EIA** World Oil Transit Chokepoints (2024) — Hormuz, Malacca, Panama throughput
- **IEA** Strait of Hormuz Factsheet (June 2025) — flow-collapse scenarios
- **CSIS** "How War with Iran Could Disrupt Energy Exports" (2025) — AIS vessel data
- **ANRPC** (1H2025) — Malacca flow shares by destination
- **RAND** RRA591-1 "Alternative Futures Following a Great Power War" (2023) — distant blockade economics
- **DoD Comptroller** FY2026 Budget Request — $961.6B, +11.8% YoY
- **Reuters** "Pentagon approaches automakers" (April 2026) — GM/Ford talks
- **Energy Institute** Statistical Review of World Energy 2024 — regional production vs consumption
- **IEA** Oil Market Report (April 2026) — 2.6 mb/d supply swing during Hormuz crisis

See `outputs/chokepoint-empirical-constraints-brief.md` for the full research brief
with numbered citations and model-parameter recommendations.

## License

MIT