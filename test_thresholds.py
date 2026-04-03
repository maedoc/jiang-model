#!/usr/bin/env python3
"""
Test nonlinear thresholds with artificial shocks.
"""

import numpy as np
from ode_model_extended import load_parameters, ExtendedODEModel


def test_shock():
    # Load base parameters
    params = load_parameters("real_params.json")
    model = ExtendedODEModel(params)

    # Run simulation with Hormuz disruption at day 50 (earlier)
    # Override disruption day by subclassing? We'll just modify model method temporarily
    original_disruption = model.compute_hormuz_disruption
    model.compute_hormuz_disruption = lambda t: original_disruption(
        t, disruption_day=50.0
    )

    print("Running 200-day simulation with Hormuz disruption at day 50...")
    sol = model.simulate(t_span=(0.0, 200.0), method="BDF", rtol=1e-6, atol=1e-8)
    print(f"Simulation completed: {sol.t.size} time points")

    # Extract final state
    n = model.n_regions
    y_final = sol.y[:, -1]
    (
        log_oil,
        log_fert,
        stability,
        log_water,
        log_military,
        logit_inequality,
        log_debt,
        log_price_oil,
        log_price_fert,
        log_price_water,
        inflation,
        interest,
        log_exchange,
        bond_yield,
        log_exchange_avg,
    ) = model.extract_state(y_final)

    # Convert to original units
    from ode_model_extended import exp_transform, inv_logit

    oil = exp_transform(log_oil)
    fert = exp_transform(log_fert)
    water = exp_transform(log_water)
    military = exp_transform(log_military)
    inequality = inv_logit(logit_inequality)
    debt = exp_transform(log_debt)
    price_oil = exp_transform(log_price_oil)
    price_fert = exp_transform(log_price_fert)
    price_water = exp_transform(log_price_water)
    exchange = exp_transform(log_exchange)
    exchange_avg = exp_transform(log_exchange_avg)

    # Compute threshold indicators
    debt_crisis = debt > 1.0
    depreciation = (exchange_avg - exchange) / (exchange_avg + 1e-8)
    currency_crisis = depreciation > 0.2
    social_unrest = (inequality > 0.6) & (inflation > 0.1)
    water_scarcity = water < (params["water_availability"] * 10.0 * 0.1)

    print("\n=== Threshold Activation Summary ===")
    print("Region".ljust(25) + "DebtCrisis CurrencyCrisis SocialUnrest WaterScarcity")
    for i in range(n):
        print(
            f"{model.region_name(i)[:25]:25} {debt_crisis[i]:11} {currency_crisis[i]:13} {social_unrest[i]:11} {water_scarcity[i]:12}"
        )

    # Print maximum values
    print("\n=== Maximum Values ===")
    print(f"Max debt/GDP: {debt.max():.3f}")
    print(f"Max inflation: {inflation.max():.3f}")
    print(f"Max inequality: {inequality.max():.3f}")
    print(f"Min water stock: {water.min():.3f}")

    # Check if any threshold triggered
    if debt_crisis.any():
        print("\nDebt crisis triggered in at least one region.")
    if currency_crisis.any():
        print("Currency crisis triggered in at least one region.")
    if social_unrest.any():
        print("Social unrest triggered in at least one region.")
    if water_scarcity.any():
        print("Water scarcity triggered in at least one region.")

    return sol


if __name__ == "__main__":
    test_shock()
