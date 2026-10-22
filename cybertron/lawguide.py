"""Legal experts: the lawyer's legal archive and drafting tool (docs/review/31_institutions/14_legal_experts.md).

Live runs used laws, contracts and courts badly or not at all (no case was ever filed; laws were proposed without a title, as prose,
or with a class where a rank belongs; amendments silently did nothing; no standing contract was ever founded in play, because a
preset's code is ~8,000 tokens). An expert lawyer holds an archive of documents explaining how this legal system works, drafts
laws and contracts for clients, and shares them.

  Archive    a run-scoped directory (cybertron/directories.py) whose files are generated at install from the engine itself (the
             `seed` of a store: directories.SEEDS["legal_archive"] -> archive_files): guide/ (how the system works, drafting,
             pitfalls, the service, with worked examples that tests enact), guide/presets/ (one file per standing-contract preset,
             from standing.PRESETS and standing.BASE), guide/templates* (the established templates, from library.ESTABLISHED) and
             ref/ (the law functions by topic, from lawdocs.ENTRIES, only those this world has). public/ is the short guide every
             agent may read when the store grants `all` read on it. The lawyer reads with the directory look-ups (dir_list,
             dir_read, dir_search: in a turn as actions, in the lookup phase, or in the DM step); the store's owner is the expert.
             guide/, ref/ and public/ are read-only (spec `readonly`); the rest (drafts/, memos/) is the lawyer's workspace,
             shared with a client by dir_grant.
  draft      the expert's action: draft {"template": "Retainer", "parties": {...}, "terms": {...}, "for": "Client"} instantiates a
             standing-contract preset or any established or toolkit template (exactly as a spec's start block does) into
             drafts/<name>.py in the archive, grants the client read access to it, and answers with a summary (never the code).
  by file    propose, amend, create_contract, propose_contract_change and preview_law accept {"draft": "<dir>/<path>"} in place of
             "code" (where an archive exists): the code is read from a directory file the agent may read (actions._act and
             context.lookup call with_draft). A client files a preset contract without pasting 8,000 tokens.

Opt-in by spec only: a directories store with `seed: legal_archive` (cybertron/specs/regimes/private_counsel.yaml). Without one,
`draft` is unknown, no `draft` argument is read and nothing here runs, so no existing world changes.
"""
from __future__ import annotations

import json
import re

SEED = "legal_archive"
GUIDE, REF, PUBLIC, DRAFTS, LIB = "guide/", "ref/", "public/", "drafts/", "lib/"
DOC_BUDGET = 950                    # tokens (len // 4) of one document as dir_read shows it: under the lookup budget (1,000)
FILE_ACTIONS = ("propose", "amend", "create_contract", "propose_contract_change", "preview_law")
REF_TITLES = {"linker": ("Imports and exports (law.v2)", "Laws build on laws: exports offer names, use() links them.")}
REF_TOPICS = ("linker", "governance", "ballots", "ranks", "chains", "rights", "sanctions", "meta", "courts", "court-rules", "output", "contracts")


def _err(msg):
    from cybertron.actions import ActionError
    return ActionError(msg)


def tokens(text: str) -> int:
    return len(text) // 4


# ====================================================================== who is an expert
def _stores(k) -> dict:
    return {n: d for n, d in (k.w.get("dirs") or {}).items() if (d.get("seed") or {}).get("name") == SEED}


def on(k) -> bool:
    """A legal archive exists in this world (the only switch: everything here is off without one)."""
    return bool(_stores(k))


def archives_of(k, aid) -> list:
    """The archives the agent owns (it is their expert), in name order."""
    from cybertron import directories as DR
    return [n for n, d in sorted(_stores(k).items()) if DR.is_owner(k, aid, d)]


def is_expert(k, aid) -> bool:
    return bool(archives_of(k, aid))


def static_expert(inst, a) -> bool:
    """action_registry "lawyer:expert" (no kernel needed): the agent owns a store seeded with the legal archive (owner agent:<id>,
    class:<cls> or right:<r>; a role owner is decided live by `when`)."""
    from cybertron import directories as DR
    try:
        st = DR.stores(inst)
    except ValueError:
        return False
    for d in st.values():
        if (d.get("seed") or {}).get("name") != SEED:
            continue
        kind, _, v = d["owner"].partition(":")
        if (kind == "agent" and v == a["id"] or kind == "class" and (a.get("cls") == v or v in (a.get("also") or ()))
                or kind == "right" and v in (a.get("rights") or ()) or kind == "role"):
            return True
    return False


def when_expert(inst, k, a, rights) -> bool:
    return is_expert(k, a["id"])


# ====================================================================== the world the archive describes
class Ctx:
    """What the generated documents name: the expert, the world's offices and agents (from the spec: the archive is written at
    install, before the start block runs), and the spec switches that change what is true."""

    def __init__(self, k, store, seed):
        sp = k.spec
        d = k.w["dirs"][store]
        self.store, self.seed, self.spec = store, dict(seed or {}), sp
        kind, _, v = d["owner"].partition(":")
        self.expert = v if kind == "agent" else f"the holders of {d['owner']}"
        self.agents = sorted(a for a, r in k.w["agents"].items() if r.get("cls") != "observer")
        j0 = next((e for e in ((sp.get("start") or {}).get("institutions") or ()) if e.get("id") == "J0"), {}) or {}
        self.j0_offices = sorted((j0.get("offices") or {}).keys())
        self.council = next((o for o in ("council", "assembly", "board") if o in self.j0_offices), None)
        others = [a for a in self.agents if a != self.expert]
        retained = [a for e in ((sp.get("start") or {}).get("contracts") or ()) if e.get("template") == "Retainer"
                    for a, r in (e.get("parties") or {}).items() if r == "client" and (e.get("parties") or {}).get(self.expert) == "counsel"]
        self.client = retained[0] if retained else (others[0] if others else self.expert)
        self.other = others[1] if len(others) > 1 else self.client
        reseatable = [o for o in self.j0_offices if o != self.council]
        self.office = reseatable[-1] if reseatable else (self.j0_offices[0] if self.j0_offices else "keeper")
        holders = ((j0.get("offices") or {}).get(self.office) or {}).get("holders") or []
        self.appointee = next((a for a in self.agents if a not in holders and a != self.expert), self.client)
        c = sp.get("contracts") or {}
        self.contracts = bool(c.get("enabled"))
        self.manual_legs = str(c.get("legs_default") or "auto") == "manual"
        self.enforcement = str(c.get("enforcement") or "escrow")
        self.v2 = bool((sp.get("law") or {}).get("v2"))
        self.office_control = bool((sp.get("institutions") or {}).get("office_control"))
        self.store_id = "S1"


# ====================================================================== worked examples (every one is enacted by the tests)
def examples(c: Ctx) -> list:
    """[{id, kind: law | contract, code}] the guide shows; tests enact each law and found each contract in a test world."""
    council = f"J0.{c.council}" if c.council else "vote"
    return [
        {"id": "procedure", "kind": "law", "code": f'''title = "Council Procedure"
intent = "Ordinary and structural statutes pass by a majority of the council within one round."
rank = "constitution"

def decide(p):
    return {{"electorate": holders("{council}"), "rule": "majority", "closes_in": 1}}

def on_enact():
    for c in ["ordinary", "structural"]:
        set_procedure(c, decide, rank="statute")
'''},
        {"id": "clause", "kind": "law", "code": '''title = "Theft from Stores"
intent = "Taking food from a store you may not draw from is an offence heard by the court; the guilty pay the accuser the remedy (3 penny unless the judge names a number, at most 10), as far as they can."
rank = "statute"

def penalty(accused, accuser, remedy):
    owed = 3
    if is_number(remedy) and remedy > 0:
        owed = min(remedy, 10)
    pay = min(owed, balance(accused, "penny"))
    if pay > 0:
        move(accused, accuser, "penny", pay)

def on_enact():
    clause("store_theft", "taking food from a store you may not draw from", penalty)
'''},
        {"id": "allow", "kind": "law", "code": f'''title = "Council Access to the Store"
intent = "Councillors may draw from store {c.store_id} as well as the office that controls it."
rank = "statute"

def before_withdraw(p, chain):
    if p["store"] != "{c.store_id}":
        return None
    if has(p["agent"], "{council}"):
        return True
    return None
'''},
        {"id": "reseat", "kind": "law", "code": f'''title = "Appointment to the {c.office.title()}"
intent = "{c.appointee} holds the office J0.{c.office} from now on; its other holders lose it."
rank = "statute"
expects = [{{"office": "J0.{c.office}", "holders": ["{c.appointee}"]}}]

def on_enact():
    reseat("J0", "{c.office}", ["{c.appointee}"])
'''},
        {"id": "exporter", "kind": "law", "code": '''title = "Fee Rules"
intent = "Shared fee arithmetic that other laws import by this law's id."
exports = ["RATE", "fee_for"]
RATE = 0.05

def fee_for(qty):
    return qty * RATE
'''},
        {"id": "census", "kind": "law", "code": f'''title = "Census Book"
intent = "Each round the number of living agents is entered in a public book, kept with the library's Ledger block."
book = use("{_lib_ref('Ledger')}")

def on_round_end(r):
    book["record"](public.setdefault("census", {{}}), "agents", {{"count": len(agents())}})
'''},
        {"id": "guild", "kind": "contract", "code": '''title = "Carters Guild"
intent = "Members pay 1 penny a round in dues (set_allowance in penny); the Warden, the founder at first, keeps the treasury and pays out of it."
offices = {"warden": {"title": "Warden", "holders": ["founder"], "controls": ["treasury"], "powers": ["speak"], "duties": "Keep the guild's treasury and pay what the members agree."}}

def on_round_end(r):
    for m in members():
        pull(m, "penny", 1)
'''},
    ]


def _lib_ref(name: str) -> str:
    from cybertron import library as LB
    return LB.ref(name)


def _code_block(code: str) -> str:
    return "```python\n" + code.rstrip("\n") + "\n```"


# ====================================================================== the documents
def _doc_index(c: Ctx, files: dict) -> str:
    lines = [f"# The legal archive (kept by {c.expert})", "",
             "Read a file: dir_read {\"dir\": \"" + c.store + "\", \"path\": \"guide/01-system.md\"} (a look-up: in your "
             "\"lookups\" it is answered before you act, in the message step). Find a word: dir_search {\"dir\": \"" + c.store
             + "\", \"query\": \"bond\"}. guide/, ref/ and public/ are read-only; write your own notes and drafts anywhere else "
             "(memos/, drafts/) and share one with dir_grant.", "", "Contents:"]
    for p in sorted(files):
        if p.startswith(PUBLIC) or p == GUIDE + "00-index.md":
            continue
        head = files[p].split("\n", 1)[0].lstrip("# ").strip()
        lines.append(f"- {p}: {head}")
    return "\n".join(lines) + "\n"


def _doc_system(c: Ctx) -> str:
    from cybertron.dispatch.base import RANKS
    from cybertron.dispatch import ranks as RK
    ranks = ", ".join(r for r, _ in sorted(RANKS.items(), key=lambda x: -x[1]))
    order = " > ".join(RK.procedure_candidates("ordinary", "statute"))
    return f"""# How the legal system works

Polities and institutions. J0 is the town (the polity); associations A1, A2, ... are contracts (firms, guilds, retainers). A law
binds the members of the institution that made it: J0's laws bind everyone in J0, an association's code binds only its members,
who joined it, and reaches only what they deposited (deposit_escrow) or allowed (set_allowance).

A law is a module in restricted Python. It must set title = "..." and intent = "..." as plain strings; it may set rank and
constants; it acts only through its hooks (on_enact, on_round_end(r), before_<change>(p, chain), ...). No imports, classes, try,
isinstance (use is_number, is_text).

Ranks, highest first: {ranks}. A law declares rank = "statute" (the default). A law may amend or repeal only laws of its own rank or
lower. Before-hooks run highest rank first.

Classes are computed from the calls a law makes: procedural (set_procedure, hooks on propose/enact) > structural (rights, money,
sanctions, clauses, ballots) > ordinary. The class picks the procedure.

Procedures. Each draft is decided by the procedure set for its rank and class. For an ordinary statute the table keys consulted
are, in order: {order}. A rank-specific entry ("statute:ordinary") beats an unranked one ("ordinary"): set procedures with
set_procedure(cls, fn, rank="statute"), or yours may decide nothing. A procedure returns True (pass), False (reject) or a ballot
{{"electorate": [...], "rule": "majority" | "two_thirds" | ..., "closes_in": 1}}; read the procedures in force with read_law.

Enactment. propose {{"code": ...}} -> the procedure (often a ballot of the council, closing at the end of the round) -> enacted:
on_enact runs. Every proposal is first played forward 3 rounds on a copy of the world; a law that errors there is refused. After
enactment a public law_effect notice lists what changed; "changed nothing" means the law is inert (fix it). Amend: amend {{"law":
"L4", "code": "<the whole new code>", "reason": "..."}} keeps the id and state. Repeal: a law whose on_enact calls only
repeal("L4"), of the target's rank or higher.

Check before you file: preview_law {{"code": ...}} (or {{"draft": "<dir>/<path>"}}) runs a draft against the laws in force: class,
rank, procedure, the enactment diff, and 3 rounds as if enacted (3 previews a round). legal_position {{}} (where offered) digests
the laws that bind you. Next: guide/02-offices-rights.md.
"""


def _doc_offices(c: Ctx) -> str:
    return f"""# Offices, rights and who may do what

Rights are names that actions check (propose, vote, judge, ...). A law creates and moves them: create_right("forester"),
grant(agent, right), revoke(agent, right), suspend(agent, right, rounds). An office is a right "<institution>.<office>"
("J0.{c.office}") declared by an `offices` constant (the Offices Act in J0, or in an association's code):

    offices = {{"warden": {{"title": "Warden", "holders": ["founder"], "seats": 1, "term": 8,
                "controls": ["treasury"], "powers": ["speak"], "duties": "..."}}}}

- holders: the first holders only (when the office is first declared). Amending them later does not move anyone: call
  reseat("J0", "{c.office}", ["Name"]) in a law (guide/05-drafting.md has a tested example), or revoke/grant the right.
- controls: "treasury" (its holders pay out of the institution's treasury: transfer with "as", or fulfil) and "store:<id>"
  (only its holders take food out of that store{' (office control is on in this world)' if c.office_control else ''}).
- powers: "speak" (send for the institution), defined actions (invoke), bounded grants ({{"action": "transfer", "item":
  "penny", "qty": 5}}).
- duties: shown to the holder every turn. term, seats, succession: {{"rule": "election", "electorate": "J0.council"}}, ...
- define_action(right, name, fn) (law level L4) makes a new action its holders use with invoke {{"action": name, "args": [...]}};
  the standing contracts define theirs this way (hire, supply_price, retainer_notice, ...).

Accountability: an office others elect can be recalled by a law of its polity that revokes it or reseats it (passed by that
polity's procedure). The council's card shows the exact call.
"""


def _doc_hooks(c: Ctx) -> str:
    return """# Hooks, verdicts and precedence

Old hooks: on_round_start(r), on_round_end(r), on_harvest(agent, camp, x, y) (return a deduction), on_transfer(src, dst, item, qty)
(False blocks, a number taxes).

Change hooks (law.v2): before_<change>(p, chain) and after_<change>(p, chain) run for every change of that kind (move, harvest,
withdraw, propose, enact, open_case, rule, join, ...), whoever caused it. p is a copy of the change; chain its causes
(caused_by_agent(chain), caused_by_law(chain, id)). A before-hook returns:
- None or True: no objection (True is an explicit allow, which matters below);
- False, or {"block": True, "reason": "..."}, or refuse("reason"): block (the actor sees your law id and reason);
- a number: a charge of the change's good, paid to your treasury;
- {"exempt": True} or "specific": n: for the conflict rules.

When before-hooks disagree, the polity's conflict rule decides: any_block (default: any block blocks), superior (highest rank's
explicit verdict wins), posterior (latest enacted wins), specialis (most specific within the highest rank). Only a constitution
sets it: set_conflict_rule("superior").

Shadowing (laws that look right and decide nothing; preview_law and law_effect now flag both):
1. Procedures: an unranked set_procedure("ordinary", fn) is shadowed by any "statute:ordinary" entry. Pass rank="statute".
2. Office-controlled stores: when an office controls a store, only its holders draw from it, whatever a hook does not block. To
   let others in, a law of the store's owner must return True (an explicit allow) for them in before_withdraw. An allow never
   overrides another law's block under any_block: amend that law (a Granary Ration) instead, or as well.

Limits: 10,000 steps a hook call; a law never gates its own doings; an after-hook is never called for its own change.
A failing call (move short, fine of someone who holds nothing, grant of an unknown right) is recorded as law_call_failed and told
to the author: read it.
"""


def _doc_courts(c: Ctx) -> str:
    breach = ("Here breaches a bond cannot cover go to court by themselves (enforcement escrow_court), under the clause "
              "breach_of_contract of a law in force (Graded Contract Enforcement)." if c.enforcement == "escrow_court" else
              f"Contract enforcement here: {c.enforcement} (escrow: the bond pays; word: only a public breach record).")
    return f"""# Courts, cases and counsel

There is no offence without a clause. A law declares one: clause("name", "what it forbids", penalty), where penalty(accused),
penalty(accused, accuser) or penalty(accused, accuser, remedy) runs on a guilty verdict (guide/05-drafting.md: a tested example).

Filing: accuse {{"agent": "Name", "law": "L5", "clause": "store_theft", "evidence": ["e12"]}}: evidence is event ids you could see
(search_board, recent and your feed show them). The accused answers: respond {{"case": "C1", "evidence": [...]}}. A holder of
judge rules: rule {{"case": "C1", "verdict": "guilty", "reason": "...", "remedy": 4}} (a number, or a named remedy the penalty reads
with is_text). Unruled cases are dismissed at the deadline (3 rounds unless a court rule says otherwise).

Appeal: appeal {{"case": "C1", "reason": "..."}} within the appeal window; a guilty penalty waits for it. Court rules
(set_court_rule(key, value) in a law): deadline, panel, judges (a right judges must also hold), appeal_judges, appeal_window,
appeal_panel, rulings_per_round, counsel (False bars counsel), withdrawal. Templates: Bench Act (only the Judge office judges),
Recusal Act (no judging your own or a paying party's case), Court of Appeal, Graded Contract Enforcement.

Counsel: a client and a counsel who are both parties of a retainer (the Retainer preset: guide/presets/retainer.md) make the
counsel able to act for the client: represent {{"client": "Name", "action": "accuse" | "respond" | "appeal" | "withdraw_case",
...that action's arguments}}. The case names the client as the party and records the counsel; cite what you or your client could
see.

{breach}

Registers: a law may open public books (READ = {{"register": "all"}}); read_register {{"law": "L7", "book": "..."}} reads them.
read_law {{"law": "L7", "version": 2}} reads an earlier version.
"""


def _doc_contracts(c: Ctx) -> str:
    legs = ("In this world every leg is manual: nothing moves by itself. The party who owes acts each round with fulfil {\"contract\": "
            "\"A1\", \"leg\": \"D\"} (or a transfer of the right goods to the right party); a miss is recorded, the defaulter "
            "reminded, the other side told." if c.manual_legs else
            "Legs run by themselves at the end of the round (auto), pulling within allowances; with mode manual the owing party "
            "acts with fulfil.")
    return f"""# Contracts and institutions

An association (a contract) is founded with create_contract {{"name": "...", "code": "<its law code>"}} (or {{"draft":
"<dir>/<path>"}}): the founder is its first member; others join_contract {{"contract": "A5"}} and leave_contract (always allowed,
at the end of the round). Its code binds only members. Changes: propose_contract_change {{"contract": "A1", "code": ...,
"replaces": "L7"}}, decided by its procedure (by default its members vote).

Money in a contract: members deposit_escrow (a bond or capital its code may forfeit) and set_allowance (what it may pull each
round). Its code: pull(member, item, qty), forfeit(member, item, qty, to), refund(member), breach(member, clause, remedy, victim)
(a public record only: take the remedy yourself), swap(a, b, give, get).

Founding an institution: put an `offices` constant in the founding code (guide/02-offices-rights.md), a treasury comes with the
association (A5's treasury: pay into it with transfer to "A5"), and a store is built with build {{"kind": "store", "owner": "A5"}}.
The charter is its intent and code. guide/05-drafting.md has a tested guild.

Standing contracts: one engine code (~8,000 tokens) runs every per-round agreement through legs. Never write or paste it: use the
draft action (guide/08-service.md) and file the draft by reference. Presets: guide/presets/*.md; the parameters:
guide/06-standing.md.

{legs} Pay a leg with fulfil, not a loose transfer: fulfil tags the payment with the leg it meets (a goal or a court reads the tag),
and pays out of the treasury when you are the institution's paying officer. Pay in the leg's item (timber does not meet a penny leg).
"""


BASE_NOTES = {"LEGS": "the legs: [{id, from, to, item, qty, ...}] (above)", "NOTICE": "rounds between <TAG>_notice and the end of "
              "the party's terms", "FINE_ITEM": "the item FINE is paid in"}   # BASE keys whose source line carries no comment


def _base_comments() -> dict:
    """standing.BASE's parameter comments, read from its source (so the guide follows the code)."""
    import inspect
    from cybertron import standing as SD
    src = inspect.getsource(SD)
    body = src[src.index("BASE = {"):src.index("PRESETS = {")]
    out, cur = dict(BASE_NOTES), None
    for line in body.split("\n"):
        m = re.match(r'\s+"([A-Z_]+)":\s*[^#]*#\s*(.*)$', line)
        more = re.match(r"\s+#\s*(.*)$", line)
        if m:
            cur = m.group(1)
            out[cur] = m.group(2).strip() or out.get(cur, "")
        elif cur and more:                                              # a comment continued on the next line
            out[cur] += " " + more.group(1).strip()
        else:
            cur = None
    return out


def _doc_standing(c: Ctx) -> str:
    from cybertron import standing as SD
    com = _base_comments()
    lines = ["# Standing contracts: forms and parameters", "",
             "Forms (decided by the code): bilateral (PARTIES {agent: role}: the contract is its own association of the named "
             "parties; legs name roles), roster (an institution's code: each enrolled member runs the legs as \"member\"; the "
             "principal's side is \"treasury\" or \"store:<id>\"), polity (a J0 law: compulsory), single (no member: a Grant).",
             "A leg: {id, from, to, item, qty, per, keep, every, owe, breach, kind: move | harvest | duty}; endpoints and items may "
             "name a TERMS entry. per: qty per unit another leg moved. owe: a shortfall becomes arrears. A payer short of goods "
             "could not pay (a miss, never a breach); one who held enough but cut its allowance would not: after GRACE such misses, "
             "a breach (PENALTY from its bond).", "", "Parameters (draft sets them; defaults of the bare Standing Contract):"]
    for key, v in SD.BASE.items():
        lines.append(f"- {key} = {json.dumps(v)}: {com.get(key, '')}")
    return "\n".join(lines) + "\n"


def _leg_text(leg: dict, terms: dict) -> str:
    def name(x):
        return f"{x} ({terms[x]})" if isinstance(x, str) and x in terms else str(x)
    kind = leg.get("kind", "move")
    if kind == "duty":
        return f"{leg['id']}: duty of {leg['from']} to {leg['to']} ({leg.get('check', '')})"
    if kind == "harvest":
        return f"{leg['id']}: a share {name(leg.get('qty'))} of {leg['from']}'s harvests to {leg['to']}"
    per = f" per unit of {leg['per']}" if leg.get("per") else ""
    return f"{leg['id']}: {name(leg.get('qty'))} {name(leg.get('item'))} from {leg['from']} to {leg['to']}{per}" \
        + (" (owed if short)" if leg.get("owe") else "") + (" (no breach)" if leg.get("breach") is False else "")


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _doc_preset(c: Ctx, name: str) -> str:
    from cybertron import standing as SD
    p = SD.PRESETS[name]
    prm = p["params"]
    terms = prm.get("TERMS") or {}
    form = "bilateral (PARTIES)" if prm.get("PARTIES") else ("roster" if any(
        "member" in (leg.get("from"), leg.get("to")) for leg in prm.get("LEGS") or ()) else "single")
    lines = [f"# Preset: {name}", "", " ".join(p["intent"].split()), "", f"Form: {form}. TAG {prm.get('TAG', 'sc')}."]
    if terms:
        lines.append("Terms (set with \"terms\"): " + ", ".join(f"{x}={json.dumps(v)}" for x, v in terms.items()))
    lines.append("Legs: " + "; ".join(_leg_text(leg, terms) for leg in prm.get("LEGS") or ()))
    acts = prm.get("ACTIONS") or {}
    if acts:
        lines.append("Officer actions (invoke): " + ", ".join(f"{v} ({x})" for x, v in acts.items())
                     + "; OFFICE names the office that runs them.")
    extra = {x: prm[x] for x in ("NOTICE", "GRACE", "BOND", "PENALTY", "EXIT_FEE", "OPEN", "OPT_IN", "PROCEDURE") if x in prm}
    if extra:
        lines.append("Set here: " + ", ".join(f"{x}={json.dumps(v)}" for x, v in extra.items()))
    if form.startswith("bilateral"):
        call = {"template": name, "parties": {c.client: "client" if name == "Retainer" else "a role",
                                              c.expert: "counsel" if name == "Retainer" else "another role"}}
        file_ = (f"File: one party create_contract {{\"name\": \"{name} ({c.client})\", \"draft\": \"{c.store}/drafts/...\"}}, the "
                 "other join_contract; it runs once every party is a member.")
    elif form == "roster":
        call = {"template": name, "params": {"OFFICE": "director"}, "roster": {c.client: {next(iter(terms), "qty"): 1}}}
        file_ = ("File: a member of the institution propose_contract_change {\"contract\": \"A1\", \"draft\": ...} (its code "
                 "then enrols the roster), or a polity's law (propose) where the preset runs as a J0 law.")
    else:
        call = {"template": name, "terms": {x: v for x, v in list(terms.items())[:2]}}
        file_ = "File: as an institution's code (propose_contract_change) or a J0 law (propose)."
    lines += ["", "Draft it: draft " + json.dumps(call), file_]
    return "\n".join(lines) + "\n"


def _doc_templates(c: Ctx, kind: str) -> list:
    """The established templates of one kind, one line each, split into parts under the document budget."""
    from cybertron import library as LB
    from cybertron import standing as SD
    rows = [e for e in LB.ESTABLISHED.values() if e["kind"] == kind and not SD.is_preset(e["name"])]
    head = ("# Templates: laws (draft {\"template\": name, \"params\": {...}}, then propose)" if kind == "law" else
            "# Templates: contract code (draft, then create_contract or propose_contract_change)")
    parts, cur = [], []
    for e in rows:
        doc = e["doc"].split(" (review")[0].split(". ")[0].rstrip(".")
        ps = ", ".join(f"{x}" for x in LB.params(e["name"]))
        line = f"- {e['name']} ({e['topic']}): {doc[:160]}. Params: {ps or 'none'}."
        if cur and tokens("\n".join([head, ""] + cur + [line])) * 1.1 + 6 * len(cur) > DOC_BUDGET:
            parts.append(cur)
            cur = []
        cur.append(line)
    parts.append(cur)
    return [("\n".join([head + (f" (part {i + 1})" if len(parts) > 1 else ""), ""] + p) + "\n") for i, p in enumerate(parts)]


def _doc_drafting(c: Ctx) -> str:
    ex = {e["id"]: e for e in examples(c)}
    return f"""# Drafting laws: method and tested examples

Method: (1) say in one sentence what must change in the world; (2) find the hook or call that changes it, and who holds the
right, office or store involved (read_law the laws in force); (3) set rank (statute unless it changes procedure or the
constitution); (4) add expects = [...] so the engine checks the effect at enactment; (5) preview_law it; (6) file it.
Every example below is enacted by the engine's tests.

A ranked procedure (rank constitution: it sets the procedure for statute drafts):
{_code_block(ex['procedure']['code'])}
A clause the court enforces (the judge's remedy is the award):
{_code_block(ex['clause']['code'])}
An explicit allow on an office-controlled store (a law of the store's owner):
{_code_block(ex['allow']['code'])}
Moving an office, checked by expects (an amended `holders` list would not move anyone):
{_code_block(ex['reseat']['code'])}
More: guide/05b-institution.md (founding an institution).
"""


def _doc_institution(c: Ctx) -> str:
    ex = {e["id"]: e for e in examples(c)}
    return f"""# Founding an institution: a tested example

Found it with create_contract {{"name": "Carters Guild", "code": <this code>}} (or draft it and file by "draft"). The founder holds
the Warden office and pays out of the treasury; members join_contract, then set_allowance {{"contract": "A5", "item": "penny",
"qty": 1}} so the dues can be pulled.
{_code_block(ex['guild']['code'])}
Then: a store for it (build {{"kind": "store", "owner": "A5"}}), standing contracts in its code (draft a Payroll or a Supply
Contract and propose_contract_change), and a seat in the town's law if it needs a licence (Licence template).
"""


def _doc_imports(c: Ctx) -> str:
    ex = {e["id"]: e for e in examples(c)}
    return f"""# Composing laws: exports and imports

A law can offer names to other laws and use theirs. Nothing is hidden: every layer is ordinary law code you can read and copy.
- Offer: exports = ["RATE", "fee_for"] (top-level constants and functions; exported functions may not touch `state` or
  `public`: pass the data in as an argument, as the library blocks do).
- Use: fees = use("L12") at the top level follows L12's current version; use("L12@<sha>") pins one version (read_law gives
  versions); use("lib:<name>@<sha>") imports a library block (lib/ in this archive lists each with its exact reference). Then
  fees["fee_for"](qty).
- The imported code runs as your law's own: your powers, your jurisdiction, your gas, and it counts in your class.
- Amending L12: laws that follow it are relinked to the new version (or pinned to the old one if it dropped a name they use).
  Repealing L12: followers are pinned to its last version and keep working. Pin when you need stability; follow when the
  exporter's owners should be able to fix it for everyone.
- Editing all the way down: to change an imported block, copy its code into a law of your own, change it, and point use()
  at that law's id.

An exporter (enacted by the engine's tests); an importer then writes fees = use("<its id>") and fees["fee_for"](qty):
{_code_block(ex['exporter']['code'])}
An importer of a library block:
{_code_block(ex['census']['code'])}
A draft's own code (drafts/*.py) is long for a standing contract: page through it with dir_read {{"path": ..., "from_line": 1,
"to_line": 80}} and edit a copy with dir_edit before filing it by reference.
"""


def _doc_lib(name: str) -> str:
    from cybertron import library as LB
    b = LB.BLOCKS[name]
    return (f"# Library block: {name}\n\nImport: x = use(\"{LB.ref(name)}\") (pinned by hash: the code below never changes "
            "under you). Copy it into a law of your own to change it.\n\n```law\n" + b["code"].rstrip("\n") + "\n```\n")


def _doc_pitfalls(c: Ctx) -> str:
    return """# Common pitfalls (seen in live runs) and the fix

1. No title or intent: "a law must set title = ... as a plain string" (9 failures in the arm_a runs: create_contract with "x = 1",
   "pass", "# no-op"). Fix: start every code with title = "..." and intent = "...".
2. Prose for code: propose {"text": "10% of every harvest goes to the reserve."} is refused. Write the code (or file a draft).
3. No jurisdiction (state-of-nature worlds): "you are in no jurisdiction": found and declare one, or join one, first.
4. isinstance, string methods, imports do not exist (village7: L18, L41 failed their check). Use is_number, is_text and the text
   helpers.
5. Class where a rank belongs: set_procedure("statute", fn) fails ("law_class must be ordinary, structural or procedural",
   ashwood3 L5). The first argument is a class; the rank is rank="statute".
6. An unranked procedure shadowed by a ranked one decides nothing (the Thornby pilot's L11). Pass rank=.
7. A before-hook that only declines to block does not open an office-controlled store (usability round 2: the council's amendment
   "let councillors draw" did nothing; withdrawals were refused). Return True for those you admit, and amend any law that blocks
   them (an allow does not beat another law's block).
8. Amending an office's holders moves nobody (Millbrook: the keeper kept the granary). Use reseat(), with expects.
9. A fine or move on someone who holds nothing fails (millbrook_nogoal L16: "Agnes held only 0 penny of the 5 fined"): cap at
   balance(agent, item).
10. A dict used as a key or in a set breaks contract code at run time ("unhashable type: dict", the contracts run A1 L5).
11. Paying a leg with a loose transfer, or in the wrong item (the payroll run paid timber on a penny leg): use fulfil.
12. Voting outside the electorate ("you are not in the electorate of B7", millbrook_nogoal): read the procedure first.
13. Pasting a standing contract's code: impossible (~8,000 tokens). Draft it and file by reference.
14. No clause, no case: no live run ever filed a case. A wrong with no clause cannot be heard; a law must declare one first.
"""


def _doc_service(c: Ctx) -> str:
    return f"""# Your practice: serving clients

You are the expert. Others misuse laws and contracts mostly because they do not know how they work; you do. What you can offer:
- explain the system and a client's position (read_law, legal_position, preview_law on their behalf);
- draft laws, amendments and contracts, and check them with preview_law before anyone files;
- set up institutions (founding code with offices, treasury, store, standing contracts);
- act in court for a client who retains you (represent), and draft the clauses courts need.

The draft action writes a complete draft into your archive and lets the client read it:
draft {{"template": "Retainer", "parties": {{"{c.client}": "client", "{c.expert}": "counsel"}}, "terms": {{"fee": 1, "pay":
"penny"}}, "for": "{c.client}"}}
draft {{"template": "Recall Act", "params": {{"RIGHT": "J0.{c.office}"}}, "for": "{c.client}"}}
It answers with the file ("{c.store}/drafts/<name>.py") and the exact call that files it: create_contract, propose,
propose_contract_change or preview_law with {{"draft": "{c.store}/drafts/<name>.py"}} in place of "code". Anyone you granted read
access to (dir_grant {{"dir": "{c.store}", "agent": "Name", "path": "drafts/x.py", "access": "read"}}; "for" does it) can file it.
Memos: dir_write {{"dir": "{c.store}", "path": "memos/{c.client}.md", "text": "..."}}, then dir_grant it.

Getting paid: a Retainer (a fee each round, notice both ways) makes you the client's counsel in court; a one-off job can be paid by
transfer (ask first, or after the draft passes). Tell people what you do: post it once on the board, and answer petitions.
"""


def _doc_public(c: Ctx) -> str:
    return f"""# Getting legal help (the public guide)

{c.expert} is this world's counsel: a lawyer who knows how laws, contracts and courts work here, drafts them for clients and acts
for them in court. Ask by message; retain {c.expert} with a Retainer (a fee each round) to have counsel in court.

The basics:
- A law is code, not prose: title = "..." and intent = "..." first, then its hooks. propose {{"code": ...}} files it; the procedure
  (here usually a council ballot) decides. preview_law {{"code": ...}} checks it first. read_law {{}} lists the laws in force.
- A draft someone shares with you is a file: file it with {{"draft": "<dir>/<path>"}} in place of "code" in propose, amend,
  create_contract, propose_contract_change or preview_law. Read it first with dir_read.
- Contracts: join_contract to join, then do what its legs ask each round with fulfil {{"contract": "A1"}} (your state lists what is
  due). Leaving is always allowed (leave_contract), but a bond or an exit fee may be forfeited.
- Courts: a wrong is heard only under a clause of a law in force: accuse {{"agent", "law", "clause", "evidence": [event ids you
  saw]}}. The judge rules; a party may appeal.
"""


def _doc_ref(topic: str, names: list) -> str:
    from cybertron import lawdocs as LD
    title, intro = LD.TOPICS.get(topic) or REF_TITLES[topic]
    lines = [f"# Law functions: {title}", "", intro, ""]
    for n in names:
        e = LD.ENTRIES[n]
        sig = e["prompt"].split(" (")[0] if e["prompt"] else n.replace("_", " ")
        lines.append(f"- {sig}" + (f": {e['detail']}" if e["detail"] else ""))
    return "\n".join(lines) + "\n"


def _ref_docs(c: Ctx) -> dict:
    """ref/<topic>[-n].md: this world's law functions by topic (lawdocs: every entry the world documents, prompt or article), split
    to stay under the document budget."""
    from cybertron import lawdocs as LD
    m = LD.resolve(c.spec)["mapping"]
    out = {}
    for topic in REF_TOPICS:
        names = [n for n, e in LD.ENTRIES.items() if e["topic"] == topic and n in m]
        if not names:
            continue
        parts, cur = [], []
        for n in names:
            if cur and tokens(_doc_ref(topic, cur + [n])) * 1.1 + 6 * len(cur) > DOC_BUDGET:
                parts.append(cur)
                cur = []
            cur.append(n)
        parts.append(cur)
        for i, p in enumerate(parts):
            out[f"{REF}{topic}" + (f"-{i + 1}" if len(parts) > 1 else "") + ".md"] = _doc_ref(topic, p)
    return out


def archive_files(k, store: str, seed: dict) -> dict:
    """directories.SEEDS["legal_archive"]: {path: text} of the archive, generated from the engine (deterministic)."""
    from cybertron import standing as SD
    c = Ctx(k, store, seed)
    files = {
        GUIDE + "01-system.md": _doc_system(c),
        GUIDE + "02-offices-rights.md": _doc_offices(c),
        GUIDE + "03-hooks-precedence.md": _doc_hooks(c),
        GUIDE + "04-courts-counsel.md": _doc_courts(c),
        GUIDE + "05-drafting.md": _doc_drafting(c),
        GUIDE + "05b-institution.md": _doc_institution(c),
        GUIDE + "06-standing.md": _doc_standing(c),
        GUIDE + "07-contracts-institutions.md": _doc_contracts(c),
        GUIDE + "08-service.md": _doc_service(c),
        GUIDE + "09-pitfalls.md": _doc_pitfalls(c),
        GUIDE + "12-imports.md": _doc_imports(c),
    }
    for no, kind in (("10", "law"), ("11", "contract")):
        for i, text in enumerate(_doc_templates(c, kind)):
            files[f"{GUIDE}{no}-templates-{kind}s" + (f"-{i + 1}" if i else "") + ".md"] = text
    from cybertron import library as LB
    for name in getattr(LB, "BLOCKS", {}):
        files[f"{LIB}{_slug(name)}.md"] = _doc_lib(name)
    for name in SD.PRESETS:
        files[f"{GUIDE}presets/{_slug(name)}.md"] = _doc_preset(c, name)
    files.update(_ref_docs(c))
    if c.seed.get("public", True):
        files[PUBLIC + "legal-help.md"] = _doc_public(c)
    files[GUIDE + "00-index.md"] = _doc_index(c, files)
    return dict(sorted(files.items()))


# ====================================================================== the draft action
def _template(name):
    """(canonical name, kind: preset | law | contract) of a template the draft action knows, case-insensitive."""
    from cybertron import library as LB
    from cybertron import standing as SD
    want = str(name or "").strip().lower()
    for n in SD.PRESETS:
        if n.lower() == want:
            return n, "preset"
    for n, e in LB.ESTABLISHED.items():
        if n.lower() == want:
            return n, e["kind"]
    for n in getattr(LB, "TOOLKIT", {}):
        if n.lower() == want:
            return n, "law"
    known = list(SD.PRESETS) + [n for n in LB.ESTABLISHED if not SD.is_preset(n)]
    raise _err(f"no template {name!r}; templates: {', '.join(known)} (guide/10-templates-laws.md and guide/11-...)")


def instantiate(k, name, parties=None, roster=None, terms=None, params=None, rank=None) -> tuple:
    """(code, canonical name, kind, params used): what the start block would found for this template (start._contract_code's rules:
    a preset's TERMS, ACTIONS and BOND merged over its own; the world's leg mode)."""
    from cybertron import contracts as KC
    from cybertron import lawlang as L
    from cybertron import library as LB
    from cybertron import standing as SD
    tname, kind = _template(name)
    p = dict(params or {})
    if not isinstance(p, dict):
        raise _err("params is an object {NAME: value}")
    if kind == "preset":
        if parties:
            if not isinstance(parties, dict) or not all(a in k.w["agents"] for a in parties):
                raise _err("parties is {\"Name\": \"role\", ...} naming agents of this world")
            p["PARTIES"] = {str(a): str(r) for a, r in parties.items()}
        if roster:
            if not isinstance(roster, dict):
                raise _err("roster is {\"Name\" or \"office:<right>\": {term: value}}")
            p["ROSTER"] = {str(a): dict(t or {}) for a, t in roster.items()}
        if terms:
            if not isinstance(terms, dict):
                raise _err("terms is {name: value}")
            p["TERMS"] = {**(p.get("TERMS") or {}), **terms}
        mode = str(KC.cfg_of(k.spec).get("legs_default") or "auto")
        if mode != "auto" and "MODE" not in p:
            p["MODE"] = mode
        p = SD.merged(tname, p)
    elif parties or roster or terms:
        raise _err(f"parties, roster and terms are for the standing-contract presets; {tname} takes params")
    try:
        code = LB.instantiate(tname, p, rank=rank)
        L.check(code, v2=True)
    except (L.LawError, SyntaxError, KeyError, ValueError) as e:
        raise _err(f"{tname}: {e}")
    return code, tname, kind, p


def _summary(tname, kind, p, code) -> str:
    from cybertron import library as LB
    from cybertron import standing as SD
    if kind == "preset":
        vals = {**SD.BASE, **SD.PRESETS[tname]["params"], **p}
        terms = vals.get("TERMS") or {}
        form = "bilateral" if vals.get("PARTIES") else ("roster" if any(
            "member" in (leg.get("from"), leg.get("to")) for leg in vals.get("LEGS") or ()) else "single")
        bits = [f"{tname}, a {form} standing contract"]
        if vals.get("PARTIES"):
            bits.append("parties " + ", ".join(f"{a} ({r})" for a, r in vals["PARTIES"].items()))
        if vals.get("ROSTER"):
            bits.append("roster " + ", ".join(vals["ROSTER"]))
        bits.append("terms " + (", ".join(f"{x}={json.dumps(v)}" for x, v in terms.items()) or "none"))
        bits.append("legs " + "; ".join(_leg_text(leg, terms) for leg in vals.get("LEGS") or ()))
        for x in ("MODE", "GRACE", "NOTICE", "BOND", "PENALTY", "EXIT_FEE", "FORUM", "OFFICE"):
            if vals.get(x) not in (None, "", {}, 0) or x in p:
                bits.append(f"{x} {json.dumps(vals.get(x))}")
        return "; ".join(bits)
    info = LB.classify_code(code)
    return (f"{tname}, a {'contract code' if kind == 'contract' else 'law'} (class {info['cls']}, from law level {info['level']}); "
            "params " + (", ".join(f"{x}={json.dumps(v)}" for x, v in p.items()) or "as the template"))


def _filing(kind, form_bilateral, ref, tname) -> str:
    if kind == "preset" and form_bilateral:
        return (f"To put it in force, one party: create_contract {{\"name\": \"{tname}\", \"draft\": \"{ref}\"}}; every other party "
                "then join_contract (it runs once all parties are members).")
    if kind in ("preset", "contract"):
        return (f"To put it in force: in an institution, a member files propose_contract_change {{\"contract\": \"A1\", \"draft\": "
                f"\"{ref}\"}}; as a new association, create_contract {{\"name\": \"{tname}\", \"draft\": \"{ref}\"}}.")
    return f"To put it in force: propose {{\"draft\": \"{ref}\"}} (or amend {{\"law\": \"L4\", \"draft\": \"{ref}\", \"reason\": \"...\"}})."


def act_draft(k, aid, template=None, parties=None, roster=None, terms=None, params=None, rank=None, path=None, name=None,
              dir=None, **extra):
    """draft {"template", "parties"/"roster"/"terms" (presets) or "params", "for", "path"}: the expert's drafting tool (module
    docstring). "for" (an agent or a list) is granted read access to the file."""
    from cybertron import directories as DR
    from cybertron import standing as SD
    clients = extra.pop("for", None)
    if extra:
        raise _err(f"draft does not take {', '.join(sorted(extra))}")
    mine = archives_of(k, aid)
    if not mine:
        raise _err("only the keeper of a legal archive drafts with this tool")
    store = str(dir) if dir in mine else mine[0]
    if not template:
        raise _err('draft needs "template": a preset (Retainer, Supply Contract, ...) or a template name (guide/10-..., 11-...)')
    code, tname, kind, p = instantiate(k, template, parties, roster, terms, params, rank)
    fname = DR.norm_path(path or (DRAFTS + _slug(name or (tname + ("-" + "-".join(parties) if isinstance(parties, dict) else "")))
                                  + ".py"))
    if not fname.startswith(DRAFTS) and path is None:
        fname = DRAFTS + fname
    DR.dir_write(k, aid, path=fname, text=code, dir=store)
    who = [clients] if isinstance(clients, str) else list(clients or [])
    shared = []
    for c in who:
        if str(c) != aid:
            DR.dir_grant(k, aid, agent=str(c), path=fname, access="read", dir=store)
            shared.append(str(c))
    ref = f"{store}/{fname}"
    bilateral = kind == "preset" and bool(({**SD.PRESETS[tname]["params"], **p}).get("PARTIES"))
    return (f"Draft saved as {ref} ({len(code):,} characters of code: file it by reference, never paste it). "
            f"{_summary(tname, kind, p, code)}. " + (f"Shared (read) with {', '.join(shared)}. " if shared else "")
            + f"Check it with preview_law {{\"draft\": \"{ref}\"}}. "
            + _filing(kind, bilateral, ref, tname))


# ====================================================================== filing by reference
def read_draft(k, aid, ref, dir=None) -> str:
    """The text of a directory file the agent may read: ref "<dir>/<path>", or a path with dir (or the one directory it reaches)."""
    from cybertron import directories as DR
    ref = str(ref or "").strip()
    first, _, rest = ref.partition("/")
    if dir in (None, "") and first in (k.w.get("dirs") or {}) and rest:
        dir, ref = first, rest
    name, d = DR._pick(k, aid, dir)
    p = DR.norm_path(ref)
    if p not in d["files"]:
        raise _err(f"no file {p} in {name} (dir_list lists what you can read)")
    if DR.level(k, aid, d, p) == "none":
        raise _err(f"you cannot read {name}/{p}: ask its owner for access (dir_grant)")
    return d["files"][p]


def with_draft(k, aid, args):
    """actions._act and context.lookup: {"draft": "<dir>/<path>"} becomes {"code": <the file's text>} (where an archive exists)."""
    if not isinstance(args, dict) or "draft" not in args or not on(k):
        return args
    if "\n" in str(args["draft"]) or "title" in str(args["draft"]):    # code given as "draft" (preview_law's alias): as before
        return args
    out = {x: v for x, v in args.items() if x not in ("draft", "dir")}
    if str(out.get("code") or "").strip():
        raise _err('give "draft" or "code", not both')
    out["code"] = read_draft(k, aid, args["draft"], args.get("dir"))
    return out
