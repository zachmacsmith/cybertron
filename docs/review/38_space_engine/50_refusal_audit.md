# 38.50: Every refusal in every run, and the misunderstandings behind them

Session 37.4, 2 Nov 2026. Zach: "Do an analysis of all refusals in every run and if the refusals messages are appropriate. Plus
if any other common misunderstandings come up."

**Method.** All 56 runs under `runs/`: 47,397 acts, 6,776 refused (14.3%), grouped into 465 kinds. Each refusal was normalised
(names, numbers and places taken out) and counted three ways: how often, in how many runs, and how often the same agent got the same
refusal on two or more days. That last count, called "repeats" below, is the best sign that a message taught nothing. Each kind was
also checked against the code, to see whether its wording is still there. Script: the session scratchpad, `refusals_all.py`. The
rate runs from 9% (Combe, the frontier) to 38% (the first M1 runs).

**What the refusals are mostly not.** None are faults in the engine's physics. Most (about 60%) are the world working as designed:
the commons picked bare, no crop in the field, the wrong season, a missing tool or material. What can be judged is whether the
message told the agent enough to act differently. Repeats say it often did not.

## The largest kinds, and whether their message is enough

| Refusal | Count | Runs | Repeats | Verdict |
|---|---|---|---|---|
| gather: *P* is picked bare | 1,163 | 44 | 238 | **True but a dead end.** Agents go back to a bare place day after day; the place line already says "you saw it picked bare". The message should say where else here the work can be done, and roughly when this place comes back. |
| pin: you have no note called "X" | 402 | 41 | 43 | **Interface misread.** Agents pin a note's text, or a title they changed in the same reply. Accept a match on the text, or the one note written this turn (item 6 of D4-94's analysis). |
| move: there is no *good* in your hands (meat, grain, wild food, milk, timber, bread, greens, fish, firewood) | about 700 | 35 | 140 or more | **The largest misunderstanding:** agents think what they gathered is in their hands when the work put it straight into the store (`gather ... for my household`). The message should say where the good is: "you hold none; the Hearne hut's store has 12 meat (your work put it there)". |
| work: there is no crop in *P* / not ripe yet / has a crop in it | 275 | 35 | 41 | Fair. "Not ripe yet" should say when ("ripe in about 2 days"), since the agent cannot see the sowing day. |
| gather: there is no standing timber left in *P* | 219 | 17 | 35 | Fair, as for picked bare: say where else. |
| work: the beasts there are watched / the cows are milked today | 390 | 27 | 71 | **Coordination, unnamed.** Someone of the household already did it. The message should name who ("Philippa watches them today"), so the agent can plan around it. |
| tell: *N* is a child and takes no part in the talk | 138 | 24 | 24 | Good: says what to do instead. |
| tell: nobody called *N* is here | 124 | 19 | 25 | Fair. Could add where one last saw them. |
| offer: could not read 'X' | 114 | 26 | 10 | Mostly fixed by D4-94 (work for a stated purpose; "every day"). |
| gather: there is little dung on *P* | 81 | 16 | 13 | Fair. |
| work: it needs *n* stone; you have *m* to hand | 80 | 15 | 18 | Fair. Could say whether the household's store counts as "to hand". It does (`takeable`). |
| work: *P* is sound | 80 | 19 | 16 | Agents mend a sound house. The place line says "sound", so this is planning by habit. Fair. |
| tell: you have sent your *n* private messages for today | 97 | 16 | 13 | Fine; the newer wording says the rest of the day's tells will fail too. |
| make bread: it needs *n* flour | 70 | 18 | 12 | **Missing the chain.** Agents hold grain and think it makes bread. Add "flour is ground from grain at millstones; a hand mill gives meal, which makes porridge, not bread". |
| fire: a fire in the open takes 2 timber | 62 | 10 | 8 | **Fixed by D4-94** (by heat, firewood first). |
| work: there is no one lying unburied here | 59 | 9 | 10 | Fair. They try to bury the dead where the body is not; could say where a known body lies. |
| *verb* is not done at *P* (felling, foraging, ...) | 70 | 9 | 13 | **Should say where it is done here** ("felling is done in forest: the Coppice, the Holm"). |
| accept: *party* has nowhere here to receive it | 30 | 6 | 5 | **Unclear.** It means the party named in "for" has no one present and no store at this place. Say so, and what to do: accept for yourself, or where they live. |
| gather: *party* has nothing here to put it into | 19 | 2 | 3 | **Unclear,** the same case for work done "for" a party away from its house. |
| set: you do not manage *P* | 25 | 1 | 2 | Ketil tried 25 times to bar the Gorm Hall. Name who manages it. |
| accept: there is no open offer 'X' | 69 | 23 | 12 | Fair. Could say whether it was taken, withdrawn, or made elsewhere. |
| work: there is no child called *N* here | 18 | 4 | 4 | Agents care for a dead or absent child; Wat tried for Margery after she died. Fine. |

## Repeated within a day

838 result lines carry an "(xN)" mark: the same act refused several times in one day, 2,567 refusals in all. Plans list the same act
two to seven times ("forage at Gorse Bank" five times), so one refusal becomes several. A refused act costs no units, so the harm is a
wasted plan, not a wasted day. Ending the day's repeats of an act after its first refusal would shorten every result list, and let
the fallback start sooner.

## Faults found on the way

1. **A dead member can be named the household's head.** `_name` picks from the household's members without checking they are alive.
   Alys named Odo the day after he died (wb2).
2. **The fallback can fill a day with one easy act** (wb3: 105 of 146 wood actions were the fallback). Not a fault of the code, but
   the prompt shows no store levels for fuel, so a full woodpile does not read as enough. A fuel line ("fuel for about 20 nights") was
   proposed in the conversation.

## Misunderstandings that are not refusals

| Misunderstanding | Where seen | What would help |
|---|---|---|
| Goods gathered "for my household" are thought to be in hand | about 700 move refusals | the move refusal says where the good is |
| Fittings built on open ground; "water mill" as a building | wb1 to wb3 | fixed by D4-94's build list |
| Covering grain with straw to keep it | wb1 (Kit) | no such act; an open question in heap_sizes.md |
| Claiming a craft one lacks ("I know how to build a water wheel") | wb1 (Rob) | in-world, not the engine's to stop |
| Naming a dead member head | wb2 (Alys) | fault 1 above |
| A plan carried forward unchanged from one's own notes | wb2 probe: 15 of 16 replies | the open probe in 38.49 (the plan removed) |
| The house fire needing timber | wb2 (Wat) | fixed by D4-93 |
| Barring a door against a theft outside it | wb2 (the Hearnes) | fixed by D4-93's theft wording |
| Weeding a clean field, mending a sound house, hay out of season | all farming runs | habits; the messages are clear and each costs no units |

## Recommendations

**Fix (bugs):**
- a dead member cannot be named head.

**Better messages (the agent should be told what to do next):**
1. "picked bare", "no standing timber" and "not done at": list where here the work can be done.
2. "No *good* in your hands": say where the good is.
3. "Not ripe yet": say when.
4. "Watched / milked today": name by whom.
5. "Make bread: needs flour": add the chain from grain to flour.
6. "Nowhere here to receive it" and "nothing here to put it into": say what is missing and the alternative.
7. "You do not manage": name the manager.

**Interface:**
- pin by the note's text, or the note written this turn;
- stop an act's repeats within a day after its first refusal.

*Current as of 2 Nov 2026.*
