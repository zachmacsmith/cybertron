# Proposal: the economics of information

**Status:** partly accepted (swept 5 Nov): D2-7, D2-8; documents as goods on parchment (D2-24), each somewhere (D4-35). Built: speech
at a node (D4-25, D4-30, D4-65; OPEN C-3 closed); lines written on buildings (D2-169, D2-170). Not built: parchment, documents,
letters, boards, shelves, scribes. Still open: 5 questions (in Open questions); large worlds superseded by the generator. **Owner:**
37.2 for the economics (materials, scribes, the price of a page, libraries and archives as buildings); 37.4 owns spec/information
(channels, letters, speech: OPEN C-3, C-4); laws are in [law.md](law.md). **Affects:** spec/economy/goods.md, buildings.md;
information/letters_and_documents.md and speech (37.4's).

## Summary

Information crosses nodes only by being carried (D4-9), so most of this is about **turning knowledge into objects and pricing
them.** A written document is knowledge with almost no weight, a cost to make, a place, an author and a date: it can be carried,
copied, posted, stored, stolen, forged and burned. Wide reach costs more (D2-8): rumour is free and uncontrolled, a paper is dear and
controlled by its editor. The cost of a page is the scribe's time, so parchment from hides is enough for first worlds and the press
is the later jump.

## The proposal

### Writing materials (02h §2)

| Material | Made from | Good for | First worlds |
|---|---|---|---|
| parchment | hides, scraped and dried (0.5 units a sheet, 02j) | lasting records, letters, maps | yes |
| wax tablets | beeswax, a frame | notes, tallies, local | maybe |
| paper | fibre rags at a paper mill (0.2 a sheet) | letters, notices, editions | later (fibre deferred) |
| ink | soot or oak galls | all writing | folded into writing |

**A page written costs about 1.5 units on parchment, 1.2 on paper; a printed copy about 0.26** (02j). Literacy is a skill learned
by practice and teaching; reading aloud for others is a service.

### Documents as objects (02h §3)

A document has text, author, round, node, seal, copy-of (with copier and round) and condition. Acts: write, read, copy, seal, give,
carry, store, post. Copies carry their provenance (cybertron 1's `documents.py`).

### Speech at a node (D2-7; mechanism 37.4's, OPEN C-3, closed 2 Nov: D4-25, D4-30, D4-65; built)

The square (everyone at the node); rooms (everyone at the node with access to the building, several in a day); private messages to
anyone at the node. Buildings become access to information.

### The information ladder (D2-8; 02h §4b)

| Rung | Reach | Who pays | Controlled by |
|---|---|---|---|
| rumour (telling merchants and travellers) | wherever they go | nobody | nobody |
| a letter | one reader | the sender: a sheet, writing, a carrier | the sender; the carrier can read an unsealed one |
| a notice | everyone at one node | the poster | whoever controls the board |
| a newsletter or paper | subscribers at many nodes | readers, patrons, placements | the editor |
| a post (later) | anyone on its routes | a fee, or a subsidy | whoever runs it |
| a press (later) | thousands | a large fixed cost | the press owner, the censor |

An edition reaching 50 readers at 5 nodes costs about 1.9 units a reader by hand, about 1 printed; **carriage dominates once
copies are cheap**, so papers ride the merchants' routes.

### Libraries, archives and maps (02h §6, §6b)

- An institution's seat is a building; its records are kept there; what leaves is only what someone carries out, **by telling**
  (testimony: partial, slanted, uncheckable) or **by giving a document** (checkable against the seal and other copies). Merchants
  carry both, so they broker information as well as goods.
- A library or archive is a building with shelves (02i §3); copying is scribes' work; a fire erases it.
- The lawyer's legal archive becomes a law library at the seat; the historian's chronicle an archive building.
- A map is a document freezing its maker's knowledge as of a date; reading it writes dated beliefs; maps can be wrong, stale or
  forged, and a frontier map is a valuable good (37.5).

### Large worlds with small settlements (02h §8)

Yes, after the small-scale economy works: 15-20 nodes, 2-3 settled hamlets of 8-12 people, unsettled land between, 60-100 rounds,
growth and depletion on. Expansion needs growth, depletion and a reason beyond; a 20-round run will show none.

## Why

Zach rates information the most important unlock. In space, every information institution (the record, the law, the library, the
post, the paper) is built from documents in places, and its power comes from who controls the copies, the boards and the carriers.

## Alternatives considered

- **Wood-pulp paper from timber:** rejected (a 19th-century technique; timber regrows slowly); parchment and fibre paper instead.
- **Channels as cybertron 1's global logs:** replaced by media in places on the same channel record (OPEN C-4).
- **Hiding in a building:** later.

## Open questions

02h §9: documents as objects (2); channels as media in places (3, with 37.4); institutions as buildings with the two archives ported
(6); large worlds (5); shelves counted in documents or pages (02i §8.5); whether wax tablets are worth a good.

As of 5 Nov:
- Documents as objects: still open in part. D2-24 and D4-35 make a document a good with a place; spec/information/
  letters_and_documents.md keeps text, author, day, place; seals, copies and condition are undecided, and nothing is built.
- Channels as media in places: still open (OPEN C-4, 37.4: letters and boards first).
- Institutions as buildings with the two archives ported: still open; no decision, and the only institutions built are households.
- ~~Large worlds~~: superseded by the generator (D2-173 to D2-191; D2-181's region of 4 settlements with wild land between) and
  growth to towns (L-33); long runs with growth on are a run plan, not a design question.
- Shelves counted in documents or pages: still open; shelves are not among the built fittings.
- Wax tablets: still open; nothing needs them yet.

## History

- 22 Oct: Zach: maps, parchment, writing and information matter most of the unlocks; how do channels, laws and libraries work in
  space? 02h written. Zach on processed timber: parchment and fibre paper chosen.
- 22 Oct: Zach: private messages to anyone at the node; hear the rooms you have access to; several rooms in a day. 02h §4a; D2-7.
- 22 Oct: Zach: widespread channels should cost more; rumour first, then letters and centralised, delivered papers. 02h §4b; D2-8.
- 22 Oct: Zach: telling merchants against giving them documents; the lawyer's and historian's archives. 02h §6b.
- 22-23 Oct: 02j costed the page: the scribe's time dominates; the press is the jump.
- 5 Nov: Swept against DECISIONS, the spec and what is built (37.2): speech decided and built (C-3 closed); large worlds superseded
  by the generator; documents, channels, archives, shelves and wax tablets still open, and no writing material is built.

## Sources

[02h](../../review/37_growth/02h_information_in_space.md), [02j](../../review/37_growth/02j_end_uses.md) (writing ladder),
[02i §3-§4](../../review/37_growth/02i_buildings.md); D2-7, D2-8, D4-9; OPEN C-3, C-4.
