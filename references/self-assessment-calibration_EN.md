<!-- Translated from: self-assessment-calibration.md -->

# Self-Assessment Calibration (dual-model final evaluation + judge agreement, O2)

> Source: jcode's rerun idea for judge agreement + research-kit judge_calibration_kit + floor-model policy
> Purpose: The post-convergence TMLR weighted final evaluation must not be "decided by a single model"; instead two models score independently and
> report agreement; disagreement = unstable final evaluation, which must not be cited directly as a conclusion.
> C1 (2026-08): Add the mandatory Agent-as-a-Judge (arXiv:2410.10934) step — a judge must be calibrated on a
> **gold set drawn from the same distribution as the task being judged** before going live; the gap between the judge and the judged capability is itself a source of bias.

## 1. Background

Current state: After Phase 4.5 converges, scholar-evaluation's TMLR weighted score
(0.30N + 0.35S + 0.25Si + 0.10C) is used for the final evaluation, written to SELF_ASSESSMENT.md.
Problem: A single-model self-assessment is simultaneously author and reviewer (serena-style role conflict), and the score may carry systematic bias.

## 1.5 Calibration before a judge goes live (Agent-as-a-Judge, C1, mandatory first step)

A final-evaluation/review judge must be self-calibrated **before being enabled**, otherwise its scores are untrustworthy:

1. **Same-distribution gold set**: Prepare manually graded examples (same type/difficulty as the manuscript under test, e.g., the graded reviews of a converged paper from a prior round); do not borrow across tasks (a judge-to-capability gap = source of bias);
2. **Calibration protocol**: Run FPR/FNR following research-kit `judge_calibration_kit.md`;
   enable the judge only if it passes the threshold (e.g., FNR<0.15 and FPR<0.10, per the ARS gate);
3. **Record**: State in SELF_ASSESSMENT.md that "this judge was calibrated on N same-distribution gold-set examples, FPR/FNR = …"; scores from an uncalibrated judge are tagged "uncalibrated model estimate";
4. Calibration failure → switch judge models or supplement the gold set; never force-enable by lowering the threshold.

## 2. Dual-model final-evaluation protocol

1. **Independent scoring**: Two models (pro + flash recommended, per the floor-model policy — flash represents "weaker but more common reviewer") score the same manuscript independently on the four dimensions, without seeing each other's scores;
2. **Report agreement**: Record each model's per-dimension scores + weighted total; agreement rate = the proportion of dimensions on which the two models agree
   (or judged by a |Δtotal| threshold);
3. **Decision**:
   - Agreement rate ≥ 80% (or |Δtotal| ≤ threshold) → final evaluation is stable; write the two-model average into
     SELF_ASSESSMENT.md and note that two models were used;
   - Agreement rate < 80% (or |Δtotal| exceeds threshold) → mark `UNSTABLE`, do not use it directly as a conclusion;
     the disagreeing dimension(s) (e.g., a 2-point N gap) become the focus of the next review round; return to Phase 4.5 to recheck.

## 3. Wiring to judge_calibration_kit

- If a gold set exists (manually graded example reviews/scores): use research-kit's
  `judge_calibration_kit.md` protocol to calibrate each reviewer model's FPR/FNR; only enable
  that model's final-evaluation score after calibration passes (isomorphic to deepteam/ARS's judge acceptance gate);
- When no gold set exists: at least keep the dual-model agreement report and declare that "the final evaluation is a model estimate,
  not a human annotation" (powercontext judge-boundary discipline).

## 4. Discipline (reinforces existing rules)

- **Review convergence ≠ scientific conclusion**: Two models agreeing only shows "process issues cleared and model estimates stable,"
  not that N/Si have real evidence — never give 4 on a dimension with no evidence (existing rule 7 unchanged);
- Any change to the final-evaluation score must be backed by new evidence; "tweaking scores to force agreement" is forbidden (extension of existing hard rule 7);
- SELF_ASSESSMENT.md records: each model's per-dimension scores, total, agreement, decision
  (stable/unstable), and gold-set calibration status (if any).

## 5. Implementation

- When a workflow tool is available: run two `agent(prompt, {model})` calls that each run scholar-evaluation
  on the four-dimension rubric independently; the main agent merges scores and computes agreement;
- Without a workflow: run twice serially, with the second prompt explicitly saying "score independently; do not reference the previous result."
