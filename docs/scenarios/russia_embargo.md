# Russia Oil Embargo

## From "energy bridge" to energy weapon

For three decades after the Cold War, Russia served as Europe's **energy bridge**—a reliable supplier of crude oil, natural gas, and refined products that tempered Europe's dependence on Middle Eastern instability. That bridge became a **weapon** in 2022, when the EU imposed successive rounds of sanctions on Russian oil exports. By 2023, observed data showed Russian oil exports to Europe had fallen by **60–70%**—not a complete cutoff, but a profound restructuring of global trade flows.

The model's Russia embargo scenario asks a harder question: what if the cutoff were **total**? Not the graduated, loophole-ridden sanctions of 2022–2024, but a comprehensive embargo enforced by naval interdiction and banking exclusion? And what if it were imposed not gradually over two years, but **suddenly, with a 30-day ramp**?

This scenario is not a forecast of current policy. It is a **stress test** of Europe's resilience and Russia's adaptability under maximum pressure.

## Geopolitical context

Russia's strategic position in the model rests on two pillars:

1. **Resource surplus**: CIS production of ~13,868 kb/d against consumption of only ~4,636 kb/d yields a **surplus of ~9,232 kb/d**—the second-largest in the world after the Middle East. This surplus is Russia's primary source of foreign exchange, government revenue, and geopolitical leverage.

2. **European dependency**: Historically, Europe sourced roughly **30% of its oil from Russia**, delivered via the Druzhba pipeline system and Baltic/Ust-Luga seaborne terminals. This dependency was not accidental; it reflected deliberate post-Cold War policy to bind Russia into European economic structures.

The model tests the breakdown of this mutual dependency. Russia loses its largest market. Europe loses its most proximate supplier. Both must reorient—Europe toward North American and Middle Eastern sources, Russia toward China and India.

## How the model implements the embargo

```python
from interventions import russia_oil_embargo

iv = russia_oil_embargo(
    onset_day=0.0,      # Immediate effect (beginning of simulation)
    severity=0.9,       # 90% of Russian oil exports eliminated
    ramp_days=30.0,     # Graduated over one month
)
```

This targets `oil_trade_flow` only, with `exporter_region=2` (Russia). Key design choices:

- **Onset at day 0**: Unlike Hormuz (day 100), the embargo begins immediately. This tests acute shock, not delayed escalation.
- **Severity 0.9 (not 1.0)**: The model allows a 10% residual flow representing smuggling, gray-market transhipment, and pipeline "technical failures" that are politically tolerated. This is realistic; even maximum sanctions regimes leak.
- **30-day ramp**: The EU's 2022 embargo was announced months in advance. The model assumes a faster, more coercive implementation.

## What the model predicts

### Oil stock dynamics
The embargo produces a **split-screen effect**:

- **Russia (exporter)**: Oil stocks rise rapidly but not catastrophically. The model's production equation includes a stability term: $\dot{O}_i = P_i^{\text{oil}}(\beta + (1-\beta)S_i) - C_i + \sum T_{ij}$. As stability erodes (discussed below), production itself falls, partially mitigating stock accumulation. Domestic consumption cannot absorb the surplus. The model shows Russia facing a **classic exporter's crisis**: plenty of oil, nowhere to sell it.

- **Europe (importer)**: Stocks decline according to the remaining 70% of non-Russian supply plus strategic reserve drawdown. Europe's baseline import portfolio includes North Sea, West African, and Middle Eastern crude, so the decline is steep but not catastrophic. Within 60–90 days, however, the price effects become severe.

### Price propagation
Oil prices spike globally, but the spike is **asymmetric**:
- Europe: +40–60% above baseline (proximity to Russia means Europe feels the loss most acutely)
- China/India: +15–25% (they gain Russian discounted crude, partially offsetting global price rises)
- North America: +10–20% (partially insulated by domestic production)

### Stability and debt feedback
The embargo triggers the model's full feedback architecture:

1. **Russia**: Stability falls because resource abundance ($a_i = \tanh(\kappa_r(O_i + F_i + W_i))$) rises (local stocks are high) but the *realized economic benefit* is gone (cannot export). The model's GDP proxy—based on production and prices—falls, reducing tax revenue and increasing debt/GDP. Military spending initially rises (fiscal response), but the debt-crisis sigmoid eventually suppresses it.

2. **Europe**: Stability falls because prices spike and stocks decline. Inequality rises ($\dot{I}_i = \gamma_{is}(1-S_i) + \gamma_{id}D_i - \gamma_{ir}I_i$) as energy costs burden lower-income households. Debt/GDP rises as governments subsidize energy and increase military preparedness.

3. **China and India**: Stability *rises* modestly because they gain access to discounted Russian crude, improving their energy security. This is a critical model prediction: embargoes create **winner regions** as well as losers.

## Empirical grounding

| Metric | Value | Source | Model parameterization |
|--------|-------|--------|----------------------|
| Russian oil production (2023) | ~13,868 kb/d | Energy Institute | `oil_production[2]` |
| Russian consumption (2023) | ~4,636 kb/d | Energy Institute | `oil_consumption[2]` |
| Surplus (exportable) | ~9,232 kb/d | Derived | Trade matrix column 2 |
| EU sanctions observed reduction | ~60–70% of exports to Europe | 2022–2023 trade data | Severity = 0.9 is upper bound |
| China's increased Russian imports (2023–24) | ~+20–30% YoY | Trade data | Captured by unperturbed Russia→China flows |
| India's increased Russian imports (2023–24) | ~+40–50% YoY | Trade data | Captured by unperturbed Russia→India flows |

## Comparison with bilateral sanctions

The Russia embargo scenario is **uni-directional**: it cuts Russia's exports to the world, but does not prevent Russia from importing (fertilizer, machinery, technology). The [Bilateral Sanctions scenario](sanctions.md) adds this second dimension, cutting Russia's inbound trade as well. The model shows that bilateral sanctions produce larger stability and debt effects for both parties because the economic shock is symmetric rather than one-sided.

## Validation status

- **Observed EU sanctions effect**: ✓ **Confirmed** — 60–70% reduction documented
- **Severity 0.9 as upper bound**: ⚠ **Partial** — No historical full embargo to validate against
- **Winner regions (China/India)**: ✓ **Confirmed** — Documented increase in discounted Russian imports
- **Price spike magnitude**: ⚠ **Partial** — Model predictions depend on price-response parameter; not independently validated

## Key insights

1. **Embargoes redistribute, they do not eliminate**: The 9,232 kb/d of Russian oil does not disappear from global markets. It flows to China, India, and other non-participating buyers at discounted prices. The model's fixed-trade matrix partially captures this; the [Price-Mediated Trade extension](price_trade.md) captures it more dynamically.

2. **The 30-day ramp is critical**: If the embargo were instantaneous (ramp_days=0), the model shows solver instability because the discontinuity propagates through price and stability derivatives. The 30-day ramp is the shortest practicable implementation that preserves numerical stability.

3. **Military expenditure as a shock absorber**: Both Russia and Europe increase military spending in response to the embargo. In Russia's case, this is partially a Keynesian stimulus; in Europe's case, it reflects energy-security militarization. The model captures both through the same $\dot{M}_i$ equation, illustrating how the same ODE structure produces different political interpretations depending on context.

## Reproducible snippet

```bash
# Full reproduction (including embargo-only, bilateral, and compound variants)
python example_sanctions.py
```

Output files: `sanctions_comparison.png`, `sanctions_impact_ranking.png`

The script compares three sub-scenarios: (a) Russia embargo only, (b) EU–Russia bilateral only, and (c) both combined. The compound scenario produces nonlinear effects larger than either individually.
