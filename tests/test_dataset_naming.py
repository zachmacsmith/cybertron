"""The Hugging Face dataset id is written once in Python (publish.DATASET) and once in the site (DATASET_REPO in
site/lib/cybertron-data.js); repack_remote_archive rebuilds a published raw archive without NEVER members (no network)."""
from __future__ import annotations

import argparse
import io
import json
import re
import tarfile
from pathlib import Path

import pytest

from cybertron import publish as P

ROOT = Path(__file__).resolve().parents[1]
QUIET = dict(log=lambda *a: None)


def _files(*globs):
    for g in globs:
        yield from (p for p in ROOT.glob(g) if p.is_file() and "out" not in p.relative_to(ROOT).parts)


def test_dataset_id_written_once_in_python_and_once_in_the_site():
    hits = {}
    for p in _files("cybertron/**/*.py", "site/**/*.js", "site/**/*.html", "site/**/*.py", "tests/**/*.py", "scripts/**/*.py"):
        n = p.read_text(errors="ignore").count(P.DATASET)
        if n:
            hits[p.relative_to(ROOT).as_posix()] = n
    assert hits == {"cybertron/publish.py": 1, "site/lib/cybertron-data.js": 1}


def test_site_constant_matches_python():
    js = (ROOT / "site/lib/cybertron-data.js").read_text()
    m = re.search(r'export const DATASET_REPO = "([^"]+)"', js)
    assert m and m.group(1) == P.DATASET
    site = (ROOT / "site/assets/site.js").read_text()
    assert "DATASET_REPO" in site and 'DATASET_REPO = "' not in site       # re-exported, not redefined


def test_env_overrides_default_and_flag_overrides_env(monkeypatch):
    monkeypatch.delenv("CYBERTRON_DATASET", raising=False)
    assert P.default_repo() == P.DATASET
    monkeypatch.setenv("CYBERTRON_DATASET", "someone/other-runs")
    assert P.default_repo() == "someone/other-runs"
    parser = argparse.ArgumentParser()
    P.add_command(parser.add_subparsers())
    assert parser.parse_args(["publish"]).repo == "someone/other-runs"
    assert parser.parse_args(["publish", "--repo", "a/b"]).repo == "a/b"


def test_publish_without_repo_uses_the_env(monkeypatch, tmp_path):
    seen = []
    monkeypatch.setenv("CYBERTRON_DATASET", "someone/other-runs")
    monkeypatch.setattr(P, "remote_catalog", lambda repo, revision=None: seen.append(repo) or [])
    with pytest.raises(SystemExit, match="no runs"):
        P.publish([], staging=tmp_path / "st", **QUIET)
    assert seen == ["someone/other-runs"]


def test_card_is_cybertron_and_names_the_repo():
    card = P.dataset_card("me/data", ["events"], [], "")
    assert "pretty_name: Cybertron runs" in card and "https://github.com/zachmacsmith/cybertron" in card
    assert "hf://datasets/me/data/" in card and "charter" not in card.lower()
    assert "charter" not in P.CHANGELOG_HEAD.lower()


# ------------------------------------------------------------------ repack
KEEP = ["E0/r1/events.jsonl", "E0/r1/run.json", "E0/r1/sub/turns.jsonl"]
DROP = ["E0/r1/checkpoints/r3.pkl", "E0/r1/claude_sessions/a/session.jsonl", "E0/r1/state.pickle", "E0/r1/abandoned_calls.jsonl"]


def _fake_archive(path: Path, names) -> Path:
    with tarfile.open(path, "w:gz") as tf:
        d = tarfile.TarInfo("E0/r1")
        d.type = tarfile.DIRTYPE
        tf.addfile(d)
        for n in names:
            data = f"content of {n}\n".encode()
            info = tarfile.TarInfo(n)
            info.size, info.mtime, info.mode = len(data), 1700000000, 0o644
            tf.addfile(info, io.BytesIO(data))
    return path


class FakeApi:
    def __init__(self):
        self.calls = []

    def upload_folder(self, folder_path, repo_id, repo_type, delete_patterns, commit_message):
        files = sorted(p.relative_to(folder_path).as_posix() for p in Path(folder_path).rglob("*") if p.is_file())
        self.calls.append({"repo": repo_id, "files": files, "deletes": delete_patterns, "msg": commit_message})
        return type("C", (), {"oid": "abc123", "commit_url": ""})()


def _rows():
    return [{"run_id": "r1", "spec": "E0", "path": "runs/E0/r1", "raw": "raw/E0/r1.tar.gz", "bytes_archive": 1, "raw_sha256": "x"},
            {"run_id": "r2", "spec": "E0", "path": "runs/E0/r2", "raw": "raw/E0/r2.tar.gz", "bytes_archive": 7}]


def test_repack_archive_drops_never_members(tmp_path):
    src = _fake_archive(tmp_path / "in.tar.gz", KEEP + DROP)
    res = P.repack_archive(src, tmp_path / "out" / "r1.tar.gz")
    assert sorted(res["dropped"]) == sorted(DROP) and res["files"] == len(KEEP)
    with tarfile.open(tmp_path / "out" / "r1.tar.gz") as tf:
        names = tf.getnames()
        assert sorted(n for n in names if n != "E0/r1") == sorted(KEEP)
        assert tf.extractfile("E0/r1/run.json").read() == b"content of E0/r1/run.json\n"
        assert tf.getmember("E0/r1/run.json").mtime == 1700000000


def test_repack_remote_dry_run_uploads_nothing(tmp_path):
    src = _fake_archive(tmp_path / "in.tar.gz", KEEP + DROP)
    api = FakeApi()
    s = P.repack_remote_archive("me/data", "raw/E0/r1.tar.gz", workdir=tmp_path / "w", download=lambda r, p: src,
                                catalog=lambda r: _rows(), api=api, **QUIET)
    assert not s["pushed"] and api.calls == [] and len(s["dropped"]) == len(DROP)
    assert (tmp_path / "w" / "raw/E0/r1.tar.gz").exists()


def test_repack_remote_push_uploads_archive_and_updated_catalog(tmp_path):
    src = _fake_archive(tmp_path / "in.tar.gz", KEEP + DROP)
    api = FakeApi()
    s = P.repack_remote_archive("me/data", "raw/E0/r1.tar.gz", dry_run=False, workdir=tmp_path / "w",
                                download=lambda r, p: src, catalog=lambda r: _rows(), api=api, **QUIET)
    assert s["pushed"] and s["commit"] == "abc123"
    [call] = api.calls
    assert call["repo"] == "me/data" and call["deletes"] == []
    assert call["files"] == ["catalog.json", "catalog.parquet", "raw/E0/r1.tar.gz"]
    assert sorted(s["catalog_updated"]) == ["r1.bytes_archive", "r1.raw_sha256"]
    rows = {r["run_id"]: r for r in json.loads((tmp_path / "w" / "catalog.json").read_text())["runs"]}
    assert rows["r1"]["bytes_archive"] == s["after"]["bytes_archive"] == (tmp_path / "w/raw/E0/r1.tar.gz").stat().st_size
    assert rows["r1"]["raw_sha256"] == s["after"]["sha256"] and rows["r2"]["bytes_archive"] == 7


def test_repack_remote_catalog_without_archive_fields_uploads_only_the_archive(tmp_path):
    src = _fake_archive(tmp_path / "in.tar.gz", KEEP + DROP)
    api = FakeApi()
    rows = [{"run_id": "r1", "spec": "E0", "raw": "raw/E0/r1.tar.gz"}]                  # today's catalog: no archive facts
    s = P.repack_remote_archive("me/data", "raw/E0/r1.tar.gz", dry_run=False, workdir=tmp_path / "w",
                                download=lambda r, p: src, catalog=lambda r: rows, api=api, **QUIET)
    assert s["catalog_updated"] == [] and api.calls[0]["files"] == ["raw/E0/r1.tar.gz"]


def test_repack_remote_clean_archive_is_not_uploaded(tmp_path):
    src = _fake_archive(tmp_path / "in.tar.gz", KEEP)
    api = FakeApi()
    s = P.repack_remote_archive("me/data", "raw/E0/r1.tar.gz", dry_run=False, workdir=tmp_path / "w",
                                download=lambda r, p: src, catalog=lambda r: _rows(), api=api, **QUIET)
    assert s["dropped"] == [] and not s["pushed"] and api.calls == []


@pytest.mark.parametrize("path", ["catalog.json", "raw/E0/r1.tar", "raw/../x.tar.gz", "/raw/E0/r1.tar.gz"])
def test_repack_remote_refuses_other_paths(tmp_path, path):
    with pytest.raises(SystemExit, match="not a raw archive path"):
        P.repack_remote_archive("me/data", path, workdir=tmp_path / "w", download=lambda r, p: pytest.fail("downloaded"),
                                catalog=lambda r: [], **QUIET)
