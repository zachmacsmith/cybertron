"""A run's journal (run.db, spec/record/journal.md), read for c2viz: its meta and spec, its steps, the world at a step, the changes
of a step and the talk of a day. The only place c2viz reads the journal's tables; the world itself comes through c2viz.touch.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from c2viz import touch as E


def _q(R, sql, args=()):
    con = sqlite3.connect(str(R["db"]))
    try:
        return con.execute(sql, args).fetchall()
    finally:
        con.close()


def open_run(run) -> dict:
    db = Path(run) / "run.db"
    R = {"db": db}
    meta = dict(_q(R, "SELECT key, value FROM meta"))
    steps = [r[0] for r in _q(R, "SELECT step FROM steps WHERE status = 'committed'")]
    days = sorted(int(s.split(".")[0][1:]) for s in steps if s.endswith(".memory"))
    return {"db": db, "spec": json.loads(meta["spec"]), "days": days, "seed": json.loads(meta.get("seed") or "1")}


def world_at(R, step):
    return E.world(R["spec"], E.checkpoint(R["db"], step)["world"])


def day_steps(R, d) -> list:
    return [r[0] for r in _q(R, "SELECT step FROM steps WHERE status = 'committed' AND step LIKE ? ORDER BY rowid", (f"d{d}.%",))]


def changes(R, step) -> list:
    """(seq, primitive, place, arguments, cause, result) of one step, in order."""
    return _q(R, "SELECT seq, primitive, place, arguments, cause, result FROM changes WHERE step = ? ORDER BY seq", (step,))


def speech(R, d) -> list:
    return [dict(zip(("actor", "place", "kind", "text"), r)) for r in _q(
        R, "SELECT actor, place, kind, text FROM events WHERE step LIKE ? AND kind = 'speech' ORDER BY rowid", (f"d{d}.talk%",))]
