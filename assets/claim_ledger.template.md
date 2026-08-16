# CLAIM_LEDGER.md

规则：
1. 每个声明（含摘要与结论）在起草前登记；修改轮新增声明必须补条目。
2. 每个数字必须可追溯到 evidence 文件 + 字段；无法追溯的声明删除或降级为 hedging。
3. 状态：draft / verified / inconclusive / blocked。
   - **inconclusive**：证据不足时的显式出口（SciAgentArena C5 模式）。声明可保留在正文，
     但必须满足：(a) 措辞 hedge（"可能/我们未观测到/尚不确定"）；(b) 在"如何验证"列写明
     命名失败模式（缺什么证据、什么条件下可升级为 verified）；(c) 评分鼓励诚实——
     证据不足给 inconclusive 优于编造数值。inconclusive 不阻塞投稿，但不得以强断言口吻出现。
   - blocked 的声明不得进入正文。
4. 每轮修改后更新本表并重新跑数字一致性扫描与验收门。

| ID | 声明（章节） | 证据文件+字段 | 数值 | 如何验证 | 状态 |
|---|---|---|---|---|---|
| C01 | 例：30 种子下 mean±sd 为 29.4±0.4% | results/e1.json -> gTV.mean / gTV.sd | 29.4 / 0.4 | 脚本重算 + 哈希对账 | template-example |
| C02 | 例：机制解释（证据不足） | — | — | 缺：消融实验；补 C03 消融后升级 verified | inconclusive |
| C03 | ... | ... | ... | ... | ... |

## 强断言登记（必须满足 TMLR 硬规则）

| 断言 | 证据支撑 | 是否在证据可证明范围内 | 结论 |
|---|---|---|---|
| 例：CNR 上界 2.94 | results/e2.json 重算 | 是（<= 2.94） | 保留 |
| 例：Conf-Gating 4.38 > 上界 | 无 | 否 | 删除/降级 |
| 例：因果解释（无干预实验） | 无 | 否（仅相关） | 降级 inconclusive + hedge |
