# AgentRealTaskBench

[English](README.md)

**你的 AI 助理真的能把事办成吗？我们用日常生活里的真实任务去测，每次测试都录屏，结果全部公开。**

AgentRealTaskBench（ARTB）是一个公开的、由真人执行的 personal agent / AI 助理评测，同时覆盖中国和海外产品。每个任务都按真实用户会说的话来写，每个分数都附录屏，完整任务集就放在这个仓库里。

## 仓库内容

| 路径 | 内容 |
|---|---|
| [`tasks/`](tasks/README.md) | 任务集，一个任务一个 YAML 文件，中英双语 |
| [`METHODOLOGY.zh-CN.md`](METHODOLOGY.zh-CN.md) | 怎么执行任务、怎么打分 |
| [`results/`](results/README.md) | 每一轮的结果（每轮结束后发布） |
| [`scripts/validate.py`](scripts/validate.py) | 校验任务文件，并重新生成任务索引 |

## 任务集 v1.0

共 30 个任务，分三个榜：

- **通用任务（20 个）**：所有 agent 都测，分数可以横向比较。
- **中国本地（5 个）**：12306 高铁、京东/淘宝/拼多多比价、小红书、微信/飞书群、快递查询。
- **海外本地（5 个）**：Amazon/Walmart/Target 比价、Reddit、Slack、美国快递查询、酒店。

任务覆盖 16 个维度：推荐质量、在线办事、购物、权限与隐私、邮件、第三方集成、记忆、出行、打电话、主动提醒、例行任务、内容创作、克制、多步任务、群聊、性格。另外加了一个**数据获取**维度，看 agent 能不能真正读到社媒、电商和实时数据。通用任务里有 6 个**安全任务**，单独计算安全分。

任务的提示词模板是公开的。具体参数（城市、商品、网址、电话号码）每一轮都会更换，并在该轮结果发布时一起公开。

## 参与方式

- **想让我们测某个 agent？** [提交测评请求](../../issues/new?template=test-request.yml)。
- **有值得加入的真实生活任务？** [提交使用场景](../../issues/new?template=use-case.yml)。
- **觉得某个任务或标准不公平？** [反馈任务问题](../../issues/new?template=task-feedback.yml)。

## 谁在维护

ARTB 由 David Li（[@davidliyangbing](https://x.com/davidliyangbing)）维护。他是 SandBase 的创始人，SandBase 做的是 AI agent 基础设施。为了保持中立：

- 不评测 SandBase，也不评测与它直接竞争的基础设施产品。
- 所有 agent 都按出厂状态测试，我们不额外加装任何工具或插件。
- 不接受赞助，不卖排名。所有被测产品的订阅费用都由我们自己支付。
- 厂商可以在发布前 48 小时核对事实，所有更正都公开记录。

## 许可

任务集和文档：[CC BY 4.0](LICENSE)。脚本：MIT（见 [LICENSE](LICENSE)）。
