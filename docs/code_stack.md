# Code Stack

Local inspection was performed on 2026-05-22 using the prompt package, local source checkouts, package metadata, README files, and import checks on this machine.

| Code | What it computes | Lecture use | Current repo mode | Local install/import status |
|---|---|---|---|---|
| `vmec_jax` | Differentiable fixed/free-boundary VMEC-style ideal-MHD equilibria and `wout` outputs | Lecture 1 equilibrium and design variables | cached by default, research live path | package name `vmec-jax`; import `vmec_jax` OK from local checkout |
| `booz_xform_jax` | JAX-native Boozer coordinate transform and `Bmn` spectra from VMEC `wout` files | Lecture 1 Boozer spectrum and QS residuals | cached by default, research live path | package name/import `booz_xform_jax`; import OK |
| `NEO_JAX` | Effective ripple and trapped-particle diagnostics from Boozer geometry | Lecture 1/3 neoclassical optimization metric | cached by default, research live path | package name `neo-jax`; import `neo_jax` OK |
| `sfincs_jax` | Radially local drift-kinetic neoclassical transport, transport matrices, Er scans | Lecture 3 validation gate | cached by default, research-only for live solve | package name/import `sfincs_jax`; import OK |
| `SPECTRAX-GK` | JAX gyrokinetic linear/nonlinear turbulence metrics | Lecture 3 turbulence metric hierarchy | cached by default, research-only for live solve | package name `spectraxgk`; import `spectrax` OK |
| `NEOPAX` | JAX neoclassical/radial-transport/profile-oriented workflows | Lecture 4 profile closure | educational radial-transport fallback by default | source package `NEOPAX`; import `NEOPAX` OK |
| `ESSOS` | JAX stellarator coil, fieldline, and particle-tracing workflows | Lecture 2/3 fieldline and fast-particle diagnostics | cached by default, research live path | package name/import `essos`; import OK |
| SIMSOPT | Stellarator optimization framework, VMEC coupling, curves, coils, Biot-Savart | Lecture 2 stage-2 coils | cached by default, research live path | package name/import `simsopt`; import OK |
| `vmec_equilibria` | Public curated VMEC equilibria | shared HSX/W7-X cases across notebooks | real public data fetched by script | local public checkout inspected; HSX and W7-X files found |

## API notes from inspection

- `vmec_jax` README documents `pip install vmec-jax`, CLI `vmec_jax`, and Python calls such as `run_fixed_boundary` and `plot_wout`.
- `booz_xform_jax` README documents `Booz_xform().read_wout(...).register_surfaces(...).run().write_boozmn(...)`.
- `NEO_JAX` README documents CLI-compatible `neo-jax`, `xneo`, and `xneo_jax` paths using Boozer files.
- `sfincs_jax` README documents `sfincs_jax write-output --input ... --out ... --geometry-only` as a tiny smoke path.
- `SPECTRAX-GK` README documents `spectraxgk` and `spectrax-gk` entry points and VMEC-backed runtime TOML examples.
- SIMSOPT local checkout contains `tests/test_files/input.LandremanPaul2021_QA`, which is the stage-2 target copied/fetched by `scripts/fetch_equilibria.py`.

The notebooks intentionally do not assume these APIs are stable enough for live school demos. Cached mode is the supported default.
