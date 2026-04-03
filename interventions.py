"""
Intervention protocol for the geopolitical ODE model.

An intervention is a callable that modifies system parameters at a given
time during integration.  Interventions are composable—stack several to
model combined shocks.
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional
import numpy as np


@dataclass
class Intervention:
    """A time-resolved modification to model parameters.

    Parameters
    ----------
    name : str
        Human-readable label (for legends / reports).
    apply : callable(t, params) -> params
        Given current time and a *mutable* copy of the parameter dict,
        return the modified dict.  The function may modify in-place and
        return the same dict.
    """
    name: str
    apply: Callable[[float, Dict], Dict]

    def __repr__(self):
        return f"Intervention({self.name!r})"


# ---------------------------------------------------------------------------
# Built-in intervention constructors
# ---------------------------------------------------------------------------

def ramp(t: float, onset: float, duration: float) -> float:
    """Smooth ramp from 0 to 1 starting at *onset* over *duration* days."""
    if t < onset:
        return 0.0
    if duration <= 0:
        return 1.0
    return min(1.0, (t - onset) / duration)


def chokepoint_disruption(
    name: str,
    exporter_region: int,
    onset_day: float = 100.0,
    ramp_days: float = 10.0,
    severity: float = 0.8,
    resources: Optional[List[str]] = None,
) -> Intervention:
    """Disrupt exports from a region (e.g. Hormuz → Middle East idx 3).

    Parameters
    ----------
    name : str
        Label, e.g. "Hormuz closure".
    exporter_region : int
        Region index whose exports are reduced.
    onset_day : float
        Day the disruption begins.
    ramp_days : float
        Days to reach full severity.
    severity : float
        Fraction of exports removed at full ramp (0–1).
    resources : list of str or None
        Which trade matrices to disrupt.
        Default: ["oil_trade_flow", "fertilizer_trade_flow", "water_trade_flow"]
    """
    if resources is None:
        resources = ["oil_trade_flow", "fertilizer_trade_flow", "water_trade_flow"]

    def _apply(t, params):
        factor = 1.0 - severity * ramp(t, onset_day, ramp_days)
        for key in resources:
            if key in params:
                params[key][:, exporter_region] *= factor
        return params

    return Intervention(name=name, apply=_apply)


def bilateral_sanction(
    name: str,
    sender: int,
    receiver: int,
    onset_day: float = 0.0,
    ramp_days: float = 5.0,
    severity: float = 1.0,
    resources: Optional[List[str]] = None,
) -> Intervention:
    """Zero out bilateral trade flow from *sender* to *receiver*.

    Parameters
    ----------
    severity : float
        1.0 = complete embargo; 0.5 = 50% reduction.
    """
    if resources is None:
        resources = ["oil_trade_flow", "fertilizer_trade_flow", "water_trade_flow"]

    def _apply(t, params):
        factor = 1.0 - severity * ramp(t, onset_day, ramp_days)
        for key in resources:
            if key in params:
                params[key][receiver, sender] *= factor
        return params

    return Intervention(name=name, apply=_apply)


def supply_shock(
    name: str,
    region: int,
    resource: str,   # "oil_production" or "fertilizer_production"
    onset_day: float = 0.0,
    ramp_days: float = 5.0,
    severity: float = 0.5,
) -> Intervention:
    """Reduce a region's production capacity."""

    def _apply(t, params):
        factor = 1.0 - severity * ramp(t, onset_day, ramp_days)
        params[resource][region] *= factor
        return params

    return Intervention(name=name, apply=_apply)


def interest_rate_intervention(
    name: str,
    region: int,
    target_rate: float,
    onset_day: float = 0.0,
    ramp_days: float = 30.0,
) -> Intervention:
    """Force a region's interest rate toward a target (central bank policy)."""

    def _apply(t, params):
        r = ramp(t, onset_day, ramp_days)
        # Store the target in a special key the ODE system reads
        if "_interest_rate_overrides" not in params:
            params["_interest_rate_overrides"] = {}
        params["_interest_rate_overrides"][region] = (target_rate, r)
        return params

    return Intervention(name=name, apply=_apply)


def compose_interventions(interventions: List[Intervention]) -> Intervention:
    """Return a single Intervention that applies all *interventions* in order."""

    def _apply(t, params):
        for iv in interventions:
            params = iv.apply(t, params)
        return params

    names = " + ".join(iv.name for iv in interventions)
    return Intervention(name=names, apply=_apply)


# ---------------------------------------------------------------------------
# Pre-built scenarios
# ---------------------------------------------------------------------------

# Region indices (for convenience)
NORTH_AMERICA = 0
EUROPE = 1
RUSSIA = 2
MIDDLE_EAST = 3
CHINA = 4
INDIA = 5
JAPAN = 6
SOUTHEAST_ASIA = 7
AUSTRALIA_NZ = 8
AFRICA = 9
SOUTH_AMERICA = 10
CENTRAL_ASIA = 11


def hormuz_closure(onset_day=100.0, severity=0.8, ramp_days=10.0):
    """Pre-built: Strait of Hormuz closure disrupting Middle East exports."""
    return chokepoint_disruption(
        "Hormuz closure",
        exporter_region=MIDDLE_EAST,
        onset_day=onset_day,
        ramp_days=ramp_days,
        severity=severity,
    )


def malacca_disruption(onset_day=100.0, severity=0.6, ramp_days=14.0):
    """Pre-built: Malacca Strait disruption affecting Southeast Asia."""
    return chokepoint_disruption(
        "Malacca disruption",
        exporter_region=SOUTHEAST_ASIA,
        onset_day=onset_day,
        ramp_days=ramp_days,
        severity=severity,
    )


def russia_oil_embargo(onset_day=0.0, severity=0.9, ramp_days=30.0):
    """Pre-built: Embargo on Russian oil exports."""
    return chokepoint_disruption(
        "Russia oil embargo",
        exporter_region=RUSSIA,
        onset_day=onset_day,
        ramp_days=ramp_days,
        severity=severity,
        resources=["oil_trade_flow"],
    )
