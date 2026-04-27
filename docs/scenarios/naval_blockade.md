# Naval Blockade

A naval blockade models the interdiction of bilateral trade by force—insurance collapse, boarding, and seizure—rather than a geographic chokepoint closure.

## Geopolitical situation

Game Theory #21 describes U.S. boarding of commercial vessels and seizure of tankers carrying energy bound for China. The empirical analog is the Iran-Iraq Tanker War (1984–1988), where physical damage was modest (~2–4% of flows) but traffic avoidance collapsed exports by 50–60%.

## Intervention definition

```python
from interventions import naval_blockade, bilateral_sanction, compose_interventions
from interventions import MIDDLE_EAST, RUSSIA, CHINA

# Scenario A: ME → China
iv_a = naval_blockade(
    sender=MIDDLE_EAST, receiver=CHINA,
    onset_day=100.0, severity=0.9, ramp_days=10.0,
)

# Scenario B: ME + Russia → China
iv_b = compose_interventions([
    naval_blockade(sender=MIDDLE_EAST, receiver=CHINA,
                   onset_day=100.0, severity=0.9, ramp_days=10.0),
    bilateral_sanction("RU→CN oil", sender=RUSSIA, receiver=CHINA,
                       onset_day=100.0, severity=0.7, ramp_days=10.0,
                       resources=["oil_trade_flow", "fertilizer_trade_flow"]),
])
```

## Empirical grounding

| Precedent | Physical damage | Traffic / export reduction | Source |
|-----------|----------------|---------------------------|--------|
| Iran-Iraq Tanker War (1984–88) | ~2–4% of flows | ~50–60% | Lloyd's, Strauss Center |
| Red Sea / Bab el-Mandeb (2023–24) | Modest | 42% Suez transit drop; 60–70% container diversion | Industry reports |
| RAND distant blockade of China | — | "Dramatically reduced" waterborne shipping; estimated 10–35% China GDP decline | RAND RRA591-1 |

## Output figures

![Naval blockade China](../assets/scenarios/naval_blockade_china.png)

*China oil stock and oil price under ME blockade vs ME+RU blockade. The Russia addition removes the last major alternative supplier, producing a steeper price spike and faster stock drawdown.*

![Naval blockade stability](../assets/scenarios/naval_blockade_stability.png)

*Political stability in Asia-Pacific regions. China stability falls sharply under the combined blockade; sender regions (Middle East, Russia) experience modest stability gains from reduced outbound dependence.*

## Key results

- **Asymmetry**: sender regions gain stability (less outbound dependency shock), while receiver regions lose stability and accumulate debt.
- **Compound Russia**: adding a Russia→China bilateral sanction removes China's last major pipeline alternative, producing the most severe price and stability effects in the library.
- **Speed**: unlike geographic chokepoint closures, naval blockades can be implemented within days (small ramp), producing faster shocks.

## Reproducible snippet

```bash
python example_naval_blockade.py
```

Output files: `naval_blockade_china.png`, `naval_blockade_stability.png`
