# Isolated performance benchmarks

The runner does not start servers, install packages or change production configuration, BIOS, GPU/RAM allocation, swap or system caches. Use a dedicated localhost llama-server with `--slots`, one slot (`-np 1`) and a port unused by production services. Do not run concurrently with other generation. The idle check is not an exclusive lock.

## Test matrix

For each fixed model GGUF SHA256: MTP off/on times context sizes 8192/32768. Compare MTP only when the specific model, GGUF and build support it. Mark unsupported combinations as `unsupported`; do not substitute ordinary draft-model speculation.

Record exact argv, `--version`, commit/build flags/backend, quantization, GPU layers, batch/ubatch, flash attention and KV-cache types in the manifest. Never copy environment variables, private configuration or tokens. Keep experimental binaries in a separate directory and change only the binary for build comparisons. Never switch production symlinks or services. Keep other parameters constant.

For 512/4096 prompt tokens, use one synthetic UTF-8 prompt file per target length and validate its token count with the model tokenizer. Different tokenizers produce different counts: report measured `prompt_n`, not just the target. The default profile has 96 lines and does NOT guarantee a specific token count.

## Running

```sh
python3 -m bench.performance --endpoint http://127.0.0.1:18081 \
  --profile profiles/performance.json --runtime-manifest manifests/run.json \
  --server-pid 12345 --prompt-file /path/synthetic-prompt.txt \
  --output results/performance-variant.jsonl
```

`--dry-run` validates inputs without networking. Output uses exclusive creation and never overwrites existing files. A manifest is mandatory: arbitrary JSON whose contents and hash are preserved with results. Suggested fields: model_sha256, binary_sha256, build_commit, argv, mtp, context_size, prompt_target_tokens, backend, hardware, experiment_label.

Defaults: seed 42, greedy decoding, 128 decode tokens (`ignore_eos`), one first request, three repetitions without prefix cache and three with prefix cache. The `phase` field separates these groups. `warm_no_cache` remeasures prefill; `prefix_cache` represents a different scenario and is NOT included in its average. `first_request` only means the first request from this runner, not a guaranteed cold model or filesystem cache. For model-cold measurements, restart only the test server and externally time startup to readiness. Do not flush system page caches. Alternate off/on ordering between repetitions; repeat the full run if needed to distinguish temperature and background-load effects.

## Metrics and limitations

JSONL records contain metadata, measurements or errors. Native llama.cpp timings separate prefill/decode counts, milliseconds and tokens/s; wall_seconds includes HTTP overhead. For cached requests, prompt_n may count only tokens actually computed. Server timings are not streaming TTFT.

Memory is sampled every 250 ms: process RSS/HWM/swap, system MemAvailable/SwapFree and load average. RSS is not VRAM. HWM is cumulative over the process lifetime; short peaks may be missed. Shared UMA RAM cannot simply be added to RSS. Record available GPU metrics with a separate sampler rather than inferring them from RAM. The operator supplies the PID.

The runner stops on timeout/error. Verify the server finished the request before another test. Truncation or an incomplete decode budget invalidates a measurement. Report the median and min/max of warm repetitions, cached results separately, and retain raw samples locally. Three repetitions provide a preliminary signal, not strong statistical evidence. Audit all artifacts before publishing.

## Correctness is mandatory

Synthetic performance does not assess answer content. For each variant, separately run `python3 -m bench run` with identical profiles/seeds/custom tasks, followed by `python3 -m bench report`. Generated code runs only in the configured sandbox.

For MTP, compare deterministic output hashes on performance requests and correctness-suite pass/fail results. Matching hashes do not prove complete correctness; different hashes require investigation but do not automatically imply an error because numerical backend variation is possible. Do not accept a performance gain without checking quality and stability.
