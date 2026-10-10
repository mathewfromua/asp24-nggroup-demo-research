# Джерела оглядів ASP24 / NG Group

`content.json` — спільне джерело тексту для PDF та адаптивного HTML. `content.py` підставляє активну адресу демо з `deployment.config.json` замість `{{PUBLIC_BASE_URL}}`. `build_editorial.py` створює PDF з фактичною кількістю сторінок (раніше 14/16); `build_html.py` — семантичні HTML. `export_standalone.py` додатково вбудовує зображення для читання без мережі.

Обкладинки в `covers/` — незмінені перші сторінки попередніх оглядів. `covers/provenance.json` містить хеші повних історичних документів та виділених обкладинок. Повні старі PDF зберігаються окремо від публічного репозиторію. Основні сторінки створюються заново, без прихованого шару старих сторінок.

Потрібні Python-залежності в `requirements.txt` і зовнішні шрифти з ідентифікаторами у `fonts/provenance.json`. Шрифтові файли не поширюються. Приклад складання з кореня репозиторію:

```sh
python3 -m pip install -r reports/requirements.txt
REPORT_FONT_DIR=/path/to/fonts python3 reports/build_editorial.py
python3 reports/build_html.py
python3 reports/export_standalone.py
```

`claim-map-editorial.json` зберігає межі тверджень і пов'язує їх із джерелами та сторінками. Для історичних матеріалів, яких немає в публічному репозиторії, вказано окремий статус доступності; це не нове читання джерела. `source_links.json` містить точні зовнішні адреси з поточної редакції, зокрема дві різні пропозиції M1550-C. `image-provenance.json` описує незмінені зображення й точні кадрування. `migration-review.json` фіксує перевірку міграційних змін. Межі публічної доказової бази — у `docs/RESEARCH.md`.

Для вихідного RC3 SHA `65ff5d...` PDF мали український `/Lang`, логічні теги `StructTreeRoot`, таблиці `TH/TD`, `Figure/Alt` та машинний PASS veraPDF PDF/UA-1. Після цієї редакції **кожен новий PDF потребує повторної незалежної валідації**: попередній PASS не переноситься на нові байти. Повний тест VoiceOver, native Safari та WCAG — NOT_RUN. HTML використовує семантичні заголовки, таблиці з `th/scope`, підписи, альтернативні тексти й доступну навігацію.

Канонічний pinned renderer: Python 3.12.14 у зафіксованому digest container, `scripts/install-report-runtime.py`, `reports/requirements.txt`, перевірені шрифти з `scripts/fetch-report-fonts.py`; veraPDF 1.30.3 — через `scripts/fetch-verapdf.py`. Відтворення: `python reports/build_editorial.py`, `python reports/build_html.py`, `python reports/export_standalone.py`, `python reports/build_inputs.py --write`, `python scripts/check-report-reproduction.py`, `python scripts/verify-structured-pdfs.py`. Точні команди й межі у `docs/DEVELOPMENT.md`.
