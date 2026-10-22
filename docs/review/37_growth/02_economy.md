# 37.2 Agriculture and a thicker economy

## Goal
An economy where people specialise because it pays, need each other's products, and where money buys things: the precondition for
markets, firms, guilds, taxes and the dependencies that make societies worth capturing.

## What exists
- **Farming (engine 14, review 31.01b), off by default:** fields camps with plots held by agents or institutions (`start.farms`),
  sow/tend/reap, crop shares paid to the holder, improvements (terraces, irrigation, shed, plough) with upkeep, skills (rotation,
  seed selection), clearing forest into fields, per-hunter hunting with party returns. **Shared fields held by an institution exist**
  (an association's members or an institution's officers farm its plots). The bench-36 worlds did not switch it on.
- Materials: copper, timber, stone; recipes (blade = 25 copper + 1 timber; crude weapon; forts; stores); typed camps (tutorial dial
  camps, a cartel copper camp with a quota input); `sell_to_window`; the market board; currencies, loans, banks; payroll and supply
  contracts; licences on camps and recipes.
- Observed: food is the only consumed good; dial camps are search puzzles that eat attention; money had little to buy (Millbrook).

## Design
1. **Farming on by default in institutional worlds**, calibrated so a farm worked well yields a surplus (1.3-1.6x the farmer's
   household), fields can be held by households, firms or the polity, and tenancy (crop share) is a real choice.
2. **Several consumed goods**, each with a reason to want it:
   - clothing or shelter (without it, hunger costs more, or health falls in lean seasons);
   - tools (raise a producer's yield by a factor, wear out, made by a smith from copper and timber);
   - prepared food (bread from grain through a mill or oven: a conversion step someone can own).
3. **Specialisation that pays:** skills learned by practice and teaching raise output in one trade; a generalist does everything
   poorly. Replace dial camps with simple extraction actions plus skill.
4. **Team production:** a mine or a large field that needs a crew (output rises with crew size up to a point), so firms and
   cooperatives have something to organise.
5. **Money that closes the loop:** prices on the market board, wages payable in coin that buy food and goods, taxes payable in coin.
6. **Flows check** extended to every good: supply, demand, who can produce it, who cannot (the dependence graph of the world).

## Spec keys (sketch)
`subsistence.fields.enabled` (exists), `economy.goods {clothing, tools, bread}` with recipes and needs, `skills.trades`,
`camps.crew {min, best, returns}`.

## Acceptance (dry runs)
- In a 24-agent world with farming, tools and bread on, scripted producers specialise (output per worker higher for specialists),
  a market clears at stable prices, and money circulates (velocity ≥ 0.1 a round).
- Every good has at least one group that cannot produce it.
- Subsistence actions ≤ 30% of all actions in normal rounds.

## Non-goals
Price discovery at scale (24 agents is too thin), long-distance trade (needs space).
