"""A seeded society with a past (D4-21, 09 §3c) for one node: a family tree simulated forward from founding couples, the living
sorted into households, kin ties derived from the tree, ties (friendships, a feud, debts, an old love), a short history, and what
each person knows (its line's crafts, what it has seen of others'), each written from the person's own position.

    python -m cybertron2.engine.generate <base spec> --seed N --out <spec.yaml>

The base spec gives the node, the houses' places and the lines: lines: {Reed: {crafts: [reap, bread], tool: sickle}, ...}.
Everything the generator writes can be edited by hand afterwards (README rule). The tree is simulated in years (its demography), then
dated in days with the world's lifespan (D2-139, D2-153): every date goes through one monotone map whose knots are the stages'
starts (4, 12, 18 and 60 years to the infant, child, youth and adult spans), so each person's stage by days is its stage by years.
Agents get `born` (a day, negative); memories count winters from the days.
"""
from __future__ import annotations

import argparse
import copy
import random

import yaml

from cybertron2.engine import life as LF
from cybertron2.engine.data import TECHNIQUES

MALE = ["Osric", "Wat", "Hob", "Aldric", "Edric", "Godwin", "Ralf", "Piers", "Hamo", "Simkin", "Tobin", "Alard", "Durand", "Hugh",
        "Ivo", "Jory", "Lambert", "Odo", "Roger", "Warin", "Adam", "Baldwin", "Colin", "Drew", "Elias", "Fulk", "Gervase", "Hamon",
        "Herbert", "Jocelin", "Martin", "Nicol", "Otes", "Payn", "Randal", "Robin", "Saer", "Thurstan", "Walter", "Wymond", "Absolon",
        "Bennet", "Clement", "Daniel", "Everard", "Geoffrey", "Gilbert", "Henry", "Jordan", "Lucas", "Matthew", "Nigel", "Oliver",
        "Peter", "Reynold", "Richard", "Stephen", "Thomas", "William", "Ancel"]
FEMALE = ["Maud", "Agnes", "Ivy", "Edith", "Alys", "Mabel", "Joan", "Cecily", "Avice", "Emma", "Hawise", "Isolde", "Letice",
          "Mariot", "Rohese", "Sibyl", "Tiffany", "Wymarc", "Beatrix", "Elena", "Amice", "Christian", "Denise", "Eva", "Felice",
          "Gunnild", "Helewise", "Idonea", "Juliana", "Lettice", "Margery", "Nichola", "Orabel", "Petronel", "Rose", "Sarra", "Thomasin",
          "Ysolt", "Alice", "Godiva", "Annora", "Basilia", "Cassandra", "Dionisia", "Ellen", "Florence", "Gillian", "Isabel",
          "Joyce", "Katherine", "Lucy", "Matilda", "Olive", "Philippa", "Richolda", "Sabina", "Susanna", "Ursula", "Wilmot", "Agatha"]
OUTSIDE = "Ashby"                                    # where spouses who married in came from


KNOTS = [0, 4, 12, 18, 60]                           # years at which each stage starts: infant, child, youth, adult, elder


def to_days(years, L=None) -> float:
    """Years (an age, or how long ago) to days, by the stages' starts (D2-153); beyond old age a year is L/40 days."""
    L = L or LF.lifespan()
    at = [0]
    for _, d in LF.spans(L):
        at.append(at[-1] + d)
    y = max(0.0, float(years))
    for k in range(len(KNOTS) - 1):
        if y <= KNOTS[k + 1]:
            return at[k] + (y - KNOTS[k]) / (KNOTS[k + 1] - KNOTS[k]) * (at[k + 1] - at[k])
    return at[-1] + (y - KNOTS[-1]) * L / 40.0


def born_day(age, L=None) -> int:
    return -int(round(to_days(age, L)))


def stage(age, L=None) -> str:
    return LF.stage_of(-born_day(age, L), L)


def winters(n, L=None, year=24) -> str:
    """How long ago, in winters, of something n years back in the tree, counted from its days."""
    k = max(1, round(to_days(n, L) / float(year)))
    return "last winter" if k <= 1 else f"{k} winters ago"


class Tree:
    def __init__(self, rng):
        self.rng, self.p, self.used = rng, {}, set()

    def name(self, sex):
        pool = [n for n in (MALE if sex == "m" else FEMALE) if n not in self.used]
        n = self.rng.choice(pool) if pool else f"{self.rng.choice(MALE if sex == 'm' else FEMALE)} the younger"
        self.used.add(n)
        return n

    def person(self, sex, born, line, parents=(), origin=None):
        n = self.name(sex)
        self.p[n] = {"name": n, "sex": sex, "born": born, "died": None, "cause": None, "parents": list(parents), "partner": None,
                     "line": line, "origin": origin, "children": [], "left": None}
        for x in parents:
            self.p[x]["children"].append(n)
        return n

    def age(self, n, year=0):
        return year - self.p[n]["born"]

    def alive(self, n, year=0):
        x = self.p[n]
        return x["born"] <= year and (x["died"] is None or x["died"] > year) and (x["left"] is None or x["left"] > year)


def simulate(lines: dict, rng, start=-62, fertility=0.28, leave=0.3, T=None, hard=None) -> tuple[Tree, list]:
    """Forward from a founding couple per line, year by year to now (year 0). Returns the tree and the history. A tree passed in
    (another place's lines, already simulated) is extended with these lines; hard winters passed in are shared across places."""
    T = T or Tree(rng)
    T.rng = rng
    hist = []
    for line in lines:
        h = T.person("m", start - rng.randint(20, 26), line)
        wf = T.person("f", start - rng.randint(18, 24), line, origin=OUTSIDE)
        T.p[h]["partner"], T.p[wf]["partner"] = wf, h
        place = (lines[line] or {}).get("place", "Millbrook")
        hist.append({"year": start, "text": f"{h} and {wf} {line} came to {place} and built the first {line} house", "who": [h, wf]})
    hard = hard or sorted(rng.sample(range(start + 5, -1), 3)) + [-2]
    for y in range(start, 1):
        winter = y in hard
        if winter:
            hist.append({"year": y, "text": "a hard winter: the frost came early and the stores ran out", "kind": "winter", "who": []})
        for n in [n for n in T.p if T.alive(n, y) and T.p[n]["line"] in lines]:
            a = T.age(n, y)
            risk = 0.002 if a < 50 else 0.03 if a < 65 else 0.10 if a < 72 else 0.25
            risk = 0.02 if a < 5 else risk
            if winter:
                risk = risk * 4 + (0.02 if a > 55 else 0)
            if y > -1 and rng.random() < risk:
                T.p[n]["died"] = y
                T.p[n]["cause"] = "the hard winter" if winter else ("a fever" if a < 50 else "old age")
                hist.append({"year": y, "text": f"{n} died ({T.p[n]['cause']})", "kind": "death", "who": [n]})
        for n in [n for n in T.p if T.alive(n, y) and T.p[n]["sex"] == "f" and T.p[n]["line"] in lines]:
            m = T.p[n]["partner"]
            if m and T.alive(m, y) and 19 <= T.age(n, y) <= 42 and rng.random() < fertility:
                last = max([T.p[c]["born"] for c in T.p[n]["children"]] or [-999])
                if y - last >= 2:
                    T.person(rng.choice("mf"), y, T.p[m]["line"], (m, n))
        single = [n for n in T.p if T.alive(n, y) and not T.p[n]["partner"] and 18 <= T.age(n, y) <= 30 and T.p[n]["line"] in lines]
        rng.shuffle(single)
        for n in single:
            if T.p[n]["partner"] or rng.random() > 0.35:
                continue
            other = [x for x in single if x != n and not T.p[x]["partner"] and T.p[x]["sex"] != T.p[n]["sex"]
                     and T.p[x]["line"] != T.p[n]["line"] and not set(T.p[x]["parents"]) & set(T.p[n]["parents"])]
            if other and rng.random() < 0.5:
                x = other[0]
            elif rng.random() < 0.3 and T.p[n]["sex"] == "m":
                x = T.person("f", y - T.age(n, y) + rng.randint(-3, 2), T.p[n]["line"], origin=OUTSIDE)
            elif rng.random() < leave:
                T.p[n]["left"] = y
                hist.append({"year": y, "text": f"{n} married into {OUTSIDE} and left {(lines[T.p[n]['line']] or {}).get('place', 'Millbrook')}",
                             "kind": "left", "who": [n]})
                continue
            else:
                continue
            husband, wife = (n, x) if T.p[n]["sex"] == "m" else (x, n)
            T.p[husband]["partner"], T.p[wife]["partner"] = wife, husband
            T.p[wife]["line_born"] = T.p[wife]["line"]
            T.p[wife]["line"] = T.p[husband]["line"]
            if T.p[wife]["origin"] != OUTSIDE:
                hist.append({"year": y, "text": f"{wife} of the {T.p[wife]['line_born']}s married {husband} {T.p[husband]['line']}",
                             "kind": "marriage", "who": [husband, wife]})
    return T, hist


# ---------------------------------------------------------------------- kin from the tree
def kin(T, a, b, deep=True) -> str | None:
    """The kin term for b as a sees it, derived from the tree (never stored)."""
    P = T.p
    par = lambda x: set(P[x]["parents"])
    kids = lambda x: set(P[x]["children"])
    sibs = lambda x: {y for p in P[x]["parents"] for y in P[p]["children"]} - {x}
    mate = lambda x: {P[x]["partner"]} if P[x]["partner"] else set()
    g = lambda m, f: m if P[b]["sex"] == "m" else f
    if b in mate(a):
        return g("your husband", "your wife")
    if b in par(a):
        return g("your father", "your mother")
    if b in kids(a):
        return g("your son", "your daughter")
    if b in sibs(a):
        return g("your brother", "your sister")
    gp = {y for p in par(a) for y in par(p)}
    gc = {y for c in kids(a) for y in kids(c)}
    if b in gp:
        return g("your grandfather", "your grandmother")
    if b in gc:
        return g("your grandson", "your granddaughter")
    if b in {y for p in gp for y in par(p)}:
        return g("your great-grandfather", "your great-grandmother")
    if b in {y for c in gc for y in kids(c)}:
        return g("your great-grandson", "your great-granddaughter")
    if b in {y for p in par(a) for s in sibs(p) for y in {s} | mate(s)}:
        return g("your uncle", "your aunt")
    if b in {y for s in sibs(a) | {z for m in mate(a) for z in sibs(m)} for y in kids(s)}:
        return g("your nephew", "your niece")
    if b in {y for p in par(a) for s in sibs(p) for y in kids(s)}:
        return "your cousin"
    if b in {y for m in mate(a) for y in par(m)}:
        return g("your father-in-law", "your mother-in-law")
    if b in {y for c in kids(a) for y in mate(c)}:
        return g("your son-in-law", "your daughter-in-law")
    if b in {y for m in mate(a) for y in sibs(m)} | {y for s in sibs(a) for y in mate(s)}:
        return g("your brother-in-law", "your sister-in-law")
    for m in mate(b) if deep else ():
        r = kin(T, a, m, False) if m != a else None
        if r and "-in-law" not in r and "'s " not in r:
            return f"{r}'s " + g("husband", "wife")
    return None


# ---------------------------------------------------------------------- the spec
def build(base: dict, seed: int, tries=600) -> dict:
    lines = base["lines"]
    nodes = base.get("nodes") or {"home": base.get("node", {})}
    houses_of = {bid: b for bid, b in (base.get("buildings") or {}).items() if b.get("household") and (b.get("fittings") or {}).get("beds")}
    for line, d in lines.items():                                          # each line's place: the node of its house
        hid = next((k for k, h in houses_of.items() if h["household"] == line), None)
        pid = houses_of[hid]["parcel"] if hid else None
        d["place"] = next((n["name"] for n in nodes.values() if pid in (n.get("parcels") or {})), "Millbrook")
    bd = base.get("bounds") or {}
    sim = dict(base.get("sim") or {})
    places = {}                                                            # lines are simulated together within a place, and
    for line, d in lines.items():                                          # places one after another (so a large region still fits)
        places.setdefault(d["place"], []).append(line)

    def fits(T, ls):
        acting = [n for n in T.p if T.alive(n) and T.age(n) >= 12 and T.p[n]["line"] in ls]
        per = [sum(1 for n in acting if T.p[n]["line"] == l) for l in ls]
        size = lambda l: (lines[l] or {}).get("acting") or [0, 99]          # a line's own bounds on its working people, if given
        return (all(any(T.p[n]["line"] == l and T.age(n) >= 18 for n in acting) for l in ls)
                and all(size(l)[0] <= p <= size(l)[1] for l, p in zip(ls, per))
                and min(per) >= bd.get("per_min", 2) and max(per) - min(per) <= bd.get("per_spread", 3)
                and all(sum(1 for n in acting if T.p[n]["line"] == l and stage(T.age(n), base.get("lifespan")) == "adult") >= int((lines[l] or {}).get("min_adults", 0))
                        for l in ls))                                  # each trade has people of working age to do it

    for k in range(tries):
        rng = random.Random(f"{seed}|tree|{k}")
        start = int(sim.get("start", -62))
        hard = sorted(rng.sample(range(start + 5, -1), 3)) + [-2]
        T, hist, ok = Tree(rng), [], True
        for place, ls in places.items():
            for j in range(tries // 2):
                T2 = copy.deepcopy(T)
                T2, h = simulate({l: lines[l] for l in ls}, random.Random(f"{seed}|tree|{k}|{place}|{j}"), T=T2, hard=hard, **sim)
                if fits(T2, ls):
                    T, hist = T2, hist + [x for x in h if x.get("kind") != "winter" or place == next(iter(places))]
                    break
            else:
                ok = False                                                 # this place never fit: start the region again
                break
        if not ok:
            continue
        living = [n for n in T.p if T.alive(n)]
        acting = [n for n in living if T.age(n) >= 12]
        lo, hi = bd.get("acting", [6, 9])
        if (lo <= len(acting) <= hi and len(living) - len(acting) <= bd.get("children_max", 3)
                and sum(stage(T.age(n), base.get("lifespan")) == "youth" for n in acting) >= bd.get("youths_min", 1)):
            break
    else:
        raise RuntimeError("no tree fits; widen the bounds")
    rng = random.Random(f"{seed}|ties")
    L = int(base.get("lifespan") or LF.lifespan())
    year = 4 * int((base.get("calendar") or {}).get("season_days", 6))
    stage_ = lambda age: stage(age, L)
    wint = lambda n: winters(n, L, year)
    spec = copy.deepcopy({k: v for k, v in base.items() if k not in ("lines",)})
    spec["generated"] = {"seed": seed, "try": k}
    date = lambda y: None if y is None else -int(round(to_days(-y, L)))      # a year of the tree as a day (0 now)
    spec["tree"] = [{**p, "born": date(p["born"]), "died": date(p["died"]), "left": date(p["left"])} for p in T.p.values()]
    spec["history"] = [{**{k: v for k, v in h.items() if k != "year"}, "day": date(h["year"])} for h in sorted(hist, key=lambda h: h["year"])]
    agents = {}
    for n in living:
        p = T.p[n]
        line = p["line"]
        agents[n] = {"household": line, "born": born_day(T.age(n), L), "stage": stage_(T.age(n)), "sex": p["sex"], "relations": {},
                     "memories": [], "knows": {}, "aware_of": {}, "holdings": {}, "concerns": []}
        if p["parents"]:
            agents[n]["parents"] = list(p["parents"])
        if p["partner"]:
            agents[n]["partner"] = p["partner"]
    # heads: the eldest man of each line who is an adult, else the eldest adult
    head = {}
    for l in lines:
        ad = sorted([n for n in agents if T.p[n]["line"] == l and agents[n]["stage"] in ("adult", "elder")], key=lambda n: T.p[n]["born"])
        men = [n for n in ad if T.p[n]["sex"] == "m" and agents[n]["stage"] == "adult"]
        head[l] = (men or [n for n in ad if agents[n]["stage"] == "adult"] or ad)[0]
        agents[head[l]]["role"] = "head"
    # kin and the dead
    for a in agents:
        for b in T.p:
            if a == b:
                continue
            r = kin(T, a, b)
            if b in agents:
                agents[a]["relations"][b] = r or f"of the {T.p[b]['line']} household"
            elif r and T.p[b]["died"] is not None and T.age(a, T.p[b]["died"]) >= 6:
                agents[a]["memories"].append(f"{r[5:].capitalize()} {b} died {wint(-T.p[b]['died'])} ({T.p[b]['cause']}).")
            elif (r and T.p[b]["left"] is not None and r.split()[-1] in ("father", "mother", "son", "daughter", "brother", "sister")
                  and sum("married into" in m for m in agents[a]["memories"]) < 2):
                agents[a]["memories"].append(f"{r[5:].capitalize()} {b} married into {OUTSIDE}, two days' walk away.")
    hard = [h["year"] for h in hist if h.get("kind") == "winter"]
    for a in agents:
        seen = list(dict.fromkeys(wint(-y) for y in hard if T.age(a, y) >= 6))
        if seen:
            agents[a]["memories"].insert(0, "Hard winters you remember, when the frost came early and the stores ran out: "
                                         + ", ".join(seen) + ".")
    for h in [h for h in hist if h["year"] == min(x["year"] for x in hist)]:
        for a in agents:
            if f" {T.p[a].get('line_born') or T.p[a]['line']} " in f" {h['text']} ":
                agents[a]["memories"].insert(0, f"Your line's founders: {h['text']}.")
    # ties: a feud between the lines, debts, friendships, an old love
    ls = list(lines)
    pairs = [(head[x], head[y]) for i, x in enumerate(ls) for y in ls[i + 1:]]
    pairs = [p for p in pairs if kin(T, *p) is None] or pairs                 # a feud between strangers if there are any
    if pairs:
        a, b = pairs[rng.randrange(len(pairs))]
        yrs = rng.randint(4, 12)
        hh = {T.p[a]["line"], T.p[b]["line"]}                             # a field either of them holds: both claim it (D4-23)
        fields = [c["thing"][1] for c in base.get("claims") or [] if c["thing"][0] == "parcel" and c["claimant"] in hh
                  and any(c["thing"][1] in (n.get("parcels") or {}) and n["parcels"][c["thing"][1]]["cover"] == "field" for n in nodes.values())]
        field = rng.choice(fields) if fields else None
        fname = next((n["parcels"][field]["name"] for n in nodes.values() if field in (n.get("parcels") or {})), None) if field else None
        why = rng.choice([f"who has the right to {fname}", f"a boundary stone moved on {fname}"]) if fname else "a pig that went missing"
        if field:
            holder = next(c["claimant"] for c in base["claims"] if c["thing"] == ["parcel", field] and c["claimant"] in hh)
            other = (hh - {holder}).pop()
            spec.setdefault("claims", []).append({"thing": ["parcel", field], "claimant": other, "rights": "all", "grounds": "custom"})
        for x, y in ((a, b), (b, a)):
            agents[x]["relations"][y] += f"; there is bad blood between your households since {wint(yrs)}, over {why}"
        ago = wint(yrs)[0].upper() + wint(yrs)[1:]
        agents[a]["memories"].append(f"{ago} you and {b} came to blows over {why}; it was never settled.")
        agents[b]["memories"].append(f"{ago} {a} struck you in a quarrel over {why}; you have not forgotten.")
        spec["history"].append({"day": date(-yrs), "text": f"{a} and {b} came to blows over {why}", "kind": "feud", "who": [a, b]})
    adults = [n for n in agents if agents[n]["stage"] in ("adult", "elder")]
    for _ in range(2):
        debtor = rng.choice(adults)
        creditor = rng.choice([n for n in adults if T.p[n]["line"] != T.p[debtor]["line"]] or [None])
        if creditor:
            q, item = rng.choice([(2, "grain"), (3, "grain"), (2, "timber"), (1, "meat")])
            agents[debtor]["relations"][creditor] += f"; you owe them {q} {item} from last winter"
            agents[creditor]["relations"][debtor] += f"; they owe you {q} {item} from last winter"
            agents[debtor]["memories"].append(f"Last winter {creditor} lent you {q} {item} when your store ran low; you have not paid it back.")
            spec.setdefault("agreements", []).append({"parties": [debtor, creditor], "legs": [{"from": debtor, "to": creditor, "item": item,
                                                      "qty": q, "when": {"by": -1}, "paid": 1, "arrears": q}], "status": "open", "seeded": True})
    young = [n for n in agents if agents[n]["stage"] == "youth"]
    for y in young:
        friends = [n for n in agents if n != y and agents[n]["stage"] in ("youth", "adult") and abs(T.age(n) - T.age(y)) <= 4
                   and T.p[n]["line"] != T.p[y]["line"]]
        if friends:
            f = rng.choice(friends)
            if "friend" not in agents[y]["relations"][f]:
                agents[y]["relations"][f] += "; your closest friend"
                agents[f]["relations"][y] += "; a close friend"
    married = [n for n in adults if T.p[n]["partner"] in agents and T.p[n]["sex"] == "f"]
    if married and rng.random() < 0.7:
        w = rng.choice(married)
        old = [n for n in adults if T.p[n]["sex"] == "m" and n != T.p[w]["partner"] and kin(T, n, w) is None]
        if old:
            o = rng.choice(old)
            agents[o]["relations"][w] += "; you courted her once, before she married"
            agents[w]["relations"][o] += "; he courted you once, before you married"
    # knowledge, tools, models, aims
    for n, a in agents.items():
        p = T.p[n]
        own = lines[p["line"]]["crafts"]
        born = lines.get(p.get("line_born") or p["line"], {}).get("crafts", [])
        age = T.age(n)
        for c in sorted(set(own) | set(born)):
            if a["stage"] in LF.MINOR:
                continue
            if a["stage"] == "youth":
                a["knows"][c] = "capable" if age >= 15 else "rough"
            else:
                a["knows"][c] = {"level": "known", "skill": round(min(1.5, 1.0 + 0.0125 * (age - 18)), 2) if TECHNIQUES[c].get("basic")
                                 else round(min(1.8, 0.8 + 0.025 * (age - 18)), 2)}           # seeded specialists start skilled (D2-52)
        for l, d in lines.items():
            for c in d["crafts"]:
                if c not in a["knows"] and a["stage"] not in LF.MINOR:         # another line's craft: seen, not known
                    a["aware_of"][c] = f"you have seen the {l}s at it all your life"
        for c in a["knows"]:
            a["concerns"] += [t for t in TECHNIQUES[c]["tags"] if t not in a["concerns"]]
        a["concerns"] = a["concerns"][:4]
        cast = base.get("cast") or {}
        a["model"] = None if a["stage"] in LF.MINOR else ((lines[p["line"]] or {}).get("head_model") or cast.get("head", "claude-opus-5-5")
                                                        if a.get("role") == "head" else
                                                        cast.get("youth", "claude-haiku-5-5") if a["stage"] == "youth" else
                                                        cast.get("rest", "claude-sonnet-5-5"))
        a["born_line"] = p.get("line_born") or p["line"]
        a["trade"] = " and ".join(TECHNIQUES[c]["label"].split(" (")[0] for c in own[:2]) if a["stage"] in ("adult", "elder") else ""
    hm = base.get("household_models") or {}                                  # one model a household, if the world says so
    for n, a in agents.items():
        if a["model"] and a["household"] in hm:
            a["model"] = hm[a["household"]]
    extra = int((base.get("cast") or {}).get("opus_extra", 0))               # more strong players: the adults who know the most
    pool = sorted([n for n, a in agents.items() if a["stage"] == "adult" and a.get("role") != "head"],
                  key=lambda n: (-len([v for v in agents[n]["knows"].values() if not isinstance(v, str)]), T.p[n]["born"]))
    for n in pool[:extra]:
        agents[n]["model"] = (base.get("cast") or {}).get("head", "claude-opus-5-5")
    pool = [n for n in pool[extra:]]                                          # a middle tier: one per household before a second
    seen, spread = set(), []
    for n in pool + pool:
        if n not in spread and (agents[n]["household"] not in seen or len(seen) >= len({agents[x]["household"] for x in pool})):
            spread.append(n)
            seen.add(agents[n]["household"])
    for n in spread[:int((base.get("cast") or {}).get("sonnet_extra", 0))]:
        agents[n]["model"] = (base.get("cast") or {}).get("middle", "claude-sonnet-5-5")
    for l, d in lines.items():
        tools = d.get("tools") or []                                      # a list: one each to the head; {tool: n}: one each to n
        workers = [head[l]] + sorted((n for n in agents if T.p[n]["line"] == l and n != head[l] and agents[n]["stage"] in ("adult", "youth")),
                                     key=lambda n: T.p[n]["born"])      # of the household's working people, the head first
        for tool, k in (tools.items() if isinstance(tools, dict) else ((t, 1) for t in tools)):
            for n in workers[:int(k)]:
                agents[n]["holdings"][tool] = agents[n]["holdings"].get(tool, 0) + 1
        for i, (item, q) in enumerate((d.get("holdings") or {}).items()):
            agents[head[l]]["holdings"][item] = q
    for n, a in agents.items():
        if a["stage"] in LF.MINOR:
            continue
        rel = a["relations"]
        others = [b for b in agents if T.p[b]["line"] != T.p[n]["line"]]
        if a.get("role") == "head":
            a["aim"] = f"See the {T.p[n]['line']} household through the winter, fed and warm."
            feud = next((b for b in rel if "bad blood" in rel[b]), None)
            if feud:
                a["aim"] += f" You will not be shamed by {feud} again."
        elif a["stage"] == "youth":
            other_crafts = [(c, l) for l, d in lines.items() for c in d["crafts"] if c not in a["knows"]]
            c, l = rng.choice(other_crafts) if other_crafts else (None, None)
            a["aim"] = "Prove yourself to your family" + (f", and learn {TECHNIQUES[c]['label'].split(' (')[0]} as the {l}s do it." if c else ".")
        elif a["stage"] == "elder":
            a["aim"] = rng.choice(["Pass on what you know before your strength goes.",
                                   "See your grandchildren settled and provided for before you die.",
                                   "Keep the family's good name, and see that what is owed to it is paid.",
                                   "Live through one more winter, and be a burden to nobody."])
        else:
            debt = next((b for b in rel if "you owe" in rel[b]), None)
            a["aim"] = "Keep your household fed and its house sound" + (f"; pay back {debt} what you owe, if you can." if debt else ".")
        line_aim = (lines[T.p[n]["line"]] or {}).get("aim")                    # a line's own aim for its adults and youths (data only: no aim is shown, D4-29)
        if line_aim and a["stage"] != "elder":
            a["aim"] = line_aim + (a["aim"][a["aim"].index(" You will not"):] if " You will not" in a["aim"] else "")
        a["memories"] = a["memories"][-8:]
    spec["agents"] = agents
    for hid, h in spec["buildings"].items():
        if hid not in houses_of:
            continue
        mouths = sum(1 for a in agents.values() if a["household"] == h["household"])
        h["fittings"] = {**h["fittings"], "beds": max(int(h["fittings"].get("beds", 4)), mouths)}
        h["size"] = max(int(h.get("size", 4)), mouths)
        k = mouths / float(base.get("stock_mouths", 3))                     # starting stores in proportion to the mouths
        h["stock"] = {i: round(q * k, 1) for i, q in (h.get("stock") or {}).items()}
    return spec


def main(argv=None):
    ap = argparse.ArgumentParser(prog="cybertron2.engine.generate")
    ap.add_argument("base")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    with open(args.base) as f:
        base = yaml.safe_load(f)
    if base.get("node_from"):
        import os
        with open(os.path.join(os.path.dirname(args.base), base["node_from"])) as f:
            node = yaml.safe_load(f)
        node.pop("agents", None)
        base = {**node, **{k: v for k, v in base.items() if k != "node_from"}, "name": os.path.basename(args.out).split(".")[0]}
    spec = build(base, args.seed)
    with open(args.out, "w") as f:
        f.write(f"# Generated by cybertron2.engine.generate from {args.base}, seed {args.seed}. Edit by hand if needed.\n")
        yaml.safe_dump(spec, f, sort_keys=False, allow_unicode=True, width=140)
    print(args.out, {n: (a["stage"], a["model"]) for n, a in spec["agents"].items()})


if __name__ == "__main__":
    main()
