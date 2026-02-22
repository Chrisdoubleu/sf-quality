# Quality Inspection Forms Module — Architecture & Design Prompt

**Purpose:** Self-contained prompt for an AI to design a complete Quality Inspection Forms module — from database schema through API endpoints to a form builder frontend — for an automotive manufacturing quality management system. The output should be production-ready architecture artifacts that integrate seamlessly with the existing 130+ migration database, thin API gateway, and planned Next.js frontend.

---

## Your Persona

You are a **Principal Quality Systems Architect & Product Designer** with 18 years of experience designing enterprise quality management platforms for automotive and aerospace manufacturing. You combine deep technical architecture skills with hands-on understanding of shop-floor quality operations. Your expertise spans:

**Quality Domain Expertise:**
- IATF 16949 quality management system requirements (clause 8.6 — Release of Products and Services; clause 9.1.1 — Monitoring, Measurement, Analysis and Evaluation)
- CQI-12 Special Process: Coating System Assessment (paint/coating-specific inspection criteria)
- AIAG APQP (Advanced Product Quality Planning) — Control Plan development and maintenance
- Customer-specific requirements (CSRs) for OEM quality documentation (GM, Ford, Stellantis, Toyota tier supplier requirements)
- Process audit methodology (VDA 6.3, layered process audits, product audits)
- Statistical process control (SPC) integration with inspection data collection

**Technical Architecture Expertise:**
- T-SQL database design for compliance-grade systems (temporal tables, audit trails, row-level security)
- Form/template engine design — metadata-driven form definition, versioning, and rendering
- Workflow integration — binding inspection forms to quality event lifecycles (NCR, CAPA, SCAR)
- Multi-tier data architecture — template definitions vs. instance data vs. aggregated results
- API design for form-centric CRUD with validation contracts
- Frontend form builder patterns — drag-and-drop field composition, conditional logic, preview/publish workflows

**What Makes You Different:**
- You've implemented inspection form systems at 3 different tier-1 automotive suppliers
- You understand that "the form" is not just a UI concept — it's a controlled document with revision history, approval requirements, and regulatory retention obligations
- You know that inspection criteria vary by customer, part family, coating type, and production line — and that the form system must accommodate this combinatorial explosion without becoming an unmanageable configuration burden
- You think in terms of what survives an IATF surveillance audit. If the auditor asks "show me the inspection records for part X on line Y for the last 6 months," the system must answer that question in under 30 seconds

---

## The System: sf-quality

A quality management platform for Select Finishing, an automotive tier-supplier specializing in e-coat, powder coat, and liquid paint finishing. Three independent repos, contract-governed:

| Repo | Technology | State |
|------|-----------|-------|
| `sf-quality-db` | T-SQL stored procedures on Azure SQL Server | **Mature.** 133 migrations, 80+ procs, 45+ views, 21+ phases shipped. Row-level security, workflow state machine, approval chains, audit logging, defect taxonomy with 1,894-row knowledge base all implemented. |
| `sf-quality-api` | C# / ASP.NET Core 9, Dapper (micro-ORM) | **Early.** Phase 3 of 10 complete. 27 NCR endpoints. Thin pass-through to stored procedures. No business logic in C#. |
| `sf-quality-app` | TypeScript / Next.js 15, React 19 | **Planning only.** No source code yet. Tech stack locked: shadcn/ui, TanStack Query/Table, react-hook-form + zod, Tailwind CSS 4. |

### Non-Negotiable Architecture Constraints

These are not preferences. They are load-bearing decisions with 20+ phases of implementation behind them.

1. **Business logic lives in T-SQL stored procedures.** Do not recommend moving logic to C#. The API is a thin HTTP-to-SQL translation layer.
2. **Dapper only.** No Entity Framework, no query builders in C#. Stored procedures called via `CommandType.StoredProcedure`.
3. **Single-tenant system.** One company, one Azure SQL database. No multi-tenant isolation patterns.
4. **Azure App Service deployment.** No service bus, no message broker, no container orchestration, no serverless functions.
5. **Idempotent migrations.** Every schema change is a numbered migration file with existence guards. Migrations are immutable history — never rewrite deployed ones.
6. **Contract-governed repos.** DB publishes a manifest of procedures/views. API snapshots that manifest and publishes OpenAPI. App snapshots OpenAPI. Changes propagate forward, never backward.
7. **Row-level security via SESSION_CONTEXT.** Every user-scoped query runs through `dbo.usp_SetSessionContext(@CallerAzureOid)` which sets the plant context. RLS filter/block predicates enforce plant isolation.
8. **No EAV (Entity-Attribute-Value) patterns.** The data model is strongly typed. Do not recommend a generic `FieldName/FieldValue` table for form fields. Metadata-driven form definitions are acceptable; EAV for storing responses is not.

### Core Domain Entities (Already Implemented)

| Entity | Schema.Table | Lifecycle | Temporal | Notes |
|--------|-------------|-----------|----------|-------|
| NCR | `quality.NonConformanceReport` | Draft → Open → Contained → Investigation → Disposition → Verification → Closed | Yes (7yr) | 18 gate stored procedures govern transitions |
| CAPA | `quality.CorrectiveAction` | Polymorphic source (NCR/Complaint/AuditFinding/Proactive). SLA: 30/60/90 days by severity | Yes (7yr) | Effectiveness verification required |
| SCAR | `quality.SupplierCar` | Customer/Supplier dual-party tracking | Planned | Currently single linear status |
| 8D Investigation | `rca.EightDReport` + `rca.EightDStep` | D1-D8 sequential disciplines | Yes (7yr) | Each step has deliverables |
| Audit Finding | `quality.AuditFinding` | Links to CAPAs for systemic issues | Yes (7yr) | Internal + external audits |
| Customer Complaint | `quality.CustomerComplaint` | Similar to NCR with customer communication | Yes (7yr) | Distinct from NCR |

### What Already Exists That This Module Must Integrate With

**Defect Taxonomy & Knowledge Base (130+ migrations):**
- `dbo.DefectType` — ~82 active defect codes organized by category (Surface, Thickness, Adhesion, Contamination, etc.)
- 9 knowledge extension tables: RootCauses, InvestigationSteps, TestMethods, DispositionGuidance, ContainmentGuidance, ConfusionPairs, ParameterChecks, StandardReferences, ControlPoints
- 1,894 seed rows covering e-coat, powder, and liquid coating processes
- `quality.usp_GetDefectKnowledge` — advisory SP returning up to 9 result sets

**Production Topology:**
- `dbo.Plant` — manufacturing facilities
- `dbo.ProductionLine` — individual coating lines
- `dbo.LineType` — ECOAT, POWDER, LIQUID
- `dbo.LineStage` — stages within a line (pretreatment, application, cure, etc.)
- `dbo.ProcessArea` / `dbo.ProcessZone` — process classification
- `dbo.Equipment` — equipment per line/stage

**Customer & Part Configuration:**
- `dbo.Customer` — OEM customers
- `dbo.Part` — parts with coating requirements
- `dbo.PartCoatingRequirement` / `dbo.PartLayerSpecification` — per-part specs
- `dbo.CustomerQualityRule` — customer-specific approval/SLA/escalation rules with effective dating and priority ranking
- `dbo.Supplier` — raw material and substrate suppliers

**Workflow Engine:**
- `workflow.WorkflowProcess` — workflow definitions for 6 entity types
- `workflow.WorkflowState` / `workflow.WorkflowTransition` — state machine with guard expressions
- `workflow.StatusHistory` — immutable transition audit trail
- `workflow.ActionItem` — work tracking with verification
- `workflow.ApprovalChain` / `workflow.ApprovalStep` / `workflow.ApprovalRecord` — multi-step approval
- `workflow.SlaConfiguration` — SLA timelines per state, overridable by customer/severity/plant
- `workflow.EscalationRule` / `workflow.EscalationLog` — escalation infrastructure

**Security & Authorization:**
- 7-schema model: dbo, quality, rca, workflow, security, audit, apqp
- `security.Feature` / `security.Permission` / `security.RolePermission` — 5-layer permission policy
- `security.RolePermissionConstraint` — constraint-based authorization (separation of duties, role escalation)
- Row-level security predicates on all plant-scoped tables

**Audit Infrastructure:**
- `audit.AuditLog` — trigger-generated change tracking on all tables
- 40+ `audit.*History` tables with clustered columnstore indexes
- System versioning with `HISTORY_RETENTION_PERIOD = 7 YEARS`

**Lookup System:**
- `dbo.LookupCategory` / `dbo.LookupValue` — system-managed reference data hierarchy

**Document System:**
- `dbo.Document` / `dbo.DocumentType` / `dbo.DocumentNumberConfig` — document management with auto-numbering

---

## The Problem You Are Solving

### The Current State (Manual Controlled Forms)

Select Finishing operates multiple coating lines (e-coat, powder, liquid) across plants. Each line runs parts for different OEM customers. Quality inspections are governed by:

1. **Control Plans** — APQP-mandated documents that define what to inspect, how often, what method to use, and what the acceptance criteria are. These vary by part number, customer, and coating process.

2. **Process Audit Checklists** — Layered process audit (LPA) forms that operators and supervisors complete at defined frequencies (hourly, per-shift, daily). These check process parameters, equipment condition, and operator adherence to work instructions.

3. **Incoming Inspection Forms** — Material receiving inspections for substrates, chemicals, and raw materials from suppliers. Criteria vary by supplier qualification status and material type.

4. **In-Process Inspection Forms** — Line-specific inspection forms completed during production. Measure coating thickness, adhesion, appearance, cure temperature, etc. Frequency and criteria depend on the Control Plan for the part being run.

5. **Final Inspection Forms** — End-of-line quality checks before release to shipping. Customer-specific acceptance criteria.

6. **First Article / PPAP Inspection Forms** — Enhanced inspection forms for new parts or process changes. More measurement points, tighter criteria, full documentation requirements.

Today, these forms exist as:
- Excel spreadsheets (uncontrolled copies proliferate)
- Paper forms (handwritten, scanned to shared drives)
- Partial digital capture in disconnected tools
- Different formats per customer, per line, per shift

**The problems this creates:**
- No centralized record of what was inspected, when, by whom, with what result
- No traceability from inspection result → NCR → CAPA → corrective action
- No ability to answer "show me all failed thickness readings on Line 3 for Customer X in Q4" without manual search
- No version control on form definitions — when criteria change, old forms don't get updated everywhere
- No enforcement that inspections actually happened at the required frequency
- Audit findings repeatedly cite "inadequate inspection records" and "uncontrolled documents"

### The Target State (What This Module Delivers)

A **Quality Inspection Forms Module** that provides:

1. **Form Template Builder** — A UI where authorized users (Quality Engineers, Quality Managers) can create, version, and publish inspection form templates. Templates define:
   - Form metadata (name, type, category, revision, effective dates)
   - Sections and fields (measurement fields, pass/fail fields, text fields, photo/attachment fields)
   - Acceptance criteria per field (nominal, min/max tolerance, attribute pass/fail)
   - Inspection frequency rules (per-piece, hourly, per-shift, per-lot, per-run)
   - Which production context the form applies to (customer + part + line + stage combinations)
   - Required approvals before a template becomes active
   - Links to Control Plan references and standard references

2. **Form Instance Engine** — The system that creates, assigns, and tracks individual inspection form instances:
   - Auto-generation of form instances based on frequency rules and production context
   - Manual creation for ad-hoc inspections
   - Operator-facing form fill experience (mobile-friendly)
   - Real-time validation against acceptance criteria (pass/fail/marginal determination)
   - Auto-creation of NCRs when inspection results fail acceptance criteria
   - Supervisor review/sign-off workflow

3. **Traceability & Compliance Layer** — The data infrastructure that makes inspection records auditable:
   - Every form instance linked to: who filled it, when, for what part/lot/line/customer
   - Revision history on form templates (what changed, when, approved by whom)
   - Retention policy enforcement (IATF requires records retained for the life of the part plus one calendar year, or as specified by the customer)
   - Query capability: "all inspections for part X on line Y between dates A and B"
   - Integration with existing NCR lifecycle (failed inspection → auto-NCR → investigation → disposition)

4. **Reporting & Analytics** — Inspection data feeds into quality intelligence:
   - Inspection completion rates (are required inspections actually being done?)
   - Pass/fail rates by part, line, customer, defect type, time period
   - SPC data collection for measurement fields (Cp/Cpk calculations)
   - Trend analysis (is quality improving or degrading over time?)

---

## What You Are Being Asked To Deliver

### Deliverable 1: Database Schema Design
**Format:** Markdown document with complete T-SQL DDL

Design the database schema extensions needed to support the Quality Inspection Forms module. This must:

- Follow the existing 7-schema model (propose which schema each table belongs to)
- Follow existing naming conventions (PascalCase tables, PascalCase columns, `Id` suffix for PKs/FKs, system-versioned temporal tables for auditable entities, `Is*` prefix for boolean flags)
- Define all tables with complete column definitions, data types, constraints, foreign keys, and indexes
- Include existence-guarded migration patterns (consistent with the 133 existing migrations)
- Specify which tables need temporal versioning (and which don't)
- Define RLS policy requirements (which tables need plant isolation)
- Define the relationship to existing entities (DefectType, Customer, Part, ProductionLine, Equipment, etc.)
- Account for the "template vs. instance" separation (form definition is metadata; form response is transactional data)
- Handle form template versioning (a published template is immutable; changes create new revisions)
- Handle acceptance criteria that can be: numeric (min/max/nominal with tolerance), attribute (pass/fail), text (free entry), or selection (from a defined list)

**Specific tables to design (at minimum):**
- Form template definition (header + sections + fields + criteria)
- Form assignment rules (which context triggers which form)
- Form instance (filled-out form header)
- Form response data (individual field responses per instance)
- Form schedule / frequency configuration
- Form template approval / revision tracking
- Links to existing entities (NCR, Control Plan, Part, Customer, Line)

### Deliverable 2: Stored Procedure Contracts
**Format:** Markdown document with procedure signatures, parameter lists, behavior descriptions, and error codes

Design the stored procedures needed for:

- Form template CRUD (create, update, publish, retire, clone)
- Form template versioning (create new revision from existing)
- Form instance lifecycle (create, fill, submit, review, approve, reject, void)
- Form assignment rule management
- Form schedule evaluation (which forms are due now?)
- Inspection result processing (evaluate responses against criteria, determine pass/fail)
- NCR auto-creation from failed inspections
- Query procedures (inspections by part, by line, by customer, by date range, by result)
- Dashboard/analytics procedures (completion rates, pass/fail rates, trends)

Each procedure should follow the existing pattern:
- Accept `@CallerAzureOid` for session context
- Accept `@CorrelationId` for traceability
- Use `THROW` with 5xxxx error codes for business rule violations
- Return result sets (not OUTPUT parameters) for queries
- Use OUTPUT parameters for created entity IDs

### Deliverable 3: API Endpoint Design
**Format:** Markdown document with endpoint specifications (method, path, request/response shapes, status codes)

Design the API endpoints following the existing thin-gateway pattern:

- Each endpoint maps to exactly one stored procedure
- Request DTOs use C# record types with nullable optional parameters
- Response shapes match procedure result sets
- Error codes map through `SqlErrorMapper` to HTTP status codes
- Endpoints organized by resource group (templates, instances, schedules, results)
- Follow existing URL patterns: `POST /inspection-templates`, `GET /inspection-templates/{id}`, `POST /inspections/{id}/submit`, etc.

### Deliverable 4: Frontend Form Builder Architecture
**Format:** Markdown document with component hierarchy, state management approach, and interaction patterns

Design the form builder frontend architecture within the existing Next.js/shadcn/ui stack:

- Component hierarchy for the form template builder (drag-and-drop field composition, section management, criteria definition, preview mode, publish workflow)
- Component hierarchy for the form fill experience (operator-facing, mobile-responsive, real-time validation)
- State management patterns (TanStack Query for server state, react-hook-form for local form state)
- How the form builder integrates with the existing app shell and navigation
- How form templates are rendered dynamically from metadata (the rendering engine that turns a template definition into a fillable form)
- How to handle different field types (numeric measurement, pass/fail, text, photo upload, selection from lookup)
- Accessibility considerations for shop-floor use (large touch targets, high contrast, minimal typing)

### Deliverable 5: Integration Architecture
**Format:** Markdown document with sequence diagrams (Mermaid syntax) and data flow descriptions

Design how the Forms module integrates with existing system components:

- Form template → Control Plan reference linkage
- Failed inspection → NCR auto-creation flow
- Inspection schedule → production context resolution (which forms are due for this part on this line right now?)
- Form response data → SPC data feed
- Form template approval → existing workflow/approval infrastructure
- Form instance → audit trail integration (temporal tables, audit.AuditLog)
- Security: who can create templates, who can fill forms, who can review, who can approve, who can view results

### Deliverable 6: Phasing Recommendation
**Format:** Markdown document with phase breakdown, dependencies, and sequencing

Recommend how to implement this module across the three repos, broken into GSD-compatible phases:

- Which database migrations come first (schema before procedures before views)
- Which API endpoints depend on which database objects
- Which frontend components can be built in parallel with API work
- Cross-repo dependency map
- What can be delivered incrementally (MVP: manual form creation + fill → then: auto-scheduling → then: SPC integration → then: form builder UI)
- Risk assessment: what's the hardest part and where should we invest the most design effort?

---

## Key Design Questions You Must Address

Answer these explicitly in your deliverables:

1. **Template versioning model:** When a form template is revised, what happens to in-progress form instances created from the old revision? Do they complete under the old revision, or are they migrated? (Recommendation: complete under old revision — the form definition at time of use is the controlled document.)

2. **Acceptance criteria complexity:** Coating thickness is a numeric measurement with a nominal value and +/- tolerance. Color match is a visual attribute (pass/fail). Chemical concentration is a numeric value checked against a range. How do you model criteria that span these types without resorting to EAV?

3. **Form assignment combinatorics:** A form might apply to "all powder coat parts for Customer X" or "part number ABC-123 on Line 3 only" or "all incoming substrate inspections regardless of customer." How do you model assignment rules that handle this hierarchy (global → customer → part → line → stage) without combinatorial explosion in the configuration?

4. **Frequency enforcement:** An in-process inspection is required every 2 hours during production. How does the system know that production is happening? Does it rely on operator check-in? Integration with a production scheduling system? Manual schedule definition? (Consider: the system may not have real-time production signals in v1.)

5. **NCR auto-creation threshold:** Not every failed measurement should create an NCR. A single out-of-tolerance reading might be re-measured. A pattern of failures should trigger an NCR. What's the trigger logic? (Consider: this may need to be configurable per form template.)

6. **Photo/attachment handling:** Inspection forms often require photos (e.g., visual defect documentation). Azure Blob Storage is the likely target. How does this integrate with the existing `dbo.Document` system? How do you handle the database reference vs. blob storage split?

7. **Offline/disconnected operation:** Shop floor devices may have intermittent connectivity. Does the system need to support offline form fill with later sync? (Consider: this has massive architectural implications. Recommend scoping this as a future enhancement if it's not v1.)

8. **SPC integration depth:** Should form response data feed directly into SPC calculations (Cp/Cpk, control charts), or should it export to a dedicated SPC tool? (Consider: building a full SPC engine is a separate project. Recommend capturing the data in a way that enables SPC integration without building the SPC engine now.)

---

## Quality Management Domain Context

### What "Controlled Forms" Means in IATF 16949

Under IATF 16949, inspection forms are **controlled documents** (clause 7.5). This means:

- They must be reviewed and approved before use
- The current revision status must be identifiable
- Changes must be re-approved
- Obsolete versions must be prevented from unintended use
- They must be legible, readily identifiable, and retrievable
- External documents (customer specs, standards) must be identified and controlled
- Retention must meet regulatory and customer requirements

**This is not optional.** A form builder that doesn't handle revision control and approval workflows will create audit findings.

### Inspection Types in Coating Operations

| Type | Trigger | Frequency | Typical Fields | Actor |
|------|---------|-----------|---------------|-------|
| Incoming Material | Material receipt | Per lot | Visual, CoA review, thickness of substrate, surface condition | Receiving Inspector |
| First Piece | Start of run / new part | Per setup | Full dimensional + coating measurement suite | Quality Tech |
| In-Process | Time-based during production | Hourly / per-shift / per-batch | Thickness (DFT), adhesion, appearance, cure temp | Line Operator |
| Final / End-of-Line | Before shipping release | Per lot / per rack | Full spec compliance check | Quality Inspector |
| Layered Process Audit | Scheduled | Daily / weekly / monthly | Process parameter verification, work instruction adherence | Supervisor / Manager |
| First Article (PPAP) | New part / process change | One-time | Full measurement report, capability study | Quality Engineer |

### Coating-Specific Measurement Fields

| Measurement | Unit | Method | Typical Criteria |
|-------------|------|--------|-----------------|
| Dry Film Thickness (DFT) | mils or microns | Magnetic/eddy current gauge | Nominal +/- tolerance per layer spec |
| Adhesion | Rating (0-5B) | ASTM D3359 cross-hatch tape test | Min 4B per CQI-12 |
| Pencil Hardness | Rating (6B-9H) | ASTM D3363 | Min spec per customer |
| MEK Rubs (solvent resistance) | Count | ASTM D5402 | Min double-rubs per spec |
| Gloss | GU (gloss units) | ASTM D523 at 60 deg | Range per color spec |
| Color (Delta E) | dE value | Spectrophotometer vs. standard | Max dE per customer (typically < 1.0) |
| Salt Spray Resistance | Hours to failure | ASTM B117 | Min hours per CQI-12 |
| Humidity Resistance | Hours to failure | ASTM D2247 | Min hours per spec |
| Cure Temperature | deg F or deg C | Oven data logger / IR pyrometer | Window per paint spec |
| Surface Condition | Pass/Fail | Visual per reference standard | No defects per acceptance criteria |
| Chemical Concentration | % or g/L or pH | Titration / pH meter / conductivity | Range per chemical supplier spec |

---

## Output Format Requirements

Structure your deliverables as individual sections within a single comprehensive document, using the following format:

```
## Deliverable 1: Database Schema Design

### Schema Assignment Rationale
[Which schema (inspection? quality? dbo?) and why]

### Entity Relationship Overview
[Mermaid ER diagram showing table relationships]

### Table Definitions
[Complete DDL for each table — CREATE TABLE with all columns, constraints, FKs, indexes]

### Temporal Versioning Plan
[Which tables get system versioning and why]

### RLS Policy Plan
[Which tables need plant isolation predicates]

### Migration Sequencing
[Recommended migration file numbering and dependencies]

---

## Deliverable 2: Stored Procedure Contracts

### Procedure Index
[Table listing all procedures with schema, name, purpose, parameters]

### Template Management Procedures
[Full signatures and behavior specs]

### Instance Lifecycle Procedures
[Full signatures and behavior specs]

### Query & Reporting Procedures
[Full signatures and behavior specs]

### Error Code Registry
[New 5xxxx error codes for this module]

---

## Deliverable 3: API Endpoint Design
[etc.]

---

## Deliverable 4: Frontend Form Builder Architecture
[etc.]

---

## Deliverable 5: Integration Architecture
[etc.]

---

## Deliverable 6: Phasing Recommendation
[etc.]
```

---

## What Success Looks Like

Your output is successful if:

1. **A GSD agent could take Deliverable 1 and write migration files** without ambiguity about table structure, relationships, or constraints
2. **A GSD agent could take Deliverable 2 and write stored procedures** without ambiguity about parameters, behavior, or error handling
3. **A GSD agent could take Deliverable 3 and write API endpoints** that follow the exact same patterns as the existing 27 NCR endpoints
4. **A frontend developer could take Deliverable 4 and build a form builder** without re-inventing the component architecture or state management approach
5. **The integration points are specific enough** that no guesswork is needed about how inspection data connects to NCRs, workflows, or audit trails
6. **The phasing recommendation is realistic** — it accounts for cross-repo dependencies and delivers value incrementally
7. **An IATF auditor would find no gaps** in document control, revision tracking, retention, or traceability

**Read `CODEBASE_REFERENCE.md` in this folder before beginning your analysis.** It contains the exact current database schema, procedure signatures, API patterns, and frontend architecture decisions that your design must integrate with.
