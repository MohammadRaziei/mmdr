# mmdr

Fast, headless Mermaid diagram rendering — two native Rust backends, **zero Python dependencies**.

| Backend | Crate | Diagram support | PNG |
|---|---|---|---|
| `mermaid-rs-renderer` (default) | [mermaid-rs-renderer](https://github.com/1jehuang/mermaid-rs-renderer) | flowchart, class, sequence, state, … | via resvg |
| `merman` | [merman](https://github.com/Latias94/merman) | full Mermaid @11.15.0 parity | native raster feature |

## Install

```bash
pip install mmdr
```

## CLI

```bash
mmdr -i diagram.mmd -o output.svg
mmdr -i diagram.mmd -o output.png --backend merman
echo 'flowchart LR; A-->B' | mmdr -i - -o -
mmdr --info
mmdr -h
```

## Library

```python
import mmdr

mmdr.backends()
# ['mermaid-rs-renderer', 'merman']

# Default backend (mermaid-rs-renderer)
svg = mmdr.render("flowchart LR; A-->B-->C")

# merman backend
svg = mmdr.render("flowchart LR; A-->B-->C", backend="merman")

# PNG — mermaid-rs-renderer
png = mmdr.render_png("flowchart LR; A-->B-->C", width=1200, height=800)

# PNG — merman (native raster, no extra deps)
png = mmdr.render_png(
    "flowchart LR; A-->B-->C",
    backend="merman",
    width=1200,
    height=800,
    background="white",
    scale=2.0,          # device pixel ratio
)

with open("out.png", "wb") as f:
    f.write(png)
```

## Options

### mermaid-rs-renderer

```python
mmdr.render(diagram, backend="mermaid-rs-renderer",
    theme="modern",           # "modern" (default) or "classic"
    node_spacing=60.0,
    rank_spacing=80.0,
    aspect_ratio=(16, 9),
)
```

### merman

```python
mmdr.render(diagram, backend="merman")  # uses merman's own defaults

mmdr.render_png(diagram, backend="merman",
    width=800,              # fit-box width in pixels
    height=600,             # fit-box height in pixels
    background="#ffffff",   # CSS background color
    scale=2.0,              # device pixel ratio
)
```

## License

MIT
