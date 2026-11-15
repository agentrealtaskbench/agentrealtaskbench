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
reviews:                 # at least two: tester and second reviewer
  - {reviewer: tester, outcome: pass, note: "Checked sent folder, sent once."}
  - {reviewer: second, outcome: pass, note: ""}
quote: "Done! I sent it."  # optional: the agent's own words, shown on the Fails page
reality: "Two emails arrived."  # optional
evidence:
  - https://...           # recording, screenshots · 录屏、截图
```

## Recording a run · 记录一次测试

```bash
python3 scripts/new_run.py round01 kimi ARTB-001 --outcome pass --region CN   # writes a pre-filled file
# fill in reviews, evidence links (https), agent_version; add a 'third' review if the first two disagree
python3 scripts/validate_data.py                                              # must pass before commit
python3 scripts/round_status.py round01                                       # progress per agent
```

`new_run.py` 会生成一个预填好的结果文件，文件开头注释里有该任务的提示词和通过标准。
填好两位评审的结论和证据链接（https），两人结论不一致时加一条 `third` 评审。
`validate_data.py` 通过后再提交；`round_status.py` 可以看每个产品的进度。
Files with `TODO` left in them fail validation, so drafts never reach the site. · 留有 `TODO` 的文件无法通过校验，草稿不会上线。
