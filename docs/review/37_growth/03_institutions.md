# 37.3 Institutions acting on each other (gap G-3)

## Goal
A society of institutions, not islands: a polity's law taxes a guild; a guild's charter is granted and revoked by the council; a
league court rules on member polities; a firm's contract binds an association's store; a sub-institution operates under a parent's
rules.

## What exists
- Institutions (polity J0 and associations A1...) each have their own laws, offices, treasuries, stores and procedures.
- Laws read other laws' public records (`public_of`), the pattern used by the Warrant Act's sources and the Cooperative's credit
  orders.
- Finding (review 31.12): one institution's laws cannot read or move into another's; the Food Co-op had to be J0's own law.

## Design
1. **A permission model.** An institution holds **powers over** another only by grant: a charter (the parent grants a child its
   existence and powers, revocable), a treaty (two institutions grant each other named powers), or membership (an institution as a
   member of another, e.g. polities in a league). Every cross-institution act names the power it uses.
2. **An API for laws**, gated by those powers: read another institution's records and holdings; levy on its treasury or store;
   appoint or remove its officers; enact into its code (as a parent); refuse its actions (a before-hook on its primitives);
   transfer between institutions' accounts.
3. **Hierarchy:** institutions under a polity (guilds, firms, households, wards) with the parent's constitution as the top rank
   their codes must respect; conflicts resolved by rank and precedence, as within one institution.
4. **Visibility:** each cross-institution act is logged with the power it used, so capture of a sub-institution by a parent (or the
   reverse) is measurable.

## Spec keys (sketch)
`institutions.cross: true`; charters and treaties as library templates; law API functions `of(iid).levy(...)`, `appoint(iid, office,
agent)`, etc., refused without the power.

## Acceptance (tests)
- A council law levies a guild's treasury only while the guild's charter grants the levy; revoking the charter stops it.
- A guild cannot act on the council's store without a granted power.
- A league court's ruling binds a member polity's office.
- Old worlds replay unchanged.

## Non-goals
Space and distance between institutions (37.5 and later).
