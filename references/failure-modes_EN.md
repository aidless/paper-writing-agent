<!-- Translated from: failure-modes.md -->

# Failure-Mode Library (real lessons from past revision rounds)

Each entry: ID | symptoms | detection | fix.

## FM-1 Stale number residue (after a seed-count update)
- Symptoms: the Abstract/contributions section still reports the 15-seed results (35.4-37.2%), while the body has been updated to the 30-seed results (29.4-30.8%).
- Detection: `scan_number_consistency.py --stale` old-value list `--fail-on-stale`.
- Fix: grep the whole document for the old values and clear them; rerun the scan until exit 0.

## FM-2 Mixed statistical definitions
- Symptoms: the CV used a calibrated sd paired with an uncalibrated mean, yielding CV=0.218; the correct definition CV=sd(gTV)/mean(gTV)=0.398/1.081=0.368, inflating the CNR upper bound beyond 4.38 to 2.94.
- Detection: recompute field by field against the evidence JSON; verify the formula inputs are the same group/config and same definitions.
- Fix: unify the group/config definitions, recompute, and sync the whole document (including Abstract and conclusions).

## FM-3 Table/caption number drift
- Symptoms: table 7.0/7.6%, with inconsistent values in the caption or body.
- Detection: the cross-file frequency table of the number-consistency scan.
- Fix: take the evidence-recomputed value as the single source of truth; unify caption/body/table.

## FM-4 Inverted CI / impossible interval
- Symptoms: lo>hi intervals such as `[0.85, 0.72]`.
- Detection: the "Inverted confidence intervals" section of scan_number_consistency.py.
- Fix: return to the evidence to recompute the bounds and check the signs.

## FM-5 Double-blind identity leakage
- Symptoms: the author/affiliation/acknowledgment/author-contribution block still has placeholder or real names; comments carry identity information.
- Detection: pre-submission grep of names, institutions, emails, ORCIDs, acknowledgment phrases.
- Fix: neutralize the author block (Anonymous), also clean comments; manage P1/P2 non-double-blind placeholders separately.

## FM-6 Fake/placeholder repository link
- Symptoms: github.com/Anonymous, fake URLs; the body and protocol.md disagree (real link vs. available at acceptance).
- Detection: grep URL patterns + cross-file comparison.
- Fix: unify to a real anonymous repository or a uniform "available at acceptance," synced across the whole document + protocol.

## FM-7 Hash/manifest mismatch
- Symptoms: after rebuilding the zip, hashes disagree with EVIDENCE_UPLOAD_MANIFEST.
- Detection: the hash_matches gate of run_acceptance_gates.py; per-package sha256 reconciliation.
- Fix: after rebuilding artifacts, recompute hashes, update the manifest, then run the gate.

## FM-8 Seed count / sample size inconsistent across sections
- Symptoms: Abstract says 30 seeds, conclusion says 15 seeds, and the caption says something else.
- Detection: scan value frequencies + manual check of N keywords.
- Fix: establish a single source of truth and unify the whole document.

## FM-9 Unregistered claim
- Symptoms: a revision round adds a new conclusion but CLAIM_LEDGER.md has no corresponding entry.
- Detection: diff against the ledger each round; every new claim must have evidence + an entry.
- Fix: add evidence and a ledger entry; if there is no evidence, delete the claim or downgrade it to a hedge.

## FM-10 Cross-paper overlap (originality)
- Symptoms: substantive reuse of text/figures/results across sister papers (e.g., claiming "sister-paper integration" but with large overlap).
- Detection: per-paper overlap comparison.
- Fix: dedupe and rewrite; present overlapping results independently in each paper and draw clear boundaries.

## FM-11 Template/class error
- Symptoms: a TMLR submission uses the jmlr class instead of tmlr.
- Detection: the G1 gate checks the preamble.
- Fix: migrate to article + `\usepackage{tmlr}` (no options, anonymous submission) + tmlr.bst, recompile and re-hash.

## FM-12 Reproducibility-script path issues
- Symptoms: rerun scripts use absolute paths or cross-machine paths; SRC/OUT are not joined on BASE.
- Detection: the G11 script_runs gate runs in a clean directory.
- Fix: use relative paths inside scripts (SRC/OUT both join BASE), and ship data inside the package.

## FM-13 Inconsistent uncertainty format
- Symptoms: the same quantitative description mixes ±25 through, +/-25, ±0.004.
- Detection: scan for ± and +/- patterns.
- Fix: unify the symbol (±) and significant figures throughout; note the source (e.g., ±0.003-±0.005 → display ±0.004).

## FM-14 Strong claim beyond the evidence upper bound
- Symptoms: a conclusion claims more than the provable upper bound (e.g., Conf-Gating 4.38 > CNR upper bound 2.94).
- Detection: compare each claim-ledger value against the evidence-computed upper bound.
- Fix: lower the claim to the range the evidence supports, or add evidence.

---

## Lessons distilled from adversarial-review rounds (FM-15 ~ FM-21)

The failure modes below come from multiple rounds of adversarial review of a research-writer demo paper (7-role cross-model mutual review;
reviewers independently recomputed/recompiled and verified with scipy/arXiv API/pdftotext); each is a real defect that actually occurred and was fixed.

## FM-15 Statistic triplets inconsistent with each other (W/p/r mutually contradictory)
- Symptoms: Wilcoxon reported W=412, p=0.0021, r=0.531, but the reviewer back-derived from W via the normal approximation
  p≈0.0002 — an order of magnitude apart. The p, W, r did not come from the same computation, or the W convention
  (min(W+,W-) vs. W+) was undefined.
- Detection: **independently recompute W/p/r from the delivered per-seed data**; all three must be derived and mutually consistent from a single
  `scipy.stats.wilcoxon` call; check the W convention and the effect-size formula.
- Fix: consolidate the statistic computation into a single analysis script (e.g., analysis.py), producing W/p/r within the same function;
  ship per-seed raw data in the evidence package; sync body/Abstract/ledger.
- Field report: R1 review, 5 roles independently found the triplet contradiction (demo paper); after the R2 fix, all roles recomputed and confirmed self-consistency.

## FM-16 Data generation and analysis mixed into one script (re-centering masks the contradiction)
- Symptoms: the analysis script used `np.random` to synthesize "per-seed data" and then re-centered it to a hardcoded
  mean, so mean(d_temp) disagreed with the reported mean difference (e.g., -0.0031 vs. -0.0094, a 3x gap), while the body
  claimed "all statistics were recomputed from per-seed data."
- Detection: for paired data, **mean(ours) - mean(temp) must equal mean(d_temp)** — verify by recomputing with an independent
  script; grep the analysis script for `np.random`/`default_rng` and the re-center
  pattern (`x - x.mean() + const`).
- Fix: **separate data generation from analysis** — generate_data.py produces raw per-seed data stored in
  an npz (including ablation-independent keys); analysis.py only reads and recomputes, asserting the key identities.
- Field report: R2 review, 5 roles independently confirmed the data contradiction; after the R3 fix, the recomputed difference was 1e-17.

## FM-17 Effect size / statistic inherited from stale data (not synced after recomputation)
- Symptoms: after a data fix, W/p/r were updated, but derived statistics such as rank-biserial still used the old W
  (e.g., after the update W=45/72, yet the body still wrote rank-biserial 0.617/0.609 = the old W=89/91
  result), and that value was not in analysis.py/e1.json/ledger, though the body claimed "all recomputed by
  analysis.py."
- Detection: every statistic in the body must have a corresponding field findable in analysis.py's output; independently recompute
  by the standard formula with current data; empty the "body number with no ledger coverage" warnings from the ledger scan.
- Fix: derived statistics (rank-biserial etc.) are produced in analysis.py in the same call as W/p/r;
  after any data change, **fully rerun** analysis.py and sync body/ledger; add the old values to
  the gates' stale-marker anti-regression gate.
- Field report: R3 review, 5 roles cross-confirmed the rank-biserial wrong value; fixed to 0.806/0.690 at R4.

## FM-18 Loss function term sign opposite to written description
- Symptoms: Eq.(1) wrote `−λH·Σp̂logp̂`, but since Σp̂logp̂ = −H(p̂), minimizing the loss actually **reduces**
  entropy and worsens overconfidence — opposite to the body's "entropy penalty guards against overconfident."
- Detection: check the mathematical identity term by term (Σp̂logp̂ = −H(p̂)), and confirm that minimizing the loss moves the target quantity
  (entropy/confidence/calibration) in the direction the body describes.
- Fix: correct the sign (`+λH·Σp̂logp̂`) and add a one-line identity explanation to the body; cross-check against the real training code.
- Field report: the R2 methodology reviewer found it; fixed at R3.

## FM-19 Citation author mix-up (arXiv metadata not checked)
- Symptoms: main.bib authors disagree with the arXiv metadata (e.g., arXiv 2302.06245 is actually
  Linwei Tao et al. but was written as Gupta et al.; 2006.06399 is actually Joo & Chung but was written as
  Karandikar et al.; 2106.09385 is actually Singh et al. but was written as Mukhoti et al.).
- Detection: **verify each entry empirically via the arXiv API** (`http://export.arxiv.org/api/query?id_list=...`),
  comparing authors/year/venue; citation keys in the body must map one-to-one to bib entries.
- Fix: correct the bib entries and citation keys per the arXiv metadata; sync the LITERATURE_REVIEW literature pool.
- Field report: an R2 reviewer used the arXiv API to catch 3 errors; fixed at R3.

## FM-20 Core method parameter undefined (loss function cannot be instantiated)
- Symptoms: the loss contains a temperature T, but the whole document only has "T ≥ 1" with no concrete value; λ is given but T is missing —
  a reader cannot reproduce the training objective. Same class: mutually exclusive terminology (class-wise vs. per-class vs.
  single scalar describing the same component).
- Detection: grep the whole document/protocol/scripts to confirm every loss parameter has a value or a selection rule; terminology is consistent throughout.
- Fix: give concrete values (e.g., T=2) with a selection rationale; unify the terminology.
- Field report: several roles confirmed it at R2/R3; fixed at R3.

## FM-21 Simulated/synthetic data with zero disclosure (presented as real experiments)
- Symptoms: demo/simulated data is presented in the body as real training results (the Setup claims "We train...30
  seeds"), grep finds zero simul/synthet/demo hits throughout, and disclosure exists only in author-side documents.
- Detection: grep the manuscript directory for simulation-disclosure words; verify that the evidence package's data-source statements are visible with the manuscript.
- Fix: explicitly disclose the data nature in the Setup/method section; state it in the generation script's docstring; add a
  data-disclosure field to the protocol; replace with real data before formal submission.
- Field report: the R3 ethics reviewer confirmed zero disclosure; fixed at R4 (three disclosures).

## FM-22 Validator semantic flaw masks drift (any-match + loose tolerance)
- Symptoms: the validator uses any-match semantics for ledger-claimed values (PASS if any claimed value matches any evidence value)
  plus loose tolerance (TOL=1e-3), so when a claimed CI [0.0275,0.0341] differs from the evidence
  [0.0274,0.0342] by 1e-4 it still reports "8/8 PASS," "23/23 acceptance gates all pass," a real data-claim
  contradiction is masked by the machine check, yet the body claims "all statistics recomputed by scripts, digit-for-digit identical."
- Detection: **regression-test the validator itself** — inject a deliberately wrong claimed value (e.g., shift a CI endpoint
  by 0.0001) and confirm the validator FAILs; check whether validation semantics is any-match or all-match,
  and whether the tolerance matches the numeric precision (4 decimals → TOL should be ≤5e-5).
- Fix: change the validation semantics to **all-match** (each claimed value must find a match in an evidence field);
  tighten the tolerance to match the significant digits (TOL=5e-5); put the fixed validator in the acceptance gates and
  run regression tests after every change. Synced lesson: **flaws in a validation tool can only be exposed by "tests of the validation tool"** — the
  value of adversarial review is not limited to catching paper defects; it also catches validation-gate defects.
- Field report: the R4 review's 7 roles found ledger 8/8 PASS coexisting with body CI≠evidence, traced to
  verify_claim_ledger.py's any-match; fixed and regression-tested at R4 (old value FAILs, new value PASSes).

## FM-23 A "fix round" itself introduces new defects (regression)
- Symptoms: the revisions made to fix the prior round's problems introduced new errors instead — the R5 round empirically found
  that three Majors were all introduced by "fix" operations: (a) to make "rounding consistent," the correct 0.806 was changed to 0.807 (an artifact
  of double-rounding the 4-digit intermediate 0.8065); (b) to close a G8 data-compliance gap, a **fabricated** "CIFAR-10 MIT
  License (official statement)" was added — the official page actually carries no license statement; (c) while adding a citation, the SCO
  method description was written incorrectly (called "temperature scaling + distribution penalty, learned temperature," when it actually
  is soft-binned calibration error SB-ECE, and the binning temperature is a tuned hyperparameter).
- Detection: **rerun a review round / independent recomputation after every change**; do not assume that later changes are safe once the prior round converged;
  empirically verify "new facts" introduced by a fix (license statements, method descriptions, comparison statements) against primary sources
  (official sites / arXiv originals); do single-step rounding checks on numeric changes (forbid re-rounding already-rounded values).
- Fix: before fixing, ask "could this fix itself introduce an error"; every new compliance/method assertion must trace to a
  primary source; after a numeric change, rerun the full chain of six scans + acceptance gates + manifest; write "must re-review after fixing" into the
  revision protocol.
- Field report: the R5 review's 7 roles independently recomputed and caught 3 fix-introduced Majors (rank-biserial double-rounding,
  fabricated MIT license, SCO description error); fixed at R5 with all regressions reverted/re-mediated.

## FM-24 Forgot to rebuild the evidence manifest after changes (stale manifest)
- Symptoms: delivery files such as main.tex/main.bib were changed and the PDF recompiled, but
  build_evidence_manifest.py was not rerun; a reviewer measured 31 PASS/3 FAIL with `--verify`, disproving the report's
  "manifest consistent with disk" claim. In the R6 round: the manifest was built at 04:16, main.tex/bib were modified at 04:18,
  main.pdf recompiled at 04:19, the manifest was not rebuilt, and 3 core files had hash mismatches.
- Detection: **immediately rerun** `build_evidence_manifest.py <paper_dir> --verify` after every change to any delivery file; before closing a round,
  verify the manifest timestamp ≥ the last file modification time; the "x/x PASS" count in the report must match the actual number of manifest entries
  (R6 also had a c: a 33/33 reported that was actually 34 entries).
- Fix: harden "edit → rebuild manifest → rerun six scans" as a fixed action sequence after every edit; do not leave manifest construction
  until the end of a round; take the count from `verify`'s actual output.
- Field report: 3+ roles at R6 independently caught the stale manifest with `--verify`; after the R6 rebuild, 36/36 all passed.

## FM-25 Tool output not reproducible (absolute paths embedded in reports)
- Symptoms: scan/validation scripts embed absolute paths in their reports (e.g., `Target: F:\deepseek\demo-tmlr-paper`,
  `Ledger: F:\deepseek\...\CLAIM_LEDGER.md`), so the very act of "rerunning the six scans per the standard procedure"
  changes the report bytes — even with the manifest rebuilt every time, the FM-24 gate keeps failing
  (R6/R8/R9/R10 four times; earlier rounds only blamed "forgot to rebuild the manifest" without reaching the path dependence).
- Detection: does the report header contain absolute paths? **Run the same scan from different cwds — are the report hashes identical?**
  (mismatch = not reproducible); does `--verify` cause reports/*.md to mismatch on rerun?
- Fix: render report paths uniformly as **relativized to the target root** (a `show()` helper:
  Target uses the root name, file paths use `relative_to(root).as_posix()`), so reports are independent of the invoking
  cwd and byte-reproducible; after the fix, run once from absolute and once from relative cwd and confirm the hashes match.
- Field report: the R12 methodology role pinpointed the root cause; after R12 fixed the 4 skill scripts, scans run from
  different cwds produced perfectly identical hashes, and the FM-24 gate passes stably.
- Meta-lesson: **reproducibility must be guaranteed at the tool level, not merely through process discipline** — making the tool output itself
  reproducible is more reliable than asking process participants to remember the discipline.

## FM-26 Report self-references ledger metadata (manifest size field)
- Symptoms: the scanner reads evidence_manifest.json as "evidence JSON," so its size/modified
  fields enter the evidence-only value set — reports/numbers.md embeds its own file size
  (e.g., 1215/3003), after manifest rebuild it records 1217/3017, the report is always one generation older than the manifest,
  and a single-pass "rescan → rebuild" flow never converges. This is the **ultimate root cause** of FM-24's six failures (R6/R8/R9/R10/R11/R12) —
  earlier rounds only blamed "forgot to rebuild the manifest" or "absolute paths"; the R14 rescan was only a bandage.
- Detection: does the report's evidence-only value set contain the manifest's size values (e.g.,
  `1215.0000`, `3003.0000`)? **rescan → rebuild manifest → rescan again**, do the two report hashes match
  (mismatch = self-reference not removed)?
- Fix: the scanner **excludes evidence_manifest.json itself** (it is process metadata, not experimental
  evidence) — tool output must depend only on results/*.json evidence, not on ledger metadata; after the fix
  the report becomes a mathematical fixed point of the canonical workflow (bytes unchanged after rescan; the manifest gate stays green without a rebuild).
- Field report: multiple roles at R12 confirmed the self-referential dependency; after the R15 fix, the fixed-point verification passed
  (rescan hashes match; the gate stays 25/25 without a rebuild).
- Meta-lesson: **a report must not self-reference ledger metadata** — tool output may depend only on experimental evidence, not on process
  metadata; this is the boundary condition of FM-25 "tool output reproducible."

## FM-27 Missing citation validity and "false completion" (the third and fourth layers of FM-19)
- Symptoms: three layers of citation defects: (a) **result validity not checked** — the cited paper's authors themselves noted "results invalidated
  by a disproven hypothesis" (singh2021, arXiv 2106.09385 v3 comment); previous rounds only verified title/author,
  never validity, and it was still used as a supporting citation until R18/R19 reviewers verified via the comment field;
  (b) **fabricated title** — when the arXiv API was unavailable, a title was written from memory (MMCE/AvUC,
  introduced at R23, caught by empirical PMLR/arXiv verification at R17); (c) **incomplete removal** — the same citation key appeared
  in two places (Introduction + Related Work), only one was deleted but it was marked done, and the PDF still contained the entry when checked
  (R25→R26). Companion pattern: "false completion" — a change log is marked done but not actually landed (R24 protocol
  hash case mismatch made the replacement ineffective; R25 deleted only one occurrence of a citation).
- Detection: (a) query the arXiv API for the comment/withdrawn fields; search arXiv/PMLR/Crossref to verify
  title and authors; (b) **grep the whole document for the citation key to confirm zero residue** (`grep singh2021 main.tex`);
  (c) after recompiling, check the reference count and specific entries with pdftotext (`pdftotext | grep Singh`);
  (d) a change-log "done" status must match an actual file change (rerun to verify, not just see whether the replacement command executed).
- Fix: every added citation must be verified against a primary source (title/author/venue/year/validity); mark "supporting citation vs. historical record" in the
  literature pool and main.bib (an invalidated reference stays as a record but is not used as support); deletion-type operations must
  pass **full-document grep for zero residue + recompile and check the artifact** before being marked done.
- Field report: R17 caught the MMCE/AvUC fabricated titles; R18 caught singh2021 invalidated but not marked; R19 caught the
  Introduction residue (R25 deleted only one occurrence); R26 fully landed (16 supporting citations with no Singh).
- Meta-lesson: **citation validity is the third layer of FM-19** (title real → author correct → result valid);
  **"claiming done" must verify actual landing** — rerun verification after the fix; do not just update the change log.

## FM-28 Verification scaffolding pollutes the delivery state (tool immunity, not process discipline)
- Symptoms: concurrent/historical review or verification processes create scaffolding directories in the repository root (.r21_verify_backup/,
  tmp_r21_fixedpoint/, .compile_check/, verify_probe_dir, etc.), overwrite reports/*.md,
  and leave aux artifacts from in-place compilation inside paper/ — causing the FM-24 gate to FAIL (25/25 becomes 24/25),
  and manifest verify to report 3 FAIL + 13~30 WARN. Occurred at R9/R11/R21 three times; the first two were only mechanically recovered
  by "clean → rescan → rebuild manifest" (process discipline); this R38 instance was cured at the tool level.
- Detection: do the manifest verify WARNINGS contain .r*/tmp_*/.verify*/verify_* directories?
  Does the scan report (text-files count) drift as temp directories appear/disappear in the repository?
  Does the FM-24 gate FAIL while nobody changed the manuscript?
- Fix: **build verification-scaffolding immunity into the scanner and the manifest builder** — exclude directories with the prefixes `.r*`, `tmp_r*`,
  `.tmp_*`, `.verify*`, `.review_*`, `.compile*` and the suffixes `_verify`/`_check`/
  `_backup`/`_fixedpoint`/`_rebuild`/`_compile` (note: the `verify_` prefix
  only matches directories, not files, so legitimate files like scripts/verify_claim_ledger.py are not harmed).
  With tool immunity, no verification activity can pollute reports/ or the manifest.
- Field report: contamination at R9/R11/R21 (process recovery); R38 tool-immunity verification (probe directories excluded,
  legitimate verify scripts still registered).
- Meta-lesson: **recurring environment problems should be upgraded to tool defenses** — "don't put scaffolding in the repo during verification"
  is process discipline and will always be violated; "the scanner is immune to scaffolding directories" is a tool defense and cannot be violated.

## FM-29 Real experiment reproducibility missing (training config is not evidence)
- Symptoms: after replacing simulated data with real training, reproducibility downgrades from "recompute statistics" to "retrain the model" —
  if the training script does not embed its config (seeds/epochs/optimizer/loss coefficients/data augmentation), does not output a cfg snapshot,
  and does not record the GPU environment (torch+cu versions), a reviewer cannot verify any number; if seed-count reduction is not disclosed,
  the statistical power is silently weakened (Phase A measured: on an RTX 3060, 200 epochs ≈ 10.6 hours per model,
  so 30 seeds × 4 configs is infeasible → 5 seeds × 4 configs × 100 epochs ≈ 1.6 hours).
- Detection: does the train script have `--seeds`/`--epochs` arguments and output a cfg snapshot to the result file?
  Does the protocol disclose seed-count reduction and the GPU environment? Is the artifact hash identical when the same training command is rerun?
- Fix: embed the full config in the training script and output cfg fields (seeds/epochs/device/T/λ/ECE bins/
  real:true); seed reduction must be explicitly disclosed ("5 seeds; a formal submission should expand to 30");
  record torch+cu versions in the protocol and requirements (FM-22); recovery logic restores from the keys actually saved in the npz
  (not from assumed keys).
- Field report: Phase A (R36+): budget baseline → seed-reduction disclosure → cfg snapshot → resume fix.
- Meta-lesson: **training config is evidence** — when model outputs are not reproducible, no number, however pretty, is evidence;
  budget constraints must be disclosed, not hidden (honest downgrade > fabricated completeness).
