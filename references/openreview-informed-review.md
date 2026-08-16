# OpenReview-Informed Review(用真实评审方法学喂给审稿与 rebuttal,O1)

> 来源: openreview-mcp(OpenReview 的 MCP 服务:评审/元评审/rebuttal/决策 + 弱点聚类)
> 目的: 对抗审稿前了解"目标 venue 到底因什么拒稿",rebuttal 用真实评审语言校准。
> 降级: openreview-mcp 未安装时,本节退化为纯方法指导(第 4 节),不阻塞流程。

## 1. 为什么

论文写作 agent 的对抗审稿是自己人审自己人——容易漏掉"该 venue 审稿人真正在意的
模式"。OpenReview 上有大量真实评审/元评审/rebuttal/决策信号:
- **拒稿弱点聚类**: 某 venue/年所有 rejections 的 weakness 主题聚类 → "这个会
  审稿人常因什么拒稿";
- **评审语言**: 真实审稿人的措辞/关注点,用于校准我们自己的审稿焦点与 rebuttal 语气。

## 2. 关键工具(openreview-mcp)

| 工具 | 用途(对本 agent) |
|---|---|
| `openreview_list_venues` / `venue_stats` | 选目标 venue 与年份;看接受率与分数分布(定位拒稿基线) |
| `openreview_search_submissions` / `get_submission` | 检索同类工作,核对 novelty 定位 |
| `openreview_get_reviews` / `get_meta_review` / `get_rebuttal` | 真实评审/AC 决策/rebuttal 范例(语言与关注点校准) |
| `openreview_aggregate_weaknesses` | **聚类目标 venue 拒稿弱点**(k 簇 + 代表片段)→ 投稿前预检清单 |

## 3. 接入点(与既有机制接线)

### 3.1 对抗审稿前(Phase 4.5 开头)
1. 选定目标 venue + 最近 1-2 年;
2. 跑 `openreview_aggregate_weaknesses`(如 "Cluster 50 rejected ICLR 2024 submissions
   by weakness theme, k=10"),得到该 venue 拒稿弱点簇;
3. 把弱点清单并入审稿焦点:8 角色各自的 focus 增加"对照该 venue 常见拒稿模式";
4. 作者侧预检:手稿是否踩中高频弱点(如"消融不完整/缺乏与 X 的对比/表述越界"）。

### 3.2 rebuttal 阶段(writing-style 的 rebuttal 结构)
- 用 `openreview_get_reviews` 取同类论文的真实评审 → 校准回应语气
  (逐条回应、先承认再证据、避免情绪化);
- 用 `openreview_get_meta_review` 了解 AC 决策模式(哪些反驳有效);
- 用 `openreview_get_rebuttal` 看成功 rebuttal 范例的结构。

### 3.3 rebuttal 模拟评测(τ-bench 两阶段,C3)
投稿前对 rebuttal 草稿做一次**模拟审稿人交互**评测(τ-bench, arXiv 2404.04442 思想):

1. **模拟审稿人**: 用真实评审(3.2 取到)或弱点聚类生成 3-5 个追问(含
   "证据不足?""表述是否越界?""重算看看?"三类);
2. **两阶段判定**:
   - 完成度(completion): 每条追问是否得到直接、有证据的回应(未回避);
   - 满意度(consultation): 模拟审稿人是否接受该回应(可用 judge 双判评分);
3. **报告**: 完成度与满意度分开报(两阶段正交,不单指标混报);满意度低 →
   回 Phase 4 补证据或收紧表述,再重跑模拟;
4. 通过标准: 全部追问完成度=1 且满意度 ≥ 阈值;未过 → rebuttal 不进 Phase 5。

### 3.3 元评审研究(可选,研究向)
- `openreview_venue_stats` + 弱点聚类可支撑"该 venue 审稿趋势"的 meta-review 分析,
  与 scholar-evaluation 的评审一致性研究衔接。

## 4. 降级模式(openreview-mcp 未安装)

按以下人工/工具化替代执行,不阻塞投稿流程:
- 弱点聚类 → 用 `references/failure-modes.md`(FM-15..29 实战库)作为第一版
  "该流程已知拒稿模式"清单;
- 评审语言 → 用上一轮 `REVIEW_R{n-1}*` 的真实问题与回应作为校准样本;
- 决策模式 → 用 `SELF_ASSESSMENT.md` 与 `ROUND_R{n}.md` 的历史收敛数据。

## 5. 纪律

- 引用真实评审数据时注明来源(venue/年份/工具调用),不虚构具体论文的评审内容;
- 弱点聚类是"概率性信号",不是"该稿必拒清单"——只用于聚焦,不用于自我否定;
- 安装方式(供参考): `pip install openreview-mcp`,Claude Code 用
  `claude mcp add openreview -- openreview-mcp`。
