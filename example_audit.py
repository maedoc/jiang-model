#!/usr/bin/env python3
"""
Assumption & Interaction Term Audit
====================================

Systematically examines every interaction term and structural assumption
in the geopolitical ODE model.  Generates diagnostic figures showing how
each mechanism behaves and where sensitivities lie.

Run:  python example_audit.py
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from model_config import ModelConfig
from geopolitical_model import (
    GeopoliticalModel, load_parameters, REGION_NAMES,
    sigmoid, exp_transform, inv_logit, log_transform, logit_transform,
)

# ══════════════════════════════════════════════════════════════════════════
# 1. TRANSFORM BEHAVIOUR
# ══════════════════════════════════════════════════════════════════════════

fig, axes = plt.subplots(1, 3, figsize=(14, 4))

# Log transform: log(1+x) and its inverse
x = np.linspace(-0.5, 10, 300)
L = log_transform(np.maximum(x, 0))
axes[0].plot(x, L, lw=2)
axes[0].set_xlabel("Physical x")
axes[0].set_ylabel("log(1+x)")
axes[0].set_title("Log transform (positive variables)")
axes[0].axhline(0, color="gray", ls="--", alpha=0.3)
axes[0].grid(True, alpha=0.3)
axes[0].annotate("Floor at x=0", xy=(0, 0), fontsize=8, color="red")

# Logit transform
p = np.linspace(0.001, 0.999, 300)
L = logit_transform(p)
axes[1].plot(p, L, lw=2)
axes[1].set_xlabel("Physical p ∈ [0,1]")
axes[1].set_ylabel("logit(p)")
axes[1].set_title("Logit transform (stability, inequality)")
axes[1].grid(True, alpha=0.3)

# Jacobian factor: d(logit)/dp = 1/(p(1-p))
jac = 1.0 / (p * (1 - p))
axes[2].semilogy(p, jac, lw=2, color="C3")
axes[2].set_xlabel("p")
axes[2].set_ylabel("1 / p(1-p)")
axes[2].set_title("Logit Jacobian (amplification near boundaries)")
axes[2].grid(True, alpha=0.3)
axes[2].annotate("Stiff near 0 and 1", xy=(0.1, 100), fontsize=8, color="red")

fig.suptitle("1. Transform Behaviour", fontsize=13)
fig.tight_layout()
fig.savefig("audit_transforms.png", dpi=150, bbox_inches="tight")
print("Saved audit_transforms.png")

# ══════════════════════════════════════════════════════════════════════════
# 2. RESOURCE ABUNDANCE → STABILITY COUPLING
# ══════════════════════════════════════════════════════════════════════════

cfg = ModelConfig()
ratio = np.linspace(0, 2, 200)

fig2, axes2 = plt.subplots(1, 3, figsize=(14, 4))

for scale_val, label in [(1.0, "scale=1"), (3.0, "scale=3 (default)"), (10.0, "scale=10")]:
    ra = np.tanh(scale_val * ratio)
    axes2[0].plot(ratio, ra, label=label, lw=1.5)
axes2[0].set_xlabel("Resource ratio (current / initial)")
axes2[0].set_ylabel("resource_abundance")
axes2[0].set_title("A: tanh(scale × ratio)")
axes2[0].legend(fontsize=8)
axes2[0].grid(True, alpha=0.3)
axes2[0].axvline(1.0, ls=":", color="gray", alpha=0.5)

# Stability equilibrium: at steady state dS/dt = 0
# -decay*s + gain*ra*(1-s) = 0  →  s = gain*ra / (decay + gain*ra)
decay = 0.1  # typical
gain = 0.15  # typical
ra_vals = np.linspace(0.001, 1.0, 200)
s_eq = gain * ra_vals / (decay + gain * ra_vals)
axes2[1].plot(ra_vals, s_eq, lw=2, color="C2")
axes2[1].set_xlabel("resource_abundance")
axes2[1].set_ylabel("Equilibrium stability")
axes2[1].set_title("B: Stability equilibrium (no unrest)")
axes2[1].grid(True, alpha=0.3)
axes2[1].annotate(f"decay={decay}, gain={gain}", xy=(0.3, 0.3), fontsize=8)

# Full chain: resource ratio → abundance → stability
for scale_val in [1.0, 3.0, 10.0]:
    ra = np.tanh(scale_val * ratio)
    s_eq_full = gain * ra / (decay + gain * ra)
    axes2[2].plot(ratio, s_eq_full, label=f"scale={scale_val}", lw=1.5)
axes2[2].set_xlabel("Resource ratio (current / initial)")
axes2[2].set_ylabel("Equilibrium stability")
axes2[2].set_title("C: Full chain — resource ratio → stability")
axes2[2].legend(fontsize=8)
axes2[2].grid(True, alpha=0.3)
axes2[2].axvline(1.0, ls=":", color="gray", alpha=0.5)

fig2.suptitle("2. Resource → Stability Coupling", fontsize=13)
fig2.tight_layout()
fig2.savefig("audit_resource_stability.png", dpi=150, bbox_inches="tight")
print("Saved audit_resource_stability.png")

# ══════════════════════════════════════════════════════════════════════════
# 3. CRISIS THRESHOLD SHAPES
# ══════════════════════════════════════════════════════════════════════════

fig3, axes3 = plt.subplots(2, 2, figsize=(11, 9))

# Debt crisis
d = np.linspace(0, 3, 200)
for k in [5, 10, 20]:
    axes3[0, 0].plot(d, sigmoid(d - 1.0, k=k), label=f"k={k}", lw=1.5)
axes3[0, 0].set_xlabel("Debt / GDP")
axes3[0, 0].set_title("Debt crisis threshold")
axes3[0, 0].legend(fontsize=8)
axes3[0, 0].axvline(1.0, ls=":", color="red", alpha=0.4)
axes3[0, 0].grid(True, alpha=0.3)

# Social unrest (product of two sigmoids)
ineq = np.linspace(0, 1, 100)
infl = np.linspace(-0.1, 0.5, 100)
INEQ, INFL = np.meshgrid(ineq, infl)
UNREST = sigmoid(INEQ - 0.6, k=10) * sigmoid(INFL - 0.1, k=20)
c = axes3[0, 1].contourf(INEQ, INFL, UNREST, levels=20, cmap="Reds")
plt.colorbar(c, ax=axes3[0, 1])
axes3[0, 1].set_xlabel("Inequality")
axes3[0, 1].set_ylabel("Inflation")
axes3[0, 1].set_title("Social unrest (product of sigmoids)")
axes3[0, 1].axvline(0.6, ls=":", color="white", alpha=0.7)
axes3[0, 1].axhline(0.1, ls=":", color="white", alpha=0.7)

# Currency crisis: depreciation-based
dep = np.linspace(-0.1, 0.5, 200)
for k in [10, 20, 40]:
    axes3[1, 0].plot(dep, sigmoid(dep - 0.2, k=k), label=f"k={k}", lw=1.5)
axes3[1, 0].set_xlabel("30-day depreciation")
axes3[1, 0].set_title("Currency crisis threshold")
axes3[1, 0].legend(fontsize=8)
axes3[1, 0].axvline(0.2, ls=":", color="red", alpha=0.4)
axes3[1, 0].grid(True, alpha=0.3)

# Austerity factor
d = np.linspace(0, 4, 200)
for sharp in [5, 10, 20]:
    aust = 1.0 / (1.0 + np.exp(sharp * (d - 2.0)))
    axes3[1, 1].plot(d, aust, label=f"sharpness={sharp}", lw=1.5)
axes3[1, 1].set_xlabel("Debt / GDP")
axes3[1, 1].set_title("Austerity factor (spending reduction)")
axes3[1, 1].legend(fontsize=8)
axes3[1, 1].axvline(2.0, ls=":", color="red", alpha=0.4)
axes3[1, 1].grid(True, alpha=0.3)

fig3.suptitle("3. Nonlinear Crisis Thresholds", fontsize=13)
fig3.tight_layout()
fig3.savefig("audit_thresholds.png", dpi=150, bbox_inches="tight")
print("Saved audit_thresholds.png")

# ══════════════════════════════════════════════════════════════════════════
# 4. TRADE FLOW LIMITATION (MONOD)
# ══════════════════════════════════════════════════════════════════════════

fig4, (ax4a, ax4b) = plt.subplots(1, 2, figsize=(12, 4.5))

stock = np.linspace(0, 5000, 300)
for kh in [10, 50, 100, 500, 1000]:
    ax4a.plot(stock, stock / (stock + kh), label=f"K_half={kh}", lw=1.5)
ax4a.set_xlabel("Exporter stock")
ax4a.set_ylabel("Fraction available for trade")
ax4a.set_title("Monod half-saturation: stock/(stock + K_half)")
ax4a.legend(fontsize=8)
ax4a.grid(True, alpha=0.3)

# Show baseline vs example trade parameters
params = load_parameters()
oil_stocks_init = np.maximum(params["oil_production"], params["oil_consumption"]) * 90
for kh, lstyle in [(1000, "--"), (50, "-")]:
    fracs = oil_stocks_init / (oil_stocks_init + kh)
    ax4b.barh(range(12), fracs, alpha=0.5, label=f"K_half={kh}")
ax4b.set_yticks(range(12))
ax4b.set_yticklabels([rn[:12] for rn in REGION_NAMES], fontsize=8)
ax4b.set_xlabel("Trade availability fraction at t=0")
ax4b.set_title("Per-region trade fractions (90-day initial stocks)")
ax4b.legend(fontsize=8)
ax4b.grid(True, alpha=0.3, axis="x")

fig4.suptitle("4. Trade Flow Limitation", fontsize=13)
fig4.tight_layout()
fig4.savefig("audit_trade_monod.png", dpi=150, bbox_inches="tight")
print("Saved audit_trade_monod.png")

# ══════════════════════════════════════════════════════════════════════════
# 5. GDP PROXY ASSUMPTIONS
# ══════════════════════════════════════════════════════════════════════════

fig5, (ax5a, ax5b) = plt.subplots(1, 2, figsize=(12, 5))

# GDP = (oil_prod + fert_prod) × stability
# This only captures resource-based GDP — no services, manufacturing
gdp_raw = (params["oil_production"] + params["fertilizer_production"]) * 0.7  # stability=0.7
ax5a.barh(range(12), gdp_raw, color="steelblue")
ax5a.set_yticks(range(12))
ax5a.set_yticklabels([rn[:12] for rn in REGION_NAMES], fontsize=8)
ax5a.set_xlabel("GDP proxy (oil_prod + fert_prod) × stability")
ax5a.set_title("GDP proxy varies wildly — dominated by resource production")
ax5a.grid(True, alpha=0.3, axis="x")

# Implication: Japan, Europe have very low GDP proxy despite being
# large economies in reality
# Ratio of Japan GDP proxy to Middle East GDP proxy
jp_gdp = (params["oil_production"][6] + params["fertilizer_production"][6]) * 0.7
me_gdp = (params["oil_production"][3] + params["fertilizer_production"][3]) * 0.7
eu_gdp = (params["oil_production"][1] + params["fertilizer_production"][1]) * 0.7

txt = (
    f"Japan GDP proxy:  {jp_gdp:.1f}\n"
    f"Europe GDP proxy: {eu_gdp:.1f}\n"
    f"Middle East GDP:  {me_gdp:.1f}\n\n"
    "Resource-based GDP proxy makes\n"
    "resource-poor economies (Japan,\n"
    "Europe) appear weak.\n\n"
    "Fix: use gdp_scale_factors in\n"
    "real_params.json to normalize\n"
    "to real GDP proportions."
)
ax5b.text(0.1, 0.5, txt, transform=ax5b.transAxes, fontsize=10,
          verticalalignment="center", fontfamily="monospace",
          bbox=dict(boxstyle="round", facecolor="lightyellow"))
ax5b.set_title("GDP Proxy Critique")
ax5b.axis("off")

fig5.suptitle("5. GDP Proxy Assumptions", fontsize=13)
fig5.tight_layout()
fig5.savefig("audit_gdp_proxy.png", dpi=150, bbox_inches="tight")
print("Saved audit_gdp_proxy.png")

# ══════════════════════════════════════════════════════════════════════════
# 6. INTERACTION TERM MATRIX — WHICH VARIABLES AFFECT WHICH?
# ══════════════════════════════════════════════════════════════════════════

# Build adjacency matrix of causal influences
var_labels = [
    "Oil stock", "Fert stock", "Stability", "Water stock",
    "Military", "Inequality", "Debt", "Oil price",
    "Fert price", "Water price", "Inflation", "Interest rate",
    "Exchange", "Bond yield", "Exch avg",
]

# Interaction matrix: rows = affected, cols = source
# Strength: 0=none, 1=weak, 2=moderate, 3=strong
interactions = np.zeros((15, 15))

# Oil stock ← stability (production), trade matrices (inter-region)
interactions[0, 2] = 2  # stability → oil prod
# Fert stock ← stability
interactions[1, 2] = 2
# Stability ← oil+fert+water (resource abundance), inequality+inflation (unrest)
interactions[2, 0] = 3  # oil → stability
interactions[2, 1] = 2  # fert → stability
interactions[2, 3] = 2  # water → stability
interactions[2, 5] = 2  # inequality → unrest → stability
interactions[2, 10] = 2  # inflation → unrest → stability
# Water ← stability
interactions[3, 2] = 2
# Military ← GDP (which depends on oil+fert prod, stability), debt crisis
interactions[4, 2] = 2
interactions[4, 6] = 2  # debt crisis suppresses military
# Inequality ← stability (instability grows it), debt
interactions[5, 2] = 2
interactions[5, 6] = 1
# Debt ← military (→gov spending), stability (→tax revenue), interest rate, debt itself
interactions[6, 4] = 2  # military → gov spending → debt
interactions[6, 2] = 3  # stability → tax revenue
interactions[6, 11] = 2  # interest rate → debt servicing
interactions[6, 6] = 2  # debt self-reinforcing
# Oil price ← production, consumption (balance)
interactions[7, 0] = 1  # indirectly via market
# Fert price
interactions[8, 1] = 1
# Water price ← water scarcity
interactions[9, 3] = 2
# Inflation ← all price derivatives
interactions[10, 7] = 3  # oil price → inflation
interactions[10, 8] = 2  # fert price → inflation
interactions[10, 9] = 2  # water price → inflation
# Interest rate ← inflation (Taylor rule), debt (risk premium, debt gap)
interactions[11, 10] = 3  # inflation → interest
interactions[11, 6] = 2   # debt → interest
# Exchange rate ← trade balance, interest (capital flow), currency crisis
interactions[12, 11] = 1  # inter-region interest coupling
interactions[12, 12] = 1  # exchange avg coupling
# Bond yield ← interest rate, debt crisis
interactions[13, 11] = 3
interactions[13, 6] = 1
# Exchange avg ← exchange rate
interactions[14, 12] = 3

fig6, ax6 = plt.subplots(figsize=(10, 9))
im = ax6.imshow(interactions, cmap="YlOrRd", aspect="auto", vmin=0, vmax=3)
ax6.set_xticks(range(15))
ax6.set_xticklabels(var_labels, rotation=60, ha="right", fontsize=8)
ax6.set_yticks(range(15))
ax6.set_yticklabels(var_labels, fontsize=8)
ax6.set_xlabel("Source variable")
ax6.set_ylabel("Affected variable")
ax6.set_title("Causal Interaction Strength (0=none, 3=strong)")
plt.colorbar(im, ax=ax6, shrink=0.7)

# Add text annotations
for i in range(15):
    for j in range(15):
        if interactions[i, j] > 0:
            ax6.text(j, i, f"{interactions[i,j]:.0f}", ha="center", va="center",
                     fontsize=7, color="white" if interactions[i, j] > 1.5 else "black")

fig6.tight_layout()
fig6.savefig("audit_interaction_matrix.png", dpi=150, bbox_inches="tight")
print("Saved audit_interaction_matrix.png")

# ══════════════════════════════════════════════════════════════════════════
# 7. FEEDBACK LOOP IDENTIFICATION
# ══════════════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("ASSUMPTION AND INTERACTION TERM AUDIT")
print("="*70)

print("""
╔══════════════════════════════════════════════════════════════════════╗
║  FEEDBACK LOOPS IDENTIFIED IN THE MODEL                             ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  1. RESOURCE-STABILITY LOOP (positive feedback)                      ║
║     Low stability → low production → resource depletion →            ║
║     low abundance → lower stability                                  ║
║     STRENGTH: Moderate — dampened by tanh saturation and             ║
║               stability mean-reversion                              ║
║                                                                      ║
║  2. DEBT SPIRAL (positive feedback)                                  ║
║     High debt → interest burden → more debt → debt crisis →          ║
║     risk premium → higher interest → even more debt                  ║
║     STRENGTH: Strong but bounded by austerity sigmoid at            ║
║               debt_ceiling=2.0 and mean_reversion=0.1              ║
║                                                                      ║
║  3. INFLATION-UNREST LOOP (positive feedback)                        ║
║     Price shocks → inflation → social unrest → lower stability →    ║
║     lower production → supply shortfall → higher prices              ║
║     STRENGTH: Weak — requires inequality>0.6 AND inflation>0.1     ║
║               (product of sigmoid gates)                            ║
║                                                                      ║
║  4. TRADE-DEPLETION LOOP (negative feedback / stabilising)           ║
║     Exporter depletion → Monod limit reduces outflow →               ║
║     exporter stock recovers                                          ║
║     STRENGTH: Strong — Monod K_half is key parameter                ║
║                                                                      ║
║  5. PRICE-TRADE LOOP (when enabled — negative feedback)              ║
║     Scarcity → price rise → attracts imports → scarcity reduced     ║
║     STRENGTH: Depends on price_trade_elasticity                     ║
║                                                                      ║
║  6. STABILITY DIFFUSION (context-dependent)                          ║
║     Neighbour instability → diffusive coupling → pulls your          ║
║     stability toward neighbours                                      ║
║     STRENGTH: Weak — coupling scaled by s(1-s) which peaks at 0.25 ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║  KEY ASSUMPTIONS                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  A1. GDP proxy = (oil_prod + fert_prod) × stability                 ║
║      PROBLEM: Services and manufacturing are ~70% of GDP for        ║
║      developed economies. Japan/Europe appear weaker than they are. ║
║      FIX: Use gdp_scale_factors in real_params.json                 ║
║                                                                      ║
║  A2. Consumption is constant (not demand-responsive)                 ║
║      PROBLEM: In reality, high prices reduce demand.                ║
║      FIX: Could add price-elastic consumption:                      ║
║           cons_eff = cons_base / (1 + α × (price - 1))             ║
║                                                                      ║
║  A3. No resource substitution (oil ↔ gas ↔ renewable)               ║
║      PROBLEM: Energy transitions and fuel switching are major        ║
║      adaptation mechanisms.                                          ║
║      FIX: Add substitution elasticity in production term            ║
║                                                                      ║
║  A4. Bilateral trade matrix is fixed (except for interventions)      ║
║      PROBLEM: Trade rerouting after sanctions is a major response.  ║
║      FIX: Price-mediated trade extension partially addresses this   ║
║                                                                      ║
║  A5. No explicit population or demographic effects                   ║
║      PROBLEM: Per-capita resource availability matters more than     ║
║      absolute levels for unrest thresholds.                          ║
║                                                                      ║
║  A6. Taylor rule for interest rate is symmetric                      ║
║      PROBLEM: Central banks are asymmetric — faster to raise rates  ║
║      than to cut (zero lower bound, credibility concerns).          ║
║      FIX: Could add asymmetric Taylor coefficients                  ║
║                                                                      ║
║  A7. Water is treated like a commodity with global trade             ║
║      PROBLEM: Water is mostly local — international trade is tiny.  ║
║      FIX: Reduce water trade matrix entries dramatically or zero    ║
║      them out; keep only desalination/pipeline flows.               ║
║                                                                      ║
║  A8. Military expenditure has no deterrence/conflict feedback        ║
║      PROBLEM: Military buildup affects neighbours' security          ║
║      perceptions and trade disruption probability.                   ║
║      FIX: Could add arms race coupling: dM_i ∝ Σ_j (M_j - M_i)   ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║  WEAKEST INTERACTION TERMS (candidates for simplification)           ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  W1. inequality_debt_rate = 0.005  (debt → inequality)              ║
║      Very weak coupling. Debt doesn't visibly affect inequality.    ║
║                                                                      ║
║  W2. capital_flow_fx_scale = 0.001 (inter-region FX coupling)       ║
║      Financial contagion through exchange rates is negligible.      ║
║                                                                      ║
║  W3. interest_coupling_scale = 0.01 (inter-region rate coupling)    ║
║      Interest rate spillovers are very small.                       ║
║                                                                      ║
║  W4. trade_balance_fx_sensitivity = 0.001                           ║
║      Trade balance barely moves exchange rates.                      ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║  STRONGEST INTERACTION TERMS (main drivers of dynamics)              ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  S1. trade_scale × trade_matrix  — resource redistribution          ║
║  S2. stability_gain × resource_abundance — stability attractor      ║
║  S3. taylor_inflation_coeff = 1.5 — inflation→interest response    ║
║  S4. debt_mean_reversion = 0.1 — debt stabilisation                ║
║  S5. price_reversion = 0.05 — price equilibrium pull                ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
""")

# ══════════════════════════════════════════════════════════════════════════
# 8. PARAMETER REGIME MAP
# ══════════════════════════════════════════════════════════════════════════

# Show how the default parameters sit relative to threshold values
print("=== Parameter Regime Map ===")
print(f"{'Parameter':<35} {'Default':>10} {'Threshold':>10} {'Gap':>8}")
print("-" * 65)

cfg = ModelConfig()
p = load_parameters()
checks = [
    ("debt_crisis_threshold", cfg.debt_crisis_threshold,
     float(p["debt_to_gdp"].max()), "max initial debt"),
    ("unrest_inequality_threshold", cfg.unrest_inequality_threshold,
     float(p["inequality"].max()), "max initial ineq"),
    ("unrest_inflation_threshold", cfg.unrest_inflation_threshold,
     float(p["inflation"].max()), "max initial infl"),
    ("austerity debt_ceiling", cfg.debt_ceiling,
     float(p["debt_to_gdp"].max()), "max initial debt"),
]

for name, threshold, initial, desc in checks:
    gap = threshold - initial
    marker = "✓ safe" if gap > 0.1 else "⚠ near" if gap > 0 else "✗ exceeded"
    print(f"  {name:<33} {threshold:>10.3f} {initial:>10.3f} {gap:>+8.3f}  {marker}")

print("\n=== Regional Production-Consumption Balance (Mtoe/day) ===")
print(f"{'Region':<25} {'OilProd':>8} {'OilCons':>8} {'Balance':>8} {'Status'}")
print("-" * 60)
for i, rn in enumerate(REGION_NAMES):
    op = p["oil_production"][i]
    oc = p["oil_consumption"][i]
    bal = op - oc
    status = "EXPORTER" if bal > 0 else "IMPORTER"
    print(f"  {rn:<23} {op:>8.2f} {oc:>8.2f} {bal:>+8.2f}  {status}")

print("\nDone. See audit_*.png figures for visual analysis.")
