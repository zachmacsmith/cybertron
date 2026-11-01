"""Build the preview page: the pixel renderer (c2viz/js, bundled in MANIFEST order) and a run's days (c2viz.model) in one
self-contained HTML file.

    python -m c2viz.build RUN [--out map.html] [--days N]           # RUN is a run directory with its journal (run.db)
    python -m c2viz.build --viz viz.json [--out map.html]           # from a model already built
    python -m c2viz.build --js c2pixel.js                           # only the renderer, bundled, for another page

Open the file in a browser; nothing is fetched. Query parameters: ?day=N, ?node=<id>, ?z=<zoom>, ?full.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from c2viz import model as MD

TEMPLATE = Path(__file__).with_name("preview.html")
JS = Path(__file__).with_name("js")


def bundle() -> str:
    """The renderer's modules in their order (js/MANIFEST): each takes what it needs from, and adds what it defines to, one shared
    namespace; api.js puts the public face on the page."""
    names = [n.strip() for n in (JS / "MANIFEST").read_text().split() if n.strip()]
    return "var C2X = {};\n" + "\n".join((JS / f"{n}.js").read_text() for n in names)


def page(viz_json: str) -> str:
    safe = viz_json.replace("</", "<\\/")                      # a "</script>" inside the data must not end the script
    return TEMPLATE.read_text().replace("__PIXEL_JS__", bundle().replace("</", "<\\/"), 1).replace("__VIZ_DATA__", safe, 1)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="c2viz.build")
    ap.add_argument("run", nargs="?")
    ap.add_argument("--days", type=int)
    ap.add_argument("--viz")
    ap.add_argument("--out")
    ap.add_argument("--js", help="write only the bundled renderer to this file")
    a = ap.parse_args(argv)
    if a.js:
        Path(a.js).write_text(bundle())
        print(a.js)
        return
    if a.viz:
        viz = Path(a.viz)
    elif a.run:
        viz = MD.build(a.run, days=a.days)
    else:
        ap.error("a run directory or --viz")
    out = Path(a.out) if a.out else viz.with_name("map.html")
    out.write_text(page(viz.read_text()))
    print(out, f"{out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
