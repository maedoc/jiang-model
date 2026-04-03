"""
Historical calibration framework for geopolitical resource dynamics model.
Calibrates model parameters to historical crisis periods:
- 1973-1975 oil crisis
- 2008-2010 financial crisis
"""

import numpy as np
import pandas as pd
import json
from typing import Dict, List, Tuple
from scipy.optimize import minimize
from ode_model_extended import ExtendedODEModel, load_parameters


class HistoricalCalibrator:
    def __init__(self, base_params: Dict, period: str):
        """
        Initialize calibrator for a specific historical period.

        Args:
            base_params: Base parameter dictionary (real_params.json)
            period: '1973' or '2008'
        """
        self.base_params = base_params.copy()
        self.period = period
        self.n_regions = len(base_params["oil_production"])
        self.region_names = [
            "North America",
            "Europe",
            "Russia",
            "Middle East",
            "China",
            "India",
            "Japan",
            "Southeast Asia",
            "Australia/New Zealand",
            "Africa (sub-Saharan)",
            "South America",
            "Central Asia/Caucasus",
        ]
        self.historical_data = None
        self.target_variables = [
            "oil_price",
            "fertilizer_price",
            "water_price",
            "inflation",
            "interest_rate",
            "exchange_rate",
            "debt_to_gdp",
            "political_stability",
            "inequality",
        ]

    def load_historical_data(self, data_path: str = None):
        """
        Load historical target trajectories from CSV.
        CSV format: columns: region, variable, day, value
        If data_path is None, look for file historical_{period}.csv,
        otherwise generate synthetic data.
        """
        if data_path is None:
            # Try to load pre-generated file
            import os

            default_path = f"historical_{self.period}.csv"
            if os.path.exists(default_path):
                print(f"Loading historical data from {default_path}")
                df = pd.read_csv(default_path)
                self.historical_data = df
            else:
                print(f"File {default_path} not found, generating synthetic data")
                # Generate synthetic data for testing (placeholder)
                self.historical_data = self._generate_synthetic_data()
        else:
            df = pd.read_csv(data_path)
            self.historical_data = df
        return self.historical_data

    def _generate_synthetic_data(self):
        """
        Generate synthetic historical data for the given period.
        Creates realistic patterns based on known crisis characteristics.
        """
        # Determine crisis characteristics
        if self.period == "1973":
            # Oil price spike, stagflation
            days = np.arange(0, 730)  # 2 years
            oil_price_mult = 1.0 + 3.0 * np.exp(
                -0.005 * (days - 100)
            )  # spike then slow decline
            inflation_base = 0.02 + 0.08 * np.exp(-0.003 * (days - 50))
            debt_growth = 0.05 * days / 365  # gradual increase
        elif self.period == "2008":
            # Financial crisis: debt surge, interest rates near zero
            days = np.arange(0, 730)
            oil_price_mult = 1.0 - 0.5 * np.exp(
                -0.01 * (days - 200)
            )  # drop then recovery
            inflation_base = 0.02 - 0.01 * np.exp(-0.005 * (days - 100))
            debt_growth = 0.15 * days / 365  # rapid increase
        else:
            raise ValueError("Period must be '1973' or '2008'")

        # Create DataFrame with all regions and variables
        records = []
        for i, region in enumerate(self.region_names):
            # Regional variation factor
            region_factor = 1.0 + 0.1 * np.sin(i * 0.5)
            for var in self.target_variables:
                if var == "oil_price":
                    baseline = self.base_params["oil_price"][i]
                    values = baseline * oil_price_mult * region_factor
                elif var == "fertilizer_price":
                    baseline = self.base_params["fertilizer_price"][i]
                    values = baseline * (1.0 + 0.5 * oil_price_mult) * region_factor
                elif var == "water_price":
                    baseline = self.base_params["water_price"][i]
                    values = (
                        baseline
                        * (1.0 + 0.1 * np.sin(days / 365 * 2 * np.pi))
                        * region_factor
                    )
                elif var == "inflation":
                    values = inflation_base * region_factor
                elif var == "interest_rate":
                    values = (
                        np.maximum(0.0, 0.03 + 0.02 * np.sin(days / 365 * np.pi))
                        * region_factor
                    )
                elif var == "exchange_rate":
                    baseline = self.base_params["exchange_rate"][i]
                    values = (
                        baseline
                        * (1.0 + 0.1 * np.sin(days / 365 * np.pi + i))
                        * region_factor
                    )
                elif var == "debt_to_gdp":
                    baseline = self.base_params["debt_to_gdp"][i]
                    values = baseline * (1.0 + debt_growth) * region_factor
                elif var == "political_stability":
                    values = 0.7 - 0.2 * np.exp(-0.005 * (days - 150)) * region_factor
                elif var == "inequality":
                    values = 0.4 + 0.1 * np.exp(-0.002 * (days - 200)) * region_factor
                else:
                    continue

                for day_idx, day in enumerate(days):
                    records.append(
                        {
                            "region": region,
                            "variable": var,
                            "day": float(day),
                            "value": values[day_idx],
                        }
                    )

        df = pd.DataFrame(records)
        return df

    def simulate_with_params(self, params: Dict, t_span: Tuple = (0.0, 30.0)):
        """
        Run simulation with given parameter set.
        Returns trajectories of target variables.
        """
        model = ExtendedODEModel(params)
        sol = model.simulate(t_span=t_span, method="BDF", rtol=1e-6, atol=1e-8)

        # Extract trajectories at historical time points
        t_sim = sol.t
        n = self.n_regions

        # Get state variables at each time point
        trajectories = {}
        for var in self.target_variables:
            trajectories[var] = np.zeros((n, len(t_sim)))

        for idx, t in enumerate(t_sim):
            y = sol.y[:, idx]
            # Use model's extract_state to get variables
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
            ) = model.extract_state(y)

            # Convert to original units
            from ode_model_extended import exp_transform, inv_logit

            price_oil = exp_transform(log_price_oil)
            price_fert = exp_transform(log_price_fert)
            price_water = exp_transform(log_price_water)
            exchange = exp_transform(log_exchange)
            debt = exp_transform(log_debt)
            inequality = inv_logit(logit_inequality)

            # Store
            trajectories["oil_price"][:, idx] = price_oil
            trajectories["fertilizer_price"][:, idx] = price_fert
            trajectories["water_price"][:, idx] = price_water
            trajectories["inflation"][:, idx] = inflation
            trajectories["interest_rate"][:, idx] = interest
            trajectories["exchange_rate"][:, idx] = exchange
            trajectories["debt_to_gdp"][:, idx] = debt
            trajectories["political_stability"][:, idx] = stability
            trajectories["inequality"][:, idx] = inequality

        trajectories["_t"] = t_sim
        return trajectories

    def compute_loss(self, simulated_traj, historical_df):
        """
        Compute RMSE loss between simulated and historical trajectories.
        """
        loss = 0.0
        n_points = 0

        # For each region and variable, interpolate simulated values at historical days
        for region_idx, region in enumerate(self.region_names):
            region_mask = historical_df["region"] == region
            for var in self.target_variables:
                var_mask = historical_df["variable"] == var
                mask = region_mask & var_mask
                if not mask.any():
                    continue

                hist_subset = historical_df[mask]
                days_hist = hist_subset["day"].values
                values_hist = hist_subset["value"].values

                # Get simulated trajectory for this region and variable
                sim_var = simulated_traj[var][region_idx, :]
                t_sim = simulated_traj["_t"]  # we'll store simulation time separately

                # Interpolate simulated values at historical days
                from scipy.interpolate import interp1d

                if len(t_sim) > 1:
                    f = interp1d(
                        t_sim, sim_var, bounds_error=False, fill_value="extrapolate"
                    )
                    values_sim = f(days_hist)
                else:
                    values_sim = np.full_like(values_hist, sim_var[0])

                # RMSE contribution
                diff = values_sim - values_hist
                # Weight by variable importance
                weight = 1.0
                if var in ["oil_price", "debt_to_gdp"]:
                    weight = 2.0
                loss += weight * np.sum(diff**2)
                n_points += len(diff)

        if n_points == 0:
            return 1e9
        return np.sqrt(loss / n_points)

    def optimize_parameters(
        self, param_names: List[str], bounds: Dict = None, method="L-BFGS-B", maxiter=50
    ):
        """
        Optimize selected parameters to minimize loss.

        Args:
            param_names: List of parameter names to optimize
            bounds: Dict mapping param_name to (min, max) tuple
            method: Optimization method
            maxiter: Maximum iterations
        """
        # Default bounds
        if bounds is None:
            bounds = {}
            for p in param_names:
                if "coupling" in p:
                    bounds[p] = (0.0, 2.0)
                elif "decay" in p or "rate" in p:
                    bounds[p] = (0.001, 0.5)
                elif "price" in p:
                    bounds[p] = (0.5, 2.0)
                else:
                    bounds[p] = (0.5, 1.5)  # +/- 50% of baseline

        # Load historical data if not already loaded
        if self.historical_data is None:
            self.load_historical_data()

        # Flatten parameter vector for optimization
        param_shapes = {}
        param_values = []
        for p in param_names:
            val = self.base_params[p]
            param_shapes[p] = val.shape
            param_values.append(val.flatten())
        x0 = np.concatenate(param_values)

        # Define objective function
        def objective(x):
            # Reconstruct parameter dictionary
            params = self.base_params.copy()
            idx = 0
            for p in param_names:
                shape = param_shapes[p]
                size = np.prod(shape)
                val = x[idx : idx + size].reshape(shape)
                params[p] = val
                idx += size

            # Run simulation
            trajectories = self.simulate_with_params(params)

            # Compute loss
            loss = self.compute_loss(trajectories, self.historical_data)
            print(f"Loss: {loss:.6f}")
            return loss

        # Define bounds for each parameter
        opt_bounds = []
        for p in param_names:
            shape = param_shapes[p]
            size = np.prod(shape)
            min_val, max_val = bounds.get(p, (0.5, 1.5))
            for _ in range(size):
                opt_bounds.append((min_val, max_val))

        # Run optimization
        result = minimize(
            objective,
            x0,
            method=method,
            bounds=opt_bounds,
            options={"maxiter": maxiter, "disp": True},
        )

        # Reconstruct optimized parameters
        optimized_params = self.base_params.copy()
        idx = 0
        for p in param_names:
            shape = param_shapes[p]
            size = np.prod(shape)
            val = result.x[idx : idx + size].reshape(shape)
            optimized_params[p] = val
            idx += size

        return optimized_params, result

    def save_calibrated_params(self, params: Dict, filename: str):
        """Save calibrated parameters to JSON file."""
        # Convert numpy arrays to lists
        save_dict = {}
        for key, val in params.items():
            if isinstance(val, np.ndarray):
                save_dict[key] = val.tolist()
            else:
                save_dict[key] = val

        with open(filename, "w") as f:
            json.dump(save_dict, f, indent=2)

        print(f"Calibrated parameters saved to {filename}")


def main():
    """Example calibration workflow."""
    print("Loading base parameters...")
    params = load_parameters("real_params.json")

    # Calibrate for 1973 oil crisis
    print("\n=== Calibrating for 1973 oil crisis ===")
    calibrator_1973 = HistoricalCalibrator(params, "1973")
    calibrator_1973.load_historical_data()  # synthetic data

    # Select parameters to calibrate
    param_names = [
        "stability_coupling",
        "capital_flow",
        "financial_coupling",
        "debt_to_gdp",  # initial debt
    ]

    # Run optimization (limited iterations for demonstration)
    optimized_params, result = calibrator_1973.optimize_parameters(
        param_names, maxiter=10
    )

    # Save calibrated parameters
    calibrator_1973.save_calibrated_params(optimized_params, "params_1973.json")

    # Calibrate for 2008 financial crisis
    print("\n=== Calibrating for 2008 financial crisis ===")
    calibrator_2008 = HistoricalCalibrator(params, "2008")
    calibrator_2008.load_historical_data()

    optimized_params_2008, result_2008 = calibrator_2008.optimize_parameters(
        param_names, maxiter=10
    )

    calibrator_2008.save_calibrated_params(optimized_params_2008, "params_2008.json")

    print("\nCalibration complete!")
    print("Calibrated parameter sets saved as params_1973.json and params_2008.json")


if __name__ == "__main__":
    main()
