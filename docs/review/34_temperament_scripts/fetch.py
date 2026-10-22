"""Download the tables the temperament scripts read (agents, messages, turns, attacks, events) for every published run into
./runs/<spec>/<run_id>/. Run from an empty directory; then run the other scripts from the same directory (python -I <script>)."""
from huggingface_hub import hf_hub_download, list_repo_files

REPO = "zachmacsmith/charter-runs"
WANT = ("agents.parquet", "messages.parquet", "turns.parquet", "attacks.parquet", "events.parquet")
for f in list_repo_files(REPO, repo_type="dataset"):
    if f.startswith("runs/") and f.split("/")[-1] in WANT:
        hf_hub_download(REPO, f, repo_type="dataset", local_dir=".")
