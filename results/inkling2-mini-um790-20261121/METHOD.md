# UM790 Pro local benchmark, 2026-11-21 UTC

Paired deployment configuration comparison on AMD Ryzen 9 7940HS / Radeon 780M RADV with shared memory. Benchmark harness: K0stIa/local-model-bench commit 33b236cbf1dc58448a2f163c8590c77148e2e994. No live service or private workload was tested. The sanitized aggregate JSON records exact flags, hashes, timing samples and scored IDs.

## Inputs

- Local Qwen main Q4_K_M: 21,713,462,944 B, SHA-256 196103269085bc54c9b8f49ed21e9f53e1b56b465e8b796c6d8e31e06f63cfa5. Q4_K_M MTP draft: 1,260,898,560 B, SHA-256 18f95176984d111018218c9c845108acdde4b1b26a1a8e858207864145ee21be. The local alias says Qwen3.8; both GGUF headers identify the base as Qwen/Qwen3.6-35B-A3B. This comparison does not claim either file as an official new Qwen release.
- ggml-org/Inkling-2-Mini-GGUF IQ4_NL: 17,627,940,768 B, revision db61c5b492a6a034d986328d28274af0a439aa6c, SHA-256 cbdf3fa9dc50a4124977980f37da4f1fa764b0cfe800d275cd43d26ce2a81af4. [Pinned file](https://huggingface.co/ggml-org/Inkling-2-Mini-GGUF/blob/db61c5b492a6a034d986328d28274af0a439aa6c/Inkling-2-Mini-IQ4_NL.gguf).
- Practical Qwen executable: llama.cpp b11827 / 970b51ce7, SHA-256 92ff7abb8a59c94a98acdbca4f50aaf54d2cb08a05fad57b254587a101366aac.
- Inkling and Qwen control: [official b12606 Vulkan release](https://github.com/ggml-org/llama.cpp/releases/tag/b12606), commit e412c6f468b7b9e0f16f2540244236f8ad68e9ae, executable SHA-256 e95c6fa1c4046977a9208caec6f6765af801272892d98d8c432027db61683624, release archive SHA-256 0c48a9bde079519d5775296d4682599fc6173a6660fe4dc18d1d243cd9f610b4. Contains [#32694](https://github.com/ggml-org/llama.cpp/pull/32694), predates the NVFP4 scale-only fix [#32704](https://github.com/ggml-org/llama.cpp/pull/32704), which does not affect the measured ggml IQ4_NL quant.

## Reproduce

Use an idle host and a single isolated loopback server at a time. Supply local model and executable paths via variables:

    common=(--host 127.0.0.1 --slots --parallel 1 --ctx-size 8192 --device Vulkan0 --gpu-layers 99 --threads 6 --threads-batch 6 --batch-size 192 --ubatch-size 48 --cache-type-k f16 --cache-type-v f16 --no-warmup)
    nice -n 10 "$B11827" "${common[@]}" --port 19089 --alias qwen-local-mtp --flash-attn on --spec-type draft-mtp --spec-draft-model "$DRAFT" --spec-draft-n-max 2 --model "$QWEN"
    nice -n 10 "$B12606" "${common[@]}" --port 19090 --alias inkling2mini-iq4nl --flash-attn off --model "$INKLING"
    nice -n 10 "$B12606" "${common[@]}" --port 19091 --alias qwen-b12606-fa-off-mtp-off --flash-attn off --spec-type none --model "$QWEN"

Measured Qwen 8192/f16/MTP2 differs from the live long-context configuration (131072 configured cap, q4_1 KV, FlashAttention enabled and MTP up to four), which was not changed or timed here.

The same synthetic UTF-8 prompt starts with "Complete this numbered synthetic list with further numbered short sentences.\n". Append exactly 27 (short) or 355 (long) lines indexed from zero, each formatted as "{i}: The small robot checks a blue box and records the result.\n". Tokenizer counts differ by model. From the pinned checkout:

    python3 -m bench.performance --endpoint "$ENDPOINT" --profile profiles/performance.json --runtime-manifest "$MANIFEST" --server-pid "$PID" --prompt-file "$PROMPT" --output "$PERF_JSONL"
    python3 -m bench run --endpoint "$ENDPOINT/v1" --model "$ALIAS" --suite custom --seed 42 --profile profiles/native-default.json --timeout 100 --budget 300 --runtime-manifest "$MANIFEST" --output "$CUSTOM_JSONL" --task code_merge --task code_topo --task code_repo_counter --task code_repo_ttl --task agent_call_history --task agent_units
    python3 -m bench run --endpoint "$ENDPOINT/v1" --model "$ALIAS" --suite humaneval --limit 3 --seed 42 --profile profiles/native-default.json --timeout 100 --budget 300 --runtime-manifest "$MANIFEST" --output "$HUMANEVAL_JSONL"

Native measurements include one first request, three warm no-cache and three prefix-cache requests, 128 forced output tokens each. Quoted medians use warm no-cache only; first request is not guaranteed filesystem-cold. For each prompt, the separate TTFT probe made three localhost POST /completion streaming requests with temperature=0, seed=42, ignore_eos=true, cache_prompt=false, n_predict=8; wall time until first nonempty content SSE chunk is raw text TTFT, not time to a final answer. GPU peaks are device-global/sampled; RSS, shared GPU memory and host memory must not be added.

The native-default quality profile is temperature=0, seed42, max 1600 tokens, using the given model's own template/reasoning behavior. Functional and strict (format) scores are separate. HumanEval adapter smoke IDs from seed42: /153, /45, /46; this is not full-suite official pass@1. Inkling's original code_topo timed out after 89.55 s of the remaining 300 s suite budget; no scores for timeout or unrun primary HumanEval. Any separate extra-budget extension must remain labeled separately and not replace original rows.


## Separate Inkling quality extension

Same server flags, model, seed and native-default profile; isolated port 19092. Only timeout/budget changes:

    python3 -m bench run --endpoint "$ENDPOINT/v1" --model "$ALIAS" --suite custom --task code_topo --seed 42 --profile profiles/native-default.json --timeout 220 --budget 240 --runtime-manifest "$MANIFEST" --output "$EXTRA_TOPO_JSONL"
    python3 -m bench run --endpoint "$ENDPOINT/v1" --model "$ALIAS" --suite humaneval --limit 3 --seed 42 --profile profiles/native-default.json --timeout 220 --budget 540 --runtime-manifest "$MANIFEST" --output "$EXTRA_HUMANEVAL_JSONL"
