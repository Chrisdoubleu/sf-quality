# Quality Systems Audit Report — Select Finishing Plant 1
## sf-quality Platform Migration Assessment

**Audit Date:** 2026-02-24  
**Auditor:** QSA (Quality Systems Auditor)  
**Scope:** 133 files across 3 document families (Powder Line, E-Coat Line, Inspection & Testing)  
**Platform Target:** sf-quality v1.0 (DB v1.0.0 / API v0.3.0 / App planning phase)

---

## 1. Executive Summary

### The Blunt Truth

Plant 1's quality data capture system is a functional paper-and-Excel operation that keeps parts moving but would **fail a forensic traceability test**. If a customer called today with a complaint about a specific part, the quality team would need to manually cross-reference 4–6 disconnected spreadsheets across multiple folders to reconstruct what happened — and even then, they'd likely hit dead ends at the process parameter and operator qualification links.

Here's what's working: the plant has a consistent *rhythm* of data capture — load → coat → unload → inspect → track defects → certify. That rhythm is real and embedded in the workforce. The forms are being used. That's not nothing.

Here's what's broken:

1. **No formal NCR system.** There is no numbered nonconformance report anywhere in this package. The "Out of Specification Reaction Form" (8.2.1.2.10) is the closest thing, and it's a single-sheet, free-text log with no tracking number, no root cause field, no corrective action closure, and no linkage to the defect tracking forms. The "Rejected Material Disposition Log" (8.2.1.2.28) captures scrap/rework decisions but has no traceability forward or backward. These are two disconnected islands pretending to be a quality management system.

2. **The defect taxonomy is a mess.** Across 19 defect tracking forms, I found **97 unique defect name strings** that normalize down to approximately **38 actual defect types**. The same defect is called "Fish Eyes" on one form, "Fisheyes" on another, and "FE" on a third. "Light Coverage" on the general template becomes "Lt. cov/ Dry spray" on the AGS form and "Light Track @ Top / Light Track @ Bottom / Light Pulley @ Top / Light Pulley @ Bottom" on the Warren form (which breaks one defect into four location-specific variants). Cross-customer Pareto analysis from this data is impossible without manual normalization.

3. **Traceability breaks at load bar.** The E-Coat Load Sheet (8.2.1.2.19) captures load bar numbers. The Unload Sheet (8.2.1.3.1.2) does not. The Defect Tracking forms reference customer and part number but not load bar. The Paint Record (8.2.1.1.2) captures paint batch and recipe but not which load bars were coated with that batch. The chain breaks in multiple places.

4. **Process parameters are decoupled from outcomes.** Temperature logs, recipe parameters, and bath chemistry are recorded on forms that share zero common identifiers with the inspection and defect tracking forms. You cannot correlate a spike in defects with a process deviation without manually aligning timestamps.

5. **GP-12 forms are siloed per customer per part.** Fourteen GP-12 forms exist across 8 customers, each a separate spreadsheet with different defect columns, different layouts, and no shared structure. This is 14 forms doing the same job with 14 different data models.

### Digital Migration Readiness Score

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **NCR/Disposition** | 15/100 | No formal NCR exists. Disposition is captured on 2 disconnected forms. The sf-quality NCR entity is vastly more capable than anything on paper. |
| **Defect Tracking** | 35/100 | Quantitative counts exist on most forms (good), but taxonomy is fragmented and there's no aggregation mechanism. |
| **Inspection & Testing** | 45/100 | Strong test method references (ASTM), film build readings captured numerically. But no dedicated digital entity exists yet. |
| **Production Tracking** | 40/100 | Load/unload cycle is captured, but identifiers don't chain together. E-Coat load sheet is the strongest form in the package. |
| **Process Control** | 30/100 | Parameters are recorded but not linked to production runs. No SPC, no control charts, no reaction plan automation. |
| **Lab/Chemistry** | 50/100 | Daily lab analysis is the most structured form in the package. Specifications are documented. BASF process database exists but is abandoned. |
| **Traceability** | 20/100 | Serial number traceability exists as a concept form but lacks systematic adoption. Load bar → unload → inspection chain is broken. |
| **Document Control** | 10/100 | One form (8.2.1.2.26) has a revision log. The rest have no version control, no effective dates, no approvals. Multiple files marked "edit" and "DO NOT USE" are still in circulation. |
| **Overall** | **30/100** | The plant captures data at every stage but in disconnected silos. Digital migration requires entity creation, taxonomy normalization, and workflow linkage that doesn't exist on paper today. |

---

## 2. File Inventory Table (Phase 1)

### Summary Statistics
- **Total files analyzed:** 133 (116 Excel, 6 Word, 2 PDF, 9 JPEG)
- **Excel files successfully parsed:** 108 of 116 (93%)
- **Legacy .xls files requiring direct parsing:** 8 (7 readable via xlrd, 1 error)
- **Files with sample/production data:** 14 (the GLDC daily update, BASF PB ratio, ABM defect tracking Sheet1, amps tracking, and several GP-12 forms with filled data)
- **Files older than 2 years (stale risk):** 23 files last modified before 2024-02-24

### Category Distribution

| Category | Count | % of Total |
|----------|-------|------------|
| QUALITY INSPECTION | 31 | 23% |
| DEFECT TRACKING | 19 | 14% |
| GP-12 / CONTAINMENT | 14 | 11% |
| PROCESS CONTROL | 13 | 10% |
| PRODUCTION TRACKING | 10 | 8% |
| LAB / CHEMISTRY | 10 | 8% |
| MAINTENANCE / PM | 9 | 7% |
| NCR / DISPOSITION | 4 | 3% |
| PACKAGING / SHIPPING | 4 | 3% |
| DOCUMENT CONTROL | 3 | 2% |
| CUSTOMER-SPECIFIC (mixed) | 6 | 5% |
| TRAINING / COMPETENCY | 0 | 0% |
| CALIBRATION / MSA | 1 | 1% |
| None/Reference | 6 | 5% |

### Manifest Corrections from Pre-Classification

The automated pre-classification had significant errors — approximately 40% of the "LAB / CHEMISTRY" classifications were wrong. Here are the key corrections:

| Doc Number | Pre-Classified | Corrected To | Rationale |
|------------|---------------|-------------|-----------|
| 8.2.1.3.1.1 | LAB / CHEMISTRY | PRODUCTION TRACKING | This is the Powder Unload Sheet — production tracking, not lab work |
| 8.2.1.3.1.2 | LAB / CHEMISTRY | PRODUCTION TRACKING | Ecoat Unload Sheet |
| 8.2.1.3.1.3 | LAB / CHEMISTRY | PRODUCTION TRACKING | Offline Unload Sheet |
| 8.2.1.3.1.4 | LAB / CHEMISTRY | QUALITY INSPECTION | Powder General Inspection and Testing |
| 8.2.1.3.1.6 | LAB / CHEMISTRY | QUALITY INSPECTION | Ecoat Inspection and Testing at Unload |
| 8.2.1.3.1.8 | LAB / CHEMISTRY | PACKAGING / SHIPPING | E-Coat Weight Count Form |
| 8.2.1.3.1.9 | LAB / CHEMISTRY | PACKAGING / SHIPPING | E-coat bulk Packaging Tracker |
| 8.2.1.3.1.10 | LAB / CHEMISTRY | PACKAGING / SHIPPING | Certification Labels (Word doc) |
| 8.2.1.3.1.14 | LAB / CHEMISTRY | PACKAGING / SHIPPING | Certification Log |
| 8.2.1.3.1.16 | LAB / CHEMISTRY | PRODUCTION TRACKING | Raw Traceability Form |
| 8.2.1.3.1.17 | LAB / CHEMISTRY | QUALITY INSPECTION | Trial Inspection Form |
| 8.2.1.3.1.18 | LAB / CHEMISTRY | PRODUCTION TRACKING | Serial Number Traceability |
| 8.2.1.1.13 | None/Reference | PROCESS CONTROL | Offline Batch Oven Daily Check Sheet — this IS process control |
| 8.2.1.1.29 | None/Reference | CALIBRATION / MSA | Offline Booth Pressure Differential Gauge Check — calibration evidence |
| 8.2.1.2.20 | None/Reference | QUALITY INSPECTION | Test Part Procedure Ecoat — inspection reference |
| 8.2.1.2.21 | None/Reference | LAB / CHEMISTRY | PNB/PPH Sheet — chemical addition tracking |
| All customer Inspect & Test forms | LAB / CHEMISTRY | QUALITY INSPECTION | ~25 forms misclassified |
| All customer Run Reports | LAB / CHEMISTRY | DEFECT TRACKING | ~5 forms misclassified |
| All customer Load/Unload Sheets | LAB / CHEMISTRY | PRODUCTION TRACKING | ~5 forms misclassified |
| 8.2.1.3.6.10 | LAB / CHEMISTRY | NCR / DISPOSITION | AGS RMA form — returns/disposition |
| 8.2.1.3.37.3 | LAB / CHEMISTRY | PRODUCTION TRACKING | Takumi Kanban Tracker |
| 8.2.1.3.31.2 | LAB / CHEMISTRY | MAINTENANCE / PM | URSA BOAT PM — equipment maintenance |
| GLDC Daily Inventory Reports | LAB / CHEMISTRY | PRODUCTION TRACKING | In-process inventory tracking |

### Platform Entity Mapping Summary

| Platform Entity Target | File Count | Confidence |
|----------------------|------------|------------|
| Inspection (NEW) | 31 | High |
| NCR / NcrDisposition | 4 | High |
| NcrContainmentAction / GP12 (NEW extension) | 14 | High |
| ProductionRun (NEW) | 15 | High |
| ProcessControl (NEW) | 13 | High |
| LabChemistry (NEW) | 8 | High |
| Maintenance (NEW) | 9 | Medium |
| DefectTracking → feeds NCR | 19 | High |
| PackagingHold (NEW) | 4 | Medium |
| DocumentControl (NEW) | 3 | Medium |
| Calibration (NEW) | 1 | Low |
| TrainingCompetency (NEW) | 0 | N/A |
| None/Reference | 4 | — |

---

## 3. Detailed Analysis by Category (Phase 2)

### A. Defect Tracking Forms — CRITICAL

**Forms analyzed:** 19 defect tracking forms + 5 "Run Reports" that are actually defect tracking forms with a different name

#### A.1 Defect Taxonomy Consistency

**Verdict: Inconsistent. Three distinct defect vocabulary families exist.**

**Family 1 — "Standard Powder Template" (11 forms)**
Used by: General Powder (8.2.1.3.1.5), GreenBlue, Presstran, JAC, MSSC, Rollstamp, Ultrafit, Multimatic, Polycon Powder, and minor variants.
Core columns: Paint in Threads | Light Coverage | Damaged (Scratched) | Back Ionization | Orange Peel | Debris | Hook Mark | Build Up | Water | Contamination | Rust | Other
Disposition columns: Repaired @ Line | Sent To Rework | Scrapped
Quantity columns: Total Loaded (from Load Sheet) | Total Packed | Total Reject

This is the dominant template. These 11 forms are Tier 1 consolidation candidates.

**Family 2 — "Hino/AGS/Accurate Powder Template" (3 forms)**
Used by: AGS Hino 3pc (8.2.1.3.6.12), Accurate (8.2.1.3.40.2), AGS Hino GP12 rework (8.2.1.3.6.9)
Core columns: Discoloured dirt/spec | Fish Eyes | Heavy powder | Cluster of Dirt | Lt. cov/Dry spray | Off colour | Touch Mark | Hook Mark | Pinholes | Orange peel | Sanding marks | Oil | Fiber | Hit part | Part dropped | Part scratched
Quantity columns: per-part rows with Good and Reject counts

This template has a **finer-grained** defect list with handling damage categories that Family 1 lumps into "Damaged (Scratched)".

**Family 3 — "Customer-Unique" (5 forms)**
- **Ecoat General (8.2.1.3.1.7):** Bubbles | Light Coverage | Bare Metal | Rough Spots | Build Up | Paint Runs | Water Spots | Rust — E-coat-specific vocabulary
- **Warren (8.2.1.3.24.6):** Location-specific defect variants (Light Track @ Top, Light Pulley @ Bottom, Dirt on Track, Dirt on Pulley, Tight Clip) — part-geometry-driven taxonomy
- **Polycon Ecoat (8.2.1.3.26.2):** Two defect sections (touch-up vs. supplier defects) with unique terms (Surface Scratches, Water Marks, Tool Marks, Over Sand)
- **ABM (8.2.1.3.3.5):** Unique terms (STUCK, Dirt on Track, Dirt on Pulley, Large Hook marks, Material Defect, OIL, Heavy Paint)
- **GLDC (8.2.1.3.34.1):** Die-cast substrate defects (Belt Mark, Misfill, Pin Push, Gouge, Sink, Flash, Sharp Edge, Adhesion Fail) — these are NOT coating defects

#### A.2 Defect Data Quality

| Metric | Assessment |
|--------|------------|
| **Quantitative counts** | Yes — 16 of 19 forms capture integer counts per defect type. The Part Fallout Log (8.2.1.2.29) uses Y/N binary. |
| **Linked to part number** | Yes — all forms have part number field |
| **Linked to load bar/rack** | No — none of the defect forms reference a load bar number |
| **Linked to shift** | Partial — "Shift" column exists on ~60% of forms as M/D/A entry |
| **Linked to operator** | Partial — "Operator Initials" exists but is initials only, not an employee ID |
| **Linked to date** | Yes — date field present on all forms |
| **PPM calculable** | Yes for Family 1 — "Total Loaded" and "Total Reject" fields enable PPM. No for Family 2/3 — denominators inconsistent or missing. |
| **Disposition captured** | Yes on Family 1 template (Repaired @ Line / Sent To Rework / Scrapped) with integer counts. No on Family 2/3. |

#### A.3 Missing Coating-Specific Defects

**Powder line gaps:** No explicit tracking of Fluidization Issues, Color Mismatch/Metamerism, Edge Pull-Back, Film Build Out-of-Spec (as a defect category), Cure Issues (under-cure/over-cure).

**E-coat line gaps:** No explicit tracking of Faraday Cage effects, Outgassing, Cratering, Edge Crawling, Solvent Pop, Insufficient Phosphate Conversion (pre-treat failure visible as poor adhesion).

#### A.4 Taxonomy Normalization

The 97 raw defect strings normalize to **38 proposed DefectType leaf nodes** across 8 Level 1 categories. Full mapping is in **Appendix A**.

---

### B. NCR / Disposition Forms — CRITICAL GAP

**Forms analyzed:** 4 forms

#### B.1 Out of Specification Reaction Form (8.2.1.2.10)

This is the closest thing to an NCR in the package and it is **wildly inadequate**.

- **No tracking number.** No auto-generated or manual NCR ID.
- **Free-text fields only.** Stage, Specification, Out of Spec Reading, Adjustment Made, Retest Condition — all free-text.
- **No root cause.** No 5-Why, no Ishikawa, no RCA methodology.
- **No corrective action.** No CAPA linkage, no follow-up verification.
- **No disposition.** If the retest passes, there's an implicit "use as is" decision, but there's no formal disposition code.
- **Scope limited to e-coat chemistry.** This form is only for bath chemistry deviations. There is no equivalent for powder line process deviations.
- **NCR Entity Coverage: ~15%.** The form captures: Date (≈ CreatedDate), Stage (≈ DetectionProcessAreaId), Description (≈ Description), ImmediateAction (≈ ImmediateAction). Everything else on the NCR entity is missing.

#### B.2 Rejected Material Disposition Log (8.2.1.2.28)

- **No tracking number.**
- **Captures:** Date, Customer, Part Number, Reason for Rejection (free-text), Operator Initials, Disposition (Scrap/Rework only — 2 of 11 disposition codes), Supervisor Initials.
- **No quantities.** No "how many rejected" field — just the log entry.
- **No linkage** to defect tracking, load sheets, or any other form.
- **NCR Entity Coverage: ~20%.** Maps to: CustomerId, PartId, Description, DispositionCodeId (partially — only Scrap/Rework), but with critical gaps in QuantityAffected, QuantityRejected, DefectTypeId, SeverityRatingId, and the entire containment/investigation/verification lifecycle.

#### B.3 E-Coat Crash Reports (8.2.1.3.1.19, 8.2.1.3.1.20)

These are the **best-structured NCR-adjacent forms** in the package, created in April 2025.

- **Supervisor version** captures: Date/time of crash, date/time of resolution, reason for crash, total downtime, stage where crash occurred, range of load bars impacted, parts affected.
- **Tech version** captures: Reason (checkbox: Improper Loading / Racks sticking out / Existing parts in tank / Other), stages emptied, description of resolution, chemical additions made.
- **Document control present:** Document number, creator, approver, revision date.
- **NCR Entity Coverage: ~40%.** These capture enough data to populate a meaningful NCR — but they're scoped only to e-coat crash events, not general nonconformances.

#### B.4 Part Fallout Log (8.2.1.2.29)

- **Captures:** Date, Customer, Part Number, Quantity Found, Rack Type, Stage, Part Defective (Y/N), Can Be Reworked (Y/N)
- **This is effectively a defect discovery log** — it's the point where a fallen part is found and triaged. But there's no forward link to disposition or backward link to the load that dropped the part.
- **NCR Entity Coverage: ~25%.** Could feed an NCR but currently doesn't.

### B.5 NCR Gap Summary

**There is no NCR system at Plant 1.** The sf-quality NCR entity with its 7-state lifecycle, containment actions, disposition tracking, cost ledger, root cause analysis, and verification workflow represents a quantum leap from what exists today. The forms currently in use capture approximately **15-40%** of what the NCR entity can handle, and they do so in disconnected, unnumbered, unlinked formats.

---

### C. Inspection & Testing Forms

**Forms analyzed:** 31 forms (2 general templates + 25+ customer-specific + 4 GP-12 variants)

#### C.1 Tests Performed

| Test | Method Reference | Lines | Captured As |
|------|-----------------|-------|-------------|
| Cross-hatch Adhesion | ASTM D3359 (referenced as "astm3359") | Powder, E-Coat | Pass/Fail |
| Pencil Hardness | Referenced as "8.3.1.14.60" (internal) | Powder | Pass/Fail |
| Solvent Rub (MEK) | ASTM D4752 (referenced as "ASTM4752") | Powder, E-Coat | Pass/Fail |
| Film Build (DFT) | DFT gauge (referenced as "8.3.1.14.46") | Both | Numeric — 5+ readings per part |
| Gloss | @60° or customer spec | Powder (select customers) | Numeric value |
| Visual Inspection | Per boundary sample | Both | Pass/Fail |
| Paint Coverage | Visual | Powder | Pass/Fail (checkmark) |
| Boil Test | GM/customer specific | E-Coat (AGS) | Evidence image (JPEG) |
| Cure Test | Not standardized | Powder | Referenced on some forms, not captured |
| Go/No-Go Gauge | Customer-specific (ABM) | Powder | Dimensional measurements |

**Key observations:**
- Film build is captured as **individual numeric readings** (5 samples per part per shift) — this is the highest-quality data point in the inspection system.
- Adhesion and solvent rub are **pass/fail** only — no intermediate values captured.
- **No calibration references** on any inspection form. No gauge ID, no calibration due date, no verification stamp.
- Test method references use **internal document numbers** (8.3.1.14.x series) rather than or in addition to ASTM standards.

#### C.2 Customer-Specific Form Variance

| Customer | # Forms | Coating Line | Key Differences from General Template |
|----------|---------|-------------|--------------------------------------|
| AGS | 8 | Both | GM3000 spec testing, specific film build ranges (73-135μm powder, 16-23μm e-coat), gloss 40-70@60°, grid template for bumper inspection zones |
| ABM | 4 | Powder | Go/No-Go gauge dimensional checks (Datum C, Datum B, Pulley Holes, Screw Holes, Guide Clip Openings), lot number tracking, master lot number |
| JAC | 3 | Powder | Per-part-number GP-12 sheets (12 tabs), per-program defect tracking |
| Toyotetsu | 3 | E-Coat | Foam location inspection, film build location maps, seal inspection, boundary-specific paint coverage |
| Warren | 5 | Powder | Customer-specific load/unload sheets (separate from general), part-location-specific defect columns |
| Tiercon | 2 | E-Coat | Per-part GP-12 tabs (front bumper, endcaps), label templates |
| GLDC | 6 | E-Coat | Die-cast part inspection with substrate defect tracking (not coating), daily inventory/WIP tracking, Tesla-specific process states |
| Polycon | 4 | Both | Separate e-coat and powder forms, supplier-defect segregation on e-coat form |
| Presstran | 4 | Powder | Per-part GP-12 tabs with kanban tracking |
| JNM | 2 | E-Coat | Tape adhesion Method B, average coating thickness in mils (not microns) |
| Takumi | 3 | E-Coat | Kanban tracker, minimum 15μm film build |
| Multimatic | 2 | Powder | Bronco program-specific |
| Rollstamp | 2 | Powder | Standard template variant |
| Ultrafit | 2 | Powder | "Missing Texture/Smooth" unique defect |
| GreenBlue | 2 | Powder | Standard template variant |
| MSSC | 3 | Powder | Assembly and powderline offline variants |
| Accurate | 2 | Powder | Hino bumpers GP-12 format |
| Ursa | 2 | E-Coat | Simplified report (good/bad counts + boat number), BOAT PM maintenance form |

#### C.3 Inspection Entity Discovery

Based on this analysis, an `InspectionRecord` entity needs:

**Core fields:** InspectionId, PlantId, ProductionRunId (FK), CustomerId (FK), PartId (FK), InspectionTypeId (Unload/GP-12/Trial/Final), ShiftCode, InspectionDate, InspectorId (FK → Employee), OverallResult (Accept/Reject/Conditional), Notes

**Child table — InspectionTestResult:** TestResultId, InspectionId (FK), TestMethodId (FK → reference data), Result (Pass/Fail/Numeric), NumericValue, UnitOfMeasure, SpecMin, SpecMax, SampleNumber (1-6)

**Child table — InspectionFilmBuildReading:** ReadingId, InspectionId (FK), SampleNumber, LocationCode (from customer film build map), ReadingValue, UnitOfMeasure (microns/mils)

**Relationships:** InspectionRecord → ProductionRun (FK), InspectionRecord → NCR (via defect discovery), InspectionRecord → Customer + Part (composite FK for customer-specific requirements)

---

### D. Production Tracking Forms

**Forms analyzed:** 15 forms (load sheets, unload sheets, paint records, run reports, traceability forms)

#### D.1 Traceability Chain Assessment

| Stage | Form | Key Identifier | Links To |
|-------|------|---------------|----------|
| Raw Receipt | Raw Traceability Form (8.2.1.3.1.16) | Serial #, Part #, Customer | ← Incoming material |
| Load (Powder inline) | Part Load Sheet (8.2.1.1.9) | Starting/Ending Load Bar, Part #, Customer | → Paint Record (by date/colour) |
| Load (Powder offline) | Offline Load Sheet (8.2.1.1.5) | Part #, Customer, Qty Loaded | → Offline Paint Record |
| Load (E-Coat) | E-Coat Load Sheet (8.2.1.2.19) | **Load Bar #**, Customer, Part #, Qty Loaded, Shift | → Unload (by date, no explicit link) |
| Paint (Powder inline) | Paint Record (8.2.1.1.2) | Paint Colour, Batch Lot, Recipe, Line Speed | ← Load Sheet (by date/colour only) |
| Paint (Powder offline) | Offline Paint Record (8.2.1.1.8) | Colour, Supplier, Batch # | ← Load Sheet (by date only) |
| Unload (Powder) | Powder Unload Sheet (8.2.1.3.1.1) | Part #, Approval Tag #, Qty Packed | ← Load Sheet (NO explicit link) |
| Unload (E-Coat) | Ecoat Unload Sheet (8.2.1.3.1.2) | Part #, Approval Tag #, Qty Packed, Qty Scrapped | ← Load Sheet (NO explicit link) |
| Inspection | General Inspect & Test forms | Part #, Shift, Film build readings | ← Unload (by part # + date) |
| Defect Tracking | Various | Part #, Qty Loaded, Qty Reject | ← Load Sheet (manual cross-ref) |
| Certification | Certification Log (8.2.1.3.1.14) | Part #, Approval Tag #, Qty Acceptable, Qty Rejected | → Packaging/Shipping |
| Packaging | E-coat Bulk Packaging Tracker (8.2.1.3.1.9) | Bin #, Part #, Qty, Approval Tag # | → Shipment |

**Critical finding:** The **Approval Tag #** is the de facto lot identifier that bridges unload → certification → packaging. But it appears on load sheets only for ABM (which has a separate "Lot Number" field). For most customers, the load-to-unload link depends on matching date + customer + part number, which is ambiguous when the same part runs on multiple shifts or across days.

**The E-Coat Load Sheet (8.2.1.2.19) is the strongest traceability form** — it captures Load Bar #, Blue Light Status, Customer, Part Number, Start/End of Bin, Raw Parts Loaded, Parts Missing at Unload, and Rejected Parts, all per shift. If every form in the system had this level of granularity, traceability would be achievable.

#### D.2 Production Run Entity Discovery

**Proposed `ProductionRun` entity:**
- ProductionRunId, PlantId, ProductionLineId (FK), ShiftCode, RunDate, CoatingTypeId (FK → LineType), PaintColour, PaintBatchLot, PaintSupplierId (FK), RecipeName, LineSpeed
- RunStartTime, RunEndTime

**Proposed `LoadRecord` child entity:**
- LoadRecordId, ProductionRunId (FK), LoadBarNumber, CustomerId (FK), PartId (FK), QuantityLoaded, QuantityAtUnload, QuantityRejected, QuantityPacked, ApprovalTagNumber, BinNumber, RackType

---

### E. Process Control Forms

**Forms analyzed:** 13 forms

#### E.1 Process Parameters Cataloged

**Powder Line Parameters:**

| Parameter | Form | Spec Limits | Frequency |
|-----------|------|------------|-----------|
| Washer Temp Stage 1 | 8.2.1.1.1 | 120-150°F | Every 30 min |
| Dry-Off Oven Temp | 8.2.1.1.1 | Setting + gauge reading | Every 30 min |
| Cure Oven Temp | 8.2.1.1.1 | Setting + gauge reading | Every 30 min |
| Stage 1-4 Pump Pressures | 8.2.1.1.1 | 10-25 PSI | Every 30 min |
| Booth Recipe (per gun): HV, Switch, Powder Qty %, kV, Total Air, Current Limit | 8.2.1.1.35 | Per recipe | At setup |
| Manual Gun: Powder Qty %, Voltage, Total Air, Current, Gun Distance | 8.2.1.1.36 | Per recipe | At setup |
| Line Speed | 8.2.1.1.4 | Per customer | At setup |
| Booth Pressure Differential | 8.2.1.1.29 | Collector gauge, Final filter | Daily |
| Batch Oven Temp | 8.2.1.1.13 | Cure temperature per customer | Per load |

**E-Coat Line Parameters:**

| Parameter | Form | Spec Limits | Frequency |
|-----------|------|------------|-----------|
| Deposition Bath Level | 8.2.1.2.1 | Above Weir | D/A shift |
| Bath Temperature | 8.2.1.2.1 | 90-98°F | D/A shift |
| Filter Pressure (In/Out) | 8.2.1.2.1 | 50 ±15 (per cell) | D/A shift |
| Rectifier Volts | 8.2.1.2.1 | Record value | D/A shift |
| Pre-Treat Spray Pressure | 8.2.1.2.2 | 10-15 PSI | D/A shift |
| Pre-Treat Exchanger Pressure | 8.2.1.2.2 | 40/40 ±15 | D/A shift |
| Tank Temperatures (1,2,4,5,9) | 8.2.1.2.26 | Various per tank | Every 30 min |
| Cure Oven | 8.2.1.2.26 | 380-415°F | Every 30 min |
| Boiler | 8.2.1.2.26 | 167-172°F | Every 30 min |
| Amp Hours | 8.2.1.2.15 | Track/calculate | Hourly |
| Metering Pump Stroke/Speed | 8.2.1.2.22 | Per tank/chemical | Weekly |

#### E.2 Reaction Plans

Only one form (8.2.1.2.10 — Out of Specification Reaction Form) documents a reaction plan, and even that is limited to "retest within 1 hour" and "escalate to quality/engineering/maintenance if out of spec >2 days." The Daily Temperature Check Log (8.2.1.1.1) has embedded instructions ("If pumps or RO unit is not acceptable, contact Supervisor or Maintenance personnel") but no formal decision tree.

**No forms link process deviations to quality outcomes.** This is a critical gap for the digital platform — the process parameter logging system needs to trigger NCR creation when readings exceed control limits.

---

### F. Lab & Chemistry Forms (E-Coat)

**Forms analyzed:** 10 forms

#### F.1 Daily Lab Analysis Template (8.2.1.2.11)

This is the **most professionally structured form** in the package. It tracks:

- **Stage 1:** Gardoclean S5176 Spray Cleaner — Free Alk (18.5-21.5 mL), Total Alk (18.5-43.0 mL)
- **Stage 2:** Gardoclean S5176 Immersion Cleaner — Free Alk (spec varies by bath age), Age of Bath (1-21 days), Total Alk (18.5-43.0 mL)
- **Stage 3:** City Water Rinse — pH (5-9), Conductivity (<500 µS)
- **Stage 4:** Gardolene V6559 Activator — Concentration (0.2-0.4%), pH (8.5-10)
- **Stage 5:** Gardobond phosphate — documented specifications
- **Stage 9:** Ecoat deposition — NV%, P/B ratio, pH, conductivity, and other parameters

**Duplicate/revision issue:** Two files share document number 8.2.1.2.11 — one with "-edit" suffix (older, 3 sheets) and one without (newer, 1 sheet, last modified 2026-02-12). The "-edit" version appears to be a superseded draft that was never removed.

#### F.2 BASF Process Database (8.2.1.2.23)

Filename literally says **"DO NOT USE, FILL OUT 2022"**. This is a macro-enabled Excel workbook (xlsm, 2.1 MB) that appears to be an abandoned BASF-provided quality tracking system. It has chart sheets. Last modified 2025-07-28, suggesting someone opened it relatively recently despite the "DO NOT USE" warning. This represents a **failed previous digitization attempt**.

#### F.3 Pigment/Binder Ratio Tracking

Two forms exist: the standard P/B Ratio worksheet (8.2.1.2.5) and a more detailed "Edit PB Ratio" version with a data input sheet and charts tab. The BASF PB Ratio Dennis file (8.2.1.2.24) is massive — **1,420 worksheet tabs**, each representing a daily P/B ratio measurement dating back to at least 2016. This is 8+ years of P/B ratio history in a single Excel file. Migration candidate.

#### F.4 Chemistry Entity Discovery

**Proposed `LabAnalysis` entity:**
- LabAnalysisId, PlantId, ProductionLineId, AnalysisDate, ShiftCode, TechnicianId (FK)
- Linked to a `LabAnalysisReading` child table per stage/parameter
- Each reading: StageNumber, ChemicalName, Parameter, SpecMin, SpecMax, ActualValue, UnitOfMeasure, InSpec (computed)

---

### G. Document Control

**Evidence of document control: Minimal.**

- Only **1 form** (8.2.1.2.26 — Ecoat Daily Temp Log) has a formal revision log with date, changes, revision number, and author.
- The Crash Report forms (8.2.1.3.1.19/20) have document number, creator, approver — but no revision history.
- **3 files** are confirmed duplicates/superseded (per duplicate_revision_map.csv): the Daily Lab Analysis "-edit" pair and the GLDC inspection record pair.
- The BASF Process Database is explicitly marked "DO NOT USE" in its filename but remains in the active forms folder.
- **23 files** have not been modified in over 2 years. The oldest: Cure Oven Cleaning Log (8.2.1.1.17) and Dry Off Oven Cleaning Log (8.2.1.1.18), both last modified November 2016 — **over 9 years old**.

---

### H. Packaging / Shipping / Hold

- **Certification Labels** (8.2.1.3.1.10): Word doc with handwritten-style label template — Date, Part #, Operator.
- **Verified Certified Label** (8.2.1.3.1.15): Two-part label — Certified (operator) + Verified By (supervisor). This is the closest thing to a ship-release approval gate.
- **Certification Log** (8.2.1.3.1.14): Tracks sorting/certification events with Original Quantity, Quantity Acceptable, Quantity Rejected, Reason for Rejection, Auditing Operator. **No supervisor sign-off field.**
- **E-coat Bulk Packaging Tracker** (8.2.1.3.1.9): Date, Bin #, Part #, Weights, Quantity, Approval Tag #.
- **GP-12 exit** is NOT explicitly captured anywhere. The GP-12 forms track the inspection results, but there is no formal "GP-12 Complete — Release to Ship" gate.

---

### I. Training / Competency / Calibration

**Training/Competency: Zero evidence.** No training records, no operator qualification forms, no competency matrices exist in this package. Operators are identified by initials only (2-3 characters) on most forms. This means you cannot link a defect to a specific qualified operator.

**Calibration: One form.** The Offline Booth Pressure Differential Gauge Check Sheet (8.2.1.1.29) is the only calibration-adjacent evidence. No gauge IDs, no calibration due dates, no certificate references appear on any inspection or testing form.

---

## 4. Critical Gap Analysis (Phase 3)

### Gap 1: The NCR Gap — SEVERITY: CRITICAL

**Status:** No formal NCR process exists. Nonconformances are scattered across 4+ forms with no central tracking number, no root cause, and no closed-loop corrective action.

**What's captured on paper vs. NCR entity:**

| NCR Entity Field | Captured? | Where? | Gap Action |
|-----------------|-----------|--------|------------|
| NcrNumber | ❌ | Nowhere | Auto-generated by platform |
| PlantId | ❌ | Implicit (all forms are Plant 1) | Automatic via RLS |
| DefectTypeId | ⚠️ | Defect tracking forms (free-text) | Normalize to taxonomy |
| SeverityRatingId | ❌ | Nowhere | NEW — must be added to workflow |
| DetectionProcessAreaId | ⚠️ | "Stage" field on fallout log | Map to ProcessArea reference data |
| QuantityAffected | ⚠️ | "Total Loaded" on defect forms | Exists on some forms |
| QuantityRejected | ⚠️ | "Total Reject" on defect forms | Exists on some forms |
| QuantityInspected | ⚠️ | GP-12 forms only | Rare |
| DispositionCodeId | ⚠️ | Disposition Log (Scrap/Rework only) | 2 of 11 codes captured |
| CustomerId | ✅ | All forms | Map to reference data |
| PartId | ✅ | All forms | Map to reference data |
| LotNumber | ⚠️ | ABM forms only | Rare |
| EstimatedCost | ❌ | Nowhere | NEW |
| Description | ⚠️ | "Reason for Rejection" (free-text) | Unstructured |
| ImmediateAction | ⚠️ | "Adjustment Made" on OOS form | E-coat chemistry only |
| RootCause | ❌ | Nowhere | NEW |
| CorrectiveAction | ❌ | Nowhere | NEW |
| CustomerApproval | ❌ | Nowhere | NEW |

**Confidence:** High. Evidence across all form categories confirms this gap.

### Gap 2: The Traceability Gap — SEVERITY: CRITICAL

**Chain breaks at 3 points:**

1. **Load → Unload:** The E-Coat Load Sheet captures Load Bar #, but the Unload Sheet does not reference it. The link depends on date + customer + part number matching, which is ambiguous for multi-shift or multi-day runs.

2. **Paint Record → Load Sheet:** The Powder Paint Record captures colour, batch lot, and recipe but not which load bars or part numbers were coated. The link is by date and colour only.

3. **Defect Tracking → Production Run:** Defect forms reference customer and part number but not load bar, paint batch, or any production run identifier.

**FK relationships needed to close:**
- `LoadRecord.ProductionRunId → ProductionRun.ProductionRunId`
- `InspectionRecord.ProductionRunId → ProductionRun.ProductionRunId`
- `NCR.ProductionRunId → ProductionRun.ProductionRunId` (new FK)
- `ProductionRun.PaintBatchLot → ChemicalBatch` (new entity or reference)

### Gap 3: The Data Consistency Gap — SEVERITY: HIGH

**97 unique defect strings** across 19 forms normalize to **~38 DefectType leaf nodes**. Specific examples of the normalization problem:

| Raw Strings (Different Forms) | Proposed Normalized Name | Count of Variants |
|------------------------------|-------------------------|-------------------|
| Light Coverage / Lt. cov / Lt. cov/ Dry spray / Light Track @ Top / Light Track @ Bottom / Light Pulley @ Top / Light Pulley @ Bottom | Light Coverage | 7 |
| Fish Eyes / Fisheyes / FE | Fisheyes | 3 |
| Hook Mark / Hook Marks / Large Hook marks / Hit Mark / Hit mark / Hit part | Hook Mark / Hit Mark | 6 |
| Damaged (Scratched) / Scratch / Scratches / Part scratched / Sanding marks / Suface Scratches | Scratch/Damage | 6 |
| Orange Peel / Orange peel | Orange Peel | 2 |
| Dirt / Dirt on Track / Dirt on Pulley / Dirt on Pully / Dirt (Blk) / Discoloured dirt / spec / Cluster of Dirt | Dirt/Debris | 7 |
| Water / Water Spots / Water Marks | Water Marks | 3 |

**Cross-customer Pareto analysis is impossible** without this normalization. The platform's 2-level DefectType hierarchy with LineType scoping will solve this, but the seed data must be carefully mapped.

### Gap 4: The Quantification Gap — SEVERITY: HIGH

PPM and yield calculations are possible from **Family 1** powder defect tracking forms (which have Total Loaded and Total Reject columns). They are NOT possible from:
- Family 2/3 defect forms (no denominator)
- E-coat general defect tracking (no Total Loaded column)
- Part Fallout Log (Y/N only)
- GP-12 forms (some have Qty Audited, but not all)

The NCR entity already has QuantityAffected, QuantityRejected, and QuantityInspected fields. The gap is that the paper forms don't consistently capture these values, especially the denominator (total inspected/loaded).

### Gap 5: The Disposition Gap — SEVERITY: HIGH

Disposition decisions are captured in **3 separate, disconnected locations:**

1. **Defect Tracking forms (Family 1):** "Repaired @ Line" / "Sent To Rework" / "Scrapped" — integer counts. Maps to REWORK, RECOAT, and SCRAP disposition codes.
2. **Rejected Material Disposition Log (8.2.1.2.28):** "Scrap/Rework" — supervisor sign-off. Maps to SCRAP and REWORK only.
3. **Nowhere** — for use-as-is, customer deviation, engineering deviation, strip-and-recoat, blend, sort, return-to-supplier, and pending-customer-decision.

Of the **11 disposition codes** in the platform, only **3** (Scrap, Rework, Recoat via "Repaired @ Line") are actively used in paper forms. The remaining 8 disposition codes represent decisions that are currently made verbally or via email with no quality record.

### Gap 6: The Temporal Gap — SEVERITY: MEDIUM

| Age Range | File Count | Examples |
|-----------|------------|---------|
| Current (< 1 year) | 62 | Most inspection forms, load sheets |
| 1-2 years | 27 | Setup verification, recipe templates |
| 2-3 years | 21 | Several customer-specific forms |
| 3-5 years | 10 | PNB/PPH sheet (2020), Weight Count (2020) |
| 5+ years | 6 | Filter Change Logs (2019), Amps Tracking (2022) |
| 9+ years | 2 | Cure/Dry-Off Oven Cleaning Logs (Nov 2016) |

The BASF Process Database file marked "DO NOT USE" was last modified July 2025, confirming that stale files remain in active directories.

### Gap 7: The Digital Readiness Gap — SEVERITY: HIGH

Structural problems for migration:
- **Free-text where dropdowns should be:** "Reason for Rejection" on disposition log, "Stage" on fallout log, "Adjustment Made" on OOS form
- **No unique record identifiers:** No form generates a unique tracking number
- **Inconsistent date formats:** Some forms use date pickers, some are free-text
- **Merged cells:** Extensive use of merged cells in inspection forms breaks tabular parsing
- **Initials instead of employee IDs:** Operators identified by 2-3 character initials, not system-linkable identifiers
- **No timestamps:** Most forms capture date but not time (exception: temperature logs, amps tracking)

### Gap 8: The Cost Visibility Gap — SEVERITY: HIGH

**Zero cost data exists** on any form in this package. No scrap cost, no rework cost, no material cost, no labor cost. The NCR entity's EstimatedCost, the NcrCostLedger, the CustomerComplaint.CostClaim, and the SupplierCar.CostChargedBack fields have no paper-form precedent. Cost tracking will be entirely new with the digital platform.

### Gap 9: The Competency Gap — SEVERITY: MEDIUM

Operators are identified by initials only. No form captures employee ID, qualification level, training completion date, or certification status. The platform cannot enforce "only qualified inspectors can sign off on GP-12" without a training/competency module.

### Gap 10: The Calibration Gap — SEVERITY: MEDIUM

**No inspection or testing form references a gauge ID or calibration status.** Film build readings are the most critical numeric measurement in the system, and there is no evidence that the DFT gauges used are calibrated or which specific gauge was used for which reading. This is a **false acceptance risk** — if a gauge is out of calibration, all readings from that gauge are suspect, but there's no way to identify which readings are affected.

### Gap 11: The Shipping-Release Gap — SEVERITY: MEDIUM

GP-12 inspection is tracked but there is no formal **GP-12 exit gate** — no form or approval step that says "GP-12 containment is complete for this program, release to normal production." The Certification Log and Verified Certified Label provide a per-lot release mechanism, but GP-12 program-level exit is not captured.

---

## 5. Platform Impact Assessment (Phase 4)

### 5a. Database Impact

#### Existing Entity Coverage Scores

| Form Category | Existing Entity | Coverage % | Covered Fields | Uncovered Fields |
|--------------|----------------|-----------|----------------|------------------|
| NCR/Disposition | quality.NonConformanceReport + NcrDisposition | 15-40% | CustomerId, PartId, Description (partial), DispositionCodeId (2 of 11), ImmediateAction (e-coat only) | NcrNumber, SeverityRatingId, DetectionProcessAreaId, QuantityAffected (inconsistent), RootCause, CostLedger, ContainmentActions, Verification lifecycle |
| Defect Tracking | quality.NonConformanceReport (as source data) | 35% | DefectTypeId (denormalized), QuantityRejected, QuantityAffected (Family 1 only), Disposition counts | Normalized taxonomy linkage, load bar traceability, operator linkage, severity |
| GP-12/Containment | quality.NcrContainmentAction | 30% | ContainmentType concept matches, QuantityInspected | Per-part-per-customer GP-12 program tracking, exit gate, defect-specific audit quantities |
| Inspection/Testing | None | 0% | — | Entire entity needed |
| Production Tracking | dbo.ProductionLine, dbo.Equipment, dbo.Shift (reference only) | 10% | Reference data exists | No ProductionRun, LoadRecord, or transactional entities |
| Process Control | None | 0% | — | Entire entity needed |
| Lab/Chemistry | None | 0% | — | Entire entity needed |
| Maintenance | None | 0% | — | Entire entity needed |
| Packaging/Shipping | None | 0% | — | Certification, bulk packaging, hold/release needed |

#### New Entity Proposals

See **Appendix D** for full SQL-style DDL and JSON definitions. Summary:

| Proposed Entity | Schema | Priority | Key Relationships |
|----------------|--------|----------|-------------------|
| `ProductionRun` | production | P1 | → ProductionLine, Shift, LineType |
| `LoadRecord` | production | P1 | → ProductionRun, Customer, Part |
| `InspectionRecord` | quality | P1 | → ProductionRun, Customer, Part, LoadRecord |
| `InspectionTestResult` | quality | P1 | → InspectionRecord, TestMethod |
| `ProcessParameterLog` | production | P2 | → ProductionLine, Equipment |
| `ProcessParameterReading` | production | P2 | → ProcessParameterLog |
| `LabAnalysis` | production | P2 | → ProductionLine |
| `LabAnalysisReading` | production | P2 | → LabAnalysis |
| `MaintenanceLog` | production | P3 | → Equipment, ProductionLine |
| `CertificationRecord` | quality | P2 | → LoadRecord, Customer, Part |
| `GP12Program` | quality | P2 | → Customer, Part |
| `GP12InspectionRecord` | quality | P2 | → GP12Program, InspectionRecord |

#### Defect Taxonomy Seed Data

See **Appendix A** for the complete mapping of 38 proposed DefectType leaf nodes. Top-level categories:

| L1 Category | L1 Code | Leaf Count | Applicable LineTypes |
|------------|---------|------------|---------------------|
| Surface Defects | SURFACE | 10 | POWDER, ECOAT |
| Coverage Defects | COVERAGE | 4 | POWDER, ECOAT |
| Contamination Defects | CONTAMINATION | 5 | POWDER, ECOAT |
| Handling/Mechanical Defects | HANDLING | 6 | POWDER, ECOAT |
| Process Defects | PROCESS | 5 | POWDER, ECOAT |
| Substrate/Material Defects | SUBSTRATE | 4 | ECOAT (mostly GLDC-specific) |
| Pre-Treatment Defects | PRETREAT | 2 | ECOAT |
| Packaging/Labeling Defects | PACKAGING | 2 | POWDER, ECOAT |

#### Reference Data Gaps

| Reference Entity | Needed Additions |
|-----------------|-----------------|
| ProcessArea | E-Coat Stage 1 through Stage 12, Pre-Treat, Deposition Tank, Cure Oven, Dry-Off Oven, Powder Booth (Inline), Powder Booth (Offline Batch), Washer, Unload, GP-12 Inspection |
| Equipment | Per-gun references (Gun 1-12 in groups), Rectifier 1/2, Metering pumps per tank, Batch oven, Filter press, Heat exchangers, Boiler |
| Customer | 18 customers identified: AGS, ABM, JAC, Warren, Tiercon, GLDC, Polycon, Presstran, JNM, Takumi, Multimatic, Rollstamp, Ultrafit, GreenBlue, MSSC, Accurate, Ursa, Toyotetsu |
| TestMethod | Cross-hatch Adhesion (ASTM D3359), Solvent Rub MEK (ASTM D4752), Film Build DFT, Pencil Hardness, Gloss @60°, Visual, Go/No-Go Gauge, Tape Adhesion Method B, Boil Test |

#### DispositionCode Coverage

| Existing Code | Found in Forms? | Evidence |
|--------------|----------------|----------|
| SCRAP | ✅ | Disposition Log, Defect Tracking "Scrapped" column |
| REWORK | ✅ | Disposition Log, Defect Tracking "Sent To Rework" column |
| RECOAT | ✅ | Defect Tracking "Repaired @ Line" (contextually = touch-up recoat) |
| USE_AS_IS | ❌ | Not captured — decision made verbally |
| RTS | ⚠️ | AGS RMA form (8.2.1.3.6.10) captures returns but not as a disposition code |
| SORT | ❌ | GP-12 is functionally a sort operation but not labeled as disposition |
| STRIP_RECOAT | ❌ | Not captured |
| CUST_DEV | ❌ | Not captured |
| ENG_DEV | ❌ | Not captured |
| PENDING_CUST | ❌ | Not captured (GLDC "suspect" inventory may be this) |
| BLEND | ❌ | Not captured |

---

### 5b. API Impact

#### Missing Endpoints (Priority Order)

| Endpoint Group | Path Pattern | Operations | Status |
|---------------|-------------|------------|--------|
| **Inspection** | /v1/inspection | CRUD, /v1/inspection/{id}/test-results, /v1/inspection/summary | NEW — Phase 3 |
| **Production Run** | /v1/production-run | CRUD, /v1/production-run/{id}/loads, /v1/production-run/active | NEW — Phase 3 |
| **Load Record** | /v1/load-record | CRUD, /v1/load-record/{id}/inspection, /v1/load-record/traceability/{tag} | NEW — Phase 3 |
| **Process Parameters** | /v1/process-parameter-log | Create, /v1/process-parameter-log/readings, /v1/process-parameter-log/out-of-spec | NEW — Phase 5 |
| **Lab Chemistry** | /v1/lab-analysis | CRUD, /v1/lab-analysis/trend/{stageId}, /v1/lab-analysis/out-of-spec | NEW — Phase 5 |
| **GP-12 Program** | /v1/gp12-program | CRUD, /v1/gp12-program/{id}/inspections, /v1/gp12-program/{id}/exit | NEW — Phase 4 |
| **Certification** | /v1/certification | Create, /v1/certification/{id}/release, /v1/certification/queue | NEW — Phase 5 |
| **Maintenance** | /v1/maintenance-log | CRUD | NEW — Phase 7 |

#### Existing Endpoint Enhancements

| Endpoint | Enhancement Needed |
|----------|-------------------|
| POST /v1/ncr/full | Add optional: `productionRunId`, `loadBarNumber`, `rackId`, `paintBatchLot`, `approvalTagNumber` — these are the traceability links from paper forms |
| GET /v1/ncr/pareto | Add filters: `byCustomer`, `byShift`, `byProductionLine`, `byCoatingType` — needed for cross-dimensional analysis |
| POST /v1/ncr/{id}/disposition | Include: `dispositionQuantity` per disposition code (to match the split disposition pattern on paper forms where some pieces are reworked and some scrapped from the same batch) |

#### Reporting Endpoints Implied by Forms

| Report | Implied By | Proposed Endpoint |
|--------|-----------|-------------------|
| Defect Pareto by Customer | Defect tracking forms (per-customer) | GET /v1/reports/defect-pareto?groupBy=customer |
| Yield by Shift | Load sheet qty vs unload qty | GET /v1/reports/yield?groupBy=shift |
| Chemistry Trend by Stage | Daily Lab Analysis | GET /v1/reports/chemistry-trend?stageId={} |
| GP-12 Status by Customer/Program | GP-12 forms | GET /v1/reports/gp12-status |
| Film Build Trend | Inspection test results | GET /v1/reports/film-build-trend?partId={}&dateRange={} |
| Process Parameter Deviation | Temperature/parameter logs | GET /v1/reports/process-deviation |

---

### 5c. Frontend/UI Impact

#### Screen Inventory

| Screen | Replaces Form(s) | Priority | Users | Input Method |
|--------|-----------------|----------|-------|-------------|
| NCR Create/Edit | 8.2.1.2.10, 8.2.1.2.28, Crash Reports | P1 | Quality Eng, Supervisor | Desktop |
| Defect Tracking Entry | 19 defect forms | P1 | Inspector, Operator | **Tablet** |
| Inspection & Test Record | 25+ inspection forms | P1 | Inspector | **Tablet** |
| Production Run / Load Sheet | 8.2.1.1.9, 8.2.1.2.19, customer load sheets | P1 | Operator | **Tablet** |
| Unload Sheet | 8.2.1.3.1.1, 8.2.1.3.1.2, customer unload sheets | P1 | Operator | **Tablet** |
| GP-12 Inspection | 14 GP-12 forms | P2 | GP-12 Inspector | **Tablet** |
| Process Parameter Log | 8.2.1.1.1, 8.2.1.2.1, 8.2.1.2.2, 8.2.1.2.26 | P2 | Operator, Tech | **Tablet** |
| Lab Analysis Entry | 8.2.1.2.11, PB Ratio forms | P2 | Lab Tech | Desktop/Tablet |
| Certification/Release | 8.2.1.3.1.14, labels | P2 | Inspector, Supervisor | Desktop |
| Paint Record | 8.2.1.1.2, 8.2.1.1.8 | P2 | Operator | **Tablet** |
| Setup Verification | 8.2.1.1.4 | P2 | Operator, Supervisor | **Tablet** |
| Dashboard — Quality KPIs | Manual aggregation today | P1 | Quality Eng, Plant Mgr | Desktop |
| Dashboard — GP-12 Status | GP-12 forms (manual tracking) | P2 | Quality Eng | Desktop |
| Dashboard — Chemistry Trends | Lab analysis (manual) | P3 | Lab Tech, Quality Eng | Desktop |

#### Form Consolidation Matrix

**Tier 1 — Identical (one configurable form):**

These forms are exact structural copies with only the customer name and part numbers changed:
- Defect Tracking: 8.2.1.3.1.5, 8.2.1.3.10.1, 8.2.1.3.21.2, 8.2.1.3.36.3, 8.2.1.3.22.1, 8.2.1.3.19.5, 8.2.1.3.26.4 (7 forms → 1)
- Inspect & Test: 8.2.1.3.1.4, 8.2.1.3.10.2, 8.2.1.3.21.3, 8.2.1.3.22.2, 8.2.1.3.26.3, 8.2.1.3.38.1 (6 forms → 1)

**Tier 2 — Minor Variants (one form with conditional sections):**

80%+ field overlap with customer-specific additions:
- Defect Tracking: 8.2.1.3.35.3 (JAC — adds "Hit mark", "Material defects"), 8.2.1.3.38.2 (Ultrafit — adds "Missing Texture/Smooth"), 8.2.1.3.3.5 (ABM — different defect vocabulary but same structure)
- Inspect & Test: 8.2.1.3.6.3/8.2.1.3.6.11 (AGS Hino — adds gloss), 8.2.1.3.25.1 (JNM — tape adhesion Method B, thickness in mils), 8.2.1.3.37.2 (Takumi — min 15μm spec)
- GP-12: 8.2.1.3.1.11, 8.2.1.3.6.2, 8.2.1.3.6.7, 8.2.1.3.25.2, 8.2.1.3.32.1, 8.2.1.3.37.1 (6 forms — same core structure, different defect columns per customer)

**Tier 3 — Genuinely Unique (dedicated templates):**
- 8.2.1.3.3.1 (ABM) — Go/No-Go gauge dimensional inspection with 16 per-part tabs
- 8.2.1.3.6.1 (AGS GM3000) — GM-specific test record with explicit ASTM references and grid-based film build maps
- 8.2.1.3.6.8 (AGS Hino Grid) — Visual zone-based inspection grid template
- 8.2.1.3.39.2 (Toyotetsu GP-12) — 9-tab workbook with foam location, film build location maps, and seal inspection
- 8.2.1.3.34.1 (GLDC) — Die-cast substrate defect tracking with per-piece inspection rows
- 8.2.1.3.26.2 (Polycon E-coat) — Dual-section defect tracking (touch-up vs. supplier defects)
- 8.2.1.3.24.6 (Warren) — Part-geometry-specific defect columns

**Consolidation impact:** 53 customer-specific forms can be reduced to approximately **12 configurable templates** — 2 standard (defect + inspection), 3 GP-12 variants, and 7 genuinely unique screens.

#### Workflow UX Patterns

| Pattern | Forms Exhibiting | UI Implication |
|---------|-----------------|---------------|
| Supervisor sign-off | Setup Verification (8.2.1.1.4), Disposition Log (8.2.1.2.28), Verified Certified Label (8.2.1.3.1.15) | Approval chain with countersignature |
| Escalation trigger | OOS Reaction Form (>2 days out of spec → email), Daily Temp Log (out of range → contact supervisor) | Notification/alert rules in process parameter logging |
| Sequential multi-step | E-Coat Crash Report (Supervisor fills first, Tech fills second) | Multi-role wizard form |
| Real-time floor entry | Temperature logs (every 30 min), Load sheets (per load bar), Defect tracking (per shift) | Mobile/tablet-optimized entry with large touch targets |
| Shift-based batching | All production forms use M/D/A shift codes | Shift selector as global context filter |

---

## 6. Cross-Plant Normalization Assessment (Phase 5)

### Plant-Universal Patterns

These patterns are almost certainly shared across all 7 plants:

1. **Load → Coat → Unload → Inspect → Defect Track → Certify cycle** — this is the fundamental production rhythm
2. **Customer-specific inspection requirements** — every plant will have customer-mandated test protocols
3. **GP-12 containment inspection** — customer-driven, applies to any plant handling new programs
4. **Certification label/log for shipment release** — required for all outbound product
5. **Defect tracking per customer per shift** — universal data capture need
6. **Approval tag as lot identifier** — appears to be a company-wide practice

### Plant-Specific Patterns

Specific to Plant 1's powder + e-coat configuration:

1. **E-coat bath chemistry tracking** — only applies to plants with e-coat lines. Other plants may have liquid paint chemistry (different parameters) or no chemistry tracking at all.
2. **Powder booth recipe parameters** (kV, powder %, air, current limitation per gun) — powder-specific
3. **Pre-treat daily checklist** — e-coat-specific (pre-treat stages 1-5)
4. **Amp hours tracking** — e-coat-specific
5. **P/B ratio tracking** — e-coat-specific
6. **E-coat crash reports** — e-coat-specific failure mode
7. **Offline batch oven process** — Plant 1-specific equipment configuration

### Customer-Driven Patterns

| Pattern | Driven By | Platform Design |
|---------|-----------|----------------|
| Film build spec ranges | Customer TDS | Customer-Part configuration table |
| Specific test methods (GM3000, GMW14829) | OEM spec callout | TestMethod reference data per Customer |
| GP-12 defect list per customer | Customer quality agreement | GP-12 program configuration |
| Dimensional inspection (ABM go/no-go) | Customer drawing requirements | Customer-specific inspection template |
| Die-cast substrate defect tracking (GLDC) | Incoming material quality | Supplier quality / incoming inspection module |

### Normalization Checklist for Plants 2-7

| Comparison Dimension | Plant 1 Baseline | Evidence to Collect | Impact |
|---------------------|-----------------|---------------------|--------|
| Coating technologies | Powder + E-Coat | What lines does the plant operate? (liquid, anodize, etc.) | High — determines process parameter schema |
| Defect vocabulary | 38 normalized types, 3 taxonomy families | Collect all defect column headers — do they use the same vocabulary? | High — feeds DefectType seed data |
| Load/unload form structure | Load bar # (e-coat), start/end load bar (powder) | What production identifiers are used? | High — determines LoadRecord schema |
| Customer overlap | 18 customers | Which customers overlap? Do shared customers use the same forms? | High — determines customer config scope |
| NCR process | None exists | Does any plant have a formal NCR form? | Critical — if one plant has a better process, adopt it |
| Chemistry tracking | BASF e-coat chemistry | What paint suppliers and what chemistry? | Medium — LabAnalysis schema flexibility |
| GP-12 structure | Per-customer per-part tabs | Same structure or different? | Medium — GP12Program entity design |
| Document control | Minimal | Does any plant have revision control? | Medium — DocumentControl entity need |
| Approval tag usage | Used as lot identifier on unload/cert | Same practice or different? | Medium — traceability chain design |
| Shift structure | M/D/A (3 shifts) | How many shifts? Same codes? | Low — reference data config |

### Cross-Plant Defect Taxonomy Guidance

| Defect Category | Universal? | Coating-Specific? |
|----------------|-----------|-------------------|
| Light Coverage | Universal | — |
| Orange Peel | Universal (but severity differs by process) | — |
| Scratches/Damage | Universal | — |
| Dirt/Debris/Contamination | Universal | — |
| Hook Marks | Universal (any racked process) | — |
| Fisheyes | Universal | — |
| Back Ionization | Powder-only | POWDER |
| Paint in Threads | Powder-only | POWDER |
| Bubbles | E-coat primary | ECOAT |
| Bare Metal | E-coat primary | ECOAT |
| Paint Runs/Sags | E-coat + Liquid | ECOAT, LIQUID |
| Water Spots | E-coat primary | ECOAT |
| Rust | E-coat (pre-treat failure) | ECOAT |
| Outgassing | E-coat-only (not yet tracked) | ECOAT |
| Faraday Cage | E-coat-only (not yet tracked) | ECOAT |
| Edge Pull-Back | E-coat-only (not yet tracked) | ECOAT |
| Fluidization Issues | Powder-only (not yet tracked) | POWDER |
| Substrate defects (Belt Mark, Misfill, etc.) | Process-agnostic (incoming material) | ALL |

---

## Appendix A: Defect Taxonomy Mapping Table

```csv
FormDefectName,ProposedParentCode,ProposedParentName,ProposedDefectCode,ProposedDefectName,LineTypeCode,DefaultSeverityId,SortOrderHint,Notes
Light Coverage,COVERAGE,Coverage Defects,COVERAGE-LIGHT,Light Coverage,POWDER,,10,Universal across all powder forms
Light Coverage,COVERAGE,Coverage Defects,COVERAGE-LIGHT,Light Coverage,ECOAT,,10,Universal across all ecoat forms
Lt. cov/ Dry spray,COVERAGE,Coverage Defects,COVERAGE-LIGHT,Light Coverage,POWDER,,10,AGS/Accurate variant - normalize
Lt. cov,COVERAGE,Coverage Defects,COVERAGE-LIGHT,Light Coverage,ECOAT,,10,AGS GP12 variant
Light Track @ Top,COVERAGE,Coverage Defects,COVERAGE-LIGHT,Light Coverage,POWDER,,10,Warren location-specific - normalize to Light Coverage + location metadata
Light Track a@ bottom,COVERAGE,Coverage Defects,COVERAGE-LIGHT,Light Coverage,POWDER,,10,Warren location-specific
Light Pulley @ top,COVERAGE,Coverage Defects,COVERAGE-LIGHT,Light Coverage,POWDER,,10,Warren location-specific
Light Pulley @ Bottom,COVERAGE,Coverage Defects,COVERAGE-LIGHT,Light Coverage,POWDER,,10,Warren location-specific
Heavy powder,COVERAGE,Coverage Defects,COVERAGE-HEAVY,Heavy Coverage/Build-Up,POWDER,,20,Excess film build
Heavy Paint,COVERAGE,Coverage Defects,COVERAGE-HEAVY,Heavy Coverage/Build-Up,POWDER,,20,ABM variant
Heavy,COVERAGE,Coverage Defects,COVERAGE-HEAVY,Heavy Coverage/Build-Up,POWDER,,20,Warren variant
Build Up,COVERAGE,Coverage Defects,COVERAGE-HEAVY,Heavy Coverage/Build-Up,POWDER,,20,Standard template
Build Up,COVERAGE,Coverage Defects,COVERAGE-HEAVY,Heavy Coverage/Build-Up,ECOAT,,20,Ecoat variant
Bare Metal,COVERAGE,Coverage Defects,COVERAGE-BARE,Bare Metal/No Coat,ECOAT,,30,E-coat specific
Dry spray,COVERAGE,Coverage Defects,COVERAGE-DRY,Dry Spray,POWDER,,40,Separate from light coverage
Orange Peel,SURFACE,Surface Defects,SURFACE-ORANGEPEEL,Orange Peel,POWDER,,10,Universal
Orange peel,SURFACE,Surface Defects,SURFACE-ORANGEPEEL,Orange Peel,ECOAT,,10,Universal
Rough Spots,SURFACE,Surface Defects,SURFACE-ORANGEPEEL,Orange Peel,ECOAT,,10,Ecoat variant - normalize
Fish Eyes,SURFACE,Surface Defects,SURFACE-FISHEYE,Fisheyes,POWDER,,20,
Fisheyes,SURFACE,Surface Defects,SURFACE-FISHEYE,Fisheyes,POWDER,,20,ABM variant
FE,SURFACE,Surface Defects,SURFACE-FISHEYE,Fisheyes,POWDER,,20,Abbreviated
Pinholes,SURFACE,Surface Defects,SURFACE-PINHOLE,Pinholes,POWDER,,30,AGS/Accurate forms
Bubbles,SURFACE,Surface Defects,SURFACE-BUBBLE,Bubbles,ECOAT,,40,E-coat specific
Paint Runs,SURFACE,Surface Defects,SURFACE-RUNS,Runs/Sags,ECOAT,,50,E-coat defect tracking
Back Ionization,PROCESS,Process Defects,PROCESS-BACKION,Back Ionization,POWDER,,10,Powder-specific
Missing Texture/Smooth,PROCESS,Process Defects,PROCESS-TEXTURE,Missing Texture,POWDER,,20,Ultrafit-specific
Paint in Threads,PROCESS,Process Defects,PROCESS-THREADS,Paint in Threads,POWDER,,30,Standard powder template
Adhesion Fail,PROCESS,Process Defects,PROCESS-ADHESION,Adhesion Failure,ECOAT,,40,GLDC form
Rust,PRETREAT,Pre-Treatment Defects,PRETREAT-RUST,Rust/Corrosion,ECOAT,,10,Pre-treat failure
Water Spots,PRETREAT,Pre-Treatment Defects,PRETREAT-WATER,Water Marks/Spots,ECOAT,,20,Post-rinse issue
Water,PRETREAT,Pre-Treatment Defects,PRETREAT-WATER,Water Marks/Spots,POWDER,,20,Standard powder template
Water Marks,PRETREAT,Pre-Treatment Defects,PRETREAT-WATER,Water Marks/Spots,ECOAT,,20,Polycon variant
Dirt,CONTAMINATION,Contamination Defects,CONTAM-DIRT,Dirt/Debris,ECOAT,,10,
Debris,CONTAMINATION,Contamination Defects,CONTAM-DIRT,Dirt/Debris,POWDER,,10,Standard template
Discoloured dirt / spec,CONTAMINATION,Contamination Defects,CONTAM-DIRT,Dirt/Debris,POWDER,,10,AGS variant
Cluster of Dirt,CONTAMINATION,Contamination Defects,CONTAM-DIRT,Dirt/Debris,POWDER,,10,AGS variant
Dirt on Track,CONTAMINATION,Contamination Defects,CONTAM-DIRT,Dirt/Debris,POWDER,,10,Warren/ABM location-specific
Dirt on Pulley,CONTAMINATION,Contamination Defects,CONTAM-DIRT,Dirt/Debris,POWDER,,10,Warren/ABM location-specific
Dirt on Pully,CONTAMINATION,Contamination Defects,CONTAM-DIRT,Dirt/Debris,POWDER,,10,Typo variant
Dirt (Blk),CONTAMINATION,Contamination Defects,CONTAM-DIRT,Dirt/Debris,POWDER,,10,AGS GP12 variant
Contamination,CONTAMINATION,Contamination Defects,CONTAM-GENERAL,General Contamination,POWDER,,20,Standard template catch-all
Contamination,CONTAMINATION,Contamination Defects,CONTAM-GENERAL,General Contamination,ECOAT,,20,
Oil,CONTAMINATION,Contamination Defects,CONTAM-OIL,Oil Contamination,POWDER,,30,AGS/ABM forms
OIL,CONTAMINATION,Contamination Defects,CONTAM-OIL,Oil Contamination,POWDER,,30,ABM variant
Fiber,CONTAMINATION,Contamination Defects,CONTAM-FIBER,Fiber/Foreign Material,POWDER,,40,AGS forms
Off colour (Discoloured),CONTAMINATION,Contamination Defects,CONTAM-DISCOLOR,Discoloration/Off Color,POWDER,,50,AGS/Accurate
Off color,CONTAMINATION,Contamination Defects,CONTAM-DISCOLOR,Discoloration/Off Color,POWDER,,50,AGS GP12
Hook Mark,HANDLING,Handling/Mechanical Defects,HANDLING-HOOK,Hook Mark,POWDER,,10,Standard template
Hook Marks,HANDLING,Handling/Mechanical Defects,HANDLING-HOOK,Hook Mark,POWDER,,10,Plural variant
Large Hook marks,HANDLING,Handling/Mechanical Defects,HANDLING-HOOK,Hook Mark,POWDER,,10,ABM variant
Hit Mark,HANDLING,Handling/Mechanical Defects,HANDLING-HIT,Hit Mark/Impact,POWDER,,20,AGS forms
Hit mark,HANDLING,Handling/Mechanical Defects,HANDLING-HIT,Hit Mark/Impact,POWDER,,20,JAC/AGS variant
Hit part,HANDLING,Handling/Mechanical Defects,HANDLING-HIT,Hit Mark/Impact,POWDER,,20,AGS 3pc
Touch Mark,HANDLING,Handling/Mechanical Defects,HANDLING-TOUCH,Touch Mark,POWDER,,30,AGS/Accurate
Damaged (Scratched),HANDLING,Handling/Mechanical Defects,HANDLING-SCRATCH,Scratch/Damage,POWDER,,40,Standard template
Damaged (Scratched),HANDLING,Handling/Mechanical Defects,HANDLING-SCRATCH,Scratch/Damage,ECOAT,,40,Ecoat variant
Scratch,HANDLING,Handling/Mechanical Defects,HANDLING-SCRATCH,Scratch/Damage,ECOAT,,40,GLDC
Scratches,HANDLING,Handling/Mechanical Defects,HANDLING-SCRATCH,Scratch/Damage,ECOAT,,40,Polycon variant
Part scratched,HANDLING,Handling/Mechanical Defects,HANDLING-SCRATCH,Scratch/Damage,POWDER,,40,AGS 3pc
Suface Scratches,HANDLING,Handling/Mechanical Defects,HANDLING-SCRATCH,Scratch/Damage,ECOAT,,40,Polycon typo variant
Sanding marks,HANDLING,Handling/Mechanical Defects,HANDLING-SCRATCH,Scratch/Damage,POWDER,,40,AGS 3pc
Part dropped,HANDLING,Handling/Mechanical Defects,HANDLING-DROP,Dropped/Dent,POWDER,,50,AGS 3pc
Dent,HANDLING,Handling/Mechanical Defects,HANDLING-DROP,Dropped/Dent,ECOAT,,50,GLDC/Polycon
Handling damage,HANDLING,Handling/Mechanical Defects,HANDLING-GENERAL,General Handling Damage,POWDER,,60,AGS GP12
STUCK,HANDLING,Handling/Mechanical Defects,HANDLING-STUCK,Stuck Parts,POWDER,,70,ABM-specific
Tight Clip Top,HANDLING,Handling/Mechanical Defects,HANDLING-CLIP,Tight Clip/Fitment,POWDER,,80,Warren-specific
Tight Clip Bottom,HANDLING,Handling/Mechanical Defects,HANDLING-CLIP,Tight Clip/Fitment,POWDER,,80,Warren-specific
Belt Mark,SUBSTRATE,Substrate/Material Defects,SUBSTRATE-BELTMARK,Belt Mark,ECOAT,,10,GLDC die-cast specific
Misfill,SUBSTRATE,Substrate/Material Defects,SUBSTRATE-MISFILL,Misfill/Short Shot,ECOAT,,20,GLDC die-cast specific
Pin Push,SUBSTRATE,Substrate/Material Defects,SUBSTRATE-PINPUSH,Pin Push,ECOAT,,30,GLDC die-cast specific
Gouge,SUBSTRATE,Substrate/Material Defects,SUBSTRATE-GOUGE,Gouge,ECOAT,,40,GLDC
Sink,SUBSTRATE,Substrate/Material Defects,SUBSTRATE-SINK,Sink Mark,ECOAT,,50,GLDC
Flash,SUBSTRATE,Substrate/Material Defects,SUBSTRATE-FLASH,Flash,ECOAT,,60,GLDC
Sharp Edge,SUBSTRATE,Substrate/Material Defects,SUBSTRATE-SHARP,Sharp Edge,ECOAT,,70,GLDC
Tool Marks,SUBSTRATE,Substrate/Material Defects,SUBSTRATE-TOOL,Tool Marks,ECOAT,,80,Polycon
Over Sand,SUBSTRATE,Substrate/Material Defects,SUBSTRATE-OVERSAND,Over Sand,ECOAT,,90,Polycon
Material Defect,SUBSTRATE,Substrate/Material Defects,SUBSTRATE-GENERAL,General Material Defect,POWDER,,100,ABM/JAC
Material defects,SUBSTRATE,Substrate/Material Defects,SUBSTRATE-GENERAL,General Material Defect,POWDER,,100,JAC variant
Raw Defects,SUBSTRATE,Substrate/Material Defects,SUBSTRATE-GENERAL,General Material Defect,ECOAT,,100,Polycon incoming
Paint Defect,PROCESS,Process Defects,PROCESS-GENERAL,General Paint Defect,ECOAT,,50,GLDC catch-all
```

---

## Appendix D: Proposed New Entity Schemas (Concise DDL)

### ProductionRun

```sql
CREATE TABLE production.ProductionRun (
    ProductionRunId     INT IDENTITY PRIMARY KEY,
    PlantId             INT NOT NULL REFERENCES dbo.Plant(PlantId),
    ProductionLineId    INT NOT NULL REFERENCES dbo.ProductionLine(ProductionLineId),
    LineTypeCode        VARCHAR(10) NOT NULL, -- POWDER, ECOAT
    ShiftCode           CHAR(1) NOT NULL, -- M, D, A
    RunDate             DATE NOT NULL,
    RunStartTime        DATETIME2 NULL,
    RunEndTime          DATETIME2 NULL,
    PaintColour         NVARCHAR(50) NULL,
    PaintBatchLot       NVARCHAR(50) NULL,
    PaintSupplierId     INT NULL REFERENCES dbo.Supplier(SupplierId),
    RecipeName          NVARCHAR(100) NULL,
    LineSpeed           DECIMAL(6,2) NULL,
    Notes               NVARCHAR(MAX) NULL,
    CreatedBy           INT NOT NULL,
    CreatedDate         DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    ModifiedBy          INT NULL,
    ModifiedDate        DATETIME2 NULL
);
```

### LoadRecord

```sql
CREATE TABLE production.LoadRecord (
    LoadRecordId        INT IDENTITY PRIMARY KEY,
    ProductionRunId     INT NOT NULL REFERENCES production.ProductionRun(ProductionRunId),
    LoadBarNumber       INT NULL, -- E-coat; powder uses start/end range
    StartLoadBar        INT NULL, -- Powder inline
    EndLoadBar          INT NULL,
    CustomerId          INT NOT NULL REFERENCES dbo.Customer(CustomerId),
    PartId              INT NOT NULL REFERENCES dbo.Part(PartId),
    QuantityLoaded      INT NULL,
    QuantityAtUnload    INT NULL,
    QuantityRejected    INT NULL,
    QuantityPacked      INT NULL,
    QuantityScrapped    INT NULL,
    ApprovalTagNumber   NVARCHAR(50) NULL,
    BinNumber           NVARCHAR(50) NULL,
    LotNumber           NVARCHAR(50) NULL,
    RackType            NVARCHAR(50) NULL,
    ReworkFlag           BIT NOT NULL DEFAULT 0,
    OperatorInitials    NVARCHAR(10) NULL,
    Notes               NVARCHAR(500) NULL,
    CreatedBy           INT NOT NULL,
    CreatedDate         DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);
```

### InspectionRecord

```sql
CREATE TABLE quality.InspectionRecord (
    InspectionRecordId  INT IDENTITY PRIMARY KEY,
    PlantId             INT NOT NULL REFERENCES dbo.Plant(PlantId),
    ProductionRunId     INT NULL REFERENCES production.ProductionRun(ProductionRunId),
    LoadRecordId        INT NULL REFERENCES production.LoadRecord(LoadRecordId),
    CustomerId          INT NOT NULL REFERENCES dbo.Customer(CustomerId),
    PartId              INT NOT NULL REFERENCES dbo.Part(PartId),
    InspectionTypeId    INT NOT NULL, -- FK to LookupValue (Unload, GP-12, Trial, Final, Pre-Cure)
    InspectionDate      DATE NOT NULL,
    ShiftCode           CHAR(1) NOT NULL,
    InspectorId         INT NULL, -- FK to Employee when available
    InspectorInitials   NVARCHAR(10) NULL,
    OverallResult       VARCHAR(20) NOT NULL, -- ACCEPT, REJECT, CONDITIONAL
    Notes               NVARCHAR(MAX) NULL,
    CreatedBy           INT NOT NULL,
    CreatedDate         DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE TABLE quality.InspectionTestResult (
    TestResultId        INT IDENTITY PRIMARY KEY,
    InspectionRecordId  INT NOT NULL REFERENCES quality.InspectionRecord(InspectionRecordId),
    TestMethodId        INT NOT NULL, -- FK to reference data (ASTM D3359, etc.)
    ResultType          VARCHAR(10) NOT NULL, -- PASS_FAIL, NUMERIC
    PassFail            BIT NULL,
    NumericValue        DECIMAL(10,4) NULL,
    UnitOfMeasure       NVARCHAR(20) NULL, -- microns, mils, gloss units
    SpecMin             DECIMAL(10,4) NULL,
    SpecMax             DECIMAL(10,4) NULL,
    SampleNumber        INT NULL, -- 1-6 for film build readings
    LocationCode        NVARCHAR(50) NULL, -- from customer film build map
    Notes               NVARCHAR(500) NULL
);
```

### LabAnalysis

```sql
CREATE TABLE production.LabAnalysis (
    LabAnalysisId       INT IDENTITY PRIMARY KEY,
    PlantId             INT NOT NULL REFERENCES dbo.Plant(PlantId),
    ProductionLineId    INT NOT NULL REFERENCES dbo.ProductionLine(ProductionLineId),
    AnalysisDate        DATE NOT NULL,
    ShiftCode           CHAR(1) NOT NULL,
    TechnicianId        INT NULL,
    TechnicianInitials  NVARCHAR(10) NULL,
    Notes               NVARCHAR(MAX) NULL,
    CreatedBy           INT NOT NULL,
    CreatedDate         DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE TABLE production.LabAnalysisReading (
    ReadingId           INT IDENTITY PRIMARY KEY,
    LabAnalysisId       INT NOT NULL REFERENCES production.LabAnalysis(LabAnalysisId),
    StageNumber         INT NOT NULL, -- 1-12 for e-coat stages
    ChemicalName        NVARCHAR(100) NOT NULL,
    ParameterName       NVARCHAR(100) NOT NULL, -- Free Alk, Total Alk, pH, Conductivity, %NV, P/B Ratio
    SpecMin             DECIMAL(10,4) NULL,
    SpecMax             DECIMAL(10,4) NULL,
    ActualValue         DECIMAL(10,4) NULL,
    UnitOfMeasure       NVARCHAR(20) NULL,
    InSpec              AS CASE WHEN ActualValue BETWEEN SpecMin AND SpecMax THEN 1 ELSE 0 END
);
```

### ProcessParameterLog

```sql
CREATE TABLE production.ProcessParameterLog (
    LogId               INT IDENTITY PRIMARY KEY,
    PlantId             INT NOT NULL REFERENCES dbo.Plant(PlantId),
    ProductionLineId    INT NOT NULL REFERENCES dbo.ProductionLine(ProductionLineId),
    LogDate             DATE NOT NULL,
    ShiftCode           CHAR(1) NOT NULL,
    OperatorId          INT NULL,
    OperatorInitials    NVARCHAR(10) NULL,
    CreatedBy           INT NOT NULL,
    CreatedDate         DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE TABLE production.ProcessParameterReading (
    ReadingId           INT IDENTITY PRIMARY KEY,
    LogId               INT NOT NULL REFERENCES production.ProcessParameterLog(LogId),
    ReadingTime         DATETIME2 NOT NULL,
    EquipmentId         INT NULL REFERENCES dbo.Equipment(EquipmentId),
    ParameterName       NVARCHAR(100) NOT NULL,
    SpecMin             DECIMAL(10,4) NULL,
    SpecMax             DECIMAL(10,4) NULL,
    ActualValue         DECIMAL(10,4) NULL,
    UnitOfMeasure       NVARCHAR(20) NULL,
    InSpec              AS CASE WHEN ActualValue BETWEEN SpecMin AND SpecMax THEN 1 ELSE 0 END,
    ReasonCode          NVARCHAR(50) NULL, -- for readings taken outside 30-min cycle
    Notes               NVARCHAR(500) NULL
);
```

### GP12Program

```sql
CREATE TABLE quality.GP12Program (
    GP12ProgramId       INT IDENTITY PRIMARY KEY,
    PlantId             INT NOT NULL REFERENCES dbo.Plant(PlantId),
    CustomerId          INT NOT NULL REFERENCES dbo.Customer(CustomerId),
    PartId              INT NOT NULL REFERENCES dbo.Part(PartId),
    ProgramName         NVARCHAR(100) NOT NULL,
    StartDate           DATE NOT NULL,
    PlannedExitDate     DATE NULL,
    ActualExitDate      DATE NULL,
    StatusCode          VARCHAR(20) NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, EXITED, EXTENDED
    RequiredShipments   INT NULL, -- customer-required # of clean shipments before exit
    CompletedShipments  INT NOT NULL DEFAULT 0,
    Notes               NVARCHAR(MAX) NULL,
    CreatedBy           INT NOT NULL,
    CreatedDate         DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);
```

### JSON Entity Definitions

```json
{
  "ProductionRun": {
    "schema": "production",
    "needsRLS": true,
    "needsTemporalVersioning": false,
    "primaryKey": "ProductionRunId",
    "foreignKeys": ["PlantId→dbo.Plant", "ProductionLineId→dbo.ProductionLine", "PaintSupplierId→dbo.Supplier"],
    "cardinality": {"LoadRecord": "one-to-many", "InspectionRecord": "one-to-many", "ProcessParameterLog": "one-to-many"}
  },
  "LoadRecord": {
    "schema": "production",
    "needsRLS": false,
    "needsTemporalVersioning": false,
    "primaryKey": "LoadRecordId",
    "foreignKeys": ["ProductionRunId→production.ProductionRun", "CustomerId→dbo.Customer", "PartId→dbo.Part"],
    "cardinality": {"InspectionRecord": "one-to-many"}
  },
  "InspectionRecord": {
    "schema": "quality",
    "needsRLS": true,
    "needsTemporalVersioning": true,
    "primaryKey": "InspectionRecordId",
    "foreignKeys": ["PlantId→dbo.Plant", "ProductionRunId→production.ProductionRun", "LoadRecordId→production.LoadRecord", "CustomerId→dbo.Customer", "PartId→dbo.Part"],
    "cardinality": {"InspectionTestResult": "one-to-many"}
  },
  "LabAnalysis": {
    "schema": "production",
    "needsRLS": true,
    "needsTemporalVersioning": false,
    "primaryKey": "LabAnalysisId",
    "foreignKeys": ["PlantId→dbo.Plant", "ProductionLineId→dbo.ProductionLine"],
    "cardinality": {"LabAnalysisReading": "one-to-many"}
  },
  "ProcessParameterLog": {
    "schema": "production",
    "needsRLS": true,
    "needsTemporalVersioning": false,
    "primaryKey": "LogId",
    "foreignKeys": ["PlantId→dbo.Plant", "ProductionLineId→dbo.ProductionLine"],
    "cardinality": {"ProcessParameterReading": "one-to-many"}
  },
  "GP12Program": {
    "schema": "quality",
    "needsRLS": true,
    "needsTemporalVersioning": true,
    "primaryKey": "GP12ProgramId",
    "foreignKeys": ["PlantId→dbo.Plant", "CustomerId→dbo.Customer", "PartId→dbo.Part"],
    "cardinality": {"GP12InspectionRecord": "one-to-many"}
  }
}
```

---

*End of Report. 133 files examined. 11 critical gaps identified. 6 new entity schemas proposed. 38 defect types normalized from 97 raw strings. 53 customer-specific forms reducible to ~12 configurable templates.*
