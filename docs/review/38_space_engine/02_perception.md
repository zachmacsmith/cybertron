# Review 38.02: what an agent should see

*22 Oct 2026. Design for discussion; nothing built. What `cybertron2` agents perceive, remember and are told, and how that changes
round to round. Evidence from the first run: [01_forest_run.md](01_forest_run.md).*

## 1. The problem

The phase-0 prompt (01_forest_run, and the round-16 example Zach asked about) is mostly local, but it is a dashboard, not a point of
view:

- **It leaks:** an agent sees its house's exact stock from the Deep Wood, where every household member is, and every death.
- **It hides what people present would notice:** Dara starved beside her party-mates, who could not see she was starving; nobody
  sees what anyone else did, even at their own place.
- **It has no time in it:** nothing says how old a piece of knowledge is, or what changed since the agent last looked.

Every behaviour we study comes through this text. Who knows what, since when and from whom is the raw material of trust, rumour,
leverage, charity, theft and enforcement. So perception should be a designed system, not a by-product of the state view.

## 2. Principles

1. **You perceive where you are.** The place, the people present and their visible condition, the buildings there, and what is done
   there while you are there.
2. **You know your own body exactly.** Hunger, what you carry, how many nights without a meal.
3. **Everything else is a belief with a source and an age.** "As you saw it in round 14", "Hal told you in round 15". Beliefs go
   stale while the world moves on: the engine never refreshes them silently.
4. **Count what you can count; estimate what you can only see.** Exact numbers for your own goods and for a stock you stand in
   front of and look into. Words for things you can only judge: the forest ("thin"), another person's load ("carrying a lot of
   meat"), another person's condition ("looks starving").
5. **Change is shown, not left to be inferred.** What is different from when you last saw it comes first, because that is what an
   agent acts on: "The Near Wood is thinner than when you were last here."
6. **Talk is testimony, not truth.** What people say is recorded as said, by whom, where and when. It can be wrong or false (01 §2.6:
   announced gifts that never happened).
7. **The prompt grows with the neighbourhood, not the world.** Perception is local and memory is summarised, so a 500-agent world
   costs each agent about what a 20-agent one does.

## 3. The knowledge model (engine side)

Each agent keeps a store of what it has observed, written by the engine at the moments it observes, never by the model:

| Kind | Entry | Written when |
|---|---|---|
| places | per place: plants, game and trees (as words), people seen there, round seen | the agent is there at any step of a round |
| houses | per house: condition; stock (exact for its own house when inside; words for others'); round seen | the agent is at the house's place |
| people | per person: where seen, condition seen, load seen, round seen | the agent and the person are at one place at a step |
| witnessed | acts done at the agent's place while it was there (who foraged, felled, took from a store, gave to whom, hunted with whom, who carried what home) | each action step |
| testimony | each say or tell heard: speaker, place, round, text | the round's speech delivery |
| deaths | a death seen (present) or told | when seen or heard |

The model's own notes stay as they are: its interpretations and plans. The engine's store holds only observations.

**Witnessing in the interleaved round.** Actions run one step at a time across agents (01 §1), so an agent sees an act if it was at
the same place at that step. Walking through the Near Wood on the way home, you see who is foraging there.

## 4. The prompt, section by section

| Section | What it holds | Source |
|---|---|---|
| **Now** | round, season and its signs ("snow on the ground"), actions available | perception |
| **Here** | the place and its signs; the people here, each with visible condition and load; the buildings here and their visible state | perception |
| **Seen here last round** | acts witnessed at the places you were (one line each, summed: "Gil felled twice; Fay took 3 food from Wynn House") | witnessed |
| **You** | hunger, nights without a meal, what you carry; your house: exact if you are there, else "as you left it in round 14: ..." | body; memory |
| **Changed since you last saw it** | differences between this observation and the last of the same thing ("Wynn House's stock is 4 lower than when you left") | memory diff |
| **Elsewhere, as you last knew it** | each other place, each person you care about (household first), each house: the last observation and its age; omitted after N rounds unless asked for | memory |
| **Heard** | last round's say and tell lines, with place | testimony |
| **What your actions did** | results and the night (meal, catch, fire, breaks) | results |
| **Your notes** | as now | the model |

Visible condition is one word from the hunger stage and shelter ("well", "hungry", "starving", "cold"); visible load is a coarse word
for what a person carries ("empty-handed", "a little food", "a lot of meat", "an armful of timber").

## 5. What it would have changed in the first run

**Dara, round 5, in the Deep Wood (phase 0, exactly as she saw it):**

```
You are at the Deep Wood ("deep_wood"): plants plentiful, game plentiful. With you: Bram, Fay, Gil.
You carry 0 food and 0 timber. You are hungry (1 night without a meal).
Alder House (in the Clearing): sound; 4 living in it, 5 beds; stock 19.7 food, 27 timber.
Your household: Bram at the Deep Wood; Cela at the Clearing; Eoin at the Clearing.
```

**As proposed:**

```
Here: the Deep Wood. Plants plentiful; game plentiful, fewer tracks than two rounds ago.
With you: Bram (well; a little food), Fay (well; a little food), Gil (well; a little food).
Seen here last round: Fay and Gil hunted as "wynn" and each caught small game; Bram and you hunted as "big": Bram caught small
game, you caught nothing.
You: hungry, 1 night without a meal, carrying nothing. Out here you need 1.5 food tonight; you have none.
Your house, as you left it in round 4: sound, about 20 food, 27 timber.
Your household, as you last knew: Cela and Eoin at the Clearing (round 4).
```

And Bram, Fay and Gil, standing next to her, would each have read "Dara (hungry; empty-handed)", and "starving" the round after. In
the run, nobody present could see it, and three rounds later she was dead.

| Run failure (01 §2, §4) | Perception that addresses it |
|---|---|
| Dara starved beside party-mates | visible condition of people present |
| party names crossed for three rounds | "seen here last round": who hunted under which name, so agents converge on the party that exists |
| gifts announced to someone not present | "Elsewhere": Wynn last seen at the Clearing in round 17, now not here; a give to an absent person is visibly impossible before it is tried |
| the game hunted out with no warning | trend words ("fewer tracks than two rounds ago") instead of a static level |
| a remote exact house stock | "as you left it in round 3" |

## 6. How it changes over a run

- **Staleness is the main dynamic.** A household split between a hunt and home sees each other's state only through what returners
  report. Coming home is when you learn what the stock really is. That makes carrying news a reason to walk, and being away a risk.
- **Witnessing makes norms possible.** A shared store is a commons only if taking from it can be seen. Seen takings let people
  complain, ration and punish; unseen ones let them free-ride. Phase 1's institutions (a shared store, a hunting rule) need this.
- **Testimony makes reputation and deception possible.** A claimed gift can be checked against what was witnessed.
- **Old knowledge fades from the prompt.** After about 5 rounds an observation drops out of "Elsewhere" unless the agent's notes keep
  it. The engine still holds it, and a `recall` look-up can bring it back.

## 7. Options and open questions

1. **Can anything be done unseen?** Proposal: no, in phase 1 (every physical act is witnessed by those present). Later, a covert
   option (by night, at a cost) for theft and secret deals.
2. **Other households' stocks.** Proposal: words when you are at their place ("Wynn House looks poorly stocked"), never numbers.
   Envy and leverage need it to be visible; numbers would make it a ledger.
3. **The map.** Proposal: residents know their land (all places and paths); in larger worlds, places beyond the agent's range are
   known only if visited or described (37.5's frontier).
4. **In-round talk** (asked earlier): a talk step among people at one place before they act. Perception and talk interact: with a
   talk step, "who is here" at the start of the round matters more, because that is who you can plan with.
5. **Budget.** Estimate: 400-700 tokens a turn for this world, against about 450 now. The "Elsewhere" section is the one to cap.

## 8. Build order

1. The knowledge store, written at each step and at the night.
2. The prompt sections of §4, replacing the leaks of §1.
3. Witnessing and visible condition and load.
4. Rerun the forest (same seed) with the fixes from 01 §4. Compare what agents did with what they could see, round by round.

## 9. As built (22 Oct, `cybertron2/perceive.py`, `prompt.py`, `run.py`)

- **Knowledge store** per agent (perceive.py): places, people and the agent's own house as last seen, with the round; the previous
  sight of each kept for "changed since"; witnessed acts; testimony; a summary band (one line a round, 8 rounds), a full band (the
  last 2 rounds: what it did, saw and heard), and lasting memories (deaths, fights, what was done to it, the cold; at most 14).
- **Witnessing:** every action returns what others see; everyone else at the place at that step sees it; a departure is seen by
  those left behind and an arrival by those at the destination; night fights and deaths by everyone at the place at night.
- **Visible condition and load:** "Brenna (starving; empty-handed)", "Torvald (hungry; timber)".
- **Beliefs with ages:** your house exact only when you are there, otherwise "as you last saw it N rounds ago"; people and places
  as last seen, dropped from the prompt after 6 rounds; other households' stocks only in words, only when you are at their house.
- **From the old context module:** the memory gradient (full band, summary band, lasting memories: review 20's history mode,
  simplified), and a field in the reply that says why the agent chose its actions. Not ported yet: token budgets with
  deterministic trimming (sections are capped by line counts instead), look-ups and `recall`.
- **The field is called `why`, not `reasoning`.** With the hills-and-forest system prompt, a required `reasoning` field described
  as "your thinking" was refused by the Sonnet 5.5 safeguard every time (3 of 3 calls for Cela's prompt; 3 of 4 Sonnet agents in
  the first live round). Either part alone passed; renaming it "why you chose these actions, in a few sentences" passed for all
  three. The 5.5 models through `claude -p` return no thinking text, so this field is the only view of their intentions.
