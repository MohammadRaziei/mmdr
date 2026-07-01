"""Tests for mmdr.render() — SVG output via .svg()."""

import pytest
import mmdr
from mmdr import Diagram
from conftest import (
    SIMPLE_FLOWCHART, COMPLEX_FLOWCHART, SEQUENCE, CLASS_DIAGRAM,
    is_valid_svg,
)


class TestReturnType:
    def test_returns_diagram(self, backend):
        assert isinstance(mmdr.render(SIMPLE_FLOWCHART, backend=backend), Diagram)

    def test_default_is_merman(self):
        d = mmdr.render(SIMPLE_FLOWCHART)
        assert "merman" in repr(d) or d._backend is None

    def test_repr(self, backend):
        d = mmdr.render(SIMPLE_FLOWCHART, backend=backend)
        assert "Diagram" in repr(d)
        assert backend in repr(d)


class TestSvg:
    def test_returns_string(self, backend):
        assert isinstance(mmdr.render(SIMPLE_FLOWCHART, backend=backend).svg(), str)

    def test_valid_svg(self, backend):
        svg = mmdr.render(SIMPLE_FLOWCHART, backend=backend).svg()
        assert is_valid_svg(svg), f"Not valid SVG:\n{svg[:300]}"

    def test_has_xmlns(self, backend):
        svg = mmdr.render(SIMPLE_FLOWCHART, backend=backend).svg()
        assert 'xmlns="http://www.w3.org/2000/svg"' in svg

    def test_cached(self, backend):
        d = mmdr.render(SIMPLE_FLOWCHART, backend=backend)
        assert d.svg() is d.svg()

    def test_complex_flowchart(self, backend):
        assert is_valid_svg(mmdr.render(COMPLEX_FLOWCHART, backend=backend).svg())

    def test_sequence(self, backend):
        assert is_valid_svg(mmdr.render(SEQUENCE, backend=backend).svg())

    def test_class_diagram(self, backend):
        assert is_valid_svg(mmdr.render(CLASS_DIAGRAM, backend=backend).svg())

    def test_pie(self, backend):
        src = 'pie title Pets\n    "Dogs" : 40\n    "Cats" : 60'
        assert is_valid_svg(mmdr.render(src, backend=backend).svg())


class TestMermaidRsOptions:
    def test_theme_modern(self, mermaid_rs):
        assert is_valid_svg(mmdr.render(SIMPLE_FLOWCHART, backend=mermaid_rs, theme="modern").svg())

    def test_theme_classic(self, mermaid_rs):
        assert is_valid_svg(mmdr.render(SIMPLE_FLOWCHART, backend=mermaid_rs, theme="classic").svg())

    def test_node_spacing(self, mermaid_rs):
        assert is_valid_svg(mmdr.render(SIMPLE_FLOWCHART, backend=mermaid_rs, node_spacing=100.0).svg())

    def test_rank_spacing(self, mermaid_rs):
        assert is_valid_svg(mmdr.render(SIMPLE_FLOWCHART, backend=mermaid_rs, rank_spacing=120.0).svg())

    def test_aspect_ratio(self, mermaid_rs):
        assert is_valid_svg(mmdr.render(SIMPLE_FLOWCHART, backend=mermaid_rs, aspect_ratio=(16.0, 9.0)).svg())


class TestErrors:
    def test_unknown_backend_raises(self):
        with pytest.raises(ValueError, match="unknown backend"):
            mmdr.render(SIMPLE_FLOWCHART, backend="nonexistent").svg()

    def test_invalid_diagram_merman(self, merman):
        with pytest.raises(ValueError):
            mmdr.render("this is !!!not### mermaid", backend=merman).svg()

    def test_invalid_diagram_mermaid_rs_returns_error_svg(self, mermaid_rs):
        # mermaid-rs-renderer renders an error SVG instead of raising
        result = mmdr.render("!!!not mermaid###", backend=mermaid_rs).svg()
        assert isinstance(result, str)
