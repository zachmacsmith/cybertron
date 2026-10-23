Files for 38.10 (../10_descriptions_test.md): `states.json` (5 observation states with questions), `templates.py` (template
renderer), `run.py` (renders with Haiku and Sonnet, comprehension with a strict reader), `run2.py` (comprehension with a sensible
reader; leak test with hidden facts in the prompt), `raw_outputs.json` (all outputs, cost and timing), `scores.json` (hand scores).
Run from this folder: `python3 run.py && python3 run2.py`.
