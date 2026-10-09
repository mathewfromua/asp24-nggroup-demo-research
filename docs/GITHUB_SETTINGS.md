# Пропозиція захисту main — не застосована

09.10.2026: `GET /rulesets` повернув `[]`. `GET /branches/main/protection` — 403 Resource not accessible by integration; стан branch protection невідомий. Repo metadata містить admin=true, але це не надає connector token адміністративних операцій. `security_and_analysis` повернуло null: secret scanning / push protection не підтверджені.

`.github/settings/main-ruleset.proposed.json` — idempotent бажаний стан одного ruleset за назвою, тільки main. Перед застосуванням перечитати rulesets і захист гілки: створити за відсутності або оновити знайдений ruleset за його ID, не створювати дубль. Фактичний check `build` успішно працює в PR №3; app ID GitHub Actions 15368 прочитано з check-runs. Застосування потребує окремого явного погодження користувача; у цьому проході settings не змінювали.

Пропонується PR, 0 сторонніх approvals, вирішені дискусії, актуальність до main, build, заборона force push і видалення. Не додаються restrict updates, deployment gate, підписування, code-owner/last-push approval, merge queue або bypass для агента. Report/browser checks можна зробити required лише після фактичного успішного й негативного запуску; YAML сам не є merge gate.

Одна вебоперація після погодження: [Settings → Rules → Rulesets](https://github.com/mathewfromua/asp24-nggroup-demo-research/settings/rules) → імпортувати/звірити зазначений JSON для main, попередньо перевіривши чинний branch protection. PAT у чат не потрібний.

Dependabot підготовлено для Actions та Python; npm-пакетів немає. Це не доказ увімкнених alerts/push protection. CodeQL/code scanning належить перевірити в Security окремо: конфігурація сканера, доступ token до findings і merge gate — різні кроки.
