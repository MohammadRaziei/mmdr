# mmdr

Render Mermaid diagrams from Python or the command line — fast, native, no browser required.

Most Mermaid rendering tools work by spinning up a headless browser and running the official JavaScript library. This works, but it's slow to start, heavy to install, and awkward to embed in a pipeline. **mmdr** takes a different approach: the rendering engine is written in Rust and ships as a compiled Python extension. Install it with pip, import it, and start rendering — no Node.js, no Puppeteer, no Chrome, no JS runtime of any kind.

```bash
pip install mmdr
```

That's it. No system dependencies, no extra steps.

**Output formats:** SVG · PNG · raw RGBA pixels · NumPy array

**Two backends, one package:**
- `merman` *(default)* — targets full parity with the official Mermaid @11.15.0 library, supports all diagram types including newer ones like kanban, architecture, and c4
- `mermaid-rs-renderer` — a lighter, faster alternative that covers the most common diagram types

---

## CLI

mmdr ships with a command-line tool that works similarly to the official
[mermaid-cli](https://github.com/mermaid-js/mermaid-cli) (`mmdc`), but
starts in milliseconds instead of seconds because there's no browser to boot.

### Quick start

```bash
# render a file to SVG
mmdr -i diagram.mmd -o output.svg

# render to PNG
mmdr -i diagram.mmd -o output.png

# read from stdin, write to stdout — works great in pipelines
echo 'flowchart LR; A-->B-->C' | mmdr -i - -o -

# save the output to a file from a pipe
echo 'flowchart LR; A-->B-->C' | mmdr -i - -o diagram.svg
```

### PNG options

```bash
mmdr -i diagram.mmd -o output.png \
  --width 1200 \               # canvas width in pixels
  --height 800 \               # canvas height in pixels
  --background '#ffffff'       # background color (transparent by default)
```

### Backend and theme

```bash
# use the faster backend for simple diagrams
mmdr -i diagram.mmd -o output.svg --backend mermaid-rs-renderer

# classic Mermaid theme (mermaid-rs-renderer only)
mmdr -i diagram.mmd -o output.svg --backend mermaid-rs-renderer --theme classic
```

### Batch rendering

```bash
# convert every .mmd file in a directory
for f in diagrams/*.mmd; do
    mmdr -i "$f" -o "${f%.mmd}.svg"
done

# same, but PNG with a white background
for f in diagrams/*.mmd; do
    mmdr -i "$f" -o "${f%.mmd}.png" --background '#ffffff'
done
```

### Other commands

```bash
mmdr --info       # render Mermaid's built-in info diagram and show its text
mmdr --version    # print the mmdr version
mmdr -h           # full list of options
```

---

## Python API

### Rendering

`mmdr.render()` accepts a Mermaid source string and returns a `Diagram` object.
The actual rendering is **lazy** — nothing runs until you ask for an output.
The SVG result is cached, so calling `.svg()` multiple times only renders once.

```python
import mmdr

d = mmdr.render("""
flowchart TD
    A[Start] --> B{Is it working?}
    B -- Yes --> C[Great!]
    B -- No  --> D[Debug it]
    D --> B
""")
```

### SVG

```python
svg = d.svg()   # str

# write to file
with open("output.svg", "w") as f:
    f.write(svg)
```

### PNG

```python
# default: transparent background, size determined by the diagram
png = d.png()

# with explicit size and background
png = d.png(width=1200, height=800, background="#ffffff")

with open("output.png", "wb") as f:
    f.write(png)
```

### Save — auto-detect format

```python
d.save("output.svg")                                  # writes SVG
d.save("output.png")                                  # writes PNG
d.save("output.png", width=1200, background="#ffffff")  # PNG with options
```

### Raw pixels

`.raw()` returns the pixel buffer directly from the renderer as
`(bytes, width, height)`. The bytes are raw RGBA8888 data —
4 bytes per pixel, row-major, top-to-bottom.
No encoding, no copying through an image library.

```python
raw, w, h = d.raw(background="#ffffff")
print(f"image is {w}×{h} pixels, {len(raw)} bytes")
```

### NumPy

`.numpy()` returns an `(H, W, 4)` array with dtype `uint8` and RGBA channel order.
It's built on `.raw()` — requires only `numpy`, no Pillow.

```python
arr = d.numpy()
print(arr.shape)   # e.g. (480, 640, 4)
print(arr.dtype)   # uint8

# drop alpha → RGB
rgb = arr[:, :, :3]

# flip upside-down
import numpy as np
flipped = np.flipud(arr)
```

### Jupyter / IPython

`Diagram` implements `_repr_svg_()`, so notebooks render it inline
without any extra code:

```python
import mmdr

# just evaluating this in a cell displays the diagram
mmdr.render("sequenceDiagram\n  Alice->>Bob: Hello!\n  Bob-->>Alice: Hi!")
```

---

## Backends

```python
mmdr.backends()
# ['merman', 'mermaid-rs-renderer']

# merman is the default — pick it explicitly if you want to be clear
d = mmdr.render("flowchart LR; A-->B", backend="merman")

# mermaid-rs-renderer for simpler diagrams where speed matters
d = mmdr.render(
    "flowchart LR; A-->B-->C",
    backend="mermaid-rs-renderer",
    theme="classic",      # "modern" (default) or "classic"
    node_spacing=60.0,
    rank_spacing=80.0,
    aspect_ratio=(16, 9),
)
```

The `theme`, `node_spacing`, `rank_spacing`, and `aspect_ratio` options only
apply to `mermaid-rs-renderer`. The merman backend uses its own layout engine
tuned for parity with the official library.

---

## Low-level utilities

If you already have an SVG string from another source, you can rasterize it
directly without going through `render()`:

```python
from mmdr import svg_to_png, svg_to_raw

svg = open("diagram.svg").read()

png = svg_to_png(svg, width=1200, background="#ffffff")
raw, w, h = svg_to_raw(svg)
```

---

## Supported diagram types

| Diagram type | merman | mermaid-rs-renderer |
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