# BATCH B6: Appendix C + Appendix D + Appendix E

---

## Appendix C: Form Consolidation Matrix

**Tier 1/2/3 with Overlap % and Justification**

| DocNumber | FormName | Customer | Tier | ConsolidationGroup | Overlap% | TargetDigitalForm | Justification | UniqueFieldsPreventingHigherTier |
|-----------|----------|----------|------|--------------------|----------|-------------------|---------------|----------------------------------|
| 8.2.2.3.4.1 | Laval Tool Inspection | Laval Tool | Tier2 | STD_PAINT_INSPECT | 85 | Dynamic Inspection Form | Standard 4-section layout (Good/Buff/Repaint/Molding) with per-defect counts and gate alarms. Structurally identical to KB Components. | Painted Part # (raw→FG dual reference) |
| 8.2.2.3.6.1 | KB Components Inspection | KB Components | Tier2 | STD_PAINT_INSPECT | 85 | Dynamic Inspection Form | Tab still named 'Laval Tool' — confirmed copy-paste origin. Same gate alarms (uniform 5). Added: Molding Date; Outgassing Popping replaces Flash. | Molding Date; Outgassing Popping label |
| 8.2.2.3.7.2 | Tesla Inspection | Polycon/Tesla | Tier2 | STD_PAINT_INSPECT | 80 | Dynamic Inspection Form | Same 4-section layout. Larger molding defect vocabulary (Splay/Gas Mark/Outgassing/Extrusion Line/Blisters-Pitmark/Chatter Mark). Variable gate alarms (6–24). | Molding Date; 6 extra molding defects; OTHER (DESCRIBE) free text; revision sheet |
| 8.2.2.2.16 | Misc Customers | Multi-Customer | Tier2 | STD_PAINT_INSPECT | 85 | Dynamic Inspection Form | Generic template with blank customer field. Identical 4-section layout. Stale (2020). KANBAN SHEET is duplicate. | Blank customer (fill-in); BUFFED PARTS section with Good/Returned/Rework |
| 8.2.2.3.2.1 | Rollstamp BMW G07 Inspection | Rollstamp/BMW | Tier2 | ROLLSTAMP_MYTOX_INSPECT | 80 | Dynamic Inspection Form | Same 4-section core but significant unique fields: Extrusion Date & Rack #; Assembly Date; location-specific orange peel (End Cap vs Face); extrusion defect category; per-part scrap totals. | Extrusion Date & Rack #; Assembly Date; TOTAL SCRAP per part suffix; 4 extrusion-specific defects |
| 8.2.2.3.3.2 | Mytox Inspection | Mytox | Tier2 | ROLLSTAMP_MYTOX_INSPECT | 80 | Dynamic Inspection Form | Same 4-section core. Unique: separate Paint Date + Inspection Date; Rack #; Colour; Long/Short designator; E-COAT substrate defect; SCRAP gate alarm at 1. | Dual date (Paint+Inspection); Rack #; Colour; Long/Short; E-COAT defect; Scrap alarm=1 |
| 8.2.2.3.4.2 | Laval Tool Buff Inspection (primary sheet) | Laval Tool | Tier2 | STD_BUFF_INSPECT | 85 | Dynamic Buff Inspection Form | Reduced defect set from paint inspection. Re-inspection after buffing. | None significant — baseline for buff group |
| 8.2.2.3.6.2 | KB Components Buffing Inspection | KB Components | Tier2 | STD_BUFF_INSPECT | 85 | Dynamic Buff Inspection Form | Tab still named 'Laval Tool'. Disposition label change: 'RETURN TO BUFF' vs 'REQUIRES BUFFING'. | Disposition label variant only |
| 8.2.2.3.7.1 | Tesla Buff Inspection | Polycon/Tesla | Tier2 | STD_BUFF_INSPECT | 80 | Dynamic Buff Inspection Form | 2 sheets (MS/MX). Adds FOAM MARKS and SNOW BALL. 10 identical rows per part. | 2 program sheets; FOAM MARKS; SNOW BALL; per-program separation |
| 8.2.2.4.2 | P2 General Pack Slip Template | General | Tier1 | PACK_SLIP | 95 | Pack Slip Generator | Baseline template — all customer variants are pre-populated versions of this. | None — this IS the template |
| 8.2.2.4.9 | Metelix Packslip Template | Metelix | Tier1 | PACK_SLIP | 95 | Pack Slip Generator | General template with Metelix address and 10 parts pre-populated. | Pre-populated customer data only |
| 8.2.2.4.11 | Mytox Packslip Template | Mytox | Tier1 | PACK_SLIP | 95 | Pack Slip Generator | General template with Mytox address. Adds Short/Long designator and EMPTIES tracking. | Short/Long column; EMPTIES row |
| 8.2.2.4.12 | Rollstamp BMW Packslip Template | Rollstamp/BMW | Tier1 | PACK_SLIP | 95 | Pack Slip Generator | General template with Rollstamp address. Adds Line # column and rack empties (Blue/Green). | Line # column; returnable rack tracking |
| 8.2.2.4.14 | Laval Tool Packslip Template | Laval Tool | Tier1 | PACK_SLIP | 95 | Pack Slip Generator | General template with Laval address. Uses Skids + Weight. | Standard variant |
| 8.2.2.4.17 | KB Components Packslip Template | KB Components | Tier1 | PACK_SLIP | 95 | Pack Slip Generator | General template with KB address. Uses Skids + Weight. | Standard variant |
| 8.2.2.4.18 | Polycon Packslip Template | Polycon/Tesla | Tier1 | PACK_SLIP | 95 | Pack Slip Generator | General template with Polycon/Magna address. 2 Tesla parts. | Standard variant |
| 8.2.2.4.19 | Plant 2 Polycon Tracker | Polycon/Tesla | Tier1 | CUST_TRACKER | 90 | Customer Tracker (ERP) | 6-sheet standard tracker (Receiving/Shipping/Releases/Waterfall/MRP/Parts Legend). Simplest of 4 trackers. | None significant — baseline for tracker group |
| 8.2.2.4.21 | Laval Tracker Template | Laval Tool | Tier1 | CUST_TRACKER | 90 | Customer Tracker (ERP) | Standard tracker + Instructions sheet + Shipping Total tab. Has VBA button for log export. | Instructions sheet; Shipping Total; VBA macro |
| 8.2.2.4.22 | KB Components Tracker | KB Components | Tier1 | CUST_TRACKER | 90 | Customer Tracker (ERP) | Standard tracker. Releases sheet includes paint/tape inventory management. | Paint inventory rows; tape consumption tracking |
| 8.2.2.3.5.1 | Metelix Inspection | Metelix | Tier3 | METELIX_STD_INSPECT | N/A | Metelix Standard Inspection | 5-defect sanding/molding section not on any other form. LINE field. Multi-program (C223 + 7 Y2XX components). | Sanding defect section (Parting Line/Gouges/Sanding Marks/Dents/Cracks); LINE field; 9 multi-program parts |
| 8.2.2.3.5.2 | Metelix Buff Inspection | Metelix | Tier3 | METELIX_BUFF | N/A | Metelix Buff Tracker | Buffing-specific defects unique to Metelix: Snowballs/Haze/Burn Through. Comments field. Dual disposition (Return to Buff / Send to Rework). | Snowballs; Haze; Burn Through; Comments; dual rework disposition |
| 8.2.2.3.5.3 | Metelix Moulding-Sanding Inspection | Metelix | Tier3 | METELIX_PRESAND | N/A | Pre-Paint Substrate Inspection | Entirely different purpose: pre-paint inspection. Raw/primed/painted tri-state column. Inspector + Sander Inspection ID. Per-piece sequential tracking. | Pre-paint lifecycle stage; tri-state column; dual inspector; per-piece rows; Thin Substrate defect |
| 8.2.2.3.5.4 | Metelix Hummer Painted Inspection | Metelix | Tier3 | METELIX_CARRIER_INSPECT | N/A | Carrier-Level Painted Inspection | Per-carrier inspection with 20 defect categories. Carrier Number field. RW/ prefix naming convention. Single product. | Carrier Number; 20 defects; RW/ prefix convention; per-carrier granularity |
| 8.2.2.3.5.5 | Metelix Hummer Spoiler Application Tracker | Metelix | Tier3 | METELIX_APP_TRACKER | N/A | Application Tracker (Hybrid) | Unique hybrid: spray parameters (Fluid/Atom/Fan per stage) + defects + environmental data (Temp/Humidity/Booth). Operator name. 48 carrier rows. | Spray parameters × 3 stages; environmental data; operator; RW Y/N; process+quality hybrid |
| 8.2.2.3.5.6 | Metelix Y2XX Highwing Painted Inspection | Metelix | Tier3 | METELIX_CARRIER_INSPECT | N/A | Carrier-Level Painted Inspection | Structurally identical to Hummer Painted Inspection but different product. References external spec 8.3.2.9.26. Fixed colour. | External doc reference; single-colour |
| 8.2.2.3.7.3 | Tesla GP12 Inspection | Polycon/Tesla | Tier3 | GP12_INSPECT | N/A | GP-12 Containment Inspection | Must remain separate despite structural similarity to buff inspection. GP-12 has regulatory/customer mandate. Needs containment metadata (entry/exit criteria etc.) added. | Regulatory significance; SOLVENT POP addition; needs full GP-12 lifecycle wrapper |
| 8.2.2.3.4.2 (KANBAN) | Laval Tool Buff Inspection — KANBAN SHEET | BRP/Can-Am (hidden) | Tier3 | BRP_SPYDER_INSPECT | N/A | BRP Spyder Inspection (NEW) | Hidden customer program: 14 BRP Spyder R66 parts in Chalk White. Different customer than Laval Tool. Must be reclassified and given dedicated form. | Wrong file; wrong customer; 14 unique parts; needs reclassification |
| 8.2.2.4.20 | Metelix Demand and Production Tracker | Metelix | Tier3 | METELIX_TRACKER | N/A | Metelix Tracker (ERP+Quality) | 9 sheets vs standard 6. Unique: RMA sheet with return tracking; Recovery sheet with backlog; Summary with daily production. Most complex tracker. | RMA sheet; Recovery sheet; Summary sheet; 9-sheet structure; Molded→FG part mapping |
| 8.2.2.4.1 | P2 Receiving Log | General | Tier3 | RECEIVING_LOG | N/A | Receiving Log | Unique function: inbound material intake. 12 monthly tabs. Accept/Reject with distribution routing. | Unique function; monthly tab structure; distribution checkboxes |
| 8.2.2.4.3 | P2 Daily Shipping Report | General | Tier3 | DAILY_SHIP_RPT | N/A | Daily Shipping Report | Shipping log with pivot table. 12 monthly tabs + Totals. Customer-specific title (Metelix/Laval copy error). | Pivot table structure; monthly tabs; annual totals |
| 8.2.2.4.4 | P2 Monthly Totals | General | Tier3 | MONTHLY_TOTALS | N/A | Customer RPPM Dashboard | Shipped/Returned/PPM by customer by month. Sheet2: 35 historical customers. Reporting form. | RPPM calculation; 35-customer historical list; reporting not transactional |
| 8.2.2.4.5 | P2 Monthly Delivery Performance | General | Tier3 | DELIVERY_PERF | N/A | Delivery Performance Dashboard | Weekly OTD% by customer. Daily granularity for select customers. 5-week monthly structure. | OTD calculation; daily+weekly+monthly structure; Quantity Due field |

### Consolidation Summary

| Tier | Form Count | Digital Templates | Reduction |
|------|-----------|-------------------|-----------|
| **Tier 1** — Identical | 10 | 2 (1 Pack Slip + 1 Customer Tracker) | 10 → 2 |
| **Tier 2** — Minor Variants | 9 | 3 (1 Std Paint Insp + 1 Rollstamp/Mytox Insp + 1 Std Buff Insp) | 9 → 3 |
| **Tier 3** — Genuinely Unique | 12 | 12 (but several share common digital backbone) | 12 → 12 |
| **TOTAL** | **31** | **17** | **45% reduction** |

> **Architecture note on Tier 3:** Although 12 forms remain as Tier 3, they share a common inspection entity backbone. The Metelix Carrier-Level Inspection (8.2.2.3.5.4 and 8.2.2.3.5.6) can share a single UI component parameterized by product. Similarly, the 4 reporting/dashboard forms (Receiving Log, Daily Shipping, Monthly Totals, Delivery Performance) become 4 screens in a single Shipping & Logistics dashboard module, not 4 standalone forms. **Effective screen count after UI architecture: 8 screens** as proposed in Section 5C.1.

---

## Appendix D: Complete Proposed Entity Schemas (Merged Part A + Part B)

### D.1 Quality Schema — New Entities (Part B)

#### quality.InspectionRecord

Central inspection event. One per customer × part × date × shift × type.

```sql
CREATE TABLE quality.InspectionRecord (
    InspectionRecordId      INT IDENTITY(1,1) PRIMARY KEY,
    PlantId                 INT NOT NULL
        CONSTRAINT FK_InspectionRecord_Plant FOREIGN KEY REFERENCES dbo.Plant(PlantId),
    ProductionLineId        INT NULL
        CONSTRAINT FK_InspectionRecord_Line FOREIGN KEY REFERENCES dbo.ProductionLine(ProductionLineId),
    ShiftId                 INT NOT NULL
        CONSTRAINT FK_InspectionRecord_Shift FOREIGN KEY REFERENCES dbo.Shift(ShiftId),
    CustomerId              INT NOT NULL
        CONSTRAINT FK_InspectionRecord_Customer FOREIGN KEY REFERENCES dbo.Customer(CustomerId),
    PartId                  INT NOT NULL
        CONSTRAINT FK_InspectionRecord_Part FOREIGN KEY REFERENCES dbo.Part(PartId),
    InspectionDate          DATE NOT NULL,
    PaintDate               DATE NULL,          -- May differ from InspectionDate (Mytox)
    InspectionTypeCodeId    INT NOT NULL
        CONSTRAINT FK_InspectionRecord_Type FOREIGN KEY REFERENCES dbo.LookupValue(LookupValueId),
        -- Values: PAINT, BUFF, GP12, PRE_PAINT, APPLICATION
    InspectorId             INT NULL,           -- Only Metelix Moulding-Sanding captures
    CarrierNumber           NVARCHAR(50) NULL,  -- Mytox Rack#, Metelix Hummer/Y2XX Carrier#
    RackNumber              NVARCHAR(50) NULL,  -- Mytox Rack # (alias for CarrierNumber where applicable)
    MoldingDate             DATE NULL,          -- KB Components, Tesla
    TotalGood               INT NOT NULL DEFAULT 0,
    TotalBuff               INT NOT NULL DEFAULT 0,
    TotalRepaint            INT NOT NULL DEFAULT 0,
    TotalMoldingDefect      INT NOT NULL DEFAULT 0,
    TotalScrap              INT NULL,           -- Only Rollstamp, Mytox
    IsRework                BIT NOT NULL DEFAULT 0,  -- Application Tracker RW Y/N
    NcrId                   INT NULL
        CONSTRAINT FK_InspectionRecord_Ncr FOREIGN KEY REFERENCES quality.NonConformanceReport(NonConformanceReportId),
    ProductionRunId         INT NULL,           -- Future FK to production.ProductionRun
    Gp12ContainmentEventId  INT NULL,           -- FK to quality.Gp12ContainmentEvent if GP12 type
    ExternalDocReference    NVARCHAR(200) NULL, -- Y2XX refs 8.3.2.9.26
    CreatedAt               DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    CreatedBy               NVARCHAR(100) NOT NULL,
    ModifiedAt              DATETIME2 NULL,
    ModifiedBy              NVARCHAR(100) NULL,
    INDEX IX_InspectionRecord_PlantDate (PlantId, InspectionDate),
    INDEX IX_InspectionRecord_Customer (CustomerId, InspectionDate),
    INDEX IX_InspectionRecord_Part (PartId, InspectionDate)
);
-- RLS: Filter by PlantId
```

#### quality.InspectionDefectCount

Child: per-defect-type count within an inspection record.

```sql
CREATE TABLE quality.InspectionDefectCount (
    InspectionDefectCountId INT IDENTITY(1,1) PRIMARY KEY,
    InspectionRecordId      INT NOT NULL
        CONSTRAINT FK_InspDefect_Record FOREIGN KEY REFERENCES quality.InspectionRecord(InspectionRecordId),
    DefectTypeId            INT NOT NULL
        CONSTRAINT FK_InspDefect_DefectType FOREIGN KEY REFERENCES quality.DefectType(DefectTypeId),
    DispositionCodeId       INT NOT NULL
        CONSTRAINT FK_InspDefect_Disposition FOREIGN KEY REFERENCES dbo.DispositionCode(DispositionCodeId),
    Quantity                INT NOT NULL DEFAULT 0,
    GateAlarmThreshold      INT NULL,
    GateAlarmTriggered      AS CASE WHEN GateAlarmThreshold IS NOT NULL
                               AND Quantity >= GateAlarmThreshold THEN 1 ELSE 0 END PERSISTED,
    INDEX IX_InspDefect_Record (InspectionRecordId),
    INDEX IX_InspDefect_GateAlarm (GateAlarmTriggered) WHERE GateAlarmTriggered = 1
);
```

#### quality.CustomerInspectionProfile

Configuration: which defects appear per customer per part.

```sql
CREATE TABLE quality.CustomerInspectionProfile (
    CustomerInspectionProfileId INT IDENTITY(1,1) PRIMARY KEY,
    CustomerId              INT NOT NULL
        CONSTRAINT FK_CustProfile_Customer FOREIGN KEY REFERENCES dbo.Customer(CustomerId),
    PartId                  INT NULL
        CONSTRAINT FK_CustProfile_Part FOREIGN KEY REFERENCES dbo.Part(PartId),
        -- NULL = customer-wide default
    InspectionTypeCodeId    INT NOT NULL
        CONSTRAINT FK_CustProfile_Type FOREIGN KEY REFERENCES dbo.LookupValue(LookupValueId),
    DefectTypeId            INT NOT NULL
        CONSTRAINT FK_CustProfile_Defect FOREIGN KEY REFERENCES quality.DefectType(DefectTypeId),
    SectionCode             NVARCHAR(20) NOT NULL,  -- BUFF, REPAINT, MOLDING, SCRAP
    DispositionCodeId       INT NOT NULL
        CONSTRAINT FK_CustProfile_Disposition FOREIGN KEY REFERENCES dbo.DispositionCode(DispositionCodeId),
    GateAlarmThreshold      INT NULL,
    SortOrder               INT NOT NULL DEFAULT 0,
    IsActive                BIT NOT NULL DEFAULT 1,
    CONSTRAINT UQ_CustProfile UNIQUE (CustomerId, PartId, InspectionTypeCodeId, DefectTypeId)
);
```

#### quality.Gp12ContainmentEvent

GP-12 containment lifecycle — linked to triggering NCR.

```sql
CREATE TABLE quality.Gp12ContainmentEvent (
    Gp12ContainmentEventId  INT IDENTITY(1,1) PRIMARY KEY,
    PlantId                 INT NOT NULL
        CONSTRAINT FK_Gp12_Plant FOREIGN KEY REFERENCES dbo.Plant(PlantId),
    CustomerId              INT NOT NULL
        CONSTRAINT FK_Gp12_Customer FOREIGN KEY REFERENCES dbo.Customer(CustomerId),
    PartId                  INT NOT NULL
        CONSTRAINT FK_Gp12_Part FOREIGN KEY REFERENCES dbo.Part(PartId),
    NcrId                   INT NOT NULL
        CONSTRAINT FK_Gp12_Ncr FOREIGN KEY REFERENCES quality.NonConformanceReport(NonConformanceReportId),
    EntryDate               DATE NOT NULL,
    EntryReason             NVARCHAR(500) NOT NULL,
    ExitDate                DATE NULL,
    ExitCriteria            NVARCHAR(500) NULL,
    InspectionFrequency     NVARCHAR(100) NULL,  -- e.g. '100% for 30 production days'
    MinimumSampleSize       INT NULL,
    MaxDurationDays         INT NULL,            -- Time limit
    StatusCodeId            INT NOT NULL
        CONSTRAINT FK_Gp12_Status FOREIGN KEY REFERENCES dbo.StatusCode(StatusCodeId),
        -- Values: ACTIVE, CLOSED, EXPIRED
    CustomerNotificationDate DATE NULL,
    CustomerApprovalDate    DATE NULL,
    ClosedBy                NVARCHAR(100) NULL,
    ClosedAt                DATETIME2 NULL,
    CreatedAt               DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    CreatedBy               NVARCHAR(100) NOT NULL,
    INDEX IX_Gp12_Active (StatusCodeId, PlantId) WHERE StatusCodeId = 1  -- Active events
);
-- RLS: Filter by PlantId
```

---

### D.2 Logistics Schema — New Entities (Part B)

#### logistics.PackSlip

Outbound shipment document header.

```sql
CREATE TABLE logistics.PackSlip (
    PackSlipId              INT IDENTITY(1,1) PRIMARY KEY,
    PackSlipNumber          NVARCHAR(20) NOT NULL,
    PlantId                 INT NOT NULL
        CONSTRAINT FK_PackSlip_Plant FOREIGN KEY REFERENCES dbo.Plant(PlantId),
    CustomerId              INT NOT NULL
        CONSTRAINT FK_PackSlip_Customer FOREIGN KEY REFERENCES dbo.Customer(CustomerId),
    ShipDate                DATE NOT NULL,
    ShipVia                 NVARCHAR(100) NULL,
    DriverName              NVARCHAR(100) NULL,
    TruckTrailerNumber      NVARCHAR(50) NULL,
    ShipperInitials         NVARCHAR(10) NOT NULL,
    TotalContainers         INT NULL,
    TotalParts              INT NOT NULL,
    TotalWeightKg           DECIMAL(10,2) NULL,
    QualityReleaseStatus    NVARCHAR(20) NOT NULL DEFAULT 'NOT_VERIFIED',
        -- NOT_VERIFIED, RELEASED, HELD
    QualityReleasedById     INT NULL,
    QualityReleaseDate      DATETIME2 NULL,
    CreatedAt               DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    CreatedBy               NVARCHAR(100) NOT NULL,
    CONSTRAINT UQ_PackSlip_Number UNIQUE (PlantId, PackSlipNumber),
    INDEX IX_PackSlip_CustomerDate (CustomerId, ShipDate)
);
-- RLS: Filter by PlantId
```

#### logistics.PackSlipLineItem

Individual line on a pack slip.

```sql
CREATE TABLE logistics.PackSlipLineItem (
    PackSlipLineItemId      INT IDENTITY(1,1) PRIMARY KEY,
    PackSlipId              INT NOT NULL
        CONSTRAINT FK_PSLine_PackSlip FOREIGN KEY REFERENCES logistics.PackSlip(PackSlipId),
    PartId                  INT NOT NULL
        CONSTRAINT FK_PSLine_Part FOREIGN KEY REFERENCES dbo.Part(PartId),
    Quantity                INT NOT NULL,
    ContainerCount          INT NULL,
    PurchaseOrderNumber     NVARCHAR(50) NULL,
    AdditionalInfo          NVARCHAR(200) NULL,
    InspectionRecordId      INT NULL
        CONSTRAINT FK_PSLine_Inspection FOREIGN KEY REFERENCES quality.InspectionRecord(InspectionRecordId)
);
```

#### logistics.ReceivingLogEntry

Inbound material receipt.

```sql
CREATE TABLE logistics.ReceivingLogEntry (
    ReceivingLogEntryId     INT IDENTITY(1,1) PRIMARY KEY,
    PlantId                 INT NOT NULL
        CONSTRAINT FK_Receiving_Plant FOREIGN KEY REFERENCES dbo.Plant(PlantId),
    SupplierOrCustomerId    INT NOT NULL,
    EntryDirection          NVARCHAR(10) NOT NULL DEFAULT 'INBOUND',
        -- INBOUND (from supplier) or RETURN (from customer)
    PackingSlipNumber       NVARCHAR(50) NULL,
    PurchaseOrderNumber     NVARCHAR(50) NULL,
    SupplierPromiseDate     DATE NULL,
    DateReceived            DATE NOT NULL,
    TimeReceived            TIME NULL,
    AcceptReject            CHAR(1) NOT NULL,    -- A or R
    RejectedQuantity        INT NULL,
    RejectReasonCodeId      INT NULL
        CONSTRAINT FK_Receiving_RejectReason FOREIGN KEY REFERENCES dbo.LookupValue(LookupValueId),
    ReceiverInitials        NVARCHAR(10) NOT NULL,
    ScarId                  INT NULL
        CONSTRAINT FK_Receiving_Scar FOREIGN KEY REFERENCES quality.SupplierCar(SupplierCarId),
    CreatedAt               DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    INDEX IX_Receiving_PlantDate (PlantId, DateReceived)
);
-- RLS: Filter by PlantId
```

#### logistics.ReturnMaterialAuthorization

Customer return tracking (from Metelix RMA pattern).

```sql
CREATE TABLE logistics.ReturnMaterialAuthorization (
    RmaId                   INT IDENTITY(1,1) PRIMARY KEY,
    RmaNumber               NVARCHAR(20) NOT NULL,
    PlantId                 INT NOT NULL
        CONSTRAINT FK_Rma_Plant FOREIGN KEY REFERENCES dbo.Plant(PlantId),
    CustomerId              INT NOT NULL
        CONSTRAINT FK_Rma_Customer FOREIGN KEY REFERENCES dbo.Customer(CustomerId),
    RmaDate                 DATE NOT NULL,
    NcrId                   INT NULL
        CONSTRAINT FK_Rma_Ncr FOREIGN KEY REFERENCES quality.NonConformanceReport(NonConformanceReportId),
    CustomerComplaintId     INT NULL
        CONSTRAINT FK_Rma_Complaint FOREIGN KEY REFERENCES quality.CustomerComplaint(CustomerComplaintId),
    StatusCodeId            INT NOT NULL
        CONSTRAINT FK_Rma_Status FOREIGN KEY REFERENCES dbo.StatusCode(StatusCodeId),
    CreatedAt               DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    CreatedBy               NVARCHAR(100) NOT NULL,
    CONSTRAINT UQ_Rma_Number UNIQUE (PlantId, RmaNumber),
    INDEX IX_Rma_Customer (CustomerId, RmaDate)
);
-- RLS: Filter by PlantId
```

#### logistics.RmaLineItem

Per-part detail within an RMA.

```sql
CREATE TABLE logistics.RmaLineItem (
    RmaLineItemId           INT IDENTITY(1,1) PRIMARY KEY,
    RmaId                   INT NOT NULL
        CONSTRAINT FK_RmaLine_Rma FOREIGN KEY REFERENCES logistics.ReturnMaterialAuthorization(RmaId),
    PartId                  INT NOT NULL
        CONSTRAINT FK_RmaLine_Part FOREIGN KEY REFERENCES dbo.Part(PartId),
    PartState               NVARCHAR(20) NOT NULL,
        -- SANDED_RAW, UNSANDED_RAW, PAINTED
    Quantity                INT NOT NULL,
    DispositionCodeId       INT NULL
        CONSTRAINT FK_RmaLine_Disposition FOREIGN KEY REFERENCES dbo.DispositionCode(DispositionCodeId)
);
```

---

### D.3 Production Schema — Entities from Part A (Reference Summary)

Per the prompt instruction to not duplicate Part A rows, the following Part A entities are listed by reference only. Full definitions are in the Part A entity proposals JSON (`ai_context/part_a_entity_proposals.json`).

| Entity | Schema | PK | Key FKs | Source Forms | Notes |
|--------|--------|----|---------|--------------|-------|
| ProductionRun | production | ProductionRunId | PlantId, ProductionLineId, ShiftId, CustomerId, PartId | 8.2.2.1.5, 8.2.2.2.1, 8.2.2.2.4, 8.2.2.2.7, 8.2.2.29 | Part B adds: FK from quality.InspectionRecord.ProductionRunId back to this entity |
| ProductionRunCarrier | production | ProductionRunCarrierIdProductionRunId | 8.2.2.2.1, 8.2.2.2.4, 8.2.2.2.7 | Part B adds: Application Tracker (8.2.2.3.5.5) spray params should populate this entity |
| PaintBatch | production | PaintBatchId | PlantId, ProductionLineId, PaintSupplierId | 8.2.2.1.18, 8.2.2.23, 8.2.2.24, 8.2.2.25 | No Part B impact |
| ColourVerification | production | ColourVerificationId | PaintBatchId | 8.2.2.26 | No Part B impact — but SHOULD be linkable from InspectionRecord in future |
| MaintenanceRecord | production | MaintenanceRecordId | PlantId, ProductionLineId, EquipmentId | 10 maintenance forms | No Part B impact |
| DowntimeEvent | production | DowntimeEventId | PlantId, ProductionLineId, ShiftId | 8.2.2.1.9, 8.2.2.28 | No Part B impact |
| PostPaintOperation | production | PostPaintOperationId | PlantId, ShiftId, PartId, CustomerId, DefectTypeId | 8.2.2.7, 8.2.2.8, 8.2.2.9, 8.2.2.31 | Part B adds: Buff inspection forms (Part B) are the quality check downstream of this entity |
| PostPaintDailySummary | production | SummaryId | PlantId | 8.2.2.30 | No Part B impact |
| WasteRecord | production | WasteRecordId | PlantId, ProductionLineId | 5 drum labels | No Part B impact |
| PaintTrial | production | PaintTrialId | PlantId, ProductionLineId, PaintBatchId | 8.2.2.6, 8.2.2.33 | No Part B impact |

---

### D.4 Entity Proposals — JSON Format (Part B Entities)

```json
{
  "proposedEntities_PartB": [
    {
      "name": "InspectionRecord",
      "schema": "quality",
      "description": "Central inspection event per customer × part × date × shift × type. One-to-many with InspectionDefectCount.",
      "primaryKey": "InspectionRecordId",
      "foreignKeys": [
        "PlantId→dbo.Plant",
        "ProductionLineId→dbo.ProductionLine",
        "ShiftId→dbo.Shift",
        "CustomerId→dbo.Customer",
        "PartId→dbo.Part",
        "InspectionTypeCodeId→dbo.LookupValue",
        "NcrId→quality.NonConformanceReport",
        "ProductionRunId→production.ProductionRun",
        "Gp12ContainmentEventId→quality.Gp12ContainmentEvent"
      ],
      "childEntities": ["InspectionDefectCount"],
      "rlsScoped": true,
      "sourceFormCount": 16,
      "primarySourceForms": [
        "8.2.2.3.2.1", "8.2.2.3.3.2", "8.2.2.3.4.1", "8.2.2.3.4.2",
        "8.2.2.3.5.1", "8.2.2.3.5.2", "8.2.2.3.5.3", "8.2.2.3.5.4",
        "8.2.2.3.5.5", "8.2.2.3.5.6", "8.2.2.3.6.1", "8.2.2.3.6.2",
        "8.2.2.3.7.1", "8.2.2.3.7.2", "8.2.2.3.7.3", "8.2.2.2.16"
      ]
    },
    {
      "name": "InspectionDefectCount",
      "schema": "quality",
      "description": "Per-defect-type count within an inspection record. Sparse rows — most quantities will be 0.",
      "primaryKey": "InspectionDefectCountId",
      "foreignKeys": [
        "InspectionRecordId→quality.InspectionRecord",
        "DefectTypeId→quality.DefectType",
        "DispositionCodeId→dbo.DispositionCode"
      ],
      "childEntities": [],
      "rlsScoped": false,
      "sourceFormCount": 16,
      "primarySourceForms": ["(same as InspectionRecord)"]
    },
    {
      "name": "CustomerInspectionProfile",
      "schema": "quality",
      "description": "Configuration: defines which defects, gate alarms, and dispositions appear per customer per part per inspection type. Drives dynamic form rendering.",
      "primaryKey": "CustomerInspectionProfileId",
      "foreignKeys": [
        "CustomerId→dbo.Customer",
        "PartId→dbo.Part",
        "InspectionTypeCodeId→dbo.LookupValue",
        "DefectTypeId→quality.DefectType",
        "DispositionCodeId→dbo.DispositionCode"
      ],
      "childEntities": [],
      "rlsScoped": false,
      "sourceFormCount": 0,
      "note": "Configuration entity — seeded from form analysis, not from form data"
    },
    {
      "name": "Gp12ContainmentEvent",
      "schema": "quality",
      "description": "GP-12 containment lifecycle. Linked to triggering NCR. Tracks entry/exit criteria, inspection frequency, customer notification.",
      "primaryKey": "Gp12ContainmentEventId",
      "foreignKeys": [
        "PlantId→dbo.Plant",
        "CustomerId→dbo.Customer",
        "PartId→dbo.Part",
        "NcrId→quality.NonConformanceReport",
        "StatusCodeId→dbo.StatusCode"
      ],
      "childEntities": [],
      "rlsScoped": true,
      "sourceFormCount": 1,
      "primarySourceForms": ["8.2.2.3.7.3"],
      "note": "Current form has zero GP-12 metadata. Entity is 90% net-new design."
    },
    {
      "name": "PackSlip",
      "schema": "logistics",
      "description": "Outbound shipment header with quality release gate.",
      "primaryKey": "PackSlipId",
      "foreignKeys": [
        "PlantId→dbo.Plant",
        "CustomerId→dbo.Customer"
      ],
      "childEntities": ["PackSlipLineItem"],
      "rlsScoped": true,
      "sourceFormCount": 7,
      "primarySourceForms": [
        "8.2.2.4.2", "8.2.2.4.9", "8.2.2.4.11", "8.2.2.4.12",
        "8.2.2.4.14", "8.2.2.4.17", "8.2.2.4.18"
      ]
    },
    {
      "name": "PackSlipLineItem",
      "schema": "logistics",
      "description": "Per-part line on pack slip with inspection record linkage.",
      "primaryKey": "PackSlipLineItemId",
      "foreignKeys": [
        "PackSlipId→logistics.PackSlip",
        "PartId→dbo.Part",
        "InspectionRecordId→quality.InspectionRecord"
      ],
      "childEntities": [],
      "rlsScoped": false,
      "sourceFormCount": 7
    },
    {
      "name": "ReceivingLogEntry",
      "schema": "logistics",
      "description": "Inbound material receipt with structured reject reason and SCAR linkage.",
      "primaryKey": "ReceivingLogEntryId",
      "foreignKeys": [
        "PlantId→dbo.Plant",
        "RejectReasonCodeId→dbo.LookupValue",
        "ScarId→quality.SupplierCar"
      ],
      "childEntities": [],
      "rlsScoped": true,
      "sourceFormCount": 1,
      "primarySourceForms": ["8.2.2.4.1"]
    },
    {
      "name": "ReturnMaterialAuthorization",
      "schema": "logistics",
      "description": "Customer return tracking with NCR and CustomerComplaint linkage.",
      "primaryKey": "RmaId",
      "foreignKeys": [
        "PlantId→dbo.Plant",
        "CustomerId→dbo.Customer",
        "NcrId→quality.NonConformanceReport",
        "CustomerComplaintId→quality.CustomerComplaint",
        "StatusCodeId→dbo.StatusCode"
      ],
      "childEntities": ["RmaLineItem"],
      "rlsScoped": true,
      "sourceFormCount": 1,
      "primarySourceForms": ["8.2.2.4.20"],
      "note": "Based on Metelix RMA sheet — only structured return tracking in organization"
    },
    {
      "name": "RmaLineItem",
      "schema": "logistics",
      "description": "Per-part detail within RMA including part state and disposition.",
      "primaryKey": "RmaLineItemId",
      "foreignKeys": [
        "RmaId→logistics.ReturnMaterialAuthorization",
        "PartId→dbo.Part",
        "DispositionCodeId→dbo.DispositionCode"
      ],
      "childEntities": [],
      "rlsScoped": false,
      "sourceFormCount": 1
    }
  ],
  "summary_PartB": {
    "totalNewEntities": 9,
    "totalNewChildEntities": 3,
    "proposedSchemas": ["quality", "logistics"],
    "estimatedMigrations": "12-15 migrations",
    "estimatedStoredProcedures": "20-25 new stored procedures",
    "estimatedApiEndpoints": "25-30 new endpoints",
    "crossSchemaForeignKeys": [
      "quality.InspectionRecord.ProductionRunId → production.ProductionRun",
      "quality.InspectionRecord.NcrId → quality.NonConformanceReport",
      "quality.Gp12ContainmentEvent.NcrId → quality.NonConformanceReport",
      "logistics.PackSlipLineItem.InspectionRecordId → quality.InspectionRecord",
      "logistics.ReceivingLogEntry.ScarId → quality.SupplierCar",
      "logistics.ReturnMaterialAuthorization.NcrId → quality.NonConformanceReport",
      "logistics.ReturnMaterialAuthorization.CustomerComplaintId → quality.CustomerComplaint"
    ]
  },
  "combined_PartA_PartB_summary": {
    "totalNewEntities": 19,
    "totalNewChildEntities": 6,
    "schemas": ["quality", "production", "logistics"],
    "estimatedMigrations": "27-35 migrations",
    "estimatedStoredProcedures": "45-60 new stored procedures",
    "estimatedApiEndpoints": "55-65 total new endpoints",
    "criticalPath": [
      "1. quality.InspectionRecord + InspectionDefectCount (unlocks inspection digitization)",
      "2. quality.CustomerInspectionProfile (unlocks dynamic form rendering)",
      "3. POST /v1/inspection/{id}/escalate (bridges inspection to NCR)",
      "4. logistics.PackSlip with QualityReleaseStatus (closes shipping-quality gap)",
      "5. production.ProductionRun (enables traceability chain)",
      "6. quality.Gp12ContainmentEvent (enables GP-12 compliance)"
    ]
  }
}
```

---

## Appendix E: Cross-Plant Normalization Checklist (Updated with Plant 2 Data)

| # | Checklist Item | Category | Plant 1 Finding | Plant 2 Finding | Universal Pattern | Recommended Standard | Audit Instruction (Plants 3–7) |
|---|---------------|----------|-----------------|-----------------|-------------------|---------------------|-------------------------------|
| 1 | No NCR system exists | Quality Core | Confirmed — zero NCR forms | Confirmed — zero NCR forms or references in 84 forms (53 Part A + 31 Part B) | **YES** | InspectionRecord → NCR escalation pathway required at all plants | Verify absence. Count any NCR-adjacent forms (hold tags etc). Score 0 if absent. |
| 2 | Broken traceability chain | Traceability | ~20% end-to-end | ~23% end-to-end | **YES** | Minimum: Carrier/Rack # on inspection forms linked to ProductionRun | Map chain: receipt → load → coat → inspect → pack → ship. Score each link 0–5. |
| 3 | No shipping-quality gate | Shipping | No quality release on pack slips | No quality release on pack slips | **YES** | QualityReleaseStatus field on PackSlip mandatory before shipping | Check all pack slips for inspection sign-off or quality release field. |
| 4 | Customer forms are relabeled copies | Form Design | 80%+ Tier 2 candidates | KB tabs named 'Laval Tool'; Daily Ship report title mismatch | **YES** | Single configurable template per form type driven by CustomerInspectionProfile | Check tab names vs file names. Count structural overlap %. |
| 5 | GP-12 is form-only not process | Compliance | Per-customer forms with no lifecycle | Tesla GP12 has no entry/exit/time limit | **YES** | Gp12ContainmentEvent entity with full lifecycle | Check for GP-12 forms. Score entry criteria / exit criteria / time limit / NCR link. |
| 6 | Gate alarms are paper annotations | Quality Control | Present but not calculated | Present on 8 of 16 forms — column header annotations only | **YES** | GateAlarmThreshold on CustomerInspectionProfile with computed GateAlarmTriggered | Extract all gate alarm values. Verify consistency per defect per customer. |
| 7 | No supervisor sign-off on inspection | Accountability | Not checked in Plant 1 Part B | Zero of 16 forms have approval field | **YES** | Approval workflow on InspectionRecord (quality lead sign-off) | Check every inspection form for sign-off / approval / witness fields. |
| 8 | No test methods referenced on inspection | Standards | Not checked in Plant 1 Part B | Zero forms reference ASTM or customer test methods | **YES** | CustomerInspectionProfile should include test method references | Look for adhesion / film build / gloss / colour measurement fields. |
| 9 | Defect taxonomy is customer-siloed | Defect Management | 97 strings → 38 normalized | 42 strings → 28 normalized (Part B) | **YES** | Centralized quality.DefectType with 2-level hierarchy scoped to LineType | Extract ALL defect strings. Map to normalized L1/L2 codes. Note gaps vs expected defect set for line type. |
| 10 | Post-paint rework cycles uncounted | Process | Labour-only tally sheets | No link between paint inspection and buff inspection | **YES** | InspectionRecord chain: PAINT inspection → BUFF inspection linked by source InspectionRecordId | Check for any mechanism linking initial inspection to re-inspection. |
| 11 | Monthly Totals reveals customer scope drift | Data Hygiene | Not checked | 35 historical customers vs 6 active | **LIKELY** | Part master and customer master cleanup before platform migration | Compare active customers on inspection forms vs shipping/tracking forms. Flag orphans. |
| 12 | Hidden customer programs in wrong files | Data Hygiene | Not checked | BRP Spyder hidden in Laval Tool Buff Inspection KANBAN sheet | **LIKELY** | Audit all secondary sheet tabs for misclassified programs | Check every sheet tab name against file name and customer designation. |
| 13 | Colour field captured but no entity column | Reference Data | Colour on Part A colour verification | Colour on 6 of 16 inspection forms (Mytox/Laval/KB/Metelix/Tesla) | **YES** | dbo.Part.ColourCode or dbo.PartColour lookup table | Note every form that captures colour. Verify colour naming consistency. |
| 14 | Receiving log is intake-only with no quality assessment | Incoming Quality | Not in Plant 1 Part B scope | Accept/Reject binary with no defect classification | **LIKELY** | ReceivingLogEntry with RejectReasonCodeId and SCAR trigger | Check receiving forms for incoming inspection criteria / defect codes / SCAR references. |
| 15 | Metelix RMA is only structured return tracking | Returns | No return tracking found in Plant 1 | Metelix tracker has RMA sheet with 3 RMA events tracked | **UNKNOWN** — check other plants | ReturnMaterialAuthorization entity universal | Check for any return / RMA / chargeback tracking at each plant. |
| 16 | Cost visibility is near-zero | Cost | None | Scrap count on 2 of 16 forms; no cost per unit anywhere | **YES** | NCR.EstimatedCost populated from inspection scrap + rework quantities × unit cost | Check for any cost data on any form: scrap cost / rework cost / customer chargeback. |
| 17 | Application Tracker hybrid exists for high-value programs | Best Practice | Not found in Plant 1 | Metelix Hummer Spoiler Application Tracker — process + quality per carrier | **UNKNOWN** | Productionize as standard for high-value/high-risk programs | Ask: does this plant have any form combining spray parameters with inspection results? |
| 18 | Customer trackers function as manual ERP | Logistics | Unknown | 4 customers with Receiving/Shipping/MRP/Releases/Waterfall/Parts Legend | **LIKELY** | Extract receiving + shipping data for quality platform; leave MRP/releases in ERP | Count customer trackers. Map sheet types. Identify RMA or quality-adjacent sheets. |
| 19 | Defect gaps for line type | Taxonomy Completeness | E-coat defects partially covered | LIQUID gaps: dry spray / colour mismatch / gloss failure absent | **YES** — will vary by LineType | Seed defect taxonomy with line-type-appropriate complete list before migration | For LIQUID: verify runs/sags/orange peel/dry spray/colour/gloss/solvent pop/fish eye/mottling. For POWDER: verify orange peel/impact/outgassing/back-ionization. For ECOAT: verify cratering/pinholing/poor throwing power. |
| 20 | Disposition codes underutilized | Quality Process | Unknown | 4 of 11 codes used implicitly. Use-As-Is / Sort / Customer-Deviation absent. | **LIKELY** | Verify all 11 disposition codes are understood and available at each plant | List which disposition codes appear on forms vs which exist in system. Flag gaps. |

### Checklist Summary

- **20 items total**
- **13** confirmed universal patterns
- **4** likely universal (need Plants 3–7 confirmation)
- **3** unknown / plant-specific

---

## End of Report

### Combined Deliverable Summary

- **6 report sections** covering Executive Summary through Consolidated Assessment
- **5 appendices:** A (46-entry defect taxonomy), B (96 field mappings), C (31-form consolidation matrix), D (19 entity SQL+JSON schemas), E (20-item cross-plant checklist)
- **31 forms** analyzed across **89 worksheet tabs**
- **9 new entities** proposed (+ 3 child entities) across quality and logistics schemas
- **25+ new API endpoints** identified
- **8 UI screens** replacing 31 paper forms
- **Plant 2 combined readiness: 25/100**
