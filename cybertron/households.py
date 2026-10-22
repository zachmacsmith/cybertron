"""Households (37.1, docs/review/37_growth/01_demography.md, devlog_37.1.md): minimal institutions a family runs, so that laws and
other institutions can address a family like any institution. Spec `life.households`, off by default: with it off nothing here
writes state or adds a word to a prompt. Needs two-parent reproduction (pairs or both) and contracts.

A household is an association (contracts.py) running the library's Household template: members put what they allow above KEEP
food into a common pot, and the pot feeds members and their minor children who are short of a meal. It is founded automatically:

  at a birth (pairs.birth), the child joins its parents' household when they share one; else the household a parent heads (the
  initiator's first); else a new one, "<initiator>'s household", headed by the initiator, with both parents and the child as
  members. A parent who moves leaves its old household (at the end of the round, through the template's after_leave, which hands
  back part of what it put in).

The head is recorded here (k.w["life"]["households"]["head"]) and passes at the head's death: to a member who is a co-parent of the
dead head, else the eldest adult member, else the eldest member (life.age). A household whose last member leaves or dies is
wound up by contracts.end_round like any memberless association.

Reads (law API, documented in household worlds): households() -> [{id, name, head, members [{agent, age}], pot (food in its
treasury), plots [{camp, plot}] (plots whose holder is its id)}], household_of(agent) -> id or None.

State, k.w["life"]["households"]: of {agent: id}, head {id: agent}, ids [id, ...] (founding order).
"""
from __future__ import annotations

from cybertron import mortality as MO

FOOD = "food"


def cfg(spec) -> dict:
    from cybertron import life as LF
    return dict(LF.DEFAULTS["households"], **(((spec or {}).get("life") or {}).get("households") or {}))


def spec_on(spec) -> bool:
    from cybertron import pairs as PR
    return bool(cfg(spec).get("enabled")) and PR.pairs_spec(spec)


def on(k) -> bool:
    return k is not None and "households" in (k.w.get("life") or {})


def state(k) -> dict:
    return k.w["life"]["households"]


def install(k) -> None:
    """life.install, after pairs: the empty roster. Households need contracts (they are associations)."""
    from cybertron import features as FT
    if not FT.on("contracts", k.spec):                                   # (contracts installs after life)
        raise ValueError("life.households needs contracts.enabled (a household is an association)")
    k.w["life"]["households"] = {"of": {}, "head": {}, "ids": []}


# ---------------------------------------------------------------------- reads
def _rec(k, iid):
    from cybertron import contracts as KC
    return KC.recs(k).get(iid)


def _active(k, iid) -> bool:
    rec = _rec(k, iid)
    return rec is not None and rec.get("status", "active") != "dissolved"


def household_of(k, aid):
    """The household aid belongs to (None: none, or households off)."""
    if not on(k):
        return None
    iid = state(k)["of"].get(aid)
    if iid is None or not _active(k, iid) or aid not in _rec(k, iid)["members"]:
        return None
    return iid


def head_of(k, iid):
    return state(k)["head"].get(iid) if on(k) else None


def members(k, iid) -> list:
    rec = _rec(k, iid)
    return [m for m in (rec or {}).get("members", []) if MO.alive(k, m)]


def pot_of(k, aid):
    """The owner key of aid's household pot (its treasury), or None."""
    iid = household_of(k, aid)
    return _rec(k, iid)["treasury"] if iid else None


def plots_of(k, iid) -> list:
    if "subsistence" not in k.w:
        return []
    from cybertron import subsistence as SB
    return [{"camp": cid, "plot": p["id"]} for cid in SB.fields_camps(k) for p in k.w["camps"][cid].get("plots") or []
            if p.get("holder") == iid]


def roster(k) -> list:
    """The household roster (board contract A): every active household with its head, members and ages, pot and plots."""
    from cybertron import life as LF
    if not on(k):
        return []
    out = []
    for iid in state(k)["ids"]:
        if not _active(k, iid):
            continue
        rec = _rec(k, iid)
        out.append({"id": iid, "name": rec["name"], "head": head_of(k, iid),
                    "members": [{"agent": m, "age": LF.age(k, m)} for m in members(k, iid)],
                    "pot": round(float(k.bal(rec["treasury"], FOOD)), 6), "plots": plots_of(k, iid)})
    return out


# ---------------------------------------------------------------------- founding and joining
def _code(k) -> str:
    from cybertron import library as LB
    c = cfg(k.spec)
    return LB.instantiate("Household", {"KEEP": float(c["keep"])})


def found(k, head, others) -> str | None:
    """A new household headed by `head`, with `others` as members (a world founding: the founder's contract limit does not apply)."""
    from cybertron import contracts as KC
    st = state(k)
    iid = f"A{k.w['contracts']['seq'] + 1}"
    name = str(cfg(k.spec)["name"]).format(head=head)[:60]
    with k.cause("world", "household", root=False):
        out = k.apply("create_contract", agent=head, contract=iid, name=name, template=None, code=[_code(k)], params={},
                      admission="closed")
    if not out.ok:
        return None
    rec = KC.recs(k)[iid]
    rec["household"] = True
    st["ids"].append(iid)
    st["head"][iid] = head
    _move_in(k, head, iid)
    for x in others:
        join(k, x, iid)
    k.log("household", head, {"household": iid, "op": "founded", "head": head, "members": [head, *others]}, vis="monitor")
    for x in [head, *others]:
        if MO.alive(k, x):
            k.notify(x, f"{name} ({iid}) is founded: {head} heads it; its members are {', '.join([head, *others])}. Members put "
                        f"food above {cfg(k.spec)['keep']:g} of their own into its pot (set_allowance on food to {iid}), and the "
                        "pot feeds members and their children who are short of a meal.")
    return iid


def _move_in(k, aid, iid) -> None:
    """aid's household is now iid; it leaves its old one (a request, made good at the end of the round)."""
    st = state(k)
    old = household_of(k, aid)
    st["of"][aid] = iid
    if old and old != iid:
        k.apply("leave", agent=aid, polity=old, via="leave")


def join(k, aid, iid) -> None:
    rec = _rec(k, iid)
    if aid not in rec["members"]:
        k.apply("join", agent=aid, polity=iid, via="household")
    _move_in(k, aid, iid)


def on_birth(k, child, a, b) -> None:
    """pairs.birth: the child's household (and its parents', when it is new)."""
    if not on(k):
        return
    ha, hb = household_of(k, a), household_of(k, b)
    if ha and ha == hb:
        join(k, child, ha)
        return
    for p, h, other in ((a, ha, b), (b, hb, a)):
        if h and head_of(k, h) == p:
            join(k, other, h)
            join(k, child, h)
            return
    found(k, a, [b, child])


# ---------------------------------------------------------------------- the head
def _next_head(k, iid, dead):
    from cybertron import life as LF
    from cybertron import pairs as PR
    living = [m for m in members(k, iid) if m != dead]
    if not living:
        return None
    co = [m for m in living if m in LF.coparents(k, dead)]
    if co:
        return sorted(co, key=lambda m: (-(LF.age(k, m) or 0), m))[0]
    adults = [m for m in living if not PR.is_minor(k, m)] or living
    return sorted(adults, key=lambda m: (-(LF.age(k, m) or 0), m))[0]


def after_death(k, aid) -> None:
    """life.after_death: a dead head's household passes to the next head."""
    if not on(k):
        return
    st = state(k)
    for iid, h in sorted(st["head"].items()):
        if h != aid or not _active(k, iid):
            continue
        nh = _next_head(k, iid, aid)
        st["head"][iid] = nh
        took = _take_seat_model(k, nh, aid) if nh else None
        k.log("household", nh, {"household": iid, "op": "head", "head": nh, "from": aid, **({"model": took} if took else {})},
              vis="monitor")
        for m in members(k, iid):
            if m != aid:
                k.notify(m, f"{aid}, head of {_rec(k, iid)['name']} ({iid}), is gone; " + (
                    f"{nh} heads it now." if nh else "it has no head."))


_RANK = (("opus", 3), ("sonnet", 2), ("haiku", 1))


def _model_rank(k, model) -> int:
    from cybertron import life as LF
    s = str(model or "").lower()
    for name, r in _RANK:
        if name in s:
            return r
    return {"strong": 3, "mid": 2, "weak": 1}.get(LF._tier_of(k, model), 1)


def _take_seat_model(k, heir, dead):
    """life.households.head_model inherit (scenario_design §2: never drift to all-Haiku): a new head takes the dead head's model
    when it is stronger than its own (the seat carries the model). Returns the model taken, or None."""
    if str(cfg(k.spec).get("head_model") or "keep") != "inherit":
        return None
    a = next((x for x in k.inst["agents"] if x["id"] == heir), None)
    d = next((x for x in k.inst["agents"] if x["id"] == dead), None)
    if a is None or d is None or _model_rank(k, d.get("model")) <= _model_rank(k, a.get("model")):
        return None
    from cybertron import life as LF
    a["model"] = d["model"]
    if "tier" in a:
        a["tier"] = LF._tier_of(k, d["model"])
    return d["model"]


# ---------------------------------------------------------------------- inheritance (board loop 2)
def inheritance(spec) -> str:
    """life.households.inheritance: none (as before: the first living child, else a co-parent, else the polity) | partible | eldest |
    household. Read whenever pairs reproduction is on, with or without households."""
    from cybertron import pairs as PR
    return str(cfg(spec).get("inheritance") or "none") if PR.pairs_spec(spec) else "none"


def _eldest_first(k, xs) -> list:
    from cybertron import life as LF
    return sorted(xs, key=lambda m: (-(LF.age(k, m) or 0), m))


def heirs(k, aid):
    """Who takes a dead holder's plots under the inheritance rule, eldest first: partible every living child, eldest the oldest,
    household its household (when it has one; else as eldest). None: the rule is none or nobody fits (the old path decides)."""
    from cybertron import life as LF
    rule = inheritance(k.spec)
    if rule == "none" or "life" not in k.w:
        return None
    if rule == "household":
        iid = household_of(k, aid)
        if iid is None:                                                  # (the dead are no longer members: the record keeps it)
            iid = state(k)["of"].get(aid) if on(k) else None
            iid = iid if iid and _active(k, iid) and members(k, iid) else None
        if iid:
            return [iid]
    kids = _eldest_first(k, [c for c in LF.children(k, aid) if MO.alive(k, c)])
    if not kids:
        return None
    return kids if rule == "partible" else kids[:1]


# ---------------------------------------------------------------------- prompts and truth
def state_lines(k, aid) -> list:
    iid = household_of(k, aid)
    if not iid:
        return []
    rec = _rec(k, iid)
    h = head_of(k, iid)
    ms = members(k, iid)
    return [f"Your household: {rec['name']} ({iid}), head {h if h != aid else 'you'}; members "
            f"{', '.join(m for m in ms)}; pot {float(k.bal(rec['treasury'], FOOD)):.3g} food."]


def truth(k) -> dict:
    if not on(k):
        return {}
    import copy
    return {"households": copy.deepcopy(state(k))}
