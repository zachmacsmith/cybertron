"""Short tags and names for things one can act on that have no unique name of their own (proposals/referent_tags.md, D4-68).

A world turns this on with `tags: true`. Groups of beasts get H1, H2, ... and things lying at a spot (piles, packs, remains,
carcasses) T1, T2, ..., given when the thing comes to be and shown in brackets wherever it is named, the same for everyone. The
verbs take a tag wherever they take a name. People, places, parcels and buildings keep their names; goods are quantities.

Naming: `name {thing: H4, as: "Old Brock"}`. A name is knowledge, not a property of the thing: it is known to the one who gave it,
to everyone at the place when it was given, and to the namer's household. Those who know it see "(H4: Old Brock)" where others see
"(H4)", and their verbs accept the name.
"""
from __future__ import annotations

import re

TAG = re.compile(r"\b([HT])(\d{1,4})\b", re.I)


def on(w) -> bool:
    return bool((w.spec or {}).get("tags"))


def give(w, kind: str) -> str:
    """The next tag of a kind ("H" or "T"), counted in the world's state."""
    t = w.s.setdefault("tag_seq", {})
    t[kind] = int(t.get(kind, 0)) + 1
    return f"{kind}{t[kind]}"


def label(name: str, tag: str | None) -> str:
    return f"{name} ({tag})" if tag else name


def strip(name: str) -> str:
    """A name without its tag."""
    return re.sub(r"\s*\([HT]\d{1,4}(:[^)]*)?\)\s*$", "", str(name or ""))


def herds_at_start(w) -> None:
    """Tags for the herds a world starts with, in a fixed order; each herd's name carries its tag."""
    if not on(w):
        return
    for hid in sorted(w.s["herds"]):
        h = w.s["herds"][hid]
        if h.get("tag"):
            continue
        h["tag"] = give(w, "H")
        h["base_name"] = h.get("base_name") or h["name"]
        h["name"] = label(h["name"], h["tag"])


def new_herd(w, hid: str) -> None:
    """A herd that has just come to be (split off, driven apart, an ox led away): its own tag and its name with it."""
    if not on(w):
        return
    h = w.s["herds"][hid]
    h["tag"] = give(w, "H")
    h["name"] = label(strip(h["name"]), h["tag"])


def renamed_herd(w, hid: str) -> None:
    """After a herd's name is set anew (an ox led away), put its tag back on it."""
    h = w.s["herds"][hid]
    if on(w) and h.get("tag") and not str(h["name"]).endswith(f"({h['tag']})"):
        h["name"] = label(strip(h["name"]), h["tag"])


def new_thing(w, cid: str) -> None:
    if on(w):
        w.s["containers"][cid]["tag"] = give(w, "T")


def tag_in(text) -> str | None:
    m = TAG.search(str(text or ""))
    return m.group(1).upper() + m.group(2) if m else None


# ---------------------------------------------------------------------- names: knowledge of who calls what by which name
def names_of(w, person) -> dict:
    """{tag: name} this person knows."""
    return (w.s["mind"].get(person) or {}).get("names") or {}


def _learn(w, person, tag, name) -> None:
    if person in w.s["mind"]:
        w.s["mind"][person].setdefault("names", {})[tag] = name


def give_name(w, namer, tag, name) -> list:
    """The namer, everyone at the namer's place and the namer's household learn the name. Returns who learned it."""
    node = w.at(namer)
    hh = w.household_of(namer)
    who = sorted({namer} | {m for m in w.living() if node is not None and w.at(m) == node}
                 | ({m for m in w.living() if hh and w.household_of(m) == hh}))
    for m in who:
        _learn(w, m, tag, name)
    return who


def resolve(w, person, text) -> str | None:
    """The tag meant by a tag or a name this person knows, or None."""
    t = tag_in(text)
    if t:
        return t
    low = strip(str(text or "")).strip().lower()
    for tag, nm in names_of(w, person).items():
        if nm.lower() == low:
            return tag
    return None


def render(w, person, text: str) -> str:
    """A message as this person reads it: the names they know beside the tags."""
    if not on(w) or not text:
        return text
    names = names_of(w, person)
    if not names:
        return text
    return re.sub(r"\(([HT]\d{1,4})\)", lambda m: f"({m.group(1)}: {names[m.group(1)]})" if m.group(1) in names else m.group(0), text)


def herd_by_tag(w, tag) -> str | None:
    return next((hid for hid, h in w.s["herds"].items() if h.get("tag") == tag), None)


def thing_by_tag(w, tag) -> str | None:
    return next((cid for cid, c in w.s["containers"].items() if c.get("tag") == tag), None)
