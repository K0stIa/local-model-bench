# Inkling 2 Mini vs local Qwen MTP on UM790 Pro

One AMD Ryzen 9 7940HS / Radeon 780M computer, measured 2026-11-21 UTC with public synthetic fixtures. [Reproduction](METHOD.md).

**Recommendation: keep Qwen MTP as the default.** This configuration generated tokens **3.18× faster short** and **3.47× faster long**. Qwen was still **2.46× faster** in the short same-runtime, no-MTP/no-FlashAttention control. Inkling is a usable optional model: its tested file is smaller, its GTT demand was lower, and it scored better strict formatting on the five completed common custom tasks.

## Timing

Median (min–max) of 3 warm no-cache samples, 128 forced output tokens. Separate streaming TTFT from 3 short raw-text completions. Both variants used the same input text and an 8192 context cap; counts differ by tokenizer.

| Variant | Actual prompt tokens | Prefill, t/s | Decode, t/s | TTFT, s |
|---|---:|---:|---:|---:|
| Qwen MTP, short | 434 | 124.00 (123.83–124.19) | 36.21 (35.40–36.33) | 3.51 (3.50–3.57) |
| Qwen MTP, long | 5937 | 122.87 (122.80–122.87) | 34.73 (34.53–34.91) | 48.43 (48.40–48.54) |
| Inkling, short | 417 | 65.19 (65.18–65.67) | 11.40 (11.38–11.42) | 6.45 (6.38–6.68) |
| Inkling, long | 5337 | 60.48 (60.34–61.88) | 10.02 (9.90–10.03) | 88.32 (86.93–89.15) |
| Qwen b12606 FA/MTP off, short control | 434 | 129.86 (129.78–130.01) | 28.08 (28.07–28.10) | 3.35 (3.35–3.39) |

| Resource | Qwen MTP | Inkling |
|---|---:|---:|
| Model plus tested draft on disk, GB | 22.97 | 17.63 |
| Time from process start to server ready, s | 19.63 | 16.13 |
| Device-global peak VRAM, GiB | 15.95 | 15.87 |
| Device-global peak GTT, GiB | 6.89 | 2.51 |
| Minimum MemAvailable, GiB | 27.28 | 32.05 |
| Process RSS high water, long phase, GiB | 0.64 | 1.08 |

UMA memory measurements overlap and are not per-process GPU attribution. Startup timing is not a controlled filesystem-cold test. No safety guard trips.

## Correctness

The five completed matched custom tasks were functional 5/5 for both; strict formatting was 2/5 Qwen and 5/5 Inkling. Matched task wall totals were 57.85 s vs 210.46 s. Inkling's first code_topo attempt timed out on the remaining original suite budget; original Inkling HumanEval did not start. The separate extension had more time, not a larger token cap; its code_topo reached the unchanged 1600-token cap and failed. It does not replace the original rows.

Each cell: functional / strict, wall time.

| Existing task | Qwen primary | Inkling primary | Inkling separate extension |
|---|---|---|---|
| code_repo_counter | pass / fail; 25.85 s | pass / pass; 51.25 s | not run |
| agent_units | pass / pass; 6.77 s | pass / pass; 45.24 s | not run |
| code_merge | pass / fail; 7.17 s | pass / pass; 64.73 s | not run |
| code_repo_ttl | pass / fail; 7.36 s | pass / pass; 30.19 s | not run |
| agent_call_history | pass / pass; 10.69 s | pass / pass; 19.05 s | not run |
| code_topo | pass / fail; 29.33 s | unscored timeout; 89.55 s | fail / fail; 149.96 s |
| HumanEval/153 | pass / pass; 22.13 s | not run | pass / pass; 127.61 s |
| HumanEval/45 | pass / pass; 5.30 s | not run | pass / pass; 29.42 s |
| HumanEval/46 | pass / pass; 15.67 s | not run | pass / pass; 142.97 s |

Few deterministic tasks, not a capability ranking. HumanEval here is an adapted three-task smoke, not official full-suite pass@1. The primary pair differs in runtime, FlashAttention, MTP, quant and tokenizer; it is a usable configuration comparison, not intrinsic architecture speed. The short control aligns runtime, backend, FA and MTP, not quant/tokenizer or long-context performance.

[Primary measurements](primary.json) · [Short control](short-control.json) · [Separate extension](inkling-extension.json)
