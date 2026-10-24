"""Offers and agreements (spec/economy/money_and_markets.md, agreements.md: D2-25 to D2-27, D2-31 to D2-40).

An offer is a proposed agreement: legs the offerer gives and legs it gets, to one person here or to anyone here, in lots. Accepting
it makes the agreement: legs due now are paid at once, both or neither; the rest (a promise by a day, payments every n days, days of
work) stay open and are paid at the end of each day's work wherever there is a way to pay (D2-32: payer and payee at one node),
else they fall into arrears, shown to both. Work legs are met by the action record: days on which the worker did work for the
payee (D2-36, D2-39). Semantics follow cybertron 1's standing contracts (D2-35), written natively: cybertron2 has no law language
yet (38.17 §9).

Leg: {from, to, item, qty, when: {"now"} | {"by": day} | {"every": n, "times": k, "next": day}, paid, arrears} or a work leg
{from, to, work: days, done, by: day?}.
"""
from __future__ import annotations

import re

from cybertron2.engine.data import ITEMS
from cybertron2.engine.here import Refused, show


# ---------------------------------------------------------------------- reading legs from what agents write
SEASONS = ("spring", "summer", "autumn", "winter")


def _season_days(text, day, cal):
    """'by autumn day 8' -> 'by day N' (the run's day of the next such date), as agents count by the season."""
    import re as _re
    if cal is None:
        return text

    def sub(m):
        season, d = m.group(1).lower(), int(m.group(2))
        for k in range(0, 4 * 60):
            c = cal(day + k)
            if c["season"] == season and c["day"] == d:
                return f"day {day + k + 1}"
        return m.group(0)
    return _re.sub(r"(spring|summer|autumn|winter)\s+day\s+(\d+)", sub, text, flags=_re.I)


def parse_legs(text, day, cal=None) -> list:
    """'2 meat, 1 copper tool by day 10' (or 'by autumn day 3') / '3 coin every 2 days for 4 times' / 'work 2 days' -> legs."""
    legs = []
    text = _season_days(str(text or ""), day, cal)
    for part in [x.strip() for x in text.replace(" and ", ",").split(",") if x.strip()]:
        low = part.lower()
        m = re.match(r"^(?:work|labour|labor)\s+(?:for\s+)?(\d+)\s+days?(?:\s+by\s+day\s+(\d+))?$", low)
        if m:
            legs.append({"work": int(m.group(1)), "done": 0, "by": int(m.group(2)) - 1 if m.group(2) else None})
            continue
        m = re.match(r"^([\d.]+)\s+(.+?)(?:\s+by\s+day\s+(\d+)|\s+every\s+(\d+)\s+days?(?:\s+for\s+(\d+)\s+times?)?)?$", low)
        if not m:
            raise Refused(f"could not read {part!r}: write goods as '2 bread', a promise as '1 copper tool by day 10', payments as "
                          f"'2 grain every 3 days for 4 times', work as 'work 2 days'")
        qty, item = float(m.group(1)), m.group(2).strip()
        from cybertron2.engine.verbs import item_of
        item = item_of(item)
        if m.group(3):
            when = {"by": int(m.group(3)) - 1}
        elif m.group(4):
            when = {"every": int(m.group(4)), "times": int(m.group(5) or 1), "next": day + int(m.group(4))}
        else:
            when = {"now": True}
        legs.append({"item": item, "qty": qty, "when": when, "paid": 0, "arrears": 0.0})
    return legs


def leg_text(leg, viewer=None, day=0, names=None) -> str:
    names = names or {}
    fr, to = names.get(leg["from"], leg["from"]), names.get(leg["to"], leg["to"])
    who = "you" if leg["from"] == viewer else fr
    whom = "you" if leg["to"] == viewer else to
    if "work" in leg:
        return f"{who} work{'s' if who != 'you' else ''} {leg['work']} days for {whom} ({leg['done']} done)" + \
            (f", by day {leg['by'] + 1}" if leg.get("by") is not None else "")
    w = leg["when"]
    head = f"{who} give{'s' if who != 'you' else ''} {leg['qty']:g} {leg['item']} to {whom}"
    if w.get("by") is not None:
        when = "paid" if leg["paid"] else f"by day {w['by'] + 1}" + (" (overdue)" if day > w["by"] else "")
    elif w.get("every"):
        when = f"every {w['every']} days, {leg['paid']} of {w['times']} paid" + (f", next on day {w['next'] + 1}" if leg["paid"] < w["times"] else "")
    else:
        when = "paid" if leg["paid"] else "now"
    arr = f"; {leg['arrears']:g} in arrears" if leg.get("arrears", 0) > 1e-9 else ""
    return f"{head}, {when}{arr}"


def _offer_goods(here, legs, party) -> str:
    """'' if the offerer has the goods due now, here (carried, or in stores it may take from, or its party's)."""
    from cybertron2.engine import knowledge as KN
    extra = here.party_container(party) if party else None
    for leg in legs:
        if "item" in leg and leg["when"].get("now") and KN.available(here, leg["item"], extra=extra) + 1e-9 < leg["qty"]:
            return f"you do not have {leg['qty']:g} {leg['item']} here"
    return ""


def make_offer(here, mind, o) -> str:
    """An offer from the talk step (D2-25, D2-26): {to, give, get, lots?, for?, until?}. Returns the result line."""
    from cybertron2.engine.verbs import _party
    to_raw = str(o.get("to") or "anyone").strip()
    to = None if to_raw.lower() in ("anyone", "all", "everyone", "") else here.person(to_raw)
    if to_raw.lower() not in ("anyone", "all", "everyone", "") and to is None:
        raise Refused(f"{to_raw} is not here; an offer is made face to face")
    party = _party(here, o["for"]) if o.get("for") else None
    give, get = parse_legs(o.get("give"), here.day, here.calendar), parse_legs(o.get("get"), here.day, here.calendar)
    if not give and not get:
        raise Refused("an offer needs something given or got")
    why = _offer_goods(here, give, party)
    if why:
        raise Refused(why)
    lots = max(1, int(float(o.get("lots") or 1)))
    same = next((oid for oid, x in here.offers().items() if x["by"] == here.name and x["to"] == to and x["give"] == give and x["get"] == get), None)
    if same:
        return f"Your offer {same} is already open."
    road = here.node is None                                                # in a meeting on the road: open while it lasts (D2-120)
    until = here.day if to or road else (int(o["until"]) - 1 if o.get("until") else None)
    oid = here.new_offer({"for": party, "to": to, "give": give, "get": get, "lots": lots, "taken": 0, "until": until, "open": True})
    return "You offered " + offer_text(here, oid) + (" (open while you meet)" if road else " (open today)" if to else " (open while you stay here)")


def offer_text(here, oid) -> str:
    o = here.offer(oid)
    g = ", ".join(_leg_short(x) for x in o["give"]) or "nothing"
    t = ", ".join(_leg_short(x) for x in o["get"]) or "nothing"
    lots = f" ({o['lots'] - o['taken']} lots)" if o["lots"] > 1 else ""
    return f"{oid}: {o['by']}" + (f" for {o['for']}" if o.get("for") else "") + f" offers {g} for {t}" + ("" if o["to"] else " (to anyone)") + lots


def _leg_short(leg) -> str:
    if "work" in leg:
        return f"work {leg['work']} days"
    w = leg["when"]
    return f"{leg['qty']:g} {leg['item']}" + (f" by day {w['by'] + 1}" if w.get("by") is not None else
                                               f" every {w['every']} days for {w['times']} times" if w.get("every") else "")


def accept(here, mind, a, party) -> str:
    oid = str(a.get("offer", "")).strip()
    o = here.offers().get(oid)
    if o is None:
        raise Refused(f"there is no open offer {oid!r} here")
    if o["to"] not in (None, here.name):
        raise Refused(f"offer {oid} was made to {o['to']}, not you")
    by = o["by"]
    if by == here.name:
        raise Refused("that is your own offer")
    if by not in here.people():
        raise Refused(f"{by} is not here; an offer is taken face to face")
    lots = max(1, min(int(float(a.get("lots") or 1)), o["lots"] - o["taken"]))
    if lots <= 0:
        raise Refused(f"offer {oid} is all taken")
    me = party or here.name
    src_them = here.party_container(o["for"]) if o.get("for") else None
    src_me = here.party_container(party) if party else None
    from cybertron2.engine import knowledge as KN
    for leg in o["give"]:
        if "item" in leg and leg["when"].get("now") and KN.available(here, leg["item"], who=by, extra=src_them) + 1e-9 < leg["qty"] * lots:
            raise Refused(f"{by} no longer has {leg['qty'] * lots:g} {leg['item']}; nothing was exchanged")
    for leg in o["get"]:
        if "item" in leg and leg["when"].get("now") and KN.available(here, leg["item"], extra=src_me) + 1e-9 < leg["qty"] * lots:
            raise Refused(f"you have only {show(KN.available(here, leg['item'], extra=src_me))} {leg['item']} to hand; nothing was exchanged")
    giver, getter = o.get("for") or by, me
    legs = [{**leg, "from": giver, "to": getter} for leg in o["give"]] + [{**leg, "from": getter, "to": giver} for leg in o["get"]]
    for leg in legs:                                                        # lots multiply the goods
        if "qty" in leg:
            leg["qty"] = round(leg["qty"] * lots, 6)
    for leg in legs:                                                        # now-legs, both ways, at once
        if "item" in leg and leg["when"].get("now"):
            payer = by if leg["from"] == giver else here.name
            src_extra = src_them if leg["from"] == giver else src_me
            _pay(here, payer, leg["from"], leg["to"], leg["item"], leg["qty"], src_extra)
            leg["paid"] = 1
    here.apply("set", ref=("offer", oid), field="taken", value=o["taken"] + lots)
    if o["taken"] >= o["lots"]:
        here.apply("close_offer", offer=oid, why="taken")
    open_legs = [l for l in legs if "work" in l or not l["when"].get("now")]
    names = {by, here.name}
    aid = here.new_agreement({"parties": sorted({giver, getter}), "legs": legs, "witnesses": here.people(),
                              "status": "open" if open_legs else "done", "offer": oid, "made_by": sorted(names)})
    here.event("trade", f"{here.name} took {by}'s offer: " + "; ".join(_leg_short(l) for l in legs), actor=here.name, target=by,
               salience=0.4, tags=["trade"], concerns=[by])
    here.record("accept", None, party, agreement=aid)
    owed = [l for l in open_legs]
    return (f"You accepted {by}'s offer {oid}" + (f" ({lots} lots)" if lots > 1 else "") + ": " + "; ".join(_leg_short(l) for l in legs)
            + (f". Agreement {aid} stays open: " + "; ".join(leg_text(l, here.name, here.day) for l in owed) if owed else "."))


def _pay(here, payer, frm, to, item, qty, extra=None):
    """Move goods from the payer's hands and stores it may take from (or the party's) to the payee here."""
    order = [here.hands_of(payer)] + ([extra] if extra else []) + [c for c in here.takeable(payer) if c != here.hands_of(payer) and c != extra]
    dst = here.hands_of(to) if to in here.people() else here.party_container(to)
    if dst is None:
        raise Refused(f"{to} has nowhere here to receive it")
    left = qty
    for cid in order:
        if left <= 1e-9:
            break
        have = here.contents(cid).get(item, 0.0)
        q = min(have, left)
        if q > 1e-9:
            here.apply("transfer", src=cid, dst=dst, item=item, qty=q)
            left -= q
    if left > 1e-6:
        raise Refused(f"{payer} has only part of the {item}")


def withdraw(here, a) -> str:
    oid = str(a.get("offer", "")).strip()
    o = here.offers().get(oid)
    if o is None or o["by"] != here.name:
        raise Refused(f"you have no open offer {oid!r} here")
    here.apply("close_offer", offer=oid, why="withdrawn")
    return f"You withdrew offer {oid}."


def release(here, mind, a) -> str:
    """Whoever is owed may count a debt paid (D4-37): the person owed, or one of the household owed. What is still owing to them on
    the agreement ends; it closes when nothing is owed either way."""
    aid = str(a.get("agreement") or a.get("offer") or "").strip()
    ag = here.agreements().get(aid)
    if ag is None:
        raise Refused(f"you are party to no agreement {aid!r}")
    mine = {here.name, here.household()}
    legs = [(i, l) for i, l in enumerate(ag["legs"]) if l["to"] in mine and not _met(l)]
    if not legs:
        raise Refused(f"nothing is owed to you on {aid}")
    for i, l in legs:
        if "work" in l:
            here.apply("leg", agreement=aid, leg=i, done=l["work"], released_by=here.name)
        else:
            w_ = l["when"]
            here.apply("leg", agreement=aid, leg=i, arrears=0.0, paid=(w_.get("times", 1) if w_.get("every") else 1), released_by=here.name)
    if all(_met(l) for l in ag["legs"]):
        here.apply("close_agreement", agreement=aid, status="done")
    debtor = sorted({l["from"] for _, l in legs})
    here.event("release", f"{here.name} counted what {', '.join(debtor)} owed on {aid} as paid", actor=here.name, salience=0.4,
               tags=["trade"], concerns=[d for d in debtor if d in here.people()])
    return f"You counted {aid} as paid: {', '.join(debtor)} owe{'s' if len(debtor) == 1 else ''} you nothing more on it."


def lines(here, mind) -> list:
    """Each open agreement one is party to, in words (agreements.md: what agents see)."""
    out = []
    names = {iid: h["name"] for iid, h in here.households().items()}
    for aid, ag in here.agreements().items():
        if ag["status"] != "open":
            continue
        for leg in ag["legs"]:
            if ("work" in leg and leg["done"] < leg["work"]) or ("item" in leg and not _met(leg)):
                out.append(f"{aid}: " + leg_text(leg, here.name if here.name in ag["parties"] else mind.household, here.day, names))
    return out


def _met(leg) -> bool:
    if "work" in leg:
        return leg["done"] >= leg["work"]
    w = leg["when"]
    return leg["paid"] >= (w.get("times", 1) if w.get("every") else 1) and leg.get("arrears", 0) <= 1e-9


# ---------------------------------------------------------------------- settlement (engine side: D2-32)
def settle(w) -> list:
    """At the end of the day's work: every leg due, or in arrears, is paid where there is a path (payer and payee at one node), from
    what the payer carries and stores it may take from; else it falls into arrears. Work legs count days of work done for the payee."""
    from cybertron2.engine.here import Here
    out = []
    for aid, ag in w.s["agreements"].items():
        if ag["status"] != "open":
            continue
        for i, leg in enumerate(ag["legs"]):
            if "work" in leg:
                days = {a["day"] for a in w.s["acts"] if a["actor"] == leg["from"] and a.get("for") == leg["to"]}
                done = len(days)
                if done != leg["done"]:
                    w.apply("leg", None, agreement=aid, leg=i, done=done)
                continue
            due, inst = _due(w, leg)
            if due <= 1e-9:
                continue
            payer = _person_for(w, leg["from"])
            node = w.at(payer) if payer else None
            paid = 0.0
            if payer and node is not None and _present_for(w, leg["to"], node):
                here = Here(w, payer)
                from cybertron2.engine import knowledge as KN
                extra = here.party_container(leg["from"]) if leg["from"] != payer else None
                q = min(KN.available(here, leg["item"], extra=extra), due)
                if q > 1e-9:
                    try:
                        with w.cause(actor=payer, verb="settle", node=node):
                            _pay(here, payer, leg["from"], leg["to"], leg["item"], q, extra)
                        paid = q
                    except Refused:                                         # no way to hand it over today: it stays owed
                        paid = 0.0
            fields = {"arrears": round(due - paid, 6)}
            if inst:                                                        # an instalment fell due today: paid, or now owed
                wh = leg["when"]
                fields["paid"] = leg["paid"] + 1
                if wh.get("every"):
                    fields["when"] = {**wh, "next": wh["next"] + wh["every"]}
            w.apply("leg", None, agreement=aid, leg=i, **fields)
            out.append({"agreement": aid, "leg": i, "paid": paid, "arrears": fields["arrears"]})
        if all(_met(l) for l in ag["legs"]):
            w.apply("close_agreement", None, agreement=aid, status="done")
    return out


def install(w) -> None:
    """Paying a debt is a give (money_and_markets.md): a hook on the chokepoint credits goods given or left by a debtor to its
    creditor (the person, or a store its household holds) against their open legs, oldest first."""
    w.hook("after", "transfer", _credit)


def _credit(w, call, out):
    cause = call.get("cause") or {}
    if cause.get("verb") not in ("give", "leave"):
        return
    kw = call["kw"]
    payer = cause.get("for") or cause.get("actor")
    payers = {payer, w.household_of(payer)} if payer in w.s["people"] else {payer}
    c = w.s["containers"][kw["dst"]]
    if c["kind"] == "hands":
        payees = {c["of"], w.household_of(c["of"])}
    elif c["kind"] == "stock":
        payees = {cl["claimant"] for cl in w.claims_on(("building", c["of"])) if cl["grounds"] != "granted"}
        payees |= {m for x in list(payees) if x in w.s["institutions"] for m in w.members(x)}     # its household's members
    else:
        return
    left = float(kw["qty"])
    for aid, ag in sorted(w.s["agreements"].items(), key=lambda kv: kv[1].get("day", 0)):
        if ag["status"] != "open" or left <= 1e-9:
            continue
        for i, leg in enumerate(ag["legs"]):
            if "item" not in leg or leg["item"] != kw["item"] or leg["from"] not in payers or leg["to"] not in payees or _met(leg):
                continue
            arrears = float(leg.get("arrears", 0.0))
            if arrears > 1e-9:
                q = min(arrears, left)
                w.apply("leg", None, agreement=aid, leg=i, arrears=round(arrears - q, 6))
                left -= q
            elif leg["when"].get("by") is not None and not leg["paid"]:
                owed = leg["qty"] - float(leg.get("prepaid", 0.0))
                q = min(owed, left)
                fields = {"prepaid": round(float(leg.get("prepaid", 0.0)) + q, 6)}
                if fields["prepaid"] >= leg["qty"] - 1e-9:
                    fields.update(paid=1)
                w.apply("leg", None, agreement=aid, leg=i, **fields)
                left -= q
        if all(_met(l) for l in ag["legs"]):
            w.apply("close_agreement", None, agreement=aid, status="done")


def _due(w, leg):
    """(what is owed on a leg today, whether an instalment falls due today): a promise on its day, a payment on each of its days,
    and arrears from before."""
    wh = leg["when"]
    arrears = float(leg.get("arrears", 0.0))
    if wh.get("now"):
        return (0.0 if leg["paid"] else leg["qty"]), False
    if wh.get("by") is not None:
        inst = not leg["paid"] and w.d >= wh["by"]
        return arrears + (leg["qty"] - float(leg.get("prepaid", 0.0)) if inst else 0.0), inst
    if wh.get("every"):
        inst = leg["paid"] < wh["times"] and w.d >= wh["next"]
        return arrears + (leg["qty"] if inst else 0.0), inst
    return arrears, False


def _person_for(w, party):
    """Who pays for a party: the person, or a living member of a household (its head first) at a node."""
    if party in w.s["people"]:
        return party if w.s["people"][party]["alive"] and w.at(party) else None
    if party in w.s["institutions"]:
        m = [w.head(party)] + w.members(party)
        return next((x for x in m if x and w.at(x)), None)
    return None


def _present_for(w, party, node) -> bool:
    if party in w.s["people"]:
        return w.s["people"][party]["alive"] and w.at(party) == node             # nothing is paid to the dead
    return any(b["node"] == node and any(c["claimant"] == party for c in w.claims_on(("building", bid))) for bid, b in w.s["buildings"].items())
