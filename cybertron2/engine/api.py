"""A person playing an agent (spec/record/human_play.md, D1-1, D1-4; R3): a thin layer on the journal, for a terminal, a web page or
any other front end.

    pending(run, agent=None)          the requests waiting for a person: [{key, agent, kind, step}]
    context(run, key)                 exactly what a model would be shown (views.context): system text, reply schema, the
                                      conversation so far, the new message
    answer(run, key, reply)           checks the reply against the schema and stores it as the answer
    advance(run, backend=None)        plays the run on (resume) until the next person's turn or its end; returns status(run)
    status(run)                       {"waiting": pending(run), "ended": bool, "at": last committed step}

`python -m cybertron2.engine play RUN --as NAME` answers in the terminal; `serve RUN [--port 8765]` gives the same over HTTP
(GET /status, GET /context/<key>, POST /answer/<key> with the reply as JSON) and a bare page at / to try it.
"""
from __future__ import annotations

import json
import threading
from pathlib import Path

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
PAGE = """<!doctype html><meta charset=utf-8><title>cybertron2: play</title>
<style>body{font:15px system-ui;max-width:900px;margin:2em auto;padding:0 1em}pre{white-space:pre-wrap;background:#f4f4f4;padding:1em}
textarea{width:100%;height:12em;font:13px monospace}</style>
<h1>Play an agent</h1><div id=s>loading...</div>
<script>
async function load(){const st=await (await fetch('status')).json();const d=document.getElementById('s');
 if(!st.waiting.length){d.innerHTML='<p>'+(st.ended?'The run has ended.':'Nobody is waiting for a person. At '+st.at+'.')+'</p>';return}
 const k=st.waiting[0].key;const c=await (await fetch('context/'+k)).json();
 d.innerHTML='<h2>'+c.agent+' &middot; '+k+'</h2><details><summary>System text</summary><pre></pre></details>'
  +c.turns.map(t=>'<details><summary>Earlier: '+t.key+'</summary><pre></pre><pre></pre></details>').join('')
  +'<pre id=m></pre><p>Your reply (JSON; keys: '+Object.keys((c.schema||{}).properties||{}).join(', ')+')</p>'
  +'<textarea id=r>{"why": "", "actions": []}</textarea><p><button id=b>Answer</button> <span id=e></span></p>';
 const pres=d.querySelectorAll('pre');pres[0].textContent=c.system;let i=1;
 for(const t of c.turns){pres[i++].textContent=t.message;pres[i++].textContent=t.reply}
 document.getElementById('m').textContent=c.message;
 document.getElementById('b').onclick=async()=>{let body;try{body=JSON.parse(document.getElementById('r').value)}catch(x){
  document.getElementById('e').textContent='not JSON';return}
  const res=await (await fetch('answer/'+k,{method:'POST',body:JSON.stringify(body)})).json();
  if(res.problems&&res.problems.length){document.getElementById('e').textContent=res.problems.join('; ');return}
  d.innerHTML='<p>Answered; the run is going on...</p>';setTimeout(load,1500)}}
load()
</script>"""


def serve(run, port=8765, backend=None) -> None:
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    run = Path(run)
    lock = threading.Lock()

    def go_on():
        with lock:
            advance(run, backend)

    class H(BaseHTTPRequestHandler):
        def _send(self, obj, code=200, ctype="application/json"):
            body = obj.encode() if isinstance(obj, str) else json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                return self._send(PAGE, ctype="text/html; charset=utf-8")
            if self.path == "/status":
                return self._send({**status(run), "advancing": lock.locked()})
            if self.path.startswith("/context/"):
                try:
                    return self._send(context(run, self.path[len("/context/"):]))
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
            problems = answer(run, self.path[len("/answer/"):], reply)
            if not problems and not pending(run):
                threading.Thread(target=go_on, daemon=True).start()         # everyone has answered: the run goes on
            self._send({"problems": problems}, 400 if problems else 200)

        def log_message(self, *a):
            pass

    print(f"serving {run} on http://127.0.0.1:{port}/", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
