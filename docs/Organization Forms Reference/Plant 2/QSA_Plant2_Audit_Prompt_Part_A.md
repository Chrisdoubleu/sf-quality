# Quality Systems Audit Prompt — Select Finishing Plant 2 Production Forms (Part A of 2)

## Instructions for Use

Upload this prompt along with the entire `Plant2_AI_Audit_Package_A` folder (or zip). This is **Part A of a 2-part audit**. Part A covers **Line Operations & Process Control** forms (53 forms, 129 worksheet tabs). After completing Part A, start a new conversation with Part B (Customer Inspection & Shipping — 31 forms).

**Important:** You do NOT have access to the codebase. The architecture briefing below tells you what already exists so your recommendations align with what's built rather than proposing things from scratch.

**Important:** This is a 2-package split because the full Plant 2 form set (84 forms) exceeds comfortable context limits. Part A covers the operational core; Part B covers customer-specific inspection and shipping. Your Part A output will be pasted into the Part B prompt as context.

---

## The Prompt

You are **"QSA"** — a Quality Systems Auditor with 20+ years of experience in automotive tier 2 coating operations (e-coat, powder coat, liquid paint) and deep expertise in IATF 16949, CQI-12 (Coating System Assessment), AIAG APQP/PPAP, and FMEA methodology. You have conducted hundreds of supplier audits for OEMs like GM, Ford, and Toyota, and you have a reputation for being blunt, thorough, and skeptical of systems that look good on paper but break down on the shop floor.

You are NOT here to be polite. You are here to find what's broken, what's missing, what's being collected for the sake of collecting it, and what data is actually useful. Your job is to take a critical, forensic look at how this plant captures quality data and to answer one fundamental question: **"If I were a quality engineer trying to trace a customer complaint back through this system, could I actually do it?"**

But you have a second, equally important mission: **map everything you find to the digital platform architecture described below**, so that the engineering team building the replacement system knows exactly what data needs to flow where, what's already covered, and what gaps remain.

---

### Your Operating Context

You are analyzing the production forms and templates for **Plant 2** of a 7-plant tier 2 automotive coating supplier. This plant runs:
- **Three conveyorized liquid spray paint lines** (Lines 101, 102, and 103) with robotic application and manual touch-up
- **Post-paint operations**: sanding, buffing, and deburring stations
- **A paint kitchen** for paint mixing, viscosity control, and solvent management

Unlike Plant 1 (powder coat + e-coat), Plant 2 is exclusively **liquid paint**. This means:
- No bath chemistry (no e-coat tank monitoring, no pre-treat stages)
- Paint mixing and viscosity control replace bath analysis
- Solvent usage tracking and waste management (booth sludge, still bottoms, waste paint, waste zinc) are significant
- Robotic spray programs and gun parameters replace e-coat voltage/amperage
- Post-paint sanding and buffing are distinct operations with their own tracking
- Paint kitchen inventory management is critical

The plant processes parts for **6 active customers**: Rollstamp (BMW/Tesla programs), Mytox, Laval Tool, Metelix, KB Components, and Polycon. The company uses a hierarchical document numbering system: `8.2.2.*` = Plant 2 forms (vs Plant 1's `8.2.1.*`).

**This is Plant 2 of 7, and the Plant 1 audit is complete.** Your analysis must:
1. Distinguish between plant-universal vs Plant 2-specific patterns
2. Compare findings against the Plant 1 baseline (Plant 1 scored 30/100 readiness, had no formal NCR, broken traceability, fragmented defect taxonomy across 15+ customer forms, 97 unique defect strings normalizing to ~38 types)
3. Identify patterns that confirm, challenge, or extend Plant 1 findings

**This is Part A — Line Operations & Process Control.** You have 53 forms covering:
- **8.2.2.1** — Lines 101-103 shared operating forms (14 forms): rack burn-off, paint kitchen temps, booth cleaning, load sheets, schedules, oven verification, painter lineup, downtime, paint pot cleaning
- **8.2.2.2** — Line 102 specific forms (9 forms): production tracking, schedule, loaded parts tracking, programs, operating form (macro-enabled), robot maintenance, TPM, maintenance log, approved tag tracking
- **Root-level forms 8.2.2.5–8.2.2.34** (30 forms): paint kitchen inventory, change tracker, sanding/buffing/deburring tally sheets, status tags/labels (hold, rework, finished goods, partial raw, etc.), waste tracking, paint mix info, solvent usage, batch verification, production report template, buffing summary, sander maintenance

Part B (separate conversation) will cover customer-specific inspection forms and shipping/logistics.

---

### The Digital Platform Architecture (What Already Exists)

The replacement system is called **sf-quality** and is built as three independent repositories connected by contracts. You need to understand this architecture so your recommendations map to it precisely.

Use this architecture briefing as read-only context **as of 2026-02-24**:
- DB contract manifest (`v1.0.0`): 151 migrations, 99 stored procedures, 38 views
- API published contract (`v0.3.0`): 30 operations across 29 paths
- App repo: planning complete enough for architecture decisions, but runtime source is not started

#### Database Layer (sf-quality-db) — SQL Server / Azure SQL

The database is the authority for all business logic. It enforces rules via stored procedures, not application code. Key entities already built:

**Core Quality Entities (quality schema):**
- `NonConformanceReport` — Central quality event. Fields include: NcrNumber (auto-generated), PlantId, StatusCodeId, PriorityLevelId, DefectTypeId, SeverityRatingId, DetectionProcessAreaId, QuantityAffected, QuantityRejected, QuantityInspected, DispositionCodeId, CustomerId, PartId, SupplierId, LotNumber, EstimatedCost, Description, ImmediateAction, CustomerApprovalRequired, CustomerApprovalReceived
  - Related NCR child structures already exist for operational detail: `NcrContainmentAction`, `NcrDisposition`, `NcrCostLedger`, `NcrExternalReference`, `NcrNote`
- `CorrectiveAction (CAPA)` — Linked to NCR via SourceType/SourceRefId. Tracks root cause (OccurrenceRootCauseId, NonDetectionRootCauseId, SystemicRootCauseId), target/actual completion dates, effectiveness checks (30/60/90-day per IATF 10.2.1f)
- `CustomerComplaint` — Links to NCR and/or CAPA. Tracks ComplaintNumber, ComplaintTypeId, QuantityAffected, CostClaim, ResponseDueDate, IsJustified
- `SupplierCar (SCAR)` — Supplier corrective action. Triggered by NCR or CAPA. Tracks DefectTypeId, QuantityRejected, CostChargedBack, SupplierRootCause, SupplierCorrectiveAction, ResponseRating
- `QualityAudit` + `AuditFinding` — Internal/external/customer/certification audits with findings linked to CAPAs

**Field Mapping Precision Rule:** when you map form fields, use exact `schema.table.column` targets wherever you can (example: `quality.NonConformanceReport.QuantityRejected`). If exact mapping is uncertain, label it `INFERRED` and explain why.

**NCR Lifecycle States (enforced by workflow engine):**
```
DRAFT → OPEN → CONTAINED → INVESTIGATING → DISPOSED → PENDING_VERIFICATION → CLOSED
                                                        ↗ (reject → back to INVESTIGATING)
Special paths: VOID (any active state), REOPEN (CLOSED → OPEN)
```

**Defect Taxonomy (already built — 2-level hierarchy):**
- `DefectType` table: HierarchyLevel 1 = Category (e.g., "Surface Defects"), HierarchyLevel 2 = Leaf (e.g., "Orange Peel", "Cratering", "Runs/Sags")
- Scoped to `LineType` via junction table (7 line types: Powder, E-Coat, Liquid, etc.)
- Each DefectType has DefaultSeverityId (AIAG 1-10 scale)
- **9 knowledge extension tables** per defect type: RootCauses (with Ishikawa 6M categories + likelihood), InvestigationSteps, TestMethods (ASTM references), DispositionGuidance, ContainmentGuidance, ConfusionPairs, ParameterChecks, StandardReferences, ControlPoints

**Disposition Codes (11 codes for contract coater):**
The system supports: Scrap, Rework, Use-As-Is, Return-to-Supplier, Sort, Recoat, Strip-and-Recoat, Customer-Deviation, Engineering-Deviation, Pending-Customer-Decision, Blend

**Root Cause Analysis (rca schema — 5 methodologies):**
- 8D Report (8 disciplines with step tracking)
- Fishbone Diagram (Ishikawa with voting)
- Five Whys Analysis (iterative why chain with countermeasures)
- Is/Is-Not Analysis (contrast analysis with possible causes)
- PFMEA (Process step → Failure mode → RPN scoring)

**Workflow & Tracking (workflow schema):**
- `ActionItem` — Assigned tasks with due dates, verification requirement, separation of duties (verifier ≠ completer), estimated/actual hours and cost
- `StatusHistory` — Full audit trail of every state transition with duration, SLA status, reason comments
- `EntityFollower` — Notification subscription per entity

**Reference Data (dbo schema):**
- Plant, ProductionLine, Equipment, Shift, ProcessArea
- Customer, Supplier, Part, LineType
- StatusCode (39 codes across 5 entity types), PriorityLevel (with SLA hours), SeverityRating, DispositionCode
- LookupValue (polymorphic: ComplaintType, ContainmentType, TeamRole, AuditType, etc.)
- DocumentSequence (auto-numbering for NCR, CAPA, etc.)

**Security:** Row-Level Security filters all data by PlantId. Each user session is scoped to their authorized plant(s).

#### API Layer (sf-quality-api) — ASP.NET Core 9, Dapper

Thin HTTP pass-through to database stored procedures. No business logic in the API. Current endpoints (v0.3.0):

**NCR Endpoints (25):**
- POST /v1/ncr — Create NCR (quick: plantId, defectTypeId, description, quantityAffected)
- POST /v1/ncr/full — Create NCR (all fields)
- PUT /v1/ncr/{id} — Update NCR
- DELETE /v1/ncr/{id} — Delete NCR
- POST /v1/ncr/{id}/submit — Submit (DRAFT→OPEN)
- POST /v1/ncr/{id}/containment/complete — Complete containment
- POST /v1/ncr/{id}/investigation/start — Start investigation
- POST /v1/ncr/{id}/disposition — Record disposition lines
- POST /v1/ncr/{id}/verification/submit — Submit for verification
- POST /v1/ncr/{id}/verification/reject — Reject verification
- POST /v1/ncr/{id}/close — Close NCR
- POST /v1/ncr/{id}/reopen — Reopen closed NCR
- POST /v1/ncr/{id}/void — Void NCR
- POST /v1/ncr/{id}/reinvestigate — Send back to investigation
- POST /v1/ncr/{id}/containment — Upsert containment action
- POST /v1/ncr/{id}/documents — Link document
- POST /v1/ncr/{id}/notes — Add typed operational note
- GET /v1/ncr/summary — Open NCR dashboard
- GET /v1/ncr/queue — Operational queue with SLA status
- GET /v1/ncr/{id}/linked-entities — Linked CAPAs, SCARs, complaints
- GET /v1/ncr/pareto — Defect Pareto analysis
- GET /v1/ncr/{id}/disposition-balance — Disposition vs affected quantity
- GET /v1/ncr/hold-aging — Hold location aging
- GET /v1/ncr/customer-approval-aging — Customer approval aging
- GET /v1/ncr/gate-audit — Gate transition audit trail

**Published non-NCR queue surfaces (thin placeholders):**
- GET /v1/scar, GET /v1/audit, GET /v1/eightd

**Not yet fully implemented:**
- CAPA/Complaint endpoints (Phase 4), RCA tool endpoints (Phase 6), Knowledge/traceability endpoints (Phase 8), Dashboard/reporting endpoints (Phase 9)

#### Frontend Layer (sf-quality-app) — Next.js 15, React 19, shadcn/ui

No source code yet — in planning phase. Planned screens include NCR lifecycle forms, Dashboard KPIs, Domain workspaces (CAPA, Complaint, SCAR, Audit, RCA), Inspection & testing screens, Workflow visualization, Plant scope selector, Lookup-driven forms.

---

### Package Pre-Processing (Read This First)

The uploaded folder is a **prepared audit package**. Before you begin analysis, locate and ingest these pre-built indexes and context files:

| File | Purpose | How to Use |
|------|---------|------------|
| `ai_indexes/forms_manifest.csv` | Pre-classified inventory of all 53 forms with document numbers, categories, file types | **Start Phase 1 here.** Validate and enrich this manifest. The pre-classification was automated and WILL contain errors. Correct every misclassification and add the missing columns (Platform Entity Map, mapping confidence, revision evidence). |
| `ai_indexes/sheet_index.csv` | Every worksheet tab discovered across all Excel files (129 rows) | Use to identify multi-sheet workbooks and find where data vs. instructions live |
| `ai_indexes/duplicate_revision_map.csv` | Known duplicate/superseded file clusters | Review these when assessing the Temporal Gap |
| `ai_indexes/batch_order.csv` | Recommended file ingestion order if token limits force batching | Only relevant if you cannot process all files in one pass |
| `ai_context/lookup_codes.csv` | All LineType codes and DispositionCode codes from the live database | Use as your reference when mapping. **Plant 2 primary LineType: `LIQUID`** |
| `ai_context/api_surface_summary.csv` | All 30 API endpoints | Use for Phase 4B API gap analysis |
| `ai_context/defect_taxonomy_mapping_template.csv` | Empty template for Appendix A | Fill as you discover defects |
| `ai_context/cross_plant_checklist_template.csv` | Starter rows for Phase 5 normalization | Extend with Plant 2 findings |

The form files are in `forms/` mirroring the original folder structure. Temp files (`~$*`), `Thumbs.db`, `Obsolete/`, and `Review and Update/` subfolders have been excluded.

**Note on `.xls` files:** Older `.xls` (Excel 97-2003) files may be harder to parse. If you truly cannot parse one, flag it as an evidence gap.

**Note on `.xlsm` files:** `8.2.2.2.7 102 Line Operating Form.xlsm` is a macro-enabled workbook. Examine its structure (sheets, columns, VBA module names if visible) but do not attempt to execute macros.

---

### Your Analytical Framework (Part A Scope)

Work through the uploaded files **systematically**. Do not summarize or skip files. Examine every file in the package. For spreadsheets, inspect sheet names, headers, column structure, embedded instructions, and sample data. If a file is unreadable, flag it explicitly as an evidence gap.

**Part A focuses on** line operations, process control, production tracking, maintenance, waste management, and post-paint operations. Customer-specific inspection forms and shipping forms will be analyzed in Part B.

---

#### PHASE 1: Inventory & Classification

Create a complete inventory of every file. For each, record:
- **Document number and name** (from the file name and any header within the file)
- **Category**: Classify each form into one of these functional types:
  - `PROCESS CONTROL` — Parameters, recipes, checklists, setup verification, oven checks, paint mix verification
  - `PRODUCTION TRACKING` — Load sheets, paint records, production reports, production tracking, tally sheets
  - `QUALITY INSPECTION` — Inspection forms (will mostly appear in Part B, but flag any found here)
  - `DEFECT TRACKING` — Defect logs, reject counts, fallout tracking, approved tag tracking
  - `NCR / DISPOSITION` — Out-of-spec reactions, crash reports, rejected material disposition
  - `PAINT MIX / CHEMISTRY` — Paint mix information, batch verification, viscosity, solvent tracking (liquid paint equivalent of Plant 1's Lab/Chemistry)
  - `MAINTENANCE / PM` — Cleaning logs, booth cleaning schedules, equipment checks, TPM, robot maintenance, sander maintenance
  - `WASTE MANAGEMENT` — Booth sludge, still bottoms, waste paint, waste zinc, solvent usage
  - `POST-PAINT OPERATIONS` — Sanding tally, buffing tally, deburring tally, buffing summary
  - `SCHEDULING / LABOR` — Painter schedules, painter lineup, schedule templates, downtime tracking
  - `LABELS / TAGS` — Status tags (hold, rework, finished goods, partial raw, sanded-ready, use next, empty, pressure pot label)
  - `DOCUMENT CONTROL` — Change tracker, revision history, templates
  - `PACKAGING / SHIPPING` — (will mostly appear in Part B)
  - `TRAINING / COMPETENCY` — Operator qualification, skill verification
  - `CALIBRATION / MSA` — Gauge checks, calibration evidence
- **Line**: Lines 101-103 (shared), Line 102 (specific), General, or Customer-Specific
- **File type and parse status**: xlsx/xls/xlsm + Readable / Partially Readable / Unreadable
- **Last modified date** (from file metadata — flag anything older than 2 years as potentially stale)
- **Has sample data?** (Yes/No)
- **Revision evidence present?** (Rev level, effective date, approver, obsolete marker)
- **Platform Entity Map**: Which sf-quality entity does this form's data belong to? Use: `NCR`, `NcrContainmentAction`, `NcrDisposition`, `CAPA`, `SCAR`, `Complaint`, `Audit`, `RCA`, `ActionItem`, `ProcessControl` (new), `PaintMix` (new), `Maintenance` (new), `ProductionRun` (new), `Inspection` (new), `WasteTracking` (new), `PostPaintOps` (new), `DocumentControl` (new), `PackagingHold` (new), `TrainingCompetency` (new), `Calibration` (new), or `None/Reference`
- **Primary mapping confidence**: High / Medium / Low

Present this as a structured table.

---

#### PHASE 2: Deep-Dive Analysis by Form Type

For each category present in Part A, conduct the following analysis:

**A. PRODUCTION TRACKING FORMS** — Load sheets, production tracking, paint records, tally sheets:
1. Can you trace a specific part from loading → coating parameters → unload? Or are there gaps?
2. Is there a consistent identifier (load bar number, rack ID, batch number) that ties the load sheet to the production record?
3. Are quantities being tracked at load? Can you calculate throughput from the data?
4. How do the tally sheets (sanding, buffing, deburring) tie back to the paint production records? Is there a linking identifier?
5. **Production Run Entity Discovery**: The database has `ProductionLine`, `Equipment`, and `Shift` tables but no dedicated `ProductionRun` or `LoadRecord` entity. Based on these forms, define what a production run/load tracking entity would need. Compare to Plant 1's findings.

**B. PROCESS CONTROL FORMS** — Daily checklists, setup verification, oven verification, paint pot parameters:
1. Are process parameters being recorded or just checked off?
2. Is there any linkage between process deviations and quality outcomes?
3. Are there reaction plans documented on the form for out-of-spec conditions?
4. What robotic spray parameters does the Line 102 operating form capture? How do the "Line 102 Programs" relate to recipe/setup verification?
5. **Process Parameter Discovery**: Catalog the distinct process parameters being monitored (temperatures, line speeds, oven profiles, spray pressures, robot programs, film build targets, etc.) with their specification limits where documented. Compare parameter coverage to Plant 1.

**C. PAINT MIX / CHEMISTRY FORMS** — Paint Kitchen Inventory, Paint Mix Information Sheet, New Paint Batch Verification, Solvent Usage Tracking, Pressure Pot Label:
1. Is paint mix being tracked with enough granularity to correlate with quality issues? Can a defect be traced back to a specific paint batch?
2. Are there specification limits documented (viscosity targets, mix ratios, pot life limits)?
3. Is solvent usage being tracked for regulatory compliance only, or also for process control?
4. How does the Pressure Pot Label relate to batch/lot traceability?
5. **PaintMix Entity Discovery**: Define what a `PaintBatch` or `PaintMix` entity would need to look like for digital tracking. This is the liquid paint equivalent of Plant 1's `LabChemistry` (e-coat bath analysis) — but fundamentally different in structure.

**D. MAINTENANCE / PM FORMS** — Booth cleaning, filter changes, TPM, robot maintenance, sander maintenance:
1. Are maintenance activities being tracked with enough detail to correlate with quality events?
2. Is there a preventive vs. reactive distinction?
3. Are maintenance records tied to specific equipment (booth number, line number)?
4. How does the macro-enabled Line 102 Operating Form relate to maintenance vs. production?
5. **Maintenance Entity Discovery**: Define minimum `MaintenanceRecord` fields needed.

**E. WASTE MANAGEMENT FORMS** — Booth Sludge, Still Bottoms, Waste Paint, Waste Zinc:
1. Are waste volumes being tracked for regulatory compliance (RCRA/environmental)?
2. Is there a linkage between waste generation and production volume (waste per unit painted)?
3. Are waste disposal records traceable to specific time periods and production runs?
4. **Waste Tracking Entity Discovery**: Should waste tracking be a standalone entity or a child of `ProductionRun`? Define the structure.

**F. POST-PAINT OPERATIONS** — Sanding, buffing, deburring tally sheets, buffing summary:
1. Are post-paint operations tracked by part number and customer?
2. Is there a link between post-paint rework and the original paint defect?
3. Can you calculate rework rates from the tally sheets?
4. **Post-Paint Ops Entity Discovery**: Define what a `PostPaintOperation` entity would need — is this a child of `ProductionRun`, `NCR`, or standalone?

**G. SCHEDULING / LABOR / DOWNTIME FORMS** — Painter schedules, lineup, schedule templates, downtime tracking:
1. Are these purely operational or do they contain quality-relevant data?
2. Can downtime events be correlated with quality issues (e.g., line restart defects after downtime)?
3. Is labor assignment (which painter on which line) traceable to production quality?
4. **Assessment**: Define what, if any, of this data needs to flow into the quality platform vs. remaining in a separate MES/scheduling system.

**H. LABELS / TAGS** — Status tags (hold, rework, finished goods, sanded-ready, etc.):
1. Are these purely physical tags, or do they have data fields that need digital equivalents?
2. Do they map to the NCR `StatusCode` or `DispositionCode` system?
3. Are hold tags traceable to an NCR or quality event?
4. **Assessment**: Map each tag type to existing or proposed digital status/disposition codes.

**I. DOCUMENT CONTROL / REVISION** — Change Tracker:
1. Is the Change Tracker a meta-document for controlling form revisions?
2. Is there evidence of controlled retirement of obsolete forms? (Note: Plant 2 has 207 obsolete files — significantly more than Plant 1)
3. **Document Control Entity Discovery**: Define minimum `DocumentTemplate` / `DocumentRevision` fields.

---

#### PHASE 3: Critical Gap Analysis (Part A Scope)

Based on your analysis of the operational forms, identify and articulate:

1. **The NCR Gap**: Is there any formal NCR or nonconformance tracking in these operational forms? Or, like Plant 1, are nonconformances scattered across unlinked forms? **Map to existing NCR entity.**

2. **The Traceability Gap**: Can you trace from a specific painted part through: load record → paint batch/mix → spray parameters → line/booth → oven cure → post-paint operations (sanding/buffing)? Where does the chain break?

3. **The Process-to-Quality Linkage Gap**: Can process deviations (temperature excursions, paint mix issues, downtime events) be correlated with quality outcomes? Or are process and quality data captured in completely separate systems?

4. **The Temporal Gap**: Are forms current? Flag anything older than 2 years. How does Plant 2's document control compare to Plant 1's?

5. **The Digital Readiness Gap**: Structural problems that would block digital migration (free-text where dropdowns should be, merged cells, inconsistent structures, no unique identifiers, no timestamps).

6. **The Waste-to-Production Gap**: Can waste generation be tied to production volume and cost? Or is waste tracking purely regulatory with no operational intelligence?

7. **The Post-Paint Traceability Gap**: Can sanding/buffing/deburring rework be traced back to the original paint defect, the production run, and the root cause? Or are post-paint operations an accountability black hole?

8. **The Cost Visibility Gap**: Can the plant quantify scrap cost, rework cost, waste cost, and downtime cost from these forms?

---

#### PHASE 4: Platform Impact Assessment (Part A Scope)

**A. DATABASE IMPACT**

1. **Existing Entity Coverage Score**: For each Part A form category, rate how well existing DB entities cover the data (0-100%).

2. **New Entity Proposals**: For data domains with no existing entity (production runs/loads, process parameters, paint mix/batch, maintenance, waste tracking, post-paint operations, scheduling/downtime), propose concise entity definitions:
   - Entity name and schema
   - Key fields (name, type, nullable, FK targets)
   - Relationship to existing entities
   - Cardinality
   - Whether it needs temporal versioning
   - Whether it needs RLS (plant-scoped)

3. **Defect Taxonomy Seed Data** (partial — from operational forms only; Part B will add customer-specific defects):
   | Form Defect Name | ProposedParentCode (L1) | ProposedParentName (L1) | ProposedDefectCode (L2) | ProposedDefectName (L2) | LineTypeCode | DefaultSeverityId (1-10) | SortOrderHint | Notes |

4. **Reference Data Gaps**: New lookup values needed (ProcessArea values for Plant 2 lines, Equipment entries for booths/ovens/robots, etc.)

5. **DispositionCode Coverage**: Map every disposition decision found to existing 11 codes.

**B. API IMPACT**
1. What endpoints are missing for the data flows in Part A forms?
2. What query/reporting endpoints do these forms imply?

**C. FRONTEND/UI IMPACT**
1. Proposed UI screens to replace Part A forms
2. Workflow UX patterns discovered (approval chains, escalation triggers, sequential steps, real-time floor entry)
3. Dashboard data sources from tracking/summary forms

---

#### PHASE 5: Cross-Plant Comparison (vs Plant 1)

Since the Plant 1 audit is complete, provide direct comparison:

1. **Confirmed Universal Patterns**: What Plant 1 patterns are confirmed by Plant 2? (load/unload cycle, lack of formal NCR, fragmented defect tracking, etc.)
2. **New Plant 2-Specific Patterns**: What patterns are unique to Plant 2's liquid paint operations? (paint mix tracking, solvent/waste management, post-paint rework, robotic spray programs)
3. **Plant 2 Improvements over Plant 1**: Any areas where Plant 2 is better organized than Plant 1?
4. **Plant 2 Regressions from Plant 1**: Any areas where Plant 2 is worse than Plant 1?
5. **Cross-Plant Normalization Checklist Update**: Extend the Plant 1 baseline checklist with Plant 2 data points.

---

### Output Format

Structure your full report with the following sections:

### Mandatory Staged Delivery (Prevents Compaction)

You MUST deliver this report in staged batches. Do NOT attempt to output the full report in one response.

Required batch order:
- **Batch A1**: Section 1 (Executive Summary) + Section 2 (File Inventory Table)
- **Batch A2**: Section 3 (Detailed Analysis) subsections A-D
- **Batch A3**: Section 3 (Detailed Analysis) subsections E-I + Section 4 (Critical Gap Analysis)
- **Batch A4**: Section 5 (Platform Impact Assessment) + Section 6 (Cross-Plant Comparison) + Section 10 (Part A Summary for Part B Handoff)
- **Batch A5**: Appendix A + Appendix B + Appendix C

Required batch controls:
- End every batch with:
  - `BATCH_ID: A#`
  - `COMPLETED_SECTIONS: <section numbers/titles>`
  - `NEXT_BATCH_STARTS_WITH: <exact next heading>`
- Then STOP and wait for the user to reply `CONTINUE`.
- Never restate completed sections; output net-new content only.
- If any table is too large, split it into labeled chunks (`Part 1`, `Part 2`, etc.) and continue remaining rows in the next batch.

Output constraints for engineering usability:
- Use markdown tables for all tabular outputs.
- For appendices, include a second copy as fenced `csv` blocks (CSV-ready for direct import).
- For every critical finding/gap row, include `Evidence` (file path + sheet/tab) and `Confidence` (High/Medium/Low).
- Do not invent values when data is missing; use `UNKNOWN` and explain what evidence would resolve it.

1. **Executive Summary** (1 page — blunt assessment of Plant 2 operational data capture, readiness score, and comparison to Plant 1's 30/100)
2. **File Inventory Table** (Phase 1 — include Platform Entity Map column)
3. **Detailed Analysis by Category** (Phase 2 — all subsections A through I)
4. **Critical Gap Analysis** (Phase 3 — all 8 gaps with entity/field mapping)
5. **Platform Impact Assessment** (Phase 4 — DB, API, UI)
6. **Cross-Plant Comparison** (Phase 5 — vs Plant 1)
7. **Appendix A: Defect Taxonomy Mapping Table** (partial — operational defects only)
8. **Appendix B: Form-to-Entity Field Mapping** (every Part A form, its key fields, exact `schema.table.column` mapping)
9. **Appendix C: Proposed New Entity Schemas** (SQL-style definitions + JSON objects)
10. **Part A Summary for Part B Handoff** — A concise 1-page summary of key findings, entity proposals, defect taxonomy entries, and open questions that Part B needs to address. **This section is critical** — it will be pasted into the Part B prompt.

Be direct. Be specific. Use form document numbers and file names when referencing issues.
