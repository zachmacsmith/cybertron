# 37.2h Writing, channels, laws, libraries and maps in a world of places

*22 Oct 2026. Design for discussion; nothing built. Zach: maps, parchment, writing and information matter most of the unlocks
(02g §1d). How do the old engine's generalised channels, its laws and its libraries work when the world is a graph of places?
Information crosses nodes only by being carried (37.4 decision 9), so this note is mostly about turning knowledge into objects. The
economic side (materials, scribes, buildings, prices) is 37.2's; laws are 37.3's and messages 37.4's: §9 says what each owns.*

## 1. The principle

Knowledge crosses space in one of three ways:

| Way | Reach | Lasts | Example |
|---|---|---|---|
| **speech** | the people at your place, now | only in memory | say, tell, a moot, a market-day crowd |
| **objects** | wherever the object is carried or kept | as long as the object | a letter, a notice, a ledger, a law text, a map |
| **signals** | many nodes, fast | a moment | a beacon: one bit ("raiders!") |

Writing is what makes the second possible. **A written document is knowledge with almost no weight, a cost to make, a place, an
author and a date.** It can be carried, copied, posted, stored, stolen, lost, forged and burned. Every information institution
(the record, the law, the library, the post, the paper) is built from documents in places.

## 2. Writing materials

| Material | Made from | Cost (rough) | Good for |
|---|---|---|---|
| **wax tablets** | beeswax, a wooden frame | cheap, reusable | notes, tallies, a lesson; bulky, so local, not letters |
| **parchment** | **hides** (the herds again, 02g §2), scraped and dried | dear: a hide makes a few sheets | lasting records: laws, titles, ledgers, maps; survives travel |
| **paper** | **fibre** (flax or hemp rags), pulped at a paper mill | cheap once there is a mill; a society-scale layer (02g §5) | letters, notices, copies, editions |
| **ink** | soot or oak galls, with gum | cheap | all writing |

Zach asked about processed timber: wood-pulp paper is a 19th-century technique and timber regrows slowly. **Parchment from hides
and paper from fibre** keep writing on renewable core resources (livestock, fibre) and tie it to the herds and the flax fields. The
cost of a page decides how much a society writes down. A **paper mill** is the information economy's watermill: below its
threshold, writing is for laws and debts; above it, for letters and notices; with a press (a later era), for papers anyone can
afford.

**Literacy** is a skill learned by practice and teaching (02c §5). A school is an institution. An illiterate agent can still
hold, carry and pass on a document, but needs someone to read it aloud. Reading for others is a service, and so a lever (the old
engine's documents: confined access, review 32).

## 3. Documents as objects

A document: **text, author, written in round, at node, sealed by (02g §1d), a copy of (with the copier and round), condition**. It
sits in someone's hands, a house, a building, or on a board. Acts on it:

| Act | Needs | Costs |
|---|---|---|
| write | literacy, a sheet, ink; at least an action, more for a long text | the sheet |
| read | to hold it, or to be where it is kept and allowed in; literacy (or a reader) | an action (headlines are free, §7) |
| copy | literacy, a sheet, the original at hand (a scribe's work) | a sheet and actions per page |
| seal | your seal | nothing; proves who wrote it, so forgery becomes possible and detectable |
| give, carry, store, post | presence, as for any good | nothing extra |

Copies carry their provenance. The old engine already does this (`documents.py`: author, sender, round, a hash and "altered" when
the text changes); here a copy is also a physical object at a place.

## 4. Channels, re-imagined in space

The old engine's channel v2 is an owned, append-only log with reader and writer selectors, delivery (push, pull, edition),
retention, a directory listing and an inbox. Every part has a spatial form:

| Old channel feature | In a world of places |
|---|---|
| the square (everyone reads) | **a gathering**: everyone at a node at a time (the moot, market day, a feast). Speech heard by those present |
| a board (pull, listed) | **a notice board at a site in a node**: posts are documents nailed up; whoever is there reads them; space on the board and the weather limit retention |
| a private message | **a letter**: a document carried by whoever the sender can persuade or pay (a merchant, a courier, a traveller, a child), arriving when they do, if they do |
| an inbox | **a box at a house or office**: letters delivered there, read by whoever may open it (keys, 02g §1d) |
| a paper, editions, subscriptions | **copies carried on a schedule**: a scribe or a press makes copies; the post or merchants deliver them to subscribers' nodes; each copy costs a sheet |
| readers and writers by selector | **presence plus permission plus literacy**: you read what is where you are, if you may enter the room, and if you can read |
| delivery push, pull, edition | heard if present; read if you go there; delivered with the carrier |
| a listed address | **knowing where**: a board's or library's location is knowledge like any other |
| retention | the board's space and weather; an archive keeps everything (until it burns) |
| rate limits | the cost of sheets, and of a carrier's time |

**The old channel record is still the right data structure.** It gains a medium (speech, board, letters, edition) and a location
(a node and site, or "carried"). The selectors' closed vocabulary gains `{"present": node}`; it had `{"camp": ...}`, presence at a
camp, already.

## 5. Laws in space (37.3's to decide)

Today a law is code the engine enforces everywhere at once, and everyone can read it. In a world of places, four questions:

1. **Where is it made?** At a seat: a council house at a node. Voting needs presence, or ballots and proxies carried in. Distance
   from the seat is political weakness: the outer villages vote late or not at all.
2. **What is the law, physically?** A text: the original in the archive at the seat, signed and sealed; copies carried out.
3. **When does it bind, and where?** Proposal: the engine applies its automatic effects within the jurisdiction's nodes from
   enactment (37.3's `reach`). Personal enforcement (fines, arrests, seizures) needs an officer present.
4. **Who knows it?** Only those who read it, heard it proclaimed, or were told. **The prompt lists only the laws an agent knows**
   (02_perception: beliefs with a source and an age). A herald or a posted copy at each node is how a law becomes known. Ignorance
   is real, and so is the power of whoever controls proclamation.

## 6. Libraries, archives and maps

**A library or archive is a building that holds documents** (the old engine's directories, given a place):

- **What it holds:** the law texts, the registers (land titles, debts, marriages, the census), letters kept, chronicles, maps.
- **Who reads:** whoever its keeper lets in (keys, 02g §1d), if they can read.
- **Copying** is scribes' work, so a library's influence spreads only as fast as copies are made and carried.
- **It persists across generations** (the old engine's namespace-scoped directories). It is the society's memory, and a fire (a
  raid on buildings, 02g §5b) can erase it.

**A map is a document that freezes its maker's knowledge** of places, edges, resources and dangers as of a date: the maker's
knowledge store (02_perception), written down.

- **Reading a map** writes dated beliefs into the reader's store ("as mapped by Hale in round 30").
- **Maps can be out of date, wrong or forged.** A map of the frontier (37.5) is a valuable good: sold, copied, stolen, kept secret.
- **Mapmaking needs travel and writing,** so explorers who can write, or a scribe who goes with them, are worth paying.

## 7. What agents see (prompt)

At their place:

- **The board's headlines,** free: "the market cross: a law of the Council of Millford (round 12), Hale's prices (round 14), a reward
  for news of Bram".
- **Reading a document in full** is an action, or a look-up (the old engine's free look-ups, ported).
- **The documents they hold,** by title.
- **The laws they know,** with where and when they learned of them.

Nothing about a document elsewhere, except what they remember of it.

## 8. Large worlds with small settlements (Zach's question)

**Recommendation: yes. A large map with a few small settled cores and unsettled land between and beyond.** Space makes this cheap:
an agent's prompt grows with its neighbourhood, not the map (02_perception principle 7), so empty nodes cost almost nothing.

**What makes expansion happen.** Without pressure, agents will not expand, as run 2's comfortable households showed. Three things
need to be on:

- **growth** (37.1: births, so more mouths and hands);
- **depletion** (37.4: soil, woods and game running down near home);
- **a reason beyond:** a rare resource, better land or a free valley, known by rumour or a map (37.5).

**What to measure:** settlements founded over time and their distance from the old cores; land in use; how far each institution's
law, knowledge and coin reach (who at the edge knows the latest law, and how old their news is); the frontier's information lag.

**A first configuration:** 15-20 nodes; 2-3 settled hamlets of 8-12 people each (20-30 agents); unsettled land of varied kinds (a
river valley, hills with ore, grassland with wild horses); 60-100 rounds; growth and depletion on. Cost at about $0.02 an agent-round
(run 2): roughly $25-60 a run.

**Caution:** expansion takes many rounds and a reason. A 20-round run will show no expansion whatever the map. Run the economy at a
small scale first (02f E1-E3), then grow the map.

## 9. Who owns what, and open decisions

| Part | Owner |
|---|---|
| writing materials, scribes, paper mills, libraries as buildings, the price of a page | 37.2 |
| channels in space, letters and their carriage, boards, signals | 37.4 (carried messages, decision 9) |
| laws' seat, reach, proclamation and enforcement | 37.3 |
| maps of the frontier, expeditions | 37.5 (no session yet) |
| the map and its size for runs | 37.4, with Zach |

**Decisions:**

1. **Parchment from hides and paper from fibre** (rather than timber), with ink and wax tablets?
2. **Documents as physical objects**, carried, copied, sealed and burned, as in §3?
3. **Channels as media in places** (§4): gatherings, boards, letters, carried editions, all on the old channel record?
4. **Laws known only by those who learned of them**, and enforced in person outside the engine's automatic effects (§5): for 37.3
   and Zach?
5. **Large worlds with small settled cores** (§8), after the small-scale economy works?
