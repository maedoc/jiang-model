# Credibility Brief: Network Compounding and Trade Elasticity
## Multi-Chokepoint Cascades and Price-Mediated Trade — Empirical Validation Report

**Date:** 2026-04-27  
**Scope:** Q3 (multi-chokepoint compounding), Q7 (price-mediated trade elasticity)  
**Sources:** Brancaccio et al. (2021), Kilian and Murphy (2014), Caldara et al. (2019), EIA World Oil Transit Chokepoints (March 2026), IEA Oil Market Report (April 2026), IIASA/GFT trade models, MIT supply-chain resilience literature.

---

## Executive Summary

| Claim | Status | Key Finding |
|-------|--------|-------------|
| Multi-chokepoint compounding > additive | **Partial** | No peer-reviewed network-science paper validates the specific "compounding > additive" claim. However, EIA data shows Hormuz (20.9 mb/d) + Malacca (23.2 mb/d) together carry ~57% of seaborne oil, so the *geographic concentration risk* is real. |
| Trade elasticity 0.5 | **Partial — defensible with caveat** | Brancaccio et al. (2021) report mean trade elasticity 0.35 (range 0.1–1.2) for shipping-cost responses. Kilian-Murphy (2014) report short-run oil *demand* elasticity −0.08 to −0.26. The model's 0.5 is within the trade-elasticity range but **not a demand elasticity**. Documentation must distinguish these. |
| Network redundancy threshold | **Unverified** | No peer-reviewed source quantifies a "redundancy threshold" at which trade networks collapse. The model's phase-transition claims lack direct literature support. |

---

## 1. Multi-Chokepoint Compounding (Q3)

### 1.1 The Model's Claim

The model asserts that simultaneous disruption of Hormuz, Malacca, and Panama produces effects that are **nonlinearly greater than the sum of individual disruptions**. This is framed as a network cascade: closing Hormuz forces rerouting, but if Malacca is also closed, the rerouting options themselves become blocked.

### 1.2 What EIA Data Show

| Chokepoint | Throughput (1H2025) | % of Seaborne Oil | China's Exposure |
|------------|---------------------|-------------------|-----------------|
| Hormuz | 20.9 mb/d | ~25% | ~46% of crude imports |
| Malacca | 23.2 mb/d | ~29% | ~48% of crude imports |
| Panama | 2.3 mb/d | ~3% | Minimal direct exposure |
| **Combined Hormuz + Malacca** | **~44 mb/d** | **~57% of seaborne oil** | **~75–80% of seaborne imports** |

**Critical insight:** The EIA data confirm that Hormuz + Malacca together are the **dominant arteries of global oil trade**. A simultaneous closure would not be "additive" in a naive sense because:
- Hormuz closure alone traps Middle East oil
- Malacca closure alone traps non-Russian oil reaching East Asia
- Combined, they trap **both** the source region (Middle East) **and** the primary transit corridor to the largest importer (China)

However, this is **geographic concentration**, not necessarily a *network phase transition*.

### 1.3 Network Science Literature

| Source | Finding | Relevance to Model |
|--------|---------|-------------------|
| Brancaccio et al. (2021) | Mean trade elasticity 0.35 (shipping cost → trade volume) | Validates trade rerouting magnitude, not compounding |
| IIASA/GFT global trade models | Multi-region shocks produce nonlinear GDP effects | Directionally supports compounding, but no chokepoint-specific calibration |
| MIT supply-chain resilience | "Hidden nodes" (unobserved suppliers) amplify cascades | Conceptually similar, but no energy-specific application |
| Hébert-Dufresne et al. (2013) | Cascades in interdependent networks have discontinuous transitions | Theoretical support for phase transitions, but not calibrated to oil trade |

**Verdict:** The network-science literature provides **conceptual support** for nonlinear compounding, but **no empirically calibrated model** validates the specific claim that Hormuz + Malacca + Panama produces a phase-transition-like collapse. The model's "compounding > additive" narrative is **plausible but unverified** in peer-reviewed literature.

### 1.4 Historical Precedents for Simultaneous Disruption

| Event | Chokepoints Affected | Duration | Effect |
|-------|-------------------|----------|--------|
| 1973 Oil Crisis | None (embargo, not chokepoint) | 6 months | ~4% global supply reduction; 4x price spike |
| 1979 Iranian Revolution | Hormuz (partial) | 6+ months | ~7% supply reduction; 2x price spike |
| 1984–88 Tanker War | Hormuz | 4 years | ~2–4% physical disruption; massive insurance effects |
| 2023–24 Houthi Attacks | Bab el-Mandeb, Suez | Ongoing | ~42% Suez transit drop; 5–10x insurance increase |
| 2024 Panama Drought | Panama | ~12 months | FY2024 transit drop 29.3% for oil; recovered in FY2025 |
| **2026 Game Theory #21** | Hormuz + Malacca | Scenario | Assumed compound shock; no historical analog |

**Key insight:** No historical event has simultaneously closed Hormuz and Malacca. The closest analog is the 1973 embargo, which achieved price effects through political coordination rather than physical closure. The model's compound scenario is **policy-relevant but historically unprecedented**.

### 1.5 Verdict: Multi-Chokepoint Compounding

| Aspect | Rating | Rationale |
|--------|--------|-----------|
| Geographic concentration risk | ✓ **Confirmed** | EIA: 57% of seaborne oil via Hormuz + Malacca |
| China's combined exposure | ✓ **Confirmed** | ~75–80% of seaborne imports via both chokepoints |
| "Compounding > additive" | ⚠ **Plausible, unverified** | No peer-reviewed network model directly validates |
| Phase-transition claims | ✗ **Unverified** | No literature source supports a specific network-collapse threshold |
| Panama role in compounding | ⚠ **Minor** | Panama carries only ~3% of seaborne oil; LPG/LNG role is niche |

---

## 2. Price-Mediated Trade Elasticity (Q7)

### 2.1 The Model's Parameter

The model uses `price_trade_elasticity = 0.5`, meaning a 1% increase in shipping/delivery costs produces a 0.5% reduction in trade volume. This parameter drives the `price_trade` scenario, where higher energy costs reduce all trade flows proportionally.

### 2.2 What the Literature Actually Says

**Critical distinction:** The literature distinguishes between:

1. **Trade-flow elasticity** (shipping cost → trade volume)
2. **Oil demand elasticity** (price → consumption)
3. **Supply elasticity** (price → production)

| Study | Elasticity Type | Estimate | Context |
|-------|----------------|----------|---------|
| Brancaccio et al. (2021) | Trade-flow elasticity to shipping costs | **0.35** mean; **0.1–1.2** range | Across 44 countries, 2007–2018 |
| Kilian & Murphy (2014) | Oil demand elasticity (short-run) | **−0.08 to −0.26** | OECD countries, 1970–2011 |
| Caldara et al. (2019) | Oil demand elasticity (short-run) | **~−0.2** | VAR with supply shocks |
| IMF (2022) | Oil demand elasticity (long-run) | **−0.4 to −0.6** | Global panel |
| NBER energy trade papers | Trade rerouting elasticity | **0.3–0.7** | Post-Fukushima LNG, post-2022 European gas |

### 2.3 The Interpretation Problem

The model's `price_trade_elasticity = 0.5` falls within Brancaccio's trade-flow range (0.1–1.2). However, **the parameter name is misleading**:

- If interpreted as **trade-flow elasticity** (shipping cost → trade volume): ✓ **Defensible** — 0.5 is near the mean of Brancaccio's range.
- If interpreted as **oil demand elasticity** (price → consumption): ✗ **Too high** — short-run demand elasticity is −0.08 to −0.26.

**The model applies this parameter to all three trade matrices (oil, fertilizer, water) as a uniform trade-reduction coefficient.** This is best understood as a **trade-rerouting responsiveness**, not a demand elasticity.

### 2.4 Historical Rerouting Cases

| Event | Rerouting Speed | Magnitude | Source |
|-------|----------------|-----------|--------|
| Post-Fukushima LNG | ~6–12 months | Japan substituted 20% of nuclear with LNG | IEA |
| Post-2022 Russian gas | ~12–18 months | EU reduced Russian gas from 40% → 8% | Eurostat |
| 2023–24 Red Sea diversion | ~2–4 weeks | ~60–70% of Asia-Europe container rerouted | Reuters |
| 2024 Panama drought | ~1–2 months | Oil transits dropped 29.3%; recovered in FY2025 | EIA |

**Key insight:** Rerouting speed varies by commodity and infrastructure:
- **Oil (tankers):** Weeks to months — tankers are mobile, but ports and refining capacity are fixed
- **LNG:** Months — requires specialized terminals
- **Pipeline gas:** Years — infrastructure is immobile
- **Fertilizer:** Weeks — bulk cargo, but demand is seasonal

The model's implicit assumption of rapid, uniform rerouting across all commodities is **directionally correct for oil but too fast for gas/LNG and possibly too slow for bulk commodities**.

### 2.5 Verdict: Price-Mediated Trade Scenario

| Aspect | Rating | Rationale |
|--------|--------|-----------|
| Elasticity 0.5 as trade-flow parameter | ✓ **Defensible** | Within Brancaccio et al. (2021) range |
| Elasticity 0.5 as demand parameter | ✗ **Too high** | Short-run oil demand elasticity is −0.08 to −0.26 |
| Parameter name clarity | ⚠ **Misleading** | Should be renamed `shipping_cost_trade_elasticity` |
| Cross-commodity uniformity | ⚠ **Oversimplified** | Oil reroutes in weeks; gas in months/years |
| Historical validation | ✓ **Partial** | Post-2022 gas rerouting and Red Sea diversion validate mechanism |

---

## 3. Summary Table: Network and Elasticity Credibility

| Claim | Parameter | Literature Estimate | Model Value | Status |
|-------|-----------|-------------------|-------------|--------|
| Trade-flow elasticity | `price_trade_elasticity` | 0.35 mean; 0.1–1.2 range (Brancaccio) | 0.5 | ✓ Defensible (rename recommended) |
| Oil demand elasticity | (mis)applied to consumption | −0.08 to −0.26 (Kilian-Murphy) | 0.5 | ✗ Misinterpreted |
| Hormuz + Malacca share | Geographic concentration | ~57% of seaborne oil (EIA) | Implicit | ✓ Confirmed |
| Network phase transition | Compounding > additive | No direct empirical validation | Assumed | ⚠ Plausible, unverified |
| Rerouting speed | Uniform across commodities | Varied by infrastructure | Uniform (implicit) | ⚠ Oversimplified |

---

## Recommendations for Model Documentation

1. **Rename `price_trade_elasticity`:** Change to `shipping_cost_trade_elasticity` or add a clear note that this is a **trade-flow rerouting parameter**, not a demand elasticity.
2. **Add commodity-specific notes:** Document that oil reroutes in weeks, gas in months/years, and fertilizer is seasonal.
3. **Downgrade phase-transition language:** Replace "compounding > additive" with "geographic concentration creates sequential elimination of rerouting options," which is empirically grounded without claiming unverified network effects.
4. **Cite Brancaccio et al. (2021):** Add this as the primary literature source for the trade elasticity range.
5. **Add a "no historical analog" flag:** The simultaneous Hormuz + Malacca closure has no precedent. Frame the scenario as a "policy-relevant but unprecedented compound shock."
