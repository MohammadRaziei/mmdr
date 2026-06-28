from typing import Optional, Tuple

__version__: str

def render(
    diagram: str,
    theme: Optional[str] = None,
    node_spacing: Optional[float] = None,
    rank_spacing: Optional[float] = None,
    aspect_ratio: Optional[Tuple[float, float]] = None,
) -> str: ...

def render_png(
    diagram: str,
    theme: Optional[str] = None,
    node_spacing: Optional[float] = None,
    rank_spacing: Optional[float] = None,
    aspect_ratio: Optional[Tuple[float, float]] = None,
    width: Optional[float] = None,
    height: Optional[float] = None,
) -> bytes: ...
