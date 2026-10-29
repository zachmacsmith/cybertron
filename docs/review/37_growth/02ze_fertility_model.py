"""Can a population replace itself? Lifetime births per woman and the net reproduction rate (R0: daughters reaching adulthood per
woman) under the engine's rules for children (life.py, data.LIFE: D2-138 to D2-153), by how often couples try, how hard, the
lifespan, and how well the young are kept. Behind proposals/fertility.md (29 Oct; D2-162 decided pregnancy 2, gap 1, cap 0.8).

Each woman is followed night by night through her adult span as probabilities (free to conceive, pregnant, in the gap after a
birth), with the engine's own timing: she conceives on night c, gives birth on night c + P, and may conceive again from night
c + P + 1 + G. Elders do not try. Survival of a child to adulthood multiplies nightly risks through infancy and childhood (youths
have no risk of their own in the engine beyond hunger and cold, left out here). A woman's own death: 0.001 a night as an adult and
the childbirth risk. Hunger and cold deaths of adults are left out, so these are ceilings for a society that is fed and warm.
Deterministic. Run: python docs/review/37_growth/02ze_fertility_model.py
"""
from __future__ import annotations

import math
from collections import defaultdict

SHARES = [1 / 16, 1 / 8, 3 / 16, 5 / 8]          # infant, child, youth, adult: of the days to old age (data.LIFE)
ADULT_RISK = 0.001                                # a night (D2-149)

AS_BUILT = dict(preg=5, gap=4, base=0.5, k=0.5)
DECIDED = dict(preg=2, gap=1, base=0.8, k=0.5)    # D2-162 (29 Oct)

# nightly death risks of the young; the engine's (data.LIFE) and a proposed "vulnerable young" set (soft limits, proposal §4)
RATES = {
    "engine": dict(birth=0.03, birth_helped=0.5, inf_cared=0.02, inf_not=0.08, inf_hungry=2.0, inf_cold=2.0,
                   child=0.005, child_hungry=1.0, child_cold=1.0),
    "vulnerable young (proposed)": dict(birth=0.04, birth_helped=0.5, inf_cared=0.02, inf_not=0.15, inf_hungry=3.0, inf_cold=3.0,
                                        child=0.006, child_hungry=4.0, child_cold=3.0),
}
# how the young are kept, as shares of nights: hungry (missed a meal), cared for (an infant's carer gave the dial's units), cold
# (a cold night without a fire); births helped by another adult or not
KEEPING = {
    "well kept": dict(hungry=0.0, cared=1.0, cold=0.0, helped=True),
    "busy (infant cared half the nights)": dict(hungry=0.0, cared=0.5, cold=0.0, helped=True),
    "poor (hungry 1 night in 4, cold 1 in 4)": dict(hungry=0.25, cared=1.0, cold=0.25, helped=True),
    "neglected (uncared, hungry 1 in 3, cold 1 in 4)": dict(hungry=1 / 3, cared=0.0, cold=0.25, helped=False),
}


def spans(L: int) -> list:
    out = [max(1, round(s * L)) for s in SHARES]
    out[-1] = max(1, L - sum(out[:-1]))
    return out


def scaled(days: float, L: int, scale: bool = True) -> int:
    return max(1, round(days * L / 32)) if scale else max(1, round(days))


def births(L=32, tries=1.0, units=1, preg=5, gap=4, base=0.5, k=0.5, scale=True, helped=True) -> float:
    """Expected births to one woman over her adult span, trying on a share `tries` of the nights she may."""
    adult = spans(L)[3]
    P, G = scaled(preg, L, scale), scaled(gap, L, scale)
    p = base * (1 - math.exp(-k * units)) * tries
    mother = 0.02 * (0.5 if helped else 1.0)
    dist, out = {("free", 0): 1.0}, 0.0
    for n in range(adult):
        nd = defaultdict(float)
        for (s, c), q in dist.items():
            q *= 1 - ADULT_RISK
            if s == "free":
                nd[("preg", n)] += q * p
                nd[("free", 0)] += q * (1 - p)
            elif s == "preg":
                if n - c >= P:
                    out += q
                    nd[("gap", n + 1 + G)] += q * (1 - mother)
                else:
                    nd[(s, c)] += q
            else:
                nd[("free", 0) if n + 1 >= c else (s, c)] += q
        dist = nd
    return out


def survival(L=32, rates="engine", keeping="well kept") -> float:
    """The chance a child born alive... from birth to youth (the birth's own risk included)."""
    r, kp = RATES[rates], KEEPING[keeping]
    inf, child = spans(L)[:2]
    birth = r["birth"] * (r["birth_helped"] if kp["helped"] else 1.0)
    h, c, cold = kp["hungry"], kp["cared"], kp["cold"]
    base = c * r["inf_cared"] + (1 - c) * r["inf_not"]
    inf_p = base * (1 + h * (r["inf_hungry"] - 1)) * (1 + cold * (r["inf_cold"] - 1))
    ch_p = r["child"] * (1 + h * (r["child_hungry"] - 1)) * (1 + cold * (r["child_cold"] - 1))
    return (1 - birth) * (1 - min(1, inf_p)) ** inf * (1 - min(1, ch_p)) ** child


def r0(b: float, s: float) -> float:
    return b * s / 2


def row(cells):
    print("| " + " | ".join(str(c) for c in cells) + " |")


TRIES = [("every night", 1.0), ("3 nights in 4", 0.75), ("half the nights", 0.5), ("a third", 1 / 3), ("1 in 5", 0.2)]

if __name__ == "__main__":
    s_eng = survival()
    print("## 1. Lifetime births and R0 by how often a couple tries (lifespan 32, 1 unit each, the young well kept)\n")
    row(["How often", "As built: births", "As built: R0", "Decided (D2-162): births", "Decided: R0"])
    row(["---"] * 5)
    for label, t in TRIES:
        a, d = births(tries=t, **AS_BUILT), births(tries=t, **DECIDED)
        row([label, f"{a:.2f}", f"{r0(a, s_eng):.2f}", f"{d:.2f}", f"{r0(d, s_eng):.2f}"])
    print(f"\nA child well kept reaches youth with chance {s_eng:.2f} (engine rates); R0 1 needs about {2 / s_eng:.1f} births a woman.")

    print("\n## 2. How hard (units each a try), decided values, lifespan 32\n")
    row(["Units each", "Chance a night", "Every night: births", "Half the nights: births", "Half the nights: R0"])
    row(["---"] * 5)
    for u in (1, 2, 3):
        p = DECIDED["base"] * (1 - math.exp(-DECIDED["k"] * u))
        e, h = births(units=u, **DECIDED), births(units=u, tries=0.5, **DECIDED)
        row([u, f"{p:.2f}", f"{e:.2f}", f"{h:.2f}", f"{r0(h, s_eng):.2f}"])

    print("\n## 3. Lifespan: pregnancy and the gap scaled with lifespan (now) or fixed in days (decided values, 1 unit)\n")
    row(["Lifespan", "Adult days", "Scaled: every night", "Scaled: half", "Fixed: every night", "Fixed: half", "Fixed: a third"])
    row(["---"] * 7)
    for L in (32, 48, 64, 96):
        sc = [births(L=L, tries=t, scale=True, **DECIDED) for t in (1.0, 0.5)]
        fx = [births(L=L, tries=t, scale=False, **DECIDED) for t in (1.0, 0.5, 1 / 3)]
        row([L, spans(L)[3], *(f"{x:.1f}" for x in sc), *(f"{x:.1f}" for x in fx)])
    print("\n(Births a woman. Scaled, family size is the same at every lifespan; fixed, longer lives allow larger families, as people's do.)")

    print("\n## 4. Soft limits: how the young are kept, and what reaches youth (lifespan 32)\n")
    row(["Keeping", "Engine rates: reaches youth", "Vulnerable young: reaches youth",
         "Vulnerable: R0 every night", "Vulnerable: R0 half", "Vulnerable: R0 a third"])
    row(["---"] * 6)
    for kp in KEEPING:
        se, sv = survival(keeping=kp), survival(rates="vulnerable young (proposed)", keeping=kp)
        helped = KEEPING[kp]["helped"]
        bs = [births(tries=t, helped=helped, **DECIDED) for t in (1.0, 0.5, 1 / 3)]
        row([kp, f"{se:.2f}", f"{sv:.2f}", *(f"{r0(b, sv):.2f}" for b in bs)])

    print("\n## 5. The same at lifespan 64 with pregnancy and the gap fixed in days (the large-family option, §3)\n")
    row(["Keeping", "Vulnerable: reaches youth", "R0 every night", "R0 half", "R0 a third", "R0 1 in 5"])
    row(["---"] * 6)
    for kp in KEEPING:
        sv = survival(L=64, rates="vulnerable young (proposed)", keeping=kp)
        helped = KEEPING[kp]["helped"]
        bs = [births(L=64, tries=t, scale=False, helped=helped, **DECIDED) for t in (1.0, 0.5, 1 / 3, 0.2)]
        row([kp, f"{sv:.2f}", *(f"{r0(b, sv):.2f}" for b in bs)])

    print("\n## 6. What a child costs to youth, against an adult's working life (pregnancy +0.3 food a day; infant 0.5 food a day)\n")
    print("Low dial: 1 unit a day of infant care, a child eats 0.7. High dial: 3 units of infant care, a child eats 1.0 and needs 1 unit"
          " of minding a day (data.LIFE). An adult works about 6 units a day; a unit is worth about 1 food (02p).\n")
    row(["Lifespan", "Dial", "Food", "Units of care", "Total", "Adult days of work", "Share of a woman's adult span"])
    row(["---"] * 7)
    for L, scale in ((32, True), (64, True), (64, False)):
        inf, child = spans(L)[:2]
        P = scaled(DECIDED["preg"], L, scale)
        for dial, care_inf, eats, mind in (("low", 1.0, 0.7, 0.0), ("high", 3.0, 1.0, 1.0)):
            food = 0.3 * P + 0.5 * inf + eats * child
            care = care_inf * inf + mind * child
            tot = food + care
            row([f"{L}{'' if scale else ' (fixed)'}", dial, f"{food:.1f}", f"{care:.0f}", f"{tot:.1f}", f"{tot / 6:.1f}",
                 f"{tot / 6 / spans(L)[3]:.0%}"])
    print("\n(People: a child to working age costs several adult-years of food and care against 25 to 30 working years, about"
          " 20 to 30%.)")
