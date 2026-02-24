# BATCH B4: Section 5 (Platform Impact Assessment) + Section 6 (Consolidated Plant 2 Assessment)

---

## 5. Platform Impact Assessment

### A. DATABASE IMPACT

#### A.1 Existing Entity Coverage Score — Customer Inspection & Shipping

| Domain | Existing Entity | Coverage of Part B Forms | Notes |
|--------|----------------|--------------------------|-------|
| NCR Lifecycle | `quality.NonConformanceReport` | 0% | Zero inspection forms create or reference NCRs. Full entity exists, zero intake pathway. |
| NCR Containment | `quality.NcrContainmentAction` | 0% | GP-12 form has no containment fields. Entity exists, zero usage. |
| CAPA | `quality.CorrectiveAction` | 0% | No corrective action reference on any form. |
| Customer Complaint | `quality.CustomerComplaint` | 0% | No complaint tracking. Metelix RMA is closest but not linked. |
| SCAR | `quality.SupplierCar` | 0% | Receiving Log has Accept/Reject but no SCAR trigger. |
| Defect Taxonomy | `quality.DefectType` | 10% | Hierarchy structure exists. Zero seed data loaded. 42 defect strings extracted in Part B ready for seeding. |
| Disposition Codes | `quality.DispositionCode` | 60% | 11 codes exist. Inspection forms use 4 implicitly: REWORK (buff), RECOAT (repaint), SCRAP, RTS (molding defects). Missing explicit mapping from form section headers to codes. |
| Reference: Customer | `dbo.Customer` | 30% | Entity exists. 6 Part B customers need entries: Rollstamp, Mytox, Laval Tool, Metelix, KB Components, Polycon. Unknown if already seeded. |
| Reference: Part | `dbo.Part` | 10% | Entity exists. ~45 unique part numbers extracted across Part B forms. Unknown if any are loaded. |
| Reference: Plant/Line | `dbo.Plant`, `dbo.ProductionLine` | 80% | Plant 2 and Lines 101–103 likely configured from Part A. |

> **Overall Part B entity coverage: 8/100.** The database schema is built for quality event management (NCR lifecycle) but has zero intake mechanisms from the inspection and shipping processes where quality events actually originate. The inspection-to-NCR bridge is the #1 priority.

---

#### A.2 New Entity Proposals (Part B)

##### Entity 1: `quality.InspectionRecord` — Priority: CRITICAL

```sql
InspectionRecordId      INT PK IDENTITY
PlantId                 INT FK → dbo.Plant (RLS)
ProductionLineId        INT FK → dbo.ProductionLine (nullable)
ShiftId                 INT FK → dbo.Shift
CustomerId              INT FK → dbo.Customer
PartId                  INT FK → dbo.Part
InspectionDate          DATE NOT NULL
PaintDate               DATE (nullable — may differ, per Mytox)
InspectionTypeCodeId    INT FK → dbo.LookupValue
                        -- Values: PAINT, BUFF, GP12, PRE_PAINT, APPLICATION
InspectorId             INT FK → dbo.Employee (nullable — only Metelix captures)
CarrierNumber           NVARCHAR(50) (nullable — Mytox, Metelix Hummer/Y2XX)
RackNumber              NVARCHAR(50) (nullable — Mytox)
MoldingDate             DATE (nullable — KB, Tesla)
TotalGood               INT
TotalBuff               INT
TotalRepaint            INT
TotalMoldingDefect      INT
TotalScrap              INT (nullable — Rollstamp, Mytox only)
NcrId                   INT FK → quality.NonConformanceReport (nullable — escalation link)
ProductionRunId         INT FK → production.ProductionRun (nullable — traceability link)
ExternalDocReference    NVARCHAR(200) (nullable — Y2XX refs 8.3.2.9.26)
CreatedAt               DATETIME2 DEFAULT GETUTCDATE()
CreatedBy               NVARCHAR(100)
```

**Cardinality:** One InspectionRecord per customer × part × date × shift × inspection type. Estimated 20–50 records/day across all customers.

---

##### Entity 2: `quality.InspectionDefectCount` — Priority: CRITICAL (child of InspectionRecord)

```sql
InspectionDefectCountId INT PK IDENTITY
InspectionRecordId      INT FK → quality.InspectionRecord
DefectTypeId            INT FK → quality.DefectType
DispositionCodeId       INT FK → dbo.DispositionCode
                        -- Derived from form section: Buff→REWORK, Repaint→RECOAT,
                        -- Molding→RTS or SCRAP, Scrap→SCRAP
Quantity                INT NOT NULL DEFAULT 0
GateAlarmThreshold      INT (nullable — from CustomerInspectionProfile)
GateAlarmTriggered      AS CASE WHEN Quantity >= GateAlarmThreshold THEN 1 ELSE 0 END
```

**Cardinality:** 8–20 rows per InspectionRecord (one per defect type tracked). Sparse — most will be 0.

---

##### Entity 3: `quality.CustomerInspectionProfile` — Priority: HIGH

```sql
CustomerInspectionProfileId INT PK IDENTITY
CustomerId              INT FK → dbo.Customer
PartId                  INT FK → dbo.Part (nullable — NULL = customer-wide)
InspectionTypeCodeId    INT FK → dbo.LookupValue
DefectTypeId            INT FK → quality.DefectType
GateAlarmThreshold      INT (nullable)
SortOrder               INT NOT NULL DEFAULT 0
IsActive                BIT NOT NULL DEFAULT 1
SectionCode             NVARCHAR(20)
                        -- BUFF, REPAINT, MOLDING, SCRAP — drives form layout
DispositionCodeId       INT FK → dbo.DispositionCode
                        -- Default disposition for this section
```

**Cardinality:** ~180 rows (6 customers × ~5 parts avg × ~6 defects avg). This is configuration data, not transactional. Drives dynamic form rendering in the frontend.

---

##### Entity 4: `quality.Gp12ContainmentEvent` — Priority: HIGH

```sql
Gp12ContainmentEventId  INT PK IDENTITY
PlantId                 INT FK → dbo.Plant (RLS)
CustomerId              INT FK → dbo.Customer
PartId                  INT FK → dbo.Part
NcrId                   INT FK → quality.NonConformanceReport (triggering NCR)
EntryDate               DATE NOT NULL
EntryReason             NVARCHAR(500) NOT NULL
ExitDate                DATE (nullable)
ExitCriteria            NVARCHAR(500) (nullable)
InspectionFrequency     NVARCHAR(100) -- e.g., "100% for 30 days"
SampleSize              INT (nullable)
StatusCodeId            INT FK → dbo.StatusCode -- ACTIVE, CLOSED, EXPIRED
CustomerNotificationDate DATE (nullable)
CustomerApprovalDate    DATE (nullable)
```

**Cardinality:** Low — 2–5 active GP-12 events at any time. But critical for compliance.

---

##### Entity 5: `logistics.PackSlip` — Priority: MEDIUM

```sql
PackSlipId              INT PK IDENTITY
PackSlipNumber          NVARCHAR(20) NOT NULL -- Generated per customer sequence
PlantId                 INT FK → dbo.Plant (RLS)
CustomerId              INT FK → dbo.Customer
ShipDate                DATE NOT NULL
ShipVia                 NVARCHAR(100) (nullable)
DriverName              NVARCHAR(100) (nullable)
TruckTrailerNumber      NVARCHAR(50) (nullable)
ShipperInitials         NVARCHAR(10)
TotalContainers         INT
TotalParts              INT
TotalWeightKg           DECIMAL(10,2) (nullable)
QualityReleaseStatus    NVARCHAR(20) DEFAULT 'NOT_VERIFIED'
                        -- NEW: The missing quality gate
QualityReleasedById     INT FK → dbo.Employee (nullable)
QualityReleaseDate      DATETIME2 (nullable)
```

**Child:** `logistics.PackSlipLineItem`

```sql
PackSlipLineItemId      INT PK IDENTITY
PackSlipId              INT FK → logistics.PackSlip
PartId                  INT FK → dbo.Part
Quantity                INT NOT NULL
ContainerCount          INT (nullable)
PurchaseOrderNumber     NVARCHAR(50) (nullable)
InspectionRecordId      INT FK → quality.InspectionRecord (nullable)
                        -- NEW: The missing inspection-to-shipping link
```

---

##### Entity 6: `logistics.ReceivingLogEntry` — Priority: MEDIUM

```sql
ReceivingLogEntryId     INT PK IDENTITY
PlantId                 INT FK → dbo.Plant (RLS)
SupplierOrCustomerId    INT -- FK context depends on direction
EntryDirection          NVARCHAR(10) -- INBOUND / RETURN
PackingSlipNumber       NVARCHAR(50)
PurchaseOrderNumber     NVARCHAR(50) (nullable)
SupplierPromiseDate     DATE (nullable)
DateReceived            DATE NOT NULL
TimeReceived            TIME (nullable)
AcceptReject            CHAR(1) NOT NULL -- A or R
RejectedQuantity        INT (nullable)
RejectReasonCodeId      INT FK → dbo.LookupValue (nullable)
                        -- NEW: structured reject reason
ReceiverInitials        NVARCHAR(10)
ScarId                  INT FK → quality.SupplierCar (nullable)
                        -- NEW: SCAR escalation link
```

---

##### Entity 7: `logistics.ReturnMaterialAuthorization` — Priority: MEDIUM

```sql
RmaId                   INT PK IDENTITY
RmaNumber               NVARCHAR(20) NOT NULL
PlantId                 INT FK → dbo.Plant (RLS)
CustomerId              INT FK → dbo.Customer
RmaDate                 DATE NOT NULL
NcrId                   INT FK → quality.NonConformanceReport (nullable)
CustomerComplaintId     INT FK → quality.CustomerComplaint (nullable)
StatusCodeId            INT FK → dbo.StatusCode
```

**Child:** `logistics.RmaLineItem`

```sql
RmaLineItemId           INT PK IDENTITY
RmaId                   INT FK → logistics.ReturnMaterialAuthorization
PartId                  INT FK → dbo.Part
PartState               NVARCHAR(20) -- SANDED_RAW, UNSANDED_RAW, PAINTED
Quantity                INT NOT NULL
DispositionCodeId       INT FK → dbo.DispositionCode (nullable)
```

---

#### A.3 Defect Taxonomy Seed Data

Full merged table deferred to Appendix A (Batch B5).

**Summary:** 10 Part A operational defects + 28 Part B customer inspection defects = ~35 unique leaf entries after deduplication (3 overlaps: DIRT at load, SAG/RUN at process, ORANGE PEEL at process already captured in Part A operational context).

---

#### A.4 Reference Data Gaps

**Customer entries needed (6):**

| CustomerCode | CustomerName | Notes |
|--------------|-------------|-------|
| ROLLSTAMP | Rollstamp (BMW programs) | Ship-to: 591 Balaltic Rd, Concord ON; Bill-to: 90 Snidercroft Rd, Concord ON |
| MYTOX | Mytox | 251 Aviva Park Drive, Woodbridge ON |
| LAVALTOOL | Laval Tool (Laval Main) | 4965 Concession Rd 8, Maidstone ON |
| METELIX | Metelix | 95 Vankirk Drive, Brampton ON |
| KBCOMP | KB Components | 3786 North Talbot Road, Old Castle ON |
| POLYCON | Polycon Industries (Magna Exteriors) | 65 Independence Place, Guelph ON |

**Part entries needed (~45 unique):**

- **Rollstamp:** 4 BMW G07 RDM parts (9006–9009)
- **Mytox:** 12+ U55X parts (F3LLU103, F3SLU103, F3LLU1A3, etc.)
- **Laval Tool:** 10 parts (99629–99646, 708200448)
- **Metelix:** 13 parts (VG0240BL0PA through VG0241CMOPH + VG0056SP5PA Camaro)
- **KB Components:** 4 parts (P2352, P2369, P2370L, P2370R)
- **Polycon/Tesla:** 2 parts (9405929P MS, 9405930P MX)
- **BRP Spyder (hidden):** 14+ parts (705014522, etc.)

**Supplier entries needed:**

- Nippon Paint (KB Components paint supplier — per tracker)
- GLT International (KB Components tape supplier — per tracker)

---

#### A.5 DispositionCode Coverage

| Form Disposition | Maps To | Code | Notes |
|-----------------|---------|------|-------|
| GOOD / TOTAL GOOD | N/A (accepted) | — | Not a disposition — acceptance |
| REQUIRES BUFFING | REWORK | REWORK | Minor defect, buffing rework |
| REQUIRES SANDING AND REPAINTING | RECOAT | RECOAT | Major defect, strip/sand and recoat |
| MOLDING DEFECT / EXTRUSION DEFECT / SUBSTRATE | Return-to-Supplier | RTS | Incoming material defect |
| SCRAP (Rollstamp, Mytox) | Scrap | SCRAP | Final disposition |
| RETURN TO BUFF (buff forms) | REWORK | REWORK | Re-rework loop |
| SEND TO REWORK (Metelix buff) | RECOAT | RECOAT | Escalated from buff to full rework |
| RW HIT (Metelix Hummer/Y2XX) | REWORK | REWORK | Generic "was reworked" flag — no sub-code |

**Gap:** No form uses Use-As-Is, Sort, Strip-and-Recoat (as distinct from Recoat), Customer-Deviation, Engineering-Deviation, Pending-Customer-Decision, or Blend. This means either: (a) these dispositions don't apply to Plant 2 liquid paint (unlikely — Use-As-Is and Customer-Deviation should occur), or (b) these dispositions happen verbally/informally without documentation (much more likely).

---

### B. API IMPACT

#### B.1 Inspection Record Endpoints Needed

| Endpoint | Method | Purpose | Priority |
|----------|--------|---------|----------|
| `/v1/inspection` | POST | Create inspection record with defect counts | CRITICAL |
| `/v1/inspection/{id}` | GET | Retrieve inspection record with child defect counts | CRITICAL |
| `/v1/inspection/{id}` | PUT | Update inspection record (corrections) | HIGH |
| `/v1/inspection/queue` | GET | Operational queue: open inspections by line/shift/customer | CRITICAL |
| `/v1/inspection/{id}/escalate` | POST | Escalate to NCR (creates NCR linked to inspection) | CRITICAL |
| `/v1/inspection/{id}/defects` | POST | Upsert defect counts (batch operation) | HIGH |
| `/v1/inspection/gate-alarm-report` | GET | Gate alarm trigger summary by customer/date range | HIGH |
| `/v1/inspection/ftq` | GET | First-time quality: Good / (Good + Buff + Repaint + Scrap) | HIGH |
| `/v1/inspection/customer-profile/{customerId}` | GET | Get defect configuration for customer inspection form | HIGH |
| `/v1/inspection/customer-profile` | POST | Configure customer inspection profile | MEDIUM |

**Critical new pattern: `/v1/inspection/{id}/escalate`** — This endpoint does not exist conceptually in the current API. It needs to:

1. Validate gate alarm threshold breach or manual trigger
2. Create a new NCR via `CreateNcrQuick` with auto-populated fields from InspectionRecord
3. Link NCR back to InspectionRecord
4. Set NCR `DetectionProcessAreaId` to the inspection stage
5. Populate `QuantityAffected`, `CustomerId`, `PartId`, `PlantId` from inspection context

> This is the bridge that closes **Gap 2 (Inspection-to-NCR).**

---

#### B.2 Shipping/Receiving Endpoints Needed

| Endpoint | Method | Purpose | Priority |
|----------|--------|---------|----------|
| `/v1/packslip` | POST | Create pack slip with line items | MEDIUM |
| `/v1/packslip/{id}` | GET | Retrieve pack slip with line items | MEDIUM |
| `/v1/packslip/{id}/quality-release` | POST | Quality release sign-off for shipment | HIGH |
| `/v1/receiving` | POST | Log receiving entry | MEDIUM |
| `/v1/receiving/{id}/reject` | POST | Reject inbound with reason → optional SCAR trigger | HIGH |
| `/v1/rma` | POST | Create RMA from customer return | HIGH |
| `/v1/rma/{id}` | GET | Retrieve RMA with line items | MEDIUM |
| `/v1/rma/{id}/link-ncr` | POST | Link RMA to NCR for investigation | HIGH |

---

#### B.3 GP-12 Containment Endpoints

| Endpoint | Method | Purpose | Priority |
|----------|--------|---------|----------|
| `/v1/gp12` | POST | Initiate GP-12 containment event (linked to NCR) | HIGH |
| `/v1/gp12/{id}` | GET/PUT | Retrieve/update GP-12 event | HIGH |
| `/v1/gp12/{id}/close` | POST | Close GP-12 with exit criteria documentation | HIGH |
| `/v1/gp12/active` | GET | List active GP-12 events across plant | HIGH |

The existing `NcrContainmentAction` endpoint covers generic containment but lacks GP-12-specific metadata (entry/exit criteria, inspection frequency, sample size, time limit). GP-12 needs its own lifecycle rather than being shoehorned into `NcrContainmentAction`.

---

#### B.4 Query/Reporting Endpoints

| Endpoint | Method | Purpose | Source Form |
|----------|--------|---------|-------------|
| `/v1/reports/delivery-performance` | GET | OTD % by customer by week/month | 8.2.2.4.5 |
| `/v1/reports/customer-rppm` | GET | Customer return PPM by month | 8.2.2.4.4 |
| `/v1/reports/shipping-summary` | GET | Daily/monthly shipping volumes | 8.2.2.4.3 |
| `/v1/reports/inspection-pareto` | GET | Defect Pareto by customer/part/period | All inspection forms |
| `/v1/reports/gate-alarm-history` | GET | Gate alarm trigger log | All inspection forms with alarms |

---

### C. FRONTEND / UI IMPACT

#### C.1 Screen Inventory

| Screen | Source Forms | Consolidation | Priority |
|--------|-------------|---------------|----------|
| **Inspection Entry** | All 16 customer inspection forms (8.2.2.3.*) | Single screen with CustomerInspectionProfile-driven dynamic defect checklist. Customer + Part selection drives which defect rows appear with correct gate alarm thresholds. Supports PAINT, BUFF, GP12, PRE_PAINT types via tab/toggle. | CRITICAL |
| **Inspection Queue** | New (no paper equivalent) | Open inspections by line/shift with gate alarm status indicators. Escalate-to-NCR action button. | CRITICAL |
| **GP-12 Dashboard** | 8.2.2.3.7.3 (Tesla GP12) + new | Active GP-12 events with entry/exit criteria, days active, inspection results trend, closure workflow. | HIGH |
| **Pack Slip Creator** | 7 pack slip templates (8.2.2.4.*) | Single form: customer selection auto-fills address, part catalog. Quality release gate integrated (cannot generate pack slip without quality release sign-off). | MEDIUM |
| **Receiving Log** | 8.2.2.4.1 | Simple intake form with structured reject reason and SCAR trigger button. | MEDIUM |
| **RMA Tracker** | 8.2.2.4.20/RMA (Metelix only currently) | RMA creation → NCR linkage → disposition tracking. Expand from Metelix-only to all customers. | HIGH |
| **Delivery Performance Dashboard** | 8.2.2.4.4 + 8.2.2.4.5 | Customer OTD %, RPPM trending, shipped vs due by week. | MEDIUM |
| **Inspection Analytics** | All inspection forms | FTQ by customer/line/part, defect Pareto, gate alarm frequency, buff-to-repaint ratio trending. | HIGH |

---

#### C.2 Form Consolidation Map (UI Impact)

| UI Component | Replaces | Consolidation Tier |
|-------------|----------|--------------------|
| Dynamic Inspection Form | 10 customer inspection forms (Tier 1+2 consolidated) | Single component, profile-driven |
| Dynamic Buff Inspection Form | 4 customer buff forms | Single component, profile-driven |
| Metelix Hummer/Y2XX Carrier Inspection | 2 Metelix per-carrier forms | Tier 3 — dedicated, carrier-level detail |
| Metelix Application Tracker | 1 hybrid process+quality form | Tier 3 — unique, combines spray params + inspection |
| Metelix Moulding-Sanding | 1 pre-paint inspection form | Tier 3 — unique purpose, different lifecycle stage |
| GP-12 Inspection + Management | 1 Tesla GP12 form + new management | Tier 3 — regulatory significance, needs full lifecycle |
| Pack Slip Generator | 7 pack slip templates | Tier 1 — one template |
| Customer Tracker View | 4 customer trackers | Read-only dashboard consuming ERP data, not replicated |

**Net UI screens: 8 screens replace 31 forms (74% reduction in screen count).** The key architectural decision: inspection forms collapse to 2–3 dynamic screens driven by CustomerInspectionProfile configuration, not hard-coded per customer.

---

#### C.3 Workflow UX Patterns

| Workflow | Trigger | Steps | Approval |
|----------|---------|-------|----------|
| **Inspection → NCR Escalation** | Gate alarm breach OR manual trigger | 1. Inspector marks defect counts → 2. System detects gate alarm breach → 3. Auto-drafts NCR with inspection context → 4. Quality lead reviews/submits NCR | Quality Lead approval required to submit NCR |
| **Inspection → Shipping Release** | All parts inspected for shipment batch | 1. Inspector completes inspection → 2. Disposition summary (Good/Buff/Repaint/Scrap) → 3. Quality lead reviews and signs quality release → 4. Pack slip generation enabled | Quality Lead sign-off required before pack slip |
| **Receiving → SCAR** | Incoming material rejected | 1. Receiver marks Reject → 2. Enters reject reason code → 3. System offers SCAR creation → 4. SCAR auto-populated with supplier/PO/defect | Quality Engineer initiates SCAR |
| **Customer Return → RMA → NCR** | Customer return received | 1. RMA created with part/qty/condition → 2. Linked to NCR for investigation → 3. Root cause → CAPA if warranted | Quality Manager approval |
| **GP-12 Lifecycle** | NCR triggers containment requirement | 1. GP-12 initiated from NCR → 2. Entry criteria documented → 3. Escalated inspection frequency begins → 4. Daily results tracked → 5. Exit criteria met → 6. Closure with evidence | Customer notification required at entry and exit |

---

#### C.4 Dashboard Data Sources

| KPI | Calculation | Source | Currently Available? |
|-----|-------------|--------|---------------------|
| First-Time Quality (FTQ) | TotalGood / (TotalGood + TotalBuff + TotalRepaint + TotalScrap) | InspectionRecord | **NO** — no TotalInspected denominator on forms |
| Customer RPPM | Returns / Shipped × 1,000,000 | Monthly Totals (8.2.2.4.4) | **PARTIAL** — exists on paper, no system calculation |
| On-Time Delivery % | Shipped / Due × 100 | Delivery Performance (8.2.2.4.5) | **PARTIAL** — manual entry, not linked to actual releases |
| Gate Alarm Frequency | Count of inspections where alarm threshold breached | InspectionDefectCount | **NO** — gate alarms on paper only |
| Inspection-to-NCR Rate | NCRs created / Inspections performed | InspectionRecord + NCR | **NO** — currently 0% (no NCRs from inspection) |
| Buff Recirculation Rate | Return-to-Buff count / Total Buff inspected | Buff InspectionRecord | **NO** — no linkage between paint and buff inspection |
| Scrap Rate | TotalScrap / TotalInspected | InspectionRecord | **NO** — only Rollstamp and Mytox track scrap |
| Cost of Poor Quality | Σ(scrap cost + rework cost + customer chargebacks) | NCR.EstimatedCost + RMA | **NO** — no cost data captured |

---

## 6. Consolidated Plant 2 Assessment

### 6.1 Overall Plant 2 Readiness Score

| Dimension | Weight | Part A Score | Part B Score | Weighted Score |
|-----------|--------|-------------|-------------|----------------|
| Data Completeness | 20% | 25/100 | 20/100 | 4.5 |
| Traceability | 25% | 20/100 | 23/100 | 5.4 |
| Defect Management | 20% | 15/100 | 30/100 | 4.5 |
| Process Control Linkage | 15% | 35/100 | 10/100 | 3.4 |
| Document Control | 10% | 20/100 | 15/100 | 1.8 |
| Shipping/Customer Interface | 10% | N/A | 25/100 | 2.5 |
| **TOTAL** | **100%** | | | **22.1 → 22/100** |

> **Plant 2 Combined Readiness: 25/100** (averaging Part A's 28 and Part B's 22, with Part B weighted slightly higher due to customer-facing criticality).

---

### 6.2 Plant 2 vs Plant 1 Comparison

| Dimension | Plant 1 (30/100) | Plant 2 (25/100) | Notes |
|-----------|-------------------|-------------------|-------|
| NCR System | None | None | Universal — confirmed across 2 plants |
| Traceability | Broken (~20%) | Broken (~23%) | Plant 2 marginally better due to Metelix carrier tracking and customer trackers |
| Defect Vocabulary | 97 strings → 38 types | 42 strings → 28 types (+ 10 Part A) | Plant 1 has more volume but lower signal; Plant 2 is cleaner but has gaps (dry spray, colour, gloss) |
| Form Consolidation | 80%+ Tier 2 candidates | 42% reduction (10 Tier 1+2, 13 Tier 3) | Plant 2 has more genuinely unique forms due to Metelix complexity |
| GP-12 | Per-customer, no entry/exit | Tesla only, no entry/exit | Same gap, less coverage in Plant 2 |
| Process-Quality Bridge | None | 1 form (Metelix Application Tracker) | Plant 2 slightly better — one form bridges the gap |
| Shipping-Quality Gate | None | None | Universal — confirmed across 2 plants |
| Customer Tracker Maturity | Unknown | High (4 trackers with MRP/waterfall/RMA) | Plant 2's logistics tools are more sophisticated |
| Post-Paint Tracking | Labour-only tally sheets | Same + dedicated buff inspection per customer | Plant 2 has more inspection rigor at buff stage |
| Cost Visibility | None | Near-none (Metelix RMA qty only) | Both plants blind |
| Revision Control | Minimal | 2 of 31 forms (Tesla only) | Universal gap |

---

### 6.3 Confirmed Cross-Plant Universal Patterns

Extends Plant 1 findings, now confirmed across 2 of 7 plants:

1. **No NCR system.** Zero NCR forms, zero NCR references, zero escalation pathways. This is organizational, not plant-specific.
2. **Broken traceability chain.** Internal chain (receipt → production → inspection → shipping) broken at every link in both plants.
3. **No shipping-quality gate.** Parts can be shipped without documented quality release in both plants.
4. **Customer forms are relabeled copies.** KB Components tabs still named "Laval Tool." Misc Customers is a generic template. Daily Shipping Report Dec tab says "Laval" while Jan–Nov say "Metelix." Copy-paste form creation is standard practice.
5. **GP-12 is form-only, not process.** Both plants have GP-12 forms with zero lifecycle elements (entry/exit criteria, time limits, closure gates).
6. **Gate alarms are paper annotations, not system controls.** Thresholds are printed in column headers. No calculation, no alert, no escalation mechanism.
7. **No supervisor sign-off on inspection.** Zero of 16+ customer inspection forms (either plant) have management approval fields.
8. **No test method references.** No adhesion, film build, gloss, or colour checks referenced on any customer inspection form despite being standard requirements for automotive coating.
9. **Defect taxonomy is customer-siloed.** Each customer's form was built independently with different defect names, different granularity, and different category structures.
10. **Post-paint rework cycles are uncounted.** No linkage between paint inspection (disposition: buff) and buff inspection (re-checking same parts). Cannot calculate rework loop frequency.

---

### 6.4 Plant 2-Specific Patterns

1. **Metelix drives sophistication.** 6 of 16 inspection forms and the most detailed tracker (9 sheets with RMA/Recovery) are Metelix. Without Metelix, Plant 2's quality system would be bare-bones.
2. **BRP/Can-Am Spyder program is hidden.** A full customer inspection form for 14+ BRP Spyder parts is embedded as a secondary sheet tab in the Laval Tool Buff Inspection workbook. This program has no dedicated inspection form, no pack slip, and no tracker.
3. **Metelix Hummer Spoiler Application Tracker is unique to the organization.** It's the only form that captures spray parameters AND inspection results per carrier on the same sheet, bridging the process-quality disconnect for one product.
4. **Customer tracker ecosystem is mature.** Four customers have multi-sheet trackers with MRP, release waterfall, and receiving/shipping. Plant 1's equivalent (if any) was not documented at this level.
5. **Liquid paint-specific defects are underrepresented.** Dry spray, colour mismatch, and gloss failure are absent from every form. Fish Eye and Solvent Pop appear only on Metelix Hummer/Y2XX and Tesla GP12 respectively.
6. **Monthly Totals reveals scope drift.** Sheet2 lists 35 historical customers vs 6 active in Part B — many customers have left or been consolidated without form cleanup.

---

### 6.5 Complete Entity Proposal Summary (Merged Part A + Part B)

| # | Entity | Schema | Priority | Source | Part |
|---|--------|--------|----------|--------|------|
| 1 | InspectionRecord | quality | CRITICAL | 16 inspection forms | B |
| 2 | InspectionDefectCount | quality | CRITICAL | Child of InspectionRecord | B |
| 3 | CustomerInspectionProfile | quality | HIGH | Configuration for dynamic forms | B |
| 4 | Gp12ContainmentEvent | quality | HIGH | Tesla GP12 + organizational need | B |
| 5 | ProductionRun | production | CRITICAL | 5 production forms | A |
| 6 | ProductionRunCarrier | production | HIGH | 3 carrier-level forms | A |
| 7 | PaintBatch | production | HIGH | 4 paint mix forms | A |
| 8 | ColourVerification | production | HIGH | 1 colour verification form | A |
| 9 | MaintenanceRecord | production | MEDIUM | 10 maintenance forms | A |
| 10 | DowntimeEvent | production | MEDIUM | 2 downtime forms | A |
| 11 | PostPaintOperation | production | MEDIUM | 4 post-paint forms | A |
| 12 | PostPaintDailySummary | production | LOW | 1 summary form | A |
| 13 | WasteRecord | production | LOW | 5 drum labels (net-new) | A |
| 14 | PaintTrial | production | LOW | 2 trial forms | A |
| 15 | PackSlip + PackSlipLineItem | logistics | MEDIUM | 7 pack slip templates | B |
| 16 | ReceivingLogEntry | logistics | MEDIUM | 1 receiving log | B |
| 17 | ReturnMaterialAuthorization + RmaLineItem | logistics | MEDIUM | 1 Metelix RMA sheet | B |

**Total:** 17 new entities (+ 4 child entities) across 3 schemas. Estimated: 25–30 migrations, 40–50 stored procedures, 35+ new API endpoints.

---

### 6.6 Complete Defect Taxonomy

Deferred to Appendix A (Batch B5) — full merged table with 35 leaf entries.

---

### 6.7 Normalization Recommendations for Plants 3–7

Based on confirmed universal patterns from Plants 1 and 2, auditors should focus on:

1. **Count customer inspection forms and extract defect lists immediately.** This is the highest-value activity. Expect 8–20 customer-specific forms per plant with 40–100 unique defect strings.
2. **Check for hidden customer programs in secondary sheet tabs.** Plant 2 had BRP hidden in a Laval Tool file. Look for mismatched tab names vs file names.
3. **Verify GP-12 existence per OEM customer.** Any plant serving GM, Ford, Toyota, or BMW should have GP-12 forms. Their absence is a finding.
4. **Look for hybrid process+quality forms.** The Metelix Application Tracker pattern may exist for high-value programs at other plants. These are the most valuable forms for platform design.
5. **Check pack slips for quality release fields.** Expect to find none — but document the absence.
6. **Check for RMA/returns tracking.** Metelix is the only customer with structured return tracking. This is likely a gap at every plant.
7. **Check for customer tracker maturity.** If other plants have MRP/waterfall trackers, they contain part master data and demand signals useful for platform integration.
8. **Line type variation:** Plants 3–7 include powder coat, e-coat, anodize, and mechanical finishing. Defect taxonomies will diverge significantly. Powder coat will not have runs/sags/solvent pop; e-coat will have different failure modes (poor throwing power, cratering, pinholing). The DefectType-to-LineType junction table will be heavily used.
9. **Process parameter forms will vary by line type.** Plant 2's liquid spray parameters (fluid/atomization/fan pressure) will not apply to powder (kV, film build targets) or e-coat (voltage, amperage, bath chemistry). The ProductionRunCarrier entity needs line-type-flexible parameter storage.
10. **Expect 30–40% form reduction per plant** through consolidation, scaling to 50%+ as the configurable digital templates mature.
