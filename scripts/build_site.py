#!/usr/bin/env python3
"""Build the static ARTB site into dist/.

Inputs:  tasks/*/*.yaml, data/agents.yaml, data/dimensions.yaml,
         results/<round>/runs/<agent>/<task>.yaml, METHODOLOGY*.md
Output:  dist/ (plain HTML/CSS/JS, deployable to Cloudflare Pages)

Usage: python3 scripts/build_site.py [--base-url https://agentrealtaskbench.ai]
"""
import argparse
import html
import json
import pathlib
import re
import shutil

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
SITE = ROOT / "site"
REPO = "https://github.com/agentrealtaskbench/agentrealtaskbench"
X_URL = "https://x.com/davidliyangbing"
LANGS = ("en", "zh")
OUTCOME_POINTS = {"pass": 2, "partial": 1, "fail": 0, "violation": -2, "unsupported": 0}
BOARD_ORDER = ("core", "china_local", "global_local")

T = {
    "en": {
        "lang": "en", "other": "zh", "other_label": "中文",
        "tagline": "Can your AI agent actually get things done?",
        "sub": "Real tasks from everyday life. Every run recorded. Every score backed by evidence. US and Chinese agents, in English and Chinese.",
        "nav": [("grid", "Scorecard"), ("agents", "Agents"), ("compare", "Compare"), ("dimensions", "Dimensions"),
                ("tasks", "Tasks"), ("fails", "Fails"), ("methodology", "Method"), ("about", "About")],
        "request": "Request a test", "usecase": "Submit a use case", "feedback": "Task feedback",
        "not_tested": "Not tested", "untested_note": "Untested means blank. We never guess a score.",
        "overall": "Overall", "safety": "Safety", "coverage": "Coverage", "agent": "Agent",
        "market": {"china": "China", "global": "Global"}, "maker": "Maker", "kind": "Type", "website": "Website",
        "status": {"tracked": "Listed, testing soon", "testing": "Testing now", "tested": "Tested"},
        "boards": {"core": "Core tasks", "china_local": "China local", "global_local": "Global local"},
        "board_note": {"core": "Every agent runs these. Scores are comparable across agents.",
                       "china_local": "Scored separately. Not part of the overall score.",
                       "global_local": "Scored separately. Not part of the overall score."},
        "outcome": {"pass": "Pass", "partial": "Partial", "fail": "Fail", "violation": "Violation", "unsupported": "Unsupported"},
        "scenario": "The situation", "prompt": "What we say to the agent", "params": "Changes every round",
        "setup": "Setup", "interruption": "Interruption", "criteria": "How it is judged", "evidence": "Evidence we keep",
        "results": "Results", "dims": "Dimensions", "task": "Task", "safety_task": "Safety task",
        "round": "Round", "no_runs": "No published runs yet. Round 01 is in progress.",
        "fails_title": "Fail of the day", "fails_empty": "Nothing here yet. When an agent confidently gets something wrong, the recording goes here.",
        "compare_pick": "Pick two agents", "versus": "vs",
        "home_diff_title": "How ARTB is built",
        "home_diff": [
            ("30 tasks, not 15", "Every dimension has at least one task. Concrete values change every round, so nobody can train for the test."),
            ("Two reviewers, blind", "A second reviewer scores from the evidence without seeing the first score. Disagreements go to a third."),
            ("Rules you can check", "Pass, partial, fail and violation are written so you can check them against the recording."),
            ("China and the US", "Doubao, Kimi and Yuanbao next to ChatGPT, Gemini and Manus. Plus separate China and global local boards."),
            ("Safety scored on its own", "Six tasks test whether an agent sends, pays or deletes without asking. Any violation is flagged."),
            ("Everything is open", "Tasks, method, fixture generators and results live in a public GitHub repo."),
        ],
        "home_round": "Round 01", "home_round_note": "10 agents, 30 tasks. Results will be published with every recording.",
        "home_who": "Run by David Li, founder of SandBase (AI agent infrastructure). SandBase and its direct competitors are never evaluated.",
        "params_note": "Prompt templates are public. The concrete values are published with each round's results.",
        "violation_note": "Safety tasks only.",
        "tested_of": "tested {n} of {m}",
        "follow": "Follow on X", "view_source": "Source on GitHub",
        "request_title": "Get involved",
        "request_items": [("request", "Request a test", "Want an agent tested? Open a request. We schedule by 👍 votes.", "test-request.yml"),
                          ("usecase", "Submit a use case", "A real task from your life that agents should be able to do. Credited if used.", "use-case.yml"),
                          ("feedback", "Task feedback", "Think a task or criterion is unfair? Tell us. Vendors please disclose.", "task-feedback.yml")],
        "about_title": "About",
        "about_body": [
            "AgentRealTaskBench (ARTB) is an open, human-run benchmark for personal AI agents and assistants.",
            "Each task is something a real person would ask. Each score links to the recording. The whole task set lives in a public repo.",
            "ARTB is run by David Li, founder of SandBase, which builds infrastructure for AI agents. To keep it neutral: SandBase and directly competing infrastructure products are not evaluated; agents are tested as shipped, with no tools or plugins added by us; no sponsorships, no paid placement, and we pay for every subscription we test; vendors can check facts 48 hours before publication, and corrections are logged in public.",
            "Think a score is wrong, or shipped a fix since we tested? Open task feedback and we will retest.",
        ],
        "footer": "Task set CC BY 4.0. No sponsors, no paid placement.",
        "agents_title": "Agents", "dims_title": "Dimensions", "tasks_title": "Task set v1.0", "grid_title": "Scorecard",
        "compare_title": "Compare", "method_title": "Method",
    },
    "zh": {
        "lang": "zh-CN", "other": "en", "other_label": "English",
        "tagline": "你的 AI 助理，真的能把事办成吗？",
        "sub": "用日常生活里的真实任务去测，每次测试都录屏，每个分数都有证据。同时覆盖中国和海外产品，中英双语。",
        "nav": [("grid", "总榜"), ("agents", "产品"), ("compare", "对比"), ("dimensions", "维度"),
                ("tasks", "任务"), ("fails", "翻车现场"), ("methodology", "方法"), ("about", "关于")],
        "request": "申请测评", "usecase": "投稿场景", "feedback": "任务反馈",
        "not_tested": "未测", "untested_note": "没测就留空，我们从不估分。",
        "overall": "总分", "safety": "安全分", "coverage": "覆盖", "agent": "产品",
        "market": {"china": "中国", "global": "海外"}, "maker": "厂商", "kind": "类型", "website": "官网",
        "status": {"tracked": "已收录，即将测试", "testing": "测试中", "tested": "已测试"},
        "boards": {"core": "通用任务", "china_local": "中国本地", "global_local": "海外本地"},
        "board_note": {"core": "所有产品都测，分数可以横向比较。",
                       "china_local": "单独计分，不计入总分。",
                       "global_local": "单独计分，不计入总分。"},
        "outcome": {"pass": "通过", "partial": "部分通过", "fail": "失败", "violation": "越权", "unsupported": "不支持"},
        "scenario": "场景", "prompt": "我们对 agent 说的话", "params": "每轮更换的参数",
        "setup": "准备", "interruption": "打断方式", "criteria": "判定标准", "evidence": "保留的证据",
        "results": "结果", "dims": "维度", "task": "任务", "safety_task": "安全任务",
        "round": "轮次", "no_runs": "还没有发布结果，第一轮正在进行。",
        "fails_title": "翻车现场", "fails_empty": "这里暂时是空的。agent 自信满满却办错的时候，录屏会放在这里。",
        "compare_pick": "选两个产品", "versus": "对比",
        "home_diff_title": "ARTB 怎么做",
        "home_diff": [
            ("30 个任务，不是 15 个", "每个维度至少一个任务。具体参数每轮更换，没法针对题目优化。"),
            ("双人盲评", "第二位评审只看证据、看不到第一位的打分，独立判定；有分歧由第三位裁定。"),
            ("标准可以核对", "通过、部分通过、失败、越权都写成可以对照录屏核对的标准。"),
            ("中国和海外一起测", "豆包、Kimi、元宝和 ChatGPT、Gemini、Manus 放在一起比，另有中国本地榜和海外本地榜。"),
            ("安全单独计分", "6 个任务专门测 agent 会不会不经同意就发送、付款或删除，越权会被标出来。"),
            ("全部公开", "任务、方法、素材生成器和结果都在公开的 GitHub 仓库里。"),
        ],
        "home_round": "第一轮", "home_round_note": "10 个产品，30 个任务。结果会和全部录屏一起发布。",
        "home_who": "由 David Li 维护。他是 SandBase（AI agent 基础设施）创始人；SandBase 和它的直接竞品不参与评测。",
        "params_note": "提示词模板是公开的，具体参数在每轮结果发布时一起公开。",
        "violation_note": "仅限安全任务。",
        "tested_of": "已测 {n} / {m}",
        "follow": "在 X 上关注", "view_source": "GitHub 源码",
        "request_title": "参与方式",
        "request_items": [("request", "申请测评", "想让我们测某个产品？提交申请，按 👍 数排期。", "test-request.yml"),
                          ("usecase", "投稿场景", "你生活里希望 agent 能办成的一件真事。被采用会署名。", "use-case.yml"),
                          ("feedback", "任务反馈", "觉得某个任务或标准不公平？告诉我们。厂商请注明身份。", "task-feedback.yml")],
        "about_title": "关于",
        "about_body": [
            "AgentRealTaskBench（ARTB）是一个公开的、由真人执行的 personal agent / AI 助理评测。",
            "每个任务都是真实用户会提的要求，每个分数都链接到录屏，完整任务集放在公开仓库里。",
            "ARTB 由 David Li 维护。他是 SandBase 的创始人，SandBase 做的是 AI agent 基础设施。为了保持中立：不评测 SandBase，也不评测与它直接竞争的基础设施产品；所有 agent 按出厂状态测试，我们不额外加装工具或插件；不接受赞助，不卖排名，所有订阅费用自己支付；厂商可以在发布前 48 小时核对事实，所有更正公开记录。",
            "觉得分数不对，或者测试之后已经修好了？提交任务反馈，我们会重测。",
        ],
        "footer": "任务集采用 CC BY 4.0 许可。不接受赞助，不卖排名。",
        "agents_title": "产品", "dims_title": "维度", "tasks_title": "任务集 v1.0", "grid_title": "总榜",
        "compare_title": "对比", "method_title": "评测方法",
    },
}

e = html.escape


def load_yaml(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load():
    tasks = [load_yaml(p) for p in sorted((ROOT / "tasks").glob("*/*.yaml"))]
    tasks.sort(key=lambda t: (BOARD_ORDER.index(t["board"]), t["id"]))
    agents = load_yaml(ROOT / "data" / "agents.yaml")
    dims = load_yaml(ROOT / "data" / "dimensions.yaml")
    runs = []
    for p in sorted((ROOT / "results").glob("*/runs/*/*.yaml")):
        run = load_yaml(p)
        run.setdefault("round", p.parts[-4])
        if run.get("outcome") not in OUTCOME_POINTS:
            raise SystemExit(f"{p}: bad outcome {run.get('outcome')!r}")
        runs.append(run)
    return tasks, agents, dims, runs


def score(task_ids, by_task):
    """0-10 score over the given tasks, or None if none of them has a run."""
    tested = [t for t in task_ids if t in by_task]
    if not tested:
        return None
    pts = sum(OUTCOME_POINTS[by_task[t]["outcome"]] for t in tested)
    # Untested tasks are left out, never counted as 0. Coverage is shown next to every score.
    return max(0.0, round(pts / (2 * len(tested)) * 10, 1))


def latest_runs(runs):
    """Latest run per (agent, task); a re-run replaces the earlier one."""
    out = {}
    for r in sorted(runs, key=lambda r: str(r.get("run_at", ""))):
        out[(r["agent"], r["task"])] = r
    return out


def compute(tasks, agents, dims, runs):
    latest = latest_runs(runs)
    core = [t["id"] for t in tasks if t["board"] == "core"]
    safety = [t["id"] for t in tasks if t["safety"]]
    board_ids = {b: [t["id"] for t in tasks if t["board"] == b] for b in BOARD_ORDER}
    dim_tasks = {d["id"]: [t["id"] for t in tasks if d["id"] in t["dimensions"]] for d in dims}
    table = {}
    for a in agents:
        by_task = {tid: r for (aid, tid), r in latest.items() if aid == a["id"]}
        table[a["id"]] = {
            "runs": by_task,
            "overall": score(core, by_task),
            "safety": score(safety, by_task),
            "violations": sum(1 for r in by_task.values() if r["outcome"] == "violation"),
            "boards": {b: score(ids, by_task) for b, ids in board_ids.items()},
            "dims": {d: score(ids, by_task) for d, ids in dim_tasks.items()},
            "coverage": sum(1 for t in core if t in by_task),
        }
    return table, dim_tasks, len(core)


# ---------------------------------------------------------------- rendering

def fmt(v, L):
    return f'<span class="score">{v:.1f}</span>' if v is not None else f'<span class="blank" title="{e(T[L]["untested_note"])}">—</span>'


def badge(outcome, L):
    return f'<span class="badge {outcome}">{e(T[L]["outcome"][outcome])}</span>'


def page(L, path, title, body, desc=None):
    t = T[L]
    nav = "".join(f'<a href="/{L}/{slug}/"{" aria-current=page" if path.startswith(slug) else ""}>{e(label)}</a>'
                  for slug, label in t["nav"])
    alt = f"/{t['other']}/{path}"
    canonical = f"{BASE}/{L}/{path}"
    full_title = f"{title} · AgentRealTaskBench" if title else "AgentRealTaskBench"
    desc = desc or t["sub"]
    return f"""<!doctype html>
<html lang="{t['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="en" href="{BASE}/en/{path}">
<link rel="alternate" hreflang="zh-CN" href="{BASE}/zh/{path}">
<link rel="alternate" hreflang="x-default" href="{BASE}/en/{path}">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary">
<meta name="twitter:creator" content="@davidliyangbing">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/style.css">
</head>
<body>
<header class="top">
  <a class="brand" href="/{L}/"><span class="mark">ARTB</span><span class="name">AgentRealTaskBench</span></a>
  <nav>{nav}</nav>
  <div class="tools"><a class="lang" href="{alt}" hreflang="{t['other']}">{e(t['other_label'])}</a>
  <a class="cta" href="/{L}/request/">{e(t['request'])}</a></div>
</header>
<main>
{body}
</main>
<footer>
  <p>{e(t['footer'])} · <a href="{REPO}">{e(t['view_source'])}</a> · <a href="{X_URL}">{e(t['follow'])}</a></p>
</footer>
</body>
</html>
"""


def task_link(task, L):
    return f'<a href="/{L}/tasks/{task["id"].lower()}/">{e(task["id"])}</a>'


def agent_name(a, L):
    return a["name"][L]


def render_home(L, tasks, agents, table, n_core):
    t = T[L]
    diff = "".join(f"<li><h3>{e(h)}</h3><p>{e(p)}</p></li>" for h, p in t["home_diff"])
    chips = "".join(
        f'<a class="chip" href="/{L}/agents/{a["id"]}/"><b>{e(agent_name(a, L))}</b>'
        f'<span>{e(t["market"][a["market"]])} · {e(t["tested_of"].format(n=table[a["id"]]["coverage"], m=n_core))}</span></a>'
        for a in agents)
    sample = [x for x in tasks if x["id"] in ("ARTB-001", "ARTB-004", "ARTB-C04")]
    cards = "".join(
        f'<a class="taskcard" href="/{L}/tasks/{x["id"].lower()}/"><span class="tid">{e(x["id"])}</span>'
        f'<h3>{e(x["title"][L])}</h3><p>{e(x["scenario"][L])}</p></a>' for x in sample)
    body = f"""
<section class="hero">
  <h1>{e(t['tagline'])}</h1>
  <p class="lede">{e(t['sub'])}</p>
  <p class="actions"><a class="cta big" href="/{L}/grid/">{e(t['grid_title'])} →</a>
  <a class="ghost" href="/{L}/tasks/">{e(t['tasks_title'])}</a></p>
</section>
<section>
  <h2>{e(t['home_round'])}</h2><p class="muted">{e(t['home_round_note'])}</p>
  <div class="chips">{chips}</div>
</section>
<section><div class="cards">{cards}</div></section>
<section>
  <h2>{e(t['home_diff_title'])}</h2>
  <ul class="diff">{diff}</ul>
</section>
<section class="who"><p>{e(t['home_who'])} <a href="/{L}/about/">{e(t['about_title'])} →</a></p></section>
"""
    return page(L, "", "", body)


def render_grid(L, tasks, agents, dims, table, n_core):
    t = T[L]
    head = "".join(f'<th scope="col"><a href="/{L}/dimensions/{d["id"]}/">{e(d["name"][L])}</a></th>' for d in dims)
    rows = []
    # Agents with most core tasks tested rank first; a high score on 1 task must not top the board.
    def rank(a):
        r = table[a["id"]]
        full = r["coverage"] * 4 >= n_core * 3  # at least 75% of core tasks tested
        return (not full, 0 if full else -r["coverage"],
                -(r["overall"] if r["overall"] is not None else -1), a["id"])
    order = sorted(agents, key=rank)
    for a in order:
        r = table[a["id"]]
        flag = f' <span class="badge violation">{r["violations"]}× {e(t["outcome"]["violation"])}</span>' if r["violations"] else ""
        cells = "".join(f"<td>{fmt(r['dims'][d['id']], L)}</td>" for d in dims)
        rows.append(f'<tr><th scope="row"><a href="/{L}/agents/{a["id"]}/">{e(agent_name(a, L))}</a>'
                    f'<small>{e(t["market"][a["market"]])}</small></th>'
                    f'<td class="strong">{fmt(r["overall"], L)}</td><td>{fmt(r["safety"], L)}{flag}</td>'
                    f'<td class="muted">{r["coverage"]}/{n_core}</td>{cells}</tr>')
    body = f"""
<h1>{e(t['grid_title'])}</h1>
<p class="muted">{e(t['untested_note'])}</p>
<div class="scroll"><table class="grid">
<thead><tr><th scope="col">{e(t['agent'])}</th><th scope="col">{e(t['overall'])}</th><th scope="col">{e(t['safety'])}</th><th scope="col">{e(t['coverage'])}</th>{head}</tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
"""
    return page(L, "grid/", t["grid_title"], body)


def outcome_cell(run, L):
    if not run:
        return f'<span class="blank">{e(T[L]["not_tested"])}</span>'
    ev = run.get("evidence") or []
    link = f' <a href="{e(ev[0])}">▶</a>' if ev else ""
    return badge(run["outcome"], L) + link


def render_agents(L, agents, table, n_core):
    t = T[L]
    items = "".join(
        f'<li><a href="/{L}/agents/{a["id"]}/"><b>{e(agent_name(a, L))}</b></a>'
        f'<span>{e(a["maker"][L])} · {e(a["kind"][L])} · {e(t["market"][a["market"]])}</span>'
        f'<span class="muted">{e(t["status"][a["status"]])}</span></li>' for a in agents)
    return page(L, "agents/", t["agents_title"], f"<h1>{e(t['agents_title'])}</h1><ul class='list'>{items}</ul>")


def render_agent(L, a, tasks, dims, table, n_core):
    t = T[L]
    r = table[a["id"]]
    boards = []
    for b in BOARD_ORDER:
        rows = "".join(
            f"<tr><td>{task_link(x, L)}</td><td>{e(x['title'][L])}{' <span class=tag>' + e(t['safety_task']) + '</span>' if x['safety'] else ''}</td>"
            f"<td>{outcome_cell(r['runs'].get(x['id']), L)}</td>"
            f"<td class='muted'>{e((r['runs'].get(x['id']) or {}).get('note_' + L) or (r['runs'].get(x['id']) or {}).get('note') or '')}</td></tr>"
            for x in tasks if x["board"] == b)
        boards.append(f"<h2>{e(t['boards'][b])} {fmt(r['boards'][b], L)}</h2><p class='muted'>{e(t['board_note'][b])}</p>"
                      f"<table class='runs'><tbody>{rows}</tbody></table>")
    dimrows = "".join(f'<li><a href="/{L}/dimensions/{d["id"]}/">{e(d["name"][L])}</a>{fmt(r["dims"][d["id"]], L)}</li>' for d in dims)
    body = f"""
<p class="crumb"><a href="/{L}/agents/">{e(t['agents_title'])}</a></p>
<h1>{e(agent_name(a, L))}</h1>
<dl class="facts">
<dt>{e(t['maker'])}</dt><dd>{e(a['maker'][L])}</dd>
<dt>{e(t['kind'])}</dt><dd>{e(a['kind'][L])}</dd>
<dt>{e(t['website'])}</dt><dd><a href="{e(a['url'])}" rel="nofollow noopener">{e(a['url'].split('//')[1])}</a></dd>
<dt>{e(t['round'])}</dt><dd>{e(a.get('round', ''))} · {e(t['status'][a['status']])}</dd>
</dl>
<div class="scorebar"><div><span>{e(t['overall'])}</span>{fmt(r['overall'], L)}</div>
<div><span>{e(t['safety'])}</span>{fmt(r['safety'], L)}</div>
<div><span>{e(t['coverage'])}</span><span class="score">{r['coverage']}/{n_core}</span></div></div>
<ul class="dimlist">{dimrows}</ul>
{''.join(boards)}
"""
    return page(L, f"agents/{a['id']}/", agent_name(a, L), body)


def render_dimensions(L, dims, dim_tasks, tasks_by_id):
    t = T[L]
    items = "".join(
        f'<li><a href="/{L}/dimensions/{d["id"]}/"><b>{e(d["name"][L])}</b></a><span>{e(d["about"][L])}</span>'
        f'<span class="muted">{len(dim_tasks[d["id"]])} × {e(t["task"])}</span></li>' for d in dims)
    return page(L, "dimensions/", t["dims_title"], f"<h1>{e(t['dims_title'])}</h1><ul class='list'>{items}</ul>")


def render_dimension(L, d, dim_tasks, tasks_by_id, agents, table):
    t = T[L]
    tl = "".join(f"<li>{task_link(tasks_by_id[x], L)} {e(tasks_by_id[x]['title'][L])}</li>" for x in dim_tasks[d["id"]])
    ranked = sorted(agents, key=lambda a: -(table[a["id"]]["dims"][d["id"]] if table[a["id"]]["dims"][d["id"]] is not None else -1))
    rows = "".join(f'<tr><td><a href="/{L}/agents/{a["id"]}/">{e(agent_name(a, L))}</a></td><td>{fmt(table[a["id"]]["dims"][d["id"]], L)}</td></tr>' for a in ranked)
    body = f"""
<p class="crumb"><a href="/{L}/dimensions/">{e(t['dims_title'])}</a></p>
<h1>{e(d['name'][L])}</h1><p class="lede">{e(d['about'][L])}</p>
<h2>{e(t['tasks_title'])}</h2><ul>{tl}</ul>
<h2>{e(t['results'])}</h2><table class="runs"><tbody>{rows}</tbody></table>
"""
    return page(L, f"dimensions/{d['id']}/", d["name"][L], body, d["about"][L])


def render_tasks(L, tasks):
    t = T[L]
    parts = []
    for b in BOARD_ORDER:
        cards = "".join(
            f'<a class="taskcard" href="/{L}/tasks/{x["id"].lower()}/"><span class="tid">{e(x["id"])}'
            f'{" · " + e(t["safety_task"]) if x["safety"] else ""}</span><h3>{e(x["title"][L])}</h3><p>{e(x["scenario"][L])}</p></a>'
            for x in tasks if x["board"] == b)
        parts.append(f"<h2>{e(t['boards'][b])}</h2><p class='muted'>{e(t['board_note'][b])}</p><div class='cards'>{cards}</div>")
    return page(L, "tasks/", t["tasks_title"], f"<h1>{e(t['tasks_title'])}</h1>{''.join(parts)}")


def render_task(L, x, dims_by_id, agents, table):
    t = T[L]
    def lst(items):
        return "<ul>" + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul>"
    crit = "".join(
        f"<div class='crit {k}'>{badge(k, L)}{lst(x['criteria'][k][L])}</div>"
        for k in ("pass", "partial", "fail", "violation") if k in x["criteria"])
    params = "".join(f"<li><code>{{{e(p['name'])}}}</code></li>" for p in x["params"]) or "<li>—</li>"
    dims = " ".join(f'<a class="tag" href="/{L}/dimensions/{d}/">{e(dims_by_id[d]["name"][L])}</a>' for d in x["dimensions"])
    inter = f"<h2>{e(t['interruption'])}</h2><p>{e(x['interruption'][L])}</p>" if "interruption" in x else ""
    rows = "".join(f'<tr><td><a href="/{L}/agents/{a["id"]}/">{e(agent_name(a, L))}</a></td>'
                   f'<td>{outcome_cell(table[a["id"]]["runs"].get(x["id"]), L)}</td></tr>' for a in agents)
    body = f"""
<p class="crumb"><a href="/{L}/tasks/">{e(t['tasks_title'])}</a> · {e(t['boards'][x['board']])}</p>
<p class="tid">{e(x['id'])} · v{e(x['task_version'])}{' · ' + e(t['safety_task']) if x['safety'] else ''}</p>
<h1>{e(x['title'][L])}</h1>
<p class="tags">{dims}</p>
<h2>{e(t['scenario'])}</h2><p class="lede">{e(x['scenario'][L])}</p>
<h2>{e(t['prompt'])}</h2><blockquote class="prompt">{e(x['prompt'][L])}</blockquote>
<h2>{e(t['params'])}</h2><ul class="inline">{params}</ul><p class="muted">{e(t['params_note'])}</p>
{inter}
<h2>{e(t['criteria'])}</h2><div class="crits">{crit}</div>
<h2>{e(t['evidence'])}</h2><p class="muted">{e(', '.join(x['evidence']))}</p>
<h2>{e(t['results'])}</h2><table class="runs"><tbody>{rows}</tbody></table>
<p class="muted"><a href="{REPO}/blob/main/tasks/{x['board']}/{x['id']}-{x['slug']}.yaml">YAML</a> ·
<a href="{REPO}/issues/new?template=task-feedback.yml&title=Task+feedback%3A+{x['id']}">{e(t['feedback'])}</a></p>
"""
    return page(L, f"tasks/{x['id'].lower()}/", f"{x['id']} {x['title'][L]}", body, x["scenario"][L])


def render_fails(L, runs, agents_by_id, tasks_by_id):
    t = T[L]
    items = [r for r in sorted(runs, key=lambda r: str(r.get("run_at", "")), reverse=True)
             if r["outcome"] in ("fail", "violation") and (r.get("quote_" + L) or r.get("quote"))]
    if not items:
        body = f"<h1>{e(t['fails_title'])}</h1><p class='empty'>{e(t['fails_empty'])}</p>"
    else:
        cards = "".join(
            f"<article class='failcard'>{badge(r['outcome'], L)} <b>{e(agent_name(agents_by_id[r['agent']], L))}</b> · "
            f"{task_link(tasks_by_id[r['task']], L)} {e(tasks_by_id[r['task']]['title'][L])}"
            f"<blockquote>{e(r.get('quote_' + L) or r.get('quote'))}</blockquote>"
            f"<p>{e(r.get('reality_' + L) or r.get('reality') or '')}</p>"
            + (f"<a href='{e(r['evidence'][0])}'>▶</a>" if r.get("evidence") else "") + "</article>" for r in items)
        body = f"<h1>{e(t['fails_title'])}</h1>{cards}"
    return page(L, "fails/", t["fails_title"], body)


def render_compare(L, agents, dims, table, n_core):
    t = T[L]
    data = {a["id"]: {"name": agent_name(a, L), "overall": table[a["id"]]["overall"], "safety": table[a["id"]]["safety"],
                      "coverage": table[a["id"]]["coverage"], "dims": table[a["id"]]["dims"]} for a in agents}
    labels = {"dims": {d["id"]: d["name"][L] for d in dims}, "overall": t["overall"], "safety": t["safety"],
              "coverage": t["coverage"], "blank": "—", "n_core": n_core}
    opts = "".join(f'<option value="{a["id"]}">{e(agent_name(a, L))}</option>' for a in agents)
    body = f"""
<h1>{e(t['compare_title'])}</h1><p class="muted">{e(t['compare_pick'])}</p>
<p class="pick"><select id="a">{opts}</select> <span>{e(t['versus'])}</span> <select id="b">{opts}</select></p>
<table class="runs compare"><tbody id="out"></tbody></table>
<script id="data" type="application/json">{json.dumps({"agents": data, "labels": labels}, ensure_ascii=False).replace("</", "<\\/")}</script>
<script src="/compare.js"></script>
"""
    return page(L, "compare/", t["compare_title"], body)


def render_md_page(L, slug, title, md_path):
    return page(L, f"{slug}/", title, md_to_html(md_path.read_text(encoding="utf-8"), L))


def render_about(L):
    t = T[L]
    paras = "".join(f"<p>{e(p)}</p>" for p in t["about_body"])
    body = f"<h1>{e(t['about_title'])}</h1>{paras}<p><a href='{X_URL}'>@davidliyangbing</a> · <a href='{REPO}'>GitHub</a></p>"
    return page(L, "about/", t["about_title"], body)


def render_request(L):
    t = T[L]
    items = "".join(f'<li><a class="cta" href="{REPO}/issues/new?template={tpl}">{e(h)}</a><p>{e(p)}</p></li>'
                    for _, h, p, tpl in t["request_items"])
    return page(L, "request/", t["request_title"], f"<h1>{e(t['request_title'])}</h1><ul class='requests'>{items}</ul>")


# ------------------------------------------------------- tiny markdown → html

def inline(s, L):
    s = e(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)

    def link(m):
        text, href = m.group(1), m.group(2)
        if href.startswith("../../"):
            href = REPO + "/" + href[6:]
        elif href in ("METHODOLOGY.md", "METHODOLOGY.zh-CN.md"):
            href = f"/{'zh' if 'zh' in href else 'en'}/methodology/"
        return f'<a href="{href}">{text}</a>'
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, s)


def md_to_html(md, L):
    out, lines, i = [], md.splitlines(), 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            text = line[level:].strip()
            if "[" in text and "](" in text and level == 1:
                text = re.sub(r"\s*\[.*$", "", text)
            out.append(f"<h{level}>{inline(text, L)}</h{level}>")
            i += 1
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                if not re.match(r"^\|[\s\-:|]+\|$", lines[i]):
                    rows.append([c.strip() for c in lines[i].strip("|").split("|")])
                i += 1
            head, *rest = rows
            out.append("<table class='runs'><thead><tr>" + "".join(f"<th>{inline(c, L)}</th>" for c in head) + "</tr></thead><tbody>"
                       + "".join("<tr>" + "".join(f"<td>{inline(c, L)}</td>" for c in r) + "</tr>" for r in rest) + "</tbody></table>")
        elif re.match(r"^(\s*)([-*]|\d+\.)\s", line):
            tag = "ol" if re.match(r"^\s*\d+\.", line) else "ul"
            items = []
            while i < len(lines) and re.match(r"^(\s*)([-*]|\d+\.)\s", lines[i]):
                items.append(re.sub(r"^\s*([-*]|\d+\.)\s", "", lines[i]))
                i += 1
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x, L)}</li>" for x in items) + f"</{tag}>")
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not re.match(r"^(#|\||\s*([-*]|\d+\.)\s)", lines[i]):
                para.append(lines[i].strip())
                i += 1
            out.append(f"<p>{inline(' '.join(para), L)}</p>")
    return "\n".join(out)


# ------------------------------------------------------------------- build

def write(rel, text):
    p = DIST / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    PAGES.append(rel)


def main():
    global BASE, PAGES
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="https://agentrealtaskbench.ai")
    BASE = ap.parse_args().base_url.rstrip("/")
    PAGES = []
    tasks, agents, dims, runs = load()
    known = {a["id"] for a in agents}
    for r in runs:
        if r["agent"] not in known:
            raise SystemExit(f"run for unknown agent {r['agent']}")
    table, dim_tasks, n_core = compute(tasks, agents, dims, runs)
    tasks_by_id = {x["id"]: x for x in tasks}
    dims_by_id = {d["id"]: d for d in dims}
    agents_by_id = {a["id"]: a for a in agents}
    unknown = {d for x in tasks for d in x["dimensions"]} - set(dims_by_id)
    if unknown:
        raise SystemExit(f"dimensions missing from data/dimensions.yaml: {unknown}")

    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(SITE, DIST)
    PAGES.clear()
    for L in LANGS:
        write(f"{L}/index.html", render_home(L, tasks, agents, table, n_core))
        write(f"{L}/grid/index.html", render_grid(L, tasks, agents, dims, table, n_core))
        write(f"{L}/agents/index.html", render_agents(L, agents, table, n_core))
        for a in agents:
            write(f"{L}/agents/{a['id']}/index.html", render_agent(L, a, tasks, dims, table, n_core))
        write(f"{L}/compare/index.html", render_compare(L, agents, dims, table, n_core))
        write(f"{L}/dimensions/index.html", render_dimensions(L, dims, dim_tasks, tasks_by_id))
        for d in dims:
            write(f"{L}/dimensions/{d['id']}/index.html", render_dimension(L, d, dim_tasks, tasks_by_id, agents, table))
        write(f"{L}/tasks/index.html", render_tasks(L, tasks))
        for x in tasks:
            write(f"{L}/tasks/{x['id'].lower()}/index.html", render_task(L, x, dims_by_id, agents, table))
        write(f"{L}/fails/index.html", render_fails(L, runs, agents_by_id, tasks_by_id))
        md = ROOT / ("METHODOLOGY.zh-CN.md" if L == "zh" else "METHODOLOGY.md")
        write(f"{L}/methodology/index.html", render_md_page(L, "methodology", T[L]["method_title"], md))
        write(f"{L}/about/index.html", render_about(L))
        write(f"{L}/request/index.html", render_request(L))

    urls = "".join(f"<url><loc>{BASE}/{p[:-len('index.html')]}</loc></url>" for p in PAGES)
    (DIST / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>',
        encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
    export = {"tasks": tasks, "agents": agents, "dimensions": dims,
              "scores": {aid: {k: v for k, v in row.items() if k != "runs"} for aid, row in table.items()},
              "runs": runs}
    (DIST / "data.json").write_text(json.dumps(export, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"Built {len(PAGES)} pages into {DIST.relative_to(ROOT)}/ ({len(runs)} runs)")


if __name__ == "__main__":
    main()
