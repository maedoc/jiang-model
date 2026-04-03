import json
import jax.numpy as jnp
from dde_model_extended import GeopoliticalDDE

with open("real_params.json", "r") as f:
    params_dict = json.load(f)

# Zero out trade flows
params_dict["oil_trade_flow"] = [[0] * 12 for _ in range(12)]
params_dict["fertilizer_trade_flow"] = [[0] * 12 for _ in range(12)]
params_dict["stability_coupling"] = [[0] * 12 for _ in range(12)]

params = {}
for key, val in params_dict.items():
    params[key] = jnp.array(val)

n = len(params["oil_production"])
model = GeopoliticalDDE(n_regions=n, state_dim=3)
model.set_parameters(params)

# Initial conditions
initial_state = []
for i in range(n):
    O_init = params["oil_production"][i] * 2.0
    F_init = params["fertilizer_production"][i] * 2.0
    S_init = 0.7
    initial_state.extend([O_init, F_init, S_init])
initial_state = jnp.array(initial_state)

print("Running simulation with zero trade...")
states, times = model.simulate(initial_state, disruption_day=100.0)
states_reshaped = states.reshape(-1, n, 3)
print("Final oil levels:")
for i in range(n):
    final_oil = states_reshaped[-1, i, 0]
    print(f"  Region {i}: {final_oil:.1f}")
# Check for NaN
if jnp.any(jnp.isnan(states)):
    print("NaN detected!")
else:
    print("No NaN - simulation stable.")
