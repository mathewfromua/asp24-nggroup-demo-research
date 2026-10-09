# RC3 hardening — поточне робоче дерево перед фінальним gate

**PRE_GATE / PREVIEW_NOT_DEPLOYED.** Нові зміни ще не мають завершеного exact-SHA CI, нового artifact або остаточного рішення щодо release. Попередній `ACCEPT_PREVIEW` стосується лише контрольної бази `b320abc302ed895704db2437ce7dbe3a6964e603`: [PR #9](https://github.com/mathewfromua/asp24-nggroup-demo-research/pull/9), [CI 37929590198](https://github.com/mathewfromua/asp24-nggroup-demo-research/actions/runs/37929590198), artifact `11614914429`. Це приймання не переноситься на змінений кандидат.

Робота триває в `release/review-integrated-rc3`. Прийнятий рукопис `reports/content.json`, E01/E02, історичні межі джерел, моделі, одиниці та умовність розрахунків збережено. Main, Pages, Settings, merge і deployment не змінено. Обсяг і короткий нативний smoke-test — у [FINAL_HARDENING](docs/FINAL_HARDENING.md).

| Блок | Фактичний стан до спільного gate |
|---|---|
| P0 — структуровані PDF | ASP24 — 14 сторінок; NG Group — 16. WeasyPrint 70.0 формує логічну структуру зі спільного HTML/рукопису; початкові векторні й текстові обкладинки збережено та семантично позначено. Це не растрова заміна обкладинок. |
| Незалежна PDF-перевірка | Переглянуто всі 30 сторінок; звірено текст, числа, одиниці, назви, посилання, порядок читання, таблиці й альтернативи Figure. Структурна перевірка та veraPDF 1.30.3 з явним профілем PDF/UA-1 — машинний PASS для обох поточних PDF. |
| R42 | Закрито щодо структурного тегування після перевірки обох PDF. Допоміжне читання/VoiceOver — NOT_RUN; машинний PASS не є повною користувацькою перевіркою доступності чи безумовною заявою PDF/UA. |
| P1 — browser fallbacks | JSON/TXT мають точну текстову копію на сторінці навіть за мовчазного блокування download; Clipboard має ручну альтернативу. Відмова storage не маскується успішним збереженням, жива чернетка доступна для експорту. При React load failure доступні класичне порівняння, каталог, документи й огляди. Адресні Chromium-перевірки виконано з увімкненим sandbox. |
| P2 — порівняння | Збережено контекст довгих таблиць, додано desktop-подання активної пари без втрати інших кандидатів, покращено допоміжні підписи. Адресно перевірено перший технічний рядок, reflow, keyboard focus і збільшення тексту; результати ще мають пройти спільний exact-SHA gate. |
| P3 — початкове завантаження | Наявні project/lab UI та CSS завантажуються за потреби; доменні правила залишаються спільними. Modern chunk починає завантажуватися раніше лише для відповідного маршруту. Порівняння з b320 виконується за однакових умов; польове прискорення не заявляється. |
| Контракти | `perspective-demo-v1`, schema 4, project import version 1, stable ID, шість кандидатів/пара та ізоляція кейсів збережені. Експорт локальної копії не означає її автоматичний імпорт або підтверджений download. |
| Нативні середовища | Safari macOS/iOS, фізичний iPhone, Chrome Android, Telegram iOS/Android, потрібні WKWebView/Android WebView, екранна клавіатура й VoiceOver — NOT_RUN. Linux Chromium або Playwright WebKit не підтверджують ці середовища. |
| R34 | OPEN_EXTERNAL_SOURCE. Початок відліку сервісних строків і включення початкової діагностики не встановлені; одне питання підготовлено, не надіслано. |

Наступний повний gate: typecheck/Node, структурна PDF-перевірка та veraPDF UA-1, відтворення звітів і негативні stale-output перевірки, root/Pages build, дев’ять browser suites у Chromium/Firefox/WebKit над тим самим dist, порівнювані performance-виміри й exact-SHA packaging. Кількість PASS визначається фактичними результатами нового запуску; історичні `122` і `46 × 3` не є результатами цього дерева. Для побайтового PDF-контролю потрібні також однакові native-бібліотеки рендерингу, а не лише Python requirements і шрифти.

До завершення цього gate новий SHA, CI run і artifact — **ще не підтверджені**. Після нього потрібне адресне незалежне приймання змінених PDF і функцій. Merge та публікація не виконуються.

---

## Історична контрольна точка b320 — ACCEPT_PREVIEW

Для `b320abc302ed895704db2437ce7dbe3a6964e603` незалежно підтверджено exact artifact `11614914429`, CI `37929590198`, 122 Node PASS та по 46 PASS у Chromium/Firefox/WebKit. Рішення — `ACCEPT_PREVIEW` з тодішніми обмеженнями, зокрема untagged PDF/R42 і нативними NOT_RUN. Нижче збережено передприймальний запис реалізації RC3; його майбутні формулювання та обмеження описують той історичний етап.

### RC3 — інтегрований кандидат 3.2.0-rc.3: історичний запис

**Локальні перевірки PASS; exact-SHA browser/CI результат і статус готовності — у workflow RC3 та draft PR. PREVIEW_NOT_DEPLOYED. Незалежне приймання ще не виконано.**

Гілка `release/review-integrated-rc3` походить від перевіреного PR #8 / `a659d2f9e8d923a7bc64a3f91133cfed959e9181`; база draft PR — `feat/modern-experience`. Main `d7d9545…`, RC2 PR #7 та Modern PR #8 не змінено. [Рішення рецензій](docs/RC3_REVIEW_DECISIONS.md) · [Читання й післяпублікаційний контроль](docs/RC3_REVIEW.md) · [Preflight](docs/rc3-preflight.json).

Виправлено DC/USB, уточнено FHP12A як розбіжність публікацій, розділено історичну опору й нове отримання PDF. Реально отримано вісім PDF і два вебподання; actual SHA/date/page/read scope записано в source register, історію не переписано. Для недоступних давніх DOM збережена явна атрибуція технічному рецензентові. Покращено контраст, джерела, HTML headings/tables/charts/citations і український hub. Modern case має компактний контекст, повернення з картки/документа зберігає modern, undo заміни відновлює слот і пару без зміни іншого стану.

| Перевірка цього робочого дерева, 09.10.2026 | Фактичний результат |
|---|---|
| Toolchain | PASS: npm ci; Node24.19.0/npm11.9.0, Python3.12.14, pinned ReportLab4.4.9/pypdf6.10.0/Pillow12.3.0, exact font hashes. |
| TypeScript / Node | PASS: strict typecheck; 122 PASS / 0 FAIL / 2 історичні SKIP. Нових SKIP немає. |
| Build / verify / HTTP | PASS: root і Pages subpath; Node HTTP/case routes; локальний HTTP byte check усіх 40 активів, PDF signatures і MIME. |
| PDF / HTML | PASS: 14+16 сторінок з одного рукопису; усі text blocks/table cells, source anchors, input digest, побайтова контрольна регенерація; stale manuscript і template відхилено. |
| PDF visual | PASS: усі 30 baseline/current pages rendered; 21 змінену сторінку переглянуто у повному рендері, 9 незмінних, включно з обкладинками. ASP p2 геометрія збережена, NG p2 незмінна. Hash-bound evidence: reports/rc3-visual-review.json. |
| Локальні Chromium / Firefox / WebKit | BLOCKED: Chromium launch/crashpad/sandbox; Firefox uid_map read-only і timeout; WebKit host libraries missing. Захисти не змінювалися. Історичний CI PASS не перенесено. |
| Exact-SHA Actions | Результат записує rc3-manifest.json успішного artifact; workflow перевіряє всі шість suites на кожному engine, actual served bytes, geometry/screenshots 1440×900/390×844, reports 320/390/1440 та поточні hashes visual review. |
| Публікація | PREVIEW_NOT_DEPLOYED. Merge/main/Pages/settings не змінено; live абсолютні PDF URLs ще можуть давати 404/старі bytes. |

`rc3-preview.yml` використовує exact push SHA, готовий dist і окремі browser jobs; packaging дозволяє `READY_FOR_INDEPENDENT_REVIEW` тільки після PASS усіх gates. Поточні SHA, run і artifact наведені у draft PR, щоб результати перевірки не вимагали зміни самих перевірених байтів. Scoped performance вимірює кандидата, без baseline чи заяви про прискорення/конверсію.

R34 і R42 OPEN. Фінальні PDF untagged, HTML — семантична альтернатива. Native Safari, фізичний iPhone, native zoom, VoiceOver, PDF/UA — NOT_RUN. Немає реальних цін, замовлень, CRM або інтеграції робочих сайтів.

Наступна дія власника після успішного artifact: незалежно переглянути exact-SHA RC3 і залишити рішення про приймання у draft PR.

---

## Історичні контрольні точки — не результати RC3

# Modern Experience — окрема перевірка

Гілка `feat/modern-experience` походить від завершеного технічного RC2 `0034b000bd1bad42f0c3ffb222a0ec58308a42bc`. [PR №7](https://github.com/mathewfromua/asp24-nggroup-demo-research/pull/7) та [artifact 11601089917](https://github.com/mathewfromua/asp24-nggroup-demo-research/actions/runs/37897909570/artifacts/11601089917) залишаються окремим результатом A: Chromium/Firefox/WebKit по 23 PASS, 111 Node PASS, перевірені PDF/HTML; незалежне приймання очікується.

Реалізовано Vite 8.3.4, strict TypeScript 7.0.2, React 19.3.0 Comparison Workbench, спільну типізовану доменну логіку й адаптери. Legacy UI та імпорт збережено. Реалізовано також узгоджені hover/focus/pressed/selected/disabled стани, touch-цілі 44 px, видимі текстові підтвердження та правдивий відгук збереження. Новий простір доступний на `demo.html#/asp/compare?experience=modern` і для бренду `ng`. Огляди й чотири початкові кейси не змінено.

Локально перед commit: typecheck/build/verify PASS, Node 116 PASS / 0 FAIL / 2 історичні SKIP. Незалежний адресний Node-probe зіставив із RC2 270 комбінацій пошуку/сортування та дії порівняння у восьми категоріях — PASS. Локальний захищений browser runtime недоступний; результат браузерів і швидкодії тут не вигаданий.

Exact-SHA workflow `modern-preview.yml` перевіряє обидва base paths, три попередні suites та React-пілот у Chromium/Firefox/WebKit, повторні вимірювання RC2/new і Lighthouse. Manifest у HTTP-preview artifact містить фактичний SHA, результати й hashes; пакування вимагає PASS усіх suites саме на цьому SHA. Статус готовності, результати вимірювань і найближча дія фіксуються у фінальному checkpoint [draft PR №8](https://github.com/mathewfromua/asp24-nggroup-demo-research/pull/8).

Main, Pages, settings не змінено. R34/R42 і native Safari/iPhone/zoom/VoiceOver залишаються відкритими. Зміст прийнятих оглядів не адаптувався під новий дизайн.

---

# ASP24 / NG Group — кандидат 3.2.0-rc.2

**Preview with limitations; незалежне приймання очікується. Main і чинний GitHub Pages не оновлено.** Гілка `release/reports-first-rc`, контрольний RC1 — `435e99440e4070371476a672d1e7a582638d8d12`. Точний новий SHA, усі результати та hashes outputs записує `candidate-manifest.json` у [Actions artifact](https://github.com/mathewfromua/asp24-nggroup-demo-research/actions/workflows/candidate.yml); поточний checkpoint і посилання на artifact — у PR #7.

## Що виправлено після незалежного читання RC1

- Відмова sessionStorage більше не означає успішне збереження. Статуси читання, запису, очищення й роботи лише в пам’яті відокремлено; українське доступне повідомлення пояснює ризик reload. Поточний стан прикладу можна явно експортувати в JSON із його версією та schema 4. Невдале очищення не перезавантажує сторінку. Особистий `perspective-demo-v1` не використовується адаптером кейсу.
- NG Group, `nggroup-11`: строк до 14 календарних днів віднесено до діагностики й ремонту гарантійного обладнання. Пояснення початку відліку й співвідношення строків R34 залишається відкритим.
- NG Group, `nggroup-07`: суттєві параметри показаного XPON-фрагмента передано текстом; це запис документа, а не нова перевірка апаратної сумісності.

## Як перевіряється кандидат

Node-тести, build і verify з кореневим та Pages base path; генерація обох PDF/HTML зі спільного рукопису; source/output integrity; контрольна побайтова генерація та негативні stale-output перевірки. Огляди зберігають 14 + 16 сторінок, прийняті обкладинки й E01/E02. Адресні зміни та порівняння рендерів записано в `reports/editorial-validation.json`.

Candidate workflow будує dist один раз. Chromium, Firefox і WebKit завантажують саме цей dist та виконують попередні regression/cases suites і новий case-storage suite. Він перевіряє успішний запис, quota, недоступний sessionStorage, getItem/removeItem exceptions, подальше редагування, точний JSON-експорт, reload, повторний вхід, Back/Forward та незмінність особистого стану. Packaging вимагає PASS кожного suite на тому самому SHA; історичний RC1 PASS не зараховується.

Локально 09.10.2026 перед фіксацією RC2, Node 24.19.0 / Python 3.12.14: `npm test` — 111 PASS, 0 FAIL, 2 збережені історичні SKIP; build/verify — PASS; контрольна генерація та два негативні stale-output тести — PASS. Нових SKIP немає.

Фактичні результати цього SHA — лише в manifest і CI-журналах. Локальні перевірки до commit є попередньою валідацією, а не незалежним прийманням. Нездатність захищеного браузера запуститися в Cloud позначається BLOCKED; sandbox не вимикається.

## Межі preview

- R34: потрібне пояснення власника сервісного процесу.
- R42: обидва фінальні PDF untagged. HTML — альтернатива; окремий tagged pilot не закриває залишок і не доводить PDF/UA.
- Stable Safari/macOS, фізичний iPhone, native zoom, VoiceOver та повне читання PDF допоміжною технологією — NOT_RUN без окремих фактичних результатів. CSS text resize і WebKit не підміняють ці перевірки.
- Каталог синтетичний, реальних замовлень/звернень чи інтеграцій немає. Широке дослідження #2 не включене; integrity не доводить правдивості джерел.
- NOT_DEPLOYED. Нові абсолютні PDF/standalone HTML URLs налаштовані на майбутню публікацію; до неї користуйтеся HTML з HTTP-preview artifact. Main, Pages і settings не змінено.

[Критерії незалежного читання](docs/REVIEW_CANDIDATE.md) · [Release notes](docs/RELEASE_NOTES.md) · [Відтворення](docs/DEVELOPMENT.md).

Наступна дія для RC2 — незалежне приймання exact-SHA artifact. Модернізація після технічного PASS розробляється окремо й автоматично в цю гілку не інтегрується.
