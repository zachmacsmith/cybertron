"""A person playing an agent (spec/record/human_play.md, D1-1, D1-4; R3): a thin layer on the journal, for a terminal, a web page or
any other front end.

    pending(run, agent=None)          the requests waiting for a person: [{key, agent, kind, step}]
    context(run, key)                 exactly what a model would be shown (views.context): system text, reply schema, the
                                      conversation so far, the new message
    answer(run, key, reply)           checks the reply against the schema and stores it as the answer
    advance(run, backend=None)        plays the run on (resume) until the next person's turn or its end; returns status(run)
    status(run)                       {"waiting": pending(run), "ended": bool, "at": last committed step}

`python -m cybertron2.engine play RUN --as NAME` answers in the terminal; `serve RUN [--port 8765]` gives the same over HTTP
(GET /status, GET /context/<key>, GET /verbs, POST /answer/<key> with the reply as JSON) and a page at / (play.html): what the
model would be shown on the left, and on the right a form built from the request's reply schema (a verb chosen from a list, its
own arguments as lists where the schema closes them, free text typed). `serve RUN --new WORLD --as NAME` starts a new run first.
"""
from __future__ import annotations

import json
import threading
from pathlib import Path
from urllib.parse import unquote

from cybertron2.engine import journal as JN, views as VW


def pending(run, agent=None) -> list:
    return [r for r in VW.requests(run, agent=agent, pending=True) if r["responder"] == "human"]


def context(run, key) -> dict:
    return VW.context(run, key)


def check(schema, reply) -> list:
    """What is wrong with a reply, by the reply schema (empty: nothing)."""
    if not isinstance(reply, dict):
        return ["the reply must be a JSON object"]
    try:
        import jsonschema
        v = jsonschema.Draft202012Validator(schema or {})
        return [f"{'/'.join(map(str, e.path)) or '(top)'}: {e.message}" for e in v.iter_errors(reply)]
    except ImportError:
        props = (schema or {}).get("properties") or {}
        return [f"unknown key {k!r}" for k in reply if props and k not in props]


def answer(run, key, reply) -> list:
    """Store a person's reply as the answer to `key`; returns the problems found instead, if any (nothing stored then)."""
    db = Path(run) / "run.db"
    row = JN.read(db, "SELECT responder, schema_sha FROM requests WHERE key = ?", (key,))
    if not row or row[0][0] != "human":
        return [f"no request {key} is waiting for a person"]
    if JN.read(db, "SELECT 1 FROM responses WHERE key = ?", (key,)):
        return [f"{key} is answered already"]
    schema = json.loads(JN.unblob(db, row[0][1])) if row[0][1] else None
    problems = check(schema, reply)
    if problems:
        return problems
    j = JN.Journal(db)
    j.response(key, [{"raw": json.dumps(reply), "error": None, "latency": None}], reply, None, {}, "human")
    j.db.close()
    return []


def status(run) -> dict:
    db = Path(run) / "run.db"
    meta = dict(JN.read(db, "SELECT key, value FROM meta"))
    return {"waiting": pending(run), "ended": "ended" in meta and not pending(run), "at": VW.last_step(run),
            "stopped": (Path(run) / "STOPPED.md").read_text() if (Path(run) / "STOPPED.md").exists() else None}


def advance(run, backend=None, workers=12) -> dict:
    """Play on from the record (every answer reused) until a person's turn comes again or the run ends."""
    from cybertron2.engine import run as R
    R.run(None, run, backend, workers=workers, mode="resume")
    return status(run)


# ---------------------------------------------------------------------- the terminal
def play(run, agent, backend=None) -> None:
    run = Path(run)
    while True:
        waiting = pending(run, agent)
        if not waiting:
            st = advance(run, backend)
            if st["ended"]:
                print("The run has ended.")
                return
            if not pending(run, agent):
                print(f"Nothing for {agent} now; waiting on: {[w['agent'] for w in st['waiting']] or 'nobody'}")
                return
            continue
        req = waiting[0]
        ctx = context(run, req["key"])
        if not ctx["turns"]:
            print("=" * 80 + "\n" + ctx["system"] + "\n" + "=" * 80)
        print(ctx["message"])
        print(f"\n[{req['key']}] Your reply as JSON (end with an empty line). The schema's keys: "
              f"{', '.join((ctx['schema'] or {}).get('properties', {}))}")
        while True:
            lines = []
            while (line := input()) != "":
                lines.append(line)
            try:
                problems = answer(run, req["key"], json.loads("\n".join(lines) or "{}"))
            except json.JSONDecodeError as e:
                problems = [f"not JSON: {e}"]
            if not problems:
                break
            print("Refused: " + "; ".join(problems[:5]) + "\nTry again:")


# ---------------------------------------------------------------------- HTTP, for a web page or anything else
PAGE = Path(__file__).with_name("play.html")


def verbs() -> dict:
    """The verbs' arguments from the registry, for a front end's form: {verb: {args, doc, fields: [[name, optional]]}}."""
    import re
    from cybertron2.engine import verbs as V
    return {v: {"args": d["args"], "doc": d["doc"].replace(": {crafts}", "").replace("{crafts}", ""),
                "fields": [[m.group(1), bool(m.group(2))] for m in re.finditer(r'"([^"]+)"(\?)?', d["args"])]}
            for v, d in V.VERB.items()}


def serve(run, port=8765, backend=None, new=None, agent=None, days=None, bots=False) -> None:
    """Serve the run over HTTP. With `new` (a world file) and `agent`, first start the run with that person played by a person."""
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    run = Path(run)
    lock = threading.Lock()

    def go_on():
        with lock:
            advance(run, backend)

    def start():
        from cybertron2.engine import run as R
        with lock:
            R.run(new, run, backend, days, bots=bots, responders={agent: "human"})

    if new:
        if (run / "run.db").exists():
            raise SystemExit(f"{run} exists already: serve it without --new, or choose another directory")
        threading.Thread(target=start, daemon=True).start()

    class H(BaseHTTPRequestHandler):
        def _send(self, obj, code=200, ctype="application/json"):
            body = obj.encode() if isinstance(obj, str) else json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = self.path.split("?")[0]
            if path in ("/", "/index.html"):
                return self._send(PAGE.read_text(), ctype="text/html; charset=utf-8")
            if path == "/verbs":
                return self._send(verbs())
            if path == "/status":
                if not (run / "run.db").exists():
                    return self._send({"waiting": [], "ended": False, "at": None, "stopped": None, "advancing": True})
                return self._send({**status(run), "advancing": lock.locked()})
            if path.startswith("/context/"):
                try:
                    return self._send(context(run, unquote(path[len("/context/"):])))
                except KeyError as e:
                    return self._send({"error": str(e)}, 404)
            self._send({"error": "not found"}, 404)

        def do_POST(self):
            if not self.path.startswith("/answer/"):
                return self._send({"error": "not found"}, 404)
            n = int(self.headers.get("Content-Length") or 0)
            try:
                reply = json.loads(self.rfile.read(n) or b"{}")
            except json.JSONDecodeError as e:
                return self._send({"problems": [f"not JSON: {e}"]}, 400)
            problems = answer(run, unquote(self.path[len("/answer/"):]), reply)
            if not problems and not pending(run):
                threading.Thread(target=go_on, daemon=True).start()         # everyone has answered: the run goes on
            self._send({"problems": problems}, 400 if problems else 200)

        def log_message(self, *a):
            pass

    print(f"serving {run} on http://127.0.0.1:{port}/" + (f"?as={agent}" if agent else ""), flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
