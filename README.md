# mmdr

Fast, headless Mermaid diagram rendering — powered by Rust, zero Python dependencies.

```bash
pip install mmdr
```

Two SVG backends. All rasterization (PNG, raw pixels) via [resvg](https://github.com/RazrFalcon/resvg) inside the extension — no Pillow, no Cairo, no browser.

| Backend | Crate | Diagram support |
|---|---|---|
| `merman` **(default)** | [Latias94/merman](https://github.com/Latias94/merman) | Full Mermaid @11.15.0 parity |
| `mermaid-rs-renderer` | [1jehuang/mermaid-rs-renderer](https://github.com/1jehuang/mermaid-rs-renderer) | Common types, faster |

---

## CLI

After `pip install mmdr` you get an `mmdr` command. It works like
[mermaid-cli](https://github.com/mermaid-js/mermaid-cli)'s `mmdc`, but
talks to native Rust — no Node.js, no browser.

### Basic usage

```bash
# SVG from a file
mmdr -i diagram.mmd -o output.svg

# PNG from a file
mmdr -i diagram.mmd -o output.png

# Read from stdin, write to stdout
echo 'flowchart LR; A-->B-->C' | mmdr -i - -o -

# Pipe and redirect
mmdr -i diagram.mmd -o - > output.svg
```

### Options

```bash
mmdr -i diagram.mmd -o output.png \
  --backend mermaid-rs-renderer \   # choose backend (default: merman)
  --width 1200 \                    # PNG canvas width in pixels
  --height 800 \                    # PNG canvas height in pixels
  --background '#ffffff' \          # PNG background color
  --theme classic                   # mermaid-rs-renderer only

mmdr --info        # render Mermaid's built-in info diagram, print its text
mmdr --version     # print mmdr version
mmdr -h            # full help
```

### Real-world examples

```bash
# Render a sequence diagram to PNG with white background
mmdr -i sequence.mmd -o sequence.png --background '#ffffff' --width 1000

# Use the faster backend for a simple flowchart
mmdr -i flow.mmd -o flow.svg --backend mermaid-rs-renderer

# Batch convert all .mmd files in a directory
for f in diagrams/*.mmd; do
    mmdr -i "$f" -o "${f%.mmd}.svg"
done
```

---

## Python API

### `mmdr.render(diagram, backend=None, **opts) → Diagram`

Returns a `Diagram` object. The SVG is rendered **lazily** — only when you
first call `.svg()`, `.png()`, `.save()`, etc.

```python
import mmdr

d = mmdr.render("flowchart LR; A-->B-->C")
```

---

### `Diagram.svg() → str`

Returns the SVG source as a string. Cached after the first call.

```python
svg = mmdr.render("flowchart LR; A-->B-->C").svg()
print(svg)  # <svg xmlns="http://www.w3.org/2000/svg" ...>...</svg>

# Write manually
with open("output.svg", "w") as f:
    f.write(svg)
```

---

### `Diagram.png(width=None, height=None, background=None) → bytes`

Rasterizes the SVG via resvg and returns PNG bytes.

```python
png = mmdr.render("flowchart LR; A-->B-->C").png()

# With options
png = mmdr.render("sequenceDiagram\n  Alice->>Bob: Hello").png(
    width=800,
    height=600,
    background="#ffffff",   # hex color, transparent by default
)

with open("output.png", "wb") as f:
    f.write(png)
```

---

### `Diagram.raw(width=None, height=None, background=None) → (bytes, int, int)`

Returns raw RGBA8888 pixel data as `(bytes, width, height)`.
Stride is `width * 4`. No encoding — the pixel buffer comes straight out of resvg.

```python
raw, w, h = mmdr.render("flowchart LR; A-->B-->C").raw()
print(f"{w}x{h}, {len(raw)} bytes")  # e.g. 640x480, 1228800 bytes
```

---

### `Diagram.numpy(width=None, height=None, background=None) → np.ndarray`

Returns an `(H, W, 4)` NumPy array, dtype `uint8`, RGBA. Built on top of
`.raw()` — no Pillow needed, just `numpy`.

```python
import numpy as np
import mmdr

arr = mmdr.render("flowchart LR; A-->B-->C").numpy()
print(arr.shape)   # (480, 640, 4)
print(arr.dtype)   # uint8

# Flip upside-down
flipped = np.flipud(arr)

# Drop alpha channel → RGB
rgb = arr[:, :, :3]
```

---

### `Diagram.save(output, width=None, height=None, background=None)`

Saves to a file. The format is inferred from the extension (`.svg` or `.png`).

```python
d = mmdr.render("flowchart LR; A-->B-->C")

d.save("output.svg")                              # SVG
d.save("output.png")                              # PNG, transparent bg
d.save("output.png", width=1200, background="#ffffff")  # PNG with options
```

---

### Backends

```python
mmdr.backends()
# ['merman', 'mermaid-rs-renderer']

# Default (merman) — full diagram support
d = mmdr.render("kanban\n  todo\n    Task A\n    Task B")
d.svg()

# mermaid-rs-renderer — faster for common diagrams
d = mmdr.render(
    "flowchart LR; A-->B-->C",
    backend="mermaid-rs-renderer",
    theme="classic",       # "modern" (default) or "classic"
    node_spacing=60.0,
    rank_spacing=80.0,
    aspect_ratio=(16, 9),
)
d.svg()
```

---

### Jupyter / IPython

`Diagram` implements `_repr_svg_()`, so it renders inline automatically:

```python
import mmdr

mmdr.render("flowchart LR; A-->B-->C")   # displays inline in Jupyter
```

---

### Low-level SVG utilities

The Rust extension also exports `svg_to_png` and `svg_to_raw` directly,
for when you already have an SVG string from somewhere else:

```python
from mmdr import svg_to_png, svg_to_raw

my_svg = open("existing.svg").read()

png = svg_to_png(my_svg, width=800, background="#ffffff")
raw, w, h = svg_to_raw(my_svg)
```

---

## Supported diagram types

| Diagram | merman | mermaid-rs-renderer |
|---|:---:|:---:|
| flowchart / graph | ✅ | ✅ |
| sequenceDiagram | ✅ | ✅ |
| classDiagram | ✅ | ✅ |
| stateDiagram | ✅ | ✅ |
| erDiagram | ✅ | ✅ |
| pie | ✅ | ✅ |
| gantt | ✅ | ✅ |
| timeline | ✅ | ✅ |
| mindmap | ✅ | ✅ |
| gitGraph | ✅ | ✅ |
| xychart | ✅ | ✅ |
| block diagram | ✅ | ❌ |
| architecture | ✅ | ❌ |
| kanban | ✅ | ❌ |
| c4diagram | ✅ | ❌ |
| sankey | ✅ | ❌ |
| packet | ✅ | ❌ |

---

## License

MIT
