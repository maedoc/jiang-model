# Naval Blockade Precedents

## Iran-Iraq Tanker War (1984–1988)

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
