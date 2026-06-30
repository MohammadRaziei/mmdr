"""Shared fixtures and helpers."""

import pytest
import mmdr

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
    return isinstance(text, str) and "<svg" in text and "</svg>" in text


def is_valid_png(data: bytes) -> bool:
    return isinstance(data, bytes) and data[:8] == PNG_MAGIC


@pytest.fixture(params=mmdr.backends())
def backend(request):
    """Parametrize every test that uses this fixture over all compiled backends."""
    return request.param


@pytest.fixture
def mermaid_rs():
    if "mermaid-rs-renderer" not in mmdr.backends():
        pytest.skip("mermaid-rs-renderer not compiled in")
    return "mermaid-rs-renderer"


@pytest.fixture
def merman():
    if "merman" not in mmdr.backends():
        pytest.skip("merman not compiled in")
    return "merman"
