"""
Scenario runner: define, execute, and compare geopolitical scenarios.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np

from model_config import ModelConfig
from geopolitical_model import GeopoliticalModel, load_parameters
from interventions import Intervention
from trajectory import Trajectory, TrajectoryComparison


@dataclass
class Scenario:
    """Bundle of parameters + interventions + simulation config.

    Parameters
    ----------
    name : str
        Human-readable label.
    params_file : str
        Path to parameter JSON.
    interventions : list of Intervention
        Time-dependent modifications.
    config : ModelConfig or None
        Structural coefficients (defaults if None).
    t_span : tuple
        Integration interval in days.
    """
    name: str
    params_file: str = "real_params.json"
    interventions: List[Intervention] = field(default_factory=list)
    config: Optional[ModelConfig] = None
    t_span: Tuple[float, float] = (0.0, 365.0)
    t_eval: Optional[np.ndarray] = None


def run_scenario(scenario: Scenario) -> Trajectory:
    """Execute a scenario and return a Trajectory."""
    params = load_parameters(scenario.params_file)
    cfg = scenario.config or ModelConfig()
    model = GeopoliticalModel(params, cfg, scenario.interventions)
    return model.simulate(
        t_span=scenario.t_span,
        t_eval=scenario.t_eval,
    )


def compare_scenarios(
    baseline: Scenario,
    alternative: Scenario,
    n_points: int = 200,
) -> Tuple[Trajectory, Trajectory, TrajectoryComparison]:
    """Run two scenarios and compute their difference.

    Returns (baseline_traj, alternative_traj, comparison).
    """
    traj_base = run_scenario(baseline)
    traj_alt = run_scenario(alternative)
    comparison = TrajectoryComparison(traj_base, traj_alt, n_points)
    return traj_base, traj_alt, comparison
