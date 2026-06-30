"""Tests for mmdr.render() — SVG output."""

import pytest
import mmdr
from conftest import (
    SIMPLE_FLOWCHART,
    COMPLEX_FLOWCHART,
    SEQUENCE,
    CLASS_DIAGRAM,
    is_valid_svg,
)


class TestRenderBasic:
    def test_returns_string(self, backend):
        result = mmdr.render(SIMPLE_FLOWCHART, backend=backend)
        assert isinstance(result, str)

    def test_output_is_valid_svg(self, backend):
        result = mmdr.render(SIMPLE_FLOWCHART, backend=backend)
        assert is_valid_svg(result), f"Not valid SVG: {result[:200]}"

    def test_svg_contains_namespace(self, backend):
        result = mmdr.render(SIMPLE_FLOWCHART, backend=backend)
        assert 'xmlns="http://www.w3.org/2000/svg"' in result

    def test_nonempty_output(self, backend):
        result = mmdr.render(SIMPLE_FLOWCHART, backend=backend)
        assert len(result) > 100

    def test_default_backend_is_mermaid_rs(self):
        """Calling render() without backend= should not raise."""
        result = mmdr.render(SIMPLE_FLOWCHART)
        assert is_valid_svg(result)


class TestRenderDiagramTypes:
    def test_flowchart_simple(self, backend):
        svg = mmdr.render(SIMPLE_FLOWCHART, backend=backend)
        assert is_valid_svg(svg)

    def test_flowchart_complex(self, backend):
        svg = mmdr.render(COMPLEX_FLOWCHART, backend=backend)
        assert is_valid_svg(svg)

    def test_sequence_diagram(self, backend):
        svg = mmdr.render(SEQUENCE, backend=backend)
        assert is_valid_svg(svg)

    def test_class_diagram(self, backend):
        svg = mmdr.render(CLASS_DIAGRAM, backend=backend)
        assert is_valid_svg(svg)

    def test_pie_chart(self, backend):
        svg = mmdr.render('pie title Pets\n    "Dogs" : 40\n    "Cats" : 60', backend=backend)
        assert is_valid_svg(svg)


class TestRenderMermaidRsOptions:
    """Options that only apply to the mermaid-rs-renderer backend."""

    def test_theme_modern(self, mermaid_rs):
        svg = mmdr.render(SIMPLE_FLOWCHART, backend=mermaid_rs, theme="modern")
        assert is_valid_svg(svg)

    def test_theme_classic(self, mermaid_rs):
        svg = mmdr.render(SIMPLE_FLOWCHART, backend=mermaid_rs, theme="classic")
        assert is_valid_svg(svg)

    def test_node_spacing(self, mermaid_rs):
        svg = mmdr.render(SIMPLE_FLOWCHART, backend=mermaid_rs, node_spacing=100.0)
        assert is_valid_svg(svg)

    def test_rank_spacing(self, mermaid_rs):
        svg = mmdr.render(SIMPLE_FLOWCHART, backend=mermaid_rs, rank_spacing=120.0)
        assert is_valid_svg(svg)

    def test_aspect_ratio(self, mermaid_rs):
        svg = mmdr.render(SIMPLE_FLOWCHART, backend=mermaid_rs, aspect_ratio=(16.0, 9.0))
        assert is_valid_svg(svg)

    def test_all_options_combined(self, mermaid_rs):
        svg = mmdr.render(
            COMPLEX_FLOWCHART,
            backend=mermaid_rs,
            theme="classic",
            node_spacing=60.0,
            rank_spacing=80.0,
            aspect_ratio=(4.0, 3.0),
        )
        assert is_valid_svg(svg)


class TestRenderErrors:
    def test_unknown_backend_raises(self):
        with pytest.raises(ValueError, match="unknown backend"):
            mmdr.render(SIMPLE_FLOWCHART, backend="nonexistent")

    def test_invalid_diagram_raises(self, backend):
        with pytest.raises(ValueError):
            mmdr.render("this is not valid mermaid at all !!!", backend=backend)

    def test_empty_string_raises(self, backend):
        with pytest.raises(ValueError):
            mmdr.render("", backend=backend)
