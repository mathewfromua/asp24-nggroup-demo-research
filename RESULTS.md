# ASP24 / NG Group — кандидат 3.2.0-rc.1

**Preview with limitations. Main і чинний GitHub Pages не оновлено.** Інтеграційна гілка `release/reports-first-rc`; [включені heads](docs/included-heads.json). Точний commit, результати на ньому та hashes файлів записує `candidate-manifest.json` у реальному [Actions artifact](https://github.com/mathewfromua/asp24-nggroup-demo-research/actions/workflows/candidate.yml). Артефакт створюється лише після успішних перевірок усіх трьох браузерів; відсутність artifact не є PASS.

| Напрям | Результат і межа |
|---|---|
| Редакція | R01–R44 мають змістове рішення у research/editorial-decisions.json; E01/E02 збережені. R34 потребує пояснення компанії про відлік сервісних строків. |
| Джерела | 11 PDF реально отримано; actual hashes і прочитані сторінки відокремлені від повідомлених рецензентом у research/editorial-source-register.json. Це не повтор історичних UI-дій і не широке SEO-дослідження. |
| PDF/HTML | Реальні 14 + 16 сторінок; один рукопис. Усі блоки й клітини таблиць звірені з відповідними PDF-сторінками та HTML. Контрольна генерація у тимчасовому дереві побайтово тотожна; негативні зміни source/шаблону виявлені. Integrity не засвідчує правдивості джерела. |
| Візуальний перегляд | Усі 30 сторінок відрендерено й переглянуто. 22 змінені; 8 збігаються з main, включно з обкладинками. Деталі та hashes: reports/editorial-validation.json. Це огляд виконавця, незалежне приймання попереду. |
| Початкова сторінка й приклади | Статичні огляди першими, 4 версійні кейси, повернення до точного розділу. Окремий sessionStorage; особисті кошик, чернетки й проєкти не перезаписуються. Старі hash URLs перенаправляються до demo.html. |
| Логіка | Локально на інтеграції 4b6afc8: 95 PASS, 0 FAIL, 2 історичні SKIP. Наступний reset/pagehide regression також пройшов. На a9489ab CI виявив overflow hub при збільшенні тексту; виправлено переноси, повторний прогін обов’язковий. Новий кандидат повторює весь набір у CI; фактичний журнал у bundle. |
| Браузери | C на fb5f831: Chromium/Firefox/WebKit по 7 PASS (run 37880168268). Це попередній C, не доказ B чи остаточного кандидата. Candidate workflow перевіряє той самий завантажений dist усіма трьома рушіями, включно з read→case→return, чистим/заповненим станом, reload, reset, Back/Forward та screenshots. Остаточні PASS/FAIL і версії — лише в exact-commit manifest. |
| Cloud | Node/Python/HTTP працюють. Локальний запуск браузерів BLOCKED sandbox/runtime цього середовища; sandbox не вимикався. Реальні браузери запускаються у GitHub Actions Ubuntu 24.04. |
| Доступність | Ціль — застосовні WCAG 2.2 AA, не сертифікація. Перевірки 320/390/430/1440 CSS px, CSS text resize, labels і частина keyboard workflow включені. Native zoom, повне keyboard-only/VoiceOver, екранна клавіатура фізичного пристрою NOT_RUN. |
| PDF R42 | Фінальні PDF untagged; HTML є альтернативою; Issue #4. Окремий двосторінковий WeasyPrint pilot створив H/Table/Figure tags; валідатор PDF/UA, читання AT і covers NOT_RUN. Pilot не замінює фінальний PDF і не є PASS PDF/UA. |
| Apple | Stable Safari та фізичний iPhone NOT_RUN; Issue #1 містить протокол HTTPS-приймання саме кандидата. WebKit не прирівняно до Safari. |
| GitHub | Draft тематичні PR #3/#5/#6; інтеграція звичайними merge. Ruleset підготовлено, settings не застосовано. Dependabot підготовлено. CodeQL JS/Python генерує SARIF artifact без запису security settings; фактичний run оцінюється окремо. На a9489ab SARIF Python без знахідок, JS знайшов DOM→iframe URL у старому тестовому стенді; введено allowlist і URLSearchParams, потрібен повторний scan. Secret scanning / push protection не підтверджено. |
| Bundle | Source через git archive точного SHA; dist будується один раз, тести отримують його як artifact. Окрема контрольна генерація. PDF/HTML, hashes, докази й інструкція включені; font binaries, caches та приватний архів виключені. |
| Публікація | NOT_DEPLOYED. Абсолютні посилання PDF/standalone HTML/OG налаштовані на майбутній погоджений origin. До дозволеної публікації нові кейси відкривати з HTML через HTTP-preview artifact. Чинний Pages ще показує попередню версію. |

[Критерії незалежного читання](docs/REVIEW_CANDIDATE.md) · [Release notes](docs/RELEASE_NOTES.md) · [Історія опублікованого демо до кандидата](https://github.com/mathewfromua/asp24-nggroup-demo-research/blob/d7d9545b9d3052a3f056514277e40e37e9c36c8a/RESULTS.md).

Наступна дія — read-only приймання exact-commit artifact координаційним чатом і незалежним рецензентом. Зауваги, що змінюють код або звіти, створюють новий SHA й новий artifact. Ширше дослідження (#2), майбутня модернізація та перенос хостингу сюди не включені.
