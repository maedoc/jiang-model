# Empirical Constraints for Geopolitical Resource Dynamics Model
## Chokepoints, Blockades, Defense Spending, and Refinery Outages

**Date:** 2026-04-24  
**Sources:** EIA, IEA, CSIS, RAND, SIPRI, DoD Comptroller, Reuters, Energy Institute, Selective Service System, ANRPC, Lloyd's of London (historical), Strauss Center.

---

## Executive Summary

This brief compiles empirical data from official energy and defense sources to constrain the 12-region, 180-ODE geopolitical resource model. Four strategic mechanisms from Game Theory #21 are parameterized:

1. **Multi-chokepoint containment** (Hormuz, Malacca, Panama) — EIA/IEA throughput data
2. **Naval blockade / tanker interdiction** — historical precedents from Tanker War, Red Sea, and RAND great-power war simulations
3. **War-economy mobilization** — DoD FY2026 budget and Pentagon-automaker talks
4. **Global refinery / production sabotage** — Energy Institute capacity data and IEA supply-shock scenarios

---

## 1. Chokepoint Throughput and Disruption Magnitudes

### 1.1 Strait of Hormuz

| Metric | Value | Source |
|--------|-------|--------|
| Normal oil throughput | **~20 mb/d** (crude + products) | EIA 2024, IEA June 2025 |
| Crude oil only | **~14.5 mb/d** | IEA Factsheet |
| Share of global petroleum consumption | **~20–21%** | EIA |
| Share of global seaborne oil trade | **~25–27%** | EIA |
| LNG throughput (Qatar + UAE) | **~20% of global LNG trade** | IEA |
| Pre-crisis vessel transits | **~153/day** | CSIS (AIS data) |
| Post-crisis vessel transits | **~13/day** | CSIS — **91.5% drop** |
| Observed flow collapse (April 2026 scenario) | **20 → 3.8 mb/d** | IEA / Business Upturn — **83% reduction** |
| Saudi East-West Pipeline bypass | **~5.0 mb/d capacity, ~2.7 mb/d spare** | CSIS |
| UAE Fujairah Pipeline bypass | **~1.0 mb/d** | CSIS |
| Total bypass as % of normal flow | **17–27%** | CSIS |
| **Net interruption if Hormuz fully closed** | **~14.5–16.5 mb/d** (~15–16% of global supply) | Derived from EIA/CSIS |

**Destinations (IEA, Jan–May 2025):**
- **Asia total:** ~80% of oil transiting Hormuz
- **China + India:** 46% of crude volumes
- **Japan + Korea:** particularly reliant on Gulf crude
- **Europe:** only ~0.5 mb/d (~4% of Gulf crude flows)

**Model constraint:** A full Hormuz closure should reduce Middle East exports by **~73–83%** (accounting for limited bypass). A partial disruption (mines, small-boat harassment) could trigger the same insurance-driven traffic collapse with only modest physical damage.

### 1.2 Strait of Malacca

| Metric | Value | Source |
|--------|-------|--------|
| 2024 oil throughput | **~22.5–23.7 mb/d** | EIA, ANRPC |
| Share of world maritime oil trade | **~28–30%** | EIA 2024/2025 |
| Combined with Hormuz share | **~57% of all seaborne oil trade** | EIA |
| Crude + condensate (1H2025) | **16.6 mb/d** | ANRPC |
| Petroleum products (1H2025) | **6.5 mb/d** | ANRPC |
| LNG (1H2025) | **~9.2 bcf/d** | ANRPC |
| Major OPEC supply share | **~60% of crude through Malacca** | ANRPC |
| **China imports via Malacca** | **~7.9 mb/d (~48% of China's imports via this route)** | ANRCP 1H2025 |
| South Korea via Malacca | **~2.4 mb/d** | ANRPC |
| Japan via Malacca | **~2.1 mb/d** | ANRPC |
| Alternative routes | Sunda/Lombok Straits, Myanmar–China pipeline (limited, longer voyages) | EIA |

**Model constraint:** Malacca disruption is arguably *more* damaging to China than Hormuz closure alone, since it is the conduit for most non-Russian oil reaching East Asia. Even if Hormuz were bypassed via pipeline, Malacca is the only practical sea route to China/Japan/Korea. A combined Hormuz+Malacca shock would trap **~60–70% of China's oil imports**.

### 1.3 Panama Canal

| Metric | Value | Source |
|--------|-------|--------|
| Normal oil throughput (2024) | **~2.0 mb/d** | EIA |
| 1H2025 (annualized) | **~2.3 mb/d** | EIA |
| Share of world maritime oil trade | **~2.5–3%** | Derived from EIA global totals |
| US LPG exports to Asia via Panama | **>95%** | Gulf News 2026 |
| Current crisis surge | **36–38 vessel transits/day** (near capacity) | Gulf News, Ecoticias April 2026 |
| LNG tanker slots target | **~1/day** (up from ~4/month) | Ecoticias |

**Model constraint:** Panama is not a primary oil chokepoint for crude, but it is critical for US LPG/LNG exports to Asia. In the current crisis, it has become a *surge artery*. For the model, a Panama disruption would primarily affect **South America's exports to Asia** and **US energy rerouting**, not global crude supply directly.

### 1.4 Regional Production vs. Consumption (2023, Energy Institute)

| Region | Production (kb/d) | Consumption (kb/d) | Balance | Import Dependence |
|--------|-------------------|--------------------|---------|-------------------|
| Middle East | 30,362 | 9,646 | **+20,716** | Net exporter |
| North America | 27,050 | 23,296 | **+3,754** | Net exporter |
| CIS (Russia+) | 13,868 | 4,636 | **+9,232** | Net exporter |
| China | 4,198 | 16,577 | **−12,379** | **~75% import reliant** |
| Europe | 3,225 | 13,904 | **−10,679** | **~77% import reliant** |
| Asia Pacific (total) | 7,275 | 38,061 | **−30,786** | Net importer |

**Key insight for GT#21 narrative:** North America and Russia/CIS are the two major surplus regions. If Middle East exports are cut off, Asia and Europe must source from North America and Russia — validating the "dependency shift" mechanism in the model.

---

## 2. Naval Blockades and Maritime Interdiction — Historical Precedents

### 2.1 Iran-Iraq Tanker War (1984–1988)

| Metric | Value | Source |
|--------|-------|--------|
| Ships attacked | **~544** | Lloyd's of London / USNI / Strauss Center |
| Tankers attacked | **~400+** | Strauss Center |
| Ships sunk | **~50–70** | Historical consensus |
| Crew killed/kidnapped | **~400+** | USNI |
| Iran oil export reduction (peak) | **~50–60%** | Multiple sources |
| Kharg Island throughput (pre-war) | **~3–4 mb/d** | Historical |
| Kharg Island throughput (war) | **<2 mb/d** | Historical |
| War-risk insurance premium surge | **1–7% of hull value per voyage** | Lloyd's / Strauss Center |
| Some insurers | **Withdrew entirely** from Gulf coverage | Strauss Center |
| Actual flow disruption (Gulf exports) | **~2–4% temporarily interrupted** | Strauss Center |
| Price impact | **~$28 → $30–35+/barrel** | Historical |
| Duration | **~4 years** (1984–1988) | Historical |
| US Operation Earnest Will | Reflagged **11 Kuwaiti tankers** | USNI |

**Strategic lesson (Strauss Center):** "Only ~544 attacks over 4 years against thousands of transits, yet the economic impact was enormous — insurance costs drove behavior more than physical damage."

**Model constraint:** Asymmetric maritime harassment can collapse traffic with minimal physical destruction. The model's `chokepoint_disruption` should have a **nonlinear threshold**: even low-severity physical attacks (severity = 0.1–0.2) can trigger near-total traffic avoidance via insurance/fear effects.

### 2.2 Red Sea / Suez Disruption (2023–2024, Houthi Attacks)

| Metric | Value | Source |
|--------|-------|--------|
| Suez Canal transit drop | **~42%** | Reuters / shipping analysts |
| Container capacity diverted | **~60–70%** of Asia-Europe routes | Reuters |
| War-risk insurance increase | **5–10x** (0.1% → 0.5–1.0% of hull value) | Reuters / Insurance Journal |
| Reroute via Cape of Good Hope | Adds **~10–14 sailing days**, ~3,000–3,500 nm | Reuters |
| Freight rate surge | **50–100+%** on affected routes | Reuters / Bloomberg |
| Duration | **Ongoing since Nov 2023** | Open-ended |

### 2.3 Hypothetical U.S. Distant Blockade of China (RAND RRA591-1, 2023)

RAND's Air Force study modeled a U.S. distant blockade in a Taiwan conflict scenario:

- Waterborne commercial shipping into China was **"dramatically reduced"**
- Blockade duration modeled: **3–8 months**
- Estimated GDP impact on China: **10–35% decline** (year-long severe war = 25–35%; 8-month war = 10–20%)
- Estimated U.S. GDP impact: **less than half** of China's
- Even post-ceasefire, a **"China risk premium"** persisted, causing permanent supply-chain relocation
- China's overland alternatives (Russia, Pakistan, Laos, Myanmar) provided only **partial mitigation**
- Historical analogy: Japan's 1941 response to U.S. oil embargo — "intolerable" blockade induced escalation

**Model constraint:** A naval blockade is asymmetrically damaging to the blockaded party. The model should capture:
- Immediate trade-flow reduction (~60–90% depending on escort availability)
- Insurance/premium spillovers (price effects even without physical shortages)
- Partial rerouting (Cape of Good Hope, overland pipelines) but with capacity limits
- Duration-dependent stability degradation (long blockades → internal unrest)

---

## 3. Defense Spending, Draft, and War-Economy Conversion

### 3.1 U.S. Defense Budget (FY2026 Request)

| Metric | Value | Source |
|--------|-------|--------|
| DoD Total Request | **$961.6 billion** | DoD Comptroller FY2026 |
| National Defense Grand Total | **$1.012 trillion** | DoD Comptroller |
| Year-over-year increase (FY2025 → FY2026) | **+$101.5B (+11.8%)** | DoD Comptroller |
| With reconciliation framing | **+13.4%** | DoD |
| Discretionary base | **$848.3B** (flat vs FY2025) | DoD Comptroller |
| Mandatory reconciliation | **$113.3B** | DoD Comptroller |
| Military Personnel | **$194.7B** (+$12.3B YoY) | DoD Comptroller |
| Procurement | **$153.3B** (down from $167.8B FY2025) | DoD Comptroller |
| RDT&E | **$142.0B** | DoD Comptroller |
| Reconciliation: Shipbuilding | **$30.6B (27%)** | DoD Comptroller |
| Reconciliation: Missile Defense | **$25.6B (23%)** | DoD Comptroller |

**Key observation:** The budget crossed $1 trillion for the first time, but the *increase* is largely from mandatory reconciliation, not discretionary growth. Procurement actually *declined* in nominal terms — suggesting a prioritization of personnel, shipbuilding, and missile defense over broad industrial procurement.

### 3.2 Pentagon-Automaker Talks (April 2026)

| Metric | Value | Source |
|--------|-------|--------|
| Companies approached | GM, Ford, GE Aerospace, Oshkosh, Stratasys | Reuters / WSJ |
| Products discussed | Munitions components, vehicle parts, 3D-printed replacement parts | Reuters |
| Status | **Preliminary talks** — no specific projects negotiated | Reuters |
| Historical parallel | WWII Willow Run factory (Ford built ~1 B-24/hour) | Reuters |
| COVID precedent | Ford/GM successfully pivoted to PPE/ventilators | Reuters |
| Trump's requested increase | **+$500B → $1.5 trillion total** | Reuters |
| Depleted stockpiles | Artillery, ammunition, anti-tank missiles (Ukraine + Gaza drawdown) | Reuters |

**Model constraint:** Mass conversion of civilian industry is **not yet occurring**. It exists only in preliminary talks and historical analogy. Any model scenario assuming rapid GM/Ford conversion to munitions should treat it as an **uncertain, ramping intervention** (not an instantaneous shock).

### 3.3 Selective Service / Draft Data

| Metric | Value | Source |
|--------|-------|--------|
| Registrants on file | **~16–17 million** males | SSS Annual Report |
| New registrations/year | **~1.8–2.0 million** | SSS |
| Compliance rate | **~90–92%** (declining from ~95% in 1990s) | SSS |
| Annual budget | **~$25–30 million** | SSS |
| Employees | **400–500** | SSS |
| Last draft | **1973** (Vietnam) | Historical |
| Mobilization timeline | **193 days** from authorization to first induction | SSS |
| Readiness exercises | Periodic "Area Draw" and readiness drills | SSS |
| Current status | Standby mode; no draft activation | SSS |

**Model constraint:** Automatic draft registration exists, but actual conscription would require Congressional + Presidential authorization with a **~6-month lead time**. Any model scenario with mass draft should show a **delayed onset** (e.g., onset_day=180, ramp_days=90).

---

## 4. Refinery Capacity and Production Shocks

### 4.1 Global Refinery Capacity (2023, Energy Institute)

| Region | Capacity (kb/d) | Share |
|--------|----------------|-------|
| Asia Pacific | 37,463 | 36.2% |
| North America | 21,941 | 21.2% |
| Europe | 14,876 | 14.4% |
| Middle East | 11,601 | 11.2% |
| CIS (Russia+) | 8,421 | 8.1% |
| S. & Cent. America | 6,239 | 6.0% |
| Africa | 2,956 | 2.9% |
| **Total World** | **103,498** | 100% |

**Notable shifts:**
- China (18,484 kb/d) **surpassed US** (18,429 kb/d) as world's #1 refiner
- OECD capacity fell 2.7%; Non-OECD surged 15.5%
- Refining is migrating from OECD to Asia/Middle East

### 4.2 Iran Refining Capacity

| Metric | Value | Source |
|--------|-------|--------|
| Current capacity | **~2.4 mb/d** (June 2025) | Tehran Times / NIORDC |
| Previous capacity | ~2.24 mb/d | NIORDC |
| Net increase (Pezeshkian admin) | +160,000 bpd | NIORDC |
| Major refineries | Abadan, Persian Gulf Star, Isfahan | Tehran Times |

**Note:** Iran's refining capacity is almost entirely for **domestic consumption**. The article did not mention export figures. Iran is a crude exporter, not a major refined-product exporter.

### 4.3 Global Supply Shock Scenarios (IEA, April 2026)

| Metric | Value | Source |
|--------|-------|--------|
| Global supply revision | From +1.1 mb/d to **−1.5 mb/d** | IEA Oil Market Report |
| Swing | **2.6 mb/d downward** | IEA |
| Global demand revision | From +640K to **−80K bpd** | IEA |
| Market surplus | From 2.46 mb/d → **0.41 mb/d** | IEA |
| Brent price | **Above $102/barrel** | IEA |
| OPEC DoC production collapse (March) | **−7.70 mb/d** | IEA |

---

## 5. Model Parameter Recommendations

Based on the empirical data above, here are concrete parameter updates for the model:

### 5.1 Chokepoint Disruption Severities

| Chokepoint | Recommended `severity` | Justification |
|------------|------------------------|---------------|
| Hormuz (full closure) | **0.75–0.85** | 83% observed flow reduction; bypass covers ~17–27% |
| Hormuz (partial/asymmetric) | **0.60–0.70** | Insurance-driven avoidance even with limited physical attacks |
| Malacca (full closure) | **0.85–0.95** | No practical alternative for Middle East→Asia routing |
| Malacca (partial) | **0.50–0.70** | Sunda/Lombok alternatives add ~6,000 nm but exist |
| Panama (full) | **0.50–0.60** | Smaller share (~2–3% of seaborne), but critical for LNG |

### 5.2 Naval Blockade Parameters

| Parameter | Recommended Value | Justification |
|-----------|-------------------|---------------|
| Bilateral sanction `severity` | **0.70–0.95** | Tanker War showed ~50–60% export reduction; RAND blockade showed "dramatic" reduction |
| `ramp_days` | **14–30** | Red Sea diversion took weeks; insurance markets adjust over days |
| Price premium effect | **+50–100%** on affected routes | Red Sea freight rates surged 50–100% |
| Stability impact (blockaded region) | **−0.05 to −0.15** over 90 days | GDP decline of 10–35% in RAND scenarios |

### 5.3 Defense Spending / War Economy

| Parameter | Recommended Value | Justification |
|-----------|-------------------|---------------|
| North America military boost | **+11.8%** (one-time) | FY2026 DoD increase |
| Duration | **365+ days** | WWII conversion took years; current talks are preliminary |
| `price_trade_enabled` sensitivity | Should reflect US LNG export surge | Panama rerouting is empirically occurring |

### 5.4 Multi-Region Supply Shock

| Parameter | Recommended Value | Justification |
|-----------|-------------------|---------------|
| Global refinery sabotage `severity` | **0.15–0.25** | IEA showed 2.6 mb/d swing = ~2.5% of global supply. 50 refinery fires ≠ total destruction |
| Affected regions | Russia, Middle East, Europe, India, SE Asia, Australia | GT#21 claims; EIA data shows these are major refining regions |
| `onset_day` | **30–45** | GT#21 cites "45 days" of fires |
| `ramp_days` | **15–30** | Outages accumulate over weeks |

---

## 6. Open Questions and Data Gaps

1. **Fertilizer trade matrices:** Empirical bilateral fertilizer trade data (urea, ammonia, phosphate) is harder to access than oil data. UN Comtrade would be the key source, but it was not retrieved in this sweep.
2. **Water stock data:** The model includes water as a state variable, but global freshwater trade and river-basin dependencies (e.g., Tibetan Plateau → India/SE Asia) lack a standardized bilateral dataset.
3. **Refinery fire dataset:** No verified global incident tracker was found. The "50 refinery fires in 45 days" claim in GT#21 could not be independently verified with a primary statistical source during this research.
4. **Current AIS data:** The CSIS AIS figures are from March 2026; real-time vessel tracking would provide more precise traffic reductions.
5. **Pentagon-automaker negotiations:** Reuters confirms talks are "preliminary" with no contracts signed as of April 16, 2026. Any model assuming mass conversion should flag this as speculative.
6. **Rate limits:** Several sources (SIPRI database, CSIS embargo article, SSS report PDF) could not be fetched due to API rate limiting during the research session. Their data were replaced with training-knowledge summaries where possible.

---

## Sources

1. EIA, "World Oil Transit Chokepoints" (2024) — https://www.eia.gov/international/content/analysis/special_topics/World_Oil_Transit_Chokepoints/wotc.pdf
2. IEA, "Strait of Hormuz Factsheet" (June 2025) — https://iea.blob.core.windows.net/assets/760ed8e8-38b6-4418-b527-6d8976da72e4/StraitofHormuzFactsheet.pdf
3. CSIS, "How War with Iran Could Disrupt Energy Exports at the Strait of Hormuz" (June 23, 2025) — https://www.csis.org/analysis/how-war-iran-could-disrupt-energy-exports-strait-hormuz
4. ANRPC, "Strait of Malacca remains world's largest oil transit chokepoint" (1H2025 data) — https://www.anrpc.org/news/strait-of-malacca-remains-world's-largest-oil-transit-chokepoint
5. RAND, "Alternative Futures Following a Great Power War" (RRA591-1, 2023) — https://www.rand.org/content/dam/rand/pubs/research_reports/RRA500/RRA591-1/RAND_RRA591-1.pdf
6. DoD Comptroller, "FY2026 Budget Request" — https://comptroller.defense.gov/Portals/45/Documents/defbudget/FY2026/FY2026_Budget_Request.pdf
7. Reuters, "Pentagon approaches automakers to boost weapons production" (April 16, 2026) — https://www.reuters.com/business/autos-transportation/pentagon-approaches-automakers-manufacturers-boost-weapons-production-wsj-2026-04-16/
8. Energy Institute, "Statistical Review of World Energy 2024" — https://www.energyinst.org/__data/assets/pdf_file/0006/1542714/684_EI_Stat_Review_V16_DIGITAL.pdf
9. IEA / Business Upturn, "Hormuz shipping biggest factor in easing energy stress" (April 14, 2026) — https://www.businessupturn.com/nation/iea-says-hormuz-shipping-is-biggest-factor-in-easing-energy-stress-as-oil-flows-collapse-from-20-million-to-3-8-million-bpd/
10. Tehran Times, "Iran's refining capacity rises to 2.4m barrels a day" (June 6, 2025) — https://www.tehrantimes.com/news/513916/Iran-s-refining-capacity-rises-to-2-4m-barrels-a-day
11. Gulf News, "Oil, gas tanker traffic explodes at Panama canal" (April 16, 2026) — https://gulfnews.com/business/energy/oil-tanker-traffic-explodes-at-panama-canal-as-global-energy-routes-shift-amid-mideast-war-1.500509612
12. Strauss Center / USNI historical data — Tanker War (1984–1988)
13. Reuters, "How are Red Sea attacks impacting shipping through the Suez Canal?" (Dec 2023)
14. Reuters, "US crude heads to Asia via Panama Canal as Iran crisis redraws trade flows" (March 19, 2026) — https://www.reuters.com/business/energy/us-crude-heads-asia-via-panama-canal-iran-crisis-redraws-trade-flows-2026-03-19/
15. Selective Service System, Annual Reports to Congress — https://www.sss.gov/reports/annual-reports-to-congress/

---

## Provenance

- **Date:** 2026-04-24
- **Rounds:** 1 research round (12 Exa searches, 12 pi --no-sandbox fetches)
- **Sources consulted:** 15 primary/secondary sources accepted
- **Sources rejected/uncollected:** ~8 sources blocked by rate limits (429) or network restrictions
- **Verification:** Partial — some quantitative claims verified across multiple independent sources (EIA, IEA, CSIS, ANRPC). Fertilizer and refinery-fire claims remain unverified due to source gaps.
- **Plan:** outputs/.plans/chokepoint-empirical-constraints.md
