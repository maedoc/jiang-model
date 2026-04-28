# Research Plan: Geopolitical Model Scenario Credibility

## Background
The Geopolitical Resource Dynamics Model (Jiang-Model) describes 9 energy-security scenarios: Hormuz closure, Malacca disruption, Panama disruption, Russia embargo, bilateral sanctions, price-mediated trade, multi-chokepoint compound shock, naval blockade, and refinery sabotage. A critical reader would view many of these as speculative. The current "Empirical Grounding" sections cite model parameters and occasional EIA/ANRPC data but lack independent historical precedent analysis, peer-reviewed literature, or institutional-source verification.

## Key Questions That Must Be Answered

### Q1: Hormuz — Is 80% severity empirically plausible?
- What was the actual traffic reduction during the Iran-Iraq Tanker War (1984–88)?
- How did insurance premiums evolve? Did Lloyd's data show proportional avoidance?
- What did naval escort operations (Earnest Will, Operation Prime Chance) actually achieve in terms of traffic restoration?
- What do peer-reviewed analyses of the Tanker War say about the relationship between physical attacks and traffic volumes?

### Q2: Malacca — Is the "Malacca Dilemma" real, and are the dependency numbers correct?
- What do actual ASEAN energy balance data (EI, IEA, BP statistical review) say about ASEAN's net position?
- What is China's actual Malacca dependency: 48%? Higher? Lower? How has it changed post-2015?
- What are the capacities of the Myanmar-China pipeline, Kra Canal proposals, and Russian ESPO pipeline alternatives?
- Is the model's sign-reversal (ASEAN as net exporter) actually wrong per the data?

### Q3: Multi-chokepoint — Does the "compounding > additive" claim have any precedent or theory?
- What does network science say about cascading failures in trade networks?
- Are there historical examples of simultaneous chokepoint disruptions producing nonlinear effects?
- What do supply-chain resilience models (e.g., from IIASA, MIT) say about redundancy thresholds in energy trade networks?
- Is there any empirically calibrated model of global energy trade that supports phase-transition behavior?

### Q4: Sanctions — Is the "fertilizer hidden vector" actually supported by 2022–2024 data?
- Did EU sanctions on Russia actually restrict fertilizer trade? How much?
- What happened to Russian fertilizer exports post-2022? To Europe? To Asia?
- Is there literature on energy sanctions cascading into food markets via fertilizer?
- Did the 2022–23 food price spike actually correlate with fertilizer supply disruption?

### Q5: Naval blockade — What do RAND and naval strategy literature actually say?
- What does RAND RRA591-1 (or successor studies) quantitatively conclude about distant blockade feasibility?
- What are UNCLOS constraints on high-seas interdiction of commercial shipping?
- What is the historical precedent for naval interdiction of energy flows (Cuba 1962, Iraq 1990–91, Iran sanctions evasion)?
- What force-structure analysis exists for sustaining a Pacific-wide blockade?

### Q6: Refinery sabotage — What is the actual IEA global outage ceiling?
- What does the IEA Oil Market Report (and its monthly supply-disruption tables) actually say about maximum outage rates?
- What are documented cases of large-scale refinery outage (Texas freeze 2021, Colonial Pipeline 2021, etc.)?
- What do critical infrastructure protection studies say about the plausibility of coordinated multi-continent sabotage?
- Is 2.5% truly the institutional ceiling, or can larger outages occur?

### Q7: Price-mediated trade — Is 0.5 elasticity a defensible number?
- What do energy economists estimate as short-run and long-run trade elasticities during supply shocks?
- Do historical rerouting events (e.g., post-Fukushima LNG, post-2022 European gas diversification) support the model's arbitrage mechanism?
- What does the energy trade literature say about the speed and magnitude of trade reallocation during crises?

## Strategy

| Researcher | Dimension | Focus | Sources |
|-----------|-----------|-------|---------|
| R1 | Historical energy security | Q1 (Hormuz), Q2 (Malacca), Q6 (refinery) | EIA, IEA, BP Statistical Review, Lloyd's, USNI, academic papers |
| R2 | Sanctions & trade policy | Q4 (fertilizer/sanctions), Q5 (naval blockade) | RAND, UNCLOS docs, EU sanctions reports, trade databases |
| R3 | Network science & economics | Q3 (compounding), Q7 (elasticity) | IIASA, MIT, academic journals (Energy Economics, Nature Energy), NBER |
| R4 (Lead) | Synthesis | Cross-cut validation, contradictions, parameter plausibility | All of the above |

## Acceptance Criteria
- [ ] All 7 questions answered with ≥2 independent sources each
- [ ] At least 3 quantitative findings with cited numbers (e.g., actual Tanker War traffic reduction percentage)
- [ ] Contradictions between sources identified and flagged
- [ ] Model claims upgraded, downgraded, or rejected based on research
- [ ] Clear mapping of each scenario's empirical status (confirmed / partial / rejected) updated in docs

## Task Ledger
| ID | Owner | Task | Status | Output |
|---|---|---|---|---|
| T1 | R1 | Hormuz historical precedent + Malacca data + IEA outage ceiling | **Complete** | `outputs/credibility-historical.md` |
| T2 | R2 | Sanctions/fertilizer cascade + naval blockade feasibility | **Complete** | `outputs/credibility-policy.md` |
| T3 | R3 | Network compounding + trade elasticity during crises | **Complete** | `outputs/credibility-networks.md` |
| T4 | Lead | Synthesize draft brief, claim sweep, update model docs | **Complete** | `outputs/.plans/geopolitical-model-credibility.md` (updated); scenario docs updated |

## Verification Log
| Item | Method | Status | Evidence |
|---|---|---|---|
| Hormuz 80% severity | Cross-read USNI + Lloyd's + academic papers | **Confirmed** | IEA factsheet: 20 mb/d baseline; observed 3.8 mb/d = ~83% reduction |
| ASEAN sign-reversal | Check EI / IEA consumption vs production data | **Confirmed** | ASEAN is net oil importer (EI 2023); model sign is reversed |
| Multi-chokepoint compounding | Search network-science literature on trade cascades | **Partial** | Brancaccio et al. (2021) trade elasticity 0.35; compounding threshold claims remain unverified in peer-reviewed network literature |
| **Stream B: Malacca 48% China dependency** | **Direct EIA/ANRPC 1H2025 data retrieval** | **Confirmed** | EIA/ANRPC 1H2025: China 7.9 mb/d through Malacca = 48% of import volumes. Total strait throughput 23.2 mb/d (29% of global maritime oil). Crude 16.6 mb/d. Gulf OPEC ~60% of crude. |
| **Stream A: Tanker War attack counts** | **Lloyd's List (March 2026) retrospective + UPI 1984/1987 archives** | **Confirmed** | Lloyd's List: Iraq 283 attacks, Iran 168 attacks (8-year conflict). UPI 1987: Lloyd's tally 333 total since May 1981. Premiums: 0.5% → 3% in 2 months (600% increase); typical rate ~5% during war. |
| Fertilizer sanctions cascade | Check EU sanctions registries + FAO food price data | **Phantom** | No "$200B+" claim found in repo or empirical sources; re-parameterization needed |
| RAND blockade study | Direct fetch of RRA591-1 PDF + cross-check RR-1140-A | **Verified with correction** | GDP figures are from RR-1140-A (10–20% shorter war; 25–35% year-long), cited in RRA591-1 fn. 221; "10–35%" is a composite range. "Twice as large" sender/receiver ratio not found in RAND text. |
| IEA 2.5% ceiling | Direct fetch of IEA Oil Market Report supply tables | **Confirmed** | IEA April 2026 OMR: 2.6 mb/d swing ≈ 2.5% global supply; 50 fires claim rejected |
| Price elasticity 0.5 | Search NBER/CEPR energy trade elasticity papers | **Partial** | Brancaccio et al. (2021) mean=0.35, range 0.1–1.2; 0.5 is within range but uncalibrated for oil demand (Kilian-Murphy 2014: −0.26 demand elasticity) |
| **Peer Review (DeepSeek-v4-Pro)** | **Independent review of all synthesis briefs and docs** | **Completed** | See `outputs/peer-review-deepseek-v4-pro.md`. Verdict: Draft audit accepted with conditions. Critical vulnerability: IEA 83% single-source dependency. Major omission: zero water-trade validation. RAND correction and phantom rejection praised. |

## Peer-Review Feedback Integration

### Critical actions required (DeepSeek Priority 1)
1. **[Hormuz 83%]**: Verify IEA factsheet directly. Try IEA press archive, Wayback Machine, or search Reuters/Platts/Bloomberg for independent corroboration.
2. **[Water trade]**: Zero empirical validation across all 8 streams. Must state explicitly in all docs that water outputs are unverified.
3. **[Trade elasticity]**: 0.5 applied uniformly to oil, fertilizer, water. DeepSeek flags water as near-zero flexibility. Needs commodity-specific parameters.

### Corrections to implement (DeepSeek Priority 2)
- Downgrade Hormuz 83% from "Confirmed" → "Partially Supported — primary source pending"
- Remove "Twice as large" ratio claims everywhere (not in RAND text)
- Rename `price_trade_elasticity` → `shipping_cost_trade_elasticity`
- Separate "model predictions" from "empirical constraints" in docs
- Add UNCLOS violation flags to naval blockade scenarios

### Academic sources to add (DeepSeek Priority 3)
- Navias & Hooton (1996) or Cordesman (1987) for Tanker War data
- Kilian (2008, AER), Hamilton (2009) for oil supply shock macro effects
- Barrot & Sauvagnat (2016, QJE) or Carvalho et al. (2021, Econometrica) for trade-network fragility

### Model self-consistency tests (DeepSeek Priority 4)
- Single vs. pair vs. triple chokepoint comparison (tests "compounding" claim)
- Sensitivity grid: `price_trade_elasticity` at 0.1, 0.3, 0.5, 0.7, 1.0
- 365-day vs. 730-day horizon (tests truncation effects)

## Updated Task Ledger
| ID | Owner | Task | Status | Output |
|---|---|---|---|---|
| T1 | R1 | Hormuz historical precedent + Malacca data | **Complete** | `outputs/credibility-historical.md` |
| T2 | R2 | Sanctions/fertilizer + naval blockade feasibility | **Complete** | `outputs/credibility-policy.md` |
| T3 | R3 | Network compounding + trade elasticity | **Complete** | `outputs/credibility-networks.md` |
| T4 | Lead | Synthesize brief, claim sweep, update docs | **Complete** | 11 files updated |
| **T5** | **DeepSeek** | **Independent peer review** | **Complete** | `outputs/peer-review-deepseek-v4-pro.md` |
| T6 | Lead | Fix IEA 83% single-source vulnerability | **Next** | Direct primary-source verification |
| T7 | Lead | Water-trade validation gap documentation | **Next** | Add "unverified" warnings to water docs |
| T8 | Lead | Academic literature sweep (Navias, Cordesman, Kilian) | **Next** | Add peer-reviewed citations |
| T9 | Lead | Model self-consistency tests (chokepoint combos + elasticity grid) | **Next** | Run simulations, add results |
| T10 | Lead | Commodity-specific trade elasticity (oil/fertilizer/water) | **Next** | Parameter documentation update |
