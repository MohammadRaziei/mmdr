"""
Shared fixtures and helpers for the mmdr test suite.

Run with:
    pip install pytest
    maturin develop --release
    pytest tests/ -v
"""

import pytest
import mmdr

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SIMPLE_FLOWCHART = "flowchart LR\n    A-->B-->C"

COMPLEX_FLOWCHART = """
flowchart TD
    A[Start] --> B{Decision}
    B -- Yes --> C[Do thing]
    B -- No  --> D[Skip]
    C --> E[End]
    D --> E
"""

SEQUENCE = """
sequenceDiagram
    Alice->>Bob: Hello
    Bob-->>Alice: Hi back
"""

CLASS_DIAGRAM = """
classDiagram
    class Animal {
        +String name
        +speak() void
    }
    class Dog {
        +fetch() void
    }
    Animal <|-- Dog
"""

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def is_valid_svg(text: str) -> bool:
    return text.strip().startswith("<svg") and "</svg>" in text


def is_valid_png(data: bytes) -> bool:
    return data[:8] == PNG_MAGIC


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(params=mmdr.backends())
def backend(request):
    """Parametrize every test that uses this fixture over all compiled backends."""
    return request.param


@pytest.fixture
def mermaid_rs():
    """Force mermaid-rs-renderer backend, skip if not compiled in."""
    if "mermaid-rs-renderer" not in mmdr.backends():
        pytest.skip("mermaid-rs-renderer backend not compiled in")
    return "mermaid-rs-renderer"


@pytest.fixture
def merman():
    """Force merman backend, skip if not compiled in."""
    if "merman" not in mmdr.backends():
        pytest.skip("merman backend not compiled in")
    return "merman"
