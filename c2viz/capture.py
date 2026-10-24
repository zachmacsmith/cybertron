"""Capture a cybertron2 run's history day by day, for the visualiser.

    python -m c2viz.capture SPEC --out DIR [--days N] [--seed S] [--bots]

Runs the engine (`cybertron2.engine.run.run`) with one hook: at the end of each day's evening (after the night, with the day's
events still in the state), the whole state is written to DIR/history/dNNNN.json.gz, with the day's calendar and weather. This is
a stand-in for the run journal (docs/cybertron2/spec/record/): when runs write checkpoints, `c2viz.frames` reads those instead.
The engine's own logs go to DIR as usual.
"""
from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path


def day_extra(w) -> dict:
    from cybertron2.engine import environment as EN
    out = {"calendar": w.calendar(), "cold": w.cold()}
    try:
        out["weather"] = EN.weather(w)
        out["words"] = EN.words(w)
    except Exception as e:                                   # a world without weather
        out["weather"] = None
        out["weather_error"] = repr(e)[:200]
    return out


def capture(spec, out_dir, days=None, seed=None, bots=True) -> Path:
    from cybertron2.engine import perceive as PC
    from cybertron2.engine import run as R
    out = Path(out_dir)
    hist = out / "history"
    hist.mkdir(parents=True, exist_ok=True)
    orig = PC.evening

    def evening(w, attend, today):
        res = orig(w, attend, today)
        rec = {"day": w.d, "extra": day_extra(w), "state": w.s}
        with gzip.open(hist / f"d{w.d:04d}.json.gz", "wt") as f:
            json.dump(rec, f, default=str)
        return res

    PC.evening = evening
    try:
        R.run(spec, out, days=days, bots=bots, seed=seed)
    finally:
        PC.evening = orig
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="c2viz.capture")
    ap.add_argument("spec")
    ap.add_argument("--out", required=True)
    ap.add_argument("--days", type=int)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--models", action="store_true", help="call the models the spec names (costs money); default: scripted bots")
    a = ap.parse_args(argv)
    print(capture(a.spec, a.out, a.days, a.seed, bots=not a.models))


if __name__ == "__main__":
    main()
