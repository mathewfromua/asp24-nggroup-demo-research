# Performance: відтворюваний початковий вимір модернізації

Вимір 09.10.2026 порівнює RC2 `0034b000bd1bad42f0c3ffb222a0ec58308a42bc` з першим Modern Experience `3c289bf7c65400ea975427f8ed59721b97d77fe3`. Це **результат конкретного SHA**, до наступних виправлень reflow та резервування місця під лінивий компонент. Фінальний `modern-experience-preview-<SHA>` містить новий exact-SHA `evidence/performance/performance.json`; його не слід підміняти цими початковими числами.

Докази: [workflow 37900710377](https://github.com/mathewfromua/asp24-nggroup-demo-research/actions/runs/37900710377), [performance artifact 11602697213](https://github.com/mathewfromua/asp24-nggroup-demo-research/actions/runs/37900710377/artifacts/11602697213). JSON містить усі 30 сирих спостережень, Resource Timing, навігацію, медіани, min/max та 12 Lighthouse-звітів. `PASS` означає завершений вимір, а не автоматично кращу швидкодію.

## Умови

Один Ubuntu 24.04 GitHub runner, Linux 6.17.0-1022-azure, Node 24.21.0, Python 3.12.14, Playwright 1.62.0, Chrome 154.0.8037.97. П'ять холодних контекстів на кожну версію і сценарій, порядок версій чергується. Розмір 1440 × 900 CSS px; reduced motion. Обидві незмінні root-збірки обслуговує одна реалізація HTTP без fallback, gzip level 9, `Cache-Control: no-store`. CPU і loopback-мережа без throttling. RC2 збирається з фіксованого `git archive`, поточна збірка завантажується з build-job без повторної генерації.

Команда CI: `python scripts/performance-sample.py --baseline-dist "$RUNNER_TEMP/rc2-baseline/dist" --modern-dist modern-build/root/dist --output performance --repeats 5 --executable /usr/bin/google-chrome`. Chrome запускається із sandbox. Порівняння містить ті самі шість UPS-моделей і ту саму пару; дія — перемикання відмінностей до двох наступних animation frames.

## Передані ресурси

Нижче медіани; байти без округлення. Gzip — фактичні encoded body bytes браузерних ресурсів, без HTTP-заголовків. Raw — decoded bytes реально завантажених JS/CSS. «Початковий JS» включає лінивий компонент, якщо прямий URL уже відкриває workbench.

| Сценарій | JS/CSS raw, RC2 → Modern | JS/CSS gzip, RC2 → Modern | Різниця gzip | Запити RC2 → Modern |
|---|---:|---:|---:|---:|
| Hub | 2 032 → 1 873 B | 1 037 → 936 B | −101 B | 4 → 4 |
| Demo/catalog | 1 281 402 → 993 475 B | 121 206 → 105 125 B | −16 081 B | 22 → 9 |
| Comparison | 1 281 402 → 1 235 729 B | 121 206 → 178 862 B | +57 656 B | 22 → 11 |

| Сценарій | Початковий JS raw, RC2 → Modern | Початковий JS gzip, RC2 → Modern | Усі передані body bytes, RC2 → Modern |
|---|---:|---:|---:|
| Hub | 302 → 157 B | 216 → 140 B | 6 898 → 6 799 B |
| Demo/catalog | 1 188 289 → 903 940 B | 99 626 → 87 643 B | 129 537 → 113 468 B |
| Comparison | 1 188 289 → 1 134 820 B | 99 626 → 158 591 B | 129 537 → 187 205 B |

Повний набір JS/CSS файлів у dist, включно з лінивими: 1 283 434 → 1 237 602 raw B; 122 243 → 179 798 gzip B. Workbench додає React лише під час відкриття його маршруту. Hub завантажує малий legacy-hash redirect, без каталогу і React. Catalogue-сторінка має менше байтів та запитів; весь demo ще містить синтетичний каталог.

## Час і стабільність компонування

| Сценарій | LCP, RC2 → Modern | Load event, RC2 → Modern | CLS, RC2 → Modern |
|---|---:|---:|---:|
| Hub | 88 → 92 ms | 45,3 → 47,7 ms | 0 → 0 |
| Demo/catalog | 276 → 248 ms | 131,3 → 109,8 ms | 0 → 0 |
| Comparison | 248 → 296 ms | 137,5 → 111,4 ms | 0 → 0,50408 |

Медіана дії порівняння: 16,9 → 9,7 ms; діапазони 13,1–18,1 і 9,0–10,3 ms. Це click-to-two-frames у лабораторії, **не INP**. Медіана long-task excess понад 50 ms: comparison 13 → 7 ms, hub/demo 0 → 0 ms; це окремий proxy, не Lighthouse TBT.

LCP-діапазони: hub RC2 84–524 / Modern 84–104 ms; demo 264–864 / 220–260 ms; comparison 244–268 / 284–352 ms. Викиди й малий loopback-час не дозволяють обіцяти таку саму різницю користувачам реальних мереж.

Перший вимір виявив суттєвий layout shift workbench: 0,50408 у всіх п'яти запусках. Малий placeholder перед завантаженням React не резервував простір повного інтерфейсу. Це конкретна підстава для виправлення компонування й повторного виміру. Додаткові gzip bytes на маршруті workbench — реальна вартість React pilot; вона не прихована за поліпшенням catalog. Загального твердження «сайт став швидшим» цей результат не обґрунтовує.

## Lighthouse

Lighthouse 13.5.0: три холодні запуски кожної версії для hub і demo, desktop preset, `throttling-method=provided`, той самий gzip HTTP. Усі 12 вимірів завершилися. Медіани:

| Сценарій | LCP, RC2 → Modern | TBT, RC2 → Modern | CLS, RC2 → Modern | Speed Index, RC2 → Modern |
|---|---:|---:|---:|---:|
| Hub | 66,0 → 63,7 ms | 0 → 0 ms | 0 → 0 | 66 → 64 ms |
| Demo/catalog | 230,7 → 187,2 ms | 0 → 0 ms | 0 → 0 | 177 → 148 ms |

Lighthouse не запускався для stateful comparison; його дані наведено у п'ятикратному браузерному вимірі вище. Це лабораторія без CPU/мережевого throttling, не польові Web Vitals, не оцінка конверсії і не доказ швидкості на фізичному iPhone. Native Safari, iPhone, zoom і VoiceOver лишаються NOT_RUN.
