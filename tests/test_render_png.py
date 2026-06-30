"""Tests for Diagram.png() — PNG byte output."""

import struct
import pytest
import mmdr
from conftest import SIMPLE_FLOWCHART, COMPLEX_FLOWCHART, is_valid_png


def png_dimensions(data: bytes) -> tuple[int, int]:
    """Extract (width, height) from a PNG IHDR chunk — no Pillow needed."""
    assert isinstance(data, bytes), f"expected bytes, got {type(data)}"
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG file"
    width  = struct.unpack(">I", data[16:20])[0]
    height = struct.unpack(">I", data[20:24])[0]
    return width, height


class TestPngBasic:
    def test_returns_bytes(self, backend):
        data = mmdr.render(SIMPLE_FLOWCHART, backend=backend).png()
        assert isinstance(data, bytes), f"expected bytes, got {type(data)}"

    def test_valid_png_magic(self, backend):
        data = mmdr.render(SIMPLE_FLOWCHART, backend=backend).png()
        assert is_valid_png(data), f"PNG magic missing, got {data[:8]!r}"

    def test_nonempty(self, backend):
        data = mmdr.render(SIMPLE_FLOWCHART, backend=backend).png()
        assert len(data) > 512

    def test_default_backend(self):
        data = mmdr.render(SIMPLE_FLOWCHART).png()
        assert is_valid_png(data)

    def test_complex_diagram(self, backend):
        data = mmdr.render(COMPLEX_FLOWCHART, backend=backend).png()
        assert is_valid_png(data)


class TestPngDimensions:
    def test_has_positive_dimensions(self, backend):
        data = mmdr.render(SIMPLE_FLOWCHART, backend=backend).png()
        w, h = png_dimensions(data)
        assert w > 0 and h > 0

    def test_mermaid_rs_width_height(self, mermaid_rs):
        data = mmdr.render(SIMPLE_FLOWCHART, backend=mermaid_rs).png(
            width=400.0, height=300.0
        )
        assert is_valid_png(data)

    def test_merman_fit_box(self, merman):
        data = mmdr.render(SIMPLE_FLOWCHART, backend=merman).png(
            width=800.0, height=600.0
        )
        w, h = png_dimensions(data)
        assert w > 0 and h > 0


class TestPngMermaidRsOptions:
    def test_theme_modern(self, mermaid_rs):
        d = mmdr.render(SIMPLE_FLOWCHART, backend=mermaid_rs, theme="modern")
        assert is_valid_png(d.png())

    def test_theme_classic(self, mermaid_rs):
        d = mmdr.render(SIMPLE_FLOWCHART, backend=mermaid_rs, theme="classic")
        assert is_valid_png(d.png())

    def test_aspect_ratio(self, mermaid_rs):
        d = mmdr.render(SIMPLE_FLOWCHART, backend=mermaid_rs, aspect_ratio=(16.0, 9.0))
        assert is_valid_png(d.png())


class TestPngMermanOptions:
    def test_background_white(self, merman):
        d = mmdr.render(SIMPLE_FLOWCHART, backend=merman)
        assert is_valid_png(d.png(background="#ffffff"))

    def test_scale_2x_is_larger_than_1x(self, merman):
        d = mmdr.render(SIMPLE_FLOWCHART, backend=merman)
        data_1x = d.png(scale=1.0)
        data_2x = d.png(scale=2.0)
        assert len(data_2x) > len(data_1x)


class TestPngErrors:
    def test_unknown_backend_raises(self):
        with pytest.raises(ValueError, match="unknown backend"):
            mmdr.render(SIMPLE_FLOWCHART, backend="fake").png()

    def test_invalid_diagram_merman_raises(self, merman):
        with pytest.raises(ValueError):
            mmdr.render("!!!not mermaid###", backend=merman).png()
