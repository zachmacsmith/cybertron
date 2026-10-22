"""cybertron2: the engine on a graph of places (docs/review/38_space_engine/00_plan.md). Phase 0: households in a forest.

Modules:
    world    the state (nodes, edges, agents, houses), the spec, the seeded random streams, the end of the round (forest, hunt,
             hearth, ration, hunger, the cold, spoilage, breaks)
    act      the actions agents take, each checked against where the agent is
    prompt   what an agent is told (system prompt, turn prompt, the reply schema)
    run      the round loop, model calls (through the old engine's leaf backend cybertron.llm), the scripted smoke-test bot, logs
    report   a run's summary from its logs

Physics ported from the old engine (cybertron/): the forest's logistic plants and the forage yield (camptypes/forest.py), the
individual hunt (camptypes/forest.py, engine 14), hunger stages, frailty and the starvation hazard (subsistence.py). New: places
and presence, houses, the hearth and the cold (docs/review/37_growth/02e_shelter.md).
"""
