# Proposal: hidden ways (edges no one knows until they are found)

**Status:** discussion (23 Oct). Design only. **Owner:** 37.2 (author); edges, places and knowledge are 37.4's (world/edges.md,
layout.md, knowledge.md, D4-47), so this goes to them. **Affects:** spec/world/edges.md, places.md, generation.md;
spec/information/ (knowledge of ways); seeding; conflict/ (raids by hidden ways).

## Summary

Every edge leaves a node from **a side and a parcel** (or a few parcels). Most are known roads. Some, through deep forest,
mountains or marsh, are **hidden**: nobody at the node knows they exist, not even as an unexplored way (D4-47 goes one step
further). People **stumble on them** while working the parcel they start from (hunting, foraging, herding), more if they pay
attention to the place, much more if they attend to it and then work in it, and more with experience. A finder knows only that a
way leaves there, not where it goes, until someone follows it (D4-47). **Who is told is the finder's choice**, so a hidden way can
be a household's secret, a smuggler's road or a raider's approach.

## The proposal

### 1. Where an edge starts

- Each end of an edge is tied to **a side of the node and one or more parcels** (layout.md: "the north road leaves from the north
  side"). The parcel decides who is near it (those working there) and what hides it (forest, rock, marsh).
- Each end has a **visibility**: a **road** (known to all at the node), a **path** (known to some: seeded or told), or **hidden**
  (known to none). The two ends of one edge can differ: a pass known on its far side and hidden on this one.

### 2. Finding a hidden way

For each person who spends time in a parcel a hidden way starts from, each day (keyed draws, D2-70):

**chance = base (how well hidden) x activity x attention x knack x traces**

| Factor | Values (proposed) |
|---|---|
| base | dense forest about 0.01; mountains 0.005; marsh 0.01; scrub 0.03 |
| activity in that parcel | hunting 1.0 (roaming after game); foraging 0.7; herding 0.5; felling 0.3; passing through 0.1 |
| attention (seeing.md) | none 1; attending to "the forest" (the place in general) x3; **attending to it and then working in it** x5 |
| knack (woodcraft: a skill by practice, D2-52, raised by roaming work: hunting, foraging, trapping, scouting) | a novice x0.5 to a master x3 |
| traces | a way someone used lately leaves tracks: x2 for a few days, x5 after a party or a herd passed |

- **What the finder learns:** "a narrow trail leaving the Deep Wood eastward, worn by deer, or by people" (an unexplored way,
  D4-47), not where it leads. Following it is how the far node is found.
- **Telling is a choice:** the finder's knowledge is its own (knowledge.md); it can tell its household, sell the knowledge, keep it
  to itself, or tell a lord. Others can learn it only by being told, led, or finding it themselves.
- **Ways close again:** a path no one uses for a long time grows back toward hidden (a slow internal change).

### 3. What hidden ways do in a world

- **Surprise:** raiders who know a hidden way arrive where no watch stands (layout.md: a watch stands on the side the road comes
  in); a village that finds the raiders' way can watch it or block it.
- **Escape and smuggling:** a household's secret way out in a siege; a way round a toll or a gate (02k).
- **The frontier:** new land (37.5) is reached first by those who find the ways into it, so woodcraft and secrecy become leverage.
- **Seeding:** generated landscapes mark some edges through deep forest, mountains and marsh as hidden at one or both ends; some
  are seeded as known to a few households (an old hunter's path).

## Why

- It turns exploration into something people do with their ordinary work and skill, not a special action.
- It makes knowledge of the land a private good that can be kept, traded or betrayed.
- It extends D4-47 and place.md (edges from sides) without a new mechanism: a hidden way is an unexplored way nobody has seen yet.

## Open questions (for Zach, and 37.4)

1. Edges tied to a side and parcels at each end, with a visibility per end (road, path, hidden)?
2. Finding by work in the parcel, raised by attention, acting after attending, knack and traces?
3. Woodcraft as a skill by practice from roaming work, raising both finding ways and reading signs on the road (journeys.md)?
4. Unused paths growing back to hidden?

## History

- 23 Oct: Zach: some edges should be hidden; each edge from a node should have a side and maybe a parcel it connects to; in deep
  forest or mountains no one knows of it until it is found; hunting or foraging there gives a chance to stumble on it; observing
  the forest or mountains raises it, observing then acting raises it a lot; finding should scale with experience; finders decide
  whom to tell. Written.
- 23 Oct: the finding rule (§2) generalised to every thing at a spot in [things_in_places.md](things_in_places.md); a hidden
  way's end is one case.

## Sources

[layout.md](layout.md), [place.md](place.md), [seeing.md](seeing.md), [knowledge.md](knowledge.md), [journeys.md](journeys.md),
[gates.md](gates.md), [attacks_and_walls.md](attacks_and_walls.md); D2-52, D2-70, D4-47, D4-48.
