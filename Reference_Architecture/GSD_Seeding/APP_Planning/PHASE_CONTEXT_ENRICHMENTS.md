# App Phase CONTEXT File Enrichments

**Apply to:** `sf-quality-app/.planning/phases/*/[N]-CONTEXT.md` stubs
**When:** Before running `/gsd:plan-phase N` for each phase
**Source:** Reference Architecture Execution_Plan.md Section B3, Pattern_Mapping.md #37-45

---

## Instructions

The existing App phase CONTEXT stubs contain generic cross-repo review requirements and entry/exit criteria. **Merge the following sections** into each CONTEXT file — do not replace the existing content.

Add a "## Reference Architecture Patterns" section and a "## Pattern-Derived Requirements" section to each CONTEXT file, positioned before the "Planner Generation Requirements" section.

---

## Phase 3 — Authentication Session UX

**CONTEXT file:** `phases/03-authentication-session-ux/03-CONTEXT.md`

### Reference Architecture Patterns

**Pattern #37 — Feature Entitlement Tree**
- The API exposes a feature entitlement tree via the security system (`security.Feature`, `security.Permission`, `security.usp_CheckPermission`)
- The auth session UX phase must surface this tree to the frontend — UI components should render/hide based on entitlements, not hardcoded role checks
- Source: `Platform_System_Architecture_Technical_Patterns.json: $.identity_and_access_patterns`

**Pattern #38 — Organizational Scope Filtering**
- The API's RLS model scopes all data to the authenticated user's plant(s) (`security.fn_PlantAccessPredicate`)
- The auth session phase must establish the plant-scope context in the frontend session — the currently-selected plant filter needs to be captured and forwarded to the API as part of each request context
- Source: `Security_Role_Architecture_Agnostic.json: $.data_authorization.rules`

### Pattern-Derived Requirements

- **APP-AUTH-04:** Feature entitlement tree governs UI action visibility — render/hide based on API-returned entitlements, not hardcoded checks
- **APP-AUTH-05:** Plant scope selector reflects API-authorized scope — current plant context forwarded in API requests

### Implementation Notes

- Feature entitlement tree should be fetched on session initialization via a dedicated API endpoint (API Phase 7 will expose `security.usp_CheckPermission` surface)
- Plant scope: if a user has access to multiple plants, a plant selector component is needed in the shell navigation (Phase 2 or 3)
- For Phase 3, the minimum viable deliverable is: capturing `PlantId` from the session context and forwarding it as a request header or URL parameter to all API calls

---

## Phase 4 — Lookup-Driven Forms

**CONTEXT file:** `phases/04-lookup-driven-forms/04-CONTEXT.md`

### Reference Architecture Patterns

**Pattern #44 — Form Preflight Validation**
- Write forms (NCR creation, CAPA creation, etc.) must support server-validated preflight before final submission
- The API will expose a `?isValidateOnly=true` parameter on write endpoints (API Phase 7, dependent on DB Phase 32)
- The frontend form should call the validate-only endpoint on form completion but before final submit, displaying inline server validation errors if any
- Source: `Platform_System_Architecture_Technical_Patterns.json: $.data_architecture_patterns`

### Pattern-Derived Requirements

- **APP-FORM-03:** Write forms support server-validated preflight — call `?isValidateOnly=true` before final submit, display inline server errors

### Implementation Notes

- Form preflight is a **progressive enhancement** — forms must work without it (disable the pre-submit preflight if the API endpoint doesn't yet support `isValidateOnly`)
- Recommended UX: "Review" step → call preflight → show server validation errors inline → "Confirm and Submit" button
- The form library (React Hook Form + Zod) handles client-side validation; the preflight call validates server-side business rules (e.g., "NCR cannot be created for a closed plant line")
- This pattern depends on API Phase 7 which depends on DB Phase 32 (`@IsValidateOnly` on write procs) — plan accordingly; this CONTEXT note is forward-looking for the planner

---

## Phase 7 — Workflow Actions and Approvals

**CONTEXT file:** `phases/07-workflow-action-approvals/07-CONTEXT.md`

### Reference Architecture Patterns

**Pattern #39 — Workflow State Visualization**
- The workflow engine (`workflow.WorkflowProcess`, `workflow.WorkflowState`, `workflow.WorkflowTransition`) provides a rich state machine. The frontend must visualize the current workflow state and available transitions.
- Minimum: status badge + available action buttons derived from API workflow state response
- Stretch: visual progress stepper for multi-step processes (e.g., 8D report using `rca.vw_EightDCompletionStatus`)
- Source: `Workflow_Engine_Architecture_Agnostic.json: $.architecture_overview`

**Pattern #42 — Notification Inbox**
- DB Phase 28 adds `workflow.NotificationQueue`; API Phase 7 will expose a notification endpoint
- The frontend notification inbox displays unread notifications for the current user
- Scope: can be deferred to Phase 10 if API notification endpoint isn't available when Phase 7 executes
- Source: `API_Integration_Architecture_Agnostic.json: $.event_and_notification_system`

### Pattern-Derived Requirements

- **APP-WORKFLOW-03:** Workflow state visualization from API state machine — show current state, available transitions, and step progress
- **APP-WORKFLOW-04:** Notification inbox from API notification queue — unread notification count + inbox view (may defer to Phase 10)

### Implementation Notes

- Workflow state component: fetch from `GET /v1/[entity]/{id}/workflow-state` (to be defined in API Phase 7)
- For 8D reports, `rca.vw_EightDCompletionStatus` data should power a step-progress component (D0-D8 steps with status indicators)
- Notification bell in shell navigation (Phase 2 shell) should show unread count; clicking opens notification panel
- If API Phase 7 notification endpoint is not yet available when App Phase 7 executes, defer notification inbox to Phase 10 (add deferred note to VERIFICATION.md)

---

## Phase 8 — Knowledge and Traceability Experience

**CONTEXT file:** `phases/08-knowledge-traceability-experience/08-CONTEXT.md`

### Reference Architecture Patterns

**Pattern #41 — Knowledge Panels in Forms**
- The knowledge retrieval layer (DB Phases 18-21, `quality.usp_GetDefectKnowledge` advisory SP and views) provides contextual knowledge about defects during NCR workflows
- The frontend should surface relevant knowledge panels inline within quality forms — e.g., when an NCR is being created for a specific defect code, show root cause guidance, investigation steps, and containment guidance from the knowledge base
- Source: `Platform_System_Architecture_Technical_Patterns.json: $.knowledge_management`

**Pattern #43 — Audit Trail Display**
- DB Phase 29 adds `audit.ApiCallLog`; the entity audit trail already exists in `audit.AuditLog`
- The frontend should display an entity audit timeline for NCR, CAPA, and SCAR detail views — showing when the entity was created, modified, state-transitioned, and by whom
- Source: `Security_Role_Architecture_Agnostic.json: $.cross_cutting_patterns.audit_trail`

### Pattern-Derived Requirements

- **APP-KNOW-01 (existing):** Knowledge panel integration in forms — surface advisory content inline during form completion
- **APP-TRACE-02:** Audit trail timeline from API audit data — entity history in detail views

### Implementation Notes

- Knowledge panels: call `GET /v1/knowledge/defect/{code}` (API Phase 8) and render relevant guidance sections as expandable panels within the NCR form
- Audit timeline: fetch from `GET /v1/[entity]/{id}/audit-history` (to be defined in API Phase 8, using `audit.AuditLog` data)
- Temporal query (`@AsOfUtc` from DB Phase 29) enables "view as of date" functionality — expose this as an optional "View history at date" control in the audit timeline if API Phase 8 supports it

---

## Phase 9 — Dashboards and Operational Views

**CONTEXT file:** `phases/09-dashboards-operational-views/09-CONTEXT.md`

### Reference Architecture Patterns

**Pattern #40 — Role-Scoped Parameterized Dashboards**
- DB Phase 30 adds `quality.vw_CapaTimelineCompliance`; other analytics views exist from v2.0 (Pareto, root cause, process zone, etc.)
- Dashboard widgets should be parameterized — each widget knows its required role/permission and hides itself if the user lacks access (using APP-AUTH-04 feature entitlement tree)
- Widgets should be parameterizable by plant scope (APP-AUTH-05) and date range
- Source: `Platform_System_Architecture_Technical_Patterns.json: $.analytics_and_reporting_patterns`

### Pattern-Derived Requirements

- **APP-DASH-01 (existing):** Role-scoped parameterized dashboard widgets — hide widgets based on entitlements, support plant and date range parameters

### Implementation Notes

- Dashboard composition: widgets are independent React components, each consuming one API endpoint
- Widget visibility: check feature entitlement (APP-AUTH-04) before rendering; show empty/locked state if unauthorized
- CAPA compliance widget: consumes `quality.vw_CapaTimelineCompliance` via API Phase 9 endpoint — show overdue count, warning count, compliant count
- Plant filter: all dashboard widgets should pass the current plant scope (APP-AUTH-05) as a query parameter
- Two-phase retrieval (Pattern #35, API Phase 9): for heavy aggregate widgets, the API will support a "load metadata first, then data" pattern — implement a loading state in heavy widgets

---

## Phase 10 — Deployment, Release, and Governance

**CONTEXT file:** `phases/10-deployment-release-governance/10-CONTEXT.md`

### Reference Architecture Patterns

**Pattern #45 — Drift Controls and Snapshot Refresh**
- The App repo maintains `api-openapi.snapshot.json` as a contract baseline — it must stay in sync with the API's published `api-openapi.publish.json`
- Phase 10 should automate this: add a script (or CI step) that detects when the API version has incremented and triggers a snapshot refresh + re-run of the contract validation check
- Breaking-change detection: when the API increments its major version, the App CI should fail loudly (not just warn) until the snapshot is explicitly updated
- Source: `API_Integration_Architecture_Agnostic.json: $.api_versioning_strategy`

### Pattern-Derived Requirements

- **APP-DRIFT-01** (new, consider adding): Automated snapshot refresh — CI detects API version increment and triggers contract refresh workflow

### Implementation Notes

- Automated snapshot sync: add a CI step `Invoke-CycleChecks.ps1` equivalent for the App repo that compares `api-openapi.snapshot.json` version against the API's published version header
- Breaking-change detection: use the existing `api-openapi.snapshot.json` → `api-openapi.publish.json` comparison; escalate warnings to CI failures on major version change
- If APP-WORKFLOW-04 (notification inbox) was deferred from Phase 7, implement it here using the API Phase 10 (integration) consumer identity and delta sync capabilities

---

## Summary of All App Pattern-Derived Enrichments

| Phase | Pattern(s) | Requirements Added | Key Dependency |
|-------|-----------|-------------------|----------------|
| 3 — Auth Session | #37 Feature Tree, #38 Org Scope | APP-AUTH-04, APP-AUTH-05 | API Phase 7 (feature gating endpoint) |
| 4 — Forms | #44 Form Preflight | APP-FORM-03 | API Phase 7 + DB Phase 32 |
| 7 — Workflow | #39 Workflow Viz, #42 Notifications | APP-WORKFLOW-03, APP-WORKFLOW-04 | API Phase 7, DB Phase 28 |
| 8 — Knowledge/Trace | #41 Knowledge Panels, #43 Audit Trail | APP-KNOW-01 (existing), APP-TRACE-02 | API Phase 8 |
| 9 — Dashboards | #40 Role-Scoped Widgets | APP-DASH-01 (existing) | API Phase 9, DB Phase 30 |
| 10 — Governance | #45 Drift Controls | APP-DRIFT-01 (new) | API Phase 10 |
