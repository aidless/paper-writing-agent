# 对抗审稿 Workflow 模板（跨模型互审，实战验证版）

> 来源：research-writer 演示论文 R1-R3 三轮对抗审稿实际跑通的脚本骨架
> （Critical 11 → 3 → 0），后续轮次（R4-R23）持续强化。用法：复制本文件的
> `script` 与 `meta`，替换 `args` 中的文件路径与 `roles` 的角色模型分配，
> 填入 `basePrompt` 的审稿焦点。

## meta（workflow 身份块）

```json
{
  "name": "tmlr-adversarial-review",
  "description": "Run 8 independent TMLR reviewer roles against the manuscript (7 text roles + R8 figure role via deepseek-eyes), each producing structured findings.",
  "phases": [{ "title": "Review", "detail": "8 independent reviewer roles attack the manuscript." }]
}
```

## args（入参，由调用者替换路径）

```json
{
  "manuscript": "<paper_dir>/paper/main.tex",
  "evidence": "<paper_dir>/results",
  "ledger": "<paper_dir>/CLAIM_LEDGER.md",
  "litreview": "<paper_dir>/LITERATURE_REVIEW.md",
  "protocol": "<paper_dir>/evidence/protocol.md",
  "roundPrev": "<paper_dir>/REVIEW_R{n-1}_summary.md",
  "pdf": "<paper_dir>/paper/main.pdf"
}
```

## roles（8 角色 + 模型分配）

> **N7/E054：模型路由配置化**——默认分配见下；要防自偏好（judge 与被测同源是
> 最强偏置源），把 methodology/statistics 换成异源模型。统一配置在
> `assets/review_models.yaml`，运行 workflow 前从该文件读取 role→model 映射
> （读取失败回退下表默认）。换模型后必须重跑 judge 校准（check_judge_calibration.py）。

| 角色 | 模型 | 审稿焦点 |
|---|---|---|
| methodology | pro（可配异源） | 方法定义、逻辑漏洞、术语统一、**Soundness 对码（G7）** |
| statistics | pro（可配异源） | W/p/r 自洽、CI/效应量口径、多重比较 |
| experiments | flash | 实验充分性、基线公平性、消融可追溯 |
| novelty | flash | novelty 声明、引文正确性、CAND 落实 |
| reproducibility | flash | 逐种子数据、脚本、环境锁、披露 |
| writing | flash | 摘要/正文一致性、声明强度、编译产物 |
| ethics | flash | Broader Impact、数据合规、COI |
| figures | flash | 图表数值与正文/e1.json 一致性（deepseek-eyes 审阅卡） |

## script（完整 JS，实战验证版）

```js
const { manuscript, evidence, ledger, litreview, protocol, roundPrev, pdf } = args

// R8 图表角色输入：调用者先用 deepseek-eyes 为 PDF 的表格/图页面生成审阅卡，
// 并将卡片文本放入 args.reviewCard（describe_image.py --image main.pdf --page N
// --mode paper --output 卡片.md 后读取该文件内容）。无卡片时 R8 降级为跳过。
const reviewCard = args.reviewCard || '（未提供图表审阅卡，跳过图表核验）'

const roles = [
  { id: 'methodology', label: 'R1 方法论审稿人', focus: '...', model: 'deepseek-v4-pro' },
  { id: 'statistics', label: 'R2 统计审稿人', focus: '...', model: 'deepseek-v4-pro' },
  { id: 'experiments', label: 'R3 实验审稿人', focus: '...', model: 'deepseek-v4-flash' },
  { id: 'novelty', label: 'R4 新颖性审稿人', focus: '...', model: 'deepseek-v4-flash' },
  { id: 'reproducibility', label: 'R5 可复现审稿人', focus: '...', model: 'deepseek-v4-flash' },
  { id: 'writing', label: 'R6 写作审稿人', focus: '...', model: 'deepseek-v4-flash' },
  { id: 'ethics', label: 'R7 伦理审稿人', focus: '...', model: 'deepseek-v4-flash' },
  { id: 'figures', label: 'R8 图表审稿人', focus: '图表数值与正文/e1.json 一致性', model: 'deepseek-v4-flash' },
]

const reviewSchema = {
  type: 'object',
  properties: {
    role: { type: 'string' },
    verdict: { type: 'string', enum: ['acceptable', 'minor-revision', 'needs-major-revision'] },
    prevClosure: { type: 'string', description: '上一轮 Critical/Major 是否核实关闭' },
    summary: { type: 'string' },
    issues: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          severity: { type: 'string', enum: ['Critical', 'Major', 'Minor', 'Nit'] },
          location: { type: 'string' },
          problem: { type: 'string' },
          expectation: { type: 'string' },
          evidenceLink: { type: 'string' },
        },
        required: ['severity', 'location', 'problem', 'expectation', 'evidenceLink'],
        additionalProperties: false,
      },
    },
  },
  required: ['role', 'verdict', 'prevClosure', 'summary', 'issues'],
  additionalProperties: false,
}

const basePrompt = (role) => {
  if (role.id === 'figures') {
    // R8 图表角色：文本模型无眼睛，先用 deepseek-eyes 生成审阅卡再核验。
    // 主 agent 需在运行 workflow 前为 PDF 的表格/图页面生成审阅卡
    // （describe_image.py --image main.pdf --page N --mode paper --output 审阅卡.md），
    // 并把卡片内容放入 reviewCard 变量。
    return `你是 TMLR 的${role.label}（第 N 轮）。你的任务：核验论文图表（${pdf}）
中的数值与正文、evidence JSON 的一致性。以下为 deepseek-eyes 生成的图表审阅卡
（视觉模型转录，作为图片的文本等价物）：

"""${reviewCard}"""

请逐项核验：1) 表中 ECE/CI/Accuracy 与 e1.json、正文是否一致（允许四舍五入差异）；
2) 统计标记（W/p/r/rank-biserial/Holm）与正文是否一致；3) 消融数值与 e2.json
是否一致；4) 图表标题/轴/图例是否完整。发现不一致时给出严重度与位置。
只报告真实存在的问题。用中文输出。`
  }
  return `你是 TMLR 的${role.label}。这是对抗性审稿（第 N 轮）。你的任务：
1) 核验上一轮（${roundPrev}）的 Critical/Major 是否核实关闭——独立用工具
   重算/重编译/arXiv API 实证，不要只信作者声明；
2) 检查${role.focus}的新问题。
文件（本地可读）：稿件 ${manuscript}；证据 ${evidence}（e1.json 主实验、
e2.json 消融、seed_pairs.npz 逐种子原始数据）；分析脚本与协议 ${protocol}；
claim ledger ${ledger}；文献综述 ${litreview}。
反偏置纪律（I2/E054，逐条自检后输出）：①不因输出位置/顺序偏向任一方；
②不偏向与你自己同族的模型产物（自偏好）；③对冗长/简短输出做长度归一后评判；
④只报告当前文件真实存在的问题，已关闭的问题不要重复报。
${role.id === 'methodology' ? `Soundness 对码硬约束（G7/E088，MLR-Bench 模式）：
评分 Soundness 前必须逐一核对 ${protocol} 与 evidence/、scripts/ 下实际代码/脚本
与正文方法描述的一致性，并显式判断论文中的结果是 real 还是 fake（在 summary 里
写出"已核对：<具体文件> ↔ <正文方法描述>，结论：real/fake"）。
未核对代码之前，Soundness 相关 issue 不得给出低于 Major 的严重度；发现
方法描述与实现不符、结果无法从脚本复现时，必须报 Critical 并给出具体文件与行。
只报告真实存在的问题。用中文输出。`
: `只报告真实存在的问题。用中文输出。`}
`

phase('Review')
const results = await parallel(roles.map((r) => () =>
  agent(basePrompt(r), { label: r.label, phase: 'Review', schema: reviewSchema, model: r.model })
    .then((v) => ({ ...v, roleId: r.id }))
))

const clean = results.filter(Boolean)
const counts = { Critical: 0, Major: 0, Minor: 0, Nit: 0 }
for (const r of clean) for (const i of r.issues || []) counts[i.severity] = (counts[i.severity] || 0) + 1

return {
  rolesRun: clean.map((r) => r.roleId),
  severityCounts: counts,
  verdicts: clean.map((r) => ({ role: r.roleId, verdict: r.verdict })),
  reviews: clean.map((r) => ({
    role: r.roleId,
    summary: r.summary,
    issues: (r.issues || []).map((i) => ({ severity: i.severity, location: i.location,
      problem: i.problem, expectation: i.expectation, evidenceLink: i.evidenceLink })),
  })),
  failedRoles: roles.map((r) => r.id).filter((id) => !clean.some((c) => c.roleId === id)),
}
```

## 关键经验（近二十轮实战沉淀）

1. **审稿人必须独立重算**：prompt 里强制"用工具重算/重编译/arXiv API 实证，
   不要只信作者声明"——这抓到了三元组矛盾、rank-biserial 错值、引文作者错误。
2. **多角色交叉验证**：同一缺陷被 2-5 个角色独立指出 = 高置信度真实缺陷。
3. **已声明资源限制不重复报**：prompt 明确"O01/O02/O05 为演示限制，不要重复报"，
   避免审稿人刷已声明的缺口。
4. **收敛判据**：Critical 归零 + 一轮无新 Major 才算收敛；收敛后跑六扫 + 验收门
   + manifest 全绿，把 REVIEW_R{n}_summary.md 与 ROUND_R{n}.md 落盘入账。
5. **回归门**：把旧错值（stale 统计量/旧引用键/旧 CI）加入 gates_config 的
   stale-marker 门，防止下一轮修改时复活。
6. **"修复轮"引入回归（R5/R6 实证，FM-23）**：为修 A 引入 B——每次修改后都
   重新审/重算；新增合规/方法断言必须一手来源可溯源；数值改动做单步舍入核对。
7. **清单纪律（R6 实证，FM-24）**：修改任何交付文件后**立即**重建 evidence_manifest
   （`build_evidence_manifest.py --verify`），不等到轮次结束；报告计数以 verify
   实际输出为准。
8. **收敛后做加权分终评**：用 scholar-evaluation 的 TMLR 加权分
   （0.30N+0.35S+0.25Si+0.10C）独立打分——审稿收敛只证明流程问题清零，
   **不证明科学结论成立**（模拟数据/缺失实验会把 N/Si 锁死，见 SELF_ASSESSMENT.md）。
9. **工具输出可复现 > 流程纪律（R12 实证，FM-25）**：扫描/验证脚本的报告必须渲染
   相对路径（不内嵌绝对路径），否则"按标准流程重跑"本身就会改变 reports 字节、
   使 FM-24 门反复失效。修复后从不同 cwd 运行应字节一致——可复现性从工具层面
   保证，比让流程参与者记得纪律更可靠。审稿时检查报告是否含绝对路径。
10. **报告不能自引用清单元数据，也不能依赖评审历史（R13-R21 实证，FM-26）**：
    (a) 扫描器必须排除 evidence_manifest.json（其 size 字段会使报告永远比清单旧一代）
    和 gates_config.json（过程配置）；(b) 扫描器必须排除流程文档（ROUND_R*/REVIEW_R*/
    SELF_ASSESSMENT*.md——评审轮次增删不得改变证据扫描输出）；(c) 同类工具修复必须
    一次覆盖全部（四个扫描器共享同一缺陷模式，只修一个会留下"1/4 固定点"）；
    (d) `--out` 输出目录应自动排除（写到默认排除集外会自引用）。审稿时验证：
    写探测流程文档 → 重扫 → 报告字节应不变。

11. **引文有效性三层核验 + 防"虚报完成"（R17-R26 实证，FM-27）**：
    (a) 引文核验分三层：标题真实 → 作者正确 → **结果有效**（用 arXiv API 查
    comment/withdrawn 字段，如 singh2021 作者自注"证明假设错误致结果失效"）；
    (b) 补引文必须一手来源（PMLR/arXiv/Crossref），arXiv API 不可用时不得凭记忆
    写标题；(c) 删除/修改引文后必须**全文 grep 确认零残留**（同一键可能在
    Introduction 与 Related Work 两处出现）+ 重编译用 pdftotext 核对参考文献
    条数；(d) 变更日志标"done"前必须验证实际落地（R24 protocol 哈希大小写不匹配
    致替换静默失效）。审稿时验证：arXiv comment 字段、全文 grep 引文键、PDF 参考文献表。

12. **验证脚手架免疫 > 清理纪律（R9/R11/R21/R38 实证，FM-28）**：并发审稿/验证进程
    会在仓库内创建 .r*_verify_backup/、tmp_r*_fixedpoint/、.compile_check/ 等脚手架
    目录并覆写 reports，污染 FM-24 门（流程清理总被违反）。根治：扫描器与 manifest
    构建器内置脚手架目录排除（.r*/tmp_r*/.verify*/.review_*/.compile* 前缀 +
    _verify/_check/_backup/_fixedpoint 后缀；注意 verify_ 前缀只匹配目录、不误伤
    scripts/verify_claim_ledger.py 类合法文件）。审稿时验证：写入探测脚手架目录 →
    扫描与 manifest 应不受影响。
13. **真实实验可复现性 = 训练配置即证据（Phase A 实证，FM-29）**：真实训练替换
    模拟数据后，可复现性从"重算统计量"扩展到"重训模型"——训练脚本必须内嵌
    全部配置（种子/epochs/优化器/损失系数/数据增广）并输出 cfg 快照到结果文件；
    种子数缩减必须显式披露（不得静默削弱统计功效）；GPU 环境（torch+cu 版本）
    记入 protocol。审稿时验证：train 脚本 --seeds N 重跑产物哈希一致、cfg 字段
    与 protocol 一致、披露语句存在。

## 成本自适应审稿（Cost-Adaptive Review，L3-3）

> 决策证据：演化账本 G003（`<PROJECT_ROOT>\.agent-memory\evolution\EVOLUTION_LEDGER.md`，
> 2026-08-15，统计门，真实模型数据）。equal-budget A/B（4 样稿/5 缺陷，双臂各
> 32 调用，calls 比 1.0，真实 LLM deepseek-v4-flash）：8 角色 multi-role 与
> 单审稿人双臂均检全 5 缺陷、配对全平（b=0/c=0，exact McNemar p=1.0000），
> 误报 multi 3 / single 2（多角色略高），成本 Wilcoxon p=1.0000（全零差）→
> **hold**：预算内无显著缺陷检出增益且误报略高，不把 multi-role 提升为默认
> 审稿姿势。

### 默认姿势不变（质量优先）

- G003 的 hold 只约束"是否把 8 角色提升为默认"：**未证明 8 角色优于单审稿人，
  也未证明缩减无损** → 默认仍按需展开 8 角色（质量优先），成本自适应只用于
  **缺陷密度低时的收敛加速**，不改变质量优先默认。
- 本节约束只回答一个问题：什么时候可以少跑角色、什么时候必须跑满——所有
  缩减都必须在收敛判据（一轮无新 Critical/Major）内完成。

### 缺陷密度驱动的收敛规则

1. **首轮判据（R1）**：汇总 REVIEW_R1 全部角色的 `severityCounts`
   （Critical/Major/Minor/Nit）：
   - **缩减条件（全部满足）**：Critical+Major ≤ 1，且 methodology 与
     statistics 两个角色**均无 Major**（Minor/Nit 不阻塞）。
   - 满足 → R2 缩减为 **4 角色：methodology / statistics / experiments /
     novelty**（保统计与方法的硬检查），收敛目标不变；
   - 不满足（首轮缺陷多）→ 保持 8 角色并按缺陷主题**延长审稿**（增加一轮
     聚焦复查或加长该轮审查），不缩减。
2. **缩减只许一次**：4 角色轮若再检出 Critical/Major → 下一轮**恢复 8 角色**
   （缺陷密度回升 = 缩减失败信号），之后不得连续缩减。
3. **记录义务**：任何缩减/恢复必须写入 `ROUND_R{n}.md` 的成本表（角色数、
   模型调用数、缩减理由、是否触发恢复），供审计与演化账本复核。
4. **不变量**：缩减永不触碰 statistics 与 methodology（统计/方法是硬检查）；
   R8 figures 无审阅卡时本就降级跳过，不计入缩减决策。

### 每轮成本记录表模板（追加到 ROUND_R{n}.md）

| 轮次 | 角色数 | 模型调用数 | 缩减？ | 触发依据（缺陷密度） | 备注 |
|---|---|---|---|---|---|
| R1 | 8 | 8（pro×2 + flash×6） | 否（默认全量） | — | 首轮 C+M = N |
| R2 | 4 | 4（pro×2 + flash×2） | 是 | R1 C+M≤1 且 meth/stat 无 Major | 恢复条件未触发 |
| Rn | 8 | 8（pro×2 + flash×6） | 恢复 | Rn-1 检出新 C/M | 缺陷密度回升 |

> 模型调用数 = 角色数 × 1 次 workflow agent 调用；终评双模型打分（O2）、
> 双轴核验质疑者等额外调用在"备注"中单列。每轮轮末把本表追加到
> `ROUND_R{n}.md` 的成本表位置。

### 取舍边界（明确）

- **硬检查不可裁剪**：statistics（W/p/r 自洽、CI/效应量口径、多重比较）与
  methodology（方法定义、逻辑漏洞、术语统一）是审稿底线，任何缩减方案不得
  跳过。
- **软角色可按缺陷密度裁剪**：experiments / novelty / reproducibility /
  writing / ethics / figures 按首轮缺陷主题取舍——例如首轮仅 writing 类
  Minor 时，R2 可保留 novelty 复查声明、把 writing 降级为双轴核验抽查。
- **缩减 ≠ 降标**：4 角色的严重度协议、双轴核验（B2）、收敛判据、六扫 +
  验收门全绿要求与 8 角色完全一致——只少角色，不少纪律。
- **G003 证据边界**：A/B 仅 4 样稿/5 缺陷、缺陷类型有限 → 本规则只以
  "缺陷密度"为触发信号，不扩展到"按论文类型/领域决定角色数"；后者需新的
  equal-budget 验证入账（G 系列）后方可生效。

## 双轴核验（Dual-Axis Verification，B2）

> 来源：skills-main code-review 的"双轴并行、互不污染"模式。审稿发现的每条
> Critical/Major 都要过两轴，两轴独立判定，结论不一致时显式标出。

### 两轴定义

| 轴 | 回答的问题 | 证据手段 | 失败含义 |
|---|---|---|---|
| **数字一致性轴 (numbers)** | 这条 finding 里的每个数字都能从证据重算出来吗？ | `verify_claim_ledger.py` + 独立重算(seed_pairs.npz/e1.json/e2.json) | finding 的数字经不起重算 → finding 本身降级 |
| **表述忠实轴 (fidelity)** | finding 的表述忠实于证据吗？有没有夸大/越界/把"在 X 条件成立"写成"普遍成立"？ | 重读 claim ↔ 证据原文，对照 scope 声明与 hedges | finding 越界声明 → 要求收紧,不得放宽证据 |

### 协议（在 Review 阶段之后执行）

1. 收集 8 角色产出的全部 Critical/Major issue（含 evidenceLink）；
2. 对每条 issue 跑双轴核验（可用 stats 角色 + 独立重算 agent，或换模型做质疑者）：
   - numbers 轴：`重算 → 比对 finding 数字 → 一致?`;
   - fidelity 轴：`重读 claim ↔ 证据原文 → 表述在范围内?`;
3. 输出每条 issue 的两轴判定；任一轴失败 → 该 issue 标记
   `needs-clarification`（不直接进修复清单,先回退给作者澄清或重算）；
4. 双轴都过 → 进入修复清单；两轴结论冲突（数字对但表述越界）→ 显式标出冲突。

### 双轴核验输出 schema（追加到 reviewSchema 之外独立输出）

```json
{
  "findings": [
    {
      "issueId": "R2-03",
      "numbers_axis": {"passed": true, "recomputed": "p=0.0123 (matched)"},
      "fidelity_axis": {"passed": false, "reason": "claims 'universal', evidence covers 3 datasets only"},
      "decision": "needs-clarification"
    }
  ]
}
```

### 接线

- B1 的 DOUBT 结构化落点：本核验即 DOUBT 的评审侧执行；
- 与 gates_config 联动：`未清 needs-clarification` 阻止 D4→D5 退出；
- 经验 1（独立重算）与经验 6（修复轮回归）在 numbers 轴复用；经验 2
  （多角色交叉）可折算为"两轴独立判定的一致性"。

## 10. no_code 消融评审（E089，MLR-Bench 模式）

> 目的：量化"证据可得性"对评审结论的影响。同一稿件评两轮——一轮给证据
> （evidence/ + scripts/ 全可见），一轮不给（只看稿件正文）——比较两轮评分
> 差异，识别"靠证据撑起来的声明"（不给证据就露馅）。

**何时做**：
- 投稿前终评（Phase 5 前）至少做一次；
- 或当 methodology/statistics 角色报告"结论依赖未展示的证据"时触发。

**做法**：
1. **两轮盲评**：同一审稿角色（建议 methodology + statistics 两个角色），
   对同一稿件分别以 `{manuscript}` 与 `{manuscript + evidence}` 两种输入评审；
   judge 不得知晓两轮的对应关系（位置交换，同 E002 双判纪律）。
2. **记录**：每轮输出 severityCounts 与逐条 finding；比较两轮差异：
   - 不给证据轮的 Critical/Major 显著多于给证据轮 → 声明过度依赖证据可得性
     （正文可读性/自足性缺陷，MLR-Bench no_code 消融同构）；
   - 两轮无差异且都给高分 → 证据对结论无贡献，警惕"证据是摆设"。
3. **输出**：`ROUND_R{n}` 的成本表加一列 `no_code 消融`（两轮 severity 差），
   并写入 `REVIEW_R{n}_summary` 的结论节。
4. **处置**：不给证据轮多出的 Critical/Major 逐条转 issue，进修复轮——
   正文必须自足（关键数字、方法、基线在正文内可核），不得依赖附录/仓库文件。

**边界**：no_code 消融是评审质量的诊断工具，不是 gate；不设硬性通过线，
但两轮差异 > 50% 时必须人工复核每条差异 finding。

## 11. 分阶段评审（G5/E086，MLR-Bench 四阶段 rubric，可选）

> 目的：长论文（>15 页或证据包>10 文件）的对抗审稿默认整稿一轮；当方法论/
> 统计角色在 R1 报告"范围过大、难以深挖"时，可切换分阶段评审，把整稿评审
> 拆成四个独立子轮，每轮只审一个研究阶段（对应 MLR-Bench 的
> idea/proposal/experiment/writeup 分步 rubric 思路）。

**四阶段维度**（每阶段独立出 REVIEW 报告，严重度协议不变）：

| 阶段 | 审什么 | 维度（MLR-Bench 对应） | 输入 |
|---|---|---|---|
| S1 idea | 研究问题/动机是否成立、与任务/文献 gap 是否对齐 | Consistency/Clarity/Novelty/Feasibility | manuscript §1 + LITERATURE_REVIEW.md |
| S2 proposal | 方法定义是否自洽、术语统一、假设是否声明 | Consistency/Clarity/Novelty/Soundness/Feasibility | manuscript §2-3 + state_snapshot |
| S3 experiment | 实验是否充分、基线公平、消融可追溯、功效论证 | Completeness/Novelty/Soundness/Insightfulness | manuscript §4-5 + evidence/ + power_analysis.json |
| S4 writeup | 数字一致性、声明强度、图表自明、摘要-正文一致 | Consistency/Clarity/Completeness/Soundness | 全文 + reports/*.md 扫描报告 |

**协议**：
1. 触发：R1 整稿评审后，若 methodology 或 statistics 报"范围过大"类 Major，
   或稿件 >15 页 → R2 起切分阶段（S1→S2→S3→S4 顺序，每阶段一个子轮）；
2. 每阶段仍跑该阶段相关的机器扫描（S3 必跑 scan_stats_consistency +
   scan_hallucination；S4 必跑 scan_number_consistency + scan_figure_claims）；
3. 收敛判据与整稿一致：Critical 归零 + 一轮无新 Major；切分后每阶段独立计数，
   全部阶段收敛才算轮收敛；
4. 切分是可选加速器，不改变默认：整稿评审保持默认路径；
5. 记录：ROUND_R{n} 成本表标注"分阶段"与各阶段角色数。
