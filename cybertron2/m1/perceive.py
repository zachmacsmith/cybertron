"""Perception (docs/cybertron2/proposals/seeing.md): facts produced on demand from the state and today's happenings, the daily notice
(the most salient facts, each with a chance by salience x relevance), attending (one target a day, in detail), what concerned you,
a glimpse of the others, being watched, sightings that teach (knowledge.md), memory bands, engine-kept beliefs and notes.

A fact: {id, about: [subject keys], sense, text, salience, tags, concerns, skill?, tech?, actor?}. Subjects: "a:<name>", "h:<house>",
"p:<parcel>", "herd:<id>", "fit:<n>", "sky". Only facts an agent was given go into its store (beliefs), so text and store agree.

w.s["mind"][name] = {
    days        [{day, did, heard, saw}] the closed days, newest last
    lasting     [lines] lasting memories (from the spec and from salient days)
    beliefs     {subject: {day, lines, ids}} what it last perceived of each thing (dated)
    today       {notice, attended, concerned, glimpse, felt, learned, heard}  filled at evening, shown the next morning
    log         [{day, notice, attended, concerned}] fact ids by channel, for the perception log
}
"""
from __future__ import annotations

from cybertron2.m1 import knowledge as KN
from cybertron2.m1.data import COVERS, EDIBLE, ITEMS, TECHNIQUES

NOTICE_MAX = 5
ATTEND_MAX = 9
SALIENT = 0.8
WORDS_STAGE = {0: "looks well enough fed", -1: "looks drawn and hungry", -2: "is gaunt and unsteady on their feet"}
TRADE_TAGS = {"farm": ["farming", "harvest", "food"], "hunt": ["hunting", "animals", "woodland"], "fish": ["water"],
              "pott": ["pottery", "craft"], "herd": ["animals"], "wood": ["timber", "woodland"], "bak": ["cooking", "food"],
              "build": ["building", "shelter"], "weav": ["craft"], "fowl": ["animals", "season"]}


def seed(w, name, spec_agent) -> None:
    w.s["mind"][name] = {"days": [], "seeded": list(spec_agent.get("memories") or []), "lasting": [], "own": [], "beliefs": {},
                         "today": _blank(), "log": []}
    a = w.s["agents"][name]
    a["notes"] = {str(k)[:60]: str(v) for k, v in (spec_agent.get("notes") or {}).items()}
    a["pinned"] = spec_agent.get("pinned")
    tags = set(spec_agent.get("interests") or [])
    trade = str(spec_agent.get("trade", "")).lower()
    for k, v in TRADE_TAGS.items():
        if k in trade:
            tags.update(v)
    for tech in (spec_agent.get("knows") or {}):
        if tech in TECHNIQUES:
            tags.update(TECHNIQUES[tech]["tags"])
    a["interests"] = sorted(tags)


def _blank() -> dict:
    return {"dawn": [], "notice": [], "attended": None, "concerned": [], "glimpse": [], "felt": [], "learned": [], "heard": []}


ROUTINE = ("work", "make", "store", "take", "give", "trade", "teach")


def dawn(w) -> None:
    """What each agent meets this morning: dawn incidents and signs, by the notice rule (concerns always; salient always; the rest
    by salience x relevance)."""
    ev = [e for e in w.s["events"] if e.get("dawn")]
    for name in w.agents_acting():
        rng = w.rng("dawn", w.d, name)
        t = store(w, name)["today"]
        for e in ev:
            f = {"concerns": e.get("concerns", []), "about": [e.get("about") or "sky"], "tags": e["tags"]}
            p = 1.0 if name in f["concerns"] or e["salience"] >= SALIENT else min(1.0, e["salience"] * (0.3 + relevance(w, name, f)))
            if rng.random() < p:
                t["dawn"].append(e["text"])
                store(w, name)["log"].append({"day": w.d, "dawn": [e["id"]]})


def store(w, name) -> dict:
    return w.s["mind"][name]


# ---------------------------------------------------------------------- facts
def _amount(q) -> str:
    return "none" if q < 0.05 else ("a little" if q < 1.5 else ("some" if q < 4 else ("plenty" if q < 10 else "a great deal")))


def facts(w) -> list:
    """Everything the node gives off now, by rule from the state, the sense table and today's happenings."""
    out = []
    n = [0]

    def add(about, text, salience, tags=(), sense="sight", concerns=(), **kw):
        n[0] += 1
        f = {"id": f"F{w.d}.{n[0]}", "about": list(about), "sense": sense, "text": text, "salience": round(salience, 3),
             "tags": list(tags), "concerns": list(concerns)}
        f.update(kw)
        out.append(f)

    s = w.s
    household = {hid: [x for x in w.living() if s["agents"][x]["house"] == hid] for hid in s["houses"]}
    # the sky and the season
    cal = w.calendar()
    if w.cold():
        first = not w.cold(w.d - 1) if w.d > 0 else True
        add(["sky"], "a hard frost lay on everything this morning" if first else "it stayed bitterly cold", 0.85 if first else 0.5,
            ["season", "shelter", "farming"], sense="touch")
    if not w.cold():
        wx = {"spring": "a mild day, showers on the wind", "summer": "a warm, settled day", "autumn": "a cool day, the nights drawing in",
              "winter": "a grey, raw day"}[cal["season"]]
        add(["sky"], wx, 0.05, ["season"])
    if cal["left"] == 0:
        add(["sky"], f"the last days of {cal['season']}: the light is changing", 0.1, ["season"])
    # parcels
    for pid, p in w.parcels().items():
        st, nm = p["state"], p["name"]
        for sense, tpl, sal in COVERS[p["cover"]]["ambient"]:
            add([f"p:{pid}"], tpl.format(name=nm), sal, ["place"], sense, ambient=True)
        c = st.get("crop")
        if c:
            crop = c.get("kind", "crop")
            ripe = w.d >= int(c.get("ripe_day", 0))
            if c.get("left", 0) <= 1e-9:
                add([f"p:{pid}"], f"{nm} is reaped bare" + ("; a little gleaning left in the stubble" if c.get("gleanings", 0) > 0.2 else ""),
                    0.15, ["farming", "food"])
            elif c.get("reaped"):
                add([f"p:{pid}"], f"{nm} is part reaped: sheaves down, the rest of the {crop} standing", 0.25, ["farming", "harvest", "food"])
            elif ripe:
                add([f"p:{pid}"], f"the {crop} in {nm} stands ripe and ready for the sickle", 0.35, ["farming", "harvest", "food"])
            else:
                k = int(c["ripe_day"]) - w.d
                add([f"p:{pid}"], f"the {crop} in {nm} is turning gold", 0.12, ["farming", "harvest"])
                add([f"p:{pid}"], f"you judge the {crop} in {nm} will be fit to reap in about {k} day{'s' if k != 1 else ''}", 0.05,
                    ["farming", "harvest"], skill="farming")
        pl = st.get("plants")
        if pl:
            r = pl["S"] / pl["K"]
            if r < 0.35:
                add([f"p:{pid}"], f"{nm} has been picked over: little wild food left", 0.2, ["food"])
            elif r > 0.75:
                add([f"p:{pid}"], f"{nm} is thick with berries, nuts and greens", 0.1, ["food"])
        g = st.get("game")
        if g:
            r = g["S"] / g["K"]
            add([f"p:{pid}"], f"fresh deer slots and droppings along the rides of {nm}" if r > 0.5 else f"few fresh tracks in {nm}: the game is thin",
                0.05, ["hunting", "animals"], skill="hunting")
        fi = st.get("fish")
        if fi:
            add([f"p:{pid}"], f"fish rising in {nm}" if fi["S"] / fi["K"] > 0.5 else f"{nm} looks fished out", 0.08, ["water", "food"],
                skill="water")
        if st.get("felled"):
            add([f"p:{pid}"], f"fresh stumps and chips in {nm} where trees were felled", 0.12, ["timber", "woodland"])
    # houses and fittings
    for hid, h in s["houses"].items():
        nm, live = h["name"], household[hid]
        cond = {2: "sound", 1: "in poor repair: the thatch slipping, a wall cracked", 0: "a ruin"}[h["condition"]]
        add([f"h:{hid}"], f"{nm} is {cond}", 0.1 if h["condition"] == 2 else 0.4, ["building", "shelter"], concerns=live)
        if live:
            if h["fire"]:
                add([f"h:{hid}"], f"smoke from {nm}'s roof at dawn", 0.08, ["shelter"], sense="smell")
            elif w.cold(w.d - 1 if w.d else 0):
                add([f"h:{hid}"], f"no smoke from {nm}'s roof after a cold night", 0.5, ["shelter", "danger"], concerns=live)
        wood = h["stock"].get("timber", 0.0)
        add([f"h:{hid}"], f"the woodpile by {nm}: {_amount(wood)}", 0.06, ["timber", "shelter"])
        if h["door"] == "barred":
            add([f"h:{hid}"], f"{nm}'s door is barred", 0.3, ["danger"])
        else:
            food = sum(q for i, q in h["stock"].items() if i in EDIBLE)
            goods = ", ".join(f"{_amount(q)} {i}" for i, q in sorted(h["stock"].items()) if q >= 0.5 and i != "timber") or "nothing much"
            add([f"h:{hid}"], f"through {nm}'s open door: {goods}", 0.05, ["food"] if food else [], peek=True)
    for i, f in enumerate(s["fittings"]):
        add([f"fit:{i}", f"p:{f['parcel']}"], f"{f.get('name') or f['kind']} on {w.parcels()[f['parcel']]['name']}", 0.15,
            ["craft", "building"])
    for hid, hd in s["herds"].items():
        p = w.parcels()[hd["parcel"]]
        add([f"herd:{hid}", f"p:{hd['parcel']}"], f"{hd['name']} ({hd['count']} head) on {p['name']}", 0.1, ["animals"])
    # people
    for x in w.living():
        a = s["agents"][x]
        add([f"a:{x}"], f"{x} {WORDS_STAGE[a['hunger']]}", 0.1 if a["hunger"] == 0 else 0.35, ["food"] if a["hunger"] else [],
            concerns=[x])
        if a["wounded"]:
            add([f"a:{x}"], f"{x} moves stiffly, bruised about the face", 0.5, ["danger"], concerns=[x])
        tools = [i for i in ("axe", "sickle", "club", "basket") if a["holdings"].get(i, 0) >= 1]
        if tools:
            add([f"a:{x}"], f"{x} carries " + " and ".join(f"a {t}" for t in tools), 0.08, ["craft"] + (["danger"] if "club" in tools else []))
        load = [(i, q) for i, q in a["holdings"].items() if q >= 2 and ITEMS[i]["weight"] > 0]
        if load:
            add([f"a:{x}"], f"{x} has a load: " + ", ".join(f"{_amount(q)} {i}" for i, q in load), 0.12,
                ["food"] if any(i in EDIBLE for i, _ in load) else [])
    # happenings
    for e in s["events"]:
        if e["kind"] == "speech":
            continue                                                     # speech is heard, not seen
        if e.get("dawn"):                                                # a dawn sign or incident lasts the day: seen again by
            add([e.get("about") or "sky"], e["text"], e["salience"], e["tags"], e.get("sense", "sight"), e.get("concerns", []),
                event=e["id"], kind=e["kind"], dawn=True)                # whoever attends to it, or notices it later
            continue
        about = [f"a:{e['actor']}"] if e.get("actor") else []
        if e.get("target"):
            about.append(f"a:{e['target']}")
        if e.get("parcel"):
            about.append(f"p:{e['parcel']}")
        if e.get("house"):
            about.append(f"h:{e['house']}")
        add(about, e["text"], e["salience"], e["tags"], e.get("sense", "sight"), e.get("concerns", []), event=e["id"],
            actor=e.get("actor"), tech=e.get("tech"), kind=e["kind"])
    return out


def relevance(w, name, f) -> float:
    a = w.s["agents"][name]
    r = 0.0
    if name in f["concerns"]:
        r += 1.0
    kin = {x for x in w.living() if w.s["agents"][x]["house"] == a["house"]}
    if any(s in (f"h:{a['house']}",) or (s.startswith("a:") and s[2:] in kin and s[2:] != name) for s in f["about"]):
        r += 0.5
    if set(f["tags"]) & set(a.get("interests", [])):
        r += 0.5
    if a["hunger"] < 0 and "food" in f["tags"]:
        r += 0.4
    if set(f["tags"]) & set(a.get("concerns", [])):
        r += 0.4
    if "danger" in f["tags"]:
        r += 0.3
    return min(1.0, r)


def _can_read(w, name, f) -> bool:
    sk = f.get("skill")
    return not sk or sk in w.s["agents"][name].get("interests", [])


def _mine(name, f) -> bool:
    return f.get("actor") == name


# ---------------------------------------------------------------------- the evening: who perceives what
def evening(w, attend: dict, today: dict) -> dict:
    """Perception for everyone after the day's work. attend: {name: target as written}. Returns {name: log record}."""
    F = facts(w)
    living = w.agents_acting()
    logs = {}
    for name in w.living():
        old = store(w, name)["today"]
        store(w, name)["today"] = {**_blank(), "heard": old.get("heard", []), "dawn": old.get("dawn", [])}
    # being watched: each watcher (attending a person, or the watch verb)
    watchers = {}
    for name in living:
        tgt = today["watch"].get(name) or attend.get(name)
        who = w.person(tgt) if tgt else None
        if who and who != name:
            watchers.setdefault(who, []).append(name)
    for name in living:
        t = store(w, name)["today"]
        rng = w.rng("notice", w.d, name)
        tgt_raw = today["watch"].get(name) or attend.get(name)
        subject, label = resolve_target(w, name, tgt_raw)
        place = subject == "place"
        # what concerns you: always, in full
        con = [f for f in F if name in f["concerns"] and f.get("event") and not _mine(name, f)]
        t["concerned"] = [f["text"] for f in con]
        seen = {f["id"] for f in con}
        # the daily notice
        cand = []
        for f in F:
            if f["id"] in seen or _mine(name, f) or f.get("peek") or f.get("ambient") or not _can_read(w, name, f):
                continue
            own = f"h:{w.s['agents'][name]['house']}"
            if f.get("dawn") and any(x in store(w, name)["today"]["dawn"] for x in [f["text"]]):
                continue                                                 # already met it at dawn
            if own in f["about"] and not f.get("event"):
                continue                                                 # your own house is shown to you every morning
            if f["salience"] < 0.2 and name not in f["concerns"]:
                continue                                                 # the notice is for what stands out
            if f.get("kind") in ROUTINE or (f["about"] and f["about"][0] == f"a:{name}"):
                continue                                                 # routine work is glimpsed, not noticed; your own look is not news
            rel = relevance(w, name, f)
            p = 1.0 if f["salience"] >= SALIENT else min(1.0, f["salience"] * (0.3 + rel) * (1.8 if place else 1.0))
            if rng.random() < p:
                cand.append((f["salience"] + rel, f))
        cand.sort(key=lambda x: -x[0])
        notice = [f for _, f in cand[:NOTICE_MAX + (2 if place else 0)]]
        t["notice"] = [f["text"] for f in notice]
        seen |= {f["id"] for f in notice}
        # attending
        att = []
        if place:
            amb = [f for f in F if f.get("ambient")]
            rng.shuffle(amb)
            att = amb[:4]
        elif subject:
            pool = [f for f in F if subject in f["about"] and f["id"] not in seen and not _mine(name, f) and _can_read(w, name, f)
                    and (not f.get("peek") or subject.startswith("h:"))]
            pool.sort(key=lambda f: -(f["salience"] + relevance(w, name, f)))
            att, texts = [], set()
            for f in pool:                                               # the same sight several times is one line
                if f["text"] not in texts and len(att) < ATTEND_MAX:
                    att.append(f)
                    texts.add(f["text"])
        if subject or place:
            t["attended"] = {"target": label, "lines": [f["text"] for f in att] or ["nothing out of the ordinary"]}
        seen |= {f["id"] for f in att}
        # a glimpse of a few others: where they spent the day
        others = [x for x in living if x != name and f"a:{x}" != subject]
        kin = [x for x in others if w.s["agents"][x]["house"] == w.s["agents"][name]["house"]]
        rest = [x for x in others if x not in kin]
        rng.shuffle(rest)
        for x in (kin + rest)[:int(w.p["glimpse"])]:
            pl = today["worked"].get(x)
            if pl:
                t["glimpse"].append(f"{x} spent the day at {w.parcels()[pl[-1]]['name']}")
            elif today["watch"].get(x):
                t["glimpse"].append(f"{x} spent the day at {today['watch'][x]}'s side")
            else:
                t["glimpse"].append(f"{x} was about the houses")
        # felt watched
        for v in watchers.get(name, []):
            mutual = (today["watch"].get(name) or attend.get(name) or "").lower() == v.lower()
            if today["watch"].get(v) == name or w.rng("felt", w.d, name, v).random() < float(w.p["felt_watched"]) * (2 if mutual else 1):
                t["felt"].append(f"You had the feeling {v} was watching you today" if today["watch"].get(v) != name
                                 else f"{v} spent the day at your side, watching how you work")
        # sightings that teach: the attended or watched person, and anyone doing a craft where you worked
        times = {}
        doer = w.person(tgt_raw) if tgt_raw else None
        for f in F:
            tech, actor = f.get("tech"), f.get("actor")
            if not tech or not actor or actor == name or KN.basic(tech):
                continue
            k = 0
            if doer == actor:
                k = 2 if today["watch"].get(name) == actor else 1
            elif f.get("kind") == "work" and any(p in today["worked"].get(name, []) for p in [s[2:] for s in f["about"] if s.startswith("p:")]):
                k = 1
            if k:
                times[(tech, actor)] = max(times.get((tech, actor), 0), k)
        for (tech, actor), k in times.items():
            before = KN.level(w, name, tech)
            rose = KN.saw(w, name, tech, actor, k)
            if before is None:
                t["learned"].append(f"You saw {actor} at {TECHNIQUES[tech]['label'].split(' (')[0]}, which you had not seen done before.")
            if rose:
                t["learned"].append(f"From watching {actor} you now have a rough idea of {TECHNIQUES[tech]['label'].split(' (')[0]}.")
        # beliefs: what it was given, dated
        for f in con + notice + att:
            for sub in f["about"]:
                b = store(w, name)["beliefs"].setdefault(sub, {"day": w.d, "lines": [], "ids": []})
                if b["day"] != w.d:
                    b.update(day=w.d, lines=[], ids=[])
                if f["id"] not in b["ids"]:
                    b["ids"].append(f["id"])
                    b["lines"].append(f["text"])
        logs[name] = {"notice": [f["id"] for f in notice], "attended": [f["id"] for f in att], "concerned": [f["id"] for f in con],
                      "target": label}
        store(w, name)["log"].append({"day": w.d, **logs[name]})
    return {"facts": F, "agents": logs}


def resolve_target(w, name, x):
    """(subject key, label) for what an agent wrote in attend."""
    if not x:
        return None, None
    s = str(x).strip()
    low = s.lower()
    if low in ("place", "the place", "the place in general", "everything", "general", "around", "the village", "the hamlet"):
        return "place", "the place in general"
    if low in ("sky", "the sky", "weather", "the weather", "the land and sky", "the land", "the sky and the weather"):
        return "sky", "the land and sky"
    who = w.person(s)
    if who and who != name:
        return f"a:{who}", who
    hid = w.house_by_name(s)
    if hid:
        return f"h:{hid}", w.s["houses"][hid]["name"]
    pid = w.parcel_by_name(s)
    if pid:
        return f"p:{pid}", w.parcels()[pid]["name"]
    for hid, h in w.s["herds"].items():
        if low in (hid.lower(), h["name"].lower(), "cattle", "the cattle", "herd", "the herd"):
            return f"herd:{hid}", h["name"]
    for i, f in enumerate(w.s["fittings"]):
        if low in (f["kind"], (f.get("name") or "").lower()):
            return f"fit:{i}", f.get("name") or f["kind"]
    return "place", f"the place in general (you could not find {s!r} to attend to)"


# ---------------------------------------------------------------------- steals, and closing the day
def steals(w, today, attend) -> None:
    """Who saw a theft: the house's people at home, someone attending the house or the place, a little chance for the rest."""
    for st in today["steals"]:
        h = w.s["houses"][st["house"]]
        seen_by = []
        for x in w.agents_acting():
            if x == st["by"]:
                continue
            sub, _ = resolve_target(w, x, today["watch"].get(x) or attend.get(x))
            at_home = w.s["agents"][x]["house"] == st["house"] and not today["worked"].get(x) and not today["watch"].get(x)
            p = 0.8 if sub == f"h:{st['house']}" else 0.45 if at_home else 0.3 if sub == "place" else 0.05
            if w.rng("steal-seen", w.d, x, st["by"]).random() < p:
                seen_by.append(x)
        owners = [x for x in w.living() if w.s["agents"][x]["house"] == st["house"]]
        if seen_by:
            w.happen("steal", f"{st['by']} slipped into {h['name']} and came out with {st['qty']:g} {st['item']}", actor=st["by"],
                     parcel=h["parcel"], salience=0.9, tags=["danger", "food"], concerns=seen_by + owners, extra={"house": st["house"]})
            store(w, st["by"])["today"].setdefault("heard", []).append("You think you were seen coming out of " + h["name"] + ".")
        else:
            w.happen("loss", f"some {st['item']} is missing from {h['name']}'s store", parcel=h["parcel"], salience=0.6,
                     tags=["food", "danger"], concerns=owners, extra={"house": st["house"]})


SPEECH = ("You told ", "You said", "You noted", "You let go of the note")
DIRECT = "(to you) "                                                     # heard lines said to the agent itself: it was asked at the time
OWN_MAX = 6                                                              # memories the agent wrote itself, kept (the oldest drop)


def own_memory(w, name, span, text) -> None:
    """The memory an agent wrote at the end of a stretch of days (converse.py), in its own words."""
    m = store(w, name)
    m["own"] = (m.get("own", []) + [{"span": span, "day": w.d, "text": " ".join(str(text).split()[:150])}])[-OWN_MAX:]


def close_day(w, name, did: list, night_lines: list) -> None:
    """The day into memory. What it did (the engine's results) is kept apart from what it said, so its own words never stand in
    the record for its acts."""
    m = store(w, name)
    t = m["today"]
    saw = t["dawn"] + t["concerned"] + t["notice"] + t["felt"] + t["learned"]
    if t["attended"]:
        saw.append(f"(attending to {t['attended']['target']}) " + "; ".join(t["attended"]["lines"]))
    acts = [x for x in did if not x.startswith(SPEECH)]
    said = [x.removeprefix("You ") for x in did if x.startswith(("You told ", "You said "))]
    m["days"].append({"day": w.d, "did": acts + night_lines, "said": said, "heard": list(t["heard"]), "saw": saw,
                      "glimpse": list(t["glimpse"])})
    for line in t["concerned"] + t["learned"] + night_lines:
        low = line.lower()
        if any(k in low for k in ("killed", "died", "beat", "raided", "taught you", "missed meal", "gave", "missing", "slipped into",
                                  "now have a rough idea", "starving")):
            m["lasting"].append(f"{_day(w, w.d)}: {line}")
    m["lasting"] = m["lasting"][-14:]
    t["heard"], t["dawn"] = [], []


def _day(w, d) -> str:
    c = w.calendar(d)
    return f"{c['season']} day {c['day']}"


def beliefs_lines(w, name, limit=6) -> list:
    """What it last perceived of people and things it did not see today, dated."""
    out, said = [], set()
    for sub, b in sorted(store(w, name)["beliefs"].items(), key=lambda kv: -kv[1]["day"]):
        if b["day"] >= w.d - 1 or not sub.startswith(("a:", "h:")) or sub == f"a:{name}":
            continue
        lines = [x for x in b["lines"] if x not in said][:3]
        said.update(lines)
        if not lines:
            continue
        k = w.d - b["day"]
        label = sub[2:] if sub.startswith("a:") else w.s["houses"][sub[2:]]["name"]
        out.append(f"{label}, {k} days ago: " + "; ".join(lines))
        if len(out) >= limit:
            break
    return out


# ---------------------------------------------------------------------- notes
def apply_notes(w, name, reply) -> list:
    """note [{title, text}], pin title, forget [titles]. Free. Returns result lines."""
    a = w.s["agents"][name]
    nt = w.p["notes"]
    out = []
    for n in reply.get("note") or []:
        if not isinstance(n, dict) or not n.get("title"):
            continue
        title = str(n["title"]).strip()[:60]
        text = " ".join(str(n.get("text", "")).split()[: int(nt["words"])])
        if title not in a["notes"] and len(a["notes"]) >= int(nt["max"]):
            out.append(f"Refused: note: you already keep {nt['max']} notes; forget one first")
            continue
        a["notes"][title] = text
        out.append(f"You noted “{title}”.")
    for title in reply.get("forget") or []:
        if a["notes"].pop(str(title), None) is not None:
            out.append(f"You let go of the note “{title}”.")
            if a["pinned"] == title:
                a["pinned"] = None
    pin = reply.get("pin")
    if pin:
        if str(pin) in a["notes"]:
            a["pinned"] = str(pin)
        else:
            out.append(f"Refused: pin: you have no note called “{pin}”")
    return out
