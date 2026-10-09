# ASP24 / NG Group — дослідження та демонстраційні приклади

Два українські аналітичні огляди про вибір обладнання. **ASP24** — пошук, порівняння й підготовка закупівлі. **NG Group** — виконання виробу, технічний документ і предметна консультація. Демо дає змогу перевірити запропоновані механізми на умовних даних.

**Прийнятий preview:** RC3 Hardening [`c494b321`](https://github.com/mathewfromua/asp24-nggroup-demo-research/commit/c494b321fcb2f34a840956734c47d887078ed116), [PR №9](https://github.com/mathewfromua/asp24-nggroup-demo-research/pull/9), [успішний exact-SHA CI](https://github.com/mathewfromua/asp24-nggroup-demo-research/actions/runs/37948200453). Це кандидат `ACCEPT_PREVIEW`, **не опублікований RC3**. До дозволеного merge [GitHub Pages](https://mathewfromua.github.io/asp24-nggroup-demo-research/) показує попередній `main`; нові кейси можуть бути недоступними. Наступні cleanup-коміти потребують адресної перевірки, а не автоматичного перенесення приймання.

| Огляд | PDF цієї гілки | Повний адаптивний HTML |
|---|---|---|
| ASP24 · від пошуку до підготовки закупівлі | [14 сторінок](public/reports/ASP24_Review.pdf) | [HTML-файл](public/reports/ASP24_Review.html) |
| NG Group · від технічної інформації до вибору рішення | [16 сторінок](public/reports/NGGroup_Review.pdf) | [HTML-файл](public/reports/NGGroup_Review.html) |

GitHub показує HTML як код. Для читання завантажте зібраний [артефакт кандидата з Actions](https://github.com/mathewfromua/asp24-nggroup-demo-research/actions): `standalone/` містить HTML з вбудованими ілюстраціями й PDF; `dist/` — сайт для HTTP-preview. Точний SHA, фактичні перевірки, посилання на artifact і залишки — у [RESULTS.md](RESULTS.md).

## Чотири приклади

- **Пара з шести кандидатів** — змінити обидві моделі, зберегти повний добір, прибрати й повернути кандидата.
- **Прогалина поруч із відмінністю** — невідома маса поряд із 520 г і 860 г.
- **Дві бухти — 610 метрів** — кількість, одиниця та умовна сума 16 950 грн.
- **Документ тієї самої моделі** — DEMO-U02/D1, запитання й повернення до картки.

Вхід і повернення прив’язані до конкретних розділів оглядів. Стан прикладу відокремлений у вкладці; особисті кошик, проєкти й чернетки не скидаються. [Карта публікації](publication.json) фіксує версії та розділи.

## Межі

384 синтетичні моделі, 13 умовних виробників, вісім категорій. Ціни не є реальними пропозиціями. Замовлення, платежі й звернення не надсилаються; інтеграцій із робочими системами компаній немає. Огляди не встановлюють трафіку, конверсії або репрезентативної частоти проблем.

Обидва фінальні PDF **структурно теговані** (14/16 сторінок, векторні обкладинки) та пройшли veraPDF PDF/UA-1 **machine validation**; [R42](reports/TAGGED_PDF.md) закрито щодо тегування. Фактичне читання VoiceOver, нативний Safari/iPhone і Telegram/Android WebView — **NOT_RUN**; Playwright WebKit їх не замінює. Семантичний HTML залишається доступною альтернативою.

## Запуск

Node.js 24; Vite 8, strict TypeScript і ліниво завантажуваний React Comparison Workbench. Готові PDF/HTML включені. Версії закріплені в lockfile.

```sh
npm ci
npm run typecheck
npm test
npm run build
npm run verify
npm run preview -- --host 127.0.0.1 --port 8000
```

Відкрийте `http://127.0.0.1:8000/asp24-nggroup-demo-research/`. Початкова сторінка не завантажує каталог. Повне демо — `demo.html`; React-простір — `demo.html#/asp/compare?experience=modern` (для NG замініть `asp` на `ng`). Посилання на нього є у порівнянні; старі `#/asp/...` і `#/ng/...` збережені. Для кореневого розміщення: `BASE_PATH=/ npm run build`. `file://` придатний для standalone-читання, але не для інтерактивного ESM-демо.

## Джерела й відтворення

[Рукопис](reports/content.json) → два генератори → PDF/HTML. [Карта джерел](reports/claim-map-editorial.json), [нове читання PDF](research/editorial-source-register.json), [рішення R01–R44](research/editorial-decisions.json), [прийняті E01/E02](research/ACCEPTED_DECISIONS_UA.md). [DEVELOPMENT](docs/DEVELOPMENT.md) містить команди точної генерації й негативні перевірки застарілих outputs; [Контракт публікації](docs/PUBLICATION_CONTRACT.md) — стабільні маршрути, стани та післярелізна перевірка.

`public/` містить лише дозволені web-активи; `dist/` генерується. `reports/` — рукопис, шаблони й manifests; `research/` — очищена карта доказів; `tests/` і `scripts/` — регресії та перевірки. Зовнішні шрифти й приватні архіви не входять до Git або bundle. [Атрибуція](THIRD_PARTY_NOTICES.md) зберігає права на сторонні матеріали.
