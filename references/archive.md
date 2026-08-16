# 知识归档规范（Sakana 式跨论文复用）

> 借鉴 Sakana AI Scientist 的 "growing archive of knowledge" 设计。
> 目标：把每篇论文/每次实验的**可复用资产**归档，让未来论文/会话站在
> 过去积累的肩膀上——不只是轮次报告（那是单论文审计链），而是跨论文知识库。

## 何时归档（触发条件）

每篇论文完成一个**实质阶段**后归档一次：
- D2 实验配置确定（训练配方/种子/预算决策）
- D3 统计管线可用（分析脚本/口径）
- D4.5 审稿教训（FM 候选）
- D5 交付后（完整配方）

## 归档内容（按类型）

| 类型 | 内容 | 命名 | 示例 |
|---|---|---|---|
| 实验配方 | 训练配置/数据管线/预算决策 | `experiments/<topic>-<date>.md` | `cifar-calibration-20260814.md` |
| 统计管线 | analysis 脚本模式/口径约定 | `statistics/<topic>.md` | `wilcoxon-holm-pipeline.md` |
| 失败教训 | 踩过的坑+修复（FM 候选） | `lessons/<topic>.md` | `torchvision-download-trap.md` |
| 文献笔记 | 领域综述/方法族表 | `literature/<topic>.md` | `calibration-methods.md` |
| 模板 | 可复用文档结构 | `templates/<name>.md` | `experiment-plan-template.md` |

## 目录布局

```
ARCHIVE/
  README.md          # 索引（每类文件一行：路径+一句话）
  experiments/
  statistics/
  lessons/
  literature/
  templates/
```

## 复用协议

1. **新论文开始时**：读 ARCHIVE/README.md → 按需加载 experiments/lessons/templates
2. **复用前验证**：归档资产必须自包含（含环境/版本），用前跑一次冒烟
3. **更新纪律**：复用中发现归档过时 → 更新归档 + 记录日期（不是新建重复文件）

## 与 evidence manifest 的关系

- **ARCHIVE 是跨论文资产，不进单论文的 evidence_manifest.json**
- 单论文 manifest 只含该论文的证据（results/paper/scripts）
- ARCHIVE 在 `F:\deepseek\ARCHIVE\`（项目级，跨 demo 论文）

## 与 FINDINGS / FM 的关系

- FINDINGS.md = 单论文的即时发现日志
- ARCHIVE/lessons/ = 跨论文的沉淀（FINDINGS 中的 Engineering 教训 → 归档 → FM 条目）
- 三者链路：FINDINGS（即时）→ ARCHIVE（跨论文）→ failure-modes.md（技能级 FM）
