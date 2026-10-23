"""What each person knows how to do (proposals/knowledge.md; D4-24, D4-33): technique records with four levels, how they rise,
cards by level, today's options with near misses, and refusals that name the shortfall.

Mind.know[tech] = {level: aware|rough|capable|known, skill, seen, wins, fails, source, since}. Basic techniques need no record.
The views take `Here` and `Mind` only (D4-35); changing a level goes through the `learn` primitive.
"""
from __future__ import annotations

from cybertron2.engine.data import BLUEPRINTS, FITTINGS, ITEMS, LEVELS, SKILL_WORDS, TECHNIQUES, TRY


def basic(tech) -> bool:
    return bool(TECHNIQUES[tech].get("basic"))


def label(tech) -> str:
    return TECHNIQUES[tech]["label"].split(" (")[0]


def resolve(x):
    """A technique from what an agent wrote: its name, an alias, or a word of its label."""
    x = str(x or "").strip().lower()
    if x in TECHNIQUES:
        return x
    for t, d in TECHNIQUES.items():
        if x in d.get("aliases", []) or x == d["label"].lower() or x == label(t).lower():
            return t
    return None


# ---------------------------------------------------------------------- the store (engine side: seeding and the learn primitive)
def seed(w, name, spec_agent) -> None:
    k = w.s["know"].setdefault(name, {})
    for tech, v in (spec_agent.get("knows") or {}).items():
        if tech in TECHNIQUES and not basic(tech):
            lvl, sk = (v, 1.0) if isinstance(v, str) else (v.get("level", "known"), float(v.get("skill", 1.0)))
            k[tech] = {"level": lvl, "skill": sk, "seen": 0, "wins": 0, "fails": 0, "source": "from your upbringing", "since": -1}
    for tech, src in (spec_agent.get("aware_of") or {}).items():
        if tech in TECHNIQUES and not basic(tech):
            k.setdefault(tech, {"level": "aware", "skill": 0.6, "seen": 0, "wins": 0, "fails": 0, "source": src, "since": -1})


def _set(w, name, tech, lvl, source) -> bool:
    k = w.s["know"].setdefault(name, {})
    r = k.get(tech)
    if r is None:
        k[tech] = {"level": lvl, "skill": 0.6, "seen": 0, "wins": 0, "fails": 0, "source": source, "since": w.d}
        return True
    if LEVELS.index(lvl) > LEVELS.index(r["level"]):
        r.update(level=lvl, since=w.d, source=source)
        return True
    return False


# ---------------------------------------------------------------------- views
def rec(mind, tech):
    return mind.know.get(tech)


def level(mind, tech):
    if tech not in TECHNIQUES:
        return None
    if basic(tech):
        return "known"
    r = rec(mind, tech)
    return r["level"] if r else None


def skill(mind, tech) -> float:
    r = rec(mind, tech)
    return float(r.get("skill", 1.0)) if r else 1.0


def skill_word(x) -> str:
    return next(word for lo, word in SKILL_WORDS if x >= lo)


def where(here, tech) -> list:
    """The sites here where a technique can be done: [(kind, id, label)]."""
    at = TECHNIQUES[tech].get("at")
    if not at:
        return [("anywhere", None, "anywhere")]
    out = []
    for c in at.get("covers", []):
        out += [("parcel", pid, p["name"]) for pid, p in here.parcels().items() if p["cover"] == c]
    for f in at.get("fittings", []):
        out += [("building", bid, here.buildings()[bid]["name"]) for bid in here.fittings(f)]
    if at.get("building"):
        out += [("building", bid, b["name"]) for bid, b in here.buildings().items() if not b.get("unfinished")]
    return out


def ready(here, tech, kind, key) -> str:
    """'' if the site can be worked by this technique now, else why not (what it draws on, in its state)."""
    t = TECHNIQUES[tech]
    y = (t.get("yield") or {}).get("kind")
    if kind == "parcel":
        p = here.parcels()[key]
        d = t.get("draws")
        if d in ("plants", "game", "wood", "seam", "quarry") and d not in p["res"]:
            return f"there is no {d if d != 'plants' else 'wild food'} at {p['name']}"
        if d in ("seam",) and p["res"][d]["S"] <= 1e-9:
            return f"the seam at {p['name']} is worked out"
        if d == "plants" and p["res"][d]["S"] <= (here.p["refuge"] + 0.02) * p["res"][d]["K"]:
            return f"{p['name']} is picked bare"
        if d == "wood" and p["res"][d]["S"] <= 0.5:
            return f"there is no standing timber left in {p['name']}"
        if y == "sow" and p.get("crop") and p["crop"].get("left", 0) > 1e-9:
            return f"{p['name']} already has a crop in it"
        if y in ("crop", "tend"):
            c = p.get("crop")
            if not c or c.get("left", 0) <= 1e-9:
                return f"there is no crop in {p['name']}"
            if y == "crop" and here.day < int(c.get("ripe_day", 0)):
                return f"the {c.get('kind', 'crop')} in {p['name']} is not ripe yet"
            if y == "tend" and here.day >= int(c.get("ripe_day", 0)):
                return f"the {c.get('kind', 'crop')} in {p['name']} is ripe: past weeding"
            if y == "tend" and c.get("weeded", 0) >= here.p["farming"]["weed_max"] - 1e-9:
                return f"the {c.get('kind', 'crop')} in {p['name']} is as clean as weeding makes it"
        if d == "herd":
            hs = [h for h in here.herds().values() if h["parcel"] == key]
            if not hs:
                return f"there are no beasts on {p['name']}"
            if y == "milk":
                h = hs[0]
                if int(h.get("in_milk", 0)) <= 0:
                    return "no cow there is in milk"
                if h["milked"]["day"] == here.day and h["milked"]["n"] >= int(h["in_milk"]):
                    return f"the cows in milk have all been milked today ({h['in_milk']} of them)"
            if y == "slaughter" and hs[0]["count"] <= 0:
                return "there are no beasts left"
    if kind == "building" and y == "repair" and here.buildings()[key]["condition"] >= 2:
        return f"{here.buildings()[key]['name']} is sound"
    return ""


def available(here, item, who=None, extra=None) -> float:
    """How much of a good one can use here: what one carries and the stores here one may take from (and a party's, acting for it)."""
    cids = here.takeable(who) + ([extra] if extra and extra not in here.takeable(who) else [])
    return sum(here.contents(cid).get(item, 0.0) for cid in cids)          # whose ever they are: hands of `who`, or stores


def shortfall(here, mind, tech, mult=1.0, at=None, extra=None) -> str:
    """'' if the technique can be done here now, else what is short."""
    t = TECHNIQUES[tech]
    sites = where(here, tech)
    if not sites:
        need = t.get("at", {})
        what = need.get("covers") or [FITTINGS[f]["label"] for f in need.get("fittings", [])] or ["building"]
        return f"there is no {' or '.join(what)} here you can use"
    if at is not None and t.get("at"):
        if not any(s[1] == at for s in sites):
            return f"{label(tech)} is done at {', '.join(s[2] for s in sites)}, not there"
        sites = [s for s in sites if s[1] == at]
    if t.get("tools"):
        tool, m = here.best_tool(t["tools"])
        if m is None:
            from cybertron2.engine.data import TOOLS
            near = next((cid for cid in here.takeable() if cid != here.hands and any(here.contents(cid).get(x, 0) >= 1 for x in TOOLS)), None)
            return f"you need a tool in your hands for {label(tech)}" + (
                f"; there is one in {here.buildings()[near[len('stock:'):]]['name']}'s store: take it into your hands (move)" if near else "; you have none")
    for item, q in (t.get("inputs") or {}).items():
        need = round(q * mult, 2)
        have = available(here, item, extra=extra)
        if have + 1e-9 < need:
            return f"it needs {need:g} {item}; you have {have:.1f} to hand"
    if sites[0][0] != "anywhere":
        why = [ready(here, tech, k, key) for k, key, _ in sites]
        if all(why):
            return why[0]
    return ""


def card(here, mind, tech) -> str:
    """What one is told about a technique, by one's level of it."""
    t = TECHNIQUES[tech]
    lvl = level(mind, tech)
    if lvl is None:
        return f"{t['label']}: you know nothing of it"
    r = rec(mind, tech)
    src = f" ({r['source']})" if r and r.get("source") else ""
    places = ", ".join(sorted({x[2] for x in where(here, tech)})) or "nowhere here"
    if lvl == "aware":
        return f"{t['label']}: you know of it{src}, but not how it is done"
    ins = ", ".join(f"{q:g} {i}" for i, q in (t.get("inputs") or {}).items()) or "no materials"
    if lvl == "rough":
        return f"{t['label']}: you have a rough idea{src}: {ins}, done at {places}. You could try (about half the time it works, and it takes more)"
    gives = t["gives"] if isinstance(t["gives"], str) else ", ".join(f"{q:g} {i}" for i, q in t["gives"].items())
    line = f"{t['label']} (`{t['verb']} {tech}`): {ins}, at {places}; {t['units']} units" + (f"; gives {gives}" if gives else "")
    if lvl == "capable":
        line += f". At your level you use about {TRY['capable']['inputs']:g} times the materials and it works about 3 times in 4"
    return line


def crafts_lines(mind) -> list:
    k = mind.know
    known = [f"{TECHNIQUES[t]['label']} ({skill_word(r['skill'])})" for t, r in sorted(k.items()) if r["level"] == "known"]
    capable = [f"{TECHNIQUES[t]['label']} ({r['source']})" for t, r in sorted(k.items()) if r["level"] == "capable"]
    rough = [f"{TECHNIQUES[t]['label']} ({r['source']})" for t, r in sorted(k.items()) if r["level"] == "rough"]
    aware = [f"{TECHNIQUES[t]['label']} ({r['source']})" for t, r in sorted(k.items()) if r["level"] == "aware"]
    basics = ", ".join(label(t) for t in TECHNIQUES if basic(t))
    out = [f"- Everyone knows: {basics}."]
    if known:
        out.append("- You know: " + "; ".join(known) + ".")
    if capable:
        out.append("- You are capable of (not yet sure of hand): " + "; ".join(capable) + ".")
    if rough:
        out.append("- You have a rough idea of: " + "; ".join(rough) + ". You could try these, at a cost in materials and a risk of failing.")
    if aware:
        out.append("- You know of, but not how: " + "; ".join(aware) + ".")
    return out


def options(here, mind, limit=10):
    """Today's options: techniques one could do here now, and near misses."""
    can, near = [], []
    for tech, t in TECHNIQUES.items():
        lvl = level(mind, tech)
        if lvl not in ("rough", "capable", "known") or t["verb"] == "build":
            continue
        why = shortfall(here, mind, tech, TRY[lvl]["inputs"])
        sites = [s for s in where(here, tech) if s[0] == "anywhere" or not ready(here, tech, s[0], s[1])]
        places = ", ".join(sorted({s[2] for s in sites}))
        tag = "" if lvl == "known" else (" (a try)" if lvl == "rough" else " (not yet sure of hand)")
        if not why:
            can.append(f"{t['verb']} {tech}{tag}" + (f" at {places}" if places and places != "anywhere" else "") + f" ({t['units']} units)")
        elif len(near) < 4 and not why.startswith(("there is no", "there are no")):
            near.append(f"{t['verb']} {tech}{tag}, but {why}")
    return can[:limit], near[:4]


def mentions(text) -> list:
    """Techniques named in a text (speech makes one aware of them: knowledge.md)."""
    low = f" {str(text).lower()} "
    out = []
    for tech, t in TECHNIQUES.items():
        if t["verb"] == "build":
            continue
        words = [tech] + t.get("aliases", [])
        if any(f" {x} " in low or f" {x}," in low or f" {x}." in low for x in words):
            out.append(tech)
    return out


# ---------------------------------------------------------------------- rising (through the learn primitive)
def tried(here, mind, tech, ok) -> str:
    """Practice: two successes a level (a failure counts half) from rough to capable to known; skill grows with use."""
    if basic(tech):
        return ""
    r = rec(mind, tech)
    if r is None:
        return ""
    r["wins" if ok else "fails"] = r.get("wins" if ok else "fails", 0) + 1
    if r["level"] == "known":
        r["skill"] = round(min(1.8, r["skill"] + 0.02), 3)
        return ""
    score = r.get("wins", 0) + 0.5 * r.get("fails", 0)
    nxt = {"rough": "capable", "capable": "known"}.get(r["level"])
    if nxt and score >= 2:
        r["wins"] = r["fails"] = 0
        here.apply("learn", person=mind.name, tech=tech, level=nxt, source="from practice")
        return nxt
    return ""


def saw(here, mind, tech, actor, k=1) -> bool:
    """Seeing it done: three sightings (watching counts double) give a rough idea."""
    if basic(tech):
        return False
    r = rec(mind, tech)
    if r is None:
        here.apply("learn", person=mind.name, tech=tech, level="aware", source=f"you saw {actor} at it")
        r = rec(mind, tech)
    r["seen"] = r.get("seen", 0) + k
    if r["level"] == "aware" and r["seen"] >= 3:
        return bool(here.apply("learn", person=mind.name, tech=tech, level="rough", source=f"from watching {actor}"))
    return False
