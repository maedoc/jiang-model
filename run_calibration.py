"""
Run limited calibration to generate parameter sets for demonstration.
"""

import json
import numpy as np
from historical_calibration import HistoricalCalibrator
from ode_model_extended import load_parameters


def calibrate_period(period, maxiter=5):
    print(f"\n=== Calibrating for {period} ===")
    params = load_parameters("real_params.json")
    calibrator = HistoricalCalibrator(params, period)
    calibrator.load_historical_data()

    # Select a small subset of parameters for demonstration
    param_names = [
        "stability_coupling",
        "capital_flow",
        "financial_coupling",
    ]

    # Run limited optimization
    optimized_params, result = calibrator.optimize_parameters(
        param_names, maxiter=maxiter
    )

    # Save calibrated parameters
    output_file = f"params_{period}.json"
    calibrator.save_calibrated_params(optimized_params, output_file)

    # Also compute loss improvement
    base_traj = calibrator.simulate_with_params(params, t_span=(0.0, 730.0))
    base_loss = calibrator.compute_loss(base_traj, calibrator.historical_data)
    opt_traj = calibrator.simulate_with_params(optimized_params, t_span=(0.0, 730.0))
    opt_loss = calibrator.compute_loss(opt_traj, calibrator.historical_data)
    print(f"Base loss: {base_loss:.6f}, Optimized loss: {opt_loss:.6f}")
    print(f"Improvement: {(base_loss - opt_loss) / base_loss * 100:.1f}%")

    return optimized_params


if __name__ == "__main__":
    # Calibrate both periods with minimal iterations (for speed)
    params_1973 = calibrate_period("1973", maxiter=2)
    params_2008 = calibrate_period("2008", maxiter=2)

    print("\nCalibration complete. Parameter files:")
    print("  - params_1973.json")
    print("  - params_2008.json")
    print("\nNote: These are demonstration files with limited optimization.")
