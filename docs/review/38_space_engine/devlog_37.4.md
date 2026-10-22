# Review 38: development log of the 37.4 session (space, environment, frontier)

Branch `wp/cybertron2`. The 37.4 session took `cybertron2` over from 37.2 on 22 Oct (handoff: [README.md](README.md); board Posts 3
and 4). Earlier 37.4 work on the old engine (the environment review, revised design and an unwired draft module) is on
`wp/environment`: `docs/review/37_growth/04_environment_design.md` and `04_environment_log.md`. Newest entries at the top of the log.

## Status

Design only: Zach designs with this session and says when to build. `cybertron2` as handed over is the starting point; nothing
changed in its code yet.

## Decisions (Zach, 22 Oct)

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
