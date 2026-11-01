"""The morning message built from what the agent believes (review 38.40 §9; a world sets `view: beliefs`; otherwise prompt.turn_prompt).

Three routes (Zach, 1 Nov): what one knows of oneself is shown directly (body, what one carries, one's units and voice, one's own
deals); everything about the world outside oneself comes through the senses as beliefs, each with when it was seen (the day and the
weather are senses too, obvious to anyone awake at a place); what was said and done between people lives only in the agent's own
conversation and memory. The opening of a stretch shows the whole of what one believes of here; each later day shows only what
changed since the last message. No computed choices: there is no list of what one could do today.

The snapshot of what was shown is kept in the mind (`view`), written as `view_next` while rendering and made current at the end of
the day (perceive.close_day), so rendering twice in a morning gives the same message.
"""
from __future__ import annotations

from cybertron2.engine import agreements as AG, perceive as PC, prompt as PR
from cybertron2.engine.here import STAGES, show

PRESENT_MAX = 10                                                               # people named here before "and N others"


def on(w) -> bool:
    return (w.spec.get("view") or "") == "beliefs"


def _age(mind, day) -> str:
    d = mind.day - int(day)
    return "today" if d <= 0 else ("yesterday" if d == 1 else f"{d} days ago")


def _now(here, mind) -> str:
    """The day and the weather, as anyone awake here sees them, and one's own means today."""
    a, cal = mind.person, here.calendar()
    return (f"## Now\n{cal['season'].capitalize()}, day {cal['day']} of the season ({cal['left']} left), day {here.day + 1} of these days"
            + (", and cold" if here.cold() else "") + f": {here.weather_words()}. You have {here.units()} units of work today (saying "
            f"something aloud takes one) and {a['messages']} private messages.")


def _present(here, mind) -> list:
    """Who is here: one's household and kin first, then others, named up to PRESENT_MAX, the rest counted."""
    others = here.people(me=False)
    near = [x for x in others if x in mind.members] + [x for x in others if x not in mind.members and x in mind.kin()]
    rest = [x for x in others if x not in near]
    named = (near + rest)[:PRESENT_MAX]
    return named, len(others) - len(named)


def _seen(mind, sub, limit=3) -> str:
    b = (mind.store.get("beliefs") or {}).get(sub)
    if not b or not b.get("lines"):
        return ""
    return f"you saw {_age(mind, b['day'])}: " + "; ".join(b["lines"][:limit])


def _here_lines(here, mind) -> list:
    """The place as one sees it: its layout, the ground's kind and what such ground allows of the crafts one knows (the place lines,
    without their state), and what one last saw of each part, dated."""
    subs = [f"parcel:{p}" for p in here.parcels()] + [f"building:{b}" for b, x in here.buildings().items() if not x.get("unfinished")]
    out = []
    for sub, line in zip(subs, PR._place_lines(here, mind)):
        seen = _seen(mind, sub)
        out.append(line + (f" ({seen})" if seen else ""))
    return out


def _here(here, mind, a) -> str:
    home = next((nid for nid, x in mind.places().items() if x["days"] == 0), here.node)
    named, more = _present(here, mind)
    hl = [f"You are at {here.node_name}" + ("" if here.node == home else ", away from home") + ". Here today: "
          + (", ".join(PR._who(here, x) for x in named) or "nobody else") + (f", and {more} others" if more else "") + "."]
    if a.get("arrived") == here.day:
        hl.append("You arrived this morning.")
        way = mind.store.get("on_the_way") or {}
        if way.get("day") == here.day and way.get("lines"):
            hl.append("On the way: " + "; ".join(way["lines"]) + ".")
        ov = here.overview()
        if ov:
            hl.append("Arriving, what you see first: " + "; ".join(ov) + ".")
    hl += _here_lines(here, mind)
    ways = []
    for nid, name, days, track in here.roads():
        known = nid in mind.places()
        lms = here.landmarks_known(nid)
        ways.append(f"{name} ({days} day{'s' if days != 1 else ''}" + (", a cart track" if track else "")
                    + ("" if known else f': a way nobody you know has followed; to go along it, travel {{"to": "{name}"}}')
                    + (f"; on the way you know {', '.join(lms)}" if lms else "") + ")")
    if ways:
        hl.append("Roads from here: " + "; ".join(ways) + f". Each night on the road you eat {here.p['camping']['out'][0]:g} "
                  f"food ({here.p['camping']['out'][1]:g} on a cold night) from what you carry.")
    lying = PR._things_lines(here, mind)
    if lying:
        hl.append("Lying about, that you know of: " + "; ".join(lying) + ".")
    return "## Here, as you see it\n" + "\n".join(hl)


def _self(here, mind, a, full) -> str:
    hold = ", ".join(f"{show(q)} {i}" for i, q in sorted(here.carried().items()) if q > 0.05) or "nothing"
    you = [f"You are {STAGES[a['hunger']]}" + (", and hurt" if a["wounded"] else "") + f". You carry: {hold}"
           + (f" (weight {show(here.load())} of the {here.capacity():g} you can travel with)" if here.roads() else "") + "."]
    age = here.age_line()                                                      # one's age and what lies ahead (D4-69)
    if age:
        you.append(age)
    fam = PR._family_lines(here, mind)
    if not full:                                                               # the standing instructions only at the opening
        fam = [x for x in fam if not x.startswith(("Looking after a child is work", "While caring for a child"))]
    house = PR._house_lines(here, mind) if full else []
    return "## You\n" + "\n".join(you + fam + (PR._beast_lines(here, mind) if full else []) + house)


def _snapshot(here, mind) -> dict:
    homes = here.homes_here()
    named, more = _present(here, mind)
    stock = {}
    house = {}
    for bid in homes:
        stock[bid] = {i: round(q, 1) for i, q in here.stock(bid).items() if q > 0.05}
        b = here.buildings()[bid]
        house[bid] = {"condition": b["condition"], "door": b["door"], "fire": bool(b.get("fire"))}
    return {"day": here.day, "node": here.node, "present": sorted(here.people(me=False)), "stock": stock, "house": house,
            "buildings": sorted(here.buildings()), "seen": {k: v["day"] for k, v in (mind.store.get("beliefs") or {}).items()}}


def _changes(here, mind, last) -> list:
    """What differs from the last message: people come and gone, what one saw anew, one's house and its store, new buildings."""
    out = []
    now = set(here.people(me=False))
    before = set(last.get("present") or [])
    came, went = sorted(now - before), sorted(before - now)
    if came:
        out.append("Here now who were not before: " + ", ".join(PR._who(here, x) for x in came) + ".")
    if went:
        out.append("Gone from here since: " + ", ".join(went) + ".")
    names = {f"parcel:{p}": x["name"] for p, x in here.parcels().items()}
    names.update({f"building:{b}": x["name"] for b, x in here.buildings().items()})
    seen_before = last.get("seen") or {}
    told = set(PR.saw_lines(mind))                                              # what "What you saw yesterday" already says
    told |= {x[2:] for x in told if x.startswith("- ")}
    for sub, b in sorted((mind.store.get("beliefs") or {}).items(), key=lambda kv: kv[0]):
        if sub in names and b.get("lines") and b["day"] > int(seen_before.get(sub, -10 ** 6)):
            new = [x for x in b["lines"] if x not in told][:3]
            if new:
                out.append(f"{names[sub]}: " + "; ".join(new) + f" ({_age(mind, b['day'])}).")
    for bid in sorted(set(here.buildings()) - set(last.get("buildings") or [])):
        out.append(f"New here: {here.buildings()[bid]['name']}.")
    for bid in here.homes_here():
        b = here.buildings()[bid]
        old = (last.get("house") or {}).get(bid)
        st = {i: round(q, 1) for i, q in here.stock(bid).items() if q > 0.05}
        was = (last.get("stock") or {}).get(bid)
        if old is None or was is None:
            out += PR._house_lines(here, mind)
            continue
        if old["condition"] != b["condition"] or old["door"] != b["door"]:
            out.append(f"{b['name']}: now {PR.CONDITION[b['condition']]}, door {b['door']}.")
        diff = []
        for i in sorted(set(st) | set(was)):
            d = round(st.get(i, 0.0) - float(was.get(i, 0.0)), 1)
            if abs(d) >= 0.1:
                diff.append(f"{i} {'+' if d > 0 else ''}{show(d)} (now {show(st.get(i, 0.0))})")
        if diff:
            out.append(f"{b['name']}'s store since you last looked: " + ", ".join(diff) + ".")
    return out


def turn(here, mind, opening=True) -> str:
    """The morning message: at the opening, the whole of what one believes of here; after, what changed."""
    if here.node is None:
        return PR.turn_prompt(here, mind, opening)
    a = mind.person
    t = mind.store["today"]
    last = mind.store.get("view") or {}
    full = opening or last.get("node") != here.node or not last
    L = PR._memory_sections(mind) if opening else []
    L.append(_now(here, mind))
    rec = PR._yesterday_record(mind, opening)
    if rec:
        L.append("## What happened yesterday\n" + "\n".join(rec))
    y = PR.saw_lines(mind)
    if here.day > 0:
        L.append("## What you saw yesterday\n" + ("\n".join(y) if y else "A quiet day: nothing stood out."))
    if t["dawn"]:
        L.append("## This morning\n" + "\n".join(f"- {x}" for x in t["dawn"]))
    if full:
        L.append(_here(here, mind, a))
    else:
        ch = _changes(here, mind, last)
        L.append("## Since your last morning\n" + ("\n".join(f"- {x}" for x in ch) if ch else "Nothing here has changed that you can see."))
    L.append(_self(here, mind, a, full))
    offers = [AG.offer_text(here, oid) for oid, o in here.offers().items() if o["by"] != here.name and o["to"] in (None, here.name)]
    mine = [AG.offer_text(here, oid) for oid, o in here.offers().items() if o["by"] == here.name]
    if offers or mine:
        L.append("## Offers open here\n" + "\n".join([f"- {x}" for x in offers] + [f"- yours: {x}" for x in mine]))
    ag = AG.lines(here, mind)
    if ag:
        L.append("## Agreements (what is owed, as you know it)\n" + "\n".join(f"- {x}" for x in ag))
    if full:
        here_subs = {f"building:{b}" for b in here.buildings()} | {f"person:{x}" for x in here.people()}
        mine = {k: v for k, v in (mind.store.get("beliefs") or {}).items() if k not in here_subs}   # elsewhere only
        bl = PC.beliefs_lines(type("M", (), {"store": {"beliefs": mine}, "day": mind.day, "name": mind.name})(), {})
        if bl:
            L.append("## As you last saw them\n" + "\n".join(f"- {x}" for x in bl))
    if mind.notes:
        nl = []
        if a["pinned"] and a["pinned"] in mind.notes:
            nl.append(f"Pinned, “{a['pinned']}”: {mind.notes[a['pinned']]}")
        rest = [k for k in mind.notes if k != a["pinned"]]
        if rest:
            nl.append("Other notes (open them to read): " + "; ".join(f"“{k}”" for k in rest))
        L.append("## Your notes\n" + "\n".join(nl))
    L.append("Plan your day. Reply with JSON only.")
    mind.store["view_next"] = _snapshot(here, mind)
    return "\n\n".join(L)
