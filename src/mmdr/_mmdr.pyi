"""Type stubs for the compiled Rust extension (_mmdr)."""

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
    """Render a Mermaid diagram to an SVG string."""
    ...

def backends() -> List[str]:
    """Return the list of SVG backends compiled into this wheel."""
    ...
