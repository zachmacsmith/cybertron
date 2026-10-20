"""The flows check of an established world's run (docs/review/31_institutions/00_framework.md §11a; 10_private_world.md §4), from a run
directory: per round, food supply against demand, store runway, the share fed, money in and out of every institution's treasury
with its runway, and whether each role's contract legs were performed.

  python -m cybertron.analysis.flows RUN_DIR [RUN_DIR ...] [--json OUT] [--licensed camp4,camp5] [--all-stores]

Reads events.jsonl, snapshots.json, turns.jsonl and the per-round checkpoints (checkpoints/r*.pkl: the standing contracts' books,
which the event log does not carry). Writes nothing into the run directory. Rounds are 1-based in the output (round 1 is the
first played round).

Per round:
  food     produced (forest forage by camp, hunting catches, reaps), eaten and missed meals (subsistence_round), deaths; food put into
           and taken out of each institution's store; store levels; runway = institutional stores / the round's demand (rounds of
           everyone's food); fed share = meals eaten / meals due.
  money    each institution's penny treasury (snapshots) and its net change; runway = treasury / the mean net outflow of the last
           3 rounds (inf when not losing).
  roles    per standing contract (law), the legs met and missed this round (from the change in its book between checkpoints:
           [kept, missed] per party and leg), duty legs counted apart.
  actions  the share of actions spent on survival: forest harvests, hunts, withdrawals from a store and food transfers to
           agents, against all actions taken (free reads and the scratchpad excluded); the same without the licensed producers'
           forage and hunts in the licensed forests (their contracted work: Supply terms); failed actions (errors).
"""
from __future__ import annotations

import argparse
import json
import math
import pickle
import re
import sys
from collections import defaultdict
from pathlib import Path

FOOD = "food"
PENNY = "penny"
# discretionary acts a role card lists (decision points, framework §11 check 3): contract and office actions are invoked
DECISIONS = ("invoke", "propose", "amend", "vote", "rule", "accuse", "appeal", "set_channel", "lend", "deposit", "redeem",
             "join_contract", "leave_contract", "set_allowance", "deposit_escrow", "guard")


def _jsonl(p: Path) -> list:
    if not p.exists():
        return []
    out = []
    for ln in p.read_text().splitlines():
        if ln.strip():
            try:
                out.append(json.loads(ln))
            except ValueError:
                continue
    return out


def _args(a) -> dict:
    try:
        x = json.loads(a.get("args_json") or "{}")
        return x if isinstance(x, dict) else {}
    except (TypeError, ValueError):
        return {}


def _r(x, n=2):
    return None if x is None else (round(x, n) if isinstance(x, float) and math.isfinite(x) else x)


def _books(run: Path) -> dict:
    """{round (0-based): {law id: {"title", "label", "inst", "book": {key: {leg: [kept, missed]}}, "duty": {leg ids}}}} from the
    per-round checkpoints (round -1 is the setup)."""
    out = {}
    idx = run / "checkpoints" / "index.json"
    if not idx.exists():
        return out
    for _, row in sorted(json.loads(idx.read_text()).items(), key=lambda kv: int(kv[0])):
        try:
            d = pickle.load(open(run / "checkpoints" / row["file"], "rb"))
        except Exception:                                               # noqa: BLE001
            continue
        w = d["kernel"]["w"]
        laws = {}
        for lid, law in (w.get("laws") or {}).items():
            st = law.get("state") or {}
            if law.get("status") != "active" or "book" not in st and "dues" not in st:
                continue
            code = law.get("code") or ""
            m = re.search(r"^LABEL = (['\"])(.*?)\1", code, re.M)
            duty = set(re.findall(r"'id': '(\w+)', 'kind': 'duty'", code))
            laws[lid] = {"title": law.get("title"), "label": (m.group(2) if m and m.group(2) else law.get("title")),
                         "inst": law.get("jurisdiction") or _inst_of(w, lid), "book": st.get("book") or {}, "duty": duty}
        out[int(row["round"])] = laws
    return out


def _inst_of(w, lid) -> str:
    for cid, rec in ((w.get("contracts") or {}).get("recs") or {}).items():
        if lid in (rec.get("laws") or ()):
            return cid
    return "J0"


def _delta(prev: dict, cur: dict) -> tuple:
    """(met, missed) legs between two books."""
    met = missed = 0
    for key, legs in cur.items():
        for leg, (k, m) in legs.items():
            pk, pm = (prev.get(key) or {}).get(leg, [0, 0])
            met += k - pk
            missed += m - pm
    return met, missed


def _licence(inst: dict) -> dict:
    """The forest Licence of the world's start laws: its TARGETS (licensed camps) and HOLDERS (the producers)."""
    for law in (((inst.get("spec") or {}).get("start") or {}).get("laws") or ()):
        if isinstance(law, dict) and law.get("template") == "Licence":
            p = law.get("params") or {}
            if "harvest" in (p.get("GATES") or ["harvest"]):
                return {"targets": list(p.get("TARGETS") or ()), "holders": list(p.get("HOLDERS") or ())}
    return {"targets": [], "holders": []}


def analyse(run: Path, licensed=None, all_stores=False) -> dict:
    ev = _jsonl(run / "events.jsonl")
    snaps = json.loads((run / "snapshots.json").read_text()) if (run / "snapshots.json").exists() else []
    turns = _jsonl(run / "turns.jsonl")
    inst_json = json.loads((run / "instance.json").read_text()) if (run / "instance.json").exists() else {}
    shocks = [int(s.get("round", 0)) for s in ((inst_json.get("spec") or {}).get("subsistence") or {}).get("shocks") or []]
    rounds = sorted({e["round"] for e in ev if e["type"] == "subsistence_round"})
    camps = {}
    for s in snaps[-1:]:
        camps = {c: v.get("type") for c, v in (s.get("camptypes") or {}).items()}
    forests = sorted(c for c, t in camps.items() if t == "forest")
    lic = _licence(inst_json)
    licensed = set(licensed or lic["targets"] or forests[:2])
    producers = set(lic["holders"])
    store_owner = {}
    for s in snaps:
        for sid, rec in ((s.get("subsistence") or {}).get("stores") or {}).items():
            store_owner[sid] = rec.get("owner")
    inst_stores = sorted(s for s, o in store_owner.items() if isinstance(o, str) and (all_stores or re.match(r"^[AJ]\d+$", o)))

    food = defaultdict(lambda: defaultdict(float))
    for e in ev:
        r, t, d = e["round"], e["type"], e.get("data") or {}
        if t == "harvest" and d.get("type") == "forest":
            food[r]["forage_licensed" if d.get("camp") in licensed else "forage_common"] += float(d.get("yield") or 0)
        elif t == "hunt_round":
            for p in d.get("parties") or ():
                food[r]["hunt_licensed" if d.get("camp") in licensed else "hunt_common"] += float(p.get("catch") or 0)
        elif t == "reap":
            food[r]["reap"] += float(d.get("qty") or 0)
        elif t == "store_deposit" and d.get("store") in inst_stores and d.get("item", FOOD) == FOOD:
            food[r][f"in_{d['store']}"] += float(d.get("qty") or 0)
        elif t == "store_withdrawal" and d.get("store") in inst_stores:
            food[r][f"out_{d['store']}"] += float(d.get("qty") or 0)
        elif t == "move" and d.get("item") == FOOD and str(d.get("src", "")).startswith("store:") and str(d.get("why", "")).startswith("law:"):
            sid = d["src"][6:]
            if sid in inst_stores:
                food[r][f"out_{sid}"] += float(d.get("qty") or 0)
        elif t == "subsistence_round":
            food[r]["ate"] = float(d.get("ate") or 0)
            food[r]["missed"] = float(d.get("missed") or 0)
            food[r]["deaths"] = float(len(d.get("deaths") or ()))
            st = d.get("stages") or {}
            food[r]["hungry"] = float(st.get("hungry", 0))
            food[r]["starving"] = float(st.get("starving", 0))
    snap_by = {int(s["round"]): s for s in snaps if "round" in s}

    treasuries = defaultdict(dict)                                     # inst -> round -> penny
    for r, s in snap_by.items():
        for cid, rec in (s.get("contracts") or {}).items():
            treasuries[cid][r] = float((rec.get("treasury") or {}).get(PENNY, 0))
        res = s.get("reserve")
        if isinstance(res, dict):
            treasuries["J0"][r] = float(res.get(PENNY, 0))

    books = _books(run)
    acts = defaultdict(lambda: defaultdict(int))
    dec = defaultdict(int)
    for t in turns:
        r = t.get("round")
        res = t.get("results") or []
        for i, a in enumerate(t.get("actions") or ()):
            if i >= len(res) or str(res[i]).startswith("(you sent"):
                continue
            name, x, out = a.get("action"), _args(a), str(res[i])
            if name in ("write_scratchpad", "lookup", "read", "manual", "recall") or name is None:
                continue
            acts[r]["all"] += 1
            failed = ": " in out and any(w in out.lower() for w in ("error", "cannot", "refused", "blocked", "needs ", "not enough",
                                                                     "no such", "unknown", "could not"))
            if failed:
                acts[r]["failed"] += 1
            surv = (name == "harvest" and x.get("camp") in forests) or name == "hunt" or (name == "withdraw") \
                or (name == "transfer" and str(x.get("item", FOOD)) == FOOD and not str(x.get("to", "")).startswith("store:"))
            if surv:
                acts[r]["survival"] += 1
                if t.get("agent") in producers and name in ("harvest", "hunt") and x.get("camp") in licensed:
                    acts[r]["survival_role"] += 1          # a licensed producer's contracted work (its Supply terms)
                if failed:
                    acts[r]["survival_failed"] += 1
            if name == "fulfil":
                acts[r]["fulfil"] += 1
            if name in DECISIONS and not failed:
                acts[r]["decisions"] += 1
                dec[name if name != "invoke" else "invoke " + str(x.get("name") or x.get("action") or "?")] += 1

    rows = []
    for r in rounds:
        f = food[r]
        produced = sum(v for k, v in f.items() if k.startswith(("forage", "hunt", "reap")))
        demand = f["ate"] + f["missed"]
        s = snap_by.get(r) or {}
        st = (s.get("subsistence") or {}).get("stores") or {}
        levels = {sid: _r(float((st.get(sid) or {}).get("food", 0)), 1) for sid in inst_stores}
        inst_food = sum(v for v in levels.values() if v)
        row = {"round": r + 1, "produced": _r(produced, 1), "licensed": _r(f["forage_licensed"] + f["hunt_licensed"], 1),
               "common": _r(f["forage_common"] + f["hunt_common"], 1), "demand": demand, "ate": f["ate"], "missed": f["missed"],
               "hungry": f["hungry"], "starving": f["starving"], "deaths": f["deaths"],
               "supply_ratio": _r(produced / demand) if demand else None,
               "fed_share": _r(f["ate"] / demand, 3) if demand else None, "stores": levels,
               "store_flows": {sid: [_r(f.get(f"in_{sid}", 0.0), 1), _r(f.get(f"out_{sid}", 0.0), 1)] for sid in inst_stores},
               "runway_rounds": _r(inst_food / demand, 1) if demand else None}
        money = {}
        for cid, ser in sorted(treasuries.items()):
            if r not in ser:
                continue
            prev = ser.get(r - 1)
            net = None if prev is None else ser[r] - prev
            back = [ser[x] - ser[x - 1] for x in range(r - 2, r + 1) if x in ser and x - 1 in ser]
            loss = -sum(back) / len(back) if back else 0.0
            money[cid] = {"penny": _r(ser[r], 1), "net": _r(net, 2), "runway": _r(ser[r] / loss, 1) if loss > 1e-9 else "inf"}
        row["money"] = money
        roles = {}
        cur, prev = books.get(r) or {}, books.get(r - 1) or {}
        for lid, law in sorted(cur.items(), key=lambda kv: int(kv[0][1:]) if kv[0][1:].isdigit() else 0):
            pb = (prev.get(lid) or {}).get("book") or {}
            duty = law["duty"]
            move_cur = {k: {g: v for g, v in legs.items() if g not in duty} for k, legs in law["book"].items()}
            move_prev = {k: {g: v for g, v in legs.items() if g not in duty} for k, legs in pb.items()}
            met, missed = _delta(move_prev, move_cur)
            dm, dmiss = _delta({k: {g: v for g, v in legs.items() if g in duty} for k, legs in pb.items()},
                               {k: {g: v for g, v in legs.items() if g in duty} for k, legs in law["book"].items()})
            if met or missed or dm or dmiss:
                roles[f"{law['inst']} {law['label']} ({lid})"] = {"met": met, "missed": missed, **({"duty_met": dm, "duty_missed": dmiss}
                                                                                                    if duty else {})}
        row["roles"] = roles
        a = acts.get(r) or {}
        row["actions"] = {"all": a.get("all", 0), "survival": a.get("survival", 0), "failed": a.get("failed", 0),
                          "fulfil": a.get("fulfil", 0), "decisions": a.get("decisions", 0),
                          "survival_role": a.get("survival_role", 0),
                          "survival_share": _r(a.get("survival", 0) / a["all"], 3) if a.get("all") else None,
                          "survival_share_ex_role": _r((a.get("survival", 0) - a.get("survival_role", 0)) / a["all"], 3)
                          if a.get("all") else None}
        rows.append(row)

    def window(lo, hi):
        sel = [x for x in rows if lo <= x["round"] <= hi]
        if not sel:
            return {}
        al = sum(x["actions"]["all"] for x in sel)
        met = sum(v["met"] for x in sel for v in x["roles"].values())
        miss = sum(v["missed"] for x in sel for v in x["roles"].values())
        dem = sum(x["demand"] for x in sel)
        return {"rounds": f"{lo}-{hi}", "produced_mean": _r(sum(x["produced"] for x in sel) / len(sel), 1),
                "licensed_mean": _r(sum(x["licensed"] for x in sel) / len(sel), 1),
                "demand_mean": _r(dem / len(sel), 1),
                "supply_ratio": _r(sum(x["produced"] for x in sel) / dem) if dem else None,
                "fed_share": _r(sum(x["ate"] for x in sel) / dem, 3) if dem else None,
                "missed_meals": sum(x["missed"] for x in sel), "deaths": sum(x["deaths"] for x in sel),
                "min_inst_stores": _r(min(sum(v for v in x["stores"].values() if v) for x in sel), 1),
                "min_runway_rounds": min((x["runway_rounds"] for x in sel if x["runway_rounds"] is not None), default=None),
                "legs_met": met, "legs_missed": miss, "legs_met_share": _r(met / (met + miss), 3) if met + miss else None,
                "survival_share": _r(sum(x["actions"]["survival"] for x in sel) / al, 3) if al else None,
                "survival_share_ex_role": _r(sum(x["actions"]["survival"] - x["actions"]["survival_role"] for x in sel) / al, 3)
                if al else None,
                "failed_share": _r(sum(x["actions"]["failed"] for x in sel) / al, 3) if al else None}
    last = rows[-1]["round"] if rows else 0
    shock = shocks[0] if shocks else None
    summary = {"first_3": window(1, 3), "before_shock": window(1, shock) if shock else window(1, last),
               "after_shock": window(shock + 1, last) if shock and last > shock else {}, "all": window(1, last)}
    posts = defaultdict(lambda: defaultdict(set))
    for e in ev:
        if e["type"] in ("post", "channel_post"):
            ch = (e.get("data") or {}).get("channel_id") or (e.get("data") or {}).get("channel") or "square"
            posts[ch][e["round"]].add(e.get("agent"))
    channels = {ch: {"posts_per_round": _r(sum(len(v) for v in by.values()) / max(1, len(rounds)), 2),
                     "authors": len(set().union(*by.values())) if by else 0} for ch, by in sorted(posts.items())}
    return {"run": str(run), "decisions": dict(sorted(dec.items(), key=lambda kv: -kv[1])), "channels": channels,
            "licensed": sorted(licensed), "forests": forests, "inst_stores": inst_stores, "shock_round": shock,
            "summary": summary, "rounds": rows}


def render(a: dict) -> str:
    out = [f"## {Path(a['run']).name}", f"forests {', '.join(a['forests'])} (licensed {', '.join(a['licensed'])}); institutional "
           f"stores {', '.join(a['inst_stores'])}; shock after round {a['shock_round']}", ""]
    for name, s in a["summary"].items():
        if s:
            out.append(f"- {name} (rounds {s['rounds']}): produced {s['produced_mean']}/round (licensed {s['licensed_mean']}) vs "
                       f"demand {s['demand_mean']} ({s['supply_ratio']}x); fed {s['fed_share']}; missed meals {s['missed_meals']}, "
                       f"deaths {s['deaths']}; institutional stores min {s['min_inst_stores']} (runway min {s['min_runway_rounds']} "
                       f"rounds); legs met {s['legs_met']}/{s['legs_met'] + s['legs_missed']} ({s['legs_met_share']}); survival "
                       f"actions {s['survival_share']} (without producers' licensed work {s['survival_share_ex_role']}); failed actions {s['failed_share']}")
    out.append(f"- decision points taken (successful discretionary acts): {a['decisions'] or 'none'}")
    out.append(f"- channels (distinct authors a round, authors in all): {a['channels'] or 'none'}")
    out += ["", "| round | produced | licensed | common | demand | fed | stores | runway | " + " | ".join(
        sorted({c for r in a["rounds"] for c in r["money"]})) + " | legs met/missed | survival share |",
        "|" + "---|" * (10 + len({c for r in a["rounds"] for c in r["money"]}))]
    cids = sorted({c for r in a["rounds"] for c in r["money"]})
    for r in a["rounds"]:
        met = sum(v["met"] for v in r["roles"].values())
        miss = sum(v["missed"] for v in r["roles"].values())
        st = ", ".join(f"{k} {v}" for k, v in r["stores"].items())
        mon = " | ".join(f"{r['money'][c]['penny']} ({r['money'][c]['net']})" if c in r["money"] else "" for c in cids)
        out.append(f"| {r['round']} | {r['produced']} | {r['licensed']} | {r['common']} | {r['demand']:.0f} | {r['fed_share']} | {st} | "
                   f"{r['runway_rounds']} | {mon} | {met}/{miss} | {r['actions']['survival_share']} |")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m cybertron.analysis.flows", description=__doc__.split("\n\n")[0])
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--json")
    ap.add_argument("--licensed", help="comma-separated licensed forest camps (default: the first two forests)")
    ap.add_argument("--all-stores", action="store_true", help="count agents' stores too (the Merchant world's dealer and pantries; "
                                                               "default: institutions' stores only)")
    a = ap.parse_args(argv)
    lic = a.licensed.split(",") if a.licensed else None
    res = [analyse(Path(r), lic, a.all_stores) for r in a.runs]
    for x in res:
        print(render(x))
        print()
    if a.json:
        Path(a.json).write_text(json.dumps(res, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
