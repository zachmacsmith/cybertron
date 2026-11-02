"""Replay a published cybertron2 run (old log format) on the engine, feeding each call the reply it got, so the run gets a journal.

    PYTHONPATH=<engine checkout> python replay.py HF_RUN_DIR OUT --days N
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import cybertron2.engine.run as RUN
from cybertron2.engine import prompt as PR
from cybertron2.engine.here import Here
from cybertron2.engine.perceive import Mind

ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("out")
ap.add_argument("--days", type=int, default=25)
a = ap.parse_args()
src = Path(a.src)

dec, seq, mem = {}, defaultdict(list), {}
for line in open(src / "turns.jsonl"):
    t = json.loads(line)
    k = (t["day"], t["agent"])
    if not t.get("on_road"):
        dec[k] = t
    for x in t.get("talk") or []:
        wv = x.get("wave")
        kind = "talk" if isinstance(wv, int) else wv
        seq[(k, kind)].append(x)
for line in open(src / "memory.jsonl"):
    m = json.loads(line)
    mem[(m["day"], m["agent"])] = m
used = defaultdict(int)
missing = []


def recorded(w, name, kind):
    k = (w.d, name)
    if kind == "decision":
        t = dec.get(k)
        if t is None:
            missing.append((k, kind)); return {"_error": "replay: no record"}, None, None
        if t.get("error"):
            return {"_error": t["error"]}, t.get("thinking"), t.get("usage")
        return t["reply"], t.get("thinking"), t.get("usage")
    if kind == "memory":
        m = mem.get(k)
        if m is None:
            missing.append((k, kind)); return {"memory": ""}, None, None
        if m.get("error"):
            return {"_error": m["error"]}, m.get("thinking"), m.get("usage")
        return {"memory": m["memory"]}, m.get("thinking"), m.get("usage")
    i = used[(k, kind)]
    used[(k, kind)] += 1
    xs = seq.get((k, kind)) or []
    if i >= len(xs):
        missing.append((k, kind, i)); return {"_error": "replay: no record"}, None, None
    x = xs[i]
    if x.get("error"):
        return {"_error": x["error"]}, x.get("thinking"), x.get("usage")
    return x.get("reply") or {}, x.get("thinking"), x.get("usage")


def decide(w, name, text, opening, system, backend, conv, talk=None, schema=None, fuse=None, transit=False, kind="decision"):
    model = w.s["people"][name]["model"]
    if model == "bot":
        return ORIG(w, name, text, opening, system, backend, conv, talk, schema, fuse, transit, kind)
    J = w.journal
    key = J.request_key(name) if J else None
    schema = schema or PR.schema_for(Here(w, name, transit=transit or fuse is not None), Mind(w, name))
    sent, ctx = conv.message(name, w.d, system, schema, text, opening)
    if J:
        c = ctx["conv"]
        J.request(key, name, kind, f"{name}@{c['day0']}", len(c["messages"]) // 2, c["system"], schema, ctx["text"], f"model:{model}")
    out, thinking, usage = recorded(w, name, kind)
    raw = None if out.get("_error") else json.dumps(out)
    usage = conv.after(ctx, raw, {k: v for k, v in (usage or {}).items() if k != "turn"})
    if J:
        J.response(key, [{"ok": not out.get("_error"), "raw": raw, "replay": True}], out, thinking, usage, "replay")
    return out, {"model": model, "usage": usage, "seconds": 0, "thinking": thinking, "sent": ctx["text"], "opening": ctx["text"] is opening,
                 "key": key}


ORIG = RUN.decide
RUN.decide = decide
run = json.load(open(src / "run.json"))
spec_path = Path(a.out + ".spec.json")
Path(a.out).mkdir(parents=True, exist_ok=True)
spec_path.write_text(json.dumps(run["spec"]))
RUN.run(str(spec_path), a.out, backend="replay", days=a.days, workers=1)
left = {k: len(v) - used[k] for k, v in seq.items() if k[0][0] < a.days and len(v) != used[k]}
print("missing", len(missing), missing[:20])
print("unused", len(left), list(left.items())[:20])
