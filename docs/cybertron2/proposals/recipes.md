# Proposal: recipes for the first worlds

**Status:** discussion (23 Oct). **Owner:** 37.2 (the content); 37.4 owns the verbs and the technique record (verbs.md,
knowledge.md), which these recipes are data for. **Affects:** spec/economy/production.md, goods.md, buildings.md; knowledge.md's
basic set (37.2's open question there). **Model:** [02m_recipes_model.py](../../review/37_growth/02m_recipes_model.py).

## Summary

About 40 techniques make the first worlds' goods (D2-24) from the land: 7 ways of gathering, 18 recipes, 15 building blueprints and
a handful of working methods. Each is a card for one of four verbs (`gather`, `make`, `build`, `work`): inputs, tools, workplace,
work units, output. About a third are **basic** (everyone knows them); the rest belong to **ten trades**. Costed down to the land,
the anchors are: **a coin is about a food, a day's work about 6 coin, a copper tool about 2 days, a blade about 3.5, a cart about
4.** Smelting cuts the weight to carry from 17 to 1, so it belongs at the seam; salt is boiled at the spring. Copper, tools, blades,
documents and coin travel; timber, stone, ore and grain stay near where they are got.

## The proposal

### 1. Gathering (`gather {site}`)

Yields with a crude tool; **bare hands x0.5** (and no quarrying or mining at all); **a copper hand tool x1.5** (D2-23).

| Good | Site | Units | Yield | Units a unit | A worker-day | Trade | Basic |
|---|---|---|---|---|---|---|---|
| wild food | forest, scrub (stock-limited) | 1 | 1.2 | 0.83 | 7 | forager | yes |
| meat (and a hide 1 time in 4) | forest game (threshold; parties) | 2 | 2 | 1.00 | 6 | hunter | yes |
| timber | forest | 2 | 3 | 0.67 | 9 | woodsman | yes |
| stone | a quarry | 2 | 2 | 1.00 | 6 | mason | no |
| copper ore | a seam (finite) | 2 | 2 | 1.00 | 6 | miner | no |
| hay | pasture, in summer | 1 | 3 | 0.33 | 18 | herder | yes |
| grain | fields (production.md; 02l) | per stage | | 0.59 | 10 | farmer | yes (sow, reap) |

Livestock (D2-6): **slaughter** an ox or cow (`work`, 2 units): about 15 meat and 2 hides, and the animal is gone.

### 2. Recipes (`make {what, qty}`)

| Good | Makes | Inputs | Units | Tool needed | Workplace | Full cost a unit | Trade | Basic |
|---|---|---|---|---|---|---|---|---|
| crude tool | 1 | 1 timber, 0.5 stone | 1 | | anywhere | 2.2 | | yes |
| crude weapon | 1 | 1 timber | 1 | | anywhere | 1.7 | | yes |
| pack | 1 | 1 hide, 1 timber | 1 | | anywhere | 2.7 | | yes |
| salted meat | 1 | 1 meat, 0.2 salt | 0.2 | | anywhere | 1.6 | | yes |
| trap | 1 | 1 timber, 0.25 hide | 1 | | anywhere | 1.9 | trapper | |
| salt | 2 | 3 timber (fuel) | 2 | | a salt spring or the shore | 2.0 | salter | |
| copper | 1 | 3 ore, 4 timber (charcoal folded in) | 3 | | a smithy's hearth with bellows | 8.7 | smelter | |
| hand tool | 1 | 1 copper, 0.5 timber | 3 | | a smithy | 12.0 | smith | |
| blade | 1 | 2 copper, 0.5 timber | 4 | | a smithy | 21.7 | smith | |
| coin | 10 | 1 copper | 1 | | a smithy | 1.0 | smith | |
| lock | 1 | 1 copper | 3 | | a smithy | 11.7 | smith | |
| plough | 1 | 4 timber, 1 copper | 4 | hand tool | anywhere | 15.3 | carpenter | |
| handcart | 1 | 6 timber | 3 | hand tool | anywhere | 7.0 | carpenter | |
| cart | 1 | 12 timber, 1 copper | 6 | hand tool | anywhere | 22.7 | carpenter | |
| harness | 1 | 2 timber, 1 hide | 2 | | anywhere | 4.3 | leatherworker | |
| saddle | 1 | 1 timber, 2 hides | 3 | | anywhere | 5.7 | leatherworker | |
| parchment | 4 sheets | 1 hide | 2 | | anywhere | 0.75 | parchmenter | |
| document | 1 page | 1 sheet | 1 | | anywhere | 1.75 | scribe (literate) | |

### 3. Building (`build {what, at}`)

02i's fittings re-costed without clay, fibre, iron or leather (not in the first worlds, D2-24):

| Blueprint | Materials | Units | Worker-days in all | Needs | Gives |
|---|---|---|---|---|---|
| small room, wattle and timber | 8 timber | 6 | 1.9 | a lot | a roof for 4 |
| medium room, timber on stone | 15 timber, 4 stone | 15 | 4.8 | a lot | a roof for 10 |
| hall, timber on stone | 30 timber, 10 stone | 30 | 10 | a lot; a carpenter | a roof for 25 |
| medium room, stone | 30 stone, 5 timber | 36 | 11.6 | a lot; a mason | a roof for 10; x2 defence (D2-20); can carry a storey (D2-3) |
| beds (one fitting, any number up to the room's size) | 2 timber, 1 hide a bed | 1 a bed | 0.6 a bed | a room | housed when sleeping here |
| hearth | 4 stone | 3 | 1.2 | a room | warmth (burns fuel); cooking |
| bins | 3 timber | 1 | 0.5 | a room | about 20 food at the house rate |
| benches and a table | 3 timber | 1 | 0.5 | a room | the room holds its full size for a meeting |
| shelves | 3 timber | 1 | 0.5 | a room | an archive of about 50 documents |
| lock | 1 lock | 1 | 2.1 | a room or a box | access by key |
| anvil and bellows | 6 stone, 2 hides, 1 timber | 4 | 2.1 | a hearth | a smithy |
| millstones | 10 stone | 10 | 3.3 | a room; a mason | milling by hand (if milling is in: Open 2) |
| water wheel | 15 timber, 1 copper | 12 | 5.1 | millstones; a river site; a carpenter | milling at full batch |
| cellar | 8 stone | 8 | 2.7 | a ground floor; a mason | a quarter of the spoilage (Open 4) |
| stalls (each) | 3 timber | 1 | 0.5 | a ground-floor room | stabling an animal (Open 4) |

Larger rooms cost less per person (D2-9; 02i §2b's curve); storeys cost more and need stone (D2-3).

**Beds and room size (fixed 23 Oct):** a room's size is how many people it holds, sleeping or sitting. Beds are **one fitting**
(one slot), however many: a hall for 25 can have 25 beds, each costing 2 timber and a hide, and still has its other slots for a
hearth, benches and shelves. The same room seats its size by day and sleeps its size by night (as great halls did), so a hall can be
a meeting place and a dormitory. Earlier text counted each bed as a fitting, which would have let a hall sleep only 6.

### 4. Working methods (`work {what, at}`)

| Method | On | Basic | Notes |
|---|---|---|---|
| sow, weed, reap | a plot | yes | production.md (D2-11 to D2-17) |
| hoe | a plot | yes | needs a hand tool |
| plough with oxen | a plot | no (ox handling) | a yoked ox with harness and a plough (D2-18) |
| manure | a plot | yes | dung from cattle |
| herd | animals at pasture | yes | 02l §5: one herder watches about 30 head |
| slaughter | an animal | yes | 15 meat, 2 hides |
| yoke an ox; break a horse | an animal | no (animal handling) | gives the animal its use with harness or saddle (D2-23) |
| repair | a building | yes | upkeep (H-5) |

### 5. Basic and trades (37.2's answer to knowledge.md's open question 1)

**Basic** (everyone knows): forage, hunt, fell, cut hay, sow, hoe, weed, reap, manure, herd, slaughter, make a crude tool, a crude
weapon or a pack, salt meat (given salt), build a small wattle room, bins, benches, shelves, beds, repair.

**Ten trades**, each a group of techniques a household passes on:

| Trade | Techniques | Where it sits in the first region (02f §4) |
|---|---|---|
| farmer and herder | plough with oxen, yoke an ox, (milling) | Barleyfield |
| woodsman and carpenter | plough, handcart, cart, medium rooms and halls, water wheel | Ashwood |
| trapper | traps | Ashwood |
| miner and smelter | mine ore; smelt copper | Coppergate |
| smith | hand tools, blades, coin, locks, anvil and bellows | Coppergate, Millford |
| mason | quarry stone; stone rooms, hearths, cellars, millstones | wherever the quarry is |
| salter | boil salt | at the spring or shore (one place, possibly outside the region) |
| leatherworker | harness, saddle | Millford |
| parchmenter and scribe | parchment; writing and reading (literacy) | Millford |
| horse breaker | break a horse | where wild herds are (D2-6) |

### 6. Skill, wear and the levels

- **Levels** (knowledge.md §4c): aware, rough idea, capable, known. **Skill** within "known" follows the practice curve (02c §5):
  shown as novice, competent, skilled, master; it raises gathering yields and cuts the units of making, up to about x1.5 and x0.7.
- **Wear:** a crude tool 10 uses; a copper hand tool 40; a plough 60; a trap 20 nights; harness 80 days, saddle 160, pack 60. **A
  crude weapon lasts about 3 fights and a blade about 10** (the engine as built uses a weapon up in every fight: Open 5).

### 7. What the costs say

- **Copper tools now pay well:** on a fell, a copper tool gives about 1 unit more timber a use for 0.08 more wear than a crude one,
  so it repays its 12 units in about 12 uses. (02j found copper tools weak against crude ones because it gave them x1.0 against
  x0.8; with copper the only metal (D2-19), it is the step up.) **That makes the smith a chokepoint** for every gathering trade.
- **Where steps belong (Weber):** smelting turns 17 weight of ore and fuel into 1 of copper, so it happens at the seam, and only
  where there is wood too; salt (6 weight of fuel into 2) at the spring.
- **What travels (Von Thunen):** full cost per unit of weight: timber, stone and ore about 0.3; grain 0.6; meat and hides 1; salt 2;
  copper 8.7; tools 12; blades 22; documents 35; coin 97. On foot an edge costs about 0.9 units per unit of weight (02g §3), so
  timber, stone, ore and grain stay within a node or one edge; **salt needs pack animals or a cart to go far**, which gives the
  transport ladder a job; copper, tools, blades, documents and coin travel anywhere.
- **Price anchors** at about 1 unit a food: a coin about 1 food; a day's work about 6 coin; salt 2; copper 9; a hand tool 12; a
  plough 16; a blade 22; a cart 23; a page 2.

### 8. Tools by method: what a tool changes, and what it cannot (23 Oct, b)

**A tool never adds to a site's stock.** Where the land holds a stock (plants, game, a forest's timber, a seam), a better tool takes
the same stock faster: more per unit of work, and the site runs down sooner (copper axes speed deforestation). Where the source is
endless (a quarry, a salt spring) or is a plot's soil, it simply cuts the work. One hand tool good (D2-23), with an effect that
differs by method (data on each method's card):

| Method | Bare hands | Crude | Copper | Wear a use | Draws on | Why |
|---|---|---|---|---|---|---|
| forage | x1 | x1 | x1 | 0 | plants (stock) | picking by hand: no tool helps (a pack helps carry) |
| fell | x0.25 | x1 | **x2** | 1 | forest timber (slow stock) | metal axes cut about twice as fast as stone ones (experimental archaeology: steel about 3x) |
| quarry | none | x1 | x1.5 | 2 | a quarry (endless) | wedges and hammers; hard on tools |
| mine | none | x1 | x1.5 | 2 | a seam (finite) | picks; no tool, no mining |
| cut hay | x0.3 | x1 | x1.5 | 0.5 | pasture | sickle or scythe |
| hoe | x0.5 | x1 | x1.5 | 1 | the plot's soil | breaking ground |
| reap | x0.6 | x1 | x1.5 | 0.5 | the crop | a sickle |
| hunt | x0.3 | x1 (spear) | x1.3 (blade) | 0.3 | game (threshold stock) | the weapon, a separate good |

**Is a copper tool worth it?** For a household of 5 in a 40-day year (felling 24 units, hoeing 72, reaping 36, hay 4): it saves
about 49 units a year (8 worker-days), and wears out about one tool a year (11 units) against 12.6 for the crude tools it replaces.
**It pays back in about 10 days of use.** So every household should want one, and the smith is the chokepoint.

**Is it worth having different tools (an axe, a pick, a sickle) instead of one?** Not as separate goods. Wear is per use, so four
tools cost the same per use as one; they only add a fourfold purchase up front and four goods to list. The heterogeneity that
matters, how much a tool helps each kind of work, is kept as data on each method. Separate goods are justified only where the
dependence differs: the plough (an ox), weapons (force), traps (work while away), harness and saddle (animals).

### 9. Weapon wear from one wear scale

The engine as built uses a weapon up in every fight: about 22 units for a blade, more than three days' work per fight. A principled
alternative: **one wear scale for every tool.** A tool's life is counted in standard uses (about 2 units of work); each method has a
wear factor (above: reaping 0.5, felling 1, mining 2). A fight is heavy use: **factor 4**. A copper blade then lasts 40 / 4 = **10
fights**; a crude weapon (10 uses, factor about 3) lasts **3**. The factor 4 is the one choice; it sits at twice mining's. A smith
can mend a worn blade for less than a new one (about 1 unit and a fifth of a copper). Alternative: a chance of breaking per fight,
higher for the losing side.

### 10. Bread (Zach: slightly better; keeps meaningfully longer)

| Step | Recipe | Work |
|---|---|---|
| porridge | grain eaten at a hearth | none beyond the hearth (as now) |
| flour by hand | a quern (basic: stone): 4 grain an unit of work | about 0.25 units a ration |
| flour at a mill | millstones turned by hand: 12 grain a unit; with a water wheel: 40 a unit | 0.08 or 0.025 a ration |
| bread | 10 flour, 1 timber, 1 unit at a hearth: **11 bread** | a batch |

- **Better in three ways:** a little more food (11 loaves from 10 grain: grain plus water); **eaten anywhere, without a hearth**
  (travel, the fields, a raid, a market day), while grain must be cooked at a hearth; and **keeps about 5% a day carried**, against
  15% for wild food and 30% for fresh meat (grain in a store keeps better still).
- **By hand it is not worth it for eating at home** (0.25 units of grinding a loaf for a tenth more food); **at a mill it is**, and
  it is always worth it for travel. That makes **the mill a chokepoint** (whoever holds it can charge a share of the grain, as mills
  did), and bread the merchant's and the traveller's food, with salted meat.

### 11. Meat and milk (decided: D2-41, D2-42)

- **Meat** (D2-41): from the hunt and slaughter; **one meat feeds 1.5** (dense food), but fresh meat loses about 30% a day; salted,
  2%. A slaughter (15 meat) feeds a household for days or a feast for many at once.
- **Milk** (D2-42): a technique (milking), not basic: an agent must learn or try it (knowledge.md). It needs **a cow in milk** (one
  that has calved this season) at the node and fed; 1 unit a day gives about 3 milk (0.5 food each), which spoils within the day.
  **Cheese** would keep it (6 milk, 0.2 salt, 1 unit: 1 cheese worth 2 food, keeping like salted meat), a second use for salt (Open).

### 12. Cellar and stalls: what they are for

- **A cellar** (8 stone, a mason): a stone storeroom on the ground floor where food (grain, meat, cheese, bread) loses a quarter of
  what it loses in the house. 02j: it pays only for a large store (a village granary), not a household's.
- **Stalls** (3 timber each, a ground-floor room): an animal housed for the winter **eats less fodder** (it is out of the cold),
  **its dung is kept** for the fields (manure), and it is **safe from rustling** behind walls and a lock. Horses and oxen alike.

### 13. The worth of things (what agents should rationally want)

A year's worth against a year's cost (capital written off over its life, plus upkeep), in units, for a household and at scale:

| Thing | Cost a year | Worth a year, household | Ratio | Worth a year, at scale | Ratio | Basis |
|---|---|---|---|---|---|---|
| hearth | 0.7 | 25 | 36 | 25 | 36 | winter without it: x1.5-2 food and the cold (H-5) |
| copper hand tool | 10.9 | 49 | 4.5 | 49 | 4.5 | §8 |
| beds for 5 | 2.5 | 10 | 4.0 | 10 | 4.0 | housed sleep (02e) |
| stalls for 2 oxen | 1.0 | 4 | 4.0 | 4 | 4.0 | §12 |
| bins | 0.5 | 1.5 | 3.0 | 1.5 | 3.0 | 02j |
| salt for 2 slaughters | 12 | 24 | 2.0 | 24 | 2.0 | keeps 30 meat |
| lock | 1.3 | 2 | 1.5 | 8 | 6.2 | the theft it stops: much on a store or treasury |
| plough and ox | 11.7 | 6 | 0.5 | 60 | 5.1 | 02l: a village shares the herd |
| cellar | 1.1 | 0.4 | 0.4 | 5 | 4.7 | 02j: a granary |
| trap line of 6 | 19 | 7 | 0.4 | 7 | 0.4 | barely beats foraging at full plants; pays where plants are short |
| cart | 5.7 | 0 | 0 | 60 | 10.6 | 02g: a merchant's |

- **The household wants:** a hearth, beds, a copper tool, bins, salt when it slaughters. **The village or a specialist wants:**
  the herd and ploughs, a granary cellar, locks on stores, carts. So the things that pay at scale are what institutions and
  specialists are for.
- **Traps barely pay** at these numbers; they become worth it where plants are short or game is close to home.
- **A thing to check later, not a finding yet:** 37.4's first one-node tests of the M1 slice (38.12: two households, food and fuel
  only, none of these recipes) had food at 85-90% of work, read there as nothing else being worth units. That says little about
  this catalogue; when multi-node runs have these goods, check whether slack goes to them, and whether agents also need things
  valued for themselves (comfort, safety, standing).

### 14. Milk and cheese: what they do that other food does not

| | Milk | Cheese | Against other food |
|---|---|---|---|
| **where it comes from** | a living animal, daily, without killing it | milk, salt and time | meat ends the animal; grain needs a plot, seed and a season |
| **what it turns into food** | grass, on land that grows no grain (hills, moor, grassland) | the same, stored | wild food is stock-limited; grain needs arable land |
| **keeping** | the same day | like salted meat (about 2% a day) | |
| **carrying** | not at all | high value per weight | |

- **Milk is interest; meat is principal.** A herd that is milked feeds people every day and stays a herd; a slaughter feeds many
  once and the animal is gone. That makes a herd a capital good that pays a return, so cattle can be lent, rented and given as
  bride price for what they yield (02g §2), and wealth in cattle differs from wealth in grain.
- **It makes pasture nodes food-producing.** Hill and grassland households live on milk where no grain grows, and are tied to
  their herds, because milk must be drunk where the cow is.
- **Cheese is how pastoral land exports food and gets through winter:** it turns the summer's milk (cows give less in winter) into
  a store that keeps and travels, and it is **salt's second use**, so a cheese-making node must trade for salt. The hills then sell
  copper and cheese; the valleys sell grain and bread.
- **Recommendation: add cheese now** (6 milk, 0.2 salt, 1 unit, a cool room or a cellar to age it: 1 cheese worth 2 food). It
  passes the pruning rule on two counts: it changes shelf life enough to move where things happen, and it creates a trade (salt
  in, cheese out).

### 15. Specialised tools

Above the base hand tool, a few **specialised tools**: each a known recipe (a master smith's technique, not basic), made at a
smithy with more copper, **better at one method, longer-lived at it, and able to do one thing the base tool cannot**. At other work
it is no better than a crude tool.

| Tool | Method | Cost (units) | Better than the copper hand tool | Life | What it alone can do | Pays back: household | Pays back: full-time specialist |
|---|---|---|---|---|---|---|---|
| felling axe | fell | 22 | x1.5 | 80 uses | fells great trees: the great beams a hall for more than 25 needs (02i §2b) | 2.7 years | 14 days |
| miner's pick | mine | 22 | x1.33 | 80 | works a deep seam that hand tools cannot | never | 18 days |
| scythe | cut hay | 21 | x1.67 | 80 | one person cuts a pasture's hay inside the summer window | 13 years | 11 days |
| mason's chisels | quarry | 13 | x1.33 | 80 | dressed stone: millstones, arches, a third storey (D2-3) | never | 8 days |
| reaping hook | reap | 12 | x1.33 | 80 | loses less grain: +10% of the harvest brought in | 1 year | 7 days |

**Why it is relevant:**
- **It makes specialisation pay for itself.** A specialised tool repays a full-time specialist in one to three weeks, and a
  household in years or never. So the woodsman, the miner, the mason and the herder buy them; the household keeps one hand tool.
  Tools then deepen the division of labour, as in Smith's pin factory, instead of every household doing everything a little better.
- **The qualitative abilities are chokepoints.** Great beams, deep seams, dressed stone and millstones exist only where a
  specialist with the right tool does the work, and the tool exists only where a smith knows the recipe. That ties the mason, the
  miner and the woodsman to the master smith.
- **It gives smithing depth:** a novice smith makes hand tools; a master makes these (knowledge.md's levels), so a master's
  know-how is worth teaching and paying for.

**Great trees: where they are and how agents see them (proposal, with 37.4, who owns land).** A forest site holds two stocks:
ordinary timber, and **a few great trees** (old growth: old oaks in a woodland, very slow to come back, so effectively finite in a
run). They appear in the forest's description ("the Deep Wood: thick, with a stand of old oaks"), as everything at a site does.
Felling one takes the felling axe and two or three people for a day, and gives **a great beam**: very heavy (a cart and oxen to
move it), used for a hall's span. Clearing or felling the stand ends it for generations (D4-4: an internal consequence). So
the great hall depends on a woodland that still has old oaks, a woodsman with a felling axe, a master smith who made it, and oxen
to haul the beam.

**What it costs the design:** five more goods, each with one use, against the pruning rule (02g §1f). They pass it on one test
only, but the important one: each creates a dependence (specialist on master smith) and an ability nobody else has. Five is enough;
more (a dozen tool kinds) would add goods without adding new dependences.

### 16. The food ladder: investment for upside (23 Oct, proposal; would replace D2-44's figures)

Zach: bread at 1.1 adds almost nothing; capital and labour should buy real upside, and farms must be able to eat without a mill.

| Eaten as | Food a grain | Units a food (hoe) | Units a food (ox plough) | Needs |
|---|---|---|---|---|
| whole grain, boiled at home | 0.7 | 0.77 | 0.60 | a hearth |
| porridge from a hand quern | 1.0 | 0.74 | 0.62 | a quern |
| porridge from mill flour | 1.0 | 0.57 | 0.45 | a mill |
| bread, baked at a hearth | **1.3** | 0.51 | 0.42 | mill flour, a hearth |
| bread, from a bakehouse oven | **1.3** | 0.46 | **0.37** | mill flour, a stone oven (batches of about 40) |

- From a hoe household eating whole grain to an ox-ploughed, milled, oven-baked loaf: **about 2.1 times the food per unit of work.**
  Each investment adds: the plough and team, the mill, the oven.
- **Bread also keeps** (about 5% a day) **and is eaten without a hearth**, so it is the town's and the traveller's food.
- **Farms eat without a mill:** whole grain, legumes, milk, cheese, meat and a garden.
- The oven returns as a fitting (stone, which fields now yield: D2-56).

**Food that travels on foot** (units of work to carry one food one edge; a milled ration costs about 0.45):

| Food | On foot | Pack ox | Ox cart |
|---|---|---|---|
| grain | 0.92 | 0.19 | 0.074 |
| bread | 0.71 | 0.15 | 0.057 |
| salted meat | 0.61 | 0.13 | 0.049 |
| cheese | 0.37 | 0.08 | 0.030 |
| dried meat (proposed: meat dried to half its weight) | 0.31 | 0.06 | 0.025 |

Bulk grain needs a pack animal for an edge or a cart for two or three; **dense food (cheese, cured meat) travels on foot.** A town
a few edges from its farms is fed by carts and cured food, as historically.


- Each good in D2-24 has a reason to be made, a place it is made and a reason to travel; no good is single-use (02g §1f).
- Interlocking chokepoints (scenario_design): the seam and the smithy (copper, tools, blades, coin, locks), the spring (salt), the
  quarry and the mason (stone, hearths, cellars, millstones), the scribe (documents), the ox (ploughing).
- The cards fit 37.4's verbs and technique record with no new verb.

## Alternatives considered

- **Charcoal, planks, leather as goods:** folded into recipes (02g §1f).
- **02i's fittings with clay, fibre and iron:** re-costed in the first worlds' goods.
- **Copper tools left out** (02j's suggestion): rejected here: copper is the only metal, so it is the tool step.

## Open questions (for Zach)

Answered 23 Oct: meat (D2-41); milk (D2-42); the basic set and trades (D2-43); bread (D2-44); cellar and stalls (D2-45); weapon wear
(D2-46); cheese (D2-47); specialised tools (D2-48).

**Reading the payback columns:** "2.7 years" means a household felling as much as it usually does (about 12 fells a year) would
need 2.7 of the world's years of that felling before the work the axe saves covered what it cost. The model's year is 40 days (a
world setting, 16-60 days: D4-13), so 2.7 years is about 108 days, longer than a run of 20-30 days: for a household it never pays
within a run. A full-time woodsman's 14 days is within one.

1. **Tool effects by method** (§8) as the base level: the one hand tool good helps different kinds of work by different amounts
   (felling x2, quarrying, mining, reaping and hay x1.5, foraging not at all), with the specialised tools above it?
2. **Great trees and great beams** (§15): a separate small stock in woodland, seen in the forest's description, felled only with a
   felling axe and a small crew, giving one very heavy beam (37.4: land and sites)?
3. Food's share of work: the open calibration.

## History

- 22 Oct: 02j costed the end uses with roots and recipes (in old-engine actions); 02g §1f pruned the goods and fittings.
- 23 Oct: D2-24 fixed the first-world goods. Zach: work on recipes. Written: the catalogue in 38.06's work units for 37.4's verbs,
  basics and trades, tool grades and wear, re-costed fittings, weight and travel, price anchors.

- 23 Oct (b): Zach: tools for every method, differing by resource; do tools take more from capacity or create from nothing; meat
  yes; bread slightly better and keeping longer; milk now if they learn it; what cellar and stalls are for; how the weapon number
  was got; more analysis of the worth of things and of different tools. Added §8-§13; decisions D2-41 to D2-43.

- 23 Oct (c): Zach: bread as described (D2-44); what milk and cheese do that other food does not; cellar and stalls in (D2-45);
  weapons wear, with a smaller chance of breaking (D2-46); could specialised versions of tools be crafted from known recipes, at a
  forge, lasting longer and doing better at one thing, with a qualitative bonus? Added §14 (milk and cheese) and §15 (specialised
  tools, with when each pays back).

- 23 Oct (d): Zach: cheese yes (D2-47); specialised tools yes (D2-48); how agents see great trees; what "2.7 years" means.
  Added great trees and beams to §15 and the reading of the payback columns.

- 23 Oct (analyses): [02n](../../review/37_growth/02n_labour.md) and [02p](../../review/37_growth/02p_chains.md): with bread only
  (D2-44 as decided) the mill never pays (a loaf's grinding costs 0.19-0.42 units for 0.055 more food); if all grain must be ground
  (quern 0.2-0.25 a ration, hand millstones 0.08, water mill 0.025) a mill pays from about 2 people, a toll of 3-5% covers it at
  15, and it is a real chokepoint (rent about 2.6% of a region's work). Proposed revision of D2-44 for Zach. Also from 02p:
  charcoal back as a good (made at the wood, 5 times lighter than its timber; Coppergate has no wood); cheese at 2.5 food from 6
  milk (it loses a third at 2); beds of timber and straw, not hides (a hall's 25 beds took 12 slaughters' hides); hearths needing 4
  stone tie every house to a quarry (fieldstone from fields, or a quarry in every settled kind); shore salt sun-dried, inland
  springs boiled; tools worth 3-8x their cost, so prices are bargained among few smiths; the copper seam the dominant chokepoint
  (about 14% of the region's work at a monopoly price); striking coin nearly free (a stamp later).

## Sources

[02m_recipes_model.py](../../review/37_growth/02m_recipes_model.py), [02j](../../review/37_growth/02j_end_uses.md),
[02g §1f, §3](../../review/37_growth/02g_resources_and_transport.md), [02i §2-3](../../review/37_growth/02i_buildings.md),
[02l](../../review/37_growth/02l_farming.md), [verbs.md](verbs.md), [knowledge.md](knowledge.md), 38.06 §3; D2-3, D2-6, D2-9,
D2-18, D2-19, D2-20, D2-23, D2-24.
