# ASP24 / NG Group — Demo & Research

Версія 3.1.1-demo.1 · локальна міграція з Checkpoint 03. **GitHub і Pages ще не опубліковано: потрібна авторизація CLI.**

| Напрям | Фактичний результат |
|---|---|
| ENVIRONMENT | PASS: локальні команди й файли працюють; 725 вхідних записів звірено; дерево й доступну Sites Git-історію збережено окремо. |
| CONTENT | E01/E02 збережені. Змінені лише поточне найменування та активні демопосилання, без нової редактури фактів. |
| RESEARCH | EDITORIAL_DECISION=RECEIVED; RECEIVED_DR_TEXT=REJECTED_AS_DIRECT_EVIDENCE; VERIFIED_DELTA=PARTIAL_ACCEPTED; BROAD_SEO_COMPETITOR_RESEARCH=PENDING_REVIEW. |
| UNIT | 87 PASS, 0 FAIL, 2 SKIP. Сім нових міграційних перевірок: root/subpath HTTP, URL/redirect, outdated PDF hash, імпорт старого формату, назва й шрифтові запити. |
| BUILD | PASS: native ESM, один deployment.config.json, HTML/CSS/JS і report-manifest. Подання / і /asp24-nggroup-demo-research/ перевірені через HTTP; у dist лише дозволені активи. |
| REPORTS | ASP24 — 14 сторінок, NG Group — 16; PDF/HTML зі спільного джерела. 14 змінених сторінок переглянуті; 16 PNG незмінні, включно з обкладинками. Джерела, E01/E02, /Lang=uk-UA збережені. PDF/UA не заявлено. |
| DESKTOP / RESPONSIVE | PARTIAL_PASS: Codex In-app Browser; реальні HTTP/ESM/UI/reload. Пара зі шести, обидва вибори, remove/undo, заміна й режими; чернетка проєкту, Save/reload, 6570+10380=16950. Контрольна геометрія порівняння 320/375/390/430/1440 без переповнення сторінки; Back/Forward пройдено. Це не повне мобільне приймання. |
| SIMULATOR_SAFARI | BLOCKED: Xcode27.0, iOS27.0 runtime встановлений, але CoreSimulatorService відхиляє з’єднання. Safari у симуляторі не запускався. |
| SAFARI_MAC | NOT_RUN для цієї збірки. Встановлений Safari27.2/macOS27.2 beta; історичні часткові PASS не повторно зараховані. |
| PHYSICAL_IPHONE | NOT_RUN. Відсутність телефона не блокує дозволений демонстраційний preview. |
| PUBLICATION | BLOCKED_GITHUB_AUTH. gh2.101.0 без авторизації; target read/create-blob через підключення404, не доказ відсутності repo. Push, Pages deployment, Release і кінцева HTTPS-перевірка не виконані. |

Публічне дерево очищено від приватного досьє, абсолютних шляхів Mac, LAN-адрес, архівів, шрифтових файлів та старих повних PDF. Чотири повні WebP без встановленої підстави розповсюдження виключено з хешами; застосовано наявні піктограми. Історичний Sites не змінено.

Файлові/clipboard/storage fault-сценарії, реальний zoom і повний keyboard-only/VoiceOver цього проходу не завершені. Докладні факти: docs/qa-local-browser.json, docs/simulator-environment.json, reports/migration-review.json, docs/PUBLICATION.md. Очікувана адреса в конфігурації й PDF поки не є доказом публікації.

Наступний зовнішній крок — штатна авторизація GitHub CLI для mathewfromua; далі створити або недеструктивно доповнити repo, push, Pages й перевірити фактичний HTTPS page_url.
