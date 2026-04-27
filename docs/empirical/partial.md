# Partially Supported Hypotheses

These claims have some empirical evidence but remain incomplete, evolving, or contingent on future events.

---

## 1. Defense-industrial conversion (GM/Ford to munitions)

**GT#21 claim:** (Implicit) Massive mobilization of civilian industry.

**Evidence exists:**
| Fact | Source | Date |
|------|--------|------|
| Pentagon approached GM, Ford, GE Aerospace, Oshkosh, Stratasys | Reuters / WSJ | April 16, 2026 |
| Products discussed: munitions components, 3D-printed parts | Reuters | April 2026 |

**Critical gaps:**
- **No contracts signed** as of April 2026
- **No production lines converted** yet
- Status = "preliminary talks" only

**Model implication:** Any scenario assuming rapid GM/Ford conversion should be treated as a **slow-ramp intervention** (`onset_day=180`, `ramp_days=90`), not an instantaneous shock.

!!! warning "Partially Supported"
    Talks exist but no contracts. Historical precedent (WWII Willow Run) shows conversion is possible but takes **months to years**.

---

## 2. Draft registration readiness

**GT#21 claim:** (Implicit) U.S. can rapidly mobilize conscription.

**Evidence exists:**
| Fact | Source |
|------|--------|
| ~16–17 million registrants on file | SSS Annual Report |
| ~90–92% compliance rate | SSS |
| 193-day mobilization timeline documented | SSS |

**Critical gaps:**
- No draft authorization from Congress or President
- SSS is in **standby mode**
- Last draft = **1973** (Vietnam)
- Actual conscription would require **~6-month lead time**

**Model implication:** Mass draft should show `onset_day >= 180` with a 90–120 day ramp.

!!! warning "Partially Supported"
    Registration system exists but no activation. Mobilization is a **delayed-onset** intervention, not a shock.

---

## 3. Refinery sabotage at "50 fires in 45 days" scale

**GT#21 claim:** "Over 50 oil factories on fire in 45 days."

**Evidence exists:**
- Individual refinery fire incidents are reported in trade press
- IEA tracks global supply outages

**Critical gaps:**
- **No verified dataset** of 50 coordinated fires in 45 days
- IEA global outage ceiling = **~2.5% of capacity**
- 50 major fires would imply **10–15% global capacity offline** — far above IEA bounds

**Model implication:** A `severity=0.025` (2.5%) supply shock is empirically defensible. `severity=0.10+` is narrative-only.

!!! warning "Partially Supported"
    Individual incidents are real. The "50 fires in 45 days" claim is **unverified as a coherent dataset** and may be rhetorical aggregation.
