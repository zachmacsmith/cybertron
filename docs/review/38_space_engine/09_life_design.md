# Review 38.09: children, households and death in cybertron2

*22 Oct 2026, 37.4 session, with Zach. Design only. The 37.1 session built demography on cybertron 1 (`wp/demography`,
`docs/review/37_growth/devlog_37.1.md`): ages and a labour factor, family raising (a child's loyalty at coming of age set by the
food it was given), minor frailty, children's surplus to the household, minors acting every k rounds, households as associations
with a pot and a head, inheritance (`partible`, `eldest`, `household`), a family bot, `start.households`, heirs to a pole seat
keeping its model. This note says what carries over to cybertron2 and what changes.*

## 1. What carries over as design

- **Fertility is a choice:** two consenting parents; no automatic births (Zach, 37.1).
- **Children are worth having** because they work for the household and, well raised, take up its cause; a neglected child may
  die young or turn against the parent who failed it (37.1 steps 3-4; a loyal child takes the parent's own goal, Zach 22 Oct).
- **Households are the economic unit** (37.2 02f §2) and the first institution (07 §4): a pot, a head, members, inheritance by
  rule (`partible`, `eldest`, `household`).
- **The seat keeps its model:** the heir to a pole seat gets the stronger model (scenario_design §2).
- 37.1's findings: cheap conception with frail, underfed children brought four to five times the starvation under bots; food was
  not scarce, so loop 1 measured the bot. The live test (does making children worth it change what models do?) is still the one
  that matters.

The code does not carry over: it sits on cybertron 1's contracts, pairs and subsistence. cybertron2 already has households as
data (each house has a household and a stock), so the life module is written for it, keeping 37.1's rules and tests as scenarios.

## 2. What changes

### 2a. Time: a round is a day

37.1 used maturity at 12 rounds. In cybertron2 a round is a day and ages are in years of the compressed calendar (devlog: a year
of about 16-60 days), so a child born in a run of 60 days does not grow up in it. Three ways to get generations, not exclusive:

| Way | How | Cost |
|---|---|---|
| **Seed every age** (recommended first) | worlds start with households of children, youths, adults and elders (37.6), so comings of age, partnerships, deaths of old age and successions happen inside a run from people already alive | none extra |
| **Chapters with time skips** | play 30-60 days, then skip a season or a year on standing orders with the life module rolling births, growth and deaths, then play again; agents get the skipped time as memories ("a year passed: ...") | cheap; fidelity during the skip is the bots' |
| **Long runs with fewer calls** | days without a call for agents whose routine runs (06 §5) | depends on how often plans change |

Not recommended: a separate, faster clock for ageing than for the calendar (a child would grow up in a few days of seasons), which
makes ages and seasons contradict each other in the prompt.

### 2b. Children are not agents until they are old enough

| Age | Is | Does | Model call |
|---|---|---|---|
| infant (0-2) | a member of the household | eats, needs shelter and care; is carried | none |
| child (3-9) | a member | small work by the household's standing orders (fetch water, mind the fire, gather) at a low labour factor; can be sent on a simple errand in the node | none |
| youth (10 to maturity) | **an agent** (the cheap model) | 3-4 units a day; errands between nodes, carrying, minding herds, learning a trade | yes |
| adult | an agent | full units | yes |
| elder | an agent | fewer units; knowledge, standing | yes |

This replaces "minors act every k rounds": the young cost nothing until they can act for themselves, and the household decides
their work. It also makes the age at which a child becomes an agent a world setting.

### 2c. Raising is what the child lived through

cybertron2 has perception: a child, even before it is an agent, **observes its node** (who is there, what is done, what it is
given), and its knowledge store fills from birth. At becoming an agent it starts with **childhood memories** (lasting memories: who
fed it, who was away, a death, a raid, a winter). 37.1's loyalty draw by food given stays the default rule; the memories make the
outcome legible to the model playing the child ("your father was away for most of your childhood; your mother fed you").

### 2d. Life happens somewhere

| Event | Where |
|---|---|
| conception | both parents at the same node (a partner from another village means someone travels) |
| birth | wherever the mother is; on the road it is dangerous; late pregnancy costs units |
| children travelling | with a parent (a party), carried if young |
| founding a household | needs a house: a lot on a node and a building (02i); a full village pushes the young outward (the frontier, 37.5) |
| joining a household | the head's consent, and living there (partners, adopted children, servants) |
| death | at a node or on an edge; what the dead carried lies there; the house stock and land pass by the inheritance rule; nobody is told except those who see it, and the news travels with witnesses (Zach: no announcements) |
| inheritance | the heir holds the house and land by rule, but goods are where they are: an heir far away must come, or send someone, to take them |

### 2e. Households as houses

In cybertron2 a household is already a house with members and a stock. 37.1's household becomes: the house (a building), its stock
(the pot), its members, its head (an office, once institutions exist: M3), its land (plots held), and its inheritance rule.
Membership changes by partnership, birth, adoption, leaving and death; a new household needs a new house.

## 3. Where it sits in the build plan (08)

- **M1** carries ages, the labour factor and household membership as data (seeded families), elders' and youths' units.
- **After M1 (with M2):** the life module: conception, birth, growth, coming of age with raising, death of old age, inheritance,
  households founded and joined. Seeded-every-age worlds first; chapters with time skips as an experiment.
- **Coordination:** the 37.1 session's design carries over; its next work would be this module on cybertron2's interfaces
  (Zach's call; as 37.2 is doing for the economy).

## 3b. Decisions (Zach, 22 Oct)

1. **Institutions grow from households:** the household is the first institution; villages form from households; specialised
   institutions emerge within them (a mill company, a guild, a temple); companies and a state come later. **Consequence for the
   engine:** an institution must be able to be a member of another from the start (a village is an institution whose members are
   households). cybertron 1 never had this (ARCHITECTURE §7.2: "an association as a member of another" not done), so cybertron2's
   membership is designed for it in M3.
2. **Short childhoods, counted in rounds** (supersedes §2a's calendar years and §2b's ages): fewer than 6 rounds as a non-agent:
   **1-3 rounds cared for** (an infant), then **3-4 rounds of menial tasks** (a child, still without a model call), then **a
   youth as an agent until adulthood**. A life is counted in rounds, faster than the calendar's seasons; prompts name the stage
   (infant, child, youth, adult, elder), never an age in years, so the two clocks never contradict each other in what agents read.
3. **Runs start with people of all ages and families.** No time skips.
4. **Youth learn faster, and it lasts:** a youth is not a weaker model; its learning multiplier is much higher, and what it learns
   while young decays more slowly (a trade learnt as an apprentice stays). This is 37.2's skill by practice (02c §5) with an age
   term.
5. Open: which model a youth gets (§4.3).

## 4. Open questions

1. How many rounds a youth lasts before adulthood (proposed 10-15), and a lifespan in rounds that gives turnover within a run.
2. ~~Chapters with time skips~~: no (Zach).
3. Which model a youth gets. Options: the model of the seat it will inherit (the heir keeps the pole's strength); the household's
   strongest; or drawn to keep the population's cast balanced (scenario_design §2). Proposed: chosen once when it becomes an agent
   and kept for life (switching models mid-life breaks the voice the others know), with heirs to pole seats taking the seat's
   model. A few rounds on a cheaper model first would save little (the cheap phase is already the non-agent childhood).
