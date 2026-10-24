"""The day (spec/core/round.md): dawn (arrivals, the scheduler's incidents and signs, goods left found), decide (everyone at once),
talk (D2-7, D4-25, D4-31: messages to one person wake them; speech in a building or to the town does not), work (the plans
interleaved, travel last), settlement of agreements (D2-32), teaching and membership matched, thefts seen or not, the night, then
perception and memory (D4-26 to D4-28).

Logs in the run directory: run.json, turns.jsonl, days.jsonl, perception.jsonl, memory.jsonl, state.json.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import time
from pathlib import Path

from cybertron2.engine import agreements as AG, fuse as FU, knowledge as KN, life as LF, night as N, perceive as PC, prompt as PR, roads as RD, settle as ST, verbs as V
from cybertron2.engine.converse import Conversations
from cybertron2.engine.data import EDIBLE, TECHNIQUES
from cybertron2.engine.here import Here, Mind
from cybertron2.engine.world import Refused, World, load_spec

MAX_SAY = 3
MAX_ACTIONS = 10
WAVES = 2


def blank_today() -> dict:
    return {"worked": {}, "thefts": [], "left": [], "joins": [], "admits": [], "sleep": {}, "travel": {}, "watch": {}, "teach": [],
            "learn": [], "fights": [], "guards": {}, "fire": {}, "partner": [], "try": [], "care": {}, "care_by": {}}


# ---------------------------------------------------------------------- a scripted bot (smoke tests only)
def bot_plan(w, name, talk=None) -> dict:
    here, mind = Here(w, name), Mind(w, name)
    can, _ = KN.options(here, mind)
    acts = []
    can = sorted(can, key=lambda x: (not x.startswith(("work reap", "work milk")), x))
    for line in can[:4]:
        verb, tech = line.split(" ", 1)
        tech = tech.split(" at ")[0].split(" (")[0]
        acts.append({"do": verb, "what": tech})
    for item in ("wild food", "grain", "timber", "meat", "milk"):
        acts.append({"do": "move", "item": item, "qty": 2, "to": "store"})
    roads = here.roads()
    if roads and w.spec.get("bot_travel", True) and w.d % 4 == 1 and len(name) % 2 == 0:
        acts = acts[:2] + [{"do": "travel", "to": roads[0][1]}]
    others = here.people(me=False)
    out = {"why": "bot", "actions": acts, "attend": others[(w.d + len(name)) % len(others)] if others else "the place in general",
           "say": [{"to": "everyone", "text": f"{name} is at work today."}] if w.d % 3 == 0 else []}
    if w.d == 1 and others:
        out["offers"] = [{"to": "anyone", "give": "1 wild food", "get": "1 timber by day 6"}]
    if talk and talk.get("offers"):
        out["actions"] = [{"do": "accept", "offer": talk["offers"][0].split(":")[0]}] + acts
    return out


def bot_fuse(w, name, x) -> dict:
    """A scripted bot's answer to an urgent call: those inside defend and raise the alarm, neighbours come to help; on the road it
    takes what it finds, keeps to its choice at trouble, and goes on after a meeting (offering a trade)."""
    e = x["events"][0]
    if e["kind"] == "meeting":
        return {"actions": [{"do": "go on"}], "say": [{"to": "everyone", "text": f"{name} greets you."}],
                "offers": [{"to": "anyone", "give": "1 wild food", "get": "1 timber"}]}
    if e["kind"] == "find":
        return {"actions": [{"do": "take"}]}
    if e["kind"] == "crossing":
        return {"actions": [{"do": e.get("default") or "wait"}]}
    if e["kind"] == "herd":
        return {"actions": [{"do": "accompany"}]}
    if e["kind"] == "split":
        return {"actions": [{"do": "go after them"}]}
    inside = e.get("building") in w.homes(name)
    return {"actions": ([{"do": "alarm"}, {"do": "defend"}] if inside else [{"do": "defend"}])[: x["acts"]]}


def decide(w, name, text, opening, system, backend, conv, talk=None, schema=None, fuse=None, transit=False) -> tuple[dict, dict]:
    model = w.s["people"][name]["model"]
    if model == "bot":
        return (bot_fuse(w, name, fuse) if fuse else bot_plan(w, name, talk)), {"model": "bot", "sent": text}
    from cybertron import llm
    t0 = time.monotonic()
    attempts = []
    schema = schema or PR.schema_for(Here(w, name, transit=transit or fuse is not None), Mind(w, name))
    sent, ctx = conv.message(name, w.d, system, schema, text, opening)
    out, reasoning, usage = llm.call(backend, model, ctx["conv"]["system"], sent, schema,
                                     thinking_budget=int((w.spec.get("llm") or {}).get("thinking_budget", 2000)), attempts=attempts)
    raw = attempts[-1].get("raw") if attempts and attempts[-1].get("ok") and not (out or {}).get("_error") else None
    usage = conv.after(ctx, raw, usage)
    return out or {}, {"model": model, "usage": usage, "seconds": round(time.monotonic() - t0, 1), "thinking": reasoning,
                       "sent": ctx["text"], "opening": ctx["text"] is opening}


def _parallel(fn, jobs: dict, workers) -> tuple[dict, dict, dict]:
    replies, meta, errors = {}, {}, {}
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(fn, *args): n for n, args in jobs.items()}
        for f in cf.as_completed(futs):
            n = futs[f]
            try:
                replies[n], meta[n] = f.result()
                if replies[n].get("_error"):
                    errors[n] = str(replies[n]["_error"])[:500]
                    replies[n] = {"actions": []}
            except Exception as e:
                replies[n], meta[n], errors[n] = {"actions": []}, {}, repr(e)[:500]
    return replies, meta, errors


# ---------------------------------------------------------------------- the talk step (information/speech.md)
def _guardian(w, child, names, node):
    """Who answers for a child here (D4-55): a parent taking part in the talk at this node, else its household's head, else an adult
    of its household."""
    kin = (w.s["mind"].get(child) or {}).get("kin") or {}
    here_ = [m for m in names if w.at(m) == node and w.s["people"][m]["alive"]]
    for rel in ("your mother", "your father"):
        p = next((m for m, k in kin.items() if k.get("rel") == rel and m in here_), None)
        if p:
            return p
    hh = w.household_of(child)
    head = w.head(hh) if hh else None
    if head in here_:
        return head
    return next((m for m in here_ if hh and w.household_of(m) == hh and w.s["people"][m]["stage"] in ("adult", "elder")), None)


def talk(w, names, replies, results) -> dict:
    """Deliver speech, explanations and offers. Returns {name: box} for those woken (a message or an offer to them; a note opened or
    a craft looked up wakes the agent itself)."""
    box = {n: {"heard": [], "also": [], "offers": [], "opened": [], "cards": []} for n in names}
    for n in names:
        r = replies[n]
        if not w.s["people"][n]["alive"] or w.at(n) is None:
            continue
        here, mind = Here(w, n), Mind(w, n)
        for x in [x for x in (r.get("say") or []) if isinstance(x, dict) and str(x.get("text", "")).strip()][:MAX_SAY]:
            text, to = str(x["text"])[:600], str(x.get("to") or "everyone")
            said = sum(1 for y in results[n] if y.startswith("You said ("))
            if (said + 1) * int(w.p["say_units"]) > here.units():
                results[n].append("Refused: say: speaking takes a unit of work, and you have none left for it today")
                continue
            bid = here.building(to) if to.lower() not in ("everyone", "all", "the town", "town") else None
            if bid and "access" not in here.rights(("building", bid)):
                results[n].append(f"Refused: say: you have no access to {here.buildings()[bid]['name']}")
                continue
            hearers = [m for m in here.people(me=False) if m in names and (not bid or "access" in here.rights(("building", bid), m))]
            where = f"in {here.buildings()[bid]['name']}" if bid else "to everyone"
            for m in hearers:
                box[m]["also"].append(f"{n} said ({where}): {text}")
                PC.store(w, m)["today"]["heard"].append(f"{n} said ({where}): {text}")
            _mentions(w, here, n, hearers, text)
            results[n].append(f"You said ({where}): {text}")
            here.event("speech", f"{n} spoke {where}", actor=n, salience=0.1, sense="sound")
        for t in [t for t in (r.get("tell") or []) if isinstance(t, dict)][:MAX_SAY]:
            text, to = str(t.get("text", ""))[:600], here.person(t.get("to"))
            if to and to not in names and w.s["people"][to]["stage"] == "child":
                results[n].append(f"Refused: tell: {to} is a child and takes no part in the talk; say it aloud, or tell someone else")
                continue
            if not to or to not in names or to == n:
                results[n].append(f"Refused: tell: nobody called {t.get('to')!r} is here to hear you")
                continue
            lim = w.s["people"][n]["messages"]
            sent = sum(1 for y in results[n] if y.startswith("You told "))
            if sent >= lim:
                results[n].append(f"Refused: tell: you have sent your {lim} private messages for today: 0 left, so every further tell "
                                  "today will fail too; the count resets tomorrow")
                continue
            box[to]["heard"].append(f"{n}: {text}")
            PC.store(w, to)["today"]["heard"].append(f"{PC.DIRECT}{n} told you: {text}")
            _mentions(w, here, n, [to], text)
            results[n].append(f"You told {to}: {text}" + (" (That was your last private message today.)" if sent + 1 >= lim else ""))
        for x in [x for x in (r.get("explain") or []) if isinstance(x, dict)][:2]:
            to, tech = here.person(x.get("to")), KN.resolve(x.get("what"))
            if not to or to not in names or tech is None:
                results[n].append(f"Refused: explain: {x.get('to')!r} or {x.get('what')!r} not found")
                continue
            if KN.level(mind, tech) != "known":
                results[n].append(f"Refused: explain: you do not know {KN.label(tech)} well enough to explain it")
                continue
            if KN.level(Mind(w, to), tech) in ("rough", "capable", "known"):
                results[n].append(f"Refused: explain: {to} already has more than a rough idea of {KN.label(tech)}")
                continue
            here.apply("learn", person=to, tech=tech, level="rough", source=f"{n} explained it")
            results[n].append(f"You explained {KN.label(tech)} to {to}.")
            box[to]["also"].append(f"{n} explained {KN.label(tech)} to you: you now have a rough idea of it.")
            PC.store(w, to)["today"]["heard"].append(f"{n} explained {KN.label(tech)} to you.")
        for o in [o for o in (r.get("offers") or []) if isinstance(o, dict)][:3]:
            kid = here.person(o.get("to"))
            if kid and kid not in names and w.s["people"][kid]["stage"] == "child":
                guardian = _guardian(w, kid, names, w.at(n))                  # an offer to a child goes to its parent (D4-55)
                if guardian is None:
                    results[n].append(f"Refused: offer: {kid} is a child, and no parent of {kid}'s is here to take the offer")
                    continue
                results[n].append(f"{kid} is a child: your offer goes to {kid}'s parent, {guardian}.")
                o = {**o, "to": guardian}
            try:
                line = AG.make_offer(here, mind, o)
            except Refused as e:
                results[n].append(f"Refused: offer: {e}")
                continue
            results[n].append(line)
            if line.startswith("You offered "):
                oid = line[len("You offered "):].split(":")[0]
                text = AG.offer_text(here, oid)
                tgt = here.offer(oid)["to"]
                for m in ([tgt] if tgt else [m for m in here.people(me=False) if m in names]):
                    if m in box:                                               # only those taking part in the talk
                        (box[m]["offers"] if tgt else box[m]["also"]).append(text)
        a = w.s["people"][n]
        for title in (r.get("open") or [])[:int(w.p["notes"]["open"])]:
            if title in a["notes"]:
                box[n]["opened"].append((title, a["notes"][title]))
        for x in (r.get("look_up") or [])[:3]:
            tech = KN.resolve(x)
            box[n]["cards"].append(KN.card(here, mind, tech) if tech else f"{x}: you know nothing of it")
    return {n: b for n, b in box.items() if b["heard"] or b["offers"] or b["opened"] or b["cards"]}


def _mentions(w, here, speaker, hearers, text):
    """Hearing a craft named makes one aware of it (knowledge.md); hearing of a place one did not know, from someone who knows it,
    tells one of it and of the way there (D4-47)."""
    low = f" {str(text).lower()} "
    for nid, pl in PC.store(w, speaker)["places"].items():
        nm = pl["name"].lower()
        if f" {nm}" in low or f" {nm.removeprefix('the ')}" in low:
            for h in hearers:
                if nid not in PC.store(w, h)["places"]:
                    PC.store(w, h)["places"][nid] = {**{k: v for k, v in pl.items() if k != "seen"}, "seen": None, "days": None,
                                                     "told": speaker}
                    PC.store(w, h)["today"]["heard"].append(f"(You had not heard of {pl['name']} before: {speaker} knows the way there.)")
    from cybertron2.engine import layout as LY                                 # a hidden way told (D2-98: the finder chooses whom)
    if any(x in low for x in (" way", " path", " trail", " track")) and here.node is not None:
        for key in (w.s["mind"][speaker].get("ways") or {}):
            rid, node = key.rsplit("@", 1)
            if node != here.node:
                continue
            end = w.s["roads"][rid]["ends"][node]
            if any(w.s["parcels"][p]["name"].lower().removeprefix("the ") in low for p in end.get("parcels") or []):
                for h in hearers:
                    if LY.learn_way(w, h, rid, node, f"told by {speaker}"):
                        PC.store(w, h)["today"]["heard"].append(f"(You did not know of a way out from there: {speaker} has found one.)")
    for tech in KN.mentions(text):
        if KN.basic(tech):
            continue
        for h in hearers:
            if KN.level(Mind(w, h), tech) is None:
                here.apply("learn", person=h, tech=tech, level="aware", source=f"you heard {speaker} speak of it")
                PC.store(w, h)["today"]["heard"].append(f"(You had not heard of {KN.label(tech)} before.)")


# ---------------------------------------------------------------------- dawn (environment/scheduler.md, D4-8)
def dawn(w) -> None:
    for inc in w.spec.get("incidents") or []:
        if int(inc["day"]) - 1 != w.d:
            continue
        node = inc["node"]
        if inc["kind"] == "stray":
            hid, pid = inc["herd"], inc["into"]
            h = w.s["herds"][hid]
            w.apply("set", node, ref=("herd", hid), field="parcel", value=pid)
            c = w.s["parcels"][pid].get("crop")
            if c and c.get("area_left", 0) > 1e-6:
                w.apply("draw", node, parcel=pid, key="crop", qty=round(min(c["left"], float(inc.get("eats", 2))), 4))
            holders = [m for m in w.living() if any(cl["claimant"] in (m, w.household_of(m)) for cl in w.claims_on(("parcel", pid)))]
            w.event(node, "stray", f"{h['name']} broke through into {w.s['parcels'][pid]['name']} at dawn and are trampling the "
                    f"{c.get('kind', 'crop') if c else 'ground'}", about=[f"parcel:{pid}"], salience=0.7, tags=["farming", "animals", "food"],
                    concerns=holders, dawn=True)
        if inc["kind"] == "death":                                          # a death in the night (old age; life.md, later)
            who = inc["person"]
            if w.s["people"][who]["alive"]:
                place = w.at(who)
                w.apply("die", place, person=who, cause=inc.get("cause", "old age"))
                w.event(place, "death", f"{who} died in the night", target=who, salience=1.0, tags=["death"], dawn=True)
        if inc["kind"] == "fire":
            bid = inc["building"]
            b = w.s["buildings"][bid]
            for item, q in list(w.goods(b["stock"]).items()):
                share = float(inc.get("food", 0.85)) if item in EDIBLE else float(inc.get("other", 0.5))
                w.apply("destroy", node, src=b["stock"], item=item, qty=q * share, why="fire")
            w.apply("set", node, ref=("building", bid), field="condition", value=max(0, b["condition"] - int(inc.get("damage", 1))))
            live = [m for m in w.living() if bid in w.homes(m)]
            w.event(node, "fire", f"fire broke out in {b['name']} in the night: the store is burnt, most of its food is gone and the roof "
                    "is damaged", about=[f"building:{bid}"], salience=0.95, tags=["danger", "food", "shelter"], concerns=live, dawn=True)
    for x in [x for x in w.s.get("left", []) if x["day"] == w.d - 1]:
        b = w.s["buildings"][x["building"]]
        live = [m for m in w.living() if x["building"] in w.homes(m)]
        w.event(b["node"], "left", f"{x['by']} left {x['qty']:g} {x['item']} at {b['name']}", actor=x["by"], about=[f"building:{x['building']}"],
                salience=0.6, tags=["food"] if x["item"] in EDIBLE else [], concerns=live, dawn=True)
    grew = LF.dawn(w)                                                       # growing up, coming of age, succession (D2-139, D2-143)
    if grew:
        w.s.setdefault("life", []).append({"day": w.d, "dawn": grew})
    for name in w.living():
        t = w.s["people"][name]["transit"]
        if t and t["arrive"] <= w.d and t.get("carried_by"):                 # an infant carried: it comes in with its mother
            w.apply("arrive", t["to"], person=name)
            continue
        if t and t["arrive"] <= w.d:
            RD.arrived(w, name, t)                                          # its notices on the way, remembered (D2-97)
            w.apply("arrive", t["to"], person=name)
            w.s["people"][name]["arrived"] = w.d
            from cybertron2.engine import herds as HD, layout as LY
            HD.arrive_with(w, name, t["to"])                                # beasts it accompanied come in with it (D2-127)
            LY.learn_way(w, name, t["road"], t["to"], "came")                # one knows the end one came in by (D2-90)
            LY.wear_way(w, t["road"], t["to"])
            w.event(t["to"], "arrive", f"{name} arrived from {w.s['nodes'][t['from']]['name']}", actor=name, salience=0.7, tags=["travel"], dawn=True)
    for sg in w.spec.get("signs") or []:
        if int(sg["day"]) - 1 == w.d:
            for node in (list(w.s["nodes"]) if sg.get("node") in (None, "all") else [sg["node"]]):
                w.event(node, "sign", sg["text"], about=[sg.get("about", "sky")], salience=float(sg.get("salience", 0.3)),
                        tags=sg.get("tags", ["season"]), sense=sg.get("sense", "sight"), dawn=True)


def night_lines(w, rec) -> dict:
    out = {}
    for n, a in w.s["people"].items():
        L = []
        slept = rec.get("slept", {}).get(n)
        homes = [w.s["buildings"][b]["name"] for b in w.homes(n)]
        if slept == "out":
            L.append("You slept out" + (" on the road." if a["transit"] else ", with no roof over you."))
        elif slept and slept not in homes:
            L.append(f"You slept at {slept}.")
        if n in rec.get("open_fire", []):
            L.append(f"You lit a fire in the open ({float(w.p['heat']['open']):g} heat from what you carried); up to {w.p['heat']['share']} slept by it.")
        if n in rec["missed"]:
            L.append("You went to bed without enough to eat: a missed meal.")
            raw = rec.get("uncooked", {}).get(n)
            if raw:
                L.append(f"With no lit fire your {' and '.join(raw)} went down raw and fed you little.")
        elif n in rec["short"]:
            L.append(f"You ate {rec['ate'][n]:g}, less than a cold night asks.")
        if n in rec["cold_falls"]:
            L.append("The night in the cold left you starving.")
        if n in rec["deaths"]:
            L.append("You died.")
        for b in w.homes(n):
            h = rec["hearth"].get(b)
            if h and not h["lit"] and w.s["buildings"][b]["fittings"].get("hearth"):
                L.append(f"{w.s['buildings'][b]['name']}'s fire went out: no timber in its store.")
            if b in rec["breaks"]:
                L.append(f"{w.s['buildings'][b]['name']} took damage in the night.")
        out[n] = L
    return out


# ---------------------------------------------------------------------- urgent calls (fuse events: D2-80 to D2-84, D2-110)
def fuse_calls(w, today, woke, results, talk_log, openings, systems, backend, conv, workers, extra_cost):
    """One call each for the woken, appended to its own conversation; a meeting on the road has up to 3 waves of talk among everyone
    in it (D2-110), each wave's speech and offers shown to all in the next; the last reply's acts are done."""
    def ask(texts):
        def one(n):
            here, mind = Here(w, n, transit=True), Mind(w, n)
            op = openings.get(n) or PR.road_opening(here, mind)
            return decide(w, n, texts[n], op + "\n\n" + texts[n], conv.system(n, systems.get(n) or ""), backend, conv, fuse=woke[n])
        r, m, e = _parallel(one, {n: (n,) for n in texts}, workers)
        for n in texts:
            extra_cost[0] += float(((m.get(n) or {}).get("usage") or {}).get("cc_equiv_usd") or 0.0) if n not in openings else 0.0
            talk_log.setdefault(n, []).append({"wave": "fuse", "prompt": texts[n], "reply": r.get(n) or {},
                                               "usage": (m.get(n) or {}).get("usage"), "error": e.get(n)})
        return r
    texts = {n: PR.fuse_prompt(Here(w, n, transit=True), Mind(w, n), x) for n, x in woke.items()}
    replies = ask(texts)
    meetings = {e["id"]: e for x in woke.values() for e in x["events"] if e["kind"] == "meeting"}
    for e in meetings.values():
        members = [n for p in e["parties"] for n in p if n in woke]
        for wave in range(1, int(RD.ROADS["waves"])):
            said, offers = RD.meeting_talk(w, e, {n: replies.get(n) or {} for n in members})
            if not said and not offers:
                break
            last = wave == int(RD.ROADS["waves"]) - 1
            texts = {n: PR.meeting_wave_prompt(Here(w, n, transit=True), Mind(w, n), [x for x in said if not x.startswith(f"{n}: ")],
                                               offers, woke[n]["acts"], last=last) for n in members}   # not one's own words back
            replies.update(ask(texts))
    for n, x in woke.items():
        lines = FU.answer(w, today, n, x, replies.get(n) or {})
        results.setdefault(n, []).extend([("On the road: " if w.at(n) is None else "In the night: ") + y for y in lines])
    for e in meetings.values():
        for f in RD.settle_meeting(w, e):
            for n in (f.get("by"), f.get("target")):
                if n:
                    results.setdefault(n, []).append(f"On the road: {f['by']} set on {f['target']}: {f['outcome']}.")


# ---------------------------------------------------------------------- the run
def run(spec_path, out_dir, backend=None, days=None, workers=12, bots=False, seed=None) -> Path:
    spec = load_spec(spec_path)
    if seed is not None:
        spec["seed"] = int(seed)
    if days:
        spec["days"] = int(days)
    if bots:
        spec["bots"] = True                                                 # those who come of age are bots too
        for a in spec["agents"].values():
            if a.get("model"):
                a["model"] = "bot"
    w = World(spec)
    backend = backend or os.environ.get("LLM_BACKEND") or "claude_code"
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    systems = {n: PR.system_prompt(Here(w, n), Mind(w, n)) for n in w.agents_acting()}
    (out / "run.json").write_text(json.dumps({"spec": spec, "backend": backend, "systems": systems,
                                              "models": {n: a["model"] for n, a in w.s["people"].items()}}, indent=1))
    files = {k: open(out / f"{k}.jsonl", "w") for k in ("turns", "days", "perception", "memory")}
    conv = Conversations(out, chunk=int((spec.get("memory") or {}).get("chunk", 3)), backend=backend)
    cost = 0.0
    last_system = dict(systems)
    extra_cost = [0.0]
    for day in range(w.days):
        w.s["day"] = day
        w.s["events"] = []
        today = w.s["today"] = blank_today()
        dawn(w)
        PC.dawn(w)
        names = w.agents_acting()
        at_day = {n: w.at(n) for n in names}
        systems = {n: PR.system_prompt(Here(w, n), Mind(w, n)) for n in names}
        openings = {n: PR.turn_prompt(Here(w, n), Mind(w, n), opening=True) for n in names}
        users = {n: PR.turn_prompt(Here(w, n), Mind(w, n), opening=False) for n in names}
        replies, meta, errors = _parallel(lambda n: decide(w, n, users[n], openings[n], systems[n], backend, conv),
                                          {n: (n,) for n in names}, workers)
        first = {n: dict(replies[n]) for n in names}
        results = {n: ([f"(Your reply could not be used, so you did nothing: {errors[n][:160]})"] if n in errors else []) for n in names}
        for n in names:
            results[n] += PC.apply_notes(Mind(w, n), replies[n])
        woken = talk(w, names, replies, results)
        talk_log = {n: [] for n in names}
        talked = set()
        for wave in range(WAVES):
            if not woken:
                break
            texts = {n: PR.talk_prompt(Here(w, n), Mind(w, n), b["heard"], b["also"], b["offers"], b["opened"], b["cards"],
                                       sum(1 for x in results[n] if x.startswith("You told "))) for n, b in woken.items()}
            rr, mm, ee = _parallel(lambda n: decide(w, n, texts[n], openings[n] + "\n\n" + texts[n], systems[n], backend, conv, woken[n]),
                                   {n: (n,) for n in woken}, workers)
            late = {}
            for n in woken:
                talked.add(n)
                r2 = rr[n]
                talk_log[n].append({"wave": wave, "prompt": texts[n], "reply": r2, "usage": (mm.get(n) or {}).get("usage"),
                                    "thinking": (mm.get(n) or {}).get("thinking"), "error": ee.get(n)})
                if n in ee or not isinstance(r2.get("actions"), list):
                    continue
                replies[n] = {**replies[n], **{k: v for k, v in r2.items() if v not in (None, "", [])}, "actions": r2["actions"]}
                results[n] += PC.apply_notes(Mind(w, n), {k: r2.get(k) for k in ("note", "pin", "forget")})
                late[n] = {k: r2.get(k) for k in ("say", "tell", "explain", "offers")}
            if not late:
                break
            woken = talk(w, names, {**{m: {} for m in names}, **late}, results)
            if wave == WAVES - 1:
                break
        attend = {n: replies[n].get("attend") for n in names if replies[n].get("attend")}
        plans = {n: [x for x in (replies[n].get("actions") or []) if isinstance(x, dict)][:MAX_ACTIONS] for n in names}
        scripted = {}
        for sc in w.spec.get("script") or []:                              # scripted acts (dry runs): done first that day, in order
            if int(sc["day"]) - 1 == day and sc["who"] in plans:
                scripted.setdefault(sc["who"], []).append(dict(sc["do"]))
        for n, acts in scripted.items():
            plans[n] = acts + plans[n]
        order = list(names)
        w.rng("order", day).shuffle(order)
        spoke = {n: sum(1 for y in results[n] if y.startswith("You said (")) * int(w.p["say_units"]) for n in names}
        budget = {n: max(0, w.units_for(n) - spoke[n]) for n in names}
        used = {n: 0 for n in names}
        rep = {n: {} for n in names}
        heavy = {}
        for i in range(max((len(p) for p in plans.values()), default=0)):
            for n in order:
                if i >= len(plans[n]) or not w.s["people"][n]["alive"] or n in today["travel"] or n in heavy:
                    continue
                here, mind = Here(w, n), Mind(w, n)
                a = plans[n][i]
                c = V.cost(here, a)
                if used[n] + c > budget[n]:
                    if c and used[n] < budget[n]:
                        results[n].append(f"Not done: {a.get('do')} {a.get('what') or ''}".rstrip() + f": it takes {c} units and you had {budget[n] - used[n]} left")
                    continue
                res = V.do(here, mind, a)
                if res.startswith("Refused: travel: you carry"):
                    heavy[n] = a
                    continue
                if not res.startswith("Refused"):
                    used[n] += c
                    results[n].append(res)
                elif res in results[n]:
                    rep[n][res] = rep[n].get(res, 1) + 1
                else:
                    results[n].append(res)
        if heavy:                                                        # too heavy to set off: what to leave, and with whom (D4-32)
            texts = {n: PR.lighten_prompt(Here(w, n), Mind(w, n), heavy[n], results[n]) for n in heavy}
            lr, lm, le = _parallel(lambda n: decide(w, n, texts[n], openings[n] + "\n\n" + texts[n], systems[n], backend, conv),
                                   {n: (n,) for n in heavy}, workers)
            for n in heavy:
                talk_log[n].append({"wave": "lighten", "prompt": texts[n], "reply": lr.get(n) or {}, "usage": (lm.get(n) or {}).get("usage")})
                acts = [x for x in ((lr.get(n) or {}).get("actions") or []) if isinstance(x, dict)
                        and str(x.get("do", "")).lower() in ("give", "leave", "move", "travel")][:8]
                if not any(str(x.get("do", "")).lower() == "travel" for x in acts):
                    results[n].append(f"You did not set off for {heavy[n].get('to')}: too heavy to carry.")
                for x in acts:
                    res = V.do(Here(w, n), Mind(w, n), x)
                    results[n].append(res)
                    if str(x.get("do", "")).lower() == "travel":
                        break
        for n in names:
            results[n] = [f"{x} (x{rep[n][x]})" if x in rep[n] else x for x in results[n]]
            if used[n] < budget[n]:
                results[n].append(f"You left {budget[n] - used[n]} of your {budget[n]} units unused.")
        today["partners"] = LF.settle(w, today)                             # partnerships both chose (D2-140)
        today["children_work"] = LF.children_work(w)                        # the head's standing order (D2-148)
        settled = AG.settle(w)
        for n, lines in list(ST.settle_teaching(w, today).items()) + list(ST.settle_joins(w, today).items()):
            results.setdefault(n, []).extend(lines)
        ST.settle_thefts(w, today, attend)
        w.s["left"] = [x for x in w.s.get("left", []) if x["day"] >= day - 1] + [{**x, "day": day} for x in today["left"]]
        N.departures(w, today)                                              # nightfall: those leaving are on their first stretch
        road_rec = RD.night(w, today)                                       # the roads tonight (world/roads.md)
        woke = FU.plan(w, today)                                            # fuse events: the urgent calls (D2-80 to D2-84)
        last_system.update(systems)
        if woke:
            fuse_calls(w, today, woke, results, talk_log, openings, last_system, backend, conv, workers, extra_cost)
        rec = N.night(w)
        rec["fuse"] = FU.record(today)
        rec["road"] = road_rec
        per = PC.evening(w, attend, today)
        nights = night_lines(w, rec)
        for n in names:
            m = meta.get(n, {})
            for u in [m.get("usage") or {}] + [x["usage"] or {} for x in talk_log[n]]:
                cost += float(u.get("cc_equiv_usd") or 0.0)
            files["turns"].write(json.dumps({
                "day": day, "agent": n, "model": w.s["people"][n]["model"], "units": budget[n], "used": used[n], "at": at_day[n],
                "household": w.household_of(n), "prompt": m.get("sent", users[n]), "opening": m.get("opening"), "reply": first[n],
                "thinking": m.get("thinking"), "talk": talk_log[n], "plan": plans[n], "attend": attend.get(n), "results": results[n],
                "night": nights.get(n, []), "usage": m.get("usage"), "seconds": m.get("seconds"), "error": errors.get(n)}) + "\n")
            PC.close_day(w, n, results[n], nights.get(n, []))
        ending = [n for n in names if w.s["people"][n]["alive"] and conv.ends(n, day) and day < w.days - 1]   # set off tonight too
        if ending:
            spans = {n: f"{PC._day(w, conv.c[n]['day0'] if n in conv.c else day)} to {PC._day(w, day)}" for n in ending}
            texts = {n: PR.memory_prompt(Mind(w, n), results[n], nights.get(n, []), spans[n]) for n in ending}
            keep = {n: json.loads(conv.c[n]["schema"]) for n in ending if n in conv.c}   # the stretch's own schema: it continues
            mr, mm, me = _parallel(lambda n: decide(w, n, texts[n], openings[n] + "\n\n" + texts[n], systems[n], backend, conv,
                                                    schema=keep.get(n), transit=True),
                                   {n: (n,) for n in ending}, workers)
            for n in ending:
                text = str((mr.get(n) or {}).get("memory") or "").strip()
                if text:
                    PC.own_memory(w, n, spans[n], text)
                u = (mm.get(n) or {}).get("usage") or {}
                cost += float(u.get("cc_equiv_usd") or 0.0)
                files["memory"].write(json.dumps({"day": day, "agent": n, "span": spans[n], "memory": text, "prompt": texts[n],
                                                  "usage": u, "thinking": (mm.get(n) or {}).get("thinking"), "error": me.get(n)}) + "\n")
        for n, lg in per["agents"].items():
            files["perception"].write(json.dumps({"day": day, "agent": n, **lg}) + "\n")
        files["perception"].write(json.dumps({"day": day, "facts": per["facts"]}) + "\n")
        rec.update(cost_usd=round(cost, 4), talked=sorted(talked), offers={k: v for k, v in w.s["offers"].items() if v.get("day", day) == day},
                   agreements_made=[k for k, v in w.s["agreements"].items() if v.get("day") == day and not v.get("seeded")], settled=settled,
                   teaching=today["teach"], learning=today["learn"], joins=today["joins"], admits=today["admits"], watch=today["watch"],
                   thefts=today["thefts"], attend=attend, errors=errors)
        cost += extra_cost[0]
        extra_cost[0] = 0.0
        for n in set(talk_log) - set(names):                                # calls to travellers on the road
            files["turns"].write(json.dumps({"day": day, "agent": n, "model": w.s["people"][n]["model"], "on_road": True,
                                             "talk": talk_log[n], "results": results.get(n, [])}) + "\n")
        files["days"].write(json.dumps(rec, default=str) + "\n")
        for f in files.values():
            f.flush()
        print(f"day {day + 1}: alive {len(w.living())}, missed {rec['missed']}, deaths {rec['deaths']}, talked {len(talked)}, "
              f"agreements {len(rec['agreements_made'])}, taught {len(today['teach'])}, thefts {len(today['thefts'])}, "
              + (f"born {[b['child'] for b in rec['life']['births']]}, " if rec["life"]["births"] else "") +
              f"errors {len(errors)}, cost ${cost:.2f}", flush=True)
        if not w.living():
            break
    w.save(out / "state.json")
    conv.close()
    for f in files.values():
        f.close()
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="cybertron2.engine")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("spec")
    r.add_argument("--out", required=True)
    r.add_argument("--days", type=int)
    r.add_argument("--backend")
    r.add_argument("--workers", type=int, default=12)
    r.add_argument("--bots", action="store_true")
    r.add_argument("--seed", type=int)
    args = ap.parse_args(argv)
    if args.cmd == "run":
        print(run(args.spec, args.out, args.backend, args.days, args.workers, args.bots, args.seed))
