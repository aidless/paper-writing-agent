# 失败模式库（来自既往修改轮次的真实教训）

每条：编号 | 症状 | 检测 | 修复。

> 注：文中具体统计值已替换为脱敏示例值（保持恒等式与教学结构不变）；症状/检测/修复描述为真实内容。

## FM 入库协议（v1，2026-10-04 起）

新增条目必须遵守，否则索引生成器（`scripts/fm_index.py --check`）会在 CI 拒绝：

1. **编号**：`FM-<N>` 严格递增、永不复用（废弃条目保留编号，正文标注 DEPRECATED）。
2. **格式**：`## FM-<N> <一句话标题>` 起头，正文依次为 `- 症状：` `- 检测：` `- 修复：` 三行（可加 `- 实战：`/`- 元教训：`）。
3. **来源**：必须来自**实际修改轮次**（写明轮次/日期），不接受纯理论推演——本库是教训库不是清单库。
4. **脱敏**：真实论文的统计值必须替换为教学示例值（恒等式与量级关系保持），遵守头部脱敏声明。
5. **索引**：新增后跑 `make fm-index`（或 `python scripts/fm_index.py --write`）重新生成 INDEX 节；CI 用 `--check` 校验同步。

## INDEX（由 scripts/fm_index.py 自动生成，勿手改）

| 编号 | 一句话标题 |
|---|---|
| FM-1 | 旧数字残留（种子数更新后） |
| FM-2 | 统计口径混用 |
| FM-3 | 表格/caption 数字漂移 |
| FM-4 | 倒置 CI / 不可能区间 |
| FM-5 | 双盲身份泄漏 |
| FM-6 | 假/占位仓库链接 |
| FM-7 | 哈希/manifest 失配 |
| FM-8 | 种子数/样本量跨段不一致 |
| FM-9 | 未登记声明 |
| FM-10 | 交叉论文重叠（原创性） |
| FM-11 | 模板/class 错误 |
| FM-12 | 可复现脚本路径问题 |
| FM-13 | 不确定度格式不一致 |
| FM-14 | 超越证据上界的强断言 |
| FM-15 | 统计量三元组不自洽（W/p/r 互相矛盾） |
| FM-16 | 数据生成与分析混在一个脚本（re-centering 掩盖矛盾） |
| FM-17 | 效应量/统计量沿用旧数据（数据重算后未同步） |
| FM-18 | 损失函数项符号与文字描述相反 |
| FM-19 | 引文作者张冠李戴（未核对 arXiv 元数据） |
| FM-20 | 方法核心参数未定义（损失函数不可实例化） |
| FM-21 | 模拟/合成数据零披露（呈现为真实实验） |
| FM-22 | 验证器语义缺陷掩盖漂移（any-match + 宽松容差） |
| FM-23 | "修复轮"自身引入新缺陷（回归） |
| FM-24 | 修改后忘记重建证据清单（manifest 过期） |
| FM-25 | 工具输出不可复现（报告内嵌绝对路径） |
| FM-26 | 报告自引用清单元数据（manifest size 字段） |
| FM-27 | 引文有效性缺失与"虚报完成"（FM-19 的第三、四层） |
| FM-28 | 验证脚手架污染交付态（工具免疫而非流程纪律） |
| FM-29 | 真实实验可复现性缺失（训练配置不是证据） |
| FM-30 | 扫描器把章节号/格式差异当作数值 mismatch（dogfood 首篇发现） |
| FM-31 | 假想值被当作实测漂移（dogfood 2：第二个仓） |
## FM-1 旧数字残留（种子数更新后）
- 症状：摘要/贡献区仍写 8 种子结果（41.2-42.6%），正文已更新为 24 种子（33.7-34.9%）。
- 检测：scan_number_consistency.py --stale 旧值列表 --fail-on-stale。
- 修复：全文 grep 旧值清零，重新跑扫描直至 exit 0。

## FM-2 统计口径混用
- 症状：CV 用了 calibrated 的 sd 配 uncalibrated 的 mean，得到 CV=0.312；正确口径 CV=sd(gTV)/mean(gTV)=0.455/1.173=0.388，导致 CNR 上界从 5.12 虚高到 3.47 之外。
- 检测：对照证据 JSON 逐字段重算；核对公式输入是否同组同口径。
- 修复：统一 group/config 口径后重算并同步全文（含摘要与结论）。

## FM-3 表格/caption 数字漂移
- 症状：表格 8.3/8.9%，caption 或正文出现不一致值。
- 检测：数字一致性扫描的 cross-file 频次表。
- 修复：以证据重算值为唯一事实源，caption/正文/表格统一。

## FM-4 倒置 CI / 不可能区间
- 症状：`[0.91, 0.78]` 这类 lo>hi 的区间。
- 检测：scan_number_consistency.py 的 Inverted confidence intervals 段。
- 修复：回到证据重算上下界，核对符号。

## FM-5 双盲身份泄漏
- 症状：作者/机构/致谢/作者贡献块残留占位或真实姓名；注释里带身份信息。
- 检测：提交前 grep 姓名、单位、邮箱、ORCID、致谢词。
- 修复：作者块中性化（Anonymous），注释一并清理；P1/P2 非双盲占位单独管理。

## FM-6 假/占位仓库链接
- 症状：github.com/Anonymous、fake URL；正文与 protocol.md 口径不一致（真链接 vs available at acceptance）。
- 检测：grep URL 模式 + 跨文件比对。
- 修复：统一为真实匿名仓库或统一 "available at acceptance"，全文+protocol 同步。

## FM-7 哈希/manifest 失配
- 症状：重建 zip 后哈希与 EVIDENCE_UPLOAD_MANIFEST 不一致。
- 检测：run_acceptance_gates.py 的 hash_matches 门；逐包 sha256 对账。
- 修复：重建产物后重新计算哈希并更新 manifest，再跑门。

## FM-8 种子数/样本量跨段不一致
- 症状：摘要 24 种子，结论 8 种子，caption 又不同。
- 检测：扫描数值频次 + 人工核对 N 关键字。
- 修复：确立唯一事实源，全文统一。

## FM-9 未登记声明
- 症状：修改轮新增结论但 CLAIM_LEDGER.md 无对应条目。
- 检测：每轮 diff 对照 ledger；新增声明必须有证据+条目。
- 修复：补证据、补 ledger 条目；无证据则删除或降级为 hedging。

## FM-10 交叉论文重叠（原创性）
- 症状：姊妹论文间 text/figures/results 实质复用（如自称 sister-paper integration 但大段重叠）。
- 检测：逐篇 overlap 比对。
- 修复：去重改写；重叠结果在各自论文中独立呈现并明确边界。

## FM-11 模板/class 错误
- 症状：TMLR 投稿用 jmlr class 而非 tmlr。
- 检测：G1 门检查 preamble。
- 修复：迁移到 article + `\usepackage{tmlr}`（无选项，匿名提交版）+ tmlr.bst，重编译重哈希。

## FM-12 可复现脚本路径问题
- 症状：重跑脚本用绝对路径或跨机器路径，SRC/OUT 未 join BASE。
- 检测：G11 script_runs 门在干净目录跑。
- 修复：脚本内相对路径（SRC/OUT 均 join BASE），包内携带数据。

## FM-13 不确定度格式不一致
- 症状：同一定量描述出现 ±25 through、+/-25、±0.004 混用。
- 检测：扫描 ± 与 +/- 模式。
- 修复：全文统一符号（±）与有效位数，注明来源（如 ±0.003-±0.005 → 显示 ±0.004）。

## FM-14 超越证据上界的强断言
- 症状：结论声称超出可证明上界（如 Conf-Gating 5.12 > CNR 上界 3.47）。
- 检测：claim ledger 值 vs 证据计算上界逐条比对。
- 修复：断言降至证据可支撑范围，或补证据。

---

## 对抗审稿轮次沉淀（FM-15 ~ FM-21）

以下失败模式来自 research-writer 演示论文的多轮对抗审稿（7 角色跨模型互审，
审稿人独立用 scipy/arXiv API/pdftotext 重算重编译核实），每条都是实际发生并
被修复的真实缺陷。

## FM-15 统计量三元组不自洽（W/p/r 互相矛盾）
- 症状：Wilcoxon 报告 W=447, p=0.0038, r=0.478，但审稿人用 W 反推正态近似得
  p≈0.0003——相差一个数量级。p、W、r 不是同一次计算产出，或 W 的约定
  （min(W+,W-) vs W+）未定义。
- 检测：**用交付的逐种子数据独立重算** W/p/r，三者必须能由同一次
  `scipy.stats.wilcoxon` 调用同时导出并互相一致；核对 W 约定与效应量公式。
- 修复：把统计量计算收敛到唯一分析脚本（如 analysis.py），W/p/r 在同一函数
  内产出；证据包携带逐种子原始数据；正文/摘要/ledger 同步。
- 实战：R1 审稿 5 个角色独立发现三元组矛盾（demo 论文），R2 修复后全部角色
  重算确认自洽。

## FM-16 数据生成与分析混在一个脚本（re-centering 掩盖矛盾）
- 症状：analysis 脚本内用 `np.random` 合成"逐种子数据"再 re-center 到硬编码
  均值，导致 mean(d_temp) 与报告均值差不相等（如 -0.0042 vs -0.0117，差 3 倍），
  正文却声称"所有统计量由逐种子数据重算"。
- 检测：配对数据下 **mean(ours) - mean(temp) 必须等于 mean(d_temp)**——用独立
  脚本重算验证；grep analysis 脚本中的 `np.random`/`default_rng` 与 re-center
  模式（`x - x.mean() + const`）。
- 修复：**数据生成与分析职责分离**——generate_data.py 生成原始逐种子数据存入
  npz（含消融独立键），analysis.py 只读重算并在关键恒等式上 assert。
- 实战：R2 审稿 5 个角色独立确认数据矛盾；R3 修复后重算差值 1e-17。

## FM-17 效应量/统计量沿用旧数据（数据重算后未同步）
- 症状：数据修复后 W/p/r 已更新，但 rank-biserial 等衍生统计量仍用旧 W
  计算（如数据更新后 W=41/68，正文 rank-biserial 仍写 0.588/0.577 = 旧 W=94/96
  的结果），且该值不在 analysis.py/e1.json/ledger 中，正文却称"全部由
  analysis.py 重算"。
- 检测：正文每个统计量必须能在 analysis.py 输出中找到对应字段；用当前数据
  按标准公式独立重算；ledger 扫描的"无覆盖正文数字"警告清零。
- 修复：衍生统计量（rank-biserial 等）在 analysis.py 中与 W/p/r 同一次调用
  产出；数据变更后**全量重跑** analysis.py 并同步正文/ledger；把旧值加入
  gates 的 stale-marker 防回归门。
- 实战：R3 审稿 5 个角色交叉确认 rank-biserial 错值；R4 修复为 0.771/0.654。

## FM-18 损失函数项符号与文字描述相反
- 症状：式(1) 写 `−λH·Σp̂logp̂`，但 Σp̂logp̂ = −H(p̂)，最小化损失实际**降低**
  熵、加剧过自信，与正文"entropy penalty guards against overconfident"相反。
- 检测：逐项核对数学恒等式（Σp̂logp̂ = −H(p̂)），确认最小化损失对目标量
  （熵/置信度/校准）的方向与正文描述一致。
- 修复：修正符号（`+λH·Σp̂logp̂`），并在正文补一句恒等式说明；与真实训练
  代码核对。
- 实战：R2 方法论审稿人发现；R3 修复。

## FM-19 引文作者张冠李戴（未核对 arXiv 元数据）
- 症状：main.bib 中作者与 arXiv 元数据不符（如 arXiv 2302.06245 实为
  Linwei Tao et al. 却写成 Gupta et al.；2006.06399 实为 Joo & Chung 却写成
  Karandikar et al.；2106.09385 实为 Singh et al. 却写成 Mukhoti et al.）。
- 检测：**逐条用 arXiv API 实证**（`http://export.arxiv.org/api/query?id_list=...`），
  比对作者/年份/venue；正文引用键与 bib 条目一一对应。
- 修复：按 arXiv 元数据修正 bib 条目与引用键；同步 LITERATURE_REVIEW 文献池。
- 实战：R2 审稿人用 arXiv API 实证抓出 3 处错误；R3 修复。

## FM-20 方法核心参数未定义（损失函数不可实例化）
- 症状：损失函数含温度 T，但全文只有 "T ≥ 1" 无具体取值，λ 给了而 T 缺失；
  读者无法复现训练目标。同类：术语互斥（class-wise vs per-class vs
  single scalar 描述同一组件）。
- 检测：grep 全文/协议/脚本确认每个损失参数都有取值或选择规则；术语全文一致。
- 修复：给出具体取值（如 T=2）与选择口径；统一术语。
- 实战：R2/R3 多个角色确认；R3 修复。

## FM-21 模拟/合成数据零披露（呈现为真实实验）
- 症状：演示/模拟数据在正文以真实训练结果呈现（Setup 断言"We train...24 seeds"），全文 grep simul/synthet/demo 零命中，披露只存在于作者侧文档。
- 检测：grep 稿件目录的模拟披露词；核对证据包数据来源声明是否随稿件可见。
- 修复：Setup/方法段显式披露数据性质；生成脚本 docstring 声明；protocol 补
  数据披露字段；正式投稿前以真实数据替换。
- 实战：R3 伦理审稿人确认零披露；R4 修复（三处披露）。

## FM-22 验证器语义缺陷掩盖漂移（any-match + 宽松容差）
- 症状：验证器对 ledger 声称值采用 any-match 语义（任一声称值匹配任一证据值
  即 PASS）+ 宽松容差（TOL=1e-3），导致声称 CI [0.0183,0.0249] 与证据
  [0.0182,0.0250] 差 1e-4 时仍报 "8/8 PASS"、"23/23 验收门全过"，真实的数据-
  声明矛盾被机器检查掩盖，正文却宣称"全部统计量由脚本重算、逐位一致"。
- 检测：**回归测试验证器本身**——注入一个故意错误的声称值（如把 CI 端点
  改 0.0001），确认验证器 FAIL；检查验证语义是 any-match 还是 all-match、
  容差是否与数值精度匹配（4 位小数 → TOL 应 ≤5e-5）。
- 修复：验证语义改为 **all-match**（每个声称值必须能在证据字段中找到匹配）；
  容差收紧到与有效位数匹配（TOL=5e-5）；把修复后的验证器纳入验收门并在
  每次修改后跑回归测试。同步教训：**验证工具自身的缺陷只能由"验证工具的
  测试"暴露**——对抗审稿的价值不止于抓论文缺陷，还包括抓验证门缺陷。
- 实战：R4 审稿 7 角色发现 ledger 8/8 PASS 与正文 CI≠证据并存，定位到
  verify_claim_ledger.py 的 any-match；R4 修复并回归测试（旧值 FAIL、新值 PASS）。

## FM-23 "修复轮"自身引入新缺陷（回归）
- 症状：为修复上一轮问题而做的修改，反而引入了新的错误——R5 轮实证三个 Major
  全部由"修复"操作引入：(a) 为"舍入一致"把正确的 0.771 改成 0.772（对 4 位中间值
  0.7715 二次舍入的伪影）；(b) 为关闭 G8 数据合规缺口而**编造** "CIFAR-10 MIT
  License（官方声明）"——官方页面实际无任何许可声明；(c) 为补引文而写错 SCO 的
  方法描述（说成"温度缩放+分布惩罚、学习温度"，实际是软分箱校准误差 SB-ECE、
  分箱温度是调优超参）。
- 检测：**每次修改后都重新跑一轮审稿/独立重算**，不要假设上一轮收敛后后续修改
  安全；对修复引入的"新增事实"（许可声明、方法描述、对照声明）用一手来源
  （官网/arXiv 原文）实证；对数值修改做单步舍入核对（禁止对已舍入值再舍入）。
- 修复：修复前先想"这个修复本身会不会引入错误"；新增合规/方法断言必须能溯源到
  一手来源；数值改动后重跑六扫+验收门+manifest 全链；把"修复后必须再审"写入
  revision 协议。
- 实战：R5 审稿 7 角色独立重算抓到 3 个修复引入的 Major（rank-biserial 双重舍入、
  编造 MIT 许可、SCO 描述错误）；R5 修复并全部回退/改证。

## FM-24 修改后忘记重建证据清单（manifest 过期）
- 症状：修改了 main.tex/main.bib 等交付文件并重编译 PDF，但没有重新运行
  build_evidence_manifest.py；审稿人用 `--verify` 实测 31 PASS/3 FAIL，证伪报告中的
  "manifest 与磁盘一致"声明。R6 轮：manifest 建于 04:16，main.tex/bib 于 04:18
  修改、main.pdf 于 04:19 重编译，清单未重建，3 个核心文件哈希失配。
- 检测：**每次修改任何交付文件后立即重跑** `build_evidence_manifest.py <paper_dir>
  --verify`；轮次收尾前核对清单时间戳 ≥ 最后文件修改时间；报告中的 "x/x PASS"
  计数与实际清单条目数一致（R6 还出现报 33/33 实为 34 项的计数错误）。
- 修复：把"修改 → 重建清单 → 重跑六扫"固化为每次编辑后的固定动作序列；清单构建
  不放只在轮次结束时做；计数以 `verify` 实际输出为准。
- 实战：R6 审稿 3+ 角色独立用 `--verify` 抓出 manifest 过期；R6 重建后 36/36 全过。

## FM-25 工具输出不可复现（报告内嵌绝对路径）
- 症状：扫描/验证脚本的报告内嵌绝对路径（如 `Target: <PROJECT_ROOT>\demo-tmlr-paper`、
  `Ledger: <PROJECT_ROOT>\...\CLAIM_LEDGER.md`），导致"按标准流程重跑六扫"这一动作
  本身就会改变 reports 字节——即使每次都记得重建 manifest，FM-24 门也会反复
  失效（R6/R8/R9/R10 四次，前几轮只归因于"忘记重建清单"，未触及路径相关性）。
- 检测：报告头部是否含绝对路径；**从不同 cwd 运行同一扫描，报告哈希是否一致**
  （不一致 = 不可复现）；`--verify` 中 reports/*.md 是否随重跑失配。
- 修复：脚本报告路径统一渲染为**相对目标 root 的形式**（`show()` 辅助函数：
  Target 用 root 名，文件路径用 `relative_to(root).as_posix()`），使报告与调用
  cwd 无关、字节可复现；修复后从绝对/相对 cwd 各跑一次验证哈希一致。
- 实战：R12 审稿方法论角色指出根因；R12 修复 4 个技能脚本后，从不同 cwd 运行
  扫描哈希完全一致，FM-24 门稳定通过。
- 元教训：**可复现性要从工具层面保证，不能只靠流程纪律**——让工具输出本身
  可复现，比让流程参与者记得纪律更可靠。

## FM-26 报告自引用清单元数据（manifest size 字段）
- 症状：扫描器把 evidence_manifest.json 当作"证据 JSON"读取，其 size/modified
  字段被纳入 evidence-only 值集——reports/numbers.md 内嵌自身文件大小
  （如 1215/3003），manifest 重建后记录 1217/3017，报告永远比清单旧一代，
  单遍"重扫→重建"流程永不收敛。这是 FM-24 六次失效（R6/R8/R9/R10/R11/R12）
  的**最终根因**——前几轮只归因于"忘记重建清单"或"绝对路径"，R14 重跑六扫
  也只是创可贴。
- 检测：报告中的 evidence-only 值集是否含 manifest 的 size 数值（如
  `1215.0000`、`3003.0000`）；**重跑扫描→重建 manifest→再重跑扫描**，两次报告
  哈希是否一致（不一致 = 自引用未除）。
- 修复：扫描器**排除 evidence_manifest.json 自身**（它是过程元数据，不是实验
  证据）——工具输出必须只依赖 results/*.json 证据，不依赖清单元数据；修复后
  报告成为规范工作流的数学固定点（重扫后字节不变、manifest 门无需重建仍绿）。
- 实战：R12 审稿多角色确认自指依赖；R15 修复后固定点验证通过（重扫哈希一致、
  门无需重建仍 25/25）。
- 元教训：**报告不能自引用清单元数据**——工具输出只依赖实验证据，不依赖过程
  元数据；这是 FM-25"工具输出可复现"的边界条件。

## FM-27 引文有效性缺失与"虚报完成"（FM-19 的第三、四层）
- 症状：三层引文缺陷：(a) **结果有效性未核**——被引论文作者已自注"证明假设错误
  致结果失效"（singh2021，arXiv 2106.09385 v3 comment），历轮只核验标题/作者
  从未标记有效性，仍被用作支撑引文，直至 R18/R19 审稿用 comment 字段实证；
  (b) **标题虚构**——补引文时 arXiv API 不可用就凭记忆写标题（MMCE/AvUC，
  R23 引入，R17 用 PMLR/arXiv 实证抓出）；(c) **移除不完整**——同一引文键出现
  两处（Introduction + Related Work），只删一处就标 done，PDF 实测仍含该条目
  （R25→R26）。伴生模式："虚报完成"——变更日志标 done 但实际未落地（R24 protocol
  哈希大小写不匹配致替换未生效；R25 引文只删一处）。
- 检测：(a) 用 arXiv API 查 comment/withdrawn 字段，检索 arXiv/PMRL/Crossref 核验
  标题与作者；(b) **全文 grep 引文键确认零残留**（`grep singh2021 main.tex`）；
  (c) 重编译后用 pdftotext 核对参考文献条数与具体条目（`pdftotext | grep Singh`）；
  (d) 变更日志"done"状态必须对应文件实际变更（重跑验证，不只看替换命令是否执行）。
- 修复：补引文必须一手来源核实（标题/作者/venue/年份/有效性）；文献池与 main.bib
  标注"支撑引文 vs 历史记录"（失效文献保留记录但不作支撑）；删除类操作必须
  **全文 grep 零残留 + 重编译核对产物**后才标 done。
- 实战：R17 抓出 MMCE/AvUC 标题虚构；R18 抓出 singh2021 失效未标记；R19 抓出
  Introduction 残留（R25 只删一处）；R26 全量落地（16 条支撑引文无 Singh）。
- 元教训：**引文有效性是 FM-19 的第三层**（标题真实 → 作者正确 → 结果有效）；
  **"声称 done"必须验证实际落地**——修复后重跑验证，不能只更新变更日志。

## FM-28 验证脚手架污染交付态（工具免疫而非流程纪律）
- 症状：并发/历史审稿或验证进程在仓库根目录内创建脚手架目录（.r21_verify_backup/、
  tmp_r21_fixedpoint/、.compile_check/、verify_probe_dir 等）并覆写 reports/*.md、
  在 paper/ 内就地编译残留 aux 产物——导致 FM-24 门 FAIL（25/25 变 24/25）、
  manifest verify 报 3 FAIL + 13~30 WARN。R9/R11/R21 三次出现，前两次仅靠
  "清理→重扫→重建 manifest"机械恢复（流程纪律），本次（R38）从工具层面根治。
- 检测：manifest verify 的 WARN 是否含 .r*/tmp_*/.verify*/verify_* 目录；
  扫描报告（text files 计数）是否随仓库内临时目录增删而漂移；
  FM-24 门在无人改动稿件时 FAIL。
- 修复：**扫描器与 manifest 构建器内置验证脚手架免疫**——排除 `.r*`、`tmp_r*`、
  `.tmp_*`、`.verify*`、`.review_*`、`.compile*` 前缀及 `_verify`/`_check`/
  `_backup`/`_fixedpoint`/`_rebuild`/`_compile` 后缀的目录（注意 `verify_` 前缀
  只匹配目录不匹配文件，避免误伤 scripts/verify_claim_ledger.py 这类合法文件）。
  工具免疫后，任何验证活动都不能再污染 reports/ 或 manifest。
- 实战：R9/R11/R21 三次污染（流程恢复）；R38 工具免疫验证（探针目录被排除、
  合法 verify 脚本仍入册）。
- 元教训：**反复出现的环境问题应升级为工具防护**——"验证别把脚手架放仓库里"
  是流程纪律，总会被违反；"扫描器对脚手架目录免疫"是工具防护，不会被违反。

## FM-29 真实实验可复现性缺失（训练配置不是证据）
- 症状：用真实训练替换模拟数据后，可复现性从"重算统计量"降级为"重训模型"——
  若训练脚本不内嵌配置（种子/epochs/优化器/损失系数/数据增广）、不输出 cfg 快照、
  不记录 GPU 环境（torch+cu 版本），审稿人无法验证任何数字；种子数缩减不披露
  则统计功效被静默削弱（Phase A 实测：RTX 3060 上 200 epochs ≈ 10.6 小时/模型，
  24 种子×4 配置不可行 → 5 种子×4 配置×100 epochs ≈ 1.6 小时）。
- 检测：train 脚本是否有 `--seeds`/`--epochs` 参数且输出 cfg 快照到结果文件；
  protocol 是否披露种子数缩减与 GPU 环境；重训同一命令产物哈希是否一致。
- 修复：训练脚本内嵌全部配置并输出 cfg 字段（seeds/epochs/device/T/λ/ECE bins/
  real:true）；种子缩减必须显式披露（"5 种子，正式投稿应扩至 30"）；
  torch+cu 版本记入 protocol 与 requirements（FM-22）；resume 逻辑按 npz 实际
  保存的 key 恢复（不是按臆想 key）。
- 实战：Phase A（R36+）：预算基准 → 种子缩减披露 → cfg 快照 → resume 修复。
- 元教训：**训练配置即证据**——模型输出不可复现时，数字再漂亮也不是证据；
  预算约束必须披露而不是隐藏（诚实降级 > 伪造完整）。

## FM-30 扫描器把章节号/格式差异当作数值 mismatch（dogfood 首篇发现）
- 症状：scan_number_consistency 的 Table-vs-prose 段把 `### 3.1 Setup`（章节号）、`{+}0.068` vs `0.068`（正负号呈现）、`1.00` vs `1.0%`（**跨量纲误配对**：PCI 倍数列 ×1.00 vs 百分比 1.0%）判为 mismatch——dogfood 首篇 5/5 命中全为误报，稿件实无漂移。
- 检测：mismatch 行上下文若为 `### \d+\.\d+` 标题模式、或两侧数值解析相等（仅符号/小数位差异），归为 format-only；两侧带不同量纲记号（`\times$` vs `%`）则整对作废；复核记录 2026-10-04（首篇稿件：初判 2 真实 + 3 误报，二次量纲核对后 5/5 全误报——**初判也会错，mismatch 必须逐对看量纲**）。
- 修复：读报告先分类 numeric-real vs format-only（数值真漂移才改稿）；格式类统一口径（百分比小数位、Δ 正负号）；长期修复=扫描器加 format-only 分类（equal(parse) 时降级为 INFO）。
- 元教训：**扫描器的误报率决定它的可信度**——把格式差异报成 mismatch，会让使用者学会忽略整段报告；分类比全报更有价值。

## FM-31 假想值被当作实测漂移（dogfood 2：第二个仓）
- 症状：table-vs-prose 门把 Limitations 段里"未来压力测试将要喂进去的近邻值对"当成测量值配对。该仓稿件 `preprint_unified_en.md:728` 写作 `feed the gate near-tied candidates ... (0.8499999 vs 0.8500001)`，表格阈值列有 `0.85`，于是被判 drift——实际数字在句中的角色是**待检验的示例**，不是已测量的值。
- 检测：段落内出现前瞻性措辞（future / follow-up(s) / planned / will / would / to be / prospective / limitation / future work）时，该段内的近邻配对属于假想语境。夹具 `hypothetical-false-positive` 锁定（期望 0 mismatch / 2 downgrades）。
- 修复：`HYPOTHETICAL_RE` 命中段落时降级为 `hypothetical`，与其他降级一样进 `Format/dimension downgrades` 段并附理由。实现注记：`follow-?up\b` 匹配不到 "follow-ups"（`s` 紧跟使词边界失败）——该稿原文正是 "Two follow-ups remain"，规则写完必须用真实稿复验。
- 元教训：**语用角色是与量纲正交的一维**。前四类（dimension/format/structural/hypothetical）都在问"这两个数字是什么"，这一类问"它们在这个句子里扮演什么角色"。换稿件域就是新的误报来源——dogfood 首篇挖出前三类，第二篇挖出第四类。
