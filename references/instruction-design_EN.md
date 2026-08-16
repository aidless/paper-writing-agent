<!-- Translated from: instruction-design.md -->

# Instruction Design for the Writing Agent (five principles for agent-facing instructions, O3)

> Source: the writing-for-agents skill in skills-main
> (context pointer / dual budget / completion criteria / leading word / negative bans backfiring)
> Use: audit the "instructions to the agent" in SKILL.md and the research-writer persona; every instruction should answer "how do I know this step is done."

## Five principles

### 1. Completion criteria (every instruction has a verifiable completion criterion)
An instruction says not only "what to do" but also "what counts as done," and the criterion must be checkable
(file exists / command exit 0 / numbers match / checklist coverage).
- Counterexample: "Check number consistency" (no criterion);
- Positive example: "Phase 3 is complete = all six scans PASS (scan_number_consistency /
  scan_stats_consistency / check_writing_style / check_tmlr_compliance /
  verify_claim_ledger / verify_taint all exit 0), and the six reports under reports/ have no FAIL."

### 2. Positive wording (state the target behavior, not a ban list)
A purely negative ban (especially "do not X") is easily taken by an LLM as "mention it and move on"; state the target behavior in the positive,
with a completion criterion.
- Counterexample: "Do not hallucinate citations" (no criterion, easily ignored);
- Positive example: "Every citation must trace back to a crawled original / primary-source file, and be verifiable in the evidence manifest"
  (positive target + checkable).

### 3. Leading word (anchor behavior through pre-trained vocabulary)
Open with domain-frequent, semantically precise words (e.g., "recompute," "independently recompute," "per-seed," "read-only verification"),
which anchor correct behavior better than newly coined terms.

### 4. Dual budget (context load / cognitive load)
Don't overload an instruction at once: control the context budget (per-step load) and the cognitive budget (per-instruction complexity)
separately; split complex flows into phases, keeping instructions within a phase few and precise.

### 5. Context pointer (pointer wording decides trigger reliability)
The key to "when should the agent load which instructions" is aligning trigger words with task vocabulary;
write the trigger conditions clearly in the description of a new skill/flow (in agentskills' three-part loading,
the discovery stage is exactly name + description).

## Audit checklist (applies to this agent's existing instructions)

Go through every Phase in SKILL.md and the persona, asking per instruction:
1. Does this instruction have a verifiable completion criterion? (If not → add one)
2. Is it a purely negative statement? (If so → make it positive + add a criterion, except for safety boundaries)
3. Does it open with a domain-frequent anchoring word?
4. Is the per-instruction cognitive load manageable? (If too long → split it)
5. Do the trigger conditions (description / when to load) align with the task vocabulary?

## Phase-level completion-criteria quick reference (implementation result)

| Phase | Completion criterion (checkable) |
|---|---|
| Phase 0 receipt | evidence_manifest.json built and --verify passes; WORKING_NOTES.md exists |
| Phase 1 claim ledger | verify_claim_ledger.py exit 0; UNRECONCILED claims = 0 (after DDD) |
| Phase 2 drafting | Abstract numbers match Results recomputation; every claim has a ledger entry |
| Phase 3 machine checks | all six scans exit 0, no FAIL under reports/ |
| Phase 4 revision round | ROUND_Rn.md has per-item records; all six scans re-run green; prior gates stay PASS |
| Phase 4.5 adversarial review | no new Critical/Major in one round; dual-model final agreement ≥ threshold (stable) |
| Phase 5 delivery | G1-G11 all pass; manifest byte-level reconciliation; zip re-hash matches |
