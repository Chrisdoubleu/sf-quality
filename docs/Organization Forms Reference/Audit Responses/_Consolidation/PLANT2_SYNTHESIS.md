# Plant 2 QSA Audit — Final Synthesis

**Plant:** Select Finishing Plant 2 (Liquid Spray Paint — Lines 101, 102, 103)
**Synthesis Date:** 2026-02-24
**Status:** COMPLETE — Dual-AI audit synthesized (Claude Part A + Part B, ChatGPT 3 batches)

---

## 1. What Was Audited

- **84 current forms + 7 obsolete exemplars** across 4 document families: Line 101-103 Operating Forms, Line 102 Operating Forms, Production Forms by Customer, Shipping Forms
- **205 obsolete files** listed in manifest but NOT included in audit (content unknown)
- **8 customers** served: Rollstamp/BMW, Mytox, Laval Tool, Metelix, KB Components, Polycon/Tesla, BRP/Spyder (hidden), Misc
- **2 AI auditors** produced independent reports: Claude (complete — Part A: 53 operational forms, Part B: 31 customer/shipping forms) + ChatGPT (complete — 3 batches covering all 84 forms + 7 obsolete exemplars)
- **No codebase assessment** — to be performed after synthesis (DB entity coverage estimated at 7-8%)

---

## 2. Overall Readiness Score: 25/100

Plant 2's quality data system is a **liquid paint operation drowning in uncontrolled documents** — Line 102 has a semi-serious data capture system while Lines 101/103 are essentially undocumented. The 2.4:1 obsolete-to-current form ratio (205:84) indicates severe document control failure. A quality engineer **cannot** trace a customer complaint back through this system reliably.

| Dimension | Claude Score | ChatGPT Score | Consensus Score | Key Evidence |
|-----------|-------------|---------------|-----------------|-------------|
| NCR/Disposition | 10/100 | ~12/100 | **10** | Zero NCR capability. Hold tags are printable labels only. Paint Trial is closest form to a deviation but has no NCR linkage. Disposition implied via routing buckets (Good/Buff/Repaint/Scrap) not formally captured. |
| Defect Tracking | 30/100 | ~28/100 | **28** | 78 unique raw defect strings across 16 inspection forms normalize to ~46 leaf types. Customer-siloed taxonomy. Metelix RW/BUFF prefix convention conflates defect with disposition. 5 confirmed absent defects for liquid paint (dry spray, colour mismatch, gloss failure, adhesion failure, solvent entrapment). |
| Inspection & Testing | 30/100 | ~32/100 | **30** | Count-based routing inspection (Good/Buff/Repaint/Scrap buckets), NOT measurement-based test results. No test method references. No Total Inspected denominator (PPM impossible). No supervisor sign-off on any inspection form. Gate alarm thresholds on 5 of 11 customer form families (paper annotation only). |
| Production Tracking | 25/100 | ~28/100 | **25** | Line 102 has carrier-level tracking (Carrier #, Starting Rack #, per-stage parameters). Lines 101/103 share a Daily Load Sheet with no rack/carrier ID. Daily Production Report template exists but has zero populated data. |
| Process Control | 35/100 | ~38/100 | **35** | 26+ process parameters captured across forms but only ONE has documented spec limits (colour delta-Ecmc < 2). No SPC, no trending, no spec limits on spray settings. CQI-12 Section 8 would flag as major nonconformance. Line 102 Operating Form (.xlsm) is the best single form in either plant audit. |
| Lab/Chemistry | 40/100 | ~38/100 | **38** | Paint batch traceability is discrete (mixed, consumed, replaced) vs Plant 1's continuous e-coat bath. New Paint Batch Verification has lab-grade colour verification (L*, a*, b*, delta-Ecmc at 3 angles). Paint Kitchen Inventory includes per-unit CAD costs. Solvent usage tracked (7 types). Pot life tracking entirely absent. |
| Traceability | 15/100 | ~18/100 | **15** | End-to-end score: 7/30 (23%). Chain breaks: (1) Shipping to Production — pack slips have no run ID/paint date; (2) Inspection to Production — no shared key (3 of 16 forms have rack/carrier #); (3) Post-paint rework — no source run, no defect reason, no outcome closure. Only Metelix Hummer Spoiler Application Tracker bridges process-to-quality gap. |
| Document Control | 15/100 | ~18/100 | **15** | 205 obsolete vs 84 current (2.4:1 churn ratio). 32 of 84 current forms stale (>2 years). Only 11/84 have revision evidence. 7 forms have Rev Log tabs (better than Plant 1). 58 known superseded clusters. 2 forms from December 2016 still in active folders (9+ years). |

---

## 3. Critical Findings (Both Auditors Agree)

1. **No NCR system exists.** Identical to Plant 1 — confirmed as a company-wide gap. Hold tags are physical labels, not data records. Paint Trial Information Sheet has a Trial # but no NCR linkage, no root cause, no corrective action.
2. **Traceability breaks at multiple points.** Three hard breaks: shipping-to-production, inspection-to-production, and post-paint-to-production. Pack slips carry part + quantity + date but no rack/carrier ID, no paint date/shift, no lot number.
3. **Post-paint rework is a data black hole (Plant 2-specific).** Sanding/buffing/deburring tally sheets capture time and counts only — no defect cause, no source run, no final disposition. "Rework without closure." This failure mode does not exist in Plant 1.
4. **78 defect strings normalize to ~46 types.** Customer-siloed taxonomy with inconsistent naming. Metelix has the richest vocabulary (20 defect categories on Hummer forms); without Metelix, taxonomy would be dangerously thin.
5. **84 current forms reduce to ~17 digital templates (45% reduction).** Pack slips: 7→1. Standard inspections: 4→1. Buff inspections: 3→1. Customer trackers: 3→1 (or dashboards). Effective UI screen count: 8 screens (74% reduction).
6. **Zero cost data.** No scrap cost, no rework cost, no waste disposal cost, no chargeback tracking. Paint Kitchen Inventory has per-unit CAD costs but not linked to consumption/waste.
7. **Inspection-to-NCR disconnect is the single most critical gap.** Zero of 16 inspection forms have an NCR reference field, escalation trigger, or quality alert linkage. The entire NCR lifecycle (25 API endpoints) is useless without an intake pathway from inspection.
8. **Line asymmetry is structural.** Line 102 has 9 dedicated forms with carrier tracking, robot programs, and TPM checklists. Lines 101/103 share 14 forms with no per-rack granularity. This represents fundamentally different operating philosophies within the same plant.
9. **No shipping-quality gate.** No quality hold/release field on any of 7 pack slip templates. Parts can move from inspection to shipping with no documented quality gate — only physical segregation prevents shipping rejected parts.
10. **GP-12 exists for Tesla only** and lacks every essential GP-12 element (no entry/exit criteria, no time-limited containment, no sample size, no customer notification). Rollstamp/BMW and Metelix/Hummer programs likely require GP-12 per OEM standards but have no forms.

---

## 4. ChatGPT-Unique Findings (12 items Claude identified separately or missed)

| # | Finding | Severity | Impact |
|---|---------|----------|--------|
| C1 | **"Rework without closure" named as distinct failure pattern** — post-paint rework loop is Plant 2's single biggest differentiating weakness vs Plant 1 | HIGH | New PostPaintReworkEvent entity required |
| C2 | **2.4:1 obsolete-to-current ratio quantified** — 205 obsolete vs 84 current with 32/84 stale and only 11/84 showing revision evidence | HIGH | Document control is structurally worse than Plant 1 |
| C3 | **Line 102 identified as the only "semi-serious system"** while Lines 101/103 are "more basic and stale" | MEDIUM | Line 102 Operating Form should be the template for digital platform |
| C4 | **Metelix Hummer Spoiler Application Tracker flagged as single most valuable form** — only true carrier-level combined parameter+defect record in organization | HIGH | Must productize this pattern as standard for high-value programs |
| C5 | **Inspection forms are defect-count routing data, not test-result style** — needs InspectionTestResult "count result" type + defect bucket | HIGH | InspectionDefectCount entity needed (distinct from InspectionTestResult) |
| C6 | **Gate alarm thresholds documented per customer** — embedded in inspection column headers as paper annotations | HIGH | CustomerInspectionProfile entity with GateAlarmThreshold field + computed GateAlarmTriggered |
| C7 | **Visual assessment override for colour verification** — operators can override instrumental delta-Ecmc measurements | MEDIUM | Must preserve override capability in digital system with audit trail |
| C8 | **Line speed verification gap** — existed as separate controlled log in obsolete forms but lost during form evolution | MEDIUM | Process parameter capture was regressed — digital system must restore |
| C9 | **58 known superseded clusters** in duplicate revision map — far worse document churn than Plant 1 | HIGH | DocumentRevision entity urgently needed |
| C10 | **ShipmentLine trace-token constraint proposed** — CHECK constraint enforcing at least one of ProductionRunId/LoadRecordId/LotNumber must be non-null | HIGH | Database-level enforcement of traceability on shipments |
| C11 | **Waste forms are labels, not tracking** — 5 waste forms contain headers only, zero data fields | MEDIUM | WasteDisposalEvent entity optional (decide scope) |
| C12 | **Full DDL proposed for 5 new entities** (PostPaintReworkEvent, Shipment, DowntimeEvent, ShiftStaffing, WasteDisposalEvent) with schemas, constraints, and RLS | INFO | Ready for engineering review |

---

## 5. Defect Taxonomy Reconciliation

**Dual-auditor reconciliation completed** — see [DEFECT_TAXONOMY_MASTER.csv](defect_taxonomy/DEFECT_TAXONOMY_MASTER.csv)

### Plant 2 Taxonomy Summary

| Source | L1 Categories | L2 Leaves | Schema |
|--------|--------------|-----------|--------|
| Claude Audit (Part A) | 6 | 10 | APP, HAND, ENV, COLOUR, MIX, EQUIP (operational/process-side defects) |
| Claude Audit (Part B) | 9 | 46 | APP, SUB, SAND, BUFF, MIX, EQUIP, HAND, COLOUR, ENV (full taxonomy) |
| ChatGPT Audit | 8 | 47 | ADH, BLS, APP, CON, COV, DAM, MAS, SPC, TEX (aligned to DB categories) |
| Live DB | 12 | 35 | ADH, TEX, CON, APP, COV, CUR, BLS, COR, DAM, MAS, SPC, DOC |

### Reconciliation Results

- **Maps to existing DB leaves:** ~30 defects (DIRT→CON-DST, ORANGE PEEL→TEX-ORP, RUNS/SAGS→TEX-SAG, FISHEYES→CON-FIS, THIN PAINT→COV-THN, SCRATCHES→DAM-SCR, etc.)
- **NEW leaf nodes required (not in Plant 1 or DB):**
  - **DAM-MLD** — Molding/Extrusion Surface Marks (Chatter Mark, Ext. Line, Flash, Gas Mark, Parting Line, Splay, Zipper Line) — 8 form strings → 1 new leaf
  - **DAM-DEF** — Substrate Deformation (Dents, Sink Marks, Thin Substrate) — 3 form strings → 1 new leaf
  - **TEX-SPT** — Spatter / Paint Spits — 1 new leaf (liquid-specific)
  - **APP-MOT** — Mottling / Uneven Metallic Appearance — 1 new leaf (liquid-specific)
  - **SPC-SWL** — Swirl Marks / Buff Lines (Haze, Sanding Marks) — 2 form strings → 1 new leaf
  - **COV-BAR** extended — Burn Through, E-Coat Showing, Missing Paint map here (3 additional form strings)
  - **BLS-SOL** extended — Outgassing, Outgassing Popping, Popping, Solvent Pop map here (4 additional form strings)
  - **CON-FOI** extended — Snowballs, Strings, Foam Marks map here (3 additional form strings)
- **Confirmed absent for liquid paint (need new leaves when evidence found):** Dry Spray, Colour Mismatch (visual), Gloss Failure, Adhesion Failure, Solvent Entrapment
- **Defect universality:** DIRT and SAG/RUN appear on all 11 customer form families. THIN PAINT: 9/11. THIN CLEAR: 8/11. ORANGE PEEL: 7/11. FIBER: 6/11. FLASH: 5/11.

### Answers to Plant 1 Open Questions

| Question | Answer from Plant 2 |
|----------|-------------------|
| Do water spots need a dedicated leaf? | No water spots found in Plant 2 liquid paint forms — likely e-coat/powder-specific |
| Does oil contamination need a dedicated leaf? | No oil contamination found in Plant 2 — may be Plant 1-specific (pretreat process) |
| What defect vocabulary do other plants use? | Plant 2 adds 5+ new leaf nodes (DAM-MLD, DAM-DEF, TEX-SPT, APP-MOT, SPC-SWL) all liquid-specific |
| What coating technologies? | Liquid spray paint (primer + base coat + clear coat multi-stage) — fundamentally different from Plant 1 powder/e-coat |

---

## 6. Entity Proposals — Plant 2 Specific

**Plant 2 audits propose 12 new entities** (some confirming Plant 1 proposals, some genuinely new).

### Confirms Plant 1 Proposals (with Extensions)
| Entity | Plant 1 Status | Plant 2 Extension Required |
|--------|---------------|---------------------------|
| ProductionRun | Approved | Add LineType=LIQUID, ColorProgram, Booth/Robot mode, multi-coat parameter groups |
| LoadRecord | Approved | Add CarrierNumber (or generic LoadIdentifier) + optional MoldingDate |
| ProcessParameterLog | Approved | Support multi-coat parameter groups (primer/base/clear) and cup test/viscosity |
| ProcessParameterReading | Approved | Add LIQUID parameter taxonomy (fluid/atom/fan, cup test, viscosity per coat stage) |
| LabAnalysis | Approved | Add analysis types: PaintMix, ColorVerification, SolventUsage, StorageTemp |
| LabAnalysisReading | Approved | Add structured colour fields (L*, a*, b*, delta-Ecmc at 25/45/75 degrees) |
| MaintenanceLog | Approved | Add checklist-style occurrences (frequency-based: daily/weekly/monthly) |
| CertificationRecord | Approved | Must link to Shipment/PackSlip + Inspection/Run; add ReleaseTagNumber |
| GP12InspectionRecord | Approved | Add customer-program scoping + stage fields |

### Genuinely New (Plant 2-Specific)
| Entity | Schema | Confidence | Purpose |
|--------|--------|------------|---------|
| **PostPaintReworkEvent** + **PostPaintReworkDefect** | postpaint | HIGH | Close the sanding/buffing/deburr black hole. Lifecycle: DRAFT→OPEN→COMPLETE→VERIFIED. Links to source ProductionRun, LoadRecord, InspectionRecord. Tracks QtyIn/QtyOut/QtyScrapped/LaborMinutes. |
| **InspectionRecord** + **InspectionDefectCount** | quality | HIGH (extends QFM) | Central inspection per customer×part×date×shift×type. Count-based defect routing (not measurement-based). Supports PAINT/BUFF/GP12/PRE_PAINT/APPLICATION types. 8-20 defect count rows per inspection. |
| **CustomerInspectionProfile** | quality | HIGH | Configuration entity driving dynamic form rendering. Maps customer×part→defect set with gate alarm thresholds. ~180 rows. |
| **Gp12ContainmentEvent** | quality | HIGH | GP-12 lifecycle: entry criteria, exit criteria, customer notification, inspection frequency, max duration. Tesla GP12 form has zero GP-12 metadata — entity is 90% net-new design. |
| **Shipment** + **ShipmentLine** (or PackSlip + PackSlipLineItem) | logistics | MEDIUM-HIGH | Replace 7 pack slip templates. QualityReleaseStatus gate (NOT_VERIFIED/RELEASED/HELD). CK_ShipmentLine_TraceToken: at least one of ProductionRunId/LoadRecordId/LotNumber must be non-null. |
| **ReceivingLogEntry** | logistics | MEDIUM | Structured reject with reason code + SCAR escalation link. Currently binary Accept/Reject with no defect classification. |
| **ReturnMaterialAuthorization** + **RmaLineItem** | logistics | MEDIUM | Based on Metelix RMA pattern. RMA→NCR linkage. Part states: SANDED_RAW/UNSANDED_RAW/PAINTED. |
| **DowntimeEvent** | production | HIGH | 15-category downtime taxonomy. Links to ProductionRun. Tracks minutes per category per line. |
| **ShiftStaffing** + **ShiftStaffingAssignment** | labor | MEDIUM-HIGH | Operator-to-run-to-defect linkage for competency/training correlation. Roles: PAINTER/BOOTH_OPERATOR/SANDING/BUFFING/DEBURRING/QC. |
| **PaintBatch** + **ColourVerification** | production | HIGH | Discrete batch tracking (fundamentally different from Plant 1 continuous bath). Lab-grade colour readings at 3 angles with delta-Ecmc pass/fail + visual override. |
| **PaintTrial** + **PaintTrialBooth** | production | MEDIUM | Trial lifecycle with per-booth parameters and change documentation. |
| **WasteDisposalEvent** | compliance | LOW-MEDIUM | Optional. 5 waste streams (BOOTH_SLUDGE/WASTE_PAINT/STILL_BOTTOMS/WASTE_ZINC/EMPTY_CONTAINERS). Evidence gap: forms are blank labels. |

### Combined Entity Count (Plant 1 + Plant 2)
- **Plant 1 approved:** 9 genuinely new + 6 QFM-superseded
- **Plant 2 additions:** ~12 new entities + 6 child entities across 5 schemas (quality, production, logistics, postpaint, labor, compliance)
- **Total estimated:** 27-35 migrations, 45-60 stored procedures, 55-65 new API endpoints

---

## 7. Gap Closure Status (21 Plant 1 Gaps + 7 New Plant 2 Gaps = 28 Total)

### Plant 1 Gaps Re-evaluated Against Plant 2

| Gap ID | Gap Name | Plant 2 Status |
|--------|----------|---------------|
| GAP-01 | No formal NCR | **YES** — Confirmed identical gap |
| GAP-02 | Traceability chain breaks | **YES** — Three hard breaks confirmed (worse pattern than Plant 1) |
| GAP-03 | Defect taxonomy fragmented | **YES** — 78 raw strings → ~46 types (different but equally fragmented) |
| GAP-04 | No PPM/yield calculation | **YES** — No Total Inspected denominator on any form |
| GAP-05 | Disposition not formally captured | **PARTIAL** — Routing buckets exist (Good/Buff/Repaint/Scrap) but not standardized; 4 of 11 codes used implicitly |
| GAP-06 | Stale forms | **YES** — 32/84 stale, 2 forms from 2016 (9+ years) |
| GAP-07 | Digital readiness poor | **YES** — Merged cells, no unique IDs, inconsistent headers, #REF! and #DIV/0! errors |
| GAP-08 | Zero cost data | **YES** — Only paint inventory has per-unit costs, not linked to quality events |
| GAP-09 | Operators by initials only | **PARTIAL** — Some full names exist (Daily Painter Schedule), Metelix has Inspector ID |
| GAP-10 | No calibration references | **YES** — Spectrophotometer implied but no instrument ID or calibration status |
| GAP-11 | No GP-12 exit gate | **PARTIAL** — Tesla GP-12 form exists but lacks all lifecycle elements |
| GAP-12 | No dedicated inspection entity | **YES** — Count-based routing forms need InspectionRecord + InspectionDefectCount |
| GAP-13 | Process params decoupled from quality | **PARTIAL** — Metelix Application Tracker ties some; all others decoupled |
| GAP-14 | No production run tracking | **YES** — Line 102 has partial carrier tracking; Lines 101/103 have none |
| GAP-15 | Lab chemistry not digitized | **YES** — Paint mix, colour verification, solvent usage all on paper |
| GAP-16 | GP-12 siloed per customer | **PARTIAL** — Only Tesla has GP-12 (1 form vs Plant 1's 14) |
| GAP-17 | Cavity/location codes | **NO** — Not observed in Plant 2 |
| GAP-18 | Extreme merged cells | **YES** — Present but not as extreme as Plant 1's BASF PB Ratio file |
| GAP-19 | No document revision control | **YES** — Only 2 of 31 Part B forms have revision tracking (both Tesla) |
| GAP-20 | No packaging hold / shipment release | **YES** — Approved Tag Tracking abandoned since Nov 2018 |
| GAP-21 | OOS → NCR auto-trigger | **YES** — Visual override on colour verification, no auto-trigger |

### New Plant 2 Gaps (GAP-22 through GAP-28)

| Gap ID | Gap Name | Severity | Evidence | Engineering Action |
|--------|----------|----------|----------|-------------------|
| GAP-22 | **Post-paint rework black hole** | CRITICAL | Sanding/buffing/deburring tally sheets capture time + qty only. No defect cause, no source run, no outcome closure. 5+ tally forms, 272 days of buffing data without quality linkage. | PostPaintReworkEvent entity with lifecycle tracking |
| GAP-23 | **Inspection-to-NCR disconnect** | CRITICAL | Zero of 16 inspection forms reference NCR. Gate alarms are paper-only. No escalation mechanism exists. | POST /v1/inspection/{id}/escalate endpoint; InspectionNcrLink |
| GAP-24 | **Shipping-quality gate absent** | CRITICAL | No quality hold/release field on any pack slip. Physical segregation is the only quality control. Approved Tag Tracking abandoned 2018. | PackSlip.QualityReleaseStatus field; quality release workflow |
| GAP-25 | **Line asymmetry (102 vs 101/103)** | HIGH | Line 102 has 9 dedicated forms with carrier tracking; Lines 101/103 share 14 forms with no per-rack granularity. | Platform must enforce uniform data capture across all lines |
| GAP-26 | **No spec limits on process parameters** | HIGH | Only colour delta-Ecmc has documented limits. All spray, viscosity, temperature parameters captured without targets. CQI-12 Section 8 nonconformance. | ProcessParameterReading needs SpecMin/SpecMax/TargetValue columns |
| GAP-27 | **Customer requirements not referenced** | HIGH | No customer appearance standards, boundary samples, dimensional checks, or test method references on any inspection form. Y2XX references external grid (not included). | CustomerInspectionProfile needs CustomerSpecReference field |
| GAP-28 | **BRP/Spyder hidden customer** | MEDIUM | Full inspection program for 14+ BRP Spyder parts hidden in Laval Tool Buff Inspection KANBAN sheet tab. No dedicated inspection form, pack slip, or tracker. | Must be reclassified under separate BRP/Spyder customer; needs dedicated forms |

---

## 8. Platform Impact Summary

### sf-quality-db
- **Existing coverage:** NCR entity (35+ fields), 11 DispositionCodes, 12/35 DefectType taxonomy, CalibrationRecord, Document (no revision). **Entity coverage against Plant 2 forms: ~7-8%** — the DB was built for quality event management; operational production domain is almost entirely absent.
- **Plant 2 confirms:** All 9 Plant 1 entity proposals remain valid with liquid-paint extensions
- **Plant 2 adds:** ~12 new entities across 5 schemas (postpaint, logistics, production, labor, compliance)
- **New DB leaves needed:** DAM-MLD, DAM-DEF, TEX-SPT, APP-MOT, SPC-SWL (5 new leaves + extensions to COV-BAR, BLS-SOL, CON-FOI)
- **Reference data needed:** 8 customers (with addresses), ~45 part numbers, 2 suppliers, 15 downtime reason codes, 65+ rack names
- **Action:** Extend Phases 35-42 with Plant 2 entity requirements; add Phases 43-47 for logistics, postpaint, labor schemas

### sf-quality-api
- **Existing coverage:** 19 NCR endpoints fully implemented
- **Plant 2 confirms:** Need for Inspection/ProductionRun/Lab/ProcessParameter/GP-12/Certification endpoint groups
- **Plant 2 adds:** ~27 new endpoints: 10 inspection, 8 shipping/receiving, 4 GP-12, 5 reporting
- **Critical new endpoint:** POST /v1/inspection/{id}/escalate (bridges inspection to NCR — without this, the NCR system has no intake)
- **Action:** 55-65 total new endpoints after all DB entities land

### sf-quality-app
- **Existing coverage:** 0% — not started
- **Plant 2 confirms:** Tablet-first design, shift selector as global context
- **Plant 2 adds:** 8 proposed screens replacing 31 paper forms (Inspection Entry, Inspection Queue, GP-12 Dashboard, Pack Slip Creator, Receiving Log, RMA Tracker, Delivery Performance Dashboard, Inspection Analytics)
- **Key design pattern:** CustomerInspectionProfile-driven dynamic form rendering — single inspection screen adapts defect columns per customer/part
- **Key finding:** Metelix Hummer Spoiler Application Tracker pattern (process+quality on same screen per carrier) should be productized as standard for high-value programs
- **Action:** App screen inventory now includes both Plant 1 and Plant 2 form replacements

---

## 9. Action Items for Plant 2 Completion

| # | Action | Owner | Priority | Blocked By | Status |
|---|--------|-------|----------|------------|--------|
| 1 | Add 5 new DefectType leaves (DAM-MLD, DAM-DEF, TEX-SPT, APP-MOT, SPC-SWL) to taxonomy seed | DB | P1 | Nothing | READY TO START |
| 2 | Extend ProductionRun entity for LIQUID line type (multi-coat, robot program, carrier) | DB | P1 | Phase 35 | BLOCKED |
| 3 | Create `postpaint` schema + PostPaintReworkEvent + PostPaintReworkDefect | DB | P1 | Phase 35 | BLOCKED |
| 4 | Create `logistics` schema + Shipment/PackSlip + ShipmentLine + ReceivingLogEntry + RMA | DB | P2 | Phase 35 | BLOCKED |
| 5 | Create InspectionRecord + InspectionDefectCount (count-based, extends QFM) | DB | P1 | QFM adjudication | BLOCKED |
| 6 | Create CustomerInspectionProfile (dynamic form config with gate alarms) | DB | P1 | Action 5 | BLOCKED |
| 7 | Create Gp12ContainmentEvent with full lifecycle | DB | P2 | QFM inspection entities | BLOCKED |
| 8 | Create PaintBatch + ColourVerification entities | DB | P1 | Phase 35 | BLOCKED |
| 9 | Create DowntimeEvent with 15-category taxonomy | DB | P2 | Phase 35 | BLOCKED |
| 10 | Create ShiftStaffing + ShiftStaffingAssignment entities | DB | P3 | Phase 35 | BLOCKED |
| 11 | Create PaintTrial + PaintTrialBooth entities | DB | P3 | Nothing | READY TO START |
| 12 | Add SpecMin/SpecMax/TargetValue to ProcessParameterReading | DB | P1 | Phase 37 | BLOCKED |
| 13 | Seed 8 Plant 2 customers + ~45 parts + 2 suppliers as reference data | DB | P1 | Nothing | READY TO START |
| 14 | Reclassify BRP/Spyder as separate customer (currently hidden in Laval buff form) | Human | P2 | Nothing | RECOMMENDED |
| 15 | Run codebase assessment against Plant 2 findings (validate entity coverage %) | DB | P1 | Nothing | READY TO START |
| 16 | Design carrier-level application tracking UX (productize Metelix Hummer pattern) | App | P2 | DB Actions 2, 5 | BLOCKED |
| 17 | Design inspection-to-NCR escalation workflow UX | App | P1 | DB Action 5 | BLOCKED |
| 18 | Design quality release gate on pack slip creation screen | App | P2 | DB Action 4 | BLOCKED |

---

## 10. Cross-Plant Patterns Confirmed (Plant 1 + Plant 2)

### Universal Patterns (2/2 plants — strong candidates for Phase 1 platform requirements)

1. **No formal NCR system** at either plant — company-wide gap requiring cultural change + platform enforcement
2. **Broken traceability chain** — identical pattern of disconnected load/production/inspection/shipping records
3. **No shipping-quality gate** — no quality release field on any pack slip at either plant
4. **Customer forms are relabeled copies** — copy-paste form creation is standard practice (KB tabs still named "Laval Tool")
5. **GP-12 is form-only, not process** — no lifecycle elements at either plant
6. **No supervisor sign-off** on any inspection form at either plant
7. **No test method references** on any customer inspection form
8. **Defect taxonomy is customer-siloed** — each form built independently with different vocabulary
9. **Post-paint rework cycles uncounted** — no linkage between paint and buff inspection
10. **Cost visibility is near-zero** — no cost-of-poor-quality tracking
11. **Document control immaturity** — both plants have severely stale forms with minimal revision tracking
12. **Operators identified by initials** — no structured employee linkage
13. **Zero calibration references** — instruments implied but not tracked

### Plant-Specific Patterns (configurable features, not universal requirements)

| Pattern | Plant 1 | Plant 2 |
|---------|---------|---------|
| Chemistry model | Continuous bath sampling (e-coat) | Discrete paint batch (mix→consume→replace) |
| Colour verification | Not found in powder/e-coat audit | Lab-grade delta-Ecmc at 3 angles with visual override |
| Spray parameters | Single-stage application (powder/e-coat) | Multi-coat (primer→base→clear) with per-stage fluid/atom/fan |
| Robotic documentation | None | Line 102 robot programs, job numbers, presets |
| Post-paint rework | Minimal (strip/recoat) | Major (buff/sand/deburr at scale — 272 days of daily data) |
| Waste complexity | Minimal | 7 solvent types, 5 waste streams (RCRA-level) |
| Customer complexity | 18 customers, GP-12 for 8 | 8 customers, GP-12 for 1 (Tesla only) |
| Gate alarm thresholds | Not found | 5 of 11 customer form families have per-defect thresholds |

### Open Questions for Plants 3-7

1. **Do any plants have a formal NCR form?** Still not found at Plant 1 or Plant 2.
2. **Do any plants track pot life / mix-to-use time limits?** Absent at Plant 2 (critical for catalyzed paint).
3. **Do any plants have structured returns/RMA tracking?** Only Metelix at Plant 2.
4. **Do other plants use carrier-level process+quality tracking?** Only Metelix Hummer at Plant 2.
5. **What coating technologies at Plants 3-7?** Powder coat, e-coat, anodize, mechanical finishing expected — defect taxonomies will diverge significantly.
6. **Do any plants have supervisor sign-off on inspection?** Zero evidence across 2 plants.
7. **Is the 15-category downtime taxonomy universal?** Plant 2 has it; Plant 1 does not — adopt as cross-plant standard?

---

*Plant 2 synthesis complete. 84 forms examined by 2 AI auditors (14 report batches total). 28 total gaps (21 from Plant 1 + 7 new). ~12 new entities proposed (confirms 9 from Plant 1 with extensions). 78 defect strings reconciled to ~46 types with 5 new DB leaves needed. Ready for codebase assessment and Plants 3-7.*
