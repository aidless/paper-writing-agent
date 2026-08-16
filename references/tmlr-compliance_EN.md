<!-- Translated from: tmlr-compliance.md -->

# TMLR Compliance Standard (built-in standard on the writing side)

The sole measuring stick for writing quality = the official TMLR standard (Author Guide / Formatting Instructions / Editorial Policies).
This document is the writing-side mirror of the review-side standard: whatever is written must pass all acceptance gates on the review side.

## 1. Acceptance decision = answering the two official TMLR questions

1. **Are the claims made in the submission supported by accurate, convincing and clear evidence?**
   —— Maps to: independently recomputable numbers + a claim-by-claim reconciliation of the evidence chain + a claim ledger.
2. **Would at least some individuals in TMLR's audience be interested in knowing the findings of this paper?**
   —— Maps to: the Significance score and audience judgment.

## 2. Four-dimension scoring (authors use the same yardstick for self-assessment)

| Dimension | Meaning |
|---|---|
| N = Novelty | A new contribution over existing work; must not merely reimplement an existing idea |
| S = Soundness | Correctness of statistics and experimental design; numbers must be recomputable |
| Si = Significance | Importance of the conclusions to the audience; supported by new evidence |
| C = Clarity | Writing is clear, readable, and free of residue |

Weighted score = 0.30N + 0.35S + 0.25Si + 0.10C (out of 5).
Thresholds: >=4.0 Strong Accept; 3.5-3.9 Accept (threshold line); 3.0-3.4 Weak Accept; <3.0 Major/Reject.

**Neutral-scoring discipline**: Without new supporting evidence, never give N/Si=4; never replace adding evidence by tweaking the score.

## 3. High-quality hard rules (violation = blocking item)

1. Numbers independently recomputable: every key statistic in the body must be recomputable from the delivered evidence (t/p/d, corrections, CI, effect size). A recomputation mismatch = blocking.
2. Claim-by-claim reconciliation of the evidence chain: every claim the paper makes about the evidence package must be consistent with the actual files, hashes, and manifest; a claim with no deliverable = blocking.
3. Zero claim-data contradictions: any "paper conclusion vs. delivered data" conflict must be resolved before delivery is allowed.
4. Residue scan: stale numbers, residual strong claims, mock/placeholder statements, `???`, cross-package ledger inconsistencies — grep and count each item.
5. Acceptance gates scripted: write every round's acceptance gates as rerunnable scripts; exit 0 = all PASS; include a zip independent compilation and hash reconciliation.
6. Neutral evaluation: evaluate only against the delivered evidence and the frozen protocol; do not be lenient with scores.

## 4. TMLR submission compliance gates (G1-G11, must all pass before submission)

| Gate | Check | Writing-side action |
|---|---|---|
| G1 | Template `\usepackage{tmlr}` (**no options** = anonymous submission) | Submission version must have no options: `[accepted]` is camera-ready only, `[preprint]` de-anonymizes (preprint server only); either appearing in a submission version = rejection |
| G2 | US Letter, produced by pdflatex | Verify compile arguments + recompile and re-hash |
| G3 | Fully anonymous body: authors/affiliations/acknowledgments/author contributions | Pre-submission grep re-scan + neutralize comments |
| G4 | Anonymous repository: real link or uniform "available at acceptance" | Uniform wording across the whole document + protocol.md |
| G5 | Supplementary material <=100MB, anonymous, PDF/ZIP | Re-check size and content after packaging |
| G6 | Consistent citation format (tmlr.bst) | Check bib output at compile |
| G7 | Broader Impact (where applicable) | Present and appropriately worded |
| G8 | OpenReview form: profiles/COI/AE suggestions/funding/IRB | Author-side completion checklist |
| G9 | Cross-paper overlap audit (originality) | Compare text/figures/results per paper |
| G10 | Double-blind isolation of preprint vs. submission | Double-blind version contains no identity clues |
| G11 | Acceptance gates all PASS + hash reconciliation | Run run_acceptance_gates.py + manifest validation |

## 5. Strong Accept threshold (writing target reference)

- Weighted total >=4.0 and at least one non-S dimension = 4, and that 4 is supported by **new evidence** (score-only changes not accepted).
- All existing acceptance gates continue to PASS; new evidence must enter evidence + manifest + freeze (hash).
- The paper must not add any statement not registered in the claim ledger.
- If the evidence cannot support a 4 on some dimension, honestly state what is missing and what supplement would reach 4.

## 6. Output and archiving

- Each round's writing/revision artifacts are saved to the paper-package directory with a version number and date.
- The deliverables must include: manuscript + evidence package + evidence_manifest.json + acceptance gate report + CLAIM_LEDGER.md.

## 7. Venue parameterization (L3-2)

- **TMLR is the default/sole automated coverage target**: this file's G1-G11 and `scripts/check_tmlr_compliance.py` both take TMLR as the authority (the script hardcodes `\usepackage{tmlr}` without options, tmlr.bst, the 100MB threshold, the TMLR anonymous-repository whitelist, and Broader Impact semantics), and are valid only for TMLR submissions.
- **Other venues (CVPR / NeurIPS / ICML / ACL) go through the mapping process**: no automated scan is currently done; they must be checked manually against [venue-mapping.md](venue-mapping.md) — that table gives the per-dimension differences (template/anonymity/page count/supplementary/references/rebuttal/author block/ethics statement), a G-level reusability matrix (which Gs can be reused directly, which need parameter substitution, which need new checks), and a minimal venue-adaptation process (copy the check → adjust template/naming rules → run local fixture regression).
- **Usage order**: for a new paper, first pass G1-G11 on the TMLR baseline; enable the mapping process only once you have decided to switch to another venue, and before submission season re-verify each conference's current-year rules on the conference website (links in venue-mapping.md §6).
