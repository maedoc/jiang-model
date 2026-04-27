# Confirmed Hypotheses

These are claims from Game Theory #21 (and related narratives) that are supported by official energy/defense data and are consistent with model outputs.

---

## 1. Hormuz closure reduces global oil flow by ~83%

**GT#21 claim:** "The world has been cut off from 20% of energy from the Middle East."

**Empirical data:**
| Metric | Value | Source |
|--------|-------|--------|
| Hormuz normal flow | ~20 mb/d | EIA |
| Post-crisis flow | ~3.8 mb/d | IEA April 2026 |
| Reduction | **~83%** | Derived |

**Model output:** `hormuz_closure(severity=0.8)` produces an ~80% reduction in Middle East exports, within 3% of the observed empirical bound.

!!! success "Confirmed"
    Model severity parameter (0.8) is validated by observed EIA/IEA flow collapse (83%).

---

## 2. North America is a resource surplus region

**GT#21 claim:** The U.S. strategy aims to force global dependency on North American resources.

**Empirical data:**
| Region | Balance | Source |
|--------|---------|--------|
| North America | +3,754 kb/d (production > consumption) | Energy Institute 2023 |

**Model output:** The trade matrix shows North America as a net exporter. Under multi-chokepoint scenarios, North American relative economic weight rises.

!!! success "Confirmed"
    North American surplus is validated by EI production/consumption balances.

---

## 3. Naval blockade produces asymmetric impacts

**GT#21 claim:** U.S. boarding of China-bound tankers.

**Empirical data:**
| Precedent | Sender stability effect | Receiver stability effect | Source |
|-----------|------------------------|--------------------------|--------|
| Iran-Iraq Tanker War | Exporters partially resilient | Importers devastated | Lloyd's, Strauss Center |
| RAND distant blockade | "Less than half" of China's GDP impact | 10–35% China GDP decline | RAND RRA591-1 |

**Model output:** `naval_blockade(sender=ME, receiver=China)` shows China stability falling while Middle East stability rises (reduced outbound dependency).

!!! success "Confirmed"
    Asymmetry validated by Tanker War historical data and RAND simulation.

---

## 4. Panama is a crisis surge artery

**GT#21 claim:** (Implicit in strategic logic) Canal traffic is surging amid Hormuz disruption.

**Empirical data:**
| Metric | Value | Source |
|--------|-------|--------|
| Vessel transits/day | 36–38 (near capacity) | Gulf News, Ecoticias April 2026 |
| US LPG to Asia via Panama | >95% | Gulf News |

**Model output:** `panama_disruption(severity=0.6)` shows modest direct oil impact but significant LPG/LNG rerouting effects.

!!! success "Confirmed"
    Surge-artery behavior validated by Gulf News/Ecoticias vessel data.

---

## 5. Multi-chokepoint containment traps ~60–70% of China's imports

**GT#21 claim:** Controlling multiple chokepoints simultaneously is the core U.S. strategy.

**Empirical data:**
| Route | China share | Source |
|-------|-------------|--------|
| Hormuz | ~40% of China's imports via ME crude | IEA |
| Malacca | ~48% of China's total imports | ANRPC |
| Combined dependency | ~60–70% if both closed | Derived |

**Model output:** `compose_interventions([hormuz, malacca, panama])` produces the largest China impact of any scenario in the library.

!!! success "Confirmed"
    Derived dependency arithmetic validated by IEA + ANRPC data.
