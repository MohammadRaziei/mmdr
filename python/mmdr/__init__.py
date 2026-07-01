"""
mmdr — Mermaid diagram rendering backed by native Rust.

Two SVG backends, all rasterization via resvg — zero Python dependencies:
  - 'merman' (default): full Mermaid @11.15.0 parity
  - 'mermaid-rs-renderer': faster, fewer diagram types

Basic usage::

    import mmdr

    d = mmdr.render("flowchart LR; A-->B-->C")   # default: merman
    d.svg()                                        # str
    d.png()                                        # bytes
    d.png(width=1200, background="#ffffff")
    d.raw()                                        # (bytes, w, h) — RGBA8888
    d.numpy()                                      # np.ndarray, no Pillow
    d.save("out.svg")
    d.save("out.png", width=1200)

    mmdr.backends()
    # ['merman', 'mermaid-rs-renderer']
"""

from ._mmdr import backends, svg_to_png, svg_to_raw, __version__
from .diagram import Diagram


def render(
    diagram: str,
    backend: str | None = None,
    **opts,
) -> Diagram:
    """Render a Mermaid diagram.

    Args:
        diagram: Mermaid source text.
        backend: ``"merman"`` (default) or ``"mermaid-rs-renderer"``.
        **opts:  Options forwarded to the SVG backend.

                 mermaid-rs-renderer only:
                   theme (``"modern"`` | ``"classic"``),
                   node_spacing, rank_spacing, aspect_ratio

    Returns:
        A :class:`Diagram`. The SVG is rendered lazily on first access.
    """
    return Diagram(diagram, backend=backend, **opts)


__all__ = ["render", "Diagram", "backends", "svg_to_png", "svg_to_raw", "__version__"]
