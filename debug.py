import jax
import jax.numpy as jnp
import numpy as np
from dde_model_extended import GeopoliticalDDE, load_parameters_from_json

params = load_parameters_from_json("real_params.json")
n = len(params["oil_production"])
print(f"n_regions = {n}")

# Create model with 1 region for simplicity
model = GeopoliticalDDE(n_regions=1, state_dim=3)
# Extract first region parameters
params1 = {}
for key, val in params.items():
    if isinstance(val, jnp.ndarray):
        if val.ndim == 1:
            params1[key] = val[:1]
        elif val.ndim == 2:
            params1[key] = val[:1, :1]
        else:
            params1[key] = val
    else:
        params1[key] = val
model.set_parameters(params1)

# Initial state
O_init = params1["oil_production"][0] * 2.0
F_init = params1["fertilizer_production"][0] * 2.0
S_init = 0.7
initial_state = jnp.array([O_init, F_init, S_init])
print(f"Initial state: {initial_state}")

# Simulate manually with Euler for few steps
state = initial_state
for step in range(10):
    # Compute local dynamics only
    O, F, S = state
    dO = params1["oil_production"][0] * S - params1["oil_consumption"][0]
    dF = params1["fertilizer_production"][0] * S - params1["fertilizer_consumption"][0]
    resource_abundance = jnp.tanh(0.01 * (O + F))
    dS = -params1["stability_decay"][0] * S + params1["stability_gain"][
        0
    ] * resource_abundance * (1 - S)
    deriv = jnp.array([dO, dF, dS])
    state = state + 1.0 * deriv
    print(f"Step {step}: {state}")
