# SOS 2026 Stellarator Optimization

This repository supports Rogerio Jorge's four 90-minute lectures for the 2026 CEA-IRFM / Renaissance Fusion School on Stellarators in Aix-en-Provence. The course treats stellarator design as a computational optimization loop: equilibrium -> Boozer spectrum -> neoclassical metrics -> coils -> turbulence metrics -> profile closure -> Pareto decisions.

## 10-minute quickstart

```bash
git clone https://github.com/rogeriojorge/sos2026-rjorge-stellarator-optimization.git
cd sos2026-rjorge-stellarator-optimization
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-core.txt -e .
python scripts/run_smoke_tests.py
python scripts/generate_all_figures.py
jupyter lab notebooks/
```

Cached mode is enough for all classroom notebooks and does not require compiling scientific codes.

## Colab quickstart

Open a notebook in Colab, clone this repo, and install the Colab requirements:

```python
!git clone https://github.com/rogeriojorge/sos2026-rjorge-stellarator-optimization.git
%cd sos2026-rjorge-stellarator-optimization
!pip install -r requirements-colab.txt -e .
```

Keep `RUN_MODE = "cached"` unless the instructor has prepared a live scientific stack.

## Full local workflow

```bash
python -m pip install -r requirements-full.txt -e .
python scripts/fetch_equilibria.py --minimal
python scripts/generate_all_figures.py
python scripts/generate_movies.py
python scripts/execute_notebooks_core.py
python scripts/make_status_report.py
pytest -q
```

The full requirements include verified package names or source installs for `vmec_jax`, `booz_xform_jax`, `NEO_JAX`, `sfincs_jax`, `SPECTRAX-GK`, `NEOPAX`, `ESSOS`, and SIMSOPT, but the notebooks remain useful when those packages are absent.

## Run modes

- `tiny`: the fastest live path, intended for short classroom experiments.
- `cached`: default mode; uses small cached or synthetic educational data with clear labels.
- `research`: opt-in mode for replacing cached arrays with real package calls after API and runtime checks.

## Notebook map

| Notebook | Topic | Default path |
|---|---|---|
| `00_environment_check.ipynb` | Environment, optional packages, write checks | cached |
| `01_vmec_jax_first_equilibrium.ipynb` | VMEC/wout surfaces and iota | cached with real wout if fetched |
| `02_boozer_spectrum.ipynb` | Boozer contour, spectrum, QS residual | cached |
| `03_effective_ripple_neo_jax.ipynb` | Effective ripple as optimization metric | cached |
| `04_simsopt_stage2_coils.ipynb` | Stage-2 coils and `B dot n` tradeoff | cached, SIMSOPT research path |
| `05_single_stage_toy.ipynb` | Single-stage objective and continuation | cached toy |
| `06_essos_fieldlines_particles.ipynb` | Fieldlines, orbits, fast-particle gates | cached, ESSOS research path |
| `07_sfincs_jax_neoclassical_cached.ipynb` | Richer neoclassical validation metrics | cached |
| `08_spectrax_gk_linear_metric.ipynb` | Linear turbulence metric | cached |
| `09_turbulence_metric_surrogate.ipynb` | Proxy vs nonlinear validation | cached |
| `10_neopax_profile_closure.ipynb` | Profile and power-balance closure | cached |
| `11_pareto_design_dashboard.ipynb` | Integrated Pareto dashboard | cached |

## Lecture map

- `slides/lecture_1_geometry_metrics.md`: geometry, VMEC, Boozer coordinates, metrics.
- `slides/lecture_2_coils_single_stage.md`: coils, stage-2 optimization, single-stage design.
- `slides/lecture_3_transport_turbulence_metrics.md`: neoclassical, turbulence, fast-particle metrics.
- `slides/lecture_4_integrated_workflow.md`: profiles, Pareto fronts, repo lab.

Slides are Marp-compatible Markdown. Build with `slides/build_slides.sh` after installing `@marp-team/marp-cli`, or read them directly in Markdown.

## Documentation

Start with `docs/install.md`, then use `docs/code_stack.md`, `docs/data_sources.md`, `docs/teaching_notes.md`, `docs/troubleshooting.md`, and `docs/references.md`.

## Honesty policy

Cached and synthetic figures are labeled educational fallbacks. They are designed to keep lectures robust, not to replace verified VMEC, Boozer, neoclassical, coil, gyrokinetic, or profile calculations.
