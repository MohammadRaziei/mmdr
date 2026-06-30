"""Tests for the Diagram object: .save(), .pdf(), .numpy(), .__repr__()."""

import struct
import tempfile
from pathlib import Path

import pytest
import mmdr
from mmdr import Diagram
from conftest import SIMPLE_FLOWCHART, is_valid_svg, is_valid_png


class TestDiagramObject:
    def test_is_diagram_instance(self, backend):
        assert isinstance(mmdr.render(SIMPLE_FLOWCHART, backend=backend), Diagram)

    def test_repr_contains_backend(self, backend):
        d = mmdr.render(SIMPLE_FLOWCHART, backend=backend)
        assert backend in repr(d)

    def test_repr_contains_first_line(self, backend):
        d = mmdr.render(SIMPLE_FLOWCHART, backend=backend)
        assert "flowchart" in repr(d)

    def test_svg_is_cached(self, backend):
        d = mmdr.render(SIMPLE_FLOWCHART, backend=backend)
        svg1 = d.svg()
        svg2 = d.svg()
        assert svg1 is svg2

    def test_png_not_cached(self, backend):
        # .png() is not cached — each call may use different kwargs
        d = mmdr.render(SIMPLE_FLOWCHART, backend=backend)
        p1 = d.png()
        p2 = d.png()
        # both should be valid, not necessarily same object
        assert is_valid_png(p1) and is_valid_png(p2)


class TestSave:
    def test_save_svg(self, backend, tmp_path):
        out = tmp_path / "out.svg"
        mmdr.render(SIMPLE_FLOWCHART, backend=backend).save(str(out))
        content = out.read_text(encoding="utf-8")
        assert is_valid_svg(content)

    def test_save_png(self, backend, tmp_path):
        out = tmp_path / "out.png"
        mmdr.render(SIMPLE_FLOWCHART, backend=backend).save(str(out))
        assert is_valid_png(out.read_bytes())

    def test_save_png_with_kwargs(self, mermaid_rs, tmp_path):
        out = tmp_path / "out.png"
        mmdr.render(SIMPLE_FLOWCHART, backend=mermaid_rs).save(str(out), width=800.0)
        assert is_valid_png(out.read_bytes())

    def test_save_unknown_extension_raises(self, backend, tmp_path):
        out = tmp_path / "out.webp"
        with pytest.raises(ValueError, match="Cannot infer"):
            mmdr.render(SIMPLE_FLOWCHART, backend=backend).save(str(out))

    def test_save_creates_file(self, backend, tmp_path):
        out = tmp_path / "diagram.svg"
        assert not out.exists()
        mmdr.render(SIMPLE_FLOWCHART, backend=backend).save(str(out))
        assert out.exists()
        assert out.stat().st_size > 0


class TestPdf:
    def test_pdf_raises_not_implemented(self, backend):
        with pytest.raises(NotImplementedError):
            mmdr.render(SIMPLE_FLOWCHART, backend=backend).pdf()


class TestNumpy:
    def test_numpy_raises_import_error_without_numpy(self, backend, monkeypatch):
        import builtins
        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "numpy":
                raise ImportError("numpy not installed")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)
        with pytest.raises(ImportError, match="numpy"):
            mmdr.render(SIMPLE_FLOWCHART, backend=backend).numpy()

    @pytest.mark.skipif(
        not __import__("importlib").util.find_spec("numpy") or
        not __import__("importlib").util.find_spec("PIL"),
        reason="requires numpy and Pillow"
    )
    def test_numpy_returns_array(self, backend):
        import numpy as np
        arr = mmdr.render(SIMPLE_FLOWCHART, backend=backend).numpy()
        assert isinstance(arr, np.ndarray)
        assert arr.ndim == 3           # H × W × channels
        assert arr.shape[2] in (3, 4)  # RGB or RGBA
        assert arr.dtype == np.uint8


class TestJupyterIntegration:
    def test_repr_svg_returns_svg_string(self, backend):
        d = mmdr.render(SIMPLE_FLOWCHART, backend=backend)
        svg = d._repr_svg_()
        assert is_valid_svg(svg)
