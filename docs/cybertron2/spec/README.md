# cybertron2 spec

The spec is a folder of areas, each a folder of small files, one per topic. Every file uses the same layout: **Summary**;
**Decided** (rules with their decision numbers, from ../DECISIONS.md); **Mechanics** (precise enough to build); **Data** (the
state it adds); **Parameters** (value and status: decided, proposed, calibrate); **What agents see**; **Open** (links to
../OPEN.md); **Sources** (the notes it was compiled from). A file is written when it is compiled; until then it is listed here as
*to compile*.

| Area | What it covers | Owner |
|---|---|---|
| [core/](core/README.md) | The engine itself: how state changes, how a day runs, what is recorded | 37.4 |
| [world/](world/README.md) | Places, land and the map | 37.4 |
| [agents/](agents/README.md) | What an agent is and can do | 37.4 |
| [information/](information/README.md) | What agents know and how it moves | 37.4 (37.2: writing materials, papers' economics) |
| [environment/](environment/README.md) | The world changing over time | 37.2 (D2-75; 37.4 builds) |
| [economy/](economy/README.md) | Goods, production and trade | 37.2 (37.4: carrying and lodging mechanisms) |
| [conflict/](conflict/README.md) | Force, defence and danger | 37.4 (37.2: the economics of walls and gates) |
| [life/](life/README.md) | People over their lives | 37.4 (until 37.1 joins) |
| [institutions/](institutions/README.md) | Institutions from households to states | 37.4 (until 37.3 joins) |
| [seeding/](seeding/README.md) | Starting worlds | 37.4 |
| [measurement/](measurement/README.md) | What we measure and how | 37.4 (37.2: economic measures) |
| [record/](record/README.md) | How a run is recorded, run, branched, viewed, exported, published and imported | 37.1 (37.4: the engine code that writes it) |

Owners decide what goes in their files (../README.md, rules 2-3). Shared files say which part each session owns.
