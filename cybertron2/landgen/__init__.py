"""The landscape generator, stage 1 (docs/cybertron2/proposals/generator_stage1.md; D2-173 to D2-188).

A world file with gaps goes in; a complete world file in today's format comes out, with the ground truth it was compressed from
(the cells of the land) saved beside it, and a report of what was pinned, generated and checked. Layers, in order:

    macro.py      primitives and named configurations: the land's large shapes, with anchors for pins (D2-178, D2-188)
    physical.py   elevation, climate, water, soil, terrain, natural cover, resources (generator.md §2b, §10; stage 1 §3, §11a)
    settle.py     sites, land in rings sized by the capacity target, nodes and parcels (stage 1 §4, §5; D2-175, D2-181)
    roads.py      roads of about a day, stopping places, landmarks, hidden ways, wild nodes (stage 1 §5, §11f; D2-182)
    names.py      names from parts chosen by the land (D2-186)
    write.py      the world file, people (generate.py, unchanged), descriptions, checks and the report (stage 1 §6 to §8)

Every draw is keyed by (seed, layer, element) through keyed.py, so a pin changes only what depends on it (D2-173). Every number is
data in vocab.py (calibrate). The grid of cells is a jittered square grid (scipy is not in the environment; stage 1 §2's Poisson
disc and Delaunay neighbours are replaced by it), and the cells are saved as .npz (pyarrow is an optional extra).

    python -m cybertron2.landgen <world with a generate: block> --out <world.yaml> [--people] [--describe]
"""
