# Each person told their age and what lies ahead

**Status:** retrospective, accepted: D4-69 (2 Nov)
**Owner:** 37.4

## Summary

Each person is shown, under "You", their age in days and what lies ahead: a youth, when they come of age; an adult, when they
turn elder and can have no more children; and their partner's age and when they turn elder. A world setting (`ages: true`).

## The proposal

As summarised. Built in life.py (`age_line`), shown by view.py and prompt.py through `Here.age_line`.

## Why

c3_combe_rich (review 38.41): Ivo and Margery were 52 days old at the start, with lifespan 96, so their childbearing ended on day
44. Nothing told them their age. They had a full store from day 16 and did not try for a second child from day 21 to day 43; they
decided to try again on day 41, and their try on day 44 was refused ("you must both be grown adults"). In life everyone knows their
age. Zach asked whether births are too hard; this was one of five changes he then asked to be built ("build all five").

## Alternatives considered

- **Nothing told** (as before): the end of childbearing found by a refusal.
- **Age in years**: the world counts in days (a year is 32 at Combe); days keep one unit for everything.

## Open questions

1. Whether to show the ages of everyone in one's household, not only one's partner.

## Affects

life.py, here.py, view.py, prompt.py; spec information/prompts.md.

## History

- 2 Nov 2026: built at Zach's request with the evening, departures and tags; written down after (retrospective).

## Sources

runs/c3_combe_rich; review 38.41; proposals/fertility.md (37.2).
