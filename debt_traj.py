import sys

sys.path.insert(0, ".")
from ode_model_extended import load_parameters, ExtendedODEModel
import numpy as np

params = load_parameters("real_params.json")
model = ExtendedODEModel(params)
sol = model.simulate(t_span=(0.0, 10.0), method="BDF", rtol=1e-6, atol=1e-8)
n = model.n_regions
log_debt = sol.y[model.idx_log_debt * n : (model.idx_log_debt + 1) * n, :]
debt = np.expm1(np.clip(log_debt, -100, 100))
print("Time steps:", sol.t.shape)
print("Debt shape:", debt.shape)
for idx in range(min(3, n)):
    print(f"\nRegion {model.region_name(idx)} debt trajectory:")
    for t_idx, t in enumerate(sol.t[:10]):  # first 10 time points
        print(f"  t={t:.2f} debt={debt[idx, t_idx]:.3f}")
# Check if debt explodes later
max_debt = debt.max()
print(f"\nMax debt across all regions and times: {max_debt}")
if max_debt > 10:
    print("Debt exploded >10")
    # Find where
    for idx in range(n):
        if debt[idx, -1] > 10:
            print(f"  Region {model.region_name(idx)} final debt {debt[idx, -1]:.2e}")
