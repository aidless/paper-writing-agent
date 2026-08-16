# Context Paging(按证据状态换页,B1,McmGPT)

> 来源: MemGPT(arXiv:2310.08560)"LLM 即操作系统":上下文 = 内存层次,不是无限缓冲。
> 适用: 长论文项目(多轮修改 + 审稿)的上下文管理,防止上下文膨胀与旧轮污染。

## 分层(与你的文件体系对应)

| 层 | 内容 | 对应 |
|---|---|---|
| 工作上下文(内存) | 当前 Phase 状态、本轮 ROUND/REVIEW、待处理的 UNRECONCILED | 会话内 + `ROUND_R{n}.md` 头部 |
| 证据层(热存储) | **verified** 的 evidence bundle、manifest、CLI 检查结果 | `results/verified/`、`evidence_manifest.json` |
| 归档层(冷存储) | 旧轮 ROUND/REVIEW、draft 证据、废弃候选 | `ROUND_R{n-k}*.md`、`results/broken/`、归档目录 |

## 换页规则(每条可执行)

1. **每轮结束归档旧轮**: ROUND_R{n} 完成后,把 R{n-1} 及更早的轮次细节压缩为
   **摘要指针**(一行结论 + 文件路径),移出工作上下文(MemGPT 的 evict);
2. **按证据状态决定驻留**: verified 证据进热存储(检索即得);draft/候选证据
   归档留指针(需要时 recall,不常驻)——draft 不该占用工作上下文;
3. **召回(recall)**: 会话开始或进入新阶段时,按需读回归档层(指针 → 文件),
   不整目录加载;
4. **防膨胀守卫**: 任一阶段的工作上下文超过预算(如 8K token 提示限制)时,
   先归档旧轮摘要再继续——不因上下文膨胀而丢证据;
5. **只读纪律**: 归档层不可写(与 evidence-states 封存一致);指针只增不改。

## 与既有机制的关系

- 与 compaction(会话级)互补: compaction 压"本会话上下文",本协议管
  "跨轮论文项目上下文"(文件层);
- 与 evidence-states 一致: verified 才常驻/引用,broken/tainted 只留审计指针;
- 与 FINDINGS/ROUND 模板一致: 摘要指针 = 轮次报告末尾的"上一轮结论"字段。

## 执行要求

- 每轮结束执行一次"归档 + 更新指针"清单(ROUND 模板的完成判据之一);
- 会话冷接管时: 读最近 MISSION/ROUND 摘要指针 → 按需 recall,不重读全量归档。
