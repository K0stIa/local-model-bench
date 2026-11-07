# TwIL-8B balanced: coding-first evaluation

Status: file size and SHA256 verified; practical and native local evaluations completed.
See `results/comparison-20261107/REPORT.md` for the separate-track results.
Pinned provenance: `manifests/twil-8b-balanced.json`. No weights or measured scores
are included. The model has a non-commercial research license; review the pinned
upstream license before using it outside permitted research. This repository's
license does not replace model-license obligations.

## Two separate tracks

- Practical equal-budget: `profiles/twil-nonthinking-2048.json`, greedy, seed 42,
  2048 output tokens, thinking explicitly disabled through the chat template.
- Native-settings exploratory track: `profiles/twil-native-4096.json`, temperature
  1.0, top_p 0.95, seed 42, 4096 output tokens, thinking enabled. This is a bounded
  local test using supplied native sampling settings, not an official evaluation.

Verify the runtime/template actually honors enable_thinking before labeling a run
nonthinking. If unsupported, record that limitation rather than claiming parity.
Do not combine the two tracks into one ranking: sampling, reasoning and output
budgets differ. `standard-2048.json` alone does not explicitly disable thinking.

## Execution order and comparable conditions

Use an isolated localhost server, one slot, identical context/backend/KV-cache
settings and exact runtime build for compared runs. Record GGUF hash, runtime
flags and template in a sanitized runtime manifest. Verify the file size and
SHA256 against the candidate manifest before serving. Do not change production
Hermes, Home Assistant or llama-swap configuration.

Start with the nine coding tasks, then HumanEval10, then ten agent tasks. To avoid
duplicating the coding work, select code_* and agent_* IDs separately using
repeated --task flags; together these form custom19. Alternatively run custom19
as one batch, noting its seeded order is not coding-first.

```sh
python3 -m bench list --suite custom
python3 -m bench run --endpoint http://127.0.0.1:18081/v1 --model twil-8b-balanced \
  --suite custom --limit 19 --seed 42 --profile profiles/twil-nonthinking-2048.json \
  --timeout 180 --budget 3600 --runtime-manifest manifests/twil-runtime.json \
  --output results/twil-practical-custom19.jsonl
python3 -m bench run --endpoint http://127.0.0.1:18081/v1 --model twil-8b-balanced \
  --suite humaneval --limit 10 --seed 42 --profile profiles/twil-nonthinking-2048.json \
  --timeout 180 --budget 1800 --runtime-manifest manifests/twil-runtime.json \
  --output results/twil-practical-humaneval10.jsonl
```

Repeat with native4096 and distinct output paths, if time permits. Use the same
suite revision, English prompts, selected IDs, seeds, timeouts and hardware for
baseline reruns. Earlier Ukrainian agent-suite results are historical, not a
matched English-suite control. Never execute generated code outside the harness
sandbox. Missing or truncated cases are failures/incomplete runs, not successes.

Report coding separately: passed functions, 168-case coverage, HumanEval10 pass
count, timeouts/truncation, wall time, output usage and reasoning overhead when
available. HumanEval10 is a small adapted chat smoke test, not official HumanEval
pass@1; one seeded sample is not a statistical quality estimate. Keep all raw
synthetic results and describe uncertainty. No vendor benchmark scores are used
as measurements on this machine.
