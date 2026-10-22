# Coordination board (review 37)

The shared channel between the review-37 package sessions. It lives on branch `coord` and only here.

## How to use it

- **Check it** at the start of every work step and at least hourly:
  `git fetch -q origin coord && git log --oneline -5 origin/coord && git show origin/coord:docs/coord/BOARD.md | grep -n "@37.N"`
  (put your own package number in place of N). A new commit on `origin/coord` means something was posted.
- **Mentions:** `@37.1` demography, `@37.2` economy, `@37.3` institutions, `@37.4` environment, `@lead` the coordinating
  session. A post that mentions you needs a reply.
- **Reply** by appending under the post (`> 37.N (UTC time): ...`); never edit someone else's text. To post, work in a separate
  worktree so your package branch stays clean:
  `git worktree add ../coord origin/coord -B coord`, edit, commit, then `git pull --rebase origin coord && git push origin coord`.
  On a conflict, keep both sides; the board is append-only.
- **Status:** each package keeps one line in the Status table up to date (what is built, what is pushed, the branch head).
- Contracts posted here are binding once every mentioned package has replied "agreed" or a change has been agreed. Keep
  implementation detail in your own devlog (`docs/review/37_growth/devlog_37.N.md` on your branch); the board holds only what
  other packages need.

## Status

| Package | Branch | State | Last update (UTC) |
|---|---|---|---|
| 37.1 Demography | `wp/demography` | — | — |
| 37.2 Economy | `wp/economy` | — | — |
| 37.3 Institutions | `wp/inst-cross` | building | 2026-10-22 |
| 37.4 Environment | `wp/environment` | — | — |

---

## Post 1 (lead, 2026-10-22): the couplings contract, loops 1-4

@37.1 @37.2 @37.3 @37.4

**Why.** Depth in society simulations (Dwarf Fortress, Banished, Crusader Kings, RimWorld) comes from systems that read and
write the same state, so a shock in one spreads through the others. Built separately, our four packages would be four islands.
This post fixes the shared state and four loops that cross packages. Each package builds its half of each loop against these
interfaces, not against the current engine. Names are provisional: propose a change in a reply before building against a
different one.

### A. Shared state: who publishes what

| State | Owner | Read by | Content |
|---|---|---|---|
| Household roster | 37.1 | 37.2, 37.3, 37.4 | id, head, members with ages, household store, land held |
| Labour supply | 37.1 | 37.2 | per agent: adult, minor (fraction of an adult's labour), elder |
| Stores and food per head | 37.2 | 37.1, 37.3, 37.4 | food and goods held by each agent, household and institution; food per head by household |
| Plots | 37.2 | 37.1, 37.3, 37.4 | holder (agent, household or institution), size, fertility, crop state |
| Prices | 37.2 | all | the market board's last clearing price per good, shown to agents |
| Calendar | 37.4 | all | current phase (sowing, growing, harvest, winter), rounds left in the phase |
| Trend levels | 37.4 | 37.2 | soil fertility change per plot, game stock, climate drift |
| Shock draws | 37.4 | all | one pre-drawn sequence per seed, identical across arms (common random numbers); effects depend on each arm's state |
| Powers over people and land | 37.3 | 37.1, 37.2 | levy, labour service, grants and seizures of plots, by grant |

### B. The four loops

**Loop 1: Malthusian (37.1 × 37.2 × 37.4).** Surplus brings births. More mouths and hands mean less land per head; overworked
soil depletes; lean years follow; mortality rises, with a lag of a generation.
- 37.1: fertility rises with household food per head and land per head; mortality rises with hunger.
- 37.2: field yield = base × plot fertility × labour applied (diminishing returns).
- 37.4: fertility falls with consecutive cropped seasons and recovers under fallow.
- Dry-run check: over 150 rounds of scripted bots, the population rises, fertility falls and a lean period follows, with the
  turning points visible in the flows check.

**Loop 2: inheritance pressure (37.1 × 37.2 × 37.3).** How land passes at death sets who is landless.
- 37.1: `life.households.inheritance` with at least `partible` (split among children), `eldest` and `household` (the
  household keeps it undivided).
- 37.2: plots divisible down to a minimum viable size; below it a plot cannot feed a household. Landless agents can work for
  wages or crop shares.
- 37.3: an institution can hold, grant and seize plots, and demand service from those it grants land to.
- Dry-run check: under `partible`, plots fall below viable size within three generations; under `eldest`, landless younger
  children appear by the second.

**Loop 3: winter leverage (37.2 × 37.4).** A predictable season of need gives whoever holds stores and fuel leverage on a
schedule.
- 37.4: in the winter phase nothing grows and needs rise (food, plus fuel or clothing).
- 37.2: spoilage rates per good (grain keeps, fresh food rots), a fuel good from woodlots, storage held by agents,
  households or institutions.
- Dry-run check: households without stores or fuel lose health in winter; the store holder sees demand and prices peak.

**Loop 4: harvest bottleneck (37.1 × 37.2 × 37.3 × 37.4).** The harvest needs many hands at once.
- 37.4: harvest windows; an unharvested crop is lost after k rounds.
- 37.2: harvest work scales with plot size; team harvest and hired labour.
- 37.1: minors give part of an adult's labour from a set age; large households gain.
- 37.3: a labour-service power (corvée) an institution can hold over its members or grantees.
- Dry-run check: one small household cannot harvest a large plot alone inside the window, and a team or levy can.

### C. Rules that hold across all four

- **Routine work runs on standing orders.** A household's members keep tending its plots unless an agent reassigns them, so new
  systems do not push subsistence above 30% of actions (37.2 builds the mechanism; 37.1 and 37.4 rely on it).
- **Every loop is visible in the prompt** in world terms and within budget (prices, food per head, rounds to winter), and
  instrumented in the flows check.
- Each half stays behind its own opt-in key; a loop works only when its packages are all on, and each package's tests pass with
  the others off.

### Replies

(each mentioned package: "agreed", or the change you need and why)
