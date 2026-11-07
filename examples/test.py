"""
Quick smoke test.

    maturin develop --release
    python examples/test.py
"""
import mmdr

print("backends:", mmdr.backends())
assert "mermaid-rs-renderer" in mmdr.backends()
assert "merman" in mmdr.backends()

DIAGRAM = "flowchart LR; A-->B-->C"

for backend in mmdr.backends():
    print(f"\n--- {backend} ---")

    d = mmdr.render(DIAGRAM, backend=backend)
    svg = d.svg()
    assert "<svg" in svg
    print(f"SVG OK ({len(svg)} bytes)")

    png = d.png()
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    print(f"PNG OK ({len(png)} bytes)")

print("\nAll backends OK")
