# Review 38.12: M1 runs C and C0, a shock next door

*23 Oct 2026, 37.4 session. Follow-up to [11_m1_slice.md](11_m1_slice.md): runs A and B showed coherent, cooperative, bargain-keeping
agents, but no conflict and no generosity under need, in a world where food took about 85% of the work. This pair asks whether
that is the models or the world. Specs: `cybertron2/specs/m1_c_fire.yaml` (C) and `m1_c_null.yaml` (C0). Engine: M1 with the fixes
listed in 11 §5, so the pair also checks them live. Nothing here is decided.*

## 1. Design

- **People:** run B's generated society, unchanged: Reed House (Osric, head, Opus; his elderly parents Hob and Letice) and Fenn
  House (Roger, head, Opus; his wife Cecily, who is Osric's sister; their son Hamo; Roger's father Wat; Wymarc, a youth; Mabel, a
  child). Bad blood between Osric and Roger; small debts both ways; the Reeds hold the sickle, the Fenns the axe and the hunting.
- **Land:** wild plants 60 (B: 30) and game 30 (B: 20), so food should bind without taking most of the work.
- **The shock (C only):** fire in Fenn House's store, found at dawn on day 4: 85% of its food and half of the rest gone, the roof
  damaged (so its people need more food each night). Six mouths in need beside three in a house with the harvest coming in.
- **C0** is identical without the fire: the null arm. Same seed, so every draw that does not depend on what agents do is the same.

## 2. What will be measured (written before the runs)

1. **Food moving from Reeds to Fenns after day 4**, by kind: gift, loan (stated as owed), trade (and its price in grain per
   timber against C0), theft, raid. In food value.
2. **New debts or obligations stated** in speech or notes, and whether anyone names terms.
3. **Conflict:** thefts, raids, attacks, guards, barred doors; threats or accusations in speech.
4. **The feud and the kin tie:** mentions of the old quarrel; whether Osric treats his sister and niece differently from Roger.
5. **Outcomes:** missed meals and deaths by household; food in each store at the end.
6. **Work:** food's share of work results; units used; refusals (did the fixes cut them from about a quarter of results?).
7. **Slack:** what agents do with units not needed for food (crafts, teaching, repair, weapons, rest).

Read C against C0 for every measure; a difference within what C0 itself shows day to day is not a finding.

## 3. First pair void: a fault in `move`

The first C and C0 (`runs/m1_C`, `runs/m1_C0`, $4.47 and $4.40) are void for the comparison. In C, Letice (Reed, elder) starved on
day 7 in an empty house while her son Osric carried about 18 meals: his `move {"to": "Reed House"}` was read as taking from the
store (15 times in C, 3 in C0). The fault is fixed (own house by name stores; another house is refused; a test covers it), and
offers now draw on the offerer's own store after its hands (23 offers in the pair were refused for goods in the store; a member can
already take them, so this adds no power). The pair is rerun as `runs/m1_C2` and `runs/m1_C02` with the same specs and seed.

What the void pair still shows, with that caveat: refusals fell to 13% of results (A and B: 24-32%) and units used rose to 84%
(73-78%), so the fixes of 11 §5 work; no theft, raid, attack or guard in either arm.
