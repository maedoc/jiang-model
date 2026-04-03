#!/usr/bin/env python3
"""
Quick calibration run for demonstration.
"""

import sys

sys.path.insert(0, ".")
from historical_calibration import HistoricalCalibrator, load_parameters


def calibrate_1973():
    print("Loading base parameters...")
    params = load_parameters("real_params.json")
    calibrator = HistoricalCalibrator(params, "1973")
    calibrator.load_historical_data()

    # Select parameters to calibrate (same as in main)
    param_names = [
        "stability_coupling",
        "capital_flow",
        "financial_coupling",
        "debt_to_gdp",  # initial debt
    ]

    print("Running optimization (maxiter=5)...")
    optimized_params, result = calibrator.optimize_parameters(param_names, maxiter=5)

    print(f"Optimization success: {result.success}")
    print(f"Final loss: {result.fun:.6f}")

    # Save calibrated parameters
    calibrator.save_calibrated_params(optimized_params, "params_1973_calibrated.json")
    print("Saved to params_1973_calibrated.json")

    return optimized_params


if __name__ == "__main__":
    calibrate_1973()
