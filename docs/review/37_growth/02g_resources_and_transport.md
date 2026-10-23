# 37.2g Resources, livestock, transport, inns and the layers only a society can afford

> **Status (23 Oct):** the current state of these ideas is in `docs/cybertron2/proposals/` (resources_and_goods.md, livestock.md, transport_and_lodging.md, attacks_and_walls.md, economy_later.md); decided rules are in `docs/cybertron2/spec/economy/`. This note keeps the analysis.

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

### 1b. What building and infrastructure consume (correction, 22 Oct)

The tests above were applied against people's needs only. Zach: resources must also be chosen for what **buildings, improvements
and infrastructure** consume. A bill of materials for everything the economy builds (rough shares, before calibration):

| Built thing | timber | stone | clay or brick | copper | iron | leather | fibre (rope, cloth) | other |
|---|---|---|---|---|---|---|---|---|
| house | frame | foundation, hearth | or brick walls | | | | | |
| granary, store | frame | raised floor (damp, rats) | storage jars | | | | sacks | |
| watermill | wheel, frame (big beams) | **millstones** | | pins | gears, fittings | | | a river site; millwright skill |
| smithy | | hearth | bellows nozzle | | | bellows | | charcoal |
| kiln | | yes | brick | | | | | fuel |
| bloomery (iron) | | yes | clay | | | bellows | | **much charcoal** |
| salt works | | | clay pans | or metal pans | | | | fuel |
| inn and stable | frame | hearth | | | | | | |
| deep mine | props | | | | tools | | **rope** | pumps later |
| palisade or wall | palisade | **stone wall** | | | | | | |
| track | | | | | | | | labour |
| road | | **gravel, paving** | | | | | | labour, upkeep |
| bridge | span | **piers, arch** | | | fittings | | | |
| irrigation, terraces | | **lining, terrace walls** | lining | | | | | labour |
| pens, fences | yes | | | | | | | |
| cart, wagon | body, wheels | | | fittings | **tyres, axles** | harness | | |
| boat, docks | **oak** hull, piles | | | nails | nails | | **rope, sails** | pitch (from pine) |
| tools, weapons | handles | | | head, blade | better head, blade | grip | | |
| harness, saddle, packs | | | | bit | bit | **yes** | straps | |
| barrels, pots | staves | | pots | hoops | hoops | | | |
| coin | | | | yes | | | | or silver |

What it changes:

- **Stone is a core resource after all.** People do not consume it, but millstones, roads, bridges, walls, terraces, foundations and
  hearths do. It is heavy, so quarries tie infrastructure to place: a good quarry near the road and the river is an advantage, and
  stone is carted one edge at most. My earlier "later" was wrong: it judged stone only against people's needs.
- **Fibre (flax, hemp; wool from sheep) is needed** for rope, sacks, nets and sails before anyone needs cloth. Mines, boats, packs
  and the granary need it. It moves from parked into the core.
- **Leather is the cattle's second product,** wanted by harness, saddles, packs and bellows: transport and the smithy depend on
  the herds.
- **Charcoal is the hidden giant.** Smelting, especially iron, eats wood. A region with a bloomery strips its woods (37.4's trends)
  unless it manages woodlots (02e §4).
- **Iron is what the higher rungs are made of:** tyres and axles, mill gears, better tools and blades. That makes iron the
  strategic material of a complex society (§1c).

**Revised core set (nine):** grain, wild food, livestock (cattle and horses), timber, **stone**, clay, copper ore, salt, **fibre**.
Hides, leather, charcoal, pitch, pottery, bricks, flour, meat and cheese are derived.

### 1c. Resources hard to get but valuable to a complex society (Zach, 22 Oct)

Some resources should be beyond a household or a hamlet: worth something only to a society organised enough to get them and use
them. What makes a resource hard, each one a threshold (02c §8):

| Kind of difficulty | Example |
|---|---|
| **deep**: a crew, props, rope, later pumps; dangerous (accidents) | a deep copper or iron seam; a silver vein |
| **rare**: one place in a region, or none (found only by a frontier expedition, 37.5) | tin, silver, a salt seam |
| **slow**: generations to regrow, so effectively finite | old-growth oak (keels, mill axles, great beams) |
| **skill-gated**: worthless without a high skill and a building | iron ore without a bloomery and a smith |
| **from beyond**: only an outside market sells it (engine gap G-8) | spices, dyes, glass, fine cloth |

What makes them valuable, each a reason a society wants them:

| Resource | Why a complex society wants it |
|---|---|
| **iron** (ore plus charcoal plus a bloomery plus skill) | tools x1.5 over copper; tyres and axles for wagons; mill gears; blades. The strategic material |
| **tin** | with copper, bronze: better tools and blades from two distant places, so it forces long-distance trade |
| **silver** | coin that carries great value in little weight (02f §6.1: carried coin), the reserve behind credit, gifts that bind |
| **old-growth oak** | ships, mill axles and great halls, where nothing else serves; once cut, gone for a lifetime |
| **wild horses** (§2c) | riders and cavalry, for a society that can catch, break and feed them |
| **goods from beyond** | status and gifts. They matter only if something values them: an agent's in-world aim, an office's insignia, a law. Without that they are dead weight, so add them only with a reason |

**The rule for this tier (widened in §1d):** every hard resource must either multiply something the society already does (productivity,
transport, force, credit) or unlock something it cannot do at all (§1d), or it will sit unwanted. Only the luxuries depend on what agents value, and they come last.

### 1e. The chains: from the ground to use (Zach, 22 Oct)

*A catalogue, not a build list (22 Oct, after Zach asked whether these were already here). They are drawn from history, not from
the old engine: it has timber, stone and copper from camps, blades, crude weapons, stores, forts and four farm improvements, and
none of these intermediate steps. Most of the steps below have a single use and should not be built. §1f says which to keep.*

```
TIMBER   standing wood (a forest, or a managed woodlot that regrows)
           └ fell (axe; a crew for big trees) → logs: heavy, bulky; float downriver as rafts
               ├ split → firewood (fuel: hearths, kilns, lime, bricks)
               ├ charcoal clamp (about 5 timber → 1 charcoal: light, so it travels) → smelting and smithing
               ├ saw pit (2 sawyers; later a sawmill on a water wheel) → planks and beams
               │    → buildings, carts, boats, fittings
               ├ old-growth oak → great beams (big halls, mill axles, keels: §1c)
               ├ pine → tar kiln → pitch (boats)
               └ oak bark → tannin (tanning hides: see HIDES)

STONE    a quarry site (hills, a ridge)
           └ quarry (a crew, iron tools, dangerous) → rough stone: very heavy, one edge by cart at most
               ├ mason → dressed stone (walls, arches, columns, upper storeys: 02i §2c)
               ├ mason → millstones (from a hard stone, found in few places)
               ├ break → gravel (roads)
               ├ limestone + kiln + fuel → lime → mortar (stone building), and lime for tired fields
               └ slate → roofs that do not burn

CLAY     a riverbank
           └ dig → clay: heavy
               ├ potter + kiln + fuel → pottery: jars and bins (storage that cuts spoilage)
               ├ mould, dry, fire in a kiln → bricks (walls, ovens, hearths)
               └ with wattle → daub (cheap walls)

COPPER   a seam → mine (deep: a crew, props, rope) → ore: heavy
           └ smelt near the mine (charcoal + bellows) → copper: light for its value
               └ smith (anvil, bellows, hearth) → tools, fittings, blades, coin
IRON     the same chain, with far more charcoal and a higher skill (a bloomery)

FIBRE    a flax or hemp field → ret, break, spin → thread → rope, sacks, nets, sails; cloth (parked); paper (rags: 02h §2)
HIDES    cattle and game → tannery (pits, oak bark, water, rounds of waiting) → leather: harness, bellows, packs, saddles
           └ scraped and dried instead → parchment (02h §2)
```

**Where each step happens (Weber's location rule).** A step that loses weight is done near the source, so less is carried. A step
that gains weight, or makes something fragile, is done near the market:

| Step | Weight | So it sits |
|---|---|---|
| charcoal (5 to 1) | loses | in the wood |
| smelting ore | loses | at the mine |
| dressing stone | loses a little | at the quarry |
| quarrying, felling | the raw stuff is heavy | at the source; carried one edge at most, or floated |
| milling | about even | at the river (power), between fields and town |
| baking | gains (water) | in town |
| building | everything converges | where the building is |

**Fuel is the hidden spine.** Hearths, charcoal, lime, bricks, pottery, smelting and smithing all burn wood. A region's woods are
the limit on everything it makes, which is why managed woodlots (02e §4) and charcoal's weight loss matter, and why 37.4's
woodland trend is economic.

**Each step is a trade and a building part:** charcoal burner, sawyer, quarryman, mason, potter, brickmaker, tanner, smelter,
smith; their fittings or works (charcoal clamp, saw pit, quarry, lime kiln, kiln, tannery, bloomery) join 02i's vocabulary
as each chain is built.

### 1f. Pruning: few goods, many uses (22 Oct)

Zach: do we need this many variants, if each has one use? No. **A good or a processing step earns its place only if:**

1. **several things use it** (stone: walls, storeys, roads, hearths, millstones), or
2. **it creates a chokepoint or a trade** someone can hold (the mill, the smith), or
3. **it changes weight or shelf life enough to move where things happen** (salted meat keeps; ore smelted at the mine is lighter), or
4. **it unlocks something** (§1d: writing).

Otherwise **fold the step into the recipe that uses it.** A blade is made at a forge from copper and timber, and the smelting and
the charcoal are inside that recipe's cost, not separate goods.

**The lean set for the first worlds (about ten goods):**

| Good | Uses | Why it stays |
|---|---|---|
| grain | food, bread at a mill, fodder for horses | the staple, and the mill's chokepoint |
| wild food | food | the bottom rung |
| livestock (cattle; horses later) | milk, meat, hides, draught | one entity, five dependences (§2) |
| timber | fuel, building, carts, fittings | used by almost everything |
| stone | walls, storeys, roads, hearths, millstones | used by every larger or lasting build (02i §2c) |
| copper | tools, blades, fittings, coin | the metal; the hill camp's trade |
| salt | keeping meat; cattle | the long-distance good and the tax (§1) |
| hides | packs, harness, bellows, parchment | the herds' second product, and writing (02h §2) |
| tools and blades | yield, fighting | made goods that wear out: the smith's trade |
| documents | writing | the unlock Zach rates highest (02h) |

**Dropped or deferred, by the rule:**

- **Folded into recipes:** charcoal, planks, lime, gravel, dressed stone, slate, leather (hides are used as they are).
- **Deferred to later eras:** pitch and boats; clay, pottery and bricks; fibre, rope and cloth; iron and tin; tannin.
- **Clay is the one to watch.** Its distinct use is storage that cuts spoilage. Bins (timber) and cellars (stone) cover that at
  first, so it waits.

**The same rule cuts 02i's fittings** to beds, hearth, bins, benches, shelves, lock, anvil-and-bellows and millstones (with a water
wheel by a river). The rest come with the goods that need them.

### 1d. Resources that add something new, not more (Zach, 22 Oct)

§1c's rule (every hard resource multiplies something the society already does) is too narrow. The more interesting resources
**unlock a capability the world does not have at all**: a new kind of act, a new kind of knowledge, a new kind of control. Each needs
a hook in an existing system, or it is decoration.

| Capability it unlocks | Made from | What becomes possible | Engine hook |
|---|---|---|---|
| **writing** (parchment, ink) | hides (parchment), soot or oak galls (ink); literacy as a skill | words that last and travel without a speaker: ledgers, contracts, laws as texts, letters, records anyone can read later | documents as items (review 32's prototype), carried letters (37.4) |
| **seals** (wax, a carved or cast seal) | beeswax; a carver or a smith | proving who wrote a letter or an order, so forgery becomes possible and detectable | the old engine's forged messages (`forge_dm`); offices' orders (G-4) |
| **locks and keys** | iron; a smith | access by object, not by permission: whoever holds the key opens the store; keys can be stolen, copied, shared | stores and buildings; the two-key armoury (G-13) |
| **dogs** | bred from a few (one more livestock kind) | warning: raiders noticed before they strike (the counter to ride and strike, §5b); herding and hunting help | night fights; perception (a sign at the place) |
| **beacons and signal fires** | timber, stone; a watch | one fast message across many nodes ("raiders!"), at the cost of saying almost nothing else | 37.4's signs; perception at neighbouring nodes |
| **carrier pigeons** | bred at a loft (again livestock) | a short message that flies home without a carrier | carried messages (37.4), the information regime |
| **lenses** (glass) | sand, ash, fuel, a glassmaker; rare skill | seeing farther: arrivals on an edge a round before they come | perception range |
| **medicine** (herbs, a healer) | rare wild plants; healing skill | wounds that heal, illness that is survived (if 37.1 brings illness) | hunger stages and wounds; 37.1's mortality |
| **maps** | parchment and someone who has travelled | knowledge of places as a good: sold, copied, stolen, lied about; lower danger on known edges | perception (places known), 37.5's frontier |
| **new crops** | seed from beyond or from the frontier | land that was useless becomes fields (poor soil, cold valleys) | fields; 37.5's regions |
| **gunpowder** (much later) | saltpetre (from manure heaps: cattle again), sulphur (rare), charcoal | blasting deep seams; firearms; walls stop protecting | combat, mines; an era change |

**Why these matter more than multipliers for this project.** Most of them are about **information, trust and access**: who can
know what, prove what and open what. Those are what institutions are built on, and what a takeover captures: the record, the seal,
the key, the warning, the map. A multiplier makes a society richer. An unlock changes what kinds of power exist in it.

**A shortlist for the first worlds:** writing, seals, locks and keys, dogs, beacons. Each fits a system that exists or is planned,
and each creates a chokepoint someone can hold: the scribe, the seal, the keyholder, the kennel, the watch. Lenses, pigeons,
medicine, maps, new crops and gunpowder come later, by era or by frontier.

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

### 2b. Horses: the same livestock system, a different kind (Zach, 22 Oct)

**Zach's question:** should horses be cattle plus another resource, or a different kind of animal?

**Recommendation: one livestock system, two kinds** (cattle and horses; later perhaps sheep for wool, donkeys for cheap packs).
Herds, pasture, breeding, fodder and herding are one mechanism with per-kind parameters. **What equipment adds is the function:**

| Animal | Equipped with | Becomes |
|---|---|---|
| ox | a yoke and harness (leather) | draught: the plough, the ox cart |
| horse | a saddle and bridle (leather, a metal bit) | a mount: a rider, a messenger, a mounted fighter |
| horse | harness | a team: wagons and coaches |

**Why not cattle plus a resource.** Then a horse would be made, not bred. Anyone with cattle and the resource could raise a cavalry
in a round, and the thing Zach wants to matter, breeding a fleet, would not. Horses should come only from horses: breeding stock
is scarce, foals take rounds to be useful (the delayed shape, 02c §3), and a stud is a layer only a society can afford.

| | Cattle | Horses |
|---|---|---|
| eats | grass; hay in winter | grass and **grain** (oats), more in winter: horses compete with people for grain, so cavalry is dear |
| breeds | about 0.10 of the herd a round while pasture holds | about 0.05; a foal is usable after several rounds |
| gives | milk, meat, hides, draught (strong, slow), manure | speed, mounted fighting, light draught; meat and hide only at death |
| skill | herding | riding (by practice); a war horse also needs training |

**What horses do:**

- **Speed.** A rider covers about 2-3 edges a round on a track or road. Fresh horses at an inn's stable (relays, §4) carry a message
  across a region in a night or two. Speed changes the information regime: whoever has riders hears first and warns first.
- **Fighting.** A mounted fighter adds about +3 strength (between a club's 2 and a blade's 5, and on top of the weapon). The larger
  gain is mobility: reach a place in one round, choose where to fight, leave before the defence gathers.
- **Armies and messengers both need herds, studs and grain.** Cavalry is the force only an organised society can field, and the
  stud farm is a chokepoint.

### 2c. Wild herds and shared livestock (Zach, 22 Oct)

- **Wild horses live on open grassland nodes** (plains, high meadows) as a herd with a threshold (37.4's kinds): it regrows if
  left above its threshold and collapses if over-caught. Catching is team work, like hunting large game (a crew shape, 02c §3).
  A caught horse is wild: it must be **broken** (riding skill, several actions over several rounds) before it can be ridden or
  harnessed. Grassland peoples have horses as their comparative advantage; everyone else buys, breeds or raids for them.
- **Herds can be held in common** (a village's herd on common pasture, its increase shared by rule) or privately. Either way
  breeding is the investment: the herd grows only while the pasture holds and someone herds it, and every animal eaten or sold
  is the next rounds' increase given up. Common herds raise the commons questions (who grazes how many, who herds) that
  institutions answer.

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

### 3b. The ladder's other dimensions: people, rest and risk (Zach, 22 Oct)

A rung is chosen for what it carries, how many people it carries, whether they can rest on it, and how dangerous the trip is:

| Rung | Goods | People | Edges a round | Rest on the road | Danger on the road (per edge-round, proposals) |
|---|---|---|---|---|---|
| on foot | 10 | 1 (themselves) | 1 | none: 1.5 food a night, 2 in the cold, 30% cold fall | highest: injury about 2%; the cold; carrying little, so rarely robbed |
| pack, pack ox | 20, 60 | 1 | 1 | camping gear if carried: about 1 food a night, no cold fall | about 2%; an ox can be lost or stolen |
| ox cart | 200 | 1 driver, 2-3 riding | 1 | **under the cart's cover**: as a damaged house (1.2, 1.5 in the cold), cold fall about 10% | about 1%; a broken wheel loses a round; conspicuous cargo |
| covered wagon | 500 | 2-4 | 2 on a road | **sleeping aboard**: as a sound house without a fire (1.0, 1.3 in the cold), no cold fall | about 0.5% |
| carriage or coach | a little | **4-6 passengers** | 2-3 on a road (relays) | sleeping aboard, or at the inns it stops at | about 0.3% |
| rider | a little | 1 | 2-3 | at inns, or out | lower than on foot, because it is faster; riders are robbed for the horse |
| river boat | 1,500 | crew and passengers | 3 down, 1 up | aboard | about 0.5%; floods and ice (37.4) |
| railway | 20,000 | hundreds | 8 | aboard: travellers arrive rested | about 0 |

**Three ways to lower the danger, besides a better rung:**

- **Travel together.** A convoy or caravan defends as one party, as a raid's defence does (combat.py).
- **Hire an escort.** Guards are a trade; this is the labour market for fighters in peace.
- **Sleep at an inn** (§4). Roads lower accidents and halve exposure by halving the time.

**Who draws the risk.** Accidents, breakdowns and weather are drawn from the seed: 37.4's incidents, the same in every arm (37.4
decision 4). Robbery is never random: it is agents present at a waypoint (run 2 says agents seldom choose it). The danger of a
road is therefore partly physics and partly who lives along it.

### 3c. Dangerous edges, the seasons, and travellers who never arrive (Zach, 22 Oct)

**Every edge has its own danger,** set by its terrain and changed by the season (proposals; the draws are 37.4's incidents):

| Edge | Danger per edge-round (summer) | Winter | Other seasons |
|---|---|---|---|
| a track through farmland | about 0.2% | x2 | |
| through forest | about 1% | x2 | |
| a river ford | about 2% | ice: x2 | **spring flood: x3, or closed** |
| a mountain pass | about 3% | **x4, or closed by snow** | |

The rung (§3b), a convoy, an escort, gear and a road lower it; an inn breaks a long edge into safer nights.

**A traveller who dies on the road never arrives, and nobody is told.**

- **The engine never tells anyone, and never counts the absence for them** (Zach, 22 Oct). The household **saw him leave** (a
  departure is witnessed by those left behind) and **heard what he said** about his trip. Both are kept as lasting memories,
  because a household member's departure and stated plans are salient (02_perception). Noticing that he has not come back is the
  household's own inference from its memory. (The phase-0 prompt's "not seen for N rounds" line for kin, `cybertron2/prompt.py`,
  does exactly what this rules out, and should go: flagged to 37.4.)
- The body and what was carried lie on the edge: the edge's ground (review 17). A later traveller on the same edge finds them with
  some chance (proposal: about 50% on a short edge, less in snow or on a long one), learns who it was if they knew them, and may
  take what lies there.
- The news then spreads by testimony. A death in transit is a slow, uncertain fact: rumour, a search party, a widow who keeps
  waiting, a finder who keeps the cart.

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

## 5b. Riders, buildings and raids at scale (proposals for 37.4, which owns travel and combat in cybertron2)

**Riders arrive before anyone knows (Zach, 22 Oct).** Under 37.4's rule (decision 8: arrive at the start of the next round, then
decide), a raider on foot is seen arriving, so the defenders can stand guard that night. Proposal: **mounted fighters may ride and
strike.**

- A mounted party travels one edge and attacks or raids at its destination in the same round. It arrives during the round, not at
  its start, so nobody there saw it coming when they decided.
- The price: it is **blind**, acting on its last knowledge of the place, so it may meet guards it did not know about. Its horses
  must rest and be fed afterwards.
- **Riders also leave fast.** The next round they ride two or three edges away before anyone on foot can follow.
- **The counters:** lookouts on the approaches (a watch at a waypoint sees riders a round ahead), mounted defenders, walls.
- This is an explicit exception to "arrive, then decide": Zach and 37.4 to agree.

**People attack buildings, and a big raid sweeps a node (Zach, 22 Oct).** Generalising combat.py's raid on a house:

| Target | What a successful attack does |
|---|---|
| a person | wound (robbed, starving) or kill, as now |
| a house or store | loot its stock, as now |
| any building (mill, granary, smithy, inn) | **damage** (its condition drops; repair is builders' work) or **burn** (ruined, its contents lost) |
| a herd | drive animals off (rustling); easy for riders |

**A big raid** (`raid` on a whole node, by a party): each raider's engagement draws a target at random among the people present,
the buildings and the herds, weighted by what is exposed (open stores and herds first, guarded sites last). Guards defend the site
they stand at; people indoors defend their house; walls (37.7) defend the whole node. What is left behind is the economy's damage:
a burned mill is a chokepoint lost for many rounds, felt across every node it served. That is the cut test (02a §5) in the form
of force.

**Who raids.** Run 2: LLM agents seldom choose violence, even starving beside full stores. So a world that needs raids can also
bring them in from outside: the same raid mechanics run by 37.4's incidents ("riders from beyond the hills") or by scripted outside
actors (engine gap G-8). Whether agents or incidents raid, defence, damage and rebuilding are the same.

## 6. Eras: ladders beyond the first world

Three ladders that a world's era (37.4's eras, set in the spec) chooses a rung on:

| Ladder | Rungs |
|---|---|
| metal | copper, then bronze (copper and tin from two places), then iron (a common ore, a high skill) |
| transport | foot and pack, then pack animals and ox carts, then roads and wagons, then boats and canals, then rail |
| information | word of mouth, then carried letters, then a postal service, then the telegraph |

Within a run, a world moves up a rung only by building (a road, a mill, a coach service), never by research. Whether research
belongs anywhere is a later question (37.5's frontier).

## 6b. Overlaps with other packages' briefs (checked 22 Oct)

| Brief | Its economic layers | How they meet this design | Proposed split |
|---|---|---|---|
| 37.7 coordination (no session yet) | defence that works (raids fought); granaries against lean seasons; works with returns (irrigation, walls, roads, mills) built by pooled labour, with decay; crowded commons; larger groups get more per head | the same objects as §5's layers and §5b's raids | **one building and works model** (02e §3.8 generalised). 37.2 owns what a work does and costs (thresholds, effects, materials: §1b); 37.7 owns how a group decides and pays for it (contributions, upkeep rules, the commons) and the defence side with 37.4 |
| 37.5 frontier (no session yet) | unexplored regions holding land or a deposit; expeditions; claims by rule; chartered companies | where hard resources come from (§1c: rare deposits found, not given) | 37.5 owns discovery, danger and claims; 37.2 owns what a found deposit yields and what it takes to work it |
| 37.4 environment | resources by how they come back; trends (soil, game, woods); incidents; the calendar | the regeneration column (§1), winter fodder (§2), dangerous edges (§3c), charcoal stripping woods (§1b) | 37.4 owns the dynamics and the draws; 37.2 owns uses and prices |
| 37.1 demography | households, ages, labour | households as the economic unit (02f §2) | as 02f §7 |

## 7. Open decisions

1a. **Unlocks (§1d):** a first shortlist of writing, seals, locks and keys, dogs and beacons?
1. **The core set, revised (§1b):** grain, wild food, livestock, timber, stone, clay, copper ore, salt, fibre; the hard tier (§1c):
   iron, tin, silver, old-growth oak, wild horses, goods from beyond (luxuries last, and only with a reason to want them)?
2. **Cattle:** in (recommended), with milk, slaughter, draught, manure and wealth?
2b. **Horses as a second kind in one livestock system** (bred, never made; equipment gives the function), with speed, +3 mounted strength,
   and grain as fodder?
2d. **Wild herds** on grassland nodes, caught by teams and broken by skill; herds held in common or privately.
2e. **Edges with their own danger by terrain and season**; travellers who die are never announced and are found only by chance
    (proposals for 37.4).
2f. **Riders who ride and strike in one round**, and **raids on buildings and whole nodes** (proposals for 37.4; the ride-and-strike
    rule is an exception to its decision 8).
2c. **The ladder's other dimensions** (people carried, rest on the road, danger per edge) as in §3b: are the proposed numbers in the
   right order?
3. **The transport ladder as the first rungs:** foot, pack, pack ox, handcart, ox cart (wagons, boats and rail by era)?
4. **Inns and hosts in the first region:** an inn at Millford and a host at the pass's waypoint (02f §4)?
5. **Salt's place in the first region:** a salt spring at the pass's waypoint (a natural toll point), or in the hills with copper?
