"""The c2viz site: browse runs, local and published, and explore any of them as its days are built (c2viz/site/README.md).

    python -m c2viz.site.server [--runs DIR]... [--repo OWNER/NAME] [--folder PATH] [--revision REV] [--no-hub] [--cache DIR] [--port 8791]

Runs are run journals: a local folder with a `run.db` (found under each --runs directory, two levels deep), or a run published to a
Hugging Face dataset (`<folder>/<run>/journal/*.parquet` with its `manifest.json`, as `cybertron2.engine exchange publish` writes
them; the dataset and folder are settings, so a run moved to another dataset is one flag away). The visuals are the engine's: the
server builds each run's viz with c2viz.model (which replays every change through the engine), the head first and then one day at a
time, and caches each part on disk, keyed by the journal and by c2viz's own code, so a changed model builds afresh. The page streams
the days in as they are built, and a day can be explored as soon as it has come.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import threading
import time
import traceback
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

HERE = Path(__file__).resolve().parent
C2VIZ = HERE.parent


def code_key() -> str:
    """A hash of c2viz's own code (Python and the renderer): a cached part built by other code is built again."""
    h = hashlib.sha256()
    for p in sorted(list(C2VIZ.glob("*.py")) + list((C2VIZ / "js").glob("*"))):
        h.update(p.name.encode()); h.update(p.read_bytes())
    return h.hexdigest()[:12]


# ---------------------------------------------------------------------------------------------------- the runs
class Catalog:
    """Every run the site can show: local journals and the published ones (listed from the dataset, at one pinned revision)."""

    def __init__(self, roots, repo, folder, revision, hub, cache):
        self.roots, self.repo, self.folder, self.revision, self.hub, self.cache = [Path(r) for r in roots], repo, folder, revision, hub, cache
        self.sha, self.hub_runs, self.hub_error, self.hub_at = None, {}, None, 0.0
        self.lock = threading.Lock()

    def local(self) -> dict:
        out = {}
        for root in self.roots:
            for db in sorted(list(root.glob("*/run.db")) + list(root.glob("run.db")) + list(root.glob("*/*/run.db"))):
                run = db.parent
                rid = "local:" + (run.name if run != root else root.name)
                if rid in out:
                    rid = "local:" + str(run.relative_to(root.parent)).replace(os.sep, "/")
                out[rid] = {"id": rid, "source": "local", "path": str(run), **summary(run)}
        return out

    def hub_list(self) -> dict:
        """The published runs that have a journal, at one revision of the dataset (fetched again after ten minutes)."""
        if not self.hub:
            return {}
        with self.lock:
            if self.hub_runs is not None and time.time() - self.hub_at < 600 and self.hub_at:
                return self.hub_runs
            try:
                from huggingface_hub import HfApi
                api = HfApi()
                self.sha = api.dataset_info(self.repo, revision=self.revision).sha
                files = api.list_repo_files(self.repo, repo_type="dataset", revision=self.sha)
                pre = self.folder.rstrip("/") + "/"
                runs = {}
                for f in files:
                    if f.startswith(pre) and f.endswith("/manifest.json") and f.count("/") == pre.count("/") + 1:
                        name = f[len(pre):].split("/")[0]
                        if any(x.startswith(f"{pre}{name}/journal/") for x in files):
                            runs["hub:" + name] = {"id": "hub:" + name, "source": "hub", "name": name, "repo": self.repo,
                                                   "revision": self.sha, **self.hub_summary(name)}
                self.hub_runs, self.hub_error, self.hub_at = runs, None, time.time()
            except Exception as e:                                          # noqa: BLE001 (offline, no such dataset: local runs still)
                self.hub_runs, self.hub_error, self.hub_at = {}, f"{type(e).__name__}: {str(e)[:200]}", time.time()
            return self.hub_runs

    def hub_summary(self, name) -> dict:
        """What a published run says of itself (its run.json: the world's spec; its manifest: the journal's tables), cached by revision."""
        out = {}
        for fn in ("run.json", "manifest.json"):
            f = self.cache / "hub" / self.sha[:12] / name / fn
            if not f.exists():
                try:
                    from huggingface_hub import hf_hub_download
                    p = hf_hub_download(repo_id=self.repo, filename=f"{self.folder}/{name}/{fn}", repo_type="dataset", revision=self.sha)
                    f.parent.mkdir(parents=True, exist_ok=True)
                    f.write_bytes(Path(p).read_bytes())
                except Exception:                                           # noqa: BLE001
                    continue
            out[fn] = json.loads(f.read_text())
        spec = (out.get("run.json") or {}).get("spec") or {}
        steps = ((out.get("manifest.json") or {}).get("journal") or {}).get("steps", {}).get("rows")
        return {"title": spec.get("name") or name, "planned_days": spec.get("days"), "seed": spec.get("seed"), "people": len(spec.get("agents") or {}),
                "places": len(spec.get("nodes") or {}), "generated": bool((spec.get("generated") or {}).get("by")), "journal_steps": steps,
                "models": sorted({a.get("model") for a in (spec.get("agents") or {}).values() if a.get("model")})}

    def all(self) -> dict:
        return {**self.hub_list(), **self.local()}

    def path_of(self, rid) -> Path:
        """Where a run's journal is on this machine; a published run is fetched (at the pinned revision) and imported first."""
        runs = self.all()
        if rid not in runs:
            raise KeyError(rid)
        r = runs[rid]
        if r["source"] == "local":
            return Path(r["path"])
        out = self.cache / "hub" / r["revision"][:12] / r["name"] / "run"
        if not (out / "run.db").exists():
            from huggingface_hub import snapshot_download
            from c2viz import touch as E
            local = snapshot_download(repo_id=self.repo, repo_type="dataset", revision=r["revision"],
                                      allow_patterns=[f"{self.folder}/{r['name']}/journal/*", f"{self.folder}/{r['name']}/manifest.json",
                                                      f"{self.folder}/{r['name']}/run.json"])
            E.import_run(Path(local) / self.folder / r["name"], out)
        return out


def summary(run: Path) -> dict:
    """A local run's journal, briefly: its world, seed, days, people, whether it ended and whether it is a generated world."""
    import sqlite3
    try:
        con = sqlite3.connect(f"file:{run / 'run.db'}?mode=ro", uri=True)
        meta = dict(con.execute("SELECT key, value FROM meta"))
        days = con.execute("SELECT COUNT(*) FROM steps WHERE status = 'committed' AND step LIKE '%.memory'").fetchone()[0]
        con.close()
        spec = json.loads(meta.get("spec") or "{}")
        ended = json.loads(meta["ended"]) if meta.get("ended") else None
        models = sorted({a.get("model") for a in (spec.get("agents") or {}).values() if a.get("model")})
        return {"name": run.name, "title": spec.get("name") or run.name, "seed": json.loads(meta.get("seed") or "null"), "days": days,
                "people": len(spec.get("agents") or {}), "places": len(spec.get("nodes") or {}), "ended": ended,
                "generated": bool((spec.get("generated") or {}).get("by")), "models": models}
    except Exception as e:                                                  # noqa: BLE001
        return {"name": run.name, "title": run.name, "error": str(e)[:200]}


# ---------------------------------------------------------------------------------------------------- building a run's viz
class Builder:
    """A run's viz built in parts by c2viz.model, in order (the head, then day 0, 1, ...), each written to the cache when done."""

    def __init__(self, rid, path, cache):
        self.rid, self.path = rid, path
        db = path / "run.db"
        key = hashlib.sha256(f"{db.resolve()}|{db.stat().st_size}|{db.stat().st_mtime_ns}|{code_key()}".encode()).hexdigest()[:16]
        self.dir = cache / "viz" / key
        self.dir.mkdir(parents=True, exist_ok=True)
        self.cond = threading.Condition()
        self.error, self.total, self.thread = None, None, None

    def part(self, name) -> Path:
        return self.dir / f"{name}.json"

    def status(self) -> dict:
        built = sorted(int(p.stem[4:]) for p in self.dir.glob("day_*.json"))
        return {"id": self.rid, "head": self.part("head").exists(), "built": len(built), "total": self.total, "error": self.error}

    def start(self):
        with self.cond:
            if self.thread and self.thread.is_alive():
                return
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()

    def _run(self):
        try:
            from c2viz.model import RunModel
            RM = RunModel(self.path)
            self.total = len(RM.days)
            if not self.part("head").exists():
                head = RM.head()
                head["meta"]["days"] = self.total
                self._write("head", head)
            for d in RM.days:
                if not self.part(f"day_{d}").exists():
                    self._write(f"day_{d}", RM.day(d))
        except Exception as e:                                              # noqa: BLE001 (shown on the page)
            self.error = f"{type(e).__name__}: {e}"
            traceback.print_exc()
            with self.cond:
                self.cond.notify_all()

    def _write(self, name, obj):
        tmp = self.part(name).with_suffix(".tmp")
        tmp.write_text(json.dumps(obj, separators=(",", ":"), default=str))
        tmp.replace(self.part(name))
        with self.cond:
            self.cond.notify_all()

    def wait(self, name, timeout=600) -> Path | None:
        self.start()
        end = time.time() + timeout
        with self.cond:
            while not self.part(name).exists() and not self.error and time.time() < end:
                self.cond.wait(timeout=1.0)
        return self.part(name) if self.part(name).exists() else None


# ---------------------------------------------------------------------------------------------------- the server
class Site:
    def __init__(self, args):
        self.cache = Path(args.cache)
        self.catalog = Catalog(args.runs, args.repo, args.folder, args.revision, not args.no_hub, self.cache)
        self.builders, self.lock = {}, threading.Lock()
        self.fetching = {}
        from c2viz.build import bundle
        self.js = bundle().encode()

    def builder(self, rid) -> Builder:
        with self.lock:
            b = self.builders.get(rid)
            if b is None:
                self.fetching[rid] = True
        if b is None:
            try:
                path = self.catalog.path_of(rid)
            finally:
                self.fetching.pop(rid, None)
            with self.lock:
                b = self.builders.setdefault(rid, Builder(rid, path, self.cache))
        return b


def handler(site: Site):
    class H(SimpleHTTPRequestHandler):
        def log_message(self, fmt, *a):                                     # quiet: only errors
            if a and str(a[1]).startswith(("4", "5")):
                super().log_message(fmt, *a)

        def send(self, code, body: bytes, ctype="application/json", cache=False):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "max-age=31536000, immutable" if cache else "no-store")
            self.end_headers()
            self.wfile.write(body)

        def json(self, obj, code=200):
            self.send(code, json.dumps(obj, default=str).encode())

        def do_GET(self):
            u = urlparse(self.path)
            parts = [unquote(p) for p in u.path.strip("/").split("/") if p]
            try:
                if not parts or parts[0] in ("index.html",):
                    return self.send(200, (HERE / "index.html").read_bytes(), "text/html; charset=utf-8")
                if parts[0] == "run.html":
                    return self.send(200, (HERE / "run.html").read_bytes(), "text/html; charset=utf-8")
                if parts[0] == "c2pixel.js":
                    return self.send(200, site.js, "text/javascript; charset=utf-8")
                if parts[:2] == ["api", "runs"]:
                    runs = site.catalog.all()
                    for rid, r in runs.items():
                        b = site.builders.get(rid)
                        r["built"] = b.status() if b else None
                    return self.json({"runs": sorted(runs.values(), key=lambda r: (r["source"], r.get("title") or "")),
                                      "hub": {"repo": site.catalog.repo, "folder": site.catalog.folder, "revision": site.catalog.sha,
                                              "enabled": site.catalog.hub, "error": site.catalog.hub_error}})
                if parts[:2] == ["api", "run"] and len(parts) >= 4:
                    rid, what = parts[2], parts[3]
                    if what == "status":
                        b = site.builders.get(rid)
                        return self.json(b.status() if b else {"id": rid, "fetching": rid in site.fetching, "built": 0})
                    b = site.builder(rid)
                    name = "head" if what == "head" else f"day_{int(parts[4])}" if what == "day" and len(parts) > 4 else None
                    if name is None:
                        return self.json({"error": "unknown"}, 404)
                    f = b.wait(name)
                    if f is None:
                        return self.json({"error": b.error or "not built", "status": b.status()}, 500 if b.error else 404)
                    return self.send(200, f.read_bytes(), cache=True)
                return self.json({"error": "not found"}, 404)
            except KeyError:
                return self.json({"error": f"no run {parts[2] if len(parts) > 2 else ''}"}, 404)
            except Exception as e:                                          # noqa: BLE001
                traceback.print_exc()
                return self.json({"error": f"{type(e).__name__}: {e}"}, 500)
    return H


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--runs", action="append", default=[], help="a directory of run folders (each with run.db); may be given again")
    ap.add_argument("--repo", default=None, help="the Hugging Face dataset of published runs (default: the project's)")
    ap.add_argument("--folder", default=None, help="the folder in the dataset that holds the runs (default: the engine's)")
    ap.add_argument("--revision", default="main", help="the dataset revision to read; the page pins the commit it resolves to")
    ap.add_argument("--no-hub", action="store_true", help="local runs only")
    ap.add_argument("--cache", default=str(Path.home() / ".cache" / "c2viz-site"))
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8791)
    a = ap.parse_args(argv)
    from c2viz import touch as E
    a.repo = a.repo or os.environ.get("C2VIZ_REPO") or E.default_repo()
    a.folder = a.folder or os.environ.get("C2VIZ_FOLDER") or E.published_folder()
    a.runs = a.runs or [os.environ.get("C2VIZ_RUNS") or str(Path.cwd() / "runs")]
    site = Site(a)
    srv = ThreadingHTTPServer((a.host, a.port), handler(site))
    print(f"c2viz site on http://{a.host}:{a.port}  (local runs: {', '.join(a.runs)}; hub: {a.repo}/{a.folder}{'' if not a.no_hub else ' (off)'})", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
