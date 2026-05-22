from sos2026.paths import DATA_DIR, CACHE_DIR, FIGURE_DIR, NOTEBOOK_DIR, ensure_directories


def test_required_folders_exist():
    ensure_directories()
    for path in [DATA_DIR, CACHE_DIR, FIGURE_DIR, NOTEBOOK_DIR]:
        assert path.exists()


def test_cached_fallback_files_exist_after_generation():
    expected = ["epsilon_eff_comparison.npz", "boozer_hsx_synthetic_or_real.npz", "pareto_design_table.csv"]
    missing = [name for name in expected if not (CACHE_DIR / name).exists()]
    assert not missing, f"Run python scripts/generate_all_figures.py; missing {missing}"
