#!/usr/bin/env python3
"""
Sanctions Scenarios
===================

1. Russia oil embargo: 90% cut to all Russian oil exports (day 0, 30-day ramp)
2. EU–Russia bilateral sanction: complete oil + fert trade cut
3. Compound scenario: embargo + EU bilateral sanction

Compares each against a 365-day baseline and generates comparison figures.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from model_config import ModelConfig
from geopolitical_model import GeopoliticalModel, load_parameters, REGION_NAMES
from interventions import (
    russia_oil_embargo, bilateral_sanction, compose_interventions,
    RUSSIA, EUROPE,
)
from trajectory import TrajectoryComparison

# ── Configuration ──────────────────────────────────────────────────────────
T_SPAN = (0.0, 365.0)
CFG = ModelConfig(trade_scale=1.0, k_half=50.0, initial_stock_days=90.0)

params = load_parameters("real_params.json")

# ── Baseline ──────────────────────────────────────────────────────────────
model_base = GeopoliticalModel(params, CFG)
traj_base = model_base.simulate(t_span=T_SPAN)

# ── Scenario A: Russia oil embargo ───────────────────────────────────────
iv_a = russia_oil_embargo(onset_day=0.0, severity=0.9, ramp_days=30.0)
model_a = GeopoliticalModel(load_parameters(), CFG, interventions=[iv_a])
traj_a = model_a.simulate(t_span=T_SPAN)

# ── Scenario B: EU–Russia bilateral sanction (oil + fert) ────────────────
iv_b = bilateral_sanction(
    "EU-Russia bilateral",
    sender=RUSSIA, receiver=EUROPE,
    severity=1.0, ramp_days=10.0,
)
model_b = GeopoliticalModel(load_parameters(), CFG, interventions=[iv_b])
traj_b = model_b.simulate(t_span=T_SPAN)

# ── Scenario C: both combined ────────────────────────────────────────────
iv_c = compose_interventions([iv_a, iv_b])
model_c = GeopoliticalModel(load_parameters(), CFG, interventions=[iv_c])
traj_c = model_c.simulate(t_span=T_SPAN)

# ── Comparisons ──────────────────────────────────────────────────────────
cmp_a = TrajectoryComparison(traj_base, traj_a)
cmp_b = TrajectoryComparison(traj_base, traj_b)
cmp_c = TrajectoryComparison(traj_base, traj_c)

# ── Figure: side-by-side variable panels for Europe & Russia ─────────────
fig, axes = plt.subplots(3, 4, figsize=(18, 12), sharex=True)

scenarios = [
    ("Russia embargo", traj_a),
    ("EU-Russia bilateral", traj_b),
    ("Combined", traj_c),
]

variables = [
    ("oil_stock", "Oil Stock"),
    ("stability", "Stability"),
    ("oil_price", "Oil Price"),
    ("debt_gdp", "Debt / GDP"),
]

for row, (sname, traj) in enumerate(scenarios):
    for col, (vname, vlabel) in enumerate(variables):
        ax = axes[row, col]

        # Europe
        ax.plot(traj_base.t, traj_base.get(vname, EUROPE),
                color="C0", lw=1.2, label="EU base" if row == 0 else None)
        ax.plot(traj.t, traj.get(vname, EUROPE),
                "--", color="C0", lw=1.2, label="EU scenario" if row == 0 else None)

        # Russia
        ax.plot(traj_base.t, traj_base.get(vname, RUSSIA),
                color="C3", lw=1.2, label="RU base" if row == 0 else None)
        ax.plot(traj.t, traj.get(vname, RUSSIA),
                "--", color="C3", lw=1.2, label="RU scenario" if row == 0 else None)

        if row == 0:
            ax.set_title(vlabel)
            if col == 0:
                ax.legend(fontsize=7, loc="best")
        if col == 0:
            ax.set_ylabel(sname, fontsize=10)

fig.suptitle("Sanction Scenarios: Europe vs Russia", fontsize=14)
fig.tight_layout()
fig.savefig("sanctions_comparison.png", dpi=150, bbox_inches="tight")
print("Saved sanctions_comparison.png")

# ── Impact ranking bar chart ─────────────────────────────────────────────
fig2, axes2 = plt.subplots(1, 3, figsize=(16, 5), sharey=True)

for idx, (sname, cmp) in enumerate([
    ("Russia embargo", cmp_a),
    ("EU-Russia bilateral", cmp_b),
    ("Combined", cmp_c),
]):
    ax = axes2[idx]
    impacts = cmp.max_absolute_impact("oil_stock")
    sorted_r = sorted(impacts.items(), key=lambda x: -x[1])[:8]
    ax.barh([r for r, _ in sorted_r], [v for _, v in sorted_r], color="steelblue")
    ax.set_xlabel("Max |Δ oil stock|")
    ax.set_title(sname)

fig2.suptitle("Oil Stock Impact Ranking by Scenario", fontsize=13)
fig2.tight_layout()
fig2.savefig("sanctions_impact_ranking.png", dpi=150, bbox_inches="tight")
print("Saved sanctions_impact_ranking.png")

# ── Summary tables ───────────────────────────────────────────────────────
for sname, traj in scenarios:
    print(f"\n=== {sname}: Final-day stability ===")
    for i, rn in enumerate(REGION_NAMES):
        sb = traj_base.stability[i, -1]
        sa = traj.stability[i, -1]
        print(f"  {rn:<25} base={sb:.3f}  scenario={sa:.3f}  Δ={sa-sb:+.4f}")
