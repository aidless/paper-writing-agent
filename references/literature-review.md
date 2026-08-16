# 文献综述工作流（D0 阶段）

对应 research-cycle 的 **D0 文献综述**：在研究设计（D1）之前完成，
输出物直接喂养 Related Work、Introduction 的 GAP 陈述，以及 claim ledger
中的"据我们所知"类声明。

## 目标

1. 定位研究空白（GAP）：一句话说清"已有方法能做到什么、不能做到什么"。
2. 建立基线池（baseline pool）：后续实验要对比哪些方法，提前列全。
3. 识别数据集/指标惯例：该方向默认评测集与评估协议（避免 D3 阶段才发现指标口径不对）。
4. 为 claim ledger 的 novelty 声明提供文献支撑：任何"首次/优于/不同于"声明必须有可核验的引用。

## 流程

### L1 检索（两条腿）

- **工具检索**：web_search（按关键词 + 年份过滤）；arXiv API（`http://export.arxiv.org/api/query?search_query=...`）；Semantic Scholar / Google Scholar 兜底。
- **引文滚雪球**：从 2-3 篇最相关综述或高引论文出发，forward/backward citation 各一层——这是 Modex 等工具常见的盲区，人工判断才可靠。

每篇候选文献记录：标题 / 作者 / 年份 / venue / 链接 / 一句话贡献 / 与本研究的相关性（强相关 / 相关 / 背景）。

### L2 归纳（结构优先）

按以下维度聚类（不要按时间线流水账）：

1. **方法族**：后处理校准（温度缩放/保序/分箱）vs 训练内方法（正则/损失/集成）——按方法机制分组。
2. **能力边界**：每族方法适用条件、已知失败模式（OOD？小样本？）。
3. **评测协议**：数据集、指标（ECE/Brier/NLL）、种子数惯例、显著性检验惯例。
4. **声明缺口**：哪些结论有证据、哪些只是主张、哪些方向没人做过。

输出为**比较表格**（行=方法，列=机制/适用条件/评测/已知缺陷），不是散文。

### L3 空白定位

从归纳表出发写 GAP 陈述，必须满足：

- **可证伪**："后处理方法不改表征，因此训练内方法有独立价值" ✓；"后处理不够好" ✗（太模糊）。
- **与本研究动作一一对应**：GAP 的每个子句都要在 Methods 里有对应设计。

### L4 输出物

`LITERATURE_REVIEW.md`（论文根目录）：

```
# LITERATURE_REVIEW.md
- 检索式与日期（可复现检索）
- 文献池：编号 L01..Ln + 一句话贡献 + 链接
- 方法族归纳表
- 评测协议惯例
- GAP 陈述（3-5 句，逐条可证伪）
- 基线池清单（D1/D3 要用的对比方法）
- "据我们所知/首次"类候选声明（进入 claim ledger 时须附文献条目）
```

## 与 claim ledger 的衔接（硬规则）

- Related Work / Introduction 中的"相比已有方法"声明 = **比较声明**，必须挂 ledger 条目：
  `LITERATURE_REVIEW.md -> 基线池.X.能力边界`，或直接引用文献编号。
- 找不到文献支撑的 novelty 声明：删除或降级为 "we are not aware of ..."（hedging）。
- 文献综述本身不是证据包：它支撑的是**定位**声明，不支撑**实验数字**声明
  （实验数字仍必须来自 results/*.json）。

## 质量检查

- [ ] 每个 GAP 子句可证伪且对应一个 Methods 设计
- [ ] 基线池包含所有实验里出现的对比方法
- [ ] 指标/数据集/种子数惯例与 protocol.md 一致
- [ ] 所有"首次/最优/不同于"声明可回溯到具体文献
- [ ] LITERATURE_REVIEW.md 已随 evidence_manifest 哈希入账

## 新鲜度门禁（投稿前, L2-3）

文献综述是"低频稳定"资产: 立项到投稿之间 arXiv 可能已出现新工作,
`LITERATURE_REVIEW.md` 越旧, 其中的"首次/优于/不同于"定位越可能过时。
投稿（Phase 5）前必须重跑一次相关文献增量门:

1. **跑新鲜度检查**（门禁命令, exit 1 = 阻塞 Phase 5）:

```
python scripts/check_literature_freshness.py <paper_dir> \
    --claims-file <novelty_claims.txt> --max-age-days 30 \
    --out reports/literature_freshness.md --fail-on-stale
```

   `LITERATURE_REVIEW.md` 的真实 mtime 距今天数达到 `--max-age-days`
   （默认 30 天）即 `Stale=1`; 文件缺失即 `Missing=1`。报告含族内机器
   可读行 `## 段落: <计数>`（综述非空段落数）与 `Missing / Age_days /
   Stale / Claims_count / Max_age_days` 字段, 可直接挂门禁断言。
   `--allow-missing` 只豁免"缺失"这一条件（如项目确实不依赖文献定位时
   使用, 报告中仍标 Missing=1）, **不豁免真过期**。`--claims-file` 每行
   一条 novelty 声称, 用于统计本轮复核的声称覆盖数。

2. **过期则重跑 D0 增量扫描**: 按**项目启动时间**过滤 arXiv 新工作
   （arXiv API `search_query` 加 `submittedDate:[<立项日期> TO 99991231]`
   或等价日期区间; `literature_discovery.py` 目前无内置日期参数, 用检索词
   年份下限或查询后按日期过滤）, 只审立项之后的新条目: 方法族是否出现
   新成员、GAP 是否被抢先、基线池是否需要补方法。

3. **与 novelty claim 复核衔接**（硬规则）: 对每条新工作逐条对照
   `--claims-file`（或 CLAIM_LEDGER.md 中"据我们所知/首次"类条目）:

   - 声称仍成立 → 在新鲜度报告中记录"已复核";
   - 被抢先/被削弱 → 改写定位（hedging 或换 GAP）并同步更新
     CLAIM_LEDGER.md 与 ROUND_R*.md, 不能只改正文;
   - 无影响但属强相关 → 补入文献池与 Related Work。

新增检查项（投稿前）:

- [ ] `check_literature_freshness.py --fail-on-stale` exit 0
- [ ] 立项日期之后的新工作已逐条对照 novelty 声称并留痕
