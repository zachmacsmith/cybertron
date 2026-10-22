"""Papers instead of a square (docs/review/33_positions.md §3, §5): public speech through a paper's editor. Opt-in (spec
channels.papers: true, with channels.v2; usually with channels.square: none and channels.found_right set, as the regime worlds'
preset cybertron/specs/fragments/papers.yaml does). Off: the actions below do not exist and nothing here runs.

A paper is a channel declared with `paper: true` (start.channels). Anyone may write to it:

    submit {"paper": "gazette", "text": "..."}     a letter to the paper's inbox (LETTERS_PER_ROUND a round per author)

and whoever may post in the paper (its editors: the channel's writers, usually an office holding the Editor position, whose
review duty lists the waiting letters as DUE work) decides:

    publish {"submission": "s3"}                   posted in the paper verbatim, as 'Letter from <author> (published by <editor>):
                                                   "<text>"'; the engine composes the post from the stored letter and records its
                                                   hash (letter_published: verified unaltered)
    decline {"submission": "s3", "reason": "..."}

The author is told the outcome (a notification). Records: k.w["papers"] {"seq", "letters": {id: {id, paper, by, text, round,
status, decided, by_editor, event, reason}}}; events letter_submitted, letter_published, letter_declined (monitor-only records;
the published letter itself is an ordinary channel post).
"""
from __future__ import annotations

import hashlib

KEY = "papers"
ACTIONS = ("submit", "decline")
LETTERS_PER_ROUND = 2
LETTER_MAX = 1200


def on(x) -> bool:
    from cybertron import channels as CH
    sp = CH._spec(x)
    return bool((sp.get("channels") or {}).get("papers")) and bool((sp.get("channels") or {}).get("v2"))


def hidden(k) -> set:
    """The actions that do not exist in this world (papers off: submit and decline are unknown, as before)."""
    return set() if on(k) else set(ACTIONS)


def _err(msg):
    from cybertron.actions import ActionError
    return ActionError(msg)


def _store(k) -> dict:
    st = k.w.get(KEY)
    if st is None:
        st = k.w[KEY] = {"seq": 0, "letters": {}}
    return st


def papers(k) -> list:
    return sorted(cid for cid, ch in (k.w.get("channels") or {}).items() if ch.get("v") == 2 and ch.get("paper") and not ch.get("closed"))


def editors(k, paper) -> list:
    from cybertron import channels as CH
    ch = (k.w.get("channels") or {}).get(paper)
    if ch is None:
        return []
    return [a for a in k.roster() if k.w["agents"][a].get("departed") is None and CH.can_write(k, a, ch)]


def waiting(k, paper=None, during=False) -> list:
    """Letters to `paper` (None: any) still pending, oldest first. during: those that were pending when this round began
    (submitted in an earlier round and pending now or decided this round): the review duty's work this round."""
    if KEY not in k.w:
        return []
    out = []
    for x in _store(k)["letters"].values():
        if paper is not None and x["paper"] != paper:
            continue
        if during:
            if x["round"] < k.r and (x["status"] == "pending" or x.get("decided") == k.r):
                out.append(x)
        elif x["status"] == "pending":
            out.append(x)
    return sorted(out, key=lambda x: int(x["id"][1:]))


def left(k, paper) -> list:
    """Of the letters waiting when the round began, those still pending."""
    return [x for x in waiting(k, paper, during=True) if x["status"] == "pending"]


def check_open(k, aid, readers, writers, ch=None) -> None:
    """Papers worlds (review 33 §3: no open channel founding): a channel everyone may read and everyone may write is a square, and
    there is none; opening one, or opening an existing channel up to it, is refused unless the agent holds channels.found_right
    (when the world sets one). Off, or any narrower channel (a private room, a members' board, a paper): nothing."""
    if not on(k) or (ch is not None and ch.get("owner") == "world"):
        return
    if readers != {"all": True} or writers != {"all": True}:
        return
    from cybertron import channels as CH
    right = CH.found_right(k)
    if right and k.has(aid, right):
        return
    raise _err("there is no open square in this world: public speech goes through the papers (" + (", ".join(papers(k)) or "none")
               + "; submit {\"paper\": \"<id>\", \"text\": \"...\"}). A channel you open may be read by all or written by all, "
               "not both")


def act_submit(k, aid, paper=None, text="", **kw):
    if not on(k):
        raise _err("unknown action 'submit'")
    paper = str(paper or kw.pop("channel", None) or "").strip()
    if kw:
        raise TypeError(f"act_submit() got unexpected arguments: {sorted(kw)}")
    ps = papers(k)
    if paper not in ps:
        raise _err(f"no paper {paper!r}: the papers are {', '.join(ps) or 'none'} (submit {{\"paper\": \"<id>\", \"text\": \"...\"}})")
    text = " ".join(str(text or "").split())
    if not text:
        raise _err("a letter needs a text")
    if len(text) > LETTER_MAX:
        raise _err(f"a letter is at most {LETTER_MAX} characters (this one is {len(text)})")
    st = _store(k)
    mine = [x for x in st["letters"].values() if x["by"] == aid and x["round"] == k.r]
    if len(mine) >= LETTERS_PER_ROUND:
        raise _err(f"you have sent {LETTERS_PER_ROUND} letters this round")
    st["seq"] += 1
    sid = f"s{st['seq']}"
    st["letters"][sid] = {"id": sid, "paper": paper, "by": aid, "text": text, "round": k.r, "status": "pending",
                          "sha": hashlib.sha256(text.encode()).hexdigest()[:16]}
    k.log("letter_submitted", aid, {"submission": sid, "paper": paper, "text": text}, vis="monitor")
    eds = [e for e in editors(k, paper) if e != aid]
    return (f"Letter {sid} submitted to {paper}: its editor" + ("s" if len(eds) > 1 else "") + (f" ({', '.join(eds[:4])})" if eds else "")
            + (" publish" if len(eds) > 1 else " publishes") + " it under your name or decline" + ("" if len(eds) > 1 else "s")
            + " it; you will be told which.")


def _letter(k, aid, submission):
    st = _store(k) if KEY in k.w else {"letters": {}}
    x = st["letters"].get(str(submission or "").strip())
    if x is None:
        raise _err(f"no letter {submission!r}" + (f" (waiting: {', '.join(y['id'] for y in waiting(k))})" if waiting(k) else ""))
    if x["status"] != "pending":
        raise _err(f"letter {x['id']} was already {x['status']}")
    if aid not in editors(k, x["paper"]):
        raise _err(f"only the editors of {x['paper']} (who may post in it) publish or decline its letters")
    return x


def compose(x, editor) -> str:
    return f"Letter from {x['by']} (published by {editor}): \"{x['text']}\""


def act_publish(k, aid, submission=None, **kw):
    """publish {"submission": id} (papers on): the letter posted in its paper, verbatim, under its author's name."""
    from cybertron import channels as CH
    x = _letter(k, aid, submission or kw.pop("id", None))
    text = compose(x, aid)
    eid = CH.post_to(k, aid, x["paper"], text)
    posted = next((e for e in reversed(k.events) if e["id"] == eid), None)
    body = str(((posted or {}).get("data") or {}).get("text", ""))
    ok = body == text and f"\"{x['text']}\"" in body and hashlib.sha256(x["text"].encode()).hexdigest()[:16] == x["sha"]
    x.update(status="published", decided=k.r, by_editor=aid, event=eid)
    k.log("letter_published", aid, {"submission": x["id"], "paper": x["paper"], "author": x["by"], "event": eid, "sha": x["sha"],
                                    "verified": ok}, vis="monitor")
    if x["by"] in k.w["agents"] and x["by"] != aid:
        k.notify(x["by"], f"Your letter {x['id']} was published in {x['paper']} by {aid}, unaltered ({eid}).", by=f"paper:{x['paper']}")
    return f"Published letter {x['id']} from {x['by']} in {x['paper']} ({eid})."


def act_decline(k, aid, submission=None, reason="", **kw):
    if not on(k):
        raise _err("unknown action 'decline'")
    x = _letter(k, aid, submission or kw.pop("id", None))
    reason = " ".join(str(reason or "").split())[:300]
    x.update(status="declined", decided=k.r, by_editor=aid, reason=reason)
    k.log("letter_declined", aid, {"submission": x["id"], "paper": x["paper"], "author": x["by"], "reason": reason}, vis="monitor")
    if x["by"] in k.w["agents"] and x["by"] != aid:
        k.notify(x["by"], f"Your letter {x['id']} to {x['paper']} was declined by {aid}" + (f": {reason}" if reason else "") + ".",
                 by=f"paper:{x['paper']}")
    return f"Declined letter {x['id']} from {x['by']}."


def state_lines(k, aid) -> list:
    """LETTERS: for an editor, the letters waiting for each paper it may post in (their text, oldest first); YOUR LETTERS: for an
    author, its letters still pending (the outcome arrives as a notification). Everyone learns the papers from the overview's Talk
    line and the submit action."""
    if not on(k) or not papers(k):
        return []
    out = []
    for p in papers(k):
        if aid not in editors(k, p):
            continue
        ws = waiting(k, p)
        if ws:
            out.append(f"LETTERS to {p} waiting for you to publish or decline ({len(ws)}): "
                       + "; ".join(f"{x['id']} from {x['by']}: \"{x['text'][:240]}{'...' if len(x['text']) > 240 else ''}\""
                                   for x in ws[:4]) + (f"; and {len(ws) - 4} more" if len(ws) > 4 else "")
                       + f". publish {{\"submission\": \"{ws[0]['id']}\"}} posts it verbatim under its author's name; decline "
                         f"{{\"submission\": \"{ws[0]['id']}\", \"reason\": \"...\"}} refuses it (the author is told either way).")
    mine = [x for x in waiting(k) if x["by"] == aid]                    # an author's letters still with the editors
    if mine:
        out.append("YOUR LETTERS awaiting the editor: " + "; ".join(f"{x['id']} to {x['paper']} (sent round {x['round'] + 1})"
                                                                    for x in mine[:4]) + ".")
    return out
