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
    dict(when=lambda x: x.growing and not x.failed and x.progress < 0.25, sense="sight", p=0.08, tags=["farming"],
         text=lambda x: f"the {x.c['kind']} in {x.nm} {x.be} just through, a green haze on the soil"),
    dict(when=lambda x: x.growing and not x.failed and x.c.get("crop") == "legumes" and 0.35 <= x.progress < 0.75 and not x.cold,
         sense="sight", p=0.1, tags=["farming"], text=lambda x: f"the {x.c['kind']} in {x.nm} {x.be} in flower, bees working along the rows"),
    dict(when=lambda x: x.growing and not x.failed and x.c.get("crop") != "legumes" and x.progress >= 0.6, sense="sight", p=0.1,
         tags=["farming"], text=lambda x: f"the {x.c['kind']} in {x.nm} {x.stands} high, the ears filling"),
    dict(when=lambda x: x.growing and not x.failed and x.c.get("hardy") and x.cold, sense="sight", p=0.12, tags=["farming", "season"],
         text=lambda x: f"the {x.c['kind']} in {x.nm} {x.stands} green through the frost"),
    dict(when=lambda x: x.growing and x.c.get("crop") == x.p.get("last_crop"), sense="sight", p=0.1, tags=["farming"], knack="sow",
         text=lambda x: f"the {x.c['kind']} in {x.nm} follows the same crop last year: the ground tires of it, and it fails more often"),
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
         text=lambda x: (f"the pods in {x.nm} rattle dry in the hand: the {x.c['kind']} {x.be} ready" if x.c.get("crop") == "legumes"
                         else f"the ears in {x.nm} rub out hard in the hand: the {x.c['kind']} {x.be} ready")),
    dict(when=lambda x: x.ripe and not x.rotting and x.weather in ("rain", "heavy rain", "gale"), sense="sound", p=0.25,
         tags=["farming", "harvest"], text=lambda x: f"{'wind' if x.weather == 'gale' else 'rain'} beating on the ripe {x.c['kind']} in {x.nm}: "
                                                      "it wants cutting"),
    dict(when=lambda x: x.ripe and not x.rotting and x.window_left <= 0, sense="sight", p=0.5, tags=["farming", "harvest", "food"],
         knack="reap", text=lambda x: f"the {x.c['kind']} in {x.nm} cannot stand much longer: it must be cut tomorrow or lost"),
    dict(when=lambda x: x.c is not None and x.c.get("reaped") and x.c["area_left"] > 1e-6, sense="sight", p=0.25,
         tags=["farming", "harvest"], text=lambda x: f"sheaves stooked in {x.nm}, the rest of the {x.c['kind']} still standing"),
    # rotting
    dict(when=lambda x: x.rotting, sense="sight", p=0.6, tags=["farming", "harvest", "food"],
         text=lambda x: f"the {x.c['kind']} in {x.nm} {x.be} going over: "
                        + ("pods splitting" if x.c.get("crop") == "legumes" else "ears shedding") + " and rotting in the field"),
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
    dict(when=lambda x: x.p.get("ground") == "wet" and x.works_done < 0.5 and x.weather == "heavy rain", sense="sight", p=0.35,
         tags=["farming"], text=lambda x: f"{x.nm} is flooded in its low parts after the rain"),
    dict(when=lambda x: x.p.get("ground") == "hill" and x.works_done < 0.5 and x.weather == "heavy rain", sense="sight", p=0.3,
         tags=["farming"], text=lambda x: f"the rain is carrying the soil of {x.nm} down the slope in brown runnels"),
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
    dict(when=lambda x: x.grass is not None and x.grass < 0.6 and x.season == "winter", sense="sight", p=0.15,
         tags=["animals", "food", "season"], knack="herd",
         text=lambda x: f"the grass on {x.nm} hardly grows in winter: what is eaten now comes back slowly till spring"),
    dict(when=lambda x: x.grass is not None and x.grass > 0.6 and x.season == "spring" and not x.cold, sense="sight", p=0.08,
         tags=["animals"], text=lambda x: f"the grass on {x.nm} is coming on fast"),
    dict(when=lambda x: x.grass is not None and x.snow, sense="sight", p=0.1, tags=["animals", "season"],
         text=lambda x: f"snow lies on {x.nm}, trodden and dirtied where the beasts have been"),
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
         text=lambda x: f"{x.h['name']} lowing and restless: they want feeding"),
    dict(when=lambda x: x.h.get("hungry", 0) >= 2, sense="sight", p=0.45, tags=["animals", "food"], knack="herd",
         text=lambda x: f"ribs showing on {x.h['name']}: they are not getting enough to eat"),
    dict(when=lambda x: x.h.get("hungry", 0) >= 3, sense="sight", p=0.5, tags=["animals", "food", "danger"], knack="herd",
         text=lambda x: f"{x.h['name']} are failing: one will die soon if they are not fed"),
    dict(when=lambda x: x.h.get("bulls", 0) > 0 and x.h.get("cows", 0) > 0 and float(x.h.get("births", 0.0)) >= 0.75, sense="sight",
         p=0.2, tags=["animals"], knack="herd", text=lambda x: f"one of the cows of {x.h['name']} is heavy in calf and near her time"),
    dict(when=lambda x: x.h.get("young", 0) > 0 and x.season in ("spring", "summer") and not x.h.get("hungry"), sense="sight", p=0.06,
         tags=["animals"], text=lambda x: f"calves kicking up their heels among {x.h['name']}"),
    dict(when=lambda x: x.weather in ("gale", "heavy rain", "snow"), sense="sight", p=0.1, tags=["animals", "season"],
         text=lambda x: f"{x.h['name']} stand bunched with their backs to the weather"),
    dict(when=lambda x: x.h.get("bulls", 0) > 0 and x.h.get("cows", 0) > 0, sense="sight", p=0.12, tags=["animals"], knack="herd",
         text=lambda x: f"the bull is running with the cows on {x.nm}"),
    dict(when=lambda x: x.h.get("bulls", 0) > 0 and x.h.get("cows", 0) == 0, sense="sight", p=0.15, tags=["animals"],
         text=lambda x: f"a bull kept on his own on {x.nm}"),
    dict(when=lambda x: x.h.get("in_milk", 0) >= 0.5, sense="sight", p=0.1, tags=["animals", "food"], knack="milk",
         text=lambda x: f"{max(1, round(x.h['in_milk']))} cow{'s' if round(x.h['in_milk']) > 1 else ''} of {x.h['name']} heavy with milk"),
    dict(when=lambda x: x.h.get("watched") != x.day and x.adj_crop and not x.fenced, sense="sight", p=0.2, tags=["animals", "farming"],
         text=lambda x: f"nobody is watching {x.h['name']}, and only open ground lies between them and {x.adj_crop}"),
    dict(when=lambda x: x.h.get("watched") != x.day and x.adj_crop and x.fenced == "gappy", sense="sight", p=0.25, tags=["animals", "farming"],
         text=lambda x: f"nobody is watching {x.h['name']}, and the fence between them and {x.adj_crop} has gaps in it"),
]


# A field beasts have been in (D2-123): it shows for some days, read by the noticing rule (`own`), so those who work or pass there see
# it and those elsewhere mostly do not. Context: signs.context (x.trampled_days, x.trampled_qty, x.trampled_from).
TRAMPLED = [
    dict(when=lambda x: x.c and x.trampled_days is not None and x.trampled_days <= 3, own=0.6, sense="sight", p=1.0,
         tags=["animals", "farming", "food"], text=lambda x: f"hoof-marks and flattened {x.c['kind']} in {x.nm}: beasts have been in it"),
    dict(when=lambda x: x.c and x.trampled_days is not None and x.trampled_days <= 1 and x.trampled_qty >= 5, own=0.8, sense="sight",
         p=0.7, tags=["animals", "farming", "food"], knack="reap",
         text=lambda x: f"a good swathe of the {x.c['kind']} in {x.nm} is grazed off and trodden into the mud"),
    dict(when=lambda x: x.c and x.trampled_days is not None and x.trampled_days <= 2, own=0.5, sense="sight", p=0.6, tags=["animals"],
         knack="herd", text=lambda x: f"dung and the tracks of cattle in {x.nm}, leading back toward {x.trampled_from}"),
]


# ---------------------------------------------------------------------- herds that are out, fences and gates (livestock.md)
# Read by the noticing rule (information/noticing.md; D2-117, D2-130, D2-132): a row's `own` is its own conspicuousness; the chance is
# p x own x the parcel's visibility for the sense x where one was (worked, passed through 0.3, next door 0.1) x attention x the eye.
# `holders` rows are read only by those who hold the herd (their pasture empty: nobody tells them) or the parcel (a gate left open:
# they shut it). Context: herd_context / fence_context below.
ASTRAY = [
    dict(when=lambda x: x.in_crop and x.ripe, own=0.95, sense="sight", p=1.0, tags=["animals", "farming", "food", "harvest"],
         text=lambda x: f"{x.name} are in {x.nm}, eating and trampling the ripe {x.crop}"),
    dict(when=lambda x: x.in_crop and not x.ripe, own=0.95, sense="sight", p=1.0, tags=["animals", "farming", "food"],
         text=lambda x: f"{x.name} are in {x.nm}, trampling the young {x.crop}"),
    dict(when=lambda x: x.in_crop and x.trampled >= 1.0, own=0.8, sense="sight", p=0.6, tags=["animals", "farming"], knack="reap",
         text=lambda x: f"a swathe of {x.crop} flattened and grazed off in {x.nm}, hoof-marks deep in the soil"),
    dict(when=lambda x: not x.in_crop and x.nm_cover in ("pasture", "meadow"), own=0.95, sense="sight", p=1.0, tags=["animals"],
         text=lambda x: f"{x.name} have strayed onto {x.nm}, away from {x.home}"),
    dict(when=lambda x: not x.in_crop and x.nm_cover not in ("pasture", "meadow"), own=0.95, sense="sight", p=1.0, tags=["animals"],
         text=lambda x: f"{x.name} are wandering loose on {x.nm}"),
    dict(when=lambda x: True, own=0.6, sense="sound", p=0.5, tags=["animals"],
         text=lambda x: f"lowing and the crack of hedges from {x.nm}: beasts loose where they should not be"),
    dict(when=lambda x: x.hungry, own=0.6, sense="sound", p=0.5, tags=["animals", "food"], knack="herd",
         text=lambda x: f"{x.name} bawling and roaming on {x.nm}: hungry beasts looking for grazing"),
    dict(when=lambda x: x.whose, own=0.7, sense="sight", p=0.5, tags=["animals"], knack="herd",
         text=lambda x: f"you know those beasts on {x.nm}: {x.whose}"),
    dict(when=lambda x: x.strays, own=0.8, sense="sight", p=0.6, tags=["animals"],
         text=lambda x: f"a few head broken off from {x.base} are on {x.nm} on their own"),
    dict(when=lambda x: x.from_road, own=0.9, sense="sight", p=1.0, tags=["animals"],
         text=lambda x: f"beasts nobody here knows are on {x.nm}: {x.words}, come in off the road"),
]
EMPTY = [
    dict(when=lambda x: True, own=0.9, sense="sight", p=1.0, tags=["animals", "danger"], holders="herd",
         text=lambda x: f"{x.home} is empty: {x.name} are not there"),
    dict(when=lambda x: x.gap, own=0.6, sense="sight", p=0.6, tags=["animals"], holders="herd",
         text=lambda x: f"hoof-marks lead out through the gap in the fence round {x.home}"),
    dict(when=lambda x: x.gate_open, own=0.6, sense="sight", p=0.6, tags=["animals"], holders="herd",
         text=lambda x: f"the gate of {x.home} stands open and the beasts are gone"),
]
FENCE = [
    dict(when=lambda x: x.building, own=0.6, sense="sight", p=0.5, tags=["animals", "farming"],
         text=lambda x: f"stakes and {'stone' if x.kind == 'stone' else 'woven hazel'} going up round {x.nm}: {x.done}"),
    dict(when=lambda x: x.gate_open, own=0.6, sense="sight", p=1.0, tags=["animals"], gate=True,
         text=lambda x: f"the gate of {x.nm} is standing open"),
    dict(when=lambda x: x.gate_open and x.opened_by, own=0.3, sense="sight", p=0.3, tags=["animals"],
         text=lambda x: f"the gate of {x.nm} is propped open with a stone, as if on purpose"),
    dict(when=lambda x: x.whole and x.kind == "wood", own=0.3, sense="sight", p=0.08, tags=["animals"],
         text=lambda x: f"a sound wattle fence round {x.nm}"),
    dict(when=lambda x: x.whole and x.kind == "stone", own=0.4, sense="sight", p=0.08, tags=["animals", "building"],
         text=lambda x: f"a dry-stone wall round {x.nm}, its coping stones even"),
    dict(when=lambda x: x.gappy, own=0.5, sense="sight", p=0.5, tags=["animals"], knack="fence",
         text=lambda x: f"the {x.word} round {x.nm} has gaps in it: it wants mending"),
    dict(when=lambda x: x.gappy and x.kind == "wood", own=0.4, sense="sight", p=0.3, tags=["animals"],
         text=lambda x: f"the wattles round {x.nm} are sagging and the stakes rotting at the foot"),
    dict(when=lambda x: x.down, own=0.5, sense="sight", p=0.4, tags=["animals"],
         text=lambda x: f"the old {x.word} round {x.nm} is down in places: beasts could walk through it"),
    dict(when=lambda x: x.whole and x.herd_in and not x.gate_open, own=0.4, sense="sight", p=0.1, tags=["animals"],
         text=lambda x: f"{x.herd_in} safe behind the {x.word} round {x.nm}"),
]


# A hidden way found (D2-98; world/roads.md): the finder learns only that a way leaves there (D4-47). Context in perceive.evening:
# x.nm (the parcel), x.side, x.opened (the land felled or cleared), x.worn (others have used it), x.way (the road's own words).
WAY = [
    dict(when=lambda x: not x.opened and not x.worn, sense="sight", p=0.6, tags=["travel"],
         text=lambda x: f"a game trail leaves {x.nm} {x.side}, under the trees, going somewhere: {x.way}"),
    dict(when=lambda x: not x.opened and not x.worn, sense="sight", p=0.4, tags=["travel"],
         text=lambda x: f"broken twigs and an old blaze on a trunk at the edge of {x.nm}: a way out {x.side} that nobody here uses"),
    dict(when=lambda x: not x.opened and x.worn, sense="sight", p=0.8, tags=["travel"],
         text=lambda x: f"a path trodden through {x.nm} {x.side}, fresh footprints on it: someone has been using a way out of here"),
    dict(when=lambda x: x.opened, sense="sight", p=1.0, tags=["travel"],
         text=lambda x: f"with the cover gone from {x.nm}, an old way shows plain, leading off {x.side}: {x.way}"),
]


# A dead beast (D4-52): fit to eat a day, then stinking, then bones; on a road it may lie off the road out of sight (its own
# conspicuousness carries that). Context: carcass_context.
CARCASS = [
    dict(when=lambda x: x.fresh and not x.off_road, sense="sight", p=1.0, tags=["animals", "food"],
         text=lambda x: f"a dead {x.beast} lies {x.at}"),
    dict(when=lambda x: x.fresh and x.off_road, sense="sight", p=1.0, tags=["animals", "food"],
         text=lambda x: f"something dead lies in the cover off the road: a {x.beast}, by the shape of it"),
    dict(when=lambda x: x.fresh and x.meat, sense="sight", p=1.0, reach="near", tags=["animals", "food"],
         text=lambda x: f"{x.of} lies dead {x.at}, not long dead: the meat would still be good today"),
    dict(when=lambda x: x.fresh and x.starved, sense="sight", p=0.8, reach="near", tags=["animals", "food"], knack="herd",
         text=lambda x: f"the dead {x.beast} {x.at} is all hide and bone: it starved, and there is little meat on it"),
    dict(when=lambda x: x.fresh and not x.starved, sense="sight", p=0.5, reach="near", tags=["animals"], knack="herd",
         text=lambda x: f"no mark on the dead {x.beast} {x.at}: it went down where it stood"),
    dict(when=lambda x: (x.fresh or x.rotten) and x.weather != "fog", sense="sight", p=0.5, tags=["animals"],
         text=lambda x: f"crows going down {x.at}, where something lies dead"),
    dict(when=lambda x: x.rotten and x.warm, sense="smell", p=0.6, reach="node", tags=["animals", "danger"],
         text=lambda x: f"the stink of a dead beast from {'the road' if x.on_road else x.where}"),
    dict(when=lambda x: x.rotten, sense="sight", p=1.0, reach="near", tags=["animals", "food"],
         text=lambda x: f"the dead {x.beast} {x.at} is bloated and gone off: past eating" + ("; the hide could still be taken" if x.hide else "")),
    dict(when=lambda x: x.rotten and x.dogs, sense="sight", p=0.3, reach="node", tags=["animals"],
         text=lambda x: f"the dogs keep going off to {x.where}, where a dead beast lies"),
    dict(when=lambda x: x.bones, sense="sight", p=1.0, tags=["animals"], text=lambda x: f"the bones of a {x.beast} {x.at}, picked clean"),
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
    dict(when=lambda x: not x.cold and x.weather == "clear", sense="sight", p=0.05, tags=["season"],
         text=lambda x: {"spring": "a mild, bright day", "summer": "a warm, settled day",
                         "autumn": "a cool, bright day, the nights drawing in", "winter": "a still, grey day"}[x.season]),
    # the day's weather and the days before it (environment.py)
    dict(when=lambda x: x.weather == "heavy rain" and x.water, sense="sight", p=0.3, tags=["season", "travel"],
         text=lambda x: f"{x.water} is up and running brown"),
    dict(when=lambda x: x.since_heavy == 1 and x.weather != "heavy rain" and x.water, sense="sight", p=0.2, tags=["season", "travel"],
         text=lambda x: f"{x.water} is still high from yesterday's rain"),
    dict(when=lambda x: x.weather == "rain" and x.season == "summer", sense="smell", p=0.08, tags=["season"],
         text=lambda x: "warm rain, and the smell of wet earth everywhere"),
    dict(when=lambda x: x.weather in ("rain", "heavy rain") and x.dry_before >= 5, sense="sight", p=0.3, tags=["season", "farming"],
         text=lambda x: "rain at last, after the dry days"),
    dict(when=lambda x: x.weather == "clear" and x.dry_before >= 6 and x.season in ("spring", "summer"), sense="touch", p=0.15,
         tags=["season", "farming"], text=lambda x: "no rain for days: the ground is hard and the dust rises"),
    dict(when=lambda x: x.weather in ("rain", "heavy rain") and x.wet_days >= 4, sense="touch", p=0.2, tags=["season"],
         text=lambda x: "it has rained for days: everything is damp, the paths are mud"),
    dict(when=lambda x: x.weather == "gale", sense="sound", p=0.2, tags=["season", "shelter"],
         text=lambda x: "the wind is loud in the thatch all day, and the smoke blows flat"),
    dict(when=lambda x: x.weather == "fog", sense="sight", p=0.15, tags=["season"],
         text=lambda x: "fog so thick the far houses are only shapes"),
    dict(when=lambda x: x.weather == "snow", sense="sight", p=0.2, tags=["season"], text=lambda x: "snow falling, the roofs whitening"),
    dict(when=lambda x: x.snow and x.weather != "snow" and x.cold, sense="sight", p=0.15, tags=["season"],
         text=lambda x: "snow lies over everything, trodden grey about the doors"),
    dict(when=lambda x: x.snow and not x.cold, sense="touch", p=0.25, tags=["season"], text=lambda x: "the snow is going to slush underfoot"),
    # tomorrow's weather, for one who reads the sky (it is drawn ahead: environment.weather)
    dict(when=lambda x: x.tomorrow in ("rain", "heavy rain") and x.weather not in ("rain", "heavy rain"), sense="sight", p=0.12,
         tags=["season", "farming"], knack="sow", text=lambda x: "the wind has backed and the cloud is thickening: rain tomorrow, likely"),
    dict(when=lambda x: x.tomorrow == "snow" and x.weather != "snow", sense="sight", p=0.12, tags=["season", "farming"], knack="sow",
         text=lambda x: "a heavy, yellow-grey sky: snow before long"),
    dict(when=lambda x: x.tomorrow == "gale" and x.weather != "gale", sense="sight", p=0.12, tags=["season", "shelter"], knack="sow",
         text=lambda x: "high cloud streaming fast and the wind getting up: a gale coming"),
    dict(when=lambda x: x.tomorrow == "clear" and x.weather in ("rain", "heavy rain", "fog", "snow"), sense="sight", p=0.08,
         tags=["season"], knack="sow", text=lambda x: "the cloud is breaking in the west: it should clear tomorrow"),
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
         text=lambda x: {"spring": f"new greens and shoots thick in {x.nm}", "summer": f"{x.nm} is thick with greens, the berries ripening",
                         "autumn": f"{x.nm} is thick with nuts and blackberries",
                         "winter": f"roots and late greens still to be had in {x.nm}"}[x.season]),
    dict(when=lambda x: x.r("plants") is not None and x.r("plants") < 0.35 and x.season == "winter", sense="sight", p=0.15, tags=["food"],
         knack="forage", land=("wild food", "thin"), text=lambda x: f"what has been picked in {x.nm} will come back slowly till spring"),
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
    dict(when=lambda x: x.r("game") is not None and x.r("game") > 0.5 and x.snow, sense="sight", p=0.15, tags=["food", "hunting"],
         knack="hunt", land=("game", "good"), text=lambda x: f"deer slots plain in the snow along the rides of {x.nm}"),
    dict(when=lambda x: x.r("game") is not None and x.r("game") < 0.2 and x.snow, sense="sight", p=0.3, tags=["food", "hunting"], eye=True,
         land=("game", "thin"), text=lambda x: f"the snow in {x.nm} lies unmarked: nothing has moved there"),
    dict(when=lambda x: x.r("game") is not None and x.r("game") < 0.15, sense="sight", p=0.2, tags=["food", "hunting"], knack="hunt",
         eye=True, land=("game", "thin"), text=lambda x: f"{x.nm} is hunted out: what game is left there will not breed back"),
    dict(when=lambda x: x.r("game") is not None and x.r("game") > 0.75, sense="sound", p=0.06, tags=["food", "hunting"],
         text=lambda x: f"something heavy moving in the undergrowth of {x.nm} at dusk"),
    dict(when=lambda x: _bare(x, "wood"), sense="sight", p=0.6, tags=["timber"], eye=True, land=("timber", "bare"),
         text=lambda x: f"no standing timber left in {x.nm}: stumps and brush only"),
    dict(when=lambda x: x.r("wood") is not None and x.r("wood") < 0.35 and not _bare(x, "wood"), sense="sight", p=lambda x: _thin(x.r("wood")),
         tags=["timber"], eye=True, land=("timber", "thin"),
         text=lambda x: f"{x.nm} is thinned out: stumps where the big trees stood"),
    dict(when=lambda x: x.r("wood") is not None and x.r("wood") < 0.5 and not _bare(x, "wood"), sense="sight", p=0.15, tags=["timber"],
         knack="fell", land=("timber", "thin"), text=lambda x: f"the good straight trees in {x.nm} are gone; what is left is crooked and small"),
    dict(when=lambda x: x.r("wood") is not None and x.r("wood") > 0.75, sense="sight", p=0.06, tags=["timber"], knack="fell",
         land=("timber", "good"), text=lambda x: f"tall, straight timber standing in {x.nm}"),
    dict(when=lambda x: x.r("wood") is not None and x.r("wood") > 0.3 and x.weather == "gale", sense="sound", p=0.15, tags=["timber"],
         text=lambda x: f"the trees of {x.nm} roar and creak in the gale"),
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
    dict(when=lambda x: x.b["condition"] == 1 and not x.camp and x.weather in ("rain", "heavy rain"), sense="sight", p=0.35,
         tags=["shelter", "building"], text=lambda x: f"rain coming in through {x.nm}'s roof, puddles on the floor"),
    dict(when=lambda x: x.b["condition"] == 1 and not x.camp and x.weather == "gale", sense="sound", p=0.35, tags=["shelter", "building"],
         text=lambda x: f"the gale tearing at {x.nm}'s loose thatch"),
    dict(when=lambda x: x.b["condition"] == 0, sense="sight", p=0.5, tags=["building", "shelter"], text=lambda x: f"{x.nm} is a ruin"),
    dict(when=lambda x: x.b["condition"] == 0 and x.snow, sense="sight", p=0.3, tags=["building", "shelter"],
         text=lambda x: f"snow drifted in through {x.nm}'s broken walls"),
    dict(when=lambda x: x.mended, sense="sight", p=0.3, tags=["building"],
         text=lambda x: f"fresh timber in {x.nm}'s walls: someone has been mending it"),
    dict(when=lambda x: x.camp, sense="sight", p=0.2, tags=["shelter", "travel"],
         text=lambda x: f"{x.nm}: a lean-to of branches round a fire ring"),
    dict(when=lambda x: x.camp and x.b.get("lasts_until") is not None and x.b["lasts_until"] - x.day <= 2, sense="sight", p=0.3,
         tags=["shelter"], text=lambda x: f"{x.nm} is sagging: it will not stand many more nights"),
    dict(when=lambda x: x.fire_place and x.b["fire"], sense="sight", p=0.06, tags=["shelter"],
         text=lambda x: f"smoke from {x.nm}'s roof at dawn"),
    dict(when=lambda x: x.fire_place and x.b["fire"] and x.weather == "fog", sense="sight", p=0.1, tags=["shelter"],
         text=lambda x: f"smoke from {x.nm} hangs low in the fog"),
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
    dict(when=lambda x: "water mill" in x.made, sense="sound", p=0.4, tags=["food"], text=lambda x: f"the creak and splash of the wheel at {x.nm}"),
    dict(when=lambda x: "dry meat" in x.made, sense="smell", p=0.3, tags=["food"], text=lambda x: f"the smell of meat drying in smoke at {x.nm}"),
    dict(when=lambda x: "cheese" in x.made, sense="smell", p=0.25, tags=["food", "animals"],
         text=lambda x: f"the sour smell of cheese-making from {x.nm}"),
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
    dict(when=lambda x: x.a["wounded"], sense="sight", p=0.2, tags=["danger"], text=lambda x: f"{x.who} winces at every lift and bend"),
    dict(when=lambda x: x.bereaved, sense="sight", p=0.2, tags=["death"],
         text=lambda x: f"{x.who} goes about grey-faced and silent since the death in their house"),
    dict(when=lambda x: x.bereaved, sense="sound", p=0.15, tags=["death"], text=lambda x: f"{x.who} was heard weeping"),
    dict(when=lambda x: x.stage == "elder" and x.cold, sense="sight", p=0.1, tags=["season"],
         text=lambda x: f"{x.who} is slow and stiff in the cold"),
    dict(when=lambda x: x.weapon, sense="sight", p=0.06, tags=["danger", "weapons"], text=lambda x: f"{x.who} goes about with a club or a spear"),
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
    from cybertron2.engine import environment as EV
    x = SimpleNamespace(here=here, pid=pid, p=p, c=c, h=h, nm=p["name"], day=here.day, season=cal["season"], cold=here.cold(),
                        weather=EV.weather(here._w), snow=EV.snow_lying(here._w))
    x.worked = {s.split(":", 1)[1] for e in here.events() if e.get("kind") == "work" for s in e.get("about") or [] if s.startswith("parcel:")}
    x.herds_on = lambda q: [k for k, g in here.herds().items() if g["parcel"] == q and FM.head(g) > 0]
    standing = [here.parcels()[q]["name"] for q in p["adj"] if (here.parcels()[q].get("crop") or {}).get("area_left", 0) > 1e-6]
    x.adj_crop = standing[0] if standing else None
    fc = p.get("fence") or {}                                                  # the parcel's own fence (livestock.md, D2-130)
    x.fenced = None if not fc.get("built") or int(fc.get("level", 0)) <= 0 or fc.get("gate") == "open" else (
        "whole" if int(fc["level"]) >= 2 else "gappy")
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
        x.progress = (here.day - int(c.get("sown", here.day))) / max(1, int(c["ripe_day"]) - int(c.get("sown", here.day)))
        tr = c.get("trampled") or {}
        x.trampled_days = here.day - int(tr["day"]) if tr.get("day") is not None else None
        x.trampled_qty = float(tr.get("qty", 0.0))
        hh = here.herds().get(tr.get("by")) or {}
        x.trampled_from = here.parcels().get(hh.get("home"), {}).get("name", "the pastures")
    else:
        x.trampled_days, x.trampled_qty, x.trampled_from = None, 0.0, ""
        x.growing = x.ripe = x.rotting = x.failed = x.weeds = x.frost_first = False
        x.window_left = 0
        x.progress = 0.0
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
    from cybertron2.engine import environment as EV
    mended = any(e.get("kind") == "work" and e.get("tech") == "repair" and f"building:{bid}" in (e.get("about") or []) for e in here.events())
    x = SimpleNamespace(here=here, b=b, nm=b["name"], day=here.day, cold=here.cold(), stock=st, timber=st.get("timber", 0.0),
                        weather=EV.weather(here._w), snow=EV.snow_lying(here._w), mended=mended,
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
    w = here._w
    hh = w.household_of(who)
    bereaved = bool(hh) and any(not q["alive"] and q.get("died") is not None and here.day - int(q["died"]) <= 5 and n != who
                                and n in w.s["institutions"][hh]["members"] for n, q in w.s["people"].items())
    x = SimpleNamespace(who=who, a=a, stage=w.s["people"][who].get("stage", "adult"), cold=here.cold(), bereaved=bereaved,
                        weapon=bool(w.weapon(who)))
    x.gear = [i for i, q in a["carried"].items() if q >= 1 and ITEMS[i].get("seen") and not ITEMS[i].get("camp")]
    x.load = [(i, q) for i, q in a["carried"].items() if q >= 2 and ITEMS[i]["weight"] > 0]
    x.travel_gear = next((i for i, q in a["carried"].items() if q >= 1 and ITEMS[i].get("camp")), None)
    return x


def sky_context(here):
    """The sky over a node: the cold and the season, today's weather and the days before it, tomorrow's (for one who reads the sky),
    and the water and wood here that show it."""
    from cybertron2.engine import environment as EV
    w, d = here._w, here.day
    cal = here.calendar()
    dry = 0
    for k in range(d - 1, max(-1, d - 11), -1):
        if EV.wet(w, k):
            break
        dry += 1
    names = lambda cover: next((p["name"] for p in here.parcels().values() if p["cover"] == cover), None)   # noqa: E731
    return SimpleNamespace(cold=here.cold(), first_cold=here.cold() and (d == 0 or not here.cold(d - 1)), season=cal["season"], left=cal["left"],
                           weather=EV.weather(w), snow=EV.snow_lying(w), since_heavy=EV.since_heavy_rain(w), tomorrow=EV.weather(w, d + 1),
                           dry_before=dry if d >= 5 else 0, wet_days=sum(1 for k in range(max(0, d - 4), d + 1) if EV.wet(w, k)),
                           water=names("water"), wood=names("forest"))


def _herds_out(here, add) -> None:
    """Herds off their home ground and empty home pastures, fences and gates: by the noticing rule (D2-117, D2-130, D2-132)."""
    w = here._w
    for hid, h in here.herds().items():
        if FM.head(h) <= 0 or h.get("parcel") is None:
            continue
        if h["parcel"] != h.get("home"):
            x = herd_context(w, hid)
            spot_rows(here, ASTRAY, x, [f"herd:{hid}", f"parcel:{h['parcel']}"], here.node, h["parcel"], add)
    for hid, h in w.s["herds"].items():                                         # home pastures of herds that are away (or lost)
        if FM.head(h) <= 0 or h.get("home") not in here.parcels() or h.get("parcel") == h.get("home"):
            continue
        holders = [cl["claimant"] for cl in w.claims_on(("herd", hid))]
        people = sorted({m for x in holders for m in ([x] if x in w.s["people"] else w.members(x) if x in w.s["institutions"] else [])})
        spot_rows(here, EMPTY, herd_context(w, hid), [f"parcel:{h['home']}"], here.node, h["home"], add, only=people, missing=hid)
    for pid, p in here.parcels().items():
        if p.get("fence"):
            spot_rows(here, FENCE, fence_context(w, pid), [f"parcel:{pid}"], here.node, pid, add)
        if (p.get("crop") or {}).get("trampled"):
            spot_rows(here, TRAMPLED, context(here, pid), [f"parcel:{pid}"], here.node, pid, add)


def facts(here, add) -> None:
    """Add every sign whose condition holds, for each field, pasture, herd, building, person and the sky here. Every sign is read by
    the one noticing rule (information/noticing.md, D4-53): each carries its spot (a parcel; the people inside a house or a household,
    who are always there; the sky, open to everyone at the node) and its own conspicuousness (`own`, 1 unless a row sets it)."""
    from cybertron2.engine import things as TH
    w = here._w
    names = {id(SKY): "sky", id(WILD): "wild", id(CROP): "crop", id(FIELD): "field", id(PASTURE): "pasture", id(HERD): "herd", id(BUILDING): "building", id(PERSON): "person"}

    def emit(rows, x, about, parcel=None, inside=(), everyone=False, concerns=()):
        for i, row in enumerate(rows):
            try:
                ok = row["when"](x)
            except (KeyError, TypeError, ZeroDivisionError):
                ok = False
            if ok:
                kw = {"knack": row.get("knack"), "sign": f"{about[0]}#{names[id(rows)]}{i}",
                      "spot": {"node": here.node, "parcel": parcel, "own": float(row.get("own", 1.0)), "inside": list(inside),
                               "everyone": everyone}}
                for k in ("peek", "eye", "land", "knows", "lay"):
                    if row.get(k):
                        kw[k] = row[k]
                p = row["p"](x) if callable(row["p"]) else row["p"]
                add(about, row["text"](x), p, row.get("tags", []), row.get("sense", "sight"), concerns=list(concerns), **kw)
    emit(SKY, sky_context(here), ["sky"], everyone=True)
    for pid, p in here.parcels().items():
        x = context(here, pid)
        emit(WILD, x, [f"parcel:{pid}"], parcel=pid)
        if p["cover"] == "field":
            if p.get("crop"):
                emit(CROP, x, [f"parcel:{pid}"], parcel=pid)
            emit(FIELD, x, [f"parcel:{pid}"], parcel=pid)
        if p["cover"] in ("pasture", "meadow") or (p["res"].get("dung") or {}).get("S", 0) > 5:
            emit(PASTURE, x, [f"parcel:{pid}"], parcel=pid)
    for hid, h in here.herds().items():
        if FM.head(h) > 0:
            emit(HERD, context(here, h["parcel"], h), [f"herd:{hid}", f"parcel:{h['parcel']}"], parcel=h["parcel"])
    _herds_out(here, add)
    for bid, b in here.buildings().items():
        live = [x for x in here.people() if bid in here.homes_here(x)]
        if b.get("unfinished"):
            add([f"building:{bid}"], f"{b['name']} is half built", 0.3, ["building"],
                spot={"node": here.node, "parcel": b["parcel"], "own": 0.8, "inside": [], "everyone": False})
            continue
        x = building_context(here, bid)
        emit(BUILDING, x, [f"building:{bid}"], parcel=b["parcel"], inside=live, concerns=x.live)
    for who in here.people():                                                     # where they were today; their household sees them
        hh = w.household_of(who)
        home = [m for m in here.people() if hh and w.household_of(m) == hh]
        emit(PERSON, person_context(here, who), [f"person:{who}"], parcel=TH.spot_of(w, who), inside=home, concerns=[who])


# =====================================================================================================================================
# Things at a spot, the road, traces, travellers far off, and the night (information/noticing.md; D2-85, D2-88, D2-97, D2-81).
# The same row shape, with two more fields:
#   reach: how the row is reached. "rule" (default): its p times the noticing rule's chance (things.chance: the thing's own
#          conspicuousness x the place's sight x presence x attention x the eye); "near": its p, only for one who worked at the spot
#          or searched it (a close look: what is in a pack, whose body it is); "node": its p, for anyone at the node (a smell).
#   knows: a technique; the row is read only by one who knows it (an expert's reading); `lay: tech` rows only by one who does not.
# A thing is known once any of its rows is noticed; what one remembers is the text one noticed (a glimpse or a close look).
# =====================================================================================================================================

NUM = ("no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve")


def _num(n) -> str:
    return NUM[n] if 0 <= n < len(NUM) else "a dozen or more"


def _folk(n) -> str:
    return "one person" if n == 1 else f"{_num(n)} people"


def _old(age) -> str:
    """How old a trace or a thing looks to one who can read it."""
    return "fresh" if age <= 0 else ("a day old" if age == 1 else (f"{_num(age)} days old" if age <= 10 else "a month or more old"))


# A thing at a spot: a body (fresh, dead some days, bones; buried), goods in the open (a heap, a bundle, at a door), goods hidden
# (under brush, buried). Glimpses never name what a cache holds or whose a body is: that is for a close look (reach "near"), and a
# close look at a hidden thing is as unlikely as its hiding makes it (perceive: a near row's p times things.hidden_factor).
_OPEN = lambda x: not x.hidden and not x.body                                          # noqa: E731
THING = [
    # ---- a body, fresh (the day of death)
    dict(when=lambda x: x.body == "fresh", sense="sight", p=1.0, tags=["death"], text=lambda x: f"someone lies still {x.at}"),
    dict(when=lambda x: x.body == "fresh" and x.cause == "attack" and x.outside, sense="sight", p=0.4, tags=["death", "danger"],
         text=lambda x: f"someone lies still {x.at}, the ground about them trampled and dark with blood"),
    dict(when=lambda x: x.body == "fresh", sense="sight", p=1.0, reach="near", tags=["death"],
         text=lambda x: f"the body of {x.of} lies {x.at}" + (f", with {x.goods_words} beside it" if x.goods_words else "")),
    dict(when=lambda x: x.body == "fresh" and x.cause == "attack" and not x.cold, sense="touch", p=0.6, reach="near", tags=["death"],
         text=lambda x: f"{x.of}'s body {x.at} is not yet cold"),
    # ---- dead some days
    dict(when=lambda x: x.body == "days", sense="sight", p=1.0, tags=["death"], text=lambda x: f"a body lies {x.at}, dead some days"),
    dict(when=lambda x: x.body == "days", sense="sight", p=1.0, reach="near", tags=["death"],
         text=lambda x: f"the body of {x.of}, dead some days, lies {x.at}" + (f", with {x.goods_words} beside it" if x.goods_words else "")),
    dict(when=lambda x: x.body == "days" and x.outside and not x.on_road and x.weather != "fog", sense="sight", p=0.25, reach="node",
         tags=["death"], text=lambda x: f"crows circling and dropping {x.at}, as they do over something dead"),
    dict(when=lambda x: x.body == "days" and x.on_road and x.weather != "fog", sense="sight", p=0.7, tags=["death"],
         text=lambda x: "crows rise from something lying by the road"),
    dict(when=lambda x: x.body in ("fresh", "days") and x.outside and x.snowed_over, sense="sight", p=0.6, tags=["death"],
         text=lambda x: f"a long shape under the snow {x.at}"),
    # ---- how they died, for one who looks close
    dict(when=lambda x: x.body in ("fresh", "days") and x.cause == "attack", sense="sight", p=0.8, reach="near", tags=["death", "danger"],
         text=lambda x: f"{x.of}, lying {x.at}, was beaten to death: the head broken, blood dried on the face"),
    dict(when=lambda x: x.body in ("fresh", "days") and x.cause == "starvation", sense="sight", p=0.8, reach="near", tags=["death", "food"],
         text=lambda x: f"{x.of}, lying {x.at}, is all skin and bone: hunger did this"),
    dict(when=lambda x: x.body in ("fresh", "days") and "cold" in x.cause, sense="sight", p=0.8, reach="near", tags=["death", "season"],
         text=lambda x: f"{x.of} lies curled tight and frozen stiff {x.at}: the cold did this"),
    dict(when=lambda x: x.body in ("fresh", "days") and x.cause not in ("attack", "starvation") and "cold" not in x.cause, sense="sight",
         p=0.6, reach="near", tags=["death"], text=lambda x: f"there is no wound on {x.of}'s body {x.at} that you can see"),
    # ---- rot: in the warm it smells and draws flies; in the frost it keeps
    dict(when=lambda x: x.rot and x.body and (x.warm or x.indoors), sense="smell", p=0.3, reach="node", tags=["death", "danger"],
         text=lambda x: "the smell of something dead hangs about the place"),
    dict(when=lambda x: x.rot and x.body and (x.warm or x.indoors), sense="smell", p=0.6, reach="near", tags=["death", "danger"],
         text=lambda x: f"the stink of a body rotting {x.at}"),
    dict(when=lambda x: x.rot and x.body and x.warm and x.outside, sense="sound", p=0.4, tags=["death"],
         text=lambda x: f"a hum of flies {x.at}"),
    dict(when=lambda x: x.rot and x.body and x.warm, sense="sight", p=0.7, reach="near", tags=["death"],
         text=lambda x: f"flies crawl thick on the body of {x.of} {x.at}"),
    dict(when=lambda x: x.body == "days" and x.cold and x.outside, sense="touch", p=0.6, reach="near", tags=["death", "season"],
         text=lambda x: f"{x.of} lies frozen hard {x.at}: the frost has kept the body"),
    dict(when=lambda x: x.rot and x.body and x.dogs and x.outside, sense="sight", p=0.15, reach="node", tags=["death"],
         text=lambda x: f"the dogs keep slinking off toward {x.where}, noses down"),
    # ---- bones
    dict(when=lambda x: x.body == "bones", sense="sight", p=1.0, tags=["death"], text=lambda x: f"bones lie {x.at}"),
    dict(when=lambda x: x.body == "bones" and x.snow, sense="sight", p=0.4, tags=["death"],
         text=lambda x: f"bones show through the snow {x.at}"),
    dict(when=lambda x: x.body == "bones", sense="sight", p=1.0, reach="near", tags=["death"],
         text=lambda x: f"bones {x.at}, bare and grey: by the rags on them, all that is left of {x.of}"
         + (f"; beside them, {x.goods_words}" if x.goods_words else "")),
    # ---- a grave (a buried body has no conspicuousness of its own: seen across the place, or close)
    dict(when=lambda x: x.grave and x.cairn, sense="sight", p=0.2, reach="node", tags=["death"], text=lambda x: f"a cairn of stones {x.at}"),
    dict(when=lambda x: x.grave and not x.cairn and x.buried_age <= 7 and not x.snow, sense="sight", p=0.15, reach="node", tags=["death"],
         text=lambda x: f"a fresh grave {x.at}, the earth heaped and raw"),
    dict(when=lambda x: x.grave and not x.cairn and x.buried_age > 7 and not x.snow, sense="sight", p=0.1, reach="node", tags=["death"],
         text=lambda x: f"a grave {x.at}, the mound sunk" + (" and grassing over" if x.season in ("spring", "summer") else "")),
    dict(when=lambda x: x.grave and not x.cairn and x.snow, sense="sight", p=0.1, reach="node", tags=["death"],
         text=lambda x: f"a long low mound under the snow {x.at}, the shape of a grave"),
    dict(when=lambda x: x.grave, sense="sight", p=0.7, reach="near", tags=["death"],
         text=lambda x: f"the grave of {x.of} {x.at}" + (", under a cairn" if x.cairn else "")),
    # ---- goods in the open: a heap
    dict(when=lambda x: x.heap and _OPEN(x) and not x.snowed_over, sense="sight", p=1.0, tags=["food"],
         text=lambda x: f"a heap of something {x.at}"),
    dict(when=lambda x: x.heap and _OPEN(x) and x.snowed_over, sense="sight", p=1.0, tags=["food"],
         text=lambda x: f"a heap of something {x.at}, under a skin of snow"),
    dict(when=lambda x: x.heap and _OPEN(x) and x.rained and not x.snowed_over, sense="sight", p=0.5, tags=["food"],
         text=lambda x: f"a heap of something {x.at}, dark and sodden from the rain"),
    dict(when=lambda x: (x.heap or x.pack) and _OPEN(x) and x.seed and x.outside and x.weather != "fog", sense="sight", p=0.4,
         tags=["food"], text=lambda x: f"rooks and pigeons busy at something lying {x.at}"),
    dict(when=lambda x: x.heap and _OPEN(x), sense="sight", p=1.0, reach="near", tags=["food"],
         text=lambda x: f"a heap of {x.goods_words} lies {x.at}"),
    # ---- a bundle
    dict(when=lambda x: x.pack and _OPEN(x) and not x.snowed_over, sense="sight", p=1.0, tags=["food"],
         text=lambda x: f"a bundle lies {x.at}"),
    dict(when=lambda x: x.pack and _OPEN(x) and x.snowed_over, sense="sight", p=1.0, tags=["food"],
         text=lambda x: f"a bundle lies half under the snow {x.at}"),
    dict(when=lambda x: x.pack and _OPEN(x) and x.rained and not x.snowed_over, sense="sight", p=0.4, tags=["food"],
         text=lambda x: f"a sodden bundle lies {x.at}"),
    dict(when=lambda x: x.pack and _OPEN(x), sense="sight", p=1.0, reach="near", tags=["food"],
         text=lambda x: f"a bundle lies {x.at}, with {x.goods_words} in it"),
    # ---- what the weather and the days have done to goods in the open (close)
    dict(when=lambda x: x.seed and not x.body and x.rained and x.hidden != "buried", sense="sight", p=0.8, reach="near",
         tags=["food"],
         text=lambda x: f"the {x.seed_words} {x.at} {'is' if ' and ' not in x.seed_words else 'are'} dark with wet and going mouldy"),
    dict(when=lambda x: x.meat and not x.body and x.warm and x.age >= 1 and x.hidden != "buried", sense="sight", p=0.7,
         reach="near", tags=["food"],
         text=lambda x: f"the meat {x.at} is turning, and flies are at it"),
    dict(when=lambda x: x.meat and not x.body and x.cold and x.hidden != "buried", sense="touch", p=0.6, reach="near",
         tags=["food"],
         text=lambda x: f"the meat {x.at} is frozen hard"),
    dict(when=lambda x: x.rotting_food and not x.body and x.hidden != "buried", sense="smell", p=1.0, reach="near", tags=["food"],
         text=lambda x: f"the stink of meat gone bad {x.at}"),
    dict(when=lambda x: x.rotting_food and not x.body and x.warm and x.outside and x.hidden != "buried", sense="smell", p=0.15,
         reach="node", tags=["food"], text=lambda x: "a smell of rot comes and goes on the wind"),
    dict(when=lambda x: x.rotting_food and not x.body and x.warm and x.outside and x.hidden != "buried", sense="sound", p=0.4,
         tags=["food"], text=lambda x: f"a buzz of flies {x.at}"),
    # ---- left at a door
    dict(when=lambda x: x.at_door, sense="sight", p=0.8, reach="node", tags=["food"],
         text=lambda x: f"something has been left at the door of {x.door_name}"),
    dict(when=lambda x: x.at_door, sense="sight", p=1.0, reach="near", tags=["food"],
         text=lambda x: f"left at the door of {x.door_name}: {x.goods_words}"),
    # ---- hidden under brush: a tracker reads cut brush for what it is
    dict(when=lambda x: x.hidden == "under brush", sense="sight", p=1.0, lay="hunt", tags=["food"],
         text=lambda x: f"the brush {x.at} looks heaped up, as if over something"),
    dict(when=lambda x: x.hidden == "under brush", sense="sight", p=1.0, knows="hunt", tags=["food"],
         text=lambda x: f"brush cut and laid {x.at}, not fallen: someone has hidden something under it"),
    dict(when=lambda x: x.hidden == "under brush" and x.untaught, sense="sight", p=0.6, tags=["food"],
         text=lambda x: f"a heap of brush {x.at}, the cut ends showing: a clumsy job"),
    dict(when=lambda x: x.hidden and x.snow and x.snow_laid and x.age <= 2 and not x.snowed_over, sense="sight", p=0.8, tags=["food"],
         text=lambda x: f"footprints in the snow lead to a spot {x.at} and back"),
    dict(when=lambda x: x.hidden == "under brush" and x.food and x.dogs, sense="sight", p=0.2, reach="node", tags=["food"],
         text=lambda x: f"a dog keeps nosing at the brush {x.at}"),
    dict(when=lambda x: x.hidden == "under brush", sense="sight", p=1.0, reach="near", tags=["food"],
         text=lambda x: f"something hidden under brush {x.at}: {x.goods_words}"),
    # ---- buried (not a body): turned earth; a close look tells something is there, not what
    dict(when=lambda x: x.hidden == "buried" and not x.body and x.age <= 5, sense="sight", p=1.0, lay="hunt", tags=["food"],
         text=lambda x: f"a patch of turned earth {x.at}, as if something were buried there"),
    dict(when=lambda x: x.hidden == "buried" and not x.body and x.age > 5, sense="sight", p=1.0, lay="hunt", tags=["food"],
         text=lambda x: f"a patch of earth {x.at} that has sunk a little, as if dug once and filled"),
    dict(when=lambda x: x.hidden == "buried" and not x.body, sense="sight", p=1.0, knows="hunt", tags=["food"],
         text=lambda x: f"the ground {x.at} has been dug and smoothed over: something is buried there"),
    dict(when=lambda x: x.hidden == "buried" and not x.body and x.rained and x.age <= 5, sense="sight", p=0.5, tags=["food"],
         text=lambda x: f"a patch {x.at} where the earth has sunk after the rain, the shape of a hole filled in"),
    dict(when=lambda x: x.hidden == "buried" and not x.body and x.food and x.dogs, sense="sight", p=0.2, reach="node", tags=["food"],
         text=lambda x: f"a dog digging {x.at}"),
    dict(when=lambda x: x.hidden == "buried" and not x.body, sense="touch", p=1.0, reach="near", tags=["food"],
         text=lambda x: f"something is buried {x.at}, not deep: the earth is loose underfoot"),
]

# The road: the day's weather on it, its terrain, its landmarks by their state, and one's own load. Each night's lines are kept as
# "On the way" (up to five on arrival), so the scenery rows are kept to a line or two a night.
ROAD = [
    # the day's weather on the road
    dict(when=lambda x: x.weather in ("rain", "heavy rain"), sense="sight", p=0.6, tags=["season"], text=lambda x: x.weather_words),
    dict(when=lambda x: x.weather in ("rain", "heavy rain") and x.terrain == "woodland", sense="sound", p=0.5, tags=["season"],
         text=lambda x: "rain dripping through the trees all day"),
    dict(when=lambda x: x.weather in ("rain", "heavy rain") and x.terrain in ("plain", "farmland", "marsh", "river valley"), sense="touch",
         p=0.5, tags=["season", "travel"], text=lambda x: "the road was mud under the rain, heavy on the feet"),
    dict(when=lambda x: x.weather == "heavy rain" and x.terrain in ("hills", "mountain"), sense="sight", p=0.5, tags=["season", "travel"],
         text=lambda x: "water ran down the road through the hills like a stream"),
    dict(when=lambda x: x.weather == "fog", sense="sight", p=0.7, tags=["season", "travel"],
         text=lambda x: "fog all day: you could see barely a stone's throw ahead"),
    dict(when=lambda x: x.weather == "gale" and x.terrain != "woodland", sense="touch", p=0.7, tags=["season", "travel"],
         text=lambda x: "a gale on the open road, hard to walk against"),
    dict(when=lambda x: x.weather == "gale" and x.terrain == "woodland", sense="sound", p=0.7, tags=["season", "travel", "danger"],
         text=lambda x: "a gale in the wood, branches cracking and coming down about the road"),
    dict(when=lambda x: x.weather == "snow", sense="sight", p=0.7, tags=["season", "travel"],
         text=lambda x: "snow falling all day, the road lost under it in places"),
    dict(when=lambda x: x.snow and x.weather != "snow", sense="sight", p=0.5, tags=["season", "travel"],
         text=lambda x: "snow lay along the road"),
    dict(when=lambda x: x.weather == "clear" and x.cold and not x.snow, sense="touch", p=0.25, tags=["season"],
         text=lambda x: "a clear, hard frost: the road rang underfoot"),
    dict(when=lambda x: x.weather == "clear" and x.season == "summer" and not x.cold, sense="touch", p=0.15, tags=["season"],
         text=lambda x: "a hot day on the road, dust underfoot"),
    # the terrain
    dict(when=lambda x: x.terrain == "woodland", sense="sight", p=0.15, tags=["travel"],
         text=lambda x: "the road ran under trees all day, little to see either side"),
    dict(when=lambda x: x.terrain == "marsh", sense="sight", p=0.15, tags=["travel"],
         text=lambda x: "the road wound through marsh, reeds and standing water on either side"),
    dict(when=lambda x: x.terrain == "hills", sense="sight", p=0.15, tags=["travel"], text=lambda x: "the road climbed and dropped through the hills"),
    dict(when=lambda x: x.terrain == "mountain", sense="touch", p=0.15, tags=["travel"], text=lambda x: "a hard climb, the road steep and stony"),
    dict(when=lambda x: x.terrain in ("mountain", "hills") and x.cold, sense="touch", p=0.25, tags=["travel", "season"],
         text=lambda x: "a bitter wind off the heights"),
    dict(when=lambda x: x.terrain == "river valley", sense="sight", p=0.15, tags=["travel"], text=lambda x: "the road kept by the river all day"),
    dict(when=lambda x: x.terrain == "farmland" and not x.snow, sense="sight", p=0.15, tags=["travel", "farming"],
         text=lambda x: "fields and hedges either side of the road"),
    dict(when=lambda x: x.terrain in ("farmland", "plain") and x.snow, sense="sight", p=0.15, tags=["travel"],
         text=lambda x: "the land either side lay white under snow"),
    dict(when=lambda x: x.terrain == "plain" and x.weather == "clear", sense="sight", p=0.15, tags=["travel"],
         text=lambda x: "open country, the road plain to see far ahead"),
    # one's own load
    dict(when=lambda x: x.cart and x.terrain in ("hills", "mountain"), sense="touch", p=0.25, tags=["travel"],
         text=lambda x: "hard work pushing the handcart up the hills"),
    dict(when=lambda x: x.cart and x.weather in ("rain", "heavy rain") and x.terrain not in ("hills", "mountain"), sense="touch", p=0.25,
         tags=["travel"], text=lambda x: "the handcart's wheels clogged with mud"),
    # a ford
    dict(when=lambda x: "ford" in x.lm and not x.state.get("ford"), sense="sight", p=1.0, tags=["travel"], text=lambda x: "you passed a ford"),
    dict(when=lambda x: "ford" in x.lm and not x.state.get("ford") and x.cold, sense="sight", p=0.4, tags=["travel", "season"],
         text=lambda x: "ice at the edges of the ford, the water black and cold"),
    dict(when=lambda x: "ford" in x.lm and not x.state.get("ford") and x.spell == "dry", sense="sight", p=0.4, tags=["travel"],
         text=lambda x: "the ford was low, the stones dry across it"),
    dict(when=lambda x: x.state.get("ford") == "high", sense="sound", p=0.8, tags=["travel", "danger"],
         text=lambda x: "the river at the ford ran brown and loud, over the stepping stones"),
    # a bridge
    dict(when=lambda x: "bridge" in x.lm and not x.state.get("bridge"), sense="sight", p=1.0, tags=["travel"],
         text=lambda x: "you crossed a bridge"),
    dict(when=lambda x: "bridge" in x.lm and not x.state.get("bridge") and x.since_heavy is not None and x.since_heavy < 2, sense="sound",
         p=0.5, tags=["travel"], text=lambda x: "the river ran high and loud under the bridge"),
    dict(when=lambda x: x.state.get("bridge") == "down", sense="sight", p=0.8, tags=["travel", "danger"],
         text=lambda x: "the bridge was down, its timbers in the river"),
    # a pass
    dict(when=lambda x: "pass" in x.lm and not x.state.get("pass"), sense="sight", p=1.0, tags=["travel"], text=lambda x: "you went over a pass"),
    dict(when=lambda x: "pass" in x.lm and not x.state.get("pass") and x.cold, sense="touch", p=0.5, tags=["travel", "season"],
         text=lambda x: "the wind on the pass cut to the bone"),
    dict(when=lambda x: "pass" in x.lm and not x.state.get("pass") and x.weather == "clear" and not x.cold, sense="sight", p=0.4,
         tags=["travel"], text=lambda x: "from the top of the pass you could see far down both sides"),
    dict(when=lambda x: x.state.get("pass") == "snowed", sense="sight", p=0.8, tags=["travel", "danger"],
         text=lambda x: "drifts deep across the pass, the track buried"),
    # a narrows: a tracker sees what it is good for
    dict(when=lambda x: "narrows" in x.lm, sense="sight", p=1.0, tags=["travel"], text=lambda x: "the road ran through a narrows"),
    dict(when=lambda x: "narrows" in x.lm, sense="sight", p=0.5, lay="hunt", tags=["travel"],
         text=lambda x: "at the narrows the road runs between steep sides, where it can be watched from above"),
    dict(when=lambda x: "narrows" in x.lm, sense="sight", p=0.8, knows="hunt", tags=["travel", "danger"],
         text=lambda x: "the narrows is a place to be caught in: a few above could stop a party there"),
    dict(when=lambda x: "narrows" in x.lm and x.weather == "fog", sense="sight", p=0.4, tags=["travel"],
         text=lambda x: "fog filled the narrows"),
    # a spring
    dict(when=lambda x: "spring" in x.lm, sense="sight", p=0.9, tags=["travel"], text=lambda x: "you drank at a spring by the road"),
    dict(when=lambda x: "spring" in x.lm and x.cold, sense="touch", p=0.4, tags=["travel", "season"],
         text=lambda x: "the spring by the road was rimmed with ice"),
    # good places out of their season (in season, roads._landmark says what one ate there); a forager knows when they give
    dict(when=lambda x: "fruit trees" in x.lm and x.season in ("winter", "spring"), sense="sight", p=0.5, lay="forage", tags=["travel", "food"],
         text=lambda x: "wild fruit trees by the road, bare now"),
    dict(when=lambda x: "fruit trees" in x.lm and x.season == "summer", sense="sight", p=0.5, lay="forage", tags=["travel", "food"],
         text=lambda x: "wild fruit trees by the road, the fruit still small and green"),
    dict(when=lambda x: "fruit trees" in x.lm and x.season != "autumn", sense="sight", p=0.8, knows="forage", tags=["travel", "food"],
         text=lambda x: "wild fruit trees by the road: there will be fruit to gather there in autumn"),
    dict(when=lambda x: "meadow" in x.lm and x.season in ("winter", "spring"), sense="sight", p=0.5, lay="forage", tags=["travel", "food"],
         text=lambda x: "a meadow by the road, " + ("the grass short and brown" if x.season == "winter" else "just greening")),
    dict(when=lambda x: "meadow" in x.lm and x.season in ("winter", "spring"), sense="sight", p=0.8, knows="forage", tags=["travel", "food"],
         text=lambda x: "a meadow by the road that will be good gathering in summer and autumn"),
    dict(when=lambda x: "hollow" in x.lm and (x.cold or x.weather in ("gale", "rain", "heavy rain", "snow")), sense="touch", p=0.5,
         tags=["travel", "shelter"], text=lambda x: "a sheltered hollow by the road, out of the wind and the wet"),
]

# Traces others left on the road (D2-88). Anyone reads the way they go and roughly how old they are; one who hunts reads how many,
# and how long ago, from the edges of a print or the warmth of ashes.
TRACE = [
    # tracks
    dict(when=lambda x: x.kind == "tracks" and not x.snow and not x.heavy, sense="sight", p=1.0, tags=["travel"],
         text=lambda x: f"{x.many} tracks going toward {x.toward}, {x.when}"),
    dict(when=lambda x: x.kind == "tracks" and x.snow and not x.snowed_over, sense="sight", p=1.0, tags=["travel"],
         text=lambda x: f"{x.many} tracks plain in the snow, going toward {x.toward}, {x.when}"),
    dict(when=lambda x: x.kind == "tracks" and x.snowed_over, sense="sight", p=0.6, tags=["travel"],
         text=lambda x: f"a line of dents in the new snow going toward {x.toward}: tracks, snowed over"),
    dict(when=lambda x: x.kind == "tracks" and x.heavy and not x.snow, sense="sight", p=0.6, tags=["travel"],
         text=lambda x: f"tracks going toward {x.toward}, half washed out by the rain"),
    dict(when=lambda x: x.kind == "tracks" and not x.snowed_over, sense="sight", p=1.0, knows="hunt", tags=["travel"],
         text=lambda x: f"the tracks of {_folk(x.n)} going toward {x.toward}, " + ("made yesterday, the edges still sharp" if x.age <= 1 and not x.rained else x.when)),
    dict(when=lambda x: x.kind == "tracks" and x.rained and not x.heavy and not x.snow and x.n >= 2, sense="sight", p=0.5, lay="hunt",
         tags=["travel"], text=lambda x: "trampled mud on the road, as if several had passed"),
    dict(when=lambda x: x.kind == "tracks" and x.terrain == "woodland" and not x.snow, sense="sight", p=0.3, tags=["travel"],
         text=lambda x: f"broken twigs and trodden leaves along the road toward {x.toward}"),
    # cart ruts: they last a season; one who hunts can tell their age
    dict(when=lambda x: x.kind == "ruts" and x.age <= 3 and not x.snowed_over, sense="sight", p=1.0, tags=["travel"],
         text=lambda x: f"cart ruts going toward {x.toward}, {x.when}"),
    dict(when=lambda x: x.kind == "ruts" and x.age > 3 and not x.snowed_over, sense="sight", p=1.0, lay="hunt", tags=["travel"],
         text=lambda x: (f"cart ruts going toward {x.toward}, some days old" if x.age <= 10
                         else "old cart ruts in the road" + (", grassed at the edges" if x.season in ("spring", "summer") else ""))),
    dict(when=lambda x: x.kind == "ruts" and x.age > 3 and not x.snowed_over, sense="sight", p=1.0, knows="hunt", tags=["travel"],
         text=lambda x: f"cart ruts going toward {x.toward}, {x.when}"),
    dict(when=lambda x: x.kind == "ruts" and x.snow, sense="sight", p=0.5, tags=["travel"],
         text=lambda x: "cart ruts showing as long lines under the snow"),
    dict(when=lambda x: x.kind == "ruts" and x.wet, sense="sight", p=0.5, tags=["travel"],
         text=lambda x: f"cart ruts going toward {x.toward}, full of rainwater"),
    # a fire's ashes
    dict(when=lambda x: x.kind == "ashes" and x.age < 3 and not x.rained and not x.snowed_over, sense="sight", p=1.0, tags=["travel"],
         text=lambda x: f"the ashes of a fire by the road, {x.when}"),
    dict(when=lambda x: x.kind == "ashes" and x.age >= 3 and not x.rained and not x.snowed_over, sense="sight", p=1.0, tags=["travel"],
         text=lambda x: "the cold ashes of a fire by the road"),
    dict(when=lambda x: x.kind == "ashes" and x.rained and not x.snowed_over, sense="sight", p=1.0, tags=["travel"],
         text=lambda x: "the ashes of a fire by the road, beaten to a grey paste by the rain"),
    dict(when=lambda x: x.kind == "ashes" and x.snowed_over, sense="sight", p=0.6, tags=["travel"],
         text=lambda x: "a ring of fire-stones under the snow by the road"),
    dict(when=lambda x: x.kind == "ashes" and x.age <= 1 and not x.rained, sense="touch", p=0.8, knows="hunt", tags=["travel"],
         text=lambda x: "the ashes by the road are still a little warm underneath: the fire was lit last night"),
    dict(when=lambda x: x.kind == "ashes" and x.n > 2 and not x.snowed_over, sense="sight", p=0.8, knows="hunt", tags=["travel"],
         text=lambda x: f"a big fire by the road, the ground flattened round it where a party slept, {x.when}"),
    dict(when=lambda x: x.kind == "ashes" and x.n <= 2 and not x.snowed_over, sense="sight", p=0.8, knows="hunt", tags=["travel"],
         text=lambda x: f"a small fire by the road, room round it for one or two to sleep, {x.when}"),
]

# Travellers seen far off on the same stretch, coming the other way (roads._notices: n, cart, armed, toward, weather).
TRAVELLER = [
    dict(when=lambda x: x.n == 1 and x.weather != "fog", sense="sight", p=1.0, tags=["travel"],
         text=lambda x: f"a lone traveller far off on the road, going toward {x.toward}" + (" with a cart" if x.cart else "")),
    dict(when=lambda x: x.n > 1 and x.weather != "fog", sense="sight", p=1.0, tags=["travel"],
         text=lambda x: f"{_num(x.n)} travellers far off on the road, going toward {x.toward}" + (" with a cart" if x.cart else "")),
    dict(when=lambda x: x.cart, sense="sound", p=0.3, reach="node", tags=["travel"],
         text=lambda x: "a cart's creak somewhere along the road"),
    dict(when=lambda x: x.weather == "fog", sense="sound", p=0.5, reach="node", tags=["travel"],
         text=lambda x: "voices on the road somewhere in the fog, and footsteps going by"),
    dict(when=lambda x: x.armed and x.weather != "fog", sense="sight", p=0.5, tags=["travel", "danger"],
         text=lambda x: "one of the travellers far off carries a club or a spear"),
    dict(when=lambda x: x.n >= 4 and x.weather != "fog", sense="sight", p=0.6, tags=["travel", "danger"],
         text=lambda x: "a big party on the road, strung out in a line"),
    dict(when=lambda x: x.weather in ("rain", "heavy rain"), sense="sight", p=0.4, tags=["travel"],
         text=lambda x: "figures far off on the road, hunched against the rain"),
    dict(when=lambda x: x.weather == "snow", sense="sight", p=0.5, tags=["travel"],
         text=lambda x: "dark figures far off against the snow"),
]

# What one woken in the night senses of a break-in (fuse._detect_raid: the watcher at the door, those asleep inside, neighbours).
NIGHT = [
    # the watcher
    dict(when=lambda x: x.role == "watcher" and not x.camp, sense="sight", p=1.0, tags=["danger"],
         text=lambda x: f"from your watch at {x.house}: a shape at the door in the dark, someone trying the bar"),
    dict(when=lambda x: x.role == "watcher" and x.camp, sense="sight", p=1.0, tags=["danger"],
         text=lambda x: f"from your watch at {x.house}: someone creeping in among the packs in the dark"),
    dict(when=lambda x: x.role == "watcher" and x.armed, sense="sight", p=0.6, tags=["danger"],
         text=lambda x: "whoever it is carries something long in one hand, a club or a spear"),
    dict(when=lambda x: x.role == "watcher" and x.snow, sense="sight", p=0.6, tags=["danger"],
         text=lambda x: f"a dark figure against the snow by {x.house}"),
    dict(when=lambda x: x.role == "watcher" and x.weather == "fog", sense="sight", p=0.6, tags=["danger"],
         text=lambda x: f"something moving in the fog by {x.house}"),
    # those asleep inside
    dict(when=lambda x: x.role == "inside" and not x.camp, sense="sound", p=1.0, tags=["danger"],
         text=lambda x: f"a crash at the door of {x.house}, where you sleep; someone is breaking in"),
    dict(when=lambda x: x.role == "inside" and x.camp, sense="sound", p=1.0, tags=["danger"],
         text=lambda x: f"someone moving about {x.house} in the dark, going through the packs"),
    dict(when=lambda x: x.role == "inside" and x.structure == "wattle", sense="sound", p=0.5, tags=["danger"],
         text=lambda x: "the wattle by the door creaks and gives under someone's weight"),
    dict(when=lambda x: x.role == "inside" and x.structure in ("timber", "stone"), sense="sound", p=0.5, tags=["danger"],
         text=lambda x: "the bar of the door jumps in its brackets at each blow"),
    dict(when=lambda x: x.role == "inside" and x.weather == "gale", sense="sound", p=0.5, tags=["danger"],
         text=lambda x: "over the noise of the wind, a blow at the door that is not the wind"),
    # anyone near: a dog, riders
    dict(when=lambda x: x.dog and x.role in ("inside", "watcher"), sense="sound", p=0.9, tags=["danger"],
         text=lambda x: "the dog will not stop barking at the door"),
    dict(when=lambda x: x.dog and x.role == "neighbour", sense="sound", p=0.9, tags=["danger"],
         text=lambda x: f"the dog at {x.house} will not stop barking"),
    dict(when=lambda x: x.riders and x.role in ("inside", "watcher"), sense="sound", p=0.8, tags=["danger"],
         text=lambda x: f"hooves outside {x.house}, beasts blowing in the dark"),
    dict(when=lambda x: x.riders and x.role == "neighbour", sense="sound", p=0.7, tags=["danger"],
         text=lambda x: f"hoofbeats in the dark, going toward {x.house}"),
    # neighbours
    dict(when=lambda x: x.role == "neighbour" and not x.camp, sense="sound", p=1.0, tags=["danger"],
         text=lambda x: f"a noise in the night from {x.house}: wood splitting, a muffled voice"),
    dict(when=lambda x: x.role == "neighbour" and x.camp, sense="sound", p=1.0, tags=["danger"],
         text=lambda x: f"a noise in the night from {x.house}: someone moving about, a voice raised and cut short"),
    dict(when=lambda x: x.role == "neighbour" and x.weather in ("gale", "heavy rain"), sense="sound", p=0.5, tags=["danger"],
         text=lambda x: f"under the {'wind' if x.weather == 'gale' else 'rain'}, a sound from {x.house} like a door giving way"),
]


# ---------------------------------------------------------------------- contexts (engine side: things, roads and nights)
def _since(w, day, test) -> bool:
    """Whether `test(d)` holds for any day from `day` to today."""
    return any(test(d) for d in range(max(0, int(day)), w.d + 1))


SEED_GOODS = ("grain", "rye", "beans", "flour", "bread", "wild food")


def thing_context(w, c):
    from cybertron2.engine import environment as EV, things as TH
    from cybertron2.engine.data import ITEMS, THINGS
    st = TH.body_state(w, c)
    qty = sum(q * max(1, ITEMS.get(i, {}).get("weight", 1)) for i, q in c["goods"].items() if q > 1e-9)
    door = c.get("door")
    where = TH.parcel_name(w, c)
    on_road = c.get("node") not in w.s["nodes"]
    indoors = c.get("in") in w.s["buildings"]
    laid = int(c.get("died", c.get("day", w.d)))
    items = {i for i, q in c["goods"].items() if q > 1e-9}
    seed = [i for i in SEED_GOODS if i in items]
    wx = EV.weather(w)
    person = w.s["people"].get(c.get("of")) or {}
    x = SimpleNamespace(c=c, kind=c["kind"], of=c.get("of"), where=where, body=st,
                        at=f"in {where}" if indoors else ("by the road" if on_road else f"at {where}"),
                        grave=bool(c.get("body")) and c.get("buried") is not None, cairn=bool(c.get("cairn")),
                        buried_age=w.d - int(c["buried"]) if c.get("buried") is not None else 0,
                        hidden=c.get("hidden"), untaught=bool(c.get("untaught")), goods=dict(c["goods"]),
                        goods_words=TH.goods_words(c["goods"]), qty=qty, heap=qty >= float(THINGS["heap_min"]),
                        pack=0 < qty < float(THINGS["heap_min"]), rot=TH.rotting(w, c),
                        rotting_food=any(ITEMS.get(i, {}).get("rot") and q > 0.2 for i, q in c["goods"].items()),
                        at_door=bool(door) and qty > 0, door_name=w.s["buildings"][door]["name"] if door in w.s["buildings"] else "",
                        age=w.d - laid, on_road=on_road, indoors=indoors, outside=not indoors,
                        cause=str(person.get("cause") or "") if c.get("body") else "",
                        food=any(ITEMS.get(i, {}).get("food", 0) > 0 for i in items), meat="meat" in items,
                        seed=bool(seed), seed_words=" and ".join(seed[:2]),
                        weather=wx, snow=EV.snow_lying(w), season=w.calendar()["season"], cold=w.cold(), day=w.d,
                        rained=not indoors and _since(w, laid, lambda d: EV.wet(w, d) and EV.weather(w, d) != "snow"),
                        snowed_over=not indoors and _since(w, laid + 1, lambda d: EV.weather(w, d) == "snow") and EV.snow_lying(w),
                        snow_laid=EV.snow_lying(w, laid),
                        dogs=not on_road and any(b["node"] == c.get("node") and b["fittings"].get("dog") for b in w.s["buildings"].values()))
    x.warm = not x.cold
    return x


def herd_context(w, hid):
    """A herd off its home ground (ASTRAY), or its home pasture without it (EMPTY)."""
    h = w.s["herds"][hid]
    par = w.s["parcels"][h["parcel"]] if h.get("parcel") in w.s["parcels"] else None
    home = w.s["parcels"].get(h.get("home")) or {}
    c = (par or {}).get("crop") or {}
    in_crop = bool(c) and c.get("area_left", 0) > 1e-6
    holders = [cl["claimant"] for cl in w.claims_on(("herd", hid))]
    hh = {iid: x["name"] for iid, x in w.s["institutions"].items()}
    whose = " and ".join(sorted({hh.get(x, x) for x in holders}))
    hfc = home.get("fence") or {}
    return SimpleNamespace(h=h, name=h["name"], base=h.get("base_name") or h["name"], words=FM.herd_words(h),
                           nm=(par or {}).get("name", ""), nm_cover=(par or {}).get("cover", ""), home=home.get("name", "their pasture"),
                           in_crop=in_crop, crop=c.get("kind", "crop"), ripe=in_crop and w.d >= int(c.get("ripe_day", 10 ** 9)),
                           trampled=float((c.get("trampled") or {}).get("qty", 0.0)) if (c.get("trampled") or {}).get("by") == hid else 0.0,
                           hungry=int(h.get("hungry", 0)) > 0, whose=(f"they are {whose}'s" if whose else ""),
                           strays=bool(h.get("split_of")), from_road=bool(h.get("strayed_in")),
                           gap=bool(hfc.get("built")) and 0 < int(hfc.get("level", 0)) < 2, gate_open=hfc.get("gate") == "open")


def fence_context(w, pid):
    from cybertron2.engine.data import FENCES
    par = w.s["parcels"][pid]
    fc = par.get("fence") or {}
    kind = fc.get("kind", "wood")
    need = FM.fence_need(par, kind)["units"]
    built = bool(fc.get("built"))
    lvl = int(fc.get("level", 0))
    frac = min(1.0, float(fc.get("units", 0.0)) / need) if need else 0.0
    herd_in = next((h["name"] for h in w.s["herds"].values() if h.get("parcel") == pid and FM.head(h) > 0), "")
    return SimpleNamespace(nm=par["name"], kind=kind, word=FENCES[kind]["words"][0], building=not built and frac > 0,
                           done=("barely begun" if frac < 0.25 else "half done" if frac < 0.75 else "nearly done"),
                           whole=built and lvl >= 2, gappy=built and lvl == 1, down=built and lvl <= 0,
                           gate_open=built and lvl > 0 and fc.get("gate") == "open", opened_by=(fc.get("opened") or {}).get("by"),
                           herd_in=herd_in)


def spot_rows(here, rows, x, about, node, parcel, add, concerns=(), only=None, **extra) -> None:
    """Emit a bundle read by the noticing rule at a spot: each true row as a fact carrying its own conspicuousness."""
    for i, row in true_rows(rows, x):
        p = row["p"](x) if callable(row["p"]) else row["p"]
        add(about, row["text"](x), p, row.get("tags", []), row.get("sense", "sight"), concerns=list(concerns), knack=row.get("knack"),
            spot={"node": node, "parcel": parcel, "own": float(row["own"])}, only=only, gate=parcel if row.get("gate") else None,
            sign=f"{about[0]}#spot{i}", **extra)


def carcass_context(w, c):
    """A dead beast at a spot (D4-52): how long dead, whether still fit to eat, how it died, the weather on it."""
    from cybertron2.engine import environment as EV, things as TH
    from cybertron2.engine.data import THINGS
    where = TH.parcel_name(w, c)
    on_road = c.get("node") not in w.s["nodes"]
    age = w.d - int(c.get("died", w.d))
    bones = age >= int(THINGS["carcass_bones_after"])
    return SimpleNamespace(beast=c.get("beast", "beast"), of=c.get("of", "a beast"), where=where, on_road=on_road,
                           at="by the road" if on_road else f"at {where}", off_road=c.get("hidden") == "off the road",
                           age=age, fresh=TH.carcass_fresh(w, c) and not bones, rotten=not TH.carcass_fresh(w, c) and not bones,
                           bones=bones, starved=c.get("cause") == "starved", hide=c["goods"].get("hide", 0) > 0,
                           meat=c["goods"].get("meat", 0) > 0, cold=w.cold(), warm=not w.cold(), weather=EV.weather(w),
                           snow=EV.snow_lying(w), dogs=not on_road and any(b["node"] == c.get("node") and b["fittings"].get("dog")
                                                                            for b in w.s["buildings"].values()))


def road_context(w, name, t, pos):
    from cybertron2.engine import environment as EV, roads as RD
    from cybertron2.engine.data import WEATHER
    st = RD.stretch(w, t["road"], pos)
    lm = [l["kind"] for l in st["landmarks"]]
    state = {l["kind"]: RD.challenge(w, t["road"], pos, l) for l in st["landmarks"]}
    wx = EV.weather(w)
    return SimpleNamespace(name=name, terrain=st["terrain"] or "plain", lm=lm, state=state, weather=wx, weather_words=WEATHER[wx]["words"],
                           snow=EV.snow_lying(w), season=w.calendar()["season"], cold=w.cold(), day=w.d, toward=w.s["nodes"][t["to"]]["name"],
                           first_night=w.d == t["left"], cart=w.goods(w.hands(name)).get("handcart", 0) >= 1,
                           spell=EV.spell(w), since_heavy=EV.since_heavy_rain(w))


def traveller_context(w, others, o, pos):
    """A party seen far off on one's stretch (roads._notices): how many, a cart, arms, beasts' loads, where bound, and the land."""
    from cybertron2.engine import environment as EV, roads as RD
    from cybertron2.engine.data import ITEMS
    st = RD.stretch(w, o["road"], pos)
    load = sum(q * ITEMS[i]["weight"] for m in others for i, q in w.goods(w.hands(m)).items() if q > 1e-9)
    return SimpleNamespace(n=len(others), cart=any(w.goods(w.hands(m)).get("handcart", 0) >= 1 for m in others),
                           armed=any(w.weapon(m) for m in others), toward=w.s["nodes"][o["to"]]["name"], weather=EV.weather(w),
                           terrain=st["terrain"] or "plain", snow=EV.snow_lying(w), laden=load >= 8 * len(others), season=w.calendar()["season"])


def trace_context(w, x):
    from cybertron2.engine import environment as EV, roads as RD
    age = w.d - x["day"]
    many = "a party's" if x["n"] > 2 else "a traveller's" if x["n"] == 1 else "two travellers'"
    try:
        terrain = RD.stretch(w, x["road"], x["pos"])["terrain"] or "plain"
    except (KeyError, IndexError):
        terrain = "plain"
    after = int(x["day"]) + 1                                                  # the weather since it was left
    return SimpleNamespace(kind=x["kind"], age=age, n=x["n"], toward=x["toward"], many=many, snow=EV.snow_lying(w), weather=EV.weather(w),
                           when=_old(age), terrain=terrain, season=w.calendar()["season"], wet=EV.wet(w),
                           rained=_since(w, after, lambda d: EV.weather(w, d) in ("rain", "heavy rain")),
                           heavy=_since(w, after, lambda d: EV.weather(w, d) == "heavy rain"),
                           snowed_over=_since(w, after, lambda d: EV.weather(w, d) == "snow") and EV.snow_lying(w))


def night_context(w, e, role):
    from cybertron2.engine import environment as EV
    b = w.s["buildings"][e["building"]]
    by = e.get("by")
    return SimpleNamespace(role=role, house=b["name"], structure=b["structure"], camp=b["structure"] == "camp",
                           dog=bool(b["fittings"].get("dog")), riders=bool(e.get("riders")), weather=EV.weather(w), cold=w.cold(),
                           season=w.calendar()["season"], snow=EV.snow_lying(w),
                           armed=bool(by in w.s["people"] and w.weapon(by)))


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


def bundle(w, c):
    """The bundle and context for a thing at a spot: a dead beast reads CARCASS, everything else THING."""
    return (CARCASS, carcass_context(w, c)) if c.get("kind") == "carcass" else (THING, thing_context(w, c))


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


# ---------------------------------------------------------------------- a meeting that passes (D4-51): one side chose not to stop
PASSING = [
    # we went by
    dict(when=lambda x: x.we_passed and not x.fog, sense="sight", p=1.0, tags=["travel"],
         text=lambda x: f"you passed {x.names} at {x.where}, going the other way, and did not stop"),
    dict(when=lambda x: x.we_passed and not x.fog and not x.they_passed, sense="sound", p=0.5, tags=["travel"],
         text=lambda x: f"{x.names} called a greeting at {x.where}; you kept walking"),
    dict(when=lambda x: x.we_passed and x.armed, sense="sight", p=0.6, tags=["travel", "danger"],
         text=lambda x: f"{x.names} watched you go by at {x.where}, with weapons to hand"),
    dict(when=lambda x: x.we_passed and x.cart, sense="sound", p=0.5, tags=["travel"],
         text=lambda x: f"you stood aside at {x.where} to let {x.names} and their cart go by, then went on"),
    dict(when=lambda x: x.we_passed and x.fog, sense="sight", p=1.0, tags=["travel"],
         text=lambda x: f"shapes in the fog at {x.where}: {x.n_words} going the other way; you kept on"),
    # they went by
    dict(when=lambda x: x.they_passed and not x.we_passed and not x.fog, sense="sight", p=1.0, tags=["travel"],
         text=lambda x: f"{x.names} passed you at {x.where} without stopping"),
    dict(when=lambda x: x.they_passed and not x.we_passed and not x.fog, sense="sight", p=0.5, tags=["travel"],
         text=lambda x: f"{x.names} kept to the far side of the road at {x.where} and would not be drawn into talk"),
    dict(when=lambda x: x.they_passed and not x.we_passed, sense="sound", p=0.4, tags=["travel"],
         text=lambda x: f"you called out to {x.names} at {x.where}, but they did not stop"),
    dict(when=lambda x: x.they_passed and not x.we_passed and x.laden, sense="sight", p=0.5, tags=["travel"],
         text=lambda x: f"{x.names} went by at {x.where} bent under heavy loads"),
    dict(when=lambda x: x.they_passed and not x.we_passed and x.fog, sense="sound", p=1.0, tags=["travel"],
         text=lambda x: f"footsteps went past you in the fog at {x.where}; whoever it was did not stop"),
]


def passing_context(w, party, other, m, we_passed, they_passed):
    from cybertron2.engine import environment as EV, roads as RD
    from cybertron2.engine.data import ITEMS, LANDMARKS
    st = RD.stretch(w, m["road"], m["pos"])
    where = LANDMARKS[st["landmarks"][0]["kind"]]["words"] if st["landmarks"] else f"the {st['terrain'] or 'road'}"
    load = sum(q * ITEMS[i]["weight"] for n in other for i, q in w.goods(w.hands(n)).items() if q > 1e-9)
    names = ", ".join(other) if len(other) <= 3 else f"{len(other)} travellers"
    return SimpleNamespace(names=names, n=len(other), n_words=f"{len(other)} traveller{'s' if len(other) > 1 else ''}", where=where,
                           we_passed=we_passed, they_passed=they_passed, fog=EV.weather(w) == "fog",
                           armed=any(w.weapon(n) for n in other), cart=any(w.goods(w.hands(n)).get("handcart", 0) >= 1 for n in other),
                           laden=load >= 8 * len(other), weather=EV.weather(w), terrain=st["terrain"] or "plain")
