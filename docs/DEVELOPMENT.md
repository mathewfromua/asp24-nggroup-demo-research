# Розробка й відтворення

## Демо

Node.js 24; точні Vite 8.3.4, TypeScript 7.0.2, React/ReactDOM 19.3.0 зафіксовані в lockfile. `scripts/build-static.mjs` викликає Vite для графа модулів і додає статичний hub/кейси через чинний publication builder. Звичайна збірка використовує готові огляди з `public/reports/`.

```sh
npm ci
npm run typecheck
npm test
npm run build
npm run verify
npm run preview -- --host 127.0.0.1 --port 8000
```

Не відкривайте застосунок через `file://`: для ESM, запитів і справжнього reload потрібний HTTP. Конфігурація для підкаталогу GitHub Pages, workflow та ідентичність збірки перевіряються окремо від локального кореневого preview. Поточні команди й результати цього проходу фіксує `RESULTS.md`.

Для нового origin localStorage починається окремо. Перед міграцією збережіть експорт проєктів і перевірте імпорт; зміна бренду не повинна змінювати ключі, версію схеми або stable ID. Неправильний JSON чи відмова сховища мають давати зрозумілий результат.

## Огляди

Зміст двох оглядів зберігається в `reports/content.json`. `content.py` завантажує його для генераторів. Готові PDF/HTML у `public/reports/` включаються в звичайний static build без повторної генерації та без доступу до шрифтів.

Для редакційної генерації потрібні Python 3.12.14, залежності з `reports/requirements.txt` та доступні файли Noto Sans Regular/Bold і DejaVu Sans. Їхні версії, походження й контрольні суми записані в `reports/fonts/provenance.json`. Файли шрифтів не входять до репозиторію. `reports/build_editorial.py` тепер викликає семантичний HTML-експорт і `reports/build_tagged.py`: WeasyPrint 70.0 формує структурований PDF, pypdf переносить початкові векторні/текстові обкладинки з `reports/covers/ASP24.pdf` і `NGGroup.pdf` та їхню логічну структуру. ReportLab збережено для векторних графіків. Обкладинки не раструються; їхнє походження — у `reports/covers/provenance.json`, ілюстрацій — у `reports/image-provenance.json`.

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

Назва `PERSPEKTYVA_FONT_DIR` збережена для сумісності; рекомендований еквівалент — `REPORT_FONT_DIR`. Інші версії шрифтів можуть змінити переноси й байти PDF. Не можна підтверджувати тотожність файлів лише однаковою сторінковістю.

WeasyPrint потребує native Pango, HarfBuzz із subset-підтримкою, Fontconfig/FreeType та їхніх транзитивних бібліотек. Python requirements не фіксують ці системні компоненти. Для побайтового відтворення потрібен той самий pinned native-профіль або образ із зафіксованим digest; записуйте `python -m weasyprint --info`, версії системних пакетів і hashes шрифтів. Зміна Linux-дистрибутива або системних бібліотек потребує окремої звірки байтів, тексту, структури й рендерів. До проходження такої звірки cross-environment reproducibility — не PASS. Остаточний CI не повинен послаблювати byte comparison для обходу розбіжностей.

Після редагування слід перевірити відповідність обох форматів джерелу, посилання, обсяг, рендери зачеплених сторінок та актуальні manifests. Табличні альтернативи графіків у HTML можуть містити пояснювальні рядки, яких немає серед декоративних підписів PDF; буквальний пошук кожного рядка не замінює змістовної звірки.

Поточний PDF має `Lang=uk-UA`, StructTreeRoot/MarkInfo, семантичні заголовки й абзаци, списки, Table/TR/TH/TD з асоціаціями заголовків, Figure/Alt, закладки та активні посилання. Обидві обкладинки мають виділюваний текст і логічну структуру. Поточна пагінація — 14/16; зміст і читабельність мають пріоритет над фіксованою кількістю сторінок. HTML залишається самостійною семантичною альтернативою. Допоміжне читання й повна WCAG/PDF/UA-сертифікація не випливають із наявності тегів.

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
python scripts/test-structured-pdfs.py
python scripts/fetch-verapdf.py --output /tmp/verapdf
python scripts/verify-structured-pdfs.py --pdf-dir public/reports --output output/verification/reports/structured-pdf-validation.json --verapdf /tmp/verapdf/verapdf
python scripts/verify-acceptance-pdfs.py
python scripts/check-report-reproduction.py
```

`reports/input-manifest.json` охоплює джерело, шаблони, код генерації включно з `build_tagged.py`, CSV, ілюстрації, covers, deployment-конфігурацію, профіль шрифтів і pinned залежності. PDF-порівняння не нормалізує відмінні outputs; ReportLab `invariant=1` стосується його векторних графіків, а не гарантії тотожності WeasyPrint між різними native-профілями. Control generation створює outputs у тимчасовому дереві, зіставляє байти й перевіряє, що зміна тексту або шаблону без outputs відхиляється. Report integrity перевіряє структуру та узгодженість, а не правдивість джерел.

`verify-structured-pdfs.py` незалежний від генератора: перевіряє повноту рукопису, MCID/ParentTree, логічний порядок, текстові обкладинки, заголовки таблиць, альтернативи зображень і links. `test-structured-pdfs.py` перевіряє, що валідатор відхиляє контрольовані дефекти. `fetch-verapdf.py` отримує офіційний veraPDF 1.30.3 із перевіркою SHA-256 в окремий каталог; потрібна Java, бінарники не комітяться. Використовується явний `--flavour ua1`, не типовий PDF/A-профіль. Машинний PASS UA-1 обліковується окремо від незалежного перегляду всіх сторінок і перевірки допоміжними технологіями. Для поточних 14/16 PDF є машинний PASS та незалежний огляд усіх 30 сторінок; VoiceOver/допоміжне читання — NOT_RUN. Після регенерації попередній результат не переноситься на нові bytes автоматично.

## Браузерні регресії

`python -m pip install --require-hashes --only-binary=:all: -r scripts/requirements-browser.txt` встановлює Playwright 1.62.0 поза публічним dist; потім `python -m playwright install --with-deps chromium firefox webkit`. Playwright має ліцензію Apache-2.0; pyee — MIT, greenlet — MIT/PSF, typing_extensions — PSF-2.0. Вартість підтримки — оновлення pins/hashes та трьох browser jobs. Простіша перевірка HTTP зберігається, але не доводить кліків, фокуса й reload. У Modern Experience React завантажується окремим chunk лише для нового простору порівняння; Playwright залишається Python-інструментом CI, поза dist.

Після build/preview: `python scripts/browser-regression.py --url http://127.0.0.1:8000/asp24-nggroup-demo-research/ --browser firefox --output /tmp/browser-results`. Для оболонки з окремим демо додайте `--demo-path demo.html`. Chromium запускається з увімкненим sandbox; `--executable` може вказати встановлений системний Chrome. Нездатність запустити захищений браузер дає BLOCKED, а не PASS. CI перевіряє кожний PR без path filters; job має лише contents:read, traces/screenshots зберігаються за помилок. Усі дані сценаріїв синтетичні.

Сценарії: точний пошук; OR-фасети й сортування до пагінації; 6 кандидатів, обидва місця мобільної пари, replace/remove/undo/reload; допоміжне оновлення DOM зі збереженням чернетки; save/reload; старий JSON; межа 64; відмова запису в storage; NG-подання; HTTP/DOM обох HTML і HTTP-сигнатура обох PDF. CSS text-size stress не замінює справжній browser zoom. Safari/macOS, фізичний iPhone, VoiceOver, native zoom та PDF viewer accessibility залишаються окремими перевірками. `scripts/browser-cases.py` перевіряє read→case→return, чистий/заповнений особистий стан, sessionStorage, Back/Forward/reload/reopen, storage event і недійсний ID/версію. Workflow запускає його, коли dist містить publication.json; C без B не підмінює відсутні маршрути успішним тестом.

## RC2: відмови сховища прикладів

`bash scripts/run-browser-checks.sh chromium /tmp/rc2-chromium` запускає всі три suites проти вже побудованого dist: загальний regression, маршрути кейсів і `browser-case-storage.py`. Для Firefox/WebKit змініть перший аргумент. Новий suite працює з синтетичним особистим fixture, примусовими помилками sessionStorage та реальним JSON-download; результати в `case-storage/results.json` входять у candidate manifest. Не запускайте тестові fault injection у профілі з особистими даними.

У кейсі кнопка «Експортувати стан прикладу (JSON)» готує поточний навчальний стан із case ID/version та schema 4. Це окремий формат `asp24-nggroup-case-state` exportVersion 1; він не передається до імпорту особистих проєктів. `browser-export.js` одночасно залишає точний JSON/TXT на сторінці: feature detection не може підтвердити, що in-app browser справді зберіг файл. При відмові Clipboard доступне ручне виділення. У разі memory-only збережіть файл або текстову копію перед reload/закриттям. Для особистого стану попередження також пропонує JSON-копію; це не новий формат імпорту проєктів. Успіх очищення є передумовою автоматичного reload; за відмови поточний стан залишається доступним для експорту.

## Modern Experience

Новий React-простір відкривається з посилання у порівнянні або через `demo.html#/asp/compare?experience=modern`; для NG — `#/ng/compare?experience=modern`. Старий і новий UI читають одну schema 4. `src/domain` не залежить від DOM, React чи storage; `logic.js` зберігає сумісний API старих Node-тестів. Нові TS/TSX-модулі перевіряються в strict mode, старий UI JS переноситься поступово.

Для повної перевірки зміни: `npm ci`, `npm run typecheck`, `npm test`, `npm run build`, `npm run verify`. `BASE_PATH=/ npm run build` дає кореневий dist; стандартний build — Pages subpath. Preview навмисно не використовує SPA fallback: вкладені кейси мають власний index.html. Вихідний Vite manifest і SHA-256 inventory також перевіряються. React і його CSS — окремі dynamic chunks; hub не імпортує каталог.

Контрольна генерація звітів копіює tracked source до тимчасового дерева та використовує вже встановлений lockfile toolchain через локальне посилання на node_modules. Перед нею виконайте `npm ci`; нові вхідні файли мають бути tracked. Тотожність PDF/HTML підтверджується фактичною контрольною генерацією в тому самому pinned renderer/native-профілі.

Після build і запуску preview додатковий suite: `python scripts/browser-modern.py --url http://127.0.0.1:8000/asp24-nggroup-demo-research/ --browser chromium --output /tmp/modern-checks` (або firefox/webkit). Він не замінює три попередні browser suites. Захищений Chromium може потребувати `--executable /usr/bin/google-chrome` у CI; sandbox не вимикається.

Interaction polish зберігає видимі дії на touch: hover діє лише для fine pointer, переходи paint-токенів — 150 ms, focus-visible має окрему рамку, active pair і selected results залишаються позначеними без наведення. Reduced motion вимикає переходи. Закрите значення native select має ellipsis і власну стрілку; меню опцій, клавіатура та доступна назва залишаються нативними. Для coarse pointer основні кнопки/select/summary мають щонайменше 44 px висоти.

Новий interaction check вимірює реальні hover/pressed/focus стани й незмінність геометрії, feedback після дій/відмови сховища та fresh touch contexts 390/320 в обох брендах. Він перевіряє доставлений `touchstart`; `navigator.maxTouchPoints` записується як спостереження, оскільки Firefox emulation може повертати 0. Компактний `modern-visual-review-*` CI artifact дозволяє перегляд рендерів при великих failure traces; фінальний HTTP artifact містить усі успішні evidence.

`modern-preview.yml` будує обидва base paths, запускає всі suites і порівнює fixed RC2 із новою збіркою на одному runner. `scripts/performance-sample.py` робить п’ять почергових холодних запусків кожного сценарію та три Lighthouse-повтори. JSON зберігає середовище, сирі виміри, медіани, ресурси й обмеження. Це loopback-лабораторія, не польовий INP або швидкість на реальному мобільному інтернеті.

HTTP-preview artifact містить вже перевірений dist, evidence, `modern-manifest.json` і мінімальний `node scripts/serve.mjs`; npm install для його перегляду не потрібний. Повна збірка з джерел вимагає Node 24 і npm ci. Release artifact RC2 залишається окремим checkpoint.

## Інтегрований RC3

`rc3-preview.yml` запускається на push у `release/review-integrated-rc3` та перевіряє exact `github.sha`, не тимчасовий PR merge ref. Build перевіряє root і Pages subpath, повний Node/typecheck, обидва PDF/HTML, побайтове відтворення й два негативні stale-output сценарії. Той самий dist передається трьом browser jobs без повторного build. Попередні generic PR jobs пропускають лише цю пару head/base, бо їхні перевірки включені в RC3 workflow; CodeQL лишається окремим.

```sh
bash scripts/run-rc3-browser-checks.sh chromium /tmp/rc3-chromium
python scripts/package-rc3.py --build rc3-build --evidence rc3-evidence --output output/rc3-preview
```

Browser runner запускає дев’ять suites: regression, cases, case-storage, modern, rc3, reports-rc3, hardening, workbench-hardening та lazy-science. Попередні перевірки збережено; нові додають відмови download/clipboard/storage/React, контекст довгих таблиць і фокус активної пари, text-size/reflow та відмови/запізніле завершення лінивого завантаження project/lab UI. Для Chromium використовують доступний захищений Chrome/Chromium; sandbox не вимикається. Локальне середовище без придатного sandbox/бібліотек позначається BLOCKED, незалежний результат Actions записується окремо. Число перевірок береться з фактичного JSON, а не з історичного `46 PASS`.

Під час реалізації запускайте лише потрібний suite, наприклад `python scripts/browser-hardening.py --url http://127.0.0.1:8000/asp24-nggroup-demo-research/ --browser chromium --executable /usr/bin/chromium --output /tmp/p1-checks`. Спільний повний gate запускається після інтеграції всіх блоків. Browser fault injection використовує окремі синтетичні контексти. `--only` у P1 призначений для адресного повтору; у повному gate його не передають.

При відмові React chunk основна оболонка пропонує класичне порівняння, каталог, документи й HTML/PDF. Відмова лінивого project/lab chunk не змінює проєкти. Явний повтор дозволений лише після фактичного успіху збереження; memory-only лишається доступним для копії. WebKit може зберігати помилку модуля навіть після reload: recovery читає вже публічний Vite manifest, перевіряє адреси hashed science JS/CSS того самого origin і додає обмежений retry token. Токен лишається в URL для наступного reload; case/version, інші query-параметри та hash зберігаються. Цей додатковий запит відсутній у звичайному холодному завантаженні. Реальний HTTP 503, успішний повтор, наступний reload і тривала відмова перевіряються чинним lazy-science suite. Нативні Safari/iOS/Telegram/WebView та екранна клавіатура мають окремий [smoke-test власника](FINAL_HARDENING.md); WebKit CI не зараховується замість нього.

Попередній `rc3-performance.py` зберігає scoped спостереження кандидата. Для hardening `scripts/hardening-performance.py` зіставляє прийнятий b320 і новий dist на одному runner: холодні сценарії desktop/mobile, JS/CSS, LCP і click-to-two-frames, сирі повтори та медіани. Project/lab UI і CSS завантажуються за потреби, доменна логіка залишається спільною; preload Modern виконується лише для explicit modern route. Це loopback-лабораторія конкретного середовища, не польові Web Vitals і не загальна гарантія прискорення. Точні команди та результати входять у новий artifact; історичні метрики не переносяться на новий SHA.

Пакування перевіряє exact SHA всіх дев’яти suites на кожному engine, source/output manifests, inventories обох збірок, standalone hashes і фактичний PDF visual review. `rc3-manifest.json` та самодостатній ZIP містять source, готові reports/dist, результати й скриншоти; ZIP обмежено 32 MiB. Шрифти, браузерні профілі й приватний handoff не входять до пакета. Статус — `PREVIEW_NOT_DEPLOYED`; публікаційний контроль описано в `docs/RC3_REVIEW.md`. Hardening `c494b321fcb2f34a840956734c47d887078ed116` пройшов exact-SHA gate (CI 37948200453) і незалежне ACCEPT_PREVIEW; для кожного наступного commit потрібне адресне приймання. Release лишається PREVIEW_NOT_DEPLOYED до дозволеного merge/deploy.

## Зафіксоване середовище structured PDF

Build job `rc3-preview.yml` виконується в офіційному Python 3.12.14 / Debian trixie
container за immutable digest. `reports/native-runtime.json` фіксує image та
версії 35 системних пакетів; `scripts/install-report-runtime.py` застосовується
лише всередині цього контейнера. Чинні TLS/GPG та перевірки строків дії APT
збережені. `native-renderer.json` у build evidence записує встановлені версії.

Локальний контроль цього контейнера дав побайтово тотожні незалежно прийнятим
PDF результати. Інші шляхи checkout і шрифтів також не змінюють байти: print
адаптер передає ілюстрації як data URI, щоб абсолютний шлях не впливав на
WeasyPrint resource IDs. Ці зміни не нормалізують готові PDF й не послаблюють
контрольне порівняння. Свідчення — `reports/hardening-renderer-acceptance.json`.
