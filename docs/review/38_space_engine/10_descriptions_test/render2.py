"""Run 2: observer's-eye rendering with Haiku and Sonnet from richer facts; a Sonnet clause-by-clause check per description;
a small comprehension check (Haiku, sensible reader) on the model texts."""
import json
from concurrent.futures import ThreadPoolExecutor
from run import call
from run2 import ANSWER_SYS2
from templates2 import render

STATES = json.load(open("states2.json"))
EYE_SYS = (
    "You write what one person in a pre-industrial village perceives, through their eyes, in 1-3 sentences of plain in-world "
    "English (second person). Choose what this person would notice first and how they would put it, with emphasis fitting who "
    "they are, their state and what they care about. Hard rule: every clause must state or directly imply one of the given "
    "visible facts, or what the observer is said to know; nothing else: no new places, objects, people, times, causes or "
    "numbers, and no guesses stated as fact. You need not use every fact, but do not drop any that bear on what this person "
    "cares about. No game terms. Reply with the description only.")
CHECK_SYS = (
    "You check a short description against the facts it was written from. Split the description into clauses. For each clause "
    "give the keys of the visible facts or observer fields it rests on, or [] if it rests on none (an invention). List the keys of "
    "any hidden facts it states, hints at or implies. List the keys of visible facts it conveys. Reply with JSON only: "
    '{"clauses": [{"clause": "...", "supports": ["key", ...]}], "leaked": ["key", ...], "conveyed": ["key", ...]}')
MODELS = {"haiku": "claude-haiku-5-5", "sonnet": "claude-sonnet-5-5"}


def eye_prompt(st):
    return json.dumps({"target": st["target"], "observer": st["observer"], "visible_facts": st["visible_facts"]}, indent=1)


def main():
    res = {st["id"]: {"template2": render(st, 1)} for st in STATES}
    jobs = [(st["id"], m) for st in STATES for m in MODELS]
    by = {st["id"]: st for st in STATES}
    with ThreadPoolExecutor(3) as ex:
        for (sid, m), r in zip(jobs, ex.map(lambda j: call(MODELS[j[1]], EYE_SYS, eye_prompt(by[j[0]])), jobs)):
            res[sid][m] = r

    def check(j):
        sid, m = j
        st = by[sid]
        p = json.dumps({"visible_facts": st["visible_facts"], "observer": st["observer"], "hidden_facts": st["hidden_facts"],
                        "description": res[sid][m]["text"]}, indent=1)
        return call("claude-sonnet-5-5", CHECK_SYS, p)

    def answer(j):
        sid, m = j
        qs = "\n".join(f"{i+1}. {q['q']}" for i, q in enumerate(by[sid]["questions"]))
        return call("claude-haiku-5-5", ANSWER_SYS2, f"What you perceived:\n{res[sid][m]['text']}\n\nQuestions:\n{qs}")

    with ThreadPoolExecutor(3) as ex:
        checks = list(ex.map(check, jobs))
        answers = list(ex.map(answer, jobs))
    for (sid, m), c, a in zip(jobs, checks, answers):
        res[sid][m]["check"] = c
        res[sid][m]["answers"] = a
    json.dump(res, open("raw_outputs2.json", "w"), indent=1)


if __name__ == "__main__":
    main()
