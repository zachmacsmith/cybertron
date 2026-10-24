"""What an agent's code may see (D4-35, spec/core/architecture.md): `Here`, a view of the node the agent stands at with its own body
and hands, and `Mind`, what it knows. The verbs, knowledge views, perception and prompts are given these and nothing else; they have
no reference to the world (a test reads their source).

Here acts only through the chokepoint at its own node: `here.apply(primitive, ...)` is `w.apply(primitive, node, ...)`, so a
primitive that touches anything elsewhere fails as an engine fault.
"""
from __future__ import annotations

from cybertron2.engine.world import CONDITION, STAGES, Refused, show  # noqa: F401  (re-exported for the agent-facing modules)


class Here:
    def __init__(self, w, name, transit=False):
        self._w = w
        self.name = name
        self.node = w.at(name)
        if self.node is None and not transit:                                  # on the road: only for an urgent call (D2-81)
            raise Refused(f"{name} is on the road")
        self.place = self.node if self.node is not None else w.place_of(("person", name))   # a node, or the road one is on

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

    def year_days(self) -> int:
        return self._w.year_days()

    @property
    def node_name(self):
        return self._w.s["nodes"][self.node]["name"]

    def road_to(self, x):
        """(node id, days, track) for a neighbouring place named x, or an unexplored way described as x, else None."""
        x = str(x or "").strip().lower().removeprefix("the ")
        for other, nm, days, track in self.roads():
            nm = nm.lower()
            if x and (x in (other.lower(), nm, nm.removeprefix("the "), nm.removeprefix("an ")) or (len(x) > 6 and x in nm)):
                return other, days, track
        return None

    def roads(self) -> list:
        """[(node id, name, days, track)] from here; a place one does not know is named by its way (D4-47)."""
        out = []
        from cybertron2.engine import layout as LY
        for rid, r in self._w.s["roads"].items():
            if self.node in (r["a"], r["b"]) and LY.way_known(self._w, self.name, rid, self.node):   # a hidden end: only if known (D2-90)
                other = r["b"] if r["a"] == self.node else r["a"]
                nm = self._w.s["nodes"][other]["name"] if self._w.knows_place(self.name, other) else r.get("way", "an unexplored way")
                out.append((other, nm, r["days"], r.get("track", False)))
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

    def capacity(self, track=False, oxen=None) -> float:
        return self._w.capacity(self.name, track, oxen)

    def pack_ox(self, want=None):
        """A herd of one's household here with an ox one could lead as a pack ox (one must carry a harness), else None (D2-136)."""
        from cybertron2.engine import herds as HD
        return HD.pack_ox_for(self._w, self.name, want)

    def led(self) -> list:
        """The beasts one is leading, here with one (D2-136): [(id, name, oxen)]."""
        from cybertron2.engine import herds as HD
        return [(hid, self._w.s["herds"][hid]["name"], int(self._w.s["herds"][hid].get("oxen", 0))) for hid in HD.led_by(self._w, self.name)]

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
        """Who is here: at the node, or on the road one's party and whoever one meets (D2-120)."""
        return [x for x in self._w.company(self.name) if me or x != self.name]

    def person(self, x):
        """A living person here, by name, else None."""
        x = str(x or "").strip().lower()
        return next((n for n in self.people() if n.lower() == x), None)

    def someone(self, x):
        """A living person anywhere, by name (for a give that cannot reach them: D2-111), else None."""
        x = str(x or "").strip().lower()
        return next((n for n in self._w.living() if n.lower() == x), None)

    def hands_of(self, x) -> str:
        if x not in self.people():
            raise Refused(f"{x} is not here")
        return self._w.s["people"][x]["hands"]

    def body(self, x) -> dict:
        """What can be seen of someone here: stage, hunger, wounds, what they carry."""
        if x not in self.people():
            raise Refused(f"{x} is not here")
        a = self._w.s["people"][x]
        from cybertron2.engine import life as LF
        return {"stage": a["stage"], "hunger": a["hunger"], "wounded": a["wounded"], "carried": dict(self._w.goods(a["hands"])),
                "sex": a.get("sex", ""), "with_child": LF.showing(self._w, x), "partner": a.get("partner"),
                "parents": list(a.get("parents") or []), "cared": dict(a.get("cared") or {}),
                "grows": LF.grows_in(self._w, x)}

    def children_on(self) -> bool:
        from cybertron2.engine import life as LF
        return LF.on(self._w)

    def life(self) -> dict:
        """The world's life settings, for the verbs: the cost dial, whether children come, the spans (D2-145, D2-153)."""
        from cybertron2.engine import life as LF
        inst = self._w.s["institutions"].get(self.household() or "", {})
        return {"on": LF.on(self._w), "dial": LF.dial(self._w), "gap": LF.in_gap(self._w, self.name), "succession": inst.get("succession"),
                "order": inst.get("order"), "heir": inst.get("heir")}

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
        return {oid: o for oid, o in self._w.s["offers"].items() if o["node"] == self.place and o["open"]
                and (self.node is not None or o["by"] in self.people())}

    def offer(self, oid) -> dict:
        o = self._w.s["offers"][oid]
        if o["node"] != self.place:
            raise Refused(f"offer {oid} is not here")
        return o

    def contents(self, cid) -> dict:
        """What is in a container here (hands of someone here, a store here)."""
        if self._w.place_of(("container", cid)) != self.place:
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

    def dwellings_here(self, who=None) -> list:
        return [b for b in self._w.dwellings(who or self.name) if self._w.s["buildings"][b]["node"] == self.node]

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

    def layout(self) -> list:
        """How the village fits together, in words (D2-116): parcels with neighbours, side and height; where the roads leave."""
        from cybertron2.engine import layout as LY
        return LY.layout_lines(self._w, self.name)

    def overview(self) -> list:
        """What strikes one first here: 3 to 5 lines (D2-116)."""
        from cybertron2.engine import layout as LY
        return LY.overview(self._w, self.node)

    def landmarks_known(self, nid) -> list:
        """The landmarks one knows on the road from here to `nid` (world/roads.md)."""
        r = next((rid for rid, x in self._w.s["roads"].items() if {x["a"], x["b"]} == {self.node, nid}), None)
        lm = self._w.s["mind"][self.name].get("landmarks") or {}
        return [f"{v['words']} (crossed {v['crossed']} time{'s' if v['crossed'] != 1 else ''})" for v in lm.values() if v.get("road") == r]

    def weather_words(self, day=None) -> str:
        from cybertron2.engine import environment as EV
        return EV.words(self._w, day)

    def house_of(self, party):
        """A person's or a household's house here (where a give that cannot reach them is left at the door: D2-111)."""
        hh = self._w.s["institutions"].get(party)
        members = hh["members"] if hh else [party] if party in self._w.s["people"] else []
        for bid in self.buildings():
            if any(bid in self._w.homes(m) for m in members):
                return bid
        return None

    # ------------------------------------------------------------------ things at a spot (world/things_in_places.md)
    def things(self) -> dict:
        from cybertron2.engine import things as TH
        return TH.at_node(self._w, self.node)

    def thing(self, cid) -> dict:
        c = self._w.s["containers"].get(cid)
        return c if c and c.get("node") == self.node else None

    def bodies(self) -> dict:
        from cybertron2.engine import things as TH
        return TH.bodies(self._w, self.node)

    def spot_name(self, c) -> str:
        from cybertron2.engine import things as TH
        return TH.parcel_name(self._w, c)

    def bury_units(self, cid, cairn=False) -> int:
        from cybertron2.engine import things as TH
        return TH.bury_units(self._w, cid, cairn)

    def find_thing(self, where, item=None):
        from cybertron2.engine import things as TH
        return TH.find(self._w, self.name, where, item)

    def remember_thing(self, cid, how) -> None:
        from cybertron2.engine import things as TH
        TH.remember(self._w, self.name, cid, how)

    def known_things(self) -> dict:
        from cybertron2.engine import things as TH
        return {cid: (r, self.thing(cid)) for cid, r in TH.known_here(self._w, self.name, self.node).items()}

    def living_in(self, bid) -> list:
        return [m for m in self._w.living() if bid in self._w.homes(m)]

    def household_name(self, bid):
        return _household_name(self._w, bid)

    def born_trades(self) -> set:
        return _born_trades(self._w, self.node)

    def agreements(self, who=None) -> dict:
        who = who or self.name
        hh = self._w.household_of(who)
        return {aid: a for aid, a in self._w.s["agreements"].items() if who in a["parties"] or hh in a["parties"]}

    def works_for(self, party) -> bool:
        """An open agreement in which I (or my household) owe work to this party (D2-36 to D2-38: the worker acts for the employer)."""
        def circle(x):                                                        # a person and their household, or a household and its members
            if x in self._w.s["people"]:
                return {x, self._w.household_of(x)}
            return {x} | set((self._w.s["institutions"].get(x) or {}).get("members", []))
        mine, theirs = circle(self.name), circle(party)
        return any(a["status"] == "open" and "work" in l and l["done"] < l["work"] and l["from"] in mine and l["to"] in theirs
                   for a in self.agreements().values() for l in a["legs"])

    # ------------------------------------------------------------------ acting, at this node only
    def apply(self, prim, **kw):
        return self._w.apply(prim, self.place, **kw)

    def event(self, kind, text, **kw):
        return self._w.event(self.place, kind, text, **kw)

    def record(self, verb, tech=None, for_=None, **extra):
        self._w.record(self.name, verb, tech, for_, self.place, **extra)

    def cause(self, verb, for_=None):
        return self._w.cause(actor=self.name, verb=verb, for_=for_, node=self.place)

    def new_offer(self, rec) -> str:
        return self.apply("offer", by=self.name, rec=rec)

    def new_agreement(self, rec) -> str:
        return self.apply("agree", node=self.place, rec=rec)

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
        self.memory_mode = (w.spec.get("memory") or {}).get("mode", "append")   # memory.py
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
