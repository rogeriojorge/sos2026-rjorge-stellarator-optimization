# Data Sources

## HSX QHS

- Repository: `https://github.com/landreman/vmec_equilibria`
- Path: `HSX/QHS_vac_ns201_fixed/wout_HSX_QHS_vacuum_ns201.nc`
- Local destination: `data/vmec_equilibria/HSX/QHS_vac_ns201_fixed/wout_HSX_QHS_vacuum_ns201.nc`
- Use: small quasisymmetric stellarator thread for equilibrium, Boozer, and neoclassical-metric examples.

## W7-X standard

- Repository: `https://github.com/landreman/vmec_equilibria`
- Path: `W7-X/Standard/wout.nc`
- Local destination: `data/vmec_equilibria/W7-X/Standard/wout.nc`
- Use: school-relevant experimental reference for transport and turbulence motivation.

## SIMSOPT QA input

- Repository: `https://github.com/hiddenSymmetries/simsopt`
- Path: `tests/test_files/input.LandremanPaul2021_QA`
- Local destination: `data/inputs/simsopt/input.LandremanPaul2021_QA`
- Use: compact QA target for stage-2 coil optimization demos.

Fetch all required minimal data with:

```bash
python scripts/fetch_equilibria.py --minimal
```

If GitHub raw download fails, the script prints manual placement instructions and can copy from known local public checkouts when available. It never fabricates fake `wout` files.
