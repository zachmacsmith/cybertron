"""Run 2 templates: the run-1 pools plus pools for the sensory and ambient facts; clauses grouped into sentences of 3-4."""
import json, random, sys
from templates import POOLS as P1, SCENE, ATTACH

POOLS = dict(P1)
POOLS.update({
    "light": ["{v}", "there is {v}"],
    "weather": ["the day is {v}", "it is {v}"],
    "sound": ["you hear {v}", "{v}, you can hear"], "sound_inside": ["there is {v}", "you hear {v}"],
    "smell": ["you smell {v}", "there is a smell of {v}"],
    "sign_doorstep": ["{v}", "you see {v}"], "sign_chopping_block": ["there are {v}", "you see {v}"],
    "sign_hands": ["there is {v}", "you see {v}"], "sign_legs": ["he has {v}", "he is spattered with {v}"],
    "sign_fence": ["there is {v}", "you find {v}"], "sign_twig": ["there is {v}", "you find {v}"],
    "sign_droppings": ["there are {v}", "you see {v}"],
    "timber": ["{v}", "the load is {v}"],
    "stream": ["{v}", "you see {v}"], "frost": ["there is {v}", "you see {v}"], "trees": ["{v}", "you see {v}"],
    "about": ["{v}"],
})
WORDS = {1: "one", 2: "two", 3: "three", 4: "four"}


def render(state, seed, per_sentence=4):
    rnd = random.Random(seed)
    t, facts = state["target"], dict(state["visible_facts"])
    ph = lambda k, v: rnd.choice(POOLS[k]).format(v=WORDS.get(v, v), t=t)
    clauses = {k: ph(k, v) for k, v in facts.items() if k not in SCENE and k not in ATTACH}
    for k, host in ATTACH.items():
        if k in facts and host in clauses:
            clauses[host] += " " + ph(k, facts[k])
    # group: what the target is and shows; then sounds and smells; then light, weather and who is about. Shuffle within groups.
    def group(k):
        return 1 if k.startswith(("sound", "smell")) else 2 if k in ("light", "weather", "about", "frost", "stream", "trees") else 0
    keys = list(clauses)
    groups = [[k for k in keys if group(k) == g] for g in range(3)]
    for g in groups[0][1:], groups[1], groups[2]:
        rnd.shuffle(g)
    groups[0] = [groups[0][0]] + sorted(groups[0][1:], key=lambda k: rnd.random())
    sents = []
    for g in groups:
        for i in range(0, len(g), per_sentence):
            sents.append(", ".join(clauses[k] for k in g[i:i + per_sentence]))
    scene = [rnd.choice(SCENE[k]).format(v=facts[k]) for k in ("season", "time") if k in facts]
    if scene:
        sents[0] = ", ".join(scene) + ": " + sents[0]
    return " ".join(s[0].upper() + s[1:] + "." for s in sents)


if __name__ == "__main__":
    for st in json.load(open(sys.argv[1])):
        print(st["id"], render(st, 1), "\n")
