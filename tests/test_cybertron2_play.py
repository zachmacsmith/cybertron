"""R3 of the run record (spec/record/human_play.md): a person plays an agent, through a thin API (terminal, HTTP, anything)."""
import json
import socket
import threading
import time
import urllib.request

from cybertron2.engine import api as API, run as R, views as VW

SPEC = "cybertron2/specs/valley_s5.yaml"


def _human_run(tmp_path, days=2):
    out = tmp_path / "play"
    R.run(SPEC, out, days=days, bots=True, responders={"Edric": "human"})
    return out


def test_a_person_is_shown_what_a_model_would_be_and_the_run_waits_for_them(tmp_path):
    out = _human_run(tmp_path)
    st = API.status(out)
    assert [w["agent"] for w in st["waiting"]] == ["Edric"] and not st["ended"] and st["at"] == "d0.dawn"
    key = st["waiting"][0]["key"]
    ctx = API.context(out, key)
    assert key == "d0.decide.Edric.1" and "## Now" in ctx["message"] and ctx["system"] and ctx["schema"]["type"] == "object"
    assert API.answer(out, key, {"actions": "gather forage"})                 # refused by the schema: nothing stored
    assert API.answer(out, key, {"why": "I'll forage.", "actions": [{"do": "gather", "what": "forage"}]}) == []
    st = API.advance(out)
    kinds = []
    while st["waiting"]:                                                   # every request a model would get: decisions, memories
        req = st["waiting"][0]
        kinds.append(req["kind"])
        ctx = API.context(out, req["key"])
        if req["key"] == "d0.memory.Edric.1":                                # the end of his stretch: his own reply is in it
            assert json.loads(ctx["turns"][0]["reply"])["why"] == "I'll forage."
        if req["key"] == "d1.decide.Edric.1":                                # and a new stretch starts from what he remembers
            assert not ctx["turns"] and "I foraged." in ctx["message"]
        reply = {"why": "The day is done.", "actions": [], "memory": "I foraged."} if req["kind"] == "memory" else {"why": "Again.", "actions": [{"do": "gather", "what": "forage"}]}
        assert API.answer(out, req["key"], reply) == []
        st = API.advance(out)
    assert "memory" in kinds and st["ended"]
    assert R.run(None, out, mode="replay")["mismatches"] == []                # a person's answers replay like any other


def test_the_same_over_http(tmp_path):
    out = _human_run(tmp_path, days=1)
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    threading.Thread(target=API.serve, args=(out, port), daemon=True).start()
    base = f"http://127.0.0.1:{port}"
    for _ in range(50):
        try:
            st = json.loads(urllib.request.urlopen(base + "/status").read())
            break
        except OSError:
            time.sleep(0.1)
    key = st["waiting"][0]["key"]
    assert "## Now" in json.loads(urllib.request.urlopen(f"{base}/context/{key}").read())["message"]
    assert b"Play an agent" in urllib.request.urlopen(base + "/").read()
    req = urllib.request.Request(f"{base}/answer/{key}", data=json.dumps({"why": "x", "actions": []}).encode(), method="POST")
    assert json.loads(urllib.request.urlopen(req).read())["problems"] == []
    for _ in range(100):
        st = json.loads(urllib.request.urlopen(base + "/status").read())
        if st["ended"] and not st["advancing"]:
            break
        time.sleep(0.1)
    assert st["ended"] and VW.requests(out, pending=True) == []
