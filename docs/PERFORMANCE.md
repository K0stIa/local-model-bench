# Відокремлені тести продуктивності

Runner не запускає сервер, не встановлює пакети й не змінює робочі конфігурації,
BIOS, GPU/RAM allocation, swap або системні caches. Потрібен окремий localhost
llama-server з `--slots`, одним slot (`-np 1`) та портом, не зайнятим сервісами.
Не запускайте паралельно з іншою генерацією. Idle-check не є ексклюзивним lock.

## Матриця

Для кожної моделі з незмінним GGUF SHA256: MTP off/on × контекст 8192/32768.
Порівнюйте MTP лише якщо конкретні модель, GGUF та build його підтримують.
Відсутність підтримки позначайте `unsupported`, а не імітуйте звичайним draft model.
Збережіть точні argv, `--version`, commit/build flags/backend, quantization,
число GPU layers, batch/ubatch, flash-attention та KV-cache типи у manifest.
Не копіюйте environment, приватні конфіги або токени. Для експериментального
build змінюйте тільки binary, тримайте його в окремій папці. Не перемикайте
production symlink чи service. Інші параметри повинні лишатися однаковими.

Для 512/4096 prompt tokens використайте один синтетичний UTF-8 prompt-файл
на кожну довжину, перевіривши довжину tokenizer конкретної моделі. Різні моделі
можуть токенізувати текст по-різному: звітуйте виміряний `prompt_n`, не лише ціль.
Default profile має 96 рядків, НЕ гарантує конкретної кількості токенів.

## Запуск

```sh
python3 -m bench.performance --endpoint http://127.0.0.1:18081 \
  --profile profiles/performance.json --runtime-manifest manifests/run.json \
  --server-pid 12345 --prompt-file /path/synthetic-prompt.txt \
  --output results/performance-variant.jsonl
```

`--dry-run` перевіряє inputs без мережі. Output створюється exclusive, не overwrite.
Manifest обов'язковий, довільний JSON, його зміст і hash зберігаються з results.
Рекомендовані поля: model_sha256, binary_sha256, build_commit, argv, mtp,
context_size, prompt_target_tokens, backend, hardware, experiment_label.

Default: seed42, greedy, 128 decode tokens (`ignore_eos`), 1 first request,
3 повтори без prefix cache, 3 з prefix cache. Поле `phase` розділяє ці групи.
Warm_no_cache перевимірює prefill; prefix_cache вимірює інший сценарій й НЕ
входить до його середнього. `first_request` є лише першим запитом цього runner:
це не гарантія холодної моделі чи filesystem cache. Для model-cold окремо
перезапустіть лише тестовий сервер і запишіть час startup→ready зовнішнім таймером.
Не чистіть системний page cache. Порядок off/on чергуйте між повторами; за потреби
зробіть повторний повний прогін, щоб відрізнити ефект температури й навантаження.

## Метрики та межі

JSONL: metadata, measurement або error. Timings native llama.cpp дають окремо
prefill/decode count, ms, tokens/s; wall_seconds включає HTTP overhead.
Для cached запитів prompt_n може означати тільки реально обчислені токени.
Server timings не є streaming TTFT. Memory samples кожні 250 ms: RSS/HWM/swap
процесу, system MemAvailable/SwapFree, load average. RSS не дорівнює VRAM,
HWM накопичений за життя процесу; короткі піки можуть бути пропущені. Shared
UMA RAM не можна просто додати до RSS. GPU metrics, якщо доступні, записуйте
окремим sampler, не робіть припущення за RAM. PID передає оператор.

При timeout/error runner зупиняється; перевірте, чи сервер завершив запит,
перед наступним тестом. Truncation і неповний decode budget вважаються invalid.
Звіт: медіана та min/max warm повторів, cached окремо, всі raw samples збережені.
Три повтори дають тільки попередній сигнал, а не статистично сильний висновок.

## Коректність обов'язкова

Synthetic performance не оцінює зміст відповідей. На кожному варіанті виконайте
окремо `python3 -m bench run` із однаковим profile/seed/custom задачами, потім
`python3 -m bench report`. Coding запускається лише в наявному sandbox.
Для MTP порівняйте deterministic output hashes на performance-запитах і
pass/fail correctness-suite. Однаковий hash не є повним доказом коректності;
різний hash потребує перевірки, не означає автоматично помилку (backend numerical
variation). Не називайте виграш прийнятним без перевірки якості та стабільності.
