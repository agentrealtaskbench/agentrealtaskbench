#!/usr/bin/env python3
"""Print round progress: runs done per agent, and what is still open.

Usage: python3 scripts/round_status.py round01 [--agent kimi]
"""
import argparse
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("round")
    ap.add_argument("--agent")
    args = ap.parse_args()
    agents = [a for a in yaml.safe_load((ROOT / "data" / "agents.yaml").read_text(encoding="utf-8"))
              if a.get("round") == args.round and (not args.agent or a["id"] == args.agent)]
    tasks = sorted(yaml.safe_load(p.read_text(encoding="utf-8"))["id"] for p in (ROOT / "tasks").glob("*/*.yaml"))
    runs_dir = ROOT / "results" / args.round / "runs"
    total_done = 0
    for a in agents:
        done = {}
        for p in (runs_dir / a["id"]).glob("*.yaml") if (runs_dir / a["id"]).exists() else []:
            r = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            done[r.get("task")] = r.get("outcome")
        todo = [t for t in tasks if t not in done or done[t] == "TODO"]
        finished = len(tasks) - len(todo)
        total_done += finished
        bar = "#" * round(20 * finished / len(tasks))
        print(f"{a['id']:<16} {finished:>2}/{len(tasks)} [{bar:<20}]")
        if args.agent:
            for t in todo:
                print(f"  open: {t}")
    print(f"\n{total_done}/{len(agents) * len(tasks)} runs finished in {args.round}")


if __name__ == "__main__":
    main()
