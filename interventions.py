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


def hormuz_closure(onset_day=100.0, severity=0.75, ramp_days=10.0):
    """Pre-built: Strait of Hormuz closure disrupting Middle East exports.

    Empirical severity bounds (EIA/IEA/CSIS 2024-2026):
    - Full closure reduces oil flow by ~83% (20 -> 3.8 mb/d).
    - Bypass pipelines cover only 17-27% of normal flow.
    - AIS data shows 91.5% vessel-traffic reduction during crisis.
    - Even partial/asymmetric disruption triggers insurance-driven
      avoidance at much lower physical severity.
    """
    return chokepoint_disruption(
        "Hormuz closure",
        exporter_region=MIDDLE_EAST,
        onset_day=onset_day,
        ramp_days=ramp_days,
        severity=severity,
    )


def malacca_disruption(onset_day=100.0, severity=0.75, ramp_days=14.0):
    """Pre-built: Malacca Strait disruption affecting Southeast Asia.

    Empirical severity bounds (EIA 2024, ANRPC 1H2025):
    - Malacca carries ~22.5-23.7 mb/d, ~28-30% of world maritime oil trade.
    - China receives ~7.9 mb/d (~48% of imports) via this route.
    - No practical alternative for Middle East->Asia routing.
    - Full closure would trap ~60-70% of China's oil imports.
    """
    return chokepoint_disruption(
        "Malacca disruption",
        exporter_region=SOUTHEAST_ASIA,
        onset_day=onset_day,
        ramp_days=ramp_days,
        severity=severity,
    )


def russia_oil_embargo(onset_day=0.0, severity=0.85, ramp_days=30.0):
    """Pre-built: Embargo on Russian oil exports.

    Empirical basis: 2022 EU sanctions achieved ~60-70% reduction in
    Russian oil exports to Europe; full embargo modeled at 85% severity.
    """
    return chokepoint_disruption(
        "Russia oil embargo",
        exporter_region=RUSSIA,
        onset_day=onset_day,
        ramp_days=ramp_days,
        severity=severity,
        resources=["oil_trade_flow"],
    )


def panama_disruption(onset_day=100.0, severity=0.55, ramp_days=14.0):
    """Pre-built: Panama Canal disruption affecting South America exports.

    Empirical severity bounds (EIA 2024, Gulf News Apr 2026):
    - Normal throughput ~2.0-2.3 mb/d crude (~2.5-3% of seaborne oil).
    - But >95% of US LPG exports to Asia transit the canal.
    - Canal currently surging to 36-38 transits/day amid Hormuz crisis.
    - Disruption affects LNG/LPG rerouting more than crude volume.
    """
    return chokepoint_disruption(
        "Panama disruption",
        exporter_region=SOUTH_AMERICA,
        onset_day=onset_day,
        ramp_days=ramp_days,
        severity=severity,
    )


def naval_blockade(
    sender: int = MIDDLE_EAST,
    receiver: int = CHINA,
    onset_day: float = 100.0,
    severity: float = 0.8,
    ramp_days: float = 10.0,
    resources: Optional[List[str]] = None,
) -> Intervention:
    """Pre-built: naval interdiction of bilateral trade (default ME → China).

    Empirical severity bounds (Tanker War 1984-88, RAND RRA591-1, Red Sea 2023-24):
    - Tanker War: ~50-60% export reduction via insurance/fear; physical
      damage only ~2-4% of flows but traffic avoidance was near-total.
    - Red Sea: 42% Suez transit drop, 60-70% container diversion.
    - RAND distant blockade of China: "dramatically reduced" waterborne
      shipping, estimated 10-35% China GDP decline.
    - Insurance markets react within days; full effect in 1-4 weeks.
    """
    if resources is None:
        resources = ["oil_trade_flow", "fertilizer_trade_flow"]
    return bilateral_sanction(
        "Naval blockade (ME→China)",
        sender=sender,
        receiver=receiver,
        onset_day=onset_day,
        ramp_days=ramp_days,
        severity=severity,
        resources=resources,
    )


def multi_region_supply_shock(
    name: str,
    regions: List[int],
    resource: str = "oil_production",
    onset_day: float = 0.0,
    ramp_days: float = 5.0,
    severity: float = 0.3,
) -> Intervention:
    """Reduce production capacity in multiple regions simultaneously."""

    def _apply(t, params):
        factor = 1.0 - severity * ramp(t, onset_day, ramp_days)
        if resource in params:
            for ri in regions:
                params[resource][ri] *= factor
        return params

    return Intervention(name=name, apply=_apply)


def global_refinery_sabotage(
    onset_day: float = 30.0,
    severity: float = 0.20,
    ramp_days: float = 15.0,
) -> Intervention:
    """Pre-built: widespread sabotage/fires hitting global refinery capacity.

    Empirical severity bounds (IEA OMR Apr 2026, Energy Institute 2024):
    - IEA observed a 2.6 mb/d downward global supply swing during the
      Hormuz crisis (~2.5% of global supply). This is the empirical
      ceiling for a plausible multi-region sabotage event.
    - Global refinery capacity = ~103.5 mb/d; a 2.5% outage = ~2.6 mb/d.
    - GT#21 claims "50 refinery fires in 45 days" - this could NOT be
      independently verified. Use the IEA empirical ceiling as the
      upper bound for model plausibility.
    - Affected regions: Russia, Middle East, Europe, India, SE Asia,
      Australia (major refining hubs per Energy Institute data).
    """
    return multi_region_supply_shock(
        "Global refinery sabotage",
        regions=[RUSSIA, MIDDLE_EAST, EUROPE, INDIA, SOUTHEAST_ASIA, AUSTRALIA_NZ],
        resource="oil_production",
        onset_day=onset_day,
        ramp_days=ramp_days,
        severity=severity,
    )
