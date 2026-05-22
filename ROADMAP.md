# Roadmap

## Before the school

- Pick the lecture-machine environment: core cached mode only, or a prepared full stack with selected real-code demos.
- Re-run `python scripts/fetch_equilibria.py --minimal` on the lecture machine and confirm HSX/W7-X files are readable.
- Decide whether to demonstrate SIMSOPT live or replay the cached stage-2 coil fallback.
- Replace any synthetic figures with real outputs only when the runtime is short and reproducible.
- Build slide HTML/PDF with Marp and check movies on the projector machine.

## During the school

- Keep notebooks in `RUN_MODE = "cached"` for student machines.
- Use `tiny` or `research` mode only on the instructor machine after a smoke test.
- Treat every metric as a model with a validation domain.

## After the school

- Add lecture annotations and student exercise solutions.
- Convert successful live research demos into optional notebooks or scripts.
- Add CI that runs cached notebooks and checks generated assets.
