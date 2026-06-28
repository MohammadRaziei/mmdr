"""
Command-line interface for mmdr.

Modeled loosely on mermaid-cli's `mmdc` (https://github.com/mermaid-js/mermaid-cli),
but talks to the native Rust renderer directly instead of spawning a browser.

    mmdr -i input.mmd -o output.svg
    mmdr -i input.mmd -o output.png -t classic
    echo 'flowchart LR; A-->B' | mmdr -i - -o -

Run `mmdr -h` for all options.
"""

from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET

from . import render, render_png


def _extract_svg_text(svg: str) -> str:
    """Parse the rendered SVG and pull out just the diagram's text labels.

    This is *not* a re/string hack — it walks the real SVG element tree
    (via xml.etree.ElementTree) and reads the text content of every
    <text> element (tspans included), in document order. No drawing
    commands, no coordinates, just the words that appear in the diagram.
    """
    root = ET.fromstring(svg)

    # The root tag looks like "{http://www.w3.org/2000/svg}svg" since the
    # renderer always sets an explicit xmlns. Reuse that namespace to find
    # <text> elements correctly instead of guessing.
    if root.tag.startswith("{"):
        ns_uri = root.tag[1:].split("}", 1)[0]
        text_tag = f"{{{ns_uri}}}text"
    else:
        text_tag = "text"

    lines = []
    for el in root.iter(text_tag):
        # itertext() merges this <text> element's own text with all of its
        # <tspan> children's text, in order - exactly the rendered label.
        line = "".join(el.itertext()).strip()
        if line:
            lines.append(line)

    return "\n".join(lines)


def _parse_aspect_ratio(value: str) -> tuple[float, float]:
    """Parse "16:9" or "16x9" into (16.0, 9.0)."""
    sep = ":" if ":" in value else "x"
    try:
        w_str, h_str = value.split(sep, 1)
        w, h = float(w_str), float(h_str)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"invalid aspect ratio {value!r}, expected e.g. '16:9'"
        ) from exc
    if w <= 0 or h <= 0:
        raise argparse.ArgumentTypeError("aspect ratio parts must be positive")
    return (w, h)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mmdr",
        description="Render a Mermaid diagram to SVG or PNG (no browser required).",
    )
    parser.add_argument(
        "-i", "--input",
        default="-",
        help="Input .mmd file. Use '-' (default) to read from stdin.",
    )
    parser.add_argument(
        "-o", "--output",
        default="-",
        help="Output file. Use '-' (default) to write to stdout. "
             "Format is guessed from the extension (.svg / .png) unless -e is given.",
    )
    parser.add_argument(
        "-e", "--format",
        choices=["svg", "png"],
        default=None,
        help="Output format. Defaults to the -o extension, or 'svg' if that's ambiguous.",
    )
    parser.add_argument(
        "-t", "--theme",
        choices=["modern", "classic"],
        default="modern",
        help="Color theme (default: modern). 'classic' matches mermaid's default look.",
    )
    parser.add_argument(
        "-w", "--width",
        type=float,
        default=None,
        help="Output canvas width in pixels (PNG only).",
    )
    parser.add_argument(
        "-H", "--height",
        type=float,
        default=None,
        help="Output canvas height in pixels (PNG only).",
    )
    parser.add_argument(
        "--node-spacing",
        type=float,
        default=None,
        help="Horizontal spacing between sibling nodes.",
    )
    parser.add_argument(
        "--rank-spacing",
        type=float,
        default=None,
        help="Spacing between ranks/levels of the diagram.",
    )
    parser.add_argument(
        "--aspect-ratio",
        type=_parse_aspect_ratio,
        default=None,
        metavar="W:H",
        help="Preferred output aspect ratio, e.g. '16:9'.",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Don't output graphics - render to SVG internally, then extract "
             "and print just the text labels found in the diagram (parsed "
             "with an XML parser, not regex). Ignores -e/--format.",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print the mmdr version and exit.",
    )
    return parser


def _read_input(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _guess_format(args: argparse.Namespace) -> str:
    if args.format:
        return args.format
    if args.output != "-" and args.output.lower().endswith(".png"):
        return "png"
    return "svg"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        from . import __version__
        print(__version__)
        return 0

    if args.input == "-" and sys.stdin.isatty():
        # Nothing was piped in and there's no file to read - reading stdin
        # here would just block forever waiting for input that's never
        # coming. Fail fast with a helpful message instead.
        parser.print_usage(sys.stderr)
        print(
            "mmdr: no input given and stdin is a terminal (not a pipe/file).\n"
            "      Pass a file with -i diagram.mmd, or pipe a diagram in, e.g.:\n"
            "      echo 'flowchart LR; A-->B' | mmdr",
            file=sys.stderr,
        )
        return 1

    try:
        diagram = _read_input(args.input)
    except OSError as exc:
        print(f"mmdr: could not read {args.input!r}: {exc}", file=sys.stderr)
        return 1

    fmt = _guess_format(args)

    try:
        if args.info:
            # Always render to SVG first (PNG has no text nodes to read),
            # regardless of -e/--format - --info is about the diagram's
            # textual content, not its pixels.
            svg = render(
                diagram,
                theme=args.theme,
                node_spacing=args.node_spacing,
                rank_spacing=args.rank_spacing,
                aspect_ratio=args.aspect_ratio,
            )
            data = _extract_svg_text(svg).encode("utf-8")
        elif fmt == "png":
            data = render_png(
                diagram,
                theme=args.theme,
                node_spacing=args.node_spacing,
                rank_spacing=args.rank_spacing,
                aspect_ratio=args.aspect_ratio,
                width=args.width,
                height=args.height,
            )
        else:
            text = render(
                diagram,
                theme=args.theme,
                node_spacing=args.node_spacing,
                rank_spacing=args.rank_spacing,
                aspect_ratio=args.aspect_ratio,
            )
            data = text.encode("utf-8")
    except ValueError as exc:
        print(f"mmdr: failed to render diagram: {exc}", file=sys.stderr)
        return 1
    except ET.ParseError as exc:
        print(f"mmdr: failed to parse generated SVG for --info: {exc}", file=sys.stderr)
        return 1

    if args.output == "-":
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()
    else:
        with open(args.output, "wb") as f:
            f.write(data)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())