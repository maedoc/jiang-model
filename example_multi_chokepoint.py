#!/usr/bin/env python3
"""
Multi-Chokepoint Scenario (GT#21)
====================================

Game Theory #21 argues that the U.S. strategy is to control multiple global
chokepoints—Hormuz, Malacca, Panama, Gibraltar—to contain China and force
global dependency on North‑American resources.

This script simulates a simultaneous closure of Hormuz, Malacca and Panama
and compares the compound shock against a 365‑day baseline.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from model_config import ModelConfig
from geopolitical_model import GeopoliticalModel, load_parameters, REGION_NAMES
from interventions import hormuz_closure, malacca_disruption, panama_disruption, compose_interventions
from trajectory import TrajectoryComparison

# ── Configuration ──────────────────────────────────────────────────────────
T_SPAN = (0.0, 365.0)
CFG = ModelConfig(trade_scale=1.0, k_half=50.0, initial_stock_days=90.0)

params = load_parameters("real_params.json")

# ── Baseline ──────────────────────────────────────────────────────────────
model_base = GeopoliticalModel(params, CFG)
traj_base = model_base.simulate(t_span=T_SPAN)

# ── Compound chokepoint scenario ──────────────────────────────────────────
iv = compose_interventions([
    hormuz_closure(onset_day=100.0, severity=0.8, ramp_days=10.0),
    malacca_disruption(onset_day=100.0, severity=0.7, ramp_days=14.0),
    panama_disruption(onset_day=100.0, severity=0.6, ramp_days=14.0),
])
model_multi = GeopoliticalModel(load_parameters(), CFG, interventions=[iv])
traj_multi = model_multi.simulate(t_span=T_SPAN)

cmp = TrajectoryComparison(traj_base, traj_multi)

# ── Figure 1: Oil stock for key impacted regions ─────────────────────────
FOCUS = [
    ("China", 4), ("Japan", 6), ("India", 5), ("Europe", 1),
    ("Southeast Asia", 7), ("South America", 10),
]

fig, axes = plt.subplots(2, 3, figsize=(15, 9), sharex=True)
axes = axes.ravel()

for idx, (rname, ri) in enumerate(FOCUS):
    ax = axes[idx]
    ax.plot(traj_base.t, traj_base.oil_stock[ri], label="Baseline", lw=1.5)
    ax.plot(traj_multi.t, traj_multi.oil_stock[ri], "--", label="Multi-choke", lw=1.5)
    ax.axvline(100, color="red", ls=":", alpha=0.4)
    ax.set_title(rname)
    ax.set_ylabel("Oil stock")
    if idx == 0:
        ax.legend(fontsize=8)

fig.suptitle("Multi-Chokepoint Scenario: Hormuz + Malacca + Panama (Oil Stock)", fontsize=14)
fig.tight_layout()
fig.savefig("multi_chokepoint_oil.png", dpi=150, bbox_inches="tight")
print("Saved multi_chokepoint_oil.png")

# ── Figure 2: Price & Stability dashboard for China ─────────────────────
fig2, axes2 = plt.subplots(2, 3, figsize=(15, 9), sharex=True)
axes2 = axes2.ravel()

variables = [
    ("oil_price", "Oil Price"), ("fertilizer_price", "Fertilizer Price"),
    ("stability", "Stability"), ("inflation", "Inflation"),
    ("debt_gdp", "Debt / GDP"), ("military", "Military"),
]
ri = 4  # China
for idx, (vname, vlabel) in enumerate(variables):
    ax = axes2[idx]
    ax.plot(traj_base.t, traj_base.get(vname, ri), label="Baseline", lw=1.5)
    ax.plot(traj_multi.t, traj_multi.get(vname, ri), "--", label="Multi-choke", lw=1.5)
    ax.axvline(100, color="red", ls=":", alpha=0.4)
    ax.set_title(f"China: {vlabel}")

fig2.suptitle("Multi-Chokepoint Scenario: China Impact Dashboard", fontsize=14)
fig2.tight_layout()
fig2.savefig("multi_chokepoint_china.png", dpi=150, bbox_inches="tight")
print("Saved multi_chokepoint_china.png")

# ── Summary table ───────────────────────────────────────────────────────
print("\n=== Final-day comparison (day 365) ===")
print(f"{'Region':<25} {'Base Oil':>10} {'Multi Oil':>10} {'Δ':>10}")
print("-" * 57)
for i, rn in enumerate(REGION_NAMES):
    bo = traj_base.oil_stock[i, -1]
    ho = traj_multi.oil_stock[i, -1]
    print(f"{rn:<25} {bo:>10.2f} {ho:>10.2f} {ho - bo:>+10.2f}")

print("\n=== Stability impact (> 0.01) ===")
for i, rn in enumerate(REGION_NAMES):
    sb = traj_base.stability[i, -1]
    sm = traj_multi.stability[i, -1]
    if abs(sm - sb) > 0.01:
        print(f"  {rn:<25} Δ = {sm - sb:+.4f}")
