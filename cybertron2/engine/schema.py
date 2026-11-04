"""The world record's shape and its version (spec/core/world_schema.md, D4-100).

WORLD_SCHEMA is the version of the shape of World.s: its top-level keys, and the fields each record in its tables may hold. It is
stored in every world (s["world_schema"]) and so in every checkpoint of the journal, and in the journal's meta ("world_schema").
Runs from before 4 Nov 2026 have none: version 0, read by their code version (the journal's provenance).

The rule: any change to the shape (a field added, renamed, removed, or changed in meaning or units) adds a line to
spec/core/world_schema.md and bumps WORLD_SCHEMA, and FINGERPRINTS gains the new version's fingerprint. test_cybertron2_schema fails
if a world holds a field not listed here, or if the lists change without the version moving.

`mind` and `know` (each person's
stores) are versioned with the memory and knowledge code, not here; `today` is the day's working record, listed by key."""

import hashlib
import json

WORLD_SCHEMA = 1

TOP = ["acts", "agreements", "buildings", "claims", "containers", "day", "events", "fuse_calls", "herds", "institutions", "know", "left", "life", "log", "mind", "nodes", "offers", "parcels", "people", "roads", "seq", "tag_seq", "today", "traces", "world_schema"]

TODAY = ["_departed", "_floor", "admits", "awake", "care", "care_by", "care_gift", "children_work", "day_seen", "drawn", "fights", "fire", "fled", "fuse", "guards", "heard", "joins", "learn", "left", "memory_done", "partner", "partners", "road", "route", "skipped_morning", "sleep", "soaked", "teach", "thefts", "travel", "travel_choices", "travel_morning", "try", "watch", "worked"]

FIELDS = {
    "nodes": ["name", "text", "unexplored"],
    "roads": ["a", "b", "days", "ends", "stretches", "terrain", "track", "way"],
    "parcels": ["adj", "broken", "clearing", "clearing_built", "cover", "crop", "fallow_since", "fence", "fertility", "fight", "ground", "height", "held_whole", "hunted", "last_crop", "last_kind", "meeting", "name", "node", "res", "shares", "side", "size", "slaughter", "text", "was", "works"],
    "buildings": ["broke", "built_day", "changes", "condition", "description", "door", "fire", "fire_hit", "fire_out", "fitting_work", "fittings", "lasts_until", "lines", "mending", "monument", "name", "node", "parcel", "raided", "rooms", "size", "stock", "structure", "theft", "tier", "unfinished", "warm", "works"],
    "herds": ["ate", "base_name", "births", "bulls", "count", "cows", "driven", "gone", "herders", "home", "hungry", "in_milk", "kind", "last_calf", "lost", "milked", "name", "node", "oxen", "pack", "parcel", "pos", "split_day", "split_of", "strayed_in", "tag", "watched", "with", "young"],
    "containers": ["beast", "body", "buried", "by", "cairn", "cairn_by", "cairn_day", "cause", "day", "died", "door", "goods", "grave", "hidden", "holders", "in", "kind", "node", "of", "on_road", "parcel", "rot", "stretch", "tag", "thing", "untaught", "wear"],
    "people": ["aim", "alive", "arrived", "arrived_by", "at", "ate_raw", "attack", "born", "born_line", "came_from", "cared", "cause", "concerns", "defence", "died", "father", "frailty", "gap_until", "guarded", "hands", "home_seen", "hunger", "interests", "messages", "missed", "model", "notes", "order", "parents", "partner", "pinned", "plan_next", "pregnant", "relations", "role", "sex", "slept_out", "stage", "trade", "transit", "widowed_of", "wounded"],
    "institutions": ["heir", "kind", "members", "name", "offices", "order", "rules", "succession"],
    "claims": ["by", "claimant", "grounds", "joint", "of", "over", "plots", "rights", "since", "thing", "until"],
    "offers": ["by", "closed", "for", "get", "give", "lots", "node", "open", "taken", "to", "until"],
    "agreements": ["day", "legs", "made_by", "node", "offer", "parties", "seeded", "status", "witnesses"],
}


def fingerprint() -> str:
    """A short hash of the declared shape: it changes whenever TOP, TODAY or FIELDS change."""
    text = json.dumps({"top": TOP, "today": TODAY, "fields": FIELDS}, sort_keys=True)
    return hashlib.sha256(text.encode()).hexdigest()[:16]


FINGERPRINTS = {1: "e1d55a118a64e158"}                                                    # the declared shape of each version


def unknown(s) -> list:
    """Fields a world holds that the declared shape does not list: [(table, field)]."""
    out = [("top", k) for k in s if k not in TOP]
    out += [("today", k) for k in (s.get("today") or {}) if k not in TODAY]
    for t, allowed in FIELDS.items():
        for rec in (s.get(t) or {}).values():
            if isinstance(rec, dict):
                out += [(t, k) for k in rec if k not in allowed]
    return sorted(set(out))


def version(s) -> int:
    """The shape version of a saved world: 0 if it predates the number."""
    return int(s.get("world_schema", 0))
