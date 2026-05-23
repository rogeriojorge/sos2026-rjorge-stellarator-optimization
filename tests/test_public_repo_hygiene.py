from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_SUFFIXES = {".pdf", ".ppt", ".pptx", ".zip", ".tar", ".gz", ".7z"}


def tracked_files() -> list[Path]:
    output = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True)
    return [ROOT / line for line in output.splitlines() if line]


def test_no_prompt_source_materials_are_tracked():
    bad = [path for path in tracked_files() if "source_materials" in path.parts]
    assert not bad


def test_no_forbidden_prompt_file_types_are_tracked():
    bad = [path.relative_to(ROOT) for path in tracked_files() if path.suffix.lower() in FORBIDDEN_SUFFIXES]
    assert not bad


def test_no_large_files_are_tracked():
    limit_bytes = 20 * 1024 * 1024
    bad = [
        (path.relative_to(ROOT), path.stat().st_size)
        for path in tracked_files()
        if path.exists() and path.stat().st_size > limit_bytes
    ]
    assert not bad
