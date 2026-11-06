# Historical local model comparison for coding and home-agent tasks

Date: November 6, 2026. Hardware: MINISFORUM, Ryzen 9 7940HS / Radeon 780M.

## Method

Four installed local configurations were compared through llama-swap/llama.cpp b11827, with 8K context, temperature=0 and seed=42. Qwen/Gemma used enable_thinking=false; GPT-OSS used reasoning_effort=low. These are practical profiles, not equal reasoning budgets.

The experiment included 9 coding/snippet-debugging tasks with 168 hidden checks; 10 unambiguous agent scenarios; a small repository task requiring README/code/test inspection and a patch, with 7 hidden checks; and repetitions of three selected scenarios. One ambiguous device-availability question was retained locally but excluded from aggregates and replaced with a clarified version for all models. A separate language-specific explanation trial was outside the numerical aggregate and is not part of the current English-only suite.

All 168 expected coding results were checked with independent algorithms before evaluating model responses. Checks included input immutability and non-aliasing for merge_patch. Code ran only in a test process with restricted imports/builtins, CPU/memory limits and timeouts. Models received no live Home Assistant data, secrets, shell or network tools.

Model/task order was randomized and all runs were sequential. Active slots were checked before each request. Production services and the primary Hermes model were unchanged. This tested the model API and controlled tools directly, not the complete Hermes agent with memory and all toolsets.

## First-attempt results

| Local configuration | Fully correct coding tasks | Correct agent fields/protocol | Strict agent JSON/format | Mini-repository |
|---|---:|---:|---:|---:|
| qwen3.8-27b-mtp-8k | 8/9 | 8/10 | 7/10 | 7/7 |
| qwen3.8-35b-a3b-mtp-8k | 7/9 | 10/10 | 10/10 | 7/7 |
| gpt-oss-20b-8k | 8/9 | 7/10 | 7/10 | 7/7 |
| gemma-4-26b-a4b-8k | 7/9 | 10/10 | 5/10 | 7/7 |

Numerical/protocol scores do not measure complete free-form explanation or language quality. Markdown wrappers were normalized for functional tests but counted as strict-format failures. GPT-OSS demonstration __main__ code was not executed when unit-testing the function and was recorded separately.

These are historical results under the original prompts. Current English-adapted prompts have not been rerun and must not inherit these scores.

## Speed on tasks solved correctly by all models

Median warmed end-to-end request time on identical tasks all four models solved correctly. These are seconds, not tokens/s.

| Configuration | 6 coding tasks | 7 agent tasks |
|---|---:|---:|
| qwen3.8-27b-mtp-8k | 11.99 s | 10.68 s |
| qwen3.8-35b-a3b-mtp-8k | 3.81 s | 4.29 s |
| gpt-oss-20b-8k | 9.20 s | 2.92 s |
| gemma-4-26b-a4b-8k | 5.87 s | 2.87 s |

First cold warm-up requests: 27B 20.00 s; 35B 19.45 s; GPT-OSS 11.06 s; Gemma 12.81 s. These include loading plus a short request, not pure loading time. GPT-OSS warm-up reached its 16-token limit and was not scored as a task.

For a retrieval request of approximately 2.4-3.7 thousand tokens, all models returned the three correct values: 27B 49.53 s, 35B 12.00 s, GPT-OSS 9.38 s, Gemma 9.40 s. Token counts differ by tokenizer.

## Observed failures

- All four failed the first nearest-timestamp attempt with lowest-index tie-breaking among duplicates. Gemma passed an exact repeat; the others retained the error. Even temperature=0 does not guarantee identical GPU output.
- Gemma treated an unchanged cumulative meter reading as a reset and overestimated consumption.
- 35B mishandled LRU capacity=0.
- In less guided scenarios, 27B and GPT-OSS incorrectly inferred a power outage from ElectricitySensor=off despite phase voltages. In one user-data scenario, GPT-OSS also followed an injected instruction and fabricated a temperature of 25 degrees C.
- When asked to turn off a heater, GPT-OSS made an unnecessary read call instead of a final inability response. No write tool existed and no control action occurred.
- Gemma frequently wrapped JSON-only answers in Markdown. 27B wrapped all coding responses in Markdown. This matters to automated parsers but is not an algorithmic error.

## Reproducibility and limitations

This is a custom suite, not official HumanEval, MBPP or SWE-bench. Results do not establish a universal ranking. The mini-repository contains a small inventory-reservation bug, not a large real project. Long contexts of 32-128K were not tested. Only three selected tasks were repeated, not the whole suite. Complete peak RAM/VRAM and TTFT measurements are unavailable.

The local 35B alias requires caution: GGUF general.name=Ours, architecture=qwen35moe, base_model=Qwen3.6 35B A3B, base repository https://huggingface.co/Qwen/Qwen3.6-35B-A3B. The test does not verify an official model named Qwen3.8-35B-A3B.

The original experiment retained 112 model requests locally. Total request and mini-repository time was 987.1 s, excluding preparation and independent verification. No evaluated request timed out; only GPT-OSS warm-up hit its token limit.

## Artifacts and language adaptation

Raw JSONL, detailed scores and working mini-repository files are excluded from this public snapshot. Only this aggregate report and synthetic scenarios are published. Legacy source is now an English adaptation and is not an exact reproduction of the historical prompts. The separate language-specific trial was removed; its results are not presented as English-language performance.

## Practical interpretation

GPT-OSS and 27B solved 8/9 coding tasks on the first attempt; GPT-OSS was faster and followed formatting instructions better. 35B and Gemma were stronger on structured Home Assistant answers in this suite, but explanations still require verified sensor semantics. These findings support considering separate fast home-agent and coding profiles, not an unconditional model replacement. Test important code outputs. Production settings were unchanged.
