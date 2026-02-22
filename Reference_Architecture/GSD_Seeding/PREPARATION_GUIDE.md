# GSD Seeding Preparation Guide

**Generated:** 2026-02-22
**Purpose:** Pre-drafted content to apply across all three repos as they progress through the Reference Architecture execution plan. All files in this folder are ready-to-use — copy or merge into the appropriate repo context.

> **Governance note:** This folder is in the workspace root (`sf-quality/Reference_Architecture/GSD_Seeding/`). Files here are *source material*. The actual `.planning/` changes must be applied while in each child repo context — the workspace CLAUDE.md prohibits modifying child repo files from here.

---

## Operating Control Layer (Use This Every Phase)

To prevent context loss and cross-repo drift, run every phase through these two control files:

1. `OPERATIONS_DASHBOARD.md`
   - Live status, gate ledger, and execution log across DB/API/App.
   - Update this before and after each GSD command sequence.
2. `PHASE_PACKET_CHECKLIST.md`
   - Required intake/discuss/plan/execute/verify checklist for each phase.
   - Do not advance a phase until all checklist items are complete.

Fast loop for every phase:
- Check readiness and dependency gates in `OPERATIONS_DASHBOARD.md`.
- Build/validate phase packet with `PHASE_PACKET_CHECKLIST.md`.
- Run `/gsd:discuss-phase` -> `/gsd:plan-phase` -> `/gsd:execute-phase` -> `/gsd:verify-work` (where applicable).
- Record results, artifact updates, and next actions in `OPERATIONS_DASHBOARD.md`.

---

## Current State Snapshot (as of 2026-02-22)

### sf-quality-db
- **Milestone:** v2.0 Quality Intelligence Platform — IN PROGRESS
- **Phase position:** Phase 21.1 COMPLETE, Phase 22 DEFERRED, Phase 23 is next
- **v3.0 milestone:** NOT YET CREATED (blocked until v2.0 ships)
- **What's missing in planning files:**
  - `REQUIREMENTS.md` — missing ARCH-01..23 requirements (v3.0 patterns)
  - `ROADMAP.md` — missing v3.0 milestone section (Phases 25-33)
  - `PROJECT.md` — missing v3.0 milestone description
  - Phase 23/24 CONTEXT files exist but are generic stubs (need specific scope)
  - Phase 25-33 directories do not exist yet (will be created by `/gsd:new-milestone`)

### sf-quality-api
- **Milestone:** v1.0 API Gateway — IN PROGRESS
- **Phase position:** Phase 3 COMPLETE, Phase 3.5 is next
- **What's already done (2026-02-22):** ✅ Phase 3.5 inserted in ROADMAP.md ✅ API-INFRA-06..10 added to REQUIREMENTS.md ✅ 03.5-CONTEXT.md created
- **Nothing more needed** in planning files before execution starts

### sf-quality-app
- **Milestone:** v1.0 Frontend Platform — IN PROGRESS
- **Phase position:** Phase 1 not started, planning baseline established
- **What's already done (2026-02-22):** ✅ APP-AUTH-04/05, APP-WORKFLOW-03/04, APP-FORM-03, APP-TRACE-02 added to REQUIREMENTS.md
- **What's missing:** Phase CONTEXT files for Phases 3, 4, 7, 8, 9, 10 are generic stubs — need pattern-derived enrichment

### Quality Forms module (workspace package)
- **Status:** No-go for implementation start until blocker checklist is closed
- **Authority:** `Quality_Forms_Module/03_adjudication/quality-forms-module-final-authoritative-review.md`
- **Note:** Sequenced in `Execution_Plan.md` Section H as a post-core extension track (DB/API/App inserted phases)

---

## Folder Structure

```
GSD_Seeding/
├── PREPARATION_GUIDE.md           ← This file
├── OPERATIONS_DASHBOARD.md        ← Live cross-repo status + gate ledger + execution log
├── PHASE_PACKET_CHECKLIST.md      ← Required phase packet checklist (Discuss/Plan/Execute/Verify)
├── DB_Planning/
│   ├── REQUIREMENTS_ADDITIONS.md  ← ARCH-01..23 requirements (append to DB REQUIREMENTS.md)
│   ├── ROADMAP_V3_SECTION.md      ← v3.0 milestone section (append to DB ROADMAP.md)
│   ├── PROJECT_V3_SECTION.md      ← v3.0 narrative (append to DB PROJECT.md)
│   ├── PHASE_23_24_ENRICHMENTS.md ← Enriched scope for imminent Phase 23 and 24 CONTEXT files
│   └── V3_PHASE_CONTEXTS/
│       ├── 25-CONTEXT.md          ← Workflow Engine Foundation Hardening
│       ├── 26-CONTEXT.md          ← Authorization and Approval Pipeline
│       ├── 27-CONTEXT.md          ← Approval Lifecycle and Timeout Processing
│       ├── 28-CONTEXT.md          ← Event-Driven Chaining and Notifications
│       ├── 29-CONTEXT.md          ← Audit Infrastructure and Temporal Query (EXECUTE FIRST)
│       ├── 30-CONTEXT.md          ← SLA Enforcement and Background Jobs
│       ├── 31-CONTEXT.md          ← Multi-Party Entity Lifecycle
│       ├── 32-CONTEXT.md          ← Validate-Only and Reference Data
│       └── 33-CONTEXT.md          ← Data Lifecycle and Bulk Operations
└── APP_Planning/
    └── PHASE_CONTEXT_ENRICHMENTS.md ← Pattern enrichments for App Phases 3, 4, 7, 8, 9, 10
```

---

## Step-by-Step Execution Order

This follows the Execution Plan's workflow sequence (Section E).

For each phase below, apply the Operating Control Layer first:
- Use `PHASE_PACKET_CHECKLIST.md` before `/gsd:discuss-phase`
- Update `OPERATIONS_DASHBOARD.md` before and after each phase command sequence

### Phase 0 — Immediate (while still in sf-quality-db v2.0)

**In sf-quality-db context:**

1. Execute Phase 23 (Platform Governance, Documentation, Deployment):
   - Use `PHASE_23_24_ENRICHMENTS.md` → Phase 23 section to enrich `23-CONTEXT.md` before running `/gsd:plan-phase 23`
   - Run: `/gsd:discuss-phase 23` → `/gsd:plan-phase 23` → `/gsd:execute-phase 23`

2. Execute Phase 24 (Incoming Substrate and NCR Integration):
   - Use `PHASE_23_24_ENRICHMENTS.md` → Phase 24 section to enrich `24-CONTEXT.md` before running `/gsd:plan-phase 24`
   - Run: `/gsd:discuss-phase 24` → `/gsd:plan-phase 24` → `/gsd:execute-phase 24`

3. Refresh DB contract manifest for Phase 21-24 additions:
   - Run: `/gsd:quick "Refresh db-contract-manifest.json to reflect Phase 21-24 additions (9 views, 1 advisory proc, Phase 23 grants, Phase 24 substrate objects)"`

4. Archive v2.0 and create v3.0 milestone:
   - Run: `/gsd:complete-milestone` (archives v2.0; Phase 22 DEFERRED — rationale in 22-DEFERRAL.md)
   - **Before running `/gsd:new-milestone`:** Append all content from `DB_Planning/REQUIREMENTS_ADDITIONS.md` to `.planning/REQUIREMENTS.md`
   - Run: `/gsd:new-milestone` with name "Architectural Hardening and Platform Maturation", version v3.0, phases 25-33
   - After milestone creation: Copy the 9 phase CONTEXT files from `V3_PHASE_CONTEXTS/` into their respective phase directories

5. Apply DB planning file additions (switch to sf-quality-db context):
   - Append `DB_Planning/ROADMAP_V3_SECTION.md` → append to `.planning/ROADMAP.md` after v2.0 milestone
   - Append `DB_Planning/PROJECT_V3_SECTION.md` → append to `.planning/PROJECT.md`

---

### Phase 1 — v3.0 Bootstrap: Phase 29 First (API Prerequisite)

**In sf-quality-db context:**

Phase 29 must execute before API Phase 3.5 (it creates `audit.ApiCallLog` that the API audit middleware writes to).

- Run: `/gsd:discuss-phase 29` → `/gsd:plan-phase 29` → `/gsd:execute-phase 29` → `/gsd:verify-work 29`
- Acceptance gate: `audit.ApiCallLog` exists; at least one proc accepts `@AsOfUtc DATETIME2 = NULL`; tree helpers callable
- Run: `/gsd:quick "Refresh db-contract-manifest.json for Phase 29 additions"`

**Also recommended — Quick item #18 before API Phase 4:**

- Run: `/gsd:quick "Add expand parameters to composite detail procs (#18 Composite Aggregate Expansion)"`

---

### Phase 2 — API Phase 3.4 (if not already done) + Phase 3.5

**In sf-quality-api context:**

First check if Phase 3.4 middleware plumbing was done in Phase 3:
- Check for: GUID CorrelationId enforcement, `SqlErrorNumber` stash on `ErrorHandlingMiddleware`, `50414→HTTP 202` mapping

If not done:
- Run: `/gsd:quick "Phase 3.4 middleware plumbing — enforce GUID correlation IDs, stash SqlErrorNumber on error handler, add 50414→HTTP 202 mapping"`

Then Phase 3.5:
- Run: `/gsd:discuss-phase 3.5` → `/gsd:plan-phase 3.5` → `/gsd:execute-phase 3.5`
- Gate: DB Phase 29 must be complete first (`audit.ApiCallLog` must exist)

---

### Phase 3 — DB Main Dependency Chain (Phases 25-28, 30)

**In sf-quality-db context:**

These can run in parallel with API Phases 4-6:

- Phase 25: `/gsd:discuss-phase 25` → `/gsd:plan-phase 25` → `/gsd:execute-phase 25` → `/gsd:verify-work 25`
- Phase 26: `/gsd:discuss-phase 26` → (gate: Phase 25 complete) → ...
- Phase 27: Depends on Phase 25+26
- Phase 28: Depends on Phase 25+27
- Phase 30: Depends on Phase 27

Run `/gsd:quick "Refresh db-contract-manifest.json for Phases 25-28 additions"` after Phase 28.

---

### Phase 4 — DB Independent Tracks (Phases 31, 32, 33)

**In sf-quality-db context:**

These are independent and can interleave with Phase 3:

- Phase 31: `/gsd:plan-phase 31` → `/gsd:execute-phase 31` (then refresh manifest — SCAR party status is cross-repo visible for API Phase 5)
- Phase 32: `/gsd:discuss-phase 32` → `/gsd:plan-phase 32` → `/gsd:execute-phase 32` (then refresh manifest — validate-only procs gate API Phase 7)
- Phase 33: `/gsd:plan-phase 33` → `/gsd:execute-phase 33`

---

### Phase 5 — App Phase CONTEXT Enrichments (before Phase 1 execution)

**In sf-quality-app context:**

Before running any `/gsd:plan-phase` for App Phases 3, 4, 7, 8, 9, or 10:

- Apply enrichments from `APP_Planning/PHASE_CONTEXT_ENRICHMENTS.md` to the corresponding CONTEXT file stubs
- Then proceed with `/gsd:plan-phase N` as normal

App Phases 1-3 can start in parallel with API Phases 3.5-6 (no domain endpoint dependency).

---

### Phase 6 — API Phases 4-10

**In sf-quality-api context:**

Execute with expanded scope per Execution Plan Section B2:
- Phase 4: CAPA + pagination + query governor (gate: DB cursor params on list procs)
- Phase 5: SCAR/Audit (gate: DB Phase 31 complete for SCAR party status)
- Phase 7: Workflow + feature gating + validate-only (gate: DB Phase 32 complete)
- Phases 8, 9, 10: Knowledge, Dashboards, Integration (sequential)

---

### Phase 7 — Quality Forms Extension Track (after core phases)

**In all three repo contexts (sequenced DB -> API -> App):**

Open this track only after the entry gates in `Execution_Plan.md` Section H are met:
- DB Phase 23/24 complete + manifest refreshed
- API Phase 3.5 complete
- Quality Forms adjudication checklist green (all 9 implementation-start criteria)
- Quality Forms docs aligned to `/v1` routes and approval-required `202` semantics

Then run three contract waves:

1. **Wave QF-A**
   - DB: insert and execute Phase 34
   - Refresh DB manifest
   - API: insert and execute Phase 11
   - Publish OpenAPI
   - App: insert and execute Phase 11

2. **Wave QF-B**
   - DB: execute Phase 35
   - Refresh DB manifest
   - API: execute Phase 12
   - Publish OpenAPI
   - App: execute Phase 12

3. **Wave QF-C**
   - DB: execute Phase 36
   - Refresh DB manifest
   - API: execute Phase 13
   - Publish OpenAPI
   - App: execute Phase 13

---

## Cross-Repo Dependency Gates Summary

| DB Phase | What it provides | Consumer | Hard gate? |
|----------|-----------------|----------|-----------|
| Phase 29 | `audit.ApiCallLog` table | API Phase 3.5 | YES — API audit middleware writes here |
| Phase 29 | `@AsOfUtc` + cursor params | API Phase 4 | YES — pagination infra |
| Phase 31 | SCAR party status columns | API Phase 5 | YES — new endpoint surface |
| Phase 32 | `@IsValidateOnly BIT` on write procs | API Phase 7 | YES — validate-only passthrough |
| Phase 28 | `workflow.NotificationQueue` | API Phase 7+ | YES — notification endpoints |
| API Phase 4+ | Domain endpoints available | App Phase 4+ | YES |
| DB Phase 34 | Quality Forms foundation contracts + safe migration set | API Phase 11 | YES — API cannot start QF endpoints without these contracts |
| DB Phase 35 | Quality Forms operational contracts | API Phase 12 | YES |
| DB Phase 36 | Quality Forms hardening/reporting contracts | API Phase 13 | YES |
| API Phases 11-13 | Versioned inspection endpoint contracts | App Phases 11-13 | YES |

---

## Content Files Index

| File | Apply to | When |
|------|----------|------|
| `DB_Planning/REQUIREMENTS_ADDITIONS.md` | `sf-quality-db/.planning/REQUIREMENTS.md` | Before `/gsd:new-milestone` for v3.0 |
| `DB_Planning/ROADMAP_V3_SECTION.md` | `sf-quality-db/.planning/ROADMAP.md` | After v2.0 milestone archived |
| `DB_Planning/PROJECT_V3_SECTION.md` | `sf-quality-db/.planning/PROJECT.md` | After v2.0 milestone archived |
| `DB_Planning/PHASE_23_24_ENRICHMENTS.md` | Phase 23 and 24 CONTEXT files | Before running `/gsd:plan-phase 23` and 24 |
| `DB_Planning/V3_PHASE_CONTEXTS/29-CONTEXT.md` | `phases/29-*/29-CONTEXT.md` | When Phase 29 directory created |
| `DB_Planning/V3_PHASE_CONTEXTS/25-CONTEXT.md` | `phases/25-*/25-CONTEXT.md` | When Phase 25 directory created |
| `DB_Planning/V3_PHASE_CONTEXTS/26-33-CONTEXT.md` | Corresponding phase dirs | When each phase directory created |
| `APP_Planning/PHASE_CONTEXT_ENRICHMENTS.md` | App phase CONTEXT stubs | Before each app phase is planned |
| `../Quality_Forms_Module/03_adjudication/quality-forms-module-final-authoritative-review.md` | DB/API/App Phase 34/11/11 entry gates | Before opening Quality Forms extension track |
| `../Quality_Forms_Module/04_packages/quality-inspection-forms-module-package/docs/02_stored_procedure_contracts.md` | API Phase 11-13 CONTEXT files | Before planning each API Quality Forms phase |
| `../Quality_Forms_Module/04_packages/quality-inspection-forms-module-package/docs/03_api_endpoint_design.md` | API + App Quality Forms phase context | Before planning each API/App Quality Forms phase |
