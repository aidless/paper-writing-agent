# Dogfood · 用本包扫描门审计一篇在投稿件（2026-10-04）

> 目的：验证包外可用性——扫描器能否直接吃一个**布局无关**的真实投稿仓。
> 对象：一篇正在投稿的双盲会议稿件。
>
> **为什么脱敏**：本仓是公开的，而该稿件处于双盲评审期。原版这里写着仓库名、
> HEAD、内部文件名和投稿去向，任何人都能据此定位到那份稿子。双盲评审的意义
> 恰恰在于作者与稿件的对应关系不可检索，所以这些字段全部替换为占位符。
> 扫描方法、判定口径和下面的复算过程一字未改——本案例的价值恰恰在于
> 「初判 2 处真实问题、复算后全部撤案」这个过程，与稿件身份无关。
>
> 稿件侧：`paper/` 目录含正文 `.tex` + `references.bib` + 统计表 `.tex` + 匿名版 `.tex`。

## 跑法（两条命令，零适配）

```bash
python3 scripts/scan_number_consistency.py <REPO>/paper --out scan.json
python3 scripts/gate_citations.py <REPO>/paper --bib references.bib
```

`scan_number_consistency.py` 直接吃任意目录（.tex/.md/.json 全文频次 + cross-file 对账）——**无需论文包布局**，验证通过。

## 发现

### A. 扫描器侧（回灌本包）
1. **Table-vs-prose 误报模式 → FM-30**：5 个 mismatch 中 3 个是误报——`### 3.1 Setup` 章节号被当数值、`{+}0.068` vs `0.068`（LaTeX 强制正号 vs 无符号）、`1.00%` vs `1.0%`（精度格式）。格式差异报成 mismatch 会训练使用者忽略整段报告；修复方向：`equal(parse(x), parse(y))` 时降级 INFO 并标 format-only（FM-30 的检测/修复字段）。
2. 正向结果：**evidence JSON ↔ 正文双向盲区均为 0**（in-text-never-in-evidence / in-evidence-never-in-text）——该稿件的证据覆盖面在扫描器口径下是满的。

### B. 稿件侧（移交该仓 owner）
| 发现 | 位置 | 定性 |
|---|---|---|
| 统计表三副本两态 | `paper/statistical_table.tex` == `experiments/statistical_table.tex` ≠ `experiments/statistical_table_new.tex` | `_new` 是早期草稿（含 TBD 占位、仅 3 行数据、Qwen-plus 全 TBD）；数值与主稿不冲突（DashScope 行 0.273/0.341/0.068 一致），但会污染检索——**已删除（git 历史可恢复）** |
| ~~百分比精度不统一~~ | 初判 `main.tex:254` 正文 `1.0%` vs 表格 `1.00%` | **复核撤案**：表格 `1.00` 是 PCI 倍数列（`\times$1.00/\times$1.55`，L281-282），与正文 `1.0%` 百分比是不同量纲——扫描器跨量纲误配对，非精度漂移 |
| ~~Δ 正负号呈现不一~~ | `statistical_table.tex:6` 表格 `{+}0.068` vs 正文 `0.068` | **复核撤案**：Δγ 列内全部带显式符号是排版对齐惯例（$-$0.208/$-$0.088/+0.068），正文作为带符号数学量写 `\Delta\gamma=0.068` 正确——两者可并存 |
| 空残留文件 | `新建 文本文档.txt`（0 字节，仓根） | 工作残留，**已删除** |

> 复核结论（2026-10-04 二次核对）：5 个 mismatch **全部为扫描器误报/可并存惯例**，该稿件数字无漂移。这一轮复核本身成为 FM-30 的核心案例：mismatch 报告必须人工分类，"2 真实格式项"的初判在量纲核对后清零。

### C. 门覆盖边界（验证 venue-mapping 的意义）
`check_tmlr_compliance.py` 对该稿（非 TMLR 场次）**不适用**——G1 模板正则、G6 bst、G7 Broader Impact 语义全是 TMLR 专属；这正是 venue-mapping.md §3b（AAAI 专节）存在的理由。该稿投稿前人工核对项：作者块内容检查（AAAI 匿名非选项驱动）、生成式 AI 使用披露（以当年 CFP 为准）、7+1 页数。

## 结论
- 包外可用性：**scan/gate_citations 开箱即用**（布局无关）；合规门 venue 绑定明确（文档已把边界写死）。
- 回灌：FM-30 入库 + 索引机制上线（本次 dogfood 的直接产出）。
- 待办（可选）：scan_number_consistency 加两类降噪——format-only 分类（±/精度）与量纲感知配对（×倍数列 vs % 百分比）——本轮 5/5 误报全部源于此二类。
