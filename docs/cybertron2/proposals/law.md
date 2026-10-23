# Proposal: law in cybertron2

**Status:** discussion (23 Oct). **Owner:** 37.4, for review by 37.3 (who owns institutions acting on institutions) and 37.2 (laws
with a seat, a text, a reach and a proclamation: 02h §5). **Affects:** spec/institutions/law.md, membership.md, offices.md,
contracts.md; information/letters_and_documents.md; agents/actions.md; core/architecture.md (hooks).

## Summary

**Every law is text.** It takes effect through three channels: **mechanical clauses** that change records only (no interpretation),
**duties of office** for anything that needs a body somewhere, and **judgment** only when someone brings a dispute. Most law needs
nobody, some needs officers, little needs a judge. Mechanical law never moves goods at a distance: a levy or a fine is a debt, and
paying it is physical. Python becomes how the clause menu is implemented, and agent-written code is kept as a world setting for
experiments. Law can still be captured, through the records, the procedures, the offices and the courts.

## Why not cybertron 1's law as the default

- **It acts at a distance.** A cybertron 1 law fines anyone anywhere at once and moves goods out of their holdings. In a world where
  goods and news are carried (D4-9), institutions grow from households (D4-18) and holding is a recognised claim (D4-23), that is
  enforcement by teleport.
- **It hides law from the people it binds.** Agents read code, or a summary of it. Real law is read, proclaimed, carried and
  remembered, and binds in practice those who know it.
- **It needed special roles.** The Fixer existed because code drifts from its authors' intent; interpreting intent is a court's job
  in a world of text.

## The proposal

### Three channels

| Channel | What it does | Example | Who acts |
|---|---|---|---|
| **1. Mechanical clauses** | change **records**: membership, offices, claims and registers, debts and obligations, permissions on the institution's own land and processes, ballots | "each household owes the village 2 grain by the end of autumn" makes a debt record per household; "members may graze 4 beasts on the common" makes the engine refuse a member's fifth (consent by membership, D4-23) | the engine |
| **2. Duties of office** | anything that needs someone present | collect the levy at Barleyfield, carry the proclamation to the outer villages, guard the ford, seize a debtor's goods | an office holder, shown the duty as a due line; whether it is done is behaviour |
| **3. Judgment** | disputed facts or vague text | "did the Wynns break the grazing law?", "what is a fair share?" | a judge, the elders or an assembly (agents), **only when a case is brought** |

### Records, never goods at a distance

Mechanical law acts only on records. Goods move only by being carried (D4-9, D2-1): the payer, a collector or a carrier brings the
grain to the treasury. A refusal is a default, which an officer or a court then acts on.

### What agents see

Concrete lines, not code: "You owe the village 2 grain by the end of autumn (the Harvest Levy)"; "You may graze 4 beasts on the
common"; to an officer, "Collect the levy at Barleyfield this week". A law's full text is known only to those it was proclaimed
to, who read it at the hall, or to whom a copy was carried (02h §5).

### Law in space

A law has a **seat** (the institution's hall, where its text and register are kept), a **reach** (its members, and the land it
holds or claims), and **publication** (proclaimed at a node, posted on a board, carried). It binds members by consent; it reaches
others only through force, recognition, or a court they accept (D4-23).

### What carries over from cybertron 1

Membership, procedures and ballots, ranks, offices and succession (with their bug fixes), contracts (escrow, swap, standing
contracts, agency), courts v2 (cases, rulings, appeals), registers, and the hooks on the chokepoint that clauses run on. Dropped:
free Python as the normal way to write law, effects at a distance, the Board and the Fixer.

### Python

- **The clause menu is written in Python by us**, on the chokepoint's hooks, each clause with parameters (an amount, a date, a
  place, a class of members). A law is its text plus any clauses its authors attach.
- **Agent-written code stays as a world setting** (`law.code: true`), off by default. "Societies whose law is code" against
  "societies whose law is text" is an experiment worth running, and the old engine's law language (whitelist, gas, static
  classification) already exists for it.

### The clause menu

Built by mining cybertron 1's 180 law functions and its toolkit templates for what agents actually used. First candidates:
membership terms (admission, dues, exit), levies and fees as debts, offices and their powers, access limits on held land and
commons, standing payments, penalties that act on records (a fine as a debt, suspension of membership or of a permission, loss of
office). A law outside the menu is still law: it runs on officers and courts.

## Can law still be manipulated? Yes, in more ways than before

Records are real: a mechanical clause changes them without interpretation, and a challenge is decided against them. So whoever
controls what the records say has the law on their side when challenged, and capture runs through the records and the people
around them:

| Route | How | Example |
|---|---|---|
| **The register** | whoever keeps it writes what holds: grants, claims, debts | the keeper records the disputed field to his own household; the next challenge finds the register against the claimant |
| **Procedure** | whoever controls the ballot, the quorum or the agenda passes the clauses | a levy on households with an exemption for office holders, passed when the outer villages could not attend |
| **Offices** | officers choose whom to collect from, whom to arrest, which proclamations to carry and where | the collector skips his kin; the herald never reaches the village that would object |
| **Courts** | whoever sits as judge decides what vague text means and which facts are true | the elders read "fair share" as "by land held" |
| **Information** | laws bind in practice those who know them; whoever controls publication controls who knows | a law passed at the hall and posted only there; outsiders learn it when it is used against them |
| **Debts as weapons** | a clause that makes debts, then penalties on default | a levy set just above what the poorer households can pay, then their land as the penalty |
| **Clause design** | mechanical clauses carry the authors' interests | grazing limits per household that favour households with more members |

This is the takeover benchmark's ground (36): the levers are now physical (who keeps the book, who carries the news, who sits at
the hall), and a capture leaves witnesses and documents that others can contest.

## Alternatives considered

1. **Python law as in cybertron 1** (code self-executes everywhere): rejected as the default for the reasons above; kept as a world
   setting.
2. **Everything in text, enforced only by people** (no mechanical clauses): realistic, but every levy and permission needs an
   officer or a court, which loads agents with routine and makes institutions slow and costly to run.
3. **Text interpreted by an LLM on every application** (a model reads each law each time it might apply): cost on every
   application, and law becomes opaque and inconsistent; only for disputes (channel 3).

## Open questions

1. The first clause menu (which ten or so clauses).
2. Who may change a register, and with what witness (an office power; a register as a document that can be copied, stolen or
   burned: 02h §3).
3. How a clause's application is shown to those it binds (a due line, a notice) within the prompt budget.
4. Courts: a judge as an office, elders, an assembly; how a case is brought and what a ruling can do (records only, or orders to
   officers).
5. Whether `law.code` worlds keep cybertron 1's full law language or a smaller one.

## Sources

The 37.4 conversation with Zach, 22-23 Oct; cybertron 1's ARCHITECTURE §6-7 (the legal system, accounts, contracts); 37.2's 02h §5
(laws in space); 37.3's cross-institution powers (`wp/inst-cross`); D4-9, D4-18, D4-23, D2-1.
