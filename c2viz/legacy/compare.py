import json, sys
pub, rep = sys.argv[1], sys.argv[2]
P = [json.loads(l) for l in open(f"{pub}/days.jsonl")]
R = [json.loads(l) for l in open(f"{rep}/days.jsonl")]
skip = {"cost_usd", "errors"}
bad = 0
for d, r in enumerate(R):
    p = P[d]
    diffs = [k for k in sorted(set(p) | set(r)) if k not in skip and json.dumps(p.get(k), sort_keys=True) != json.dumps(r.get(k), sort_keys=True)]
    if diffs:
        bad += 1
        print("day", d, "differs:", diffs)
        for k in diffs[:3]:
            print("  pub", json.dumps(p.get(k), sort_keys=True)[:300]); print("  rep", json.dumps(r.get(k), sort_keys=True)[:300])
TP = {(t["day"], t["agent"], bool(t.get("on_road"))): t for t in map(json.loads, open(f"{pub}/turns.jsonl"))}
tb = 0
for t in map(json.loads, open(f"{rep}/turns.jsonl")):
    p = TP.get((t["day"], t["agent"], bool(t.get("on_road"))))
    for k in ("results", "night", "plan", "used", "units", "at"):
        if p is None or p.get(k) != t.get(k):
            tb += 1
            if tb <= 8:
                print("turn", t["day"], t["agent"], k); print("  pub", json.dumps(p and p.get(k))[:400]); print("  rep", json.dumps(t.get(k))[:400])
print(f"days {len(R)}: {bad} differ; turn fields differing {tb}")
