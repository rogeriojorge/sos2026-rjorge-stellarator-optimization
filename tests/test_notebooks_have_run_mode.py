import nbformat
from sos2026.paths import NOTEBOOK_DIR


def test_all_notebooks_have_run_mode():
    notebooks = sorted(NOTEBOOK_DIR.glob("*.ipynb"))
    assert len(notebooks) == 12
    for path in notebooks:
        nb = nbformat.read(path, as_version=4)
        text = "\n".join(cell.get("source", "") for cell in nb.cells)
        assert 'RUN_MODE = "cached"' in text


def test_notebooks_have_required_markdown_sections():
    for path in NOTEBOOK_DIR.glob("*.ipynb"):
        nb = nbformat.read(path, as_version=4)
        first = nb.cells[0].get("source", "")
        assert "What you will learn" in first
        assert "Codes used" in first
        assert "Run mode" in first
        assert "Expected outputs" in first
        tail = "\n".join(cell.get("source", "") for cell in nb.cells[-3:])
        assert "Try this" in tail
        assert "Expected qualitative answer" in tail
        assert "Research extension" in tail
