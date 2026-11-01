"""The evening at the hearth (proposals/speech_order.md; D4-65, D4-66). A world turns it on with `evening: true`.

After the day's work and before the day's settling and the night, everyone at a place meets where they will sleep: their house (or
the house they mean to sleep in), or in the open if they have none here. Each is asked once, together, and shown how the day went
(what they did and got, whom they arrived among); each may talk to those at the same hearth (free: everyone there hears), tell one
person at the place a private word, and settle the night with the acts that take no work (where to sleep, letting someone in, taking
someone into the household, becoming partners, trying for a child with units kept back, a fire, the door, an offer accepted, goods
given or moved, a name given, setting off at nightfall). Then one wave: only those asked something directly (told something, named
in what was said at their hearth, asked to answer a request) are woken once to answer. What is said reaches the others next morning.
"""
from __future__ import annotations

import re

from cybertron2.engine import perceive as PC, prompt as PR, verbs as V
from cybertron2.engine.here import Here, Mind
from cybertron2.engine.world import Refused

NIGHT_VERBS = ("sleep", "host", "grant", "revoke", "admit", "join", "leave_household", "found", "partner", "part", "try", "fire", "set",
               "accept", "withdraw", "release", "give", "move", "name", "travel", "rest", "order", "claim", "meet")
MAX = 3


def on(w) -> bool:
    return PR.evening(w)


def gathering(w, n) -> tuple:
    """(key, words) for where one spends the evening: the building one means to sleep in, one's house here, or the open."""
    node = w.at(n)
    today = w.s["today"]
    bid = today["sleep"].get(n)
    if bid is None or w.s["buildings"].get(bid, {}).get("node") != node:
        bid = next((b for b in w.homes(n) if w.s["buildings"][b]["node"] == node and not w.s["buildings"][b].get("unfinished")
                    and w.s["buildings"][b]["fittings"].get("beds")), None)
    if bid:
        return f"building:{bid}", f"at {w.s['buildings'][bid]['name']}"
    return f"open:{node}", f"in the open at {w.s['nodes'][node]['name']}"


def who_is_called(w, names) -> list:
    """Those at a place this evening, not setting off tonight (their night is on the road)."""
    today = w.s["today"]
    return [n for n in names if w.s["people"][n]["alive"] and w.at(n) is not None and n not in today["travel"]]


def _requests(w, n, since=None) -> list:
    """What waits on one's answer tonight: others trying for a child with one, asking to be partners, asking to join one's household,
    offers to one."""
    t = w.s["today"]
    out = []
    mine = {x["with"] for x in t["try"] if x["by"] == n}
    for x in t["try"][since["try"] if since else 0:]:
        if x["with"] == n and x["by"] not in mine:
            out.append(f"{x['by']} is trying for a child with you tonight; it counts only if you try with {x['by']} too (\"try\", with units "
                       "you have left today).")
    partners = {x.get("with") for x in t["partner"] if x.get("by") == n}
    for x in t["partner"][since["partner"] if since else 0:]:
        if x.get("with") == n and x.get("by") not in partners:
            out.append(f"{x.get('by')} asks to become partners with you (\"partner\" with {x.get('by')} to agree).")
    hh = w.household_of(n)
    for x in t["joins"][since["joins"] if since else 0:]:
        if hh and x.get("household") == hh and w.head(hh) == n:
            out.append(f"{x['by']} asks to be taken into your household (\"admit\" {x['by']} to agree).")
    here = Here(w, n)
    for oid, o in here.offers().items():
        if o["by"] != n and o["to"] == n and (since is None or o.get("day") == w.d):
            from cybertron2.engine import agreements as AG
            out.append(f"An offer to you: {AG.offer_text(here, oid)} (\"accept\" it, or leave it).")
    return out


def prompt(w, n, results, left, place, others, arrived) -> str:
    here, mind = Here(w, n), Mind(w, n)
    L = ["## This evening"]
    L.append(f"You are {place} for the evening" + (f", having come in at nightfall from {arrived}" if arrived else "") + ". "
             + (f"With you: {', '.join(others)}." if others else "Nobody else is with you."))
    did = [x for x in results if not x.startswith(PC.SPEECH)]
    L.append("## Your day\n" + ("\n".join(f"- {x}" for x in did) if did else "You did nothing today."))
    req = _requests(w, n)
    if req:
        L.append("## Waiting on your answer\n" + "\n".join(f"- {x}" for x in req))
    L.append("## Tonight\n"
             "This is the time to talk with those here and to settle the night. \"say\" is heard by everyone at this hearth and costs "
             "nothing (to ask someone something, name them, and they may answer tonight); \"tell\" is a private word to one person at "
             "this place. In \"actions\" put only what settles the night, which takes no work: sleep, host, grant, admit, join, partner, "
             f"try (with units you kept back: you have {left} left today), fire, set the door, accept an offer, give or move goods, "
             "name, travel (to set off at nightfall). Work, gathering and making wait for tomorrow. \"why\": what you make of the day and "
             "what you mean to do tomorrow. Reply with JSON only.")
    return "\n\n".join(L)


def answer_prompt(w, n, heard, asked, left) -> str:
    L = ["## Before you sleep"]
    if heard:
        L.append("Said to you tonight:\n" + "\n".join(f"- {x}" for x in heard))
    if asked:
        L.append("Waiting on your answer:\n" + "\n".join(f"- {x}" for x in asked))
    L.append(f"You may answer (say, tell) and settle the night (actions, as before; you have {left} units left today). This is the last "
             "word tonight: what you say now is heard, but answered tomorrow. Reply with JSON only.")
    return "\n\n".join(L)


def apply(w, n, reply, gather, names, results, left, box) -> int:
    """One evening reply: speech to the hearth (free), private words, the night's acts. Returns units spent (trying for a child)."""
    here, mind = Here(w, n), Mind(w, n)
    results.extend(PC.apply_notes(mind, {k: reply.get(k) for k in ("note", "pin", "forget")}))
    hearth = [m for m in names if m != n and gather.get(m) == gather.get(n)]
    for x in [x for x in (reply.get("say") or []) if isinstance(x, dict) and str(x.get("text", "")).strip()][:MAX]:
        text = str(x["text"])[:600]
        for m in hearth:
            box.setdefault(m, {"heard": [], "asked": []})
            if re.search(rf"\b{re.escape(m)}\b", text):
                box[m]["heard"].append(f"{n} (at the hearth): {text}")
            PC.store(w, m)["today"]["heard"].append(f"{n} said in the evening: {text}")
        results.append(f"You said (in the evening): {text}")
    for t in [t for t in (reply.get("tell") or []) if isinstance(t, dict)][:MAX]:
        text, to = str(t.get("text", ""))[:600], here.person(t.get("to"))
        if not to or to not in names or to == n:
            results.append(f"Refused: tell: nobody called {t.get('to')!r} is here to hear you")
            continue
        lim = w.s["people"][n]["messages"]
        if sum(1 for y in results if y.startswith("You told ")) >= lim:
            results.append(f"Refused: tell: you have sent your {lim} private messages for today")
            continue
        box.setdefault(to, {"heard": [], "asked": []})["heard"].append(f"{n} (to you alone): {text}")
        PC.store(w, to)["today"]["heard"].append(f"{PC.DIRECT}{n} told you in the evening: {text}")
        results.append(f"You told {to}: {text}")
    spent = 0
    for a in [a for a in (reply.get("actions") or []) if isinstance(a, dict)][:8]:
        verb = str(a.get("do", "")).lower()
        if verb not in NIGHT_VERBS:
            results.append(f"Refused: {verb}: the day's work is done; that waits for tomorrow")
            continue
        if verb == "travel" and str(a.get("when") or "").lower() == "morning":
            results.append("Refused: travel: to set off in the morning, put it first in tomorrow's plan")
            continue
        c = V.cost(here, a)
        if c > left - spent:
            results.append(f"Not done: {verb}: it takes {c} units and you have {max(0, left - spent)} left today")
            continue
        res = V.do(here, mind, a)
        if not res.startswith("Refused"):
            spent += c
            if verb == "host":                                                  # a guest let in tonight sleeps there
                guest = here.person(a.get("person") or a.get("to"))
                if guest and guest not in w.s["today"]["sleep"]:
                    bid = gather.get(n, "").removeprefix("building:")
                    if bid in w.s["buildings"]:
                        w.s["today"]["sleep"][guest] = bid
        results.append(res)
    return spent


def snapshot(w) -> dict:
    t = w.s["today"]
    return {"try": len(t["try"]), "partner": len(t["partner"]), "joins": len(t["joins"])}


# ---------------------------------------------------------------------- planning at the hearth (`evening: plan`, D4-77)
def plans_at_hearth(w) -> bool:
    return str((w.spec or {}).get("evening")) == "plan"


def split_plan(reply) -> tuple:
    """An evening reply's acts: those for tonight, and the rest as tomorrow's plan."""
    acts = [a for a in (reply.get("actions") or []) if isinstance(a, dict)]
    night = [a for a in acts if str(a.get("do", "")).lower() in NIGHT_VERBS and not (str(a.get("do", "")).lower() == "travel"
                                                                                    and str(a.get("when") or "").lower() == "morning")]
    return night, [a for a in acts if a not in night]


def needs_morning(w, n) -> bool:
    """With the plan made at the hearth, one is asked again at dawn only if something new reached one: a sign at dawn, something
    that concerned one, a night that touched one's household (a birth, a death, a missed meal), or a meeting called."""
    t = PC.store(w, n)["today"]
    if t.get("dawn") or t.get("concerned"):
        return True
    log = (w.s.get("log") or [{}])[-1] if w.s.get("log") else {}
    hh = w.household_of(n)
    near = {m for m in w.living() if hh and w.household_of(m) == hh} | {n}
    life = log.get("life") or {}
    if any(x in near for x in (log.get("missed") or [])) or any(d in near or d == n for d in (log.get("deaths") or [])):
        return True
    if any(b.get("mother") in near for b in life.get("births") or []) or life.get("deaths"):
        return True
    return Here(w, n).meeting_today() is not None


# ---------------------------------------------------------------------- a meeting called for the morning (D4-77)
def meeting_block(w, n) -> str:
    m = Here(w, n).meeting_today()
    if not m:
        return ""
    return (f"## A meeting this morning\n{m['by']} has called everyone here to meet at {m['at']} before the day's work"
            + (f", about {m['about']}" if m.get("about") else "") + ". To go, put {\"do\": \"come\"} in your plan: it takes a unit, and "
            "before work you talk there with all who come, and may change your plan.")


def meeting_prompt(w, n, m, present, said) -> str:
    L = [f"## The meeting at {m['at']}, called by {m['by']}" + (f" about {m['about']}" if m.get("about") else "")]
    L.append("Here: " + ", ".join(present) + ".")
    if said:
        L.append("Said so far:\n" + "\n".join(f"- {x}" for x in said))
    L.append("Speak with \"say\" (everyone here hears it; free); make or answer offers (\"offers\"; what is offered here, all here "
             "witness); and give your whole plan for the day again in \"actions\" if it changes. Reply with JSON only.")
    return "\n\n".join(L)


def witness(w, present, line) -> None:
    for m in present:
        st = PC.store(w, m)
        st["lasting"] = (st.get("lasting") or []) + [f"{PC._day(w, w.d)}: witnessed at the meeting: {line}"]
        st["lasting"] = st["lasting"][-14:]
