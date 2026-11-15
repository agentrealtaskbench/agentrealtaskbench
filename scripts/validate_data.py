#!/usr/bin/env python3
"""Validate data/agents.yaml, data/dimensions.yaml and every results run file.

Usage: python3 scripts/validate_data.py
"""
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
GROUPS = {"assistant", "doer", "texting", "open"}
MARKETS = {"global", "china"}
STATUSES = {"tracked", "testing", "tested"}
OUTCOMES = {"pass", "partial", "fail", "violation", "unsupported"}
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def bilingual(v):
    return isinstance(v, dict) and v.get("en") and v.get("zh")


def check_agents(errors):
    agents = yaml.safe_load((ROOT / "data" / "agents.yaml").read_text(encoding="utf-8"))
    seen = set()
    for a in agents:
        where = f"data/agents.yaml: {a.get('id', '?')}"
        for key in ("id", "group", "name", "maker", "market", "url", "kind", "status"):
            if key not in a:
                errors.append(f"{where}: missing '{key}'")
        if not ID_RE.match(str(a.get("id", ""))):
            errors.append(f"{where}: id must be lowercase-with-dashes")
        if a.get("id") in seen:
            errors.append(f"{where}: duplicate id")
        seen.add(a.get("id"))
        if a.get("group") not in GROUPS:
            errors.append(f"{where}: unknown group '{a.get('group')}'")
        if a.get("market") not in MARKETS:
            errors.append(f"{where}: unknown market '{a.get('market')}'")
        if a.get("status") not in STATUSES:
            errors.append(f"{where}: unknown status '{a.get('status')}'")
        if not str(a.get("url", "")).startswith("https://"):
            errors.append(f"{where}: url must be https")
        for key in ("name", "maker", "kind"):
            if key in a and not bilingual(a[key]):
                errors.append(f"{where}: '{key}' needs en and zh")
        for key in ("price", "regions"):
            if key in a:
                if not bilingual(a[key]):
                    errors.append(f"{where}: '{key}' needs en and zh")
                if "checked" not in a:
                    errors.append(f"{where}: '{key}' needs a 'checked' date")
        if not (ROOT / "site" / "logos" / f"{a.get('id')}.png").exists():
            print(f"note: {where}: no icon at site/logos/{a.get('id')}.png (a letter is shown instead)")
    return seen


def check_dimensions(errors):
    dims = yaml.safe_load((ROOT / "data" / "dimensions.yaml").read_text(encoding="utf-8"))
    for d in dims:
        if not (bilingual(d.get("name")) and bilingual(d.get("about"))):
            errors.append(f"data/dimensions.yaml: {d.get('id')}: name and about need en and zh")


def check_runs(errors, agent_ids):
    tasks = {}
    for p in (ROOT / "tasks").glob("*/*.yaml"):
        t = yaml.safe_load(p.read_text(encoding="utf-8"))
        tasks[t["id"]] = t
    count = 0
    for p in sorted((ROOT / "results").glob("*/runs/*/*.yaml")):
        where = p.relative_to(ROOT)
        run = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        count += 1
        for key in ("task", "task_version", "agent", "outcome", "run_at", "reviews", "evidence"):
            if key not in run:
                errors.append(f"{where}: missing '{key}'")
        task = tasks.get(run.get("task"))
        if not task:
            errors.append(f"{where}: unknown task '{run.get('task')}'")
        if run.get("agent") not in agent_ids:
            errors.append(f"{where}: unknown agent '{run.get('agent')}'")
        if p.parent.name != run.get("agent") or p.stem != run.get("task"):
            errors.append(f"{where}: path must be results/<round>/runs/<agent>/<task>.yaml")
        if run.get("outcome") not in OUTCOMES:
            errors.append(f"{where}: bad outcome '{run.get('outcome')}'")
        if task and run.get("outcome") == "violation" and not task["safety"]:
            errors.append(f"{where}: 'violation' is only allowed on safety tasks")
        reviews = run.get("reviews") or []
        if run.get("outcome") != "unsupported" and len(reviews) < 2:
            errors.append(f"{where}: needs at least two reviews (tester and second reviewer)")
        if not run.get("evidence") and run.get("outcome") != "unsupported":
            errors.append(f"{where}: needs at least one evidence link")
        for ev in run.get("evidence") or []:
            if not str(ev).startswith("https://"):
                errors.append(f"{where}: evidence must be https links, got '{ev}'")
        outs = [r.get("outcome") for r in reviews]
        if any(o not in OUTCOMES for o in outs):
            errors.append(f"{where}: every review needs a final outcome (no TODO)")
        names = [r.get("reviewer") for r in reviews]
        if len(set(outs[:2])) > 1 and "third" not in names:
            errors.append(f"{where}: tester and second reviewer disagree; add a 'third' review")
        decided = next((r.get("outcome") for r in reviews if r.get("reviewer") == "third"), outs[0] if outs else None)
        if reviews and run.get("outcome") != decided:
            errors.append(f"{where}: outcome must equal the agreed review (or the third reviewer's call)")
    return count


def main():
    errors = []
    agent_ids = check_agents(errors)
    check_dimensions(errors)
    runs = check_runs(errors, agent_ids)
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print(f"OK: {len(agent_ids)} agents, {runs} runs")


if __name__ == "__main__":
    main()
