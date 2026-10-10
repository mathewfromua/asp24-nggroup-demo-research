# Unified Integration Ledger — A/B/C/D

**Source of audit verdicts:** four independent read-only reviews on Git SHA `65ff5d270328a8842da22e524713d3a7ad3f9a1e`; these status classes are taken **from reviewers**, not new primary source retrieval. Date 10.10.2026. Source edit is `reports/content.json` only; PDF/HTML must be regenerated and separately accepted. Use `research/claim-ledger-integration.csv` for **all 97 A IDs**; original review A detailed ledger remains separately archived with audit ZIP.

## A — evidence, all P1 buckets

| Issue | Decision / changed location | Evidence boundary / status |
|---|---|---|
| PATCH-01 / EA-03 FHP12A | `reports/content.json` NG `nggroup-05` note now states URL path date ≠ document revision | Text clarification, **fixed in manuscript**; revision of actual delivered unit **OPEN** |
| PATCH-02 / EA-02 historical `16→9, 14→0, 30→0` | ASP `asp24-05` caption no longer claims independent raw recomputation | **SECONDARY_BOUNDED**. Raw six history-v5 JSON/recompute not found across 8 tracked branch trees; numerators unchanged |
| PATCH-03 / EA-01 legacy DOM/filter/search/cart and Quattro-II/MultiPlus-II | Quattro-II/MultiPlus-II now explicitly attributed to prior DEPS review; 97-ID A ledger distinguishes PRIMARY/SECONDARY/OPEN | **SECONDARY_BOUNDED** absent timestamped raw DOM/click-path/PDF bytes; no synthetic claim of direct replay |
| PATCH-04 FHP12A measurement scopes | Preserve all four different published ranges and model applicability caution | **OPEN_EXTERNAL_SOURCE**: serial/revision/datasheet shipment unknown |
| PATCH-05 R34 service terms | Do not merge 14 calendar days and 2 weeks–3 months; keep source reading limitation | **OPEN_EXTERNAL_SOURCE** pending NG process owner |
| PATCH-06 invalid historic date | NG `nggroup-07`: literal «13.16.2025» labeled invalid; printed 14.06.2024–13.06.2025 retained | **FIXED TEXT**; not a fabricated date |
| PATCH-07/08 graph and PDF gates | Keep zeros ≠ missing description, buyer funnel ≠ vendor test; segregate historic editorial-validation | **FIXED DOCS**, new PDF/UA machine + visual gates still required |

A has 97 claim IDs: 25 PRIMARY_VERIFIED by auditor A, 44 SECONDARY_BOUNDED, 11 OPEN, 9 DERIVED_CHECKED, 8 HYPOTHESIS; classifications preserved, **no promotion** to newly acquired PRIMARY by this integration. A flagged 41 claim records P1, not 41 confirmed factual errors. No independent full historical DOM replay performed.

## B — editorial findings B-001…B-021

| ID | Action and manuscript location | Status before PDF acceptance |
|---|---|---|
| B-001 (P1) | ASP p2 search breadth neutralized | **SOURCE_EDIT_APPLIED**, PDF/HTML gate pending |
| B-002 (P2) | Preserve established phrasing unless evidence-backed benefit; no global rewriting | **DEFERRED_NONBLOCKING** |
| B-003 (P2) | Preserve established phrasing unless evidence-backed benefit; no global rewriting | **DEFERRED_NONBLOCKING** |
| B-004 (P1) | ASP p5 8/24 LAN; 20/56 unverified; empty Combo not 0 | **SOURCE_EDIT_APPLIED**, PDF/HTML gate pending |
| B-005 (P2) | Preserve established phrasing unless evidence-backed benefit; no global rewriting | **DEFERRED_NONBLOCKING** |
| B-006 (P2) | Preserve established phrasing unless evidence-backed benefit; no global rewriting | **DEFERRED_NONBLOCKING** |
| B-007 (P1) | ASP p7 6 570+10 380=16 950; 2x305=610 m synthetic | **SOURCE_EDIT_APPLIED**, PDF/HTML gate pending |
| B-008 (P2) | Preserve established phrasing unless evidence-backed benefit; no global rewriting | **DEFERRED_NONBLOCKING** |
| B-009 (P2) | Preserve established phrasing unless evidence-backed benefit; no global rewriting | **DEFERRED_NONBLOCKING** |
| B-010 (P1) | ASP p11 specific SEO category/filter question | **SOURCE_EDIT_APPLIED**, PDF/HTML gate pending |
| B-011 (P1) | ASP p11 value/items mismatch described narrowly | **SOURCE_EDIT_APPLIED**, PDF/HTML gate pending |
| B-012 (P2) | Preserve established phrasing unless evidence-backed benefit; no global rewriting | **DEFERRED_NONBLOCKING** |
| B-013 (P2) | Preserve established phrasing unless evidence-backed benefit; no global rewriting | **DEFERRED_NONBLOCKING** |
| B-014 (P1) | NG p5 nonbreaking dBm units; visual overflow must be checked | **SOURCE_EDIT_APPLIED**, PDF/HTML gate pending |
| B-015 (P2) | Preserve established phrasing unless evidence-backed benefit; no global rewriting | **DEFERRED_NONBLOCKING** |
| B-016 (P1) | NG p5 automatic check may detect discrepancies | **SOURCE_EDIT_APPLIED**, PDF/HTML gate pending |
| B-017 (P1) | NG p6 t=E/P theoretical pre-figure label | **SOURCE_EDIT_APPLIED**, PDF/HTML gate pending |
| B-018 (P2) | Preserve established phrasing unless evidence-backed benefit; no global rewriting | **DEFERRED_NONBLOCKING** |
| B-019 (P2) | Preserve established phrasing unless evidence-backed benefit; no global rewriting | **DEFERRED_NONBLOCKING** |
| B-020 (P2) | Preserve established phrasing unless evidence-backed benefit; no global rewriting | **DEFERRED_NONBLOCKING** |
| B-021 (P1) | NG p15 08.10 secondary reading separated from 09.10 PDF | **SOURCE_EDIT_APPLIED**, PDF/HTML gate pending |

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
