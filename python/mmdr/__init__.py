"""
mmdr - fast native Mermaid diagram rendering, powered by Rust.

>>> import mmdr
>>> svg = mmdr.render("flowchart LR; A-->B-->C")
"""

from ._mmdr import render, render_png, __version__

__all__ = ["render", "render_png", "__version__"]
