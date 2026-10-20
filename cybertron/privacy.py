"""The privacy gate for publishing: scan what is about to leave the machine for private strings, secrets and local paths.

    python -m cybertron publish --audit PATH        # scan a local directory, archive or downloaded dataset snapshot; push nothing

What is looked for, in every file under a directory, every member of every .tar.gz / .tgz / .tar (and .gz members inside them),
and the text of every parquet table (all columns, nested ones as JSON):

- private strings, collected automatically: the email address(es), accountUuid, organizationUuid, machineID and userID of the
  Claude Code account files (~/.claude.json, $CLAUDE_CONFIG_DIR/.claude.json, and any .claude.json inside the runs being
  published or the tree being audited, archives included), $CLAUDE_CODE_USER_EMAIL, and a user denylist: comma-separated
  values in $CYBERTRON_PRIVATE_STRINGS and/or one value per line in the file named by $CYBERTRON_PRIVATE_FILE;
- secrets: Anthropic keys (sk-ant-), Hugging Face tokens, GitHub tokens (ghp_, gho_, github_pat_), Authorization: Bearer
  headers, AWS access key ids;
- claude.ai session URLs, and absolute home or root paths (/root/, /home/<user>/, /Users/<user>/) that _scrub should have removed;
- files that are never published at all (publish.NEVER: checkpoints, pickles, claude_sessions, .claude*, credentials, keys).

A hit is reported as file (and archive member / table column), kind and a short context in which every private value, secret
and home-directory user name is redacted: the values themselves are never printed, logged or put in an exception. Every hit
blocks a push; there is no override (a path hit means the scrubber missed something: fix the scrubber, not the gate).
"""
from __future__ import annotations

import gzip
import io
import json
import os
import re
import tarfile
from dataclasses import dataclass
from pathlib import Path

MIN_PRIVATE = 6                                     # shorter denylist values would match everywhere
CONTEXT = 30                                        # characters of redacted context on each side of a hit
MAX_SCAN = 512 * 1024 * 1024                        # bytes of one file/member read into memory (bigger ones are a hit themselves)

# key in an account file -> kind of the private value it holds
ACCOUNT_KEYS = {"emailaddress": "account email", "email": "account email", "accountuuid": "account uuid",
                "organizationuuid": "organization uuid", "machineid": "machine id", "userid": "user id",
                "accesstoken": "oauth token", "refreshtoken": "oauth token"}

SECRETS = [
    ("anthropic key", re.compile(r"sk-ant-[A-Za-z0-9_\-]{8,}")),
    ("hf token", re.compile(r"(?<![A-Za-z0-9])hf_[A-Za-z0-9]{30,}")),
    ("github token", re.compile(r"(?<![A-Za-z0-9])(?:gh[po]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})")),
    ("bearer authorization", re.compile(r"(?i)authorization[\"']?\s*[:=]\s*[\"']?\s*bearer\s+[A-Za-z0-9._~+/=\-]{8,}")),
    ("aws access key", re.compile(r"(?<![A-Z0-9])AKIA[0-9A-Z]{16}(?![A-Z0-9])")),
    ("claude session url", re.compile(r"claude\.ai/code/session_[A-Za-z0-9_\-]*")),
]
PATHS = [
    ("root path", re.compile(r"(?<![\w.~\-])/root/")),
    ("home path", re.compile(r"(?<![\w.~\-])/(?:home|Users)/[^/\s\"'<>]+/")),
]
SECRET_KINDS = {k for k, _ in SECRETS}
PATH_KINDS = {k for k, _ in PATHS}


@dataclass(frozen=True)
class Hit:
    file: str                                       # path relative to the scanned root
    where: str                                      # archive member / table column, or ""
    kind: str                                       # "account email", "hf token", "home path", "never published", ...
    context: str                                    # redacted

    @property
    def blocking(self) -> bool:
        return True                                 # every kind blocks a push (module docstring)

    def __str__(self) -> str:
        loc = f"{self.file}:{self.where}" if self.where else self.file
        return f"privacy: {self.kind} in {loc}" + (f": ...{self.context}..." if self.context else "")


# ------------------------------------------------------------------ private strings
class Private:
    """The private values to look for, kept out of every repr and message."""

    def __init__(self, values: dict[str, str] | None = None):
        self._v: dict[str, str] = {}                # lower-cased value -> kind
        self._re = None
        for v, k in (values or {}).items():
            self.add(v, k)

    def add(self, value, kind: str) -> None:
        if not isinstance(value, str):
            return
        value = value.strip()
        if len(value) < MIN_PRIVATE or value.lower() in self._v:
            return
        self._v[value.lower()] = kind
        if kind == "account email" or "@" in value:
            self._v.setdefault(value.lower().replace("@", "%40"), kind)     # URL-encoded form
        self._re = None

    def kinds(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for k in self._v.values():
            out[k] = out.get(k, 0) + 1
        return out

    def __len__(self) -> int:
        return len(self._v)

    def __repr__(self) -> str:                      # never the values
        return f"Private({len(self._v)} values: {self.kinds()})"

    def finditer(self, text: str):
        if not self._v:
            return
        if self._re is None:
            alts = sorted(self._v, key=len, reverse=True)
            self._re = re.compile("|".join(re.escape(a) for a in alts), re.I)
        for m in self._re.finditer(text):
            yield self._v[m.group(0).lower()], m

    # -- sources
    def add_account_json(self, data) -> None:
        """Values under the identifying keys of a Claude Code account file (.claude.json, .credentials.json), any depth."""
        if isinstance(data, dict):
            for k, v in data.items():
                kind = ACCOUNT_KEYS.get(str(k).lower())
                if kind and isinstance(v, str):
                    self.add(v, kind)
                else:
                    self.add_account_json(v)
        elif isinstance(data, list):
            for v in data:
                self.add_account_json(v)

    def add_account_text(self, text: str) -> None:
        try:
            self.add_account_json(json.loads(text))
        except ValueError:
            for m in re.finditer(r'"(emailAddress|accountUuid|organizationUuid|machineID|userID)"\s*:\s*"([^"]+)"', text):
                self.add(m.group(2), ACCOUNT_KEYS[m.group(1).lower()])


def account_files() -> list[Path]:
    home = Path.home()
    out = [home / ".claude.json", home / ".claude" / ".claude.json", home / ".claude" / ".credentials.json"]
    cfg = os.environ.get("CLAUDE_CONFIG_DIR")
    if cfg:
        out += [Path(cfg) / ".claude.json", Path(cfg) / ".credentials.json"]
    return out


def collect_private(trees=(), env=None) -> Private:
    """The private values of this machine (account files, env, denylist) plus those in account files found under `trees`
    (run directories, a staged dataset or an audited snapshot; .claude.json members of archives included)."""
    env = os.environ if env is None else env
    priv = Private()
    for f in account_files():
        try:
            priv.add_account_text(f.read_text(errors="replace"))
        except OSError:
            pass
    if env.get("CLAUDE_CODE_USER_EMAIL"):
        priv.add(env["CLAUDE_CODE_USER_EMAIL"], "account email")
    for v in (env.get("CYBERTRON_PRIVATE_STRINGS") or "").split(","):
        priv.add(v, "private string")
    pf = env.get("CYBERTRON_PRIVATE_FILE")
    if pf:
        try:
            lines = Path(pf).expanduser().read_text().splitlines()
        except OSError as e:
            raise SystemExit(f"CYBERTRON_PRIVATE_FILE: cannot read it ({e.strerror})")
        for v in lines:
            if v.strip() and not v.lstrip().startswith("#"):
                priv.add(v, "private string")
    for t in trees:
        for name, text in _account_texts(Path(t)):
            priv.add_account_text(text)
    return priv


_ACCOUNT_NAME = re.compile(r"(^|/)\.(claude|credentials)[^/]*\.json$")


def _account_texts(root: Path):
    files = [root] if root.is_file() else sorted(p for p in root.rglob("*") if p.is_file())
    for p in files:
        if _ACCOUNT_NAME.search(p.as_posix()):
            try:
                yield p.as_posix(), p.read_text(errors="replace")
            except OSError:
                pass
        elif _is_tar(p):
            try:
                with tarfile.open(p) as tf:
                    for m in tf.getmembers():
                        if m.isfile() and _ACCOUNT_NAME.search(m.name) and m.size <= MAX_SCAN:
                            yield f"{p}:{m.name}", tf.extractfile(m).read().decode(errors="replace")
            except (tarfile.TarError, OSError, EOFError):
                pass


# ------------------------------------------------------------------ scanning
def _is_tar(p: Path) -> bool:
    return p.name.endswith((".tar.gz", ".tgz", ".tar"))


def redact(text: str, priv: Private) -> str:
    """text with every private value, secret and home-directory user name replaced by a marker."""
    out = text
    spans = [(m.start(), m.end(), kind) for kind, m in priv.finditer(out)]
    for kind, rx in SECRETS:
        spans += [(m.start(), m.end(), kind) for m in rx.finditer(out)]
    for s, e, kind in sorted(spans, reverse=True):
        out = out[:s] + f"[{kind.upper()}]" + out[e:]
    out = re.sub(r"/(home|Users)/[^/\s\"'<>]+/", r"/\1/<user>/", out)
    return out


def _context(text: str, start: int, end: int, priv: Private) -> str:
    a, b = max(0, start - CONTEXT), min(len(text), end + CONTEXT)
    lo, hi = text[a:start], text[end:b]
    marker = "\x00HIT\x00"
    ctx = redact(lo + marker + hi, priv)
    snippet = text[start:end]
    kind_marker = "[REDACTED]" if not snippet.startswith("/") else redact(snippet, priv)
    return re.sub(r"\s+", " ", ctx.replace(marker, kind_marker))[: 4 * CONTEXT + 40]


def scan_text(text: str, priv: Private, file: str, where: str = "", paths: bool = True) -> list[Hit]:
    hits, seen = [], set()
    found = [(kind, m.start(), m.end()) for kind, m in priv.finditer(text)]
    for kind, rx in SECRETS + (PATHS if paths else []):
        found += [(kind, m.start(), m.end()) for m in rx.finditer(text)]
    for kind, s, e in sorted(found, key=lambda x: x[1]):
        if kind in seen:                            # one hit per kind per file/member/column is enough to report
            continue
        seen.add(kind)
        hits.append(Hit(file, where, kind, _context(text, s, e, priv)))
    return hits


def _scan_bytes(data: bytes, name: str, priv: Private, file: str, where: str) -> list[Hit]:
    if name.endswith(".gz") and not name.endswith((".tar.gz",)):
        try:
            data = gzip.decompress(data)
            name = name[:-3]
        except (OSError, EOFError):
            pass
    if name.endswith(".parquet"):
        return _scan_parquet(io.BytesIO(data), priv, file, where)
    return scan_text(data.decode("utf-8", errors="replace"), priv, file, where)


def _scan_parquet(src, priv: Private, file: str, where: str = "") -> list[Hit]:
    try:
        import pyarrow.parquet as pq
        t = pq.read_table(src)
    except Exception as e:                          # unreadable table: say so, without its content
        return [Hit(file, where, "unreadable parquet", type(e).__name__)]
    hits = []
    for name in t.column_names:
        text = json.dumps(t.column(name).to_pylist(), default=str, ensure_ascii=False)
        hits += scan_text(text, priv, file, f"{where}[{name}]" if where else f"[{name}]")
    md = t.schema.metadata or {}
    if md:
        hits += scan_text(" ".join(v.decode("utf-8", "replace") for v in md.values()), priv, file,
                          f"{where}[schema metadata]" if where else "[schema metadata]")
    return hits


def scan_archive(p: Path, priv: Private, rel: str, never=None) -> list[Hit]:
    hits = []
    try:
        with tarfile.open(p) as tf:
            for m in tf.getmembers():
                if never is not None and never.search(m.name):
                    hits.append(Hit(rel, m.name, "never published", ""))
                hits += scan_text(m.name, priv, rel, m.name, paths=False)
                if not m.isfile():
                    continue
                if m.size > MAX_SCAN:
                    hits.append(Hit(rel, m.name, "too large to scan", f"{m.size} bytes"))
                    continue
                hits += _scan_bytes(tf.extractfile(m).read(), m.name, priv, rel, m.name)
    except (tarfile.TarError, OSError, EOFError) as e:
        hits.append(Hit(rel, "", "unreadable archive", type(e).__name__))
    return hits


def scan_file(p: Path, priv: Private, rel: str, never=None) -> list[Hit]:
    hits = []
    if never is not None and never.search(rel):
        hits.append(Hit(rel, "", "never published", ""))
    hits += scan_text(rel, priv, rel, "(file name)", paths=False)
    if _is_tar(p):
        return hits + scan_archive(p, priv, rel, never)
    if p.suffix == ".parquet":
        return hits + _scan_parquet(p, priv, rel)
    if p.stat().st_size > MAX_SCAN:
        return hits + [Hit(rel, "", "too large to scan", f"{p.stat().st_size} bytes")]
    return hits + _scan_bytes(p.read_bytes(), p.name, priv, rel, "")


def scan_tree(root, priv: Private | None = None, never=None) -> list[Hit]:
    """Every hit in a directory (or one file): files, archive members, parquet text. `never` (publish.NEVER) also flags files
    that should never have been staged. Skips .git."""
    root = Path(root)
    if priv is None:
        priv = collect_private([root])
    if root.is_file():
        return scan_file(root, priv, root.name, never)
    hits = []
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root).as_posix()
        if not p.is_file() or ".git" in Path(rel).parts:
            continue
        hits += scan_file(p, priv, rel, never)
    return hits


def report(hits: list[Hit], log=print) -> None:
    by_kind: dict[str, int] = {}
    for h in hits:
        by_kind[h.kind] = by_kind.get(h.kind, 0) + 1
        log(f"  PROBLEM {h}")
    if hits:
        log("privacy: " + ", ".join(f"{n} {k}" for k, n in sorted(by_kind.items())))


def audit(path, log=print, never=None) -> list[Hit]:
    """`publish --audit PATH`: scan a local directory / archive / dataset snapshot; nothing is uploaded."""
    path = Path(path)
    if not path.exists():
        raise SystemExit(f"--audit: {path} does not exist")
    priv = collect_private([path])
    log(f"audit {path}: looking for {len(priv)} private value(s) {priv.kinds()}, secrets, session URLs and local paths")
    hits = scan_tree(path, priv, never)
    report(hits, log)
    files = {h.file for h in hits}
    log(f"audit: {len(hits)} hit(s) in {len(files)} file(s)" if hits else "audit: clean")
    return hits
