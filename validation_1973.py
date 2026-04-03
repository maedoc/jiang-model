#!/usr/bin/env python3
"""
Validation simulation for 1973 oil crisis scenario using calibrated parameters.
"""

import numpy as np
from ode_model_extended import load_parameters, ExtendedODEModel


def run_validation():
    # Load calibrated parameters for 1973
    try:
        params = load_parameters("params_1973.json")
        print("Loaded calibrated parameters for 1973 oil crisis.")
    except FileNotFoundError:
        print("params_1973.json not found, falling back to base parameters.")
        params = load_parameters("real_params.json")

    model = ExtendedODEModel(params)
    # Override disruption day to day 100 (as in original scenario)
    # But for 1973 crisis, we might want to simulate different shock.
    # We'll keep Hormuz disruption as a generic shock.

    print("Running 365-day validation simulation...")
    sol = model.simulate(t_span=(0.0, 365.0), method="BDF", rtol=1e-6, atol=1e-8)
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

    # Compute summary statistics
    print("\n=== Validation Summary (1973) ===")
    print(
        f"Average oil price change: {price_oil.mean() / params['oil_price'].mean() - 1:.1%}"
    )
    print(f"Average inflation: {inflation.mean():.3f}")
    print(f"Average debt/GDP: {debt.mean():.3f}")
    print(f"Average political stability: {stability.mean():.3f}")

    # Threshold activations
    debt_crisis = debt > 1.0
    depreciation = (exchange_avg - exchange) / (exchange_avg + 1e-8)
    currency_crisis = depreciation > 0.2
    social_unrest = (inequality > 0.6) & (inflation > 0.1)
    water_scarcity = water < (params["water_availability"] * 10.0 * 0.1)

    print("\n=== Threshold Activations ===")
    print(f"Debt crisis regions: {debt_crisis.sum()} / {n}")
    print(f"Currency crisis regions: {currency_crisis.sum()} / {n}")
    print(f"Social unrest regions: {social_unrest.sum()} / {n}")
    print(f"Water scarcity regions: {water_scarcity.sum()} / {n}")

    # Plot results (optional)
    plot = input("Plot results? (y/n): ").strip().lower()
    if plot == "y":
        model.plot_results(sol)

    print("\nValidation complete.")
    return sol


if __name__ == "__main__":
    run_validation()
