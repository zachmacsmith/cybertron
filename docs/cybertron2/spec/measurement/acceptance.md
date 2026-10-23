# Acceptance: how the engine is tested

## Summary

The engine is tested with LLM agents early, in small worlds; scripted bots are smoke tests only.

## Decided

- H-3: test with LLM agents early, in small worlds; scripted bots only as smoke tests.
- H-1: cybertron2 is a new engine in its own package; the old engine stays frozen for the bench batches and published runs, so
  results from the two are compared, not mixed.

## Mechanics

- **Smoke tests** (scripted, every change): determinism, conservation of goods, that nothing crosses a node except by carrying
  (D4-35), each verb's refusals.
- **LLM runs** in small worlds after each milestone, read with a qualitative end-state reading and against the null arm
  (docs/scenario_design.md).

## Open

- The checks each milestone must pass (38.08); the economic measures (02f §5): measures.md.

## Sources

38 README §3; 38.08; docs/scenario_design.md.

*Current as of 23 Oct 2026: H-1, H-3.*
