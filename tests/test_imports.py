import importlib


def test_core_imports():
    for name in ["numpy", "scipy", "matplotlib", "pandas", "xarray", "netCDF4", "h5py", "nbformat"]:
        importlib.import_module(name)


def test_package_import():
    import sos2026
    assert sos2026.__version__


def test_optional_imports_are_reportable():
    optional = ["jax", "vmec_jax", "booz_xform_jax", "neo_jax", "sfincs_jax", "spectrax", "simsopt", "NEOPAX", "essos"]
    statuses = {}
    for name in optional:
        try:
            importlib.import_module(name)
            statuses[name] = True
        except Exception:
            statuses[name] = False
    assert set(statuses) == set(optional)
