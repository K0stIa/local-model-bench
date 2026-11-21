# Stronger community-benchmark pilot on UM790 Pro

Measured 2026-11-21 UTC on the same Ryzen 9 7940HS / Radeon 780M as the [initial report](REPORT.md). Separate fixed-budget pilot, not a full leaderboard run. Keep local Qwen MTP as the default: Inkling showed fully working parallel structured calls and passed three difficult coding cases, but had no functional success exclusive to Inkling in these selected tasks. These small subsets are not general capability claims.

## Paired headline results

| Suite | Configuration | Functional | Strict | Model-response total, s | Sampled TTFT median, s | Median output tokens | Median exposed thinking tokens, est. |
|---|---|---:|---:|---:|---:|---:|---:|
| BFCL adapted | Qwen | 5/6 | 5/6 | 49.22 | 5.94 | 301 | 172 |
| BFCL adapted | Inkling | 5/6 | 5/6 | 159.18 | 10.12 | 282.5 | 126.5 |
| HumanEval+ adapted | Qwen | 4/6 | 3/6 | 173.08 | 1.93 | 823 | 361 |
| HumanEval+ adapted | Inkling | 3/6 | 3/6 | 1380.46 | 4.12 | 3056.5 | 1665.5 |

BFCL correct responses by 15 s: Qwen 5/6, Inkling 0/6; by 30 s: 5/6 vs 3/6. HumanEval+ correct generated solutions by 30 s: 4/6 vs 0/6; by 120 s: 4/6 vs 1/6; by 240 s: 4/6 vs 2/6; by 360 s: 4/6 vs 3/6. Generation time ends at the completed model response and excludes grader execution.

## Selected tasks

Each cell is functional / strict with model-response elapsed seconds. No infrastructure failure was recorded. BFCL hypothetical calls were scored as structured data and never executed.

| Task | Qwen | Inkling |
|---|---|---|
| bfcl_parallel_multiple_81 | pass / pass, 5.30 s | pass / pass, 21.62 s |
| bfcl_parallel_multiple_85 | pass / pass, 10.55 s | pass / pass, 29.93 s |
| bfcl_parallel_multiple_110 | pass / pass, 9.44 s | pass / pass, 31.76 s |
| bfcl_multiple_51 | pass / pass, 4.60 s | pass / pass, 16.68 s |
| bfcl_multiple_26 | fail / fail, 12.83 s | fail / fail, 15.16 s |
| bfcl_irrelevance_11 | pass / pass, 6.50 s | pass / pass, 44.04 s |
| HumanEval/81 | pass / pass, 23.97 s | pass / pass, 286.91 s |
| HumanEval/105 | pass / pass, 18.13 s | pass / pass, 160.67 s |
| HumanEval/38 | pass / pass, 10.84 s | pass / pass, 67.82 s |
| HumanEval/132 | fail / fail, 66.20 s | fail / fail, 288.26 s |
| HumanEval/76 | fail / fail, 39.62 s | fail / fail, 288.32 s |
| HumanEval/111 | pass / fail, 14.31 s | fail / fail, 288.48 s |

Both local APIs reported support for tools and parallel calls, and both emitted all correct native calls in all three selected parallel-multiple cases (3, 4 and 4 calls). Both missed the same game-tool fixture: Qwen emitted the required rewards call plus one unnecessary missions call; Inkling emitted only the wrong missions call. This is single-turn exact scoring, not stateful multi-turn.

Both coded /81, /105 and /38 correctly. Qwen alone passed /111 functionally (strict output did not pass). On Qwen, /132 failed an assertion and /76's candidate was killed in the sandbox at approximately 60 s (exit 137, consistent with the existing CPU cap; not a completed model-inference timeout). Inkling's /132, /76 and /111 hit the shared 3,072-token output cap. Strict coding also requires the expected output format; strict BFCL enforces the exact native response structure in addition to correct calls.

## Provenance and scoring limits

- Existing **local** harness commit a16e24e39aac5aae6222cd34ade162fd01e66a07. The exact harness/fixture subset is not fully published; this result does not claim turnkey public reproducibility. Six independent reference programs passed the selected expanded inputs in the existing bubblewrap grader; no new packages or production services were used.
- [EvalPlus HumanEval+ v0.1.10](https://github.com/evalplus/humanevalplus_release/releases/tag/v0.1.10), full-input release SHA-256 272720b90ac375502c8ed23cd791c2a93dfb22a911641a494da74a426c09f101. Select tasks with ≥500 combined tests, rank by number of canonical AST If, IfExp, For, While, comprehension, ExceptHandler and Match nodes, then combined testcase count and numeric ID; exclude the existing /153, /45, /46 smoke tasks and documented /32 oracle exception. This is a deterministic complexity proxy, not a published difficulty rating. Standard grader 60 s CPU / 90 s wall.
- [Berkeley BFCL v4](https://gorilla.cs.berkeley.edu/leaderboard.html), pinned source revision 6ea57973c7a6097fd7c5915698c54c17c5b1b6c8; local pinned subset SHA-256 df5a3df5b38a20b42ba28a313c30894fbfa5153abc13953b41ab7c67c675d14c. Six benign tasks from parallel-multiple, multiple, and irrelevance. No tool action was dispatched.
- Both native chat defaults, temperature 0, seed 42, no forced common thinking effort. Matched per-request limits: BFCL 1,024 output tokens / 130 s; HumanEval+ 3,072 output tokens / 360 s; case runner budgets were 145 s and 375 s, with separate subprocess guards including grading. Native Qwen b11827 Vulkan MTP2/FA-on and native Inkling b12606 Vulkan FA-off, same bounded 8192 context settings as [METHOD.md](METHOD.md). End-to-end configuration comparison, not intrinsic model speed.
- Sampled TTFT is an independent, ungraded 8-token streaming probe of the same input, to first nonempty content, reasoning or tool-call delta. Thinking count retokenizes exposed reasoning text, an estimate (not exact inference usage). Completion output count is server-reported.
- Existing public problems may be familiar to either model. These selected tasks do not establish parity or superiority across suites.

[Sanitized aggregate and complete per-task measurement rows](strong-pilot.json).
