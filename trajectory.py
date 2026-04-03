"""
Trajectory: structured output from a simulation run.

Wraps the raw scipy solution with named dimensions (time, region,
variable) and automatic inverse-transforms to physical units.
"""

import numpy as np
from typing import Dict, List, Optional

# Import index constants & transforms
from geopolitical_model import (
    N_VARS, REGION_NAMES, VAR_NAMES,
    IDX_LOG_OIL, IDX_LOG_FERT, IDX_LOGIT_STABILITY, IDX_LOG_WATER,
    IDX_LOG_MILITARY, IDX_LOGIT_INEQUALITY, IDX_LOG_DEBT,
    IDX_LOG_PRICE_OIL, IDX_LOG_PRICE_FERT, IDX_LOG_PRICE_WATER,
    IDX_INFLATION, IDX_INTEREST, IDX_LOG_EXCHANGE, IDX_BOND_YIELD,
    IDX_LOG_EXCHANGE_AVG,
    LOG_INDICES, LOGIT_INDICES, RAW_INDICES,
    exp_transform, inv_logit,
)


class Trajectory:
    """Structured wrapper for ODE solution.

    Parameters
    ----------
    t : (T,) array — time points in days
    y : (N_VARS*n_regions, T) array — raw state in transformed space
    n_regions : int
    region_names : list of str
    """

    def __init__(self, t, y, n_regions, region_names=None):
        self.t = t
        self._y_raw = y
        self.n_regions = n_regions
        self.n_vars = N_VARS
        self.region_names = region_names or REGION_NAMES[:n_regions]
        self._cache: Dict[str, np.ndarray] = {}

    @property
    def n_time(self):
        return len(self.t)

    @property
    def days(self):
        return self.t

    # --- Raw block access ------------------------------------------------

    def _raw_block(self, var_idx: int) -> np.ndarray:
        """(n_regions, T) array or a specific variable in transformed space."""
        n = self.n_regions
        return self._y_raw[var_idx * n:(var_idx + 1) * n, :]

    # --- Physical-unit accessors -----------------------------------------

    def _to_physical(self, var_idx: int) -> np.ndarray:
        """Inverse-transform a variable block to physical units."""
        key = var_idx
        if key in self._cache:
            return self._cache[key]
        raw = self._raw_block(var_idx)
        if var_idx in LOG_INDICES:
            result = exp_transform(raw)
        elif var_idx in LOGIT_INDICES:
            result = inv_logit(raw)
        else:
            result = raw.copy()
        self._cache[key] = result
        return result

    def variable(self, name: str) -> np.ndarray:
        """Get (n_regions, T) array for a named variable in physical units.

        *name* must be one of VAR_NAMES (e.g. "oil_stock", "stability", etc.)
        """
        idx = VAR_NAMES.index(name)
        return self._to_physical(idx)

    def region_idx(self, name_or_idx) -> int:
        if isinstance(name_or_idx, int):
            return name_or_idx
        return self.region_names.index(name_or_idx)

    def get(self, var_name: str, region=None) -> np.ndarray:
        """Get time series for a variable, optionally for a single region.

        Returns (T,) if region given, else (n_regions, T).
        """
        data = self.variable(var_name)
        if region is not None:
            ri = self.region_idx(region)
            return data[ri, :]
        return data

    # --- Convenience properties ------------------------------------------

    @property
    def oil_stock(self):     return self._to_physical(IDX_LOG_OIL)
    @property
    def fert_stock(self):    return self._to_physical(IDX_LOG_FERT)
    @property
    def stability(self):     return self._to_physical(IDX_LOGIT_STABILITY)
    @property
    def water_stock(self):   return self._to_physical(IDX_LOG_WATER)
    @property
    def military(self):      return self._to_physical(IDX_LOG_MILITARY)
    @property
    def inequality(self):    return self._to_physical(IDX_LOGIT_INEQUALITY)
    @property
    def debt(self):          return self._to_physical(IDX_LOG_DEBT)
    @property
    def oil_price(self):     return self._to_physical(IDX_LOG_PRICE_OIL)
    @property
    def fert_price(self):    return self._to_physical(IDX_LOG_PRICE_FERT)
    @property
    def water_price(self):   return self._to_physical(IDX_LOG_PRICE_WATER)
    @property
    def inflation(self):     return self._to_physical(IDX_INFLATION)
    @property
    def interest_rate(self): return self._to_physical(IDX_INTEREST)
    @property
    def exchange_rate(self):  return self._to_physical(IDX_LOG_EXCHANGE)
    @property
    def bond_yield(self):    return self._to_physical(IDX_BOND_YIELD)
    @property
    def exchange_avg(self):  return self._to_physical(IDX_LOG_EXCHANGE_AVG)

    # --- Summary ---------------------------------------------------------

    def summary(self) -> str:
        """Print a summary table of final values."""
        lines = []
        lines.append(f"Trajectory: {self.n_time} time points, "
                      f"{self.t[0]:.0f}–{self.t[-1]:.0f} days, "
                      f"{self.n_regions} regions")
        lines.append("")
        header = f"{'Region':<25} {'Oil':>8} {'Fert':>8} {'Stab':>6} {'Debt':>8} {'OilP':>6} {'Inf':>7} {'Int':>7}"
        lines.append(header)
        lines.append("-" * len(header))
        for i in range(self.n_regions):
            lines.append(
                f"{self.region_names[i]:<25} "
                f"{self.oil_stock[i, -1]:>8.1f} "
                f"{self.fert_stock[i, -1]:>8.1f} "
                f"{self.stability[i, -1]:>6.3f} "
                f"{self.debt[i, -1]:>8.3f} "
                f"{self.oil_price[i, -1]:>6.2f} "
                f"{self.inflation[i, -1]:>7.4f} "
                f"{self.interest_rate[i, -1]:>7.4f}"
            )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Comparison utility
# ---------------------------------------------------------------------------

class TrajectoryComparison:
    """Compute and store differences between two trajectories.

    Both trajectories must have the same regions.  Time grids are
    interpolated to a common set of points.
    """

    def __init__(self, baseline: Trajectory, alternative: Trajectory,
                 n_points: int = 200):
        t_lo = max(baseline.t[0], alternative.t[0])
        t_hi = min(baseline.t[-1], alternative.t[-1])
        self.t = np.linspace(t_lo, t_hi, n_points)
        self.baseline = baseline
        self.alternative = alternative
        self.region_names = baseline.region_names

        # Interpolate both to common grid
        self._base_interp = {}
        self._alt_interp = {}
        for name in VAR_NAMES:
            b_data = baseline.get(name)
            a_data = alternative.get(name)
            bi = np.array([np.interp(self.t, baseline.t, b_data[r]) for r in range(baseline.n_regions)])
            ai = np.array([np.interp(self.t, alternative.t, a_data[r]) for r in range(alternative.n_regions)])
            self._base_interp[name] = bi
            self._alt_interp[name] = ai

    def delta(self, var_name: str, region=None) -> np.ndarray:
        """Alternative minus baseline for a variable.

        Returns (T,) if region given, (n_regions, T) otherwise.
        """
        d = self._alt_interp[var_name] - self._base_interp[var_name]
        if region is not None:
            ri = self.baseline.region_idx(region) if isinstance(region, str) else region
            return d[ri]
        return d

    def pct_delta(self, var_name: str, region=None) -> np.ndarray:
        """Percentage change: (alt - base) / (|base| + eps) * 100."""
        b = self._base_interp[var_name]
        d = self._alt_interp[var_name] - b
        pct = d / (np.abs(b) + 1e-10) * 100.0
        if region is not None:
            ri = self.baseline.region_idx(region) if isinstance(region, str) else region
            return pct[ri]
        return pct

    def max_absolute_impact(self, var_name: str) -> dict:
        """Per-region max absolute delta over the time span."""
        d = np.abs(self.delta(var_name))
        result = {}
        for i, rn in enumerate(self.region_names):
            result[rn] = float(d[i].max())
        return result
