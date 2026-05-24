# References And Links

## Code repositories

- UWPlasma `vmec_jax`: https://github.com/uwplasma/vmec_jax
- UWPlasma `booz_xform_jax`: https://github.com/uwplasma/booz_xform_jax
- UWPlasma `NEO_JAX`: https://github.com/uwplasma/NEO_JAX
- UWPlasma `sfincs_jax`: https://github.com/uwplasma/sfincs_jax
- UWPlasma `SPECTRAX-GK`: https://github.com/uwplasma/SPECTRAX-GK
- UWPlasma `NEOPAX`: https://github.com/uwplasma/NEOPAX
- UWPlasma `ESSOS`: https://github.com/uwplasma/ESSOS
- SIMSOPT: https://github.com/hiddenSymmetries/simsopt
- SIMSOPT docs: https://simsopt.readthedocs.io/
- VMEC equilibria: https://github.com/landreman/vmec_equilibria
- DESC: https://github.com/PlasmaControl/DESC
- REGCOIL: https://github.com/landreman/regcoil

## Scientific reading list

Use this as the instructor reading path. The lecture slides cite only a few of these papers on the core path; the notebooks use the list to explain why each cached metric exists.

### Optimization frameworks and quasisymmetry

- Landreman, Medasani, Wechsung, Giuliani, Jorge, and Zhu, "SIMSOPT: A flexible framework for stellarator optimization," *Journal of Open Source Software* 6, 3525 (2021). https://joss.theoj.org/papers/10.21105/joss.03525
- Landreman and Paul, "Magnetic fields with precise quasisymmetry for plasma confinement," *Physical Review Letters* 128, 035001 (2022). https://arxiv.org/abs/2108.03711
- Landreman, Medasani, and Zhu, "Stellarator optimization for good magnetic surfaces at the same time as quasisymmetry," *Physics of Plasmas* 28, 092505 (2021). https://arxiv.org/abs/2106.14930
- Baillod, Loizu, Graves, and Landreman, "Stellarator optimization for nested magnetic surfaces at finite beta and toroidal current," *Physics of Plasmas* 29, 042505 (2022). https://arxiv.org/abs/2111.15564

### Coils and single-stage design

- Giuliani, Wechsung, Landreman, Stadler, and Cerfon, "Single-stage gradient-based stellarator coil design: optimization for near-axis quasi-symmetry," *Journal of Computational Physics* 459, 111147 (2022). https://doi.org/10.1016/j.jcp.2022.111147
- Jorge, Goodman, Landreman, Rodrigues, and Wechsung, "Single-stage stellarator optimization: combining coils with fixed boundary equilibria," *Plasma Physics and Controlled Fusion* 65, 074003 (2023). https://arxiv.org/abs/2302.10622
- Jorge, Giuliani, and Loizu, "Simplified and flexible coils for stellarators using single-stage optimization" (2024). https://arxiv.org/abs/2406.07830

### Neoclassical validation and W7-X

- Beidler et al., "Demonstration of reduced neoclassical energy transport in Wendelstein 7-X," *Nature* 596, 221-226 (2021). https://www.nature.com/articles/s41586-021-03687-w
- Landreman, Ernst, and Catto, "Comparison of particle trajectories and collision operators for collisional transport in nonaxisymmetric plasmas," *Physics of Plasmas* 21, 042503 (2014). https://publications.lib.chalmers.se/records/fulltext/199559/local_199559.pdf
- `sfincs_jax` public package notes and install smoke path. https://pypi.org/project/sfincs-jax/

### Turbulence and profile closure

- Kim et al., "Optimization of nonlinear turbulence in stellarators," *Journal of Plasma Physics* 90, 905900203 (2024). https://www.cambridge.org/core/journals/journal-of-plasma-physics/article/optimization-of-nonlinear-turbulence-in-stellarators/916FCC56452B5B166C14868F56D99AF5
- `SPECTRAX-GK` public package notes and claim-scope ledger. https://pypi.org/project/spectraxgk/
- W7-X ion-temperature clamping and turbulence-regime literature, used here as motivation for treating turbulence as a validation gate rather than as an afterthought.

### Broader background

- Helander, "Theory of plasma confinement in non-axisymmetric magnetic fields," *Reports on Progress in Physics* 77, 087001 (2014).
- NESCOIL, REGCOIL, FOCUS, QUADCOIL, and SIMSOPT coil-design literature for current potentials, filamentary coils, coil complexity, and manufacturability metrics.
- DESC and GX/DESC-GX literature for differentiable equilibrium and turbulence optimization.

Source PDFs and slide decks supplied in the prompt package were used only for local planning context and are not redistributed in this public teaching repo.
