# Refinery Capacity Data

## Global capacity by region (2023, Energy Institute)

| Region | Capacity (kb/d) | Share |
|--------|----------------|-------|
| Asia Pacific | 37,463 | 36.2% |
| North America | 21,941 | 21.2% |
| Europe | 14,876 | 14.4% |
| Middle East | 11,601 | 11.2% |
| CIS (Russia+) | 8,421 | 8.1% |
| S. \u0026 Cent. America | 6,239 | 6.0% |
| Africa | 2,956 | 2.9% |
| **Total World** | **103,498** | 100% |

**Notable shifts:**
- China (18,484 kb/d) **surpassed US** (18,429 kb/d) as world's #1 refiner
- OECD capacity fell 2.7%; Non-OECD surged 15.5%
- Refining is migrating from OECD to Asia/Middle East

## Iran refining capacity

| Metric | Value | Source |
|--------|-------|--------|
| Current capacity | **~2.4 mb/d** (June 2025) | Tehran Times / NIORDC |
| Previous capacity | ~2.24 mb/d | NIORDC |
| Net increase (Pezeshkian admin) | +160,000 bpd | NIORDC |
| Major refineries | Abadan, Persian Gulf Star, Isfahan | Tehran Times |

**Note:** Iran's refining capacity is almost entirely for **domestic consumption**. Iran is a crude exporter, not a major refined-product exporter.

## Global supply shock scenarios (IEA, April 2026)

| Metric | Value | Source |
|--------|-------|--------|
| Global supply revision | From +1.1 mb/d to **−1.5 mb/d** | IEA Oil Market Report |
| Swing | **2.6 mb/d downward** | IEA |
| Global demand revision | From +640K to **−80K bpd** | IEA |
| Market surplus | From 2.46 mb/d → **0.41 mb/d** | IEA |
| Brent price | **Above $102/barrel** | IEA |
| OPEC DoC production collapse (March) | **−7.70 mb/d** | IEA |

## Model parameter recommendations

| Parameter | Recommended value | Justification |
|-----------|-------------------|---------------|
| Global refinery sabotage `severity` | **0.15–0.25** (15–25%) | IEA swing = 2.6 mb/d = ~2.5% of global supply. 50 fires ≠ total destruction. |
| Affected regions | Russia, Middle East, Europe, India, SE Asia, Australia | GT#21 claims; EIA data shows these are major refining regions |
| `onset_day` | **30–45** | GT#21 cites "45 days" of fires |
| `ramp_days` | **15–30** | Outages accumulate over weeks |

!!! warning
    The GT#21 narrative claims "over 50 refinery fires in 45 days" implying massive coordinated destruction. The IEA shows a **~2.5% global capacity ceiling** for even severe supply shocks. A 10–15% outage (as implied by 50 major fires) has **no empirical precedent** in the IEA dataset and produces model instability. See [Rejected / Unverified](rejected.md).
