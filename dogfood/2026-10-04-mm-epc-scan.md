# Dogfood · 用本包扫描门审计 mm-epc（2026-10-04）

> 目的：验证包外可用性——扫描器能否直接吃一个**布局无关**的真实投稿仓。
> 对象：`aidless/mm-epc`（AAAI 2027 在投线，HEAD 10854cc，paper/ 目录：mm_epc_paper.tex + references.bib + statistical_table.tex + mm_epc_paper_blind.tex）。

## 跑法（两条命令，零适配）

```bash
python3 scripts/scan_number_consistency.py /path/to/mm-epc/paper --out scan.json
python3 scripts/gate_citations.py /path/to/mm-epc/paper --bib references.bib
```

`scan_number_consistency.py` 直接吃任意目录（.tex/.md/.json 全文频次 + cross-file 对账）——**无需论文包布局**，验证通过。

## 发现

### A. 扫描器侧（回灌本包）
1. **Table-vs-prose 误报模式 → FM-30**：5 个 mismatch 中 3 个是误报——`### 3.1 Setup` 章节号被当数值、`{+}0.068` vs `0.068`（LaTeX 强制正号 vs 无符号）、`1.00%` vs `1.0%`（精度格式）。格式差异报成 mismatch 会训练使用者忽略整段报告；修复方向：`equal(parse(x), parse(y))` 时降级 INFO 并标 format-only（FM-30 的检测/修复字段）。
2. 正向结果：**evidence JSON ↔ 正文双向盲区均为 0**（in-text-never-in-evidence / in-evidence-never-in-text）——mm-epc 的证据覆盖面在扫描器口径下是满的。

### B. mm-epc 侧（移交该仓 owner）
| 发现 | 位置 | 定性 |
|---|---|---|
| 统计表三副本两态 | `paper/statistical_table.tex` == `experiments/statistical_table.tex` ≠ `experiments/statistical_table_new.tex` | `_new` 是早期草稿（含 TBD 占位、仅 3 行数据、Qwen-plus 全 TBD）；数值与主稿不冲突（DashScope 行 0.273/0.341/0.068 一致），但会污染检索——建议删除或挪 archive/ |
| 百分比精度不统一 | `mm_epc_paper.tex:254` 正文 `1.0%` vs 表格 `1.00%` | 同值不同格式；投稿前统一小数位 |
| Δ 正负号呈现不一 | `statistical_table.tex:6` 表格 `{+}0.068` vs 正文 `0.068` | 同上，格式口径问题 |
| 空残留文件 | `新建 文本文档.txt`（0 字节，仓根） | 工作残留，删 |

### C. 门覆盖边界（验证 venue-mapping 的意义）
`check_tmlr_compliance.py` 对 mm-epc（AAAI 稿）**不适用**——G1 模板正则、G6 bst、G7 Broader Impact 语义全是 TMLR 专属；这正是 venue-mapping.md §3b（AAAI 专节）存在的理由。mm-epc 投稿前人工核对项：作者块内容检查（AAAI 匿名非选项驱动）、生成式 AI 使用披露（以当年 CFP 为准）、7+1 页数。

## 结论
- 包外可用性：**scan/gate_citations 开箱即用**（布局无关）；合规门 venue 绑定明确（文档已把边界写死）。
- 回灌：FM-30 入库 + 索引机制上线（本次 dogfood 的直接产出）。
- 待办（可选）：scan_number_consistency 加 format-only 分类（FM-30 修复字段）。
