# Contributing · 参与贡献

- **Request a test / 测评请求**: open a *Test request* issue. We schedule by 👍 votes. · 提交 *测评请求* issue，按 👍 数排期。
- **Suggest a task / 投稿任务**: open a *Use case* issue. Good tasks are real, specific, and objectively checkable. · 提交 *使用场景* issue。好的任务要真实、具体、能客观核对。
- **Change a task / 修改任务**: open a pull request. Edit the YAML in `tasks/`, then run: · 提交 pull request，修改 `tasks/` 里的 YAML，然后运行：

  ```
  pip install pyyaml
  python3 scripts/validate.py
  ```

  Commit the regenerated `tasks/README.md`. CI runs `validate.py --check`. · 一起提交重新生成的 `tasks/README.md`，CI 会运行 `validate.py --check`。

## Writing a task · 怎么写任务

- Write the scenario as a real person would describe it, not as a capability test. · 场景按真实用户的口吻写，不要写成能力测试。
- Every placeholder in `prompt` must be listed in `params`, in both languages. · `prompt` 里的每个占位符都要在 `params` 里列出，中英都要有。
- `pass`, `partial` and `fail` must be checkable from the evidence without judgment calls where possible. · `pass`、`partial`、`fail` 尽量做到看证据就能判定，不靠主观判断。
- Safety tasks (`safety: true`) must define `violation`. · 安全任务（`safety: true`）必须写 `violation`。

If you work for a company whose product ARTB tests, please say so in your issue or PR. · 如果你任职于被 ARTB 测评的产品公司，请在 issue 或 PR 里说明。
