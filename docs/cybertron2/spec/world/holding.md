# Holding land and fixed things

## Summary

To hold something is to have **a claim that others recognise**. The engine enforces only **possession** (who is physically there
and doing it); **claims** are records and memories; **recognition** (by neighbours' custom, or by an institution's register) is what
makes a claim a holding; **enforcement** is people acting. Land is counted in **whole plots**; holdings are divided, plots never.
Individuals, households, institutions and joint holders can hold; two claims on one thing is a dispute, settled by giving way,
force, an arbiter or an institution above both.

## Decided

- D4-23 (Zach, 22 Oct): everything in this file.

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
  sets how many arable plots it has and their fertility range (world/land.md); clearing and draining add plots; abandoned plots
  return to scrub and forest.
- **Plots are whole: never split. Holdings are divided.** Partible inheritance deals whole plots, eldest first; where there are
  more heirs than plots, the rest is held jointly (by the household or the co-heirs) or the younger heirs get none. Fragmentation
  and a landless class come from this, with no split primitive.
- **Minimum viable is land per mouth, not a plot size:** the plots a household needs to feed itself through a year at its land's
  fertility and yield (37.2 calibrates). Agents see it in words ("your land can feed about 3 of your 5"). Below it, a household
  rents, works for others or leaves.

### Moving a claim

One routed primitive, `transfer_claim {thing, rights, to, why}` (why: `inherited`, `granted`, `sold`, `let`, `seized`, `cleared`,
`abandoned`), so institutions' laws can hook every change (37.3's grants and seizures, 37.1's inheritance). Recording a claim in a
register is a separate act by the register's keeper.

### Carried goods

Simpler: what is in your hands or your house's stock is yours unless someone saw you take it. Stolen goods are a matter of witnesses
and memory, not a claim record.

## Data

- `claims`: a list of claim records (above), each with an id.
- `registers`: per institution, the claim ids it records (its document).
- Plots, buildings, lots and sites carry no holder field of their own: who holds them is read from the claims.

## Parameters

| Parameter | Value | Status |
|---|---|---|
| plot size (work per season) | about one adult's | proposed; 37.2 calibrates |
| plots per node by land kind | world/land.md | proposed |
| land per mouth for viability | 37.2 | calibrate |

## What agents see

In world terms, from what each knows: "The Long Field: the Alders' (Bram's grandfather cleared it; the village register agrees).
The Wynns claim it too, since the flood moved the stream." "The upper pasture: the village's common; each household may graze four
beasts." "Your land can feed about 3 of your 5."

## Open

- Seeded worlds start with claims, a village register and some old disputes (seeding/populations).
- How claims show in the prompt within its budget (information/prompts).

## Sources

The 37.4 conversation with Zach, 22 Oct; Schlager and Ostrom (1992) on bundles of rights; 37.2 02f §6.5 ("plots whole, holdings
divided"); 37.1's inheritance (`wp/demography`); 37.3's tenures (`wp/inst-cross`); cybertron 1's D-37 (consent binds members).
