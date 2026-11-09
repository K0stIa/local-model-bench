# Public and synthetic benchmarks: 6 completed models

Measured on November 7-8, 2026, sequentially on the same local system. This is a local adapted-protocol comparison, not an official leaderboard, a repository-engineering evaluation, or proof of agent safety.

All six models completed 164 HumanEval+ tasks, 100 frozen BFCL cases and 32 assist-mini v2 cases: 1,776 full scored attempts. Smoke checks are excluded from these totals.

## Quality

Functional correctness and strict formatting are separate. HumanEval+ includes all 164 tasks and all 124,253 available base/plus inputs; each failing candidate stops at its first failed assertion, so this does not mean every failing candidate executed every input. Assist-mini v2 contains 32 synthetic cases.

| Model | HumanEval+ functional /164 | HumanEval+ strict /164 | Assist functional /32 | Assist strict /32 |
|---|---:|---:|---:|---:|
| qwen35 | 142 | 124 | 32 | 32 |
| gemma26 | 152 | 152 | 32 | 9 |
| laguna | 145 | 35 | 32 | 32 |
| gptoss20 | 145 | 145 | 32 | 31 |
| qwen27 | 145 | 120 | 26 | 22 |
| gemma12 | 155 | 155 | 32 | 8 |

GPT-OSS is a separate native-low reasoning track with a 4096-token ceiling. All other models use the practical 2048-token profile with enable_thinking=false. Do not describe this as equal-compute reasoning versus nonthinking.

## BFCL: native tool-call compatibility

The frozen sample has 20 cases in each category. Calls are scored as data and never executed. This uses an adapted exact-alternative grader, not the official BFCL AST evaluator.

| Model | Simple /20 | Multiple-choice tools /20 | Irrelevance /20 | Parallel /20 | Parallel-multiple /20 | Common zero/one-call cases /60 | Full native-stack result /100 |
|---|---:|---:|---:|---:|---:|---:|---:|
| qwen35 | 20 | 17 | 17 | 14 | 19 | 54 | 87 |
| gemma26 | 20 | 15 | 15 | 16 | 17 | 50 | 83 |
| laguna | 18 | 14 | 15 | 0 | 0 | 47 | 47 |
| gptoss20 | 19 | 15 | 17 | Unsupported | Unsupported | 51 | 51 (compatibility only) |
| qwen27 | 20 | 17 | 16 | 13 | 15 | 53 | 81 |
| gemma12 | 19 | 15 | 17 | 15 | 18 | 51 | 84 |

GPT-OSS native template reports no parallel-call support, and the pinned specialized parser permits only one call. Setting parallel_tool_calls=true would not enable repetition in that parser. Its 40 parallel cases are unsupported by the tested stack, not demonstrated reasoning failures. Compare every model on the identical common 60 cases separately; never mix a 60-case percentage with a 100-case percentage. [Pinned parser](https://github.com/ggml-org/llama.cpp/blob/970b51ce7/common/parsers/gpt-oss.cpp#L91-L125).

Laguna reports parallel support enabled, and its grammar allows repeated calls. It nevertheless returned only the first call in many multi-call requests. This is observed single-turn behavior of the model plus native runtime, not proof that a multi-turn agent could never finish those requests. [Default capability handling](https://github.com/ggml-org/llama.cpp/blob/970b51ce7/tools/server/server-common.cpp#L1338-L1346).

## Measured timing

Medians below are response wall times, not time to first token or total benchmark duration. Prompt-cache reuse, tokenizer differences, output length and reasoning affect latency; these are not repeated fixed-workload hardware trials. Qwen27 was resumed across processes, so its combined medians include a cache/order discontinuity.

| Model | Median response seconds: H+ / BFCL / Assist | Median decode tokens/s: H+ / BFCL / Assist |
|---|---:|---:|
| qwen35 | 6.96 / 5.03 / 1.47 | 27.03 / 26.83 / 26.77 |
| gemma26 | 8.19 / 2.64 / 1.45 | 26.36 / 26.13 / 26.29 |
| laguna | 6.62 / 3.66 / 1.29 | 35.01 / 34.55 / 34.48 |
| gptoss20 | 7.15 / 2.89 / 1.96 | 27.17 / 27.07 / 27.13 |
| qwen27 | 22.60 / 26.35 / 8.69 | 3.89 / 3.90 / 3.91 |
| gemma12 | 20.39 / 5.28 / 3.26 | 10.37 / 10.34 / 10.38 |

## Failures and validation caveats

- No transport/runner errors occurred in the completed full runs. Incorrect outputs, syntax/runtime failures, resource-limit failures and truncation remain counted as failures.
- Qwen35 truncated HumanEval/76; Gemma26 truncated HumanEval/130. These reached the 2048-token generation ceiling.
- Gemma26, Laguna, Qwen27 and Gemma12 each returned exit 137 on HumanEval/163 under the bounded execution environment. The CPU cap is 60 seconds and reference generation shares the resource budget. These remain failures; exit 137 is not itself proof of which limit fired, nor a pure semantic-correctness verdict. No sandbox wall-time timeout occurred.
- The upstream canonical HumanEval/32 Newton reference violates the official polynomial residual tolerance on 7 of 888 inputs. The correct residual oracle and all inputs are retained. Canonical validation is 163/164, not 164/164. See the protocol document for details.
- An initial assist-mini v1 smoke prompt had multiple missing fields but expected only one. That smoke result is excluded as invalid fixture evidence. All full runs use the corrected v2; Qwen repeated the corrected smoke IDs as the first three full cases.
- An interrupted startup before any inference is preserved locally and excluded from model scores. Raw outputs, logs and tool transcripts are not published.

## Reproducibility and isolation

All six runs use llama.cpp build11827, commit970b51ce7, the same Vulkan build, context8192, one slot, requested99 GPU layers, flash attention on, native Jinja templates, f16 KV defaults, MTP off, temperature0 and seed42. Exact model hashes, binary hash, flags, profiles, protocols and per-run source hashes are in SUMMARY.json. GGUF size is a disk measurement, not a RAM-peak measurement.

| Model | GGUF | Size GiB | SHA256 |
|---|---|---:|---|
| qwen35 | Qwen3.8-35B-A3B-Q4_K_M.gguf | 20.222 | 196103269085bc54c9b8f49ed21e9f53e1b56b465e8b796c6d8e31e06f63cfa5 |
| gemma26 | gemma-4-26b-a4b-it-qat-q4_0.gguf | 13.448 | 4c856523d61d77922dbc0b26753a6bf6208e5d69d80db0c04dcd776832d054c5 |
| laguna | Laguna-XS-2.1-Q4_K_M.gguf | 18.882 | 1ac7079101fca5a6df8c5a7523a3c30ea7d1c0e4b1258090e7d6d4039287f6cb |
| gptoss20 | gpt-oss-20b-mxfp4.gguf | 11.278 | be37a636aca0fc1aae0d32325f82f6b4d21495f06823b5fbc1898ae0303e9935 |
| qwen27 | Qwen3.8-27B-Q4_K_M.gguf | 17.671 | c600de0300ae8a0eb3a6c0b8b5561b8b96f16bd2c863c2a66c42de29d391a747 |
| gemma12 | gemma-4-12b-it-qat-q4_0.gguf | 6.497 | faff1a63667fac17ac5e777f47114688fcefea96e220e211aaa8d62c2c4561f1 |

Generated coding solutions run in fail-closed bubblewrap: no home or credentials mounted, no network, read-only system files, bounded temporary storage, process/output/file limits. HumanEval+ uses 60 seconds CPU, 90 seconds wall and 1 GiB address space shared by reference generation and candidate evaluation. This is defense in depth, not a VM or tamper-proof Python grading. Tool-call/HA scenarios never execute proposed calls and never contact a real home. Production configurations were unchanged; the controller stops only its own benchmark processes if production inference becomes resident.

The first Qwen35 H+ run uses commit 0611877; subsequent full primary runs use 4d8cf05. The only intervening benchmark change was assist-mini v2, applied before every full assist run. H+ and BFCL acceptance rules were unchanged. After the primary batch, launcher-status and NumPy-preflight hardening does not change task scoring rules.

## Restart and reproducibility

Qwen27 stopped when production became resident, after 155 HumanEval+ results. A checkpoint-aware controller resumed only the nine missing tasks into a new file, then completed BFCL and assist-mini. The 155 original results and three smoke files were SHA256-verified unchanged. The missing-only subset was seeded independently, changing its order and cache state; quality coverage remains identical, but timings are not a continuous run. Gemma12 then ran sequentially from fresh files. All resumed requests used source digest `1e939add0a4dc99d658e734e23c80f6eee173b47b162bff14151462ff51d6d5e`, with unchanged task acceptance rules. Qwen27 used a 900-second request timeout and Gemma12 600 seconds, compared with the earlier models' recorded shorter limits; no transport timeout occurred. Inspect per-file provenance rather than assuming equal timeout budgets.

The production residency/process guard ran every two seconds and an exclusive lock prevented a second benchmark controller. Only owned benchmark processes were stopped. The queue ended at 2026-11-08T11:57:12Z; no benchmark server remained and production was idle. No model downloads or production configuration changes were made.

Publication scope: this revision adds the report, aggregate summary, protocol documentation and dataset provenance only. The expanded harness, auditor script and benchmark fixture files remain in the tested local snapshot `a16e24e39aac5aae6222cd34ade162fd01e66a07`; that local commit is not published by this report-only update. Commands below require that local snapshot and retained traces, and are not runnable from this public revision alone. Raw model outputs are deliberately excluded.

Rebuild the aggregate from the tested local snapshot:

```sh
python3 -B scripts/summarize_expanded.py --input-root LOCAL_TRACE_ROOT --output results/public-20261107/SUMMARY.json
python3 -B -m unittest discover -s tests -v
```

The auditor accepts full and resumed result files, verifies unique complete IDs, exact requests against the current task fixtures, model identity, sampling profiles, all 124,253 input cases, and per-file hashes. It exports an allowlist of runtime metadata and aggregate scores only. Source manifests record the original measured code; report-only changes do not rerun inference. Without the local traces, the published JSON supports inspection but not independent replay of the observed outputs. To reproduce new inference, follow the protocol document and use new output files with the recorded profiles and runtime flags.

## Earlier smoke comparisons: separate evidence

The earlier 29-task suite used nine custom coding tasks, ten synthetic agent scenarios and a seeded ten-task HumanEval subset. Its task set and grading differ from this expanded run: do not combine scores or treat a model's change between tables as a controlled improvement/regression.

| Model | Earlier custom coding /9 | Earlier agents /10 | Earlier HumanEval smoke /10 | Expanded coverage here |
|---|---:|---:|---:|---|
| Qwen35 | 7 | 10 | 10 | Complete |
| Qwen27 | 8 | 9 | 10 | Complete |
| Gemma26 | 8 | 10 | 10 | Complete |
| Gemma12 | 7 | 8 | 10 | Complete |
| Laguna | 8 | 7 | 9 | Complete |
| GPT-OSS | 8 | 7 | 10 | Complete, separate reasoning track |
| MiMo9 | 3 | 7 | 9 | Not measured |
| Devstral | 8 | 7 | 9 | Not measured |
| GLM | 5 | 7 | 9 | Not measured |
| TwIL practical | 6 | 6 | 9 | Not measured |
| TwIL native thinking | 7 | 8 | 10 | Not measured; different sampling/budget |

These are functional scores only. Earlier strict scores and timings are retained in the [seven-model report](../seven-models-20261107/REPORT.md) and [earlier five-model comparison](../comparison-20261107/REPORT.md). TwIL native used temperature 1, top_p 0.95 and 4096 tokens, with two coding truncations and 115.71-second median custom-coding latency; its gains cannot be attributed solely to thinking. Earlier Qwen MTP performance tests used a separate repetitive fixed-budget workload and q4_1 KV; the quality tables here use MTP off and f16 KV. No MTP-on full-suite quality equivalence is claimed.

## Practical reading

- Gemma12 leads observed expanded coding correctness at 155/164, followed by Gemma26 at 152/164. This does not prove a general size/quality reversal: it is one quantized, seeded, public task set with resource bounds and possible training contamination.
- Gemma26 offers faster coding responses (8.19-second median versus Gemma12's 20.39) with 152/164 passes. Gemma12 is a useful smaller-footprint coding option, not the fastest option on this machine.
- Qwen35 leads full BFCL native-stack score at 87/100 and retains strict assist-mini 32/32. Gemma12 passes all assist cases functionally but only 8/32 strictly; Markdown/format handling matters.
- Qwen27 achieves 145/164 coding, 81/100 BFCL and 26/32 assist, at low MTP-off throughput. It does not displace the faster balanced alternatives on this experiment alone. Its exact files and production settings were left untouched.
- Laguna is fast and has strict assist-mini 32/32, but parallel-call failures limit its full BFCL score. GPT-OSS should be compared separately for native reasoning and on the same common 60 tool-call cases, not penalized as a pure reasoning failure for unsupported parser behavior.

Small, public and synthetic sets do not establish broad production superiority or agent safety. No automatic model deletion or production replacement follows from this report.

See [protocol details](../../docs/PUBLIC_BENCHMARKS.md), [BFCL provenance](../../data/bfcl/PROVENANCE.json), [HumanEval+ provenance](../../data/humanevalplus/PROVENANCE.json), and [aggregate JSON](SUMMARY.json).
