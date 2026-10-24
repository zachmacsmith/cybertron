"""Memory rewritten (cybertron2/engine/memory.py, under test; review 38.36): one memory, rewritten each stretch within a length that
grows with age, largest rises early; nothing kept by the engine on the agent's behalf."""
import json

from cybertron2.engine import memory as M, run as R
from cybertron2.engine.world import load_spec

SPEC = "cybertron2/specs/valley_s5.yaml"


def test_the_budget_grows_over_a_life_and_levels_off():
    b = [M.budget_tokens(a, 64) for a in range(0, 65, 8)]
    steps = [y - x for x, y in zip(b, b[1:])]
    assert b[0] == M.DEFAULTS["lo"] and b[-1] == M.DEFAULTS["hi"]
    assert all(s > 0 for s in steps) and all(s2 < s1 for s1, s2 in zip(steps, steps[1:]))   # rising, by less each time
    assert M.budget_tokens(200, 64) == M.DEFAULTS["hi"]


def test_a_memory_is_cut_back_only_when_well_over():
    text = "One thing. " * 60                                              # 120 words
    assert M.cut(text, 110) == " ".join(text.split())                       # within the slack: as written
    assert M.cut(text, 50).endswith("thing.") and len(M.cut(text, 50).split()) <= 50


def test_in_rewrite_mode_the_memory_is_replaced_and_shown_alone(tmp_path, monkeypatch):
    from cybertron import llm
    calls = []

    def api(model, system, user, schema, thinking_budget, max_tokens):
        u = str(user)
        calls.append(u)
        if "## Your memory as it stands" in u:
            n = sum("## Your memory as it stands" in c for c in calls)
            raw = json.dumps({"why": "", "actions": [], "memory": f"Version {n}: the barley is late."})
        else:
            raw = json.dumps({"why": "steady", "actions": [{"do": "gather", "what": "forage"}]})
        return raw, json.loads(raw), "", {}
    monkeypatch.setattr(llm, "_api", api)
    spec = load_spec(SPEC)
    spec["memory"] = {"mode": "rewrite", "chunk": 2}
    p = tmp_path / "spec.json"
    p.write_text(json.dumps(spec))
    monkeypatch.setattr(R, "load_spec", lambda path: json.loads(open(path).read()))
    R.run(str(p), tmp_path / "run", backend="api", days=5)
    st = json.loads((tmp_path / "run" / "state.json").read_text())
    mem = {n: m.get("memory") for n, m in st["mind"].items() if m.get("memory")}
    assert mem and all(x["text"].startswith("Version") for x in mem.values()) and all(not m.get("own") for m in st["mind"].values())
    asks = [c for c in calls if "## Your memory as it stands" in c]
    assert any("Version" in c.split("## Your memory as it stands")[1][:200] for c in asks)        # the old one is put before them
    later = [c for c in calls if "## Your memory (in your own words)" in c]
    assert later and not any("## Your own memory of recent days" in c for c in calls)
