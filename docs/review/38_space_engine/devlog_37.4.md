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
