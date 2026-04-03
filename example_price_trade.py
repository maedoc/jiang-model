#!/usr/bin/env python3
"""
Price-Mediated Trade Extension
==============================

Compares three configurations:
  A) Fixed trade (default): bilateral flows from trade matrix, no price response
  B) Price-mediated trade enabled: flows driven by price differentials
  C) Price-mediated trade under Hormuz disruption

The price-mediated extension closes the economic loop: scarcity raises
prices, which attract imports, which reduce scarcity.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from model_config import ModelConfig
from geopolitical_model import GeopoliticalModel, load_parameters, REGION_NAMES
from interventions import hormuz_closure
from trajectory import TrajectoryComparison

T_SPAN = (0.0, 365.0)

# ── A. Fixed trade (baseline) ────────────────────────────────────────────
cfg_fixed = ModelConfig(trade_scale=1.0, k_half=50.0, initial_stock_days=90.0, price_trade_enabled=False)
model_a = GeopoliticalModel(load_parameters(), cfg_fixed)
traj_a = model_a.simulate(t_span=T_SPAN)

# ── B. Price-mediated trade ──────────────────────────────────────────────
cfg_price = ModelConfig(
    trade_scale=1.0,
    k_half=50.0,
    initial_stock_days=90.0,
    price_trade_enabled=True,
    price_trade_elasticity=0.5,
    price_trade_max_fraction=0.3,
    price_trade_transport_cost=0.1,
)
model_b = GeopoliticalModel(load_parameters(), cfg_price)
traj_b = model_b.simulate(t_span=T_SPAN)

# ── C. Price-mediated trade + Hormuz ─────────────────────────────────────
iv = hormuz_closure(onset_day=100.0, severity=0.8)
model_c = GeopoliticalModel(load_parameters(), cfg_price, interventions=[iv])
traj_c = model_c.simulate(t_span=T_SPAN)

# ── Comparisons ──────────────────────────────────────────────────────────
cmp_ab = TrajectoryComparison(traj_a, traj_b)  # fixed vs price-mediated
cmp_ac = TrajectoryComparison(traj_a, traj_c)  # fixed vs price-mediated+Hormuz

# ── Figure 1: Oil stock comparison for key importers ─────────────────────
IMPORTERS = [("Europe", 1), ("Japan", 6), ("China", 4), ("India", 5)]

fig, axes = plt.subplots(2, 2, figsize=(13, 9), sharex=True)
for idx, (rname, ri) in enumerate(IMPORTERS):
    ax = axes.ravel()[idx]
    ax.plot(traj_a.t, traj_a.oil_stock[ri], label="Fixed trade", lw=1.5)
    ax.plot(traj_b.t, traj_b.oil_stock[ri], "--", label="Price-mediated", lw=1.5)
    ax.plot(traj_c.t, traj_c.oil_stock[ri], ":", label="Price-med + Hormuz", lw=1.5)
    ax.axvline(100, color="red", ls=":", alpha=0.3)
    ax.set_title(rname)
    ax.set_ylabel("Oil stock")
    if idx == 0:
        ax.legend(fontsize=8)

fig.suptitle("Price-Mediated Trade: Oil Stock for Major Importers", fontsize=13)
fig.tight_layout()
fig.savefig("price_trade_oil.png", dpi=150, bbox_inches="tight")
print("Saved price_trade_oil.png")

# ── Figure 2: Oil price dynamics ─────────────────────────────────────────
fig2, axes2 = plt.subplots(2, 2, figsize=(13, 9), sharex=True)
for idx, (rname, ri) in enumerate(IMPORTERS):
    ax = axes2.ravel()[idx]
    ax.plot(traj_a.t, traj_a.oil_price[ri], label="Fixed trade", lw=1.5)
    ax.plot(traj_b.t, traj_b.oil_price[ri], "--", label="Price-mediated", lw=1.5)
    ax.plot(traj_c.t, traj_c.oil_price[ri], ":", label="Price-med + Hormuz", lw=1.5)
    ax.axvline(100, color="red", ls=":", alpha=0.3)
    ax.set_title(rname)
    ax.set_ylabel("Oil price (normalized)")
    if idx == 0:
        ax.legend(fontsize=8)

fig2.suptitle("Price-Mediated Trade: Oil Price Dynamics", fontsize=13)
fig2.tight_layout()
fig2.savefig("price_trade_prices.png", dpi=150, bbox_inches="tight")
print("Saved price_trade_prices.png")

# ── Figure 3: Stability comparison ───────────────────────────────────────
fig3, axes3 = plt.subplots(2, 2, figsize=(13, 9), sharex=True)
for idx, (rname, ri) in enumerate(IMPORTERS):
    ax = axes3.ravel()[idx]
    ax.plot(traj_a.t, traj_a.stability[ri], label="Fixed trade", lw=1.5)
    ax.plot(traj_b.t, traj_b.stability[ri], "--", label="Price-mediated", lw=1.5)
    ax.plot(traj_c.t, traj_c.stability[ri], ":", label="Price-med + Hormuz", lw=1.5)
    ax.axvline(100, color="red", ls=":", alpha=0.3)
    ax.set_title(rname)
    ax.set_ylabel("Stability")
    if idx == 0:
        ax.legend(fontsize=8)

fig3.suptitle("Price-Mediated Trade: Stability Impact", fontsize=13)
fig3.tight_layout()
fig3.savefig("price_trade_stability.png", dpi=150, bbox_inches="tight")
print("Saved price_trade_stability.png")

# ── Summary table ────────────────────────────────────────────────────────
print("\n=== Final-day oil stocks ===")
print(f"{'Region':<25} {'Fixed':>8} {'Price-med':>10} {'PM+Hormuz':>10}")
print("-" * 55)
for i, rn in enumerate(REGION_NAMES):
    print(f"{rn:<25} {traj_a.oil_stock[i,-1]:>8.1f} "
          f"{traj_b.oil_stock[i,-1]:>10.1f} {traj_c.oil_stock[i,-1]:>10.1f}")

print("\n=== Stability delta: price-mediated vs fixed trade ===")
print(f"{'Region':<25} {'Δ stability':>12}")
print("-" * 39)
for i, rn in enumerate(REGION_NAMES):
    d = traj_b.stability[i, -1] - traj_a.stability[i, -1]
    print(f"{rn:<25} {d:>+12.4f}")
