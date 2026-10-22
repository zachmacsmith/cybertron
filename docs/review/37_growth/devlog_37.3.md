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
