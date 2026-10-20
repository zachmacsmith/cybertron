"""Counsel: a lawyer acting in court for a client who retains them (docs/review/31_institutions/07_rules_courts.md §8 #7-9, §5.5;
00_framework.md §9; 08_integration.md item 2.2).

Before this, representation was impossible: agency (contracts.AGENCY_ACTIONS) covers only transfers and escrow deposits. Here:

  Retainer   who is whose counsel is read from the contracts in force, never declared to the engine: an active association whose
             law declares PARTIES {agent: role} naming a "client" and a "counsel" (the Retainer preset of cybertron/standing.py, or
             any bilateral standing contract with those roles) makes every counsel party the counsel of every client party while
             all its parties are members. Ending the retainer (notice, leaving) ends the agency.
  represent  the counsel's action: represent {"client": "Ann", "action": "accuse" | "respond" | "appeal" | "withdraw_case", ...the
             action's own arguments}. The client is the party: the case names the client as accuser (accuse) or the accused who
             answers (respond); the counsel only acts. Evidence may be any logged entry the counsel or the client could see (shown
             as the one who could see it saw it). The case records its counsel (case "counsel": {client: counsel}, shown to laws by
             cases() and cases_of()), a public `counsel_acted` event says who acted for whom, and the client is told.
  court rule `counsel` (courts.OPT_RULES, default on): a polity's law may set it False, and then counsel may not act in its courts.

Opt-in: the represent action exists only in a world where some retainer is in force, and is listed only for agents who are counsel
under one (action_registry: represent's `when`; actions._act treats it as unknown elsewhere, see world_hidden). No existing world
has a retainer, so no existing world changes. law.v2 only (courts v2: the routed filings and appeals).
"""
from __future__ import annotations

from cybertron import accounts as AC
from cybertron import courts as CO
from cybertron import dispatch as D
from cybertron import jurisdictions as J
from cybertron import roles as R

ACTIONS = ("accuse", "respond", "appeal", "withdraw_case")
_CONSTS: dict = {}                                                    # code -> its PARTIES (parsed once per code text)


def _parties(code: str) -> dict:
    p = _CONSTS.get(code)
    if p is None:
        from cybertron import contracts as KC
        try:
            got = KC.constants(code).get("PARTIES")
        except (SyntaxError, ValueError):
            got = None
        p = _CONSTS[code] = {str(a): str(r) for a, r in got.items()} if isinstance(got, dict) else {}
    return p


def retainers(k) -> list:
    """[(contract id, {client agents}, {counsel agents})] for every association in force whose law names client and counsel parties
    who are all still its members."""
    if "contracts" not in k.w:
        return []
    out = []
    for cid, rec in sorted(AC.assocs(k).items()):
        if rec.get("status") == "dissolved":
            continue
        members = set(rec.get("members") or ())
        for lid in rec.get("laws") or ():
            law = k.w["laws"].get(lid)
            if not law or law.get("status") != "active":
                continue
            parties = _parties(law["code"])
            roles = set(parties.values())
            if "client" in roles and "counsel" in roles and set(parties) <= members:
                out.append((cid, {a for a, r in parties.items() if r == "client"}, {a for a, r in parties.items() if r == "counsel"}))
    return out


def any_retainer(k) -> bool:
    return bool(retainers(k))


def counsel_of(k, client) -> list:
    """The agents retained as counsel by client, in name order."""
    return sorted({c for _, cl, co in retainers(k) if client in cl for c in co} - {client})


def clients_of(k, lawyer) -> list:
    """The agents whose counsel lawyer is, in name order."""
    return sorted({c for _, cl, co in retainers(k) if lawyer in co for c in cl} - {lawyer})


def world_hidden(k) -> set:
    """Review 31.07/31.05 actions that do not exist in this world now (actions._act treats them as unknown): represent without any
    retainer, withdraw_case without a court that allows withdrawal, read_register without a law that declares a readable register."""
    from cybertron import registers as RG
    out = set()
    if not (D.v2(k) and any_retainer(k)):
        out.add("represent")
    if not CO.withdrawal_on(k):
        out.add("withdraw_case")
    if not RG.any_readable(k):
        out.add("read_register")
    from cybertron import surveillance as SV                            # review 31.04 #10: only under the pull wiretap
    if not SV.pull(k):
        out.add("wiretap")
    return out


# ---------------------------------------------------------------------- the represent action
def _error(msg):
    from cybertron.actions import ActionError
    return ActionError(msg)


def _evidence(k, viewers, evidence) -> tuple:
    """(events, cited) for the evidence ids: each must be visible to one of the viewers (the counsel or the client); cited as that one
    saw it."""
    from cybertron.agents import render_event
    by_id = {e["id"]: e for e in k.events}
    evs, cited = [], []
    for eid in (evidence or []):
        e = by_id.get(str(eid))
        who = next((v for v in viewers if e is not None and (k.can_see(v, e) or R.saw(k, v, e["id"]))), None)
        if who is None:
            raise _error(f"you cannot cite {eid}: it does not exist, or neither you nor your client could see it")
        evs.append(e)
        cited.append({"id": e["id"], "as_seen": (render_event(k, e, viewer=who) or "")[:400]})
    return evs, cited


def _allowed(k, c_or_lid, case=True) -> None:
    pol = CO.polity_of(k, c_or_lid) if case else AC.account_of(k, c_or_lid)
    if not CO.opt_rule(k, pol, "counsel"):
        raise _error("counsel may not act in this court (a law in force sets the court rule counsel to False)")


def _done(k, aid, client, action, case) -> None:
    CO.note_counsel(k, case, client, aid)
    k.log("counsel_acted", aid, {"case": case, "client": client, "counsel": aid, "action": action}, vis="public")
    k.notify(client, f"Your counsel {aid} acted for you: {action} in case {case}.")


def act_represent(k, aid, client, action, agent=None, law=None, clause=None, evidence=None, case=None, reason=""):
    """represent {"client", "action", ...}: act in court for a client who retains you (see the module docstring)."""
    client = str(client)
    if client not in k.w["agents"]:
        raise _error(f"unknown client {client}")
    if aid not in counsel_of(k, client):
        mine = clients_of(k, aid)
        raise _error(f"you are not {client}'s counsel: no retainer in force names you" + (
            f" (your clients: {', '.join(mine)})" if mine else ""))
    action = str(action or "").strip().lower()
    if action not in ACTIONS:
        raise _error(f"represent's action is one of {', '.join(ACTIONS)}")
    if action == "accuse":
        if agent is None or law is None or clause is None:
            raise _error('accuse for a client needs "agent", "law", "clause" and "evidence"')
        cid = f"{law}:{clause}"
        if cid not in k.w["clauses"]:
            raise _error(f"no clause '{clause}' in {law}")
        lid = k.w["clauses"][cid]["law"]
        _allowed(k, lid, case=False)
        if J.enabled(k):                                                # jurisdictions: the law must bind the accused
            J.check_case(k, client, str(agent), lid)
        evs, cited = _evidence(k, (aid, client), evidence)
        cnum = f"C{k.w['case_seq'] + 1}"
        k.apply("open_case", jurisdiction=D.jur_of(k, lid), case=cnum, accuser=client, accused=str(agent), clause=cid,
                evidence=[e["id"] for e in evs], cited=cited)
        _done(k, aid, client, "accuse", cnum)
        return f"Case {cnum} filed for {client}" + ("" if k.w["cases"][cnum]["judges"] else " (no judge yet)") + "."
    c = k.w["cases"].get(str(case))
    if c is None:
        raise _error(f"no case {case}")
    _allowed(k, c)
    if action == "respond":
        if c["accused"] != client or c["status"] != "open":
            raise _error(f"{client} cannot respond to {case}: " + ("it is not the accused" if c["accused"] != client else "it is not open"))
        evs, cited = _evidence(k, (aid, client), evidence)
        k.apply("answer_case", jurisdiction=D.jur_of(k, CO.clause_law(k, c)), case=c["id"], accused=client,
                evidence=[e["id"] for e in evs], cited=cited)
        _done(k, aid, client, "respond", c["id"])
        return f"Counter-evidence added to {c['id']} for {client}."
    if action == "appeal":
        out = CO.act_appeal(k, client, c["id"], reason)
        _done(k, aid, client, "appeal", c["id"])
        return out.replace("Appeal of", f"Appeal for {client} of", 1)
    out = CO.withdraw(k, client, c["id"], reason, counsel=aid)
    _done(k, aid, client, "withdraw_case", c["id"])
    return out
