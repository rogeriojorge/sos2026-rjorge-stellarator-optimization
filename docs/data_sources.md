# Data Sources

Data and figure provenance use these categories: `real public data`, `real package output`, `cached derived data`, and `synthetic educational fallback`.
Generated figure metadata is recorded in `assets/figures/manifest.json`.

## HSX QHS

- Repository: `https://github.com/landreman/vmec_equilibria`
- Path: `HSX/QHS_vac_ns201_fixed/wout_HSX_QHS_vacuum_ns201.nc`
- Local destination: `data/vmec_equilibria/HSX/QHS_vac_ns201_fixed/wout_HSX_QHS_vacuum_ns201.nc`
- Use: small quasisymmetric stellarator thread for equilibrium, Boozer, and neoclassical-metric examples.
- Category: `real public data`.

## W7-X standard

- Repository: `https://github.com/landreman/vmec_equilibria`
- Path: `W7-X/Standard/wout.nc`
- Local destination: `data/vmec_equilibria/W7-X/Standard/wout.nc`
- Use: school-relevant experimental reference for transport and turbulence motivation.
- Category: `real public data`.

## SIMSOPT QA input

- Repository: `https://github.com/hiddenSymmetries/simsopt`
- Path: `tests/test_files/input.LandremanPaul2021_QA`
- Local destination: `data/inputs/simsopt/input.LandremanPaul2021_QA`
- Use: compact QA target for stage-2 coil optimization demos.
- Category: `real public data`.

Fetch all required minimal data with:

```bash
python scripts/fetch_equilibria.py --minimal
```

If GitHub raw download fails, the script prints manual placement instructions. Instructors with local public checkouts can set `SOS2026_PUBLIC_CHECKOUT_ROOT` to enable an opt-in copy fallback. The script never fabricates fake `wout` files.

Cached and synthetic classroom arrays live under `data/cached/`. They are intentionally small and labeled as `cached derived data` or `synthetic educational fallback`; they should not be cited as validated HSX, W7-X, SIMSOPT, SFINCS, SPECTRAX-GK, or NEOPAX results.
