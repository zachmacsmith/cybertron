# 02zc: the systems of cybertron2 as they stand

Session 37.2, 29 Oct 2026, for Zach. One entry per system, eight fields each. These are facts from the engine (`cybertron2/engine/`, read on 29 Oct),
the spec and the run reports 38.22 to 38.36 and the devlog. Where there is no evidence the entry says "unknown" or "not yet observed".
Run keys: 38.22 (hamlet and two valleys), 38.23 (region), 38.24 (Packages A and B), 38.25 (C), 38.26 (r1 region), 38.27 (D, bot
dry run), 38.28 (F), 38.30 (h2 Hollins), 38.31 (w1 Wide Country), 38.36 (memory tests on w1).

Most runs so far predate Package F (forests, 23 to 24 Oct). Behaviour in 38.22 to 38.26 was shaped by fuel shortages that F
removes, so it is not a guide to the present engine. Only h2 (41 days) and w1 (24 good days) ran on the current fuel rules.

## 1. Weather and seasons

- **What it does:** each day's weather is drawn within a spell for the season; it sets cold nights, rain, lying snow, and how far
  sight and sound carry at each place. A year is 24 days in four 6-day seasons, and winter is cold.
- **Leverage:** nobody controls it. It rewards whoever stored fuel and food before winter, and that converts into leverage over
  those who did not, through hosting, sale and credit.
- **Information:** every prompt states today's weather and whether it is cold. Coming days and the spell are not shown. Visibility
  and loudness are hidden values, felt only through what one notices.
- **Scarcity:** seasonal, set by the calendar in the world data:
  - a person's work units fall from 7 in spring to 5 in winter;
  - a hearth needs 4 heat on a cold night against 1 on a normal one.
- **Persistence:** agents cannot affect it.
- **Interactions:** it feeds fuel need, work units, crop growth, decay of goods left in the open, trouble at fords on the roads, and
  noticing (visibility and sound).
- **Behaviour observed:**
  - in 38.22 agents prepared at the frost: sowed rye, moved hay to the byre and mended houses;
  - in 38.23 the first cold night put out every Barleyfield house's fire and 11 died in three days;
  - in 38.31 a seeded custom of exploring gave way in winter.
- **Status:** implemented (D2-69, D2-99 to D2-103).
  - Blight is the only incident; floods, gales, drought, disease and fire are flagged for later.
  - Before Package F, winter was the main killer in every multi-village run.

## 2. Land and the parcel graph

- **What it does:** a node's land is parcels (field, pasture, meadow, forest, scrub, built ground, water). Each parcel has
  neighbours, a side and a height; there are no coordinates and no walking inside a node.
- **Leverage:** the parcels a household holds (fields, woods, pasture) are the base of all its production.
  - Gained by claiming and by clearing (D4-60).
  - Lost by losing the claim or by degrading the ground (a felled wood becomes scrub).
- **Information:** agents get an overview of the village on arrival and sense along the parcels they work that day. Stocks (trees,
  game, soil) are shown only through signs.
- **Scarcity:** parcels per node are fixed by the world file; clearing adds fields at a labour cost.
- **Persistence:** clearing, fencing, ditching, terracing, felling and grazing all change a parcel for good.
- **Interactions:** it carries agriculture, livestock, forests, wild food and claims, and sets noticing (the day's chain of parcels).
- **Behaviour observed:**
  - in 38.31 the Rooks cleared the Glade into a field, then claimed and fenced it, and Gunnild Reed cleared Fen Meadow;
  - in 38.26 Coppergate's 20 timber stood on scrub, where felling is not allowed (a world-design error);
  - before the graph, 40% of actions went on walking between sites (devlog).
- **Status:** implemented (D2-114 to D2-116, D4-60, layout.py). Ground has no space limit for buildings yet (Package E deferred).

## 3. Perception and noticing

- **What it does:** each morning an agent hears what concerned it and the most salient of what happened, attends to one target in
  detail, and notices things by one rule: conspicuousness × visibility × presence × attention × eye × traces.
- **Leverage:** noticing first gives first access (a cache, a stray herd, a body, a theft). The eye for the land rises with
  practice at hunting and foraging, so it accumulates and dies with the person.
- **Information:** this system *is* the information layer. Nobody sees stocks, others' stores, odds or hidden values directly, only
  signs of them.
- **Scarcity:** attention: one attended target a day and about 4 noticed items (38.26). It is tuned by base chances in signs.py and
  presence and visibility in data.py.
- **Persistence:** traces and things left lie for days; an agent's eye persists.
- **Interactions:** it carries the information of every other system and depends on weather, the parcel graph and things in places.
- **Behaviour observed:**
  - 38.22: signs pointing at a job (weeds, standing water, ripeness) were acted on; signs of animals' condition were not;
  - 38.24: a cache under brush was noticed by two people and left alone;
  - 38.25 c4: herds trampled a field at night unnoticed;
  - 38.26: 7% still worked a parcel the day after seeing it bare, and a death seen was acted on the next day in 79 of 131
    agent-days.
- **Status:** implemented (perceive.py, signs.py, things.py; D2-85, D2-99, D4-48, D4-53, D4-59). Faults found in runs were fixed:
  - everyone seeing the trampled-field lines;
  - a mother not told of her birth (17a8cda).

## 4. Agriculture

- **What it does:** fields, counted in plots, are sown, broken by plough or hoe, weeded, manured and reaped. Yield follows seed,
  the broken share, weeding, weather and blight. Dibbling, ditching and terraces raise it.
- **Leverage:**
  - the ox plough and know-how (ditching, dibbling) multiply output;
  - grain converts into wages, hosting and credit (Barleyfield hired reapers in 38.23);
  - an ox can be eaten, turning capital into food (the Millers, 38.22).
- **Information:** crop state shows only through signs. Yields and the odds of blight are hidden.
- **Scarcity:** plots per node, seed, oxen and work. A plot takes about 23 units with an ox plough and 35 by hoe. Worlds are seeded
  at 60 to 70% of what their land gives each year (D2-161, capacity.py).
- **Persistence:** manure, ditches, terraces, fallow, cleared fields and kept seed carry over.
- **Interactions:** it feeds food and exchange; it depends on livestock (plough, manure, trampling), fuel (grain must be cooked),
  labour and children's work.
- **Behaviour observed:**
  - 38.22: full harvests, with ditching led by the one who knew how;
  - 38.30: the Thornes ploughed 61 times, manured 95, weeded 49 and sowed 48;
  - 38.28: bots died because they do not sow.
- **Status:** implemented (farm.py; D4-38 to D4-40). Known problem: the mill was not a chokepoint, because every large house had a
  hand mill (38.22).

## 5. Livestock and herds

- **What it does:**
  - herds graze, breed and give milk, calves, meat, manure and ploughing;
  - unherded beasts wander up to 8 steps a night, split by how many can be watched, and stray onto roads;
  - fences and gates stop them;
  - an ox can be led as a pack ox carrying 60.
- **Leverage:** oxen are the plough and the pack ox (6 times a carrier's load) and few households hold them. Herds grow by
  breeding and are lost by straying, theft, starvation or slaughter.
- **Information:** owners see where their herd is and its condition through signs. Strays are found by noticing and hoof marks.
  The odds of wandering are hidden.
- **Scarcity:** beasts, pasture and winter hay, set in the world file.
- **Persistence:** fences (wood weaker than stone), herd size and trampled crops last.
- **Interactions:** it feeds agriculture, transport, food, roads, claims and theft.
- **Behaviour observed:**
  - 38.25 c6 and c7: after herds trampled North Field, households fenced it, set a herder on guard, warned each other and drove
    the beasts home;
  - 38.26: the Merchants' ox strayed and a search followed: Elias tracked hoof marks, Everard offered 3 coin for news, Rohese found
    it at Ashwood;
  - 38.30: the Thorne cattle began to starve by day 40.
- **Status:** implemented (herds.py, farm.py; D2-117 to D2-132, D4-41 to D4-45, D4-58).
  - The pack-ox fault is fixed (4ad63cc, 8099eef).
  - Agents do not act on signs of animals' condition (38.22).

## 6. Forests and fuel

- **What it does:** forest and scrub hold three stocks: trees, young growth and dead wood.
  - Felling gives timber; gathering gives firewood; cutting young growth with a tool gives firewood.
  - Timber burns into charcoal (6 heat for the weight of one timber).
  - A hearth burns firewood first, then timber, then charcoal.
- **Leverage:** villages with woods hold fuel that others need to cook and survive winter. Charcoal lets distant forest holders
  sell at a third of the weight. Felling a wood out turns that leverage into a one-time stock.
- **Information:** stocks show through signs (felling, scrub, firewood: D4-59); regrowth and shedding rates are hidden.
- **Scarcity:** set by each wood's kind and size against what it sheds and regrows each year, checked by capacity.py (D2-161).
- **Persistence:** strong. Felling turns forest to scrub and cuts what it sheds; grazing stops young growth.
- **Interactions:** it feeds fire, cooking, buildings, transport (weight), exchange and children's work (firewood), and holds game
  for wild food.
- **Behaviour observed:**
  - before Package F every run stripped its near woods (Hollow Wood 55 to 0.25 in 38.22; Deep Wood's 441 felled out by day 20 in
    38.26) and lack of fire caused most deaths (38.23: 27 of 51 died; 38.26: 12 of 17 died with food in reach and no fire);
  - after F, h2 had 1 unlit hearth-night in 41 days, with 145 Thorne firewood actions.
- **Status:** implemented (Package F, forests.py; D2-156 to D2-161). Open: poles from young growth (forests Q4).

## 7. Wild food

- **What it does:** foraging and hunting draw on pools of plants and game per parcel. The pools regrow, but game does not come back
  below 15% of capacity. A hunt succeeds by chance, better armed.
- **Leverage:** small. It is open to anyone without tools; the eye for the land rises with practice.
- **Information:** pool levels show through signs ("few fresh tracks") and refusals on picked-bare land.
- **Scarcity:** pool sizes per cover and the 0.15 game threshold, in data.py.
- **Persistence:** overhunting ends game in a wood for good (Hollow Wood, 38.22).
- **Interactions:** it feeds food and depends on forests and perception; travellers can gather on the road.
- **Behaviour observed:**
  - 38.23: near wild food was picked bare by day 5, with 321 refusals on bare land in 20 days;
  - 38.30: Osric and Wymond hunted at Fern Hollow and brought meat home;
  - 38.36: memories record the Carr hunted out and Payn going west for game.
- **Status:** implemented. Known problem: agents keep trying on bare land.

## 8. Food, cooking and hunger

- **What it does:** each person eats a meal a night from what they carry or their household's store.
  - Grain and flour need a fire; bread and some foods are eaten raw, some at less worth, some not at all.
  - Goods spoil by kind and condition; missed meals lead to hunger and death.
- **Leverage:** food stores convert into wages, hosting, credit and gifts. Withholding food is leverage: Ancel stopped the Reeds'
  gifts in 38.23.
- **Information:** one's own hands and household store are shown; others' stores are hidden except through talk and signs.
- **Scarcity:** set by farm yields, wild pools and the capacity check. The design aim is food at 30% of actions or less; the actual
  share since Package F is unknown. It was 85 to 90% of work in an early pair (devlog).
- **Persistence:** stores carry over and spoil.
- **Interactions:** it depends on agriculture, livestock, wild food and fuel, and feeds exchange, hosting and travel.
- **Behaviour observed:**
  - 38.23: people died beside full stores (Barleyfield held more than 100 grain and no fire);
  - Emma (Haiku) said "I carry 8 grain, enough to eat tonight" and died;
  - 38.26: the Coles died with 55 meals in store;
  - 38.30: Agatha starved alone on a journey carrying 4 grain.
- **Status:** implemented, with eating raw added after the region deaths. Known problem: Haiku agents did not connect fire with
  meals (38.23).

## 9. Shelter, fire and hosting

- **What it does:** a person sleeps in a bed at home or as a guest, at a camp, or in the open.
  - A hearth needs 1 heat a night (4 when cold) and warms 12 spaces.
  - A fire in the open is shared by up to 4.
  - A cold night without a fire is hard and can kill.
- **Leverage:** a household with a lit hearth and free beds can save or refuse lives; beds and a fire were paid as wages (reapers,
  38.23).
- **Information:** an agent sees its own building's fuel and what the fire takes tonight; others' fires show as smoke and light.
- **Scarcity:** fuel and beds, set by the world file's buildings and woods.
- **Persistence:** buildings fall into disrepair without timber.
- **Interactions:** it depends on forests and buildings, and feeds food (cooking), households, travel (sleeping out) and life (cold
  deaths).
- **Behaviour observed:**
  - 38.23: hosting at a lit fire saved lives but was rarely given; Thurstan died the night before the Reeds took in his son;
  - 38.26: hosting on 66 nights;
  - 38.24: arriving travellers asked for a bed and food at a lit hearth.
- **Status:** implemented (night.py; D4-49, D2-159). Known problem: household members sleep at home whatever the beds, so beds bind
  only guests.

## 10. Buildings

- **What it does:** a building is rooms of one structure (wattle, timber or stone) with fittings (beds, hearth, bins, quern, anvil,
  cellar and others). It is built from materials and days of work, and decays without repair.
- **Leverage:**
  - some fittings are chokepoints for production: an anvil for smithing and coin, millstones;
  - a stone structure makes a raid slower to finish (more time to respond);
  - a house decides who sleeps warm.
- **Information:** agents see the buildings at their node; what is inside others' buildings is hidden.
- **Scarcity:** timber, stone and work. Ground, floor space and storage are unlimited.
- **Persistence:** buildings last and decay.
- **Interactions:** it feeds households (home), raids (the structure sets how long a raid takes), fire, storage and speech (talk in
  a building reaches those inside), and needs claims to the ground.
- **Behaviour observed:**
  - houses mended at the frost (38.22);
  - the Fenwicks built a cellar and then a new house at Stannick (38.31), the only new building in any report.
- **Status:** partial.
  - The prompt lists a building only when one holds its materials.
  - A fitting goes in with one 2-unit action whatever its listed work (bug, unfixed).
  - Space, storage limits, extension and stone blueprints are not built.
  - Package E is deferred until Zach says otherwise.

## 11. Crafts and know-how

- **What it does:** each technique has four levels (aware, rough, capable, known). One rises by watching, by trying, or by a day of
  teaching. Recipes turn inputs into goods, some only at a fitting.
- **Leverage:** knowing a trade is a monopoly until one teaches it. It can be traded as teaching, and is lost with the person.
- **Information:** agents see their own know-how and what they have seen or been told of others' (seeded by generate.py).
- **Scarcity:** who knows what at the start, ore (copper) and fittings.
- **Persistence:** know-how lasts and spreads by teaching.
- **Interactions:** it feeds every production chain, tools for exchange, and buildings (a hearth or an anvil takes a trade).
- **Behaviour observed:**
  - copper tools were made and taught: 7 teachings in 38.23, 8 in 38.26;
  - the smith was idle where there was no ore (38.22);
  - Simkin bought a copper tool for 8 grain (38.25).
- **Status:** implemented (knowledge.py; D4-24, D4-33). Withholding a craft for advantage: not yet observed.

## 12. Exchange and money

- **What it does:** an offer names what one gives and gets, to one person or to anyone present, in lots. Accepting settles the
  parts due now, both or neither. Coin is struck from copper at an anvil (10 a copper).
- **Leverage:**
  - holders of what others need set terms;
  - whoever has an anvil and copper can mint;
  - carriers between villages (a pack ox, a handcart) hold the trade between them.
- **Information:** open offers are seen by those present. There are no posted prices and no market across nodes; distant prices
  are learned only by travel and talk.
- **Scarcity:** that of the goods; coin from the seeded stock and copper.
- **Persistence:** none beyond holdings.
- **Interactions:** it depends on every production system and on transport, and feeds agreements.
- **Behaviour observed:**
  - 38.22: Opus agents made about 9 offers each and closed about 3, and prices formed only late, by bidding;
  - 38.23: the planned grain-for-timber trade did not form;
  - 38.26: 206 offers and 71 accepted, typically 2 to 5 timber for about as much grain;
  - 38.24: at a ford Simkin bought 1 timber for 2 coin from a traveller he met.
- **Status:** implemented (agreements.py). Markets exist only as seeded customs (D2-30), with no market place or day in the engine.

## 13. Agreements, credit and hiring

- **What it does:** an agreement can hold later legs: a promise by a day, payments every n days, or days of work. The engine pays
  them when payer and payee are at one node and the goods are there; otherwise they fall into arrears, shown to both. A creditor
  can release a debt.
- **Leverage:** credit and wages turn stores into others' labour, and arrears are a hold on a debtor. Beyond paying when it can, the
  engine enforces nothing; there is no law or court.
- **Information:** both parties see the agreement and arrears; third parties do not unless told.
- **Scarcity:** not applicable.
- **Persistence:** agreements and arrears last until paid or released.
- **Interactions:** it depends on exchange and households (agreements made for a household), and feeds labour in farming and
  carrying.
- **Behaviour observed:**
  - 38.22: 29 agreements in the two valleys (27 done), including credit across the road;
  - 38.23: 46 agreements, with hired reapers paid what was owed;
  - 38.26: 72 agreements;
  - 38.31: a quarter-share reaping deal, and the lesson in memory that "work must be written 'work 2 days'".
- **Status:** implemented (D2-25 to D2-40). Deliberate default on an agreement: not yet observed.

## 14. Roads and transport

- **What it does:** a road is one stretch a day, each with a terrain and up to two landmarks (ford, bridge, pass, narrows, spring,
  good places).
  - A crossing can give trouble; the traveller chose beforehand to push on, wait, turn back or go round.
  - Travellers meet as fuse events, with up to three rounds of talk and trades.
  - Finds, traces and hidden ways lie along the road.
  - Loads: foot 10, pack 20, handcart 40, pack ox 60.
- **Leverage:** carrying links villages that need each other. Knowing a hidden way, and holding a pack ox or cart, is leverage over
  those who cannot carry.
- **Information:** agents know the roads and places they have learned of; other places are known only as last seen or told.
- **Scarcity:** carrying capacity, days on the road, and food and fire carried.
- **Persistence:** traces and things left on roads last for days. Roads do not change.
- **Interactions:** it feeds exchange, speech (messages are carried), herds (strays), noticing (meetings, finds) and weather
  (fords).
- **Behaviour observed:**
  - 38.23: 106 journeys, and starving travellers set out without food and died (Drew, Florence, Reynold, Ancel, Adam);
  - 38.24: Ancel baked bread, made a pack and set off to push on through trouble;
  - 38.26: nobody reached Elmdale, the High Moor or Grey Crag, and Henry was held back by load limits twice;
  - 38.30: about twenty trips between Hollins and Fern Hollow and none of the other three ways tried;
  - 38.31: nobody took the deer path, the drove road or the pass.
- **Status:** implemented (roads.py; D2-81, D2-104 to D2-113). The fault refusing unexplored ways is fixed (85b62a7). Known
  problem: agents rarely explore beyond one known place.

## 15. Holding, claims and theft

- **What it does:** land, buildings and herds are held by claims that people know of. Anyone can use what they can reach, but use
  of what others hold is seen and remembered, and taking from a store one has no right to is theft, seen by chance.
- **Leverage:** a claim is leverage only as far as others respect it; the engine enforces possession, not claims. Clearing and
  fencing make a claim with grounds.
- **Information:** an agent sees who claims a thing (prompt names claimants); a theft is known only if seen.
- **Scarcity:** not applicable.
- **Persistence:** claims last until changed; who was seen taking what stays in memory.
- **Interactions:** it depends on the parcel graph, buildings, herds and noticing, and is the base for any future law.
- **Behaviour observed:**
  - 38.24: Avice took a dropped sack;
  - 38.24: an owner left their buried coin untouched;
  - 38.31: the Rooks claimed and fenced a field they cleared;
  - devlog v3: a disputed field was settled by custom.
  - No theft from a store by an agent's own choice is reported.
- **Status:** implemented (world.py claims, settle.py thefts; D4-23). There is no dispute verb, so disputes happen only in speech.

## 16. Households

- **What it does:** a household is the first institution: members, a head, a house, a store and land. Members use its store, and
  the head manages it, names an heir and can set children to small work. People can join with the head's consent, leave or found a
  household.
- **Leverage:** the head controls the store, admission and children's work, and names the heir. Headship passes by the household's
  own rule of succession.
- **Information:** members see the household store and each other; other households' stores are hidden.
- **Scarcity:** houses (a new household must occupy, join or build: D4-36).
- **Persistence:** households and their customs last across deaths.
- **Interactions:** it holds claims, buildings and stores, and feeds hosting, agreements and life.
- **Behaviour observed:**
  - 38.23: grain was given to poor households, then stopped by Ancel, then given again after deaths in the village;
  - 38.25: heads passed herd news to their households;
  - heirs were named in 38.26;
  - joining or founding a household, and children's standing orders: not yet observed.
- **Status:** implemented (D4-18, D4-23, D4-36, D4-57).

## 17. Life: children, ageing and death

- **What it does:**
  - children come only by choice: two people try with work units, with diminishing returns;
  - pregnancy lasts 5 days with a gap of 4;
  - lifespan is a world setting that scales every stage;
  - births carry risk to mother and infant by shelter and food, halved with another adult there;
  - beyond hunger, cold and wounds, an adult dies with 0.001 chance a night and an elder 0.01, doubling every 20 days of old age;
  - the dead are buried or left.
- **Leverage:** children become future labour, and heirs carry a household's holdings. Old age removes heads and their know-how.
- **Information:** a couple is told of a pregnancy and a birth (since 17a8cda); others notice pregnancy and babies through signs.
  The odds of conception and death are hidden.
- **Scarcity:** fertility, the food cost of pregnancy and infants, and carers' time.
- **Persistence:** births and deaths change the population for good.
- **Interactions:** it depends on food, fire and households, and feeds labour, succession and memory.
- **Behaviour observed:**
  - 38.31: the Fenwicks (Opus 4.7) tried every day from day 0; Lucy conceived on day 5 ("We need the numbers before autumn turns") and had the first child;
  - the Cotters (Haiku 4.5) never tried but cared for their infant (43 care actions);
  - 38.30: the Webbs never tried, though their custom said they should;
  - 38.30: 6 died of old age.
- **Status:** implemented (life.py, Package D; D2-138 to D2-152). Whether agents try for children is strongly model-dependent
  (38.31).
  - As built, the population cannot replace itself at any effort: R0 0.59 with every couple trying every night (02ze).
  - D2-162 (29 Oct): pregnancy 2 days, gap 1, cap 0.8; built (478944e).

## 18. Speech and messages

- **What it does:** agents speak to those present, in a building (to those inside) or to the village. They may send 3 private
  messages a day (plus jitter, at most 10: D4-31) to people present. Messages to other places are carried by travellers.
- **Leverage:** news is leverage. Who knows first, and who carries news between villages, controls what others believe, and news
  can be paid for.
- **Information:** each agent hears only what reaches it. Agents keep up to 8 private notes (one pinned to every morning), which
  nobody else can read; there is no shared or written record.
- **Scarcity:** private messages a day and travellers to carry them.
- **Persistence:** none except in memories and private notes. Writing, letters and documents are not built.
- **Interactions:** it carries information for every system; it depends on roads, buildings (who hears) and memory.
- **Behaviour observed:**
  - 38.25: Bennet told Randal "Leave our gates alone", and Simkin turned back on Osric's word;
  - 38.26: warnings followed deaths, and Everard paid 3 coin for news;
  - 38.30: 89 pinned notes were refused, and Wymond used a pin as a morning reminder.
- **Status:** speech and private notes are implemented. A revision of pinning is proposed in proposals/notes.md. Writing and
  documents that others can read are planned (spec/information/letters_and_documents.md), not built.

## 19. Memory

- **What it does:** at the end of each stretch of days an agent rewrites its one memory, keeping what it wants from before within a
  length that grows with age (D4-61). Haiku keeps the older queue of memories.
- **Leverage:** an agent that remembers debts, promises and who did what can act on them; nothing in the engine keeps that record
  for it.
- **Information:** an agent sees only its own memory, its private notes and its conversation within a stretch.
- **Scarcity:** the length allowed.
- **Persistence:** the memory is the only long-term record an agent has.
- **Interactions:** it carries everything learned across stretches, including customs, debts, plans and grudges.
- **Behaviour observed:**
  - 38.26: 247 memories of about 150 words, "accurate and plan-carrying";
  - 38.36: Haiku rewrote 80 to 90% each time and dropped a live pregnancy;
  - Sonnet "keep_change" was the only variant that caught a stale belief;
  - some variants invented relatives and crises;
  - every instruction led agents to hoard mechanics (offer ids, store counts).
- **Status:** implemented (memory.py). An end-to-end in-engine run of rewrite mode is pending (38.36, "Next").

## 20. Conflict: fights, raids and guarding

- **What it does:**
  - an agent can attack a person or building (rob or hurt), settled at night by strength, weapons and helpers;
  - a raid on a building is a fuse event: those who detect it before it finishes get one urgent call to respond;
  - guarding a building adds defence.
- **Leverage:** force can take stores, and a stone house and guards protect them. Weapons are made goods, so force is
  convertible from crafts and materials.
- **Information:** a raid is detected only sometimes (D2-81); a fight is known to those present and to those told.
- **Scarcity:** weapons and people willing to guard.
- **Persistence:** wounds, deaths and grudges in memory.
- **Interactions:** it depends on buildings (structure), crafts (weapons), noticing (detection) and households, and feeds holding
  and speech.
- **Behaviour observed:**
  - in 38.24's dry run a raid on a timber house woke one person and on a stone house four;
  - no agent chose to attack in any live run reported;
  - a scripted gate-opening (38.25 c3) drew only a verbal rebuke.
- **Status:** implemented (settle.py, fuse.py; D2-5, D2-20, D2-51, D2-80 to D2-86). Raids by agents' choice: not yet observed. A
  village watch is not built.

## 21. Customs and aims

- **What it does:** households and villages are seeded with customs written into each member's knowledge (D4-57); agents are given
  no aims (D4-29).
- **Leverage:** none enforced. A custom shapes behaviour only as far as agents follow it.
- **Information:** each member knows its household's customs; other households' customs are known only by observation or talk.
- **Scarcity:** not applicable.
- **Persistence:** customs persist in memory; agents changing a custom is not observed.
- **Interactions:** it shapes exploring, farming, trade and children, and settles disputes in place of law.
- **Behaviour observed:**
  - 38.30: the Thornes followed their custom and the Webbs' did not move them;
  - 38.31: the explorer custom gave way in winter;
  - 38.22: Highcombe's "nobody goes over the scarp" likely discouraged exploring (the report's hedge);
  - devlog v3: a field dispute was settled by custom.
- **Status:** customs implemented as seeded knowledge. Aims are data only and not shown (one exception, Wilmot in region_c1).
  Passing customs on to children is flagged for later.

## 22. Governance, law and institutions above the household

- **What it does:** nothing yet. Institutions can in principle be members of other institutions (D4-18), but no village, office,
  law, court, tax or proclamation exists in the engine.
- **Leverage:** none from this system. Power above the household now comes only from holding scarce goods, know-how, carrying,
  hosting, credit and force.
- **Information:** not applicable.
- **Scarcity:** not applicable.
- **Persistence:** none; there is no accumulated rule or record.
- **Interactions:** it would read claims, agreements, households and speech, and need writing for records.
- **Behaviour observed:** none beyond custom settling a dispute (devlog v3) and the mill failing as a chokepoint (38.22).
- **Status:** planned. spec/institutions law.md, contracts.md and offices.md are "to compile", with no owner working on them. This
  is the largest gap against cybertron 1's takeover bench, where procedure and records were the main lever.
