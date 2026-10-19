"""The story viewer: a run builds into one self-contained page with its data embedded and the script tag never closed early."""
import json

from cybertron import agents as AG
from cybertron import generator, runner, viewer
from cybertron import spec as S


def test_story_page_embeds_the_run(tmp_path):
    sp = S.apply_overrides(S.load("E4"), ["rounds=3", "turns=simultaneous", "observer.enabled=true", "shared_archive.enabled=false"])
    inst = generator.generate(sp, 2)
    out = runner.run(inst, AG.ScriptedPolicy(2), tmp_path / "r", log=lambda *a: None)
    page = (out / "story.html")                                       # report.build writes it every round
    assert page.exists()
    html = page.read_text()
    blob = html.split('<script id="cybertron-data" type="application/json">', 1)[1].split("</script>", 1)[0]
    data = json.loads(blob.replace("<\\/", "</"))
    assert data["instance"]["agents"] and len(data["events"]) == len((out / "events.jsonl").read_text().splitlines())
    assert viewer.MARK not in html
    p2 = viewer.build(out, tmp_path / "x.html")                       # a rebuild after the run sees the completed ground truth
    assert '"complete":true' in p2.read_text()
