"""
Generate real-world parameters for DDE model.
"""

import json
import numpy as np
import jax.numpy as jnp
from data_loader import (
    real_world_parameters,
    REGIONS,
    load_political_stability,
    compute_water_trade_flow,
    compute_capital_flow,
    compute_financial_coupling,
)


def scale_parameters(
    params, target_total_oil=200.0, target_total_fert=200.0, target_total_water=200.0
):
    """Scale production/consumption to match target total while preserving ratios.

    Args:
        params: dict with oil_production, oil_consumption, etc.
        target_total_oil: desired sum of oil production across all regions (model units per day)
        target_total_fert: same for fertilizer.
        target_total_water: desired sum of water availability across all regions (model units per day)

    Returns:
        scaled params dict.
    """
    # Convert JAX arrays to numpy for manipulation
    oil_prod = np.array(params["oil_production"])
    oil_cons = np.array(params["oil_consumption"])
    fert_prod = np.array(params["fertilizer_production"])
    fert_cons = np.array(params["fertilizer_consumption"])
    water_avail = np.array(params["water_availability"])
    water_cons = np.array(params["water_consumption"])

    # Compute current totals (per year)
    total_oil_prod = oil_prod.sum()
    total_fert_prod = fert_prod.sum()
    total_water_avail = water_avail.sum()  # km³/year

    # Scaling factors
    scale_oil = target_total_oil / total_oil_prod if total_oil_prod > 0 else 1.0
    scale_fert = target_total_fert / total_fert_prod if total_fert_prod > 0 else 1.0
    # Convert water from annual to daily and scale to target
    # water_avail is km³/year, convert to per day: divide by 365.25
    water_avail_per_day = total_water_avail / 365.25
    scale_water = (
        target_total_water / water_avail_per_day if water_avail_per_day > 0 else 1.0
    )

    print(f"Oil scaling factor: {scale_oil:.6f}")
    print(f"Fertilizer scaling factor: {scale_fert:.6f}")
    print(
        f"Water scaling factor: {scale_water:.6f} (annual total {total_water_avail:.2f} km³/year -> {water_avail_per_day:.2f} km³/day)"
    )

    # Apply scaling
    oil_prod_scaled = oil_prod * scale_oil
    oil_cons_scaled = oil_cons * scale_oil
    fert_prod_scaled = fert_prod * scale_fert
    fert_cons_scaled = fert_cons * scale_fert
    # Water: scale annual to daily and apply scaling factor
    water_avail_scaled = water_avail * scale_water / 365.25
    water_cons_scaled = water_cons * scale_water / 365.25

    # Convert back to JAX arrays
    params_scaled = params.copy()
    params_scaled["oil_production"] = jnp.array(oil_prod_scaled)
    params_scaled["oil_consumption"] = jnp.array(oil_cons_scaled)
    params_scaled["fertilizer_production"] = jnp.array(fert_prod_scaled)
    params_scaled["fertilizer_consumption"] = jnp.array(fert_cons_scaled)
    params_scaled["water_availability"] = jnp.array(water_avail_scaled)
    params_scaled["water_consumption"] = jnp.array(water_cons_scaled)

    return params_scaled


def compute_trade_flows(oil_prod, oil_cons, fert_prod, fert_cons):
    """Compute trade matrices based on surplus/deficit.

    Args:
        oil_prod, oil_cons: arrays of shape (n_regions,)

    Returns:
        oil_trade, fert_trade matrices shape (n_regions, n_regions)
        where element (i,j) is flow from j to i.
    """
    n = len(oil_prod)
    oil_surplus = oil_prod - oil_cons
    fert_surplus = fert_prod - fert_cons

    # Adjust fertilizer surplus to create trade: assume Asia regions are importers,
    # Middle East, Russia, North America are exporters
    # We'll modify fert_surplus by shifting some production
    # Let's create a simple pattern: reduce surplus in Asia, increase in exporters
    # Indices: 4 China, 5 India, 6 Japan, 7 Southeast Asia -> deficit
    # Exporters: 0 North America, 2 Russia, 3 Middle East
    asia_idx = [4, 5, 6, 7]
    exporter_idx = [0, 2, 3]
    # Reduce surplus in Asia by 30% of their production, add to exporters
    for i in asia_idx:
        reduction = fert_prod[i] * 0.3
        fert_surplus[i] -= reduction
        # Distribute reduction equally among exporters
        for j in exporter_idx:
            fert_surplus[j] += reduction / len(exporter_idx)

    oil_trade = np.zeros((n, n))
    fert_trade = np.zeros((n, n))

    # Identify deficit and surplus regions
    deficit_mask = oil_surplus < 0
    surplus_mask = oil_surplus > 0

    deficit_regions = np.where(deficit_mask)[0]
    surplus_regions = np.where(surplus_mask)[0]

    # For each deficit region, allocate imports proportionally to surplus
    for i in deficit_regions:
        deficit = -oil_surplus[i]
        total_surplus = oil_surplus[surplus_mask].sum()
        if total_surplus > 0:
            for j in surplus_regions:
                share = oil_surplus[j] / total_surplus
                flow = deficit * share
                oil_trade[i, j] = flow

    # Same for fertilizer
    deficit_mask = fert_surplus < 0
    surplus_mask = fert_surplus > 0
    deficit_regions = np.where(deficit_mask)[0]
    surplus_regions = np.where(surplus_mask)[0]
    for i in deficit_regions:
        deficit = -fert_surplus[i]
        total_surplus = fert_surplus[surplus_mask].sum()
        if total_surplus > 0:
            for j in surplus_regions:
                share = fert_surplus[j] / total_surplus
                flow = deficit * share
                fert_trade[i, j] = flow

    # Add some baseline trade for stability coupling (small random)
    # Ensure no self-trade
    for i in range(n):
        oil_trade[i, i] = 0
        fert_trade[i, i] = 0

    return oil_trade, fert_trade


def add_stability_coupling(params, region_names):
    """Add stability coupling matrix based on geographic proximity and trade.
    Placeholder: simple inverse distance weighting.
    """
    n = len(region_names)
    coupling = np.zeros((n, n))
    # Use simple heuristic: coupling stronger between regions with high trade
    oil_trade = np.array(params["oil_trade_flow"])
    fert_trade = np.array(params["fertilizer_trade_flow"])
    total_trade = oil_trade + fert_trade

    # Normalize trade to 0-1 range
    if total_trade.max() > 0:
        total_trade_norm = total_trade / total_trade.max()
    else:
        total_trade_norm = total_trade

    # Coupling strength proportional to trade volume, scaled by factor
    coupling_strength = 0.01  # arbitrary
    coupling = total_trade_norm * coupling_strength

    # Ensure diagonal zero
    np.fill_diagonal(coupling, 0)

    params["stability_coupling"] = jnp.array(coupling)
    return params


def save_parameters(params, filename="real_params.json"):
    """Convert JAX arrays to lists and save as JSON."""
    params_dict = {}
    for key, value in params.items():
        if isinstance(value, jnp.ndarray):
            params_dict[key] = value.tolist()
        else:
            params_dict[key] = value
    with open(filename, "w") as f:
        json.dump(params_dict, f, indent=2)
    print(f"Parameters saved to {filename}")


def load_parameters(filename="real_params.json"):
    """Load parameters from JSON and convert to JAX arrays."""
    with open(filename, "r") as f:
        params_dict = json.load(f)
    params = {}
    for key, value in params_dict.items():
        params[key] = jnp.array(value)
    return params


def main():
    print("Generating real-world parameters for 12 regions...")
    params = real_world_parameters(year=2023)

    print("\nOriginal aggregates:")
    print(
        f"Total oil production: {np.array(params['oil_production']).sum():.2f} TWh/year"
    )
    print(
        f"Total oil consumption: {np.array(params['oil_consumption']).sum():.2f} TWh/year"
    )
    print(
        f"Total fertilizer production: {np.array(params['fertilizer_production']).sum():.2f} tonnes/year"
    )
    print(
        f"Total fertilizer consumption: {np.array(params['fertilizer_consumption']).sum():.2f} tonnes/year"
    )

    # Scale to model units
    params_scaled = scale_parameters(
        params,
        target_total_oil=200.0,
        target_total_fert=200.0,
        target_total_water=200.0,
    )

    print("\nScaled aggregates (per day):")
    print(
        f"Total oil production: {np.array(params_scaled['oil_production']).sum():.2f} units/day"
    )
    print(
        f"Total oil consumption: {np.array(params_scaled['oil_consumption']).sum():.2f} units/day"
    )
    print(
        f"Total fertilizer production: {np.array(params_scaled['fertilizer_production']).sum():.2f} units/day"
    )
    print(
        f"Total fertilizer consumption: {np.array(params_scaled['fertilizer_consumption']).sum():.2f} units/day"
    )
    print(
        f"Total water availability: {np.array(params_scaled['water_availability']).sum():.2f} units/day"
    )
    print(
        f"Total water consumption: {np.array(params_scaled['water_consumption']).sum():.2f} units/day"
    )

    # Add political stability index
    stability = load_political_stability()
    params_scaled["political_stability"] = jnp.array(stability)

    # Compute trade matrices based on scaled production/consumption
    oil_prod = np.array(params_scaled["oil_production"])
    oil_cons = np.array(params_scaled["oil_consumption"])
    fert_prod = np.array(params_scaled["fertilizer_production"])
    fert_cons = np.array(params_scaled["fertilizer_consumption"])
    water_avail = np.array(params_scaled["water_availability"])
    water_cons = np.array(params_scaled["water_consumption"])

    oil_trade, fert_trade = compute_trade_flows(
        oil_prod, oil_cons, fert_prod, fert_cons
    )
    water_trade = compute_water_trade_flow(water_avail, water_cons)
    params_scaled["oil_trade_flow"] = jnp.array(oil_trade)
    params_scaled["fertilizer_trade_flow"] = jnp.array(fert_trade)
    params_scaled["water_trade_flow"] = jnp.array(water_trade)
    # Keep old keys for compatibility (set to zeros)
    params_scaled["oil_trade"] = jnp.zeros_like(oil_trade)
    params_scaled["fertilizer_trade"] = jnp.zeros_like(fert_trade)

    # Compute capital flow and financial coupling matrices
    trade_matrices = [oil_trade, fert_trade, water_trade]
    capital_flow = compute_capital_flow(trade_matrices, stability)
    financial_coupling = compute_financial_coupling(trade_matrices, stability)
    params_scaled["capital_flow"] = jnp.array(capital_flow)
    params_scaled["financial_coupling"] = jnp.array(financial_coupling)

    # Add stability coupling
    params_scaled = add_stability_coupling(params_scaled, REGIONS)

    # Save parameters
    save_parameters(params_scaled, "real_params.json")

    # Print region-wise values
    print("\nRegion breakdown:")
    for i, region in enumerate(REGIONS):
        print(f"{region}:")
        print(
            f"  Oil: prod={oil_prod[i]:.2f}, cons={oil_cons[i]:.2f}, surplus={oil_prod[i] - oil_cons[i]:.2f}"
        )
        print(
            f"  Fert: prod={fert_prod[i]:.2f}, cons={fert_cons[i]:.2f}, surplus={fert_prod[i] - fert_cons[i]:.2f}"
        )

    print("\nOil trade matrix (row i imports from col j):")
    print(np.array2string(oil_trade, precision=2, suppress_small=True))

    print("\nFertilizer trade matrix:")
    print(np.array2string(fert_trade, precision=2, suppress_small=True))

    print("\nStability coupling matrix:")
    print(
        np.array2string(
            np.array(params_scaled["stability_coupling"]),
            precision=4,
            suppress_small=True,
        )
    )


if __name__ == "__main__":
    main()
