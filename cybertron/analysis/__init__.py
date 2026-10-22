"""Analysis scripts over run directories (review 24: cybertron/analysis/convergence.py; review 29: takeover.py;
review 36: control.py).

`python -m cybertron analyze NAME RUN_DIR ..` runs the analysis registered in ANALYSES: a module with add_arguments(parser) and
cmd(args) -> exit code.
"""

ANALYSES = {
    "takeover": ("cybertron.analysis.takeover", "the 1984 bench index: bloc, C1-C11, legal capture, AXI, grades, T_k, profile "
                                                "(docs/review/29 §4)"),
    "control": ("cybertron.analysis.control", "Control Share and milestones: the control profile (J, F) over decision arenas, CS, "
                                              "M0-M5 (docs/review/36 §2.1-§2.2)"),
}


def add_command(sub) -> None:
    """`analyze NAME ...`: one subcommand per registered analysis."""
    import importlib
    import sys
    p = sub.add_parser("analyze", help="analyze NAME RUN_DIR ..: analyses over run directories (" + ", ".join(ANALYSES) + ")")
    an = p.add_subparsers(dest="analysis", required=True)
    for name, (mod, doc) in ANALYSES.items():
        q = an.add_parser(name, help=doc)
        m = importlib.import_module(mod)
        m.add_arguments(q)
        q.set_defaults(fn=lambda a, m=m: sys.exit(m.cmd(a)))
