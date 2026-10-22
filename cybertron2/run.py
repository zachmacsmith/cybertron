"""The round loop. Each round: every living agent decides from the same state (model calls in parallel); the plans are carried out
interleaved, one action from each agent in turn, in an order shuffled per round from the seed; speech is delivered to whoever is
at the speaker's place when the round ends; then the world's end of round (world.end_of_round). Models are called through the old
engine's leaf backend (cybertron.llm: `claude -p` on the subscription, or the API).

Logs, in the run directory:
    run.json       the spec, each agent's model and system prompt
    turns.jsonl    one line per agent-round: the turn prompt, the reply, the results, usage and cost, any error
    rounds.jsonl   one line per round: the end-of-round record (hunts, meals, shelter, deaths, falls, breaks, stocks)
    state.json     the final state

The scripted bot ("bot" as an agent's model) is a smoke-test fixture (determinism, no crash), not evidence about behaviour.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import time
from pathlib import Path

from cybertron2 import act, prompt
from cybertron2.world import World, load_spec

MAX_SPEECH = 3


def bot_plan(w: World, name: str) -> dict:
    """A simple household bot: eat from the house, keep its fire, forage in the near wood."""
    a = w.s["agents"][name]
    h = w.home(name)
    home = h["node"]
    wood = next(n for n in w.s["edges"][home] if w.s["nodes"][n]["plants"])
    acts = []
    if a["at"] != home:
        acts.append({"do": "travel", "to": home})
        for i in ("food", "timber"):
            if a["holdings"][i] > 0:
                acts.append({"do": "store", "item": i, "qty": a["holdings"][i] - 1e-9})
        return {"actions": acts, "say": [], "note": ""}
    if h["condition"] < 2 and h["stock"]["timber"] >= w.p["repair"]["timber"]:
        return {"actions": [{"do": "repair"}] * 3, "say": [], "note": ""}
    acts.append({"do": "travel", "to": wood})
    acts.append({"do": "fell" if h["stock"]["timber"] < 6 else "forage"})
    acts.append({"do": "forage"})
    return {"actions": acts, "say": [f"{name} is going to {wood}."], "note": ""}


def decide(w: World, name: str, system: str, user: str, backend: str) -> tuple[dict, dict]:
    model = w.s["agents"][name]["model"]
    if model == "bot":
        return bot_plan(w, name), {"model": "bot"}
    from cybertron import llm
    attempts = []
    t0 = time.monotonic()
    out, reasoning, usage = llm.call(backend, model, system, user, prompt.SCHEMA, attempts=attempts)
    return out or {}, {"model": model, "usage": usage, "seconds": round(time.monotonic() - t0, 1), "reasoning": reasoning,
                       "raw": attempts[-1].get("raw") if attempts else None}


def run(spec_path: str, out_dir: str, backend: str | None = None, rounds: int | None = None, workers: int = 8) -> Path:
    spec = load_spec(spec_path)
    if rounds:
        spec["rounds"] = int(rounds)
    w = World(spec)
    backend = backend or os.environ.get("LLM_BACKEND") or "claude_code"
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    systems = {n: prompt.system_prompt(w, n) for n in w.living()}
    (out / "run.json").write_text(json.dumps({"spec": spec, "backend": backend, "systems": systems,
                                              "models": {n: a["model"] for n, a in w.s["agents"].items()}}, indent=1))
    results = {n: [] for n in w.living()}
    heard = {n: [] for n in w.living()}
    cost = 0.0
    turns_f = open(out / "turns.jsonl", "w")
    rounds_f = open(out / "rounds.jsonl", "w")
    for _ in range(w.rounds):
        rnd = w.r
        names = w.living()
        users = {n: prompt.turn_prompt(w, n, results[n], heard[n]) for n in names}
        replies, meta, errors = {}, {}, {}
        with cf.ThreadPoolExecutor(max_workers=workers) as ex:
            futs = {ex.submit(decide, w, n, systems[n], users[n], backend): n for n in names}
            for f in cf.as_completed(futs):
                n = futs[f]
                try:
                    replies[n], meta[n] = f.result()
                except Exception as e:                                          # a failed call: the agent rests this round
                    replies[n], meta[n], errors[n] = {"actions": []}, {"model": w.s["agents"][n]["model"]}, repr(e)[:500]
        plans = {}
        for n in names:
            acts = [x for x in (replies[n].get("actions") or []) if isinstance(x, dict)]
            plans[n] = acts[:w.actions_for(n)]
            if isinstance(replies[n].get("note"), str):
                w.s["agents"][n]["notes"] = replies[n]["note"][:1500]
        order = list(names)
        w.rng("order", rnd).shuffle(order)
        done = {n: [] for n in names}
        for i in range(max((len(p) for p in plans.values()), default=0)):           # interleaved: one action each in turn
            for n in order:
                if i < len(plans[n]):
                    done[n].append(act.do(w, n, plans[n][i]))
        heard = {n: [] for n in w.living()}
        for n in names:                                                          # speech: heard where the speaker ends the round
            here = w.s["agents"][n]["at"]
            place = w.s["nodes"][here]["name"]
            says = [str(x)[:600] for x in (replies[n].get("say") or []) if isinstance(x, str)]
            tells = [t for t in (replies[n].get("tell") or []) if isinstance(t, dict)]
            budget = MAX_SPEECH
            for text in says[:budget]:
                for m in w.at(here):
                    if m != n:
                        heard[m].append(f"{n} said (at {place}): {text}")
            budget -= min(len(says), budget)
            for t in tells[:budget]:
                to = str(t.get("to", ""))
                if to in heard and w.s["agents"][to]["at"] == here:
                    heard[to].append(f"{n} told you (at {place}): {str(t.get('text', ''))[:600]}")
                    done[n].append(f"You told {to}: {str(t.get('text', ''))[:80]}")
                else:
                    done[n].append(f"Refused: tell: {to} is not here to hear you")
        rec = w.end_of_round()
        for n in names:                                                          # the night, as each agent saw it
            for hunt in rec["hunts"]:
                if n in hunt["caught"]:
                    done[n].append(f"Your hunt (party {hunt['party']!r}, effort {hunt['effort']:g}) caught {hunt['caught'][n]:g} food.")
            if n in rec["ate"]:
                done[n].append(f"You ate {rec['ate'][n]:g} food ({rec['shelter'][n]}).")
            elif n in rec["missed"]:
                done[n].append(f"You could not eat a full meal ({rec['shelter'][n]}) and went without.")
            if n in rec["cold_falls"]:
                done[n].append("The night in the cold left you starving.")
            if n in rec["deaths"]:
                done[n].append("You died.")
            hid = w.s["agents"][n]["house"]
            if hid in rec["breaks"]:
                done[n].append(f"{w.s['houses'][hid]['name']} was damaged in the night.")
            if hid in rec["hearth"] and rec["hearth"][hid]["sleepers"] and not rec["hearth"][hid]["lit"]:
                done[n].append(f"{w.s['houses'][hid]['name']}'s fire went out: no timber in its stock.")
        for n in names:
            m = meta.get(n, {})
            usage = m.get("usage") or {}
            cost += float(usage.get("cc_equiv_usd") or 0.0)
            turns_f.write(json.dumps({"round": rnd, "agent": n, "model": m.get("model"), "prompt": users[n],
                                      "reply": replies[n], "plan": plans[n], "results": done[n], "usage": usage,
                                      "seconds": m.get("seconds"), "reasoning": m.get("reasoning"), "error": errors.get(n)}) + "\n")
        rec["cost_usd"] = round(cost, 4)
        rounds_f.write(json.dumps(rec) + "\n")
        turns_f.flush()
        rounds_f.flush()
        results = done
        print(f"round {rnd + 1}: alive {len(w.living())}, deaths {rec['deaths']}, missed {rec['missed']}, "
              f"cold falls {rec['cold_falls']}, breaks {rec['breaks']}, cost ${cost:.2f}, errors {len(errors)}", flush=True)
        if not w.living():
            break
    w.save(out / "state.json")
    turns_f.close()
    rounds_f.close()
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m cybertron2")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("spec")
    r.add_argument("--out", required=True)
    r.add_argument("--backend")
    r.add_argument("--rounds", type=int)
    r.add_argument("--bots", action="store_true", help="replace every model with the scripted bot (smoke test)")
    rp = sub.add_parser("report")
    rp.add_argument("run_dir")
    args = ap.parse_args(argv)
    if args.cmd == "run":
        if args.bots:
            spec = load_spec(args.spec)
            for a in spec["agents"].values():
                a["model"] = "bot"
            tmp = Path(args.out)
            tmp.mkdir(parents=True, exist_ok=True)
            import yaml
            (tmp / "spec_bots.yaml").write_text(yaml.safe_dump(spec))
            run(str(tmp / "spec_bots.yaml"), args.out, args.backend, args.rounds)
        else:
            run(args.spec, args.out, args.backend, args.rounds)
    else:
        from cybertron2 import report
        print(report.summary(args.run_dir))


if __name__ == "__main__":
    main()
