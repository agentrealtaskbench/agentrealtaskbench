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
        "lang": "en", "other": "zh", "other_label": "中文", "theme_label": "Switch light / dark",
        "tagline": "Can your AI agent actually [get things done]?",
        "sub": "Real tasks from everyday life. Every run recorded. Every score backed by evidence. In English and Chinese.",
        "nav": [("grid", "Scorecard"), ("agents", "Agents"), ("compare", "Compare"), ("dimensions", "Dimensions"),
                ("tasks", "Tasks"), ("fails", "Fails"), ("methodology", "Method"), ("about", "About")],
        "request": "Request a test", "usecase": "Submit a use case", "feedback": "Task feedback",
        "not_tested": "Not tested", "untested_note": "Untested means blank. We never guess a score.",
        "overall": "Overall", "safety": "Safety", "coverage": "Coverage", "agent": "Agent",
        "market": {"china": "China", "global": "Global"}, "maker": "Maker", "kind": "Type", "website": "Website",
        "status": {"tracked": "Listed, testing soon", "testing": "Testing now", "tested": "Tested"},
        "boards": {"core": "Core tasks", "china_local": "Local: China apps", "global_local": "Local: US apps"},
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
            ("30 real tasks", "Every dimension has at least one task. Concrete values change every round, so nobody can train for the test."),
            ("Two reviewers, blind", "A second reviewer scores from the evidence without seeing the first score. Disagreements go to a third."),
            ("Rules you can check", "Pass, partial, fail and violation are written so you can check them against the recording."),
            ("Same tasks for everyone", "Big-lab assistants, startups you text and open-source agents all run the same 20 core tasks."),
            ("Safety scored on its own", "Six tasks test whether an agent sends, pays or deletes without asking. Any violation is flagged."),
            ("Everything is open", "Tasks, method, fixture generators and results live in a public GitHub repo."),
        ],
        "home_round": "Round 01", "home_round_note": "{n} agents, {m} tasks. Results will be published with every recording.",
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
        "lang": "zh-CN", "other": "en", "other_label": "English", "theme_label": "切换白色 / 深色",
        "tagline": "你的 AI 助理，|[真的能把事办成]吗？",
        "sub": "用日常生活里的真实任务去测，每次测试都录屏，每个分数都有证据。中英双语。",
        "nav": [("grid", "总榜"), ("agents", "产品"), ("compare", "对比"), ("dimensions", "维度"),
                ("tasks", "任务"), ("fails", "翻车现场"), ("methodology", "方法"), ("about", "关于")],
        "request": "申请测评", "usecase": "投稿场景", "feedback": "任务反馈",
        "not_tested": "未测", "untested_note": "没测就留空，我们从不估分。",
        "overall": "总分", "safety": "安全分", "coverage": "覆盖", "agent": "产品",
        "market": {"china": "中国", "global": "海外"}, "maker": "厂商", "kind": "类型", "website": "官网",
        "status": {"tracked": "已收录，即将测试", "testing": "测试中", "tested": "已测试"},
        "boards": {"core": "通用任务", "china_local": "本地任务 · 国内应用", "global_local": "本地任务 · 海外应用"},
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
            ("30 个真实任务", "每个维度至少一个任务。具体参数每轮更换，没法针对题目优化。"),
            ("双人盲评", "第二位评审只看证据、看不到第一位的打分，独立判定；有分歧由第三位裁定。"),
            ("标准可以核对", "通过、部分通过、失败、越权都写成可以对照录屏核对的标准。"),
            ("所有产品同一套题", "大厂助理、发消息就能用的创业产品和开源 agent，都跑同样的 20 个通用任务。"),
            ("安全单独计分", "6 个任务专门测 agent 会不会不经同意就发送、付款或删除，越权会被标出来。"),
            ("全部公开", "任务、方法、素材生成器和结果都在公开的 GitHub 仓库里。"),
        ],
        "home_round": "第一轮", "home_round_note": "{n} 个产品，{m} 个任务。结果会和全部录屏一起发布。",
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
    return f'<span class="status {outcome}">{e(T[L]["outcome"][outcome])}</span>'


STRIP = {
    "en": ("ROUND 01", "{n} agents, {m} real tasks. Results land here with every recording.", "Request a test"),
    "zh": ("第一轮", "{n} 个产品，{m} 个真实任务。结果会和全部录屏一起发布在这里。", "申请测评"),
}


COUNTS = {"agents": 0, "tasks": 0}

GROUPS = {
    "assistant": {"en": "Everyday assistants", "zh": "日常助理"},
    "doer": {"en": "Agents that do the work", "zh": "替你动手的 agent"},
    "texting": {"en": "Assistants you text", "zh": "发消息就能用的助理"},
    "open": {"en": "Open source", "zh": "开源 · 自部署"},
}
CATS = {
    "comms": {"en": "Messages & email", "zh": "沟通与邮件"},
    "travel": {"en": "Travel & places", "zh": "出行与地点"},
    "shopping": {"en": "Shopping", "zh": "购物"},
    "web": {"en": "On the web", "zh": "网页操作"},
    "schedule": {"en": "Schedule & memory", "zh": "日程与记忆"},
    "research": {"en": "Research & data", "zh": "查资料"},
    "files": {"en": "Files & creative", "zh": "文件与创作"},
}


def icon(a, size=24):
    """Real product icon if we have one, otherwise a lettered disc."""
    f = SITE / "logos" / f"{a['id']}.png"
    if f.exists():
        return (f'<img class="ico" src="/logos/{a["id"]}.png" alt="" width="{size}" height="{size}" '
                f'loading="lazy" decoding="async" style="width:{size}px;height:{size}px">')
    return f'<span class="ico av" style="width:{size}px;height:{size}px">{e(a["name"]["en"][:1])}</span>'


def tabs(name, items, L):
    """Filter buttons. items: [(key, label)]; 'all' is added first."""
    allb = "全部" if L == "zh" else "All"
    btn = lambda k, v, on: f'<button type="button" data-f="{k}" aria-pressed="{"true" if on else "false"}">{e(v)}</button>'
    return f'<div class="tabs" role="group" data-filter="{name}">' + btn("all", allb, True) + "".join(btn(k, v, False) for k, v in items) + "</div>"


def task_tags(x):
    return " ".join([f"cat:{x['category']}", f"board:{x['board']}"] + (["safety"] if x["safety"] else []))


def tcard(x, L, dname, filt=None):
    t = T[L]
    attr = f' data-item="{filt}" data-tags="{task_tags(x)}"' if filt else ""
    tags = f'<span class="tag">{e(CATS[x["category"]][L])}</span>'
    if x["board"] != "core":
        tags += f'<span class="tag">{e(t["boards"][x["board"]])}</span>'
    if x["safety"]:
        tags += f'<span class="tag safe">{e(t["safety_task"])}</span>'
    return (f'<a class="tcard"{attr} href="/{L}/tasks/{x["id"].lower()}/">'
            f'<span class="tid">{e(x["id"])}</span><h3>{e(x["title"][L])}</h3><p class="bubble">{ep(x["prompt"][L])}</p>'
            f'<div class="foot">{tags}</div></a>')


def asset(name):
    """URL with a content hash, so a new deploy never pairs new HTML with a cached old file."""
    import hashlib
    h = hashlib.sha256((SITE / name).read_bytes()).hexdigest()[:10]
    return f"/{name}?v={h}"


def page(L, path, title, body, desc=None, main_class=""):
    t = T[L]
    nav = "".join(f'<a href="/{L}/{slug}/"{" aria-current=page" if path.startswith(slug) else ""}>{e(label)}</a>'
                  for slug, label in t["nav"])
    alt = f"/{t['other']}/{path}"
    canonical = f"{BASE}/{L}/{path}"
    full_title = f"{title} · AgentRealTaskBench" if title else "AgentRealTaskBench"
    desc = desc or t["sub"]
    sb, st, sl = STRIP[L]
    st = st.format(n=COUNTS["agents"], m=COUNTS["tasks"])
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
<meta property="og:image" content="{BASE}/og-{L}.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{BASE}/og-{L}.png">
<meta name="twitter:creator" content="@davidliyangbing">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/fonts/ClashGrotesk-Variable.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{asset('style.css')}">
<script src="{asset('theme.js')}"></script>
</head>
<body>
<div class="strip"><b>{e(sb)}</b><span class="long">{e(st)}</span><a href="/{L}/request/">{e(sl)}</a></div>
<header class="top">
  <a class="brand" href="/{L}/"><span class="logo" aria-hidden="true"><i></i><i></i><i></i><i></i></span><span class="bname">AgentRealTaskBench</span></a>
  <nav>{nav}</nav>
  <div class="tools"><a class="lang" href="{alt}" hreflang="{t['other']}">{e(t['other_label'])}</a><button class="theme" type="button" aria-label="{e(t['theme_label'])}" title="{e(t['theme_label'])}"><svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg><svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg></button>
  <a class="btn primary sm" href="/{L}/request/">{e(t['request'])}</a></div>
</header>
<main{' class=' + main_class if main_class else ''}>
{body}
</main>
<footer>
  <span>AgentRealTaskBench · {e(t['footer'])}</span>
  <span><a href="{REPO}">{e(t['view_source'])}</a> · <a href="{X_URL}">{e(t['follow'])}</a> · <a href="{alt}">{e(t['other_label'])}</a></span>
</footer>
</body>
</html>
"""


def task_link(task, L):
    return f'<a href="/{L}/tasks/{task["id"].lower()}/">{e(task["id"])}</a>'


def agent_name(a, L):
    return a["name"][L]


def phead(eyebrow, title, lede=None, crumb=None, icon_html=""):
    c = f'<p class="crumb">{crumb}</p>' if crumb else ""
    l = f'<p class="lede">{e(lede)}</p>' if lede else ""
    h = f'<div class="titlerow">{icon_html}<h1>{e(title)}</h1></div>' if icon_html else f"<h1>{e(title)}</h1>"
    return f'<div class="phead">{c}<p class="eyebrow">{e(eyebrow)}</p>{h}{l}</div>'


def ep(text):
    """Escape a prompt and draw its {placeholders} as chips."""
    return re.sub(r"\{(\w+)\}", r'<span class="ph">\1</span>', e(text))


def chat_card(x, L, with_rule=True):
    """A task drawn as the conversation it starts: header, the user's message, the pass rule."""
    t = T[L]
    tag = t["safety_task"] if x["safety"] else t["boards"][x["board"]]
    rule = (f'<div class="rule">{badge("pass", L)}<span>{e(x["criteria"]["pass"][L][0])}</span></div>' if with_rule else "")
    return (f'<a class="card" href="/{L}/tasks/{x["id"].lower()}/"><div class="ch"><span>{e(x["id"])}</span><span>{e(tag)}</span></div>'
            f'<p class="bubble">{ep(x["prompt"][L])}</p>{rule}</a>')


def render_home(L, tasks, agents, table, n_core):
    t = T[L]
    zh = L == "zh"
    title = ("你的 AI 助理，<br>真的能<mark>把事办成</mark>吗？" if zh
             else "Can your AI agent<br>actually <mark>get it done?</mark>")
    eyebrow = "一个公开的、由真人执行的 AI 助理评测" if zh else "An open, human-run benchmark for AI assistants"
    fine = (["每个分数都有录屏", "不收赞助", "任务全部公开"] if zh
            else ["Every score has a recording", "No sponsors", "Every task is public"])
    dname = {d["id"]: d["name"][L] for d in load_yaml(ROOT / "data" / "dimensions.yaml")}
    rows = []
    for g, label in GROUPS.items():
        members = [a for a in agents if a.get("group") == g]
        if not members:
            continue
        pills = "".join(f'<a class="pill" href="/{L}/agents/{a["id"]}/">{icon(a, 22)}{e(agent_name(a, L))}</a>' for a in members)
        rows.append(f'<div class="prow"><span class="plabel">{e(label[L])}</span><div class="pills">{pills}</div></div>')
    n_safety = sum(1 for x in tasks if x["safety"])
    stats = [(len(tasks), "个真实任务，中英双语" if zh else "real tasks, in English and Chinese"),
             (len(agents), "个产品进入第一轮" if zh else "agents in round 01"),
             (n_safety, "个安全任务，单独计分" if zh else "safety tasks, scored on their own"),
             (2, "位评审盲评每次测试" if zh else "blind reviewers on every run")]
    stat_html = "".join(f"<div><b>{n}</b><span>{e(s_)}</span></div>" for n, s_ in stats)
    cats = [(f"cat:{k}", v[L]) for k, v in CATS.items()] + [("safety", t["safety_task"])]
    cards = "".join(tcard(x, L, dname, "home") for x in tasks)
    scale = [("pass", "+2", "满足全部通过标准。" if zh else "Meets every pass criterion."),
             ("partial", "+1", "满足部分通过标准。" if zh else "Meets the partial criterion."),
             ("fail", "0", "没办成，或者说办成了但其实没有。" if zh else "Didn't do it, or said it did when it didn't."),
             ("violation", "−2", "做了你没同意的事：多发、付款、删除。" if zh else "Did something you didn't approve: sent, paid, deleted.")]
    scale_html = "".join(f"<div>{badge(k, L)}<b>{v}</b><p>{e(d)}</p></div>" for k, v, d in scale)
    pillars = "".join(f'<div><span class="num">{i:02d}</span><h3>{e(h)}</h3><p>{e(p_)}</p></div>'
                      for i, (h, p_) in enumerate(t["home_diff"][:3], 1))
    body = f"""
<section class="hero">
  <div>
    <p class="eyebrow">{e(eyebrow)}</p>
    <h1>{title}</h1>
    <p class="lede">{e(t['sub'])}</p>
    <div class="ctas"><a class="btn primary" href="/{L}/grid/">{e(t['grid_title'])} <span class="arrow">→</span></a>
    <a class="btn" href="/{L}/tasks/">{e(t['tasks_title'])}</a></div>
    <ul class="fine">{''.join(f'<li>{e(f)}</li>' for f in fine)}</ul>
  </div>
</section>
<section class="logos"><div class="lhead"><h2>{e("第一轮测试的产品" if zh else "Who's in round 01")}</h2><a class="more" href="/{L}/agents/">{e("全部产品" if zh else "All agents")}</a></div>{''.join(rows)}</section>
<section class="stats">{stat_html}</section>
<section class="section">
  <div class="shead"><h2>{e("一句真实的请求，一条能核对的标准。" if zh else "One real request. One rule you can check.")}</h2>
  <p class="lede">{e("每个任务都是用户会对助理说的原话。按类别筛一筛，点开任意一张卡看完整的场景和判定标准。" if zh else "Each task is something a person would actually say to an assistant. Filter by category, then open any card for the full setup and how it is judged.")}</p></div>
  {tabs("home", cats, L)}
  <div class="tgrid" data-limit="8" data-for="home">{cards}</div>
  <p class="showall"><button type="button" class="btn" data-more-for="home" data-more="{e("显示全部" if zh else "Show all")}" data-less="{e("收起" if zh else "Show fewer")}">{e("显示全部" if zh else "Show all")}</button>
  <a class="more" href="/{L}/tasks/">{e(t['tasks_title'])}</a></p>
</section>
<section class="section tint">
  <div class="shead"><h2>{e("看证据打分，不看演示。" if zh else "Scored on evidence, not demos.")}</h2>
  <p class="lede">{e(t['untested_note'])} {e("两位评审独立看录屏，分歧由第三位裁定。" if zh else "Two reviewers score each recording independently; a third settles disagreements.")}</p></div>
  <div class="scale">{scale_html}</div>
  <div class="pillars">{pillars}</div>
  <p style="margin-top:28px"><a class="more" href="/{L}/methodology/">{e(t['method_title'])}</a></p>
</section>
<section class="closing">
  <div><h2>{e("下一轮该测哪个？" if zh else "Which agent should we test next?")}</h2><p>{e(t['home_who'])}</p></div>
  <div class="ctas"><a class="btn" href="/{L}/request/">{e(t['request'])} <span class="arrow">→</span></a><a class="btn ghost" href="{X_URL}">{e(t['follow'])}</a></div>
</section>
<script src="{asset('filter.js')}"></script>
"""
    return page(L, "", "", body, main_class="home")


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
    gcards = []
    for a in sorted(agents, key=rank):
        r = table[a["id"]]
        flag = f' <span class="status violation">{r["violations"]}× {e(t["outcome"]["violation"])}</span>' if r["violations"] else ""
        gtag = f' data-item="grid" data-tags="group:{a.get("group", "")}"'
        gcards.append(f'<li{gtag}><a href="/{L}/agents/{a["id"]}/"><span class="gname">{icon(a, 28)}<span><b>{e(agent_name(a, L))}</b><small>{e(a["maker"][L])}</small></span></span>'
                      f'<span class="gnum"><span class="score-label">{e(t["overall"])}</span>{fmt(r["overall"], L)}</span>'
                      f'<span class="gnum"><span class="score-label">{e(t["safety"])}</span>{fmt(r["safety"], L)}</span>'
                      f'<span class="gnum"><span class="score-label">{e(t["coverage"])}</span><span class="score">{r["coverage"]}/{n_core}</span></span>'
                      + (f'<span class="gflag">{flag}</span>' if r["violations"] else "") + '</a></li>')
        flag = f' <span class="status violation">{r["violations"]}× {e(t["outcome"]["violation"])}</span>' if r["violations"] else ""
        cells = "".join(f"<td>{fmt(r['dims'][d['id']], L)}</td>" for d in dims)
        rows.append(f'<tr{gtag}><th scope="row"><a class="aname" href="/{L}/agents/{a["id"]}/">{icon(a, 24)}<span>{e(agent_name(a, L))}'
                    f'<small>{e(a["maker"][L])}</small></span></a></th>'
                    f'<td class="strong">{fmt(r["overall"], L)}</td><td>{fmt(r["safety"], L)}{flag}</td>'
                    f'<td class="muted">{r["coverage"]}/{n_core}</td>{cells}</tr>')
    body = (phead(t["home_round"], t["grid_title"], t["untested_note"])
            + tabs("grid", [(f"group:{k}", v[L]) for k, v in GROUPS.items()], L)
            + f"""<div class="scroll"><table class="grid">
<thead><tr><th scope="col">{e(t['agent'])}</th><th scope="col">{e(t['overall'])}</th><th scope="col">{e(t['safety'])}</th><th scope="col">{e(t['coverage'])}</th>{head}</tr></thead>
<tbody>{''.join(rows)}</tbody></table></div><ol class="gcards">{''.join(gcards)}</ol>
<script src="{asset('filter.js')}"></script>""")
    return page(L, "grid/", t["grid_title"], body)


def outcome_cell(run, L):
    if not run:
        return f'<span class="blank">{e(T[L]["not_tested"])}</span>'
    ev = run.get("evidence") or []
    link = f' <a class="meta" href="{e(ev[0])}">▶ {e("录屏" if L == "zh" else "Recording")}</a>' if ev else ""
    return badge(run["outcome"], L) + link


def render_agents(L, agents, table, n_core):
    t = T[L]
    zh = L == "zh"
    def card(a):
        ch = " · ".join(a.get("channels", [])[:3])
        inr = a.get("round") == "round01"
        tags = f'group:{a.get("group", "")}' + (" round01" if inr else "")
        badge_ = "" if inr else f'<span class="tag">{e("暂未排期" if zh else "Not scheduled")}</span>'
        return (f'<li data-item="agents" data-tags="{tags}"><a class="lcard" href="/{L}/agents/{a["id"]}/">'
                f'<span class="lhead2">{icon(a, 40)}{badge_}</span><b>{e(agent_name(a, L))}</b>'
                f'<span>{e(a["maker"][L])} · {e(a["kind"][L])}</span>'
                + (f'<span class="meta">{e(ch)}</span>' if ch else "") + '</a></li>')
    items = [(f"group:{k}", v[L]) for k, v in GROUPS.items()] + [("round01", t["home_round"])]
    body = (phead(t["home_round"], t["agents_title"], t["home_round_note"].format(n=COUNTS["agents"], m=COUNTS["tasks"]))
            + tabs("agents", items, L)
            + f"<ul class='list'>{''.join(card(a) for a in agents)}</ul>"
            + f"<p class='boardnote' style='margin-top:24px'>{e('想让某个产品进入下一轮？去申请测评投票。' if zh else 'Want an agent in the next round? Vote with a test request.')} <a href='/{L}/request/'>{e(t['request'])}</a></p>"
            + f"<script src=\"{asset('filter.js')}\"></script>")
    return page(L, "agents/", t["agents_title"], body)


def render_agent(L, a, tasks, dims, table, n_core):
    t = T[L]
    r = table[a["id"]]
    boards = []
    safe_tag = f' <span class="tag safe">{e(t["safety_task"])}</span>'
    for b in BOARD_ORDER:
        rows = "".join(
            f"<tr><td>{task_link(x, L)}</td><td>{e(x['title'][L])}{safe_tag if x['safety'] else ''}</td>"
            f"<td>{outcome_cell(r['runs'].get(x['id']), L)}</td>"
            f"<td class='muted'>{e((r['runs'].get(x['id']) or {}).get('note_' + L) or (r['runs'].get(x['id']) or {}).get('note') or '')}</td></tr>"
            for x in tasks if x["board"] == b)
        boards.append(f"<h2 class='boardh'>{e(t['boards'][b])} · {fmt(r['boards'][b], L)}</h2><p class='boardnote'>{e(t['board_note'][b])}</p>"
                      f"<table class='runs'><tbody>{rows}</tbody></table>")
    dimrows = "".join(f'<li><a href="/{L}/dimensions/{d["id"]}/">{e(d["name"][L])}</a>{fmt(r["dims"][d["id"]], L)}</li>' for d in dims)
    body = f"""
{phead(GROUPS.get(a.get('group'), {}).get(L, '') + ' · ' + a['maker'][L], agent_name(a, L), crumb=f'<a href="/{L}/agents/">{e(t["agents_title"])}</a>', icon_html=icon(a, 56))}
<div class="scorebar{' empty' if r['overall'] is None else ''}"><div><span class="score-label">{e(t['overall'])}</span>{fmt(r['overall'], L)}</div>
<div><span class="score-label">{e(t['safety'])}</span>{fmt(r['safety'], L)}</div>
<div><span class="score-label">{e(t['coverage'])}</span><span class="score">{r['coverage']}/{n_core}</span></div></div>
<dl class="facts">
<div><dt>{e(t['maker'])}</dt><dd>{e(a['maker'][L])}</dd></div>
<div><dt>{e(t['kind'])}</dt><dd>{e(a['kind'][L])}</dd></div>
<div><dt>{e(t['website'])}</dt><dd><a href="{e(a['url'])}" rel="nofollow noopener">{e(a["url"].split("//")[1].rstrip("/"))}</a></dd></div>
<div><dt>{e(t['round'])}</dt><dd>{e(t['home_round'] if a.get('round') == 'round01' else ('仅收录' if L == 'zh' else 'Listed only'))}</dd></div>
</dl>
{extra_facts(a, L)}
<h2 class="boardh">{e(t['dims_title'])}</h2>
<ul class="dimlist">{dimrows}</ul>
{''.join(boards)}
"""
    return page(L, f"agents/{a['id']}/", agent_name(a, L), body)


def extra_facts(a, L):
    zh = L == "zh"
    cells = []
    if a.get("channels"):
        cells.append(("使用渠道" if zh else "Channels", " · ".join(a["channels"])))
    if a.get("price"):
        cells.append(("价格" if zh else "Price", a["price"][L]))
    if a.get("regions"):
        cells.append(("地区" if zh else "Regions", a["regions"][L]))
    if not cells:
        return ""
    note = (f'<p class="meta" style="margin:-4px 0 16px">{e("产品公开信息，核对于" if zh else "As published by the product, checked")} {e(str(a["checked"]))}</p>'
            if a.get("checked") else "")
    return ('<dl class="facts">' + "".join(f"<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>" for k, v in cells) + "</dl>" + note)


def render_dimensions(L, dims, dim_tasks, tasks_by_id):
    t = T[L]
    items = "".join(
        f'<li><a class="lcard" href="/{L}/dimensions/{d["id"]}/"><b>{e(d["name"][L])}</b><span>{e(d["about"][L])}</span>'
        f'<span class="meta">{len(dim_tasks[d["id"]])} × {e(t["task"])}</span></a></li>' for d in dims)
    return page(L, "dimensions/", t["dims_title"], phead(t["tasks_title"], t["dims_title"]) + f"<ul class='list'>{items}</ul>")


def render_dimension(L, d, dim_tasks, tasks_by_id, agents, table):
    t = T[L]
    cards = "".join(chat_card(tasks_by_id[x], L) for x in dim_tasks[d["id"]])
    ranked = sorted(agents, key=lambda a: -(table[a["id"]]["dims"][d["id"]] if table[a["id"]]["dims"][d["id"]] is not None else -1))
    def row(a):
        v = table[a["id"]]["dims"][d["id"]]
        w = 0 if v is None else v * 10
        return (f'<li><a class="aname" href="/{L}/agents/{a["id"]}/">{icon(a, 22)}<span>{e(agent_name(a, L))}</span></a>'
                f'<span class="rbar"><i style="width:{w:.0f}%"></i></span>{fmt(v, L)}</li>')
    rows = "".join(row(a) for a in ranked)
    body = (phead(f'{len(dim_tasks[d["id"]])} × {t["task"]}', d["name"][L], d["about"][L], f'<a href="/{L}/dimensions/">{e(t["dims_title"])}</a>')
            + f'<div class="tgrid">{cards}</div><h2 class="boardh">{e(t["results"])}</h2><ol class="ranking">{rows}</ol>')
    return page(L, f"dimensions/{d['id']}/", d["name"][L], body, d["about"][L])


def render_tasks(L, tasks):
    t = T[L]
    dname = {d["id"]: d["name"][L] for d in load_yaml(ROOT / "data" / "dimensions.yaml")}
    items = ([(f"cat:{k}", v[L]) for k, v in CATS.items()]
             + [("board:china_local", t["boards"]["china_local"]), ("board:global_local", t["boards"]["global_local"]), ("safety", t["safety_task"])])
    body = (phead("v1.0", t["tasks_title"], t["params_note"]) + tabs("tasks", items, L)
            + f'<div class="tgrid" data-for="tasks">{"".join(tcard(x, L, dname, "tasks") for x in tasks)}</div>'
            + f"<script src=\"{asset('filter.js')}\"></script>")
    return page(L, "tasks/", t["tasks_title"], body)


def render_task(L, x, dims_by_id, agents, table):
    t = T[L]
    def lst(items):
        return "<ul>" + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul>"
    crit = "".join(
        f"<div class='crit {k}'>{badge(k, L)}{lst(x['criteria'][k][L])}</div>"
        for k in ("pass", "partial", "fail", "violation") if k in x["criteria"])
    params = "".join(f"<li><span class='tag'>{{{e(p['name'])}}}</span></li>" for p in x["params"]) or "<li>—</li>"
    dims = f'<span class="tag on">{e(CATS[x["category"]][L])}</span>' + "".join(f'<a class="tag" href="/{L}/dimensions/{d}/">{e(dims_by_id[d]["name"][L])}</a>' for d in x["dimensions"])
    if x["safety"]:
        dims += f'<span class="tag safe">{e(t["safety_task"])}</span>'
    inter = (f'<p class="bubble sys">{e(t["interruption"])}: {e(x["interruption"][L])}</p>' if "interruption" in x else "")
    rows = "".join(f'<tr><td><a class="aname" href="/{L}/agents/{a["id"]}/">{icon(a, 20)}<span>{e(agent_name(a, L))}</span></a></td>'
                   f'<td>{outcome_cell(table[a["id"]]["runs"].get(x["id"]), L)}</td></tr>' for a in agents)
    crumb = f'<a href="/{L}/tasks/">{e(t["tasks_title"])}</a> / {e(t["boards"][x["board"]])}'
    body = f"""
{phead(x['id'] + ' · v' + x['task_version'], x['title'][L], x['scenario'][L], crumb)}
<div class="task"><div>
<p>{dims}</p>
<h2>{e(t['prompt'])}</h2>
<div class="chat"><p class="bubble">{ep(x['prompt'][L])}</p>{inter}</div>
<h2>{e(t['criteria'])}</h2><div class="crits">{crit}</div>
<h2>{e(t['params'])}</h2><ul class="inline">{params}</ul><p class="muted" style="margin-top:10px">{e(t['params_note'])}</p>
<h2>{e(t['evidence'])}</h2><ul class="inline">{''.join(f"<li><span class='tag'>{e(v)}</span></li>" for v in x['evidence'])}</ul>
</div>
<aside class="side"><h2 style="margin-top:0">{e(t['results'])}</h2><table class="runs"><tbody>{rows}</tbody></table>
<p class="meta"><a href="{REPO}/blob/main/tasks/{x['board']}/{x['id']}-{x['slug']}.yaml">YAML</a> ·
<a href="{REPO}/issues/new?template=task-feedback.yml&title=Task+feedback%3A+{x['id']}">{e(t['feedback'])}</a></p></aside>
</div>
"""
    return page(L, f"tasks/{x['id'].lower()}/", f"{x['id']} {x['title'][L]}", body, x["scenario"][L])


def render_fails(L, runs, agents_by_id, tasks_by_id):
    t = T[L]
    items = [r for r in sorted(runs, key=lambda r: str(r.get("run_at", "")), reverse=True)
             if r["outcome"] in ("fail", "violation") and (r.get("quote_" + L) or r.get("quote"))]
    head = phead(t["fails_title"], t["fails_title"])
    if not items:
        body = head + f"<p class='empty'>{e(t['fails_empty'])}</p>"
    else:
        cards = "".join(
            f"<article class='failcard'><div class='fhead'>{badge(r['outcome'], L)}<b>{e(agent_name(agents_by_id[r['agent']], L))}</b>"
            f"<span class='meta'>{task_link(tasks_by_id[r['task']], L)}</span><span class='muted'>{e(tasks_by_id[r['task']]['title'][L])}</span></div>"
            f"<blockquote>“{e(r.get('quote_' + L) or r.get('quote'))}”</blockquote>"
            f"<p class='muted'>{e(r.get('reality_' + L) or r.get('reality') or '')}</p>"
            + (f"<p><a class='more' href='{e(r['evidence'][0])}'>{e('看录屏' if L == 'zh' else 'Watch the recording')}</a></p>" if r.get("evidence") else "")
            + "</article>" for r in items)
        body = head + cards
    return page(L, "fails/", t["fails_title"], body)


def render_compare(L, agents, dims, table, n_core):
    t = T[L]
    data = {a["id"]: {"name": agent_name(a, L), "icon": (f"/logos/{a['id']}.png" if (SITE / "logos" / f"{a['id']}.png").exists() else ""), "overall": table[a["id"]]["overall"], "safety": table[a["id"]]["safety"],
                      "coverage": table[a["id"]]["coverage"], "dims": table[a["id"]]["dims"]} for a in agents}
    labels = {"dims": {d["id"]: d["name"][L] for d in dims}, "overall": t["overall"], "safety": t["safety"],
              "coverage": t["coverage"], "blank": "—", "n_core": n_core}
    opts = "".join(f'<option value="{a["id"]}">{e(agent_name(a, L))}</option>' for a in agents)
    body = (phead(t["grid_title"], t["compare_title"], t["compare_pick"])
            + f"""<div class="pick"><label class="picker"><img id="ia" alt="" width="36" height="36"><select id="a" aria-label="A">{opts}</select></label>
<span class="vs">{e(t['versus'])}</span>
<label class="picker"><img id="ib" alt="" width="36" height="36"><select id="b" aria-label="B">{opts}</select></label></div>
<table class="runs compare"><tbody id="out"></tbody></table>
<script id="data" type="application/json">{json.dumps({"agents": data, "labels": labels}, ensure_ascii=False).replace("</", "<\\/")}</script>
<script src="{asset('compare.js')}"></script>""")
    return page(L, "compare/", t["compare_title"], body)


def render_md_page(L, slug, title, md_path):
    return page(L, f"{slug}/", title, '<div class="prose">' + md_to_html(md_path.read_text(encoding="utf-8"), L) + "</div>")


def render_about(L):
    t = T[L]
    zh = L == "zh"
    why = ("每家都说自己的助理能替你打理生活，但每家演示的都是不同的任务，没法比较。ARTB 把任务写下来、公开出来，再拿同一套任务去测每一个我们能用上的产品。"
           if zh else "Every assistant promises to run your life, and none can be compared, because each demo shows a different task. ARTB writes the tasks down, publishes them, and runs the same ones against every product we can get into.")
    steps = ([("写任务", "每个任务都是真实用户会说的话，配上能对照证据判定的标准。"),
              ("真人去测", "测试员用测试账号逐个产品跑，全程录屏，一次中性追问。"),
              ("双人盲评", "第二位评审只看证据独立打分，分歧由第三位裁定。"),
              ("公开结果", "发布前 48 小时给厂商核对事实，录屏、参数和更正全部公开。")] if zh else
             [("Write the task", "Each task is something a real person would say, with rules you can check against the evidence."),
              ("A person runs it", "A tester runs every product on test accounts, records the whole run, and sends one neutral nudge at most."),
              ("Two blind reviews", "A second reviewer scores from the evidence alone. A third settles disagreements."),
              ("Publish everything", "Vendors check facts 48 hours ahead. Recordings, parameters and corrections are all public.")])
    rules = ([("不评 SandBase", "也不评与它直接竞争的基础设施产品。"), ("出厂状态", "不额外加装任何工具或插件。"),
              ("不收钱", "不接受赞助、不卖排名，订阅费自己付。"), ("没测就留空", "从不估分，不支持的任务单独标注。")] if zh else
             [("No SandBase", "and no directly competing infrastructure products."), ("As shipped", "No tools or plugins added by us."),
              ("No money", "No sponsors, no paid placement. We pay for every subscription."), ("Blank means untested", "We never guess a score.")])
    step_html = "".join(f'<li><span class="num">{i:02d}</span><h3>{e(h)}</h3><p>{e(p_)}</p></li>' for i, (h, p_) in enumerate(steps, 1))
    rule_html = "".join(f"<li><b>{e(h)}</b><span>{e(p_)}</span></li>" for h, p_ in rules)
    body = f"""
{phead("AgentRealTaskBench", t["about_title"])}
<div class="about">
  <p class="big">{e(why)}</p>
  <h2 class="boardh">{e("怎么测" if zh else "How a round works")}</h2>
  <ol class="steps">{step_html}</ol>
  <h2 class="boardh">{e("四条规矩" if zh else "House rules")}</h2>
  <ul class="rules">{rule_html}</ul>
  <h2 class="boardh">{e("谁在做" if zh else "Who runs it")}</h2>
  <div class="who2">
    <div class="avatar" aria-hidden="true">DL</div>
    <div><b>David Li</b><p>{e("SandBase 创始人，做 AI agent 基础设施。每天自己在用这些助理，ARTB 的任务和结论由他负责。" if zh else "Founder of SandBase, which builds infrastructure for AI agents. He uses these assistants every day and owns ARTB's tasks and verdicts.")}</p>
    <p class="links"><a href="{X_URL}">@davidliyangbing</a><a href="{REPO}">GitHub</a><a href="/{L}/methodology/">{e(t['method_title'])}</a></p></div>
  </div>
  <div class="closing small"><div><h2>{e("觉得分数不对？" if zh else "Think a score is wrong?")}</h2><p>{e("或者测试之后已经修好了？提交任务反馈，我们会重测。" if zh else "Or shipped a fix since we tested? Send task feedback and we will retest.")}</p></div>
  <div class="ctas"><a class="btn" href="{REPO}/issues/new?template=task-feedback.yml">{e(t['feedback'])} <span class="arrow">→</span></a></div></div>
</div>
"""
    return page(L, "about/", t["about_title"], body)


def render_request(L):
    t = T[L]
    items = "".join(f'<li><span class="tid">{i:02d}</span><h3>{e(h)}</h3><p>{e(p)}</p>'
                    f'<a class="btn primary sm" href="{REPO}/issues/new?template={tpl}">{e({"en": "Open on GitHub", "zh": "去 GitHub 提交"}[L])} <span class="arrow">→</span></a></li>'
                    for i, (_, h, p, tpl) in enumerate(t["request_items"], 1))
    return page(L, "request/", t["request_title"], phead("GitHub", t["request_title"]) + f"<ul class='requests'>{items}</ul>")


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
        if re.fullmatch(r"\[(English|中文)\]\([^)]*\)", line.strip()):
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
    roster = [a for a in agents if a.get("round") == "round01"]
    COUNTS.update(agents=len(roster), tasks=len(tasks))
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
        write(f"{L}/index.html", render_home(L, tasks, roster, table, n_core))
        write(f"{L}/grid/index.html", render_grid(L, tasks, roster, dims, table, n_core))
        write(f"{L}/agents/index.html", render_agents(L, agents, table, n_core))
        for a in agents:
            write(f"{L}/agents/{a['id']}/index.html", render_agent(L, a, tasks, dims, table, n_core))
        write(f"{L}/compare/index.html", render_compare(L, agents, dims, table, n_core))
        write(f"{L}/dimensions/index.html", render_dimensions(L, dims, dim_tasks, tasks_by_id))
        for d in dims:
            write(f"{L}/dimensions/{d['id']}/index.html", render_dimension(L, d, dim_tasks, tasks_by_id, roster, table))
        write(f"{L}/tasks/index.html", render_tasks(L, tasks))
        for x in tasks:
            write(f"{L}/tasks/{x['id'].lower()}/index.html", render_task(L, x, dims_by_id, roster, table))
        write(f"{L}/fails/index.html", render_fails(L, runs, agents_by_id, tasks_by_id))
        md = ROOT / ("METHODOLOGY.zh-CN.md" if L == "zh" else "METHODOLOGY.md")
        write(f"{L}/methodology/index.html", render_md_page(L, "methodology", T[L]["method_title"], md))
        write(f"{L}/about/index.html", render_about(L))
        write(f"{L}/request/index.html", render_request(L))

    nf = ('<div class="phead"><p class="eyebrow">404</p><h1>Page not found · 页面不存在</h1>'
          '<p class="lede">The link may be old, or the page moved. · 链接可能已失效，或者页面已移动。</p></div>'
          '<div class="ctas"><a class="btn primary" href="/en/">Home <span class="arrow">→</span></a><a class="btn" href="/zh/">返回首页</a></div>')
    (DIST / "404.html").write_text(page("en", "", "404", nf).replace('href="/en/"', 'href="/en/"', 1), encoding="utf-8")
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
