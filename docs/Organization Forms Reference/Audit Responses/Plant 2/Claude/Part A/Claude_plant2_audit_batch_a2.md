# BATCH A2: Section 3 (Detailed Analysis) — Subsections A through D

## Section 3: Detailed Analysis by Category

---

### A. PRODUCTION TRACKING FORMS

**Forms analyzed:** 8.2.2.1.5 (Daily Load Sheet), 8.2.2.2.1 (102 Production Tracking), 8.2.2.2.4 (102 Loaded Parts Tracking), 8.2.2.29 (Daily Production Report Template), 8.2.2.1.18 (Daily Paint Tally Sheet — production-relevant fields)

#### A1. Can you trace a specific part from loading → coating parameters → unload?

**No.** The chain breaks in at least three places.

**Break 1 — Load Sheet to Production Tracking:** The Daily Load Sheet (8.2.2.1.5) is organized by customer section (Laval Tool, Tesla, KB Components, Metelix) with raw part numbers and part descriptions, plus columns for "Raw" and "RW" (rework) quantities. But it has no rack/carrier ID, no timestamp for when racks entered the line, and no line assignment. The header has fields for Date, Line, and Operator — but these are manually written on a printed copy. The load sheet tells you what was available to paint on a given day, not what actually went through the line in what order.

The 102 Line Paint Production Tracking (8.2.2.2.1) does have a "Starting Rack #" column — this is the closest thing to a traceability link. It also captures start/end times, base coat and clear coat spray parameters (Fluid PSI, Atomizing PSI, Fan PSI, 15-sec cup test, fan check, rack visual check, catalyst check). But there's no corresponding field on the Load Sheet to cross-reference. The rack number exists only on the Line 102 form.

The 102 Line Loaded Parts Tracking (8.2.2.2.4) adds Part Description, Carrier #, Molding Date, Quantity Loaded, and Initials — this is a tighter link but again only exists for Line 102.

Lines 101 and 103 have no production tracking form equivalent. The Daily Production Report Template (8.2.2.29) has sheets for "#101 JANUARY 2024" and "#103 JANUARY 2024" with columns: DATE, PART, COLOUR, BOOTH, PAINTER, FLUID RATE, AIR PRESSURE, TEMP, HUMIDITY, FIRST-OFF TIME, LAST-OFF TIME, SUPPLIER, NOTES (PROCESS), NOTES (RESULTS), FTQ %, TOTAL DOWNTIME. This is a monthly summary — one row per production run — not a per-rack tracker. It's the only production data source for Lines 101/103 and it's a template with zero populated data.

**Break 2 — Production Tracking to Paint Batch:** The Production Tracking form (8.2.2.2.1) captures spray parameters but does not reference a paint batch number or mix record. The Daily Paint Tally Sheet (8.2.2.1.18) captures batch numbers, viscosity, and solvent amounts — but is filed separately with no production run cross-reference. The Paint Tally Sheet records Date, Line, and Painter Mixer but no rack number or time window. To correlate a specific rack's quality issues with the paint batch, you'd need to manually match dates and lines across two separate forms.

**Break 3 — Production to Post-Paint:** The sanding, buffing, and deburring tally sheets (covered in Section F) record part name and quantity only. No rack number, no production date, no line, no defect code. There is zero backward traceability from a sanded/buffed part to its original production run.

> **Evidence:** 8.2.2.1.5/Load Sheet, 8.2.2.2.1/Line Paint Production Tracking, 8.2.2.2.4/Line Paint Production Tracking, 8.2.2.29/#101 JANUARY 2024 | **Confidence:** High

#### A2. Consistent identifier tying load sheet to production record?

**No consistent identifier exists across lines.** Line 102 uses "Starting Rack #" (8.2.2.2.1) and "Carrier #" (8.2.2.2.4), but these are not referenced on the shared Load Sheet (8.2.2.1.5) or in the 101/103 Production Report (8.2.2.29). There is no universal rack ID, load bar number, or batch identifier that threads through all forms.

The 102 Operating Form (8.2.2.2.7, Option 2 sheet) uses "Carrier #" in its production data section — this appears to be the same identifier as 8.2.2.2.4. But Line 102 is the only line with this level of granularity.

#### A3. Are quantities tracked at load? Can you calculate throughput?

**Partially.** The Load Sheet (8.2.2.1.5) has "Raw" and "RW" columns per customer/part, presumably for quantity counts. The 102 Loaded Parts Tracking (8.2.2.2.4) has an explicit "Quantity Loaded" field. The Buffing Summary (8.2.2.30) tracks "Ttl Buffed" daily with efficiency calculations.

However, there's no "Quantity Painted" or "Quantity Good" field on any production tracking form. The Daily Production Report (8.2.2.29) has "FTQ %" but no raw quantity basis. You could estimate throughput from the Buffing Summary's daily totals (323–855 parts/day in January 2024 data), but this only counts parts that reach the buffing stage. Throughput from loading through paint is not directly calculable.

#### A4. How do tally sheets tie back to paint production records?

**They don't.** The Daily Sanding Tally Sheet (8.2.2.7) captures: Time Spent, Part #/Description, Qty Sanded. The Daily Buffing Tally Sheet (8.2.2.8) captures: Time Spent, Part #/Description, Qty Buffed. The Daily Deburring Tally Sheet (8.2.2.9) captures: Part Name, TIME (two time-block columns). The Daily Hummer Sanding Tally Sheet (8.2.2.31) captures: Time (hourly blocks 6:30–3:00), Running Tally, Total per Hour.

None of these forms have fields for: line number, production date (only the tally sheet's own date), rack/carrier #, defect type, or paint batch. The tally sheets are labor-tracking documents — they tell you how many parts each person sanded/buffed, not why those parts needed rework.

The Buffing Tally Sheet's KANBAN tab is slightly different — it pre-lists specific Spyder part names (LH Low Fairing, RH Low Fairing, Front Fascia, Hood, etc.) with AM/PM quantity columns. This is part-specific counting, but still disconnected from production data.

#### A5. Production Run Entity Discovery

Based on the forms analyzed, a `ProductionRun` / `LoadRecord` entity needs to capture two distinct levels:

**Level 1 — Daily Line Assignment** (from Load Sheet + Production Report):

- Date, PlantId, ProductionLineId (101/102/103), ShiftId
- CustomerId, PartId, ColourCode
- QuantityLoaded, QuantityRework
- PainterId (from Painter Schedule/Lineup)
- BoothAssignment

**Level 2 — Per-Rack/Carrier Tracking** (from 102 Production Tracking + Operating Form):

- CarrierId / RackNumber (string, free-text today)
- StartTime, EndTime
- PaintBatchRef (FK → PaintBatch, currently not captured)
- BaseCoat parameters: FluidPSI, AtomizingPSI, FanPSI, CupTestResult, FanCheck (pass/fail), RackVisualCheck (pass/fail)
- ClearCoat parameters: same field set + CatalystCheck (pass/fail)
- Temperature (°F), Humidity (%), BoothTemp
- IsRework (boolean)
- RollerInitials (operator who loaded rack)
- SupervisorInitials

**Comparison to Plant 1:** Plant 1 had a similarly broken load-to-production chain. The fundamental pattern is identical — load sheets exist as part reference documents, not transactional records. Plant 2's Line 102 forms are more advanced than anything in Plant 1, with actual per-carrier parameter capture, but this sophistication doesn't extend to Lines 101/103.

---

### B. PROCESS CONTROL FORMS

**Forms analyzed:** 8.2.2.1.2 (Paint Kitchen Temp Log), 8.2.2.1.16 (Oven Verification Log), 8.2.2.2.7 (102 Line Operating Form), 8.2.2.2.6 (Line 102 Programs), 8.2.2.33 (Paint Trial Information Sheet)

#### B1. Are process parameters being recorded or just checked off?

**Mixed — mostly check-off, with one significant exception.**

**Check-off forms:**

- **Oven Verification Log (8.2.2.1.16):** Three columns — Date, Oven Setting, Initial. That's it. No actual temperature reading, no profile data, no upper/lower spec limits. This is verification that someone looked at the oven, not that the oven was within specification. File is from December 2016.
- **Paint Kitchen Temp Log (8.2.2.1.2):** Date/Time, TEMPERATURE, Initial, Line Speed. Marginally better — it records an actual temperature value — but no target range, no reaction plan for excursions. Also from December 2016.

**The exception — 102 Line Operating Form (8.2.2.2.7):** This macro-enabled workbook is the most sophisticated process control document in either plant audit. It has four sheets:

1. **Sheet1 (SWI):** 11-step standardized work instruction for robot spray operators. Steps include: verify pot room supplies, confirm viscosity via cookbook, verify gun assembly, program parameters and conduct cup test with supervisor sign-off, verify rack condition, observe fan pattern. This is a real SWI that references actual quality checkpoints.

2. **Option 1:** Floor Supervisor - Initiate & Manage Shift Report. Captures 6 colour/program slots with Value, Operator Initials, Supervisor Initials per task (solvent fill, base fill, clear fill). This is a basic check-off.

3. **Option 2 (best form in both plant audits):** "Line 102 Application Tracker." Captures:
   - **Header:** Name, Date, Program, Colour, Temp/Humidity at start and end, Booth Temp at start and end
   - **18-item checklist with actual values** (not just pass/fail): solvent amount added, base+hardener amount, clear+hardener amount, viscosity reading, gun assembly verification, fan test, robot bag check, rack visual checks at basecoat and clearcoat, queue job verification, ml/15sec or cc/min at base and clear, fan pattern observation, flash time, vestibule part check
   - **Per-carrier production data:** Carrier #, Time, Temp/Humidity, RW Y/N, Roller Initial, then per-stage (Primer, Base, Clear): Fluid, Atom, Fan, flow rate (ml/15sec or cc/min), Comments

4. **Sheet2:** A condensed variant of Option 2 with the same structure but fewer columns.

> **Evidence:** 8.2.2.1.16/Line 101 103, 8.2.2.1.2/Sheet1, 8.2.2.2.7/Option 2 | **Confidence:** High

#### B2. Linkage between process deviations and quality outcomes?

**Zero linkage.** No process control form references an NCR, quality event, defect code, or customer complaint. Step 18 of the 102 Operating Form's checklist is "Start Up Approved" — implying a go/no-go gate — but there's no documented reaction plan for what happens when parameters fail. Step 11 of the SWI says "Continue with production run and communicate with inspection area for any repeated application defects" — this is the closest thing to a process-to-quality bridge, but it's a verbal instruction, not a data linkage.

#### B3. Reaction plans for out-of-spec conditions?

**Minimal.** The 102 Operating Form SWI (Sheet1, Step 10) states: "If there is a deviation from the supplied parameters, obtain supervisor approval to make the change and continue painting." This is a procedure but not a formal reaction plan — no severity thresholds, no escalation matrix, no hold-for-inspection trigger.

The New Paint Batch Verification (8.2.2.26) has pass/fail criteria for colour: "ΔEcmc < 2" for solids, "ΔL, Δa, Δb < 1.15 and ΔEcmc < 2" for metallics, with "Visual assessment will always override numerical measurement data." This is a genuine reaction plan with quantified spec limits, but it only covers incoming paint colour verification, not in-process parameters.

No other form in the Part A package contains reaction plans.

#### B4. Robotic spray parameters and Line 102 Programs

The Line 102 Programs form (8.2.2.2.6) is a reference table mapping customer programs to robot job numbers, colour valves, and presets. Structure for Mytox section:

| Base Job | Colour Valve | Presets | Colour | Clear Job | Clear Valve | Clear Desc | Clear Presets |
|----------|-------------|---------|--------|-----------|-------------|------------|---------------|
| 3 | 1 | 0.5 Short | — | — | — | — | — |
| 3 | 3 | 1 | 0.5 Long | — | — | — | — |
| 5 | 1 | 0.5 | White Short | 3 | 3 | White Midcoat Short | 0.5 |
| 5 | 1 | 0.5 | White Long | 3 | 3 | 3 White Midcoat Long | 0.5 |

This is a recipe/configuration document — it defines what job numbers correspond to what programs. The 102 Operating Form (Option 2) then verifies "Are all the right JOB(s) in Basecoat Queue?" and "Are all the right JOB(s) in Clearcoat Queue?" as checklist items. The Schedule Template (8.2.2.2.3) MasterJobRef sheet contains the full cross-reference of part codes to job numbers per colour — 60 rows covering all part/colour combinations.

This is actually a reasonable setup for recipe management — the problem is it exists only for Line 102 and only in spreadsheet form.

#### B5. Process Parameter Discovery

Distinct process parameters being monitored across all Part A forms:

| Parameter | Unit | Spec Limits Documented? | Form Source | Line Scope |
|-----------|------|------------------------|-------------|------------|
| Oven temperature (setting) | °F | No | 8.2.2.1.16 | 101/103 |
| Paint kitchen temperature | °F | No | 8.2.2.1.2 | All |
| Line speed | UNKNOWN | No | 8.2.2.1.2 | All |
| Paint raw viscosity | UNKNOWN (cup seconds?) | No | 8.2.2.1.18 | All |
| Paint reduced viscosity | UNKNOWN | No | 8.2.2.1.18 | All |
| Booth temperature | °F | No | 8.2.2.2.7/Option 2 | 102 |
| Ambient temperature | °F | No | 8.2.2.2.7/Option 2, 8.2.2.29 | 102, 101/103 |
| Ambient humidity | % | No | 8.2.2.2.7/Option 2, 8.2.2.29 | 102, 101/103 |
| Fluid pressure/rate — Base | PSI or ml/15sec or cc/min | No | 8.2.2.2.1, 8.2.2.2.7, 8.2.2.29 | 102, 101/103 |
| Atomizing pressure — Base | PSI | No | 8.2.2.2.1, 8.2.2.2.7 | 102 |
| Fan pressure — Base | PSI | No | 8.2.2.2.1, 8.2.2.2.7 | 102 |
| 15-sec cup test — Base | ml/15sec | No | 8.2.2.2.1 | 102 |
| Fluid pressure/rate — Clear | PSI or ml/15sec or cc/min | No | 8.2.2.2.1, 8.2.2.2.7 | 102 |
| Atomizing pressure — Clear | PSI | No | 8.2.2.2.1, 8.2.2.2.7 | 102 |
| Fan pressure — Clear | PSI | No | 8.2.2.2.1, 8.2.2.2.7 | 102 |
| 15-sec cup test — Clear | ml/15sec | No | 8.2.2.2.1 | 102 |
| Catalyst check | Pass/Fail | No | 8.2.2.2.1 | 102 |
| Flash time | minutes | No | 8.2.2.2.7/Option 2 | 102 |
| Fan check (visual) | Pass/Fail | No | 8.2.2.2.1, 8.2.2.2.7 | 102 |
| Rack visual check | Pass/Fail | No | 8.2.2.2.1, 8.2.2.2.7 | 102 |
| E-stats on/off | UNKNOWN | No | 8.2.2.2.7/SWI Step 6 | 102 |
| Paint agitation time | minutes | No | 8.2.2.1.18 | All |
| Raw paint temperature | °F | No | 8.2.2.1.18 | All |
| Straining filter size | UNKNOWN | No | 8.2.2.1.18 | All |
| Inline filter size | UNKNOWN | No | 8.2.2.1.18, 8.2.2.23 | All |
| P-Mix ratio | ratio | No | 8.2.2.23, 8.2.2.24 | All |
| Robot job number | integer | N/A (reference) | 8.2.2.2.6, 8.2.2.2.3 | 102 |
| Colour ΔEcmc | number | **Yes (<2)** | 8.2.2.26 | All |
| Colour ΔL, Δa, Δb | number | **Yes (<1.15 metallics)** | 8.2.2.26 | All |
| Air pressure (general) | PSI | No | 8.2.2.1.7, 8.2.2.1.10, 8.2.2.29 | 101/103 |
| Paint pressure at P-Mix | PSI | No (reference: 60 PSI) | 8.2.2.1.10 | All |

> **Critical finding:** Only **ONE** parameter in the entire Part A package has documented specification limits — colour verification (ΔEcmc < 2). Every spray parameter, every temperature, every viscosity reading is collected without a target or tolerance band. This means there is no systematic way to determine if a process was "in control" or not. CQI-12 Section 8 (Process Control) would flag this as a major nonconformance.

**Comparison to Plant 1:** Plant 1 had bath chemistry parameters with some spec limits (pH, conductivity targets on lab forms). Plant 2 has more parameters being captured (spray pressures, cup tests, humidity, booth temps) but fewer documented limits. Plant 2 is collecting more data points but with less analytical structure.

---

### C. PAINT MIX / CHEMISTRY FORMS

**Forms analyzed:** 8.2.2.1.18 (Daily Paint Tally Sheet), 8.2.2.5 (Paint Kitchen Inventory), 8.2.2.23 (Paint Mix Information Sheet), 8.2.2.24 (Pressure Pot Label), 8.2.2.25 (Solvent Usage Tracking), 8.2.2.26 (New Paint Batch Verification)

#### C1. Can a defect be traced back to a specific paint batch?

**Not reliably.** The path exists in theory but breaks in practice.

The Daily Paint Tally Sheet (8.2.2.1.18) captures Batch # per paint colour mixed. The header captures Date, Painter Mixer, and Line. If you knew the date and line of a defective part, you could look up the Paint Tally Sheet and find which batch(es) were used that day. But:

- Multiple batches can be mixed in one day (12 line items per form)
- No time stamps per mix — just numbered rows 1–12
- No cross-reference to which rack or carrier received which batch
- The Production Tracking form (8.2.2.2.1) doesn't reference a batch number

The Pressure Pot Label (8.2.2.24) is printed and attached to the physical pot with: Pot #, Date, Colour, Mixing Info, Viscosity, Inline Filter, P-Mix Ratio. This label creates a physical-to-batch link at the pot level, but it's a printed label with no digital trace. Multiple labels are printed per page (8 per page layout), clearly designed for high-volume printing and physical attachment.

**Net assessment:** You could reconstruct batch traceability after the fact by correlating dates and lines across multiple forms. You could not do it in real time, and the reconstruction would be uncertain when multiple batches of the same colour were mixed on the same day.

#### C2. Specification limits (viscosity, mix ratios, pot life)?

**Viscosity:** The Paint Tally Sheet captures "Raw Viscosity" and "Reduced Viscosity" but documents no target values. The Paint Mix Information Sheet (8.2.2.23) captures "Viscosity: Raw ___ / Reduced ___" — again no targets on the form itself. The 102 Operating Form checklist asks "What is the paint viscosity?" as an open-ended question with no pass/fail threshold. The SWI references "using the cook book" to confirm mixing — this implies external specification documents exist but are not embedded in the forms.

**Mix ratios:** The Paint Mix Information Sheet (8.2.2.23) has a "P-Mix Ratio" field, and the Pressure Pot Label (8.2.2.24) repeats it. No target ratio is documented on either form.

**Pot life:** Not tracked anywhere in the Part A form set. No pot life timer, no mix-to-use time limit, no expiration flag.

**Colour verification (the exception):** The New Paint Batch Verification (8.2.2.26) has explicit acceptance criteria: ΔEcmc < 2 for solids, ΔL/Δa/Δb < 1.15 and ΔEcmc < 2 for metallics. It captures master plaque readings vs supplier batch panel readings at 25°/45°/75° angles, plus first and second spray-out readings. This is genuinely rigorous — approaching OEM lab-grade incoming inspection.

#### C3. Is solvent tracking regulatory-only or process control?

**Primarily regulatory, with some process intelligence baked in.**

The Solvent Usage Tracking form (8.2.2.25) is organized by product type:

- **Primers section:** Ad Pro (US Paint), Low Gloss Conductive Grey (Red Spot), Anti Chip (NPAA), Ad Pro (Red Spot) — with columns: Supplier, Amount Raw, Total Consumption, Batch, Reducer, Same Drum, New Drum
- **Solvents section:** MEK, MAK, Xylene, IBA, SC150, Alcohol, Virgin Purge — all from UNIVAR — with columns: Supplier, Total Consumption, Batch, Same Drum, New Drum

The "Same Drum / New Drum" tracking is a container-level inventory control — useful for regulatory reporting (total solvent consumed per period) and for detecting unusual consumption spikes. But there's no per-production-run allocation. You can't calculate "gallons of MEK per 100 parts painted" from this form because there's no production volume denominator.

#### C4. How does the Pressure Pot Label relate to batch/lot traceability?

The Pressure Pot Label (8.2.2.24) is a physical label — printed 8-up per page — that gets attached to a pressure pot. Fields: Pot #, Date, Colour, Mixing Info, Viscosity, Inline Filter, P-Mix Ratio. It bridges the paint kitchen (where paint is mixed) to the spray booth (where paint is applied) by physically identifying which pot contains which mix.

In the digital system, this maps to a junction between PaintBatch and Equipment (pressure pot as spray-line equipment). The label's data is a subset of the Paint Mix Information Sheet — it's a portable reference copy of the mix record.

#### C5. PaintMix / PaintBatch Entity Discovery

The liquid paint equivalent of Plant 1's bath chemistry is fundamentally different in structure. E-coat is a continuous bath with periodic sampling; liquid paint is a batch process — discrete mixes prepared, consumed, and replaced.

**Proposed `production.PaintBatch` entity:**

| Field | Type | Nullable | FK Target | Notes |
|-------|------|----------|-----------|-------|
| PaintBatchId | int (PK) | No | — | Auto-increment |
| PlantId | int | No | dbo.Plant | RLS scope |
| ProductionLineId | int | Yes | dbo.ProductionLine | Which line consumed this batch |
| BatchDate | date | No | — | From Paint Tally Sheet date |
| SequenceNumber | smallint | No | — | 1–12 per day (from tally row) |
| PaintColourCode | nvarchar(50) | No | — | Free-text today; needs lookup |
| PaintSupplierId | int | Yes | dbo.Supplier | NB Coatings, BASF, Red Spot, US Paint |
| PaintProductCode | nvarchar(50) | Yes | — | Supplier product code |
| SupplierBatchNumber | nvarchar(50) | Yes | — | From Paint Tally Sheet "Batch #" |
| RawPaintQuantityGal | decimal(8,2) | Yes | — | Gallons raw paint |
| AgitationTimeMins | smallint | Yes | — | Minutes |
| RawPaintTempF | decimal(5,1) | Yes | — | °F |
| RawViscosity | decimal(6,2) | Yes | — | Units TBD (cup seconds?) |
| SolventType | nvarchar(50) | Yes | — | From tally "Solvent Used" |
| SolventAmountPerHalfPail | decimal(6,2) | Yes | — | Needs unit clarification |
| ReducedViscosity | decimal(6,2) | Yes | — | After reduction |
| TotalPaintConsumptionGal | decimal(8,2) | Yes | — | Total consumed |
| StrainingFilterSize | nvarchar(20) | Yes | — | Filter size |
| InlineFilterSize | nvarchar(20) | Yes | — | Filter size |
| PMixRatio | nvarchar(20) | Yes | — | e.g., "4:1:1" |
| CatalystType | nvarchar(50) | Yes | — | From Paint Mix Info Sheet |
| ReducerType | nvarchar(50) | Yes | — | From Paint Mix Info Sheet |
| PotNumber | nvarchar(10) | Yes | — | From Pressure Pot Label |
| MixedByEmployeeId | int | Yes | — | Painter Mixer initials |
| VerifiedByEmployeeId | int | Yes | — | Supervisor verification |
| ColourVerificationId | int | Yes | → ColourVerification | FK to batch verification record |
| CreatedAt | datetime2 | No | — | System timestamp |

**Proposed `production.ColourVerification` entity** (from 8.2.2.26):

| Field | Type | Nullable | Notes |
|-------|------|----------|-------|
| ColourVerificationId | int (PK) | No | — |
| PaintBatchId | int | Yes | FK → PaintBatch |
| PaintSupplier | nvarchar(50) | No | — |
| ColourName | nvarchar(50) | No | — |
| PaintCode | nvarchar(50) | No | — |
| SupplierBatchNumber | nvarchar(50) | No | — |
| VerificationDate | date | No | — |
| Viscosity | decimal(6,2) | Yes | — |
| MasterL_25 / MasterA_25 / MasterB_25 | decimal(6,3) | Yes | Master plaque readings at 25° |
| MasterL_45 / MasterA_45 / MasterB_45 | decimal(6,3) | Yes | At 45° |
| MasterL_75 / MasterA_75 / MasterB_75 | decimal(6,3) | Yes | At 75° |
| BatchL_25 / BatchA_25 / BatchB_25 | decimal(6,3) | Yes | Supplier panel readings |
| *(same pattern for 45° and 75°)* | | | |
| DeltaEcmc_25 / _45 / _75 | decimal(6,3) | Yes | Calculated |
| SprayOut1_L/a/b/DeltaEcmc at 25/45/75 | decimal(6,3) | Yes | First spray out |
| SprayOut2_L/a/b/DeltaEcmc at 25/45/75 | decimal(6,3) | Yes | Second spray out |
| PassFail | bit | No | — |
| ApprovedByEmployeeId | int | Yes | — |
| Comments | nvarchar(500) | Yes | — |

**Needs temporal versioning?** No — each batch is a discrete event, not a continuously updated record.

**Needs RLS?** Yes — plant-scoped.

---

### D. MAINTENANCE / PM FORMS

**Forms analyzed:** 8.2.2.1.1 (Rack Burn Off Tracker), 8.2.2.1.3 (Daily Booth Cleaning), 8.2.2.1.4 (Monthly Booth Cleaning), 8.2.2.1.19 (103 Pot Cleaning Chart), 8.2.2.1.20 (101 Pot Cleaning Chart), 8.2.2.2.8 (Robot Operator Maintenance), 8.2.2.2.9 (102 TPM Checklist), 8.2.2.2.10 (102 Maintenance Log), 8.2.2.32 (Dustless Sander Maintenance), 8.2.2.34 (Sanding Booth Cleaning)

#### D1. Are maintenance activities tracked with enough detail to correlate with quality events?

**No.** Maintenance forms are almost exclusively check-off / initial-box documents. None reference NCRs, defect events, or quality outcomes.

The 102 Maintenance Log (8.2.2.2.10) is the most promising — it has four columns: Date, Task, Reason, Comments — with a dropdown-ready task list on Sheet2 (Robot Dress, P-Mix Base, P-Mix Clear, Floor Filters, Floor Grates, Ceiling Filters, Vestibule Filters, Oven Filters, Vestibule Mop, Booth Walls, Booth Conveyor, Booth Lights, plus 15 more items). This is structured enough to build on. But "Reason" is a free-text field with no categorization, and 200 rows suggests this is meant for extended use without analysis.

All other maintenance forms are binary check-off grids — "initial box when complete" per task per day/week.

#### D2. Preventive vs. reactive distinction?

**Implicitly preventive only.** The forms are all structured as scheduled activities:

- **Daily:** booth cleaning, sander maintenance, robot dressing, floor filters
- **Weekly:** rack burn-off tracking (52-week calendar)
- **Monthly:** deep cleaning (P-Mix systems, washer, oven), filter swap-out

The 102 Maintenance Log could capture reactive maintenance (the "Reason" column allows it), but there's no flag distinguishing planned vs. unplanned, and no downtime duration or cost field.

None of the maintenance forms link to downtime tracking. If a robot goes down and requires unplanned maintenance, that event would appear on the Daily Down Time form (8.2.2.1.9) as a "Reason" entry but not on any maintenance form.

#### D3. Are records tied to specific equipment?

**Partially.**

- **Rack Burn Off Tracker (8.2.2.1.1):** Rows are specific rack names (LH F3T Low Fairing, RH Fairing, etc.) tracked across 52 weeks. This is equipment-specific.
- **Booth Cleaning (8.2.2.1.3):** Columns are "First Booth, Second Booth, Third Booth, Fourth Booth, Primer, Flash Tunnel" — positional but not named. No equipment ID.
- **Pot Cleaning Charts (8.2.2.1.19, 8.2.2.1.20):** Line-specific (103 and 101 respectively), with columns for P-Mix Cleaning (Clear, Base), Counters. Six date/initial column pairs per sheet.
- **Robot Maintenance (8.2.2.2.8):** Line 102-specific, but tasks are generic (dress robot, clean P-Mix, pails empty, floor filters).
- **TPM Checklist (8.2.2.2.9):** Line 102-specific. Items: Check Air Cap, Check Fluid Nozzle, Check Electrode — references specific robot spray components.
- **Sander Maintenance (8.2.2.32):** Per-sander tracking (Sander 1–6). Equipment-specific.
- **Sanding Booth (8.2.2.34):** Booth-level daily/monthly tracking.

Equipment ID is implicit via form title/line number, never via an explicit equipment reference number or asset tag.

#### D4. Macro-enabled Operating Form vs. maintenance

The 102 Line Operating Form (8.2.2.2.7) is primarily a process control and production tracking document, not a maintenance form. Its SWI references maintenance-adjacent tasks (verify gun assembly, dress robot, check pot room supplies) but these are start-of-shift verification steps, not maintenance records. The actual maintenance record for these activities lives in the Robot Operator Maintenance form (8.2.2.2.8) and TPM Checklist (8.2.2.2.9).

**The relationship:** the SWI tells you to do the checks. The TPM/maintenance forms record that you did them. There's no digital link between the two.

#### D5. Maintenance Entity Discovery

**Proposed `production.MaintenanceRecord` entity:**

| Field | Type | Nullable | FK Target | Notes |
|-------|------|----------|-----------|-------|
| MaintenanceRecordId | int (PK) | No | — | |
| PlantId | int | No | dbo.Plant | RLS |
| ProductionLineId | int | Yes | dbo.ProductionLine | |
| EquipmentId | int | Yes | dbo.Equipment | Booth, robot, sander, oven, P-Mix |
| MaintenanceDate | date | No | — | |
| MaintenanceTypeCode | nvarchar(20) | No | — | DAILY, WEEKLY, MONTHLY, UNPLANNED |
| TaskCode | nvarchar(50) | No | — | From 102 Maintenance Log dropdown list |
| IsCompleted | bit | No | — | |
| Reason | nvarchar(500) | Yes | — | For unplanned / reactive |
| CompletedByEmployeeId | int | Yes | — | |
| VerifiedByEmployeeId | int | Yes | — | Supervisor/manager initial |
| DurationMinutes | int | Yes | — | Not currently captured but needed |
| Comments | nvarchar(500) | Yes | — | |
| NcrId | int | Yes | quality.NCR | Link to quality event if applicable |
| DowntimeEventId | int | Yes | → DowntimeEvent | Link if maintenance caused downtime |
| CreatedAt | datetime2 | No | — | |

**Reference data needed:** Equipment entries for Plant 2's paint booths (Booth 1–4, Primer booth per line), ovens (per line), robots (Line 102 basecoat/clearcoat), P-Mix systems (base/clear per line), sanders (1–6), sanding booth.

**Needs temporal versioning?** No — discrete events.

**Needs RLS?** Yes — plant-scoped.
