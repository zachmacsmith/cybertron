"""Memory rewritten (proposals/memory_rewrite.md, under test): at the end of each stretch of days an agent rewrites its one memory,
keeping what it still wants from before and adding what it wants from these days, within a length that grows with its age.

- The default (`memory.mode: append`) is unchanged: a new memory of at most 150 words each stretch, the last six shown, and the
  engine's own list of marked events (perceive.close_day: `lasting`).
- `memory.mode: rewrite`: one memory, rewritten each stretch; the engine keeps no list of its own (what matters is the agent's
  choice); its length is set by `budget`.

The budget, in tokens, rises over a life with the largest rises early and levelling off later:

    budget(age) = lo + (hi - lo) * (1 - e^(-k * age / L)) / (1 - e^(-k))        age in days, L the lifespan

A memory is cut to the budget (at a sentence end) only when it runs well over (CAP).
"""
from __future__ import annotations

import math
import re

from cybertron2.engine import life as LF

DEFAULTS = {"lo": 150, "hi": 1200, "k": 3.0, "words_per_token": 0.75, "cap": 1.15, "prompt": "keep_change"}

# Very short instructions, compared live (review 38.36). {limit}: the length allowed, and how much more than last time (Zach:
# "you should also say ... n more than last time"); the agent's memory as it stands and the stretch's own days are in front of it.
PROMPTS = {
    "plain": "Rewrite your memory to carry forward, in at most {limit}.",
    "keep_change": "Rewrite your memory in at most {limit}: keep what still matters, add from these days only what you will want "
                   "later, and leave the rest.",
    "most_days": "Rewrite your memory in at most {limit}. Most days are not worth keeping; some things are. Keep what still "
                 "matters from before.",
    "revise": "Rewrite your memory in at most {limit}: keep what still matters, correct what has changed, and add from these "
              "days only what you will want later.",
    "future_days": "What might you still want to know in the days to come? Rewrite your memory with that, in at most {limit}.",
    "keep_future": "Rewrite your memory in at most {limit}: keep what still matters, and add what you might still want to know in the "
                   "days to come.",
    "future_self": "Rewrite your memory in at most {limit}, for yourself in a season's time: what will you need to know?",
}


def settings(w) -> dict:
    m = (w.spec.get("memory") or {})
    return {**DEFAULTS, **(m.get("rewrite") or {}), "mode": m.get("mode", "append")}


def rewriting(w) -> bool:
    return settings(w)["mode"] == "rewrite"


def budget_tokens(age_days, lifespan, lo=DEFAULTS["lo"], hi=DEFAULTS["hi"], k=DEFAULTS["k"]) -> int:
    x = max(0.0, min(1.0, float(age_days) / float(lifespan)))
    return int(round(lo + (hi - lo) * (1 - math.exp(-k * x)) / (1 - math.exp(-k))))


def budget(w, name) -> dict:
    s = settings(w)
    age = LF.days_old(w, name)
    if age is None:                                                          # a world not dated in days: a grown adult's
        age = LF.lifespan(w) * 0.5
    tokens = budget_tokens(age, LF.lifespan(w), s["lo"], s["hi"], s["k"])
    return {"tokens": tokens, "words": int(round(tokens * s["words_per_token"] / 10.0)) * 10, "age": age}


def limit(words, last=None, wrote=None) -> str:
    """"520 words (40 more than last time; last time you wrote 410 of 480)", or "520 words" when there is no last time
    (Zach: say how much more, and how much of the last allowance was used)."""
    if not last:
        return f"{words} words"
    more = words - int(last)
    head = f"{more} more than last time" if more > 0 else "the same as last time"
    used = f"; last time you wrote {int(wrote)} of {int(last)}" if wrote is not None else ""
    return f"{words} words ({head}{used})"


def current(mind) -> str:
    return ((mind.store.get("memory") or {}).get("text")) or ""


def request(w, name, mind, did, night, span, variant=None) -> str:
    """The end of a stretch: what happened last, the memory as it stands, and the instruction."""
    from cybertron2.engine import perceive as PC
    b = budget(w, name)
    L = ["## The day is over", "You did: " + (" ".join(x for x in did if not x.startswith(PC.SPEECH)) or "nothing")]
    if night:
        L.append("In the night: " + " ".join(night))
    L.append(f"This is the end of a stretch of days ({span}). Tomorrow you will remember only your memory, your notes and what you "
             "have always known, not the detail of these days.")
    L.append("## Your memory as it stands\n" + (current(mind) or "(nothing yet)"))
    mem = mind.store.get("memory") or {}
    wrote = len(mem["text"].split()) if mem.get("text") else None
    instr = PROMPTS[variant or settings(w)["prompt"]].format(limit=limit(b["words"], mem.get("budget"), wrote))
    L.append(f"{instr} Write it in \"memory\"; leave \"actions\" empty. Reply with JSON only.")
    return "\n\n".join(L)


def cut(text, words) -> str:
    """Within CAP of the budget it stands; beyond, it is cut back to the budget at the last sentence end."""
    ws = str(text).split()
    if len(ws) <= words * DEFAULTS["cap"]:
        return " ".join(ws)
    head = " ".join(ws[:words])
    m = list(re.finditer(r"[.!?](\s|$)", head))
    return head[: m[-1].end()].strip() if m else head


def keep(w, name, text, span) -> dict:
    """The rewritten memory replaces the old (an empty reply keeps the old)."""
    from cybertron2.engine import perceive as PC
    m = PC.store(w, name)
    b = budget(w, name)
    text = str(text or "").strip()
    if not text:
        return m.get("memory") or {}
    m["memory"] = {"text": cut(text, b["words"]), "span": span, "day": w.d, "budget": b["words"], "written": len(text.split())}
    return m["memory"]
