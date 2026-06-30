from typing import Optional, Tuple, List

__version__: str

def render(
    diagram: str,
    backend: Optional[str] = None,
    theme: Optional[str] = None,
    node_spacing: Optional[float] = None,
    rank_spacing: Optional[float] = None,
    aspect_ratio: Optional[Tuple[float, float]] = None,
) -> str:
    """
    Render a Mermaid diagram to SVG.

    backend: "mermaid-rs-renderer" (default) or "merman"
    theme, node_spacing, rank_spacing, aspect_ratio: mermaid-rs-renderer only.
    """
    ...

def render_png(
    diagram: str,
    backend: Optional[str] = None,
    theme: Optional[str] = None,
    node_spacing: Optional[float] = None,
    rank_spacing: Optional[float] = None,
    aspect_ratio: Optional[Tuple[float, float]] = None,
    width: Optional[float] = None,
    height: Optional[float] = None,
    background: Optional[str] = None,
    scale: Optional[float] = None,
) -> bytes:
    """
    Render a Mermaid diagram to PNG bytes.

    backend: "mermaid-rs-renderer" (default) or "merman"

    mermaid-rs-renderer options: theme, node_spacing, rank_spacing,
        aspect_ratio, width (canvas px), height (canvas px)

    merman options: width (fit-box px), height (fit-box px),
        background (CSS color string), scale (device pixel ratio)
    """
    ...

def backends() -> List[str]:
    """Return the list of backends compiled into this wheel."""
    ...
