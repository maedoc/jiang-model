# Defense Spending \u0026 War Economy

## U.S. Defense Budget (FY2026 Request)

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
| RDT\u0026E | **$142.0B** | DoD Comptroller |
| Reconciliation: Shipbuilding | **$30.6B (27%)** | DoD Comptroller |
| Reconciliation: Missile Defense | **$25.6B (23%)** | DoD Comptroller |

**Key observation:** The budget crossed $1 trillion for the first time, but the *increase* is largely from mandatory reconciliation, not discretionary growth. Procurement actually *declined* in nominal terms — suggesting a prioritization of personnel, shipbuilding, and missile defense over broad industrial procurement.

## Pentagon-Automaker Talks (April 2026)

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

## Selective Service / Draft Data

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

**Model constraint:** Automatic draft registration exists, but actual conscription would require Congressional + Presidential authorization with a **~6-month lead time**. Any model scenario with mass draft should show a **delayed onset** (e.g., `onset_day=180`, `ramp_days=90`).
