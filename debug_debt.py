import sys

sys.path.insert(0, ".")
from ode_model_extended import load_parameters, ExtendedODEModel
import numpy as np

params = load_parameters("real_params.json")
model = ExtendedODEModel(params)
n = model.n_regions
# Get default initial condition
y0 = None
sol = model.simulate(t_span=(0.0, 10.0), y0=y0, method="BDF", rtol=1e-6, atol=1e-8)
# Extract initial state
y0 = sol.y[:, 0]
# Compute derivative at t=0
dydt = model.system(0.0, y0)
# Extract debt derivative
log_debt0 = y0[model.idx_log_debt * n : (model.idx_log_debt + 1) * n]
debt0 = np.expm1(np.clip(log_debt0, -100, 100))
dlog_debt = dydt[model.idx_log_debt * n : (model.idx_log_debt + 1) * n]
ddebt = dlog_debt * (1 + debt0)  # approximate conversion
print("Initial debt:", debt0)
print("Debt derivative (approx):", ddebt)
print("Region names:", model.region_names)
# Compute gov_spending, tax_revenue etc. We'll need to replicate the system logic.
# Instead, let's add a debug flag to model. For now, let's compute using the system method but we need to extract intermediate variables.
# Let's add a debug method later.
# For now, just print debt and derivative.
print("\nDebt target (initial debt_to_gdp):", params["debt_to_gdp"])
# Compute GDP proxy
# Let's compute using the system method but we need to extract gdp.
# We'll hack: modify system temporarily to print.
print("\nRunning simulation with debug prints...")


# We'll create a subclass that overrides system.
class DebugModel(ExtendedODEModel):
    def system(self, t, y):
        n = self.n_regions
        # Extract state variables
        (
            log_oil,
            log_fert,
            stability,
            log_water,
            log_military,
            logit_inequality,
            log_debt,
            log_price_oil,
            log_price_fert,
            log_price_water,
            inflation,
            interest,
            log_exchange,
            bond_yield,
        ) = self.extract_state(y)
        # Convert transformed variables back to original units
        oil = np.expm1(np.clip(log_oil, -100, 100))
        fert = np.expm1(np.clip(log_fert, -100, 100))
        water = np.expm1(np.clip(log_water, -100, 100))
        military = np.expm1(np.clip(log_military, -100, 100))
        inequality = 1.0 / (1.0 + np.exp(-np.clip(logit_inequality, -50, 50)))
        debt = np.expm1(np.clip(log_debt, -100, 100))
        price_oil = np.expm1(np.clip(log_price_oil, -100, 100))
        price_fert = np.expm1(np.clip(log_price_fert, -100, 100))
        price_water = np.expm1(np.clip(log_price_water, -100, 100))
        exchange = np.expm1(np.clip(log_exchange, -100, 100))
        # GDP proxy
        stability_clipped = np.clip(stability, 0.0, 1.0)
        oil_prod = self.params["oil_production"]
        fert_prod = self.params["fertilizer_production"]
        gdp = oil_prod * stability_clipped + fert_prod * stability_clipped
        gdp_scale = np.mean(gdp) if np.mean(gdp) > 0 else 1.0
        gdp = gdp / gdp_scale
        # Compute gov_spending, tax_revenue for first region
        i = 0
        gov_spending = military[i] * gdp[i] * 0.01
        tax_revenue = gdp[i] * 0.3 * stability_clipped[i]
        debt_ceiling = 2.0
        debt_clipped = np.clip(debt[i], -5.0, 10.0)
        austerity_factor = 1.0 / (1.0 + np.exp(10.0 * (debt_clipped - debt_ceiling)))
        gov_spending *= austerity_factor
        primary_deficit = gov_spending - tax_revenue
        growth_rate = 0.02 * stability_clipped[i]
        debt_target = self.params["debt_to_gdp"][i]
        mean_reversion = 0.1 * (debt_target - debt[i])
        dDdt = primary_deficit + (interest[i] - growth_rate) * debt[i] + mean_reversion
        print(
            f"t={t:.2f} region {self.region_name(i)}: debt={debt[i]:.3f}, gov={gov_spending:.3f}, tax={tax_revenue:.3f}, primary={primary_deficit:.3f}, interest={interest[i]:.3f}, growth={growth_rate:.3f}, dDdt={dDdt:.3f}"
        )
        # Only print once per call
        # Call parent system
        return super().system(t, y)


debug_model = DebugModel(params)
sol2 = debug_model.simulate(t_span=(0.0, 2.0), method="BDF", rtol=1e-6, atol=1e-8)
print("Done.")
