"""Farming and cattle (spec/economy/production.md, livestock.md; D2-52 to D2-54, D2-59, D2-63, D4-38 to D4-45).

A field is counted in plots (D4-40, D2-59: about 16 seed a sowing). Its crop record holds the seed sown (in plot-equivalents of
seed: dibbled seed counts for more), the share of it on broken soil, the weeding done, what is left and how much ground is left to
reap; what is left is always recomputed from those. The soil's fertility multiplies the harvest; each crop takes from it and restores
it toward a level; fallow, grazing and dung restore it too (D4-39). A crop grows from the day sown for its share of the year; the
cold kills what is still growing unless it is hardy; the same crop twice is likelier to fail (D2-53).

Cattle are one kind with roles (D2-63): cows, oxen, bulls, and young counted with the herd. A herd grazes the parcel it is on, eats
fodder from its holder's stores where the grass runs short, breeds where a bull is with the cows and the herd is fed (D4-44), wears
its pasture down if too many (D4-45), drops dung where it stands, and strays into crops if nobody watches it.

The acts (sow, hoe, plough, weed, manure, reap, herd, milk, slaughter, drive) see only `Here` and `Mind` (D4-35); `night` is the
engine's.
"""
from __future__ import annotations

import math

from cybertron2.engine import knowledge as KN
from cybertron2.engine.data import CROP_OF, CROPS, FENCES, ITEMS, SEED_CROP, TECHNIQUES
from cybertron2.engine.here import Refused, show

ROLES = ("cows", "oxen", "bulls", "young")
ROLE_WORD = {"cows": ("cow", "cows"), "oxen": ("ox", "oxen"), "bulls": ("bull", "bulls"), "young": ("calf", "calves")}
ROLE_OF = {w: r for r, ws in ROLE_WORD.items() for w in ws} | {r: r for r in ROLES} | {"steer": "young", "heifer": "young"}


# ---------------------------------------------------------------------- crops: shared arithmetic
def weed_gain(f, units_a_plot) -> float:
    return float(f["weed_max"]) * (1 - math.exp(-units_a_plot / float(f["weed_tau"])))


def crop_left(f, c) -> float:
    """What a crop will give if reaped now: its base, weeding, the ground still standing, and the rot."""
    if c.get("failed") and c.get("shown_failed"):
        return 0.0
    area = max(1e-9, c["area"])
    gain = weed_gain(f, c.get("weeded", 0.0) / area)
    return round(c["base"] * (1 + gain) * (c["area_left"] / area) * c.get("rot", 1.0), 4)


def normalise_crop(par, c, day, grow) -> dict:
    """A seeded crop ({kind, left, ripe_day}) in the full record."""
    fam = CROP_OF.get(str(c.get("kind", "grain")).lower(), "grain")
    area = float(c.get("area", par["size"]))
    left = float(c.get("left", 0.0))
    out = {"kind": c.get("kind", fam), "crop": fam, "sown": int(c.get("sown", int(c.get("ripe_day", day)) - grow)),
           "ripe_day": int(c.get("ripe_day", day + grow)), "window": int(c.get("window", 2)),
           "seed": float(c.get("seed", area * float(_f_default()["plot_seed"]))),
           "area": area, "area_left": area, "broken": float(c.get("broken", 0.0)), "weeded": 0.0, "base": left, "rot": 1.0,
           "failed": bool(c.get("failed", False)), "hardy": CROPS[fam]["hardy"], "sower": c.get("sower")}
    out["left"] = crop_left(_f_default(), out)
    return out


def _f_default():
    from cybertron2.engine.data import PHYSICS
    return PHYSICS["farming"]


def grow_days(year, fam) -> int:
    return max(2, round(year * float(CROPS[fam]["share"])))


def soil_step(f, fert, fam_or_state) -> float:
    """One crop slot's effect on the soil (02l §2): a crop takes its share, then the soil comes back toward a level."""
    if fam_or_state in CROPS:
        c = CROPS[fam_or_state]
        fert *= 1 - float(c["takes"])
        r, level = c["restores"]
    elif fam_or_state == "grazed":
        r, level = f["grazed"]
    else:
        r, level = float(f["fallow"]), 1.0
    return round(fert + float(r) * max(0.0, float(level) - fert), 4)


def soil_word(fert) -> str:
    return "worn out" if fert < 0.55 else "tired" if fert < 0.8 else "good" if fert < 1.05 else "rich"


# ---------------------------------------------------------------------- cattle: shared arithmetic
def head(h) -> int:
    return int(sum(int(h.get(r, 0)) for r in ROLES))


def herd_capacity(p, h, day, drovers=0) -> int:
    """How many head the people with a herd hold together (D2-128): 10 a drover on a road, 30 a herder on pasture, about 6 unherded."""
    from cybertron2.engine.data import HERDS
    cap = HERDS["capacity"]
    if drovers:
        return int(cap["drover"]) * drovers
    hd = h.get("herders") or {}
    n = int(hd.get("n", 0)) if hd.get("day") == day else 0
    return int(cap["herder"]) * n if n else int(cap["unherded"])


def herd_words(h) -> str:
    bits = [f"{int(h[r])} {ROLE_WORD[r][0 if int(h[r]) == 1 else 1]}" for r in ROLES if int(h.get(r, 0)) > 0]
    milk = int(round(h.get("in_milk", 0.0)))
    return ", ".join(bits) + (f" ({milk} in milk)" if milk else "") if bits else "no beasts"


def usable_herds(here, role, n=1) -> list:
    """Herds here with at least n of a role that this person may use (access by a claim, D4-23; or ones nobody holds)."""
    out = []
    for hid, h in here.herds().items():
        if int(h.get(role, 0)) >= n and ("access" in here.rights(("herd", hid)) or not here.claims(("herd", hid))):
            out.append(hid)
    return out


def team_shortfall(here, t) -> str:
    """What is missing for work that needs animals or equipment at hand (the plough: a yoked pair, a plough, harness)."""
    for role, n in (t.get("animals") or {}).items():
        if not usable_herds(here, role, n):
            return f"it needs {n} {ROLE_WORD[role][0 if n == 1 else 1]} you may use, here"
    for item, n in (t.get("uses") or {}).items():
        have = KN.available(here, item)
        if have + 1e-9 < n:
            return f"it needs {n} {item} to hand (you have {show(have)})"
    return ""


# ---------------------------------------------------------------------- the acts (Here and Mind only)
def act(here, mind, tech, key, place_name, out, m, tm, a) -> tuple:
    """The farming and cattle yields. Returns (got, gives, word, thing)."""
    t = TECHNIQUES[tech]
    y = t["yield"]
    k = y["kind"]
    f = here.p["farming"]
    if k == "sow":
        return _sow(here, mind, tech, key, place_name, out, m, a, f)
    if k == "works":
        return _works(here, mind, tech, key, place_name, out, m * tm, a, y)
    if k == "fence":
        return _fence(here, mind, tech, key, place_name, out, m * tm, a, y)
    if k == "gate":
        return _gate(here, key, place_name, y["gate"])
    if k == "select":
        c = dict(here.parcels()[key]["crop"])
        c["selected_by"] = here.name
        here.apply("set", ref=("parcel", key), field="crop", value=c)
        return 0.0, None, f"You went through the {c['kind']} in {place_name}, marking the best ears to keep for seed.", ("parcel", key)
    if k == "break":
        return _break(here, tech, key, place_name, out, m * tm, f)
    if k == "tend":
        par = here.parcels()[key]
        c = dict(par["crop"])
        c["weeded"] = round(c.get("weeded", 0.0) + m, 4)
        c["left"] = crop_left(f, c)
        here.apply("set", ref=("parcel", key), field="crop", value=c)
        return 0.0, None, f"You weeded the {c['kind']} in {place_name}: it will bear more.", ("parcel", key)
    if k == "manure":
        par = here.parcels()[key]
        plots = min(float(par["size"]), float(y["plots"]) * m)
        fert = par["fertility"]
        r, level = f["manure"]
        new = round(fert + float(r) * max(0.0, float(level) - fert) * plots / max(1.0, float(par["size"])), 4)
        here.apply("set", ref=("parcel", key), field="fertility", value=new)
        return 0.0, None, f"You spread dung on {place_name}: the soil will be the better for it.", ("parcel", key)
    if k == "crop":
        return _reap(here, tech, key, place_name, out, m * tm, f, y)
    if k == "herd":
        hid = _herd_on(here, key, a)
        here.apply("set", ref=("herd", hid), field="watched", value=here.day)
        hd = here.herds()[hid].get("herders") or {}
        n = int(hd.get("n", 0)) + 1 if hd.get("day") == here.day else 1        # herders today: each holds about 30 head (D2-128)
        here.apply("set", ref=("herd", hid), field="herders", value={"day": here.day, "n": n})
        return 0.0, None, f"You watched {here.herds()[hid]['name']} on {place_name} today.", ("herd", hid)
    if k == "milk":
        hid = _herd_on(here, key, a, role="cows")
        h = here.herds()[hid]
        mk = h["milked"] if h["milked"]["day"] == here.day else {"day": here.day, "n": 0}
        n = min(int(y["cows"]), int(round(h.get("in_milk", 0.0))) - mk["n"])
        here.apply("set", ref=("herd", hid), field="milked", value={"day": here.day, "n": mk["n"] + n})
        return round(n * float(y["each"]) * m, 2), "milk", "", ("herd", hid)
    if k == "slaughter":
        return _slaughter(here, key, out, a, y)
    raise Refused(f"{tech} cannot be done that way")


def _herd_on(here, key, a, role=None):
    hs = [hid for hid, h in here.herds().items() if h["parcel"] == key and head(h) > 0 and (role is None or int(h.get(role, 0)) > 0)]
    want = a.get("thing")
    pick = next((hid for hid in hs if want and str(want).lower() in (hid.lower(), here.herds()[hid]["name"].lower())), None)
    if not hs:
        raise Refused("there are no beasts there")
    return pick or hs[0]


def ground_mult(p, par) -> float:
    """A plot's yield from its ground (D2-66): wet or hill ground yields less until field works bring it to 1.0."""
    pen = float(p["ground"].get(par.get("ground") or "", 1.0))
    wk = par.get("works") or {}
    done = min(1.0, float(wk.get("done", 0.0)) / max(1.0, float(par["size"]))) if wk.get("ground") == par.get("ground") else 0.0
    return round(pen + (1 - pen) * done, 4)


def master_share(here, mind, tech) -> float:
    lo, hi = KN.curve(tech)
    return max(0.0, min(1.0, (KN.skill(mind, tech) - lo) / (hi - lo)))


def _works(here, mind, tech, key, place_name, out, mult, a, y):
    """A field work as a project on the plot (D2-66): work by anyone counts on a day one who knows the technique works on it."""
    par = here.parcels()[key]
    wk = dict(par.get("works") or {"ground": y["ground"], "units": 0.0, "done": 0.0, "kept": 0.0, "pending": {}})
    size = float(par["size"])
    leads = KN.level(mind, tech) in ("capable", "known")
    stone = float(y.get("stone", 0.0)) / float(y["units"]) * mult
    if stone > 0:
        from cybertron2.engine.verbs import _consume
        from cybertron2.engine.verbs import _src
        _consume(here, {"stone": round(stone, 3)}, extra=_src(here, a.get("for") and here.household(), out))
    if wk["done"] >= size - 1e-6:                                              # finished: this is upkeep (mending)
        wk["kept"] = round(wk.get("kept", 0.0) + mult, 3)
        here.apply("set", ref=("parcel", key), field="works", value=wk)
        return 0.0, None, f"You mended the {_works_word(y)} of {place_name}.", ("parcel", key)
    day = str(here.day)
    pend = dict(wk.get("pending") or {})
    p = pend.get(day, {"units": 0.0, "led": False})
    p = {"units": round(p["units"] + mult, 3), "led": p["led"] or leads}
    pend = {day: p}                                                          # only today's work waits for a leader
    wk["pending"] = pend
    here.apply("set", ref=("parcel", key), field="works", value=wk)
    how = "" if leads else " (it holds only if someone who knows how to lay them out works on them today)"
    return 0.0, None, f"You worked on the {_works_word(y)} of {place_name}{how}.", ("parcel", key)


# ---------------------------------------------------------------------- fences round a parcel and gates (D2-130, D2-132)
def fence_need(par, kind) -> dict:
    """What a whole fence of this kind round this parcel takes: work units and materials, x the square root of its size."""
    d = FENCES[kind]
    r = math.sqrt(max(1.0, float(par["size"])))
    return {"units": float(d["units"]) * r, "inputs": {i: q * r for i, q in d["inputs"].items()}}


def fence_word(kind) -> str:
    return FENCES[kind]["words"][0]


def _fence(here, mind, tech, key, place_name, out, mult, a, y):
    """Fencing as a field work (D2-130): materials go in with the work, in proportion; a wall's work counts on a day one who knows
    walling works on it. Work on a whole fence is mending (a quarter of the build a season keeps it); on a gappy one it restores it."""
    par = here.parcels()[key]
    kind = y["fence"]
    fc = dict(par.get("fence") or {})
    if not fc or fc.get("kind") != kind or (fc.get("level", 0) <= 0 and fc.get("built")):
        fc = {"kind": kind, "units": 0.0, "level": 0, "built": False, "gate": "shut", "mend": 0.0, "pending": {}}
    need = fence_need(par, kind)
    from cybertron2.engine.verbs import _consume, _src
    _consume(here, {i: round(q / need["units"] * mult, 3) for i, q in need["inputs"].items()}, extra=_src(here, a.get("for") and here.household(), out))
    word = fence_word(kind)
    led = FENCES[kind].get("led")
    leads = not led or KN.level(mind, led) in ("capable", "known")
    if fc["built"]:
        fc["mend"] = round(float(fc.get("mend", 0.0)) + mult, 3)
        here.apply("set", ref=("parcel", key), field="fence", value=fc)
        return 0.0, None, f"You mended the {word} round {place_name}.", ("parcel", key)
    day = str(here.day)
    p = (fc.get("pending") or {}).get(day, {"units": 0.0, "led": False})
    fc["pending"] = {day: {"units": round(p["units"] + mult, 3), "led": p["led"] or leads}}
    here.apply("set", ref=("parcel", key), field="fence", value=fc)
    done = min(1.0, (fc["units"] + fc["pending"][day]["units"]) / need["units"])
    how = "" if leads else f" (it holds only if someone who knows {KN.label(led)} works on it today)"
    return 0.0, None, f"You worked on a {word} round {place_name}: about {round(done * 100):d} parts in a hundred done{how}.", ("parcel", key)


def _gate(here, key, place_name, to):
    """Opening a gate and leaving it, or shutting one: no units; seen by whoever is about (D2-132)."""
    par = here.parcels()[key]
    fc = dict(par["fence"])
    fc["gate"] = to
    if to == "open":
        fc["opened"] = {"day": here.day, "by": here.name}
    here.apply("set", ref=("parcel", key), field="fence", value=fc)
    holders = [c["claimant"] for c in here.claims(("parcel", key))]
    people = sorted({m for x in holders for m in ([x] if x in here.people() else (here.households().get(x) or {}).get("members", []))})
    here.event("gate", f"{here.name} {'opened the gate of ' + place_name + ' and left it open' if to == 'open' else 'shut the gate of ' + place_name}",
               actor=here.name, about=[f"parcel:{key}"], salience=0.45 if to == "open" else 0.25, tags=["animals"], concerns=people)
    return 0.0, None, (f"You opened the gate of {place_name} and left it standing open." if to == "open"
                       else f"You shut the gate of {place_name}."), ("parcel", key)


def _works_word(y) -> str:
    return "ditches and banks" if y["ground"] == "wet" else "terraces"


def _sow(here, mind, tech, key, place_name, out, m, a, f):
    par = here.parcels()[key]
    if not a.get("item"):
        raise Refused(f"say which seed to sow (item: {', '.join(sorted(SEED_CROP))})")
    seed_good = str(a.get("item")).lower()
    fam = SEED_CROP.get(seed_good) or CROP_OF.get(seed_good)
    if fam is None:
        raise Refused(f"{seed_good!r} is not seed; one sows {', '.join(sorted(SEED_CROP))}")
    seed_good = CROPS[fam]["seed"]
    mods = a.get("_mods") or {}
    y = {**TECHNIQUES[tech]["yield"], **(mods.get("yield") or {})}           # the sowing method (a modifier: D2-94)
    c = par.get("crop")
    if c and (c["crop"] != fam or here.day >= c["ripe_day"]):
        raise Refused(f"{par['name']} already has {c['kind']} in it")
    worth = float(y["worth"])
    sown = c["seed"] if c else 0.0                                         # in plot-seed equivalents
    room = float(par["size"]) * float(f["plot_seed"]) - sown
    from cybertron2.engine.verbs import _party, _src
    extra = _src(here, _party(here, a["for"]) if a.get("for") else None, out)
    have = KN.available(here, seed_good, extra=extra)
    seed = round(min(float(y["seed"]) * m, room / worth, have), 2)
    if seed <= 1e-9:
        raise Refused(f"you have no {seed_good} to sow" if room > 1e-9 else f"{par['name']} is sown as thick as it will take")
    from cybertron2.engine.verbs import _consume
    _consume(here, {seed_good: seed}, extra=extra)
    year = here.year_days()
    new = c is None
    if new:
        last = par.get("last_crop")
        fail = f["fail"][1] if last == fam else f["fail"][0]
        failed = here.rng("blight", here.day, key).random() < float(fail)
        g = grow_days(year, fam)
        if KN.level(mind, "select seed") == "known":                          # seed selection (D2-65)
            g = max(2, round(g * float(here.p["seed_selection"])))
        name = next((n for n in CROPS[fam]["names"] if n == str(par.get("last_kind", "")).lower()), CROPS[fam]["names"][0])
        c = {"kind": name, "crop": fam, "sown": here.day, "ripe_day": here.day + g, "window": int(f["window"]), "seed": 0.0, "area": 0.0,
             "area_left": 0.0, "broken": 0.0, "weeded": 0.0, "base": 0.0, "rot": 1.0, "failed": failed, "hardy": CROPS[fam]["hardy"],
             "sower": a.get("for") or here.name}
    c = dict(c)
    eq = seed * worth
    area = eq / float(f["plot_seed"])
    broken_here = min(float(par.get("broken", 0.0)), area)
    if broken_here > 0:
        here.apply("set", ref=("parcel", key), field="broken", value=round(float(par.get("broken", 0.0)) - broken_here, 4))
    ratio = float(f["ratio"]) + float(f["break_gain"]) * (broken_here / area)
    c["seed"] = round(c["seed"] + eq, 4)
    c["area"] = round(c["area"] + area, 4)
    c["area_left"] = round(c["area_left"] + area, 4)
    c["broken"] = round(c["broken"] + broken_here, 4)
    skill_yield = 1 + float(here.p["master_yield"]) * master_share(here, mind, tech)       # D2-64
    c["base"] = round(c["base"] + eq * ratio * float(par["fertility"]) * ground_mult(here.p, par) * skill_yield, 4)
    c["left"] = crop_left(f, c)
    here.apply("set", ref=("parcel", key), field="crop", value=c)
    how = mods.get("word") or "sowed"
    soil = " on broken ground" if broken_here > 0 else ""
    word = (f"You {how} {show(seed)} {seed_good} in {place_name}{soil} (about {show(area)} of a plot); the {c['kind']} should be ready to "
            f"reap in about {c['ripe_day'] - here.day} days.")
    if not c["hardy"]:
        word += " It is not hardy: winter will kill it if it is still growing."
    return 0.0, None, word, ("parcel", key)


def _break(here, tech, key, place_name, out, mult, f):
    par = here.parcels()[key]
    y = TECHNIQUES[tech]["yield"]
    sown = float((par.get("crop") or {}).get("area", 0.0))                     # break only the ground not yet sown
    room = float(par["size"]) - float(par.get("broken", 0.0)) - sown
    plots = round(min(room, float(y["plots"]) * mult), 4)
    if plots <= 1e-9:
        raise Refused(f"{par['name']} is already broken and ready for sowing")
    here.apply("set", ref=("parcel", key), field="broken", value=round(float(par.get("broken", 0.0)) + plots, 4))
    stone = round(float(y.get("stone", 0.0)) * plots, 2)
    if stone > 0:
        here.apply("create", dst=out, item="stone", qty=stone, why="fieldstone")          # D2-56
    for item, n in (TECHNIQUES[tech].get("uses") or {}).items():
        if ITEMS[item].get("life"):
            src = next((cid for cid in here.takeable() if here.contents(cid).get(item, 0) >= 1), None)
            if src:
                here.apply("wear", container=src, item=item, uses=plots if item == "wooden plough" else 1.0 / n)
    how = "ploughed" if tech == "plough" else "hoed"
    left = float(par["size"]) - float(par.get("broken", 0.0)) - plots
    word = f"You {how} {show(plots)} of a plot of {place_name}" + (f", turning up {show(stone)} stone" if stone >= 0.05 else "")
    word += "; the field is ready for sowing." if left <= 1e-6 else f"; {show(left)} plots still unbroken."
    return 0.0, None, word, ("parcel", key)


def _reap(here, tech, key, place_name, out, mult, f, y):
    par = here.parcels()[key]
    c = dict(par["crop"])
    if c.get("failed") and c.get("shown_failed"):
        raise Refused(f"the {c['kind']} in {place_name} has failed: there is nothing to reap")
    plots = min(c["area_left"], float(y["plots"]) * mult)
    left = crop_left(f, c)
    got = round(left * plots / max(1e-9, c["area_left"]), 2)
    here.apply("draw", parcel=key, key="crop", qty=got)
    c = dict(here.parcels()[key]["crop"])                                       # the draw took its ground with it (world.p_draw)
    c["left"] = crop_left(f, c)
    here.apply("set", ref=("parcel", key), field="crop", value=c)
    gives = CROPS[c["crop"]]["gives"]
    straw = round(float(y.get("straw", 0.0)) * plots, 2) if CROPS[c["crop"]]["straw"] else 0.0
    if straw > 0:
        here.apply("create", dst=out, item="straw", qty=straw, why="reap")
    word = ""
    if c["area_left"] <= 1e-6:
        word = f" {place_name} is reaped."
    return got, gives, word, ("parcel", key)


def _slaughter(here, key, out, a, y):
    hid = _herd_on(here, key, a)
    h = here.herds()[hid]
    want = ROLE_OF.get(str(a.get("item") or "").lower().strip())
    role = want or next(r for r in ("young", "cows", "oxen", "bulls") if int(h.get(r, 0)) > 0)
    if int(h.get(role, 0)) <= 0:
        raise Refused(f"there is no {ROLE_WORD[role][0]} in {h['name']} ({herd_words(h)})")
    here.apply("set", ref=("herd", hid), field=role, value=int(h[role]) - 1)
    if role == "cows" and h.get("in_milk", 0) > int(h["cows"]) - 1:
        here.apply("set", ref=("herd", hid), field="in_milk", value=float(max(0, int(h["cows"]) - 1)))
    here.apply("set", ref=("herd", hid), field="count", value=head(here.herds()[hid]))
    gives = y["gives"][role]
    for item, q in gives.items():
        here.apply("create", dst=out, item=item, qty=q, why="slaughter")
    word = f"You slaughtered a {ROLE_WORD[role][0]} of {h['name']}: " + ", ".join(f"{q:g} {i}" for i, q in gives.items()) + "."
    return 0.0, None, word, ("herd", hid)


def ready(here, tech, key) -> str:
    """'' if this farming or cattle work can be done on this parcel now, else why not."""
    t = TECHNIQUES[tech]
    y = t["yield"]["kind"]
    p = here.parcels()[key]
    c = p.get("crop")
    f = here.p["farming"]
    if t.get("seasons") and here.calendar()["season"] not in t["seasons"]:
        return f"{KN.label(tech)} is done in {' and '.join(t['seasons'])}"
    if y == "sow" and c and here.day >= c["ripe_day"]:
        return f"{p['name']} has {c['kind']} standing in it"
    if y == "sow" and c and c["seed"] >= float(p["size"]) * float(f["plot_seed"]) - 1e-6:
        return f"{p['name']} is sown as thick as it will take"
    if y == "break":
        if c and (here.day >= int(c["ripe_day"]) or c["area"] >= float(p["size"]) - 1e-6):
            return f"{p['name']} has a crop in it"
        if float(p.get("broken", 0.0)) + (c["area"] if c else 0.0) >= float(p["size"]) - 1e-6:
            return f"{p['name']} is broken and ready for sowing" if not c else f"the rest of {p['name']} is broken and ready for sowing"
        why = team_shortfall(here, t)
        if why:
            return why
    if y in ("crop", "tend"):
        if not c or c["area_left"] <= 1e-6:
            return f"there is no crop in {p['name']}"
        if c.get("failed") and c.get("shown_failed"):
            return f"the {c['kind']} in {p['name']} has failed"
        if y == "crop" and here.day < int(c["ripe_day"]):
            return f"the {c['kind']} in {p['name']} is not ripe yet"
        if y == "tend" and here.day >= int(c["ripe_day"]):
            return f"the {c['kind']} in {p['name']} is ripe: past weeding"
        if y == "tend" and weed_gain(f, c.get("weeded", 0.0) / max(1e-9, c["area"])) >= float(f["weed_max"]) * 0.95:
            return f"the {c['kind']} in {p['name']} is as clean as weeding makes it"
    if y == "fence":
        fc = p.get("fence") or {}
        kind = t["yield"]["fence"]
        if fc.get("built") and fc.get("level", 0) > 0 and fc.get("kind") != kind:
            return f"there is already a {fence_word(fc['kind'])} round {p['name']}"
        if fc.get("built") and fc.get("level", 0) >= 2 and float(fc.get("mend", 0.0)) >= float(FENCES[kind]["mend"]) * fence_need(p, kind)["units"] - 1e-6:
            return f"the {fence_word(kind)} round {p['name']} is whole and mended this season"
    if y == "gate":
        fc = p.get("fence") or {}
        if not fc.get("built") or fc.get("level", 0) <= 0:
            return f"there is no fence round {p['name']}, so no gate"
        if fc.get("gate") == t["yield"]["gate"]:
            return f"the gate of {p['name']} is {'open' if fc['gate'] == 'open' else 'shut'} already"
    if y == "works":
        yy = t["yield"]
        if p.get("ground") != yy["ground"]:
            return f"{p['name']} is not {'wet' if yy['ground'] == 'wet' else 'hill'} ground"
        wk = p.get("works") or {}
        if wk.get("done", 0) >= float(p["size"]) - 1e-6 and wk.get("kept", 0) >= float(yy["upkeep"]) * float(p["size"]) - 1e-6:
            return f"the {_works_word(yy)} of {p['name']} are whole and kept this season"
    if y == "select":
        if not c or here.day < int(c["ripe_day"]) or c["area_left"] <= 1e-6:
            return f"there is no ripe crop in {p['name']} to choose seed from"
        if c.get("selected_by") == here.name:
            return f"you have chosen the seed from {p['name']} already"
    if y in ("herd", "milk", "slaughter"):
        hs = [h for h in here.herds().values() if h["parcel"] == key and head(h) > 0]
        if not hs:
            return f"there are no beasts on {p['name']}"
        if y == "milk":
            n = sum(int(round(h.get("in_milk", 0.0))) - (h["milked"]["n"] if h["milked"]["day"] == here.day else 0) for h in hs)
            if n <= 0:
                return "no cow there is in milk" if not any(h.get("in_milk", 0) >= 0.5 for h in hs) else "the cows in milk are milked today"
        if y == "herd" and all(h.get("watched") == here.day and head(h) <= herd_capacity(here.p, h, here.day) for h in hs):
            return "the beasts there are watched today"
    return ""


def drive(here, a, party) -> str:
    """Move beasts to another parcel here (D4-44: a bull kept apart does not breed). Moving part of a herd makes a herd of its own,
    held as the first was; beasts brought to a herd held the same way join it."""
    hid = here.herd(a.get("thing") or a.get("what") or "")
    if hid is None:
        raise Refused("there is no herd here by that name")
    h = here.herds()[hid]
    to = here.parcel(a.get("to") or a.get("at") or "")
    if to is None:
        raise Refused(f"there is no place called {a.get('to')!r} here to drive them to")
    if here.parcels()[to]["cover"] not in ("pasture", "meadow", "field", "scrub", "forest", "built"):
        raise Refused(f"beasts cannot be kept on {here.parcels()[to]['name']}")
    word = str(a.get("item") or "").lower().strip()
    roles = list(ROLES) if word in ("", "all", "the herd", "herd", "them") else [ROLE_OF.get(word)]
    if roles == [None]:
        raise Refused(f"{word!r} is not a kind of beast in a herd (cow, ox, bull, calf, or all)")
    qty = a.get("qty")
    moving = {r: int(h.get(r, 0)) if qty is None or len(roles) > 1 else min(int(h.get(r, 0)), int(qty)) for r in roles}
    if sum(moving.values()) <= 0:
        raise Refused(f"{h['name']} has none of those ({herd_words(h)})")
    claims = [(c["claimant"], c["rights"], c["grounds"]) for c in here.claims(("herd", hid))]
    whole = all(moving.get(r, 0) == int(h.get(r, 0)) for r in ROLES)
    dest = next((x for x, g in here.herds().items() if x != hid and g["parcel"] == to and g["kind"] == h["kind"]
                 and sorted((c["claimant"], tuple(c["rights"])) for c in here.claims(("herd", x)))
                 == sorted((c[0], tuple(c[1])) for c in claims)), None)
    milk = min(float(h.get("in_milk", 0.0)), float(moving.get("cows", 0)))
    if whole and dest is None:
        here.apply("set", ref=("herd", hid), field="parcel", value=to)
        here.apply("set", ref=("herd", hid), field="home", value=to)
        moved_to = hid
    else:
        if dest is None:
            dest = here.apply("new_herd", like=hid, parcel=to)
            for claimant, rights, grounds in claims:
                here.apply("claim", thing=("herd", dest), claimant=claimant, rights=rights, grounds=grounds)
        g = here.herds()[dest]
        for r, n in moving.items():
            here.apply("set", ref=("herd", hid), field=r, value=int(h.get(r, 0)) - n)
            here.apply("set", ref=("herd", dest), field=r, value=int(g.get(r, 0)) + n)
        here.apply("set", ref=("herd", hid), field="in_milk", value=round(float(h.get("in_milk", 0.0)) - milk, 4))
        here.apply("set", ref=("herd", dest), field="in_milk", value=round(float(g.get("in_milk", 0.0)) + milk, 4))
        for x in (hid, dest):
            here.apply("set", ref=("herd", x), field="count", value=head(here.herds()[x]))
        moved_to = dest
    what = ", ".join(f"{n} {ROLE_WORD[r][0 if n == 1 else 1]}" for r, n in moving.items() if n)
    pname = here.parcels()[to]["name"]
    here.event("work", f"{here.name} drove {what} of {h['name']} to {pname}", actor=here.name, about=[f"herd:{moved_to}", f"parcel:{to}"],
               salience=0.3, tags=["animals"])
    here.record("drive", None, party, site=to)
    return f"You drove {what} to {pname}."


# ---------------------------------------------------------------------- the night (engine side)
def night(w) -> dict:
    """Crops grow, fail, die of the cold, ripen and rot; fields rest; herds graze, eat fodder, breed, drop dung and stray."""
    rec = {"crops": [], "herds": []}
    _crops(w, rec)
    from cybertron2.engine import herds as HD
    HD.night(w, rec)                                                         # fences, splitting, wandering, roads (D2-117 to D2-131)
    _herds(w, rec)
    return rec


def _works_night(w, rec):
    """Field works (D2-66): today's work holds if one who knew how worked on it; each season's upkeep, or the works decay a level."""
    new_season = w.calendar(w.d + 1)["season"] != w.calendar()["season"]
    for pid, par in w.s["parcels"].items():
        wk = par.get("works")
        if not wk:
            continue
        wk = dict(wk)
        tech = "ditch" if wk["ground"] == "wet" else "terrace"
        y = TECHNIQUES[tech]["yield"]
        p = (wk.get("pending") or {}).get(str(w.d))
        if p and p["led"]:
            wk["units"] = round(wk["units"] + p["units"], 3)
            wk["done"] = round(min(float(par["size"]), wk["units"] / float(y["units"])), 4)
            rec["crops"].append((pid, "works", wk["done"]))
        wk["pending"] = {}
        if new_season and wk["done"] > 0:
            if wk.get("kept", 0.0) + 1e-6 < float(y["upkeep"]) * wk["done"] and wk.get("finished_season") != w.calendar()["season"]:
                wk["done"] = round(wk["done"] * 0.75, 4)                         # unkept, they decay a level
                wk["units"] = round(wk["done"] * float(y["units"]), 3)
                w.event(par["node"], "works", f"the {_works_word(y)} of {par['name']} are falling in for want of mending",
                        about=[f"parcel:{pid}"], salience=0.4, tags=["farming"])
            wk["kept"] = 0.0
        if wk["done"] >= float(par["size"]) - 1e-6 and not wk.get("finished_season"):
            wk["finished_season"] = w.calendar()["season"]
        w.apply("set", par["node"], ref=("parcel", pid), field="works", value=wk)


def _crops(w, rec):
    _works_night(w, rec)
    f = w.p["farming"]
    year = w.year_days()
    winter = w.calendar()["season"] == "winter"
    slot = grow_days(year, "grain")
    for pid, par in w.s["parcels"].items():
        if par["cover"] != "field":
            continue
        c = par.get("crop")
        node = par["node"]
        if c:
            c = dict(c)
            growing = w.d < int(c["ripe_day"])
            if growing and c.get("failed") and not c.get("shown_failed") and w.d >= c["sown"] + (c["ripe_day"] - c["sown"]) // 2:
                c["shown_failed"] = True
                w.event(node, "crop", f"the {c['kind']} in {par['name']} has blight: it is withering and will bear nothing",
                        about=[f"parcel:{pid}"], salience=0.6, tags=["farming", "food"])
                rec["crops"].append((pid, "failed"))
            if growing and winter and not c.get("hardy"):
                c["area_left"] = 0.0
                c["killed"] = True
                w.event(node, "crop", f"the frost has killed the {c['kind']} growing in {par['name']}", about=[f"parcel:{pid}"],
                        salience=0.7, tags=["farming", "food", "season"])
                rec["crops"].append((pid, "frost"))
            elif w.d >= int(c["ripe_day"]) + int(c.get("window", f["window"])):
                c["rot"] = round(c.get("rot", 1.0) * (1 - float(f["rot"])), 4)
                c["rotting"] = True
            c["left"] = crop_left(f, c)
            withering = c.get("failed") and growing                             # a blighted crop stands until its day
            if c["area_left"] <= 1e-6 or (c["left"] <= 0.05 and not withering):
                fert = soil_step(f, par["fertility"], c["crop"])               # the crop's slot ends (D4-39)
                w.apply("set", node, ref=("parcel", pid), field="fertility", value=fert)
                w.apply("set", node, ref=("parcel", pid), field="last_crop", value=c["crop"])
                w.apply("set", node, ref=("parcel", pid), field="last_kind", value=c["kind"])
                w.apply("set", node, ref=("parcel", pid), field="crop", value=None)
                w.apply("set", node, ref=("parcel", pid), field="fallow_since", value=w.d)
            else:
                w.apply("set", node, ref=("parcel", pid), field="crop", value=c)
        else:                                                                    # resting: fallow restores (grazed: in _herds)
            grazed = any(h["parcel"] == pid and head(h) > 0 for h in w.s["herds"].values())
            if not grazed:
                d = 1 - (1 - float(f["fallow"])) ** (1 / slot)
                fert = round(par["fertility"] + d * max(0.0, 1.0 - par["fertility"]), 4)
                w.apply("set", node, ref=("parcel", pid), field="fertility", value=fert)


def _fodder_stores(w, hid) -> list:
    """The stores at the herd's node of whoever holds it (the holders' houses and buildings)."""
    h = w.s["herds"][hid]
    holders = {c["claimant"] for c in w.s["claims"].values() if tuple(c["thing"]) == ("herd", hid) and not c.get("ended")}
    out = []
    for bid, b in w.s["buildings"].items():
        if b["node"] != h["node"]:
            continue
        bh = {c["claimant"] for c in w.s["claims"].values() if tuple(c["thing"]) == ("building", bid) and not c.get("ended")}
        if bh & holders:
            out.append(b["stock"])
    return out


def _herds(w, rec):
    cp = w.p["cattle"]
    f = w.p["farming"]
    year = w.year_days()
    winter = w.calendar()["season"] == "winter"
    slot = grow_days(year, "grain")
    for hid, h in sorted(w.s["herds"].items()):
        n = head(h)
        if n <= 0:
            continue
        node, pid = h["node"], h["parcel"]
        if node not in w.s["nodes"] or pid is None:                            # on a road (herds.py)
            continue
        par = w.s["parcels"][pid]
        need = float(n)
        got = 0.0
        ate = h.get("ate") or {}
        if ate.get("day") == w.d:                                              # what it ate and trampled in a crop (herds.trample)
            got += min(need, float(ate["q"]))
        g = par["res"].get("grass")
        if g and got < need:
            got += w.apply("draw", node, parcel=pid, key="grass", qty=round(min(need - got, max(0.0, g["S"] - 0.05 * g["K"])), 4))
        for cid in _fodder_stores(w, hid):                                     # then fodder from the holders' stores (D4-42)
            for item in ("hay", "straw"):
                if got + 1e-9 < need:
                    have = w.goods(cid).get(item, 0.0)
                    if have > 1e-9:
                        q = min(have, (need - got) / ITEMS[item]["fodder"])
                        got += w.apply("destroy", node, src=cid, item=item, qty=round(q, 4), why="fodder") * ITEMS[item]["fodder"]
        fed = got + 1e-6 >= 0.9 * need
        hungry = 0 if fed else int(h.get("hungry", 0)) + 1
        w.apply("set", node, ref=("herd", hid), field="hungry", value=hungry)
        milk = float(h.get("in_milk", 0.0))
        milk -= milk / max(1.0, float(cp["in_milk_share"]) * year)              # a cow is in milk 0.6 of the year after calving
        if hungry >= 2:
            milk *= float(cp["hungry_milk"])
            w.event(node, "herd", f"{h['name']} are hungry: ribs showing, lowing at the gate", about=[f"herd:{hid}"], salience=0.4,
                    tags=["animals", "food"])
        if hungry >= int(cp["starve_nights"]):
            role = next(r for r in ("young", "cows", "oxen", "bulls") if int(h.get(r, 0)) > 0)
            w.apply("set", node, ref=("herd", hid), field=role, value=int(h[role]) - 1)
            milk = min(milk, float(w.s["herds"][hid]["cows"]))
            w.event(node, "herd", f"a {ROLE_WORD[role][0]} of {h['name']} died of hunger in the night", about=[f"herd:{hid}"],
                    salience=0.6, tags=["animals", "death"])
            rec["herds"].append((hid, "starved", role))
        if fed and int(h.get("bulls", 0)) > 0 and int(h.get("cows", 0)) > 0:  # breeding where a bull is with the cows (D4-44)
            acc = float(h.get("births", 0.0)) + int(h["cows"]) * float(cp["births"]) * float(cp["survive"]) / year
            while acc >= 1.0:
                acc -= 1.0
                w.apply("set", node, ref=("herd", hid), field="young", value=int(w.s["herds"][hid].get("young", 0)) + 1)
                w.apply("set", node, ref=("herd", hid), field="last_calf", value=w.d + 1)
                milk = min(float(w.s["herds"][hid]["cows"]), milk + 1.0)
                w.event(node, "herd", f"a calf was born to {h['name']} on {par['name']}", about=[f"herd:{hid}"], salience=0.4,
                        tags=["animals"])
                rec["herds"].append((hid, "calf"))
            w.apply("set", node, ref=("herd", hid), field="births", value=round(acc, 4))
        w.apply("set", node, ref=("herd", hid), field="in_milk", value=round(max(0.0, milk), 4))
        d = par["res"].setdefault("dung", {"S": 0.0, "K": 1e9, "r": 0.0})     # dung where they stand
        d["S"] = round(d["S"] + n * float(cp["dung"]) / year, 4)
        if par["cover"] == "field" and not par.get("crop"):                    # a grazed fallow (D4-39)
            r, level = f["grazed"]
            dd = 1 - (1 - float(r)) ** (1 / slot)
            w.apply("set", node, ref=("parcel", pid), field="fertility",
                    value=round(par["fertility"] + dd * max(0.0, float(level) - par["fertility"]), 4))
        w.apply("set", node, ref=("herd", hid), field="count", value=head(w.s["herds"][hid]))
