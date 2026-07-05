# Examples

## Flowchart

```python
import mmdr

d = mmdr.render("""
flowchart TD
    A[Start] --> B{Is it working?}
    B -- Yes --> C[Great!]
    B -- No  --> D[Debug it]
    D --> B
""")

d.save("flowchart.svg")
d.save("flowchart.png", background="#ffffff")
```

## Sequence diagram

```python
d = mmdr.render("""
sequenceDiagram
    autonumber
    Client->>Server: GET /api/data
    Server->>Database: SELECT *
    Database-->>Server: rows
    Server-->>Client: 200 OK
""")

d.save("sequence.svg")
```

## Class diagram

```python
d = mmdr.render("""
classDiagram
    class Animal {
        +String name
        +int age
        +speak() void
    }
    class Dog {
        +fetch() void
    }
    class Cat {
        +purr() void
    }
    Animal <|-- Dog
    Animal <|-- Cat
""")

d.save("classes.svg")
```

## Batch rendering

Render all `.mmd` files in a directory:

```python
from pathlib import Path
import mmdr

for mmd_file in Path("diagrams").glob("*.mmd"):
    source = mmd_file.read_text()
    mmdr.render(source).save(mmd_file.with_suffix(".svg"))
```

## NumPy integration

Process a rendered diagram as a NumPy array — no Pillow needed:

```python
import numpy as np
import mmdr

arr = mmdr.render("flowchart LR; A-->B-->C").numpy()

print(arr.shape)   # (H, W, 4) — RGBA
print(arr.dtype)   # uint8

# Drop alpha → RGB
rgb = arr[:, :, :3]

# Check if the image is mostly white
white_ratio = (rgb == 255).all(axis=2).mean()
print(f"{white_ratio:.1%} of pixels are white")
```

## Rasterize an existing SVG

Use `svg_to_png` and `svg_to_raw` directly on any SVG string:

```python
from mmdr import svg_to_png, svg_to_raw

svg = open("diagram.svg").read()

# → PNG
png = svg_to_png(svg, width=1200, background="#ffffff")
open("output.png", "wb").write(png)

# → raw RGBA pixels
raw, w, h = svg_to_raw(svg)
print(f"{w}×{h} pixels, {len(raw)} bytes")
```

## FastAPI endpoint

Serve rendered diagrams over HTTP:

```python
from fastapi import FastAPI
from fastapi.responses import Response
import mmdr

app = FastAPI()

@app.post("/render/svg")
def render_svg(body: dict) -> Response:
    svg = mmdr.render(body["diagram"]).svg()
    return Response(content=svg, media_type="image/svg+xml")

@app.post("/render/png")
def render_png(body: dict) -> Response:
    png = mmdr.render(body["diagram"]).png(background="#ffffff")
    return Response(content=png, media_type="image/png")
```
