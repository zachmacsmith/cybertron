# The engine's architecture

## Summary

cybertron2 is rebuilt on a general core: everything has a place, every change passes one chokepoint, and the code that serves an
agent sees only where the agent is and what it knows. Narrow code that fits one scenario is replaced, not kept beside the general
form.

## Decided

- H-1: cybertron2 is a new engine in its own package, `cybertron2/`; the old engine is frozen for the bench batches and
  published runs.
- H-2: the physical systems are ported onto nodes; the institutional layer is copied keeping its interface and fixes; only leaf
  modules are imported unchanged.
- D4-1: start from what 37.2 built and extend it; what does not match the plans is redesigned, not patched.
- D4-34: the engine is rebuilt on the designed general core: state by place, containers as records, buildings from fittings, one
  chokepoint of primitives with hooks and causes, placed events, agent-facing code that sees only `Here` and `Mind`, and households,
  claims, hosting, offers and agreements as records.
- D4-35: everything happens in a place; nothing at one node can be seen at another except as people, messages or goods carry it,
  and the engine is built so that this cannot fail by accident.
- D4-24: the world grows by data (techniques, fittings, settings, powers, clauses) on a small set of verbs.

## Mechanics

- **Place.** Every entity has a place: a parcel, building, herd, offer or container at a node; a person at a node or on a road
  (hands are where their person is). Every event is recorded at a node or a road (D4-35).
- **The chokepoint.** Every change of state is a primitive applied through one function: it checks that everything the primitive
  touches is at the place where it acts, runs the hooks registered before the primitive (which may refuse it), makes the change,
  and runs the hooks registered after it. Each application records its cause: the act, the actor, and for whom it was done (D4-34).
- **Containers.** Goods are always in a container with a place: a person's hands, a building's stock, what the dead left (D4-34).
- **The agent's view.** The code that builds an agent's prompt, carries out its acts and records what it perceives reads only a view
  of the node the agent is at (`Here`) and the agent's own mind (`Mind`). It cannot read another node (D4-35).
- **Data.** Goods, techniques, fittings, blueprints, covers and what is seen of each are tables; adding one is adding a row (D4-24).

## Data

The tables of the state and the primitives are listed in the engine reference, review 38.17.

## Open

- Laws attached to the chokepoint's hooks: proposals/law.md (M3).

## Sources

38.07 §2-§5, 38.08 M1, 38.16, 38.17; proposals/place.md.

*Current as of 23 Oct 2026: H-1, H-2, D4-1, D4-24, D4-34, D4-35.*
