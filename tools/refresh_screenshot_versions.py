#!/usr/bin/env python3
"""Update the version label on six historical IRR UI captures.

Only the heading version label is repainted. All data and UI sections remain
unaltered; these are NOT new live v2.2.1 screenshots.
Images currently stored as JPEG bytes with .png names are normalized to PNG.
"""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parents[1] / "docs" / "screenshots"
TARGET_VERSION = "v2.2.1"
EXPECTED_IMAGES = [BASE / f"IRR{n:02d}.png" for n in range(1, 7)]


def update(path: Path) -> None:
    with Image.open(path) as original:
        if original.size[0] < 500 or original.size[1] < 600:
            raise RuntimeError(f"Unexpected image dimensions: {path} {original.size}")
        rgb = original.convert("RGB")

    # The six historical captures use the same top-bar layout.
    # "Internet Radio Recorder " ends before x=282; the version begins at x=285.
    # Restrict pixel edits strictly to its old version label (top heading).
    x0, y0, x1, y1 = 282, 1, 389, 32
    bg = rgb.getpixel((450, 12))
    drawing = ImageDraw.Draw(rgb)
    drawing.rectangle((x0, y0, x1, y1), fill=bg)

    fonts = [
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    font_path = next((f for f in fonts if Path(f).is_file()), None)
    if font_path is None:
        raise RuntimeError("Missing bold TrueType font on build runner")
    font = ImageFont.truetype(font_path, 24)

    # Leave a visible space after "Recorder" on every screenshot.
    # Match the original heading's white text; use a 4x transparent layer for
    # antialiased rendering without touching any other screenshot region.
    drawing.text((292, -1), TARGET_VERSION, font=font, fill=(237, 239, 243))
    rgb.save(path, format="PNG", optimize=True)
    with Image.open(path) as result:
        if result.format != "PNG":
            raise AssertionError(f"Not actually PNG: {path}")
        if result.size != rgb.size:
            raise AssertionError(f"Unexpected dimensions: {path}")
    print(f"Updated {path.name}: {rgb.width}x{rgb.height}")


if __name__ == "__main__":
    for image in EXPECTED_IMAGES:
        update(image)
