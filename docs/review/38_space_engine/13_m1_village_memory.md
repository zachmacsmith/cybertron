# Review 38.13: M1 run D, a three-household village with an Opus and Haiku cast, and an audit of memory and perception

*23 Oct 2026, 37.4 session. Zach: "Try again with a few more Opus and a Haiku bulk. Describe the full setup. Then examine
specifically if the new memory etc. systems are working." Spec: `cybertron2/specs/m1_village_s8.yaml` (generated from
`m1_village.yaml`, seed 8). Run: `runs/m1_D` ($7.13: Opus $6.73, Haiku $0.40). Nothing here is decided.*

## 1. Setup

**Engine changes since run C:** the reply schema now lists the allowed values of every closed argument (verbs, goods, crafts,
places, people, attention targets), which the CLI enforces, so `"to": "Reed House"` becomes `"house"` before the engine sees it;
offers draw on one's own store; the generator takes a size, rates and a cast from the spec, puts the feud between unrelated heads,
and varies the elders' aims.

**Village:** Millbrook, three houses on the green; the same parcels, incidents and signs as runs A-C (geese day 2, cattle in the
barley day 4, smoke day 5, frost day 7, cold from day 8), with land for about a dozen (wild plants 76, game 40, fish 24, barley 40,
oats 16).

| House | People (stage, model) | Crafts and tools | Stores at start |
|---|---|---|---|
| **Reed** (2) | Hamo (elder, head, Opus), Joan his wife (elder, Haiku); the founders, 58 years here | reaping, bread, pottage; **the sickle** | 3.3 grain, 1.3 bread, 1.3 timber |
| **Fenn** (6) | Wat (adult, head, Opus), Mabel his wife (Haiku), his parents Piers and Mariot (elders, Haiku; the Fenn founders), their daughter Maud (youth, Haiku), son Edric (child) | felling, hunting; **the axe** | 6 meat, 2 greens, 10 timber |
| **Hale** (4) | Ivo (adult, head, Opus), Letice his wife (adult, Opus; **Hamo's daughter**, born a Reed), daughters Isolde (adult, Haiku) and Alys (youth, Haiku) | fishing, lines, baskets, pots, firing pit; **a line**; Letice also knows the Reed crafts | 2.7 fish, 2.7 greens, 4 timber |

**Ties:** the Reeds and Hales are kin by Letice's marriage; the Fenns are kin to neither. **Feud:** Hamo and Wat came to blows 12
winters ago over who has the right to Long Field. **Debts:** Piers (Fenn) owes Hamo 3 grain; Joan (Reed) owes Wat 1 meat. Aims:
heads "see the household through the winter" (Hamo and Wat add "you will not be shamed by [the other] again"); youths learn a
craft of another house (Maud reaping, Alys felling); elders' aims vary (the family's good name and its debts; one more winter).
**Cast:** 4 Opus (three heads and Letice, the adult who knows most), 7 Haiku, no Sonnet.

## 2. What happened (briefly)

Everyone lived. Both debts were settled (one of them on false accounting, §3.1). Hamo taught Maud reaping on day 1 and promised
it before the harvest; Ivo taught Wat fishing; Mariot explained felling to Alys. Trade ran at 3 grain a timber. The cattle and
the frost were noticed and acted on. By the end the Fenns held 41 grain, 17 meat and 14 timber; the Hales, with two Opus adults,
had half a timber and missed the last meal; nobody built the firing pit the Hales could build. No theft, raid or fight.

## 3. The audit

### 3.1 Memory: the two-day band, the one-line days, lasting memories

| Check | Result |
|---|---|
| Sections present as designed | yes: recent days (from day 2), earlier one-liners, lasting memories, beliefs, notes, in every prompt they apply to |
| Size | the turn prompt grows from 1.2k to **16.4k characters** by day 10 (runs B-C: 7.7k). In Piers's day-10 prompt, "Recent days" is 13k of 16k: 50 heard lines (everyone's `say` for two days) and 22 of his own "You told..." lines |
| Lasting memories formed in the run | 13 in 10 days for 12 people, and the wrong ones: "Piers gave 1 timber to Hamo" (a keyword match on "gave"), while trades, the teaching of reaping, promises and the cattle in the barley formed none |
| **Said is not done** | Piers (Haiku) *said* "Here is another timber toward the 3 grain... That makes two timber paid" with no `give` in his plan. His note recorded it as paid, and each later note inflated the count: 3 timber actually given became "six timber paid". Hamo (Opus) was shown the true events ("Piers gave 1 timber", "Piers gave 2 timber") but wrote "He says he has paid 4 timber in all, so I count the debt settled" |
| Correct recall elsewhere | Wat's note "Joan paid her 1 meat debt on the last day of summer" is right (day 2); "owe", "last winter" and "promised" appear 40 times in reasoning and speech, most checked cases correct |

**Reading.** The bands work mechanically, but (a) the full band is dominated by other people's speech, (b) lasting memory is a
keyword filter that keeps trivia and misses what matters, and (c) the band puts "You told Hamo: here is another timber" beside
"You gave 2 timber to Hamo" with nothing to tell them apart, so an agent's own words become its record of what it did. The engine
had the true facts; the agents preferred the claim.

### 3.2 Notes

| | Haiku (7) | Opus (4) |
|---|---|---|
| Notes written per agent | 8 | 6.8 |
| Pins | 75 | 17 |
| Opened | 15 | 0 |
| Look-ups | 10 | 6 |

Notes are working as running ledgers: Wat's "Winter plan" was rewritten 13 times with dated store counts ("Autumn day 4: store
had 25 timber and 36.8 meals"), trade rates, who holds the axe and settled debts. They are where the Piers error was amplified:
an agent writes its notes from its intentions and speech, and nothing checks them. With a Haiku bulk, notes are used far more than
with Sonnet (runs B-C: Sonnet agents wrote none).

### 3.3 Perception

| System | Result |
|---|---|
| Dawn notice | cattle in the barley reached 11 agents (9 mentioned it); frost 11 (9 mentioned it); smoke 6 (2); geese 4 (1). Works, and the salient incidents change plans |
| Attending | Haiku: places 46, people 15, sky 9; Opus: places 23, **own house 15** (redirected to "the place in general" with a note; Opus kept choosing it), people 1. The next day's reasoning names the attended target in 83 of 89 cases (a weak test: agents often attend where they work) |
| "As you last saw them" | present in 70 of 110 prompts, correct and dated, but thin: "Hamo, 4 days ago: Hamo was reaping Long Field". Little sign it is used |
| Felt watched | 4 times; reacted to once |

### 3.4 Knowledge

Transitions this run: taught (Hamo -> Maud reaping, Ivo -> Wat fishing), explained (Mariot -> Alys felling), watching (Letice,
Hamo, Alys: hunting rough), practice (Joan: hunting rough -> known by trying). One fault: the source shown for a level kept the
first source ("you have seen the Reeds at it all your life" after Hamo taught Maud); fixed after the run. Rejections fell to 11% of
results (A-B: 24-32%), and 22% of rejected actions were planned again the next day (mostly "move fish to the house" before the
catch is known, which is harmless).

### 3.5 The talk step

Everyone was asked again every day (110 of 110) and 90 plans changed: the step is doing real work, at double the calls. Opus is 94%
of the cost.

## 4. Proposals (for Zach; not built)

1. **Separate what you did from what you said** in the memory bands: "You did" from engine results only; "You said" apart and
   shorter. The record of one's own acts should be the engine's.
2. **A ledger of transfers between people**, kept by the engine and shown when it bears on the moment ("Between you and Hamo since
   summer day 5: you gave 3 timber; he gave you nothing"). Debts stay information (02f); transfers are facts. This would have
   caught the Piers error, on both sides.
3. **Heard speech in the full band:** keep what was told to you and says that name you; summarise or cap the rest. That cuts the
   prompt by about two thirds at this size.
4. **Lasting memories by event kind, not keyword:** trades and gifts across households, teaching, promises made to you, incidents,
   deaths, fights, thefts; not routine gives inside a household.
5. **Attending one's own house** (11 §6 Q4): Opus chose it 15 times even after being told it is shown daily. Allow it, giving the
   comings and goings and the store's changes.
