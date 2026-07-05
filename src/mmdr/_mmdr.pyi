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

def svg_to_png(
    svg: str,
    width: Optional[float] = None,
    height: Optional[float] = None,
    background: Optional[str] = None,
) -> bytes:
    """Convert an SVG string to PNG bytes using resvg."""
    ...

def svg_to_raw(
    svg: str,
    width: Optional[float] = None,
    height: Optional[float] = None,
    background: Optional[str] = None,
) -> Tuple[bytes, int, int]:
    """Convert an SVG string to raw RGBA8888 bytes.

    Returns (raw_bytes, width, height).
    Use with numpy: np.frombuffer(raw, dtype=np.uint8).reshape(h, w, 4)
    """
    ...

def backends() -> List[str]:
    """Return the list of SVG backends compiled into this wheel."""
    ...
