# AgentRealTaskBench

[中文](README.zh-CN.md)

**Can your AI agent actually get things done? We give agents real tasks from everyday life, record every run, and publish the results.**

AgentRealTaskBench (ARTB) is an open, human-run benchmark for personal AI agents and assistants, from both the US and China. Every task is written as something a real person would ask, every score links to a recording, and the whole task set lives in this repo.

## What's here

| Path | Contents |
|---|---|
| [`tasks/`](tasks/README.md) | The task set, one YAML file per task, English and Chinese |
| [`METHODOLOGY.md`](METHODOLOGY.md) | How we run tasks and score them |
| [`results/`](results/README.md) | Results per round (published after each round) |
| [`scripts/validate.py`](scripts/validate.py) | Validates task files and rebuilds the task index |

## Task set v1.0

30 tasks in three boards:

- **Core (20)**: every agent runs these. Scores are comparable across agents.
- **China local (5)**: 12306 trains, JD/Taobao/Pinduoduo prices, Xiaohongshu, WeChat/Feishu groups, parcel tracking.
- **Global local (5)**: Amazon/Walmart/Target prices, Reddit, Slack, US parcel tracking, hotels.

Tasks cover 16 dimensions (recommendations, online tasks, purchasing, privacy, email, integrations, memory, travel, phone calls, proactive behavior, routines, content creation, restraint, chained tasks, groups, personality) plus **data access**: whether the agent can actually read social, shopping and live data. Six core tasks are **safety tasks** and feed a separate safety score.

Prompt templates are public. The concrete values (cities, products, URLs, phone numbers) change every round and are published together with that round's results.

## Get involved

- **Want an agent tested?** [Open a test request](../../issues/new?template=test-request.yml).
- **Have a real-life task we should add?** [Submit a use case](../../issues/new?template=use-case.yml).
- **Think a task or criterion is unfair?** [Give task feedback](../../issues/new?template=task-feedback.yml).

## Who runs this

ARTB is run by David Li ([@davidliyangbing](https://x.com/davidliyangbing)), founder of SandBase, which builds infrastructure for AI agents. To keep the benchmark neutral:

- SandBase and directly competing infrastructure products are not evaluated.
- Agents are scored exactly as shipped, with no extra tools or plugins added by us.
- No sponsorships, no paid placement. We pay for every subscription we test.
- Vendors can check facts 48 hours before publication. Corrections are logged publicly.

## License

Task set and documentation: [CC BY 4.0](LICENSE). Scripts: MIT (see [LICENSE](LICENSE)).
