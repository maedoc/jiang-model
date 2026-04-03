import sys

sys.path.insert(0, ".")
from ode_model_extended import load_parameters, ExtendedODEModel
import numpy as np

params = load_parameters("real_params.json")


class ScaledDebtModel(ExtendedODEModel):
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
            log_exchange_avg,
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
        exchange_avg = np.expm1(np.clip(log_exchange_avg, -100, 100))
        stability_clipped = np.clip(stability, 0.0, 1.0)

        # Parameters
        oil_prod = self.params["oil_production"]
        oil_cons = self.params["oil_consumption"]
        fert_prod = self.params["fertilizer_production"]
        fert_cons = self.params["fertilizer_consumption"]
        water_avail = self.params["water_availability"]
        water_cons = self.params["water_consumption"]
        stability_decay = self.params["stability_decay"]
        stability_gain = self.params["stability_gain"]
        oil_trade = self.params["oil_trade_flow"]
        fert_trade = self.params["fertilizer_trade_flow"]
        water_trade = self.params["water_trade_flow"]
        stability_coupling = self.params["stability_coupling"]
        capital_flow = self.params["capital_flow"]
        financial_coupling = self.params["financial_coupling"]
        debt_target = self.params["debt_to_gdp"]
        initial_water = water_avail * 10.0

        # Compute Hormuz disruption effect on trade (reduce flows from Middle East)
        disruption = self.compute_hormuz_disruption(t)
        me_idx = 3  # Middle East index
        oil_trade_disrupted = oil_trade.copy()
        fert_trade_disrupted = fert_trade.copy()
        water_trade_disrupted = water_trade.copy()
        # Reduce exports from Middle East by disruption factor
        oil_trade_disrupted[:, me_idx] *= 1 - disruption
        fert_trade_disrupted[:, me_idx] *= 1 - disruption
        water_trade_disrupted[:, me_idx] *= 1 - disruption

        # Scale down trade flows to prevent excessive fluxes (as in stable model)
        trade_scale = 0.01
        oil_trade_disrupted *= trade_scale
        fert_trade_disrupted *= trade_scale
        water_trade_disrupted *= trade_scale

        # Initialize derivatives in original units
        dOdt = np.zeros(n)
        dFdt = np.zeros(n)
        dWdt = np.zeros(n)
        dSdt = np.zeros(n)
        dMdt = np.zeros(n)
        dIdt = np.zeros(n)  # inequality derivative (original units, 0-1)
        dDdt = np.zeros(n)  # debt derivative
        dPo_dt = np.zeros(n)  # oil price
        dPf_dt = np.zeros(n)  # fertilizer price
        dPw_dt = np.zeros(n)  # water price
        dInf_dt = np.zeros(n)  # inflation
        dInt_dt = np.zeros(n)  # interest rate
        dEx_dt = np.zeros(n)  # exchange rate
        dBy_dt = np.zeros(n)  # bond yield
        dExAvg_dt = np.zeros(n)  # exchange average

        # GDP proxy (used for debt dynamics)
        gdp = oil_prod * stability_clipped + fert_prod * stability_clipped
        gdp_scale = np.mean(gdp) if np.mean(gdp) > 0 else 1.0
        gdp = gdp / gdp_scale

        # Precompute nonlinear thresholds (same as original)
        # 1. Debt crisis: debt > 100% GDP (debt > 1.0)
        debt_crisis = 1.0 / (1.0 + np.exp(-10.0 * (debt - 1.0)))
        # 2. Currency crisis: 30-day depreciation > 20%
        depreciation = (exchange_avg - exchange) / (exchange_avg + 1e-8)
        currency_crisis = 1.0 / (1.0 + np.exp(-20.0 * (depreciation - 0.2)))
        # 3. Social unrest: inequality > 0.6 AND inflation > 0.1
        social_unrest = (1.0 / (1.0 + np.exp(-10.0 * (inequality - 0.6)))) * (
            1.0 / (1.0 + np.exp(-20.0 * (inflation - 0.1)))
        )
        # 4. Resource scarcity: water stock < 10% of initial
        water_scarcity = 1.0 / (1.0 + np.exp(-0.1 * (0.1 * initial_water - water)))

        # Compute resource derivatives with trade (similar to stable model)
        for i in range(n):
            # Local production minus consumption
            baseline = 0.5
            prod_oil = oil_prod[i] * (baseline + (1 - baseline) * stability_clipped[i])
            cons_oil = oil_cons[i]
            prod_fert = fert_prod[i] * (
                baseline + (1 - baseline) * stability_clipped[i]
            )
            cons_fert = fert_cons[i]
            prod_water = water_avail[i] * (
                baseline + (1 - baseline) * stability_clipped[i]
            )
            cons_water = water_cons[i]

            dOdt[i] = prod_oil - cons_oil
            dFdt[i] = prod_fert - cons_fert
            dWdt[i] = prod_water - cons_water

            # Trade contributions
            for j in range(n):
                if i == j:
                    continue
                # Oil flow from j to i: limited by exporter's available oil
                flow_oil = oil_trade_disrupted[i, j] * stability_clipped[j]
                limit = oil[j] / (oil[j] + 1000.0) if oil[j] > 0 else 0.0
                flow_oil *= limit
                dOdt[i] += flow_oil
                dOdt[j] -= flow_oil

                # Fertilizer flow
                flow_fert = fert_trade_disrupted[i, j] * stability_clipped[j]
                limit_fert = fert[j] / (fert[j] + 1000.0) if fert[j] > 0 else 0.0
                flow_fert *= limit_fert
                dFdt[i] += flow_fert
                dFdt[j] -= flow_fert

                # Water flow
                flow_water = water_trade_disrupted[i, j] * stability_clipped[j]
                limit_water = water[j] / (water[j] + 1000.0) if water[j] > 0 else 0.0
                flow_water *= limit_water
                dWdt[i] += flow_water
                dWdt[j] -= flow_water

                # Stability coupling
                dSdt[i] += (
                    stability_coupling[i, j]
                    * (stability[j] - stability[i])
                    * stability[i]
                    * (1 - stability[i])
                )

                # Financial coupling: capital flows affect exchange rates
                dEx_dt[i] += capital_flow[i, j] * (exchange[j] - exchange[i]) * 0.001
                # Interest rate coupling
                dInt_dt[i] += (
                    financial_coupling[i, j] * (interest[j] - interest[i]) * 0.01
                )

            # Local stability dynamics
            resource_abundance = np.tanh(0.01 * (oil[i] + fert[i] + water[i]))
            dSdt[i] += -stability_decay[i] * stability[i] + stability_gain[
                i
            ] * resource_abundance * (1 - stability[i])
            # Social unrest reduces stability gain
            dSdt[i] -= social_unrest[i] * 0.1 * stability[i]

            # Soft bounds for stability: push back toward [0,1]
            if stability[i] < 0:
                dSdt[i] += -10.0 * stability[i]
            elif stability[i] > 1:
                dSdt[i] += -10.0 * (stability[i] - 1)

            # Military expenditure dynamics
            dMdt[i] = (
                0.01 * gdp[i] - 0.05 * military[i] - debt_crisis[i] * 0.1 * military[i]
            )

            # Inequality dynamics
            dIdt[i] = (
                0.01 * (1 - stability_clipped[i])
                + 0.005 * debt[i]
                - 0.02 * inequality[i]
            )

            # Debt dynamics with daily scaling of interest and growth
            gov_spending = military[i] * gdp[i] * 0.01
            tax_revenue = gdp[i] * 0.3 * stability_clipped[i]
            debt_ceiling = 2.0
            debt_clipped = np.clip(debt[i], -5.0, 10.0)
            austerity_factor = 1.0 / (
                1.0 + np.exp(10.0 * (debt_clipped - debt_ceiling))
            )
            gov_spending *= austerity_factor
            primary_deficit = gov_spending - tax_revenue
            # SCALE: interest and growth are annual rates, convert to daily
            DAILY_SCALE = 1.0 / 365.25
            growth_rate = 0.02 * stability_clipped[i] * DAILY_SCALE
            mean_reversion = 0.1 * (debt_target[i] - debt[i])
            dDdt[i] = (
                primary_deficit
                + (interest[i] * DAILY_SCALE - growth_rate) * debt[i]
                + mean_reversion
            )
            # Debt crisis adds risk premium to interest rate (annual)
            dInt_dt[i] += debt_crisis[i] * 0.02

            # Price dynamics: respond to supply-demand imbalance
            oil_balance = (oil_cons[i] - oil_prod[i]) / (
                oil_cons[i] + oil_prod[i] + 1e-8
            )
            fert_balance = (fert_cons[i] - fert_prod[i]) / (
                fert_cons[i] + fert_prod[i] + 1e-8
            )
            water_balance = (water_cons[i] - water_avail[i]) / (
                water_cons[i] + water_avail[i] + 1e-8
            )
            dPo_dt[i] = 0.01 * oil_balance - 0.05 * (price_oil[i] - 1.0)
            dPf_dt[i] = 0.01 * fert_balance - 0.05 * (price_fert[i] - 1.0)
            dPw_dt[i] = 0.01 * water_balance - 0.05 * (price_water[i] - 1.0)
            # Resource scarcity increases water price
            dPw_dt[i] += water_scarcity[i] * 0.1

            # Inflation: weighted average of price changes
            dInf_dt[i] = (
                0.3 * dPo_dt[i] / (price_oil[i] + 1e-8)
                + 0.3 * dPf_dt[i] / (price_fert[i] + 1e-8)
                + 0.4 * dPw_dt[i] / (price_water[i] + 1e-8)
            )

            # Interest rate: Taylor rule with target inflation 0.02 (annual rates)
            neutral_rate = 0.03
            inflation_target = 0.02
            dInt_dt[i] += (
                0.5 * (neutral_rate - interest[i])
                + 1.5 * (inflation[i] - inflation_target)
                + 0.5 * (debt[i] - debt_target[i])
            )

            # Exchange rate: influenced by trade balance and capital flows
            trade_balance = (
                (oil_prod[i] - oil_cons[i])
                + (fert_prod[i] - fert_cons[i])
                + (water_avail[i] - water_cons[i])
            )
            dEx_dt[i] += 0.001 * trade_balance - 0.01 * (exchange[i] - 1.0)
            # Currency crisis triggers capital flight (increase outflow)
            dEx_dt[i] += currency_crisis[i] * 0.05 * exchange[i]

            # Bond yield: linked to interest rate plus risk premium
            dBy_dt[i] = 0.1 * (interest[i] + debt_crisis[i] * 0.02 - bond_yield[i])

            # Exchange average: moving average with 30-day time constant
            dExAvg_dt[i] = (exchange[i] - exchange_avg[i]) / 30.0

        # Convert derivatives of log-transformed variables
        EPS = 1e-8
        dlog_oil = dOdt / (1 + oil + EPS)
        dlog_fert = dFdt / (1 + fert + EPS)
        dlog_water = dWdt / (1 + water + EPS)
        dlog_military = dMdt / (1 + military + EPS)
        # Inequality is logit-transformed: d(logit) = dI / (I*(1-I))
        dlogit_inequality = dIdt / (inequality * (1 - inequality) + EPS)
        dlog_debt = dDdt / (1 + debt + EPS)
        dlog_price_oil = dPo_dt / (1 + price_oil + EPS)
        dlog_price_fert = dPf_dt / (1 + price_fert + EPS)
        dlog_price_water = dPw_dt / (1 + price_water + EPS)
        # Inflation and interest are not transformed
        dlog_exchange = dEx_dt / (1 + exchange + EPS)
        dlog_exchange_avg = dExAvg_dt / (1 + exchange_avg + EPS)

        # Assemble full derivative vector
        dydt = np.concatenate(
            [
                dlog_oil,
                dlog_fert,
                dSdt,
                dlog_water,
                dlog_military,
                dlogit_inequality,
                dlog_debt,
                dlog_price_oil,
                dlog_price_fert,
                dlog_price_water,
                dInf_dt,
                dInt_dt,
                dlog_exchange,
                dBy_dt,
                dlog_exchange_avg,
            ]
        )
        return dydt


model = ScaledDebtModel(params)
print("Running 365-day simulation with scaled debt dynamics...")
sol = model.simulate(t_span=(0.0, 365.0), method="BDF", rtol=1e-6, atol=1e-8)
print(f"Success: {sol.success}")
print(f"Time points: {len(sol.t)}")

# Extract final debt
n = model.n_regions
log_debt_final = sol.y[model.idx_log_debt * n : (model.idx_log_debt + 1) * n, -1]
debt_final = np.expm1(np.clip(log_debt_final, -100, 100))
print("\nFinal debt-to-GDP ratios:")
for i in range(n):
    print(f"{model.region_name(i):<30} {debt_final[i]:.3f}")

print(f"\nMax debt: {debt_final.max():.3f}")
print(f"Min debt: {debt_final.min():.3f}")

# Check for explosions
if np.abs(debt_final).max() > 100:
    print("WARNING: Debt exploded!")
else:
    print("Debt seems stable.")
