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
}
EVENT_COLS = ("id", "day", "place", "kind", "actor", "target", "about", "concerns", "text")


def dumps(x) -> str:
    try:
        return json.dumps(x, sort_keys=True, default=_plain, separators=(",", ":"))
    except TypeError:                                                         # keys of mixed kinds (a YAML `on:` is True)
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
        with self.lock:
            row = self.db.execute("SELECT MAX(attempt) FROM steps WHERE step = ?", (key,)).fetchone()
            self.step, self.attempt, self.day = key, int(row[0] or 0) + 1, day
            self._x("INSERT INTO steps VALUES (?, ?, 'open', ?, NULL, NULL)", (key, self.attempt, time.time()))
        return key

    def commit(self, state, runner=None) -> None:
        """The step's checkpoint (the whole world state and the runner's own) and its commit, in one transaction (execution.md)."""
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

    def request_key(self, agent) -> str:
        with self.lock:
            k = (self.step, agent)
            self.counts[k] = self.counts.get(k, 0) + 1
            return f"{self.step}.{agent}.{self.counts[k]}"

    def request(self, key, agent, kind, conversation, index, system, schema, message, responder) -> None:
        self._x("INSERT OR REPLACE INTO requests VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (key, self.step, self.attempt, agent, kind, conversation, index, self.blob(system), self.blob(schema),
                 self.blob(str(message)), responder))

    def response(self, key, attempts, parsed, thinking, usage, transport) -> None:
        tries = [{"raw": a.get("raw"), "error": a.get("error"), "latency": a.get("latency_s")} for a in (attempts or [])]
        self._x("INSERT OR REPLACE INTO responses VALUES (?, ?, ?, ?, ?, ?)",
                (key, dumps(tries), dumps(parsed), thinking or None, dumps(usage or {}), transport))

    def event(self, e: dict, cause=None) -> None:
        extra = {k: v for k, v in e.items() if k not in EVENT_COLS}
        self._x("INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (e["id"], e["day"], self.step, self.attempt, e["place"], e["kind"], e.get("actor"), e.get("target"),
                 dumps(e.get("about") or []), dumps(e.get("concerns") or []), e.get("text"), dumps(cause), dumps(extra)))

    def change(self, call: dict, result) -> None:
        self._x("INSERT INTO changes (day, step, attempt, primitive, place, arguments, cause, result) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (call["day"], self.step, self.attempt, call["prim"], call["place"], dumps(call["kw"]), dumps(call["cause"]),
                 dumps(result)))

    def close(self) -> None:
        with self.lock:
            self.meta("journal_failures", self.failures)
            self.db.close()


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


def checkpoint(path, step, attempt=None) -> dict:
    sql = "SELECT z FROM checkpoints WHERE step = ? " + ("AND attempt = ?" if attempt else "ORDER BY attempt DESC LIMIT 1")
    rows = read(path, sql, (step, attempt) if attempt else (step,))
    return json.loads(zlib.decompress(rows[0][0]).decode()) if rows else None
