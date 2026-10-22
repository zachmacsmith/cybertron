# 37.2i Buildings from parts: structures, rooms and fittings

*22 Oct 2026. Design for discussion; nothing built. Zach: rather than template buildings, let rooms, capacities and fittings each
cost resources, so people can build a room just to sleep in or just to talk in, add a hearth, attach a room to a forge or a
library, keep an archive; and channels become rooms a group can book. This note replaces the fixed building list of 02e §3.8 and
02g §5 with parts. It is the economy's side of 37.7's works (02g §6b).*

## 1. The principle: functions attach to fittings, not to building types

The engine never asks "is this a mill?". It asks: is there a water wheel and a pair of millstones, in a room, at a river site?
Every rule (shelter, warmth, cooking, storage, speech, smithing, milling, copying) reads the parts. So:

- **any combination works:** a forge with a meeting room attached, an inn with an archive, a house with a loom;
- **specialisation branches by itself:** what a building becomes depends on what its owner adds;
- **templates still exist, as blueprints:** named sets of parts ("house", "inn", "hall") that seeding uses and agents can order in one
  action, so nobody has to design a building from scratch to get a roof.

## 2. The parts

**Structure.** A building has a footprint on its node's land (lots, 02e §3.9), a material and a size.

| Material | Cost per room (rough) | Breaks (02e) | Fire |
|---|---|---|---|
| wattle and timber | timber | as now (2% a round, 8% in the cold) | burns easily |
| timber frame on stone | timber and stone | half | burns |
| stone or brick | stone or brick, much more labour | a quarter | the roof burns, the walls stand |

**Rooms.** A room has a size: how many people it holds, and how many fittings it takes.

| Size | People | Fitting slots | Cost (wattle and timber) |
|---|---|---|---|
| small | 4 | 2 | about 8 timber |
| medium | 10 | 4 | about 15 timber, 4 stone |
| large (a hall) | 25 | 6 | about 30 timber, 10 stone |

**A room by itself gives two things:** a roof (out of the weather: from "unsheltered" to "damaged", 02e §3.2) and **a speech
scope** (02h §4a: everyone with access to the room hears what is said in it).

## 3. The fittings (a closed vocabulary)

A closed list, like the old channel selectors: every fitting has a cost, a capacity, upkeep, prerequisites and one hook in the
rules. Rough numbers, to calibrate:

| Fitting | Cost | Gives | Prerequisites |
|---|---|---|---|
| **beds** | 2 timber, 1 fibre each | a bed: sleeping here counts as housed (02e) | a room |
| **hearth** | 4 stone, 2 clay | **warmth**: the room's sleepers are housed in winter if it is lit (it burns fuel, 02e §3.6); **cooking** for the room | a room |
| **oven** | 6 brick or clay, 2 stone | bread from flour; a cook's batch for many | a hearth |
| **bins and jars** | 3 timber or 4 clay | storage: about 20 food at the house rate of spoilage | a room |
| **cellar** | 8 stone, labour | storage at a quarter of the spoilage | the ground floor; stone |
| **benches and a table** | 3 timber | seats: the room holds its full size for a meeting | a room |
| **shelves** | 3 timber | an archive: about 50 documents (or 200 pages) kept safe | a room |
| **copy desks** | 2 timber, light | a scriptorium place: copying at full speed | a room |
| **strongbox or lock** | 1 iron, 2 timber | access by key (02g §1d): only keyholders open the room or the box | a smith |
| **stalls** | 3 timber each | stabling one animal (fed from the room's fodder) | a ground-floor room |
| **anvil** | 3 iron, or 6 stone for a stone anvil | smithing, with bellows and a hearth | a hearth |
| **bellows** | 2 leather, 1 timber | smelting and forging heat | a hearth |
| **loom** | 4 timber | weaving (clothing is parked: 02_economy_worklog) | a room |
| **kiln** | 10 brick or clay | pottery and bricks | its own room; fuel |
| **millstones** | 10 stone and a mason | milling, with a wheel or by hand at a fraction | a room |
| **water wheel** | 15 timber, 2 iron | power: millstones and bellows at full batch | a river site |
| **press** (a later era) | iron, timber, a skilled smith | cheap copies (02h §4b) | a room, copy desks |

**How a hearth differs from a room.** The room keeps out the weather. The hearth keeps out the cold, and cooks. A room without
a hearth is a fine summer sleeping room and a poor winter one ("no fuel": 1.3 food). A hearth is also where the household's food
is cooked: one hearth and one cook serve everyone in the room. That is the shelter and household scale economy of 02e, now
attached to a part.

## 4. Rooms as channels: booking a room

A room's speech scope is a channel (02h §4). Who has access is set by its owner:

| Access | Example |
|---|---|
| the household | a house's rooms |
| members, officers, a list | a hall, a guild's room |
| anyone at the node | an inn's common room, a market hall |
| **whoever has booked it, for N rounds** | a meeting room let to a group |

**Booking is renting a room's access.** A standing arrangement with the owner: so many rounds, for a price, to a list of people.
While it lasts, they hear each other there and nobody else does.

- **A meeting room built only for meeting** (a room with benches, perhaps a lock) is a business: an innkeeper's back room, a
  guild's hall let between its own meetings.
- **A secret meeting** is a booked room with a lock. Who booked it, and when, is itself information: the owner knows, and so does
  anyone who saw them go in (witnessing, 02h §4a).
- **Old engine channels map here directly:** a channel's members are a room's access list, its owner is the room's owner, and its
  retention is what the room keeps (nothing, unless it has shelves and a scribe).

## 5. The ladder branches

From a lean-to to a town, each step adds rooms or fittings. The branches are specialisations:

```
lean-to (a roof)
 └ hut (small room + hearth + beds)
    └ house (rooms: hall with hearth, sleeping room with beds, store with bins)
       ├ farmstead: + barn (bins, cellar) + byre (stalls)
       ├ workshop house: + workshop room
       │   ├ smithy (hearth + anvil + bellows) ── foundry (+ water wheel: bellows at full batch)
       │   ├ bakehouse (hearth + oven) ── bakery
       │   ├ pottery (kiln)
       │   └ weaving shed (looms)
       ├ inn: common room (hearth, benches) + guest rooms (beds) + kitchen (oven) + stable (stalls)
       │   └ coaching inn: + more stalls, fresh horses (02g §4)
       └ hall: large room (benches) + strongroom (lock)
           ├ council house: + archive (shelves): laws, registers (02h §5)
           ├ guild hall: + meeting rooms to let
           └ library: archive (shelves) + reading room (benches) + scriptorium (copy desks)
               └ printing house: + press (a later era)
mill: room + millstones (by hand) ── watermill (+ water wheel, river site) ── + granary (bins, cellar)
```

Any branch can borrow from another: a forge with a meeting room, a library with guest beds, an inn with an archive of letters
left for collection (02g §4). The tree is what owners tend to build, not a rule.

## 6. Keeping it from becoming a sandbox

- **A closed vocabulary of fittings** (§3), each with one hook. No new fitting without a rule that reads it.
- **Slots per room, rooms per footprint, lots per node.** Land is finite (02e §3.9), so a node cannot hold everything.
- **Upkeep per fitting and per room** (02e §3.5), so building big has a running cost. A hall nobody uses decays.
- **Site requirements:** a water wheel needs a river, a cellar stone.
- **Some fittings dislike each other:** a forge or a kiln raises the fire chance of the rooms around it, so an archive should not sit
  next to the smithy. One rule, worth having because fire is how records are lost.
- **Blueprints by default.** Seeding and most building use blueprints (one action: "build a house here"). Adding a room or a fitting
  to an existing building is one action. Designing a whole building part by part is optional, never needed.

## 7. What agents see and do

- **At their node:** the buildings, each with the rooms they have access to and the fittings that matter ("Millford Hall: the great
  room (benches, 25), the archive (shelves: 31 documents), locked").
- **Actions:** build from a blueprint (a site, then work, as in 02e §3.8); add a room; add a fitting; let or book a room; lock and
  unlock.
- **Their own house** is shown exactly as now (02e §3.11), plus its rooms when it has more than one.

## 8. Open decisions

1. **Parts instead of templates** (§1-3), with blueprints as named sets of parts for seeding and one-action building?
2. **The fitting vocabulary** (§3): is the list right for the first worlds? Could be cut to beds, hearth, bins, benches, shelves,
   lock and anvil-bellows, with the rest by era.
3. **Booking rooms as channels** (§4), on the old channel record?
4. **Fire spreading from forges and kilns to neighbouring rooms** (§6)?
5. **Document capacity in documents or in pages** (§3, shelves)? Pages tie archives to what reading costs in the prompt; documents are
   simpler.
