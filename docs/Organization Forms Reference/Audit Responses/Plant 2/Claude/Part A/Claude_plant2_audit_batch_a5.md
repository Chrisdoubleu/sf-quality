# BATCH A5: Appendix A + Appendix B + Appendix C

---

## Appendix A: Defect Taxonomy Mapping Table (Partial — Operational Defects Only)

As noted in Section A3, Part A operational forms contain very few explicit defect references. This table captures everything discoverable from Part A; Part B customer inspection forms will be the primary source.

### Defect Mapping Table

| Form Defect Name | Proposed Parent Code (L1) | Proposed Parent Name (L1) | Proposed Defect Code (L2) | Proposed Defect Name (L2) | Line Type Code | Default Severity Id (1–10) | Sort Order Hint | Notes |
|---|---|---|---|---|---|---|---|---|
| Fan pattern break | APP | Application Defects | FAN_BREAK | Fan Pattern Break | LIQUID | 5 (INFERRED) | 10 | 8.2.2.2.7/Option 2 item 14: "Observe fan during application, was there any breaks?" |
| Part damage at blow-off | HAND | Handling Defects | PART_DMG_BLOWOFF | Part Damage at Blow-Off | LIQUID | 4 (INFERRED) | 20 | 8.2.2.28 downtime category: "PARTS HIT IN BLOW OFF" |
| Booth environmental feedback | ENV | Environmental Defects | BOOTH_FEEDBACK | Booth Environmental Feedback | LIQUID | 6 (INFERRED) | 30 | 8.2.2.28 downtime category: "BOOTH FEEDBACK" |
| Colour out of tolerance | COLOUR | Colour Defects | COLOUR_OOT | Colour Out of Tolerance | LIQUID | 7 (INFERRED) | 40 | 8.2.2.26: ΔEcmc > 2 or ΔL/Δa/Δb > 1.15 for metallics |
| Viscosity out of tolerance | MIX | Paint Mix Defects | VISC_OOT | Viscosity Out of Tolerance | LIQUID | 5 (INFERRED) | 50 | Inferred from 8.2.2.1.18 viscosity capture fields and 8.2.2.2.7 SWI Step 2 viscosity check |
| Catalyst issue | MIX | Paint Mix Defects | CATALYST_ISSUE | Catalyst Check Failure | LIQUID | 7 (INFERRED) | 60 | 8.2.2.2.1: "Catalyst Check" column implies this is a monitored failure mode |
| Rack visual check failure | HAND | Handling Defects | RACK_VISUAL_FAIL | Rack Condition Failure | LIQUID | 3 (INFERRED) | 70 | 8.2.2.2.1, 8.2.2.2.7: "Rack Visual Check" column — contamination, damaged racking, improper loading |
| Equipment issue — primer | EQUIP | Equipment Defects | EQUIP_PRIME | Equipment Issue — Primer Stage | LIQUID | 6 (INFERRED) | 80 | 8.2.2.28: "EQUIPMENT ISSUES PRIME" |
| Equipment issue — base | EQUIP | Equipment Defects | EQUIP_BASE | Equipment Issue — Base Stage | LIQUID | 6 (INFERRED) | 90 | 8.2.2.28: "EQUIPMENT ISSUES BASE" |
| Equipment issue — clear | EQUIP | Equipment Defects | EQUIP_CLEAR | Equipment Issue — Clear Stage | LIQUID | 6 (INFERRED) | 100 | 8.2.2.28: "EQUIPMENT ISSUES CLEAR" |

### CSV Block

```csv
FormDefectName,ProposedParentCode_L1,ProposedParentName_L1,ProposedDefectCode_L2,ProposedDefectName_L2,LineTypeCode,DefaultSeverityId,SortOrderHint,Notes,EvidencePath,Confidence
Fan pattern break,APP,Application Defects,FAN_BREAK,Fan Pattern Break,LIQUID,5,10,Checklist item 14: observe fan breaks,8.2.2.2.7/Option 2,Medium
Part damage at blow-off,HAND,Handling Defects,PART_DMG_BLOWOFF,Part Damage at Blow-Off,LIQUID,4,20,Downtime category: PARTS HIT IN BLOW OFF,8.2.2.28/Feb,Medium
Booth environmental feedback,ENV,Environmental Defects,BOOTH_FEEDBACK,Booth Environmental Feedback,LIQUID,6,30,Downtime category: BOOTH FEEDBACK,8.2.2.28/Feb,Medium
Colour out of tolerance,COLOUR,Colour Defects,COLOUR_OOT,Colour Out of Tolerance,LIQUID,7,40,DEcmc > 2 or DL/Da/Db > 1.15 metallics,8.2.2.26/Sheet1,High
Viscosity out of tolerance,MIX,Paint Mix Defects,VISC_OOT,Viscosity Out of Tolerance,LIQUID,5,50,Inferred from viscosity capture fields,8.2.2.1.18/Paint Tally,Low
Catalyst issue,MIX,Paint Mix Defects,CATALYST_ISSUE,Catalyst Check Failure,LIQUID,7,60,Catalyst Check column on production tracking,8.2.2.2.1/Line Paint Production Tracking,Medium
Rack visual check failure,HAND,Handling Defects,RACK_VISUAL_FAIL,Rack Condition Failure,LIQUID,3,70,Rack Visual Check column,8.2.2.2.1/Line Paint Production Tracking,Medium
Equipment issue - primer,EQUIP,Equipment Defects,EQUIP_PRIME,Equipment Issue - Primer Stage,LIQUID,6,80,Downtime category: EQUIPMENT ISSUES PRIME,8.2.2.28/Feb,Medium
Equipment issue - base,EQUIP,Equipment Defects,EQUIP_BASE,Equipment Issue - Base Stage,LIQUID,6,90,Downtime category: EQUIPMENT ISSUES BASE,8.2.2.28/Feb,Medium
Equipment issue - clear,EQUIP,Equipment Defects,EQUIP_CLEAR,Equipment Issue - Clear Stage,LIQUID,6,100,Downtime category: EQUIPMENT ISSUES CLEAR,8.2.2.28/Feb,Medium
```

### L1 Categories Proposed from Part A (5 Categories)

| Code | Name | Expected Part B Expansion |
|---|---|---|
| APP | Application Defects | Runs/sags, orange peel, dry spray, overspray, thin/heavy film — expect heavy expansion |
| HAND | Handling Defects | Scratches, dents, fingerprints, racking marks — expect moderate expansion |
| ENV | Environmental Defects | Dirt/contamination, fisheye, cratering, solvent pop — expect heavy expansion |
| COLOUR | Colour Defects | Metamerism, mottling, colour mismatch — expect moderate expansion |
| MIX | Paint Mix Defects | Gel, skinning, settling, contamination — expect light expansion |
| EQUIP | Equipment Defects | Gun spit, robot path error, oven profile failure — expect moderate expansion |

> **Note:** Plant 1 audit identified ~38 normalized defect types. Part B customer inspection forms are expected to reveal the majority of Plant 2's defect vocabulary. The L1 categories above should be cross-referenced with Plant 1's L1 hierarchy for normalization.

---

## Appendix B: Form-to-Entity Field Mapping (Every Part A Form)

### B.1 — Production Tracking Forms

#### 8.2.2.1.5 — 101-103 Daily Load Sheet

| Form Field | Data Type (observed) | Schema.Table.Column Target | Mapping Type | Notes |
|---|---|---|---|---|
| Date | date (manual) | production.ProductionRun.RunDate | INFERRED | Header field — one date per sheet |
| Line | text (manual) | production.ProductionRun.ProductionLineId → dbo.ProductionLine | INFERRED | Header field — 101 or 103 |
| Operator | text (manual) | production.ProductionRun.CreatedByEmployeeId | INFERRED | No employee lookup; initials only |
| Raw # (per customer section) | text | dbo.Part.PartNumber | High | e.g., 99629, 9929, VG0241CM1PC |
| Part Description (per customer) | text | dbo.Part.PartName | High | e.g., "Main Lower Cover", "MS Tesla" |
| Customer section header | text | dbo.Customer.CustomerName | INFERRED | "Laval Tool", "Tesla", "KB Components", "Metelix" |
| Raw (quantity) | integer (manual) | production.ProductionRun.QuantityLoaded | INFERRED | Raw parts loaded |
| RW (quantity) | integer (manual) | production.ProductionRun.QuantityRework | INFERRED | Rework parts loaded |

#### 8.2.2.2.1 — 102 Line Paint Production Tracking

| Form Field | Data Type | Schema.Table.Column Target | Mapping Type | Notes |
|---|---|---|---|---|
| Date | date (manual) | production.ProductionRun.RunDate | High | |
| Starting Rack # | text | production.ProductionRunCarrier.CarrierId | High | Only per-carrier ID in 101-103 system |
| Colour | text | production.ProductionRun.ColourCode | High | Free-text; needs lookup |
| Part Desc. | text | dbo.Part.PartName | High | |
| Start Time | time | production.ProductionRunCarrier.StartTime | High | |
| End Time | time | production.ProductionRunCarrier.EndTime | High | |
| Base Coat — Fluid (PSI) | decimal | production.ProductionRunCarrier.BaseFluidPSI | High | |
| Base Coat — Atomizing (PSI) | decimal | production.ProductionRunCarrier.BaseAtomizingPSI | High | |
| Base Coat — Fan (PSI) | decimal | production.ProductionRunCarrier.BaseFanPSI | High | |
| Base Coat — 15 Sec Cup Test | decimal | production.ProductionRunCarrier.BaseCupTest_ml15s | High | |
| Base Coat — Fan Check | pass/fail | production.ProductionRunCarrier.BaseFanCheckPassed | High | |
| Base Coat — Rack Visual Check | pass/fail | production.ProductionRunCarrier.BaseRackVisualPassed | High | |
| Clear Coat — Fluid (PSI) | decimal | production.ProductionRunCarrier.ClearFluidPSI | High | |
| Clear Coat — Atomizing (PSI) | decimal | production.ProductionRunCarrier.ClearAtomizingPSI | High | |
| Clear Coat — Fan (PSI) | decimal | production.ProductionRunCarrier.ClearFanPSI | High | |
| Clear Coat — 15 Sec Cup Test | decimal | production.ProductionRunCarrier.ClearCupTest_ml15s | High | |
| Clear Coat — Fan Check | pass/fail | production.ProductionRunCarrier.ClearFanCheckPassed | High | |
| Clear Coat — Rack Visual Check | pass/fail | production.ProductionRunCarrier.ClearRackVisualPassed | High | |
| Clear Coat — Catalyst Check | pass/fail | production.ProductionRunCarrier.CatalystCheckPassed | High | |
| Temp / Humidity (3 locations) | text (manual) | production.ProductionRunCarrier.AmbientTempF, .AmbientHumidityPct | INFERRED | Multiple readings per form; structure unclear |
| Comments | text | production.ProductionRunCarrier.Comments | High | |

#### 8.2.2.2.4 — 102 Line Loaded Parts Tracking

| Form Field | Data Type | Schema.Table.Column Target | Mapping Type | Notes |
|---|---|---|---|---|
| Date | date | production.ProductionRun.RunDate | High | |
| Part Description | text | dbo.Part.PartName | High | |
| Carrier # | text | production.ProductionRunCarrier.CarrierId | High | Same key as "Starting Rack #" on 8.2.2.2.1 |
| Molding Date | date | UNKNOWN | Low | Upstream supplier data — no entity target |
| Quantity Loaded | integer | production.ProductionRunCarrier.QuantityLoaded | High | |
| Initials | text | production.ProductionRunCarrier.LoadedByEmployeeId | INFERRED | |

#### 8.2.2.29 — Daily Production Report Template

| Form Field | Data Type | Schema.Table.Column Target | Mapping Type | Notes |
|---|---|---|---|---|
| DATE | date | production.ProductionRun.RunDate | High | |
| PART | text | dbo.Part.PartName | High | |
| COLOUR | text | production.ProductionRun.ColourCode | High | |
| BOOTH | text | production.ProductionRun.BoothAssignment | INFERRED | |
| PAINTER | text | production.ProductionRun.PainterEmployeeId | INFERRED | |
| FLUID RATE (CC/15 SEC) | decimal | production.ProductionRunCarrier.BaseFluidPSI | INFERRED | Units differ from 102 form (cc vs PSI) |
| AIR PRESSURE (PSI) | decimal | production.ProductionRunCarrier.BaseAtomizingPSI | INFERRED | Generic — not per-stage |
| TEMP (°F) | decimal | production.ProductionRunCarrier.AmbientTempF | High | |
| HUMIDITY (%) | decimal | production.ProductionRunCarrier.AmbientHumidityPct | High | |
| FIRST-OFF TIME | time | production.ProductionRun.FirstOffTime | High | |
| LAST-OFF TIME | time | production.ProductionRun.LastOffTime | High | |
| SUPPLIER | text | dbo.Customer.CustomerName | INFERRED | Ambiguous — could be paint supplier or customer |
| NOTES (PROCESS) | text | production.ProductionRun.ProcessNotes | High | |
| NOTES (RESULTS) | text | production.ProductionRun.ResultNotes | High | Quality-adjacent — could link to NCR |
| FTQ (%) | decimal | production.ProductionRun.FTQPercent | High | No raw data basis on this form |
| TOTAL DOWNTIME | decimal | production.ProductionRun.TotalDowntimeMinutes | High | |

---

### B.2 — Process Control Forms

#### 8.2.2.1.16 — Oven Verification Log

| Form Field | Data Type | Schema.Table.Column Target | Mapping Type | Notes |
|---|---|---|---|---|
| Date | date | production.ProcessParameterReading.ReadingDate | INFERRED | No dedicated entity proposed yet — could be child of ProductionRun or standalone |
| Oven Setting | text/numeric | production.ProcessParameterReading.ParameterValue | INFERRED | No spec limits documented |
| Initial | text | production.ProcessParameterReading.RecordedByEmployeeId | INFERRED | |
| (implicit) Line 101 / Line 103 | — | dbo.ProductionLine via context | High | Separate columns per line |

#### 8.2.2.1.2 — Paint Kitchen Temp Log

| Form Field | Data Type | Schema.Table.Column Target | Mapping Type | Notes |
|---|---|---|---|---|
| Date/Time | datetime | production.ProcessParameterReading.ReadingDateTime | INFERRED | |
| TEMPERATURE | decimal | production.ProcessParameterReading.ParameterValue | INFERRED | No target range |
| Line Speed | decimal | production.ProcessParameterReading.ParameterValue (second param) | INFERRED | |
| Initial | text | production.ProcessParameterReading.RecordedByEmployeeId | INFERRED | |

#### 8.2.2.2.7 — 102 Line Operating Form (Option 2 — Application Tracker)

| Form Field | Data Type | Schema.Table.Column Target | Mapping Type | Notes |
|---|---|---|---|---|
| Name | text | production.ProductionRun.OperatorEmployeeId | High | |
| Date | date | production.ProductionRun.RunDate | High | |
| Program | text | production.ProductionRun.RobotProgramCode | High | References 8.2.2.2.6 job numbers |
| Colour | text | production.ProductionRun.ColourCode | High | |
| Temp At Start / End | decimal | production.ProductionRun.AmbientTempStartF, .AmbientTempEndF | High | |
| Humidity At Start / End | decimal | production.ProductionRun.HumidityStartPct, .HumidityEndPct | High | |
| Booth Temp At Start / End | decimal | production.ProductionRun.BoothTempStartF, .BoothTempEndF | High | |
| Checklist items 1–18 | mixed (value + initials) | production.StartupChecklist (proposed child entity) | INFERRED | 18 items with Value, OP Initial, Sup Initial per item |
| Carrier # | text | production.ProductionRunCarrier.CarrierId | High | Per-row production data |
| Time | time | production.ProductionRunCarrier.Timestamp | High | |
| Temp/Humidity | text | production.ProductionRunCarrier.AmbientReading | INFERRED | Combined field |
| RW Y/N | boolean | production.ProductionRunCarrier.IsRework | High | |
| Roller Initial | text | production.ProductionRunCarrier.LoadedByEmployeeId | INFERRED | |
| Primer — Fluid/Atom/Fan/flow/Comments | decimal+text | production.ProductionRunCarrier.PrimerFluid, .PrimerAtom, .PrimerFan, .PrimerFlowRate, .PrimerComments | High | |
| Base — Fluid/Atom/Fan/flow/Comments | decimal+text | production.ProductionRunCarrier.BaseFluid, .BaseAtom, .BaseFan, .BaseFlowRate, .BaseComments | High | |
| Clear — Fluid/Atom/Fan/flow/Comments | decimal+text | production.ProductionRunCarrier.ClearFluid, .ClearAtom, .ClearFan, .ClearFlowRate, .ClearComments | High | |

#### 8.2.2.2.6 — Line 102 Programs

| Form Field | Data Type | Schema.Table.Column Target | Mapping Type | Notes |
|---|---|---|---|---|
| Customer section header | text | dbo.Customer.CustomerName | High | Mytox, Rollstamp, etc. |
| Base Job | integer | production.RobotProgram.BaseJobNumber | INFERRED | New reference entity needed |
| Colour Valve | integer | production.RobotProgram.ColourValve | INFERRED | |
| Presets | decimal | production.RobotProgram.Presets | INFERRED | |
| Colour description | text | production.RobotProgram.ColourDescription | INFERRED | |
| Clear Job | integer | production.RobotProgram.ClearJobNumber | INFERRED | |

#### 8.2.2.33 — Paint Trial Information Sheet

| Form Field | Data Type | Schema.Table.Column Target | Mapping Type | Notes |
|---|---|---|---|---|
| Trial # | text | production.PaintTrial.TrialNumber | High | |
| Date | date | production.PaintTrial.TrialDate | High | |
| Temp / Humidity | text | production.PaintTrial.AmbientConditions | INFERRED | Combined field |
| Paint Supplier | text | production.PaintTrial.PaintSupplierId → dbo.Supplier | High | |
| Paint Code | text | production.PaintTrial.PaintCode | High | |
| Colour | text | production.PaintTrial.ColourCode | High | |
| Batch # | text | production.PaintTrial.PaintBatchId → PaintBatch | High | |
| Amount of Paint Used | text | production.PaintTrial.PaintAmountUsed | High | |
| Reducers and Amount Used | text | production.PaintTrial.ReducerInfo | High | |
| Catalyst | text | production.PaintTrial.CatalystType | High | |
| P-Mix Ratio | text | production.PaintTrial.PMixRatio | High | |
| Raw Viscosity / Reduced Viscosity | decimal | production.PaintTrial.RawViscosity, .ReducedViscosity | High | |
| Agitation Time | decimal | production.PaintTrial.AgitationTimeMin | High | |
| Inline Filters | text | production.PaintTrial.InlineFilterSize | High | |
| Primer Used | text | production.PaintTrial.PrimerUsed | High | |
| Parts Painted | text | production.PaintTrial.PartsPainted | High | |
| Reason for Trial | text | production.PaintTrial.ReasonForTrial | High | |
| Paint Line | text | production.PaintTrial.ProductionLineId → dbo.ProductionLine | High | |
| Clearcoat Used | text | production.PaintTrial.ClearcoatUsed | High | |
| Per-booth settings (Booth #1–4: Fluid Rate, Atomizing Air, Painter Name) | text/decimal | production.PaintTrialBooth (child) | INFERRED | 4 booth slots |

---

### B.3 — Paint Mix / Chemistry Forms

#### 8.2.2.1.18 — Daily Paint Tally Sheet

| Form Field | Data Type | Schema.Table.Column Target | Mapping Type | Notes |
|---|---|---|---|---|
| Date (header) | date | production.PaintBatch.BatchDate | High | Manual write-in |
| Painter Mixer (header) | text | production.PaintBatch.MixedByEmployeeId | INFERRED | |
| Line (header) | text | production.PaintBatch.ProductionLineId | INFERRED | |
| Row number (1–12) | integer | production.PaintBatch.SequenceNumber | High | |
| Paint Colour | text | production.PaintBatch.PaintColourCode | High | Free-text |
| Supplier | text | production.PaintBatch.PaintSupplierId → dbo.Supplier | High | |
| Batch # | text | production.PaintBatch.SupplierBatchNumber | High | |
| Amount of raw paint (gallons) | decimal | production.PaintBatch.RawPaintQuantityGal | High | |
| Agitation Time (mins) | integer | production.PaintBatch.AgitationTimeMin | High | |
| Temp. of Raw Paint | decimal | production.PaintBatch.RawPaintTempF | High | |
| Raw Viscosity | decimal | production.PaintBatch.RawViscosity | High | |
| Solvent Used / Amount per ½ pail | text | production.PaintBatch.SolventType, .SolventAmount | High | Combined field |
| Reduced Viscosity | decimal | production.PaintBatch.ReducedViscosity | High | |
| Total paint consumption (gallons) | decimal | production.PaintBatch.TotalPaintConsumptionGal | High | |
| Straining filter size | text | production.PaintBatch.StrainingFilterSize | High | |
| In line filter size | text | production.PaintBatch.InlineFilterSize | High | |

#### 8.2.2.23 — Paint Mix Information Sheet

| Form Field | Data Type | Schema.Table.Column Target | Mapping Type | Notes |
|---|---|---|---|---|
| Date | date | production.PaintBatch.BatchDate | High | |
| Supplier | text | production.PaintBatch.PaintSupplierId | High | |
| Paint Name | text | production.PaintBatch.PaintColourCode | High | |
| Reducers | text | production.PaintBatch.ReducerType | High | |
| Reference Note | text | production.PaintBatch.Comments | INFERRED | |
| Catalyst | text | production.PaintBatch.CatalystType | High | |
| Viscosity — Raw | decimal | production.PaintBatch.RawViscosity | High | |
| Viscosity — Reduced | decimal | production.PaintBatch.ReducedViscosity | High | |
| In-Line Filter | text | production.PaintBatch.InlineFilterSize | High | |
| P-Mix Ratio | text | production.PaintBatch.PMixRatio | High | |
| Comments | text | production.PaintBatch.Comments | High | |

#### 8.2.2.26 — New Paint Batch Verification

| Form Field | Data Type | Schema.Table.Column Target | Mapping Type | Notes |
|---|---|---|---|---|
| Date | date | production.ColourVerification.VerificationDate | High | |
| Paint Supplier | text | production.ColourVerification.PaintSupplier | High | |
| Colour | text | production.ColourVerification.ColourName | High | |
| Paint Code | text | production.ColourVerification.PaintCode | High | |
| Batch # | text | production.ColourVerification.SupplierBatchNumber | High | |
| Viscosity | decimal | production.ColourVerification.Viscosity | High | |
| Approved By | text | production.ColourVerification.ApprovedByEmployeeId | High | |
| Master L/a/b at 25°/45°/75° | decimal×9 | production.ColourVerification.MasterL_25 through .MasterB_75 | High | |
| Batch Panel L/a/b at 25°/45°/75° | decimal×9 | production.ColourVerification.BatchL_25 through .BatchB_75 | High | |
| ΔL/Δa/Δb/ΔEcmc at 25°/45°/75° (Batch) | decimal×12 | production.ColourVerification.DeltaL_25 through .DeltaEcmc_75 | High | |
| SprayOut1 L/a/b/ΔEcmc at 25°/45°/75° | decimal×12 | production.ColourVerification.SprayOut1_L_25 through .SprayOut1_Ecmc_75 | High | |
| SprayOut2 readings + Changes Made | decimal×12 + text | production.ColourVerification.SprayOut2_* + .ChangesDescription | High | |
| Pass/Fail | bit | production.ColourVerification.PassFail | High | |
| Comments | text | production.ColourVerification.Comments | High | |

#### Inventory & Consumption Reference Forms (Summarized)

| Form | Target | Notes |
|---|---|---|
| 8.2.2.5 | dbo.PaintProduct (proposed reference table) or direct fields on PaintBatch | Vendor Part#, Product Code, Container Size, Cost per UM-CAD, Min/Max QTY |
| 8.2.2.25 | production.PaintBatch (solvent sub-fields) + production.WasteRecord (output) | Primer/solvent consumption per day; drum tracking |
| 8.2.2.24 | production.PaintBatch (label output) | Pressure Pot Label is a print artifact of PaintBatch data; fields are a subset of 8.2.2.1.18/8.2.2.23 |

---

### B.4 — Maintenance Forms (Summarized)

All 10 maintenance forms map to `production.MaintenanceRecord`. Key field mappings:

| Form | Unique Fields → MaintenanceRecord | Equipment Target | Frequency |
|---|---|---|---|
| 8.2.2.1.1 Rack Burn Off | RackName, WeekDate, IsCompleted | RACK (65+ named racks) | Weekly |
| 8.2.2.1.3 Daily Booth Cleaning | TaskName (Gun cleaned, Hose wiped, Filters pulled, etc.), BoothPosition (1–4, Primer, Flash) | SPRAY_BOOTH | Daily |
| 8.2.2.1.4 Monthly Booth Cleaning | TaskName (P-Mix Base/Clear, Washer, Dry Off Oven, Booths Scraped, etc.), WeekNumber | SPRAY_BOOTH, PMIX, OVEN | Monthly |
| 8.2.2.1.19/20 Pot Cleaning Charts | SubSystem (P-Mix Clear/Base, Counters), DateCompleted, Initials | PMIX (Line 103 / 101) | Per-event |
| 8.2.2.2.8 Robot Operator Maint | TaskName (Dress Robot, Clean P-Mix, Pails Empty, Floor Filters), DayOfWeek, SupervisorInitial, OpsManagerInitial | ROBOT (102) | Daily |
| 8.2.2.2.9 TPM Checklist | TPMItem (Check Air Cap, Fluid Nozzle, Electrode), Date, Colour, Time, SupervisorInitial | ROBOT (102) | Per-colour-change |
| 8.2.2.2.10 Maintenance Log | Date, TaskCode (from dropdown), Reason, Comments | All Line 102 equipment | Per-event |
| 8.2.2.32 Sander Maint | TaskName (Replace Bag, Hose Wiped, Head Wiped, Vacuum Interior, Floor, Garbage, Filters), SanderNumber (1–6) | SANDER (1–6) | Daily |
| 8.2.2.34 Sanding Booth | Daily: TaskName (Bucket emptied, Floor swept, Table cleaned, etc.); Monthly: Filter swap date/initials | SANDING_BOOTH | Daily + Monthly |

---

### B.5 — Post-Paint, Scheduling, Tags, Waste, Document Control (Summarized)

| Form | Target Entity | Key Fields Mapped | Notes |
|---|---|---|---|
| 8.2.2.7 Sanding Tally | production.PostPaintOperation | OperationDate, TimeSpent, PartDescription, QtySanded, OperatorName | OperationTypeCode = SANDING |
| 8.2.2.8 Buffing Tally | production.PostPaintOperation | OperationDate, TimeSpent, PartDescription, QtyBuffed, OperatorName | OperationTypeCode = BUFFING; KANBAN tab has Spyder-specific pre-printed part list |
| 8.2.2.9 Deburring Tally | production.PostPaintOperation | OperationDate, PartName, TimeBlocks | OperationTypeCode = DEBURRING; no quantity field |
| 8.2.2.31 Hummer Sanding | production.PostPaintOperation | OperationDate, HourlyBlock, RunningTally, TotalPerHour, OperatorName | OperationTypeCode = HUMMER_SANDING; throughput-focused |
| 8.2.2.30 Buffing Summary | production.PostPaintDailySummary | Date, IntoBuffFromLine, TtlBuffed, NumBuffers, AvePerPerson, AvePerHr, Target, Efficiency, ReturnedToBuff, RWAfterBuff, FTQ | 272 days of data on Charts Info tab |
| 8.2.2.1.9 Daily Down Time | production.DowntimeEvent | Date, Name, Line, StartTime, EndTime, DownTimeLineOff, DownTimeLineOn, Reason | Per-event log |
| 8.2.2.28 Downtime Tracking | production.DowntimeEvent (aggregated) | Month, Line, CategoryCode, DayOfMonth, MinutesPerDay | Monthly matrix — 15 categories × 31 days × 3 lines |
| 8.2.2.10–16, 22 Tags | No direct entity — become NCR/ProductionRun status outputs | Quantity, PartDescription, Colour, Date, LH/RH | Tags are print artifacts, not data sources |
| 8.2.2.17–21 Waste Labels | production.WasteRecord (no current data to map) | WasteStreamCode only (from label title) | Drum labels — zero data fields |
| 8.2.2.6 Change Tracker | production.PaintTrial (Paint Trial tab) + N/A (Ship Request tab) | TrialNo, IssueIdentified, Date, Initiator, Approver, StartTime, EndTime, SampleSize, ParametersChanged | Ship Request tab is out-of-scope for quality platform |
| 8.2.2.2.17 Approved Tag Tracking | quality.NcrDisposition (INFERRED) | Date, TagNumber, Colour, PartDescription, Quantity, Initials | Abandoned since 2018; concept maps to NCR disposition audit trail |

---

### CSV Block — Complete Form-to-Entity Summary

```csv
DocNumber,FormName,PrimaryEntity,SecondaryEntity,KeyLinkingField,MappingConfidence,CriticalGaps
8.2.2.1.5,101-103 Daily Load Sheet,production.ProductionRun,dbo.Part,NONE - no rack/carrier ID,Medium,No carrier ID; no timestamp; no paint batch link
8.2.2.2.1,102 Line Paint Production Tracking,production.ProductionRunCarrier,production.ProductionRun,Starting Rack #,High,No paint batch reference; no defect field
8.2.2.2.4,102 Line Loaded Parts Tracking,production.ProductionRunCarrier,dbo.Part,Carrier #,High,Molding Date has no entity target
8.2.2.29,Daily Production Report Template,production.ProductionRun,dbo.Part,DATE + LINE (composite),Medium,Monthly summary - not per-carrier; FTQ has no basis data
8.2.2.1.18,Daily Paint Tally Sheet,production.PaintBatch,dbo.Supplier,DATE + LINE + SequenceNumber,High,No link to which carriers used this batch
8.2.2.1.16,Oven Verification Log,production.ProcessParameterReading,dbo.Equipment,DATE + LINE,Medium,No spec limits; no dedicated entity proposed; 2016 stale
8.2.2.1.2,Paint Kitchen Temp Log,production.ProcessParameterReading,dbo.Equipment,DateTime,Medium,No target range; 2016 stale
8.2.2.2.7,102 Line Operating Form,production.ProductionRun + ProductionRunCarrier,production.StartupChecklist,Carrier # + Date,High,Best form in audit - covers SWI + checklist + production data
8.2.2.2.6,Line 102 Programs,production.RobotProgram (new ref),dbo.Customer,Job Number,Medium,Reference data - not transactional
8.2.2.33,Paint Trial Information Sheet,production.PaintTrial,production.PaintBatch,Trial #,High,Comprehensive trial documentation
8.2.2.23,Paint Mix Information Sheet,production.PaintBatch,dbo.Supplier,DATE (no explicit batch ID),Medium,Subset of Paint Tally data - may be redundant
8.2.2.24,Pressure Pot Label,production.PaintBatch (label output),NONE,Pot #,Medium,Print artifact - 8-up layout
8.2.2.25,Solvent Usage Tracking,production.PaintBatch + WasteRecord,dbo.Supplier,DATE,Medium,Input tracking only - no waste output data
8.2.2.26,New Paint Batch Verification,production.ColourVerification,production.PaintBatch,Batch # + Colour,High,Lab-grade data with spec limits
8.2.2.5,Paint Kitchen Inventory,dbo.PaintProduct (proposed ref),dbo.Supplier,Vendor Part#,High,Reference + inventory - not transactional quality
8.2.2.1.1,Rack Burn Off Tracker,production.MaintenanceRecord,dbo.Equipment (RACK),RackName + WeekDate,High,52-week tracker with 65+ racks
8.2.2.1.3,Daily Booth Cleaning,production.MaintenanceRecord,dbo.Equipment (BOOTH),TaskName + BoothPosition,High,Check-off only
8.2.2.1.4,Monthly Booth Cleaning,production.MaintenanceRecord,dbo.Equipment (BOOTH/PMIX/OVEN),TaskName + WeekNumber,High,Has Rev Log
8.2.2.1.19,103 Pot Cleaning Chart,production.MaintenanceRecord,dbo.Equipment (PMIX),SubSystem + Date,High,Line 103 specific
8.2.2.1.20,101 Pot Cleaning Chart,production.MaintenanceRecord,dbo.Equipment (PMIX),SubSystem + Date,High,Line 101 specific
8.2.2.2.8,Robot Operator Maintenance,production.MaintenanceRecord,dbo.Equipment (ROBOT),TaskName + DayOfWeek,High,Line 102 - dual manager sign-off
8.2.2.2.9,102 TPM Checklist,production.MaintenanceRecord,dbo.Equipment (ROBOT),TPMItem + Date,High,Per-colour-change frequency
8.2.2.2.10,102 Maintenance Log,production.MaintenanceRecord,dbo.Equipment (various),Date + TaskCode,High,Best maintenance form - has dropdown task list
8.2.2.32,Sander Maintenance,production.MaintenanceRecord,dbo.Equipment (SANDER),TaskName + SanderNumber,High,6 individual sanders tracked
8.2.2.34,Sanding Booth Cleaning,production.MaintenanceRecord,dbo.Equipment (SANDING_BOOTH),TaskName + Date,High,Daily + monthly tabs
8.2.2.7,Daily Sanding Tally,production.PostPaintOperation,dbo.Part,Date + OperatorName,High,No defect type; no production source
8.2.2.8,Daily Buffing Tally,production.PostPaintOperation,dbo.Part,Date + OperatorName,High,KANBAN tab has Spyder part list
8.2.2.9,Daily Deburring Tally,production.PostPaintOperation,dbo.Part,Date + PartName,High,No quantity column
8.2.2.31,Hummer Sanding Tally,production.PostPaintOperation,NONE,Date + HourBlock,Medium,Throughput rate only - no part detail
8.2.2.30,Buffing Summary,production.PostPaintDailySummary,NONE,Date,High,272 days data; FTQ formulas; input fields unpopulated
8.2.2.17,Booth Sludge,production.WasteRecord,NONE,NONE,Low,Drum label only - zero data fields
8.2.2.18,Empty,production.WasteRecord,NONE,NONE,Low,Container label only
8.2.2.19,Still Bottoms,production.WasteRecord,NONE,NONE,Low,Drum label only
8.2.2.20,Waste Paint,production.WasteRecord,NONE,NONE,Low,Drum label only
8.2.2.21,Waste Zinc,production.WasteRecord,NONE,NONE,Low,Drum label only
8.2.2.1.9,Daily Down Time,production.DowntimeEvent,dbo.ProductionLine,Date + Line + StartTime,Medium,Free-text reason field
8.2.2.28,Downtime Tracking Template,production.DowntimeEvent (aggregated),dbo.ProductionLine,Month + Line + Category + Day,High,15 categories - propose as standard
8.2.2.1.6,101 Schedule Template,None/Reference,dbo.Part,N/A,Low,MES/planning - not quality
8.2.2.1.7,Daily Painter Schedule,production.ProductionRun (painter assignment),dbo.ProductionLine,Date + Line + Booth,Medium,Quality-relevant for root cause
8.2.2.1.9,Daily Down Time,production.DowntimeEvent,dbo.ProductionLine,Date + Line + StartTime,Medium,Per-event capture
8.2.2.1.10,Daily Painter Line Up,production.ProductionRun (painter assignment),dbo.ProductionLine,Date + Line + Booth,Medium,Overlaps with 8.2.2.1.7
8.2.2.1.11,103 Schedule Template,None/Reference,dbo.Part,N/A,Low,MES/planning - not quality
8.2.2.2.3,102 Schedule Template,None/Reference,dbo.Part + RobotProgram,N/A,Low,Has MasterJobRef - reference data for recipe verification
8.2.2.10,Sanded-Ready For Paint,NCR status output,quality.NCR,NONE,Medium,Print tag - maps to RECOAT disposition
8.2.2.11,Finished Goods/Partial,None/Reference,NONE,NONE,Low,Shipping/WIP tag
8.2.2.12,Hold Tag,quality.NCR (status indicator),NONE,NONE,Medium,REVIEW/REJECT/REINSPECT checkboxes
8.2.2.13,Hold For Review,quality.NCR (status indicator),NONE,NONE,Medium,Softer hold variant
8.2.2.14,Partial Raw,None/Reference,NONE,NONE,Low,Raw material ID tag
8.2.2.15,Rework-To Be Sanded,quality.NcrDisposition,quality.NCR,NONE,Medium,Maps to REWORK disposition
8.2.2.16,To Be Buffed,quality.NcrDisposition,quality.NCR,NONE,Medium,REWORK or routine
8.2.2.22,Use Next,None/Reference,NONE,NONE,Low,FIFO flag only
8.2.2.27,Template,None/Reference,NONE,NONE,Low,Blank ATT template
8.2.2.2.17,Approved Tag Tracking,quality.NcrDisposition (INFERRED),quality.NCR,Tag #,Low,Abandoned since 2018
8.2.2.6,Change Tracker,production.PaintTrial,production.PaintBatch,Trial No,Medium,Mislabeled - is paint trial tracker not doc control
```

---

## Appendix C: Proposed New Entity Schemas

### C1. SQL-Style Definitions

```sql
-- ============================================================
-- SCHEMA: production
-- Purpose: Operational production data for sf-quality platform
-- ============================================================

CREATE SCHEMA production;
GO

-- ------------------------------------------------------------
-- ProductionRun: Daily line-level production record
-- Parent of ProductionRunCarrier (per-rack detail)
-- ------------------------------------------------------------
CREATE TABLE production.ProductionRun (
    ProductionRunId         INT IDENTITY(1,1) PRIMARY KEY,
    PlantId                 INT NOT NULL REFERENCES dbo.Plant(PlantId),
    ProductionLineId        INT NOT NULL REFERENCES dbo.ProductionLine(ProductionLineId),
    ShiftId                 INT NULL REFERENCES dbo.Shift(ShiftId),
    RunDate                 DATE NOT NULL,
    CustomerId              INT NULL REFERENCES dbo.Customer(CustomerId),
    PartId                  INT NULL REFERENCES dbo.Part(PartId),
    ColourCode              NVARCHAR(50) NULL,
    BoothAssignment         NVARCHAR(50) NULL,
    PainterEmployeeId       INT NULL,
    RobotProgramCode        NVARCHAR(20) NULL,
    QuantityLoaded          INT NULL,
    QuantityRework          INT NULL,
    QuantityGood            INT NULL,
    FTQPercent              DECIMAL(5,2) NULL,
    FirstOffTime            TIME NULL,
    LastOffTime             TIME NULL,
    AmbientTempStartF       DECIMAL(5,1) NULL,
    AmbientTempEndF         DECIMAL(5,1) NULL,
    HumidityStartPct        DECIMAL(5,1) NULL,
    HumidityEndPct          DECIMAL(5,1) NULL,
    BoothTempStartF         DECIMAL(5,1) NULL,
    BoothTempEndF           DECIMAL(5,1) NULL,
    TotalDowntimeMinutes    INT NULL,
    ProcessNotes            NVARCHAR(1000) NULL,
    ResultNotes             NVARCHAR(1000) NULL,
    CreatedByEmployeeId     INT NULL,
    CreatedAt               DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    ModifiedAt              DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

-- ------------------------------------------------------------
-- ProductionRunCarrier: Per-rack/carrier detail within a run
-- Child of ProductionRun
-- ------------------------------------------------------------
CREATE TABLE production.ProductionRunCarrier (
    ProductionRunCarrierId  INT IDENTITY(1,1) PRIMARY KEY,
    ProductionRunId         INT NOT NULL REFERENCES production.ProductionRun(ProductionRunId),
    CarrierId               NVARCHAR(30) NOT NULL,
    SequenceNumber          SMALLINT NULL,
    Timestamp               TIME NULL,
    QuantityLoaded          INT NULL,
    MoldingDate             DATE NULL,
    IsRework                BIT NOT NULL DEFAULT 0,
    AmbientTempF            DECIMAL(5,1) NULL,
    AmbientHumidityPct      DECIMAL(5,1) NULL,
    -- Primer stage
    PrimerFluidPSI          DECIMAL(6,2) NULL,
    PrimerAtomizingPSI      DECIMAL(6,2) NULL,
    PrimerFanPSI            DECIMAL(6,2) NULL,
    PrimerFlowRate          DECIMAL(6,2) NULL,
    PrimerComments          NVARCHAR(500) NULL,
    -- Base coat stage
    BaseFluidPSI            DECIMAL(6,2) NULL,
    BaseAtomizingPSI        DECIMAL(6,2) NULL,
    BaseFanPSI              DECIMAL(6,2) NULL,
    BaseCupTest_ml15s       DECIMAL(6,2) NULL,
    BaseFlowRate            DECIMAL(6,2) NULL,
    BaseFanCheckPassed      BIT NULL,
    BaseRackVisualPassed    BIT NULL,
    BaseComments            NVARCHAR(500) NULL,
    -- Clear coat stage
    ClearFluidPSI           DECIMAL(6,2) NULL,
    ClearAtomizingPSI       DECIMAL(6,2) NULL,
    ClearFanPSI             DECIMAL(6,2) NULL,
    ClearCupTest_ml15s      DECIMAL(6,2) NULL,
    ClearFlowRate           DECIMAL(6,2) NULL,
    ClearFanCheckPassed     BIT NULL,
    ClearRackVisualPassed   BIT NULL,
    CatalystCheckPassed     BIT NULL,
    ClearComments           NVARCHAR(500) NULL,
    --
    LoadedByEmployeeId      INT NULL,
    CreatedAt               DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

-- ------------------------------------------------------------
-- PaintBatch: Discrete paint mix event
-- ------------------------------------------------------------
CREATE TABLE production.PaintBatch (
    PaintBatchId            INT IDENTITY(1,1) PRIMARY KEY,
    PlantId                 INT NOT NULL REFERENCES dbo.Plant(PlantId),
    ProductionLineId        INT NULL REFERENCES dbo.ProductionLine(ProductionLineId),
    BatchDate               DATE NOT NULL,
    SequenceNumber          SMALLINT NOT NULL,
    PaintColourCode         NVARCHAR(50) NOT NULL,
    PaintSupplierId         INT NULL REFERENCES dbo.Supplier(SupplierId),
    PaintProductCode        NVARCHAR(50) NULL,
    SupplierBatchNumber     NVARCHAR(50) NULL,
    RawPaintQuantityGal     DECIMAL(8,2) NULL,
    AgitationTimeMin        SMALLINT NULL,
    RawPaintTempF           DECIMAL(5,1) NULL,
    RawViscosity            DECIMAL(6,2) NULL,
    SolventType             NVARCHAR(50) NULL,
    SolventAmount           DECIMAL(6,2) NULL,
    ReducedViscosity        DECIMAL(6,2) NULL,
    TotalConsumptionGal     DECIMAL(8,2) NULL,
    StrainingFilterSize     NVARCHAR(20) NULL,
    InlineFilterSize        NVARCHAR(20) NULL,
    PMixRatio               NVARCHAR(20) NULL,
    CatalystType            NVARCHAR(50) NULL,
    ReducerType             NVARCHAR(50) NULL,
    PotNumber               NVARCHAR(10) NULL,
    MixedByEmployeeId       INT NULL,
    VerifiedByEmployeeId    INT NULL,
    ColourVerificationId    INT NULL,  -- FK added after ColourVerification created
    CreatedAt               DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

-- ------------------------------------------------------------
-- ColourVerification: Lab-grade incoming paint colour check
-- ------------------------------------------------------------
CREATE TABLE production.ColourVerification (
    ColourVerificationId    INT IDENTITY(1,1) PRIMARY KEY,
    PaintBatchId            INT NULL REFERENCES production.PaintBatch(PaintBatchId),
    VerificationDate        DATE NOT NULL,
    PaintSupplier           NVARCHAR(50) NOT NULL,
    ColourName              NVARCHAR(50) NOT NULL,
    PaintCode               NVARCHAR(50) NOT NULL,
    SupplierBatchNumber     NVARCHAR(50) NOT NULL,
    Viscosity               DECIMAL(6,2) NULL,
    -- Master plaque readings (3 angles × L,a,b)
    MasterL_25  DECIMAL(6,3) NULL, MasterA_25  DECIMAL(6,3) NULL, MasterB_25  DECIMAL(6,3) NULL,
    MasterL_45  DECIMAL(6,3) NULL, MasterA_45  DECIMAL(6,3) NULL, MasterB_45  DECIMAL(6,3) NULL,
    MasterL_75  DECIMAL(6,3) NULL, MasterA_75  DECIMAL(6,3) NULL, MasterB_75  DECIMAL(6,3) NULL,
    -- Supplier batch panel readings
    BatchL_25   DECIMAL(6,3) NULL, BatchA_25   DECIMAL(6,3) NULL, BatchB_25   DECIMAL(6,3) NULL,
    BatchL_45   DECIMAL(6,3) NULL, BatchA_45   DECIMAL(6,3) NULL, BatchB_45   DECIMAL(6,3) NULL,
    BatchL_75   DECIMAL(6,3) NULL, BatchA_75   DECIMAL(6,3) NULL, BatchB_75   DECIMAL(6,3) NULL,
    -- Deltas (batch vs master)
    DeltaEcmc_25 DECIMAL(6,3) NULL, DeltaEcmc_45 DECIMAL(6,3) NULL, DeltaEcmc_75 DECIMAL(6,3) NULL,
    -- First spray out
    SprayOut1_L_25 DECIMAL(6,3) NULL, SprayOut1_A_25 DECIMAL(6,3) NULL, SprayOut1_B_25 DECIMAL(6,3) NULL,
    SprayOut1_Ecmc_25 DECIMAL(6,3) NULL,
    SprayOut1_L_45 DECIMAL(6,3) NULL, SprayOut1_A_45 DECIMAL(6,3) NULL, SprayOut1_B_45 DECIMAL(6,3) NULL,
    SprayOut1_Ecmc_45 DECIMAL(6,3) NULL,
    SprayOut1_L_75 DECIMAL(6,3) NULL, SprayOut1_A_75 DECIMAL(6,3) NULL, SprayOut1_B_75 DECIMAL(6,3) NULL,
    SprayOut1_Ecmc_75 DECIMAL(6,3) NULL,
    -- Second spray out
    SprayOut2_L_25 DECIMAL(6,3) NULL, SprayOut2_A_25 DECIMAL(6,3) NULL, SprayOut2_B_25 DECIMAL(6,3) NULL,
    SprayOut2_Ecmc_25 DECIMAL(6,3) NULL,
    SprayOut2_L_45 DECIMAL(6,3) NULL, SprayOut2_A_45 DECIMAL(6,3) NULL, SprayOut2_B_45 DECIMAL(6,3) NULL,
    SprayOut2_Ecmc_45 DECIMAL(6,3) NULL,
    SprayOut2_L_75 DECIMAL(6,3) NULL, SprayOut2_A_75 DECIMAL(6,3) NULL, SprayOut2_B_75 DECIMAL(6,3) NULL,
    SprayOut2_Ecmc_75 DECIMAL(6,3) NULL,
    ChangesDescription      NVARCHAR(500) NULL,
    PassFail                BIT NOT NULL,
    ApprovedByEmployeeId    INT NULL,
    Comments                NVARCHAR(500) NULL,
    CreatedAt               DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

-- Add FK from PaintBatch to ColourVerification
ALTER TABLE production.PaintBatch
ADD CONSTRAINT FK_PaintBatch_ColourVerification
    FOREIGN KEY (ColourVerificationId) REFERENCES production.ColourVerification(ColourVerificationId);

-- ------------------------------------------------------------
-- MaintenanceRecord
-- ------------------------------------------------------------
CREATE TABLE production.MaintenanceRecord (
    MaintenanceRecordId     INT IDENTITY(1,1) PRIMARY KEY,
    PlantId                 INT NOT NULL REFERENCES dbo.Plant(PlantId),
    ProductionLineId        INT NULL REFERENCES dbo.ProductionLine(ProductionLineId),
    EquipmentId             INT NULL REFERENCES dbo.Equipment(EquipmentId),
    MaintenanceDate         DATE NOT NULL,
    MaintenanceTypeCode     NVARCHAR(20) NOT NULL,  -- DAILY, WEEKLY, MONTHLY, UNPLANNED
    TaskCode                NVARCHAR(50) NOT NULL,
    IsCompleted             BIT NOT NULL DEFAULT 0,
    Reason                  NVARCHAR(500) NULL,
    CompletedByEmployeeId   INT NULL,
    VerifiedByEmployeeId    INT NULL,
    DurationMinutes         INT NULL,
    Comments                NVARCHAR(500) NULL,
    NcrId                   INT NULL,  -- FK to quality.NonConformanceReport
    DowntimeEventId         INT NULL,  -- FK to production.DowntimeEvent
    CreatedAt               DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

-- ------------------------------------------------------------
-- WasteRecord
-- ------------------------------------------------------------
CREATE TABLE production.WasteRecord (
    WasteRecordId           INT IDENTITY(1,1) PRIMARY KEY,
    PlantId                 INT NOT NULL REFERENCES dbo.Plant(PlantId),
    ProductionLineId        INT NULL REFERENCES dbo.ProductionLine(ProductionLineId),
    WasteStreamCode         NVARCHAR(20) NOT NULL,  -- BOOTH_SLUDGE, STILL_BOTTOMS, WASTE_PAINT, WASTE_ZINC, EMPTY_CONTAINER
    ContainerId             NVARCHAR(30) NULL,
    DateOpened              DATE NULL,
    DateClosed              DATE NULL,
    QuantityGal             DECIMAL(8,2) NULL,
    WeightLbs               DECIMAL(8,2) NULL,
    ManifestNumber          NVARCHAR(30) NULL,
    DisposalVendor          NVARCHAR(100) NULL,
    RegulatoryClassification NVARCHAR(50) NULL,
    DisposalDate            DATE NULL,
    DisposalMethod          NVARCHAR(50) NULL,
    EstimatedCostCAD        DECIMAL(10,2) NULL,
    Comments                NVARCHAR(500) NULL,
    CreatedByEmployeeId     INT NULL,
    CreatedAt               DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

-- ------------------------------------------------------------
-- PostPaintOperation: Individual rework/finishing record
-- ------------------------------------------------------------
CREATE TABLE production.PostPaintOperation (
    PostPaintOperationId    INT IDENTITY(1,1) PRIMARY KEY,
    PlantId                 INT NOT NULL REFERENCES dbo.Plant(PlantId),
    OperationDate           DATE NOT NULL,
    ShiftId                 INT NULL REFERENCES dbo.Shift(ShiftId),
    OperationTypeCode       NVARCHAR(20) NOT NULL,  -- SANDING, BUFFING, DEBURRING, HUMMER_SANDING
    PartId                  INT NULL REFERENCES dbo.Part(PartId),
    PartDescription         NVARCHAR(100) NULL,
    CustomerId              INT NULL REFERENCES dbo.Customer(CustomerId),
    Quantity                INT NULL,
    TimeSpentMinutes        INT NULL,
    OperatorEmployeeId      INT NULL,
    IsRework                BIT NOT NULL DEFAULT 0,
    DefectTypeId            INT NULL,  -- FK to quality.DefectType
    SourceProductionRunId   INT NULL REFERENCES production.ProductionRun(ProductionRunId),
    SourceProductionLineId  INT NULL REFERENCES dbo.ProductionLine(ProductionLineId),
    NcrId                   INT NULL,  -- FK to quality.NonConformanceReport
    PassFail                BIT NULL,
    ReturnedToPostPaintOps  BIT NULL,
    Comments                NVARCHAR(500) NULL,
    CreatedAt               DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

-- ------------------------------------------------------------
-- PostPaintDailySummary: Aggregated daily KPIs
-- ------------------------------------------------------------
CREATE TABLE production.PostPaintDailySummary (
    SummaryId               INT IDENTITY(1,1) PRIMARY KEY,
    PlantId                 INT NOT NULL REFERENCES dbo.Plant(PlantId),
    SummaryDate             DATE NOT NULL,
    OperationTypeCode       NVARCHAR(20) NOT NULL,
    PartsInFromLine         INT NULL,
    TotalPartsProcessed     INT NULL,
    NumberOfOperators       INT NULL,
    AveragePerPerson        DECIMAL(6,1) NULL,
    AveragePerHour          DECIMAL(6,1) NULL,
    TargetPerHour           DECIMAL(6,1) NULL,
    EfficiencyPercent       DECIMAL(5,2) NULL,
    ReturnedToOperation     INT NULL,
    ReworkAfterOperation    INT NULL,
    FTQPercent              DECIMAL(5,4) NULL,
    CreatedAt               DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

-- ------------------------------------------------------------
-- DowntimeEvent
-- ------------------------------------------------------------
CREATE TABLE production.DowntimeEvent (
    DowntimeEventId         INT IDENTITY(1,1) PRIMARY KEY,
    PlantId                 INT NOT NULL REFERENCES dbo.Plant(PlantId),
    ProductionLineId        INT NOT NULL REFERENCES dbo.ProductionLine(ProductionLineId),
    ShiftId                 INT NULL REFERENCES dbo.Shift(ShiftId),
    EventDate               DATE NOT NULL,
    StartTime               TIME NOT NULL,
    EndTime                 TIME NULL,
    DurationMinutes         INT NULL,
    DowntimeCategoryCode    NVARCHAR(30) NOT NULL,
    ProcessStageCode        NVARCHAR(10) NULL,  -- PRIME, BASE, CLEAR, GENERAL
    Reason                  NVARCHAR(500) NULL,
    IsPlanned               BIT NOT NULL DEFAULT 0,
    NcrId                   INT NULL,  -- FK to quality.NonConformanceReport
    CreatedAt               DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

-- ------------------------------------------------------------
-- PaintTrial
-- ------------------------------------------------------------
CREATE TABLE production.PaintTrial (
    PaintTrialId            INT IDENTITY(1,1) PRIMARY KEY,
    PlantId                 INT NOT NULL REFERENCES dbo.Plant(PlantId),
    TrialNumber             NVARCHAR(20) NOT NULL,
    IssueIdentified         NVARCHAR(500) NOT NULL,
    InitiatedByEmployeeId   INT NULL,
    ApprovedByEmployeeId    INT NULL,
    TrialDate               DATE NOT NULL,
    StartTime               TIME NULL,
    EndTime                 TIME NULL,
    SampleSize              INT NULL,
    ParametersChanged       NVARCHAR(2000) NULL,
    ProductionLineId        INT NULL REFERENCES dbo.ProductionLine(ProductionLineId),
    PaintBatchId            INT NULL REFERENCES production.PaintBatch(PaintBatchId),
    ColourCode              NVARCHAR(50) NULL,
    PaintCode               NVARCHAR(50) NULL,
    PaintSupplierId         INT NULL REFERENCES dbo.Supplier(SupplierId),
    PaintAmountUsed         NVARCHAR(50) NULL,
    ReducerInfo             NVARCHAR(200) NULL,
    CatalystType            NVARCHAR(50) NULL,
    PMixRatio               NVARCHAR(20) NULL,
    RawViscosity            DECIMAL(6,2) NULL,
    ReducedViscosity        DECIMAL(6,2) NULL,
    AgitationTimeMin        SMALLINT NULL,
    InlineFilterSize        NVARCHAR(20) NULL,
    PrimerUsed              NVARCHAR(50) NULL,
    PartsPainted            NVARCHAR(200) NULL,
    ReasonForTrial          NVARCHAR(500) NULL,
    ClearcoatUsed           NVARCHAR(50) NULL,
    AmbientConditions       NVARCHAR(100) NULL,
    Result                  NVARCHAR(20) NULL,  -- PASS, FAIL, INCONCLUSIVE
    Comments                NVARCHAR(2000) NULL,
    CreatedAt               DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

-- ------------------------------------------------------------
-- PaintTrialBooth: Per-booth settings for a trial
-- Child of PaintTrial
-- ------------------------------------------------------------
CREATE TABLE production.PaintTrialBooth (
    PaintTrialBoothId       INT IDENTITY(1,1) PRIMARY KEY,
    PaintTrialId            INT NOT NULL REFERENCES production.PaintTrial(PaintTrialId),
    BoothNumber             SMALLINT NOT NULL,  -- 1-4
    FluidRate               NVARCHAR(30) NULL,
    AtomizingAir            NVARCHAR(30) NULL,
    PainterName             NVARCHAR(50) NULL,
    CreatedAt               DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);
```

---

### C2. JSON Object Definitions

```json
{
  "proposedEntities": [
    {
      "name": "ProductionRun",
      "schema": "production",
      "description": "Daily line-level production record. One per line per customer/colour per day.",
      "primaryKey": "ProductionRunId",
      "foreignKeys": [
        "PlantId→dbo.Plant",
        "ProductionLineId→dbo.ProductionLine",
        "ShiftId→dbo.Shift",
        "CustomerId→dbo.Customer",
        "PartId→dbo.Part"
      ],
      "childEntities": ["ProductionRunCarrier"],
      "rlsScoped": true,
      "temporalVersioning": false,
      "sourceFormCount": 5,
      "primarySourceForms": ["8.2.2.1.5", "8.2.2.2.1", "8.2.2.2.4", "8.2.2.2.7", "8.2.2.29"]
    },
    {
      "name": "ProductionRunCarrier",
      "schema": "production",
      "description": "Per-rack/carrier detail within a production run. Captures spray parameters per stage.",
      "primaryKey": "ProductionRunCarrierId",
      "foreignKeys": ["ProductionRunId→production.ProductionRun"],
      "childEntities": [],
      "rlsScoped": false,
      "temporalVersioning": false,
      "sourceFormCount": 3,
      "primarySourceForms": ["8.2.2.2.1", "8.2.2.2.4", "8.2.2.2.7"]
    },
    {
      "name": "PaintBatch",
      "schema": "production",
      "description": "Discrete paint mix event. Liquid paint equivalent of Plant 1 bath analysis but batch-oriented.",
      "primaryKey": "PaintBatchId",
      "foreignKeys": [
        "PlantId→dbo.Plant",
        "ProductionLineId→dbo.ProductionLine",
        "PaintSupplierId→dbo.Supplier",
        "ColourVerificationId→production.ColourVerification"
      ],
      "childEntities": ["ColourVerification"],
      "rlsScoped": true,
      "temporalVersioning": false,
      "sourceFormCount": 4,
      "primarySourceForms": ["8.2.2.1.18", "8.2.2.23", "8.2.2.24", "8.2.2.25"]
    },
    {
      "name": "ColourVerification",
      "schema": "production",
      "description": "Lab-grade incoming paint colour verification with L/a/b colorimetry at 3 angles.",
      "primaryKey": "ColourVerificationId",
      "foreignKeys": ["PaintBatchId→production.PaintBatch"],
      "childEntities": [],
      "rlsScoped": true,
      "temporalVersioning": false,
      "sourceFormCount": 1,
      "primarySourceForms": ["8.2.2.26"]
    },
    {
      "name": "MaintenanceRecord",
      "schema": "production",
      "description": "Equipment maintenance event — daily/weekly/monthly/unplanned.",
      "primaryKey": "MaintenanceRecordId",
      "foreignKeys": [
        "PlantId→dbo.Plant",
        "ProductionLineId→dbo.ProductionLine",
        "EquipmentId→dbo.Equipment",
        "NcrId→quality.NonConformanceReport",
        "DowntimeEventId→production.DowntimeEvent"
      ],
      "childEntities": [],
      "rlsScoped": true,
      "temporalVersioning": false,
      "sourceFormCount": 10,
      "primarySourceForms": [
        "8.2.2.1.1", "8.2.2.1.3", "8.2.2.1.4", "8.2.2.1.19", "8.2.2.1.20",
        "8.2.2.2.8", "8.2.2.2.9", "8.2.2.2.10", "8.2.2.32", "8.2.2.34"
      ]
    },
    {
      "name": "WasteRecord",
      "schema": "production",
      "description": "Waste container lifecycle tracking. Net-new digital process — no paper form to digitize.",
      "primaryKey": "WasteRecordId",
      "foreignKeys": [
        "PlantId→dbo.Plant",
        "ProductionLineId→dbo.ProductionLine"
      ],
      "childEntities": [],
      "rlsScoped": true,
      "temporalVersioning": false,
      "sourceFormCount": 5,
      "primarySourceForms": ["8.2.2.17", "8.2.2.18", "8.2.2.19", "8.2.2.20", "8.2.2.21"],
      "note": "Source forms are drum labels with zero data fields. Entity is 100% net-new."
    },
    {
      "name": "PostPaintOperation",
      "schema": "production",
      "description": "Individual sanding/buffing/deburring event per operator per part per day.",
      "primaryKey": "PostPaintOperationId",
      "foreignKeys": [
        "PlantId→dbo.Plant",
        "ShiftId→dbo.Shift",
        "PartId→dbo.Part",
        "CustomerId→dbo.Customer",
        "DefectTypeId→quality.DefectType",
        "SourceProductionRunId→production.ProductionRun",
        "NcrId→quality.NonConformanceReport"
      ],
      "childEntities": [],
      "rlsScoped": true,
      "temporalVersioning": false,
      "sourceFormCount": 4,
      "primarySourceForms": ["8.2.2.7", "8.2.2.8", "8.2.2.9", "8.2.2.31"]
    },
    {
      "name": "PostPaintDailySummary",
      "schema": "production",
      "description": "Aggregated daily KPIs for buffing/sanding operations.",
      "primaryKey": "SummaryId",
      "foreignKeys": ["PlantId→dbo.Plant"],
      "childEntities": [],
      "rlsScoped": true,
      "temporalVersioning": false,
      "sourceFormCount": 1,
      "primarySourceForms": ["8.2.2.30"]
    },
    {
      "name": "DowntimeEvent",
      "schema": "production",
      "description": "Production line downtime event with 15-category taxonomy.",
      "primaryKey": "DowntimeEventId",
      "foreignKeys": [
        "PlantId→dbo.Plant",
        "ProductionLineId→dbo.ProductionLine",
        "ShiftId→dbo.Shift",
        "NcrId→quality.NonConformanceReport"
      ],
      "childEntities": [],
      "rlsScoped": true,
      "temporalVersioning": false,
      "sourceFormCount": 2,
      "primarySourceForms": ["8.2.2.1.9", "8.2.2.28"]
    },
    {
      "name": "PaintTrial",
      "schema": "production",
      "description": "Paint process change trial with comprehensive parameter and result documentation.",
      "primaryKey": "PaintTrialId",
      "foreignKeys": [
        "PlantId→dbo.Plant",
        "ProductionLineId→dbo.ProductionLine",
        "PaintBatchId→production.PaintBatch",
        "PaintSupplierId→dbo.Supplier"
      ],
      "childEntities": ["PaintTrialBooth"],
      "rlsScoped": true,
      "temporalVersioning": false,
      "sourceFormCount": 2,
      "primarySourceForms": ["8.2.2.6", "8.2.2.33"]
    }
  ],
  "summary": {
    "totalNewEntities": 10,
    "totalNewChildEntities": 3,
    "proposedSchema": "production",
    "estimatedMigrationCount": "15-20 migrations",
    "estimatedStoredProcedures": "25-35 new stored procedures",
    "crossSchemaForeignKeys": [
      "production.MaintenanceRecord.NcrId → quality.NonConformanceReport",
      "production.PostPaintOperation.DefectTypeId → quality.DefectType",
      "production.PostPaintOperation.NcrId → quality.NonConformanceReport",
      "production.DowntimeEvent.NcrId → quality.NonConformanceReport"
    ]
  }
}
```

---

**BATCH_ID:** A5
**COMPLETED_SECTIONS:** Appendix A (Defect Taxonomy Mapping Table), Appendix B (Form-to-Entity Field Mapping), Appendix C (Proposed New Entity Schemas)
