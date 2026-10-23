"""What an agent's code may see (D4-35, spec/core/architecture.md): `Here`, a view of the node the agent stands at with its own body
and hands, and `Mind`, what it knows. The verbs, knowledge views, perception and prompts are given these and nothing else; they have
no reference to the world (a test reads their source).

Here acts only through the chokepoint at its own node: `here.apply(primitive, ...)` is `w.apply(primitive, node, ...)`, so a
primitive that touches anything elsewhere fails as an engine fault.
"""
from __future__ import annotations

from cybertron2.engine.world import CONDITION, STAGES, Refused, show  # noqa: F401  (re-exported for the agent-facing modules)


class Here:
    def __init__(self, w, name):
        self._w = w
        self.name = name
        self.node = w.at(name)
        if self.node is None:
            raise Refused(f"{name} is on the road")

    # ------------------------------------------------------------------ time and rules
    @property
    def day(self):
        return self._w.d

    @property
    def p(self):
        return self._w.p

    def calendar(self, day=None):
        return self._w.calendar(day)

    def cold(self, day=None):
        return self._w.cold(day)

    def rng(self, *parts):
        return self._w.rng(*parts)

    @property
    def node_name(self):
        return self._w.s["nodes"][self.node]["name"]

    def road_to(self, x):
        """(node id, days) for a neighbouring node named x, else None. Roads from here are part of the place."""
        x = str(x or "").strip().lower().removeprefix("the ")
        for r in self._w.s["roads"].values():
            if self.node in (r["a"], r["b"]):
                other = r["b"] if r["a"] == self.node else r["a"]
                if x in (other.lower(), self._w.s["nodes"][other]["name"].lower()):
                    return other, r["days"]
        return None

    def roads(self) -> list:
        """[(node id, name, days)] from here."""
        out = []
        for r in self._w.s["roads"].values():
            if self.node in (r["a"], r["b"]):
                other = r["b"] if r["a"] == self.node else r["a"]
                out.append((other, self._w.s["nodes"][other]["name"], r["days"]))
        return sorted(out, key=lambda x: x[1])

    # ------------------------------------------------------------------ me
    @property
    def me(self) -> dict:
        return self._w.s["people"][self.name]

    @property
    def hands(self) -> str:
        return self.me["hands"]

    def carried(self) -> dict:
        return dict(self._w.goods(self.hands))

    def wear(self, cid=None) -> dict:
        return dict(self._w.s["containers"][cid or self.hands]["wear"])

    def load(self) -> float:
        return self._w.load(self.name)

    def units(self) -> int:
        return self._w.units_for(self.name)

    def yield_mult(self) -> float:
        return self._w.yield_mult(self.name)

    def best_tool(self, table):
        return self._w.best_tool(self.name, table)

    def weapon(self):
        return self._w.weapon(self.name)

    # ------------------------------------------------------------------ who and what is here
    def people(self, me=True) -> list:
        return [x for x in self._w.present(self.node) if me or x != self.name]

    def person(self, x):
        """A living person here, by name, else None."""
        x = str(x or "").strip().lower()
        return next((n for n in self.people() if n.lower() == x), None)

    def hands_of(self, x) -> str:
        if x not in self.people():
            raise Refused(f"{x} is not here")
        return self._w.s["people"][x]["hands"]

    def body(self, x) -> dict:
        """What can be seen of someone here: stage, hunger, wounds, what they carry."""
        if x not in self.people():
            raise Refused(f"{x} is not here")
        a = self._w.s["people"][x]
        return {"stage": a["stage"], "hunger": a["hunger"], "wounded": a["wounded"], "carried": dict(self._w.goods(a["hands"]))}

    def buildings(self) -> dict:
        return {bid: b for bid, b in self._w.s["buildings"].items() if b["node"] == self.node}

    def building(self, x):
        x = str(x or "").strip().lower().removeprefix("the ").removeprefix("my ").removeprefix("your ")
        for bid, b in self.buildings().items():
            nm = b["name"].lower()
            if x in (bid.lower(), nm, nm.removeprefix("the ")):
                return bid
        hh = {iid: h for iid, h in self._w.s["institutions"].items() if h["kind"] == "household"}
        for iid, h in hh.items():                                             # "the Fenns" or "Fenn": that household's house here
            if x in (iid.lower(), iid.lower() + "s", h["name"].lower(), h["name"].lower().removeprefix("the ")):
                hb = [bid for bid in self.buildings() if any(c["claimant"] == iid for c in self._w.claims_on(("building", bid)))]
                if hb:
                    return hb[0]
        return None

    def parcels(self) -> dict:
        return {pid: p for pid, p in self._w.s["parcels"].items() if p["node"] == self.node}

    def parcel(self, x):
        x = str(x or "").strip().lower()
        for pid, p in self.parcels().items():
            if x in (pid.lower(), p["name"].lower(), p["name"].lower().removeprefix("the ")):
                return pid
        return None

    def herds(self) -> dict:
        return {hid: h for hid, h in self._w.s["herds"].items() if h["node"] == self.node}

    def herd(self, x=None):
        hs = self.herds()
        x = str(x or "").strip().lower()
        return next((hid for hid, h in hs.items() if not x or x in (hid.lower(), h["name"].lower(), h["kind"], "cattle", "the herd", "herd")), None)

    def fittings(self, kind) -> list:
        """Buildings here with this fitting that the agent can get into."""
        return [bid for bid, b in self.buildings().items() if not b.get("unfinished") and b["fittings"].get(kind)
                and self._w.can_enter(self.name, bid)]

    def stock(self, bid) -> dict:
        return dict(self._w.goods(self.buildings()[bid]["stock"]))

    def remains(self) -> dict:
        return {cid: c for cid, c in self._w.s["containers"].items() if c["kind"] == "remains" and c["node"] == self.node
                and any(q > 1e-9 for q in c["goods"].values())}

    def offers(self) -> dict:
        return {oid: o for oid, o in self._w.s["offers"].items() if o["node"] == self.node and o["open"]}

    def offer(self, oid) -> dict:
        o = self._w.s["offers"][oid]
        if o["node"] != self.node:
            raise Refused(f"offer {oid} is not here")
        return o

    def contents(self, cid) -> dict:
        """What is in a container here (hands of someone here, a store here)."""
        if self._w.place_of(("container", cid)) != self.node:
            raise Refused("that is not here")
        return dict(self._w.goods(cid))

    def events(self) -> list:
        return [e for e in self._w.s["events"] if e["place"] == self.node]

    def acts_today(self) -> list:
        return [a for a in self._w.s["acts"] if a["day"] == self.day and a["node"] == self.node]

    # ------------------------------------------------------------------ rights here (D4-23)
    def rights(self, thing, who=None) -> set:
        return self._w.rights(who or self.name, thing)

    def may_grant(self, thing) -> bool:
        return self._w.may_grant(self.name, thing)

    def claims(self, thing) -> list:
        return self._w.claims_on(thing)

    def claim_records(self, thing) -> list:
        thing = tuple(thing)
        return [(cid, c) for cid, c in self._w.s["claims"].items() if tuple(c["thing"]) == thing
                and (c.get("until") is None or c["until"] >= self.day)]

    def takeable(self, who=None) -> list:
        return self._w.takeable(who or self.name, self.node)

    def may_take(self, cid, who=None) -> bool:
        return self._w.may_take(who or self.name, cid)

    def can_enter(self, bid, who=None) -> bool:
        return self._w.can_enter(who or self.name, bid)

    def homes_here(self, who=None) -> list:
        return [b for b in self._w.homes(who or self.name) if self._w.s["buildings"][b]["node"] == self.node]

    def household(self, who=None):
        return self._w.household_of(who or self.name)

    def institution(self, iid) -> dict:
        return self._w.s["institutions"][iid]

    def households(self) -> dict:
        return {iid: h for iid, h in self._w.s["institutions"].items() if h["kind"] == "household"}

    def head(self, iid):
        return self._w.head(iid)

    def party_container(self, party):
        """The container here that acting for a party fills or draws on (D2-37): a person's hands, or the stock of a building here
        its household holds."""
        if party in self.people():
            return self._w.s["people"][party]["hands"]
        for bid, b in self.buildings().items():
            if any(c["claimant"] == party and "withdrawal" in c["rights"] for c in self._w.claims_on(("building", bid))):
                return b["stock"]
        return None

    def household_name(self, bid):
        return _household_name(self._w, bid)

    def born_trades(self) -> set:
        return _born_trades(self._w, self.node)

    def agreements(self, who=None) -> dict:
        who = who or self.name
        hh = self._w.household_of(who)
        return {aid: a for aid, a in self._w.s["agreements"].items() if who in a["parties"] or hh in a["parties"]}

    # ------------------------------------------------------------------ acting, at this node only
    def apply(self, prim, **kw):
        return self._w.apply(prim, self.node, **kw)

    def event(self, kind, text, **kw):
        return self._w.event(self.node, kind, text, **kw)

    def record(self, verb, tech=None, for_=None, **extra):
        self._w.record(self.name, verb, tech, for_, self.node, **extra)

    def cause(self, verb, for_=None):
        return self._w.cause(actor=self.name, verb=verb, for_=for_, node=self.node)

    def new_offer(self, rec) -> str:
        return self.apply("offer", by=self.name, rec=rec)

    def new_agreement(self, rec) -> str:
        return self.apply("agree", node=self.node, rec=rec)

    def today(self) -> dict:
        return self._w.s["today"]


def _household_name(w, bid):
    hh = next((c["claimant"] for c in w.claims_on(("building", bid)) if c["claimant"] in w.s["institutions"]
               and "alienation" in c["rights"]), None)
    return w.s["institutions"][hh]["name"] if hh else None


def _born_trades(w, node) -> set:
    """The trades of the lines born at a node (D4-33: its repute), from those whose home is there."""
    from cybertron2.engine.data import TECHNIQUES
    out = set()
    for x, a in w.s["people"].items():
        hh = w.household_of(x)
        if not a["alive"] or not hh or a.get("born_line") != hh:
            continue
        if not any(w.s["buildings"][b]["node"] == node for b in w.homes(x)):
            continue
        out |= {t for t, r in w.s["know"].get(x, {}).items() if r["level"] == "known" and not TECHNIQUES[t].get("basic")}
    return out


class NodeView:
    """A read view of one node for seeding what people know of places (engine side only; agents never get one)."""

    def __init__(self, w, node):
        self._w, self.node = w, node

    def parcels(self):
        return {k: v for k, v in self._w.s["parcels"].items() if v["node"] == self.node}

    def buildings(self):
        return {k: v for k, v in self._w.s["buildings"].items() if v["node"] == self.node}

    def herds(self):
        return {k: v for k, v in self._w.s["herds"].items() if v["node"] == self.node}

    def household_name(self, bid):
        return _household_name(self._w, bid)

    def born_trades(self):
        return _born_trades(self._w, self.node)


class Mind:
    """What one person knows: its knowledge of crafts, its memory and beliefs, its notes, its kin and places as it knows them. It
    is the agent's own; reading it never reads the world."""

    def __init__(self, w, name):
        self.name = name
        self.know = w.s["know"].setdefault(name, {})
        self.store = w.s["mind"][name]
        self.person = w.s["people"][name]
        self._cal = w.calendar
        self.day = w.d
        self.p = w.p
        self.household = w.household_of(name)
        h = w.s["institutions"].get(self.household) if self.household else None
        self.household_name = h["name"] if h else None
        self.members = [m for m in (h["members"] if h else []) if m != name]   # one knows who belongs to one's household
        self.head = h["offices"].get("head") if h else None

    def calendar(self, day=None):
        return self._cal(self.day if day is None else day)

    @property
    def notes(self) -> dict:
        return self.person["notes"]

    def kin(self) -> dict:
        return self.store.get("kin", {})

    def places(self) -> dict:
        return self.store.get("places", {})

    def home_seen(self):
        return self.person.get("home_seen")
