# FINDINGS.md — 跨阶段发现日志（Research + Engineering 双轨）

> **用途**：记录实验/修改/审稿过程中的发现——研究洞见与工程教训。
> 对应 research-cycle 的 D2/D3/D4.5 阶段；**每次实质工作后追加**，session 恢复时
> 先读本文件（比 ROUND_R 修改记录更适合恢复上下文）。
>
> **为什么存在**：实验产生对后续决策关键的发现，但不属于正式实验报告。
> 没有集中日志，发现会在会话间丢失——下个会话重复同样的错误或错过重要信号。

---

# Research Findings（研究洞见）

> 方法级洞见：什么有效、什么无效、为什么。直接影响声明、实验设计、论文叙事。

## [YYYY-MM-DD] 主题
- 发现
- 证据（结果文件/指标/数据集）
- 影响（如何改变声明/设计）

## [YYYY-MM-DD] 示例：合成数据的循环确证
- Phase B Reflector 发现：synthetic 逐种子 ECE 是构造产物，任何"假设被数据支持"都是循环论证
- 证据：generate_data.py 显式 scale 差值到目标均值
- 影响：必须真实训练（Phase A），synthetic 数据只作管线演示

---

# Engineering Findings（工程教训）

> 环境/调试/管线教训。防止未来会话重复调试同样问题。

## [YYYY-MM-DD] 主题
- 问题与根因
- 修复
- 防复发机制（如可执行门/失败模式条目）

## [YYYY-MM-DD] 示例：torchvision download=True 卡顿
- CIFAR10(download=True) 每次构造都检查 tar md5，不匹配就重下 170MB → 训练"卡住"
- 修复：download=False + 预下载数据
- 防复发：FM-29（训练配置即证据）记录此陷阱

---

## 纪律

1. **追加不覆盖**（append-only），每天一段。
2. **Research 与 Engineering 分开**——研究洞见影响科学声明，工程教训影响复现。
3. **链接证据**：每条发现引用具体文件/行号（如 `results/e1.json -> configs.ours_tf`）。
4. **session 恢复先读**：新会话开始工作前，先扫 FINDINGS.md 近 3 天条目。
5. **与 ROUND_R 分工**：ROUND_R = 修改记录（变更/原因/验证）；FINDINGS = 发现日志（洞见/教训/决策）。两者互补。
6. **importance（0-1，可选但推荐）**：每条发现可标注重要性 =
   `min(1, 0.2·连续失败次数 + 0.4·审稿Critical次数 + 0.4·FM命中数)`，
   供 `scripts/retrieve_experience.py` 三因子检索（recency×importance×relevance）排序；
   缺省由检索脚本按 conf/状态推导。要进入检索，FINDINGS 需以结构化 JSONL
   （`{"id","sit","act","importance","date"}`）提供，FINDINGS.md 自由格式需手工转。
