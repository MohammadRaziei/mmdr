"""
mmdr — Mermaid diagram rendering backed by native Rust.

Two backends, zero Python dependencies:
  - 'mermaid-rs-renderer' (default): fast, ~3ms per diagram
  - 'merman': full Mermaid @11.15.0 parity

Basic usage::

    import mmdr

    d = mmdr.render("flowchart LR; A-->B-->C")
    d.svg()                          # SVG string
    d.png()                          # PNG bytes
    d.save("diagram.svg")            # auto-detects format
    d.save("diagram.png", width=1200)
    d.numpy()                        # numpy array (requires numpy+Pillow)

    mmdr.backends()
    # ['mermaid-rs-renderer', 'merman']
"""

from ._mmdr import backends, __version__
from .diagram import Diagram


def render(
    diagram: str,
    backend: str | None = None,
    **opts,
) -> "Diagram":
    """Render a Mermaid diagram.

    Args:
        diagram: Mermaid source text.
        backend: ``"mermaid-rs-renderer"`` (default) or ``"merman"``.
        **opts: rendering options forwarded to the backend.

            mermaid-rs-renderer options:
                theme (``"modern"`` | ``"classic"``),
                node_spacing, rank_spacing, aspect_ratio

            merman options (PNG only):
                width, height, background, scale

    Returns:
        A :class:`Diagram` instance. The actual render is lazy — it only
        happens on the first call to :meth:`~Diagram.svg`,
        :meth:`~Diagram.png`, or :meth:`~Diagram.save`.
    """
    return Diagram(diagram, backend=backend, **opts)


__all__ = ["render", "Diagram", "backends", "__version__"]
