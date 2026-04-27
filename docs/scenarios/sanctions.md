# Bilateral Sanctions

## Cutting the double helix

Oil trade between Russia and Europe is not a simple buyer-seller relationship. It is a **double helix**: two intertwined strands of dependency that have evolved over 40 years. Europe needs Russia's oil. Russia needs Europe's technology, banking services, and refined products. The EU–Russia bilateral sanction scenario severs **both strands simultaneously**.

This is not what happened in 2022. The 2022 EU sanctions cut Europe's *inbound* oil from Russia but did not prevent Russia from importing European machinery, semiconductors, or banking services. European firms continued to comply with existing contracts. Russian gas (distinct from oil) continued to flow through Ukraine. The sanctions were, by design, **partial and asymmetric**.

The bilateral scenario models the harder case: a complete, mutual cutoff. Russia cannot sell oil to Europe. Russia cannot buy European technology. The pipeline is physically shut. The correspondent banking relationships are severed. Insurance markets, which depend on London and EU underwriters, withdraw coverage from Russian vessels.

## Geopolitical context

The bilateral scenario tests the logic of **economic autarky under pressure**. Both the EU and Russia have attempted to reduce dependence on the other since 2022:
- **Europe**: Built LNG terminals, diversified to North American gas, extended nuclear plant lifetimes
- **Russia**: Constructed the Power of Siberia pipeline to China, developed a "shadow fleet" of tankers, moved payment systems to CIPS/SPFS

Neither has achieved full independence. The bilateral scenario asks: what happens when the transition is **forced and immediate** rather than gradual?

## How the model implements bilateral sanctions

```python
from interventions import russia_oil_embargo, bilateral_sanction, compose_interventions
from interventions import RUSSIA, EUROPE

# Embargo: Russia cannot export oil
iv_embargo = russia_oil_embargo(
    onset_day=0.0, severity=0.9, ramp_days=30.0
)

# Bilateral: Russia and Europe cannot trade oil OR fertilizer
iv_bilateral = bilateral_sanction(
    name="EU-Russia bilateral",
    sender=RUSSIA,
    receiver=EUROPE,
    severity=1.0,       # Complete cut
    ramp_days=10.0,     # Faster than embargo (immediate crisis response)
    resources=[
        "oil_trade_flow",
        "fertilizer_trade_flow",
    ],
)

# Compound: both together
iv = compose_interventions([iv_embargo, iv_bilateral])
```

The `compose_interventions` function stacks both effects multiplicatively. If the embargo removes 90% of Russia's oil exports and the bilateral sanction removes 100% of the Russia→Europe flow, the residual flow is 10% × 0% = **0%**. The bilateral sanction is therefore redundant with the embargo for the Russia→Europe direction but adds the **reverse effect**: Europe→Russia fertilizer exports are also eliminated.

This reverse effect is crucial. Russia's agricultural sector depends on European fertilizer technology and equipment. A bilateral cutoff means:
- Russia's domestic fertilizer production falls (no spare parts for German-built plants)
- Russia's food prices rise
- Political stability in Russia's rural regions is threatened

The model captures this through the `fertilizer_trade_flow` disruption.

## Output figures

![Sanctions comparison](../assets/scenarios/sanctions_comparison.png)

*The figure presents a 3×4 grid: three scenarios (embargo only, bilateral only, combined) across four variables (oil stock, stability, oil price, debt/GDP) for Europe (left half) and Russia (right half).*

### Reading the grid

**Row 1: Russia Embargo Only**
- Europe's oil stock declines steadily as Russian supply is removed
- Russia's oil stock rises (cannot export)
- Europe's stability falls gradually
- Russia's stability falls too, but more slowly—domestic production partially compensates
- Prices spike moderately for both
- Europe's debt/GDP rises; Russia's rises but plateaus as austerity kicks in

**Row 2: Bilateral Only**
- The effect is **asymmetric**: Russia is hurt more than Europe
- Europe loses some Russian supply but retains global alternatives
- Russia loses not just oil export revenue but also fertilizer import inputs
- Russia's stability drops faster than in the embargo-only case

**Row 3: Combined**
- **Nonlinear amplification**: the compound scenario produces larger stability and debt effects than either alone
- Russia's stability collapses to ~0.6 by day 200 (from ~0.8 baseline)
- Europe's debt/GDP accelerates because the bilateral component removes Russia's ability to finance energy purchases, tightening global credit

### Impact ranking

![Sanctions impact ranking](../assets/scenarios/sanctions_impact_ranking.png)

The ranking figure quantifies which regions suffer most under the compound scenario. Russia and Europe are, predictably, the top two. But the ranking also reveals **secondary effects**:
- **Central Asia/Caucasus** (region 11) suffers because its trade routes to Russia are degraded
- **China** suffers modestly because it must absorb additional Russian oil at prices that depress its own domestic energy sector profitability
- **North America** benefits (negative impact score) by gaining European market share

## Model predictions vs. empirics

| Prediction | Model mechanism | Empirical analog | Status |
|-----------|----------------|------------------|--------|
| Russia hurt more than Europe | Bilateral cuts fertilizer imports too | Russia's agricultural dependence on EU tech | ✓ Partially confirmed |
| Nonlinear compound effect | Multiplicative stacking | No historical precedent for simultaneous oil+fertilizer cutoff | ⚠ Unverified |
| North America gains market share | Fixed-trade matrix reallocation | U.S. LNG exports to Europe surged 2022–24 | ✓ Confirmed |
| China absorbs discounted Russian oil | Unperturbed Russia→China flow | China-Russia oil trade +20–30% 2022–24 | ✓ Confirmed |
| Central Asia suffers collateral damage | Stability diffusion via coupling matrix | Kazakhstan oil export routes disrupted 2022 | ✓ Partially confirmed |

## Key insights

1. **The fertilizer channel is the hidden vector**: Oil embargoes make headlines. Fertilizer disruptions cause **famines**. The bilateral scenario's inclusion of fertilizer trade is not an afterthought; it is the mechanism by which an energy crisis becomes a food crisis. The model shows Russian food prices rising within 60 days of the bilateral cutoff.

2. **Russia's short-term resilience is misleading**: The model shows Russian stability holding relatively steady for the first 30–60 days. This reflects fiscal buffers built from pre-crisis oil revenues. But once those buffers are exhausted and the debt-crisis sigmoid activates (at D_i > 1.0), military spending is suppressed and stability collapses. The delayed nonlinearity is a core model feature.

3. **Europe's debt spiral is faster**: Europe has smaller fiscal buffers and higher baseline debt. The model shows Europe hitting the debt-crisis threshold (D_i > 1.0) within 90–120 days, triggering austerity that further suppresses stability. This is consistent with the 1973 oil crisis timeline: the UK required an IMF bailout by 1976, three years after the initial shock.

4. **The "shadow fleet" is not modeled**: The real world has workarounds—uninsured tankers, ship-to-ship transfers off Namibia, falsified bills of lading. The model does not capture these. The bilateral scenario should therefore be read as a **lower bound** on actual disruption: reality would leak, but the structural damage to legitimate trade flows would be similar.

## Running the scenario

```bash
python example_sanctions.py
```

The script generates three comparison figures and prints a summary table to stdout. Runtime is ~60–90 seconds on a standard laptop.
