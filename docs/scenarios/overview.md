# Scenarios — Overview

Scenarios are composable counterfactuals: a baseline 365-day simulation is compared against the same world plus a layered intervention (chokepoint closure, bilateral sanction, supply shock, or naval blockade).

## Scenario summary

| Scenario | Chokepoint(s) | Intervention type | Key figure | Primary insight |
|----------|---------------|-------------------|------------|-----------------|
| [Hormuz Strait Closure](hormuz.md) | Hormuz | `hormuz_closure` (chokepoint) | `hormuz_oil_stock.png` | 80% ME export cut → 83% flow reduction empirically validated |
| [Malacca Strait Disruption](malacca.md) | Malacca | `malacca_disruption` (chokepoint) | — | ~48% of China's imports via this route; no practical alternative |
| [Panama Canal Disruption](panama.md) | Panama | `panama_disruption` (chokepoint) | — | >95% US LPG to Asia; crisis surge to 36–38 transits/day |
| [Russia Oil Embargo](russia_embargo.md) | — | `russia_oil_embargo` (supply shock) | `sanctions_comparison.png` | 85% export cut; 2022 EU sanctions achieved 60–70% |
| [Bilateral Sanctions](sanctions.md) | — | `bilateral_sanction` | `sanctions_comparison.png` | EU–Russia complete oil+fert trade cut |
| [Price-Mediated Trade](price_trade.md) | — | ModelConfig toggle | `price_trade_oil.png` | Scarcity raises prices → attracts imports → reduces scarcity |
| [Multi-Chokepoint](multi_chokepoint.md) | Hormuz + Malacca + Panama | `compose_interventions` | `multi_chokepoint_oil.png` | Compound shock traps 60–70% of China's imports |
| [Naval Blockade](naval_blockade.md) | ME → China | `naval_blockade` (bilateral) | `naval_blockade_china.png` | Asymmetric impact: sender stability rises, receiver falls |
| [Refinery Sabotage](refinery_sabotage.md) | Global | Multi-region supply shock | — | IEA ceiling ≈ 2.5% global capacity |

## Quick-start template

Every scenario page follows the same structure:

1. **Geopolitical situation** — why the counterfactual matters
2. **Intervention definition** — Python constructor call
3. **Empirical grounding** — model value vs official source
4. **Output figure(s)** — with interpretation
5. **Key results** — 3–5 bullet takeaways
6. **Reproducible snippet** — minimal code to re-run

```python
from geopolitical_model import GeopoliticalModel, load_parameters
from model_config import ModelConfig
from interventions import hormuz_closure
from trajectory import TrajectoryComparison

params = load_parameters("real_params.json")
cfg = ModelConfig(trade_scale=1.0, k_half=50.0, initial_stock_days=90.0)

# Baseline
base = GeopoliticalModel(params, cfg).simulate(t_span=(0, 365))

# Intervention
iv = hormuz_closure(onset_day=100.0, severity=0.8, ramp_days=10.0)
shock = GeopoliticalModel(params, cfg, interventions=[iv]).simulate(t_span=(0, 365))

# Compare
cmp = TrajectoryComparison(base, shock)
```
