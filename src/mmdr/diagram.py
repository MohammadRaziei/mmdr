"""
Diagram — the object returned by mmdr.render().

SVG comes from the chosen backend (merman or mermaid-rs-renderer).
Everything else (PNG, raw pixels, numpy) is produced by resvg inside the
Rust extension — no Python imaging dependencies needed.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from . import _mmdr

if TYPE_CHECKING:
    import numpy as np


class Diagram:
    """A rendered Mermaid diagram.

    Created by :func:`mmdr.render`. SVG is computed lazily on first access
    and cached. PNG and raw pixels are always derived from that SVG via resvg.

    Example::

        import mmdr

        d = mmdr.render("flowchart LR; A-->B-->C")

        d.svg()                          # str
        d.png()                          # bytes (PNG)
        d.png(width=1200, background="#ffffff")
        d.raw()                          # (bytes, width, height) — RGBA8888
        d.numpy()                        # np.ndarray H×W×4, no Pillow needed
        d.save("out.svg")
        d.save("out.png", width=1200)
        d._repr_svg_()                   # Jupyter inline rendering
    """

    def __init__(self, source: str, backend: str | None = None, **opts) -> None:
        self._source = source
        self._backend = backend
        self._opts = opts
        self._svg_cache: str | None = None

    # ------------------------------------------------------------------
    # SVG — from the chosen backend
    # ------------------------------------------------------------------

    def svg(self) -> str:
        """Return the diagram as an SVG string (cached after first call)."""
        if self._svg_cache is None:
            svg_opts = {
                k: v for k, v in self._opts.items()
                if k in {"theme", "node_spacing", "rank_spacing", "aspect_ratio"}
                and v is not None
            }
            self._svg_cache = _mmdr.render(self._source, self._backend, **svg_opts)
        return self._svg_cache

    # ------------------------------------------------------------------
    # Rasterization — always via resvg inside the Rust extension
    # ------------------------------------------------------------------

    def png(
        self,
        width: float | None = None,
        height: float | None = None,
        background: str | None = None,
    ) -> bytes:
        """Return the diagram as PNG bytes.

        Args:
            width:      Canvas width hint in pixels.
            height:     Canvas height hint in pixels.
            background: Background fill as a CSS hex color, e.g. ``"#ffffff"``.
                        Transparent by default.
        """
        return _mmdr.svg_to_png(self.svg(), width, height, background)

    def raw(
        self,
        width: float | None = None,
        height: float | None = None,
        background: str | None = None,
    ) -> tuple[bytes, int, int]:
        """Return raw RGBA8888 pixel data as ``(bytes, width, height)``.

        The bytes have stride ``width * 4``, row-major, top-to-bottom.
        No Python imaging library needed — resvg writes pixels directly
        into a Rust buffer and hands it to Python as ``bytes``.

        Args:
            width:      Canvas width hint in pixels.
            height:     Canvas height hint in pixels.
            background: Background fill as a CSS hex color.
        """
        return _mmdr.svg_to_raw(self.svg(), width, height, background)

    def numpy(
        self,
        width: float | None = None,
        height: float | None = None,
        background: str | None = None,
    ) -> "np.ndarray":
        """Return the diagram as a NumPy array (H×W×4, uint8, RGBA).

        No Pillow needed — uses :meth:`raw` directly.
        Requires ``numpy``::

            pip install numpy
        """
        try:
            import numpy as np
        except ImportError as exc:
            raise ImportError(
                "numpy is required for .numpy(). Install it with:\n"
                "    pip install numpy"
            ) from exc

        raw, w, h = self.raw(width=width, height=height, background=background)
        return np.frombuffer(raw, dtype=np.uint8).reshape(h, w, 4)

    def pdf(self) -> bytes:
        """Return the diagram as PDF bytes.

        Not yet supported — planned via resvg/krilla.
        """
        raise NotImplementedError(
            "PDF export is not yet supported. Planned for a future release."
        )

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def save(
        self,
        output: str,
        width: float | None = None,
        height: float | None = None,
        background: str | None = None,
    ) -> None:
        """Save the diagram to *output*, inferring the format from the extension.

        Args:
            output:     Destination path, e.g. ``"diagram.svg"`` or ``"diagram.png"``.
            width:      Canvas width in pixels (PNG only).
            height:     Canvas height in pixels (PNG only).
            background: Background color, e.g. ``"#ffffff"`` (PNG only).

        Raises:
            ValueError: if the file extension is not recognised.
        """
        path = Path(output)
        suffix = path.suffix.lower()

        if suffix == ".svg":
            path.write_text(self.svg(), encoding="utf-8")
        elif suffix == ".png":
            path.write_bytes(self.png(width=width, height=height, background=background))
        elif suffix == ".pdf":
            path.write_bytes(self.pdf())
        else:
            raise ValueError(
                f"Cannot infer output format from {output!r}. "
                "Supported extensions: .svg  .png  .pdf"
            )

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        first_line = (self._source.strip().splitlines() or [""])[0]
        backend_label = self._backend or "default"
        return f"<Diagram backend={backend_label!r} {first_line!r}>"

    def _repr_svg_(self) -> str:
        """Jupyter/IPython rich display — renders inline SVG automatically."""
        return self.svg()
