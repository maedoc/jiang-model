"""
Historical calibration framework for the geopolitical ODE model.

Calibrates model parameters to historical crisis periods using
the new GeopoliticalModel / Trajectory infrastructure.
"""

import numpy as np
import pandas as pd
import json
from typing import Dict, List, Optional, Tuple
from scipy.optimize import minimize
from scipy.interpolate import interp1d

from geopolitical_model import GeopoliticalModel, load_parameters, REGION_NAMES
from model_config import ModelConfig
from trajectory import Trajectory, VAR_NAMES


# Variable mapping: calibration target name → Trajectory accessor
TARGET_VAR_MAP = {
    "oil_price": "oil_price",
    "fertilizer_price": "fertilizer_price",
    "water_price": "water_price",
    "inflation": "inflation",
    "interest_rate": "interest_rate",
    "exchange_rate": "exchange_rate",
    "debt_to_gdp": "debt_gdp",
    "political_stability": "stability",
    "inequality": "inequality",
}


class HistoricalCalibrator:
    """Calibrate model parameters to match historical target trajectories.

    Parameters
    ----------
    base_params : dict
        Base parameter dictionary (from load_parameters).
    period : str
        Crisis label ('1973', '2008', or custom).
    config : ModelConfig, optional
        Structural coefficients.
    weights : dict, optional
        Per-variable loss weights.  Default: oil_price and debt_to_gdp
        get weight 2.0, others 1.0.
    regularization : float
        L2 penalty on parameter deviation from base (0 = none).
    """

    def __init__(
        self,
        base_params: Dict,
        period: str,
        config: Optional[ModelConfig] = None,
        weights: Optional[Dict[str, float]] = None,
        regularization: float = 0.01,
    ):
        self.base_params = {
            k: np.array(v, dtype=np.float64) if not isinstance(v, np.ndarray) else v.copy()
            for k, v in base_params.items()
        }
        self.period = period
        self.config = config or ModelConfig()
        self.n_regions = len(base_params["oil_production"])
        self.region_names = REGION_NAMES[: self.n_regions]
        self.historical_data: Optional[pd.DataFrame] = None
        self.regularization = regularization

        self.target_variables = list(TARGET_VAR_MAP.keys())

        self.weights = weights or {
            "oil_price": 2.0,
            "debt_to_gdp": 2.0,
        }

    # --- Data loading ----------------------------------------------------

    def load_historical_data(self, data_path: Optional[str] = None) -> pd.DataFrame:
        """Load historical CSV or generate synthetic data.

        CSV format: columns ``region, variable, day, value``
        """
        import os

        if data_path is None:
            default_path = f"historical_{self.period}.csv"
            if os.path.exists(default_path):
                df = pd.read_csv(default_path)
            else:
                df = self._generate_synthetic_data()
        else:
            df = pd.read_csv(data_path)

        self.historical_data = df
        return df

    def _generate_synthetic_data(self) -> pd.DataFrame:
        """Generate synthetic historical target data for testing."""
        days = np.arange(0, 730, dtype=float)

        if self.period == "1973":
            oil_mult = 1.0 + 3.0 * np.exp(-0.005 * np.maximum(days - 100, 0))
            infl_base = 0.02 + 0.08 * np.exp(-0.003 * np.maximum(days - 50, 0))
            debt_growth = 0.05 * days / 365
        elif self.period == "2008":
            oil_mult = 1.0 - 0.5 * np.exp(-0.01 * np.maximum(days - 200, 0))
            infl_base = 0.02 - 0.01 * np.exp(-0.005 * np.maximum(days - 100, 0))
            debt_growth = 0.15 * days / 365
        else:
            oil_mult = np.ones_like(days)
            infl_base = np.full_like(days, 0.02)
            debt_growth = np.zeros_like(days)

        records = []
        for i, region in enumerate(self.region_names):
            rf = 1.0 + 0.1 * np.sin(i * 0.5)
            for var in self.target_variables:
                if var == "oil_price":
                    vals = self.base_params["oil_price"][i] * oil_mult * rf
                elif var == "fertilizer_price":
                    vals = self.base_params["fertilizer_price"][i] * (1 + 0.5 * oil_mult) * rf
                elif var == "water_price":
                    vals = self.base_params["water_price"][i] * (1 + 0.1 * np.sin(days / 365 * 2 * np.pi)) * rf
                elif var == "inflation":
                    vals = infl_base * rf
                elif var == "interest_rate":
                    vals = np.maximum(0, 0.03 + 0.02 * np.sin(days / 365 * np.pi)) * rf
                elif var == "exchange_rate":
                    vals = self.base_params["exchange_rate"][i] * (1 + 0.1 * np.sin(days / 365 * np.pi + i)) * rf
                elif var == "debt_to_gdp":
                    vals = self.base_params["debt_to_gdp"][i] * (1 + debt_growth) * rf
                elif var == "political_stability":
                    vals = np.clip(0.7 - 0.2 * np.exp(-0.005 * np.maximum(days - 150, 0)) * rf, 0.05, 0.95)
                elif var == "inequality":
                    vals = np.clip(0.4 + 0.1 * np.exp(-0.002 * np.maximum(days - 200, 0)) * rf, 0.05, 0.95)
                else:
                    continue

                for d, v in zip(days, vals):
                    records.append({"region": region, "variable": var, "day": d, "value": v})

        return pd.DataFrame(records)

    # --- Simulation ------------------------------------------------------

    def simulate_with_params(
        self, params: Dict, t_span: Tuple = (0, 30),
    ) -> Trajectory:
        """Run model with given parameters and return Trajectory."""
        model = GeopoliticalModel(params, self.config)
        return model.simulate(t_span=t_span)

    # --- Loss computation ------------------------------------------------

    def compute_loss(self, traj: Trajectory, historical_df: pd.DataFrame) -> float:
        """Weighted RMSE between simulated trajectory and historical targets."""
        loss = 0.0
        n_points = 0

        for region_idx, region in enumerate(self.region_names):
            rmask = historical_df["region"] == region
            for var in self.target_variables:
                vmask = historical_df["variable"] == var
                mask = rmask & vmask
                if not mask.any():
                    continue

                hist = historical_df[mask]
                days_hist = hist["day"].values
                vals_hist = hist["value"].values

                traj_name = TARGET_VAR_MAP.get(var)
                if traj_name is None:
                    continue
                sim_data = traj.get(traj_name, region_idx)

                if len(traj.t) > 1:
                    f = interp1d(traj.t, sim_data, bounds_error=False, fill_value="extrapolate")
                    vals_sim = f(days_hist)
                else:
                    vals_sim = np.full_like(vals_hist, sim_data[0])

                w = self.weights.get(var, 1.0)
                loss += w * np.sum((vals_sim - vals_hist) ** 2)
                n_points += len(vals_hist)

        return np.sqrt(loss / max(n_points, 1))

    # --- Optimisation ----------------------------------------------------

    def optimize_parameters(
        self,
        param_names: List[str],
        bounds: Optional[Dict[str, Tuple[float, float]]] = None,
        method: str = "L-BFGS-B",
        maxiter: int = 50,
        t_span: Tuple = (0, 30),
        verbose: bool = True,
    ) -> Tuple[Dict, object]:
        """Optimise selected parameters to minimise calibration loss.

        Returns (optimised_params, scipy OptimizeResult).
        """
        if bounds is None:
            bounds = {}
            for p in param_names:
                if "coupling" in p or "flow" in p:
                    bounds[p] = (0.0, 5.0)
                elif "decay" in p or "rate" in p:
                    bounds[p] = (0.001, 1.0)
                else:
                    bounds[p] = (0.01, 3.0)

        if self.historical_data is None:
            self.load_historical_data()

        shapes = {}
        x_parts = []
        for p in param_names:
            v = self.base_params[p]
            shapes[p] = v.shape
            x_parts.append(v.flatten())
        x0 = np.concatenate(x_parts)
        x_base = x0.copy()

        opt_bounds = []
        for p in param_names:
            lo, hi = bounds[p]
            for _ in range(int(np.prod(shapes[p]))):
                opt_bounds.append((lo, hi))

        call_count = [0]

        def objective(x):
            params = {k: v.copy() for k, v in self.base_params.items()}
            idx = 0
            for p in param_names:
                sz = int(np.prod(shapes[p]))
                params[p] = x[idx:idx + sz].reshape(shapes[p])
                idx += sz

            traj = self.simulate_with_params(params, t_span=t_span)
            data_loss = self.compute_loss(traj, self.historical_data)
            reg_loss = self.regularization * np.sqrt(np.mean((x - x_base) ** 2))
            total = data_loss + reg_loss
            call_count[0] += 1
            if verbose and call_count[0] % 5 == 0:
                print(f"  iter {call_count[0]}: loss={total:.6f} (data={data_loss:.6f} reg={reg_loss:.6f})")
            return total

        result = minimize(objective, x0, method=method, bounds=opt_bounds,
                          options={"maxiter": maxiter, "disp": verbose})

        opt_params = {k: v.copy() for k, v in self.base_params.items()}
        idx = 0
        for p in param_names:
            sz = int(np.prod(shapes[p]))
            opt_params[p] = result.x[idx:idx + sz].reshape(shapes[p])
            idx += sz

        return opt_params, result

    # --- I/O -------------------------------------------------------------

    def save_calibrated_params(self, params: Dict, filename: str):
        save_dict = {}
        for key, val in params.items():
            save_dict[key] = val.tolist() if isinstance(val, np.ndarray) else val
        with open(filename, "w") as f:
            json.dump(save_dict, f, indent=2)
