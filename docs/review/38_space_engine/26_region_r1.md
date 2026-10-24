# 38.26: the region world, run r1 (dependent arm), stopped at day 23 of 48

Session 37.4, 24 Oct 2026. World cybertron2/specs/region_c1.yaml (37.2's 02t, D2-137, with Zach's additions: Wilmot the explorer,
three unexplored places, one hidden way). 58 people in four villages. Stopped by Zach at day 23; cost $33.99. Run on the engine as
of 9e4655d (before Package D and the travel-destination fix), so the two bugs below held throughout. No null arm (Zach: "just do one
arm"); read qualitatively (02t §5).

## 1. What happened

**17 of 58 died, none for want of food in the region.**

| Village | People | Dead | Households hit |
|---|---|---|---|
| Coppergate (ore) | 11 | 9 | Cole 6 (of 6), Moor 3 |
| Barleyfield (farms) | 21 | 6 | Lowe 4, Hale 2 |
| Millford (market) | 18 | 1 | Miller 1 |
| Ashwood (wood) | 8 | 1 | Ash 1 |

12 of the 17 died with food in reach and no fire to cook it on (D2-60: grain and flour are eaten only boiled or baked): their
hearths were out for want of timber. 3 died sleeping out on the road, 2 with no food. 6 were children, 7 adults, 3 elders, 1 youth.

**The world had the food and the timber, in the wrong places.** House stores (food in meals / timber), from the agents' own prompts:

| House | Day 0 | Day 9 | Day 15 | Day 22 |
|---|---|---|---|---|
| Reed House (Barleyfield) | 52 / 14 | 218 / 19 | 258 / 0 | 174 / 2 |
| Moor House (Coppergate) | 152 / 10 | 110 / 4 | 99 / 0 | 92 / 3 |
| Cole House (Coppergate) | 80 / 8 | 55 / 0 (all dead by day 9) | | |
| Fenn House (Ashwood) | 38 / 13 | 26 / 68 | 23 / 113 | 26 / 41 |
| Ash House (Ashwood) | 25 / 13 | 22 / 38 | 6 / 38 | 0 / 3 |
| Miller House, the Bell, Smith House (Millford) | 14, 51, 21 | 0, 16, 7 | 5, 11, 13 | 0, 5, 0 |

The Moors died beside 100 meals; the Fenns held 113 timber on day 15 while three villages' hearths went out; by day 21 Ashwood, the
wood village, had no food, and Millford's millers, smiths and innkeepers none, a day from Barleyfield's 300 meals.

**Trade happened, but small.** 206 offers, 71 accepted, 72 agreements in all. Across villages the typical deal was 2 to 5 timber
for about as much grain, bread or flour, or a copper tool for 4 timber. Deep Wood gave 441 timber (it was felled out by day 20).
What limited it, in the agents' own words: carrying. "I'm carrying 34 weight against a limit of 10, so I can't get home with this
load" (Henry, Moor head, stuck at Ashwood on day 5 while the Coles died); "my load is over the 20 I can carry on the road home,
which has no cart track" (Henry, day 17). On foot a person carries 10, with a pack 20; Coppergate is two days from Ashwood with no
track. A winter hearth burns 2 a night.

## 2. The Coppergate collapse

Coppergate held ore, stone and 160 grain, and 20 timber on the Hillside, which nobody could cut: felling is done in forest, and the
Hillside is scrub (a world-design error, mine). The Coles' fire went out on night 3. Simkin and Sabina went to Ashwood for timber (2
days); Simkin died on the way back (day 5). The rest ate wild food and died one by one with 55 meals in the store (Helewise and Jory
day 6, Aldric 8, Godiva 9); the dying elder Aldric asked the Moors next door for help only on day 7. Henry, the Opus Moor head,
spent days 3 to 11 away getting timber and charcoal, couldn't carry it home, came back to find the Coles dead, and then the Moors'
own fire went out: Mabel, Martin and Petronel died on days 13 to 14 with 100 meals in the house.

## 3. What worked

- **The noticing rule**: 4 noticed and 6 attended items a day each, 1.3 that concern
  them; after seeing a parcel's game, wild food or wood as bare, 7% still worked it the next day; deaths seen were acted on (burials,
  cairns, warnings) the next day in 79 of 131 agent-days.
- **Self-written memories**: 247, about 150 words each, accurate and plan-carrying (but see §4).
- **The search for the lost ox** (days 12 to 22): the Merchants' ox walked out of Riverside Meadow through a gap in the fence; Elias
  organised a search by hoof-marks, Katherine and Ysolt mended the gap and followed the tracks, Everard asked along the Barleyfield
  road and offered 3 coin for news, Rohese found it on the Glade at Ashwood, and Elias and Ysolt herded it there for days and
  brought it home. The world's tracks, fences and wandering herds made a whole story.
- **Harvest and hiring**: the farms took on reapers for grain (Everard reaped the Millers' barley at 1 grain a unit); 31 sowings,
  35 sow acts at Barleyfield for spring.
- Hosting (66 nights), teaching (8), burials (16), heirs named.

## 4. Engine faults found (fixed after, for later runs)

1. **No unexplored way could be chosen as a destination** (fixed 85b62a7, then a67c542): the reply schema's "to" enum held only
   places the agent knew. Wilmot, seeded to explore, wrote it in "stop at" on day 0 and was refused, and from day 1 reasoned "the
   deer path north still isn't one of the places I'm allowed to name for travel"; she tried the hidden way west from Barleyfield on
   day 4 and couldn't name that either. Nobody reached Elmdale, the High Moor or Grey Crag. "to" is now free text.
2. **Memories lost when one set off at a stretch's end** (fixed a67c542): 44 stretches went unsummarised, mostly travellers'.
3. **A pack ox can be silently left behind**: Everard's `travel {lead: "the Merchant's ox"}` on day 11 was accepted, but at
   departure the ox stayed ("The ox stayed behind, so I can only carry about 7 timber home"). To investigate: the verb's check and
   the departure's (`pack_ox_for`) disagree; the departure should report it.
4. The build verb said a camp needs built ground or scrub (fixed 9e14772); build options never show without materials in hand
   (Package E item 7, deferred by Zach).

## 5. Reading

Dependence, as designed, bound hard: every village needed another's goods, and at the scale they could carry, trade could not move
enough timber through two winters' nights. The cast traded readily, but in loads of 2 to 10 on foot, while the ox (60) was lost and
no carts went to Coppergate (no track). This is a real finding about the world's numbers, not the agents: a winter's fuel for a
hearth (about 12 timber, and 2 a cold night) against a carry of 10 and two days' walk makes Coppergate unviable without a track,
an ox, or wood of its own. For the next region world: let scrub be cut for firewood (or give Coppergate a coppice), a cart track to
Coppergate, and fewer cold nights or more stored fuel; and a null arm, to read what dependence itself did.

*Run files: runs/r1_region_dependent (turns, days, perception, memory).*
