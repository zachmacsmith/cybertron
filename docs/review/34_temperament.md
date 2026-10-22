# Review 34: temperament and values, a redesign brief

*22 Oct 2026. A brief for an agent to build from; section 8 says what was built. Read docs/threads.md ("Temperament and values
redesign") for the discussion that led here, and docs/review/33_positions.md for the positions system being built in parallel
on `wp/positions` (see section 7 on how the two fit together).*

## 1. What exists

- **Traits** (`cybertron/personality.py`): 7 independent Beta(2, 2) draws on 0..1: risk, trust, honesty, assertiveness, patience,
  reciprocity, talkativeness. Each is bucketed low (< 0.35), mid, high (> 0.65), each bucket has one fixed sentence, and the 4 most
  extreme traits (distance from 0.5) are rendered into the system prompt; the other 3 are not shown. Goalless worlds use reworded
  sentences without payoffs (generator.py, personality section; `personality.none`, `personality.explicit`).
- **Archetypes** (`cybertron/archetypes.py`): an independent draw (default prob 0.5) of one of 8 (secretive, chaotic, zealot,
  opportunist, loyalist, contrarian, paranoid, gossip; aggressor, protector, nurturer by weight), one stronger sentence placed first.
  Drawn independently of the traits, so they can contradict ("contrarian" with "You tend to follow others' proposals").
- **Elsewhere:** children inherit a blend of parents' traits (`pairs.py`); traits are exported (agents table `personality_*`).
  No game mechanic reads them.

## 2. What the published runs show (36 runs, 790 agents; scripts in 34_temperament_scripts/)

Behaviour z-scored within run x model; Spearman r against the trait. A trait drawn but not among the 4 shown is a natural control
(same score, never seen by the agent).

| Trait -> behaviour | r when shown | r when not shown |
|---|---|---|
| talkativeness -> DM length | **+0.69** (385) | +0.03 |
| talkativeness -> post length | **+0.58** (242) | +0.09 |
| talkativeness -> reasoning length | +0.28 | +0.01 |
| talkativeness -> DMs per turn | +0.22 | +0.01 (capped by DM limits) |
| assertiveness -> proposals | +0.24 | -0.10 |
| risk -> attacks | +0.28 (58, weak) | -0.10 |
| trust -> gifts | +0.02 | -0.04 |

DM length by shown talkativeness roughly doubles low -> high for every model (Haiku 134 -> 272 chars, Sonnet 79 -> 217,
Opus 147 -> 347).

Conditioned behaviour and promises (where a disposition should matter):
- Vote promises naming a ballot, checked against the vote: kept 88% (258); no honesty effect (high 84%, low 95%, not shown 88%).
- Payment promises: regex extraction is not valid (most matches are trade terms, information offers or policies); 50 explicit ones,
  too few. Needs a text judge.
- Gift returned within 3 rounds, by recipient reciprocity or trust: 23-34% at every level. Retaliation after being attacked: 2 of
  112 targets at every level. Giving first, by trust: 74-78% at every level.
- Reasoning that discusses deceiving: under 1% of turns at every honesty level. Only the risk sentence is echoed in reasoning
  (8.4% of turns when shown vs 0.7%).
- Archetypes (mean z vs none; n 25-90, about +-0.2 is noise): secretive posts less (-0.55); chaotic messages, posts and varies
  actions more; zealot and loyalist narrow their actions (-0.41); opportunist proposes more (+0.46), gives less; paranoid
  withdraws; loyalist writes more and longer DMs; gossip goes the wrong way (fewer, shorter DMs).

**Conclusion:** text that names a concrete, frequent behaviour works (talk length and volume, proposing); dispositions without an
obvious action (trust, reciprocity, honesty, retaliation) do not move behaviour; the models' own defaults win (cooperative, keep
votes, do not retaliate). Interviews in the Directorate run also suggest all Haiku share the same default values (18 of 19 said
privately they were not loyal).

Caveats: observational (but traits are randomly assigned, and the shown/not-shown contrast is clean); many comparisons; "gifts"
include trade payments; retaliation needs conflict on and arms; Opus/Sonnet logged reasoning is the stated summary.

## 3. Design: three layers, sampled jointly

1. **Temperament (biological, stable): HEXACO at facet level.** Draw the 6 factors (Honesty-Humility, Emotionality, eXtraversion,
   Agreeableness, Conscientiousness, Openness) from a multivariate normal with the published inter-factor correlations; each facet
   = loading x factor + unique noise (a Gaussian copula, mapped to 0..1). Take loadings and correlations from the HEXACO-PI-R norms
   (Lee and Ashton); do not invent them. Keep about 15 game-relevant facets of the 25: Sincerity, Fairness, Greed Avoidance,
   Modesty; Fearfulness, Anxiety; Social Boldness, Sociability; Forgiveness, Flexibility; Diligence, Prudence; Inquisitiveness,
   Unconventionality; Altruism (interstitial).
2. **Strategic preferences:** risk, time preference (patience as waiting for a payoff, not the anger facet), trust, reciprocity.
   Partly derived from temperament (Fearfulness and Prudence push risk aversion; Honesty-Humility pushes trust and fairness) plus
   their own noise.
3. **Values:** Schwartz's 10 (power, achievement, hedonism, stimulation, self-direction, universalism, benevolence, tradition,
   conformity, security) or Moral Foundations (care, fairness, loyalty, authority, purity, liberty). The circumplex is the joint
   distribution: neighbours correlate, opposites anti-correlate. Values are the lever for loyalty, compliance and dissent in the
   regime worlds (conformity and security vs self-direction and universalism).

**Archetypes become named regions** of this space (zealot: one dominant value, low Flexibility; paranoid: high Anxiety, low
Forgiveness, low trust; gossip: high Sociability, low Sincerity...). An archetype can be sampled (a mixture component) or assigned,
and its sentence is consistent with the traits by construction.

**Rendering:**
- Every sentence names a concrete behaviour in this world, not an adjective (section 2: adjectives and dispositions do nothing).
  Fairness: "You refuse gifts from people whose cases you decide", not "You are fair". Forgiveness (low): "When someone breaks a deal
  with you, you make them pay for it before you deal with them again." Where a behaviour depends on a situation, say the situation.
- 5 levels instead of 3; show the 4-6 most extreme dimensions across the three layers within a fixed sentence budget; values get at
  most 1-2 sentences.
- Consider worked examples for the dispositions that did nothing (one short "for example, ..." clause), and test whether they help.
- Goalless worlds keep goal-free wording, as today.

## 4. Spec and compatibility

- Opt-in: e.g. `personality: {model: hexaco}` (default `legacy`, today's exact behaviour and text; old runs and goldens unchanged).
- Keep `personality.explicit` (now able to fix factors, facets, values or an archetype per agent) so scenarios and sweeps can set
  profiles directly; add `personality.dist` overrides (means and spreads per factor) so a world can shift its population (a
  conformist society, a fearful one).
- Each drawn profile is recorded in instance.json and exported (new columns or a JSON column in the agents table); children inherit
  (pairs.py) per factor and value with noise.
- Seeded stream of its own (as archetypes do), so turning it on does not move any other draw.

## 5. Validation (before adopting it as a default)

1. **Free, from data:** rerun section 2 on new runs with the new model (scripts here; extend them with the conditioned measures).
2. **Controlled pilot (model usage, small):** one seat in a fixed situation (e.g. a guard ordered to serve a dubious warrant; an
   official offered a bribe; a worker offered a loan; an agent wronged by a partner), run with profiles varied one dimension at a
   time, n samples each (the interview tool's `--n`, or short forks of a run). Measure the decision, not the text.
3. **Text judge for honesty and reciprocity (model usage):** rate messages against private reasoning for misleading claims, and
   promises against later actions.
4. Adopt a facet or value sentence only where it moves behaviour; drop or rewrite the rest.

## 6. Build plan

1. `cybertron/temperament.py` (new): factors, facets, preferences, values, archetype regions, sampler, renderer; norms tables in one
   place with their source.
2. Hook into generator.py's personality section behind `personality.model` (small edit), and into the prompt where the temperament
   text is placed (small edit).
3. Export columns; pairs.py inheritance; schema keys and docs.
4. Tests: legacy byte-identical; sampler reproduces the target correlations within tolerance over many draws; rendering budget;
   explicit profiles; goalless wording; inheritance.
5. A pilot spec (section 5.2) and a write-up section 7 "As built" here.

## 7. Fit with positions (`wp/positions`, in progress)

Positions say what an agent is responsible for (identity, duties, rights); temperament and values say how it tends to act and what
it cares about; goals say what it wants. Keep the three apart in the prompt (identity line, then temperament, then goal), so a run
can vary one at a time. The positions agent edits context.py, agents.py and generator.py (class and identity text): keep this
work's edits to those files minimal (a hook each) and put the substance in the new module, to keep merges easy. Coordinate the
prompt section order with `wp/positions` before merging.

## 8. As built (22 Oct 2026)

Built on `claude/charming-wozniak-4iqwdk` (on `subsistence`), opt-in; `personality.model: legacy` (the default) is unchanged:
the legacy draws still happen, so no other draw of a world moves, and the golden runs' events and prompts are identical.

**Not done: the norms.** The published tables (HEXACO-PI-R inter-factor correlations and facet loadings, the Schwartz value
intercorrelations, factor-value and facet-preference correlations) could not be read from the build environment (its network
policy refused hexaco.org, PMC, OSF, ResearchGate and the publishers), and section 3 forbids made-up numbers. `NORMS` in
cybertron/temperament.py lists each table with the source to take it from and stays empty; `personality.temperament.norms:
published` (the default) refuses to draw until `factor_corr`, `facet_r` and `value_corr` are filled (factor-value and
facet-preference correlations may stay empty: 0). `norms: uncorrelated` draws every dimension independently, with no
coefficients at all: usable for the pilot, which varies one dimension at a time, and for tests. Filling the tables needs no code
change; the sampler is tested against a synthetic fixture (tests/test_temperament.py) and reproduces its correlations within 0.04.

**cybertron/temperament.py** (the substance; small hooks elsewhere):
- Model: the 6 factors and the 10 Schwartz values are one latent multivariate normal (factor block, value block, factor-value
  block; the off-diagonals shrunk in steps of 0.02 only if the joint matrix is not positive definite, recorded as `Model.shrunk`).
  A facet = its weights x the factors + unique noise, the weights solved from the facet's correlations with its domain(s)
  (one for most, H/E/A for Altruism); a preference = weights x the facets or factors named in `pref_r` + its own noise. A
  dimension's score is its normal CDF: a percentile of the reference population. Levels are that population's quintiles.
- Values: Schwartz's 10 (not Moral Foundations: the regime worlds' lever is conformity and security against self-direction and
  universalism, section 3; Moral Foundations would be a second table and renderer).
- Archetypes: all 11 of archetypes.py are regions (`REGIONS`: conditions on percentiles, a behavioural sentence each), so the
  sentence never contradicts the traits. `personality.temperament.archetypes: natural` (the default) names an agent's archetype
  only when its freely drawn profile lies in a region (the deepest, if several), so the population stays the norms'; `drawn`
  draws one first as before (`personality.archetypes`: prob, weights; two draws per agent) and conditions the profile into it by
  rejection sampling (clamping after 5,000 tries; a child's inherited profile is clamped, never redrawn). With the base spec's
  prob 0.5, `drawn` pushes half the population into the regions' corners, away from the norms: use it for archetype sweeps, not
  as a population model. Assigned archetypes (`archetypes.explicit`, or `archetype` in `personality.explicit.<id>`) condition in
  either mode; enabled, weights (> 0), exclude and gating say which archetypes a world names in both. Under natural a child is
  named by its own profile. An explicit dimension that contradicts an explicit archetype is an error.
- Rendering: 4 sentences per dimension (very low, low, high, very high; the middle quintile says nothing), each a concrete
  behaviour in the world, none naming a goal, payoff or score (so goalless worlds need no rewording; tested). The archetype's
  sentence first (the dimensions it is defined by are not repeated), then the most extreme dimensions across the three layers,
  `budget` sentences in all (5), values at most `values_max` (2). `examples: true` appends a worked example to sincerity,
  fairness, forgiveness, trust and reciprocity at the extremes (section 3's open question; off by default, to be tested).
- Streams: `temperament:<seed>:<agent>` per agent (generation and arrivals), `temperament:<seed>:child:<key>` per birth.
- Spec (schema.EXTRA, frozen per run): `personality.model` legacy|hexaco; `personality.temperament`: norms, archetypes, budget, values_max,
  examples, shift and spread (per dimension: mean shift in SD units, SD multiplier; a facet's or preference's of its own noise),
  inherit_sd (0.3). `personality.explicit.<id>` takes any dimension (percentile 0..1; factors and values set the latent before
  facets and preferences are derived) and `archetype`.
- Records: `inst.agents[*].temperament` (percentiles by layer, archetype, conditioning, regions, explicit dimensions, the
  dimensions shown, the latent); `personality` is {} and `archetype_text` "" under hexaco (the archetype's sentence is in
  `personality_text`). Export: `agents.temperament_json` (schema 2.8).
- Inheritance: pairs.py (both parents) and life.py (the Maker's parent) blend every latent component, u x a + (1 - u) x b, plus
  Normal(0, inherit_sd) (0 with `life.mutation.enabled: false`); the child's archetype (inherited or mutated as before) conditions it.

Hooks: generator.py (after the legacy draws and archetypes.assign), events.draw_agent (arrivals and children), pairs._mix and
life.py's birth (the inherited profile), schema.py (keys, docs, explicit check), export.py (the column), interventions.py
(`set_temperament`, below). context.py, agents.py and the prompt order are untouched: the text sits where "Your temperament:"
always has, so section 7's order (identity, temperament, goal) is for the positions merge to settle.

**Pilot (section 5.2).** `cybertron/specs/temperament_pilot.yaml` (village7, 8 rounds, all weak models, hexaco with uncorrelated
norms) is the base run. The intervention `set_temperament {agent, profile}` sets some of a seat's dimensions (and archetype)
from a round on, keeping the rest of its latent, and rebuilds its system prompt; `34_temperament_scripts/pilot.py` writes one
schedule per arm (each listed dimension at each listed percentile, plus a control; every arm drops the seat's archetype unless
`--keep-archetype`) and prints the fork commands (`cybertron fork RUN --at N --apply ARM.yaml --replicates K`). Checked end to end
on a dry run; not run with models (model usage). Interviews cannot do this (they rebuild the recorded context, so a profile cannot
vary). The fixed situations of section 5.2 (a bribe, a dubious warrant, a loan, a wronged partner) are not built: the pilot
measures what the seat does in the base world's rounds; a situation would be a set of interventions at the fork (an offer by
`inject_action`, a notice) and is the next step.

**Not done:** the norms (above); the text judge (section 5.3); extending the analysis scripts to `temperament_json` and the
conditioned measures (section 5.1, for runs made with the model); Moral Foundations.

## Scripts (34_temperament_scripts/)

Run from an empty directory: `python -I fetch.py` downloads the five tables for every published run (about 50 MB), then
`python -I traits_vs_behaviour.py` (section 2 table, archetypes, length by level), `python -I promises.py` (vote and payment
promises vs actions), `python -I reasoning_text.py` (deception talk, trait echoes). The conditioned-behaviour analysis (gift return,
retaliation, giving first) was run inline; re-implement it from section 2's definitions.
