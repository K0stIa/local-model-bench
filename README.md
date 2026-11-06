# Local Model Bench

Відтворювані локальні тести coding, tool calling та інтерпретації синтетичних даних Home Assistant. Ніякого підключення до реального дому, токенів або зміни Hermes/llama-swap. Публічний відтворюваний snapshot локального benchmark-репозиторію.

## Що є

- `custom`: 9 coding-задач (168 крайових cases) + 10 структурованих агентних сценаріїв. Specs походять із тестування 6 листопада 2026; неоднозначну задачу unavailable замінено явним device mapping.
- `humaneval`: 164 офіційні задачі OpenAI HumanEval (MIT), pinned commit та SHA256 у `data/humaneval/PROVENANCE.json`. `--limit 10 --seed 42` — детермінований smoke subset, **не офіційний HumanEval pass@1**. Ми запитуємо повну функцію через chat, а не raw completion. Повний набір теж є адаптованим протоколом.
- Агрегований історичний звіт у `results/legacy-20261106/REPORT.md`. Сирі запити, відповіді, tool transcripts і детальні grading JSON залишені локально та не публікуються. Історичний звіт має інші умови, ніж новий harness. Legacy source збережено як `.py.txt`, не як рекомендований executor.
- Fail-closed `bubblewrap` sandbox для згенерованого коду: окремі PID/network/user namespaces, без домашньої файлової системи, read-only root і системні бібліотеки, 16 MiB tmpfs, обмеження CPU/RAM/output/time/processes. Це defense in depth, не VM і не гарантія проти kernel exploit.

## Швидкий початок

Потрібні Linux, Python 3.12+, git і bubblewrap з дозволеними user namespaces. Ніяких Python dependencies. Перевірка без моделей:

```sh
python3 -m unittest discover -s tests -v
python3 -m bench.verify_references
python3 -m bench list --suite custom
```

Запустіть окремий локальний OpenAI-compatible llama-server з `--host 127.0.0.1 --slots`, правильною моделлю та рідним chat template. Сервіс самостійно не запускається, модель не завантажується, робочий конфіг не редагується.

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

`--dry-run` друкує вибрані задачі без мережі/генерації. `--task ID` дозволяє повторювати конкретний тест. `--repeat 3` зберігає кожну спробу, не вибирає найкращу. Output створюється через exclusive-create, існуючий запуск не перезаписується.

Орієнтир: custom 19 задач може зайняти 3–15 хвилин залежно від моделі/reasoning; HumanEval10 приблизно 2–10 хвилин. Це бюджет планування, не обіцянка. `--budget` і `--timeout` зупиняють клієнт; після timeout необхідно перевірити, що сервер припинив генерацію. Runner зупиняється на першій транспортній помилці, не перемикає модель автоматично. Idle-check зменшує ризик завадити користувачу, але не є ексклюзивним lock: використовуйте окремий benchmark server та координуйте GPU.

## Чесне порівняння

Зафіксуйте GGUF URL/revision/hash/quant, runtime version, backend, context, GPU offload, KV types, sampling, max_tokens, reasoning mode. Копіюйте лише whitelist параметрів, не entire user config. JSONL містить exact request/response, profile, IDs, seed, час, commit/dirty flag і source SHA256 harness. `--runtime-manifest sanitized.json` вбудовує окремий manifest та його SHA256; без нього runtime provenance позначено null. Зберігайте додатковий `runtime-manifest.json` поруч.

Не примушуйте always-thinking модель до unsupported non-thinking. Профілі — явні JSON-файли; для LFM потрібен більший max_tokens і native reasoning. `profiles/nonthinking.json` — лише для моделей, які підтримують enable_thinking. `reasoning-low.json` — для відповідних endpoint. Native-default не нав'язує model-specific flags.

Coding correctness окремо від Markdown/JSON formatting. Agent functional score перевіряє лише визначені поля/виклики, не всю семантику пояснення, українську чи загальну безпеку. Загальний pass rate малих subset має велику невизначеність. Public tasks можуть бути в training data. Не змішуйте різні seeds/subsets/quantization чи legacy scores в один рейтинг.

## Розширення

1. Додайте task зі spec, незалежними test cases і reference у `bench/custom_coding.py`, або messages/tools і очікування у `custom_agents.py`/`agent_grading.py`.
2. Не додавайте живі датчики/секрети. Усі fixtures синтетичні.
3. Покрийте grading unit-тестом, перевірте reference і known-wrong solution.
4. Нові suites додавайте через `load_suite` з pinned dataset/licensing/provenance. Full SWE-bench потребує великих контейнерів і тривалих agent loops, тому тут не ввімкнений.

## Перевірено

На benchmark-host: unit tests; sandbox home/network/timeout probes; усі 164 canonical HumanEval solutions; 9 custom reference solutions. Ці тести не викликають моделі. Нові кандидатні моделі запускаються окремо і мають власні JSONL результати.

## Ліцензії

HumanEval: MIT, повний upstream LICENSE поряд із dataset. Для оригінального harness/синтетичних fixtures ліцензію на повторне використання наразі не призначено. Публічна видимість не означає надання окремої open-source ліцензії. Моделі мають власні ліцензії та не входять до Git.

## Межі автоматичного grading

Порівняння ізольовані від namespace кандидата, ранній вихід не означає успіх. Sandbox захищає host, але цей Python harness не є криптографічно захищеним від навмисного зламу grading через introspection. Для свідомо ворожого коду потрібен окремий VM/додаткове зміцнення. Не називайте це гарантією безпеки агента.

Candidate download manifests in `manifests/` describe upstream expected hashes and pinned revisions, not completed downloads or measured results. Update local validation only after hashing the complete file. LFM always-thinking uses a separately recorded output budget (`profiles/lfm-native.json`); this is not an equal-compute comparison.

## Окремий профіль продуктивності

`profiles/performance.json` і `python3 -m bench.performance` вимірюють native
llama.cpp prefill/decode, warm/cache phases та sampled memory. Матриця MTP,
контекстів і збірок, правила cold/warm та обов'язкової перевірки коректності:
[docs/PERFORMANCE.md](docs/PERFORMANCE.md). Runner не змінює робочих сервісів.
