# Local model benchmark plan

Goal: preserve and extend the user's synthetic coding/agent benchmark, with repeatable local inference and selected public coding tasks.

Architecture: Python standard library runner, OpenAI-compatible local endpoints, JSONL traces, independent grading, OS-isolated candidate execution. No live Home Assistant, secret files, or model downloads in this repository.

1. Write harness unit tests first: strict output extraction, timeout, mutation/error handling, OS isolation; verify failures.
2. Implement runner and bubblewrap grader, fail closed if namespaces unavailable.
3. Preserve legacy benchmark sources/results as historical evidence, not comparable new scores.
4. Add pinned HumanEval dataset fetch and deterministic smoke subset with license provenance.
5. Verify reference solutions, malicious-code probes, runner with fake local API and offline unit tests; commit locally without remote.

Constraints: no modification of Hermes or llama-swap. No home paths mounted inside candidate sandbox. Inference profile/model parameters recorded per run. Public smoke subset is not full benchmark pass@1.
