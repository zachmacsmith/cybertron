"""The merge gate: the tests a change can break, in minutes rather than the full suite's half hour.

    python scripts/test_fast.py [BASE] [-n N] [--list] [-- extra pytest args]

BASE (default origin/subsistence) is what the change is measured against: the files changed since the merge base with BASE,
committed or not. It runs
  - the gate set, always: goldens, legacy and current prompts, schema, settings, the registry tables (consistency, contract,
    event types, tiers) and every spec loading (test_media2_frozen loads them all);
  - every test file that changed;
  - every test file that imports a changed cybertron module directly (`from cybertron import x`, `cybertron.x`, `from
    cybertron.x import`); dependents through other modules are the full suite's job. Hub modules (kernel, actions, agents, spec... imported by over HUB_SHARE of the test
    files) select nothing by themselves: the gate set's goldens and prompts run the whole engine through them.
The full suite stays the daily check and gates `main`; this gates `subsistence`. Use a unique --basetemp per agent (pytest wipes it).
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PKG, TESTS = ROOT / "cybertron", ROOT / "tests"
GATE = ("test_cybertron_golden.py", "test_cybertron_prompts.py", "test_cybertron_schema.py", "test_settings.py",
        "test_cybertron_consistency.py", "test_cybertron_contract.py", "test_cybertron_eventtypes.py", "test_cybertron_tiers.py",
        "test_media2_frozen.py")
HUB_SHARE = 0.15         # a module more than this share of test files import is a hub: the gate set covers it
IMPORT = re.compile(r"from cybertron import ([\w ,()\n]+)|from cybertron\.([\w.]+) import|import cybertron\.([\w.]+)|cybertron\.(\w+)")


def git(*args) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def changed(base: str) -> list:
    mb = git("merge-base", base, "HEAD").strip()
    names = set(git("diff", "--name-only", mb).split()) | set(git("ls-files", "--others", "--exclude-standard").split())
    return sorted(n for n in names if n.endswith(".py") or n.endswith(".yaml") or n.endswith(".json"))


def module_of(path: str) -> str | None:
    p = Path(path)
    if p.parts[:1] != ("cybertron",) or p.suffix != ".py":
        return None
    parts = list(p.with_suffix("").parts[1:])
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts) or None


def imported(text: str) -> set:
    """Top-level cybertron modules a file names (cybertron.dispatch.changes.legal counts as dispatch and dispatch.changes.legal)."""
    out = set()
    for m in IMPORT.finditer(text):
        if m.group(1):
            out |= {x.split(" as ")[0].strip() for x in m.group(1).replace("(", "").replace(")", "").replace("\n", " ").split(",")}
        for g in m.groups()[1:]:
            if g:
                bits = g.split(".")
                out |= {".".join(bits[:i]) for i in range(1, len(bits) + 1)}
    return {x for x in out if x}


def select(base: str) -> tuple[list, list]:
    files = changed(base)
    tests = {t.name: imported(t.read_text(errors="ignore")) for t in TESTS.glob("test_*.py")}
    hubs = {m for m in set().union(*tests.values()) if sum(m in v for v in tests.values()) > HUB_SHARE * len(tests)}
    mods = {m for m in map(module_of, files) if m}
    spec_changed = any(f.startswith("cybertron/specs/") for f in files)
    reach = mods - hubs                                                # a hub (actions, agents, generator...) selects everything:
    picked = set(GATE)                                                 # the gate's goldens and prompts run the whole engine instead
    for name, uses in tests.items():
        if f"tests/{name}" in files or uses & reach:
            picked.add(name)
    if spec_changed:
        picked |= {t.name for t in TESTS.glob("test_*.py") if any(Path(f).stem in t.read_text(errors="ignore")
                                                                for f in files if f.startswith("cybertron/specs/"))}
    return files, sorted(p for p in picked if (TESTS / p).exists())


def main(argv) -> int:
    extra = argv[argv.index("--") + 1:] if "--" in argv else []
    argv = argv[:argv.index("--")] if "--" in argv else argv
    n = argv[argv.index("-n") + 1] if "-n" in argv else "3"
    rest = [a for i, a in enumerate(argv) if a not in ("-n", "--list") and (i == 0 or argv[i - 1] != "-n")]
    base = rest[0] if rest else "origin/subsistence"
    files, tests = select(base)
    total = len(list(TESTS.glob("test_*.py")))
    print(f"{len(files)} changed files since {base}; {len(tests)} of {total} test files", file=sys.stderr)
    if "--list" in argv:
        print("\n".join(tests))
        return 0
    cmd = [sys.executable, "-m", "pytest", "-q", "-n", n, "-p", "no:cacheprovider", *[f"tests/{t}" for t in tests], *extra]
    return subprocess.call(cmd, cwd=ROOT)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
