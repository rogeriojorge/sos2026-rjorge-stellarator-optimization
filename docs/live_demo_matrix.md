# Live Demo Matrix

This matrix separates the reliable classroom path from optional live-code paths.

| Notebook | Classroom default | Real package path | Risk level | Failure mode to teach |
|---|---|---|---|---|
| `00_environment_check` | import table and figure write test | optional package import/version table | low | optional packages are not core requirements |
| `01_vmec_jax_first_equilibrium` | cached surface plus fetched `wout` iota when available | `vmec_jax` fixed-boundary run | medium | equilibrium solves can be slow or fail to converge |
| `02_boozer_spectrum` | cached Boozer-like modes | `booz_xform_jax` transform of HSX/W7-X `wout` | medium | coordinate transforms depend on resolution and input quality |
| `03_effective_ripple_neo_jax` | cached epsilon-effective curves | `neo_jax` solve from a Boozer file | medium | a compact metric is not a full transport calculation |
| `04_simsopt_stage2_coils` | synthetic coils and `B dot n` maps | SIMSOPT QA input and tiny stage-2 replay | medium | better field accuracy can worsen coil complexity |
| `05_single_stage_toy` | pure Python continuation toy | JAX/SIMSOPT coupled objective prototype | low to medium | weight choices can hide infeasible optima |
| `06_essos_fieldlines_particles` | synthetic fieldline/orbit plots | ESSOS fieldline or particle trace | medium | good flux surfaces do not guarantee particle confinement |
| `07_sfincs_jax_neoclassical_cached` | cached D11/Er/bootstrap curves | `sfincs_jax` tiny geometry or transport run | high | validation metrics cost more and need input discipline |
| `08_spectrax_gk_linear_metric` | cached growth/frequency curves | `spectraxgk` default linear run | high | linear growth is a proxy, not nonlinear heat flux |
| `09_turbulence_metric_surrogate` | cached proxy-vs-validation table | replace validation column with real output | low | proxies can reorder design choices |
| `10_neopax_profile_closure` | educational radial model | NEOPAX radial-transport example | medium | profiles close the loop and can undo field-only optimism |
| `11_pareto_design_dashboard` | cached design table | replace one metric column with real output | low | a Pareto front exposes value judgments |

## Recommendation

Use cached mode for all student machines. On the instructor machine, pick at most one live research demo per lecture and test it immediately before the session.
