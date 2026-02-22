# Project State

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-02-22)

**Core value:** Workflow enforcement that turns quality data capture into operational discipline -- extended with structured knowledge that guides investigators, inspectors, and quality engineers
**Current focus:** v2.0 Quality Intelligence Platform -- Phase 22 DEFERRED, Phase 23 preflight package complete, discuss/plan/execute sequence ready

## Current Position

Phase: 23 READY -- Platform Governance, Documentation, and Deployment
Plan: 00 of TBD
Status: Phase 23 preflight completed -- assumptions/context/research/verification package authored and planning artifacts reconciled for discuss-phase startup.
Last activity: 2026-02-22 -- Phase 23 deep-dive prep completed (phase packet authored, planning/codebase drift refresh)

Progress: [############        ] 57% (v2.0)

## Milestones

- **v2.0 Quality Intelligence Platform** -- ACTIVE (Phase 18 COMPLETE, Phase 19 COMPLETE, Phase 20 COMPLETE, Phase 21 COMPLETE, Phase 21.1 COMPLETE -- migration 130 deployed, taxonomy v3 cleanup verified, planning closeout done)
- v1.1 NCR Disposition Operationalization -- **SHIPPED 2026-02-17** (GO WITH ACCEPTED WARNINGS). 6 phases, 25 plans, 57 requirements.
- v1.0 Quality System Backend -- **SHIPPED 2026-02-15**. 11 phases, 41 plans + 3 deferred.

## Deployment Status

| Environment | Server | Database | Status |
|-------------|--------|----------|--------|
| Dev | sql-sf-quality-0b1f-dev | sqldb-quality-core-dev | LIVE (v2.0 Phase 21.1 COMPLETE, migrations 125-130 deployed, 1894 knowledge rows preserved, 82 active leaf codes, 12 categories, 3 new codes, EQUIP/CONTAM inactive, AIAG-VDA severity rebaselined) |
| Prod | sql-sf-quality-0b1f-dev | sqldb-quality-core-prod | LIVE (v1.0, v1.1 upgrade ready) |

## Accumulated Context

### Roadmap Evolution
- Phase 21.1 inserted after Phase 21: Defect taxonomy v3 migration (URGENT)
- Phase 22 DEFERRED (2026-02-21): Schema still evolving, no API/app consumers, role architecture not locked. Analytics views would create column dependencies that break on schema changes. SEC-01 security grants are handled inline in Phase 23 governance closure. See `22-DEFERRAL.md`.
- Phase 23 preflight package completed (2026-02-22): assumptions locked, context/research expanded, verification checklist established, planning/codebase staleness reconciled.

### Carried Forward
1. Phase 7 Plans 02-04 remain open (optimization/testing backlog).
2. Populate client data sections when available (BACKFILL-01/02, TEMPLATE-01).
3. v1.1 accepted warnings: PITR rehearsal deferred to pre-cutover window.

### v2.0 Specific
4. Schema DDL 125 deployed to dev and verified (92/92 checks passing). No longer pending.
5. E-coat FINAL promoted to migration 126a (Plan 01 complete). Dimension pre-reqs, pre-flight, 6 MOTHER_NATURE corrections, 6 NODETECT retrofits included. Deployed to dev.
6. Powder FINAL promoted to migration 126b (Plan 02 complete). 23 NODETECT + 7 SYSTEMIC retrofits included. Deployed to dev.
7. Liquid FINAL synthesized from 2 draft files (1740 lines, ~733 rows). Column remapping complete. Ready for migration promotion in Plan 02.
8. IsVerified governance flag -- DECIDED: include in DDL (IsVerified, VerifiedBy, VerifiedDate on all 9 tables). ContentSource provenance column also added. See 18-ASSUMPTIONS-FINAL.md S3a.
9. 88% historical bug rate in deploy scaffolding -- write verify artifacts AFTER migration SQL is finalized.
10. Research-phase guidance updated: Phase 23 should run discuss-phase with explicit cross-repo artifact review; no skip shortcuts for this phase.

### Phase 19 Assumptions & Governance Decisions (locked 2026-02-18)
11. Content audit matrix complete: 41 codes audited across 9 tables. See `19-CONTENT-QUALITY-AUDIT-MATRIX.md`.
12. Missing NODETECT rows: 29 total (6 e-coat + 23 powder). All must be retrofitted in 126a/126b.
13. SYSTEMIC candidates: exactly 7 powder codes (CURE-GELTIME, CURE-UNDER, EQUIP-CALOUT, EQUIP-CONVEYOR, EQUIP-FILTER, THICK-FARADAY, THICK-LOW).
14. MOTHER_NATURE corrections: 6 e-coat data-row occurrences only. Powder has zero data-row uses.
15. Full 9-table coverage gaps: 7 codes (2 e-coat GEN, 5 powder) missing ConfusionPair. ACCEPTED as exceptions.
16. **GOV-DECISION-01 (Coverage):** Core8 is hard gate for all 41 codes. ConfusionPair is conditional advisory. V02A = 8-table mandatory, V02B = exact 7-code ConfusionPair exception allowlist (drift in either direction fails).
17. **GOV-DECISION-02 (Naming):** No -PW- infix in Phase 19. No mixed-style renaming for retrofit rows. Governance reconciliation deferred to Phase 20 harmonization.
18. **GOV-DECISION-03 (Section 1):** Strip dbo.DefectType.Description MERGE from 126a/126b. Knowledge tables + dimension pre-reqs only. Description updates ship separately if needed.

### Key v2.0 Decisions (deployed + verified on dev)
- 9-table model (not 8) -- matches FINALs, preserves StandardReference semantics
- String code FKs for knowledge -- no env dependency, human-readable seed SQL
- Advisory SP pattern -- companion to gate SPs, not embedded
- Universal/line-specific row layering (NULL = universal)
- New `analytics` schema for cross-process views
- Code-family-based universal ownership: 126a owns ADHES/PRETR/CONTAM/GEN universals, 126b owns THICK/CURE/EQUIP, 126c (Phase 20) owns SURF/COLOR
- IsVerified + VerifiedBy + VerifiedDate columns on all 9 knowledge tables as optional tracking metadata (not gates or blockers)
- ContentSource provenance column (CLAUDE, CHATGPT, QE_AUTHORED, PRODUCTION_DATA) on all 9 knowledge tables as metadata
- IshikawaCategoryCode CHECK uses ENVIRONMENT (not MOTHER_NATURE) -- dimension table update in Phase 19 pre-requisite
- CauseLevelCode CHECK uses 4 values (ROOT, CONTRIBUTING, NODETECT, SYSTEMIC) -- dbo.CauseLevel expansion in Phase 19 pre-requisite
- Filtered indexes on IsActive=1 for all 9 knowledge tables (net-new, not in draft DDL)
- NODETECT/SYSTEMIC cause-level semantics: CauseLevelCode=ROOT for both patterns in Phase 19 (not native NODETECT/SYSTEMIC values)
- CP- prefix dual-use (ConfusionPair + ControlPoint) retained -- no XP rename in Phase 19

### Phase 19 Plan 01 Execution Notes (2026-02-18)
19. Content-first authoring workflow validated: drafted 36 retrofit statements in markdown, locked, then generated SQL. Reusable pattern for future phases.
20. CreatedBy column on knowledge tables is INT NULL (not NVARCHAR). Plan specified string value; corrected to NULL in migration. CauseLevel.CreatedBy is NVARCHAR -- string values valid there.
21. 126a migration is 1131 lines, covers 18 e-coat codes across all 9 knowledge tables. Static validation passed (0 violations).
22. Retrofit content draft (19-RETROFIT-CONTENT-DRAFT.md) is LOCKED and shared between Plan 01 (126a) and Plan 02 (126b).

### Phase 19 Plan 02 Execution Notes (2026-02-18)
23. dbo.IshikawaCategory uses CategoryCode/CategoryName (not IshikawaCategoryCode). Fixed in 126a Section 0 during deploy.
24. dbo.CauseLevel has only 5 columns (CauseLevelId, CauseLevelCode, CauseLevelName, Description, SortOrder). No IsActive, CreatedBy, or audit columns. Fixed in 126a Section 0.
25. CauseDescription is NVARCHAR(500). 4 of 7 SYSTEMIC retrofit descriptions exceeded limit (532, 576, 519, 504 chars). Trimmed to fit.
26. No Apply-Phase18/19 deploy script existed. Created Apply-Phase19.ps1 following Phase 16 pattern with spot-check stage.
27. Both 126a and 126b deployed to dev: 1103 total knowledge rows, 268 RootCause (incl 29 NODETECT + 7 SYSTEMIC), 0 MOTHER_NATURE. Idempotency verified.

### Phase 19 Plan 03 Execution Notes (2026-02-18)
28. Verify-Phase19.sql already existed from Plan 02 scaffolding. Updated with prerequisite guards (PG-01/02/03), V06 fix (knowledge table text fields instead of DefectType.Description), and header/completion message updates.
29. SQL Server `RowCount` is a reserved keyword. V01 failed on first run with syntax error. Fixed by renaming all `AS RowCount` aliases to `AS Cnt` throughout script (V01, V07, V08, V09).
30. V05 ConfusionPair bidirectionality found 6 one-way pairs (all e-coat source data authored unidirectionally). Changed V05 from BLOCKER (THROW) to advisory (WARN + PRINT) since ConfusionPair is conditional per GOV-01.
31. Apply-Phase19.ps1 updated with Stage 4 (verify execution) and -SkipVerify parameter. PowerShell `$sender`/`$event` automatic variable conflict fixed by renaming to `$snd`/`$evt`.
32. All V01-V13 checks pass against dev (20 GO-separated batches, 2.2s). Phase 19 seed data CERTIFIED.

### Phase 18 Execution Notes
11. Migration 125 authored and static-validated (579 lines, 9 tables, 15 CHECK constraints, 9 filtered indexes, 9 audit triggers)
12. Migration 125 deployed to dev and verified with 92/92 checks passing (Verify-Phase18.sql)
13. RLS interaction discovered: audit.AuditLog has PlantIsolationPolicy FILTER on PlantId; knowledge triggers write PlantId=NULL making audit rows invisible to non-admin SELECTs. Documented for future phases.
14. Trigger naming pattern is trg_[TableName]_Audit (generated by usp_CreateAuditTrigger), audit.AuditLog uses Action column (not Operation), RecordId is INT.
15. SC-2 DML verification uses 2-layer approach (trigger existence + DML success) due to RLS filtering on audit.AuditLog.

### Phase 20 Assumptions Review (2026-02-18)
33. **Architectural intent established:** Universal knowledge is the platform; process-specific knowledge is the overlay. Universal rows must be written process-agnostically -- they serve ALL process families, not just the first one that authors them.
34. Phase 20 is canonical universal owner for all 27 SURF/COLOR codes. No prior migration provides universal rows for these codes.
35. Zero "liquid-only" codes -- all 27 are bridge-mapped to multiple process families (POWDER, LIQUID, and some to ECOAT).
36. 5 of 9 knowledge tables are universal-only by design (TestMethod, DispositionGuidance, ContainmentGuidance, StandardReference, ConfusionPair).
37. Migration 126d forward-fixes 6 one-way e-coat confusion pairs -- V05 becomes BLOCKER for all 68 codes.
38. Synthesis spec corrected: MOTHER_NATURE to ENVIRONMENT, SYMPTOM to ROOT/CONTRIBUTING, stale deployment status updated, "liquid-only" claims removed.
39. Containment staging draft corrected: CTN to CG prefix, SortOrder normalization deferred to promotion.
40. Stale FINAL source files flagged with SUPERSEDED headers (e-coat, powder, master integration plan, Codex spec).
41. GOV-05 locked: descriptions included in 126c (fresh synthesis, not retrofit).
42. GOV-07 revised: ContentSource=NULL (matches deployed 126a/126b pattern).
43. GOV-08 locked: 5 universal-only tables, 4 tables with process-specific overlays.
44. Harmonization audit must include universal content language review of 126a/126b for process-specific language leakage.
45. Verification framework designed as reusable Verify-KnowledgeLayer.sql, not phase-scoped.

### Phase 20 Plan 01 Execution Notes (2026-02-18)
46. 126c FINAL SQL synthesized: 1740 lines, ~733 rows across 8 knowledge tables (Section 6 reserved for 127 per GOV-04).
47. Content synthesis from dual AI drafts (Claude + ChatGPT) with complete column remapping (14+ transformations). Every row validated against deployed schema.
48. 7 SYSTEMIC candidates identified for liquid: ORANGE, FISHEYE, SEED, DIRT, SPITMARK, STRIPE, COLOR-MISMATCH. All use METHOD/ROOT/MEDIUM/SortOrder=80.
49. 28 bidirectional confusion pairs (56 rows) from Codex Section 26 minimum network. Surface clusters + cross-domain + color pairs all covered.
50. Batched MERGE blocks used in Sections 3-5 for efficiency (grouping multiple codes per block). Sections 2, 8, 9, 10 use per-code MERGEs matching 126a pattern.
51. 8 LIQUID-specific TestMethod rows and 2 LIQUID-specific StandardReference rows for CQI-12 S6 coverage. All other TestMethod/StandardReference/DispositionGuidance/ConfusionPair rows are universal-only per GOV-08.
52. Execution required 4 continuation sessions due to output token limits on the 1740-line file. No data loss or inconsistency -- each session resumed from exact stopping point.

### Phase 20 Plan 02 Execution Notes (2026-02-18)
53. 126c promoted as 1:1 byte-for-byte copy from FINAL (SHA256 verified). No transformation step = no transformation bugs.
54. 126d authored with 6 individual MERGE blocks for reverse confusion pairs. All e-coat bidirectionality gaps closed.
55. 127 Section A promoted with SortOrder normalization (1,2,3,4 -> 10,20,30,40) and ContentSource/IsVerified columns added.
56. Apply-Phase20.ps1 authored following Phase 19 4-stage pattern. Includes grand-total spot-check across all 68 codes.
57. Deployment to dev: 785 SURF/COLOR knowledge rows + 99 containment rows. 1894 total across all 68 codes. Zero MOTHER_NATURE. 27 NODETECT. 57 bidirectional confusion pairs.
58. Idempotent re-run verified: identical row counts, no errors, no duplicates.
59. Static validation: 0 violations across all 130 migration files.

### Phase 20 Plan 03 Execution Notes (2026-02-18)
60. Verify-Phase20.sql authored as reusable parameterized V01-V14 framework (~650 lines, 22 GO-separated batches). #VerifyCodes populated from dbo.DefectTypeLineType bridge table (not hardcoded).
61. V05 bidirectionality upgraded from advisory (WARN) to BLOCKER (THROW) -- after 126d, zero legacy exceptions.
62. V14 string domain validation added (NEW): DispositionCode (11 values), ContainmentCode (10 values), ProcessZoneCode (7 values + NULL), MinSeverity/MaxSeverity (1-10 range).
63. V02B exception allowlist expanded from 7 to 8 codes: SURF-HIGLOSS added (genuinely no confusion partner -- opposite of LOWGLOSS).
64. All V01-V14 PASS for 68 codes. Row counts: 480 RC, 302 INV, 129 TM, 169 DG, 191 CG, 114 CP, 225 PC, 105 SR, 179 CTRL = 1894 total.
65. Universal language review: 30-row sample from 126a/126b universal rows. 90% CLEAN, 10% REVIEW, 0% FIX. 1 forward-fix candidate: RC-CURMEK-CONTAM.
66. Content maintenance: migration-based UPDATE for IsVerified flips and content corrections. Forward-fix migration pattern is the update mechanism.
67. Naming convention inventory: -EC- (e-coat), no infix (powder legacy), -LQ- (liquid). Formally documented but not retroactively changed. Phase 23 PLAT-02 locks convention.

### Phase 21 Assumptions (locked 2026-02-18)
68. Assumptions reviewed, redlined, and locked in `21-ASSUMPTIONS-FINAL.md` (16 sections, 11 decisions, 13 verification checks).
69. Migration packaging: 128 (retrieval layer: 9 views + advisory SP + queue view ALTER) + 129 (CHECK expansion on RootCause.HypothesisSource + pre-population SP).
70. @CallerAzureOid parameter on advisory SP: required when @NcrId is used (RLS session context for NCR lookup).
71. IsVerified is NOT a gating filter on advisory SP -- returns all IsActive=1 rows. IsVerified is optional tracking metadata, not a blocker.
72. Knowledge views are UNFILTERED (include IsActive=0) -- serve analytics (Phase 22) and admin (Phase 23) use cases.
73. Pre-population SP (`quality.usp_PrePopulateRootCauses`) returns data only, does NOT INSERT -- app supplies CorrectiveActionId + PlantId at INSERT time.
74. HypothesisSource CHECK expansion: add `N'DefectTypeRootCause'` to existing allowlist on `dbo.RootCause`.
75. Gate SP knowledge documentation is a markdown artifact only -- no code changes to any of the 18 gate SPs.
76. GATE-15 (`quality.usp_CreateCAPA`) is the natural INTEL-05 trigger point for root cause pre-population.

### Phase 21 Plan 02 Execution Notes (2026-02-18)
77. Migration 129 authored: 148 lines. Part 1: CHECK expansion (idempotency guard on `definition NOT LIKE`). Part 2: `quality.usp_PrePopulateRootCauses` with INNER JOIN to IshikawaCategory (CategoryCode) and CauseLevel (CauseLevelCode).
78. Pre-population SP resolves code-based FKs: IshikawaCategoryCode -> IshikawaCategoryId, CauseLevelCode -> CauseLevelId. @RootCauseTypeId passed through (D21-11).
79. Gate knowledge mapping document (21-GATE-KNOWLEDGE-MAPPING.md): all 18 gates mapped with exact @Sections CSV strings, companion advisory pattern, INTEL-05 integration at GATE-15.
80. Static SQL validation: 0 violations across 132 migration files. No deviations from plan.

### Phase 21 Plan 03 Execution Notes (2026-02-19)
81. Migration 129 originally used temporal SYSTEM_VERSIONING OFF/ON for CHECK constraint expansion. RLS PlantIsolationPolicy blocked ALTER TABLE SET SYSTEM_VERSIONING on dbo.RootCause. Fixed: CHECK constraint DROP/ADD does NOT require SYSTEM_VERSIONING OFF (only column changes do). Removed unnecessary temporal choreography.
82. Apply-Phase21.ps1 authored: 4-stage deploy (static rules, migrations 128+129, spot checks, verify). Spot checks: 9 views, 2 SPs, CHECK constraint, queue view columns.
83. Verify-Phase21.sql authored: V01-V13 (16 GO-separated batches). V06 graceful SKIP for zero-NCR dev. V07 TRY/CATCH for conflict THROW. No RowCount alias (uses Cnt).
84. Deployment results: Stage 1 static rules 0 violations (132 files). Stage 2 migrations 128+129 deployed (0.3s). Stage 3 spot checks all pass. Stage 4 V01-V13: 12 PASS, 0 FAIL, 1 SKIP (V06 no NCR data).
85. Idempotent re-run verified: identical results, no errors (4.8s total).
86. INTEL-01 through INTEL-05 all marked COMPLETE in REQUIREMENTS.md.
87. Knowledge retrieval layer test data: DefectTypeId 62 returned 8 RootCauses rows, V04 confirmed LineTypeId=1 sorts first (process-specific precedence), V08 severity filter returned 2 rows, V13 all rows have HypothesisSource=DefectTypeRootCause.

### Phase 21.1 Plan 01 Execution Notes (2026-02-20)
88. Source SQL had incorrect column name `RelatedDefectTypeId` -- actual deployed schema uses `ConfusedWithDefectTypeId` on `dbo.DefectTypeConfusionPair`. Fixed in both migration and verification SQL.
89. Junction table remap (DefectTypeProcessFamily, DefectTypeLineType) caused UNIQUE constraint violations when multiple merge sources mapped to the same survivor. Fixed: DELETE all merge-source junction rows instead of UPDATE (survivors already have correct mappings).
90. ConfusionPair remap requires NOCHECK/CHECK choreography for `CK_DefectTypeConfusionPair_NotSelf` during intermediate state where both sides of a pair may merge to the same target.
91. Migration 130 deployed to dev: 82 active leaf codes (from 112+), 12 active categories, 3 new codes (SURF-OVERSPRAY, SURF-MASKFAIL, THICK-PLUG). EQUIP/CONTAM categories deactivated. All AIAG-VDA severity values rebaselined.
92. Verification passed: no merge-source FK references detected. WARNING about missing merge-source codes is benign (deactivate-only codes not in merge map).
93. Static SQL validation: 0 violations across 133 migration files.

## Session Continuity

Last session date: 2026-02-22
Stopped at: Phase 23 preflight complete; ready to execute assumptions and discuss workflow.
Resume point: `/gsd:list-assumptions 23` -> `/gsd:discuss-phase 23` -> `/gsd:plan-phase 23`

---
*Updated: 2026-02-22 -- Phase 23 preflight package complete; ready for list-assumptions/discuss/plan/execute workflow.*
