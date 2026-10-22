# 37.2k Fuse events and gates: time to respond, and entry to a place

*22 Oct 2026, with Zach. Design for cybertron2. Most of it is 37.4's (the day's order, the night, the scheduler, combat); 37.2's part
is the economics (what walls, gates and stone buy, tolls) and the information (passes and seals as documents). Posted on the board
for 37.4. Nothing built.*

**Decided (Zach, 22 Oct):** fuse events are worth adding (rare, and only a subset of people are woken, so cheap); gates check
arrivals automatically first, and otherwise the keeper and the arrivals talk in the day they arrive.

## 1. Fuse events

**The idea.** Some events do not finish the moment they start: a break-in, a fire, a flood, a party seen on the road. Each has a
**detection time** (when someone notices) and a **completion time** (when it is done). If someone notices before it is done, they get
an **urgent call**: a short decision with a narrow menu. Then the event resolves.

**Defence is mostly buying that time:**

| Thing | What it does to the fuse |
|---|---|
| stone walls | lengthen it (the break-in takes longer) |
| a night watch, dogs | detect earlier |
| beacons | carry detection to other nodes |
| arriving on foot | the fuse is a day: they were seen arriving (37.4's "arrive, then decide") |
| riders | almost none (02g §5b) |
| a wattle hut | none: in before anyone wakes |

So stone, walls, watches, beacons, and riders against foot need no special rules each: they set the fuse. A night watch is an
office whose holder is awake, so the town detects first. Neighbours who are woken may come and help: the hue and cry, and the root
of a militia.

**Not only violence.** The same mechanism carries:
- **fire**: neighbours form a bucket line (02b's crew S-curve); stone slows it, so there is more time;
- **flood**: move the stock to an upper storey (02i §2c);
- **a thief at the store**: the dog barks;
- **a birth or an illness**: fetch the midwife or the healer (37.1);
- **wolves at the herd, a calving**;
- **a traveller at a shut gate at night** (§2);
- **an urgent message** ("the bridge is down", "raiders tomorrow");
- at the scale of a day: **a storm before the harvest is in**.

**Rules:**
1. **One wave per event.** Those woken decide at once, in parallel; then it resolves. The side that started it does not answer
   back: it committed when it acted.
2. **Who can be woken:** only those at the node, or reached by a beacon; and only those who detect it (presence, the watch, dogs,
   noise from the building next door). A cap on urgent calls per agent per night.
3. **No warning, no call.** Without detection a fixed default applies (asleep: defend at half strength, as built). One rule: you act
   only on what you learn in time.
4. **The menu is the event's own:** go there, defend, flee, hand over, fight the fire, move the stock, raise the alarm, stay put.
5. **Order:** fuse events resolve in step 7 (the night), in a fixed order by start time, then by a seeded draw; overlapping events
   at one node share one wave (each woken agent sees all the events it detected).

**Costs.** A sub-step in the night (deterministic order); a short second prompt; one call per woken agent, only for events with a
fuse. Raids may be rare (run 2's agents seldom chose violence), so outside raiders as incidents may be what exercises it; fire and
illness need no one to choose them.

**Before reflexes.** Urgent calls need one new thing, a call outside the day's turn. Reflexes (38.06 §4, deferred by Zach) need a
condition language. Urgent calls can come first; reflexes later replace the fixed default for those not woken.

## 2. Gates: a boundary with an entry rule

**The idea.** Any enclosure has an entry rule: a room (02h §4a), a house door (38.06 §4's policy "my door is open to the Wynns"), a
walled compound, a walled town, a toll bridge, a pass, later a polity's border. A walled node is a building at the scale of a node,
so its gate is a door.

**Rules a gate can have:** open; a list of names; a token (a pass, a seal: documents, 02h); a payment (a toll); otherwise the keeper
decides.

**How it fits the day (37.4's 05 §1), with no new phase:**
1. **Walls change the node's layout.** Edges end at a site outside the walls (historically, the suburb outside the gate, often with
   an inn). Entering is a crossing with a rule.
2. **Dawn:** arrivals appear outside. The automatic rule runs; those it admits are inside before they look and decide.
3. **Look and decide:** the rest see they are outside the gate and decide from there (wait, ask, trade outside, lodge at the inn
   outside, leave). Each states its business to the keeper in its messages.
4. **Talk:** the keeper and the waiting arrivals are at the same site, so they talk in the ordinary talk step: together, with
   private messages as in 02h. **Admitting is a talk-step act** (free, like a message), so it takes effect at once. The admitted
   arrival has received something, so it is asked again (05 §1 step 4) and may change its plan to act inside for the rest of the
   day.
5. **Talk runs out** (`talk.waves`) without admission: the arrival stays outside for the day and can try again tomorrow.

**What it makes worth having:**
- **A pass saves a day.** Admission by rule is at dawn; a negotiation can cost the day. That is the price that makes passes and
  seals worth carrying, forging and stealing.
- **A gate is only as good as its enforcement:** the keeper can be bribed or fooled with a forged pass; the gate can be forced (a
  building raid on it); a wall with gaps can be walked round; no keeper on duty means only the automatic rule; at night the gate is
  shut, and an arrival wakes the keeper (a fuse event, §1).
- **A toll is the town's revenue:** the wall pays for its upkeep and its keeper. Market towns paid for their walls this way. It ties
  the institution, its revenue, its gate and its documents together. The keeper is an office (37.3).

## 3. Attacks and buildings (proposals still open)

From the same discussion; for Zach and 37.4 to settle.

| Kind | Target | How it resolves |
|---|---|---|
| **attack a person** | someone at your node | as built (`cybertron2/combat.py`); the target's response (fight back, flee, hand over) once reflexes or a fuse exist |
| **raid a building** | one building | (1) **break in**: work set by the structure (wattle quick, a barred timber door longer, stone much longer); noisy, so those inside may wake (a fuse); (2) **fight whoever defends**, who chose to defend, flee (lose the stock, keep their lives) or hand over. An empty building is the break-in only, against its lock and walls |
| **raid a node** | a sweep by a party | each raider's engagement draws a target weighted by exposure x value / hardness: herds, crops, open stores and people outside first; wattle and timber next; stone and guarded sites last (02g §5b) |

**Stone (Zach):** a stone building is both less likely to be picked in a node raid and stronger when it is. Proposal: walls
**multiply the defence of those inside** (asleep x0.5 with no house; x1 behind a timber door; x2 behind stone), rather than adding
a fixed defence, so a wall needs people and numbers still beat walls. With 37.4's harm contest and a household of four with crude
weapons, three raiders with crude weapons succeed 62% / 32% / 11% (none, timber, stone); twelve with blades 99% / 97% / 89%. An empty
stone house is defended only by its lock.

**What follows:**
- **Fortifying displaces raids:** in a sweep, a stone house sends the raiders to the neighbours. That is a private defence with a
  cost to others, and a principled reason to pool into a village wall, whose cost per household falls with population (its
  perimeter grows with the square root of the area enclosed).
- **Stone pays for whoever holds stock:** at 02j's prices it costs about 18 actions more than a timber frame and repays after about
  nine raids on a 20-food household, one or two on a 120-food store. The rich household's tower, the stone granary, the church as
  refuge.
- **A refuge is leverage:** in a node raid, people flee to the strongest building, and whoever controls its door can charge for it.
- **Horses fit the node raid:** strike on arrival, drive herds off, carry loot, leave before pursuit. Proposal: node raids only by
  riders or large parties; building raids by small groups.

## 4. Open

1. Fuse events: the cap on urgent calls per agent per night; which events have a fuse in the first worlds (raids on stone, fire,
   arrivals at a shut gate).
2. Gates: whether an admitted arrival's re-ask counts as one of the talk waves; tolls as a payment rule now or with coin (E5).
3. §3's attack kinds, the wall multipliers, and node raids for riders and large parties only.
