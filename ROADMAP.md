# Roadmap

## Before the school

- Pick the lecture-machine environment: core cached mode only, or a prepared full stack with selected real-code demos.
- Re-run `python scripts/check_release_ready.py` on the lecture machine.
- Decide whether to demonstrate SIMSOPT live or replay the cached stage-2 coil fallback.
- Replace any synthetic figures with real outputs only when the runtime is short and reproducible.
- Build slide HTML/PDF with Marp and check movies on the projector machine.
- Use `docs/instructor_checklist.md` and `docs/live_demo_matrix.md` to choose a conservative live-demo plan.

## During the school

- Keep notebooks in `RUN_MODE = "cached"` for student machines.
- Use `tiny` or `research` mode only on the instructor machine after a smoke test.
- Treat every metric as a model with a validation domain.

## After the school

- Add lecture annotations and student exercise solutions.
- Convert successful live research demos into optional notebooks or scripts.
- Convert one successful live demo per lecture into a tested `tiny` mode.
