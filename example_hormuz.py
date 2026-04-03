#!/usr/bin/env python3
"""
Hormuz Strait Closure: Baseline vs Disruption
==============================================

Simulates a 365-day baseline and overlays an 80% disruption of Middle East
exports starting on day 100.  Produces a multi-panel comparison figure.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from model_config import ModelConfig
from geopolitical_model import GeopoliticalModel, load_parameters, REGION_NAMES
from interventions import hormuz_closure
from trajectory import TrajectoryComparison

# ── Configuration ──────────────────────────────────────────────────────────
T_SPAN = (0.0, 365.0)
# trade_scale=1.0 puts bilateral flows at their estimated real-world values.
# k_half=50 makes the Monod limit bite only when stocks are very low.
# initial_stock_days=90 gives 90-day reserves (roughly real-world strategic+commercial).
CFG = ModelConfig(trade_scale=1.0, k_half=50.0, initial_stock_days=90.0)

# ── Run baseline ──────────────────────────────────────────────────────────
params = load_parameters("real_params.json")
model_base = GeopoliticalModel(params, CFG)
traj_base = model_base.simulate(t_span=T_SPAN)

# ── Run Hormuz scenario ──────────────────────────────────────────────────
iv = hormuz_closure(onset_day=100.0, severity=0.8, ramp_days=10.0)
model_hormuz = GeopoliticalModel(load_parameters(), CFG, interventions=[iv])
traj_hormuz = model_hormuz.simulate(t_span=T_SPAN)

# ── Comparison ────────────────────────────────────────────────────────────
cmp = TrajectoryComparison(traj_base, traj_hormuz, n_points=300)

# Which regions to highlight
FOCUS = [
    ("Europe", 1),
    ("Middle East", 3),
    ("China", 4),
    ("India", 5),
    ("Japan", 6),
]

# ── Figure 1: Oil stock trajectories ─────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(15, 9), sharex=True)
axes = axes.ravel()

for idx, (rname, ri) in enumerate(FOCUS):
    ax = axes[idx]
    ax.plot(traj_base.t, traj_base.oil_stock[ri], label="Baseline", lw=1.5)
    ax.plot(traj_hormuz.t, traj_hormuz.oil_stock[ri], "--", label="Hormuz", lw=1.5)
    ax.axvline(100, color="red", ls=":", alpha=0.5, label="Onset" if idx == 0 else None)
    ax.set_title(rname)
    ax.set_ylabel("Oil stock")
    if idx == 0:
        ax.legend(fontsize=8)

# Summary panel
ax = axes[-1]
impacts = cmp.max_absolute_impact("oil_stock")
regions_sorted = sorted(impacts.items(), key=lambda x: -x[1])[:6]
ax.barh([r for r, _ in regions_sorted], [v for _, v in regions_sorted], color="salmon")
ax.set_xlabel("Max |Δ oil stock|")
ax.set_title("Impact ranking")

fig.suptitle("Hormuz Strait Closure: Oil Stock Impact", fontsize=14)
fig.tight_layout()
fig.savefig("hormuz_oil_stock.png", dpi=150, bbox_inches="tight")
print(f"Saved hormuz_oil_stock.png")

# ── Figure 2: Multi-variable dashboard ────────────────────────────────────
variables = [
    ("oil_stock", "Oil Stock"),
    ("stability", "Stability"),
    ("oil_price", "Oil Price"),
    ("debt_gdp", "Debt / GDP"),
    ("inflation", "Inflation"),
    ("interest_rate", "Interest Rate"),
]

fig2, axes2 = plt.subplots(2, 3, figsize=(15, 9), sharex=True)
axes2 = axes2.ravel()

# Show Europe (heavy ME importer) baseline vs disruption
ri = 1  # Europe
for idx, (vname, vlabel) in enumerate(variables):
    ax = axes2[idx]
    base_data = traj_base.get(vname, ri)
    alt_data = traj_hormuz.get(vname, ri)
    ax.plot(traj_base.t, base_data, label="Baseline", lw=1.5)
    ax.plot(traj_hormuz.t, alt_data, "--", label="Hormuz", lw=1.5)
    ax.axvline(100, color="red", ls=":", alpha=0.4)
    ax.set_title(f"Europe: {vlabel}")
    if idx == 0:
        ax.legend(fontsize=8)

fig2.suptitle("Hormuz Closure: Europe Multi-Variable Impact", fontsize=14)
fig2.tight_layout()
fig2.savefig("hormuz_europe_dashboard.png", dpi=150, bbox_inches="tight")
print(f"Saved hormuz_europe_dashboard.png")

# ── Summary table ─────────────────────────────────────────────────────────
print("\n=== Final-day comparison (day 365) ===")
print(f"{'Region':<25} {'Base Oil':>10} {'Hormuz Oil':>10} {'Δ':>10}")
print("-" * 57)
for i, rn in enumerate(REGION_NAMES):
    bo = traj_base.oil_stock[i, -1]
    ho = traj_hormuz.oil_stock[i, -1]
    print(f"{rn:<25} {bo:>10.2f} {ho:>10.2f} {ho - bo:>+10.2f}")
