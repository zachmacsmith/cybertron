"""Documents: literacy, personal document stores, copies and confined access (docs/review/32_documents.md; behind spec flags, off by
default).

Built on cybertron/directories.py: a document is a file of a directory, and every agent's documents are one directory, the
agent's *personal store*, named by the agent's id (run scope; owner kind "personal"). What this module adds:

  literacy   `documents.literate` says who can write documents: "all" (default), "none", or a selector {agents, classes, roles,
             rights, profiles, officers}. It is read live: an agent who takes an office the selector names becomes literate, one
             who loses it stops being so. A literate agent owns its personal store (dir_write, dir_edit, dir_grant, ...).
  confined   a non-literate agent cannot write a document of its own. It reaches only what was given to it: copies that landed in
             its personal store (read; and it may pass a copy on) and the files other owners granted it (read, or write where
             granted: it may then edit that document, and nothing else).
  copies     doc_send {"dir", "path", "to"}: a copy of a file the sender can read lands in the recipient's personal store under
             received/<sender>/ (routed through the dir_write primitive, so a law.v2 before_dir_write hook may gate it). The copy
             carries its provenance (store meta: where it was copied from, its author, who sent it, the round and the hash at
             sending); an index line shows it, and shows "altered" once the text no longer matches. A copy cannot be recalled.
  live share the owner's dir_grant (read or write, on a file or a folder; access "none" revokes): unchanged.

Spec `documents: {enabled, literate, max_bytes, max_file_bytes, notice_chars}`. Off (the default) nothing here runs: the
directories, prompts and state of every existing world are unchanged.
"""
from __future__ import annotations

import copy
import hashlib

DEFAULTS = {
    "enabled": False,                    # personal document stores, literacy, doc_send
    "literate": "all",                   # "all" | "none" | {agents, classes, roles, rights, profiles, officers: bool}
    "max_bytes": 20_000,                 # a personal store's size limit (about 5,000 tokens; received copies count)
    "max_file_bytes": 4_000,             # one document (about 1,000 tokens, the old personal file's size)
    "notice_chars": 160,                 # the head of a copy quoted in the recipient's notice
}
SELECTOR_KEYS = ("agents", "classes", "roles", "rights", "profiles", "officers")
RECEIVED = "received/"
ACTIONS = ("doc_send",)                  # beside directories.ACTIONS, in documents worlds only
OWNER_KIND = "personal"


def _spec(x) -> dict:
    if x is None:
        return {}
    if isinstance(x, dict):
        return x["spec"] if isinstance(x.get("spec"), dict) else x
    return x.spec


def cfg(x) -> dict:
    out = copy.deepcopy(DEFAULTS)
    out.update(_spec(x).get("documents") or {})
    return out


def on(x) -> bool:
    return bool((_spec(x).get("documents") or {}).get("enabled"))


def check_literate(sel) -> None:
    if sel in ("all", "none"):
        return
    if not isinstance(sel, dict):
        raise ValueError(f"documents.literate must be \"all\", \"none\" or a selector {{{', '.join(SELECTOR_KEYS)}}}, not {sel!r}")
    bad = sorted(set(sel) - set(SELECTOR_KEYS))
    if bad:
        raise ValueError(f"documents.literate: unknown key(s) {', '.join(bad)}; keys: {', '.join(SELECTOR_KEYS)}")


# ====================================================================== literacy
def _right_match(rights, pats) -> bool:
    for p in pats or ():
        p = str(p)
        if p.endswith("*") and any(str(r).startswith(p[:-1]) for r in rights):
            return True
        if p in rights:
            return True
    return False


def _selects(sel, a, roles, rights, officer) -> bool:
    if sel == "all":
        return True
    if sel == "none" or not isinstance(sel, dict):
        return False
    classes = {a.get("cls")} | set(a.get("also") or ())
    return bool(a.get("id") in (sel.get("agents") or ()) or classes & set(sel.get("classes") or ())
                or set(roles) & set(sel.get("roles") or ()) or _right_match(rights, sel.get("rights"))
                or set(a.get("profiles") or ()) & set(sel.get("profiles") or ()) or (sel.get("officers") and officer))


def _officer(k, aid) -> bool:
    from cybertron import institutions as IN
    return any(aid in IN.officers(k, iid) for iid in (k.w.get(IN.OFFICES) or {}))


def literate(k, aid) -> bool:
    """Can this agent write documents now? (Live: roles, rights and offices as they stand; a departed agent cannot.)"""
    a = k.w["agents"].get(aid)
    if not a or a.get("departed") is not None or a.get("cls") == "observer":
        return False
    sel = cfg(k)["literate"]
    if sel in ("all", "none"):
        return sel == "all"
    from cybertron import roles as RO
    roles = [r for r in RO.ROLES if RO.has_role(k, aid, r)]
    prof = next((x for x in k.inst["agents"] if x["id"] == aid), {}) if getattr(k, "inst", None) else {}
    rights = [r for r in a.get("rights", []) if k.has(aid, r)]
    return _selects(sel, {**a, "profiles": prof.get("profiles") or a.get("profiles")}, roles, rights,
                    bool(sel.get("officers")) and _officer(k, aid))


def literate_static(inst, a) -> bool:
    """Literacy from the instance alone (the system prompt written before a kernel exists): offices are not known yet."""
    if a.get("cls") == "observer":
        return False
    sel = cfg(inst)["literate"]
    holders = ((inst.get("roles") or {}).get("holders") or {}) if isinstance(inst, dict) else {}
    roles = [r for r, hs in holders.items() if a["id"] in (hs or ())]
    return _selects(sel, a, roles, a.get("rights") or [], False)


# ====================================================================== personal stores
def store_name(k, aid) -> str:
    return ((k.w.get("doc_stores") or {}).get(aid)) or aid


def is_personal(d) -> bool:
    return d.get("personal") is not None


def _new_store(k, aid) -> dict:
    c = cfg(k)
    return {"owner": f"{OWNER_KIND}:{aid}", "personal": aid, "scope": "run", "namespace": None,
            "max_bytes": int(c["max_bytes"]), "max_file_bytes": int(c["max_file_bytes"]), "records": False,
            "title": f"{aid}'s documents", "readonly": [], "files": {}, "grants": {}, "meta": {}}


def ensure(k, aid) -> str | None:
    """The agent's personal store (made on first need: agents born later get theirs the same way). Its name is the agent's id,
    or <id>-docs where a directory of that name exists. None when documents are off or the agent is not a player."""
    if not on(k):
        return None
    a = k.w["agents"].get(aid)
    if not a or a.get("cls") == "observer":
        return None
    dirs = k.w.setdefault("dirs", {})
    names = k.w.setdefault("doc_stores", {})
    if aid in names:
        return names[aid]
    name = aid if aid not in dirs else f"{aid}-docs"
    dirs[name] = _new_store(k, aid)
    names[aid] = name
    return name


def install(k) -> None:
    """Kernel construction (after directories.install): a personal store for every player. Off: nothing."""
    if not on(k):
        return
    check_literate(cfg(k)["literate"])
    for aid in sorted(k.w["agents"]):
        ensure(k, aid)


def owner_access(k, aid, d) -> bool:
    """directories.is_owner for a personal store: its agent, while literate."""
    return d.get("personal") == aid and literate(k, aid)


def own_papers(k, aid, d) -> str:
    """directories.level for a non-literate agent's own store: read once it holds something (received copies), else none."""
    return "read" if d.get("personal") == aid and d["files"] else "none"


# ====================================================================== provenance
def _sha(text) -> str:
    return hashlib.sha256(str(text).encode()).hexdigest()


def tag(d, path) -> str:
    """The index note of a copied file: where it came from, and whether it was altered since."""
    m = (d.get("meta") or {}).get(path)
    if not m:
        return ""
    by = f", written by {m['author']}" if m.get("author") else ""
    altered = "; altered since it was received" if _sha(d["files"].get(path, "")) != m.get("sha") else ""
    return f"; a copy of {m['from']}{by}, sent by {m['sent_by']} in round {m['round'] + 1}{altered}"


def author_of(d, path):
    """The recorded author of a file: the original's author for a copy; the owner of a personal store; else None."""
    m = (d.get("meta") or {}).get(path)
    if m:
        return m.get("author")
    return d.get("personal")


# ====================================================================== doc_send
def _dest(files, sender, path) -> str:
    base = path.rsplit("/", 1)[-1]
    stem, dot, ext = base.rpartition(".")
    stem, ext = (stem, "." + ext) if dot and stem else (base, "")
    out, n = f"{RECEIVED}{sender}/{base}", 2
    while out in files:
        out = f"{RECEIVED}{sender}/{stem}-{n}{ext}"
        n += 1
    return out


def doc_send(k, aid, dir=None, path=None, to=None) -> str:
    """A copy of a file the sender can read, into the recipient's personal store (received/<sender>/...). The recipient is told,
    with the head of the text. Literacy is not needed to pass a copy on (a paper can be handed over by anyone who holds it)."""
    from cybertron import directories as DR
    if not on(k):
        raise DR._err("unknown action 'doc_send'")
    name, d = DR._pick(k, aid, dir)
    p = DR.norm_path(path)
    if p not in d["files"]:
        raise DR._err(f"no file {p} in {name} (dir_list lists them)")
    DR._need(k, aid, d, p, "read")
    who = str(to or "")
    ta = k.w["agents"].get(who)
    if ta is None or who == aid or ta.get("cls") == "observer" or ta.get("departed") is not None:
        raise DR._err(f"unknown recipient {who!r}")
    rname = ensure(k, who)
    rd = k.w["dirs"][rname]
    text = d["files"][p]
    dest = _dest(rd["files"], aid, p)
    try:
        DR._check_size(rd, dest, text)
    except Exception as e:
        raise DR._err(f"{who}'s documents cannot take this copy: {e}")
    meta = {"from": f"{name}/{p}", "author": author_of(d, p), "sent_by": aid, "round": k.r, "sha": _sha(text)}
    DR._apply(k, "dir_write", agent=aid, dir=rname, path=dest, op="write", text=text, meta=meta)
    n = int(cfg(k)["notice_chars"])
    head = " ".join(text.split())
    head = head if len(head) <= n else head[:n - 3] + "..."
    k.notify(who, f"{aid} sent you a copy of {name}/{p} ({len(text.encode())} bytes): \"{head}\" It is in your documents as "
             f"{rname}/{dest}; read it with dir_read {{\"dir\": \"{rname}\", \"path\": \"{dest}\"}}.", by=aid)
    return f"Sent {who} a copy of {name}/{p} (it is {rname}/{dest} in their documents; you cannot take it back)."


# ====================================================================== prompt
def heading(k, aid, name, d) -> str | None:
    """turn_section's header for a personal store (None: not a personal store)."""
    if not is_personal(d):
        return None
    size = f"{len(d['files'])} file(s), {sum(len(t.encode()) for t in d['files'].values())} of {d['max_bytes']} bytes"
    if d["personal"] == aid:
        if literate(k, aid):
            return f"{name} (your documents; {size}):"
        return (f"{name} (documents given to you; you cannot write documents of your own, only read these and pass copies on "
                f"with doc_send; {size}):")
    from cybertron import directories as DR
    return f"{name} ({d['personal']}'s documents; shared with you: {DR.level(k, aid, d)}; {size}):"


def role_line(k, aid) -> str:
    """The one line the turn prompt adds under "Your directories" in a documents world."""
    if literate(k, aid):
        return ("You can write documents (dir_write in your own store, \"dir\": \"" + store_name(k, aid) + "\"), give a copy "
                "(doc_send) or let someone read or edit one live (dir_grant; access none revokes).")
    return ""
