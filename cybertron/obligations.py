"""Manual obligations and the accountability layer (docs/review/31_institutions/00_framework.md §1: an institution works only while
its people do its work; automation is the accountability layer, never the labour).

A standing contract's leg (cybertron/standing.py) runs in one of two modes. `auto` is the engine-18 behaviour: the leg moves goods at
the end of the round with no action from anyone. `manual` (contracts.legs_default, or the contract's MODE, or a leg's own "mode"):
nothing moves by itself. The obligated party meets the leg by acting within the round:

  fulfil {"contract": "A1", "leg": "D"}  moves exactly what is still due, from the party's holdings (above the leg's keep), or, for
                                         an institution's leg, out of its treasury (transfer "as") or its store (withdraw, then
                                         give) when the actor is an officer allowed to;
  any matching transfer                  the right item, from the obligor (or "as" the obligor institution, or by one of its
                                         officers), to the right counterparty (agent, treasury or store), counts toward it;
                                         partial counts as partial.

What the engine does by itself is the accountability layer, here:
  settle (round end, before the laws)    reads this round's transfers (transfer, store_deposit, office_payment events) and credits
                                         them to the open obligations: tagged fulfil payments first, then fixed legs, then legs paid
                                         per unit of another (whose due is what the base leg delivered); writes each law's
                                         state["paid"]; the law (standing.run_manual) then records kept / missed / overdue, counts
                                         could-not vs would-not misses, and escalates by the contract's terms (GRACE, bond, PENALTY,
                                         FORUM, ON_BREACH);
  notices (round end, after the laws)    an unmet obligation notifies the counterparty ("Bryn did not deliver 2 food to ...; 2
                                         overdue") and the defaulter (what it missed, why, and how far it is from the penalty); a
                                         missed duty leg (done by acting) is recorded and told the same way;
  state lines (every turn)               OBLIGATIONS: what is due this round, to whom, the exact fulfil, what is overdue and what was
                                         missed last round; and what others owe the agent;
  role cards (contracts.role_cards)      ROLE: one card per office and contract position (framework §2): purpose, whom it answers to
                                         and who answers to it, what it gets and from which leg, this round's numbers, and the 2-4
                                         decisions it owns with exact syntax (a vital line: at the top of the state); an
                                         officer's card also lists members on no roster and applicants (with the enrol action),
                                         and the recall route of an elected office; OFFER: an open contract (a shop's Board) for
                                         agents not on it, with the steps to take it up (review 31.09 fixes 1-3, 7);
  petitions                              messages to an institution's inbox (@A1) by non-officers, unanswered (no officer has sent
                                         the petitioner a message since), are listed to the officers; after
                                         institutions.petition_public_after rounds a public notice names the office.

The scripted bots perform their obligations (contracts.bot_obligations perform), or neglect them (neglect: a collapse test).

Engine 19 (contracts.miss_judged turn): a miss is judged on what the payer held at the end of its turns this round, not at the
round's end (holdings at turns, below). The rest is off by default: a spec turns it on with contracts {legs_default: manual,
obligations: true, role_cards: true}, actions.forgiving and institutions.petition_public_after (cybertron/specs/usability/v2/*).
"""
from __future__ import annotations

import functools
import json

EPS = 1e-6


# ---------------------------------------------------------------------- settings
def _kc():
    from cybertron import contracts as KC
    return KC


def cfg(k) -> dict:
    return _kc().cfg(k)


def fulfil_on(k) -> bool:
    return "contracts" in k.w and bool(cfg(k).get("obligations"))


def cards_on(k) -> bool:
    return "contracts" in k.w and bool(cfg(k).get("role_cards"))


def petition_after(k) -> int:
    from cybertron import laweffects as LE
    try:
        return max(0, int(LE.setting(k.spec, "institutions.petition_public_after") or 0))
    except (TypeError, ValueError):
        return 0


@functools.lru_cache(maxsize=512)
def _consts(code: str) -> dict:
    try:
        return _kc().constants(code)
    except Exception:                                                   # noqa: BLE001 (not a standing contract's code)
        return {}


def consts(law) -> dict:
    return _consts(law.get("code") or "")


def _fmt(x) -> str:
    x = float(x)
    return f"{x:.3g}" if abs(x - round(x)) > 1e-9 else str(int(round(x)))


# ---------------------------------------------------------------------- accounts
def _inst(k, acct):
    """(institution id, resource) of an institution's account: ("A1", "treasury") for assoc:A1, ("J0", "treasury") for the reserve,
    ("A1", "store:S1") for A1's store; (None, None) for an agent or an agent's store."""
    from cybertron import accounts as AC
    if not isinstance(acct, str) or acct in k.w["agents"]:
        return None, None
    if acct.startswith(AC.ASSOC):
        return acct[len(AC.ASSOC):], "treasury"
    if acct == "reserve":
        return "J0", "treasury"
    if acct.startswith("reserve:"):
        return acct[len("reserve:"):], "treasury"
    if acct.startswith("store:"):
        rec = AC.stores(k).get(acct[6:])
        if rec is None or rec["owner"] in k.w["agents"]:
            return None, None
        return rec["owner"], acct
    if acct == "J0" or acct in AC.assocs(k):
        return acct, "treasury"
    return None, None


def norm(k, acct):
    """An account as the obligations compare them: an institution's id is its treasury's key."""
    from cybertron import accounts as AC
    if not isinstance(acct, str) or acct in k.w["agents"] or acct.startswith("store:"):
        return acct
    if acct == "J0" or acct in AC.assocs(k):
        return AC.treasury_of(k, acct)
    return acct


def payers_of(k, acct) -> list:
    """Who meets an obligation from this account: the agent itself; an agent's store's owner; for an institution's treasury or store,
    the holders of the offices controlling it, else its officers, else (an association without offices) its founder."""
    from cybertron import accounts as AC
    from cybertron import institutions as IN
    if not isinstance(acct, str):
        return []
    if acct in k.w["agents"]:
        return [acct]
    if acct.startswith("store:"):
        rec = AC.stores(k).get(acct[6:])
        if rec is not None and rec["owner"] in k.w["agents"]:
            return [rec["owner"]]
    iid, res = _inst(k, acct)
    if iid is None:
        return []
    offs = IN.controlling(k, iid, res)
    if offs:
        return sorted({h for o in offs for h in IN.holders(k, iid, o)})
    off = IN.officers(k, iid)
    if off:
        return list(off)
    rec = AC.assocs(k).get(iid) if "contracts" in k.w else None
    if rec and rec.get("founder") in rec.get("members", ()):
        return [rec["founder"]]
    return []


def shown(k, acct) -> str:
    """An account in a sentence: an agent's name, "A1's treasury", "the Corner Shop's store S1"."""
    from cybertron import institutions as IN
    if not isinstance(acct, str):
        return "?"
    if acct in k.w["agents"]:
        return acct
    iid, res = _inst(k, acct)
    if iid is None:
        return acct[6:] + "'s store" if acct.startswith("store:") else acct
    name = (IN.get(k, iid) or {}).get("name")
    who = f"{name} ({iid})" if name else iid
    return f"{who}'s treasury" if res == "treasury" else f"{who}'s store {res[6:]}"


def party_name(k, acct) -> str:
    from cybertron import institutions as IN
    if not isinstance(acct, str) or acct in k.w["agents"]:
        return str(acct)
    iid, _ = _inst(k, acct)
    if iid is None:
        return acct
    name = (IN.get(k, iid) or {}).get("name")
    return f"{name} ({iid})" if name else iid


def _money(k, item) -> bool:
    return item in (k.w.get("currencies") or {}) or item in ("penny", "coin", "silver", "gold")


# ---------------------------------------------------------------------- the open obligations
def laws(k) -> list:
    """Active laws with manual legs (their state carries "dues", written by standing.write_lines), in enactment order."""
    out = []
    for lid in k.w.get("law_order") or ():
        law = k.w["laws"].get(lid)
        if law and law.get("status") == "active" and isinstance((law.get("state") or {}).get("dues"), list):
            out.append(law)
    return out


def obligations(k) -> list:
    """Every manual leg due this round or overdue, one dict each (the law's dues plus where it lives)."""
    from cybertron import jurisdictions as J
    out = []
    for law in laws(k):
        c = consts(law)
        iid = J.law_jur(k, law["id"])
        for d in law["state"]["dues"]:
            ob = dict(d)
            ob.update({"lid": law["id"], "iid": iid, "label": str(c.get("LABEL") or law.get("title") or law["id"]),
                       "id": f"{law['id']}|{d['key']}|{d['leg']}", "src": norm(k, d["from"]), "dst": norm(k, d["to"])})
            out.append(ob)
    return out


def _round_events(k) -> list:
    out = []
    for e in reversed(k.events):
        if e.get("round") != k.r:
            break
        out.append(e)
    out.reverse()
    return out


def payments(k) -> list:
    """This round's transfers as payments: {payer: ("agent", id) | ("inst", iid), officer, dst, item, qty, tag}."""
    out = []
    for e in _round_events(k):
        t, d = e["type"], e.get("data") or {}
        if t == "transfer":
            dst = d.get("treasury") or d.get("to")
            payer = ("inst", d["as"]) if d.get("as") else ("agent", e["agent"])
        elif t == "store_deposit":
            dst, payer = "store:" + str(d.get("store")), ("agent", e["agent"])
        elif t == "office_payment":
            dst, payer = d.get("treasury") or d.get("to"), ("inst", d.get("as"))
        else:
            continue
        try:
            q = float(d.get("qty") or 0)
        except (TypeError, ValueError):
            continue
        if q <= EPS:
            continue
        out.append({"payer": payer, "officer": e["agent"], "dst": norm(k, dst), "item": d.get("item", "food"), "left": q,
                    "tag": d.get("fulfil")})
    return out


def _src_ok(k, ob, pay, loose) -> bool:
    who, x = pay["payer"]
    s = ob["src"]
    if who == "agent":
        if x == s:
            return True
        return loose and s not in k.w["agents"] and x in payers_of(k, s)
    return _inst(k, s)[0] == x and x is not None


def ledger(k, obs=None) -> dict:
    """{obligation id: [due now, credited]} from this round's payments. Tagged fulfil payments go to their obligation; then fixed
    legs take matching payments (the obligor's own first, then an officer's personal ones for an institution's leg); then legs paid
    per unit of another leg, whose due is what that leg delivered this round (plus anything overdue)."""
    obs = obligations(k) if obs is None else obs
    got = {ob["id"]: 0.0 for ob in obs}
    byid = {ob["id"]: ob for ob in obs}
    states = {law["id"]: law["state"] for law in laws(k)}

    def due(ob):
        if ob["kind"] == "duty":
            return 0.0
        if ob.get("per"):
            if ob.get("per_harvest"):
                base = float(((states.get(ob["lid"]) or {}).get("took") or {}).get(ob["key"], {}).get(ob["per"], 0.0))
            else:
                base = got.get(f"{ob['lid']}|{ob['key']}|{ob['per']}", 0.0)
            return float(ob.get("overdue") or 0) + float(ob.get("unit") or 0) * base
        return float(ob.get("qty") or 0) + float(ob.get("overdue") or 0)

    def take(ob, pay):
        room = due(ob) - got[ob["id"]]
        q = min(room, pay["left"])
        if q > EPS:
            got[ob["id"]] += q
            pay["left"] -= q

    def fits(ob, pay):
        return ob["kind"] != "duty" and pay["item"] == ob["item"] and pay["dst"] == ob["dst"]

    pays = payments(k)
    for pay in pays:
        ob = byid.get(pay["tag"]) if pay["tag"] else None
        if ob is not None and fits(ob, pay):
            take(ob, pay)
    for per in (False, True):
        for loose in (False, True):
            for pay in pays:
                if pay["left"] <= EPS:
                    continue
                for ob in obs:
                    if bool(ob.get("per")) == per and fits(ob, pay) and _src_ok(k, ob, pay, loose):
                        take(ob, pay)
                        if pay["left"] <= EPS:
                            break
    return {i: [due(byid[i]), got[i]] for i in got}


def open_for(k, aid) -> list:
    """The obligations aid meets (as the obligor, or as an officer paying for its institution), each with "due" and "paid"."""
    obs = obligations(k)
    led = ledger(k, obs)
    out = []
    for ob in obs:
        if aid in payers_of(k, ob["src"]):
            ob["due_now"], ob["paid"] = led[ob["id"]]
            out.append(ob)
    return out


# ---------------------------------------------------------------------- holdings at the payer's turns (engine 19)
# A manual leg is met by acting, so a miss is judged on what the payer held when it could act: at the end of each of its turns
# this round (contracts.miss_judged turn). Holdings change after a turn by harvests and production resolved at the round's end
# (camps.end_of_round runs before the laws' on_round_end), by other agents' transfers on later turns, and by laws' hooks; none of
# that could have been delivered. Under simultaneous turns every agent decided from the view before the first action ran, so what
# others gave it between then and the end of its turn is taken off too (its own actions in the turn, a harvest, count). k.w
# "turn_held" = {"round": r, "simultaneous": bool, "start": {aid: holdings}, "begin": {aid: holdings}, "agents": {aid: {"turns":
# [position], "held": {item: max}, "at": {item: position}}}}; written only with the setting on and contracts present.
def at_turn(k) -> bool:
    return "contracts" in k.w and cfg(k).get("miss_judged") == "turn"


def turns_begin(k, simultaneous: bool) -> None:
    """The round's turns start (runner, before any decision): a fresh record; the decision view for simultaneous turns."""
    if not at_turn(k):
        return
    start = {aid: dict(a["holdings"]) for aid, a in sorted(k.w["agents"].items())} if simultaneous else {}
    k.w["turn_held"] = {"round": k.r, "simultaneous": bool(simultaneous), "start": start, "begin": {}, "agents": {}}


def _record(k):
    th = k.w.get("turn_held")
    return th if at_turn(k) and th and th.get("round") == k.r else None


def turn_begin(k, aid) -> None:
    th = _record(k)
    a = k.w["agents"].get(aid)
    if th is not None and a is not None:
        th["begin"][aid] = dict(a["holdings"])


def turn_end(k, aid, pos) -> None:
    """After aid's turn: the most it held of each item at the end of a turn this round (less, under simultaneous turns, what
    others gave it since the decisions), and the turn (round position) it held that at."""
    th = _record(k)
    a = k.w["agents"].get(aid)
    if th is None or a is None:
        return
    end = a["holdings"]
    rec = th["agents"].setdefault(aid, {"turns": [], "held": {}, "at": {}})
    rec["turns"].append(pos)
    b, s = th["begin"].pop(aid, {}), th["start"].get(aid)
    for item in sorted(set(end) | set(rec["held"])):
        q = float(end.get(item, 0.0))
        if s is not None:                                              # simultaneous: others' gifts before its turn ran
            q -= max(0.0, float(b.get(item, 0.0)) - float(s.get(item, 0.0)))
        q = round(max(0.0, q), 6)
        if item not in rec["held"] or q > rec["held"][item] + EPS:
            rec["held"][item], rec["at"][item] = q, pos


def held_at_turn(k, aid, item):
    """(most held at the end of a turn this round, its position or None) for an agent, or None when not judged at turns (setting
    off, or no turns were played this round: a law driven without the runner)."""
    th = _record(k)
    if th is None:
        return None
    rec = th["agents"].get(aid) or {}
    return float((rec.get("held") or {}).get(item, 0.0)), (rec.get("at") or {}).get(item, (rec.get("turns") or [None])[-1])


# ---------------------------------------------------------------------- round end
def settle(k) -> None:
    """Before the laws' on_round_end: each manual law's state["paid"] = what this round's payments credited, per binding and leg;
    with contracts.miss_judged turn, also state["turn_held"] = what each agent payer held at its turns ({key: {leg: {held, turn}}})."""
    if "contracts" not in k.w:
        return
    obs = obligations(k)
    if not obs:
        return
    led = ledger(k, obs)
    paid, held = {}, {}
    judged = _record(k) is not None
    for ob in obs:
        q = led[ob["id"]][1]
        if q > EPS:
            paid.setdefault(ob["lid"], {}).setdefault(ob["key"], {})[ob["leg"]] = round(q, 6)
        h = held_at_turn(k, ob["src"], ob["item"]) if judged and ob["kind"] != "duty" and ob["src"] in k.w["agents"] else None
        if h is not None:
            held.setdefault(ob["lid"], {}).setdefault(ob["key"], {})[ob["leg"]] = {"held": round(h[0], 6), "turn": h[1]}
    for law in laws(k):
        law["state"]["paid"] = paid.get(law["id"], {})
        if judged:
            law["state"]["turn_held"] = held.get(law["id"], {})


def _escalation(c, rec, src_agent, polity) -> str:
    grace = int(c.get("GRACE", 1) or 0)
    if rec.get("breached"):
        pen = c.get("PENALTY") or {}
        forum = str(c.get("FORUM") or "escrow")
        if forum.startswith("arbiter:"):
            return f"That is a breach: a claim goes to the arbiter {forum[8:]}."
        what = f"{_fmt(pen.get('qty', 0))} {pen.get('item', '')} from your bond" if pen.get("item") and pen.get("qty") else "no penalty set"
        tail = {"drop": " and your terms end", "expel": " and you are expelled"}.get(str(c.get("ON_BREACH") or ""), "")
        return f"That is a breach: penalty {what}{tail}."
    if not src_agent:
        return "It stays owed (arrears) until paid."
    turn = "held_turn" in rec                                           # engine 19: judged on what it held at its turns
    if rec.get("why") == "could":
        return ("You lacked it at your turn" if turn else "You lacked it") + " (a could-not miss): no penalty, but it stays overdue."
    if polity:
        return "It stays overdue" + (" and you are fined" if c.get("FINE") else "") + "."
    if rec.get("misses"):
        n = grace + 1 - int(rec["misses"])
        pen = c.get("PENALTY") or {}
        what = f"a penalty of {_fmt(pen['qty'])} {pen['item']} from your bond" if pen.get("item") and pen.get("qty") else "a breach"
        head = "" if rec.get("duty") else ("You held it at your turn and did not act: " if turn else "You held it and did not act: ")
        return f"{head}{what[0].upper() if not head else what[0]}{what[1:]} after {n} more miss{'es' if n != 1 else ''} like this."
    return "It stays overdue."


def notices(k) -> None:
    """After the laws' on_round_end: an unmet manual obligation notifies the counterparty and the defaulter (one message each per
    contract a round; the defaulter's lists each leg once, with what was missed, the consequence and the exact fulfil)."""
    if "contracts" not in k.w:
        return
    from cybertron import jurisdictions as J
    for law in laws(k):
        st = law["state"]
        c = consts(law)
        label = str(c.get("LABEL") or law.get("title") or law["id"])
        iid = J.law_jur(k, law["id"])
        polity = J.association(k, iid) is None
        to_cp, to_df = {}, {}
        for key, legs in sorted((st.get("last") or {}).items()):
            for leg, rec in sorted(legs.items()):
                if rec.get("r") != k.r or float(rec.get("late") or 0) <= EPS:
                    continue
                src, dst, item = rec.get("src"), rec.get("dst"), rec.get("item")
                verb = "pay" if _money(k, item) else "deliver"
                who = party_name(k, src)
                ov = float(rec.get("overdue") or 0)
                if rec.get("duty"):
                    cp = f"{who} did not perform its {item} for {shown(k, norm(k, dst))} this round ({label}, {iid}, leg {leg})."
                else:
                    cp = (f"{who} did not {verb} {_fmt(rec['late'])} {item} to {shown(k, norm(k, dst))} this round ({label}, {iid}, "
                          f"leg {leg}); {_fmt(ov)} overdue.")
                for a in ([dst] if dst in k.w["agents"] else payers_of(k, norm(k, dst))):
                    to_cp.setdefault(a, []).append(cp)
                then = _escalation(c, rec, src in k.w["agents"], polity)
                what = f"your {item} for {shown(k, norm(k, dst))}" if rec.get("duty") else \
                    f"{_fmt(rec['late'])} {item} to {shown(k, norm(k, dst))}"
                head = f"You missed {label} ({iid}) leg {leg}" + ("" if src in k.w["agents"] else f" for {who}")
                for a in payers_of(k, norm(k, src)):
                    g = to_df.setdefault(a, {}).setdefault((head, then, leg, bool(rec.get("duty"))), [[], 0.0])
                    g[0].append(what)
                    g[1] += ov
        for a, xs in sorted(to_cp.items()):
            if a in k.w["agents"]:
                k.notify(a, " ".join(xs[:4]) + (f" (and {len(xs) - 4} more)" if len(xs) > 4 else ""), by=f"law:{law['id']}")
        for a, gs in sorted(to_df.items()):
            if a not in k.w["agents"]:
                continue
            out = []
            for (head, then, leg, duty), (whats, ov) in gs.items():
                t = head + ": " + ", ".join(whats[:5]) + (f" and {len(whats) - 5} more" if len(whats) > 5 else "")
                t += ("." if duty else f"; {_fmt(ov)} overdue.") + " " + then
                if not duty:
                    t += f" Meet it with fulfil {{\"contract\": \"{iid}\", \"leg\": \"{leg}\"}}."
                out.append(t)
            k.notify(a, " ".join(out[:3]) + (f" (and {len(out) - 3} more)" if len(out) > 3 else ""), by=f"law:{law['id']}")


def end_round(k) -> None:
    notices(k)
    petition_notices(k)


# ---------------------------------------------------------------------- fulfil
def _err(msg):
    from cybertron.actions import ActionError
    return ActionError(msg)


def _pick(k, aid, contract, leg, member):
    obs = open_for(k, aid)
    if not obs:
        raise _err("nothing is due from you this round (no manual contract leg names you or an institution you pay for)")
    if contract not in (None, ""):
        c = str(contract).strip().lstrip("@")
        sel = [ob for ob in obs if c in (ob["iid"], ob["lid"]) or c.lower() == ob["label"].lower()]
        if not sel:
            raise _err(f"nothing is due from you in {c}; due: " + ", ".join(sorted({f'{ob["iid"]} ({ob["label"]})' for ob in obs})))
        obs = sel
    if leg not in (None, ""):
        legs = []
        for ob in obs:
            if ob["leg"] not in legs:
                legs.append(ob["leg"])
        want = str(leg).strip()
        if want not in legs and want.isdigit() and 1 <= int(want) <= len(legs):
            want = legs[int(want) - 1]
        sel = [ob for ob in obs if ob["leg"] == want]
        if not sel:
            raise _err(f"no leg {leg} is due from you here; legs due: {', '.join(legs)}")
        obs = sel
    if member not in (None, ""):
        m = str(member)
        sel = [ob for ob in obs if m in (ob["key"], ob["dst"], ob["to"])]
        if not sel:
            raise _err(f"nothing here is due to or for {m}")
        obs = sel
    return obs


def _pay(k, aid, ob, q) -> str:
    """One payment toward ob, by the ordinary transfer paths (laws' hooks and taxes apply), tagged with the obligation."""
    from cybertron import actions as A
    from cybertron import institutions as IN
    from cybertron import subsistence as SB
    extra = {"fulfil": ob["id"]}
    src, dst, item = ob["src"], ob["dst"], ob["item"]
    dst_inst, dst_res = _inst(k, dst)
    if src in k.w["agents"]:
        if dst in k.w["agents"]:
            return A._send(k, aid, dst, item, q, extra=extra)
        if str(dst).startswith("store:"):
            return SB.deposit(k, aid, dst, item, q, extra=extra)
        if dst_inst is not None:
            return A.pay_institution(k, aid, dst_inst, item, q, extra=extra)
        raise _err(f"cannot pay {dst}")
    iid, res = _inst(k, src)
    if iid is None:
        raise _err(f"cannot pay out of {src}")
    if res == "treasury":
        to = dst if (dst in k.w["agents"] or str(dst).startswith("store:")) else dst_inst
        return IN.pay_as(k, aid, iid, to, item, q, extra=extra)
    out = SB.act_withdraw(k, aid, res[6:], q)                           # a store: its own code decides who takes food out
    if dst in k.w["agents"]:
        if dst == aid:
            k.log("transfer", aid, {"to": aid, "item": item, "qty": q, "tax": 0.0, **extra}, vis=[aid])
            return out
        return out + " " + A._send(k, aid, dst, item, q, extra=extra)
    if str(dst).startswith("store:"):
        return out + " " + SB.deposit(k, aid, dst, item, q, extra=extra)
    return out + " " + A.pay_institution(k, aid, dst_inst, item, q, extra=extra)


def act_fulfil(k, aid, contract=None, leg=None, member=None, **kw):
    """fulfil {"contract": "A1", "leg": "D"}: pay or deliver what your manual contract legs ask this round (and anything overdue),
    from your holdings, or out of an institution's treasury or store you pay for as its officer. Without leg: every leg due from you
    in that contract; without contract: everything due from you."""
    for alias in ("to", "agent", "worker", "member_id"):
        if alias in kw:
            v = kw.pop(alias)
            member = v if member is None else member
    for extra in ("qty", "item", "note", "memo", "amount"):              # what is due is computed: given amounts are ignored
        kw.pop(extra, None)
    if kw:
        raise TypeError(f"act_fulfil() got unexpected arguments: {sorted(kw)}")
    obs = _pick(k, aid, contract, leg, member)
    led = ledger(k, obligations(k))
    done, short, duty = [], [], []
    for ob in obs:
        if ob["kind"] == "duty":
            duty.append(f"{ob['leg']} ({ob['check']}: done by acting)")
            continue
        due, paid = led.get(ob["id"], [0.0, 0.0])
        rem = due - paid
        if rem <= EPS:
            continue
        src = ob["src"]
        if src in k.w["agents"]:
            have = k.bal(src, ob["item"]) - float(ob.get("keep") or 0)
        else:
            from cybertron import accounts as AC
            have = AC.bal(k, src, ob["item"])
        q = round(min(rem, max(0.0, have)), 6)
        if q <= EPS:
            short.append(f"{ob['leg']} to {ob['to']}: {_fmt(rem)} {ob['item']} due, " + (f"you hold {_fmt(max(0.0, k.bal(src, ob['item'])))} "
                         f"(keep {_fmt(ob.get('keep') or 0)})" if src in k.w["agents"] else f"{shown(k, src)} holds {_fmt(max(0.0, have))}"))
            continue
        try:
            _pay(k, aid, ob, q)
        except Exception as e:                                          # noqa: BLE001 (an ActionError, a block, a refusal)
            short.append(f"{ob['leg']} to {ob['to']}: {e}")
            continue
        done.append(f"{ob['leg']} {_fmt(q)} {ob['item']} to {shown(k, ob['dst'])}" + (f" ({_fmt(rem - q)} still due)" if rem - q > EPS else ""))
        led = ledger(k, obligations(k))
    if not done and not short and not duty:
        return "Nothing left to pay: what is due here this round is met."
    if not done and short:
        raise _err("could not fulfil: " + "; ".join(short))
    return ("Fulfilled: " + "; ".join(done) if done else "Nothing paid") + (". Not met: " + "; ".join(short) if short else "") \
        + (". Duties: " + "; ".join(duty) if duty else "") + "."


# ---------------------------------------------------------------------- state lines
def _call(ob) -> str:
    return f"fulfil {{\"contract\": \"{ob['iid']}\", \"leg\": \"{ob['leg']}\"}}"


def _late(k, ob) -> float:
    """What of an obligation's carried amount is truly late (arrears). A fixed leg's overdue is late. A leg paid per unit of another
    may wait to the end of the next round, so its overdue at the start of a round is mostly the last round's deliveries, payable by
    the end of this round: only what was already late at the end of the last round (its record's "late") is in arrears."""
    ov = float(ob.get("overdue") or 0)
    if ov <= EPS or not ob.get("per"):
        return ov
    law = k.w["laws"].get(ob.get("lid")) or {}
    rec = (((law.get("state") or {}).get("last") or {}).get(ob.get("key")) or {}).get(ob.get("leg"))
    if not rec or rec.get("r") != k.r - 1:
        return ov
    return min(ov, max(0.0, float(rec.get("late") or 0)))


def _split(k, ob) -> tuple:
    """(due by the end of this round, of it in arrears, payable by the end of next round) still open on an obligation whose
    "due_now" and "paid" are set: a payment meets the oldest part first."""
    rem = max(0.0, float(ob["due_now"]) - float(ob["paid"]))
    if not ob.get("per"):
        return rem, max(0.0, min(rem, float(ob.get("overdue") or 0) - float(ob["paid"]))), 0.0
    ov = float(ob.get("overdue") or 0)
    carried = max(0.0, ov - float(ob["paid"]))
    late = max(0.0, _late(k, ob) - float(ob["paid"]))
    return min(rem, carried), min(late, carried), max(0.0, rem - carried)


def due_lines(k, aid) -> list:
    """OBLIGATIONS: what is due from the agent (or an institution it pays for) this round, to whom, the exact action, overdue, last
    round's misses; and what is owed to it."""
    if "contracts" not in k.w:
        return []
    obs = obligations(k)
    if not obs:
        return []
    led = ledger(k, obs)
    mine, owed = {}, []
    compact = bool(cfg(k).get("compact_lines"))                        # engine 20: laws with the same label and leg summed
    owed_sum = {}
    for ob in obs:
        due, paid = led[ob["id"]]
        ob["due_now"], ob["paid"] = due, paid
        if aid in payers_of(k, ob["src"]):
            mine.setdefault((ob["iid"], ob["label"], ob["leg"], None if compact else ob["lid"]), []).append(ob)
        elif ob["dst"] == aid and ob["kind"] != "duty" and due - paid > EPS:
            if compact:
                g = (party_name(k, ob["src"]), ob["iid"], ob["leg"], ob["item"])
                owed_sum[g] = owed_sum.get(g, 0.0) + due - paid
            else:
                owed.append(f"{_fmt(due - paid)} {ob['item']} from {party_name(k, ob['src'])} ({ob['iid']} {ob['leg']})")
    for (src, iid, leg, item), q in owed_sum.items():
        owed.append(f"{_fmt(q)} {item} from {src} ({iid} {leg})")
    parts = []
    for (iid, label, leg, lid), xs in mine.items():
        if compact and len({x["lid"] for x in xs}) > 1:                # one row per destination, summed over the laws
            by = {}
            for x in xs:
                y = by.setdefault((x["dst"], x["src"], x["item"]), dict(x, due_now=0.0, paid=0.0, overdue=0.0))
                y["due_now"] += x["due_now"]
                y["paid"] += x["paid"]
                y["overdue"] = float(y.get("overdue") or 0) + float(x.get("overdue") or 0)
            n = len({x["lid"] for x in xs})
            label = f"{label} ({n} laws)"
            xs = list(by.values())
        if xs[0]["kind"] == "duty":
            if any(x.get("on") for x in xs):
                parts.append(f"{iid} {label} {leg}: {xs[0]['check']} duty to {shown(k, xs[0]['dst'])} this round (done by acting)")
            continue
        rem = [x for x in xs if x["due_now"] - x["paid"] > EPS]
        if not rem:
            if any(x["paid"] > EPS for x in xs):
                parts.append(f"{iid} {label} {leg}: met this round")
            continue
        item = xs[0]["item"]
        tot = sum(x["due_now"] - x["paid"] for x in rem)
        ov = sum(_split(k, x)[1] for x in rem)
        if len(rem) == 1:
            to = shown(k, rem[0]["dst"])
        else:
            to = ", ".join(f"{_fmt(x['due_now'] - x['paid'])} to {shown(k, x['dst'])}" for x in rem[:6]) + (" ..." if len(rem) > 6 else "")
        src = xs[0]["src"]
        frm = "" if src == aid else f" out of {shown(k, src)}"
        acc = ""
        if xs[0].get("per"):
            fresh = sum(_split(k, x)[2] for x in rem)
            if fresh > EPS:
                acc = f" ({_fmt(fresh)} for {xs[0]['per']} this round is payable by the end of next round)"
        parts.append(f"{iid} {label} {leg}: {_fmt(tot)} {item} {'to ' + to if len(rem) == 1 else '(' + to + ')'}{frm}"
                     + (f", of which {_fmt(ov)} overdue" if ov > EPS else "") + acc + f" -> {_call(xs[0])}")
    from cybertron import jurisdictions as J
    groups = {}                                                         # (label, leg, consequence) -> ["1 food to Bo", ...]
    for law in laws(k):
        c = consts(law)
        polity = J.association(k, J.law_jur(k, law["id"])) is None
        for key, legs in sorted((law["state"].get("last") or {}).items()):
            for leg, rec in sorted(legs.items()):
                if rec.get("r") == k.r - 1 and float(rec.get("late") or 0) > EPS and aid in payers_of(k, norm(k, rec.get("src"))):
                    then = _escalation(c, rec, rec.get("src") in k.w["agents"], polity).rstrip(".")
                    g = (str(c.get("LABEL") or law.get("title")), leg, then[0].lower() + then[1:])
                    what = f"{rec['item']}" if rec.get("duty") else f"{_fmt(rec['late'])} {rec['item']}"
                    groups.setdefault(g, []).append(f"{what} to {shown(k, norm(k, rec['dst']))}")
    missed = [f"{label} {leg}: " + ", ".join(xs[:5]) + (" ..." if len(xs) > 5 else "") + f" ({then})"
              for (label, leg, then), xs in groups.items()]
    out = []
    if parts or missed:
        line = ("OBLIGATIONS: nothing moves unless you act. Due this round: " + ("; ".join(parts) if parts else "nothing") + "."
                + (" Missed last round: " + "; ".join(missed[:4]) + "." if missed else ""))
        out.append(line)
    if owed:
        out.append("OWED TO YOU this round: " + "; ".join(owed[:6]) + (" ..." if len(owed) > 6 else "") + ".")
    return out


def situation_line(k, aid) -> str | None:
    """One short line for the closing block: how many obligations are open."""
    if "contracts" not in k.w:
        return None
    obs = [ob for ob in open_for(k, aid) if ob["kind"] != "duty" and ob["due_now"] - ob["paid"] > EPS]
    if not obs:
        return None
    calls = []
    for ob in obs:
        c = _call(ob)
        if c not in calls:
            calls.append(c)
    return f"Obligations still due this round: {len(obs)} (" + "; ".join(calls[:3]) + ")."


# ---------------------------------------------------------------------- petitions
def petitions(k, iid, window=None) -> list:
    """Messages to iid's inbox from non-officers that no officer has answered since (a message to the petitioner): [{id, by, round,
    text}], oldest first."""
    from cybertron import institutions as IN
    inbox = "@" + str(iid)
    offs = set(IN.officers(k, iid))
    if not offs or not any(ch == inbox for ch in (k.w.get("channels") or {})):
        return []
    lo = k.r - (window if window is not None else max(6, petition_after(k) + 3))
    evs = []
    for e in reversed(k.events):
        if e.get("round", 0) < lo:
            break
        evs.append(e)
    evs.reverse()
    pending = {}
    for e in evs:
        d = e.get("data") or {}
        if e["type"] == "channel_post" and d.get("channel") == inbox and e["agent"] and e["agent"] not in offs:
            pending[e["id"]] = {"id": e["id"], "by": e["agent"], "round": e["round"], "text": str(d.get("text") or "")}
        elif e["agent"] in offs and e["type"] in ("dm", "channel_post") and d.get("to"):
            for pid in [p for p, x in pending.items() if x["by"] == d["to"]]:
                pending.pop(pid)
    return sorted(pending.values(), key=lambda x: int(x["id"][1:]))


def petition_notices(k) -> None:
    """Round end: a petition unanswered for institutions.petition_public_after rounds gets one public notice naming the office."""
    n = petition_after(k)
    if not n:
        return
    from cybertron import institutions as IN
    from cybertron import channels as CH
    if not CH.active(k):
        return
    done = set(k.w.get("petitions_public") or ())
    for cid, ch in sorted((k.w.get("channels") or {}).items()):
        if not (isinstance(cid, str) and cid.startswith("@")) or cid[1:] in k.w["agents"]:
            continue
        iid = cid[1:]
        for p in petitions(k, iid, window=n + 3):
            if p["id"] in done or k.r - p["round"] + 1 < n:
                continue
            offs = IN.officers(k, iid)
            titles = [f"{(IN.office(k, iid, o) or {}).get('title') or o} ({', '.join(IN.holders(k, iid, o)) or 'vacant'})"
                      for o in IN.offices(k, iid)]
            rec = IN.get(k, iid) or {}
            name = f"{rec['name']} ({iid})" if rec.get("name") else iid
            text = (f"Public notice: {p['by']}'s petition to {name} of round {p['round'] + 1} has had no answer for {k.r - p['round'] + 1} "
                    f"rounds. Its offices: {'; '.join(titles) or ', '.join(offs)}. The petition: \"{p['text'][:160]}\"")
            k.log("petition_unanswered", None, {"institution": iid, "petition": p["id"], "by": p["by"], "officers": list(offs),
                                                "rounds": k.r - p["round"] + 1, "text": text}, vis="public")
            k.w.setdefault("petitions_public", []).append(p["id"])
            done.add(p["id"])


def petition_lines(k, aid) -> list:
    """PETITIONS: for an officer, the unanswered petitions to each institution it holds office in (petition_public_after set)."""
    if not petition_after(k):
        return []
    from cybertron import institutions as IN
    out = []
    for iid in sorted({i for i, _ in IN.offices_held(k, aid)}):
        ps = petitions(k, iid)
        if ps:
            n = petition_after(k)
            out.append(f"PETITIONS to {iid} waiting for an answer ({len(ps)}): "
                       + "; ".join(f"{p['by']} (round {p['round'] + 1}, {p['id']}): \"{p['text'][:80]}\"" for p in ps[:4])
                       + f". Answer with send {{\"to\": \"<petitioner>\", \"text\": \"...\"}}; unanswered after {n} rounds a public "
                       f"notice names the office.")
    return out


# ---------------------------------------------------------------------- role cards
CARD_BUDGET = 1800                                                      # characters for the whole ROLE block (the essentials first)
ACTION_ARGS = {"enrol": '["<agent>", <{term}>]', "drop": '["<agent>", <severance>]', "set": '["<agent> or all", <{term}>]',
               "post": '["<job text>", <wage>]', "assign": '["<agent> or all", "<{term}>"]'}
ACTION_WHAT = {"enrol": "take on", "drop": "remove", "set": "set {term}", "post": "post a job", "assign": "assign the {term}"}


def _standing_laws(k, iid) -> list:
    from cybertron import jurisdictions as J
    out = []
    for lid in k.w.get("law_order") or ():
        law = k.w["laws"].get(lid)
        if law and law.get("status") == "active" and J.law_jur(k, lid) == iid and "LEGS" in consts(law) and "TAG" in consts(law):
            out.append(law)
    return out


def _office_decisions(k, aid, iid, law) -> list:
    from cybertron import institutions as IN
    c = consts(law)
    office = str(c.get("OFFICE") or "")
    if not office:
        return []
    short = office.split(".")[-1]
    if aid not in IN.holders(k, iid, short):
        return []
    out = []
    term = {"enrol": c.get("ENROL_TERM") or "value", "set": c.get("SET_TERM") or "value",
            "assign": (list(c.get("AGENT_TERMS") or ()) or ["agent"])[0]}
    label = str(c.get("LABEL") or law.get("title") or law["id"])
    for verb in ("set", "enrol", "drop", "post", "assign"):
        name = (c.get("ACTIONS") or {}).get(verb)
        if name:
            args = ACTION_ARGS[verb].format(term=term.get(verb, "value"))
            what = ACTION_WHAT[verb].format(term=term.get(verb, "value"))
            out.append(f"{what} ({label}): invoke {{\"action\": \"{iid}.{name}\", \"args\": {args}}}")
    return out


def _office_generic(k, aid, iid, offs) -> list:
    """An office's decisions from what it holds: open ballots it votes in, the stores and treasury it controls, proposing laws (the
    propose right), its institution's inbox."""
    out = []
    bal = [b for b in (k.w.get("ballots") or {}).values() if b.get("status") == "open" and aid in (b.get("electorate") or ())
           and aid not in (b.get("votes") or {})]
    if bal:
        out.append(f"vote on {', '.join(b['id'] for b in bal[:3])}: vote {{\"ballot\": \"{bal[0]['id']}\", \"choice\": \"yes\"}}")
    ctl = []
    for o in offs:
        for c in o.get("controls") or ():
            if c not in ctl:
                ctl.append(c)
    for c in ctl:
        if str(c).startswith("store:"):
            out.append(f"draw food from store {c[6:]}: withdraw {{\"store\": \"{c[6:]}\", \"qty\": <n>}}, then give it: transfer "
                       f"{{\"to\": \"<agent>\", \"item\": \"food\", \"qty\": <n>}}")
        elif c == "treasury":
            out.append(f"pay out of {iid}'s treasury: transfer {{\"to\": \"<agent>\", \"item\": \"<item>\", \"qty\": <n>, "
                       f"\"as\": \"{iid}\"}}")
    if "propose" in (k.w["agents"].get(aid, {}).get("rights") or ()):
        out.append('propose a law: propose {"code": "<law source>", "intent": "..."}')
    inbox = "@" + str(iid)
    ch = (k.w.get("channels") or {}).get(inbox)
    if ch is not None and _readable(k, aid, ch):
        out.append(f"read what is sent to {iid}: read {{\"channel\": \"{inbox}\"}}")
    if not out:
        out.append(f"speak for {iid} or pay from it: transfer {{\"to\", \"item\", \"qty\", \"as\": \"{iid}\"}}")
    return out


def _readable(k, aid, ch) -> bool:
    from cybertron import channels as CH
    try:
        return bool(CH.can_read(k, aid, ch))
    except Exception:                                                   # noqa: BLE001 (channels off or an old record)
        return False


def _treasury_text(k, iid) -> str:
    from cybertron import accounts as AC
    try:
        h = AC.holdings(k, AC.treasury_of(k, iid))
    except Exception:                                                   # noqa: BLE001
        return ""
    return ", ".join(f"{_fmt(q)} {i}" for i, q in sorted(h.items()) if q > EPS) or "empty"


def _stores_text(k, iid) -> str:
    from cybertron import accounts as AC
    xs = [f"store {sid} {_fmt(s['holdings'].get('food', 0))}/{_fmt(s['capacity'])} food" for sid, s in sorted(AC.stores(k).items())
          if s["owner"] == iid]
    return ", ".join(xs)


def _purpose(text) -> str:
    """The first sentence of an office's duties, as a purpose line."""
    t = " ".join(str(text or "").split())
    if not t:
        return ""
    head = t.split(". ", 1)[0]
    if len(head) > 160:
        head = head[:160].rsplit(" ", 1)[0].rstrip(" ,;:") + "..."
    return head.rstrip(".") + "."


def _who(k, ref) -> str:
    """An electorate or office reference in words: "J0.council" -> "Councillor of J0 (Ada, Bram, Cora)"; "vote" -> "holders of vote"."""
    from cybertron import institutions as IN
    ref = str(ref or "")
    if "." in ref:
        iid, name = ref.split(".", 1)
        o = IN.office(k, iid, name)
        if o is not None:
            hs = IN.holders(k, iid, name)
            return f"{o.get('title') or name} of {iid} ({', '.join(hs) or 'vacant'})"
    return f"holders of {ref}"


def _answers_to(k, aid, iid, o) -> str:
    from cybertron import accounts as AC
    from cybertron import jurisdictions as J
    cl = o.get("succession") or {}
    if cl.get("electorate"):
        return f"answers to {_who(k, cl['electorate'])}, who fill the office by {cl.get('rule') or 'election'}"
    rec = AC.assocs(k).get(iid) if "contracts" in k.w else None
    if rec:
        if rec.get("founder") and rec["founder"] != aid:
            return f"answers to its founder {rec['founder']}"
        return f"answers to its members ({len(rec.get('members') or ())})"
    return "answers to the polity's law" if J.association(k, iid) is None else ""


def _parties_of(k, iid, short) -> list:
    """(role, [agents]) of the standing contracts of iid whose OFFICE is this office: who answers to its holder."""
    out = []
    for law in _standing_laws(k, iid):
        c = consts(law)
        if str(c.get("OFFICE") or "").split(".")[-1] != short:
            continue
        who = sorted(a for a in ((law.get("state") or {}).get("terms_lines") or {}) if a in k.w["agents"])
        if who:
            out.append((f"{str(c.get('ROLE') or 'party')}s ({str(c.get('LABEL') or law.get('title') or law['id'])})", who))
    return out


def _sums(k, obs, led) -> str:
    """What a set of obligations still asks this round, per item: "2 food, 3 penny"."""
    tot = {}
    for ob in obs:
        q = max(0.0, led[ob["id"]][0] - led[ob["id"]][1])
        if q > EPS:
            tot[ob["item"]] = tot.get(ob["item"], 0.0) + q
    return ", ".join(f"{_fmt(q)} {i}" for i, q in sorted(tot.items()))


def _pay_text(k, obs, every=None) -> str:
    """What the agent gets from these legs: "1.5 penny per food of leg D (A1 P)", "2 penny a round (A1 W)"."""
    xs = []
    every = obs if every is None else every
    for ob in obs:
        if ob["kind"] == "duty":
            continue
        if ob.get("per") and float(ob.get("unit") or 0) > EPS:
            base = next((x for x in every if x["lid"] == ob["lid"] and x["key"] == ob["key"] and x["leg"] == ob["per"]), None)
            what = base["item"] if base and base["kind"] != "duty" else "unit"
            t = f"{_fmt(ob['unit'])} {ob['item']} per {what} of leg {ob['per']} ({ob['iid']} {ob['leg']})"
        elif float(ob.get("qty") or 0) > EPS:
            t = f"{_fmt(ob['qty'])} {ob['item']} a round ({ob['iid']} {ob['leg']})"
        else:
            continue
        if t not in xs:
            xs.append(t)
    return "; ".join(xs[:3])


def _enrol_calls(k, aid, iid) -> list:
    """The enrol actions aid may call as an officer of iid ("A1.supply_enrol"): its standing contracts whose OFFICE it holds."""
    from cybertron import institutions as IN
    out = []
    for law in _standing_laws(k, iid):
        c = consts(law)
        name = (c.get("ACTIONS") or {}).get("enrol")
        office = str(c.get("OFFICE") or "").split(".")[-1]
        if name and office and aid in IN.holders(k, iid, office) and f"{iid}.{name}" not in out:
            out.append(f"{iid}.{name}")
    return out


def _unrostered(k, iid) -> list:
    """Members of association iid who are on no roster of its standing contracts (not enrolled, not a party) and hold none of its
    offices: who joined and was never taken on."""
    from cybertron import accounts as AC
    from cybertron import institutions as IN
    rec = AC.assocs(k).get(iid) if "contracts" in k.w else None
    if not rec:
        return []
    on = set(IN.officers(k, iid))
    for law in _standing_laws(k, iid):
        st = law.get("state") or {}
        on |= set(st.get("terms_lines") or {}) | set(st.get("roster") or {})
    return [m for m in rec.get("members") or () if m in k.w["agents"] and m not in on
            and k.w["agents"][m].get("departed") is None]


def _revoke_call(holder, right) -> str:
    code = (f'title = \\"Recall of {holder}\\"\\nintent = \\"{holder} no longer holds {right}\\"\\ndef on_enact():\\n'
            f'    revoke(\\"{holder}\\", \\"{right}\\")')
    return f'propose {{"code": "{code}"}}'


def _recall_route(k, aid, iid, o) -> str:
    """The office's accountability route with the action (review 31.09 #7): a law of iid revoking the office's right removes the
    holder (a removal: the office falls vacant and its succession rule refills it)."""
    from cybertron import jurisdictions as J
    right = str(o.get("id") or "")
    elected = bool((o.get("succession") or {}).get("electorate"))
    if "." not in right or not (elected or (J.association(k, iid) is None and o.get("controls"))):
        return ""                                                       # only offices others elect, or a polity's that control goods
    return f"Recall: a law of {iid} revoking {right} removes you (passed by {iid}'s procedure), e.g. {_revoke_call(aid, right)}"


def _oversees(k, iid, offs) -> str:
    """For an office that elects another office of iid (its succession electorate): who answers to it and the recall action."""
    from cybertron import institutions as IN
    mine = {str(o.get("id") or "") for o in offs}
    xs = []
    for name in IN.offices(k, iid):
        o = IN.office(k, iid, name) or {}
        cl = o.get("succession") or {}
        if str(cl.get("electorate") or "") in mine and str(o.get("id") or "") not in mine:
            hs = IN.holders(k, iid, name)
            call = _revoke_call(hs[0], o["id"]) if hs else ""
            xs.append(f"{o.get('title') or name} ({', '.join(hs) or 'vacant'}), elected by you"
                      + (f"; recall by a law: {call}" if call else ""))
    return ("Oversee: " + "; ".join(xs[:2])) if xs else ""


def _offer_text(k, aid, law, iid, rec) -> str:
    """An open standing contract (OPEN: a shop's Board) as an offer to an agent not on it: what it gives and costs, and how to
    take it up."""
    from cybertron import institutions as IN
    c = consts(law)
    d = dict(c.get("TERMS") or {})
    d.update((law.get("state") or {}).get("defaults") or {})

    def v(x):
        return d.get(x, x) if isinstance(x, str) else x

    def where(x):
        x = v(x)
        if x == "treasury":
            return f"{iid}'s treasury"
        if isinstance(x, str) and x.startswith("store:"):
            return f"store {x[6:]}"
        return str(x)
    legs = {l.get("id"): l for l in c.get("LEGS") or ()}
    gets, pays, allow = [], [], {}
    for l in c.get("LEGS") or ():
        if any(v(x) != y for x, y in (l.get("when") or {}).items()) or l.get("kind", "move") != "move":
            continue
        try:
            q = float(v(l.get("qty", 0)) or 0)
        except (TypeError, ValueError):
            continue
        item = v(l.get("item", ""))
        base = legs.get(l.get("per") or "")
        each = f" per {v(base.get('item', 'unit'))}" if base else " a round"
        if l.get("to") == "member":
            gets.append(f"{_fmt(q)} {item}{each} from {where(l.get('from'))}")
        elif l.get("from") == "member":
            pays.append(f"{_fmt(q)} {item}{each} to {where(l.get('to'))}")
            mult = float(v(base.get("qty", 1)) or 1) if base else 1.0
            allow[item] = allow.get(item, 0.0) + q * mult
    if not gets:
        return ""
    name = f"{rec['name']} ({iid})" if rec.get("name") and rec["name"] != iid else iid
    label = str(c.get("LABEL") or law.get("title") or law["id"])
    steps = []
    if aid not in (rec.get("members") or ()):
        steps.append(f"join_contract {{\"contract\": \"{iid}\"}}")
    if allow:                                                           # an association's legs take from a member's allowance
        steps += [f"set_allowance {{\"contract\": \"{iid}\", \"item\": \"{i}\", \"qty\": {_fmt(q)}}}" for i, q in allow.items()]
    if not steps:
        return ""
    return (f"OFFER: {label} of {name}: you get {'; '.join(gets)}" + (f"; you pay {'; '.join(pays)}" if pays else "")
            + f". To take it up: {', then '.join(steps)}.")


def offer_lines(k, aid) -> list:
    """OFFER: open standing contracts (a Board open to its members) the agent is not on, whose institution it may join (or is a
    member of): what they give and cost, and the exact steps to take them up (role cards on; at most two)."""
    from cybertron import accounts as AC
    from cybertron import institutions as IN
    from cybertron import jurisdictions as J
    out = []
    for lid in k.w.get("law_order") or ():
        law = k.w["laws"].get(lid)
        if not law or law.get("status") != "active":
            continue
        c = consts(law)
        if not c.get("OPEN") or "LEGS" not in c or c.get("PARTIES"):
            continue
        st = law.get("state") or {}
        iid = J.law_jur(k, lid)
        rec = AC.assocs(k).get(iid) if "contracts" in k.w else None
        if not rec or rec.get("status") == "dissolved" or st.get("ended") or aid in (st.get("terms_lines") or {}):
            continue
        if aid in IN.officers(k, iid) or (aid not in (rec.get("members") or ()) and rec.get("admission") == "closed"):
            continue
        t = _offer_text(k, aid, law, iid, rec)
        if t:
            out.append(t)
        if len(out) >= 2:
            break
    return out


def role_lines(k, aid) -> list:
    """ROLE: one card per office the agent holds and per standing contract it is a party to (framework §2): the purpose, whom it
    answers to and who answers to it, its pay and the contract it comes from, this round's numbers, and the 2-4 decisions it owns
    with exact syntax. Budgeted: past CARD_BUDGET characters the decisions are cut to two per card."""
    if not cards_on(k):
        return []
    from cybertron import contracts as KC
    from cybertron import institutions as IN
    from cybertron import jurisdictions as J
    obs = obligations(k)
    led = ledger(k, obs) if obs else {}
    cards = []
    held = {}
    for iid, o in IN.offices_held(k, aid):
        held.setdefault(iid, []).append(o)
    for iid, offs in sorted(held.items()):
        rec = IN.get(k, iid) or {}
        name = f"{rec['name']} ({iid})" if rec.get("name") else iid
        about = []
        purpose = " ".join(p for p in (_purpose(o.get("duties")) for o in offs) if p)
        if purpose:
            about.append("Purpose: " + purpose.rstrip("."))
        up = _answers_to(k, aid, iid, offs[0])
        if up:
            about.append(up[0].upper() + up[1:])
        rc = _recall_route(k, aid, iid, offs[0])
        if rc:
            about.append(rc)
        ov = _oversees(k, iid, offs)
        if ov:
            about.append(ov)
        down = []
        for o in offs:
            short = str(o.get("id") or "").split(".")[-1]
            down += [f"{r} {', '.join(w[:5])}" + (" ..." if len(w) > 5 else "") for r, w in _parties_of(k, iid, short)]
        if down:
            about.append("Answer to you: " + "; ".join(down))
        pay = _pay_text(k, [ob for ob in obs if ob["dst"] == aid], obs)
        if pay:
            about.append("You get: " + pay)
        nums = [f"treasury {_treasury_text(k, iid)}"]
        st = _stores_text(k, iid)
        if st:
            nums.append(st)
        owes = [ob for ob in obs if _inst(k, ob["src"])[0] == iid and ob["kind"] != "duty"]
        due = _sums(k, owes, led)
        now, arrears, later = {}, 0.0, {}
        for ob in owes:
            ob["due_now"], ob["paid"] = led[ob["id"]]
            d_, a_, l_ = _split(k, ob)
            now[ob["item"]] = now.get(ob["item"], 0.0) + d_
            later[ob["item"]] = later.get(ob["item"], 0.0) + l_
            arrears += a_
        now_t = ", ".join(f"{_fmt(q)} {i}" for i, q in sorted(now.items()) if q > EPS)
        later_t = ", ".join(f"{_fmt(q)} {i}" for i, q in sorted(later.items()) if q > EPS)
        if now_t:
            nums.append(f"it owes {now_t} this round" + (f" ({_fmt(arrears)} in arrears)" if arrears > EPS else ""))
        if later_t:
            nums.append(f"{later_t} for this round's deliveries payable by the end of next round")
        owed_in = _sums(k, [ob for ob in obs if _inst(k, ob["dst"])[0] == iid and ob["kind"] != "duty"], led)
        if owed_in:
            nums.append(f"owed to it {owed_in} this round")
        ac = (KC.recs(k).get(iid) or {}) if "contracts" in k.w else {}
        enrol = _enrol_calls(k, aid, iid)
        how = f" (take on: {' or '.join(enrol)})" if enrol else ""
        if ac.get("applicants"):
            nums.append(f"applicants {', '.join(ac['applicants'])}{how}")
        idle = _unrostered(k, iid) if enrol else []
        if idle:
            nums.append(f"members on no roster: {', '.join(idle[:6])}{' ...' if len(idle) > 6 else ''}{how}")
        ps = petitions(k, iid) if petition_after(k) else []
        if ps:
            nums.append(f"{len(ps)} petition(s) unanswered")
        dec = []
        if due:
            dec.append(f"pay what {iid} owes: fulfil {{\"contract\": \"{iid}\"}}")
        if ps:
            dec.append(f"answer {ps[0]['by']}'s petition: send {{\"to\": \"{ps[0]['by']}\", \"text\": \"...\"}}")
        for law in _standing_laws(k, iid):
            dec += _office_decisions(k, aid, iid, law)
        dec += _office_generic(k, aid, iid, offs)
        titles = "/".join(o["title"] for o in offs)
        cards.append([f"ROLE: {titles} of {name}. " + "".join(x + ". " for x in about) + "Now: " + "; ".join(nums) + ".", dec])
    for lid in k.w.get("law_order") or ():
        law = k.w["laws"].get(lid)
        if not law or law.get("status") != "active":
            continue
        st = law.get("state") or {}
        if aid not in (st.get("terms_lines") or {}):
            continue
        c = consts(law)
        iid = J.law_jur(k, lid)
        label = str(c.get("LABEL") or law.get("title") or lid)
        role = (c.get("PARTIES") or {}).get(aid) or c.get("ROLE") or "party"
        mine = [ob for ob in obs if ob["lid"] == lid and aid in payers_of(k, ob["src"]) and ob["kind"] != "duty"]
        toward = [ob for ob in obs if ob["lid"] == lid and ob["dst"] == aid]
        about = []
        office = str(c.get("OFFICE") or "")
        if office:
            short = office.split(".")[-1]
            o = IN.office(k, iid, short) or {}
            about.append(f"You answer to the {o.get('title') or short} of {iid} ({', '.join(IN.holders(k, iid, short)) or 'vacant'})")
        pay = _pay_text(k, toward, obs)
        if pay:
            about.append("You get: " + pay)
        nums = []
        d = _sums(k, mine, led)
        if d:
            nums.append(f"you owe {d} this round")
        o_ = _sums(k, toward, led)
        if o_:
            ov = sum(float(x.get("overdue") or 0) for x in toward)
            nums.append(f"owed to you {o_}" + (f" ({_fmt(ov)} overdue)" if ov > EPS else ""))
        book = (st.get("book") or {}).get(aid) or {}
        if book:
            kept = sum(v[0] for v in book.values())
            miss = sum(v[1] for v in book.values())
            nums.append(f"your record kept {kept}, missed {miss}")
        dec = []
        if d:
            dec.append(f"meet it: fulfil {{\"contract\": \"{iid}\"}}")
        if c.get("NOTICE", 0) or c.get("PARTIES"):
            dec.append(f"give notice: invoke {{\"action\": \"{iid}.{c.get('TAG', 'sc')}_notice\"}}")
        dec.append(f"raise terms with the office: send {{\"to\": \"{iid}\", \"text\": \"...\"}}")
        if J.association(k, iid) is not None:
            dec.append(f"leave: leave_contract {{\"contract\": \"{iid}\"}}")
        if not nums and not mine and not toward and len(dec) <= 1:          # nothing to do or to watch (an automatic leg's party)
            continue
        cards.append([f"ROLE: {role} in {label} ({iid}). " + "".join(x + ". " for x in about) + "Now: "
                      + ("; ".join(nums) if nums else "nothing open") + ".", dec])
    offers = offer_lines(k, aid)
    if not cards:
        return offers

    def render(n):
        return [head + " Decisions: " + "; ".join(dec[:n]) + "." for head, dec in cards]
    out = render(4)
    if sum(len(x) for x in out) > CARD_BUDGET:
        out = render(2)
    return out + offers


def state_lines(k, aid) -> list:
    """contracts.state_lines' head: obligations, petitions, role cards (each gated; [] when nothing applies)."""
    out = due_lines(k, aid)
    out += petition_lines(k, aid)
    out += role_lines(k, aid)
    return out


# ---------------------------------------------------------------------- scripted bots
def scripted_actions(k, a) -> list:
    """Dry runs: a bot meets what is due from it (one fulfil per contract), unless contracts.bot_obligations is neglect. No RNG."""
    if "contracts" not in k.w or cfg(k).get("bot_obligations") == "neglect" or not fulfil_on(k):
        return []
    aid = a["id"]
    try:
        obs = open_for(k, aid)
    except Exception:                                                   # noqa: BLE001
        return []
    out, seen = [], set()
    for ob in obs:
        if ob["kind"] == "duty" or ob["due_now"] - ob["paid"] <= EPS:
            continue
        src = ob["src"]
        if src in k.w["agents"]:
            if k.bal(src, ob["item"]) - float(ob.get("keep") or 0) <= EPS:
                continue
        else:
            from cybertron import accounts as AC
            if AC.bal(k, src, ob["item"]) <= EPS:
                continue
        if ob["iid"] in seen:
            continue
        seen.add(ob["iid"])
        out.append({"action": "fulfil", "args_json": json.dumps({"contract": ob["iid"]})})
    return out
