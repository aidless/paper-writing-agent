# 全科研周期编排（research-writer 预设配套）

从研究问题到 TMLR 投稿的端到端编排。写作只是最后一环：前面每个阶段的产出
（设计、数据、分析）都是写作阶段 evidence package 的输入。任何阶段产出不足，
写作阶段就会在 claim ledger 阶段被阻塞——这是设计使然。

## 阶段门控总览

| 阶段 | 产出 | 出口标准（未达到不得进入下一阶段） |
|---|---|---|
| D0 文献综述 | LITERATURE_REVIEW.md（检索日志/方法族表/GAP/基线池） | GAP 可证伪；基线池齐全；novelty 声明可溯源 |
| D0.5 假设生成 | HYPOTHESES.md（四角色循环候选 + 溯源 + 反例记录） | ≥5 候选；≥2 轮进化；每个候选依据可追溯；无依据标记 exploratory |
| D1 实验设计 | protocol.md（假设/设计/分析计划/排除标准）、预注册记录 | 假设可证伪；分析计划先于数据；功效/样本量已论证 |
| D2 实验执行 | 原始结果 JSON/CSV、seed 记录、环境冻结 | 种子/样本量口径唯一；随机性可复现 |
| D3 数据分析 | 统计报告（检验/效应量/CI/校正）、图表 | 每个统计量可重算；口径不混用 |
| D4 写作 | manuscript + CLAIM_LEDGER.md + evidence_manifest.json | 六扫全过；ledger 全覆盖 |
| D4.5 对抗审稿 | REVIEW_Rn_<role>.md + ROUND_Rn 回应 | 一轮无新 Critical/Major；评分达标 |
| D5 投稿 | 匿名 zip + 合规报告 | G1-G11 全过；哈希对账 |

## D0 文献综述（新论文的第一步）

按需加载：`web_search` 工具 + 引文滚雪球；技能脚本 `literature_discovery.py`
（Elicit 式 arXiv 语义检索）、`citation_network.py`（Scite 式引文关系筛选）、
`consensus_check.py`（Consensus 式证据裁决）、`chat_pdf.py`（SciSpace 式
Chat-with-PDF）。

- 流程见 `references/literature-review.md`：检索 → 归纳（方法族比较表）→ 空白定位（可证伪 GAP）→ 基线池。
- 产出 `LITERATURE_REVIEW.md` 入 evidence manifest；"相比已有工作/首次/最优"声明必须挂 ledger 条目并引用具体文献。
- 用 consensus_check.py 对关键研究问题做证据裁决（YES/NO/MIXED + 强度），
  用 citation_network.py 快速筛查引文关系（支持/矛盾/中性，标注为 screening aid）。

## D0.5 假设生成（对标 Google AI co-scientist，D0 与 D1 之间）

按需加载：`scholar-evaluation`（novelty/significance 排序）。

- 流程见 `references/hypothesis-generation.md`：Generator 发散 → Reflector 批判 →
  Ranker 排序（novelty × feasibility）→ Evolver 进化，≥2 轮。
- 产出 `HYPOTHESES.md`：每候选含可证伪陈述/文献依据（L## 可追溯）/反例风险/
  验证实验设计/预期结果。无依据候选必须标记 exploratory，不得混入 evidence-based 池。
- 采纳的假设最终成为 C 类声明时，claim ledger 必须溯源到 HYPOTHESES.md 条目
  （"预先假设 H03，实验支持"——预注册精神）。

## D1 实验设计（前置，最容易返工）

按需加载：`ablation-design` / `hyperparameter-optimization` / `statistical-analysis` /
`registered-report` / `survey-design`。

- 消融：组件移除 / 特征消融 / 模块替换，一次只变一个因素，避免混淆。
- 统计：先定检验与功效（多少组比较才够？），再定样本量；多重比较校正方案先写进 protocol。
- 预注册：假设/设计/分析计划/排除标准在拿到结果前定稿（OSF/AsPredicted）。
- 因果（如适用）：DAG 先行，区分混杂/中介/对撞，避免把相关当因果。

## D2 实验执行（决定可复现性分数）

按需加载：`reproducibility` / `pytorch` / `data-management`。

- 种子管理：全局种子 + 每配置多 seed；seed 数在 protocol 里定死，事后不得改口径。
- 环境冻结：pip freeze / lock 文件 / Docker；记录硬件与框架版本。
- 数据版本：原始数据只读，派生数据可重建；命名规范与元数据（FAIR）。
- **三级测试金字塔（任何长训练前必须依次通过，评估 P0 整改）**：
  - T1 静态：脚本语法 + 关键函数存在（可重跑检查）
  - T2 学习：1 seed × 少量 epochs 后 acc 显著 > 随机（证明数据/模型/损失管线正确——
    防"训练发散到 acc 0.18 还跑完 60 epochs"这类数小时浪费）
  - T3 产物：run 输出含 cfg.real、概率合法（rowsum=1）、关键指标在合理范围
  - 全量实验只允许由**通过三级测试的脚本版本**启动。
- **不可变运行记录（评估 P0 整改）**：每次运行生成 run ID，绑定代码哈希、数据哈希、
  依赖锁、硬件、命令行参数、随机种子、输出哈希；论文只能引用已封存 run ID 的数据。
- **合成/真实证据物理隔离（评估 P0 整改）**：synthetic 与 real 产物分目录/命名空间，
  任何真实结论页面不得读取 synthetic 结果；异常的中间快照隔离到 `results/broken/`。

## D3 数据分析（决定 soundness 分数）

按需加载：`statistical-analysis` / `model-evaluation` / `meta-analysis` /
`survival-analysis` / `time-series-analysis` / `causal-inference` /
`uncertainty-quantification` / `network-science` / `nlp-text-analysis`。

- 先描述性后推断；每分析报告检验、自由度、效应量、CI：`t(df) = val, p = val, d = val, 95% CI [lo, hi]`。
- 多模型多数据集比较：Friedman + Nemenyi、CD 图、pairwise Wilcoxon。
- 校正：Bonferroni/Holm/FDR，校正方法必须标注。
- 不确定性：calibration、conformal prediction、OOD 检测（如适用）。
- 每个数字在 `reports/` 下留可重跑脚本（Python/R），作为写作阶段的重算源。

## D4 写作（本技能核心）

严格按 SKILL.md 的 Phase 0-5 执行：

0. 新项目一键初始化（骨架 + 匿名 TMLR 模板 + 工作文档）：

   ```
   python scripts/init_paper.py <paper_dir> --title "Title" --round-report
   ```

1. Phase 0 收据：evidence 清单 + SHA-256 manifest + WORKING_NOTES。
2. Phase 1 claim ledger：起草前枚举全部声明，数字逐条映射证据文件+字段。
3. Phase 2 起草：Methods/Results 只从算好的值写，Discussion 次之，Abstract 最后。
4. Phase 3 机器检查：六扫全过（数字 / 统计 / 风格 / TMLR / 账本 / 污染）。
5. Phase 4 修改轮：ROUND_Rn 记录变更，旧验收门保持 PASS。
6. Phase 5 合规：G1-G11 全过 + 重哈希 + manifest 逐字节校验。

**流程纪律（FM-24 教训）**：每次修改任何交付文件（main.tex/main.bib/evidence/脚本）
后，立即重跑 `build_evidence_manifest.py --verify`，不要等到轮次结束才重建清单——
否则清单过期会让审稿人抓到"报告声称 x/x PASS 但哈希失配"的矛盾（R6 实证）。

## D4.5 对抗审稿（投稿前的最后一道人视角关卡）

机器六扫查硬事实，对抗审稿查论证强度。流程见 `references/adversarial-review.md`：

- 7 个独立审稿角色（方法论/统计/实验/新颖性/可复现/写作/伦理）各出一份问题清单；
- 严重度 Critical/Major/Minor/Nit；Critical/Major 只允许"修复"或"证据补齐"，不允许无视；
- 每轮修改后重跑六扫；连续一轮无新 Critical/Major 才收敛；
- 可选的跨模型互审：workflow 工具按角色指定 model 独立审稿，结构化 JSON 汇总；
- 收敛后用 scholar-evaluation 的 TMLR 加权分（0.30N+0.35S+0.25Si+0.10C）做最终自评。

## D5 投稿合规

见 `references/tmlr-compliance.md` 的 G1-G11 清单。TMLR 硬线：

- G1 模板 `\usepackage{tmlr}`（无选项 = 匿名提交版）；G3/G4 匿名化与匿名仓库；
- G9 交叉论文重叠审计；G10 双盲隔离；G11 验收门全 PASS + 哈希对账。

## 全程纪律（写作阶段硬规则的来源）

1. 数字独立可复算：D1-D3 每个统计量都能用交付证据重算，不一致 = 阻塞。
2. 零 claim-data 矛盾：无证据支撑的声明删除或 hedging。
3. 口径唯一：种子数/样本量/统计口径在 protocol 定死后全文一致，跨阶段不得漂移。
4. 中立评分：无新证据不得提分；4 分必须由新证据支撑。
