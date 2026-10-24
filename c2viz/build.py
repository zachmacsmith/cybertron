"""Build the preview page: the pixel renderer (pixel.js) and a run's frames in one self-contained HTML file.

    python -m c2viz.build CAPTURE_DIR [--out map.html]           # frames (c2viz.frames) then the page
    python -m c2viz.build --viz viz.json [--out map.html]          # from frames already built

Open the file in a browser; nothing is fetched. Query parameters: ?day=N, ?node=<id>, ?theme=broadsheet|night.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from c2viz import frames as F

TEMPLATE = Path(__file__).with_name("preview.html")
PIXEL = Path(__file__).with_name("pixel.js")


def page(viz_json: str) -> str:
    safe = viz_json.replace("</", "<\\/")                      # a "</script>" inside the data must not end the script
    return TEMPLATE.read_text().replace("__PIXEL_JS__", PIXEL.read_text().replace("</", "<\\/"), 1).replace("__VIZ_DATA__", safe, 1)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="c2viz.build")
    ap.add_argument("capture", nargs="?")
    ap.add_argument("--viz")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    if a.viz:
        viz = Path(a.viz)
    elif a.capture:
        viz = F.build(a.capture)
    else:
        ap.error("a capture directory or --viz")
    out = Path(a.out) if a.out else viz.with_name("map.html")
    out.write_text(page(viz.read_text()))
    print(out, f"{out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
