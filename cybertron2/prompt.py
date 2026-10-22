"""What an agent is told (docs/review/38_space_engine/02_perception.md §4). World terms only: no scores, no game (scenario_design
§3); concrete options with exact syntax; "Any actions you do not use are wasted" kept.

The system prompt (fixed for the run, so it caches): who the agent is, its household and the others, the land, its aim, the rules
with their numbers, the reply format. The turn prompt, in sections:

    Now                 round, season, actions
    Here                the place and its signs (with change since you last saw it), its houses (yours exact; others in words),
                        the people here (how they look, what they visibly carry)
    Seen last round     what you witnessed at the places you were, and at night
    You                 your hunger, what you carry, what you need tonight if you sleep here
    Your house          exact when you are there; otherwise as you last saw it, and how long ago
    Elsewhere           your household and others as you last saw them, places as you last saw them (at most ELSEWHERE_ROUNDS old)
    Lasting memories    deaths, fights, gifts, the cold
    Earlier rounds      one line each (the summary band)
    Last rounds         the last FULL_ROUNDS in full: what you did and its results, what you saw, what you heard
    Your notes
The reply carries a "why" field: a few sentences on why the agent chose its actions, so a run shows its intentions. (A field
named "reasoning" that asks for "your thinking" is refused by the Sonnet 5.5 safeguard with this system prompt: review 38.03.)
"""
from __future__ import annotations

import collections

from cybertron2 import perceive as PC
from cybertron2.act import NAMES
from cybertron2.world import CONDITION, ITEM_WORDS, ITEMS, STAGES, World, show

SCHEMA = {
    "type": "object",
    "properties": {
        "why": {"type": "string"},
        "actions": {"type": "array", "items": {"type": "object", "properties": {
            "do": {"type": "string", "enum": list(NAMES)}, "to": {"type": "string"}, "item": {"type": "string"},
            "qty": {"type": "number"}, "party": {"type": "string"}, "target": {"type": "string"}, "house": {"type": "string"}},
            "required": ["do"]}},
        "say": {"type": "array", "items": {"type": "string"}},
        "tell": {"type": "array", "items": {"type": "object", "properties": {"to": {"type": "string"}, "text": {"type": "string"}},
                                             "required": ["to", "text"]}},
        "note": {"type": "string"},
    },
    "required": ["why", "actions"],
}


def _features(w, nid) -> list:
    n = w.s["nodes"][nid]
    f = []
    if n["plants"]:
        f.append("plants to forage")
    if n["game"]:
        f.append("game to hunt")
    if n["timber"]:
        f.append("trees to fell")
    if n["copper"]:
        f.append(f"a copper seam ({n['copper']:g} copper a dig)")
    if n["forge"]:
        f.append("a forge")
    houses = [h["name"] for h in w.s["houses"].values() if h["node"] == nid]
    if houses:
        f.append(", ".join(houses))
    return f


def _places(w: World) -> str:
    out = []
    for nid, n in w.s["nodes"].items():
        nb = ", ".join(w.place(x) + f' ("{x}")' for x in w.s["edges"][nid])
        feats = _features(w, nid)
        out.append(f'- {n["name"]} ("{nid}"): {n["text"]}' + (f" [{'; '.join(feats)}]" if feats else "") + f" Next to: {nb}.")
    return "\n".join(out)


def _households(w, name) -> str:
    me = w.s["agents"][name]
    out = []
    for hid, h in w.s["houses"].items():
        members = [n for n, a in w.s["agents"].items() if a["household"] == h["household"]]
        if h["household"] == me["household"]:
            continue
        out.append(f"the {h['household']} household ({', '.join(members)}), whose house is {h['name']} in {w.place(h['node'])}")
    return "; ".join(out)


def system_prompt(w: World, name: str) -> str:
    a, p = w.s["agents"][name], w.p
    h = w.home(name)
    kin = [n for n, b in w.s["agents"].items() if b["household"] == a["household"] and n != name]
    cold = sorted(r + 1 for r in w.cold_rounds)
    winter = f"Winter comes in round {cold[0]} and lasts {len(cold)} rounds (to round {cold[-1]})." if cold else "There is no winter."
    sc, scc, cb = p["shelter"], p["shelter_cold"], p["combat"]
    cannot = (f"\nYou do not know how to {' or '.join(a['cannot'])}: your people never learned." if a["cannot"] else "")
    return f"""You are {name}, {a['role']}{f', aged {a["age"]}' if a.get('age') else ''}. You live with the {a['household']} household in {h['name']} in {w.place(h['node'])}: {', '.join(kin)}. Others in this land: {_households(w, name)}.{cannot}

What you want: {a['aim']}

The land:
{_places(w)}

How life works here (each round):
- You have {p['actions']} actions a round ({p['actions'] - 1} when hungry, 2 when starving). Any actions you do not use are wasted.
- Food. At the end of every round you eat: {p['ration']:g} food when you sleep in a sound house. In a damaged or overcrowded house you need {sc['damaged']:g}; sleeping anywhere else (out in the open, or with no house) {sc['unsheltered']:g}. You eat from what you carry first, then, if you sleep at your own house, from its stock. Eating less than {p['ration']:g} is a missed meal: hungry, then starving; three missed meals in a row and you may die. Eating at least {p['ration']:g} but less than you needed holds you where you are; a full meal moves you back up one step.
- Food you carry loses {int(p['spoil']['hands'] * 100)}% a round; food in a house's stock {int(p['spoil']['house'] * 100)}%.
- Gathering: foraging gives up to about 2 food when the plants are plentiful, less as they thin; they grow back over rounds, slowly in winter. Hunting: alone you mostly catch small game (about 1 food); everyone hunting at the same place in the same round hunts together, and a party of 3 to 6 gives each hunter a fair chance of a deer (5) or a large animal (20); each keeps what they catch; game grows back slowly and walks in from the land around. Felling gives {p['fell']['timber']:g} timber and shrinks the wood a little for good. Hungry you gather three quarters as well, starving half. At most {p['gather_per_round']} forage, hunt, fell or dig actions a round.
- Making: a blade takes {p['forge']['copper']:g} copper and {p['forge']['timber']:g} timber at a forge; a club (crude weapon) takes {p['craft']['timber']:g} timber, anywhere.
- {winter} In winter the plants hardly grow and the game grows back at half speed. In a winter round you need {scc['housed']:g} food in a sound house with its fire lit, {scc['no_fuel']:g} if the fire is out, {scc['damaged']:g} in a damaged house and {scc['unsheltered']:g} out in the cold, and a night out in the cold may leave you starving the next round ({int(p['cold']['starving'] * 100)}% each night).
- The fire: a house burns {p['fuel']['normal']:g} timber a round from its stock when anyone sleeps there, {p['fuel']['cold']:g} in winter.
- Houses break now and then (more often in winter): a damaged house needs {p['repair']['work']} repair actions there and {p['repair']['timber']:g} timber in its stock.
- Fighting happens at night, between whoever is at the place then. Attack someone (or raid a house for its food) where they are: it takes {cb['attack_actions']} actions and {cb['food_cost']:g} food you carry, and uses up your best weapon (a blade counts far more than a club, a club more than bare hands), win or lose. A fight can kill, or wound (the wounded is robbed of the food they carry and left starving), or be driven off. A raid that succeeds takes most of a house's food. Those asleep at home defend it weakly; anyone who stands guard defends the people and houses at their place strongly. Hunger weakens a fighter; you cannot fight while starving.
- You see only what is where you are. What you know of elsewhere is what you last saw there, or what you were told.
- You can hand goods only to someone at the same place, and use your house's stock only at your house.
- What you say is heard by everyone at the place where you end the round; tell is private to one person there. Both are free (at most 3 a round in all).

Reply with JSON only: {{"why": "why you chose these actions, in a few sentences", "actions": [actions, done in order, up to your actions this round], "say": ["..."], "tell": [{{"to": "Name", "text": "..."}}], "note": "notes to yourself, shown to you every round"}}.
Actions:
{{"do": "travel", "to": "<place id>"}}   move to a place next to yours
{{"do": "forage"}} | {{"do": "hunt"}} (add "party": "<name>" only to hunt apart from others here) | {{"do": "fell"}} | {{"do": "mine"}}
{{"do": "forge"}}   a blade, at a forge | {{"do": "craft"}}   a club
{{"do": "give", "to": "<name>", "item": "<{' | '.join(ITEMS)}>", "qty": <number>}}
{{"do": "store", "item": "...", "qty": <number>}} | {{"do": "take", "item": "...", "qty": <number>}}   your house's stock (at your house)
{{"do": "repair"}}   your damaged house (at your house)
{{"do": "guard"}}   stand guard here tonight
{{"do": "attack", "target": "<name>"}}   ({cb['attack_actions']} actions) | {{"do": "raid", "house": "<house id>"}}   ({cb['raid_actions']} actions)
{{"do": "rest"}}
House ids: {', '.join(f'{h["name"]} = "{hid}"' for hid, h in w.s["houses"].items())}."""


def _goods(holdings, items=ITEMS) -> str:
    parts = [f"{show(holdings[i])} {ITEM_WORDS.get(i, i) if i in ITEM_WORDS else i}" for i in items if holdings.get(i, 0) > 1e-9]
    return ", ".join(parts) if parts else "nothing"


def _seen(w, entries, here) -> list:
    """What was witnessed, grouped by place and then by person: "At the Meadow: Cela foraged (2 times), stood guard". Night events
    and other lines that are not one person's act stay whole."""
    by_place = collections.OrderedDict()
    for e in entries:
        by_place.setdefault(e["place"], []).append(e["text"])
    out = []
    for place, texts in by_place.items():
        acts, whole = collections.OrderedDict(), []
        for t in texts:
            who = t.split(" ", 1)[0]
            if who in w.s["agents"] and not t.startswith("At night") and " died" not in t:
                acts.setdefault(who, collections.Counter())
                acts[who][t.split(" ", 1)[1]] += 1
            elif t not in whole:
                whole.append(t)
        parts = [f"{who} " + ", ".join(v + (f" ({c} times)" if c > 1 else "") for v, c in verbs.items()) for who, verbs in acts.items()]
        where = "here" if place == w.place(here) else f"at {place}"
        if parts:
            out.append(f"{where[0].upper() + where[1:]}: " + "; ".join(parts) + ".")
        out += [f"{x} ({where})." for x in whole]
    return out


def turn_prompt(w: World, name: str) -> str:
    a = w.s["agents"][name]
    k = PC.store(w, name)
    here = a["at"]
    node = w.s["nodes"][here]
    h = w.home(name)
    rnd = w.r + 1
    cold = sorted(r + 1 for r in w.cold_rounds)
    if w.cold():
        season = f"It is winter (it lasts to round {cold[-1]})."
    elif cold and rnd < cold[0]:
        season = f"Winter comes in {cold[0] - rnd} round{'s' if cold[0] - rnd != 1 else ''} (round {cold[0]})."
    else:
        season = "Winter is over." if cold else ""
    out = [f"Round {rnd} of {w.rounds}. {season} You have {w.actions_for(name)} actions this round."]

    # Here
    prev = k.get("prev_places", {}).get(here)
    signs = []
    for key, word in (("plants", w.plants_word(here)), ("game", w.game_word(here))):
        if word:
            was = prev.get(key) if prev and prev.get("round", w.r) < w.r else None
            signs.append(f"{key} {word}" + (f" (were {was} {PC.age(w, prev['round'])})" if was and was != word else ""))
    lines = [f"Here: {node['name']} (\"{here}\")" + (": " + ", ".join(signs) if signs else "") + "."]
    for hid, hh in w.s["houses"].items():
        if hh["node"] == here and hid != a["house"]:
            lines.append(f"{hh['name']} is here: {CONDITION[hh['condition']]}, it looks {w.stock_word(hid)}.")
    company = [n for n in w.at(here) if n != name]
    lines.append("With you: " + ", ".join(f"{n} ({w.condition_word(n)}; {w.load_word(n)})" for n in company) + "."
                 if company else "Nobody else is here.")
    out.append("\n".join(lines))

    # Seen last round
    last = k["full"][-1] if k["full"] else None
    if last and last["seen"]:
        out.append("Seen last round:\n" + "\n".join(f"- {x}" for x in _seen(w, last["seen"], here)[:12]))

    # You
    tonight = w.p["ration"] * w.shelter_mult(w.shelter(name))
    you = [f"You: {STAGES[a['stage']]}" + (f", {a['missed']} missed meal{'s' if a['missed'] != 1 else ''} in a row" if a["missed"] else "")
           + f". You carry {_goods(a['holdings'])}. If you sleep here tonight you need {tonight:g} food."]
    if a["cannot"]:
        you.append(f"You cannot {' or '.join(a['cannot'])}.")
    out.append(" ".join(you))

    # Your house
    if h:
        n_live = sum(1 for n in w.living() if w.s["agents"][n]["house"] == a["house"])
        if h["node"] == here:
            line = (f"Your house, {h['name']} (here): {CONDITION[h['condition']]}"
                    + (f", repair work {h['work']} of {w.p['repair']['work']}" if h["condition"] < 2 and h["work"] else "")
                    + f"; {n_live} living in it, {h['beds']} beds; stock {_goods(h['stock'])}.")
            old = k.get("prev_house")
            if old and old["round"] < w.r - 1:
                diffs = [f"{show(abs(h['stock'][i] - old['stock'].get(i, 0)))} {'more' if h['stock'][i] > old['stock'].get(i, 0) else 'less'} {i}"
                         for i in ITEMS if abs(h["stock"][i] - old["stock"].get(i, 0)) >= 0.5]
                if diffs:
                    line += f" Since you last saw it ({PC.age(w, old['round'])}): {', '.join(diffs)}."
        else:
            seen = k.get("house")
            line = (f"Your house, {h['name']} (in {w.place(h['node'])}): as you last saw it {PC.age(w, seen['round'])}, "
                    f"{CONDITION[seen['condition']]}, stock {_goods(seen['stock'])}." if seen else
                    f"Your house, {h['name']}, is in {w.place(h['node'])}.")
        out.append(line)

    # Elsewhere
    kin = [n for n, b in w.s["agents"].items() if b["household"] == a["household"] and n != name]
    ew = []
    for n in kin + sorted(n for n in k["people"] if n not in kin):
        b = w.s["agents"][n]
        p = k["people"].get(n)
        if n in company:
            continue
        if not b["alive"] and any(n in m["text"] and "died" in m["text"] or "killed " + n in m["text"] for m in k["memories"]):
            ew.append(f"{n}: dead")
            continue
        if p and w.r - p["round"] <= PC.ELSEWHERE_ROUNDS:
            ew.append(f"{n}: at {w.place(p['at'])} {PC.age(w, p['round'])}, {p['condition']}, {p['load']}")
        elif n in kin:
            ew.append(f"{n}: not seen for {w.r - p['round']} rounds" if p else f"{n}: not seen")
    for pid, pl in k["places"].items():
        if pid == here or w.r - pl["round"] > PC.ELSEWHERE_ROUNDS:
            continue
        s = ", ".join(f"{key} {pl[key]}" for key in ("plants", "game") if pl.get(key))
        hs = "; ".join(f"{w.s['houses'][x]['name']} looked {v}" for x, v in pl["houses"].items() if x != a["house"])
        if s or hs:
            ew.append(f"{w.place(pid)} {PC.age(w, pl['round'])}: " + "; ".join(x for x in (s, hs) if x))
    if ew:
        out.append("Elsewhere, as you last knew it:\n" + "\n".join(f"- {x}" for x in ew))

    # Memories
    if k["memories"]:
        out.append("Lasting memories:\n" + "\n".join(f"- {m['text']}" for m in k["memories"]))
    older = [r for r in k["rounds"] if r["round"] < w.r - PC.FULL_ROUNDS]
    if older:
        out.append("Earlier rounds:\n" + "\n".join(f"- Round {r['round'] + 1}: {r['line']}" for r in older[-PC.SUMMARY_ROUNDS:]))
    for f in k["full"]:
        part = [f"Round {f['round'] + 1}, what you did:"] + [f"- {x}" for x in f["did"]]
        if f["heard"]:
            part += ["What you heard:"] + [f"- {x}" for x in f["heard"]]
        if f is not last and f["seen"]:
            part += ["What you saw:"] + [f"- {x}" for x in _seen(w, f["seen"], here)[:8]]
        out.append("\n".join(part))
    if a["notes"]:
        out.append(f"Your notes: {a['notes']}")
    out.append("Decide this round's actions.")
    return "\n\n".join(out)
