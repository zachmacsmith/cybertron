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
from cybertron2.engine.data import CROP_OF, CROPS, FENCES, FITTINGS, ITEMS, SEED_CROP, TECHNIQUES
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


# ---------------------------------------------------------------------- plot shares: a crop for each holding (D2-163, D2-172)
# A field's ground is held in whole plots by claims (a claim without `plots` covers all of them). The parcel's own crop and soil
# fields (crop, fertility, broken, last_crop, last_kind, fallow_since) are the record of the ground held whole (by those whose claims
# cover all of it, `held_whole`), or, where nobody holds it whole, of its unclaimed plots: holder None. Each holding of part of a
# field has its own record in the parcel's `shares` list: {holder, plots, crop, fertility, broken, last_crop, last_kind,
# fallow_since}. A field held whole therefore keeps its state exactly where it always was.
REC = ("crop", "fertility", "broken", "last_crop", "last_kind", "fallow_since")
LAND = ("field", "pasture", "meadow")                                      # covers whose claims may name plots
SPLIT = ("seed", "area", "area_left", "broken", "weeded", "base", "left")  # a crop's quantities that go with its ground


def layout(claims, size) -> tuple:
    """(holders of the whole, {holder: plots} for those holding part), from the live claims on a parcel. One holder's part claims
    add up, to the parcel's plots at most; a holder with a claim of the whole holds the whole. Grants and claims for anyone hold no
    plots."""
    whole, part = [], {}
    for c in claims:
        if c.get("grounds") == "granted" or c["claimant"] == "anyone":
            continue
        if c.get("plots") is None:
            if c["claimant"] not in whole:
                whole.append(c["claimant"])
        else:
            part[c["claimant"]] = min(int(size), part.get(c["claimant"], 0) + int(c["plots"]))
    return whole, {h: n for h, n in part.items() if n > 0 and h not in whole}


def holdings(claims, size) -> dict:
    """{holder: plots} from the live claims on a parcel: a claim without plots covers all of them; one holder's claims add up, to
    the parcel's plots at most. Grants and claims for anyone hold no plots."""
    out = {}
    for c in claims:
        if c.get("grounds") == "granted" or c["claimant"] == "anyone":
            continue
        n = int(size) if c.get("plots") is None else int(c["plots"])
        out[c["claimant"]] = min(int(size), out.get(c["claimant"], 0) + n)
    return {h: n for h, n in out.items() if n > 0}


def shares(par) -> list:
    return par.get("shares") or []


def whole(par) -> list:
    """Those whose claims cover all of a field (its own record is theirs)."""
    return list(par.get("held_whole") or [])


def records(par) -> list:
    """[(holder, record)]: the parcel's own record first (holder None: the ground held whole, or the unclaimed plots), then each
    part holding's record."""
    return [(None, par)] + [(r["holder"], r) for r in shares(par)]


def record(par, holder):
    return par if holder is None else next((r for r in shares(par) if r["holder"] == holder), None)


def unclaimed(par) -> int:
    """The plots no claim covers, at least 0 (claims may overlap: a dispute)."""
    if whole(par):
        return 0
    return max(0, int(par["size"]) - sum(int(r["plots"]) for r in shares(par)))


def plots_of(par, holder) -> int:
    if holder is None:
        return int(par["size"]) if whole(par) else unclaimed(par)
    r = record(par, holder)
    return int(r["plots"]) if r else 0


def standing(par) -> list:
    """[(holder, record, crop)] for each crop on the field."""
    return [(h, r, r["crop"]) for h, r in records(par) if r.get("crop")]


def main_rec(par) -> tuple:
    """The holding that stands for the whole field where one is wanted (a view, the village's overview): the one with the most crop
    standing, else the one with the most plots."""
    st = [(h, r) for h, r, c in standing(par)]
    if st:
        return max(st, key=lambda hr: float(hr[1]["crop"].get("area_left", 0.0)))
    return max(records(par), key=lambda hr: plots_of(par, hr[0]))


def main_crop(par):
    return main_rec(par)[1].get("crop") if par.get("cover") == "field" else par.get("crop")


def view(par, holder) -> dict:
    """The field as one holding shows it: the parcel with that holding's crop and soil."""
    if holder is None:
        return par
    r = record(par, holder) or {}
    return {**par, **{k: r.get(k) for k in REC}}


def field_fertility(par) -> float:
    """The field's soil over all its plots (an export, a summary)."""
    parts = [(plots_of(par, h), float(r["fertility"])) for h, r in records(par) if plots_of(par, h) > 0]
    tot = sum(n for n, _ in parts)
    return round(sum(n * f for n, f in parts) / tot, 4) if tot else float(par.get("fertility", 1.0))


def named(par) -> bool:
    """Whether a field's holdings are told apart in words: more than one crop on it, or a holding of only part of it. A field held
    whole, by one claim or several, reads as before."""
    if par.get("cover") != "field":
        return False
    if len(standing(par)) > 1:
        return True
    size = int(par["size"])
    return any(0 < plots_of(par, h) < size for h, _ in records(par))


def who_words(names, x) -> str:
    """A holder in words: a household's name ("the Reeds"), else the person's."""
    return names.get(x, x) if x is not None else "nobody"


def short_words(names, x) -> str:
    return who_words(names, x).removeprefix("the ")


def possessive(names, x) -> str:
    w_ = who_words(names, x)
    return w_ + ("'" if w_.endswith("s") else "'s")


def owner(par, holder):
    """Who a record is: a part holder, the first holder of the whole, or None (the unclaimed plots)."""
    if holder is not None:
        return holder
    w_ = whole(par)
    return w_[0] if w_ else None


def the_crop(names, par, holder, c) -> str:
    """'the barley', or on a field held in shares 'the Reeds' barley' (the unclaimed plots' crop: 'the barley on the unclaimed plots')."""
    if not named(par):
        return f"the {c['kind']}"
    o = owner(par, holder)
    return f"the {c['kind']} on the unclaimed plots" if o is None else f"{possessive(names, o)} {c['kind']}"


def the_part(names, par, holder) -> str:
    """The field, or on a field held in shares one holding's part of it."""
    if not named(par):
        return par["name"]
    o = owner(par, holder)
    return f"the unclaimed part of {par['name']}" if o is None else f"{possessive(names, o)} part of {par['name']}"


def held_words(names, par, claims) -> str:
    """'Reeds 3, Webbs 2, Coles 1; 1 unclaimed' and the disputes ('the Wynns claim 2 of the Reeds' plots'), for a parcel whose claims
    name plots; '' for one held whole."""
    if not any(c.get("plots") is not None for c in claims):
        return ""
    size = int(par["size"])
    hold = holdings(claims, size)
    bits = [f"{short_words(names, h)} {n}" for h, n in hold.items()]
    free = max(0, size - sum(hold.values()))
    out = "held: " + ", ".join(bits) + (f"; {free} unclaimed" if free else "")
    for c in claims:
        if c.get("of") and c.get("over"):
            out += f"; {who_words(names, c['claimant'])} claim{'s' if c['claimant'] not in names else ''} {c['over']} of {possessive(names, c['of'])} plots"
    if sum(hold.values()) > size and not any(c.get("of") for c in claims):
        out += f" (disputed: {sum(hold.values())} claimed of {size})"
    return out


def crop_words(names, par) -> str:
    """'barley on 4 (Reeds 3, Webbs 1), beans on 1 (Coles), 1 fallow': what stands on a field, by holding where it is held in shares."""
    size = float(par["size"])
    kinds = {}
    for h, r, c in standing(par):
        if c.get("area_left", 0.0) <= 1e-6:
            continue
        kinds.setdefault(c["kind"], []).append((h, float(c["area"])))
    bits, used = [], 0.0
    for kind, parts in kinds.items():
        tot = sum(a for _, a in parts)
        used += tot
        who = ""
        if named(par):
            who = " (" + ", ".join((short_words(names, owner(par, h)) if owner(par, h) is not None else "unclaimed")
                                   + (f" {round(a, 1):g}" if len(parts) > 1 else "")
                                   for h, a in parts) + ")"
        bits.append(f"{kind} on {round(tot, 1):g}{who}")
    rest = size - used
    if bits and rest > 0.05:
        bits.append(f"{round(rest, 1):g} fallow")
    return ", ".join(bits)


def scale_crop(c, frac) -> dict:
    out = dict(c)
    for k in SPLIT:
        if k in out:
            out[k] = round(float(out[k]) * frac, 4)
    return out


def merge_crop(a, b) -> dict:
    out = dict(a)
    for k in SPLIT:
        if k in b:
            out[k] = round(float(out.get(k, 0.0)) + float(b[k]), 4)
    return out


def sync(w, pid, carry=False) -> None:
    """The holdings' records follow the claims (engine side: inside the claim primitives and the night). Plots lost go into a pool
    with their soil; plots gained are drawn from that pool first, then from the unclaimed ground, so fertility and broken ground
    follow the plots (D2-163). With `carry` (seeding, inheritance), a holding that lost all its plots hands its standing crop on to
    those who took them, split by plots; otherwise a crop stays with its sower's holding until reaped (the away-going crop), save
    that a holder of the whole who comes to hold only part keeps the crop it had on the whole."""
    par = w.s["parcels"][pid]
    if par.get("cover") != "field":
        return
    size = int(par["size"])
    w_new, new = layout(w.claims_on(("parcel", pid)), size)
    w_old = whole(par)
    recs = [dict(r) for r in shares(par)]
    old = {r["holder"]: int(r["plots"]) for r in recs}
    if w_new == w_old and {h: n for h, n in old.items() if n > 0} == new and all(int(r["plots"]) > 0 or r.get("crop") for r in recs):
        return
    by = {r["holder"]: r for r in recs}
    u0 = size if w_old else max(0, size - sum(old.values()))                    # the parcel's own record's plots before
    pool = []                                                                  # [holder, plots, fertility, broken, last_crop, last_kind]
    for r in recs:
        lost = int(r["plots"]) - new.get(r["holder"], 0)
        if lost > 0:
            b = round(float(r.get("broken") or 0.0) * lost / int(r["plots"]), 4)
            pool.append([r["holder"], lost, float(r["fertility"]), b, r.get("last_crop"), r.get("last_kind")])
            r["broken"] = round(float(r.get("broken") or 0.0) - b, 4)
            r["plots"] = new.get(r["holder"], 0)
    unc = [None, 0 if w_new else u0, float(par["fertility"]), float(par.get("broken") or 0.0), par.get("last_crop"), par.get("last_kind")]
    took = {}
    for h, n in new.items():
        gain = n - old.get(h, 0)
        if gain <= 0:
            continue
        r = by.get(h)
        if r is None:
            r = by[h] = {"holder": h, "plots": 0, "crop": None, "fertility": float(par["fertility"]), "broken": 0.0,
                         "last_crop": None, "last_kind": None, "fallow_since": par.get("fallow_since")}
            recs.append(r)
        got = []
        for src in pool + [unc]:
            k = min(gain, src[1])
            if k <= 0:
                continue
            b = src[3] * k / src[1]
            src[1] -= k
            src[3] -= b
            gain -= k
            got.append((k, src[2], b, src[4], src[5], src[0]))
            if gain <= 0:
                break
        if gain > 0:                                                           # plots others already hold (a dispute)
            got.append((gain, float(par["fertility"]), 0.0, par.get("last_crop"), par.get("last_kind"), "_held"))
        had = int(r["plots"])
        tot = had + sum(g[0] for g in got)
        r["fertility"] = round((had * float(r["fertility"]) + sum(g[0] * g[1] for g in got)) / tot, 4)
        r["broken"] = round(float(r.get("broken") or 0.0) + sum(g[2] for g in got), 4)
        if had == 0 and not r.get("last_crop"):
            r["last_crop"], r["last_kind"] = got[0][3], got[0][4]
        r["plots"] = n
        took[h] = got
    left = [s_ for s_ in pool if s_[1] > 0]                                    # what nobody took goes back to the parcel's own record
    if left:
        keep = size if w_new else unc[1]
        tot = keep + sum(s_[1] for s_ in left)
        par["fertility"] = round((keep * unc[2] + sum(s_[1] * s_[2] for s_ in left)) / tot, 4)
        if keep == 0:
            par["last_crop"], par["last_kind"] = left[0][4], left[0][5]
    if not w_new:
        par["broken"] = round(unc[3] + sum(s_[3] for s_ in left), 4)
    lost_own = u0 > 0 and not w_new and unc[1] == 0                             # the parcel's own record gave up all its plots
    if carry:                                                                  # crops carried with the plots (seeding, inheritance)
        srcs = [(r["holder"], r) for r in recs if int(r["plots"]) == 0 and old.get(r["holder"], 0) > 0] + ([(None, par)] if lost_own else [])
        for sh, sr in srcs:
            c = sr.get("crop")
            parts = [(h, g[0]) for h, gs in took.items() for g in gs if g[5] == sh]
            total = sum(k for _, k in parts)
            if not c or total <= 0:
                continue
            back = None
            for h, k in parts:
                piece = scale_crop(c, k / total)
                dst = by[h]
                if not dst.get("crop"):
                    dst["crop"] = piece
                elif dst["crop"].get("kind") == piece.get("kind"):
                    dst["crop"] = merge_crop(dst["crop"], piece)
                else:
                    back = piece if back is None else merge_crop(back, piece)
            sr["crop"] = back
    elif w_old and not w_new and par.get("crop"):                              # the whole's holder now holds part: its crop with it
        h = next((x for x in w_old if x in by), None)
        if h is not None and not by[h].get("crop"):
            by[h]["crop"], par["crop"] = par["crop"], None
    par["held_whole"] = list(w_new)
    par["shares"] = [by[h] for h in new] + [r for r in recs if r["holder"] not in new and r.get("crop")]


def seed_crops(w, pid, rows) -> None:
    """A world file's crops by holding (`state: {crops: [{holder, kind, left, ripe_day, plots?}]}`), after the claims are in."""
    par = w.s["parcels"][pid]
    for row in rows:
        h = row.get("holder")
        h = None if h in whole(par) else h
        rec = record(par, h)
        if rec is None:
            raise ValueError(f"{pid}: a crop for {h!r}, who holds no plots of it")
        fam = CROP_OF.get(str(row.get("kind", "grain")).lower(), "grain")
        area = float(row.get("plots", plots_of(par, h)))
        rec["crop"] = normalise_crop({**par, "size": area}, {**row, "area": area}, 0, grow_days(w.year_days(), fam))
        rec["crop"]["sower"] = row.get("sower", h)


def names_of(here_or_w) -> dict:
    """{household id: its name}, from a Here or the world."""
    if hasattr(here_or_w, "households"):
        return {iid: h["name"] for iid, h in here_or_w.households().items()}
    return {iid: h["name"] for iid, h in here_or_w.s["institutions"].items() if h.get("kind") == "household"}


def _mine(here, a, key=None) -> list:
    """Whose holdings are one's own: the party one acts for, else oneself and one's household, and any share held jointly with one."""
    if a.get("for"):
        from cybertron2.engine.verbs import _party
        return [_party(here, a["for"])]
    out = [x for x in (here.name, here.household()) if x]
    if key is not None:
        out += [c["claimant"] for c in here.claims(("parcel", key)) if here.name in (c.get("joint") or []) and c["claimant"] not in out]
    return out


def own_records(here, key, a) -> list:
    """The holders' keys of one's own records on a field, in order: one's part holdings, and the field's own record (None) where it
    is held whole by one's own."""
    par = here.parcels()[key]
    mine = _mine(here, a, key)
    out = [h for h in mine if record(par, h) is not None]
    if any(x in mine for x in whole(par)):
        out.append(None)
    return out


def on_holder(here, key, x):
    """The holding named by `on`: a household or a person holding plots of this field (or "unclaimed")."""
    par = here.parcels()[key]
    low = str(x or "").strip().lower().removeprefix("the ").removesuffix("'s").removesuffix("'").removesuffix(" plots")
    if low in ("unclaimed", "unclaimed plots", "nobody", "no one"):
        return None
    names = names_of(here)
    for h in [r["holder"] for r in shares(par)] + whole(par):
        nm = names.get(h, h).lower()
        if low in {h.lower(), h.lower() + "s", nm, nm.removeprefix("the ")}:
            return None if h in whole(par) else h
    held = ", ".join(who_words(names, h) for h in whole(par) + [r["holder"] for r in shares(par)])
    raise Refused(f"nobody called {x!r} holds plots of {par['name']}" + (f" (it is held by {held})" if held else " (nobody holds any of it)"))


def _why(here, par, holder, y, f) -> str:
    """'' if this field work can be done on this holding's plots now, else why not."""
    rec = record(par, holder) or {}
    c = rec.get("crop")
    names = names_of(here)
    part = the_part(names, par, holder)
    n = plots_of(par, holder)
    if y == "break":
        if c and (here.day >= int(c["ripe_day"]) or c["area"] >= n - 1e-6):
            return f"{part} has a crop in it"
        if float(rec.get("broken") or 0.0) + (c["area"] if c else 0.0) >= n - 1e-6:
            return f"{part} is broken and ready for sowing" if not c else f"the rest of {part} is broken and ready for sowing"
        return ""
    if y == "manure":
        return "" if n > 0 else f"there is no ground of {part} to manure"
    if not c or c["area_left"] <= 1e-6:
        return f"there is no ripe crop in {part} to choose seed from" if y == "select" else f"there is no crop in {part}"
    the = the_crop(names, par, holder, c)
    if y == "select":
        if here.day < int(c["ripe_day"]):
            return f"there is no ripe crop in {part} to choose seed from"
        if c.get("selected_by") == here.name:
            return f"you have chosen the seed from {part} already"
        return ""
    if c.get("failed") and c.get("shown_failed"):
        return f"{the} in {par['name']} has failed"
    if y == "crop" and here.day < int(c["ripe_day"]):
        return f"{the} in {par['name']} is not ripe yet"
    if y == "tend" and here.day >= int(c["ripe_day"]):
        return f"{the} in {par['name']} is ripe: past weeding"
    if y == "tend" and weed_gain(f, c.get("weeded", 0.0) / max(1e-9, c["area"])) >= float(f["weed_max"]) * 0.95:
        return f"{the} in {par['name']} is as clean as weeding makes it"
    return ""


def target(here, key, y, a, f):
    """Whose holding a field work falls on (D2-172): the one named by `on`; else one's own (the party's, one's own, one's
    household's) where one has one with something to work; else the unclaimed plots; else, where only one holding has work of
    this kind to do, that one (a field held whole by others, as before); else one must say whose."""
    par = here.parcels()[key]
    if a.get("on"):
        h = on_holder(here, key, a["on"])
        why = _why(here, par, h, y, f)
        if why:
            raise Refused(why)
        return h
    crop_work = y in ("crop", "tend", "select")
    relevant = (lambda h, r: bool(r.get("crop"))) if crop_work else (lambda h, r: plots_of(par, h) > 0)
    mine = own_records(here, key, a)
    recs = records(par)
    own = [(h, record(par, h)) for h in mine if relevant(h, record(par, h))]
    if own:
        for h, _ in own:
            if not _why(here, par, h, y, f):
                return h
        raise Refused(_why(here, par, own[0][0], y, f))
    rest = [(h, r) for h, r in recs if relevant(h, r) and h not in mine]
    ok = [h for h, _ in rest if not _why(here, par, h, y, f)]
    if None in ok:
        return None
    if len(ok) == 1:
        return ok[0]
    if not ok:
        if rest:
            raise Refused(_why(here, par, rest[0][0], y, f))
        raise Refused(f"there is no crop in {par['name']}" if crop_work else f"there is no ground of {par['name']} to work")
    names = names_of(here)
    raise Refused(f"more than one holding in {par['name']} could be worked so: say whose with \"on\" ("
                  + ", ".join(who_words(names, h) for h in ok) + ")")


def against(here, key, holder) -> str:
    """Working another's holding is allowed and seen (D2-172): the words for it ('' for one's own or the unclaimed plots)."""
    o = owner(here.parcels()[key], holder)
    if o is None or holder in own_records(here, key, {}):
        return ""
    return f" on {possessive(names_of(here), o)} plots"


def _set(here, key, holder, field, value):
    here.apply("set_share", parcel=key, holder=holder, field=field, value=value)


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
    if k in ("select", "break", "tend", "manure", "crop"):                      # on whose holding (D2-172)
        h = target(here, key, k, a, f)
        a["_on"] = h
        par = here.parcels()[key]
        names = names_of(here)
    if k == "select":
        c = dict(record(par, h)["crop"])
        c["selected_by"] = here.name
        _set(here, key, h, "crop", c)
        return 0.0, None, f"You went through {the_crop(names, par, h, c)} in {place_name}, marking the best ears to keep for seed.", ("parcel", key)
    if k == "break":
        return _break(here, tech, key, place_name, out, m * tm, f, h)
    if k == "tend":
        c = dict(record(par, h)["crop"])
        c["weeded"] = round(c.get("weeded", 0.0) + m, 4)
        c["left"] = crop_left(f, c)
        _set(here, key, h, "crop", c)
        return 0.0, None, f"You weeded {the_crop(names, par, h, c)} in {place_name}: it will bear more.", ("parcel", key)
    if k == "manure":
        rec = record(par, h)
        n = float(plots_of(par, h))
        plots = min(n, float(y["plots"]) * m)
        fert = rec["fertility"]
        r, level = f["manure"]
        new = round(fert + float(r) * max(0.0, float(level) - fert) * plots / max(1.0, n), 4)
        _set(here, key, h, "fertility", new)
        return 0.0, None, f"You spread dung on {the_part(names, par, h)}: the soil will be the better for it.", ("parcel", key)
    if k == "crop":
        return _reap(here, tech, key, place_name, out, m * tm, f, y, h)
    if k == "herd":
        hid = _herd_on(here, key, a)
        here.apply("set", ref=("herd", hid), field="watched", value=here.day)
        hd = here.herds()[hid].get("herders") or {}
        n = int(hd.get("n", 0)) + 1 if hd.get("day") == here.day else 1        # herders today: each holds about 30 head (D2-128)
        who = (list(hd.get("by") or []) if hd.get("day") == here.day else []) + [here.name]   # who, for the next one's refusal (D4-95)
        here.apply("set", ref=("herd", hid), field="herders", value={"day": here.day, "n": n, "by": who})
        return 0.0, None, f"You watched {here.herds()[hid]['name']} on {place_name} today.", ("herd", hid)
    if k == "milk":
        hid = _herd_on(here, key, a, role="cows")
        h = here.herds()[hid]
        mk = h["milked"] if h["milked"]["day"] == here.day else {"day": here.day, "n": 0}
        n = min(int(y["cows"]), int(round(h.get("in_milk", 0.0))) - mk["n"])
        here.apply("set", ref=("herd", hid), field="milked", value={"day": here.day, "n": mk["n"] + n,
                                                                    "by": list(mk.get("by") or []) + [here.name]})
        return round(n * float(y["each"]) * m, 2), "milk", "", ("herd", hid)
    if k == "slaughter":
        return _slaughter(here, key, out, a, y)
    raise Refused(f"{tech} cannot be done that way")


def _herd_on(here, key, a, role=None):
    hs = [hid for hid, h in here.herds().items() if h["parcel"] == key and head(h) > 0 and (role is None or int(h.get(role, 0)) > 0)]
    want = str(a.get("thing") or "").strip().lower()
    pick = next((hid for hid in hs if want and (want in (hid.lower(), here.herds()[hid]["name"].lower())
                                                or want == str(here.herds()[hid].get("tag") or "").lower())), None)
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
    worth = float(y["worth"])
    ps = float(f["plot_seed"])
    targets = sow_targets(here, key, a)
    phys = float(par["size"]) * ps - sum(float(c["seed"]) for _, _, c in standing(par))   # the field's ground, all holdings
    cap = float(a["plots"]) * ps if a.get("plots") not in (None, "") else float("inf")
    from cybertron2.engine.verbs import _party, _src
    extra = _src(here, _party(here, a["for"]) if a.get("for") else None, out)
    have = KN.available(here, seed_good, extra=extra)
    want = min(float(y["seed"]) * m, have)
    names = names_of(here)
    parts, why = [], ""
    for h in targets:                                                          # one's own unsown plots, then the unclaimed (D2-172)
        rec = record(par, h)
        c = rec.get("crop")
        if c and (c["crop"] != fam or here.day >= c["ripe_day"]):
            why = why or f"{the_part(names, par, h)} already has {c['kind']} in it"
            continue
        if plots_of(par, h) <= 0 and not c:
            continue
        room = min(plots_of(par, h) * ps - (c["seed"] if c else 0.0), phys, cap)   # in plot-seed equivalents
        seed = round(min(want, room / worth), 2)
        if seed <= 1e-9:
            why = why or (f"you have no {seed_good} to sow" if room > 1e-9 else f"{the_part(names, par, h)} is sown as thick as it will take")
            continue
        parts.append((h, seed))
        want -= seed
        phys -= seed * worth
        cap -= seed * worth
        if want <= 1e-9:
            break
    if not parts:
        raise Refused(why or _sow_why(here, key, a) or f"{par['name']} is sown as thick as it will take")
    from cybertron2.engine.verbs import _consume
    _consume(here, {seed_good: round(sum(s for _, s in parts), 2)}, extra=extra)
    year = here.year_days()
    words = []
    for h, seed in parts:
        rec = record(par, h)
        c = rec.get("crop")
        if c is None:
            last = rec.get("last_crop")
            fail = f["fail"][1] if last == fam else f["fail"][0]
            salt = () if h is None or plots_of(par, h) >= int(par["size"]) else (h,)   # a field held whole draws as before
            failed = here.rng("blight", here.day, key, *salt).random() < float(fail)
            g = grow_days(year, fam)
            if KN.level(mind, "select seed") == "known":                      # seed selection (D2-65)
                g = max(2, round(g * float(here.p["seed_selection"])))
            name = next((n for n in CROPS[fam]["names"] if n == str(rec.get("last_kind", "")).lower()), CROPS[fam]["names"][0])
            c = {"kind": name, "crop": fam, "sown": here.day, "ripe_day": here.day + g, "window": int(f["window"]), "seed": 0.0, "area": 0.0,
                 "area_left": 0.0, "broken": 0.0, "weeded": 0.0, "base": 0.0, "rot": 1.0, "failed": failed, "hardy": CROPS[fam]["hardy"],
                 "sower": a.get("for") or here.name}
        c = dict(c)
        eq = seed * worth
        area = eq / ps
        broken_here = min(float(rec.get("broken") or 0.0), area)
        if broken_here > 0:
            _set(here, key, h, "broken", round(float(rec.get("broken") or 0.0) - broken_here, 4))
        ratio = float(f["ratio"]) + float(f["break_gain"]) * (broken_here / area)
        c["seed"] = round(c["seed"] + eq, 4)
        c["area"] = round(c["area"] + area, 4)
        c["area_left"] = round(c["area_left"] + area, 4)
        c["broken"] = round(c["broken"] + broken_here, 4)
        skill_yield = 1 + float(here.p["master_yield"]) * master_share(here, mind, tech)       # D2-64
        c["base"] = round(c["base"] + eq * ratio * float(rec["fertility"]) * ground_mult(here.p, par) * skill_yield, 4)
        c["left"] = crop_left(f, c)
        _set(here, key, h, "crop", c)
        words.append((h, seed, area, broken_here, c))
    if a.get("on"):
        a["_on"] = parts[0][0]
    how = mods.get("word") or "sowed"
    seed = round(sum(s for _, s in parts), 2)
    area = sum(x[2] for x in words)
    c = words[0][4]
    soil = " on broken ground" if any(x[3] > 0 for x in words) else ""
    where = ""
    if named(par):
        own = set(own_records(here, key, a))
        where = " (" + ", ".join(f"{show(x[2])} on " + ("your plots" if x[0] in own else "the unclaimed plots" if owner(par, x[0]) is None
                                                         else f"{possessive(names, owner(par, x[0]))} plots") for x in words) + ")"
    word = (f"You {how} {show(seed)} {seed_good} in {place_name}{soil} (about {show(area)} of a plot){where}; the {c['kind']} should be "
            f"ready to reap in about {c['ripe_day'] - here.day} days.")
    if not c["hardy"]:
        word += " It is not hardy: winter will kill it if it is still growing."
    return 0.0, None, word, ("parcel", key)


def sow_targets(here, key, a) -> list:
    """Whose plots a sowing falls on (D2-172): those named by `on` (another's: allowed, and seen); else one's own (the party's, or
    one's own and one's household's) that are unsown, then the unclaimed plots."""
    par = here.parcels()[key]
    if a.get("on"):
        return [on_holder(here, key, a["on"])]
    mine = [h for h in own_records(here, key, a) if plots_of(par, h) > 0]
    return mine + ([None] if None not in mine and not whole(par) else [])


def _sow_why(here, key, a) -> str:
    """'' if there is ground this sowing could take (any seed), else why not."""
    par = here.parcels()[key]
    f = here.p["farming"]
    names = names_of(here)
    ps = float(f["plot_seed"])
    phys = float(par["size"]) * ps - sum(float(c["seed"]) for _, _, c in standing(par))
    try:
        targets = sow_targets(here, key, a)
    except Refused as e:
        return str(e)
    why = ""
    for h in targets:
        c = record(par, h).get("crop")
        n = plots_of(par, h)
        if c and here.day >= c["ripe_day"]:
            why = why or f"{the_part(names, par, h)} has {c['kind']} standing in it"
            continue
        if n <= 0 and not c:
            continue
        if c and c["seed"] >= n * ps - 1e-6 or phys <= 1e-6:
            why = why or f"{the_part(names, par, h)} is sown as thick as it will take"
            continue
        return ""
    if why:
        return why
    held = whole(par) + [h for h, _ in records(par) if h is not None and plots_of(par, h) > 0]
    return (f"{par['name']} is all held by {', '.join(who_words(names, h) for h in held)}: to sow their plots, say whose with \"on\""
            if held else f"{par['name']} is sown as thick as it will take")


def _break(here, tech, key, place_name, out, mult, f, h=None):
    par = here.parcels()[key]
    rec = record(par, h)
    y = TECHNIQUES[tech]["yield"]
    sown = float((rec.get("crop") or {}).get("area", 0.0))                     # break only the ground not yet sown
    room = float(plots_of(par, h)) - float(rec.get("broken") or 0.0) - sown
    plots = round(min(room, float(y["plots"]) * mult), 4)
    if plots <= 1e-9:
        raise Refused(f"{the_part(names_of(here), par, h)} is already broken and ready for sowing")
    _set(here, key, h, "broken", round(float(rec.get("broken") or 0.0) + plots, 4))
    stone = round(float(y.get("stone", 0.0)) * plots, 2)
    if stone > 0:
        here.apply("create", dst=out, item="stone", qty=stone, why="fieldstone")          # D2-56
    for item, n in (TECHNIQUES[tech].get("uses") or {}).items():
        if ITEMS[item].get("life"):
            src = next((cid for cid in here.takeable() if here.contents(cid).get(item, 0) >= 1), None)
            if src:
                here.apply("wear", container=src, item=item, uses=plots if item == "wooden plough" else 1.0 / n)
    how = "ploughed" if tech == "plough" else "hoed"
    left = float(plots_of(par, h)) - float(rec.get("broken") or 0.0) - plots     # the holding's ground (D2-172)
    where = the_part(names_of(here), par, h) if named(par) else place_name
    word = f"You {how} {show(plots)} of a plot of {where}" + (f", turning up {show(stone)} stone" if stone >= 0.05 else "")
    word += "; the field is ready for sowing." if left <= 1e-6 else f"; {show(left)} plots still unbroken."
    return 0.0, None, word, ("parcel", key)


def _reap(here, tech, key, place_name, out, mult, f, y, h=None):
    """Reaping a holding's crop: the grain goes to the reaper, whoever's plots it stood on (production.md: a crop is nobody's until
    reaped; D2-172)."""
    par = here.parcels()[key]
    names = names_of(here)
    c = dict(record(par, h)["crop"])
    if c.get("failed") and c.get("shown_failed"):
        raise Refused(f"{the_crop(names, par, h, c)} in {place_name} has failed: there is nothing to reap")
    plots = min(c["area_left"], float(y["plots"]) * mult)
    left = crop_left(f, c)
    got = round(left * plots / max(1e-9, c["area_left"]), 2)
    here.apply("draw", parcel=key, key="crop", qty=got, **({"holder": h} if h is not None else {}))
    c = dict(record(here.parcels()[key], h)["crop"])                           # the draw took its ground with it (world.p_draw)
    c["left"] = crop_left(f, c)
    _set(here, key, h, "crop", c)
    gives = CROPS[c["crop"]]["gives"]
    straw = round(float(y.get("straw", 0.0)) * plots, 2) if CROPS[c["crop"]]["straw"] else 0.0
    if straw > 0:
        here.apply("create", dst=out, item="straw", qty=straw, why="reap")
    word = ""
    if c["area_left"] <= 1e-6:
        word = f" {the_part(names, par, h)} is reaped." if named(par) else f" {place_name} is reaped."
    return got, gives, word, ("parcel", key)


def _slaughter(here, key, out, a, y):
    hid = _herd_on(here, key, a)
    h = here.herds()[hid]
    want = ROLE_OF.get(str(a.get("item") or "").lower().strip()) or ROLE_OF.get(str(a.get("thing") or "").lower().strip())
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
    rec = here.parcels()[key].get("slaughter") or {}                          # the day's kills on this ground, for its signs (D4-71)
    kills = list(rec.get("kills") or []) if rec.get("day") == here.day else []
    kills.append({"beast": ROLE_WORD[role][0], "herd": h["name"], "by": here.name})
    here.apply("set", ref=("parcel", key), field="slaughter", value={"day": here.day, "kills": kills})
    word =f"You slaughtered a {ROLE_WORD[role][0]} of {h['name']}: " + ", ".join(f"{q:g} {i}" for i, q in gives.items()) + "."
    return 0.0, None, word, ("herd", hid)


def ready(here, tech, key, a=None) -> str:
    """'' if this farming or cattle work can be done on this parcel now (on the holding it would fall on: D2-172), else why not."""
    t = TECHNIQUES[tech]
    y = t["yield"]["kind"]
    p = here.parcels()[key]
    f = here.p["farming"]
    a = a or {}
    if t.get("seasons") and here.calendar()["season"] not in t["seasons"]:
        return f"{KN.label(tech)} is done in {' and '.join(t['seasons'])}"
    if y == "sow" and p["cover"] == "field":
        return _sow_why(here, key, a)
    if y in ("break", "crop", "tend", "manure") and p["cover"] == "field":
        try:
            target(here, key, y, a, f)
        except Refused as e:
            return str(e)
    if y == "break":
        why = team_shortfall(here, t)
        if why:
            return why
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
        try:
            target(here, key, y, a, f)
        except Refused as e:
            return str(e)
    if y in ("herd", "milk", "slaughter"):
        hs = [h for h in here.herds().values() if h["parcel"] == key and head(h) > 0]
        if not hs:
            return f"there are no beasts on {p['name']}"
        if y == "milk":
            n = sum(int(round(h.get("in_milk", 0.0))) - (h["milked"]["n"] if h["milked"]["day"] == here.day else 0) for h in hs)
            if n <= 0:
                by = sorted({x for h in hs if h["milked"]["day"] == here.day for x in h["milked"].get("by") or []})
                return "no cow there is in milk" if not any(h.get("in_milk", 0) >= 0.5 for h in hs) else \
                    "the cows in milk are milked today" + (f": {_names(by)} milked them" if by else "")
        if y == "herd" and all(h.get("watched") == here.day and head(h) <= herd_capacity(here.p, h, here.day) for h in hs):
            by = sorted({x for h in hs if (h.get("herders") or {}).get("day") == here.day for x in (h["herders"].get("by") or [])})
            return "the beasts there are watched today" + (f": {_names(by)} {'is' if len(by) == 1 else 'are'} watching them" if by else "")
    return ""


def _names(xs) -> str:
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]


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
    if here.parcels()[to]["cover"] not in ("pasture", "meadow", "field", "scrub", "forest", "built", "heath", "moor", "fen", "saltmarsh"):
        raise Refused(f"beasts cannot be kept on {here.parcels()[to]['name']}")
    if here.calendar()["season"] == "winter":                                  # housed in stalls: not driven off without coming in
        from cybertron2.engine import buildings as BL
        mine = {c["claimant"] for c in here.claims(("herd", hid))}
        held = {bid: b for bid, b in here.buildings().items() if mine & {c["claimant"] for c in here.claims(("building", bid))}}
        share, bid = BL.stall_share(h, held, head(h))
        if share > 0 and not here.can_enter(bid):
            raise Refused(f"{h['name']} are in the stalls of {here.buildings()[bid]['name']}, behind its barred door")
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
        if h.get("with"):                                                    # a led beast turned out: let go there (D2-136)
            for f in ("with", "pack"):
                here.apply("set", ref=("herd", hid), field=f, value=None)
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
    here.apply("set", ref=("herd", moved_to), field="driven", value={"day": here.day, "from": h["parcel"], "to": to, "by": here.name})
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
    from cybertron2.engine import layout as LY
    LY.regrow(w)                                                             # hidden ways grow back unused (D2-92)
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


def _crops(w, rec_):
    _works_night(w, rec_)
    f = w.p["farming"]
    year = w.year_days()
    winter = w.calendar()["season"] == "winter"
    slot = grow_days(year, "grain")
    names = names_of(w)
    for pid, par in w.s["parcels"].items():
        if par["cover"] != "field":
            continue
        node = par["node"]
        if layout(w.claims_on(("parcel", pid)), par["size"]) != (whole(par), {r["holder"]: int(r["plots"]) for r in shares(par) if int(r["plots"]) > 0}):
            w.apply("shares", node, parcel=pid)                                # a claim ran out: the holdings follow (D2-163)
        grazed = any(h["parcel"] == pid and head(h) > 0 for h in w.s["herds"].values())
        gone = False
        for hd, rec in records(par):                                           # a crop for each holding (D2-172)
            c = rec.get("crop")
            if c:
                c = dict(c)
                the = the_crop(names, par, hd, c)
                growing = w.d < int(c["ripe_day"])
                if growing and c.get("failed") and not c.get("shown_failed") and w.d >= c["sown"] + (c["ripe_day"] - c["sown"]) // 2:
                    c["shown_failed"] = True
                    w.event(node, "crop", f"{the} in {par['name']} has blight: it is withering and will bear nothing",
                            about=[f"parcel:{pid}"], salience=0.6, tags=["farming", "food"])
                    rec_["crops"].append((pid, "failed"))
                if growing and winter and not c.get("hardy"):
                    c["area_left"] = 0.0
                    c["killed"] = True
                    w.event(node, "crop", f"the frost has killed {the} growing in {par['name']}", about=[f"parcel:{pid}"],
                            salience=0.7, tags=["farming", "food", "season"])
                    rec_["crops"].append((pid, "frost"))
                elif w.d >= int(c["ripe_day"]) + int(c.get("window", f["window"])):
                    c["rot"] = round(c.get("rot", 1.0) * (1 - float(f["rot"])), 4)
                    c["rotting"] = True
                c["left"] = crop_left(f, c)
                withering = c.get("failed") and growing                         # a blighted crop stands until its day
                if c["area_left"] <= 1e-6 or (c["left"] <= 0.05 and not withering):
                    fert = soil_step(f, rec["fertility"], c["crop"])           # the crop's slot ends (D4-39)
                    w.apply("set_share", node, parcel=pid, holder=hd, field="fertility", value=fert)
                    w.apply("set_share", node, parcel=pid, holder=hd, field="last_crop", value=c["crop"])
                    w.apply("set_share", node, parcel=pid, holder=hd, field="last_kind", value=c["kind"])
                    w.apply("set_share", node, parcel=pid, holder=hd, field="crop", value=None)
                    w.apply("set_share", node, parcel=pid, holder=hd, field="fallow_since", value=w.d)
                    gone = gone or (hd is not None and int(rec["plots"]) <= 0)
                else:
                    w.apply("set_share", node, parcel=pid, holder=hd, field="crop", value=c)
            elif not grazed and plots_of(par, hd) > 0:                         # resting: fallow restores (grazed: in _herds)
                d = 1 - (1 - float(f["fallow"])) ** (1 / slot)
                fert = round(rec["fertility"] + d * max(0.0, 1.0 - rec["fertility"]), 4)
                w.apply("set_share", node, parcel=pid, holder=hd, field="fertility", value=fert)
        if gone:
            w.apply("shares", node, parcel=pid)                                # a holding with no plots left and its crop gone


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
        stalled = 0.0
        if winter:                                                             # housed in stalls in winter (D2-45; 02zh §4)
            from cybertron2.engine import buildings as BL
            mine = {c["claimant"] for c in w.claims_on(("herd", hid))}
            held = {bid: b for bid, b in w.s["buildings"].items() if b["node"] == node
                    and mine & {c["claimant"] for c in w.claims_on(("building", bid))}}
            stalled, _ = BL.stall_share(h, held, n)
            need *= 1 - stalled * (1 - float(FITTINGS["stalls"]["fodder"]))
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
            from cybertron2.engine import things as TH                         # it lies where it fell (D4-52)
            TH.leave_carcass(w, node, ROLE_WORD[role][0], h["name"], [c["claimant"] for c in w.claims_on(("herd", hid))], "starved",
                             TECHNIQUES["slaughter"]["yield"]["gives"][role], parcel=pid)
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
        dS = (par["res"].get("dung") or {}).get("S", 0.0)                       # dung where they stand
        kept = 1 + stalled * (float(FITTINGS["stalls"]["dung"]) - 1)             # dung kept in the stalls (D2-45)
        w.apply("set_res", node, parcel=pid, key="dung", fields={"S": round(dS + n * float(cp["dung"]) * kept / year, 4)},
                init={"S": 0.0, "K": 1e9, "r": 0.0})
        if par["cover"] == "field":                                            # grazed stubble and fallow (D4-39), holding by holding
            r, level = f["grazed"]
            dd = 1 - (1 - float(r)) ** (1 / slot)
            for hd, rc in records(par):
                if not rc.get("crop") and plots_of(par, hd) > 0:
                    w.apply("set_share", node, parcel=pid, holder=hd, field="fertility",
                            value=round(rc["fertility"] + dd * max(0.0, float(level) - rc["fertility"]), 4))
        w.apply("set", node, ref=("herd", hid), field="count", value=head(w.s["herds"][hid]))
