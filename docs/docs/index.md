# mmdr

**Fast, native Mermaid diagram rendering for Python — no browser required.**

Render [Mermaid](https://mermaid.js.org) diagrams directly from Python or the command line. No Node.js, no Puppeteer, no headless Chrome. Just install and render.

```bash
pip install mmdr
```

---

## Quick start

=== "CLI"

    ```bash
    mmdr -i diagram.mmd -o output.svg
    mmdr -i diagram.mmd -o output.png --background '#ffffff'
    echo 'flowchart LR; A-->B-->C' | mmdr -i - -o -
    ```

=== "Python"

    ```python
    import mmdr

    d = mmdr.render("flowchart LR; A-->B-->C")

    d.svg()                          # str
    d.png(background="#ffffff")      # bytes
    d.save("output.png", width=1200) # auto-detects format
    d.numpy()                        # np.ndarray — no Pillow needed
    ```

=== "Jupyter"

    ```python
    import mmdr

    # just evaluating this in a cell displays the diagram inline
    mmdr.render("flowchart LR; A-->B-->C")
    ```

---

## Why mmdr?

The standard way to render Mermaid in Python is to spin up a headless browser
and run the official JavaScript library. It works, but it's slow to start,
heavy to install, and awkward to embed in a pipeline.

mmdr takes a different approach: the rendering engine is compiled Rust,
shipped as a native Python extension. No JS runtime, no browser, no extra
system dependencies — just a ~7 MB wheel.

| | mmdr | mermaid-cli |
|---|:---:|:---:|
| Requires Node.js | ❌ | ✅ |
| Requires a browser | ❌ | ✅ |
| `pip install` only | ✅ | ❌ |
| Startup time | ~0ms | ~3–5s |
| Speed | 100–1400x faster | baseline |

---

## Two backends

mmdr ships with two Rust rendering engines in one package:

- **`merman`** *(default)* — targets full parity with the official Mermaid library (baseline defined by the merman crate), supports all diagram types
- **`mermaid-rs-renderer`** — faster and lighter, covers the most common diagram types

```python
mmdr.backends()
# ['merman', 'mermaid-rs-renderer']
```

See [Backends](backends.md) for a full comparison.

---

## Output formats

| Format | Method |
|---|---|
| SVG | `.svg()` |
| PNG | `.png()` |
| Raw RGBA pixels | `.raw()` |
| NumPy array | `.numpy()` |
| File (auto-detect) | `.save("out.svg")` |
