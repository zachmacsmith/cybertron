"""The economics of every published cybertron2 run (Hugging Face: zachmacsmith/charter-runs, experimental/cybertron2): for each, what
its world held at the start against what its people needed, and what happened (missed meals, hunger, deaths and their likely cause,
fires out). The aim (Zach, 2 Nov): learn from past runs when the economics worked and when they failed, to build automatic checks a
world must pass before a run, so nobody starts bound to starve. Analysis by 37.2; nothing decided.

    python docs/review/37_growth/02zk_run_economics.py <dir of downloaded runs>     # each run: <dir>/<run>/days.jsonl, run.json
    python docs/review/37_growth/02zk_run_economics.py --check <dir>                # the pre-run checks against what happened

Download (days.jsonl and run.json of each run, about 20 MB in all):
    python docs/review/37_growth/02zk_run_economics.py --fetch <dir>

What it reads from each run's starting world (run.json's spec), by plain arithmetic, so it works for worlds of every engine version:
- people: grown (eat 1 a night), children and infants (a share);
- food in store: each building's stock in meals (food a unit, data.ITEMS), whole grain counted at its boiled worth;
- food in the ground: crops standing, at what they will give;
- fuel in store: heat (data.ITEMS heat), against a hearth's need each night;
- capacity: the node's yearly flows (capacity.py's method), against its people;
and from what happened (days.jsonl): person-days, missed meals, short meals, deaths, unlit hearth-nights, harvests.
"""
from __future__ import annotations

import ast
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..")))

from cybertron2.engine.data import ITEMS  # noqa: E402

BASE = "https://huggingface.co/datasets/zachmacsmith/charter-runs/resolve/main/experimental/cybertron2"
TREE = "https://huggingface.co/api/datasets/zachmacsmith/charter-runs/tree/main/experimental/cybertron2"


def fetch(out: str) -> None:
    import concurrent.futures as cf
    import urllib.request
    runs = [x["path"].split("/")[-1] for x in json.load(urllib.request.urlopen(TREE)) if x["type"] == "directory"]

    def get(run, f):
        os.makedirs(os.path.join(out, run), exist_ok=True)
        p = os.path.join(out, run, f)
        if not os.path.exists(p):
            urllib.request.urlretrieve(f"{BASE}/{run}/{f}", p)

    with cf.ThreadPoolExecutor(8) as ex:
        list(ex.map(lambda a: get(*a), [(r, f) for r in runs for f in ("days.jsonl", "run.json")]))


def _v(x):
    """days.jsonl holds values as JSON in newer runs and as Python reprs in older ones."""
    if isinstance(x, str):
        try:
            return ast.literal_eval(x)
        except (ValueError, SyntaxError):
            return x
    return x


def meals(item: str, qty: float) -> float:
    it = ITEMS.get(item) or {}
    return float(qty) * float(it.get("food", 0.0) or 0.0)


def heat(item: str, qty: float) -> float:
    it = ITEMS.get(item) or {}
    return float(qty) * float(it.get("heat", 0.0) or 0.0)


def start(spec: dict) -> dict:
    """What a world holds at the start against what its people need."""
    agents = spec.get("agents") or {}
    grown = sum(1 for a in agents.values() if a.get("stage") not in ("infant", "child"))
    young = len(agents) - grown
    eaters = grown + 0.6 * young
    food = sum(meals(i, q) for b in (spec.get("buildings") or {}).values() for i, q in (b.get("stock") or {}).items())
    carried = sum(meals(i, q) for a in agents.values() for i, q in (a.get("holdings") or a.get("carry") or {}).items()
                  if isinstance(q, (int, float)))
    fuel = sum(heat(i, q) for b in (spec.get("buildings") or {}).values() for i, q in (b.get("stock") or {}).items())
    hearths = sum(1 for b in (spec.get("buildings") or {}).values() if (b.get("fittings") or {}).get("hearth"))
    crops, ripe = 0.0, []
    for n in (spec.get("nodes") or {}).values():
        for p in (n.get("parcels") or {}).values():
            c = (p.get("state") or {}).get("crop")
            if isinstance(c, dict) and c.get("left"):
                crops += float(c["left"]) * float(ITEMS.get("grain", {}).get("food", 0.7))
                if c.get("ripe_day") is not None:
                    ripe.append(int(c["ripe_day"]))
    fields = sum(int(p.get("size", 1)) for n in (spec.get("nodes") or {}).values() for p in (n.get("parcels") or {}).values()
                 if p.get("cover") == "field")
    herds = sum(int(h.get("cows", 0)) + int(h.get("oxen", 0)) + int(h.get("bulls", 0)) + int(h.get("young", 0)) + int(h.get("count", 0))
                for h in (spec.get("herds") or {}).values())
    cal = spec.get("calendar") or {}
    sd = int(cal.get("season_days", 6))
    season = cal.get("season", "summer")
    to_winter = {"spring": 2 * sd, "summer": sd, "autumn": 0, "winter": 0}.get(season, sd) + (sd - int(cal.get("day", 1)) + 1 if season != "winter" else 0)
    return {"people": len(agents), "grown": grown, "young": young, "food_meals": round(food + carried, 1),
            "food_days": round((food + carried) / eaters, 1) if eaters else None, "crops_meals": round(crops, 1),
            "first_ripe": min(ripe) if ripe else None, "fuel_heat": round(fuel, 1), "hearths": hearths,
            "fuel_nights": round(fuel / hearths, 1) if hearths else None, "fields": fields, "herd_head": herds,
            "nodes": len(spec.get("nodes") or {}), "days": int(spec.get("days", 0)), "to_winter": to_winter, "season_days": sd}


GOOD_DAYS = {"w1_wide": 24}            # runs whose later days are an artefact (w1: the usage limit; empty replies after day 24, 38.31)


def outcome(days: list, spec: dict) -> dict:
    alive0 = len(spec.get("agents") or {})
    person_days = missed = short = unlit = cold_nights = 0
    deaths, starved, cold_died, old, young_died = [], 0, 0, 0, 0
    miss_run = defaultdict(int)
    first_death = first_miss = None
    for d in days:
        day = int(_v(d.get("day", 0)))
        ate = _v(d.get("ate")) or {}
        person_days += len(ate) + len(_v(d.get("missed")) or [])
        ms = _v(d.get("missed")) or []
        missed += len(ms)
        short += len(_v(d.get("short")) or [])
        if ms and first_miss is None:
            first_miss = day
        for n in list(miss_run):
            if n not in ms:
                miss_run[n] = 0
        for n in ms:
            miss_run[n] += 1
        cold = _v(d.get("cold")) in (True, "True")
        cold_nights += int(cold)
        for h in (_v(d.get("hearth")) or {}).values():
            if isinstance(h, dict) and h.get("sleepers") and not h.get("lit"):
                unlit += 1
        life = _v(d.get("life")) or {}
        old += len(life.get("old_age") or [])
        young_died += len(life.get("deaths") or [])
        for n in _v(d.get("deaths")) or []:
            deaths.append((day, n))
            if first_death is None:
                first_death = day
            if miss_run.get(n, 0) >= 2:
                starved += 1
            elif cold:
                cold_died += 1
    return {"days_run": len(days), "person_days": person_days, "missed": missed,
            "missed_share": round(missed / person_days, 3) if person_days else None, "short": short, "deaths": len(deaths),
            "died_share": round(len(deaths) / alive0, 2) if alive0 else None, "starved": starved, "cold": cold_died, "old_age": old,
            "young": young_died, "first_miss": first_miss, "first_death": first_death, "unlit_hearth_nights": unlit,
            "cold_nights": cold_nights}


def verdict(s: dict, o: dict) -> str:
    if o["died_share"] is None:
        return "no people"
    hunger_deaths = o["starved"] + o["cold"]                         # old age and infants' deaths are not the economy's
    if hunger_deaths / max(1, s["people"]) >= 0.1 or (o["missed_share"] or 0) >= 0.1:
        return "failed"
    if (o["missed_share"] or 0) >= 0.03 or o["starved"]:
        return "strained"
    return "held"


def table(root: str) -> list:
    rows = []
    for run in sorted(os.listdir(root)):
        p = os.path.join(root, run)
        if not os.path.exists(os.path.join(p, "run.json")):
            continue
        spec = json.load(open(os.path.join(p, "run.json")))["spec"]
        days = [json.loads(l) for l in open(os.path.join(p, "days.jsonl"))] if os.path.exists(os.path.join(p, "days.jsonl")) else []
        if run in GOOD_DAYS:
            days = [d for d in days if int(_v(d.get("day", 0))) < GOOD_DAYS[run]]
        s, o = start(spec), outcome(days, spec)
        rows.append({"run": run, **s, **o, "verdict": verdict(s, o)})
    return rows


def validate(root: str, rows: list) -> list:
    """The pre-run checks (cybertron2/landgen/economy.py) on each run's starting world, against what happened. A run that stopped
    before half its planned days and did not fail is `cut short`: it says nothing either way (its full-length twin does)."""
    import contextlib
    import io
    from cybertron2.landgen import economy as EC
    out = []
    for r in rows:
        if not r["people"]:
            continue
        spec = json.load(open(os.path.join(root, r["run"], "run.json")))["spec"]
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                c = EC.check(spec)
        except KeyError as e:                                              # m1_*: the first engine's world format (no nodes)
            out.append({"run": r["run"], "verdict": r["verdict"], "error": f"does not load: {e!r}"})
            continue
        cut = r["verdict"] != "failed" and r["days_run"] < 0.5 * max(1, r["days"])
        ref = EC.refused(c)
        warn = [k for k, v in c.items() if not v["ok"] and v["level"] == "warn"]
        call = "cut short" if cut else ("TP" if ref else "FN") if r["verdict"] == "failed" else ("FP" if ref else "TN")
        out.append({"run": r["run"], "verdict": r["verdict"], "call": call, "refused": ref, "warned": warn,
                    "burden": max((v["share_on_the_road"] for v in (c["carrying burden"]["detail"] or {}).values() if "share_on_the_road" in v), default=0.0)})
    return out


def row(cells):
    print("| " + " | ".join(str(c) for c in cells) + " |")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--fetch":
        fetch(sys.argv[2])
        sys.exit(0)
    if len(sys.argv) > 2 and sys.argv[1] == "--check":
        rows = table(sys.argv[2])
        v = validate(sys.argv[2], rows)
        row(["run", "verdict", "call", "refused", "warned", "burden"])
        row(["---"] * 6)
        for x in v:
            row([x["run"], x["verdict"], x.get("call", x.get("error")), ", ".join(x.get("refused", [])), ", ".join(x.get("warned", [])),
                 x.get("burden", "")])
        from collections import Counter
        print(dict(Counter(x.get("call", "error") for x in v)))
        sys.exit(0)
    rows = table(sys.argv[1])
    cols = ["run", "people", "days_run", "food_days", "crops_meals", "first_ripe", "fuel_nights", "to_winter", "missed_share",
            "deaths", "starved", "cold", "old_age", "first_miss", "first_death", "unlit_hearth_nights", "verdict"]
    row(cols)
    row(["---"] * len(cols))
    for r in rows:
        if r["people"]:
            row([r[c] for c in cols])
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w") as f:
            json.dump(rows, f, indent=1)
