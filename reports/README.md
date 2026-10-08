# Джерела оглядів ASP24 / NG Group

`content.json` — спільне джерело тексту для PDF та адаптивного HTML. `content.py` підставляє активну адресу демо з `deployment.config.json` замість `{{PUBLIC_BASE_URL}}`. `build_editorial.py` створює PDF на 14 і 16 сторінок; `build_html.py` — семантичні HTML. `export_standalone.py` додатково вбудовує зображення для читання без мережі.

Обкладинки в `covers/` — незмінені перші сторінки попередніх оглядів. `covers/provenance.json` містить хеші повних історичних документів та виділених обкладинок. Повні старі PDF зберігаються окремо від публічного репозиторію. Основні сторінки створюються заново, без прихованого шару старих сторінок.

Потрібні Python-залежності в `requirements.txt` і зовнішні шрифти з ідентифікаторами у `fonts/provenance.json`. Шрифтові файли не поширюються. Приклад складання з кореня репозиторію:

```sh
python3 -m pip install -r reports/requirements.txt
REPORT_FONT_DIR=/path/to/fonts python3 reports/build_editorial.py
python3 reports/build_html.py
python3 reports/export_standalone.py
```

`claim-map-editorial.json` зберігає межі тверджень і пов'язує їх із джерелами та сторінками. Для історичних матеріалів, яких немає в публічному репозиторії, вказано окремий статус доступності; це не нове читання джерела. `source_links.json` містить точні зовнішні адреси з поточної редакції, зокрема дві різні пропозиції M1550-C. `image-provenance.json` описує незмінені зображення й точні кадрування. `migration-review.json` фіксує перевірку міграційних змін. Межі публічної доказової бази — у `docs/RESEARCH.md`.

PDF мають український `/Lang`, але не перевірений `StructTreeRoot`. HTML містить семантичні заголовки, таблиці з `th`/`scope`, підписи та альтернативні тексти. PDF/UA чи повну WCAG-сертифікацію не заявлено.
