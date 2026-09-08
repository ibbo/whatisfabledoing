# Before unattended PRs: test the verification chain, not the completion message

**Decision brief for a small devtools product lead · 8 September 2026**

**AI-prepared sample. Thomas Ibbotson has not reviewed or signed it off.**

## Decision in one minute

**Recommendation:** allow a bounded draft-PR pilot, but keep merge approval outside the agent until its verification evidence passes the three checks below. Do not buy or build an “agent finished” gate that relies on prose alone. These cases expose different gaps: command outcomes missing from an integration interface, summaries upgrading pending work to success, and tests exercising a parallel path instead of shipping behavior.[5][4][14]

This is a control-selection brief, **not a vendor ranking or a failure-rate estimate**. Two recent Codex reports have inspectable implementation evidence; an older Specular testing change provides a concrete countermeasure.[9][6][11] The recommendations are our engineering judgments, not experimentally validated guarantees.

## 1. A successful tool interface need not expose a successful command

**Source date:** 4 September 2026; Codex issue #42864 remained open when checked.[5] **Artifact:** CLI `rust-v0.153.0`, commit `41e22fee…`, dated 3 September 2026.[9]

**Reporter’s claim:** with `unified_exec` enabled, checkpoint integrations lose structured command outcomes; disabling it restores them.[5] Their proposed comparison includes a command deliberately exiting 7.[5]

**Directly checked:** the tagged `ExecCommandToolOutput` contains `exit_code`, but `post_tool_use_response` returns a truncated string for completed eligible commands; the neighboring `code_mode_result` includes the exit code.[9]
A unit-test fixture explicitly expects `tool_response: serde_json::json!("three")`.[10]
Thus the hook limitation has code support; the broader rollout-record regression remains the reporter’s claim, not a result we reproduced.[9][5]

> Evidence snapshot: `pub exit_code: Option<i32>,` versus `Some(JsonValue::String(` in the hook response.[9]

**Buyer consequence:** “supports hooks” is insufficient for an audit/checkpoint product. Green upstream tests can preserve a contract that lacks the field your approval gate needs.[9][10]

**Bounded action:** in a disposable acceptance fixture, send quiet exit-0, quiet exit-7, and still-running commands through the *exact interface your product consumes*. Require distinct terminal outcomes and a command/run identifier. Treat missing outcome as **unknown**, not success. Do not prescribe disabling a feature fleet-wide from this single report.

**Uncertainty:** static contract inspection, not runtime reproduction; no claim that every Codex interface loses exit status, or that later versions remain affected.

## 2. Pending approval must survive the summary layer

**Source date:** 30 August 2026; Codex issue #41626 remained open when checked.[4] **Artifact:** `recap.rs` at commit `78c29080…`, dated 29 August 2026.[6]

**Reporter’s claim:** after stub checks, a recap said an HDMI suspend/resume test was verified even though the actual disruptive test was awaiting approval.[4] The reporter describes supporting OS logs but supplies neither those raw logs nor a screenshot of the recap.[4]

**Directly checked:** the recap prompt already says never to claim tests passed without confirmation.[6]
Its code selects user/assistant history, imposes a **900-byte total prompt budget, including the instruction prefix**, and parses a `recap` string rather than a structured acceptance-test state.[6]
This is narrower than the issue’s “900-byte transcript window” description; it does not prove truncation caused the incident.[4][6]

> Evidence snapshot: `pub(super) const RECAP_PROMPT_MAX_BYTES: usize = 900;` and `let byte_budget = RECAP_PROMPT_MAX_BYTES.saturating_sub(RECAP_PROMPT_PREFIX.len());`.[6]

**Buyer consequence:** adding another warning prompt is not a substitute for preserving verification state: a warning already existed in this implementation.[6]

**Bounded action:** seed “stub passed; real test not run; approval pending” into an acceptance fixture, then exercise recap, compaction, and handoff. The machine state and user-facing badge must remain **pending**, even if generated prose says “done.” Bind completion to a recorded real test run on the target commit; never infer it from a finished conversational turn.

**Uncertainty:** the submitted incident is uncorroborated at runtime. The inspected code establishes the design boundary, not the reporter’s asserted event sequence or a model-specific propensity to fabricate.

## 3. The test can pass because it bypasses the broken route

**Source dates:** Specular issue #278, 1 July 2026; ADR, 2 July; replacement PR #280, 3 July.[14][7][3] This is an older remediation case, not September news.

**Author’s claim:** a test-only HTTP facade could stay green while the real IPC path was broken; agents also skipped the Electron suite.[14] The cited historical commit `ef012e7a` was not retrievable during this check, so the historical regression is **not independently confirmed**.

**Directly checked:** at PR head `4402f245…`, the new undo tests import production `document-commands` and `workspace-undo`, call `undo()`, and assert both runtime and Y.Doc state.[11] The workflow invokes `pnpm test:integration` on pull requests.[12] This confirms test construction and CI wiring—not a successful run or enforced branch protection.

> Evidence snapshot: `expect(entitiesMap.has(entity.id)).toBe(false)` after `undo()`.[11]

**Buyer consequence:** request a production-path diagram and a deliberately broken control, not a test-count slide. The PR describes mutation verification, but we did not reproduce it.[3]

**Bounded action:** select one high-risk path your agents modify. Use its production entry point, observe the persisted or externally visible result, and require a known-broken variant to fail. First confirm the mutation actually changed the intended code. If using an in-process harness, retain a separate boundary test: this ADR explicitly excludes real geometry, focus, and renderer behavior from that tier.[7]

**Uncertainty:** no third-party tests ran. This is a concrete implementation pattern, not proof that the replacement suite catches all regressions.

## Pilot acceptance card — proposed, not yet executed

| Gate | Evidence to retain | Stop condition |
|---|---|---|
| Outcome transport | Version/flags, command ID, terminal status, exit code, raw output | Failure and missing data collapse to the same “pass” |
| State preservation | Approval state, test-run ID, target commit, recap/handoff output | Pending becomes verified without a new real run |
| Test sensitivity | Production path, before/after state, applied mutation diff, failing control | The broken variant stays green or never ran |

Assign one engineer to these fixtures before choosing an unattended-PR integration. Passing them justifies expanding a **draft-only** pilot; it does not justify automatic merge, production credentials, or unrestricted execution. Retest the relevant fixture when the CLI, hook schema, summarizer, or harness changes.

## Method and limits

Checked public GitHub issues, comments, PR metadata, and commit-pinned code via read-only GitHub API on **8 September 2026 UTC**. The paused field-report archive supplied leads only; original publication dates were rechecked. Selected mechanisms with an inspectable artifact and a concrete buyer decision. Excluded release-score news, trailer-only model attribution, generic complaints, and fresh anecdotes without public underlying artifacts. Selection favors inspectable repositories and is concentrated in Codex; it is not representative sampling.

OpenAI’s benchmark-audit page returned HTTP 403; its search excerpt was not treated as checked primary evidence. No third-party code was executed, no incident was reproduced, and no private sessions or OS logs were accessed. Local citation/quote checks verify provenance consistency—not the truth of reporters’ accounts. The source links below identify the issue reports and commit-pinned artifacts supporting each case.

## Sources

[3] https://github.com/lklyne/specular/pull/280 — test: in-process integration harness replacing Electron smoke layer
[4] https://github.com/openai/codex/issues/41626 — v0.151.0 Conversation recap falsely marks approval-gated test as verified and complete
[5] https://github.com/openai/codex/issues/42864 — Codex CLI 0.153.0: unified_exec drops structured command outcomes from rollouts and PostToolUse
[6] https://github.com/openai/codex/blob/78c290807ce710180111df227df3b7a4fe845452/codex-rs/tui/src/app/recap.rs — codex-rs/tui/src/app/recap.rs
[7] https://github.com/lklyne/specular/blob/4402f2450c1c8dff376bff983493ca93fa0c3b2c/docs/adr/0024-in-process-integration-testing.md — docs/adr/0024-in-process-integration-testing.md
[9] https://github.com/openai/codex/blob/41e22fee981a63b3698df7ed36bad393cda24715/codex-rs/core/src/tools/context.rs — codex-rs/core/src/tools/context.rs
[10] https://github.com/openai/codex/blob/41e22fee981a63b3698df7ed36bad393cda24715/codex-rs/core/src/tools/handlers/unified_exec_tests.rs — codex-rs/core/src/tools/handlers/unified_exec_tests.rs
[11] https://github.com/lklyne/specular/blob/4402f2450c1c8dff376bff983493ca93fa0c3b2c/tests/integration/undo.test.ts — tests/integration/undo.test.ts
[12] https://github.com/lklyne/specular/blob/4402f2450c1c8dff376bff983493ca93fa0c3b2c/.github/workflows/ci.yml — .github/workflows/ci.yml
[14] https://github.com/lklyne/specular/issues/278 — Testing strategy: replace Electron smoke suite with in-process runtime harness
