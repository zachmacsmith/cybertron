# Review 38.15: the valley, three villages over 20 days (run m2_V)

Session 37.4, 23 Oct 2026. The first multi-node LLM run of cybertron2: the generated valley (`cybertron2/specs/m2_valley_s5.yaml`,
base `m2_valley.yaml`), 20 days, one run. Data: `runs/m2_V/` (local, not committed); readable chronicle `runs/m2_V_chronicle.html`.

## 1. The world

- **Roads:** Millbrook to Ashwood 1 day, Ashwood to Coppergate 1 day, Millbrook to Coppergate 2 days.
- **Calendar:** summer days 1-3, autumn 4-9, winter 10-15 (cold from day 9), spring 16-20.
- **Millbrook:** fields (barley, oats), cows (2 in milk), a small copse. Two houses:
  - Reed: Edric (Opus), Sibyl, Odo, Isolde, Cecily, Hugh (a child);
  - Hale: Hamo (Opus), Tiffany. Hamo and Edric have had a feud over Long Field.
- **Ashwood:** a deep forest. Fenn House: Simkin (Opus), Edith (Sonnet, born a Smith), Aldric, Alard.
- **Coppergate:** the copper seam, the only smithy, thin scrub and pasture. Smith House: Warin (Opus), Rohese (Sonnet, born a Fenn),
  Elena, Osric, Piers (a child).
- **Cast:** 15 acting; 4 Opus, 2 Sonnet, 9 Haiku.
- **Changes made before the run (D4-33):**
  - other lines' crafts are awareness only;
  - a village's repute comes from the lines born there.

## 2. What happened

| | Result |
|---|---|
| Deaths | 4, all of the Smith household: Piers (day 6), Rohese (12, on the road), Elena (14), Warin (19, a guest at Fenn House) |
| Missed meals | Osric 9, Warin 8, Elena 7, Rohese 4, Piers 3, Edric 3, Simkin 2; nobody else |
| Journeys | 15, of which 13 were between Coppergate and Ashwood by Smiths or Simkin; Millbrook's first (Edric to Ashwood) on day 16 |
| Hosting | `welcome` used 14 times, all at Fenn House, all for Smiths and Edric |
| Flows between households | Fenn to Smith: 18 wild food, 10 meat, 11 timber, 3 ore. Smith to Fenn: 17 coin, 2 copper tools, a crude tool and weapon, 7 timber |
| Copper chain | 1 smelt, 2 copper tools made, 3 minings (10 ore); no coin struck |
| End state | Coppergate empty (Osric alive, at Ashwood); Reed House 18 bread, 3 grain, 23 timber |
| Cost | $8.85, of which Opus $6.47, Sonnet $0.80, Haiku $0.47; 81% of input read from the prompt cache |
| Speech | 508 tells, 24 says (5% public); 222 of 285 turns were woken |
| Work | 1059 of 1379 units used |
| Refusals | 208. The largest: cows already milked (48), moving goods not in hand after a failed hunt or milking (54), a null pin (19), travel (12) |

The course of the run:

- **Coppergate could not feed itself.** The scrub was foraged to nothing by day 5. The household then lived on what the Fenns gave and
  on trips to Ashwood, each costing nights on the road.
- **Kin carried all the trade.** The two marriages between the Fenns and the Smiths gave beds, gifts, and meat "on credit against
  an axe" (Warin and Simkin, day 3; kept in notes and memories only). Warin paid the debt with copper tools on days 10 and 18.
- **Millbrook was untouched until late.** It had no kin ties to the other villages and was 2 days from Coppergate. Nobody from
  Coppergate went there. Millbrook's own store ran low by day 16 and Edric went to Ashwood to hunt and trade.
- **Nobody tried to move house.** No agent proposed moving a household or staying elsewhere for good. The engine offers no way to
  do so, and nothing in the prompt suggests it.

## 3. Engine faults the run showed, and what was done

| Fault | Effect in the run | Fix |
|---|---|---|
| Item weights and each person's load not shown | Warin and Rohese were refused at nightfall for being overweight (days 4-7, 11); each refusal cost a day | Fixed: weights in the map line, load in "You"; D4-32: a traveller over the limit is asked what to leave, with a person or at a house (`leave`), found there next morning |
| `make` did not say its inputs come from what you carry | Rohese and Osric took copper and left the timber in the store; tools not made on days 2, 4, 9 | Fixed: said in the verb line |
| Offers to anyone shown in every village | Ashwood and Coppergate agents tried to accept offers made in Millbrook | Fixed in the prompt; the offer itself still has no place (§4) |
| A restated offer made twice | Duplicate offers (O137 and O139, and others) | Fixed |
| Away from home, "You" showed the home house's live state and "Sleeping there: you, Osric" | Warin at Ashwood was told about Smith House as if he were in it, and given its live store | Fixed: the house as last seen when leaving, and "away from home you eat only what you carry" |
| A pin written as "None" | 19 refusals | Fixed |

## 4. Scope: where things happen

Where things happen is tracked as follows:
- **People and parcels:** an agent has `at`; a parcel has a node.
- **Houses, fittings and herds:** their node is derived from their parcel.
- **Events:** each carries a node.
- **Verbs:** each checks "same node" in its own code.
- **Offers:** no place at all.

Several pieces of code still read the whole world:
- milking takes any herd in milk;
- the knowledge check for milk looks at all herds;
- `set` bars one's door from another village;
- in a raid, absent household members and guards anywhere count as defenders;
- attending to a herd or fitting resolves its name world-wide.

The proposed fix:
- explicit nodes on every placed thing, offers included;
- one local view (`w.local(node)`) through which every verb and every prompt section except the map and kin lines read the world;
- offers close when the offerer leaves (D2-26);
- a sweep test: agents in every village, no prompt names another village's houses, parcels, people or offers outside the map and kin
  lines, and every verb refuses a target that is not local.

## 5. Questions for Zach

1. **Does a host feed a guest?** The lodging spec says a guest "is sheltered as the household is" and says nothing of food. M1 has a
   guest eat only what it carries. Warin died a guest at Fenn House, whose store held 8 wild food and more. In the run the Fenns fed
   guests only by giving. That is one reading of the spec; the other is that a welcome includes a meal from the store.
2. **Migration.** No mechanism, and nothing in the spec, proposals or OPEN. The smallest version is joining a kin household (Warin and
   Osric as members of Fenn House); others are taking up an empty house, or building one.
3. **Promises and messages between villages** (D2-27, D2-31 to D2-40, D4-9). The axe credit and the crossing of Simkin and Warin on
   the road on day 7 are the cases. These are decided and specced, not built.

## 6. Reading

This is one run, with no null arm and no replicate. A single run can show what happens; it cannot say how often. Read with that in
mind:

- **The pressure behaved as the world's design predicted, and as I warned before the run:** dependence was lopsided. Coppergate
  needed food within days. Nobody needed copper within 20 days.
- **The deaths are not good evidence about the agents.** Four of the six faults in §3 were the engine's presentation, not the agents'
  choices, and each one cost a Smith a day or a meal. A rerun with the fixes is needed before reading the deaths as agent behaviour.
- **What is evidence:** kin ties carried every exchange; credit appeared unprompted and was repaid; the Fenns sheltered the Smiths
  14 times. No agent tried to move house or to reach Millbrook.

*This note records a run and the fixes made after it; the decisions it led to are D4-32 and D4-33 in DECISIONS.md.*
