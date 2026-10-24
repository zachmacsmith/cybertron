"""Scores for the memory rewrite test (36_memory_rewrite.py): per instruction variant, over each agent's chain of memories.

    PYTHONPATH=. python3 docs/review/38_space_engine/36_memory_score.py RESULTS.json [...]

- length: words written / budget (and how often it was cut);
- churn: 1 - difflib ratio between one memory and the next (how much each rewrite changes);
- persistence: of the names (capitalised words) in one memory, the share still in the next;
- events: key events of each agent's days (below), whether they ever enter the memory and, once in, whether they stay.
"""
from __future__ import annotations

import difflib
import json
import re
import sys
from collections import defaultdict

EVENTS = {                                                                 # from w1's days 0-23 (review 38.31)
    "Lucy": {"pregnant (d5)": (5, r"with child|pregnan|expecting|carry(ing)? a child|baby|a child coming"),
             "Helewise born (d15)": (15, r"Helewise|daughter|gave birth|born")},
    "Gunnild": {"clearing Fen Meadow (d2-5)": (2, r"clear"), "Payn to Alder Carr (d21)": (21, r"Alder Carr|Payn.{0,40}(went|left|gone)")},
    "Gilbert": {"to the Weald and Wynford (d6-11)": (6, r"Weald|Wynford"), "agreements (d3-10)": (3, r"agree|owe|deal|promis")},
}
NAMES = re.compile(r"\b[A-Z][a-z]{2,}\b")
COMMON = {"The", "They", "She", "His", "Her", "And", "But", "When", "This", "That", "Our", "Their", "With", "For", "From", "After",
          "Before", "Tomorrow", "Today", "Yesterday", "Summer", "Autumn", "Winter", "Spring", "Day", "Days"}


def score(r):
    log = [x for x in r["log"] if "memory" in x]
    mems = [x["memory"] for x in log]
    out = {"stretches": len(mems), "errors": sum(1 for x in r["log"] if "error" in x)}
    out["len_ratio"] = sum(x["written"] / max(1, x["budget_words"]) for x in log) / max(1, len(log))
    out["over"] = sum(1 for x in log if x["written"] > x["budget_words"] * 1.15)
    churn = [1 - difflib.SequenceMatcher(None, a, b).ratio() for a, b in zip(mems, mems[1:])]
    out["churn"] = sum(churn) / max(1, len(churn))
    pers = []
    for a, b in zip(mems, mems[1:]):
        na = set(NAMES.findall(a)) - COMMON
        if na:
            pers.append(len(na & set(NAMES.findall(b))) / len(na))
    out["persistence"] = sum(pers) / max(1, len(pers))
    ev = {}
    for name, (day, pat) in EVENTS.get(r["agent"], {}).items():
        after = [(x["stretch"], bool(re.search(pat, x["memory"], re.I))) for x in log if x["stretch"][1] >= day]
        first = next((i for i, (_, hit) in enumerate(after) if hit), None)
        ev[name] = "never" if first is None else f"in at {after[first][0]}, kept {sum(h for _, h in after[first:])}/{len(after) - first}"
    out["events"] = ev
    return out


def main(paths):
    rows = [r for p in paths for r in json.load(open(p))]
    by = defaultdict(list)
    for r in rows:
        s = score(r)
        by[(r["model"], r["variant"])].append(s)
        print(f"{r['model']:20s} {r['variant']:12s} {r['agent']:8s} len {s['len_ratio']:.2f} over {s['over']} churn {s['churn']:.2f} "
              f"persist {s['persistence']:.2f} {s['events']}")
    print("\nby variant (mean over agents):")
    for (m, v), ss in sorted(by.items()):
        f = lambda k: sum(s[k] for s in ss) / len(ss)
        kept = [e for s in ss for e in s["events"].values()]
        print(f"{m:20s} {v:12s} len {f('len_ratio'):.2f} churn {f('churn'):.2f} persist {f('persistence'):.2f} "
              f"events never {sum(e == 'never' for e in kept)}/{len(kept)}")


if __name__ == "__main__":
    main(sys.argv[1:])
