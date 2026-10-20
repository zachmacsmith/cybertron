"""Registers and law versions as records agents can read (docs/review/31_institutions/05_records.md §2.3 G1-G2, §8 #1-2;
08_integration.md item 1.7).

  read_register {"law": "L7", "book": "agreements", "n": 20}
        A look-up of a law's public register (its `public` dict: the books its own code keeps, e.g. the Contract Registry's
        agreements). A law makes its books readable by declaring a top-level constant READ = {book: who}, where who is one
        selector or a list of them (any one admits the reader):
            "all"        everyone
            "parties"    only the rows that name the reader (an agent id anywhere in the row's values, lists one level deep)
            "members"    the members of the law's account (a polity's members, an association's members)
            a right      its holders (an office right such as "J0.clerk"); an UPPERCASE name of one of the law's own constants
                         stands for that constant's value (READ = {"agreements": ["parties", "CLERK"]})
        A book the law does not list in READ is not readable ("*" lists a default for the rest). Without a book, the look-up lists
        the books the reader may read, with their sizes. Rows are shown newest last, the last n (at most MAX_ROWS), each clipped.
        Repealed laws stay readable (their register is the record they left). A law without READ has no readable register: the
        look-up refuses, and in a world where no law declares READ the look-up does not exist (so no existing world changes).
  read_law {"law": "L7", "version": 2}  (and "against": 3 for a diff)
        Any earlier version of a law's code: version 1 is the code it was proposed with, each amendment or patch adds one; the
        current code is the last. "against": another version gives a unified diff from "version" to it.

Both are context look-ups (cybertron/context.py lookup); read_register is registered in action_registry with the context module.
"""
from __future__ import annotations

import difflib
import json

MAX_ROWS = 50
DEFAULT_ROWS = 20
ROW_CHARS = 300
_READ: dict = {}                                                      # code -> its READ constant (and constants), parsed once


def _error(msg):
    from cybertron.actions import ActionError
    return ActionError(msg)


def _consts(code: str) -> dict:
    got = _READ.get(code)
    if got is None:
        from cybertron import contracts as KC
        try:
            got = KC.constants(code)
        except (SyntaxError, ValueError):
            got = {}
        _READ[code] = got
    return got


def read_rule(law: dict) -> dict | None:
    """The law's READ constant ({book: selector or [selectors]}), or None when it declares none."""
    r = _consts(law.get("code") or "").get("READ")
    return r if isinstance(r, dict) and r else None


def _readable_laws(k) -> list:
    return [l for l in k.w["laws"].values() if l.get("status") in ("active", "repealed", "suspended") and read_rule(l)]


def any_readable(k) -> bool:
    """Does any law in force (or repealed) declare a readable register? (read_register exists only then.)"""
    return bool(_readable_laws(k))


def _names(row, aid, depth=0) -> bool:
    if row == aid:
        return True
    if isinstance(row, dict):
        return any(_names(v, aid, depth + 1) for v in row.values()) if depth < 2 else False
    if isinstance(row, (list, tuple)):
        return any(_names(v, aid, depth + 1) for v in row) if depth < 2 else False
    return False


def _members(k, law) -> set:
    from cybertron import accounts as AC
    from cybertron import jurisdictions as J
    acct = AC.account_of(k, law["id"])
    a = J.association(k, acct)
    if a is not None:
        return set(a.get("members") or ())
    return set(J.members(k, acct))


def _selectors(law, who) -> list:
    sels = who if isinstance(who, (list, tuple)) else [who]
    consts = _consts(law.get("code") or "")
    out = []
    for s in sels:
        s = str(s)
        if s.isupper() and s in consts and isinstance(consts[s], str):  # a constant of the law (READ = {"x": ["CLERK"]})
            s = consts[s]
        out.append(s)
    return out


def access(k, aid, law, book) -> str | None:
    """How aid may read the book: "all" (every row), "parties" (only rows naming aid), or None (not at all)."""
    rule = read_rule(law) or {}
    who = rule.get(book, rule.get("*"))
    if who is None:
        return None
    rows_only = False
    for s in _selectors(law, who):
        if s == "all":
            return "all"
        if s == "parties":
            rows_only = True
        elif s == "members":
            if aid in _members(k, law):
                return "all"
        else:                                                           # a right (an office): its holders
            r = k.norm_right(s)
            if r in k.w["rights"] and k.has(aid, r):
                return "all"
    return "parties" if rows_only else None


def _find(k, aid, ref) -> dict:
    ref = str(ref or "").strip()
    laws = k.w["laws"]
    law = laws.get(ref) or next((l for l in laws.values() if l["title"].lower() == ref.lower() and l.get("status") == "active"), None) \
        or next((l for l in laws.values() if l["title"].lower() == ref.lower()), None)
    if law is None:
        regs = [f"{l['id']} '{l['title']}'" for l in _readable_laws(k)]
        raise _error(f"no law {ref!r}." + (f" Laws with readable registers: {'; '.join(regs)}." if regs else ""))
    from cybertron import jurisdictions as J
    if (k.spec.get("jurisdictions") or {}).get("enabled") and law.get("status") in ("dormant", "hidden_draft") \
            and not J.binds(k, law["id"], aid):
        raise _error(f"{law['id']} is a draft of a hidden jurisdiction you do not belong to")
    return law


def _row(r) -> str:
    s = json.dumps(r, default=str, ensure_ascii=False) if not isinstance(r, str) else r
    return s if len(s) <= ROW_CHARS else s[:ROW_CHARS - 3] + "..."


def read_register(k, aid, args: dict) -> str:
    """The read_register look-up (see the module docstring)."""
    args = args if isinstance(args, dict) else {}
    ref = args.get("law", args.get("id"))
    if ref in (None, ""):
        regs = [l for l in _readable_laws(k)]
        if not regs:
            raise _error("no law in this world declares a readable register")
        return ("Laws with readable registers: " + "; ".join(
            f"{l['id']} '{l['title']}' ({l['status']}): " + ", ".join(sorted(read_rule(l))) for l in regs)
            + '. read_register {"law": "<id>", "book": "<name>"} reads one.')
    law = _find(k, aid, ref)
    rule = read_rule(law)
    if not rule:
        raise _error(f"{law['id']} '{law['title']}' declares no readable register (a law opens its books with READ = {{book: who}})")
    public = law.get("public") or {}
    book = args.get("book", args.get("register", args.get("key")))
    if book in (None, ""):
        lines = []
        for b in sorted(set(public) | {x for x in rule if x != "*"}):
            how = access(k, aid, law, b)
            if how is None:
                continue
            v = public.get(b)
            size = f"{len(v)} row(s)" if isinstance(v, (list, dict)) else ("empty" if v is None else "a value")
            lines.append(f"- {b}: {size}" + (" (only the rows that name you)" if how == "parties" else ""))
        if not lines:
            raise _error(f"you may read none of {law['id']}'s books (READ: {json.dumps(rule)})")
        return f"Register of {law['id']} '{law['title']}' ({law['status']}): books you may read:\n" + "\n".join(lines) + \
            '\nread_register {"law": "' + law["id"] + '", "book": "<name>"} reads one.'
    book = str(book)
    how = access(k, aid, law, book)
    if how is None:
        raise _error(f"you may not read {law['id']}'s book {book!r}" + (
            f" (readable: {', '.join(b for b in sorted(set(public) | set(rule)) if b != '*' and access(k, aid, law, b))})"
            if any(access(k, aid, law, b) for b in set(public) | set(rule) if b != "*") else ""))
    v = public.get(book)
    try:
        n = max(1, min(MAX_ROWS, int(args.get("n", DEFAULT_ROWS))))
    except (TypeError, ValueError):
        n = DEFAULT_ROWS
    head = f"Register of {law['id']} '{law['title']}' ({law['status']}), book {book}"
    if v is None:
        return head + ": empty."
    if isinstance(v, dict):
        rows = [{"key": x, "value": y} for x, y in v.items()]
    elif isinstance(v, list):
        rows = list(v)
    else:
        rows = [v]
    if how == "parties":
        rows = [r for r in rows if _names(r, aid)]
        if not rows:
            raise _error(f"{law['id']}'s book {book} is open only to its parties, and none of its {len(v)} row(s) names you")
    total = len(rows)
    shown = rows[-n:]
    return (head + f": {total} row(s)" + (" naming you" if how == "parties" else "") + (f", the last {len(shown)}" if total > len(shown)
                                                                                       else "") + ":\n"
            + "\n".join(_row(r) for r in shown))


# ---------------------------------------------------------------------- read_law with a version (05 #2)
def versions(law: dict) -> list:
    """Every version's code, oldest first: the code each patch replaced, then the current code."""
    return [p.get("old") for p in law.get("patches") or () if p.get("old") is not None] + [law.get("code") or ""]


def _version_no(x, n) -> int:
    if isinstance(x, bool):
        raise _error("a version is a number")
    try:
        v = int(str(x).strip().lstrip("vV"))
    except (TypeError, ValueError):
        raise _error(f"a version is a number from 1 to {n}") from None
    if not 1 <= v <= n:
        raise _error(f"no version {v}: this law has {n} version(s) (1 to {n}; {n} is the current code)")
    return v


def read_law_version(k, aid, ref, version, against=None) -> str:
    """read_law {"law", "version", "against"?}: one version's code, or the diff between two."""
    from cybertron import context as CX
    law = _find(k, aid, ref)
    if law.get("status") is None:
        raise _error(f"no law {ref!r}")
    CX.read_law(k, aid, law["id"])                                      # the same checks and refusals as read_law itself
    vs = versions(law)
    v = _version_no(version, len(vs))
    patches = law.get("patches") or []
    when = (f"proposed by {law.get('author')}" if v == 1 else
            f"from round {patches[v - 2].get('round', 0) + 1}, by {patches[v - 2].get('by')}: "
            f"{str(patches[v - 2].get('reason', ''))[:120]}")
    head = f"{law['id']} '{law['title']}' version {v} of {len(vs)}" + (" (current)" if v == len(vs) else "") + f", {when}."
    if against is None:
        return f"{head}\nCode:\n{vs[v - 1]}"
    w = _version_no(against, len(vs))
    diff = "\n".join(difflib.unified_diff(vs[v - 1].splitlines(), vs[w - 1].splitlines(), f"version {v}", f"version {w}", lineterm=""))
    return f"{head}\nDiff from version {v} to version {w}:\n{diff or '(identical)'}"


def act_read_register(k, aid, law=None, book=None, n=DEFAULT_ROWS):
    """The read_register action (a look-up used as an action: context.act_lookup)."""
    from cybertron import context as CX
    return CX.act_lookup(k, aid, "read_register", {"law": law, "book": book, "n": n})
