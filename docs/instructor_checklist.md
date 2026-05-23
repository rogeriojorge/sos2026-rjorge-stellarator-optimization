# Instructor Checklist

Use this checklist to make the repository predictable on the lecture machine.
Canonical rendered documentation: https://sos2026-rjorge-stellarator-optimization.readthedocs.io/

## One week before

- Clone the repo on the exact machine that will drive the projector.
- Create a fresh core environment with `requirements-core.txt`.
- Run `python scripts/check_release_ready.py`.
- Decide whether the live path is `cached`, `tiny`, or selected `research` demos.
- If using real packages live, record the package versions in `STATUS.md`.
- Open every PowerPoint deck in `slides/pptx/` once and confirm figures load.

## One day before

- Re-run `python scripts/check_release_ready.py`.
- Run `python scripts/audit_no_local_paths.py` and `python scripts/audit_readthedocs_links.py`.
- Build the lecture bundle with `python scripts/make_lecture_bundle.py` if distributing files offline.
- Launch JupyterLab and execute the first two cells of every notebook.
- Check both GIFs in `assets/movies/`.
- Review the contact sheets in `slides/pptx/contact_sheets/`; build Marp HTML/PDF only if using rendered Markdown slides.
- Keep a local copy of `STATUS.md` open for honest caveats during questions.

## Day of lecture

- Start in cached mode.
- Run only the notebook cells needed for the demo break.
- Avoid live package installs during class.
- Say explicitly when a figure is cached or synthetic.
- If a research-mode demo fails, continue from the cached figure and record the failure after the lecture.

## Suggested live choices

| Slot | Safe live demo | Optional stretch |
|---|---|---|
| Lecture 1 | `01`, `02`, `03` in cached mode | fetch real HSX/W7-X `wout` before class and show the file-read path |
| Lecture 2 | `04`, `05`, `06` in cached mode | SIMSOPT import and public QA input inspection |
| Lecture 3 | `07`, `08`, `09` in cached mode | `sfincs_jax` or `spectraxgk` tiny CLI smoke outside class |
| Lecture 4 | `10`, `11` in cached mode | replace one Pareto-column value with a real metric computed earlier |

## Abort criteria

Use cached mode immediately if:

- importing a research package takes more than 60 seconds,
- JAX selects an unexpected GPU backend,
- a notebook cell starts compiling during a lecture break,
- a live metric changes a plotted conclusion without enough time to explain it.
