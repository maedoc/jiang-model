# Model Overview

The Geopolitical Resource Dynamics Model is a nonlinear dynamical-systems simulator of resource, economic, and political interactions across **12 geopolitical regions** and **15 state variables per region** (180 coupled ODEs).

## Architecture

```
geopolitical_model.py    Core ODE system (180 equations)
model_config.py          ~60 structural coefficients (ModelConfig dataclass)
interventions.py         Composable time-resolved interventions
scenarios.py             Scenario definition and comparison runner
trajectory.py            Structured output with named access & inverse transforms
sensitivity.py           Morris screening & parameter sweeps
historical_calibration.py   Calibration framework for crisis periods
data_loader.py           Real-world data loading and aggregation
real_params.json         Regional parameters for 12 regions
```

## Purpose

The model is designed for **counterfactual analysis**:
1. Define a baseline (365-day simulation with default parameters).
2. Layer on interventions (chokepoints, sanctions, supply shocks, naval blockades).
3. Compare resulting trajectories via `TrajectoryComparison`.

## Quick start

```python
from geopolitical_model import GeopoliticalModel, load_parameters
from model_config import ModelConfig

model = GeopoliticalModel(
    load_parameters("real_params.json"),
    ModelConfig(trade_scale=1.0, k_half=50.0, initial_stock_days=90.0),
)
traj = model.simulate(t_span=(0, 365))
print(traj.summary())
```

## Model pipeline

```
Data sources (EIA, IEA, World Bank, FAO)
    ↓
data_loader.py  →  Country-level CSVs
    ↓
generate_params.py  →  Aggregation + scaling  →  real_params.json
    ↓
GeopoliticalModel(params, config, interventions)
    ↓
simulate(t_span)  →  Trajectory(180 variables × T timesteps)
    ↓
TrajectoryComparison(base, shock)  →  Impact ranking, max deviation, summary
```

## Numerical solver

The system is **stiff** and requires an implicit solver. Default:
- Method: `BDF` (Backward Differentiation Formula)
- Relative tolerance: `1e-6`
- Absolute tolerance: `1e-8`

Explicit methods (e.g., forward Euler) diverge due to the stiffness of debt, price, and stability feedback loops.
