# BATCH A3: Section 3 (Detailed Analysis) Subsections E–I + Section 4 (Critical Gap Analysis)

---

## Section 3: Detailed Analysis (continued)

### E. Waste Management Forms

**Forms analyzed:** 8.2.2.17 (Booth Sludge), 8.2.2.18 (Empty), 8.2.2.19 (Still Bottoms), 8.2.2.20 (Waste Paint), 8.2.2.21 (Waste Zinc), 8.2.2.25 (Solvent Usage Tracking — waste-relevant fields)

#### E1. Are waste volumes tracked for regulatory compliance?

**No.** These are not tracking forms — they are printable drum labels. This is worse than expected.

All five "waste" files (8.2.2.17 through 8.2.2.21) share an identical structure: a single sheet named "In Process Tag" at 25×14 cells containing nothing but a large title (BOOTH SLUDGE / STILL BOTTOMS / WASTE PAINT / WASTE ZINC / EMPTY) and a footer with the document number, creation date (05/05/17), and revision date (08/01/23). There are zero data fields. No volume, no weight, no date, no container ID, no manifest number, no disposal vendor, no regulatory stream classification.

These are labels that get printed and physically attached to drums or containers in the waste storage area. They exist so a waste hauler can identify what's in each drum. That's the entire function.

The Solvent Usage Tracking form (8.2.2.25) captures consumption data (amount raw, total consumption, batch, same drum/new drum) for primers and solvents, but this is an input tracking form, not a waste output form. It tells you how much solvent went into the process, not how much waste came out.

**Net assessment:** Plant 2 has no digital waste volume tracking whatsoever. If an environmental auditor asked "How many gallons of booth sludge did you generate in Q3?", the answer would come from paper manifests filed with the waste hauler — not from any internal system. This is a regulatory risk and a complete cost visibility black hole.

> **Evidence:** 8.2.2.17/In Process Tag through 8.2.2.21/In Process Tag — all five files contain only title text and document footer | **Confidence:** High

#### E2. Linkage between waste generation and production volume?

**Nonexistent.** There is no data to link. The waste labels capture no quantities and the Solvent Usage Tracking form has no production volume denominator. You cannot calculate waste-per-unit-painted, waste-per-gallon-consumed, or any other waste intensity metric from these forms.

#### E3. Waste disposal records traceable to time periods and production runs?

**No.** No date fields on waste labels. No production run reference. No time period stamping. The only temporal data is the form revision date (08/01/23), which tells you when the label template was last revised, not when waste was generated.

#### E4. Waste Tracking Entity Discovery

**Recommendation:** Standalone entity, not a child of ProductionRun.

**Rationale:** Waste generation is continuous and accumulates across multiple production runs. A drum of booth sludge accumulates over days or weeks, not per-rack. However, a foreign key to ProductionLine is appropriate since waste streams are line-specific (each line's booths generate their own sludge).

**Proposed `production.WasteRecord` entity:**

| Field | Type | Nullable | FK Target | Notes |
|---|---|---|---|---|
| WasteRecordId | int (PK) | No | — | |
| PlantId | int | No | dbo.Plant | RLS |
| ProductionLineId | int | Yes | dbo.ProductionLine | Line generating waste |
| WasteStreamCode | nvarchar(20) | No | — | BOOTH_SLUDGE, STILL_BOTTOMS, WASTE_PAINT, WASTE_ZINC, EMPTY_CONTAINER |
| ContainerId | nvarchar(30) | Yes | — | Drum/container barcode |
| DateOpened | date | Yes | — | When container started accumulating |
| DateClosed | date | Yes | — | When container sealed for disposal |
| QuantityGal | decimal(8,2) | Yes | — | Volume |
| WeightLbs | decimal(8,2) | Yes | — | Weight (regulatory requirement) |
| ManifestNumber | nvarchar(30) | Yes | — | Waste hauler manifest |
| DisposalVendor | nvarchar(100) | Yes | — | |
| RegulatoryClassification | nvarchar(50) | Yes | — | RCRA code if applicable |
| DisposalDate | date | Yes | — | |
| DisposalMethod | nvarchar(50) | Yes | — | Incineration, landfill, reclaim, etc. |
| EstimatedCostCAD | decimal(10,2) | Yes | — | Disposal cost |
| Comments | nvarchar(500) | Yes | — | |
| CreatedByEmployeeId | int | Yes | — | |
| CreatedAt | datetime2 | No | — | |

- **Needs temporal versioning?** No.
- **Needs RLS?** Yes — plant-scoped.

---

### F. Post-Paint Operations

**Forms analyzed:** 8.2.2.7 (Daily Sanding Tally), 8.2.2.8 (Daily Buffing Tally), 8.2.2.9 (Daily Deburring Tally), 8.2.2.31 (Daily Hummer Sanding Tally), 8.2.2.30 (Buffing Summary Template)

#### F1. Are post-paint operations tracked by part number and customer?

**Partially.** The tally sheets record part number/description, but customer must be inferred from the part name — it is never an explicit field.

- **Sanding Tally (8.2.2.7):** Columns are Time Spent, Part #/Description, Qty Sanded. Open-ended — operator writes whatever part name they're working on. No customer field.
- **Buffing Tally (8.2.2.8):** Same structure: Time Spent, Part #/Description, Qty Buffed. However, the KANBAN sheet tab pre-lists Spyder parts by name (LH Low Fairing, RH Low Fairing, Front Fascia, Hood, LH Fairing, RH Fairing, LH Vent Panel, RH Vent Panel, Tank Cover, LH Access Panel, RH Access Panel, F3T variants) with AM/PM columns. This is customer-specific (Spyder = BRP program via Rollstamp) but hardcoded to one customer's parts.
- **Deburring Tally (8.2.2.9):** Part Name, two TIME columns. Even sparser than sanding — no quantity column, just time blocks.
- **Hummer Sanding Tally (8.2.2.31):** Hourly time blocks (6:30–3:00), Running Tally, Total per Hour. Product-specific (Hummer = GM program) but captures throughput rate rather than part-level detail. No part number — just hourly running count.

#### F2. Link between post-paint rework and original paint defect?

**None.** This is the accountability black hole the prompt warned about.

No tally sheet captures: defect type (why was this part sanded/buffed?), line number (which line produced it), production date (when was it painted), rack/carrier number, or paint batch. A part enters the sanding station and gets counted as "1 sanded" — the reason, origin, and root cause are lost.

The Buffing Summary (8.2.2.30) does track "Returned to Buff" and "RW after buff" (rework after buffing) with FTQ calculations — this tells you the rate at which buffing fails but not why. The FTQ formula is:

> **FTQ = 1 − (RW after buff / Ttl Buffed)**

The Charts Info tab has 272 daily data points dating from January 2023 — this is genuinely useful trend data, but it's aggregate. You know that on 2023-01-11 the plant buffed 855 parts, but you don't know which parts, from which lines, with which defects.

The "Rework- To Be Sanded" tag (8.2.2.15) and "To Be Buffed" tag (8.2.2.16) are physical tags with Quantity, Part Description, Colour, Date, and L/H or R/H (left/right hand) fields — but no defect code and no NCR reference. These tags identify *what* needs rework, not *why*.

> **Evidence:** 8.2.2.7/1st, 8.2.2.8/Days, 8.2.2.9/1st, 8.2.2.31/1st, 8.2.2.30/Charts Info | **Confidence:** High

#### F3. Can you calculate rework rates from the tally sheets?

**For buffing: yes, from the summary. For sanding and deburring: no.**

The Buffing Summary (8.2.2.30) already calculates:

- Parts Into Buff from Line (input)
- Total Parts Buffed (output)
- Average per Person
- Average per Hour (target: 10/hr)
- % Efficiency
- Returned to Buff (rework count)
- RW after Buff (parts rejected after buffing)
- FTQ for Buff

These are real KPIs. However, "Into Buff from Line" has zero data populated in most months (the column shows 0 or blank across Jan–Oct 2023 data), making the efficiency calculation return `#DIV/0!` errors. The formulas exist but the input data isn't being entered. "Ttl Buffed" is populated (323–855 parts/day in populated months), suggesting operators report output but not input. This means the FTQ calculation defaults to 1.0 (100%) when RW fields are also zero — masking the real rate.

Sanding and deburring tally sheets capture quantity per part per operator per day. You could sum these to get daily sanding/deburring volume, but there's no input denominator (total parts painted) to calculate a rework rate. The Hummer Sanding Tally gives hourly throughput rates which could inform staffing decisions but not quality metrics.

#### F4. Post-Paint Operations Entity Discovery

**Recommendation:** Child of ProductionRun AND linkable to NCR.

Post-paint operations serve two purposes — routine finishing (all parts get buffed) and defect rework (some parts get sanded because they have runs or dirt). The entity needs to support both use cases.

**Proposed `production.PostPaintOperation` entity:**

| Field | Type | Nullable | FK Target | Notes |
|---|---|---|---|---|
| PostPaintOperationId | int (PK) | No | — | |
| PlantId | int | No | dbo.Plant | RLS |
| OperationDate | date | No | — | |
| ShiftId | int | Yes | dbo.Shift | |
| OperationTypeCode | nvarchar(20) | No | — | SANDING, BUFFING, DEBURRING, HUMMER_SANDING |
| PartId | int | Yes | dbo.Part | FK to part master; free-text today |
| PartDescription | nvarchar(100) | Yes | — | Fallback free-text |
| CustomerId | int | Yes | dbo.Customer | Inferred from part today |
| Quantity | int | Yes | — | Pieces processed |
| TimeSpentMinutes | int | Yes | — | From tally sheet time column |
| OperatorEmployeeId | int | Yes | — | From Name field |
| IsRework | bit | No | — | True if defect-driven, False if routine |
| DefectTypeId | int | Yes | quality.DefectType | WHY it was sanded/buffed — currently not captured |
| SourceProductionRunId | int | Yes | → ProductionRun | Which run produced the defective parts |
| SourceProductionLineId | int | Yes | dbo.ProductionLine | Which line |
| NcrId | int | Yes | quality.NCR | Link to NCR if formal nonconformance |
| PassFail | bit | Yes | — | Did it pass after post-paint operation? |
| ReturnedToPostPaintOps | bit | Yes | — | Returned to buff = repeat rework |
| Comments | nvarchar(500) | Yes | — | |
| CreatedAt | datetime2 | No | — | |

**Companion summary entity `production.PostPaintDailySummary`** (from Buffing Summary 8.2.2.30):

| Field | Type | Nullable | Notes |
|---|---|---|---|
| SummaryId | int (PK) | No | |
| PlantId | int | No | RLS |
| SummaryDate | date | No | |
| OperationTypeCode | nvarchar(20) | No | BUFFING (extend to others later) |
| PartsInFromLine | int | Yes | |
| TotalPartsProcessed | int | Yes | |
| NumberOfOperators | int | Yes | |
| AveragePerPerson | decimal(6,1) | Yes | |
| AveragePerHour | decimal(6,1) | Yes | |
| TargetPerHour | decimal(6,1) | Yes | |
| EfficiencyPercent | decimal(5,2) | Yes | |
| ReturnedToOperation | int | Yes | Parts returned for re-rework |
| ReworkAfterOperation | int | Yes | Parts rejected after operation |
| FTQPercent | decimal(5,4) | Yes | |

- **Needs temporal versioning?** No — daily summaries are discrete.
- **Needs RLS?** Yes.

---

### G. Scheduling / Labor / Downtime Forms

**Forms analyzed:** 8.2.2.1.6 (101 Schedule Template), 8.2.2.1.7 (Daily Painter Schedule), 8.2.2.1.9 (Daily Down Time), 8.2.2.1.10 (Daily Painter Line Up), 8.2.2.1.11 (103 Schedule Template), 8.2.2.2.3 (102 Schedule Template), 8.2.2.28 (Downtime Tracking Template)

#### G1. Purely operational or quality-relevant data?

**Primarily operational, but three forms contain quality-relevant data:**

- **Daily Painter Schedule (8.2.2.1.7) and Daily Painter Line Up (8.2.2.1.10):** Both capture which painter is assigned to which booth on which line, along with fluid rate and air pressure settings per painter. This creates a painter→booth→parameter→date chain that is quality-relevant: if a specific booth shows recurring defects, you can trace back to the painter and their parameter settings. The Painter Schedule has sample data showing an actual lineup (Anna at blow-off, Hannah at prime with 40cc/45psi, Brandon at Booth #1 with 45cc/45psi).

- **Downtime Tracking Template (8.2.2.28):** This is a monthly downtime register with pre-defined categories per line. The categories are highly quality-relevant:
  - Training categories (Prime/Base/Clear): new painter training occupies a booth
  - Equipment issues (Prime/Base/Clear): equipment failures per stage
  - Colour change: changeover time
  - Booth feedback: paint booth environmental feedback events
  - Parts hit in blow off: incoming part handling damage
  - Flushing lines: purge time between colours/products
  - Power outage, Unknown: unplanned stoppages

  The template tracks minutes per category per day per line (Lines 101, 102, and 103 in parallel), with monthly totals and conversion to hours. This data would be critical for correlating downtime events with post-restart defects (a known paint quality failure mode).

- **Daily Down Time (8.2.2.1.9):** A simpler per-event log with: Down Time Line Off (time), Down Time Line On (time), Reason (free-text). This is the real-time capture form; the Tracking Template (8.2.2.28) is the monthly roll-up.

#### G2. Can downtime events be correlated with quality issues?

**Not currently.** The downtime forms capture time and category but have no cross-reference to quality outcomes. A line restart after "EQUIPMENT ISSUES BASE" would be a prime candidate for first-article inspection — but there's no trigger mechanism in any form. The Daily Down Time form's "Reason" field is free-text with no categorization.

The Downtime Tracking Template's categories (EQUIPMENT ISSUES PRIME/BASE/CLEAR, BOOTH FEEDBACK, PARTS HIT IN BLOW OFF) could map to quality event triggers in the digital system, but they currently exist only as monthly minute tallies.

#### G3. Is labor assignment traceable to production quality?

**Yes, for manual lines (101/103); partially for robotic line (102).**

The Daily Painter Schedule and Painter Line Up forms capture painter-to-booth assignments with parameter settings. The Schedule Templates (8.2.2.1.6, 8.2.2.1.11) have "Painter Matrix" tabs that show painter skill/certification per colour program. The 102 Operating Form captures operator name and supervisor initials.

However, this traceability is physical-form-only. There's no database of painter qualifications linked to production records. If you needed to answer "What was Brandon's FTQ when spraying Summit White in Booth #1?", you'd have to manually correlate Painter Schedule forms with quality inspection data from Part B — and even then, the inspection forms likely don't record which painter sprayed the part.

#### G4. Assessment: What flows into quality platform vs. MES/scheduling?

**Into quality platform (sf-quality):**

- Downtime event records (especially equipment failure, booth feedback, parts-hit categories) — these correlate with quality events and should link to NCR triggers
- Painter-to-booth-to-parameter assignments — needed for root cause investigation when defects are painter-dependent

**Remains in MES/scheduling system:**

- Weekly production schedules (part quantities, day assignments)
- Paint usage forecasting (8.2.2.1.6/Paint Usage tab)
- Time matrix / cycle time calculations (8.2.2.1.6/Time Matrix tab)
- Robot job queue planning (8.2.2.2.3/MasterJobRef)

**Proposed `production.DowntimeEvent` entity** (linked to both ProductionRun and optionally NCR):

| Field | Type | Nullable | FK Target | Notes |
|---|---|---|---|---|
| DowntimeEventId | int (PK) | No | — | |
| PlantId | int | No | dbo.Plant | RLS |
| ProductionLineId | int | No | dbo.ProductionLine | |
| ShiftId | int | Yes | dbo.Shift | |
| EventDate | date | No | — | |
| StartTime | time | No | — | Line off |
| EndTime | time | Yes | — | Line on |
| DurationMinutes | int | Yes | — | Calculated |
| DowntimeCategoryCode | nvarchar(30) | No | — | From 8.2.2.28 categories |
| ProcessStageCode | nvarchar(10) | Yes | — | PRIME, BASE, CLEAR, GENERAL |
| Reason | nvarchar(500) | Yes | — | Free-text detail |
| IsPlanned | bit | No | — | Colour change, training = planned |
| NcrId | int | Yes | quality.NCR | If downtime triggered quality event |
| CreatedAt | datetime2 | No | — | |

**DowntimeCategoryCode reference values** (from 8.2.2.28):

`LUNCH_BREAK`, `TRAINING`, `CATCH_UP`, `CHANGE_FILTERS`, `PRIMER_REFILL`, `BASE_REFILL`, `CLEAR_REFILL`, `EQUIPMENT_ISSUE`, `COLOUR_CHANGE`, `UNKNOWN`, `FLUSHING_LINES`, `POWER_OUTAGE`, `BOOTH_FEEDBACK`, `PAINTER_SWITCH`, `PARTS_HIT_BLOWOFF`

---

### H. Labels / Tags

**Forms analyzed:** 8.2.2.10 (Sanded-Ready For Paint), 8.2.2.11 (Finished Goods/Partial), 8.2.2.12 (Hold Tag), 8.2.2.13 (Hold For Review), 8.2.2.14 (Partial Raw), 8.2.2.15 (Rework-To Be Sanded), 8.2.2.16 (To Be Buffed), 8.2.2.22 (Use Next), 8.2.2.27 (Template), 8.2.2.2.17 (Approved Tag Tracking)

#### H1. Purely physical tags or data fields needing digital equivalents?

**Primarily physical tags with minimal data fields.** All tags share an identical template structure (the "In Process Tag" sheet at 25×14 cells). The common data fields across most tags are:

| Field | Present On | Notes |
|---|---|---|
| QUANTITY | All except Use Next and Empty | Manual write-in |
| PART DESCRIPTION | All except Use Next and Empty | Manual write-in |
| COLOUR | All except Use Next and Empty | Manual write-in |
| DATE | All except Use Next and Empty | Manual write-in |
| L/H or R/H | All except Use Next and Empty | Left-hand / Right-hand designation |

The **Hold Tag (8.2.2.12)** has three additional checkbox options at the top: **REVIEW, REJECT, REINSPECT**. This is the only tag with a disposition-like decision field. But it's still just a checkbox on a printed tag — no root cause, no NCR number, no corrective action, no cost.

The **Template (8.2.2.27)** is a blank "ATT" template — appears to be a base layout for creating new tag types. No data fields.

**Use Next (8.2.2.22)** is the simplest — just the words "USE NEXT" in large print. No data fields at all. This is a FIFO indicator, not a status tag.

#### H2. Mapping to NCR StatusCode or DispositionCode system?

| Tag | Maps To (StatusCode or DispositionCode) | Mapping Type |
|---|---|---|
| Hold Tag (8.2.2.12) — REVIEW option | StatusCode: OPEN or CONTAINED (NCR pending review) | INFERRED — Hold with review = NCR created but not yet dispositioned |
| Hold Tag (8.2.2.12) — REJECT option | DispositionCode: SCRAP or REWORK (pending decision) | INFERRED — Reject = material not acceptable, needs disposition |
| Hold Tag (8.2.2.12) — REINSPECT option | StatusCode: PENDING_VERIFICATION (needs re-inspection) | INFERRED — Reinspect = verification gate |
| Hold For Review (8.2.2.13) | StatusCode: CONTAINED (material isolated, awaiting decision) | INFERRED — Softer hold than Hold Tag |
| Rework- To Be Sanded (8.2.2.15) | DispositionCode: REWORK | High confidence — explicit rework designation |
| To Be Buffed (8.2.2.16) | DispositionCode: REWORK or BLEND | Medium — buffing could be routine or rework |
| Sanded- Ready For Paint (8.2.2.10) | DispositionCode: RECOAT or STRIP_RECOAT | INFERRED — sanded and ready for repaint cycle |
| Finished Goods/Partial (8.2.2.11) | StatusCode: N/A (inventory status, not quality status) | None — this is a shipping/WIP tag |
| Partial Raw (8.2.2.14) | StatusCode: N/A (raw material inventory) | None — incoming material identification |
| Use Next (8.2.2.22) | StatusCode: N/A (FIFO flag) | None — operational instruction only |

#### H3. Are hold tags traceable to an NCR or quality event?

**No.** No tag in the package references an NCR number, a quality event ID, or any cross-reference to a tracking system. The Hold Tag's REVIEW/REJECT/REINSPECT checkboxes represent disposition decisions, but the decision is recorded only on the physical tag. When the tag is removed (because the material was dispositioned), the decision history is lost.

The **Approved Tag Tracking form (8.2.2.2.17)** is the closest thing to a tag-to-event bridge. It records: Date, Tag #, Colour, Part Description, Quantity, and Initial. The "Tag #" field suggests a sequential numbering system for physical tags. But the form hasn't been updated since November 2018 and has no defect type, disposition code, or NCR reference. It's a register of which tags were used, not what quality events they represent.

#### H4. Tag-to-Digital Status Mapping Summary

In the digital system, these physical tags should be replaced by status transitions on the ProductionRun or NCR entity:

| Physical Tag | Digital Replacement | Entity | Status/Disposition |
|---|---|---|---|
| Hold Tag | NCR creation with hold location | quality.NCR | StatusCode = OPEN or CONTAINED |
| Hold For Review | NCR with review flag | quality.NCR | StatusCode = CONTAINED |
| Rework- To Be Sanded | NCR disposition line | quality.NcrDisposition | DispositionCode = REWORK |
| To Be Buffed | NCR disposition line or production routing | quality.NcrDisposition or production.PostPaintOperation | REWORK or routine routing |
| Sanded- Ready For Paint | NCR status update (rework complete, awaiting recoat) | quality.NCR | StatusCode = DISPOSED (rework path) |
| Finished Goods/Partial | Production status (out of scope for quality platform) | N/A | Shipping/WIP system |
| Partial Raw | Incoming material status | N/A | Receiving system |
| Use Next | FIFO queue flag | N/A | MES/scheduling |
| Approved Tag Tracking | NCR disposition audit trail | quality.NcrDisposition + workflow.StatusHistory | Gate audit trail |

---

### I. Document Control / Revision

**Forms analyzed:** 8.2.2.6 (Change Tracker), revision logs embedded in 8.2.2.4, 8.2.2.5, 8.2.2.7, 8.2.2.8, 8.2.2.9, 8.2.2.31

#### I1. Is the Change Tracker a meta-document for controlling form revisions?

**No** — it's a paint trial and shipping tracker, not a document control register.

The Change Tracker (8.2.2.6) has two active tabs:

- **Paint Trial tab:** Fields are Issue Identified, Date, Initiated By, Approved By, Start Time, End Time, Trial No, Sample Size, "Parameters Changed (List all setting, operator and system changes)". This is a paint trial log — it documents process change experiments, not document revisions.
- **Ship Request tab:** Ship to, Address, City, Date Required, Shipping Date, Part Name, Part Number, Reason for Trial. This is a sample shipping request for trial parts.

Despite its name, the "Change Tracker" tracks process changes (paint trials), not document changes. This is actually a useful quality document — paint trials are a formal change management practice — but it's mislabeled and miscategorized.

#### I2. Evidence of controlled retirement of obsolete forms?

**Limited but present.** The prompt notes Plant 2 has 207 obsolete files (significantly more than Plant 1), which were excluded from this audit package. Within the Part A forms:

- **Paint Kitchen Inventory (8.2.2.5)** retains both "Rev 7" (current) and "Rev 6" (superseded) as separate tabs in the same workbook. Rev 6 has a different structure — organized by customer program (GM Splash Guards, Cadillac, Venza, Rimowa) rather than by paint supplier. This is a controlled revision with the old version preserved for reference.
- **Monthly Booth Cleaning (8.2.2.1.4)** has a Rev Log showing 3 revisions from 2014 to 2023, with the most recent adding document number and heading name. This suggests a 2023 document control cleanup.
- **Sanding/Buffing/Deburring Tally Sheets (8.2.2.7, 8.2.2.8, 8.2.2.9)** all share an identical Rev Log with 4 revisions from 2016 to 2023. The most recent revision (07/18/23 AS) made structural changes: "Changed the specified time to manually writing the time on the sheet. Changed description to part name."
- **Hummer Sanding Tally (8.2.2.31)** has a single Rev Log entry: Created 2023-11-13 by AP.

Seven forms have revision evidence. The remaining 46 forms in Part A have no revision log, no creation date embedded (other than the file system timestamp), and no version identifier. The "Created: 05/05/17 TG" footer on the tag templates is the most common pattern — a creation stamp with initials but no formal revision history.

**Comparison to Plant 1:** Plant 2 is marginally better on document control. The presence of Rev Log tabs on 7+ forms and the preservation of Rev 6 alongside Rev 7 in the Inventory workbook shows some discipline. Plant 1 had virtually no embedded revision tracking.

#### I3. Document Control Entity Discovery

**Proposed `admin.DocumentTemplate` + `admin.DocumentRevision` entities:**

The Change Tracker (8.2.2.6) is not actually a document control tool, so this entity proposal is based on what *should* exist rather than what's captured today.

**`admin.DocumentTemplate`:**

| Field | Type | Nullable | Notes |
|---|---|---|---|
| DocumentTemplateId | int (PK) | No | |
| DocumentNumber | nvarchar(20) | No | e.g., "8.2.2.7" |
| DocumentTitle | nvarchar(200) | No | e.g., "Daily Sanding Tally Sheet" |
| Category | nvarchar(50) | No | PROCESS_CONTROL, PRODUCTION, etc. |
| PlantScope | nvarchar(20) | No | PLANT_2, ALL_PLANTS |
| LineScope | nvarchar(20) | Yes | 101-103, 102, GENERAL |
| CurrentRevisionNumber | int | No | |
| IsActive | bit | No | |
| ObsoleteDate | date | Yes | |

**`admin.DocumentRevision`:**

| Field | Type | Nullable | Notes |
|---|---|---|---|
| DocumentRevisionId | int (PK) | No | |
| DocumentTemplateId | int | No | FK → DocumentTemplate |
| RevisionNumber | int | No | |
| CreatedDate | date | Yes | |
| RevisedDate | date | Yes | |
| CreatedByInitials | nvarchar(10) | Yes | e.g., "JB", "AS", "AP" |
| RevisedByInitials | nvarchar(10) | Yes | |
| ChangeDescription | nvarchar(500) | Yes | |
| ApprovedByInitials | nvarchar(10) | Yes | |

Additionally, the paint trial function currently in the Change Tracker should map to a **`production.PaintTrial`** entity:

| Field | Type | Nullable | Notes |
|---|---|---|---|
| PaintTrialId | int (PK) | No | |
| PlantId | int | No | RLS |
| TrialNumber | nvarchar(20) | No | From Change Tracker "Trial No" |
| IssueIdentified | nvarchar(500) | No | What prompted the trial |
| InitiatedByEmployeeId | int | Yes | |
| ApprovedByEmployeeId | int | Yes | |
| TrialDate | date | No | |
| StartTime | time | Yes | |
| EndTime | time | Yes | |
| SampleSize | int | Yes | |
| ParametersChanged | nvarchar(2000) | Yes | Description of changes |
| PaintLineId | int | Yes | dbo.ProductionLine |
| PaintBatchId | int | Yes | → PaintBatch |
| ColourCode | nvarchar(50) | Yes | |
| PaintSupplierId | int | Yes | dbo.Supplier |
| Result | nvarchar(20) | Yes | PASS, FAIL, INCONCLUSIVE |
| Comments | nvarchar(2000) | Yes | |

The **Paint Trial Information Sheet (8.2.2.33)** captures additional trial detail: paint code, batch number, reducers, catalyst, P-Mix ratio, viscosity (raw/reduced), agitation time, inline filters, primer used, parts painted, reason for trial, clearcoat used, and per-booth spray settings (fluid rate, atomizing air, painter name). This is a richer version of the Change Tracker trial data and should be the primary source for the PaintTrial entity.

---

## Section 4: Critical Gap Analysis

### Gap 1: The NCR Gap

**Finding:** Zero formal NCR capability exists in Plant 2 operational forms.

| Aspect | Status | Evidence | Confidence |
|---|---|---|---|
| Formal NCR form | ABSENT | No form in the 53-file package constitutes an NCR | High |
| Defect type capture | ABSENT | Hold Tag (8.2.2.12) has REVIEW/REJECT/REINSPECT checkboxes but no defect classification | High |
| Root cause field | ABSENT | No form captures root cause data | High |
| Corrective action field | ABSENT | No form captures corrective actions | High |
| Cost capture | ABSENT | No form captures scrap or rework cost | High |
| Disposition tracking | MINIMAL | Hold Tag checkboxes imply disposition decisions; Rework/Buffed tags imply rework disposition; but no formal disposition log exists | High |
| Nonconformance register | DEFUNCT | Approved Tag Tracking (8.2.2.2.17) last updated 2018-11-30 | High |

**Mapping to existing NCR entity:** The entire NCR lifecycle (DRAFT → OPEN → CONTAINED → INVESTIGATING → DISPOSED → PENDING_VERIFICATION → CLOSED) is unsupported. The Hold Tag represents a primitive CONTAINED state. The Rework/Buffed tags represent a primitive DISPOSED state with implicit REWORK disposition. Everything between and around these states — including the all-important investigation, root cause, and verification steps — is absent.

This confirms Plant 1's finding. The NCR gap is not a Plant 2 problem; it is a **company-wide gap**. Neither plant has a formal NCR system.

---

### Gap 2: The Traceability Gap

**Finding:** Traceability chain breaks at three critical points, and two of three lines have no per-rack tracking at all.

| Chain Link | Status | Linking Key | Evidence | Confidence |
|---|---|---|---|---|
| Part → Load Record | PARTIAL | Part number (implicit, no formal FK) | 8.2.2.1.5/Load Sheet | High |
| Load → Paint Batch | BROKEN | No linking field exists | 8.2.2.1.5 vs 8.2.2.1.18 — date+line only | High |
| Load → Spray Parameters | BROKEN for 101/103; PARTIAL for 102 | Rack # (102 only) | 8.2.2.2.1, 8.2.2.2.7 vs nothing for 101/103 | High |
| Spray Parameters → Oven Cure | BROKEN | No linking field | 8.2.2.1.16 has no rack/run reference | High |
| Oven Cure → Post-Paint | BROKEN | No linking field | Tally sheets have no production reference | High |
| Post-Paint → Original Defect | BROKEN | No linking field | Tally sheets have no defect type | High |

**Line 102 partial traceability:** Date → Carrier # (8.2.2.2.4) → Starting Rack # + Base/Clear parameters (8.2.2.2.1) → Carrier # + per-stage parameters (8.2.2.2.7 Option 2). This chain works within Line 102's forms but has no upstream link to paint batch or downstream link to post-paint.

**Lines 101/103:** Only the Daily Production Report Template (8.2.2.29) and the Daily Load Sheet (8.2.2.1.5) exist. The Production Report is a monthly summary, not per-rack. There is no per-carrier tracking equivalent.

---

### Gap 3: The Process-to-Quality Linkage Gap

**Finding:** Complete disconnect. Process data and quality data exist in separate universes.

No form in the Part A package links a process deviation (temperature excursion, viscosity out-of-range, equipment failure) to a quality outcome (defect, scrap, rework, customer complaint). The 102 Operating Form SWI mentions communicating with the inspection area (Step 11) but this is a verbal instruction, not a data link.

The Downtime Tracking Template (8.2.2.28) captures equipment failure events by line and process stage — data that correlates strongly with restart defects — but has no quality event cross-reference.

The New Paint Batch Verification (8.2.2.26) is the only form with a formal pass/fail gate, but a batch failure does not trigger an NCR or hold record — it's just a standalone verification.

**Digital mapping:** `production.DowntimeEvent.NcrId` (proposed) and `production.PaintBatch.ColourVerificationId` (proposed) would close this gap. The API would need an endpoint to query NCRs by linked downtime events and paint batches.

---

### Gap 4: The Temporal Gap

**Finding:** Three forms are critically stale; document control is marginally better than Plant 1 but still weak.

| Form | Last Modified | Age (from Feb 2026) | Risk |
|---|---|---|---|
| 8.2.2.1.2 Paint Kitchen Temp Log | 2016-12-16 | 9+ years | CRITICAL — process control form unchanged since before current quality system |
| 8.2.2.1.16 Oven Verification Log | 2016-12-16 | 9+ years | CRITICAL — same |
| 8.2.2.2.17 Approved Tag Tracking | 2018-11-30 | 7+ years | HIGH — quality tracking form abandoned |
| 8.2.2.1.9 Daily Down Time | 2023-06-27 | 2.7 years | MODERATE — template may still be in use but not recently revised |
| 8.2.2.6 Change Tracker | 2023-06-27 | 2.7 years | MODERATE |

Of 53 forms: 3 are critically stale (>5 years), 10 are >2 years since modification, and 15 have been modified within the last 12 months (active maintenance). Compared to Plant 1, Plant 2 has a wider spread — some forms are very current (December 2025) while others haven't been touched in nearly a decade.

Seven forms have embedded Rev Logs vs. essentially zero in Plant 1 — a genuine improvement. However, 46 forms still lack any revision tracking.

---

### Gap 5: The Digital Readiness Gap

**Finding:** Severe structural problems block migration for most forms.

| Problem | Affected Forms | Count | Severity |
|---|---|---|---|
| Free-text where dropdowns needed | Part descriptions on Load Sheet, Paint Tally Sheet colour field, Maintenance Log reason/task, Downtime reason, Tally sheet part names | 10+ | HIGH |
| Merged cells | Tag templates (all), Paint Tally Sheet headers, Operating Form headers | 15+ | MEDIUM — tags are print-only so less concern |
| No unique identifiers | Load Sheet (no rack ID for 101/103), Tally sheets (no event ID), Maintenance records (no work order #), Paint Tally (no mix batch ID) | 12+ | CRITICAL |
| No timestamps | Load Sheet (date only, no time), Paint Tally (no time per mix), Tally sheets (time-spent but not clock time), Maintenance forms (date only) | 10+ | HIGH |
| Dual-purpose sheets | Buffing Tally has KANBAN (Spyder-specific) + generic tab; Paint Tally has two layouts; 102 Operating Form has 4 variant sheets | 4 | MEDIUM |
| Inconsistent structures across lines | 102 has 9 dedicated forms; 101/103 share 14 forms with less granularity; 101 and 103 schedule templates are structurally identical but separate files | Systemic | HIGH |
| `#REF!` errors | 101 Schedule Template Paint Usage tab — all cells show `#REF!` | 1 | HIGH — broken formulas indicate disconnected references |
| `#DIV/0!` errors | Buffing Summary — most months show `#DIV/0!` for efficiency metrics due to missing input data | 1 | HIGH — formulas exist but aren't being fed |
| Print-only layouts | All 10 tag files, Pressure Pot Label (8-up per page) | 11 | LOW for quality system (these become app-generated labels) |
| KANBAN sheet duplication | Paint Tally, Daily Down Time, Buffing Tally, Approved Tag Tracking all have identical duplicate tabs named "KANBAN SHEET" | 4 | LOW — appears to be a print variant pattern |

---

### Gap 6: The Waste-to-Production Gap

**Finding:** Waste tracking is non-functional. No volumes, no dates, no production linkage, no cost data.

The five waste "forms" are drum labels with zero data fields. The Solvent Usage Tracking form captures input consumption but not waste output. There is no way to calculate waste generation rates, waste cost per unit, or waste trends over time from any Part A form.

**Cost visibility:** ZERO. No disposal cost is captured anywhere. No waste-per-gallon-painted or waste-per-unit metric is calculable.

**Mapping:** The proposed `production.WasteRecord` entity has no current form to populate it. This data would need to be captured as a net-new digital process — there is no paper form to digitize.

---

### Gap 7: The Post-Paint Traceability Gap

**Finding:** Post-paint operations are an accountability black hole, as suspected. No backward traceability to defect, production run, or root cause.

Tally sheets capture operator, part name, quantity, and time — all labor-tracking fields. The critical quality fields are missing: why was this part sanded? Which line produced it? Which rack? Which paint batch? What was the defect?

The Buffing Summary (8.2.2.30) has aggregate quality metrics (FTQ, return-to-buff rate) but the input data isn't being populated ("Into Buff from Line" shows zero across most months). The formulas are designed for quality analysis but the operators aren't filling in the quality-relevant fields.

**This is a measurement system failure, not a form design failure.** The Buffing Summary template is actually well-designed — it just isn't being used as intended.

---

### Gap 8: The Cost Visibility Gap

**Finding:** Near-zero cost visibility from operational forms.

| Cost Type | Captured? | Source | Calculable? |
|---|---|---|---|
| Scrap cost | No | No form captures scrap quantities or values | No |
| Rework cost | No | Tally sheets capture rework labour hours but no cost rate | PARTIAL — could estimate if labour rates were applied to tally sheet hours |
| Waste disposal cost | No | No disposal cost on any form | No |
| Paint material cost | Yes | Paint Kitchen Inventory (8.2.2.5) has "Cost per UM-CAD" and "Total value CAD" | Yes — inventory value calculable |
| Downtime cost | No | Downtime minutes captured but no cost-per-minute rate | PARTIAL — could estimate with line rate |
| Paint consumption cost | Partial | Paint Tally captures gallons consumed; Inventory has unit costs | PARTIAL — could join consumption × cost |

The Paint Kitchen Inventory (8.2.2.5) is the only form with actual cost data. It includes per-unit CAD costs for each paint product (e.g., Sierra Black at $130.13/unit, Summit White at $160.96/unit, BMW Black II at $72.80/unit). Combined with the Paint Tally Sheet's consumption data, you could estimate daily paint material costs. But no form does this calculation, and the data lives in separate files with no linking mechanism.

**Mapping:** `quality.NcrCostLedger` exists in the database with cost line items per NCR. None of the operational forms feed this entity. Until NCRs exist, there's no cost accumulation mechanism.

---

## Batch Metadata

| Field | Value |
|---|---|
| **BATCH_ID** | A3 |
| **COMPLETED_SECTIONS** | Section 3 subsections E (Waste), F (Post-Paint Ops), G (Scheduling/Labor/Downtime), H (Labels/Tags), I (Document Control/Revision); Section 4 (Critical Gap Analysis — all 8 gaps) |
| **NEXT_BATCH_STARTS_WITH** | Section 5: Platform Impact Assessment — A. Database Impact |
