# Short tags for things one can act on that have no unique name

**Status:** accepted: D4-68 (2 Nov)
**Owner:** 37.4

## Summary

Some things an agent can act on have no unique name in the world: groups of beasts after a herd splits, things lying at a spot,
documents, offers and agreements. Give each a short tag (H2, T5, ...) that is shown in brackets wherever it is mentioned and that
the verbs accept. Things with a unique in-world name (people, places, parcels, buildings, roads) keep their names and get no tag.
Goods (grain, timber) are quantities and need none. The tag exists to make reference exact. Saving characters is not its purpose.

## The proposal

1. **Which kinds get a tag** (from the engine's referents):

   | Kind | Engine | Tag | Why |
   |---|---|---|---|
   | Groups of beasts | `herds` (counts by role; a split makes a new herd, `herds.split`) | H | split groups share the parent's name |
   | Things lying at a spot | `things` (bundles, packs, bodies, graves, caches) | T | several identical "a bundle lies at the Common, with hay in it" |
   | Documents, when built | D2-24, D4-35 | D | many alike |
   | Offers, agreements | `offers`, `agreements` | O, A | to accept or settle one exactly |
   | Claims | `claims` (already C1, C2, ...) | C | already ids; show them |
   | People, nodes, parcels, buildings, roads | named | none | names are unique; the engine keeps them unique (a second John is "John of Ashby") |
   | Goods, tools | quantities in containers | none | fungible: "3 grain" |
   | Fittings | parts of a building | none | building + kind |
   | Crafts | vocabulary | none | reply words |
   | Kept lines, notes | numbered or titled already | as now | |

2. **One tag per thing, shared:** the world id, shortened (H2 is herd 2). Anyone who perceives the thing sees the same tag, so
   people can talk about it exactly ("H2 is at the river").
3. **Shown with the description, not instead of it:** "a group of five broke off from the Hobb cattle (H2) and wandered toward the
   river"; "a bundle lies at the Common, with hay in it (T7)". The agent still reads what the thing is; the tag only says which one.
4. **The verbs take a tag wherever they take a name:** `drive {herd: H2}`, `take {from: T7}`. A tag for a thing not here is
   refused as an unknown name is now.
5. **Identity is knowledge.** A tag shows only what the observer could know is the same thing: one's own household's beasts and
   things one put down or saw put down are recognised; a stranger's group seen in two places is not known to be the same group, so
   the tag is shown only while one can tell (one saw it, the group is marked as one's own, or someone said so). Open: whether a
   stranger's group gets a tag of its own per sighting, or no tag.
6. **Lifecycle:** a tag dies with its thing. A group that rejoins its herd: "H2 has rejoined the Hobb cattle (H1)". A bundle taken
   up empty: gone. Beliefs keep a dead tag with the day last seen, as for anything else remembered.

7. **Names on top of tags (a second step).** Anyone may name a thing that has a tag: `name {thing: H4, as: "Old Brock"}`. A name is
   knowledge, not a property of the thing: it is known to the namer, to everyone present when it is given, and to the namer's
   household (a household shares the names it uses). Others still see the tag and the description. Where one knows a name, the
   message shows "Old Brock (H4)" and the verbs accept the name. Two households may call one thing by two names; the tag keeps them
   straight. The same act names a place nobody has named, for whoever first comes to it, in worlds that leave places unnamed.
8. **Individual beasts: not now.** A group of one is already an individual: an ox that strays alone is its own group with its own
   tag, and can be named. Splitting by role is readable without ranges (`drive {herd: H1, take: {oxen: 2}}` makes a new group).
   Beasts as individuals (each with age, sex, milk, owner, name) would change farm.py's milk, ploughing, breeding and capacity,
   herds.py's splits, merges and roads, and would grow state and messages in worlds with flocks of a hundred.

## Why

Zach (2 Nov): "each subject that can be acted on [could] have a very short identifier that shows up in brackets when it is
mentioned ... so that they can always know exactly what to act on, and then these are shared so they won't get confused".

Evidence from c3_combe_rich (review 38.41):
- 18 drive refusals, 13 of them "the Hobb cattle has none of those (no beasts)". After splits, Everard's morning message listed
  five groups of his household's beasts: three named "the Hobb cattle" and two "an ox of the Hobb cattle". No agent could find
  out which was which.
- His "Lying about" list held six bundles, three of them "a bundle lies at the Common, with hay in it". `take` names a place,
  not a bundle. Margery kept as a lasting line a false rule learned from this: "bundles left lying on open ground can't be picked
  up again".
- `take {from: Ivo}` was refused three times ("there is no building called 'Ivo' here") for goods lying by his body.
- d1_duo: "there is no child called 'Cotter House' here" (8), and offers that could not be read (3).

## Alternatives considered

- **Tag everything, as a compression scheme.** Tags for named things add characters, not remove them. "the Hobb cattle" is about
  4 tokens and "H1" about 2; the daily message is about 2,400 characters and the system text 14,000, so the saving is negligible.
  Codes also leak into speech ("drive H1 to P3") and make the agents' talk less like people's.
- **Unique descriptive names generated by the engine** ("the strays by the brook"). Natural to read, but they change as the thing
  moves, and agents must copy them exactly.
- **Fix only the herd split names.** Fixes the worst case; the bundles, the body and offers have the same problem.

## Open questions

1. Strangers' groups and things. 37.4's view: the world's tag for anyone who perceives the thing. One tag for everyone is what
   makes talk exact; it lets an observer tell that a stranger's group seen twice is the same one, which neighbours can mostly do by
   sight anyway.
2. (Answered by Zach, 2 Nov: speech is the agents' own; they say what they say.)
3. Individual beasts (point 8): deferred; groups of one carry most of the value.
4. Whether names spread beyond household and presence: free speech is not parsed (knowledge.md §4e), so a name told in passing
   does not teach the engine anything; an explicit act (`explain` a name) could.

## Affects

prompt.py, view.py, perceive.py and signs.py (rendering), verbs.py (resolving), herds.py (split names), things.py; proposals
verbs.md, agent_view.md; spec information/prompts.md, agents/actions.md.

## History

- 2 Nov 2026: proposed (37.4) from Zach's question, with the c3_combe_rich evidence.
- 2 Nov 2026: revised after Zach ("things without names they can name, meaning they can call it by that thing later ... would it
  be that names are an individual thing, where people hear names from others"; "would individual cattle be too much?"): naming
  added as a second step, names held as knowledge by the namer, those present and the household (point 7); individual beasts
  deferred, groups of one standing in (point 8); speech left to the agents.
- 2 Nov 2026: accepted and built as D4-68 (Zach: "build all five"), as a world setting (`tags: true`): tags for groups of beasts
  and things lying at a spot; naming known to the namer, those at the place and the household; by a herd's name, the group with
  beasts in it. Not built: documents, offers and agreements tagged (not in the engine yet, or already ids), naming places.

## Sources

runs/c3_combe_rich; review 38.41; cybertron2/engine/herds.py `split`, verbs.py `_take`, `_drive`.
