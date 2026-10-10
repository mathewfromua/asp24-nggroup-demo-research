# Фактичний стан та план правил GitHub (10.10.2026)

**Перевірено аудитом C на `65ff5d...`:** ruleset `24766636`, назва `main`, `enforcement=active`, ціль `~DEFAULT_BRANCH`. PR gate, strict required check `build` (GitHub Actions app 15368), заборона non-fast-forward та видалення; bypass відсутній. Classic branch-protection endpoint недоступний (403) — **NOT_VERIFIED**, не стверджуємо його відсутності.

**Важливо:** `.github/settings/main-ruleset.proposed.json` — історична пропозиція, **не** фактична конфігурація. Job `build` повторюється в `pages.yml`, `modern-preview.yml`, `rc3-preview.yml`; це неоднозначний required-check context. У старому репозиторії job/required-check не перейменовувати без узгодженої міграції (можна заблокувати відкриті PR). Для нового repo визначити унікальний required PR gate, прогнати його на живому PR і синхронно ввімкнути відповідний ruleset; не обходити захист.

Dependabot охоплює `github-actions`, `pip` для `reports/` і `scripts/`, а після інтеграції також `npm /` (weekly). YAML не доводить реальну активність alerts. CodeQL у `code-scan.yml` має `upload:false`: SARIF artifact ≠ доступні code-scanning alerts або enforced security gate. Secret scanning, push protection, dependency graph та Private Vulnerability Reporting перевіряти окремо; стан **NOT_VERIFIED**. Публікація Pages/visibility/rulesets у цій інтеграції **НЕ ЗМІНЮВАЛИСЬ**.
