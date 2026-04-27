# Panama Canal Disruption

## The overlooked chokepoint

The Panama Canal rarely appears in lists of "critical energy chokepoints" alongside Hormuz or Malacca. At ~2.0–2.3 mb/d of crude oil throughput, it moves only about **2.5–3% of global seaborne oil**. Yet this figure is profoundly misleading. Two factors make Panama strategically significant in ways that pure volume statistics obscure:

1. **The LPG/LNG bottleneck**: Over **95% of U.S. liquefied petroleum gas (LPG) exports to Asia** transit the Panama Canal. LPG is the primary feedstock for Asian petrochemical industries—plastics, fertilizers, synthetic textiles. A canal closure does not merely reroute crude; it severs the chemical-industry supply chain.

2. **The surge-artery effect**: In the current crisis (April 2026), Gulf News reports that tanker traffic through Panama has surged to **36–38 vessel transits per day**, near the canal's operational capacity. This surge occurs precisely because Hormuz is already compromised. Shippers are rerouting Middle East oil around Africa to the U.S. Gulf Coast, then through Panama to Asia. The canal has become a **relief valve** for Hormuz disruption.

Disrupting Panama in the model therefore tests a subtle but critical strategic proposition: in a multi-chokepoint world, the canal is not a primary artery but a **backup route whose closure removes the last alternative**.

## Geopolitical situation

The canal's vulnerability differs fundamentally from Hormuz or Malacca:
- **Geographic**: The canal is a freshwater lock system dependent on Lake Gatún rainfall. Drought (2023–2024) has already demonstrated how climate can restrict traffic independent of geopolitics.
- **Political**: Panama is a sovereign nation with no U.S. military presence since 1999, but the U.S. retains treaty rights to defend canal neutrality.
- **Economic**: Canal tolls fund roughly 15% of Panama's government budget. Extended closure would trigger a domestic fiscal crisis regardless of global oil markets.

## How the model implements the disruption

```python
from interventions import panama_disruption

iv = panama_disruption(
    onset_day=100.0,
    severity=0.55,    # Moderate severity reflecting lower throughput share
    ramp_days=14.0,  # Slower ramp reflecting logistical complexity
)
```

This applies `chokepoint_disruption` to `exporter_region=10` (South America). The severity of 0.55 is calibrated as follows:
- 2.5% of seaborne oil × 0.55 = ~1.1 mb/d direct crude impact
- LPG impact is modeled implicitly through the **fertilizer trade matrix** (LPG → petrochemicals → fertilizers)
- The lower severity reflects that Panama is a *secondary* chokepoint; full closure (~1.0) would be geopolically extraordinary

## Model predictions

### Standalone Panama impact
For a standalone Panama disruption, the model predicts:
- **South America**: Stock accumulation (exports blocked)
- **East Asia**: Delayed price effect on LPG-linked commodities (fertilizer, petrochemicals)
- **North America**: Modest oil price increase as U.S. Gulf exports to Asia must reroute around Cape Horn

The standalone effect is **not catastrophic** because 97% of global seaborne oil still flows through other routes. No figure is generated for the standalone case because the visual impact is too modest to be informative.

### Compound Panama impact (the strategic insight)
The Panama scenario becomes meaningful only in combination with other chokepoints:

| Scenario | China's remaining import options |
|----------|--------------------------------|
| Baseline | Hormuz + Malacca + Panama + Russia pipeline + African routes |
| Hormuz only | Malacca + Panama + Russia + Africa |
| Hormuz + Malacca | Panama + Russia + Africa |
| Hormuz + Malacca + Panama | **Russia + Africa only** |

The model's [Multi-Chokepoint scenario](multi_chokepoint.md) captures this sequential elimination. At the three-chokepoint level, China's oil imports are constrained to:
- Russian pipeline supply (~15–20% of baseline)
- African Cape-route supply (~15%)
- Domestic production (~10–15%)
- Total: ~40–50% of baseline demand

This is the **"dependency shift"** mechanism that Game Theory #21 describes as the core U.S. strategy.

## Empirical grounding

| Metric | Value | Source |
|--------|-------|--------|
| Normal oil throughput (2024) | ~2.0 mb/d | EIA |
| 1H2025 annualized | ~2.3 mb/d | EIA |
| Share of world maritime oil trade | ~2.5–3% | Derived from EIA global totals |
| US LPG exports to Asia via Panama | **>95%** | Gulf News 2026 |
| Current crisis surge | **36–38 vessel transits/day** (near capacity) | Gulf News, Ecoticias April 2026 |
| Drought restriction (2023–24 precedent) | Tonnage limits, queue delays | Panama Canal Authority |

## Key model insights

1. **The amplification mechanism**: Panama is not dangerous in isolation. It is dangerous because it is the **last remaining rerouting option** when Hormuz and Malacca are already compromised. The model's nonlinearity (sigmoid thresholds, multiplicative coupling terms) means that removing the last alternative produces disproportionate effects compared to removing the first.

2. **LPG as a hidden vulnerability**: The model's fertilizer trade matrix captures LPG disruption indirectly. Fertilizer prices spike not because fertilizer itself is blocked at Panama, but because the petrochemical feedstock (LPG) is stranded. This is a **second-order effect** that pure oil-trade models miss.

3. **Duration matters**: A short Panama closure (weeks) is absorbed by inventory. A long closure (months) forces structural retooling of petrochemical supply chains. The model's 365-day horizon reveals chronic effects that short-horizon analyses miss.

## Validation status

- **LPG dependency**: ✓ **Confirmed** — Gulf News >95% figure
- **Surge-artery behavior**: ✓ **Confirmed** — 36–38 transits/day near capacity
- **Standalone severity**: ⚠ **Partial** — No direct empirical calibration; 55% is a reasoned estimate
- **Compound effect with Hormuz+Malacca**: ⚠ **Partial** — Hypothetical; no three-chokepoint historical precedent

## Reproducible snippet

```python
from interventions import panama_disruption, compose_interventions
from geopolitical_model import GeopoliticalModel, load_parameters
from model_config import ModelConfig

params = load_parameters("real_params.json")
cfg = ModelConfig(trade_scale=1.0, k_half=50.0, initial_stock_days=90.0)

# Standalone (modest effect)
iv = panama_disruption(onset_day=100.0, severity=0.55, ramp_days=14.0)
traj = GeopoliticalModel(params, cfg, interventions=[iv]).simulate(t_span=(0, 365))

# Compound (see multi_chokepoint.py for full implementation)
```
