---
marp: true
theme: default
paginate: true
size: 16:9
---

# Can we design a stellarator by following gradients?

Lecture 1: what the optimizer actually sees

![bg right:48% contain](../assets/figures/01_hsx_surface.png)
- Equilibrium, Boozer spectrum, and metrics become the design language
- Docs: https://sos2026-rjorge-stellarator-optimization.readthedocs.io/

---

# PART 1. From field lines to hidden symmetry

- Goal: turn confinement physics into computable objectives
- Caveat: geometry freedom creates an inverse problem

---

# Metrics are compressed physics

- They are useful only when we know what was compressed

---

# Three literature gates shape the workflow

- Precise quasisymmetry: make the Boozer spectrum sparse, then test what remains
- Good magnetic surfaces: compare surface-based objectives with island and chaos diagnostics
- W7-X validation: reduced neoclassical transport is real progress, but it is one gate in the loop

<small>Refs: Landreman & Paul PRL 128, 035001 (2022); Landreman et al. Phys. Plasmas 28, 092505 (2021); Beidler et al. Nature 596, 221-226 (2021).</small>

---

# The optimizer sees artifacts with provenance

- Boundary and profiles create an equilibrium
- Spectra and scalars turn physics into objectives
- Every scalar needs a validation gate

---

# The first object is a surface

![bg right:48% contain](../assets/figures/01_hsx_surface.png)
- Read the shape as a parameterized boundary
- This is a cached educational surface

_A visible surface is a design variable, not yet a validated device._

<small>VMEC background: Hirshman & Whitson, Phys. Fluids 26, 3553 (1983); public cases from landreman/vmec_equilibria.</small>

---

# W7-X is the reference case to keep in mind

![bg right:48% contain](../assets/figures/01_w7x_surface.png)
- Use it as experimental motivation
- Do not treat the fallback surface as a new W7-X result

_The reference case anchors the design discussion without duplicating geometry lectures._

<small>Ref: Beidler et al., Nature 596, 221-226 (2021), reduced neoclassical energy transport in W7-X.</small>

---

# Rotational transform is an optimization target

![bg right:48% contain](../assets/figures/01_iota_profile.png)
- Plot pitch before optimizing spectra
- Watch low-order rational surfaces

_A profile can be a constraint, an objective, or a diagnostic._

<small>Ref: Landreman, Medasani & Zhu, Phys. Plasmas 28, 092505 (2021), good surfaces and quasisymmetry together.</small>

---

# A small boundary mode can move the objective

![bg right:48% contain](../assets/figures/01_boundary_mode_scan.png)
- One knob changes QS residual and aspect ratio
- This is the gradient intuition for stage 1

_The optimizer needs knobs whose effects can be measured._

---

# Equilibrium convergence is part of the result

- Record resolution and residuals
- Do not compare designs before the solve is trustworthy
- Cached mode keeps the teaching path alive

---

# The wout file is the first checked artifact

- Inspect dimensions, surfaces, and mode counts
- Use public HSX/W7-X files when present
- Record what was actually read

---

# Demo break: first equilibrium object

![bg right:48% contain](../assets/figures/01_iota_profile.png)
`notebooks/01_vmec_jax_first_equilibrium.ipynb`

- Locate the HSX wout file
- Plot surface and iota
- Change one boundary-mode proxy

_Cached mode first. Repo: https://github.com/rogeriojorge/sos2026-rjorge-stellarator-optimization | Docs: https://sos2026-rjorge-stellarator-optimization.readthedocs.io/_

---

# PART 2. Boozer coordinates make symmetry measurable

- The spectrum turns geometry into a table
- Bad modes become penalties

---

# Boozer coordinates make symmetry visible

![bg right:48% contain](../assets/figures/02_boozer_contour.png)
- Clean bands suggest the intended symmetry
- Broken bands warn before the scalar metric

_This contour is a teaching diagnostic, not a fresh Boozer transform._

---

# The spectrum tells the optimizer what to penalize

![bg right:48% contain](../assets/figures/02_boozer_spectrum.png)
- Green modes preserve the intended line
- Red modes are symmetry-breaking targets

_Good and bad modes are marked explicitly for the classroom scan._

<small>Ref: Landreman & Paul, Phys. Rev. Lett. 128, 035001 (2022), precise quasisymmetry.</small>

---

# A bad mode changes the picture immediately

![bg right:48% contain](../assets/figures/02_bad_mode_perturbation.png)
- Perturb one coefficient
- Regenerate contour and residual

_The exercise is to connect a table entry to a visible field-strength change._

---

# Several symmetry targets use the same workflow

- Quasi-axisymmetry: penalize modes off the QA line
- Quasi-helical symmetry: keep the QH ridge clean
- Quasi-isodynamic: use different metrics but the same artifact discipline

---

# Effective ripple is an early transport warning

![bg right:48% contain](../assets/figures/03_epsilon_eff_comparison.png)
- Lower is better for this screen
- Use it before expensive validation

_This cached curve teaches how to read a metric; it is not a new NEO result._

<small>Ref: Beidler et al., Nature 596, 221-226 (2021), effective ripple as a W7-X optimization target.</small>

---

# Gradients tell us which knobs matter

![bg right:48% contain](../assets/figures/03_epsilon_eff_sensitivity.png)
- Finite differences are robust for teaching
- Autodiff becomes important at scale

_The point is sensitivity ranking, not a production derivative._

---

# The scalar objective is a negotiation

- Weights encode scientific and engineering priorities

---

# Demo break: spectrum and ripple

![bg right:48% contain](../assets/figures/02_boozer_spectrum.png)
`notebooks/02_boozer_spectrum.ipynb + notebooks/03_effective_ripple_neo_jax.ipynb`

- Circle bad modes
- Change one scalar
- Explain what the plot proves

_Cached mode first. Repo: https://github.com/rogeriojorge/sos2026-rjorge-stellarator-optimization | Docs: https://sos2026-rjorge-stellarator-optimization.readthedocs.io/_

---

# Failure mode: optimizing a beautiful plot

- A clean surface is not a validated design
- A scalar can hide the wrong physics
- A cached figure must say what it is

---

# Lecture 1 what to remember

- Optimization starts with a parameterization
- A wout file is a scientific artifact
- Boozer spectra turn symmetry into penalties
- Metrics must stay connected to validation

---

# A design loop starts when the artifact can be rerun

- Repo and docs are part of the scientific object

---

# APPENDIX. Lecture 1 checks and replacements

- Use this section when a live package succeeds
- Keep cached mode as the classroom baseline

---

# VMEC file review

- Dimensions: surfaces, modes, field periods
- Variables: iota, pressure, boundary coefficients
- Provenance: public repo path and hash

---

# Boozer file review

- Surface labels: choose the same radial grid
- Mode truncation: report m/n limits
- Residual: separate symmetry-preserving from breaking modes

---

# When cached mode is enough

- Teaching the loop structure
- Testing plotting and data plumbing
- Preparing exercises with qualitative answers

---

# When research mode is needed

- Reporting a numerical value
- Comparing HSX and W7-X quantitatively
- Changing VMEC or Boozer resolution

---

# Research path: VMEC_JAX to Boozer transform

- Start from a verified input or wout file
- Run a tiny equilibrium on the lecture machine
- Replace cached arrays with documented outputs

---

# Metric acceptance checklist

- Cached figure: use for trend and classroom discussion
- Real-code run: use for numerical claim after provenance check
- STATUS.md record: package, data source, and validation domain

---

# Backup figure: HSX surface

![bg right:48% contain](../assets/figures/01_hsx_surface.png)
- Use if the live surface plot fails
- Keep the cached label visible

_Fallback image for a short live-demo recovery._

---

# Backup figure: Boozer contour

![bg right:48% contain](../assets/figures/02_boozer_contour.png)
- Use if the transform is slow
- Discuss the expected symmetry pattern

_Fallback image for reading the contour before scalarizing._

---

# Discussion: what did the optimizer see?

- Design variable: boundary modes and profiles
- Computed object: equilibrium, spectra, scalar metrics
- Decision variable: which scalar deserves trust

---

# What to remember

- Keep the scientific object and the computed artifact together
- Rerun, perturb, compare, and explain before trusting the optimum
- Docs: https://sos2026-rjorge-stellarator-optimization.readthedocs.io/
