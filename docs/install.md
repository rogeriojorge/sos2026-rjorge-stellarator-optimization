# Installation

## 10-minute local setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-core.txt -e .
python scripts/run_smoke_tests.py
```

This is the recommended student setup. It runs cached notebooks and generates all educational figures.

To run the same cached-mode checks used before publishing:

```bash
python scripts/check_release_ready.py
```

## Colab setup

```python
!git clone https://github.com/rogeriojorge/sos2026-rjorge-stellarator-optimization.git
%cd sos2026-rjorge-stellarator-optimization
!pip install -r requirements-colab.txt -e .
```

Do not run long package installs during lecture unless the instructor explicitly prepared that path.

## Full local setup

```bash
python -m pip install -r requirements-full.txt -e .
python scripts/fetch_equilibria.py --minimal
python scripts/generate_all_figures.py
python scripts/generate_movies.py
python scripts/execute_notebooks_core.py
python scripts/execute_all_notebooks.py
pytest -q
```

To execute every notebook in cached mode after changing lesson content:

```bash
python scripts/execute_all_notebooks.py
```

The generated PowerPoint decks are already tracked in `slides/pptx/`. To rebuild them after editing `slides/powerpoint/deck_spec.json`, run this inside the Codex desktop runtime:

```bash
node scripts/build_powerpoint_decks.mjs
```

`requirements-full.txt` is best effort. Some scientific packages may need compiler, MPI, GPU, or platform-specific work.

## JAX notes

Use CPU for classroom reliability unless a GPU environment has already been tested:

```bash
JAX_PLATFORMS=cpu python scripts/run_smoke_tests.py
```

If GPU JAX is installed, verify devices before a live demo.
