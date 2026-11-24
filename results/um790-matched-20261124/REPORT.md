# UM790 Pro matched model rerun, 2026-11-24

**Takeaway:** Qwen is the better default on this machine for this workload. This small rerun found identical functional outcomes with a lower response time for Qwen. Inkling had one stricter formatting success in coding; that is not evidence of broader coding superiority.

| Metric | Qwen | Inkling 2 Mini |
|---|---:|---:|
| BFCL-derived tool tasks, functional / strict | 3/4 / 3/4 | 3/4 / 3/4 |
| HumanEval+ coding, functional / strict | 2/3 / 1/3 | 2/3 / 2/3 |
| Sum of tool response wall times | 66.99 s | 148.84 s |
| Sum of coding response wall times | 73.02 s | 446.38 s |
| Sum of response wall times | 140.00 s | 595.23 s |
| Median decode throughput | 28.31 token/s | 10.95 token/s |
| Median prefill throughput | 114.90 token/s | 54.36 token/s |
| Peak llama-server RSS | 2.24 GiB | 2.58 GiB |
| Peak device-wide VRAM | 15.52 GiB | 15.93 GiB |

Both models passed the same three tool cases and coding cases 105 and 111. Both failed coding case 81: Qwen's emitted implementation failed the differential tests; Inkling hit the 2,048-token output cap. The extra strict pass for Inkling was on coding case 111. RSS and device-wide VRAM are separately measured and must not be added on this unified-memory platform. Wall-time sums are for responses, not model loading, grading or entire harness elapsed time.

## Conditions

- MINISFORUM UM790 Pro, Ryzen 9 7940HS, AMD Radeon 780M, 64 GB installed RAM with 16 GiB reserved for the iGPU.
- Qwen Q4_K_M: local alias references 3.8, but the GGUF metadata identifies Qwen3.6-35B-A3B. These results do not establish a Qwen3.8 checkpoint's performance. Inkling 2 Mini IQ4_NL.
- Same upstream llama.cpp b12606 (`e412c6f46`), Vulkan, native chat templates, 8,192 context, f16 KV, up to 99 layers requested for offload, Flash Attention off, speculative decoding/MTP off, one slot, six threads. Temperature 0, seed 42, prompt cache off; output caps 1,024 tool / 2,048 code.
- One response per item per model. Same four selected BFCL-derived tool cases and three selected HumanEval+ coding cases. No concurrent benchmark servers. Coding outputs were tested in an isolated sandbox.

These task counts are not official BFCL or HumanEval+ leaderboard scores. Public items may have been seen during training. Results are for these quantizations, templates, caps and runtime only; they do not measure long-context, image, agentic repository work or MTP performance. No raw prompts, model responses, credentials or local configuration are published.

## Reproduction identifiers

- Tool suite: BFCL v4-derived, Gorilla revision `6ea57973c7a6097fd7c5915698c54c17c5b1b6c8`: `bfcl_parallel_multiple_81`, `bfcl_parallel_multiple_110`, `bfcl_multiple_26`, `bfcl_irrelevance_11`. Both failed `bfcl_multiple_26`. Coding suite: HumanEval+ v0.1.10, IDs 81 (1,006 inputs), 105 (1,004), and 111 (663).
- Harness commit: `a16e24e39aac5aae6222cd34ade162fd01e66a07`; harness source SHA-256: `1e939add0a4dc99d658e734e23c80f6eee173b47b162bff14151462ff51d6d5e`. Runtime executable SHA-256: `e95c6fa1c4046977a9208caec6f6765af801272892d98d8c432027db61683624`.
- Qwen GGUF SHA-256: `196103269085bc54c9b8f49ed21e9f53e1b56b465e8b796c6d8e31e06f63cfa5`; Inkling GGUF SHA-256: `cbdf3fa9dc50a4124977980f37da4f1fa764b0cfe800d275cd43d26ce2a81af4`.
- Throughput is the unweighted median of seven per-response llama-server timings for each model, not a pooled rate. Memory metrics sampled approximately every 0.4 seconds (`VmHWM` for process RSS, AMD device counters for VRAM). Qwen ran first; no separate warmup. Markdown fences caused Qwen's strict-only failure on case 111.
