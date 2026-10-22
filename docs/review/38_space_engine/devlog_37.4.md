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

## Proposed, not yet decided

- **Speech (Zach: not a round late).** Port cybertron 1's DM step (fast mode: messages in the plans are delivered before any
  action runs; recipients are asked again and may reply and change their plan, up to `exchanges` waves), limited to the people at
  the agent's node at the start of the round.
- **Time and travel, revised:** a round is a work period (actions are stints of work); an edge costs actions by its length;
  a short hop is done inside the round (the agent acts at the destination without having seen it, since plans are decided once);
  a trip longer than the round's actions continues next round; ending a round on the road means sleeping out (unsheltered
  unless carrying gear). Revises decision 3's "arrive next round" for short hops; Zach to confirm.
- **Node size:** a hamlet or neighbourhood (2-5 households, up to about 15-20 people, a handful of buildings); a village is a
  cluster of such nodes joined by short edges.
- **Node kinds set comparative advantage**; no kind self-sufficient.

- **Messages between nodes** as a world setting: `instant` (as now in cybertron 1), `post` (delayed by the travel time),
  `carried` (a letter is an item someone carries; couriers, traders and children carry mail). cybertron2 today has no messages
  between places at all.
- Physical goods change hands only between people at the same node; money and credit (once ported) move anywhere.

## Log

- **22 Oct.** Zach: speech must not lag a round (keep a DM step, limited to people present); how time and space interact; node
  size (neighbourhood or village); travel gear (packs, camping gear); node kinds as comparative advantage. Proposals above.

- **22 Oct.** Took over `cybertron2` (Posts 3 and 4 on the board). Read the code: world, act, perceive, prompt, run, the two specs.
  Recorded Zach's decisions above.
