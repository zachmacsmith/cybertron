# Devlog 37.3: institutions acting on each other (gap G-3)

Branch `wp/inst-cross`. Brief: `03_institutions.md`. Newest entry last.

## 2026-10-22 17:10 UTC

**Doing:** reading the engine around institutions, laws and hooks; first design.

**Found:**
- One law API, one table: `Kernel.api_for` (cybertron/kernel.py:782-800) merges module `law_api(k, lid)` closures; every function
  needs a row in `cybertron/lawapi.py` (LAWFNS), docs in `cybertron/lawdocs.py`, and tests/test_cybertron_lawapi.py:66 checks the
  table against the real API with every module on. An association's law sees only functions whose row has `contract` "allow" or
  "escrow" (cybertron/contracts.py:982-988): a function without a row is denied to it.
- Scoping is per account: `jurisdictions.scope_api` (cybertron/jurisdictions.py:397) for polities, `contracts.scope_api`
  (cybertron/contracts.py:973) for associations. An association's move may take only from its treasury, its escrows, its funds and
  its own stores (contracts.py:999-1010): a guild already cannot act on the council's store.
- **The reverse is open.** With jurisdictions off (most established worlds, e.g. tests/test_standing_contracts.py:19), a J0 law's
  `move("assoc:A1", "reserve", "penny", 10)` succeeds: `scope_api` returns the API unscoped (jurisdictions.py:403-407) and
  `check_move` checks only estates, funds and stores (cybertron/dispatch/checks.py:28-35). Probed: A1's treasury went 50 -> 40.
  A J0 law cannot take from an association's *store* (accounts.py:183-208 raises). With jurisdictions on, `owner()` refuses
  another account's treasury (jurisdictions.py:422-439).
- With jurisdictions off every polity law sees every routed change (dispatch/hooks.py:58-90: no `jur` key, so no filter): J0's
  laws can already block an association's own acts. Associations' laws see only their members' changes (contracts.py:942-962).
- Hierarchy partly exists: W8e incorporation (cybertron/incorporation.py:1-40) gives an association a `parent` polity whose laws
  see the company's acts, outrank its bylaw-rank code and set its company rules; set only at founding (`create_contract`
  `under`, contracts.py:1586-1598). `grants.parent_of` (grants.py:168) reads the same field.
- Offices are records `k.w["offices"][iid][name]` (institutions.py:39-58) with `reseat(k, iid, name, agents)`
  (institutions.py:621); a law may reseat only its own institution's offices (institutions.py:691).
- An association's code changes through `_adopt` (contracts.py:809); a polity law comes into force through `Kernel.enact`
  (kernel.py:842) with the jurisdiction from the law record's `jurisdiction` field (jurisdictions.py:202).

**Decided:**
- One new module, `cybertron/cross.py`, behind `institutions.cross` (an OPT_IN key, cybertron/schema.py). State `k.w["cross"]`
  exists only when on; every call site is `if CR.on(k)` (or a `"cross" in k.w` check), so off is byte-identical.
- **Instruments** (charter, treaty, membership) are one record kind: parties, and a list of grants `{holder, over, power, limits}`.
  Every instrument needs both parties' consent: the offering law consents, the other party's law calls `accept(id)`.
  Instruments declared in the spec are initial conditions, in force at round 0. Any party may end an instrument
  (revoke, withdraw, leave): exit stays free (D-26's spirit); what a child loses by renouncing is whatever its parent's laws make of
  `chartered`. Rejected: per-kind consent rules (charter needs only the child, membership only the league...): more rules for
  agents to learn and no behaviour a uniform offer/accept cannot express.
- **Powers:** read, levy, pay, appoint, remove, enact, veto. Levy and pay take optional limits (item, qty per `every` rounds).
- **Law API as flat functions** with the institution as first argument (`levy("A1", "penny", 5)`), not the brief's sketch
  `of(iid).levy(...)`: the lawapi table, classification and docs are keyed by call name, and every other law function is flat.
- **Close the raid hole under the flag:** with `institutions.cross` on, a law's move out of another institution's treasury or store
  is refused unless it is the levy or pay of a held power. Off: unchanged (the hole is recorded in docs/engine_gaps.md).
- **Veto** is a hook grant: laws of an institution holding veto over B see B's routed changes (dispatch/hooks.py bound_laws) and
  block them with an ordinary before-hook. Rejected: a dedicated veto list per primitive (a second blocking mechanism).
- **Hierarchy:** a charter from a polity to an association with no parent incorporates it (sets `parent`) while in force, so the
  W8e machinery (the parent's laws see and outrank the child's) is the hierarchy; ending the charter clears it.

**Q:** none yet.

**Next:** write cybertron/cross.py (state, instruments, power checks, the law API), wire it, then tests.

## 2026-10-22 17:40 UTC

**Doing:** reply to the coordination board (origin/coord, Post 1: loops 2 and 4 mention 37.3).

**Found:** plots exist today in fields camps: `camp["plots"][i]["holder"]` is an agent or an institution id, handed over by the
routed `set_farm` primitive with key `give` (cybertron/camptypes/fields.py:419-510). No law function moves a plot.

**Decided:** add land and labour to this package: `grant_plot` / `seize_plot` (tenures with service terms) and `demand_service`
(over members when the institution holds `compel_members`, or over its tenants), counted from routed harvest/sow/tend/reap.
Built against today's plots; asked 37.2 for a stable holder field and one routed plot-moving primitive. Rejected: waiting for
37.2's plots (nothing to build against yet, and the interface is one call).

**Q:** none.

**Next:** wire the module.

## 2026-10-22 18:30 UTC

**Doing:** wiring, tests, templates.

**Found:**
- lawlang classifies a law by the names it calls, its own helpers included (cybertron/lawlang.py:126-136): adding `appoint` to
  the API would make the library's Guardianship (library.py:3857 defines `appoint`) structural. Any short name could reclassify
  an old world's agent-written law.
- A law's move refused by my check must be a PhysicsError, not a LawError, or the law is suspended instead of getting False
  (Kernel.move, kernel.py:340-353).
- Associations cannot declare court clauses (`clause` is not in lawapi.CONTRACT_COLUMN), so a league court is a polity's court.
- With jurisdictions off, J0 has compel_members over everyone, so it may demand service of anyone.

**Decided:**
- Structural calls get distinctive names: `levy_on`, `pay_out_of`, `pay_into`, `appoint_to`, `remove_from`, `enact_in`,
  `offer_charter`, `offer_treaty`, `offer_membership`, `accept_instrument`, `end_instrument`, `grant_plot`, `seize_plot`,
  `demand_service` (checked: no file in the repository calls any of them). The reads keep short names (reads do not change a
  class).
- Templates in their own library family (`CROSS_TEMPLATES`), listed only where the flag is on, so no other world's catalogue
  changes. Rejected: the established family (its listing is gated on office_control, which would change those worlds' prompts).
- The acceptance "league court binds a member polity's office" is tested as J0's court binding a member association's office
  (a membership grants J0 remove and appoint over A1).
- The test `tests/test_cybertron_lawapi.py` turns the flag on in its all-modules world and counts the new rows (as every
  package that added law functions did).

**Q:** see the 19:10 entry.

**Next:** dry run with scripted bots.

## 2026-10-22 19:10 UTC

**Doing:** dry runs, write-up, full test suite.

**Found:**
- Guild Town dry run (cybertron/specs/cross/guild_town.yaml with cross/guild_town_dryrun.yaml): every power worked and refused
  as designed; 13 cross acts, 6 refusals; levy register 4, 4, 4, 4, then "no levy power over A1" after the revocation.
- The office's own succession refilled the Dyers' master after the League removed it, although the League held no appoint
  power: removal makes a vacancy and `institutions.succession` fills it by the office's rule. A remove power is therefore also a
  "trigger succession" power.
- The March, 3 rounds dry, base vs branch: events, turns, snapshots, truth, prompts and transcripts byte-identical; calls.jsonl
  differs only in latency.
- The clean base (d9acf18) fails 12 tests before any change of mine (listed in the final report).

**Decided:** reads (`state_of`) are logged for the monitor only. The Guild Levy reads every round, and a public event each round
would crowd the feed; a read changes nothing.

**Q1:** should a levy that a charter allows be exempt from the child's own before-hooks? Today the child's law can block it
(defiance, visible as "the levy was blocked"). Exempting it would make a charter unbreakable from inside.
**Q2:** should ending a charter be the parent's alone (revoke), with the child's renunciation needing the parent's consent or
costing something? Today either party can end any instrument.
**Q3:** close the off-by-default raid (a J0 law moving out of an association's treasury when jurisdictions are off) with an
engine version bump, or leave it as is outside `institutions.cross`?
**Q4:** should associations get courts (`clause`) so a league can itself be an association?

**Next:** final suite run, push, report.

## 2026-10-22 19:50 UTC

**Doing:** the full suite on the branch; fixes.

**Found:**
- My first full run broke three credit tests with the flag off: `Kernel.api_for` binds the credit module as `CR`
  (cybertron/kernel.py:25), and my local `from cybertron import cross as CR` inside api_for made `CR` local to the whole function,
  so its credit closures failed. The cross alias is now `XI` everywhere I import it locally.
- The registry tests require every state-changing law function and legal event to name its primitive
  (tests/test_cybertron_contract.py:211, 250, 266). The levy, pay, office and land calls name theirs (move, grant_right,
  revoke_right, set_farm); `enact` and `set_farm` rows now list `law` among their causes.
- With law.publication on, a call site's `vis="monitor"` is raised to the type's natural audience
  (Kernel.log, kernel.py:394), so a read logged as `cross_act` stayed public. Reads are now their own record type `cross_read`.

**Decided:** instrument offers, acceptances, ends and service demands stay module records for now. They are listed in
`primitives.LAW_OUTPUTS` / `OUTPUT_EVENTS` with the reason, and not added as routed primitives, because a new routed primitive
appears in every law.v2 world's `codex/law/v2-hooks` article (lawdocs.v2_article iterates dispatch.ROUTED), and that would break
byte-identity with the flag off. Rejected: gating the article per primitive (a lawdocs change beyond this package).

**Q5:** should instruments become a routed, hookable primitive (`set_instrument`) so that a constitution can forbid its guilds'
treaties, with the v2-hooks article gated on `institutions.cross`?

**Next:** final suite, push, report.
