"""What an agent is shown (seeing.md §1): the system prompt (who it is, how life works, the place, what it knows how to do, how to
act), the turn prompt each morning, and the talk prompt when it is asked again before work. The reply schema."""
from __future__ import annotations

import json

from cybertron2.m1 import knowledge as KN, perceive as PC
from cybertron2.m1.data import COVERS, EDIBLE, ITEMS, TECHNIQUES
from cybertron2.m1.world import CONDITION, STAGES, show

SCHEMA = {
    "type": "object",
    "properties": {
        "why": {"type": "string"},
        "actions": {"type": "array", "items": {"type": "object", "properties": {
            "do": {"type": "string"}, "what": {"type": "string"}, "at": {"type": "string"}, "to": {"type": "string"},
            "item": {"type": "string"}, "qty": {"type": "number"}, "from": {"type": "string"}, "target": {"type": "string"},
            "aim": {"type": "string"}, "offer": {"type": "string"}, "person": {"type": "string"}, "thing": {"type": "string"}},
            "required": ["do"]}},
        "say": {"type": "array", "items": {"type": "object", "properties": {"to": {"type": "string"}, "text": {"type": "string"}},
                                            "required": ["to", "text"]}},
        "tell": {"type": "array", "items": {"type": "object", "properties": {"to": {"type": "string"}, "text": {"type": "string"}},
                                             "required": ["to", "text"]}},
        "explain": {"type": "array", "items": {"type": "object", "properties": {"to": {"type": "string"}, "what": {"type": "string"}},
                                                "required": ["to", "what"]}},
        "offers": {"type": "array", "items": {"type": "object", "properties": {
            "to": {"type": "string"}, "give": {"type": "string"}, "get": {"type": "string"}}, "required": ["give", "get"]}},
        "attend": {"type": "string"},
        "note": {"type": "array", "items": {"type": "object", "properties": {"title": {"type": "string"}, "text": {"type": "string"}},
                                             "required": ["title", "text"]}},
        "pin": {"type": "string"},
        "forget": {"type": "array", "items": {"type": "string"}},
        "open": {"type": "array", "items": {"type": "string"}},
        "look_up": {"type": "array", "items": {"type": "string"}},
        "memory": {"type": "string"},
    },
    "required": ["why", "actions"],
}

def access(w, name) -> list:
    """The buildings an agent has access to (D2-7, D4-30)."""
    return [bid for bid in w.buildings() if w.has_access(name, bid)]


def schema_for(w, name) -> dict:
    """The reply schema with the closed arguments as enums, so a reply can only name verbs, goods, crafts, places and people that
    exist (the CLI enforces the schema). Free text stays free: why, say, tell text, notes."""
    import copy
    from cybertron2.m1.act import VERBS
    from cybertron2.m1.data import ITEMS as _ITEMS
    people = sorted(x for x in w.s["agents"] if x != name and w.s["agents"][x]["alive"])
    houses = sorted(h["name"] for h in w.s["houses"].values())
    parcels = sorted(p["name"] for p in w.parcels().values())
    holds = sorted({a["household"] for a in w.s["agents"].values()})
    techs = sorted(TECHNIQUES)
    targets = people + houses + parcels + [h["name"] for h in w.s["herds"].values()] + ["the sky", "the place in general"]
    s = copy.deepcopy(SCHEMA)
    a = s["properties"]["actions"]["items"]["properties"]
    a["do"]["enum"] = list(VERBS)
    a["item"]["enum"] = list(_ITEMS)
    a["what"]["enum"] = techs
    a["at"]["enum"] = parcels + houses
    a["to"]["enum"] = ["house", "hands"] + people
    a["from"]["enum"] = people + houses
    a["target"]["enum"] = people + houses
    a["person"]["enum"] = people
    a["aim"]["enum"] = ["rob", "hurt"]
    a["thing"]["enum"] = ["door"]
    s["properties"]["tell"]["items"]["properties"]["to"]["enum"] = people
    s["properties"]["say"]["items"]["properties"]["to"]["enum"] = ["everyone"] + [w.buildings()[b]["name"] for b in access(w, name)]
    s["properties"]["explain"]["items"]["properties"]["to"]["enum"] = people
    s["properties"]["explain"]["items"]["properties"]["what"]["enum"] = techs
    s["properties"]["offers"]["items"]["properties"]["to"]["enum"] = ["anyone"] + people
    s["properties"]["attend"]["enum"] = targets
    s["properties"]["look_up"]["items"]["enum"] = techs
    return s


VERB_LINES = """- gather {"what": forage | hunt | fell, "at": place}  hunting needs a weapon to do well; felling a tool (bare hands do little)
- make {"what": grind | bread | crude weapon, "qty"?}  grind grain to flour at your house's quern; bake bread from flour
- work {"what": reap | milk | repair, "at"?: place}    reap a ripe field (a tool helps); milk a cow in milk; repair your house
- move {"item", "qty", "to": house | hands}            "house" puts it in your house's store; "hands" takes it out (free)
- give {"to": person, "item", "qty"}                    (free)
- accept {"offer": id}                                  an open offer made to you or to anyone: both sides at once, or nothing (free)
- set {"thing": door, "to": open | barred}              your house's door (free)
- watch {"person"}                                      spend the day working beside them: you see how they do things (4 units)
- teach {"to", "what"} / learn {"from", "what"}         one session, if both set aside the time the same day (2 units each)
- attack {"target": person | house, "aim": rob | hurt}  settled tonight (3 units)
- guard                                                 stand guard tonight over your house and anyone set upon (1 unit)
- steal {"from": house, "item", "qty"}                  from a house whose door is not barred; you may be seen (1 unit)
- rest"""

REPLY_LINES = """Reply with JSON:
- "why": a sentence or two on what you mean to do today and why.
- "actions": today's plan, in order, each {"do": verb, ...}. Actions beyond your units are not done.
- "tell": [{"to": a person, "text"}] said to that person alone. They hear it before the day's work and may answer or change
  their plans. You have a set number of private messages a day (answers count too); shown each morning.
- "say": [{"to": "everyone" or a building you have access to, "text"}] said to the whole village, or in a building (everyone who
  has access to it and is here today hears it, wherever they are). They hear it, but it does not call them away from their day:
  they take it in when they next have a moment. Each thing you say aloud takes one unit of your day's work.
- "explain": [{"to", "what": the craft's name}] explain a craft you know well to someone (they get a rough idea of it; free).
- "offers": [{"to": a person or "anyone", "give": "2 bread", "get": "1 timber"}] an exchange anyone named may accept today. What
  you offer comes from your hands, then your house's store; it is set aside until taken, or returned to your hands at nightfall.
  Only goods can be offered.
- "attend": the one thing you pay close attention to today: a person, a house, a place, the cattle, the sky, or "the place in general".
  You will see it in detail tomorrow morning. It costs nothing.
- "note": [{"title", "text"}] write or replace one of your private notes (up to 8, about 150 words each); "pin": a title to show
  in full every morning; "forget": [titles].
- "open": [note titles] and "look_up": [crafts]: shown to you before the day's work, when you may change your plan.
- "memory": only when asked for at the end of a stretch of days."""


def _kin(w, name) -> list:
    a = w.s["agents"][name]
    out = []
    for x, b in w.s["agents"].items():
        if x == name:
            continue
        rel = a["relations"].get(x)
        same = b["household"] == a["household"]
        if rel or same:
            dead = "" if b["alive"] else " (dead)"
            st = {"child": " (a child)", "youth": " (a youth)", "elder": " (an elder)"}.get(b.get("stage"), "")
            out.append(f"- {x}{st}: {rel or 'of your household'}{dead}" + (f"; {b['trade']}" if b.get("trade") else ""))
    for x, b in w.s["agents"].items():
        if x != name and x not in a["relations"] and b["household"] != a["household"]:
            out.append(f"- {x}: of {w.s['houses'][b['house']]['name'] if b['house'] else 'no house'}" + (f"; {b['trade']}" if b.get("trade") else ""))
    return out


def _place_lines(w) -> list:
    out = []
    for pid, p in w.parcels().items():
        c = COVERS[p["cover"]]
        can = [g for g in c["gather"]] + c["work"]
        adj = ", ".join(w.parcels()[q]["name"] for q in p["adj"])
        line = f"- {p['name']} ({p['cover']}{', ' + p['side'] if p['side'] else ''}): {p['text']}".rstrip(": ")
        bits = []
        if can:
            bits.append("here one can " + ", ".join(can))
        if c["lots"]:
            bits.append("ground to build on")
        if c["risks"]:
            bits.append("risks: " + ", ".join(c["risks"]))
        if c["becomes"]:
            bits.append("becomes " + c["becomes"])
        houses = [h["name"] for h in w.s["houses"].values() if h["parcel"] == pid]
        if houses:
            bits.append("houses: " + ", ".join(houses))
        out.append(line + ". " + "; ".join(bits) + (f". Next to {adj}." if adj else "."))
    for f in w.s["node"]["features"].values():
        out.append(f"- {f['name']}: {f['text']}")
    return out


def system_prompt(w, name) -> str:
    a = w.s["agents"][name]
    h = w.home(name)
    stage = {"youth": "a youth, not yet grown", "adult": "a grown adult", "elder": "an elder"}.get(a["stage"], a["stage"])
    lines = [f"You are {name}, {stage}, of {h['name'] if h else 'no house'} in {w.s['node']['name']}."
             + (f" You are the household's {a['role']}." if a.get("role") else "") + (f" By trade: {a['trade']}." if a.get("trade") else "")]
    if w.s["node"]["text"]:
        lines.append(w.s["node"]["text"])
    lines += ["", "Your people:"] + _kin(w, name)
    if a.get("aim") and w.spec.get("aims", False):                       # aims are off unless a world turns them on
        lines += ["", f"What you want: {a['aim']}"]
    p = w.p
    lines += ["", "How life works here:",
              f"- A day: you plan in the morning; anyone may speak to you before work, and you may answer; then you work. Work is counted in units: {p['units']['summer']} in "
              f"summer, {p['units']['autumn']} in autumn, {p['units']['winter']} in winter (at most {p['youth_units']} for a youth, "
              f"{p['elder_units']} for an elder); fewer when "
              "hungry or hurt. Any units you do not use are wasted.",
              f"- Each night everyone eats {p['ration']:g} food, from what they carry first, then from their house's store. Without a "
              "sound, warm house you need more. Missed meals make you hungry, then starving; starving people work less and can die.",
              f"- Food: grain is a meal as porridge at your hearth; bread (from flour) is a little more and keeps, and is eaten "
              f"anywhere; wild food is a meal; meat is a meal and a half but spoils fast; milk is half a meal and spoils within the "
              f"day. A house's store keeps food better than your hands. A house's fire burns {p['fuel']['normal']:g} timber "
              f"a night ({p['fuel']['cold']:g} on a cold one), taken from its store; a cold night without a fire is hard.",
              "- Houses fall into disrepair; repair takes timber. Goods lie in your hands or in your house's store; anything you carry "
              "you can give, and anything in a store with an open door can be taken.",
              "- Knowing how: a craft you know you can do well. You can know of a craft without knowing how. You get a rough idea of "
              "one by watching someone do it (a few days of seeing it done, or one day at their side), or by having it explained. "
              "With a rough idea you can try it, at a cost in materials and a fair chance of failing; each try teaches you. A day "
              "being taught by someone who knows it makes you capable (a youth learns faster). Practice makes you surer and better.",
              "- What you notice: each morning you hear what concerned you and what stood out the day before. You see one thing "
              "closely each day, whatever you chose to attend to; the rest you only glimpse.",
              "", f"The place, {w.s['node']['name']}:"] + _place_lines(w)
    lines += ["", "What you know how to do:"] + KN.crafts_lines(w, name)
    lines += ["", "What you can do (each action is a verb and what it acts on):", VERB_LINES, "", REPLY_LINES]
    return "\n".join(lines)


def _house_lines(w, name) -> list:
    h = w.home(name)
    if h is None:
        return ["You have no house."]
    hid = w.s["agents"][name]["house"]
    who = [x for x in w.living() if w.s["agents"][x]["house"] == hid and x != name]
    stock = ", ".join(f"{show(q)} {i}" for i, q in sorted(h["stock"].items()) if q > 0.05) or "empty"
    food = w.food_value(h["stock"])
    need = len(who) + 1
    return [f"{h['name']} is {CONDITION[h['condition']]}; door {h['door']}; fire {'lit' if h['fire'] else 'out'} last night. "
            f"Sleeping there: you{', ' + ', '.join(who) if who else ''}.",
            f"Its store: {stock} (food worth {show(food)} meals; the household eats about {need} a night, and the fire takes "
            f"{w.p['fuel']['cold' if w.cold() else 'normal']:g} timber)."]


def _offer_text(w, oid, o) -> str:
    g = ", ".join(f"{q:g} {i}" for i, q in o["give"].items())
    t = ", ".join(f"{q:g} {i}" for i, q in o["get"].items())
    return f"{oid}: {o['by']} offers {g} for {t}" + ("" if o["to"] else " (to anyone)")


def _yesterday_record(w, name, opening) -> list:
    """What it did yesterday (the engine's results), what it heard, and (in an opening) what it said."""
    days = PC.store(w, name)["days"]
    if not days:
        return []
    r = days[-1]
    out = ["You did: " + (" ".join(r["did"]) or "nothing")]
    if opening and r.get("said"):
        out.append("You said (words, not deeds): " + " | ".join(x[:200] for x in r["said"]))
    heard = r["heard"] if opening else [x for x in r["heard"] if not x.startswith(PC.DIRECT)]
    if heard:
        out.append("Heard" + ("" if opening else " (besides what was said to you, which you answered at the time)") + ":")
        out += [f"- {x}" for x in heard]
    return out


def turn_prompt(w, name, opening=True) -> str:
    """The morning message. An opening (the first message of a conversation) carries what the agent remembers: its seeded memories
    and lasting ones, and the memory it wrote itself; a continuing message carries only the day, since its earlier days are in
    the conversation."""
    a = w.s["agents"][name]
    cal = w.calendar()
    m = PC.store(w, name)
    t = m["today"]
    L = []
    if opening:
        mem = m.get("seeded", []) + m["lasting"]
        if mem:
            L.append("## What you remember\n" + "\n".join(f"- {x}" for x in mem))
        own = m.get("own", [])
        if own:
            L.append("## Your own memory of recent days (written by you)\n" + "\n".join(f"- {x['span']}: {x['text']}" for x in own))
    L.append(f"## Now\n{cal['season'].capitalize()}, day {cal['day']} of {w.season_len} ({cal['left']} left in the season)"
             + (", and cold" if w.cold() else "") + f". You have {w.units_for(name)} units of work today (saying something aloud "
             f"takes one) and {a['messages']} private messages.")
    rec = _yesterday_record(w, name, opening)
    if rec:
        L.append("## What happened yesterday\n" + "\n".join(rec))
    y = []
    if t["felt"] or t["learned"]:
        y += [f"- {x}" for x in t["felt"] + t["learned"]]
    if t["concerned"]:
        y += ["What concerned you:"] + [f"- {x}" for x in t["concerned"]]
    if t["notice"]:
        y += ["What stood out:"] + [f"- {x}" for x in t["notice"]]
    if t["attended"]:
        y += [f"You paid close attention to {t['attended']['target']}:"] + [f"- {x}" for x in t["attended"]["lines"]]
    if t["glimpse"]:
        y += ["In passing: " + "; ".join(t["glimpse"]) + "."]
    if w.d > 0:
        L.append("## What you saw yesterday\n" + ("\n".join(y) if y else "A quiet day: nothing stood out."))
    if t["dawn"]:
        L.append("## This morning\n" + "\n".join(f"- {x}" for x in t["dawn"]))
    hold = ", ".join(f"{show(q)} {i}" for i, q in sorted(a["holdings"].items()) if q > 0.05) or "nothing"
    you = [f"You are {STAGES[a['hunger']]}" + (", and hurt" if a["wounded"] else "") + f". You carry: {hold}."]
    L.append("## You\n" + "\n".join(you + _house_lines(w, name)))
    can, near = KN.options(w, name)
    opt = ["Today you could: " + "; ".join(can) + "." if can else "Of your crafts, none can be done today with what you have."]
    if near:
        opt.append("Not yet: " + "; ".join(near) + ".")
    if not opening:
        opt.append("What you know how to do: " + " ".join(x.removeprefix("- ") for x in KN.crafts_lines(w, name)))
    L.append("## Your crafts today\n" + "\n".join(opt))
    owed = [_offer_text(w, oid, o) for oid, o in w.s["offers"].items() if o["open"] and o["by"] != name and o["to"] in (None, name)]
    mine = [_offer_text(w, oid, o) for oid, o in w.s["offers"].items() if o["open"] and o["by"] == name]
    if owed or mine:
        L.append("## Offers open\n" + "\n".join([f"- {x}" for x in owed] + [f"- yours: {x}" for x in mine]))
    bl = PC.beliefs_lines(w, name)
    if bl:
        L.append("## As you last saw them\n" + "\n".join(f"- {x}" for x in bl))
    if a["notes"]:
        nl = []
        if a["pinned"] and a["pinned"] in a["notes"]:
            nl.append(f"Pinned, \u201c{a['pinned']}\u201d: {a['notes'][a['pinned']]}")
        rest = [k for k in a["notes"] if k != a["pinned"]]
        if rest:
            nl.append("Other notes (open them to read): " + "; ".join(f"\u201c{k}\u201d" for k in rest))
        L.append("## Your notes\n" + "\n".join(nl))
    L.append("Plan your day. Reply with JSON only.")
    return "\n\n".join(L)


def talk_prompt(w, name, heard: list, also: list, offers: list, opened: list, cards: list, results_so_far=None) -> str:
    """Asked again before work, in the same conversation: what was said to it, offers made to it, what else it heard this morning,
    notes it opened, crafts it looked up."""
    L = ["## Before the day's work"]
    if heard:
        L.append("Said to you:\n" + "\n".join(f"- {x}" for x in heard))
    if also:
        L.append("Also said this morning where you could hear:\n" + "\n".join(f"- {x}" for x in also))
    if offers:
        L.append("Offers made to you (accept with {\"do\": \"accept\", \"offer\": id}):\n" + "\n".join(f"- {x}" for x in offers))
    if opened:
        L.append("Your notes:\n" + "\n".join(f"- \u201c{k}\u201d: {v}" for k, v in opened))
    if cards:
        L.append("What you know of:\n" + "\n".join(f"- {c}" for c in cards))
    sent = sum(1 for x in results_so_far if x.startswith("You told ")) if results_so_far is not None else 0
    L.append(f"You have {max(0, w.s['agents'][name]['messages'] - sent)} private messages left today. You may answer (tell, say) and "
             "change your plan: give your whole plan for the day again (it replaces the one before). Reply with JSON only.")
    return "\n\n".join(L)


def memory_prompt(w, name, did: list, night: list, span: str) -> str:
    """At the end of a stretch of days, in the same conversation: the day's results, then the request to write its memory."""
    L = ["## The day is over", "You did: " + (" ".join(x for x in did if not x.startswith(PC.SPEECH)) or "nothing")]
    if night:
        L.append("In the night: " + " ".join(night))
    L.append(f"This is the end of a stretch of days ({span}). Tomorrow you start afresh: you will keep what you write now, your notes, "
             "and what you have always remembered, but not the detail of these days. In \"memory\", write in your own words what you "
             "want to remember of them (at most 150 words): what happened, what was agreed or promised, who owes what, what you mean "
             "to do. Leave \"actions\" empty. Reply with JSON only.")
    return "\n\n".join(L)
