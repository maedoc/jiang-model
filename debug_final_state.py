#!/usr/bin/env python3
import numpy as np
from ode_model_extended import ExtendedODEModel, load_parameters
from scipy.integrate import solve_ivp

params = load_parameters("real_params.json")
model = ExtendedODEModel(params)
y0 = model.simulate(t_span=(0.0, 0.0)).y[:, 0]
n = model.n_regions

# Simulate 1 day with BDF
sol = solve_ivp(
    lambda t, y: model.system(t, y),
    (0.0, 1.0),
    y0,
    method="BDF",
    rtol=1e-6,
    atol=1e-8,
    dense_output=False,
)
print(f"Success: {sol.success}, Steps: {sol.t.size}")
y_final = sol.y[:, -1]

# Extract each variable type
var_names = [
    "log_oil",
    "log_fert",
    "stability",
    "log_water",
    "log_military",
    "logit_inequality",
    "log_debt",
    "log_price_oil",
    "log_price_fert",
    "log_price_water",
    "inflation",
    "interest",
    "log_exchange",
    "bond_yield",
    "log_exchange_avg",
]

print("\nMax absolute value per variable type:")
for i, name in enumerate(var_names):
    block = y_final[i * n : (i + 1) * n]
    max_abs = np.max(np.abs(block))
    print(f"  {name:<20}: {max_abs:.2e}")
    # If max_abs > 1e6, show the region index
    if max_abs > 1e6:
        idx = np.argmax(np.abs(block))
        print(f"    (region {idx}: {block[idx]:.2e})")


# Convert back to original units for key variables
def exp_transform(x):
    return np.expm1(x) + 1


def inv_logit(x):
    return 1.0 / (1.0 + np.exp(-x))


print("\nOriginal units for key variables (region 0):")
log_oil = y_final[0 * n : 1 * n]
log_fert = y_final[1 * n : 2 * n]
stability = y_final[2 * n : 3 * n]
log_debt = y_final[6 * n : 7 * n]
log_price_oil = y_final[7 * n : 8 * n]
inflation = y_final[10 * n : 11 * n]

oil = exp_transform(log_oil)
fert = exp_transform(log_fert)
debt = exp_transform(log_debt)
price_oil = exp_transform(log_price_oil)

print(f"Oil stock: {oil[0]:.2f}")
print(f"Fertilizer stock: {fert[0]:.2f}")
print(f"Stability: {stability[0]:.3f}")
print(f"Debt/GDP: {debt[0]:.3f}")
print(f"Oil price: {price_oil[0]:.2f}")
print(f"Inflation: {inflation[0]:.4f}")

# Check for extreme values
print("\nChecking extremes across all regions:")
for i, name in enumerate(var_names):
    block = y_final[i * n : (i + 1) * n]
    if np.max(np.abs(block)) > 1e6:
        print(f"  {name} has extreme values")
        for j in range(n):
            if abs(block[j]) > 1e6:
                print(f"    Region {j}: {block[j]:.2e}")
