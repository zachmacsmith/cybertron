"""Frames for the map: one compact record per day of everything the visualiser draws, plus the static world and its layout.

    python -m c2viz.frames CAPTURE_DIR [--out viz.json]

Input: a capture (c2viz.capture: history/dNNNN.json.gz, the whole state at each day's end, with the calendar and weather) and the
engine's own logs in the same directory (turns.jsonl for what each agent said and why). When runs write the journal
(docs/cybertron2/spec/record/), a reader of its checkpoints replaces `load_history`; nothing else changes.

Output (viz.json):
  meta     the world's name, days, people, where it came from
  static   nodes, roads (terrain, stretches, landmarks, ends), parcels (cover, size, side, height, neighbours, text),
           layout: world positions, and per node: parcel cells, centres, lots, outline, road exits
  days     one record a day: calendar and weather; per parcel resources (share of capacity), crop, fertility, fence, works,
           holders; buildings; herds; things lying about; people (where, doing what, hunger, stage, household, hands); travellers
           on roads; the day's acts, events, speech and the night (deaths, fights, breaks, the cold); households; claims
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import math
from pathlib import Path

from c2viz import layout as L

FOOD = {"grain", "flour", "bread", "beans", "rye", "wild food", "meat", "milk", "cheese", "porridge", "fish", "hay"}
QUIET_EVENTS = {"sign"}                                      # ambient signs: shown in the detail panel, not as map marks


def load_history(cap: Path) -> list:
    out = []
    for f in sorted(glob.glob(str(cap / "history" / "d*.json.gz"))):
        with gzip.open(f, "rt") as fh:
            out.append(json.load(fh))
    return out


def _goods(g, n=8) -> dict:
    return {k: round(v, 2) for k, v in sorted((g or {}).items(), key=lambda kv: -kv[1])[:n] if v > 1e-6}


def _holders(s) -> dict:
    """thing -> [claimant, ...] with management or withdrawal rights (who holds it, as recognised)."""
    out = {}
    for c in s["claims"].values():
        if c.get("until") is not None and c["until"] < s["day"]:
            continue
        kind, key = c["thing"]
        if {"management", "withdrawal", "access"} & set(c.get("rights") or []):
            out.setdefault(f"{kind}:{key}", []).append(c["claimant"])
    return out


def _household_of(s) -> dict:
    out = {}
    for iid, inst in s["institutions"].items():
        if inst.get("kind") == "household":
            for m in inst.get("members") or []:
                out[m] = iid
    return out


def static(first: dict, last: dict, seed=1) -> dict:
    s0, s1 = first["state"], last["state"]
    nodes = {k: {"name": v["name"], "text": v.get("text", ""), "unexplored": bool(v.get("unexplored"))} for k, v in s1["nodes"].items()}
    roads = {}
    for rid, r in s1["roads"].items():
        roads[rid] = {"a": r["a"], "b": r["b"], "days": r.get("days", 1), "terrain": r.get("terrain"), "way": r.get("way"),
                      "track": r.get("track"), "stretches": r.get("stretches") or [],
                      "ends": {n: {"side": e.get("side"), "parcels": e.get("parcels"), "hidden": e.get("hidden")}
                               for n, e in (r.get("ends") or {}).items()}}
    parcels = {pid: {k: p.get(k) for k in ("node", "name", "cover", "size", "side", "height", "adj", "text")}
               for pid, p in s1["parcels"].items()}
    wl = L.world_layout(nodes, roads, seed)
    nl = {nid: L.node_layout(nid, s1["parcels"], s1["roads"], seed) for nid in nodes}
    for nid, lay in nl.items():                                    # a road leaving from the middle points at its other end
        for rid, ex in lay["exits"].items():
            if ex["dir"] == [0.0, 0.0] and ex["to"] in wl:
                dx, dy = wl[ex["to"]][0] - wl[nid][0], wl[ex["to"]][1] - wl[nid][1]
                d = math.hypot(dx, dy) or 1.0
                ex["dir"] = [round(dx / d, 3), round(dy / d, 3)]
    return {"nodes": nodes, "roads": roads, "parcels": parcels, "layout": {"world": wl, "nodes": nl}}


def day_record(rec: dict, prev: dict | None, said: dict) -> dict:
    s, d = rec["state"], rec["day"]
    hold = _holders(s)
    hh = _household_of(s)
    acts = [a for a in s["acts"] if a["day"] == d]
    last_site = {}
    for a in acts:
        if a.get("site"):
            last_site[a["actor"]] = a["site"]
    night = next((x for x in reversed(s.get("log") or []) if x.get("day") == d), {})
    slept = night.get("slept") or {}
    bname = {b["name"]: bid for bid, b in s["buildings"].items()}
    parcels = {}
    for pid, p in s["parcels"].items():
        res = {k: round(min(1.0, float(r.get("S", 0)) / float(r.get("K") or 1)), 3) for k, r in (p.get("res") or {}).items()
               if isinstance(r, dict) and r.get("K")}
        crop = p.get("crop")
        if crop:
            ripe = d >= int(crop.get("ripe_day", 1e9))
            crop = {"kind": crop.get("kind"), "crop": crop.get("crop"), "sown": crop.get("sown"), "ripe_day": crop.get("ripe_day"),
                    "window": crop.get("window"), "left": round(float(crop.get("area_left", 0)) / max(1e-6, float(crop.get("area") or 1)), 3),
                    "ripe": ripe, "failed": bool(crop.get("failed")), "weeded": crop.get("weeded")}
        fence = p.get("fence")
        if fence:
            fence = {"kind": fence.get("kind"), "level": fence.get("level"), "built": fence.get("built"), "gate": fence.get("gate")}
        parcels[pid] = {"res": res, "crop": crop, "fertility": round(float(p.get("fertility") or 0), 3), "fence": fence,
                        "works": p.get("works"), "broken": p.get("broken"), "holders": hold.get(f"parcel:{pid}", [])}
    buildings = {}
    for bid, b in s["buildings"].items():
        st = s["containers"].get(b.get("stock") or "", {}).get("goods", {})
        un = b.get("unfinished")
        buildings[bid] = {"node": b["node"], "parcel": b["parcel"], "name": b["name"], "structure": b.get("structure"),
                          "size": b.get("size"), "fittings": b.get("fittings") or {}, "condition": b.get("condition"),
                          "fire": bool(b.get("fire")), "door": b.get("door"), "stock": _goods(st, 10),
                          "food": round(sum(v for k, v in st.items() if k in FOOD), 1),
                          "unfinished": ({"blueprint": un.get("blueprint"), "units_left": un.get("units_left")} if un else None),
                          "holders": hold.get(f"building:{bid}", []),
                          "sleepers": sorted(n for n, where in slept.items() if where == b["name"])}
    herds = {hid: {"node": x["node"], "parcel": x.get("parcel"), "home": x.get("home"), "name": x.get("name"), "kind": x.get("kind"),
                   "count": x.get("count"), "hungry": x.get("hungry"), "in_milk": x.get("in_milk"),
                   "holders": hold.get(f"herd:{hid}", [])}
             for hid, x in s["herds"].items()}
    things = {}
    for cid, c in s["containers"].items():
        if c["kind"] in ("hands", "stock"):
            continue
        has = any(q > 1e-9 for q in c["goods"].values())
        if not (has or c.get("body") or c.get("beast")):
            continue
        kind = "body" if c.get("body") else "carcass" if c.get("beast") else c["kind"]
        things[cid] = {"node": c.get("node"), "parcel": c.get("parcel"), "in": c.get("in"), "kind": kind, "of": c.get("of"),
                       "goods": _goods(c["goods"], 6), "buried": c.get("buried"), "died": c.get("died"),
                       "on_road": bool(c.get("on_road")), "hidden": c.get("hidden")}
    people, travellers = {}, {}
    for n, p in s["people"].items():
        if not p.get("alive") and (p.get("died") is None or p["died"] < d - 3):
            continue                                              # the long dead drop off the map (their bodies stay as things)
        hands = s["containers"].get(p.get("hands") or "", {}).get("goods", {})
        where_b = bname.get(slept.get(n)) if slept.get(n) else None
        parcel = last_site.get(n) or (s["buildings"][where_b]["parcel"] if where_b else None)
        rec_p = {"node": p.get("at"), "parcel": parcel, "slept": where_b, "alive": bool(p.get("alive")), "died": p.get("died"),
                 "cause": p.get("cause"), "stage": p.get("stage"), "sex": p.get("sex"), "household": hh.get(n), "hunger": p.get("hunger"),
                 "missed": p.get("missed"), "wounded": bool(p.get("wounded")), "trade": p.get("trade"), "model": p.get("model"),
                 "hands": _goods(hands, 6), "aim": p.get("aim")}
        t = p.get("transit")
        if t:
            span = max(1, int(t.get("arrive", d + 1)) - int(t.get("left", d)))
            rec_p["transit"] = {"road": t.get("road"), "from": t.get("from"), "to": t.get("to"), "left": t.get("left"),
                                "arrive": t.get("arrive"), "progress": round(min(1.0, max(0.0, (d + 1 - int(t.get("left", d))) / span)), 3)}
            travellers[n] = rec_p["transit"]
        people[n] = rec_p
    events = [{"kind": e["kind"], "place": e["place"], "about": e.get("about") or [], "actor": e.get("actor"), "target": e.get("target"),
               "text": e.get("text"), "tech": e.get("tech")}
              for e in s.get("events") or [] if e["kind"] not in QUIET_EVENTS]
    signs = [{"place": e["place"], "about": e.get("about") or [], "text": e.get("text")} for e in s.get("events") or []
             if e["kind"] in QUIET_EVENTS][:60]
    households = {iid: {"name": x.get("name"), "members": x.get("members") or [], "head": (x.get("offices") or {}).get("head")}
                  for iid, x in s["institutions"].items() if x.get("kind") == "household"}
    changed = []
    if prev:
        for kind, cur, old in (("building", buildings, prev["buildings"]), ("parcel", parcels, prev["parcels"]),
                               ("herd", herds, prev["herds"])):
            changed += [f"{kind}:{k}" for k, v in cur.items() if old.get(k) != v]
    ex = rec.get("extra") or {}
    return {"day": d, "calendar": ex.get("calendar"), "weather": ex.get("weather"), "weather_words": ex.get("words"),
            "cold": ex.get("cold"), "parcels": parcels, "buildings": buildings, "herds": herds, "things": things, "people": people,
            "travellers": travellers, "acts": [{k: a.get(k) for k in ("actor", "verb", "tech", "for", "node", "site")} for a in acts],
            "events": events, "signs": signs, "said": said.get(d, {}),
            "night": {k: night.get(k) for k in ("deaths", "fights", "breaks", "cold_falls", "departed", "missed", "spoiled")},
            "households": households, "changed": changed}


def _lines(x) -> list:
    """say / tell as the reply gives them ([{to, text}], a string, or a list of strings) -> [{to, text}]."""
    if not x:
        return []
    if isinstance(x, str):
        return [{"to": "everyone", "text": x[:400]}]
    out = []
    for y in x if isinstance(x, list) else [x]:
        if isinstance(y, dict) and y.get("text"):
            out.append({"to": str(y.get("to") or "everyone"), "text": str(y["text"])[:400]})
        elif isinstance(y, str):
            out.append({"to": "everyone", "text": y[:400]})
    return out


def said_by_day(cap: Path) -> dict:
    """{day: {agent: {why, say}}} from turns.jsonl (what each said aloud and why it chose its acts), when the run has it."""
    out = {}
    f = cap / "turns.jsonl"
    if not f.exists():
        return out
    with open(f) as fh:
        for line in fh:
            t = json.loads(line)
            r = t.get("reply") or {}
            why = r.get("why")
            say = _lines(r.get("say"))
            tell = _lines(r.get("tell"))
            for x in t.get("talk") or []:                            # what the talk step added
                rr = x.get("reply") or {}
                say += _lines(rr.get("say"))
                tell += _lines(rr.get("tell"))
            if why or say or tell:
                out.setdefault(t["day"], {})[t["agent"]] = {"why": (why or "")[:600], "say": say[:6], "tell": tell[:6]}
    return out


def build(cap, out=None, seed=None) -> Path:
    cap = Path(cap)
    hist = load_history(cap)
    if not hist:
        raise SystemExit(f"{cap}: no history/ (capture a run with python -m c2viz.capture)")
    run = json.loads((cap / "run.json").read_text()) if (cap / "run.json").exists() else {}
    spec = run.get("spec") or {}
    seed = seed if seed is not None else spec.get("seed", 1)
    said = said_by_day(cap)
    days, prev = [], None
    for rec in hist:
        dr = day_record(rec, prev, said)
        days.append(dr)
        prev = dr
    st = static(hist[0], hist[-1], seed)
    people0 = hist[0]["state"]["people"]
    meta = {"name": spec.get("name") or cap.name, "days": len(days), "source": str(cap), "seed": seed,
            "people": {n: {"sex": p.get("sex"), "stage": p.get("stage"), "model": p.get("model"), "born_line": p.get("born_line"),
                           "trade": p.get("trade"), "aim": p.get("aim")} for n, p in people0.items()},
            "models": sorted({p.get("model") for p in people0.values() if p.get("model")})}
    data = {"meta": meta, "static": st, "days": days}
    out = Path(out) if out else cap / "viz.json"
    out.write_text(json.dumps(data, separators=(",", ":"), default=str))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="c2viz.frames")
    ap.add_argument("capture")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    p = build(a.capture, a.out)
    print(p, f"{p.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
