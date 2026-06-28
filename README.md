# mmdr

Fast native Mermaid diagram rendering for Python — powered by Rust
([mermaid-rs-renderer](https://github.com/1jehuang/mermaid-rs-renderer)).
No browser, no Node.js, no Puppeteer.

## Install

```bash
pip install mmdr
```

## CLI

After `pip install mmdr` you also get an `mmdr` command, similar in spirit to
[mermaid-cli](https://github.com/mermaid-js/mermaid-cli)'s `mmdc` — but it
talks to the native Rust renderer directly, no browser involved:

```bash
mmdr -i input.mmd -o output.svg
mmdr -i input.mmd -o output.png -t classic
mmdr -i input.mmd -o output.png --width 1200 --height 800

# stdin -> stdout
echo 'flowchart LR; A-->B-->C' | mmdr -i - -o -

# also works as:
python -m mmdr -i input.mmd -o output.svg

mmdr -h   # see all options
```

## Library

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
