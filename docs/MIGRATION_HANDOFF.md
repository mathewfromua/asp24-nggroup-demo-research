# F migration handoff — curated snapshot, no history

**Поточна задача E:** усі адресні редагування здійснюються у PR #9; не створювати repo, не змінювати visibility, `main`, Pages чи domain. Передача F — тільки після exact-SHA CI та незалежної privacy/evidence перевірки.

## Точні дані й межі

- Джерело істини: `reports/content.json` → `public/reports/*.pdf` + `*.html`; обидва генеруються тільки pinned renderer. `reports/input-manifest.json` / HTML/PDF manifests оновлюються разом. `reports/editorial-validation.json` — **історичний** RC2/RC3 індекс; старі PASS не поширюються на нові байти. `reports/hardening-pdf-acceptance.json` прив'язаний до вихідного SHA; машинна PDF/UA-1 і VoiceOver оцінюються окремо.
- Поточне дерево до cleanup: 227 tracked files. Нуль масових видалень: 23 `ARCHIVE_OFF_REPO` не видаляти без durable restricted archive, old→new index, SHA-256 і CI dependency proof; `reports/figures/*.pdf` (3) не видаляти до перевірки renderer/manifests. 3 brand/social assets — OWNER_DECISION.
- **Заборонено до нового публічного репозиторію:** старий `.git`/refs/commits/tags/PR history, старі raw Actions/ZIP/logs/traces, приватні DOM/JSON/cookies, машинні абсолютні шляхи й контакти, локальні `.env` та тимчасові інструкції інтегратора. Git history old має confirmed author/committer PII у 49/54 ancestor commits; новий clean repository не очищує стару публічну історію.
- **Обов'язково зберігати:** неособисту upstream licensing attribution; джерела, дати, непевності, E01/E02; PDF/UA tags/XMP `/Lang`, TH/TD, Figure/Alt, bookmarks, links. Заборона blind metadata stripping.

## URL/base-path diff contract

Старий `https://mathewfromua.github.io/asp24-nggroup-demo-research/` і `BASE_PATH=/asp24-nggroup-demo-research/` — операційний контракт саме старого repo. Для нового owner/slug: `deployment.config.json`, Vite/base-path, `publication.json` generation, pages/workflows, canonical/OG, CSS/asset URLs, 4 versioned case paths + 4 aliases, HTML/PDF internal links, `public/reports`, README/docs, SEO robots/noindex, root та subpath check. Аудит D знайшов 38 tracked files / 146 old-slug mentions та 12 PDF URL annotations: мігрувати **за призначенням**, не глобальним search-replace. Історичні джерельні URL не переписувати. Нові built bytes → нові SHA256 та повний re-render.

## Owner decisions / gates

1. Новий private staging → fresh one-parentless clean history; allowlisted neutral/noreply Git author/committer/tagger, без старих refs; публікація тільки після окремого GO.
2. Правовий режим коду, документів, брендів, зображень; explicit grants або виключення.
3. Доля old public GitHub+Pages+artifact logs після restricted archiving; external caches/clones не можна гарантовано стерти.
4. Офіційна відповідь NG щодо R34/FHP12A, чи є дозволені historical raw captures; поки `OPEN_EXTERNAL_SOURCE`/`SECONDARY_BOUNDED`.
5. Нові required job IDs, npm Dependabot actual run, security alerts/Private Vulnerability Reporting states.
6. Exact-SHA Node24 + Python3.12.14 native pinned renderer + veraPDF, 3 browser engines, 8 case routes, 30+ PDF pages actual, all file hashes; native Safari/iPhone/VoiceOver залишаються NOT_RUN, якщо не перевірені.

**Final release verdict:** HOLD_PUBLIC_RELEASE до виконання owner, privacy, evidence та new exact-SHA gates. Не називати snapshot правочинним OSS-дистрибутивом без owner decision.
