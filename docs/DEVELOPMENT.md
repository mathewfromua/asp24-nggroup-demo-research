# Розробка й відтворення

## Демо

Node.js 22 або новіший; runtime npm-залежностей немає. Активний builder — `scripts/build-static.mjs`; звичайна збірка використовує готові огляди з `public/reports/`.

```sh
npm test
npm run build
npm run verify
npm run preview -- --host 127.0.0.1 --port 8000
```

Не відкривайте застосунок через `file://`: для ESM, запитів і справжнього reload потрібний HTTP. Конфігурація для підкаталогу GitHub Pages, workflow та ідентичність збірки перевіряються окремо від локального кореневого preview. Поточні команди й результати цього проходу фіксує `RESULTS.md`.

Для нового origin localStorage починається окремо. Перед міграцією збережіть експорт проєктів і перевірте імпорт; зміна бренду не повинна змінювати ключі, версію схеми або stable ID. Неправильний JSON чи відмова сховища мають давати зрозумілий результат.

## Огляди

Зміст двох оглядів зберігається в `reports/content.json`. `content.py` завантажує його для генераторів. Готові PDF/HTML у `public/reports/` включаються в звичайний static build без повторної генерації та без доступу до шрифтів.

Для редакційної генерації потрібні Python 3.12, залежності з `reports/requirements.txt` та власні доступні файли Noto Sans Regular/Bold і DejaVu Sans. Їхні версії, походження й контрольні суми записані в `reports/fonts/provenance.json`. Файли шрифтів не входять до репозиторію. Обкладинки беруться з односторінкових `reports/covers/ASP24.pdf` і `reports/covers/NGGroup.pdf`; їхня типографіка зберігається. `reports/covers/provenance.json` містить походження цих сторінок, а `reports/image-provenance.json` — походження й межі кадрування використаних ілюстрацій.

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r reports/requirements.txt
export PERSPEKTYVA_FONT_DIR=/absolute/path/to/your/fonts
python3 reports/build_editorial.py
python3 reports/build_html.py
python3 reports/export_standalone.py
npm run build
npm run verify
```

Назва змінної середовища збережена для сумісності генератора; це не поточна назва проєкту. Інші версії шрифтів можуть змінити переноси й байти PDF. Не можна підтверджувати тотожність файлів лише однаковою сторінковістю.

Після редагування слід перевірити відповідність обох форматів джерелу, посилання, обсяг, рендери зачеплених сторінок та актуальні manifests. Табличні альтернативи графіків у HTML можуть містити пояснювальні рядки, яких немає серед декоративних підписів PDF; буквальний пошук кожного рядка не замінює змістовної звірки.

PDF: `Lang=uk-UA`; надійне структурне тегування не підтверджене. HTML містить семантичні заголовки, таблиці, підписи й альтернативи зображень. PDF/UA та повної WCAG-сертифікації немає.

## Контрольне складання кандидата

Python 3.12.14 і точні версії requirements потрібні для побайтового контролю. Шрифти можна відтворити з офіційних архівів LibreOffice; URLs, hashes архівів та ліцензії зафіксовано в `reports/fonts/downloads.json`, hashes кожного шрифту — у `provenance.json`.

```sh
python scripts/fetch-report-fonts.py /tmp/report-fonts
export REPORT_FONT_DIR=/tmp/report-fonts
python reports/build_editorial.py
python reports/build_html.py
python reports/export_standalone.py
python reports/build_inputs.py --write
python scripts/verify-reports.py
python scripts/check-report-reproduction.py
```

`reports/input-manifest.json` охоплює джерело, шаблони, код генерації, CSV, ілюстрації, covers, deployment-конфігурацію, профіль шрифтів і pinned залежності. Нормалізовано лише час/ID ReportLab через invariant=1; manifests мають відносні шляхи. Різні байти за іншого renderer не називаються однаковими. Control generation створює outputs у тимчасовому дереві, зіставляє байти й перевіряє, що зміна тексту або шаблону без outputs відхиляється. Report integrity перевіряє структуру та узгодженість, а не правдивість джерел.

## Браузерні регресії

`python -m pip install --require-hashes --only-binary=:all: -r scripts/requirements-browser.txt` встановлює Playwright 1.62.0 поза публічним dist; потім `python -m playwright install --with-deps chromium firefox webkit`. Playwright має ліцензію Apache-2.0; pyee — MIT, greenlet — MIT/PSF, typing_extensions — PSF-2.0. Вартість підтримки — оновлення pins/hashes та трьох browser jobs. Простіша перевірка HTTP зберігається, але не доводить кліків, фокуса й reload. Npm-залежностей застосунку не додано.

Після build/preview: `python scripts/browser-regression.py --url http://127.0.0.1:8000/asp24-nggroup-demo-research/ --browser firefox --output /tmp/browser-results`. Для оболонки з окремим демо додайте `--demo-path demo.html`. Chromium запускається з увімкненим sandbox; `--executable` може вказати встановлений системний Chrome. Нездатність запустити захищений браузер дає BLOCKED, а не PASS. CI перевіряє кожний PR без path filters; job має лише contents:read, traces/screenshots зберігаються за помилок. Усі дані сценаріїв синтетичні.

Сценарії: точний пошук; OR-фасети й сортування до пагінації; 6 кандидатів, обидва місця мобільної пари, replace/remove/undo/reload; допоміжне оновлення DOM зі збереженням чернетки; save/reload; старий JSON; межа 64; відмова запису в storage; NG-подання; HTTP/DOM обох HTML і HTTP-сигнатура обох PDF. CSS text-size stress не замінює справжній browser zoom. Safari/macOS, фізичний iPhone, VoiceOver, native zoom та PDF viewer accessibility залишаються окремими перевірками. Контроль read→case→return додається разом із маршрутами кейсів.
