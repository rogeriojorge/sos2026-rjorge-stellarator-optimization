# Code Stack

Local inspection was performed on 2026-05-22 using the prompt package, local source checkouts, package metadata, README files, and import checks on this machine.

| Code | What it computes | Lecture use | Current repo mode | Local install/import status |
|---|---|---|---|---|
| VMEC | Standard ideal-MHD stellarator equilibrium solver and `wout` producer | Lecture 1 equilibrium baseline and Lecture 2 target surfaces | represented by public `wout` data and optional VMEC-compatible paths | no standalone VMEC executable assumed in cached mode |
| DESC | Spectral, differentiable stellarator equilibrium and optimization framework | Lecture 1 comparison path and Lecture 2/4 alternative equilibrium backend | optional research path | package/import `desc` OK, version `0.17.1+11.g2471d5504.dirty` |
| `vmec_jax` | Differentiable fixed/free-boundary VMEC-style ideal-MHD equilibria and `wout` outputs | Lecture 1 equilibrium and design variables | cached by default, research live path | package name `vmec-jax`; import `vmec_jax` OK from local checkout |
| `booz_xform_jax` | JAX-native Boozer coordinate transform and `Bmn` spectra from VMEC `wout` files | Lecture 1 Boozer spectrum and QS residuals | cached by default, research live path | package name/import `booz_xform_jax`; import OK |
| `NEO_JAX` | Effective ripple and trapped-particle diagnostics from Boozer geometry | Lecture 1/3 neoclassical optimization metric | cached by default, research live path | package name `neo-jax`; import `neo_jax` OK |
| SFINCS | Drift-kinetic neoclassical transport, ambipolar Er, and bootstrap-current calculations | Lecture 3 D11/Er/bootstrap validation | shown conceptually; live run is optional | Python import `sfincs` not present in the local environment |
| `sfincs_jax` | Radially local drift-kinetic neoclassical transport, transport matrices, Er scans | Lecture 3 validation gate | cached by default, research-only for live solve | package name/import `sfincs_jax`; import OK |
| NTX | Differentiable neoclassical/profile transport and bootstrap optimization workflows | Lecture 3/4 comparison lane for neoclassical/profile closure | optional research path | local source checkout import `ntx` OK, version `0.2.3` |
| `SPECTRAX-GK` | JAX gyrokinetic linear/nonlinear turbulence metrics | Lecture 3 turbulence metric hierarchy | cached by default, research-only for live solve | package name `spectraxgk`; import `spectrax` OK |
| GX | Gyrokinetic turbulence code used for nonlinear heat-flux validation | Lecture 3 turbulence validation and Lecture 4 profile credibility | external comparison/validation lane | Python import `gx` not present in the local environment |
| Trinity3D | Integrated transport workflow often paired with turbulence/neoclassical inputs | Lecture 4 profile-closure context | external comparison/validation lane | Python import `trinity3d` not present in the local environment |
| `NEOPAX` | JAX neoclassical/radial-transport/profile-oriented workflows | Lecture 4 profile closure | educational radial-transport fallback by default | source package `NEOPAX`; import `NEOPAX` OK |
| `ESSOS` | JAX stellarator coil, fieldline, and particle-tracing workflows | Lecture 2/3 fieldline and fast-particle diagnostics | cached by default, research live path | package name/import `essos`; import OK |
| SIMSOPT | Stellarator optimization framework, VMEC coupling, curves, coils, Biot-Savart | Lecture 2 stage-2 coils | cached by default, research live path | package name/import `simsopt`; import OK |
| NESCOIL / REGCOIL | Current-potential and regularized coil-design methods | Lecture 2 coil inverse-problem context | conceptual comparison, not required for cached demos | no local import/API assumed |
| FOCUS / QUADCOIL | Coil optimization families for modular-coil comparison and topology constraints | Lecture 2 coil-design comparison | conceptual comparison, not required for cached demos | no local import/API assumed |
| KNOSOS / MONKES | Neoclassical comparison solvers for low-collisionality stellarator transport | Lecture 3 validation context | external comparison lane | Python imports `knosos` and `monkes` not present in the local environment |
| `vmec_equilibria` | Public curated VMEC equilibria | shared HSX/W7-X cases across notebooks | real public data fetched by script | local public checkout inspected; HSX and W7-X files found |

## API notes from inspection

- `vmec_jax` README documents `pip install vmec-jax`, CLI `vmec_jax`, and Python calls such as `run_fixed_boundary` and `plot_wout`.
- `booz_xform_jax` README documents `Booz_xform().read_wout(...).register_surfaces(...).run().write_boozmn(...)`.
- `NEO_JAX` README documents CLI-compatible `neo-jax`, `xneo`, and `xneo_jax` paths using Boozer files.
- `sfincs_jax` README documents `sfincs_jax write-output --input ... --out ... --geometry-only` as a tiny smoke path.
- `SPECTRAX-GK` README documents `spectraxgk` and `spectrax-gk` entry points and VMEC-backed runtime TOML examples.
- SIMSOPT local checkout contains `tests/test_files/input.LandremanPaul2021_QA`, which is the stage-2 target copied/fetched by `scripts/fetch_equilibria.py`.
- DESC, NTX, and SIMSOPT imported successfully in the local environment used for this pass. GX, Trinity3D, classic SFINCS, KNOSOS, and MONKES were named as comparison/validation tools but were not importable as Python modules here.

The notebooks intentionally do not assume these APIs are stable enough for live school demos. Cached mode is the supported default.

Use `STATUS.md` and `assets/figures/manifest.json` to distinguish `real public data`, `real package output`, `cached derived data`, and `synthetic educational fallback`. Import success alone is not a claim that a real scientific calculation was run for a notebook output.

## Literature-backed teaching role

- Equilibrium and Boozer notebooks use the precise-quasisymmetry and good-magnetic-surface literature to motivate why spectra, iota, and topology checks are objective terms.
- Coil notebooks use SIMSOPT and single-stage papers to frame coils as part of the design variable set, not only as a downstream drawing exercise.
- Neoclassical notebooks use W7-X, SFINCS, NTX, KNOSOS, and MONKES context to explain why effective ripple, D11 scans, Er roots, and bootstrap current appear as validation gates.
- Turbulence/profile notebooks use GX, SPECTRAX-GK, Trinity3D, and nonlinear turbulence-optimization literature to explain why a cheap proxy can fail and why profile closure belongs in the final design loop.
