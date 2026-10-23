"""Second pass: (1) comprehension with a reader allowed to draw sensible conclusions; (2) leak test where the narrator is also
given the hidden facts, marked as unknown to the observer (as a per-node narrator would hold the whole node's state)."""
import json
from concurrent.futures import ThreadPoolExecutor
from run import call, RENDER_SYS, STATES

ANSWER_SYS2 = ("You are a villager. You are given what you perceived. Answer each numbered question in one short sentence, as a "
               "sensible villager would, drawing reasonable conclusions from what you perceived. Say 'Cannot tell' only if what you "
               "perceived gives no basis for an answer.")
LEAK_SYS = RENDER_SYS + (" You are also shown hidden facts about the scene: the observer cannot perceive them, so they must not "
                         "appear, be hinted at or be implied in the description.")

res = json.load(open("raw_outputs.json"))
jobs = []
for st in STATES:
    qs = "\n".join(f"{i+1}. {q['q']}" for i, q in enumerate(st["questions"]))
    srcs = {"template": res[st["id"]]["template"], "haiku": res[st["id"]]["haiku"]["text"],
            "raw": json.dumps({"target": st["target"], **st["visible_facts"]})}
    for name, text in srcs.items():
        jobs.append(("answers2", st["id"], name, ANSWER_SYS2, f"What you perceived:\n{text}\n\nQuestions:\n{qs}"))
    full = {"target": st["target"], "observer": st["observer"], "visible_facts": st["visible_facts"],
            "hidden_facts": st["hidden_facts"]}
    jobs.append(("leak_test", st["id"], "haiku", LEAK_SYS, json.dumps(full, indent=1)))
with ThreadPoolExecutor(3) as ex:
    for (kind, sid, name, _, _), r in zip(jobs, ex.map(lambda j: call("claude-haiku-5-5", j[3], j[4]), jobs)):
        res[sid].setdefault(kind, {})[name] = r
json.dump(res, open("raw_outputs.json", "w"), indent=1)
