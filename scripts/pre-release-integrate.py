"""One-shot coordinated RC3 source integration. No GitHub operations in this script.
The renderer/commit gate is kept separate and self-deleting after success.
"""
from __future__ import annotations
import base64,csv,io,json,re,zlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'reports/content.json'
data=json.loads(p.read_text(encoding='utf-8'))
changes=[]

def sec(brand,ident):return next(s for s in data[brand] if s['id']==ident)
def replace(brand,ident,index,old,new):
    block=sec(brand,ident)['blocks'][index]
    def change(item):
        if isinstance(item,str):return item.replace(old,new)
        if isinstance(item,list):return [change(x) for x in item]
        return item
    previous=json.dumps(block,ensure_ascii=False)
    assert previous.count(old)==1,(brand,ident,index,previous.count(old))
    block[:]=change(block)
    changes.append(f'{ident}[{index}]')

# Exact B P1 edits and A evidence corrections. Quote assertions prevent drift.
replace('ASP24','asp24-02',1,'Запит за потребою може об’єднувати різне обладнання.', 'Запит, що описує потребу без назви моделі, може потребувати уточнення за призначенням і характеристиками обладнання.')
replace('ASP24','asp24-05',0,'Ці рядки дозволяють зіставити комутатори, якщо назви й значення мають однаковий зміст.', 'Кількість LAN-портів відрізняється — 8 і 24. Інші рядки потребують застережень: значення «Пропускної здатності» не звірено з паспортами, а порожнє поле Combo-портів не означає нуля.')
replace('ASP24','asp24-07',5,'Синтетичні дані демо.','Сума двох умовних позицій — 16 950 грн (6 570 + 10 380). Дві бухти кабелю становлять 610 м. Синтетичні дані демо.')
replace('ASP24','asp24-11',2,'Відмінність змістовної категорії від випадкової комбінації фільтрів','Чи утворює сторінка категорії самостійний зміст; які комбінації фільтрів потребують окремих URL та індексації')
replace('ASP24','asp24-11',5,'Отже, код формував суму й перелік товарів для різного складу.','Отже, value та items у цьому фрагменті стосувалися різних наборів товарів.')
replace('NGGroup','nggroup-05',6,'Автоматична перевірка знаходить розбіжності, але не визначає застосовності документа.','Автоматична перевірка може виявляти розбіжності між опублікованими значеннями; застосовність документа до конкретного виробу потребує окремого технічного звірення.')
replace('NGGroup','nggroup-15',6,'</link> Додаткова текстова звірка','</link>. Додаткова текстова звірка')
replace('ASP24','asp24-05',6,'Підрахунок відтворено зі збережених витягів.','Числа походять із раніше збережених підрахунків; первинні архівні витяги недоступні для незалежного перерахунку в цьому пакеті.')
replace('NGGroup','nggroup-05',2,'Номери не означають обсягу, дата URL — редакції. Поставка невідома.','Друковані номери не визначають кількості доступних сторінок, а дата у шляху URL не підтверджує редакції документа. Виконання поставки не встановлено.')
replace('NGGroup','nggroup-07',4,'Історичний підпис 13.16.2025 і надрукований строк — окремі спостереження.','Історичний некоректний календарний підпис «13.16.2025» у переліку файлів і надрукований строк чинності документа 14.06.2024–13.06.2025 — різні спостереження.')

# B-014: numeric digits/signs unchanged; protect measurement + unit from split.
measure=sec('NGGroup','nggroup-05')['blocks'][1]
count=0
for row in measure[2]:
    for j,value in enumerate(row):
        if isinstance(value,str):
            updated,n=re.subn(r'(?<=[0-9]) dBm\b','\u00a0dBm',value)
            row[j]=updated;count+=n
assert count==5,count
changes.append('nggroup-05[1]:nonbreaking-dBm')

# B-017: new note above, retained original caveat below.
blocks=sec('NGGroup','nggroup-06')['blocks']
index=next(i for i,item in enumerate(blocks) if item[:2]==['figure','autonomy'])
assert not any('Теоретична тривалість за t' in str(x) for x in blocks)
blocks.insert(index,['note','Теоретична тривалість за t = E/P, без урахування втрат.'])
changes.append('nggroup-06:pre-figure-qualifier')
assert len(data['ASP24'])==13 and len(data['NGGroup'])==15
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Engineering P1: include root npm ecosystem without disturbing existing schedules.
dep=ROOT/'.github/dependabot.yml'
s=dep.read_text();assert 'package-ecosystem: npm' not in s
anchor='  - package-ecosystem: pip\n    directory: /reports'
assert s.count(anchor)==1
dep.write_text(s.replace(anchor,'  - package-ecosystem: npm\n    directory: /\n    schedule:\n      interval: weekly\n'+anchor))

# Resolve obvious contradictory current docs; keep historical artifacts clearly labeled.
readme=ROOT/'README.md'
s=readme.read_text()
pos=s.index('**Прийнятий preview:**');end=s.index('\n\n| Огляд',pos)
s=s[:pos]+('**Передрелізна інтеграція 10.10.2026:** PR #9, гілка `release/review-integrated-rc3`. '
    'Попередній доказовий SHA `65ff5d270328a8842da22e524713d3a7ad3f9a1e`; поточний інтеграційний SHA беріть безпосередньо з PR/Actions. '
    '**HOLD_PUBLIC_RELEASE:** без нового independent exact-SHA gate, рішення щодо прав та remediated privacy old Git history публікація не дозволена. '
    'Успіх попередніх CI-run не переноситься на нові PDF/HTML; чинна GitHub Pages відображає `main`, не RC3. '
    'Вихідні докази мають межі `SECONDARY_BOUNDED`, а не незалежно відновлену історію.')+s[end:]
s += ('\n\n## Передача незалежному розробнику\n\n'
      'Поточний маршрут: [архітектура](docs/ARCHITECTURE.md) → [розробка](docs/DEVELOPMENT.md) → '
      '[відтворення оглядів](reports/README.md) → [інтеграційний ledger](docs/INTEGRATION_LEDGER.md) → '
      '[рішення щодо прав](docs/RIGHTS_LICENSE_DECISION.md) → [migration handoff](docs/MIGRATION_HANDOFF.md). '
      '`manifest.json` є історичним 3.1.1 snapshot, на відміну від генерованого `publication.json`; '
      'current-vs-historical QA-перевірки не змішуються. Наявність notices для сторонніх компонентів не є OSS-ліцензією власного коду.\n')
readme.write_text(s)

r=ROOT/'reports/README.md';s=r.read_text()
s=s.replace('`build_editorial.py` створює PDF на 14 і 16 сторінок;', '`build_editorial.py` створює PDF з фактичною кількістю сторінок (раніше 14/16);')
s=s.replace('PDF мають український `/Lang`, але не перевірений `StructTreeRoot`. HTML містить семантичні заголовки, таблиці з `th`/`scope`, підписи та альтернативні тексти. PDF/UA чи повну WCAG-сертифікацію не заявлено.',
    'Для вихідного RC3 SHA `65ff5d...` PDF мали український `/Lang`, логічні теги `StructTreeRoot`, таблиці `TH/TD`, `Figure/Alt` та машинний PASS veraPDF PDF/UA-1. Після цієї редакції **кожен новий PDF потребує повторної незалежної валідації**: попередній PASS не переноситься на нові байти. Повний тест VoiceOver, native Safari та WCAG — NOT_RUN. HTML використовує семантичні заголовки, таблиці з `th/scope`, підписи, альтернативні тексти й доступну навігацію.\n\nКанонічний pinned renderer: Python 3.12.14 у зафіксованому digest container, `scripts/install-report-runtime.py`, `reports/requirements.txt`, перевірені шрифти з `scripts/fetch-report-fonts.py`; veraPDF 1.30.3 — через `scripts/fetch-verapdf.py`. Відтворення: `python reports/build_editorial.py`, `python reports/build_html.py`, `python reports/export_standalone.py`, `python reports/build_inputs.py --write`, `python scripts/check-report-reproduction.py`, `python scripts/verify-structured-pdfs.py`. Точні команди й межі у `docs/DEVELOPMENT.md`.')
r.write_text(s)

r=ROOT/'docs/ARCHITECTURE.md';s=r.read_text()
s=s.replace('# Modern Experience: реалізовані межі','# ASP24 / NG Group — current RC3 architecture and boundaries')
s=s.replace('Ця гілка походить від технічно перевіреного RC2 `0034b000bd1bad42f0c3ffb222a0ec58308a42bc`. Вона не змінює release-гілку автоматично. Два українські огляди залишаються основним продуктом; їхні готові PDF/HTML та рукопис збережено.',
    'Поточний об’єкт — PR #9 `release/review-integrated-rc3`, похідний від RC2 `0034b000...`; головна гілка та Pages не приймають зміни автоматично. Продукт: два україномовні огляди, спільний рукопис і синтетичний React/legacy demo. Доступність структури PDF/UA-1 перевіряється на exact generated bytes, не за статусом старого baseline.')
s=s.replace('R42 досліджується окремим повним tagged-експортом. До змістової, структурної й візуальної перевірки цей експеримент не замінює чинні PDF і не закриває PDF/UA. R34 також залишається відкритим.',
    'Для вихідного RC3 R42 закрито щодо machine PDF/UA-1 structural validation; скринрідер VoiceOver NOT_RUN. Після будь-якої перегенерації потрібен **новий exact-byte gate**, а не перенесення старого PASS. R34 залишається OPEN_EXTERNAL_SOURCE. `manifest.json` — історичний release record 3.1.1; поточна карта маршрутів — `publication.json`, яку генерує build.')
s += ('\n\n## Developer entrypoints та data flow\n\n'
      '| Межа | Вхід | Вихід / контроль |\n|---|---|---|\n'
      '| Зміст і PDF/HTML | `reports/content.json`, `reports/build_editorial.py`, `build_tagged.py`, `build_html.py` | `public/reports/*`, `reports/*manifest.json`; `scripts/verify-reports.py` |\n'
      '| Синтетичні дані | `data.js`, `catalog-expanded.js`, `src/data/` | каталожний стан і версійні кейси; Node + browser tests |\n'
      '| Правила й збереження | `src/domain/`, `src/adapters/`, `logic.js` | типізовані інваріанти, storage schema 4 і відмови |\n'
      '| Інтерфейс | `app.js`, `src/ui/`, `src/styles/` | Vite-built `dist`, dynamic React import |\n'
      '| Build / routing | `scripts/build-static.mjs`, `scripts/verify-build.mjs`, `deployment.config.json` | root/Pages paths, asset allowlist, 8 case routes |\n'
      '| CI | `.github/workflows/rc3-preview.yml` | exact-SHA build, 3 browser engines; старі workflow лишено для відкритих PR |\n')
r.write_text(s)

r=ROOT/'docs/GITHUB_SETTINGS.md'
r.write_text('''# Фактичний стан та план правил GitHub (10.10.2026)

**Перевірено аудитом C на `65ff5d...`:** ruleset `24766636`, назва `main`, `enforcement=active`, ціль `~DEFAULT_BRANCH`. PR gate, strict required check `build` (GitHub Actions app 15368), заборона non-fast-forward та видалення; bypass відсутній. Classic branch-protection endpoint недоступний (403) — **NOT_VERIFIED**, не стверджуємо його відсутності.

**Важливо:** `.github/settings/main-ruleset.proposed.json` — історична пропозиція, **не** фактична конфігурація. Job `build` повторюється в `pages.yml`, `modern-preview.yml`, `rc3-preview.yml`; це неоднозначний required-check context. У старому репозиторії job/required-check не перейменовувати без узгодженої міграції (можна заблокувати відкриті PR). Для нового repo визначити унікальний required PR gate, прогнати його на живому PR і синхронно ввімкнути відповідний ruleset; не обходити захист.

Dependabot охоплює `github-actions`, `pip` для `reports/` і `scripts/`, а після інтеграції також `npm /` (weekly). YAML не доводить реальну активність alerts. CodeQL у `code-scan.yml` має `upload:false`: SARIF artifact ≠ доступні code-scanning alerts або enforced security gate. Secret scanning, push protection, dependency graph та Private Vulnerability Reporting перевіряти окремо; стан **NOT_VERIFIED**. Публікація Pages/visibility/rulesets у цій інтеграції **НЕ ЗМІНЮВАЛИСЬ**.
''')

r=ROOT/'docs/DEVELOPMENT.md';s=r.read_text().replace('export PERSPEKTYVA_FONT_DIR=/absolute/path/to/your/fonts','export REPORT_FONT_DIR=/absolute/path/to/your/fonts');r.write_text(s)

prefix='''# Пріоритетне оновлення 10.10.2026 — адресна інтеграція PR #9

Цей документ нижче є **історією приймання попередніх SHA**, а не автоматичним PASS після зміни `reports/content.json`. Поточний кандидат слід ідентифікувати за actual PR #9 HEAD і exact run. Окремі статуси: evidence SECONDARY_BOUNDED, R34 OPEN_EXTERNAL_SOURCE, невідома ревізія FHP12A, license OWNER_DECISION, old Git history SENSITIVE_BLOCKER, new PDF/CI requires actual validation, public release HOLD. Нативний Safari, Telegram WebView і VoiceOver — NOT_RUN. `main`/Pages не змінювалися.

---

'''
for name in ['RESULTS.md','docs/RELEASE_NOTES.md']:
    r=ROOT/name;s=r.read_text();assert 'Пріоритетне оновлення 10.10.2026' not in s;r.write_text(prefix+s)

rights='''# Rights / License Decision Sheet — owner GO required

**НЕ є ліцензією і не надає прав повторного використання.** Жодну OSS або proprietary ліцензію тут не вибрано; root `LICENSE` не створювати до письмового рішення правовласника.

| Категорія | Поточний стан | Потрібна дія |
|---|---|---|
| Власний JS/TS/Python, tests, docs | Немає root `LICENSE`; відсутній загальний дозвіл стороннім розробникам | Owner: OSS з точною ліцензією і scope **або** explicit proprietary/demo-read-only/reuse permissions |
| Два оригінальні українські огляди, фото/графіки | Тексти й власні демонстраційні схеми; сторонні цитовані матеріали | Окремо встановити права на текст, таблиці, інфографіку та умови відтворення |
| ASP24/NG Group trademarks, screenshots і логотипи | `public/assets/asp24-original.webp`, `ng-original.svg`, `research-social.png` мають невизначений rights scope | Підтвердити дозвіл або замінити/виключити за погодженим правовим рішенням; після заміни перевірити allowlist, visuals та посилання |
| Third-party JS, шрифтові ліцензії | `THIRD_PARTY_NOTICES.md`, `public/vendor-licenses.txt`, upstream font notices | Зберігати оригінальні copyright/license notices; чужі ліцензійні email не вважаються приватним контактом власника |
| Джерельні PDF / screenshots / historical evidence | Можливі сторонні copyrights, приватні raw captures | Публікувати лише дозволені мінімально необхідні цитати/демо; confidential provenance archive поза public repo |
| GitHub Actions, CI artifacts / archived QA | Rights/retention окремі від коду | Визначити строк, власність, privacy review і допуск до публікації |

**Відкриті рішення:** точна ліцензія власного коду, ліцензія на документацію/власні ілюстрації, юридична підстава використання логотипів/скриншотів, privacy old repo і new slug/Pages. Тільки власник може зняти OWNER_DECISION. Навіть open source code license не ліцензує чужі торгові марки, datasheets і copyrighted screenshots.
'''
(ROOT/'docs/RIGHTS_LICENSE_DECISION.md').write_text(rights)

handoff='''# F migration handoff — curated snapshot, no history

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
'''
(ROOT/'docs/MIGRATION_HANDOFF.md').write_text(handoff)

# Full A-categorization without fabricating primary evidentiary status.
compressed='eNp9lcFugzAMQO_7Fibh2Alw7ErWommAylapp_7_X4yVdmUQ3hFe7ZgX290N_WueSzbEfdfWu9Pl-tZ9t3Wss15edjfosv7UfP6iczw1783I2q6Nd6oUaino7tBTZKDIAisqKW8FUHI4VISgo7SadX1sn88pK8_6hbxIIFgQJC1SZfVo8hzr6_4Y9x__CnI56XaC1FHihRhnUKIjLS5MmWa5Czq4JLh28bhmzaEGlex46buvYxyaYZZPcX6U5kdtIyW5UGoRLaCLlVpEq3QtRk4Mm8PQjJEZMwz1y3awsKq-PRw2Nt8Mb8z1BJWgEfR8aqDYjRucYEmR1YazG5XElD8iRYA5zKpIDalHGtIzPMHib7NMz-XiGVWMC2879bjvADqCOuvK6Q1-v_Or34fte3AFXP248OggtKE5UvlvVmlilCZGaWJ05UIDzMG45pLjruhB0YOhB1t4MPJg5MEMPsw8RZISo_6wMu3LqvR7jy786p_wB6mvtm4='
rows=zlib.decompress(base64.urlsafe_b64decode(compressed)).decode().splitlines()
assert len(rows)==97
out=io.StringIO();w=csv.writer(out);w.writerow(['claim_id','review_A_classification','A_priority','integration_disposition','new_primary_evidence'])
choices={'PRIMARY_VERIFIED':'RETAIN_REVIEW_A_ASSESSED','SECONDARY_BOUNDED':'RETAIN_WITH_HISTORICAL_ATTRIBUTION','OPEN':'REMAIN_OPEN_EXTERNAL_OR_PROVENANCE','DERIVED_CHECKED':'RETAIN_WITH_EXPLICIT_ASSUMPTIONS','HYPOTHESIS':'RETAIN_AS_HYPOTHESIS_ONLY'}
for row in rows:
    ident,cls,priority=row.split(',');w.writerow([ident,cls,priority,choices[cls],'NO_NEW_PRIMARY_CAPTURE'])
(ROOT/'research/claim-ledger-integration.csv').write_text(out.getvalue())

# Unified ledger readable without displaying personal findings.
ledger='''# Unified Integration Ledger — A/B/C/D

**Source of audit verdicts:** four independent read-only reviews on Git SHA `65ff5d270328a8842da22e524713d3a7ad3f9a1e`; these status classes are taken **from reviewers**, not new primary source retrieval. Date 10.10.2026. Source edit is `reports/content.json` only; PDF/HTML must be regenerated and separately accepted. Use `research/claim-ledger-integration.csv` for **all 97 A IDs**; original review A detailed ledger remains separately archived with audit ZIP.

## A — evidence, all P1 buckets

| Issue | Decision / changed location | Evidence boundary / status |
|---|---|---|
| PATCH-01 / EA-03 FHP12A | `reports/content.json` NG `nggroup-05` note now states URL path date ≠ document revision | Text clarification, **fixed in manuscript**; revision of actual delivered unit **OPEN** |
| PATCH-02 / EA-02 historical `16→9, 14→0, 30→0` | ASP `asp24-05` caption no longer claims independent raw recomputation | **SECONDARY_BOUNDED**. Raw six history-v5 JSON/recompute not found across 8 tracked branch trees; numerators unchanged |
| PATCH-03 / EA-01 legacy DOM/filter/search/cart and Quattro-II/MultiPlus-II | Retain existing historical wording; 97-ID A ledger explicitly distinguishes PRIMARY/SECONDARY/OPEN | **SECONDARY_BOUNDED** absent timestamped raw DOM/click-path/PDF bytes; no synthetic claim of direct replay |
| PATCH-04 FHP12A measurement scopes | Preserve all four different published ranges and model applicability caution | **OPEN_EXTERNAL_SOURCE**: serial/revision/datasheet shipment unknown |
| PATCH-05 R34 service terms | Do not merge 14 calendar days and 2 weeks–3 months; keep source reading limitation | **OPEN_EXTERNAL_SOURCE** pending NG process owner |
| PATCH-06 invalid historic date | NG `nggroup-07`: literal «13.16.2025» labeled invalid; printed 14.06.2024–13.06.2025 retained | **FIXED TEXT**; not a fabricated date |
| PATCH-07/08 graph and PDF gates | Keep zeros ≠ missing description, buyer funnel ≠ vendor test; segregate historic editorial-validation | **FIXED DOCS**, new PDF/UA machine + visual gates still required |

A has 97 claim IDs: 25 PRIMARY_VERIFIED by auditor A, 44 SECONDARY_BOUNDED, 11 OPEN, 9 DERIVED_CHECKED, 8 HYPOTHESIS; classifications preserved, **no promotion** to newly acquired PRIMARY by this integration. A flagged 41 claim records P1, not 41 confirmed factual errors. No independent full historical DOM replay performed.

## B — editorial findings B-001…B-021

| ID | Action and manuscript location | Status before PDF acceptance |
|---|---|---|
'''
ids={'B-001':'ASP p2 search breadth neutralized','B-004':'ASP p5 8/24 LAN; 20/56 unverified; empty Combo not 0','B-007':'ASP p7 6 570+10 380=16 950; 2x305=610 m synthetic','B-010':'ASP p11 specific SEO category/filter question','B-011':'ASP p11 value/items mismatch described narrowly','B-014':'NG p5 nonbreaking dBm units; visual overflow must be checked','B-016':'NG p5 automatic check may detect discrepancies','B-017':'NG p6 t=E/P theoretical pre-figure label','B-021':'NG p15 08.10 secondary reading separated from 09.10 PDF'}
for i in range(1,22):
    tag=f'B-{i:03d}'
    if tag in ids:ledger+=f'| {tag} (P1) | {ids[tag]} | **SOURCE_EDIT_APPLIED**, PDF/HTML gate pending |\n'
    else:ledger+=f'| {tag} (P2) | Preserve established phrasing unless evidence-backed benefit; no global rewriting | **DEFERRED_NONBLOCKING** |\n'
ledger+='''
## C — repository

- C-LEGAL (P0): `docs/RIGHTS_LICENSE_DECISION.md` — **OWNER_DECISION**, no license chosen.
- C-DOCS (P1): README/reports README/ARCHITECTURE/GITHUB_SETTINGS/DEVELOPMENT/RESULTS/RELEASE_NOTES — **SOURCE_EDIT_APPLIED**; historical CI/PDF snapshots explicitly labeled.
- C-CI (P1): `.github/dependabot.yml` npm added; existing `build` required check **not renamed** because main ruleset 24766636 active. New-repo job/context migration remains OWNER_DECISION; security alerts **NOT_VERIFIED**.
- C-HYGIENE (P1): 169 KEEP, 24 SIMPLIFY, 5 CONSOLIDATE, 23 conditional archive, 3 conditional generated-PDF delete, 3 brand rights decision; **0 bulk deletions** prior to evidence retention and dependency check.

## D — privacy

- D-HISTORY (P0): confirmed old Git author/committer contact exposure in 49/54 ancestors — **SENSITIVE_BLOCKER_OLD_PUBLIC_HISTORY**, unaffected by content editing. Clean first commit in new private staging, not fork/merge old graph, awaits owner GO.
- D-SOURCE/PDF: no known personal contact in two original tagged PDFs according to review D; **new regenerated bytes require repeated audit** of source, Info/XMP, link annotations, images, attachments, PDF/UA tags, full-page review.
- D-LICENSE: 29 font-upstream license-email matches preserved as required legal attribution; not owner PII.
- D-MIGRATION: new owner/slug, old Pages/PR refs, artifact retention and security settings remain **OWNER_DECISION / NOT_VERIFIED**.

## Acceptance

`SOURCE_EDIT_APPLIED` is not `PDF_GENERATED`, `CI_PASS` or `INDEPENDENT_ACCEPTED`. E → F only after pinned reproducible reports, byte-level manifest, exact-SHA CI + 3 browser engines, privacy/rights review and handoff crosswalk. Public release HOLD.
'''
(ROOT/'docs/INTEGRATION_LEDGER.md').write_text(ledger)

print(json.dumps({'changes':changes,'claim_rows':len(rows),'doc_files':['README.md','reports/README.md','docs/ARCHITECTURE.md','docs/GITHUB_SETTINGS.md','docs/DEVELOPMENT.md','RESULTS.md','docs/RELEASE_NOTES.md','docs/RIGHTS_LICENSE_DECISION.md','docs/MIGRATION_HANDOFF.md','docs/INTEGRATION_LEDGER.md','research/claim-ledger-integration.csv','.github/dependabot.yml']},ensure_ascii=False))
