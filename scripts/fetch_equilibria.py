from __future__ import annotations
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import argparse
import hashlib
import json
import os
import shutil
import urllib.request
import warnings
from pathlib import Path

from sos2026.paths import PROJECT_ROOT, STATUS_DIR, VMEC_DIR, INPUT_DIR, ensure_directories

LOCAL_PUBLIC_ROOT = os.environ.get("SOS2026_PUBLIC_CHECKOUT_ROOT")


def optional_local_hint(relative_path: str) -> Path | None:
    """Return an opt-in local public-checkout fallback path.

    Public CI and student machines should download from GitHub or use files
    already present in this repo. Instructors with local public checkouts can
    set SOS2026_PUBLIC_CHECKOUT_ROOT without baking private paths into git.
    """
    if not LOCAL_PUBLIC_ROOT:
        return None
    return Path(LOCAL_PUBLIC_ROOT).expanduser() / relative_path


CASES_MINIMAL = [
    {
        "label": "HSX QHS vacuum ns201",
        "repo": "landreman/vmec_equilibria",
        "path": "HSX/QHS_vac_ns201_fixed/wout_HSX_QHS_vacuum_ns201.nc",
        "dest": VMEC_DIR / "HSX/QHS_vac_ns201_fixed/wout_HSX_QHS_vacuum_ns201.nc",
        "local_hint": optional_local_hint("vmec_equilibria/HSX/QHS_vac_ns201_fixed/wout_HSX_QHS_vacuum_ns201.nc"),
        "netcdf": True,
    },
    {
        "label": "W7-X standard",
        "repo": "landreman/vmec_equilibria",
        "path": "W7-X/Standard/wout.nc",
        "dest": VMEC_DIR / "W7-X/Standard/wout.nc",
        "local_hint": optional_local_hint("vmec_equilibria/W7-X/Standard/wout.nc"),
        "netcdf": True,
    },
    {
        "label": "SIMSOPT Landreman-Paul QA input",
        "repo": "hiddenSymmetries/simsopt",
        "path": "tests/test_files/input.LandremanPaul2021_QA",
        "dest": INPUT_DIR / "simsopt/input.LandremanPaul2021_QA",
        "local_hint": optional_local_hint("simsopt/tests/test_files/input.LandremanPaul2021_QA"),
        "netcdf": False,
    },
]

CASES_OPTIONAL = [
    {
        "label": "NCSX li383 low resolution",
        "repo": "landreman/vmec_equilibria",
        "path": "NCSX/li383_1.4m/wout_li383_1.4m.nc",
        "dest": VMEC_DIR / "NCSX/li383_1.4m/wout_li383_1.4m.nc",
        "local_hint": optional_local_hint("vmec_equilibria/NCSX/li383_1.4m/wout_li383_1.4m.nc"),
        "netcdf": True,
    }
]


def raw_urls(repo: str, path: str):
    for branch in ["master", "main"]:
        yield f"https://raw.githubusercontent.com/{repo}/{branch}/{path}"


def validate_netcdf(path: Path) -> str:
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=".*pynvml package is deprecated.*",
                category=FutureWarning,
            )
            import xarray as xr

            with xr.open_dataset(path) as ds:
                return f"netCDF OK; variables={len(ds.variables)}"
    except Exception as exc:
        return f"netCDF validation failed: {type(exc).__name__}: {exc}"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch_case(case: dict) -> dict:
    dest = Path(case["dest"])
    dest.parent.mkdir(parents=True, exist_ok=True)
    result = {"label": case["label"], "dest": str(dest.relative_to(PROJECT_ROOT)), "ok": False, "source": None, "message": ""}
    if dest.exists() and dest.stat().st_size > 0:
        result.update(ok=True, source="existing", message=f"present ({dest.stat().st_size} bytes)")
    else:
        errors = []
        for url in raw_urls(case["repo"], case["path"]):
            try:
                urllib.request.urlretrieve(url, dest)
                if dest.stat().st_size == 0:
                    raise RuntimeError("downloaded zero-byte file")
                result.update(ok=True, source=url, message=f"downloaded ({dest.stat().st_size} bytes)")
                break
            except Exception as exc:
                errors.append(f"{url}: {type(exc).__name__}: {exc}")
                if dest.exists() and dest.stat().st_size == 0:
                    dest.unlink()
        if not result["ok"] and case.get("local_hint") and Path(case["local_hint"]).exists():
            shutil.copy2(case["local_hint"], dest)
            result.update(ok=True, source=f"local public checkout fallback: {case['local_hint']}", message=f"copied ({dest.stat().st_size} bytes)")
        if not result["ok"]:
            result["message"] = "Download failed. Manual instruction: retrieve " + case["path"] + " from https://github.com/" + case["repo"] + " and place it at " + str(dest)
            result["errors"] = errors
    if result["ok"] and case.get("netcdf"):
        result["validation"] = validate_netcdf(dest)
    if result["ok"]:
        result["category"] = "real public data" if case.get("netcdf") else "real public data"
        result["sha256"] = sha256(dest)
        result["warning"] = "Public input artifact; downstream teaching figures may still be cached or synthetic."
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--minimal", action="store_true", help="Fetch HSX, W7-X standard, and SIMSOPT QA input")
    parser.add_argument("--all", action="store_true", help="Fetch minimal plus optional comparison cases")
    args = parser.parse_args(argv)
    ensure_directories()
    cases = list(CASES_MINIMAL)
    if args.all:
        cases += CASES_OPTIONAL
    results = [fetch_case(case) for case in cases]
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    (STATUS_DIR / "fetch_equilibria.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    for item in results:
        print(f"{item['label']}: {'OK' if item['ok'] else 'FAIL'} - {item['message']}")
        if item.get("validation"):
            print(f"  {item['validation']}")
    return 0 if all(item["ok"] for item in results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
