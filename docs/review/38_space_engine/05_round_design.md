# Review 38.05: the round (a day)

*22 Oct 2026, 37.4 session, with Zach. Design only: nothing built. Follows the decisions in [devlog_37.4.md](devlog_37.4.md)
(a round is a day; travel is the last act of a day; arrive, then decide; speech is not a round late; transport and messages between
nodes are carried) and the places design ([04_places_design.md](04_places_design.md)). Changes to `cybertron2` as built are marked
**(change)**.*

## 1. The order of a day

| Step | What happens | Model calls |
|---|---|---|
| **1. Dawn** | Travellers whose journey ends today appear at their destination. The calendar moves on (the season, days to the next). Morning incidents fire (a stray herd, a traveller's news). Each node's signs for today are drawn. | none |
| **2. Look** | Everyone at a node observes it: who is here (and who arrived this morning), the sites and their state, today's signs, what is visibly carried. Travellers still on the road observe nothing. | none |
| **3. Decide** | Everyone at a node decides from the same state, in parallel: the day's actions, messages to people here, a note to themselves, a short why. | one per agent at a node |
| **4. Talk** | Messages are delivered to their recipients at the same node. Each agent who received one is asked again: it sees the messages, may reply, and may change its plan. Replies are delivered and their recipients asked again, up to `talk.waves` times. (cybertron 1's DM step, limited to the node.) **(change: speech no longer waits until the end of the round)** | one more per agent who received something, per wave |
| **5. Work** | The plans run interleaved: one action from each agent in turn, in an order shuffled per day from the seed. Everyone present witnesses each act as it happens. **Travel is only allowed as the last action**; anything listed after it is dropped. **(change: travel was an ordinary action)** | none |
| **6. Departures** | Travellers leave with what they carry (goods, letters, passengers who left with them). Those staying see them go and in which direction. | none |
| **7. Night** | The world step, in order: hunts settle; fights and raids against whoever is at the node; regrowth (by kind, season and era); hearths burn fuel; everyone eats where they sleep (§3); the starvation hazard; the cold; spoilage; breaks; the land's slow changes (soil, forest returning on abandoned land); night incidents (fire, flood). Travellers on the road eat from their packs and draw the road's risk. | none |
| **8. Memory** | Each agent's day moves into memory (the full band, then a one-line summary), as built. | none |

**Everyone plans at once**, as cybertron 1's simultaneous mode: every agent decides from the same state in parallel, and only the
talk step asks anyone again. No agent waits for another's turn, so a day takes about two model calls of wall-clock time however
many agents there are. Nodes keep it cheap as worlds grow: talk, witnessing and the prompt's "Here" are all limited to one node,
so each agent's prompt and message traffic grow with its node (at most about 15-20 people), not with the world.

Cost: one call per agent at a node, plus one per message recipient per wave. Agents on the road cost nothing.

## 2. Travel

- **Leaving.** `travel {to}` must be the day's last action. The traveller can do anything else first: trade, pack, hand over a
  letter, say goodbye. It leaves in step 6 and is no longer at the node for the night.
- **On the road.** An edge of length d days: the traveller is in transit for the nights of days 1 to d-1 and arrives at dawn of day
  d. While in transit it makes no model call, receives nothing (it is not at any node), eats from what it carries at the
  sleeping-out rate (1.5; less with camping gear), and draws the edge's risk each night (injury, robbery, getting lost: set by the
  edge and the land it crosses).
- **Together.** People who leave by the same edge on the same day in the same direction travel as one party: they arrive together,
  and the risk falls with the party's size. That is how caravans and escorts form.
- **Arriving.** At dawn the traveller is at the destination, sees it fresh (step 2) and decides there (step 3). It may come with a
  plan (in its note), and change it on seeing what is there.
- **Waypoint nodes.** If a journey crosses real nodes (a forest, a pass), each is one day: the traveller arrives, looks, decides
  (go on, turn back, forage, rest) and travels again. Real nodes are where things can happen on the way; edge lengths are where
  they cannot.
- **What someone at home knows of a traveller:** where they were going, as last seen. Nothing more until they return or a letter
  comes.

## 3. Where you sleep, and what you eat

Decided at night by where the agent is:

| Where | Food | Notes |
|---|---|---|
| Its own house, sound, fire lit | 1 | as built |
| Its own house, damaged or overcrowded | 1.2 (winter 1.5) | as built |
| A host's house, as a guest | as the host's house | needs the host's welcome and a free bed; adds to the host's fuel |
| An inn | as housed | paid to the innkeeper |
| Out, with camping gear | about 1.2 (winter 1.5) | the gear wears out |
| Out in the open | 1.5 (winter 2, and the cold) | as built |

**Hosting.** A household's head (or anyone its household allows) can welcome a guest for the night (`host {guest}`, at the house)
or keep the door open (`welcome {all | household | name}`, a standing setting). A guest sleeps there if welcome and a bed is free.
An inn is a building whose keeper sets a price; staying is `lodge {inn}`, paid at once.

## 4. Trading face to face

Run 2 showed what goes wrong with only `give`: goods were handed over on trust, and payments came a day late or never. So:

- **`offer {to, give: {item: qty}, get: {item: qty}}`**: an offer to someone at the node, open until the end of the day.
- **`accept {offer}`**: carries out both sides at once, if both are still here and still hold the goods; otherwise refused.
  Neither side can be cheated inside one exchange.
- `give` stays for gifts, debts paid and trust.

With the talk step (step 4) the two sides can agree before the work step, so the offer and the acceptance happen the same day.

## 5. Messages beyond the node

Nothing crosses an edge unless someone carries it:

- **A letter** is an item: `write {to, text, sealed?}` makes one (a sealed letter needs a seal, later a good). It is carried like
  any item and handed over with `give`. The carrier can read an unsealed letter, keep it, or lose it on the road.
- **An errand**: when a letter or goods are handed to a carrier with a destination (`give {to, item, deliver_to, at}`), the
  carrier sees it as a due line every day until it is done ("carry Mira's letter to Ana at the Hollow"). Whether it delivers, and
  when, is measurable.
- **News** travels with people: a traveller arriving can say what it saw elsewhere (the talk step), and its observations of other
  places come with it as dated beliefs.

## 6. Incidents: morning or night

- **Night** (step 7): what happens while people sleep and is found in the morning: fire, flood, a raid, a theft, a death, a house
  breaking. Witnessed by whoever is at the node that night.
- **Dawn** (step 1): what people find or meet in the day: a stray herd, a traveller passing through with news, a sick neighbour.
- Both are drawn from the seed (the same in every arm), at rates set by the land's kind, the season and the era.

## 7. Open questions

1. **Talk waves.** One wave (messages and replies, then work) is cheaper; two allow a reply to a reply. cybertron 1 used two.
2. **Can the talk step reach someone who arrives today?** Proposed: yes; arrivals are present from dawn.
3. **Should agents in transit be called** when something happens to them (an ambush)? Proposed: no; a world that wants encounters
   on the way uses waypoint nodes.
4. **Day length in the calendar** (devlog: a world setting of about 16-60 days a year).
