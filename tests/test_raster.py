"""Tests for Diagram.png() / .raw() / .numpy() rasterization (novasvg)."""

import struct

import pytest

import mmdr

np = pytest.importorskip("numpy")  # only the pixel-inspection tests need it

# 100x50 canvas: left half = 50 % transparent red, right circle = opaque blue.
SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="50">'
    '<rect width="50" height="50" fill="#ff0000" fill-opacity="0.5"/>'
    '<circle cx="75" cy="25" r="20" fill="#0000ff"/></svg>'
)


def diagram_from_svg(svg: str) -> mmdr.Diagram:
    """A Diagram whose SVG is fixed, so pixels are predictable."""
    d = mmdr.Diagram("flowchart LR; A-->B")
    d._svg_cache = svg
    return d


def png_wh(data: bytes) -> tuple[int, int]:
    return struct.unpack(">II", data[16:24])


def pixels(d: mmdr.Diagram, **kwargs):
    raw, w, h = d.raw(**kwargs)
    return np.frombuffer(raw, np.uint8).reshape(h, w, 4)


def test_novasvg_is_a_runtime_dependency():
    import novasvg

    assert novasvg.version_string()


class TestSize:
    def test_intrinsic_size_by_default(self):
        assert png_wh(diagram_from_svg(SVG).png()) == (100, 50)

    def test_width_only_keeps_aspect_ratio(self):
        assert png_wh(diagram_from_svg(SVG).png(width=200)) == (200, 100)

    def test_height_only_keeps_aspect_ratio(self):
        assert png_wh(diagram_from_svg(SVG).png(height=100)) == (200, 100)

    def test_width_and_height(self):
        assert png_wh(diagram_from_svg(SVG).png(width=300, height=300)) == (300, 300)

    def test_float_sizes_are_rounded(self):
        assert png_wh(diagram_from_svg(SVG).png(width=200.4)) == (200, 100)

    def test_real_diagram_scales(self):
        w, h = png_wh(mmdr.render("flowchart LR; A-->B").png(width=640))
        assert w == 640 and h > 0


class TestPixels:
    def test_raw_layout(self):
        raw, w, h = diagram_from_svg(SVG).raw()
        assert (w, h) == (100, 50)
        assert len(raw) == w * h * 4

    def test_transparent_by_default(self):
        assert tuple(pixels(diagram_from_svg(SVG))[0, 99]) == (0, 0, 0, 0)

    def test_channel_order_is_rgba(self):
        assert tuple(pixels(diagram_from_svg(SVG))[25, 75]) == (0, 0, 255, 255)

    def test_alpha_is_straight_not_premultiplied(self):
        r, g, b, a = pixels(diagram_from_svg(SVG))[10, 10]
        assert r == 255 and g == 0 and b == 0
        assert 120 <= a <= 135

    @pytest.mark.parametrize(
        "color, expected",
        [
            ("#ffffff", (255, 255, 255, 255)),
            ("ffffff", (255, 255, 255, 255)),
            ("#fff", (255, 255, 255, 255)),
            ("#102030", (16, 32, 48, 255)),
            ("#10203040", (16, 32, 48, 64)),
            ("white", (255, 255, 255, 255)),
            ("red", (255, 0, 0, 255)),
            ("transparent", (0, 0, 0, 0)),
        ],
    )
    def test_background_color(self, color, expected):
        got = [int(v) for v in pixels(diagram_from_svg(SVG), background=color)[0, 99]]
        # Semi-transparent colors go through premultiply/unpremultiply,
        # so allow +-1 rounding on the color channels; alpha is exact.
        assert got[3] == expected[3]
        assert all(abs(g - e) <= 1 for g, e in zip(got[:3], expected[:3]))

    def test_numpy_matches_raw(self):
        d = mmdr.render("flowchart LR; A-->B")
        assert np.array_equal(
            d.numpy(background="#ffffff"), pixels(d, background="#ffffff")
        )

    def test_diagram_text_is_drawn(self, backend):
        """Labels must survive the resvg-safe pipeline and show up as pixels."""
        arr = mmdr.render("flowchart LR; A[Hello]-->B[World]", backend=backend).numpy(
            background="#ffffff"
        )
        assert (arr[..., :3] < 128).any(), "expected dark text/strokes on white"


class TestErrors:
    @pytest.mark.parametrize("bad", ["not svg", "<svg", ""])
    def test_invalid_svg_raises_value_error(self, bad):
        d = diagram_from_svg(bad)
        with pytest.raises(ValueError, match="SVG"):
            d.png()
        with pytest.raises(ValueError, match="SVG"):
            d.raw()

    @pytest.mark.parametrize("bad", ["#12", "#gggggg", "rgb(1,2,3)", "", "not a color"])
    def test_invalid_background_raises(self, bad):
        with pytest.raises(ValueError):
            diagram_from_svg(SVG).png(background=bad)

    def test_zero_sized_svg_raises(self):
        d = diagram_from_svg('<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0"/>')
        with pytest.raises(ValueError):
            d.png()
