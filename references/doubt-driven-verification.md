# Doubt-Driven Verification(claim 对抗式验证协议,B1)

> 来源: agent-skills 的 doubt-driven-development(CLAIM→EXTRACT→DOUBT→RECONCILE→STOP)
> 与 evidence-states.md 的分层互补:evidence-states 管"证据有没有科学资格",
> 本协议管"每条 claim 是否真的被证据支撑"——用**新鲜上下文**对抗验证,而非自报。
> 可跨模型升级:DOUBT 阶段换一个模型/视角做质疑者,防止"作者自证"。
> A1(2026-08): 补 CRITIC(arXiv:2305.11738)式**外部工具验证**环——自纠错必须
> 过外部工具验证(重算/查证/执行),不只模型内省。

## 六步协议(每条 claim 都走一遍)

```
CLAIM -> EXTRACT -> DOUBT -> VERIFY -> RECONCILE -> STOP
```

1. **CLAIM**:从 `CLAIM_LEDGER.md` 取一条待验证声明(含正文定位、证据文件+字段)。
2. **EXTRACT(新鲜上下文)**:**不依赖写作时的记忆/缓存**,重新打开证据源
   (evidence_manifest 对应文件 + 独立重算脚本输出),抽取支持该声明的具体内容。
   抽取结果必须自带出处(文件路径 + 行/字段/命令输出)。
3. **DOUBT(主动质疑)**:对抽取结果做对抗式审查——
   - 换模型/换视角(如用 flash 质疑 pro 的结论)重新读一遍"声明 ↔ 证据"对;
   - 检查:数字可重算吗?范围声明(该数据集/该设置)有证据吗?"首次/最佳/优于"
     有引文与基线对照吗?有无被截断/被挑选(outcome-selective)的证据?
4. **VERIFY(外部工具验证,CRITIC)**:质疑的落点必须用**外部工具**裁决,而非模型内省——
   - 数字: 独立重算脚本/`verify_claim_ledger.py`(字段存在、数值匹配);
   - 引文: arXiv API/一手来源核验标题、作者、结果有效性(FM-27);
   - 代码/产物: 重跑、重编译、`seal_run` 只读校验;
   - 工具验证失败 = 该 claim 的证据不足,进入 RECONCILE;不允许"模型说可以"替代工具验证。
5. **RECONCILE**:质疑/验证发现的缺口要么补上证据(回到 EXTRACT),要么收紧声明
   (把"普遍成立"改成"在 X 条件下成立");无法 reconcile 的缺口进入 STOP。
6. **STOP**:任何无法 reconcile 的声明**不进正文**——标记为
   `UNRECONCILED`,降级为"待补实验/待补引用",绝不硬凑。

## 与现有机制的接线

| 现有机制 | 本协议的作用 |
|---|---|
| `verify_claim_ledger.py`(机械校验:字段存在、数值匹配) | 前置;过不了先修 |
| evidence-states 封存/只读验证 | EXTRACT 只读 verified bundle,不写不覆盖 |
| 双轴评审(B2) | DOUBT 的结构化落点:数字一致性轴 + 表述忠实轴 |
| gates_config | "无 UNRECONCILED 声明"作为 D4→D5 的退出门 |

## 执行要求

- 每条声明至少一轮 DOUBT;高风险声明(摘要/结论/新颖性)至少两轮(可换模型)。
- DOUBT 的质疑记录进 `REVIEW_*.md` 或专用 `DOUBT_LOG.md`(append-only),供审稿人追溯。
- 验证器/质疑器**只读** verified bundle(与 evidence-states 规则 4 一致);
  任何"证据不足但想保留"的冲动 → 走"收紧声明"而不是"放宽证据"。
- 判定口径:通过 = EXTRACT 有出处 + DOUBT 无未解缺口;任何一条不满足 = 该 claim 未通过。
