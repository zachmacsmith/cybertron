"""Render each state with templates and with Haiku/Sonnet via the claude CLI, then ask Haiku the comprehension questions."""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor
from templates import render

STATES = json.load(open("states.json"))
RENDER_SYS = ("You describe what one person in a pre-industrial village perceives. Write 1-2 sentences in plain in-world English, "
              "in the second person or about the target, using only the visible facts given. Invent nothing: no names, causes, "
              "numbers, events or details that are not in the facts. No game terms. Reply with the description only.")
ANSWER_SYS = ("You are a villager. You are given what you perceived. Answer each numbered question in one short sentence, using only "
              "what you perceived. If it does not tell you, say 'Cannot tell'.")


def call(model, system, prompt):
    t0 = time.time()
    out = subprocess.run(["claude", "-p", prompt, "--model", model, "--system-prompt", system, "--output-format", "json",
                          "--tools", "", "--no-session-persistence", "--setting-sources", ""],
                         capture_output=True, text=True, timeout=300)
    j = json.loads(out.stdout)
    u = j["usage"]
    return {"text": j["result"].strip(), "cost_usd": j["total_cost_usd"], "wall_s": round(time.time() - t0, 2),
            "api_ms": j["duration_api_ms"], "in_tokens": u["input_tokens"] + u["cache_creation_input_tokens"] + u["cache_read_input_tokens"],
            "out_tokens": u["output_tokens"]}


def render_prompt(st):
    return json.dumps({"target": st["target"], "observer": st["observer"], "visible_facts": st["visible_facts"]}, indent=1)


def main():
    res = {st["id"]: {"template": render(st, 1)} for st in STATES}
    jobs = [(st["id"], m, render_prompt(st)) for st in STATES for m in ("claude-haiku-5-5", "claude-sonnet-5-5")]
    with ThreadPoolExecutor(3) as ex:
        for (sid, m, _), r in zip(jobs, ex.map(lambda j: call(j[1], RENDER_SYS, j[2]), jobs)):
            res[sid][m.split("-")[1]] = r
    qjobs = []
    for st in STATES:
        qs = "\n".join(f"{i+1}. {q['q']}" for i, q in enumerate(st["questions"]))
        srcs = {"template": res[st["id"]]["template"], "haiku": res[st["id"]]["haiku"]["text"],
                "raw": json.dumps({"target": st["target"], **st["visible_facts"]})}
        for name, text in srcs.items():
            qjobs.append((st["id"], name, f"What you perceived:\n{text}\n\nQuestions:\n{qs}"))
    with ThreadPoolExecutor(3) as ex:
        for (sid, name, _), r in zip(qjobs, ex.map(lambda j: call("claude-haiku-5-5", ANSWER_SYS, j[2]), qjobs)):
            res[sid].setdefault("answers", {})[name] = r
    json.dump(res, open("raw_outputs.json", "w"), indent=1)


if __name__ == "__main__":
    main()
