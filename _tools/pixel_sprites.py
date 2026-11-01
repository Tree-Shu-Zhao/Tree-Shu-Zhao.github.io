"""Pixel sprites for the homepage: the tree logo/favicon and the hand-drawn icons.

Each sprite is an ASCII grid; one character is one pixel ('.' = transparent).
Running the script writes the favicon files and prints <symbol> markup; with --inject it also
replaces the block between the sprite markers in index.html.

Usage: python _tools/pixel_sprites.py OUT_DIR [--preview PNG] [--inject index.html]
"""

import argparse
import os
import re

from PIL import Image

# Tree logo, 16x16. Palette keys: o outline, h highlight, l light leaf, m mid leaf, d dark leaf, t trunk, b trunk shadow.
TREE = [
    "................",
    ".....oooooo.....",
    "...oohhhllmoo...",
    "..ohhhllllmmmo..",
    ".ohhlllllmmmmdo.",
    ".ollllmmmmmmddo.",
    "ohllmmlllmmmmddo",
    "olllmmllllmmdddo",
    "olmmmmmlllmddddo",
    "ommmmmmmmmdddddo",
    ".odmmmmmddddddo.",
    "..oddddddddddo..",
    "...ooooobboooo..",
    "......otbo......",
    ".....ottbbo.....",
    "....oooooooo....",
]
TREE_COLORS = {
    "o": "#1f2d1b",
    "h": "#d7eab9",
    "l": "#a9d07e",
    "m": "#73a64a",
    "d": "#3f6d2d",
    "t": "#9a6a3e",
    "b": "#61401f",
}

# Single-colour icons on a 12x12 grid (drawn with currentColor).
ICONS = {
    "scholar": [
        "............",
        ".....##.....",
        "...######...",
        ".##########.",
        "############",
        "...........#",
        "..########.#",
        "..########.#",
        "..########.#",
        "...######.##",
        "..........##",
        "............",
    ],
    "linkedin": [
        ".##########.",
        "############",
        "##..########",
        "############",
        "##..#....###",
        "##..#..#..##",
        "##..#..#..##",
        "##..#..#..##",
        "##..#..#..##",
        "############",
        "############",
        ".##########.",
    ],
    "star": [
        ".....##.....",
        ".....##.....",
        "....####....",
        "############",
        ".##########.",
        "..########..",
        "...######...",
        "...######...",
        "..########..",
        "..###..###..",
        ".###....###.",
        ".##......##.",
    ],
    "arrow": [
        "............",
        "...##.......",
        "...###......",
        "...####.....",
        "...#####....",
        "...######...",
        "...######...",
        "...#####....",
        "...####.....",
        "...###......",
        "...##.......",
        "............",
    ],
}

# Icons taken from pixelarticons (MIT, (c) 2019 Gerrit Halfmann), drawn on a 24x24 viewBox.
PIXELARTICONS = {
    "mail": "M22 4H2v16h20V4zM4 18V6h16v12H4zM8 8H6v2h2v2h2v2h4v-2h2v-2h2V8h-2v2h-2v2h-4v-2H8V8z",
    "github": "M5 2h4v2H7v2H5V2Zm0 10H3V6h2v6Zm2 2H5v-2h2v2Zm2 2v-2H7v2H3v-2H1v2h2v2h4v4h2v-4h2v-2H9Zm0 0v2H7v-2h2Zm6-12v2H9V4h6Zm4 2h-2V4h-2V2h4v4Zm0 6V6h2v6h-2Zm-2 2v-2h2v2h-2Zm-2 2v-2h2v2h-2Zm0 2h-2v-2h2v2Zm0 0h2v4h-2v-4Z",
    "article": "M5 3H3v18h18V3H5zm14 2v14H5V5h14zm-2 2H7v2h10V7zM7 11h10v2H7v-2zm7 4H7v2h7v-2z",
    "code": "M8 5h2v2H8V5zM6 7h2v2H6V7zM4 9h2v2H4V9zm-2 2h2v2H2v-2zm2 2h2v2H4v-2zm2 2h2v2H6v-2zm2 2h2v2H8v-2zm8-12h-2v2h2V5zm2 2h-2v2h2V7zm2 2h-2v2h2V9zm2 2h-2v2h2v-2zm-2 2h-2v2h2v-2zm-2 2h-2v2h2v-2zm-2 2h-2v2h2v-2z",
    "external": "M21 11V3h-8v2h4v2h-2v2h-2v2h-2v2H9v2h2v-2h2v-2h2V9h2V7h2v4h2zM11 5H3v16h16v-8h-2v6H5V7h6V5z",
}


def grid_to_path(grid, cell):
    """Merge horizontal runs of filled pixels into rects and return one SVG path."""
    parts = []
    for y, row in enumerate(grid):
        x = 0
        while x < len(row):
            if row[x] == "#":
                start = x
                while x < len(row) and row[x] == "#":
                    x += 1
                parts.append(f"M{start * cell} {y * cell}h{(x - start) * cell}v{cell}h-{(x - start) * cell}z")
            else:
                x += 1
    return "".join(parts)


def tree_svg_body():
    """One <path> per colour, merged runs, on a 16x16 grid."""
    by_color = {}
    for y, row in enumerate(TREE):
        assert len(row) == 16, (y, len(row))
        x = 0
        while x < 16:
            ch = row[x]
            if ch == ".":
                x += 1
                continue
            start = x
            while x < 16 and row[x] == ch:
                x += 1
            by_color.setdefault(ch, []).append(f"M{start} {y}h{x - start}v1h-{x - start}z")
    return "".join(f'<path fill="{TREE_COLORS[k]}" d="{"".join(v)}"/>' for k, v in by_color.items())


def tree_png(size):
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(TREE):
        for x, ch in enumerate(row):
            if ch != ".":
                c = TREE_COLORS[ch].lstrip("#")
                img.putpixel((x, y), tuple(int(c[i : i + 2], 16) for i in (0, 2, 4)) + (255,))
    return img.resize((size, size), Image.NEAREST)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--preview")
    ap.add_argument("--inject", help="HTML file whose <!-- sprites:start/end --> block is replaced")
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)

    body = tree_svg_body()
    with open(os.path.join(args.out_dir, "tree.svg"), "w") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" shape-rendering="crispEdges">{body}</svg>\n')
    tree_png(32).save(os.path.join(args.out_dir, "favicon-32.png"))
    # Apple touch icon: tree centred on the page colour with a margin.
    touch = Image.new("RGBA", (180, 180), (239, 245, 228, 255))
    touch.alpha_composite(tree_png(160), (10, 6))
    touch.convert("RGB").save(os.path.join(args.out_dir, "apple-touch-icon.png"))

    symbols = [f'<symbol id="i-tree" viewBox="0 0 16 16">{body}</symbol>']
    for name, grid in ICONS.items():
        assert all(len(r) == 12 for r in grid) and len(grid) == 12, name
        symbols.append(f'<symbol id="i-{name}" viewBox="0 0 24 24"><path fill="currentColor" d="{grid_to_path(grid, 2)}"/></symbol>')
    for name, d in PIXELARTICONS.items():
        symbols.append(f'<symbol id="i-{name}" viewBox="0 0 24 24"><path fill="currentColor" d="{d}"/></symbol>')
    print("\n".join(symbols))

    if args.inject:
        with open(args.inject) as f:
            html = f.read()
        block = "<!-- sprites:start -->\n" + "\n".join(symbols) + "\n<!-- sprites:end -->"
        new, n = re.subn(r"<!-- sprites:start -->.*?<!-- sprites:end -->", lambda _: block, html, flags=re.S)
        if n != 1:
            raise SystemExit(f"expected one sprite block in {args.inject}, found {n}")
        with open(args.inject, "w") as f:
            f.write(new)

    if args.preview:
        # Rasterise the ASCII icons for a quick visual check (pixelarticons are checked in the browser).
        tiles = [tree_png(96)]
        for grid in ICONS.values():
            img = Image.new("RGBA", (12, 12), (0, 0, 0, 0))
            for y, row in enumerate(grid):
                for x, ch in enumerate(row):
                    if ch == "#":
                        img.putpixel((x, y), (31, 45, 27, 255))
            tiles.append(img.resize((96, 96), Image.NEAREST))
        sheet = Image.new("RGBA", (len(tiles) * 112, 112), (239, 245, 228, 255))
        for i, t in enumerate(tiles):
            sheet.alpha_composite(t, (i * 112 + 8, 8))
        sheet.convert("RGB").save(args.preview)


if __name__ == "__main__":
    main()
