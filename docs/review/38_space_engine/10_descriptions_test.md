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

## Run 2: richer facts, seen through the observer's eyes

**What changed.** Each state got the sensory and ambient facts an engine could derive by simple rules (sounds, smells, light,
weather, signs of recent use, who else is about): 11-15 visible facts each, 64 in all. The observer was given properly: name,
stage of life, trade and skill, state, what they care about, and how they stand to the target (a neighbour who paid late, a
brother, their own field, their own hunting ground). The prompt asked for what this person would notice, in 1-3 sentences, with a
hard rule that every clause must rest on a given fact. Compared with a template over the same facts, grouped by sense. 30 calls,
$0.18 ([render2.py](10_descriptions_test/render2.py), [raw_outputs2.json](10_descriptions_test/raw_outputs2.json),
[scores2.json](10_descriptions_test/scores2.json)).

| State | Template, run 2 | Haiku, run 2 | Sonnet, run 2 |
|---|---|---|---|
| House, Brenna the builder, tired, wants winter work, he paid late before | It is late autumn, evening: the miller's house stands two storeys high built of timber frame on stone and is worn with age, there are old grey chips round the chopping block, no fresh ones, your eye catches that the ridge beam over the door is rotten at one end, its door is locked. The shutters are closed, the chimney is cold, no smoke, dead leaves drifted against the doorstep, undisturbed. You hear no sound from inside, ... (4 sentences, 108 words) | Two storeys of worn timber frame on stone sit in low evening sun on the west wall, and the lane's woodsmoke stops at this house. The ridge beam over the door is rotten at one end, the chimney is cold, the shutters are closed, and the door is locked, with dead leaves undisturbed against the doorstep and only old grey chips round the chopping block. No sound comes from inside, and nobody else is in the lane. | Your eye goes straight to the ridge beam over the door, rotten at one end, on a worn two-storey house of timber frame on stone, and you know that's work for someone before the winter. The chimney is cold, the shutters closed, the door locked, and there's no sound from inside. ... and you stand there tired from the roofing, remembering he paid you late last time. |
| Gil, seen by his sister Ash, hungry herself, worried the house will not eat | Midday: Gil looks hungry, thin in the face, he has mud to the knee, you see him walking slowly, favouring the arm, he is bent under a load of split timber on his back. ... (92 words) | Gil comes out of the deep wood alone at midday, thin in the face and breathing hard under a load of freshly split pine. Your eye goes to the rag bound on his left forearm, still seeping, and to the mud on his legs as he favours that arm and walks slowly past you. He smells of sweat and fresh-cut pine, and resin shows on his hands. | Gil comes past thin in the face and breathing hard, a load of fresh-cut split pine on his back, and you see he's walking slowly, favouring the left arm, where the rag round his cut is still seeping. He's alone, mud to the knee from the deep wood, resin on his hands and the smell of sweat and pine on him, and you can't help wondering whether he's fit enough to bring in more, with the house still hungry. |
| Tracks, Kell the hunter, hungry, his own ground | Early morning: there are deer prints, fresh, heading out of the wood toward the field, every print made since the rain last night, you see fresh deer droppings by the field gate, there is one set of boot prints, large, going into the wood, none coming out in the soft mud. ... (105 words) | Fresh deer prints, made since the rain last night, run out of the wood toward the field, and fresh droppings lie by the gate, so the deer have only just passed. But one large set of boots went into the trees, none came back out, and a hazel twig lies snapped at head height where they entered, in your ground. | The deer prints are fresh in the soft mud, made since last night's rain and heading out of the wood toward the field, and there are fresh droppings by the gate. But one set of big boot prints goes in past a hazel twig snapped at head height, and none come back out of your wood. Nobody is in sight, the village below is quiet, and all you hear is water dripping from the branches and a woodpecker drumming deeper in. |

| | Template 2 | Haiku 2 | Sonnet 2 | (Run 1: Haiku / Sonnet) |
|---|---|---|---|---|
| Visible facts conveyed | 64 of 64 | 53 of 64 (83%) | 54 of 64 (84%) | 29 / 29 of 32 |
| Clauses with no supporting fact | 0 | 0 | 0 | 2 minor / 2 minor |
| Small stretches (facts joined into a cause, "all you hear") | 0 | 1 | 3 | |
| Hidden facts leaked | 0 | 0 | 1 borderline | 0 / 0 |
| Takes the observer's view | no | slightly | clearly | no / no |
| Comprehension, sensible reader (of 10) | (run 1: 10) | 10 | 10 | 10 / not tested |
| Words per description | 86-108 | 60-89 | 79-113 | 43-58 / 37-46 |
| Cost / model time per description | 0 | $0.0008 / 4.6 s | $0.011 / 4.3 s | $0.0004 / $0.007 |

**Findings.**
- **The clause rule worked.** Neither model wrote a clause without a supporting fact (the checker agreed); run 1's "beyond the
  ridge" kind of invention did not recur. What remains are small joins: "mud to the knee from the deep wood" makes a cause of two
  facts; "all you hear is" claims there was no other sound.
- **One borderline leak, from the observer's view itself.** Sonnet's almanac keeper "knows what that means before she lets herself
  say it" on seeing the early geese, which hints at the hidden hard winter. It is also a fair belief for her to hold, so a
  check cannot tell the two apart without knowing which beliefs the observer may form.
- **Sonnet clearly takes the observer's eye; Haiku barely does.** Sonnet's builder goes straight to the rotten beam, sees winter work
  and remembers being paid late; the farmer's field is "your barley"; the sister thinks of "the house still hungry". Haiku writes
  the same facts in good prose with "your eye goes to" added.
- **Both drop facts, sensibly.** Drops were mostly season, time, light and weather. Haiku's hunter kept only the 5 track facts of
  11, the ones he cares about. Haiku's sister lost "hungry", which bears on her concern. Sonnet ran to 4 sentences twice.
- **The template with all the senses is long and reads as a list** (86-108 words), though grouping by sense helps. Every reader
  still answered every question.

**Is the observer's-eye prompt clearly better?** With Sonnet, yes for reading: it is the only version that sounds like a person
with a stake in what they see, and it invented nothing. With Haiku, only a little. It does not help comprehension, which was
already full, and it costs Sonnet prices (about $0.01 a description, 15 times Haiku). The run-1 recommendation stands for the
engine: templates for the facts. The observer's eye, if wanted, belongs in a Sonnet narrator, tested on longer runs against an
agent's choices, with a check that knows which beliefs an observer may form.
