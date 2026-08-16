# TMLR 合规标准（写作侧内置标准）

写作质量的唯一裁判尺度 = TMLR 官方标准（Author Guide / Formatting Instructions / Editorial Policies）。
本文件是审稿侧标准的作者侧镜像：写出来的稿子必须能通过审稿侧全部验收门。

## 1. 录用决策 = 回答 TMLR 官方两问

1. **Are the claims made in the submission supported by accurate, convincing and clear evidence?**
   —— 对应：数字独立可复算 + 证据链逐条对账 + claim ledger。
2. **Would at least some individuals in TMLR's audience be interested in knowing the findings of this paper?**
   —— 对应：Significance 评分与受众判断。

## 2. 四维评分（作者自评时使用同一把尺子）

| 维度 | 含义 |
|---|---|
| N = Novelty | 对既有工作的新贡献；不得仅重实现已有想法 |
| S = Soundness | 统计与实验设计的正确性；数字可复算 |
| Si = Significance | 结论对受众的重要性；由新证据支撑 |
| C = Clarity | 写作清晰、可读、无残留 |

加权分 = 0.30N + 0.35S + 0.25Si + 0.10C（满分 5）。
阈值：>=4.0 Strong Accept；3.5-3.9 Accept（阈值线）；3.0-3.4 Weak Accept；<3.0 Major/Reject。

**中性评分纪律**：无新证据支撑不得给 N/Si=4；绝不通过改分数代替补证据。

## 3. 高质量硬规则（违反 = 阻塞项）

1. 数字独立可复算：正文每个关键统计量都能用交付证据重算（t/p/d、校正、CI、效应量）。重算不一致 = 阻塞。
2. 证据链逐条对账：论文对 evidence package 的每个声明必须与实际文件、哈希、manifest 一致；声明无交付物 = 阻塞。
3. 零 claim-data 矛盾：任何"论文结论 vs 交付数据"冲突必须在闭环后才允许交付。
4. 残差扫描：旧数字、强结论残留、mock/占位声明、`???`、跨包账本不一致，逐项 grep 计数。
5. 验收门脚本化：每轮验收门写成可重跑脚本，exit 0 = 全部 PASS；含 zip 独立编译与哈希对账。
6. 中立评价：只依据交付证据与冻结协议评价；分数不通融。

## 4. TMLR 投稿合规门（G1-G11，提交前必须全过）

| 门 | 检查项 | 写作侧动作 |
|---|---|---|
| G1 | 模板 `\usepackage{tmlr}`（**无选项** = 匿名提交版） | 提交版必须无选项：`[accepted]` 仅供 camera-ready，`[preprint]` 会去匿名化（仅供预印本服务器），两者出现在提交版 = 拒绝 |
| G2 | US Letter + pdflatex 生成 | 编译参数核对 + 重编译重哈希 |
| G3 | 全文匿名：作者/机构/致谢/作者贡献 | 提交前 grep 复扫 + 注释中性化 |
| G4 | 匿名仓库：真链接或统一 "available at acceptance" | 全文 + protocol.md 统一口径 |
| G5 | 补充材料 <=100MB、匿名、PDF/ZIP | 打包后复核大小与内容 |
| G6 | 引用格式一致（tmlr.bst） | 编译检查 bib 输出 |
| G7 | Broader Impact（如适用） | 存在且措辞恰当 |
| G8 | OpenReview 表单：profiles/COI/AE 建议/funding/IRB | 作者侧填写核对清单 |
| G9 | 交叉论文重叠审计（原创性） | 逐篇比对 text/figures/results |
| G10 | 预印本与提交版双盲隔离 | 双盲版不含任何身份线索 |
| G11 | 验收门全 PASS + 哈希对账 | 运行 run_acceptance_gates.py + manifest 校验 |

## 5. Strong Accept 门槛（写作目标参考）

- 加权总分 >=4.0 且至少一个非 S 维度 = 4，且该 4 分由**新证据**支撑（不接受仅改分）。
- 全部既有验收门继续 PASS；新证据必须进入 evidence + manifest + freeze（哈希）。
- 论文不得新增任何未经 claim ledger 登记的声明。
- 若证据无法支撑 4 分维度，如实说明缺什么、补什么可达 4 分。

## 6. 输出与归档

- 每轮写作/修改产物落盘到论文包目录，附版本号与日期。
- 交付物必须包含：manuscript + evidence package + evidence_manifest.json + 验收门报告 + CLAIM_LEDGER.md。

## 7. Venue 参数化（L3-2）

- **TMLR 是默认/唯一自动化覆盖目标**：本文件 G1-G11 与 `scripts/check_tmlr_compliance.py` 均以 TMLR 为准（脚本硬编码 `\usepackage{tmlr}` 无选项、tmlr.bst、100MB 阈值、TMLR 匿名仓库白名单、Broader Impact 语义），只对 TMLR 投稿有效。
- **其他 venue（CVPR / NeurIPS / ICML / ACL）走映射流程**：当前不做自动化扫描，须人工按 [venue-mapping.md](venue-mapping.md) 核对——该表给出各维度差异（模板/匿名化/页数/补充材料/参考文献/rebuttal/author 块/伦理声明）、G 级可复用性矩阵（哪些 G 可直接复用、哪些需替换参数、哪些需新增检查）与 venue 适配最小流程（复制检查 → 调整模板/命名规则 → 本地夹具回归）。
- **使用顺序**：新论文先按 TMLR 基线过 G1-G11；只有确定转投其他 venue 时才启用映射流程，且投稿季前必须回各会议官网核对当年规则（链接见 venue-mapping.md §6）。