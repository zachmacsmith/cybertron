# viz.json: the contract between the model and the renderer

`c2viz/model.py` (Python, the engine's side) writes it; `c2viz/js` (the renderer) reads only it. When the engine changes, the model
changes to keep this contract; if the contract itself must change, `c2viz/schema.py` `SCHEMA_VERSION` goes up and this file says
what changed. `schema.validate` checks a viz.json (the build prints any problem; the tests require none).

Schema version: **1**.

| Part | Holds | Built by |
|---|---|---|
| `meta` | `name`, `days`, `seed`, `source`, `people {name: {household, model}}`, `season_days`, `schema` | model.build |
| `tables` | the engine's tables the renderer may read (covers, crops, fittings, blueprints, fences, weather, seen, height, things, terrain, landmarks, event_extent) and `spec` (the space model: spaces, ground, rooms) | touch.tables, spec_rooms |
| `static` | `nodes {id: {name, text, unexplored}}`, `parcels {id: {node, name, cover, size, side, height, adj, text, ground}}`, `roads {id: {a, b, days, track, way, terrain, stretches, ends {node: {side, parcels, hidden}}}}`, `layout {world, nodes}` (presentation positions, layout.py) | model.static |
| `days[]` | one record a day, the state after its night (below) | extract.day_record |
| `days[].timeline` | the day as it happened (below), when built with timelines | timeline.timeline |

## A day

`day`, `calendar {season, day, left, year_day}`, `cold`, `weather`, `words`, `wet`, `snow`, and:

| Key | Each record |
|---|---|
| `parcels {id}` | `cover`, `was`, `fertility`, `soil`, `res {stock: S/K}`, `dung`, `felled`, `smoky`, `high`, `sight`, `broken` (share), `last_crop`, `last_kind`, `fallow_since`, `holders`; `crop {kind, family, stage, progress, sown, reaped, weeds, trampled}`; `works {ground, done, begun, unkept}`; `fence {kind, level, built, gate}`; `clearing` (share); `ground_spaces` |
| `buildings {id}` | `node`, `parcel`, `name`, `structure`, `condition`, `door`, `fire`, `warm`, `fittings`, `new`, `crowded`, `worked_on`, `made [techniques]`, `sleepers`, `holders`, `stock {food, timber, firewood, weight}`, `seen_as`, `rooms [{kind, floor, storey}]`, `derived`, `floor`, `used`, `footprint`; `unfinished {blueprint, done}`; `nights_left` |
| `herds {id}` | `node`, `parcel`, `home`, `name`, `kind`, `cows`, `oxen`, `bulls`, `young`, `in_milk`, `hungry`, `watched`, `holders`, `with`, `pack`; `road`, `pos` when on a road |
| `things {id}` | `kind` (pile, remains, carcass), `node`, `parcel`, `in`, `door`, `of`, `beast`, `goods`, `weight`, `heap`, `hidden`, `buried`, `cairn`, `body` (fresh, days, bones), `rotting`, `died`; `fresh`, `bones` (carcasses); `stretch` (on a road) |
| `people {name}` | `at`, `alive`, `died`, `cause`, `stage`, `sex`, `hunger`, `missed`, `wounded`, `household`, `homes`, `slept`, `worked`, `spot`, `carried`, `gear`, `arrived`, `pregnant`; `transit {road, from, to, pos, days}` |
| `roads {id}` | `ends {node: {worn, used}}`, `challenges {"stretch:landmark": challenge}` |
| `traces`, `fights`, `acts` | as the engine keeps them |
| `events []` | `id`, `place`, `kind`, `actor`, `target`, `about`, `text`, `salience`, `tech`, `dawn`, `extent` (node, building, parcel) |

## The day as it happened (`timeline`)

`from` (the step replayed from), `morning {parcels, buildings, herds, things, people}` (records as above, before the work), `acts []`
(`actor`, `verb`, `for`, `tech`, `site`, `node`, `units`, `t0`, `t1` (presentation: units against the day's), `delta {parcels,
buildings, herds, things, carried}`: the records an act changed, after it), `routes {name: [parcel]}` (the engine's, D4-62; `routes_derived` when the run predates the engine keeping them and the engine's rule was applied afterwards),
`budget {name: units}`, `talk [{actor, place, kind, text}]`, `unreplayed` (changes that did not replay: 0 when all is well).

## Words the renderer knows

The renderer reads the engine's own words for covers, structures, crop families and stages, fittings, techniques, herd roles,
terrains and event kinds. Those it draws differently are listed in `js/vocab.js` (and the colours of covers and roofs in
`js/palette.js`, `js/buildings.js`); a word it does not know is drawn plainly, never an error.
