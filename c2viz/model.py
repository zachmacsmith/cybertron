"""A run's days in the engine's own terms, for the renderer (c2viz/ENGINE.md §8, c2viz/SCHEMA.md).

Reads a run's journal (c2viz.source), rebuilds the World at each day's end (the `d{d}.memory` checkpoint) and builds each day's
record (c2viz.extract) and, optionally, the day as it happened (c2viz.timeline). The engine is touched only through c2viz.touch;
the renderer reads only what c2viz.schema describes.

    python -m c2viz.model RUN [--out RUN/viz.json] [--days N] [--no-timeline]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from c2viz import ground as GR
from c2viz.extract import day_record
from c2viz.layout import node_layout, world_layout
from c2viz.schema import SCHEMA_VERSION, validate
from c2viz.source import open_run, world_at
from c2viz.spec_rooms import GROUND, ROOMS, SPACES, Rooms
from c2viz.timeline import timeline
from c2viz import touch as E


# ---------------------------------------------------------------------------------------------------- the whole run
def static(w0, seed) -> dict:
    s = w0.s
    nodes = {nid: {"name": n["name"], "text": n.get("text"), "unexplored": bool(n.get("unexplored"))} for nid, n in s["nodes"].items()}
    parcels = {pid: {k: p.get(k) for k in ("node", "name", "cover", "size", "side", "height", "adj", "text", "ground")} for pid, p in s["parcels"].items()}
    roads = {rid: {"a": r["a"], "b": r["b"], "days": r["days"], "track": bool(r.get("track")), "way": r.get("way"), "terrain": r.get("terrain"),
                   "stretches": r.get("stretches") or [],
                   "ends": {n: {"side": e.get("side"), "parcels": e.get("parcels") or [], "hidden": bool(e.get("hidden"))} for n, e in (r.get("ends") or {}).items()}}
             for rid, r in s["roads"].items()}
    wl = world_layout(s["nodes"], s["roads"], seed)
    nl = {nid: node_layout(nid, s["parcels"], s["roads"], seed) for nid in s["nodes"]}
    return {"nodes": nodes, "parcels": parcels, "roads": roads, "layout": {"world": wl, "nodes": nl}}


def tables() -> dict:
    """The engine's tables the renderer reads (never its own copies), and the spec's space model until the engine has it."""
    return E.tables() | {"spec": {"spaces": SPACES, "ground": GROUND, "rooms": ROOMS, "source": "economy/buildings.md D2-154, D2-155 (not yet in the engine)"}}


def build(run, out=None, days=None, timelines=True, land=None) -> Path:
    R = open_run(run)
    want = R["days"] if days is None else [d for d in R["days"] if d < days]
    rooms = Rooms()
    w0 = world_at(R, "d0.dawn")
    st = static(w0, R["seed"])
    recs = []
    for d in want:
        rec = day_record(world_at(R, f"d{d}.memory"), rooms)
        if timelines:
            rec["timeline"] = timeline(R, d, rooms)
        recs.append(rec)
    people = {n: {"household": w0.household_of(n), "model": p.get("model")} for n, p in w0.s["people"].items()}
    meta = {"name": R["spec"].get("name") or Path(run).name, "days": len(recs), "seed": R["seed"], "source": str(Path(run).resolve()),
            "people": people, "season_days": w0.season_len, "schema": SCHEMA_VERSION}
    viz = {"meta": meta, "tables": tables(), "static": st, "days": recs}
    ground = GR.pack(run, R["spec"], st["roads"], land)                      # a generated world's ground truth (ENGINE.md §12)
    if ground:
        viz["land"] = ground
        c = ground["roads_check"]
        print(f"c2viz ground: {Path(ground['source']).name}, roads by the generator's rule {c['match']}/{c['roads']} leave by the world's parcels"
              + (f" (not: {', '.join(c['unmatched'])})" if c["unmatched"] else ""))
    for problem in validate(viz):
        print("c2viz schema:", problem)
    out = Path(out) if out else Path(run) / "viz.json"
    out.write_text(json.dumps(viz, separators=(",", ":"), default=str))
    return out


def build_world(path, out=None, land=None) -> Path:
    """A world that has not been run, drawn as its file makes it (dawn of day 0: the land, the houses, the people at home, the
    herds), from the world file alone; a generated world with its ground truth (the cells beside it). No journal, no timeline."""
    path = Path(path)
    spec = E.load_spec(path)
    w0 = E.fresh_world(spec)
    rooms = Rooms()
    rec = day_record(w0, rooms)
    st = static(w0, w0.seed)
    people = {n: {"household": w0.household_of(n), "model": p.get("model")} for n, p in w0.s["people"].items()}
    meta = {"name": spec.get("name") or path.stem, "days": 1, "seed": w0.seed, "source": str(path.resolve()), "people": people,
            "season_days": w0.season_len, "schema": SCHEMA_VERSION, "unrun": True}
    viz = {"meta": meta, "tables": tables(), "static": st, "days": [rec]}
    cells = Path(land) if land else path.with_name(path.stem + ".cells.npz")                # the generator writes it beside the world
    ground = GR.pack(path.parent, spec, st["roads"], cells) if cells.exists() else None
    if ground:
        viz["land"] = ground
    for problem in validate(viz):
        print("c2viz schema:", problem)
    out = Path(out) if out else path.with_suffix(".viz.json")
    out.write_text(json.dumps(viz, separators=(",", ":"), default=str))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("run", help="a run (its journal), or with --world a world file")
    ap.add_argument("--world", action="store_true", help="draw a world file that has not been run (dawn of day 0)")
    ap.add_argument("--out")
    ap.add_argument("--days", type=int)
    ap.add_argument("--no-timeline", action="store_true", help="only each day's end, not the day as it happened")
    ap.add_argument("--land", help="the world's cells (.cells.npz) when not beside the run or its world file")
    a = ap.parse_args(argv)
    p = build_world(a.run, a.out, a.land) if a.world else build(a.run, a.out, a.days, not a.no_timeline, a.land)
    print(p, f"{p.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
