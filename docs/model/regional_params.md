# Regional Parameters

The `real_params.json` file holds **per-region parameters** for the 12 model regions. These are distinct from `ModelConfig` structural coefficients.

## JSON schema

Top-level keys (each is length-12 for regions, or 12×12 for matrices):

| Key | Shape | Description |
|-----|-------|-------------|
| `oil_production` | (12,) | Daily production by region |
| `oil_consumption` | (12,) | Daily consumption by region |
| `fertilizer_production` | (12,) | Daily fertilizer production |
| `fertilizer_consumption` | (12,) | Daily fertilizer consumption |
| `oil_trade` | (12, 12) | Bilateral oil trade matrix |
| `fertilizer_trade` | (12, 12) | Bilateral fertilizer trade matrix |
| `stability_decay` | (12,) | Region-specific stability decay rate |
| `stability_gain` | (12,) | Region-specific stability gain rate |
| `stability_coupling` | (12, 12) | Bilateral stability diffusion matrix |

## Per-region summary

| Region | Oil prod | Oil cons | Fert prod | Fert cons | Net oil | Key trade partners |
|--------|----------|----------|-----------|-----------|---------|-------------------|
| North America | High | High | High | High | Surplus | Europe, Asia |
| Europe | Low | High | Med | Med | Deficit | Russia, Middle East |
| Russia | High | Low | Med | Low | Surplus | Europe, China |
| Middle East | Very high | Low | Low | Med | Very high | Asia, Europe |
| China | Low | Very high | High | Very high | Deficit | Middle East, Russia, SE Asia |
| India | Med | High | Med | High | Deficit | Middle East, SE Asia |
| Japan | Very low | High | Low | Med | Deficit | Middle East, SE Asia |
| SE Asia | Med | Med | High | High | Mixed | China, Japan, India |
| Australia/NZ | Med | Low | High | Low | Surplus | Asia |
| Africa | Med | Low | Low | Low | Mixed | Europe, Asia |
| South America | Med | Med | Med | Med | Mixed | North America, Europe |
| Central Asia | Med | Low | Med | Low | Mixed | Russia, China |

!!! note
    Exact numeric values are omitted here because they are scaled model units (~200 global total) rather than raw physical kb/d. See `real_params.json` for precise values.

## Loading parameters

```python
from geopolitical_model import load_parameters

params = load_parameters("real_params.json")

# Access
params["oil_production"]          # list of 12 floats
params["oil_trade"][i][j]        # flow from region j to region i
```

## Trade matrix structure

```python
# oil_trade[i][j] = net flow from region j to region i
# Columns sum to production surplus
# Rows sum to consumption deficit
```

The matrix is computed by `generate_params.py` from the country-level data in `data_loader.py` using a surplus-proportional allocation heuristic.

!!! warning
    The trade matrices are heuristics, not observed bilateral flows. UN Comtrade substitution is flagged as a future improvement. See [Data Sources](../data_sources.md).
