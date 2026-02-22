# DB PROJECT.md — v3.0 Milestone Section

**Apply to:** `sf-quality-db/.planning/PROJECT.md`
**When:** Append after v2.0 milestone description, once v2.0 is archived via `/gsd:complete-milestone`
**Source:** Reference Architecture Execution_Plan.md

---

## Instructions

Append the following block to `PROJECT.md`. Update the milestone status header at the top of PROJECT.md to show v3.0 as the active milestone.

---

## v3.0 — Architectural Hardening and Platform Maturation

### What This Milestone Is

v3.0 takes the production-quality intelligence platform built in v2.0 and hardens it to the architectural standards of a reference enterprise quality management system. Where v2.0 was about building the intelligence layer (knowledge schema, analytics views, taxonomy, retrieval), v3.0 is about building the *durability* layer — the authorization depth, workflow precision, audit completeness, and data lifecycle management that a long-running, multi-party quality system requires.

**Core value:** A quality system that is not just functionally complete, but structurally sound — with traceability from every workflow transition to an audit log, timeout handling that never leaks, approval routing that is dynamically resolved, and data that can be safely archived and queried as-of any past moment.

### Architecture Rationale

This milestone closes the gap between the current sf-quality implementation and 24 patterns identified in the Reference Architecture audit (`sf-quality/Reference_Architecture/Pattern_Mapping.md`). The patterns were sourced from four JSON architecture specifications and three reverse-engineered hidden patterns from a production enterprise platform.

Key architectural decisions for this milestone:
- **DB-first remains the law:** All business logic for new patterns lives in T-SQL stored procedures. The API remains a thin gateway.
- **Validate-only via transaction rollback:** The reference pattern for dry-run validation is `@IsValidateOnly BIT = 0` on write procs → execute all validation → `IF @IsValidateOnly = 1 BEGIN ROLLBACK; SELECT validation resultset; RETURN; END`. No staging tables.
- **Audit.ApiCallLog is the first deliverable:** API Phase 3.5 (audit trail middleware) depends on this table. Phase 29 executes before all others.
- **Presave via workflow, not staging schema:** Optimistic commit mode (Phase 27) is implemented as an `IsPresave` flag on `workflow.WorkflowTransition`, not as a separate draft entity model.
- **Policy resolution in views:** The Policy Resolution Engine pattern (#17) is implemented as `security.vw_EffectivePolicyMap` — a diagnostic view over existing `workflow.SlaConfiguration` and `security.Permission` data, not a separate rules engine.

### Phase Summary

| Phase | Name | Patterns | Type |
|-------|------|----------|------|
| 25 | Workflow Engine Foundation Hardening | #2, #11 | Strengthen |
| 26 | Authorization and Approval Pipeline | #1, #7, #6 | Strengthen + New |
| 27 | Approval Lifecycle and Timeout Processing | #3, #20 | Strengthen + New |
| 28 | Event-Driven Chaining and Notifications | #8, #13 | Strengthen + New |
| 29 | Audit Infrastructure and Temporal Query | #5, #4, #22 | Strengthen |
| 30 | SLA Enforcement and Background Jobs | #12, #17 | Strengthen |
| 31 | Multi-Party Entity Lifecycle | #19, #9 | New + Strengthen |
| 32 | Validate-Only and Reference Data | #14, #10, #15 | New + Strengthen |
| 33 | Data Lifecycle and Bulk Operations | #16, #24 | Strengthen + New |
| Quick | Composite Aggregate Expansion | #18 | Strengthen |
| Quick | Document Storage Contract | #23 | Strengthen (blocked) |

### Cross-Repo Impact

This milestone introduces several DB artifacts that gate API and App work:
- `audit.ApiCallLog` (Phase 29) → gates API Phase 3.5
- `@AsOfUtc` + cursor params (Phase 29) → gates API Phase 4 pagination
- SCAR party status columns (Phase 31) → gates API Phase 5
- `@IsValidateOnly` write procs (Phase 32) → gates API Phase 7 and App form preflight

### Target State

On completion of v3.0:
- All 24 DB patterns from the Reference Architecture audit are implemented, deferred with rationale, or enriched into v4.0 planning
- `db-contract-manifest.json` reflects all v3.0 proc and view additions
- `Invoke-CycleChecks.ps1` passes with no drift
- API Phase 3.5 can proceed immediately after Phase 29 completes

### Key Decisions

- Pattern #21 (Organizational Scoping) deferred — no concrete gap beyond current plant-level RLS model
- Pattern #23 (Document Storage) blocked — pending SharePoint vs. Azure Blob storage decision
- Pattern #18 (Composite Aggregate) executed as quick item — no phase dependency, low risk
- Guided Process Orchestration hidden pattern distilled into Phase 25 step state enum (not a separate orchestration tier)
- Policy Resolution Engine hidden pattern distilled into Phase 30 SLA + policy views (not a separate rules engine)
- Data Staging hidden pattern split: presave mode → Phase 27; validate-only → Phase 32

### Design Authority Documents

- `sf-quality/Reference_Architecture/Pattern_Mapping.md` — Source audit of all 46 patterns
- `sf-quality/Reference_Architecture/Execution_Plan.md` — Phase definitions and dependency map
- `sf-quality/Reference_Architecture/Hidden_Patterns/Hidden_Architecture_Patterns_Refined.json` — Authoritative hidden pattern specs
- `sf-quality/Reference_Architecture/GSD_Seeding/DB_Planning/V3_PHASE_CONTEXTS/` — Pre-drafted CONTEXT files for each phase
