"""Publish cybertron2 runs to the Hugging Face dataset, in their own folder, marked experimental.

    python -m cybertron2.publish_hf RUN_DIR [RUN_DIR...] [--repo OWNER/NAME] [--staging DIR] [--push]

Layout on the Hub (nothing else in the dataset is touched: no catalog row, no table, no card change, so the site and the main
dataset's viewer are unaffected):

    experimental/cybertron2/README.md                 what this is, and that it is not comparable with the main runs
    experimental/cybertron2/<run>/run.json            the spec, each agent's model and system prompt
    experimental/cybertron2/<run>/turns.jsonl         one line per agent-round: the prompt, the reply (with `why`), the results
    experimental/cybertron2/<run>/rounds.jsonl        one line per round: the end-of-round record
    experimental/cybertron2/<run>/state.json          the final state, with every agent's knowledge store
    experimental/cybertron2/<run>/report.md           the generated summary (cybertron2.report)

Privacy, as the main publisher does (cybertron/specs/bench36/publish.sh, cybertron/privacy.py): this machine's Claude Code session,
container, account and organisation ids and the account email are replaced with "<redacted>" in every staged file, then the
privacy gate scans the staging and refuses to upload on any hit. Without --push nothing leaves the machine. --push needs
huggingface_hub and a token with write access to the dataset in HF_TOKEN.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import time
from pathlib import Path

FOLDER = "experimental/cybertron2"
FILES = ("run.json", "turns.jsonl", "rounds.jsonl", "days.jsonl", "perception.jsonl", "memory.jsonl", "state.json")   # those a run has
ID_VARS = ("CLAUDE_CODE_SESSION_ID", "CLAUDE_CODE_REMOTE_SESSION_ID", "CLAUDE_CODE_CONTAINER_ID", "CLAUDE_CODE_ACCOUNT_UUID",
           "CLAUDE_CODE_ORGANIZATION_UUID", "CLAUDE_CODE_USER_EMAIL")

CARD = """# Experimental: cybertron2, the engine on a graph of places

**These runs come from a new, experimental engine and are not comparable with the rest of this dataset.** cybertron2 is a rewrite
in progress: the world is a graph of places, agents act only where they are, and they see only their own place (everything else
is a dated belief). Its physics, prompts and output format differ from the main engine's, it has no institutions or laws yet, and
nothing here is in `catalog.parquet` or the site. Treat each run as a probe of the mechanics, not a measurement.

Code and write-ups: the `wp/cybertron2` branch of the cybertron repository, `cybertron2/` and `docs/review/38_space_engine/`.

## Runs

| Run | World | Agents | Rounds | Cost | In one line |
|---|---|---|---|---|---|
{rows}

## Files in each run folder

- `run.json`: the spec, each agent's model and its system prompt.
- `turns.jsonl`: one line per agent and round: the turn prompt it saw, its reply (`why`: a few sentences on why it chose its actions;
  `actions`, `say`, `tell`, `note`), what each action did, usage.
- `rounds.jsonl` (older runs) or `days.jsonl`: one line per round or day: meals, shelter, deaths, the cold, fires, births.
- `perception.jsonl` and `memory.jsonl` (newer runs): what each agent noticed each day, and the memories each wrote itself.
- `state.json`: the final state, with every agent's knowledge store (what it saw where, and when).
- `report.md`: the generated summary.

Models were called through Claude Code (`claude -p`). The 5.5 models return no thinking text there, so `why` is the only view of
their intentions.
"""

SUMMARIES = {                                                         # one line per known run (the write-ups: review 38.01, 38.03)
    "forest_households_seed1": "two households in a forest: they stocked up for winter; one starved on a risky hunt",
    "hills_and_forest_seed2": "two forest households and a hill household that cannot gather food: the raiders never raided; "
                              "they traded blades in good faith, and two starved",
}


def stage(runs, staging: Path) -> Path:
    from cybertron2 import report
    root = staging / FOLDER
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    rows = []
    for r in runs:
        r = Path(r)
        dst = root / r.name
        dst.mkdir()
        for f in FILES:
            if (r / f).exists():
                shutil.copy2(r / f, dst / f)
        try:
            (dst / "report.md").write_text(report.summary(r))
        except Exception:                                                   # the newer runs' layout (days.jsonl): no summary yet
            pass
        run = json.loads((r / "run.json").read_text())
        rf = r / "rounds.jsonl" if (r / "rounds.jsonl").exists() else r / "days.jsonl"
        rounds = [json.loads(x) for x in rf.read_text().splitlines() if x.strip()]
        cost = rounds[-1].get("cost_usd", 0.0) if rounds else 0.0
        rows.append(f"| {r.name} | `{run['spec'].get('name')}` | {len(run['spec']['agents'])} | {len(rounds)} | ${cost:.2f} | "
                    f"{SUMMARIES.get(r.name, '')} |")
    (root / "README.md").write_text(CARD.format(rows="\n".join(rows)))
    ids = [os.environ.get(v, "") for v in ID_VARS]
    for p in root.rglob("*"):
        if p.is_file():
            text = p.read_text()
            new = text
            for v in ids:
                if len(v) >= 6:
                    new = new.replace(v, "<redacted>")
            if new != text:
                p.write_text(new)
    return root


def main(argv=None):
    from cybertron import privacy as PV, publish as P
    ap = argparse.ArgumentParser(prog="python -m cybertron2.publish_hf")
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--repo", default=None)
    ap.add_argument("--staging", default=None)
    ap.add_argument("--push", action="store_true")
    a = ap.parse_args(argv)
    repo = a.repo or P.default_repo()
    staging = Path(a.staging or f"cybertron/out/_publish/cybertron2_{time.strftime('%Y%m%dT%H%M%S', time.gmtime())}")
    os.environ["CYBERTRON_PRIVATE_STRINGS"] = ",".join(v for v in (os.environ.get(x, "") for x in ID_VARS) if len(v) >= 6)
    root = stage(a.runs, staging)
    if PV.audit(str(staging), never=P.NEVER):
        raise SystemExit(f"privacy audit found hits in {staging}: nothing uploaded")
    files = sorted(str(p.relative_to(staging)) for p in root.rglob("*") if p.is_file())
    print(f"staged {len(files)} files in {staging} (audit clean):")
    for f in files:
        print("  " + f)
    if not a.push:
        print(f"dry run: nothing uploaded (add --push to upload to {repo})")
        return
    if not os.environ.get("HF_TOKEN"):
        raise SystemExit("HF_TOKEN is not set: a token with write access to the dataset is needed to upload")
    from huggingface_hub import HfApi
    HfApi().upload_folder(repo_id=repo, repo_type="dataset", folder_path=str(staging), allow_patterns=[f"{FOLDER}/**"],
                          commit_message=f"experimental: cybertron2 runs ({', '.join(Path(r).name for r in a.runs)})")
    print(f"uploaded to {repo}/{FOLDER}")


if __name__ == "__main__":
    main()
