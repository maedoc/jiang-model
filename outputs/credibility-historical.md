# Credibility Brief: Historical Energy Security Precedents
## Hormuz, Malacca, and Refinery Sabotage — Empirical Validation Report

**Date:** 2026-04-27  
**Scope:** Q1 (Hormuz severity), Q2 (Malacca dependency), Q6 (refinery outage ceiling)  
**Sources:** EIA World Oil Transit Chokepoints (March 2026), ANRPC 1H2025, Lloyd's List (March 2026), UPI Archives (1984, 1987), IEA Oil Market Report (April 2026), Energy Institute Statistical Review (2023), RAND RR-1140-A (2016), RAND RRA591-1 (2023).

---

## Executive Summary

| Claim | Status | Key Finding |
|-------|--------|-------------|
| Hormuz 80% severity | **Confirmed** | IEA observed 83% reduction (20 → 3.8 mb/d). Tanker War precedent shows insurance-driven avoidance can collapse traffic with only 2–4% physical flow interruption. |
| Malacca 48% China dependency | **Confirmed** | EIA/ANRPC 1H2025: China 7.9 mb/d = 48% of Malacca import volumes. Total strait throughput 23.2 mb/d (29% of global maritime oil). |
| ASEAN sign-reversal | **Confirmed** | Energy Institute 2023: ASEAN is net oil importer. Model predicts stock buildup; reality would be stock drawdown. |
| Refinery 2.5% ceiling | **Confirmed** | IEA April 2026 OMR: 2.6 mb/d swing ≈ 2.5% global supply. Abqaiq 2019: 64% of facility capacity (4.5/7 mb/d) or 58% of total Saudi production. |
| RAND blockade GDP impact | **Verified with correction** | GDP figures are from RR-1140-A (10–20% shorter war; 25–35% year-long), cited in RRA591-1 fn. 221. "Twice as large" sender/receiver ratio is unverified narrative interpolation. |

---

## 1. Hormuz Strait Closure (Q1)

### 1.1 The 83% IEA Observation

The IEA and EIA both report that in 1H2025, the Strait of Hormuz handled **20.9 mb/d** of total oil (crude + condensate + products). In the April 2026 crisis scenario, IEA observed flows collapsed to **3.8 mb/d** — an **83% reduction**.

The model's 80% severity parameter is therefore **conservative by 3 percentage points** relative to the observed April 2026 event. This is an unusually strong validation for a scenario parameter.

### 1.2 Tanker War Historical Precedent

The Iran-Iraq Tanker War (1984–1988) provides the most relevant historical analog. Independent verification from Lloyd's List (March 2026 retrospective) and UPI archives (1984, 1987) yields:

| Metric | Verified Value | Source |
|--------|---------------|--------|
| Iraqi attacks | 283 vessels | Lloyd's List, March 2026 |
| Iranian attacks | 168 vessels | Lloyd's List, March 2026 |
| Lloyd's 1987 cumulative tally | 333 since May 1981 | UPI, July 1987 |
| Physical flow interruption | ~2–4% of Gulf exports | Strauss Center |
| Iran export reduction (peak) | 50–60% | Multiple sources |
| Premium start (March 1984) | 0.5% of cargo value | UPI / Lloyd's, May 1984 |
| Premium spike (May 1984) | 3.0% of cargo value | UPI / Lloyd's, May 1984 |
| Premium increase magnitude | **600% in 2 months** | Derived |
| Typical premium during war | ~5% of hull value | Lloyd's List, March 2026 |

**Critical insight:** The economic mechanism was *insurance and fear*, not physical destruction. The model correctly captures this through the `chokepoint_disruption` abstraction: a severity parameter that represents net trade reduction, not physical damage.

### 1.3 Bypass Capacity Reality Check

EIA and CSIS data on pipeline bypasses:
- Saudi East-West Pipeline: ~5.0 mb/d capacity, ~2.7 mb/d spare
- UAE Fujairah Pipeline: ~1.0 mb/d
- Iran Goreh-Jask: ~0.3 mb/d (limited utilization)
- Total bypass: ~3.7–4.0 mb/d = **18–20% of normal Hormuz flow**

The model's 80% severity implies ~73% physical blockage after accounting for bypass. This is consistent: if bypass handles ~18–20%, a net 80% reduction implies ~73% of Hormuz capacity is physically obstructed or avoided.

### 1.4 Verdict: Hormuz Scenario

| Aspect | Rating | Rationale |
|--------|--------|-----------|
| Severity parameter (0.8) | ✓ **Plausible, slightly conservative** | Actual observed 83% reduction in April 2026 |
| Insurance mechanism | ✓ **Well-grounded** | Tanker War precedent: 600% premium surge, insurer withdrawals |
| Bypass accounting | ✓ **Consistent with EIA/CSIS** | 18–20% bypass capacity validated |
| Europe impact (minimal) | ✓ **Validated** | Europe only ~0.5 mb/d (~4%) via Hormuz per IEA |
| Duration dynamics | ⚠ **Uncalibrated** | No historical full closure >2 weeks; model runs 365 days |

---

## 2. Malacca Strait Disruption (Q2)

### 2.1 EIA/ANRPC 1H2025 Data

The EIA's March 2026 World Oil Transit Chokepoints report — the most authoritative public source — provides exact figures:

| Metric | Value |
|--------|-------|
| Total oil throughput | **23.2 mb/d** |
| % of global maritime oil trade | **29%** |
| Crude + condensate | **16.6 mb/d** |
| Petroleum products | **6.5 mb/d** |
| LNG | **9.2 Bcf/d** |
| Gulf OPEC crude share | **~60%** |
| China import volume | **7.9 mb/d = 48% of import volumes through strait** |
| South Korea | **2.4 mb/d** |
| Japan | **2.1 mb/d** |
| Iran (despite sanctions) | **1.6 mb/d** (up from 0.3 in 2020) |
| Russia | **0.4 mb/d** |
| USA (Atlantic → East Asia) | **0.8 mb/d** |

**The 48% China figure is directly confirmed by EIA/ANRPC primary-source data.**

### 2.2 The "Malacca Dilemma" Is Real

Chinese strategic literature (the term was coined by President Hu Jintao in 2003) is validated by hard numbers:
- China receives **7.9 mb/d** through Malacca
- This represents **48% of all crude/condensate import volumes** through the strait
- China's **total** oil imports are ~10.5 mb/d (IEA); Malacca thus carries **~75% of China's seaborne oil imports**
- Alternative: Myanmar–China pipeline is **not a viable large-scale alternative** per EIA
- Alternative: Sunda/Lombok straits add **~6,000 nm (~10–14 days)**

### 2.3 ASEAN Sign-Reversal: Confirmed Limitation

The model treats Southeast Asia (region 7) as a **net exporter** because production exceeds consumption in the aggregated region (Indonesia + Malaysia + Singapore + Thailand + Vietnam + Philippines).

**Energy Institute 2023 data:** ASEAN as a whole is a **net oil importer**. The model's prediction of stock buildup for Southeast Asia during a Malacca disruption is therefore **sign-reversed**. The real-world effect would be stock drawdown for the ASEAN importers (Singapore, Thailand, Philippines, Vietnam), partially offset by accumulation in Indonesia/Malaysia.

This is a **structural limitation of the 12-region aggregation**, not a calibration error.

### 2.4 Verdict: Malacca Scenario

| Aspect | Rating | Rationale |
|--------|--------|-----------|
| China 48% dependency | ✓ **Confirmed** | Direct EIA/ANRPC 1H2025 data |
| Japan/Korea dependency | ✓ **Confirmed** | 2.1 and 2.4 mb/d directly reported |
| Throughput magnitude | ✓ **Confirmed** | 23.2 mb/d = world's largest chokepoint |
| No practical alternative | ✓ **Confirmed** | EIA: Myanmar pipeline limited; Sunda/Lombok add 6,000 nm |
| ASEAN stock prediction | ✗ **Sign-reversed** | Model predicts buildup; reality is drawdown (EI 2023) |
| 75% severity | ⚠ **Reasoned estimate** | No full Malacca closure precedent; insurance mechanism would likely dominate |

---

## 3. Refinery Sabotage / Production Outage Ceiling (Q6)

### 3.1 IEA Institutional Ceiling

The IEA Oil Market Report (April 2026) reports a **2.6 mb/d supply swing** — approximately **2.5% of global supply** — as the typical maximum monthly disruption. This is treated by energy analysts as the institutional ceiling for "normal" shock scenarios.

### 3.2 Historical Ceiling: Abqaiq 2019

The September 14, 2019 drone attack on Saudi Aramco's Abqaiq processing facility remains the largest single-site energy infrastructure attack in history:

| Metric | Value | Source |
|--------|-------|--------|
| Abqaiq processing capacity | ~7.0 mb/d | Saudi Aramco / Energy Institute |
| Outage at Abqaiq | 4.5 mb/d | Saudi Aramco |
| % of Abqaiq capacity | **64%** | Derived |
| % of total Saudi production | **58%** (5.7/9.8 mb/d) | Derived |
| Global supply share | ~5.7% | Derived |
| Recovery time | ~2 weeks | Historical |

**Key insight:** A single coordinated attack achieved a **58% production reduction** for a brief period. The model's refinery sabotage scenario assumes multiple geographically distributed attacks, so the per-facility severity could plausibly match or exceed Abqaiq. However, sustaining such outages for 365 days (as the model does) has **no historical precedent**.

### 3.3 Verdict: Refinery Sabotage Scenario

| Aspect | Rating | Rationale |
|--------|--------|-----------|
| 2.5% ceiling as "normal" bound | ✓ **Confirmed** | IEA April 2026 OMR validates |
| Single-site outage ceiling | ✓ **Confirmed by Abqaiq** | 58% of national production possible |
| Multi-site coordinated attack | ⚠ **No precedent** | The model assumes a capability that has never been demonstrated |
| Sustained 365-day outage | ✗ **Unprecedented** | Longest major outage: Abqaiq (~2 weeks), Texas freeze (~2–3 weeks) |
| 15% severity (model default) | ⚠ **Physically possible, duration unrealistic** | Would require sustained campaign; model treats as single shock |

---

## 4. Summary Table: Historical Scenario Credibility

| Scenario | Key Parameter | Verified Value | Model Value | Status |
|----------|--------------|----------------|-------------|--------|
| Hormuz closure | Severity | 83% (IEA April 2026) | 80% | ✓ Confirmed (conservative) |
| Hormuz closure | Bypass capacity | 18–20% (EIA/CSIS) | Implied ~20% | ✓ Confirmed |
| Hormuz closure | Insurance surge | 0.5% → 3% → ~5% (Lloyd's) | Implicit | ✓ Mechanism confirmed |
| Malacca disruption | China dependency | 48% (EIA/ANRPC 1H2025) | 48% | ✓ Confirmed |
| Malacca disruption | Total throughput | 23.2 mb/d (EIA 1H2025) | 22.5–23.7 mb/d | ✓ Confirmed |
| Malacca disruption | ASEAN net position | Net importer (EI 2023) | Net exporter (model) | ✗ Sign-reversed |
| Refinery sabotage | Single-site ceiling | 58% of national prod. (Abqaiq) | 15% global (model) | ⚠ Different scale |
| Refinery sabotage | Duration ceiling | ~2–3 weeks (historical) | 365 days (model) | ✗ Unprecedented |

---

## Recommendations for Model Documentation

1. **Hormuz:** Add explicit citation to the IEA 83% observed reduction and Lloyd's premium trajectory (0.5% → 3% → ~5%).
2. **Malacca:** Flag the ASEAN sign-reversal as a known structural limitation in all scenario documentation.
3. **Refinery sabotage:** Add a duration-realism warning: the model assumes sustained outages that have no historical precedent beyond ~2–3 weeks.
4. **General:** Cross-reference all scenario parameters against the EIA World Oil Transit Chokepoints (March 2026) update cycle, as this is now the highest-quality public data source.
