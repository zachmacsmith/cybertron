# Proposal: what can happen (eras, weather, hazards that spread, and how people meet them)

**Status:** partly accepted: D2-76 to D2-79 (23 Oct); disease deferred (OPEN Q-13). Design only. **Owner:** 37.2 (at Zach's request). A companion to
[environment.md](environment.md), which holds the scheduler that runs these. **Affects:** as environment.md.

## Summary

A catalogue for the scheduler: **eras** (slow regimes of climate, disease, ecology and outside pressure), **weather events**
(by season and land kind), and **hazards that spread** (fire, crop disease and pests, livestock disease, human disease) within and
between nodes. Each entry says where it happens, how it moves, what it does, what warns of it, and how people can **prepare,
respond and recover**, and which institution it calls for. Not every hazard is bad: floods leave silt, fire renews pasture, mast
years feed pigs and game. Proposed first-world set at the end.

## 1. Eras (years)

Eras move the odds of everything below. They come in four families; a world has one era per family at a time (a dry era and a
raiding era can coincide).

| Family | Era | What shifts | Land that gains | Land that loses |
|---|---|---|---|---|
| **climate** (moisture, temperature, storminess) | steady | nothing | | |
| | **dry** | longer dry spells; droughts, wildfire, locusts; rivers low | wet valley floors, fens (drainable, fever falls) | grassland, hills, moor (peat fires) |
| | **wet** | longer wet spells; floods, blight, fevers, foot rot; rivers high | grassland, hills | valleys and fens (floods, fever) |
| | **cold** | shorter growing seasons, hard winters, late and early frosts, blizzards; passes closed longer | (none much; the south of a region) | hills, moor, high passes |
| | **warm** | longer growing seasons, two crops where one grew; more pests and fevers; summer droughts | cold lands | hot, dry lands |
| | **stormy** | more gales and storm surges on coasts; storm damage inland | sheltered valleys | coasts, exposed hills |
| | **the dark year** (a sudden shock: a volcanic winter) | one to two years cold and dim: harvests fail everywhere | none | everyone (stores decide who lives) |
| **disease** | quiet | | | |
| | **pestilence** | a contagious disease (people or cattle) stays in the region for years, flaring along roads and markets | isolated places | crossroads, market towns, armies |
| **ecology** | **mast and bust cycles** | game and wild food boom and crash every few years (a predator-prey cycle) | hunters in a boom | hunters in a bust |
| **outside pressure** (37.4's incidents) | **raiding** | outside raiders come more often (the same raid rules, D2-20 to D2-22) | walled places, high places | open farms, herds |
| | **trade** | outside merchants and caravans arrive more often | markets, crossroads | |
| | **migration** | newcomers arrive looking for land | the land-poor, labour-short | the crowded |

## 2. Weather events (days)

| Event | Where | When | What it does | Warning (and how long) | Prepare | Respond | After |
|---|---|---|---|---|---|---|---|
| **drought** (a long dry spell) | grassland, hills, moor most; everywhere in a dry era | summer | crops lose growth each dry day; forage and pasture thin; rivers low (mills slow, fords easy) | a dry spring; low streams (days to weeks) | stores, irrigation, wells, drought-hardy crops, fewer beasts | ration, move herds to wet land, buy food, migrate | a thin harvest; herds sold cheap |
| **river flood** | river valleys, fens | spring melt, wet spells | low plots' crops lost, buildings on low lots damaged, fords and bridges closed, stores ruined | the river rising, brown and fast (hours to a day: a fuse event) | banks and ditches (D2-66), build on high lots, stores upstairs (02i storeys) | move stock and herds up, boats, rescue | **silt: the flooded plots' fertility rises** next season |
| **flash flood** | hills, narrow valleys | after heavy rain | a sudden torrent along one stream: a mill, a road, a few plots | almost none (thunder upstream) | don't build in the gully | flee | wreckage, a changed stream |
| **storm surge** | coasts | stormy seasons and eras | shore plots salted for a season, boats and shore buildings lost | a gale and a strange tide (hours) | dykes, building back from the shore | move inland | salted fields recover slowly |
| **gale** | coasts, exposed hills; storms inland | autumn, winter | roofs damaged, trees down (a timber windfall), standing crops flattened at harvest, boats lost | red sky, rising wind (a day) | mend roofs, harvest early, stone | stay in, rope down | repair work; fallen timber to claim |
| **whirlwind** (a tornado) | open land, inland | summer, rare | a narrow track of ruin: two or three buildings and plots along a line | a black sky, a roar (minutes) | none much | shelter in stone or a cellar | one household ruined beside an untouched one: incidence |
| **hail** | anywhere | summer | standing crops on a patch of plots shredded | a green-black cloud (an hour) | none much (spread your plots) | | an unlucky few: who helps them |
| **lightning** | hills, open land | summer storms | a fire started (a building, a wood), sometimes a death | thunder | stone, clearing round the house | fight the fire | |
| **late and early frost** | everywhere; hills most | spring, autumn | young crops or a ripening crop killed | a clear still evening (a night) | sow later, smoke fires in the fields | cover, harvest early | a resown field |
| **heatwave** | lowlands | summer | the old, the sick and workers suffer (units down), water short | days of heat | shade, wells | rest at midday | |
| **blizzard, deep snow** | hills, moor, passes; cold eras | winter | edges closed, herds starve or freeze, people trapped | heavy sky, wind turning (a day) | hay in, herds in stalls (D2-45), fuel stocked | stay in; dig out | losses in the flock; roof collapses |
| **fog** | fens, coasts, valleys | autumn, winter | travellers lose their way or take longer; raiders come unseen | rising damp at dusk | | stay put; guides | |
| **landslide, rockfall** | hills, after wet spells | spring | a road closed, a quarry or mine collapses | cracks, falling stones (hours) | props in mines; avoid the slope | dig out | the road rerouted |

## 3. Hazards that spread

How each moves is one of six patterns, which the scheduler needs as a small vocabulary:

| Pattern | Moves through | Examples |
|---|---|---|
| **adjacency** | neighbouring parcels and buildings (layout.md) | fire, blight, foot rot |
| **contact** | people or animals together (a house, a node, a pasture, a market) | fever, pox, murrain |
| **carriage** | goods and travellers along edges | plague carried by a merchant; smut in traded seed; murrain in a driven herd; rats in a cart of grain |
| **flow** | downstream along a river | floods, a poisoned stream |
| **track** | a path across places | a whirlwind; a locust swarm moving node to node |
| **place-bound** | stays where conditions are | fen fever (from marsh air), anthrax in a field |

### Fire

| Kind | Where | Spreads by | Raised by | Prepare | Fight | After |
|---|---|---|---|---|---|---|
| **house fire** (exists) | buildings with hearths | adjacency to wattle and timber neighbours | dry spells, thatch, crowded lots, arson (D2-51) | stone, space between houses, water near | a bucket line (a fuse event), pull down the next roof | rebuild; deaths (D2-50) |
| **wildfire** | woodland, scrub, grassland | adjacency, faster with wind | dry era and spell, summer, fuel, lightning, a careless fire | firebreaks (a cleared parcel), a fire watch | beat it out at the edges, a back-burn, flee | the wood black and open: **easy to clear for fields**, game gone for a season, then new growth |
| **peat fire** | moor | smoulders underground for weeks | a dry era | | hard to put out | the moor's fuel lost |
| **controlled burning** (people's own) | scrub, old pasture, cleared wood | as wildfire if it escapes | | firebreaks first | | **renewed pasture; cleared land** (slash and burn, economy_later.md) |

### Crop disease and pests

| Kind | Spreads by | Raised by | Prepare | Respond | After |
|---|---|---|---|---|---|
| **blight** (rot) | adjacency among plots of the same crop | wet spells, warm, the same crop twice (D2-53) | rotation, mixed crops, spread plots | burn the infected field, harvest early | a failed field; less seed |
| **smut** (seed-borne) | **carriage: in the seed** | seed from an infected field | seed from a known clean field, seed selection (D2-65) | | clean seed becomes worth paying for |
| **locusts** | **track**: a swarm moves node to node | dry era, heat | stores | beat and burn them, harvest what is ripe at once | a stripped region; famine prices |
| **rats in the stores** | contact between stores; carriage in grain | full stores, wattle buildings | stone and cellars (D2-45), bins | traps | a store's food lost: the keyholder may hide it (old design) |

### Livestock disease

| Kind | Spreads by | Raised by | Prepare | Respond | After |
|---|---|---|---|---|---|
| **murrain** (cattle plague) | contact on shared pasture; **carriage: herds driven to market** | wet and warm, crowding, markets | keep herds apart, buy from known herds | isolate, slaughter the sick, stop driving herds | a herd lost: wealth in cattle gone (02o) |
| **foot rot** | adjacency on wet pasture | wet spells | drain the pasture (D2-66), stalls | move the herd to dry ground | lame beasts work less |
| **anthrax** | place-bound in a field where carcasses lay | hot after wet | | burn carcasses, shun the field | **the handler can die**: people and beasts linked |
| **wolves** (not a disease, but moves like one) | track: a pack moves between pastures | cold winters, game scarce | a watch (D2-21), stalls, dogs later | hunt them, a bounty | |

### Human disease

| Kind | Spreads by | Raised by | Prepare | Respond | After |
|---|---|---|---|---|---|
| **fen fever** (ague) | **place-bound**: marsh air, late summer | wet era, fen and valley floors | live on high ground, drain the fen | rest; a healer later | weakens rather than kills; fens shunned |
| **flux** (bad water) | contact and water; crowding | crowding, armies and sieges, floods | clean wells | care; move the camp | deaths among the weak |
| **winter cough** | contact in a house | cold, crowding, hunger | fuel, food | rest | mild: units lost |
| **pox or plague** | contact, and **carriage by travellers** | a pestilence era, crossroads, markets | **close the gate** (D2-5), turn away travellers | nurse the sick (nursing cuts deaths, but the nurse is exposed), bury the dead, flee | **survivors are immune**; orphans, empty houses, land to claim, wages up |
| **bad food** | the food | spoiled meat (spoilage), hunger | salting, cellars | | a household sick for days |

## 4. The good years too

Not every incident is a loss, and windfalls make the claims and sharing problems that losses make: a **bumper harvest** on one
holder's plots; **flood silt**; a **mast year** (acorns: pigs and game boom); **fish runs** on a river or coast; **storm-felled
oaks** (great beams without the felling axe); a **stray herd** of wild horses or cattle (D2-6); **a warm era's** second crop; a
**trader's caravan** with rare goods. Whose is the windfall: the finder's, the land's holder's, the village's?

## 5. How people meet them: what it asks of agents and institutions

| Stage | Acts (verbs) | Institutions it calls for |
|---|---|---|
| **prepare** | build (stone, banks, cellars, firebreaks), store, choose crops, rotate, keep herds apart, keep a watch, learn the signs | granaries, an almanac or weather-wise office, building rules, a fire watch |
| **respond** | work together (bucket lines, digging out, beating fires), move goods and herds, guard, close the gate, nurse, flee (travel) | a fire crew, a quarantine officer at the gate, rationing |
| **recover** | rebuild, resow, lend and give, take in orphans, claim empty land | mutual aid and burial clubs (agreements: a subscription that pays out), credit, inheritance rules, a lord's or village's relief |
| **learn** | remember, tell, write it down | a chronicle; elders; records of harvests and floods (02h) |

**Insurance falls out of the agreements system** (D2-31): a burial club or a fire club is a subscription whose pay-out leg is
conditioned on the incident ("if your house burns, the members owe you 10 timber each").

## 6. Proposed for the first worlds

- **Eras:** one climate era (steady, dry, wet or cold) as a starting condition (environment.md §10); disease quiet; outside
  pressure as 37.4 sets it.
- **Weather:** drought, river flood, gale, hail, late frost, blizzard (on hills), lightning.
- **Spreading:** house fire, wildfire, blight, smut in seed, rats in stores, murrain and wolves (with cattle), fen fever, winter
  cough, and one contagious disease kept rare (pox) to test gates and nursing.
- **Windfalls:** bumper harvest, flood silt, storm-felled oaks, a stray herd.
- **Later:** storm surge and coasts, whirlwinds, locusts, anthrax, peat fires, the dark year, migration and trade eras, landslides.

## Open questions (for Zach)

1. The four families of eras, one of each at a time?
2. The weather list and the first-world set (§6)?
3. The six spreading patterns as the scheduler's vocabulary (adjacency, contact, carriage, flow, track, place-bound)?
4. Disease mortality and immunity (with 37.1); whether nursing reduces deaths; a healer later (economy_later.md: medicine).
5. Windfalls' claims: the finder's, the holder's, or set by custom and law?

## Answers (23 Oct)

1. Four families of eras as a start, not the final schema; **outside raiders are new agents with raiding goals**, not scripts;
   scripted dangers can be herds of dangerous beasts (D2-76).
2. The first-world set (§6), every kind as data, the rest kept as expansions (D2-77).
3. The six spreading patterns (D2-78).
4. Disease: put off (OPEN Q-13).
5. **Windfalls** (good-luck incidents: a bumper harvest, a stray herd, storm-felled oaks, a fish run) need no rule: whoever finds
   one can take it, and custom and law decide claims (D2-79).

## History

- 23 Oct: Zach asked what eras and weather events there could be (droughts, floods mostly in valleys and near rivers, storms,
  hurricanes and tornadoes, coasts) and things that spread within or between nodes (fires, diseases of crops, cattle and people),
  each with ways to prepare, respond and fight back. Written: this catalogue.

- 23 Oct: Zach answered 1-5 (D2-76 to D2-79).

## Sources

[environment.md](environment.md), 38.04 §3 (land kinds' responses), [farming.md](farming.md) (field works, irrigation),
[attacks_and_walls.md](attacks_and_walls.md) (fire), [fuse_events.md](fuse_events.md), [gates.md](gates.md), [agreements.md](agreements.md),
[02o_livestock.md](../../review/37_growth/02o_livestock.md); D2-5, D2-6, D2-20 to D2-22, D2-31, D2-45, D2-49 to D2-53, D2-65, D2-66.
