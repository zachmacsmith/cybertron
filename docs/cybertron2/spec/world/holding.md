# Holding land and fixed things

## Summary

To hold something is to have **a claim that others recognise**. The engine enforces only **possession** (who is physically there
and doing it); **claims** are records and memories; **recognition** (by neighbours' custom, or by an institution's register) is what
makes a claim a holding; **enforcement** is people acting. Land is counted in **whole plots**; holdings are divided, plots never.
Individuals, households, institutions and joint holders can hold; two claims on one thing is a dispute, settled by giving way,
force, an arbiter or an institution above both.

## Decided

- D4-23 (Zach, 22 Oct): everything in this file but "Wood".
- D2-158: dead wood, and young growth on common land, are anyone's to gather; trees are their holder's.
- D4-60: clearing new ground for fields.
- D2-163: land is held in plot shares within a parcel.
- D2-172: a field carries one crop for each holding on it.

## Mechanics

### Possession (physics)

- Anyone present at a node can physically use any site there: sow or reap a plot, graze a pasture, draw from a well, dig a seam.
  The engine never refuses it for want of a right.
- What is taken belongs physically to whoever carries it. A crop belongs to nobody until reaped; the reaper carries the harvest.
- Every use is witnessed by those present (information/perception), so using land against a claim is seen and remembered.

### Claims

A claim is a record about something that cannot be carried: a **plot**, a building, a lot, a well, a seam, a pasture.

| Field | What |
|---|---|
| `thing` | the plot or site (with its node) |
| `claimant` | an agent, a household, an institution (village, company, polity), or a list of agents holding jointly |
| `rights` | any of: `access` (use it), `withdrawal` (take its produce), `management` (decide what is done with it, improve it), `exclusion` (decide who else may use it), `alienation` (sell, let, bequeath) |
| `grounds` | `seeded`, `cleared`, `inherited`, `granted` (by whom), `bought` (from whom), `seized`, `custom` |
| `since` | the round |
| `recognised_by` | the institutions whose registers record it (none: a bare or customary claim) |

Rights can be split among claimants: a tenant holds access and withdrawal, a lord exclusion and alienation, the village sets
rules on fallow and common grazing.

### Recognition

| Recognised by | What it gives |
|---|---|
| the claimant only | a **bare claim**: it lasts as long as the claimant holds the land physically |
| neighbours, by custom | a **customary holding**: others leave it alone; breaking it costs standing with them (memories and relationships) |
| an institution's register | a **recognised holding**. The institution's code may refuse its own members' trespass outright (members consented to its rules by joining); outsiders it can resist only by force, or answer in its court if they accept it |
| two institutions that disagree | a dispute between institutions: a border, a war, a treaty |

What an individual believes about a claim is in its knowledge store (it was told, saw a grant, read a deed). A register is a
document at an institution's seat (information/letters_and_documents). Two people can believe different things about the same
field.

### Kinds of holder

- **An individual** holds personally, decides alone; at death the claim passes by its household's inheritance custom
  (life/birth_and_death).
- **A household** holds as an institution: its members may work it, the head manages it, the household's rule decides whether it
  can be sold or divided.
- **An institution** (common land, company land, a lord's demesne, a polity's) holds under its own rules: who may graze, how many
  beasts, whose turn it is.
- **Joint holders** (co-heirs, partners) hold together; how they share is their arrangement.

### Disputes

Two claims to the same rights over the same thing make a dispute (a feud between people, a border between institutions). Both
sides can act on it: sow, reap, stand guard, fight (conflict/). It ends when one side gives way, force settles it, both accept an
arbiter (an elder, a court) and live by the ruling, or an institution over both decides and its members enforce it.

### Plots

- **Land at a node is counted in plots**, a fixed unit per world: about what one adult can work in a season. A node's land kind
  sets how many arable plots it has and their fertility range (world/parcel_graph.md; land.md was never written); clearing and draining add plots; abandoned plots
  return to scrub and forest.
- **Clearing (D4-60):** a meadow or pasture (6 units of work a unit of size) or scrub (10) is cleared into a fallow field; a wood
  is felled to scrub first. Land nobody holds is held, once cleared, by whoever cleared it (grounds `cleared`).
- **Plots are whole: never split. Holdings are divided.** Fragmentation and a landless class come from this, with no split
  primitive.
- **Plot shares (D2-163):** a parcel is one place; what is held, divided among heirs, sold and disputed is a number of its plots. A
  claim on a field, pasture or meadow may name a number of its plots (`plots: n`); a claim without one covers all of them. One
  holder's claims on a parcel add up, to its plots at most.
- **Overlaps are disputes (D2-163, D4-23):** claims on one parcel may come to more than its plots; both are recorded, neither is
  refused. A claim of more plots than are unclaimed records whose plots it overlaps (the holder with the most plots there).
- **Unclaimed plots** are the parcel's plots less what its claims cover, at least 0.
- **Claiming (D2-163):** `claim {thing, plots?, for?}`: unclaimed plots are claimed like anything else; claiming plots others hold is
  allowed, and seen as a dispute.
- **Inheritance (D2-163, D2-143):** a holding passes in whole plots by the household's rule: eldest, all to one heir; partible, among
  the heirs, eldest first (5 plots to 2 heirs: 3 and 2); where there are more heirs than plots, each of the first heirs takes one
  plot and the last plot is held jointly by the rest (by the household where they are of it, with the co-heirs named as joint
  holders, who have its rights). The soil and any crop standing go with the plots.
- **Clearing (D4-60, D2-163)** claims all of the cleared parcel's plots.
- **Pasture and meadow (D2-163)** are held in plots too; grazing and hay stay whole-parcel: any holder's herd grazes the whole
  pasture.
- **Fences (D2-130)** stay round the whole parcel.

### A crop for each holding (D2-172)

- **The record:** each holding on a field has one record: holder, plots, crop (kind, seed, broken share, weeding, sown day, sower,
  failed), fertility, broken ground, last crop. The ground held whole (by the claims that cover all of it), or where nobody holds it
  whole the unclaimed plots, is the field's own record. The crops on a field together cover no more than its plots.
- **Sowing** (`work {what: sow, at, item, plots?, on?, for?}`) sows the sower's own (or the `for` party's) held plots that are
  unsown, then the unclaimed plots, then stops; `plots` caps the act. Sowing plots another holds needs `on: <party>`: allowed, and
  seen. A holding carries one crop: its unsown plots take only the crop already on it.
- **Breaking, weeding, manuring, choosing seed and reaping** fall on one's own holding (the party's, one's own, one's
  household's) where one has one with that work to do; else on the unclaimed plots; else, where exactly one holding has that work
  to do, on it; else one names whose (`on`). Working another's holding is allowed and seen ("Ann was reaping at Long Field on the
  Webbs' plots"), concerning that holding's people.
- **Reaping another's holding** gives the grain to the reaper (a crop is nobody's until reaped).
- **Fertility** is kept per holding: each crop's slot, fallow, grazing and dung act on its holding's soil. Plots moving between
  holders take their soil with them (plots given up are pooled with their soil; plots gained are drawn from that pool first, then
  from the unclaimed plots).
- **A crop standing on plots that change hands by an agreement** stays with the holding that sowed it until reaped; a holder of the
  whole who comes to hold part keeps the crop it had on the whole. On inheritance (and in a world file) the crop goes with the plots,
  split by plots.
- **Herds on a field** graze its stubble and fallow holding by holding, and trample every standing crop at the trampling rate (D2-123),
  so the loss falls on the holdings by their plots.
- **Signs** are per crop record and, on a field held in shares, name the holding: "the Reeds' barley in Long Field stands ripe",
  "stubble in the Wynns' part of Long Field" (information/signs.md). A field held whole reads as before.
- **Minimum viable is land per mouth, not a plot size:** the plots a household needs to feed itself through a year at its land's
  fertility and yield (37.2 calibrates). Agents see it in words ("your land can feed about 3 of your 5"). Below it, a household
  rents, works for others or leaves.

### Moving a claim

One routed primitive, `transfer_claim {thing, rights, to, why}` (why: `inherited`, `granted`, `sold`, `let`, `seized`, `cleared`,
`abandoned`), so institutions' laws can hook every change (37.3's grants and seizures, 37.1's inheritance). Recording a claim in a
register is a separate act by the register's keeper.

**Plots by agreement (D2-163):** an agreement's leg "2 plots of Long Field" moves n plots of a parcel from one party to another when
the offer is taken (the giver's claims there give them up, newest first; the getter has a claim of n plots, grounds `bought`).
Only a party that holds the plots, by one who may part with them (`alienation`), can give them.

### Wood (D2-158)

A forest or scrub parcel's three stocks (environment/resources.md "Forests") are held differently:

| Stock | Whose |
|---|---|
| dead wood (firewood gathered by hand) | anyone's, on any land |
| young growth (cut with a tool) | anyone's on common land; the holder's on held land (cutting it there is using what others hold: seen and remembered) |
| trees (felled for timber) | the parcel's holder's (felling another's is heard: the ring of axes) |

### Carried goods

Simpler: what is in your hands or your house's stock is yours unless someone saw you take it. Stolen goods are a matter of witnesses
and memory, not a claim record.

## Data

- `claims`: a list of claim records (above), each with an id; on a field, pasture or meadow, `plots` (none: all of them), and for a
  dispute `of` and `over` (whose plots it overlaps, and how many); `joint`: co-heirs holding one share together (D2-163).
- A field's records (D2-172): the parcel's own crop and soil (the ground held whole, or the unclaimed plots), `held_whole` (who
  holds it whole), and `shares`: one record for each holding of part of it.
- `registers`: per institution, the claim ids it records (its document).
- Plots, buildings, lots and sites carry no holder field of their own: who holds them is read from the claims.

## Parameters

| Parameter | Value | Status |
|---|---|---|
| plot size (work per season) | about one adult's | proposed; 37.2 calibrates |
| plots per node by land kind | world/parcel_graph.md (land.md was never written) | proposed |
| land per mouth for viability | 37.2 | calibrate |

## What agents see

A field's line (D2-163, D2-172): "Long Field (field; 6 plots; barley on 4 (Reeds 3, Webbs 1), beans on 1 (Coles), 1 fallow;
held: Reeds 3, Webbs 2, Coles 1)"; a dispute: "the Wynns claim 2 of the Reeds' plots"; a field held whole keeps "held by the
Reeds", with what stands on it ("barley on 5").

In world terms, from what each knows: "The Long Field: the Alders' (Bram's grandfather cleared it; the village register agrees).
The Wynns claim it too, since the flood moved the stream." "The upper pasture: the village's common; each household may graze four
beasts." "Your land can feed about 3 of your 5."

## Open

- Seeded worlds start with claims, a village register and some old disputes (seeding/populations).
- How claims show in the prompt within its budget (information/prompts).

## Sources

The 37.4 conversation with Zach, 22 Oct; Schlager and Ostrom (1992) on bundles of rights; 37.2 02f §6.5 ("plots whole, holdings
divided"); 37.1's inheritance (`wp/demography`); 37.3's tenures (`wp/inst-cross`); cybertron 1's D-37 (consent binds members).

*Current as of 3 Nov 2026: D4-23, D2-158, D4-60, D2-163, D2-172.*
