# Real-World Data Integration for Geopolitical DDE Model

This document describes the integration of real-world data into the JAX-based Delay Differential Equation (DDE) model for geopolitical resource dynamics.

## Overview

The original model used arbitrary parameters for three regions (Middle East, Asia, North America) with state variables: Oil supply (O), Fertilizer supply (F), Political stability (S). This extension replaces arbitrary parameters with real‑world data and expands the model to 12 geopolitical regions.

## Data Sources

1. **Oil production and consumption** – Our World in Data (`oil‑production‑by‑country.csv`, `oil‑consumption‑by‑country.csv`), originally from the Energy Institute Statistical Review of World Energy (2023). Data are in terawatt‑hours per year.

2. **Fertilizer consumption** – Our World in Data (`fertilizer‑total‑use.csv`), sourced from FAO. Data are in tonnes per year.

3. **Political stability** – World Bank Worldwide Governance Indicators (WGI) “Political Stability and Absence of Violence/Terrorism” (indicator `PV.EST`). Values range from –2.5 to +2.5, normalized to 0–1.

4. **Country‑to‑region mapping** – Custom mapping of ISO3 codes to 12 geopolitical regions (see `data_loader.py`).

5. **Trade flows** – Estimated from production‑consumption surplus/deficit using a simple proportional‑allocation algorithm. Real trade matrices can be substituted from UN Comtrade or similar sources.

## File Structure

- `dde_model.py` – original three‑region model (unchanged).
- `data_loader.py` – functions to download, load, and aggregate country‑level data.
- `generate_params.py` – generates scaled parameters and trade matrices, saves `real_params.json`.
- `dde_model_extended.py` – generalized DDE model that works with any number of regions.
- `real_params.json` – generated parameter set for 12 regions (scaled to model units).
- `oil_production.csv`, `oil_consumption.csv`, `fertilizer_total_use.csv` – downloaded data files.

## Region Definitions

1. North America (USA, CAN, MEX)
2. Europe (EU + UK, Norway, Switzerland, etc.)
3. Russia
4. Middle East (GCC, Iran, Iraq, Turkey, Egypt)
5. China (including Taiwan, Hong Kong, Macau)
6. India
7. Japan
8. Southeast Asia (ASEAN members)
9. Australia/New Zealand
10. Africa (sub‑Saharan)
11. South America
12. Central Asia/Caucasus

## Usage

### 1. Download the data

```bash
cd dde_model
python data_loader.py
```

This downloads the three CSV files from Our World in Data.

### 2. Generate real‑world parameters

```bash
python generate_params.py
```

This reads the CSV files, aggregates to regions, scales the values, computes trade matrices, and saves `real_params.json`.

### 3. Run the extended model

```bash
python dde_model_extended.py
```

The script loads `real_params.json`, initializes the 12‑region model, runs a 365‑day simulation with a Strait of Hormuz disruption at day 100, and produces two plots:
- `real_simulation_resources.png` – oil, fertilizer, and stability trajectories.
- `real_simulation_choke_point.png` – disruption factor and shipping delay.

## Parameter Scaling

Real‑world data are given in physical units (TWh/year for oil, tonnes/year for fertilizer). To keep the numerical integration stable, the aggregates are scaled so that total oil production and total fertilizer production each sum to 200 “model units” per day. This preserves regional proportions while matching the order of magnitude of the original arbitrary parameters.

Trade flows are computed as the deficit of a region allocated proportionally to the surplus of exporting regions. The resulting flow matrix (units/day) is stored as `oil_trade_flow` and `fertilizer_trade_flow`. The coupling term in `dde_model_extended.py` uses these flows directly, modulated by the exporter’s political stability.

## Model Stability Notes

The current parameter set may produce unstable simulations (negative diverging stocks) because:

- Some regions have large consumption‑production imbalances (e.g., Europe, Asia).
- The political‑stability feedback can lead to a collapse spiral when resource stocks become negative.
- The Euler integration with a 1‑day step may be too coarse for stiff dynamics.

**Suggested improvements:**

1. **Add resource stock lower bounds** – prevent O and F from becoming negative (or impose a minimum strategic reserve).
2. **Reduce the time step** – use DT = 0.1 or 0.01 days.
3. **Tune stability dynamics** – adjust `stability_decay` and `stability_gain` to slow down political feedback.
4. **Introduce price mechanisms** – high deficits could raise prices, reducing consumption and attracting more trade.
5. **Use a more robust integration scheme** – e.g., Runge‑Kutta 4 with interpolated delay history.

## Extending the Model

- **Additional state variables** – water resources, military expenditure, sovereign debt can be added by extending `state_dim` and adding corresponding equations.
- **More accurate trade data** – replace the surplus‑based heuristic with real bilateral trade matrices from UN Comtrade.
- **Time‑varying parameters** – load multiple years and simulate evolving production/consumption trends.
- **Stochastic disruptions** – replace the deterministic Hormuz disruption with a random process.

## Dependencies

- Python 3.9+
- JAX, JAXlib
- NumPy, Matplotlib, Pandas, Requests
- wbdata (for World Bank Governance Indicators)
- pycountry (for country‑code mapping)

All dependencies are listed in `pyproject.toml`.

## License

MIT

## Recent Improvements (April 2025)

### 1. Water Resources and Trade
- Added water availability and consumption data (km³/year) scaled to per‑day model units.
- Water trade matrix (`water_trade_flow`) computed from regional surplus/deficit.
- Integrated water stocks and flows into the extended ODE model.

### 2. Financial Coupling
- Capital flow matrix (`capital_flow`) for financial contagion (proportional to trade volume and stability).
- Financial coupling matrix (`financial_coupling`) for interest‑rate and exchange‑rate spillovers.
- Enabled inter‑region financial coupling in the ODE dynamics.

### 3. Debt Dynamics Stabilization
- Revised sovereign debt equations with fiscal rule, austerity factor, soft ceiling (debt ≤ 5×GDP), and mean reversion.
- Debt/GDP now remains bounded (0.15–5.26) over 365‑day simulations; no exponential explosion.

### 4. Scale Normalization
- Water parameters scaled to target 200 units/day (same order as oil and fertilizer).
- All resource flows now in consistent per‑day units.

### 5. Updated Code
- `data_loader.py`: new functions for water‑trade and financial matrices.
- `generate_params.py`: water scaling, addition of three new matrices.
- `ode_model_extended.py`: use of new matrices, improved debt dynamics, financial coupling.
- `real_params.json`: includes all new matrices and scaled water data.

### 6. Validation
- 365‑day simulation runs without numerical instability.
- Debt remains bounded, water stocks positive, no variable exceeds reasonable limits.

### 7. Nonlinear Thresholds and Historical Calibration
- **Nonlinear thresholds** implemented with smooth sigmoid transitions:
  - Debt crisis: triggers when debt > 100% GDP, adds risk premium to interest rates.
  - Currency crisis: triggers when 30‑day depreciation > 20%, amplifies capital flight.
  - Social unrest: triggers when inequality > 0.6 AND inflation > 0.1, reduces stability gain.
  - Resource scarcity: triggers when water stock < 10% of initial, increases water price.
- **Historical calibration framework** (`historical_calibration.py`) calibrates model parameters to historical crisis periods (1973‑1975 oil crisis, 2008‑2010 financial crisis).
  - Synthetic historical data generated for testing (`historical_1973.csv`, `historical_2008.csv`).
  - Calibrated parameter sets produced (`params_1973.json`, `params_2008.json`).
- **Financial coupling** refined using calibrated parameters; capital flow and financial coupling matrices now active.
- **Exchange‑rate moving average** (`log_exchange_avg`) added for currency‑crisis detection.

### 8. Next Steps
- Validation simulations (365 days) with historical crisis scenarios.
- Sensitivity analysis of threshold parameters.
- Integration of real historical data (e.g., OECD, World Bank) for calibration.

## References

- Energy Institute (2023). *Statistical Review of World Energy*. https://www.energyinst.org/statistical-review
- Our World in Data. https://ourworldindata.org
- World Bank Worldwide Governance Indicators. https://databank.worldbank.org/source/worldwide-governance-indicators
- FAO FAOSTAT. https://www.fao.org/faostat