# 证据状态机（Evidence States）

> R43 评估确立：工程失效结果不得作为科学结论。本文件定义证据的分类与流转。

## 状态定义

| 状态 | 含义 | 能否支撑论文结论 | 处置 |
|---|---|---|---|
| `broken_engineering` | 训练发散/工程故障产物 | 否 | ARCHIVE/lessons + 工程附录 |
| `tainted_provenance` | 来源不明/被覆盖/无法确认 | 否 | 仅审计记录（results/broken/） |
| `backfilled_candidate` | 运行后补记 run record（provenance 弱） | 仅诊断/候选，**不可单独作最终唯一证据** | run 工作目录 + 诚实标注 |
| `pre_run_recorded_candidate` | 启动前已写 run record + 输出基线 | 可进入独立重算与封存流程 | run 工作目录 |
| `candidate_real_evidence` | 修复后、冻结配置、完整 run record | 仅封存+独立重算+审计后 | run 工作目录 |
| `verified_real_evidence` | 封存+验证+独立重算通过 | 是（主张强度受范围约束） | results/verified/ |

**provenance 等级**（审查 R46 要求）：
- `backfilled_candidate` < `pre_run_recorded_candidate` < `verified_real_evidence`
- backfilled 可作候选，但需 `--pre-run` 完整复现 seed 验证协议可从头启动后才可信

## 流转规则

```
训练完成 → candidate_real_evidence
  → 独立重算一致 → 只读验证通过 → 原子 seal → verified_real_evidence
  → 论文/ledger 只读 verified bundle
任何环节失败 → broken_engineering 或 tainted_provenance（不进论文）
```

## 硬规则

1. **工程失效结果 ≠ 科学负结果**：发散/覆盖/来源不明的 run 只能作为诊断证据
   （broken/tainted），不能写成"协议下未观察到支持"——因为协议本身没被有效执行。
2. **论文状态透明**：证据未就绪时，正文应标 `evidence under re-execution`，
   不引用候选/失效数字。
3. **H1/H2 未决**：候选证据封存前，假设状态只能是"未决"，不是"支持/否决"。
4. **只读验证**：验证器/门禁不得改写 canonical evidence（verify_tree_diff 检查）。
5. **封存不可覆盖**：sealed run 任何命令不得改写（seal_run.py STATUS）。

## 与现有机制的关系

- gates/manifest 验证的是工程一致性；证据状态机验证的是科学资格。
- 两者分离：工程全绿 ≠ 证据可用（R39 实证）。
- FINDINGS 记录工程教训；证据状态机决定哪些结果能进论文。

## 污染传播（L2-5）：源文件 tainted → 引用它的声称自动 blocked

状态机只管证据文件本身的状态；本机制把状态传播到声称层：一旦某个证据
源文件被判定为 broken/tainted（或 `state` 中任何非 `verified`/`candidate`
的取值），`CLAIM_LEDGER.md` 中引用它的所有声称自动进入 blocked 语义——
在证据恢复（重新独立重算 + 封存 + 状态改回 `verified`/`candidate`）之前
不得进入正文，验证器直接以 exit 1 阻断。

### tainted.json 格式

`<paper_dir>/evidence/tainted.json`（可选文件，缺失 = 无污染）：

```json
{
  "tainted": ["results/e1.json"],
  "state": {"results/e1.json": "broken", "results/e2.json": "verified"}
}
```

- `tainted`（数组）与 `state`（映射）可二选一，也可同时给出；
- `state` 中取值不是 `verified` / `candidate` 的文件视为污染，报告用该取值
  作状态（如 `broken`）；
- `tainted` 列表中的文件一律视为污染（状态取 `state` 中的值，缺省 `tainted`）；
- 使用短状态名，与本文档长名的对应：`broken_engineering` → `broken`、
  `tainted_provenance` → `tainted`、各 `*_candidate` → `candidate`、
  `verified_real_evidence` → `verified`；
- 路径写法与 ledger 一致，支持相对写法容错（如 `evidence/../results/e1.json`）。

### 用法（Phase 1 起草前 + Phase 3 机器检查）

```
python scripts/verify_taint.py <paper_dir> --fail-on-error --out reports/taint.md
```

- `Tainted_claims`（ERROR）：引用污染文件的声称（claim id + 证据路径 + 污染状态）；
- `Missing_evidence`（ERROR）：声称引用的证据文件不存在；
- `Claims_checked`（INFO）/ `Tainted_files`（INFO）；
- `--fail-on-error`：任一 ERROR 段 > 0 → exit 1。

### 状态机 → 声称阻断规则

1. `broken_engineering` / `tainted_provenance`（`broken` / `tainted`）及
   `state` 中任何非 `verified`/`candidate` 的取值，一律阻断引用声称；
2. `candidate` 不触发污染阻断（但按状态机硬规则仍不可单独作最终唯一证据，
   由 verify_claim_ledger / 验收门另行把关）；
3. `verified` 不阻断；
4. 证据恢复 = 重新独立重算 + 封存 + 状态改回 `verified`/`candidate`，然后
   重跑 `verify_taint.py` 直至 ERROR 清零。

### 与 verify_claim_ledger 的分工

- `verify_claim_ledger.py`：工程一致性——证据文件/字段存在、数值匹配、
  正文数字有账本覆盖；
- `verify_taint.py`：科学资格——证据状态机是否把某声称判为 blocked；
  两者独立运行、缺一不可：工程全绿 ≠ 证据可用（R39 实证）。
