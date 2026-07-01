"""Tests for Diagram.png() and Diagram.raw() — all rasterized via resvg."""

import struct
import pytest
import mmdr
from conftest import SIMPLE_FLOWCHART, COMPLEX_FLOWCHART, is_valid_png


def png_wh(data: bytes) -> tuple[int, int]:
    """Extract (width, height) from PNG IHDR — no Pillow needed."""
    assert isinstance(data, bytes), f"expected bytes, got {type(data).__name__}"
    assert data[:8] == b"\x89PNG\r\n\x1a\n", f"not PNG, got {data[:8]!r}"
    return struct.unpack(">II", data[16:24])


class TestPng:
    def test_returns_bytes(self, backend):
        result = mmdr.render(SIMPLE_FLOWCHART, backend=backend).png()
        assert isinstance(result, bytes), f"expected bytes, got {type(result).__name__}"

    def test_valid_magic(self, backend):
        data = mmdr.render(SIMPLE_FLOWCHART, backend=backend).png()
        assert is_valid_png(data), f"PNG magic missing, got {data[:8]!r}"

    def test_nonempty(self, backend):
        assert len(mmdr.render(SIMPLE_FLOWCHART, backend=backend).png()) > 512

    def test_default_backend(self):
        data = mmdr.render(SIMPLE_FLOWCHART).png()
        assert is_valid_png(data)

    def test_complex_diagram(self, backend):
        assert is_valid_png(mmdr.render(COMPLEX_FLOWCHART, backend=backend).png())

    def test_positive_dimensions(self, backend):
        data = mmdr.render(SIMPLE_FLOWCHART, backend=backend).png()
        w, h = png_wh(data)
        assert w > 0 and h > 0

    def test_width_height_hint(self, backend):
        data = mmdr.render(SIMPLE_FLOWCHART, backend=backend).png(width=400.0, height=300.0)
        assert is_valid_png(data)

    def test_background_white(self, backend):
        data = mmdr.render(SIMPLE_FLOWCHART, backend=backend).png(background="#ffffff")
        assert is_valid_png(data)

    def test_background_transparent(self, backend):
        data = mmdr.render(SIMPLE_FLOWCHART, backend=backend).png(background=None)
        assert is_valid_png(data)

    def test_unknown_backend_raises(self):
        with pytest.raises(ValueError, match="unknown backend"):
            mmdr.render(SIMPLE_FLOWCHART, backend="fake").png()


class TestRaw:
    def test_returns_tuple(self, backend):
        result = mmdr.render(SIMPLE_FLOWCHART, backend=backend).raw()
        assert isinstance(result, tuple) and len(result) == 3

    def test_raw_is_bytes(self, backend):
        raw, w, h = mmdr.render(SIMPLE_FLOWCHART, backend=backend).raw()
        assert isinstance(raw, bytes), f"expected bytes, got {type(raw).__name__}"

    def test_dimensions_positive(self, backend):
        raw, w, h = mmdr.render(SIMPLE_FLOWCHART, backend=backend).raw()
        assert w > 0 and h > 0

    def test_stride_is_rgba(self, backend):
        raw, w, h = mmdr.render(SIMPLE_FLOWCHART, backend=backend).raw()
        # RGBA8888: exactly width * height * 4 bytes
        assert len(raw) == w * h * 4, (
            f"expected {w*h*4} bytes for {w}x{h} RGBA, got {len(raw)}"
        )

    def test_background_white(self, backend):
        raw, w, h = mmdr.render(SIMPLE_FLOWCHART, backend=backend).raw(background="#ffffff")
        assert isinstance(raw, bytes) and len(raw) == w * h * 4


class TestNumpy:
    def test_shape_and_dtype(self, backend):
        pytest.importorskip("numpy")
        import numpy as np
        arr = mmdr.render(SIMPLE_FLOWCHART, backend=backend).numpy()
        assert isinstance(arr, np.ndarray)
        assert arr.ndim == 3
        assert arr.shape[2] == 4       # RGBA
        assert arr.dtype == np.uint8

    def test_numpy_raises_without_numpy(self, backend, monkeypatch):
        import builtins
        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "numpy":
                raise ImportError("mocked: numpy not installed")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)
        with pytest.raises(ImportError, match="numpy"):
            mmdr.render(SIMPLE_FLOWCHART, backend=backend).numpy()

    def test_numpy_consistent_with_raw(self, backend):
        """numpy() should be exactly np.frombuffer(raw, uint8).reshape(h, w, 4)."""
        pytest.importorskip("numpy")
        import numpy as np
        d = mmdr.render(SIMPLE_FLOWCHART, backend=backend)
        raw, w, h = d.raw()
        expected = np.frombuffer(raw, dtype=np.uint8).reshape(h, w, 4)
        actual = d.numpy()
        assert np.array_equal(actual, expected)
