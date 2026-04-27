# Panama Canal Disruption

The Panama Canal is not a primary crude-oil chokepoint, but it is critical for US LPG/LNG exports to Asia and for South American rerouting.

## Geopolitical situation

In the current crisis, the canal has become a *surge artery*: vessel transits have risen to 36–38/day, near capacity, as shippers reroute away from Hormuz.

## Intervention definition

```python
from interventions import panama_disruption

iv = panama_disruption(
    onset_day=100.0,
    severity=0.55,
    ramp_days=14.0,
)
```

## Empirical grounding

| Metric | Value | Source |
|--------|-------|--------|
| Normal oil throughput (2024) | ~2.0 mb/d | EIA |
| 1H2025 annualized | ~2.3 mb/d | EIA |
| Share of world maritime oil trade | ~2.5–3% | Derived from EIA global totals |
| US LPG exports to Asia via Panama | >95% | Gulf News 2026 |
| Current crisis surge | 36–38 vessel transits/day (near capacity) | Gulf News, Ecoticias April 2026 |

**Model insight**: A Panama disruption primarily affects **South America's exports to Asia** and **US energy rerouting**, not global crude supply directly. In the compound multi-chokepoint scenario, Panama acts as an amplifier: if Hormuz is already closed, shippers try to reroute through Panama, and *then* Panama closure removes the last alternative.

## Key results

- Panama alone has limited global oil impact (~2.5–3% of seaborne trade).
- In combination with Hormuz + Malacca, Panama closure removes the final rerouting option for Western Hemisphere suppliers.
- The >95% US LPG dependency means Asian petrochemical feedstock is disproportionately affected.
