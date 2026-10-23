"""Each agent's conversation, as cybertron 1's history mode (cybertron/memory.py, agents.LLMPolicy._history and _send): an agent's
calls over a stretch of `chunk` days form one conversation, so its own earlier replies (its plans and stated reasons) stay in
context, and on the CLI one `claude -p` session per conversation serves everything before the new message from the prompt cache.
Conversations restart at days staggered per agent; the opening message carries what it remembers, including the memory it wrote
itself at the end of the last stretch (perceive.own_memory).

The system prompt and the schema are frozen for a conversation (on --resume the CLI keeps the first call's system prompt, and the
schema leads the cached prefix); a changed schema (someone died) restarts it. When a session cannot be continued, llm.call sends the
whole conversation as one prompt (the Turn's fallback) and the next call seeds a new session with it.
"""
from __future__ import annotations

import json
import threading
import zlib


class Conversations:
    def __init__(self, out_dir, chunk=3, backend="claude_code"):
        from cybertron import llm
        self.llm = llm
        self.sessions = llm.Sessions(out_dir) if backend == "claude_code" else None
        self.chunk = max(1, int(chunk))
        self.c = {}
        self.lock = threading.Lock()

    def offset(self, name) -> int:
        return zlib.crc32(name.encode()) % self.chunk

    def starts(self, name, day) -> bool:
        return day == 0 or (day - self.offset(name)) % self.chunk == 0

    def ends(self, name, day) -> bool:
        """The last day of this agent's stretch: its memory is written tonight."""
        return self.starts(name, day + 1)

    def system(self, name, fresh):
        """The system prompt of the agent's running conversation (frozen), or `fresh` when none is running."""
        c = self.c.get(name)
        return c["system"] if c else fresh

    def message(self, name, day, system, schema, text, opening):
        """What to send for this call, and the context for after(). `opening` is the self-contained text that starts a
        conversation (what it remembers, then the day)."""
        key = json.dumps(schema, sort_keys=True)
        with self.lock:
            c = self.c.get(name)
            if c is None or c["schema"] != key or (self.starts(name, day) and c["day0"] != day):
                self.end(name)
                c = self.c[name] = {"day0": day, "system": system, "schema": key, "messages": [], "session": None}
                text = opening
            msgs = list(c["messages"])
        flat = self.llm.flatten(msgs + [text])
        if self.sessions is None or not self.sessions.usable:
            return flat, {"conv": c, "text": text, "transport": "flattened"}
        if c["session"] and msgs:
            turn = self.llm.Turn(text, history=msgs, fallback=flat, sessions=self.sessions, session=c["session"])
        else:                                                            # start, or reseed after a failed continuation
            turn = self.llm.Turn(flat, fallback=flat, sessions=self.sessions, session=self.sessions.new_id())
        return turn, {"conv": c, "text": text, "transport": "cached-session"}

    def after(self, ctx, reply_raw, usage) -> dict:
        """Keep the exchange in the conversation. Returns the usage with how it was sent."""
        c = ctx["conv"]
        with self.lock:
            c["messages"] += [ctx["text"], reply_raw if reply_raw else json.dumps({"why": "(no reply)", "actions": []})]
            turn = (usage or {}).get("turn")
            c["session"] = (usage or {}).get("session") if turn in ("start", "continued") else None
        return {**(usage or {}), "history": "flattened" if turn == "fallback" else ctx["transport"]}

    def end(self, name) -> None:
        c = self.c.pop(name, None)
        if c and c.get("session") and self.sessions is not None:
            self.sessions.drop(c["session"])

    def close(self) -> dict:
        return self.sessions.collect() if self.sessions is not None else {}
