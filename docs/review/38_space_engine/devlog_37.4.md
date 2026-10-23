# Review 38: development log of the 37.4 session (space, environment, frontier)

Branch `wp/cybertron2`. The 37.4 session took `cybertron2` over from 37.2 on 22 Oct (handoff: [README.md](README.md); board Posts 3
and 4). Earlier 37.4 work on the old engine (the environment review, revised design and an unwired draft module) is on
`wp/environment`: `docs/review/37_growth/04_environment_design.md` and `04_environment_log.md`. Newest entries at the top of the log.

## Status

Design only: Zach designs with this session and says when to build. `cybertron2` as handed over is the starting point; nothing
changed in its code yet. **From 22 Oct the decisions are kept in [docs/cybertron2/DECISIONS.md](../../cybertron2/DECISIONS.md)**
(this log's list below became D4-1 to D4-21 there); this log records work only.

## Decisions (Zach, 22 Oct; now in docs/cybertron2/DECISIONS.md)

1. **Start from what 37.2 built** and extend it; the parts that do not match the plans below are redesigned, not patched.
2. **A node is a village, a valley or a camp**: a few buildings and the land around them, not a single field or wood. Places people
   use routinely (their fields, the wood, the well, the house) are **sites inside one node**; an edge is a real trip. (Run 1 spent
   40% of actions walking between sites that should have been one node.)
3. **Travel takes time.** Moving is an action in the turn's list; what comes before it happens where the agent is; the agent then
   leaves and **arrives at the start of the next round**, seeing the destination only then. A trip of d edges keeps the agent on
   the road d - 1 rounds. No moving as a pre-action (it would let an agent look at the destination and act there in one round).
4. **External change is separate from internal consequences.** Eras, cycles and incidents are drawn from the seed (the same in
   every arm, one central scheduler); depletion, exhaustion and collapse are the resources' own physics, diverging by arm.
5. **Three time scales, each modulating the one below:** eras and trends (adapt through), cycles such as the seasons (understand
   and build around), incidents (react to).
6. **Signs:** environmental change is shown as at most one in-world sentence ("it hasn't rained in twelve days"), with an
   audience, a lag and a reliability, kept separate from the effects (so a placebo arm can test over-reaction).
7. **Resources by how they come back:** finite (a seam), fast renewable (plants), renewable with a threshold (game), slow (soil,
   timber), periodic (a migrating herd).

8. **Arrival, then decide (restores decision 3).** An agent comes with a plan but adapts on arrival: travel is the last physical
   act of a turn; the agent arrives at the start of the next round, sees the place, and decides there. Nobody trades blind at a
   place they have not seen.
9. **Transport and communication between nodes are delayed.** Goods, letters and people cross only by being carried. Merchants
   carry trade, messages and passengers between places; institutions must send people to reach outer villages.
10. **Both kinds of distance are supported.** An edge has a length in rounds; while on a long edge an agent is in transit (no
    model call; provisions and the risk drawn each round). A world can instead put real nodes along the way (a forest to cross, a
    pass) where travellers sleep, forage, meet and can be ambushed. An edge of length d is a chain of d - 1 nodes nobody acts in.

11. **Node scale: if you could go there and be back before nightfall, it is the same node.** Daily places are sites in the node;
    an edge is far enough that you sleep at the other end. A larger settlement is a cluster of nodes. (04_places_design.md §1.)
12. **A night out costs 1.5 food** (the unsheltered ration as built; winter 2 and the cold). **Hosts and inns are part of the
    design.**

13. **Actions (06):** units and costs settled by experiment; daylight varies by season; reflexes, fallbacks and policies later
    (routine first); a shop needs a shopkeeper.

14. **Institutions grow from households** to villages, specialised institutions within them, then companies and a state; an
    institution can be a member of another from the start (09 §3b).
15. **Short childhoods counted in rounds:** 1-3 rounds cared for, 3-4 rounds of menial tasks (no model call either way), then a
    youth as an agent; prompts name stages, not ages in years. Runs start with all ages and families; no time skips. Youth learn
    faster and keep it longer (09 §3b).

16. **One agent, one model, for life:** a child's model is chosen once when it becomes an agent and kept to its death; heirs to pole
    seats take the seat's model; the rest keep the population's cast balanced (09 §3b.5).

17. **Worlds are seeded as a society with a past,** with **a full family tree** of the whole population (living and dead, back to
    the founders; every kin tie derived from it): all ages, households, bloodlines, kin across places,
    relationships, debts and obligations, holdings and tenure, standing, institutions, a short history; written into each agent's
    knowledge from its own position (09 §3c).

## Proposed, not yet decided

- **Speech (Zach: not a round late).** Port cybertron 1's DM step (fast mode: messages in the plans are delivered before any
  action runs; recipients are asked again and may reply and change their plan, up to `exchanges` waves), limited to the people at
  the agent's node at the start of the round.
- ~~Time and travel as work periods with short hops inside a round~~: rejected by Zach (an agent would trade blind on arrival);
  see decision 8.
- **A round is a day; the calendar is compressed** (as RimWorld's 60-day year): year length a world setting (about 16-60 days).
- **Kinds of land** (04_places_design.md §2-3): a node's kind sets its resources and their regimes, what it lacks, settlement,
  climate response, incident rates, travel and signs; a hidden climate on two axes (temperature, moisture) so an era shifts
  comparative advantage between kinds.
- **Letters** are items (sender, recipient, text, sealed or not) handed over in person; a carrier can read an unsealed one, lose
  it or keep it. Errands (carry this to X at Y) shown to the carrier as a due line.
- **Node size:** a hamlet or neighbourhood (2-5 households, up to about 15-20 people, a handful of buildings); a village is a
  cluster of such nodes joined by short edges.
- **Node kinds set comparative advantage**; no kind self-sufficient.

- **Messages between nodes** as a world setting: `instant` (as now in cybertron 1), `post` (delayed by the travel time),
  `carried` (a letter is an item someone carries; couriers, traders and children carry mail). cybertron2 today has no messages
  between places at all.
- Physical goods change hands only between people at the same node; money and credit (once ported) move anywhere.

## Log

- **23 Oct.** Valley rerun on the rebuilt engine (v3, $10.27): 1 death against 4, 38 journeys, 15 agreements all completed, a
  disputed field settled by custom, credit across the road; nobody built or joined. Faults found and fixed during the run; D4-37
  (release). [18_valley_rebuilt.md](18_valley_rebuilt.md).

- **23 Oct.** Zach: rebuild everything (D4-34); every event in a place (D4-35); moving is general (D4-36). 37.4's decisions
  compiled into spec files (core, world, environment, signs, agents, life, seeding, institutions). `cybertron2/engine/` written on
  the designed core (38.17): place, containers, the chokepoint, Here and Mind, verbs from data, households, claims, hosting,
  building, farming, offers and agreements; 18 tests (scope canary, conservation, source check); `cybertron2/m1/` removed. Valley
  rerun (runs/v2) started.

- **23 Oct.** Generality audit at Zach's request: every spec file, 37.4's design notes 04-09 and all of M1. M1 skipped 38.08's
  core (chokepoint, containers with a place, records); most systems are narrow cases of designed general ones. Rebuild proposed.
  [16_generality_audit.md](16_generality_audit.md).

- **23 Oct.** The valley: a verb registry and generated prompt verbs, generated village descriptions, the three-village world
  generated, multi-node wiring in the run loop; a 20-day LLM run (m2_V, $8.85). Coppergate starved (4 deaths), kin carried all
  trade. Fixes after the run: carrying shown, leaving goods (D4-32), offers by place, make's inputs, home as last seen; scope audit.
  [15_m2_valley.md](15_m2_valley.md).

- **23 Oct.** Zach: speech by scope with only direct speech waking (D4-25), thinking and past reasoning (D4-26), conversation memory
  (D4-27), agent-written memory at set times (D4-28), no aims (D4-29). Built in M1 (`converse.py`); M1 re-based on the decided
  economy (undecided crafts removed); check run E. Comparison with cybertron 1 and the content history: [14](14_cybertron1_comparison.md).

- **23 Oct.** Run D: a three-household generated village, 4 Opus and 7 Haiku, with an enum-constrained reply schema; audit of
  memory, notes, perception and knowledge: [13_m1_village_memory.md](13_m1_village_memory.md).

- **23 Oct.** Follow-up to 11: a fire in one house's store (C) against a null arm (C0), richer land, measures written first. The
  first pair was void (a `move` fault made Osric's storing take food out; his mother starved); fixed and rerun as C2 and C02. No
  need arose, no gifts, the fire read as a risk; food stays 85-90% of work with full bellies. [12_m1_shock.md](12_m1_shock.md).

- **23 Oct.** Zach: build one node with memory, attending and knowledge, and test it with LLM runs, first planted founders,
  then a generated society. Built `cybertron2/m1/` (data, world, knowledge, act, perceive, prompt, run, generate, report) and ran
  A (6 founders, $3.21) and B (generated, 9 people, $4.28). Report and questions: [11_m1_slice.md](11_m1_slice.md).

- **23 Oct.** Zach: teaching passes skill; agents should know how learning works; the world grows by data (D4-24); a deep dive on
  what agents see, attention and descriptions. Updated knowledge.md; wrote proposals/seeing.md.

- **23 Oct.** Zach: the whole possible action space against what an agent is shown; force and defence. Wrote proposals/verbs.md.

- **23 Oct.** Zach: a limited private notes directory, one pinned. Wrote proposals/notes.md.

- **23 Oct.** Zach: how agents know what they can do, make and build. Wrote proposals/knowledge.md.

- **23 Oct.** Zach: how law comes over, and whether it can still be manipulated; a place for what we are thinking over, apart
  from the spec. Added docs/cybertron2/proposals/ (README, layout) and proposals/law.md (text law, three channels, records not
  goods, Python as clause implementation and a world setting, routes of capture).

- **22 Oct.** Zach: what it means to hold a plot. Wrote spec/world/holding.md (D4-23): possession, claims, recognition,
  holders, disputes, whole plots, land per mouth, `transfer_claim`. Posted to 37.1, 37.2 and 37.3.

- **22 Oct.** Zach: one central, current description of cybertron2, with design notes per session and the board for talk. Set up
  [docs/cybertron2/](../../cybertron2/README.md): the three layers, file list, ownership, rules; DECISIONS.md compiled from every
  source (H-1..7, D4-1..22, D2-1..5, directions); OPEN.md with 9 conflicts and 10 open questions; spec/README.md with the sections
  to compile and their owners. Merged `econ/37.2-thicker-economy` into `wp/cybertron2` so 37.2's notes for cybertron2 (02e-02k)
  are on one branch. Posted the structure to 37.2 on the board.

- **22 Oct.** Zach's decisions on life (14, 15, 16); seeded worlds with a past (17).

- **22 Oct.** Zach: how do children, households and death come over (37.1 built them on cybertron 1, `wp/demography`)? Read 37.1's
  devlog. Wrote [09_life_design.md](09_life_design.md): the design carries over, the code does not; changes for day rounds
  (seed every age, chapters with time skips), children not agents until old enough, raising as lived memories, life events
  located, households as houses.

- **22 Oct.** Read 37.2's designs for cybertron2 (02f economy plan, 02g resources and transport, 02h information in space, 02i
  buildings) and its board posts to 37.4 (missed until now). Wrote [08_build_plan.md](08_build_plan.md): where the two sets of
  designs meet (carrying: take 37.2's numbers; lots = slots; the talk step carries the square, rooms and private messages; coin is
  carried, superseding 37.4's proposal), milestones M0-M5, the node interface as the next step. Publishing runs to Hugging Face is
  not possible here (no HF_TOKEN; the run logs are not in the repository).

- **22 Oct.** Zach: carrying, how actions vary, overexertion (1-2 extra units for x2 food), whether cybertron 1's event system and
  contracts come over. Added to 06: working late, carrying weights, who gets more. Wrote [07_cybertron1_review.md](07_cybertron1_review.md):
  cybertron 1 as an engine, what to keep, what drifted (dual paths from byte identity, seven ways to speak, accounts as strings,
  kernel roles, the spec surface), the port plan for the institution layer (the chokepoint first), standing orders as hooks.

- **22 Oct.** Zach: routine yes; unsure about not calling agents (they should decide); more actions a day, varying; enumerate every
  action; standing orders (if attacked, if an action fails). Written: [06_actions_design.md](06_actions_design.md) (all 145
  cybertron 1 actions and 15 cybertron2 actions with their treatment on nodes, what space adds, a day's budget in work units,
  standing orders of four kinds decided by the agent, everyone called every day in the first runs).

- **22 Oct.** Zach: everyone plans at once, as cybertron 1 (confirmed in 05 §1). Should the round diverge from it? Proposed in 05
  §7: keep it as the core; add standing orders, calls only when something happens (with a k-day floor), fallbacks, reflexes,
  works and errands that persist, and later assemblies on set days.

- **22 Oct.** Round order designed: [05_round_design.md](05_round_design.md) (dawn, look, decide, talk at the node, work with travel
  last, departures, night, memory; travel and transit; where you sleep; face-to-face offers; letters and errands).

- **22 Oct.** Zach: rivers between nodes, how to generate a landscape, felling and clearing, fertility by land. Added to
  04_places_design.md: land cover and soil (§5), generation physical-first with rivers by drainage (§6).

- **22 Oct.** Node scale and nights away decided (11, 12). First design of kinds of land and the climate axes:
  [04_places_design.md](04_places_design.md).

- **22 Oct.** Zach: what about popping over somewhere and back? Proposal: such places are sites in your node; a night at the
  other end of an edge is cheap in a mild season, with hosts, inns and camping gear as the ways to make it cheaper.

- **22 Oct.** Zach: arrive then decide (decision 8); transport and messages between nodes delayed and carried, merchants as the
  carriers (9); edge lengths and waypoint nodes both supported (10).

- **22 Oct.** Zach: speech must not lag a round (keep a DM step, limited to people present); how time and space interact; node
  size (neighbourhood or village); travel gear (packs, camping gear); node kinds as comparative advantage. Proposals above.

- **22 Oct.** Took over `cybertron2` (Posts 3 and 4 on the board). Read the code: world, act, perceive, prompt, run, the two specs.
  Recorded Zach's decisions above.
