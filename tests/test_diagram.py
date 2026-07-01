"""Tests for the Diagram object: .save(), .pdf(), .__repr__(), Jupyter."""

import pytest
import mmdr
from mmdr import Diagram
from conftest import SIMPLE_FLOWCHART, is_valid_svg, is_valid_png


class TestDiagramObject:
    def test_is_diagram(self, backend):
        assert isinstance(mmdr.render(SIMPLE_FLOWCHART, backend=backend), Diagram)

    def test_repr(self, backend):
        d = mmdr.render(SIMPLE_FLOWCHART, backend=backend)
        assert "Diagram" in repr(d)
        assert backend in repr(d)
        assert "flowchart" in repr(d)

    def test_svg_cached(self, backend):
        d = mmdr.render(SIMPLE_FLOWCHART, backend=backend)
        assert d.svg() is d.svg()

    def test_png_not_same_object(self, backend):
        d = mmdr.render(SIMPLE_FLOWCHART, backend=backend)
        assert d.png() is not d.png()  # not cached — correct

    def test_jupyter_repr_svg(self, backend):
        svg = mmdr.render(SIMPLE_FLOWCHART, backend=backend)._repr_svg_()
        assert is_valid_svg(svg)


class TestSave:
    def test_save_svg(self, backend, tmp_path):
        out = tmp_path / "out.svg"
        mmdr.render(SIMPLE_FLOWCHART, backend=backend).save(str(out))
        assert is_valid_svg(out.read_text(encoding="utf-8"))

    def test_save_png(self, backend, tmp_path):
        out = tmp_path / "out.png"
        mmdr.render(SIMPLE_FLOWCHART, backend=backend).save(str(out))
        assert is_valid_png(out.read_bytes())

    def test_save_png_with_options(self, backend, tmp_path):
        out = tmp_path / "out.png"
        mmdr.render(SIMPLE_FLOWCHART, backend=backend).save(
            str(out), width=800.0, background="#ffffff"
        )
        assert is_valid_png(out.read_bytes())

    def test_save_creates_file(self, backend, tmp_path):
        out = tmp_path / "diagram.svg"
        assert not out.exists()
        mmdr.render(SIMPLE_FLOWCHART, backend=backend).save(str(out))
        assert out.exists() and out.stat().st_size > 0

    def test_save_unknown_extension_raises(self, backend, tmp_path):
        out = tmp_path / "out.webp"
        with pytest.raises(ValueError, match="Cannot infer"):
            mmdr.render(SIMPLE_FLOWCHART, backend=backend).save(str(out))


class TestPdf:
    def test_raises_not_implemented(self, backend):
        with pytest.raises(NotImplementedError):
            mmdr.render(SIMPLE_FLOWCHART, backend=backend).pdf()
