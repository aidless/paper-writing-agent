# Dogfood · 第二次：用本包审计另一个仓（2026-10-04）

> 第一次 dogfood 见 [首篇报告](2026-10-04-dogfood-1-under-review.md)（产出 FM-30）。本次目标：换一个完全不同的稿件域（英文长稿 + 多版本目录 + 已有 review 归档）再看一次门的表现。
> 对象：另一个已公开的研究仓（Python，约 96MB），`papers/` 含 `preprint_unified_en.md`（1624 行）、`COVER_LETTER.md`、`tmlr/`、`reviews/`、`_deprecated/`（5 篇旧稿归档）。

## 跑法

```bash
python3 scripts/scan_number_consistency.py <REPO>/papers
```

## 发现 A：第四类误报——假想值（→ 新规则 hypothetical）

v1.2.0 的 FM-30 修复（dimension / format / structural）在该仓上把 2 条命中中的 1 条正确降级，另一条**未捕获**：

```
- table `0.85` vs prose `0.8499999` @ preprint_unified_en.md:728
  :: order bits    (0.8499999 vs 0.8500001)
```

核实上下文（§6.4 Limitations）：该数字对是**未来压力测试计划要喂进去的近邻值**，不是测量结果：

> 2. **Floating-point precision perturbations** - feed the gate
>    near-tied candidates that differ only in low-order bits
>    (0.8499999 vs 0.8500001) to confirm deterministic behavior.

这是与前三类正交的第四类：**语用角色**——数字在句中的角色是"待检验的示例"还是"已测量的值"。修法：新增 `HYPOTHETICAL_RE`（future / follow-up(s) / planned / will / would / to be / prospective / limitation），命中段落内的近邻配对降级为 `hypothetical` 并照常列出。

> 实现注记：`follow-?up\b` 匹配不到 "follow-ups"（`s` 紧跟使词边界失败）。该稿件原文正是 "Two follow-ups remain"——第一次写规则时漏了，写完立即用真实稿复验才发现。

修后复扫该仓：**0 mismatch / 19 downgrades**；首篇稿件不回归（0 / 5）；真漂移夹具仍报出 1 条。

## 发现 B：双语库静默分叉（→ fm_index 双语化 + 计数门）

`references/failure-modes_EN.md`（EN 版失败模式库）落后 CN 版**两轮**：

1. **脱敏遗漏**：CN 版在 2026-10-04 做了 22 处统计值脱敏，EN 版**一处都没做**——`35.4-37.2%`、`CV=0.218`、`0.398/1.081=0.368`、`W=412, p=0.0021, r=0.531`、`[0.0275,0.0341]`、`0.806→0.807` 等全部以原值留在公开文件里。这正是"公开前脱敏"这一动作本身漏了一半。
2. **FM-30 缺失**：EN 版停在 FM-29，没有协议节、没有 INDEX、没有 FM-30。

`fm_index.py` 因此从"单文件生成器"升级为**双语门**：同时维护 CN/EN 两份 INDEX，并在 `--check` 里断言两者条目数一致（EN=30 与 CN=30）。反证：人为删掉 EN 的 FM-30 条目后 `--check` 立即 exit 1 并同时报 `entry-count drift CN=30 EN=29`。

**教训**：翻译一份纪律性文档时，脱敏/新增/协议三类改动必须成对执行，否则"已脱敏"的结论只在一种语言里成立。本次由 CI 兜住（新增 `fm_index.py --check` 步骤）。

## 发现 C：稿件自带的诚实声明（本包未覆盖，但值得记录）

该仓的 README 与稿件顶部已经自带 pwa 哲学的雏形——"earlier conclusions deprecated by newer analyses"、"do not reuse the superseded `p<0.01` claims"、"the two samples are not directly comparable"。这类**自我作废声明**目前不在本包任何门的覆盖范围内；它靠人工写、靠人守。本包的 stale-marker 门只能查"旧数字是否还在文本里"，查不了"作者有没有写下作废声明"。

→ 记入 §遗留（不实现，等有第二个真实用例再动）。

## 结论

- 门在第二个域的表现：v1.2.0 的三类降级全部生效，新发现一类（语用角色）。**每次换域都能挖出一类新的误报**——这是把 FM-30 的教训再往前推一格的理由。
- 本仓自身的缺陷（本轮修）：双语库分叉 + 脱敏半漏。
- 回归 25 → 27 项全 PASS；`table-prose-dirty` 夹具在每次新增降级规则后都必须继续断言 ≥1 条真 mismatch（本次 40 字符窗口版和 `follow-up` 漏配两次都是被它和真实稿抓到的）。