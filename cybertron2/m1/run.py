"""The day (docs/review/38_space_engine/05_round_design.md, one node): dawn (incidents), decide (everyone at once, in parallel),
talk (messages, explanations and offers delivered; whoever received something, or opened a note or looked up a craft, is asked
again and may change its plan; one wave), work (the plans interleaved, one action each in turn, in an order shuffled per day from the
seed), teaching settled, thefts seen or not, the night, then perception (what each agent will be shown in the morning) and memory.

Logs, in the run directory:
    run.json          the spec, models, system prompts (as of day 1)
    turns.jsonl       one line per agent-day: prompt, reply, talk prompt and reply (if asked again), plan, results, usage
    days.jsonl        one line per day: the night record, offers, teaching, talk counts, cost
    perception.jsonl  one line per agent-day: the fact ids it was given, by channel, and the day's facts (once per day)
    state.json        the final state
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import re
import time
from pathlib import Path

from cybertron2.m1 import act as AC, knowledge as KN, perceive as PC, prompt as PR
from cybertron2.m1.data import EDIBLE, ITEMS, TECHNIQUES
from cybertron2.m1.world import World, load_spec

MAX_SAY = 3
MAX_ACTIONS = 10


def _blank_today() -> dict:
    return {"fights": [], "guards": [], "watch": {}, "teach": [], "learn": [], "worked": {}, "steals": []}


def _goods(x) -> dict:
    """'2 bread, 1 timber' -> {bread: 2, timber: 1}; unknown goods dropped."""
    out = {}
    for q, item in re.findall(r"(\d+(?:\.\d+)?)\s*([a-z ]+?)(?:,|$| and )", str(x or "").lower() + ","):
        try:
            i = AC._item(item.strip())
        except AC.Refused:
            continue
        out[i] = out.get(i, 0.0) + float(q)
    return out


# ---------------------------------------------------------------------- a scripted bot (smoke test only)
def bot_plan(w, name, talk=None) -> dict:
    a = w.s["agents"][name]
    h = w.home(name)
    acts = []
    others = [x for x in w.agents_acting() if x != name]
    attend = others[(w.d + len(name)) % len(others)] if others else "the place in general"
    youth = [x for x in others if w.s["agents"][x]["stage"] == "youth" and w.s["agents"][x]["house"] == a["house"]]
    teach = next(((y, t) for y in youth for t in TECHNIQUES if KN.level(w, name, t) == "known" and KN.level(w, y, t) in (None, "aware", "rough")
                  and not KN.basic(t)), None)
    if teach and w.d % 3 == 1:
        acts.append({"do": "teach", "to": teach[0], "what": teach[1]})
    if a["stage"] == "youth" and w.d % 3 == 1:
        elder = next((x for x in others if w.s["agents"][x]["house"] == a["house"] and w.s["agents"][x]["stage"] != "youth"), None)
        tech = next((t for t in TECHNIQUES if elder and KN.level(w, elder, t) == "known" and KN.level(w, name, t) in (None, "aware", "rough")
                     and not KN.basic(t)), None)
        if tech:
            acts.append({"do": "learn", "from": elder, "what": tech})
    if any(KN._crop_ripe(w, pid) for pid in w.parcels()) and KN.level(w, name, "reap") == "known" and a["holdings"].get("sickle", 0) >= 1:
        acts += [{"do": "work", "what": "reap"}] * 2
    if KN.level(w, name, "fell") == "known" and a["holdings"].get("axe", 0) >= 1 and h and h["stock"].get("timber", 0) < 4:
        acts.append({"do": "gather", "what": "fell", "at": "Alder Wood"})
    acts += [{"do": "gather", "what": "forage", "at": "Alder Wood"}, {"do": "gather", "what": "forage", "at": "Brook Meadow"}]
    if a["holdings"].get("grain", 0) >= 2.5 and a["holdings"].get("timber", 0) >= 0.5 and KN.level(w, name, "bread") == "known":
        acts.append({"do": "make", "what": "bread"})
    for item in ("greens", "grain", "timber", "meat", "fish", "bread"):
        acts.append({"do": "move", "item": item, "qty": 1, "to": "house"})
    out = {"why": "bot", "actions": acts, "attend": attend, "say": [f"{name} is out foraging today."] if w.d % 2 == 0 else []}
    if w.d == 1 and name == min(w.agents_acting()):
        out["offers"] = [{"to": "anyone", "give": "1 greens", "get": "1 timber"}]
        out["note"] = [{"title": "plan", "text": "keep the store full before the frost"}]
        out["pin"] = "plan"
    if talk and talk.get("offers"):
        oid = talk["offers"][0].split(":")[0]
        out["actions"] = [{"do": "accept", "offer": oid}] + acts
    return out


def decide(w, name, system, user, backend, talk=None) -> tuple[dict, dict]:
    model = w.s["agents"][name]["model"]
    if model == "bot":
        return bot_plan(w, name, talk), {"model": "bot"}
    from cybertron import llm
    t0 = time.monotonic()
    attempts = []
    out, reasoning, usage = llm.call(backend, model, system, user, PR.SCHEMA, attempts=attempts)
    return out or {}, {"model": model, "usage": usage, "seconds": round(time.monotonic() - t0, 1), "thinking": reasoning}


def _parallel(fn, jobs: dict, workers) -> tuple[dict, dict, dict]:
    replies, meta, errors = {}, {}, {}
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(fn, *args): n for n, args in jobs.items()}
        for f in cf.as_completed(futs):
            n = futs[f]
            try:
                replies[n], meta[n] = f.result()
                if replies[n].get("_error"):
                    errors[n] = str(replies[n]["_error"])[:500]
                    replies[n] = {"actions": []}
            except Exception as e:
                replies[n], meta[n], errors[n] = {"actions": []}, {}, repr(e)[:500]
    return replies, meta, errors


# ---------------------------------------------------------------------- the talk step
def talk(w, names, replies, results) -> dict:
    """Deliver say, tell, explain and offers from the plans. Returns {name: {heard, offers, opened, cards}} for whoever is asked
    again (received something, opened a note, or looked up a craft)."""
    box = {n: {"heard": [], "offers": [], "opened": [], "cards": []} for n in names}
    for n in names:
        r = replies[n]
        says = [str(x)[:600] for x in (r.get("say") or []) if isinstance(x, str) and x.strip()][:MAX_SAY]
        for text in says:
            hearers = [m for m in names if m != n]
            for m in hearers:
                box[m]["heard"].append(f"{n} said: {text}")
                PC.store(w, m)["today"]["heard"].append(f"{n} said: {text}")
            for h, tech in KN.mentions(w, n, hearers, text):
                PC.store(w, h)["today"]["heard"].append(f"(You had not heard of {TECHNIQUES[tech]['label'].split(' (')[0]} before.)")
            w.happen("speech", f"{n} spoke to everyone", actor=n, salience=0.1, sense="sound")
        for t in [t for t in (r.get("tell") or []) if isinstance(t, dict)][:MAX_SAY]:
            to, text = w.person(t.get("to")), str(t.get("text", ""))[:600]
            if to and to in names and to != n:
                box[to]["heard"].append(f"{n} told you: {text}")
                PC.store(w, to)["today"]["heard"].append(f"{n} told you: {text}")
                KN.mentions(w, n, [to], text)
                results[n].append(f"You told {to}: {text}")
            else:
                results[n].append(f"Refused: tell: nobody called {t.get('to')!r} is here to hear you")
        for x in [x for x in (r.get("explain") or []) if isinstance(x, dict)][:2]:
            to, tech = w.person(x.get("to")), KN.resolve(x.get("what"))
            if not to or to not in names or tech is None:
                results[n].append(f"Refused: explain: {x.get('to')!r} or {x.get('what')!r} not found")
                continue
            why = KN.explained(w, n, to, tech)
            label = TECHNIQUES[tech]["label"].split(" (")[0]
            if why:
                results[n].append(f"Refused: explain: {why}")
            else:
                results[n].append(f"You explained {label} to {to}.")
                box[to]["heard"].append(f"{n} explained {label} to you: you now have a rough idea of it.")
                PC.store(w, to)["today"]["heard"].append(f"{n} explained {label} to you.")
        for o in [o for o in (r.get("offers") or []) if isinstance(o, dict)][:3]:
            give, get = _goods(o.get("give")), _goods(o.get("get"))
            to_raw = str(o.get("to") or "anyone")
            to = None if to_raw.lower() in ("anyone", "all", "everyone", "") else w.person(to_raw)
            if not give or not get or (to is None and to_raw.lower() not in ("anyone", "all", "everyone", "")):
                results[n].append(f"Refused: offer: could not read {o!r} (write goods as '2 bread, 1 timber')")
                continue
            short = [i for i, q in give.items() if w.s["agents"][n]["holdings"].get(i, 0) + 1e-9 < q]
            if short:
                results[n].append(f"Refused: offer: you do not carry enough {', '.join(short)}")
                continue
            w.s["seq"] += 1
            oid = f"O{w.s['seq']}"
            w.s["offers"][oid] = {"by": n, "to": to, "give": give, "get": get, "day": w.d, "open": True}
            results[n].append("You offered " + PR._offer_text(w, oid, w.s["offers"][oid]))
            for m in ([to] if to else [m for m in names if m != n]):
                box[m]["offers"].append(PR._offer_text(w, oid, w.s["offers"][oid]))
        a = w.s["agents"][n]
        for title in (r.get("open") or [])[:int(w.p["notes"]["open"])]:
            if title in a["notes"]:
                box[n]["opened"].append((title, a["notes"][title]))
        for x in (r.get("look_up") or [])[:3]:
            tech = KN.resolve(x)
            box[n]["cards"].append(KN.card(w, n, tech) if tech else f"{x}: you know nothing of it")
    return {n: b for n, b in box.items() if any(b.values())}


# ---------------------------------------------------------------------- the run
def run(spec_path, out_dir, backend=None, days=None, workers=12, bots=False) -> Path:
    spec = load_spec(spec_path)
    if days:
        spec["days"] = int(days)
    if bots:
        for a in spec["agents"].values():
            a["model"] = "bot"
    w = World(spec)
    backend = backend or os.environ.get("LLM_BACKEND") or "claude_code"
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    systems = {n: PR.system_prompt(w, n) for n in w.living()}
    (out / "run.json").write_text(json.dumps({"spec": spec, "backend": backend, "systems": systems,
                                              "models": {n: a["model"] for n, a in w.s["agents"].items()}}, indent=1))
    files = {k: open(out / f"{k}.jsonl", "w") for k in ("turns", "days", "perception")}
    cost = 0.0
    for day in range(w.days):
        w.s["day"] = day
        w.s["events"] = []
        today = w.s["today"] = _blank_today()
        dawn(w)
        PC.dawn(w)
        names = w.agents_acting()
        systems = {n: PR.system_prompt(w, n) for n in names}                  # rebuilt: what it knows may have changed
        users = {n: PR.turn_prompt(w, n) for n in names}
        replies, meta, errors = _parallel(lambda n: decide(w, n, systems[n], users[n], backend), {n: (n,) for n in names}, workers)
        first = {n: dict(replies[n]) for n in names}
        results = {n: ([f"(Your reply could not be used, so you did nothing: {errors[n][:160]})"] if n in errors else []) for n in names}
        for n in names:
            results[n] += PC.apply_notes(w, n, replies[n])
        box = talk(w, names, replies, results)
        talk_users, talk_replies, talk_meta = {}, {}, {}
        if box:
            talk_users = {n: PR.talk_prompt(w, n, b["heard"], b["offers"], b["opened"], b["cards"], first[n]) for n, b in box.items()}
            talk_replies, talk_meta, terr = _parallel(lambda n: decide(w, n, systems[n], talk_users[n], backend, box[n]),
                                                      {n: (n,) for n in box}, workers)
            for n in box:
                r2 = talk_replies[n]
                if n in terr or not isinstance(r2.get("actions"), list):
                    continue
                replies[n] = {**replies[n], **{k: v for k, v in r2.items() if v not in (None, "", [])}, "actions": r2["actions"]}
                results[n] += PC.apply_notes(w, n, {k: r2.get(k) for k in ("note", "pin", "forget")})
                late = {k: r2.get(k) for k in ("say", "tell", "explain", "offers")}
                if any(late.values()):                                       # replies: delivered, not asked again (one wave)
                    talk(w, names, {**{m: {} for m in names}, n: late}, results)
        attend = {n: replies[n].get("attend") for n in names if replies[n].get("attend")}
        # work: interleaved
        plans = {n: [x for x in (replies[n].get("actions") or []) if isinstance(x, dict)][:MAX_ACTIONS] for n in names}
        order = list(names)
        w.rng("order", day).shuffle(order)
        budget = {n: w.units_for(n) for n in names}
        used = {n: 0 for n in names}
        for i in range(max((len(p) for p in plans.values()), default=0)):
            for n in order:
                if i >= len(plans[n]) or not w.s["agents"][n]["alive"]:
                    continue
                a = plans[n][i]
                c = AC.cost(w, n, a)
                if used[n] + c > budget[n]:
                    if c and used[n] < budget[n]:
                        results[n].append(f"Not done: {a.get('do')} {a.get('what') or ''}".rstrip() + f": it takes {c} units and you had {budget[n] - used[n]} left")
                    continue
                res = AC.do(w, n, a, today)
                if not res.startswith("Refused"):
                    used[n] += c
                results[n].append(res)
        for n, lines in AC.settle_teaching(w, today).items():
            results.setdefault(n, []).extend(lines)
        PC.steals(w, today, attend)
        rec = w.night()
        per = PC.evening(w, attend, today)
        nights = night_lines(w, rec)
        for n in names:
            m = meta.get(n, {})
            tm = talk_meta.get(n, {})
            for u in (m.get("usage") or {}, tm.get("usage") or {}):
                cost += float(u.get("cc_equiv_usd") or 0.0)
            files["turns"].write(json.dumps({
                "day": day, "agent": n, "model": w.s["agents"][n]["model"], "units": budget[n], "used": used[n], "prompt": users[n],
                "reply": first[n], "thinking": m.get("thinking"), "talk_prompt": talk_users.get(n), "talk_reply": talk_replies.get(n),
                "talk_thinking": tm.get("thinking"), "plan": plans[n], "attend": attend.get(n), "results": results[n],
                "night": nights.get(n, []), "usage": m.get("usage"), "talk_usage": tm.get("usage"), "seconds": m.get("seconds"),
                "error": errors.get(n)}) + "\n")
            PC.close_day(w, n, results[n], nights.get(n, []))
        for n, lg in per["agents"].items():
            files["perception"].write(json.dumps({"day": day, "agent": n, **lg}) + "\n")
        files["perception"].write(json.dumps({"day": day, "facts": per["facts"]}) + "\n")
        rec.update(cost_usd=round(cost, 4), talked=sorted(box), offers={k: v for k, v in w.s["offers"].items() if v["day"] == day},
                   teaching=[t for t in today["teach"]], learning=[t for t in today["learn"]], watch=today["watch"], steals=today["steals"],
                   attend=attend, errors=errors)
        files["days"].write(json.dumps(rec) + "\n")
        for f in files.values():
            f.flush()
        print(f"day {day + 1}: alive {len(w.living())}, missed {rec['missed']}, deaths {rec['deaths']}, talked {len(box)}, "
              f"offers {len(rec['offers'])}, taught {len([t for t in today['teach']])}, steals {len(today['steals'])}, "
              f"errors {len(errors)}, cost ${cost:.2f}", flush=True)
        if not w.living():
            break
    w.save(out / "state.json")
    for f in files.values():
        f.close()
    return out


def dawn(w) -> None:
    """Morning incidents from the spec: a herd strays into a field (eats the crop until driven out)."""
    for inc in w.spec.get("incidents") or []:
        if int(inc["day"]) - 1 != w.d:
            continue
        if inc["kind"] == "stray":
            hd = w.s["herds"][inc["herd"]]
            pid = w.parcel_by_name(inc["into"])
            hd["parcel"] = pid
            c = w.parcels()[pid]["state"].get("crop")
            if c:
                c["left"] = round(max(0.0, c["left"] - float(inc.get("eats", 2.0))), 4)
            w.happen("stray", f"{hd['name']} broke through into {w.parcels()[pid]['name']} at dawn and are trampling the "
                     f"{c.get('kind', 'crop') if c else 'ground'}", parcel=pid, salience=0.7, tags=["farming", "animals", "food"],
                     concerns=inc.get("concerns", []), extra={"dawn": True, "about": f"p:{pid}"})
    for sg in w.spec.get("signs") or []:
        if int(sg["day"]) - 1 == w.d:
            w.happen("sign", sg["text"], salience=float(sg.get("salience", 0.3)), tags=sg.get("tags", ["season"]),
                     sense=sg.get("sense", "sight"), extra={"dawn": True, "about": sg.get("about", "sky")})
    for hd in w.s["herds"].values():                                      # a stray herd wanders home after a day
        if hd["parcel"] != hd["home"] and not any(int(i["day"]) - 1 == w.d for i in w.spec.get("incidents") or []):
            hd["parcel"] = hd["home"]


def night_lines(w, rec) -> dict:
    out = {}
    for n in w.s["agents"]:
        L = []
        if n in rec["missed"]:
            L.append("You went to bed without enough to eat: a missed meal.")
        elif n in rec["short"]:
            L.append(f"You ate {rec['ate'][n]:g}, less than a cold night asks.")
        if n in rec["cold_falls"]:
            L.append("The night in the cold left you starving.")
        if n in rec["deaths"]:
            L.append("You died.")
        hid = w.s["agents"][n]["house"]
        if hid in rec["hearth"] and rec["hearth"][hid]["sleepers"] and not rec["hearth"][hid]["lit"]:
            L.append(f"{w.s['houses'][hid]['name']}'s fire went out: no timber in its store.")
        if hid in rec["breaks"]:
            L.append(f"{w.s['houses'][hid]['name']} took damage in the night.")
        out[n] = L
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="cybertron2.m1")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("spec")
    r.add_argument("--out", required=True)
    r.add_argument("--days", type=int)
    r.add_argument("--backend")
    r.add_argument("--workers", type=int, default=12)
    r.add_argument("--bots", action="store_true")
    args = ap.parse_args(argv)
    if args.cmd == "run":
        print(run(args.spec, args.out, args.backend, args.days, args.workers, args.bots))
