# Review 38.11: M1, one node with knowledge, perception and notes, and two live runs

*23 Oct 2026, 37.4 session. Built on Zach's go ("build out just a single node and all of the relevant memory, attending, knowledge
of actions etc. testing how agents interact... do it with an llm run... then another one with the generated family trees and
ties"). Code: `cybertron2/m1/`. Specs: `cybertron2/specs/m1_founders.yaml` (run A), `m1_society.yaml` and the generated
`m1_society_s4.yaml` (run B). Runs: `runs/m1_A`, `runs/m1_B` (local, not committed). Nothing here is decided; findings feed the
proposals named in §6.*

> **Correction (23 Oct, after runs C and C0, [12_m1_shock.md](12_m1_shock.md)):** `move` with `"to": "Reed House"` (the agent's own
> house by name) was read as *take from* the house; only the word "house" stored. It happened 8 times in A and 23 in B, almost
> all Osric's. So in B the Reed elders' hunger beside Osric's bread, and "never did" give Wymarc bread, are partly this fault,
> not hoarding: his attempts to store food did nothing or took more out. Fixed; the readings of Osric below should be held loosely.

## 1. What was built

| File | What it does | From |
|---|---|---|
| `data.py` | goods, cover types (what can be gathered, worked, built, risks, what it becomes, what it gives off), 16 techniques as data, physics | layout.md, D4-24 |
| `world.py` | one node of parcels, houses, a herd, people; the calendar; today's happenings; the night (fights, regrowth, hearths, meals, cold, hazard, spoilage, breaks) | cybertron2 phase 0 |
| `knowledge.py` | four levels (aware, rough, capable, known) with sources; told, seen (3 sightings, x2 watching), explained, taught, trying; cards by level; today's options and near misses; refusals naming the shortfall; the mention rule | knowledge.md |
| `act.py` | 15 verbs: gather, make, build, work, move, give, accept, set, attack, guard, steal, watch, teach, learn, rest | verbs.md (subset) |
| `perceive.py` | facts produced from state, a sense table and happenings; dawn notice; daily notice (salience x relevance); attending one target; what concerns you; a glimpse; felt watched; sightings that teach; thefts seen or not; memory bands (2 full days, 8 one-liners, lasting); dated beliefs; notes | seeing.md, notes.md |
| `prompt.py` | system prompt (who, kin, aim, how life works incl. learning, the place by cover type, crafts, verbs, reply); turn prompt; talk prompt | seeing.md §1 |
| `run.py` | dawn (incidents, signs), decide in parallel, talk (say, tell, explain, offers, opened notes, look-ups; whoever received something is asked again; one wave), work interleaved, teaching, thefts, night, perception, memory; logs | 05_round_design |
| `generate.py` | a society with a past: a family tree simulated forward from two founding couples, kin derived from the tree, a feud, debts, friendships, an old love, hard winters, inherited crafts, each written from the person's position | D4-21, 09 §3c |
| `report.py` | per-agent and per-day summary of a run | |

Deviations from the proposals, for this slice only: `learn` is a verb (verbs.md has the learner accept a teaching offer);
descriptions are templates only (no model describer); no travel, letters, institutions or claims.

## 2. The runs

Both on the same node: Millbrook, two houses on a green, Long Field (barley ripe day 3), Brook Field (oats ripe day 6), Common
Pasture with the village cattle, Alder Wood, the Brook, Brook Meadow. Incidents and signs the same in both: geese leaving early
(day 2), the cattle in the barley (day 4), smoke beyond the north hill (day 5), an early frost (day 7), cold from day 8. Leverage:
the Reeds hold the only sickle and the reaping; the Fenns the only axe, the felling and hunting, and the pottery (no firing pit at
the start). 10 days each, `claude -p`, Opus heads, Sonnet adults and elders, Haiku youths.

| | Run A: planted founders | Run B: generated society |
|---|---|---|
| People | 6 adults and youths, written by hand | 8 acting + 1 child from a family tree of 18 people over three generations (the founders still alive as elders, one dead, eight married away to Ashby) |
| Ties | kin, a debt (Maud owes Agnes 2 grain), an old quarrel over Long Field | kin derived from the tree (Osric's sister Cecily married into the Fenns; grandparents on both sides), a feud between the heads (a pig, 11 winters ago), two debts, friendships |
| Households | 3 and 3 | Reed 3 (Osric and his elderly parents), Fenn 5 + a child |
| Cost | $3.21 (120 calls) | $4.28 (160 calls) |
| Survival | all fed at the end; 1 missed meal in 10 days | no deaths; 7 of 9 missed the last night's meal; the Fenns hungry from day 7 |

## 3. What happened

**Run A.** Agnes taught Wat to hunt on day 1 in exchange for one share of his first two kills; he kept the bargain on day 8 (gave
her 0.9 meat). Osric explained reaping to Wat, Maud and Ivy (each got a rough idea) and reaped both fields himself. Trade settled at
**2 grain a timber** and ran four times (offers, accepted in the work step). Maud's old debt of 2 grain was **paid twice**, by Osric
("Maud's two are paid besides. We're square") and by Maud the next day; Agnes thanked her and kept both. Tam built the firing pit on
day 2 and made two pots, then Agnes stopped him using timber for pots ("no pots until spring") and he spent the rest of the run
foraging; Maud, who wanted a pot, never got one. Both heads barred their doors from day 5 on. Ivy spent the run trying to learn
to fish: she watched Osric for a day believing he fished (he does not), asked everyone, looked up the card twice, and never got
past "know of it": nobody in the hamlet fishes, and a craft one only knows of cannot be tried.

**Run B.** Kinship carried the talk: "Sister, ... I'll pay you in bread", "Grandmother Letice", "Niece, you're welcome by our
fire". Wat repaid his 2-timber debt to Letice on day 1 and made sure everyone heard. Hob acknowledged his meat debt to Hamo six
times and never paid it (he never had meat). Wymarc (Haiku, a youth) pursued her aim, to learn pottage, across the whole run: dug
clay, **built a firing pit**, fired a pot, failed three times to coordinate a teaching day with her grandmother, was taught on day
6, and cooked; her notes tracked the plan ("my notes say I already know how to cook pottage"). The feud was never named; it showed
as strictness: Roger "Just don't owe Osric anything", Osric's note "Bar the door around Roger in hard times", "a fair trade isn't a
shame". Roger claimed a custom unprompted: "The gleanings come to Fenn House, as gleanings always have." Trade settled at **4 grain
for 3 timber** (1.3 grain a timber), worse for the Fenns than run A's 2, though they were the hungry side: a
distress price. It ran six times; it fed the Reeds' fire but not the Fenns: Osric sold
grain for timber while noting "Wymarc is gaunt; give her bread if we can spare it", and never did.

**A against B.** B has more mouths on the same land (9 against 6) and the same wild food, so it is hungrier; the comparison of
behaviour is confounded by that, not only by the ties. With that caveat: in B the generated ties were used (kin terms, debts
named and repaid, a youth's aim pursued through a grandparent), the feud changed tone rather than acts, and less was learned
(everyone was seeded with its line's crafts, so there was less to learn and nobody watched anybody).

## 4. What the runs say about the designs

| Design | Evidence | Reading |
|---|---|---|
| **Knowledge levels and paths** | A: Wat aware -> known in one taught day (youth); Osric aware -> rough from 3 sightings at Alder Wood, then capable at hunting by trying; three rough ideas by explanation; B: Wymarc aware -> known by one session | the paths work and agents use them by name ("watch someone, ask to be taught, or have it explained" is quoted back). One session to *known* for a youth is fast (§6 Q3). |
| **A craft nobody here knows** | Ivy: 10 days, no way forward | §6 Q1 |
| **Teaching needs both on the same day** | B: Wymarc and Letice missed three times; A: Agnes re-taught Wat a craft he already knew | coordination of `teach` + `learn` is fragile; an offer to teach that the learner accepts (verbs.md) would remove the miss |
| **The daily notice** | the cattle in the barley reached every farmer at dawn; the geese, smoke and frost reached 0-2 people each | works as designed: low-salience signs reach few. Whether the frost should be that easy to miss is a calibration question |
| **Attending** | A: parcels 25, houses 22, persons 7, sky 4; B: houses 58 of 80, mostly the agent's own | agents attend to their own store, as a guard. seeing.md made it unattendable (it is shown daily); the revealed use is security (§6 Q4) |
| **Felt watched, sightings** | "You had the feeling Wat was watching you today"; "From watching Agnes you now have a rough idea of felling timber" | work; read naturally |
| **Notes** | Opus and Haiku write and pin; Sonnet almost never (A: Maud, Tam 0; B: 5 Sonnets 0). Opened notes: 2 in 280 turns; look-ups: 7 | pinned notes carry plans and debts across days (Osric's "Winter plan", Wymarc's "Pottage"); opening the rest is unused at this size (most have 1-2 notes) |
| **The talk step** | everyone re-asked every day (say reaches all); plans changed in 40 of 60 (A) and 52 of 80 (B) re-asks | the step matters: most plans change after hearing others. It doubles the calls (§6 Q2) |
| **Offers** | A 4 trades, B 6; failures: goods in the store not in hand; the offerer used the goods before the accept ran | fixed after the runs: offered goods are set aside until taken or nightfall |
| **Refusals** | 141 of 594 results (A), 165 of 523 (B); units used 78% and 73% | mostly bad plans the engine invited: gleaning listed for unreaped fields, moves of more than carried, the same refusal 5-7 times. Fixed after the runs (§5) |
| **Work shares** | food 157 of ~190 work results (A), 182 of ~215 (B) | food dominates far beyond scenario_design's 30%: wild food here is too thin for six to nine people; the next spec must give the land more (or fewer mouths) |
| **Prompt size** | system ~6.2-6.9k chars; turn mean 4.5-7.6k, max 11.8k chars; about 7.4k input tokens a call | fine at this size |
| **Models** | Opus: deals, debts, notes; Sonnet: dutiful foraging, little talk or notes; Haiku youths: the most notes, the clearest aims pursued | consistent with earlier runs; Sonnet adults are the passive middle |

## 5. Engine faults found and fixed after the runs (not in either run)

| Fault | Fix |
|---|---|
| gleaning listed as an option on unreaped fields | glean needs a reaped field with gleanings; options and refusals say so |
| the same refusal 5-7 times in a plan | shown once, with a count; unused units are reported |
| `move` of more than is there refused | moves what there is |
| teaching someone who already has the level wasted both days | refused at settlement, with the reason |
| attending the sky gave "nothing out of the ordinary"; dawn signs gone after dawn | the day's weather is a fact; dawn signs last the day for attending and later notice |
| one's own house in "what stood out"; house events shown for the other house on the same green | own house not news and not attendable (§6 Q4); store events carry their house |
| repeated identical attended lines | merged |
| `explain` with a description instead of a craft name refused | the craft is read from the text |
| `tell` to "Reeds" refused | a household can be told |
| offers failed when the offerer used the goods first | goods set aside when offered, returned at nightfall |
| refusal "you do not know how to reaping grain" | "reaping grain is not among your crafts" |

## 6. Questions for Zach (proposals to update once answered)

1. **Experimenting from awareness** (knowledge.md). Ivy knew fishing existed, had a line and the brook, and could never try. Should
   an agent be able to *try* a craft it only knows of, at a low chance and a high cost, as a slow path of discovery (D4-24's
   "agents explore and learn it")? Or should the world always seed a source (a stranger, a manual)?
2. **Who the talk step re-asks** (05 §1). Re-asking everyone who heard a `say` means everyone, every day: two calls per agent-day.
   Options: re-ask only those named in a say, told, offered or explained to; or keep it (most plans did change).
3. **A youth taught once knows the craft** (knowledge.md §4c). One session took Wat and Wymarc from nothing to *known*. Proposal:
   a youth goes to *capable* from one session (as an adult does) and learns the rest by trying at double speed.
4. **Attending one's own house** (seeing.md §3b). Agents chose it far more than anything else once doors were barred. Proposal:
   allow it, giving who came to the house, the door, and the store's changes; it is the guard's view, not a duplicate.
5. **Teaching as an offer** (verbs.md). Replace `teach` + `learn` on the same day with an offer to teach that the learner accepts
   in the talk step, as verbs.md proposed; the runs showed the same-day match failing.
6. **The next spec** (scenario_design). More wild food or fewer mouths, so food stays under a third of the work; and a fisher or a
   way to discover fishing, so Ivy's line of play exists.

## 7. Next

Rerun A with the fixes (about $3) to check them, then a pair at a size where the generated society and the planted founders have
the same mouths per land, so ties are the only difference. The generator's faults and next steps: mortality is too low (one death in 62 years with three hard winters, so the
founders are still alive and the tree has few dead); claims and holdings from the history (D4-23); more marriages between the
lines; the elders' memory of the hard winters tied to the signs.
