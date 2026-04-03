#!/usr/bin/env python3
"""
Sensitivity Analysis
====================

1. Trade-scale sweep: how does trade_scale affect average end-of-year
   stability and total oil stock?
2. Morris screening: rank the top structural coefficients by importance.
3. Regional parameter sweep: how does Middle East oil production affect
   global stability?

Generates sensitivity figures.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from model_config import ModelConfig
from sensitivity import parameter_sweep, morris_screening, regional_parameter_sweep

T_SPAN = (0.0, 90.0)  # 90-day horizon for speed

# ── 1. Trade-scale sweep ─────────────────────────────────────────────────
print("Running trade_scale sweep …")
ts_values = np.logspace(-3, 0.5, 15)  # 0.001 to ~3.16
vals_ts, stab_ts = parameter_sweep(
    "trade_scale", ts_values,
    t_span=T_SPAN, metric="avg_stability",
)
_, oil_ts = parameter_sweep(
    "trade_scale", ts_values,
    t_span=T_SPAN, metric="total_oil",
)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
ax1.semilogx(vals_ts, stab_ts, "o-", color="C0")
ax1.set_xlabel("trade_scale")
ax1.set_ylabel("Avg final stability")
ax1.set_title("Stability vs trade_scale")
ax1.grid(True, alpha=0.3)

ax2.semilogx(vals_ts, oil_ts, "o-", color="C1")
ax2.set_xlabel("trade_scale")
ax2.set_ylabel("Total final oil stock")
ax2.set_title("Oil stock vs trade_scale")
ax2.grid(True, alpha=0.3)

fig.suptitle("Trade Scale Sensitivity", fontsize=13)
fig.tight_layout()
fig.savefig("sensitivity_trade_scale.png", dpi=150, bbox_inches="tight")
print("Saved sensitivity_trade_scale.png")

# ── 2. Morris screening ─────────────────────────────────────────────────
print("Running Morris screening …")
PARAMS_TO_SCREEN = [
    "trade_scale",
    "baseline_production",
    "social_unrest_strength",
    "price_response",
    "tax_rate",
    "military_gdp_fraction",
]

morris = morris_screening(
    PARAMS_TO_SCREEN,
    n_trajectories=4,
    delta=0.15,
    t_span=T_SPAN,
    metric="avg_stability",
)

# Sort by mu_star
sorted_params = sorted(morris.items(), key=lambda x: -x[1]["mu_star"])

fig2, ax = plt.subplots(figsize=(10, 6))
names = [p for p, _ in sorted_params]
mu_stars = [v["mu_star"] for _, v in sorted_params]
sigmas = [v["sigma"] for _, v in sorted_params]

ax.barh(names[::-1], mu_stars[::-1], xerr=sigmas[::-1],
        color="steelblue", edgecolor="navy", alpha=0.8, capsize=3)
ax.set_xlabel("μ* (mean absolute elementary effect)")
ax.set_title("Morris Screening: Parameter Importance for Stability")
ax.grid(True, alpha=0.3, axis="x")

fig2.tight_layout()
fig2.savefig("sensitivity_morris.png", dpi=150, bbox_inches="tight")
print("Saved sensitivity_morris.png")

# Print table
print("\n=== Morris Screening Results ===")
print(f"{'Parameter':<30} {'μ':>8} {'μ*':>8} {'σ':>8}")
print("-" * 56)
for pname, vals in sorted_params:
    print(f"{pname:<30} {vals['mu']:>8.4f} {vals['mu_star']:>8.4f} {vals['sigma']:>8.4f}")

# ── 3. Regional parameter sweep: ME oil production ──────────────────────
print("\nRunning ME oil production sweep …")
multipliers = np.linspace(0.5, 1.5, 6)
mults, stab_me = regional_parameter_sweep(
    "oil_production", 3,  # Middle East
    multipliers,
    t_span=T_SPAN, metric="avg_stability",
)
_, min_stab_me = regional_parameter_sweep(
    "oil_production", 3,
    multipliers,
    t_span=T_SPAN, metric="min_stability",
)

fig3, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
ax1.plot(mults, stab_me, "o-", color="C2")
ax1.set_xlabel("ME oil production multiplier")
ax1.set_ylabel("Avg final stability")
ax1.set_title("Global avg stability vs ME oil production")
ax1.axvline(1.0, ls=":", color="gray", alpha=0.5)
ax1.grid(True, alpha=0.3)

ax2.plot(mults, min_stab_me, "o-", color="C3")
ax2.set_xlabel("ME oil production multiplier")
ax2.set_ylabel("Min final stability (worst region)")
ax2.set_title("Worst-case stability vs ME oil production")
ax2.axvline(1.0, ls=":", color="gray", alpha=0.5)
ax2.grid(True, alpha=0.3)

fig3.suptitle("Middle East Oil Production Sensitivity", fontsize=13)
fig3.tight_layout()
fig3.savefig("sensitivity_me_oil.png", dpi=150, bbox_inches="tight")
print("Saved sensitivity_me_oil.png")
