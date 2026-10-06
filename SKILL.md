---
name: paper-writing-agent
description: "Evidence-first academic paper writing, revision, and TMLR-compliant submission agent. Use when the user asks to write, draft, revise, polish, or finalize a research paper (论文写作/起草/修改/润色/终稿/投稿准备), respond to reviewer comments (rebuttal letter), prepare supplementary evidence packages, or wants number-consistency scans, claim ledgers, acceptance gates, and TMLR submission compliance checks before delivery."
---

# Paper Writing Agent

## Role

Author-side writing agent. Turn delivered evidence into a high-quality manuscript that clears the TMLR bar: every claim is supported by accurate, convincing, clear evidence, and at least some of TMLR's audience would care about the findings. Never invent or copy numbers; recompute every statistic from the evidence package.

## Research cycle (full scientific cycle)

This skill is the writing core of the full research cycle; it also carries the
cycle's orchestration rules. When the task starts before evidence exists
(experiment design, data analysis, reproducibility), follow
[references/research-cycle.md](references/research-cycle.md) first: its D1-D5
stage gates (design → execution → analysis → writing → submission) define what
each stage must hand over, and the `paper-writing-agent` phases below are D4.
A stage whose exit gate is unmet blocks the next stage by design — for example,
a manuscript whose numbers cannot be recomputed from delivered evidence is a
blocker, not a drafting problem. Load sibling research skills as the cycle's
stages require (ablation-design, statistical-analysis, model-evaluation,
reproducibility, scholar-evaluation, ...); the paper's evidence package is the
single source of truth those skills read from and this skill writes against.

## Workflow

> 每阶段完成判据(可检查)速查: [references/instruction-design.md](references/instruction-design.md)。
> 长论文项目上下文: 按证据状态换页(MemGPT)——[references/context-paging.md](references/context-paging.md)。
> 经验检索: 三因子(新近度×重要性×相关性)——`python scripts/retrieve_experience.py`(Phase 0 步骤 0; 协议见 [references/memory-retrieval.md](references/memory-retrieval.md))。
> 原则: 每条指令回答"我怎么知道这一步做完了";纯否定式禁令改正面表述 + 判据。

### Phase 0 - Intake
0. **会话开始经验检索（三因子，证据门禁）**——接新任务/新会话先跑一次，把相关经验带进上下文：

```
python scripts/retrieve_experience.py --task "<任务目标>" \
    --ledger <.agent-memory/ledger/lessons.md> \
    [--findings <paper_dir>/FINDINGS.jsonl] [--top 5] \
    --out <paper_dir>/EXPERIENCE_DIGEST.md
```

   默认只检索 verified/active 条目（无证据的 draft 不进摘要）；`--include-draft` 仅审计用。
   项目内有结构化 FINDINGS JSONL（`{"id","sit","act","importance","date"}`）时加 `--findings`。
   α 任务类型加权自动生效（knowledge 重相关性、reasoning/防幻觉压相关性抬重要性/新近度）。
   产出 `EXPERIENCE_DIGEST.md` 阅读后进入后续阶段。
0b. **项目切换（N3）**——多项目并行时先确认/切换活动项目，避免跨项目串扰
    （evidence_manifest/gates/账本按项目隔离）：

```
python scripts/switch_project.py list
python scripts/switch_project.py <paper_name>
```

    切换后上下文加载该项目摘要（manifest 文件数/ledger 条目数/最新轮次/
    SELF_ASSESSMENT 存在性）。
1. Bootstrap a new paper project (skeleton + anonymous TMLR template + working docs) in one command:

```
python scripts/init_paper.py <paper_dir> --title "Your Title" --round-report
```

   The generated `paper/main.tex` uses the anonymous `\usepackage{tmlr}` (no option, per official double-blind semantics) with the template's sample author block and camera-ready `\def` lines neutralized, so a fresh project already passes the G1/G3/G4 scans. The bootstrap also lays down a G8 OpenReview form checklist, a protocol.md that bakes in the failure-mode lessons (statistics recomputed from per-seed data by one canonical script, explicit coefficient values, simulated-data disclosure, traceable dataset licensing, real environment lock), and a gates_config.json with anti-regression stale-marker placeholders — so new papers start immune to the FM-15..FM-29 failure modes (including the FM-24 manifest-reconciliation gate and FM-25 reproducible tool output).
2. Run a literature survey FIRST (research cycle D0) when the paper needs Related Work / GAP positioning / a baseline pool: follow [references/literature-review.md](references/literature-review.md) to produce `LITERATURE_REVIEW.md` (retrieval log, method-family table, falsifiable GAP statements, baseline pool, novelty-claim candidates). Every "compared to prior work" / "first / best / differs from" claim must later get a ledger entry citing a specific reference.
3. When the research question is open and hypotheses need generation (not just a fixed question), run the D0.5 hypothesis loop after D0: follow [references/hypothesis-generation.md](references/hypothesis-generation.md) to produce `HYPOTHESES.md` (Generator → Reflector → Ranker → Evolver), then let D1 design the experiments that test the adopted hypotheses.
3. Locate the evidence package: results JSON/CSV, analysis scripts, protocol, prior manuscript versions.
4. Inventory all evidence files and record their SHA-256 in `evidence_manifest.json`:

```
python scripts/build_evidence_manifest.py <paper_dir> --out evidence_manifest.json
```

3. Create `WORKING_NOTES.md` at the paper root: scope, assumptions, open questions.

### Phase 1 - Claim ledger
1. Copy [assets/claim_ledger.template.md](assets/claim_ledger.template.md) to `CLAIM_LEDGER.md`.
2. Enumerate every intended claim, including abstract and conclusion, BEFORE drafting.
3. Every number must trace to an evidence file + field; every claim must map to a ledger entry with verification method.
4. Verify the ledger mechanically before drafting:

```
python scripts/verify_claim_ledger.py <paper_dir> --out reports/ledger.md
```

It checks that each evidence file + field exists, values match, and reports text numbers without ledger coverage.

4b. **inconclusive 出口（E095）**——证据不足的声明不要硬编也不要硬删：在"状态"列标
`inconclusive`，在"如何验证"列写明缺失的证据与升级条件（缺什么实验/数据、什么条件下
可升 verified）。verify 脚本对 inconclusive 条目不验证证据（设计如此）、计 WARN 不 FAIL，
但正文中该声明必须以 hedge 措辞出现（"可能/未观测到/尚不确定"），不得强断言口吻。
评分纪律：证据不足给 inconclusive 优于编造数值（SciAgentArena C5 claim-validation 模式）。

4c. **科研状态快照（E104）**——复制 [assets/state_snapshot.template.md](assets/state_snapshot.template.md)
到 `STATE_SNAPSHOT.md` 并初始化：state_of_the_art（要超越的基线）/ hypotheses
（`[TESTING]/[PROVEN]/[TODO]`）/ key_knowledge / reflection / experiment_history /
recent_actions / open_questions。每次起草与修改轮后与 ledger 同批更新；
Phase 5 交付前对账：快照 `[PROVEN]` ↔ ledger `verified` ↔ 正文强断言三处一致。

5. **污染传播检查（L2-5）**——源证据被标记 broken/tainted（state 非
   verified/candidate）时，引用它的声称必须阻断，起草前跑一次：

```
python scripts/verify_taint.py <paper_dir> --fail-on-error --out reports/taint.md
```

   exit 1 = 存在引用污染/缺失证据的声称（Tainted_claims / Missing_evidence
   ERROR），先修复（换证据 / 重新验证 / 删除声称）再进入起草；tainted.json
   格式与阻断规则见 references/evidence-states.md「污染传播」节。

6. **Doubt-driven verification (B1)** — every claim then passes a fresh-context
   adversarial check before drafting: CLAIM → EXTRACT (re-open the evidence source,
   no reliance on drafting memory) → DOUBT (actively attack the claim-evidence pair,
   optionally with a different model as doubter) → **VERIFY (external-tool check:
   recompute / verify_claim_ledger / arXiv API — CRITIC rule: tool verification,
   not model introspection, settles the doubt)** → RECONCILE (fill the gap or tighten
   the claim) → STOP (anything unreconciled does not enter the manuscript). Full
   protocol: [references/doubt-driven-verification.md](references/doubt-driven-verification.md).
   Claims marked `UNRECONCILED` block D4→D5 exit (see gates_config).

### Phase 2 - Draft
1. Follow [references/writing-style.md](references/writing-style.md) for IMRaD structure, tense, hedging, and statistical reporting.
2. Write Methods and Results from computed values only; write Discussion next; write Abstract last so its numbers match Results.
2b. **Power analysis for sample-size claims (G1)** — before writing the Methods
    "N = ..." sentence for any inferential test (paired/two-sample t, exact
    McNemar, proportion, correlation), justify the sample size with a power
    analysis. Save the JSON to `results/power_analysis.json` and add a ledger
    entry ("sample size justified by power analysis at alpha/power/effect"):

```
python scripts/power_analysis.py --t-paired --solve n --d 0.5 --alpha 0.05 --power 0.80 --out results/power_analysis.json
python scripts/power_analysis.py --t-two-sample --solve power --n 30 --d 0.5 --alpha 0.05
python scripts/power_analysis.py --mcnemar --solve n --or 4 --p-discordant 0.3 --alpha 0.05 --power 0.80
python scripts/power_analysis.py --proportion --solve n --p0 0.5 --p1 0.65 --alpha 0.05 --power 0.80
python scripts/power_analysis.py --correlation --solve d --n 40 --alpha 0.05 --power 0.80
```

    Rules: (a) state alpha, power, effect size AND N in Methods; (b) when N is
    fixed by the experiment (not chosen for power), report `--solve power`
    (achieved power) or `--solve d` (minimum detectable effect) instead of
    pretending N was power-justified; (c) McNemar requires a `--p-discordant`
    estimate from pilot/prior work — disclose the source; (d) the JSON is
    evidence: ledger value must match `n_ceil`/`power`/`d_min` in the file.
3. Recompute each statistic from raw evidence; never copy a number from one section to another without rechecking.
4. Match hedging strength to evidence strength. A strong claim without a ledger entry is a blocker.
5. **Writing provenance (L2-6)** — after writing or revising any section, append a
   provenance record so every paragraph is traceable to model + prompt version +
   evidence snapshot: `python scripts/log_writing_session.py --log writing_session.jsonl
   --file <tex> --section <name> --model <name> --prompt-hash <h> --evidence-hash <h>`
   (hash = SHA-256 from build_evidence_manifest or sha256sum; append-only, never overwrite).

### Phase 3 - Machine checks
Run all machine checks and fix everything they flag (number-scan / stats-scan /
style-scan / tmlr-scan / ledger-scan / taint-scan / compile-gate):

```
python scripts/scan_number_consistency.py <paper_dir> --out reports/numbers.md --fail-on-stale
python scripts/scan_stats_consistency.py <paper_dir> --out reports/stats.md --fail-on-error
python scripts/check_writing_style.py <paper_dir> --out reports/style.md
python scripts/check_tmlr_compliance.py <paper_dir> --names "author1,author2" --out reports/tmlr.md
python scripts/verify_claim_ledger.py <paper_dir> --out reports/ledger.md
python scripts/verify_taint.py <paper_dir> --out reports/taint.md --fail-on-error
python scripts/scan_hallucination.py <paper_dir> --out reports/hallucination.md --fail-on-error
python scripts/compile_gate.py <paper_dir> --out reports/compile.md
```

- Number scan: stale markers, inverted CIs, cross-file numeric inventory, evidence values never used in text.
- Stats scan: impossible p-values, out-of-range effect sizes, p-value vs co-located statistic recomputed mismatch (t/z/chi2/F, stdlib CDFs), p-inequality contradictions, same-line n/N conflicts, sign mismatches, `p = 0.000`, multiple-comparison risk without any correction term (`--mcp-threshold`, default 10), df-vs-n and r/t/n info notes.
- Style scan: strong claims, `can + claim verb`, redundant adverbs, Chinese-English residue, CI crossing zero with a significance claim.
- TMLR scan: G1 template, G3 anonymization residues, G4 URLs, G6 bibliography, placeholders, zip size, `+/-` format.
- Taint scan: claims referencing broken/tainted evidence or missing files (exit 1 blocks them from entering the manuscript; protocol in references/evidence-states.md「污染传播」).
- Hallucination scan (MLR-Bench four types, E087): (E) Nonexistent Citations — \cite keys without a .bib entry, bib entries missing title/author; (E) Hallucinated Methodology — prose-named files under evidence/ or scripts/ that do not exist (method not reproducible from the package); (W) Mathematical Errors — inline "X = a + b" arithmetic contradictions; (I) Faked Results surface — strong-claim count + uncovered numeric literals for the LLM judge to verify (`--fail-on-error` blocks on the two (E) classes).
- Compile gate: pdflatex -draftmode + bibtex in a temp copy (never pollutes the delivery tree, FM-28), log scan for compile errors / undefined references / undefined citations / multiply-defined labels / overfull hboxes; static key check as fallback when TeX is unavailable (documented degradation, "## Compile skipped: 1"); orphan labels and uncited bib entries are warnings (`--fail-on-warning` promotes them).

7. **Label-matcher validation (G006, pilot-derived)** — whenever outcomes are
   determined by a programmatic label matcher (string/numeric comparison), the
   matcher itself must be validated before its labels may ground calibration
   or accuracy claims. A brittle matcher can silently mislabel semantically
   correct answers (e.g., ``1789年'' vs ``1789'', ``80元'' vs ``80'',
   ``不会'' vs ``否'') and flip the measured result (our pilot: accuracy
   63.3\% $\rightarrow$ 86.7\%, ECE 0.363 $\rightarrow$ 0.130 after
   semantic-tolerant relabeling). Gate:
   ```
   python scripts/verify_labels.py <data.jsonl> --report reports/labels.md
   ```
   - compare exact-match vs tolerant-match outcomes and report the flip set;
   - the flip set must be human- or LLM-adjudicated (each flipped row's
     predicted vs gold shown); a flip rate $> 5\%$ with unadjudicated flips is
     a blocker: do not proceed to calibration analysis until every flip is
     adjudicated and the matcher is fixed or the labels are corrected;
   - record the adjudication as evidence (e.g., `outcome_source =
     gold_label_relabeled_semantic`) and add a CLAIM_LEDGER entry documenting
     the relabeling, so the pre/post numbers are traceable.

### Phase 4 - Revision loop (R-rounds)
1. Open a round report from [assets/revision_round_report.template.md](assets/revision_round_report.template.md) at `ROUND_R{n}.md`; log every change with reason and evidence impact.
2. Update `CLAIM_LEDGER.md` for every change; never let a revision silently alter a reported value.
3. Re-run the six machine checks after every edit.
4. Maintain acceptance gates as executable checks: copy [assets/gates_config.example.json](assets/gates_config.example.json), adapt it, then run:

```
python scripts/run_acceptance_gates.py gates_config.json --record gates_history.jsonl
```

Exit 0 = all PASS. Old gates must stay PASS in every round; add new gates for new evidence.

5. **Reflexion-style reflection (落地改造)** — record gate history every round (the
   `--record` above) and, when a gate FAILs 2 consecutive rounds, inject a
   structured reflection into the next round:

```
python scripts/gate_reflection.py --history gates_history.jsonl --consecutive 2 --out ROUND_R{n+1}_reflection.md
```

   Copy the generated block to the top of ROUND_R{n+1}: reproduce the failure →
   fix the root cause (skill/config/evidence, never weaken the gate) → re-run the
   gate → log to GATES. At `--max-consecutive 3` still failing → escalate to the
   user (adjust criteria / skip / abort) — never silently retry forever.
   进入反思时同时重跑一次经验检索（Phase 0 步骤 0 的命令，`--task` 用当前失败主题），
   把相关教训/失败模式并入 ROUND_R 的反思块。

6. **Scanner regression fixtures (Voyager-style 课程回归)** — when a review or
   self-check reveals a failure class the scanners missed, add a fixture
   under [assets/scanner_fixtures/number-consistency/](assets/scanner_fixtures/number-consistency/)
   or [assets/scanner_fixtures/stats-consistency/](assets/scanner_fixtures/stats-consistency/)
   (dirty fixture = the failure class, `clean/` = no-false-positive control) and
   lock it in:

```
python scripts/scanner_regression.py
```

   Exit 0 = all failure classes caught and the control stays clean.

### Phase 4.5 - Adversarial review loop

Before launching the roles, optionally inform the review with the target
venue's real rejection patterns: [references/openreview-informed-review.md](references/openreview-informed-review.md)
— cluster the venue's rejections by weakness theme (openreview-mcp
`openreview_aggregate_weaknesses`) and fold the top themes into each role's
focus; if openreview-mcp is not installed, fall back to the FM-15..29 library
as the first-pass pattern list (documented degradation, does not block).

After the machine checks pass, run the multi-role adversarial review from
[references/adversarial-review.md](references/adversarial-review.md) before
submission: independent reviewer roles (methodology / statistics /
experiments / novelty / reproducibility / writing / ethics / figures) each
attack the manuscript, then the author responds per issue (fix / evidence /
rebut), then re-review until one round adds no new Critical/Major issue.
The figures role (R8) uses the deepseek-eyes skill to turn PDF table/figure
pages into structured review cards, then verifies the transcribed numbers
against the text and evidence JSON — this closes the vision gap of
text-only reviewer models.

1. Copy [assets/review_round_report.template.md](assets/review_round_report.template.md) to `REVIEW_R{n}_<role>.md` per role; issues carry ID / severity (Critical/Major/Minor/Nit) / location / expectation / evidence link.
2. Respond to every Critical/Major issue in `ROUND_R{n}.md`; Critical/Major allow only "fix" or "evidence" (no bare rebuttal); every response must leave a trace (changed file / new ledger entry).
3. Re-run the six machine checks after every fix; already-closed issues must not reappear.
4. Optionally fan review roles across models with the workflow tool (`agent(prompt, { model })`) when several models are configured — independent prompts, no cross-role communication, structured JSON output merged by the main agent.
5. Converge when a full round adds no new Critical/Major; then run the final
   self-assessment as a **dual-model scoring** (O2): score the TMLR weighted
   rubric (0.30N + 0.35S + 0.25Si + 0.10C) independently with two models (pro +
   flash), report agreement, and mark `UNSTABLE` when agreement < 80% (or the
   score gap exceeds threshold) — an unstable final score is not a conclusion.
   Protocol and judge-calibration wiring:
   [references/self-assessment-calibration.md](references/self-assessment-calibration.md).
   **Judge calibration gate (C1/L1-4, executable)**: before a judge model's score
   may count, run `python scripts/check_judge_calibration.py <calibration.json>
   --fail-on-uncalibrated` for each judge (report shape: judge / prompt_version /
   n_gold / fnr / fpr; ARS defaults FNR < 0.15, FPR < 0.10 per research-kit
   judge_calibration_kit.md). Gate FAIL → either calibrate the judge (gold set
   ≥20, same distribution as the manuscript) or mark that model's score
   "未经校准的模型估计" in SELF_ASSESSMENT.md and treat the final score as
   UNSTABLE-adjacent; never lower the threshold to enable an uncalibrated judge.
6. **Cross-round reflection (B3)** — every 3 rounds, aggregate the GATES logs,
   gate-reflections, review Critical/Major, and round failures into a failure
   pattern profile `FAILURE_PATTERN_<n>.md` (cluster against the FM-15..29
   library; new patterns become FM candidates after user approval). Inject the
   profile into the next round; feed it to the final assessment. Protocol:
   [references/reflection-aggregation.md](references/reflection-aggregation.md).
7. **Evidence-backed review-mode A/B (I1, E051)** — if you must decide whether the
   8-role fan-out beats a single reviewer, do not argue from intuition: run the
   equal-budget harness (same budget, paired defect hits, exact McNemar +
   Wilcoxon, hold when not significant):

```
python <PROJECT_ROOT>\study_repos\equal-budget-experiment\equal_budget_review.py --dir <PROJECT_ROOT>\study_repos\equal-budget-experiment
```

   Swap the mock `review_fn` for the real LLM reviewer, use ≥20 manuscripts with
   injected-defect ground truth (extend `sample_manuscripts/` + `ground_truth.json`).
   Only a significant result changes the review mode; otherwise keep the current
   mode and record the negative result.
8. **Anti-bias review discipline (I2, E054)** — load [references/judge-bias-checklist.md](references/judge-bias-checklist.md)
   before fanning roles: position (already handled by dual-judge swap), self-preference
   (keep judge heterogeneous w.r.t. the authoring model), verbosity/length (normalize),
   format (JSON-only). Fold the checklist into each role's basePrompt.
9. **Round-consistency trend (I4, E047)** — append each round's dual-judge consistency
   rate to `rounds_consistency.jsonl` (round, consistency, n_pairs). If consistency
   declines across rounds (self-bias amplification, 2504.02902), mark the final
   assessment `UNSTABLE`-adjacent and re-check judge prompts before converging.
10. **Rebuttal simulation gate (I3, E060)** — before Phase 5, verify the rebuttal
    draft against three simulated reviewer types (evidence-doubt / overclaim /
    mechanism), two-phase orthogonal (completion + satisfaction):
```
python scripts/rebuttal_sim.py --rebuttal REBUTTAL.md --evidence <evidence_dir> --out out/rebuttal_sim
python scripts/rebuttal_sim.py --rebuttal REBUTTAL.md --live --out out/rebuttal_sim   # 接 LLM 底座(无 key 自动 sim)
```

    Gate FAIL (any completion/satisfaction = 0) → return to Phase 4 (add evidence /
    tighten scope), do not enter Phase 5. `--live` 走共享底座 llm_client
    (research-kit/llm-client, E079): 无 DEEP_API_KEY 或 LLM_DRY_RUN=1 → sim(关键词模拟,
    与 mock 同构); 有 key → 真实 LLM(指数退避重试)。结果带 reviewer 标记
    mock/live-sim/live(溯源, E078); 调用级日志 llm_calls.jsonl; 追问生成仍可来自
    openreview 弱点聚类或 FM-15..29。

10b. **真实 rebuttal 草稿（N5）**——收到真实审稿意见（OpenReview 导出或
     REVIEW_R{n}_summary.md）时，先生成结构化骨架再逐条人工确认定稿
     （rebuttal 是保护层文档：代表作者面对审稿人）：

```
python scripts/draft_rebuttal.py --review REVIEW_R1_summary.md --out REBUTTAL.md
```

     骨架每条含 Reviewer concern / Our response / Evidence / Manuscript change
     四项 [TODO]；Evidence 必须指向具体文件+字段（claim ledger 纪律）。
11. **Cost-adaptive review (L3-3, evidence: evolution ledger G003)** — default stays
    quality-first: still expand the full 8 roles on demand. G003's equal-budget A/B
    (real model, 4 manuscripts / 5 defects, 32 calls/arm, paired tie b=0/c=0, exact
    McNemar p=1.0000; false positives multi 3 > single 2; cost Wilcoxon p=1.0000) →
    **hold**: 8-role fan-out shows no significant gain over a single reviewer within
    budget, so cost adaptation is only a convergence accelerator at low defect
    density, never a change of the quality-first default. Rule: if R1 has
    Critical+Major ≤ 1 AND neither methodology nor statistics raised a Major, R2 may
    shrink to 4 roles (methodology / statistics / experiments / novelty — statistics
    & methodology are hard checks and must never be trimmed); if R1 is defect-dense,
    keep 8 roles and extend. Shrink is one-shot: a 4-role round surfacing new
    Critical/Major restores 8 roles. Record every shrink/restore in the cost table
    appended to ROUND_R{n}.md (roles × model calls × round; template in
    assets/adversarial_review.workflow.md §成本自适应审稿).
12. **Figure-claim scanner (L2-4)** — run the mechanical figure-claim scan before
    fanning R8 out, so the role spends its budget on semantics instead of bookkeeping:

```
python scripts/scan_figure_claims.py <paper_dir> --fail-on-error --out reports/figures.md
```

    Exit 1 = a `\ref{fig:...}`/`\autoref{fig:...}` targets a label that is never
    defined, or an `\includegraphics` file is missing (ERROR). The report also flags
    figures defined but never referenced (WARNING, orphan check) and counts the raw
    numeric "Fig(ure) N" mentions in prose (INFO). R8 then owns the semantic half —
    does the figure the text points at actually contain the claimed values
    (deepseek-eyes card vs text vs evidence JSON)?

### Phase 5 - Submission compliance（TMLR 默认自动化，其他 venue 走映射）
0. **文献新鲜度门（L2-3）**——投稿前重跑相关文献增量门, 防 novelty 定位过时:

```
python scripts/check_literature_freshness.py <paper_dir> --claims-file <novelty_claims.txt> --max-age-days 30 --out reports/literature_freshness.md --fail-on-stale
```

   `LITERATURE_REVIEW.md` 缺失或达到 `--max-age-days`(默认 30 天) → exit 1,
   阻塞 Phase 5; 过期先重跑 D0 增量扫描(按立项日期过滤 arXiv 新工作),
   再逐条复核 novelty 声称并更新 CLAIM_LEDGER.md
   (协议: references/literature-review.md「新鲜度门禁」)。
1. TMLR 是默认/唯一自动化覆盖目标：按 [references/tmlr-compliance.md](references/tmlr-compliance.md) 走 G1-G11（template, US Letter, anonymization, anonymous repo, supplementary size/format, citations, broader impact, OpenReview form, cross-paper overlap, double-blind separation, hash reconciliation），运行 `python scripts/check_tmlr_compliance.py <paper_dir> --names "author1,author2" --out reports/tmlr.md`（脚本硬编码 TMLR 模板/tmlr.bst/阈值/白名单/Broader Impact 语义，只对 TMLR 有效）。
2. Run the citation-verification gate (L2-2) on the final bibliography — network
   outage degrades the gate to a documented pass, it never silently blocks:

```
python scripts/gate_citations.py <paper_dir> --fail-on-suspicious --out reports/citations_gate.md
```

   Exit 0 = no suspicious citations (or documented degradation `## Skipped_network: 1`);
   exit 1 = `## Not_found`+`## Mismatch` > 0 under --fail-on-suspicious (or no
   main.bib/references.bib found); exit 2 = infra error (bib/verifier missing, crash).
   Fix or delete every not_found/mismatch entry and re-run; manual_needed/suspicious
   entries require human review before delivery. Wraps research-kit verify_citations.py
   (4-layer verification, 90-day cache, needs network) via subprocess; report carries
   the fixed `paper` target label, relative bib path, and six `## <段落>: <计数>` lines
   (Verified/Not_found/Mismatch/Manual_needed/Skipped_network/No_bib_found).
3. 目标 venue ≠ TMLR（CVPR/NeurIPS/ICML/ACL/**AAAI**）时：TMLR 脚本结果不作数，按 [references/venue-mapping.md](references/venue-mapping.md) 人工映射——复用通用 G（G3 匿名/G9 重叠/G10 双盲/G11 门与哈希、占位符/±/zip 大小），替换 venue 专属项（G1 模板包名/G2 页面/G4 匿名白名单/G5 阈值/G6 bst/G7 伦理语义/G8 表单），并核对当年官网（链接见 venue-mapping.md §6；页数/补充材料/匿名化表述逐年变化，映射表是快照）。**AAAI 特别注意**（venue-mapping.md §3b）：匿名不由包选项驱动（无 [preprint] 选项体系），G1 改为作者块内容检查；近年 CFP 含生成式 AI 使用披露条款，LLM 辅助稿件必查；摘要注册 deadline 早于全文 1-2 周。
4. Rebuild submission zips, re-hash every artifact, and verify the manifest byte-for-byte:

```
python scripts/build_evidence_manifest.py <paper_dir> --verify evidence_manifest.json
```

5. **Submission package + checklist (N1/N4)** — before upload, build the package
   and run the mechanical pre-upload checks; the upload itself stays MANUAL
   (protected layer: OpenReview account + final confirmation + irreversible):

```
python scripts/prepare_submission.py <paper_dir> --name submission_<paper>   # zip + OpenReview checklist + G3 anonym re-scan
python scripts/check_submission_package.py <paper_dir> --fail-on-error       # C1-C7 mechanical checks
```

   Fix every FAIL (anonymity hits, missing pdf, gate failures, manifest
   missing files); confirm the human [ ] checklist items (authors,
   confidentiality, cross-submission declaration) before uploading.

6. Deliver: manuscript + evidence package + manifest + gate report + claim ledger + round report.

## Hard rules (violation = blocker)

1. Numbers must be independently recomputable from the delivered evidence. Recompute mismatch = blocker.
2. Zero claim-data contradictions: remove or hedge any claim without delivered evidence.
3. Do not mix statistics across groups or configurations (e.g., a CV computed from calibrated sd paired with uncalibrated mean).
4. Keep seed counts / sample sizes consistent across abstract, body, tables, and captions.
5. No new claims after a round closes without a new ledger entry backed by new evidence.
6. TMLR hard lines: template (G1), anonymization (G3/G4), originality and cross-paper overlap (G9), double-blind separation (G10).
7. No score inflation: a dimension gets 4 only when new evidence supports it, never by changing the score.
8. **Grounding (D1)**: every number / citation / date in the text is anchored to a
   deterministic snapshot — the `evidence_manifest.json` entry for that file, a
   first-hand source (FM-27), or a recomputed output. Never write a number from
   memory, cache, or another section without re-anchoring it to the snapshot.

## Resources

### scripts/
- [init_paper.py](scripts/init_paper.py) - one-command paper project bootstrap (skeleton + anonymous TMLR template + claim ledger / protocol with FM-15..29 lessons baked in / G8 form checklist / gates config with anti-regression placeholders + FM-24 manifest gate / round report / manifest)
- [scan_number_consistency.py](scripts/scan_number_consistency.py) - number-consistency scanner (stale markers, inverted CIs, inventory, evidence-only values)
- [scan_stats_consistency.py](scripts/scan_stats_consistency.py) - statistical-consistency scanner (stdlib CDF recomputation of p vs t/z/chi2/F, effect-size ranges, n conflicts, sign mismatches, p = 0.000, multiple-comparison risk; `--fail-on-error` for gates)
- [verify_claim_ledger.py](scripts/verify_claim_ledger.py) - claim-ledger verifier (file/field/value traceability; inconclusive status = WARN not FAIL with named missing evidence)
- [scan_hallucination.py](scripts/scan_hallucination.py) - hallucination scanner (MLR-Bench four types: cite keys without bib entries / incomplete bib / prose-named evidence+scripts files missing / inline arithmetic contradictions / strong-claim surface for LLM judge)
- [power_analysis.py](scripts/power_analysis.py) - statistical power / sample-size analysis (paired & two-sample t, exact McNemar, proportion, correlation; solve n / power / min detectable effect; JSON evidence for claim ledger, Methods sentence generator)
- [validate_judge_output.py](scripts/validate_judge_output.py) - judge-output schema validator + tolerant parser (review/rebuttal/score schemas; multi-regex drift recovery: fences/trailing commas/single quotes; invalid output counts as judge failure in denominator, never silently dropped)
- [suggest_experiments.py](scripts/suggest_experiments.py) - experiment-suggestion generator (maps review Critical/Major + ledger inconclusive gaps to structured experiment-completion plans with priority and evidence target)
- [prepare_submission.py](scripts/prepare_submission.py) - submission package builder (zip + OpenReview field checklist + G3 anonymity re-scan; upload stays manual — protected layer)
- [check_submission_package.py](scripts/check_submission_package.py) - submission package checker (C1-C7: zip size / main.pdf / anonymity / manifest / gates / ledger / no process docs) with human checklist
- [run_experiment_plan.py](scripts/run_experiment_plan.py) - experiment-plan orchestrator (declarative JSON plan: resource pre-check, topological scheduling, artifact verification, resume-skip, failure classification E053)
- [switch_project.py](scripts/switch_project.py) - multi-project switcher (list / switch / init; project context digest: manifest size, ledger count, latest round)
- [draft_rebuttal.py](scripts/draft_rebuttal.py) - rebuttal draft skeleton generator (parses review summaries incl. table rows; per-comment response/evidence/change TODOs; human-confirmed before submit)
- [make_camera_ready.py](scripts/make_camera_ready.py) - camera-ready converter ([accepted] option + author block injection + anonymous backup)
- [stats.py](scripts/stats.py) - statistical library (exact McNemar, Wilcoxon+CLES, Friedman+Nemenyi with CD, bootstrap CI, Breslow-Day heterogeneity, CD plot / forest plot generators)
- [verify_taint.py](scripts/verify_taint.py) - evidence-taint verifier (claims referencing broken/tainted/missing evidence are blocked; tainted.json + state machine per references/evidence-states.md)
- [compile_gate.py](scripts/compile_gate.py) - LaTeX compile gate (pdflatex -draftmode + bibtex in a temp copy + log scan for compile errors/undefined refs/cites/multiply-defined labels/overfull; static cite-ref-label-bib key check as TeX-free fallback; documented degradation when TeX unavailable; orphan labels / uncited bib entries as warnings)
- [build_evidence_manifest.py](scripts/build_evidence_manifest.py) - evidence manifest builder/verifier (SHA-256)
- [check_tmlr_compliance.py](scripts/check_tmlr_compliance.py) - TMLR G1/G3/G4/G6/G7 + placeholder/zip/format scanner
- [check_writing_style.py](scripts/check_writing_style.py) - writing-style static checker (hedging, CI-signal, Chinglish residue)
- [run_acceptance_gates.py](scripts/run_acceptance_gates.py) - config-driven acceptance gate runner, exit 0 = all PASS
- [check_judge_calibration.py](scripts/check_judge_calibration.py) - judge-calibration gate (FNR/FPR vs ARS thresholds; uncalibrated judge scores must not count in O2 final assessment)
- [literature_discovery.py](scripts/literature_discovery.py) - arXiv semantic discovery (Elicit-style): query → dedupe → relevance rank → structured table
- [check_literature_freshness.py](scripts/check_literature_freshness.py) - literature-freshness gate (LITERATURE_REVIEW.md missing/stale vs --max-age-days; novelty-claim coverage count)
- [citation_network.py](scripts/citation_network.py) - citation-relation screening (Scite-style proxy): supportive/contradictory/neutral from abstracts
- [consensus_check.py](scripts/consensus_check.py) - evidence-synthesis adjudicator (Consensus-style): YES/NO/MIXED verdict + strength
- [chat_pdf.py](scripts/chat_pdf.py) - lightweight Chat-with-PDF (SciSpace-style): pdftotext → chunk → keyword retrieve → cited answers
- [polish_manuscript.py](scripts/polish_manuscript.py) - polishing suggestions (Paperpal-style): redundant adverbs, Chinglish, can+claim, line outliers; never rewrites
- [retrieve_experience.py](scripts/retrieve_experience.py) - session-start three-factor experience retrieval (recency×importance×relevance, Generative Agents B2) + α task-type weighting (E073); importance column in lessons.md; evidence-gate default (verified/active only)
- [gen_review_cards.py](scripts/gen_review_cards.py) - generate deepseek-eyes review cards for PDF table/figure pages (feeds R8 figures reviewer)
- [scan_figure_claims.py](scripts/scan_figure_claims.py) - figure-claim scanner (undefined fig-label refs / missing includegraphics files / orphan figures / numeric mention counts)
- [log_writing_session.py](scripts/log_writing_session.py) - writing-provenance logger (append-only JSONL: file/section/model/prompt-hash/evidence-hash)
- [gate_citations.py](scripts/gate_citations.py) - Phase 5 citation-verification gate (subprocess wrapper over research-kit verify_citations.py; network outage degrades to documented pass; exit 1 on Not_found/Mismatch under --fail-on-suspicious)
- [verify_tree_diff.py](scripts/verify_tree_diff.py) - protected-tree snapshot/diff: verifiers must never mutate evidence (read-only invariant)
- [seal_run.py](scripts/seal_run.py) - atomically seal an experiment run (immutable, cannot be overwritten)
- [test_evidence_protection.py](scripts/test_evidence_protection.py) - negative fault-injection: generators/verifiers must not write canonical evidence

### templates/
- [tmlr/](templates/tmlr/) - official TMLR LaTeX style file and template (from the JmlrOrg/tmlr-style-file repo: `tmlr.sty`, `tmlr.bst`, `main.tex`, `math_commands.tex`, `fancyhdr.sty`). The submission must keep `\usepackage{tmlr}` with NO option (anonymous); `[accepted]` is camera-ready only, `[preprint]` de-anonymizes for preprint servers.

### references/
- [research-cycle.md](references/research-cycle.md) - full scientific cycle D0-D5 stage gates (literature → hypothesis → design → execution → analysis → writing → submission), the evidence-first discipline that feeds the phases below
- [literature-review.md](references/literature-review.md) - D0 literature survey workflow: retrieval log, method-family table, falsifiable GAP statements, baseline pool, novelty-claim ledger linkage
- [hypothesis-generation.md](references/hypothesis-generation.md) - D0.5 hypothesis-generation loop (Generator → Reflector → Ranker → Evolver, ≥2 rounds): falsifiable candidates, literature-traceable rationale, honest counter-evidence, HYPOTHESES.md output
- [findings-log.md](references/findings-log.md) - cross-stage discovery log (Research + Engineering dual track): session-recovery context, evidence-linked insights, FM linkage (from Modex FINDINGS template)
- [archive.md](references/archive.md)
- [evidence-states.md](references/evidence-states.md) - evidence state machine: broken/tainted/candidate/verified; engineering failures are NOT scientific negative results - cross-paper knowledge archive (Sakana growing archive): what to archive, naming, reuse protocol
- [adversarial-review.md](references/adversarial-review.md) - D4.5 multi-role adversarial review loop: 7 reviewer roles, severity protocol, response protocol, cross-model fan-out, convergence criterion
- [tmlr-compliance.md](references/tmlr-compliance.md) - TMLR two questions, scoring rubric, G1-G11 submission checklist
- [writing-style.md](references/writing-style.md) - IMRaD, tense, hedging, statistical reporting, rebuttal structure
- [failure-modes.md](references/failure-modes.md) - failure-mode library from past revision rounds with detection + fix

### assets/
- [claim_ledger.template.md](assets/claim_ledger.template.md) - claim ledger template
- [review_round_report.template.md](assets/review_round_report.template.md) - per-role adversarial review report template (issue IDs, severity, evidence link)
- [adversarial_review.workflow.md](assets/adversarial_review.workflow.md) - battle-tested cross-model adversarial review workflow (8 roles incl. R8 figures, independent-recompute prompt, schema, convergence criteria) - ready to copy into the workflow tool
- [hypothesis_generation.workflow.md](assets/hypothesis_generation.workflow.md) - battle-tested Generate-Reflect-Rank-Evolve hypothesis loop (2 rounds, pre-registration discipline)
- [research_cycle.workflow.md](assets/research_cycle.workflow.md) - full D0-D5 research-cycle orchestration skeleton (Sakana AI Scientist-style staged agents)
- [autonomous_cycle.workflow.md](assets/autonomous_cycle.workflow.md) - open-ended autonomous research loop: result -> feedback -> next hypothesis (Sakana open-ended, termination guards, knowledge persistence)
- [gates_config.example.json](assets/gates_config.example.json) - example acceptance-gate config
- [evidence_manifest.template.json](assets/evidence_manifest.template.json) - evidence manifest template
- [revision_round_report.template.md](assets/revision_round_report.template.md) - R-round change log + verification report template
- [FINDINGS_TEMPLATE.md](assets/FINDINGS_TEMPLATE.md) - cross-stage discovery log template (Research + Engineering dual track, from Modex FINDINGS design)