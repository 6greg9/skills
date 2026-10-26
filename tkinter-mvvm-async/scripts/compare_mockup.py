"""Put Claude Design mockups next to tkinter renders, one PNG per screen state.

Usage:
    python tools/compare_mockup.py [--mockups design/mockups] [--shots shots] [--out shots/compare]

Pairs files by name: design/mockups/<screen>__<scenario>.png  <->  shots/<screen>__<scenario>__<WxH>.png
(the size suffix written by snap_view.py). Mockups are exported from the Design canvas at the
same size as the tkinter render. Unpaired files are listed so missing states get noticed.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

from PIL import Image, ImageDraw

SIZE_SUFFIX = re.compile(r"__\d+x\d+$")


def side_by_side(left: Image.Image, right: Image.Image, labels: tuple[str, str]) -> Image.Image:
    bar = 22
    h = max(left.height, right.height) + bar
    out = Image.new("RGB", (left.width + right.width + 12, h), "white")
    out.paste(left.convert("RGB"), (0, bar))
    out.paste(right.convert("RGB"), (left.width + 12, bar))
    d = ImageDraw.Draw(out)
    d.text((4, 4), labels[0], fill="black")
    d.text((left.width + 16, 4), labels[1], fill="black")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mockups", default="design/mockups")
    ap.add_argument("--shots", default="shots")
    ap.add_argument("--out", default="shots/compare")
    a = ap.parse_args()
    mock_dir, shot_dir, out = map(pathlib.Path, (a.mockups, a.shots, a.out))
    out.mkdir(parents=True, exist_ok=True)

    mocks = {p.stem: p for p in mock_dir.glob("*.png")}
    shots: dict[str, list[pathlib.Path]] = {}
    for p in shot_dir.glob("*.png"):
        shots.setdefault(SIZE_SUFFIX.sub("", p.stem), []).append(p)

    for key, mock in sorted(mocks.items()):
        for shot in sorted(shots.get(key, [])):
            m, s = Image.open(mock), Image.open(shot)
            note = "" if m.size == s.size else f"  (size differs: mockup {m.size}, tk {s.size})"
            path = out / f"{shot.stem}__compare.png"
            side_by_side(m, s, ("mockup (Claude Design)", f"tkinter {s.width}x{s.height}")).save(path)
            print(f"{path}{note}")
    missing_tk = sorted(set(mocks) - set(shots))
    missing_mock = sorted(set(shots) - set(mocks))
    if missing_tk:
        print("mockup without tkinter render:", ", ".join(missing_tk))
    if missing_mock:
        print("tkinter render without mockup:", ", ".join(missing_mock))
    return 0


if __name__ == "__main__":
    sys.exit(main())
