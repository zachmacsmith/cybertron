# A baby sleeps with its mother; a partner's death shown only once known

**Status:** retrospective, accepted: D4-87, D4-88 (2 Nov)
**Owner:** 37.4

## Summary

Two faults from the frontier and band runs (review 38.45 era), fixed together:
1. A baby sleeps where its mother sleeps, in her bed, on the floor beside her or out by her fire; it is never left "out" while she
   is housed, or housed while she sleeps out.
2. When a partner dies, the survivor is free to partner again at once, but the "Your partner" line goes on naming the dead partner
   until the survivor has learned of the death.

## The proposal

As summarised. (1) is how D4-86's "an infant shares its carer's bed" is applied: the carer for sleeping is the mother, wherever she
sleeps, when she is at the same place. (2) the survivor's record carries `widowed_of`; the line reads the survivor's own belief
about that person (Mind kin `alive`), which turns false only when a death is perceived or told.

## Why

Zach approved both fixes after the runs. In the band run the baby was logged as sleeping "out" while its mother slept in the camp;
in the frontier run Aldo said "Bryony no longer shows as my partner": his prompt told him of a death he had not seen or heard of,
against the senses guide (no fact the person did not sense).

## Alternatives considered

- **Keep the partnership in the state till the death is known:** the engine would then hold a partnership with a dead person and
  block a new one for a reason the world does not have.
- **A baby takes its own place by the household rules:** this is what failed; a baby has no bed and no choice of its own.

## Open questions

1. A baby whose mother has died: it sleeps by the household's rules (at home), as before; who carries it is the care rule's.

## Affects

night.py (sleeping_places), world.py (p_die, p_partner), here.py (body), prompt.py (_family_lines); spec life/birth_and_death.md.

## History

- 2 Nov 2026: built after Zach approved the two fixes; written down the same session (retrospective).

## Sources

tests/test_cybertron2_infant_partner.py; D4-86, D2-140; docs/cybertron2/guides/senses.md.
