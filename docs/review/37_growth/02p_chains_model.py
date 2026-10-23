"""Supply chains for the first worlds: labour through each chain, returns by trade, rents at chokepoints, returns to capital and
know-how, trade between the nodes of the first region. The model behind docs/review/37_growth/02p_chains.md (analysis for Zach;
nothing here is decided).

The catalogue (gathering, recipes, buildings, tool effects, specialised tools) is imported from 02m_recipes_model.py, so the two
models cannot drift. Goods 02m does not yet cost (flour, bread, milk, cheese, a great beam, charcoal) are added here from
proposals/recipes.md §10-§15, marked ADDED. Units are 38.06's work units (6 a day for an adult); 1 food is valued at about 1 unit.
Every number is a PROPOSAL. Deterministic. Run: python docs/review/37_growth/02p_chains_model.py
"""
from __future__ import annotations

import importlib.util
import pathlib

_SPEC = importlib.util.spec_from_file_location("m02m", pathlib.Path(__file__).with_name("02m_recipes_model.py"))
M = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(M)

DAY, table = M.DAY, M.table
WEIGHT = dict(M.WEIGHT)
WEIGHT.update({"flour": 1, "bread": 1, "milk": 1, "cheese": 0.5, "great beam": 40, "charcoal": 2})

# ---------------------------------------------------------------- ADDED recipes (recipes.md §10, §11, §14, §15)
QUERN, HAND_MILL, WATER_MILL = 4, 12, 40           # grain ground per unit of work (recipes.md §10)
MILK_PER_UNIT, MILK_FOOD = 3, 0.5                  # milking: 1 unit, 3 milk; a milk feeds 0.5 (recipes.md §11)
CHEESE = (6, 0.2, 1, 2.0)                          # 6 milk, 0.2 salt, 1 unit -> 1 cheese feeding 2 (recipes.md §14)
BEAM_UNITS = 18                                    # a felling axe and three people for a day (recipes.md §15)
MEAT_FOOD = 1.5                                    # one meat feeds 1.5 (D2-41)


def cost(good: str) -> float:
    """Full cost in units down to the land; 02m's, extended with the ADDED goods."""
    if good == "flour":                            # by hand quern
        return M.cost("grain") + 1 / QUERN
    if good == "flour (water mill)":
        return M.cost("grain") + 1 / WATER_MILL
    if good == "bread":                            # 10 flour + 1 timber + 1 unit -> 11
        return (10 * cost("flour") + M.cost("timber") + 1) / 11
    if good == "milk":
        return 1 / MILK_PER_UNIT                   # the cow's keep is set aside here (livestock.md)
    if good == "cheese":
        m, s, u, _ = CHEESE
        return m * cost("milk") + s * M.cost("salt") + u
    if good == "great beam":
        return BEAM_UNITS
    if good == "charcoal":                         # proposed in finding 1: 5 timber + 1 unit -> 1 charcoal
        return 5 * M.cost("timber") + 1
    if good in M.SPECIAL:
        _, cu, units, *_ = M.SPECIAL[good]
        return units + cu * M.cost("copper")
    return M.cost(good)


# ---------------------------------------------------------------- 1. labour through each chain
def steps(good: str, qty: float = 1.0, out=None) -> dict:
    """Units of work at each step to make qty of good, down to the land: {step: (units, where)}."""
    out = {} if out is None else out

    def add(label, units, where):
        u, _ = out.get(label, (0.0, where))
        out[label] = (u + units, where)

    if good == "grain":
        add("grow grain", qty * M.cost("grain"), "fields")
    elif good == "hide":
        add("hide (by-product of slaughter or the hunt)", qty * 1.0, "a herd, the hunt")
    elif good in M.GATHER:
        site, units, yld, *_ = M.GATHER[good]
        add(f"gather {good}", qty * units / yld, site)
    elif good in ("flour", "flour (water mill)"):
        steps("grain", qty, out)
        rate = QUERN if good == "flour" else WATER_MILL
        add("grind" if good == "flour" else "grind (water mill)", qty / rate, "a quern" if good == "flour" else "a mill")
    elif good == "bread":
        steps("flour", qty * 10 / 11, out)
        steps("timber", qty / 11, out)
        add("bake", qty / 11, "a hearth")
    elif good == "milk":
        add("milk a cow", qty / MILK_PER_UNIT, "a cow in milk")
    elif good == "cheese":
        m, s, u, _ = CHEESE
        steps("milk", qty * m, out)
        steps("salt", qty * s, out)
        add("make cheese", qty * u, "a cool room or cellar")
    elif good == "great beam":
        add("fell a great tree (felling axe, a crew)", qty * BEAM_UNITS, "old oaks in a woodland")
    elif good in M.SPECIAL:
        _, cu, units, *_ = M.SPECIAL[good]
        steps("copper", qty * cu, out)
        add(f"forge {good}", qty * units, "a smithy (master)")
    elif good in M.MAKE:
        q, ins, units, _, place, trade, _ = M.MAKE[good]
        for g, n in ins.items():
            steps(g, qty * n / q, out)
        add(f"make {good}", qty * units / q, place or "anywhere")
    else:
        raise KeyError(good)
    return out


def build_steps(blueprint: str) -> dict:
    mat, units, needs, _ = M.BUILD[blueprint]
    out = {}
    for g, n in mat.items():
        steps(g, n, out)
    out["build"] = (units, needs)
    return out


CHAIN_GOODS = ["hand tool", "blade", "coin", "lock", "plough", "cart", "harness", "saddle", "salt", "salted meat", "parchment",
               "document", "flour", "bread", "cheese", "felling axe", "miner's pick", "scythe", "mason's chisels",
               "reaping hook", "great beam"]
CHAIN_BUILDINGS = ["small room (wattle and timber)", "large room, a hall (timber on stone)", "stone room, medium", "hearth",
                   "anvil and bellows", "millstones", "water wheel", "beds (each)"]


def chains():
    rows = []
    for g in CHAIN_GOODS:
        s = steps(g)
        tot = sum(u for u, _ in s.values())
        top = max(s.items(), key=lambda kv: kv[1][0])
        parts = "; ".join(f"{k} {u:.2f}" for k, (u, _) in sorted(s.items(), key=lambda kv: -kv[1][0]))
        rows.append([g, f"{tot:.2f}", f"{top[0]} ({top[1][0] / tot:.0%}, {top[1][1]})", parts])
    print("## 1. Labour through each chain (units per unit of the good, down to the land)\n")
    print(table(rows, ["good", "units", "the dominant step (share, where)", "every step"]))
    rows = []
    for b in CHAIN_BUILDINGS:
        s = build_steps(b)
        tot = sum(u for u, _ in s.values())
        top = max(s.items(), key=lambda kv: kv[1][0])
        rows.append([b, f"{tot:.1f}", f"{tot / DAY:.1f}", f"{top[0]} ({top[1][0] / tot:.0%})"])
    print("\n## 1b. Buildings: labour through the chain\n")
    print(table(rows, ["blueprint", "units", "worker-days", "the dominant step"]))
    rows = [
        ["copper", "3 ore (9) + 4 timber (8) = 17", "1", "x17", "at the seam, and only with wood there"],
        ["salt", "3 timber (6)", "2", "x3", "at the spring (with wood), or sun-dried on a shore"],
        ["cheese", "6 milk (6)", "0.5", "x12", "where the cows are"],
        ["flour", "1 grain (1)", "1", "x1", "anywhere: milling saves work, not weight"],
        ["parchment", "1 hide (1)", "4 sheets (0.2)", "x5", "where hides are"],
        ["charcoal (proposed)", "5 timber (10)", "1 (2)", "x5", "at the wood, carried to the ore"],
    ]
    print("\n## 1c. Weight before and after the step that changes it (Weber)\n")
    print(table(rows, ["good", "weight in", "weight out", "falls by", "so the step belongs"]))


# ---------------------------------------------------------------- 2. what buyers save: the value ceilings
def hand_tool_value() -> float:
    """Units a copper hand tool saves a household over its life, against crude tools (02m's worksheet)."""
    saved = uses_k = crude_wear = 0.0
    for m, u in M.HOUSEHOLD_UNITS.items():
        if m == "hunt":
            continue
        b, c, k, w, *_ = M.METHODS[m]
        saved += u - u * c / k
        uses_k += u * c / k / 2 * w
        crude_wear += u / 2 * w / M.TOOLS["crude tool"][0] * M.cost("crude tool")
    tools_a_year = uses_k / M.TOOLS["hand tool"][0]
    return (saved + crude_wear) / tools_a_year


def salt_value() -> float:
    """Food a salt keeps: 0.2 salt keeps a meat that would lose about 88% in 6 days fresh (30% a day) against 11% salted."""
    kept = (1 - 0.7 ** 6) - (1 - 0.98 ** 6)
    return kept * MEAT_FOOD / 0.2


def plough_value() -> float:
    """A plough's 60 uses each save the hoe's work less the plough's (02l), less a village team's ox cost per use."""
    from_02l_hoe, from_02l_plough, ox_year, uses_year = 3.0, 0.75, 19.0, 60
    return 60 * ((from_02l_hoe - from_02l_plough) - ox_year / uses_year)


def special_value(t: str) -> float:
    m, cu, units, x, life, _ = M.SPECIAL[t]
    saved = M.USE_UNITS * (1 - 1 / x)
    return life * saved + cost("hand tool") * life / M.TOOLS["hand tool"][0]   # its work saved, and hand tools not worn


VALUE = {   # good: (what one is worth to a buyer, the basis)
    "hand tool": (hand_tool_value(), "a household's units saved over its life against crude tools (02m worksheet)"),
    "blade": (40 * 0.3 * 2 * MEAT_FOOD, "hunting only: 40 hunts in its life at +30% catch (x1.3); worth more in a fight"),
    "coin": (1.0, "accepted at about a food (an anchor, not a cost)"),
    "lock": (80, "on a store or treasury: about 8 units of theft stopped a year for 10 years (household: about 20)"),
    "plough": (plough_value(), "60 uses, each saving the hoe's work less the plough's, less the shared ox (02l)"),
    "salt": (salt_value(), "the meat it keeps from rotting"),
    "flour (water mill)": (1 / QUERN - 1 / WATER_MILL, "the quern's work it saves (only if grain must be ground to eat)"),
    "cheese": (CHEESE[3], "food that keeps, from milk that would otherwise spoil"),
    "felling axe": (special_value("felling axe"), "a woodsman's work saved over its 80 uses"),
    "miner's pick": (special_value("miner's pick"), "a miner's work saved over its 80 uses"),
    "scythe": (special_value("scythe"), "a herder's work saved over its 80 uses"),
    "mason's chisels": (special_value("mason's chisels"), "a mason's work saved over its 80 uses"),
    "reaping hook": (special_value("reaping hook"), "a reaper's work saved over its 80 uses (more: +10% grain)"),
    "great beam": (30, "rough: what the stone alternative (arches, columns) costs more for a hall over 25"),
}


def own_units_and_inputs(good: str):
    """The maker's own units for one unit of good, and its bought inputs at full cost."""
    if good == "flour (water mill)":
        return 1 / WATER_MILL, 0.0                 # the miller grinds others' grain: a service
    if good == "cheese":
        m, s, u, _ = CHEESE
        return u + m * cost("milk"), s * cost("salt")   # the dairy milks its own cows
    if good in M.SPECIAL:
        _, cu, units, *_ = M.SPECIAL[good]
        return units, cu * cost("copper")
    if good == "great beam":
        return BEAM_UNITS, 0.0
    q, ins, units, *_ = M.MAKE[good]
    return units / q, sum(n * cost(g) for g, n in ins.items()) / q


TRADES = [("smith", "hand tool"), ("smith", "blade"), ("smith", "coin"), ("smith", "lock"), ("master smith", "felling axe"),
          ("master smith", "miner's pick"), ("master smith", "scythe"), ("master smith", "mason's chisels"),
          ("master smith", "reaping hook"), ("carpenter", "plough"), ("salter", "salt"), ("miller", "flour (water mill)"),
          ("dairy", "cheese"), ("woodsman", "great beam")]


def returns():
    print("\n## 2. Returns per unit of work by trade\n")
    print("At full-cost prices every trade earns its skill x its tool's multiplier, by construction: a novice 0.5, a competent "
          "maker 1, a master 2 (trades); basic work 1-1.5; a copper tool doubles a woodsman's return. So the comparison that "
          "matters is at what buyers would pay at most, below.\n")
    rows = []
    for trade, g in TRADES:
        own, bought = own_units_and_inputs(g)
        v, basis = VALUE[g]
        c = 1 / WATER_MILL if g == "flour (water mill)" else cost(g)    # the miller sells the grinding, not the grain
        r = lambda s: (v - bought) / (own / s)
        rows.append([trade, g, f"{c:.3g}", f"{v:.3g}", f"{v / c:.1f}", f"{r(0.5):.1f}", f"{r(1):.1f}", f"{r(2):.1f}", basis])
    print(table(rows, ["trade", "good", "full cost", "worth to a buyer", "worth / cost", "return a unit: novice",
                       "competent", "master", "basis of the worth"]))


# ---------------------------------------------------------------- 3. rents at chokepoints
FOOT, PACK_OX, OX_CART = 0.93, 0.26, 0.09         # units per unit of weight per edge, empty return (02g in work units)


def rents():
    print("\n## 3. Rents at chokepoints (the most a holder could capture; competition and buyers' patience set the actual)\n")
    region = 40 * DAY                              # the first region's work a day
    copper_at_millford = cost("copper") + 2 * FOOT * WEIGHT["copper"]
    copper_derived = VALUE["hand tool"][0] - 3 - 0.5 * M.cost("timber")   # what a copper is worth made into a hand tool
    copper_per_year = 25                           # the region's copper a year: tools, coin, ploughs, carts, locks, blades
    salt_delivered = cost("salt") + FOOT * WEIGHT["salt"]
    salt_per_year = 80                             # about 20 slaughters (3 salt each) and some cheese
    mill_flour_day = {"grain must be ground to eat": 28, "only bread is ground": 4}   # Millford and Barleyfield
    rows = []
    r_cu = (copper_derived - copper_at_millford) * copper_per_year / 40
    rows.append(["the copper seam (with a smelter)", f"cost at Millford {copper_at_millford:.1f}; worth as a tool up to "
                 f"{copper_derived:.0f}", f"{copper_derived - copper_at_millford:.0f} a copper", f"{copper_per_year} a year",
                 f"{r_cu:.0f}", f"{r_cu / region:.0%}"])
    r_salt = (VALUE["salt"][0] - salt_delivered) * salt_per_year / 40
    rows.append(["the salt spring", f"cost delivered {salt_delivered:.1f}; worth {VALUE['salt'][0]:.1f}",
                 f"{VALUE['salt'][0] - salt_delivered:.1f} a salt", f"{salt_per_year} a year", f"{r_salt:.1f}",
                 f"{r_salt / region:.0%}"])
    for case, n in mill_flour_day.items():
        per = VALUE["flour (water mill)"][0] if case.startswith("grain") else 0.1   # bread's tenth more food, as the gain
        rows.append([f"the water mill ({case})", f"the quern's {1 / QUERN:.2f} a ration against {1 / WATER_MILL:.3f}",
                     f"{per:.2f} a ration", f"{n} a day", f"{per * n:.1f}", f"{per * n / region:.1%}"])
    beam_rent = VALUE["great beam"][0] - cost("great beam") - 2 * OX_CART * WEIGHT["great beam"]
    rows.append(["old oaks (great beams)", f"cost {cost('great beam'):.0f} + hauling by ox cart", f"{beam_rent:.0f} a beam",
                 "a hall a decade", "-", "~0"])
    rows.append(["a quarry", "stone 1 unit, weight 3: never carried far", "small where every node has one; a gate where none "
                 "does (hearths need stone)", "-", "-", "-"])
    rows.append(["a smithy (the building)", "about 49 units to build", "none in the building: the rent is in copper "
                 "access and a master's know-how", "-", "-", "-"])
    print(table(rows, ["chokepoint", "cost against worth", "rent at most", "volume", "rent a day (units)",
                       "share of the region's work"]))


# ---------------------------------------------------------------- 4. returns to capital and know-how
def capital():
    print("\n## 4. Returns to capital and know-how\n")
    smithy = sum(sum(u for u, _ in build_steps(b).values()) for b in ("medium room (timber on stone)", "hearth",
                                                                       "anvil and bellows"))
    mill = sum(sum(u for u, _ in build_steps(b).values()) for b in ("small room (wattle and timber)", "millstones",
                                                                     "water wheel"))
    cart_team = cost("cart") + 2 * 20 + 2 * cost("harness")
    rows = []
    margin_tool = 0.25 * cost("hand tool")                     # a smith's 25% markup over full cost
    rows.append(["smithy", f"{smithy:.0f}", "25% markup on 25 copper items a year", f"{margin_tool * 25:.0f} a year",
                 f"{smithy / (margin_tool * 25) * 40:.0f} days"])
    for toll, label in ((1 / 16, "a sixteenth"), (1 / 8, "an eighth")):
        per_day = 28 * toll * M.cost("grain")
        rows.append([f"water mill, toll {label} of the grain (grain must be ground)", f"{mill:.0f}", "28 rations a day",
                     f"{per_day:.1f} a day", f"{mill / per_day:.0f} days"])
    rows.append(["water mill (only bread is ground)", f"{mill:.0f}", "about 4 loaves a day", "about 0.1 a day", "never"])
    for load in (15, 30, 60):
        per_day = (FOOT - OX_CART) * load
        rows.append([f"ox cart, 2 oxen, harness: merchant carrying {load} weight a day one edge", f"{cart_team:.0f}",
                     "the walk it saves buyers", f"{per_day:.0f} a day", f"{cart_team / per_day:.0f} days"])
    for t in M.SPECIAL:
        _, cu, units, x, life, _ = M.SPECIAL[t]
        saved = M.USE_UNITS * (1 - 1 / x)
        rows.append([f"{t} (full-time specialist)", f"{cost(t):.0f}", "about 2.4 uses a day", f"{saved * 2.4:.1f} a day",
                     f"{cost(t) / (saved * 2.4):.0f} days"])
    print(table(rows, ["capital", "cost (units)", "use", "return", "payback"]))
    smith_units_year = 25 * 3                                  # 25 copper items at about 3 units each
    rows = [
        ["teaching one session (knowledge.md: teacher 2, learner 4)", "6 units", "novice to capable"],
        ["a capable smith against a novice (units per hand tool 3 against 6)", f"{smith_units_year:.0f} units saved a year",
         "the session repays itself about 12 times in a year"],
        ["a master against a competent smith (1.5 against 3 units a tool)", f"{smith_units_year / 2:.0f} units a year",
         f"about {smith_units_year / 2 / DAY:.0f} worker-days a year"],
        ["a master woodsman (x1.5 on basic work) with a felling axe (x3) against a competent one with a crude tool",
         "x4.5 timber per unit", "the specialist's whole case"],
    ]
    print("\n" + table(rows, ["know-how", "worth", "note"]))


# ---------------------------------------------------------------- 5. trade between the nodes of the first region (02f §4)
FLOWS = [
    # good, from, to, edges
    ("grain", "Barleyfield", "Millford (to the mill)", 1),
    ("flour or bread", "Millford", "Barleyfield", 1),
    ("copper", "Coppergate", "Millford (smithy)", 2),
    ("hand tool", "Millford", "Barleyfield, Ashwood", 1),
    ("timber (fuel)", "Ashwood", "Millford", 1),
    ("timber (smelting fuel: 4 a copper)", "Ashwood", "Coppergate", 1),
    ("charcoal (proposed: 0.8 a copper)", "Ashwood", "Coppergate", 1),
    ("stone", "a quarry", "the next node", 1),
    ("salt", "outside the region", "everyone", 2),
    ("cheese", "a pasture node", "the towns", 2),
    ("hides", "Barleyfield, Ashwood", "Millford", 1),
    ("documents", "Millford", "anywhere", 2),
]
_FLOW_COST = {"grain": ("grain", 1), "flour or bread": ("bread", 1), "copper": ("copper", 1), "hand tool": ("hand tool", 1),
              "timber (fuel)": ("timber", 2), "timber (smelting fuel: 4 a copper)": ("timber", 2),
              "charcoal (proposed: 0.8 a copper)": ("charcoal", 2), "stone": ("stone", 3), "salt": ("salt", 1),
              "cheese": ("cheese", 0.5), "hides": ("hide", 1), "documents": ("document", 0.05)}


def region():
    print("\n## 5. Trade between the nodes of the first region (Millford, Barleyfield, Ashwood, Coppergate)\n")
    rows = []
    for g, a, b, e in FLOWS:
        key, w = _FLOW_COST[g]
        c = cost(key)
        foot, cart = e * FOOT * w, e * OX_CART * w
        verdict = ("on foot" if foot < 0.3 * c else "by pack animal or cart" if cart < 0.3 * c else "never far")
        rows.append([g, a, b, e, f"{c:.2f}", f"+{foot / c:.0%}", f"+{cart / c:.0%}", verdict])
    print(table(rows, ["good", "from", "to", "edges", "cost at source", "carrying on foot", "by ox cart", "travels"]))
    print(f"\nA merchant with an ox cart earns, against buyers walking it themselves, about {FOOT - OX_CART:.2f} units per unit "
          f"of weight per edge: {(FOOT - OX_CART) * 200:.0f} units for a full 200-weight load, so its income is set by the "
          "region's volume, not by the cart. At 30 weight a day it is about 25 units a day: four worker-days.")


# ---------------------------------------------------------------- 6. the grinding question, both ways
def grinding():
    print("\n## 6. If grain must be ground to eat (a quern, about 0.25 units a ration) or not\n")
    rows = []
    for case, grind in (("porridge needs no grinding (D2-44 as decided)", 0.0), ("grain must be ground (proposed)", 1 / QUERN)):
        ration = M.cost("grain") + grind
        rows.append([case, f"{ration:.2f}", f"{ration / DAY:.0%}",
                     "only bread and travel food" if grind == 0 else "every ration: a village of 15 grinds about 4 units a day",
                     "a tenth more food a loaf: never pays" if grind == 0 else f"saves {1 / QUERN - 1 / WATER_MILL:.2f} a ration: "
                     "pays for a village of a few households"])
    print(table(rows, ["case", "units a ration of grain", "share of a 6-unit day", "the mill grinds", "the mill"]))


if __name__ == "__main__":
    chains()
    returns()
    rents()
    capital()
    region()
    grinding()
