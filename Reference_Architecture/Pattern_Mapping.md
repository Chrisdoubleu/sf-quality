# Reference Architecture Pattern Mapping — sf-quality

**Generated:** 2026-02-21
**Last Audited:** 2026-02-21
**Scope:** Maps applicable reference-architecture patterns to implemented artifacts and gaps in `sf-quality-db`, `sf-quality-api`, and `sf-quality-app`.

## Method and Constraints

- **Reference sources re-read from scratch:**
  - `Reference_Architecture_Package/Platform_System_Architecture_Technical_Patterns.json`
  - `Reference_Architecture_Package/Security_Role_Architecture_Agnostic.json`
  - `Reference_Architecture_Package/Workflow_Engine_Architecture_Agnostic.json`
  - `Reference_Architecture_Package/API_Integration_Architecture_Agnostic.json`
  - `Reference_Architecture_Package/architectural_briefing.md`
  - `Reference_Architecture_Package/Hidden_Architecture_Patterns_Reverse_Engineered.json` (v4: three reverse-engineered patterns)
- **Codebase rescanned:**
  - `sf-quality-db` — 133 migrations (001–130 including 086a and 126a–d), 80 published procedures, 36 published views per `db-contract-manifest.json` v1.0.0. Note: Phase 21 (migrations 122–130) adds 9 knowledge views and 1 advisory procedure not yet reflected in the v1.0.0 manifest; actual counts are 81 procedures and 45 views.
  - `sf-quality-api` — 10 C# source files, 27 endpoints (25 NCR + 2 diagnostics), Phase 3 of 10 complete, `api-openapi.publish.json` v0.2.0.
  - `sf-quality-app` — 51 planning files, 0 runtime source files. Phase 1 of 10 not started. `api-openapi.snapshot.json` v0.1.0 (behind API publish v0.2.0).
- **Constraints enforced from** `README_AGENT_ORIENTATION_COMBINED.md`: SQL-first business logic, thin Dapper API, single-tenant scope, Azure App Service runtime.

**Classification key:**
- **Strengthen Existing** — Pattern is present in usable form, but has clear hardening/coverage gaps.
- **Net New** — Pattern is not implemented in the current architecture and would add concrete value.
- **Inform Planning** — Pattern is relevant to `sf-quality-app` planning or later API phases.

**Revision history:**
- **v1 (initial):** 36 patterns from two independent analyses.
- **v2 (first re-audit):** Corrected classifications, normalized JSON path citations, added 6 missing patterns. Total: 42.
- **v3:** Full re-read of all four JSON specs and architectural briefing. Systematic rescan of all three repos (133 DB migrations, 10 API source files, 51 app planning files). All 42 entries audited: every `$.json_path` verified against source JSON, every migration/file citation verified against filesystem, every classification re-evaluated. No entries removed. 2 applicable missing patterns added; 2 Appendix A exclusions added. No cosmetic-only changes. **Updated pattern count: 44.**
- **v4 (this revision):** Cross-referenced three reverse-engineered hidden architecture patterns (`Reference_Architecture_Package/Hidden_Architecture_Patterns_Reverse_Engineered.json`) — Guided Process Orchestration, Policy Resolution Engine, Data Staging and Edit Mode Architecture. Five existing entries enriched with deeper context from hidden patterns (#2, #6, #12, #14, #31). Two new entries added for genuinely distinct architectural concepts not covered by existing entries: Multi-Party Entity Lifecycle Tracking (#23) and Optimistic Commit Mode for Safety-Critical Transitions (#24). Three Appendix A exclusions added for hidden pattern sub-patterns that exceed single-tenant scope. **Updated pattern count: 46.**

Patterns that do not fit a single-tenant Azure App Service quality-management system are listed in Appendix A.

---

## sf-quality-db

### HIGH IMPACT

#### 1. Defense-in-Depth Layered Authorization Pipeline
**Reference JSON paths:**
- `Platform_System_Architecture_Technical_Patterns.json: $.identity_and_access_patterns.authorization_architecture`
- `Security_Role_Architecture_Agnostic.json: $.security_model_summary.layers`
- `Security_Role_Architecture_Agnostic.json: $.data_authorization.rules`

**Code evidence:**
- `sf-quality-db/database/migrations/007_session_context_sp.sql` (`dbo.usp_SetSessionContext` sets `UserId`, `AzureOid`, `IsAdmin`)
- `sf-quality-db/database/migrations/006_rls_predicates.sql` (`security.fn_PlantAccessPredicate`, `security.fn_PlantWriteBlockPredicate`, `security.PlantIsolationPolicy`)
- `sf-quality-db/database/migrations/091_create_security_catalog.sql` (`security.Feature`, `security.Permission`, `security.RolePermission`, `security.RolePermissionConstraint`)
- `sf-quality-db/database/migrations/096_create_policy_engine_sps.sql` (`security.usp_CheckPermission`, `security.usp_EvaluatePolicy`)
- `sf-quality-db/database/migrations/005_security_tables.sql` (`dbo.Role.RoleTier`)

**Classification:** Strengthen Existing
**Rationale:** Layered authorization is implemented, but parent-child role inheritance is not explicitly modeled as a constrained tree and CRUD matrix semantics are not represented as an auditable role x data x CRUD matrix.

**Recommended strengthening:** Add explicit role parent metadata and a subtractive-inheritance validator; add an effective CRUD matrix diagnostic view for governance review.

---

#### 2. Workflow Orchestration Engine with Typed Node Concepts
**Reference JSON paths:**
- `Workflow_Engine_Architecture_Agnostic.json: $.architecture_overview`
- `Workflow_Engine_Architecture_Agnostic.json: $.node_types.routing`
- `Workflow_Engine_Architecture_Agnostic.json: $.expression_engine`
- `Platform_System_Architecture_Technical_Patterns.json: $.workflow_orchestration_engine.graph_engine`
- `Hidden_Architecture_Patterns_Reverse_Engineered.json: $.pattern_1_guided_process_orchestration` (guided process as higher-tier orchestration above workflow engine)

**Code evidence:**
- `sf-quality-db/database/migrations/046_workflow_state_machine.sql` (`workflow.WorkflowProcess`, `workflow.WorkflowState`, `workflow.WorkflowTransition`, `workflow.SlaConfiguration`)
- `sf-quality-db/database/migrations/051_escalation_approval_tables.sql` (`workflow.ApprovalChain`, `workflow.ApprovalStep`, `workflow.ApprovalRecord`, `workflow.EscalationRule`)
- `sf-quality-db/database/migrations/098_harden_workflow_transition_sp.sql` (`workflow.usp_TransitionState`)
- `sf-quality-db/database/migrations/072_harden_workflow_guard_parsing.sql`
- `sf-quality-db/database/migrations/037_eightd_tables.sql` (`rca.EightDReport`, `rca.EightDStep` with D0-D8 disciplines — partial guided process implementation)

**Classification:** Strengthen Existing
**Rationale:** Table-driven orchestration, approval gates, and guard evaluation are real and active; reusable condition catalogs and notification-node semantics are still implicit. The hidden pattern reveals the reference platform uses a two-tier orchestration model (guided process conductor above the workflow engine) for multi-step processes like 8D investigations. Our 8D step model (`rca.EightDStep`) is a pragmatic single-tier implementation appropriate for single-tenant scope, but the per-step state tracking is limited to a `IsComplete` BIT flag — insufficient for tracking in-progress, skipped, or blocked steps.

**Recommended strengthening:** Introduce reusable guard definitions and explicit notification metadata instead of embedding all behavior at transition rows. Enhance `rca.EightDStep` with a proper step state enum (NotStarted/InProgress/Complete/Skipped/Blocked) replacing the `IsComplete` BIT flag, add `IsSkippable` configuration and `SkippedReason`/`SkippedByUserId` audit fields, and add advisory prerequisite configuration (`PrerequisiteStepNumber`) per step. Add `rca.vw_EightDCompletionStatus` view computing overall process completion metrics (total/complete/skipped/in-progress/overdue step counts) to support dashboard reporting and SLA evaluation — this achieves the hidden pattern's monitoring workflow concept without a separate orchestration tier.

---

#### 3. Approval Timeout and Auto-Resolution
**Reference JSON paths:**
- `Workflow_Engine_Architecture_Agnostic.json: $.timeout_and_auto_resolution.description`
- `Platform_System_Architecture_Technical_Patterns.json: $.workflow_orchestration_engine.timeout_and_auto_resolution`

**Code evidence:**
- `sf-quality-db/database/migrations/051_escalation_approval_tables.sql` (`workflow.ApprovalChain.TimeoutAction`, `TimeoutHours`)
- `sf-quality-db/database/migrations/097_create_pending_transition_lifecycle.sql` (`workflow.PendingApprovalTransition` has `Expired` status but no timeout scheduler)
- `sf-quality-db/database/migrations/062_approval_escalation_sps.sql` (`workflow.usp_EvaluateEscalationRules` for batch escalation rules)

**Classification:** Strengthen Existing
**Rationale:** Timeout intent exists at chain level, but pending-approval rows are not automatically evaluated/resolved by timeout action.

**Recommended strengthening:** Add pending-expiry timestamps plus a scheduled processor (`workflow.usp_ProcessPendingApprovalTimeouts`) that applies chain timeout policy deterministically.

---

#### 4. Temporal Data Model and Point-in-Time Querying
**Reference JSON paths:**
- `Platform_System_Architecture_Technical_Patterns.json: $.data_architecture_patterns.temporal_data_model`
- `API_Integration_Architecture_Agnostic.json: $.api_interaction_patterns.point_in_time_queries.description`
- `Security_Role_Architecture_Agnostic.json: $.cross_cutting_patterns.effective_dating.description`

**Code evidence:**
- `sf-quality-db/database/migrations/024_document_infrastructure.sql` (temporal tables including `dbo.Document`, `dbo.RecordRetentionPolicy`)
- `sf-quality-db/database/migrations/028_ncr_tables.sql` and `sf-quality-db/database/migrations/046_workflow_state_machine.sql` (entity and workflow temporal modeling)
- `sf-quality-db/database/migrations/048_status_tracking_tables.sql` (`workflow.StatusHistory`, recency indexing)

**Classification:** Strengthen Existing
**Rationale:** Temporal modeling is pervasive, but point-in-time query semantics are not consistently exposed through API-facing procedures/views.

**Recommended strengthening:** Add optional `@AsOfUtc` parameters to key read procedures and route through `FOR SYSTEM_TIME AS OF` for deterministic historical views.

---

#### 5. Universal Change Audit with Anomaly Detection
**Reference JSON paths:**
- `Platform_System_Architecture_Technical_Patterns.json: $.infrastructure_patterns.audit_infrastructure`
- `Security_Role_Architecture_Agnostic.json: $.user_activity_monitoring.suspicious_behavior_indicators`
- `Security_Role_Architecture_Agnostic.json: $.cross_cutting_patterns.audit_trail.description`

**Code evidence:**
- `sf-quality-db/database/migrations/003_audit_log.sql` (`audit.AuditLog`)
- `sf-quality-db/database/migrations/004_audit_trigger_utility.sql` (`dbo.usp_CreateAuditTrigger`)
- `sf-quality-db/database/migrations/057_regenerate_all_audit_triggers.sql`
- `sf-quality-db/database/migrations/120_phase16_operational_views.sql` (`quality.vw_NcrGateAudit`)

**Classification:** Strengthen Existing
**Rationale:** Auditing is strong for data mutations, but suspicious-activity detection and API-call durability are not implemented as first-class audit artifacts.

**Recommended strengthening:** Add anomaly views (`audit.vw_SuspiciousActivity`) and API call log table (`audit.ApiCallLog`) linked by correlation ID.

---

#### 6. Hierarchy-Aware Dynamic Routing for Approval Resolution
**Reference JSON paths:**
- `Workflow_Engine_Architecture_Agnostic.json: $.node_types.routing.properties.routing_targets.target_types.send_to_role_relative_to_affected_record`
- `Workflow_Engine_Architecture_Agnostic.json: $.node_types.routing.properties.routing_targets.target_types.send_to_authority_type_relative_to_affected_record.algorithm`
- `Platform_System_Architecture_Technical_Patterns.json: $.workflow_orchestration_engine.dynamic_routing_engine`
- `Hidden_Architecture_Patterns_Reverse_Engineered.json: $.pattern_3_data_staging_and_edit_mode_architecture.what_we_know_directly` (edit modes with per-field-group workflow routing)

**Code evidence:**
- `sf-quality-db/database/migrations/051_escalation_approval_tables.sql` (`workflow.ApprovalStep.ApproverRoleId` static assignment)
- `sf-quality-db/database/migrations/101_add_authority_constraint_tables.sql` (`dbo.DispositionAuthorityRule`)
- `sf-quality-db/database/migrations/099_harden_approval_sps.sql` (approval processing against configured role/permission)

**Classification:** Net New
**Rationale:** Runtime hierarchy walk and early-termination recipient discovery are not implemented; approval routing is configured statically. The hidden data staging pattern reveals the reference platform uses "edit modes" where different field groups on the same entity trigger different approval workflows (e.g., severity reclassification routes to Director; containment updates route to Manager). Our current model routes all modifications in a given state through the same approval chain.

**Recommended approach:** Add a resolver procedure (for example `workflow.usp_ResolveApprovers`) and optional dynamic-routing mode on `workflow.ApprovalStep`. Additionally, extend `GuardExpression` syntax on `workflow.WorkflowTransition` to support field-change detection (e.g., severity changed → route to Director chain, default → route to Manager chain). This achieves the hidden pattern's edit-mode concept without a separate field-group framework — high-impact field changes trigger different approval chains via guard conditions on existing transitions.

---

#### 7. Self-Approval Prevention
**Reference JSON paths:**
- `Workflow_Engine_Architecture_Agnostic.json: $.security_considerations.self_approval_prevention.description`
- `Security_Role_Architecture_Agnostic.json: $.workflow_driven_approvals.security_hardening`

**Code evidence:**
- `sf-quality-db/database/migrations/099_harden_approval_sps.sql` (`workflow.usp_ProcessApprovalStep` enforces SoD; throws `50413`)
- `sf-quality-db/database/migrations/095_backfill_approval_escalation_permissions.sql` (`DecisionGlobal` constraint path used by SoD logic)

**Classification:** Strengthen Existing
**Rationale:** Core SoD guard exists; remaining work is coverage assurance across all approval paths and future entities.

**Recommended strengthening:** Centralize self-approval checks in shared approval helper logic and add regression tests for all approval-gated transitions.

---

#### 8. Event-Driven Workflow Chaining + Outbox Generalization
**Reference JSON paths:**
- `Workflow_Engine_Architecture_Agnostic.json: $.event_system.description`
- `Workflow_Engine_Architecture_Agnostic.json: $.common_workflow_patterns.event_chained_processing.description`
- `Platform_System_Architecture_Technical_Patterns.json: $.workflow_orchestration_engine.event_chaining`
- `API_Integration_Architecture_Agnostic.json: $.event_and_notification_system.description`

**Code evidence:**
- `sf-quality-db/database/migrations/033_quality_event_link.sql` (`quality.QualityEventLink`)
- `sf-quality-db/database/migrations/119_phase16_integration_schema_ack_table.sql` (`integration.NcrNotificationAck`)
- `sf-quality-db/database/migrations/121_phase16_outbox_view_and_sps.sql` (`quality.vw_NcrNotificationOutbox`, `integration.usp_GetPendingNotifications`, `integration.usp_AcknowledgeNcrOutboxEvent`)

**Classification:** Strengthen Existing
**Rationale:** Outbox/pull-ack pattern is implemented for NCR transitions, but generalized cross-entity chaining/event subscription is not.

**Recommended strengthening:** Extend outbox to CAPA/SCAR/Complaint/Audit and add internal event-subscription metadata for automatic workflow chaining.

---

### MEDIUM IMPACT

#### 9. Dual-Key Identity Pattern (Internal Surrogate + External Reference)
**Reference JSON paths:**
- `Platform_System_Architecture_Technical_Patterns.json: $.data_architecture_patterns.entity_identity_pattern`
- `API_Integration_Architecture_Agnostic.json: $.architectural_summary.entity_identification`

**Code evidence:**
- `sf-quality-db/database/migrations/008_document_numbering.sql` (`dbo.usp_GenerateDocumentNumber`)
- `sf-quality-db/database/migrations/106_add_ncr_external_reference_bridge.sql` (`quality.NcrExternalReference`)
- `sf-quality-api/src/SfQualityApi/Endpoints/NcrEndpoints.cs` (routes and `Created` responses use internal `int` ids)

**Classification:** Strengthen Existing
**Rationale:** Surrogate + external identity exists in DB, but API currently exposes internal integer IDs as primary route identifiers.

**Recommended strengthening:** Add lookup/index strategy around external document identifiers and move API routes to external keys for integration-facing contracts.

---

#### 10. Codebook / Reference Data Pattern
**Reference JSON paths:**
- `Platform_System_Architecture_Technical_Patterns.json: $.data_architecture_patterns.reference_data_pattern`
- `Security_Role_Architecture_Agnostic.json: $.cross_cutting_patterns.reference_codes.description`

**Code evidence:**
- `sf-quality-db/database/migrations/013_lookup_tables.sql` (`dbo.LookupCategory`, `dbo.LookupValue`)
- `sf-quality-db/database/migrations/014_aiag_scales.sql`
- `sf-quality-db/database/migrations/015_quality_reference_tables.sql`
- `sf-quality-db/database/migrations/081_promote_lookupvalue_tier1.sql`

**Classification:** Strengthen Existing
**Rationale:** Reference-data model is broad and mature, but consumption patterns are still mixed between generic and entity-specific lookup reads.

**Recommended strengthening:** Publish canonical lookup views/procs per domain and enforce consistent code-based API contracts.

---

#### 11. Workflow Definition Immutability / Versioned Lifecycle
**Reference JSON paths:**
- `Workflow_Engine_Architecture_Agnostic.json: $.workflow_lifecycle.states.active.description`
- `Workflow_Engine_Architecture_Agnostic.json: $.security_considerations.immutability_protection.description`
- `Platform_System_Architecture_Technical_Patterns.json: $.workflow_orchestration_engine.immutability_pattern`

**Code evidence:**
- `sf-quality-db/database/migrations/046_workflow_state_machine.sql` (workflow metadata tables)
- `sf-quality-db/database/migrations/047_seed_workflow_processes.sql` (workflow seeds and transitions)

**Classification:** Strengthen Existing
**Rationale:** Workflow definitions are effectively controlled through migrations, but there is no explicit runtime lifecycle state model for draft/active/system versions.

**Recommended strengthening:** Add versioned workflow metadata with explicit activation windows and immutable-after-activation enforcement.

---

#### 12. SLA Enforcement with Configurable Timeout
**Reference JSON paths:**
- `Platform_System_Architecture_Technical_Patterns.json: $.workflow_orchestration_engine.execution_model`
- `Workflow_Engine_Architecture_Agnostic.json: $.timeout_and_auto_resolution.description`
- `Hidden_Architecture_Patterns_Reverse_Engineered.json: $.pattern_2_policy_resolution_engine` (policy resolution as the mechanism that determines which SLA/timeline applies)

**Code evidence:**
- `sf-quality-db/database/migrations/046_workflow_state_machine.sql` (`workflow.SlaConfiguration`, transition SLA columns)
- `sf-quality-db/database/migrations/062_approval_escalation_sps.sql` (`workflow.usp_EvaluateEscalationRules`)
- `sf-quality-db/database/migrations/120_phase16_operational_views.sql` (`quality.vw_NcrHoldAging`, `quality.vw_NcrCustomerApprovalAging`)
- `sf-quality-db/database/migrations/104_customer_quality_rules.sql` (`dbo.CustomerQualityRule` with `NotificationSlaTierId`, `NotificationSlaHours` — effective-dated, priority-ranked SLA rule resolution)

**Classification:** Strengthen Existing
**Rationale:** SLA metadata and breach analytics exist; direct SLA-to-action execution is partial and not uniformly automated. The hidden policy resolution pattern reveals that the reference platform uses a generalized policy resolution engine (identify candidates → filter by scope → resolve conflicts by priority → return effective policy) to determine which SLA/timeline applies. Our `workflow.SlaConfiguration` and `dbo.CustomerQualityRule` already implement this resolution pattern with effective dating and priority ranking — confirming our architecture aligns with the reference platform's deeper engineering. The gap is activation: `SlaConfiguration` is schema-ready for CAPA entities (Decision #15) but not yet seeded with CAPA-specific timelines.

**Recommended strengthening:** Standardize SLA clock computation and wire SLA breach outcomes to deterministic escalation/timeout handlers. Seed `workflow.SlaConfiguration` with CAPA-specific entries (30-day Critical, 60-day Major, 90-day Minor) and wire `workflow.usp_EvaluateEscalationRules` to evaluate CAPA entities. Add `quality.vw_CapaTimelineCompliance` dashboard view. Consider adding `security.vw_EffectivePolicyMap` diagnostic view that surfaces all active CustomerQualityRules + SlaConfigurations + EscalationRules for a given entity and evaluation date — useful for configuration validation and governance audit.

---

#### 13. Post-Approval Notification Queue
**Reference JSON paths:**
- `Workflow_Engine_Architecture_Agnostic.json: $.security_considerations.post_approval_notification.description`
- `Workflow_Engine_Architecture_Agnostic.json: $.node_types.notification.purpose`

**Code evidence:**
- `sf-quality-db/database/migrations/121_phase16_outbox_view_and_sps.sql` (integration outbox is external-consumer oriented)
- `sf-quality-db/database/migrations/098_harden_workflow_transition_sp.sql` and `sf-quality-db/database/migrations/099_harden_approval_sps.sql` (no internal `workflow.NotificationQueue` writes)

**Classification:** Net New
**Rationale:** External notification outbox exists, but there is no internal user notification queue for approval outcomes and owner alerts.

**Recommended approach:** Add `workflow.NotificationQueue` and write hooks in transition/approval procedures.

---

#### 14. Validate-Only / Dry-Run Mode
**Reference JSON paths:**
- `Platform_System_Architecture_Technical_Patterns.json: $.api_design_patterns.validate_only_mode`
- `API_Integration_Architecture_Agnostic.json: $.api_interaction_patterns.write_operations.validate_only_mode.description`
- `Hidden_Architecture_Patterns_Reverse_Engineered.json: $.pattern_3_data_staging_and_edit_mode_architecture.what_we_know_directly` (IsValidateOnly as part of the broader staging architecture)

**Code evidence:**
- `sf-quality-db/database/migrations/112_gate_create_submit.sql` (`quality.usp_CreateNcrQuick`, `quality.usp_SubmitNcr`)
- `sf-quality-db/database/migrations/115_gate_verify_close_void.sql` (`quality.usp_CloseNcr`)
- `sf-quality-db/database/migrations/058_crud_ncr_capa.sql` (`quality.usp_UpdateNCR`)

**Classification:** Net New
**Rationale:** Write procedures do not expose a validate-only switch; all calls are commit paths. The hidden data staging pattern reveals that in the reference platform, validate-only operates against a staging layer — validating the full business rule pipeline without committing. In our architecture (no staging layer, Draft-state edits on live tables), validate-only is implemented as a transaction that executes all validation then rolls back, returning the validation resultset. Same outcome, different mechanism.

**Recommended approach:** Add `@IsValidateOnly BIT = 0` to write procedures and return validation resultsets after rollback in validation mode.

---

#### 15. Configuration Portability (Export/Import)
**Reference JSON paths:**
- `Platform_System_Architecture_Technical_Patterns.json: $.infrastructure_patterns.configuration_portability`
- `Security_Role_Architecture_Agnostic.json: $.configuration_portability.description`

**Code evidence:**
- `sf-quality-db/database/migrations/091_create_security_catalog.sql` and `sf-quality-db/database/migrations/092_seed_workflow_permissions_features.sql` (security config exists in schema)
- `sf-quality-db/.planning/contracts/db-contract-manifest.json` (no export/import contract procedures for role/security portability)

**Classification:** Net New
**Rationale:** Configuration model exists, but no SQL-first portability pipeline is implemented for environment promotion.

**Recommended approach:** Implement manifest-based export/import procedures with upsert-only semantics and contract-level validation.

---

#### 16. Data Lifecycle Management (Retention + Purging)
**Reference JSON paths:**
- `Platform_System_Architecture_Technical_Patterns.json: $.infrastructure_patterns.data_lifecycle_management`

**Code evidence:**
- `sf-quality-db/database/migrations/024_document_infrastructure.sql` (`dbo.RecordRetentionPolicy` temporal table; `HISTORY_RETENTION_PERIOD = 7 YEARS` on temporal history tables)
- `sf-quality-db/database/migrations/025_seed_document_reference.sql` (seeded retention policies by entity)

**Classification:** Strengthen Existing
**Rationale:** Retention policy metadata is implemented and temporal tables auto-purge history older than 7 years via `HISTORY_RETENTION_PERIOD`. However, business-level record archival (e.g., archiving closed NCRs older than the configured retention period, purging audit data beyond regulatory minimums) is not implemented as operational jobs.

**Recommended strengthening:** Add policy-driven archive/purge procedures that evaluate `dbo.RecordRetentionPolicy` rules against live data and execute with purge audit logs.

---

#### 17. Asynchronous Background Job Processing
**Reference JSON paths:**
- `Platform_System_Architecture_Technical_Patterns.json: $.infrastructure_patterns.background_job_processing`

**Code evidence:**
- `sf-quality-db/database/migrations/062_approval_escalation_sps.sql` (`workflow.usp_EvaluateEscalationRules` designed for Azure Automation)
- `sf-quality-db/database/migrations/064_rootcause_effectiveness_sps.sql` (`quality.usp_ScheduleEffectivenessChecks`)

**Classification:** Strengthen Existing
**Rationale:** Batch procedures exist, but scheduler contract, retries, and run telemetry are not standardized.

**Recommended strengthening:** Introduce job-run logging, idempotency keys, and documented Azure scheduler orchestration per job class.

---

#### 18. Composite Aggregate Root with Sub-Resource Collections
**Reference JSON paths:**
- `Platform_System_Architecture_Technical_Patterns.json: $.data_architecture_patterns.composite_aggregate_pattern`
- `Platform_System_Architecture_Technical_Patterns.json: $.data_architecture_patterns.composite_aggregate_pattern.access_patterns`

**Code evidence:**
- `sf-quality-db/database/migrations/028_ncr_tables.sql` (`quality.NonConformanceReport` as aggregate root, `quality.NcrContainmentAction` as subordinate)
- `sf-quality-db/database/migrations/032_document_junctions.sql` (6 document junction tables linking aggregate roots to documents)
- `sf-quality-db/database/migrations/033_quality_event_link.sql` (`quality.QualityEventLink` linking entities)
- `sf-quality-api/src/SfQualityApi/Endpoints/NcrEndpoints.cs` (sub-resource routes: `/ncr/{id}/containment`, `/ncr/{id}/documents`, `/ncr/{id}/notes`, `/ncr/{id}/disposition`, `/ncr/{id}/linked-entities`)

**Classification:** Strengthen Existing
**Rationale:** The NCR is an aggregate root with 5+ subordinate collections (containment actions, documents, notes, dispositions, linked entities). Sub-resource API routes exist. However, selective expansion semantics (lazy vs. eager loading of subordinate collections) are not formalized — all sub-resources require separate API calls with no `Expand` parameter on the root endpoint.

**Recommended strengthening:** Add an optional `expand` query parameter to the NCR detail endpoint (once `GET /ncr/{id}` is implemented) to allow callers to request specific subordinate collections in a single round-trip. Define the canonical aggregate shape in the API contract.

---

#### 19. Multi-Party Entity Lifecycle Tracking
**Reference JSON paths:**
- `Hidden_Architecture_Patterns_Reverse_Engineered.json: $.pattern_3_data_staging_and_edit_mode_architecture.what_we_can_infer.multi_party_staging`
- `Hidden_Architecture_Patterns_Reverse_Engineered.json: $.pattern_3_data_staging_and_edit_mode_architecture.what_we_can_infer.relevance_to_quality_management` (SCAR cross-organizational staging)

**Code evidence:**
- `sf-quality-db/database/migrations/031_scar_complaint_audit_tables.sql` (`quality.SupplierCar` with `IssuedById`, `VerifiedById`, `ClosedById` — different users per phase, but single linear `StatusCodeId`)
- `sf-quality-db/database/migrations/048_status_tracking_tables.sql` (`workflow.StatusHistory` shared across entity types — no per-party status separation)
- `sf-quality-db/database/migrations/061_workflow_transition_sp.sql` (`workflow.usp_TransitionState` operates on single entity status, no per-party state)

**Classification:** Net New
**Rationale:** SCAR (Supplier Corrective Action Request) is inherently a cross-organizational process: the issuing team defines the defect description and requirements, then waits for the supplier's root cause analysis and corrective action plan (entered by the internal team on the supplier's behalf). Currently, SCAR tracks a single linear status (`StatusCodeId`), which cannot represent "customer portion complete, awaiting supplier response." The hidden data staging pattern reveals the reference platform uses per-party state machines where each party has independent status tracking and the record only completes when all parties reach their terminal states. For sf-quality, the parties are tracked as workflow metadata (not external portal users) — the internal quality team manages both sides, but needs to track whose deliverable is pending.

**Recommended approach:** Add `CustomerResponseStatus TINYINT` and `SupplierResponseStatus TINYINT` columns to `quality.SupplierCar` with independent state enums (Customer: Issued/PendingSupplierResponse/SupplierResponded/Verified; Supplier: NotReceived/InProgress/Submitted/RevisionRequested). Add `quality.ScarPartyStatusHistory` table for per-party audit trail. Derive SCAR overall status from combined party states. Add `quality.vw_ScarPartyStatus` for dashboard/queue queries filtering by which party's action is pending.

---

#### 20. Optimistic Commit Mode for Safety-Critical Transitions
**Reference JSON paths:**
- `Hidden_Architecture_Patterns_Reverse_Engineered.json: $.pattern_3_data_staging_and_edit_mode_architecture.what_we_can_infer.presave_vs_approved_commit_patterns`
- `Hidden_Architecture_Patterns_Reverse_Engineered.json: $.pattern_3_data_staging_and_edit_mode_architecture.what_we_can_infer.relevance_to_quality_management` (containment action with immediate visibility)
- `Workflow_Engine_Architecture_Agnostic.json: $.node_types.process.properties.function_parameters` (Presave mode)

**Code evidence:**
- `sf-quality-db/database/migrations/097_create_pending_transition_lifecycle.sql` (`workflow.PendingApprovalTransition` — approval lifecycle tracking exists, but all transitions are sequential: request → approve → apply)
- `sf-quality-db/database/migrations/098_harden_workflow_transition_sp.sql` (`workflow.usp_TransitionState` — state changes only execute after approval completion, no pre-commit path)
- `sf-quality-db/database/migrations/099_harden_approval_sps.sql` (`workflow.usp_ApplyApprovedTransition` with stale-state protection)

**Classification:** Net New
**Rationale:** Current workflow transitions follow a pessimistic pattern: request → approve → apply. Data only becomes visible to other users after the approval chain completes. The hidden data staging pattern reveals the reference platform supports a Presave (optimistic) mode where data commits immediately and approval runs in parallel. For quality management, this directly applies to containment actions: when a defect is found on the production line, quarantine instructions and sort orders must be visible to production supervisors immediately, not after the Quality Manager completes a formal approval. The current architecture forces containment visibility to wait for the approval chain.

**Recommended approach:** Add `IsPresave BIT DEFAULT 0` to `workflow.WorkflowTransition`. When a Presave transition fires, `workflow.usp_TransitionState` applies the entity state change immediately AND creates a `PendingApprovalTransition` with Status='Pending' for formal review. If the pending approval is later rejected, a compensating transition reverses the entity to its prior state (new status: 'Compensated' on PendingApprovalTransition). Initial use: containment action transitions where production visibility is safety-critical.

---

### LOWER IMPACT

#### 21. Organizational Scoping with Multi-Level Hierarchy
**Reference JSON paths:**
- `Security_Role_Architecture_Agnostic.json: $.organizational_scoping.security_implications`
- `Security_Role_Architecture_Agnostic.json: $.data_authorization.scope_models`

**Code evidence:**
- `sf-quality-db/database/migrations/005_security_tables.sql` (`RoleTier`, `UserRole` + `PlantId` assignment)
- `sf-quality-db/database/migrations/006_rls_predicates.sql` and phase expansions (`026`, `035`, `044`, `053`, `079`)

**Classification:** Strengthen Existing
**Rationale:** Plant-level scoping is strong; full configurable multi-level org hierarchy entities are not part of the current single-tenant implementation.

**Recommended strengthening:** Keep current model unless business needs exceed plant scope; then add explicit org-unit hierarchy with migration-safe rollout.

---

#### 22. Tree Data Structures (Adjacency List Standardization)
**Reference JSON paths:**
- `Platform_System_Architecture_Technical_Patterns.json: $.data_architecture_patterns.tree_data_structures`

**Code evidence:**
- `sf-quality-db/database/migrations/015_quality_reference_tables.sql` (`dbo.DefectType.ParentDefectTypeId`)
- `sf-quality-db/database/migrations/030_rootcause_effectiveness.sql` (`dbo.RootCause.ParentRootCauseId`)
- `sf-quality-db/database/migrations/038_fishbone_tables.sql` (`rca.FishboneCause.ParentCauseId`)
- `sf-quality-db/database/migrations/091_create_security_catalog.sql` (`security.Feature.ParentFeatureId`)

**Classification:** Strengthen Existing
**Rationale:** Multiple adjacency-list trees are implemented; traversal/validation patterns are duplicated and not standardized.

**Recommended strengthening:** Add shared hierarchy traversal helpers and cycle-detection checks for all parent-child structures.

---

#### 23. Document Storage Pattern
**Reference JSON paths:**
- `Platform_System_Architecture_Technical_Patterns.json: $.data_architecture_patterns.document_storage_pattern`
- `API_Integration_Architecture_Agnostic.json: $.data_model_topology.core_entities.document.description`

**Code evidence:**
- `sf-quality-db/database/migrations/024_document_infrastructure.sql` (`dbo.Document` uses `StorageProvider` + `StorageReference`)
- `sf-quality-db/database/migrations/032_document_junctions.sql`
- `sf-quality-db/database/migrations/066_traceability_document_sps.sql`

**Classification:** Strengthen Existing
**Rationale:** Document management exists, but current model is metadata + external storage reference, not in-database BLOB + API base64 payloads.

**Recommended strengthening:** Formalize/document the selected storage contract (reference-based vs BLOB path) and enforce it consistently through API endpoints.

---

#### 24. Bulk Import/Export Framework
**Reference JSON paths:**
- `Platform_System_Architecture_Technical_Patterns.json: $.infrastructure_patterns.import_export_framework`
- `Security_Role_Architecture_Agnostic.json: $.cross_cutting_patterns.import_export_pattern`

**Code evidence:**
- `sf-quality-db/database/migrations/013_lookup_tables.sql` (lookup categories/values seeded via migrations only)
- `sf-quality-db/database/migrations/015_quality_reference_tables.sql` (18 reference tables seeded via migrations only)
- `sf-quality-db/database/migrations/125_defect_knowledge_schema.sql` through `sf-quality-db/database/migrations/127_liquid_paint_containment.sql` (knowledge base seeded via migrations; no runtime import path)

**Classification:** Net New
**Rationale:** All reference data and knowledge base entries are loaded through migrations. No runtime bulk import procedures exist for administrative data (defect types, suppliers, lookup values, knowledge entries). The reference architecture describes CSV-based import with header-locked schemas and upsert-only semantics — directly applicable to quality system administrative data that plant engineers need to maintain without developer intervention.

**Recommended approach:** Add bulk import procedures with CSV-compatible parameter patterns and upsert semantics for high-churn reference entities (lookup values, defect types, knowledge base entries). Include validation resultsets with row-level error reporting.

---

## sf-quality-api

### HIGH IMPACT

#### 1. API Security Boundary with Feature Gating
**Reference JSON paths:**
- `API_Integration_Architecture_Agnostic.json: $.security_framework_at_api_boundary.description`
- `API_Integration_Architecture_Agnostic.json: $.authentication_and_authorization.authorization_model.description`
- `Security_Role_Architecture_Agnostic.json: $.api_and_integration_security.field_level_api_access.description`

**Code evidence:**
- `sf-quality-api/src/SfQualityApi/Auth/EasyAuthHandler.cs`
- `sf-quality-api/src/SfQualityApi/Program.cs` (`AddAuthentication`, `AddAuthorization`)
- `sf-quality-api/src/SfQualityApi/Endpoints/NcrEndpoints.cs` (`RequireAuthorization()`)
- `sf-quality-api/src/SfQualityApi/Infrastructure/DbConnectionFactory.cs` (calls `dbo.usp_SetSessionContext` before returning connection)

**Classification:** Strengthen Existing
**Rationale:** Auth-to-session-context-to-RLS chain is implemented; API-specific field-level projection and integration account patterns are not yet surfaced in API routes.

**Recommended strengthening:** Add integration-specific endpoint paths and explicit field-level filtering strategy for API consumers where required.

---

#### 2. Deterministic Business Error Contract Mapping
**Reference JSON paths:**
- `API_Integration_Architecture_Agnostic.json: $.architecture_overview.core_architectural_decisions`
- `Platform_System_Architecture_Technical_Patterns.json: $.api_design_patterns.resource_oriented_design`

**Code evidence:**
- `sf-quality-api/src/SfQualityApi/Infrastructure/SqlErrorMapper.cs` (explicit `504xx` and `52xxx` mappings)
- `sf-quality-api/src/SfQualityApi/Middleware/ErrorHandlingMiddleware.cs` (mapped SQL exceptions -> deterministic HTTP status)

**Classification:** Strengthen Existing
**Rationale:** Error mapping is strong and explicit; governance still depends on manual mapping maintenance for new DB error codes.

**Recommended strengthening:** Add automated cross-check that DB manifested error-code ranges are fully mapped in API.

---

#### 3. Delta Synchronization Pattern (Change Data Capture)
**Reference JSON paths:**
- `Platform_System_Architecture_Technical_Patterns.json: $.api_design_patterns.delta_sync_pattern`
- `API_Integration_Architecture_Agnostic.json: $.api_interaction_patterns.delta_synchronization.description`

**Code evidence:**
- `sf-quality-api/src/SfQualityApi/Endpoints/NcrEndpoints.cs` (list endpoints `/ncr/summary`, `/ncr/queue`, `/ncr/pareto`, etc., no updated-window parameters)
- `sf-quality-api/.planning/phases/10-integration-deployment/10-CONTEXT.md` (integration endpoint phase planned, not implemented)

**Classification:** Net New
**Rationale:** API has summary/list reads but no change-window filtering contract.

**Recommended approach:** Add `updatedStartUtc`/`updatedEndUtc` filters to integration-grade reads and back with indexed DB predicates.

---

#### 4. Persistent API Audit Trail with Correlation
**Reference JSON paths:**
- `Platform_System_Architecture_Technical_Patterns.json: $.infrastructure_patterns.audit_infrastructure`
- `API_Integration_Architecture_Agnostic.json: $.security_framework_at_api_boundary.auditing`

**Code evidence:**
- `sf-quality-api/src/SfQualityApi/Middleware/CorrelationIdMiddleware.cs` (header propagation + log context)
- `sf-quality-api/src/SfQualityApi/Middleware/ErrorHandlingMiddleware.cs` (error log + response correlation)
- No API middleware writes to DB audit table (`audit.ApiCallLog` not present)

**Classification:** Net New
**Rationale:** Correlation exists, but durable API call audit records are not persisted.

**Recommended approach:** Add DB-backed API call logging middleware with route, caller OID, status, duration, and correlation ID.

---

### MEDIUM IMPACT

#### 5. Symmetric Read-Write Payload Design
**Reference JSON paths:**
- `Platform_System_Architecture_Technical_Patterns.json: $.api_design_patterns.symmetric_payload_design`
- `API_Integration_Architecture_Agnostic.json: $.api_interaction_patterns.write_operations.symmetric_payloads`

**Code evidence:**
- `sf-quality-api/src/SfQualityApi/Endpoints/NcrEndpoints.cs` (request DTOs exist; no `GET /ncr/{id}` detail endpoint)
- `sf-quality-api/.planning/contracts/api-openapi.publish.json` (create/update/delete and view routes; no canonical detail payload route)

**Classification:** Strengthen Existing
**Rationale:** Write DTOs are defined, but round-trip read/write schema symmetry is incomplete without canonical detail retrieval.

**Recommended strengthening:** Add `GET /ncr/{id}` with the same canonical shape used by create/update contracts.

---

#### 6. Rate Limiting
**Reference JSON paths:**
- `Platform_System_Architecture_Technical_Patterns.json: $.api_design_patterns.rate_limiting`
- `API_Integration_Architecture_Agnostic.json: $.rate_limiting.description`

**Code evidence:**
- `sf-quality-api/src/SfQualityApi/Program.cs` (no `AddRateLimiter`/`UseRateLimiter`)

**Classification:** Net New
**Rationale:** No API throttling policy is configured.

**Recommended approach:** Add ASP.NET rate limiter policies (integration endpoints first), keyed by consumer identity and aligned to single-tenant operational targets.

---

#### 7. Cursor-Based Pagination
**Reference JSON paths:**
- `Platform_System_Architecture_Technical_Patterns.json: $.api_design_patterns.cursor_based_pagination`
- `API_Integration_Architecture_Agnostic.json: $.api_interaction_patterns.paging.description`

**Code evidence:**
- `sf-quality-api/src/SfQualityApi/Endpoints/NcrEndpoints.cs` (no `PageSize`/continuation token parameters)
- `sf-quality-api/.planning/contracts/api-openapi.publish.json` (no paging schema)

**Classification:** Net New
**Rationale:** Large-list endpoints are unpaged.

**Recommended approach:** Add cursor-based paging contracts and keyset-backed DB query support for high-volume reads.

---

#### 8. URL Versioning
**Reference JSON paths:**
- `API_Integration_Architecture_Agnostic.json: $.url_architecture.pattern`
- `API_Integration_Architecture_Agnostic.json: $.url_architecture.segments.version`

**Code evidence:**
- `sf-quality-api/src/SfQualityApi/Endpoints/NcrEndpoints.cs` (`/ncr` base route)
- `sf-quality-api/src/SfQualityApi/Endpoints/DiagnosticEndpoints.cs` (`/diagnostics`)
- `sf-quality-api/.planning/contracts/api-openapi.publish.json` (unversioned paths)

**Classification:** Net New
**Rationale:** API contract versioning is SemVer at artifact level, but route surface is unversioned.

**Recommended approach:** Introduce route prefix (`/v1`) before external integration onboarding.

---

#### 9. Validate-Only Mode on Write Endpoints
**Reference JSON paths:**
- `Platform_System_Architecture_Technical_Patterns.json: $.api_design_patterns.validate_only_mode`
- `API_Integration_Architecture_Agnostic.json: $.api_interaction_patterns.write_operations.validate_only_mode.description`
- `Hidden_Architecture_Patterns_Reverse_Engineered.json: $.pattern_3_data_staging_and_edit_mode_architecture.what_we_know_directly` (validate-only as part of staging architecture; in our case implemented via transaction rollback)

**Code evidence:**
- `sf-quality-api/src/SfQualityApi/Endpoints/NcrEndpoints.cs` (write handlers have no `isValidateOnly` option)

**Classification:** Net New
**Rationale:** API writes always execute commit semantics. The hidden data staging pattern confirms this is a core pattern in the reference platform, used for form preflight validation in the staging context. In our architecture, the API would pass `isValidateOnly` through to DB procedures that execute full validation then roll back.

**Recommended approach:** Add `isValidateOnly` query option and pass through to DB write procedures once DB support is added (see db #14).

---

#### 10. Query Governor Pattern
**Reference JSON paths:**
- `Platform_System_Architecture_Technical_Patterns.json: $.api_design_patterns.query_governor_pattern`
- `API_Integration_Architecture_Agnostic.json: $.api_interaction_patterns.batch_retrieval_for_large_datasets.query_governor.limit`

**Code evidence:**
- `sf-quality-api/src/SfQualityApi/Endpoints/NcrEndpoints.cs` (collection endpoints can return full result sets)

**Classification:** Net New
**Rationale:** Request-level max-row enforcement is absent.

**Recommended approach:** Enforce maximum rows per request and return deterministic governor errors with batching guidance.

---

#### 11. Two-Phase Retrieval (Discovery Then Detail)
**Reference JSON paths:**
- `Platform_System_Architecture_Technical_Patterns.json: $.api_design_patterns.two_phase_retrieval`
- `API_Integration_Architecture_Agnostic.json: $.api_interaction_patterns.two_step_retrieval.description`

**Code evidence:**
- `sf-quality-api/src/SfQualityApi/Endpoints/NcrEndpoints.cs` (no lightweight discovery endpoint returning external identifiers)
- `sf-quality-api/.planning/contracts/api-openapi.publish.json` (no dedicated discovery/detail pairing by external key)

**Classification:** Net New
**Rationale:** Current API is direct-operation oriented rather than explicit two-phase discovery/detail retrieval.

**Recommended approach:** Add discovery endpoints returning external NCR references, then detail endpoints keyed by that reference.

---

### LOWER IMPACT

#### 12. Consumer-Generated Identity for Idempotent Creates
**Reference JSON paths:**
- `Platform_System_Architecture_Technical_Patterns.json: $.api_design_patterns.consumer_generated_identity`
- `API_Integration_Architecture_Agnostic.json: $.api_interaction_patterns.write_operations.post.xrefcode_ownership`

**Code evidence:**
- `sf-quality-api/src/SfQualityApi/Endpoints/NcrEndpoints.cs` (`CreateNcrQuick`, `CreateNcr` use DB-generated IDs)
- `sf-quality-db/database/migrations/008_document_numbering.sql` (server-generated document numbering)

**Classification:** Inform Planning
**Rationale:** Useful for future integration idempotency, but not required for the current user-facing NCR lifecycle surface.

**Recommended planning note:** Introduce optional `ClientRequestId`/external reference uniqueness when integration endpoints are delivered.

---

## sf-quality-app

All app patterns remain **Inform Planning** because there is no runtime app source yet; evidence is in planning/contracts/governance artifacts.

### HIGH IMPACT

#### 1. Feature Tree / UI Entitlement System
**Reference JSON paths:**
- `Security_Role_Architecture_Agnostic.json: $.feature_access_control.description`
- `Security_Role_Architecture_Agnostic.json: $.feature_access_control.feature_parameterization.description`

**Code evidence:**
- `sf-quality-app/.planning/REQUIREMENTS.md` (`APP-WORKFLOW-02`)
- `sf-quality-app/.planning/PROJECT.md` (contract-governed workflow execution)
- `sf-quality-app/.planning/decisions/ADR-0001-frontend-platform-auth-boundary.md`

**Classification:** Inform Planning
**Rationale:** UI entitlement architecture is required but not yet implemented.

---

#### 2. Organizational Scope Filtering in UI
**Reference JSON paths:**
- `Security_Role_Architecture_Agnostic.json: $.organizational_scoping.security_implications`
- `Security_Role_Architecture_Agnostic.json: $.data_authorization.scope_models`

**Code evidence:**
- `sf-quality-app/.planning/REQUIREMENTS.md` (workflow views must remain API/DB-authoritative)
- `sf-quality-app/.planning/codebase/ARCHITECTURE.md` (delegated token forwarding to API)

**Classification:** Inform Planning
**Rationale:** UI scope affordances are required to align with DB-enforced RLS, but frontend code is not started.

---

#### 3. Workflow Visualization and Gate Navigation
**Reference JSON paths:**
- `Workflow_Engine_Architecture_Agnostic.json: $.common_workflow_patterns.single_level_approval.description`
- `Workflow_Engine_Architecture_Agnostic.json: $.security_considerations.form_visibility_control.description`
- `Platform_System_Architecture_Technical_Patterns.json: $.workflow_orchestration_engine.execution_model`

**Code evidence:**
- `sf-quality-app/.planning/REQUIREMENTS.md` (`APP-WORKFLOW-01`, `APP-WORKFLOW-02`)
- `sf-quality-app/.planning/phases/05-ncr-lifecycle-experience/05-CONTEXT.md`
- `sf-quality-app/.planning/phases/07-workflow-action-approvals/07-CONTEXT.md`

**Classification:** Inform Planning
**Rationale:** Planned app workflows depend on DB/API state-machine outputs; no visual workflow implementation exists yet.

---

#### 4. Dashboard / Summary Views with Role-Scoped Parameterization
**Reference JSON paths:**
- `Security_Role_Architecture_Agnostic.json: $.feature_access_control.feature_parameterization.description`
- `API_Integration_Architecture_Agnostic.json: $.report_retrieval_architecture.description`

**Code evidence:**
- `sf-quality-app/.planning/REQUIREMENTS.md` (`APP-DASH-01`)
- `sf-quality-app/.planning/phases/09-dashboards-operational-views/09-CONTEXT.md`

**Classification:** Inform Planning
**Rationale:** Role-scoped dashboard behavior is required in roadmap, but frontend implementation is pending.

---

#### 5. Defect Knowledge Integration in Forms
**Reference JSON paths:**
- `Workflow_Engine_Architecture_Agnostic.json: $.form_binding.description`
- `Platform_System_Architecture_Technical_Patterns.json: $.data_architecture_patterns.reference_data_pattern`

**Code evidence:**
- `sf-quality-app/.planning/REQUIREMENTS.md` (`APP-KNOW-01`)
- `sf-quality-app/.planning/phases/08-knowledge-traceability-experience/08-CONTEXT.md`
- `sf-quality-db/database/migrations/128_knowledge_retrieval_layer.sql` (`quality.usp_GetDefectKnowledge` available for API exposure)

**Classification:** Inform Planning
**Rationale:** Backend knowledge retrieval exists; app-side in-form knowledge surfaces are planned only.

---

### MEDIUM IMPACT

#### 6. Notification Inbox
**Reference JSON paths:**
- `Workflow_Engine_Architecture_Agnostic.json: $.node_types.notification.purpose`
- `Platform_System_Architecture_Technical_Patterns.json: $.notification_and_event_patterns.push_pull_notification_system`

**Code evidence:**
- `sf-quality-app/.planning/REQUIREMENTS.md` (workflow/approval UX pending)
- `sf-quality-db/database/migrations/121_phase16_outbox_view_and_sps.sql` (external notification feed exists, no app inbox API yet)

**Classification:** Inform Planning
**Rationale:** Inbox UX is relevant once internal notification queue endpoints exist.

---

#### 7. Audit Trail Display
**Reference JSON paths:**
- `Platform_System_Architecture_Technical_Patterns.json: $.infrastructure_patterns.audit_infrastructure`
- `Security_Role_Architecture_Agnostic.json: $.cross_cutting_patterns.audit_trail.description`

**Code evidence:**
- `sf-quality-app/.planning/phases/08-knowledge-traceability-experience/08-CONTEXT.md`
- `sf-quality-db/database/migrations/003_audit_log.sql` and `sf-quality-db/database/migrations/120_phase16_operational_views.sql` (backend audit sources exist)

**Classification:** Inform Planning
**Rationale:** Backend audit data exists; app audit timeline components are not implemented.

---

#### 8. Server-Validated Form Preflight
**Reference JSON paths:**
- `API_Integration_Architecture_Agnostic.json: $.api_interaction_patterns.write_operations.validate_only_mode.description`
- `Platform_System_Architecture_Technical_Patterns.json: $.api_design_patterns.validate_only_mode`

**Code evidence:**
- `sf-quality-app/.planning/codebase/STACK.md` (Zod is courtesy; gate procs are authoritative)
- `sf-quality-app/.planning/REQUIREMENTS.md` (server-authoritative workflow validation)

**Classification:** Inform Planning
**Rationale:** App preflight depends on DB/API validate-only support that is not yet implemented.

---

### LOWER IMPACT

#### 9. Contract Snapshot Drift Controls
**Reference JSON paths:**
- `API_Integration_Architecture_Agnostic.json: $.architecture_overview.design_philosophy`

**Code evidence:**
- `sf-quality-api/.planning/contracts/api-openapi.publish.json` (`info.version = 0.2.0`)
- `sf-quality-app/.planning/contracts/api-openapi.snapshot.json` (`info.version = 0.1.0`)
- `sf-quality-app/scripts/Test-ApiContractReferences.ps1`
- `sf-quality-app/.github/workflows/planning-contract-validation.yml`

**Classification:** Inform Planning
**Rationale:** Drift controls exist, but the app snapshot is currently behind API publish version and still advisory pre-v1.

---

## Cross-Repo Patterns

### Contract Chain Integrity
**Reference JSON paths:**
- `API_Integration_Architecture_Agnostic.json: $.architecture_overview.core_architectural_decisions`
- `API_Integration_Architecture_Agnostic.json: $.architectural_summary`

**Code evidence:**
- `sf-quality-db/.planning/contracts/db-contract-manifest.json` (v1.0.0; 80 procedures, 36 views)
- `sf-quality-api/.planning/contracts/api-openapi.publish.json` (v0.2.0; 27 operations)
- `sf-quality-app/.planning/contracts/api-openapi.snapshot.json` (v0.1.0; 2 paths)
- `sf-quality-api/scripts/Test-DbContractReferences.ps1`, `sf-quality-api/scripts/Test-OpenApiPublication.ps1`, `sf-quality-api/scripts/Test-PlanningConsistency.ps1`
- `sf-quality-app/scripts/Test-ApiContractReferences.ps1`, `sf-quality-app/scripts/Test-PlanningConsistency.ps1`
- `sf-quality-api/.github/workflows/planning-contract-validation.yml`
- `sf-quality-app/.github/workflows/planning-contract-validation.yml`

**Classification:** Strengthen Existing
**Rationale:** Contract chain is implemented and CI-enforced, but breaking-change semantic detection and cross-repo snapshot sync are still weak.

**Recommended strengthening:** Add diff-based breaking-change checks and automated snapshot refresh workflow between API publish and app snapshot.

---

## Appendix A — Skipped Patterns (Non-Applicable to Current Constraints)

| Pattern | Reference Location | Reason for Exclusion |
|---------|--------------------|----------------------|
| Multi-tenant URL/tenant isolation architecture | `Platform_System_Architecture_Technical_Patterns.json: $.multi_tenancy_architecture`; `API_Integration_Architecture_Agnostic.json: $.architectural_summary.multi_tenancy` | System is explicitly single-tenant |
| EAV / polymorphic custom-property framework | `Platform_System_Architecture_Technical_Patterns.json: $.data_architecture_patterns.polymorphic_properties_pattern` | Fixed, strongly-typed schema is a deliberate architecture choice |
| Hybrid/fallback auth and in-app password/MFA policy engines | `Platform_System_Architecture_Technical_Patterns.json: $.identity_and_access_patterns.authentication_patterns.hybrid_authentication`; `Platform_System_Architecture_Technical_Patterns.json: $.identity_and_access_patterns.authentication_patterns.mfa_pipeline`; `Security_Role_Architecture_Agnostic.json: $.identity_and_authentication` | App Service Easy Auth boundary is the mandated runtime model |
| Secure file transfer (SFTP) hardening pattern | `Security_Role_Architecture_Agnostic.json: $.secure_file_transfer` | No SFTP channel in active repo scope |
| Legacy SOAP report/event retrieval architecture | `API_Integration_Architecture_Agnostic.json: $.legacy_soap_architecture`; `API_Integration_Architecture_Agnostic.json: $.report_retrieval_architecture.soap_paged_reports` | Current delivery scope is REST/OpenAPI only |
| Network/IP perimeter controls as primary implementation pattern | `Security_Role_Architecture_Agnostic.json: $.network_access_management` | Infra policy concern; not expressed in app/db/api repo runtime code |
| Electronic-signature workflow integration | `Workflow_Engine_Architecture_Agnostic.json: $.electronic_signature_integration` | Not in active v1 API/app scope despite schema foundations |
| Per-entity localization with language fallback | `Platform_System_Architecture_Technical_Patterns.json: $.infrastructure_patterns.localization_framework`; `Security_Role_Architecture_Agnostic.json: $.cross_cutting_patterns.localization` | Single-tenant US-based quality system; no multi-language requirement in v1 scope |
| Application-layer encryption (PGP outbound) | `Platform_System_Architecture_Technical_Patterns.json: $.infrastructure_patterns.encryption_model` | Encryption at rest handled by Azure SQL TDE; in transit by TLS. No PGP outbound integration channel in active scope |
| Two-tier guided process orchestration (conductor above workflow engine) | `Hidden_Architecture_Patterns_Reverse_Engineered.json: $.pattern_1_guided_process_orchestration.what_we_can_infer.orchestration_layer_architecture` | Solves multi-tenant self-service problem of orchestrating independent form/workflow executions. Our 8D steps are sub-entities managed by one workflow, not independent forms. Per-step state machine enhancements captured in entry #2 instead |
| Separate transactional staging store (staging tables apart from production tables) | `Hidden_Architecture_Patterns_Reverse_Engineered.json: $.pattern_3_data_staging_and_edit_mode_architecture.what_we_can_infer.staging_layer_architecture` | Single-tenant, low-concurrency quality system. Draft-state edits on live tables with PendingApprovalTransition context capture achieves equivalent UX without doubling table count. Validate-only covered by #14/#33 |
| Tenant-configurable guided process definitions with effective-dated publishing | `Hidden_Architecture_Patterns_Reverse_Engineered.json: $.pattern_1_guided_process_orchestration.what_we_know_directly` | 8D methodology is fixed per AIAG standard. Process definition changes handled by migration-based schema evolution, not runtime configuration |

---

## Summary Table (46 Patterns)

| # | Pattern | Repo | Classification | Impact |
|---|---------|------|----------------|--------|
| 1 | Defense-in-Depth Layered Authorization Pipeline | db | Strengthen Existing | High |
| 2 | Workflow Orchestration Engine with Typed Node Concepts | db | Strengthen Existing | High |
| 3 | Approval Timeout and Auto-Resolution | db | Strengthen Existing | High |
| 4 | Temporal Data Model and Point-in-Time Querying | db | Strengthen Existing | High |
| 5 | Universal Change Audit with Anomaly Detection | db | Strengthen Existing | High |
| 6 | Hierarchy-Aware Dynamic Routing for Approval Resolution | db | Net New | High |
| 7 | Self-Approval Prevention | db | Strengthen Existing | High |
| 8 | Event-Driven Workflow Chaining + Outbox Generalization | db | Strengthen Existing | High |
| 9 | Dual-Key Identity Pattern | db | Strengthen Existing | Medium |
| 10 | Codebook / Reference Data Pattern | db | Strengthen Existing | Medium |
| 11 | Workflow Definition Immutability / Versioned Lifecycle | db | Strengthen Existing | Medium |
| 12 | SLA Enforcement with Configurable Timeout | db | Strengthen Existing | Medium |
| 13 | Post-Approval Notification Queue | db | Net New | Medium |
| 14 | Validate-Only / Dry-Run Mode | db | Net New | Medium |
| 15 | Configuration Portability (Export/Import) | db | Net New | Medium |
| 16 | Data Lifecycle Management (Retention + Purging) | db | Strengthen Existing | Medium |
| 17 | Asynchronous Background Job Processing | db | Strengthen Existing | Medium |
| 18 | Composite Aggregate Root with Sub-Resource Collections | db | Strengthen Existing | Medium |
| 19 | Multi-Party Entity Lifecycle Tracking | db | Net New | Medium |
| 20 | Optimistic Commit Mode for Safety-Critical Transitions | db | Net New | Medium |
| 21 | Organizational Scoping with Multi-Level Hierarchy | db | Strengthen Existing | Lower |
| 22 | Tree Data Structures (Adjacency List Standardization) | db | Strengthen Existing | Lower |
| 23 | Document Storage Pattern | db | Strengthen Existing | Lower |
| 24 | Bulk Import/Export Framework | db | Net New | Lower |
| 25 | API Security Boundary with Feature Gating | api | Strengthen Existing | High |
| 26 | Deterministic Business Error Contract Mapping | api | Strengthen Existing | High |
| 27 | Delta Synchronization Pattern | api | Net New | High |
| 28 | Persistent API Audit Trail with Correlation | api | Net New | High |
| 29 | Symmetric Read-Write Payload Design | api | Strengthen Existing | Medium |
| 30 | Rate Limiting | api | Net New | Medium |
| 31 | Cursor-Based Pagination | api | Net New | Medium |
| 32 | URL Versioning | api | Net New | Medium |
| 33 | Validate-Only Mode on Write Endpoints | api | Net New | Medium |
| 34 | Query Governor Pattern | api | Net New | Medium |
| 35 | Two-Phase Retrieval (Discovery Then Detail) | api | Net New | Medium |
| 36 | Consumer-Generated Identity for Idempotent Creates | api | Inform Planning | Lower |
| 37 | Feature Tree / UI Entitlement System | app | Inform Planning | High |
| 38 | Organizational Scope Filtering in UI | app | Inform Planning | High |
| 39 | Workflow Visualization and Gate Navigation | app | Inform Planning | High |
| 40 | Dashboard / Summary Views with Role-Scoped Parameterization | app | Inform Planning | High |
| 41 | Defect Knowledge Integration in Forms | app | Inform Planning | High |
| 42 | Notification Inbox | app | Inform Planning | Medium |
| 43 | Audit Trail Display | app | Inform Planning | Medium |
| 44 | Server-Validated Form Preflight | app | Inform Planning | Medium |
| 45 | Contract Snapshot Drift Controls | app | Inform Planning | Lower |
| 46 | Contract Chain Integrity | cross | Strengthen Existing | Medium |
