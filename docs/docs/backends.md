# Backends

mmdr ships with two Rust rendering engines. Both produce SVG from Mermaid
source text. Everything else — PNG, raw pixels, NumPy — is handled by
[novasvg](https://mohammadraziei.github.io/novasvg/) (>=0.10) regardless of which backend
you choose.

## Comparison

| | `merman` | `mermaid-rs-renderer` |
|---|:---:|:---:|
| **Default** | ✅ | — |
| **Diagram parity** | Full (baseline defined by merman) | Common types only |
| **Speed** | Fast | Faster |
| **Layout options** | — | `theme`, `node_spacing`, `rank_spacing`, `aspect_ratio` |

## Diagram support

| Diagram type | `merman` | `mermaid-rs-renderer` |
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

## When to use which

**Use `merman` (default) when:**

- You need a diagram type not supported by `mermaid-rs-renderer`
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
