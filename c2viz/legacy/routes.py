"""Routes for a run made before the engine kept them: today's engine's rule (layout.route, D4-62) on the world at each work step's end."""
import json, sys
import c2viz.source as S, c2viz.touch as E
run, vizp = sys.argv[1], sys.argv[2]
R = S.open_run(run); v = json.load(open(vizp))
for rec in v["days"]:
    d, T = rec["day"], rec["timeline"]
    w = S.world_at(R, f"d{d}.work")
    T["routes"] = {n: r for n in w.agents_acting() if len(r := E.route(w, n)) > 1}
    T["routes_derived"] = True
json.dump(v, open(vizp, "w"), separators=(",", ":"), default=str)
print("routes", [len(x["timeline"]["routes"]) for x in v["days"]])
