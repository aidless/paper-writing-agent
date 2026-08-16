# 假设生成 Workflow 模板（Generator→Reflector→Ranker→Evolve，实战验证版）

> 来源：research-writer 迭代计划 Phase B 实战跑通的四角色循环
> （对校准主题生成 6 候选 → Reflector 全数批判 → Evolver 进化 H1-H3 → 复核）。
> 用法：复制 `script` 与 `meta`，替换 `args` 中的路径与主题。

## meta

```json
{
  "name": "hypothesis-generation",
  "description": "Run the Generate-Reflect-Rank-Evolve hypothesis loop (2 rounds) against the literature pool.",
  "phases": [{ "title": "Hypotheses", "detail": "4-role hypothesis loop." }]
}
```

## args

```json
{
  "litreview": "<paper_dir>/LITERATURE_REVIEW.md",
  "protocol": "<paper_dir>/evidence/protocol.md",
  "out": "<paper_dir>/HYPOTHESES.md",
  "topic": "<research topic>"
}
```

## script（骨架）

```js
const { litreview, protocol, out, topic } = args

const genSchema = {
  type: 'object',
  properties: {
    candidates: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          hypothesis: { type: 'string', description: '一句话可证伪陈述' },
          basis: { type: 'string', description: '依据：引 L## 或 arXiv ID' },
          experiment: { type: 'string', description: '验证实验设计' },
          expected: { type: 'string', description: '若不成立则如何' },
        },
        required: ['id', 'hypothesis', 'basis', 'experiment', 'expected'],
        additionalProperties: false,
      },
    },
  },
  required: ['candidates'],
  additionalProperties: false,
}

const reflectSchema = {
  type: 'object',
  properties: {
    reflections: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          counterEvidence: { type: 'string' },
          feasibility: { type: 'number' },
          novelty: { type: 'number' },
        },
        required: ['id', 'counterEvidence', 'feasibility', 'novelty'],
        additionalProperties: false,
      },
    },
  },
  required: ['reflections'],
  additionalProperties: false,
}

phase('Hypotheses')
const gen = await agent(`你是科研假设生成器（Generator）。基于文献综述的 GAP 陈述与基线池，
生成 6 个可证伪研究假设候选（主题：${topic}）。文献综述：${litreview}。协议：${protocol}。
硬规则：每个候选的 basis 必须引 L## 或 arXiv ID 可追溯；无依据候选标注 exploratory。输出 JSON。`,
  { label: 'Generator', phase: 'Hypotheses', schema: genSchema, model: 'deepseek-v4-pro' })

const candidates = (gen && gen.candidates) || []

const reflect = await agent(`你是对抗性反射器（Reflector）。对以下候选逐一找反例/文献矛盾/
可行性障碍（绝不温和）。候选：${JSON.stringify(candidates)}。文献综述：${litreview}。输出 JSON。`,
  { label: 'Reflector', phase: 'Hypotheses', schema: reflectSchema, model: 'deepseek-v4-pro' })

const reflections = (reflect && reflect.reflections) || []
const ranked = (reflections.length ? reflections : [])
  .sort((a, b) => (b.novelty + b.feasibility) - (a.novelty + a.feasibility))

const top = ranked.slice(0, 3).map(r => candidates.find(c => c.id === r.id)).filter(Boolean)
const evolve = await agent(`你是假设进化器（Evolver）。根据反射意见改进 top-3：
候选：${JSON.stringify(top)}。反射：${JSON.stringify(ranked)}。
每个假设给出修订版（应对反例、强化可证伪性、明确验证实验）。输出 JSON（结构同候选列表）。`,
  { label: 'Evolver', phase: 'Hypotheses', schema: genSchema, model: 'deepseek-v4-pro' })

const reflect2 = await agent(`你是对抗性反射器（Reflector）第二轮。复核进化后假设：
${JSON.stringify((evolve && evolve.candidates) || [])}。是否仍有致命缺陷？输出 JSON。`,
  { label: 'Reflector-R2', phase: 'Hypotheses', schema: reflectSchema, model: 'deepseek-v4-flash' })

return {
  round1Candidates: candidates.map(c => c.id),
  round1Reflections: ranked,
  round2Evolved: ((evolve && evolve.candidates) || []).map(c => ({ id: c.id, hypothesis: c.hypothesis })),
  round2Reflections: (reflect2 && reflect2.reflections) || [],
  adopted: ((evolve && evolve.candidates) || []).slice(0, 2).map(c => c.id),
  note: '完整 HYPOTHESES.md 由主 agent 依据此输出写入',
}
```

## 关键纪律（Phase B 实战教训）

1. **Reflector 必须诚实**：demo 实战中 Reflector 抓出了 synthetic 数据循环确证、
   TS 基线可疑、统计口径缺陷——这些正是"该做什么实验"的信号。假设生成循环的
   价值不在"生成"，在"批判"。
2. **预注册纪律**：Evolver 输出的确认性假设必须有功效分析/等价界/门控预注册，
   否则"成功区域为空"（H1 实战教训）。
3. **无依据候选标记 exploratory**：不得混入 evidence-based 池（FM-15 幻觉防护）。
4. **与 claim ledger 联动**：采纳假设最终成 C 类声明时溯源到 HYPOTHESES.md。
