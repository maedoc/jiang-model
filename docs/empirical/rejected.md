# Rejected / Unverified Hypotheses

These claims contradict official data or lack any verifiable primary source.

---

## 1. "50 refinery fires in 45 days" implies 10–15% global capacity offline

**GT#21 claim:** "Over 50 oil factories that have been on fire these past 45 days."

**Why it fails:**
| Metric | Narrative implication | Empirical bound | Source |
|--------|---------------------|---------------|--------|
| 50 major refinery fires in 45 days | ~10–15% global capacity offline | IEA outage ceiling ≈ **2.5%** | IEA Oil Market Report April 2026 |
| Global refinery capacity | 103,498 kb/d | — | Energy Institute 2023 |
| IEA observed supply swing | −2.6 mb/d (~2.5%) | — | IEA |

The narrative claim implies a destruction rate **4–6× higher** than the IEA's maximum credible supply shock. Even the March 2026 OPEC production collapse (−7.7 mb/d) was a political decision, not physical sabotage.

**Model behavior:** At `severity=0.10+`, the model produces numerically unstable outcomes (negative oil stocks, political stability collapse spirals, solver divergence). This is a **consistency check failure**, not a calibrated scenario.

!!! failure "Rejected"
    Claim contradicts IEA global outage ceiling. Treat as rhetorical, not empirical.

---

## 2. Malacca in model = real Malacca effect

**GT#21 claim:** Southeast Asia is severely impacted by Malacca closure.

**Why it fails:**
The model's trade matrix treats **Southeast Asia as a net exporter**. In reality (EI data, ANRPC), ASEAN is a **net importer** of crude oil. A Malacca closure in the model therefore produces an **exporter-stock-buildup** effect for Southeast Asia — the opposite sign of the real-world impact.

**Mitigation:** The scenario is retained for exploratory analysis but is explicitly flagged as **sign-reversed**.

!!! failure "Rejected / Unverified"
    Model sign does not match empirical ASEAN balance. See [Malacca scenario](../scenarios/malacca.md) for caveats.

---

## 3. "Full GM/Ford conversion" as instantaneous shock

**GT#21 claim:** (Implicit) Rapid industrial pivot to munitions.

**Why it fails:**
- Pentagon-automaker talks are **preliminary** (Reuters April 2026)
- **No contracts signed**
- WWII Willow Run conversion took **months to years**
- Current DoD procurement actually **declined** in FY2026 nominal terms

Any model scenario treating defense-industrial conversion as an instantaneous supply shock (`severity=1.0`, `ramp_days=5`) is **empirically indefensible**.

!!! failure "Rejected / Unverified"
    No evidence of signed contracts or production line conversion. Treat as speculative.

---

## Summary table

| Claim | Status | Primary contradicting source |
|-------|--------|----------------------------|
| 50 refinery fires = 10–15% capacity | **Rejected** | IEA outage ceiling |
| Malacca model effect = real effect | **Rejected** | EI/ANRPC ASEAN net importer |
| Full GM/Ford instant conversion | **Rejected** | Reuters "preliminary talks" |
