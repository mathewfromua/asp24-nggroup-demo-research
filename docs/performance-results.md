# Performance після виправлень Modern Experience

Вимір 09.10.2026: RC2 `0034b000bd1bad42f0c3ffb222a0ec58308a42bc` → Modern `1e1877624e0024666e4b8c5bce1b4672c1a7a66c`. Це результат точного SHA зі змінами інтерфейсу, а не висновок із факту встановлення Vite або React. [Workflow 37920434893](https://github.com/mathewfromua/asp24-nggroup-demo-research/actions/runs/37920434893) · [performance artifact 11611977052](https://github.com/mathewfromua/asp24-nggroup-demo-research/actions/runs/37920434893/artifacts/11611977052). JSON містить усі сирі спостереження, ресурси, середовище й Lighthouse-звіти.

Фінальний `modern-experience-preview-<SHA>` містить власний `evidence/performance/performance.json`. Якщо HEAD новіший, цей документ не підмінює його вимір; порівнюйте за SHA у manifest. `PASS` означає виконаний вимір і пройдені бюджети стабільності компонування, а не автоматичне прискорення.

## Умови

Один Ubuntu 24.04 GitHub runner, `Linux-6.17.0-1022-azure-x86_64-with-glibc2.39`, Node `v24.21.0`, Python `3.12.14`, Playwright `1.62.0`, Chrome `154.0.8037.97`. П’ять холодних запусків кожної версії та кожного з трьох сценаріїв; порядок чергується — 30 спостережень. 1440 × 900 CSS px, reduced motion, loopback без CPU/мережевого throttling, однаковий HTTP/gzip level 9 і `Cache-Control: no-store`. RC2 збирається з фіксованого git archive; новий dist з build-job використовується без повторної збірки.

Команда: `python scripts/performance-sample.py --baseline-dist "$RUNNER_TEMP/rc2-baseline/dist" --modern-dist modern-build/root/dist --output performance --repeats 5 --executable /usr/bin/google-chrome`. Sandbox увімкнений. Порівняння має ті самі шість UPS-моделей і активну пару.

## Передані ресурси

Медіани; bytes без HTTP-заголовків. Raw — decoded body реально завантажених JS/CSS, gzip — encoded body, «початковий JS» охоплює й лінивий компонент при прямому вході на workbench.

| Сценарій | JS/CSS raw, B | JS/CSS gzip, B | Запити |
|---|---|---|---|
| Hub | 2 032 → 1 873 | 1 037 → 936 | 4 → 4 |
| Demo / каталог | 1 281 402 → 996 795 | 121 206 → 105 880 | 22 → 9 |
| Comparison | 1 281 402 → 1 243 788 | 121 206 → 180 765 | 22 → 11 |

| Сценарій | Початковий JS raw, B | Початковий JS gzip, B | Усі передані body bytes |
|---|---|---|---|
| Hub | 302 → 157 | 216 → 140 | 6 898 → 6 799 |
| Demo / каталог | 1 188 289 → 904 177 | 99 626 → 87 871 | 129 537 → 114 220 |
| Comparison | 1 188 289 → 1 135 986 | 99 626 → 159 148 | 129 537 → 189 105 |

Повний набір JS/CSS у dist, включно з лінивими: 1 283 434 → 1 245 661 raw B; 122 243 → 181 701 gzip B. Hub не завантажує каталог або React. React/CSS workbench завантажуються лише при відкритті його маршруту.

## Час і компонування

| Сценарій | LCP, ms | Load event, ms | CLS | Long-task proxy, ms |
|---|---|---|---|---|
| Hub | 84 → 88 | 43,9 → 52 | 0 → 0 | 0 → 0 |
| Demo / каталог | 272 → 236 | 131,9 → 103,2 | 0 → 0 | 0 → 0 |
| Comparison | 248 → 280 | 134 → 103 | 0 → 0 | 6 → 4 |

Дія порівняння — click до двох animation frames: 16,1 → 10 ms. Діапазони: baseline 13,4–16,9 ms; modern 8,7–10,5 ms. Це лабораторний proxy, не INP. Long-task excess понад 50 ms теж не Lighthouse TBT.

LCP min–max: Hub 76–372/80–92 ms; Demo / каталог 268–472/232–268 ms; Comparison 236–252/268–300 ms.

Каталог передає на 15 326 gzip B менше; cold workbench передає на 59 559 B більше. Ціна React-пілота збережена у вимірі. Початковий Modern `3c289bf7c65400ea975427f8ed59721b97d77fe3` мав CLS 0,50408; резервування простору усунуло цей зафіксований дефект. Числа поточного SHA наведено вище. Загального твердження «сайт став швидшим» або обіцянки такого ж результату на реальній мережі немає.

## Lighthouse

Lighthouse 13.5.0: три холодні запуски кожної версії для hub/demo, desktop preset, `throttling-method=provided`, той самий runner і gzip HTTP. Усі 12 запусків — PASS. Медіани:

| Сценарій | LCP, ms | TBT, ms | CLS | Speed Index, ms |
|---|---|---|---|---|
| Hub | 64,0 → 62,3 | 0 → 0 | 0 → 0 | 64 → 63 |
| Demo / каталог | 218,7 → 183,8 | 0 → 0 | 0 → 0 | 168 → 143 |

Stateful comparison не вимірювався Lighthouse; для нього наведено п’ять браузерних повторів. Польовий INP, швидкість мобільної мережі, native Safari, фізичний iPhone, native zoom та VoiceOver — NOT_RUN. CSS text stress і WebKit не підмінюють ці перевірки.
