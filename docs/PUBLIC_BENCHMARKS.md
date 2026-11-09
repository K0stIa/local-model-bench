# Public and synthetic benchmark protocols

Publication note: these protocols describe the tested local expanded benchmark snapshot. This report-only publication does not include its executable harness or fixture files; reproduction commands require the local snapshot identified in the comparison report.

## Scope

- `humanevalplus`: all 164 HumanEval+ v0.1.10 tasks and all 124,253 base/plus input cases, pinned by SHA256. Full functions are requested through chat. Differential expected outputs and generated code execute only in bubblewrap. Comparison rules follow EvalPlus v0.3.1, including the polynomial residual oracle. This is an adapted protocol, not an official leaderboard submission: base/plus are combined, fixed per-task resources replace reference-relative per-input timing, and reference generation shares the sandbox budget.
- `bfcl`: fixed 100-case stratified BFCL sample. See [BFCL protocol](BFCL.md). Native tool-call outputs are inspected, never executed. The exact-alternative grader is adapted and is not the official BFCL AST evaluator.
- `assist-mini`: 32 local synthetic read-only Home Assistant protocol cases. See [assist-mini](ASSIST_MINI.md). No real house, sensors, tokens, accounts or device actions are used. This is not an official public HA benchmark.

## Validation discoveries

The upstream HumanEval+ OriginFmt export was rejected: it contains fewer inputs than the canonical full format and a malformed special assertion for task 32. Only the canonical input-format file is used. Its complete source hash and license are in `data/humanevalplus/PROVENANCE.json`.

The official Newton reference for HumanEval/32 fails the official polynomial residual tolerance on 7 of its 888 inputs (zero-based combined indices 219, 277, 285, 499, 716, 750 and 794). The grader retains every input and the correct residual oracle. Do not report an all-164 canonical validation pass. Tests independently exercise the residual oracle on simple known polynomials. This known reference defect does not authorize weakening the model's tests.

HumanEval+ requires NumPy; this machine uses system Python 3.12 and NumPy 1.26.4. The existing sandbox's Debian BLAS alternatives links were inaccessible without `/etc`; the sandbox now sets a library path to already-mounted system BLAS/LAPACK directories instead of exposing `/etc`. No credentials or home directory are mounted. The CLI checks NumPy inside the sandbox before submitting any HumanEval+ inference request. Other operating-system layouts must pass this preflight. Launcher startup is distinguished with a pre-execution marker instead of classifying arbitrary candidate stderr as a launcher error.

HumanEval+ bounds are 60 seconds CPU, 90 seconds wall and 1 GiB address space for reference plus candidate. The larger bound is necessary for extreme Tribonacci inputs and the slow canonical reference for task 139. Other coding suites retain 5 seconds CPU, 8 seconds wall and 512 MiB. Every candidate retains no network namespace access, read-only system mounts, empty environment apart from explicit safe values, 16 MiB temporary storage, process/file/output limits and fail-closed isolation. This is defense in depth, not a VM or tamper-proof Python grading.

## Model-free checks

```sh
python3 -B -m unittest discover -s tests -v
python3 -B -m bench.verify_references
python3 -B -m bench list --suite humanevalplus
python3 -B -m bench list --suite bfcl
python3 -B -m bench list --suite assist-mini
```

## Run procedure

Use a dedicated loopback server, one model and one request at a time. Verify production inference is unloaded, and stop only benchmark-owned processes if production becomes resident. Never change Hermes or llama-swap. First run three cases from each suite; only proceed to full runs after transport, schema, sandbox and result-count checks pass. A low functional score is a measurement, not an infrastructure failure.

```sh
python3 -B -m bench run --endpoint http://127.0.0.1:18081/v1 \
  --model MODEL --suite humanevalplus --limit 164 --seed 42 \
  --profile profiles/standard-2048.json --runtime-manifest sanitized-runtime.json \
  --timeout 180 --budget 10800 --output LOCAL_RESULTS/full-humanevalplus.jsonl
```

Use `--limit 3` for smoke, `--suite bfcl --limit 100`, and `--suite assist-mini --limit 32`. Profile selection must respect each model's supported native reasoning behavior. The comparison order is Qwen35, Gemma26, Laguna, GPT-OSS. GPT-OSS native low reasoning with 4096 output tokens is a separate compute track from the 2048-token nonthinking models.

Record actual GGUF and runtime hashes, runtime version, flags, quantization, context, KV, backend, MTP status, sampling, seed, token budget, reasoning mode, NumPy version and measured total elapsed time. CLI `wall_s` is successful response latency, not total benchmark time including grading. Raw outputs stay local; publish only audited aggregates. No new model scores are claimed by this implementation document.
