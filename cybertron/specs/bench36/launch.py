"""Run the first batch (review 36b §8): live runs from manifest.json, a few at a time, resumed until complete.

    LLM_BACKEND=claude_code python cybertron/specs/bench36/launch.py [--max-runs 4] [--stop-launch 13:30] [--deadline 14:00]
                                                                    [--weekly-budget 0.27] [--only L3,L4]

Each run is `python -m cybertron run <spec> --seed 1 --sandbox off [--apply <id>_iv.yaml]` without --fresh, so a rerun of the same
spec resumes its stable directory. A run that stops early (usage limit, a crash) is retried after a pause. New runs are launched
in the manifest's priority order while the weekly subscription window has risen less than --weekly-budget since the launcher
started and before --stop-launch (UTC); at --deadline running runs are stopped (they stay resumable). State: cybertron/out/bench36/
state.json; logs: cybertron/out/bench36/logs/<id>.log."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import re
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
OUTD = ROOT / "cybertron" / "out" / "bench36"
STATE = OUTD / "state.json"
PRIORITY = ["L3", "L4", "L5", "L1", "L2", "M1o", "M1s", "M1h", "N1", "M3o", "M3s", "M3h", "N3", "M2o", "M2s", "M2h", "N2"] + \
           [f"T{i}" for i in range(1, 19)]


def now():
    return dt.datetime.now(dt.timezone.utc)


def at_utc(hhmm):
    h, m = map(int, hhmm.split(":"))
    return now().replace(hour=h, minute=m, second=0, microsecond=0)


def usage():
    """The subscription windows' utilization from one tiny Haiku call ({} if unknown)."""
    try:
        out = subprocess.run(["claude", "-p", "ok", "--model", "claude-haiku-5-5", "--output-format", "stream-json", "--verbose"],
                             capture_output=True, text=True, timeout=120).stdout
        for line in out.splitlines():
            if '"rate_limit_event"' in line:
                info = json.loads(line)["rate_limit_info"]
                return {n: w["utilization"] for n, w in info.get("unifiedWindows", {}).items()} | {"status": info.get("status")}
    except Exception as e:                                             # noqa: BLE001
        print("usage check failed:", e, flush=True)
    return {}


def load_state():
    return json.loads(STATE.read_text()) if STATE.exists() else {"runs": {}, "started": now().isoformat()}


def save_state(st):
    STATE.write_text(json.dumps(st, indent=1))


def complete(run_dir):
    return bool(run_dir) and (pathlib.Path(run_dir) / "summary.json").exists()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-runs", type=int, default=4)
    ap.add_argument("--stop-launch", default="13:30")
    ap.add_argument("--deadline", default="14:00")
    ap.add_argument("--weekly-budget", type=float, default=0.27)
    ap.add_argument("--only", default="")
    ap.add_argument("--usage-stop", default="0.85")
    a = ap.parse_args()
    (OUTD / "logs").mkdir(parents=True, exist_ok=True)
    st = load_state()
    u0 = usage()
    st.setdefault("weekly_at_start", u0.get("seven_day"))
    save_state(st)
    print("start usage", u0, flush=True)
    env = dict(os.environ, LLM_BACKEND=os.environ.get("LLM_BACKEND", "claude_code"), CYBERTRON_USAGE_STOP=a.usage_stop)
    procs: dict = {}
    only = set(x for x in a.only.split(",") if x)
    last_usage, cur = 0.0, u0
    while True:
        manifest = {r["id"]: r for r in json.loads((HERE / "manifest.json").read_text())}
        order = [i for i in PRIORITY if i in manifest and (not only or i in only)]
        for rid, p in list(procs.items()):                            # reap
            if p.poll() is None:
                continue
            rec = st["runs"][rid]
            log = (OUTD / "logs" / f"{rid}.log").read_text(errors="replace")
            m = re.findall(r"run dir: (\S+)", log)
            if m:
                rec["dir"] = m[-1]
            rec["exit"] = p.returncode
            rec["status"] = "done" if complete(rec.get("dir")) else "stopped"
            rec["ended"] = now().isoformat()
            if rec["status"] != "done":
                rec["retry_after"] = (now() + dt.timedelta(minutes=10 if "usage" not in log[-3000:] else 20)).isoformat()
            print(now().strftime("%H:%M"), rid, rec["status"], "exit", p.returncode, flush=True)
            del procs[rid]
            save_state(st)
        if now() >= at_utc(a.deadline):
            for rid, p in procs.items():
                p.terminate()
                st["runs"][rid]["status"] = "stopped at deadline"
            save_state(st)
            print("deadline: stopped", list(procs), flush=True)
            return
        if time.time() - last_usage > 600:
            cur = usage() or cur
            last_usage = time.time()
            st["usage_now"] = cur
            save_state(st)
        w0 = st.get("weekly_at_start") or 0
        over_budget = cur.get("seven_day") is not None and cur["seven_day"] - w0 >= a.weekly_budget
        hot = (cur.get("five_hour") or 0) >= float(a.usage_stop) or cur.get("status") not in (None, "allowed", "allowed_warning")
        may_launch = now() < at_utc(a.stop_launch) and not over_budget and not hot
        pending = [i for i in order if st["runs"].get(i, {}).get("status") != "done" and i not in procs]
        if may_launch:
            for rid in pending:
                if len(procs) >= a.max_runs:
                    break
                rec = st["runs"].setdefault(rid, {"attempts": 0})
                ra = rec.get("retry_after")
                if ra and dt.datetime.fromisoformat(ra) > now():
                    continue
                r = manifest[rid]
                cmd = [sys.executable, "-m", "cybertron", "run", r["spec"], "--seed", "1", "--sandbox", "off"]
                if r.get("apply"):
                    cmd += ["--apply", r["apply"]]
                rec["attempts"] += 1
                rec["status"] = "running"
                rec["started"] = now().isoformat()
                logf = open(OUTD / "logs" / f"{rid}.log", "a")
                logf.write(f"\n=== attempt {rec['attempts']} at {rec['started']}: {' '.join(cmd)}\n")
                logf.flush()
                procs[rid] = subprocess.Popen(cmd, cwd=ROOT, env=env, stdout=logf, stderr=subprocess.STDOUT)
                print(now().strftime("%H:%M"), "launched", rid, "attempt", rec["attempts"], flush=True)
                save_state(st)
        if not procs and not pending:
            print("all runs done", flush=True)
            return
        if not procs and not may_launch and (over_budget or now() >= at_utc(a.stop_launch)):
            print("nothing running and no more launches allowed", {"over_budget": over_budget}, flush=True)
            return
        time.sleep(30)


if __name__ == "__main__":
    main()
