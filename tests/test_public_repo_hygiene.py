from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_SUFFIXES = {".pdf", ".ppt", ".zip", ".tar", ".gz", ".7z"}
EXPECTED_PPTX = {
    Path("slides/pptx/lecture_1_geometry_metrics.pptx"),
    Path("slides/pptx/lecture_2_coils_single_stage.pptx"),
    Path("slides/pptx/lecture_3_transport_turbulence_metrics.pptx"),
    Path("slides/pptx/lecture_4_integrated_workflow.pptx"),
}


def tracked_files() -> list[Path]:
    output = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True)
    return [ROOT / line for line in output.splitlines() if line]


def test_no_prompt_source_materials_are_tracked():
    bad = [path for path in tracked_files() if "source_materials" in path.parts]
    assert not bad


def test_no_forbidden_prompt_file_types_are_tracked():
    bad = [path.relative_to(ROOT) for path in tracked_files() if path.suffix.lower() in FORBIDDEN_SUFFIXES]
    assert not bad


def test_only_generated_powerpoint_decks_are_tracked():
    tracked_pptx = {path.relative_to(ROOT) for path in tracked_files() if path.suffix.lower() == ".pptx"}
    assert tracked_pptx == EXPECTED_PPTX


def test_powerpoint_contact_sheets_are_tracked():
    expected = {
        Path("slides/pptx/contact_sheets/lecture_1_geometry_metrics_contact_sheet.png"),
        Path("slides/pptx/contact_sheets/lecture_2_coils_single_stage_contact_sheet.png"),
        Path("slides/pptx/contact_sheets/lecture_3_transport_turbulence_metrics_contact_sheet.png"),
        Path("slides/pptx/contact_sheets/lecture_4_integrated_workflow_contact_sheet.png"),
    }
    tracked_png = {path.relative_to(ROOT) for path in tracked_files() if "slides/pptx/contact_sheets" in path.as_posix()}
    assert tracked_png == expected


def test_no_large_files_are_tracked():
    limit_bytes = 20 * 1024 * 1024
    bad = [
        (path.relative_to(ROOT), path.stat().st_size)
        for path in tracked_files()
        if path.exists() and path.stat().st_size > limit_bytes
    ]
    assert not bad
