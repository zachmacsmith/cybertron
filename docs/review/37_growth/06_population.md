# 37.6 Generated populations

## Goal
Worlds seeded as societies with a past, not as a set of strangers: interwoven family trees, households, occupations, holdings,
debts, friendships and rivalries drawn from distributions, and a short history, so that cross-cutting ties and conflicts of
interest arise naturally at any size, while any field can still be hand-set.

## What exists
- `start:` blocks: people, rights, offices with holders, holdings, stores, channels, contracts, laws (review 27).
- Personality (legacy traits; HEXACO and values with population shifts, review 34).
- Goals per agent (`goals.explicit`, `Aim`), positions for offices.
- Observed: every world so far was hand-placed; kinship lived only in prompt text; bench-36 conflicts of interest were planted one by
  one ("a headman is the miller's brother").

## Design
1. **A generator** (`population.generate`), deterministic by seed, writing an ordinary `start:` block (so a generated world can be
   saved, inspected and hand-edited):
   - **Family trees** over 2-3 generations: founders' ages, marriages, children, siblings and cousins, some dead (their estates
     inherited), with household membership (37.1).
   - **Occupations** allocated to match the world's labour demand (farmers, smiths, millers, soldiers, clerks), passed partly within
     families.
   - **Holdings** from a skewed distribution (a target Gini), land by household, tools and stores.
   - **A credit network:** who owes whom, drawn from wealth and kin distance.
   - **Relationships:** friendships, rivalries, grudges and debts of favour, from distributions conditioned on kin, occupation and
     neighbourhood; each agent knows its own.
   - **Offices with history:** holders chosen by the world's rules at a notional earlier time, plus a short chronicle of past
     holders and disputes (a few lines each agent can read).
   - **Temperament and values** drawn per agent, correlated within families.
2. **Prompts:** each agent's system prompt gets its own relations in a compact form (family, household, close ties, debts, rivals;
   within budget); the rest is discoverable (a register, the chronicle).
3. **Overrides:** any person, tie, office or holding can be fixed in the spec; the generator fills the rest around it.
4. **Parameters as experiment factors:** size, inequality, kin density, occupational specialisation, network density, institutional
   density, so a world is a draw from a distribution the experiment design can vary.

## Spec keys (sketch)
`population.generate {size, generations, households, occupations, wealth_gini, credit_density, ties, history}`,
`population.fixed {...}` for hand-set parts.

## Acceptance (tests and dry runs)
- The same seed gives the same society; the output is a valid `start:` block that loads and runs.
- Generated statistics match the targets (Gini, household sizes, tie densities) within tolerance.
- Hand-fixed fields survive generation unchanged.
- Each agent's prompt lists its own ties within budget.

## Non-goals
Realism of any particular culture.
