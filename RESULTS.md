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
