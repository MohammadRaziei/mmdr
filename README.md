# mmdr

Mermaid diagram rendering — fast, native, no browser required.

Built on Rust. No Node.js, no Puppeteer, no headless Chrome. Just install and render.

```bash
pip install mmdr
```

**Output formats:** SVG · PNG · raw pixels (RGBA) · NumPy array

**Two backends:**
- `merman` *(default)* — full Mermaid parity, supports all diagram types
- `mermaid-rs-renderer` — faster, covers common diagram types

---

## CLI

```bash
# SVG
mmdr -i diagram.mmd -o output.svg

# PNG
mmdr -i diagram.mmd -o output.png --width 1200 --background '#ffffff'

# stdin → stdout
echo 'flowchart LR; A-->B-->C' | mmdr -i - -o -

# choose backend
mmdr -i diagram.mmd -o output.svg --backend mermaid-rs-renderer

# batch
for f in diagrams/*.mmd; do
    mmdr -i "$f" -o "${f%.mmd}.svg"
done

mmdr --info       # Mermaid version info
mmdr --version    # mmdr version
mmdr -h           # all options
```

---

## Python

```python
import mmdr

d = mmdr.render("flowchart LR; A-->B-->C")

d.svg()                                    # str
d.png()                                    # bytes
d.png(width=1200, background="#ffffff")    # bytes, with options
d.raw()                                    # (bytes, width, height) — RGBA8888
d.numpy()                                  # np.ndarray (H×W×4, uint8)
d.save("output.svg")                       # auto-detects format
d.save("output.png", width=1200)
```

The result is lazy — rendering happens on first access and the SVG is cached.

### Backends

```python
# merman (default) — all diagram types
d = mmdr.render("kanban\n  todo\n    Task A")
d.svg()

# mermaid-rs-renderer — faster, with layout options
d = mmdr.render(
    "flowchart LR; A-->B-->C",
    backend="mermaid-rs-renderer",
    theme="classic",          # "modern" (default) or "classic"
    node_spacing=60.0,
    rank_spacing=80.0,
    aspect_ratio=(16, 9),
)
d.svg()

mmdr.backends()
# ['merman', 'mermaid-rs-renderer']
```

### Jupyter

`Diagram` renders inline automatically — no extra steps needed:

```python
mmdr.render("flowchart LR; A-->B-->C")   # displays inline
```

### Raw SVG utilities

```python
from mmdr import svg_to_png, svg_to_raw

svg = open("existing.svg").read()
png = svg_to_png(svg, width=800, background="#ffffff")
raw, w, h = svg_to_raw(svg)
```

---

## Supported diagrams

| | merman | mermaid-rs-renderer |
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