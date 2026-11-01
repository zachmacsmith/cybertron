# 02zg: build brief for 37.4: fitting work over days, and ground shown used and free

Session 37.2, 3 Nov 2026. **Zach asked for these two to be built** (3 Nov: "1. Yes. 2. Yes", on the list of what was ready).
README rule 10: nothing else here is to be built. Plot shares (D2-163) wait for a design question to Zach; Package E stays
deferred; no calibration numbers change.

## 1. The fitting-work bug

**Now:** `_build` in verbs.py puts a fitting in with one 2-unit action and never reads `FITTINGS[x]["units"]`. A cellar (8 units),
millstones (10) and a water wheel (12) cost the same labour as bins (1).

**Build:** a fitting's work is charged over days like a building's (spec/economy/buildings.md "Fittings": "its work is charged
over days like a building's (each `build` action does 2 units, more with skill, until its work is done)").
- The materials go in when it is started.
- The building then carries the unfinished fitting with its units left (for beds, the units a bed × the number).
- Each later `build {what, at}` on it does its units.
- It counts (sleeps, stores, grinds, warms) only when finished.
- The building's signs show work under way, as for a building.
- The skill roll stays as now, at the start.

**Tests:**
- bins (1 unit) are finished in one action;
- a cellar (8 units) needs 4 actions, and food put in before the last keeps at the house rate;
- 3 beds (1 unit each) take 2 actions;
- a second start of the same fitting while one is unfinished carries on the first, and takes no more materials.

## 2. D2-164: ground and plots shown used and free

**Now:** each parcel's line names its cover, holder, fence, crafts and buildings, but not its size or how much room is left. The
first an agent learns of a full parcel is the refusal "there is no room left to build on …".

**Build:** add to each parcel's line, in the prompt's place lines and in the belief view's lines for here, as the agent last saw it:
- **built ground and scrub:** buildings and room left, in the engine's current lots (6 a unit of size on built ground, 4 on scrub)
  until Package E's spaces: "the Green (built ground; 5 buildings, room for 1 more)";
- **fields, pasture and meadow:** the size in plots: "Long Field (field; 6 plots; held by the Reeds)".

No new mechanics.

**Tests:**
- the Green of size 1 with 5 buildings reads "room for 1 more";
- with 6 it reads "no room left";
- a field of size 6 reads "6 plots";
- the refusal text is unchanged.

## Sources

D2-164 (DECISIONS.md); spec/economy/buildings.md (Fittings; What agents see); review 02zf (calibration, for context only).
