from sos2026.paths import FIGURE_DIR, MOVIE_DIR


def test_at_least_eight_figures_exist():
    figures = list(FIGURE_DIR.glob("*.png"))
    assert len(figures) >= 8


def test_required_figures_exist():
    for name in ["01_hsx_surface.png", "02_boozer_contour.png", "02_boozer_spectrum.png", "03_epsilon_eff_comparison.png", "04_bdotn_before_after.png", "09_proxy_vs_nonlinear.png", "11_pareto_front.png"]:
        assert (FIGURE_DIR / name).exists()


def test_movies_generated_or_status_can_document():
    assert len(list(MOVIE_DIR.glob("*.gif"))) >= 2
