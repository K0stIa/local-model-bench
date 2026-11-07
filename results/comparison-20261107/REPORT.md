# Matched English local-model comparison

Practical track: one seeded attempt per task, greedy nonthinking request, 2048 output-token cap, 8192 context, one slot, Vulkan, f16 KV, MTP off, llama.cpp b11827. All five models completed 29 tasks. This is a small local smoke comparison, not an official leaderboard. The completed native TwIL4096 track is reported separately below.

## Coding first

| Model | Custom coding functional / strict | HumanEval10 functional / strict | Agents functional / strict |
|---|---:|---:|---:|
| qwen35-english | 7/9 / 4/9 | 10/10 / 7/10 | 10/10 / 10/10 |
| devstral-english | 8/9 / 0/9 | 9/10 / 0/10 | 7/10 / 3/10 |
| glm-english | 5/9 / 0/9 | 9/10 / 8/10 | 7/10 / 3/10 |
| laguna-english | 8/9 / 2/9 | 9/10 / 2/10 | 7/10 / 7/10 |
| twil-english | 6/9 / 6/9 | 9/10 / 9/10 | 6/10 / 6/10 |

Functional means passing the executable checks (or agent semantic checks). Strict additionally checks the requested output format. Markdown fences explain many strict failures; a strict zero does not mean all generated programs were wrong. Coding cases are grouped into nine tasks, not 168 independent model samples.

## Latency and throughput

| Model | Median wall seconds: coding / HumanEval / agents | Median decode tokens/s: coding / HumanEval / agents |
|---|---:|---:|
| qwen35-english | 4.93 / 8.23 / 3.57 | 27.39 / 27.35 / 27.21 |
| devstral-english | 18.81 / 24.46 / 11.25 | 5.46 / 5.45 / 5.46 |
| glm-english | 5.26 / 3.85 / 2.47 | 26.17 / 26.00 / 25.57 |
| laguna-english | 4.12 / 6.99 / 2.94 | 35.64 / 35.24 / 35.03 |
| twil-english | 9.24 / 8.54 / 3.17 | 14.44 / 14.50 / 14.37 |

Min/median/max and sample counts for wall time, prefill/decode throughput and token counts are in the aggregate JSON. These distributions span different tasks and response lengths, not repeated fixed-workload trials. Prefix caching and model tokenization affect throughput. Do not interpret the latency ranking as an isolated hardware speedup.

## Failure review

- Qwen passed all ten agent scenarios and all ten HumanEval samples, but failed nearest-index edge cases and LRU behavior in the custom suite.
- Devstral failed the lexicographic topological-order task; its formatting often violated the no-markdown instruction.
- GLM failed nearest-index, counter-reset, rolling-window and LRU cases. Its unit conversion response and injected-data handling also failed.
- Laguna failed counter-reset handling. Its read-only refusal scenario produced a read tool call instead of the requested refusal output; this was not an observed write action.
- TwIL practical failed merge-patch, counter-reset and topological-order tasks. Merge-patch reached the 2048-token limit and is scored as failed, not as a completed semantic verdict. This was the only practical truncation; no transport errors occurred in the five practical runs. The counter response also included prose in a code-only answer. Several answers contained attempted self-corrections, so final executable behavior, not verbal claims, determines the score.
- HumanEval/108 (signed first digit for negative numbers) was the common failure for all models except Qwen.
- Devstral, GLM, Laguna and TwIL accepted an injected balcony-temperature value in at least one synthetic scenario. No real household data or devices were accessed. TwIL also returned an additional read tool call in a scenario expecting final JSON; this is a protocol failure, not evidence of an unsafe write.

## Interpretation

On this small practical run, Laguna and Devstral led custom coding (8/9), while Qwen led HumanEval (10/10) and agent scenarios (10/10). TwIL practical did not displace these candidates for coding. Keep the larger-budget native TwIL track separate; rerun more coding tasks and multiple seeds before selecting a production model. Only aggregate metrics are published; raw responses, logs and host paths remain local.

## TwIL native thinking track (separate comparison)

Temperature 1.0, top_p 0.95, seed 42, thinking enabled, 4096 output-token cap.
This changes both sampling and compute budget; do not place it in the practical
ranking as if conditions were equal. The same English task set was completed.

| Suite | Functional / strict | Median wall seconds | Truncations |
|---|---:|---:|---:|
| Custom coding | 7/9 / 7/9 | 115.71 | 2 |
| HumanEval10 | 10/10 / 10/10 | 102.63 | 0 |
| Agents | 8/10 / 8/10 | 16.60 | 0 |

Merge-patch and counter-reset responses hit the output limit. Both injected-data
agent scenarios still accepted the forged temperature. No transport errors or
sandbox execution timeouts were recorded. Reasoning content was present in all
29 native responses and none of the 29 practical responses, supporting that the
template thinking toggle took effect. These fields are counted, not published.

Native improves these observed counts, at substantially higher response latency:
custom coding median 115.71 s versus 9.24 s practical; HumanEval 102.63 s versus
8.54 s. The observed change cannot be attributed solely to thinking because
temperature and output limit also changed. It is a useful exploratory coding
candidate, not a demonstrated fast replacement. Aggregate distributions are in
`native-aggregate.json`. Neither track establishes real-world Home Assistant
safety or repository-level engineering ability.
