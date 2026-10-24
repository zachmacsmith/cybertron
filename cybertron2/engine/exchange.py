"""Export, publish, import and fetch a run (spec/record/exchange.md, D1-1, D1-3, D1-4, D1-5; R5 of proposals/run_record.md).

    export RUN... --out DIR          DIR/<run>/journal/<table>.parquet (lossless, one to one with run.db), views/<table>.parquet
                                     (for analysis and a site), manifest.json (row counts and checksums), run.json
    import DIR --out RUN             rebuilds run.db exactly from the journal tables (checked against the manifest)
    publish RUN... [--push]          stages the export under experimental/cybertron2/ with the dataset card, through the privacy
                                     gate (this machine's session, container, account and organisation ids and the account email
                                     replaced, then every text and every compressed blob scanned); uploads only with --push
    fetch RUN_ID [--revision R] --out RUN   downloads a published run (pinned to a dataset revision) and imports it

Export, import and replay reproduce the run byte for byte (tests/test_cybertron2_exchange.py).
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import time
import zlib
from pathlib import Path

from cybertron2.engine import journal as JN, views as VW

FOLDER = "experimental/cybertron2"
SQL_TYPES = {"TEXT": "string", "INTEGER": "int64", "REAL": "float64", "BLOB": "binary"}
ID_VARS = ("CLAUDE_CODE_SESSION_ID", "CLAUDE_CODE_REMOTE_SESSION_ID", "CLAUDE_CODE_CONTAINER_ID", "CLAUDE_CODE_ACCOUNT_UUID",
           "CLAUDE_CODE_ORGANIZATION_UUID", "CLAUDE_CODE_USER_EMAIL")
COMPRESSED = {("blobs", "z"), ("checkpoints", "z")}


def _pa():
    import pyarrow as pa
    import pyarrow.parquet as pq
    return pa, pq


def _sha(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _redactor(strings):
    strings = [s for s in strings if s and len(s) >= 6]

    def red(v):
        if not strings:
            return v
        if isinstance(v, str):
            for s in strings:
                v = v.replace(s, "<redacted>")
            return v
        return v
    return red


# ---------------------------------------------------------------------- export
def export(run, out, redact=()) -> Path:
    """A run's journal tables (lossless) and view tables, as Parquet, with a manifest."""
    pa, pq = _pa()
    run, out = Path(run), Path(out)
    dst = out / run.name
    if dst.exists():
        shutil.rmtree(dst)
    (dst / "journal").mkdir(parents=True)
    (dst / "views").mkdir()
    db = sqlite3.connect(str(run / "run.db"))
    db.execute("PRAGMA wal_checkpoint(FULL)")
    red = _redactor(redact)
    manifest = {"schema": JN.SCHEMA, "run": run.name, "exported": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "redacted": bool([s for s in redact if s]), "journal": {}, "views": {}}
    for table in JN.TABLES:
        cols = [(c[1], c[2].split()[0].upper() if c[2] else "TEXT") for c in db.execute(f"PRAGMA table_info({table})").fetchall()]
        rows = db.execute(f"SELECT {', '.join(c for c, _ in cols)} FROM {table} ORDER BY rowid").fetchall()
        data = {}
        for i, (c, t) in enumerate(cols):
            vals = [r[i] for r in rows]
            if (table, c) in COMPRESSED and redact:
                vals = [zlib.compress(red(zlib.decompress(v).decode()).encode(), 6) if v is not None else None for v in vals]
            elif t == "TEXT":
                vals = [red(v) for v in vals]
            data[c] = pa.array(vals, type=getattr(pa, SQL_TYPES.get(t, "string"))())
        f = dst / "journal" / f"{table}.parquet"
        pq.write_table(pa.table(data), f)
        manifest["journal"][table] = {"rows": len(rows), "columns": [c for c, _ in cols], "types": [t for _, t in cols], "sha256": _sha(f)}
    db.close()
    for name, rows in view_tables(run).items():
        f = dst / "views" / f"{name}.parquet"
        rows = [{k: (json.dumps(v) if isinstance(v, (dict, list)) else (red(v) if isinstance(v, str) else v)) for k, v in r.items()}
                for r in rows]
        pq.write_table(pa.Table.from_pylist(rows) if rows else pa.table({}), f)
        manifest["views"][name] = {"rows": len(rows), "sha256": _sha(f)}
    if (run / "run.json").exists():
        (dst / "run.json").write_text(red((run / "run.json").read_text()))
    (dst / "manifest.json").write_text(json.dumps(manifest, indent=1))
    return dst


def view_tables(run) -> dict:
    """The tables for analysis and a site, from the journal (regenerable): one row a day from each day's last checkpoint."""
    people, holdings, buildings, parcels, claims, messages = [], [], [], [], [], []
    for step in [s["step"] for s in VW.steps(run) if s["step"].endswith(".memory")]:
        day = int(step.split(".")[0][1:])
        cp = JN.checkpoint(Path(run) / "run.db", step)
        w = cp["world"]
        hh = {m: h for h, i in w["institutions"].items() for m in (i.get("members") or [])}
        for n, a in w["people"].items():
            people.append({"day": day, "name": n, "alive": a.get("alive"), "stage": a.get("stage"), "sex": a.get("sex"),
                           "household": hh.get(n), "at": a.get("at"), "road": (a.get("transit") or {}).get("road"),
                           "hunger": a.get("hunger"), "model": a.get("model"), "pregnant": a.get("pregnant") is not None,
                           "partner": a.get("partner")})
        for cid, c in w["containers"].items():
            for item, q in (c.get("goods") or {}).items():
                if q > 1e-9:
                    holdings.append({"day": day, "container": cid, "kind": c.get("kind"), "of": c.get("of"), "item": item, "qty": q})
        for bid, b in w["buildings"].items():
            buildings.append({"day": day, "id": bid, "name": b.get("name"), "node": b.get("node"), "parcel": b.get("parcel"),
                              "structure": b.get("structure"), "size": b.get("size"), "condition": b.get("condition"),
                              "fire": b.get("fire"), "warm": b.get("warm"), "fittings": b.get("fittings")})
        for pid, p in w["parcels"].items():
            parcels.append({"day": day, "id": pid, "node": p.get("node"), "cover": p.get("cover"), "size": p.get("size"),
                            "crop": (p.get("crop") or {}).get("kind"), "fertility": p.get("fertility"),
                            "res": {k: r.get("S") for k, r in (p.get("res") or {}).items()}})
        for cl in (w.get("claims") or {}).values():
            claims.append({"day": day, "thing": cl.get("thing"), "claimant": cl.get("claimant"), "rights": cl.get("rights"),
                           "grounds": cl.get("grounds"), "until": cl.get("until")})
        res = JN.unslim(((cp.get("runner") or {}).get("carry") or {}).get("results") or {}, Path(run) / "run.db")
        for who, lines in res.items():
            for line in lines:
                if line.startswith("You told "):
                    to, text = line[len("You told "):].split(":", 1)
                    messages.append({"day": day, "from": who, "to": to, "where": "private", "text": text.strip()})
                elif line.startswith("You said ("):
                    where, text = line[len("You said ("):].split("):", 1)
                    messages.append({"day": day, "from": who, "to": None, "where": where, "text": text.strip()})
    return {"people_days": people, "holdings": holdings, "buildings": buildings, "parcels": parcels, "claims": claims,
            "messages": messages, "calls": VW.calls(run), "layout": VW.layout(run), "frames": VW.frames(run)}


# ---------------------------------------------------------------------- import
def import_(src, out) -> Path:
    """run.db rebuilt exactly from exported journal tables (each file checked against the manifest first)."""
    _, pq = _pa()
    src, out = Path(src), Path(out)
    man = json.loads((src / "manifest.json").read_text())
    for table, m in man["journal"].items():
        if _sha(src / "journal" / f"{table}.parquet") != m["sha256"]:
            raise SystemExit(f"{table}.parquet does not match its manifest")
    out.mkdir(parents=True, exist_ok=True)
    for f in ("run.db", "run.db-wal", "run.db-shm"):
        (out / f).unlink(missing_ok=True)
    JN.Journal(out / "run.db").db.close()                                      # the tables, empty
    db = sqlite3.connect(str(out / "run.db"))
    for table, m in man["journal"].items():
        t = pq.read_table(src / "journal" / f"{table}.parquet").to_pydict()
        cols = m["columns"]
        rows = list(zip(*[t[c] for c in cols])) if cols and t else []
        db.executemany(f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join('?' * len(cols))})", rows)
        if len(rows) != m["rows"]:
            raise SystemExit(f"{table}: {len(rows)} rows, the manifest says {m['rows']}")
    db.commit()
    db.close()
    if (src / "run.json").exists():
        shutil.copy(src / "run.json", out / "run.json")
    return out


# ---------------------------------------------------------------------- publish and fetch
def _private() -> list:
    return [v for v in (os.environ.get(x, "") for x in ID_VARS) if len(v) >= 6]


def scan(root, strings) -> list:
    """The privacy gate for Parquet: every text value and every compressed blob read back and searched."""
    _, pq = _pa()
    hits = []
    for f in Path(root).rglob("*"):
        if not f.is_file():
            continue
        if f.suffix == ".parquet":
            t = pq.read_table(f).to_pydict()
            for col, vals in t.items():
                for v in vals:
                    if isinstance(v, bytes):
                        try:
                            v = zlib.decompress(v).decode()
                        except Exception:
                            continue
                    if isinstance(v, str) and any(s in v for s in strings):
                        hits.append(f"{f}:{col}")
                        break
        else:
            text = f.read_text(errors="ignore")
            if any(s in text for s in strings):
                hits.append(str(f))
    return hits


def publish(runs, staging=None, push=False, repo=None) -> Path:
    from cybertron2 import publish_hf as LEGACY
    staging = Path(staging or f"cybertron/out/_publish/cybertron2_{time.strftime('%Y%m%dT%H%M%S', time.gmtime())}")
    root = staging / FOLDER
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    private = _private()
    rows = []
    for r in map(Path, runs):
        if (r / "run.db").exists():
            export(r, root, redact=private)
        else:                                                                    # a run from before the journal: its files
            (root / r.name).mkdir()
            for f in LEGACY.FILES:
                if (r / f).exists():
                    text = (r / f).read_text()
                    for s in private:
                        text = text.replace(s, "<redacted>")
                    (root / r.name / f).write_text(text)
        spec = json.loads((r / "run.json").read_text())["spec"] if (r / "run.json").exists() else {}
        days = [json.loads(x) for x in (r / "days.jsonl").read_text().splitlines()] if (r / "days.jsonl").exists() else []
        rows.append(f"| {r.name} | `{spec.get('name')}` | {len(spec.get('agents') or {})} | {len(days)} | "
                    f"${(days[-1].get('cost_usd', 0.0) if days else 0.0):.2f} | {LEGACY.SUMMARIES.get(r.name, '')} |")
    card = LEGACY.CARD.format(rows="\n".join(rows)) + """
## Runs with a journal (newer)

`<run>/journal/*.parquet` are the run's journal tables, one to one with its `run.db` (spec/record/journal.md): `python -m
cybertron2.engine fetch <run>` downloads and rebuilds it as a local run that can be replayed, viewed, forked and continued.
`<run>/views/*.parquet` are tables for analysis: people_days, holdings, buildings, parcels, claims, messages, calls, layout, frames.
"""
    (root / "README.md").write_text(card)
    hits = scan(root, private) if private else []
    if hits:
        raise SystemExit(f"privacy gate: private strings found in {hits[:5]}: nothing uploaded")
    if not push:
        return root
    if not os.environ.get("HF_TOKEN"):
        raise SystemExit("HF_TOKEN is not set: a token with write access to the dataset is needed to upload")
    from cybertron import publish as P
    from huggingface_hub import HfApi
    HfApi().upload_folder(repo_id=repo or P.default_repo(), repo_type="dataset", folder_path=str(staging),
                          allow_patterns=[f"{FOLDER}/**"], commit_message=f"experimental: cybertron2 runs ({', '.join(Path(r).name for r in runs)})")
    return root


def fetch(run_id, out, revision=None, repo=None) -> Path:
    """A published run, downloaded at a pinned revision of the dataset and imported."""
    from cybertron import publish as P
    from huggingface_hub import snapshot_download
    local = snapshot_download(repo_id=repo or P.default_repo(), repo_type="dataset", revision=revision,
                              allow_patterns=[f"{FOLDER}/{run_id}/journal/*", f"{FOLDER}/{run_id}/manifest.json", f"{FOLDER}/{run_id}/run.json"])
    return import_(Path(local) / FOLDER / run_id, out)
