# Публікація демонстраційного випуску

Стан: **PUBLISHED_DEMO_VERIFIED**. Дата: 09.10.2026.

- Репозиторій: https://github.com/mathewfromua/asp24-nggroup-demo-research
- HTTPS-демо: https://mathewfromua.github.io/asp24-nggroup-demo-research/
- Випуски: https://github.com/mathewfromua/asp24-nggroup-demo-research/releases
- Перший змістовний коміт: `55a4e2515d0bf1b5c94ad99449bf8f8ee125ec08`.
- Перша успішна публікація: https://github.com/mathewfromua/asp24-nggroup-demo-research/actions/runs/37863652491

Після штатного входу GitHub CLI підтвердив mathewfromua та права repo/workflow. Створено публічний репозиторій, відправлено main і повторно прочитано SHA коміту з GitHub. Окремий чистий clone підтвердив 121 запис початкового manifest, 87 PASS / 0 FAIL / 2 SKIP, build і verify без встановлення npm-залежностей.

Pages налаштовано на GitHub Actions, HTTPS увімкнено. Workflow публікує лише dist. Етап verify-publication одержав усі 33 файли саме з публічної адреси; SHA-256, PDF-сигнатури й MIME PDF/HTML збіглися. Машинний результат з автентифіковано отриманого журналу Actions: [published-byte-check-ci.json](published-byte-check-ci.json). Пізніші зміни README й доказів не змінюють байти застосунку та звітів; актуальний коміт визначається Git і тегом випуску.

У браузері на кінцевій адресі перевірено шість кандидатів, вибір обох позицій пари U05/U06, режим відмінностей та reload. Відкриті обидва HTML-огляди; NG HTML на ширині 390 CSS px і повернення до демо перевірені окремо. Деталі й межі: [qa-published-browser.json](qa-published-browser.json). Це не Safari або фізичний iPhone.

Перша локальна спроба HTTPS-перевірки через Python затримувалася під час встановлення proxy-з’єднання й була зупинена. Це не результат FAIL застосунку. Повний HTTP-прохід цього deployment виконано в GitHub Actions; окремий локальний curl-прохід записано у published-byte-check.json зі своїм методом.

Попередня відсутність авторизації й HTTP404 належать до підготовчого проходу. Блокер авторизації усунено користувачем; ці старі результати не описують поточний доступ.

Історичний Sites не видалено, не змінено й не перенаправлено. localStorage між origin автоматично не переноситься. E01/E02, 384 моделі та схема сховища збережені. Ширший SEO/конкурентний матеріал і завершене Apple-приймання залишаються окремими відкритими завданнями; демонстраційний prerelease не засвідчує їх виконання.
