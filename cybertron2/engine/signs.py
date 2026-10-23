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


# ---------------------------------------------------------------------- the sky and the season
SKY = [
    dict(when=lambda x: x.cold and x.first_cold, sense="touch", p=0.85, tags=["season", "shelter", "farming"],
         text=lambda x: "a hard frost lay on everything this morning"),
    dict(when=lambda x: x.cold and x.first_cold, sense="sight", p=0.4, tags=["season", "farming"],
         text=lambda x: "ice on the water butts and the puddles"),
    dict(when=lambda x: x.cold and not x.first_cold, sense="touch", p=0.5, tags=["season", "shelter"], text=lambda x: "it stayed bitterly cold"),
    dict(when=lambda x: x.cold and not x.first_cold, sense="sight", p=0.2, tags=["season", "timber"],
         text=lambda x: "everyone is burning more wood against the cold"),
    dict(when=lambda x: not x.cold, sense="sight", p=0.05, tags=["season"],
         text=lambda x: {"spring": "a mild day, showers on the wind", "summer": "a warm, settled day",
                         "autumn": "a cool day, the nights drawing in", "winter": "a grey, raw day"}[x.season]),
    dict(when=lambda x: x.left == 0, sense="sight", p=0.1, tags=["season"], text=lambda x: f"the last days of {x.season}: the light is changing"),
    dict(when=lambda x: x.left <= 1 and x.season == "autumn", sense="touch", p=0.3, tags=["season", "farming"], knack="sow",
         text=lambda x: "the nights are sharp: frost is not far off, and anything still growing will not see it through"),
    dict(when=lambda x: x.left <= 1 and x.season == "winter", sense="sight", p=0.2, tags=["season", "farming"], knack="sow",
         text=lambda x: "the days lengthen: soon the ground can be worked again"),
]

# ---------------------------------------------------------------------- what grows wild on a parcel (forage, game, wood, the seam)
def _bare(x, key) -> bool:
    """As bare as the gathering refusal finds it (knowledge.ready)."""
    r = x.p["res"].get(key)
    if not r or r["K"] <= 0:
        return False
    return r["S"] <= 0.5 if key == "wood" else r["S"] <= (x.here.p["refuge"] + 0.02) * r["K"]


def _thin(r, at=0.35, lo=0.1, hi=0.5) -> float:
    """The chance of noticing grows with how bare the place is (D4-50)."""
    return lo + (hi - lo) * max(0.0, min(1.0, (at - r) / at))


# `land` marks a sign that tells how bare a place is: the noticer remembers it against the place (D4-50); `eye` makes it depend on
# the person's eye for the land, which for some is none: they find out only by failing.
WILD = [
    dict(when=lambda x: _bare(x, "plants"), sense="sight", p=0.5, tags=["food"], eye=True, land=("wild food", "bare"),
         text=lambda x: f"{x.nm} is picked bare: nothing left worth gathering"),
    dict(when=lambda x: x.r("plants") is not None and x.r("plants") < 0.35 and not _bare(x, "plants"), sense="sight",
         p=lambda x: _thin(x.r("plants")), tags=["food"], eye=True, land=("wild food", "thin"),
         text=lambda x: f"{x.nm} has been picked over: little wild food left"),
    dict(when=lambda x: x.r("plants") is not None and x.r("plants") < 0.35, sense="sight", p=lambda x: _thin(x.r("plants"), lo=0.05, hi=0.3),
         tags=["food"], knack="forage", eye=True, land=("wild food", "thin"),
         text=lambda x: f"bare stems where the berries were in {x.nm}: it will take days to come back"),
    dict(when=lambda x: x.r("plants") is not None and x.r("plants") > 0.75, sense="sight", p=0.08, tags=["food"], land=("wild food", "good"),
         text=lambda x: f"{x.nm} is thick with berries, nuts and greens"),
    dict(when=lambda x: x.r("game") is not None and x.r("game") < 0.35, sense="sight", p=lambda x: _thin(x.r("game")),
         tags=["food", "hunting"], knack="hunt", eye=True, land=("game", "thin"),
         text=lambda x: f"few fresh tracks in {x.nm}: the game is thin"),
    dict(when=lambda x: x.r("game") is not None and x.r("game") < 0.2, sense="sound", p=lambda x: _thin(x.r("game"), at=0.2, lo=0.1, hi=0.4),
         tags=["food", "hunting"], eye=True, land=("game", "thin"),
         text=lambda x: f"{x.nm} is quiet: nothing moves at dusk"),
    dict(when=lambda x: x.r("game") is not None and x.r("game") > 0.75, sense="sight", p=0.08, tags=["food", "hunting"], knack="hunt",
         land=("game", "good"), text=lambda x: f"fresh deer slots and droppings along the rides of {x.nm}"),
    dict(when=lambda x: x.r("game") is not None and x.r("game") > 0.75, sense="sight", p=0.06, tags=["food", "hunting"],
         text=lambda x: f"a hare starts from the bracken in {x.nm}"),
    dict(when=lambda x: _bare(x, "wood"), sense="sight", p=0.6, tags=["timber"], eye=True, land=("timber", "bare"),
         text=lambda x: f"no standing timber left in {x.nm}: stumps and brush only"),
    dict(when=lambda x: x.r("wood") is not None and x.r("wood") < 0.35 and not _bare(x, "wood"), sense="sight", p=lambda x: _thin(x.r("wood")),
         tags=["timber"], eye=True, land=("timber", "thin"),
         text=lambda x: f"{x.nm} is thinned out: stumps where the big trees stood"),
    dict(when=lambda x: x.r("wood") is not None and x.r("wood") < 0.5 and not _bare(x, "wood"), sense="sight", p=0.15, tags=["timber"],
         knack="fell", land=("timber", "thin"), text=lambda x: f"the good straight trees in {x.nm} are gone; what is left is crooked and small"),
    dict(when=lambda x: x.r("seam") is not None and 0 < x.r("seam") < 0.35, sense="sight", p=0.25, tags=["mining"], knack="mine",
         text=lambda x: f"the seam at {x.nm} is nearly worked out"),
    dict(when=lambda x: x.r("seam") is not None and x.r("seam") >= 0.35, sense="sight", p=0.05, tags=["mining"],
         text=lambda x: f"a green-stained seam in {x.nm}"),
    dict(when=lambda x: "quarry" in x.p["res"], sense="sight", p=0.05, tags=["building"], text=lambda x: f"a face of good stone at {x.nm}"),
]


# ---------------------------------------------------------------------- a building
def _amt(q) -> str:
    return "none" if q < 0.05 else ("a little" if q < 1.5 else ("some" if q < 4 else ("plenty" if q < 10 else "a great deal")))


BUILDING = [
    dict(when=lambda x: x.b["condition"] == 2 and not x.camp, sense="sight", p=0.06, tags=["building"],
         text=lambda x: f"{x.nm} is sound"),
    dict(when=lambda x: x.b["condition"] == 1, sense="sight", p=0.35, tags=["building", "shelter"],
         text=lambda x: f"{x.nm} is in poor repair: the thatch slipping, a wall cracked"),
    dict(when=lambda x: x.b["condition"] == 1 and x.cold, sense="touch", p=0.3, tags=["shelter"],
         text=lambda x: f"a cold draught cuts through {x.nm}"),
    dict(when=lambda x: x.b["condition"] == 0, sense="sight", p=0.5, tags=["building", "shelter"], text=lambda x: f"{x.nm} is a ruin"),
    dict(when=lambda x: x.camp, sense="sight", p=0.2, tags=["shelter", "travel"],
         text=lambda x: f"{x.nm}: a lean-to of branches round a fire ring"),
    dict(when=lambda x: x.camp and x.b.get("lasts_until") is not None and x.b["lasts_until"] - x.day <= 2, sense="sight", p=0.3,
         tags=["shelter"], text=lambda x: f"{x.nm} is sagging: it will not stand many more nights"),
    dict(when=lambda x: x.fire_place and x.b["fire"], sense="sight", p=0.06, tags=["shelter"],
         text=lambda x: f"smoke from {x.nm}'s roof at dawn"),
    dict(when=lambda x: x.fire_place and x.b["fire"] and x.cold, sense="smell", p=0.1, tags=["shelter"],
         text=lambda x: f"wood smoke from {x.nm} on the cold air"),
    dict(when=lambda x: x.fire_place and not x.b["fire"] and x.was_cold and x.live, sense="sight", p=0.5, tags=["shelter", "danger"],
         text=lambda x: f"no smoke from {x.nm}'s roof after a cold night"),
    dict(when=lambda x: x.timber < 2 and x.live, sense="sight", p=0.3, tags=["timber", "shelter"],
         text=lambda x: f"the woodpile by {x.nm} is nearly gone"),
    dict(when=lambda x: x.timber >= 2, sense="sight", p=0.05, tags=["timber", "shelter"],
         text=lambda x: f"the woodpile by {x.nm}: {_amt(x.timber)}"),
    dict(when=lambda x: "bread" in x.made or "oven bread" in x.made, sense="smell", p=0.4, tags=["food"],
         text=lambda x: f"the smell of baking bread from {x.nm}"),
    dict(when=lambda x: {"grind", "mill", "water mill"} & x.made, sense="sound", p=0.3, tags=["food"],
         text=lambda x: f"the grinding of stones from {x.nm}"),
    dict(when=lambda x: {"smelt", "copper tool", "coin"} & x.made, sense="sound", p=0.45, tags=["craft", "smithing"],
         text=lambda x: f"hammering from {x.nm}"),
    dict(when=lambda x: {"smelt"} & x.made, sense="smell", p=0.3, tags=["craft", "mining"],
         text=lambda x: f"sharp fumes from {x.nm}: someone is smelting"),
    dict(when=lambda x: x.fits, sense="sight", p=0.05, tags=["building"], text=lambda x: f"{x.nm} has " + ", ".join(x.fits)),
    dict(when=lambda x: x.b["door"] == "barred", sense="sight", p=0.3, tags=["danger"], text=lambda x: f"{x.nm}'s door is barred"),
    dict(when=lambda x: x.b["door"] != "barred", sense="sight", p=0.05, tags=["food"], peek=True,
         text=lambda x: f"through {x.nm}'s open door: " + (", ".join(f"{_amt(q)} {i}" for i, q in sorted(x.stock.items())
                                                                    if q >= 0.5 and i != "timber") or "nothing much")),
    dict(when=lambda x: x.food_left < x.live_n and x.live, sense="sight", p=0.2, tags=["food"], knack=None,
         text=lambda x: f"the bins in {x.nm} look near empty"),
]

# ---------------------------------------------------------------------- a person
PERSON = [
    dict(when=lambda x: x.a["hunger"] == 0, sense="sight", p=0.08, tags=[], text=lambda x: f"{x.who} looks well enough fed"),
    dict(when=lambda x: x.a["hunger"] == -1, sense="sight", p=0.35, tags=["food"], text=lambda x: f"{x.who} looks drawn and hungry"),
    dict(when=lambda x: x.a["hunger"] == -1, sense="sound", p=0.15, tags=["food"], text=lambda x: f"{x.who} is short with everyone today"),
    dict(when=lambda x: x.a["hunger"] == -2, sense="sight", p=0.6, tags=["food", "danger"],
         text=lambda x: f"{x.who} is gaunt and unsteady on their feet"),
    dict(when=lambda x: x.a["hunger"] == -2, sense="sight", p=0.3, tags=["food"], text=lambda x: f"{x.who} sat down twice in the day's work"),
    dict(when=lambda x: x.a["wounded"], sense="sight", p=0.5, tags=["danger"], text=lambda x: f"{x.who} moves stiffly, bruised about the face"),
    dict(when=lambda x: x.gear, sense="sight", p=0.08, tags=["craft"],
         text=lambda x: f"{x.who} carries " + " and ".join(f"a {i}" for i in x.gear)),
    dict(when=lambda x: x.load, sense="sight", p=0.12, tags=["food"],
         text=lambda x: f"{x.who} has a load: " + ", ".join(f"{_amt(q)} {i}" for i, q in x.load)),
    dict(when=lambda x: x.travel_gear, sense="sight", p=0.25, tags=["travel"],
         text=lambda x: f"{x.who} has a {x.travel_gear} rolled on their back, as if for a journey"),
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
    x.r = lambda key: (p["res"][key]["S"] / p["res"][key]["K"]) if key in p["res"] and p["res"][key]["K"] > 0 else None
    x.dung = (p["res"].get("dung") or {}).get("S", 0.0)
    return x


def building_context(here, bid):
    from cybertron2.engine.data import FITTINGS
    b = here.buildings()[bid]
    st = here.stock(bid)
    live = [x for x in here.people() if bid in here.homes_here(x)]
    made = {e.get("tech") for e in here.events() if e.get("kind") == "make" and f"building:{bid}" in (e.get("about") or [])}
    x = SimpleNamespace(here=here, b=b, nm=b["name"], day=here.day, cold=here.cold(), stock=st, timber=st.get("timber", 0.0),
                        live=live, live_n=len(live), made=made, camp=b["structure"] == "camp",
                        was_cold=here.cold(here.day - 1 if here.day else 0),
                        fire_place=any(b["fittings"].get(f) for f in ("hearth", "fire ring")),
                        fits=[FITTINGS[f]["label"] for f in b["fittings"] if f in FITTINGS and f not in ("beds",)])
    from cybertron2.engine.data import ITEMS
    x.food_left = sum(q * ITEMS[i]["food"] for i, q in st.items() if i in ITEMS)
    return x


def person_context(here, who):
    from cybertron2.engine.data import ITEMS
    a = here.body(who)
    x = SimpleNamespace(who=who, a=a)
    x.gear = [i for i, q in a["carried"].items() if q >= 1 and ITEMS[i].get("seen") and not ITEMS[i].get("camp")]
    x.load = [(i, q) for i, q in a["carried"].items() if q >= 2 and ITEMS[i]["weight"] > 0]
    x.travel_gear = next((i for i, q in a["carried"].items() if q >= 1 and ITEMS[i].get("camp")), None)
    return x


def facts(here, add) -> None:
    """Add every sign whose condition holds, at its base chance, for each field, pasture and herd here."""
    names = {id(SKY): "sky", id(WILD): "wild", id(CROP): "crop", id(FIELD): "field", id(PASTURE): "pasture", id(HERD): "herd", id(BUILDING): "building", id(PERSON): "person"}

    def emit(rows, x, about, concerns=()):
        for i, row in enumerate(rows):
            try:
                ok = row["when"](x)
            except (KeyError, TypeError, ZeroDivisionError):
                ok = False
            if ok:
                kw = {"knack": row.get("knack"), "sign": f"{about[0]}#{names[id(rows)]}{i}"}
                for k in ("peek", "eye", "land"):
                    if row.get(k):
                        kw[k] = row[k]
                p = row["p"](x) if callable(row["p"]) else row["p"]
                add(about, row["text"](x), p, row.get("tags", []), row.get("sense", "sight"), concerns=list(concerns), **kw)
    cal = here.calendar()
    emit(SKY, SimpleNamespace(cold=here.cold(), first_cold=here.cold() and (here.day == 0 or not here.cold(here.day - 1)),
                              season=cal["season"], left=cal["left"]), ["sky"])
    for pid, p in here.parcels().items():
        x = context(here, pid)
        emit(WILD, x, [f"parcel:{pid}"])
        if p["cover"] == "field":
            if p.get("crop"):
                emit(CROP, x, [f"parcel:{pid}"])
            emit(FIELD, x, [f"parcel:{pid}"])
        if p["cover"] in ("pasture", "meadow") or (p["res"].get("dung") or {}).get("S", 0) > 5:
            emit(PASTURE, x, [f"parcel:{pid}"])
    for hid, h in here.herds().items():
        if FM.head(h) > 0:
            emit(HERD, context(here, h["parcel"], h), [f"herd:{hid}", f"parcel:{h['parcel']}"])
    for bid, b in here.buildings().items():
        if b.get("unfinished"):
            add([f"building:{bid}"], f"{b['name']} is half built", 0.3, ["building"])
            continue
        x = building_context(here, bid)
        emit(BUILDING, x, [f"building:{bid}"], concerns=x.live)
    for who in here.people():
        emit(PERSON, person_context(here, who), [f"person:{who}"], concerns=[who])


# =====================================================================================================================================
# Things at a spot, the road, traces, travellers far off, and the night (information/noticing.md; D2-85, D2-88, D2-97, D2-81).
# The same row shape, with two more fields:
#   reach: how the row is reached. "rule" (default): its p times the noticing rule's chance (things.chance: the thing's own
#          conspicuousness x the place's sight x presence x attention x the eye); "near": its p, only for one who worked at the spot
#          or searched it (a close look: what is in a pack, whose body it is); "node": its p, for anyone at the node (a smell).
#   knows: a technique; the row is read only by one who knows it (an expert's reading); `lay: tech` rows only by one who does not.
# A thing is known once any of its rows is noticed; what one remembers is the text one noticed (a glimpse or a close look).
# =====================================================================================================================================

THING = [
    # a body, fresh (the day of death)
    dict(when=lambda x: x.body == "fresh", sense="sight", p=1.0, tags=["death"], text=lambda x: f"someone lies still at {x.where}"),
    dict(when=lambda x: x.body == "fresh", sense="sight", p=1.0, reach="near", tags=["death"],
         text=lambda x: f"the body of {x.of} lies at {x.where}" + (f", with {x.goods_words} beside it" if x.goods_words else "")),
    # dead some days
    dict(when=lambda x: x.body == "days", sense="sight", p=1.0, tags=["death"], text=lambda x: f"a body lies at {x.where}, dead some days"),
    dict(when=lambda x: x.body == "days", sense="sight", p=1.0, reach="near", tags=["death"],
         text=lambda x: f"the body of {x.of}, dead some days, lies at {x.where}"),
    dict(when=lambda x: x.rot and x.body, sense="smell", p=0.3, reach="node", tags=["death", "danger"],
         text=lambda x: f"the smell of something dead hangs about the place"),
    dict(when=lambda x: x.rot and x.body, sense="smell", p=1.0, reach="near", tags=["death", "danger"],
         text=lambda x: f"the stink of a body rotting at {x.where}"),
    # bones
    dict(when=lambda x: x.body == "bones", sense="sight", p=1.0, tags=["death"], text=lambda x: f"bones lie at {x.where}"),
    # a grave
    dict(when=lambda x: x.grave, sense="sight", p=0.6, tags=["death"],
         text=lambda x: (f"a cairn of stones at {x.where}" if x.cairn else f"a fresh grave at {x.where}")),
    # goods in the open
    dict(when=lambda x: x.heap and not x.hidden and not x.body, sense="sight", p=1.0, tags=["food"],
         text=lambda x: f"a heap of something at {x.where}"),
    dict(when=lambda x: x.heap and not x.hidden and not x.body, sense="sight", p=1.0, reach="near", tags=["food"],
         text=lambda x: f"a heap of {x.goods_words} lies at {x.where}"),
    dict(when=lambda x: x.pack and not x.hidden and not x.body, sense="sight", p=1.0, tags=["food"],
         text=lambda x: f"a pack lies at {x.where}"),
    dict(when=lambda x: x.pack and not x.hidden and not x.body, sense="sight", p=1.0, reach="near", tags=["food"],
         text=lambda x: f"a pack lies at {x.where}, with {x.goods_words} in it"),
    dict(when=lambda x: x.at_door, sense="sight", p=0.8, reach="node", tags=["food"],
         text=lambda x: f"something has been left at the door of {x.door_name}"),
    dict(when=lambda x: x.rotting_food and not x.body, sense="smell", p=1.0, reach="near", tags=["food"],
         text=lambda x: f"the stink of meat gone bad at {x.where}"),
    # hidden
    dict(when=lambda x: x.hidden == "under brush", sense="sight", p=1.0, tags=["food"],
         text=lambda x: f"the brush at {x.where} looks heaped up, as if over something"),
    dict(when=lambda x: x.hidden == "under brush", sense="sight", p=1.0, reach="near", tags=["food"],
         text=lambda x: f"something hidden under brush at {x.where}: {x.goods_words}"),
    dict(when=lambda x: x.hidden == "buried" and not x.body, sense="sight", p=1.0, tags=["food"],
         text=lambda x: f"a patch of turned earth at {x.where}, as if something were buried there"),
]

ROAD = [
    # the day's weather on the road
    dict(when=lambda x: x.weather != "clear", sense="sight", p=0.9, tags=["season"], text=lambda x: x.weather_words),
    # landmarks, by their state
    dict(when=lambda x: "ford" in x.lm and not x.state.get("ford"), sense="sight", p=1.0, tags=["travel"], text=lambda x: "you passed a ford"),
    dict(when=lambda x: "bridge" in x.lm and not x.state.get("bridge"), sense="sight", p=1.0, tags=["travel"], text=lambda x: "you crossed a bridge"),
    dict(when=lambda x: "pass" in x.lm and not x.state.get("pass"), sense="sight", p=1.0, tags=["travel"], text=lambda x: "you went over a pass"),
    dict(when=lambda x: "narrows" in x.lm, sense="sight", p=1.0, tags=["travel"], text=lambda x: "the road ran through a narrows"),
    dict(when=lambda x: "spring" in x.lm, sense="sight", p=0.9, tags=["travel"], text=lambda x: "you drank at a spring by the road"),
]

TRACE = [
    dict(when=lambda x: x.kind == "tracks", sense="sight", p=1.0, tags=["travel"],
         text=lambda x: f"{x.many} tracks going toward {x.toward}, {x.when}"),
    dict(when=lambda x: x.kind == "ruts", sense="sight", p=1.0, tags=["travel"], text=lambda x: f"cart ruts going toward {x.toward}, {x.when}"),
    dict(when=lambda x: x.kind == "ashes", sense="sight", p=1.0, tags=["travel"], text=lambda x: f"the ashes of a fire by the road, {x.when}"),
]

TRAVELLER = [
    dict(when=lambda x: True, sense="sight", p=1.0, tags=["travel"],
         text=lambda x: f"{x.n} traveller{'s' if x.n > 1 else ''} on the road" + (" with a cart" if x.cart else "")),
]

NIGHT = [
    dict(when=lambda x: x.role == "watcher", sense="sight", p=1.0, tags=["danger"],
         text=lambda x: f"from your watch at {x.house}: a shape at the door in the dark, someone trying the bar"),
    dict(when=lambda x: x.role == "inside", sense="sound", p=1.0, tags=["danger"],
         text=lambda x: f"a crash at the door of {x.house}, where you sleep; someone is breaking in"),
    dict(when=lambda x: x.role == "neighbour", sense="sound", p=1.0, tags=["danger"],
         text=lambda x: f"a noise in the night from {x.house}: wood splitting, a muffled voice"),
]


# ---------------------------------------------------------------------- contexts (engine side: things, roads and nights)
def thing_context(w, c):
    from cybertron2.engine import environment as EV, things as TH
    from cybertron2.engine.data import ITEMS, THINGS
    st = TH.body_state(w, c)
    qty = sum(q * max(1, ITEMS.get(i, {}).get("weight", 1)) for i, q in c["goods"].items() if q > 1e-9)
    door = c.get("door")
    x = SimpleNamespace(c=c, kind=c["kind"], of=c.get("of"), where=TH.parcel_name(w, c), body=st,
                        grave=bool(c.get("body")) and c.get("buried") is not None, cairn=bool(c.get("cairn")),
                        hidden=c.get("hidden"), untaught=bool(c.get("untaught")), goods=dict(c["goods"]),
                        goods_words=TH.goods_words(c["goods"]), qty=qty, heap=qty >= float(THINGS["heap_min"]),
                        pack=0 < qty < float(THINGS["heap_min"]), rot=TH.rotting(w, c),
                        rotting_food=any(ITEMS.get(i, {}).get("rot") and q > 0.2 for i, q in c["goods"].items()),
                        at_door=bool(door) and qty > 0, door_name=w.s["buildings"][door]["name"] if door in w.s["buildings"] else "",
                        age=w.d - int(c.get("died", c.get("day", w.d))), on_road=c.get("node") not in w.s["nodes"],
                        weather=EV.weather(w), snow=EV.snow_lying(w), season=w.calendar()["season"], cold=w.cold(), day=w.d)
    return x


def road_context(w, name, t, pos):
    from cybertron2.engine import environment as EV, roads as RD
    from cybertron2.engine.data import WEATHER
    st = RD.stretch(w, t["road"], pos)
    lm = [l["kind"] for l in st["landmarks"]]
    state = {l["kind"]: RD.challenge(w, t["road"], pos, l) for l in st["landmarks"]}
    wx = EV.weather(w)
    return SimpleNamespace(name=name, terrain=st["terrain"] or "plain", lm=lm, state=state, weather=wx, weather_words=WEATHER[wx]["words"],
                           snow=EV.snow_lying(w), season=w.calendar()["season"], cold=w.cold(), day=w.d, toward=w.s["nodes"][t["to"]]["name"],
                           first_night=w.d == t["left"], cart=w.goods(w.hands(name)).get("handcart", 0) >= 1)


def trace_context(w, x):
    from cybertron2.engine import environment as EV
    age = w.d - x["day"]
    many = "a party's" if x["n"] > 2 else "a traveller's" if x["n"] == 1 else "two travellers'"
    return SimpleNamespace(kind=x["kind"], age=age, n=x["n"], toward=x["toward"], many=many, snow=EV.snow_lying(w), weather=EV.weather(w),
                           when="fresh" if age <= 0 else ("a day old" if age == 1 else f"{age} days old"))


def night_context(w, e, role):
    from cybertron2.engine import environment as EV
    b = w.s["buildings"][e["building"]]
    return SimpleNamespace(role=role, house=b["name"], structure=b["structure"], dog=bool(b["fittings"].get("dog")),
                           riders=bool(e.get("riders")), weather=EV.weather(w), cold=w.cold(), season=w.calendar()["season"])


# ---------------------------------------------------------------------- rolling a bundle for one observer
def readable(row, know) -> bool:
    """`knows`: only one who knows the technique reads the row; `lay`: only one who does not."""
    if row.get("knows") and row["knows"] not in know:
        return False
    if row.get("lay") and row["lay"] in know:
        return False
    return True


def true_rows(rows, x) -> list:
    out = []
    for i, row in enumerate(rows):
        try:
            ok = row["when"](x)
        except (KeyError, TypeError, ZeroDivisionError, AttributeError):
            ok = False
        if ok:
            out.append((i, row))
    return out


def roll(rows, x, rng, mult=1.0, know=(), near=False, at_node=True, least=False) -> list:
    """The texts of a bundle one observer notices: each true row it can read, by its reach, at its p times `mult` (the noticing rule's
    chance for "rule" rows), rolled on its own. With `least`, the likeliest true row if none came up (an event already detected)."""
    got, best = [], None
    for i, row in true_rows(rows, x):
        if not readable(row, know):
            continue
        reach = row.get("reach", "rule")
        p = row["p"](x) if callable(row["p"]) else row["p"]
        if reach == "near":
            p = p if near else 0.0
        elif reach == "rule":
            p = p * mult
        elif reach == "node" and not at_node:
            p = 0.0
        if best is None or p > best[0]:
            best = (p, row)
        if p > 0 and rng.random() < min(1.0, p):
            got.append(row["text"](x))
    if least and not got and best is not None:
        got.append(best[1]["text"](x))
    return list(dict.fromkeys(got))
