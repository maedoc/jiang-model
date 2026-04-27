# Geopolitical Resource Dynamics Model

Welcome to the documentation site for the **Geopolitical Resource Dynamics Model**—a nonlinear dynamical-systems simulator of resource, economic, and political interactions across 12 geopolitical regions.

## What the model does

- Tracks **180 coupled ODEs** (15 state variables × 12 regions)
- Captures feedback loops between **resource stocks**, **political stability**, **inequality**, **sovereign debt**, **commodity prices**, and **financial contagion**
- Designed for **counterfactual analysis**: define a baseline, layer on interventions, and compare trajectories

## Quick start

```bash
python -m venv env && source env/bin/activate
pip install -r requirements.txt
```

```python
from geopolitical_model import GeopoliticalModel, load_parameters

model = GeopoliticalModel(load_parameters())
traj = model.simulate(t_span=(0, 365))
print(traj.summary())
```

## Site map

| Section | Contents |
|---------|----------|
| **Model Specification** | Equations, state variables, thresholds, config parameters |
| **API Reference** | Auto-generated docs for the Python API |
| **Scenarios** | Walk-throughs of Hormuz, Malacca, Panama, sanctions, blockades, multi-chokepoint shocks |
| **Empirical Grounding** | Cross-referencing model outputs against EIA/IEA/CSIS/RAND/ANRPC data; tracking which Game Theory #21 hypotheses are **confirmed**, **partially supported**, or **rejected** |
| **Data Sources** | Condensed data-integration notes |
| **Calibration** | Historical calibration framework (1973, 2008 crises) |
| **Sensitivity Analysis** | Parameter sweeps and Morris screening |

---

*This site is generated from the repository source and kept in sync with the model code.*
