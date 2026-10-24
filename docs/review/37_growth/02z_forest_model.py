"""A forest as a system: standing trees, young growth, dead wood; timber, firewood and charcoal; what felling, gathering, cutting
and grazing do to it over a run. The model behind docs/cybertron2/proposals/forests.md (exploration for Zach; nothing decided).

Units: wood in the engine's timber (weight 2); heat in hearth-nights (a hearth needs 1 a normal night, 4 a cold one: today's 0.5 and
2 timber, so a timber gives 2 heat). Time in days; a year is 24 days (the compressed calendar), so trees grow as in a real year each
24 days. A unit of work is worth about 1 food (02p). Deterministic. Run: python docs/review/37_growth/02z_forest_model.py
"""
from __future__ import annotations

YEAR = 24
HEAT = {"timber": 2.0, "firewood": 0.5, "charcoal": 6.0}          # heat a unit (proposed)
WEIGHT = {"timber": 2, "firewood": 1, "charcoal": 2}
WORK = {"fell": 1.5, "gather": 3.0, "cut": 5.0}                    # a unit of work: timber felled (crude tool); dead wood gathered
                                                                   # (no tool, at a full pool); young growth cut (a tool)

# per unit of forest size (a unit of size is about 2 ha, the land a plot of 16 seed takes), by kind, at roughly real magnitudes:
# standing timber T (a high forest holds hundreds of tonnes a hectare; a timber here is about 240 kg, from a hearth's 21 a year
# against a household's few tonnes), young growth Y and dead wood W as firewood (4 firewood to a timber's mass: firewood is bundles
# of a quarter the heat); yearly rates: trees grow (grow_T), young growth regrows (grow_Y), trees shed dead wood (shed, a share of T a
# year), dead wood rots (decay)
KINDS = {
    "old forest": dict(T=2500, Y=50, W=300, grow_T=0.005, grow_Y=0.5, shed=0.01, decay=0.3),
    "managed wood (coppice)": dict(T=600, Y=400, W=100, grow_T=0.01, grow_Y=1.0, shed=0.01, decay=0.3),
    "copse": dict(T=300, Y=40, W=50, grow_T=0.01, grow_Y=0.6, shed=0.01, decay=0.3),
    "scrub": dict(T=0, Y=60, W=10, grow_T=0.0, grow_Y=0.6, shed=0.0, decay=0.3),
}
FIREWOOD_PER_TIMBER = 4      # firewood to a timber's mass
BRASH = 1.0                  # firewood left as dead wood for each timber felled (branches)


def run(kind: str, size: float, days: int, fell_a_day: float = 0.0, gather_a_day: float = 0.0, cut_a_day: float = 0.0,
        grazed: bool = False) -> dict:
    """A forest parcel day by day: T grows slowly toward its capacity, Y regrows fast (not where grazed), trees shed dead wood (more
    when there are more of them), dead wood rots; felling takes T and leaves brash (1 firewood a timber) as dead wood."""
    k = KINDS[kind]
    KT, KY, KW = k["T"] * size, k["Y"] * size, k["W"] * size
    T, Y, W = KT, KY, KW
    got = {"timber": 0.0, "firewood": 0.0}
    short = 0
    for _ in range(days):
        T += k["grow_T"] / YEAR * T * (1 - T / KT) if KT else 0
        if not grazed:
            Y += k["grow_Y"] / YEAR * max(Y, 0.05 * KY) * (1 - Y / KY) if KY else 0
        W += k["shed"] / YEAR * T * FIREWOOD_PER_TIMBER - k["decay"] / YEAR * W     # shedding from the trees there; rotting
        f = min(fell_a_day, T)
        T -= f
        W += f * BRASH                                                      # brash: firewood for each timber felled
        got["timber"] += f
        g = min(gather_a_day, W * min(1.0, W / max(KW, 1e-9)) ** 0.5)       # harder to find as the pool thins
        W -= g
        c = min(cut_a_day, Y)
        Y -= c
        got["firewood"] += g + c
        if g + c + 1e-9 < gather_a_day + cut_a_day:
            short += 1
    return dict(T=T / KT if KT else 0, Y=Y / KY if KY else 0, W=W / KW if KW else 0, short_days=short, **got,
                cover=("forest" if KT and T / KT > 0.4 else "scrub" if KT else kind))


def sustained(kind: str, size: float) -> float:
    """Firewood a year that dead wood and young growth give without running down: what the trees shed less what rots, and the young
    growth's best yearly regrowth."""
    k = KINDS[kind]
    shed = k["shed"] * k["T"] * size * FIREWOOD_PER_TIMBER
    young = k["grow_Y"] * k["Y"] * size / 4
    return shed + young


def row(cells):
    print("| " + " | ".join(str(c) for c in cells) + " |")


if __name__ == "__main__":
    print("## 1. Heat for work and for weight\n")
    row(["Fuel", "Heat a unit", "Weight", "Heat a unit of weight", "How it is got", "Heat a unit of work"])
    row(["---"] * 6)
    row(["timber", HEAT["timber"], WEIGHT["timber"], HEAT["timber"] / WEIGHT["timber"], "felled from standing trees, with a tool",
         HEAT["timber"] * WORK["fell"]])
    row(["firewood (dead wood)", HEAT["firewood"], WEIGHT["firewood"], HEAT["firewood"] / WEIGHT["firewood"],
         "gathered by hand, while the pool lasts", HEAT["firewood"] * WORK["gather"]])
    row(["firewood (young growth)", HEAT["firewood"], WEIGHT["firewood"], HEAT["firewood"] / WEIGHT["firewood"],
         "cut with a tool (coppicing)", HEAT["firewood"] * WORK["cut"]])
    row(["charcoal", HEAT["charcoal"], WEIGHT["charcoal"], HEAT["charcoal"] / WEIGHT["charcoal"], "burned from 5 timber, 2 units",
         f"{HEAT['charcoal'] / (5 / WORK['fell'] + 2):.1f}"])

    hearth_year = (YEAR - 6) * 1 + 6 * 4
    print(f"\nA hearth needs about {hearth_year} heat a year ({YEAR - 6} normal nights, 6 cold): {hearth_year / HEAT['timber']:.0f} timber "
          f"or {hearth_year / HEAT['firewood']:.0f} firewood.\n")

    print("## 2. What a wood gives back each year without running down (firewood), and what it holds (timber)\n")
    row(["Kind (a unit of size)", "Standing timber", "Firewood a year, sustained", "Heat a year, sustained", "Hearths it keeps warm"])
    row(["---"] * 5)
    for kind in KINDS:
        s = sustained(kind, 1)
        row([kind, KINDS[kind]["T"], f"{s:.0f}", f"{s * HEAT['firewood']:.0f}", f"{s * HEAT['firewood'] / hearth_year:.2f}"])

    print("\n## 3. A village of 3 hearths over 48 days (two winters) on a copse of size 1\n")
    need = 2 * hearth_year
    row(["Plan", "Timber got", "Firewood got", "Heat got", "Heat needed", "Days short", "Copse after: trees / young / dead wood", "Cover after"])
    row(["---"] * 8)
    for label, kw in [("gather dead wood only, 5 a day", dict(gather_a_day=5)),
                      ("fell its trees, 2.6 a day (the whole need as timber)", dict(fell_a_day=2.6)),
                      ("fell its trees hard, 8 a day (and sell the rest)", dict(fell_a_day=8)),
                      ("gather 3 and cut young growth 2 a day", dict(gather_a_day=3, cut_a_day=2)),
                      ("the same, the village's cattle in the copse", dict(gather_a_day=3, cut_a_day=2, grazed=True))]:
        r = run("copse", 1, 48, **kw)
        heat = r["timber"] * HEAT["timber"] + r["firewood"] * HEAT["firewood"]
        row([label, f"{r['timber']:.0f}", f"{r['firewood']:.0f}", f"{heat:.0f}", f"{3 * need:.0f}", r["short_days"],
             f"{r['T']:.0%} / {r['Y']:.0%} / {r['W']:.0%}", r["cover"]])

    after = run("copse", 1, 48, fell_a_day=8)
    print(f"\nAfter felling hard, the copse sheds {KINDS['copse']['shed'] * KINDS['copse']['T'] * after['T'] * FIREWOOD_PER_TIMBER:.0f} "
          f"firewood a year instead of {KINDS['copse']['shed'] * KINDS['copse']['T'] * FIREWOOD_PER_TIMBER:.0f}: fewer trees, less dead wood.")
    print("\n## 4. An old forest of size 6 (a forest node) felled for a village's whole fuel for 48 days\n")
    for fell in (2.0, 4.0, 8.0, 40.0):
        r = run("old forest", 6, 48, fell_a_day=fell)
        print(f"- felling {fell:g} a day: {r['timber']:.0f} timber; trees left {r['T']:.0%}; dead wood {r['W']:.0%} of its usual; cover "
              f"{r['cover']}")
