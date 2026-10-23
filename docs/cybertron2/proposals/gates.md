# Proposal: gates (entry to a place)

**Status:** accepted: D2-5 (an automatic check first, otherwise the keeper and the arrivals talk on the day they arrive); the rest
discussion. **Owner:** 37.2 (author); the mechanism is 37.4's (places, the day, conflict), tolls and passes are 37.2's (economy,
documents).

## Summary

Any enclosure has an entry rule: a room, a house door, a walled compound, a walled town, a toll bridge, a pass, later a border. A
walled node is a building at the scale of a node, so its gate is a door. The rule is checked at dawn; whoever it does not admit
waits outside and talks with the keeper in the ordinary talk step, and an admission takes effect at once, so the admitted arrival
can still act inside that day. No new phase is needed.

## The proposal

### Rules a gate can have

Open; a list of names; a token (a pass, a seal: documents, 02h); a payment (a toll); otherwise the keeper decides.

### How it fits the day (05 §1)

1. **Walls change the node's layout.** Edges end at a site outside the walls (the suburb outside the gate, often with an inn).
   Entering is a crossing with a rule.
2. **Dawn:** arrivals appear outside. The automatic rule runs; those it admits are inside before they look and decide.
3. **Look and decide:** the rest see they are outside and decide from there (wait, ask, trade outside, lodge at the inn outside,
   leave). Each states its business in its messages.
4. **Talk:** the keeper and the waiting arrivals are at the same site, so they talk in the talk step, together, with private
   messages (D2-7). **Admitting is a talk-step act** (free, like a message), so it takes effect at once; the admitted arrival has
   received something, so it is asked again and may change its plan to act inside for the rest of the day.
5. **Talk runs out** (`talk.waves`) without admission: the arrival stays outside for the day and can try again tomorrow.

### What it makes worth having

- **A pass saves a day:** admission by rule is at dawn; a negotiation can cost the day. That price is what makes passes and seals
  worth carrying, forging and stealing.
- **A gate is only as good as its enforcement:** a keeper can be bribed or fooled with a forged pass; a gate can be forced (a
  building raid on it, [attacks_and_walls.md](attacks_and_walls.md)); a wall with gaps can be walked round; with no keeper on duty
  only the automatic rule applies; at night the gate is shut and an arrival wakes the keeper (a [fuse event](fuse_events.md)).
- **A toll is the town's revenue:** the wall pays for its upkeep and its keeper, as market towns paid for theirs. The keeper is an
  office (37.3).

## Why

- One mechanism covers rooms, doors, walls, bridges and borders, so nothing gate-specific is built.
- It reuses presence and the talk step: the people at the gate talk because they are at the same place.
- It ties walls to revenue and to documents, both of which make chokepoints someone can hold.

## Alternatives considered

1. **A pre-entry phase before the day:** a separate step for walled nodes; rejected as unnecessary, since the dawn check and the
   talk step cover it.
2. **Admission as a work-step action:** it could run after the arrival's own actions, so anything tried inside would be refused;
   the arrival would lose the day. Rejected in favour of a talk-step act.
3. **Separate conversations between the keeper and each arrival:** not needed; they share a site, and private messages exist.
4. **Walls as a pure defence bonus with no entry rule:** loses tolls, passes and the keeper's power.

## Open questions

1. Whether the admitted arrival's re-ask counts as one of the talk waves.
2. Tolls before coin exists (paid in goods) or only with coin (E5, D2-1).
3. Whether a gate's rule is a standing setting of its holder or a law of the institution that holds the wall (proposals/law.md).
4. What arrivals see of the gate and its rule before they arrive (their beliefs about the place).

## Affects

world/places.md (the site outside the walls), core/round.md (dawn check; admission in talk), information/speech.md,
conflict/defence.md (walls and gates; 37.2 the economics), economy/money_and_markets.md (tolls), information/letters_and_documents.md
(passes, seals), institutions/offices.md (the keeper).

## History

- 22 Oct: Zach asked whether a walled node should have a pre-entry check: automatic ("if they have X, let them in", a list of names),
  otherwise a doorkeeper who talks with the arrivals and decides. 37.2 proposed a boundary with an entry rule, the same as a room's
  or a house door's, with no new phase (02k §2).
- 22 Oct: Zach agreed: automatic first, otherwise the keeper and arrivals talk on the day they arrive (D2-5). He asked whether they
  could be let in during the talk step so they can still act; 37.2: yes, admission as a talk-step act, so the admitted arrival is
  asked again (05 §1 step 4).

## Sources

[02k §2](../../review/37_growth/02k_fuses_and_gates.md); [38.05 §1](../../review/38_space_engine/05_round_design.md);
[38.06 §4](../../review/38_space_engine/06_actions_design.md) (door policies); [02h §4a](../../review/37_growth/02h_information_in_space.md);
D2-5, D2-7, D4-8.
