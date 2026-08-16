# Instruction Design for the Writing Agent(面向 agent 的指令五原则,O3)

> 来源: skills-main 的 writing-for-agents 技能
> (context pointer / 双预算 / completion criteria / leading word / 否定式禁令反效果)
> 用途: 审计 SKILL.md 与 research-writer 预设人物段里"给 agent 的指令",
> 每条指令应能回答"我怎么知道这一步做完了"。

## 五原则

### 1. Completion criteria(每条指令有可验证完成判据)
指令不只说"做什么",还要说"做成什么样算完成",且判据必须可检查
(文件存在/命令 exit 0/数字匹配/清单覆盖)。
- 反例: "检查数字一致性"(无判据);
- 正例: "Phase 3 完成 = 六扫全部 PASS(scan_number_consistency /
  scan_stats_consistency / check_writing_style / check_tmlr_compliance /
  verify_claim_ledger / verify_taint 均 exit 0),且 reports/ 六份报告无 FAIL"。

### 2. 正面表述(说目标行为,不说禁止清单)
纯否定式禁令(尤其"不要 X")容易被 LLM 当成"提一下就行";正面写目标行为,
配完成判据。
- 反例: "不要幻觉引用"(无判据、易被忽略);
- 正例: "每条引用必须能回溯到抓取原文/一手来源文件,且证据 manifest 可验证"
  (正面目标 + 可检查)。

### 3. Leading word(复用预训练词汇锚定行为)
用领域高频、语义精确的词开头(如"重算""独立重算""逐种子""只读验证"),
比新造术语更能锚定正确行为。

### 4. 双预算(context load / cognitive load)
指令别一次塞爆:上下文预算(每步加载量)与认知预算(单条指令的复杂度)
分开控制;复杂流程拆阶段,阶段内指令少而准。

### 5. Context pointer(指针措辞决定触发可靠性)
让 agent"什么时候该加载哪份指令"的关键是触发词与任务词汇对齐;
新技能/新流程的 description 里写清触发条件(agentskills 三段式加载的
discovery 阶段就是 name+description)。

## 审计清单(对本 agent 的既有指令)

对 SKILL.md 每个 Phase 与 preset 人物段逐条问:
1. 这条指令有可验证完成判据吗?(没有 → 补判据)
2. 是纯否定式表述吗?(是 → 改正面 + 判据;安全边界除外)
3. 开头用了领域高频锚定词吗?
4. 单条指令的认知负载可控吗?(过长 → 拆)
5. 触发条件(description/何时加载)与任务词汇对齐吗?

## Phase 级完成判据速查(落地结果)

| Phase | 完成判据(可检查) |
|---|---|
| Phase 0 收据 | evidence_manifest.json 已构建且 --verify 通过;WORKING_NOTES.md 存在 |
| Phase 1 claim ledger | verify_claim_ledger.py exit 0;UNRECONCILED 声明 = 0(DDD 后) |
| Phase 2 起草 | 摘要数字与 Results 重算一致;每条声明有 ledger 条目 |
| Phase 3 机器检查 | 六扫全部 exit 0,reports/ 无 FAIL |
| Phase 4 修改轮 | ROUND_Rn.md 有逐条记录;六扫重跑全绿;旧 gate 保持 PASS |
| Phase 4.5 对抗审稿 | 一轮无新 Critical/Major;双模型终评 agreement ≥ 阈值(stable) |
| Phase 5 交付 | G1-G11 全过;manifest 字节对账;zip 重哈希一致 |
