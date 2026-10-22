# 37.2g Resources, livestock, transport, inns and the layers only a society can afford

*22 Oct 2026. Design for discussion; nothing built. Extends the economy plan for cybertron2 ([02f_economy_plan.md](02f_economy_plan.md))
with a principled set of base resources, cattle, a transport ladder, hospitality, and the catalogue of things too dear for a
household but affordable for a society. Transport numbers from [02g_transport_model.py](02g_transport_model.py) (deterministic;
proposals to calibrate). Zach, 22 Oct: coin is carried and debts move only as information (02f §6.1); one merchant household is
seeded (02f §6.2).*

## 1. Base resources, chosen by principle

The old set (food, timber, stone, copper; silver, gold and quicksilver in the oldest worlds) was inherited, not chosen. A base
resource earns its place by passing all of these:

1. **It traces to a need** (food, warmth and shelter, tools and security, transport), directly or through a chain (02c §11).
2. **It is found in different places** from the others, so node kinds differ and depend on each other.
3. **It comes back in its own way** (37.4's kinds: finite, fast renewable, renewable with a threshold, slow, periodic), so each
   has its own dynamic.
4. **It has its own weight for its value and its own perishability**, which decide how far it travels and how long it keeps.
5. **It adds a dependence edge no other resource adds.** If removing it changes nobody's dependence, it goes.
6. **The set is the smallest that passes 1-5.**

**Audit of the old set:**

| Resource | Verdict | Why |
|---|---|---|
| food (one item) | **split** | grain (grown, keeps, bulky), wild food (gathered, spoils: the bottom rung) and livestock products differ on every test |
| timber | keep | fuel, building, carts; slow renewable; bulky, so local |
| stone | **later** | heavy and cheap, so it never travels and adds little dependence; needed only for millstones, walls and paved roads |
| copper | keep | the metal: a finite seam in the hills, light for its value, so it travels |
| silver, gold, quicksilver | **drop** | no need path: scoring artefacts. Silver may return as coin metal |

**Proposed core set (seven):**

| Base resource | Where | Comes back | Weight for value | Keeps | Serves | Its own dependence edge |
|---|---|---|---|---|---|---|
| **grain** | fields (farm villages) | yearly, by season | bulky | well (in a granary) | the staple; flour and bread | farms feed the region |
| **wild food** | forest, scrub | fast (plants), threshold (game) | bulky | badly | the bottom rung of food; travellers' food | the exit option; game makes the hunting party |
| **cattle** | pasture (farm villages, valleys) | grows by breeding | walks itself | alive: indefinitely | milk, meat, hides, draught, wealth (§2) | farms give the region its traction and its winter food |
| **timber** | woods | slow | bulky | well | fuel, building, carts, charcoal | the wood hamlet sells fire and frames |
| **clay** | riverbanks | effectively endless | bulky | well | pottery (storage that cuts spoilage), bricks (houses that break less) | the river town sells storage and durable building |
| **copper ore** | a seam in the hills | finite | light for its value | well | tools, blades, cart fittings, coin | the hill camp sells metal |
| **salt** | a salt spring or seam | effectively endless, in one place | light for its value | forever | preserving meat, fish and cheese; cattle need it | **the classic long-distance trade good and tax**: everyone needs it, one place has it |

**Derived goods** (made, not found): flour and bread; meat, salted meat, milk and cheese; leather (hides); charcoal (timber);
pottery and bricks (clay and fuel); tools, blades and fittings (copper and charcoal); carts (timber, fittings); coin (copper, or
later silver).

**Later, for eras beyond the first:** tin (bronze needs copper and tin from two different places, which forces long-distance trade),
iron (a common ore but a high rung: a bloomery, charcoal and skill), stone, fibre (flax or wool, for cloth: parked with clothing),
coal (much later: rail and steam).

## 2. Cattle

**Recommendation: add them.** One entity creates five dependence edges:

| Use | How | What it adds |
|---|---|---|
| **milk** | a steady yield while the herd is kept and fed | a capital good that pays interest: keep it, or eat it |
| **meat and hides** | slaughter: a large food store at once and a hide | it spoils fast unless salted (salt's main use) |
| **draught** | an ox doubles a plough's work and pulls a pack or a cart | the farm-to-transport link (§3); the old engine's plough becomes an ox team a village shares |
| **manure** | grazing raises a field's fertility | the link to 37.4's soil trends |
| **wealth** | a herd is savings that walk, breed, and can be lent, given as bride price or paid as a fine | credit and kinship in kind |

**Mechanics (proposal):**

- A herd is a count per owner at a node. It grazes a pasture site, whose grass is stock-limited like the forest's plants.
- It grows by breeding while the pasture holds out. In winter it needs fodder (hay cut from the pasture in summer: a seasonal
  task, 37.4's calendar), or animals weaken and die.
- Herding is standing work: about one action a round per six head. An unherded herd strays.
- Milk about 0.6-0.8 food a round per cow. Slaughter about 12 food and a hide. Meat spoils about 25% a round, salted about 2%.
- Cattle walk themselves: a drover moves ten head on foot, so a herd is cargo that carries itself to market.
- Cattle can be driven off by raiders. (Run 2 suggests agents rarely raid; cattle make raiding easier to choose than attacking a
  guarded house, which is worth testing.)

**The decision cattle create:** a cow is worth about 12 food today, or 0.6-0.8 a round for as long as it lives. Keeping pays
after about 15-20 rounds, and pays more with breeding. In a famine people eat the herd and lose the next years' milk, draught and
calves.

## 3. The transport ladder

Every rung costed in actions per unit carried per edge, at full load, for a round trip. Each covers the carriers' rounds, their
food on the road, fodder, and capital written off over 40 rounds plus upkeep:

| Rung | Capacity | Edges a round | Needs | Actions a unit an edge | vs on foot | Capital (actions) | Who can afford it |
|---|---|---|---|---|---|---|---|
| on foot | 10 | 1 | nothing | 0.92 | 1x | 0 | anyone |
| pack (basket, leather) | 20 | 1 | nothing | 0.47 | 2x | 3 | anyone |
| pack ox, led | 60 | 1 | pasture or fodder | 0.19 | 5x | 30 | a household with cattle |
| handcart | 40 | 1 | a track | 0.25 | 4x | 12 | a household |
| ox cart (2 oxen) | 200 | 1 | a track | 0.074 | 12x | 80 | a merchant house, a rich farm, a village |
| wagon (4 horses) | 500 | 2 | a road | 0.033 | 28x | 220 | a merchant house or a town |
| river boat (crew 2) | 1,500 | 3 down, 1 up | a river | 0.006 | about 150x | 150 | a merchant house at a river town |
| railway (much later) | 20,000 | 8 | a railway | 0.002 | about 400x | 6,000 | a polity or a company |

**What it means for grain, which costs 0.3-0.5 actions a unit to grow** (02b):

- **On foot**, one edge costs about 0.9 actions a unit: twice the grain's own cost. Grain does not walk between villages.
- **By ox cart**, one edge adds 15-25% and three edges 50-70%. Grain travels one or two edges.
- **By boat** it costs almost nothing. River towns become the granaries of their region.

This is Von Thünen between nodes: bulky goods stay near their source; light, dear goods (copper, salt, tools, coin) travel.

**Break-even volumes** (the traffic a route needs before a rung beats the one below):

| Rung | Beats | From about |
|---|---|---|
| pack ox | pack | 3 units a round |
| ox cart | pack ox | 16 units a round: a few households' trade |
| wagon | ox cart | 115 a round: a town's |
| river boat | ox cart | 60 a round |

In a region of about 40 people, ox carts pay and wagons do not. That is the layer only a society can afford, in numbers.

**Infrastructure is separate,** and it belongs to the edge, not the vehicle:

| Infrastructure | What it does |
|---|---|
| a track | cleared once, needs some upkeep; lets carts pass |
| a road | a public work: stone and labour per edge, plus upkeep; lets wagons run and halves the time |
| a bridge or ferry | lets an edge be crossed at all, or in winter. A natural toll point and chokepoint (37.3's tolls) |
| docks, then locks and canals | open a river, then extend it |
| a railway | much later. It crosses several edges in one night, and travellers sleep aboard: shelter at scale, with no night out on the road |

**People are cargo too.** A carriage carries 4-6 passengers, so officials, merchants and messengers move faster than walkers. A
**scheduled coach** (an institution: a route, a timetable, a fare) also carries letters on a schedule. That is the first postal
service, and it changes the information regime: news ages less.

## 4. Inns and hosts (Zach, 22 Oct)

A night on the road costs 1.5 food (2 in the cold) and risks the cold (02e). Shelter for travellers is a service:

| Where a traveller sleeps | Costs | Gives |
|---|---|---|
| out on the road | 1.5 food, 2 in the cold; a 30% chance of waking starving in the cold | nothing |
| camping gear (a good: hides and timber) | the gear, carried | about 1 food a night, no cold fall |
| **a host's house** (a bed in someone's house) | payment or reciprocity; it takes one of the house's beds and its stock | a sound roof and the host's hearth |
| **an inn** (a building at a town or a waypoint) | a fee in coin or goods | a bed, a meal, the fire, a stable and fodder for animals |

**Why an inn pays only at a society's scale:** it is the shelter scale economy of 02e. One hearth heats many beds, and a keeper's
time serves many guests. An inn needs a flow of travellers, roughly 3-5 a round, to cover its upkeep and its keeper's actions. A
hamlet off the road has hosts, not an inn. A town on a trade route has an inn.

**Inns are information hubs** (02_perception: testimony):

- **News and prices collect there.** Travellers talk, so the innkeeper hears more than anyone, and an inn is where a merchant learns
  what grain fetches two valleys over.
- **Letters are left there for collection.** The inn becomes the first post office.
- **A coaching inn keeps a stable and changes horses,** which lets coaches run faster on post roads (relays).
- **An inn knows who is travelling, where, with what.** That makes it a chokepoint for surveillance, robbery or protection.

**Hosting without an inn:** households take in kin and travellers. That is reciprocity, and later guest-right as a norm or a law.
A host learns the traveller's news; a traveller who is refused sleeps out.

## 5. Layers only a society can afford

Each of these is indivisible capital with a high fixed cost, a cost per unit that falls with volume, a threshold (people or
volume), an owner, upkeep, and usually a chokepoint. Each must sit on a large share of what people need, or it moves little (02b
§4.3, Amdahl):

| Layer | What it does | Threshold (rough) | Usual owner | Chokepoint |
|---|---|---|---|---|
| watermill | flour in big batches | 25-70 people (02d §3) | a lord, a town, a merchant | yes: the miller's toll |
| ox team and plough | doubles field work | 3 or more households | a village or rich farm | who gets the team first |
| granary | stores grain with little loss; a famine reserve | a village | the polity, a temple | who is fed in a famine |
| smithy | tools and fittings; with a bloomery later, iron | about 20 people within reach | a smith, a guild | tools for everyone |
| kiln | pottery (storage) and bricks | a village | a potter, a town | durable houses |
| salt works | salt from a spring or brine | one site per region | whoever holds the spring | **the region's salt** |
| ox carts | 12x cheaper carrying | about 16 units a round on a route | a merchant house | the route |
| roads and bridges | wagons, speed, winter crossing | about 115 units a round (wagons) | the polity, by levy | **tolls** |
| boats and docks | about 150x cheaper carrying | a river and about 60 units a round | a merchant house, a town | the landing |
| inn and stables | shelter, news, letters, fresh animals | about 3-5 travellers a round | an innkeeper, a lord | who travels, and what they know |
| market and market days | buyers and sellers at one place and time | a town | the polity | stalls, dues |
| mint and ledger house | coin, debts, remote payment by note | a region | the polity, a merchant house | money itself |
| coach service | passengers and letters on a schedule | a town pair | a company, the polity | the post |
| railway, telegraph (much later) | goods across many edges in a night; messages anywhere at once | a state | a company or the polity | everything |

## 6. Eras: ladders beyond the first world

Three ladders that a world's era (37.4's eras, set in the spec) chooses a rung on:

| Ladder | Rungs |
|---|---|
| metal | copper, then bronze (copper and tin from two places), then iron (a common ore, a high skill) |
| transport | foot and pack, then pack animals and ox carts, then roads and wagons, then boats and canals, then rail |
| information | word of mouth, then carried letters, then a postal service, then the telegraph |

Within a run, a world moves up a rung only by building (a road, a mill, a coach service), never by research. Whether research
belongs anywhere is a later question (37.5's frontier).

## 7. Open decisions

1. **The core set:** grain, wild food, cattle, timber, clay, copper ore, salt (stone later, the precious metals dropped)?
2. **Cattle:** in (recommended), with milk, slaughter, draught, manure and wealth?
3. **The transport ladder as the first rungs:** foot, pack, pack ox, handcart, ox cart (wagons, boats and rail by era)?
4. **Inns and hosts in the first region:** an inn at Millford and a host at the pass's waypoint (02f §4)?
5. **Salt's place in the first region:** a salt spring at the pass's waypoint (a natural toll point), or in the hills with copper?
