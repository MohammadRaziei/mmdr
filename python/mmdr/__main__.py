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
    """Parse an SVG string with a real XML parser and return just its
    text content (every <text> element, tspans merged in), one per line.
    """
    root = ET.fromstring(svg)

    # The renderer always sets an explicit xmlns on the root <svg> tag, so
    # reuse that namespace instead of guessing one.
    if root.tag.startswith("{"):
        ns_uri = root.tag[1:].split("}", 1)[0]
        text_tag = f"{{{ns_uri}}}text"
    else:
        text_tag = "text"

    lines = []
    for el in root.iter(text_tag):
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
        help="Render Mermaid's built-in 'info' diagram (shows the version) "
             "and print just its text, extracted from the SVG with an XML "
             "parser. Takes no input - ignores -i/stdin and any diagram.",
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

    if args.info:
        # Mermaid's own built-in "info" diagram - we don't read any file or
        # stdin here, the diagram source is just the literal word "info".
        # This assumes the underlying renderer (mermaid-rs-renderer) knows
        # how to render an "info" diagram into a valid SVG containing the
        # version as text; we don't special-case it on our side.
        try:
            svg = render(
                "info",
                theme=args.theme,
                node_spacing=args.node_spacing,
                rank_spacing=args.rank_spacing,
                aspect_ratio=args.aspect_ratio,
            )
            print(_extract_svg_text(svg))
        except ValueError as exc:
            print(f"mmdr: failed to render info diagram: {exc}", file=sys.stderr)
            return 1
        except ET.ParseError as exc:
            print(f"mmdr: failed to parse generated SVG: {exc}", file=sys.stderr)
            return 1
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
        if fmt == "png":
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

    if args.output == "-":
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()
    else:
        with open(args.output, "wb") as f:
            f.write(data)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
