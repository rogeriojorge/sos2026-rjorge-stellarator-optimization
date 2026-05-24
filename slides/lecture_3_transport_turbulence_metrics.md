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

# The optimizer follows the metric we choose

- Metric design is part of physics

---

# Cost hierarchy for transport metrics

- Geometry metrics: fastest screens
- Effective ripple and Boozer metrics: early transport warnings
- DKE, gyrokinetics, particles, profiles: validation gates

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

_Cached curves teach the screen; they are not new transport calculations._

---

# D11 scans add richer validation

![bg right:48% contain](../assets/figures/07_sfincs_d11_scan.png)
- Collisionality changes the answer
- Er suppression changes the interpretation

_This SFINCS-style scan is cached educational data._

<small>Ref: Landreman et al., Phys. Plasmas 21, 042503 (2014), SFINCS drift-kinetic solver.</small>

---

# Ambipolar roots are not always unique

![bg right:48% contain](../assets/figures/07_er_roots.png)
- Multiple roots imply multiple regimes
- Optimization needs a root-choice rule

_The root structure is the lesson; the numbers are not a live SFINCS result._

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

# Demo break: neoclassical cached validation

![bg right:48% contain](../assets/figures/07_sfincs_d11_scan.png)
`notebooks/07_sfincs_jax_neoclassical_cached.ipynb`

- Read a collisionality scan
- Inspect Er roots
- Plot bootstrap feedback

_Cached mode first. Repo: https://github.com/rogeriojorge/sos2026-rjorge-stellarator-optimization | Docs: https://sos2026-rjorge-stellarator-optimization.readthedocs.io/_

---

# PART 2. Turbulence metrics

- Linear calculations are early screens
- Nonlinear validation changes rankings

---

# Linear growth is a fast warning

![bg right:48% contain](../assets/figures/08_growth_rate_spectrum.png)
- Positive growth marks unstable branches
- The peak is not the heat flux

_Use growth rate as a screen, not as the final objective._

<small>Ref: SPECTRAX-GK PyPI/docs, JAX-native gyrokinetic solver for stellarator optimization workflows.</small>

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
`notebooks/08_spectrax_gk_linear_metric.ipynb + notebooks/09_turbulence_metric_surrogate.ipynb`

- Choose the proxy winner
- Compare validation ranking
- Explain the failure mode

_Cached mode first. Repo: https://github.com/rogeriojorge/sos2026-rjorge-stellarator-optimization | Docs: https://sos2026-rjorge-stellarator-optimization.readthedocs.io/_

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

- Screen: cached or reduced model trend
- Ranking hypothesis: tiny or quasilinear run
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
- Keep cached ranking plots ready

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

# Research path: NEO_JAX and SFINCS_JAX

- Choose the same equilibrium and flux surface
- Scan collisionality and radial electric field
- Compare compact metrics before detailed validation

---

# Research path: SPECTRAX-GK

- Start with a tiny linear calculation
- Plot growth rate and frequency versus ky
- Keep nonlinear validation gate explicit

---

# How to read a fast metric

- Growth rate screens instability before heat-flux validation
- A scalar ripple value should point back to where losses occur
- A profile proxy should lead to a solved discharge model

---

# Backup figure: growth-rate spectrum

![bg right:48% contain](../assets/figures/08_growth_rate_spectrum.png)
- Use if a live linear run is slow
- Ask what the scalar should be

---

# Backup figure: W7-X clamping cartoon

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
