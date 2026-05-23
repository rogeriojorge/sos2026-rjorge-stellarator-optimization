# Installation

Canonical rendered documentation: https://sos2026-rjorge-stellarator-optimization.readthedocs.io/

## 10-minute local setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-core.txt -e .
python scripts/run_smoke_tests.py
```

This is the recommended student setup. It runs cached notebooks and generates all educational figures. Cached mode is the classroom default; full scientific packages are optional.

To run the same cached-mode checks used before publishing:

```bash
python scripts/check_release_ready.py
```

## Colab setup

```text
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
python scripts/execute_notebooks_in_place.py
python scripts/audit_no_local_paths.py
python scripts/audit_readthedocs_links.py
python scripts/audit_notebook_outputs.py
pytest -q
```

To execute every notebook in cached mode after changing lesson content:

```bash
python scripts/execute_all_notebooks.py
```

To refresh the outputs that are committed for GitHub rendering:

```bash
python scripts/execute_notebooks_in_place.py
```

Then audit the committed outputs:

```bash
python scripts/audit_notebook_outputs.py
```

To create the offline instructor bundle:

```bash
python scripts/make_lecture_bundle.py
```

The generated PowerPoint decks are already tracked in `slides/pptx/`. To rebuild them after editing `slides/powerpoint/deck_spec.json`, run this inside the Codex desktop runtime:

```bash
node scripts/build_powerpoint_decks.mjs
```

`requirements-full.txt` is best effort. Some scientific packages may need compiler, MPI, GPU, or platform-specific work.
If a full-stack install fails, continue in cached mode and use the live demo matrix to decide which research path to skip.

## JAX notes

Use CPU for classroom reliability unless a GPU environment has already been tested:

```bash
JAX_PLATFORMS=cpu python scripts/run_smoke_tests.py
```

If GPU JAX is installed, verify devices before a live demo.
