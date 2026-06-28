# mmdr

Fast native Mermaid diagram rendering for Python — powered by Rust
([mermaid-rs-renderer](https://github.com/1jehuang/mermaid-rs-renderer)).
No browser, no Node.js, no Puppeteer.

## Install

```bash
pip install mmdr
```

## Usage

```python
import mmdr

svg = mmdr.render("flowchart LR; A-->B-->C")
print(svg)

png_bytes = mmdr.render_png("flowchart LR; A-->B-->C")
with open("out.png", "wb") as f:
    f.write(png_bytes)
```

### Options

```python
mmdr.render(
    diagram,
    theme="modern",       # "modern" (default) or "classic"
    node_spacing=60.0,
    rank_spacing=80.0,
    aspect_ratio=(16, 9),
)
```

## License

MIT
