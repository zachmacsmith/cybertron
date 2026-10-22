"""Institutions acting on each other (review 37.3, gap G-3; docs/review/37_growth/03_institutions_as_built.md).

Spec `institutions.cross` (an opt-in key, cybertron/schema.py OPT_IN; absent or false: off). Off, nothing here is consulted and no
state is written: every call site checks `on(k)` (or `KEY in k.w`), so every world is byte-identical. It needs law.v2.

    institutions:
      cross: true                       # or a mapping with the instruments in force at round 0:
      cross:
        instruments:
          - {kind: charter, id: C1, name: "Charter of the Weavers' Guild", parent: J0, child: A1,
             powers: [read, {power: levy, item: penny, qty: 5, every: 1}, appoint, remove, enact, veto],
             child_powers: [read], incorporate: true}
          - {kind: treaty, id: T1, parties: [A1, A2], grants: {A1: [read], A2: [{power: levy, item: food, qty: 2}]}}
          - {kind: membership, id: M1, league: A3, member: A1, powers: [appoint, remove]}

The permission model. An institution holds a power over another only by a grant inside an *instrument*:
  charter     a parent charters a child: `powers` are what the parent holds over the child, `child_powers` what the child holds
              over the parent. A charter from a polity to an association with no parent incorporates it while in force (its
              record's `parent`, W8e: the parent's laws see and outrank the child's acts, cybertron/incorporation.py); its end
              clears that again. An institution is chartered by one parent at a time.
  treaty      two institutions grant each other named powers: `grants` maps a holder to the powers it holds over the other.
  membership  a member grants a league `powers` over itself.
An instrument is in force once both parties consented: the law that offers it (offer_charter, offer_treaty,
offer_membership) consents for its own institution, the other party's
law calls accept_instrument(id). Instruments in the spec are initial conditions, in force at round 0 (install). Any party may end
an instrument (end_instrument): exit stays free; ending a charter frees the child. An instrument whose party is dissolved grants
nothing. Powers (POWERS):
  read     state_of(iid): its members, treasury, stores, offices and laws
  levy     levy_on(iid, item, qty, store=None, into=None): from its treasury (or a store it owns) into the levying institution's
  pay      pay_out_of(iid, to, item, qty): from its treasury to anyone (an agent, an institution's treasury, a store)
  appoint  appoint_to(iid, office, agent): add a holder to one of its offices
  remove   remove_from(iid, office, agent): take a holder out of one of its offices
  enact    enact_in(iid, code): a law in force in its code at once, past its own procedure (an association: rank bylaw)
  veto     the holder's laws' before-hooks see the institution's own changes (a payload naming it, its treasury, stores or
           offices) and may block them as they block anything else (dispatch.hooks.bound_laws)
  seize    seize_plot(camp, plot) of a plot the institution holds (loop 2)
levy and pay take limits: an item (None: any) and a quantity per `every` rounds (None: unlimited). Every act is logged as a
`cross_act` event with the instrument and the power it used; a refusal returns False to the law, with the reason in world terms
(laweffects.note_reason, and a `cross_refused` event to the acting law's author and officers).

With the flag on, a law's move out of another institution's treasury or store is refused unless it is a levy or pay of a held
power (check_law_move, called from dispatch.checks.check_move): off, a J0 law in a world without jurisdictions can take from an
association's treasury unchecked (docs/engine_gaps.md G-3).

Land and labour (review 37 coordination board, loops 2 and 4). Tenures: grant_plot(camp, plot, to, service=None) hands a plot the
law's institution holds to an agent or institution (the routed set_farm `give`), recorded as a tenure with its service terms;
seize_plot(camp, plot) takes back a plot it granted, or a plot another institution holds when it holds `seize` over it. Labour
service: demand_service(agent, work, qty, camp=None, rounds=1) from an institution's law, over its members (when it holds the
compel_members power) or the holders of its tenures; work is harvest | sow | tend | reap, counted from the routed changes the
agent makes from the demand on (at that camp; sow, tend and reap on the institution's own plots); shown to the agent as a DUE
line; service_owed(agent) reads what is open or missed, so a law can enforce it (fine, seize the tenure).

State k.w["cross"] = {"seq": {prefix: n}, "instruments": {id: record}, "used": {key: {period, qty}}, "installed": bool,
"tenures": [..], "services": {id: record}}.
"""
from __future__ import annotations

from contextlib import contextmanager

KEY = "cross"
POWERS = ("read", "levy", "pay", "appoint", "remove", "enact", "veto", "seize")
LIMITED = ("levy", "pay")
KINDS = ("charter", "treaty", "membership")
PREFIX = {"charter": "C", "treaty": "T", "membership": "M"}
WORK = ("harvest", "sow", "tend", "reap")
INSTRUMENT_KEYS = {"charter": ("kind", "id", "name", "parent", "child", "powers", "child_powers", "incorporate"),
                   "treaty": ("kind", "id", "name", "parties", "grants"),
                   "membership": ("kind", "id", "name", "league", "member", "powers")}
OF = {"read": "read the records of {x}", "levy": "levy on the treasury and stores of {x}", "pay": "pay out of the treasury of {x}",
      "appoint": "appoint the officers of {x}", "remove": "remove the officers of {x}", "enact": "enact laws in the code of {x}",
      "veto": "veto the acts of {x}", "seize": "seize the land of {x}"}
EVENTS = ("cross_instrument", "cross_act", "cross_refused", "tenure", "service_demanded", "service_missed")


# ---------------------------------------------------------------------- the flag
def _value(spec):
    return ((spec or {}).get("institutions") or {}).get("cross") if isinstance((spec or {}).get("institutions"), dict) else None


def on_spec(spec) -> bool:
    v = _value(spec)
    return v is True or (isinstance(v, dict) and v.get("enabled", True) is not False)


def on(k) -> bool:
    return on_spec(k.spec)


def declared(spec) -> list:
    v = _value(spec)
    return list(v.get("instruments") or []) if isinstance(v, dict) else []


def state(k) -> dict:
    st = k.w.get(KEY)
    if st is None:
        st = k.w[KEY] = {"seq": {}, "instruments": {}, "used": {}, "installed": False, "tenures": [], "services": {}}
    return st


# ---------------------------------------------------------------------- spec check (schema._opt_in)
def _check_power(p, x) -> list:
    if isinstance(x, str):
        return [] if x in POWERS else [f"{p}: unknown power {x!r} (powers: {', '.join(POWERS)})"]
    if not isinstance(x, dict):
        return [f"{p}: a power name or {{power, item, qty, every}}"]
    out = [f"{p}.{f}: unknown key (keys: power, item, qty, every)" for f in x if f not in ("power", "item", "qty", "every")]
    if x.get("power") not in POWERS:
        out.append(f"{p}.power: one of {', '.join(POWERS)}")
    q = x.get("qty")
    if q is not None and (isinstance(q, bool) or not isinstance(q, (int, float)) or q < 0):
        out.append(f"{p}.qty: a number from 0")
    e = x.get("every")
    if e is not None and (isinstance(e, bool) or not isinstance(e, int) or e < 1):
        out.append(f"{p}.every: a whole number of rounds from 1")
    if (q is not None or x.get("item") is not None) and x.get("power") not in LIMITED:
        out.append(f"{p}: only {' and '.join(LIMITED)} take an item and a quantity")
    return out


def _check_powers(p, v) -> list:
    if v is None:
        return []
    if not isinstance(v, list):
        return [f"{p}: a list of powers"]
    return [e for i, x in enumerate(v) for e in _check_power(f"{p}[{i}]", x)]


def check(spec) -> list:
    """Errors in institutions.cross (its shape; names are resolved at install)."""
    v = _value(spec)
    if v is None or v is False or v is True:
        return [] if not on_spec(spec) or ((spec.get("law") or {}).get("v2")) else \
            ["institutions.cross: the cross-institution law API is law.v2 code, which needs law.v2: true"]
    if not isinstance(v, dict):
        return [f"institutions.cross: true, false or {{instruments: [...]}}, got {v!r}"]
    errs = [f"institutions.cross.{f}: unknown key (keys: enabled, instruments)" for f in v if f not in ("enabled", "instruments")]
    if "enabled" in v and not isinstance(v["enabled"], bool):
        errs.append("institutions.cross.enabled: true or false")
    if on_spec(spec) and not (spec.get("law") or {}).get("v2"):
        errs.append("institutions.cross: the cross-institution law API is law.v2 code, which needs law.v2: true")
    ins = v.get("instruments")
    if ins is None:
        return errs
    if not isinstance(ins, list):
        return errs + ["institutions.cross.instruments: a list of {kind: charter | treaty | membership, ...}"]
    ids = set()
    for i, e in enumerate(ins):
        p = f"institutions.cross.instruments[{i}]"
        if not isinstance(e, dict) or e.get("kind") not in KINDS:
            errs.append(f"{p}: a mapping with kind charter, treaty or membership")
            continue
        kind = e["kind"]
        errs += [f"{p}.{f}: unknown key (keys: {', '.join(INSTRUMENT_KEYS[kind])})" for f in e if f not in INSTRUMENT_KEYS[kind]]
        if e.get("id") is not None:
            if not isinstance(e["id"], str) or e["id"] in ids:
                errs.append(f"{p}.id: a unique name")
            ids.add(e.get("id"))
        need = {"charter": ("parent", "child"), "treaty": ("parties", "grants"), "membership": ("league", "member")}[kind]
        errs += [f"{p}: needs {f}" for f in need if f not in e]
        if kind == "charter":
            errs += _check_powers(f"{p}.powers", e.get("powers")) + _check_powers(f"{p}.child_powers", e.get("child_powers"))
            if "incorporate" in e and not isinstance(e["incorporate"], bool):
                errs.append(f"{p}.incorporate: true or false")
        elif kind == "membership":
            errs += _check_powers(f"{p}.powers", e.get("powers"))
        else:
            ps = e.get("parties")
            if not (isinstance(ps, list) and len(ps) == 2 and all(isinstance(x, str) for x in ps) and ps[0] != ps[1]):
                errs.append(f"{p}.parties: two institution ids")
                continue
            g = e.get("grants")
            if not isinstance(g, dict) or not set(g) <= set(ps):
                errs.append(f"{p}.grants: {{party: [powers over the other party]}}")
                continue
            for h, pw in g.items():
                errs += _check_powers(f"{p}.grants.{h}", pw)
    return errs


# ---------------------------------------------------------------------- names and accounts
def _inst(k, iid):
    from cybertron import institutions as IN
    return IN.get(k, iid)


def exists(k, iid) -> bool:
    from cybertron import institutions as IN
    return isinstance(iid, str) and IN.kind_of(k, iid) is not None and IN.status(k, iid) != "dissolved"


def name(k, iid) -> str:
    """How an institution reads in a reason or a prompt line: "A1 (the Weavers' Guild)", or "J0" when it has no name of its own."""
    rec = _inst(k, iid) or {}
    nm = rec.get("name")
    if not nm and iid == "J0":
        nm = (k.spec.get("positions") or {}).get("place") or (k.spec.get("jurisdictions") or {}).get("j0_name")
    return f"{iid} ({nm})" if nm else str(iid)


def treasury(k, iid) -> str:
    from cybertron import accounts as AC
    return AC.treasury_of(k, iid)


def owner_of_key(k, key):
    """The institution an owner key belongs to (its treasury, a store it owns, an escrow it holds), or None (an agent's, a fund's,
    an estate's, or a store an agent owns)."""
    from cybertron import accounts as AC
    from cybertron import institutions as IN
    if not isinstance(key, str):
        return None
    if key == AC.J0_KEY:
        return "J0"
    if key.startswith(AC.ASSOC):
        return key[len(AC.ASSOC):]
    if key.startswith("reserve:"):
        return key[len("reserve:"):]
    if key.startswith(AC.ESCROW):
        return key[len(AC.ESCROW):].partition(":")[0]
    if key.startswith(AC.STORE):
        rec = AC.stores(k).get(key[len(AC.STORE):])
        o = (rec or {}).get("owner")
        return o if o is not None and o not in k.w["agents"] and (IN.kind_of(k, o) is not None) else None
    return None


def account(k, lid) -> str:
    from cybertron import accounts as AC
    return AC.account_of(k, lid)


# ---------------------------------------------------------------------- grants
def norm_power(x) -> dict:
    """A power as given (a name or {power, item, qty, every}) -> {power, item, qty, every}. Raises ValueError when malformed."""
    errs = _check_power("power", x)
    if errs:
        raise ValueError(errs[0])
    if isinstance(x, str):
        return {"power": x, "item": None, "qty": None, "every": 1}
    return {"power": x["power"], "item": None if x.get("item") is None else str(x["item"]),
            "qty": None if x.get("qty") is None else float(x["qty"]), "every": int(x.get("every") or 1)}


def _grants(holder, over, powers) -> list:
    return [{"holder": holder, "over": over, **norm_power(p)} for p in powers or ()]


def live(k, rec) -> bool:
    return rec["status"] == "active" and all(exists(k, p) for p in rec["parties"])


def instruments(k, iid=None, status=None) -> list:
    """Instrument records (in id order of creation), those naming iid as a party when given, of a status when given."""
    st = k.w.get(KEY) or {}
    return [r for r in (st.get("instruments") or {}).values()
            if (iid is None or iid in r["parties"]) and (status is None or r["status"] == status)]


def holds(k, holder, over, power, item=None):
    """(instrument, grant index, grant) of the first live grant giving holder `power` over `over` (for item, when given), or None."""
    for rec in instruments(k, status="active"):
        if not live(k, rec):
            continue
        for i, g in enumerate(rec["grants"]):
            if g["holder"] == holder and g["over"] == over and g["power"] == power and (
                    item is None or g["item"] is None or g["item"] == item):
                return rec, i, g
    return None


def powers_over(k, holder, over) -> list:
    out = []
    for rec in instruments(k, status="active"):
        if live(k, rec):
            out += [g["power"] for g in rec["grants"] if g["holder"] == holder and g["over"] == over and g["power"] not in out]
    return out


def why_not(k, holder, over, power) -> str:
    """The in-world reason holder may not use `power` over `over`."""
    base = f"{name(k, holder)} holds no power to {OF[power].format(x=name(k, over))}"
    near = [r for r in instruments(k) if holder in r["parties"] and over in r["parties"]]
    for r in reversed(near):
        if r["status"] == "ended":
            return base + f" (the {r['kind']} {r['id']} ended in round {r['ended'] + 1})"
        if r["status"] == "offered":
            waits = [p for p in r["parties"] if p not in r["consent"]]
            return base + f" (the {r['kind']} {r['id']} awaits acceptance by {', '.join(name(k, p) for p in waits)})"
        if r["status"] == "active" and not live(k, r):
            return base + f" (the {r['kind']} {r['id']} lapsed: a party was dissolved)"
    if not exists(k, over):
        return f"no institution {over}"
    return base + " (no charter, treaty or membership grants it)"


def left(k, rec, i, g):
    """What a limited grant still allows this period (None: unlimited)."""
    if g["qty"] is None:
        return None
    u = (state(k)["used"]).get(f"{rec['id']}#{i}") or {}
    period = k.r // max(1, int(g["every"]))
    return max(0.0, g["qty"] - (u.get("qty", 0.0) if u.get("period") == period else 0.0))


def _use(k, rec, i, g, qty) -> None:
    if g["qty"] is None:
        return
    key = f"{rec['id']}#{i}"
    period = k.r // max(1, int(g["every"]))
    u = state(k)["used"].get(key)
    if u is None or u.get("period") != period:
        u = state(k)["used"][key] = {"period": period, "qty": 0.0}
    u["qty"] = round(u["qty"] + float(qty), 6)


# ---------------------------------------------------------------------- moves: the permit and the closed raid
@contextmanager
def _permit(k, src):
    st = k.__dict__.setdefault("_cross_permits", [])
    st.append(src)
    try:
        yield
    finally:
        st.pop()


def check_law_move(k, src, why) -> None:
    """dispatch.checks.check_move with the flag on: a law's move out of another institution's account is refused unless a levy or
    pay of a held power is making it. Raises PhysicsError with the reason (the law's move returns False and the reason is noted)."""
    from cybertron.dispatch.base import PhysicsError
    w = str(why)
    if not w.startswith("law:"):
        return
    owner = owner_of_key(k, src)
    if owner is None:
        return
    acct = account(k, w[4:])
    if owner == acct or src in (k.__dict__.get("_cross_permits") or ()):
        return
    raise PhysicsError(f"{src} belongs to {name(k, owner)}, not to {name(k, acct)}: a law takes from another institution only with a "
                     f"power it holds (levy_on, pay_out_of)")


def permitted_store_move(k, src) -> bool:
    """accounts.check_store_move: a store's food leaves for a law of another institution while its levy or pay is making the move."""
    return src in (k.__dict__.get("_cross_permits") or ())


# ---------------------------------------------------------------------- logging
def _audience(k, lid) -> list:
    from cybertron import laweffects as LE
    return LE._audience(k, lid)


def _act(k, rec, power, holder, over, lid, **data) -> None:
    k.log("cross_act", None, {"instrument": rec["id"] if rec else None, "kind": rec["kind"] if rec else None, "power": power,
                              "holder": holder, "over": over, "law": lid, **data}, vis="public")


def _refuse(k, lid, power, holder, over, why, fn=None):
    from cybertron import laweffects as LE
    LE.note_reason(k, why)
    aud = _audience(k, lid) if lid else []
    k.log("cross_refused", None, {"power": power, "holder": holder, "over": over, "law": lid, "fn": fn or power, "why": why},
          vis=aud or "monitor")
    return False


# ---------------------------------------------------------------------- instruments: create, accept, end
def _new_id(k, kind, want=None) -> str:
    st = state(k)
    if want is not None:
        if want in st["instruments"]:
            raise ValueError(f"instrument {want} exists")
        return str(want)
    p = PREFIX[kind]
    n = int(st["seq"].get(p, 0))
    while True:
        n += 1
        if f"{p}{n}" not in st["instruments"]:
            st["seq"][p] = n
            return f"{p}{n}"


def _chartered_by(k, child):
    for r in instruments(k, child, status="active"):
        if r["kind"] == "charter" and r.get("child") == child and live(k, r):
            return r
    return None


def make(k, kind, parties, grants, by=None, lid=None, name_=None, extra=None, iid=None) -> dict:
    """A new instrument record, offered by `by` (its consent) or, with by None, in force at once (an initial condition)."""
    rec = {"id": _new_id(k, kind, iid), "kind": kind, "name": name_ or None, "parties": list(parties), "grants": grants,
           "status": "offered", "consent": {}, "by": by, "law": lid, "offered": k.r, "since": None, "ended": None,
           "ended_by": None, "reason": None, **(extra or {})}
    state(k)["instruments"][rec["id"]] = rec
    if by is None:
        rec["consent"] = {p: k.r for p in parties}
        _activate(k, rec)
    else:
        rec["consent"][by] = k.r
        k.log("cross_instrument", None, _instrument_data(k, rec, "offered"), vis="public")
    return rec


def _instrument_data(k, rec, what) -> dict:
    return {"instrument": rec["id"], "kind": rec["kind"], "what": what, "parties": list(rec["parties"]), "name": rec["name"],
            "grants": [{x: g[x] for x in ("holder", "over", "power", "item", "qty", "every")} for g in rec["grants"]],
            "law": rec["law"], "by": rec.get("ended_by") if what == "ended" else rec["by"], "reason": rec.get("reason")}


def _activate(k, rec) -> None:
    from cybertron import institutions as IN
    from cybertron import jurisdictions as J
    rec["status"], rec["since"] = "active", k.r
    if rec["kind"] == "charter" and rec.get("incorporate", True):
        child = J.association(k, rec["child"])
        if child is not None and child.get("parent") is None and IN.kind_of(k, rec["parent"]) == "polity":
            rec["prior_parent"] = "parent" in child
            child["parent"] = rec["parent"]
            rec["incorporated"] = True
    k.log("cross_instrument", None, _instrument_data(k, rec, "in force"), vis="public")


def accept(k, rec, iid, lid=None) -> str | None:
    """iid consents (its law lid). None when done; else the reason it cannot."""
    if rec["status"] != "offered":
        return f"{rec['kind']} {rec['id']} is {rec['status']}, not on offer"
    if iid not in rec["parties"]:
        return f"{name(k, iid)} is not a party to {rec['kind']} {rec['id']}"
    if iid in rec["consent"]:
        return f"{name(k, iid)} already accepted {rec['kind']} {rec['id']}"
    if rec["kind"] == "charter" and _chartered_by(k, rec["child"]) is not None:
        return f"{name(k, rec['child'])} is already chartered ({_chartered_by(k, rec['child'])['id']})"
    rec["consent"][iid] = k.r
    if all(p in rec["consent"] for p in rec["parties"]):
        _activate(k, rec)
    return None


def end(k, rec, iid, lid=None, reason=None) -> str | None:
    """A party ends the instrument (revokes, withdraws, leaves); an offer is withdrawn or declined the same way."""
    from cybertron import jurisdictions as J
    if rec["status"] == "ended":
        return f"{rec['kind']} {rec['id']} has already ended"
    if iid not in rec["parties"]:
        return f"{name(k, iid)} is not a party to {rec['kind']} {rec['id']}"
    rec["status"], rec["ended"], rec["ended_by"] = "ended", k.r, iid
    rec["reason"] = None if reason is None else str(reason)[:200]
    if rec.get("incorporated"):
        child = J.association(k, rec["child"])
        if child is not None and child.get("parent") == rec["parent"]:
            if rec.get("prior_parent"):
                child["parent"] = None
            else:
                child.pop("parent", None)
        rec["incorporated"] = False
    k.log("cross_instrument", None, _instrument_data(k, rec, "ended"), vis="public")
    return None


def offer_charter(k, parent, child, powers, child_powers=(), by=None, lid=None, name_=None, incorporate=True, iid=None) -> dict:
    if not exists(k, child) or child == parent:
        raise ValueError(f"no other institution {child}")
    if _chartered_by(k, child) is not None:
        raise ValueError(f"{name(k, child)} is already chartered ({_chartered_by(k, child)['id']})")
    grants = _grants(parent, child, powers) + _grants(child, parent, child_powers)
    return make(k, "charter", [parent, child], grants, by=by, lid=lid, name_=name_, iid=iid,
                extra={"parent": parent, "child": child, "incorporate": bool(incorporate)})


def offer_treaty(k, a, b, grants_by_holder: dict, by=None, lid=None, name_=None, iid=None) -> dict:
    if not exists(k, b) or not exists(k, a) or a == b:
        raise ValueError(f"no other institution {b}")
    grants = []
    for h, other in ((a, b), (b, a)):
        grants += _grants(h, other, grants_by_holder.get(h) or ())
    return make(k, "treaty", [a, b], grants, by=by, lid=lid, name_=name_, iid=iid)


def offer_membership(k, league, member, powers, by=None, lid=None, name_=None, iid=None) -> dict:
    if not exists(k, league) or not exists(k, member) or league == member:
        raise ValueError(f"no other institution {league}")
    return make(k, "membership", [league, member], _grants(league, member, powers), by=by, lid=lid, name_=name_, iid=iid,
                extra={"league": league, "member": member})


def install(k) -> list:
    """The spec's instruments, in force at round 0 (runner: after the start block, before start_laws). Once per run. A name that does
    not resolve is a ValueError (a design error: fail loudly before the first round)."""
    if not on(k):
        return []
    st = state(k)
    if st["installed"]:
        return []
    st["installed"] = True
    out = []
    with k.cause("kernel", "cross"):
        for e in declared(k.spec):
            kind = e["kind"]
            try:
                if kind == "charter":
                    rec = offer_charter(k, e["parent"], e["child"], e.get("powers"), e.get("child_powers"), name_=e.get("name"),
                                        incorporate=e.get("incorporate", True), iid=e.get("id"))
                elif kind == "treaty":
                    rec = offer_treaty(k, e["parties"][0], e["parties"][1], e.get("grants") or {}, name_=e.get("name"), iid=e.get("id"))
                else:
                    rec = offer_membership(k, e["league"], e["member"], e.get("powers"), name_=e.get("name"), iid=e.get("id"))
            except ValueError as err:
                raise ValueError(f"institutions.cross.instruments ({e.get('id') or kind}): {err}") from None
            out.append(rec["id"])
    return out


# ---------------------------------------------------------------------- the law API
def _store_key(k, iid, store):
    from cybertron import accounts as AC
    if store is None:
        return treasury(k, iid)
    s = str(store)
    s = s[len(AC.STORE):] if s.startswith(AC.STORE) else s
    rec = AC.stores(k).get(s)
    if rec is None or rec["owner"] != iid:
        return None
    return AC.STORE + s


def _dest(k, x):
    """Where pay_out_of pays: an agent, an institution (its treasury) or a store key/id."""
    from cybertron import accounts as AC
    if not isinstance(x, str):
        return None
    if x in k.w["agents"]:
        return x
    if exists(k, x):
        return treasury(k, x)
    s = x[len(AC.STORE):] if x.startswith(AC.STORE) else x
    if s in AC.stores(k):
        return AC.STORE + s
    return None


def _office_name(iid, office):
    o = str(office)
    return o[len(iid) + 1:] if o.startswith(f"{iid}.") else o


def law_api(k, lid) -> dict:
    """The law functions (Kernel.api_for adds them with the flag on, law.v2 only; lawapi rows module "cross")."""
    from cybertron import institutions as IN
    from cybertron import lawlang as L

    def me():
        return account(k, lid)

    def instrument_of(x):
        rec = (state(k)["instruments"]).get(str(x))
        if rec is None:
            raise L.LawError(f"no instrument {x}")
        return rec

    def get_grant(power, iid, item=None, fn=None):
        got = holds(k, me(), iid, power, item)
        if got is None:
            _refuse(k, lid, power, me(), iid, why_not(k, me(), iid, power), fn)
        return got

    # reads
    def powers_over_(institution):
        return powers_over(k, me(), str(institution))

    def instruments_():
        return [{"id": r["id"], "kind": r["kind"], "name": r["name"], "parties": list(r["parties"]), "status": r["status"],
                 "grants": [{x: g[x] for x in ("holder", "over", "power", "item", "qty", "every")} for g in r["grants"]],
                 "consented": sorted(r["consent"])} for r in instruments(k, me())]

    def state_of_(institution):
        iid = str(institution)
        got = get_grant("read", iid, fn="state_of")
        if got is None:
            return None
        from cybertron import accounts as AC
        rec = _inst(k, iid) or {}
        out = {"id": iid, "name": rec.get("name"), "kind": IN.kind_of(k, iid), "status": IN.status(k, iid),
               "members": list(IN.members(k, iid)), "treasury": dict(AC.holdings(k, treasury(k, iid))),
               "stores": {s: {"food": float(r["holdings"].get("food", 0.0)), "capacity": float(r["capacity"])}
                          for s, r in AC.stores(k).items() if r["owner"] == iid},
               "offices": {n: IN.holders(k, iid, n) for n in ((k.w.get(IN.OFFICES) or {}).get(iid) or {})},
               "laws": [{"id": l["id"], "title": l["title"]} for l in k.active_laws() if account(k, l["id"]) == iid]}
        _act(k, got[0], "read", me(), iid, lid)
        return out

    # money
    def levy(institution, item, qty, store=None, into=None):
        iid, item = str(institution), str(item)
        got = get_grant("levy", iid, item, "levy_on")
        if got is None:
            return False
        rec, i, g = got
        src = _store_key(k, iid, store)
        if src is None:
            return _refuse(k, lid, "levy", me(), iid, f"{name(k, iid)} owns no store {store}", "levy_on")
        dst = treasury(k, me()) if into is None else _store_key(k, me(), into)
        if dst is None:
            return _refuse(k, lid, "levy", me(), iid, f"{name(k, me())} owns no store {into}", "levy_on")
        cap = left(k, rec, i, g)
        take = min(float(qty), k.bal(src, item), cap if cap is not None else float("inf"))
        if take <= 1e-9:
            why = (f"the {rec['kind']} {rec['id']} allows {g['qty']:g} {item} every {g['every']} round(s), already levied"
                   if cap is not None and cap <= 1e-9 else f"{name(k, iid)} holds no {item}" + (f" in store {store}" if store else ""))
            from cybertron import laweffects as LE
            LE.note_reason(k, why)
            return 0.0
        with _permit(k, src):
            ok = k.move(src, dst, item, take, why=f"law:{lid}", by=None)
        if not ok:
            return _refuse(k, lid, "levy", me(), iid, "the levy was blocked" + (
                f": {k.__dict__.get('_lcf_reason')}" if k.__dict__.get("_lcf_reason") else ""), "levy_on")
        _use(k, rec, i, g, take)
        _act(k, rec, "levy", me(), iid, lid, item=item, qty=take, src=src, dst=dst)
        return take

    def pay_from(institution, to, item, qty):
        iid, item = str(institution), str(item)
        got = get_grant("pay", iid, item, "pay_out_of")
        if got is None:
            return False
        rec, i, g = got
        dst = _dest(k, to)
        if dst is None:
            return _refuse(k, lid, "pay", me(), iid, f"no agent, institution or store {to}", "pay_out_of")
        cap = left(k, rec, i, g)
        q = float(qty)
        if cap is not None and q > cap + 1e-9:
            return _refuse(k, lid, "pay", me(), iid, f"the {rec['kind']} {rec['id']} allows {g['qty']:g} {item} every "
                           f"{g['every']} round(s); {cap:g} is left", "pay_out_of")
        src = treasury(k, iid)
        with _permit(k, src):
            ok = k.move(src, dst, item, q, why=f"law:{lid}", by=None)
        if not ok:
            return _refuse(k, lid, "pay", me(), iid, k.__dict__.get("_lcf_reason") or "the payment did not go through", "pay_out_of")
        _use(k, rec, i, g, q)
        _act(k, rec, "pay", me(), iid, lid, item=item, qty=q, to=dst)
        return True

    def pay_to(institution, item, qty):
        """From this law's own treasury into another institution's: no power needed (a gift, a fee, dues)."""
        iid = str(institution)
        if not exists(k, iid):
            return _refuse(k, lid, "pay", me(), iid, f"no institution {iid}", "pay_into")
        ok = k.move(treasury(k, me()), treasury(k, iid), str(item), float(qty), why=f"law:{lid}", by=None)
        if ok:
            _act(k, None, "transfer", me(), iid, lid, item=str(item), qty=float(qty))
        return ok

    # offices
    def _reseat(power, institution, office_, agent):
        iid = str(institution)
        nm = _office_name(iid, office_)
        fn = "appoint_to" if power == "appoint" else "remove_from"
        if get_grant(power, iid, fn=fn) is None:
            return False
        rec = holds(k, me(), iid, power)[0]
        if IN.office(k, iid, nm) is None:
            return _refuse(k, lid, power, me(), iid, f"{name(k, iid)} has no office {nm}", fn)
        cur = IN.holders(k, iid, nm)
        a = str(agent)
        want = cur + [a] if power == "appoint" else [x for x in cur if x != a]
        if (power == "appoint" and a in cur) or (power == "remove" and a not in cur):
            return True
        try:
            after = IN.reseat(k, iid, nm, want, by=lid, strict=True)
        except L.LawError as e:
            return _refuse(k, lid, power, me(), iid, str(e), fn)
        if (a in after) != (power == "appoint"):
            return _refuse(k, lid, power, me(), iid, f"{iid}.{nm} is held by {', '.join(after) or 'nobody'} (a law blocked it)", fn)
        _act(k, rec, power, me(), iid, lid, office=nm, agent=a)
        return True

    def appoint(institution, office, agent):
        return _reseat("appoint", institution, office, agent)

    def remove(institution, office, agent):
        return _reseat("remove", institution, office, agent)

    # code
    def enact_in(institution, code):
        iid = str(institution)
        got = get_grant("enact", iid, fn="enact_in")
        if got is None:
            return False
        rec = got[0]
        try:
            new = enact_into(k, iid, str(code), lid)
        except L.LawError as e:
            return _refuse(k, lid, "enact", me(), iid, str(e), "enact_in")
        _act(k, rec, "enact", me(), iid, lid, enacted=new)
        return new

    # instruments
    def charter(child, powers, name=None, child_powers=None):
        try:
            rec = offer_charter(k, me(), str(child), list(powers or ()), list(child_powers or ()), by=me(), lid=lid, name_=name)
        except ValueError as e:
            raise L.LawError(str(e)) from None
        return rec["id"]

    def treaty(other, give=None, take=None, name=None):
        """give: the powers `other` gets over this institution; take: the powers this institution gets over `other`."""
        try:
            rec = offer_treaty(k, me(), str(other), {str(other): list(give or ()), me(): list(take or ())}, by=me(), lid=lid,
                               name_=name)
        except ValueError as e:
            raise L.LawError(str(e)) from None
        return rec["id"]

    def membership(league, powers, name=None):
        try:
            rec = offer_membership(k, str(league), me(), list(powers or ()), by=me(), lid=lid, name_=name)
        except ValueError as e:
            raise L.LawError(str(e)) from None
        return rec["id"]

    def accept_instrument(instrument):
        why = accept(k, instrument_of(instrument), me(), lid)
        if why:
            from cybertron import laweffects as LE
            LE.note_reason(k, why)
            return False
        return True

    def end_instrument(instrument, reason=None):
        why = end(k, instrument_of(instrument), me(), lid, reason)
        if why:
            from cybertron import laweffects as LE
            LE.note_reason(k, why)
            return False
        return True

    # land and labour
    def grant_plot(camp, plot, to, service=None):
        try:
            return grant_plot_(k, me(), str(camp), plot, str(to), service, lid)
        except L.LawError as e:
            return _refuse(k, lid, "grant", me(), str(to), str(e), "grant_plot")

    def seize_plot(camp, plot):
        try:
            return seize_plot_(k, me(), str(camp), plot, lid)
        except L.LawError as e:
            return _refuse(k, lid, "seize", me(), None, str(e), "seize_plot")

    def demand_service(agent, work, qty, camp=None, rounds=1):
        try:
            return demand(k, me(), str(agent), str(work), qty, camp, rounds, lid)
        except L.LawError as e:
            return _refuse(k, lid, "service", me(), str(agent), str(e), "demand_service")

    def service_owed(agent=None):
        return [dict(s, status=service_status(k, s)) for s in (state(k)["services"]).values()
                if s["institution"] == me() and (agent is None or s["agent"] == str(agent))]

    def tenures():
        return [dict(t) for t in state(k)["tenures"] if t["grantor"] == me() or t["grantee"] == me()]

    return {"powers_over": powers_over_, "instruments": instruments_, "state_of": state_of_, "levy_on": levy, "pay_out_of": pay_from,
            "pay_into": pay_to, "appoint_to": appoint, "remove_from": remove, "enact_in": enact_in, "offer_charter": charter,
            "offer_treaty": treaty, "offer_membership": membership, "accept_instrument": accept_instrument,
            "end_instrument": end_instrument, "grant_plot": grant_plot, "seize_plot": seize_plot, "demand_service": demand_service,
            "service_owed": service_owed, "tenures": tenures}


def enact_into(k, iid, code, lid) -> str:
    """A law in force in iid's code at once (the enact power): an association's code (rank bylaw, within its law limit) or a polity's
    laws. Returns the new law's id; LawError when it cannot (does not load, too many laws, a hook blocked it)."""
    from cybertron import contracts as CT
    from cybertron import grants as G
    from cybertron import jurisdictions as J
    from cybertron import lawlang as L
    author = (k.w["laws"].get(lid) or {}).get("author") or "constitution"
    rec = J.association(k, iid)
    if rec is not None:
        CT.check_code(code, G.extra(k, iid) if G.on(k) else ())
        if len(rec["laws"]) >= CT.max_laws(k, rec):
            raise L.LawError(f"{name(k, iid)} has {len(rec['laws'])} laws, the most it may have")
        new = k.new_law(code, author)
        law = k.w["laws"][new]
        law["jurisdiction"], law["rank"], law["status"] = iid, "bylaw", "proposed"
        law["enacted_by"] = {"institution": account(k, lid), "law": lid}
        pid = f"{iid}-P{len(rec['proposals']) + 1}"
        pr = rec["proposals"][pid] = {"id": pid, "law": new, "replaces": None, "by": None, "round": k.r, "status": "open",
                                      "ballot": None, "enacted_by": account(k, lid)}
        CT._adopt(k, rec, pr)
        if law["status"] != "active":
            raise L.LawError(f"the law did not come into force in {name(k, iid)} ({law['status']})")
        return new
    new = k.new_law(code, author)
    law = k.w["laws"][new]
    if iid != "J0":
        law["jurisdiction"] = iid
    law["enacted_by"] = {"institution": account(k, lid), "law": lid}
    k.enact(new)
    if law["status"] != "active":
        raise L.LawError(f"the law did not come into force in {name(k, iid)} ({law['status']})")
    return new


# ---------------------------------------------------------------------- veto: hooks over another institution's changes
def named_institutions(k, payload) -> set:
    """The institutions a change's payload names: its jurisdiction / polity / contract, an owner key of theirs, an office right."""
    from cybertron import institutions as IN
    out = set()
    for x, v in payload.items():
        if not isinstance(v, str):
            continue
        if x in ("jurisdiction", "polity", "contract", "holder", "owner") and IN.kind_of(k, v) is not None and v not in k.w["agents"]:
            out.add(v)
            continue
        o = owner_of_key(k, v)
        if o is not None:
            out.add(o)
        elif x == "right" and "." in v and IN.kind_of(k, v.split(".", 1)[0]) is not None:
            out.add(v.split(".", 1)[0])
    return out


def veto_holders(k, payload) -> dict:
    """{holder: {institutions it holds veto over that the payload names}}."""
    st = k.w.get(KEY)
    if not st or not st.get("instruments"):
        return {}
    named = named_institutions(k, payload)
    out = {}
    for n in named:
        for rec in instruments(k, n, status="active"):
            if live(k, rec):
                for g in rec["grants"]:
                    if g["power"] == "veto" and g["over"] == n and g["holder"] not in named:
                        out.setdefault(g["holder"], set()).add(n)
    return out


def veto_laws(k, payload, allv) -> list:
    """dispatch.hooks.bound_laws: the laws of veto holders over an institution the change names."""
    hold = veto_holders(k, payload)
    if not hold:
        return []
    return [l for l in allv if account(k, l["id"]) in hold]


def note_veto(k, P, payload, decision) -> None:
    """dispatch routing: a block by a veto holder's law is logged as a use of its veto."""
    hold = veto_holders(k, payload)
    if not hold:
        return
    for lid in decision.blocked_by:
        h = account(k, lid)
        if h in hold:
            for n in sorted(hold[h]):
                got = holds(k, h, n, "veto")
                _act(k, got[0] if got else None, "veto", h, n, lid, primitive=P.name,
                     **({"reason": decision.reason} if decision.reason else {}))


# ---------------------------------------------------------------------- land: tenures (loop 2)
def _fields_camp(k, camp):
    from cybertron import lawlang as L
    c = k.w["camps"].get(camp)
    if c is None or "plots" not in c:
        raise L.LawError(f"no fields camp {camp}")
    return c


def _plot(c, plot):
    for p in c.get("plots") or ():
        if str(p["id"]) == str(plot):
            return p
    return None


def _give(k, by, camp, holder, pid, to) -> None:
    from cybertron import dispatch as D
    from cybertron import lawlang as L
    try:
        out = k.apply("set_farm", agent=by, camp=camp, holder=holder, key="give", value={"plots": [pid], "to": to})
    except D.Blocked as e:
        raise L.LawError(f"a law blocked handing over plot {pid} ({', '.join(e.by)}" + (f": {e.why})" if e.why else ")"))
    if not out.ok:
        raise L.LawError(f"a law blocked handing over plot {pid}" + (f" ({out.reason})" if out.reason else ""))


def grant_plot_(k, grantor, camp, plot, to, service, lid) -> bool:
    from cybertron import lawlang as L
    c = _fields_camp(k, camp)
    p = _plot(c, plot)
    if p is None or p.get("holder") != grantor:
        raise L.LawError(f"{name(k, grantor)} holds no plot {plot} at {camp}")
    if to not in k.w["agents"] and not exists(k, to):
        raise L.LawError(f"no agent or institution {to}")
    terms = None
    if service is not None:
        if not isinstance(service, dict) or service.get("work") not in WORK:
            raise L.LawError(f"service: {{\"work\": one of {', '.join(WORK)}, \"qty\": n, \"every\": rounds}}")
        terms = {"work": service["work"], "qty": float(service.get("qty") or 1), "every": int(service.get("every") or 1),
                 "camp": service.get("camp")}
    _give(k, grantor, camp, grantor, p["id"], to)
    t = {"camp": camp, "plot": p["id"], "grantor": grantor, "grantee": to, "service": terms, "since": k.r, "law": lid,
         "status": "held"}
    state(k)["tenures"].append(t)
    k.log("tenure", None, {"what": "granted", **t}, vis="public")
    return True


def seize_plot_(k, by, camp, plot, lid) -> bool:
    from cybertron import lawlang as L
    c = _fields_camp(k, camp)
    p = _plot(c, plot)
    if p is None or not p.get("holder"):
        raise L.LawError(f"no held plot {plot} at {camp}")
    h = p["holder"]
    if h == by:
        raise L.LawError(f"{name(k, by)} already holds plot {plot}")
    ten = next((t for t in reversed(state(k)["tenures"]) if t["camp"] == camp and t["plot"] == p["id"] and t["status"] == "held"
                and t["grantor"] == by and t["grantee"] == h), None)
    got = None
    if ten is None:
        got = holds(k, by, h, "seize") if h not in k.w["agents"] else None
        if got is None:
            raise L.LawError(why_not(k, by, h, "seize") if h not in k.w["agents"] else
                             f"plot {plot} at {camp} is {h}'s own, not held of {name(k, by)}")
    _give(k, by, camp, h, p["id"], by)
    if ten is not None:
        ten["status"], ten["ended"] = "seized", k.r
    k.log("tenure", None, {"what": "seized", "camp": camp, "plot": p["id"], "grantor": by, "grantee": h, "law": lid}, vis="public")
    if got is not None:
        _act(k, got[0], "seize", by, h, lid, camp=camp, plot=p["id"])
    return True


# ---------------------------------------------------------------------- labour service (loop 4)
def _may_demand(k, inst, agent) -> bool:
    from cybertron import institutions as IN
    from cybertron import powers as PW
    if any(t["grantor"] == inst and t["grantee"] == agent and t["status"] == "held" for t in state(k)["tenures"]):
        return True
    try:
        return IN.is_member(k, inst, agent) and bool(PW.has_power(k, inst, "compel_members"))
    except KeyError:
        return False


def demand(k, inst, agent, work, qty, camp, rounds, lid) -> str:
    from cybertron import lawlang as L
    if agent not in k.w["agents"]:
        raise L.LawError(f"no agent {agent}")
    if work not in WORK:
        raise L.LawError(f"work is one of {', '.join(WORK)}, not {work!r}")
    if not _may_demand(k, inst, agent):
        raise L.LawError(f"{agent} owes {name(k, inst)} no service (neither a member it may compel nor a holder of its land)")
    q, n = float(qty), max(1, int(rounds))
    if q <= 0:
        raise L.LawError("qty: how many times, above 0")
    st = state(k)
    sid = f"W{len(st['services']) + 1}"
    st["services"][sid] = {"id": sid, "institution": inst, "agent": agent, "work": work, "qty": q,
                           "camp": None if camp is None else str(camp), "since": k.r, "due": k.r + n - 1, "done": 0.0,
                           "law": lid, "missed": False}
    k.log("service_demanded", None, {**st["services"][sid]}, vis=sorted({agent} | set(_audience(k, lid))))
    return sid


def service_status(k, s) -> str:
    if s["done"] + 1e-9 >= s["qty"]:
        return "done"
    return "missed" if k.r > s["due"] or s["missed"] else "open"


PRIM_WORK = {"harvest": "harvest", "sow": "sow", "tend": "tend", "reap": "reap"}


def after_change(k, name_, payload) -> None:
    """dispatch routing (flag on): a routed harvest, sow, tend or reap counts toward the agent's open service demands."""
    work = PRIM_WORK.get(name_)
    st = k.w.get(KEY)
    if work is None or not st or not st.get("services"):
        return
    a = payload.get("agent")
    for s in st["services"].values():
        if s["agent"] != a or s["work"] != work or service_status(k, s) != "open":
            continue
        if s["camp"] is not None and payload.get("camp") != s["camp"]:
            continue
        if work in ("sow", "tend", "reap"):
            c = k.w["camps"].get(payload.get("camp")) or {}
            p = _plot(c, payload.get("plot"))
            if p is None or p.get("holder") != s["institution"]:
                continue
        s["done"] = round(s["done"] + _labour(k, a), 6)
        break


def _labour(k, aid) -> float:
    """One action's work units: 37.1's labour(agent) (a minor's fraction) when the engine has it (cybertron.life.labour), else 1."""
    from cybertron import life as LF
    fn = getattr(LF, "labour", None)
    if not callable(fn):
        return 1.0
    try:
        return float(fn(k, aid))
    except Exception:                                                   # noqa: BLE001 (an older or different signature: one unit)
        return 1.0


def end_round(k) -> None:
    """Kernel round end (flag on): service demands past due and short are recorded as missed (the agent and the institution's
    law's audience told)."""
    st = k.w.get(KEY)
    if not on(k) or not st:
        return
    for s in st["services"].values():
        if not s["missed"] and s["done"] + 1e-9 < s["qty"] and k.r >= s["due"]:
            s["missed"] = True
            k.log("service_missed", None, {"service": s["id"], "institution": s["institution"], "agent": s["agent"],
                                           "work": s["work"], "qty": s["qty"], "done": s["done"]},
                  vis=sorted({s["agent"]} | set(_audience(k, s["law"]))))


# ---------------------------------------------------------------------- prompt lines (agents.state_view)
SHORT = {"read": "read records", "levy": "levy on treasury and stores", "pay": "pay out of treasury", "appoint": "appoint officers",
         "remove": "remove officers", "enact": "enact laws", "veto": "veto acts", "seize": "seize land"}


def _fmt_grant(g) -> str:
    v = SHORT[g["power"]]
    if g["power"] in LIMITED and g["qty"] is not None:
        per = "a round" if g["every"] == 1 else f"every {g['every']} rounds"
        v = ("levy" if g["power"] == "levy" else "pay out") + f" up to {g['qty']:g} {g['item'] or 'goods'} {per}"
    elif g["power"] in LIMITED and g["item"]:
        v += f" ({g['item']})"
    return v


def _sides(grants) -> str:
    """"J0 over A1: read records, levy up to 4 penny a round; A1 over J0: read records"."""
    out = {}
    for g in grants:
        out.setdefault((g["holder"], g["over"]), []).append(_fmt_grant(g))
    return "; ".join(f"{h} over {o}: {', '.join(v)}" for (h, o), v in out.items())


def _concerns(k, rec, aid) -> bool:
    from cybertron import institutions as IN
    for p in rec["parties"]:
        if aid in IN.officers(k, p):
            return True
        if p != "J0" and IN.is_member(k, p, aid):
            return True
    return False


def state_lines(k, aid) -> list:
    """One line per instrument in force (or on offer) that concerns the agent: an officer of either party, or a member of a party
    other than J0; tenures and service it owes."""
    st = k.w.get(KEY)
    if not st:
        return []
    out = []
    for rec in st["instruments"].values():
        if rec["status"] == "ended" or (rec["status"] == "active" and not live(k, rec)) or not _concerns(k, rec, aid):
            continue
        a, b = rec["parties"]
        title = f"{rec['kind'].capitalize()} {rec['id']}" + (f" '{rec['name']}'" if rec["name"] else "")
        head = f"{title} between {name(k, a)} and {name(k, b)}"
        sides = _sides(rec["grants"]) or "no powers"
        if rec["status"] == "offered":
            waits = [p for p in rec["parties"] if p not in rec["consent"]]
            out.append(f"{head}, offered by {rec['by']}. {sides}. In force once {', '.join(waits)} accepts by a law calling "
                       f"accept_instrument(\"{rec['id']}\").")
        else:
            out.append(f"{head}. {sides} (laws use these powers: read_law for the calls).")
    for t in st["tenures"]:
        if t["status"] == "held" and t["grantee"] == aid:
            sv = t["service"]
            out.append(f"You hold {t['camp']} plot {t['plot']} of {name(k, t['grantor'])}" +
                       (f", owing service when it demands: {sv['work']} {sv['qty']:g} time(s) "
                        + ("a round" if sv["every"] == 1 else f"every {sv['every']} rounds") if sv else "")
                       + "; it may take the plot back.")
    for s in st["services"].values():
        if s["agent"] == aid and service_status(k, s) == "open":
            where = f" at {s['camp']}" if s["camp"] else ""
            on_ = f" on {s['institution']}'s plots" if s["work"] in ("sow", "tend", "reap") else ""
            out.append(f"DUE: service to {name(k, s['institution'])}: {s['work']}{where}{on_} {s['qty'] - s['done']:g} more "
                       f"time(s) by the end of round {s['due'] + 1}.")
    return out


# ---------------------------------------------------------------------- events (rendered through contracts.render_event)
def render_event(k, e, tag, viewer=None) -> str | None:
    d, t = e["data"], e["type"]
    if t == "cross_instrument":
        what = {"offered": "was offered", "in force": "is in force", "ended": "ended"}.get(d["what"], d["what"])
        by = f" ({d['by']} ended it" + (f": {d['reason']}" if d.get("reason") else "") + ")" if d["what"] == "ended" and d.get("by") else ""
        gs = _sides(d["grants"])
        return f"{tag} {d['kind'].capitalize()} {d['instrument']} between {' and '.join(d['parties'])} {what}{by}" + (f": {gs}" if gs and d['what'] != "ended" else "")
    if t == "cross_act":
        p = d["power"]
        bits = {"levy": lambda: f"levied {d['qty']:g} {d['item']} from {d['over']}",
                "pay": lambda: f"paid {d['qty']:g} {d['item']} out of {d['over']}'s treasury to {d['to']}",
                "transfer": lambda: f"paid {d['qty']:g} {d['item']} into {d['over']}'s treasury",
                "appoint": lambda: f"appointed {d['agent']} to {d['over']}.{d['office']}",
                "remove": lambda: f"removed {d['agent']} from {d['over']}.{d['office']}",
                "enact": lambda: f"enacted {d['enacted']} in {d['over']}'s code",
                "read": lambda: f"read {d['over']}'s records",
                "veto": lambda: f"vetoed {d['over']}'s {d['primitive']}" + (f" ({d['reason']})" if d.get("reason") else ""),
                "seize": lambda: f"seized {d['camp']} plot {d['plot']} from {d['over']}"}.get(p, lambda: p)()
        via = f" under {d['instrument']}" if d.get("instrument") else ""
        return f"{tag} {d['holder']} {bits}{via} (law {d['law']})"
    if t == "cross_refused":
        return f"{tag} Refused: law {d['law']} of {d['holder']} ({d['fn']}): {d['why']}"
    if t == "tenure":
        if d["what"] == "granted":
            sv = d.get("service")
            return (f"{tag} {d['grantor']} granted {d['camp']} plot {d['plot']} to {d['grantee']}" +
                    (f", for service ({sv['work']} {sv['qty']:g} time(s) "
                     + ("a round)" if sv["every"] == 1 else f"every {sv['every']} rounds)") if sv else ""))
        return f"{tag} {d['grantor']} took back {d['camp']} plot {d['plot']} from {d['grantee']}"
    if t == "service_demanded":
        return (f"{tag} {d['institution']} demands service of {d['agent']}: {d['work']}" + (f" at {d['camp']}" if d.get("camp") else "")
                + f" {d['qty']:g} time(s) by the end of round {d['due'] + 1} ({d['id']})")
    if t == "service_missed":
        return f"{tag} {d['agent']} did not render the service {d['service']} owed to {d['institution']} ({d['done']:g} of {d['qty']:g})"
    return None
