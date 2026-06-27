#!/usr/bin/env python3
"""Render a PlantUML .puml file to a real image file.

Encodes the diagram source (deflate + PlantUML's custom base64) and fetches the
already-rendered image from the public PlantUML server, then writes the bytes to
disk. The user never has to convert anything by hand.

This is a faithful port of the encoding used by the original AI DevStudio web app
(PlantUMLRenderer.tsx: pako.deflate level 9 -> custom base64 -> "~1" URL prefix).

Standard library only (zlib + urllib). No pip install required.

Usage:
    python render_puml.py <input.puml> [--format png|svg] [--output <path>]
                          [--server <url>] [--timeout <seconds>] [--print-url]

Exit codes:
    0  success (image written)
    1  usage / file error
    2  render / network error (the .puml is kept; nothing was overwritten)
"""
import argparse
import os
import re
import sys
import zlib
import urllib.request
import urllib.error

DEFAULT_SERVER = "https://www.plantuml.com/plantuml"


def encode6bit(b: int) -> str:
    if b < 10:
        return chr(48 + b)
    b -= 10
    if b < 26:
        return chr(65 + b)
    b -= 26
    if b < 26:
        return chr(97 + b)
    b -= 26
    if b == 0:
        return "-"
    if b == 1:
        return "_"
    return "?"


def append3bytes(b1: int, b2: int, b3: int) -> str:
    c1 = b1 >> 2
    c2 = ((b1 & 0x3) << 4) | (b2 >> 4)
    c3 = ((b2 & 0xF) << 2) | (b3 >> 6)
    c4 = b3 & 0x3F
    return (
        encode6bit(c1 & 0x3F)
        + encode6bit(c2 & 0x3F)
        + encode6bit(c3 & 0x3F)
        + encode6bit(c4 & 0x3F)
    )


def encode64(data: bytes) -> str:
    r = []
    n = len(data)
    i = 0
    while i < n:
        if i + 2 < n:
            r.append(append3bytes(data[i], data[i + 1], data[i + 2]))
        elif i + 1 < n:
            r.append(append3bytes(data[i], data[i + 1], 0))
        else:
            r.append(append3bytes(data[i], 0, 0))
        i += 3
    return "".join(r)


def clean_source(code: str) -> str:
    """Mirror the web app's cleanup: prefer the @startuml..@enduml block,
    strip stray markdown fences, and ensure the start/end markers exist."""
    match = re.search(r"@startuml[\s\S]*?@enduml", code)
    if match:
        return match.group(0)
    clean = code.strip()
    if clean.startswith("```"):
        lines = clean.split("\n")
        clean = "\n".join(lines[1:-1]).strip()
    if not clean.startswith("@startuml"):
        clean = "@startuml\n" + clean
    if not clean.endswith("@enduml"):
        clean = clean + "\n@enduml"
    return clean


def encode_plantuml(code: str) -> str:
    source = clean_source(code)
    raw = source.encode("utf-8")
    compressed = zlib.compress(raw, 9)
    return encode64(compressed)


def build_url(server: str, fmt: str, encoded: str) -> str:
    return f"{server.rstrip('/')}/{fmt}/~1{encoded}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a .puml file to an image.")
    parser.add_argument("input", help="Path to the .puml source file")
    parser.add_argument("--format", default="png", choices=["png", "svg"],
                        help="Output image format (default: png)")
    parser.add_argument("--output", help="Output image path (default: alongside input)")
    parser.add_argument("--server", default=DEFAULT_SERVER,
                        help="PlantUML server base URL")
    parser.add_argument("--timeout", type=float, default=30.0,
                        help="Network timeout in seconds (default: 30)")
    parser.add_argument("--print-url", action="store_true",
                        help="Also print the encoded server URL")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"ERROR: input file not found: {args.input}", file=sys.stderr)
        return 1

    try:
        with open(args.input, "r", encoding="utf-8") as fh:
            code = fh.read()
    except OSError as exc:
        print(f"ERROR: cannot read {args.input}: {exc}", file=sys.stderr)
        return 1

    if not code.strip():
        print(f"ERROR: {args.input} is empty", file=sys.stderr)
        return 1

    encoded = encode_plantuml(code)
    url = build_url(args.server, args.format, encoded)
    if args.print_url:
        print(url)

    output = args.output or (os.path.splitext(args.input)[0] + "." + args.format)

    req = urllib.request.Request(url, headers={"User-Agent": "prd-sdd-studio/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            data = resp.read()
    except urllib.error.HTTPError as exc:
        print(f"ERROR: PlantUML server returned HTTP {exc.code}. "
              f"The diagram source likely has a syntax error. "
              f"The .puml file was kept at {args.input}.", file=sys.stderr)
        return 2
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"ERROR: could not reach PlantUML server ({exc}). "
              f"Check your network. The .puml file was kept at {args.input}.",
              file=sys.stderr)
        return 2

    if not data:
        print("ERROR: server returned an empty response.", file=sys.stderr)
        return 2

    try:
        with open(output, "wb") as fh:
            fh.write(data)
    except OSError as exc:
        print(f"ERROR: cannot write {output}: {exc}", file=sys.stderr)
        return 1

    print(f"OK: wrote {output} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
