"""Birth and death (spec/life/birth_and_death.md: D2-138 to D2-152; life_stages.md D4-19, D4-20).

Engine side. Every span of life is counted in days (D2-139): a person's stage follows its days since birth (`born`, a day, negative
for those born before the run); a world dated in days ages everyone each dawn. Children come only by choice: two people of opposite
sex at one node each spend units trying (D2-138, D2-146, D2-152), and that night the woman may conceive. A pregnancy costs food and,
late on, work; a birth carries risk; infants and children eat, need care (the world's cost dial: D2-145, D2-151), do small work by
the head's standing order (D2-148), and at the end of childhood become agents with memories of what they lived through. The old die
with a risk that rises with age (D2-149). On a death, the household's own rules say who heads it and who inherits (D2-143).

A world turns this on with `children: {on: true, dial: low | high}`; off (the default), nobody conceives, but a world dated in days
still ages and its old still die.
"""
from __future__ import annotations

import math

from cybertron2.engine.data import LIFE

STAGES = [s for s, _ in LIFE["shares"]] + ["elder"]
MINOR = ("infant", "child")


# ---------------------------------------------------------------------- settings and stages
def setting(w) -> dict:
    c = w.spec.get("children")
    if isinstance(c, dict):
        return {"on": bool(c.get("on", True)), "dial": str(c.get("dial", "low"))}
    return {"on": bool(c), "dial": "low"}


def on(w) -> bool:
    return setting(w)["on"]


def dial(w) -> dict:
    return LIFE["dial"].get(setting(w)["dial"], LIFE["dial"]["low"])


def lifespan(w=None) -> int:
    """Days from birth to old age, a world setting (D2-153; default 32)."""
    return int((w.spec.get("lifespan") if w is not None else None) or LIFE["lifespan"])


def scaled(days, L) -> int:
    """A span given at the default lifespan, scaled to this one: whole days, at least 1 (D2-153)."""
    return max(1, round(float(days) * L / float(LIFE["lifespan"])))


def spans(L=None) -> list:
    """[(stage, days)] for a lifespan: each stage its share, whole days, at least 1; the adult span takes up the rounding."""
    L = int(L or LIFE["lifespan"])
    out = [(name, max(1, round(share * L))) for name, share in LIFE["shares"]]
    young = sum(d for _, d in out[:-1])
    out[-1] = (out[-1][0], max(1, L - young))
    return out


def stage_of(days: float, L=None) -> str:
    """The stage by days since birth (D2-139, D2-153)."""
    t = 0
    for name, span in spans(L):
        t += span
        if days < t:
            return name
    return "elder"


def days_old(w, name):
    born = w.s["people"][name].get("born")
    return None if born is None else w.d - int(born)


def elder_from(L=None) -> int:
    return sum(span for _, span in spans(L))


def pregnancy_days(w) -> int:
    return scaled(LIFE["pregnancy"]["days"], lifespan(w))


# ---------------------------------------------------------------------- dawn: growing up, coming of age, succession
def dawn(w) -> list:
    """Each dawn: stages follow days since birth; a child that turns youth becomes an agent (D4-20); a household's 2 days to name a
    head end (D2-143). Returns what happened, for the day's log."""
    out = []
    for name in w.living():
        a = w.s["people"][name]
        d = days_old(w, name)
        if d is None:
            continue
        new = stage_of(d, lifespan(w))
        if new != a["stage"]:
            old = a["stage"]
            a["stage"] = new
            out.append((name, old, new))
            if old in MINOR and new == "youth":
                come_of_age(w, name)
    for iid, h in w.s["institutions"].items():
        sc = h.get("succession")
        if sc and w.d >= int(sc["until"]):
            names = {}
            for voter, choice in (sc.get("named") or {}).items():
                if choice in w.s["people"] and w.s["people"][choice]["alive"] and w.household_of(choice) == iid:
                    names[choice] = names.get(choice, 0) + 1
            if names:
                top = sorted(names.items(), key=lambda kv: (-kv[1], w.s["people"][kv[0]].get("born") or 0))[0][0]
                h["offices"]["head"] = top
                out.append(("succession", iid, top))
            h.pop("succession", None)
    return out


def come_of_age(w, name) -> None:
    """A child becomes a youth: an agent, its model chosen now (D4-20: the heir to a pole seat takes that seat's model; the rest the
    cast's youth model), with lasting memories of what it was present for, and its household's crafts as awareness (D4-33)."""
    a = w.s["people"][name]
    hh = w.household_of(name)
    inst = w.s["institutions"].get(hh) or {}
    head = (inst.get("offices") or {}).get("head")
    cast = w.spec.get("cast") or {}
    if inst.get("heir") == name and head in w.s["people"]:
        a["model"] = w.s["people"][head].get("model") or cast.get("youth") or "claude-haiku-5-5"
    else:
        a["model"] = cast.get("youth") or "claude-haiku-5-5"
    hm = (w.spec.get("household_models") or {}).get(hh)                         # a world may give each household one model
    if hm:
        a["model"] = hm
    if w.spec.get("bots"):
        a["model"] = "bot"
    m = w.s["mind"][name]
    lines = list(dict.fromkeys((m.get("childhood") or [])))[-6:]
    if lines:
        m.setdefault("lasting", []).extend(f"From when you were small: {x}" for x in lines)
    from cybertron2.engine import knowledge as KN
    from cybertron2.engine.data import TECHNIQUES
    k = w.s["know"].setdefault(name, {})
    for other in w.members(hh) if hh else []:
        for tech, r in (w.s["know"].get(other) or {}).items():
            if tech in TECHNIQUES and not KN.basic(tech) and r.get("level") == "known" and tech not in k:
                k[tech] = {"level": "aware", "skill": 0.6, "seen": 0, "wins": 0, "fails": 0,
                           "source": f"you grew up watching {other} at it", "since": w.d}
    w.event(w.at(name) or w.place_of(("person", name)), "grown", f"{name} is grown now, a youth", actor=name, salience=0.4,
            tags=["family"], concerns=w.members(hh) if hh else [])


# ---------------------------------------------------------------------- the day: partners, children's work
def settle(w, today) -> list:
    """Partnerships both chose today at one place (D2-140). Returns [(a, b)] made."""
    out = []
    picks = today.get("partner") or []
    for x in picks:
        a, b = x["by"], x["with"]
        if a < b and any(y["by"] == b and y["with"] == a for y in picks) and w.place_of(("person", a)) == w.place_of(("person", b)):
            w.apply("partner", w.place_of(("person", a)), person=a, other=b)
            out.append((a, b))
            w.event(w.place_of(("person", a)), "household", f"{a} and {b} are partners now", actor=a, target=b, salience=0.6,
                    tags=["family"], concerns=sorted(set(w.members(w.household_of(a)) or []) | set(w.members(w.household_of(b)) or [])))
    return out


def children_work(w) -> dict:
    """Each child does its household's standing order (D2-148), up to the dial's units: at the high setting half a unit, so every
    other day. Returns {child: result line}."""
    from cybertron2.engine import verbs as V
    from cybertron2.engine.here import Here, Mind
    out = {}
    share = float(dial(w)["child_works"])
    for name in w.living():
        a = w.s["people"][name]
        if a["stage"] != "child" or a["at"] is None:
            continue
        hh = w.household_of(name)
        order = (w.s["institutions"].get(hh) or {}).get("order")
        if not order or order.get("node") not in (None, a["at"]):
            continue
        if share < 1 and w.rng("child-work", w.d, name).random() >= share:
            continue
        from cybertron2.engine.data import TECHNIQUES
        act = {"do": TECHNIQUES[order["what"]]["verb"], "what": order["what"], "for": "my household"}
        if order.get("at"):
            act["at"] = order["at"]
        out[name] = V.do(Here(w, name), Mind(w, name), act)
    return out


# ---------------------------------------------------------------------- what people eat and can do
def ration_factor(w, name) -> tuple:
    """(multiplier on the ration, food added): an infant eats 0.5, a child by the dial; a pregnancy adds 0.3 a day (D2-141)."""
    a = w.s["people"][name]
    if a["stage"] == "infant":
        return float(LIFE["infant"]["eats"]), 0.0
    if a["stage"] == "child":
        return float(dial(w)["child_eats"]), 0.0
    extra = float(LIFE["pregnancy"]["food"]) if a.get("pregnant") is not None else 0.0
    return 1.0, extra


def late_pregnancy(w, name) -> bool:
    a = w.s["people"][name]
    late = scaled(LIFE["pregnancy"]["late"], lifespan(w))
    return a.get("pregnant") is not None and w.d - int(a["pregnant"]) > pregnancy_days(w) - late     # its last 2 days


def unit_penalty(w, name) -> int:
    return int(LIFE["pregnancy"]["late_units"]) if late_pregnancy(w, name) else 0


def infants_of(w, name, place=None) -> list:
    """The living infants whose mother this is, with her (at her node, or carried on the road)."""
    place = w.place_of(("person", name)) if place is None else place
    return sorted(n for n, a in w.s["people"].items() if a["alive"] and a["stage"] == "infant" and (a.get("parents") or [None])[0] == name
                  and w.place_of(("person", n)) == place)


def feeders(w, name) -> list:
    """Who may feed a child from their own hands: its parents and its household's adults and youths, where it is."""
    a = w.s["people"][name]
    hh = w.household_of(name)
    near = set(w.company(name))
    kin = set(a.get("parents") or []) | set(w.members(hh) if hh else [])
    return sorted(x for x in kin & near if x != name and w.s["people"][x]["alive"] and w.s["people"][x]["stage"] not in MINOR)


def carried_weight(w, name) -> float:
    if w.s["people"][name].get("sex") != "f":
        return 0.0
    return float(LIFE["infant"]["weight"]) * len(infants_of(w, name))


def showing(w, name) -> bool:
    """A pregnancy shows from its third day (D2-141)."""
    a = w.s["people"][name]
    return a.get("pregnant") is not None and w.d - int(a["pregnant"]) >= scaled(LIFE["pregnancy"]["signs_from"], lifespan(w))


def grows_in(w, name):
    """Days until a child is grown (a youth), else None."""
    d = days_old(w, name)
    if d is None or w.s["people"][name]["stage"] not in MINOR:
        return None
    L = lifespan(w)
    return sum(span for st, span in spans(L) if st in MINOR) - d


def in_gap(w, name) -> bool:
    a = w.s["people"][name]
    return a.get("gap_until") is not None and w.d < int(a["gap_until"])


def may_conceive(w, name) -> str:
    """'' if this woman could conceive now, else why not."""
    a = w.s["people"][name]
    if a.get("sex") != "f":
        return ""
    if a.get("pregnant") is not None:
        return f"{name} is with child already"
    if a.get("gap_until") is not None and w.d < int(a["gap_until"]):
        return f"{name} gave birth lately and cannot conceive yet"
    return ""


# ---------------------------------------------------------------------- the night (after eating)
def night(w, today, rec, where) -> dict:
    """Conception, pregnancy, births; infants' and children's deaths; old age; what children were present for (D2-138 to D2-150)."""
    out = {"conceived": [], "lost": [], "births": [], "deaths": [], "old_age": []}
    if on(w):
        _conceive(w, today, rec, where, out)
    _pregnancies(w, today, rec, where, out)
    _young(w, today, rec, where, out)
    _old_age(w, out)
    _childhood(w, today, rec)
    return out


def chance(units) -> float:
    c = LIFE["conceive"]
    return float(c["base"]) * (1 - math.exp(-float(c["k"]) * float(units)))


def _conceive(w, today, rec, where, out):
    tries = today.get("try") or []
    for t in tries:
        a, b, units = t["by"], t["with"], t["units"]
        back = next((x for x in tries if x["by"] == b and x["with"] == a), None)
        if not back:
            continue
        if a > b:
            continue                                                            # each pair once
        wom = a if w.s["people"][a].get("sex") == "f" else b
        if not all(w.s["people"][x]["alive"] for x in (a, b)) or may_conceive(w, wom):
            continue
        if where.get(a) != where.get(b) or w.place_of(("person", a)) != w.place_of(("person", b)):
            continue                                                            # they slept apart
        if a in rec["missed"] or b in rec["missed"]:
            continue                                                            # one of them went hungry
        u = min(int(units), int(back["units"]))
        if w.rng("conceive", w.d, a, b).random() < chance(u):
            w.s["people"][wom]["pregnant"] = w.d
            w.s["people"][wom]["father"] = b if wom == a else a
            out["conceived"].append(wom)


def _pregnancies(w, today, rec, where, out):
    pg = LIFE["pregnancy"]
    for name in w.living():
        a = w.s["people"][name]
        if a.get("pregnant") is None:
            continue
        if late_pregnancy(w, name) and a["at"] is None and w.rng("road-loss", w.d, name).random() < float(pg["road_loss"]):
            a["pregnant"] = None
            out["lost"].append(name)
            continue
        if w.d - int(a["pregnant"]) >= pregnancy_days(w):                      # the night ending its fifth day
            _birth(w, name, where, rec, out)


def _birth(w, mother, where, rec, out):
    """The birth, wherever the mother is that night (D2-141, D2-147): risks by shelter and food, halved with another adult there."""
    b = LIFE["birth"]
    a = w.s["people"][mother]
    bid = where.get(mother)
    housed = bid is not None and w.s["buildings"][bid]["condition"] > 0 and mother not in rec["missed"] \
        and not (w.cold() and not w.s["buildings"][bid].get("fire"))
    risk = b["housed" if housed else "out"]
    helped = any(n != mother and where.get(n) == bid and w.s["people"][n]["stage"] in ("adult", "elder") and
                 w.place_of(("person", n)) == w.place_of(("person", mother)) for n in w.living())
    half = float(b["helped"]) if helped else 1.0
    rng = w.rng("birth", w.d, mother)
    place = w.place_of(("person", mother))
    father = a.get("father")
    a["pregnant"], a["gap_until"], a["father"] = None, w.d + 1 + scaled(LIFE["gap"], lifespan(w)), None
    child = w.apply("born", place, mother=mother, father=father)
    out["births"].append({"mother": mother, "child": child, "helped": helped, "housed": housed})
    hh = w.household_of(mother)
    concerns = (w.members(hh) if hh else []) + ([father] if father else [])
    w.event(place, "birth", f"{mother} gave birth to a child, {child}", actor=mother, target=child, salience=0.7, tags=["family"],
            concerns=concerns, about=[f"building:{bid}"] if bid else [])
    if rng.random() < float(risk["infant"]) * half:
        w.apply("die", place, person=child, cause="born too weak")
        out["deaths"].append(child)
    if rng.random() < float(risk["mother"]) * half:
        w.apply("die", place, person=mother, cause="childbirth")
        out["deaths"].append(mother)


def _young(w, today, rec, where, out):
    """Infants and children: deaths by care, hunger and cold (D2-150, the dial: D2-145)."""
    care = today.get("care") or {}
    d = dial(w)
    for name in w.living():
        a = w.s["people"][name]
        if a["stage"] not in MINOR or a.get("born") == w.d:                  # born tonight: the birth's own risk only
            continue
        units = float(care.get(name, 0.0))
        a["cared"] = {"day": w.d, "units": units, "by": list((today.get("care_by") or {}).get(name, []))}
        if a["stage"] == "infant":
            inf = LIFE["infant"]
            p = float(inf["dies"]["cared" if units + 1e-9 >= float(d["infant_care"]) else "not"])
            if name in rec["missed"]:
                p *= float(inf["hungry"])
            bid = where.get(name)
            if w.cold() and (bid is None or not w.s["buildings"][bid].get("fire")):
                p *= float(inf["cold"])
        else:
            p = float(LIFE["child"]["dies"])
            if float(d["child_minding"]) > 0 and units + 1e-9 < float(d["child_minding"]):
                p *= float(LIFE["child"]["unminded"])
        if w.rng("young", w.d, name).random() < p:
            place = w.place_of(("person", name))
            cause = "neglect" if a["stage"] == "infant" and units <= 0 else ("hunger" if name in rec["missed"] else "a fever")
            w.apply("die", place, person=name, cause=cause)
            out["deaths"].append(name)
            if place in w.s["nodes"]:
                hh = w.household_of(name)
                w.event(place, "death", f"{name}, a {a['stage']}, died in the night", target=name, salience=0.9, tags=["death", "family"],
                        concerns=w.members(hh) if hh else [])


def _old_age(w, out):
    """Beyond hunger, cold and wounds: an adult 0.001 a night, an elder 0.01 doubling every 20 days of old age (D2-149)."""
    oa = LIFE["old_age"]
    for name in w.living():
        a = w.s["people"][name]
        if a["stage"] == "adult":
            p = float(oa["adult"])
        elif a["stage"] == "elder":
            d, L = days_old(w, name), lifespan(w)
            into = max(0, (d if d is not None else elder_from(L)) - elder_from(L))
            p = float(oa["elder"]) * 2 ** (into / (float(oa["doubling"]) * L / float(LIFE["lifespan"])))
        else:
            continue
        if a.get("born") is None and a["stage"] != "elder":
            continue                                                            # a world not dated in days: only elders age
        if w.rng("old-age", w.d, name).random() < min(1.0, p):
            place = w.place_of(("person", name))
            w.apply("die", place, person=name, cause="old age")
            out["old_age"].append(name)
            if place in w.s["nodes"]:
                w.event(place, "death", f"{name} died in the night, of old age", target=name, salience=1.0, tags=["death"])


def _childhood(w, today, rec):
    """What a child was present for goes into its memories (D2-144): who cared for and fed it, deaths and births where it was, cold
    nights without a fire, going hungry."""
    care_by = today.get("care_by") or {}
    for name in w.living():
        a = w.s["people"][name]
        if a["stage"] not in MINOR or a["at"] is None:
            continue
        m = w.s["mind"][name].setdefault("childhood", [])
        for who in care_by.get(name, []):
            m.append(f"{who} looked after you")
        if name in rec["missed"]:
            m.append("you went hungry to bed")
        for e in w.s["events"]:
            if e.get("place") == a["at"] and e.get("day") == w.d and e["kind"] in ("death", "birth", "raid", "fire", "fight", "alarm"):
                m.append(e["text"])
        w.s["mind"][name]["childhood"] = m[-12:]


# ---------------------------------------------------------------------- death: succession and inheritance (D2-143)
def on_death(w, person) -> None:
    """The head's succession by the household's rules: the named heir; else the eldest adult for now, while the adult members have 2
    days to name a head; the dead's own claims pass by the inheritance rule (eldest, partible, household)."""
    for iid, h in w.s["institutions"].items():
        if h.get("kind") != "household":
            continue
        if h["offices"].get("head") == person:
            heir = h.get("heir")
            if heir in w.s["people"] and w.s["people"][heir]["alive"] and w.household_of(heir) == iid and heir != person:
                h["offices"]["head"] = heir
            else:
                h["offices"]["head"] = w._eldest([m for m in w.members(iid) if m != person])
                h["succession"] = {"until": w.d + int(LIFE["succession_days"]), "named": {}}
        if h.get("heir") == person:
            h["heir"] = None
    hh = w.household_of(person)
    rule = ((w.s["institutions"].get(hh) or {}).get("rules") or {}).get("inheritance", "household")
    kids = sorted([n for n, x in w.s["people"].items() if x["alive"] and person in (x.get("parents") or []) and x["stage"] in ("adult", "elder", "youth")],
                  key=lambda n: w.s["people"][n].get("born") or 0)
    for cid, c in list(w.s["claims"].items()):
        if c["claimant"] != person or (c.get("until") is not None and c["until"] < w.d):
            continue
        if rule == "eldest" and kids:
            heirs = kids[:1]
        elif rule == "partible" and kids:
            heirs = kids
        else:
            heirs = [hh] if hh else kids[:1]
        for x in heirs:
            w._claim(tuple(c["thing"]), x, c["rights"], "inherited", by=person)
        c["until"] = w.d - 1
