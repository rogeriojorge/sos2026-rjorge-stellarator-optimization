# Troubleshooting

## JAX CPU/GPU issues

Start with CPU mode:

```bash
JAX_PLATFORMS=cpu python scripts/run_smoke_tests.py
```

GPU JAX wheels are platform-specific. A GPU import failure should not block cached notebooks.

## Missing netCDF/HDF5

Install the core requirements again:

```bash
python -m pip install -r requirements-core.txt
```

If `netCDF4` fails on your platform, try conda-forge or pixi.

## SIMSOPT install issues

SIMSOPT can require compiled components depending on the selected features. Use cached coil notebooks during lecture, then install SIMSOPT separately after class.

## Optional package import failures

`run_smoke_tests.py` reports optional packages but does not require them. Check `STATUS.md` for which notebooks are cached, live, or research-only.

## Colab limitations

Colab can run cached mode. Avoid live VMEC/Boozer/neoclassical/gyrokinetic installs during a timed lecture unless the environment was prepared beforehand.

## Cached-mode fallback

Cached mode is intentional. It uses labeled synthetic or cached educational data to keep plots and exercises available even when heavy packages fail.
