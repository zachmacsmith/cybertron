# 37.7 Coordination problems

## Goal
Problems that only collective action solves, so institutions arise because the world rewards them: defence, storage against lean
seasons, works that multiply output, and order in crowded commons.

## What exists
- Projects (roads, granaries, upgrades, discoveries) funded by contributions, with assurance contracts.
- Outside power raids (abstract stock losses; a garrison cannot fight them: gap G-29).
- Commons laws (quotas, caps, Ostrom's rule), hunting parties, the militia and muster.

## Design
1. **Defence that works (G-29):** raids are fought. Defenders on watch (guards, militia, a garrison) reduce or repel a raid by
   their number, arms and forts; an undefended target loses more. Paying tribute stays an option. So a garrison earns its keep,
   and who controls it matters.
2. **Storage against predictable lean seasons** (37.4): food spoils outside stores, a granary keeps it, and building and filling one
   needs contributions. Who keeps the key is the old principal-agent problem.
3. **Works with returns:** irrigation (fields' yields up for everyone on the channel), walls (raid losses down), roads (access to
   frontier land, 37.5), mills (37.2). Built by pooled labour or materials over several rounds; maintained or they decay.
4. **Crowded commons:** as population grows (37.1), open forests deplete unless a rule limits use; the rule needs enforcement.
5. **Incentives to scale:** larger cooperating groups get more per head (up to a point) in defence, works and team production, so
   institutions that organise more people are better off.

## Spec keys (sketch)
`conflict.raids.defence {...}`, `projects.works {irrigation, walls, roads, mill}`, decay and upkeep per work.

## Acceptance (dry runs)
- A defended world loses less to raids than an undefended one, by the configured amounts.
- A world that builds a granary survives a lean season that kills in one that does not.
- A pooled work pays back its contributors within its design horizon.

## Non-goals
War between societies (later), formal public-goods games.
