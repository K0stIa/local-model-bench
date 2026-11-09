# Fixed BFCL sample

Publication note: these protocols describe the tested local expanded benchmark snapshot. This report-only publication does not include its executable harness or fixture files; reproduction commands require the local snapshot identified in the comparison report.

This suite is an **adapted BFCL-derived comparison**, not an official BFCL
leaderboard score. It uses 100 single-turn Python cases from BFCL v4 at
[Gorilla commit 6ea57973c7a6097fd7c5915698c54c17c5b1b6c8](https://github.com/ShishirPatil/gorilla/tree/6ea57973c7a6097fd7c5915698c54c17c5b1b6c8/berkeley-function-call-leaderboard).
The upstream Apache-2.0 license is preserved in `data/bfcl/LICENSE`.

## Frozen selection

The sample contains 20 cases from each of `simple_python`, `multiple`,
`parallel`, `parallel_multiple`, and `irrelevance`. Within each category,
all upstream cases were sorted by the hexadecimal SHA256 of the UTF-8 string
`42:` followed by the upstream task ID; the first 20 were selected. No cases
were removed based on content or model performance. Source category sizes
were 400, 200, 200, 200, and 240 respectively.

`data/bfcl/PROVENANCE.json` records all selected IDs, upstream question and
answer URLs, pinned revision, source byte sizes and SHA256 digests. The frozen
`subset.jsonl` combines each original question record, its category, and its
original possible-answer record (an empty answer list for irrelevance).
Its SHA256 is `df5a3df5b38a20b42ba28a313c30894fbfa5153abc13953b41ab7c67c675d14c`.
The loader verifies that digest before using it. No network is needed at run time.

## Adaptations and scoring

- Original single-turn user messages are unchanged. A synthetic-benchmark system
  message replaces the harness's general read-only policy, so hypothetical write
  functions are not incorrectly prohibited. No tool is actually executed.
- Function names are made OpenAI-compatible by replacing characters outside
  ASCII letters, digits, underscore and hyphen with underscores. The reversible
  mapping is stored on each task, and collisions fail closed.
- Python schema types `dict`, `float`, `list`, and `tuple` are converted to JSON
  Schema `object`, `number`, `array`, and `array`, respectively.
- Responses must use native `tool_calls` with JSON object argument strings.
  Python-call text, Markdown or calls embedded in prose are not interpreted.
- Expected argument alternatives are matched using exact JSON structural
  equality. Booleans are not numbers. Numeric integer/float equivalents are
  accepted; strings are case-sensitive and arrays are order-sensitive.
- An empty-string alternative allows an argument to be omitted, matching BFCL's
  optional-argument convention. Unexpected arguments and functions fail.
- Parallel calls require an exact one-to-one multiset match. Bipartite matching
  handles overlapping alternatives without greedy-order dependence. Missing or
  extra calls fail. No-call irrelevance responses pass regardless of explanation.
- Duplicate JSON keys, malformed calls, non-object arguments and non-finite
  numeric constants are rejected. Arguments are parsed as data only.

The official BFCL evaluator includes additional language parsing and
normalization behavior which this deliberately conservative grader does not
implement. Differences can lower or change measured accuracy. The functional field reports the structural call criterion; strict pass also
requires an assistant-role message with string/null content and either valid
calls or nonempty response text. Empty responses can satisfy functional no-call
irrelevance but never strict formatting. Non-null deprecated `function_call`
responses fail both criteria rather than being mistaken for no-call answers.
Neither criterion claims semantic explanation correctness, real-world agent
safety or full BFCL coverage. Report each category separately alongside the 100-case
micro-average. The equal category weights do not reproduce the full dataset's
category proportions. Public cases may be present in training data.

## Model-free checks

`python3 -B -m unittest discover -s tests -p test_bfcl.py -v` checks fixed
selection, schema conversion, optional arguments, malformed outputs, duplicate
keys, one-to-one matching, no-call cases, every selected reference answer,
negative function-name mutations, and the synthetic system prompt. These are
checks of the adapter, not model benchmark results.
