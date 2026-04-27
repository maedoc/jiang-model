# Multi-Chokepoint (GT#21)

## The strategy of sequential elimination

Game Theory #21 posits a grand-strategic vision: the United States does not need to win a shooting war with China or Iran. It needs only to **control the arteries** through which industrial civilization flows. Hormuz, Malacca, Panama, Gibraltar—these are not chokepoints to be defended. They are **switches to be thrown**.

The multi-chokepoint scenario tests this claim in its starkest form. Three chokepoints—Hormuz, Malacca, and Panama—are simultaneously disrupted at day 100, each following its empirically calibrated severity but all acting together. The question is not whether any single chokepoint matters. It is whether **the combination produces effects that are greater than the sum of its parts**.

This is a test of **network fragility**. The global oil trade network is designed with redundancy: if one route fails, others exist. But redundancy is not infinite. Each chokepoint closure eliminates a set of rerouting options. When the set of remaining options becomes smaller than the set of required flows, the network undergoes a **phase transition**—not gradual degradation, but sudden system-wide stress.

The model's 15-variable, 180-ODE architecture is specifically designed to capture such transitions. The debt-crisis sigmoid, the social-unrest threshold, and the stability-feedback loop all introduce nonlinearities that can amplify small shocks into large outcomes.

## Why this scenario is the central test

All other scenarios in this library are **fragments** of the multi-chokepoint story:
- [Hormuz](hormuz.md) tests the Middle East export blockage
- [Malacca](malacca.md) tests the Asian import chokepoint
- [Panama](panama.md) tests the Atlantic-Pacific bypass
- [Naval Blockade](naval_blockade.md) tests bilateral interdiction
- [Russia Embargo](russia_embargo.md) tests supplier elimination

The multi-chokepoint scenario is the **integration test**: it combines all three geographic chokepoints simultaneously to ask whether the global system can absorb their combined stress.

## How the model implements the compound shock

```python
from interventions import hormuz_closure, malacca_disruption, panama_disruption, compose_interventions

iv = compose_interventions([
    hormuz_closure(onset_day=100.0, severity=0.8, ramp_days=10.0),
    malacca_disruption(onset_day=100.0, severity=0.7, ramp_days=14.0),
    panama_disruption(onset_day=100.0, severity=0.6, ramp_days=14.0),
])
```

The `compose_interventions` function is critical. It does not sum the interventions; it **stacks them multiplicatively**. The parameter dict is modified by each intervention in sequence. So:

- At day 100: all three chokepoints begin their ramps
- At day 110: Hormuz reaches 80% severity
- At day 114: Malacca reaches 70% severity
- At day 114: Panama reaches 60% severity
- At day 200: all three are at full severity

The Middle East's outbound trade is reduced by 80%. Southeast Asia's outbound trade is reduced by 70%. South America's outbound trade is reduced by 60%. The regions that depend on these flows must now source from the remaining suppliers: North America, Russia, and Africa.

## China's import straitjacket

The central prediction of the multi-chokepoint scenario is that **China's oil import options are systematically eliminated**:

| Supplier | Normal share | After Hormuz | After Hormuz+Malacca | After all three |
|-----------|-------------|--------------|---------------------|----------------|
| Middle East via Hormuz | ~40% | ~8% (20% residual) | ~2% (pipeline only) | ~2% |
| Middle East via Malacca | ~35% | ~28% (rerouted) | ~8% (bypass) | ~3% |
| Russia via pipeline | ~15% | ~15% | ~15% | ~15% |
| Africa via Cape | ~7% | ~7% | ~7% | ~7% |
| Central Asia | ~3% | ~3% | ~3% | ~3% |
| **Total available** | **100%** | **61%** | **35%** | **30%** |

The model predicts that China would enter a **sustained resource deficit** of ~30–40% of its baseline oil consumption. This is not a temporary shortage absorbable by strategic reserves. It is a **structural shortfall** that requires either demand destruction (industrial shutdowns, rationing) or diplomatic reversal (lifting of chokepoint controls).

## Output figures

### Oil stock trajectories

![Multi-chokepoint oil](../assets/scenarios/multi_chokepoint_oil.png)

The oil stock figure reveals the **hierarchy of vulnerability**:

- **China**: Stocks fall to ~50% of baseline by day 250, then collapse further. The curve is convex (accelerating decline) rather than concave (decelerating), indicating that the initial strategic reserve buffer is exhausted and the remaining shortfall becomes chronic.
- **Japan**: Shows the steepest decline of any region, reaching ~30% of baseline by day 300. Japan has minimal domestic production and its SPR is smaller relative to consumption than China's.
- **India**: Declines to ~45% of baseline. India's domestic production (~1 mb/d equivalent) and proximity to African suppliers provide partial buffering.
- **Europe**: Declines to ~60% of baseline. Europe is partially shielded by North Sea, Russian pipeline, and West African sources.
- **Southeast Asia**: Shows a complex pattern. The model treats the region as a net exporter, so the Malacca disruption initially produces stock buildup. But over time, the loss of export revenue and the regional price collapse (too much oil, nowhere to sell) causes instability and production cuts.
- **South America**: Shows modest stock buildup from the Panama disruption, but the effect is smaller than for Southeast Asia because South America's export volumes through Panama are lower.

### China dashboard

![Multi-chokepoint China](../assets/scenarios/multi_chokepoint_china.png)

The China dashboard is the most disturbing figure in the model's output library. It tracks six variables simultaneously:

1. **Oil price**: Spikes to ~4× baseline by day 150, then remains elevated. The persistence (not just the magnitude) is critical: prices do not self-correct because the supply constraint is structural, not transient.

2. **Fertilizer price**: Spikes in parallel with oil (fertilizer is oil-intensive to produce and transport) but with a 10–15 day lag. The lag represents the time for oil price shocks to propagate through the petrochemical supply chain.

3. **Political stability**: Falls from ~0.8 to ~0.55 by day 300. The decline is driven by the social-unrest threshold ($I_i > 0.6$ AND $\pi_i > 0.1$). Inflation from energy and fertilizer prices crosses the 0.1 threshold around day 150. Inequality rises because energy costs burden lower-income households more than wealthy households.

4. **Inflation**: Rises to ~0.25 (annualized 25%) by day 200. This is hyperinflationary territory. The model's Taylor-rule interest rate response pushes $r_i$ to ~0.15 (15%), but this is insufficient to control inflation because the price shock is supply-driven, not demand-driven. Monetary policy is largely ineffective against supply shocks.

5. **Debt/GDP**: Rises from ~0.6 to ~1.8 by day 300, crossing the debt-crisis threshold ($D_i > 1.0$) around day 180. The austerity sigmoid then suppresses military spending, creating a feedback loop: less military spending → less stability gain → more unrest → more debt.

6. **Military expenditure**: Initially spikes (government responds to crisis) but is then suppressed by the debt-crisis sigmoid after day 180. The result is a **double bind**: China needs military spending to project power and secure alternative supply routes, but cannot afford it because debt is already too high.

## The dependency shift: who wins?

While China suffers, the model predicts **surplus regions gain**:

| Region | Mechanism | Outcome |
|--------|-----------|---------|
| **North America** | Gains European and Asian market share; prices rise but stocks remain comfortable | Stability rises; debt/GDP improves |
| **Russia** | Becomes China's primary remaining supplier; gains leverage | Stability rises; military spending increases |
| **Africa** | Gains Asian market share for non-Hormuz crude | Moderate stability gain; some stock drawdown |
| **Australia/NZ** | LNG and coal exports surge to Asia | Significant stability gain |

This is the **dependency shift** that Game Theory #21 describes as the core strategic objective. The goal is not to destroy China. It is to make China's continued industrialization conditional on North American and Russian goodwill.

## Validation and caveats

| Claim | Status | Evidence |
|-------|--------|----------|
| Compounding > additive | ✓ **Confirmed** by model structure — multiplicative stacking of trade reductions | No direct historical precedent for three simultaneous chokepoint closures |
| China loses ~60–70% of imports | ✓ **Confirmed** by ANRPC + EIA arithmetic | Hormuz (40%) + Malacca (35%) minus overlaps = ~60% |
| Stability collapse in import-dependent regions | ⚠ **Partial** — Model mechanism is structurally plausible but not empirically calibrated | No historical precedent for simultaneous Hormuz+Malacca closure |
| Surplus regions gain stability | ⚠ **Partial** — Mechanism is plausible but depends on many auxiliary assumptions (price response, military spending feedback) | 1973 oil crisis: surplus regions (Saudi Arabia, USSR) gained economic and political weight |
| Model ASEAN net-exporter assumption | ✗ **Rejected** — See [Malacca caveat](malacca.md) and [Rejected / Unverified](../empirical/rejected.md) | EI data shows ASEAN is net importer |

## Key insights

1. **The 60-day window**: The model shows that most damage occurs between day 100 and day 160. This is the period when strategic reserves are drawn down, price spikes trigger inflation, and debt begins to accumulate. After day 200, the system reaches a new quasi-equilibrium—painful, but no longer accelerating. This temporal structure has strategic implications: a chokepoint closure that lasts <60 days may be survivable; one that lasts >180 days is potentially transformative.

2. **Military expenditure as a leading indicator**: Military spending spikes before stability falls. This is because governments attempt to "buy" stability through defense spending (the $\alpha_i^{\text{gain}} \cdot a_i \cdot (1-S_i)$ term in the stability ODE). When this spending is cut off by debt crisis, stability collapses rapidly. Military spending therefore functions as a **leading indicator** of political trajectory.

3. **The fertilizer-to-food cascade**: The fertilizer price spike (visible in the China dashboard) is a **second-order effect** that pure oil-trade models miss. Fertilizer prices translate to food prices within 3–6 months. The 365-day simulation horizon is insufficient to fully capture this cascade, but the trend is clear: by day 300, fertilizer prices are ~3× baseline, implying severe food price inflation by month 12–15.

4. **China's strategic response is not modeled**: The model treats China as a passive recipient of shocks. In reality, China would activate SPR releases, accelerate pipeline construction, pursue diplomatic offensives, and potentially consider military options (e.g., securing Hormuz by force). These responses are outside the model's scope. The multi-chokepoint scenario should therefore be read as a **baseline stress test**, not a forecast of actual outcomes.

## Reproducible snippet

```bash
python example_multi_chokepoint.py
```

Output files: `multi_chokepoint_oil.png`, `multi_chokepoint_china.png`

Runtime: ~60 seconds (baseline + compound comparison).
