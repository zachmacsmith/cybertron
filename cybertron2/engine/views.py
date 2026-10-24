"""Views of a run (spec/record/views.md, D1-1, D1-2, D1-4): everything people look at, built from the journal and never authoritative.

    state(run, step)                 the world at a committed step
    beliefs(run, agent, step)        what the agent knew and believed then (its mind and its knowledge of crafts)
    context(run, key)                the exact input to a request: system text, reply schema, the conversation so far, the new message
    steps / events / changes / calls the journal's rows, filtered
    layout(run), frames(run)         the map: a stored layout of the world, and one frame a day of where everyone was and what happened

All read-only; the run may be writing as they read (WAL). Committed attempts by default; `with_open=True` adds the step in progress.
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

from cybertron2.engine import journal as JN

NO_REPLY = json.dumps({"why": "(no reply)", "actions": []})           # what a conversation keeps after a failed call (converse.py)


def _db(run) -> Path:
    run = Path(run)
    return run if run.suffix == ".db" else run / "run.db"


def _rows(run, sql, args=()) -> list:
    return JN.read(_db(run), sql, args)


def steps(run, with_open=False) -> list:
    ok = ("committed", "open") if with_open else ("committed",)
    return [{"step": s, "attempt": a, "status": st} for s, a, st in _rows(run, "SELECT step, attempt, status FROM steps ORDER BY rowid")
            if st in ok]


def state(run, step) -> dict:
    cp = JN.checkpoint(_db(run), step)
    if cp is None:
        raise KeyError(f"no checkpoint at {step}")
    return cp["world"]


def last_step(run) -> str:
    rows = _rows(run, "SELECT step FROM steps WHERE status = 'committed' ORDER BY rowid DESC LIMIT 1")
    return rows[0][0] if rows else None


def beliefs(run, agent, step=None) -> dict:
    w = state(run, step or last_step(run))
    return {"mind": (w.get("mind") or {}).get(agent), "know": (w.get("know") or {}).get(agent)}


# ---------------------------------------------------------------------- an agent's exact context (R3 rests on this)
def context(run, key) -> dict:
    """What the answerer of request `key` was given, rebuilt from the record (exact by construction): the system text, the reply
    schema, every earlier message and reply of the agent's running conversation, and the new message."""
    db = _db(run)
    row = _rows(run, "SELECT agent, kind, step, conversation, idx, system_sha, schema_sha, message_sha, responder FROM requests WHERE key = ?",
                (key,))
    if not row:
        raise KeyError(f"no request {key}")
    agent, kind, step, conv, idx, sys_sha, schema_sha, msg_sha, responder = row[0]
    turns = []
    if conv:
        for k, m_sha in _rows(run, "SELECT key, message_sha FROM requests WHERE conversation = ? AND idx < ? ORDER BY idx", (conv, idx)):
            turns.append({"key": k, "message": JN.unblob(db, m_sha), "reply": raw_reply(run, k)})
    answer = _rows(run, "SELECT parsed FROM responses WHERE key = ?", (key,))
    return {"key": key, "agent": agent, "kind": kind, "step": step, "responder": responder, "conversation": conv,
            "system": JN.unblob(db, sys_sha), "schema": json.loads(JN.unblob(db, schema_sha)) if schema_sha else None,
            "turns": turns, "message": JN.unblob(db, msg_sha),
            "answer": json.loads(answer[0][0]) if answer and answer[0][0] not in (None, "null") else None}


def raw_reply(run, key) -> str:
    """The reply as the conversation kept it: the raw text of the answer, or the placeholder a failed call leaves."""
    row = _rows(run, "SELECT attempts, parsed FROM responses WHERE key = ?", (key,))
    if not row:
        return NO_REPLY
    tries = json.loads(row[0][0] or "[]")
    last = tries[-1] if tries else {}
    if last.get("raw") and not last.get("error"):
        return last["raw"]
    parsed = json.loads(row[0][1]) if row[0][1] else None
    if parsed and not parsed.get("_error") and not tries:                    # a bot's or a human's answer: its JSON
        return json.dumps(parsed)
    return NO_REPLY


def requests(run, agent=None, pending=False) -> list:
    """Requests, oldest first; `pending`: those not yet answered (a human's turn waiting, R3)."""
    sql = ("SELECT r.key, r.agent, r.kind, r.step, r.responder, s.key IS NOT NULL FROM requests r LEFT JOIN responses s USING (key)"
           + (" WHERE r.agent = ?" if agent else "") + " ORDER BY r.rowid")
    out = [{"key": k, "agent": a, "kind": kd, "step": st, "responder": rp, "answered": bool(ans)}
           for k, a, kd, st, rp, ans in _rows(run, sql, (agent,) if agent else ())]
    return [r for r in out if not r["answered"]] if pending else out


# ---------------------------------------------------------------------- the journal's rows, filtered (history)
def events(run, kind=None, place=None, actor=None, days=None) -> list:
    sql, args = "SELECT id, day, step, place, kind, actor, target, about, concerns, text, cause, extra FROM events WHERE 1", []
    for col, v in (("kind", kind), ("place", place), ("actor", actor)):
        if v is not None:
            sql += f" AND {col} = ?"
            args.append(v)
    if days is not None:
        sql += " AND day BETWEEN ? AND ?"
        args += list(days)
    return [{"id": i, "day": d, "step": st, "place": p, "kind": k, "actor": a, "target": t, "about": json.loads(ab), "concerns": json.loads(c),
             "text": tx, "cause": json.loads(cs), **json.loads(ex)} for i, d, st, p, k, a, t, ab, c, tx, cs, ex in _rows(run, sql + " ORDER BY rowid", args)]


def changes(run, primitive=None, actor=None, days=None) -> list:
    sql, args = "SELECT seq, day, step, primitive, place, arguments, cause, result FROM changes WHERE 1", []
    if primitive:
        sql += " AND primitive = ?"
        args.append(primitive)
    if days is not None:
        sql += " AND day BETWEEN ? AND ?"
        args += list(days)
    out = [{"seq": q, "day": d, "step": st, "primitive": pr, "place": pl, "args": json.loads(a), "cause": json.loads(c), "result": json.loads(r)}
           for q, d, st, pr, pl, a, c, r in _rows(run, sql + " ORDER BY seq", args)]
    return [x for x in out if actor is None or (x["cause"] or {}).get("actor") == actor]


def calls(run, agent=None) -> list:
    """One row a request: who, which step, which responder, how long, what it cost, whether it failed."""
    out = []
    for key, ag, kind, step, resp, tries, parsed, usage in _rows(run, """SELECT r.key, r.agent, r.kind, r.step, r.responder, s.attempts,
            s.parsed, s.usage FROM requests r LEFT JOIN responses s USING (key) ORDER BY r.rowid"""):
        if agent and ag != agent:
            continue
        t, u, p = json.loads(tries or "[]"), json.loads(usage or "{}"), json.loads(parsed) if parsed else None
        out.append({"key": key, "agent": ag, "kind": kind, "step": step, "responder": resp, "attempts": len(t),
                    "latency": sum(float(x.get("latency") or 0) for x in t), "input_tokens": u.get("input_tokens"),
                    "output_tokens": u.get("output_tokens"), "cost_usd": u.get("cc_equiv_usd"),
                    "error": (p or {}).get("_error") if p else ("unanswered" if parsed is None else None)})
    return out


# ---------------------------------------------------------------------- the map
def layout(run) -> list:
    """Where each place is drawn (presentation only; the world has no coordinates): nodes by a seeded spring layout of the road
    graph weighted by days, parcels around their node by side, buildings on their parcel."""
    w = state(run, steps(run)[0]["step"])
    seed = json.loads(dict(_rows(run, "SELECT key, value FROM meta"))["seed"])
    nodes = sorted(w["nodes"])
    rng = random.Random(f"{seed}|layout")
    pos = {n: [rng.uniform(-1, 1), rng.uniform(-1, 1)] for n in nodes}
    edges = [(r["a"], r["b"], float(r.get("days", 1))) for r in w["roads"].values()]
    for it in range(300):                                                       # Fruchterman-Reingold, cooling
        disp = {n: [0.0, 0.0] for n in nodes}
        for i, a in enumerate(nodes):
            for b in nodes[i + 1:]:
                dx, dy = pos[a][0] - pos[b][0], pos[a][1] - pos[b][1]
                d = max(1e-3, math.hypot(dx, dy))
                f = 0.05 / d
                disp[a][0] += dx / d * f
                disp[a][1] += dy / d * f
                disp[b][0] -= dx / d * f
                disp[b][1] -= dy / d * f
        for a, b, days in edges:
            dx, dy = pos[a][0] - pos[b][0], pos[a][1] - pos[b][1]
            d = max(1e-3, math.hypot(dx, dy))
            f = (d - 0.35 * days) * 0.5
            disp[a][0] -= dx / d * f
            disp[a][1] -= dy / d * f
            disp[b][0] += dx / d * f
            disp[b][1] += dy / d * f
        t = 0.1 * (1 - it / 300) + 0.002
        for n in nodes:
            dx, dy = disp[n]
            d = max(1e-9, math.hypot(dx, dy))
            pos[n][0] += dx / d * min(d, t)
            pos[n][1] += dy / d * min(d, t)
    xs, ys = [p[0] for p in pos.values()], [p[1] for p in pos.values()]
    sx, sy = (max(xs) - min(xs)) or 1.0, (max(ys) - min(ys)) or 1.0
    rows = [{"kind": "node", "id": n, "name": w["nodes"][n].get("name", n), "node": n,
             "x": round((pos[n][0] - min(xs)) / sx, 4), "y": round((pos[n][1] - min(ys)) / sy, 4)} for n in nodes]
    at = {r["id"]: (r["x"], r["y"]) for r in rows}
    sides = {"centre": (0, 0), "north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}
    for pid, p in sorted(w["parcels"].items()):
        cx, cy = at.get(p["node"], (0.5, 0.5))
        ox, oy = sides.get(p.get("side") or "centre", (0, 0))
        j = random.Random(f"{seed}|{pid}").uniform(-0.01, 0.01)
        rows.append({"kind": "parcel", "id": pid, "name": p.get("name", pid), "node": p["node"],
                     "x": round(cx + 0.03 * ox + j, 4), "y": round(cy + 0.03 * oy - j, 4)})
    par = {r["id"]: (r["x"], r["y"]) for r in rows if r["kind"] == "parcel"}
    for bid, b in sorted(w["buildings"].items()):
        x, y = par.get(b.get("parcel"), at.get(b.get("node"), (0.5, 0.5)))
        rows.append({"kind": "building", "id": bid, "name": b.get("name", bid), "node": b.get("node"), "x": x, "y": y})
    return rows


def frames(run) -> list:
    """One frame a day (the end of the day, its `memory` step): where everyone was (at a node, or on a road by days travelled), and
    the day's events at their places. Rows: {day, kind: person|event, id, place, x, y, ...}."""
    lay = {(r["kind"], r["id"]): (r["x"], r["y"]) for r in layout(run)}
    node_xy = {i: xy for (k, i), xy in lay.items() if k == "node"}
    out = []
    ends = [s["step"] for s in steps(run) if s["step"].endswith(".memory")]
    for step in ends:
        day = int(step.split(".")[0][1:])
        w = state(run, step)
        for name, a in w["people"].items():
            if not a.get("alive", True) and a.get("died") is not None and a["died"] < day:
                continue
            t = a.get("transit")
            if a.get("at"):
                (x, y), place = node_xy.get(a["at"], (0.5, 0.5)), a["at"]
            elif t:
                r = w["roads"][t["road"]]
                (x0, y0), (x1, y1) = node_xy[t["from"]], node_xy[t["to"]]
                f = min(1.0, max(0.0, (day + 1 - t["left"]) / max(1, t["arrive"] - t["left"])))
                x, y, place = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f, t["road"]
            else:
                continue
            out.append({"day": day, "kind": "person", "id": name, "place": place, "x": round(x, 4), "y": round(y, 4),
                        "household": next((h for h, i in w["institutions"].items() if name in (i.get("members") or [])), None),
                        "alive": a.get("alive", True), "stage": a.get("stage")})
        for e in events(run, days=(day, day)):
            x, y = node_xy.get(e["place"], (None, None))
            if x is None and e["place"] in w["roads"]:
                r = w["roads"][e["place"]]
                (x0, y0), (x1, y1) = node_xy[r["a"]], node_xy[r["b"]]
                x, y = (x0 + x1) / 2, (y0 + y1) / 2
            out.append({"day": day, "kind": "event", "id": e["id"], "place": e["place"], "x": x, "y": y, "text": e["text"],
                        "event": e["kind"], "actor": e["actor"]})
    return out
