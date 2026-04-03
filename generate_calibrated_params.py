"""
Generate placeholder calibrated parameter sets by adding small random perturbations.
This is for demonstration purposes only; full calibration requires extensive computation.
"""

import json
import numpy as np
from ode_model_extended import load_parameters


def perturb_params(base_params, seed=1973, scale=0.1):
    """
    Add small random perturbations to parameters.
    Preserves shape and constraints (non-negative, etc.).
    """
    np.random.seed(seed)
    perturbed = {}
    for key, val in base_params.items():
        if isinstance(val, np.ndarray):
            # Perturb each element by up to ±scale*abs(val)
            # Ensure non-negative for certain parameters
            perturbation = 1.0 + scale * (2 * np.random.rand(*val.shape) - 1)
            new_val = val * perturbation
            # Clip to reasonable ranges
            if "price" in key or "exchange" in key:
                new_val = np.clip(new_val, val * 0.5, val * 2.0)
            elif "coupling" in key or "flow" in key:
                new_val = np.clip(new_val, 0.0, val * 3.0)
            elif "debt" in key:
                new_val = np.clip(new_val, 0.0, val * 1.5)
            elif "stability" in key:
                new_val = np.clip(new_val, 0.0, 1.0)
            else:
                new_val = np.maximum(new_val, 0.0)  # non-negative
            perturbed[key] = new_val
        else:
            perturbed[key] = val
    return perturbed


def save_params(params, filename):
    """Save parameters to JSON file."""
    save_dict = {}
    for key, val in params.items():
        if isinstance(val, np.ndarray):
            save_dict[key] = val.tolist()
        else:
            save_dict[key] = val

    with open(filename, "w") as f:
        json.dump(save_dict, f, indent=2)
    print(f"Saved {filename}")


def main():
    base_params = load_parameters("real_params.json")

    # Generate 1973 calibrated params (oil crisis adjustments)
    print("Generating params_1973.json (oil crisis profile)...")
    params_1973 = perturb_params(base_params, seed=1973, scale=0.15)
    # Adjust specific parameters for oil crisis: higher oil price sensitivity
    if "oil_price" in params_1973:
        params_1973["oil_price"] *= 1.5  # higher baseline oil price
    if "stability_coupling" in params_1973:
        params_1973["stability_coupling"] *= 1.2  # stronger stability spillovers
    save_params(params_1973, "params_1973.json")

    # Generate 2008 calibrated params (financial crisis adjustments)
    print("Generating params_2008.json (financial crisis profile)...")
    params_2008 = perturb_params(base_params, seed=2008, scale=0.2)
    # Adjust for financial crisis: higher debt, stronger financial coupling
    if "debt_to_gdp" in params_2008:
        params_2008["debt_to_gdp"] *= 1.8
    if "financial_coupling" in params_2008:
        params_2008["financial_coupling"] *= 2.0
    if "capital_flow" in params_2008:
        params_2008["capital_flow"] *= 1.5
    save_params(params_2008, "params_2008.json")

    print("\nPlaceholder calibrated parameter sets generated.")
    print(
        "These are for demonstration only; full calibration requires extensive optimization."
    )


if __name__ == "__main__":
    main()
