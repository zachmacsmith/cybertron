"""Live test of the rewritten memory (cybertron2/engine/memory.py; review 38.36): real agents' stretches from the Wide Country run w1
(days 0 to 23), played to a model with the memory section rewritten each stretch under each prompt variant.

    PYTHONPATH=. python3 docs/review/38_space_engine/36_memory_rewrite.py --model claude-sonnet-5-5 --agents Lucy Jory Gunnild Gilbert \
        --variants plain keep_change most_days future_self --out /tmp/mem.json

Each stretch is the agent's own conversation as it was (its day prompts, talk prompts and replies), with the opening's memory
sections replaced by the memory it has rewritten so far (the engine's own list of marked events left out, as in rewrite mode), then
the end-of-stretch request with the variant's instruction. Only memory calls are made.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import re
import sys
from pathlib import Path

from cybertron2.engine import memory as M

RUN = Path("runs/w1_wide")
SPEC = Path("cybertron2/specs/wide_s7.yaml")
LAST_DAY = 23                                                              # before the usage limit (review 38.31)
SCHEMA = {"type": "object", "properties": {"memory": {"type": "string"}}, "required": ["memory"]}
LASTING = re.compile(r"^- (spring|summer|autumn|winter) day \d+: ")


def stretches(agent):
    turns = [json.loads(l) for l in open(RUN / "turns.jsonl")]
    mems = [json.loads(l) for l in open(RUN / "memory.jsonl")]
    mine = {t["day"]: t for t in turns if t.get("agent") == agent and not t.get("on_road")}
    ends = sorted(m["day"] for m in mems if m["agent"] == agent and m["day"] <= LAST_DAY)
    out, start = [], 0
    for end in ends:
        days = [mine[d] for d in range(start, end + 1) if d in mine]
        mem = next(m for m in mems if m["agent"] == agent and m["day"] == end)
        if days:
            out.append({"start": start, "end": end, "days": days, "span": mem["span"],
                        "close": mem["prompt"].split("This is the end of a stretch")[0].strip()})
        start = end + 1
    return out


def opening(text, memory):
    """The stretch's opening with its memory sections as rewrite mode would show them."""
    text = re.sub(r"## Your own memory of recent days \(written by you\)\n.*?(?=\n## )", "", text, flags=re.S)
    lines = [l for l in text.split("\n") if not LASTING.match(l)]
    text = "\n".join(lines)
    if memory:
        text = text.replace("## Now\n", f"## Your memory (in your own words)\n{memory}\n\n## Now\n", 1)
    return text


def conversation(st, memory):
    msgs = []
    for i, t in enumerate(st["days"]):
        prompt = t["prompt"]
        if i == 0:
            prompt = opening(prompt, memory)
        msgs += [prompt, json.dumps(t.get("reply") or {})]
        for x in t.get("talk") or []:
            if x.get("prompt") and x.get("wave") != "fuse":
                msgs += [x["prompt"], json.dumps(x.get("reply") or {})]
    return msgs


def play(agent, variant, model, backend, system, born, lifespan, lo=M.DEFAULTS["lo"], hi=M.DEFAULTS["hi"], growth=False):
    from cybertron import llm
    memory, log, last = "", [], None
    for st in stretches(agent):
        b = M.budget_tokens(st["end"] - born, lifespan, lo, hi)
        words = int(round(b * 0.75 / 10.0)) * 10
        req = "\n\n".join([st["close"], f"This is the end of a stretch of days ({st['span']}). Tomorrow you will remember only your "
                           "memory, your notes and what you have always known, not the detail of these days.",
                           "## Your memory as it stands\n" + (memory or "(nothing yet)"),
                           M.PROMPTS[variant].format(limit=M.limit(words, last if growth else None,
                                                                         len(memory.split()) if growth and memory else None))
                           + ' Write it in "memory". Reply with JSON only.'])
        text = llm.flatten(conversation(st, memory) + [req])
        out, _, usage = llm.call(backend, model, system, text, SCHEMA, thinking_budget=0)
        new = str((out or {}).get("memory") or "").strip()
        if (out or {}).get("_error"):
            log.append({"stretch": [st["start"], st["end"]], "error": out["_error"]})
            break
        log.append({"stretch": [st["start"], st["end"]], "budget_words": words, "written": len(new.split()), "memory": new,
                    "cost": (usage or {}).get("cc_equiv_usd")})
        memory = M.cut(new, words) if new else memory
        last = words
    return {"agent": agent, "variant": variant + ("+growth" if growth else ""), "model": model, "lo": lo, "hi": hi, "log": log}


def main():
    import yaml
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="claude-sonnet-5-5")
    ap.add_argument("--backend", default="claude_code")
    ap.add_argument("--agents", nargs="+", default=["Lucy", "Jory", "Gunnild", "Gilbert"])
    ap.add_argument("--variants", nargs="+", default=list(M.PROMPTS))
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--lo", type=int, default=M.DEFAULTS["lo"])
    ap.add_argument("--hi", type=int, default=M.DEFAULTS["hi"])
    ap.add_argument("--growth", action="store_true", help='say "(n more than last time)" with the length')
    a = ap.parse_args()
    run = json.loads((RUN / "run.json").read_text())
    spec = yaml.safe_load(SPEC.read_text())
    jobs = [(ag, v) for ag in a.agents for v in a.variants]
    res = []
    with cf.ThreadPoolExecutor(a.workers) as ex:
        futs = {ex.submit(play, ag, v, a.model, a.backend, run["systems"][ag], int(spec["agents"][ag]["born"]),
                          int(spec.get("lifespan") or 64), a.lo, a.hi, a.growth): (ag, v) for ag, v in jobs}
        for f in cf.as_completed(futs):
            r = f.result()
            res.append(r)
            print(r["agent"], r["variant"], [x.get("written", x.get("error", "")[:40]) for x in r["log"]], flush=True)
    Path(a.out).write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    sys.exit(main())
