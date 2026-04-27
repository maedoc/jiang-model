# MkDocs Site Plan: Geopolitical Resource Dynamics Model

## Objective

Build a static documentation site documenting everything: model equations, state variables, configuration parameters, all explored scenarios, and a dedicated section tracking which empirical hypotheses from Game Theory #21 are confirmed, partially supported, or rejected by model output.

## Site Structure (nav)

```yaml
nav:
  - Home: index.md

  - Model Specification:
    - Overview: model/overview.md
    - Regions & State Variables: model/variables.md
    - Mathematical Specification: model/equations.md
    - Nonlinear Thresholds: model/thresholds.md
    - ModelConfig Parameters: model/config.md
    - Regional Parameters: model/regional_params.md

  - API Reference:
    - Core Model: api/geopolitical_model.md
    - Interventions: api/interventions.md
    - Trajectory & Comparison: api/trajectory.md
    - Scenarios: api/scenarios.md
    - Sensitivity & Calibration: api/sensitivity.md
    - Data Loading: api/data_loader.md

  - Scenarios:
    - Overview: scenarios/overview.md
    - Hormuz Strait Closure: scenarios/hormuz.md
    - Malacca Strait Disruption: scenarios/malacca.md
    - Panama Canal Disruption: scenarios/panama.md
    - Russia Oil Embargo: scenarios/russia_embargo.md
    - Bilateral Sanctions: scenarios/sanctions.md
    - Price-Mediated Trade: scenarios/price_trade.md
    - Multi-Chokepoint (GT#21): scenarios/multi_chokepoint.md
    - Naval Blockade (GT#21): scenarios/naval_blockade.md
    - Global Refinery Sabotage: scenarios/refinery_sabotage.md

  - Empirical Grounding:
    - Overview: empirical/overview.md
    - Chokepoint Throughput Data: empirical/chokepoints.md
    - Naval Blockade Precedents: empirical/blockades.md
    - Defense Spending & War Economy: empirical/defense.md
    - Production & Consumption Balances: empirical/energy_balances.md
    - Refinery Capacity Data: empirical/refineries.md
    - Confirmed Hypotheses: empirical/confirmed.md
    - Partially Supported: empirical/partial.md
    - Rejected / Unverified: empirical/rejected.md

  - Data Sources: data_sources.md
  - Calibration: calibration.md
  - Sensitivity Analysis: sensitivity.md
  - Research Briefs: research_briefs.md
  - Game Theory Transcripts: transcripts.md
```

## Theme & Plugins

```yaml
theme:
  name: material
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: indigo
      accent: indigo
  features:
    - navigation.tabs        # top-level tabs
    - navigation.sections    # section index pages
    - navigation.top         # back-to-top button
    - content.code.copy      # copy button on code blocks
    - content.tabs.link      # sync tab groups

plugins:
  - search
  - mkdocstrings:            # auto-generate Python API docs
      handlers:
        python:
          options:
            show_source: true
            show_root_heading: true
            docstring_style: numpy
  - mkdocs-jupyter:          # render Jupyter notebooks if any
  - table-reader:            # read CSV/JSON as tables
  - glightbox:               # lightbox for images

markdown_extensions:
  - pymdownx.arithmatex:     # LaTeX equation rendering
      generic: true
  - pymdownx.superfences     # nested fenced code blocks
  - pymdownx.tabbed          # content tabs
  - pymdownx.details         # collapsible admonitions
  - admonition               # note/warning/tip blocks
  - toc:
      permalink: true

extra_javascript:
  - javascripts/mathjax.js   # MathJax config
extra_css:
  - stylesheets/extra.css    # custom overrides
```

## Page Content Mapped to Source Files

| MkDocs Page | Source Material | Key Contents |
|---|---|---|
| `model/overview.md` | `README.md` | 12-region model, 180 ODEs, purpose (counterfactual analysis), quick-start code |
| `model/variables.md` | `MATH_SPEC.md` §1, `geopolitical_model.py` IDs | 15 variables per region, transforms (log, logit), region table |
| `model/equations.md` | `MATH_SPEC.md` §2–5 | Full equation set with LaTeX rendering (reuse and expand from MATH_SPEC.md with more explanation) |
| `model/thresholds.md` | `MATH_SPEC.md` §5, `model_config.py` | Debt crisis, currency crisis, social unrest, water scarcity — trigger parameters and sigmoid formulas |
| `model/config.md` | `model_config.py` docstrings | All ~60 coefficients with names, defaults, descriptions. Auto-generated via mkdocstrings |
| `model/regional_params.md` | `real_params.json` schema | Per-region parameters (oil/fertilizer production, initial stocks, trade matrix structure) |
| `api/geopolitical_model.md` | `geopolitical_model.py` | `GeopoliticalModel` class, `simulate()`, `load_parameters()`, region/variable constants |
| `api/interventions.md` | `interventions.py` | `Intervention` dataclass, constructors (`chokepoint_disruption`, `bilateral_sanction`, `supply_shock`), pre-built scenarios |
| `api/trajectory.md` | `trajectory.py` | `Trajectory`, `TrajectoryComparison` — variable access, inverse transforms, impact ranking |
| `api/scenarios.md` | `scenarios.py` | `Scenario`, `run_scenario`, `compare_scenarios` |
| `api/sensitivity.md` | `sensitivity.py` | `parameter_sweep`, `morris_screening` |
| `api/data_loader.md` | `data_loader.py` | Country→region mapping, CSV loading, data aggregation |

| MkDocs Page | Source Material | Key Contents |
|---|---|---|
| `scenarios/hormuz.md` | `example_hormuz.py`, research brief §1.1 | Scenario description, intervention params, output figures, empirical grounding (EIA: 83% flow reduction) |
| `scenarios/malacca.md` | `interventions.py`, research brief §1.2 | Same pattern for Malacca (ANRPC: 28–30% of maritime oil) |
| `scenarios/panama.md` | `interventions.py`, research brief §1.3 | Panama (EIA: ~2.5–3% of seaborne oil, >95% US LPG) |
| `scenarios/russia_embargo.md` | `example_sanctions.py`, research brief | Russia oil embargo |
| `scenarios/sanctions.md` | `example_sanctions.py` | EU–Russia bilateral sanctions, compound scenarios |
| `scenarios/price_trade.md` | `example_price_trade.py` | Fixed vs price-mediated trade comparison |
| `scenarios/multi_chokepoint.md` | `example_multi_chokepoint.py`, research brief | Compound Hormuz+Malacca+Panama, China impact dashboard |
| `scenarios/naval_blockade.md` | `example_naval_blockade.py`, research brief §2 | ME→China and ME+RU→China blockades |
| `scenarios/refinery_sabotage.md` | `interventions.py`, research brief §4 | Global refinery sabotage, IEA empirical ceiling |

| MkDocs Page | Source Material | Key Contents |
|---|---|---|
| `empirical/chokepoints.md` | Research brief §1 | EIA/IEA/CSIS/ANRPC data, throughput tables |
| `empirical/blockades.md` | Research brief §2 | Tanker War, Red Sea, RAND blockades |
| `empirical/defense.md` | Research brief §3 | DoD FY2026 budget, Pentagon-automaker talks, draft |
| `empirical/energy_balances.md` | Research brief §1.4, EI Stat Review | Regional production vs consumption table |
| `empirical/refineries.md` | Research brief §4 | Global capacity by region, Iran capacity |
| `empirical/confirmed.md` | Research brief + test results | Hypotheses supported: Hormuz 83% reduction, North America surplus, naval blockade asymmetries, Panama crisis surge |
| `empirical/partial.md` | Research brief caveats | Partially supported: defense-industrial conversion (talks exist but no contracts), draft registration readiness |
| `empirical/rejected.md` | Research brief §6 | Rejected/unverified: "50 refinery fires in 45 days" (IEA ceiling = 2.5%), Malacca in model ≠ real Malacca effect due to SE Asia being net importer, "full GM/Ford conversion" (talks are preliminary) |

| MkDocs Page | Source Material |
|---|---|
| `data_sources.md` | `DATA_INTEGRATION.md` (condensed) |
| `calibration.md` | `historical_calibration.py`, `params_1973.json`, `params_2008.json` |
| `sensitivity.md` | `example_sensitivity.py`, `sensitivity_*.png` figures |
| `research_briefs.md` | Link to `outputs/chokepoint-empirical-constraints-brief.md`, `outputs/.plans/` |
| `transcripts.md` | Brief summaries of `game-theory-18.txt` and `game-theory-21.txt` with links to full text |

## Implementation Steps

### Phase 1 — Scaffolding
1. `mkdocs new .` (or manually create `mkdocs.yml` and `docs/`)
2. Set up `mkdocs.yml` with theme, plugins, nav structure
3. Add MathJax/KaTeX support for equation rendering
4. Set up `docs/javascripts/mathjax.js` and `docs/stylesheets/extra.css`

### Phase 2 — Model Specification Pages
5. Write `docs/index.md` (overview from `README.md`)
6. Write `docs/model/overview.md` (regions, state variables, architecture diagram)
7. Write `docs/model/variables.md` (15 variables with transforms)
8. Port `MATH_SPEC.md` → `docs/model/equations.md` with proper LaTeX rendering
9. Write `docs/model/thresholds.md` (nonlinear crisis triggers)
10. Generate `docs/model/config.md` via mkdocstrings from `model_config.py`
11. Write `docs/model/regional_params.md` with JSON schema explanation

### Phase 3 — API Reference (mkdocstrings)
12. Add mkdocstrings directives to `docs/api/geopolitical_model.md`
13. Add mkdocstrings directives to `docs/api/interventions.md`
14. Add mkdocstrings directives to `docs/api/trajectory.md`
15. Add mkdocstrings directives to `docs/api/scenarios.md`
16. Add mkdocstrings directives to `docs/api/sensitivity.md`
17. Add mkdocstrings directives to `docs/api/data_loader.md`

### Phase 4 — Scenario Pages
18. Write `docs/scenarios/overview.md` (summary table of all scenarios)
19. Write each scenario page with: description, intervention definition, empirical grounding table, figure, key results
20. Embed existing `.png` figures (hormuz_oil_stock.png, multi_chokepoint_oil.png, naval_blockade_china.png, etc.)

### Phase 5 — Empirical Grounding Pages
21. Write `docs/empirical/overview.md` (methodology: cross-referencing official sources)
22. Write chokepoints, blockades, defense, energy_balances, refineries pages from research brief
23. Write `docs/empirical/confirmed.md` — tabulate model outputs that match empirical data
24. Write `docs/empirical/partial.md` — flag uncertain or evolving findings
25. Write `docs/empirical/rejected.md` — catalog claims that failed verification

### Phase 6 — Supplementary Pages
26. Write `docs/data_sources.md` (condensed from DATA_INTEGRATION.md)
27. Write `docs/calibration.md` (historical calibration framework, 1973/2008 crises)
28. Write `docs/sensitivity.md` (parameter sweeps, Morris screening)
29. Write `docs/research_briefs.md` (link to outputs/)
30. Write `docs/transcripts.md` (game theory text summaries)

### Phase 7 — Parallel Execution via Subagents & Worktrees
**Strategy**: After Phase 1 scaffolding is complete, farm out independent content batches to parallel subagents operating in separate Git worktrees. The main agent polls every 10 min and pokes stuck subagents.

| Batch | Worktree | Subagent Task | Pages | Source Files |
|---|---|---|---|---|
| **A** | `wt-model-spec` | Write all model specification pages | `model/*.md` | `README.md`, `MATH_SPEC.md`, `model_config.py` |
| **B** | `wt-scenarios` | Write all scenario pages | `scenarios/*.md` | `example_*`, `research_brief` §1–2 |
| **C** | `wt-empirical` | Write all empirical grounding pages | `empirical/*.md` | `research_brief` §1–6, EIA/IEA data |
| **D** | `wt-supplementary` | Write supplementary & misc pages | `data_sources.md`, `calibration.md`, `sensitivity.md`, `research_briefs.md`, `transcripts.md` | `DATA_INTEGRATION.md`, `historical_calibration.py`, game-theory transcripts |
| **E** | `wt-api` | Generate API skeleton pages with mkdocstrings directives | `api/*.md` | `geopolitical_model.py`, `interventions.py`, `trajectory.py`, `scenarios.py`, `sensitivity.py`, `data_loader.py` |

**Worktree mechanics**:
1. Main branch: `main-agent` worktree at repo root.
2. For each batch X: `git worktree add ../jiang-model-wt-X` (or sibling dir), copy scaffolding from main, subagent writes there.
3. Subagents commit to their worktree branches (`batch/model-spec`, `batch/scenarios`, etc.).
4. Main agent gathers: `git worktree add` → read/copy files → merge into single `docs/` tree → resolve nav conflicts in `mkdocs.yml`.

**Polling**: Every 10 minutes, main agent checks subagent status. If a subagent has been silent >10 min, send a "poke" message asking for current status and next intended action.

### Phase 8 — Gather, Integrate, Build & Deploy
38. **Gather**: Pull each worktree's `docs/` content back into the main branch's `docs/` directory.
39. **Integrate nav**: Reconcile `mkdocs.yml` nav entries; ensure no duplicates or broken paths.
40. **Copy assets**: Move existing `.png` figures → `docs/assets/scenarios/`.
41. **Install**: `pip install mkdocs mkdocs-material mkdocstrings mkdocstrings-python mkdocs-jupyter mkdocs-table-reader-plugin mkdocs-glightbox`.
42. **Build**: `mkdocs build --strict` — fix any warnings or broken links.
43. **Serve test**: `mkdocs serve` (spot-check).
44. **GitHub Actions workflow** (non-optional): `.github/workflows/pages.yml` — trigger on `push` to `main`, run `mkdocs gh-deploy --force`.
45. Commit everything, push branch, verify Actions run.

### Phase 9 — Quality & Maintenance
46. Enforce link checking (`mkdocs build --strict` in CI).
47. Spell-check / markdown lint on pull requests.
48. Auto-regenerate API docs when Python sources change.

## Estimated Page Count

~30 pages across 7 sections, plus auto-generated API reference pages.

## Design Decisions

- **Math rendering**: Use MathJax (not KaTeX) for compatibility with the existing LaTeX-heavy MATH_SPEC.md equations (amsmath, align environments). The `pymdownx.arithmatex` extension with `generic: true` and a custom `mathjax.js` loader.
- **Figures**: Existing `.png` outputs from example scripts should be copied into `docs/assets/scenarios/` with captions and references.
- **Empirical pages**: These form a unique "provenance" section — showing which parts of the Game Theory narratives are measurable, which are contradicted by data, and which remain speculative. This is the value-add over a standard API docs site.
- **Code examples**: Every scenario page should include a minimal Python snippet showing how to run that scenario, encouraging reproducibility.
