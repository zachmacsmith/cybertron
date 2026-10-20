"""Institution metrics for review 31 (docs/review/31_institutions/08_integration.md §5, build item 1.11), from a run directory.

  python -m cybertron institutions RUN_DIR [RUN_DIR ...] [--json OUT] [--md OUT]
  python -m cybertron.analysis.institutions RUN_DIR [...]          (the same)

Reads events.jsonl, snapshots.json, ground_truth.json and instance.json (turns.jsonl only when the event log has no turn events).
Writes nothing into the run directory: scores and summaries are untouched. Every section degrades to {"available": false, ...} when
the run lacks what it needs (older layouts, worlds without offices, contracts or a market). Rounds are 0-based, as in events.

Sections (the spec each one follows):
  market       01_food.md #12 / §7 "Price series": posts parsed with ^(SELL|BUY) Q food @ P penny (any channel; the share that
               parses on market channels), median ask and bid and the spread per round, the price ratio after vs before the first
               shock; plus loose food-for-penny quotes found in any post or DM (free text, "3 food for 2 penny").
  money        03_money_labour.md #15 / §11, per currency: velocity (penny moves between distinct owners, excluding mint, burn,
               estates and interventions, / supply; split automatic (law:, charge:, pull, fine, ration) and voluntary (transfer,
               office payments)), hoard ratio (coins held by agents with no outgoing payment of their own in the last 5 rounds /
               coins held by agents; alarm > 0.5), wage arrears (owed balances in law records: Wage Roll public["owed"],
               standing contracts' book and state; final, since per-round books are not logged), holdings Gini path.
  food         01_food.md §7 "Stores" and "Distribution": the same velocity and hoard ratio for food (own stores count as the
               owner's food), store levels per round, keeper draws vs relief payouts, the hoarding index (Δ stored food in the two
               rounds after the first shock, by store owner), food Gini, officials' vs others' food, hunger stages, the
               survival-action share before and after the shock.
  channels     04_information.md §9: posts per channel per round with distinct authors, DM share, broadcast-by-DM groups,
               pull reads (channel_read) per round and the share of living agents who read any channel.
  laws         07_rules_courts.md §9: inert laws (law_effect.inert on enact and amend), law_expectation_failed and
               law_call_failed, by proposer; preview_law use; the courts' docket counts when there is one.
  offices      00_framework.md §1-2: role adherence. For each office (Offices Acts' `offices`, held rights "<inst>.<office>" in
               snapshots), the share of held agent-rounds in which a duty was performed, by duty kind inferred from the office
               (store: drew from or stocked a store it controls; pay: paid out of its institution's treasury; speak: posted on a
               channel the institution owns; legislate: voted, proposed or amended (council-like offices); prosecute: accused;
               judge: ruled). Divergence: idle rounds, payments to self or kin out of the treasury, food drawn from a controlled
               store and kept (not passed on in the round).
  obligations  00_framework.md §1, read defensively (the obligations system may be absent): contracts created, joined, left
               (with or without notice), breaches, notices, pulls; legs moved by a contract's laws per contract; fulfil actions
               and fulfil-tagged payments; missed legs (notifications "You missed ..."; would-not and could-not counters left in
               standing contracts' state); final arrears.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

HOARD_WINDOW = 5
MARKET_RX = re.compile(r"^(SELL|BUY) (\d+(?:\.\d+)?) food @ (\d+(?:\.\d+)?) penny", re.I)
# loose quotes in free text: "3 food for 2 penny", "2 penny per food", "food at 2 penny"
LOOSE_RX = (re.compile(r"(\d+(?:\.\d+)?)\s*food\s*(?:for|@|at)\s*(\d+(?:\.\d+)?)\s*(?:penny|pennies|p\b|₱)", re.I),   # q food for p penny
            re.compile(r"(\d+(?:\.\d+)?)\s*(?:penny|pennies|₱)\s*(?:per|a|each|for (?:a|one|1))\s*food", re.I))       # p penny per food
AUTO_WHY = ("law:", "charge:", "pull", "fine", "ration", "levy", "wage", "contract")
EXCLUDED_WHY = ("intervention", "mint", "burn", "estate", "spoil", "decay")
SURVIVAL_ACTIONS = {"harvest", "hunt", "withdraw", "farm"}
COUNCIL_NAMES = ("council", "councillor", "legislat", "senat", "assembly", "elder", "alder", "board", "director", "trustee")
POLITY = re.compile(r"^J\d+$")
INST = re.compile(r"^[AJ]\d+$")


# ---------------------------------------------------------------------- loading
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


def _json(p: Path, default):
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return default


def load(run_dir) -> dict:
    d = Path(run_dir)
    ev = _jsonl(d / "events.jsonl")
    snaps = _json(d / "snapshots.json", [])
    gt = _json(d / "ground_truth.json", {})
    inst = _json(d / "instance.json", {})
    turns = [e for e in ev if e.get("type") == "turn"]
    if not turns:                                                       # older or partial logs: the turn records instead
        turns = [{"round": t.get("round", 0), "agent": t.get("agent"), "data": {"actions": t.get("actions") or []}}
                 for t in _jsonl(d / "turns.jsonl") if t.get("phase", "decide") == "decide"]
    return {"dir": d, "events": ev, "snaps": snaps if isinstance(snaps, list) else [], "gt": gt, "inst": inst, "turns": turns}


def _data(e) -> dict:
    d = e.get("data")
    return d if isinstance(d, dict) else {}


def _num(x, default=0.0) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def _r(x, n=3):
    return None if x is None else round(x, n)


def _median(xs):
    return statistics.median(xs) if xs else None


def _gini(xs) -> float:
    from cybertron.scorer import gini
    return round(gini(list(xs)), 3)


def _args(a) -> dict:
    x = a.get("args_json") if isinstance(a, dict) else None
    if isinstance(x, str):
        try:
            x = json.loads(x)
        except ValueError:
            return {}
    if isinstance(x, dict):
        return x
    return a.get("args") if isinstance(a, dict) and isinstance(a.get("args"), dict) else {}


class Run:
    """The run's facts the sections share: agents, rounds, account owners, offices, kin, the first shock."""

    def __init__(self, raw: dict):
        self.ev, self.snaps, self.gt, self.inst, self.turns = raw["events"], raw["snaps"], raw["gt"], raw["inst"], raw["turns"]
        self.name = raw["dir"].name
        ids = [a.get("id") for a in self.inst.get("agents", []) if isinstance(a, dict)]
        for s in self.snaps:
            ids += list((s.get("values") or {}).keys())
        ids += [e.get("agent") for e in self.turns]
        self.agents = sorted({a for a in ids if isinstance(a, str) and a})
        self.agent_set = set(self.agents)
        rounds = [e.get("round", 0) for e in self.ev] + [s.get("round", 0) for s in self.snaps]
        self.rounds = (max(rounds) + 1) if rounds else 0
        self.snap = {s.get("round"): s for s in self.snaps}
        self.store_owner = {}
        for s in self.snaps:
            for sid, rec in ((s.get("subsistence") or {}).get("stores") or {}).items():
                if isinstance(rec, dict) and rec.get("owner"):
                    self.store_owner[sid] = rec["owner"]
        for e in self.ev:
            d = _data(e)
            if e.get("type") in ("store_built", "store_owner") and d.get("store") and d.get("owner"):
                self.store_owner.setdefault(d["store"], d["owner"])
        self.kin = defaultdict(set)
        for e in self.ev:
            d = _data(e)
            if e.get("type") == "kin" and d.get("child"):
                for p in d.get("parents") or []:
                    self.kin[d["child"]].add(p)
                    self.kin[p].add(d["child"])
        self.alive = {}                                                 # round -> living agents
        for s in self.snaps:
            dead = set(((s.get("conflict") or {}).get("dead") or {}).keys())
            self.alive[s.get("round")] = [a for a in (s.get("values") or {}) if a not in dead]
        self.shock = self._first_shock()

    def _first_shock(self):
        rs = [e.get("round", 0) for e in self.ev if e.get("type") in ("forest_shock", "blight", "shock")]
        rs += [e.get("round", 0) for e in self.ev if e.get("type") == "subsistence_round" and _data(e).get("shocks")]
        return min(rs) if rs else None

    def owner(self, acct):
        """The owner of an account key: an agent, an institution id, or None for the world and estates."""
        if not isinstance(acct, str) or not acct:
            return None
        if acct == "reserve":
            return "J0"
        if acct.startswith("reserve:"):
            return acct[8:]
        if acct.startswith("assoc:"):
            return acct[6:]
        if acct.startswith("store:"):
            return self.store_owner.get(acct[6:], acct)
        if acct in ("world", "nobody") or acct.startswith(("estate", "world")):
            return None
        return acct

    def moves(self):
        for e in self.ev:
            if e.get("type") == "move":
                d = _data(e)
                yield e, d


# ---------------------------------------------------------------------- market (01 #12)
def market(R: Run) -> dict:
    posts = [e for e in R.ev if e.get("type") in ("channel_post", "post")]
    dms = [e for e in R.ev if e.get("type") == "dm"]
    by_ch = defaultdict(lambda: [0, 0])
    asks, bids = defaultdict(list), defaultdict(list)
    for e in posts:
        d = _data(e)
        ch = d.get("channel_id") or d.get("channel") or "square"
        by_ch[ch][0] += 1
        m = MARKET_RX.match(str(d.get("text") or "").strip())
        if m:
            by_ch[ch][1] += 1
            (asks if m.group(1).upper() == "SELL" else bids)[e.get("round", 0)].append(float(m.group(3)))
    mkt = [c for c in by_ch if "market" in str(c).lower()]
    n_m = sum(by_ch[c][0] for c in mkt)
    p_m = sum(by_ch[c][1] for c in mkt)
    rows = []
    for r in range(R.rounds):
        a, b = _median(asks.get(r, [])), _median(bids.get(r, []))
        if a is not None or b is not None:
            rows.append({"round": r, "asks": len(asks.get(r, [])), "bids": len(bids.get(r, [])), "median_ask": a, "median_bid": b,
                         "spread": _r(a - b) if a is not None and b is not None else None})
    loose = defaultdict(list)
    for e in posts + dms:
        t = str(_data(e).get("text") or "")
        if MARKET_RX.match(t.strip()):                                  # counted by the strict parser
            continue
        for m in LOOSE_RX[0].finditer(t):
            q, p = float(m.group(1)), float(m.group(2))
            if q > 0:
                loose[e.get("round", 0)].append(p / q)
        for m in LOOSE_RX[1].finditer(t):
            loose[e.get("round", 0)].append(float(m.group(1)))

    def ratio(series):
        if R.shock is None:
            return None
        pre = [x for r, xs in series.items() if r < R.shock for x in xs]
        post = [x for r, xs in series.items() if r >= R.shock for x in xs]
        return _r(_median(post) / _median(pre)) if pre and post and _median(pre) else None

    parsed = sum(v[1] for v in by_ch.values())
    return {"available": bool(posts or dms), "posts": len(posts), "parsed": parsed,
            "market_channels": mkt, "market_posts": n_m, "market_parse_share": _r(p_m / n_m) if n_m else None,
            "parsed_by_channel": {c: v[1] for c, v in sorted(by_ch.items()) if v[1]},
            "median_ask": _median([x for xs in asks.values() for x in xs]),
            "median_bid": _median([x for xs in bids.values() for x in xs]),
            "price_ratio_after_shock": ratio({r: asks.get(r, []) + bids.get(r, []) for r in set(asks) | set(bids)}),
            "series": rows,
            "loose_quotes": sum(len(v) for v in loose.values()),
            "loose_median_price": _r(_median([x for xs in loose.values() for x in xs])),
            "loose_price_ratio_after_shock": ratio(loose)}


# ---------------------------------------------------------------------- money and food flows (03 #15)
def _currencies(R: Run) -> list:
    cs = set()
    for s in R.snaps:
        cs |= set((s.get("supplies") or {}).keys())
    cur = R.gt.get("currencies")
    if isinstance(cur, dict):
        cs |= set(cur)
    elif isinstance(cur, list):
        cs |= {c if isinstance(c, str) else c.get("name") for c in cur if c}
    return sorted(c for c in cs if c)


def _flows(R: Run, item: str):
    """Per round: (auto qty, voluntary qty), and per agent the rounds with an outgoing payment of their own."""
    auto, vol = Counter(), Counter()
    paid = defaultdict(set)
    for e, d in R.moves():
        if d.get("item") != item:
            continue
        why = str(d.get("why") or "")
        if why.startswith(EXCLUDED_WHY):
            continue
        so, do = R.owner(d.get("src")), R.owner(d.get("dst"))
        if so is None or do is None or so == do:
            continue
        r, q = e.get("round", 0), _num(d.get("qty"))
        if why.startswith(AUTO_WHY):
            auto[r] += q
        else:
            vol[r] += q
            actor = e.get("agent")
            if actor in R.agent_set and actor == so and not why.startswith("charge"):
                paid[actor].add(r)
    return auto, vol, paid


def _hoard(R: Run, held_by_round: dict, paid: dict) -> list:
    out = []
    for r in sorted(held_by_round):
        held = held_by_round[r]
        tot = sum(held.values())
        if tot <= 0:
            out.append(None)
            continue
        idle = sum(q for a, q in held.items() if not any(r - HOARD_WINDOW < x <= r for x in paid.get(a, ())))
        out.append(_r(idle / tot))
    return out


def _arrears(R: Run) -> dict:
    owed = defaultdict(float)
    by_law = {}
    for lid, law in (R.gt.get("laws") or {}).items():
        if not isinstance(law, dict):
            continue
        pub, st = law.get("public"), law.get("state")
        books = []
        for src in (pub, st):
            if isinstance(src, str):
                try:
                    src = ast.literal_eval(src)
                except (ValueError, SyntaxError):
                    src = None
            if isinstance(src, dict):
                books.append(src.get("owed"))
                if isinstance(src.get("book"), dict):
                    books.append(src["book"].get("owed"))
        tot = 0.0
        seen = set()
        for b in books:
            if not isinstance(b, dict):
                continue
            for who, v in b.items():
                if who in seen:
                    continue
                q = sum(_num(x) for x in v.values()) if isinstance(v, dict) else _num(v)
                if q > 1e-9:
                    seen.add(who)
                    owed[who] += q
                    tot += q
        if tot > 1e-9:
            by_law[lid] = {"title": law.get("title"), "owed": _r(tot), "status": law.get("status")}
    return {"total": _r(sum(owed.values())), "creditors": len(owed), "by_creditor": {a: _r(q) for a, q in sorted(owed.items())},
            "by_law": by_law, "note": "final balances from the laws' records (per-round books are not logged)"}


def money(R: Run) -> dict:
    out = {}
    for c in _currencies(R):
        auto, vol, paid = _flows(R, c)
        rows = []
        for r in range(R.rounds):
            supply = _num(((R.snap.get(r) or {}).get("supplies") or {}).get(c), 0.0)
            v = (auto[r] + vol[r]) / supply if supply > 0 else None
            rows.append({"round": r, "velocity": _r(v), "auto": _r(auto[r]), "voluntary": _r(vol[r]), "supply": supply or None})
        held = {s.get("round"): {a: _num(h.get(c)) for a, h in (s.get("holdings") or {}).items() if a in R.agent_set}
                for s in R.snaps}
        hoard = _hoard(R, held, paid)
        tv, ta = sum(vol.values()), sum(auto.values())
        vs = [x["velocity"] for x in rows if x["velocity"] is not None]
        g = [_gini(h.values()) for _, h in sorted(held.items())]
        out[c] = {"velocity_mean": _r(statistics.mean(vs)) if vs else None, "voluntary_share": _r(tv / (tv + ta)) if tv + ta else None,
                  "hoard_ratio_mean": _r(statistics.mean([h for h in hoard if h is not None])) if any(h is not None for h in hoard) else None,
                  "hoard_ratio_end": hoard[-1] if hoard else None,
                  "hoard_alarm_rounds": sum(1 for h in hoard if h is not None and h > 0.5),
                  "gini_start": g[0] if g else None, "gini_end": g[-1] if g else None,
                  "series": [dict(x, hoard_ratio=h) for x, h in zip(rows, hoard + [None] * (len(rows) - len(hoard)))]}
    vals = [_gini((s.get("values") or {}).values()) for s in R.snaps]
    return {"available": bool(out), "currencies": out, "arrears": _arrears(R),
            "holdings_gini": {"start": vals[0] if vals else None, "end": vals[-1] if vals else None, "path": vals}}


# ---------------------------------------------------------------------- food (01 §7)
def _office_holders(R: Run, r) -> dict:
    """{agent: [office rights]} held at the end of round r."""
    s = R.snap.get(r) or {}
    return {a: [x for x in rs if isinstance(x, str) and "." in x and INST.match(x.split(".", 1)[0])]
            for a, rs in (s.get("rights") or {}).items()}


def food(R: Run) -> dict:
    if not any((s.get("subsistence") or {}).get("food") for s in R.snaps):
        return {"available": False, "why": "no subsistence food in the snapshots"}
    auto, vol, paid = _flows(R, "food")
    held = {}
    for s in R.snaps:
        sub = s.get("subsistence") or {}
        h = {a: _num(q) for a, q in (sub.get("food") or {}).items() if a in R.agent_set}
        for sid, rec in (sub.get("stores") or {}).items():
            if isinstance(rec, dict) and rec.get("owner") in R.agent_set:
                h[rec["owner"]] = h.get(rec["owner"], 0.0) + _num(rec.get("food"))
        held[s.get("round")] = h
    hoard = _hoard(R, held, paid)
    rows = []
    for r in range(R.rounds):
        tot = sum((held.get(r) or {}).values()) + sum(_num(x.get("food")) for x in (((R.snap.get(r) or {}).get("subsistence") or {})
                                                                                    .get("stores") or {}).values()
                                                       if isinstance(x, dict) and x.get("owner") not in R.agent_set)
        rows.append({"round": r, "velocity": _r((auto[r] + vol[r]) / tot) if tot > 0 else None, "auto": _r(auto[r]),
                     "voluntary": _r(vol[r]), "food": _r(tot), "hoard_ratio": hoard[r] if r < len(hoard) else None,
                     "gini": _gini((held.get(r) or {}).values()) if held.get(r) else None})
    stores = defaultdict(dict)
    for s in R.snaps:
        for sid, rec in ((s.get("subsistence") or {}).get("stores") or {}).items():
            if isinstance(rec, dict):
                stores[sid][s.get("round")] = _r(_num(rec.get("food")), 2)
    # keeper draws (withdrawals by holders of an office that controls the store) vs relief (law moves of food to agents)
    controls = _office_controls(R)
    draws = Counter()
    for e in R.ev:
        d = _data(e)
        if e.get("type") == "store_withdrawal":
            sid, a = d.get("store"), e.get("agent")
            if any(f"store:{sid}" in ctl and a in _holders_at(R, right, e.get("round", 0)) for right, ctl in controls.items()):
                draws[a] += _num(d.get("qty"))
    relief = Counter()
    for e, d in R.moves():
        if d.get("item") == "food" and str(d.get("why") or "").startswith("law:") and d.get("dst") in R.agent_set \
                and R.owner(d.get("src")) not in R.agent_set:
            relief[d["dst"]] += _num(d.get("qty"))
    # hoarding index: Δ stored food in the 2 rounds after the shock, by owner kind
    hoarding = None
    if R.shock is not None:
        def lvl(r):
            out = defaultdict(float)
            for sid, rec in (((R.snap.get(r) or {}).get("subsistence") or {}).get("stores") or {}).items():
                if isinstance(rec, dict):
                    o = rec.get("owner")
                    k = "agents" if o in R.agent_set else ("polity" if isinstance(o, str) and POLITY.match(o) else "institutions")
                    out[k] += _num(rec.get("food"))
            return out
        a, b = lvl(R.shock - 1), lvl(min(R.shock + 2, R.rounds - 1))
        if R.snap.get(R.shock - 1) is not None:
            hoarding = {"shock_round": R.shock, "from_round": R.shock - 1, "to_round": min(R.shock + 2, R.rounds - 1),
                        **{k: _r(b.get(k, 0) - a.get(k, 0)) for k in ("agents", "institutions", "polity")}}
    # officials vs others (end-of-run food holdings, own stores included)
    last = R.snaps[-1].get("round") if R.snaps else None
    offs = {a for a, rs in _office_holders(R, last).items() if rs}
    h = held.get(last) or {}
    off_f = [q for a, q in h.items() if a in offs]
    oth_f = [q for a, q in h.items() if a not in offs]
    stages = [{"round": e.get("round", 0), **(_data(e).get("stages") or {}), "deaths": len(_data(e).get("deaths") or [])}
              for e in R.ev if e.get("type") == "subsistence_round"]
    surv = {"before": [0, 0], "after": [0, 0]}
    for t in R.turns:
        k = "after" if R.shock is not None and t.get("round", 0) >= R.shock else "before"
        for a in _data(t).get("actions") or []:
            name = a.get("action") if isinstance(a, dict) else None
            if not name:
                continue
            surv[k][1] += 1
            if name in SURVIVAL_ACTIONS or (name == "transfer" and _args(a).get("item") == "food"):
                surv[k][0] += 1
    vs = [x["velocity"] for x in rows if x["velocity"] is not None]
    hs = [x for x in hoard if x is not None]
    return {"available": True, "velocity_mean": _r(statistics.mean(vs)) if vs else None,
            "hoard_ratio_mean": _r(statistics.mean(hs)) if hs else None, "hoard_ratio_end": hoard[-1] if hoard else None,
            "gini_start": rows[0]["gini"] if rows else None, "gini_end": next((x["gini"] for x in reversed(rows) if x["gini"] is not None), None),
            "keeper_draws": _r(sum(draws.values())), "keeper_draws_by_agent": {a: _r(q) for a, q in sorted(draws.items())},
            "relief_paid": _r(sum(relief.values())), "relief_recipients": len(relief),
            "hoarding_index": hoarding, "shock_round": R.shock,
            "officials_mean_food": _r(statistics.mean(off_f)) if off_f else None,
            "others_mean_food": _r(statistics.mean(oth_f)) if oth_f else None,
            "survival_share_before": _r(surv["before"][0] / surv["before"][1]) if surv["before"][1] else None,
            "survival_share_after": _r(surv["after"][0] / surv["after"][1]) if surv["after"][1] else None,
            "deaths": sum(x["deaths"] for x in stages), "hunger": stages,
            "stores": {sid: [lv.get(r) for r in range(R.rounds)] for sid, lv in sorted(stores.items())},
            "series": rows}


# ---------------------------------------------------------------------- channels (04 §9)
def channels(R: Run) -> dict:
    posts = defaultdict(Counter)
    authors = defaultdict(set)
    engine = Counter()
    agent_posts = 0
    for e in R.ev:
        if e.get("type") not in ("channel_post", "post"):
            continue
        d = _data(e)
        ch = d.get("channel_id") or d.get("channel") or "square"
        a = e.get("agent")
        if a in R.agent_set:
            agent_posts += 1
            posts[ch][e.get("round", 0)] += 1
            authors[ch].add(a)
        else:
            engine[ch] += 1
    dms = [e for e in R.ev if e.get("type") == "dm" and e.get("agent") in R.agent_set]
    groups = Counter((e.get("round"), e.get("agent"), str(_data(e).get("text") or "").strip()) for e in dms)
    reads = [e for e in R.ev if e.get("type") == "channel_read"]
    readers = defaultdict(set)
    by_ch_reads = Counter()
    unread = 0
    for e in reads:
        d = _data(e)
        readers[e.get("round", 0)].add(d.get("agent") or e.get("agent"))
        by_ch_reads[d.get("channel")] += 1
        unread += _num(d.get("unread_before")) > 0
    n = max(1, R.rounds)
    read_share = []
    for r in range(R.rounds):
        alive = R.alive.get(r) or R.agents
        read_share.append(_r(len(readers.get(r, set()) & set(alive)) / len(alive)) if alive else None)
    rs = [x for x in read_share if x is not None]
    return {"available": bool(posts or dms or reads),
            "per_channel": {ch: {"posts": sum(c.values()), "per_round": _r(sum(c.values()) / n), "authors": len(authors[ch]),
                                 "rounds_active": len(c), "reads": by_ch_reads.get(ch, 0)}
                            for ch, c in sorted(posts.items(), key=lambda kv: -sum(kv[1].values()))},
            "channels_used": len(posts), "agent_posts": agent_posts, "engine_posts": dict(engine), "dms": len(dms),
            "dm_share": _r(len(dms) / (len(dms) + agent_posts)) if dms or agent_posts else None,
            "broadcast_by_dm_groups": sum(1 for k, v in groups.items() if v >= 2 and k[2]),
            "reads": len(reads), "reads_with_unread": unread,
            "reader_share_mean": _r(statistics.mean(rs)) if rs else None, "reader_share": read_share,
            "reads_by_channel": dict(by_ch_reads)}


# ---------------------------------------------------------------------- laws (07 §9)
def laws(R: Run) -> dict:
    gl = R.gt.get("laws") or {}
    eff = [e for e in R.ev if e.get("type") == "law_effect"]

    def author(lid, d):
        return d.get("by") or (gl.get(d.get("proposal") or "") or {}).get("author") or (gl.get(lid) or {}).get("author")
    acts, inert, shadowed = [], [], []
    for e in eff:
        d = _data(e)
        if d.get("act") not in ("enact", "amend", None):
            continue
        row = {"round": e.get("round", 0), "law": d.get("law"), "title": d.get("title"), "act": d.get("act") or "enact",
               "author": author(d.get("law"), d), "inert": bool(d.get("inert")), "changes": d.get("n_changes")}
        acts.append(row)
        if row["inert"]:
            inert.append(row)
        if d.get("shadowed"):                                           # a change a rule of higher precedence overrides
            shadowed.append({**row, "shadowed": [s.get("change") for s in d["shadowed"]], "notes": d.get("shadow_notes") or []})
    agent_acts = [a for a in acts if a["author"] in R.agent_set]
    exp_failed = [e for e in R.ev if e.get("type") == "law_expectation_failed"]
    call_failed = [e for e in R.ev if e.get("type") == "law_call_failed"]
    fallback = None
    if not eff:                                                         # older logs: enacted agent laws that never had an effect
        no_eff = [lid for lid, l in gl.items() if isinstance(l, dict) and l.get("author") in R.agent_set
                  and _num(l.get("enacted_round"), -1) > 0 and not l.get("effects")
                  and l.get("status") in ("active", "repealed", "enacted_amendment", "expired")]
        fallback = {"enacted_agent_laws_without_recorded_effect": sorted(no_eff)}
    previews = Counter()
    for t in R.turns:
        for a in _data(t).get("actions") or []:
            if isinstance(a, dict) and a.get("action") == "preview_law":
                previews[t.get("agent")] += 1
    for e in R.ev:
        if e.get("type") == "lookup" and _data(e).get("name") == "preview_law":
            previews[e.get("agent")] += 1
    proposals = [e for e in R.ev if e.get("type") == "proposal"]
    courts = Counter(e.get("type") for e in R.ev if e.get("type") in
                     ("accuse", "respond", "court_rule", "ruling", "appeal", "case_dismissed", "case_final"))
    return {"available": bool(eff or gl), "law_effect_recorded": bool(eff),
            "enacted_acts": len(acts) if eff else None, "inert": len(inert) if eff else None,
            "inert_share": _r(len(inert) / len(acts)) if acts else None,
            "agent_acts": len(agent_acts), "agent_inert": sum(1 for a in agent_acts if a["inert"]),
            "inert_laws": inert, "inert_by_author": dict(Counter(a["author"] for a in inert)),
            "shadowed": len(shadowed) if eff else None, "shadowed_laws": shadowed,
            "expectation_failed": len(exp_failed), "call_failed": len(call_failed),
            "call_failed_by_law": dict(Counter(_data(e).get("law") for e in call_failed)),
            "proposals": len(proposals), "previews": sum(previews.values()), "previews_by_agent": dict(previews),
            "courts": dict(courts), "fallback": fallback}


# ---------------------------------------------------------------------- offices: role adherence and divergence (00 §1-2)
def _literal_offices(code: str):
    if not isinstance(code, str) or "offices" not in code:
        return None
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "offices" for t in node.targets):
            try:
                v = ast.literal_eval(node.value)
            except ValueError:
                return None
            return v if isinstance(v, dict) else None
    return None


def office_specs(R: Run) -> dict:
    """{"<inst>.<office>": spec} from the Offices Acts in ground truth (later versions win), plus any office right seen held."""
    out = {}
    for lid, law in (R.gt.get("laws") or {}).items():
        if not isinstance(law, dict):
            continue
        offs = _literal_offices(law.get("code"))
        if not offs:
            continue
        inst = law.get("jurisdiction") or "J0"
        for name, spec in offs.items():
            if isinstance(spec, dict):
                out[f"{inst}.{name}"] = spec
    for s in R.snaps:
        for rs in (s.get("rights") or {}).values():
            for x in rs:
                if isinstance(x, str) and "." in x and INST.match(x.split(".", 1)[0]):
                    out.setdefault(x, {})
    for lid, law in (R.gt.get("laws") or {}).items():                  # a store law gated on an office (Granary Ration: STORE,
        if not isinstance(law, dict) or law.get("status") not in ("active", None):   # OFFICE) makes that store the office's
            continue
        c = _constants(law.get("code"))
        office, store = c.get("OFFICE"), c.get("STORE")
        if isinstance(office, str) and office in out and isinstance(store, str) and store:
            sid = store if store.startswith("store:") else f"store:{store}"
            spec = out[office] = dict(out[office])
            if sid not in (spec.get("controls") or []):
                spec["controls"] = list(spec.get("controls") or []) + [sid]
    return out


def _constants(code) -> dict:
    """A law's top-level literal constants (NAME = literal)."""
    out = {}
    if not isinstance(code, str):
        return out
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return out
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                out[node.targets[0].id] = ast.literal_eval(node.value)
            except ValueError:
                continue
    return out


def _office_controls(R: Run) -> dict:
    return {right: [str(c) for c in (spec.get("controls") or [])] for right, spec in office_specs(R).items()}


def _holders_at(R: Run, right, r) -> set:
    s = R.snap.get(r) or R.snap.get(r - 1) or {}
    return {a for a, rs in (s.get("rights") or {}).items() if right in rs}


def duty_kinds(right: str, spec: dict) -> list:
    inst, _, name = right.partition(".")
    title = f"{name} {spec.get('title') or ''}".lower()
    kinds = []
    ctl = [str(c) for c in spec.get("controls") or []]
    if any(c.startswith("store:") for c in ctl):
        kinds.append("store")
    pw = spec.get("powers") or []
    if "treasury" in ctl or any(isinstance(p, dict) and p.get("action") in ("transfer", "pay") for p in pw):
        kinds.append("pay")
    if "speak" in pw:
        kinds.append("speak")
    if any(w in title for w in COUNCIL_NAMES):
        kinds.append("legislate")
    if any(w in title for w in ("constable", "prosecut", "sheriff", "marshal", "watch")):
        kinds.append("prosecute")
    if any(w in title for w in ("judge", "justice", "arbiter", "magistrate", "court")):
        kinds.append("judge")
    return kinds or ["act"]


def offices(R: Run) -> dict:
    specs = office_specs(R)
    if not specs:
        return {"available": False, "why": "no offices (no Offices Act and no held office rights)"}
    ch_owner = {}
    for s in R.snaps:
        for cid, rec in (s.get("channels") or {}).items():
            if isinstance(rec, dict) and rec.get("owner"):
                ch_owner[cid] = rec["owner"]
    for e in R.ev:
        d = _data(e)
        if e.get("type") == "channel_opened" and d.get("owner"):
            ch_owner.setdefault(d.get("id") or d.get("channel"), d["owner"])
    # evidence per (agent, round): kinds of institutional acts, with the institution or store they concern
    acts = defaultdict(set)                                             # (agent, round) -> {(kind, target)}
    pay_self = Counter()                                                # right -> treasury payments to self or kin
    kept = defaultdict(float)                                           # (agent, round) -> food drawn from controlled stores
    given = defaultdict(float)                                          # (agent, round) -> food passed on
    any_act = set()
    for t in R.turns:
        if _data(t).get("actions"):
            any_act.add((t.get("agent"), t.get("round", 0)))
    for e in R.ev:
        t, d, a, r = e.get("type"), _data(e), e.get("agent"), e.get("round", 0)
        if a not in R.agent_set:
            continue
        if t in ("store_withdrawal", "store_deposit"):
            acts[(a, r)].add(("store", f"store:{d.get('store')}"))
            if t == "store_withdrawal":
                kept[(a, r)] += _num(d.get("qty"))
        elif t == "move" and str(d.get("src") or "").startswith(("assoc:", "reserve")) and d.get("why") in ("transfer", "office_payment"):
            acts[(a, r)].add(("pay", R.owner(d.get("src"))))
        elif t == "office_payment":
            acts[(a, r)].add(("pay", d.get("as")))
        elif t in ("channel_post", "post"):
            ch = d.get("channel_id") or d.get("channel")
            acts[(a, r)].add(("speak", ch_owner.get(ch)))
            acts[(a, r)].add(("speak_channel", ch))
        elif t in ("vote", "proposal", "amend", "veto_vote"):
            acts[(a, r)].add(("legislate", None))
        elif t in ("accuse", "open_case"):
            acts[(a, r)].add(("prosecute", None))
        elif t in ("court_rule", "ruling", "award"):
            acts[(a, r)].add(("judge", None))
        if t == "transfer" and d.get("item") == "food" and d.get("to") != a:
            given[(a, r)] += _num(d.get("qty"))
    rows = {}
    for right, spec in sorted(specs.items()):
        inst = right.split(".", 1)[0]
        kinds = duty_kinds(right, spec)
        stores = {c for c in (spec.get("controls") or []) if str(c).startswith("store:")}
        held = performed = idle = 0
        per_kind = Counter()
        kept_food = 0.0
        holders = Counter()
        for r in range(R.rounds):
            for a in _holders_at(R, right, r):
                if R.alive.get(r) is not None and a not in R.alive[r]:
                    continue
                held += 1
                holders[a] += 1
                ev = acts.get((a, r), set())
                did = set()
                for k in kinds:
                    if k == "store" and any(x == ("store", s) for s in stores for x in ev):
                        did.add(k)
                    elif k == "pay" and ("pay", inst) in ev:
                        did.add(k)
                    elif k == "speak" and (("speak", inst) in ev or any(x[0] == "speak_channel" and inst in str(x[1]) for x in ev)):
                        did.add(k)
                    elif k in ("legislate", "prosecute", "judge") and (k, None) in ev:
                        did.add(k)
                    elif k == "act" and ev:
                        did.add(k)
                per_kind.update(did)
                performed += bool(did)
                idle += (a, r) not in any_act
                if "store" in kinds and any(x[0] == "store" and x[1] in stores for x in ev):
                    kept_food += max(0.0, kept.get((a, r), 0.0) - given.get((a, r), 0.0))
        rows[right] = {"title": spec.get("title"), "duties": kinds, "holders": dict(holders), "held_rounds": held,
                       "performed_rounds": performed, "adherence": _r(performed / held) if held else None,
                       "by_duty": {k: _r(per_kind[k] / held) if held else None for k in kinds},
                       "idle_rounds": idle, "food_drawn_and_kept": _r(kept_food) if "store" in kinds else None}
    # treasury payments by officers to themselves or their kin (capture)
    for e in R.ev:
        d = _data(e)
        if e.get("type") == "office_payment":
            a, to = e.get("agent"), d.get("to")
            if to == a or to in R.kin.get(a, ()):
                pay_self[d.get("as")] += _num(d.get("qty"))
    held = sum(x["held_rounds"] for x in rows.values())
    perf = sum(x["performed_rounds"] for x in rows.values())
    return {"available": True, "offices": rows, "held_rounds": held, "performed_rounds": perf,
            "adherence": _r(perf / held) if held else None,
            "treasury_paid_to_self_or_kin": {k: _r(v) for k, v in pay_self.items()}}


# ---------------------------------------------------------------------- obligations (defensive: the system may be absent)
def obligations(R: Run) -> dict:
    types = Counter(e.get("type") for e in R.ev)
    ctypes = {t: types[t] for t in sorted(types) if t.startswith(("contract_", "obligation", "fulfil", "petition"))}
    contract_laws = {}
    for s in R.snaps:
        for cid, rec in (s.get("contracts") or {}).items():
            if isinstance(rec, dict):
                for lid in rec.get("laws") or []:
                    contract_laws[lid] = cid
    for lid, law in (R.gt.get("laws") or {}).items():
        if isinstance(law, dict) and law.get("jurisdiction") and law.get("jurisdiction") != "J0":
            contract_laws.setdefault(lid, law["jurisdiction"])
    legs = defaultdict(lambda: {"moves": 0, "qty": Counter(), "rounds": set()})
    for e, d in R.moves():
        why = str(d.get("why") or "")
        if why.startswith("law:") and why[4:] in contract_laws:
            c = legs[contract_laws[why[4:]]]
            c["moves"] += 1
            c["qty"][d.get("item")] += _num(d.get("qty"))
            c["rounds"].add(e.get("round", 0))
    fulfil_acts = sum(1 for t in R.turns for a in _data(t).get("actions") or [] if isinstance(a, dict) and a.get("action") == "fulfil")
    tagged = [e for e in R.ev if e.get("type") in ("transfer", "store_deposit", "office_payment", "move") and _data(e).get("fulfil")]
    missed = defaultdict(int)
    for e in R.ev:
        if e.get("type") != "notify":
            continue
        txt = str(_data(e).get("text") or "")
        for m in re.finditer(r"You missed ([^()]*?)\(([AJ]\d+)\)", txt):
            missed[m.group(2)] += 1
        if "You missed" in txt and not re.search(r"\(([AJ]\d+)\)", txt):
            missed["?"] += 1
    would = could = 0
    for lid, law in (R.gt.get("laws") or {}).items():
        st = law.get("state") if isinstance(law, dict) else None
        if isinstance(st, str):
            try:
                st = ast.literal_eval(st)
            except (ValueError, SyntaxError):
                st = None
        if isinstance(st, dict):
            for key, name in (("missed", "would"), ("could", "could")):
                for per in (st.get(key) or {}).values():
                    if isinstance(per, dict):
                        n = sum(int(_num(v)) for v in per.values())
                        if name == "would":
                            would += n
                        else:
                            could += n
    left = [e for e in R.ev if e.get("type") == "contract_left"]
    notice = types.get("contract_leave_pending", 0) + sum(1 for e in R.ev if e.get("type") == "gazette"
                                                           and "gave notice" in str(_data(e).get("text") or ""))
    has = bool(ctypes or legs or fulfil_acts or tagged or missed)
    return {"available": has, "obligations_system": bool(fulfil_acts or tagged or missed or types.get("petition_unanswered")),
            "event_counts": ctypes,
            "contracts_created": types.get("contract_created", 0), "joined": types.get("contract_joined", 0),
            "left": len(left), "left_by_reason": dict(Counter(str(_data(e).get("why")) for e in left)),
            "notices_given": notice, "breaches": types.get("contract_breach", 0), "pulls": types.get("contract_pull", 0),
            "legs_run": {c: {"moves": v["moves"], "rounds": len(v["rounds"]), "qty": {k: _r(q) for k, q in v["qty"].items()}}
                         for c, v in sorted(legs.items())},
            "fulfil_actions": fulfil_acts, "fulfil_payments": len(tagged),
            "missed_notices": dict(missed), "missed_would_not": would, "missed_could_not": could,
            "arrears": _arrears(R)["total"]}


# ---------------------------------------------------------------------- the whole analysis
SECTIONS = (("market", market), ("money", money), ("food", food), ("channels", channels), ("laws", laws), ("offices", offices),
            ("obligations", obligations))


def analyse(run_dir) -> dict:
    raw = load(run_dir)
    if not raw["events"]:
        return {"run": Path(run_dir).name, "available": False, "why": "no events.jsonl"}
    R = Run(raw)
    out = {"run": R.name, "rounds": R.rounds, "agents": len(R.agents), "shock_round": R.shock}
    for name, fn in SECTIONS:
        try:
            out[name] = fn(R)
        except Exception as e:                                          # one broken section never hides the others
            out[name] = {"available": False, "error": f"{type(e).__name__}: {e}"}
    out["headline"] = headline(out)
    return out


def headline(res: dict) -> dict:
    m = (res.get("money") or {}).get("currencies") or {}
    cur = "penny" if "penny" in m else (sorted(m)[0] if m else None)
    mc = m.get(cur) or {}
    f, c, lw, o, ob = (res.get(k) or {} for k in ("food", "channels", "laws", "offices", "obligations"))
    return {"currency": cur, "velocity": mc.get("velocity_mean"), "voluntary_share": mc.get("voluntary_share"),
            "hoard_ratio": mc.get("hoard_ratio_mean"), "hoard_ratio_end": mc.get("hoard_ratio_end"),
            "arrears": ((res.get("money") or {}).get("arrears") or {}).get("total"),
            "food_velocity": f.get("velocity_mean"), "food_hoard_ratio": f.get("hoard_ratio_mean"),
            "food_hoarding_index": f.get("hoarding_index"), "keeper_draws": f.get("keeper_draws"), "relief_paid": f.get("relief_paid"),
            "market_parsed": (res.get("market") or {}).get("parsed"), "loose_food_quotes": (res.get("market") or {}).get("loose_quotes"),
            "channels_used": c.get("channels_used"), "dm_share": c.get("dm_share"), "reader_share": c.get("reader_share_mean"),
            "inert_laws": lw.get("inert"), "enacted_acts": lw.get("enacted_acts"), "call_failed": lw.get("call_failed"),
            "laws_without_recorded_effect": len((lw.get("fallback") or {}).get("enacted_agent_laws_without_recorded_effect") or [])
            if lw.get("fallback") else None,
            "role_adherence": o.get("adherence"), "breaches": ob.get("breaches"), "missed_obligations": sum((ob.get("missed_notices") or {}).values())
            if ob.get("available") else None}


# ---------------------------------------------------------------------- text and markdown
def _f(x, nd=2):
    return "n/a" if x is None else (f"{x:.{nd}f}" if isinstance(x, float) else str(x))


def markdown(res: dict) -> str:
    if res.get("available") is False:
        return f"# Institutions: {res.get('run')}\n\n{res.get('why')}\n"
    h = res["headline"]
    L = [f"# Institutions: {res['run']}", "",
         f"{res['agents']} agents, {res['rounds']} rounds; first shock round: {_f(res.get('shock_round'))}. "
         "Metrics of review 31 (docs/review/31_institutions/08_integration.md item 1.11); `python -m cybertron institutions`.", "",
         "## Headline", "", "| metric | value |", "|---|---|"]
    for k, v in h.items():
        L.append(f"| {k} | {_f(json.dumps(v) if isinstance(v, dict) else v)} |")
    o = res.get("offices") or {}
    if o.get("available"):
        L += ["", "## Role adherence (offices)", "", "| office | title | duties | held rounds | adherence | by duty | idle | food kept |",
              "|---|---|---|---|---|---|---|---|"]
        for right, x in o["offices"].items():
            L.append(f"| {right} | {x.get('title') or ''} | {', '.join(x['duties'])} | {x['held_rounds']} | {_f(x['adherence'])} | "
                     + ", ".join(f"{k} {_f(v)}" for k, v in x["by_duty"].items()) + f" | {x['idle_rounds']} | {_f(x['food_drawn_and_kept'])} |")
    m = (res.get("money") or {}).get("currencies") or {}
    if m:
        L += ["", "## Money", "", "| currency | velocity | voluntary share | hoard ratio (mean, end) | alarm rounds | Gini start → end |",
              "|---|---|---|---|---|---|"]
        for c, x in m.items():
            L.append(f"| {c} | {_f(x['velocity_mean'], 3)} | {_f(x['voluntary_share'])} | {_f(x['hoard_ratio_mean'])}, "
                     f"{_f(x['hoard_ratio_end'])} | {x['hoard_alarm_rounds']} | {_f(x['gini_start'])} → {_f(x['gini_end'])} |")
        ar = res["money"]["arrears"]
        L.append(f"\nArrears at the end: {_f(ar['total'])} to {ar['creditors']} creditors ({', '.join(ar['by_law']) or 'none'}).")
    f = res.get("food") or {}
    if f.get("available"):
        L += ["", "## Food", "",
              f"- velocity {_f(f['velocity_mean'], 3)}, hoard ratio {_f(f['hoard_ratio_mean'])} (end {_f(f['hoard_ratio_end'])}), "
              f"Gini {_f(f['gini_start'])} → {_f(f['gini_end'])}, deaths {f['deaths']}",
              f"- keeper draws {_f(f['keeper_draws'])}, relief paid {_f(f['relief_paid'])} to {f['relief_recipients']} agents",
              f"- hoarding index (Δ stored food after the shock): {json.dumps(f['hoarding_index'])}",
              f"- officials' mean food {_f(f['officials_mean_food'])} vs others' {_f(f['others_mean_food'])}",
              f"- survival-action share {_f(f['survival_share_before'])} before the shock, {_f(f['survival_share_after'])} after"]
    c = res.get("channels") or {}
    if c.get("available"):
        L += ["", "## Channels", "", f"DM share {_f(c['dm_share'])} ({c['dms']} DMs, {c['agent_posts']} agent posts); "
              f"broadcast-by-DM groups {c['broadcast_by_dm_groups']}; reads {c['reads']}, mean share of agents reading a round "
              f"{_f(c['reader_share_mean'])}.", "", "| channel | posts | per round | authors | rounds active | reads |", "|---|---|---|---|---|---|"]
        for ch, x in c["per_channel"].items():
            L.append(f"| {ch} | {x['posts']} | {_f(x['per_round'])} | {x['authors']} | {x['rounds_active']} | {x['reads']} |")
    lw = res.get("laws") or {}
    if lw.get("available"):
        L += ["", "## Laws", "", (f"{lw['inert']} inert of {lw['enacted_acts']} enactments and amendments (agent-written: "
              f"{lw['agent_inert']} of {lw['agent_acts']})" if lw["law_effect_recorded"] else
              "No law_effect events (older log); agent laws enacted after setup with no recorded effect: "
              + (", ".join(lw["fallback"]["enacted_agent_laws_without_recorded_effect"]) or "none"))
              + f"; expectation failures {lw['expectation_failed']}, failed calls {lw['call_failed']}; {lw['proposals']} proposals, "
              f"{lw['previews']} previews."]
        for x in lw["inert_laws"]:
            L.append(f"- r{x['round']} {x['law']} '{x['title']}' ({x['act']}, by {x['author']})")
        if lw.get("shadowed_laws"):                                     # changes that do not apply (laweffects.shadows)
            L += ["", f"{len(lw['shadowed_laws'])} acts with shadowed changes (in the tables, overridden by a rule of higher precedence):"]
            for x in lw["shadowed_laws"]:
                L.append(f"- r{x['round']} {x['law']} '{x['title']}' ({x['act']}, by {x['author']}): " + "; ".join(x["shadowed"]))
    ob = res.get("obligations") or {}
    if ob.get("available"):
        L += ["", "## Contracts and obligations", "",
              f"created {ob['contracts_created']}, joined {ob['joined']}, left {ob['left']} {json.dumps(ob['left_by_reason'])}, "
              f"notices {ob['notices_given']}, breaches {ob['breaches']}, pulls {ob['pulls']}; fulfil actions {ob['fulfil_actions']}, "
              f"fulfil payments {ob['fulfil_payments']}; missed {json.dumps(ob['missed_notices'])} (would-not {ob['missed_would_not']}, "
              f"could-not {ob['missed_could_not']}); legs run {json.dumps(ob['legs_run'])}."]
    return "\n".join(L) + "\n"


def text(res: dict) -> str:
    h = res.get("headline") or {}
    return f"{res.get('run')}: " + ", ".join(f"{k} {_f(json.dumps(v) if isinstance(v, dict) else v)}" for k, v in h.items())


def add_arguments(p) -> None:
    p.add_argument("runs", nargs="+", help="run directories")
    p.add_argument("--json", help="write the results here (one object for one run, a list for several); nothing is written into the run")
    p.add_argument("--md", help="write the markdown report here (several runs: concatenated)")


def cmd(a) -> int:
    res = [analyse(r) for r in a.runs]
    for r in res:
        print(text(r))
    if a.json:
        Path(a.json).write_text(json.dumps(res[0] if len(res) == 1 else res, indent=1, default=str))
    if a.md:
        Path(a.md).write_text("\n".join(markdown(r) for r in res))
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m cybertron.analysis.institutions", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    add_arguments(p)
    return cmd(p.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
