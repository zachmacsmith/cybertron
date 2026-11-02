"""Economic checks a world must pass before a run, so nobody starts bound to starve (Zach, 2 Nov; evidence in review 02zk, the
published cybertron2 runs). For any world file with people, hand-made or generated:

    python -m cybertron2.landgen.economy <world.yaml>

Each check is a heuristic read off what failed before (validated on the 48 published runs: review 02zl):
- region food and heat: what the land keeps for good (capacity.py's flows) against everyone living there: a warning, as a run may
  end before the land's shortfall arrives.
- food and heat over the run: what the run's days need against store, crops ripening within it, milk, the wild's standing food and
  the land's flows for those days; heat refuses only when even the woods standing could not cover it.
- a village's carrying burden: the people a short village must keep on the road every day to fetch what its land lacks. Villages
  needing about a quarter of their people carrying (Coppergate in r1 and w3, Hollins in h1 and h2) lost people.
- households' runway: food in store a member against the days to their own harvest. Early missed meals came from the households
  that started with under two days' food (the Lowes and Hales, the Smiths, the Newcomes): it predicts missed meals, not deaths.
- succession: someone a household leans on dies of age within the run (c2_combe).
- fuel, cooking and growth: fuel in store a hearth against the nights until its woods are worked; food that needs a fire against the
  fuel to cook it (w3: grain beside cold hearths); room to grow (c2_combe: births outran the land).
Levels: `refuse` (the world should not run as it is) or `warn` (a designed hardship, or a risk to watch). Thresholds are data
(THRESHOLDS), first values from the runs, to calibrate.
"""
from __future__ import annotations

import copy
import io
import contextlib
import sys

import yaml

from cybertron2.engine import capacity as CAP
from cybertron2.engine.data import ITEMS

THRESHOLDS = {
    "region_share_refuse": 1.0,     # people / what the land keeps: above this, the region cannot feed itself in a year
    "region_share_warn": 0.85,
    "burden_refuse": 0.12,          # carriers on the road a day / the village's people: every past village at 0.13 or more failed;
    "burden_warn": 0.04,            # ... no past run had a short village that held, so below 0.13 is not yet calibrated (02zl)
    "runway_days": 3.0,             # a household with less food a member than this, and no harvest of its own sooner, will go hungry
    "runway_people_warn": 0.2,      # ... warn when such households hold this share of everyone (missed meals, not deaths: 02zl)
    "fuel_nights": 3.0,             # fuel in store a hearth, where the node has no wood of its own
    "run_refuse": 1.0,              # what the run needs / what store, standing crops and the land's flow give in its days
    "run_warn": 0.85,
}
CARRY = {"foot": 10, "pack": 20, "pack ox": 60}


def _world(spec: dict):
    from cybertron2.engine.world import World
    with contextlib.redirect_stdout(io.StringIO()):
        return World(copy.deepcopy(spec))


def _home_node(w, n):
    h = w.homes(n)
    return w.s["buildings"][h[0]]["node"] if h else w.s["people"][n].get("at")


def _eaters(w, folk) -> float:
    young = sum(1 for n in folk if w.s["people"][n].get("stage") in ("infant", "child"))
    return len(folk) - young + 0.6 * young


def _herd_node(w, h):
    return h.get("node") or (w.s["parcels"].get(h.get("parcel")) or {}).get("node")


def _container_node(w, c):
    if c.get("kind") == "hands":
        return (w.s["people"].get(c.get("of")) or {}).get("at")
    for b in w.s["buildings"].values():
        if c is w.s["containers"].get(b.get("stock")):
            return b["node"]
    return (w.s["parcels"].get(c.get("parcel")) or {}).get("node") or c.get("node")


def _stock(w, key, nid=None) -> float:
    """Food (meals) or heat in every store and every pair of hands (of a node, if given)."""
    return sum(float(q) * float((ITEMS.get(i) or {}).get(key, 0.0) or 0.0)
               for c in w.s["containers"].values() if nid is None or _container_node(w, c) == nid
               for i, q in (c.get("goods") or {}).items())


def run_balance(w, days: int, nid=None, folk=None) -> dict:
    """What the run's days need against what they can have: store, crops standing that ripen within the run, and the land's flows
    for the days (woods' forage and firewood at any time; fields' flow only past a year, as unsown fields give nothing sooner).
    The yearly check says whether the land can keep its people; this says whether the shortfall arrives before the run ends."""
    year = w.year_days()
    if folk is None:
        folk = [n for n, a in w.s["people"].items() if a.get("alive", True)]
    pars = [p for p in w.s["parcels"].values() if nid is None or p["node"] == nid]
    need_food = _eaters(w, folk) * days
    crops = sum(float((p.get("crop") or {}).get("left", 0.0)) for p in pars
                if (p.get("crop") or {}).get("ripe_day") is not None and int(p["crop"]["ripe_day"]) <= w.d + days)
    woods = sum(p["size"] for p in pars if p["cover"] in ("forest", "scrub"))
    fields = sum(p["size"] for p in pars if p["cover"] == "field")
    grain = float(ITEMS["grain"]["food"])
    # the wild's standing plants and game, and the cows in milk (a milking a day: data TECHNIQUES milk, 1.6 a cow), which yearly
    # capacity leaves out; w1 and w2 lived on them through runs their crops and store alone would not have fed
    wild = sum(float((p["res"].get("plants") or {}).get("S", 0)) * float(ITEMS["wild food"]["food"])
               + float((p["res"].get("game") or {}).get("S", 0)) * float(ITEMS["meat"]["food"])
               for p in pars if isinstance(p.get("res"), dict))
    herds = [h for h in w.s["herds"].values() if nid is None or _herd_node(w, h) == nid]
    milk = sum(int(h.get("in_milk", 0)) for h in herds) * 1.6 * float(ITEMS["milk"]["food"]) * days
    have_food = _stock(w, "food", nid) + crops * grain + wild + milk + woods * CAP.WILD * days / year \
        + fields * (CAP.PLOT["grain"] - CAP.PLOT["seed"]) * grain * max(0, days - year) / year
    hearths = max(1, -(-len(folk) // int(CAP.PEOPLE_A_HEARTH)))                # households keep a fire each; about 4.5 to a hearth
    homes = {h for n in folk for h in w.homes(n) if (w.s["buildings"][h].get("fittings") or {}).get("hearth")}
    hearths = max(hearths if not homes else 0, len(homes))
    cold = sum(1 for d in range(w.d, w.d + days) if w.cold(d))
    hp = w.p["heat"]
    need_heat = hearths * ((days - cold) * float(hp["normal"]) + cold * float(hp["cold"]))
    have_heat = _stock(w, "heat") + sum(CAP.wood_flow(p) for p in w.s["parcels"].values()) * CAP.FIREWOOD_HEAT * days / year
    # what the woods stand at: dead wood and young growth as firewood, trees as timber. A run may burn into them (the hearths of
    # a2, c1 and w1 stayed lit on less flow than they burned); it cannot burn more than stands
    standing = sum(float((p["res"].get("dead") or {}).get("S", 0)) * float(ITEMS["firewood"]["heat"])
                   + float((p["res"].get("young") or {}).get("S", 0)) * float(ITEMS["firewood"]["heat"])
                   + float((p["res"].get("wood") or {}).get("S", 0)) * float(ITEMS["timber"]["heat"])
                   for p in w.s["parcels"].values() if isinstance(p.get("res"), dict))
    return {"food": (need_food, have_food), "heat": (need_heat, have_heat), "heat_standing": standing, "cold_nights": cold,
            "hearths": hearths}


def check(spec: dict) -> dict:
    """The economic checks of a world with people: {name: {level, ok, detail}}; level is the severity if the check fails."""
    T = THRESHOLDS
    out = {}
    if not spec.get("agents"):
        return {"people": {"level": "warn", "ok": False, "detail": "no people: the economic checks need them (generate with --people)"}}
    w = _world(spec)
    people = {nid: [] for nid in w.s["nodes"]}
    for n in w.s["people"]:
        people.setdefault(_home_node(w, n), []).append(n)
    caps = {nid: CAP.node(w, nid) for nid in w.s["nodes"]}
    P = sum(len(v) for v in people.values())
    food = sum(c["food_people"] for c in caps.values())
    heat = sum(c["heat_people"] for c in caps.values())
    days = int(spec.get("days", 0))
    year = w.year_days()
    sd = w.season_len
    cal = spec.get("calendar") or {}
    to_winter = max(0, {"spring": 2 * sd, "summer": sd, "autumn": 0}.get(cal.get("season", "summer"), 0) + sd - int(cal.get("day", 1)) + 1) \
        if cal.get("season", "summer") != "winter" else 0
    rb = run_balance(w, days)
    for key, kept in (("food", food), ("heat", heat)):
        share = P / max(kept, 1e-9)
        need, have = rb[key]
        rshare = need / max(have, 1e-9)
        out[f"region {key}"] = {"level": "warn", "ok": share <= T["region_share_warn"],
                                "detail": f"{P} people; the land keeps {kept:.0f} for good ({share:.2f} of it)"}
        if key == "food":
            out["food over the run"] = {"level": "refuse" if rshare > T["run_refuse"] else "warn", "ok": rshare <= T["run_warn"],
                                        "detail": f"{days} days need {need:.0f} meals; store, crops ripening and the land give {have:.0f} "
                                                  f"({rshare:.2f})"}
        else:                                       # the flow short: a warning (they burn into the woods); the woods short: refuse
            all_ = have + rb["heat_standing"]
            out["heat over the run"] = {"level": "refuse" if need > all_ * T["run_refuse"] else "warn", "ok": rshare <= T["run_warn"],
                                        "detail": f"{days} days need {need:.0f} heat ({rb['hearths']} hearths, {rb['cold_nights']} cold "
                                                  f"nights); store and the woods' flow give {have:.0f} ({rshare:.2f}); the woods stand "
                                                  f"at {rb['heat_standing']:.0f} more"}
    # each village short of food or fuel: who must be on the road each day to fetch it, on foot or by the best beast it holds. Food
    # is the yearly shortfall (the land's flow against its people: r1, w3, v3, Hollins); fuel is the run's (store, the woods' flow
    # and the woods standing in the village against its hearths: wb2, where the region's woods were a day off and 11 of 14 died,
    # 38.49), carried as timber, the lightest heat to carry
    def node_of_herd(h):
        par = w.s["parcels"].get(h.get("parcel")) or {}
        return h.get("node") or par.get("node")

    def node_heat(nid):
        pars = [p for p in w.s["parcels"].values() if p["node"] == nid]
        store = sum(float(q) * float((ITEMS.get(i) or {}).get("heat", 0.0) or 0.0)
                    for b in w.s["buildings"].values() if b["node"] == nid
                    for i, q in ((w.s["containers"].get(b.get("stock")) or {}).get("goods") or {}).items())
        flow = sum(CAP.wood_flow(p) for p in pars) * CAP.FIREWOOD_HEAT * days / year
        stand = sum(float((p["res"].get("dead") or {}).get("S", 0)) * float(ITEMS["firewood"]["heat"])
                    + float((p["res"].get("young") or {}).get("S", 0)) * float(ITEMS["firewood"]["heat"])
                    + float((p["res"].get("wood") or {}).get("S", 0)) * float(ITEMS["timber"]["heat"])
                    for p in pars if isinstance(p.get("res"), dict))
        return store + flow + stand

    hp = w.p["heat"]
    cold_n = sum(1 for d in range(w.d, w.d + days) if w.cold(d))
    night = ((days - cold_n) * float(hp["normal"]) + cold_n * float(hp["cold"])) / max(days, 1)
    timber_weight = float(ITEMS["timber"]["weight"]) / float(ITEMS["timber"]["heat"])
    burdens = {}
    for nid, folk in people.items():
        if not folk:
            continue
        # the food short is the yearly flow's, not the run's: counting the store and the wild's standing food as the run's to eat
        # (run_balance by node) missed five of the ten failures (b1_wild, f1, h2, wb1, c2), as people do not live off a stock
        # they must gather and share; the land's flow against its people caught nine (02zl §3)
        deficit = max(0.0, len(folk) - caps[nid]["food_people"])
        need, have = run_balance(w, days, nid, folk)["food"]
        in_run = max(0.0, need - have) / max(days, 1)
        hearths = len({h for n in folk for h in w.homes(n) if (w.s["buildings"][h].get("fittings") or {}).get("hearth")}) \
            or -(-len(folk) // int(CAP.PEOPLE_A_HEARTH))
        fuel_short = max(0.0, hearths * night * days - node_heat(nid)) / max(days, 1)       # heat a day to bring in
        if deficit < 0.5 and fuel_short <= 0:
            continue
        roads = [r["days"] for r in w.s["roads"].values() if nid in (r["a"], r["b"])]
        if not roads:
            burdens[nid] = (float("inf"), deficit, fuel_short, None, in_run)
            continue
        oxen = sum(int(h.get("oxen", 0)) for h in w.s["herds"].values() if node_of_herd(h) == nid)
        carry = CARRY["pack ox"] if oxen else CARRY["pack"] if any(
            (w.s["people"][n].get("holdings") or {}).get("pack") for n in folk) else CARRY["foot"]
        grain = 1.0 / float(ITEMS["grain"]["food"])                         # a ration as grain
        weight = deficit * grain + fuel_short * timber_weight
        carriers = weight * 2 * min(roads) / carry
        burdens[nid] = (carriers / len(folk), deficit, fuel_short, min(roads), in_run)
    worst = max((b[0] for b in burdens.values()), default=0.0)
    out["carrying burden"] = {"level": "refuse" if worst > T["burden_refuse"] else "warn", "ok": worst <= T["burden_warn"],
                              "detail": {w.s["nodes"][k]["name"]: {"short_people": round(b[1], 1), "short_heat_a_day": round(b[2], 1),
                                                                     "road_days": b[3], "share_on_the_road": round(b[0], 2),
                                                                     "short_rations_a_day_in_the_run": round(b[4], 1)}
                                         for k, b in burdens.items()}}
    # households: food a member against their own first harvest
    first_ripe = {}
    for pid, par in w.s["parcels"].items():
        crop = par.get("crop") or {}
        holders = [c["claimant"] for c in w.claims_on(("parcel", pid))]
        rd = crop.get("ripe_day")
        for h in holders:
            if rd is not None:
                first_ripe[h] = min(first_ripe.get(h, 99), int(rd))
    short, short_people, runways = [], 0, {}
    for iid, inst in w.s["institutions"].items():
        if inst.get("kind") != "household" or not inst["members"]:
            continue
        meals = 0.0
        for bid, b in w.s["buildings"].items():
            if b.get("household") == iid or iid in [c["claimant"] for c in w.claims_on(("building", bid))]:
                st = w.s["containers"].get(b.get("stock")) or {}
                for item, q in (st.get("goods") or {}).items():
                    meals += float(q) * float((ITEMS.get(item) or {}).get("food", 0.0) or 0.0)
        per = meals / len(inst["members"])
        runways[inst.get("name", iid)] = round(per, 1)
        if per < T["runway_days"] and first_ripe.get(iid, 99) > per + 1:
            short.append(inst.get("name", iid))
            short_people += len(inst["members"])
    share_short = short_people / max(P, 1)
    out["households' runway"] = {"level": "warn", "ok": share_short <= T["runway_people_warn"],
                                 "detail": {"short": short, "share_of_people": round(share_short, 2), "days_of_food_a_member": runways}}
    # fuel: nights in store a hearth, where a node has no wood of its own
    lows = {}
    for nid in w.s["nodes"]:
        woods = sum(p["size"] for p in w.s["parcels"].values() if p["node"] == nid and p["cover"] in ("forest", "scrub"))
        for bid, b in w.s["buildings"].items():
            if b["node"] != nid or not (b.get("fittings") or {}).get("hearth"):
                continue
            st = w.s["containers"].get(b.get("stock")) or {}
            heat_in = sum(float(q) * float((ITEMS.get(i) or {}).get("heat", 0.0) or 0.0) for i, q in (st.get("goods") or {}).items())
            nights = heat_in / float(w.p["heat"]["normal"])
            if nights < T["fuel_nights"] and woods == 0:
                lows[b["name"]] = round(nights, 1)
    out["fuel"] = {"level": "warn", "ok": not lows, "detail": lows or "every hearth has wood in store or woods at hand"}
    # growth: children on and a long run; births projected for couples trying about half the nights (D2-162: a birth about every
    # 12 days then, at the default lifespan; scaled), against the land (c2_combe: three births, and the land ran out)
    ch = spec.get("children") or {}
    on = bool(ch.get("on") or ch.get(True) or ch.get("true"))      # YAML reads `on:` as true; JSON writes it "true"
    couples = 0
    for inst in w.s["institutions"].values():
        if inst.get("kind") == "household":
            men = sum(1 for n in inst["members"] if w.s["people"][n].get("stage") == "adult" and w.s["people"][n].get("sex") == "m")
            women = sum(1 for n in inst["members"] if w.s["people"][n].get("stage") == "adult" and w.s["people"][n].get("sex") == "f")
            couples += min(men, women)
    every = 12.0 * float(spec.get("lifespan", 32)) / 32.0
    births = couples * days / every if on else 0.0
    gshare = (P + births) / max(min(food, heat), 1e-9)
    out["room to grow"] = {"level": "warn", "ok": not on or gshare <= 1.0,
                           "detail": f"{couples} couples; about {births:.0f} births in {days} days if they try often; the region would be "
                                     f"at {gshare:.2f} of its land" if on else "children off"}
    # succession: someone the household leans on dies of age within the run (c2_combe: the head died on day 62 of 80, and the two
    # he had fed starved within a week, on land that kept sixteen)
    life = float(spec.get("lifespan", 32))
    ends = []
    for iid, inst in w.s["institutions"].items():
        if inst.get("kind") != "household":
            continue
        grown = [n for n in inst["members"] if w.s["people"][n].get("stage") == "adult"]
        dying = [n for n in grown if w.s["people"][n].get("born") is not None
                 and float(w.s["people"][n]["born"]) + life <= w.d + days]
        if dying and len(inst["members"]) > len(dying):
            left = len(grown) - len(dying)
            ends.append(f"{inst.get('name', iid)}: {', '.join(dying)} of {len(grown)} grown die of age in the run; {left} grown left"
                        f" for {len(inst['members']) - len(dying)}")
    out["succession"] = {"level": "warn", "ok": not ends, "detail": ends or "nobody a household leans on dies of age in the run"}
    return out


def refused(checks: dict) -> list:
    return [k for k, v in checks.items() if not v["ok"] and v["level"] == "refuse"]


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    from cybertron2.engine.world import load_spec
    spec = load_spec(argv[0])
    c = check(spec)
    for k, v in c.items():
        print(f"{'ok  ' if v['ok'] else v['level']:6} {k}: {v['detail']}")
    return 1 if refused(c) else 0


if __name__ == "__main__":
    sys.exit(main())
