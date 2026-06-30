"""
mmdr - Mermaid diagram rendering backed by native Rust.

Two backends, zero Python dependencies:
  - 'mermaid-rs-renderer': fast, lighter, fewer diagram types
  - 'merman': parity-focused, targets Mermaid @11.15.0

>>> import mmdr
>>> mmdr.backends()
['mermaid-rs-renderer', 'merman']

>>> svg = mmdr.render("flowchart LR; A-->B-->C")
>>> svg = mmdr.render("flowchart LR; A-->B-->C", backend="merman")
"""

from ._mmdr import render, render_png, backends, __version__

__all__ = ["render", "render_png", "backends", "__version__"]
