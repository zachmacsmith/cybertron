"""What is settled after the day's acts, engine-side: fights at night among those present (spec/conflict, to compile: the M1 harm
model), teaching and membership matched by day (knowledge.md; 09 §2d), thefts seen or not, goods left found at dawn. Every change
goes through the chokepoint at the node where it happens (D4-35).
"""
from __future__ import annotations

from cybertron2.engine import knowledge as KN
from cybertron2.engine.data import EDIBLE, ITEMS, TECHNIQUES


def settle_fights(w, today) -> list:
    fights, guards = today.get("fights", []), today.get("guards", {})
    cc = w.p["combat"]
    out = []

    def strength(n, base):
        x = w.s["people"][n]
        wpn = w.weapon(n)
        return x[base] * w.yield_mult(n) + (ITEMS[wpn]["weapon"] if wpn else 0.0)

    def wear_weapon(n):
        wpn = w.weapon(n)
        if wpn:
            w.apply("wear", w.at(n), container=w.hands(n), item=wpn, uses=cc["fight_wear"])

    for f in fights:
        node = f["node"]
        by = f["by"]
        if not w.s["people"][by]["alive"] or w.at(by) != node:
            continue
        rng = w.rng("fight", w.d, by, f.get("target") or f.get("building"))
        P = strength(by, "attack")
        wear_weapon(by)
        if f["kind"] == "raid":
            bid = f["building"]
            b = w.s["buildings"][bid]
            fled, awake = set(today.get("fled", [])), set(today.get("awake", []))       # what the woken chose (fuse events, D2-81)
            inside = [n for n in w.present(node) if bid in w.homes(n) and n != by and n not in fled]
            gd = [g for g, at in guards.items() if at == bid and w.at(g) == node and g != by and g not in fled]
            D = sum(strength(d, "defence") + cc["guard"] for d in gd) + sum(
                (1.0 if d in awake else cc["asleep"]) * strength(d, "defence") for d in inside if d not in gd)
            X = 2 * (D + 1) * (2.0 if b["structure"] == "stone" else 1.0) * (1.5 if b["door"] == "barred" else 1.0)   # D2-20
            holders = inside + [m for m in w.living() if bid in w.homes(m) and w.at(m) == node and m not in inside]
            if f.get("handed"):                                                 # food handed out at the door: no fight
                h = f["handed"]
                rec = {"kind": "raid", "by": by, "building": bid, "outcome": "handed", "took": h["qty"]}
                w.event(node, "raid", f"in the night someone came to {b['name']} and was handed {h['item']} at the door", actor=by,
                        about=[f"building:{bid}"], salience=0.95, tags=["danger", "food"], concerns=holders)
                out.append(rec)
                continue
            if rng.random() < P ** 2 / (P ** 2 + (X / 2) ** 2):
                took = 0.0
                for item in EDIBLE:
                    q = round(w.goods(b["stock"]).get(item, 0.0) * cc["raid_share"], 6)
                    if q > 1e-9:
                        w.apply("transfer", node, src=b["stock"], dst=w.hands(by), item=item, qty=q)
                        took += q * ITEMS[item]["food"]
                rec = {"kind": "raid", "by": by, "building": bid, "outcome": "taken", "took": round(took, 2)}
                w.event(node, "raid", f"in the night {b['name']} was broken into and food taken", actor=by, about=[f"building:{bid}"],
                        salience=0.95, tags=["danger", "food"], concerns=holders)
            else:
                rec = {"kind": "raid", "by": by, "building": bid, "outcome": "repelled"}
                w.event(node, "raid", f"in the night someone tried to break into {b['name']} and was driven off", actor=by,
                        about=[f"building:{bid}"], salience=0.95, tags=["danger"], concerns=holders + gd)
            for d in gd:
                wear_weapon(d)
            out.append(rec)
            continue
        t = f["target"]
        if not w.s["people"][t]["alive"] or w.at(t) != node:
            continue
        helpers = [g for g in guards if g not in (t, by) and w.at(g) == node]
        D = strength(t, "defence") + (cc["guard"] if t in guards else 0.0) + sum(strength(g, "defence") for g in helpers)
        wear_weapon(t)
        X = 2 * (D + 1)
        p_kill = P ** 2 / (P ** 2 + X ** 2) if f["aim"] == "hurt" else 0.0
        p_wound = P ** 2 / (P ** 2 + (X / 2) ** 2)
        u = rng.random()
        if u < p_kill:
            w.apply("die", node, person=t, cause="attack", to=by)
            rec = {"kind": "attack", "by": by, "target": t, "outcome": "killed", "killed": t}
            w.event(node, "death", f"{t} was killed by {by}", actor=by, target=t, salience=1.0, tags=["danger", "death"])
        elif u < p_wound:
            took = 0.0
            for item in EDIBLE:
                q = w.goods(w.hands(t)).get(item, 0.0)
                if q > 1e-9:
                    w.apply("transfer", node, src=w.hands(t), dst=w.hands(by), item=item, qty=q)
                    took += q * ITEMS[item]["food"]
            w.apply("harm", node, person=t, wounded=True, hunger=-2)
            rec = {"kind": "attack", "by": by, "target": t, "outcome": "wounded", "took": round(took, 2)}
            w.event(node, "fight", f"{by} beat {t} and took what food {t} carried", actor=by, target=t, salience=0.95, tags=["danger"], concerns=[t])
        else:
            rec = {"kind": "attack", "by": by, "target": t, "outcome": "repelled"}
            w.event(node, "fight", f"{by} set on {t} and was beaten off", actor=by, target=t, salience=0.9, tags=["danger"], concerns=[t])
        out.append(rec)
    return out


def settle_teaching(w, today) -> dict:
    """Teaching happens when a teach and a learn match the same day, both at one node."""
    out = {}
    for t in today["teach"]:
        match = next((l for l in today["learn"] if l["by"] == t["to"] and l["from"] == t["by"] and l["tech"] == t["tech"]), None)
        label = KN.label(t["tech"])
        if not match or w.at(t["by"]) != w.at(t["to"]):
            out.setdefault(t["by"], []).append(f"You meant to teach {t['to']} {label}, but {t['to']} did not set aside time to learn.")
            continue
        target = "known" if w.s["people"][t["to"]]["stage"] == "youth" else "capable"
        k = w.s["know"].setdefault(t["to"], {})
        before = k.get(t["tech"], {}).get("level") or "aware"
        from cybertron2.engine.data import LEVELS
        if LEVELS.index(before) >= LEVELS.index(target):
            out.setdefault(t["by"], []).append(f"{t['to']} already has {label} as well as a day's teaching can give; you lost the day's time.")
            out.setdefault(t["to"], []).append(f"{t['by']} had nothing more to teach you of {label} that a day could give; practice is what you need.")
            continue
        node = w.at(t["by"])
        w.apply("learn", node, person=t["to"], tech=t["tech"], level=target, source=f"taught by {t['by']}")
        tk = w.s["know"].get(t["by"], {}).get(t["tech"], {})
        r = k[t["tech"]]
        share = float(w.p["teach"]["skill_share"]) * (2 if w.s["people"][t["to"]]["stage"] == "youth" else 1)
        r["skill"] = round(r.get("skill", 0.6) + share * max(0.0, float(tk.get("skill", 1.0)) - r.get("skill", 0.6)), 3)
        out.setdefault(t["by"], []).append(f"You taught {t['to']} {label}.")
        out.setdefault(t["to"], []).append(f"{t['by']} taught you {label} ({before} -> {target}).")
        w.event(node, "teach", f"{t['by']} spent the day teaching {t['to']} {label}", actor=t["by"], target=t["to"], salience=0.3,
                tags=TECHNIQUES[t["tech"]]["tags"], concerns=[t["to"]])
    for l in today["learn"]:
        if not any(t["by"] == l["from"] and t["to"] == l["by"] and t["tech"] == l["tech"] for t in today["teach"]):
            out.setdefault(l["by"], []).append(f"You meant to learn from {l['from']}, but {l['from']} did not set aside time to teach you.")
    return out


def settle_joins(w, today) -> dict:
    """Joining a household (09 §2d; D4-36): the person asks and one who may admit agrees, the same day, at one node."""
    out = {}
    for j in today["joins"]:
        ok = next((a for a in today["admits"] if a["person"] == j["by"] and a["household"] == j["household"]
                   and w.at(a["by"]) == w.at(j["by"])), None)
        name = w.s["institutions"][j["household"]]["name"]
        if not ok:
            out.setdefault(j["by"], []).append(f"Nobody of {name} took you in today.")
            continue
        node = w.at(j["by"])
        old = w.household_of(j["by"])
        w.apply("admit", node, person=j["by"], inst=j["household"])
        out.setdefault(j["by"], []).append(f"You are now one of {name}." + (f" You have left {w.s['institutions'][old]['name']}." if old else ""))
        out.setdefault(ok["by"], []).append(f"{j['by']} is now one of {name}.")
        w.event(node, "household", f"{j['by']} was taken into {name}", actor=ok["by"], target=j["by"], salience=0.7, tags=["household"],
                concerns=w.members(j["household"]) + ([*w.members(old)] if old else []))
    for a in today["admits"]:
        if not any(j["by"] == a["person"] and j["household"] == a["household"] for j in today["joins"]):
            out.setdefault(a["by"], []).append(f"{a['person']} did not ask to join today.")
    return out


def settle_thefts(w, today, attend) -> None:
    """Who saw a theft: those of the house at home, anyone attending to it or the place, a small chance for the rest."""
    from cybertron2.engine import perceive as PC
    for st in today["thefts"]:
        b = w.s["buildings"][st["building"]]
        node = b["node"]
        seen = []
        for x in w.agents_acting():
            if x == st["by"] or w.at(x) != node:
                continue
            tgt = str(today["watch"].get(x) or attend.get(x) or "").lower()
            at_home = st["building"] in w.homes(x) and not today["worked"].get(x) and not today["watch"].get(x)
            p = 0.8 if b["name"].lower() in tgt else 0.45 if at_home else 0.3 if tgt in ("place", "the place") else 0.05
            if w.rng("steal-seen", w.d, x, st["by"]).random() < p:
                seen.append(x)
        owners = [m for m in w.living() if st["building"] in w.homes(m)]
        if seen:
            w.event(node, "theft", f"{st['by']} slipped into {b['name']} and came out with {st['qty']:g} {st['item']}", actor=st["by"],
                    about=[f"building:{st['building']}"], salience=0.9, tags=["danger", "food"], concerns=seen + owners)
            PC.store(w, st["by"])["today"]["heard"].append(f"You think you were seen coming out of {b['name']}.")
        else:
            w.event(node, "loss", f"some {st['item']} is missing from {b['name']}'s store", about=[f"building:{st['building']}"],
                    salience=0.6, tags=["food", "danger"], concerns=owners)
