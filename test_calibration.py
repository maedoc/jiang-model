"""
Quick test of historical calibration framework.
"""

from historical_calibration import HistoricalCalibrator
from ode_model_extended import load_parameters

params = load_parameters("real_params.json")
calibrator = HistoricalCalibrator(params, "1973")
calibrator.load_historical_data()  # loads CSV
print("Historical data loaded")

# Test simulation with base parameters
print("Running simulation with base parameters...")
trajectories = calibrator.simulate_with_params(params, t_span=(0.0, 10.0))
print(
    f"Simulation successful, t span: {trajectories['_t'][0]:.1f} to {trajectories['_t'][-1]:.1f}"
)
print(f"Trajectories keys: {list(trajectories.keys())}")

# Compute loss
loss = calibrator.compute_loss(trajectories, calibrator.historical_data)
print(f"Loss (base): {loss:.6f}")

print("Test completed successfully.")
