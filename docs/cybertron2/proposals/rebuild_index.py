"""Rebuild proposals/README.md's table from the files (status and owner as each file states them; a row's summary kept if it has one,
file's title), and add log rows for files the log lacks."""
import os, re, subprocess, sys
d = sys.argv[1]
path = f"{d}/README.md"
lines = open(path).read().split("\n")
i0 = next(i for i, l in enumerate(lines) if l.startswith("## Proposals"))
i1 = next(i for i, l in enumerate(lines) if l.startswith("## Log"))
old = {}
for l in lines[i0:i1]:
    m = re.match(r"\| \[([^\]]+\.md)\]\([^)]+\) \| (.*?) \| (.*?) \| (.*?) \|$", l)
    if m:
        old[m.group(1)] = (m.group(2), m.group(3))
def field(txt, name):
    """A field's text to the next field, heading or blank line, its wrapped lines joined."""
    m = re.search(r"\*\*" + name + r":?\*\*:?\s*((?:.|\n(?!\n|#|\*\*[A-Z]))*)", txt) or \
        re.search(r"^" + name + r":\s*((?:.|\n(?!\n|#))*)", txt, re.M)
    v = (m.group(1) if m else "").strip()
    v = re.split(r"\s\*\*(?:Owner|Affects|Model)", v)[0]
    return " ".join(v.split())
def short_status(s):
    s = re.sub(r"\*\*", "", s).strip()
    s = re.split(r"\. Owner|; Owner|\. \*\*Owner", s)[0]
    if len(s) <= 140:
        return s
    cut = s[:140]
    for stop in (". ", "; "):                                          # end at a sentence or clause if one ends late enough
        k = cut.rfind(stop)
        if k > 60:
            return cut[:k + 1].rstrip(";") + " ..."
    return cut[:cut.rfind(" ")] + " ..."
def title(txt):
    m = re.search(r"^# (?:Proposal: )?(.*)", txt, re.M)
    return m.group(1).strip() if m else ""
files = sorted(f for f in os.listdir(d) if f.endswith(".md") and f != "README.md")
order = [f for f in old] + [f for f in files if f not in old]
rows = ["## Proposals", "", "Rebuilt from the files on 5 Nov (status and owner as each file states them; 37.2's sweep).", "",
        "| File | Summary | Owner | Status |", "|---|---|---|---|"]
for f in order:
    if f not in files:
        continue
    txt = open(f"{d}/{f}").read()
    summ, own = old.get(f, (None, None))
    summ = summ or title(txt)
    own_f = field(txt, "Owner")
    m = re.search(r"37\.\d", own_f)
    own = own or (m.group(0) if m else own_f[:20])
    st = short_status(field(txt, "Status"))
    rows.append(f"| [{f}]({f}) | {summ} | {own or '?'} | {st} |")
rows.append("")
# log rows for files the log lacks
log = "\n".join(lines[i1:])
add = []
for f in files:
    if f"({f})" in log:
        continue
    txt = open(f"{d}/{f}").read()
    date = subprocess.run(["git", "log", "--diff-filter=A", "--format=%ad", "--date=format:%-d %b", "--", f"{d}/{f}"],
                          capture_output=True, text=True).stdout.strip().split("\n")[-1] or "?"
    add.append(f"| {date} | {title(txt)} | {short_status(field(txt, 'Status'))} | [{f}]({f}) |")
new = lines[:i0] + rows + lines[i1:]
text = "\n".join(new).rstrip("\n") + "\n" + ("\n".join(add) + "\n" if add else "")
open(path, "w").write(text)
print(len(order), "rows;", len(add), "log rows added")
