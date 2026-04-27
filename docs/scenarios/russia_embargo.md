# Russia Oil Embargo

A full embargo on Russian oil exports models the upper-bound of 2022-style EU sanctions—extended to a complete cutoff rather than the observed 60–70% reduction.

## Geopolitical situation

Russia is a major resource surplus region (CIS production ~13,868 kb/d vs consumption ~4,636 kb/d). Cutting Russian exports forces a dependency shift toward North America and the Middle East.

## Intervention definition

```python
from interventions import russia_oil_embargo

iv = russia_oil_embargo(
    onset_day=0.0,
    severity=0.9,
    ramp_days=30.0,
)
```

This targets `oil_trade_flow` only, with `exporter_region=2` (Russia).

## Empirical grounding

| Metric | Value | Source |
|--------|-------|--------|
| Russian oil production (2023) | ~13,868 kb/d | Energy Institute |
| Russian consumption (2023) | ~4,636 kb/d | Energy Institute |
| Surplus (exportable) | ~9,232 kb/d | Derived |
| EU sanctions observed reduction | ~60–70% of exports to Europe | 2022–2023 trade data |
| Model severity | 85–90% | Upper-bound hypothetical |

## Key results

- Europe is the most affected importer (historically ~30% of oil from Russia).
- North America and Middle East gain market share.
- Price effects are globally distributed but strongest in Europe.
- The model's fixed-trade matrix overstates the speed of substitution; price-mediated trade extension (see [Price-Mediated Trade](price_trade.md)) partially corrects this.
