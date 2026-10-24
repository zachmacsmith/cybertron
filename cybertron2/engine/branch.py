"""Branching a run (spec/record/branching.md, D1-1, D1-4; R4 of proposals/run_record.md): rewind, fork, replicates, interventions,
continuing under other code, and the branches of a run.

- `rewind RUN --to STEP --out NEW`: a new run whose journal holds the parent's record up to that step's commit; `resume NEW` plays
  on from there. The parent is never changed.
- `fork RUN --at STEP [--apply iv.yaml] [--replicates K] [--as NAME=model:<id>|bot|human] --out DIR`: a rewind whose new run
  also applies interventions, gives agents other responders and, for replicates, salts the seed for every draw after the fork
  point; then it is played on. Earlier requests are answered from the parent's record (the replay of resume).
- `continue RUN --at STEP --out DIR`: plays on from the checkpoint at the end of a day under the current code, with no claim that
  a replay would match (a segment with both code shas).

Interventions are typed ops on primitives, applied through World.apply inside a cause of kind `intervention` after the commit of
their step, every time the run is played (so a resume reproduces them), and recorded as applied once, with a digest of the state.
"""
from __future__ import annotations

import json
import shutil
import sqlite3
from pathlib import Path

from cybertron2.engine import journal as JN

STEPS = ("dawn", "decide", "talk.0", "talk.1", "work", "settle", "night", "memory")


def order(key: str) -> tuple:
    """A step key's place in the run: (day, step)."""
    day, step = key.split(".", 1)
    return int(day[1:]), STEPS.index(step)


def _later(key, step) -> bool:
    return order(key) > order(step)


def _committed(db, step) -> bool:
    return bool(JN.read(db, "SELECT 1 FROM steps WHERE step = ? AND status = 'committed'", (step,)))


def _copy(src: Path, out: Path) -> Path:
    """The parent's journal and run.json, copied (the WAL folded in first)."""
    src, out = Path(src), Path(out)
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"{out} is not empty")
    out.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(src / "run.db"))
    db.execute("PRAGMA wal_checkpoint(FULL)")
    db.close()
    shutil.copy(src / "run.db", out / "run.db")
    shutil.copy(src / "run.json", out / "run.json")
    return out / "run.db"


def step_of(key: str) -> str:
    """The step of a request key: d3.decide.Alard.1 -> d3.decide; d3.talk.0.Alard.1 -> d3.talk.0."""
    parts = key.split(".")
    return ".".join(parts[:3] if parts[1] == "talk" else parts[:2])


def _cut(db: Path, to: str) -> None:
    """Remove everything after `to` (steps and their checkpoints, requests and their answers, events, changes), and any attempt
    not committed."""
    con = sqlite3.connect(str(db))
    con.create_function("later", 1, lambda k: bool(k) and _later(k, to))
    con.create_function("key_later", 1, lambda k: _later(step_of(k), to))
    con.execute("BEGIN")
    for table in ("steps", "checkpoints", "events", "changes", "requests"):
        con.execute(f"DELETE FROM {table} WHERE later(step)")
    con.execute("DELETE FROM responses WHERE key_later(key)")
    con.execute("DELETE FROM abandoned WHERE key_later(key)")
    con.execute("DELETE FROM steps WHERE status != 'committed'")
    con.execute("COMMIT")
    con.close()


def _segment(db, kind, step, parent, extra=None) -> None:
    prov = JN.provenance()
    con = sqlite3.connect(str(db))
    con.execute("INSERT INTO segments (kind, first_step, code_sha, parent, responders) VALUES (?, ?, ?, ?, ?)",
                (kind, None, prov["code_sha"], JN.dumps({"run": str(parent), "step": step, **(extra or {})}), JN.dumps({})))
    con.commit()
    con.close()


def rewind(run, to, out) -> Path:
    if not _committed(Path(run) / "run.db", to):
        raise SystemExit(f"{to} is not a committed step of {run}")
    db = _copy(run, out)
    _cut(db, to)
    _segment(db, "rewind", to, run)
    return Path(out)


def fork(run, at, out, interventions=None, responders=None, salt=None) -> Path:
    """A new run from `at`: the record to there, then the interventions, responders and salt from the fork point on."""
    if not _committed(Path(run) / "run.db", at):
        raise SystemExit(f"{at} is not a committed step of {run}")
    db = _copy(run, out)
    _cut(db, at)
    for x in interventions or []:
        x = {"after": x.get("after") or at, **x}
        if _later(at, x["after"]):
            raise SystemExit(f"an intervention after {x['after']} is before the fork point {at}")
        con = sqlite3.connect(str(db))
        con.execute("INSERT INTO interventions (submitted, applied) VALUES (?, NULL)", (JN.dumps(x),))
        con.commit()
        con.close()
    settings = {"at": at, "salt": salt, "responders": dict(responders or {})}
    con = sqlite3.connect(str(db))
    con.execute("INSERT OR REPLACE INTO meta VALUES ('fork', ?)", (JN.dumps(settings),))
    con.commit()
    con.close()
    _segment(db, "fork", at, run, {"salt": salt, "responders": settings["responders"]})
    return Path(out)


def replicates(run, at, out, k, interventions=None, responders=None) -> list:
    """K forks that differ only by a salt on the draws after the fork point (D1-4: `rep<k>`)."""
    return [fork(run, at, Path(out) / f"rep{i}", interventions, responders, salt=f"rep{i}") for i in range(1, int(k) + 1)]


def continue_(run, at, out) -> Path:
    """A new run that plays on from the checkpoint at the end of a day under the current code (run.py mode "continue")."""
    if not at.endswith(".memory") or not _committed(Path(run) / "run.db", at):
        raise SystemExit(f"{at}: continue starts from the end of a committed day (dN.memory)")
    db = _copy(run, out)
    _cut(db, at)
    con = sqlite3.connect(str(db))
    con.execute("INSERT OR REPLACE INTO meta VALUES ('continue', ?)", (JN.dumps({"at": at}),))
    con.commit()
    con.close()
    _segment(db, "continue", at, run, {"from_code": JN.read(db, "SELECT code_sha FROM segments ORDER BY id LIMIT 1")[0][0]})
    return Path(out)


# ---------------------------------------------------------------------- applied while a run is played (run.py: J.after_commit)
def after_commit(w, J, step) -> None:
    """After a step's commit: the fork's settings from its fork point, and the interventions due after this step. Done on every
    play of the run (a resume reproduces them); recorded as applied the first time."""
    fk = J.fork
    if fk and fk["at"] == step:
        if fk.get("salt"):
            w.s["salt"] = fk["salt"]
        for name, responder in (fk.get("responders") or {}).items():
            if name in w.s["people"]:
                model = responder.split(":", 1)[1] if responder.startswith("model:") else responder
                w.apply("set", w.place_of(("person", name)), ref=("person", name), field="model", value=model)
    for iid, x, applied in J.interventions_after(step):
        quiet, J.quiet = J.quiet, J.quiet and bool(applied)                # its first application is written, even in a replay
        with w.cause(actor="(intervention)", verb="intervention", for_=x.get("note")):
            if x["op"] == "event":
                w.event(x["place"], x["args"].get("kind", "intervention"), x["args"]["text"], **{k: v for k, v in x["args"].items()
                                                                                                  if k not in ("kind", "text")})
            else:
                w.apply(x["op"], x.get("place"), **_args(x["args"]))
        J.quiet = quiet
        if not applied:
            J.applied(iid, {"step": step, "op": x["op"], "args": x["args"], "note": x.get("note"),
                            "digest": JN.sha(JN.dumps(w.s))})


def _args(a: dict) -> dict:
    """References written in YAML as lists are tuples to the primitives (ref, thing)."""
    return {k: (tuple(v) if k in ("ref", "thing") and isinstance(v, list) else v) for k, v in a.items()}


def branches(run) -> dict:
    """A run's own lineage (its segments) and the runs beside it that were branched from it."""
    run = Path(run)
    segs = JN.read(run / "run.db", "SELECT kind, first_step, code_sha, parent FROM segments ORDER BY id")
    children = []
    for d in sorted(p for p in run.parent.rglob("run.db") if p.parent != run):
        for kind, parent in JN.read(d, "SELECT kind, parent FROM segments WHERE parent IS NOT NULL"):
            p = json.loads(parent)
            if Path(p["run"]).resolve() == run.resolve():
                children.append({"run": str(d.parent), "kind": kind, "at": p["step"]})
    return {"segments": [{"kind": k, "first_step": f, "code_sha": c, "parent": json.loads(p) if p else None} for k, f, c, p in segs],
            "branches": children}
