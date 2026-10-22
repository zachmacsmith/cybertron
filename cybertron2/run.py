"""The round loop. Each round: every living agent observes where it is and decides from the same state (model calls in parallel);
the plans are carried out interleaved, one action from each agent in turn, in an order shuffled per round from the seed (an attack
or a raid takes two of an agent's actions); after every step everyone observes again and witnesses what was done where it stands;
speech is heard by whoever is at the speaker's place when the round ends; then the night (world.end_of_round: hunts, fights,
meals, the cold), which those present witness; then each agent's round moves into its memory (perceive.close_round). Models are
called through the old engine's leaf backend (cybertron.llm: `claude -p` on the subscription, or the API).

Logs, in the run directory:
    run.json       the spec, each agent's model and system prompt
    turns.jsonl    one line per agent-round: the turn prompt, the reply (with its reasoning), the results, usage and cost, any error
    rounds.jsonl   one line per round: the end-of-round record (hunts, fights, meals, shelter, deaths, falls, breaks, stocks)
    state.json     the final state (with every agent's knowledge store)

The scripted bot ("bot" as an agent's model) is a smoke-test fixture (determinism, no crash), not evidence about behaviour.
"""
from __future__ import annotations

import argparse
import collections
import concurrent.futures as cf
import json
import os
import time
from pathlib import Path

from cybertron2 import act, perceive as PC, prompt
from cybertron2.world import World, load_spec

MAX_SPEECH = 3


def _path(w, frm, to) -> list:
    """Shortest path of places from frm to to (excluding frm)."""
    prev, q = {frm: None}, collections.deque([frm])
    while q:
        x = q.popleft()
        for y in w.s["edges"][x]:
            if y not in prev:
                prev[y] = x
                q.append(y)
    out, x = [], to
    while x is not None and x != frm:
        out.append(x)
        x = prev.get(x)
    return out[::-1]


def bot_plan(w: World, name: str) -> dict:
    """A simple bot: gatherers keep home stocked from the nearest plants; raiders walk to the nearest other house and raid it."""
    a = w.s["agents"][name]
    h = w.home(name)
    home = h["node"]
    if "forage" in a["cannot"]:
        if a["holdings"]["food"] < 1 and a["at"] == home and h["stock"]["food"] >= 1:
            return {"actions": [{"do": "take", "item": "food", "qty": 2 if h["stock"]["food"] >= 2 else 1}], "reasoning": "bot"}
        targets = sorted((len(_path(w, a["at"], x["node"])), hid) for hid, x in w.s["houses"].items() if hid != a["house"])
        _, hid = targets[0]
        path = _path(w, a["at"], w.s["houses"][hid]["node"])
        if not path:
            return {"actions": [{"do": "raid", "house": hid}], "reasoning": "bot"}
        return {"actions": [{"do": "travel", "to": x} for x in path[:4]], "reasoning": "bot"}
    if a["at"] != home:
        acts = [{"do": "travel", "to": x} for x in _path(w, a["at"], home)]
        return {"actions": acts + [{"do": "store", "item": "food", "qty": max(0.1, a["holdings"]["food"] - 1)}], "reasoning": "bot"}
    if h["condition"] < 2 and h["stock"]["timber"] >= w.p["repair"]["timber"]:
        return {"actions": [{"do": "repair"}] * 3, "reasoning": "bot"}
    if w.s["nodes"][home]["plants"]:
        acts = [{"do": "forage"}, {"do": "forage"}]
        if a["holdings"]["food"] > 1:
            acts.append({"do": "store", "item": "food", "qty": a["holdings"]["food"] - 1})
        return {"actions": acts + [{"do": "guard"}], "reasoning": "bot", "say": [f"{name} is foraging at home."]}
    wood = next(n for n in w.s["edges"][home] if w.s["nodes"][n]["plants"])
    return {"actions": [{"do": "travel", "to": wood}, {"do": "forage"}, {"do": "forage"}, {"do": "travel", "to": home}],
            "reasoning": "bot"}


def decide(w: World, name: str, system: str, user: str, backend: str) -> tuple[dict, dict]:
    model = w.s["agents"][name]["model"]
    if model == "bot":
        return bot_plan(w, name), {"model": "bot"}
    from cybertron import llm
    attempts = []
    t0 = time.monotonic()
    out, reasoning, usage = llm.call(backend, model, system, user, prompt.SCHEMA, attempts=attempts)
    return out or {}, {"model": model, "usage": usage, "seconds": round(time.monotonic() - t0, 1), "thinking": reasoning}


def run(spec_path: str, out_dir: str, backend: str | None = None, rounds: int | None = None, workers: int = 12) -> Path:
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
    cost = 0.0
    turns_f = open(out / "turns.jsonl", "w")
    rounds_f = open(out / "rounds.jsonl", "w")
    for _ in range(w.rounds):
        rnd = w.r
        names = w.living()
        PC.observe_all(w)
        users = {n: prompt.turn_prompt(w, n) for n in names}
        replies, meta, errors = {}, {}, {}
        with cf.ThreadPoolExecutor(max_workers=workers) as ex:
            futs = {ex.submit(decide, w, n, systems[n], users[n], backend): n for n in names}
            for f in cf.as_completed(futs):
                n = futs[f]
                try:
                    replies[n], meta[n] = f.result()
                    if replies[n].get("_error"):                                # the backend's failed-call placeholder
                        errors[n] = str(replies[n]["_error"])[:500]
                        replies[n] = {"actions": []}
                except Exception as e:                                          # a failed call: the agent rests this round
                    replies[n], meta[n], errors[n] = {"actions": []}, {"model": w.s["agents"][n]["model"]}, repr(e)[:500]
        plans = {}
        for n in names:
            plans[n] = [x for x in (replies[n].get("actions") or []) if isinstance(x, dict)][:8]
            if isinstance(replies[n].get("note"), str):
                w.s["agents"][n]["notes"] = replies[n]["note"][:1500]
        order = list(names)
        w.rng("order", rnd).shuffle(order)
        done = {n: ([f"(Your reply could not be used, so you did nothing: {errors[n][:160]})"] if n in errors else []) for n in names}
        budget = {n: w.actions_for(n) for n in names}
        used = {n: 0 for n in names}
        for i in range(max((len(p) for p in plans.values()), default=0)):           # interleaved: one action each in turn
            for n in order:
                if i >= len(plans[n]) or not w.s["agents"][n]["alive"]:
                    continue
                a = plans[n][i]
                c = act.cost(w, a)
                if used[n] >= budget[n]:
                    continue                                                    # out of actions: the rest of the plan is dropped
                if used[n] + c > budget[n]:
                    done[n].append(f"Refused: {a.get('do')}: it takes {c} actions and you have {budget[n] - used[n]} left")
                    used[n] = budget[n]
                    continue
                frm = w.s["agents"][n]["at"]
                before = w.at(frm)
                res, seen = act.do(w, n, a)
                used[n] += c
                done[n].append(res)
                PC.witness(w, n, w.s["agents"][n]["at"], seen, before)
            PC.observe_all(w)
        for n in names:                                                          # speech: heard where the speaker ends the round
            here = w.s["agents"][n]["at"]
            place = w.place(here)
            says = [str(x)[:600] for x in (replies[n].get("say") or []) if isinstance(x, str)]
            tells = [t for t in (replies[n].get("tell") or []) if isinstance(t, dict)]
            room = MAX_SPEECH
            for text in says[:room]:
                for m in w.at(here):
                    if m != n:
                        PC.store(w, m)["heard"].append(f"{n} said (at {place}): {text}")
            room -= min(len(says), room)
            for t in tells[:room]:
                to = str(t.get("to", ""))
                text = str(t.get("text", ""))[:600]
                if to in w.s["agents"] and w.s["agents"][to]["alive"] and w.s["agents"][to]["at"] == here:
                    PC.store(w, to)["heard"].append(f"{n} told you (at {place}): {text}")
                    done[n].append(f"You told {to}: {text}")
                else:
                    done[n].append(f"Refused: tell: {to} is not here to hear you")
        rec = w.end_of_round()
        PC.night(w, rec)
        for n in names:                                                          # the night, as each agent saw it
            for hunt in rec["hunts"]:
                if n in hunt["caught"]:
                    others = [x for x in hunt["caught"] if x != n]
                    done[n].append(f"Your hunt{' with ' + ', '.join(others) if others else ' alone'} (effort {hunt['effort']:g}) "
                                   f"caught you {hunt['caught'][n]:g} food" + (f"; the others caught {sum(hunt['caught'][x] for x in others):g}" if others else "") + ".")
            if n in rec["missed"]:
                done[n].append(f"You could not eat a meal ({rec['shelter'][n]}): a missed meal.")
            elif n in rec["short"]:
                done[n].append(f"You ate {rec['ate'][n]:g} food, short of what you needed ({rec['shelter'][n]}).")
            elif n in rec["ate"]:
                done[n].append(f"You ate {rec['ate'][n]:g} food ({rec['shelter'][n]}).")
            if n in rec["cold_falls"]:
                done[n].append("The night in the cold left you starving.")
            if n in rec["deaths"]:
                done[n].append("You died.")
            hid = w.s["agents"][n]["house"]
            if hid in rec["hearth"] and rec["hearth"][hid]["sleepers"] and not rec["hearth"][hid]["lit"] and w.sleeps_home(n):
                done[n].append(f"{w.s['houses'][hid]['name']}'s fire went out: no timber in its stock.")
        for n in names:
            m = meta.get(n, {})
            usage = m.get("usage") or {}
            cost += float(usage.get("cc_equiv_usd") or 0.0)
            turns_f.write(json.dumps({"round": rnd, "agent": n, "model": m.get("model"), "prompt": users[n],
                                      "reply": replies[n], "plan": plans[n], "results": done[n], "usage": usage,
                                      "seconds": m.get("seconds"), "error": errors.get(n)}) + "\n")
            PC.close_round(w, n, done[n], rec)
        rec["cost_usd"] = round(cost, 4)
        rounds_f.write(json.dumps(rec) + "\n")
        turns_f.flush()
        rounds_f.flush()
        fights = [f"{f['kind']} {f.get('house') or f.get('target')}: {f['outcome']}" for f in rec["fights"]]
        print(f"round {rnd + 1}: alive {len(w.living())}, deaths {rec['deaths']}, missed {rec['missed']}, fights {fights}, "
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
