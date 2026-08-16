<!-- Translated from: evidence-states.md -->

# Evidence State Machine (Evidence States)

> Established at evaluation R43: engineering-failure outcomes must not be treated as scientific conclusions. This file defines the classification and flow of evidence.

## State definitions

| State | Meaning | Can it support a paper conclusion? | Disposition |
|---|---|---|---|
| `broken_engineering` | Output of training divergence / engineering failure | No | ARCHIVE/lessons + engineering appendix |
| `tainted_provenance` | Unknown origin / overwritten / unconfirmable | No | Audit record only (results/broken/) |
| `backfilled_candidate` | Run record backfilled after the run (weak provenance) | Diagnostic/candidate only, **must not alone serve as final sole evidence** | Run working directory + honest labeling |
| `pre_run_recorded_candidate` | Run record written before launch + output baseline | May enter independent recomputation and sealing | Run working directory |
| `candidate_real_evidence` | Post-repair, frozen config, complete run record | Only after sealing + independent recomputation + audit | Run working directory |
| `verified_real_evidence` | Sealed + verified + independent recomputation passed | Yes (claim strength constrained by scope) | results/verified/ |

**Provenance levels** (required by review R46):
- `backfilled_candidate` < `pre_run_recorded_candidate` < `verified_real_evidence`
- backfilled may serve as candidate, but is only trustworthy once a complete `--pre-run` seed reproduction-of-protocol verification can be launched from scratch

## Flow rules

```
training completes → candidate_real_evidence
  → independent recomputation agrees → read-only verification passed → atomic seal → verified_real_evidence
  → paper/ledger read only verified bundles
any step fails → broken_engineering or tainted_provenance (not into the paper)
```

## Hard rules

1. **Engineering failure ≠ scientific negative result**: a diverging/overwritten/unknown-origin run may only serve as diagnostic evidence
   (broken/tainted) and cannot be written as "no support observed under the protocol" — because the protocol itself was not validly executed.
2. **Paper state transparency**: when the evidence is not ready, the body should mark `evidence under re-execution`
   and not cite candidate/failed numbers.
3. **H1/H2 undecided**: until a candidate evidence is sealed, the hypothesis state can only be "undecided," not "supported/rejected."
4. **Read-only verification**: validators/gates must not rewrite canonical evidence (verify_tree_diff check).
5. **Sealing is not overwriteable**: no command may rewrite a sealed run (seal_run.py STATUS).

## Relationship to existing mechanisms

- Gates / manifest verify engineering consistency; the evidence state machine verifies scientific eligibility.
- The two are separate: engineering all-green ≠ evidence usable (empirical finding at R39).
- FINDINGS records engineering lessons; the evidence state machine decides which results may enter the paper.

## Contamination propagation (L2-5): a tainted source file → claims referencing it are automatically blocked

The state machine only governs the state of evidence files themselves; this mechanism propagates state to the claim layer: once an evidence
source file is judged broken/tainted (or any value in `state` other than `verified`/`candidate`),
all claims in `CLAIM_LEDGER.md` that reference it automatically enter blocked semantics —
they must not enter the body until the evidence is recovered (re-run independent recomputation + sealing + reset the state to `verified`/`candidate`),
and the validator blocks directly with exit 1.

### tainted.json format

`<paper_dir>/evidence/tainted.json` (optional file; absence = no contamination):

```json
{
  "tainted": ["results/e1.json"],
  "state": {"results/e1.json": "broken", "results/e2.json": "verified"}
}
```

- `tainted` (array) and `state` (mapping) may be present alone or together;
- a file whose `state` value is not `verified` / `candidate` is treated as contaminated, and the report uses that value
  as its state (e.g., `broken`);
- every file listed in `tainted` is treated as contaminated (state takes the value in `state`, defaulting to `tainted`);
- use the short state names, mapped from the long names in this document: `broken_engineering` → `broken`,
  `tainted_provenance` → `tainted`, any `*_candidate` → `candidate`,
  `verified_real_evidence` → `verified`;
- paths follow the same convention as the ledger, tolerating relative forms (e.g., `evidence/../results/e1.json`).

### Usage (before Phase 1 drafting + in Phase 3 machine checks)

```
python scripts/verify_taint.py <paper_dir> --fail-on-error --out reports/taint.md
```

- `Tainted_claims` (ERROR): claims referencing contaminated files (claim id + evidence path + contamination state);
- `Missing_evidence` (ERROR): evidence file referenced by a claim does not exist;
- `Claims_checked` (INFO) / `Tainted_files` (INFO);
- `--fail-on-error`: if any ERROR section has > 0 → exit 1.

### State machine → claim blocking rule

1. `broken_engineering` / `tainted_provenance` (`broken` / `tainted`) and
   any value in `state` other than `verified`/`candidate` always block the referencing claims;
2. `candidate` does not trigger contamination blocking (but under the state-machine hard rules it still cannot alone serve as the final sole evidence;
   gatekept separately by verify_claim_ledger / the acceptance gates);
3. `verified` does not block;
4. evidence recovery = re-run independent recomputation + sealing + reset the state to `verified`/`candidate`, then
   rerun `verify_taint.py` until ERROR is zero.

### Division of labor with verify_claim_ledger

- `verify_claim_ledger.py`: engineering consistency — evidence files/fields exist, values match,
  every body number has ledger coverage;
- `verify_taint.py`: scientific eligibility — whether the evidence state machine has judged a claim blocked;
  the two run independently, and both are required: engineering all-green ≠ evidence usable (empirical finding at R39).
