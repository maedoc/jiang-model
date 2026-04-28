# Peer Review Report: Verification of Jiang-Model Geopolitical Scenario Claims

**Reviewer:** DeepSeek-v4-Pro (simulated independent empirical peer reviewer)  
**Date:** 2026-04-28  
**Material under review:** 3 synthesis briefs, 2 supporting documents, 11 updated documentation files, 8 verification streams (A–H)

---

## 1. Methodology Assessment

### 1.1 Overall Design: Strong structure, uneven execution

The agent adopted a sound verification architecture: a pre-registered research plan (Q1–Q7 mapped to 3 researcher roles), explicit acceptance criteria (≥2 independent sources per question, ≥3 quantitative findings), parallel execution via 8 verification streams, and a three-brief synthesis structure (historical / policy / networks). This mirrors good peer-review and replication methodology. **Confidence: High.**

However, the execution exhibits three methodological weaknesses:

**Gap 1: Primary-source fetch failure cascade.** The single most important quantitative finding — the IEA 83% flow reduction figure — was **not verified from a primary source**. The agent could not fetch the IEA factsheet (`iea.blob.core.windows.net/.../StraitofHormuzFactsheet.pdf`) directly. The 83% figure arrived via a secondary aggregator (Business Upturn, April 14, 2026) that itself cited the IEA. This is a single-point-of-failure in the verification chain. **Confidence: Medium.**

**Gap 2: Acceptance criteria met selectively.** Some questions met this (Q2 Malacca: EIA + ANRPC cross-referenced). Others did not: Q1 (Hormuz severity) relies on IEA → Business Upturn → agent, a two-hop chain with no independent cross-check. Q3 (compounding) has no empirical validation of the core claim at all. **Confidence: High.**

**Gap 3: No negative-result or falsification protocol.** Several claims fell into unverifiability (e.g., 365-day outage duration, water-trade subsystem). The agent correctly flagged these but did not systematically distinguish "falsified" from "untestable." **Confidence: Medium.**

### 1.2 Verification stream coverage

| Stream | Scenario | Validation depth | Verdict |
|--------|----------|-----------------|---------|
| A | Hormuz closure | Deep | Mostly confirmed |
| B | Malacca disruption | Deep | Confirmed |
| C | Panama disruption | Moderate | Partial |
| D | Russia embargo | Moderate | Partial |
| E | Bilateral sanctions | Light | Partial |
| F | Naval blockade | Deep | Verified with correction |
| G | Fertilizer | Deep | **Rejected** |
| H | Multi-chokepoint compounding | Light | Partial / Unverified |

Two scenarios received **no dedicated empirical validation stream**: price-mediated trade and refinery sabotage. The water-trade subsystem received **zero empirical attention** across all 8 streams. **Confidence: High.**

---

## 2. Source Quality Check

### 2.1 Tier-1 sources (gold standard)

| Source | Use | Quality |
|--------|-----|---------|
| EIA World Oil Transit Chokepoints (March 2026) | Malacca, Hormuz, Panama throughput | Gold standard |
| RAND RR-1140-A (Gompert et al., 2016) | GDP impact of blockade | Gold standard |
| Energy Institute Statistical Review (2023) | Production/consumption balances | Gold standard |
| DoD Comptroller FY2026 Budget | Defense spending | Gold standard |
| IEA Oil Market Report (April 2026) | Supply swing, outage ceiling | Gold standard — but **NOT directly fetched** |

### 2.2 Tier-3 sources (weak, critical dependencies)

| Source | Use | Quality concern |
|--------|-----|-----------------|
| **Business Upturn** (April 14, 2026) | IEA 83% flow reduction | **Weak** — secondary aggregator, no original research. **Critical dependency.** |
| ANRPC (natural rubber org.) | Malacca oil throughput | Puzzling — no explanation why a rubber org tracks oil. Likely republishing EIA. |
| Ecoticias | Panama surge data | Weak — environmental news aggregator |

### 2.3 Missing sources that should have been consulted

1. **IEA OMR direct tables** — disruption by cause, not just aggregate
2. **Lloyd's List Intelligence / Casualty database** — direct hull-loss records
3. **UNCTAD / UN Comtrade** — bilateral fertilizer trade matrices
4. **Vortexa / Kpler / MarineTraffic** — AIS vessel tracking for chokepoint throughput
5. **Peer-reviewed academic articles** — Navias & Hooton (1996), Cordesman (1987), Kilian (2008), Barrot & Sauvagnat (2016)

**Overall source quality verdict:** The agent used high-quality sources for most claims, **except for the most important one**. The IEA 83% figure rests on a weak secondary aggregator. This is a **critical vulnerability** in an otherwise well-sourced report.

---

## 3. Claim-by-Claim Audit

### 3.1 Hormuz 80% Severity — Is the 83% IEA Figure Real?

**Status:** ⚠ **Partially Supported, one critical dependency.** The 83% figure relies on Business Upturn (secondary aggregator) + CSIS vessel-transit data (different variable). The CSIS vessel drop (91.5%) corroborates directionally, but vessels ≠ volume. The agent never attempted a second-source cross-check (Reuters, Bloomberg, Platts). **Recommended:** Downgrade from "Confirmed" to "Partially Supported." Downgrade confidence from High to Medium.

### 3.2 Tanker War Attack Counts

**Status:** ⚠ **Adequate but improvable.** Lloyd's List retrospective + UPI archives are acceptable, but not optimal. **Recommended:** Add at least one academic source (Navias & Hooton 1996 or Cordesman 1987) for corroboration. Seek premium time-series rather than point estimates.

### 3.3 Malacca 48%

**Status:** ✓ **Confirmed.** EIA/ANRPC 1H2025 data are solid. Minor clarity issue: scenario doc says "48% of total oil imports" while credibility-historical says "48% of import volumes through the strait." **Recommended:** Reconcile denominators across documents.

### 3.4 RAND GDP Attribution

**Status:** ✓ **Verified with correction. Best piece of detective work.** Correctly distinguishes RR-1140-A (primary) from RRA591-1 (secondary cite). "Twice as large" removal is clean. **Confidence: High.**

### 3.5 Fertilizer $200B+

**Status:** ✓ **Rejected.** Sound methodological process: systematic grep, web search, no source found. **Recommended:** Trace the claim's *origin* — if it appeared in an early draft, note which document and when. The replacement $20–40B range is itself a placeholder requiring verification.

### 3.6 Trade Elasticity 0.5

**Status:** ⚠ **Partially Supported, well-distinguished, with commodity-blindness caveat.** The agent's distinction between trade-flow elasticity (0.35 mean, Brancaccio) and oil demand elasticity (−0.08 to −0.26, Kilian-Murphy) is sound. **Critical nuance missed:** The model applies 0.5 uniformly across oil, fertilizer, and water. Water trade has near-zero short-run price flexibility because freshwater is not globally arbitraged. **Recommended:** Commodity-specific parameters with different values.

### 3.7 ASEAN Sign-Reversal

**Status:** ✗ **Correctly identified, framing debatable.** The agent correctly diagnoses this as a 12-region aggregation artifact. However, calling it a "limitation" rather than a "bug" may be generous — a model predicting the wrong sign for a region's response is pragmatically a bug, even if its origin is known.

### 3.8 Refinery Outage 365 Days

**Status:** ⚠ **Directionally correct but under-argued.** The objection to sustained 365-day outages is fair, but the agent conflates (a) single-attack magnitude (Abqaiq proves ~58% is possible) with (b) sustained global campaign plausibility. **Missing arguments:**
1. Coordinated multi-continent sabotage requires an adversary with global reach and undetected presence at dozens of facilities
2. IEA-coordinated SPR releases (1991, 2005, 2011, 2022) would trigger within 30 days of sustained outage
3. Iran-Iraq refinery destruction (Abadan) is a closer analog — years to restore, but bilateral, not global
**Recommended:** Separate magnitude from duration arguments explicitly.

---

## 4. Logical Gaps

### Untested assumptions

| Assumption | Why untested |
|------------|-------------|
| Insurance-driven avoidance applies equally to all chokepoints | Tanker War validated only for Hormuz; no evidence for Malacca/Panama |
| Stability coupling matrix ($c_{ij}$) is correctly parameterized | No empirical source for political stability diffusion between regions |
| Trade matrix is fixed under non-price-mediated scenarios | Russian re-routing to India/China shows trade reconfigures in 6–12 months |
| 365-day horizon is appropriate | Real crises play out over 12–36 months; 365 days may truncate long-run adjustments |

### Scenarios with zero empirical validation

1. **Water trade subsystem:** The model includes water as a state variable with a bilateral water-trade matrix. **Zero searches, fetches, or parameter checks were conducted on water data.** This is a **major gap** — the model could be producing physically impossible trajectories.

2. **Price-mediated trade parameter `c_t` (transport cost):** Set to 0.1 with no justification. No sensitivity analysis.

3. **Fertilizer trade matrix magnitudes:** Gap identified but never pursued.

### The most important unanswered question

Q3 asks: "Does the 'compounding > additive' claim have any precedent or theory?" After 8 streams, the answer is: "Conceptual support found, but no empirically calibrated model validates the specific claim." The remaining option is **simulation-based verification** — running single/pair/triple chokepoint configurations within the model itself. The agent never proposes or conducts this analysis.

---

## 5. Peer-Review Recommendations

### (a) Corrections (must-fix)

| Issue | Action |
|-------|--------|
| RAND GDP attribution | Attribute GDP figures to **RR-1140-A** throughout; RRA591-1 = fn. 221 reference |
| "Twice as large" ratio | **Remove entirely.** Replace with "qualitatively asymmetric" |
| $200B+ phantom claim | **Remove** across all docs |
| Hormuz baseline discrepancy | Reconcile 20.9 mb/d (EIA) vs. ~20 mb/d (scenario docs) |

### (b) Additional Evidence (must-obtain)

1. **IEA Hormuz factsheet (direct):** The 83% figure must be verified from primary source. Try alternative URLs, IEA press archive, Wayback Machine.
2. **Peer-reviewed Tanker War source:** Add Navias & Hooton (1996) or Cordesman (1987).
3. **UN Comtrade fertilizer data:** Bilateral fertilizer trade matrices for 2020–2024.
4. **IEA emergency response documentation:** Historical SPR triggers and magnitudes to constrain "no institutional response" assumptions.

### (c) Rewordings (must-improve)

| Current | Recommended |
|---------|-------------|
| "compounding > additive" | "sequential elimination of rerouting options creates geographic concentration risk" |
| `price_trade_elasticity` | Rename to `shipping_cost_trade_elasticity` |
| "Confirmed" for Hormuz 83% | "Partially Supported — primary source pending" |
| "Structural limitation" for ASEAN | "Sign-reversed due to 12-region aggregation; SE Asia predictions unreliable" |

### (d) Additions (should-include)

1. **Commodity-specific rerouting speed table:** Oil (weeks), LNG (months), pipeline gas (years), fertilizer (seasonal)
2. **UNCLOS legality section** cross-referenced in all maritime-interdiction scenario docs
3. **Sensitivity analysis for trade elasticity:** Grid search at 0.1, 0.3, 0.5, 0.7, 1.0
4. **Water-trade subsystem documentation:** State clearly that water has received **zero empirical validation**

### (e) Deletions (should-remove)

1. The "50 refinery fires in 45 days" claim (keep only in rejected.md)
2. Repeated "phantom fleet" caveat in sanctions.md (consolidate across docs)

---

## 6. Imputation Assessment

### Stream G ($200B+ Fertilizer) — Rejection: JUSTIFIED

Systematic repo search confirmed no source. Web search confirmed no empirical source. **However:** The agent should have traced the claim's *origin*. If from early research notes, name the document and author. Archival provenance matters.

### Stream F (RAND GDP Attribution) — Rejection: JUSTIFIED

Correctly distinguishes primary from secondary cite. Clean, traceable correction.

### Other claims that should be similarly downgraded

| Claim | Current | Recommended | Reason |
|-------|--------|-------------------|--------|
| Panama "surge artery" | ✓ Confirmed | ⚠ Partially Supported | Sources are Gulf News/Ecoticias (Tier-3) |
| "China SPR buys 60–90 days" | Implicit | ✗ Unverified | No SPR volume data cited |
| "Prices spike globally within days" | Implicit | ⚠ Model output | Not empirically verified |

**Key principle violation:** Several documents intermix **model outputs** with **empirical constraints**. Model predictions must be clearly separated from verified findings.

---

## 7. What Next? Evidence for Future Rounds

### Priority 1: Fix the single-point-of-failure

| Target | Method |
|--------|--------|
| IEA Hormuz factsheet (direct) | wget with user-agent spoofing, IEA press archive, Wayback Machine |
| Reuters/Platts/Bloomberg independent reporting on Hormuz flows | Search for "Hormuz 3.8 mb/d April 2026" across wires |

### Priority 2: Fill water/fertilizer gap

| Target | Dataset |
|--------|---------|
| Fertilizer trade calibration | UN Comtrade HS codes 3102–3105 |
| Water trade calibration | FAO AQUASTAT virtual water data |

### Priority 3: Academic literature sweep

| Topic | Specific papers |
|-------|-----------------|
| Tanker War economic impact | Navias & Hooton (1996), Cordesman (1987), El-Shazly (1998) |
| Trade network fragility | Barrot & Sauvagnat (2016, *QJE*), Carvalho et al. (2021, *Econometrica*) |
| Oil supply shock macro effects | Kilian (2008, *AER*), Hamilton (2009), Baumeister & Hamilton (2019) |
| Resource conflict and political instability | Collier & Hoeffler (2004), Brückner & Ciccone (2011, *AER*) |

### Priority 4: Institutional datasets

| Dataset | Access | Use |
|---------|--------|-----|
| IEA MODS | Subscription/academic | Production/consumption calibration |
| V-Dem Varieties of Democracy | Free academic | Political stability time-series |
| World Bank WDI | Free | GDP/debt/inflation model validation |

### Priority 5: Model self-consistency tests

| Test | Purpose |
|------|---------|
| Single vs. pair vs. triple chokepoint comparison | Test "compounding" claim empirically within the model |
| Sensitivity analysis for `price_trade_elasticity` | Grid search at 0.1, 0.3, 0.5, 0.7, 1.0 |
| 365-day vs. 730-day horizon | Test whether long-run adjustments are truncated |

---

## Overall Assessment

The verification effort is **competent, thorough in places, but has one critical vulnerability** (the IEA 83% figure resting on an unverified secondary aggregator) and **one major omission** (zero water-trade validation). The RAND attribution correction and phantom-rejection are clean, well-executed catches.

**Recommendation:** Accept as a **draft empirical audit** with the following conditions for elevation to publication-ready:
1. Directly verify the IEA 83% flow reduction from primary source
2. Add at least one peer-reviewed academic source for Tanker War data
3. Document the water-trade validation gap explicitly
4. Conduct the single/pair/triple chokepoint comparison within the model
5. Clearly separate model predictions from empirical constraints
6. Add UNCLOS compliance flags to all maritime-interdiction scenarios

**Confidence in overall verification quality: Medium.** The agent did good work within its constraints, but those constraints introduce vulnerabilities in the single most important finding. The report is honest about its limitations, which increases trust in what *was* verified.
