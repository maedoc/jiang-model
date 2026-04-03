import sys

sys.path.insert(0, ".")
from ode_model_extended import load_parameters, ExtendedODEModel
import numpy as np

params = load_parameters("real_params.json")
model = ExtendedODEModel(params)
# Simulate for 100 days
sol = model.simulate(t_span=(0.0, 100.0), method="BDF", rtol=1e-6, atol=1e-8)
# Extract debt
n = model.n_regions
log_debt = sol.y[model.idx_log_debt * n : (model.idx_log_debt + 1) * n, -1]
debt = np.expm1(np.clip(log_debt, -100, 100))
print("Debt/GDP final:", debt)
print("Mean debt:", debt.mean())
print("Max debt:", debt.max())
print("Min debt:", debt.min())
# Also compute debt/GDP ratio? Already scaled.
# Check if any debt > 10
if (debt > 10).any():
    print("WARNING: Debt exploded > 10")
# Print for each region
for i in range(n):
    print(f"{model.region_name(i)}: {debt[i]:.2f}")
