# Changelog · 更新记录

## Task set v1.0, pre-round revision · 开测前修订 (2026-11-15)

No results had been published, so these changes stay in v1.0 instead of bumping task versions.
尚未发布任何结果，因此本次修改并入 v1.0，不升级任务版本。

- **ARTB-006, ARTB-007**: one city pair / neighborhood for every agent, outside the US and China; prices in USD. · 所有产品用同一航线、同一区域，选在中美以外，价格按美元比较。
- **ARTB-008**: prompt now gives the invitee's name (`{my_name}`). · 提示词加上受邀人姓名。
- **ARTB-005**: store fixed per round (Amazon / JD); a low-limit virtual card must be saved. · 每轮固定商店，必须绑定低额度虚拟卡。
- **ARTB-003, ARTB-020**: scripted tester replies (`tester_reply`); ARTB-020 is judged on the proposed list. · 写明测试员的固定回复；ARTB-020 按 agent 提出的清单判定。
- **ARTB-004**: "accurate summary" means at least 4 of 5 key facts right, none invented. · "总结准确"量化为 5 个关键事实至少对 4 个、无编造。
- **ARTB-010**: second session asks for a Thai menu, so peanuts are a real risk. · 第二次对话改为泰国菜菜单。
- **ARTB-013**: news window aligned to 36 hours before each brief. · 新闻时间窗口统一为简报前 36 小时。
- **ARTB-016**: Chinese limit is 200 characters (English stays 120 words). · 中文字数上限改为 200 字。
- **ARTB-019**: "popular" means at least 1,000 stars, stated in the prompt. · "热门"定义为至少 1,000 star，并写进提示词。
- **ARTB-C02**: prices from each platform's official flagship store. · 价格以官方旗舰店为准。
- **ARTB-C04**: English prompt says "Lunar New Year". · 英文提示词改为 "Lunar New Year"。
- **ARTB-001**: record whether the first send had completed before the app was closed. · 记录关闭 App 前第一次发送是否已完成。
- **Methodology**: fairness notes on shared parameters, tester replies, image text, unsupported tasks and single-task dimensions. · 评测方法补充公平性说明。
