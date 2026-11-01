"""The day (spec/core/round.md): dawn (arrivals, the scheduler's incidents and signs, goods left found), decide (everyone at once),
talk (D2-7, D4-25, D4-31: messages to one person wake them; speech in a building or to the town does not), work (the plans
interleaved, travel last), settlement of agreements (D2-32), teaching and membership matched, thefts seen or not, the night, then
perception and memory (D4-26 to D4-28).

Logs in the run directory: run.json, turns.jsonl, days.jsonl, perception.jsonl, memory.jsonl, state.json; and the journal, run.db
(spec/record: every request and answer by key, every event and change, a checkpoint at each committed step).
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import time
from pathlib import Path

from cybertron2.engine import agreements as AG, fuse as FU, knowledge as KN, life as LF, night as N, perceive as PC, prompt as PR, roads as RD, settle as ST, verbs as V
from cybertron2.engine import branch as BR, evening as EVN, journal as JN, memory as MEM, tags as TG, view as VW
from cybertron2.engine.converse import Conversations
from cybertron2.engine.data import EDIBLE, TECHNIQUES
from cybertron2.engine.here import Here, Mind
from cybertron2.engine.world import Refused, World, load_spec

MAX_SAY = 3
MAX_ACTIONS = 10
WAVES = 2


def blank_today() -> dict:
    return {"worked": {}, "thefts": [], "left": [], "joins": [], "admits": [], "sleep": {}, "travel": {}, "watch": {}, "teach": [],
            "learn": [], "fights": [], "guards": {}, "fire": {}, "partner": [], "try": [], "care": {}, "care_by": {}, "care_gift": {}, "route": {}}


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


class Stopped(Exception):
    """The run cannot go on (a replay whose record ends): it stops."""


class HumanTurn(Exception):
    """A person is to answer (the `human` responder, R3): the request is written, and the run stops until it is answered."""

    def __init__(self, turns):
        self.turns = list(turns)                                           # [(key, agent)]
        super().__init__(", ".join(f"{a} ({k})" for k, a in self.turns))


class UsageStop(Exception):
    """The subscription's weekly window is at the stop level (`llm.week_stop`, env CYBERTRON2_WEEK_STOP; default 0.9): the run stops
    cleanly before the day, to be resumed later."""


def _week_stop(spec):
    """Why to stop before a live day, or None: the claude CLI reports each window's use with every call (cybertron.llm.USAGE)."""
    from cybertron import llm
    v = os.environ.get("CYBERTRON2_WEEK_STOP")
    level = float(v) if v not in (None, "") else float(((spec.get("llm") or {}).get("week_stop")) or 0.9)
    wins = (llm.USAGE or {}).get("windows") or {}
    used = wins.get("seven_day")
    if used is not None and used >= level:
        return f"the subscription's weekly window is {used:.0%} used (stop at {level:.0%})"
    return None


class Abandoned(Exception):
    """Too many calls of the day failed (cybertron 1's fail-stop: a usage limit, auth, CLI errors): the day is dropped."""


class Tally:
    """A day's model calls and how many failed. At `llm.fail_stop_fraction` (default half) of max(planned decisions, calls so
    far), the day is abandoned and the run stops, to be resumed later (cybertron 1's failstop.py)."""

    def __init__(self, frac, planned):
        self.frac, self.planned = frac, planned
        self.calls, self.failed, self.errors = 0, 0, []

    def add(self, n_calls, errors) -> None:
        self.calls += n_calls
        self.failed += len(errors)
        self.errors += list(errors.items())
        if self.failed > 0 and self.failed >= self.frac * max(self.planned, self.calls):
            raise Abandoned(f"{self.failed} of {self.calls} model calls failed")


def _recorded(w, J, key, name, model, rec, text, opening, system, conv, schema, fuse, transit):
    """A request answered from the journal (resume, replay): the conversation is kept as it was, and nothing is asked."""
    out = rec["parsed"]
    if model == "bot":
        J.check_message(key, text)
        return out, {"model": "bot", "sent": text, "key": key}
    schema = schema or PR.schema_for(Here(w, name, transit=transit or fuse is not None), Mind(w, name))
    sent, ctx = conv.message(name, w.d, system, schema, text, opening)
    J.check_message(key, ctx["text"])
    conv.after(ctx, rec["raw"] if not (out or {}).get("_error") else None, {**(rec["usage"] or {}), "turn": "replayed"})
    usage = rec["usage"]                                                   # (no session to continue: the next live call starts one)
    return out or {}, {"model": model, "usage": usage, "seconds": 0.0, "thinking": rec["thinking"], "sent": ctx["text"],
                       "opening": ctx["text"] is opening, "key": key}


def decide(w, name, text, opening, system, backend, conv, talk=None, schema=None, fuse=None, transit=False, kind="decision") -> tuple[dict, dict]:
    """One request to an agent's responder (execution.md): keyed, and written with its answer to the journal as they exist."""
    model = w.s["people"][name]["model"]
    J = w.journal
    key = J.request_key(name) if J else None
    rec = J.answer(key) if J else None                                     # answered once, never asked again (execution.md)
    if rec is not None:
        return _recorded(w, J, key, name, model, rec, text, opening, system, conv, schema, fuse, transit)
    if J and J.strict:
        raise Stopped(f"no recorded answer for {key}")
    if model == "bot":
        if J:
            J.request(key, name, kind, None, None, system, None, text, "bot")
        try:
            out = bot_fuse(w, name, fuse) if fuse else bot_plan(w, name, talk)
        except Exception as e:                                             # the failure is the answer on record
            if J:
                J.response(key, [{"error": repr(e)[:500]}], {"_error": repr(e)[:500]}, None, {}, "bot")
            raise
        if J:
            J.response(key, [], out, None, {}, "bot")
        return out, {"model": "bot", "sent": text, "key": key}
    if model == "human":                                                   # human_play.md: shown exactly what a model would be
        if J is None:
            raise Stopped("a human responder needs the run's journal")
        schema = schema or PR.schema_for(Here(w, name, transit=transit or fuse is not None), Mind(w, name))
        sent, ctx = conv.message(name, w.d, system, schema, text, opening)
        c = ctx["conv"]
        J.request(key, name, kind, f"{name}@{c['day0']}", len(c["messages"]) // 2, c["system"], schema, ctx["text"], "human")
        raise HumanTurn([(key, name)])
    from cybertron import llm
    t0 = time.monotonic()
    attempts = []
    schema = schema or PR.schema_for(Here(w, name, transit=transit or fuse is not None), Mind(w, name))
    sent, ctx = conv.message(name, w.d, system, schema, text, opening)
    if J:
        c = ctx["conv"]
        J.request(key, name, kind, f"{name}@{c['day0']}", len(c["messages"]) // 2, c["system"], schema, ctx["text"], f"model:{model}")
    out, reasoning, usage = llm.call(backend, model, ctx["conv"]["system"], sent, schema,
                                     thinking_budget=int((w.spec.get("llm") or {}).get("thinking_budget", 2000)), attempts=attempts)
    raw = attempts[-1].get("raw") if attempts and attempts[-1].get("ok") and not (out or {}).get("_error") else None
    usage = conv.after(ctx, raw, usage)
    if J:
        J.response(key, attempts, out, reasoning, usage, usage.get("history") or ctx["transport"])
    return out or {}, {"model": model, "usage": usage, "seconds": round(time.monotonic() - t0, 1), "thinking": reasoning,
                       "sent": ctx["text"], "opening": ctx["text"] is opening, "key": key}


def _parallel(fn, jobs: dict, workers, tally=None) -> tuple[dict, dict, dict]:
    replies, meta, errors, waiting = {}, {}, {}, []
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(fn, *args): n for n, args in jobs.items()}
        for f in cf.as_completed(futs):
            n = futs[f]
            try:
                replies[n], meta[n] = f.result()
                if replies[n].get("_error"):
                    errors[n] = str(replies[n]["_error"])[:500]
                    replies[n] = {"actions": []}
            except HumanTurn as e:
                waiting += e.turns
            except Exception as e:
                replies[n], meta[n], errors[n] = {"actions": []}, {}, repr(e)[:500]
    if waiting:                                                            # the others' answers are kept; the run waits
        raise HumanTurn(sorted(waiting))
    if tally is not None:
        tally.add(len(jobs), errors)
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
            arrive(w, name, t, dawn=True)
    for sg in w.spec.get("signs") or []:
        if int(sg["day"]) - 1 == w.d:
            for node in (list(w.s["nodes"]) if sg.get("node") in (None, "all") else [sg["node"]]):
                w.event(node, "sign", sg["text"], about=[sg.get("about", "sky")], salience=float(sg.get("salience", 0.3)),
                        tags=sg.get("tags", ["season"]), sense=sg.get("sense", "sight"), dawn=True)


def arrive(w, name, t, dawn=True) -> None:
    """A traveller in: at dawn (set off at nightfall; with an evening, in at midday with half the day's units, D4-67) or at nightfall
    (set off in the morning)."""
    RD.arrived(w, name, t)                                                  # its notices on the way, remembered (D2-97)
    w.apply("arrive", t["to"], person=name)
    w.apply("set", t["to"], ref=("person", name), field="arrived", value=w.d)
    if EVN.on(w):
        w.apply("set", t["to"], ref=("person", name), field="arrived_by", value="nightfall" if t.get("by_day") else "midday")
        w.apply("set", t["to"], ref=("person", name), field="came_from", value=t["from"])
    from cybertron2.engine import herds as HD, layout as LY
    HD.arrive_with(w, name, t["to"])                                        # beasts it accompanied come in with it (D2-127)
    LY.learn_way(w, name, t["road"], t["to"], "came")                        # one knows the end one came in by (D2-90)
    LY.wear_way(w, t["road"], t["to"])
    w.event(t["to"], "arrive", f"{name} arrived from {w.s['nodes'][t['from']]['name']}" + ("" if dawn else " at nightfall"), actor=name,
            salience=0.7, tags=["travel"], dawn=dawn)


def morning_departures(w, today) -> None:
    """Those who set off this morning (D4-67): on the road all day; a one-day road brings them in by nightfall, a longer one at
    nightfall of its last day, with a night out for each day between."""
    tm = dict(today["travel_morning"])
    N.departures(w, {"travel": tm, "travel_choices": today.get("travel_choices") or {}})
    for name in sorted(tm):
        t = w.s["people"][name]["transit"]
        if not t:
            continue
        due = w.d + int(w.s["roads"][t["road"]]["days"]) - 1
        for m in [name] + [b for b, x in w.s["people"].items() if (x.get("transit") or {}).get("carried_by") == name]:
            w.apply("transit", t["road"], person=m, fields={"by_day": True, "arrive": due})
    arrive_evening(w)


def arrive_evening(w) -> None:
    for name in w.living():
        t = w.s["people"][name]["transit"]
        if t and t.get("by_day") and t["arrive"] <= w.d:
            if t.get("carried_by"):
                w.apply("arrive", t["to"], person=name)
                continue
            arrive(w, name, t, dawn=False)


def evening_step(w, names, results, budget, used, talk_log, openings, systems, backend, conv, workers, tally) -> None:
    """The evening at the hearth (evening.py): one call each, together, then one wave of answers for those asked something."""
    called = EVN.who_is_called(w, names)
    if not called:
        return {}
    arrive_evening(w)
    gather = {n: EVN.gathering(w, n) for n in called}
    keys = {n: g[0] for n, g in gather.items()}
    left = {n: max(0, budget.get(n, 0) - used.get(n, 0)) for n in called}
    for n in called:
        PC.store(w, n)["evening_shown"] = [x for x in results[n] if not x.startswith(PC.SPEECH)]
    texts = {}
    fold = [n for n in called if conv.ends(n, w.d) and w.d < w.days - 1] \
        if (w.spec or {}).get("memory_at_evening") else []                        # off by default: D4-80 (the evening's acts were lost)
    spans, mem_texts = {}, {}
    for n in fold:
        spans[n] = f"{PC._day(w, conv.c[n]['day0'] if n in conv.c else w.d)} to {PC._day(w, w.d)}"
        t = (MEM.request(w, n, Mind(w, n), results[n], [], spans[n]) if MEM.rewriting(w, n)
             else PR.memory_prompt(Mind(w, n), results[n], [], spans[n]))
        mem_texts[n] = t.replace(" Reply with JSON only.", "") + "\n\n" + MEM.kept_request(w, n)
    for n in called:
        a = w.s["people"][n]
        came = None
        if a.get("arrived") == w.d and a.get("arrived_by") == "nightfall" and a.get("came_from") in w.s["nodes"]:
            came = w.s["nodes"][a["came_from"]]["name"]
        others = [m for m in called if m != n and keys[m] == keys[n]]
        t = EVN.prompt(w, n, results[n], left[n], gather[n][1], others, came)
        if EVN.plans_at_hearth(w):
            t = t.replace(" Reply with JSON only.", " Put tomorrow's plan of work in \"actions\" too, after the night's acts (and a "
                                                     "\"fallback\"): you will be asked again at dawn only if something new has come. Reply "
                                                     "with JSON only.")
        skipped = (w.s["today"].get("skipped_morning") or {}).get(n)
        if skipped:                                                              # what the morning would have shown, not asked then
            t = skipped.replace("Plan your day. Reply with JSON only.", "").rstrip() + "\n\n" + t
        if n in mem_texts:
            t = t.replace(" Reply with JSON only.", "") + "\n\n" + mem_texts[n] + "\n\nReply with JSON only."
        texts[n] = TG.render(w, n, t)
    since = EVN.snapshot(w)
    rr, mm, ee = _parallel(lambda n: decide(w, n, texts[n], openings.get(n, texts[n]) + "\n\n" + texts[n], systems.get(n), backend, conv,
                                            kind="evening"), {n: (n,) for n in called}, workers, tally)
    box = {}
    for n in called:
        talk_log.setdefault(n, []).append({"wave": "evening", "prompt": texts[n], "reply": rr.get(n) or {},
                                           "usage": (mm.get(n) or {}).get("usage"), "thinking": (mm.get(n) or {}).get("thinking"),
                                           "error": ee.get(n)})
        if n in ee:
            continue
        r = dict(rr.get(n) or {})
        if EVN.plans_at_hearth(w):
            night_acts, tomorrow = EVN.split_plan(r)
            r["actions"] = night_acts
            w.apply("set", w.at(n), ref=("person", n), field="plan_next",
                    value={"day": w.d + 1, "actions": tomorrow, "fallback": [x for x in (r.get("fallback") or []) if isinstance(x, dict)]})
        spent = EVN.apply(w, n, r, keys, called, results[n], left[n], box)
        used[n] = used.get(n, 0) + spent
        left[n] -= spent
    folded = {}
    for n in fold:
        if n in ee:
            continue
        r = rr.get(n) or {}
        text = str(r.get("memory") or "").strip()
        if MEM.rewriting(w, n):
            MEM.keep(w, n, text, spans[n])
        elif text:
            PC.own_memory(w, n, spans[n], text)
        kept_out = MEM.kept_apply(w, n, r)
        w.s["today"].setdefault("memory_done", {})[n] = True
        folded[n] = {"agent": n, "span": spans[n], "memory": text, "kept": kept_out, "kept_lines": MEM.kept_lines_text(w, n),
                     "prompt": "(at the evening)", "usage": None, "error": None}
    asked = {n: EVN._requests(w, n, since) for n in called}
    woken = sorted(n for n in called if (box.get(n) or {}).get("heard") or asked[n])
    if not woken:
        return folded
    texts2 = {n: TG.render(w, n, EVN.answer_prompt(w, n, (box.get(n) or {}).get("heard", []), asked[n], left[n])) for n in woken}
    rr, mm, ee = _parallel(lambda n: decide(w, n, texts2[n], openings.get(n, texts2[n]) + "\n\n" + texts2[n], systems.get(n), backend, conv,
                                            kind="evening"), {n: (n,) for n in woken}, workers, tally)
    late = {}
    for n in woken:
        talk_log[n].append({"wave": "evening answer", "prompt": texts2[n], "reply": rr.get(n) or {}, "usage": (mm.get(n) or {}).get("usage"),
                            "thinking": (mm.get(n) or {}).get("thinking"), "error": ee.get(n)})
        if n in ee:
            continue
        spent = EVN.apply(w, n, rr.get(n) or {}, keys, called, results[n], left[n], late)
        used[n] = used.get(n, 0) + spent
    return folded


def meeting_step(w, names, replies, results, talk_log, openings, systems, backend, conv, workers, tally) -> None:
    """A meeting called for this morning (D4-77): those whose plan has `come` meet before work, for up to MEETING_WAVES rounds; all
    present hear what is said; what is offered there they witness; each may give their whole plan again."""
    by_node = {}
    for n in names:
        if w.at(n) is None or not w.s["people"][n]["alive"]:
            continue
        if any(str(a.get("do", "")).lower() == "come" for a in (replies[n].get("actions") or []) if isinstance(a, dict)):
            by_node.setdefault(w.at(n), []).append(n)
    for node, present in sorted(by_node.items()):
        m = Here(w, present[0]).meeting_today()
        if m is None or len(present) < 2:
            continue
        said = []
        for wave in range(MEETING_WAVES):
            texts = {n: TG.render(w, n, EVN.meeting_prompt(w, n, m, present, said)) for n in present}
            rr, mm, ee = _parallel(lambda n: decide(w, n, texts[n], openings.get(n, texts[n]) + "\n\n" + texts[n], systems.get(n), backend,
                                                    conv, kind="meeting"), {n: (n,) for n in present}, workers, tally)
            spoke = False
            for n in present:
                r = rr.get(n) or {}
                talk_log.setdefault(n, []).append({"wave": f"meeting {wave}", "prompt": texts[n], "reply": r,
                                                   "usage": (mm.get(n) or {}).get("usage"), "error": ee.get(n)})
                if n in ee:
                    continue
                for x in [x for x in (r.get("say") or []) if isinstance(x, dict) and str(x.get("text", "")).strip()][:MAX_SAY]:
                    line = f"{n}: {str(x['text'])[:600]}"
                    said.append(line)
                    results[n].append(f"You said (at the meeting): {str(x['text'])[:600]}")
                    for h in present:
                        if h != n:
                            PC.store(w, h)["today"]["heard"].append(f"{n} said at the meeting: {str(x['text'])[:600]}")
                    spoke = True
                for o in [o for o in (r.get("offers") or []) if isinstance(o, dict)][:3]:
                    try:
                        line = AG.make_offer(Here(w, n), Mind(w, n), o)
                    except Refused as e:
                        results[n].append(f"Refused: offer: {e}")
                        continue
                    results[n].append(line)
                    if line.startswith("You offered "):
                        oid = line[len("You offered "):].split(":")[0]
                        EVN.witness(w, present, f"{n} offered {AG.offer_text(Here(w, n), oid)}")
                        said.append(f"{n} offered: {AG.offer_text(Here(w, n), oid)}")
                        spoke = True
                if isinstance(r.get("actions"), list) and r["actions"]:
                    acts = [a for a in r["actions"] if isinstance(a, dict)]
                    if not any(str(a.get("do", "")).lower() == "come" for a in acts):
                        acts = [{"do": "come"}] + acts                           # one was there: the unit is given
                    replies[n] = {**replies[n], "actions": acts}
            if not spoke:
                break


MEETING_WAVES = 3


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
        for b in (rec.get("life") or {}).get("births", []):                 # lived through, not merely seen (D2-141)
            child = w.s["people"].get(b["child"]) or {}
            kind = {"f": "a daughter", "m": "a son"}.get(child.get("sex"), "a child")
            if n == b["mother"]:
                L.append(f"In the night you gave birth to {kind}, {b['child']}" + ("." if child.get("alive", True) else ", who did not live."))
            elif n == child.get("father") or n in (child.get("parents") or []):
                L.append(f"In the night {b['mother']} gave birth to your {kind[2:] if kind != 'a child' else 'child'}, {b['child']}.")
        care = rec.get("care") or {}
        for x in care.get("passed") or []:                                     # what one passed on to a child (D4-64)
            if x["by"] != n:
                continue
            if x["kept"]:
                L.append(f"{x['child']} will keep what you passed on: “{x['text']}”.")
            elif x["why"] == "full":
                L.append(f"{x['child']} holds as much as a child can; what you passed on was not kept.")
            else:
                L.append(f"{x['child']} will keep what {x['why']} passed on today, not yours.")
        if n in ((rec.get("life") or {}).get("lost") or []):
            L.append("You lost the child you were carrying.")
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
def fuse_calls(w, today, woke, results, talk_log, openings, systems, backend, conv, workers, extra_cost, tally=None):
    """One call each for the woken, appended to its own conversation; a meeting on the road has up to 3 waves of talk among everyone
    in it (D2-110), each wave's speech and offers shown to all in the next; the last reply's acts are done."""
    def ask(texts):
        def one(n):
            here, mind = Here(w, n, transit=True), Mind(w, n)
            op = openings.get(n) or PR.road_opening(here, mind)
            return decide(w, n, texts[n], op + "\n\n" + texts[n], conv.system(n, systems.get(n) or ""), backend, conv, fuse=woke[n],
                          kind="fuse")
        r, m, e = _parallel(one, {n: (n,) for n in texts}, workers, tally)
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
CARRY = ("today", "names", "at_day", "systems", "openings", "users", "replies", "meta", "errors", "first", "results", "woken", "talk_log",
         "talked", "attend", "plans", "budget", "used", "rep", "heavy", "settled", "road_rec", "woke", "rec", "nights", "last_system",
         "extra_cost")                                                    # what one step of the day hands the next


def _runner(J, cost, conv, scope) -> dict:
    """The runner's own state at a commit (journal.md, Checkpoints): each agent's running conversation, the cost so far, and what the
    day's steps carry between them. Long texts are stored once as blobs and referred to by sha."""
    def slim(x):
        if isinstance(x, str) and len(x) > 200:
            return {"$blob": J.blob(x)}
        if isinstance(x, dict):
            return {str(k): slim(v) for k, v in x.items()}
        if isinstance(x, (list, tuple, set)):
            return [slim(v) for v in x]
        return x
    convs = {n: {**{k: v for k, v in c.items() if k not in ("messages", "session")}, "messages": slim(c["messages"])}
             for n, c in conv.c.items()}
    return {"cost": cost, "conversations": convs, "carry": slim({k: scope[k] for k in CARRY if k in scope})}


def _abandon(J, out, day, days, tally, why) -> str:
    """Drop the day (cybertron 1's fail-stop): its steps are marked aborted and its failed calls set aside, so that a resume plays it
    again, reusing the answers that came and asking the failed ones again; STOPPED.md says why."""
    J.abandon_day(day)
    kept = "the start of the run" if day == 0 else f"the end of day {day}"
    samples, seen = [], set()
    for who, err in tally.errors:
        if str(err)[:120] not in seen:
            seen.add(str(err)[:120])
            samples.append(f"- {who}: {str(err)[:400]}")
    (out / "STOPPED.md").write_text("\n".join([
        "# Run stopped", "", f"- When: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- Day {day + 1} of {days} was abandoned: {why} (the stop is at {tally.frac:.0%} of max({tally.planned} planned decisions, "
        "calls made)).",
        f"- The run is kept as of {kept}; the day's answers that came are kept and reused, the failed calls are set aside (journal "
        "table `abandoned`) and will be asked again.",
        f"- Continue with `python -m cybertron2.engine resume {out}` once the cause is fixed (a usage limit: after it resets).", "",
        "## Sample errors", ""] + samples[:5]) + "\n")
    return f"day {day + 1}: {why}; the day was abandoned and the run kept as of {kept}. Resume to play day {day + 1} again."


def run(spec_path, out_dir, backend=None, days=None, workers=12, bots=False, seed=None, until=None, mode="start", responders=None):
    """mode "start": a new run from a world file; "resume": go on with the run in out_dir from its journal (every answered request
    reused, the first step not committed run again live); "replay": play the run in out_dir again from its record alone, in a
    scratch copy, checking every committed step's state against its checkpoint, and return what was found. `until`: pause after
    that step's commit (execution.md)."""
    out = Path(out_dir)
    if mode == "start":
        spec = load_spec(spec_path)
        if seed is not None:
            spec["seed"] = int(seed)
        if days:
            spec["days"] = int(days)
        if bots:
            spec["bots"] = True                                             # those who come of age are bots too
            for a in spec["agents"].values():
                if a.get("model"):
                    a["model"] = "bot"
        for name, who in (responders or {}).items():                        # --as NAME=human|bot|model:<id>
            spec["agents"][name]["model"] = who.split(":", 1)[1] if who.startswith("model:") else who
    else:
        src = Path(out_dir) / "run.db"
        if not src.exists():
            raise SystemExit(f"{src}: no journal to {mode} from")
        spec = json.loads(dict(JN.read(src, "SELECT key, value FROM meta"))["spec"])
        backend = backend or json.loads((Path(out_dir) / "run.json").read_text()).get("backend")
        if mode == "continue":
            at = json.loads(dict(JN.read(src, "SELECT key, value FROM meta"))["continue"])["at"]
            restored = JN.checkpoint(src, at)
            if days:                                                        # played on past the world's own length
                spec["days"] = int(days)
        if mode == "replay":                                                # never touch the run itself
            import shutil
            import tempfile
            out = Path(tempfile.mkdtemp(prefix="replay_"))
            import sqlite3
            db = sqlite3.connect(str(src))
            db.execute("PRAGMA wal_checkpoint(FULL)")                       # fold the WAL in before copying
            db.close()
            shutil.copy(src, out / "run.db")
    w = World(spec)
    start_day = 0
    if mode == "continue":                                                  # the world as it was at the end of that day
        w.s = restored["world"]
        start_day = int(at.split(".")[0][1:]) + 1
    backend = backend or os.environ.get("LLM_BACKEND") or "claude_code"
    out.mkdir(parents=True, exist_ok=True)
    systems = {n: PR.system_prompt(Here(w, n), Mind(w, n)) for n in w.agents_acting()}
    (out / "run.json").write_text(json.dumps({"spec": spec, "backend": backend, "systems": systems,
                                              "models": {n: a["model"] for n, a in w.s["people"].items()}}, indent=1))
    files = {k: open(out / f"{k}.jsonl", "w") for k in ("turns", "days", "perception", "memory")}
    conv = Conversations(out, chunk=int((spec.get("memory") or {}).get("chunk", 3)), backend=backend)
    if mode == "start":
        for f in ("run.db", "run.db-wal", "run.db-shm"):                   # a fresh run: a fresh journal
            (out / f).unlink(missing_ok=True)
    J = w.journal = JN.Journal(out / "run.db")
    if mode == "start":
        J.start(spec, w.seed, {n: (a["model"] if a.get("model") in (None, "bot") else f"model:{a['model']}") for n, a in w.s["people"].items()})
        J.until = until
    elif mode == "continue":
        J.until = until
        if days:
            J.meta("spec", spec)                                            # a later resume plays to the new length
    else:
        J.resume(strict=mode == "replay", until=until)
    J.after_commit = lambda step: BR.after_commit(w, J, step)
    stopped = None
    if mode == "resume" and (out / "STOPPED.md").exists():               # a resumed run shows only a current stop
        with open(out / "stop_history.md", "a") as h:
            h.write((out / "STOPPED.md").read_text() + "\n")
        (out / "STOPPED.md").unlink()
    cost = 0.0
    last_system = dict(systems)
    extra_cost = [0.0]
    if mode == "continue":                                                  # the runner as it was: conversations, cost, systems
        r = JN.unslim(restored["runner"], out / "run.db")
        cost = float(r["cost"])
        conv.c = {n: {**c, "session": None} for n, c in r["conversations"].items()}
        last_system.update(r["carry"].get("last_system") or {})
    finished = False
    try:
        for day in range(start_day, w.days):
            if not (J.replaying and f"d{day}.dawn" in J.committed) and mode != "replay":
                why = _week_stop(spec)
                if why:
                    raise UsageStop(why)
            J.open_step(day, "dawn")
            w.s["day"] = day
            w.s["events"] = []
            today = w.s["today"] = blank_today()
            dawn(w)
            PC.dawn(w)
            J.commit(w.s, _runner(J, cost, conv, locals()))
            J.open_step(day, "decide")
            names = w.agents_acting()
            at_day = {n: w.at(n) for n in names}
            systems = {n: PR.system_prompt(Here(w, n), Mind(w, n)) for n in names}
            turn = VW.turn if VW.on(w) else PR.turn_prompt                     # the message from beliefs (38.40 §9), or as before
            openings = {n: TG.render(w, n, turn(Here(w, n), Mind(w, n), opening=True)) for n in names}
            users = {n: TG.render(w, n, turn(Here(w, n), Mind(w, n), opening=False)) for n in names}
            if EVN.on(w):                                                       # a meeting called for this morning (D4-77)
                for n in names:
                    blk = EVN.meeting_block(w, n)
                    if blk:
                        users[n] = users[n].replace("Plan your day. Reply with JSON only.", blk + "\n\nPlan your day. Reply with JSON only.")
                        openings[n] = openings[n].replace("Plan your day. Reply with JSON only.", blk + "\n\nPlan your day. Reply with JSON only.")
            planned = {}
            if EVN.plans_at_hearth(w):                                          # planned at the hearth: asked at dawn only if needed
                for n in names:
                    pn = w.s["people"][n].get("plan_next") or {}
                    if int(pn.get("day", -1)) == day and not EVN.needs_morning(w, n):
                        planned[n] = {"why": "(planned at the hearth last night)", "actions": pn.get("actions") or [],
                                      "fallback": pn.get("fallback") or []}
                        today.setdefault("skipped_morning", {})[n] = users[n]
            tally = Tally(float(((w.spec.get("llm") or {}).get("fail_stop_fraction")) or 0.5), len(names))
            replies, meta, errors = _parallel(lambda n: decide(w, n, users[n], openings[n], systems[n], backend, conv),
                                              {n: (n,) for n in names if n not in planned}, workers, tally)
            for n, r in planned.items():
                replies[n], meta[n] = r, {"sent": "(no morning call: planned at the hearth)"}
            first = {n: dict(replies[n]) for n in names}
            results = {n: ([f"(Your reply could not be used, so you did nothing: {errors[n][:160]})"] if n in errors else []) for n in names}
            for n in names:
                results[n] += PC.apply_notes(Mind(w, n), replies[n])
            J.commit(w.s, _runner(J, cost, conv, locals()))
            J.open_step(day, "talk.0")
            woken = talk(w, names, replies, results)
            talk_log = {n: [] for n in names}
            talked = set()
            waves = 1 if EVN.on(w) else WAVES                                  # with an evening, one wave of answers (D4-65)
            for wave in range(waves):
                if not woken:
                    break
                if wave:
                    J.commit(w.s, _runner(J, cost, conv, locals()))
                    J.open_step(day, f"talk.{wave}")
                texts = {n: TG.render(w, n, PR.talk_prompt(Here(w, n), Mind(w, n), b["heard"], b["also"], b["offers"], b["opened"], b["cards"],
                                           sum(1 for x in results[n] if x.startswith("You told ")))) for n, b in woken.items()}
                rr, mm, ee = _parallel(lambda n: decide(w, n, texts[n], openings[n] + "\n\n" + texts[n], systems[n], backend, conv, woken[n],
                                                        kind="talk"),
                                       {n: (n,) for n in woken}, workers, tally)
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
                if wave == waves - 1:
                    break
            if EVN.on(w):
                meeting_step(w, names, replies, results, talk_log, openings, systems, backend, conv, workers, tally)
            J.commit(w.s, _runner(J, cost, conv, locals()))
            J.open_step(day, "work")
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
                    if i >= len(plans[n]) or not w.s["people"][n]["alive"] or n in today["travel"] or n in heavy \
                            or n in today.get("travel_morning", {}):
                        continue
                    here, mind = Here(w, n), Mind(w, n)
                    a = plans[n][i]
                    morning = EVN.on(w) and str(a.get("do", "")).lower() == "travel" and str(a.get("when") or "").lower() == "morning"
                    if morning and used[n] > 0:                                # setting off in the morning: the day's first act (D4-67)
                        results[n].append("Refused: travel: to set off in the morning, make it your first act; to go after the day's "
                                          "work, set off at nightfall")
                        continue
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
                        if n in today.get("travel_morning", {}):
                            used[n] = budget[n]                                 # the day spent walking
                        results[n].append(res)
                    elif res in results[n]:
                        rep[n][res] = rep[n].get(res, 1) + 1
                    else:
                        results[n].append(res)
            for n in order:                                                  # units left over: one's own fallback, in order (D4-76)
                fb = [x for x in (replies[n].get("fallback") or []) if isinstance(x, dict)][:3]
                if not fb or not w.s["people"][n]["alive"] or n in today["travel"] or n in heavy or n in today.get("travel_morning", {}):
                    continue
                for _ in range(budget[n] + 1):
                    if used[n] >= budget[n]:
                        break
                    done = False
                    for a in fb:
                        here, mind = Here(w, n), Mind(w, n)
                        c = V.cost(here, a)
                        if c <= 0 or used[n] + c > budget[n] or str(a.get("do", "")).lower() == "travel":
                            continue
                        res = V.do(here, mind, a)
                        if res.startswith("Refused"):
                            continue
                        used[n] += c
                        results[n].append(res + " (your fallback)")
                        done = True
                        if used[n] >= budget[n]:
                            break
                    if not done:
                        break
            if heavy:                                                        # too heavy to set off: what to leave, and with whom (D4-32)
                texts = {n: PR.lighten_prompt(Here(w, n), Mind(w, n), heavy[n], results[n]) for n in heavy}
                lr, lm, le = _parallel(lambda n: decide(w, n, texts[n], openings[n] + "\n\n" + texts[n], systems[n], backend, conv,
                                                        kind="lighten"),
                                       {n: (n,) for n in heavy}, workers, tally)
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
            if today.get("travel_morning"):                                    # set off this morning: in by nightfall (D4-67)
                morning_departures(w, today)
            from cybertron2.engine import layout as LY
            LY.routes(w, today)                                             # each one's day as a chain of parcels (D4-62)
            J.commit(w.s, _runner(J, cost, conv, locals()))
            if EVN.on(w):                                                       # the evening at the hearth (D4-65, D4-66)
                J.open_step(day, "evening")
                folded = evening_step(w, names, results, budget, used, talk_log, openings, systems, backend, conv, workers, tally)
                for n, mrec in folded.items():
                    files["memory"].write(json.dumps({"day": day, **mrec}) + "\n")
                J.commit(w.s, _runner(J, cost, conv, locals()))
            J.open_step(day, "settle")
            today["partners"] = LF.settle(w, today)                             # partnerships both chose (D2-140)
            today["children_work"] = LF.children_work(w)                        # the head's standing order (D2-148)
            settled = AG.settle(w)
            for n, lines in list(ST.settle_teaching(w, today).items()) + list(ST.settle_joins(w, today).items()):
                results.setdefault(n, []).extend(lines)
            ST.settle_thefts(w, today, attend)
            w.s["left"] = [x for x in w.s.get("left", []) if x["day"] >= day - 1] + [{**x, "day": day} for x in today["left"]]
            J.commit(w.s, _runner(J, cost, conv, locals()))
            J.open_step(day, "night")
            N.departures(w, today)                                              # nightfall: those leaving are on their first stretch
            road_rec = RD.night(w, today)                                       # the roads tonight (world/roads.md)
            woke = FU.plan(w, today)                                            # fuse events: the urgent calls (D2-80 to D2-84)
            last_system.update(systems)
            if woke:
                fuse_calls(w, today, woke, results, talk_log, openings, last_system, backend, conv, workers, extra_cost, tally)
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
            J.commit(w.s, _runner(J, cost, conv, locals()))
            J.open_step(day, "memory")
            ending = [n for n in names if w.s["people"][n]["alive"] and conv.ends(n, day) and day < w.days - 1
                      and n not in today.get("memory_done", {})]                 # set off tonight too; not if written at the evening
            if ending:
                spans = {n: f"{PC._day(w, conv.c[n]['day0'] if n in conv.c else day)} to {PC._day(w, day)}" for n in ending}
                rewrite = {n: MEM.rewriting(w, n) for n in ending}            # D4-61: one memory, rewritten (append for weak models)
                texts = {n: (MEM.request(w, n, Mind(w, n), results[n], nights.get(n, []), spans[n]) if rewrite[n]
                             else PR.memory_prompt(Mind(w, n), results[n], nights.get(n, []), spans[n])) for n in ending}
                texts = {n: t.replace(" Reply with JSON only.", "") + "\n\n" + MEM.kept_request(w, n) + "\n\nReply with JSON only."
                         for n, t in texts.items()}                             # kept for good, its own question (D4-64)
                keep = {n: json.loads(conv.c[n]["schema"]) for n in ending if n in conv.c}   # the stretch's own schema: it continues
                mr, mm, me = _parallel(lambda n: decide(w, n, texts[n], openings[n] + "\n\n" + texts[n], systems[n], backend, conv,
                                                        schema=keep.get(n), transit=True, kind="memory"),
                                       {n: (n,) for n in ending}, workers, tally)
                for n in ending:
                    text = str((mr.get(n) or {}).get("memory") or "").strip()
                    if rewrite[n]:
                        MEM.keep(w, n, text, spans[n])
                    elif text:
                        PC.own_memory(w, n, spans[n], text)
                    kept_out = MEM.kept_apply(w, n, mr.get(n) or {})
                    u = (mm.get(n) or {}).get("usage") or {}
                    cost += float(u.get("cc_equiv_usd") or 0.0)
                    files["memory"].write(json.dumps({"day": day, "agent": n, "span": spans[n], "memory": text, "kept": kept_out,
                                                      "kept_lines": MEM.kept_lines_text(w, n), "prompt": texts[n],
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
            J.commit(w.s, _runner(J, cost, conv, locals()))
            print(f"day {day + 1}: alive {len(w.living())}, missed {rec['missed']}, deaths {rec['deaths']}, talked {len(talked)}, "
                  f"agreements {len(rec['agreements_made'])}, taught {len(today['teach'])}, thefts {len(today['thefts'])}, "
                  + (f"born {[b['child'] for b in rec['life']['births']]}, " if rec["life"]["births"] else "") +
                  f"errors {len(errors)}, cost ${cost:.2f}", flush=True)
            if not w.living():
                break
        finished = True
    except JN.Paused as e:
        print(str(e), flush=True)
    except Abandoned as e:
        stopped = _abandon(J, out, day, w.days, tally, str(e))
        print(stopped, flush=True)
    except HumanTurn as e:
        stopped = f"waiting for {e}: answer with `play {out} --as NAME` (or the api), then the run goes on"
        print(stopped, flush=True)
    except UsageStop as e:
        stopped = f"stopped before day {day}: {e}. Resume with `python -m cybertron2.engine resume {out}`."
        (out / "STOPPED.md").write_text(f"# Run stopped\n\n- {stopped}\n")
        print(stopped, flush=True)
    if stopped is None:
        w.save(out / "state.json")
    if mode != "replay" and finished:
        J.meta("ended", {"day": w.d, "alive": len(w.living()), "cost_usd": round(cost, 4)})
    report = {"checked": J.checked, "mismatches": J.mismatches, "at": J.step}
    J.close()
    w.journal = None
    conv.close()
    for f in files.values():
        f.close()
    return report if mode == "replay" else out


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
    r.add_argument("--until", help="pause after this step's commit, e.g. d10.memory")
    r.add_argument("--as", dest="as_", action="append", default=[], help="NAME=human|bot|model:<id>")
    g = sub.add_parser("resume")
    g.add_argument("run")
    g.add_argument("--until")
    g.add_argument("--backend")
    g.add_argument("--workers", type=int, default=12)
    p = sub.add_parser("replay")
    p.add_argument("run")
    p.add_argument("--to", help="stop after this step")
    x = sub.add_parser("rewind")
    x.add_argument("run")
    x.add_argument("--to", required=True)
    x.add_argument("--out", required=True)
    f = sub.add_parser("fork")
    f.add_argument("run")
    f.add_argument("--at", required=True)
    f.add_argument("--out", required=True)
    f.add_argument("--apply", help="a YAML list of interventions: {after, op, place, args, note}")
    f.add_argument("--replicates", type=int)
    f.add_argument("--as", dest="as_", action="append", default=[], help="NAME=model:<id>|bot|human")
    f.add_argument("--backend")
    f.add_argument("--workers", type=int, default=12)
    f.add_argument("--no-play", action="store_true", help="make the fork without playing it on")
    c = sub.add_parser("continue")
    c.add_argument("run")
    c.add_argument("--at", required=True)
    c.add_argument("--out", required=True)
    c.add_argument("--backend")
    c.add_argument("--workers", type=int, default=12)
    c.add_argument("--days", type=int, help="play on to this many days in all (past the world's own length)")
    b = sub.add_parser("branches")
    b.add_argument("run")
    e = sub.add_parser("export")
    e.add_argument("runs", nargs="+")
    e.add_argument("--out", required=True)
    i = sub.add_parser("import")
    i.add_argument("src")
    i.add_argument("--out", required=True)
    pb = sub.add_parser("publish")
    pb.add_argument("runs", nargs="+")
    pb.add_argument("--staging")
    pb.add_argument("--repo")
    pb.add_argument("--push", action="store_true")
    ft = sub.add_parser("fetch")
    ft.add_argument("run_id")
    ft.add_argument("--revision")
    ft.add_argument("--repo")
    ft.add_argument("--out", required=True)
    cx = sub.add_parser("context")
    cx.add_argument("run")
    cx.add_argument("key", nargs="?", help="a request key; without it, the agent's latest")
    cx.add_argument("--agent")
    fr = sub.add_parser("frames")
    fr.add_argument("run")
    fr.add_argument("--out", required=True)
    pl = sub.add_parser("play")
    pl.add_argument("run")
    pl.add_argument("--as", dest="agent", required=True)
    pl.add_argument("--backend")
    sv = sub.add_parser("serve")
    sv.add_argument("run")
    sv.add_argument("--port", type=int, default=8765)
    sv.add_argument("--backend")
    sv.add_argument("--new", help="a world file: start a new run in RUN first, with --as played by a person")
    sv.add_argument("--as", dest="agent", help="the person you play (with --new; the page shows only their turns)")
    sv.add_argument("--days", type=int)
    sv.add_argument("--bots", action="store_true", help="with --new: everyone else scripted (no model calls), to try it out")
    dp = sub.add_parser("dump")
    dp.add_argument("run")
    dp.add_argument("--table", default="events")
    args = ap.parse_args(argv)
    if args.cmd == "run":
        print(run(args.spec, args.out, args.backend, args.days, args.workers, args.bots, args.seed, until=args.until,
                  responders=dict(a.split("=", 1) for a in args.as_)))
    elif args.cmd == "resume":
        print(run(None, args.run, args.backend, workers=args.workers, until=args.until, mode="resume"))
    elif args.cmd == "rewind":
        print(BR.rewind(args.run, args.to, args.out))
    elif args.cmd == "fork":
        import yaml
        ivs = yaml.safe_load(open(args.apply)) if args.apply else None
        who = dict(a.split("=", 1) for a in args.as_)
        outs = (BR.replicates(args.run, args.at, args.out, args.replicates, ivs, who) if args.replicates
                else [BR.fork(args.run, args.at, args.out, ivs, who)])
        for o in outs:
            print(o if args.no_play else run(None, o, args.backend, workers=args.workers, mode="resume"))
    elif args.cmd == "continue":
        BR.continue_(args.run, args.at, args.out)
        print(run(None, args.out, args.backend, days=args.days, workers=args.workers, mode="continue"))
    elif args.cmd == "branches":
        print(json.dumps(BR.branches(args.run), indent=1))
    elif args.cmd in ("export", "import", "publish", "fetch"):
        from cybertron2.engine import exchange as EX
        if args.cmd == "export":
            for r in args.runs:
                print(EX.export(r, args.out))
        elif args.cmd == "import":
            print(EX.import_(args.src, args.out))
        elif args.cmd == "publish":
            root = EX.publish(args.runs, args.staging, args.push, args.repo)
            print(f"{'uploaded' if args.push else 'staged (dry run: add --push to upload)'}: {root}")
        else:
            print(EX.fetch(args.run_id, args.out, args.revision, args.repo))
    elif args.cmd == "context":
        from cybertron2.engine import views as VW
        key = args.key or [r for r in VW.requests(args.run, agent=args.agent)][-1]["key"]
        print(json.dumps(VW.context(args.run, key), indent=1))
    elif args.cmd == "frames":
        from cybertron2.engine import views as VW
        Path(args.out).mkdir(parents=True, exist_ok=True)
        (Path(args.out) / "layout.json").write_text(json.dumps(VW.layout(args.run)))
        (Path(args.out) / "frames.json").write_text(json.dumps(VW.frames(args.run)))
        print(args.out)
    elif args.cmd == "play":
        from cybertron2.engine import api as API
        API.play(args.run, args.agent, args.backend)
    elif args.cmd == "serve":
        from cybertron2.engine import api as API
        API.serve(args.run, args.port, args.backend, new=args.new, agent=args.agent, days=args.days, bots=args.bots)
    elif args.cmd == "dump":
        from cybertron2.engine import views as VW
        rows = {"events": VW.events, "changes": VW.changes, "calls": VW.calls, "steps": VW.steps}[args.table](args.run)
        for r in rows:
            print(json.dumps(r))
    elif args.cmd == "replay":
        rep = run(None, args.run, until=args.to, mode="replay")
        print(json.dumps(rep, indent=1))
        if rep["mismatches"]:
            raise SystemExit(1)
