"""What an agent is told. World terms only: no scores, no game (scenario_design §3); concrete options with exact syntax; "Any
actions you do not use are wasted" kept (36c: without it agents took half as many actions).

The system prompt (fixed for the run, so it caches) says who the agent is, the place, the household, its aim and the rules with
their numbers. The turn prompt says where it is, who is with it, what it holds, its house, its hunger, the forest here, what it
heard and what its last actions did.
"""
from __future__ import annotations

from cybertron2.act import NAMES
from cybertron2.world import CONDITION, STAGES, World, show

SCHEMA = {
    "type": "object",
    "properties": {
        "actions": {"type": "array", "items": {"type": "object", "properties": {
            "do": {"type": "string", "enum": list(NAMES)}, "to": {"type": "string"}, "item": {"type": "string"},
            "qty": {"type": "number"}, "party": {"type": "string"}}, "required": ["do"]}},
        "say": {"type": "array", "items": {"type": "string"}},
        "tell": {"type": "array", "items": {"type": "object", "properties": {"to": {"type": "string"}, "text": {"type": "string"}},
                                             "required": ["to", "text"]}},
        "note": {"type": "string"},
    },
    "required": ["actions"],
}


def _places(w: World) -> str:
    out = []
    for nid, n in w.s["nodes"].items():
        nb = ", ".join(w.s["nodes"][x]["name"] + f' ("{x}")' for x in w.s["edges"][nid])
        out.append(f'- {n["name"]} ("{nid}"): {n["text"]} Next to: {nb}.')
    return "\n".join(out)


def system_prompt(w: World, name: str) -> str:
    a, p = w.s["agents"][name], w.p
    h = w.home(name)
    kin = [n for n, b in w.s["agents"].items() if b["household"] == a["household"] and n != name]
    others = [n for n, b in w.s["agents"].items() if b["household"] != a["household"]]
    cold = sorted(r + 1 for r in w.cold_rounds)
    winter = f"Winter comes in round {cold[0]} and lasts {len(cold)} rounds (to round {cold[-1]})." if cold else "There is no winter."
    sc, scc = p["shelter"], p["shelter_cold"]
    return f"""You are {name}, {a['role']}{f', aged {a["age"]}' if a.get('age') else ''}. You live with the {a['household']} household in {h['name']} in {w.s['nodes'][h['node']]['name']}: {', '.join(kin)}. The other people in this forest are {', '.join(others)}.

What you want: {a['aim']}

The places:
{_places(w)}

How life works here (each round):
- You have {p['actions']} actions a round ({p['actions'] - 1} when hungry, 2 when starving). Any actions you do not use are wasted.
- Food. At the end of every round you eat: {p['ration']:g} food when you sleep in a sound house. Sleeping in a damaged or overcrowded house you need {sc['damaged']:g}; sleeping anywhere else (out in the woods, or with no house) {sc['unsheltered']:g}. You eat from what you carry first, then, if you sleep at your own house, from its stock. If you cannot eat the whole amount you eat nothing that night and go hungry; hungry, then starving; three nights in a row without a meal and you may die. A full meal moves you back up one step.
- Food you carry loses {int(p['spoil']['hands'] * 100)}% a round; food in a house's stock {int(p['spoil']['house'] * 100)}%.
- The forest: foraging gives about {w.s['nodes'][next(n for n in w.s['nodes'] if w.s['nodes'][n]['plants'])]['plants']['yield']:g} food when the plants are plentiful, less as they thin; they grow back over rounds, slowly in winter. Hunting: alone you mostly catch small game (about 1 food); a party of 3 to 6 hunting together gives each hunter a fair chance of a deer (5) or a large animal (20); each hunter keeps what they catch; the game grows back slowly. Hungry you gather and hunt three quarters as well, starving half as well. Felling gives {p['fell']['timber']:g} timber and shrinks the wood a little for good. At most {p['gather_per_round']} forage, hunt or fell actions a round.
- {winter} In winter the plants hardly grow and the game grows back at half speed. In a winter round you need {scc['housed']:g} food in a sound house with its fire lit, {scc['no_fuel']:g} if the fire is out, {scc['damaged']:g} in a damaged house and {scc['unsheltered']:g} out in the cold, and a night out in the cold may leave you starving the next round ({int(p['cold']['starving'] * 100)}% each night).
- The fire: a house burns {p['fuel']['normal']:g} timber a round from its stock when anyone sleeps there, {p['fuel']['cold']:g} in winter. With no timber in its stock the fire goes out.
- Houses break now and then (more often in winter): a damaged house needs {p['repair']['work']} repair actions there and {p['repair']['timber']:g} timber in its stock; a house that breaks again is ruined.
- You can hand food or timber only to someone at the same place, and use your house's stock only at your house.
- What you say is heard by everyone at the place where you end the round; tell is private to one person there. Both are free (at most 3 a round in all).

Reply with JSON only: {{"actions": [up to {p['actions']} actions, done in order], "say": ["..."], "tell": [{{"to": "Name", "text": "..."}}], "note": "notes to yourself, shown to you every round"}}.
Actions:
{{"do": "travel", "to": "<place id>"}}   move to a place next to yours
{{"do": "forage"}}   gather plants where you are
{{"do": "hunt", "party": "<a name>"}}   hunt where you are; everyone here naming the same party hunts together (leave out party to hunt alone)
{{"do": "fell"}}   cut timber where you are
{{"do": "give", "to": "<name>", "item": "food" | "timber", "qty": <number>}}
{{"do": "store", "item": "food" | "timber", "qty": <number>}}   put into your house's stock (at your house)
{{"do": "take", "item": "food" | "timber", "qty": <number>}}   take from your house's stock (at your house)
{{"do": "repair"}}   work on your damaged house (at your house)
{{"do": "rest"}}"""


def turn_prompt(w: World, name: str, results: list, heard: list) -> str:
    a = w.s["agents"][name]
    here = a["at"]
    node = w.s["nodes"][here]
    h = w.home(name)
    rnd = w.r + 1
    cold = sorted(r + 1 for r in w.cold_rounds)
    if w.cold():
        season = f"It is winter (round {rnd}; it lasts to round {cold[-1]})."
    elif cold and rnd < cold[0]:
        season = f"Winter comes in {cold[0] - rnd} round{'s' if cold[0] - rnd != 1 else ''} (round {cold[0]})."
    else:
        season = "Winter is over." if cold else ""
    company = [n for n in w.at(here) if n != name]
    forest = []
    if node["plants"]:
        forest.append(f"plants {w.plants_word(here)}")
    if node["game"]:
        forest.append(f"game {w.game_word(here)}")
    lines = [f"Round {rnd} of {w.rounds}. {season} You have {w.actions_for(name)} actions this round.",
             f"You are at {node['name']} (\"{here}\"){': ' + ', '.join(forest) if forest else ''}. "
             + (f"With you: {', '.join(company)}." if company else "Nobody else is here."),
             f"You carry {show(a['holdings']['food'])} food and {show(a['holdings']['timber'])} timber. You are {STAGES[a['stage']]}"
             + (f" ({a['missed']} night{'s' if a['missed'] != 1 else ''} without a meal)." if a["missed"] else ".")]
    if h:
        sleepers = sum(1 for n in w.living() if w.s["agents"][n]["house"] == a["house"])
        lines.append(f"{h['name']} (in {w.s['nodes'][h['node']]['name']}): {CONDITION[h['condition']]}"
                     + (f", repair work {h['work']} of {w.p['repair']['work']}" if h["condition"] < 2 and h["work"] else "")
                     + f"; {sleepers} living in it, {h['beds']} beds; stock {show(h['stock']['food'])} food, {show(h['stock']['timber'])} timber.")
    kin = [n for n, b in w.s["agents"].items() if b["household"] == a["household"] and n != name]
    seen = []
    for n in kin:
        b = w.s["agents"][n]
        seen.append(f"{n} died in round {b['died'] + 1}" if not b["alive"] else f"{n} at {w.s['nodes'][b['at']]['name']}")
    lines.append("Your household: " + "; ".join(seen) + ".")
    dead = [n for n, b in w.s["agents"].items() if not b["alive"] and b["household"] != a["household"]]
    if dead:
        lines.append("Dead: " + ", ".join(f"{n} (round {w.s['agents'][n]['died'] + 1})" for n in dead) + ".")
    if results:
        lines.append("What you did last round:\n" + "\n".join(f"- {r}" for r in results))
    if heard:
        lines.append("What you heard last round:\n" + "\n".join(f"- {x}" for x in heard))
    if a["notes"]:
        lines.append(f"Your notes: {a['notes']}")
    lines.append("Decide this round's actions.")
    return "\n\n".join(lines)
