"""Fights, settled at night (world.end_of_round step 2): raids on houses, then attacks on people. A simplified port of the old
engine's harm model (cybertron/conflict.py, docs/review/21_combat.md).

Strength. Each person has an attack and a defence base, drawn once in physics.combat.base ([0.5, 1.5]), times their hunger
(fed 1, hungry 0.75, starving 0.5), plus the one best weapon they hold (a blade 5, a crude weapon 2). A fighter who attacks or raids
uses that weapon up and spends combat.food_cost food, win or lose.

Who fights. Only those at the place at night. Raiders and attackers who have walked away, or whose target has, do nothing. A raid is
defended by the house's household asleep there (combat.asleep x their defence) and by anyone standing guard at the place (full
defence plus combat.guard). An attack on a person is met by the target's defence (plus combat.guard if on guard) and by everyone else
on guard there.

The contest, as in the harm model: P = the attackers' strength, D = the defence; X = 2 (D + 1).
    raid    success with chance P^2 / (P^2 + (X/2)^2): the raiders take combat.raid_share of the house's food, shared equally; with
            chance P^2 / (P^2 + X^2) one defender is also wounded (robbed of the food it carries, left starving). Repelled: each
            raider is wounded with chance combat.counter x D / (P + D), dropping the food it carries.
    attack  kill with chance P^2 / (P^2 + X^2): the target dies and the attackers share what it carried; wound with chance
            P^2 / (P^2 + (X/2)^2): the target is robbed of the food it carries and left starving. Repelled: as for a raid.
"""
from __future__ import annotations

ITEMS_TAKEN = ("food",)


def hunger(w, name) -> float:
    return float(w.p["hunger_yield"][w.s["agents"][name]["stage"]])


def best_weapon(w, name):
    h = w.s["agents"][name]["holdings"]
    for item in ("blade", "crude"):
        if h.get(item, 0.0) >= 1 - 1e-9:
            return item
    return None


def weapon_q(w, item) -> float:
    return float(w.p["combat"]["weapon"].get(item, 0.0)) if item else 0.0


def attack_strength(w, name) -> float:
    return w.s["agents"][name]["attack"] * hunger(w, name) + weapon_q(w, best_weapon(w, name))


def defence_strength(w, name) -> float:
    return w.s["agents"][name]["defence"] * hunger(w, name) + weapon_q(w, best_weapon(w, name))


def _spend(w, fighters) -> dict:
    """Each fighter uses up its best weapon and spends its food cost. Returns the weapon each used."""
    used = {}
    fc = float(w.p["combat"]["food_cost"])
    for f in fighters:
        h = w.s["agents"][f]["holdings"]
        item = best_weapon(w, f)
        used[f] = item
        if item:
            h[item] = round(h[item] - 1, 6)
        h["food"] = round(max(0.0, h["food"] - fc), 6)
    return used


def wound(w, name, to=None) -> float:
    """Robbed of the food it carries (to the given takers, or dropped into its house stock), and left starving."""
    a = w.s["agents"][name]
    q = a["holdings"]["food"]
    a["holdings"]["food"] = 0.0
    if to:
        for b in to:
            w.s["agents"][b]["holdings"]["food"] = round(w.s["agents"][b]["holdings"]["food"] + q / len(to), 6)
    else:
        h = w.home(name)
        if h is not None:
            h["stock"]["food"] = round(h["stock"]["food"] + q, 6)
    a["stage"] = -2
    return round(q, 2)


def _counter(w, rng, fighters, P, D) -> list:
    hit = []
    p = float(w.p["combat"]["counter"]) * (D / (P + D) if P + D > 0 else 0.0)
    for f in fighters:
        if rng.random() < p:
            wound(w, f)
            hit.append(f)
    return hit


def resolve(w) -> list:
    out = []
    fights = w.s["fights"]
    guards = set(w.s["guards"])
    cc = w.p["combat"]
    raids = {}
    for f in fights:
        if f["kind"] == "raid":
            raids.setdefault(f["house"], []).append(f["by"])
    for hid in sorted(raids):
        h = w.s["houses"][hid]
        node = h["node"]
        raiders = sorted({r for r in raids[hid] if w.s["agents"][r]["alive"] and w.s["agents"][r]["at"] == node})
        rec = {"kind": "raid", "house": hid, "node": node, "raiders": raiders}
        if not raiders:
            rec["outcome"] = "fizzled"
            out.append(rec)
            continue
        defenders = sorted(n for n in w.at(node) if n not in raiders and (w.s["agents"][n]["household"] == h["household"] or n in guards))
        P = round(sum(attack_strength(w, r) for r in raiders), 4)
        D = round(sum(defence_strength(w, d) + float(cc["guard"]) if d in guards else float(cc["asleep"]) * defence_strength(w, d)
                      for d in defenders), 4)
        used = _spend(w, raiders)
        X = 2 * (D + 1)
        p_win, p_harm = P ** 2 / (P ** 2 + (X / 2) ** 2), P ** 2 / (P ** 2 + X ** 2)
        rng = w.rng("raid", w.r, hid)
        u = rng.random()
        rec.update({"defenders": defenders, "guards": [d for d in defenders if d in guards], "P": P, "D": D,
                    "p": round(p_win, 4), "roll": round(u, 4), "weapons": used})
        if u < p_win:
            took = round(h["stock"]["food"] * float(cc["raid_share"]), 6)
            h["stock"]["food"] = round(h["stock"]["food"] - took, 6)
            for r in raiders:
                w.s["agents"][r]["holdings"]["food"] = round(w.s["agents"][r]["holdings"]["food"] + took / len(raiders), 6)
            rec.update({"outcome": "taken", "took": round(took, 2)})
            if u < p_harm and defenders:
                victim = defenders[rng.randrange(len(defenders))]
                rec["wounded"] = [victim]
                rec["robbed"] = wound(w, victim, to=raiders)
        else:
            rec["outcome"] = "repelled"
            rec["wounded"] = _counter(w, rng, raiders, P, D)
        out.append(rec)
    attacks = {}
    for f in fights:
        if f["kind"] == "attack":
            attacks.setdefault(f["target"], []).append(f["by"])
    for target in sorted(attacks):
        t = w.s["agents"][target]
        rec = {"kind": "attack", "target": target, "node": t["at"]}
        attackers = sorted({a for a in attacks[target] if w.s["agents"][a]["alive"] and w.s["agents"][a]["at"] == t["at"]})
        rec["attackers"] = attackers
        if not attackers or not t["alive"]:
            rec["outcome"] = "fizzled"
            out.append(rec)
            continue
        helpers = sorted(g for g in guards if g != target and g not in attackers and w.s["agents"][g]["alive"]
                         and w.s["agents"][g]["at"] == t["at"])
        P = round(sum(attack_strength(w, a) for a in attackers), 4)
        D = round(defence_strength(w, target) + (float(cc["guard"]) if target in guards else 0.0)
                  + sum(defence_strength(w, g) for g in helpers), 4)
        used = _spend(w, attackers)
        X = 2 * (D + 1)
        p_kill, p_wound = P ** 2 / (P ** 2 + X ** 2), P ** 2 / (P ** 2 + (X / 2) ** 2)
        rng = w.rng("attack", w.r, target)
        u = rng.random()
        rec.update({"guards": helpers, "P": P, "D": D, "p_kill": round(p_kill, 4), "p_wound": round(p_wound, 4),
                    "roll": round(u, 4), "weapons": used})
        if u < p_kill:
            rec["outcome"] = "killed"
            rec["killed"] = target
            w.die(target, "attack", to={a: 1.0 / len(attackers) for a in attackers})
        elif u < p_wound:
            rec["outcome"] = "wounded"
            rec["robbed"] = wound(w, target, to=attackers)
        else:
            rec["outcome"] = "repelled"
            rec["wounded"] = _counter(w, rng, attackers, P, D)
        out.append(rec)
    return out
