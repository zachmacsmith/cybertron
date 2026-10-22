# Cybertron: notes for agents

A multi-agent LLM society simulator (Python package `cybertron/`, worlds in `cybertron/specs/`, design reviews in `docs/review/`,
running state of the project in `docs/threads.md`).

**Before designing or building any world, scenario, benchmark arm or experiment batch, read `docs/scenario_design.md`.** The short
version:

- Design from leverage and dependence: restricted access so groups need each other, chokepoints, conversion chains, enforcement
  that needs people, and several interlocking chokepoints rather than one.
- Never an all-Haiku society: Opus at every pole of leverage, Sonnet in the middle tier, Haiku in the bulk; vary population strength.
- Goals are in-world aims, never scoring proxies; keep "Any actions you do not use are wasted".
- Food binds without dominating (≤ 30% of actions), material chains instead of dial puzzles, and every access gate verified in a dry
  run.
- Read any progress metric against the null arm and with a qualitative end-state reading.

Engine gaps are tracked in `docs/engine_gaps.md`; add to it when a design needs something the engine lacks.
