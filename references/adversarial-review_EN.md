<!-- Translated from: adversarial-review.md -->

# Adversarial Review Workflow (Adversarial Review Loop)

Corresponds to D4.5 adversarial review in the research cycle: after the Draft is complete and the six machine scans pass,
enter a **multi-role adversarial review → revision → re-review** loop until no Critical/Major problems remain.
The idea comes from Modex's Auto-Review Loop, but is grounded in the TMLR review scale: reviewers only ask
"can the evidence support the claims," not "is the prose good."

## Why adversarial review is needed

The six machine scans (number consistency / statistical consistency / writing style / TMLR compliance / ledger verification / evidence contamination) check **verifiable hard facts**.
Adversarial review checks **argument strength**: whether the method has logical holes, whether the experiments leave room for doubt,
whether the claims are hedged enough, whether there are weak spots a reviewer would spot at a glance. The two kinds of checks are complementary —
passing the six scans ≠ a reviewer cannot find fault.

## Reviewer role matrix (each role is an independent attack angle)

A complete review round launches all roles; each role produces a problem list (sorted by severity).

| Role | Attack focus | Typical attack questions |
|---|---|---|
| R1 Methodology reviewer | Whether the method has logical holes / undefined cases; **whether the method description matches the implementation (Soundness vs. code, G7)** | When does the assumption fail? How were hyperparameters chosen — is there tuning-overfitting? Can the ablation truly isolate variables? **Does the body's method description line up with the actual code in evidence/scripts one-to-one? Are the results real or fake?** (hard constraint: code must be checked before scoring Soundness, with an explicit real/fake judgment; do not give Soundness ≥6 without the check) |
| R2 Statistics reviewer | Whether numbers stand up to recomputation and testing | Was multiple-comparison correction applied? Was the effect size reported? Are the CI and significance claims consistent? Is the sample size sufficient? |
| R3 Experiments reviewer | Whether experiments are sufficient and comparisons are fair | Are the baseline hyperparameters fair? Did they cherry-pick only favorable datasets? Are variance/seed counts sufficient? |
| R4 Novelty reviewer | Whether novelty claims are overstated | Do "first/state-of-the-art/different from" have supporting literature? Is an incremental contribution dressed up as a paradigm contribution? |
| R5 Reproducibility reviewer | Whether someone else can redo it from the paper | Are seeds/environment/data versions/scripts complete? Is randomness described? Is the training config embedded and disclosed? |
| R6 Writing reviewer | Whether claim strength matches evidence strength | Are strong assertions hedged? Do Abstract numbers match the body? Are figures/tables self-explanatory? |
| R7 Ethics reviewer | TMLR ethics/impact statements | Is a broader impact needed? Are data/human-subject compliance OK? Is COI declared? |
| R8 Figures/tables reviewer | Consistency of figure/table values with the body/evidence | Do the ECE/CI in the tables match e1.json? Do the statistical marks match the body? Are axes/legends complete? (use deepseek-eyes to turn PDF figure pages into a structured review card, then verify — a text-only model has no eyes, so it relies on the card) |

## Loop protocol

### A1 Launch

- Input: the completed Draft manuscript + evidence package + CLAIM_LEDGER.md.
- Each role reviews independently (**no inter-role communication**, to avoid groupthink — matches scholar-evaluation's independent-review principle).

### A2 Review (each role produces a REVIEW_R{n}_<role>.md)

Every problem must include:

```
- ID: R{n}-R3-07
- Severity: Critical / Major / Minor / Nit
- Location: §3.2 or Table 2
- Problem: (concrete enough to act on)
- Expectation: what the reviewer needs to see for it to count as resolved
- Evidence link: the evidence file/field this problem maps to, or "no evidence available to support"
```

Severity definitions:
- **Critical**: the evidence cannot support a main claim, or the method has a fatal flaw → the paper cannot be submitted in its current form.
- **Major**: a claim or experimental step has an obvious defect needing substantive revision.
- **Minor**: does not affect the conclusions but needs clarification/supplementation.
- **Nit**: wording, formatting, readability.

### A3 Response (author side, written into ROUND_R{n})

Respond to each item, choosing one of three treatments:

1. **Fix**: revise the manuscript / add experiments / recompute, and state what changed.
2. **Supply evidence**: existing evidence can address it; add the citation/number/explanation.
3. **Reasonable rebuttal**: state why it will not be changed (a reason is required; ignoring is not allowed).

Critical/Major may only be treated as "Fix" or "Supply evidence"; Minor/Nit may be "Reasonable rebuttal."
Every response must leave a trace (which file changed, which ledger entry was added),
otherwise the re-reviewing reviewer cannot verify — this is the same table as the CHG table in revision_round_report.

### A4 Re-review (the next round of A2)

- All Critical/Major from the prior round must be closed (re-run the six scans + ledger verification after the changes).
- Re-review may introduce **new reviewer role angles** (e.g., add a "reader representative" role),
  but **closed problems must not be resurrected**.
- Convergence criterion: one consecutive round with no new Critical/Major → the loop ends and Phase 5 submission compliance begins.

## Cross-model mutual review (optional enhancement)

The current deployment has multiple models (e.g., deepseek-v4-flash / deepseek-v4-pro) or multiple configurable providers.
The point of cross-model mutual review: different models have different blind spots, and independent review reduces a single model's self-consistency bias.

**Reusable script skeleton**: see [assets/adversarial_review.workflow.md](../assets/adversarial_review.workflow.md)
— contains 7 roles + model assignment, a structured output schema, prompts that force independent recomputation,
and aggregation/convergence criteria, proven across three rounds of practice (Critical 11→3→0). Copy it and replace the paths and review focus.

Implementation (using the workflow tool):

```js
// pseudocode: one subagent per role; different roles can specify different models
const roles = ['methodology', 'statistics', 'experiments', 'novelty', 'reproducibility', 'writing', 'ethics']
const reviews = await parallel(roles.map((role) => () =>
  agent(`You are a TMLR ${role} reviewer. Adversarially review the following manuscript and independently recompute the key statistics with tools...`, {
    label: role, schema: reviewSchema, model: role === 'statistics' ? 'deepseek-v4-pro' : 'deepseek-v4-flash'
  })
))
```

Constraints:
- Each role has an independent prompt; they share only the manuscript + evidence paths, never each other's review opinions.
- **The reviewer must independently use tools to recompute / recompile / query the arXiv API as evidence**, not merely trust the authors' claims — this is
  the key to catching triple inconsistencies, wrong effect sizes, and wrong citation authors (see failure-modes FM-15/17/19).
- Review output must be structured JSON (severity/location/problem/expectation), so it can be aggregated into REVIEW_R{n}.
- Aggregation is done by the main agent: dedupe, sort by severity, and map into ROUND_R{n}'s response table.
- Declared resource limits (e.g., demonstration data, missing real baselines) should be told to reviewers so they do not report them repeatedly.

## Convergence and deliverables

- After the loop converges, deliver: REVIEW_R{n}_*.md (per role) + an aggregated review report + the ROUND_R{n} response records.
- The review report enters the evidence_manifest hash accounting (review itself is process evidence, not paper evidence).
- Any Critical/Major fix from re-review must update CLAIM_LEDGER.md and re-run the six scans.

## Relationship to existing skills

- scholar-evaluation: provides the four-dimension scoring rubrics and reviewer agreement (ICC) — adversarial review uses it
  for the final quantitative self-assessment (TMLR weighted score); the two are used in sequence: adversarial review fixes problems first, then scoring measures whether the bar is met.
- Six machine scans: must be re-run after every adversarial-review revision, as a regression gate.
