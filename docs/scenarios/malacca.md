# Malacca Strait Disruption

The Strait of Malacca carries ~22.5–23.7 mb/d of oil (ANRPC 1H2025), making it the largest maritime oil conduit by volume. Unlike Hormuz, there is no practical pipeline alternative for Middle East→Asia routing.

## Geopolitical situation

A Malacca disruption would not require physical closure. Insurance-driven traffic avoidance—mirroring the Hormuz mechanism—would reroute vessels through the longer Sunda/Lombok straits or the Myanmar–China pipeline (limited capacity). The practical effect is a delay and cost shock rather than a volume cutoff.

## Intervention definition

```python
from interventions import malacca_disruption

iv = malacca_disruption(
    onset_day=100.0,
    severity=0.75,
    ramp_days=14.0,
)
```

This applies `chokepoint_disruption` to `exporter_region=7` (Southeast Asia), affecting all three trade matrices (oil, fertilizer, water).

## Empirical grounding

| Metric | Value | Source |
|--------|-------|--------|
| 2024 oil throughput | ~22.5–23.7 mb/d | EIA, ANRPC |
| Share of world maritime oil trade | ~28–30% | EIA 2024/2025 |
| Combined Hormuz + Malacca share | ~57% of all seaborne oil trade | EIA |
| China imports via Malacca | ~7.9 mb/d (~48% of China's imports) | ANRPC 1H2025 |
| South Korea via Malacca | ~2.4 mb/d | ANRPC |
| Japan via Malacca | ~2.1 mb/d | ANRPC |

**Model insight**: Malacca disruption is arguably *more* damaging to China than Hormuz closure alone, since it is the conduit for most non-Russian oil reaching East Asia. Even if Hormuz were bypassed via pipeline, Malacca is the only practical sea route to China/Japan/Korea.

## Key results

- A combined Hormuz + Malacca shock would trap **~60–70% of China's oil imports**.
- Unlike Hormuz, Malacca has **no significant pipeline bypass**.
- The ASEAN region (Southeast Asia) is treated as a net exporter in the model's trade matrix; in reality the region is a net importer. This is acknowledged as a model limitation.

!!! warning
    The model treats Southeast Asia as a net exporter. In reality, ASEAN is a net importer. A Malacca disruption in the model therefore has a different sign than the real-world effect. See [Rejected / Unverified](../empirical/rejected.md).
