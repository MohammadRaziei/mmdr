# CLI Reference

After `pip install mmdr`, the `mmdr` command is available on your PATH.
It works similarly to the official [mermaid-cli](https://github.com/mermaid-js/mermaid-cli)
(`mmdc`), but starts in milliseconds — no browser to boot.

## Basic usage

```bash
mmdr -i diagram.mmd -o output.svg
mmdr -i diagram.mmd -o output.png
```

The output format is inferred from the file extension. Supported: `.svg`, `.png`.

## Stdin / stdout

Use `-` to read from stdin or write to stdout:

```bash
# stdin → stdout
echo 'flowchart LR; A-->B-->C' | mmdr -i - -o -

# stdin → file
echo 'flowchart LR; A-->B-->C' | mmdr -i - -o diagram.svg

# file → stdout
mmdr -i diagram.mmd -o -
```

## Options

| Flag | Default | Description |
|---|---|---|
| `-i`, `--input` | `-` (stdin) | Input `.mmd` file |
| `-o`, `--output` | `-` (stdout) | Output file |
| `-e`, `--format` | auto | Output format: `svg` or `png` |
| `--backend` | `merman` | Rendering backend: `merman` or `mermaid-rs-renderer` |
| `-w`, `--width` | — | Canvas width in pixels (PNG) |
| `-H`, `--height` | — | Canvas height in pixels (PNG) |
| `-b`, `--background` | transparent | Background color, e.g. `'#ffffff'` (PNG) |
| `-t`, `--theme` | `modern` | Color theme: `modern` or `classic` (mermaid-rs-renderer only) |
| `--node-spacing` | — | Horizontal node spacing (mermaid-rs-renderer only) |
| `--rank-spacing` | — | Vertical rank spacing (mermaid-rs-renderer only) |
| `--aspect-ratio` | — | Preferred aspect ratio, e.g. `16:9` (mermaid-rs-renderer only) |
| `--info` | — | Render Mermaid's built-in info diagram and print its text |
| `--version` | — | Print mmdr version and exit |
| `-h`, `--help` | — | Show help |

## Examples

```bash
# PNG with white background and fixed size
mmdr -i diagram.mmd -o output.png \
  --width 1200 \
  --height 800 \
  --background '#ffffff'

# Use the faster backend
mmdr -i diagram.mmd -o output.svg --backend mermaid-rs-renderer

# Classic Mermaid theme
mmdr -i diagram.mmd -o output.svg \
  --backend mermaid-rs-renderer \
  --theme classic

# Batch convert all .mmd files in a directory
for f in diagrams/*.mmd; do
    mmdr -i "$f" -o "${f%.mmd}.svg"
done

# Also works as a Python module
python -m mmdr -i diagram.mmd -o output.svg
```
