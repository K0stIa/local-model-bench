# Seven installed models: coding and agent comparison

Completed November 7, 2026 on the existing Ryzen 9 7940HS / Radeon 780M system. This is a small, single-attempt smoke suite, not an official leaderboard, full HumanEval pass@1, repository-engineering evaluation, or proof of agent safety.

## Protocol and coverage

All seven models completed the identical 9 custom coding tasks, 10 synthetic agent scenarios and seeded 10-task HumanEval subset (seed 42). Existing valid Qwen35 and Laguna runs were preserved; the other five were added. English prompts, executable grading, Vulkan llama.cpp b11827, 8192 context, one slot, f16 KV, full GPU offload and MTP off were used. The practical profile is temperature 0, seed 42, max_tokens 2048 and enable_thinking=false. No reasoning response field appeared in these six practical runs.

**GPT-OSS is a separate native reasoning track:** temperature 0, seed 42, reasoning_effort=low, max_tokens 4096 and a 360-second request timeout rather than 180 seconds. It emitted reasoning in all 29 responses. Its scores use the same tasks and grader, but its compute budget and reasoning mode differ. It must not be presented as an equal-budget nonthinking result.

No completed response was truncated; no transport error or sandbox execution timeout was recorded in the scored attempts. Gemma12's first HumanEval process was interrupted before any task result was saved. Its completed custom suite was preserved, and only the missing HumanEval suite was resumed. That incomplete, unscored attempt is not evidence of a model failure. The process restart may affect cache/latency conditions.

## Quality

Each cell is functional / strict-format passes. Functional coding scores require all cases for a task to pass; strict additionally requires the requested output format. Markdown fences account for many strict failures, so Qwen27's strict coding zero does not mean its code was incorrect.

| Model | Custom coding /9 | Agents /10 | HumanEval smoke /10 |
|---|---:|---:|---:|
| qwen35-english | 7/9 / 4/9 | 10/10 / 10/10 | 10/10 / 7/10 |
| qwen27-english | 8/9 / 0/9 | 9/10 / 8/10 | 10/10 / 8/10 |
| laguna-english | 8/9 / 2/9 | 7/10 / 7/10 | 9/10 / 2/10 |
| gemma26-english | 8/9 / 8/9 | 10/10 / 5/10 | 10/10 / 10/10 |
| gptoss20-native | 8/9 / 8/9 | 7/10 / 7/10 | 10/10 / 10/10 |
| gemma12-english | 7/9 / 5/9 | 8/10 / 4/10 | 10/10 / 10/10 |
| mimo9-english | 3/9 / 3/9 | 7/10 / 7/10 | 9/10 / 9/10 |

## Response latency and decode throughput

Medians across different tasks, not repeated fixed-workload hardware trials. Output length, tokenizer, prompt cache and reasoning affect these figures. These are wall times, not time to first token.

| Model | Wall seconds: coding / agents / HumanEval | Decode tokens/s: coding / agents / HumanEval |
|---|---:|---:|
| qwen35-english | 4.93 / 3.57 / 8.23 | 27.39 / 27.21 / 27.35 |
| qwen27-english | 32.56 / 22.28 / 21.12 | 3.90 / 3.90 / 3.90 |
| laguna-english | 4.12 / 2.94 / 6.99 | 35.64 / 35.03 / 35.24 |
| gemma26-english | 6.17 / 3.09 / 8.87 | 26.97 / 26.91 / 26.62 |
| gptoss20-native | 9.82 / 3.48 / 7.00 | 27.27 / 27.17 / 27.24 |
| gemma12-english | 17.24 / 7.18 / 22.34 | 10.26 / 10.24 / 10.35 |
| mimo9-english | 9.55 / 5.80 / 8.93 | 12.32 / 12.31 / 12.34 |

## Failure review

- Qwen35: nearest-index duplicate/tie behavior and LRU. All agent scenarios and HumanEval samples passed.
- Qwen27: nearest-index and injected tool-data handling. All HumanEval samples passed.
- Laguna: counter-reset handling, both injected-data scenarios, read-only refusal protocol and HumanEval/108. The refusal failure was an extra read call, not an observed device write.
- Gemma26: counter-reset handling only; unchanged readings were treated as resets. All agents passed functionally, but only half satisfied strict formatting.
- GPT-OSS: nearest-index, both injected-data scenarios and long-context retrieval. All HumanEval samples passed.
- Gemma12: nearest-index, LRU, unit conversion and injected tool-data handling. All HumanEval samples passed.
- MiMo9: merge patch, nearest-index, rolling window, energy, LRU and topological order; unit conversion and both injected-data scenarios; HumanEval/108.

All fixtures were synthetic. No real household data, write tools, production configuration changes or model deletions were involved. The guard terminated only benchmark processes if production became resident; production was idle before and after this run.

## Practical interpretation

- Gemma26 is the strongest balanced challenger in this small run: 8/9 custom coding, 10/10 agents and 10/10 HumanEval, with fast responses. Its agent output formatting still needs handling.
- Keep Qwen35 as the current agent baseline: 10/10 functional and strict agent responses. These tests do not justify changing Hermes automatically.
- Laguna remains a fast coding candidate. GPT-OSS is a useful coding candidate with clean formatting, but its separate reasoning budget and weaker agent results matter.
- Qwen27 improves custom coding relative to Qwen35 here, but its MTP-off baseline is much slower. Keep the exact local files until independent reproducible-download verification is complete.
- Gemma12 provides a smaller-footprint option, but is slower than Gemma26 on this hardware. MiMo9 is the weakest custom-coding candidate here and a reasonable first deletion candidate *if* these are the intended workloads. Neither should be deleted on this small sample without the user's decision and considering other use cases.

## Separate MTP performance evidence

The earlier fixed-budget experiment is not this quality run. On 514/2078-token repetitive prompts, Qwen27 MTP increased warm no-cache decode from 4.02/4.00 to 10.35/9.35 tokens/s (2.58x/2.34x); total latency improved from 21.85/40.38 to 12.47/32.35 seconds. Qwen35 MTP did not improve those workloads (27.75/27.37 versus 26.88/26.74 tokens/s). Those tests used q4_1 KV and 64-token native completions, so they must not be merged into the f16-KV chat latency table above. MTP-on full-suite quality equivalence has not been established. The model labels refer to installed artifacts; local Qwen35 metadata points to Qwen3.6-35B-A3B, not a verified official Qwen3.8 release.

## Provenance and validation

Aggregate JSON contains exact artifact hashes, runtime flags, profiles, task IDs, source hashes, result-file hashes, failure IDs and timing distributions. Raw prompts/responses, logs and host paths remain local. The source digest differs between preserved and new runs only because the reporting-only `bench/aggregate_comparison.py` was added; git comparison verifies no change to task generation, grading, data or profiles. The preserved source digest starts `5e45246a`; new runs start `b4fb9e44`.

Before inference, 39 unit tests passed, all 164 canonical HumanEval solutions passed, and all 9 custom references passed their 168 cases. One attempt per task has substantial uncertainty and possible public-data contamination. No filled 32K/128K test, sustained thermal benchmark, complete peak UMA memory measurement, full Hermes integration, or general engineering/safety claim is made.
