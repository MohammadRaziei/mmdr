"""
The Diagram class: the object returned by mmdr.render().

Lazily renders the diagram on first access, caches the SVG, and provides
format-specific accessors (.svg(), .png(), .pdf(), .numpy()) plus a
.save() helper that infers the output format from the file extension.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from . import _mmdr

if TYPE_CHECKING:
    import numpy as np


class Diagram:
    """A Mermaid diagram ready to be rendered to multiple output formats.

    Created by :func:`mmdr.render`. The source is rendered lazily: the
    first call to :meth:`svg` (or any derived method) triggers the actual
    render; the result is cached so subsequent calls are free.

    Example::

        import mmdr

        d = mmdr.render("flowchart LR; A-->B-->C")
        d.save("diagram.svg")
        d.save("diagram.png", width=1200)
        print(d.svg())
        img = d.numpy()             # requires numpy + Pillow
    """

    def __init__(
        self,
        source: str,
        backend: str | None = None,
        **opts,
    ) -> None:
        self._source = source
        self._backend = backend
        self._opts = opts
        self._svg_cache: str | None = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _svg_opts(self) -> dict:
        valid = {"theme", "node_spacing", "rank_spacing", "aspect_ratio"}
        return {k: v for k, v in self._opts.items() if k in valid and v is not None}

    def _png_opts(self) -> dict:
        valid = {
            "theme", "node_spacing", "rank_spacing", "aspect_ratio",
            "width", "height", "background", "scale",
        }
        return {k: v for k, v in self._opts.items() if k in valid and v is not None}

    # ------------------------------------------------------------------
    # Output formats
    # ------------------------------------------------------------------

    def svg(self) -> str:
        """Return the diagram as an SVG string (cached after first call)."""
        if self._svg_cache is None:
            self._svg_cache = _mmdr.render(
                self._source, self._backend, **self._svg_opts()
            )
        return self._svg_cache

    def png(self, **kwargs) -> bytes:
        """Return the diagram as PNG bytes.

        Keyword arguments override any options set at construction time.
        Valid options depend on the backend:

        mermaid-rs-renderer:
            width, height (canvas size hint in pixels),
            theme, node_spacing, rank_spacing, aspect_ratio

        merman:
            width, height (fit-box in pixels),
            background (CSS color, e.g. ``"#ffffff"``),
            scale (device pixel ratio, e.g. ``2.0`` for HiDPI)
        """
        opts = {**self._png_opts(), **kwargs}
        return _mmdr.render_png(self._source, self._backend, **opts)

    def pdf(self) -> bytes:
        """Return the diagram as PDF bytes.

        Not yet supported. Planned via merman's ``svg2pdf`` feature.
        """
        raise NotImplementedError(
            "PDF export is not yet supported. "
            "Planned for a future release via merman's svg2pdf feature."
        )

    def numpy(self) -> "np.ndarray":
        """Return the diagram as a NumPy array (H×W×4, uint8, RGBA).

        Requires ``numpy`` and ``Pillow``::

            pip install numpy Pillow
        """
        try:
            import numpy as np_mod
        except ImportError as exc:
            raise ImportError(
                "numpy is required for .numpy(). Install it with:\n"
                "    pip install numpy"
            ) from exc
        try:
            from PIL import Image
        except ImportError as exc:
            raise ImportError(
                "Pillow is required for .numpy(). Install it with:\n"
                "    pip install Pillow"
            ) from exc
        import io
        return np_mod.array(Image.open(io.BytesIO(self.png())))

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def save(self, output: str, **kwargs) -> None:
        """Save the diagram to *output*, inferring the format from its extension.

        Args:
            output: destination path, e.g. ``"diagram.svg"`` or ``"diagram.png"``.
            **kwargs: forwarded to the relevant format method
                      (same options as :meth:`png`).

        Raises:
            ValueError: if the extension is not recognised.
        """
        path = Path(output)
        suffix = path.suffix.lower()

        if suffix == ".svg":
            path.write_text(self.svg(), encoding="utf-8")
        elif suffix == ".png":
            path.write_bytes(self.png(**kwargs))
        elif suffix == ".pdf":
            path.write_bytes(self.pdf(**kwargs))  # type: ignore[call-arg]
        else:
            raise ValueError(
                f"Cannot infer output format from {output!r}. "
                "Supported extensions: .svg, .png, .pdf"
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
