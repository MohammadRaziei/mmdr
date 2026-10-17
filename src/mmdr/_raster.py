"""
SVG rasterization for mmdr, backed by novasvg (>=0.11).

The Rust extension only produces SVG. Everything pixel-related lives here.

Notes on novasvg behaviour that this module normalises:

* ``Document.load_from_data`` returns ``None`` for invalid SVG instead of raising.
* ``Document.render_to_bitmap`` defaults to an *opaque black* background, so a
  transparent background has to be requested explicitly.
* A ``Bitmap`` stores premultiplied BGRA. ``Bitmap.tobytes(rgba=True)`` returns a
  copy as straight (non-premultiplied) RGBA — what PNG and NumPy users expect —
  without importing NumPy.
"""

from __future__ import annotations

import novasvg


def _parse_color(value: str | None) -> "novasvg.Color":
    """Parse a CSS color with novasvg (hex ``#rgb`` / ``#rrggbb`` / ``#rrggbbaa``,
    or a CSS color name such as ``"white"``). ``None`` means fully transparent.
    """
    if value is None:
        return novasvg.Color(0, 0, 0, 0)
    try:
        return novasvg.Color(value)
    except ValueError as exc:
        raise ValueError(f"invalid background color {value!r}: {exc}") from exc


def _to_px(value: float | None, name: str) -> int:
    """Convert an optional size hint to novasvg's convention (-1 = automatic)."""
    if value is None:
        return -1
    px = int(round(value))
    if px <= 0:
        raise ValueError(f"{name} must be a positive number of pixels, got {value!r}")
    return px


def _render_bitmap(
    svg: str,
    width: float | None,
    height: float | None,
    background: str | None,
) -> "novasvg.Bitmap":
    doc = novasvg.Document.load_from_data(svg)
    if doc is None:
        raise ValueError("SVG parse error: novasvg could not load the document")

    bitmap = doc.render_to_bitmap(
        _to_px(width, "width"),
        _to_px(height, "height"),
        _parse_color(background),
    )
    if bitmap.is_null():
        raise ValueError("failed to rasterize SVG (empty or zero-sized canvas)")
    return bitmap


def svg_to_png(
    svg: str,
    width: float | None = None,
    height: float | None = None,
    background: str | None = None,
) -> bytes:
    """Convert an SVG string to PNG bytes.

    Args:
        svg:        SVG source text.
        width:      Output width in pixels. If only one of width/height is given
                    the other follows the SVG's aspect ratio. Default: the SVG's
                    intrinsic size.
        height:     Output height in pixels.
        background: Any color novasvg understands: CSS hex such as ``"#ffffff"``
                    (``#rgb`` and ``#rrggbbaa`` too) or a CSS name such as
                    ``"white"``. Transparent by default.
    """
    return _render_bitmap(svg, width, height, background).to_png()


def svg_to_raw(
    svg: str,
    width: float | None = None,
    height: float | None = None,
    background: str | None = None,
) -> tuple[bytes, int, int]:
    """Convert an SVG string to raw RGBA8888 pixels.

    Returns ``(raw_bytes, width, height)``. Rows are laid out top to bottom with
    stride ``width * 4``, and alpha is *straight* (not premultiplied).
    """
    bitmap = _render_bitmap(svg, width, height, background)
    return bitmap.tobytes(rgba=True), bitmap.width, bitmap.height
