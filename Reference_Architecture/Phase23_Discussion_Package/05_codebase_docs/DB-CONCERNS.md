# Codebase Concerns

**Analysis Date:** 2026-02-22 (updated for Phase 23 preflight)

## Tech Debt

**Deploy Scaffolding Quality Gap (Historical 88% Bug Rate):**
- Issue: Deployment scripts, verify queries, and smoke tests have far higher bug rates than migration SQL itself
- Files: `database/deploy/Apply-Phase*.ps1`, `database/deploy/Verify-Phase*.sql`, `database/deploy/Smoke-Phase*.sql`
- Impact: 26 deployment bugs in v1.0: 23 (88%) in scaffolding, only 3 (12%) in migration SQL. Bugs include wrong column names, hardcoded OIDs, references to empty client tables, PowerShell batch splitter edge cases
- Fix approach: Write verify/smoke queries AFTER migration SQL is finalized with direct schema reference, not from plan context. Use graceful SKIP pattern for smoke tests on empty tables. Validate PowerShell with `-WhatIf` before live execution
- Evidence: `.planning/research/PITFALLS.md` lines 239-254, project MEMORY.md pattern documentation

**Migration Immutability Enforcement with Forward-Fix Pattern:**
- Issue: Migrations 001-086 treated as immutable history, but bugs in utility SPs (like `usp_CreateAuditTrigger`) require fixes
- Files: `database/migrations/086a_fix_audit_trigger_rowversion.sql` (forward-fix example), `database/migrations/004_audit_trigger_utility.sql` (original)
- Impact: Cannot directly edit migration 004 to fix ROWVERSION bug. Must create forward-fix migration 086a to patch the SP. Pattern works but creates migration numbering complexity (3-digit + optional alpha suffix)
- Fix approach: Continue forward-fix pattern for utility SP bugs. Document that migrations 001-086 remain immutable per governance policy
- Current mitigation: Migration 086a successfully patched `usp_CreateAuditTrigger` to exclude ROWVERSION columns from audit triggers

**RLS Security Policy Rebuild Fragility:**
- Issue: Adding tables to RLS or altering temporal tables requires DROP/rebuild of `security.PlantIsolationPolicy` using cursor-based dynamic SQL. Single syntax error in rebuild loses all 150+ predicates
- Files: `database/migrations/079_topology_wave5_quality_rls_integration.sql` lines 40-62 and 206-260, `database/migrations/090_ncr_notes_hold_locations.sql` (RLS rebuild pattern)
- Impact: If rebuild dynamic SQL fails, all plant-scoped tables lose RLS isolation. Data leakage across plants until manually reconstructed
- Fix approach: Only one migration per phase should do full DROP/rebuild (e.g., 087 for Phase 13). Subsequent migrations in same phase use simpler `ALTER SECURITY POLICY ... ADD FILTER PREDICATE` pattern. Add verification query that asserts exact predicate count post-deploy
- Safe modification: Copy exact cursor pattern from migration 079 or 086. Test on staging database first. Add explicit predicate count verification

**Temporal ALTER Choreography for NonConformanceReport:**
- Issue: Adding columns to `quality.NonConformanceReport` (system-versioned temporal table) requires complex three-step dance per column: `SET SYSTEM_VERSIONING = OFF`, `ALTER TABLE` on both base and history tables, `SET SYSTEM_VERSIONING = ON`
- Files: `database/migrations/087_ncr_operational_columns.sql`, pattern established in `database/migrations/079_topology_wave5_quality_rls_integration.sql` lines 76-84
- Impact: Each column addition creates multiple failure points. Partial migration leaves table unversioned. Security policy rebuild fails if temporal versioning is down
- Fix approach: Wrap each column ALTER block in idempotent `IF NOT EXISTS (SELECT 1 FROM sys.columns ...)` guard. Add explicit SYSTEM_VERSIONING state check after each block. Keep security policy rebuild as LAST operation in migration
- Test coverage: Run migration on staging first. Verify `temporal_type_desc = 'SYSTEM_VERSIONED_TEMPORAL_TABLE'` post-deploy

**NCR Temporal ALTER for Incoming Substrate FK (v2.0 Phase 24):**
- Issue: Migration 127 Section C adds `IncomingSubstrateDefectReasonId INT NULL` FK to `quality.NonConformanceReport` — a system-versioned temporal table. Requires the same three-step choreography: versioning off, ALTER both base + history tables, versioning on. If security policy is active, must also handle DROP/rebuild
- Files: `quality.NonConformanceReport` (migration 087), existing pattern in `database/migrations/087_ncr_operational_columns.sql`
- Impact: Same risks as existing temporal ALTER concern — partial migration leaves table unversioned, security policy rebuild required, FK target (`dbo.IncomingSubstrateDefectReason`) must exist before ALTER
- Fix approach: Follow established migration 087 pattern exactly. IncomingSubstrateDefectReason CREATE TABLE must precede the ALTER. Wrap in `IF NOT EXISTS (SELECT 1 FROM sys.columns ...)` guard for idempotency. Verify `temporal_type_desc = 'SYSTEM_VERSIONED_TEMPORAL_TABLE'` post-deploy
- Staging: SQL already authored at `docs/defect-knowledge-expansion/Defect Knowledge Expansion/LIQUID/127_liquid_paint_containment_and_incoming_substrate.sql` Section C — needs validation against current security policy rebuild pattern before promotion to migration chain

**Legacy NCR Data Compatibility After Schema Split:**
- Issue: Existing NCRs in production have disposition on header (`DispositionCodeId`). After migration 088, gate SPs expect child `quality.NcrDisposition` rows for quantity reconciliation
- Files: `database/migrations/088_ncr_split_disposition.sql`, gate SPs in migrations 111-118
- Impact: Re-opened legacy NCRs appear "unbalanced" (zero disposition lines vs nonzero header quantity). Gate closure blocked. Queue views show false-positive reconciliation warnings
- Fix approach: Add legacy compatibility logic in gate SPs: if NCR created before Phase 13 deploy AND no disposition lines exist, fall back to header fields. Use LEFT JOIN with COALESCE in views, not INNER JOIN
- Residual risk: Identified as RR-002 in decision closeout package

**Client Data Population Deferred:**
- Issue: `Import-Phase11-ClientData.sql` has 7 placeholder TODO sections for Equipment, Supplier, ProductionLine, LineStage mapping, DefectType override data
- Files: `database/deploy/Import-Phase11-ClientData.sql` lines 65, 84, 116, 143, 167, 190
- Impact: Zero rows in Equipment and Supplier tables. Smoke tests must gracefully SKIP. FKs remain unpopulated. BACKFILL-01/02 deferred
- Fix approach: Populate sections incrementally as client data becomes available. Script executes cleanly as no-op when empty (by design)
- Safe modification: File is template with RLS disable/enable wrapper. Add actual INSERT/UPDATE statements in TODO sections when data available

**NODETECT/SYSTEMIC Root Cause Gaps Across Both FINALs (v2.0) -- RESOLVED Phase 19:**
- Status: RESOLVED -- All 29 NODETECT rows (6 e-coat + 23 powder) and 7 SYSTEMIC rows deployed in 126a/126b. 6 MOTHER_NATURE corrections applied. V01 row counts confirmed, V07 confirms zero MOTHER_NATURE remaining.
- Evidence: 19-VERIFICATION.md (V01, V07), 19-02-SUMMARY.md, 19-03-SUMMARY.md

**NODETECT/SYSTEMIC CauseLevelCode Semantic Limitation (v2.0):**
- Issue: All knowledge seed migrations (126a, 126b, 126c) use CauseLevelCode=ROOT for both NODETECT and SYSTEMIC rows. The dbo.CauseLevel table has native NODETECT and SYSTEMIC values (added in 126a preamble), but they are not used for knowledge table rows -- only ROOT is used. This means NODETECT/SYSTEMIC rows are indistinguishable from regular root causes by CauseLevelCode alone; identification depends on IshikawaCategoryCode (MEASUREMENT for NODETECT, METHOD for SYSTEMIC) and naming convention (RC-*-NODETECT, RC-*-SYSTEMIC suffix)
- Files: `database/migrations/126a_defect_knowledge_seed_ecoat.sql`, `database/migrations/126b_defect_knowledge_seed_powder.sql`, `database/migrations/126c_defect_knowledge_seed_liquid.sql`
- Impact: Queries filtering for "all NODETECT root causes" must use naming pattern match or IshikawaCategory, not CauseLevelCode. Future taxonomy hardening could migrate to native NODETECT/SYSTEMIC values
- Fix approach: Deferred to Phase 23 (PLAT-05 knowledge curation). Current contract: CauseLevelCode=ROOT is locked across all 3 process families
- Evidence: 19-CONTEXT.md, 20-HARMONIZATION-AUDIT.md (consistent across all 3 seed migrations)

**E-coat/Powder Verification Depth Gap (v2.0) -- RESOLVED Phase 19:**
- Status: RESOLVED -- Verify-Phase19.sql implements unified V01-V13 for both e-coat and powder (41 codes). V02A (8-table mandatory) + V02B (7-code ConfusionPair allowlist) enforced. V12 (line-type leakage) + V13 (scope leakage) added and passing. All checks pass against dev (20 batches, 2.2s).
- Evidence: 19-VERIFICATION.md (all V01-V13 PASS), `database/deploy/Verify-Phase19.sql`

**ConfusionPair One-Way Pairs Advisory (v2.0) -- RESOLVED Phase 20:**
- Status: RESOLVED -- Migration 126d deployed 6 reverse confusion pair rows. V05 bidirectionality is now a BLOCKER (THROW) in Verify-Phase20.sql. All 114 confusion pair rows (57 bidirectional pairs) pass V05 with zero legacy exceptions.
- Evidence: `database/migrations/126d_confusion_pair_bidirectional_fix.sql`, `database/deploy/Verify-Phase20.sql` (V05 BLOCKER), 20-VERIFICATION.md

**Cross-FINAL Cohesion Not Validated (v2.0) -- RESOLVED Phase 20:**
- Status: RESOLVED -- Phase 20 harmonization audit sampled 30 universal rows (20 RootCause + 10 InvestigationStep) from 126a/126b codes. Results: 90% CLEAN (genuinely universal), 10% REVIEW (borderline but acceptable), 0% FIX (no blocking process-specific language). One forward-fix candidate identified: RC-CURMEK-CONTAM ("Powder chemistry" -> "Coating chemistry") -- deferred to Phase 23 (not blocking). Verify-Phase20.sql provides permanent reusable cross-process verification (V01-V14).
- Evidence: 20-HARMONIZATION-AUDIT.md (Section 2: Universal Content Language Review), 20-VERIFICATION.md (V01-V14 PASS), `database/deploy/Verify-Phase20.sql`

**Universal Content Language Leakage Risk (v2.0) -- LOW RISK, MONITORED:**
- Status: Assessed in Phase 20 harmonization audit. 30-row sample found 90% CLEAN / 10% REVIEW / 0% FIX. The 3 REVIEW items: (1) RC-CUREOVER-NODETECT mentions "powder" -- borderline, content still functionally correct; (2) RC-THKVAR-RECIPSPD references "reciprocator" -- acceptable, used across spray processes; (3) RC-CURMEK-CONTAM mentions "Powder chemistry" -- forward-fix candidate ("Coating chemistry"), deferred to Phase 23.
- Files: `database/migrations/126a_defect_knowledge_seed_ecoat.sql`, `database/migrations/126b_defect_knowledge_seed_powder.sql`
- Impact: Low. No universal rows contain blocking process-specific language. When ANODIZE onboards, the 3 REVIEW items should be reviewed but none would cause incorrect guidance.
- Fix approach: Forward-fix migration for RC-CURMEK-CONTAM in Phase 23 knowledge curation. Monitor remaining 2 REVIEW items during ANODIZE onboarding.
- Evidence: 20-HARMONIZATION-AUDIT.md (Section 2: Language Review Summary)

**Stale FINAL Source Files in docs/ (v2.0):**
- Issue: The e-coat and powder FINAL files in `docs/defect-knowledge-expansion/.../FINAL/` predate Phase 19 deployment. They are missing ContentSource/IsVerified columns, NODETECT/SYSTEMIC retrofits, and contain stale data (MOTHER_NATURE values in e-coat FINAL). The Codex master integration plan recommends an 8-table model that was overruled by the deployed 9-table schema.
- Files: `126_defect_knowledge_seed_ecoat_FINAL.sql`, `126_defect_knowledge_seed_powder_FINAL.sql`, `126_defect_knowledge_master_integration_plan_codex.md`, `126_liquid_defect_knowledge_final_synthesis_plan_codex.md`
- Impact: Any agent or implementer reading these files without checking deployed migrations will get stale or contradictory guidance
- Fix approach: SUPERSEDED headers added to all affected files (done 2026-02-18). Files point to deployed migrations as authority. The deployed 126a/126b are the pattern references, not the FINAL docs.
- Evidence: File audit conducted 2026-02-18, headers added to e-coat FINAL, powder FINAL, master integration plan, Codex spec

## Known Bugs

**Zero Active Plants in Dev:**
- Symptoms: `dbo.Plant` has 0 active rows in dev environment
- Files: Seed data in `database/migrations/009_seed_plants.sql`
- Trigger: Verify/smoke checks that depend on plant-scoped seed data
- Workaround: Smoke tests use graceful SKIP when no plants exist. Not a production issue (prod has plant data)
- Evidence: Project MEMORY.md deployment patterns

**Zero Escalation Rules in Dev:**
- Symptoms: `workflow.EscalationRule` has 0 rows in dev
- Files: Seed data in workflow schema
- Trigger: Verify/smoke checks referencing escalation data
- Workaround: Checks gracefully SKIP on zero-escalation-rule condition
- Evidence: Project MEMORY.md deployment patterns

## Security Considerations

**RLS Predicate Duplication on Migration Re-Run:**
- Risk: Migrations that save/drop/rebuild security policy AND hardcode new table predicates will duplicate those predicates on re-run (saved from previous run + hardcoded again)
- Files: `database/migrations/090_ncr_notes_hold_locations.sql` (example fix)
- Current mitigation: DELETE the new tables from `#SecurityPredicates` before cursor loop to prevent duplication
- Recommendations: All RLS rebuild migrations should use this pattern. Add static verification query that detects duplicate predicates post-deploy
- Evidence: Project MEMORY.md: "RLS policy rebuild idempotency" pattern

**SP-Only Mutation Security Model Enforced (Phase 16 COMPLETE):**
- Status: RESOLVED -- Migration 123 creates 5 DB roles with scoped EXECUTE/SELECT grants; TC-CONTRACT-001 triple-asserted (migration, verify, smoke)
- Files: `database/migrations/123_security_roles_grants.sql`, `database/deploy/Verify-Phase17.sql` F04a/b/c, `database/deploy/Smoke-Phase17.sql` SM-05a/b
- Evidence: gate-report-SC2.md confirms TC-CONTRACT-001 structural coverage

**Dual-Path Authorization with Legacy RoleId Fallback:**
- Risk: Permission-first authorization with legacy RoleId fallback creates deprecation surface. Fallback path may mask permission config gaps
- Files: `database/migrations/098_harden_workflow_transition_sp.sql` lines 126-182
- Current mitigation: Dual-path implementation logs deprecation warning when fallback is used. Plant scope mandatory in both paths
- Scaling path: Monitor fallback usage. Plan migration to permission-only once fallback usage drops to zero

**Knowledge Content Maintenance (v2.0):**
- Note: Knowledge seed data is advisory reference content authored by the project owner. Content corrections and updates follow the forward-fix migration pattern
- Files: All three FINAL seed files (e-coat, powder, liquid)
- Schema: `IsVerified`, `VerifiedBy`, `VerifiedDate`, and `ContentSource` columns exist on all 9 knowledge tables as optional tracking metadata (not gates or blockers)
- Maintenance: Content corrections use forward-fix migrations (e.g., 126e_fix_description_typo.sql). IsVerified can be flipped via migration UPDATE when the owner marks rows as reviewed

**Knowledge Maintenance Workflow (v2.0):**
- Note: Post-deploy content corrections (typos, likelihood updates, IsVerified flips) use the forward-fix migration pattern
- Files: All knowledge seed migrations (126a, 126b, 126c, 126d, 127)
- Approach: Forward-fix migration (e.g., 126e_fix_description_typo.sql) for any content changes. No admin SP required -- migrations are the update mechanism
- Priority: Low -- forward-fix pattern is established and sufficient

**ConfusionPair Exception Allowlist Drift (v2.0):**
- Risk: V02B ConfusionPair exception allowlist was 8 codes prior to Phase 21.1 taxonomy cleanup. After migration 130, some codes (GEN-UNDEF, EQUIP-FILTER, EQUIP-PUMP) have been deactivated or merged. The effective allowlist for active codes may have changed. If production data reveals genuine confusion patterns for remaining active exception codes, the allowlist must shrink (pairs added) and Verify-Phase20.sql re-run
- Files: `database/deploy/Verify-Phase20.sql` (V02B allowlist), `database/deploy/Verify-Migration130.sql`
- Impact: Low -- taxonomy v3 cleanup reduces the active code surface, which may reduce the exception allowlist naturally
- Fix approach: Verify V02B allowlist against post-migration-130 active codes in Phase 23 governance closure. Monitor production NCR data for confusion patterns involving remaining exception codes
- Evidence: 20-HARMONIZATION-AUDIT.md (Section 5.2: Exception Allowlist), 20-VERIFICATION.md (V02B PASS), 21.1-01-SUMMARY.md (migration 130 deployed)

**Dimension Table Alignment for Knowledge Layer (v2.0) -- RESOLVED Phase 19:**
- Status: RESOLVED -- 126a preamble executed dimension pre-requisites: `MOTHER_NATURE` -> `ENVIRONMENT` UPDATE on dbo.IshikawaCategory; `NODETECT` + `SYSTEMIC` added to dbo.CauseLevel. V07 confirms zero MOTHER_NATURE rows in knowledge tables. Dimension alignment is now permanent.
- Evidence: 19-VERIFICATION.md (V07), `database/migrations/126a_defect_knowledge_seed_ecoat.sql` Section 0

**Naming Convention Contract Conflict — -PW- Infix (v2.0):**
- Risk: KNOW-13 requires `-PW-` process infix for powder-specific knowledge rows, but current powder FINAL and liquid synthesis guidance use no-infix pattern. All 23 powder codes have no `-PW-` infix in existing keys
- Files: `database/migrations/126b_defect_knowledge_seed_powder.sql`, `.planning/REQUIREMENTS.md` KNOW-13
- Decision: Phase 19 defers resolution per GOV-02. No mass rename, no mixed-style for retrofit rows. Governance reconciliation planned before/with Phase 20 harmonization
- Impact: KNOW-13 remains partial until naming contract conflict is resolved. Phase 19 validated prefix patterns (RC-, INV-, etc.) via V04 natural key uniqueness but did not enforce -PW- infix
- Evidence: 19-ASSUMPTIONS-FINAL.md §4.7, 19-VERIFICATION.md (V04 PASS), GOV-02 decision

**CP- Prefix Dual-Use (v2.0):**
- Issue: `CP-` prefix is used for both ConfusionPair PairCode (e.g., CP-XH-DELAM) and ControlPoint ControlCode (e.g., CP-ADHES-CROSSHATCH-MONITOR). The two tables have independent natural keys so no collision occurs, but CP- is semantically ambiguous
- Files: `database/migrations/126a_defect_knowledge_seed_ecoat.sql`, `database/migrations/126b_defect_knowledge_seed_powder.sql`
- Decision: Retained as-is in Phase 19 per governance. No rename to XP- (ConfusionPair) considered. Tables have different key structures so collision is impossible, but code-level searches for CP- prefix will return both types
- Impact: Low -- confusion is documentary, not functional. Anyone filtering by prefix should be aware of dual-use
- Fix approach: Could rename ConfusionPair to XP- prefix in Phase 20 harmonization if desired. Not blocking
- Evidence: 19-CONTEXT.md (locked decisions), STATE.md item #71

**CQI-12 Standard Reference Specificity (v2.0):**
- Risk: Standard references cite CQI-12 generically (e.g., "Section 6" for liquid paint). Specific subsection numbers (6.1, 6.2) may not be accurately cited. Same risk for ASTM references — method qualifiers (e.g., "Method B") may not match actual standard content
- Files: DefectTypeStandardReference and DefectTypeTestMethod seed data in all FINALs
- Current mitigation: Use generic section references (e.g., `N'CQI-12 Section 6'`). Accept that specificity requires manual verification against actual standards documents
- Recommendations: Verify top standard references against physical CQI-12 and ASTM documents before production deployment. Add verification column to track which references have been manually confirmed
- Evidence: Vision document §12

## Performance Bottlenecks

**RLS Performance on Multi-Table Joins:**
- Problem: Operational queue views join multiple RLS-filtered tables (`NonConformanceReport`, `StatusHistory`, `NcrDisposition`). Each table's RLS predicate fires independently
- Files: Phase 16 views (not yet created): `quality.vw_NcrOperationalQueue`, `quality.vw_NcrDispositionBalance`, `quality.vw_NcrHoldAging`
- Cause: RLS predicates are inline table-valued functions with `EXISTS (SELECT ... FROM dbo.UserPlantAccess ...)`. Query optimizer evaluates predicate per table, not once per query
- Improvement path: Denormalize PlantId on every table (already done). Add composite covering indexes: `NonConformanceReport(PlantId, StatusCodeId, PriorityLevelId, CreatedDate)`. Profile execution plans early in Phase 16. Consider materialized snapshot table if P95 exceeds 2s SLO
- Evidence: `.planning/research/PITFALLS.md` lines 221-236, Microsoft RLS performance guidance

**Azure SQL Serverless Wake-Up Latency:**
- Problem: First connection after idle fails with "database not currently available", ~30s wake-up time
- Files: `database/deploy/Deploy-Common.ps1` Connect-QualityDb function
- Cause: Serverless tier auto-pauses after inactivity
- Improvement path: Add retry logic to Connect-QualityDb with 30s delay. Already documented in project MEMORY.md
- Current impact: Deployment scripts may fail on first attempt, succeed on retry

## Fragile Areas

**Workflow Guard Dispatch (Non-Extensible):**
- Files: `database/migrations/061_workflow_transition_sp.sql` lines 140-326 (`workflow.usp_TransitionState`)
- Why fragile: Guard types dispatched via hardcoded CASE chain: `IF @GuardType = N'SeveritySkip' ... ELSE IF @GuardType = N'ChildEntityState'`. Adding new guard type requires SP update, not just transition row seed
- Safe modification: Gate SPs should perform all validation BEFORE calling `usp_TransitionState`. New transitions should use `GuardType = NULL` or existing types only. If new guard type needed, migration must include `CREATE OR ALTER PROCEDURE usp_TransitionState` with new guard branch
- Test coverage: Add static verification query: `SELECT * FROM workflow.WorkflowTransition WHERE GuardType NOT IN (<known types>) AND GuardType IS NOT NULL` should return zero rows
- Evidence: `.planning/research/PITFALLS.md` lines 272-285

**Nested Transaction Collision Between Gate SPs and usp_TransitionState:**
- Files: Gate SPs in migrations 111-118, `workflow.usp_TransitionState` line 335
- Why fragile: Gate SP opens `BEGIN TRANSACTION`, calls `usp_TransitionState` which opens another `BEGIN TRANSACTION`. SQL Server increments `@@TRANCOUNT` to 2. If transition THROW fires, `ROLLBACK TRANSACTION` resets to 0, rolling back EVERYTHING including gate SP's writes
- Safe modification: Gate SPs should NOT open their own transaction when calling `usp_TransitionState`. Let transition SP own outermost transaction scope. Alternative: use `SAVE TRANSACTION` savepoints for partial rollback
- Test coverage: Call gate SP with guard that will fail. Verify disposition lines are/aren't committed per design intent
- Evidence: `.planning/research/PITFALLS.md` lines 76-93

**Temporal Column Nullability Must Match Between Base and History Tables:**
- Files: Migrations that add NOT NULL columns to temporal tables (e.g., `database/migrations/087_ncr_operational_columns.sql`)
- Why fragile: Adding NOT NULL column to base table requires matching NOT NULL on history table (with DEFAULT to fill existing rows). SQL Server blocks SYSTEM_VERSIONING ON if nullability mismatches
- Safe modification: When adding NOT NULL column to temporal table: (1) ADD column as NOT NULL with DEFAULT on BOTH base and history, (2) Re-enable SYSTEM_VERSIONING, (3) Optionally DROP DEFAULT from base table if not needed for future inserts
- Test coverage: Verify `temporal_type_desc = 'SYSTEM_VERSIONED_TEMPORAL_TABLE'` after column additions
- Evidence: Project MEMORY.md: "Temporal column nullability must match"

**OPENJSON Parse Errors Produce Cryptic Messages:**
- Files: Gate SPs with JSON wrapper pattern (e.g., `quality.usp_RecordNcrDisposition` planned in migration 114)
- Why fragile: `OPENJSON` returns zero rows on malformed JSON or NULL for mismatched property names (case-sensitive). Gate SP proceeds with empty/NULL TVP, creates invalid disposition lines, FK constraint fails with unhelpful error
- Safe modification: After `OPENJSON ... WITH` parsing, validate required TVP columns NOT NULL. Check row count > 0. Use error code 52001 for all parse/validation failures. Pre-compute error messages into variables (THROW concatenation limitation)
- Test coverage: Pass malformed JSON, verify graceful error with code 52001
- Evidence: `.planning/research/PITFALLS.md` lines 187-202

## Scaling Limits

**Migration Chain Length (133 Migrations):**
- Current capacity: 133 migration files (001-130, with 086a forward-fix and 126c/126d multi-suffix)
- Limit: Three-digit numbering supports 001-999. Alpha suffix (a-z) supports 26 variants per number
- Scaling path: Current naming allows ~26,000 migrations before exhaustion. Not a practical concern for this project lifecycle
- Evidence: `database/deploy/Test-SqlStaticRules.ps1`, static validation confirmed 0 violations across 133 files

**RLS Predicate Count:**
- Current capacity: ~150+ predicates across 40+ tables (4 predicates per plant-scoped table: 1 FILTER + 3 BLOCK)
- Limit: No documented SQL Server limit on predicate count, but dynamic SQL rebuild complexity increases linearly
- Scaling path: If predicate count exceeds 500, consider breaking into multiple security policies by schema. Profile rebuild time during Phase 16 deployment
- Evidence: `.planning/research/PITFALLS.md` lines 33-51

**Entra Token Expiration:**
- Current capacity: Deployment uses `az account get-access-token` with default 1-hour expiration
- Limit: Long-running deployments (>60min) will fail mid-execution with token expiry
- Scaling path: Add token refresh logic to Deploy-Common.ps1. Track elapsed time and refresh before 60min. Already implemented in Connect-QualityDb
- Evidence: `database/deploy/Deploy-Common.ps1` lines 52-100

## Dependencies at Risk

**Azure CLI Dependency for Token Acquisition:**
- Risk: Deployment scripts depend on `az` CLI for Entra authentication. If `az login` not current or subscription not set, all deployments fail
- Impact: Complete deployment blockage until manual `az login` and `az account set` executed
- Migration plan: No planned alternative. Azure CLI is official Microsoft tooling for serverless SQL auth
- Evidence: `database/deploy/Deploy-Common.ps1` lines 69-79

**System.Data.SqlClient vs Microsoft.Data.SqlClient Assembly Loading:**
- Risk: Deploy-Common.ps1 attempts to load Microsoft.Data.SqlClient first, falls back to System.Data.SqlClient. Library mismatch could cause subtle connection string parsing differences
- Impact: Connection string parameter incompatibility, token auth behavior differences
- Migration plan: Standardize on Microsoft.Data.SqlClient (modern library). Add explicit assembly reference or NuGet package
- Evidence: `database/deploy/Deploy-Common.ps1` lines 83-100

## Resolved Critical Gaps (Phase 17 -- COMPLETE)

**End-to-End Orchestration Scripts:**
- Status: RESOLVED -- `Apply-Full.ps1` (clean-install, 123 migrations) and `Apply-v1.1.ps1` (upgrade, 37 migrations) implemented with PITR timestamp capture
- Evidence: `docs/evidence/v1.1/gate-report-SC1.md`, WhatIf logs in `docs/evidence/v1.1/`

**Cross-Cutting Verification Layer:**
- Status: RESOLVED -- `Verify-Phase17.sql` (94 checks across 9 categories) and `Smoke-Phase17.sql` (6 blocks) implemented
- Evidence: `docs/evidence/v1.1/gate-report-SC1.md`, `docs/evidence/v1.1/gate-report-SC2.md`

**Cutover Handoff and Evidence Package:**
- Status: RESOLVED -- 19-file cutover documentation package under `docs/handoffs/v1.1-cutover/`, 6 evidence files under `docs/evidence/v1.1/`
- Evidence: `docs/evidence/v1.1/sign-off-record.md` (GO WITH ACCEPTED WARNINGS)

**Index Optimization at Scale:**
- Problem: Covering indexes are in place for Phase 16, but representative-volume performance validation is still deferred
- Blocks: P95 behavior at production data volume remains uncertain
- Priority: Medium — pilot readiness dependency, not Phase 17 blocker if documented as accepted risk
- Evidence: `.planning/REQUIREMENTS.md` OPT-01..OPT-03 deferred

## Test Coverage Gaps

**End-to-End Lifecycle Testing:**
- What's not tested: Complete NCR lifecycle (create → submit → contain → investigate → disposition → verify → close) through gate SPs with real authority checks, RLS filtering, and approval lifecycle
- Files: Test requirements TEST-01 to TEST-05 deferred to future milestone
- Risk: Gate SPs tested in isolation (smoke tests), but multi-step workflows with session context switching and approval chains not validated
- Priority: High — required before pilot/UAT
- Evidence: `.planning/REQUIREMENTS.md` lines 115-116

**RLS Cross-Plant Isolation Validation:**
- What's not tested: Systematic verification that users in PlantId=1 cannot see/modify rows from PlantId=2 for every new plant-scoped table
- Files: Phase 13-15 tables: `NcrDisposition`, `NcrReworkRun`, `NcrNote`, `HoldLocation`, `DispositionAuthorityRule`
- Risk: RLS predicate configuration bug could leak data across plants
- Priority: High — security concern
- Evidence: `.planning/research/PITFALLS.md` lines 67-73, requirement SEC-05

**Gate SP Error Code Coverage:**
- What's not tested: All error code paths (52001-52499 range) for gate SPs with real session context, authority failures, reconciliation failures, CAPA dependency blocks
- Files: Gate SPs in migrations 111-118
- Risk: Error messages may be unclear or error codes may overlap. Client error handling logic unvalidated
- Priority: Medium — affects user experience
- Evidence: Phase 15 gate SPs use error code bands but no systematic error path testing documented

**Knowledge Layer Integration Testing (v2.0) -- PARTIALLY RESOLVED Phase 21:**
- Status: PARTIALLY RESOLVED -- Advisory SP verified via V01-V13 (12 PASS, 1 SKIP). V03 confirms result sets returned. V04 confirms retrieval precedence (process-specific before universal). V05 confirms @Sections filtering. V07 confirms conflict detection. V08 confirms severity band filter. V06 (NcrId overload) SKIPPED -- requires NCR data and valid RLS session.
- Remaining: V06 NcrId overload untested in zero-NCR dev environment. Full lifecycle test (NCR created -> advisory SP called with @NcrId -> RLS session context validated) requires production or seeded NCR data.
- Files: `database/deploy/Verify-Phase21.sql` (V01-V13), `quality.usp_GetDefectKnowledge` (migration 128)
- Risk: LOW -- core retrieval paths verified. NcrId overload is convenience mode, not primary.
- Priority: Medium — NcrId overload testing deferred to Phase 23/24 integration
- Evidence: Verify-Phase21.sql V01-V13 output, Apply-Phase21.ps1 deployment log

**Cross-Process Seed Data Integrity (v2.0) -- RESOLVED Phase 20:**
- Status: RESOLVED -- Verify-Phase20.sql V01-V14 validates all 68 codes across 3 process families deployed together. V03 (orphan FK) PASS, V04 (duplicate natural key) PASS, V05 (bidirectional confusion pairs) PASS with BLOCKER enforcement, V12 (line-type leakage) PASS, V13 (scope leakage) PASS. 1894 total rows with zero integrity violations.
- Files: `database/deploy/Verify-Phase20.sql`, all 126/127 migration files
- Evidence: 20-VERIFICATION.md (V01-V14 all PASS for 68 codes)

**Incoming Substrate Conditional FK Enforcement (v2.0):**
- What's not tested: Application-layer enforcement that `IncomingSubstrateDefectReasonId` is required when `DefectTypeId` = DMG-SUB and NULL otherwise. Database allows NULL unconditionally (correct design — FK is nullable). Business rule lives in Next.js frontend form logic (enforced via API validation)
- Files: `quality.NonConformanceReport` (Phase 24 ALTER), sf-quality-app NCR form (not in this repo)
- Risk: Without app-layer enforcement, inspectors can submit DMG-SUB NCRs without sub-reason, defeating the purpose of the lookup table. Conversely, non-DMG-SUB NCRs could accidentally have a sub-reason set
- Priority: Medium — data quality concern, not data integrity concern (FK still valid)
- Evidence: `docs/defect-knowledge-expansion/Defect Knowledge Expansion/LIQUID/126_liquid_paint_additions_spec.md` §2.5-2.6

**Fresh Database Deploy vs Re-Deploy Parity:**
- Status: PARTIALLY RESOLVED -- Apply-Full.ps1 and Apply-v1.1.ps1 both pass WhatIf validation. Static SQL analysis: 0 violations. Live execution blocked by unprovisioned clean database.
- Files: All 123 migrations
- Remaining risk: Full live execution on clean database deferred to pre-cutover window (ISS-01 in issues-log.md)
- Priority: Medium -- script validation complete; live execution is pre-cutover checklist item
- Evidence: `docs/evidence/v1.1/gate-report-SC1.md`, `docs/evidence/v1.1/issues-log.md` ISS-01

---

*Concerns audit: 2026-02-22 — Phase 23 preflight complete. Updated: deferred-phase references aligned (Phase 22 remains deferred), ConfusionPair allowlist follow-up moved to Phase 23 governance closure, migration chain remains 133.*
