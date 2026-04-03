import jax
import jax.numpy as jnp
import numpy as np
from dde_model_extended import GeopoliticalDDE, load_parameters_from_json

params = load_parameters_from_json("real_params.json")
n = len(params["oil_production"])
print(f"n_regions = {n}")

# Create model with 2 regions (Europe and Middle East)
model = GeopoliticalDDE(n_regions=2, state_dim=3)
# Extract region 1 (Europe) and region 3 (Middle East) indices 1 and 3
idx1, idx2 = 1, 3
params2 = {}
for key, val in params.items():
    if isinstance(val, jnp.ndarray):
        if val.ndim == 1:
            params2[key] = val[[idx1, idx2]]
        elif val.ndim == 2:
            params2[key] = val[[idx1, idx2], :][:, [idx1, idx2]]
        else:
            params2[key] = val
    else:
        params2[key] = val
model.set_parameters(params2)

# Initial states
O1 = params["oil_production"][idx1] * 2.0
F1 = params["fertilizer_production"][idx1] * 2.0
S1 = 0.7
O2 = params["oil_production"][idx2] * 2.0
F2 = params["fertilizer_production"][idx2] * 2.0
S2 = 0.7
state_i = jnp.array([O1, F1, S1])
state_j = jnp.array([O2, F2, S2])
print(f"State i (Europe): {state_i}")
print(f"State j (Middle East): {state_j}")

# Compute coupling term from j to i (i imports from j)
oil_trade_flow = params2["oil_trade_flow"][0, 1]  # i=0 (Europe), j=1 (ME)
fert_trade_flow = params2["fertilizer_trade_flow"][0, 1]
stability_coupling = params2["stability_coupling"][0, 1]
print(f"oil_trade_flow: {oil_trade_flow}")
print(f"fert_trade_flow: {fert_trade_flow}")
print(f"stability_coupling: {stability_coupling}")

# Manual coupling term
dO = oil_trade_flow * S2
dF = fert_trade_flow * S2
dS = stability_coupling * (S2 - S1) * S1 * (1 - S1)
print(f"Coupling derivatives: dO={dO}, dF={dF}, dS={dS}")

# Now compute full derivative with local + coupling
# Local derivative for i
oil_prod = params2["oil_production"][0]
oil_cons = params2["oil_consumption"][0]
fert_prod = params2["fertilizer_production"][0]
fert_cons = params2["fertilizer_consumption"][0]
stability_decay = params2["stability_decay"][0]
stability_gain = params2["stability_gain"][0]

dO_local = oil_prod * S1 - oil_cons
dF_local = fert_prod * S1 - fert_cons
resource_abundance = jnp.tanh(0.01 * (O1 + F1))
dS_local = -stability_decay * S1 + stability_gain * resource_abundance * (1 - S1)
print(
    f"Local derivatives: dO_local={dO_local}, dF_local={dF_local}, dS_local={dS_local}"
)

dO_total = dO_local + dO
dF_total = dF_local + dF
dS_total = dS_local + dS
print(
    f"Total derivatives: dO_total={dO_total}, dF_total={dF_total}, dS_total={dS_total}"
)

# Compute next state with Euler step DT=1
next_state = state_i + jnp.array([dO_total, dF_total, dS_total])
print(f"Next state: {next_state}")
