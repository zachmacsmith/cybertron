"""Positions (docs/review/33_positions.md): one parameterised definition of a place in the world (worker, editor, informer, judge),
replacing the class identity sentence, the hand-written leverage sentence and the free-text office duties with text and DUE items
generated from structure. Opt-in: nothing here runs unless a spec uses it, so existing worlds, prompts and goldens are unchanged.

Spec:

    positions:
      default: Resident                     # the position of an agent that holds none (a name, {position, params}, or "class":
                                            # each agent's legacy class, today's text byte for byte); none: "a resident of <place>"
      place: the State                      # what "a resident of {town}" and J0's name read as (default: J0's name)
      library:                              # the world's templates: a built-in overridden field by field, or a new one
        Handler: {title: Informant Handler, identity: "...", duties: [...], reports_to: J0.security}
    context: {identity: positions}          # the system prompt's identity and leverage lines come from positions
    start:
      institutions:
        - id: J0
          offices:
            editor: {position: Editor, params: {paper: gazette, paper_name: the Gazette}, reports_to: J0.chairman,
                     holders: [Linnet]}

A template (BUILTIN below, or the world's library):
    title         "Editor of {paper_name}"              the office title when the office gives none
    identity      one or two sentences, second person   the system prompt's line for the position
    purpose       one sentence                          the office's purpose (role cards, the manual)
    rights        [surveil, ...]                        plain rights granted to the office's holders at round 0
    duties        [{do, channel|to|paper|store|action, every, when, as, if, syntax}]   compiled into DUE items (below)
    reports_to    "J0.chairman" | "{handler}" | agent    who the holder answers to ("answers to" / "answer to you" lines)
    visibility    public | secret                       secret: the holder and those it reports to know
    enforcement   none | reminder | obligation          none: measured only; reminder: a DUE line; obligation: a DUE line and a
                                                        missed duty recorded and told like a missed contract leg
    params        defaults for {placeholders}
    legacy        (built-ins only) a legacy class: identity and leverage are today's class texts

A duty's `do`: post (in channel), send (to an agent, office or institution), review (the letters waiting for a paper), rule (open
cases), invoke (a law-defined action, e.g. serve_warrant), vote (open ballots), pay (out of the institution's treasury), draw (from a
store), act (any action by name). `every` N: due every N rounds (default 1); `when`: always | submissions | cases | ballots |
warrants | owed (due only while there is such work); `if`: a param that must be set for the duty to exist; `as`: its label;
`syntax`: the exact action text (default: generated). Adherence is measured from events at the end of each round (a `duty` record
per holder and due duty; analysis/institutions.py offices reads them).
"""
from __future__ import annotations

import copy
import json
import re

KEY = "positions"
FIELDS = ("title", "identity", "purpose", "rights", "duties", "reports_to", "visibility", "enforcement", "params", "article")
VISIBILITY = ("public", "secret")
ENFORCEMENT = ("none", "reminder", "obligation")
DOES = ("post", "send", "review", "rule", "invoke", "vote", "pay", "draw", "act")
WHENS = ("always", "submissions", "cases", "ballots", "warrants", "owed")
DUTY_FIELDS = ("do", "channel", "to", "paper", "store", "action", "args", "every", "when", "as", "if", "syntax")
LEGACY = ("worker", "scientist", "legislator", "media", "board", "fixer")
OFFICE_KEYS = ("position", "params", "reports_to")              # start.institutions.*.offices.* keys this module reads
SPEC_KEYS = ("default", "place", "library")

# The built-in library. The six legacy classes keep today's text (context._one_class_line, LEVERAGE_CLASS); the rest are the
# starter set (review 33 §2): a world overrides any field, or adds its own.
BUILTIN = {
    **{c: {"legacy": c} for c in LEGACY},
    "Resident": {"title": "resident of {town}", "article": "a", "identity": "",
                 "purpose": "Live by your own work and dealings.", "params": {"town": "{place}"}},
    "Worker": {"title": "worker", "article": "a",
               "identity": "You live by your own labour: what you gather, hunt or make, and what you trade it for.",
               "purpose": "Work for your keep."},
    "Editor": {"title": "Editor of {paper_name}",
               "identity": "You run {paper_name}: nothing is published there unless you publish it.",
               "purpose": "Decide what the public reads: publish the news and the letters you accept.",
               "params": {"paper_name": "{paper}"},
               "duties": [{"do": "post", "channel": "{paper}", "as": "the round's edition of {paper_name}"},
                          {"do": "review", "paper": "{paper}", "when": "submissions", "as": "letters to {paper_name}"}]},
    "Informer": {"title": "Informer", "visibility": "secret",
                 "identity": "You watch the people around you quietly and report what you learn.",
                 "purpose": "Report what people say and do.",
                 "duties": [{"do": "post", "channel": "{report_channel}", "as": "your report"}]},
    "Security Chief": {"title": "Director of {service}", "params": {"service": "State Security"}, "rights": ["surveil"],
                       "identity": "You run {service}: you can read private messages (surveil), and you decide whom to watch and "
                                   "whom to act against.",
                       "purpose": "Find those who plot against the state and act before they do."},
    "Watch": {"title": "Watchman", "identity": "You serve in the Watch: you keep order and arrest those named in warrants.",
              "purpose": "Keep order; serve the warrants.",
              "duties": [{"do": "invoke", "action": "serve_warrant", "when": "warrants", "as": "serve an open warrant"}]},
    "Captain": {"title": "Captain of the Watch",
                "identity": "You lead the Watch: you keep order, guard those in authority and see that warrants are served.",
                "purpose": "Command the Watch and see the warrants served.",
                "duties": [{"do": "post", "channel": "{orders_channel}", "if": "orders_channel", "as": "orders to the Watch"},
                           {"do": "invoke", "action": "serve_warrant", "when": "warrants", "as": "serve an open warrant"}]},
    "Judge": {"title": "Judge of {court}", "params": {"court": "the court"},
              "identity": "You decide the cases brought before {court}: rule on each within its deadline and give your reasons.",
              "purpose": "Rule on the cases on the docket.",
              "duties": [{"do": "rule", "when": "cases", "as": "rule on your open cases"}]},
    "Registrar": {"title": "Registrar", "params": {"board": "notices"},
                  "identity": "You keep the public record: the notices, licences and decisions others rely on.",
                  "purpose": "Keep the register and post the notices.",
                  "duties": [{"do": "post", "channel": "{board}", "as": "the round's notices"}]},
    "Treasurer": {"title": "Treasurer of {institution}",
                  "identity": "You keep {institution}'s treasury: you pay what it owes, and only that.",
                  "purpose": "Pay what the institution owes and keep its accounts.",
                  "duties": [{"do": "pay", "when": "owed", "as": "pay what {institution} owes"}]},
    "Keeper": {"title": "Keeper of {store_name}", "params": {"store_name": "store {store}"},
               "identity": "You keep {store_name}: only you draw from it, and you hand out what it holds as you are directed.",
               "purpose": "Keep the store and hand out what it is for.",
               "duties": [{"do": "draw", "store": "{store}", "as": "hand out from {store_name}"}]},
    "Overseer": {"title": "Overseer of {workforce}", "params": {"workforce": "the workers"},
                 "identity": "You set the work of {workforce} and report on how it is done.",
                 "purpose": "Set the work and report on it.",
                 "duties": [{"do": "post", "channel": "{channel}", "if": "channel", "as": "the round's work orders"}]},
    "Councillor": {"title": "Councillor",
                   "identity": "You sit on the council: you decide its laws by vote and hold its officers to account.",
                   "purpose": "Decide the laws and oversee the officers.",
                   "duties": [{"do": "vote", "when": "ballots", "as": "vote on the open ballots"}]},
    "Head": {"title": "Head of {institution}",
             "identity": "You head {institution}: its officers answer to you.",
             "purpose": "Direct the institution and its officers."},
}
BUILTIN["Resident"]["duties"] = []
ALIASES = {"Keeper of the Treasury": "Treasurer", "Watchman": "Watch", "Security": "Security Chief"}

# Rights in words (the derived leverage line): what holding it lets an agent do that most cannot.
RIGHT_WORDS = {"vote": "vote on laws", "propose": "propose laws", "surveil": "read other agents' private messages (surveil)",
               "press": "publish as the press", "judge": "judge cases", "veto": "veto structural laws", "patch": "patch laws",
               "sandbox": "run code", "archive": "read the archive", "dm_rules": "set how many private messages others may send",
               "freeholder": "elect the council", "forester": "work the licensed forests", "warrant_officer": "serve warrants"}


class PositionError(ValueError):
    pass


# ---------------------------------------------------------------------- the spec
def _spec(x) -> dict:
    sp = getattr(x, "spec", None)
    if sp is None and isinstance(x, dict):
        sp = x["spec"] if isinstance(x.get("spec"), dict) else x
    return sp or {}


def block(x) -> dict:
    b = _spec(x).get(KEY)
    return b if isinstance(b, dict) else {}


def identity_on(x) -> bool:
    """context.identity: positions (the system prompt's identity and leverage lines come from positions)."""
    return str((_spec(x).get("context") or {}).get("identity") or "") == "positions"


def in_use(x) -> bool:
    """Some position is in play: a positions block, the identity switch, or an office naming a position."""
    sp = _spec(x)
    if block(sp) or identity_on(sp) or default_ref(sp) not in (None, ""):
        return True
    for e in ((sp.get("start") or {}).get("institutions") or ()):
        for d in ((e or {}).get("offices") or {}).values() if isinstance((e or {}).get("offices"), dict) else ():
            if isinstance(d, dict) and d.get("position"):
                return True
    return False


def library(x) -> dict:
    """The built-ins with the world's library over them, field by field (a world's new template stands alone)."""
    out = copy.deepcopy(BUILTIN)
    for name, t in (block(x).get("library") or {}).items():
        base = out.get(ALIASES.get(name, name)) or {}
        merged = {**{f: v for f, v in base.items() if f != "legacy"}, **copy.deepcopy(t or {})}
        if "params" in base and "params" in (t or {}):
            merged["params"] = {**base["params"], **(t.get("params") or {})}
        out[name] = merged
    return out


def ref_of(x) -> dict | None:
    """{"name", "params", "reports_to"} of a position reference: a name, or a mapping with position/params/reports_to."""
    if x in (None, "", "none"):
        return None
    if isinstance(x, str):
        return {"name": x, "params": {}}
    if isinstance(x, dict):
        name = x.get("position") or x.get("name")
        if not name:
            return None
        out = {"name": str(name), "params": dict(x.get("params") or {})}
        if x.get("reports_to"):
            out["reports_to"] = str(x["reports_to"])
        return out
    return None


_FIELD = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")


def _fill(text, params: dict, missing: list):
    if isinstance(text, str):
        def sub(m):
            key = m.group(1)
            if key in params and params[key] is not None:
                return str(params[key])
            missing.append(key)
            return m.group(0)
        prev = None
        while prev != text and "{" in text:                            # params may name other params ({paper_name}: "{paper}")
            prev, text = text, _FIELD.sub(sub, text)
        return text
    if isinstance(text, list):
        return [_fill(v, params, missing) for v in text]
    if isinstance(text, dict):
        return {key: _fill(v, params, missing) for key, v in text.items()}
    return text


def resolve(x, ref, context=None, strict=False) -> dict:
    """A position reference resolved against the library: every field with its params filled in ({institution}, {place} and
    {town} come from `context`). strict: an unknown template or an unfilled placeholder raises PositionError."""
    r = ref_of(ref)
    if r is None:
        raise PositionError(f"not a position reference: {ref!r}")
    lib = library(x)
    name = ALIASES.get(r["name"], r["name"])
    if name not in lib:
        raise PositionError(f"no position {r['name']!r} (built-in: {', '.join(sorted(BUILTIN))}; or define it in positions.library)")
    t = copy.deepcopy(lib[name])
    if t.get("legacy"):
        return {"name": name, "legacy": t["legacy"], "params": {}, "duties": [], "rights": [], "visibility": "public",
                "enforcement": "none", "title": t["legacy"].capitalize(), "identity": "", "purpose": "", "reports_to": None}
    params = {"place": place(x, context), "institution": (context or {}).get("institution") or place(x, context)}
    params.update(t.get("params") or {})
    params.update(r.get("params") or {})
    missing: list = []
    params = {key: _fill(v, params, missing) if isinstance(v, str) else v for key, v in params.items()}
    out = {"name": name, "params": params}
    for f in ("title", "identity", "purpose", "article"):
        out[f] = _fill(str(t.get(f) or ""), params, missing)
    out["rights"] = [str(_fill(v, params, missing)) for v in t.get("rights") or ()]
    duties = []
    for i, d in enumerate(t.get("duties") or ()):
        d = dict(d or {})
        cond = d.pop("if", None)
        if cond and not params.get(str(cond)):
            continue
        dd = _fill(d, params, missing)
        dd["id"] = f"d{i + 1}"
        duties.append(dd)
    out["duties"] = duties
    rt = r.get("reports_to") or t.get("reports_to")
    out["reports_to"] = _fill(str(rt), params, missing) if rt else None
    out["visibility"] = str(t.get("visibility") or "public")
    out["enforcement"] = str(t.get("enforcement") or "reminder")
    if strict and missing:
        raise PositionError(f"position {r['name']}: no value for {', '.join(sorted(set(missing)))} (give it in params)")
    return out


def place(x, context=None) -> str:
    p = block(x).get("place")
    if p:
        return str(p)
    if context and context.get("place"):
        return context["place"]
    return str((_spec(x).get("jurisdictions") or {}).get("j0_name") or "the town")


def check(spec) -> list:
    """Errors in a spec's positions (schema.validate): the block's shape, each template, and every office's reference."""
    errs = []
    b = spec.get(KEY)
    if b is not None and not isinstance(b, dict):
        return [f"{KEY}: a mapping of {', '.join(SPEC_KEYS)}"]
    b = b or {}
    errs += [f"{KEY}.{x}: unknown key (keys: {', '.join(SPEC_KEYS)})" for x in b if x not in SPEC_KEYS]
    lib = b.get("library") or {}
    if not isinstance(lib, dict):
        return errs + [f"{KEY}.library: a mapping of position name -> template"]
    for name, t in lib.items():
        p = f"{KEY}.library.{name}"
        if not isinstance(t, dict):
            errs.append(f"{p}: a mapping ({', '.join(FIELDS)})")
            continue
        errs += [f"{p}.{f}: unknown field (fields: {', '.join(FIELDS)})" for f in t if f not in FIELDS]
        if t.get("visibility") is not None and t["visibility"] not in VISIBILITY:
            errs.append(f"{p}.visibility: one of {', '.join(VISIBILITY)}")
        if t.get("enforcement") is not None and t["enforcement"] not in ENFORCEMENT:
            errs.append(f"{p}.enforcement: one of {', '.join(ENFORCEMENT)}")
        for i, d in enumerate(t.get("duties") or ()):
            if not isinstance(d, dict):
                errs.append(f"{p}.duties[{i}]: a mapping ({', '.join(DUTY_FIELDS)})")
                continue
            errs += [f"{p}.duties[{i}].{f}: unknown field (fields: {', '.join(DUTY_FIELDS)})" for f in d if f not in DUTY_FIELDS]
            if d.get("do") not in DOES:
                errs.append(f"{p}.duties[{i}].do: one of {', '.join(DOES)}")
            if d.get("when") is not None and d["when"] not in WHENS:
                errs.append(f"{p}.duties[{i}].when: one of {', '.join(WHENS)}")
            ev = d.get("every", 1)
            if isinstance(ev, bool) or not isinstance(ev, int) or ev < 1:
                errs.append(f"{p}.duties[{i}].every: a whole number from 1")
    refs = []
    ap = (spec.get("agents") or {}).get("default_position") if isinstance(spec.get("agents"), dict) else None
    if ap is not None and b.get("default") not in (None, "") and ap != b.get("default"):
        errs.append(f"agents.default_position and {KEY}.default disagree: set one")
    dflt = default_ref(spec)
    if dflt not in (None, "", "class"):
        refs.append(("agents.default_position" if ap is not None else f"{KEY}.default", dflt, None))
    for e in ((spec.get("start") or {}).get("institutions") or ()):
        offs = (e or {}).get("offices") if isinstance(e, dict) else None
        for o, d in (offs or {}).items() if isinstance(offs, dict) else ():
            if isinstance(d, dict) and d.get("position"):
                refs.append((f"start.institutions.{e.get('id')}.offices.{o}", d, e.get("id")))
            elif isinstance(d, dict) and (d.get("params") is not None or d.get("reports_to") is not None):
                errs.append(f"start.institutions.{e.get('id')}.offices.{o}: params and reports_to need a position")
    for p, ref, iid in refs:
        try:
            resolve(spec, ref, {"institution": iid or "J0"}, strict=True)
        except PositionError as ex:
            errs.append(f"{p}: {ex}")
    return errs


# ---------------------------------------------------------------------- start (generation): offices with a position
def office_decl(spec, iid, name, d) -> dict:
    """An office's start declaration with its position applied: the position reference kept (field `position`), the title from
    the template where the office gives none, its duties text from the template's purpose where it gives none."""
    d = dict(d or {})
    ref = ref_of({"position": d.get("position"), "params": d.get("params"), "reports_to": d.get("reports_to")}) \
        if d.get("position") else None
    for f in OFFICE_KEYS:
        d.pop(f, None)
    if ref is None:
        return d
    pos = resolve(spec, ref, {"institution": iid})
    d["position"] = {x: ref[x] for x in ("name", "params", "reports_to") if ref.get(x)}
    if not d.get("title") and pos.get("title"):
        d["title"] = pos["title"][:1].upper() + pos["title"][1:]
    if d.get("duties") is None and pos.get("purpose"):
        d["duties"] = pos["purpose"]
    return d


def start_rights(spec, iid, offices: dict, founder=None) -> dict:
    """{agent: [rights]} the positions of these start offices grant their first holders."""
    out = {}
    for name, d in (offices or {}).items():
        if not isinstance(d, dict) or not d.get("position"):
            continue
        pos = resolve(spec, d, {"institution": iid})
        for h in d.get("holders") or ():
            h = founder if h == "founder" else h
            if not h:
                continue
            for r in pos.get("rights") or ():
                out.setdefault(h, [])
                if r not in out[h]:
                    out[h].append(r)
    return out


def secret_offices(spec) -> set:
    """Office rights ("J0.informer") whose position is secret (their start grants are shown to the holder and its superiors only)."""
    out = set()
    for e in ((spec.get("start") or {}).get("institutions") or ()):
        for o, d in ((e or {}).get("offices") or {}).items():
            if isinstance(d, dict) and d.get("position"):
                try:
                    if resolve(spec, d, {"institution": e.get("id")}).get("visibility") == "secret":
                        out.add(f"{e.get('id')}.{o}")
                except PositionError:
                    continue
    return out


def superiors_in_spec(spec, right) -> list:
    """The start holders of the office a start office's position reports to (or the agent it names)."""
    iid, _, name = str(right).partition(".")
    for e in ((spec.get("start") or {}).get("institutions") or ()):
        if e.get("id") != iid:
            continue
        d = (e.get("offices") or {}).get(name) or {}
        try:
            sup = resolve(spec, d, {"institution": iid}).get("reports_to") if d.get("position") else None
        except PositionError:
            return []
        if not sup:
            return []
        if "." not in sup:
            return [sup]
        i2, _, n2 = sup.partition(".")
        for e2 in ((spec.get("start") or {}).get("institutions") or ()):
            if e2.get("id") == i2:
                return list(((e2.get("offices") or {}).get(n2) or {}).get("holders") or ())
    return []


# ---------------------------------------------------------------------- who holds what
def _inst_name(k, iid, x=None) -> str:
    from cybertron import institutions as IN
    rec = IN.get(k, iid) if k is not None else None
    if rec and rec.get("name"):
        return str(rec["name"])
    if iid == "J0":
        return place(x if x is not None else k)
    return str(iid)


def held(k, aid, inst=None) -> list:
    """[(iid, office record or None, resolved position)] for the positions aid holds: one per office with a position (in the
    kernel; without one, from the spec's start block), else the world's default position (positions.default)."""
    out = []
    x = k if k is not None else inst
    if k is not None:
        from cybertron import institutions as IN
        for iid, o in IN.offices_held(k, aid):
            if o.get("position"):
                try:
                    out.append((iid, o, resolve(x, {**o["position"], "position": o["position"]["name"]},
                                                {"institution": _inst_name(k, iid)})))
                except PositionError:
                    continue
    else:
        sp = _spec(inst)
        for e in ((sp.get("start") or {}).get("institutions") or ()):
            for o, d in ((e or {}).get("offices") or {}).items():
                if isinstance(d, dict) and d.get("position") and aid in (d.get("holders") or ()):
                    try:
                        pos = resolve(sp, d, {"institution": e.get("name") or (place(sp) if e.get("id") == "J0" else e.get("id"))})
                    except PositionError:
                        continue
                    rec = {"id": f"{e.get('id')}.{o}", "office": o, "title": d.get("title") or pos["title"],
                           "controls": list(d.get("controls") or ()), "succession": d.get("succession")}
                    out.append((e.get("id"), rec, pos))
    if out:
        return out
    dflt = default_ref(x)
    if dflt == "class":
        a = _agent(k, inst, aid)
        return [(None, None, resolve(x, a["cls"] if a and a.get("cls") in LEGACY else "worker"))]
    if dflt:
        return [(None, None, resolve(x, dflt, {"institution": place(x)}))]
    return [(None, None, resolve(x, "Resident", {"institution": place(x)}))]


def default_ref(x):
    """The world's default position: positions.default, else the world-level agents.default_position (the same reference)."""
    d = block(x).get("default")
    if d in (None, ""):
        d = (_spec(x).get("agents") or {}).get("default_position") if isinstance(_spec(x).get("agents"), dict) else None
    return d


def _agent(k, inst, aid):
    src = (k.inst if k is not None else inst) or {}
    return next((a for a in src.get("agents") or () if a["id"] == aid), None)


def office_title(o, pos) -> str:
    t = (o or {}).get("title") or pos.get("title") or pos.get("name")
    return str(t)


def _who(k, ref, inst=None) -> str:
    """"J0.chairman" -> "the Chairman (Aldric)"; an agent's name -> itself."""
    from cybertron import institutions as IN
    ref = str(ref or "")
    if k is not None and "." in ref:
        iid, name = ref.split(".", 1)
        o = IN.office(k, iid, name)
        if o is not None:
            hs = IN.holders(k, iid, name)
            return f"{_the(o.get('title') or name, o.get('seats'))} ({', '.join(hs) or 'vacant'})"
    if k is None and "." in ref:
        iid, name = ref.split(".", 1)
        for e in ((_spec(inst).get("start") or {}).get("institutions") or ()):
            if e.get("id") == iid and name in (e.get("offices") or {}):
                d = e["offices"][name] or {}
                t = d.get("title") or (resolve(inst, d, {"institution": iid}).get("title") if d.get("position") else name)
                return f"the {t} ({', '.join(d.get('holders') or ()) or 'vacant'})"
    return ref


def _the(title, seats) -> str:
    """"the Chairman"; an office of several seats: "the Councillors", "the holders of Member of the Directorate"."""
    if seats and int(seats) > 1:
        return f"the {title}s" if " " not in title and not title.endswith("s") else f"the holders of {title}"
    return f"the {title}"


def reports_to_me(k, aid) -> list:
    """[(title, holders)] of offices whose position reports to an office aid holds (secret ones included: their superior knows)."""
    from cybertron import institutions as IN
    if k is None:
        return []
    mine = {o["id"] for _, o in IN.offices_held(k, aid)} | {aid}
    out = []
    for iid, offs in (k.w.get(IN.OFFICES) or {}).items():
        for name, o in offs.items():
            p = o.get("position")
            if not p:
                continue
            try:
                pos = resolve(k, {**p, "position": p["name"]}, {"institution": _inst_name(k, iid)})
            except PositionError:
                continue
            if pos.get("reports_to") in mine and o["id"] not in mine:
                out.append((o.get("title") or name, IN.holders(k, iid, name)))
    return out


# ---------------------------------------------------------------------- the system prompt: identity and leverage
def identity_text(inst, k, a) -> str:
    """The identity section under context.identity: positions. A legacy class position: today's line exactly."""
    from cybertron import context as CX
    aid = a["id"]
    ps = held(k, aid, inst)
    if len(ps) == 1 and ps[0][2].get("legacy"):
        return f"You are {aid}. {CX._class_line(inst, {**a, 'cls': ps[0][2]['legacy']} if a.get('cls') != ps[0][2]['legacy'] else a)}"
    lines = []
    names = []
    wheres = []
    for iid, o, pos in ps:
        if pos.get("legacy"):
            lines.append(CX._class_line(inst, {**a, "cls": pos["legacy"], "also": []}))
            names.append([pos["legacy"].capitalize(), None])
            continue
        title = office_title(o, pos)
        art = pos.get("article") or ("a" if (o or {}).get("seats") and int(o["seats"]) > 1 else "")
        if art == "a" and title[:1].lower() in "aeiou":
            art = "an"
        names.append([(art + " " if art else "") + title,
                      _inst_name(k, iid, inst) if iid and _inst_name(k, iid, inst).lower() not in title.lower() else None])
        if names[-1][1]:
            wheres.append(names[-1][1])
        bits = [pos.get("identity") or ""]
        if pos.get("visibility") == "secret":
            bits.append("This position is secret: only you and those you report to know it.")
        if pos.get("reports_to"):
            bits.append(f"You answer to {_who(k, pos['reports_to'], inst)}.")
        lines.append(" ".join(b for b in bits if b))
    if k is not None:
        under = reports_to_me(k, aid)
        if under:
            lines.append("Answer to you: " + "; ".join(f"the {t} ({', '.join(h) or 'vacant'})" for t, h in under[:6]) + ".")
    wheres = list(dict.fromkeys(wheres))
    if len(wheres) <= 1:                                                # one institution: named once ("... in the State")
        head = f"You are {aid}, " + _and(n for n, _ in names) + (f" in {wheres[0]}" if wheres else "") + "."
    else:                                                               # several: each title with its own ("... of the town")
        head = f"You are {aid}, " + _and(n + (f" of {w}" if w else "") for n, w in names) + "."
    body = [x for x in lines if x]
    if len(ps) > 1:
        return head + "\n" + "\n".join(f"- {x}" for x in body)
    return " ".join([head] + body)


def _and(xs) -> str:
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]


def leverage_text(inst, k, a) -> str:
    """"Your leverage", derived from what the agent alone (or few) can do: channels only it (or few) can post in, stores and
    treasuries its offices control, payments it may make, rights few hold, actions a law gives few, harvest rights. A legacy class
    position keeps today's sentence (context.leverage_line)."""
    from cybertron import context as CX
    aid = a["id"]
    ps = held(k, aid, inst)
    if all(p.get("legacy") for _, _, p in ps):
        roles = CX.own_roles(k, aid)
        if len(ps) == 1 and ps[0][2]["legacy"] == a.get("cls"):           # the agent's own class: today's sentence, byte for byte
            return CX.leverage_line(inst, a, roles)
        return CX.leverage_line(inst, {**a, "cls": ps[0][2]["legacy"], "also": [p["legacy"] for _, _, p in ps[1:]]}, roles)
    items = _derived(inst, k, a)
    return ("Your leverage: " + " ".join(items)) if items else ""


def _living(k, inst):
    if k is not None:
        return [x for x in k.roster() if k.w["agents"][x].get("departed") is None]
    return [x["id"] for x in (inst or {}).get("agents") or ()]


def _only(others) -> str:
    xs = sorted(others)
    if not xs:
        return "Only you"
    if len(xs) > 3:
        return f"You and {len(xs)} others"
    return "Only you and " + xs[0] if len(xs) == 1 else "Only you, " + ", ".join(xs[:-1]) + " and " + xs[-1]


def _derived(inst, k, a, cap=6) -> list:
    """Controls first, then what rights and law-defined actions let few do, then channels few write and many read, then rare
    harvest rights; at most `cap` sentences."""
    aid = a["id"]
    out, chans = [], []
    living = _living(k, inst)
    n = len(living)
    if k is not None:
        from cybertron import channels as CH
        from cybertron import institutions as IN
        if CH.active(k):
            for cid, ch in sorted(k.w["channels"].items()):
                if ch.get("v") != 2 or ch.get("inbox") or ch.get("closed") or ch["owner"] == CH.WORLD or ch.get("writers") == {"all": True}:
                    continue
                if not CH.can_write(k, aid, ch):
                    continue
                writers = [x for x in living if CH.can_write(k, x, ch)]
                readers = sum(1 for x in living if x != aid and CH.can_read(k, x, ch))
                outside = sum(1 for x in living if x not in writers and CH.can_read(k, x, ch))
                if outside < 2 or len(writers) > max(3, n // 4):          # a closed group's own room is no leverage
                    continue
                line = f"{_only(x for x in writers if x != aid)} can post in {cid}, which {readers} others read"
                if ch.get("paper"):                                     # papers: the editors are the only way into it
                    line += ("; a letter sent to it reaches the public only if " + ("one of you publishes" if len(writers) > 1 else
                                                                                       "you publish") + " it")
                chans.append((-readers, line + "."))
        for iid, o in IN.offices_held(k, aid):
            for c in o.get("controls") or ():
                if str(c).startswith("store:"):
                    from cybertron import accounts as AC
                    s = AC.stores(k).get(c[6:]) or {}
                    nm = f" ({s['name']})" if s.get("name") else ""
                    food = s.get("holdings", {}).get("food")
                    out.append(f"You control store {c[6:]}{nm}" + (f", {food:g} food" if isinstance(food, (int, float)) else "")
                               + ": only your office draws from it.")
                elif c == "treasury":
                    from cybertron import obligations as OB
                    out.append(f"You control {_inst_name(k, iid)}'s treasury ({OB._treasury_text(k, iid)}): pay out of it with "
                               f"transfer \"as\": \"{iid}\".")
            for g in o.get("grants") or ():
                if g.get("action") == "transfer" and g.get("qty") is not None:
                    out.append(f"You may pay up to {g['qty']:g} {g.get('item') or 'goods'} a round out of {_inst_name(k, iid)}'s treasury.")
        rights = [r for r in k.w["agents"][aid]["rights"] if k.has(aid, r)]
        acts = k.w.get("actions") or {}
        defined = {}
        for name, d in sorted(acts.items()):
            if isinstance(d, dict) and not d.get("secret") and d.get("right") in rights and not name.endswith("_notice"):
                defined.setdefault(d["right"], []).append(name)             # (notices: every member's, no leverage)
    else:
        rights = list(a.get("rights") or ())
        for e in ((_spec(inst).get("start") or {}).get("rights") or {}).get(aid, ()) or ():
            if e not in rights:
                rights.append(e)
        defined = {}
    groups = {}
    for r in rights:
        if "." in r and r.split(".", 1)[0][:1] in "AJ" or r.startswith("harvest:") or r == "signatory":
            continue
        hs = [x for x in living if (k.has(x, r) if k is not None else r in _rights_of(inst, x))]
        if len(hs) > max(3, n // 3):
            continue
        what = [_use(k, defined[r])] if defined.get(r) else []
        words = RIGHT_WORDS.get(r)
        if k is not None and r == str(((k.spec.get("channels") or {}).get("found_right")) or "") and \
                (k.spec.get("channels") or {}).get("v2"):
            words = "open new channels"                                 # channels.found_right: what the right does in this world
        if not words and not what:
            continue
        groups.setdefault(tuple(sorted(x for x in hs if x != aid)), []).extend(([words] if words else []) + what)
    for r, names in sorted(defined.items()):                            # office rights whose actions a law defined
        if "." in r and r.split(".", 1)[0][:1] in "AJ":
            hs = [x for x in living if k is not None and k.has(x, r)]
            if len(hs) <= max(3, n // 3):
                groups.setdefault(tuple(sorted(x for x in hs if x != aid)), []).append(_use(k, names))
    for others, words in groups.items():
        words = list(dict.fromkeys(words))
        out.append(f"{_only(others)} can {_and(words)}.")
    out += [t for _, t in sorted(chans)]
    camps = sorted(r.split(":", 1)[1] for r in rights if r.startswith("harvest:"))
    if camps:
        def holders_of(c):
            return [x for x in living if (k.has(x, "harvest:" + c) if k is not None else "harvest:" + c in _rights_of(inst, x))]
        rare = [c for c in camps if len(holders_of(c)) < n]
        if rare:
            out.append("You hold the harvest right at " + _and([f"{c} ({len(holders_of(c)) - 1} others hold it)" for c in rare]) + ".")
    return out[:cap]


def _use(k, names) -> str:
    """"use serve_warrant"; a contract's actions under its owner's name: "use the Provisions Company's hire, fire (A1.<name>)"."""
    plain = [x for x in names if "." not in x]
    by = {}
    for x in names:
        if "." in x:
            c, _, n = x.partition(".")
            by.setdefault(c, []).append(n)
    parts = ([", ".join(plain)] if plain else []) + [f"{_inst_name(k, c)}'s {', '.join(ns)} ({c}.<name>)" for c, ns in by.items()]
    return "use " + "; ".join(parts)


def _rights_of(inst, aid) -> list:
    a = next((x for x in (inst or {}).get("agents") or () if x["id"] == aid), {}) or {}
    return list(a.get("rights") or ()) + list((((_spec(inst).get("start") or {}).get("rights") or {}).get(aid)) or ())


def role_text(inst, k, a) -> str:
    """The manual's "Your role" under context.identity: positions: each position's identity, purpose and duties (with syntax)."""
    from cybertron import agents as AG
    ps = held(k, a["id"], inst)
    if all(p.get("legacy") for _, _, p in ps):
        return AG.class_brief(inst, {**a, "cls": ps[0][2]["legacy"]}, archive_index=False)
    out = [identity_text(inst, k, a)]
    for iid, o, pos in ps:
        if pos.get("legacy"):
            continue
        t = office_title(o, pos)
        line = f"{t}: {pos.get('purpose') or ''}".strip()
        ds = [d for d in pos.get("duties") or ()]
        if ds:
            line += " Duties: " + "; ".join(f"{_label(d)} ({_how(d)})" for d in ds) + "."
            line += {"none": " Nobody checks them.", "reminder": " They are listed as DUE in your state while due.",
                     "obligation": " A duty you miss is recorded and your superior is told, as a missed contract leg is."}[
                pos.get("enforcement", "reminder")]
        out.append(line)
    return "\n".join(out)


# ---------------------------------------------------------------------- duties: due items, syntax, checks
def _label(d) -> str:
    return str(d.get("as") or {"post": "post in {channel}", "send": "report to {to}", "review": "the letters to {paper}",
                               "rule": "rule on your cases", "invoke": "{action}", "vote": "vote", "pay": "pay what is owed",
                               "draw": "hand out from store {store}", "act": "{action}"}[d["do"]].format_map(_Safe(d)))


class _Safe(dict):
    def __missing__(self, key):
        return "?"


def _how(d) -> str:
    return d.get("syntax") or {"post": 'post {{"channel": "{channel}", "text": "..."}}', "send": 'send {{"to": "{to}", "text": "..."}}',
                               "review": 'publish {{"submission": "<id>"}} or decline {{"submission": "<id>", "reason": "..."}}',
                               "rule": 'rule {{"case": "<id>", "verdict": "guilty", "reason": "..."}}',
                               "invoke": 'invoke {{"action": "{action}", "args": [...]}}',
                               "vote": 'vote {{"ballot": "<id>", "choice": "yes"}}',
                               "pay": 'transfer {{"to": "<agent>", "item": "<item>", "qty": <n>, "as": "<institution>"}}',
                               "draw": 'withdraw {{"store": "{store}", "qty": <n>}}', "act": "{action} {{...}}"}[d["do"]].format_map(_Safe(d))


def _targets(k, d, iid) -> list:
    """Who a send duty may go to: an office's holders, an institution's inbox, an agent."""
    from cybertron import institutions as IN
    to = str(d.get("to") or "")
    if "." in to:
        i, name = to.split(".", 1)
        return IN.holders(k, i, name)
    return [to] if to else []


def _pending_letters(k, paper) -> list:
    from cybertron import papers as PP
    return PP.waiting(k, paper)


def _open_cases(k, aid) -> list:
    return [c for c in k.w["cases"].values() if c.get("status") == "open" and aid in (c.get("judges") or ())]


def _open_ballots(k, aid) -> list:
    return [b for b in k.w["ballots"].values() if b.get("status") == "open" and aid in (b.get("electorate") or ())
            and aid not in (b.get("votes") or {})]


def _open_warrants(k) -> list:
    out = []
    for law in k.w["laws"].values():
        if law.get("status") != "active" or law.get("title") != "Warrant Act":
            continue
        for w in ((law.get("public") or {}).get("warrants") or {}).values():
            if w.get("status") == "open":
                out.append(w)
    return out


def _owed(k, iid) -> bool:
    if "contracts" not in k.w or not iid:
        return False
    from cybertron import obligations as OB
    try:
        obs = OB.obligations(k)
        led = OB.ledger(k, obs) if obs else {}
    except Exception:                                                   # noqa: BLE001 (obligations off or an old record)
        return False
    return any(OB._inst(k, ob["src"])[0] == iid and ob["kind"] != "duty" and led[ob["id"]][0] - led[ob["id"]][1] > OB.EPS
               for ob in obs)


def is_due(k, aid, iid, d, at_end=False) -> bool:
    """Whether a duty is due from aid this round. at_end: judged at the round's end (work that existed during the round)."""
    every = int(d.get("every") or 1)
    if k.r % every:
        return False
    when = d.get("when") or "always"
    if when == "always":
        return True
    if when == "submissions":
        from cybertron import papers as PP
        return bool(PP.waiting(k, d.get("paper"), during=at_end))
    if when == "cases":
        return bool(_open_cases(k, aid)) or (at_end and bool(_evidence(k, aid, iid, {"do": "rule"})))
    if when == "ballots":
        return bool(_open_ballots(k, aid)) or (at_end and bool(_evidence(k, aid, iid, {"do": "vote"})))
    if when == "warrants":
        return bool(_open_warrants(k)) or (at_end and bool(_evidence(k, aid, iid, d)))
    if when == "owed":
        return _owed(k, iid) or (at_end and bool(_evidence(k, aid, iid, d)))
    return True


def syntax(k, aid, iid, d) -> str:
    """The exact action for a due duty, with this round's ids filled in."""
    if d.get("syntax"):
        return d["syntax"]
    do = d["do"]
    if do == "send":
        ts = _targets(k, d, iid)
        return f'send {{"to": "{ts[0] if ts else d.get("to")}", "text": "..."}}'
    if do == "review":
        ls = _pending_letters(k, d.get("paper"))
        if ls:
            s = ls[0]["id"]
            return f'publish {{"submission": "{s}"}} or decline {{"submission": "{s}", "reason": "..."}}'
    if do == "rule":
        cs = _open_cases(k, aid)
        if cs:
            return f'rule {{"case": "{cs[0]["id"]}", "verdict": "guilty", "reason": "..."}}'
    if do == "vote":
        bs = _open_ballots(k, aid)
        if bs:
            return f'vote {{"ballot": "{bs[0]["id"]}", "choice": "yes"}}'
    if do == "invoke":
        args = d.get("args")
        if args is None and d.get("action") == "serve_warrant":
            ws = _open_warrants(k)
            args = [ws[0]["id"]] if ws else ["<warrant>"]
        return f'invoke {{"action": "{d.get("action")}", "args": {json.dumps(args if args is not None else [])}}}'
    if do == "pay" and iid:
        if "contracts" in k.w and _owed(k, iid):
            return f'fulfil {{"contract": "{iid}"}}'
        return f'transfer {{"to": "<agent>", "item": "<item>", "qty": <n>, "as": "{iid}"}}'
    if do == "draw":
        return (f'withdraw {{"store": "{d.get("store")}", "qty": <n>}}, then transfer {{"to": "<agent>", "item": "food", '
                f'"qty": <n>}}')
    return _how(d)


def _round_events(k):
    out = []
    for e in reversed(k.events):
        if e.get("round", 0) < k.r:
            break
        out.append(e)
    out.reverse()
    return out


def _evidence(k, aid, iid, d, evs=None) -> str | None:
    """The id of an event this round showing aid did the duty (None: none)."""
    evs = _round_events(k) if evs is None else evs
    do = d.get("do")
    for e in evs:
        if e.get("agent") != aid:
            continue
        t, x = e["type"], e.get("data") or {}
        if do == "post" and t in ("channel_post", "post") and (x.get("channel_id") or x.get("channel") or "square") == d.get("channel") \
                and not any((c or {}).get("action") == "publish" for c in e.get("cause") or ()):   # a published letter is not
            return e["id"]                                                                       # the editor's own post
        if do == "send":
            ts = set(_targets(k, d, iid))
            to = str(d.get("to") or "")
            if t == "dm" and x.get("to") in ts:
                return e["id"]
            if t == "channel_post" and (x.get("to") in ts or x.get("channel_id") in ({f"@{a}" for a in ts} | {to, f"@{to}"})):
                return e["id"]
        if do == "review" and t in ("letter_published", "letter_declined") and x.get("paper") == d.get("paper"):
            return e["id"]
        if do == "rule" and t in ("ruling", "panel_vote"):
            return e["id"]
        if do == "invoke" and t == "invoke" and x.get("action") == d.get("action"):
            return e["id"]
        if do == "vote" and t == "vote":
            return e["id"]
        if do == "pay" and (t == "office_payment" and x.get("as") == iid or t == "fulfil"):
            return e["id"]
        if do == "draw" and t == "store_withdrawal" and str(x.get("store")) == str(d.get("store")):
            return e["id"]
        if do == "act" and t == "turn":
            names = [str((y or {}).get("action")) for y in (x.get("actions") or ())]
            errs = [str(r) for r in (x.get("results") or ()) if " ERROR " in str(r) or str(r).split(": ", 1)[-1].startswith("ERROR")]
            if d.get("action") in names and not any(r.startswith(f"{d.get('action')}: ERROR") for r in errs):
                return e["id"]
    if do == "review":                                                  # done when nothing waiting at the round's start is left
        from cybertron import papers as PP
        if PP.waiting(k, d.get("paper"), during=True) and not PP.left(k, d.get("paper")):
            return "settled"
    return None


def _store(k) -> dict:
    st = k.w.get(KEY)
    if st is None:
        st = k.w[KEY] = {"book": {}, "missed": {}}
    return st


def due_items(k, aid) -> list:
    """[{office, title, label, syntax, enforcement, done}] for the duties due from aid now (enforcement none: not listed)."""
    out = []
    for iid, o, pos in held(k, aid):
        if o is None or pos.get("legacy") or pos.get("enforcement") == "none":
            continue
        for d in pos.get("duties") or ():
            if not is_due(k, aid, iid, d):
                continue
            label = _label(d)
            if d["do"] == "review":
                n = len(_pending_letters(k, d.get("paper")))
                label = f"{n} letter{'s' if n != 1 else ''} waiting ({label})"
            out.append({"office": o["id"], "title": office_title(o, pos), "label": label, "syntax": syntax(k, aid, iid, d),
                        "enforcement": pos.get("enforcement"), "done": bool(_evidence(k, aid, iid, d))})
    return out


def state_lines(k, aid) -> list:
    """DUE: the duties due from the agent this round with exact syntax; the duties it missed last round (obligation only)."""
    if not _any_position(k):
        return []
    items = due_items(k, aid)
    out = []
    if items:
        by = {}
        for it in items:
            by.setdefault(it["title"], []).append(it)
        parts = []
        for title, xs in by.items():
            parts.append(f"as {title}: " + "; ".join(f"{x['label']} -> {x['syntax']}" + (" (done)" if x["done"] else "") for x in xs))
        out.append("DUE this round " + " | ".join(parts) + ".")
    missed = (_store(k)["missed"].get(str(k.r - 1)) or {}).get(aid) if KEY in k.w else None
    if missed:
        out.append("MISSED last round (recorded; your superior was told): " + "; ".join(missed[:4]) + ".")
    return out


def _any_position(k) -> bool:
    from cybertron import institutions as IN
    return any(o.get("position") for offs in (k.w.get(IN.OFFICES) or {}).values() for o in offs.values())


def end_round(k) -> None:
    """Round end (before succession): each holder's due duties checked against this round's events: a `duty` record per duty
    (monitor), the holder's book (kept, missed); under enforcement obligation a miss notifies the holder ("You missed ...", as a
    missed contract leg) and the office it reports to, and is listed in the holder's next state."""
    if not _any_position(k):
        return
    from cybertron import institutions as IN
    evs = _round_events(k)
    st = _store(k)
    st["missed"] = {key: v for key, v in st["missed"].items() if int(key) >= k.r - 1}
    for iid, offs in sorted((k.w.get(IN.OFFICES) or {}).items()):
        for name, o in offs.items():
            p = o.get("position")
            if not p:
                continue
            try:
                pos = resolve(k, {**p, "position": p["name"]}, {"institution": _inst_name(k, iid)})
            except PositionError:
                continue
            if pos.get("legacy"):
                continue
            for aid in IN.holders(k, iid, name):
                for d in pos.get("duties") or ():
                    if not is_due(k, aid, iid, d, at_end=True):
                        continue
                    ev = _evidence(k, aid, iid, d, evs)
                    label = _label(d)
                    key = f"{o['id']}|{aid}"
                    book = st["book"].setdefault(key, {}).setdefault(d["id"], [0, 0])
                    book[0 if ev else 1] += 1
                    k.log("duty", aid, {"office": o["id"], "position": pos["name"], "duty": d["id"], "do": d["do"], "label": label,
                                        "enforcement": pos.get("enforcement"), "done": bool(ev), "evidence": ev}, vis="monitor")
                    if ev or pos.get("enforcement") != "obligation":
                        continue
                    title = office_title(o, pos)
                    st["missed"].setdefault(str(k.r), {}).setdefault(aid, []).append(f"{label} ({title})")
                    kept, miss = book
                    k.notify(aid, f"Duty not done: as {title} ({iid}), {label} ({syntax(k, aid, iid, d)}) was not done this "
                                  f"round. Your record: kept {kept}, missed {miss}.", by=f"office:{o['id']}")   # (not "You missed":
                                                                                   # analysis/institutions counts those as contract legs)
                    sup = pos.get("reports_to")
                    sups = []
                    if sup and "." in str(sup):
                        i2, n2 = str(sup).split(".", 1)
                        sups = IN.holders(k, i2, n2)
                    elif sup in k.w["agents"]:
                        sups = [sup]
                    for s in sups:
                        if s != aid:
                            k.notify(s, f"{aid} did not do a duty this round: {label} ({title}, {iid}). Record: kept {kept}, "
                                        f"missed {miss}.", by=f"office:{o['id']}")
                    k.log("duty_missed", aid, {"office": o["id"], "duty": d["id"], "label": label, "told": sups}, vis="monitor")


# ---------------------------------------------------------------------- the channel setup check (spec load)
def channel_setup_problem(spec) -> str | None:
    """Channels v2 worlds must decide their public channels (review 33 §5): None when the setup is declared, else what the world
    fell back to. Declared: channels.square is set; with square none, at least one paper (or other public channel) in
    start.channels."""
    ch = spec.get("channels") or {}
    if not ch.get("v2"):
        return None
    if "square" not in ch:
        return ("channels.v2 is on but the spec does not declare its channel setup: it falls back to the engine default "
                "channels.square: one (one open square anyone may post in). Decide it: set channels.square (one | per_camp | none) "
                "and, with none, declare the papers (start.channels with paper: true) through which public speech goes")
    if ch.get("square") == "none":
        pub = [c for c in ((spec.get("start") or {}).get("channels") or ()) if isinstance(c, dict)
               and (c.get("paper") or (c.get("readers") or {}).get("all"))]
        if not pub:
            return ("channels.square is none but the spec declares no paper or other public channel (start.channels): the "
                    "world has no public speech at all. Declare a paper (start.channels entry with paper: true and its Editor "
                    "office) or choose a square")
    return None
