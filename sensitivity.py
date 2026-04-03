"""
Sensitivity analysis toolkit for the geopolitical ODE model.

Provides Morris one-at-a-time (OAT) elementary effects method and
parameter sweep utilities to identify which structural coefficients
and regional parameters the model is most sensitive to.
"""

import numpy as np
from typing import Callable, Dict, List, Optional, Tuple
from dataclasses import fields

from model_config import ModelConfig
from geopolitical_model import GeopoliticalModel, load_parameters
from trajectory import Trajectory


def _extract_scalar_metric(traj: Trajectory, metric: str = "avg_stability") -> float:
    """Reduce a trajectory to a single scalar for comparison."""
    if metric == "avg_stability":
        return float(traj.stability[:, -1].mean())
    elif metric == "avg_debt":
        return float(traj.debt[:, -1].mean())
    elif metric == "avg_oil_price":
        return float(traj.oil_price[:, -1].mean())
    elif metric == "total_oil":
        return float(traj.oil_stock[:, -1].sum())
    elif metric == "max_debt":
        return float(traj.debt[:, -1].max())
    elif metric == "min_stability":
        return float(traj.stability[:, -1].min())
    else:
        raise ValueError(f"Unknown metric: {metric}")


# ---------------------------------------------------------------------------
# Parameter sweep
# ---------------------------------------------------------------------------

def parameter_sweep(
    param_name: str,
    values: np.ndarray,
    params_file: str = "real_params.json",
    base_config: Optional[ModelConfig] = None,
    t_span: Tuple[float, float] = (0.0, 365.0),
    metric: str = "avg_stability",
    interventions=None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Sweep a single ModelConfig parameter over a range of values.

    Returns (values, metric_values).
    """
    base_cfg = base_config or ModelConfig()
    params = load_parameters(params_file)
    results = []

    for v in values:
        cfg = ModelConfig(**{**base_cfg.to_dict(), param_name: v})
        model = GeopoliticalModel(params, cfg, interventions or [])
        traj = model.simulate(t_span=t_span)
        results.append(_extract_scalar_metric(traj, metric))

    return values, np.array(results)


# ---------------------------------------------------------------------------
# Morris elementary effects
# ---------------------------------------------------------------------------

def morris_screening(
    param_names: List[str],
    n_trajectories: int = 10,
    delta: float = 0.1,
    params_file: str = "real_params.json",
    base_config: Optional[ModelConfig] = None,
    t_span: Tuple[float, float] = (0.0, 365.0),
    metric: str = "avg_stability",
    interventions=None,
    seed: int = 42,
) -> Dict[str, Dict[str, float]]:
    """Morris method screening for parameter importance.

    For each parameter, computes the elementary effect (EE) by perturbing
    it by ±delta fraction and measuring the metric change.

    Returns dict[param_name] → {"mu": mean EE, "mu_star": mean |EE|, "sigma": std EE}
    """
    rng = np.random.default_rng(seed)
    base_cfg = base_config or ModelConfig()
    base_dict = base_cfg.to_dict()
    params = load_parameters(params_file)

    # Filter to numeric parameters
    numeric_params = []
    for name in param_names:
        val = base_dict.get(name)
        if val is not None and isinstance(val, (int, float)) and not isinstance(val, bool):
            numeric_params.append(name)

    effects = {name: [] for name in numeric_params}

    # Compute base simulation once (same for all trajectories since base_dict is fixed)
    import warnings
    cfg_base = ModelConfig(**base_dict)
    model_base = GeopoliticalModel(params, cfg_base, interventions or [])
    traj_base = model_base.simulate(t_span=t_span)
    y_base = _extract_scalar_metric(traj_base, metric)

    for _ in range(n_trajectories):
        for pname in numeric_params:
            base_val = base_dict[pname]
            if abs(base_val) < 1e-12:
                continue

            sign = rng.choice([-1.0, 1.0])
            perturbed_val = base_val * (1.0 + sign * delta)

            # Run perturbed
            perturbed_dict = {**base_dict, pname: perturbed_val}
            cfg_pert = ModelConfig(**perturbed_dict)
            model_pert = GeopoliticalModel(params, cfg_pert, interventions or [])
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                traj_pert = model_pert.simulate(t_span=t_span)
            y_pert = _extract_scalar_metric(traj_pert, metric)

            ee = (y_pert - y_base) / (sign * delta * base_val) if abs(base_val) > 1e-12 else 0.0
            effects[pname].append(ee)

    # Aggregate
    result = {}
    for pname, ees in effects.items():
        if len(ees) == 0:
            continue
        arr = np.array(ees)
        result[pname] = {
            "mu": float(arr.mean()),
            "mu_star": float(np.abs(arr).mean()),
            "sigma": float(arr.std()),
        }

    return result


# ---------------------------------------------------------------------------
# Regional parameter sensitivity
# ---------------------------------------------------------------------------

def regional_parameter_sweep(
    param_key: str,
    region_idx: int,
    multipliers: np.ndarray,
    params_file: str = "real_params.json",
    config: Optional[ModelConfig] = None,
    t_span: Tuple[float, float] = (0.0, 365.0),
    metric: str = "avg_stability",
    interventions=None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Sweep a regional parameter (e.g. oil_production for region 3).

    multipliers: array of factors to multiply the base value by.
    """
    base_params = load_parameters(params_file)
    cfg = config or ModelConfig()
    base_val = base_params[param_key][region_idx]
    results = []

    for m in multipliers:
        params = load_parameters(params_file)
        params[param_key][region_idx] = base_val * m
        model = GeopoliticalModel(params, cfg, interventions or [])
        traj = model.simulate(t_span=t_span)
        results.append(_extract_scalar_metric(traj, metric))

    return multipliers, np.array(results)
