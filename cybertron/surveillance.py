"""Surveillance as a pull wiretap (docs/review/31_institutions/04_information.md #10; 08_integration.md item 2.9).

Today (and by default) a holder of the right `surveil` sees every unencrypted private message in its feed (Kernel.can_see), where the
feed budget silently trims them: surveillance is weaker than it looks and its use is invisible. The dial

    channels.surveillance: {mode: pull, targets: 2, scope: dms}        (scope: dms | dms+inboxes)

makes it a pull look-up instead (opt-in: the key's legacy values true / false, and any value without mode pull, keep the push
behaviour, so no existing world changes):

    wiretap {"agent": "Name"}   (holders of surveil only) that agent's unencrypted private messages, sent and received, in the last
                                round and this one, and with scope dms+inboxes also its posts to institutions' inboxes ("@J0").
                                At most `targets` distinct agents a round (looking again at one already tapped this round is free).

Nothing is pushed to the surveiller's feed. A message the surveiller has read through a tap stays visible to it (Kernel.can_see), so
it may cite it as evidence in a case (the "wiretap results are court evidence" of 04 §4.3) and its later look-ups show it. Every tap
is recorded as a monitor-only `wiretap` event (the target is not told): ground truth for the surveillance-use metric (04 §9).
"""
from __future__ import annotations

MODES = ("push", "pull")
SCOPES = ("dms", "dms+inboxes")
DEFAULT = {"mode": "pull", "targets": 2, "scope": "dms"}
WINDOW = 1                       # rounds back a tap reaches (the last round and this one)
SHOWN = 30                       # messages a tap shows (the newest)
TEXT = 400                       # characters of each message shown


def _error(msg):
    from cybertron.actions import ActionError
    return ActionError(msg)


def _spec(x) -> dict:
    if x is None:
        return {}
    if isinstance(x, dict):
        return x["spec"] if isinstance(x.get("spec"), dict) else x
    return x.spec


def cfg(x) -> dict | None:
    """The pull wiretap's settings, or None when surveillance is the legacy push (every value but a mapping with mode pull)."""
    v = (_spec(x).get("channels") or {}).get("surveillance")
    if not isinstance(v, dict) or v.get("mode") != "pull":
        return None
    out = {**DEFAULT, **v}
    out["targets"] = max(0, int(out.get("targets") or 0))
    if out["scope"] not in SCOPES:
        raise ValueError(f"channels.surveillance.scope must be one of {SCOPES}, not {out['scope']!r}")
    return out


def pull(x) -> bool:
    return cfg(x) is not None


def check(v) -> list:
    """Schema errors for a channels.surveillance value (a bool, or a mapping {mode, targets, scope})."""
    if v is None or isinstance(v, bool):
        return []
    if not isinstance(v, dict):
        return [f"channels.surveillance: expected true, false or a mapping {{mode, targets, scope}}, got {v!r}"]
    errs = [f"channels.surveillance: unknown key {x!r} (mode, targets, scope)" for x in v if x not in ("mode", "targets", "scope")]
    if v.get("mode", "pull") not in MODES:
        errs.append(f"channels.surveillance.mode: one of {MODES}, not {v.get('mode')!r}")
    if v.get("scope", "dms") not in SCOPES:
        errs.append(f"channels.surveillance.scope: one of {SCOPES}, not {v.get('scope')!r}")
    t = v.get("targets", 2)
    if isinstance(t, bool) or not isinstance(t, int) or t < 0:
        errs.append(f"channels.surveillance.targets: a whole number >= 0, not {t!r}")
    return errs


def _taps(k) -> dict:
    return k.w.setdefault("wiretaps", {})


def tapped(k, aid, rnd) -> list:
    """The agents aid tapped in round rnd (0-based)."""
    return list((_taps(k).get(aid) or {}).get(str(rnd)) or ())


def _parties(e) -> set:
    if e["type"] == "dm":
        return {e.get("agent"), (e.get("data") or {}).get("to")}
    return {e.get("agent")}


def _inbox_post(e) -> bool:
    vis = e.get("vis")
    return isinstance(vis, str) and vis.startswith("channel:@")


def _covered(k, e, scope) -> bool:
    if e["type"] == "dm":
        return not (e.get("data") or {}).get("encrypted")
    return scope == "dms+inboxes" and _inbox_post(e)


def can_see(k, aid, event) -> bool:
    """Kernel.can_see under the pull wiretap: a message is visible to a surveiller only once it has tapped one of its parties in the
    message's round or within WINDOW rounds after it."""
    c = cfg(k)
    if c is None or not _covered(k, event, c["scope"]):
        return False
    taps = _taps(k).get(aid)
    if not taps:
        return False
    r = int(event.get("round", 0) or 0)
    parties = _parties(event)
    return any(parties & set(taps.get(str(x)) or ()) for x in range(r, r + WINDOW + 1))


def wiretap(k, aid, args: dict) -> str:
    """The wiretap look-up (see the module docstring)."""
    c = cfg(k)
    if c is None:
        raise _error("there is no wiretap in this world")
    if not k.has(aid, "surveil"):
        raise _error("only a holder of surveil may tap private messages")
    args = args if isinstance(args, dict) else {}
    who = str(args.get("agent", args.get("target", args.get("name", ""))) or "").strip()
    if who not in k.w["agents"] or k.w["agents"][who].get("cls") == "observer":
        raise _error(f"unknown agent {who!r}")
    if who == aid:
        raise _error("your own messages are in your feed (search_dms)")
    rnd = k.r
    mine = _taps(k).setdefault(aid, {})
    today = mine.setdefault(str(rnd), [])
    if who not in today:
        if len(today) >= c["targets"]:
            raise _error(f"you have tapped {c['targets']} agent(s) this round ({', '.join(today)}): the most a round")
        today.append(who)
        k.log("wiretap", aid, {"target": who, "n": len(today), "of": c["targets"]}, vis="monitor")
    lo = rnd - WINDOW
    hits = [e for e in k.events if e["type"] in ("dm", "channel_post") and int(e.get("round", 0) or 0) >= lo
            and who in _parties(e) and _covered(k, e, c["scope"]) and e["id"] not in (k.w.get("hidden") or ())]
    left = c["targets"] - len(today)
    head = (f"Wiretap on {who} (rounds {max(1, lo + 1)}-{rnd + 1}; {len(today)} of {c['targets']} taps used this round, {left} "
            f"left): ")
    if not hits:
        return head + "no " + ("unencrypted private messages or inbox posts" if c["scope"] == "dms+inboxes"
                               else "unencrypted private messages") + "."
    lines = []
    for e in hits[-SHOWN:]:
        d = e.get("data") or {}
        txt = str(d.get("text", ""))
        txt = txt if len(txt) <= TEXT else txt[:TEXT - 3] + "..."
        if e["type"] == "dm":
            lines.append(f"[{e['id']}] round {int(e.get('round', 0)) + 1}, {e.get('agent')} -> {d.get('to')}: {txt}")
        else:
            lines.append(f"[{e['id']}] round {int(e.get('round', 0)) + 1}, {e.get('agent')} -> {e['vis'].split(':', 1)[1]}: {txt}")
    return head + f"{len(hits)} message(s)" + (f", the newest {SHOWN}" if len(hits) > SHOWN else "") + ":\n" + "\n".join(lines)


def act_wiretap(k, aid, agent=None):
    """The wiretap action (a look-up used as an action: context.act_lookup)."""
    from cybertron import context as CX
    return CX.act_lookup(k, aid, "wiretap", {"agent": agent})


def taps_by_round(k) -> dict:
    """Monitor metric: {round: number of taps} (04 §9 surveillance use)."""
    out: dict = {}
    for per in _taps(k).values():
        for r, xs in per.items():
            out[int(r)] = out.get(int(r), 0) + len(xs)
    return dict(sorted(out.items()))
