# Backends

mmdr ships with two Rust rendering engines. Both produce SVG from Mermaid
source text. Everything else — PNG, raw pixels, NumPy — is handled by
[novasvg](https://mohammadraziei.github.io/novasvg/) (pinned to 0.11.5) regardless of which backend
you choose.

## Comparison

| | `merman` | `mermaid-rs-renderer` |
|---|:---:|:---:|
| **Default** | ✅ | — |
| **Diagram parity** | Aims at full parity (baseline defined by merman) | Draws the same diagram types, rejects some syntax |
| **Speed** | 22.9 ms median per diagram | 16.2 ms median per diagram |
| **Benchmark: diagrams drawn** | 50 of 50 | 45 of 50 |
| **Layout options** | — | `theme`, `node_spacing`, `rank_spacing`, `aspect_ratio` |

## Diagram support

Both backends rendered every one of these types in our checks: flowchart, sequence, class, state, ER, pie, gantt, timeline, mindmap, journey, gitGraph, xychart, quadrant, sankey, block, architecture, kanban, C4 and packet.

Drawing a type does not mean drawing every feature of it. In the [mermaidx benchmark](https://mohammadraziei.github.io/mermaidx/benchmarks) `mermaid-rs-renderer` rejected five of the 50 samples and `merman` none:

- the bare `info` diagram;
- sequence diagrams that use `+` / `-` activation shorthand (two samples), and one that uses a participant it could not resolve;
- a class diagram with a `<<abstract>>` annotation.

The rejected input raises `ValueError`. Producing an image is also not the same as producing a correct one, so compare the pictures in the gallery before choosing `mermaid-rs-renderer` for a diagram type.

## When to use which

**Use `merman` (default) when:**

- Your diagrams use syntax that `mermaid-rs-renderer` rejects (see above)
- Output correctness and parity with the official library matters
- You don't need layout fine-tuning

**Use `mermaid-rs-renderer` when:**

- You're rendering simple flowcharts or common diagrams at high volume
- You want to control layout parameters (`node_spacing`, `aspect_ratio`, etc.)
- Every millisecond counts

## Selecting a backend

=== "Python"

    ```python
    import mmdr

    # merman (default)
    d = mmdr.render("flowchart LR; A-->B")

    # mermaid-rs-renderer
    d = mmdr.render(
        "flowchart LR; A-->B",
        backend="mermaid-rs-renderer",
        theme="classic",
        node_spacing=60.0,
        rank_spacing=80.0,
        aspect_ratio=(16, 9),
    )
    ```

=== "CLI"

    ```bash
    # merman (default)
    mmdr -i diagram.mmd -o output.svg

    # mermaid-rs-renderer
    mmdr -i diagram.mmd -o output.svg --backend mermaid-rs-renderer --theme classic
    ```
