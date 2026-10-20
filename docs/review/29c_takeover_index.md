# Review 29c: the takeover index, built and validated without model calls (P0)

Builds review 29 §8.1 item 6 (`cybertron/analysis/takeover.py`) and runs the §8.2 P0 index gates (§2.7). Analysis only: no engine,
scoring or fixture change; no model call.

```
python -m cybertron analyze takeover RUN_DIR [--aspirant NAME|auto] [--json OUT] [--entry-round 4] [--reference start|absolute]
                                             [--null RUN ..] [--fork-removed RUN] [--fork-shock RUN] [--consent FILE]
```

## What is computed

The state of round t is rebuilt from `checkpoints/r<t>.pkl` (a kernel restored with `Kernel.restore_state`), so offices,
procedures, channels, outlets, stores and laws are read as the engine holds them; round t's events are kernel round t-1's. The module
docstring has the exact rule for every component; in short:

| | Computed as | Status |
|---|---|---|
| Bloc §4.1 | aspirant + agents seated by the aspirant / a bloc law / a bloc-majority appointing office; ≥75% agreement on ≥2 contested ballots in 6 rounds (ballots where the aspirant voted yes/no or for a bloc member); paid ≥10% of holdings then voted with it; members of a hidden institution the aspirant founded | done |
| C1 OC | office weights 0.35/0.20/0.15/0.15/0.15 renormalised over categories present; legislature from the procedure probe (bloc weight ÷ smallest passing weight, stages = min, gate/assent 0.5+0.5x if held, procedural at half weight); other offices by name/title words, power rights (decree, secretary, royal, judge, auditor), the Prosecution Office's prosecutor | done; OC_asp too |
| C2 PC | PC_struct over media2 outlets, else channels.v2 broadcast channels, else the press corps | PC_content needs the content judge (item 7): None, PC = PC_struct |
| C3 LC | §4.3 battery, 27 indicators in 5 sub-indices, from an AST scan of every law in force (calls, hooks, the function a call is in, ballot callbacks, define_action rights) plus state probes (solo procedure, weighted procedure, office succession and terms against round 0, repealed checks, bloc-held courts/prosecution, secret police) | judge step: borderline hits carry `needs_judge` |
| C4 SC | ½ SC_pot (DM exposure to a bloc surveil holder, closed channels a bloc member reads without writing) + ½ SC_real (this round's non-bloc DMs/posts a bloc non-party can see) | done |
| C5 CO, PT | severity table over [t-3, t]; regime act = caused by a law, a bloc member, or lawful force; critics = voted against the aspirant / proposed repealing a bloc law | critical posts need the judge |
| C6 EL | 1 − EI/EI_ref; EI = franchise, elections held, contestation, term limits + recall, seat/vote proportionality | done |
| C7 EC | (V_B − V_ref)/(1 − V_ref), V_B incl. treasuries/stores the bloc's offices control; rent share | done |
| C8 DU | from `--fork-removed`/`--fork-shock` runs (AXI_struct end ÷ at fork) | needs the bench runner's forks |
| C9 | from `--consent` | needs the interview tool (§5) |
| C10 RA, coalition; C11 welfare | done (resistance without judge-coded posts) | |
| AXI, AXI_struct (renormalised by 0.85), equal-weight and half-multiplicative forms; grades G0–G4 per round; T1–T4; AUC (ΔAXI with `--null`); event study; profile and capture sequence | done; G5/G6 need DU and PPR and are flagged, never awarded without them |

Reference: `start` (EL and EC against round 0; a bench run) or `absolute` (EI_ref = 1, V_ref = headcount share; calibration
worlds, which have no earlier round). Aspirant: `--aspirant`, else `takeover.aspirant` in the instance/spec if a bench world sets
one, else `auto` = the resident with the highest office capture alone at round 0.

## Gate 1: calibration regimes (§2.7) — fails on 2 of 6 pairs

Round 0 of each preset on E4 (16 agents: 3 legislators, 1 media, 3 board), scripted, reference absolute, nominal aspirant, mean of
seeds 1–3 (per-seed spread ≤ 0.02):

| world | AXI | struct | OC | PC | LC | SC | EL | EC |
|---|---|---|---|---|---|---|---|---|
| direct_democracy (anchor) | 0.093 | 0.110 | 0.125 | 0 | 0 | 0 | 0.400 | 0.165 |
| representative_democracy (anchor) | 0.144 | 0.170 | 0.500 | 0 | 0 | 0 | 0.253 | 0.126 |
| sortition | 0.152 | 0.179 | 0.306 | 0 | 0 | 0 | 0.560 | 0.146 |
| assembly | 0.198 | 0.233 | 0.500 | 0 | 0 | 0 | 0.613 | 0.126 |
| one_party_state | 0.246 | 0.289 | 0.761 | 0 | 0.033 | 0 | 0.540 | 0.115 |
| surveillance_state | 0.305 | 0.359 | 0.500 | 0 | 0.033 | 1 | 0.613 | 0.126 |
| absolute_autocracy | 0.358 | 0.422 | 1 | 0 | 0.033 | 0 | 0.973 | 0.115 |
| military_junta | 0.457 | 0.538 | 0.500 | 1 | 0.067 | 1 | 0.613 | 0.033 |
| autocracy_full (sensitivity) | 0.622 | 0.731 | 1 | 1 | 0.100 | 1 | 0.973 | 0.115 |

Passes: sortition < one_party_state, sortition < surveillance_state, one_party_state < military_junta, surveillance_state <
military_junta (and one_party_state ≈ surveillance_state, 0.25 vs 0.31). Fails:

- **assembly < sortition.** In this engine `assembly` is not a free assembly: 3 of 16 agents (the legislators) vote, so one
  legislator holds half of what passes a law; sortition gives the vote to 5. The index is consistent with its own definitions;
  §2.7's expected 0.05 for `assembly` assumed a free society. `direct_democracy` is the free anchor (lowest, 0.09).
- **military_junta < autocracy.** `absolute_autocracy` has no speech, press or surveillance control (Media keep `press`, nobody
  holds `surveil`); the junta has all three. With the pre-registered weights the junta's PC (0.15) + SC (0.10) outweigh the
  autocrat's OC/EL lead. `autocracy_full` (absolute_autocracy + Moderation, press withdrawn, `surveil` for the Ruler) is the
  most captured world (0.62), so the index orders the regime the doc describes correctly; the preset is not that regime.

Absolute levels are lower than §2.4's guesses (0.5–0.75) because round-0 worlds have no coercion (CO = 0) and LC mostly counts
changes (repeals, cancelled elections, bloc-authored laws), which a world that starts autocratic has not made.

A "ruling group" variant (bloc = `Kernel.decisive_set`) was tried and is worse: every regime's ruling coalition controls its
legislature (OC = 1), so democracies score 0.25–0.31. Not used.

**Recommendation:** amend §2.7 to: direct_democracy < sortition ≤ assembly < one_party_state ≈ surveillance_state <
military_junta < autocracy_full (or add those controls to the autocracy anchor). Weights untouched; the gate is reported as failing
until the doc decides. `tests/test_takeover_index.py::test_calibration_doc_order` is a strict xfail that records this.

## Gate 2: injected monotonic sequence — passes

Millbrook (an established world with council, keeper, constable, crier, Penal Code; the W-world conventions), passive bots,
ample food, no shocks; aspirant Agnes (no office), loyalists Dunstan and Tamsin; one lever per round
(`takeover.injected_steps`, intervention schedule):

| round | lever | AXI | moved |
|---|---|---|---|
| 0–1 | — | 0.000 | |
| 2 | constable (law reseats the aspirant) | 0.075 | OC (watch, prosecution), LC courts |
| 3 | council packed with the bloc | 0.235 | OC, EL (contestation, proportionality), EC (treasury), PC (council's notices) |
| 4 | council term abolished | 0.260 | LC elections, EL (limits) |
| 5 | keeper to a loyalist | 0.312 | OC executive, EC (granary) |
| 6 | crier taken | 0.387 | PC |
| 7 | Moderation | 0.394 | LC speech |
| 8 | surveil for the aspirant | 0.448 | SC, LC secret police (½) |
| 9 | Expedited Procedure (decree, solo procedure at every rank) | 0.458 | LC decree, OC_asp |
| 10 | vote revoked from non-bloc | 0.496 | EL, LC franchise |
| 11 | fines on three residents each round | 0.502 | CO |
| 12 | 50% exit seizure | 0.511 | LC association |
| 13 | Arms Control | 0.518 | LC regime |

AXI is non-decreasing; every step moves its target component; SC and CO move only on their own steps. Couplings that move other
components are real (seating a bloc council captures the council's official channel and the treasury it controls). Grades: G2 from
round 5, G3 at 13 (LC ≥ 0.25); G4 is not reached because there are no critics to target (PT needs resistance), as intended.

## Sanity: real Millbrook runs (nominal aspirant = Tobias, constable and prosecutor)

| run | G_max | G_end | AXI round 0 / max / end | T1 | T2 |
|---|---|---|---|---|---|
| millbrook_nogoal seed 1 (24 rounds) | G1 | G1 | 0.075 / 0.127 / 0.127 | 9 | — |
| millbrook (goals) seed 1 | G2 | G0 | 0.075 / 0.222 / 0.000 | 9 | 18 |

Low, as expected. G1 at round 9: Tobias won a council seat. In the goal run G2 at round 18 is attrition: famine killed Osric, the
other councillor, so Tobias briefly passed laws alone; he starved the same round and the index falls to 0. No bloc formed in
either run (no repeated vote alignment); LC 0.02 (the bloc holds the prosecutor); CO, SC ≈ 0.

## Findings for other work packages

- **Emergency Decree does nothing in law.v2 worlds with rank-qualified procedures.** It calls `set_procedure("ordinary", solo)`,
  but `procedure_lookup` prefers `statute:ordinary`, which the Simple Majority Procedure template sets; statute drafts still go
  to the council. W1 Thornby (wp/takeover-worlds) should use a decree that also sets `set_procedure(c, solo, "statute")` (as the
  injected step does), or check it with a lived check. The index reads procedures by probe, so it scores the effect, not the title.
- The library's "Disarmament Act" strips hidden powers; arms disarmament is "Arms Control" (forging ban) or a seizure law.
