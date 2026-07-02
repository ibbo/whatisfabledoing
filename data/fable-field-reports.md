# Claude Fable Field Reports

## 2026-07-01

### [Four hundred bugs found across dozens of open-source projects](https://iscinumpy.dev/post/claude-code-reviews/) — Henry Schreiner
Henry Schreiner, who maintains projects across scientific Python, PyPA, and C++, wrote up months of running Fable-powered code review over dozens of repositories. He counts roughly 400 bugs found, plus another 400-odd performance and modernization improvements, feeding several hundred pull requests — nearly every PR he decided to submit was merged. Highlights include cutting a pyhs3 runtime from 118 to 73 seconds, catching a nox bug that deleted sessions with non-ASCII names, and finding an option-interaction bug in CLI11. He calls it the best signal-to-noise ratio he has seen from automated review, ahead of Opus and well ahead of Kimi/OpenCode, where only about 70% of findings were worth acting on.

### [A pipx review with a false-positive rate near zero](https://github.com/pypa/pipx/issues/1856) — Henry Schreiner
Schreiner ran a four-pass Fable review of pipx and filed the results as a public issue. The findings include corrupt metadata crashing venv-listing commands, an invalid pip flag translation in the uv backend, metadata pollution from `--force`, a shared-list mutation, and `--editable` silently dropped in multi-package installs. He verified the top findings against the source and reproduced two of them locally, saying he has been "really happy" with the results and that the false-positive rate is close to zero.

### [A maintenance sweep of meson-python, down to line numbers](https://github.com/mesonbuild/meson-python/issues/861) — Henry Schreiner
A Fable review of meson-python found no showstoppers but produced a ranked list of genuine maintenance issues: a Windows path normalization bug, missing `check=True` on subprocess calls that read RPaths, an invalid `direct_url.json`, a typo in the wheel filename regex, and a hang on symlink cycles — each with file and line references, suggested priorities, and testing guidance. Schreiner again reported near-zero false positives and offered to generate fixes.

### [A release-blocking regression caught in PyPA's packaging library](https://github.com/pypa/packaging/issues/1239) — Henry Schreiner
Six Fable agents run in parallel over `packaging`, the library underneath most of Python's packaging tooling, found an unreleased release-blocking regression in boundary-version ordering. Schreiner independently reproduced every high-severity claim, backed the ordering bug with 28 fuzzing divergences, and reported further marker-evaluation bugs, with fixes linked from the issue.

## 2026-07-02

### [Four subtle robustness fixes in an agent orchestrator](https://github.com/lynxsyn/aide/pull/17) — lynxsyn
A Claude Code session running Fable fixed four operationally subtle bugs in aide's agent fan-out dispatcher: failed dependencies now terminally block the lanes waiting on them, clean but detached git worktrees are safely auto-repaired, merged workers are only reaped after two consecutive idle polls, and tmux pane snapshots now cover all windows so dev-server child processes stop leaking. Each fix ships with a targeted test for its failure mode.

### [Fable as the triage brain in a spreadsheet compatibility pipeline](https://github.com/FRIKKern/barkpark/pull/805) — FRIKKern
The barkpark spreadsheet app is using Fable as the coordinating layer in a multi-agent workflow: "miner" agents dig up Excel-compatibility gaps, and Fable selects and sequences which fixes to land. This batch shipped five of them — COUNTIF/SUMIF/AVERAGEIF criteria semantics, #N/A handling, anchor-aware formula fill, number-format rendering, and an undo-stack repair — each built in an isolated worktree with self-review and test coverage described in the PR.

### [Overlapping drum hits fixed in a real-time audio plugin](https://github.com/rutgerwolf/Adaptive-drumming-vst/pull/11) — rutgerwolf
A finding from a Fable review led to a low-level fix in this adaptive drumming VST: the synth and sampler engines shared a single voice cursor, so overlapping drum hits cut each other off. The fix introduces fixed four-slot voice pools while respecting the plugin's real-time-safety constraints, and deterministic tests show overlapping kicks now stacking to 1.5 amplitude where the old code could never exceed 0.5.

### [A 4x speedup in a Julia dynamic-programming library, with 260 new tests](https://github.com/QuantEcon/ContinuousDPs.jl/pull/93) — oyamad / QuantEcon
A Fable-authored PR to ContinuousDPs.jl adds a non-allocating kernel for evaluating tensor-product interpolants at a single point, then uses it inside the library's dynamic-programming loops. The benchmark table speaks for itself: `bellman_operator` drops from 779µs and 36,452 allocations to 396µs and 102 allocations, and `solve_PFI` from 24.8ms to 6.6ms. The change comes with 260 new tests checking agreement with the existing evaluator across Chebyshev, spline, linear, mixed-dimensional, and boundary cases, and is written generally enough to lift upstream to BasisMatrices.jl.

### [Shaving package load times inside the Julia compiler itself](https://github.com/JuliaLang/julia/pull/62250) — gbaraldi / JuliaLang
A Julia core developer landed a Fable co-authored optimization to the compiler's subtyping code that skips repeated typevar-aliasing walks for closed queries, recovering about half of a known package-image load-time regression: StaticArrays goes from 211ms to 158ms, Graphs from 0.72s to 0.60s, ReverseDiff from 2.86s to 2.65s. The author's own framing — "AI slop ahead though it's kinda nice" — undersells a targeted compiler patch that passed the core test suite.

### [Integration-boundary bugs found in a marine navigation server plugin](https://github.com/KEGustafsson/signalk-edge-link/pull/181) — KEGustafsson
A deep Fable review of a Signal K plugin found the kind of bugs that only show up where packages meet: vessel data duplicated under a nested `vessels.vessels...` context on real servers, startup failures silently swallowed because the server never awaits `plugin.start()`, unattributed raw logs, inaccurate dashboard write-rate counts, and misrouted plugin status. Each fix was verified against the signalk-server source rather than assumed from documentation.

### [A music-practice app discovers data it was already storing](https://github.com/andrewdmason/mason-family-hq/pull/401) — andrewdmason
A nice example of a cross-layer fix: this family music-practice app had been storing per-note velocity and sustain-pedal data in its MIDI transcriptions all along — the parser was just throwing it away. After the Fable-built fix, notes are shaded by how hard they were played, a sustain-pedal lane appears under the piano roll, and playback uses the real dynamics — retroactively, for every previously recorded session. A synthetic-MIDI test locks down exact velocities and pedal timing.

### [A 14x faster i18n scanner that produces byte-identical output](https://github.com/JustasMonkev/i18n-string-check/pull/5) — JustasMonkev
Fable co-authored a three-part optimization of a hardcoded-string scanner: a lexical pre-scan that skips expensive tree-sitter parsing for clean files, AST context checks that run only after a literal actually matches, and similarity matching rebuilt on interned token ids with memoization. Scanning a clean 120-file corpus drops from 150ms to 17ms. The interesting discipline: output was verified byte-identical to the old implementation across 20 corpus and flag combinations, with the one deliberate behavior change documented in the README.

### [A security review that moved straight into fixes](https://github.com/molefrog/vetka/pull/5) — evangus / molefrog
A Fable review of a site-builder app produced a prioritized list of flaws and then fixed the critical ones in the same PR: domain takeover prevention, one-site-per-user enforcement, server-side session resolution to close a cross-user access hole, tightened CORS and CSRF rules, user emails removed from world-readable rows, and builder access gated to owners. Notably, the remaining anonymous-write risk is documented in the PR rather than glossed over.

### [Where Fable says no: a smart-contract security benchmark](https://github.com/0xSoftBoi/anthropic-fellowship/pull/5) — 0xSoftBoi
Not every report is a success story. A researcher expanding BRIDGE-bench, a benchmark of vulnerable cross-chain bridge contracts, from 3 to 16 verified contracts found that Fable 5 refused the exploit-analysis task in every framing tried — agentic, single-turn, and explicitly authorized-defensive — while Opus 4.8 engaged and identified the correct root cause on 15 of 16 contracts. For security teams whose work resembles exploit analysis, that's a real constraint worth knowing about, even in defensive, documented contexts.
