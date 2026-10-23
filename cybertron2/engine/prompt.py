"""What an agent is shown (proposals/seeing.md): the system prompt (who it is, how life works, its place and others as it knows them,
what it knows how to do, how to act), the morning message, the talk-step and setting-off messages, and the reply schema. Built from
`Here` and `Mind` only (D4-35); every rule's number comes from the physics, every verb from the registry (D4-24).
"""
from __future__ import annotations

import copy

from cybertron2.engine import agreements as AG, knowledge as KN, perceive as PC, verbs as V
from cybertron2.engine.data import BLUEPRINTS, FITTINGS, ITEMS, TECHNIQUES
from cybertron2.engine.here import CONDITION, STAGES, show

SCHEMA = {
    "type": "object",
    "properties": {
        "why": {"type": "string"},
        "actions": {"type": "array", "items": {"type": "object", "properties": {
            "do": {"type": "string"}, "what": {"type": "string"}, "at": {"type": "string"}, "to": {"type": "string"},
            "item": {"type": "string"}, "qty": {"type": "number"}, "from": {"type": "string"}, "target": {"type": "string"},
            "aim": {"type": "string"}, "offer": {"type": "string"}, "person": {"type": "string"}, "thing": {"type": "string"},
            "household": {"type": "string"}, "name": {"type": "string"}, "for": {"type": "string"}, "feed": {"type": "boolean"},
            "days": {"type": "number"}, "lots": {"type": "number"}, "agreement": {"type": "string"}},
            "required": ["do"]}},
        "say": {"type": "array", "items": {"type": "object", "properties": {"to": {"type": "string"}, "text": {"type": "string"}},
                                            "required": ["to", "text"]}},
        "tell": {"type": "array", "items": {"type": "object", "properties": {"to": {"type": "string"}, "text": {"type": "string"}},
                                             "required": ["to", "text"]}},
        "explain": {"type": "array", "items": {"type": "object", "properties": {"to": {"type": "string"}, "what": {"type": "string"}},
                                                "required": ["to", "what"]}},
        "offers": {"type": "array", "items": {"type": "object", "properties": {
            "to": {"type": "string"}, "give": {"type": "string"}, "get": {"type": "string"}, "lots": {"type": "number"},
            "for": {"type": "string"}}, "required": ["give", "get"]}},
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


def _known(mind):
    """The names the agent knows: people, households, buildings, places and herds (seeded and seen: D4-21, D4-35)."""
    people = sorted(x for x, k in mind.kin().items() if x != mind.name)
    places = mind.places()
    buildings = sorted({b for p in places.values() for b in p.get("buildings", [])})
    parcels = sorted({x for p in places.values() for x in p.get("parcels", [])})
    herds = sorted({x for p in places.values() for x in p.get("herds", [])})
    nodes = sorted(p["name"] for p in places.values())
    holds = sorted({k.get("household") for k in mind.kin().values() if k.get("household")} | ({mind.household} if mind.household else set()))
    return people, buildings, parcels, herds, nodes, holds


def schema_for(here, mind) -> dict:
    """The reply schema with closed arguments as enums of what the agent knows; free text stays free."""
    people, buildings, parcels, herds, nodes, holds = _known(mind)
    techs = sorted(t for t in TECHNIQUES if KN.level(mind, t) is not None) or sorted(TECHNIQUES)
    s = copy.deepcopy(SCHEMA)
    a = s["properties"]["actions"]["items"]["properties"]
    a["do"]["enum"] = [v for v in V.VERBS if V.verb_here(here, v)]
    a["item"]["enum"] = list(ITEMS)
    a["what"]["enum"] = techs + [x for x in ("shelter", "shelter and food") if x not in techs]
    a["at"]["enum"] = parcels + buildings
    a["to"]["enum"] = ["store", "hands", "anyone"] + people + holds + nodes
    a["from"]["enum"] = people + buildings
    a["target"]["enum"] = people + buildings
    a["person"]["enum"] = people
    a["aim"]["enum"] = ["rob", "hurt"]
    a["thing"]["enum"] = ["door"] + parcels + buildings + herds
    a["household"]["enum"] = holds
    a["for"]["enum"] = ["my household"] + people + holds
    for k in ("tell", "explain"):
        s["properties"][k]["items"]["properties"]["to"]["enum"] = people
    s["properties"]["explain"]["items"]["properties"]["what"]["enum"] = techs
    s["properties"]["say"]["items"]["properties"]["to"]["enum"] = ["everyone"] + buildings
    s["properties"]["offers"]["items"]["properties"]["to"]["enum"] = ["anyone"] + people
    s["properties"]["offers"]["items"]["properties"]["for"]["enum"] = ["my household"] + holds
    s["properties"]["attend"]["enum"] = people + buildings + parcels + herds + ["the sky", "the place in general"]
    s["properties"]["look_up"]["items"]["enum"] = techs
    return s


def _craft_note(tech) -> str:
    t = TECHNIQUES[tech]
    bits = []
    at = t.get("at") or {}
    if at.get("fittings"):
        bits.append("at " + " or ".join(FITTINGS[f]["label"] for f in at["fittings"]))
    tools = t.get("tools")
    if tools:
        bits.append("bare hands cannot" if "bare" not in tools else f"bare hands x{tools['bare']:g}")
        if "copper" in tools:
            bits.append(f"a copper tool x{tools['copper']:g}")
    if t.get("weapon"):
        bits.append("a weapon helps")
    if t["verb"] == "build":
        b = BLUEPRINTS.get(tech) or FITTINGS.get(tech)
        bits.append(", ".join(f"{q:g} {i}" for i, q in b["materials"].items()) + (" a bed" if b.get("per") else "") + f", {b['units']} units of work")
    return tech + (f" ({', '.join(bits)})" if bits else "")


def verb_lines(here, mind) -> str:
    out = []
    for v, d in V.VERB.items():
        if not V.verb_here(here, v):
            continue
        crafts = [_craft_note(t) for t in TECHNIQUES if TECHNIQUES[t]["verb"] == v and KN.level(mind, t) is not None]
        if "{crafts}" in d["doc"] and not crafts:
            continue
        n = V.verb_units(here.p, v)
        cost = "the craft's units" if n is None else ("free" if n == 0 else f"{n} unit{'s' if n > 1 else ''}")
        out.append(f"- {v} {d['args']}".rstrip() + f": {d['doc'].replace('{crafts}', '; '.join(crafts))}".rstrip(": ") + f" ({cost})")
    return "\n".join(out)


REPLY_LINES = """Reply with JSON:
- "why": a sentence or two on what you mean to do today and why.
- "actions": today's plan, in order, each {"do": verb, ...}. Actions beyond your units are not done. "for": a person or your
  household, on work, gathering, making, building, giving and accepting: done on their behalf (the goods go into their store here).
- "tell": [{"to": a person here, "text"}] said to that person alone. They hear it before the day's work and may answer or change
  their plans. You have a set number of private messages a day (answers count too); shown each morning.
- "say": [{"to": "everyone" or a building you have access to, "text"}] said to everyone here, or in a building (everyone who has
  access to it and is here today hears it). It does not call them away from their day. Each thing you say aloud takes one unit.
- "explain": [{"to", "what": the craft's name}] explain a craft you know well to someone here (they get a rough idea of it; free).
- "offers": [{"to": a person here or "anyone", "give", "get", "lots"?, "for"?}] an exchange. Goods as "2 bread"; a promise as
  "1 copper tool by day 10"; payments as "2 grain every 3 days for 4 times"; work as "work 2 days". What is due now moves at once
  when accepted, both ways or not at all; the rest is owed, and paid wherever both are at one place on its day, or falls into
  arrears. An offer to one person lasts the day; to anyone, while you stay here.
- "attend": the one thing you pay close attention to today. You will see it in detail tomorrow morning. It costs nothing.
- "note": [{"title", "text"}] write or replace a private note (up to 8, about 150 words each); "pin": a title to show every morning;
  "forget": [titles].
- "open": [note titles] and "look_up": [crafts]: shown to you before the day's work, when you may change your plan.
- "memory": only when asked for at the end of a stretch of days."""


def _kin_lines(mind) -> list:
    out = []
    for x, k in sorted(mind.kin().items(), key=lambda kv: (kv[0] not in mind.members, kv[0])):
        same = x in mind.members
        rel = k["rel"] if not k["rel"].startswith("of the ") or not same else "of your household"
        out.append(f"- {x}: {rel}" + ("" if same else f" ({k['lives']})") + ("" if k.get("alive", True) else " (dead, as you know)"))
    return out


def _place_lines(here) -> list:
    out = []
    for pid, p in here.parcels().items():
        adj = ", ".join(here.parcels()[q]["name"] for q in p["adj"] if q in here.parcels())
        herds = [h for h in here.herds().values() if h["parcel"] == pid]
        what = sorted({t for t, d in TECHNIQUES.items() if p["cover"] in (d.get("at") or {}).get("covers", [])
                       and (d.get("draws") in (None, "plot", "crop") or d.get("draws") in p["res"] or (d.get("draws") == "herd" and herds))})
        held = _holders(here, ("parcel", pid))
        bits = [f"{p['cover']}"] + ([f"held by {held}"] if held else []) + (["here one can " + ", ".join(what)] if what else [])
        bs = [b["name"] + (" (half built)" if b.get("unfinished") else "") for b in here.buildings().values() if b["parcel"] == pid]
        if bs:
            bits.append("buildings: " + ", ".join(bs))
        out.append(f"- {p['name']} ({'; '.join(bits)}): {p['text']}" + (f". Next to {adj}." if adj else "."))
    for bid, b in here.buildings().items():
        if b.get("unfinished"):
            continue
        fits = ", ".join(f"{n} beds" if f == "beds" else FITTINGS[f]["label"] for f, n in b["fittings"].items() if f in FITTINGS and n)
        held = _holders(here, ("building", bid))
        out.append(f"- {b['name']}: {b['structure']}, for {b['size']}" + (f"; {fits}" if fits else "; no fittings") + (f"; held by {held}" if held else ""))
    return out


def _holders(here, thing) -> str:
    hh = here.households()
    names = sorted({(hh[c["claimant"]]["name"] if c["claimant"] in hh else c["claimant"]) for c in here.claims(thing)
                    if c["grounds"] != "granted" and c["claimant"] != "anyone"})
    return " and ".join(names) + (" (disputed)" if len(names) > 1 else "") if names else ""


def _map_lines(mind) -> list:
    out = []
    home = next((nid for nid, p in mind.places().items() if p["days"] == 0), None)
    for nid, p in mind.places().items():
        if nid == home:
            continue
        far = f"{p['days']} day{'s' if p['days'] != 1 else ''} from home" if p["days"] is not None else "no way known"
        ways = ", ".join(f"{n} ({k} day{'s' if k > 1 else ''})" for n, k in p["ways"])
        seen = "" if p["seen"] is None else f" (as you saw it on {_daystr(mind, p['seen'])})" if p["seen"] >= 0 else ""
        out.append(f"- {p['name']}, {far}{seen}: {p['text']} Roads lead from it to {ways}.")
    return out


def _daystr(mind, d) -> str:
    c = mind.calendar(d)
    return f"{c['season']} day {c['day']}"


def weights_text() -> str:
    from collections import Counter
    common = Counter(v.get("weight", 1) for v in ITEMS.values()).most_common(1)[0][0]
    odd = [f"{i} {v.get('weight', 1):g}" for i, v in ITEMS.items() if v.get("weight", 1) != common]
    return "weights: " + ", ".join(odd) + f", everything else {common:g}"


def system_prompt(here, mind) -> str:
    a = mind.person
    stage = {"youth": "a youth, not yet grown", "adult": "a grown adult", "elder": "an elder"}.get(a["stage"], a["stage"])
    home = next((nid for nid, x in mind.places().items() if x["days"] == 0), here.node)
    hn = mind.places()[home]["name"]
    head = " You are its head." if mind.head == mind.name else (f" Its head is {mind.head}." if mind.head else "")
    lines = [f"You are {mind.name}, {stage}, of {mind.household_name or 'no household'} in {hn}.{head}"
             + (f" By trade: {a['trade']}." if a.get("trade") else "")]
    lines.append(f"{hn}: {mind.places()[home]['text']}")
    lines += ["", "Your people:"] + _kin_lines(mind)
    p = here.p
    lines += ["", "How life works here:",
              f"- A day: you plan in the morning; anyone here may speak to you before work, and you may answer; then you work. Work is "
              f"counted in units: {p['units']['summer']} in summer, {p['units']['autumn']} in autumn, {p['units']['winter']} in winter "
              f"(at most {p['youth_units']} for a youth, {p['elder_units']} for an elder); fewer when hungry or hurt. Any units you do "
              "not use are wasted.",
              f"- Each night everyone eats {p['ration']:g} food: what they carry first, then from the stores they may take from where "
              "they are (their household's, or a host's who feeds them). Without a sound, warm house you need more. Missed meals make "
              "you hungry, then starving; starving people work less and can die.",
              "- Food, in meals a unit: " + "; ".join(f"{i} {v['food']:g}" + (" (as porridge at a hearth)" if i == "grain" else "")
                                                      for i, v in ITEMS.items() if v["food"] > 0)
              + ". Spoils fastest in your hands: " + ", ".join(i for i, v in sorted(ITEMS.items(), key=lambda kv: -kv[1]["spoil"])
                                                           if v["food"] > 0 and v["spoil"] >= 0.15)
              + f"; a store keeps food {1 / p['house_spoil']:.0f} times better. A hearth burns {p['fuel']['normal']:g} timber a night "
              f"({p['fuel']['cold']:g} on a cold one) from its building's store; a cold night without a fire is hard.",
              "- Buildings are what is in them: beds, a hearth, bins, a quern, an anvil. Anyone can build a small room and put in beds and "
              "bins; a hearth or an anvil takes a trade. Buildings fall into disrepair; repair takes timber.",
              "- What is whose: land, buildings and herds are held by claims that people know of. Anyone can use anything they can reach, "
              "but using what others hold is seen and remembered, and taking from a store that is not yours is theft. A household's "
              "members may use its house and store; its head manages it. You may let others into a house you may let people into (host, "
              "grant), join another household if one who may admit you agrees, leave yours, start one of your own, claim an empty house "
              "or land, or build.",
              "- Knowing how: a craft you know you can do well. You can know of a craft without knowing how. You get a rough idea of "
              "one by watching someone do it, or by having it explained. With a rough idea you can try it, at a cost in materials and a "
              "fair chance of failing; each try teaches you. A day being taught by someone who knows it makes you capable (a youth "
              "learns faster).",
              "- What you notice: each morning you hear what concerned you and what stood out the day before. You see one thing "
              "closely each day, whatever you chose to attend to; the rest you only glimpse."]
    if len(mind.places()) > 1:
        lines += ["", f"Other places, as you know them (only what is carried goes between them; a night out costs "
                  f"{p['shelter']['unsheltered']:g} meals, {p['shelter_cold']['unsheltered']:g} in the cold, unless someone takes you in; "
                  f"on foot you carry at most {p['carry']['foot']:g} weight; {weights_text()}):"] + _map_lines(mind)
    lines += ["", "What you know how to do:"] + KN.crafts_lines(mind)
    lines += ["", "What you can do (each action is a verb and what it acts on):", verb_lines(here, mind), "", REPLY_LINES]
    return "\n".join(lines)


def _yesterday_record(mind, opening) -> list:
    days = mind.store["days"]
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


def _house_lines(here, mind) -> list:
    homes = here.homes_here()
    out = []
    if not mind.household:
        out.append("You belong to no household.")
    elif not homes:
        seen = mind.home_seen()
        if seen:
            stock = ", ".join(f"{show(q)} {i}" for i, q in sorted(seen["stock"].items()) if q > 0.05) or "empty"
            out.append(f"You are away from home. When you left it on {_daystr(mind, seen['day'])} it was {CONDITION[seen['condition']]}, "
                       f"door {seen['door']}, its store: {stock}.")
        else:
            out.append("Your household has no house here.")
        hosts = [b for b, x in here.buildings().items() if "access" in here.rights(("building", b))]
        feed = [b for b in hosts if "withdrawal" in here.rights(("building", b))]
        out.append("Tonight: " + (f"you may sleep at {', '.join(here.buildings()[b]['name'] for b in hosts)}" if hosts else "nobody has let you in here yet")
                   + (f", and eat from {', '.join(here.buildings()[b]['name'] for b in feed)}'s store" if feed else
                      "; away from a store you may take from, you eat only what you carry") + ".")
    others = [b for b in homes if not here.buildings()[b]["fittings"].get("beds")]
    if others:
        out.append("Also yours here: " + "; ".join(f"{here.buildings()[b]['name']} (store: " + (", ".join(f"{show(q)} {i}" for i, q in
                   sorted(here.stock(b).items()) if q > 0.05) or "empty") + ")" for b in others) + ".")
    for bid in [b for b in homes if b not in others]:
        b = here.buildings()[bid]
        st = here.stock(bid)
        who = [x for x in here.people(me=False) if bid in here.homes_here(x)]
        stock = ", ".join(f"{show(q)} {i}" for i, q in sorted(st.items()) if q > 0.05) or "empty"
        food = sum(st.get(i, 0) * ITEMS[i]["food"] for i in ITEMS if ITEMS[i]["food"])
        out.append(f"{b['name']} is {CONDITION[b['condition']]}; door {b['door']}" + ((f"; fire {'lit' if b['fire'] else 'out'} last night" if here.day else "")
                   if b['fittings'].get('hearth') else "; no hearth")
                   + f". Sleeping there: you{', ' + ', '.join(who) if who else ''} ({b['fittings'].get('beds', 0)} beds).")
        out.append(f"Its store: {stock} (food worth {show(food)} meals; those who eat from it eat about {len(who) + 1} a night"
                   + (f", and the fire takes {here.p['fuel']['cold' if here.cold() else 'normal']:g} timber" if b['fittings'].get('hearth') else "") + ").")
    return out


def turn_prompt(here, mind, opening=True) -> str:
    a = mind.person
    cal = here.calendar()
    t = mind.store["today"]
    L = []
    if opening:
        mem = mind.store.get("seeded", []) + mind.store["lasting"]
        if mem:
            L.append("## What you remember\n" + "\n".join(f"- {x}" for x in mem))
        own = mind.store.get("own", [])
        if own:
            L.append("## Your own memory of recent days (written by you)\n" + "\n".join(f"- {x['span']}: {x['text']}" for x in own))
    L.append(f"## Now\n{cal['season'].capitalize()}, day {cal['day']} of the season ({cal['left']} left), day {here.day + 1} of these days"
             + (", and cold" if here.cold() else "") + f". You have {here.units()} units of work today (saying something aloud takes one) and "
             f"{a['messages']} private messages.")
    rec = _yesterday_record(mind, opening)
    if rec:
        L.append("## What happened yesterday\n" + "\n".join(rec))
    y = [f"- {x}" for x in t["felt"] + t["learned"]]
    if t["concerned"]:
        y += ["What concerned you:"] + [f"- {x}" for x in t["concerned"]]
    if t["notice"]:
        y += ["What stood out:"] + [f"- {x}" for x in t["notice"]]
    if t["attended"]:
        y += [f"You paid close attention to {t['attended']['target']}:"] + [f"- {x}" for x in t["attended"]["lines"]]
    if t["glimpse"]:
        y += ["In passing: " + "; ".join(t["glimpse"]) + "."]
    if here.day > 0:
        L.append("## What you saw yesterday\n" + ("\n".join(y) if y else "A quiet day: nothing stood out."))
    if t["dawn"]:
        L.append("## This morning\n" + "\n".join(f"- {x}" for x in t["dawn"]))
    home = next((nid for nid, x in mind.places().items() if x["days"] == 0), here.node)
    hl = [f"You are at {here.node_name}" + ("" if here.node == home else ", away from home") + ". Here today: "
          + (", ".join(here.people(me=False)) or "nobody else") + "."]
    if a.get("arrived") == here.day:
        hl.append("You arrived this morning.")
    hl += _place_lines(here)
    L.append("## Here\n" + "\n".join(hl))
    hold = ", ".join(f"{show(q)} {i}" for i, q in sorted(here.carried().items()) if q > 0.05) or "nothing"
    you = [f"You are {STAGES[a['hunger']]}" + (", and hurt" if a["wounded"] else "") + f". You carry: {hold}"
           + (f" (weight {show(here.load())} of the {here.p['carry']['foot']:g} you can travel with)" if here.roads() else "") + "."]
    L.append("## You\n" + "\n".join(you + _house_lines(here, mind)))
    can, near = KN.options(here, mind)
    opt = ["Today you could: " + "; ".join(can) + "." if can else "Of your crafts, none can be done here today with what you have."]
    if near:
        opt.append("Not yet: " + "; ".join(near) + ".")
    if not opening:
        opt.append("What you know how to do: " + " ".join(x.removeprefix("- ") for x in KN.crafts_lines(mind)))
    L.append("## Your crafts today\n" + "\n".join(opt))
    offers = [AG.offer_text(here, oid) for oid, o in here.offers().items() if o["by"] != here.name and o["to"] in (None, here.name)]
    mine = [AG.offer_text(here, oid) for oid, o in here.offers().items() if o["by"] == here.name]
    if offers or mine:
        L.append("## Offers open here\n" + "\n".join([f"- {x}" for x in offers] + [f"- yours: {x}" for x in mine]))
    ag = AG.lines(here, mind)
    if ag:
        L.append("## Agreements (what is owed, as you know it)\n" + "\n".join(f"- {x}" for x in ag))
    names = {f"building:{b}": x["name"] for b, x in here.buildings().items()}
    bl = PC.beliefs_lines(mind, names)
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
    return "\n\n".join(L)


def talk_prompt(here, mind, heard, also, offers, opened, cards, sent=0) -> str:
    L = ["## Before the day's work"]
    if heard:
        L.append("Said to you:\n" + "\n".join(f"- {x}" for x in heard))
    if also:
        L.append("Also said this morning where you could hear:\n" + "\n".join(f"- {x}" for x in also))
    if offers:
        L.append("Offers made to you (accept with {\"do\": \"accept\", \"offer\": id}):\n" + "\n".join(f"- {x}" for x in offers))
    if opened:
        L.append("Your notes:\n" + "\n".join(f"- “{k}”: {v}" for k, v in opened))
    if cards:
        L.append("What you know of:\n" + "\n".join(f"- {c}" for c in cards))
    L.append(f"You have {max(0, mind.person['messages'] - sent)} private messages left today. You may answer (tell, say) and change your "
             "plan: give your whole plan for the day again (it replaces the one before). Reply with JSON only.")
    return "\n\n".join(L)


def lighten_prompt(here, mind, a: dict, did: list) -> str:
    goods = ", ".join(f"{show(q)} {i} ({show(q * ITEMS[i]['weight'])} weight)" for i, q in sorted(here.carried().items()) if q > 0.05)
    L = ["## Setting off", "Today so far: " + (" ".join(x for x in did if not x.startswith(PC.SPEECH)) or "nothing"),
         f"You meant to set off for {a.get('to')} tonight, but you carry {show(here.load())} weight and on foot you can carry "
         f"{here.p['carry']['foot']:g}. You carry: {goods}.",
         f"Before you go you may give things to someone here ({', '.join(here.people(me=False)) or 'nobody is here'}), put them in a store "
         f"you may use, or leave them at a building here ({', '.join(b['name'] for b in here.buildings().values()) or 'none'}): "
         "{\"do\": \"leave\", \"item\", \"qty\", \"at\": building}; what is left there is found by its household in the morning. Then "
         "travel again. Or stay here tonight: leave out the travel.",
         "Reply with JSON only: put these in \"actions\" (give, leave, move, travel; no work), and leave everything else empty."]
    return "\n\n".join(L)


def memory_prompt(mind, did: list, night: list, span: str) -> str:
    L = ["## The day is over", "You did: " + (" ".join(x for x in did if not x.startswith(PC.SPEECH)) or "nothing")]
    if night:
        L.append("In the night: " + " ".join(night))
    L.append(f"This is the end of a stretch of days ({span}). Tomorrow you start afresh: you will keep what you write now, your notes, "
             "and what you have always remembered, but not the detail of these days. In \"memory\", write in your own words what you "
             "want to remember of them (at most 150 words): what happened, what was agreed or promised, who owes what, what you mean "
             "to do. Leave \"actions\" empty. Reply with JSON only.")
    return "\n\n".join(L)
