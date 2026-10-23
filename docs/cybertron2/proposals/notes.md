# Proposal: private notes (what an agent keeps in mind)

**Status:** discussion (23 Oct). **Owner:** 37.4. **Affects:** information/perception.md, information/prompts.md,
information/letters_and_documents.md, life/birth_and_death.md.

## Summary

Each agent keeps a **small set of private notes**: what it chooses to remember, in its own words. **One note is pinned** and shown in
full every round; the others show **only their titles**, and the agent **opens** the ones it wants to read. Notes are **memory, not
objects**: nobody else can read, take, copy or inherit them; they pass to others only by telling, or by writing them down as a
document; they die with the agent. This is cybertron 1's scratchpad and files (`write_scratchpad`, `write_file`, `pin`,
`read_file`), limited and kept private.

## The proposal

| | |
|---|---|
| How many | up to **8 notes** per agent (calibrate) |
| How long | up to about **150 words** each (calibrate) |
| Pinned | **one**, shown in full in every turn prompt |
| The rest | **titles always shown** (one line each, so the agent knows what it has); **opening a note is a talk-step action**: an agent that opens notes in its plan is asked again in the talk step with them shown in full, and may change its plan (cybertron 1's look-ups in the DM step) |
| Writing | `note {title, text}` (new or replacing), `pin {title}`, `forget {title}`; free (no work units) |
| Who can read | only the agent |
| Death | lost, except what was told or written down |
| Literacy | not needed: this is memory, not writing |

**Notes against the other kinds of memory:**

| | Written by | Shown | Others can get it | Survives death |
|---|---|---|---|---|
| knowledge store (perception) | the engine, at the moment of seeing or hearing | by relevance and age | no; only by telling | no |
| **notes** | **the agent, in its own words** | the pinned one; titles; opened ones | **only by telling** | no |
| documents (02h) | the agent, with materials and literacy | when read | yes: carried, given, copied, stolen, read by others | yes, as an object |

## Why

- **Memory is short** (2 rounds in full, 8 as one-line summaries, 14 lasting memories), so an agent needs a place for what it wants
  to keep: a plan, a debt someone owes it, a price at Millford, what it thinks of a neighbour, a recipe it was taught.
- **Opening a note is useful only if it is shown at once,** so it is part of the talk step: one more call, only for agents who
  opened something (or received a message), in the same wave.
- **Keeping notes private keeps documents meaningful.** A document is valuable because it can be carried, copied, stolen and
  outlive its writer; notes cannot. Writing a note down as a document (paper, ink, literacy) is the bridge from one to the other,
  and death without having taught or written is how knowledge is lost.

## Is it too similar to documents?

Not if the line stays sharp: notes are the agent's mind (private, free, no materials, lost at death), documents are objects in the
world (made, carried, shared, kept). An agent may use notes where a person would keep a private diary; documents matter when
knowledge has to reach someone else or outlast the writer, which is where institutions, records and libraries come from.

## Alternatives considered

1. **One scratchpad, shown every round** (cybertron2 now): too small for an agent with a household, a trade and debts.
2. **Many files, all shown**: the prompt budget fills with the agent's own notes.
3. **Notes as documents** (physical from the start): every reminder would need paper and literacy, and illiterate agents would have
   no memory beyond the engine's.
4. **Opening for the next round** (no extra call): rejected by Zach: a note seen a day later is not worth opening.

## Open questions

1. How many notes and how long (8 and 150 words as a start).
2. How many notes may be opened in one talk step (attention).
3. Whether old notes fade (a memory that is never opened blurs), or stay exact.

## History

- 23 Oct: proposed (37.4, with Zach): Zach suggested a limited private directory with one pinned note and the rest read by choice,
  never passed on except by telling, and asked whether it is too similar to documents.

- 23 Oct: opening a note became a talk-step action shown at once (Zach: a note shown a day later is not worth opening).

## Sources

cybertron 1's context module (scratchpad, files, pins, read_file, recall); 38.02 (perception, memory bands); 02h §3 (documents as
objects); proposals/knowledge.md.
