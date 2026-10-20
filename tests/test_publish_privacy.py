"""The publish privacy gate (cybertron/privacy.py): account files and secrets never leave the machine, and the gate never prints
the values it finds. All values here are fake; the machine's own account files are hidden by pointing HOME at a temp dir."""
from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

pytest.importorskip("pyarrow")

from cybertron import agents as AG, generator, privacy as PV, publish as P, runner  # noqa: E402
from cybertron import spec as S  # noqa: E402

QUIET = dict(log=lambda *a: None)
FAKE_EMAIL = "jane.fakeperson@example.invalid"
FAKE_UUID = "0f0f0f0f-1111-4222-8333-944444444444"
FAKE_ORG = "0e0e0e0e-5555-4666-8777-988888888888"
FAKE_MACHINE = "fa" * 32
# token-shaped fakes, built so this file holds no literal that looks like a real secret
FAKE_TOKENS = {
    "anthropic key": "sk-" + "ant-api03-" + "Q" * 40,
    "hf token": "hf" + "_" + "Zx9" * 12,
    "github token": "gh" + "p_" + "A1b2" * 9,
    "aws access key": "AK" + "IA" + "Z" * 16,
    "bearer authorization": "Authorization: " + "Bearer " + "t0k3n" * 6,
    "claude session url": "https://claude.ai/code/" + "session_" + "0FakeSession",
}
REPO = Path(__file__).resolve().parents[1]


def account_json(email=FAKE_EMAIL) -> str:
    return json.dumps({"oauthAccount": {"emailAddress": email, "accountUuid": FAKE_UUID, "organizationUuid": FAKE_ORG},
                       "machineID": FAKE_MACHINE, "userID": "ab" * 32, "numStartups": 3})


@pytest.fixture(autouse=True)
def private_env(tmp_path_factory, monkeypatch):
    """No real account file or denylist is read: HOME is an empty temp dir and the env vars are cleared."""
    home = tmp_path_factory.mktemp("home")
    monkeypatch.setenv("HOME", str(home))
    for k in ("CLAUDE_CONFIG_DIR", "CLAUDE_CODE_USER_EMAIL", "CYBERTRON_PRIVATE_STRINGS", "CYBERTRON_PRIVATE_FILE"):
        monkeypatch.delenv(k, raising=False)
    return home


@pytest.fixture(scope="module")
def base_run(tmp_path_factory):
    d = tmp_path_factory.mktemp("out") / "E0" / "priv1"
    inst = generator.generate(S.apply_overrides(S.load("E0"), ["rounds=1", "shared_archive.enabled=false"]), 1)
    inst["run_id"] = "priv1"
    runner.run(inst, AG.ScriptedPolicy(1), d, **QUIET)
    return d


@pytest.fixture()
def run(base_run, tmp_path):
    d = tmp_path / "out" / "E0" / "priv1"
    shutil.copytree(base_run, d)
    return d


@pytest.fixture()
def hub(monkeypatch):
    calls = []
    api = NS(upload_folder=lambda **kw: calls.append(kw) or NS(oid="abc", commit_url=""))
    monkeypatch.setattr(P, "_api", lambda: api)
    monkeypatch.setattr(P, "remote_catalog", lambda repo, revision=None: [])
    monkeypatch.setattr(P, "remote_changelog", lambda repo: "")
    return calls


def _no_value_in(text: str, *values):
    for i, v in enumerate(values):
        if v.lower() in text.lower():
            pytest.fail(f"private value #{i} was printed")                    # not the value itself, nor the text


# ------------------------------------------------------------------ exclusion
def test_account_files_and_secrets_are_never_archived(run, tmp_path):
    (run / "claude_sessions").mkdir()
    (run / "claude_sessions" / ".claude.json").write_text(account_json())
    (run / "claude_sessions" / "t.jsonl").write_text("{}\n")
    for rel in (".claude/settings.json", ".claude-2/x.json", ".claude.json", ".credentials.json", "sub/.credentials.v2.json",
                ".env", ".env.local", "id_rsa", "id_rsa.pub", "keys/server.pem"):
        (run / rel).parent.mkdir(parents=True, exist_ok=True)
        (run / rel).write_text("secret")
    out = tmp_path / "raw.tar.gz"
    P.raw_archive(run, out, "E0")
    with tarfile.open(out) as tf:
        names = [m.name.split("priv1/", 1)[1] for m in tf.getmembers()]
    assert "events.jsonl" in names
    bad = [n for n in names if "claude" in n or "credentials" in n or ".env" in n or "id_rsa" in n or n.endswith(".pem")]
    assert bad == []
    for ok in ("env.json", "environment.md", "my.claudette.txt", "credentials_note.md", "pemmican.txt"):
        assert not P.NEVER.search(f"E0/r/{ok}"), ok


# ------------------------------------------------------------------ the gate in publish
def test_planted_email_refuses_push_without_printing_it(run, tmp_path, hub):
    (run / "claude_sessions").mkdir()
    (run / "claude_sessions" / ".claude.json").write_text(account_json())        # the only source of the email
    with (run / "calls.jsonl").open("a") as f:
        f.write(json.dumps({"round": 1, "note": f"contact {FAKE_EMAIL} org {FAKE_ORG}"}) + "\n")
    lines = []
    with pytest.raises(SystemExit) as e:
        P.publish([run], repo="me/data", staging=tmp_path / "st", push=True, log=lines.append)
    assert hub == [], "nothing may be uploaded"
    text = "\n".join(map(str, lines)) + "\n" + str(e.value)
    _no_value_in(text, FAKE_EMAIL, FAKE_ORG, FAKE_UUID, FAKE_MACHINE)
    assert "account email in raw/E0/priv1.tar.gz:E0/priv1/calls.jsonl" in text
    assert "organization uuid" in text and "[REDACTED]" in text


def test_dry_run_reports_hits_in_summary(run, tmp_path, hub, private_env, monkeypatch):
    (private_env / ".claude.json").write_text(account_json("other.fake@example.invalid"))
    monkeypatch.setenv("CYBERTRON_PRIVATE_STRINGS", "Zanzibar-Codeword, x")              # "x" is too short to be used
    with (run / "turns.jsonl").open("a") as f:
        f.write(json.dumps({"t": "mail other.fake@example.invalid re zanzibar-codeword"}) + "\n")
    s = P.publish([run], repo="me/data", staging=tmp_path / "st", **QUIET)
    joined = "\n".join(s["problems"])
    assert s["privacy_hits"] >= 2 and "account email" in joined and "private string" in joined
    _no_value_in(joined, "other.fake@example.invalid", "zanzibar-codeword")


def test_clean_run_passes_and_pushes(run, tmp_path, hub, private_env):
    (private_env / ".claude.json").write_text(account_json())                           # present, but nowhere in the run
    s = P.publish([run], repo="me/data", staging=tmp_path / "st", push=True, **QUIET)
    assert s["problems"] == [] and s["privacy_hits"] == 0 and s["pushed"] and len(hub) == 1


# ------------------------------------------------------------------ the scanner
@pytest.mark.parametrize("kind", sorted(FAKE_TOKENS))
def test_token_patterns_detected_and_redacted(kind):
    tok = FAKE_TOKENS[kind]
    hits = PV.scan_text(f'{{"x": "before {tok} after"}}', PV.Private(), "f.json")
    assert [h.kind for h in hits] == [kind]
    secret = tok.split()[-1] if kind == "bearer authorization" else tok.split("session_")[-1]
    _no_value_in(str(hits[0]), secret)


def test_not_tokens():
    text = "hf_short sk-ant ghp_x AKIA123 /homework/a /x/root/y ~/home/a/ run/home/u/ the bearer of news"
    assert PV.scan_text(text, PV.Private(), "f") == []


def test_paths_detected_with_user_redacted():
    hits = PV.scan_text('{"cwd": "/home/somebody/project/x", "p": "file:///root/a"}', PV.Private(), "f")
    assert {h.kind for h in hits} == {"home path", "root path"}
    assert all("somebody" not in str(h) for h in hits) and any("/home/<user>/" in str(h) for h in hits)


def test_private_sources(private_env, tmp_path, monkeypatch):
    cfg = tmp_path / "cfg"
    cfg.mkdir()
    (cfg / ".claude.json").write_text(account_json("cfg.fake@example.invalid"))
    (tmp_path / "deny.txt").write_text("# comment\nLongCodename42\n")
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(cfg))
    monkeypatch.setenv("CLAUDE_CODE_USER_EMAIL", "env.fake@example.invalid")
    monkeypatch.setenv("CYBERTRON_PRIVATE_FILE", str(tmp_path / "deny.txt"))
    priv = PV.collect_private()
    kinds = {k for k, _ in priv.finditer("cfg.fake@example.invalid ENV.FAKE%40example.invalid longcodename42 " + FAKE_MACHINE)}
    assert kinds == {"account email", "private string", "machine id"}
    _no_value_in(repr(priv), "cfg.fake", "env.fake", "longcodename42", FAKE_MACHINE)


def test_parquet_columns_scanned(tmp_path):
    import pyarrow as pa
    import pyarrow.parquet as pq
    pq.write_table(pa.table({"n": [1], "msgs": [[{"text": "hi " + FAKE_EMAIL}]]}), tmp_path / "t.parquet")
    hits = PV.scan_tree(tmp_path, PV.Private({FAKE_EMAIL: "account email"}))
    assert [(h.file, h.where, h.kind) for h in hits] == [("t.parquet", "[msgs]", "account email")]


# ------------------------------------------------------------------ --audit
def _leaky_snapshot(root: Path) -> None:
    """A dataset snapshot shaped like the leaked one: an archive with claude_sessions/.claude.json and a transcript."""
    raw = root / "raw" / "E0"
    raw.mkdir(parents=True)
    with tarfile.open(raw / "r1.tar.gz", "w:gz") as tf:
        for name, text in (("E0/r1/claude_sessions/.claude.json", account_json()),
                           ("E0/r1/claude_sessions/s.jsonl", f'{{"ctx": "user {FAKE_EMAIL}"}}\n'),
                           ("E0/r1/events.jsonl", '{"round": 1}\n')):
            data = text.encode()
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
    (root / "catalog.json").write_text('{"runs": []}')


def test_audit_cli_flags_leaked_snapshot_without_printing_values(tmp_path, private_env):
    snap = tmp_path / "snap"
    _leaky_snapshot(snap)
    env = {**os.environ, "HOME": str(private_env), "PYTHONPATH": str(REPO)}
    r = subprocess.run([sys.executable, "-m", "cybertron", "publish", "--audit", str(snap)], cwd=REPO, env=env,
                       capture_output=True, text=True, timeout=120)
    out = r.stdout + r.stderr
    assert r.returncode == 1, out[-2000:]
    assert "never published in raw/E0/r1.tar.gz:E0/r1/claude_sessions/.claude.json" in out
    assert "account email in raw/E0/r1.tar.gz:E0/r1/claude_sessions/s.jsonl" in out
    _no_value_in(out, FAKE_EMAIL, FAKE_UUID, FAKE_ORG, FAKE_MACHINE)


def test_audit_clean_dir(tmp_path):
    (tmp_path / "a.json").write_text('{"ok": "relative/path.txt"}')
    assert PV.audit(tmp_path, never=P.NEVER, **QUIET) == []
