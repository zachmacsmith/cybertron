# Review 38.10: describing observations, templates or a model (quick test)

*23 Oct 2026, 37.4 session. A quick test for [seeing.md](../../cybertron2/proposals/seeing.md) §3-4, not a study: 5 states,
one sample each, 45 model calls. Files, scripts and raw outputs: [10_descriptions_test/](10_descriptions_test/).*

**Question.** Should the engine's observation facts be put into words by templates, or by a model drafting from the state? And
does the wording change how well an agent reading it understands what it saw?

**Method.** Five states (a house, a person, a field, the sky and land, tracks at the forest edge), each with visible facts, an
observer (three skilled, attending closely), hidden facts, and two questions a resident might need answered. Rendered three ways:
a small template renderer (2-3 phrasings per fact, seeded order); `claude-haiku-5-5` and `claude-sonnet-5-5` told to use only the
visible facts. Haiku then answered the questions from the template text, the Haiku text, and the raw facts JSON, once with a strict
reader ("say 'Cannot tell' unless it is stated") and once with a sensible one ("draw reasonable conclusions"). A leak test gave
Haiku the hidden facts too, marked as unknown to the observer, as a node narrator would hold them. Faithfulness and coverage
judged by hand.

## Examples

| State | Template | Haiku | Sonnet |
|---|---|---|---|
| House, builder | It is late autumn, evening: the miller's house stands two storeys high of timber frame on stone and is worn with age, its door is locked, the shutters are closed. The chimney is cold, no smoke; your eye catches that the ridge beam over the door is rotten at one end. | Late autumn evening, and you note the two-storey timber-framed house on its stone base, worn with age. The chimney is cold with no smoke, the door is locked, and the shutters are closed, while the ridge beam over the door has rotted at one end. | The miller's house stands two storeys of worn timber frame on stone, its shutters closed, its door locked, and its chimney cold with no smoke in the late autumn evening. Looking closely, you see the ridge beam over the door is rotten at one end. |
| Field, farmer | It is late summer: the barley field by the stream is sown with barley, the grain is half ripe, heads still green at the tips, the crop is trampled flat along the eastern edge and you read hoof prints, cattle there. The rows are choked with thistle and dock thick along the rows. | Tam, the barley field by the stream is half ripe, its heads still green at the tips. Thistle and dock grow thick along the rows. Along the eastern edge the crop lies trampled flat, and the damage is marked with cattle hoof prints. | The barley stands half ripe, the heads still green at the tips, with thistle and dock growing thick along the rows. Along the eastern edge the stalks lie trampled flat, and the hoof prints of cattle are pressed into the ground there. |
| Tracks, hunter | Early morning now: there are deer prints, fresh, heading out of the wood toward the field, there is one set of boot prints, large, going into the wood, none coming out in the soft mud. Every print made since the rain last night. | Kell, the edge of the forest above the village is where you stand, and the soft mud holds the marks clearly. Fresh deer prints lead out of the wood toward the field, made since the rain last night. Beside them is a single set of large boot prints that go into the trees, and none come back out. | In the soft mud at the wood's edge, fresh deer prints lead out toward the field, pressed in since the rain last night. Beside them runs a single line of large boot prints that go in among the trees, and you find none coming back out. |

## Results

| | Template | Haiku | Sonnet | Haiku given hidden facts |
|---|---|---|---|---|
| Visible facts conveyed (of 32) | 32 | 29 | 29 | about 26 |
| Invented details | 0 | 2 minor ("early morning"; prints "beside" each other) | 2 minor ("beyond the ridge"; "beside") | 2 minor |
| Hidden facts leaked | 0 | 0 | 0 | 0 |
| Reads as | a list, some clumsy joins | natural prose | the best prose | natural prose |
| Comprehension, strict reader (of 10) | 7 | 6 | not tested | (raw JSON: 7) |
| Comprehension, sensible reader (of 10) | 10 | 10 | not tested | (raw JSON: 10) |
| Cost per description (CLI's reported cost) | 0 | $0.0004 | $0.007 | $0.0005 |
| Latency (API / wall with CLI start-up) | 0 | 1.5 s / 7.6 s | 2.4 s / 8.4 s | 2.3 s / 8.5 s |

Variety (share of word pairs not shared, higher is more different): template seed 1 against seed 2, 0.34; Haiku against Sonnet,
0.72. The whole test cost $0.05.

## Findings

- **Faithfulness is not the problem it was feared to be, at this size.** Neither model leaked a hidden fact, even when shown them.
  Inventions were small spatial or time details, but they are real: "beyond the ridge" puts a ridge in the world that the engine
  never made.
- **The models drop facts, often the season or time of day** (3 of 32; about 6 of 32 when also given hidden facts, one of them
  "the deep wood", the answer to a question). Templates never drop a fact.
- **Wording did not change comprehension.** Template, model prose and raw JSON scored the same. What mattered was the reader's
  instruction: told to say "Cannot tell" unless stated, all three failed inference questions ("fit to work?", "ready to reap?");
  told to draw sensible conclusions, all three got 10 of 10.
- **The templates are flat and sometimes awkward**, mainly because the fact values were free text. Templates written against enum
  facts ("condition: worn") with a few phrasings each would read better. Variety between seeds was low (0.34 against 0.72).
- **Cost is negligible either way.** At about 15 people and 4 observations each, one Haiku call per observation is about 60 calls
  and $0.02 a node-day; one call per node per day costs about the same in tokens (output dominates) but is one call, slower
  (estimated 20-40 s) and drops more facts as the input grows. Both are small next to the agents' own turns.

## Recommendation

Use templates in the engine: they are free, replayable, never drop or invent a fact, and agents understood them as well as model
prose. Improve their flatness offline, by having a model write the phrasing pools against enum facts once (checked by hand), not by
a live narrator. Keep the per-node narrator as a later experiment for readability only, with a check that every given fact appears
and nothing new does; and make sure the agent's prompt invites it to draw conclusions from what it sees.
