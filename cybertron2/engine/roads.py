"""Roads: stretches, landmarks, crossing, daily notices, meetings and finds (world/roads.md, information/noticing.md "On the road";
D2-81, D2-86, D2-97, D2-104 to D2-110, D2-113).

A road with a terrain is one place with parts: one stretch a day of its length, each with a terrain and 0 to 2 landmarks. Each
night, after the departures, `night` places every party on its stretch, settles minor trouble by its choices at departure (or the
default), feeds those passing good places, gathers what each notices, and finds the meetings and the finds worth taking, which the
fuse sub-step turns into urgent calls (fuse.py: kinds "meeting", "find", "crossing", registered here). Every road has a terrain, a farm
track unless its world says otherwise (D2-122); a road made bare holds nothing (D2-104), the switch for a comparison arm.

Positions are counted from the road's `a` end: a party on its k-th stretch from its own start is at k (from a) or n+1-k (from b).
"""
from __future__ import annotations

from types import SimpleNamespace

from cybertron2.engine import environment as EV, fuse as FU, things as TH
from cybertron2.engine.data import ITEMS, LANDMARKS, ROADS, TERRAIN, WEATHER
from cybertron2.engine.world import Refused


# ---------------------------------------------------------------------- the road's parts
def active(road) -> bool:
    """A bare road holds nothing (D2-104): only a switch for a comparison arm, since every road has a terrain (D2-122)."""
    return not road.get("bare") and (bool(road.get("terrain")) or any(s.get("landmarks") for s in road.get("stretches") or []))


def build(extra: dict, days: int) -> dict:
    """A road's terrain and stretches from its spec (`terrain`, `stretches`: {k: {terrain, landmarks}} counted from its first node);
    a road given no terrain is a farm track (D2-122); `bare: true` makes it hold nothing (the comparison switch)."""
    if extra.get("bare"):
        return {"terrain": None, "bare": True, "stretches": [{"terrain": None, "landmarks": []} for _ in range(days)]}
    terrain = extra.get("terrain") or ROADS["terrain"]
    st = []
    given = {int(k): v for k, v in (extra.get("stretches") or {}).items()}
    for k in range(1, days + 1):
        x = given.get(k) or {}
        lms = [({"kind": l} if isinstance(l, str) else dict(l)) for l in x.get("landmarks") or []]
        st.append({"terrain": x.get("terrain") or terrain, "landmarks": lms})
    return {"terrain": terrain, "stretches": st}


def stretch_of(w, t) -> int:
    """The stretch a traveller is on tonight, from its own start (1 the first night)."""
    n = w.s["roads"][t["road"]]["days"]
    return max(1, min(n, n - (t["arrive"] - w.d) + 1))


def position(w, t) -> int:
    """Its stretch counted from the road's `a` end."""
    r = w.s["roads"][t["road"]]
    k = stretch_of(w, t)
    return k if t["from"] == r["a"] else r["days"] + 1 - k


def stretch(w, road_id, pos) -> dict:
    return w.s["roads"][road_id]["stretches"][pos - 1]


def stretch_name(w, road_id, pos) -> str:
    r = w.s["roads"][road_id]
    st = stretch(w, road_id, pos)
    lm = [LANDMARKS[l["kind"]]["words"] for l in st["landmarks"]]
    a, b = w.s["nodes"][r["a"]]["name"], w.s["nodes"][r["b"]]["name"]
    return (" and ".join(lm) + f" on the road between {a} and {b}") if lm else f"the {st['terrain'] or 'road'} between {a} and {b}"


def landmark_key(road_id, pos, kind) -> str:
    return f"{road_id}#{pos}#{kind}"


# ---------------------------------------------------------------------- landmark states (from the weather: environment.py)
def challenge(w, road_id, pos, lm) -> str:
    """'' or the trouble this landmark gives tonight: a ford high, a bridge down, a pass snowed."""
    kind = LANDMARKS[lm["kind"]].get("challenge")
    if kind == "high":
        since = EV.since_heavy_rain(w)
        wet_week = EV.spell(w) == "wet" and any(EV.spell(w, d) == "wet" for d in range(max(0, w.d - 7), w.d - 5))
        return "high" if (since is not None and since < 2) or wet_week or lm.get("state") == "high" else ""
    if kind == "down":
        return "down" if lm.get("state") == "down" else ""
    if kind == "snowed":
        return "snowed" if (w.calendar()["season"] == "winter" and (EV.weather(w) == "snow" or EV.snow_lying(w))) \
            or lm.get("state") == "snowed" else ""
    return ""


CHALLENGE_WORDS = {"high": "the ford was high", "down": "the bridge was down", "snowed": "the pass was snowed up"}


# ---------------------------------------------------------------------- parties on the roads tonight
def parties(w) -> dict:
    """Travellers on active roads, grouped: those who left one end the same day for the same place travel together."""
    out = {}
    for n, a in w.s["people"].items():
        t = a.get("transit")
        if not a["alive"] or not t or not active(w.s["roads"][t["road"]]):
            continue
        key = (t["road"], t["from"], t["to"], t["left"], t["arrive"])
        out.setdefault(key, []).append(n)
    return {k: sorted(v) for k, v in out.items()}


def experience(w, name, key) -> float:
    """Trouble at a landmark halves after about five crossings (D2-106)."""
    n = float((w.s["mind"][name].get("landmarks") or {}).get(key, {}).get("crossed", 0))
    return 0.5 ** (n / float(ROADS["experience"]))


def knows(w, name, key) -> bool:
    return key in (w.s["mind"][name].get("landmarks") or {})


def _learn(w, name, road_id, pos, lm, crossed=True):
    k = landmark_key(road_id, pos, lm["kind"])
    rec = w.s["mind"][name].setdefault("landmarks", {}).setdefault(k, {"crossed": 0, "words": LANDMARKS[lm["kind"]]["words"],
                                                                         "road": road_id, "pos": pos, "kind": lm["kind"]})
    if crossed:
        rec["crossed"] += 1


def _note(w, name, text, first=False):
    """A line for "On the way" (D2-97). What happened (trouble, a stop, a meeting, a find) goes before what was merely seen, so the
    arrival lines keep it when there are many."""
    t = w.s["people"][name]["transit"]
    if t is None:
        return
    t.setdefault("notices", [])
    if text in t["notices"]:
        return
    if first:
        k = int(t.get("notices_first", 0))
        t["notices"].insert(k, text)
        t["notices_first"] = k + 1
    else:
        t["notices"].append(text)


def night(w, today) -> dict:
    """The roads tonight (D2-97, D2-104 to D2-110, D2-113): positions, trouble, good places, notices, meetings and finds."""
    rec = {"trouble": [], "meetings": [], "finds": [], "good": []}
    today["road"] = {"meetings": [], "finds": [], "crossings": [], "fed": {}}
    today["road"].update(herds=[], splits=[])
    ps = parties(w)
    from cybertron2.engine import herds as HD
    HD.follow(w)                                                            # herds a party accompanies go with it (D2-127)
    for key, members in ps.items():
        t = w.s["people"][members[0]]["transit"]
        pos = position(w, t)
        st = stretch(w, t["road"], pos)
        for lm in st["landmarks"]:
            _landmark(w, today, rec, members, t, pos, lm)
        _notices(w, members, t, pos, ps)
        _finds(w, today, rec, members, t, pos)
        _herd_finds(w, today, rec, members, t, pos)
        _driven_splits(w, today, rec, members, t, pos)
    _meetings(w, today, rec, ps)
    for key, members in ps.items():                                         # what each party leaves behind it (D2-88)
        t = w.s["people"][members[0]]["transit"]
        if t is not None:
            leave_traces(w, members, t, position(w, t))
    return rec


# ---------------------------------------------------------------------- traces (D2-88)
def leave_traces(w, members, t, pos):
    """Tracks (and cart ruts, a fire's ashes) on the stretch a party spent the night on; they fade (ROADS trace_days)."""
    kinds = ["tracks"]
    if any(w.goods(w.hands(n)).get("handcart", 0) >= 1 for n in members):
        kinds.append("ruts")
    if any(n in (w.s.get("today") or {}).get("fire", {}) for n in members):
        kinds.append("ashes")
    toward = w.s["nodes"][t["to"]]["name"]
    for k in kinds:
        w.s.setdefault("traces", []).append({"road": t["road"], "pos": pos, "day": w.d, "kind": k, "n": len(members), "toward": toward,
                                             "by": list(members)})
    w.s["traces"] = [x for x in w.s["traces"] if w.d - x["day"] <= int(ROADS["trace_days"][x["kind"]])]


def _landmark(w, today, rec, members, t, pos, lm):
    d = LANDMARKS[lm["kind"]]
    road_id = t["road"]
    lkey = landmark_key(road_id, pos, lm["kind"])
    if d.get("good"):
        stop = str((t.get("choices") or {}).get("stop at") or "").lower()
        if stop and stop in (d["words"].lower(), lm["kind"]) and not t.get("stopped") and knows(w, members[0], lkey):
            days = max(1, int((t.get("choices") or {}).get("days") or 1))   # stopping only by choice, only where known (D2-109)
            for n in members:
                tt = w.s["people"][n]["transit"]
                tt.update(stopped=True, stop_until=w.d + days - 1, arrive=tt["arrive"] + days)
                _note(w, n, f"you stopped {days} day{'s' if days > 1 else ''} at {d['words']}", first=True)
        if t.get("stop_until") is not None and w.d <= t["stop_until"]:
            for n in members:
                today["road"].setdefault("camp", {})[n] = True
                q = round(float(ROADS["good"]["gather"][1]) if w.calendar()["season"] in d.get("seasons", []) else 0.5, 2)
                w.apply("create", road_id, dst=w.hands(n), item="wild food", qty=q, why="gathered at a stop")
        if w.calendar()["season"] in d.get("seasons", []):
            g = ROADS["good"]
            for n in members:
                mult = float(g["known"]) if knows(w, n, lkey) else 1.0
                if (t.get("choices") or {}).get("gather"):
                    q = round(min(2.0, float(g["gather"][0]) * mult), 2)
                    w.apply("create", road_id, dst=w.hands(n), item="wild food", qty=q, why="gathered on the way")
                    _note(w, n, f"you gathered {q:g} wild food at {d['words']}", first=True)
                else:
                    today["road"]["fed"][n] = float(g["fed"])
                    _note(w, n, f"you ate well on the way, at {d['words']}")
                rec["good"].append(n)
        for n in members:
            _learn(w, n, road_id, pos, lm, crossed=True)
        return
    ch = challenge(w, road_id, pos, lm)
    for n in members:
        _learn(w, n, road_id, pos, lm, crossed=not ch)
    if not ch:
        for n in members:
            _note(w, n, f"you passed {d['words']}")
        return
    choice = str((t.get("choices") or {}).get("on trouble") or d.get("default") or "wait").lower()
    lead = members[0]
    exp = experience(w, lead, lkey)
    risk = _risk(w, members, lm, ch, exp)
    serious = risk["death"] >= float(ROADS["call"]["death"]) or risk["loss"] >= float(ROADS["call"]["loss"])
    minor_call = w.rng("road-call", w.d, lead, lkey).random() < float(ROADS["call"]["minor"])
    noticed = w.rng("road-notice", w.d, lead, lkey).random() < min(1.0, TH.eye(w, lead) * EV.visibility(w, None, sense="sight",
                                                                                                         cover=st_cover(w, road_id, pos)) + 0.5)
    if (serious or minor_call) and noticed:
        today["road"]["crossings"].append({"id": f"crossing:{lead}:{lkey}", "kind": "crossing", "road": road_id, "pos": pos, "lm": lm,
                                           "challenge": ch, "members": members, "risk": risk, "label": d["words"],
                                           "default": choice})
        return
    apply_choice(w, rec, members, t, pos, lm, ch, choice, exp)


def st_cover(w, road_id, pos):
    return stretch(w, road_id, pos)["terrain"] or "plain"


def _risk(w, members, lm, ch, exp) -> dict:
    d = LANDMARKS[lm["kind"]]
    push = d.get("push") or {}
    loss = 0.0
    if "cart_loss" in push and any(w.goods(w.hands(n)).get("handcart", 0) >= 1 for n in members):
        loss = push["cart_loss"][0] * push["cart_loss"][1] * exp
    blizzard = ch == "snowed" and EV.weather(w) == "snow"
    return {"death": float(push.get("death", 0.0)) * exp if blizzard else 0.0, "loss": loss}


def apply_choice(w, rec, members, t, pos, lm, ch, choice, exp=1.0, by_call=False):
    """Minor trouble settled by the party's choice (D2-105, D2-113)."""
    d = LANDMARKS[lm["kind"]]
    road_id = t["road"]
    words = CHALLENGE_WORDS.get(ch, ch)
    if choice.startswith("go round") and ch == "down":
        other = any(l["kind"] == "ford" for s in w.s["roads"][road_id]["stretches"] for l in s["landmarks"])
        choice = "go round" if other else "turn back"
    if choice.startswith("wait"):
        for n in members:
            w.s["people"][n]["transit"]["arrive"] += 1
            _note(w, n, f"{words}: you waited a day", first=True)
        rec["trouble"].append({"members": members, "at": d["words"], "what": ch, "did": "waited"})
    elif choice.startswith("go round"):
        for n in members:
            w.s["people"][n]["transit"]["arrive"] += 1
            _note(w, n, f"{words}: you went round by another way, a day longer", first=True)
        rec["trouble"].append({"members": members, "at": d["words"], "what": ch, "did": "went round"})
    elif choice.startswith("turn back"):
        for n in members:
            turn_back(w, n)
            _note(w, n, f"{words}: you turned back", first=True)
        rec["trouble"].append({"members": members, "at": d["words"], "what": ch, "did": "turned back"})
    else:                                                                      # push on: cross anyway
        push = d.get("push") or {}
        lost = []
        for n in members:
            g = w.goods(w.hands(n))
            if "cart_loss" in push and g.get("handcart", 0) >= 1:
                p, share = push["cart_loss"]
                if w.rng("road-loss", w.d, n, road_id, pos).random() < p * exp:
                    for item, q in list(g.items()):
                        if ITEMS[item]["weight"] > 0 and item != "handcart" and q > 1e-9:
                            w.apply("destroy", road_id, src=w.hands(n), item=item, qty=round(q * share, 6), why="lost at the ford")
                    lost.append(n)
                    _note(w, n, f"{words}: you crossed anyway, and the water took part of your load", first=True)
            elif push.get("foot") == "soaked":
                today_soaked = w.s["today"].setdefault("soaked", [])
                today_soaked.append(n)
                _note(w, n, f"{words}: you crossed anyway and were soaked to the skin", first=True)
            if push.get("death") and EV.weather(w) == "snow" and w.rng("road-death", w.d, n).random() < float(push["death"]) * exp:
                w.apply("die", road_id, person=n, cause="the cold on the pass")
                lost.append(n)
            _learn(w, n, road_id, pos, lm, crossed=True)
        rec["trouble"].append({"members": members, "at": d["words"], "what": ch, "did": "pushed on", "lost": lost})


def turn_back(w, name):
    """Back over the stretches covered: a party on its k-th stretch tonight spends k-1 more nights going back and is home at the
    dawn after (D2-110)."""
    t = w.s["people"][name]["transit"]
    k = stretch_of(w, t)
    t.update({"from": t["to"], "to": t["from"], "arrive": w.d + k, "turned": True})


def travel_with(w, name, other):
    """Change course: go with the other party, the same way, to its destination (D2-110)."""
    t, o = w.s["people"][name]["transit"], w.s["people"][other]["transit"]
    t.update({"from": o["from"], "to": o["to"], "arrive": o["arrive"], "left": o["left"], "with": other})


# ---------------------------------------------------------------------- daily notices (D2-97)
def _notices(w, members, t, pos, ps):
    """What each traveller notices on its stretch tonight, from the bundles in signs.py (ROAD, THING, TRACE, TRAVELLER; D2-97)."""
    from cybertron2.engine import perceive as PC, signs as SG
    road_id = t["road"]
    cover = stretch(w, road_id, pos)["terrain"] or "plain"
    sight = EV.visibility(w, None, sense="sight", cover=cover)
    for n in members:
        know = PC.practised(PC.Mind(w, n))
        eye = TH.eye(w, n)
        rng = w.rng("road-notice", w.d, n)
        for text in SG.roll(SG.ROAD, SG.road_context(w, n, t, pos), rng, know=know):
            _note(w, n, text)
        for c in things_on(w, road_id, pos).values():
            rows, x = SG.bundle(w, c)
            for text in SG.roll(rows, x, rng, mult=TH.own(w, c) * sight * eye, know=know, at_node=False):
                _note(w, n, text)
        for x in w.s.get("traces", []):                                 # traces of others who passed (D2-88): fading
            if x["road"] != road_id or x["pos"] != pos or n in x["by"] or w.d - x["day"] < 1:
                continue
            fade = 1 - (w.d - x["day"]) / float(ROADS["trace_days"][x["kind"]])
            snow = 3.0 if EV.snow_lying(w) and x["kind"] == "tracks" else 1.0
            for text in SG.roll(SG.TRACE, SG.trace_context(w, x), rng, mult=0.3 * fade * snow * sight * eye, know=know):
                _note(w, n, text)
        for key, others in ps.items():                                  # other travellers seen far off on the same stretch
            if others == members or key[0] != road_id:
                continue
            o = w.s["people"][others[0]]["transit"]
            if position(w, o) != pos or (o["from"], o["to"]) == (t["from"], t["to"]):
                continue
            for text in SG.roll(SG.TRAVELLER, SG.traveller_context(w, others, o, pos), rng, mult=sight, know=know):
                _note(w, n, text)


def things_on(w, road_id, pos) -> dict:
    return {cid: c for cid, c in w.s["containers"].items() if c["kind"] in TH.KINDS and c.get("node") == road_id
            and int(c.get("stretch") or 1) == pos and (c.get("body") or c.get("beast") or any(q > 1e-9 for q in c["goods"].values()))}


# ---------------------------------------------------------------------- finds on the road (D2-86)
def _finds(w, today, rec, members, t, pos):
    road_id = t["road"]
    sight = EV.visibility(w, None, sense="sight", cover=st_cover(w, road_id, pos))
    for cid, c in things_on(w, road_id, pos).items():
        if c.get("by") in members or c.get("of") in members:
            continue
        worth = any(q > 1e-9 and ITEMS.get(i, {}).get("food", 1) > 0 or not ITEMS.get(i, {}).get("rot") and q > 1e-9
                    for i, q in c["goods"].items()) or (c.get("body") and c.get("buried") is None)   # not rotting meat alone
        if not worth:
            continue
        finder = next((n for n in members if w.rng("road-find", w.d, n, cid).random() < min(1.0, TH.own(w, c) * sight * TH.eye(w, n))), None)
        if finder:
            from cybertron2.engine import signs as SG
            rows, x = SG.bundle(w, c)
            look = SG.roll(rows, x, w.rng("road-find-look", w.d, finder, cid), mult=0.0, near=True, at_node=False,
                           least=True)                                       # the finder's close look, not the glimpse again
            today["road"]["finds"].append({"id": f"find:{cid}:{finder}:{w.d}", "kind": "find", "road": road_id, "pos": pos, "thing": cid,
                                           "members": members, "finder": finder, "label": "; ".join(look) or TH.describe(w, c)})
            rec["finds"].append({"by": finder, "thing": cid})


# ---------------------------------------------------------------------- herds on the road (D2-124, D2-125, D2-127, D2-128)
def searching_for(w, name, hid) -> bool:
    """Whether one set out searching for this herd (`travel {searching: ...}`, D2-125): its name, its owners', or any beasts."""
    want = str((w.s["people"][name]["transit"].get("choices") or {}).get("searching") or "").strip().lower().removeprefix("the ")
    if not want:
        return False
    h = w.s["herds"][hid]
    names = {h["name"].lower(), str(h.get("base_name") or "").lower(), h.get("kind", "cattle"), "herd", "beasts", "cattle", "cows"}
    owners = {str(w.s["institutions"].get(c["claimant"], {}).get("name") or c["claimant"]).lower() for c in w.claims_on(("herd", hid))}
    return want in names or any(want in x or x in want for x in names | owners if x)


def herd_chance(w, name, hid, pos) -> float:
    """The noticing rule on a stretch (information/noticing.md): own x the terrain's sight x presence (1.0) x the eye, x5 searching."""
    h = w.s["herds"][hid]
    sight = EV.visibility(w, None, sense="sight", cover=st_cover(w, h["node"], pos))
    from cybertron2.engine.data import HERDS
    att = float(HERDS["road"]["search"]) if searching_for(w, name, hid) else 1.0
    return min(1.0, float(HERDS["own"]) * sight * TH.eye(w, name) * att)


def _herd_finds(w, today, rec, members, t, pos):
    from cybertron2.engine import farm as FM, herds as HD
    for hid, h in HD.on_stretch(w, t["road"], pos).items():
        if h.get("with"):
            continue
        finder = next((n for n in members if w.rng("herd-find", w.d, n, hid).random() < herd_chance(w, n, hid, pos)), None)
        if finder:
            today["road"]["herds"].append({"id": f"herd:{hid}:{finder}:{w.d}", "kind": "herd", "road": t["road"], "pos": pos, "herd": hid,
                                           "members": members, "finder": finder, "label": f"{FM.herd_words(h)} loose by the road"})
            rec.setdefault("herds", []).append({"by": finder, "herd": hid})


def _driven_splits(w, today, rec, members, t, pos):
    """A group breaking off a herd the party accompanies (D2-128): a call only if it is a quarter of the herd or 3 head or more and a
    drover notices it (D2-127)."""
    from cybertron2.engine import farm as FM, herds as HD
    from cybertron2.engine.data import HERDS
    for hid, h in list(w.s["herds"].items()):
        if h.get("with") not in members or FM.head(h) <= 0:
            continue
        n = FM.head(h)
        r = {"herds": []}
        new = HD.split(w, hid, r, drove=len(members))
        if not new:
            continue
        w.apply("set", t["road"], ref=("herd", new), field="lost", value={"day": w.d, "from": t["from"], "road": t["road"]})
        k = FM.head(w.s["herds"][new])
        rec.setdefault("splits", []).append({"herd": hid, "new": new, "head": k})
        big = k >= float(HERDS["call"]["share"]) * n or k >= int(HERDS["call"]["head"])
        saw = next((m for m in members if w.rng("split-see", w.d, m, new).random() < herd_chance(w, m, new, pos)), None)
        if big and saw:
            today["road"]["splits"].append({"id": f"split:{new}:{w.d}", "kind": "split", "road": t["road"], "pos": pos, "herd": hid,
                                            "new": new, "members": members, "finder": saw,
                                            "label": f"{k} head breaking away from {h['name']}"})
        elif saw:
            for m in members:
                _note(w, m, f"{k} head strayed off from {h['name']} at {stretch_name(w, t['road'], pos)}", first=True)


# ---------------------------------------------------------------------- meetings (D2-110)
def _meetings(w, today, rec, ps):
    keys = list(ps)
    for i, ka in enumerate(keys):
        for kb in keys[i + 1:]:
            if ka[0] != kb[0]:
                continue
            ta, tb = w.s["people"][ps[ka][0]]["transit"], w.s["people"][ps[kb][0]]["transit"]
            if (ta["from"], ta["to"]) == (tb["from"], tb["to"]):
                continue                                                    # the same way: not a meeting
            pa, pb = position(w, ta), position(w, tb)
            prev_a, prev_b = ta.get("last_pos"), tb.get("last_pos")
            crossed = prev_a is not None and prev_b is not None and (prev_a - prev_b) * (pa - pb) < 0
            if pa != pb and not crossed:
                continue
            pos = meeting_stretch(w, ka[0], pa, pb, ps[ka][0], ps[kb][0])
            st = stretch(w, ka[0], pos)
            p = max([float(LANDMARKS[l["kind"]].get("meet", 0.0)) for l in st["landmarks"]] or [0.0]) or \
                float(TERRAIN.get(st["terrain"] or "plain", {}).get("meet", 0.6))
            if EV.weather(w) == "fog":
                p *= 0.5
            if w.rng("meet", w.d, ps[ka][0], ps[kb][0]).random() < p:
                m = {"id": f"meeting:{ps[ka][0]}:{ps[kb][0]}:{w.d}", "kind": "meeting", "road": ka[0], "pos": pos,
                     "parties": [ps[ka], ps[kb]], "label": stretch_name(w, ka[0], pos)}
                passing = [i for i, party in enumerate(m["parties"]) if passes(w, party)]
                if passing:                                                  # one side will not stop: no call, both told (D4-51)
                    pass_by(w, m, passing)
                    rec["meetings"].append({"parties": m["parties"], "at": m["label"], "passed": True})
                    continue
                today["road"]["meetings"].append(m)
                rec["meetings"].append({"parties": m["parties"], "at": m["label"]})
    for key, members in ps.items():
        for n in members:
            t = w.s["people"][n]["transit"]
            if t is not None:
                t["last_pos"] = position(w, t)


def meeting_stretch(w, road_id, pa, pb, a, b) -> int:
    """Where crossing parties meet: a stretch between the two positions, drawn (keyed), three times likelier on one with a landmark
    (D2-121)."""
    span = list(range(min(pa, pb), max(pa, pb) + 1))
    weights = [float(ROADS["meet_landmark"]) if stretch(w, road_id, k)["landmarks"] else 1.0 for k in span]
    x = w.rng("meet-where", w.d, a, b).random() * sum(weights)
    for k, wt in zip(span, weights):
        x -= wt
        if x < 0:
            return k
    return span[-1]


def passes(w, party) -> bool:
    """A party that chose at departure not to stop for others (D4-51)."""
    return any(str((w.s["people"][n]["transit"].get("choices") or {}).get("meeting", "")).lower() == "pass by" for n in party)


def pass_by(w, m, passing):
    """A meeting that passes on its own: each side is told what it saw, from signs.PASSING (D4-51)."""
    from cybertron2.engine import signs as SG
    for i, party in enumerate(m["parties"]):
        other = m["parties"][1 - i]
        x = SG.passing_context(w, party, other, m, we_passed=i in passing, they_passed=(1 - i) in passing)
        for n in party:
            for text in SG.roll(SG.PASSING, x, w.rng("pass", w.d, n, m["id"]), least=True)[:2]:
                _note(w, n, text, first=True)


# ---------------------------------------------------------------------- fuse kinds on the road (fuse.py)
@FU.source("meeting")
def _src_meetings(w, today):
    return [dict(m, structure="road") for m in (today.get("road") or {}).get("meetings", [])]


@FU.source("find")
def _src_finds(w, today):
    return [dict(f, structure="road") for f in (today.get("road") or {}).get("finds", [])]


@FU.source("crossing")
def _src_crossings(w, today):
    return [dict(c, structure="road") for c in (today.get("road") or {}).get("crossings", [])]


@FU.source("herd")
def _src_herds(w, today):
    return [dict(f, structure="road") for f in (today.get("road") or {}).get("herds", [])]


@FU.source("split")
def _src_splits(w, today):
    return [dict(f, structure="road") for f in (today.get("road") or {}).get("splits", [])]


def whose_herd(w, name, hid) -> str:
    """What a finder makes of whose beasts these are: its own household's it knows; a neighbour's from its own village it knows by
    sight; strangers' it cannot tell."""
    h = w.s["herds"][hid]
    holders = [c["claimant"] for c in w.claims_on(("herd", hid)) if c.get("grounds") != "found"]
    if {name, w.household_of(name)} & set(holders):
        return f" They are your own: {h.get('base_name') or h['name']}."
    home = w.s["parcels"].get(h.get("home") or "", {}).get("node")
    mine = {w.s["buildings"][b]["node"] for b in w.homes(name)}                # the village one lives in
    if home and home in mine:
        names = sorted({w.s["institutions"].get(c, {}).get("name", c) for c in holders})
        return f" You know them: {h.get('base_name') or h['name']}" + (f", {' and '.join(names)}'s" if names else "") + "."
    return " Whose they are you cannot tell."


@FU.detector("herd")
def _det_herd(w, today, e):
    n = e["finder"]
    return {n: f"by the road, at {stretch_name(w, e['road'], e['pos'])}, you come upon beasts with nobody minding them: "
               f"{e['label']}.{whose_herd(w, n, e['herd'])} A herd loose on the road soon dies or is lost for good"}


@FU.detector("split")
def _det_split(w, today, e):
    return {e["finder"]: f"on the road, at {stretch_name(w, e['road'], e['pos'])}: {e['label']}, off into the {st_cover(w, e['road'], e['pos'])}"}


def _hold_found(w, name, e):
    """Whoever takes a found herd holds it (D4-23): a claim for the taker's household (or itself); the owner's claim stays, for custom and
    law."""
    hid = e["herd"]
    me = w.household_of(name) or name
    if not any(c["claimant"] == me for c in w.claims_on(("herd", hid))):
        w.apply("claim", e["road"], thing=("herd", hid), claimant=me, rights=["access", "withdrawal"], grounds="found")


@FU.choice("herd", "drive on")
@FU.choice("herd", "drive back")
def _ch_drive(w, today, name, e, a):
    from cybertron2.engine import herds as HD
    h = w.s["herds"].get(e["herd"])
    if not h or h["node"] != e["road"] or h.get("with"):
        raise Refused("the beasts are not there to drive")
    t = w.s["people"][name]["transit"]
    back = str(a.get("do")).lower() == "drive back"
    toward = t["from"] if back else t["to"]
    HD.drive_stretch(w, e["herd"], toward)
    if back:                                                                    # a stretch back and a stretch again: two days more
        for n in e["members"]:
            w.s["people"][n]["transit"]["arrive"] += 2
    word = f"back toward {w.s['nodes'][toward]['name']}" if back else f"on toward {w.s['nodes'][toward]['name']}"
    _note(w, name, f"you found {FM_words(w, e['herd'])} loose by the road and drove them a stretch {word}", first=True)
    return f"You drove the beasts a stretch {word} and left them there."


@FU.choice("herd", "accompany")
def _ch_accompany(w, today, name, e, a):
    from cybertron2.engine import herds as HD
    h = w.s["herds"].get(e["herd"])
    if not h or h["node"] != e["road"] or h.get("with"):
        raise Refused("the beasts are not there to take")
    t = w.s["people"][name]["transit"]
    to = str(a.get("to") or "").strip().lower()
    if to in ("back", "home", w.s["nodes"][t["from"]]["name"].lower()):
        for n in e["members"]:
            if not w.s["people"][n]["transit"].get("turned"):
                turn_back(w, n)
    _hold_found(w, name, e)
    HD.accompany(w, e["herd"], name)
    dest = w.s["nodes"][w.s["people"][name]["transit"]["to"]]["name"]
    _note(w, name, f"you found {FM_words(w, e['herd'])} loose by the road and took them along to {dest}", first=True)
    return f"You took the beasts along with you, toward {dest}; they go at your pace."


@FU.choice("herd", "leave")
def _ch_leave_herd(w, today, name, e, a):
    _note(w, name, f"you saw {FM_words(w, e['herd'])} loose by the road and left them", first=True)
    return "You left the beasts where they were."


@FU.choice("split", "go after them")
def _ch_after(w, today, name, e, a):
    """Rounding them up costs the party a day; the group rejoins the herd it broke from."""
    new, hid = w.s["herds"].get(e["new"]), w.s["herds"].get(e["herd"])
    if not new or not hid or new["node"] != e["road"]:
        raise Refused("they are gone")
    for role in ("cows", "oxen", "bulls", "young"):
        w.apply("set", e["road"], ref=("herd", e["herd"]), field=role, value=int(hid.get(role, 0)) + int(new.get(role, 0)))
        w.apply("set", e["road"], ref=("herd", e["new"]), field=role, value=0)
    w.apply("set", e["road"], ref=("herd", e["new"]), field="count", value=0)
    from cybertron2.engine import farm as FM
    w.apply("set", e["road"], ref=("herd", e["herd"]), field="count", value=FM.head(w.s["herds"][e["herd"]]))
    for n in e["members"]:
        w.s["people"][n]["transit"]["arrive"] += 1
        _note(w, n, f"some of the beasts broke away at {stretch_name(w, e['road'], e['pos'])}; rounding them up cost a day", first=True)
    return "You went after them and brought them back; it cost the day."


@FU.choice("split", "let them go")
def _ch_let_go(w, today, name, e, a):
    for n in e["members"]:
        _note(w, n, f"{e['label']} at {stretch_name(w, e['road'], e['pos'])}; you let them go", first=True)
    return "You let them go and kept the rest together."


def FM_words(w, hid) -> str:
    from cybertron2.engine import farm as FM
    return FM.herd_words(w.s["herds"][hid])


def _party_words(w, members) -> str:
    bits = []
    for m in members:
        g = w.goods(w.hands(m))
        seen = [i for i, q in g.items() if q >= 1 and (ITEMS[i].get("seen") or ITEMS[i]["weight"] >= 2)]
        armed = any(ITEMS[i].get("weapon") for i in seen)
        bits.append(m + (" (armed)" if armed else "") + (f", with {', '.join(sorted(seen)[:3])}" if seen else ""))
    return "; ".join(bits)


@FU.detector("meeting")
def _det_meeting(w, today, e):
    out = {}
    for i, party in enumerate(e["parties"]):
        other = e["parties"][1 - i]
        for n in party:
            out[n] = f"on the road, at {e['label']}, you meet {len(other)} traveller{'s' if len(other) > 1 else ''} coming the other way: " \
                     + _party_words(w, other)
    return out


@FU.detector("find")
def _det_find(w, today, e):
    return {e["finder"]: f"by the road, at {stretch_name(w, e['road'], e['pos'])}, you come upon this: {e['label']}"}


@FU.detector("crossing")
def _det_crossing(w, today, e):
    words = CHALLENGE_WORDS.get(e["challenge"], e["challenge"])
    danger = " A night on it in this weather could kill you." if e["risk"]["death"] else ""
    loss = " Crossing with a laden cart could cost you part of the load." if e["risk"]["loss"] else ""
    return {n: f"on the road: {words} at {e['label']}.{danger}{loss}" for n in e["members"]}


def _members(e, name):
    if e["kind"] == "meeting":
        return next(p for p in e["parties"] if name in p)
    return e["members"]


@FU.choice("crossing", "push on")
@FU.choice("crossing", "wait")
@FU.choice("crossing", "turn back")
@FU.choice("crossing", "go round")
def _ch_crossing(w, today, name, e, a):
    if e.get("settled"):
        return "The party had already chosen."
    e["settled"] = True
    do = str(a.get("do")).lower()
    t = w.s["people"][name]["transit"]
    rec = {"trouble": []}
    apply_choice(w, rec, e["members"], t, e["pos"], e["lm"], e["challenge"], do, experience(w, name, landmark_key(e["road"], e["pos"], e["lm"]["kind"])))
    return f"You chose to {do}."


@FU.choice("find", "take")
def _ch_take(w, today, name, e, a):
    c = w.s["containers"].get(e["thing"])
    if not c:
        raise Refused("it is gone")
    cap = w.capacity(name, w.s["roads"][e["road"]].get("track", False))
    took = []
    for item, q in sorted(c["goods"].items(), key=lambda kv: ITEMS[kv[0]]["weight"]):
        if q <= 1e-9:
            continue
        want = str(a.get("item") or "").lower()
        if want and want != item:
            continue
        load = sum(qq * ITEMS[i]["weight"] for i, qq in w.goods(w.hands(name)).items())
        room = (cap - load) / max(1e-9, ITEMS[item]["weight"]) if ITEMS[item]["weight"] else q
        x = round(min(q, float(a.get("qty") or q), max(0.0, room)), 6)
        if x > 1e-9:
            w.apply("transfer", e["road"], src=e["thing"], dst=w.hands(name), item=item, qty=x)
            took.append(f"{x:g} {item}")
    w.s["mind"][name].setdefault("found", []).append(e["thing"])
    if took:
        _note(w, name, "you found something by the road and took " + ", ".join(took), first=True)
    return ("You took " + ", ".join(took) + ".") if took else "You could carry nothing more."


@FU.choice("find", "bury")
def _ch_bury(w, today, name, e, a):
    c = w.s["containers"].get(e["thing"])
    if not c or not c.get("body"):
        raise Refused("there is no body to bury")
    w.apply("set_thing", e["road"], cid=e["thing"], field="buried", value=w.d)
    return f"You buried {c['of']} by the road."


@FU.choice("find", "go on")
@FU.choice("meeting", "go on")
def _ch_go_on(w, today, name, e, a):
    return "You went on your way."


@FU.choice("meeting", "turn back")
def _ch_turn(w, today, name, e, a):
    for n in _members(e, name):
        if not w.s["people"][n]["transit"].get("turned") or n == name:
            turn_back(w, n)
    return "You turned back the way you came."


@FU.choice("meeting", "change course")
def _ch_change(w, today, name, e, a):
    other = next(p for p in e["parties"] if name not in p)
    for n in _members(e, name):
        travel_with(w, n, other[0])
    return f"You turned and went on with {', '.join(other)}."


@FU.choice("meeting", "attack")
def _ch_attack(w, today, name, e, a):
    other = next(p for p in e["parties"] if name not in p)
    tgt = str(a.get("target") or other[0])
    tgt = next((x for x in other if x.lower() == tgt.lower()), other[0])
    e.setdefault("attacks", []).append({"by": name, "target": tgt, "aim": str(a.get("aim") or "rob")})
    return f"You set on {tgt}."


@FU.choice("meeting", "flee")
def _ch_flee(w, today, name, e, a):
    e.setdefault("fled", []).append(name)
    return "You tried to get away."


@FU.choice("meeting", "give")
def _ch_give(w, today, name, e, a):
    other = [x for p in e["parties"] for x in p if x != name]
    to = next((x for x in other if x.lower() == str(a.get("to") or "").lower()), None)
    if not to:
        raise Refused(f"there is nobody called {a.get('to')!r} in the meeting")
    item, q = str(a.get("item") or "").lower(), float(a.get("qty") or 0)
    if w.goods(w.hands(name)).get(item, 0.0) + 1e-9 < q or q <= 0:
        raise Refused(f"you carry only {w.goods(w.hands(name)).get(item, 0.0):g} {item}")
    w.apply("transfer", e["road"], src=w.hands(name), dst=w.hands(to), item=item, qty=q)
    return f"You gave {q:g} {item} to {to}."


@FU.choice("meeting", "accept")
def _ch_accept(w, today, name, e, a):
    """Taking an offer made in the meeting: the agreement system as at a node, the road the place (D2-120); a promise stays open and
    is paid where the two are next at one node (D2-32)."""
    from cybertron2.engine import agreements as AG
    from cybertron2.engine.here import Here, Mind
    out = AG.accept(Here(w, name, transit=True), Mind(w, name), a, None)
    e.setdefault("deals", []).append(out.split(": ", 1)[-1].split(". Agreement")[0].rstrip("."))
    return out


def meeting_talk(w, e, replies) -> tuple:
    """A wave of a meeting's conversation (D2-110): what each said (to all in the meeting: speech is free in transit) and the offers
    made, through the agreement system with the road as the place (D2-120). Returns (lines, offers) for the next wave."""
    from cybertron2.engine import agreements as AG
    from cybertron2.engine.here import Here, Mind
    said, offers = [], []
    for n, r in replies.items():
        for x in [x for x in (r.get("say") or []) + (r.get("tell") or []) if isinstance(x, dict) and str(x.get("text", "")).strip()][:3]:
            said.append(f"{n}: {str(x['text'])[:400]}")
        here = Here(w, n, transit=True)
        for o in [o for o in (r.get("offers") or []) if isinstance(o, dict)][:2]:
            try:
                line = AG.make_offer(here, Mind(w, n), o)
            except Refused as err:
                e.setdefault("refused", []).append(f"{n}: {err}")
                continue
            if line.startswith("You offered "):
                offers.append(line.removeprefix("You offered ").split(" (open")[0])
    return said, offers


def settle_meeting(w, e) -> list:
    """Attacks on the road, fought as at a node (conflict/combat.md); the other side's choice is its response (flee: a chance to
    get away). Returns lines for the record."""
    from cybertron2.engine import settle as ST
    out = []
    for i, party in enumerate(e["parties"]):                                  # remembered on arrival (D2-97)
        other = e["parties"][1 - i]
        lms = stretch(w, e["road"], e["pos"])["landmarks"]
        where = LANDMARKS[lms[0]["kind"]]["words"] if lms else "the road"
        deals = "".join(f"; agreed: {d}" for d in e.get("deals", []))
        for n in party:
            if w.s["people"][n]["alive"] and w.s["people"][n]["transit"] is not None:
                _note(w, n, f"you met {', '.join(other)} at {where}{deals}", first=True)
    for at in e.get("attacks", []):
        tgt = at["target"]
        if tgt in e.get("fled", []) and w.rng("flee", w.d, tgt).random() < float(ROADS["flee"]):
            out.append({"by": at["by"], "target": tgt, "outcome": "fled"})
            continue
        out.append(ST.duel(w, e["road"], at["by"], tgt, at["aim"]))
    return out


# ---------------------------------------------------------------------- arrival (D2-97)
def arrived(w, name, t) -> None:
    """On arrival its notices become memories: "On the way: ..." at the top of its next turn."""
    lines = list(t.get("notices") or [])
    if len(lines) > int(ROADS["notices"]):
        lines = lines[: int(ROADS["notices"]) - 1] + [f"and {len(lines) - int(ROADS['notices']) + 1} other things"]
    w.s["mind"][name]["on_the_way"] = {"day": w.d, "lines": lines}
