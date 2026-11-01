"""Memory rewritten (D4-61, spec/information/memory.md; review 38.36): at the end of each stretch of days an agent rewrites its one
memory, keeping what it still wants from before and adding what it wants from these days, within a length that grows with its age.

- `rewrite` (the default): one memory, rewritten each stretch; the engine keeps no list of its own (what matters is the agent's
  choice); its length is set by `budget`.
- `append` (D4-28's rule, kept for weak models, which rewrite badly: `memory.append_models`, default the Haiku models): a new memory
  of at most 150 words each stretch, the last six shown, and the engine's own list of marked events (perceive.close_day: `lasting`).
  `memory.mode: append` puts every agent on it.

The budget, in tokens, rises over a life with the largest rises early and levelling off later:

    budget(age) = lo + (hi - lo) * (1 - e^(-k * age / L)) / (1 - e^(-k))        age in days, L the lifespan

A memory is cut to the budget (at a sentence end) only when it runs well over (CAP).
"""
from __future__ import annotations

import math
import re

from cybertron2.engine import life as LF

DEFAULTS = {"lo": 150, "hi": 800, "k": 3.0, "words_per_token": 0.75, "cap": 1.15, "prompt": "keep_change"}
APPEND_MODELS = ("claude-haiku",)                                          # weak models keep the queue (review 38.36: Haiku rewrites
                                                                           # from scratch and drops what matters)

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
    return {**DEFAULTS, **(m.get("rewrite") or {}), "mode": m.get("mode", "rewrite"),
            "append_models": tuple(m.get("append_models", APPEND_MODELS))}


def mode_for(w, name) -> str:
    """rewrite, or append for a weak model (by its model id's start) or when the world says append."""
    s = settings(w)
    if s["mode"] == "append":
        return "append"
    model = str((w.s["people"].get(name) or {}).get("model") or "")
    return "append" if any(model.startswith(p) for p in s["append_models"]) else "rewrite"


def rewriting(w, name) -> bool:
    return mode_for(w, name) == "rewrite"


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
    L.append(f"This is the end of a stretch of days ({span}). Tomorrow you will remember only your memory, your notes, what you "
             "keep for good and what you have always known, not the detail of these days.")
    L.append("## Your memory as it stands\n" + (current(mind) or "(nothing yet)"))
    instr = PROMPTS[variant or settings(w)["prompt"]].format(limit=limit(b["words"]))   # the plain limit (38.36: a growth note
                                                                                          # made agents fill the space)
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


# ---------------------------------------------------------------------- kept for good (D4-64, spec/information/memory.md)
# Beside the rewritten memory, places for lines one wants to remember for good: a sentence each, kept word for word, shown at
# every opening. Kept or let go at the end of each stretch; passed on to a child with care (life.care_gifts), each childhood line
# adding a place; at coming of age the childhood lines and one place more, then places open over adult life by the schedule.
# Customs are such lines, seeded to those alive when a world starts (perceive.seed_knowledge); a world may fix lines.
KEPT = {"words": 25, "childhood": 4, "most": None, "per_lifespan": 5, "schedule": "evenly", "every": None, "refill": "now"}
KEPT_ASK = ("Kept for good: what you want to remember for good, a sentence each (at most {words} words), kept word for word "
            "whatever you rewrite. When your places are full, you can forget one to keep something that matters more. "
            '("keep": [new lines]; "drop": [the numbers of lines to forget]; {refill}.)')


def kept_settings(w) -> dict:
    return {**KEPT, **((w.spec.get("memory") or {}).get("kept") or {})}


def kept(w, name) -> dict:
    """One's kept lines and where its places are counted from: {lines: [{text, source, day, fixed}], start, from, shown}."""
    from cybertron2.engine import perceive as PC
    return PC.store(w, name).setdefault("kept", {"lines": [], "start": None, "from": None, "shown": None, "refused": 0})


def line(text, words=None) -> str:
    ws = str(text or "").split()
    return " ".join(ws[: int(words or KEPT["words"])])


def seed_line(w, name, text, source="seeded", fixed=False) -> None:
    k = kept(w, name)
    t = line(text, kept_settings(w)["words"])
    if t and t not in [x["text"] for x in k["lines"]]:
        k["lines"].append({"text": t, "source": source, "day": w.d, "fixed": bool(fixed)})


def come_of_age(w, name, day=None) -> None:
    """Places are counted from coming of age: one for each line already held, and one more (D4-64)."""
    k = kept(w, name)
    k["start"] = len(k["lines"]) + 1
    k["from"] = w.d if day is None else int(day)


def places(w, name) -> int:
    """How many places one has today: the start, then more over adult life by the world's schedule, up to the most."""
    k, s = kept(w, name), kept_settings(w)
    a = w.s["people"][name]
    if a["stage"] in LF.MINOR:
        return len(k["lines"])
    if k["start"] is None:                                                   # grown, with no coming of age on record (an undated world)
        come_of_age(w, name)
    start = int(k["start"])
    L = LF.lifespan(w)
    most = max(start, int(s["most"]) if s["most"] else start + int(round(L / float(s["per_lifespan"]))))
    since = max(0, w.d - int(k["from"]))
    if s["schedule"] == "none":
        n = start
    elif s["schedule"] == "every" and s.get("every"):
        n = start + since // int(s["every"])
    else:                                                                    # evenly from coming of age to the end of the lifespan
        end = int(a.get("born") or 0) + L
        span = max(1, end - int(k["from"]))
        n = start + int(math.floor((most - start) * min(1.0, since / span)))
    return max(len(k["lines"]), min(most, n))


def kept_lines_text(w, name) -> list:
    return [x["text"] for x in kept(w, name)["lines"]]


def kept_request(w, name) -> str:
    """The memory request's own question: the lines, the places (empty ones shown, a new one said), and the wording (D4-64)."""
    k, s = kept(w, name), kept_settings(w)
    n = places(w, name)
    rows = [f"{i + 1}. " + (k["lines"][i]["text"] + (" (fixed)" if k["lines"][i].get("fixed") else "") if i < len(k["lines"]) else "(empty)")
            for i in range(n)]
    L = [f"## Kept for good ({len(k['lines'])} of {n} place{'s' if n != 1 else ''})"] + rows
    if k["shown"] is not None and n > int(k["shown"]):
        L.append("A new place has opened since last time." if n - int(k["shown"]) == 1 else f"{n - int(k['shown'])} new places have opened since last time.")
    if k.get("refused"):
        L.append(f"(Last time {k['refused']} line{'s' if k['refused'] > 1 else ''} found no empty place and "
                 f"{'were' if k['refused'] > 1 else 'was'} not kept.)")
    refill = "a place you empty can be filled at once" if s["refill"] == "now" else "a place you empty can be filled from next time"
    L.append(KEPT_ASK.format(words=s["words"], refill=refill))
    return "\n".join(L)


def kept_apply(w, name, reply) -> dict:
    """The reply's drop (forgetting lines; not fixed ones) then keep (into empty places, in order); what found no place is counted for next time."""
    k, s = kept(w, name), kept_settings(w)
    n = places(w, name)
    reply = reply if isinstance(reply, dict) else {}
    out = {"forgot": [], "kept": [], "refused": []}
    drop = set()
    for x in reply.get("drop") or []:
        try:
            i = int(x) - 1
        except (TypeError, ValueError):
            continue
        if 0 <= i < len(k["lines"]) and not k["lines"][i].get("fixed"):
            drop.add(i)
    if drop:
        out["forgot"] = [k["lines"][i]["text"] for i in sorted(drop)]
        k["lines"] = [x for i, x in enumerate(k["lines"]) if i not in drop]
    room = n - len(k["lines"]) - (len(drop) if s["refill"] != "now" else 0)
    for t in reply.get("keep") or []:
        t = line(t, s["words"])
        if not t or t in [x["text"] for x in k["lines"]]:
            continue
        if room > 0:
            k["lines"].append({"text": t, "source": "own", "day": w.d, "fixed": False})
            out["kept"].append(t)
            room -= 1
        else:
            out["refused"].append(t)
    k["refused"] = len(out["refused"])
    k["shown"] = n
    return out
