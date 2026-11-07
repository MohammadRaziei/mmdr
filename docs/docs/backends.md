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

| Diagram type | `merman` | `mermaid-rs-renderer` | Benchmark samples `mermaid-rs-renderer` drew |
| --- | :---: | :---: | :---: |
| flowchart / graph | ✅ | ✅ | 7 of 7 |
| sequenceDiagram | ✅ | ⚠️ | 2 of 5 |
| classDiagram | ✅ | ⚠️ | 1 of 2 |
| stateDiagram | ✅ | ✅ | 3 of 3 |
| erDiagram | ✅ | ✅ | 2 of 2 |
| requirementDiagram | ✅ | ✅ | 1 of 1 |
| gitGraph | ✅ | ✅ | 1 of 1 |
| mindmap | ✅ | ✅ | 2 of 2 |
| timeline | ✅ | ✅ | 2 of 2 |
| journey | ✅ | ✅ | 1 of 1 |
| gantt | ✅ | ✅ | 2 of 2 |
| pie | ✅ | ✅ | 2 of 2 |
| quadrantChart | ✅ | ✅ | 1 of 1 |
| xychart | ✅ | ✅ | 1 of 1 |
| sankey | ✅ | ✅ | 1 of 1 |
| block | ✅ | ✅ | 1 of 1 |
| architecture | ✅ | ✅ | 1 of 1 |
| kanban | ✅ | ✅ | 1 of 1 |
| C4 | ✅ | ✅ | 1 of 1 |
| packet | ✅ | ✅ | 1 of 1 |
| radar | ✅ | ✅ | 1 of 1 |
| treemap | ✅ | ✅ | 1 of 1 |
| venn | ✅ | ✅ | 1 of 1 |
| ishikawa | ✅ | ✅ | 1 of 1 |
| wardley | ✅ | ✅ | 1 of 1 |
| ZenUML | ✅ | ✅ | 3 of 3 |
| ELK layout (`flowchart-elk`) | ✅ | ✅ | 3 of 3 |
| `info` | ✅ | ❌ | 0 of 1 |

✅ drew every sample · ⚠️ rejected some samples · ❌ rejected the sample. The last column is from the [mermaidx benchmark](https://mohammadraziei.github.io/mermaidx/benchmarks): 50 samples, `merman` drew all of them, `mermaid-rs-renderer` 45.

What `mermaid-rs-renderer` rejected, and raised `ValueError` for:

- the bare `info` diagram;
- three sequence diagrams: two use `+` / `-` activation shorthand (`S->>+W`), one uses a participant it could not resolve;
- one class diagram with a `<<abstract>>` annotation.

A ✅ means an image came out, not that it is a correct one. We also ran one small diagram each of flowchart, sequence, class, state, ER, pie, gantt, timeline, mindmap, journey, gitGraph, xychart, quadrant, sankey, block, architecture, kanban, C4 and packet straight through `mmdr 0.4.0`, and both backends rendered all of them. Compare the pictures in the gallery before choosing `mermaid-rs-renderer` for a type.

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
