# BATCH A4: Section 5 + Section 6 + Section 10

---

## Section 5: Platform Impact Assessment (Part A Scope)

### A. DATABASE IMPACT

#### A1. Existing Entity Coverage Score

| Form Category | # Forms | Existing Entity Coverage | Score | Notes |
|---|---|---|---|---|
| **PRODUCTION TRACKING** (Load sheets, production tracking, production reports) | 5 | `dbo.ProductionLine`, `dbo.Equipment`, `dbo.Shift`, `dbo.Part`, `dbo.Customer` exist as reference data. No transactional production run/load entity exists. | 10% | Reference tables cover metadata; zero coverage of actual production events |
| **PROCESS CONTROL** (Oven verification, temp logs, operating forms, programs, paint trials) | 5 | `dbo.ProductionLine`, `dbo.Equipment` for reference. No process parameter capture entity exists. | 5% | Only static reference data matches; the actual parameter readings have no home |
| **PAINT MIX / CHEMISTRY** (Paint tally, inventory, mix info, pressure pot label, solvent tracking, batch verification) | 6 | `dbo.Supplier` covers paint suppliers. No PaintBatch/PaintMix entity exists. | 8% | Supplier reference matches; all batch-level data is uncovered |
| **MAINTENANCE / PM** (Rack burn-off, booth cleaning, pot cleaning, robot maint, TPM, maint log, sander maint, sanding booth maint) | 10 | `dbo.Equipment` for equipment references. No MaintenanceRecord entity exists. | 5% | Equipment exists conceptually but Plant 2 equipment isn't seeded |
| **WASTE MANAGEMENT** (Booth sludge, still bottoms, waste paint, waste zinc, empty) | 5 | Nothing. Zero entity coverage. | 0% | Drum labels with no data fields — entity needed AND data capture process needed |
| **POST-PAINT OPERATIONS** (Sanding, buffing, deburring tallies, buffing summary) | 5 | Nothing. Zero entity coverage. | 0% | Entire operation domain is unrepresented in database |
| **SCHEDULING / LABOR / DOWNTIME** (Schedules, painter lineup, downtime tracking) | 7 | `dbo.Shift`, `dbo.ProductionLine` for reference. No DowntimeEvent entity exists. | 8% | Downtime categories are quality-relevant but have no entity |
| **LABELS / TAGS** (Hold, rework, finished goods, use next, approved tag tracking) | 10 | `quality.NCR.StatusCodeId`, `dbo.StatusCode`, `dbo.DispositionCode` cover the concept of hold/rework/scrap decisions. But no tag-to-NCR bridge exists because NCRs aren't being created. | 25% | The disposition code system maps well to tag semantics; the gap is that tags exist without NCRs |
| **DOCUMENT CONTROL** (Change tracker) | 1 | `dbo.DocumentSequence` exists for auto-numbering. No DocumentTemplate/Revision entity exists. No PaintTrial entity. | 5% | Numbering infrastructure exists; content management doesn't |

**Weighted Overall Coverage: ~7%** — The existing sf-quality database is built around quality event management (NCR/CAPA/SCAR/Complaint). The operational production domain (runs, batches, parameters, maintenance, waste, post-paint) is almost entirely absent. This is expected — the database was designed for quality, not MES — but it means the operational forms need either new sf-quality entities or an explicit interface boundary with a separate production system.

#### A2. New Entity Proposals

Detailed entity definitions were provided in the Detailed Analysis sections. Summary of all proposed entities:

| Proposed Entity | Schema | Primary Source Forms | Relationship to Existing | Cardinality | Temporal Versioning? | RLS? |
|---|---|---|---|---|---|---|
| ProductionRun | production | 8.2.2.1.5, 8.2.2.2.1, 8.2.2.2.4, 8.2.2.2.7, 8.2.2.29 | FK → `dbo.ProductionLine`, `dbo.Shift`, `dbo.Part`, `dbo.Customer`, `dbo.Plant` | Many runs per line per day | No | Yes |
| PaintBatch | production | 8.2.2.1.18, 8.2.2.23, 8.2.2.24 | FK → `dbo.Supplier`, `dbo.ProductionLine`, `dbo.Plant`; parent of ColourVerification | Many batches per day per line | No | Yes |
| ColourVerification | production | 8.2.2.26 | FK → PaintBatch; standalone verification record | 1:1 with PaintBatch (when verified) | No | Yes |
| MaintenanceRecord | production | 8.2.2.1.1, 8.2.2.1.3, 8.2.2.1.4, 8.2.2.1.19-20, 8.2.2.2.8-10, 8.2.2.32, 8.2.2.34 | FK → `dbo.Equipment`, `dbo.ProductionLine`, `dbo.Plant`; optional FK → `quality.NCR`, DowntimeEvent | Many per equipment per period | No | Yes |
| WasteRecord | production | 8.2.2.17-21 (labels only — net-new capture needed) | FK → `dbo.ProductionLine`, `dbo.Plant` | One per container lifecycle | No | Yes |
| PostPaintOperation | production | 8.2.2.7, 8.2.2.8, 8.2.2.9, 8.2.2.31 | FK → `dbo.Part`, `dbo.Plant`; optional FK → `quality.NCR`, `quality.DefectType`, ProductionRun | Many per operator per day | No | Yes |
| PostPaintDailySummary | production | 8.2.2.30 | FK → `dbo.Plant` | One per operation type per day | No | Yes |
| DowntimeEvent | production | 8.2.2.1.9, 8.2.2.28 | FK → `dbo.ProductionLine`, `dbo.Shift`, `dbo.Plant`; optional FK → `quality.NCR` | Many per line per day | No | Yes |
| PaintTrial | production | 8.2.2.6 (Paint Trial tab), 8.2.2.33 | FK → `dbo.ProductionLine`, `dbo.Supplier`, `dbo.Plant`; optional FK → PaintBatch | Occasional — per trial event | No | Yes |
| DocumentTemplate | admin | 8.2.2.6 (meta), embedded Rev Logs | Standalone | One per form | Yes (revision history) | No (cross-plant) |
| DocumentRevision | admin | Embedded Rev Logs across 7+ forms | FK → DocumentTemplate | Many per template | N/A (child of versioned parent) | No |

**Schema decision:** Proposing a new `production` schema for operational entities. This keeps the `quality` schema focused on NCR/CAPA/SCAR/Complaint/Audit and the `production` schema focused on runs, batches, parameters, maintenance, waste, and post-paint operations. The two schemas connect via foreign keys (e.g., `PostPaintOperation.NcrId → quality.NonConformanceReport`).

#### A3. Defect Taxonomy Seed Data (Partial — Operational Forms Only)

Operational forms in Part A contain very few explicit defect references. The primary defect intelligence will come from Part B (customer inspection forms). What can be extracted from Part A:

| Form Defect Name | ProposedParentCode (L1) | ProposedParentName (L1) | ProposedDefectCode (L2) | ProposedDefectName (L2) | LineTypeCode | DefaultSeverityId (1-10) | SortOrderHint | Notes |
|---|---|---|---|---|---|---|---|---|
| "REJECT" (Hold Tag checkbox) | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | LIQUID | UNKNOWN | — | Hold Tag has reject option but no defect classification. Part B will define. |
| "repeated application defects" (8.2.2.2.7 SWI Step 11) | SURF | Surface Defects | UNKNOWN | UNKNOWN | LIQUID | UNKNOWN | — | Generic reference to spray application defects. Part B inspection forms will enumerate. |
| "breaks in the fan" (8.2.2.2.7 checklist item 14) | APP | Application Defects | FAN_BREAK | Fan Pattern Break | LIQUID | 5 (INFERRED) | 10 | Robot spray pattern interruption — causes uneven coverage |
| "Parts hit in blow off" (8.2.2.28 downtime category) | HAND | Handling Defects | PART_DAMAGE_BLOWOFF | Part Damage at Blow-Off | LIQUID | 4 (INFERRED) | 20 | Incoming part damage before paint |
| "Booth feedback" (8.2.2.28 downtime category) | ENV | Environmental Defects | BOOTH_FEEDBACK | Paint Booth Environmental Feedback | LIQUID | 6 (INFERRED) | 30 | Booth airflow/temperature/humidity excursion |
| Colour deviation (8.2.2.26 ΔEcmc fail) | COLOUR | Colour Defects | COLOUR_DEVIATION | Colour Out of Tolerance | LIQUID | 7 (INFERRED) | 40 | ΔEcmc > 2 or ΔL/a/b > 1.15 for metallics |
| Viscosity deviation (8.2.2.1.18 implied) | MIX | Paint Mix Defects | VISCOSITY_OOT | Viscosity Out of Tolerance | LIQUID | 5 (INFERRED) | 50 | No spec limits documented — existence inferred from viscosity capture fields |

> **Note:** This is an intentionally sparse table. Part A operational forms are not designed to capture defect types. The bulk of defect taxonomy data will come from Part B's customer inspection forms, which Plant 1 analysis showed contain 15+ customer-specific defect lists with ~97 unique strings normalizing to ~38 types.

#### A4. Reference Data Gaps

**ProcessArea values needed for Plant 2:**

| ProcessArea | Code | Description | Line Scope |
|---|---|---|---|
| Paint Kitchen | PAINT_KITCHEN | Paint mixing, storage, inventory | All lines |
| Blow-Off Station | BLOWOFF | Part blow-off/de-stat before prime | 101/103 |
| De-Stat Station | DESTAT | Electrostatic discharge station | 101/103 |
| Primer Booth | PRIME_BOOTH | Primer spray booth | All lines |
| Base Coat Booth 1 | BASE_BOOTH_1 | Base coat spray — Booth 1 | 101/103 |
| Base Coat Booth 2 | BASE_BOOTH_2 | Base coat spray — Booth 2 | 101/103 |
| Base Coat Booth 3 | BASE_BOOTH_3 | Base coat spray — Booth 3 | 101/103 |
| Base Coat Booth 4 | BASE_BOOTH_4 | Base coat spray — Booth 4 | 101/103 |
| Base Coat Robot | BASE_ROBOT | Robotic base coat application | 102 |
| Clear Coat Robot | CLEAR_ROBOT | Robotic clear coat application | 102 |
| Flash Tunnel | FLASH_TUNNEL | Flash-off zone between coats | All lines |
| Cure Oven | CURE_OVEN | Cure/bake oven | All lines |
| Vestibule | VESTIBULE | Post-oven cooling vestibule | 102 |
| Sanding Booth | SAND_BOOTH | Post-paint sanding station | General |
| Buffing Area | BUFF_AREA | Post-paint buffing station | General |
| Deburring Station | DEBURR_STATION | Pre-paint or post-paint deburr | General |
| Waste Storage | WASTE_STORAGE | Waste drum storage area | General |

**Equipment entries needed:**

| Equipment | Type | LineId | Notes |
|---|---|---|---|
| Line 101 Oven | OVEN | 101 | From 8.2.2.1.16 |
| Line 103 Oven | OVEN | 103 | From 8.2.2.1.16 |
| Line 102 Basecoat Robot | ROBOT | 102 | From 8.2.2.2.7, 8.2.2.2.8 |
| Line 102 Clearcoat Robot | ROBOT | 102 | From 8.2.2.2.7, 8.2.2.2.8 |
| Line 101 P-Mix System (Base) | PMIX | 101 | From 8.2.2.1.20 |
| Line 101 P-Mix System (Clear) | PMIX | 101 | From 8.2.2.1.20 |
| Line 103 P-Mix System (Base) | PMIX | 103 | From 8.2.2.1.19 |
| Line 103 P-Mix System (Clear) | PMIX | 103 | From 8.2.2.1.19 |
| Line 102 P-Mix System (Base) | PMIX | 102 | From 8.2.2.2.8, 8.2.2.2.10 |
| Line 102 P-Mix System (Clear) | PMIX | 102 | From 8.2.2.2.8, 8.2.2.2.10 |
| Sander 1–6 | SANDER | General | From 8.2.2.32 |
| Sanding Booth | BOOTH | General | From 8.2.2.34 |
| Pressure Pots (numbered) | PRESSURE_POT | Per-line | From 8.2.2.24 |
| Line 101 Booths 1–4 + Primer | SPRAY_BOOTH | 101 | From 8.2.2.1.3 |
| Line 103 Booths 1–4 + Primer | SPRAY_BOOTH | 103 | From 8.2.2.1.3 |
| Racks (65+ named racks) | RACK | 101/103 | From 8.2.2.1.1 — LH/RH Fairings, Scoops, Fenders, Hoods, etc. |

**Supplier entries needed (Paint Suppliers):**

| Supplier | Products | Source |
|---|---|---|
| NB Coatings | Sierra Black, Summit White, Clear Coat, Base Catalyst, Clear Catalyst, Anti-Chip Primer | 8.2.2.5/Rev 7 |
| BASF | BMW Black II, Evergloss 905 Clear, Hardener | 8.2.2.5/Rev 7 |
| Red Spot | Conductive Grey Primer | 8.2.2.5/Rev 7 |
| US Paint | Ad Pro Primer | 8.2.2.25 |
| NPAA | Anti Chip Primer | 8.2.2.25 |
| UNIVAR | MEK, MAK, Xylene, IBA, SC150, Alcohol, Virgin Purge (solvents) | 8.2.2.25 |

#### A5. DispositionCode Coverage

Mapping every disposition decision found in Part A forms to existing 11 codes:

| Observed Decision | Form Source | Existing DispositionCode | Match Quality |
|---|---|---|---|
| "REJECT" on Hold Tag | 8.2.2.12 | SCRAP or REWORK — ambiguous without further data | LOW — reject could mean either |
| "REINSPECT" on Hold Tag | 8.2.2.12 | SORT | MEDIUM — reinspect ≈ sort/inspect to determine acceptability |
| "REVIEW" on Hold Tag | 8.2.2.12 | PENDING_CUST or none — review is a process step, not a disposition | LOW |
| "Rework- To Be Sanded" tag | 8.2.2.15 | REWORK | HIGH |
| "To Be Buffed" tag | 8.2.2.16 | REWORK or BLEND | MEDIUM — routine buffing vs defect-driven |
| "Sanded- Ready For Paint" tag | 8.2.2.10 | RECOAT or STRIP_RECOAT | HIGH — sanded and awaiting recoat |
| "Approved Tag Tracking" entries | 8.2.2.2.17 | USE_AS_IS or CUST_DEV | INFERRED — "approved" implies material accepted despite deviation |
| "RW" column on Load Sheet | 8.2.2.1.5 | REWORK or RECOAT | MEDIUM — RW = rework quantity loaded for reprocess |

**Codes NOT observed in Part A:** SCRAP (explicit), RTS (Return-to-Supplier), STRIP_RECOAT (explicit), ENG_DEV (Engineering Deviation). These are likely to appear in Part B customer inspection forms where formal disposition decisions are documented.

---

### B. API IMPACT

#### B1. Missing Endpoints for Part A Data Flows

The current API (v0.3.0) has 30 endpoints — 25 NCR-specific, 3 thin placeholders (SCAR, Audit, 8D), and 2 diagnostics. Zero endpoints exist for production operations. The following would be needed:

| Proposed Endpoint | Method | Purpose | Priority |
|---|---|---|---|
| `/v1/production/run` | POST | Create production run record | HIGH |
| `/v1/production/run/{id}/carriers` | POST | Add carrier/rack-level data to run | HIGH |
| `/v1/production/run/{id}/parameters` | POST | Record spray parameters per carrier | HIGH |
| `/v1/production/run/daily` | GET | Daily production summary by line | MEDIUM |
| `/v1/production/paint-batch` | POST | Create paint batch record | HIGH |
| `/v1/production/paint-batch/{id}/verification` | POST | Record colour verification results | HIGH |
| `/v1/production/paint-batch/active` | GET | Currently active batches by line | MEDIUM |
| `/v1/production/maintenance` | POST | Create maintenance record | MEDIUM |
| `/v1/production/maintenance/schedule` | GET | Upcoming scheduled maintenance | LOW |
| `/v1/production/maintenance/overdue` | GET | Overdue maintenance items | MEDIUM |
| `/v1/production/waste` | POST | Create waste record | LOW (net-new process) |
| `/v1/production/waste/summary` | GET | Waste summary by period/stream | LOW |
| `/v1/production/post-paint` | POST | Record post-paint operation | HIGH |
| `/v1/production/post-paint/daily-summary` | GET | Daily buffing/sanding summary | MEDIUM |
| `/v1/production/post-paint/ftq` | GET | FTQ trend by operation type | MEDIUM |
| `/v1/production/downtime` | POST | Record downtime event | MEDIUM |
| `/v1/production/downtime/summary` | GET | Downtime summary by category/line/period | MEDIUM |
| `/v1/production/paint-trial` | POST | Create paint trial record | LOW |

#### B2. Query/Reporting Endpoints Implied by Forms

| Report Need | Source Form | Proposed Endpoint | Notes |
|---|---|---|---|
| Daily production by line (racks, parts, FTQ) | 8.2.2.29 | `GET /v1/reports/production/daily` | Replaces Daily Production Report Template |
| Buffing efficiency dashboard | 8.2.2.30 | `GET /v1/reports/post-paint/buffing-summary` | Daily/monthly/trend views |
| Paint consumption by colour/supplier | 8.2.2.1.18, 8.2.2.5 | `GET /v1/reports/paint/consumption` | Joins batch data with inventory costs |
| Downtime Pareto by category | 8.2.2.28 | `GET /v1/reports/downtime/pareto` | Minutes by category by line by period |
| Rack burn-off compliance | 8.2.2.1.1 | `GET /v1/reports/maintenance/rack-burnoff` | Weekly compliance tracker |
| Solvent usage trend | 8.2.2.25 | `GET /v1/reports/paint/solvent-usage` | Regulatory and process trending |
| Colour verification history | 8.2.2.26 | `GET /v1/reports/paint/colour-verification` | Pass/fail history by colour/supplier |

---

### C. FRONTEND/UI IMPACT

#### C1. Proposed UI Screens to Replace Part A Forms

| Screen | Replaces Forms | Key Features | User Persona |
|---|---|---|---|
| Production Run Entry | 8.2.2.1.5, 8.2.2.2.1, 8.2.2.2.4, 8.2.2.29 | Line selector, part/customer dropdowns, per-carrier parameter entry, real-time rack counting, auto-timestamp | Line Operator, Supervisor |
| Line 102 Application Tracker | 8.2.2.2.7 (Option 2) | Digitized checklist with value fields, per-carrier row entry, parameter validation against specs (when defined), supervisor sign-off workflow | Robot Operator, Supervisor |
| Paint Kitchen Console | 8.2.2.1.18, 8.2.2.23, 8.2.2.24, 8.2.2.25, 8.2.2.5 | Batch creation wizard (colour → supplier → mix), viscosity entry with target display, auto-generate pressure pot labels, solvent consumption tracker, inventory dashboard | Paint Mixer |
| Colour Verification Entry | 8.2.2.26 | L/a/b data entry at 25°/45°/75°, auto-calculate ΔEcmc, pass/fail indicator, link to paint batch, approval workflow | Lab/Quality Tech |
| Maintenance Dashboard | 8.2.2.1.3, 8.2.2.1.4, 8.2.2.1.19-20, 8.2.2.2.8-10, 8.2.2.32, 8.2.2.34 | Task checklists by line/equipment, frequency indicators (daily/weekly/monthly), completion tracking, overdue alerts | Operator, Maintenance Lead |
| Downtime Logger | 8.2.2.1.9, 8.2.2.28 | Quick-entry: line, start time, category dropdown, process stage; auto-calculate duration; monthly rollup view | Operator, Supervisor |
| Post-Paint Tally | 8.2.2.7, 8.2.2.8, 8.2.2.9, 8.2.2.31 | Operator selects operation type, scans/selects part, enters quantity, optionally links to NCR/defect, auto-calculate daily totals | Sander/Buffer/Deburrer |
| Buffing Summary Dashboard | 8.2.2.30 | Auto-calculated from PostPaintOperation records: daily/monthly totals, per-person efficiency, FTQ trend, return-to-buff rate | Supervisor, Quality Manager |
| Production Schedule Viewer | 8.2.2.1.6, 8.2.2.1.11, 8.2.2.2.3 | Read-only view of schedule (remains in MES/planning system); provides context for production run entry | Supervisor |
| Tag/Label Printer | 8.2.2.10-16, 8.2.2.17-22, 8.2.2.24, 8.2.2.27 | Generate printable labels from NCR/production status; hold tags auto-linked to NCR; waste labels linked to WasteRecord; pressure pot labels linked to PaintBatch | All |
| Paint Trial Entry | 8.2.2.6, 8.2.2.33 | Trial creation wizard: reason, parameters changed, per-booth settings, result, link to paint batch | Quality Engineer, Supervisor |

#### C2. Workflow UX Patterns Discovered

| Pattern | Source | UX Implementation |
|---|---|---|
| Start-of-shift checklist with value capture | 8.2.2.2.7 (18-item checklist with operator + supervisor initials) | Guided checklist UI: each item requires value entry or pass/fail, then operator signs, then supervisor counter-signs. Block production start if critical items incomplete. |
| Supervisor sign-off gate | 8.2.2.2.7 Step 4 (cup test + fan test require supervisor sign-off), Step 18 (Start Up Approved) | Approval workflow: operator submits, supervisor reviews and approves via separate auth. Maps to `workflow.ActionItem` with separation of duties. |
| Sequential daily → monthly rollup | 8.2.2.1.9 (daily event log) → 8.2.2.28 (monthly tracking template) | Automatic aggregation: daily entries auto-roll into monthly dashboard. Eliminates manual re-entry. |
| Per-operator labour tracking | All tally sheets, Buffing Summary by-name columns | Operator-scoped views: each operator sees their own tally; supervisor sees team-level summary. |
| Recipe/program verification | 8.2.2.2.6 (Programs reference), 8.2.2.2.7 checklist items 10-11 (queue verification) | Program lookup: operator selects part/colour, system displays correct job number; operator confirms match against teach pendant. |
| Print-and-attach label generation | All tag templates (8.2.2.10-22, 8.2.2.24) | Label printing from app: when an NCR is created with REWORK disposition, system offers to print a "Rework- To Be Sanded" label. When a PaintBatch is created, system offers to print Pressure Pot Labels. |
| Colour verification approval chain | 8.2.2.26 ("Approved By" field, pass/fail gate) | Two-stage verification: tech enters readings → system auto-calculates ΔEcmc → pass/fail displayed → approver signs off. Fail triggers hold on batch. |

#### C3. Dashboard Data Sources from Tracking/Summary Forms

| Dashboard Widget | Data Source Entity | Metrics | Refresh |
|---|---|---|---|
| Production throughput by line | ProductionRun | Racks/day, parts/day, FTQ% | Real-time |
| Buffing efficiency | PostPaintDailySummary | Parts buffed, avg/person, avg/hr, % efficiency, FTQ | Daily |
| Downtime Pareto | DowntimeEvent | Minutes by category, by line, trend | Daily |
| Paint consumption | PaintBatch | Gallons consumed by colour, cost by colour, batches/day | Daily |
| Colour verification pass rate | ColourVerification | Pass/fail trend by supplier/colour | Per-event |
| Maintenance compliance | MaintenanceRecord | % tasks completed on time by line, overdue count | Daily |
| Rack burn-off tracking | MaintenanceRecord (subtype) | Racks burned off per week, compliance % | Weekly |
| Solvent usage trend | PaintBatch (solvent fields) + WasteRecord | Gallons consumed vs waste generated, net efficiency | Weekly |
| Waste generation | WasteRecord | Volume by stream, cost by stream, trend | Monthly |
| Rework pipeline | PostPaintOperation (IsRework = true) | Parts in sanding queue, buffing queue, deburring queue | Real-time |

---

## Section 6: Cross-Plant Comparison (vs Plant 1)

### 6.1 Confirmed Universal Patterns

| Pattern | Plant 1 Evidence | Plant 2 Confirmation | Implication |
|---|---|---|---|
| No formal NCR system | Zero NCR forms in Plant 1 package; nonconformances scattered across unlinked forms | Zero NCR forms in Plant 2 Part A package; Hold Tags are the only nonconformance indicator | Company-wide gap. The sf-quality NCR entity is solving a problem that has never been formally managed at either plant. Roll-out will require cultural change, not just technology deployment. |
| Broken traceability chain | Load-to-production chain broken; no consistent rack/batch identifier | Same breaks. Load Sheet → Production Tracking → Post-Paint all disconnected. Line 102 has partial carrier tracking but no upstream/downstream links. | Universal. The ProductionRun entity proposal must enforce a linking key (CarrierId or RackNumber) that flows through all downstream records. |
| Process data collected but never analyzed | Bath chemistry readings captured without trending or SPC | Spray parameters, viscosity, temperatures captured without spec limits, trending, or SPC. Only ΔEcmc has documented tolerance. | Universal. The digital platform must include parameter specification tables and trend visualization from day one, or operators will treat digital entry the same way they treat paper — as compliance theater. |
| Post-paint operations disconnected | Limited post-paint data in Plant 1 (powder coat); buffing/sanding less prevalent | Extensive post-paint operations (sanding, buffing, deburring) with zero backward traceability to production run or defect | Universal pattern, but significantly more impactful in Plant 2 due to volume of post-paint rework in liquid paint operations. |
| Fragmented defect terminology | 97 unique defect strings across 15+ forms normalizing to ~38 types | Part A shows minimal explicit defect vocabulary; Part B will likely reveal similar fragmentation in customer inspection forms | Expected to confirm at Plant 2 scale — await Part B data. |
| Tags/labels as informal quality status | Physical tags used for hold/rework without NCR linkage | Identical pattern: 10 tag types, none linked to formal quality events | Universal. Tag printing should become an NCR workflow output, not a standalone process. |
| Document control immaturity | Near-zero revision tracking | Marginally better (7 Rev Logs), but 46 of 53 forms still lack revision history. Two forms from 2016 still in active file structure. | Universal with slight Plant 2 improvement. |

### 6.2 New Plant 2-Specific Patterns

| Pattern | Plant 2 Evidence | Plant 1 Comparison | Impact |
|---|---|---|---|
| Paint mix batch traceability | Daily Paint Tally Sheet captures batch #, viscosity (raw/reduced), solvent amounts, agitation time, temperature, filter sizes per mix | Plant 1's e-coat equivalent was bath analysis — continuous monitoring of a shared tank, not discrete batch preparation | Fundamentally different data model. Plant 1 needs a BathAnalysis entity (periodic readings of a persistent system). Plant 2 needs a PaintBatch entity (discrete mix events with lifecycle: mixed → active → consumed/expired). |
| Colour verification with lab-grade data | New Paint Batch Verification captures L/a/b colorimetry at 3 angles with ΔEcmc calculation and pass/fail criteria | No equivalent in Plant 1 (powder coat colour verification not documented in operational forms) | Plant 2-specific. The ColourVerification entity is liquid-paint-specific and may not apply to powder coat or e-coat. |
| Robotic spray program management | Line 102 Programs document maps part/colour combinations to robot job numbers and valve/preset configurations | Plant 1 had no robotic application documentation in audit scope | Plant 2-specific to Line 102. The robot program reference data maps to `dbo.Equipment` configuration but needs a RobotProgram or SprayRecipe reference table. |
| Post-paint operations at scale | 5 dedicated tally sheet forms, Buffing Summary with 272 days of daily data, Hummer Sanding (product-specific), 6 individual sander units | Plant 1 had minimal post-paint rework documentation | Plant 2 volume is dramatically higher — liquid paint generates significantly more surface defects requiring sanding/buffing than powder coat. This is the dominant rework pathway. |
| Solvent/waste management complexity | 7 solvent types tracked, 5 waste stream labels, solvent reduction ratios per paint mix | Plant 1 had minimal waste documentation (no solvent reduction in powder coat) | Plant 2-specific. Regulatory exposure is higher — liquid paint operations generate hazardous waste (MEK, Xylene, MAK) that requires RCRA-level tracking. |
| Multi-stage spray process | Primer → Base Coat → Clear Coat with separate parameter capture per stage, flash time between stages | Plant 1 powder coat was predominantly single-stage application | Plant 2 process is 3x more complex per part. The ProductionRun entity needs per-stage parameter sub-records (primer parameters, base parameters, clear parameters). |
| Paint trial management | Two dedicated forms (Change Tracker + Paint Trial Information Sheet) with detailed trial documentation | Not documented in Plant 1 | Plant 2-specific. Indicates a more formalized PPAP/change management culture for paint processes. |

### 6.3 Plant 2 Improvements over Plant 1

| Area | Plant 2 Advantage | Evidence |
|---|---|---|
| Line 102 Operating Form | Best single form in either plant audit. Combines SWI, start-up checklist with actual values, per-carrier production data, and supervisor sign-off. | 8.2.2.2.7 Option 2 — captures 18 checklist items with values + per-carrier parameters |
| Revision logs | 7 forms have embedded Rev Log tabs with creation dates, revision dates, author initials, and change descriptions | 8.2.2.4, 8.2.2.5, 8.2.2.7, 8.2.2.8, 8.2.2.9, 8.2.2.31 Rev Log tabs |
| Buffing Summary analytics | Pre-built KPI calculations (efficiency %, FTQ, average per person/hour) with 272 days of trend data | 8.2.2.30 Charts Info tab |
| Paint batch verification rigour | Lab-grade incoming colour verification with quantified acceptance criteria (ΔEcmc < 2) | 8.2.2.26 |
| Downtime categorization | Pre-defined 15-category downtime taxonomy per process stage, tracked per line per day per month | 8.2.2.28 |
| Schedule template sophistication | Master reference sheets for parts, cycle times, paint usage forecasting, and robot job programs | 8.2.2.1.6, 8.2.2.1.11, 8.2.2.2.3 |
| Paint Kitchen Inventory with costing | Inventory tracker with vendor part numbers, product codes, min/max quantities, container sizes, and per-unit CAD cost | 8.2.2.5 Rev 7 |

### 6.4 Plant 2 Regressions from Plant 1

| Area | Plant 2 Disadvantage | Evidence |
|---|---|---|
| Line asymmetry | Line 102 has 9 dedicated forms with carrier-level tracking; Lines 101/103 share 14 forms with no per-rack granularity | 8.2.2.2.* vs 8.2.2.1.* — Line 102 is a different generation of data capture |
| Stale critical forms | Two process control forms from December 2016 (9+ years old) still in the active file structure | 8.2.2.1.2, 8.2.2.1.16 — Paint Kitchen Temp Log and Oven Verification Log |
| Waste tracking | Plant 2 has drum labels with zero data fields; at least Plant 1 had some waste-related documentation | 8.2.2.17-21 — all five files are label-only |
| Approved Tag Tracking abandoned | The only quality event register in the package hasn't been updated since November 2018 | 8.2.2.2.17 — 7+ years stale |
| Buffing Summary data gaps | Formulas built for FTQ analysis but "Into Buff from Line" column is empty, causing #DIV/0! errors throughout | 8.2.2.30 — most months show systematic data entry failure |
| Schedule template broken formulas | Paint Usage tab in 101 Schedule Template shows #REF! errors across all cells | 8.2.2.1.6/Paint Usage — broken external references |

### 6.5 Cross-Plant Normalization Checklist Update

| Checklist Item | Plant 1 Status | Plant 2 Status (Part A) | Normalized Requirement |
|---|---|---|---|
| Formal NCR form exists | ❌ Absent | ❌ Absent | `quality.NonConformanceReport` — mandatory for both plants |
| Per-rack/carrier production tracking | ❌ Absent | ⚠️ Partial (Line 102 only) | `production.ProductionRun` with carrier-level child records |
| Load sheet with rack/carrier ID | ❌ Absent | ❌ Absent (date+line only) | Add CarrierId/RackNumber to all load records |
| Paint batch traceability | N/A (e-coat bath) | ⚠️ Partial (batch # captured but not linked to production) | `production.PaintBatch` with FK to ProductionRun |
| Process parameter spec limits | ⚠️ Partial (some bath limits) | ⚠️ Partial (ΔEcmc only) | Parameter specification table with target/USL/LSL per parameter per product |
| Post-paint rework linked to defect | ❌ Absent | ❌ Absent | `production.PostPaintOperation.DefectTypeId` + FK to NCR |
| Maintenance linked to equipment ID | ⚠️ Informal | ⚠️ Informal (line-level, not asset-tagged) | `production.MaintenanceRecord.EquipmentId` FK to `dbo.Equipment` |
| Waste volume tracking | ⚠️ Minimal | ❌ Absent (labels only) | `production.WasteRecord` — net-new for Plant 2 |
| Downtime categorization | ❌ Absent or free-text | ✅ 15-category taxonomy | Adopt Plant 2's taxonomy as cross-plant standard |
| Document revision tracking | ❌ Near-zero | ⚠️ Partial (7 of 53 forms) | `admin.DocumentTemplate` + `DocumentRevision` |
| Cost visibility | ❌ Absent | ⚠️ Partial (paint inventory costs only) | `quality.NcrCostLedger` + paint consumption × unit cost |
| Defect taxonomy standardized | ❌ 97 strings → ~38 types | ⏳ Part B will reveal | `quality.DefectType` hierarchy — await Part B |
| Colour verification with lab data | N/A | ✅ ΔEcmc pass/fail at 3 angles | `production.ColourVerification` — Plant 2-specific |
| Supervisor sign-off workflows | ❌ Absent | ✅ On Line 102 Operating Form | `workflow.ActionItem` with verifier ≠ completer |

---

## Section 10: Part A Summary for Part B Handoff

### Part A Key Findings (for Part B Context)

**Scope:** 53 forms, 129 worksheet tabs covering Line Operations & Process Control for Plant 2 (Lines 101, 102, 103 — liquid spray paint).

**Digital Readiness Score:** 28/100 (vs Plant 1's 30/100).

**Critical gaps confirmed (universal pattern):**

1. **No formal NCR system** — zero NCR forms exist. Hold Tags are the most primitive quality event indicator.
2. **Broken traceability** — no consistent identifier flows from load → paint batch → spray parameters → post-paint rework. Line 102 has partial carrier tracking; Lines 101/103 have none.
3. **Process-quality disconnect** — process data and quality outcomes are captured in completely separate systems with no cross-reference.
4. **Post-paint is an accountability black hole** — sanding/buffing/deburring tally sheets capture labor but no defect type, production source, or root cause.
5. **Waste tracking is non-functional** — five drum labels with zero data fields.

**Plant 2-specific findings:**

- **Line 102 Operating Form** (8.2.2.2.7) is the best form in either plant — SWI + checklist + per-carrier parameters + supervisor sign-off.
- **Paint batch data** (batch #, viscosity, solvent, agitation, filters) is captured on the Daily Paint Tally Sheet but not linked to production records.
- **Colour verification** (8.2.2.26) captures lab-grade ΔEcmc data with pass/fail criteria — the only process parameter with documented spec limits.
- **Buffing Summary** (8.2.2.30) has 272 days of daily KPIs but critical input fields are unpopulated.
- **Downtime Tracking** (8.2.2.28) has a 15-category taxonomy per process stage — propose as cross-plant standard.

### Entity Proposals from Part A

- `production.ProductionRun` (+ carrier-level children)
- `production.PaintBatch` + `production.ColourVerification`
- `production.MaintenanceRecord`
- `production.WasteRecord`
- `production.PostPaintOperation` + `production.PostPaintDailySummary`
- `production.DowntimeEvent`
- `production.PaintTrial`
- `admin.DocumentTemplate` + `admin.DocumentRevision`

### Defect Taxonomy from Part A

Only 7 entries extracted (operational forms lack explicit defect vocabulary). Part B customer inspection forms are expected to yield the bulk of defect taxonomy data — comparable to Plant 1's 97 unique strings.

### Open Questions for Part B

1. Do customer inspection forms contain formal defect lists that can seed the `quality.DefectType` hierarchy for LIQUID line type?
2. Is there any NCR or nonconformance tracking embedded in customer-specific forms?
3. Do shipping/packaging forms have lot/batch traceability fields that connect back to production records?
4. Are disposition decisions (scrap, rework, use-as-is) documented in customer inspection forms?
5. Do any Part B forms reference the Approved Tag Tracking system (8.2.2.2.17) that was abandoned in 2018?
6. Is FTQ captured at the customer inspection level, and does it correlate with the Buffing Summary's FTQ calculations?
