"""What the land, its crops and its beasts show (H-7, D4-6; information/perception.md): for each state, a bundle of possible signs.

Each sign is a row: the sense it reaches, its words, a base chance of being noticed, its tags, a condition on the state and on what
else is there (who worked the plot today, a herd near, the season, the cold), and a knack: the work whose practice makes one read it
(a farmer reads the soil, a herder reads hungry cattle). Every observer meets each sign on its own (perceive.evening): one may see
the rooks at the barley and miss the thin soil, another the reverse. New states add rows here, not code (D4-24).

A condition is a function of a context `x`: x.c (the crop, or None), x.p (the parcel), x.h (the herd), x.day, x.season, x.cold,
x.worked (parcels worked on today), x.herds_on(pid), x.adj_crop (a neighbouring parcel with a crop standing), and helpers below.
"""
from __future__ import annotations

from types import SimpleNamespace

from cybertron2.engine import farm as FM


def _k(n) -> str:
    return f"{n} day{'s' if n != 1 else ''}"


# ---------------------------------------------------------------------- crops in a field
CROP = [
    # growing
    dict(when=lambda x: x.growing and not x.failed, sense="sight", p=0.10, tags=["farming"],
         text=lambda x: f"the {x.c['kind']} in {x.nm} {x.be} up in green rows"),
    dict(when=lambda x: x.growing and not x.failed, sense="sight", p=0.12, tags=["farming", "harvest"], knack="reap",
         text=lambda x: f"you judge the {x.c['kind']} in {x.nm} will be fit to reap in about {_k(x.c['ripe_day'] - x.day)}"),
    dict(when=lambda x: x.growing and not x.failed and x.weeds and x.day - x.c["sown"] >= 2, sense="sight", p=0.2,
         tags=["farming"], knack="weed", text=lambda x: f"thistle and dock are coming up among the {x.c['kind']} in {x.nm}"),
    dict(when=lambda x: x.growing and not x.failed and not x.weeds, sense="sight", p=0.08, tags=["farming"],
         text=lambda x: f"{x.nm} is clean of weeds"),
    dict(when=lambda x: x.growing and not x.failed and x.c["broken"] >= 0.5 * x.c["area"], sense="sight", p=0.08,
         tags=["farming"], knack="sow", text=lambda x: f"the {x.c['kind']} in {x.nm} {x.stands} thick and even"),
    dict(when=lambda x: x.growing and not x.failed and not x.c.get("hardy") and x.frost_first, sense="sight", p=0.3,
         tags=["farming", "season", "food"], knack="sow",
         text=lambda x: f"the {x.c['kind']} in {x.nm} will not ripen before the frosts come"),
    dict(when=lambda x: x.growing and x.failed, sense="sight", p=0.6, tags=["farming", "food"],
         text=lambda x: f"the {x.c['kind']} in {x.nm} {x.be} withering, the leaves spotted and brown"),
    dict(when=lambda x: x.growing and x.failed and not x.cold, sense="smell", p=0.2, tags=["farming"],
         text=lambda x: f"a sour smell off {x.nm}"),
    # ripe
    dict(when=lambda x: x.ripe and not x.rotting, sense="sight", p=0.35, tags=["farming", "harvest", "food"],
         text=lambda x: f"the {x.c['kind']} in {x.nm} {x.stands} ripe and ready for the sickle"),
    dict(when=lambda x: x.ripe and not x.rotting and x.pid not in x.worked, sense="sound", p=0.3, tags=["farming", "harvest"],
         text=lambda x: f"rooks and pigeons are at the ripe {x.c['kind']} in {x.nm}, with nobody there to drive them off"),
    dict(when=lambda x: x.ripe and not x.rotting, sense="touch", p=0.2, tags=["farming", "harvest"], knack="reap",
         text=lambda x: f"the ears in {x.nm} rub out hard in the hand: the {x.c['kind']} {x.be} ready"),
    dict(when=lambda x: x.ripe and not x.rotting and x.window_left <= 0, sense="sight", p=0.5, tags=["farming", "harvest", "food"],
         knack="reap", text=lambda x: f"the {x.c['kind']} in {x.nm} cannot stand much longer: it must be cut tomorrow or lost"),
    dict(when=lambda x: x.c is not None and x.c.get("reaped") and x.c["area_left"] > 1e-6, sense="sight", p=0.25,
         tags=["farming", "harvest"], text=lambda x: f"sheaves stooked in {x.nm}, the rest of the {x.c['kind']} still standing"),
    # rotting
    dict(when=lambda x: x.rotting, sense="sight", p=0.6, tags=["farming", "harvest", "food"],
         text=lambda x: f"the {x.c['kind']} in {x.nm} {x.be} going over: ears shedding and rotting in the field"),
    dict(when=lambda x: x.rotting and not x.cold, sense="smell", p=0.3, tags=["farming", "food"],
         text=lambda x: f"a smell of wet rot from {x.nm}"),
    dict(when=lambda x: x.rotting, sense="sight", p=0.25, tags=["farming"],
         text=lambda x: f"half the {x.c['kind']} in {x.nm} lies flat, beaten down"),
]

# ---------------------------------------------------------------------- the ground of a field with no crop, its soil and its works
FIELD = [
    dict(when=lambda x: x.c is None and x.p.get("broken", 0) > 0.1, sense="sight", p=0.15, tags=["farming"],
         text=lambda x: f"{x.nm} is dug over, the soil turned dark and ready for seed"),
    dict(when=lambda x: x.c is None and x.p.get("broken", 0) <= 0.1 and x.p.get("last_crop"), sense="sight", p=0.06, tags=["farming"],
         text=lambda x: f"stubble in {x.nm}"),
    dict(when=lambda x: x.c is None and x.herds_on(x.pid), sense="sight", p=0.12, tags=["farming", "animals"],
         text=lambda x: f"the beasts are grazing the stubble in {x.nm}"),
    dict(when=lambda x: x.c is None and not x.p.get("last_crop") and x.p.get("broken", 0) <= 0.1, sense="sight", p=0.06,
         tags=["farming"], text=lambda x: f"{x.nm} lies fallow, rough with grass and weeds"),
    dict(when=lambda x: x.p["fertility"] >= 1.05, sense="touch", p=0.15, tags=["farming"], knack="sow",
         text=lambda x: f"the soil of {x.nm} crumbles dark and rich"),
    dict(when=lambda x: 0.55 <= x.p["fertility"] < 0.8, sense="sight", p=0.18, tags=["farming"], knack="sow",
         text=lambda x: f"the soil of {x.nm} is pale and thin: it has been cropped hard"),
    dict(when=lambda x: x.p["fertility"] < 0.55, sense="sight", p=0.3, tags=["farming", "food"], knack="sow",
         text=lambda x: f"the soil of {x.nm} is worn out: last year's crop came up sparse and yellow"),
    dict(when=lambda x: x.p.get("ground") == "wet" and x.works_done < 0.5, sense="sight", p=0.25, tags=["farming"],
         text=lambda x: f"water stands in the low corners of {x.nm}"),
    dict(when=lambda x: x.p.get("ground") == "wet" and x.works_done < 0.5 and x.season in ("autumn", "spring"), sense="touch",
         p=0.3, tags=["farming"], knack="sow", text=lambda x: f"the ground of {x.nm} is sodden underfoot: it wants draining"),
    dict(when=lambda x: x.p.get("ground") == "wet" and x.works_done >= 0.5, sense="sight", p=0.1, tags=["farming"],
         text=lambda x: f"{x.nm}'s ditches run full and the ground between them is firm"),
    dict(when=lambda x: x.p.get("ground") == "hill" and x.works_done < 0.5, sense="sight", p=0.2, tags=["farming"],
         text=lambda x: f"the soil of {x.nm} has washed down the slope, stones showing at the top"),
    dict(when=lambda x: x.p.get("ground") == "hill" and x.works_done >= 0.5, sense="sight", p=0.12, tags=["farming"],
         text=lambda x: f"stone terraces step up {x.nm}"),
    dict(when=lambda x: x.works_unkept, sense="sight", p=0.3, tags=["farming"], knack="sow",
         text=lambda x: f"the {'banks round' if x.p.get('ground') == 'wet' else 'terrace walls of'} {x.nm} are slumping: they want mending"),
    dict(when=lambda x: x.works_begun, sense="sight", p=0.25, tags=["farming"],
         text=lambda x: f"{'ditches' if x.p.get('ground') == 'wet' else 'terraces'} half made in {x.nm}"),
]

# ---------------------------------------------------------------------- grass and dung on a pasture or meadow
PASTURE = [
    dict(when=lambda x: x.grass is not None and x.grass < 0.25, sense="sight", p=0.3, tags=["animals", "food"],
         text=lambda x: f"{x.nm} is grazed bare, the earth showing through"),
    dict(when=lambda x: x.grass is not None and x.grass < 0.45 and x.herds_on(x.pid), sense="sight", p=0.25, tags=["animals"],
         knack="herd", text=lambda x: f"the grass on {x.nm} will not carry the beasts much longer"),
    dict(when=lambda x: x.grass is not None and x.grass > 0.8, sense="sight", p=0.06, tags=["animals"],
         text=lambda x: f"good grass on {x.nm}"),
    dict(when=lambda x: x.grass is not None and x.grass > 0.7 and x.season == "summer", sense="sight", p=0.15, tags=["animals"],
         knack="hay", text=lambda x: f"the grass on {x.nm} is long enough to cut for hay"),
    dict(when=lambda x: x.dung > 5, sense="sight", p=0.12, tags=["animals", "farming"],
         text=lambda x: f"dung lies thick where the beasts have been on {x.nm}"),
    dict(when=lambda x: x.dung > 5 and not x.cold, sense="smell", p=0.1, tags=["animals"],
         text=lambda x: f"the smell of dung from {x.nm}"),
]

# ---------------------------------------------------------------------- a herd
HERD = [
    dict(when=lambda x: True, sense="sight", p=0.15, tags=["animals"],
         text=lambda x: f"{x.h['name']} on {x.nm}: {FM.herd_words(x.h)}"),
    dict(when=lambda x: x.h.get("last_calf") is not None and x.day - x.h["last_calf"] <= 1, sense="sight", p=0.45, tags=["animals"],
         text=lambda x: f"a new calf on unsteady legs among {x.h['name']}"),
    dict(when=lambda x: x.h.get("hungry", 0) >= 1, sense="sound", p=0.3, tags=["animals", "food"],
         text=lambda x: f"{x.h['name']} lowing and restless"),
    dict(when=lambda x: x.h.get("hungry", 0) >= 2, sense="sight", p=0.45, tags=["animals", "food"], knack="herd",
         text=lambda x: f"ribs showing on {x.h['name']}: they are not getting enough to eat"),
    dict(when=lambda x: x.h.get("bulls", 0) > 0 and x.h.get("cows", 0) > 0, sense="sight", p=0.12, tags=["animals"], knack="herd",
         text=lambda x: f"the bull is running with the cows on {x.nm}"),
    dict(when=lambda x: x.h.get("bulls", 0) > 0 and x.h.get("cows", 0) == 0, sense="sight", p=0.15, tags=["animals"],
         text=lambda x: f"a bull kept on his own on {x.nm}"),
    dict(when=lambda x: x.h.get("in_milk", 0) >= 0.5, sense="sight", p=0.1, tags=["animals", "food"], knack="milk",
         text=lambda x: f"{max(1, round(x.h['in_milk']))} cow{'s' if round(x.h['in_milk']) > 1 else ''} of {x.h['name']} heavy with milk"),
    dict(when=lambda x: x.h.get("watched") != x.day and x.adj_crop, sense="sight", p=0.2, tags=["animals", "farming"],
         text=lambda x: f"nobody is watching {x.h['name']}, and only a broken hedge stands between them and {x.adj_crop}"),
]


def context(here, pid, h=None):
    p = here.parcels()[pid]
    c = p.get("crop")
    f = here.p["farming"]
    cal = here.calendar()
    seasons = ("spring", "summer", "autumn", "winter")
    x = SimpleNamespace(here=here, pid=pid, p=p, c=c, h=h, nm=p["name"], day=here.day, season=cal["season"], cold=here.cold())
    x.worked = {s.split(":", 1)[1] for e in here.events() if e.get("kind") == "work" for s in e.get("about") or [] if s.startswith("parcel:")}
    x.herds_on = lambda q: [k for k, g in here.herds().items() if g["parcel"] == q and FM.head(g) > 0]
    standing = [here.parcels()[q]["name"] for q in p["adj"] if (here.parcels()[q].get("crop") or {}).get("area_left", 0) > 1e-6]
    x.adj_crop = standing[0] if standing else None
    plural = bool(c) and str(c.get("kind", "")).endswith("s")
    x.be, x.stands = ("are", "stand") if plural else ("is", "stands")
    if c:
        x.growing = here.day < int(c["ripe_day"])
        x.ripe = not x.growing and c["area_left"] > 1e-6
        x.rotting = bool(c.get("rotting")) and c["area_left"] > 1e-6
        x.failed = bool(c.get("failed") and c.get("shown_failed"))
        x.weeds = FM.weed_gain(f, c.get("weeded", 0.0) / max(1e-9, c["area"])) < 0.2
        x.window_left = int(c["ripe_day"]) + int(c.get("window", 2)) - 1 - here.day
        left_in_season = cal["left"]
        winter_next = seasons[(seasons.index(cal["season"]) + 1) % 4] == "winter"
        x.frost_first = winter_next and int(c["ripe_day"]) - here.day > left_in_season
    else:
        x.growing = x.ripe = x.rotting = x.failed = x.weeds = x.frost_first = False
        x.window_left = 0
    wk = p.get("works") or {}
    x.works_done = min(1.0, float(wk.get("done", 0.0)) / max(1.0, float(p["size"]))) if wk.get("ground") == p.get("ground") else 0.0
    x.works_unkept = bool(wk) and x.works_done > 0 and cal["left"] <= 1 and wk.get("kept", 0.0) < 1.0
    x.works_begun = bool(wk) and 0.0 < x.works_done < 1.0
    g = p["res"].get("grass")
    x.grass = g["S"] / g["K"] if g and g["K"] > 0 else None
    x.dung = (p["res"].get("dung") or {}).get("S", 0.0)
    return x


def facts(here, add) -> None:
    """Add every sign whose condition holds, at its base chance, for each field, pasture and herd here."""
    def emit(rows, x, about):
        for i, row in enumerate(rows):
            try:
                ok = row["when"](x)
            except (KeyError, TypeError, ZeroDivisionError):
                ok = False
            if ok:
                add(about, row["text"](x), row["p"], row.get("tags", []), row.get("sense", "sight"), knack=row.get("knack"),
                    sign=f"{about[0]}#{rows is CROP and 'crop' or rows is FIELD and 'field' or rows is PASTURE and 'pasture' or 'herd'}{i}")
    for pid, p in here.parcels().items():
        x = context(here, pid)
        if p["cover"] == "field":
            if p.get("crop"):
                emit(CROP, x, [f"parcel:{pid}"])
            emit(FIELD, x, [f"parcel:{pid}"])
        if p["cover"] in ("pasture", "meadow") or (p["res"].get("dung") or {}).get("S", 0) > 5:
            emit(PASTURE, x, [f"parcel:{pid}"])
    for hid, h in here.herds().items():
        if FM.head(h) > 0:
            emit(HERD, context(here, h["parcel"], h), [f"herd:{hid}", f"parcel:{h['parcel']}"])
