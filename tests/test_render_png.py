"""Tests for mmdr.render_png() — PNG byte output."""

import struct
import zlib

import pytest
import mmdr
from conftest import SIMPLE_FLOWCHART, COMPLEX_FLOWCHART, is_valid_png


def png_dimensions(data: bytes) -> tuple[int, int]:
    """Extract (width, height) from a PNG IHDR chunk without Pillow."""
    # PNG layout: 8-byte sig + 4 len + 4 "IHDR" + 4 width + 4 height + ...
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    width  = struct.unpack(">I", data[16:20])[0]
    height = struct.unpack(">I", data[20:24])[0]
    return width, height


class TestRenderPngBasic:
    def test_returns_bytes(self, backend):
        result = mmdr.render_png(SIMPLE_FLOWCHART, backend=backend)
        assert isinstance(result, bytes)

    def test_valid_png_magic(self, backend):
        result = mmdr.render_png(SIMPLE_FLOWCHART, backend=backend)
        assert is_valid_png(result), "Output does not start with PNG magic bytes"

    def test_nonempty_output(self, backend):
        result = mmdr.render_png(SIMPLE_FLOWCHART, backend=backend)
        assert len(result) > 512

    def test_default_backend_works(self):
        result = mmdr.render_png(SIMPLE_FLOWCHART)
        assert is_valid_png(result)

    def test_complex_diagram(self, backend):
        result = mmdr.render_png(COMPLEX_FLOWCHART, backend=backend)
        assert is_valid_png(result)


class TestRenderPngDimensions:
    def test_png_has_positive_dimensions(self, backend):
        data = mmdr.render_png(SIMPLE_FLOWCHART, backend=backend)
        w, h = png_dimensions(data)
        assert w > 0
        assert h > 0

    def test_mermaid_rs_width_height(self, mermaid_rs):
        """width/height act as canvas size hints for the mermaid-rs backend."""
        data = mmdr.render_png(SIMPLE_FLOWCHART, backend=mermaid_rs,
                               width=400.0, height=300.0)
        assert is_valid_png(data)

    def test_merman_fit_box(self, merman):
        """width/height act as a fit-box for the merman backend."""
        data = mmdr.render_png(SIMPLE_FLOWCHART, backend=merman,
                               width=800.0, height=600.0)
        w, h = png_dimensions(data)
        assert w > 0 and h > 0


class TestRenderPngMermanOptions:
    def test_background_white(self, merman):
        data = mmdr.render_png(SIMPLE_FLOWCHART, backend=merman,
                               background="#ffffff")
        assert is_valid_png(data)

    def test_background_transparent(self, merman):
        data = mmdr.render_png(SIMPLE_FLOWCHART, backend=merman,
                               background=None)
        assert is_valid_png(data)

    def test_scale(self, merman):
        data_1x = mmdr.render_png(SIMPLE_FLOWCHART, backend=merman, scale=1.0)
        data_2x = mmdr.render_png(SIMPLE_FLOWCHART, backend=merman, scale=2.0)
        # 2x should produce a larger PNG
        assert len(data_2x) > len(data_1x)


class TestRenderPngMermaidRsOptions:
    def test_theme_modern(self, mermaid_rs):
        data = mmdr.render_png(SIMPLE_FLOWCHART, backend=mermaid_rs, theme="modern")
        assert is_valid_png(data)

    def test_theme_classic(self, mermaid_rs):
        data = mmdr.render_png(SIMPLE_FLOWCHART, backend=mermaid_rs, theme="classic")
        assert is_valid_png(data)

    def test_aspect_ratio(self, mermaid_rs):
        data = mmdr.render_png(SIMPLE_FLOWCHART, backend=mermaid_rs,
                               aspect_ratio=(16.0, 9.0))
        assert is_valid_png(data)


class TestRenderPngErrors:
    def test_unknown_backend_raises(self):
        with pytest.raises(ValueError, match="unknown backend"):
            mmdr.render_png(SIMPLE_FLOWCHART, backend="fake")

    def test_invalid_diagram_raises(self, backend):
        with pytest.raises(ValueError):
            mmdr.render_png("not mermaid!!!", backend=backend)
