# Venue 参数化映射（L3-2：TMLR G1-G11 → CVPR / NeurIPS / ICML / ACL）

> 审计项 L3-2「venue 参数化」的落地文档（纯文档，无脚本改动）。
> 目的：把 `scripts/check_tmlr_compliance.py` 的 TMLR 专用合规检查映射到其他主流 venue，明确「哪些检查可复用、哪些需替换/新增」，并给出人工适配的最小流程。
> 本表为**撰写时点快照**：各会议规则逐年更新，投稿季前必须以各会议官网当年 submission 页面为准（来源见 §6；遗留风险见 §7）。

## 1. 边界声明（重要）

- `check_tmlr_compliance.py` **当前只覆盖 TMLR**：硬编码了 TMLR 模板正则（`\usepackage{tmlr}` 无选项、jmlr class 反例）、`tmlr.bst` 引用检查、100MB 补充材料阈值、TMLR 匿名仓库白名单（`ALLOWED_URL_MARKERS` 含 jmlr.org 等）、Broader Impact 节语义（G7）。
- 脚本实际自动化覆盖：**G1（模板）、G3（匿名化）、G4（匿名仓库/URL）、G6（引用）、G7（Broader Impact）** + EXTRA（占位符、`+/-` 格式、zip 大小）。
- 脚本**未**覆盖（需人工/其他脚本）：G2（US Letter + pdflatex 编译参数）、G5（补充材料匿名性）、G8（OpenReview 表单）、G9（交叉论文重叠）、G10（双盲隔离）、G11（验收门 + 哈希对账）。
- 对 CVPR / NeurIPS / ICML / ACL：**不运行 TMLR 脚本当作结论**。按 §4 的 G 级可复用性矩阵人工映射，或按 §5 的最小流程先做参数化改造再复用。

## 2. G1-G11 现状盘点

| 门 | 检查项 | 脚本覆盖？ | 通用性（跨 venue） |
|---|---|---|---|
| G1 | 模板（匿名提交版） | ✅ 脚本（TMLR 包名硬编码） | 逻辑通用，包名/正则需替换 |
| G2 | US Letter + pdflatex | ❌ 人工 | 通用（四会均为 US Letter / letterpaper） |
| G3 | 匿名化（作者/机构/致谢/邮箱/姓名） | ✅ 脚本 | **完全通用**（四会均为双盲） |
| G4 | 匿名仓库 / URL | ✅ 脚本（白名单 TMLR 化） | 逻辑通用，白名单需替换 |
| G5 | 补充材料 ≤ 上限、匿名、PDF/ZIP | ⚠️ 仅 zip 大小（EXTRA） | 阈值/格式按 venue 参数化 |
| G6 | 引用格式（bst） | ✅ 脚本（tmlr.bst 硬编码） | 需替换为各 venue bst |
| G7 | Broader Impact / 伦理声明 | ✅ 脚本（TMLR 语义） | **语义各 venue 不同**，需替换/新增 |
| G8 | OpenReview 表单 | ❌ 人工（init_paper.py 下发的核对清单） | 字段各 venue 不同，需重做 |
| G9 | 交叉论文重叠审计（原创性） | ❌ 人工 | **venue 无关，通用** |
| G10 | 预印本与提交版双盲隔离 | ❌ 人工 | **通用** |
| G11 | 验收门全 PASS + 哈希对账 | ❌ 其他脚本（run_acceptance_gates.py / build_evidence_manifest.py） | **通用** |

## 3. 维度差异主表（TMLR 基线 → 四个 venue）

> 标注「以当年官网为准」的单元格是历年波动项；本表数值为快照。

| 维度 | TMLR（基线，默认自动化） | CVPR | NeurIPS | ICML | ACL（ARR + 会议 commitment） |
|---|---|---|---|---|---|
| 模板与排版 | `\usepackage{tmlr}` **无选项** = 匿名；`[accepted]` 仅供 camera-ready；`[preprint]` 去匿名（仅供预印本） | `cvpr.sty`（双栏 letterpaper）；匿名提交用 `\usepackage[review]{cvpr}` | `neurips_2025.sty` 等（双栏）；提交版无选项；`[preprint]` 选项去匿名 | `icml2025.sty`（双栏）；`[accepted]` = camera-ready（去匿名）；`[preprint]` = 预印本 | `acl.sty`（双栏）；`\usepackage[preprint]{acl}` 去匿名 |
| 匿名化规则 | 双盲；作者/机构/致谢/作者贡献全部去除 | 双盲（`[review]` 选项）；去除作者块与致谢；**需匿名化对自身工作的引用**（如 "Anonymous et al." 惯例，以当年指南为准） | 双盲；允许对自身 prior work 的匿名化引用（anon 占位惯例，以当年 CFP 为准） | 双盲；自身引用匿名化惯例同 NeurIPS（以当年 CFP 为准） | 双盲（ARR）；自身引用匿名化惯例同 ACL 指南（以当年为准） |
| 页数限制 | 风格文件**无硬上限**；惯例正文 ~10-20 页，参考文献/附录另计（以 author guide 为准） | 正文 ≤ 8 页（不含参考文献）；camera-ready 通常放宽 1-2 页（以当年为准） | 正文 ≤ 9 页；参考文献不限；**附录在参考文献之后，不限页** | 正文 ≤ 9 页；参考文献不限；附录不限页；camera-ready 正文 10 页（以当年为准） | 正文 ≤ 8 页；参考文献不限；附录不限页 |
| 补充材料 | ≤ 100MB（脚本阈值）、匿名、PDF/ZIP | 单 PDF 或 ZIP ≤ 100MB、匿名 | 单 ZIP ≤ 100MB（内含 PDF）、匿名 | 单 PDF 或 ZIP（近年上限 100MB，以当年 CFP 为准）、匿名 | 单 PDF 或 ZIP；体积上限**以 ARR 官网当年说明为准**（历年在 ~20-100MB 区间波动，勿写死） |
| 参考文献格式 | `tmlr.bst`（硬编码检查） | IEEE 风格 bst（模板指定，如 `IEEEtran` 系；以当年 author-kit 为准） | natbib + `plain`/`unsrtnat`（模板未强制专属 bst） | `icml2025.bst`（natbib） | `acl_natbib.bst`（natbib） |
| Rebuttal 阶段与回复格式 | 公开评审（OpenReview）；评审后有作者回复/讨论阶段，随后编辑决策 | 评审后有 author response 窗口（近年走 OpenReview，以当年为准）；回复格式按平台要求 | author response 窗口 ~1 周（OpenReview）；只允许回答评审问题、禁止新增实验主张（以当年为准） | author response 窗口（OpenReview，以当年为准） | ARR 评审后有作者回复窗口（AC 推荐前）；commitment 到会议端后无新回复 |
| author 块（camera-ready 反匿名化） | 提交版删除；camera-ready 用 `[accepted]` 恢复 | camera-ready 恢复作者块（去掉 `[review]`） | camera-ready 恢复作者块；预印本用 `[preprint]` 选项 | camera-ready 用 `[accepted]` 恢复作者块 | camera-ready 恢复作者块；预印本用 `[preprint]` 选项 |
| 伦理声明 / 更广泛影响 | G7：Broader Impact 节（如适用，低风险可显式豁免） | 无强制 broader impact 节；存在 **ethics review 流程**（敏感论文被转伦理审查，以当年为准） | **Ethics Checklist 强制**（随稿提交）；Broader Impact 建议但近年非强制（以当年 CFP 为准） | 伦理影响讨论逐年表述不同（CFP 要求/建议视年份）；以当年 CFP 为准 | ACL Code of Ethics；建议 Ethical Considerations 节；涉人数据需 IRB/知情同意（以当年指南为准） |

## 3b. AAAI 专节（L3-2 增补，2026-10 快照）

> 动机：本包作者的一条实际投稿线目标为 AAAI；本节为 AAAI 做与 §3 等价的维度映射。
> ⚠ §7 快照警示同样适用：AAAI 各年度 CFP 差异显著（页数、双截止、AI 披露条款），投稿前以当年 aaai.org 官网为准。

### 3b.1 维度差异（TMLR 基线 → AAAI）

| 维度 | TMLR（基线） | AAAI（快照，以当年 CFP 为准） |
|---|---|---|
| 模板 | `\usepackage{tmlr}` 无选项=匿名 | `aaai.sty`（双栏 letterpaper）；**风格文件来自 AAAI Author Kit 官网，许可为 AAAI 自定义条款——禁止入仓再分发**，作者各自下载 |
| 匿名化 | 双盲 | 双盲；作者块留空/Anonymous、致谢与资助删除、自身引用匿名化（同 NeurIPS 惯例） |
| 页数 | 无硬上限（惯例 10-20） | 近年主文 **正文 7 页 + 第 8 页仅参考文献**（7+1/7+2 历年波动）；camera-ready 可 +1 页（以当年 CFP 为准） |
| 补充材料 | ≤100MB、匿名、PDF/ZIP | ZIP/PDF 匿名；体积上限以当年 CFP 为准（勿写死） |
| 引用格式 | `tmlr.bst` | `aaai.bst`（Author Kit 随附；G6 的替换目标） |
| 伦理 / AI 披露 | G7 Broader Impact（如适用可豁免） | 无强制 ethics checklist；**近年 CFP 引入生成式 AI 使用披露条款**——LLM 辅助写作的稿件必须核对该年要求（存在与否、披露位置与措辞） |
| 截止节奏 | 随时可投 | **摘要注册 deadline 早于全文约 1-2 周**，双截止均硬；另有独立 Student Abstract 赛道（篇幅更短、单独评审） |
| Rebuttal | 公开评审 + 作者讨论 | author feedback 窗口较短（通常数天、仅限回答评审问题，以当年为准） |
| 投稿系统 | OpenReview | 以当年为准（历史 CMT/OpenReview 均有）；字段需当年核对 |

### 3b.2 G 级映射（check_tmlr_compliance.py → AAAI）

| 门 | AAAI | 说明 |
|---|---|---|
| G1 模板 | 🔧 换检查语义 | 匹配目标 `aaai.sty`；**AAAI 匿名不由包选项驱动**（无 TMLR 的无选项/[preprint] 体系），应改为「作者块为空/Anonymous + 无真名」的内容检查——与 TMLR 语义不同，勿直接套选项正则 |
| G2 页面 | ✅ 复用 | letterpaper；7+1 页数人工核对 |
| G3 匿名化 | ✅ 复用 | 双盲通用；identity/email/name 扫描零改动 |
| G4 匿名仓库 | 🔧 换白名单 | AAAI 双盲下匿名仓库策略以当年为准 |
| G5 补充材料 | 🔧 参数化 | 逻辑复用；上限按当年 |
| G6 引用 | 🔧 换 bst | `aaai.bst` |
| G7 伦理 | ❌ 语义替换 | AAAI 无 Broader Impact 节语义；替换为「生成式 AI 使用披露 + 可选 Ethics Statement」核对 |
| G8 表单 | 🔧 重做清单 | 双截止 + Student Abstract 字段，按当年系统 |
| G9-G11、EXTRA | ✅ 复用 | venue 无关 |

### 3b.3 AAAI 适配最小流程（§5 之上的增量）

1. §5 第 1 步同款参数化；G1 按 3b.2 改为内容检查而非选项检查。
2. Author Kit 不入 `templates/`（许可限制）；本表只记录官方入口，投稿时人工置入。
3. 该投稿线的仓内已有 `aaai_student_abstract/`（Student Abstract 赛道产物），复用本表核对页数与匿名。


## 4. G 级可复用性矩阵（check_tmlr_compliance.py 的检查 × venue）

| 门 | CVPR | NeurIPS | ICML | ACL | 说明 |
|---|---|---|---|---|---|
| G1 模板 | 🔧 替换包名/反例正则 | 🔧 替换包名 | 🔧 替换包名 | 🔧 替换包名 | 逻辑（无选项=匿名、`[preprint]/[accepted]` 反例）**完全复用**，只换正则目标 |
| G2 页面 | ✅ 复用 | ✅ 复用 | ✅ 复用 | ✅ 复用 | 四会均 US Letter；pdflatex 编译参数人工核对 |
| G3 匿名化 | ✅ 复用 | ✅ 复用 | ✅ 复用 | ✅ 复用 | 双盲通用；脚本的 identity/email/name 扫描零改动 |
| G4 匿名仓库 | 🔧 换白名单 | 🔧 换白名单 | 🔧 换白名单 | 🔧 换白名单 | 逻辑通用；`ALLOWED_URL_MARKERS` 去掉 TMLR 专属项、按各会匿名策略增补 |
| G5 补充材料 | 🔧 阈值可复用 100MB | 🔧 阈值可复用 100MB | 🔧 阈值按当年 | 🔧 阈值按当年 | zip 大小检查逻辑通用，仅 `SIZE_LIMIT` 参数化；匿名性检查需人工 |
| G6 引用 | 🔧 换 bst | 🔧 换 style | 🔧 换 bst | 🔧 换 bst | 检查逻辑（bib 机制存在即可）通用，匹配目标替换 |
| G7 伦理 | ❌ 替换为 ethics review 核对 | ❌ 替换为 Ethics Checklist 表单核对 | ❌ 按当年 CFP 语义 | ❌ 替换为 Code of Ethics / 伦理声明核对 | Broader Impact 节检查是 **TMLR 语义**，不得原样套用 |
| G8 表单 | 🔧 重做清单 | 🔧 重做清单（含 Ethics Checklist、lay summary） | 🔧 重做清单 | 🔧 重做清单（ARR commitment 流程不同） | 各会 OpenReview 字段不同；沿用 init_paper.py 下发清单的模式，逐会定制 |
| G9 重叠 | ✅ 复用 | ✅ 复用 | ✅ 复用 | ✅ 复用 | venue 无关的原创性审计 |
| G10 双盲隔离 | ✅ 复用 | ✅ 复用 | ✅ 复用 | ✅ 复用 | venue 无关 |
| G11 门+哈希 | ✅ 复用 | ✅ 复用 | ✅ 复用 | ✅ 复用 | run_acceptance_gates.py / build_evidence_manifest.py 通用 |
| EXTRA 占位符/± | ✅ 复用 | ✅ 复用 | ✅ 复用 | ✅ 复用 | venue 无关 |

图例：✅ 直接复用（零改动）｜🔧 逻辑复用、参数/白名单/目标替换｜❌ 语义不兼容，需替换或新增检查。

## 5. venue 适配最小流程（人工或后续自动化改造）

1. **复制**：`scripts/check_tmlr_compliance.py` → `scripts/check_<venue>_compliance.py`（或先做参数化：把 `TMLR_PKG_RE`、反例 class 正则、`BIBSTYLE_RE`、`SIZE_LIMIT`、`ALLOWED_URL_MARKERS`、G7 语义提为 CLI 参数/配置文件，一份脚本多 venue 复用）。
2. **调整模板/命名规则**：按 §3 表替换——包名正则（cvpr / neurips_2025 / icml2025 / acl）、bst 匹配目标、补充材料阈值、匿名仓库白名单；G7 按 venue 语义重写（如 NeurIPS 改为核对 Ethics Checklist 表单项，CVPR 改为核对 ethics review 声明）。
3. **本地夹具回归**：在 `assets/scanner_fixtures/` 下按 venue 建 `clean/`（无假阳性对照）与 `dirty/`（该 venue 专属失败类）夹具，沿用 number-consistency 的 clean/dirty 模式；`scanner_regression.py` 目前只回归 number-consistency / stats-consistency 两个目录，新夹具要么扩展该脚本、要么至少用 `--exit-zero` 跑一遍新脚本确认「dirty 必报、clean 不报」。
4. **人工兜底**：G2/G5 匿名性/G8/G9/G10 不自动化，按 §2 清单人工核对；每次投稿季重跑官网核对（§7）。
5. **记录**：每个 venue 适配的改动与回归结果记入论文包 ROUND 报告与 GATES，便于下次复用。

## 6. 信息来源（各会议官网 submission 页；投稿前以此为准）

- **TMLR**：Author Guide <https://jmlr.org/tmlr/author-guide.html> ｜ Submission Instructions <https://jmlr.org/tmlr/submissions.html> ｜ Editorial Policies <https://jmlr.org/tmlr/editorial-policies.html> ｜ 风格文件仓库 JmlrOrg/tmlr-style-file（本技能 templates/tmlr/ 即来源于此）
- **CVPR**：2025 Author Guidelines <https://cvpr.thecvf.com/Conferences/2025/AuthorGuidelines> ｜ Call for Papers <https://cvpr.thecvf.com/Conferences/2025/CallForPapers> ｜ 模板 author-kit（cvpr-org/author-kit）
- **NeurIPS**：Call for Papers 2025 <https://neurips.cc/Conferences/2025/CallForPapers> ｜ 风格文件页面（NeurIPS 官网 PaperInformation/StyleFiles，随年份更新）
- **ICML**：ICML 2025 Call for Papers <https://icml.cc/Conferences/2025/CallForPapers> ｜ Author Instructions（camera-ready）<https://icml.cc/Conferences/2025/AuthorInstructions>
- **AAAI**：当年 CFP（如 AAAI-26 <https://aaai.org/conference/aaai/>，URL 随年份变）｜ Author Kit 下载页（aaai.org → Authors，许可禁止再分发）｜ 生成式 AI 披露条款以当年 CFP 正文为准
- **ACL**：ACL Rolling Review CFP <http://aclrollingreview.org/cfp> ｜ ACL 官方 portal <https://www.aclweb.org/portal/content/acl-rolling-review> ｜ 当年主会页面（如 <https://2025.aclweb.org>）与 ACL Style Files（acl-org/ACLPUB 风格包）

## 7. 遗留风险

- **规则每年变化**：页数上限、补充材料体积、匿名化表述、rebuttal 窗口、伦理要求逐年调整；本表为快照，**投稿季前必须逐一打开 §6 官网核对当年数值与选项名**（例如各年 style 文件名 `neurips_2025.sty` / `icml2025.sty` 随年份变化，正则目标需同步）。
- **本表未写死的单元格**（如 ACL 补充材料上限、ICML 伦理表述）是有意留白，勿凭经验补值。
- **check_tmlr_compliance.py 的 TMLR 专属硬编码**一旦被误用于其他 venue，会产生假阳/假阴（如 G1 报「无 tmlr 包」、G7 报「无 Broader Impact 节」）；适配前先确认脚本参数化状态。
- 自动化扩展（把脚本真正参数化、夹具回归入 scanner_regression.py）属于后续审计项，本 L3-2 只交付文档与映射流程。
