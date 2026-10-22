# 37.2f The economy plan for cybertron2

*22 Oct 2026. Replaces the build plan in [02a_economy_design.md](02a_economy_design.md) §3 and the work log's phases P1-P6, which
assumed the old engine (an opt-in `economy` block, byte-identical replays). The economy is now built in `cybertron2` (owned by
37.4; handoff: docs/review/38_space_engine/README.md), on 37.4's node model. The analyses (02b, 02d) and the guide (02c) still
hold; this note says what changes because the world now has villages, travel, carried goods, merchants and households. Nothing is
built; Zach decides when.*

## 1. What the new world changes

37.4's decisions (docs/review/38_space_engine/devlog_37.4.md, Zach, 22 Oct) that shape the economy:

| Decision | Consequence for the economy |
|---|---|
| A node is a village, valley or camp; routine places (fields, wood, well, houses) are **sites inside one node**; an edge is a real trip | inside a node, moving goods between sites costs no travel: the within-node handling cost of 02d §4 is about zero. Distance matters only between nodes |
| A node holds a hamlet: **2-5 households, up to about 15-20 people** (proposed) | one node is too small for the deep layers. 02d put the village's lead over households at about 11 agents and the mill's threshold at 25-69. **Deep layers must serve several nodes**, so they need transport |
| **Travel takes rounds**; edges have lengths; agents arrive, then decide | a trade between nodes takes at least two trips; goods spend rounds in transit (spoiling, at risk) |
| **Goods, letters and people cross only by being carried**; merchants carry them | transport is labour, and someone has to do it: merchants are a trade, not a mechanic |
| Node kinds set comparative advantage; no kind self-sufficient (proposed) | the dependence graph runs between nodes (village to village), not only between households |
| Physical goods change hands only at the same node; money and credit "move anywhere" (proposed) | open question §6.1: whether coin is carried or teleports decides what merchants risk and who can pay at a distance |
| Speech: a DM step among people at the node, not a round late (proposed) | offers and payments stop crossing in transit (run 2's problem), inside a node |

Two run findings shape the order of work (38.01, 38.03):

- **Trade ran on good faith and failed both ways.** The Irons handed 9 blades over before payment. The Alders paid, nearly emptying
  their stock before winter; Wynn did not. Nothing let a buyer and seller swap safely.
- **The agents would not fight even starving.** For the economy this cuts both ways: theft and raids will be rare, so a merchant's
  main risks are spoilage, delay and default, not robbery, unless a world deliberately seeds aggressors.

## 2. The economy in two scales

**Inside a node: the household and the hamlet.** Households are the producers: a house, a pooled stock, members of different ages
and labour (37.1). Their work is routine (tend, gather, cook), so it runs on standing work (Post 1 rule C). Specialisation inside a
node is limited by its size (02d: households beat a village below about 11 people). So inside a node, expect mostly households of
generalists, plus one or two specialists the node's size can carry (a smith, a keeper).

**Between nodes: the region.** Comparative advantage by node kind: a farm village has grain and no ore; a hill camp has copper and
no food; a wood hamlet has timber and game; a market town has the mill, the smithy and the market. The deep layers (milling,
smithing, the market) sit at the place that serves several nodes. This is central place theory (02c §9): each layer has a
threshold (the population it needs) and a range (how far its customers can be), and a node hosts a layer only if the population
within its range meets the threshold. **Merchants are what make the range larger than one node.**

## 3. Phases

Each phase depends on 37.4's node interface and is built in `cybertron2` only after Zach says so and 37.4 agrees on the board.

| Phase | What | Why now |
|---|---|---|
| **E1. Exchange at a node** | an escrowed swap: one side offers (give X, want Y, to Z or to anyone here), the other accepts; nothing moves until both sides hold what they promised; settles at once. Standing offers at the node (a market board per node: "3 bread a round for 1 blade-share", until cancelled or unpaid), one action to post or take. Each node records its trades: **prices are per node**, shown at the node, and elsewhere only as dated beliefs (02_perception) | run 2: trade on good faith failed both ways. The cheapest, most general fix, and it makes prices exist |
| **E2. Households at work** | standing work orders (a member keeps doing a routine task each round, spending actions, until reassigned or it cannot be done); the house stock as the household's pot, with who may take from it set by the head; skill by practice per trade (02c §5); tools that multiply a trade and wear out | keeps food work below the 30% target without making it free; makes specialisation pay (02d) |
| **E3. Production and buildings** | sites in a node with the five production shapes (02c §3: flat, stock-limited, crew, batch, delayed); buildings with an owner, a site, upkeep and the recipes they enable (02e §3.8 generalised: houses, workshops, stores); `make` by recipe; the first chains: grain to porridge or bread (hand, then mill), copper to tools and blades (smithy), food to preserved food (drying, smoking) | gives node kinds their advantage and the deep layers their thresholds |
| **E4. Transport and merchants** | a carrying capacity per person (about 10 units; a pack 20; a cart or pack animal 60, needing a track), weight per good; goods in transit spoil at their rate and are lost with the carrier; travel gear and provisions for long edges (37.4); consignment (carry my goods, sell them there, bring back the price) as a standing arrangement between two agents; letters as items carrying orders and prices (37.4's carried messages) | the region's economy runs on it; merchants profit from price differences and from knowing them first |
| **E5. Money and credit** | coin from the old engine's currencies, light to carry and durable; debts as records both parties hold; a ledger at a node (an institution's: a merchant house, a temple); taxes, tolls at passes and bridges, levies (37.3's powers) | coin carries value with little weight, so merchants can pay at a distance; tolls make routes chokepoints |
| **E6. Calibration and acceptance** | a seeded region (§4) calibrated so that organised households and merchants put needs at or below 30% of actions while a node cut off from trade rises to about 50-60% (02b §4.2); the dependence graph between nodes measured by cutting each route | the stakes: what a route closure, a toll or a lost merchant costs |

Shelter (02e) is already built, in `cybertron2` (37.4's).

## 4. A first region (for E1-E6 dry runs and the first LLM runs)

Four nodes, three days' walk end to end, about 40 people:

| Node | People | Has | Lacks |
|---|---|---|---|
| **Millford** (market town, on a river) | 2 households and a merchant house (about 14) | the mill (water power: a big batch), the smithy, the market, a store | grain of its own, ore, much timber |
| **Barleyfield** (farm village) | 3 households (about 14) | fields, a granary | tools, metal, timber beyond fuel |
| **Ashwood** (wood hamlet) | 2 households (about 8) | timber, game, charcoal | fields; buys grain |
| **Coppergate** (hill camp) | 1 household (about 4) | a copper seam, a forge | any food |

Edges: Barleyfield - Millford (1 round), Ashwood - Millford (1), Coppergate - Ashwood (1), Coppergate - Millford by the pass (2,
with a waypoint where travellers can be stopped).

Chains: grain from Barleyfield is milled at Millford and comes back as flour or bread; copper from Coppergate, with charcoal from
Ashwood, is forged into tools at Millford's smithy; tools go back to the farms and the wood. The merchant house carries all of it
and keeps the market. Chokepoints: the mill, the smithy, the pass, the merchant house's cart and ledger.

## 5. What to measure (adds to 02a §5)

- **Load per node** (actions on needs), against the same node cut off from trade.
- **Trade volume and prices per node, and the price gap between nodes** (what a merchant earns per trip, net of carrying,
  spoilage and time).
- **Information lag:** how old each agent's knowledge of another node's prices is when it acts on it.
- **Defaults and their cost:** swaps make spot trade safe, but consignment and credit still rest on trust. Count broken
  arrangements and what they cost the victim.
- **The cut test per route:** close one edge (a flood, a toll, a lost cart) and measure each node's loss.

## 6. Open decisions

1. **Coin: carried, or moving anywhere?** 37.4's proposal says money and credit move anywhere. **Recommendation: coin is carried
   like any good; debts are records that move only as information** (in person or by letter), and settling one needs coin or goods
   to be carried. If coin teleports, a merchant never carries value home and the region's transport problem shrinks to bulky goods
   only.
2. **Merchants: seeded or emergent?** Recommendation: seed one merchant household with a cart in the first region (worlds are seeded:
   02a §6), and let anyone else trade too.
3. **Carrying capacities and weights** (§3 E4): to calibrate so that grain travels one edge at a profit and not three (Von Thünen
   between nodes).
4. **Prices: what agents see.** Recommendation: at a node, its trades of the last few rounds; elsewhere, only what they saw there or
   were told, with its age.
5. **Still open from before:** skill by practice (0.5 novice to 2.0 master, decay); the automation rule (transfers and standing
   offers free, routine work spends actions, decisions never automated); placing chokepoints by the gap between rungs (porridge 0.8,
   mill 1.6); the levers for a 2-2.5x organised advantage (02d §5b); plots whole, holdings divided.

## 7. What this needs from the other packages

| Package | Needs |
|---|---|
| 37.4 | the node and site model (what a site holds, land per node), edge lengths and transit (provisions, risk), carried letters, the calendar; where goods sit when their owner is away |
| 37.1 | households as the economic unit: head, members, ages, labour per member, inheritance of houses, plots and stock; children's work |
| 37.3 | contracts and powers ported to cybertron2: tolls, levies, grants, seizure; standing arrangements (consignment, supply) as instruments |
