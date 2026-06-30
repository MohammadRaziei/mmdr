"""Tests for mmdr.render() — checks that it returns a Diagram with valid SVG."""

import pytest
import mmdr
from mmdr import Diagram
from conftest import (
    SIMPLE_FLOWCHART, COMPLEX_FLOWCHART, SEQUENCE, CLASS_DIAGRAM,
    is_valid_svg,
)


class TestRenderReturnType:
    def test_returns_diagram_object(self, backend):
        result = mmdr.render(SIMPLE_FLOWCHART, backend=backend)
        assert isinstance(result, Diagram)

    def test_default_backend_returns_diagram(self):
        result = mmdr.render(SIMPLE_FLOWCHART)
        assert isinstance(result, Diagram)

    def test_repr(self, backend):
        d = mmdr.render(SIMPLE_FLOWCHART, backend=backend)
        assert "Diagram" in repr(d)
        assert backend in repr(d)


class TestSvgOutput:
    def test_svg_returns_string(self, backend):
        svg = mmdr.render(SIMPLE_FLOWCHART, backend=backend).svg()
        assert isinstance(svg, str)

    def test_svg_is_valid(self, backend):
        svg = mmdr.render(SIMPLE_FLOWCHART, backend=backend).svg()
        assert is_valid_svg(svg), f"Not valid SVG: {svg[:200]}"

    def test_svg_contains_namespace(self, backend):
        svg = mmdr.render(SIMPLE_FLOWCHART, backend=backend).svg()
        assert 'xmlns="http://www.w3.org/2000/svg"' in svg

    def test_svg_is_cached(self, backend):
        d = mmdr.render(SIMPLE_FLOWCHART, backend=backend)
        assert d.svg() is d.svg()  # same object = cached

    def test_flowchart_complex(self, backend):
        assert is_valid_svg(mmdr.render(COMPLEX_FLOWCHART, backend=backend).svg())

    def test_sequence_diagram(self, backend):
        assert is_valid_svg(mmdr.render(SEQUENCE, backend=backend).svg())

    def test_class_diagram(self, backend):
        assert is_valid_svg(mmdr.render(CLASS_DIAGRAM, backend=backend).svg())

    def test_pie_chart(self, backend):
        src = 'pie title Pets\n    "Dogs" : 40\n    "Cats" : 60'
        assert is_valid_svg(mmdr.render(src, backend=backend).svg())


class TestMermaidRsOptions:
    def test_theme_modern(self, mermaid_rs):
        svg = mmdr.render(SIMPLE_FLOWCHART, backend=mermaid_rs, theme="modern").svg()
        assert is_valid_svg(svg)

    def test_theme_classic(self, mermaid_rs):
        svg = mmdr.render(SIMPLE_FLOWCHART, backend=mermaid_rs, theme="classic").svg()
        assert is_valid_svg(svg)

    def test_node_spacing(self, mermaid_rs):
        svg = mmdr.render(SIMPLE_FLOWCHART, backend=mermaid_rs, node_spacing=100.0).svg()
        assert is_valid_svg(svg)

    def test_rank_spacing(self, mermaid_rs):
        svg = mmdr.render(SIMPLE_FLOWCHART, backend=mermaid_rs, rank_spacing=120.0).svg()
        assert is_valid_svg(svg)

    def test_aspect_ratio(self, mermaid_rs):
        svg = mmdr.render(SIMPLE_FLOWCHART, backend=mermaid_rs, aspect_ratio=(16.0, 9.0)).svg()
        assert is_valid_svg(svg)


class TestErrors:
    def test_unknown_backend_raises(self):
        with pytest.raises(ValueError, match="unknown backend"):
            mmdr.render(SIMPLE_FLOWCHART, backend="nonexistent").svg()

    def test_invalid_diagram_merman(self, merman):
        # merman raises ValueError for input it can't parse at all
        with pytest.raises(ValueError):
            mmdr.render("this is !!!not### mermaid", backend=merman).svg()

    def test_invalid_diagram_mermaid_rs_returns_error_svg(self, mermaid_rs):
        # mermaid-rs-renderer renders a visual error diagram (SVG) rather than
        # raising — this is intentional upstream behaviour.
        result = mmdr.render("this is !!!not### mermaid", backend=mermaid_rs).svg()
        assert isinstance(result, str)  # doesn't raise, returns something
