"""Specs: YAML files of fixed values and distributions, with inheritance, explicit overrides, and seeded sampling.

A spec value is either fixed (`rounds: 30`) or a distribution:
  {uniform: [a, b]}     float in [a, b]
  {randint: [a, b]}     int in [a, b]
  {choice: [x, y, z]}   one of the options, uniformly
  {weights: {x: 2, y: 1}}  one key, proportionally to the weights
  {beta: [a, b]}        Beta(a, b) draw
`extends: [base, E3]` deep-merges the named files from cybertron/specs/ (later ones win), then this file on top.
Overrides (`--set a.b=value`) are applied last; a value of `{choice: [...]}` given there is sampled like any other.
Which keys exist, their types and allowed values: cybertron/schema.py (`schema.validate(spec)`, run by the generator; dist_error and
dist_options below are its distribution checks).
"""
from __future__ import annotations

import copy
import functools
import random
import warnings
from pathlib import Path

import yaml

SPEC_DIR = Path(__file__).parent / "specs"
DIST_KEYS = {"uniform", "randint", "choice", "weights", "beta"}


def deep_merge(base: dict, top: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in (top or {}).items():
        # A mapping merges into a section (a dict in the parent that is not itself a distribution), even if its only key looks like
        # a distribution: `goals: {weights: {...}}` sets goals.weights, it does not replace the goals block.
        if isinstance(v, dict) and isinstance(out.get(k), dict) and (not is_dist(out[k]) or not (set(v) & DIST_KEYS)):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def _find(name: str) -> Path:
    p = Path(name)
    if p.suffix in (".yaml", ".yml") and p.exists():
        return p
    q = SPEC_DIR / f"{name}.yaml"
    if q.exists():
        return q
    raise FileNotFoundError(f"spec {name!r} not found (looked for {p} and {q})")


@functools.lru_cache(maxsize=256)
def _parse(text: str) -> dict:
    """yaml.safe_load of a spec file's text, memoised on the text (load deep-copies it): parsing the preset chain with the pure
    Python YAML loader dominated generating a small world, and the same few presets are loaded over and over."""
    return yaml.safe_load(text) or {}


# Top-level keys a file sets whole, never merged into an inherited value (docs/review/27 §0 bug 2): an inline `regime:` is one
# definition. Merging a child's inline regime into its parent's kept the parent's `base` (state_of_nature) and silently voided every
# starting law; a child that wants to build on a regime names it with `base:`.
WHOLE = ("regime",)


def load(name_or_path: str, _seen: tuple = ()) -> dict:
    """Load a spec with its `extends` chain resolved (no sampling yet). Keys in WHOLE replace the inherited value."""
    path = _find(name_or_path)
    if str(path) in _seen:
        raise ValueError(f"circular extends: {path}")
    raw = copy.deepcopy(_parse(path.read_text()))
    merged: dict = {}
    for parent in raw.pop("extends", []) or []:
        merged = _merge_file(merged, load(parent, _seen + (str(path),)))
    out = _merge_file(merged, raw)
    if not _seen:
        warn_frozen(out, path.name)
        check_channel_setup(out, path, declares_channels(path))
    return out


class FrozenModuleWarning(FutureWarning):
    """A spec turns on a frozen module (bug fixes only; no new specs): shown by default, never an error."""


MEDIA2_FROZEN = ("media2 is frozen (bug fixes only; docs/ARCHITECTURE.md, 'media2 is frozen'): channels v2 is the canonical press "
                 "and newspaper model. Existing media2 specs still run; a new world should use channels.v2 instead")


def warn_frozen(spec: dict, name: str = "spec") -> None:
    """Warn (FrozenModuleWarning) when a loaded spec has media2 on. tests/test_media2_frozen.py lists the specs allowed to."""
    m = (spec or {}).get("media2")
    if isinstance(m, dict) and m.get("enabled") not in (None, False):
        warnings.warn(f"{name}: {MEDIA2_FROZEN}", FrozenModuleWarning, stacklevel=3)


# ---------------------------------------------------------------------- review 33: the channel setup is a per-scenario decision
STRICT_DIRS = ("regimes",)                                              # specs here must declare it (an error, not a warning)
QUIET_DIRS = ("fragments",)                                             # presets, not worlds: never checked on their own
GENERIC_SETUP = ("fragments/channels_v2.yaml",)                        # switches channels v2 on with the engine's square: no decision


class ChannelSetupWarning(UserWarning):
    pass


def _rel(path):
    try:
        return Path(path).resolve().relative_to(SPEC_DIR.resolve())
    except ValueError:
        return None


def declares_channels(name_or_path, _seen: tuple = ()) -> bool:
    """Whether the file, or a file it extends other than the generic presets (GENERIC_SETUP), sets channels.square or
    channels.papers: the world chose its public channels rather than inheriting the engine's one square."""
    path = _find(name_or_path)
    if str(path) in _seen:
        return False
    raw = _parse(path.read_text())
    rel = _rel(path)
    ch = raw.get("channels") if isinstance(raw.get("channels"), dict) else {}
    if (rel is None or rel.as_posix() not in GENERIC_SETUP) and ("square" in ch or "papers" in ch):
        return True
    return any(declares_channels(x, _seen + (str(path),)) for x in raw.get("extends") or ())


def check_channel_setup(spec: dict, path=None, declared: bool = True) -> str | None:
    """Review 33: a channels-v2 world's public channels are a deliberate per-scenario decision, never a silent fallback to the
    engine's open square. When the loaded spec does not declare them (declares_channels: channels.square or channels.papers set by
    the world or a world it extends; or, positions.channel_setup_problem, square none with no paper), a ChannelSetupWarning names
    what it fell back to; for specs under cybertron/specs/regimes/ and worlds using positions it is an error. The resolved spec is
    never changed."""
    from cybertron import positions as PS
    rel = _rel(path) if path is not None else None
    if rel is not None and len(rel.parts) > 1 and rel.parts[0] in QUIET_DIRS:
        return None
    why = PS.channel_setup_problem(spec)
    if not why and not declared and (spec.get("channels") or {}).get("v2"):
        why = ("channels.v2 is on but the world does not declare its channel setup: it inherits the engine's default "
               f"channels.square: {(spec.get('channels') or {}).get('square', 'one')} from a generic preset. Decide it: set "
               "channels.square (one | per_camp | none) in the world's spec and, with none, declare the papers (channels.papers "
               "and start.channels entries with paper: true; cybertron/specs/fragments/papers.yaml)")
    if not why:
        return None
    strict = PS.in_use(spec) or (rel is not None and len(rel.parts) > 1 and rel.parts[0] in STRICT_DIRS)
    if strict:
        raise ValueError(f"{path}: {why}")
    import warnings
    warnings.warn(f"{path}: {why}", ChannelSetupWarning, stacklevel=3)
    return why


# Named placements a file clears by setting them to {} (merging {} into an inherited mapping kept every entry: haiku100's
# `goals: {explicit: {}}` silently kept grand35's placed goals, keyed by names its world does not have).
CLEARABLE = (("goals", "explicit"), ("models", "overrides"), ("personality", "explicit"), ("roles", "explicit"), ("agent_rules",))


def _merge_file(base: dict, top: dict) -> dict:
    out = deep_merge({k: v for k, v in base.items() if k not in WHOLE or k not in (top or {})}, top)
    for path in CLEARABLE:
        cur, dst = top or {}, out
        for p in path[:-1]:
            cur = cur.get(p) if isinstance(cur, dict) else None
            dst = dst.get(p) if isinstance(dst, dict) else None
        if isinstance(cur, dict) and cur.get(path[-1]) == {} and isinstance(dst, dict):
            dst[path[-1]] = {}
    return out


def set_path(spec: dict, dotted: str, value) -> dict:
    """Apply one override, e.g. set_path(s, "conditions.fixer", "hidden")."""
    out = copy.deepcopy(spec)
    cur = out
    keys = dotted.split(".")
    for k in keys[:-1]:
        cur = cur.setdefault(k, {})
    cur[keys[-1]] = value
    return out


def apply_overrides(spec: dict, overrides: list[str] | None) -> dict:
    base, keys = spec, set()
    for o in overrides or []:
        key, _, val = o.partition("=")
        keys.add(key.strip())
        spec = set_path(spec, key.strip(), yaml.safe_load(val))
    return _keep_design_rounds(base, spec, keys)


def _keep_design_rounds(base: dict, spec: dict, keys: set) -> dict:
    """Overriding `rounds` must not compress Life's lifespans (life._scale): record the preset's own rounds as life.design_rounds,
    unless the overrides also set life.full_scale_rounds or life.design_rounds (the caller then chose the scaling) or Life is off."""
    life = spec.get("life")
    if ("rounds" not in keys or not isinstance(life, dict) or not life.get("enabled")
            or keys & {"life", "life.full_scale_rounds", "life.design_rounds"} or life.get("design_rounds") is not None):
        return spec
    r0, r1 = base.get("rounds"), spec.get("rounds")
    if all(isinstance(x, int) and not isinstance(x, bool) for x in (r0, r1)) and r0 > r1:     # only a shortened run needs it
        spec = set_path(spec, "life.design_rounds", r0)
    return spec


def is_dist(v) -> bool:
    return isinstance(v, dict) and len(v) == 1 and next(iter(v)) in DIST_KEYS


def dist_error(v) -> str | None:
    """Why a distribution is malformed (None when it is well formed). Only call it on values where is_dist(v) holds."""
    kind, arg = next(iter(v.items()))
    if kind in ("uniform", "randint", "beta"):
        if not (isinstance(arg, (list, tuple)) and len(arg) == 2 and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in arg)):
            return f"{{{kind}: ...}} needs two numbers [a, b], got {arg!r}"
        if kind == "randint" and not all(isinstance(x, int) or float(x).is_integer() for x in arg):
            return f"{{randint: ...}} needs two integers, got {arg!r}"
        if kind != "beta" and arg[0] > arg[1]:
            return f"{{{kind}: [a, b]}} needs a <= b, got {arg!r}"
        if kind == "beta" and min(arg) <= 0:
            return f"{{beta: [a, b]}} needs a, b > 0, got {arg!r}"
    elif kind == "choice":
        if not (isinstance(arg, (list, tuple)) and arg):
            return f"{{choice: ...}} needs a non-empty list, got {arg!r}"
    elif kind == "weights":
        if not (isinstance(arg, dict) and arg):
            return f"{{weights: ...}} needs a non-empty mapping {{option: weight}}, got {arg!r}"
        if not all(isinstance(w, (int, float)) and not isinstance(w, bool) and w >= 0 for w in arg.values()):
            return f"{{weights: ...}} needs weights >= 0, got {arg!r}"
        if not sum(arg.values()) > 0:
            return "{weights: ...} needs at least one positive weight"
    return None


def _num_key(k):
    """A weights key as written: JSON turns number keys into strings ({0: 37} -> {"0": 37}), so instance.json and run files carry
    them as strings; read them back as the numbers they were."""
    if isinstance(k, str):
        for cast in (int, float):
            try:
                return cast(k)
            except ValueError:
                pass
    return k


def dist_options(v) -> list:
    """The values a distribution can give that can be checked one by one: choice options, weights keys, uniform/randint/beta ends."""
    kind, arg = next(iter(v.items()))
    if kind == "weights":
        return [_num_key(k) for k in arg]
    if kind == "beta":
        return [0.0, 1.0]
    return list(arg)


def draw(v, rng: random.Random):
    """Sample one value (fixed values pass through)."""
    if not is_dist(v):
        return v
    kind, arg = next(iter(v.items()))
    if kind == "uniform":
        return rng.uniform(*arg)
    if kind == "randint":
        return rng.randint(*arg)
    if kind == "choice":
        return rng.choice(list(arg))
    if kind == "weights":
        keys = list(arg)
        return _num_key(rng.choices(keys, weights=[arg[k] for k in keys])[0])
    if kind == "beta":
        return rng.betavariate(*arg)
    raise ValueError(kind)


def resolve(spec, rng: random.Random):
    """Sample every distribution in a spec tree (depth-first, in key order, so a seed gives the same world)."""
    if is_dist(spec):
        return draw(spec, rng)
    if isinstance(spec, dict):
        return {k: resolve(v, rng) for k, v in spec.items()}
    if isinstance(spec, list):
        return [resolve(v, rng) for v in spec]
    return spec
