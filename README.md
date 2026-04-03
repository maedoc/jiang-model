# Geopolitical Resource Dynamics Model

A nonlinear dynamical systems model simulating resource, economic, and political interactions across 12 geopolitical regions with 15 state variables per region (180 ODEs total). The model captures feedback loops between resource stocks, political stability, inequality, sovereign debt, prices, and financial variables.

## Model Overview

### Key Features
- **12 geopolitical regions**: North America, Europe, Russia, Middle East, China, India, Japan, Southeast Asia, Australia/New Zealand, Africa, South America, Central Asia/Caucasus
- **15 state variables per region**: 
  1. Oil stock (log-transformed)
  2. Fertilizer stock (log-transformed)
  3. Political stability (0-1)
  4. Water stock (log-transformed)
  5. Military expenditure (log-transformed)
  6. Inequality (Gini, logit-transformed)
  7. Sovereign debt/GDP ratio (log-transformed)
  8. Oil price (log-transformed)
  9. Fertilizer price (log-transformed)
  10. Water price (log-transformed)
  11. Inflation rate
  12. Interest rate
  13. Exchange rate (log-transformed)
  14. Bond yield
  15. 30-day moving average of exchange rate (log-transformed)

### Core Dynamics
- **Resource flows**: Production, consumption, and bilateral trade with half-saturation limits
- **Political stability**: Affected by resource abundance, social unrest, and regional coupling
- **Financial coupling**: Interest rate and exchange rate spillovers between regions
- **Nonlinear thresholds**: Debt crises, currency crises, social unrest, resource scarcity
- **Hormuz disruption**: Configurable disruption of Middle East exports (day 100 default)

### Model Evolution
- **Original**: 3-region Delay Differential Equation (DDE) model with shipping delays
- **Current**: 12-region Ordinary Differential Equation (ODE) model without delays (simplified for numerical stability)
- **Rationale**: ODE framework more suitable for stiff systems with many variables; delays can be reintroduced as needed
- **Backward compatibility**: Original DDE model preserved in `dde_model.py` for reference

## Recent Accomplishments

### 1. **Stiffness Resolution**
- **Problem**: Original price balance formula `(consumption - production) / (production + EPS)` caused extreme stiffness when production = 0 (Japan oil)
- **Solution**: Normalized balance `(consumption - production) / (consumption + production + EPS)` bounds derivative to [-1, 1]
- **Result**: System remains stiff but manageable with BDF solver; derivatives reduced from 10⁸ to ~10⁰

### 2. **Debt Dynamics Stabilization**
- **Problem**: Debt exploded (>10²⁷) due to unscaled annual interest rates in daily ODE
- **Solution**: Added `DAILY_SCALE = 1/365.25` to convert annual rates to daily
- **Fixed equation**: `(interest * DAILY_SCALE - growth_rate) * debt`
- **Result**: Debt now bounded between -1.0 and 2.62 over 365-day simulations

### 3. **Performance Optimization**
- **Numba acceleration**: 80x speedup over pure Python implementation
- **Maintained correctness**: Numba output matches original within numerical tolerance
- **Efficient integration**: SciPy's BDF solver handles stiffness; RK4 removed due to instability

### 4. **Real-World Parameterization**
- **Data sources**: Oil/fertilizer production/consumption from Energy Institute (2023), political stability from World Bank WGI, financial data from central banks
- **Trade matrices**: Estimated from production-consumption surpluses
- **Calibration**: Historical scenarios (1973 oil crisis, 2008 financial crisis)

## Model Specifications

### ODE System
- **Total equations**: 180 (12 regions × 15 variables)
- **Integration method**: SciPy `solve_ivp` with BDF (Backward Differentiation Formula)
- **Time span**: Configurable, tested up to 365 days
- **Solver tolerances**: `rtol=1e-6`, `atol=1e-8` (adjustable)

### Key Nonlinearities
1. **Trade limitation**: `resource / (resource + K_HALF)` with `K_HALF = 1000`
2. **Debt crisis**: Sigmoid trigger when debt > 100% GDP
3. **Currency crisis**: 30-day depreciation > 20%
4. **Social unrest**: Inequality > 0.6 AND inflation > 0.1
5. **Resource scarcity**: Water stock < 10% of initial
6. **Austerity factor**: Sigmoid reduction in government spending near debt ceiling

### Transformations for Stability
- **Positive variables** (oil, fertilizer, water, military, debt, prices, exchange): `log(1 + x)`
- **Bounded variables** (stability, inequality): logit transform
- **Untransformed**: Inflation, interest rate, bond yield

## Assumptions and Limitations

### 1. **Economic Simplifications**
- GDP proxy: `oil_prod × stability + fert_prod × stability`
- Government spending: 1% of GDP × military expenditure
- Tax revenue: 30% of GDP × stability
- Primary deficit drives debt accumulation

### 2. **Financial Market Assumptions**
- Taylor rule: Interest rate responds to inflation and debt deviations
- Exchange rate: Influenced by trade balance and capital flows
- Bond yield: Follows interest rate plus debt crisis premium
- No explicit banking sector or credit creation

### 3. **Resource Dynamics**
- Water: Simplified availability vs. consumption (no climate variability)
- No substitution between resources (oil ↔ fertilizer ↔ water)
- Trade flows proportional to surpluses (not price-mediated)
- No strategic reserves or stockpiling policies

### 4. **Political and Social Dynamics**
- Stability coupling: Diffusive spread between regions
- Inequality: Increases with low stability and high debt
- Military expenditure: Grows with GDP, reduced by debt crisis
- No explicit regime changes or civil wars

### 5. **Numerical Considerations**
- System is stiff due to trade nonlinearities and financial coupling
- BDF solver required; explicit methods (RK4) unstable
- Some variables may require clipping to prevent numerical overflow
- Daily time scale with annual-rate conversions

## Usage

### Installation
```bash
cd dde_model
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Basic Simulation
```python
from ode_model_extended import load_parameters, ExtendedODEModel

params = load_parameters("real_params.json")
model = ExtendedODEModel(params)
sol = model.simulate(t_span=(0.0, 365.0), method="BDF", rtol=1e-6, atol=1e-8)
model.plot_results(sol)
```

### Numba-Accelerated Version
```python
from ode_model_extended_numba import ExtendedODEModelNumba

model = ExtendedODEModelNumba(params)  # Automatically uses Numba if available
sol = model.simulate(t_span=(0.0, 365.0))
```

### Validation and Testing
```bash
# Check stability and bounds
python3 check_stability_and_bounds.py

# Test Numba acceleration
python3 test_numba_acceleration.py

# Run 365-day validation
python3 validate_365.py
```

## Key Files

### Core Implementation
- `ode_model_extended.py` - Main ODE model with 15 variables per region
- `ode_model_extended_numba.py` - Numba-accelerated version (80x speedup)
- `data_loader.py` - Real-world data loading and aggregation
- `real_params.json` - Generated parameters for 12 regions

### Testing and Validation
- `check_stability_and_bounds.py` - Analyzes stiffness and variable bounds
- `test_numba_acceleration.py` - Verifies Numba correctness and performance
- `validate_365.py` - 365-day simulation test
- `debug_debt.py` - Debt dynamics debugging

### Historical Calibration
- `historical_calibration.py` - Calibration framework for crisis periods
- `params_1973.json`, `params_2008.json` - Calibrated parameters
- `generate_calibrated_params.py` - Parameter generation for historical scenarios

## Next Steps

### Short-term (Implementation Ready)
1. **Additional choke points**: Malacca Strait, Suez Canal with configurable disruptions
2. **Policy interventions**: Sanctions, strategic reserves, austerity packages
3. **Scenario analysis**: Comparative simulations with/without interventions
4. **Enhanced visualization**: Interactive dashboards, regional heatmaps

### Medium-term (Requires Design)
5. **Stochastic elements**: Random disruptions, policy uncertainty
6. **Price-mediated trade**: Endogenous trade flows based on price differentials
7. **Financial sector**: Banking system, credit availability, sovereign risk spreads
8. **Climate variability**: Water availability shocks, agricultural impacts

### Long-term (Research Directions)
9. **Machine learning calibration**: Bayesian inference for parameter estimation
10. **Network analysis**: Graph-theoretic study of systemic risk propagation
11. **Multi-scale modeling**: Coupling with agent-based regional models
12. **Policy optimization**: Reinforcement learning for optimal intervention timing

## Performance Notes
- **Numba acceleration**: 80x speedup crucial for parameter sweeps and sensitivity analysis
- **Memory usage**: ~180 state variables × time points (manageable for 365 days)
- **Integration time**: ~1-2 seconds for 365-day simulation with BDF solver
- **Parallelization**: Region-level computations already vectorized; trade loops serial

## References
- **Data sources**: Energy Institute Statistical Review (2023), World Bank WGI, FAO
- **Methodology**: Inspired by macroeconomic DSGE models and ecological Lotka-Volterra systems
- **Software**: SciPy for ODE integration, Numba for acceleration, Matplotlib for visualization

## License
MIT