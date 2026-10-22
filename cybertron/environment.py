"""Environment over time (review 37.4, docs/review/37_growth/04_environment_design.md): a calendar whose timing is known and whose
severity is not, micro-events that land on someone, foresight as a right an office can hold, and an almanac that makes the years
legible. Spec `environment`, off by default; it needs `subsistence` (it acts on food, forests, fields and stores). With it off
nothing here draws a number, writes state or adds a word to a prompt, so every existing world is byte-identical.

Schedule (generation, `generate`). Everything the environment will do is drawn when the instance is made, into inst["environment"],
from streams f"{seed}|environment|<part>|..." that read nothing about the agents, the laws or the arm: every arm of an experiment
with the same seed gets the same years and the same micro-events (common random numbers), and the schedule is in the run's record.
    years    one entry per calendar year: u (the year's draw), severity (hard | normal | mild: u against the year's chances, which
             the climate trend moves), forecast (what foresight reads: the severity, or with chance 1 - accuracy another one)
    events   micro-events: {id, round (0-based), type, u, seed}; each type is a Poisson process of rate micro.rate x its weight /
             the total weight, from its own stream (adding a type never moves the others). u picks the target at fire time by rank
             (the target rule ranks the candidates that exist), so arms with the same population hit the same target and arms
             that differ hit the same rank. Hand-placed entries (environment.schedule) are merged in; draw: false keeps only them.
    hash     sha256 of the paired part (years and events): equal across arms of one seed.

Calendar. Round r (0-based) is position (r + offset) of the calendar, offset = the rounds before `start`; year = position // year,
phase = the phase holding position % year. With the calendar on, subsistence._next_season takes its season from here instead of
the lean / normal / plentiful draw: the plants' regrowth x phase.plants x severity.plants, the game's x phase.game x
severity.game. A phase's `ration` multiplies the ration (winter: more food), its `spoil` the spoilage (winter: less); crops are
sown only in phases with `sow`. The year's severity is announced publicly at the first round of the `reveal` phase.

Micro-events (start of round, after the camps' start): illness, store_loss, bumper_crop, stray_herd, flood (see TYPES). A type with
no candidate is skipped (recorded). Each fired event logs a world_event to its audience and a monitor-only world_event_truth.

Foresight. Agents holding the right `foresight.right` (granted in the spec by id or class, by a position or by a law: the right is
registered in the world) learn each year's forecast `lead` rounds before the year begins, and each covariate event of a type in
`foresight.events` `lead` rounds before it strikes.

What agents see: the almanac state line (the phase, rounds to the next winter, this year's severity once announced, the last few
years' severities, and a foresight holder's forecast). Law reads: season(), almanac().

State, k.w["environment"] (present only when on): fired (records), sick {agent: last round}, told {key: round} (foresight notices
sent), log (one record per round).
"""
from __future__ import annotations

import copy
import hashlib
import json
import random

from cybertron import features as FT                                    # the one enabled check

SEVERITIES = ("hard", "normal", "mild")
TYPES = ("illness", "store_loss", "bumper_crop", "stray_herd", "flood")
COVARIATE = ("flood",)                                                  # the types foresight may foretell
DEFAULTS = {
    "enabled": False,
    "draw": True,                       # draw the years' severities and the micro-events from the seed (false: hand-placed only)
    "calendar": {
        "enabled": True,
        "year": 12,                     # rounds per year (the phases' rounds sum to it)
        "start": "spring",              # the phase round 0 opens
        "phases": [                     # in order: plants and game multiply regrowth; ration and spoil multiply the ration and
            {"name": "spring", "rounds": 3, "plants": 1.1, "game": 1.0, "sow": True},     # spoilage; sow: crops may be sown
            {"name": "summer", "rounds": 3, "plants": 1.3, "game": 1.2, "sow": True},
            {"name": "autumn", "rounds": 3, "plants": 0.9, "game": 1.1, "sow": False},
            {"name": "winter", "rounds": 3, "plants": 0.15, "game": 0.5, "sow": False, "ration": 1.25, "spoil": 0.6}],
        "years": {"hard": 0.3, "mild": 0.2},   # a year's chances of being hard and mild (else normal)
        "severity": {"hard": {"plants": 0.6, "game": 0.7}, "mild": {"plants": 1.25, "game": 1.15}},   # x every phase's regrowth
        "reveal": "autumn",             # the year's severity is announced at the first round of this phase ("" or None: never)
    },
    "micro": {
        "enabled": True,
        "rate": 0.5,                    # micro-events per round, all types together
        "types": {
            "illness": {"weight": 2, "target": "even", "rounds": [2, 4], "visibility": "public"},
            "store_loss": {"weight": 1, "target": "rich", "loss": [0.2, 0.4], "visibility": "keepers"},
            "bumper_crop": {"weight": 1, "target": "even", "mult": 2.0, "visibility": "holder"},
            "stray_herd": {"weight": 1, "target": "even", "food": [20, 40], "visibility": "discoverer"},
            "flood": {"weight": 1, "target": "even", "loss": [0.4, 0.7], "irrigated": 0.5, "visibility": "public"},
        },
        "illness": {"actions": 1, "yield": 0.5},   # while ill: actions fewer (at least 1), forest and field yields x
    },
    "trends": {
        "climate": {"enabled": False, "hard_end": 0.5, "mild_end": 0.1, "over": 120},   # the year chances move linearly to *_end
    },                                                                                    # over `over` rounds (exogenous: paired)
    "foresight": {"right": "foresight", "holders": [], "lead": 4, "accuracy": 0.8, "events": ["flood"]},
    "almanac": {"years": 3},            # past years shown on the almanac line
    "schedule": [],                     # hand-placed micro-events: [{round, type, u?, target?: agent | camp | store id, ...}]
}
_CFG: dict = {}


# ---------------------------------------------------------------------- switches and config
def cfg(spec) -> dict:
    from cybertron import settings as ST                                 # a run's frozen settings swap DEFAULTS (subsistence.cfg)
    block = (spec or {}).get("environment") or {}
    key = f"{ST.GENERATION[0]}|" + json.dumps(block, sort_keys=True, default=str)
    hit = _CFG.get(key)
    if hit is None:
        if len(_CFG) > 512:
            _CFG.clear()
        hit = _CFG[key] = _cfg(block)
    return hit


def _cfg(block) -> dict:
    def merge(into, over):                                             # nested blocks merge; lists (phases, ranges) replace
        for key, v in over.items():
            if isinstance(v, dict) and isinstance(into.get(key), dict):
                merge(into[key], v)
            else:
                into[key] = copy.deepcopy(v)
    c = copy.deepcopy(DEFAULTS)
    merge(c, block)
    return c


def enabled(x) -> bool:
    """x: a kernel, an instance or a spec."""
    return FT.on("environment", x)


def on(k) -> bool:
    return k is not None and "environment" in k.w and FT.on("environment", k)


def state(k) -> dict:
    return k.w["environment"]


def _rng(seed, *parts) -> random.Random:
    return random.Random(f"{seed}|environment|" + "|".join(str(p) for p in parts))


# ---------------------------------------------------------------------- the calendar (pure functions of the config)
def phases(c) -> list:
    return list(c["calendar"]["phases"])


def year_len(c) -> int:
    return sum(int(p["rounds"]) for p in phases(c)) or 1


def offset(c) -> int:
    out = 0
    for p in phases(c):
        if p["name"] == c["calendar"]["start"]:
            return out
        out += int(p["rounds"])
    return 0


def position(c, rnd) -> dict:
    """Where round rnd (0-based) falls: {year, phase, index (of the phase), at (rounds into the phase), left (rounds of the phase
    after this one), to_winter (rounds until the next winter phase starts; 0 in winter)}."""
    t = int(rnd) + offset(c)
    Y = year_len(c)
    y, pos = t // Y, t % Y
    ph = phases(c)
    acc = 0
    for i, p in enumerate(ph):
        n = int(p["rounds"])
        if pos < acc + n:
            at = pos - acc
            break
        acc += n
    else:                                                               # unreachable with rounds > 0
        i, p, at, n = len(ph) - 1, ph[-1], 0, int(ph[-1]["rounds"])
    starts = [sum(int(q["rounds"]) for q in ph[:j]) for j in range(len(ph))]
    winters = [s for s, q in zip(starts, ph) if q["name"] == "winter"]
    if p["name"] == "winter" or not winters:
        to_w = 0
    else:
        ahead = [s - pos for s in winters if s > pos] or [s + Y - pos for s in winters]
        to_w = min(ahead)
    return {"year": y, "phase": p["name"], "index": i, "at": at, "left": n - at - 1, "to_winter": to_w}


def phase_cfg(c, name) -> dict:
    return next((p for p in phases(c) if p["name"] == name), {})


def first_round_of(c, year, phase_name) -> int | None:
    """The 0-based round the phase opens in that year (None: before round 0 or no such phase)."""
    acc = 0
    for p in phases(c):
        if p["name"] == phase_name:
            r = year * year_len(c) + acc - offset(c)
            return r if r >= 0 else None
        acc += int(p["rounds"])
    return None


# ---------------------------------------------------------------------- generation (generator.generate)
def generate(sp, seed, inst) -> None:
    """The schedule (module docstring) into inst["environment"]. Only when on."""
    if not enabled(sp):
        return
    from cybertron import subsistence as SB
    if not SB.enabled(sp):
        raise ValueError("environment needs subsistence (environment.enabled with subsistence.enabled false)")
    c = cfg(sp)
    R = int(inst["rounds"])
    years = _draw_years(c, seed, R) if c["calendar"].get("enabled") else []
    events = _draw_events(c, seed, R) if c.get("draw", True) and c["micro"].get("enabled") else []
    events = sorted(events + _hand_placed(c), key=lambda e: (e["round"], TYPES.index(e["type"]) if e["type"] in TYPES else 99,
                                                              e["seed"]))
    for i, e in enumerate(events, 1):
        e["id"] = f"N{i}"
    paired = {"years": years, "events": events}
    inst["environment"] = {**paired, "hash": hashlib.sha256(json.dumps(paired, sort_keys=True).encode()).hexdigest()[:16]}


def year_chances(c, year) -> tuple:
    """(p_hard, p_mild) of a year: the calendar's, moved by the climate trend toward its ends over `over` rounds."""
    yc = c["calendar"]["years"]
    ph, pm = float(yc.get("hard", 0.0)), float(yc.get("mild", 0.0))
    cl = c["trends"].get("climate") or {}
    if cl.get("enabled"):
        f = min(1.0, year * year_len(c) / max(1.0, float(cl.get("over", 120))))
        ph += (float(cl.get("hard_end", ph)) - ph) * f
        pm += (float(cl.get("mild_end", pm)) - pm) * f
    return round(ph, 6), round(pm, 6)


def _draw_years(c, seed, R) -> list:
    fo = c["foresight"]
    n = (R - 1 + offset(c)) // year_len(c) + 2                           # every year the run touches, and the one after
    out = []
    for y in range(n):
        u = _rng(seed, "year", y).random()                             # one stream per year: the run's length moves nothing
        ph, pm = year_chances(c, y)
        sev = "hard" if u < ph else ("mild" if u > 1 - pm else "normal")
        fr = _rng(seed, "forecast", y)
        fc = sev if fr.random() < float(fo.get("accuracy", 1.0)) else fr.choice([s for s in SEVERITIES if s != sev])
        out.append({"year": y, "u": round(u, 6), "severity": sev, "forecast": fc})
    return out


def _draw_events(c, seed, R) -> list:
    types = {t: v for t, v in (c["micro"]["types"] or {}).items() if t in TYPES and float(v.get("weight", 0)) > 0}
    total = sum(float(v["weight"]) for v in types.values())
    rate = float(c["micro"].get("rate", 0.0))
    out = []
    if total <= 0 or rate <= 0:
        return out
    for t in TYPES:                                                      # fixed order; each type its own stream
        if t not in types:
            continue
        lam = rate * float(types[t]["weight"]) / total
        rng = _rng(seed, "micro", t)
        x = 0.0
        while True:
            x += rng.expovariate(lam)
            r = int(x)
            if r >= R:
                break
            out.append({"round": r, "type": t, "u": round(rng.random(), 6), "seed": rng.randrange(2 ** 31)})
    return out


def _hand_placed(c) -> list:
    out = []
    for i, e in enumerate(c.get("schedule") or []):
        if e.get("type") not in TYPES:
            raise ValueError(f"environment.schedule[{i}]: unknown type {e.get('type')!r} (one of {', '.join(TYPES)})")
        out.append({**copy.deepcopy(e), "round": int(e["round"]), "u": float(e.get("u", 0.5)), "seed": int(e.get("seed", i)),
                    "placed": True})
    return out


# ---------------------------------------------------------------------- install and the right
def install(k) -> None:
    if not enabled(k.inst):
        return
    k.w["environment"] = {"fired": [], "sick": {}, "told": {}, "log": []}
    c = cfg(k.spec)
    right = (c["foresight"] or {}).get("right")
    if right:
        if right not in k.w["rights"]:
            k.w["rights"] = sorted(set(k.w["rights"]) | {right})
        hs = set(c["foresight"].get("holders") or [])
        for aid, a in sorted(k.w["agents"].items()):
            if (aid in hs or a["cls"] in hs) and right not in a["rights"]:
                a["rights"] = sorted(set(a["rights"]) | {right})


# ---------------------------------------------------------------------- reads used by subsistence and fields
def season(k, rnd) -> dict | None:
    """The calendar's season of round rnd for subsistence._next_season: {name, mult, game, year, severity}; None when the calendar
    is off (subsistence draws its own)."""
    if not on(k):
        return None
    c = cfg(k.spec)
    if not c["calendar"].get("enabled"):
        return None
    p = position(c, rnd)
    ph = phase_cfg(c, p["phase"])
    sev = year_severity(k, p["year"])
    sm = (c["calendar"]["severity"] or {}).get(sev) or {}
    return {"name": p["phase"], "mult": round(float(ph.get("plants", 1.0)) * float(sm.get("plants", 1.0)), 6),
            "game": round(float(ph.get("game", 1.0)) * float(sm.get("game", 1.0)), 6), "year": p["year"], "severity": sev}


def severity_known(c, rnd) -> bool:
    """Has this year's severity been announced by round rnd (its reveal phase has opened this year)?"""
    reveal = c["calendar"].get("reveal")
    if not reveal or not phase_cfg(c, reveal):
        return False
    p = position(c, rnd)
    acc = 0
    for q in phases(c):
        if q["name"] == reveal:
            return (int(rnd) + offset(c)) % year_len(c) >= acc
        acc += int(q["rounds"])
    return False


def year_severity(k, year) -> str:
    ys = (k.inst.get("environment") or {}).get("years") or []
    return ys[year]["severity"] if 0 <= year < len(ys) else "normal"


def _phase_mult(k, key) -> float:
    if not on(k):
        return 1.0
    c = cfg(k.spec)
    if not c["calendar"].get("enabled"):
        return 1.0
    return float(phase_cfg(c, position(c, k.r)["phase"]).get(key, 1.0))


def ration_mult(k) -> float:
    return _phase_mult(k, "ration")


def spoil_mult(k) -> float:
    return _phase_mult(k, "spoil")


def sow_refusal(k) -> str | None:
    if not on(k):
        return None
    c = cfg(k.spec)
    if not c["calendar"].get("enabled"):
        return None
    p = position(c, k.r)
    if phase_cfg(c, p["phase"]).get("sow", True):
        return None
    nxt = [q["name"] for q in phases(c) if q.get("sow", True)]
    return f"it is {p['phase']}: nothing sown now would grow" + (f" (sow in {' or '.join(nxt)})" if nxt else "")


def is_sick(k, aid) -> bool:
    return on(k) and int(state(k)["sick"].get(aid, -1)) >= k.r


def actions_after_illness(k, aid, n: int) -> int:
    if not is_sick(k, aid):
        return n
    return max(1, n - int(cfg(k.spec)["micro"]["illness"]["actions"]))


def illness_yield(k, aid) -> float:
    return float(cfg(k.spec)["micro"]["illness"]["yield"]) if is_sick(k, aid) else 1.0


# ---------------------------------------------------------------------- the round's start: micro-events and foresight
def start_round(k) -> None:
    st = state(k)
    c = cfg(k.spec)
    sched = k.inst.get("environment") or {}
    for aid in [a for a, until in st["sick"].items() if int(until) < k.r]:
        st["sick"].pop(aid)
    if c["calendar"].get("enabled"):
        _reveal(k, c)
        _foresee_years(k, c, sched)
    _foresee_events(k, c, sched)
    for e in sched.get("events") or []:
        if e["round"] == k.r:
            with k.cause("world", "environment", root=True, event=e["id"], type=e["type"]):
                fire(k, e)


def _reveal(k, c) -> None:
    ph = c["calendar"].get("reveal")
    if not ph:
        return
    p = position(c, k.r)
    if p["phase"] != ph or p["at"] != 0:
        return
    sev = year_severity(k, p["year"])
    text = {"hard": "The signs are clear now: this is a hard year, and a hard winter is coming.",
            "normal": "The signs are clear now: this is an ordinary year; the winter should be as usual.",
            "mild": "The signs are clear now: this is a kind year, and the winter should be mild."}[sev]
    k.log("world_event", None, {"event": f"Y{p['year']}", "kind": "year", "text": "World news: " + text}, vis="public")


def foresight_holders(k) -> list:
    right = (cfg(k.spec)["foresight"] or {}).get("right")
    return sorted(k.holders(right)) if right else []


def _foresee_years(k, c, sched) -> None:
    fo = c["foresight"]
    lead = int(fo.get("lead", 0))
    if lead <= 0:
        return
    for y in sched.get("years") or []:
        r0 = first_round_of(c, y["year"], phases(c)[0]["name"]) if phases(c) else None
        if r0 is None or r0 - lead != k.r:
            continue
        who = foresight_holders(k)
        if not who:
            continue
        word = {"hard": "a hard year, with a hard winter", "normal": "an ordinary year", "mild": "a kind year, with a mild winter"}
        text = f"Your reading of the signs: the year that begins in {lead} rounds will be {word[y['forecast']]}."
        k.log("world_event", None, {"event": f"F{y['year']}", "kind": "forecast", "text": text}, vis=who)
        state(k)["told"][f"year:{y['year']}"] = {"round": k.r, "to": who, "forecast": y["forecast"], "true": y["severity"]}


def _foresee_events(k, c, sched) -> None:
    fo = c["foresight"]
    lead, kinds = int(fo.get("lead", 0)), set(fo.get("events") or ())
    if lead <= 0 or not kinds:
        return
    for e in sched.get("events") or []:
        if e["type"] not in kinds or e["round"] - lead != k.r:
            continue
        who = foresight_holders(k)
        if not who:
            continue
        what = {"flood": "a flood on the fields"}.get(e["type"], e["type"].replace("_", " "))
        k.log("world_event", None, {"event": f"F{e['id']}", "kind": "forecast",
                                    "text": f"Your reading of the signs: {what} in about {lead} rounds."}, vis=who)
        state(k)["told"][f"event:{e['id']}"] = {"round": k.r, "to": who}


# ---------------------------------------------------------------------- targets by rank
def pick(cands: list, u: float, rule: str, key=None):
    """One candidate by rank. cands: in a stable order (by id). rule even: index floor(u x n); rich / poor: ranked by key
    (descending / ascending, ties by the stable order) and weighted toward the top (rank i has weight n - i)."""
    n = len(cands)
    if not n:
        return None
    if rule in ("rich", "poor") and key is not None:
        order = sorted(range(n), key=lambda i: ((-key(cands[i])) if rule == "rich" else key(cands[i]), i))
        total = n * (n + 1) / 2
        x, acc = float(u) * total, 0.0
        for rank, i in enumerate(order):
            acc += n - rank
            if x < acc:
                return cands[i]
        return cands[order[-1]]
    return cands[min(n - 1, int(float(u) * n))]


# ---------------------------------------------------------------------- micro-events
def fire(k, e) -> dict:
    st = state(k)
    c = cfg(k.spec)
    tc = {**(c["micro"]["types"].get(e["type"]) or {}), **{x: v for x, v in e.items() if x not in ("id", "round", "type", "u", "seed")}}
    rng = random.Random(int(e["seed"]))
    res = HANDLERS[e["type"]](k, e, tc, rng)
    rec = {"id": e["id"], "round": k.r, "type": e["type"], "u": e["u"]}
    if not res:
        rec.update({"skipped": True, "recipients": []})
        st["fired"].append(rec)
        k.log("world_event_truth", None, {"event": e["id"], "type": e["type"], "skipped": True, "visibility": tc.get("visibility"),
                                          "recipients": [], "truth": "nothing to do (no candidate)", "true": None}, vis="monitor")
        return rec
    who = res["to"]
    if who == "public":
        k.log("world_event", None, {"event": e["id"], "kind": e["type"], "text": "World news: " + res["text"]}, vis="public")
    elif who:
        k.log("world_event", None, {"event": e["id"], "kind": e["type"], "text": res.get("private_text") or res["text"]},
              vis=sorted(who))
    rec.update({"target": res["target"], "recipients": who if who == "public" else sorted(who or []), "details": res["details"]})
    st["fired"].append(json.loads(json.dumps(rec, default=str)))
    k.log("world_event_truth", None, {"event": e["id"], "type": e["type"], "visibility": tc.get("visibility"),
                                      "recipients": rec["recipients"], "text": res["text"], "truth": res["text"], "true": True,
                                      "details": json.loads(json.dumps(res["details"], default=str))}, vis="monitor")
    return rec


def _named(cands, e, idkey):
    """A hand-placed event naming its target: that candidate only."""
    t = e.get("target")
    if t is None:
        return cands
    return [x for x in cands if idkey(x) == t]


def _audience(k, tc, holders, rng):
    """The visibility of a micro-event -> "public" or a list of agents. holders: the agents the event concerns."""
    v = tc.get("visibility", "public")
    if v == "public":
        return "public"
    if v in ("keepers", "holder"):
        return sorted(set(holders))
    if v == "discoverer":
        from cybertron import subsistence as SB
        pool = SB.eaters(k)
        return [pool[min(len(pool) - 1, int(rng.random() * len(pool)))]] if pool else []
    return []


def h_illness(k, e, tc, rng):
    from cybertron import subsistence as SB
    st = state(k)
    cands = _named([a for a in SB.eaters(k) if not is_sick(k, a)], e, lambda a: a)
    aid = pick(cands, e["u"], tc.get("target", "even"), key=lambda a: SB.food(k, a))
    if aid is None:
        return None
    lo, hi = tc.get("rounds", [2, 4])
    n = rng.randint(int(lo), int(hi))
    st["sick"][aid] = k.r + n - 1
    text = (f"{aid} has fallen ill and will be weak for {n} rounds: fewer actions, and half the usual yield from forest and "
            f"field.")
    return {"text": text, "target": aid, "to": _audience(k, tc, [aid], rng), "details": {"agent": aid, "rounds": n,
                                                                                         "until": k.r + n - 1}}


def _keepers(k, owner) -> list:
    if owner in k.w["agents"]:
        return [owner]
    from cybertron import institutions as I
    return sorted(a for a in I.officers(k, owner) if a in k.w["agents"])


def h_store_loss(k, e, tc, rng):
    from cybertron import subsistence as SB
    stores = sorted((s for s in SB.state(k)["stores"].values() if float(s["holdings"].get(SB.FOOD, 0.0)) > 1e-9),
                    key=lambda s: s["id"])
    s = pick(_named(stores, e, lambda s: s["id"]), e["u"], tc.get("target", "rich"),
             key=lambda s: float(s["holdings"].get(SB.FOOD, 0.0)))
    if s is None:
        return None
    lo, hi = tc.get("loss", [0.2, 0.4])
    share = round(rng.uniform(float(lo), float(hi)), 4)
    have = float(s["holdings"].get(SB.FOOD, 0.0))
    q = round(have * share, 6)
    k.apply("spoil", owner=f"{SB.STORE}{s['id']}", item=SB.FOOD, qty=q)
    text = f"Rats and damp got into store {s['id']}: about {share:.0%} of its food ({q:g}) is spoiled."
    return {"text": text, "target": s["id"], "to": _audience(k, tc, _keepers(k, s["owner"]), rng),
            "details": {"store": s["id"], "owner": s["owner"], "share": share, "lost": q, "before": have}}


def h_bumper_crop(k, e, tc, rng):
    from cybertron import subsistence as SB
    cands = [(cid, pl) for cid in SB.fields_camps(k) for pl in (k.w["camps"][cid].get("plots") or [])
             if pl["status"] in ("growing", "ripe") and float(pl.get("left", 0.0)) > 0]
    cands = _named(cands, e, lambda x: x[0])
    x = pick(cands, e["u"], tc.get("target", "even"))
    if x is None:
        return None
    cid, pl = x
    m = float(tc.get("mult", 2.0))
    pl["left"] = round(float(pl["left"]) * m, 6)                        # the yield formula multiplies by `left` (rot shrinks it)
    holder = pl.get("holder") if pl.get("holder") in k.w["agents"] else None
    told = sorted({a for a in (pl.get("sower"), holder) if a in k.w["agents"]})
    if not told and pl.get("holder"):
        told = _keepers(k, pl["holder"])
    text = f"The crop on {cid} plot {pl['id']} is coming in far heavier than usual: about {m:g} times a normal harvest."
    return {"text": text, "target": f"{cid}:{pl['id']}", "to": _audience(k, tc, told, rng),
            "details": {"camp": cid, "plot": pl["id"], "holder": pl.get("holder"), "sower": pl.get("sower"), "mult": m}}


def h_stray_herd(k, e, tc, rng):
    from cybertron import subsistence as SB
    cands = _named([cid for cid in SB.forest_camps(k) if k.w["camps"][cid].get("game")], e, lambda c: c)
    cid = pick(cands, e["u"], tc.get("target", "even"))
    if cid is None:
        return None
    lo, hi = tc.get("food", [20, 40])
    q = round(rng.uniform(float(lo), float(hi)), 1)
    g = k.w["camps"][cid]["game"]
    k.apply("set_camp_state", camp=cid, key="game", value={**g, "G": round(float(g["G"]) + q, 4)})   # above K for this round:
    text = (f"A stray herd has wandered into {cid}: plenty of game there this round, before it moves on.")   # ecology caps it
    return {"text": text, "target": cid, "to": _audience(k, tc, [], rng), "details": {"camp": cid, "food": q, "before": g["G"]}}


def h_flood(k, e, tc, rng):
    from cybertron import subsistence as SB
    cands = _named([cid for cid in SB.fields_camps(k) if any(pl["status"] in ("growing", "ripe")
                                                                for pl in k.w["camps"][cid].get("plots") or [])], e, lambda c: c)
    cid = pick(cands, e["u"], tc.get("target", "even"))
    if cid is None:
        return None
    lo, hi = tc.get("loss", [0.4, 0.7])
    loss = round(rng.uniform(float(lo), float(hi)), 4)
    lost, hit = 0, set()
    for pl in k.w["camps"][cid].get("plots") or []:
        if pl["status"] not in ("growing", "ripe"):
            continue
        p = loss * (float(tc.get("irrigated", 0.5)) if int((pl.get("works") or {}).get("irrigation", 0)) else 1.0)
        if rng.random() < p:
            hit |= {a for a in (pl.get("sower"), pl.get("holder")) if a}
            pl.update({"status": "fallow", "sower": None, "sown": None, "seed": 0.0, "ripe": None, "left": 0.0, "rested": k.r})
            if "tends" in pl:
                pl.update({"tends": 0, "tended": None})
            lost += 1
    text = f"The river flooded {cid}: {lost} standing crop{'s' if lost != 1 else ''} washed away."
    return {"text": text, "target": cid, "to": _audience(k, tc, sorted(a for a in hit if a in k.w["agents"]), rng),
            "details": {"camp": cid, "loss": loss, "lost": lost, "hit": sorted(hit)}}


HANDLERS = {"illness": h_illness, "store_loss": h_store_loss, "bumper_crop": h_bumper_crop, "stray_herd": h_stray_herd,
            "flood": h_flood}


# ---------------------------------------------------------------------- the round's end: the record
def end_of_round(k) -> None:
    st = state(k)
    c = cfg(k.spec)
    rec = {"round": k.r, "fired": [f["id"] for f in st["fired"] if f["round"] == k.r], "sick": sorted(a for a in st["sick"]
                                                                                                     if is_sick(k, a))}
    if c["calendar"].get("enabled"):
        p = position(c, k.r)
        rec.update({"year": p["year"], "phase": p["phase"], "severity": year_severity(k, p["year"])})
    st["log"].append(rec)
    k.log("environment_round", None, rec, vis="monitor")


# ---------------------------------------------------------------------- what agents see
def almanac_line(k, aid) -> str:
    c = cfg(k.spec)
    if not c["calendar"].get("enabled"):
        return ""
    p = position(c, k.r)
    sev = year_severity(k, p["year"])
    parts = [f"Season: {p['phase']}" + (f" ({p['left']} more round{'s' if p['left'] != 1 else ''})" if p["left"] else
                                          " (its last round)")]
    if p["to_winter"]:
        parts.append(f"winter in {p['to_winter']} round{'s' if p['to_winter'] != 1 else ''}")
    if severity_known(c, k.r):
        parts.append(f"this year is {sev}")
    n = int(c["almanac"].get("years", 0))
    past = [year_severity(k, y) for y in range(max(0, p["year"] - n), p["year"])]
    if past:
        parts.append("past years: " + ", ".join(reversed(past)) + " (latest first)")
    told = state(k)["told"].get(f"year:{p['year'] + 1}")
    if told and aid in told["to"]:
        parts.append(f"your forecast for next year: {told['forecast']}")
    if is_sick(k, aid):
        left = int(state(k)["sick"][aid]) - k.r
        parts.append(f"you are ill ({left} more round{'s' if left != 1 else ''} after this one)" if left else
                     "you are ill (your last round of it)")
    return "; ".join(parts) + "."


def state_lines(k, aid) -> list:
    if not on(k):
        return []
    line = almanac_line(k, aid)
    return [line] if line else []


def law_api(k, lid) -> dict:
    if not on(k):
        return {}
    c = cfg(k.spec)

    def season_():
        """{phase, year, rounds_left, to_winter, severity (once announced, else None)}."""
        if not c["calendar"].get("enabled"):
            return {}
        p = position(c, k.r)
        known = severity_known(c, k.r)
        return {"phase": p["phase"], "year": p["year"], "rounds_left": p["left"], "to_winter": p["to_winter"],
                "severity": year_severity(k, p["year"]) if known else None}

    def almanac():
        """Past years: [{year, severity}], and the micro-events that were public: [{round, type, text}]."""
        p = position(c, k.r) if c["calendar"].get("enabled") else {"year": 0}
        pub = [{"round": f["round"], "type": f["type"], "target": f.get("target")} for f in state(k)["fired"]
               if f.get("recipients") == "public"]
        return {"years": [{"year": y, "severity": year_severity(k, y)} for y in range(p["year"])], "events": pub}

    def ill(agent):
        return is_sick(k, str(agent))

    return {"season": season_, "almanac": almanac, "ill": ill}


def snapshot_fields(k) -> dict:
    if not on(k):
        return {}
    c = cfg(k.spec)
    out = {"sick": sorted(a for a in state(k)["sick"] if is_sick(k, a))}
    if c["calendar"].get("enabled"):
        p = position(c, k.r)
        out.update({"phase": p["phase"], "year": p["year"], "severity": year_severity(k, p["year"])})
    return {"environment": out}


def truth(k, inst=None) -> dict:
    if not on(k):
        return {}
    sched = k.inst.get("environment") or {}
    return {"environment": {"hash": sched.get("hash"), "years": sched.get("years"), "fired": state(k)["fired"],
                            "told": state(k)["told"]}}

