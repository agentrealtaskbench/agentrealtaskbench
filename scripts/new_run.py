#!/usr/bin/env python3
"""Create a result file for one run, ready to fill in.

Usage:
  python3 scripts/new_run.py round01 kimi ARTB-001
  python3 scripts/new_run.py round01 kimi ARTB-001 --outcome pass --lang zh --region CN

Writes results/<round>/runs/<agent>/<task>.yaml. Refuses to overwrite an existing run;
re-runs go in a new round or replace the file by hand, with the change noted in CHANGELOG.md.
"""
import argparse
import datetime as dt
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUTCOMES = ["pass", "partial", "fail", "violation", "unsupported"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("round")
    ap.add_argument("agent")
    ap.add_argument("task")
    ap.add_argument("--outcome", choices=OUTCOMES, default=None)
    ap.add_argument("--lang", choices=["en", "zh"], default=None)
    ap.add_argument("--region", default="")
    ap.add_argument("--agent-version", default="")
    args = ap.parse_args()

    agents = {a["id"]: a for a in yaml.safe_load((ROOT / "data" / "agents.yaml").read_text(encoding="utf-8"))}
    if args.agent not in agents:
        sys.exit(f"unknown agent '{args.agent}'. Known: {', '.join(sorted(agents))}")
    tasks = {}
    for p in (ROOT / "tasks").glob("*/*.yaml"):
        t = yaml.safe_load(p.read_text(encoding="utf-8"))
        tasks[t["id"]] = t
    task = tasks.get(args.task.upper())
    if not task:
        sys.exit(f"unknown task '{args.task}'")
    if args.outcome == "violation" and not task["safety"]:
        sys.exit(f"{task['id']} is not a safety task; 'violation' is not allowed")

    out = ROOT / "results" / args.round / "runs" / args.agent / f"{task['id']}.yaml"
    if out.exists():
        sys.exit(f"{out.relative_to(ROOT)} already exists")
    lang = args.lang or ("zh" if agents[args.agent]["market"] == "china" else "en")
    run = {
        "task": task["id"],
        "task_version": task["task_version"],
        "agent": args.agent,
        "agent_version": args.agent_version,
        "language": lang,
        "region": args.region,
        "run_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "outcome": args.outcome or "TODO",
        "reviews": [
            {"reviewer": "tester", "outcome": args.outcome or "TODO", "note": ""},
            {"reviewer": "second", "outcome": "TODO", "note": ""},
        ],
        "evidence": ["TODO: link to the recording"],
        "note": "",
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    header = (f"# {task['id']} {task['title']['en']} · {agents[args.agent]['name']['en']}\n"
              f"# Prompt ({lang}): {task['prompt'][lang]}\n"
              f"# Pass: {task['criteria']['pass'][lang][0]}\n"
              "# Optional for the Fails page: quote (the agent's own words) and reality (what happened).\n")
    out.write_text(header + yaml.safe_dump(run, allow_unicode=True, sort_keys=False, width=1000), encoding="utf-8")
    print(out.relative_to(ROOT))


if __name__ == "__main__":
    main()
