"""
Quick manual smoke test.

Run after building the extension locally, e.g.:

    pip install maturin
    maturin develop --release
    python examples/test.py
"""

import mmdr

svg = mmdr.render("flowchart LR; A-->B-->C")
assert "<svg" in svg
print("SVG render OK, length:", len(svg))

png_bytes = mmdr.render_png("flowchart LR; A-->B-->C")
assert png_bytes[:8] == b"\x89PNG\r\n\x1a\n"
with open("test_output.png", "wb") as f:
    f.write(png_bytes)
print("PNG render OK, wrote test_output.png (", len(png_bytes), "bytes)")

print("version:", mmdr.__version__)
