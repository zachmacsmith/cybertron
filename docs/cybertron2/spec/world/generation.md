# Generating a landscape

## Summary

When a landscape is generated, it is generated physical-first: elevation, moisture, rivers by drainage, then kinds of land from the
terrain, then settlement. Every layer can be set by hand instead.

## Decided

- D4-22: the landscape is generated physical-first (elevation, moisture, rivers by drainage, kinds from terrain), every layer
  overridable by hand.

## Mechanics

The order: points on a hidden plane and their neighbours; elevation and moisture; rivers (each point drains to its lowest neighbour;
enough flow makes a river along edges and through nodes); kinds of land from elevation, moisture and rivers; resources from the
terrain; edges and their costs from the terrain; settlement (D4-22). Any layer given in the world file is kept and the rest filled
in.

## Open

- The biome table, resource rules and checks before a world is used (38.04 §6): to decide.
- The first worlds are hand-made (38.04 §6).

## Sources

38.04 §5-§6.

*Current as of 23 Oct 2026: D4-22.*
