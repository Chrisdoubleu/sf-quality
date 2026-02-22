# sf-quality Workspace Remediation Deep Dive and Execution-Safe Master Plan

Date: 2026-02-22  
Authoring scope: `sf-quality` workspace root (`Reference_Architecture`)  
Execution scope: `sf-quality-db`, `sf-quality-api`, `sf-quality-app`

---

## 1. Objective

Integrate the two remediation tracks into one execution-safe program:

1. `Reference_Architecture/Execution_Plan.md` (46 pattern closure, capability expansion)
2. `Reference_Architecture/ENTERPRISE_ARCHITECTURE_ASSESSMENT_AND_REMEDIATION_PLAN.md` (structural coupling remediation)

Primary success condition: remediate architectural debt without breaking contract-chain stability or downstream execution flow.

---

## 2. No-Break Contract

This plan is governed by hard stop rules:

1. No dependent phase starts before producer gate is green.
2. No contract-affecting change merges without contract artifact refresh and cycle checks.
3. No cross-repo speculative edits; each repo owns its own implementation.
4. No big-bang rewrites of workflow or API layers; changes are phased with compatibility windows.
5. If any required check fails, execution stops and enters amendment protocol.

Definition of "break":

- contract-chain drift (DB manifest -> API snapshot -> API publish -> App snapshot)
- failing CI checks in any touched repo
- runtime contract behavior mismatch (error mapping, route semantics, proc signatures)
- irreversible schema coupling regressions (cross-context DML reintroduced, hard FK misuse)

---

## 3. Deep-Dive Findings

## 3.1 Confirmed Baseline Facts

1. Architecture is SQL-first, thin API, API-only frontend.
   - Evidence: `Reference_Architecture/README.md`
   - Evidence: `sf-quality-db/README.md`
   - Evidence: `sf-quality-api/README.md`
   - Evidence: `sf-quality-app/README.md`
2. Contract chain is implemented and operational.
   - Evidence: `sf-quality-db/.planning/contracts/db-contract-manifest.json`
   - Evidence: `sf-quality-api/.planning/contracts/db-contract-manifest.snapshot.json`
   - Evidence: `sf-quality-api/.planning/contracts/api-openapi.publish.json`
   - Evidence: `sf-quality-app/.planning/contracts/api-openapi.snapshot.json`
3. DB remediation context is real and active (v2.0 Phase 23 next, 22 deferred).
   - Evidence: `sf-quality-db/.planning/STATE.md`
   - Evidence: `sf-quality-db/.planning/ROADMAP.md`
4. Full cross-repo checks currently pass in baseline state.
   - Command: `pwsh scripts/Invoke-CycleChecks.ps1` (from `sf-quality-db`)

## 3.2 Structural Debt Confirmed (Assessment is Valid)

1. Workflow god-module coupling is present (`workflow.usp_TransitionState` direct domain table dispatch/update).
   - Evidence: `sf-quality-db/database/migrations/061_workflow_transition_sp.sql`
2. Context ownership violation exists (`quality` writing `workflow.StatusHistory` directly).
   - Evidence: `sf-quality-db/database/migrations/112_gate_create_submit.sql`
3. Outbox/eventing is NCR-focused, not generalized.
   - Evidence: `sf-quality-db/database/migrations/121_phase16_outbox_view_and_sps.sql`
4. Department/jurisdiction ABAC is not deeply implemented.
   - Evidence: `sf-quality-db/database/migrations/007_session_context_sp.sql`
   - Evidence: `sf-quality-db/database/migrations/096_create_policy_engine_sps.sql`
5. API endpoint SQL coupling exists (`CommandType.Text` query strings in endpoints).
   - Evidence: `sf-quality-api/src/SfQualityApi/Endpoints/NcrEndpoints.cs`

## 3.3 Execution Hazards Discovered (Must Be Addressed First)

1. API/App CI scope can no-op on runtime code changes.
   - Current trigger scope is `.planning/**` + `scripts/**` only.
   - Evidence: `sf-quality-api/.github/workflows/planning-contract-validation.yml`
   - Evidence: `sf-quality-app/.github/workflows/planning-contract-validation.yml`
2. API Phase 3.4 plumbing appears incomplete in codebase (even though planned).
   - Correlation ID accepts arbitrary header value (no GUID enforcement).
   - Error middleware does not stash `SqlErrorNumber` in `HttpContext.Items`.
   - `50414` is mapped to HTTP `403`, not `202`.
   - Evidence: `sf-quality-api/src/SfQualityApi/Middleware/CorrelationIdMiddleware.cs`
   - Evidence: `sf-quality-api/src/SfQualityApi/Middleware/ErrorHandlingMiddleware.cs`
   - Evidence: `sf-quality-api/src/SfQualityApi/Infrastructure/SqlErrorMapper.cs`
3. DB static SQL rules do not enforce cross-schema DML boundary ownership today.
   - Evidence: `sf-quality-db/database/deploy/Test-SqlStaticRules.ps1`
4. Local global-GSD patch check is machine-specific and can fail in valid environments.
   - Evidence: `sf-quality-db/.planning/enforcement/ENFORCEMENT-REGISTRY.json`
   - Evidence: `sf-quality-db/database/deploy/Test-EnforcementRegistry.ps1`
5. Some root reference docs are stale vs current repo state and should be refreshed before planning dependencies.
   - Evidence: `Reference_Architecture/Pattern_Mapping.md`

---

## 4. Reconciliation: Execution Plan vs Assessment

Use this authoritative mapping:

| Assessment Phase | Existing Execution Plan Coverage | Required Reconciliation Action |
|---|---|---|
| Boundary Hardening (adapter-proc, cross-schema DML controls) | Partial in Phase 25 | Expand Phase 25 with structural remediations |
| Outbox Generalization | Present in Phase 28 | Keep as-is, tighten compatibility criteria |
| ABAC Deepening (department/jurisdiction) | Pattern #21 deferred | Reverse deferral and implement as Phase 26.1 (or expanded 26) |
| API Ports/Adapters | Not explicit in current API sequence | Add API Phase 3.6 (preferred) before API Phase 4 |
| Inspection FK Policy | Partial in Quality Forms Section H | Add explicit FK policy gate before QF DB phase opens |

### 4.1 Requirement Namespace Conflict Resolution

Assessment ticket IDs currently use `ARCH-01..10`, which collides with v3.0 `ARCH-*`.

Resolution:

- Keep existing `ARCH-*` for pattern-derived requirements.
- Introduce `STRUCT-01..10` for structural debt remediation.
- Add mapping table (`ARCH` vs `STRUCT`) in reconciliation documentation.

### 4.2 ABAC Decision Gate (Decide, Do Not Default)

Before scheduling DB Phase `26.1`, run an explicit ABAC decision gate and record the result in a dated ADR.

ABAC deepening becomes mandatory if any trigger is true:

1. Any plant has multi-department quality ownership requiring intra-plant data separation.
2. SoD, audit, or internal control findings require department/jurisdiction enforcement.
3. The business needs explicit same-plant cross-department visibility restrictions.
4. A customer or auditor asks, "Can Department X users view Department Y NCRs in the same plant?" and current answer is effectively "yes."

If none are true, defer with:

1. dated ADR
2. explicit revisit triggers
3. next review date

---

## 5. Integrated Execution-Safe Sequence

## Stage 0 - Safety Hardening (Mandatory Before Structural Work)

## 0A. Baseline and Preflight

Run and archive outputs:

```powershell
# DB repo
pwsh ./database/deploy/Test-EnforcementRegistry.ps1 -RepoRoot (Get-Location)
pwsh ./database/deploy/Test-DbContractManifest.ps1 -RepoRoot (Get-Location)
pwsh ./database/deploy/Test-SqlStaticRules.ps1 -RepoRoot (Get-Location)

# Cross-repo
pwsh ./scripts/Invoke-CycleChecks.ps1

# API
dotnet build
```

## 0B. CI Scope Hardening

1. API/App workflow scope must include runtime source changes.
2. Add explicit trigger patterns for app/api source surfaces (`src/**` and app runtime folders).
3. Keep `validation_mode` support (`advisory`/`blocking`) unchanged.

Exit criteria:

- API/App planning-contract workflows run for runtime code changes.

## 0C. Guardrail Script Hardening

1. DB: extend static rules with cross-schema DML boundary checks + allowlist.
2. API: add static check to ban new endpoint-level inline SQL text where repository port pattern is required.
3. Resolve `ENF-CLAUDE-GSD-GLOBAL-PATCHES` strategy explicitly:
   - Option A (recommended): retire it completely.
   - Option B (fallback): keep it local-only/advisory and never CI-blocking.

If Option A is selected, apply full retirement in one change set:

1. remove `ENF-CLAUDE-GSD-GLOBAL-PATCHES` from enforcement registry
2. remove `-CheckGlobalGsd` operational expectations from active guidance
3. keep `Test-EnforcementRegistry.ps1` focused on repository-governed checks

Exit criteria:

- new checks fail on prohibited patterns
- no false-positive environment failures for local patch markers
- no half-retired enforcement states (either fully retired or explicitly local/advisory)

## Stage 1 - Complete DB v2.0 and Archive

1. Execute DB Phase 23.
2. Execute DB Phase 24.
3. Refresh DB manifest only if proc/view contract surface changed.
4. Archive v2.0 milestone.

Gate:

- v2.0 complete with Phase 22 still documented as deferred
- cross-repo cycle checks pass

## Stage 2 - Workspace Root Reconciliation Updates

Update root architecture artifacts before v3.0 execution:

1. Expand `Execution_Plan.md` Phase 25 for boundary hardening.
2. Insert ABAC deepening into 26.1 (or expanded 26).
3. Insert API 3.6 ports/adapters phase.
4. Rename Assessment ticket namespace to `STRUCT-*`.
5. Add reconciliation section to assessment doc.
6. Update GSD seeding context files for 25 and 26.

Gate:

- root docs internally consistent
- no ID collisions

## Stage 3 - DB v3.0 Initialization

1. Seed v3.0 requirements (`ARCH-*` + `STRUCT-*`).
2. Create v3.0 milestone phases.
3. Apply v3 phase context files.

Gate:

- DB roadmap/requirements/project/state aligned

## Stage 4 - Producer-First Prerequisite Chain

1. DB Phase 29 first (`audit.ApiCallLog`, temporal query support).
2. API Phase 3.4 must be completed (if missing).
3. API Phase 3.5 executes only after DB 29 gate.

Gate:

- DB 29 artifacts present
- API 3.4 behavior validated (`GUID correlation`, `SqlErrorNumber stash`, `50414 -> 202`)

## Stage 5 - Main Structural Chain

1. DB Phase 25 (expanded with STRUCT-01/02/03).
2. DB Phase 26 (existing auth/approval).
3. ABAC decision gate executes and is documented (Section 4.2).
4. DB Phase 26.1 (STRUCT-07/08 ABAC deepening), if gate triggers require implementation.
5. DB Phase 27.
6. DB Phase 28.
7. DB Phase 30.
8. API Phase 3.6 (STRUCT-09 ports/adapters refactor).
9. API Phase 4+ continuation.

Gate:

- each phase passes `/gsd:verify-work` before next dependent phase

## Stage 6 - Independent and Parallel Tracks

1. DB 31/32/33 as planned.
2. API 5-10 with standard DB dependency gates.
3. App 1-10 after API contract readiness.

## Stage 7 - Quality Forms Extension Gate

Before opening QF phases:

1. enforce STRUCT-10 FK policy decision record
2. confirm API approval-required semantics (`202`) and `/v1` alignment
3. confirm all Section H entry gates are green

---

## 6. Gate Matrix (Do Not Skip)

| Gate ID | Producer | Consumer | Command(s) | Pass Condition |
|---|---|---|---|---|
| GATE-BASELINE | All repos | All stages | `Invoke-CycleChecks.ps1` | All checks pass |
| GATE-DB29-API35 | DB Phase 29 | API 3.5 | DB manifest refresh + cycle checks | `audit.ApiCallLog` and related contract visible |
| GATE-API34-API35 | API 3.4 | API 3.5 | build + targeted behavioral checks | `GUID`, `SqlErrorNumber stash`, `50414->202` in code and tests |
| GATE-DB25-DB26 | DB 25 | DB 26 | DB verify work | adapter foundations + guard definitions stable |
| GATE-DB26-DB261 | DB 26 | DB 26.1 | DB verify work | role/routing changes stable before ABAC deepening |
| GATE-ABAC-DECISION | Architecture governance | DB 26.1 | ADR + trigger checklist | explicit implement/defer decision with date and revisit conditions |
| GATE-DB261-API36 | DB 26.1 | API 3.6+ | manifest + cycle checks | ABAC behavior contract stabilized |
| GATE-DB32-API7 | DB 32 | API 7 | manifest + cycle checks | validate-only proc contracts published |
| GATE-SKILL-SYNC | Phase closeout | Next phase planning | closeout checklist update | custom skill updated or explicit no-change rationale recorded |
| GATE-QF-ENTRY | Core complete | QF phases | Section H checklist | all mandatory QF entry gates green |
| GATE-STABILITY-3PH | Post-remediation run | Program closeout | trend report over 3 phases | zero boundary violations and zero allowlist additions for 3 consecutive phases |

---

## 6A. GitHub Required Checks Mapping

Use these as required branch-protection checks so remediation gates are enforceable at merge time.

## sf-quality-db (`main`)

1. Workflow: `.github/workflows/sql-validation.yml`
   - Job: `Static Lint`
   - Job: `Deploy To CI Database`
   - Job: `Verify + Smoke`
2. Workflow: `.github/workflows/enforcement-governance.yml`
   - Job: `Enforcement Contract`

## sf-quality-api (`main`)

1. Workflow: `.github/workflows/planning-contract-validation.yml`
   - Job: `Planning and Contract Checks`
   - Includes runtime-scope build validation for source/config changes.

## sf-quality-app (`main`)

1. Workflow: `.github/workflows/planning-contract-validation.yml`
   - Job: `Planning and Contract Checks`
   - Includes runtime-scope build validation when app runtime is scaffolded.

Operational note:

1. Keep per-repo `workflow.validation_mode` aligned with desired strictness (`advisory` vs `blocking`).
2. For post-remediation hardening, promote API/App to `blocking` when ready.

---

## 7. Planned File Update Set (By Scope)

## Workspace Root (`sf-quality/Reference_Architecture`)

1. `Execution_Plan.md`
2. `ENTERPRISE_ARCHITECTURE_ASSESSMENT_AND_REMEDIATION_PLAN.md`
3. `GSD_Seeding/DB_Planning/V3_PHASE_CONTEXTS/25-CONTEXT.md`
4. `GSD_Seeding/DB_Planning/V3_PHASE_CONTEXTS/26-CONTEXT.md`
5. `GSD_Seeding/DB_Planning/REQUIREMENTS_ADDITIONS.md`
6. (optional) `Pattern_Mapping.md` stale-state refresh

## sf-quality-db

1. `.planning` milestone/requirements/phase files for v3.0 and STRUCT requirements
2. `database/deploy/Test-SqlStaticRules.ps1` (cross-schema DML rule extension)
3. optional boundary allowlist file for controlled exceptions

## sf-quality-api

1. `.planning` roadmap/requirements/phase insertion for API 3.6
2. CI workflow scope expansion
3. API 3.4 plumbing completion
4. repository ports/adapters phase implementation

## sf-quality-app

1. CI workflow scope expansion
2. planned context/requirements enrichments aligned to API publication gates

---

## 8. Contract Artifact Refresh Decision Rules

Refresh DB manifest when:

- procedure/view names are added, removed, or renamed
- proc/view signatures or contracts materially change

Do not refresh DB manifest for pure data migrations that do not change contract objects.

Refresh API OpenAPI publish artifact when:

- any endpoint path/method/schema/status contract changes

Refresh App API snapshot when:

- API OpenAPI publish artifact version changes

---

## 9. Failure Handling and Amendment Protocol

If a consumer phase finds a producer gap:

1. pause consumer phase immediately
2. open targeted producer hotfix (`/gsd:quick` or inserted mini-phase)
3. verify producer fix
4. refresh producer artifact
5. rerun cycle checks
6. resume consumer phase

If a gate fails repeatedly:

1. mark gate `BLOCKED` in operations dashboard
2. document blocker and required owner decision
3. do not advance dependent phases

---

## 9A. Post-Remediation Anti-Drift Controls

Execution safety is not sufficient by itself. Once structural remediation lands, these controls keep the architecture remediated.

### 9A.1 Permanent CI Guardrails

1. DB cross-schema DML checker:
   - deny by default
   - explicit allowlist only for approved exceptions
2. API inline SQL boundary checker:
   - enforce repository-port pattern in target endpoint surfaces
   - fail on new endpoint-layer raw SQL text where disallowed
3. API/App workflow trigger scope:
   - include runtime source paths so code changes cannot bypass checks

### 9A.2 Skill-Based Pattern Retention

Maintain a custom architecture skill as long-lived pattern memory (`sf-quality-architecture`).

Required phase closeout decision:

1. `Skill Sync: Updated` with changed sections listed, or
2. `Skill Sync: No Change` with date, phase, and rationale.

This prevents stale or implicit pattern drift between phases.

### 9A.3 Stability Evidence Gate

A "remediated and stable" claim requires measured evidence:

1. 3 consecutive completed phases
2. cross-schema DML checker reports zero violations
3. API inline SQL checker reports zero violations
4. zero allowlist additions during those same 3 phases

If any condition fails, stability clock resets.

---

## 10. Definition of Done

Program is complete only when all are true:

1. all 46 pattern items and all 10 structural items are completed or explicitly deferred with rationale
2. contract chain remains green at each wave
3. no endpoint-level architectural violations remain where disallowed (inline SQL in targeted phases, unmapped approval semantics)
4. ABAC decision gate is closed: implemented and deny-tested when triggers are true, or deferred via dated ADR with explicit revisit triggers when false
5. boundary enforcement checks prevent cross-context DML regressions
6. Quality Forms track starts only after entry gates are green
7. anti-drift controls are active (CI + skill sync cadence) and functioning
8. stability evidence gate passed (`GATE-STABILITY-3PH`)

---

## Appendix A - Proposed STRUCT Requirement IDs

| ID | Summary | Target Phase |
|---|---|---|
| STRUCT-01 | Refactor `workflow.usp_TransitionState` to adapter-proc model | DB 25 |
| STRUCT-02 | Remove direct foreign-context status writes (`quality -> workflow.StatusHistory`) | DB 25 |
| STRUCT-03 | Add cross-schema DML static checker + allowlist | DB 25 |
| STRUCT-04 | Create generic `integration.DomainEventOutbox` + generic polling/ack | DB 28 |
| STRUCT-05 | Maintain NCR compatibility layer during outbox migration | DB 28 |
| STRUCT-06 | Add `workflow.EventSubscription` + `workflow.NotificationQueue` | DB 28 |
| STRUCT-07 | Extend session/policy model to department/jurisdiction ABAC | DB 26.1 |
| STRUCT-08 | Add explicit same-plant cross-department deny tests | DB 26.1 |
| STRUCT-09 | API repository ports/adapters; remove endpoint inline SQL in target scope | API 3.6 |
| STRUCT-10 | Publish and enforce hard-FK vs soft-reference policy for inspection links | Pre-QF gate |

---

## Appendix B - Minimal Execution Check Commands

```powershell
# DB local checks
pwsh ./database/deploy/Test-EnforcementRegistry.ps1 -RepoRoot (Get-Location)
pwsh ./database/deploy/Test-DbContractManifest.ps1 -RepoRoot (Get-Location)
pwsh ./database/deploy/Test-SqlStaticRules.ps1 -RepoRoot (Get-Location)

# API local checks
dotnet build
pwsh ./scripts/Test-PlanningConsistency.ps1 -RepoRoot (Get-Location)
pwsh ./scripts/Test-DbContractReferences.ps1 -RepoRoot (Get-Location)
pwsh ./scripts/Test-OpenApiPublication.ps1 -RepoRoot (Get-Location)

# App local checks
pwsh ./scripts/Test-PlanningConsistency.ps1 -RepoRoot (Get-Location)
pwsh ./scripts/Test-ApiContractReferences.ps1 -RepoRoot (Get-Location)

# Cross-repo
pwsh ./scripts/Invoke-CycleChecks.ps1
```
