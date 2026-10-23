"""What each agent knows how to do (docs/cybertron2/proposals/knowledge.md): technique records with four levels, the paths by which
they rise, recipe cards by level, today's options with near misses, and refusals that name the shortfall.

w.s["know"][agent][tech] = {level: aware|rough|capable|known, skill (0.5 novice .. 2 master), seen (sightings), wins, fails,
source (how it came to know), since (day)}. Basic techniques (data.TECHNIQUES basic) are known by everyone and need no record.

Moving up (counts proposed in knowledge.md §4c):
    told of it / read of it            -> aware
    seen done 3 times (watching: x2)   -> rough
    explained by someone who knows it  -> rough
    taught (one session)               -> capable (a youth: known); skill += share x (teacher's - learner's), x2 for a youth
    trying: 2 successes per level (a failure counts half) from rough to capable to known
"""
from __future__ import annotations

from cybertron2.m1.data import ITEMS, LEVELS, SKILL_WORDS, TECHNIQUES, TRY

ALIASES = {
    "hunt": ["hunt", "hunting"], "fell": ["fell", "felling", "chop timber"], "fish": ["fish", "fishing"],
    "reap": ["reap", "reaping", "harvest"], "bread": ["bread", "baking", "bake"], "pottage": ["pottage", "stew"],
    "pot": ["pot", "pots", "pottery", "firing pots"], "basket": ["basket", "baskets", "basketry", "weave"],
    "line": ["fishing line", "line"], "firing pit": ["firing pit", "kiln", "pit"], "club": ["club"],
}


def basic(tech) -> bool:
    return bool(TECHNIQUES[tech].get("basic"))


def rec(w, name, tech) -> dict | None:
    return w.s["know"].setdefault(name, {}).get(tech)


def level(w, name, tech):
    if tech not in TECHNIQUES:
        return None
    if basic(tech):
        return "known"
    r = rec(w, name, tech)
    return r["level"] if r else None


def skill(w, name, tech) -> float:
    r = rec(w, name, tech)
    return float(r.get("skill", 1.0)) if r else 1.0


def skill_word(x) -> str:
    return next(word for lo, word in SKILL_WORDS if x >= lo)


def _set(w, name, tech, lvl, source):
    k = w.s["know"].setdefault(name, {})
    r = k.get(tech)
    if r is None:
        r = k[tech] = {"level": lvl, "skill": 0.6, "seen": 0, "wins": 0, "fails": 0, "source": source, "since": w.d}
        return True
    if LEVELS.index(lvl) > LEVELS.index(r["level"]):
        r["level"] = lvl
        r["since"] = w.d
        if r["level"] in ("rough", "capable") or not r.get("source"):
            r["source"] = source
        return True
    return False


def seed(w, name, spec_agent) -> None:
    """A founder's knowledge from its spec: knows {tech: level | {level, skill}}, aware_of {tech: how it heard of it}."""
    for tech, v in (spec_agent.get("knows") or {}).items():
        if tech not in TECHNIQUES or basic(tech):
            continue
        lvl, sk = (v, 1.0) if isinstance(v, str) else (v.get("level", "known"), float(v.get("skill", 1.0)))
        w.s["know"].setdefault(name, {})[tech] = {"level": lvl, "skill": sk, "seen": 0, "wins": 0, "fails": 0,
                                                 "source": "from your upbringing", "since": -1}
    for tech, src in (spec_agent.get("aware_of") or {}).items():
        if tech in TECHNIQUES and not basic(tech):
            w.s["know"].setdefault(name, {}).setdefault(tech, {"level": "aware", "skill": 0.6, "seen": 0, "wins": 0, "fails": 0,
                                                               "source": src, "since": -1})


# ---------------------------------------------------------------------- the paths
def told_of(w, hearer, tech, speaker) -> bool:
    if level(w, hearer, tech) is None:
        return _set(w, hearer, tech, "aware", f"{speaker} told you of it")
    return False


def saw(w, viewer, tech, doer, times=1) -> str | None:
    """A sighting of someone doing a technique. Returns the new level if it rose."""
    if basic(tech) or viewer == doer:
        return None
    k = w.s["know"].setdefault(viewer, {})
    if tech not in k:
        _set(w, viewer, tech, "aware", f"you saw {doer} at it")
    r = k[tech]
    r["seen"] += times
    if r["level"] == "aware" and r["seen"] >= 3:
        _set(w, viewer, tech, "rough", f"you watched {doer} at it")
        return "rough"
    return None


def explained(w, speaker, hearer, tech) -> str:
    if level(w, speaker, tech) != "known":
        return f"you do not know {TECHNIQUES[tech]['label']} well enough to explain it"
    if LEVELS.index(level(w, hearer, tech) or "aware") >= LEVELS.index("rough"):
        return f"{hearer} already has an idea of it"
    _set(w, hearer, tech, "rough", f"{speaker} explained it to you")
    return ""


def taught(w, teacher, learner, tech) -> str:
    """One teaching session: the learner to capable (a youth to known), and a share of the skill gap."""
    youth = w.s["agents"][learner]["stage"] == "youth"
    target = "known" if youth else "capable"
    before = level(w, learner, tech)
    _set(w, learner, tech, target, f"{teacher} taught you")
    r = rec(w, learner, tech)
    gap = skill(w, teacher, tech) - r["skill"]
    if gap > 0:
        r["skill"] = round(r["skill"] + float(w.p["teach"]["skill_share"]) * gap * (2 if youth else 1), 3)
    return f"{before or 'nothing'} -> {r['level']}"


def tried(w, name, tech, success) -> str | None:
    """Practice and trying: successes raise skill and, below known, the level (2 per level; 2 failures count as 1)."""
    if basic(tech):
        return None
    r = rec(w, name, tech)
    if r is None:
        return None
    youth = w.s["agents"][name]["stage"] == "youth"
    if success:
        r["wins"] += 1
        r["skill"] = round(min(2.0, r["skill"] + 0.05 * (2 if youth else 1)), 3)
    else:
        r["fails"] += 1
    progress = r["wins"] + r["fails"] // 2
    if r["level"] in ("rough", "capable") and progress >= 2:
        nxt = LEVELS[LEVELS.index(r["level"]) + 1]
        r["wins"], r["fails"] = 0, 0
        _set(w, name, tech, nxt, "your own practice")
        return nxt
    return None


def mentions(w, speaker, hearers, text) -> list:
    """The mention rule: a technique named in speech makes every hearer who did not know of it aware of it (if the speaker
    knows of it). Returns [(hearer, tech)]."""
    low = f" {str(text).lower()} "
    out = []
    for tech, names in ALIASES.items():
        if level(w, speaker, tech) is None:
            continue
        if any(f" {n}" in low or f"{n} " in low for n in names):
            for h in hearers:
                if h != speaker and told_of(w, h, tech, speaker):
                    out.append((h, tech))
    return out


def resolve(x):
    """A technique from what an agent wrote ("pots", "baking", "firing pit")."""
    x = str(x or "").strip().lower()
    if x in TECHNIQUES:
        return x
    for tech, names in ALIASES.items():
        if x in names:
            return tech
    for tech, t in TECHNIQUES.items():
        if x and (x in t["label"].lower() or t["label"].lower().startswith(x)):
            return tech
    for tech, names in ALIASES.items():                                  # a description that names the craft ("Pottage: boil...")
        if any(x.startswith(n) for n in names):
            return tech
    return None


# ---------------------------------------------------------------------- needs, cards, options
def _where(w, name, tech):
    """The places this technique can be done for this agent, as (kind, id, label)."""
    at = TECHNIQUES[tech]["needs"].get("at")
    if not at:
        return [("anywhere", None, "anywhere")]
    out = []
    for a in at:
        if a == "house":
            h = w.home(name)
            if h is not None:
                out.append(("house", w.s["agents"][name]["house"], h["name"]))
        elif a in ("firing pit",):
            for f in w.fittings_at(a):
                out.append(("fitting", f["parcel"], f.get("name") or a))
        else:
            for pid, p in w.parcels().items():
                if p["cover"] == a:
                    out.append(("parcel", pid, p["name"]))
    return out


def shortfall(w, name, tech, mult=1.0, at=None) -> str:
    """'' if the technique can be done now by this agent (at `at`, a parcel id, if given), else what is short."""
    t = TECHNIQUES[tech]
    nd = t["needs"]
    a = w.s["agents"][name]
    where = _where(w, name, tech)
    if not where:
        need = nd.get("at", [])
        return f"there is no {' or '.join(need)} here" if need != ["house"] else "you have no house"
    if at is not None and nd.get("at") and nd["at"] != ["house"]:
        if not any(x[1] == at for x in where):
            names = ", ".join(x[2] for x in where)
            return f"{tech} is done at {names}, not there"
    for tool in nd.get("tools", []):
        if a["holdings"].get(tool, 0.0) < 1 - 1e-9:
            return f"you need {'an' if tool[0] in 'aeiou' else 'a'} {tool}; you have none"
    for item, q in (nd.get("inputs") or {}).items():
        need = round(q * mult, 2)
        have = a["holdings"].get(item, 0.0)
        if have + 1e-9 < need:
            return f"it needs {need:g} {item}; you carry {have:.1f}"
    if nd.get("crop") == "ripe":
        pids = [at] if at else [x[1] for x in where]
        if not any(_crop_ripe(w, pid) for pid in pids):
            return "no crop there is ripe"
    if nd.get("crop") == "reaped":
        pids = [at] if at else [x[1] for x in where]
        if not any(_gleanable(w, pid) for pid in pids):
            return "no field here has been reaped, so there is nothing to glean" if not at else "that field has not been reaped, or is gleaned bare"
    return ""


def _gleanable(w, pid) -> bool:
    c = w.parcels()[pid]["state"].get("crop")
    return bool(c) and bool(c.get("reaped")) and float(c.get("gleanings", 0)) > 0.05


def _crop_ripe(w, pid) -> bool:
    c = w.parcels()[pid]["state"].get("crop")
    return bool(c) and w.d >= int(c.get("ripe_day", 0)) and float(c.get("left", 0)) > 1e-9


def card(w, name, tech) -> str:
    """What the agent is told about a technique, by its level."""
    t = TECHNIQUES[tech]
    lvl = level(w, name, tech)
    nd = t["needs"]
    places = ", ".join(sorted({x[2] for x in _where(w, name, tech)})) or "nowhere you know here"
    if lvl is None:
        return f"{t['label']}: you know nothing of it"
    r = rec(w, name, tech)
    src = f" ({r['source']})" if r and r.get("source") else ""
    if lvl == "aware":
        return f"{t['label']}: you know of it{src}, but not how it is done"
    if lvl == "rough":
        ins = ", ".join(nd.get("inputs") or {}) or "nothing but the work"
        tools = (", with a " + " and a ".join(nd["tools"])) if nd.get("tools") else ""
        return f"{t['label']}: you have a rough idea{src}: {ins}{tools}, done at {places}. You could try (about half the time it works, and it takes more)"
    ins = ", ".join(f"{q:g} {i}" for i, q in (nd.get("inputs") or {}).items()) or "no materials"
    tools = (", a " + " and a ".join(nd["tools"])) if nd.get("tools") else ""
    gives = t["gives"] if isinstance(t["gives"], str) else ", ".join(f"{q:g} {i}" for i, q in t["gives"].items())
    line = f"{t['label']} (`{t['verb']} {tech}`): {ins}{tools}, at {places}; {t['units']} units; gives {gives}"
    if lvl == "capable":
        line += f". At your level you use about {TRY['capable']['inputs']:g} times the materials and it works about 3 times in 4"
    return line


def crafts_lines(w, name) -> list:
    """For the system prompt: what it knows, has a rough idea of, and knows of."""
    k = w.s["know"].get(name, {})
    known = [f"{TECHNIQUES[t]['label']} ({skill_word(r['skill'])})" for t, r in sorted(k.items()) if r["level"] == "known"]
    capable = [f"{TECHNIQUES[t]['label']} ({r['source']})" for t, r in sorted(k.items()) if r["level"] == "capable"]
    rough = [f"{TECHNIQUES[t]['label']} ({r['source']})" for t, r in sorted(k.items()) if r["level"] == "rough"]
    aware = [f"{TECHNIQUES[t]['label']} ({r['source']})" for t, r in sorted(k.items()) if r["level"] == "aware"]
    basics = ", ".join(TECHNIQUES[t]["label"].split(" (")[0] for t in TECHNIQUES if basic(t))
    out = [f"- Everyone here knows: {basics}."]
    if known:
        out.append("- You know: " + "; ".join(known) + ".")
    if capable:
        out.append("- You are capable of (not yet sure of hand): " + "; ".join(capable) + ".")
    if rough:
        out.append("- You have a rough idea of: " + "; ".join(rough) + ". You could try these, at a cost in materials and a risk of failing.")
    if aware:
        out.append("- You know of, but not how: " + "; ".join(aware) + ".")
    return out


def options(w, name, limit=8) -> list:
    """Today's options: techniques it can do now, and near misses."""
    can, near = [], []
    for tech, t in TECHNIQUES.items():
        lvl = level(w, name, tech)
        if lvl not in ("rough", "capable", "known") or tech == "repair":
            continue
        mult = TRY[lvl]["inputs"]
        why = shortfall(w, name, tech, mult)
        places = ", ".join(sorted({x[2] for x in _where(w, name, tech) if (tech != "reap" or _crop_ripe(w, x[1]))
                                   and (tech != "glean" or _gleanable(w, x[1]))}))
        verb = t["verb"]
        tag = "" if lvl == "known" else (" (a try)" if lvl == "rough" else " (not yet sure of hand)")
        if not why:
            can.append(f"{verb} {tech}{tag} at {places} ({t['units']} units)")
        elif len(near) < 4 and not why.startswith("there is no"):
            near.append(f"{verb} {tech}{tag}, but {why}")
    h = w.home(name)
    if h is not None and h["condition"] < 2:
        can.append(f"work repair at {h['name']} (2 timber, 2 units)")
    return can[:limit], near[:4]
