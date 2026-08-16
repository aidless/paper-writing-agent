# 全自动科研循环 Workflow 模板（Sakana AI Scientist 式编排）

> 用途：把 D0 文献 → D0.5 假设 → D1 设计 → D2 真实实验 → D3 分析 →
> D4 写作 → D4.5 对抗审稿 → D5 合规的完整循环编排为一个可重复的
> workflow 骨架。用法：复制 `script` 与 `meta`，替换路径与各阶段 agent 提示。
> 每个阶段是一个独立 agent 调用；阶段间通过 `args` 传递产物路径
> （不跨 agent 传对象，避免上下文污染）。

## meta（workflow 身份块）

```json
{
  "name": "research-cycle",
  "description": "Run the full D0-D5 research cycle as staged agents (literature -> hypothesis -> design -> experiment -> analysis -> writing -> review -> compliance).",
  "phases": [
    { "title": "Literature", "detail": "D0 literature survey to LITERATURE_REVIEW.md." },
    { "title": "Hypotheses", "detail": "D0.5 Generate-Reflect-Rank-Evolve to HYPOTHESES.md." },
    { "title": "Design", "detail": "D1 protocol.md + preregistration." },
    { "title": "Experiments", "detail": "D2 real training (train script + results)." },
    { "title": "Analysis", "detail": "D3 recompute statistics + reports." },
    { "title": "Writing", "detail": "D4 manuscript + ledger + manifest." },
    { "title": "Review", "detail": "D4.5 adversarial review (8 roles incl. figures)." },
    { "title": "Compliance", "detail": "D5 G1-G11 + hash reconciliation." }
  ]
}
```

## args（入参）

```json
{
  "paperDir": "<paper_dir>",
  "topic": "<research topic>",
  "question": "<falsifiable research question>"
}
```

## script（骨架）

```js
const { paperDir, topic, question } = args

phase('Literature')
await agent(`执行 D0 文献综述（topic: ${topic}）。按 skill references/literature-review.md
流程，用 literature_discovery.py + arXiv API 检索，产出 ${paperDir}/LITERATURE_REVIEW.md
（方法族表 + 可证伪 GAP + 基线池）。`, { label: 'D0-Literature', phase: 'Literature', model: 'deepseek-v4-pro' })

phase('Hypotheses')
await agent(`执行 D0.5 假设生成（question: ${question}）。按 skill references/hypothesis-generation.md
四角色循环，产出 ${paperDir}/HYPOTHESES.md。依据必须引文献池可追溯。`,
  { label: 'D0.5-Hypotheses', phase: 'Hypotheses', model: 'deepseek-v4-pro' })

phase('Design')
await agent(`执行 D1 实验设计。读取 ${paperDir}/HYPOTHESES.md，把采纳假设转成可执行设计：
protocol.md（配置/种子/检验/功效/排除标准）+ 预注册。载入 ablation-design / statistical-analysis /
registered-report 技能。`, { label: 'D1-Design', phase: 'Design', model: 'deepseek-v4-pro' })

phase('Experiments')
await agent(`执行 D2 真实实验。按 protocol.md 写 train 脚本（pytorch 技能），跑训练，
把原始逐种子结果存入 ${paperDir}/results/。环境冻结 + 种子管理（reproducibility 技能）。`,
  { label: 'D2-Experiments', phase: 'Experiments', model: 'deepseek-v4-pro' })

phase('Analysis')
await agent(`执行 D3 分析。写 analysis.py 从逐种子数据重算全部统计量（statistical-analysis /
model-evaluation / uncertainty-quantification 技能），产出 reports/。每个数字可重算。`,
  { label: 'D3-Analysis', phase: 'Analysis', model: 'deepseek-v4-pro' })

phase('Writing')
await agent(`执行 D4 写作。按 paper-writing-agent 技能 Phase 0-5：manifest → claim ledger →
草稿 → 六扫 → 门。${paperDir}/paper/main.tex + CLAIM_LEDGER.md + evidence_manifest.json。`,
  { label: 'D4-Writing', phase: 'Writing', model: 'deepseek-v4-pro' })

phase('Review')
await agent(`执行 D4.5 对抗审稿（8 角色含 R8 图表）。按 skill assets/adversarial_review.workflow.md
模式。收敛标准：一轮无新 Critical/Major。`, { label: 'D4.5-Review', phase: 'Review', model: 'deepseek-v4-pro' })

phase('Compliance')
await agent(`执行 D5 合规。G1-G11 全过 + build_evidence_manifest --verify 0 WARN +
加权分终评（scholar-evaluation）。`, { label: 'D5-Compliance', phase: 'Compliance', model: 'deepseek-v4-pro' })

return { note: 'full cycle dispatched; each stage agent reports its own output path', paperDir }
```

## 关键纪律（Sakana 式归档）

- **知识归档**：每轮失败教训/实验结果/文献笔记沉淀到 `${paperDir}/ARCHIVE/`，
  跨论文复用（超越单论文轮次报告）。
- **阶段门控**：上一阶段出口标准未达成不进入下一阶段（research-cycle.md 的表格）。
- **计算预算**：D2 训练脚本必须内嵌配置并支持 --seeds 缩减 + 诚实披露（FM-29）。
