"""
Command-line interface for mmdr.

    mmdr -i input.mmd -o output.svg
    mmdr -i input.mmd -o output.png --backend merman
    echo 'flowchart LR; A-->B' | mmdr -i - -o -
    mmdr --info
    mmdr -h
"""

from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET

import mmdr


def _extract_svg_text(svg: str) -> str:
    root = ET.fromstring(svg)
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
        "-i", "--input", default="-",
        help="Input .mmd file. Use '-' (default) to read from stdin.",
    )
    parser.add_argument(
        "-o", "--output", default="-",
        help="Output file. Use '-' (default) to write to stdout. "
             "Format is guessed from the extension (.svg / .png) unless -e is given.",
    )
    parser.add_argument(
        "-e", "--format", choices=["svg", "png"], default=None,
        help="Output format. Defaults to the -o extension, or 'svg' if ambiguous.",
    )
    parser.add_argument(
        "--backend", choices=["mermaid-rs-renderer", "merman"], default=None,
        help="Rendering backend (default: mermaid-rs-renderer).",
    )
    parser.add_argument(
        "-t", "--theme", choices=["modern", "classic"], default="modern",
        help="Color theme (mermaid-rs-renderer only, default: modern).",
    )
    parser.add_argument(
        "-w", "--width", type=float, default=None,
        help="Output canvas width in pixels (PNG).",
    )
    parser.add_argument(
        "-H", "--height", type=float, default=None,
        help="Output canvas height in pixels (PNG).",
    )
    parser.add_argument(
        "--node-spacing", type=float, default=None,
        help="Node spacing (mermaid-rs-renderer only).",
    )
    parser.add_argument(
        "--rank-spacing", type=float, default=None,
        help="Rank spacing (mermaid-rs-renderer only).",
    )
    parser.add_argument(
        "--aspect-ratio", type=_parse_aspect_ratio, default=None, metavar="W:H",
        help="Preferred aspect ratio, e.g. '16:9' (mermaid-rs-renderer only).",
    )
    parser.add_argument(
        "--info", action="store_true",
        help="Render Mermaid's built-in 'info' diagram and print its text. "
             "No input needed.",
    )
    parser.add_argument(
        "--version", action="store_true",
        help="Print mmdr version and exit.",
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
        print(mmdr.__version__)
        return 0

    if args.info:
        try:
            d = mmdr.render("info", backend=args.backend)
            print(_extract_svg_text(d.svg()))
        except (ValueError, ET.ParseError) as exc:
            print(f"mmdr: --info failed: {exc}", file=sys.stderr)
            return 1
        return 0

    if args.input == "-" and sys.stdin.isatty():
        parser.print_usage(sys.stderr)
        print(
            "mmdr: no input given and stdin is a terminal.\n"
            "      Pass a file with -i diagram.mmd, or pipe:\n"
            "      echo 'flowchart LR; A-->B' | mmdr",
            file=sys.stderr,
        )
        return 1

    try:
        source = _read_input(args.input)
    except OSError as exc:
        print(f"mmdr: could not read {args.input!r}: {exc}", file=sys.stderr)
        return 1

    render_opts = dict(
        backend=args.backend,
        theme=args.theme,
        node_spacing=args.node_spacing,
        rank_spacing=args.rank_spacing,
        aspect_ratio=args.aspect_ratio,
        width=args.width,
        height=args.height,
    )

    try:
        d = mmdr.render(source, **{k: v for k, v in render_opts.items() if v is not None})
        fmt = _guess_format(args)

        if args.output == "-":
            data = d.png() if fmt == "png" else d.svg().encode("utf-8")
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()
        else:
            d.save(args.output)

    except (ValueError, NotImplementedError) as exc:
        print(f"mmdr: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
