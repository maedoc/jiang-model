import sys

sys.path.insert(0, ".")
from ode_model_extended import load_parameters, ExtendedODEModel
import numpy as np
import warnings

warnings.filterwarnings("ignore")

params = load_parameters("real_params.json")
model = ExtendedODEModel(params)
print("Running 365-day simulation...")
sol = model.simulate(t_span=(0.0, 365.0), method="BDF", rtol=1e-4, atol=1e-6)
n = model.n_regions
log_debt = sol.y[model.idx_log_debt * n : (model.idx_log_debt + 1) * n, :]
debt = np.expm1(np.clip(log_debt, -100, 100))
print(f"Simulation completed with {sol.t.size} time points")
print(f"Max debt over time: {debt.max():.3f}")
print(f"Min debt over time: {debt.min():.3f}")
print(f"Final debt:")
for i in range(n):
    print(f"  {model.region_name(i)}: {debt[i, -1]:.3f}")
# Check if any variable exploded
max_vals = []
for var_idx in range(model.n_vars_per_region):
    start = var_idx * n
    vals = sol.y[start : start + n, -1]
    max_vals.append(np.max(np.abs(vals)))
print(f"Max absolute state per variable: {max_vals}")
if debt.max() > 10:
    print("WARNING: Debt exceeded 10")
else:
    print("SUCCESS: Debt bounded below 10")
# Also check water stocks
log_water = sol.y[model.idx_log_water * n : (model.idx_log_water + 1) * n, :]
water = np.expm1(np.clip(log_water, -100, 100))
print(f"Water stocks min: {water.min():.3f}, max: {water.max():.3f}")
