# Malacca Strait Disruption

## The jugular vein of East Asian energy security

If Hormuz is the aorta, Malacca is the jugular. The strait carries roughly **22.5–23.7 million barrels per day** of oil—more than Hormuz by volume—and approximately **28–30% of all maritime oil trade globally**. Unlike Hormuz, where Saudi Arabia and the UAE have invested billions in pipeline bypasses, **Malacca has no practical alternative**. The Sunda and Lombok straits exist, but they add roughly 6,000 nautical miles to the voyage from the Middle East to East Asia. The Myanmar–China pipeline is operational but carries only a fraction of China's demand.

This is why strategists in Beijing view Malacca with far greater anxiety than Hormuz. Chinese strategic literature has coined the term **"Malacca Dilemma"** to describe the existential vulnerability of having 48% of total oil imports (and roughly 80% of seaborne imports) pass through a single chokepoint controlled by multiple nations—Malaysia, Indonesia, and Singapore—each of which hosts a significant U.S. military presence or defense relationship.

## Why this scenario matters

In the Game Theory #21 narrative, Malacca is not disrupted by mines or missiles. Instead, it is subjected to the same **insurance-collapse mechanism** that historically choked Hormuz: asymmetric harassment of commercial shipping, combined with explicit or implicit threats from naval forces. The ANRPC (Asia Natural Rubber Producers' Corporation, which also tracks maritime oil data) reported that in the first half of 2025, **7.9 mb/d of Chinese imports** transited Malacca. South Korea and Japan depend on the strait for 2.4 and 2.1 mb/d respectively.

The model's Malacca disruption therefore tests a critical claim: that controlling Malacca is **more damaging to China than controlling Hormuz**, because Hormuz can be partially bypassed by pipeline, while Malacca cannot.

## How the model implements the disruption

```python
from interventions import malacca_disruption

iv = malacca_disruption(
    onset_day=100.0,
    severity=0.75,     # 75% of Southeast Asia's exports blocked
    ramp_days=14.0,   # Gradual escalation over two weeks
)
```

This applies `chokepoint_disruption` to `exporter_region=7` (Southeast Asia), affecting all three trade matrices. The severity of 0.75 is chosen because:
- A full closure is physically improbable
- The Sunda/Lombok alternatives would absorb some traffic
- Insurance-driven avoidance would peak at roughly 70–80% of normal traffic

The 14-day ramp reflects the time required for markets to fully process the threat and for alternative routing logistics to be attempted and abandoned.

## Model predictions vs. empirical constraints

Unlike the Hormuz scenario, we do not have a dedicated figure for the standalone Malacca disruption. Instead, the model's Malacca effect is most clearly visible in the [Multi-Chokepoint scenario](multi_chokepoint.md), where it compounds with Hormuz and Panama.

However, the model does make clear predictions for a standalone Malacca shock:

| Model prediction | Expected behavior | Empirical plausibility |
|-----------------|-------------------|----------------------|
| China oil stocks decline steeply | China loses 48% of import pathway | ✓ ANRPC validates dependency |
| Japan/Korea suffer proportionally | Both highly Malacca-dependent | ✓ EIA/ANRPC validate route shares |
| Southeast Asia stock buildup | Model treats SE Asia as net exporter | ✗ **Sign reversed in reality** |
| Price spike exceeds Hormuz alone | Worse bottleneck (no pipeline bypass) | ✓ EIA data supports severity |

### Critical model limitation

!!! warning "Sign-Reversed Effect for Southeast Asia"
    The model treats Southeast Asia (region 7) as a **net exporter** because its trade matrix is derived from aggregated production-consumption balances, and the region includes substantial Indonesian and Malaysian oil production. In reality, ASEAN as a whole is a **net importer** of crude oil. This means the model predicts a *stock buildup* for Southeast Asia (exporters cannot export), while the real-world effect would be a *stock drawdown* (importers cannot import).
    
    This is not a calibration error but a **structural limitation** of the 12-region aggregation. Indonesia and Malaysia are exporters; Singapore, Thailand, Vietnam, and the Philippines are importers. The model collapses this heterogeneity into a single region. The standalone Malacca scenario is therefore retained for exploratory sensitivity analysis but flagged as **not empirically reliable** for Southeast Asia itself.

## How Malacca compounds with Hormuz

The true strategic significance of Malacca becomes visible only when combined with Hormuz:

| Route | China's import share | Transits |
|-------|---------------------|----------|
| Middle East → China via Hormuz + Malacca | ~40% of total imports | Both chokepoints |
| Russia → China via pipeline | ~15–20% | No chokepoints |
| Angola/Brazil → China via Cape of Good Hope | ~15% | No chokepoints |
| SE Asia domestic/South China Sea | ~10% | Partially via Malacca |
| Other (Central Asia, Central Asia) | ~10–15% | No chokepoints |

If Hormuz closes, China's Middle East supply is cut. If Malacca *also* closes, even the Middle East crude that might have been rerouted via pipeline (East-West to Red Sea, then around Africa) now faces a second blockage. The model's multi-chokepoint scenario captures this: the compound effect is not 80% + 75% = 155%, but rather the **sequential elimination of rerouting options**.

## Empirical grounding

| Metric | Value | Source |
|--------|-------|--------|
| 2024 oil throughput | ~22.5–23.7 mb/d | EIA, ANRPC |
| Share of world maritime oil trade | ~28–30% | EIA 2024/2025 |
| Combined with Hormuz share | **~57% of all seaborne oil trade** | EIA |
| China imports via Malacca | ~7.9 mb/d (~48% of China's imports) | ANRPC 1H2025 |
| South Korea via Malacca | ~2.4 mb/d | ANRPC |
| Japan via Malacca | ~2.1 mb/d | ANRPC |
| Alternative: Myanmar–China pipeline | ~0.4 mb/d (limited capacity) | EIA |
| Alternative: Sunda/Lombok straits | Adds ~6,000 nm, ~10–14 days | Reuters shipping data |

## Validation status

- **China/Japan/Korea impact**: ✓ **Confirmed** — ANRPC and EIA data directly validate import dependencies
- **Severity magnitude**: ⚠ **Partial** — No historical Malacca closure to calibrate against; 75% is a reasoned estimate
- **Southeast Asia sign**: ✗ **Rejected** — Model predicts stock buildup; reality would be stock drawdown

## Running the scenario

```python
from interventions import malacca_disruption, compose_interventions
from geopolitical_model import GeopoliticalModel, load_parameters
from model_config import ModelConfig

params = load_parameters("real_params.json")
cfg = ModelConfig(trade_scale=1.0, k_half=50.0, initial_stock_days=90.0)

iv = malacca_disruption(onset_day=100.0, severity=0.75, ramp_days=14.0)
traj = GeopoliticalModel(params, cfg, interventions=[iv]).simulate(t_span=(0, 365))
```

For the compound effect with Hormuz, see [Multi-Chokepoint](multi_chokepoint.md).
