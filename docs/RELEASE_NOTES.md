# Пріоритетне оновлення 10.10.2026 — адресна інтеграція PR #9

Цей документ нижче є **історією приймання попередніх SHA**, а не автоматичним PASS після зміни `reports/content.json`. Поточний кандидат слід ідентифікувати за actual PR #9 HEAD і exact run. Окремі статуси: evidence SECONDARY_BOUNDED, R34 OPEN_EXTERNAL_SOURCE, невідома ревізія FHP12A, license OWNER_DECISION, old Git history SENSITIVE_BLOCKER, new PDF/CI requires actual validation, public release HOLD. Нативний Safari, Telegram WebView і VoiceOver — NOT_RUN. `main`/Pages не змінювалися.

---

# RC3 Hardening — прийнятий preview · 09.10.2026

**SHA `c494b321fcb2f34a840956734c47d887078ed116`**; PR #9, [CI SUCCESS](https://github.com/mathewfromua/asp24-nggroup-demo-research/actions/runs/37948200453), artifact 11624359601. Статус `ACCEPT_PREVIEW / PREVIEW_NOT_DEPLOYED`.

- Структуровані PDF ASP24 14 с. і NG Group 16 с. із векторними обкладинками; veraPDF PDF/UA-1 machine PASS. R42 `CLOSED_STRUCTURAL_TAGGING`; VoiceOver NOT_RUN.
- HTML, `reports/content.json`, E01/E02 і доказові межі залишені без редакційних змін.
- Sticky-контекст, активна пара A/B, краща мобільна типографіка, відновлення позицій та fallback для export/clipboard/storage/lazy loading; Node 127 PASS і по 60 PASS у трьох рушіях.
- R34 `OPEN_EXTERNAL_SOURCE`; native Safari/iPhone, Android Chrome, Telegram/WebView та native zoom NOT_RUN.

Розділи нижче описують **історичні** RC3/RC2; їхні старі R42 OPEN і PRE_GATE більше не характеризують чинний прийнятий RC3 Hardening.

---

# 3.2.0-rc.3 — інтегрований кандидат для незалежного читання

Огляди уточнюють п’ять DC-виходів окремо від USB, розбіжність опублікованих діапазонів FHP12A та застосовність документів до виконання виробу. Нова атрибуція розділяє історичну вторинну опору і конкретне отримання PDF з actual hashes, датою, сторінками та межами. Два PDF і два HTML відтворено з одного рукопису; обкладинки й frozen section IDs збережено.

Покращено контраст дрібного помаранчевого тексту, джерела й підписи, предметні HTML-заголовки, назви таблиць, citation anchors та вузькі графіки. Hub українською представляє огляди перед демонстраційними прикладами.

Modern Experience має компактний контекст кейсу, зберігає свій режим після картки/документа та підтримує скасування останньої заміни зі збереженням слота й пари. Кошик, інші групи та чернетки не залежать від цього undo; особистий стан ізольований від кейсів.

Фактичні exact-SHA результати, viewport geometry, скриншоти й готовий HTTP-preview знаходяться в artifact workflow RC3 та draft PR. Це не незалежне приймання. R34/R42 залишаються відкритими; Native Safari, фізичний iPhone, native zoom, VoiceOver — NOT_RUN. **PREVIEW_NOT_DEPLOYED:** main, PR #7/#8 і Pages не змінено. Деталі: [RC3_REVIEW.md](RC3_REVIEW.md).

---

# 3.2.0-rc.2 — preview with limitations

Виправлено блокер незалежного читання RC1: помилки sessionStorage не приховуються як успішний запис. Кейс повідомляє про роботу лише в пам’яті та ризик перезавантаження; поточний навчальний стан можна явно експортувати до JSON. Невдалий reset не перезавантажує сторінку. Особисті кошик, проєкти, кандидати й чернетки залишаються ізольованими від чотирьох кейсів.

У NG Group уточнено застосовність 14 календарних днів до діагностики й ремонту гарантійного обладнання та текстовий відповідник XPON-ілюстрації. Обидва PDF/HTML генеруються зі спільного рукопису; E01/E02, сторінковість 14 + 16, обкладинки, одиниці та історичні межі збережено. Загальної редакції й нового дослідження немає.

Адресний case-storage suite доповнює всі попередні Node і Chromium/Firefox/WebKit перевірки; artifact містить їхні фактичні результати на одному SHA. Статус незалежного приймання не випливає автоматично з CI.

Залишки: R34 — відлік сервісних строків; R42 — untagged фінальні PDF; stable Safari, фізичний iPhone, native zoom і VoiceOver — NOT_RUN. PDF/UA чи WCAG-сертифікація не заявляється. Main і чинний Pages не оновлено. Не позначати кандидат stable/latest. Технологічна модернізація розробляється окремим PR після технічного завершення RC2.
