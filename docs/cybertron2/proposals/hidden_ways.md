# Proposal: hidden ways (edges no one knows until they are found)

**Status:** partly accepted: D2-90 to D2-92 (23 Oct); finding by the noticing rule (D2-85) to confirm. Design only. **Owner:** 37.2 (author); edges, places and knowledge are 37.4's (world/edges.md,
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
- Each end is a **road** (known to all at the node) or **hidden** (D2-90); a hidden way some know of is simply one they know. The
  two ends of one edge can differ: a pass known on its far side and hidden on this one.
- **How hidden it is follows its land (D2-92):** the parcel's cover (dense forest, scrub, rock hide it; open ground does not), how
  much the way is used (traffic wears it into a path, then a road), and changes to the land (felling the wood exposes it;
  regrowth hides it again where the land regrows).

### 2. Finding a hidden way

For each person who spends time in a parcel a hidden way starts from, each day (keyed draws, D2-70):

**chance = base (how well hidden) x activity x attention x knack x traces**

| Factor | Values (proposed) |
|---|---|
| base | dense forest about 0.01; mountains 0.005; marsh 0.01; scrub 0.03 |
| activity in that parcel | hunting 1.0 (roaming after game); foraging 0.7; herding 0.5; felling 0.3; passing through 0.1 |
| attention (seeing.md) | none 1; attending to "the forest" (the place in general) x3; **attending to it and then working in it** x5 |
| knack: the eye for the land (D4-50, D2-91), raised by practice at roaming work (hunting, foraging, trapping, scouting) | none x0.5 to a keen eye x3 |
| traces | a way someone used lately leaves tracks: x2 for a few days, x5 after a party or a herd passed |

- **What the finder learns:** "a narrow trail leaving the Deep Wood eastward, worn by deer, or by people" (an unexplored way,
  D4-47), not where it leads. Following it is how the far node is found.
- **Telling is a choice:** the finder's knowledge is its own (knowledge.md); it can tell its household, sell the knowledge, keep it
  to itself, or tell a lord. Others can learn it only by being told, led, or finding it themselves.
- **Ways close again** as their land allows (D2-92): an unused forest path grows over in about a season; one across open ground
  never hides.

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

1. ~~Edges tied to a side and parcels~~ decided: D2-90.
2. Finding by the noticing rule (D2-85) with the numbers in §2: Zach "probably yes"; elaborated 23 Oct, to confirm.
3. ~~Woodcraft~~ decided: the eye for the land (D2-91).
4. ~~Growing back~~ decided: follows the land (D2-92).

## History

- 23 Oct: Zach: some edges should be hidden; each edge from a node should have a side and maybe a parcel it connects to; in deep
  forest or mountains no one knows of it until it is found; hunting or foraging there gives a chance to stumble on it; observing
  the forest or mountains raises it, observing then acting raises it a lot; finding should scale with experience; finders decide
  whom to tell. Written.
- 23 Oct: the finding rule (§2) generalised to every thing at a spot in [things_in_places.md](things_in_places.md); a hidden
  way's end is one case.

- 23 Oct: Zach decided D2-90 (side and parcels; road or hidden), D2-91 (one knack, the eye for the land, for spotting ways and
  noticing in general), D2-92 (hiding follows the land: cover, use, felling and regrowth). Finding by the noticing rule: "probably
  yes", to confirm.

## Sources

[layout.md](layout.md), [place.md](place.md), [seeing.md](seeing.md), [knowledge.md](knowledge.md), [journeys.md](journeys.md),
[gates.md](gates.md), [attacks_and_walls.md](attacks_and_walls.md); D2-52, D2-70, D4-47, D4-48.
