---
marp: true
theme: default
paginate: true
size: 16:9
---

# What should go into the objective function?
Lecture 3: neoclassical, turbulence, and fast-particle gates

![bg right:48% contain](../assets/figures/09_proxy_vs_nonlinear.png)
- Can transport physics become an optimization metric?
- Docs: https://sos2026-rjorge-stellarator-optimization.readthedocs.io/

---

# PART 1. A hierarchy of transport calculations
- Cheap screens move many designs
- Expensive calculations validate finalists

---

# What is neoclassical transport?
- **Term:** Neoclassical transport
- **Definition:** Collisional transport caused by guiding-center drifts in a toroidal magnetic field with trapped particles.
- **Equation:** Gamma, Q = functions(geometry, nu, E_r, profiles)
- **Physical meaning:** It is geometry sensitive, especially in stellarators, and can be reduced by optimization.
- **Optimizer sees:** Use cheap geometry metrics first, then drift-kinetic validation for finalists.
- **Failure mode:** The result depends on collisionality, radial electric field, species, and profiles.
- **Remember:** Neoclassical metrics are geometry gates with plasma-state assumptions.

<small>Refs: Helander RPP 77, 087001 (2014); Beidler et al., Nature 596, 221-226 (2021).</small>

---

# Trapped particles explain the need for symmetry
![bg right:48% contain](../assets/figures/ref_trapped_particles_quasisymmetry.png)
- Trapped particles sample only part of a surface
- Drift averages can fail
- Quasisymmetry restores a conserved quantity

_This is the clearest bridge from orbit physics to an optimization target._

<small>Source visual: Landreman, Charkiw Stellarator Optimization Lectures, slide 20.</small>

---

# The optimizer follows the metric we choose
- Metric design is part of physics

---

# Main ideas for Lecture 3
| Main idea | What students should be able to say |
|---|---|
| Neoclassical | Trapped-particle drifts make geometry-dependent transport, measured with epsilon_eff, D11, Er roots, and bootstrap current. |
| Turbulence | Microinstabilities drive fluctuation transport; fast growth-rate screens need nonlinear validation. |
| Cost hierarchy | Use cheap metrics to rank many designs, then expensive solvers to validate finalists. |
| Optimization | A transport number is useful only with its species, profiles, collisionality, and normalization. |

_This lecture does not derive the DKE or GKE; it shows where these quantities enter a design loop._

---

# Cheap screens come before expensive transport
- Boozer spectra and epsilon_eff screen many geometries quickly
- DKE solvers such as SFINCS add collisionality, Er, and bootstrap-current physics
- Gyrokinetic solvers such as GX validate turbulence ranking for finalists

---

# Codes used in this lecture
| Code | What it does here |
|---|---|
| NEO_JAX | Fast epsilon_eff and trapped-particle screens from Boozer geometry. |
| SFINCS / sfincs_jax | Drift-kinetic neoclassical transport: D11 scans, ambipolar Er roots, bootstrap current, and JAX experiments. |
| NTX | Differentiable neoclassical, bootstrap-current, and profile-transport optimization lane; local import verified. |
| KNOSOS / MONKES | Comparison neoclassical lanes for cross-checking low-collisionality conclusions. |
| GX / Trinity3D | Gyrokinetic turbulence and integrated transport validation when ranking finalists. |
| SPECTRAX-GK | JAX gyrokinetic metrics for optimization loops and fast growth-rate scans. |

_Teaching point: use a ladder of cost and trust; live class runs can focus on selected tools._

<small>Code references: NEO_JAX, SFINCS, sfincs_jax, NTX, GX, Trinity3D, SPECTRAX-GK, KNOSOS, and MONKES.</small>

---

# Transport means neoclassical plus turbulent flux
![bg right:48% contain](../assets/figures/ref_total_flux_neoclassical_turbulent.png)
- Neoclassical flux follows guiding-center drifts
- Turbulent flux follows instabilities
- Both depend on geometry

_This slide gives students the mental equation before the individual metrics appear._

<small>Source visual: Landreman, Introduction to Stellarator Optimization, IPFN 2022, slide 16.</small>

---

# Transport literature says: validate the winner
- W7-X: neoclassical optimization reduced the geometry-driven loss channel
- SFINCS: drift-kinetic validation depends on trajectory, electric-field, and collision modeling choices
- Nonlinear turbulence: heat-flux objectives can be noisy enough to need stochastic or staged optimization

<small>Refs: Beidler et al., Nature 596, 221-226 (2021); Landreman et al., Phys. Plasmas 21, 042503 (2014); Kim et al., JPP 90, 905900203 (2024).</small>

---

# Effective ripple is a neoclassical screen
![bg right:48% contain](../assets/figures/03_epsilon_eff_comparison.png)
- Rank candidates before expensive runs
- Do not treat the scalar as the whole transport story

_These curves show how the screen should be read; full transport validation remains a separate step._

---

# What is D11?
- **Term:** D11 transport coefficient
- **Definition:** A radial particle-transport coefficient from the drift-kinetic response, often scanned versus collisionality.
- **Equation:** Gamma_1 = - n D_11 (d ln n / dr + ...)
- **Physical meaning:** It tells how strongly particles diffuse radially for a given thermodynamic drive.
- **Optimizer sees:** Use D11 scans to test whether a low-ripple design remains good under richer kinetic physics.
- **Failure mode:** A single D11 curve is not a full flux prediction without Er, sources, profiles, and species choices.
- **Remember:** D11 is a validation coefficient, not a universal confinement number.

<small>Ref: Landreman et al., Phys. Plasmas 21, 042503 (2014).</small>

---

# DKE calculations turn geometry into transport coefficients
![bg right:48% contain](../assets/figures/ref_drift_kinetic_bootstrap_equation.png)
- Solve along phase-space characteristics
- Compute distribution-function moments
- Scan coefficients before claiming performance

_Use this to explain what sits behind D11 and bootstrap-current validation plots._

<small>Source visual: Landreman, PoP webinar on bootstrap current and energetic particles, 2022, slide 16.</small>

---

# D11 scans add richer validation
![bg right:48% contain](../assets/figures/07_sfincs_d11_scan.png)
- Collisionality changes the answer
- Er suppression changes the interpretation

_Read the slope, the electric-field suppression, and the collisionality window._

<small>Ref: Landreman et al., Phys. Plasmas 21, 042503 (2014), SFINCS drift-kinetic solver.</small>

---

# Ambipolar roots are not always unique
![bg right:48% contain](../assets/figures/07_er_roots.png)
- Multiple roots imply multiple regimes
- Optimization needs a root-choice rule

_Read the zero crossings as possible radial electric-field roots; the physical branch depends on profiles, species, and stability._

---

# Bootstrap current feeds back on equilibrium
![bg right:48% contain](../assets/figures/07_bootstrap_profile.png)
- Bootstrap current can alter transform and islands
- Profile dependence enters early

_Transport outputs become equilibrium inputs._

---

# W7-X lesson for optimizers
- Neoclassical optimization: reduced radial losses
- Ion-temperature clamping: turbulence bottleneck
- Profiles: decide whether the metric matters experimentally

---

# Neoclassical success can expose turbulence
![bg right:48% contain](../assets/figures/09_w7x_clamping_cartoon.png)
- The blue expectation keeps rising
- The orange curve saturates

_The cartoon motivates turbulence-aware validation without rederiving transport theory._

<small>Ref: Beidler et al., Nature 596, 221-226 (2021); W7-X ion-temperature clamping literature.</small>

---

# Demo break: neoclassical validation
![bg right:48% contain](../assets/figures/07_sfincs_d11_scan.png)
- Read a collisionality scan
- Inspect Er roots
- Plot bootstrap feedback

_Notebook 07: SFINCS-style neoclassical validation._

---

# PART 2. Turbulence metrics
- Linear calculations are early screens
- Nonlinear validation changes rankings

---

# What is turbulent transport?
- **Term:** Turbulent transport
- **Definition:** Radial heat and particle transport driven by microinstabilities and nonlinear fluctuations.
- **Equation:** Q_turb ~ <delta v_E · delta p>
- **Physical meaning:** It can dominate after neoclassical losses are reduced, as seen in W7-X temperature-clamping discussions.
- **Optimizer sees:** Start with linear or proxy metrics, then validate finalists with nonlinear heat-flux calculations.
- **Failure mode:** Linear growth rates can rank designs differently from nonlinear heat flux.
- **Remember:** A transport optimizer must survive both neoclassical and turbulence gates.

<small>Ref: Kim et al., J. Plasma Phys. 90, 905900203 (2024).</small>

---

# Turbulence optimization starts with a rankable metric
![bg right:48% contain](../assets/figures/ref_numerical_turbulence_optimization.png)
- Linear growth is a useful first screen
- Heat flux remains the validation target
- The wrong proxy can win the wrong race

_The lecture uses this same staged logic: cheap metric first, expensive validation later._

<small>Source visual: Landreman UMD numerical-analysis seminar, 2023, slide 22.</small>

---

# Turbulence metrics need invariant feature maps
![bg right:48% contain](../assets/figures/ref_turbulence_ml_workflow.png)
- Many geometries feed the simulation database
- Features must respect translations and symmetries
- Regression is useful only after validation

_This visual motivates the notebook surrogate without replacing gyrokinetic validation._

<small>Source visual: Landreman, Plasma turbulence in stellarators, 2026, slide 20.</small>

---

# Multiple feature checks agree on the same physics
![bg right:48% contain](../assets/figures/ref_sherwood_feature_importance.png)
- Compare methods before trusting a surrogate
- Look for a repeated physical feature
- Use agreement as a diagnostic, not a proof

_Several independent ranking methods point to the same bad-curvature-region metric._

<small>Source visual: Landreman Sherwood ML turbulence regression deck, 2025, slide 37.</small>

---

# Linear growth is a fast warning
![bg right:48% contain](../assets/figures/08_growth_rate_spectrum.png)
- Positive growth marks unstable branches
- The peak is not the heat flux

_Use growth rate as a screen, not as the final objective._

<small>Ref: SPECTRAX-GK PyPI/docs, JAX-native gyrokinetic solver for stellarator optimization workflows.</small>

---

# What are growth rate and frequency?
- **Term:** Linear gyrokinetic spectrum
- **Definition:** The growth rate says whether a mode amplifies; the frequency helps identify the branch.
- **Equation:** omega = omega_r + i gamma
- **Physical meaning:** Positive gamma marks an unstable mode, but the nonlinear saturated flux is a separate result.
- **Optimizer sees:** Use spectra as fast screens and branch diagnostics before nonlinear validation.
- **Failure mode:** A design with a lower peak gamma can still have worse nonlinear heat flux.
- **Remember:** Linear spectra are warning lights; nonlinear flux is the stronger gate.

<small>Ref: SPECTRAX-GK public package notes and nonlinear turbulence optimization literature.</small>

---

# Frequency helps identify the branch
![bg right:48% contain](../assets/figures/08_frequency_spectrum.png)
- Growth and frequency belong together
- The sign and trend help classify modes

_Frequency is diagnostic context, not the scalar objective._

---

# A proxy can pick the wrong winner
![bg right:48% contain](../assets/figures/09_proxy_vs_nonlinear.png)
- Red circle: proxy winner
- Green circle: validation winner

_The ranking failure is the point of the plot._

<small>Ref: Kim et al., J. Plasma Phys. 90, 905900203 (2024), nonlinear turbulence optimization with noisy heat fluxes.</small>

---

# Demo break: turbulence proxy versus validation
![bg right:48% contain](../assets/figures/09_proxy_vs_nonlinear.png)
- Choose the proxy winner
- Compare validation ranking
- Explain the failure mode

_Notebook path: notebooks/08_spectrax_gk_linear_metric.ipynb + notebooks/09_turbulence_metric_surrogate.ipynb_

---

# PART 3. Fast particles are reactor gates
- Alpha confinement, wall loads, and orbit classes matter
- Particle metrics must rerun after coil changes

---

# Particle metrics connect back to coils
![bg right:48% contain](../assets/figures/06_particle_orbit.png)
- A fieldline picture can look acceptable
- An orbit diagnostic can still fail

_Fast-particle checks belong in the validation ladder._

---

# Validation compares failure modes
- Does the metric fail on a known bad design?
- Does it rank a known good design correctly?
- Does it change smoothly under perturbations?

---

# Metric trust ladder
- Screen: reduced model trend
- Ranking hypothesis: fast or quasilinear run
- Validation: expensive run or experimental comparison

---

# Lecture 3 what to remember
- Use cheap metrics to steer the search
- Use expensive metrics to challenge finalists
- Plot profiles and regimes
- Never hide proxy failure

---

# Transport metrics are validation gates
- A good design survives a stronger metric

---

# APPENDIX. Lecture 3 checks and replacements
- Use this section when SFINCS, SPECTRAX, or particle tools are live
- Keep reference ranking plots ready

---

# Neoclassical outputs to track
- Effective ripple: low-collisionality screen
- Ambipolar roots: radial electric-field validation
- Bootstrap current: profile-dependent equilibrium feedback

---

# Turbulence outputs to track
- Linear growth rate: fast instability screen
- Quasilinear weight: ranking hypothesis
- Nonlinear heat flux: validation for finalists

---

# Package path: NEO_JAX, SFINCS, and SFINCS_JAX
- Choose the same equilibrium and flux surface
- Scan collisionality and radial electric field
- Compare compact metrics before detailed validation

---

# Package path: GX and SPECTRAX-GK
- Start with a short linear calculation
- Plot growth rate and frequency versus ky
- Keep nonlinear validation gate explicit

---

# How to read a fast metric
- Growth rate screens instability before heat-flux validation
- A scalar ripple value should point back to where losses occur
- A profile proxy should lead to a solved discharge model

---

# Reference figure: growth-rate spectrum
![bg right:48% contain](../assets/figures/08_growth_rate_spectrum.png)
- Use if a live linear run is slow
- Ask what the scalar should be

---

# Reference figure: W7-X clamping cartoon
![bg right:48% contain](../assets/figures/09_w7x_clamping_cartoon.png)
- Use to motivate turbulence after neoclassical success
- Keep the cartoon label visible

---

# Before showing a transport number
- Equilibrium: which surface and assumptions?
- Kinetics: which species and collisionality?
- Validation: which expensive calculation confirms it?

---

# Discussion: what can reverse the ranking?
- Neoclassical winner: can lose on turbulence
- Turbulence winner: can fail alpha confinement
- Profile change: can move both metrics together

---

# What to remember
- Keep the scientific object and the computed artifact together
- Rerun, perturb, compare, and explain before trusting the optimum
- Docs: https://sos2026-rjorge-stellarator-optimization.readthedocs.io/
