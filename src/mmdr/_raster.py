"""
SVG rasterization for mmdr, backed by novasvg (>=0.10).

The Rust extension only produces SVG. Everything pixel-related lives here.

Notes on novasvg behaviour that this module normalises:

* ``Document.load_from_data`` returns ``None`` for invalid SVG instead of raising.
* ``Document.render_to_bitmap`` defaults to an *opaque black* background, so a
  transparent background has to be requested explicitly.
* Raw pixels are only available through ``Bitmap.numpy()`` (NumPy is therefore a
  mmdr dependency; novasvg itself no longer requires it). It returns premultiplied BGRA; ``convert_to_rgba()`` turns it
  into straight (non-premultiplied) RGBA, which is what PNG and NumPy users expect.
"""

from __future__ import annotations

import re

import novasvg

_HEX_RE = re.compile(r"^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


def _parse_color(value: str | None) -> "novasvg.Color":
    """Parse a CSS hex color (``#rgb``, ``#rrggbb`` or ``#rrggbbaa``).

    ``None`` means fully transparent.
    """
    if value is None:
        return novasvg.Color(0, 0, 0, 0)

    match = _HEX_RE.match(value.strip())
    if match is None:
        raise ValueError(
            f"invalid background color {value!r}; expected a CSS hex color "
            "such as '#ffffff'"
        )
    digits = match.group(1)
    if len(digits) == 3:
        digits = "".join(ch * 2 for ch in digits)
    r, g, b = (int(digits[i : i + 2], 16) for i in (0, 2, 4))
    a = int(digits[6:8], 16) if len(digits) == 8 else 255
    return novasvg.Color(r, g, b, a)


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
        background: CSS hex color such as ``"#ffffff"`` (``#rrggbbaa`` is also
                    accepted). Transparent by default.
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
    bitmap.convert_to_rgba()
    w, h = bitmap.width, bitmap.height
    return bitmap.numpy().tobytes(), w, h
