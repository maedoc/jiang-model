# Global Refinery Sabotage

A global campaign against refinery infrastructure is a recurring narrative in strategic-threat assessments. The model treats it as a multi-region supply shock rather than a chokepoint closure.

## Geopolitical situation

The GT#21 narrative claims "over 50 oil factories on fire in 45 days" across Russia, Myanmar, and other locations. This would imply a massive, coordinated sabotage campaign.

## Intervention definition

```python
from interventions import multi_region_supply_shock

iv = multi_region_supply_shock(
    name="Global refinery sabotage",
    regions=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],  # all regions
    resource="oil_production",
    onset_day=100.0,
    ramp_days=5.0,
    severity=0.025,  # 2.5% of global capacity
)
```

Note the **severity=0.025** (2.5%). This is not a typo.

## Empirical grounding

| Claim | Narrative value | Empirical bound | Source | Status |
|-------|---------------|---------------|--------|--------|
| "50 refinery fires in 45 days" | Implies ~10–15% global capacity offline | IEA global outage ceiling ≈ 2.5% | IEA supply-shock scenarios | **Rejected** |
| Coordinated global sabotage | Implies synchronized multi-region attack | No historical precedent beyond 1973 (partial, regional) | — | **Unverified** |

The IEA maintains a global refinery outage ceiling based on spare capacity, maintenance schedules, and strategic reserves. A 2.5% global outage is already at the upper bound of what markets can absorb without triggering emergency stock release (SPR/IEA coordinated action).

## Model behavior

Even at 2.5% severity, the model shows:
- Oil price spikes of 20–40% in net-importing regions.
- Stability degradation in resource-dependent economies.
- Debt accumulation as governments subsidize fuel costs.

A 10% severity (as implied by the GT#21 narrative) produces numerically unstable outcomes: negative oil stocks, political stability collapse spirals, and solver divergence. This is a **model consistency check** rather than a calibrated scenario.

## Status

This scenario is included for completeness but is flagged as **narrative-unverified**. See [Rejected / Unverified](../empirical/rejected.md) for detailed discussion.
