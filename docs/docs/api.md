# Python API

## `mmdr.render()`

```python
mmdr.render(
    diagram: str,
    backend: str | None = None,
    **opts,
) -> Diagram
```

Render a Mermaid diagram. Returns a [`Diagram`](#diagram) object.

The SVG is rendered **lazily** — nothing runs until you call `.svg()`,
`.png()`, `.save()`, etc. The SVG result is cached, so calling `.svg()`
multiple times only renders once.

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `diagram` | `str` | — | Mermaid source text |
| `backend` | `str \| None` | `None` (`"merman"`) | `"merman"` or `"mermaid-rs-renderer"` |
| `theme` | `str` | `"modern"` | `"modern"` or `"classic"` — mermaid-rs-renderer only |
| `node_spacing` | `float` | — | Horizontal node spacing — mermaid-rs-renderer only |
| `rank_spacing` | `float` | — | Vertical rank spacing — mermaid-rs-renderer only |
| `aspect_ratio` | `tuple[float, float]` | — | Preferred aspect ratio — mermaid-rs-renderer only |

**Example:**

```python
import mmdr

d = mmdr.render("flowchart LR; A-->B-->C")
d = mmdr.render("flowchart LR; A-->B-->C", backend="mermaid-rs-renderer")
d = mmdr.render(
    "flowchart LR; A-->B-->C",
    backend="mermaid-rs-renderer",
    theme="classic",
    node_spacing=60.0,
    aspect_ratio=(16, 9),
)
```

---

## `Diagram`

The object returned by `mmdr.render()`.

### `.svg() → str`

Return the diagram as an SVG string. Cached after first call.

```python
svg = d.svg()
print(svg)  # <svg xmlns="http://www.w3.org/2000/svg" ...>
```

### `.png(width, height, background) → bytes`

Return the diagram as PNG bytes, rasterized via novasvg.

```python
png = d.png()
png = d.png(width=1200, height=800, background="#ffffff")

with open("output.png", "wb") as f:
    f.write(png)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `width` | `float \| None` | `None` | Output width in pixels (height follows the aspect ratio if omitted) |
| `height` | `float \| None` | `None` | Output height in pixels |
| `background` | `str \| None` | `None` | Background fill as CSS hex, e.g. `"#ffffff"`. Transparent by default. |

### `.raw(width, height, background) → tuple[bytes, int, int]`

Return raw RGBA8888 pixel data as `(bytes, width, height)`.
Stride is `width * 4`, row-major, top-to-bottom, with straight
(non-premultiplied) alpha. No encoding — the pixel buffer comes straight out of novasvg.

```python
raw, w, h = d.raw(background="#ffffff")
print(f"{w}×{h}, {len(raw)} bytes")  # 640×480, 1228800 bytes
```

### `.numpy(width, height, background) → np.ndarray`

Return an `(H, W, 4)` NumPy array, dtype `uint8`, RGBA channel order.
Requires NumPy (`pip install mmdr[numpy]`). No Pillow needed.

```python
arr = d.numpy()
print(arr.shape)   # (480, 640, 4)
print(arr.dtype)   # uint8

# Drop alpha → RGB
rgb = arr[:, :, :3]

# Flip upside-down
import numpy as np
flipped = np.flipud(arr)
```

### `.save(output, width, height, background)`

Save to a file. Format is inferred from the extension.

```python
d.save("output.svg")
d.save("output.png")
d.save("output.png", width=1200, background="#ffffff")
```

Supported extensions: `.svg`, `.png`.

### `.pdf() → bytes`

!!! warning "Not yet implemented"
    PDF export is planned for a future release.

---

## `mmdr.backends() → list[str]`

Return the list of backends compiled into this wheel.

```python
mmdr.backends()
# ['merman', 'mermaid-rs-renderer']
```

---

## `mmdr.svg_to_png()`

```python
mmdr.svg_to_png(
    svg: str,
    width: float | None = None,
    height: float | None = None,
    background: str | None = None,
) -> bytes
```

Convert an SVG string to PNG bytes using novasvg.
Useful if you already have an SVG from another source.

```python
from mmdr import svg_to_png

svg = open("existing.svg").read()
png = svg_to_png(svg, width=800, background="#ffffff")
```

---

## `mmdr.svg_to_raw()`

```python
mmdr.svg_to_raw(
    svg: str,
    width: float | None = None,
    height: float | None = None,
    background: str | None = None,
) -> tuple[bytes, int, int]
```

Convert an SVG string to raw RGBA8888 pixel data.
Returns `(bytes, width, height)`.

```python
from mmdr import svg_to_raw

raw, w, h = svg_to_raw(open("existing.svg").read())
```

---

## Jupyter integration

`Diagram` implements `_repr_svg_()`, so it renders inline automatically
in Jupyter notebooks and IPython — no extra code needed:

```python
import mmdr

# evaluating this in a cell displays the diagram inline
mmdr.render("sequenceDiagram\n  Alice->>Bob: Hello!\n  Bob-->>Alice: Hi!")
```
