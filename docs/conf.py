from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

project = "SOS 2026 Stellarator Optimization"
author = "Rogerio Jorge"
copyright = "2026, Rogerio Jorge"
release = "0.1.0"

extensions = ["myst_parser", "sphinx.ext.autodoc", "sphinx.ext.napoleon"]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
master_doc = "index"

html_theme = "sphinx_rtd_theme"
html_static_path: list[str] = []
html_title = project

myst_enable_extensions = ["colon_fence", "deflist"]
myst_heading_anchors = 3

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
