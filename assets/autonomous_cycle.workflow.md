# 自主科研循环 Workflow（Sakana AI Scientist 式开放循环）

> 核心升级：从"一次 D0-D5 流程"到"结果→反馈→新假设"的**开放式循环**。
> 用法：复制 script/meta，替换路径。每个循环 = 一个完整 D0-D5 迭代，
> 循环间通过 ARCHIVE/ + HYPOTHESES.md 的 Killed/Switch log 传递知识。

## meta

```json
{
  "name": "autonomous-research-cycle",
  "description": "Open-ended autonomous research loop: literature -> hypothesis -> design -> experiment -> analysis -> writing -> review -> archive -> next hypothesis.",
  "phases": [
    { "title": "Iterate", "detail": "One full research cycle (D0-D5 + archive + reflect)." },
    { "title": "NextHypothesis", "detail": "Decide next hypothesis or terminate." }
  ]
}
```

## args

```json
{
  "paperDir": "<paper_dir>",
  "topic": "<topic>",
  "hypotheses": "<paper_dir>/HYPOTHESES.md",
  "archive": "F:\\deepseek\\ARCHIVE",
  "roundIndex": 1
}
```

## script（骨架）

```js
const { paperDir, topic, hypotheses, archive, roundIndex } = args

phase('Iterate')
// D0 文献（用 ARCHIVE 的 literature/ 加速）
await agent(`D0 文献综述（topic: ${topic}）。先读 ARCHIVE ${archive}/literature/ 已有笔记，
再补新检索，产出 ${paperDir}/LITERATURE_REVIEW.md。`, { label: `R${roundIndex}-D0`, phase: 'Iterate', model: 'deepseek-v4-pro' })

// D0.5 假设（读 HYPOTHESES 当前池，决定验证哪个或生成新候选）
await agent(`D0.5 假设决策。读 ${hypotheses}（含 Killed Ideas + Switch Log）：
1) 若池中有待验证候选 → 选最强一个（激活 contract）
2) 若池耗尽 → 生成新候选（Generator→Reflector）并更新 HYPOTHESES.md
产出：当前活跃假设。`, { label: `R${roundIndex}-D0.5`, phase: 'Iterate', model: 'deepseek-v4-pro' })

// D1-D3 设计+实验+分析
await agent(`D1-D3：按活跃假设设计实验（EXPERIMENT_PLAN: Claim Map + Run Order），
执行（真实训练/分析），产出 results/ + 更新 FINDINGS.md（Research 洞见）。`,
  { label: `R${roundIndex}-D1D3`, phase: 'Iterate', model: 'deepseek-v4-pro' })

// D4 写作 + D4.5 审稿
await agent(`D4-D4.5：写作（只从算好的值写）+ 对抗审稿（8 角色）。若发现新问题
→ 修复轮；收敛后进入归档。`, { label: `R${roundIndex}-D4`, phase: 'Iterate', model: 'deepseek-v4-pro' })

// 归档
await agent(`归档本轮资产到 ARCHIVE：实验配方/失败教训/文献笔记（见 archive.md 规范），
更新 ARCHIVE/README.md。`, { label: `R${roundIndex}-Archive`, phase: 'Iterate', model: 'deepseek-v4-flash' })

phase('NextHypothesis')
// 结果→反馈→新假设（Sakana 核心）
const decision = await agent(`科研进展评估。读 ${paperDir}/FINDINGS.md（本轮 Research 洞见）
与 ${hypotheses}：
1) 当前假设结果：支持 / 否决 / 部分支持？
2) 若否决 → 从 Killed Ideas 确认不重走，从池中选下一候选（更新 Switch Log）
3) 若支持 → 是否开启新方向（新候选）？还是收敛？
4) 终止条件检查：假设池耗尽 OR 审稿收敛 OR 用户确认
产出结构化决策。`, { label: `R${roundIndex}-Next`, phase: 'NextHypothesis', schema: {
  type: 'object',
  properties: {
    currentVerdict: { type: 'string', enum: ['supported', 'rejected', 'partial'] },
    nextHypothesis: { type: 'string' },
    terminate: { type: 'boolean' },
    reason: { type: 'string' },
  },
  required: ['currentVerdict', 'nextHypothesis', 'terminate', 'reason'],
  additionalProperties: false,
}, model: 'deepseek-v4-pro' })

return {
  round: roundIndex,
  ...decision,
  note: '若 !terminate：主 agent 以 roundIndex+1 重启循环；知识已存 HYPOTHESES + FINDINGS + ARCHIVE',
}
```

## 终止条件（硬编码，防失控）

1. 假设池耗尽（全部验证/否决）
2. 审稿连续 2 轮 0C/0M + 加权分达标
3. **用户确认终止**（AI 科学家"与人类携手"，保留人类决策点）
4. 轮次上限（默认 5）

## 人类检查点（借鉴 Modex schema：checkpoint_type）

工作流在以下**决策点**必须暂停等待人类确认（对应 Modex workflows 表的
enable_checkpoints + checkpoints 表）：

| 检查点 | 类型 | 时机 | 展示给用户 |
|---|---|---|---|
| 想法选择 | idea_select | D0.5 选定活跃假设后 | 候选池 + 推荐 + 风险 → 用户批准/换选 |
| 实验方案 | approve | D1 设计完成后 | Claim Map + Run Order + 预算 → 用户批准 |
| 关键反馈 | feedback | 审稿发现 Critical/Major 后 | 问题 + 修复选项 → 用户决定 |
| 收敛确认 | approve | 审稿 0C/0M 后 | 加权分 + 交付 → 用户确认终止 |

**机制**：每个检查点 = 状态（pending → resolved）+ 用户响应（JSON），
与 continuous-memory 的文件持久化结合（检查点状态写入
`<paperDir>/.agent-memory/` 或 ROUND 审计链）。

## 关键纪律

- **文件是真相**：每循环结束，知识必须落盘（HYPOTHESES/FINDINGS/ARCHIVE），
  新循环不依赖上下文（continuous-memory 协议精神）。
- **诚实降级**：n=3 等功效受限如实披露（FM-29），不伪装。
- **Killed Ideas 尊重**：否决的假设不重走（除非新证据）。
- **无证据不提升**：归档的教训必须有可重跑证据（continuous-memory LESSON 纪律）。
- **人类检查点不可绕过**：idea_select/approve 检查点必须等用户（Modex 设计——
  这是"与人类携手"的机制化，不是可选的礼貌）。
