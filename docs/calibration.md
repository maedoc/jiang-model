# Calibration

The `historical_calibration.py` module calibrates model parameters to match observed crisis trajectories. It is used to parameterize counterfactual "what-if" baselines rather than to forecast.

## Framework

```python
from historical_calibration import HistoricalCalibrator

cal = HistoricalCalibrator(base_params, period='1973')
optimal_params = cal.fit(target_df)
```

The calibrator:
1. Loads a baseline parameter set (`real_params.json`).
2. Accepts a target DataFrame (time series of observed variables).
3. Minimizes a weighted L2 loss between simulated and target trajectories.
4. Applies an optional L2 regularization penalty to keep parameters near their base values.

## Supported target variables

| Target name | Trajectory accessor | Typical crisis signature |
|-------------|---------------------|--------------------------|
| `oil_price` | `traj.oil_price` | Supply-shock spike |
| `debt_to_gdp` | `traj.debt_gdp` | Contagion-driven rise |
| `inflation` | `traj.inflation` | Monetary shock |
| `interest_rate` | `traj.interest_rate` | Policy response |
| `political_stability` | `traj.stability` | Collapse or resilience |

## Calibrated crisis periods

### 1973 oil crisis

```python
params = load_parameters("params_1973.json")
```

- **Key features**: Sudden Middle-East supply reduction (~15% global), inflation spike, debt accumulation in importing regions.
- **Target data**: `historical_1973.csv` (synthetic for testing; replace with OECD/World Bank series).

### 2008 financial crisis

```python
params = load_parameters("params_2008.json")
```

- **Key features**: Trade freeze, currency volatility, debt/GDP jump in Europe and North America.
- **Target data**: `historical_2008.csv` (synthetic for testing).

## Loading calibrated parameters

```python
from geopolitical_model import load_parameters

params_1973 = load_parameters("params_1973.json")
model = GeopoliticalModel(params_1973)
traj = model.simulate(t_span=(0, 365))
```

## Next steps

- Replace synthetic target CSVs with real OECD / World Bank historical series.
- Validate out-of-sample: calibrate on 1973–1975, test on 1979 oil shock.
- Sensitivity analysis of calibration weights (see [Sensitivity Analysis](sensitivity.md)).
