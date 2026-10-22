# 37.5 Frontier and exploration

## Goal
Room to grow that has to be earned together: land beyond the settled area that a society can open only by sending people, at a
cost and a risk, so expeditions, sponsors, charters and claims become reasons for institutions.

## What exists
- Projects (`projects.py`): funded thresholds that open a road (a new camp with rights to contributors), a discovery, a granary or
  a camp upgrade.
- World events: `camp_discovered` (a new camp; the discoverer learns of it).
- Clearing forest into fields (farming).
- Jurisdictions can be founded; outside powers raid.

## Design
1. **Unexplored regions** held by the engine, hidden from agents: each holds land of some kind (forest, fields, a copper or stone
   deposit, a spring, nothing) and a danger level.
2. **Expeditions:** an agent (or a party) spends rounds away (no other actions), brings food for the trip, and faces a chance of
   injury or death that falls with party size, arms and skill. On return the party reports what it found; nothing is opened yet.
3. **Opening and claiming:** a found region is opened by work (clearing, a road project) and claimed by a rule: the finder, the
   sponsor who paid for the expedition, the polity by law, or first come. The rule is law, so it is contested.
4. **Sponsors and charters:** expeditions are expensive, so they invite investment (an expedition company with shares in what is
   found) and charters (the council grants a monopoly on a region). With 37.3 a chartered company is an institution under the
   polity.
5. **Pressure:** population growth (37.1) and soil depletion (37.4) make new land valuable over time.

## Spec keys (sketch)
`frontier.regions {n, kinds, danger}`, `frontier.expedition {rounds, provisions, risk}`, claim rules as library laws.

## Acceptance (dry runs)
- Scripted expeditions find regions at the configured rates, cost what they should, and kill at the configured risk.
- An opened region adds plots, forest or a camp, held by the claim rule in force.
- Without growth or depletion, few expeditions are worth it; with them, opening land raises carrying capacity.

## Non-goals
A map with distances (space); conflict with other societies over land (a later package).
