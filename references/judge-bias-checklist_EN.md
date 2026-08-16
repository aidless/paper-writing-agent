<!-- Translated from: judge-bias-checklist.md -->

# Judge Anti-Bias Checklist (LLM-as-Judge survey E054 implemented, I2)

> Source: the bias taxonomy of A Survey on LLM-as-a-Judge (2411.15594) + your stack's existing mitigations.
> Use: consult this table before enabling and during the adversarial review / final evaluation / rebuttal simulation judge prompts.

## Four main bias classes and mitigations

| Bias | Behavior | Mitigation in this stack | Check |
|---|---|---|---|
| Position bias | Favors whichever of A/B appears first | Blind dual judgment + position swap (judge_dual.py) | Agreement rate ≥80%? |
| Self-preference | Favors outputs matching one's own (same-family model) | judge and subject are heterogeneous; dual-model final evaluation (O2) | Is the judge model not in the same family as the judged model? |
| Verbosity/format bias | Long outputs or specific formats score higher | Output truncation cap + JSON-only schema | Length normalized? |
| Authority/ordering bias | Influenced by role or ordering | Role-independent prompts, no cross-role communication | No inter-role communication? |

## Pre-enable checks (each checkable)

- [ ] Position bias: dual-judgment position swap enabled, agreement rate reported
- [ ] Self-preference: judge and subject model are heterogeneous (or declare them same-source and count it into agreement)
- [ ] Verbosity: input truncation (e.g., 40k-character cap) + output is JSON only
- [ ] Calibration: judge calibrated on a same-distribution gold set (FPR<0.10/FNR<0.15, self-assessment-calibration.md §1.5)
- [ ] Decision priority: programmatically decidable items (numbers/files/citations) go through assertions first; the judge only backstops

## Monitoring during review

- Record the judge agreement rate each round → rounds_consistency.jsonl (I4); a drop signals amplified self-bias;
- The same defect independently flagged by ≥2 roles = high confidence (existing experience rule 2); flagged by a single role only = re-verify.

## Discipline

- The judge is an instrument; report its performance (FPR/FNR/agreement), and never treat judge output as human annotation (powercontext boundary declaration);
- When a bias is found, fix the judge prompt or swap the judge first; do not mask it by "running a few more times."
