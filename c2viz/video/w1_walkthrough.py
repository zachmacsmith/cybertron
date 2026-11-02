"""A walk-through video of w1_wide days 0-23: per day the region, then the busiest places close up through the day.

    python3 render.py VIDEO_DIR HF_RUN_DIR OUT.mp4 [--days N] [--stills]
"""
import base64, json, re, subprocess, sys
from collections import Counter
from pathlib import Path
from playwright.sync_api import sync_playwright

vd, hf, outp = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
ndays = int(sys.argv[sys.argv.index("--days") + 1]) if "--days" in sys.argv else 24
stills = "--stills" in sys.argv
FPS = 12
V = json.load(open(vd / "viz.json"))
DAYS = [json.loads(l) for l in open(hf / "days.jsonl")]
TURNS = [json.loads(l) for l in open(hf / "turns.jsonl")]
NODES = V["static"]["nodes"]
PEOPLE = V["meta"]["people"]


def model_word(m):
    m = m or ""
    x = re.match(r"claude-([a-z]+)-(\d+)-(\d+)", m)
    return f"{x.group(1).capitalize()} {x.group(2)}.{x.group(3)}" if x else m


HOUSE_MODEL = {}
for n, p in PEOPLE.items():
    if p.get("model") and p.get("household"):
        HOUSE_MODEL.setdefault(p["household"], model_word(p["model"]))


def cal(rec):
    c = rec["calendar"]
    return f"{c['season'].capitalize()}, day {c['day']} of the season · {rec.get('words') or rec.get('weather')}"


def plural(h):
    return f"the {h}s" if not h.endswith("s") else f"the {h}es"


def headlines(d, rec):
    D = DAYS[d]
    out = []
    for x in D.get("deaths") or []:
        nm = x if isinstance(x, str) else (x.get("name") or x.get("who"))
        c = x.get("cause") if isinstance(x, dict) else (rec["people"].get(nm) or {}).get("cause")
        cause = f" ({c})" if c else ""
        out.append(f"{nm} died{cause}")
    life = D.get("life") or {}
    for b in life.get("births") or []:
        out.append(f"{b.get('child')} was born to {b.get('mother') or b.get('parents')}")
    for c in life.get("conceived") or []:
        out.append(f"{c if isinstance(c, str) else c.get('mother')} conceived")
    ev = rec["events"]
    seen = set()
    for e in ev:
        if e["kind"] in ("arrive", "depart", "build", "birth", "grown", "claim", "fence") and e["text"] not in seen and e.get("salience", 0) >= 0.3:
            seen.add(e["text"]); out.append(e["text"])
    if D.get("agreements_made"):
        out.append(f"{len(D['agreements_made'])} agreement{'s' if len(D['agreements_made']) > 1 else ''} made")
    if D.get("missed"):
        out.append("went hungry: " + ", ".join(D["missed"]))
    return out[:5]


def quotes(d, nid):
    qs = []
    for t in TURNS:
        if t["day"] != d or t.get("at") != nid:
            continue
        for r in t.get("results") or []:
            m = re.match(r"You told ([^:]+): (.*)", r) or re.match(r"You said \(([^)]*)\): (.*)", r)
            if m and 30 < len(m.group(2)) < 260:
                qs.append(f"{t['agent']} to {m.group(1)}: “{m.group(2)}”")
    return qs


def who_at(rec, nid):
    hs = Counter(PEOPLE.get(n, {}).get("household") for n, p in rec["people"].items() if p.get("at") == nid and p.get("alive"))
    return ", ".join(f"{plural(h)} ({HOUSE_MODEL.get(h, '?')})" for h, _ in hs.most_common() if h)


def places(d, rec):
    T = rec.get("timeline") or {}
    acts = Counter(a.get("node") for a in T.get("acts") or [])
    hot = {e["place"] for e in rec["events"] if e["kind"] in ("arrive", "death", "birth", "build")}
    score = {n: acts.get(n, 0) + (40 if n in hot and acts.get(n, 0) else 0) for n in NODES}
    return [n for n, s in sorted(score.items(), key=lambda x: -x[1]) if s >= 3][:3]


def clock(t):
    if t < 0: return "before work: talk"
    if t < 0.34: return "morning"
    if t < 0.67: return "midday"
    if t <= 1.0: return "afternoon"
    return "night"


def plan():
    segs, chapters = [], []
    segs.append(("card", [["The Wide Country", 64, "#e0b25a"], ["run w1 · seven households, one model each · 23 people", 28],
                          ["days 1 to 24 of the run (day 25 on, the usage limit: nobody acted)", 24, "#a99c80"],
                          ["replayed from the published replies on the engine it ran on; every change replays", 22, "#a99c80"]], 4 * FPS))
    chapters.append(("The Wide Country", 0))
    for d in range(ndays):
        rec = V["days"][d]
        chapters.append((f"Day {d + 1}", len(segs)))
        title = f"Day {d + 1} of 24"
        heads = headlines(d, rec)
        segs.append(("world", {"kind": "world", "day": d, "scale": 1, "title": title, "sub": cal(rec), "lines": heads or ["no travel, building, births, deaths or agreements today"],
                               "foot": "the region (places drawn larger, roads shorter than travel days)"}, int(2.5 * FPS)))
        for nid in places(d, rec):
            qs = quotes(d, nid)
            n = 4 * FPS
            for i in range(n):
                t = -0.12 + 1.3 * i / (n - 1)
                q = qs[0 if i < n // 2 or len(qs) < 2 else 1] if qs else None
                segs.append(("node", {"kind": "node", "nid": nid, "day": d, "t": t, "scale": 3, "title": f"{NODES[nid]['name']} · day {d + 1}",
                                      "sub": who_at(rec, nid), "clock": clock(t), "quote": q,
                                      "foot": "people walk the engine's route rule (D4-62) between their acts; acts land in the journal's order"}, 1))
    segs.append(("card", [["Day 25: the usage limit", 48, "#e0b25a"], ["every model call failed from about 13:10 UTC;", 26],
                          ["the run went on with nobody acting, so days 25 to 73 say nothing about the agents", 26],
                          ["(review 38.31)", 22, "#a99c80"]], 4 * FPS))
    chapters.append(("Day 25: the usage limit", len(segs) - 1))
    return segs, chapters


def main():
    segs, chapters = plan()
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
        pg = b.new_page(viewport={"width": 1920, "height": 1080})
        pg.on("pageerror", lambda e: print("page error:", e))
        pg.goto("file://" + str((vd / "page.html").resolve()))
        if stills:
            picks = [s for s in segs if s[0] == "world"][:1] + [s for s in segs if s[0] == "node" and abs(s[1]["t"] - 0.5) < 0.02][:3] + [segs[0]]
            for i, (k, x, _) in enumerate(picks):
                url = pg.evaluate("c => card(c)", x) if k == "card" else pg.evaluate("s => draw(s)", x)
                (vd / f"still_{i}.png").write_bytes(base64.b64decode(url.split(",", 1)[1]))
            print("stills", len(picks)); return
        meta = vd / "chapters.txt"
        frame_of, total = [], 0
        for k, x, n in segs:
            frame_of.append(total); total += n
        lines = [";FFMETADATA1", "title=The Wide Country, run w1, days 1 to 24"]
        for j, (name, si) in enumerate(chapters):
            start = frame_of[si] * 1000 // FPS
            end = (frame_of[chapters[j + 1][1]] * 1000 // FPS) if j + 1 < len(chapters) else total * 1000 // FPS
            lines += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={start}", f"END={end}", f"title={name}"]
        meta.write_text("\n".join(lines) + "\n")
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "png", "-i", "-",
                               "-i", str(meta), "-map_metadata", "1", "-map_chapters", "1", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                               "-pix_fmt", "yuv420p", "-r", str(FPS), "-movflags", "+faststart", outp], stdin=subprocess.PIPE)
        done = 0
        for k, x, n in segs:
            if k == "card":
                for i in range(n):
                    fade = max(0, 1 - i / 6, (i - (n - 7)) / 6)
                    ff.stdin.write(base64.b64decode(pg.evaluate("([c, f]) => card(c, f)", [x, min(1, fade)]).split(",", 1)[1]))
            else:
                png = base64.b64decode(pg.evaluate("s => draw(s)", x).split(",", 1)[1])
                for _ in range(n):
                    ff.stdin.write(png)
            done += n
            if done % 240 < n:
                print(f"{done}/{total} frames", flush=True)
        ff.stdin.close(); ff.wait()
        print(outp, total, "frames", total / FPS, "s")


main()
