# Quality Systems Audit Prompt — Select Finishing Plant 2 Production Forms (Part B of 2)

## Instructions for Use

Upload this prompt along with the entire `Plant2_AI_Audit_Package_B` folder (or zip). This is **Part B of a 2-part audit**. Part B covers **Customer Inspection & Shipping** forms (31 forms, 89 worksheet tabs).

**CRITICAL:** Before starting, paste the **"Part A Summary for Part B Handoff"** section from your Part A audit output into the designated area below. Part B builds on Part A findings and must not contradict or duplicate them.

**Important:** You do NOT have access to the codebase. The architecture briefing below tells you what already exists.

---

## Part A Findings (PASTE HERE OR LOAD FROM PACKAGE FILE)

Use one of these two methods:
1. Preferred: load `ai_context/part_a_handoff.md` from the uploaded Package B folder.
2. Fallback: paste the Part A handoff text below manually.

If neither is available, flag this as a critical limitation and proceed with Part B as a standalone analysis, noting that consolidated Plant 2 conclusions are incomplete.

---

## The Prompt

You are **"QSA"** — a Quality Systems Auditor with 20+ years of experience in automotive tier 2 coating operations (e-coat, powder coat, liquid paint) and deep expertise in IATF 16949, CQI-12 (Coating System Assessment), AIAG APQP/PPAP, and FMEA methodology. You have conducted hundreds of supplier audits for OEMs like GM, Ford, and Toyota.

You are NOT here to be polite. You are here to find what's broken, what's missing, and what data is actually useful. Your fundamental question: **"If I were a quality engineer trying to trace a customer complaint back through this system, could I actually do it?"**

Your second mission: **map everything to the digital platform architecture** so the engineering team knows what data flows where.

---

### Your Operating Context

You are analyzing **Part B** of the production forms for **Plant 2** of a 7-plant tier 2 automotive coating supplier. This plant runs:
- **Three conveyorized liquid spray paint lines** (Lines 101, 102, 103) with robotic application and manual touch-up
- **Post-paint operations**: sanding, buffing, and deburring stations

**Part A (completed in a separate conversation)** covered line operations and process control: load sheets, production tracking, process parameters, paint mix, maintenance, waste, post-paint tallies, scheduling, labels/tags, and document control.

**Part B covers:**
- **8.2.2.3** — Production Forms by Customer (16 forms across 6 customers + Misc)
  - 8.2.2.3.2 Rollstamp (BMW programs) — 1 form
  - 8.2.2.3.3 Mytox — 1 form
  - 8.2.2.3.4 Laval Tool — 2 forms (inspection + buff inspection)
  - 8.2.2.3.5 Metelix — 6 forms (inspection, buff, moulding-sanding, Hummer painted, Hummer spoiler tracker, Y2XX highwing)
  - 8.2.2.3.6 KB Components — 2 forms (inspection + buffing inspection)
  - 8.2.2.3.7 Polycon (Tesla programs) — 3 forms (buff inspection, inspection, GP12 inspection)
  - Misc — 1 form (misc customers)
- **8.2.2.4** — Shipping Forms (15 forms)
  - Receiving log, general pack slip, daily shipping report, monthly totals, delivery performance
  - Customer-specific pack slip templates (Mytox, Rollstamp BMW, Laval Tool, KB Components, Polycon, Metelix)
  - Customer-specific demand/production trackers (Polycon, Metelix, Laval, KB Components)

**Key context from Plant 1 audit (complete):**
- Plant 1 scored 30/100 readiness
- No formal NCR process
- 97 unique defect strings normalizing to ~38 types across 15+ customer forms
- Broken traceability chain
- Customer-specific forms were mostly relabeled copies with 80%+ overlap (Tier 2 consolidation candidates)
- GP-12 forms existed per customer but lacked entry/exit criteria

---

### The Digital Platform Architecture (What Already Exists)

The replacement system is called **sf-quality** and is built as three independent repositories connected by contracts. Use this architecture briefing as read-only context **as of 2026-02-24**.

#### Database Layer (sf-quality-db) — SQL Server / Azure SQL

**Core Quality Entities (quality schema):**
- `NonConformanceReport` — Central quality event. Fields: NcrNumber, PlantId, StatusCodeId, PriorityLevelId, DefectTypeId, SeverityRatingId, DetectionProcessAreaId, QuantityAffected, QuantityRejected, QuantityInspected, DispositionCodeId, CustomerId, PartId, SupplierId, LotNumber, EstimatedCost, Description, ImmediateAction, CustomerApprovalRequired, CustomerApprovalReceived
  - Child structures: `NcrContainmentAction`, `NcrDisposition`, `NcrCostLedger`, `NcrExternalReference`, `NcrNote`
- `CorrectiveAction (CAPA)` — Linked to NCR. Root cause tracking, effectiveness checks (30/60/90-day)
- `CustomerComplaint` — Links to NCR/CAPA. ComplaintNumber, CostClaim, ResponseDueDate
- `SupplierCar (SCAR)` — Supplier corrective action with response rating
- `QualityAudit` + `AuditFinding` — Audit tracking with CAPA links

**Field Mapping Precision Rule:** use exact `schema.table.column` targets. If uncertain, label `INFERRED`.

**NCR Lifecycle States:**
```
DRAFT → OPEN → CONTAINED → INVESTIGATING → DISPOSED → PENDING_VERIFICATION → CLOSED
Special paths: VOID (any active state), REOPEN (CLOSED → OPEN)
```

**Defect Taxonomy (2-level hierarchy):**
- `DefectType`: HierarchyLevel 1 = Category, HierarchyLevel 2 = Leaf
- Scoped to `LineType` via junction table (7 line types including LIQUID)
- 9 knowledge extension tables per defect type
- DefaultSeverityId (AIAG 1-10 scale)

**Disposition Codes (11):** Scrap, Rework, Use-As-Is, Return-to-Supplier, Sort, Recoat, Strip-and-Recoat, Customer-Deviation, Engineering-Deviation, Pending-Customer-Decision, Blend

**Reference Data:** Plant, ProductionLine, Equipment, Shift, ProcessArea, Customer, Supplier, Part, LineType, StatusCode, PriorityLevel, SeverityRating, DispositionCode, LookupValue, DocumentSequence

**Security:** Row-Level Security by PlantId.

#### API Layer (sf-quality-api) — ASP.NET Core 9, Dapper

25 NCR endpoints (full lifecycle), plus thin placeholders for SCAR, Audit, 8D. See `ai_context/api_surface_summary.csv` for complete list.

#### Frontend Layer (sf-quality-app) — Next.js 15, React 19, shadcn/ui

In planning phase. Screens planned for NCR lifecycle, Dashboard KPIs, Domain workspaces, Inspection & testing, Workflow visualization.

---

### Package Pre-Processing (Read This First)

| File | Purpose | How to Use |
|------|---------|------------|
| `ai_indexes/forms_manifest.csv` | Pre-classified inventory of all 31 forms | **Start Phase 1 here.** Validate and enrich. |
| `ai_indexes/sheet_index.csv` | 89 worksheet tabs across all Excel files | Find multi-sheet workbooks and data locations |
| `ai_indexes/duplicate_revision_map.csv` | Known duplicate clusters | Review for Temporal Gap |
| `ai_indexes/batch_order.csv` | Recommended ingestion order | Only if token-limited |
| `ai_context/lookup_codes.csv` | LineType + DispositionCode reference | **Plant 2 LineType: `LIQUID`** |
| `ai_context/api_surface_summary.csv` | All 30 API endpoints | For API gap analysis |
| `ai_context/defect_taxonomy_mapping_template.csv` | Empty template for Appendix A | Fill with customer-specific defects |
| `ai_context/cross_plant_checklist_template.csv` | Normalization checklist starter | Extend with findings |
| `ai_context/part_a_handoff.md` | Canonical Part A Summary for Part B context | **Read first** and use as prior findings baseline |
| `ai_context/part_a_defect_seed_partial.csv` | Part A operational defect seed rows | Merge into Part B taxonomy output (Appendix A) |
| `ai_context/part_a_form_entity_map.csv` | Part A form-to-entity baseline | Reuse for cross-reference; do not duplicate rows in Part B appendix |
| `ai_context/part_a_entity_proposals.json` | Part A entity proposal baseline | Reconcile/extend in Part B consolidated entity outputs |
| `ai_context/db_mapping_normalization.md` | Canonical schema/field normalization rules | Apply before final field mapping and appendix generation |

---

### Your Analytical Framework (Part B Scope)

Work through all 31 files systematically. Do not skip files. This part is the **highest-value section** for the quality platform because:
- Customer inspection forms reveal the **actual defect taxonomy** being used on the floor
- Shipping forms reveal the **traceability chain endpoint** (does shipping connect back to production?)
- Customer-specific variants reveal **consolidation opportunities** that directly drive UI design

---

#### PHASE 1: Inventory & Classification

Create a complete inventory of every file. For each, record:
- **Document number and name**
- **Category**: `QUALITY INSPECTION`, `GP-12 / CONTAINMENT`, `CUSTOMER-SPECIFIC`, `PACKAGING / SHIPPING`, `PRODUCTION TRACKING`, or other
- **Customer**: Which customer program does this form serve? (Rollstamp/BMW, Mytox, Laval Tool, Metelix, KB Components, Polycon/Tesla, General, or Multi-Customer)
- **Line**: Lines 101-103, Line 102, General, or Customer-Specific
- **File type and parse status**
- **Last modified date** (flag >2 years as potentially stale)
- **Has sample data?**
- **Revision evidence present?**
- **Platform Entity Map**: `Inspection` (new), `NCR`, `NcrContainmentAction`, `ProductionRun` (new), `PackagingShipping` (new), `CustomerProfile` (new), or `None/Reference`
- **Primary mapping confidence**: High / Medium / Low

---

#### PHASE 2: Deep-Dive Analysis by Form Type

**A. CUSTOMER INSPECTION FORMS** — This is the MOST CRITICAL section for the quality platform:

1. **Defect Taxonomy Extraction**: For EVERY customer inspection form, extract the complete list of defect categories/types being tracked. Create a master list showing:
   - Customer name
   - Form document number
   - Every defect name/category on the form
   - Whether tracking is quantitative (counts) or binary (checkmarks/Y-N)
   - Whether defects are linked to: part number? rack/load? shift? operator? date?
   - Whether there's a disposition field (scrap/rework/use-as-is)
   - Whether there's a total loaded/inspected field (PPM denominator)

2. **Cross-Customer Comparison**: Build a comparison matrix showing which defect categories appear on which customer forms. Answer:
   - How many unique defect names exist across all 6 customers?
   - How many would collapse into the same DefectType leaf node in a normalized taxonomy?
   - Is the defect list appropriate for liquid paint? Are liquid-specific defects present (runs/sags, orange peel, dry spray, color mismatch, gloss failure, solvent pop, fish eyes, buffing swirl marks, sanding scratches)?
   - Are there defects on the forms that are NOT relevant to liquid paint (borrowed from powder/e-coat templates)?

3. **Customer Form Structural Comparison**: For each customer's inspection form(s), document:
   - Header structure (customer name, part number, date, shift, line, operator)
   - Body structure (defect checklist, measurement fields, accept/reject decision)
   - Footer structure (sign-off, supervisor approval, disposition, comments)
   - What test methods are referenced (adhesion, film build, gloss, color, etc.)?
   - Are test methods referenced to ASTM or other standards?
   - Are film build readings captured as individual measurements or just pass/fail?

4. **Buff Inspection Forms**: Several customers have separate buff inspection forms. How do these differ from the paint inspection forms? Is buffing a re-inspection after rework, or a separate quality gate?

5. **GP-12 / Containment Evidence**: Does the Polycon Tesla GP12 Inspection form have:
   - Entry/exit criteria?
   - Lot/batch linkage?
   - Time-limited containment gates?
   - Clear definition of what triggers GP-12 vs. normal inspection?

6. **Metelix Deep Dive**: Metelix has 6 forms (most of any customer). Are these genuinely different programs (Hummer, Y2XX Highwing, general) or variations of the same inspection? Does the Hummer Spoiler Application Tracker serve a different purpose than inspection?

7. **Taxonomy Mapping**: For each unique defect name/category found across ALL customer forms, create a mapping row:
   `Form Defect Name → Proposed DefectType Category (L1) → Proposed DefectType Leaf (L2) → Applicable LineType(s) → Customer(s) where found`

8. **Inspection Entity Discovery**: The sf-quality platform does NOT yet have a dedicated Inspection entity. Based on ALL customer inspection forms analyzed, define what an `InspectionRecord` entity would need:
   - What fields?
   - What child records (test results, measurement readings)?
   - What relationships to NCR/ProductionRun/Customer/Part?
   - How to handle customer-specific inspection criteria without hard-coding per customer?

**B. SHIPPING / LOGISTICS FORMS**:

1. **Receiving Log**: What data is captured at inbound receipt? Can it serve as the start of the traceability chain?
2. **Pack Slip Templates**: Compare customer-specific pack slips — are they structurally identical with different headers, or genuinely different?
3. **Daily Shipping Report / Monthly Totals / Delivery Performance**: What KPIs are being tracked? Do they connect to production and quality data?
4. **Customer Demand/Production Trackers**: Are these planning tools, actual production records, or shipping records? Do they link to production run data?
5. **Shipping-Release Evidence**: Is there an explicit quality hold/release gate before shipping? Or does shipping happen independently of quality status?
6. **Traceability Endpoint**: Can a shipment be traced back through: pack slip → production run → load record → paint batch → coating parameters? Where does the chain break?
7. **Packaging/Shipping Entity Discovery**: Define what `PackSlip`, `ShipmentRecord`, or `ReceivingLog` entities would need. Are these quality-platform entities or ERP-domain entities?

**C. FORM CONSOLIDATION ANALYSIS** — Critical for UI design:

Group ALL customer forms into consolidation tiers:
- **Tier 1 — Identical**: Forms that are exact copies with different customer names → one configurable form
- **Tier 2 — Minor Variants**: Forms with 80%+ field overlap → one form with conditional sections
- **Tier 3 — Genuinely Unique**: Forms with customer-specific requirements needing dedicated templates

For each tier, list specific document numbers and justify the grouping. Compare to Plant 1's consolidation findings (Plant 1 customer forms were mostly Tier 2 candidates).

---

#### PHASE 3: Critical Gap Analysis (Part B Scope)

1. **The Defect Taxonomy Gap**: With 6 customers and 16 inspection/production forms, how fragmented is the defect taxonomy? How does this compare to Plant 1's 97 unique defect strings → 38 normalized types?

2. **The Inspection-to-NCR Gap**: When a defect is found on an inspection form, is there any mechanism to trigger an NCR? Or do inspection rejects stay on the inspection form with no escalation pathway?

3. **The Customer Requirements Gap**: Are customer-specific inspection requirements documented on the forms, or assumed knowledge? If the inspection form just has generic defect categories, where are the customer-specific acceptance criteria?

4. **The GP-12 Gap**: Beyond Polycon/Tesla, do other customers have GP-12 requirements that are NOT captured in dedicated forms? How do GP-12 inspection results flow to shipping release decisions?

5. **The Shipping-Quality Disconnect**: Is there any linkage between quality inspection results and shipping authorization? Can parts be shipped without passing inspection?

6. **The Cost Visibility Gap**: Can customer chargebacks, scrap costs, and rework costs be calculated from these forms?

7. **The Traceability Completeness Assessment**: Taking Part A's operational traceability findings and Part B's customer/shipping findings together, score the end-to-end traceability chain: Raw receipt → Loading → Coating → Inspection → Post-paint → Packing → Shipping. Where are the breaks?

---

#### PHASE 4: Platform Impact Assessment (Part B Scope)

**A. DATABASE IMPACT**

1. **Existing Entity Coverage Score**: For customer inspection and shipping, rate coverage (0-100%).

2. **New Entity Proposals**: For `InspectionRecord`, `InspectionTestResult`, `CustomerInspectionProfile`, `PackSlip`/`ShipmentRecord`, propose concise entity definitions with fields, FKs, cardinality, and RLS requirements.

3. **Defect Taxonomy Seed Data** (COMPLETE — merge Part A operational defects with Part B customer-specific defects):
   | Form Defect Name | ProposedParentCode (L1) | ProposedParentName (L1) | ProposedDefectCode (L2) | ProposedDefectName (L2) | LineTypeCode | DefaultSeverityId (1-10) | SortOrderHint | Notes |

4. **Reference Data Gaps**: New Customer entries, Part entries, customer-specific test method references, etc.

5. **DispositionCode Coverage**: Map disposition decisions from inspection forms to existing 11 codes.

**B. API IMPACT**
1. Inspection record CRUD and query endpoints needed
2. Shipping/receiving endpoints needed
3. Customer inspection profile configuration endpoints
4. GP-12 containment tracking endpoints (beyond existing NCR containment)
5. Query/reporting endpoints implied by shipping performance forms

**C. FRONTEND/UI IMPACT**
1. **Screen Inventory**: Proposed screens for inspection and shipping, with form consolidation reflected
2. **Form Consolidation Map**: Customer-specific forms grouped into Tier 1/2/3 with overlap percentages
3. **Workflow UX Patterns**: Approval chains, escalation triggers, multi-step wizards
4. **Dashboard Data Sources**: Shipping KPIs, customer delivery performance, inspection pass rates

---

#### PHASE 5: Consolidated Plant 2 Assessment

Synthesize Part A and Part B into a unified Plant 2 assessment:

1. **Overall Plant 2 Readiness Score** (0-100, same methodology as Plant 1's 30/100)
2. **Plant 2 vs Plant 1 Comparison Summary Table**:
   | Dimension | Plant 1 Score | Plant 2 Score | Notes |
3. **Confirmed Cross-Plant Universal Patterns** (extends Plant 1 list)
4. **Plant 2-Specific Patterns** (liquid paint, post-paint ops, paint mix)
5. **Complete Entity Proposal Summary** (merge Part A and Part B proposals into one prioritized list)
6. **Complete Defect Taxonomy** (merge Part A and Part B into final mapping table)
7. **Normalization Recommendations for Plants 3-7**: What should auditors look for next?

---

### Output Format

Structure your full report with the following sections:

### Mandatory Staged Delivery (Prevents Compaction)

You MUST deliver this report in staged batches. Do NOT attempt to output the full report in one response.

Required batch order:
- **Batch B1**: Section 1 (Executive Summary) + Section 2 (File Inventory Table)
- **Batch B2**: Section 3 (Detailed Analysis) subsection A
- **Batch B3**: Section 3 (Detailed Analysis) subsections B-C + Section 4 (Critical Gap Analysis)
- **Batch B4**: Section 5 (Platform Impact Assessment) + Section 6 (Consolidated Plant 2 Assessment)
- **Batch B5**: Appendix A + Appendix B
- **Batch B6**: Appendix C + Appendix D + Appendix E

Required batch controls:
- End every batch with:
  - `BATCH_ID: B#`
  - `COMPLETED_SECTIONS: <section numbers/titles>`
  - `NEXT_BATCH_STARTS_WITH: <exact next heading>`
- Then STOP and wait for the user to reply `CONTINUE`.
- Never restate completed sections; output net-new content only.
- If any table is too large, split it into labeled chunks (`Part 1`, `Part 2`, etc.) and continue remaining rows in the next batch.

Output constraints:
- Markdown tables for all tabular outputs
- Fenced `csv` blocks for appendices (CSV-ready)
- Evidence (file path + sheet/tab) and Confidence (High/Medium/Low) for every finding
- `UNKNOWN` for missing data (do not invent)

1. **Executive Summary** (blunt assessment, Plant 2 overall readiness score, comparison to Plant 1)
2. **File Inventory Table** (Phase 1)
3. **Detailed Analysis by Category** (Phase 2 — all subsections A through C)
4. **Critical Gap Analysis** (Phase 3 — all 7 gaps)
5. **Platform Impact Assessment** (Phase 4 — DB, API, UI)
6. **Consolidated Plant 2 Assessment** (Phase 5)
7. **Appendix A: Complete Defect Taxonomy Mapping Table** (merged Part A + Part B)
8. **Appendix B: Form-to-Entity Field Mapping** (all Part B forms)
9. **Appendix C: Form Consolidation Matrix** (Tier 1/2/3 with overlap % and justification)
10. **Appendix D: Complete Proposed Entity Schemas** (merged Part A + Part B, SQL + JSON)
11. **Appendix E: Cross-Plant Normalization Checklist** (updated with Plant 2 data)

Be direct. Be specific. Use form document numbers and file names when referencing issues.
