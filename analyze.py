import sys

sys.path.insert(0, ".")
from ode_model_extended import load_parameters, ExtendedODEModel
import numpy as np

params = load_parameters("real_params.json")
model = ExtendedODEModel(params)
n = model.n_regions
# Get default initial condition using model's simulate with tiny span
sol = model.simulate(t_span=(0.0, 0.0), method="BDF", rtol=1e-6, atol=1e-8)
y0 = sol.y[:, 0]
# Extract state
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
) = model.extract_state(y0)
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
stability_clipped = np.clip(stability, 0.0, 1.0)
# GDP proxy
oil_prod = params["oil_production"]
fert_prod = params["fertilizer_production"]
gdp = oil_prod * stability_clipped + fert_prod * stability_clipped
gdp_scale = np.mean(gdp) if np.mean(gdp) > 0 else 1.0
gdp = gdp / gdp_scale

print(
    "Region\tDebt\tInterest\tGrowth\tInterest-Growth\tGovSpend\tTaxRev\tPrimaryDeficit"
)
for i in range(n):
    gov_spending = military[i] * gdp[i] * 0.01
    tax_revenue = gdp[i] * 0.3 * stability_clipped[i]
    debt_ceiling = 2.0
    debt_clipped = np.clip(debt[i], -5.0, 10.0)
    austerity_factor = 1.0 / (1.0 + np.exp(10.0 * (debt_clipped - debt_ceiling)))
    gov_spending *= austerity_factor
    primary_deficit = gov_spending - tax_revenue
    debt_target = params["debt_to_gdp"][i]
    primary_deficit -= 0.1 * (debt[i] - debt_target)
    growth_rate = 0.02 * stability_clipped[i]
    mean_reversion = 0.5 * (debt_target - debt[i])
    dDdt = primary_deficit + (interest[i] - growth_rate) * debt[i] + mean_reversion
    print(
        f"{model.region_name(i)[:15]}\t{debt[i]:.3f}\t{interest[i]:.4f}\t{growth_rate:.4f}\t{interest[i] - growth_rate:.4f}\t{gov_spending:.3f}\t{tax_revenue:.3f}\t{primary_deficit:.3f}"
    )
print("\nGDP proxy:", gdp)
print("Military:", military)
print("Stability:", stability)
