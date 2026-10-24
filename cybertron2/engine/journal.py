"""The run's journal (spec/record/journal.md, execution.md; D1-1 to D1-5): one SQLite file per run, `run.db`, in WAL mode, written as
things happen and readable while the run writes. It holds the run's inputs (provenance, the frozen data tables, the resolved spec
and seed, every request and its answer by key), a checkpoint at each committed step, and every event and change with its cause.

R1 (proposals/run_record.md, "Order of work"): the journal is written alongside the run's other files and changes nothing the run
does. Resume, cancel, pause and replay (R2) read it later.
"""
from __future__ import annotations

import hashlib
import json
import platform
import sqlite3
import subprocess
import threading
import time
import zlib
from pathlib import Path

SCHEMA = 1
TABLES = {
    "meta": "key TEXT PRIMARY KEY, value TEXT",
    "data": "name TEXT PRIMARY KEY, content TEXT",
    "segments": "id INTEGER PRIMARY KEY, kind TEXT, first_step TEXT, code_sha TEXT, parent TEXT, responders TEXT",
    "steps": "step TEXT, attempt INTEGER, status TEXT, started REAL, ended REAL, checkpoint TEXT, PRIMARY KEY (step, attempt)",
    "requests": "key TEXT PRIMARY KEY, step TEXT, attempt INTEGER, agent TEXT, kind TEXT, conversation TEXT, idx INTEGER, "
                "system_sha TEXT, schema_sha TEXT, message_sha TEXT, responder TEXT",
    "responses": "key TEXT PRIMARY KEY, attempts TEXT, parsed TEXT, thinking TEXT, usage TEXT, transport TEXT",
    "blobs": "sha TEXT PRIMARY KEY, z BLOB",
    "checkpoints": "step TEXT, attempt INTEGER, sha TEXT, z BLOB, PRIMARY KEY (step, attempt)",
    "events": "id TEXT, day INTEGER, step TEXT, attempt INTEGER, place TEXT, kind TEXT, actor TEXT, target TEXT, about TEXT, "
              "concerns TEXT, text TEXT, cause TEXT, extra TEXT",
    "changes": "seq INTEGER PRIMARY KEY, day INTEGER, step TEXT, attempt INTEGER, primitive TEXT, place TEXT, arguments TEXT, "
               "cause TEXT, result TEXT",
    "interventions": "id INTEGER PRIMARY KEY, submitted TEXT, applied TEXT",
    "abandoned": "key TEXT, attempts TEXT, parsed TEXT, at REAL",          # failed calls of an abandoned day (fail-stop)
}
EVENT_COLS = ("id", "day", "place", "kind", "actor", "target", "about", "concerns", "text")


def dumps(x) -> str:
    """JSON in the order the engine made it: dicts keep their order, which the engine's iteration depends on (a world built from a
    key-sorted copy is not the same world)."""
    return json.dumps(x, default=_plain, separators=(",", ":"))


def _plain(x):
    if isinstance(x, (set, frozenset)):
        return sorted(x, key=str)
    return str(x)


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def provenance(root=None) -> dict:
    """The code a run ran under: git sha, dirty flag and diff sha, a sha per cybertron2 module, python (journal.md, Inputs)."""
    root = Path(root or Path(__file__).resolve().parents[2])
    git = lambda *a: subprocess.run(["git", "-C", str(root), *a], capture_output=True, text=True).stdout
    head = git("rev-parse", "HEAD").strip() or None
    status = git("status", "--porcelain", "--untracked-files=no")
    diff = git("diff", "HEAD") if status.strip() else ""
    mods = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()[:16]
            for p in sorted((root / "cybertron2").rglob("*.py"))}
    return {"git": head, "dirty": bool(status.strip()), "diff_sha": sha(diff) if diff else None, "modules": mods,
            "code_sha": sha(dumps(mods)), "python": platform.python_version()}


def frozen_tables() -> dict:
    """Every engine data table the run reads, as it stood at the start (journal.md, Inputs)."""
    from cybertron2.engine import data as D, signs as SG
    out = {k: v for k, v in vars(D).items() if k.isupper() and isinstance(v, (dict, list, tuple))}
    out.update({f"signs.{k}": v for k, v in vars(SG).items() if k.isupper() and isinstance(v, (dict, list, tuple))})
    return out


class Paused(Exception):
    """The run stops after a committed step: `--until`, or the end of a replay."""


class Journal:
    """Rows are written the moment they exist, each tagged with its step and attempt; a step's commit (one transaction: its
    checkpoint and its status) makes it official (D1-2)."""

    def __init__(self, path):
        self.path = Path(path)
        self.db = sqlite3.connect(str(self.path), check_same_thread=False, isolation_level=None)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=NORMAL")
        for name, cols in TABLES.items():
            self.db.execute(f"CREATE TABLE IF NOT EXISTS {name} ({cols})")
        self.lock = threading.RLock()
        self.step, self.attempt, self.day = None, None, None
        self.counts = {}
        self.failures = 0
        self.replaying = False                 # resume and replay: committed steps are played again, checked, not rewritten
        self.strict = False                    # replay: stop at the first step not committed
        self.until = None                      # pause after this step's commit
        self.quiet = False
        self.committed = {}
        self.checked, self.mismatches = 0, []
        self.after_commit = None               # called after each commit (branch.after_commit: a fork's settings, interventions)
        row = self.db.execute("SELECT value FROM meta WHERE key = 'fork'").fetchone()
        self.fork = json.loads(row[0]) if row else None

    def interventions_after(self, step) -> list:
        with self.lock:
            rows = self.db.execute("SELECT id, submitted, applied FROM interventions ORDER BY id").fetchall()
        return [(i, x, a) for i, x, a in ((i, json.loads(sub), app) for i, sub, app in rows) if x.get("after") == step]

    def applied(self, iid, rec) -> None:
        self._x("UPDATE interventions SET applied = ? WHERE id = ? AND applied IS NULL", (dumps(rec), iid))

    # ------------------------------------------------------------------ resume and replay (R2, execution.md)
    def resume(self, strict=False, until=None, kind="resume") -> None:
        """Play the run again from its start: every request is answered from the journal, each committed step is checked against
        its checkpoint instead of written, and the first step not committed is run live as a new attempt."""
        self.committed = {k: (a, h) for k, a, h in self.db.execute(
            "SELECT step, attempt, checkpoint FROM steps WHERE status = 'committed'").fetchall()}
        self.replaying, self.strict, self.until = True, strict, until
        if not strict:
            prov = provenance()
            row = self.db.execute("SELECT value FROM meta WHERE key = 'provenance'").fetchone()
            was = json.loads(row[0])["code_sha"] if row else None
            if was != prov["code_sha"]:
                print(f"journal: the code has changed since this run began ({was} -> {prov['code_sha']}); resuming anyway", flush=True)
            self._x("INSERT INTO segments (kind, first_step, code_sha, parent, responders) VALUES (?, ?, ?, ?, ?)",
                    (kind, None, prov["code_sha"], None, dumps({})))

    def abandon_day(self, day) -> None:
        """A day dropped by the fail-stop: its steps aborted, its failed calls set aside (not answers: asked again on resume)."""
        pat = f"d{day}.%"
        with self.lock:
            self.db.execute("BEGIN")
            self.db.execute("INSERT INTO abandoned SELECT key, attempts, parsed, ? FROM responses WHERE key LIKE ? AND parsed LIKE '%\"_error\"%'",
                            (time.time(), pat))
            self.db.execute("DELETE FROM responses WHERE key LIKE ? AND parsed LIKE '%\"_error\"%'", (pat,))
            self.db.execute("UPDATE steps SET status = 'aborted' WHERE step LIKE ? AND status IN ('open', 'committed')", (pat,))
            self.db.execute("COMMIT")

    def answer(self, key) -> dict | None:
        """The recorded answer to a request, if it was answered (an answer, or a failure the run took as one)."""
        with self.lock:
            row = self.db.execute("SELECT parsed, attempts, thinking, usage, transport FROM responses WHERE key = ?", (key,)).fetchone()
        if not row or row[0] in (None, "null"):
            return None
        tries = json.loads(row[1] or "[]")
        last = tries[-1] if tries else {}
        return {"parsed": json.loads(row[0]), "raw": last.get("raw") if not last.get("error") else None, "thinking": row[2],
                "usage": json.loads(row[3] or "{}"), "transport": row[4]}

    def check_message(self, key, message) -> None:
        """On replay, the message the engine would send now must be the one it sent then (the prompt reads only the state)."""
        with self.lock:
            row = self.db.execute("SELECT message_sha FROM requests WHERE key = ?", (key,)).fetchone()
        if row and row[0] and row[0] != sha(str(message)):
            self.mismatches.append({"key": key, "what": "message"})

    # ------------------------------------------------------------------ writing
    def _x(self, sql, args=()):
        with self.lock:
            try:
                self.db.execute(sql, args)
            except sqlite3.Error as e:                                        # the journal never stops the run; it says so
                self.failures += 1
                if self.failures <= 3:
                    print(f"journal: {type(e).__name__}: {e}", flush=True)

    def blob(self, text) -> str | None:
        if text is None:
            return None
        text = text if isinstance(text, str) else dumps(text)
        h = sha(text)
        self._x("INSERT OR IGNORE INTO blobs VALUES (?, ?)", (h, zlib.compress(text.encode(), 6)))
        return h

    def meta(self, key, value) -> None:
        self._x("INSERT OR REPLACE INTO meta VALUES (?, ?)", (key, dumps(value)))

    def start(self, spec, seed, responders, kind="start") -> None:
        """A run's inputs at its start: provenance, the frozen data, the resolved spec and seed; its first segment."""
        prov = provenance()
        self.meta("schema", SCHEMA)
        self.meta("provenance", prov)
        self.meta("spec", spec)
        self.meta("seed", seed)
        self.meta("log_format", "cybertron2 run directory: run.json, turns, days, perception, memory (jsonl), state.json, run.db")
        for name, table in frozen_tables().items():
            self._x("INSERT OR REPLACE INTO data VALUES (?, ?)", (name, dumps(table)))
        self._x("INSERT INTO segments (kind, first_step, code_sha, parent, responders) VALUES (?, ?, ?, ?, ?)",
                (kind, "d0.dawn", prov["code_sha"], None, dumps(responders)))

    def open_step(self, day, name) -> str:
        key = f"d{day}.{name}"
        if self.replaying:
            if key in self.committed:
                self.step, self.attempt, self.day, self.quiet = key, self.committed[key][0], day, True
                return key
            if self.strict:
                raise Paused(f"replayed to {key}: the record ends here")
            self.replaying, self.quiet = False, False                           # live from here: earlier open attempts aborted
            self._x("UPDATE steps SET status = 'aborted' WHERE status = 'open'")
            self._x("UPDATE segments SET first_step = ? WHERE id = (SELECT MAX(id) FROM segments)", (key,))
        with self.lock:
            row = self.db.execute("SELECT MAX(attempt) FROM steps WHERE step = ?", (key,)).fetchone()
            self.step, self.attempt, self.day = key, int(row[0] or 0) + 1, day
            self._x("INSERT INTO steps VALUES (?, ?, 'open', ?, NULL, NULL)", (key, self.attempt, time.time()))
        return key

    def commit(self, state, runner=None) -> None:
        """The step's checkpoint (the whole world state and the runner's own) and its commit, in one transaction (execution.md)."""
        if self.quiet:                                                        # a committed step played again: check it
            self.checked += 1
            rec = checkpoint(self.path, self.step, self.committed[self.step][0], conn=self.db, lock=self.lock)
            now = json.loads(dumps(state))
            if rec is None or dumps(rec["world"]) != dumps(now):
                self.mismatches.append({"step": self.step, "what": "world state",
                                        "paths": differences(rec["world"], now)[:8] if rec else []})
            if self.after_commit:
                self.after_commit(self.step)
            if self.until == self.step:
                raise Paused(f"paused after {self.step}")
            return
        text = dumps({"world": state, "runner": runner or {}})
        h = sha(text)
        with self.lock:
            try:
                self.db.execute("BEGIN")
                self.db.execute("INSERT OR REPLACE INTO checkpoints VALUES (?, ?, ?, ?)",
                                (self.step, self.attempt, h, zlib.compress(text.encode(), 6)))
                self.db.execute("UPDATE steps SET status = 'committed', ended = ?, checkpoint = ? WHERE step = ? AND attempt = ?",
                                (time.time(), h, self.step, self.attempt))
                self.db.execute("COMMIT")
            except sqlite3.Error as e:
                self.db.execute("ROLLBACK") if self.db.in_transaction else None
                self.failures += 1
                print(f"journal: commit {self.step}: {e}", flush=True)
        if self.after_commit:
            self.after_commit(self.step)
        if self.until == self.step:
            raise Paused(f"paused after {self.step}")

    def request_key(self, agent) -> str:
        with self.lock:
            k = (self.step, agent)
            self.counts[k] = self.counts.get(k, 0) + 1
            return f"{self.step}.{agent}.{self.counts[k]}"

    def request(self, key, agent, kind, conversation, index, system, schema, message, responder) -> None:
        if self.quiet:
            return
        self._x("INSERT OR REPLACE INTO requests VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (key, self.step, self.attempt, agent, kind, conversation, index, self.blob(system), self.blob(schema),
                 self.blob(str(message)), responder))

    def response(self, key, attempts, parsed, thinking, usage, transport) -> None:
        if self.quiet:
            return
        tries = [{"raw": a.get("raw"), "error": a.get("error"), "latency": a.get("latency_s")} for a in (attempts or [])]
        self._x("INSERT OR REPLACE INTO responses VALUES (?, ?, ?, ?, ?, ?)",
                (key, dumps(tries), dumps(parsed), thinking, dumps(usage or {}), transport))

    def event(self, e: dict, cause=None) -> None:
        if self.quiet:
            return
        extra = {k: v for k, v in e.items() if k not in EVENT_COLS}
        self._x("INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (e["id"], e["day"], self.step, self.attempt, e["place"], e["kind"], e.get("actor"), e.get("target"),
                 dumps(e.get("about") or []), dumps(e.get("concerns") or []), e.get("text"), dumps(cause), dumps(extra)))

    def change(self, call: dict, result) -> None:
        if self.quiet:
            return
        self._x("INSERT INTO changes (day, step, attempt, primitive, place, arguments, cause, result) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (call["day"], self.step, self.attempt, call["prim"], call["place"], dumps(call["kw"]), dumps(call["cause"]),
                 dumps(result)))

    def close(self) -> None:
        with self.lock:
            self.meta("journal_failures", self.failures)
            self.db.close()


def differences(a, b, path="") -> list:
    """Where two JSON values differ: paths, for a replay's report."""
    if type(a) is not type(b):
        return [path or "/"]
    if isinstance(a, dict):
        out = []
        for k in sorted(set(a) | set(b), key=str):
            out += [f"{path}/{k}"] if (k not in a or k not in b) else differences(a[k], b[k], f"{path}/{k}")
        return out
    if isinstance(a, list):
        if len(a) != len(b):
            return [f"{path} (length {len(a)} vs {len(b)})"]
        return [p for i, (x, y) in enumerate(zip(a, b)) for p in differences(x, y, f"{path}[{i}]")]
    return [] if a == b else [path]


# ---------------------------------------------------------------------- reading (for tests and the views to come, R5)
def read(path, sql, args=()) -> list:
    db = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        return db.execute(sql, args).fetchall()
    finally:
        db.close()


def unblob(path, h) -> str | None:
    rows = read(path, "SELECT z FROM blobs WHERE sha = ?", (h,))
    return zlib.decompress(rows[0][0]).decode() if rows else None


def unslim(x, path):
    """The runner's state with its blob references ({"$blob": sha}) read back."""
    if isinstance(x, dict):
        if set(x) == {"$blob"}:
            return unblob(path, x["$blob"])
        return {k: unslim(v, path) for k, v in x.items()}
    if isinstance(x, list):
        return [unslim(v, path) for v in x]
    return x


def checkpoint(path, step, attempt=None, conn=None, lock=None) -> dict:
    sql = "SELECT z FROM checkpoints WHERE step = ? " + ("AND attempt = ?" if attempt else "ORDER BY attempt DESC LIMIT 1")
    args = (step, attempt) if attempt else (step,)
    if conn is not None:
        with lock:
            rows = conn.execute(sql, args).fetchall()
    else:
        rows = read(path, sql, args)
    return json.loads(zlib.decompress(rows[0][0]).decode()) if rows else None
