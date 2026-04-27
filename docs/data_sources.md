# Data Sources

The model integrates real-world energy, governance, and economic data at the country level, then aggregates to the 12 geopolitical regions.

## Sources table

| Source | Type | Coverage | Used in model file | Last updated |
|--------|------|----------|-------------------|--------------|
| Energy Institute Statistical Review of World Energy (2023) | Oil production and consumption by country | Global, annual | `data_loader.py` → `oil_production.csv`, `oil_consumption.csv` | 2023 |
| FAO FAOSTAT | Fertilizer total use by country | Global, annual | `data_loader.py` → `fertilizer_total_use.csv` | 2023 |
| World Bank Worldwide Governance Indicators | Political stability (`PV.EST`) | Global, annual | `data_loader.py` | 2023 |
| UN Comtrade (estimated) | Bilateral trade matrices | Regional aggregates | `generate_params.py` (surplus-allocation heuristic) | Ongoing |

## Aggregation methodology

1. **Download** — `data_loader.py` fetches CSVs from Our World in Data mirrors.
2. **Map** — ISO3 country codes are mapped to the 12 model regions via a custom lookup table.
3. **Aggregate** — Country-level values are summed to regional totals.
4. **Scale** — Regional totals are scaled so that global oil and fertilizer production each sum to ≈200 model units per day. This preserves regional proportions while keeping the ODE solver numerically stable.

## Parameter scaling notes

Real-world data arrive in physical units (TWh/year for oil, tonnes/year for fertilizer). The scaling pipeline is:

```python
# Pseudo-code from generate_params.py
regional_production = aggregate_to_regions(country_data)
scale_factor = 200.0 / regional_production.sum()
model_units = regional_production * scale_factor
```

Trade flows are computed as the deficit of a region, allocated proportionally to the surplus of exporting regions. The resulting matrices (`oil_trade_flow`, `fertilizer_trade_flow`, `water_trade_flow`) are stored in `real_params.json`.

## Extending the data pipeline

- Replace the surplus-allocation heuristic with real bilateral trade matrices from UN Comtrade.
- Load multiple years to simulate evolving production/consumption trends.
- Add water-availability data (km³/year) scaled to per-day model units.

!!! note
    The current trade matrices are heuristics, not observed bilateral flows. This is a known limitation flagged in `MATH_SPEC.md` §8.
