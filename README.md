# Local Model Bench

Reproducible local benchmarks for coding, tool calling and interpretation of synthetic Home Assistant data. No connection to a real home, credentials or changes to Hermes/llama-swap. This is a sanitized public snapshot of a local benchmark repository.

## Included suites

- `custom`: 9 coding tasks (168 edge cases) and 10 structured agent scenarios. Specifications originate from the November 6, 2026 experiment; an ambiguous availability question was replaced with explicit device mapping. Current prompts and response fields are English-only.
- `humaneval`: 164 official OpenAI HumanEval tasks (MIT), with pinned commit and SHA256 in `data/humaneval/PROVENANCE.json`. `--limit 10 --seed 42` selects a deterministic smoke subset, **not official HumanEval pass@1**. We request complete functions through chat rather than raw completions; the full suite also uses an adapted protocol.
- Aggregate historical report: `results/legacy-20261106/REPORT.md`. Raw requests, responses, tool transcripts and detailed grading JSON remain local and are not published. Historical conditions differ from the current harness. Legacy sources are stored as `.py.txt`, not recommended executors; their prompts have been adapted to English, so they are not exact historical reproductions.
- Fail-closed `bubblewrap` sandbox for generated code: separate PID/network/user namespaces, no home filesystem, read-only root/system libraries, 16 MiB tmpfs, and CPU/RAM/output/time/process limits. This is defense in depth, not a VM or protection guaranteed against kernel exploits.

## Quick start

Requires Linux, Python 3.12+, git and bubblewrap with user namespaces enabled. No Python dependencies. Model-free validation:

```sh
python3 -m unittest discover -s tests -v
python3 -m bench.verify_references
python3 -m bench list --suite custom
```

Start a separate local OpenAI-compatible llama-server with `--host 127.0.0.1 --slots`, the correct model and its native chat template. The harness does not start services, download models or edit production configuration.

```sh
python3 -m bench run \
  --endpoint http://127.0.0.1:18081/v1 --model MODEL_ALIAS \
  --suite custom --limit 19 --seed 42 \
  --profile profiles/native-default.json \
  --timeout 180 --budget 1800 --output results/MODEL-custom.jsonl
python3 -m bench run \
  --endpoint http://127.0.0.1:18081/v1 --model MODEL_ALIAS \
  --suite humaneval --limit 10 --seed 42 \
  --profile profiles/native-default.json \
  --timeout 180 --budget 1200 --output results/MODEL-humaneval10.jsonl
python3 -m bench report results/MODEL-custom.jsonl
```

`--dry-run` prints selected tasks without network access or generation. `--task ID` selects a specific task. `--repeat 3` preserves every attempt rather than selecting the best. Output files use exclusive creation; existing runs are not overwritten.

Planning estimates: 19 custom tasks may take 3-15 minutes depending on model/reasoning, and HumanEval10 approximately 2-10 minutes. These are not guarantees. `--budget` and `--timeout` stop the client; after a timeout, verify the server stopped generation. The runner stops on the first transport error and never switches models automatically. The idle check is not an exclusive lock: use a dedicated benchmark server and coordinate GPU use.

## Fair comparisons

Record GGUF URL/revision/hash/quantization, runtime version, backend, context, GPU offload, KV types, sampling, max_tokens and reasoning mode. Copy only an allowlist of parameters, never entire private configuration. Local JSONL output contains exact requests/responses, profile, IDs, seed, timing, commit/dirty flag and harness source SHA256. `--runtime-manifest sanitized.json` embeds a separate manifest and its SHA256; runtime provenance is null without it. Keep an additional `runtime-manifest.json` beside each run. Audit results before any publication.

Do not force an always-thinking model into unsupported non-thinking mode. Profiles are explicit JSON files. LFM needs a larger max_tokens budget and native reasoning. `profiles/nonthinking.json` is only for models supporting enable_thinking; `reasoning-low.json` is for compatible endpoints. Native-default imposes no model-specific flags.

Coding correctness is separate from Markdown/JSON formatting. Agent functional scores check specified fields/calls, not complete explanation semantics, language quality or general safety. Small subsets have considerable uncertainty. Public tasks may occur in training data. Do not combine different seeds, subsets, quantizations or historical scores into a single ranking. English-adapted prompts have not inherited the historical model scores.

## Extending the suite

1. Add specifications, independent test cases and references to `bench/custom_coding.py`, or messages/tools and expectations to `custom_agents.py`/`agent_grading.py`.
2. Never add live sensor data or secrets. All fixtures must be synthetic and all repository text must be English.
3. Add grading unit tests; validate reference and known-wrong solutions.
4. Register new suites through `load_suite` with pinned datasets, licensing and provenance. Full SWE-bench needs large containers and long agent loops, so it is not enabled here.

## Validation

Model-free checks cover unit tests, sandbox home/network/timeout probes, all 164 canonical HumanEval solutions and 9 custom references. Candidate inference runs are separate and produce local JSONL results.

## Licenses

HumanEval uses MIT; its full unmodified upstream license accompanies the dataset. No reuse license has yet been selected for the original harness or synthetic fixtures. Public visibility does not grant a separate open-source license. Models have their own licenses and are not included in Git.

## Grading limitations

Comparisons are isolated from the candidate namespace; early exit does not imply success. The sandbox protects the host, but this Python harness is not cryptographically protected against deliberate grading attacks through introspection. Intentionally hostile code needs a separate VM and further hardening. This is not a guarantee of agent safety.

Candidate manifests in `manifests/` describe expected upstream hashes and pinned revisions, not completed downloads or measured results. Record local validation only after hashing the complete file. LFM always-thinking uses a separately recorded output budget (`profiles/lfm-native.json`); this is not an equal-compute comparison.

## Separate performance profile

`profiles/performance.json` and `python3 -m bench.performance` measure native llama.cpp prefill/decode, warm/cache phases and sampled memory. See [docs/PERFORMANCE.md](docs/PERFORMANCE.md) for the MTP/context/build matrix, cold/warm definitions and mandatory correctness checks. The runner does not change production services.
