"""Perception (proposals/seeing.md; information/signs.md; D4-35): facts produced from what is at the agent's node (`Here`) and today's
events there, by the data's words for each kind of thing; the daily notice (the most salient facts, each with a chance by salience x
relevance), attending (one target a day, in detail), what concerned you, a glimpse of others, being watched, sightings that teach,
memory, beliefs and notes. Knowledge of other places and of kin lives in the Mind, seeded (D4-21) and changed by being there.

A fact: {id, about: [subject keys], sense, text, salience, tags, concerns, skill?, tech?, actor?}. Subjects: "person:<name>",
"building:<id>", "parcel:<id>", "herd:<id>", "sky".

Mind store (w.s["mind"][name]): days, seeded, lasting, own, beliefs, today, log, kin {name: {rel, lives, alive, seen}},
places {node: {name, days, text, seen}}.
"""
from __future__ import annotations

from cybertron2.engine import knowledge as KN
from cybertron2.engine.data import COVERS, EDIBLE, FITTINGS, ITEMS, RESOURCES, TECHNIQUES
from cybertron2.engine.here import Here, Mind

NOTICE_MAX = 5
ATTEND_MAX = 9
SALIENT = 0.8
WORDS_STAGE = {0: "looks well enough fed", -1: "looks drawn and hungry", -2: "is gaunt and unsteady on their feet"}
ROUTINE = ("work", "make", "store", "take", "give", "trade", "teach", "build")


def store(w, name) -> dict:
    return w.s["mind"][name]


def _blank() -> dict:
    return {"dawn": [], "notice": [], "attended": None, "concerned": [], "glimpse": [], "felt": [], "learned": [], "heard": []}


def _amount(q) -> str:
    return "none" if q < 0.05 else ("a little" if q < 1.5 else ("some" if q < 4 else ("plenty" if q < 10 else "a great deal")))


# ---------------------------------------------------------------------- seeding the mind (D4-21: from one's own position)
def seed(w, name, spec_agent) -> None:
    w.s["mind"][name] = {"days": [], "seeded": list(spec_agent.get("memories") or []), "lasting": [], "own": [], "beliefs": {},
                         "today": _blank(), "log": [], "kin": {}, "places": {}}
    a = w.s["people"][name]
    a["notes"] = {str(k)[:60]: str(v) for k, v in (spec_agent.get("notes") or {}).items()}
    a["pinned"] = spec_agent.get("pinned")
    tags = set(spec_agent.get("interests") or [])
    for tech in (spec_agent.get("knows") or {}):
        if tech in TECHNIQUES:
            tags.update(TECHNIQUES[tech]["tags"])
    a["interests"] = sorted(tags)


def seed_knowledge(w) -> None:
    """After everyone exists: where one's kin live, and the places one knows of (their roads and repute), as of the start."""
    from cybertron2.engine.here import NodeView
    views = {nid: NodeView(w, nid) for nid in w.s["nodes"]}
    texts = {nid: describe(v) for nid, v in views.items()}
    for name, a in w.s["people"].items():
        m = w.s["mind"][name]
        for x, rel in a["relations"].items():
            if x not in w.s["people"]:
                continue
            hh = w.household_of(x)
            homes = w.homes(x)
            lives = f"{w.s['buildings'][homes[0]]['name']}, {w.s['nodes'][w.s['buildings'][homes[0]]['node']]['name']}" if homes else "no house"
            m["kin"][x] = {"rel": rel, "lives": lives, "household": hh, "alive": True, "seen": None}
        home = next((w.s["buildings"][b]["node"] for b in w.homes(name)), a["at"])
        for c in w.spec.get("customs") or []:                                   # seeded custom (D2-30: markets), as local knowledge
            if c.get("nodes") in (None, "all") or home in c["nodes"]:
                m["seeded"].append(c["text"])
        dist = {home: 0}
        todo = [home]
        hidden = {nid for nid, n in w.s["nodes"].items() if n.get("unexplored") and nid != home}     # D4-47
        while todo:
            x = todo.pop(0)
            for r in w.s["roads"].values():
                if x in (r["a"], r["b"]):
                    y = r["b"] if r["a"] == x else r["a"]
                    if y not in hidden and (y not in dist or dist[x] + r["days"] < dist[y]):
                        dist[y] = dist[x] + r["days"]
                        todo.append(y)
        for nid, n in w.s["nodes"].items():
            if nid in hidden:
                continue
            m["places"][nid] = place_record(w, views[nid], nid, dist.get(nid), texts[nid], None if nid != home else -1, hidden)


def place_record(w, view, nid, days, text, seen, hidden=()) -> dict:
    """What one knows of a place: its roads (an unexplored one by its way, D4-47), what it is like, and what is there."""
    ways = sorted(((r.get("way", "an unexplored way") if (r["b"] if r["a"] == nid else r["a"]) in hidden
                    else w.s["nodes"][r["b"] if r["a"] == nid else r["a"]]["name"]), r["days"], r.get("track", False))
                  for r in w.s["roads"].values() if nid in (r["a"], r["b"]))
    return {"name": w.s["nodes"][nid]["name"], "days": days, "ways": ways, "text": text, "seen": seen,
            "buildings": sorted(b["name"] for b in view.buildings().values()),
            "parcels": sorted(p["name"] for p in view.parcels().values()),
            "herds": sorted(h["name"] for h in view.herds().values())}


def describe(view) -> str:
    """A node in one line, from what is there (a view of that node): houses and households, land and what it gives, fittings, herds,
    and the crafts of the lines born there (its repute, D4-33)."""
    bs = view.buildings()
    houses = [b for b in bs.values() if b["fittings"].get("beds") and not b.get("unfinished")]
    holds = sorted({view.household_name(bid) for bid in bs if view.household_name(bid)})
    bits = [f"{len(houses)} house{'s' if len(houses) != 1 else ''}" + (f" ({', '.join(holds)})" if holds else "")]
    land = []
    for cover, cv in COVERS.items():
        here = [p for p in view.parcels().values() if p["cover"] == cover]
        if not here or cover == "built":
            continue
        gives = sorted({k for p in here for k in p["res"] if k in ("game", "seam", "quarry")} | {p["crop"]["kind"] for p in here if p.get("crop")})
        words = {"game": "game", "seam": "a copper seam", "quarry": "stone"}
        size = sum(p["size"] for p in here)
        land.append(("much " if size >= 6 else "") + cv["words"] + (f" ({', '.join(words.get(g, g) for g in gives)})" if gives else ""))
    if land:
        bits.append(", ".join(land))
    fits = sorted({f for b in bs.values() for f in b["fittings"] if f in ("anvil", "cellar")})
    if fits:
        bits.append(", ".join(FITTINGS[f]["label"] for f in fits))
    herds = [h for h in view.herds().values() if h["count"] > 0]
    if herds:
        from cybertron2.engine import farm as FM
        bits.append(", ".join(f"{h['kind']} ({FM.herd_words(h)})" for h in herds))
    trades = view.born_trades()
    if trades:
        bits.append("its people know " + ", ".join(sorted(KN.label(t) for t in trades)))
    return "; ".join(bits) + "."


# ---------------------------------------------------------------------- facts at a node
def facts(here) -> list:
    out = []
    n = [0]

    def add(about, text, salience, tags=(), sense="sight", concerns=(), **kw):
        if not text:
            return
        n[0] += 1
        f = {"id": f"F{here.day}.{here.node}.{n[0]}", "about": list(about), "sense": sense, "text": text, "salience": round(salience, 3),
             "tags": list(tags), "concerns": list(concerns)}
        f.update(kw)
        out.append(f)

    for pid, p in here.parcels().items():
        nm, sub = p["name"], f"parcel:{pid}"
        for sense, tpl, sal in COVERS[p["cover"]]["ambient"]:
            add([sub], tpl.format(name=nm), sal, ["place"], sense, ambient=True)
    from cybertron2.engine import signs as SG                                  # fields, pastures and herds: bundles of signs
    SG.facts(here, add)
    for cid, c in here.remains().items():
        goods = ", ".join(f"{_amount(q)} {i}" for i, q in c["goods"].items() if q > 0.05)
        add(["sky"], f"what {c['of']} carried lies where they died: {goods}", 0.7, ["death", "food"])
    for e in here.events():
        if e["kind"] == "speech":
            continue
        about = list(e.get("about") or [])
        if e.get("actor"):
            about.insert(0, f"person:{e['actor']}")
        if e.get("target"):
            about.append(f"person:{e['target']}")
        add(about or ["sky"], e["text"], e["salience"], e["tags"], e.get("sense", "sight"), e.get("concerns", []), event=e["id"],
            actor=e.get("actor"), tech=e.get("tech"), kind=e["kind"], dawn=e.get("dawn", False))
    return out


def relevance(here, mind, f) -> float:
    r = 0.0
    if mind.name in f["concerns"]:
        r += 1.0
    homes = {f"building:{b}" for b in here.homes_here()}
    if any(s in homes or (s.startswith("person:") and s[7:] in mind.members) for s in f["about"]):
        r += 0.5
    a = mind.person
    if set(f["tags"]) & set(a.get("interests", [])):
        r += 0.5
    if a["hunger"] < 0 and "food" in f["tags"]:
        r += 0.4
    if set(f["tags"]) & set(a.get("concerns", [])):
        r += 0.4
    if "danger" in f["tags"]:
        r += 0.3
    return min(1.0, r)


def knack(mind, f) -> float:
    """A sign with a knack is read twice as often by one practised at that work, half as often by one who is not (signs.py)."""
    k = f.get("knack")
    if not k or k not in TECHNIQUES:
        return 1.0
    r = mind.know.get(k)
    lo = KN.curve(k)[0]
    if r and (r.get("level") == "known" and (not KN.basic(k) or float(r.get("skill", lo)) >= lo + 0.05)):
        return 2.0
    return 1.0 if KN.basic(k) else 0.5                                        # ordinary hands read basic work's signs as usual


def _can_read(mind, f) -> bool:
    sk = f.get("skill")
    return not sk or sk in mind.person.get("interests", [])


# ---------------------------------------------------------------------- dawn and evening
def dawn(w) -> None:
    """What each agent meets this morning at its node: dawn incidents and signs (concerns always; salient always; the rest by
    salience x relevance)."""
    for name in w.agents_acting():
        here, mind = Here(w, name), Mind(w, name)
        rng = here.rng("dawn", here.day, name)
        t = mind.store["today"]
        for e in [e for e in here.events() if e.get("dawn")]:
            f = {"concerns": e.get("concerns", []), "about": e.get("about") or ["sky"], "tags": e["tags"]}
            p = 1.0 if name in f["concerns"] or e["salience"] >= SALIENT else min(1.0, e["salience"] * (0.3 + relevance(here, mind, f)))
            if rng.random() < p:
                t["dawn"].append(e["text"])
                mind.store["log"].append({"day": here.day, "dawn": [e["id"]]})


def evening(w, attend: dict, today: dict) -> dict:
    """Perception after the day's work, each at its node."""
    living = w.agents_acting()
    by_node, logs = {}, {}
    for name in w.living():
        m = store(w, name)
        m["today"] = {**_blank(), "heard": m["today"].get("heard", []), "dawn": m["today"].get("dawn", [])}
    watchers = {}
    for name in living:
        here = Here(w, name)
        who = here.person(today["watch"].get(name) or attend.get(name))
        if who and who != name:
            watchers.setdefault(who, []).append(name)
    for name in living:
        here, mind = Here(w, name), Mind(w, name)
        if here.node not in by_node:
            by_node[here.node] = facts(here)
        F = by_node[here.node]
        t = mind.store["today"]
        rng = here.rng("notice", here.day, name)
        tgt_raw = today["watch"].get(name) or attend.get(name)
        subject, label = resolve_target(here, tgt_raw)
        place = subject == "place"
        con = [f for f in F if name in f["concerns"] and f.get("event") and f.get("actor") != name]
        t["concerned"] = [f["text"] for f in con]
        seen = {f["id"] for f in con}
        homes = {f"building:{b}" for b in here.homes_here()}
        cand = []
        for f in F:
            if f["id"] in seen or f.get("actor") == name or f.get("peek") or f.get("ambient") or not _can_read(mind, f):
                continue
            if f.get("dawn") and f["text"] in t["dawn"]:
                continue
            if homes & set(f["about"]) and not f.get("event"):
                continue
            if f["salience"] < 0.2 and name not in f["concerns"]:
                continue
            if f.get("kind") in ROUTINE or (f["about"] and f["about"][0] == f"person:{name}"):
                continue
            rel = relevance(here, mind, f)
            p = 1.0 if f["salience"] >= SALIENT else min(1.0, f["salience"] * (0.3 + rel) * (1.8 if place else 1.0) * knack(mind, f))
            if rng.random() < p:
                cand.append((f["salience"] + rel, f))
        cand.sort(key=lambda x: -x[0])
        notice = [f for _, f in cand[:NOTICE_MAX + (2 if place else 0)]]
        t["notice"] = [f["text"] for f in notice]
        seen |= {f["id"] for f in notice}
        att = []
        if place:
            amb = [f for f in F if f.get("ambient")]
            rng.shuffle(amb)
            att = amb[:4]
        elif subject:
            pool = [f for f in F if subject in f["about"] and f["id"] not in seen and f.get("actor") != name and _can_read(mind, f)
                    and (not f.get("peek") or subject.startswith("building:"))]
            pool.sort(key=lambda f: -(f["salience"] + relevance(here, mind, f)))
            texts = set()
            for f in pool:
                if f["text"] not in texts and len(att) < ATTEND_MAX:
                    att.append(f)
                    texts.add(f["text"])
        if subject or place:
            t["attended"] = {"target": label, "lines": [f["text"] for f in att] or ["nothing out of the ordinary"]}
        seen |= {f["id"] for f in att}
        others = [x for x in here.people(me=False) if x in living and f"person:{x}" != subject]
        kin = [x for x in others if x in mind.members]
        rest = [x for x in others if x not in kin]
        rng.shuffle(rest)
        for x in (kin + rest)[:int(here.p["glimpse"])]:
            pl = today["worked"].get(x)
            if pl:
                spot = here.parcels().get(pl[-1]) or here.buildings().get(pl[-1])
                t["glimpse"].append(f"{x} spent the day at {spot['name']}" if spot else f"{x} was about the place")
            elif today["watch"].get(x):
                t["glimpse"].append(f"{x} spent the day at {today['watch'][x]}'s side")
            else:
                t["glimpse"].append(f"{x} was about the houses")
        for v in watchers.get(name, []):
            mutual = str(today["watch"].get(name) or attend.get(name) or "").lower() == v.lower()
            if today["watch"].get(v) == name or here.rng("felt", here.day, name, v).random() < float(here.p["felt_watched"]) * (2 if mutual else 1):
                t["felt"].append(f"You had the feeling {v} was watching you today" if today["watch"].get(v) != name
                                 else f"{v} spent the day at your side, watching how you work")
        times = {}
        doer = here.person(tgt_raw) if tgt_raw else None
        for f in F:
            tech, actor = f.get("tech"), f.get("actor")
            if not tech or not actor or actor == name or tech not in TECHNIQUES or KN.basic(tech):
                continue
            k = 0
            if doer == actor:
                k = 2 if today["watch"].get(name) == actor else 1
            elif f.get("kind") == "work" and any(s[7:] in today["worked"].get(name, []) for s in f["about"] if s.startswith("parcel:")):
                k = 1
            if k:
                times[(tech, actor)] = max(times.get((tech, actor), 0), k)
        for (tech, actor), k in times.items():
            before = KN.level(mind, tech)
            rose = KN.saw(here, mind, tech, actor, k)
            if before is None:
                t["learned"].append(f"You saw {actor} at {KN.label(tech)}, which you had not seen done before.")
            if rose:
                t["learned"].append(f"From watching {actor} you now have a rough idea of {KN.label(tech)}.")
        for f in con + notice + att:
            for sub in f["about"]:
                b = mind.store["beliefs"].setdefault(sub, {"day": here.day, "lines": [], "ids": []})
                if b["day"] != here.day:
                    b.update(day=here.day, lines=[], ids=[])
                if f["id"] not in b["ids"]:
                    b["ids"].append(f["id"])
                    b["lines"].append(f["text"])
        _update_known(here, mind, F)
        logs[name] = {"notice": [f["id"] for f in notice], "attended": [f["id"] for f in att], "concerned": [f["id"] for f in con],
                      "target": label}
        mind.store["log"].append({"day": here.day, **logs[name]})
    return {"facts": by_node, "agents": logs}


def _update_known(here, mind, F) -> None:
    """Being somewhere updates what one knows of it and of the people one meets there (D4-35: only by being there)."""
    pl = mind.store["places"].get(here.node)
    if pl is None:                                                              # a place found (D4-47)
        mind.store["places"][here.node] = pl = {"name": here.node_name, "days": None, "ways": [], "text": "", "seen": here.day,
                                                "buildings": [], "parcels": [], "herds": [], "found": here.day}
    if pl is not None:
        pl["ways"] = sorted((n, d, t) for _, n, d, t in here.roads())
        pl.update(text=describe(here), seen=here.day, buildings=sorted(b["name"] for b in here.buildings().values()),
                  parcels=sorted(p["name"] for p in here.parcels().values()), herds=sorted(h["name"] for h in here.herds().values()))
    for x in here.people(me=False):
        k = mind.store["kin"].get(x)
        if k:
            k.update(seen=here.day, seen_at=here.node_name)
    for f in F:
        if f.get("kind") == "death":
            dead = next((s[7:] for s in f["about"] if s.startswith("person:") and s[7:] != f.get("actor")), None)
            if dead and dead in mind.store["kin"]:
                mind.store["kin"][dead]["alive"] = False


def resolve_target(here, x):
    if not x:
        return None, None
    s = str(x).strip()
    low = s.lower()
    if low in ("place", "the place", "the place in general", "everything", "general", "around", "the village", "the hamlet"):
        return "place", "the place in general"
    if low in ("sky", "the sky", "weather", "the weather", "the land and sky", "the land", "the sky and the weather"):
        return "sky", "the land and sky"
    who = here.person(s)
    if who and who != here.name:
        return f"person:{who}", who
    bid = here.building(s)
    if bid:
        return f"building:{bid}", here.buildings()[bid]["name"]
    pid = here.parcel(s)
    if pid:
        return f"parcel:{pid}", here.parcels()[pid]["name"]
    hid = here.herd(s)
    if hid and s:
        return f"herd:{hid}", here.herds()[hid]["name"]
    return "place", f"the place in general (you could not find {s!r} to attend to)"


# ---------------------------------------------------------------------- memory
SPEECH = ("You told ", "You said", "You noted", "You let go of the note")
DIRECT = "(to you) "
OWN_MAX = 6


def own_memory(w, name, span, text) -> None:
    m = store(w, name)
    m["own"] = (m.get("own", []) + [{"span": span, "day": w.d, "text": " ".join(str(text).split()[:150])}])[-OWN_MAX:]


def close_day(w, name, did: list, night_lines: list) -> None:
    m = store(w, name)
    t = m["today"]
    saw = t["dawn"] + t["concerned"] + t["notice"] + t["felt"] + t["learned"]
    if t["attended"]:
        saw.append(f"(attending to {t['attended']['target']}) " + "; ".join(t["attended"]["lines"]))
    acts = [x for x in did if not x.startswith(SPEECH)]
    said = [x.removeprefix("You ") for x in did if x.startswith(("You told ", "You said "))]
    m["days"].append({"day": w.d, "did": acts + night_lines, "said": said, "heard": list(t["heard"]), "saw": saw, "glimpse": list(t["glimpse"])})
    for line in t["concerned"] + t["learned"] + night_lines:
        low = line.lower()
        if any(k in low for k in ("killed", "died", "beat", "broken into", "taught you", "missed meal", "gave", "missing", "slipped into",
                                  "now have a rough idea", "starving", "taken into", "claimed")):
            m["lasting"].append(f"{_day(w, w.d)}: {line}")
    m["lasting"] = m["lasting"][-14:]
    t["heard"], t["dawn"] = [], []


def _day(w, d) -> str:
    c = w.calendar(d)
    return f"{c['season']} day {c['day']}"


def beliefs_lines(mind, names, limit=6) -> list:
    """What it last perceived of people and buildings it did not see today, dated. names: subject -> label (from its own view)."""
    out, said = [], set()
    for sub, b in sorted(mind.store["beliefs"].items(), key=lambda kv: -kv[1]["day"]):
        if b["day"] >= mind.day - 1 or not sub.startswith(("person:", "building:")) or sub == f"person:{mind.name}":
            continue
        lines = [x for x in b["lines"] if x not in said][:3]
        said.update(lines)
        if not lines:
            continue
        label = names.get(sub, sub.split(":", 1)[1])
        out.append(f"{label}, {mind.day - b['day']} days ago: " + "; ".join(lines))
        if len(out) >= limit:
            break
    return out


def apply_notes(mind, reply) -> list:
    """note [{title, text}], pin title, forget [titles]. Free. A note is the agent's own memory."""
    notes = mind.notes
    nt = mind.p["notes"]
    out = []
    for n in reply.get("note") or []:
        if not isinstance(n, dict) or not n.get("title"):
            continue
        title = str(n["title"]).strip()[:60]
        text = " ".join(str(n.get("text", "")).split()[: int(nt["words"])])
        if title not in notes and len(notes) >= int(nt["max"]):
            out.append(f"Refused: note: you already keep {nt['max']} notes; forget one first")
            continue
        notes[title] = text
        out.append(f"You noted “{title}”.")
    for title in reply.get("forget") or []:
        if notes.pop(str(title), None) is not None:
            out.append(f"You let go of the note “{title}”.")
            if mind.person["pinned"] == title:
                mind.person["pinned"] = None
    pin = reply.get("pin")
    if str(pin).strip().lower() in ("none", "null", ""):
        pin = None
    written = [str(n["title"]).strip()[:60] for n in (reply.get("note") or []) if isinstance(n, dict) and n.get("title")]
    if pin and str(pin) not in notes and len(written) == 1 and written[0] in notes:
        pin = written[0]
    if pin:
        if str(pin) in notes:
            mind.person["pinned"] = str(pin)
        else:
            out.append(f"Refused: pin: you have no note called “{pin}”")
    return out
