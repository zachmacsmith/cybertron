# Households and dwellings: membership, use and home are data that agents change

**Status:** partly accepted: D4-36 (the principle); the open questions remain. **Owner:** 37.4 (37.2: building costs; 37.1 when it joins: inheritance).

## Summary

Who belongs to a household, who may use a house, and where a person lives all change through what agents do. None of them is fixed
at seeding. Joining another household, taking up an empty house and building a new one then need no feature of their own; each is
an ordinary action on general rules. They follow from four decided pieces:
- D4-18: households are institutions with members;
- D4-30: access to a building is data;
- D4-23: the engine enforces possession, and claims are recognised or disputed;
- D2-9: buildings are made from parts.

## The proposal

1. **Membership is data.**
   - A household is an institution (D4-18) with a list of members.
   - `admit {person}`: the household takes someone in; who may admit is the household's own rule.
   - `leave household`: any member may leave.
   - A person belongs to one household at a time. Joining another means leaving the first.
   - People who leave keep what they carry. What is in the store stays with the household.
2. **Use follows membership and access.** Who may use a house is its access list (D4-30). By default that is its household, plus
   anyone the household grants.
   - `grant {person, house}` gives a non-member use of the house, standing until withdrawn.
   - `withdraw {person, house}` ends a grant.
3. **The night follows use.**
   - You sleep in a house you may use at the node where you are.
   - You eat what you carry first, then from that house's store (`buildings.md`: "sleeping in a house you may use").
   - `welcome` stays as a one-night shelter. Whether it also feeds the guest is an open question below.
4. **Home is derived.** Your home is the house you may use as a member of its household. Join a household and its house becomes your
   home that night; leave and you have none until you join, occupy or build. The prompt's "You" section and the map distances follow
   from this.
5. **An empty house can be occupied.** Living in a house nobody occupies is possession, which the engine allows (D4-23). Occupying
   it records a claim, "lives there since day n"; claims already held on the house stay; custom or an institution recognises one, or
   it is a dispute. A household that occupies a house adds it to its own access.
6. **A house can be built.** Building is construction from parts on a plot one holds or claims, from materials and work over days
   (D2-9, `buildings.md`). It needs one general verb for adding work and materials to a building in progress. A house is then just a
   building whose fittings include a hearth and beds.
7. **What agents see.**
   - Membership, access and claims appear where they matter: in "You", in the place description, and in the kin list.
   - Changes are events at a place (place.md): "Warin and Osric were taken into Fenn House", "Osric moved into the empty house on
     the Green".

## Why

The valley run (38.15) showed the cost of the fixed rule:
- The Smiths' village could not feed them. Their kin a day away sheltered them for 14 nights, yet a guest could not eat from the
  store.
- Warin died a guest at Fenn House, whose store held food.
- No agent proposed moving, which may be because nothing in the world allowed it.

With membership, use and home as data:
- the move becomes one of the things agents can choose;
- whether they choose it becomes a finding, not an artefact of the engine.

## Alternatives considered

- **A migration verb that moves a household.** Rejected (Zach, 23 Oct): it is one case of general rules; joining, occupying and
  building should all be supported.
- **`welcome` for many nights in a row.** Keeps the guest outside the household. Rights to the store, access and home stay unclear,
  and the host must renew it every night.

## Open questions

- **Does a one-night `welcome` include a meal from the store,** or only shelter, with feeding a guest done by giving or by `grant`?
- **Who in a household may admit someone or grant use:** the head only, or any member? Should it be the household's own rule, with a
  seeded default?
- **An emptied house.** Does it stay held by the old household's claim, or become empty and open to occupation, and after how long?
- **Joint households.** May two households merge into one?
- **Building numbers.** The parts, materials and days for a small house: 37.2's `buildings.md`.

## Affects

- `spec/institutions/membership.md` (to compile);
- `spec/world/holding.md` (occupying as possession and a claim);
- `spec/economy/buildings.md` (shelter by use; building as work on parts);
- `spec/economy/lodging.md` (welcome against grant);
- `spec/agents/` (verbs: admit, leave, grant, withdraw, and the build verb).

## History

- **23 Oct 2026.** Zach stated the principle (D4-36): joining, taking up an empty house and building one are all supported. Open questions unchanged.

- **23 Oct 2026.** Found that 38.09 and 38.05 already designed joining and hosting; this proposal follows them (38.16).

- **23 Oct 2026.** Proposed by 37.4 after the valley run (38.15). Zach: joining another household, taking up an empty home and
  building one should all be supported, not a migration feature.

## Sources

- 38.09 §2d-2e (joining: the head's consent and living there; membership by partnership, birth, adoption, leaving, death; a
  new household needs a new house); 38.05 §3 (hosting: `host` by the head or whoever the household allows, a standing `welcome`,
  beds).

- 38.15 §2 and §5;
- D2-9, D4-18, D4-23, D4-30;
- `buildings.md`, `holding.md`, `lodging.md`, place.md.
