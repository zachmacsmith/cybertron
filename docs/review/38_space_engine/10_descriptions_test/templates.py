"""Small template renderer for observations: a few phrasings per fact, seeded choice and order."""
import json, random, sys

# Each fact key -> list of phrasings; {v} is the fact's value, {t} the target.
POOLS = {
    "storeys": ["{t} stands {v} storeys high", "{t} rises {v} storeys", "{t}, {v} storeys tall,"],
    "material": ["built of {v}", "of {v}"],
    "condition": ["and looks {v}", "and is {v} with age", "its walls {v}"],
    "chimney": ["the chimney is {v}", "its chimney is {v}"],
    "door": ["the door is {v}", "its door is {v}"],
    "shutters": ["the shutters are {v}", "its shutters are {v}"],
    "beam": ["you can see that {v}", "your eye catches that {v}", "a builder's eye finds that {v}"],
    "look": ["{t} looks {v}", "{t} is {v}"],
    "wound": ["there is {v}", "he has {v}"],
    "carrying": ["he carries {v}", "he is bent under {v}"],
    "came_from": ["he has come from {v}", "he is back from {v}"],
    "gait": ["he is {v}", "you see him {v}"],
    "crop": ["{t} is in {v}", "{t} is sown with {v}"],
    "ripeness": ["the grain is {v}", "it stands {v}"],
    "weeds": ["{v}", "the rows are choked with {v}"],
    "damage": ["the crop is {v}", "part of it lies {v}"],
    "tracks_in_damage": ["with {v} in the mud", "and you read {v} there"],
    "wind": ["the wind is {v}", "a {v} wind blows"],
    "birds": ["{v}", "overhead, {v}"],
    "smoke": ["{v}", "you see {v}"],
    "sky": ["the sky is {v}", "overhead the sky is {v}"],
    "deer_tracks": ["there are {v}", "you find {v}"],
    "boot_tracks": ["there is {v}", "you also find {v}"],
    "freshness": ["all made {v}", "every print made {v}"],
    "ground": ["in the {v}", "pressed into {v}"],
}
# Facts that set the scene rather than describe the target.
SCENE = {"season": ["It is {v}", "In the {v}"], "time": ["{v}", "this {v}"]}
# Facts that only make sense attached to another fact (appended to it).
ATTACH = {"material": "storeys", "condition": "storeys", "tracks_in_damage": "damage", "ground": "boot_tracks"}


def render(state, seed):
    rnd = random.Random(seed)
    t = state["target"]
    facts = dict(state["visible_facts"])
    def ph(k, v):
        return rnd.choice(POOLS[k]).format(v=v, t=t)
    clauses = {}
    for k, v in facts.items():
        if k in SCENE or k in ATTACH:
            continue
        clauses[k] = ph(k, v)
    for k, host in ATTACH.items():
        if k in facts and host in clauses:
            clauses[host] += " " + ph(k, facts[k])
    keys = list(clauses)
    head, rest = keys[0], keys[1:]   # the defining fact leads; the rest are shuffled
    rnd.shuffle(rest)
    order = [head] + rest
    cut = 1 + len(order) // 2 if len(order) > 2 else len(order)
    s1 = ", ".join(clauses[k] for k in order[:cut])
    s2 = "; ".join(clauses[k] for k in order[cut:])
    scene = [rnd.choice(SCENE[k]).format(v=facts[k]) for k in ("season", "time") if k in facts]
    if scene:
        s1 = ", ".join(scene) + ": " + s1
    out = s1[0].upper() + s1[1:] + "."
    if s2:
        out += " " + s2[0].upper() + s2[1:] + "."
    return out.replace(",,", ",")


if __name__ == "__main__":
    states = json.load(open(sys.argv[1]))
    for st in states:
        for seed in (1, 2):
            print(st["id"], seed, render(st, seed))
