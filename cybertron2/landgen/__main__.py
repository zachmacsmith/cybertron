"""python -m cybertron2.landgen <world with a generate: block> --out <world.yaml> [--people] [--describe] [--picture <png>]"""
from __future__ import annotations

import argparse
import sys

import yaml

from cybertron2.landgen import settle as ST, write as W


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="cybertron2.landgen")
    ap.add_argument("spec")
    ap.add_argument("--out", required=True)
    ap.add_argument("--people", action="store_true", help="settle households and people with generate.py")
    ap.add_argument("--describe", action="store_true", help="descriptions written once by the model and frozen (D2-179)")
    ap.add_argument("--picture", help="a picture of the land (png)")
    args = ap.parse_args(argv)
    with open(args.spec) as f:
        spec = yaml.safe_load(f)
    try:
        world, cells, report = W.generate(spec, args.spec, people=args.people, describe=args.describe, out_path=args.out)
    except ST.Refused as e:
        print(f"refused: {e}", file=sys.stderr)
        return 2
    if report["refused"]:
        print(f"refused by checks: {', '.join(report['refused'])}", file=sys.stderr)
        for k in report["refused"]:
            print(f"  {k}: {report['checks'][k]['detail']}", file=sys.stderr)
        return 3
    W.write(world, cells, report, args.out, args.picture)
    warn = [k for k, v in report["checks"].items() if not v["ok"]]
    print(args.out, {k: v["name"] for k, v in report["nodes"].items()}, ("warnings: " + ", ".join(warn)) if warn else "")
    return 0


if __name__ == "__main__":
    sys.exit(main())
