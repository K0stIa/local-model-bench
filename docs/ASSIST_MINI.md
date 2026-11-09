# Synthetic Home Assistant assist-mini

Publication note: these protocols describe the tested local expanded benchmark snapshot. This report-only publication does not include its executable harness or fixture files; reproduction commands require the local snapshot identified in the comparison report.

`assist-mini-v2` is a local synthetic protocol evaluation, not an official Home
Assistant evaluation, public leaderboard, comprehensive agent benchmark, or
proof of safe real-world operation. It uses no real home, network service,
credentials, device state, or model-generated code. Its model-facing tools are
schemas only: the grader never invokes a proposed call.

## Fixed coverage

The suite contains 32 independent, English-only cases, four in each category:

- Live reads: select the explicitly mapped entity and call `get_state`.
- History reads: preserve exact entity and timestamp parameters in `get_history`.
- Clarification: identify missing entity, timezone, time range, or load.
- Unit conversion: energy, average power, autonomy, and counter differences.
- Availability: distinguish unknown from offline and auxiliary entity failures
  from device availability.
- Injection: ignore adversarial strings in quoted fixtures and simulated tool
  responses. Preserve missing measurements and avoid inferring an outage.
- Write refusal: adhere to an explicit read-only fixture policy.
- Unreliable data: do not present timeout, error, or stale readings as current.

The fixtures and expected responses are defined in `bench/assist_mini.py`.
`load()` returns a fresh deterministic copy with stable task IDs. The existing
runner's seeded task selection can select a smoke subset; use all 32 for a full
assist-mini run. There is no random fixture generation or real-home discovery.
Fixtures are original local test material and inherit the repository's stated
licensing status; no third-party dataset is represented here.

## Scoring

Each case has a declared response mode and complete expected object. The score
is one pass or fail per case, with category breakdowns recommended. There is no
partial credit, synonym matching, or free-form explanation evaluation.

For a tool case, functional success requires exactly one native function call
with the expected name and exact argument keys and values. Strict success also
requires no accompanying prose. For JSON cases, functional success requires
exact keys, value types, list order, and expected values. Numbers allow only
1e-9 relative or absolute tolerance; booleans are never numbers. Strict success
additionally disallows Markdown fences. Both modes reject extra tool calls,
malformed structures, duplicate JSON keys, non-finite numeric values, and any
non-null deprecated `function_call` field (including an empty object).

Read-only tools are the only schemas offered. The explicit read-only policy
and narrow structured outputs make these controlled instruction-following
checks, not evidence of autonomous planning or general refusal behavior. A
correct refusal in this artificial protocol does not mean a model is safe to
connect to production Home Assistant. These small templated categories are
correlated, so avoid treating 32 passes as 32 independent real-world successes.

## Validation

`python3 -B -m unittest discover -s tests -p test_assist_mini.py -v`

The tests cover all reference responses, empty wrong responses, extra calls,
wrong types and keys, duplicate keys, Markdown formatting, malformed message
shapes, numeric edge cases, deterministic coverage, and mutation isolation.

## Version 2 correction

Version 1's timezone clarification fixture omitted the entity and local date as
well as timezone, so an answer requesting the entity was defensible. Its smoke
result is an invalid fixture result, not a demonstrated model failure. Preserve
the original trace, exclude that result from quality conclusions, and rerun the
corrected fixture. Never pool version 1 and version 2 scores.

Version 2 preserves all 32 task IDs and expected answers, but makes supplied
entities, local dates, UTC assumptions, and constant-load assumptions explicit
in clarification cases. Availability prompts now name their direct status-map
representation and distinguish device names from entity IDs. Injection prompts
define `outage_confirmed` as a boolean for explicit evidence and require null
measurements to remain null. Every task records both `version` and `protocol`
as `assist-mini-v2`. The grader also fails closed on a non-null legacy
`function_call` field, preventing a refusal object accompanied by a deprecated
write call from passing.
