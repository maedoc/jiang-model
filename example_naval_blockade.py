#!/usr/bin/env python3
"""
Naval Blockade Scenario (GT#21)
==================================

Game Theory #21 describes U.S. boarding of commercial vessels and seizure
of tankers carrying energy bound for China.  This models the blockade as
bilateral sanctions cutting oil & fertilizer trade from the Middle East
(and optionally Russia) to China.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from model_config import ModelConfig
from geopolitical_model import GeopoliticalModel, load_parameters, REGION_NAMES
from interventions import (
    naval_blockade, bilateral_sanction, compose_interventions,
    MIDDLE_EAST, RUSSIA, CHINA,
)
from trajectory import TrajectoryComparison

# ── Configuration ──────────────────────────────────────────────────────────
T_SPAN = (0.0, 365.0)
CFG = ModelConfig(trade_scale=1.0, k_half=50.0, initial_stock_days=90.0)

params = load_parameters("real_params.json")

# ── Baseline ──────────────────────────────────────────────────────────────
model_base = GeopoliticalModel(params, CFG)
traj_base = model_base.simulate(t_span=T_SPAN)

# ── Scenario A: ME → China blockade ──────────────────────────────────────
iv_a = naval_blockade(sender=MIDDLE_EAST, receiver=CHINA,
                      onset_day=100.0, severity=0.9, ramp_days=10.0)
model_a = GeopoliticalModel(load_parameters(), CFG, interventions=[iv_a])
traj_a = model_a.simulate(t_span=T_SPAN)

# ── Scenario B: ME + Russia → China blockade ───────────────────────────────
iv_b1 = naval_blockade(sender=MIDDLE_EAST, receiver=CHINA,
                       onset_day=100.0, severity=0.9, ramp_days=10.0)
iv_b2 = bilateral_sanction("RU→CN oil", sender=RUSSIA, receiver=CHINA,
                           onset_day=100.0, severity=0.7, ramp_days=10.0,
                           resources=["oil_trade_flow", "fertilizer_trade_flow"])
iv_b = compose_interventions([iv_b1, iv_b2])
model_b = GeopoliticalModel(load_parameters(), CFG, interventions=[iv_b])
traj_b = model_b.simulate(t_span=T_SPAN)

# ── Comparisons ──────────────────────────────────────────────────────────
cmp_a = TrajectoryComparison(traj_base, traj_a)
cmp_b = TrajectoryComparison(traj_base, traj_b)

# ── Figure 1: China oil stock & price ────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharex=True)
ri = CHINA

axes[0].plot(traj_base.t, traj_base.oil_stock[ri], label="Baseline", lw=1.5)
axes[0].plot(traj_a.t, traj_a.oil_stock[ri], "--", label="ME blockade", lw=1.5)
axes[0].plot(traj_b.t, traj_b.oil_stock[ri], ":", label="ME+RU blockade", lw=1.5)
axes[0].axvline(100, color="red", ls=":", alpha=0.4)
axes[0].set_title("China Oil Stock")
axes[0].set_ylabel("Oil stock")
axes[0].legend()

axes[1].plot(traj_base.t, traj_base.oil_price[ri], label="Baseline", lw=1.5)
axes[1].plot(traj_a.t, traj_a.oil_price[ri], "--", label="ME blockade", lw=1.5)
axes[1].plot(traj_b.t, traj_b.oil_price[ri], ":", label="ME+RU blockade", lw=1.5)
axes[1].axvline(100, color="red", ls=":", alpha=0.4)
axes[1].set_title("China Oil Price")
axes[1].set_ylabel("Price")
axes[1].legend()

fig.suptitle("Naval Blockade: China Energy Impact", fontsize=14)
fig.tight_layout()
fig.savefig("naval_blockade_china.png", dpi=150, bbox_inches="tight")
print("Saved naval_blockade_china.png")

# ── Figure 2: Stability for Asia-Pacific ──────────────────────────────────
FOCUS = [("China", CHINA), ("Japan", 6), ("India", 5), ("Southeast Asia", 7)]

fig2, axes2 = plt.subplots(2, 2, figsize=(12, 9), sharex=True)
axes2 = axes2.ravel()

for idx, (rname, ri) in enumerate(FOCUS):
    ax = axes2[idx]
    ax.plot(traj_base.t, traj_base.stability[ri], label="Baseline", lw=1.5)
    ax.plot(traj_a.t, traj_a.stability[ri], "--", label="ME blockade", lw=1.5)
    ax.plot(traj_b.t, traj_b.stability[ri], ":", label="ME+RU blockade", lw=1.5)
    ax.axvline(100, color="red", ls=":", alpha=0.4)
    ax.set_title(f"{rname}: Stability")
    if idx == 0:
        ax.legend(fontsize=8)

fig2.suptitle("Naval Blockade: Regional Stability Impact", fontsize=14)
fig2.tight_layout()
fig2.savefig("naval_blockade_stability.png", dpi=150, bbox_inches="tight")
print("Saved naval_blockade_stability.png")

# ── Summary tables ────────────────────────────────────────────────────────
print("\n=== Final-day China metrics ===")
print(f"{'Scenario':<25} {'Oil':>10} {'Price':>10} {'Stability':>10}")
print("-" * 60)
for sname, traj in [("Baseline", traj_base), ("ME blockade", traj_a), ("ME+RU blockade", traj_b)]:
    print(f"{sname:<25} {traj.oil_stock[CHINA,-1]:>10.2f} "
          f"{traj.oil_price[CHINA,-1]:>10.2f} {traj.stability[CHINA,-1]:>10.4f}")

print("\n=== Oil stock delta vs baseline (day 365) ===")
for sname, cmp in [("ME blockade", cmp_a), ("ME+RU blockade", cmp_b)]:
    impacts = cmp.max_absolute_impact("oil_stock")
    print(f"\n{sname}:")
    for r, v in sorted(impacts.items(), key=lambda x: -x[1])[:6]:
        print(f"  {r:<25} max |Δ| = {v:>10.2f}")
