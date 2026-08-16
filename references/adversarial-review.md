# 对抗审稿工作流（Adversarial Review Loop）

对应 research-cycle 的 D4.5 对抗审稿：在 Draft 完成、机器六扫通过之后，
进入**多角色对抗审稿 → 修改 → 再审**循环，直到没有 Critical/Major 问题。
理念来自 Modex 的 Auto-Review Loop，但按 TMLR 评审尺度落地：审稿人只问
"证据能不能支撑声明"，不问"文笔好不好"。

## 为什么需要对抗审稿

机器六扫（数字一致性/统计一致性/写作风格/TMLR 合规/账本验证/证据污染）查的是**可验证的硬事实**。
对抗审稿查的是**论证强度**：方法有没有逻辑漏洞、实验有没有被质疑的空间、
声明的 hedging 够不够、有没有审稿人一眼就看穿的薄弱点。两类检查互补，
六扫通过 ≠ 审稿人挑不出毛病。

## 审稿角色矩阵（每个角色是独立的攻击视角）

一次完整审稿轮启动全部角色；每个角色产出一张问题清单（按严重度排序）。

| 角色 | 攻击焦点 | 典型攻击问题 |
|---|---|---|
| R1 方法论审稿人 | 方法是否有逻辑漏洞/未定义情形；**方法描述与实现是否一致（Soundness 对码，G7）** | 假设何时不成立？超参怎么选的，有没有调参过拟合？消融能不能真正隔离变量？**正文方法描述与 evidence/scripts 实际代码是否逐一对得上？结果是 real 还是 fake？**（硬约束：评分 Soundness 前必须核对代码并显式判断 real/fake；未核对不得给 Soundness ≥6） |
| R2 统计审稿人 | 数字是否经得起重算与检验 | 多重比较校正了吗？效应量报了吗？CI 和显著性声明一致吗？样本量够吗？ |
| R3 实验审稿人 | 实验是否充分、对比是否公平 | 基线超参公平吗？是否只挑了对自己有利的数据集？方差/种子数足够吗？**六类失败模式检查（源自 ResearchClawBench 论文 §4，E158）**：① Experiment Design Mismatch（实验协议/处理/基线/验证与声明不符）② Evidence Mismatch（图/数字/结论与关键证据不符）③ Scientific Core Missing（核心机制/发现缺失）④ Goal Misalignment（解决了相关但不等价的问题）⑤ Reliability/Reporting Failure（无支撑声明/无效证据/报告失败）⑥ Execution Failure（未生成可用产物）——逐类过一遍，命中的即为 Major+ |
| R4 新颖性审稿人 | novelty 声明是否过度 | "首次/最优/不同于"有没有文献支撑？增量贡献是否被包装成范式贡献？ |
| R5 可复现审稿人 | 别人能不能照着重做 | 种子/环境/数据版本/脚本是否齐全？随机性说明了吗？训练配置内嵌并披露了吗？ |
| R6 写作审稿人 | 声明强度 vs 证据强度是否匹配 | 强断言有没有 hedged？摘要数字和正文一致吗？图表自明吗？ |
| R7 伦理审稿人 | TMLR 伦理/影响声明 | 需要 broader impact 吗？数据/人类受试者合规吗？COI 声明了吗？ |
| R8 图表审稿人 | 图表数值与正文/证据的一致性 | 表中 ECE/CI 与 e1.json 一致吗？统计标记与正文一致吗？轴/图例完整吗？（用 deepseek-eyes 把 PDF 图表页转结构化审阅卡，再核验——文本模型无眼睛，靠卡片） |

## 循环协议

### A1 启动

- 输入：Draft 完成的 manuscript + evidence package + CLAIM_LEDGER.md。
- 每个角色独立审稿（**互不通信**，避免群体思维——对应 scholar-evaluation 的独立评审原则）。

### A2 审稿（每个角色产出一份 REVIEW_R{n}_<角色>.md）

每条问题必须包含：

```
- ID: R{n}-R3-07
- 严重度: Critical / Major / Minor / Nit
- 位置: §3.2 或 Table 2
- 问题: （具体到可操作）
- 期望: 审稿人要看到什么才算解决
- 证据关联: 该问题对应的证据文件/字段，或"无证据可支撑"
```

严重度定义：
- **Critical**：证据无法支撑主要声明，或方法存在致命漏洞 → 论文不能以当前形态提交。
- **Major**：某个声明或实验环节有明显缺陷，需实质修改。
- **Minor**：不影响结论但需澄清/补充。
- **Nit**：措辞、格式、可读性。

### A3 回应（作者侧，写入 ROUND_R{n}）

逐条回应，三种处理方式之一：

1. **修复**：改稿/补实验/重算，说明改了什么。
2. **证据补齐**：已有证据能回应，补充引用/数字/说明。
3. **合理反驳**：说明为何不改（必须给出理由，不能无视）。

Critical/Major 只允许"修复"或"证据补齐"；Minor/Nit 可"合理反驳"。
每条回应必须留下痕迹（改了什么文件、加了哪条 ledger 条目），
否则再审稿人无法验证——这和 revision_round_report 的 CHG 表是同一张表。

### A4 再审（A2 的下一轮）

- 上轮所有 Critical/Major 必须关闭（修改后重跑六扫 + 账本验证）。
- 再审可以引入**新的审稿角色视角**（如增加一个"读者代表"角色），
  但**已关闭的问题不得复活**。
- 收敛判据：连续一轮无新 Critical/Major → 循环结束，进入 Phase 5 投稿合规。

## 跨模型互审（可选增强）

当前部署有多个模型（如 deepseek-v4-flash / deepseek-v4-pro）或可配置多个 provider。
跨模型互审的意义：不同模型的盲区不同，独立审稿减少单一模型的自洽偏差。

**可直接复用的脚本骨架**：见 [assets/adversarial_review.workflow.md](../assets/adversarial_review.workflow.md)
——含 7 角色 + 模型分配、结构化输出 schema、强制独立重算的 prompt、
汇总与收敛判据，来自三轮实战（Critical 11→3→0）。复制后替换路径与审稿焦点即可。

实现方式（使用 workflow 工具）：

```js
// 伪代码：每个角色一个 subagent，不同角色可指定不同 model
const roles = ['methodology', 'statistics', 'experiments', 'novelty', 'reproducibility', 'writing', 'ethics']
const reviews = await parallel(roles.map((role) => () =>
  agent(`你是 TMLR ${role} 审稿人。请对以下稿件做对抗性审稿，并用工具独立重算关键统计量...`, {
    label: role, schema: reviewSchema, model: role === 'statistics' ? 'deepseek-v4-pro' : 'deepseek-v4-flash'
  })
))
```

约束：
- 每个角色独立 prompt，只共享 manuscript + evidence 路径，不共享彼此的审稿意见。
- **审稿人必须独立用工具重算/重编译/arXiv API 实证**，不只信作者声明——这是
  抓到三元组矛盾、效应量错值、引文作者错误的关键（见 failure-modes FM-15/17/19）。
- 审稿输出必须是结构化 JSON（严重度/位置/问题/期望），便于汇总成 REVIEW_R{n}。
- 汇总由主 agent 完成：去重、按严重度排序、映射到 ROUND_R{n} 的回应表。
- 已声明的资源限制（如演示数据、缺真实基线）明确告知审稿人不要重复报。

## 收敛与产出

- 循环收敛后，交付：REVIEW_R{n}_*.md（各角色）+ 汇总审稿报告 + ROUND_R{n} 回应记录。
- 审稿报告进入 evidence_manifest 哈希入账（审稿本身是过程证据，不是论文证据）。
- 任何再审新增的 Critical/Major 修复，必须同步更新 CLAIM_LEDGER.md 并重跑六扫。

## 与现有技能的关系

- scholar-evaluation：提供四维评分 rubrics 与评审员一致性（ICC）——对抗审稿用它
  做最终量化自评（TMLR 加权分），两者先后用：先对抗审稿修问题，再用评分衡量达没达标。
- 机器六扫：对抗审稿每轮修改后必须重跑，作为回归门。
