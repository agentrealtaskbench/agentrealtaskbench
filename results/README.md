# Results · 结果

No round has been published yet. The first round is in progress.
目前还没有发布任何一轮结果，第一轮正在进行中。

## Layout · 目录结构

```
results/
  2026-12/                  # one folder per round · 每轮一个目录
    agents.yaml             # agents, versions, plans, regions · 产品、版本、套餐、地区
    params.yaml             # parameter values used this round · 本轮使用的参数
    runs/<agent>/<task-id>.yaml
    CHANGELOG.md            # corrections · 更正记录
```

## Run file · 单次结果文件

```yaml
task: ARTB-001
task_version: "1.0"
agent: example-agent
agent_version: "2026-12-01 web"
language: en
region: US
run_at: 2026-12-03T15:04:00Z
outcome: pass            # pass | partial | fail | violation | unsupported
reviews:
  - {reviewer: tester, outcome: pass, note: "Checked sent folder, sent once."}
  - {reviewer: second, outcome: pass, note: ""}
evidence:
  - https://...           # recording, screenshots · 录屏、截图
```
