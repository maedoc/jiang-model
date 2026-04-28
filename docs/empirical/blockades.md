# Naval Blockade Precedents

## Iran-Iraq Tanker War (1984–1988)

| Metric | Value | Source |
|--------|-------|--------|
| Ships attacked (Iraq) | **283** | Lloyd's List (March 2026), citing Lloyd's historical records |
| Ships attacked (Iran) | **168** | Lloyd's List (March 2026), citing Lloyd's historical records |
| Total ships attacked (Lloyd's 1987 tally) | **~333 since May 1981** | UPI / Lloyd's casualty reporting officer, July 1987 |
| Ships sunk | **~50–70** | Historical consensus |
| Crew killed/kidnapped | **~400+** | USNI |
| Iran oil export reduction (peak) | **~50–60%** | Multiple sources |
| Kharg Island throughput (pre-war) | **~3–4 mb/d** | Historical |
| Kharg Island throughput (war) | **<2 mb/d** | Historical |
| War-risk insurance premium (early 1984) | **0.5% → 3% of cargo value** | UPI / Lloyd's, May 1984 — **600% increase in 2 months** |
| War-risk insurance premium (typical during war) | **~5% of hull value** | Lloyd's List retrospective, March 2026 |
| Some insurers | **Withdrew entirely** from Gulf coverage | Strauss Center |
| Actual flow disruption (Gulf exports) | **~2–4% temporarily interrupted** | Strauss Center |
| Price impact | **~$28 → $30–35+/barrel** | Historical |
| Duration | **~4 years** (1984–1988) | Historical |
| US Operation Earnest Will | Reflagged **11 Kuwaiti tankers** | USNI |
| Lloyd's estimated neutral-vessel losses (first 3 weeks 1984) | **$80 million** | UPI, May 1984 |

**Strategic lesson (Strauss Center):** "Only ~544 attacks over 4 years against thousands of transits, yet the economic impact was enormous — insurance costs drove behavior more than physical damage."

**Strategic lesson (Strauss Center):** "Only ~544 attacks over 4 years against thousands of transits, yet the economic impact was enormous — insurance costs drove behavior more than physical damage."

**Model constraint:** Asymmetric maritime harassment can collapse traffic with minimal physical destruction. The model's `chokepoint_disruption` should have a **nonlinear threshold**: even low-severity physical attacks (severity = 0.1–0.2) can trigger near-total traffic avoidance via insurance/fear effects.

## Red Sea / Suez Disruption (2023–2024, Houthi Attacks)

| Metric | Value | Source |
|--------|-------|--------|
| Suez Canal transit drop | **~42%** | Reuters / shipping analysts |
| Container capacity diverted | **~60–70%** of Asia-Europe routes | Reuters |
| War-risk insurance increase | **5–10x** (0.1% → 0.5–1.0% of hull value) | Reuters / Insurance Journal |
| Reroute via Cape of Good Hope | Adds **~10–14 sailing days**, ~3,000–3,500 nm | Reuters |
| Freight rate surge | **50–100+%** on affected routes | Reuters / Bloomberg |
| Duration | **Ongoing since Nov 2023** | Open-ended |

## Hypothetical U.S. Distant Blockade of China (RAND RRA591-1, 2023)

- Waterborne commercial shipping into China was **"dramatically reduced"**
- Blockade duration modeled: **3–8 months**
- Estimated GDP impact on China: **10–20% decline** (shorter war); **25–35% decline** (year-long severe war). These figures originate in RAND RR-1140-A (Gompert, Cevallos, and Garafola, 2016) and are referenced in RRA591-1 Chapter 4, footnote 221 — not原创 in RRA591-1 itself.
- Estimated U.S. GDP impact: **less than half** of China's (qualitative assessment in RR-1140-A; no exact ratio is provided in RRA591-1)
- Even post-ceasefire, a **"China risk premium"** persisted, causing permanent supply-chain relocation
- China's overland alternatives (Russia, Pakistan, Laos, Myanmar) provided only **partial mitigation**
- Historical analogy: Japan's 1941 response to U.S. oil embargo — "intolerable" blockade induced escalation

**Model constraint:** A naval blockade is asymmetrically damaging to the blockaded party. The model should capture:
- Immediate trade-flow reduction (~60–90% depending on escort availability)
- Insurance/premium spillovers (price effects even without physical shortages)
- Partial rerouting (Cape of Good Hope, overland pipelines) but with capacity limits
- Duration-dependent stability degradation (long blockades → internal unrest)
