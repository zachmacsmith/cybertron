"""Live test of lines kept for good (proposals/lasting_memory.md; review 38.39): w1's real stretches (days 0 to 23) replayed as in
38.36's harness (36_memory_rewrite.py), the memory rewritten each stretch with keep_change (D4-61), and beside it a few places for
lines kept word for word, in three arms:

    none      the rewrite alone (control)
    replace   an emptied place can be filled at once ("forget" and "keep" in one reply, or "replace")
    later     an emptied place is free only from the next stretch

    PYTHONPATH=. python3 docs/review/38_space_engine/39_lasting_memory.py --agents Lucy Jory Gunnild Gilbert \
        --arms none replace later --places 4 --out /tmp/lasting.json
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import importlib.util
import json
import sys
from pathlib import Path

from cybertron2.engine import memory as M

_spec = importlib.util.spec_from_file_location("h36", Path(__file__).with_name("36_memory_rewrite.py"))
H = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(H)

LINE_WORDS = 25
SCHEMAS = {
    "none": {"type": "object", "properties": {"memory": {"type": "string"}}, "required": ["memory"]},
    "replace": {"type": "object", "properties": {
        "memory": {"type": "string"},
        "keep": {"type": "array", "items": {"type": "string"}},
        "forget": {"type": "array", "items": {"type": "integer"}},
        "replace": {"type": "array", "items": {"type": "object", "properties": {"place": {"type": "integer"}, "text": {"type": "string"}},
                                                "required": ["place", "text"]}}},
        "required": ["memory"]},
    "later": {"type": "object", "properties": {
        "memory": {"type": "string"},
        "keep": {"type": "array", "items": {"type": "string"}},
        "forget": {"type": "array", "items": {"type": "integer"}}},
        "required": ["memory"]},
}
RULES = {
    "replace": 'In "keep", new lines go into empty places; "forget": [numbers] empties those places, and an emptied place can be '
               'filled in the same reply; "replace": [{"place", "text"}] puts a new line in place of an old one.',
    "later": 'In "keep", new lines go into empty places; "forget": [numbers] empties those places, but a place you empty now can be '
             'filled only from the next stretch.',
}


def kept_block(places, n):
    used = sum(1 for p in places if p)
    rows = [f"{i + 1}. " + (places[i] or "(empty)") for i in range(n)]
    return f"## Kept for good ({used} of {n} places)\n" + "\n".join(rows)


def cut_line(s):
    w = str(s).split()
    return " ".join(w[:LINE_WORDS])


def play(agent, arm, model, backend, system, born, lifespan, n):
    from cybertron import llm
    memory, log = "", []
    places = [None] * n
    cooling = set()
    refused = 0
    for st in H.stretches(agent):
        b = M.budget_tokens(st["end"] - born, lifespan)
        words = int(round(b * 0.75 / 10.0)) * 10
        conv = H.conversation(st, memory)
        if arm != "none" and any(places):                                   # the opening shows them, before the memory
            kb = "## Kept for good\n" + "\n".join(f"- {p}" for p in places if p)
            first = conv[0]
            conv[0] = first.replace("## Your memory (in your own words)", kb + "\n\n## Your memory (in your own words)", 1) \
                if "## Your memory (in your own words)" in first else first.replace("## Now\n", kb + "\n\n## Now\n", 1)
        parts = [st["close"], f"This is the end of a stretch of days ({st['span']}). Tomorrow you will remember only your memory, "
                 "your notes, what you keep for good and what you have always known, not the detail of these days."
                 if arm != "none" else
                 f"This is the end of a stretch of days ({st['span']}). Tomorrow you will remember only your memory, your notes and "
                 "what you have always known, not the detail of these days.",
                 "## Your memory as it stands\n" + (memory or "(nothing yet)")]
        if arm != "none":
            parts.append(kept_block(places, n) + (f"\n(Last time {refused} line{'s' if refused > 1 else ''} found no empty place and "
                                                  f"{'were' if refused > 1 else 'was'} not kept.)" if refused else ""))
        ask = M.PROMPTS["keep_change"].format(limit=M.limit(words)) + ' Write it in "memory".'
        if arm != "none":
            ask += (f" Kept for good is for what you mean to know for years, word for word: one sentence a line, at most {LINE_WORDS} "
                    "words; the memory may change, these do not unless you change them. " + RULES[arm])
        parts.append(ask + " Reply with JSON only.")
        text = llm.flatten(conv + ["\n\n".join(parts)])
        out, _, usage = llm.call(backend, model, system, text, SCHEMAS[arm], thinking_budget=0)
        out = out or {}
        if out.get("_error"):
            log.append({"stretch": [st["start"], st["end"]], "error": out["_error"]})
            break
        new = str(out.get("memory") or "").strip()
        memory = M.cut(new, words) if new else memory
        ev = {"forget": [], "keep": [], "replace": [], "refused": []}
        if arm != "none":
            cooling = set()
            for k in out.get("forget") or []:
                i = int(k) - 1
                if 0 <= i < n and places[i]:
                    ev["forget"].append(places[i])
                    places[i] = None
                    if arm == "later":
                        cooling.add(i)
            for r in out.get("replace") or [] if arm == "replace" else []:
                i = int(r.get("place", 0)) - 1
                if 0 <= i < n:
                    ev["replace"].append([places[i], cut_line(r.get("text"))])
                    places[i] = cut_line(r.get("text"))
            for line in out.get("keep") or []:
                free = [i for i in range(n) if not places[i] and i not in cooling]
                if free:
                    places[free[0]] = cut_line(line)
                    ev["keep"].append(cut_line(line))
                else:
                    ev["refused"].append(cut_line(line))
        refused = len(ev["refused"])
        log.append({"stretch": [st["start"], st["end"]], "budget_words": words, "written": len(new.split()), "memory": memory,
                    "places": list(places), "events": ev, "cost": (usage or {}).get("cc_equiv_usd")})
    return {"agent": agent, "arm": arm, "model": model, "places": n, "log": log}


def main():
    import yaml
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="claude-sonnet-5-5")
    ap.add_argument("--backend", default="claude_code")
    ap.add_argument("--agents", nargs="+", default=["Lucy", "Jory", "Gunnild", "Gilbert"])
    ap.add_argument("--arms", nargs="+", default=["none", "replace", "later"])
    ap.add_argument("--places", type=int, default=4)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    run = json.loads((H.RUN / "run.json").read_text())
    spec = yaml.safe_load(H.SPEC.read_text())
    jobs = [(ag, arm) for ag in a.agents for arm in a.arms]
    res = []
    with cf.ThreadPoolExecutor(a.workers) as ex:
        futs = {ex.submit(play, ag, arm, a.model, a.backend, run["systems"][ag], int(spec["agents"][ag]["born"]),
                          int(spec.get("lifespan") or 64), a.places): (ag, arm) for ag, arm in jobs}
        for f in cf.as_completed(futs):
            r = f.result()
            res.append(r)
            print(r["agent"], r["arm"], r["model"], [(x.get("written"), len(x.get("events", {}).get("keep", [])),
                                                      len(x.get("events", {}).get("forget", []))) if "error" not in x else x["error"][:40]
                                                     for x in r["log"]], flush=True)
            Path(a.out).write_text(json.dumps(res, indent=1))
    Path(a.out).write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    sys.exit(main())
