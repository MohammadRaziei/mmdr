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
) -> str: ...

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
) -> bytes: ...

def backends() -> List[str]: ...
