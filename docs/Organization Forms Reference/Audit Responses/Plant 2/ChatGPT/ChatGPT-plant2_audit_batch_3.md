# Appendix C: Form Consolidation Matrix

**Customer-Specific Forms → Tier 1 / 2 / 3**

---

## Consolidation Matrix (Engineering View)

### INS-01 — Standard Paint Inspection

| Field | Value |
|---|---|
| **Domain** | Quality Inspection |
| **Tier** | 1 |
| **Forms Included** | 8.2.2.3.4.1 Laval Tool Inspection · 8.2.2.3.6.1 KB Components Inspection · 8.2.2.3.9 Misc Customers Inspection |
| **Proposed Replacement** | "Standard Paint Inspection" (single configurable template) |
| **Consolidation Logic** | **Common:** identical grid-style daily inspection table, same defect-count + routing buckets. **Configurable:** Customer name/logo, part list, optional molding defect section toggle, defect columns (lookup-driven). |
| **Platform Entity Targets** | `InspectionRecord` (proposed) + `InspectionTestResult` (proposed) + link to `LoadRecord` (proposed) |
| **Universal vs Configurable** | Platform-standard template; customer-configurable defect set |
| **Evidence** | KB sheet/tab name shows carryover from Laval template; Misc looks like same family. |
| **Confidence** | **High** |

---

### INS-02 — Standard Buff Inspection

| Field | Value |
|---|---|
| **Domain** | Quality Inspection |
| **Tier** | 1 |
| **Forms Included** | 8.2.2.3.4.2 Laval Tool Buff Inspection · 8.2.2.3.6.2 KB Components Buffing Inspection |
| **Proposed Replacement** | "Standard Buff Inspection" (single configurable template) |
| **Consolidation Logic** | **Common:** buff-stage defect categories + disposition routing ("return to buff / send to rework" style). **Configurable:** defect list (lookup-driven), pass/fail rules, required fields (shift/date/operator). |
| **Platform Entity Targets** | `InspectionRecord` + `InspectionTestResult` + disposition routing to `PostPaintReworkEvent` (new) where applicable |
| **Universal vs Configurable** | Platform-standard template; customer-configurable |
| **Evidence** | Same template family pattern across Laval/KB. |
| **Confidence** | **High** |

---

### INS-03 — Tesla Program Inspection

| Field | Value |
|---|---|
| **Domain** | GP-12 / Containment + Inspection |
| **Tier** | 2 |
| **Forms Included** | 8.2.2.3.7.1 Tesla Inspection · 8.2.2.3.7.2 Tesla Buff Inspection · 8.2.2.3.8.1 Tesla GP12 Inspection |
| **Proposed Replacement** | "Tesla Program Inspection" (one template w/ stage mode) |
| **Consolidation Logic** | **Common:** Tesla-specific molding + paint defect taxonomy, similar layout. **Configurable:** Stage selector = PAINT / BUFF / GP12, and GP12 adds containment fields & enforcement. |
| **Platform Entity Targets** | `InspectionRecord` + `InspectionTestResult` + `GP12InspectionRecord` (proposed) + workflow gate to `CertificationRecord` (proposed) |
| **Universal vs Configurable** | Customer-specific template (Tesla), but platform-standard mechanics (stage-based inspection) |
| **Evidence** | Tesla has dedicated forms + GP12 variant. |
| **Confidence** | **High** |

---

### INS-04 — Metelix Painted Inspection

| Field | Value |
|---|---|
| **Domain** | Quality Inspection |
| **Tier** | 2 |
| **Forms Included** | 8.2.2.3.5.1 Metelix Inspection · 8.2.2.3.5.4 Metelix Hummer Painted Inspection · 8.2.2.3.5.6 Metelix Y2XX Highwing Painted Inspection |
| **Proposed Replacement** | "Metelix Painted Inspection" (one template w/ program variants) |
| **Consolidation Logic** | **Common:** Metelix painted-part inspection grids + defect tallies. **Configurable:** program (Hummer/Y2XX/etc) controls which defect columns appear + which part IDs are valid. |
| **Platform Entity Targets** | `InspectionRecord` + `InspectionTestResult` + link to `LoadRecord` |
| **Universal vs Configurable** | Customer-specific template (Metelix), but platform-standard mechanics |
| **Evidence** | Multiple Metelix painted inspection variants in same folder set. |
| **Confidence** | **High** |

---

### INS-05 — Metelix Buff Inspection

| Field | Value |
|---|---|
| **Domain** | Quality Inspection |
| **Tier** | 3 |
| **Forms Included** | 8.2.2.3.5.2 Metelix Buff Inspection |
| **Proposed Replacement** | "Metelix Buff Inspection" (standalone template or stage of INS-04) |
| **Consolidation Logic** | **Unique:** Metelix buff defect modes (snowballs/haze/burn-through etc) + routing logic. Could be merged into a generic Buff template, but only if defect taxonomy is lookup-driven and configurable. |
| **Platform Entity Targets** | `InspectionRecord` + `InspectionTestResult` + route to `PostPaintReworkEvent` |
| **Universal vs Configurable** | Customer-specific (likely) |
| **Evidence** | Metelix buff defects differ materially from Laval/KB buff templates. |
| **Confidence** | **Medium-High** |

---

### INS-06 — Molding/Sanding Stage Inspection

| Field | Value |
|---|---|
| **Domain** | Quality Inspection + Post-Paint |
| **Tier** | 3 |
| **Forms Included** | 8.2.2.3.5.3 Metelix Moulding-Sanding Inspection |
| **Proposed Replacement** | "Molding/Sanding Stage Inspection" |
| **Consolidation Logic** | **Unique:** explicit stage inspection IDs (molding vs sanding), mixed "pre-paint" and "post-sand" defect capture. Requires stage-aware linkage + possibly WIP status tracking. |
| **Platform Entity Targets** | `InspectionRecord` + `InspectionTestResult` + link to `PostPaintReworkEvent` (new) |
| **Universal vs Configurable** | Plant 2 / customer-specific (Metelix) |
| **Evidence** | Dedicated inspection IDs suggest separate workflow stage vs paint line unload. |
| **Confidence** | **High** |

---

### INS-07 — Carrier-Level Application Log

| Field | Value |
|---|---|
| **Domain** | Process Control + Traceability |
| **Tier** | 3 |
| **Forms Included** | 8.2.2.3.5.5 Metelix Hummer Spoiler Application Tracker |
| **Proposed Replacement** | "Carrier-Level Application Log" |
| **Consolidation Logic** | **Unique:** carrier-level spray parameters + good/buff/rework counts in one sheet. This should be split digitally into (1) `LoadRecord` + (2) `ProcessParameterLog/Reading` + (3) `InspectionRecord` linkage. |
| **Platform Entity Targets** | `LoadRecord` + `ProcessParameterLog/Reading` + `InspectionRecord` |
| **Universal vs Configurable** | Plant 2 / customer-specific (but features become platform-standard for LIQUID line type) |
| **Evidence** | This is the only true carrier-level combined parameter+defect record in current set. |
| **Confidence** | **High** |

---

### INS-08 — BMW/Rollstamp Rack Inspection

| Field | Value |
|---|---|
| **Domain** | Quality Inspection |
| **Tier** | 3 |
| **Forms Included** | 8.2.2.3.1.1 Rollstamp BMW G07 Inspection Form |
| **Proposed Replacement** | "BMW/Rollstamp Rack Inspection" |
| **Consolidation Logic** | **Unique:** rack-centric linkage + "gate alarm" style fields + location-specific orange peel. Needs dedicated config for rack/range/alarms. |
| **Platform Entity Targets** | `InspectionRecord` + `InspectionTestResult` + link to `LoadRecord` |
| **Universal vs Configurable** | Customer-specific template |
| **Evidence** | Rack # field + BMW-specific defect columns. |
| **Confidence** | **High** |

---

### INS-09 — Mytox Inspection

| Field | Value |
|---|---|
| **Domain** | Quality Inspection |
| **Tier** | 3 |
| **Forms Included** | 8.2.2.3.3.1 Mytox Inspection Form |
| **Proposed Replacement** | "Mytox Inspection" |
| **Consolidation Logic** | **Unique:** Mytox-specific defect list (thin clear, paint spits, e-coat showing) and shift/time fields. Can't safely collapse into INS‑01 without losing requirements. |
| **Platform Entity Targets** | `InspectionRecord` + `InspectionTestResult` |
| **Universal vs Configurable** | Customer-specific template |
| **Evidence** | Distinct defect list and table layout vs Laval/KB/Misc family. |
| **Confidence** | **High** |

---

### SHIP-01 — Shipment / Pack Slip

| Field | Value |
|---|---|
| **Domain** | Packaging / Shipping |
| **Tier** | 2 |
| **Forms Included** | 8.2.2.4.2 P2 General Pack Slip · 8.2.2.4.9 Metelix Packslip · 8.2.2.4.11 Mytox Packslip · 8.2.2.4.12 Rollstamp BMW Packslip · 8.2.2.4.14 Laval Tool Packslip · 8.2.2.4.17 KB Packslip · 8.2.2.4.18 Polycon Packslip |
| **Proposed Replacement** | "Shipment / Pack Slip" (one platform flow w/ customer print layouts) |
| **Consolidation Logic** | **Common:** pack slip header + lines (part/qty). **Configurable:** customer addresses, ship-to formats, label/logo, customer-required fields. **Required change:** enforce linkage to `ProductionRunId` or `LoadRecordId` per shipment line. |
| **Platform Entity Targets** | `logistics.Shipment` (new) + `logistics.ShipmentLine` (new) + link to `CertificationRecord` (proposed) |
| **Universal vs Configurable** | Platform-standard (multi-plant value) with customer-configurable output |
| **Evidence** | Many customer pack slip templates exist; they're variants of the same business object. |
| **Confidence** | **Medium** |

---

### SHIP-02 — Shipping Planning Trackers (Dashboard Replacement)

| Field | Value |
|---|---|
| **Domain** | Packaging / Shipping (planning trackers) |
| **Tier** | 2 |
| **Forms Included** | 8.2.2.4.19 Polycon Tracker · 8.2.2.4.20 Metelix Demand & Production Tracker · 8.2.2.4.21 Laval Tracker · 8.2.2.4.22 KB Tracker |
| **Proposed Replacement** | **Do NOT rebuild as forms** → replace with dashboards + shipment backlog |
| **Consolidation Logic** | **Common:** demand vs produced vs shipped tracking. **Recommendation:** platform should provide "open orders / produced / shipped" dashboards once shipments + production runs exist. |
| **Platform Entity Targets** | Reporting on `ProductionRun`, `LoadRecord`, `Shipment/Line` |
| **Universal vs Configurable** | Likely out-of-scope for sf-quality as data entry; in-scope for reporting |
| **Evidence** | These are Excel planning artifacts; not controlled quality records. |
| **Confidence** | **Medium** |

---

## Appendix C — CSV Reference

```csv
ConsolidationGroupId,Domain,Tier,FormsIncluded,ProposedReplacement,ConsolidationLogic,PlatformEntityTargets,UniversalVsConfigurable,Evidence,Confidence
INS-01,QUALITY INSPECTION,1,"8.2.2.3.4.1 Laval Tool Inspection; 8.2.2.3.6.1 KB Components Inspection; 8.2.2.3.9 Misc Customers Inspection","Standard Paint Inspection (configurable template)","Common: identical inspection grid + defect counts + routing buckets. Configurable: customer branding, part list, defect columns (lookup-driven), optional molding section","InspectionRecord; InspectionTestResult; link to LoadRecord","Platform-standard template; customer-configurable","KB template shows carryover from Laval; Misc appears same family",High
INS-02,QUALITY INSPECTION,1,"8.2.2.3.4.2 Laval Tool Buff Inspection; 8.2.2.3.6.2 KB Components Buffing Inspection","Standard Buff Inspection (configurable template)","Common: buff-stage defect categories + routing buckets. Configurable: defect list, required fields, pass/fail logic","InspectionRecord; InspectionTestResult; routes to PostPaintReworkEvent","Platform-standard template; customer-configurable","Same template family pattern across Laval/KB",High
INS-03,GP-12 / CONTAINMENT + INSPECTION,2,"8.2.2.3.7.1 Tesla Inspection; 8.2.2.3.7.2 Tesla Buff Inspection; 8.2.2.3.8.1 Tesla GP12 Inspection","Tesla Program Inspection (stage mode)","Common: Tesla-specific defect taxonomy and layout. Configurable: stage selector PAINT/BUFF/GP12 with containment enforcement in GP12 mode","InspectionRecord; InspectionTestResult; GP12InspectionRecord; workflow gate to CertificationRecord","Customer-specific template (Tesla) with platform-standard mechanics","Dedicated Tesla forms + GP12 variant",High
INS-04,QUALITY INSPECTION,2,"8.2.2.3.5.1 Metelix Inspection; 8.2.2.3.5.4 Metelix Hummer Painted Inspection; 8.2.2.3.5.6 Metelix Y2XX Highwing Painted Inspection","Metelix Painted Inspection (program variants)","Common: Metelix painted inspection grids. Configurable: program controls defect columns and valid parts","InspectionRecord; InspectionTestResult; link to LoadRecord","Customer-specific template (Metelix) with platform-standard mechanics","Multiple Metelix painted variants present",High
INS-05,QUALITY INSPECTION,3,"8.2.2.3.5.2 Metelix Buff Inspection","Metelix Buff Inspection (standalone or stage of Metelix)","Unique: Metelix buff defect modes and routing; can merge only if defect list is fully configurable","InspectionRecord; InspectionTestResult; routes to PostPaintReworkEvent","Customer-specific (likely)","Metelix buff defects differ from Laval/KB",Medium-High
INS-06,QUALITY INSPECTION + POST-PAINT,3,"8.2.2.3.5.3 Metelix Moulding-Sanding Inspection","Molding/Sanding Stage Inspection","Unique: explicit molding vs sanding inspection IDs and stage-aware defects; needs workflow linkage","InspectionRecord; InspectionTestResult; links to PostPaintReworkEvent","Plant 2/customer-specific","Dedicated stage inspection IDs in sheet",High
INS-07,PROCESS CONTROL + TRACEABILITY,3,"8.2.2.3.5.5 Metelix Hummer Spoiler Application Tracker","Carrier-Level Application Log","Unique: carrier-level spray parameters + defect routing in one tool; should split into LoadRecord + ProcessParameterLog + InspectionRecord digitally","LoadRecord; ProcessParameterLog/Reading; InspectionRecord","Plant 2/customer-specific; features become LIQUID platform-standard","Only carrier-level combined parameter+defect record in current set",High
INS-08,QUALITY INSPECTION,3,"8.2.2.3.1.1 Rollstamp BMW G07 Inspection","BMW/Rollstamp Rack Inspection","Unique: rack-centric linkage + gate alarm fields + location-specific orange peel; dedicated config required","InspectionRecord; InspectionTestResult; link to LoadRecord","Customer-specific","Rack # field and BMW-specific columns",High
INS-09,QUALITY INSPECTION,3,"8.2.2.3.3.1 Mytox Inspection","Mytox Inspection","Unique: Mytox defect list (thin clear, paint spits, e-coat showing) and layout; not safe to collapse into generic family without config","InspectionRecord; InspectionTestResult","Customer-specific","Distinct defect list and structure",High
SHIP-01,PACKAGING / SHIPPING,2,"8.2.2.4.2 General Pack Slip; 8.2.2.4.9 Metelix; 8.2.2.4.11 Mytox; 8.2.2.4.12 Rollstamp BMW; 8.2.2.4.14 Laval; 8.2.2.4.17 KB; 8.2.2.4.18 Polycon","Shipment / Pack Slip (single flow)","Common: header + part/qty lines. Configurable: addresses, branding, customer-required fields. Required control: enforce run/load linkage per shipment line","logistics.Shipment; logistics.ShipmentLine; link to CertificationRecord","Platform-standard with customer-configurable print layouts","Multiple customer pack slip templates exist; likely variants",Medium
SHIP-02,PACKAGING / SHIPPING (planning trackers),2,"8.2.2.4.19 Polycon Tracker; 8.2.2.4.20 Metelix Demand & Production Tracker; 8.2.2.4.21 Laval Tracker; 8.2.2.4.22 KB Tracker","Dashboards (no form rebuild)","Common: demand vs produced vs shipped tracking; replace with dashboards once production+shipment exist","Reporting on ProductionRun/LoadRecord/Shipment","Out-of-scope for data entry; in-scope for reporting","Excel planning artifacts, not controlled quality records",Medium
```

---
---

# Appendix D: Proposed New Entity Schemas

**Plant 2-Originated Proposals Only**

---

## D.0 Summary — What's New (and Why It Exists)

| Proposed Entity | Why It Exists | Evidence | RLS (PlantId) | Temporal Versioning | Confidence |
|---|---|---|:---:|:---:|:---:|
| `postpaint.PostPaintReworkEvent` (+ defects child) | Post-paint rework is currently a data black hole; must track rework lifecycle + outcome | 8.2.2.7 Daily Sanding Tally Sheet.xlsx · 8.2.2.8 Daily Buffing Tally Sheet.xlsx · 8.2.2.9 Daily Deburring Tally Sheet.xlsx · WIP tags 8.2.2.10/8.2.2.15/8.2.2.16 | YES | NO (use `workflow.StatusHistory`) | High |
| `logistics.Shipment` + `logistics.ShipmentLine` | Shipping forms exist but are not traceable; need shipment header/line that links to run/load | Pack slip templates 8.2.2.4.2, .9, .11, .12, .14, .17, .18 + trackers | YES | NO | Medium-High |
| `production.DowntimeEvent` | Plant 2 tracks downtime heavily; needs structured downtime events tied to run | 8.2.2.27 Daily Down Time.xlsx · 8.2.2.28 Down time Tracking Template.xlsx | YES | NO | High |
| `labor.ShiftStaffing` + `labor.ShiftStaffingAssignment` | Scheduling exists and is the only operator identity source; needed for competency correlation | 8.2.2.1.7 Daily Painter Schedule.xlsx · 8.2.2.1.10 Daily Painter Line Up.xlsx | YES | NO | Medium-High |
| `compliance.WasteDisposalEvent` (OPTIONAL) | Waste forms exist but are mostly empty templates; decide if in-scope | 8.2.2.30 Booth Sludge.xlsx · 8.2.2.17 Still Bottoms.xlsx · 8.2.2.18 Waste Paint.xlsx · 8.2.2.19 Waste Zinc.xlsx · 8.2.2.15 Empty.xlsx | YES | NO | Low-Medium |

> **Critical note (no sugar coating):** If engineering implements Shipments and PostPaintRework but does not enforce linkage to `ProductionRunId`/`LoadRecordId`, Plant 2 will still be untraceable. These entities only matter if they close the chain.

---

## D.1 `postpaint.PostPaintReworkEvent` (+ child: `postpaint.PostPaintReworkDefect`)

### Purpose

Track sanding / buffing / deburring as a first-class lifecycle: entered rework → worked → outcome (pass/fail) → disposition with linkage to source inspection/load/run.

### Key Fields (Minimum Viable)

| Field | Type | Null | FK Target | Notes |
|---|---|:---:|---|---|
| `PostPaintReworkEventId` | int identity | NO | — | PK |
| `PlantId` | int | NO | `dbo.Plant.PlantId` | RLS key |
| `ReworkEventNumber` | nvarchar(20) | NO | `dbo.DocumentSequence` (INFERRED) | Human-facing number like NCR |
| `StatusCodeId` | int | NO | `dbo.StatusCode` | Workflow states (DRAFT/OPEN/COMPLETE/VERIFIED) |
| `ReworkTypeLookupId` | int | NO | `dbo.LookupValue` | REWORK_TYPE: BUFF/SAND/DEBURR |
| `ProcessAreaId` | int | YES | `dbo.ProcessArea` | Sanding/buffing station |
| `ProductionLineId` | int | YES | `dbo.ProductionLine` | Origin line (101/102/103) if known |
| `CustomerId` | int | YES | `dbo.Customer` | If known |
| `PartId` | int | YES | `dbo.Part` | If known |
| `SourceProductionRunId` | int | YES | `ProductionRun` (proposed) | Required for traceability once platform live |
| `SourceLoadRecordId` | int | YES | `LoadRecord` (proposed) | Carrier/rack link |
| `SourceInspectionRecordId` | int | YES | `InspectionRecord` (proposed) | Where defect was detected |
| `PrimaryDefectTypeId` | int | YES | `quality.DefectType` | Fast filter; detailed defects in child table |
| `QtyIn` | int | NO | — | Quantity entering rework |
| `QtyOut` | int | YES | — | Quantity leaving rework OK |
| `QtyScrapped` | int | YES | — | Quantity scrapped during rework |
| `LaborMinutes` | int | YES | — | Ties to tally sheets without building cost engine on day 1 |
| `ExternalEmployeeRef` | nvarchar(50) | YES | — | Employee number from HR system (no FK assumed) |
| `OperatorName` | nvarchar(100) | YES | — | For day-1 migration (names/initials) |
| `OutcomeDispositionCodeId` | int | YES | `dbo.DispositionCode` | REWORK/RECOAT/SCRAP/etc |
| `Notes` | nvarchar(1000) | YES | — | Free text |
| `CreatedAt` | datetime2(0) | NO | — | UTC |
| `UpdatedAt` | datetime2(0) | YES | — | UTC |

### Child Table: Defects Per Rework Event

Store multiple defect types and affected counts (incoming vs post-rework).

### SQL-Style DDL

```sql
-- Plant 2-originated schema proposal
CREATE SCHEMA postpaint;
GO

CREATE TABLE postpaint.PostPaintReworkEvent (
    PostPaintReworkEventId       INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_PostPaintReworkEvent PRIMARY KEY,
    PlantId                      INT NOT NULL,
    ReworkEventNumber            NVARCHAR(20) NOT NULL,
    StatusCodeId                 INT NOT NULL,
    ReworkTypeLookupId           INT NOT NULL, -- LookupValue where LookupType = 'REWORK_TYPE'
    ProcessAreaId                INT NULL,
    ProductionLineId             INT NULL,
    CustomerId                   INT NULL,
    PartId                       INT NULL,
    SourceProductionRunId        INT NULL, -- FK to proposed ProductionRun
    SourceLoadRecordId           INT NULL, -- FK to proposed LoadRecord
    SourceInspectionRecordId     INT NULL, -- FK to proposed InspectionRecord
    PrimaryDefectTypeId          INT NULL, -- FK quality.DefectType
    QtyIn                        INT NOT NULL,
    QtyOut                       INT NULL,
    QtyScrapped                  INT NULL,
    LaborMinutes                 INT NULL,
    ExternalEmployeeRef          NVARCHAR(50) NULL,
    OperatorName                 NVARCHAR(100) NULL,
    OutcomeDispositionCodeId     INT NULL,
    Notes                        NVARCHAR(1000) NULL,
    CreatedAt                    DATETIME2(0) NOT NULL CONSTRAINT DF_PostPaintReworkEvent_CreatedAt DEFAULT (SYSUTCDATETIME()),
    UpdatedAt                    DATETIME2(0) NULL
);

ALTER TABLE postpaint.PostPaintReworkEvent
ADD CONSTRAINT FK_PostPaintReworkEvent_Plant
FOREIGN KEY (PlantId) REFERENCES dbo.Plant(PlantId);

ALTER TABLE postpaint.PostPaintReworkEvent
ADD CONSTRAINT FK_PostPaintReworkEvent_StatusCode
FOREIGN KEY (StatusCodeId) REFERENCES dbo.StatusCode(StatusCodeId);

ALTER TABLE postpaint.PostPaintReworkEvent
ADD CONSTRAINT FK_PostPaintReworkEvent_ReworkType
FOREIGN KEY (ReworkTypeLookupId) REFERENCES dbo.LookupValue(LookupValueId);

ALTER TABLE postpaint.PostPaintReworkEvent
ADD CONSTRAINT FK_PostPaintReworkEvent_ProcessArea
FOREIGN KEY (ProcessAreaId) REFERENCES dbo.ProcessArea(ProcessAreaId);

ALTER TABLE postpaint.PostPaintReworkEvent
ADD CONSTRAINT FK_PostPaintReworkEvent_ProductionLine
FOREIGN KEY (ProductionLineId) REFERENCES dbo.ProductionLine(ProductionLineId);

ALTER TABLE postpaint.PostPaintReworkEvent
ADD CONSTRAINT FK_PostPaintReworkEvent_Customer
FOREIGN KEY (CustomerId) REFERENCES dbo.Customer(CustomerId);

ALTER TABLE postpaint.PostPaintReworkEvent
ADD CONSTRAINT FK_PostPaintReworkEvent_Part
FOREIGN KEY (PartId) REFERENCES dbo.Part(PartId);

ALTER TABLE postpaint.PostPaintReworkEvent
ADD CONSTRAINT FK_PostPaintReworkEvent_PrimaryDefectType
FOREIGN KEY (PrimaryDefectTypeId) REFERENCES quality.DefectType(DefectTypeId);

ALTER TABLE postpaint.PostPaintReworkEvent
ADD CONSTRAINT FK_PostPaintReworkEvent_DispositionCode
FOREIGN KEY (OutcomeDispositionCodeId) REFERENCES dbo.DispositionCode(DispositionCodeId);

ALTER TABLE postpaint.PostPaintReworkEvent
ADD CONSTRAINT UQ_PostPaintReworkEvent_Plant_Number
UNIQUE (PlantId, ReworkEventNumber);

ALTER TABLE postpaint.PostPaintReworkEvent
ADD CONSTRAINT CK_PostPaintReworkEvent_QtyBalance
CHECK (
    QtyIn >= 0
    AND (QtyOut IS NULL OR QtyOut >= 0)
    AND (QtyScrapped IS NULL OR QtyScrapped >= 0)
    AND (QtyOut IS NULL OR QtyScrapped IS NULL OR (QtyOut + QtyScrapped) <= QtyIn)
);

-- Defects per rework event (recommended)
CREATE TABLE postpaint.PostPaintReworkDefect (
    PostPaintReworkDefectId      INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_PostPaintReworkDefect PRIMARY KEY,
    PostPaintReworkEventId       INT NOT NULL,
    DefectTypeId                 INT NOT NULL,
    QuantityAffected             INT NOT NULL,
    DefectStageLookupId          INT NOT NULL, -- LookupValue where LookupType = 'REWORK_DEFECT_STAGE' (INCOMING/POST_REWORK)
    Notes                        NVARCHAR(500) NULL
);

ALTER TABLE postpaint.PostPaintReworkDefect
ADD CONSTRAINT FK_PostPaintReworkDefect_Event
FOREIGN KEY (PostPaintReworkEventId) REFERENCES postpaint.PostPaintReworkEvent(PostPaintReworkEventId);

ALTER TABLE postpaint.PostPaintReworkDefect
ADD CONSTRAINT FK_PostPaintReworkDefect_DefectType
FOREIGN KEY (DefectTypeId) REFERENCES quality.DefectType(DefectTypeId);

ALTER TABLE postpaint.PostPaintReworkDefect
ADD CONSTRAINT FK_PostPaintReworkDefect_Stage
FOREIGN KEY (DefectStageLookupId) REFERENCES dbo.LookupValue(LookupValueId);

ALTER TABLE postpaint.PostPaintReworkDefect
ADD CONSTRAINT CK_PostPaintReworkDefect_Qty
CHECK (QuantityAffected >= 0);
```

### Compact JSON Object

```json
{
  "entity": "postpaint.PostPaintReworkEvent",
  "purpose": "Close-loop tracking for BUFF/SAND/DEBURR rework with linkage to source inspection/load/run and final disposition.",
  "rls": { "enabled": true, "plantIdColumn": "PlantId" },
  "temporal": { "enabled": false, "useInstead": "workflow.StatusHistory" },
  "pk": "PostPaintReworkEventId",
  "unique": ["PlantId", "ReworkEventNumber"],
  "lookups": [
    { "table": "dbo.LookupValue", "type": "REWORK_TYPE", "values": ["BUFF", "SAND", "DEBURR"] },
    { "table": "dbo.LookupValue", "type": "REWORK_DEFECT_STAGE", "values": ["INCOMING", "POST_REWORK"] }
  ],
  "relationships": {
    "Plant": "dbo.Plant(PlantId)",
    "StatusCode": "dbo.StatusCode(StatusCodeId)",
    "ReworkType": "dbo.LookupValue(LookupValueId)",
    "ProcessArea": "dbo.ProcessArea(ProcessAreaId)",
    "ProductionLine": "dbo.ProductionLine(ProductionLineId)",
    "Customer": "dbo.Customer(CustomerId)",
    "Part": "dbo.Part(PartId)",
    "PrimaryDefectType": "quality.DefectType(DefectTypeId)",
    "OutcomeDisposition": "dbo.DispositionCode(DispositionCodeId)",
    "SourceProductionRunId": "ProductionRun(ProductionRunId) [PROPOSED]",
    "SourceLoadRecordId": "LoadRecord(LoadRecordId) [PROPOSED]",
    "SourceInspectionRecordId": "InspectionRecord(InspectionRecordId) [PROPOSED]"
  },
  "childEntities": [
    {
      "entity": "postpaint.PostPaintReworkDefect",
      "purpose": "Defect counts tied to a rework event (incoming vs post-rework).",
      "pk": "PostPaintReworkDefectId"
    }
  ]
}
```

---

## D.2 `logistics.Shipment` + `logistics.ShipmentLine`

### Purpose

Replace pack slip templates with a real shipment object and enforce traceability (shipment lines must link to run/load/lot).

### Key Fields — `logistics.Shipment`

| Field | Type | Null | FK Target | Notes |
|---|---|:---:|---|---|
| `ShipmentId` | int identity | NO | — | PK |
| `PlantId` | int | NO | `dbo.Plant` | RLS |
| `CustomerId` | int | NO | `dbo.Customer` | Required |
| `PackSlipNumber` | nvarchar(50) | NO | — | Customer reference |
| `ShipDateTime` | datetime2(0) | YES | — | — |
| `StatusCodeId` | int | NO | `dbo.StatusCode` | DRAFT/SHIPPED/VOID |
| `CarrierName` | nvarchar(100) | YES | — | — |
| `ProNumber` | nvarchar(50) | YES | — | — |
| `BillOfLadingNumber` | nvarchar(50) | YES | — | — |
| `Notes` | nvarchar(1000) | YES | — | — |

### Key Fields — `logistics.ShipmentLine`

| Field | Type | Null | FK Target | Notes |
|---|---|:---:|---|---|
| `ShipmentLineId` | int identity | NO | — | PK |
| `ShipmentId` | int | NO | `logistics.Shipment` | — |
| `PartId` | int | NO | `dbo.Part` | — |
| `QuantityShipped` | int | NO | — | — |
| `ProductionRunId` | int | YES | `ProductionRun` (proposed) | Enforce traceability |
| `LoadRecordId` | int | YES | `LoadRecord` (proposed) | Enforce traceability |
| `LotNumber` | nvarchar(50) | YES | — | Fallback trace token |
| `ReleaseTagNumber` | nvarchar(50) | YES | `CertificationRecord` (proposed) (INFERRED) | Ties to Approved Tag Tracking |
| `CertificationRecordId` | int | YES | `CertificationRecord` (proposed) | Optional until built |

### SQL-Style DDL

```sql
CREATE SCHEMA logistics;
GO

CREATE TABLE logistics.Shipment (
    ShipmentId              INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_Shipment PRIMARY KEY,
    PlantId                 INT NOT NULL,
    CustomerId              INT NOT NULL,
    PackSlipNumber          NVARCHAR(50) NOT NULL,
    ShipDateTime            DATETIME2(0) NULL,
    StatusCodeId            INT NOT NULL,
    CarrierName             NVARCHAR(100) NULL,
    ProNumber               NVARCHAR(50) NULL,
    BillOfLadingNumber      NVARCHAR(50) NULL,
    Notes                   NVARCHAR(1000) NULL,
    CreatedAt               DATETIME2(0) NOT NULL CONSTRAINT DF_Shipment_CreatedAt DEFAULT (SYSUTCDATETIME()),
    UpdatedAt               DATETIME2(0) NULL
);

ALTER TABLE logistics.Shipment
ADD CONSTRAINT FK_Shipment_Plant
FOREIGN KEY (PlantId) REFERENCES dbo.Plant(PlantId);

ALTER TABLE logistics.Shipment
ADD CONSTRAINT FK_Shipment_Customer
FOREIGN KEY (CustomerId) REFERENCES dbo.Customer(CustomerId);

ALTER TABLE logistics.Shipment
ADD CONSTRAINT FK_Shipment_StatusCode
FOREIGN KEY (StatusCodeId) REFERENCES dbo.StatusCode(StatusCodeId);

ALTER TABLE logistics.Shipment
ADD CONSTRAINT UQ_Shipment_Plant_PackSlip
UNIQUE (PlantId, PackSlipNumber);

CREATE TABLE logistics.ShipmentLine (
    ShipmentLineId          INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_ShipmentLine PRIMARY KEY,
    ShipmentId              INT NOT NULL,
    PartId                  INT NOT NULL,
    QuantityShipped         INT NOT NULL,
    UnitOfMeasure           NVARCHAR(20) NOT NULL CONSTRAINT DF_ShipmentLine_UOM DEFAULT ('EA'),
    ProductionRunId         INT NULL, -- FK to proposed ProductionRun
    LoadRecordId            INT NULL, -- FK to proposed LoadRecord
    LotNumber               NVARCHAR(50) NULL,
    ReleaseTagNumber        NVARCHAR(50) NULL,
    CertificationRecordId   INT NULL, -- FK to proposed CertificationRecord
    Notes                   NVARCHAR(1000) NULL
);

ALTER TABLE logistics.ShipmentLine
ADD CONSTRAINT FK_ShipmentLine_Shipment
FOREIGN KEY (ShipmentId) REFERENCES logistics.Shipment(ShipmentId);

ALTER TABLE logistics.ShipmentLine
ADD CONSTRAINT FK_ShipmentLine_Part
FOREIGN KEY (PartId) REFERENCES dbo.Part(PartId);

-- Enforce minimum traceability: require at least one linkage token
ALTER TABLE logistics.ShipmentLine
ADD CONSTRAINT CK_ShipmentLine_TraceToken
CHECK (ProductionRunId IS NOT NULL OR LoadRecordId IS NOT NULL OR LotNumber IS NOT NULL);

ALTER TABLE logistics.ShipmentLine
ADD CONSTRAINT CK_ShipmentLine_Qty
CHECK (QuantityShipped > 0);
```

### Compact JSON Object

```json
{
  "entity": "logistics.Shipment",
  "purpose": "Shipment header replacing pack slip templates; links shipped product to customer and shipping metadata.",
  "rls": { "enabled": true, "plantIdColumn": "PlantId" },
  "temporal": { "enabled": false },
  "pk": "ShipmentId",
  "unique": ["PlantId", "PackSlipNumber"],
  "relationships": {
    "Plant": "dbo.Plant(PlantId)",
    "Customer": "dbo.Customer(CustomerId)",
    "StatusCode": "dbo.StatusCode(StatusCodeId)"
  },
  "childEntities": [
    {
      "entity": "logistics.ShipmentLine",
      "purpose": "Shipment part/qty lines with enforced trace token (Run/Load/Lot).",
      "pk": "ShipmentLineId",
      "relationships": {
        "Shipment": "logistics.Shipment(ShipmentId)",
        "Part": "dbo.Part(PartId)",
        "ProductionRunId": "ProductionRun(ProductionRunId) [PROPOSED]",
        "LoadRecordId": "LoadRecord(LoadRecordId) [PROPOSED]",
        "CertificationRecordId": "CertificationRecord(CertificationRecordId) [PROPOSED]"
      },
      "constraints": ["ProductionRunId OR LoadRecordId OR LotNumber must be present"]
    }
  ]
}
```

---

## D.3 `production.DowntimeEvent`

### Purpose

Structured downtime capture that can roll up to OEE and correlate downtime to defects (by run).

### Key Fields (Minimum Viable)

| Field | Type | Null | FK Target | Notes |
|---|---|:---:|---|---|
| `DowntimeEventId` | int identity | NO | — | PK |
| `PlantId` | int | NO | `dbo.Plant` | RLS |
| `ProductionRunId` | int | NO | `ProductionRun` (proposed) | Required |
| `ProductionLineId` | int | NO | `dbo.ProductionLine` | Required |
| `DowntimeReasonLookupId` | int | NO | `dbo.LookupValue` | DOWNTIME_REASON |
| `ProcessAreaId` | int | YES | `dbo.ProcessArea` | Optional |
| `StartDateTime` | datetime2(0) | NO | — | — |
| `EndDateTime` | datetime2(0) | NO | — | — |
| `Notes` | nvarchar(1000) | YES | — | — |

### SQL-Style DDL

```sql
CREATE SCHEMA production;
GO

CREATE TABLE production.DowntimeEvent (
    DowntimeEventId              INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_DowntimeEvent PRIMARY KEY,
    PlantId                      INT NOT NULL,
    ProductionRunId              INT NOT NULL, -- FK to proposed ProductionRun
    ProductionLineId             INT NOT NULL,
    ProcessAreaId                INT NULL,
    DowntimeReasonLookupId       INT NOT NULL, -- LookupValue where LookupType = 'DOWNTIME_REASON'
    StartDateTime                DATETIME2(0) NOT NULL,
    EndDateTime                  DATETIME2(0) NOT NULL,
    Notes                        NVARCHAR(1000) NULL,
    CreatedAt                    DATETIME2(0) NOT NULL CONSTRAINT DF_DowntimeEvent_CreatedAt DEFAULT (SYSUTCDATETIME())
);

ALTER TABLE production.DowntimeEvent
ADD CONSTRAINT FK_DowntimeEvent_Plant
FOREIGN KEY (PlantId) REFERENCES dbo.Plant(PlantId);

ALTER TABLE production.DowntimeEvent
ADD CONSTRAINT FK_DowntimeEvent_ProductionLine
FOREIGN KEY (ProductionLineId) REFERENCES dbo.ProductionLine(ProductionLineId);

ALTER TABLE production.DowntimeEvent
ADD CONSTRAINT FK_DowntimeEvent_ProcessArea
FOREIGN KEY (ProcessAreaId) REFERENCES dbo.ProcessArea(ProcessAreaId);

ALTER TABLE production.DowntimeEvent
ADD CONSTRAINT FK_DowntimeEvent_Reason
FOREIGN KEY (DowntimeReasonLookupId) REFERENCES dbo.LookupValue(LookupValueId);

ALTER TABLE production.DowntimeEvent
ADD CONSTRAINT CK_DowntimeEvent_Time
CHECK (EndDateTime > StartDateTime);
```

### Compact JSON Object

```json
{
  "entity": "production.DowntimeEvent",
  "purpose": "Downtime event tied to ProductionRun for OEE and correlation to quality outcomes.",
  "rls": { "enabled": true, "plantIdColumn": "PlantId" },
  "temporal": { "enabled": false },
  "pk": "DowntimeEventId",
  "lookups": [
    { "table": "dbo.LookupValue", "type": "DOWNTIME_REASON", "values": "Seed from current downtime sheets" }
  ],
  "relationships": {
    "Plant": "dbo.Plant(PlantId)",
    "ProductionLine": "dbo.ProductionLine(ProductionLineId)",
    "ProcessArea": "dbo.ProcessArea(ProcessAreaId)",
    "DowntimeReason": "dbo.LookupValue(LookupValueId)",
    "ProductionRunId": "ProductionRun(ProductionRunId) [PROPOSED]"
  }
}
```

---

## D.4 `labor.ShiftStaffing` + `labor.ShiftStaffingAssignment`

### Purpose

Capture "who was working where" (line/booth/station) so defects and process data can be correlated to competency/training.

### Key Fields — `labor.ShiftStaffing`

| Field | Type | Null | FK Target | Notes |
|---|---|:---:|---|---|
| `ShiftStaffingId` | int identity | NO | — | PK |
| `PlantId` | int | NO | `dbo.Plant` | RLS |
| `StaffingDate` | date | NO | — | — |
| `ShiftId` | int | NO | `dbo.Shift` | — |
| `ProductionLineId` | int | YES | `dbo.ProductionLine` | — |
| `Notes` | nvarchar(1000) | YES | — | — |

### Key Fields — `labor.ShiftStaffingAssignment`

| Field | Type | Null | FK Target | Notes |
|---|---|:---:|---|---|
| `ShiftStaffingAssignmentId` | int identity | NO | — | PK |
| `ShiftStaffingId` | int | NO | `labor.ShiftStaffing` | — |
| `ProcessAreaId` | int | YES | `dbo.ProcessArea` | Booth/sanding/buffing |
| `RoleLookupId` | int | YES | `dbo.LookupValue` | LABOR_ROLE |
| `ExternalEmployeeRef` | nvarchar(50) | YES | — | Preferred (HR employee #) |
| `EmployeeName` | nvarchar(100) | YES | — | Day-1 migration (names/initials) |
| `StartTime` | time(0) | YES | — | — |
| `EndTime` | time(0) | YES | — | — |

### SQL-Style DDL

```sql
CREATE SCHEMA labor;
GO

CREATE TABLE labor.ShiftStaffing (
    ShiftStaffingId         INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_ShiftStaffing PRIMARY KEY,
    PlantId                 INT NOT NULL,
    StaffingDate            DATE NOT NULL,
    ShiftId                 INT NOT NULL,
    ProductionLineId        INT NULL,
    Notes                   NVARCHAR(1000) NULL,
    CreatedAt               DATETIME2(0) NOT NULL CONSTRAINT DF_ShiftStaffing_CreatedAt DEFAULT (SYSUTCDATETIME())
);

ALTER TABLE labor.ShiftStaffing
ADD CONSTRAINT FK_ShiftStaffing_Plant
FOREIGN KEY (PlantId) REFERENCES dbo.Plant(PlantId);

ALTER TABLE labor.ShiftStaffing
ADD CONSTRAINT FK_ShiftStaffing_Shift
FOREIGN KEY (ShiftId) REFERENCES dbo.Shift(ShiftId);

ALTER TABLE labor.ShiftStaffing
ADD CONSTRAINT FK_ShiftStaffing_Line
FOREIGN KEY (ProductionLineId) REFERENCES dbo.ProductionLine(ProductionLineId);

CREATE UNIQUE INDEX UQ_ShiftStaffing_UniqueDayShiftLine
ON labor.ShiftStaffing (PlantId, StaffingDate, ShiftId, ProductionLineId);

CREATE TABLE labor.ShiftStaffingAssignment (
    ShiftStaffingAssignmentId    INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_ShiftStaffingAssignment PRIMARY KEY,
    ShiftStaffingId              INT NOT NULL,
    ProcessAreaId                INT NULL,
    RoleLookupId                 INT NULL, -- LookupValue where LookupType = 'LABOR_ROLE'
    ExternalEmployeeRef          NVARCHAR(50) NULL,
    EmployeeName                 NVARCHAR(100) NULL,
    StartTime                    TIME(0) NULL,
    EndTime                      TIME(0) NULL,
    Notes                        NVARCHAR(500) NULL
);

ALTER TABLE labor.ShiftStaffingAssignment
ADD CONSTRAINT FK_ShiftStaffingAssignment_Header
FOREIGN KEY (ShiftStaffingId) REFERENCES labor.ShiftStaffing(ShiftStaffingId);

ALTER TABLE labor.ShiftStaffingAssignment
ADD CONSTRAINT FK_ShiftStaffingAssignment_ProcessArea
FOREIGN KEY (ProcessAreaId) REFERENCES dbo.ProcessArea(ProcessAreaId);

ALTER TABLE labor.ShiftStaffingAssignment
ADD CONSTRAINT FK_ShiftStaffingAssignment_Role
FOREIGN KEY (RoleLookupId) REFERENCES dbo.LookupValue(LookupValueId);

ALTER TABLE labor.ShiftStaffingAssignment
ADD CONSTRAINT CK_ShiftStaffingAssignment_Person
CHECK (ExternalEmployeeRef IS NOT NULL OR EmployeeName IS NOT NULL);
```

### Compact JSON Object

```json
{
  "entity": "labor.ShiftStaffing",
  "purpose": "Daily staffing header to connect operators to lines/stations for competency and correlation analysis.",
  "rls": { "enabled": true, "plantIdColumn": "PlantId" },
  "temporal": { "enabled": false },
  "pk": "ShiftStaffingId",
  "unique": ["PlantId", "StaffingDate", "ShiftId", "ProductionLineId"],
  "relationships": {
    "Plant": "dbo.Plant(PlantId)",
    "Shift": "dbo.Shift(ShiftId)",
    "ProductionLine": "dbo.ProductionLine(ProductionLineId)"
  },
  "childEntities": [
    {
      "entity": "labor.ShiftStaffingAssignment",
      "purpose": "Assignments of people to process areas/roles with optional time ranges.",
      "pk": "ShiftStaffingAssignmentId",
      "lookups": [
        { "table": "dbo.LookupValue", "type": "LABOR_ROLE", "values": ["PAINTER", "BOOTH_OPERATOR", "SANDING", "BUFFING", "DEBURRING", "QC"] }
      ],
      "relationships": {
        "ShiftStaffing": "labor.ShiftStaffing(ShiftStaffingId)",
        "ProcessArea": "dbo.ProcessArea(ProcessAreaId)",
        "Role": "dbo.LookupValue(LookupValueId)"
      }
    }
  ]
}
```

---

## D.5 `compliance.WasteDisposalEvent` (OPTIONAL / Scope Decision)

### Purpose

If Plant 2 must track waste for environmental compliance in the same platform, this is the minimal structure. If sf-quality is strictly "quality events only," then don't build this and keep it in EHS systems.

### Evidence Reality Check

The uploaded waste forms are largely blank templates; required fields for compliance are **UNKNOWN** from this evidence set.

### SQL-Style DDL

```sql
CREATE SCHEMA compliance;
GO

CREATE TABLE compliance.WasteDisposalEvent (
    WasteDisposalEventId     INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_WasteDisposalEvent PRIMARY KEY,
    PlantId                  INT NOT NULL,
    WasteTypeLookupId        INT NOT NULL, -- LookupValue where LookupType = 'WASTE_TYPE'
    EventDate                DATE NOT NULL,
    Quantity                 DECIMAL(12,3) NULL,
    UnitOfMeasure            NVARCHAR(20) NULL,
    ContainerCount           INT NULL,
    VendorName               NVARCHAR(200) NULL,
    ManifestNumber           NVARCHAR(100) NULL,
    Notes                    NVARCHAR(1000) NULL,
    CreatedAt                DATETIME2(0) NOT NULL CONSTRAINT DF_WasteDisposalEvent_CreatedAt DEFAULT (SYSUTCDATETIME())
);

ALTER TABLE compliance.WasteDisposalEvent
ADD CONSTRAINT FK_WasteDisposalEvent_Plant
FOREIGN KEY (PlantId) REFERENCES dbo.Plant(PlantId);

ALTER TABLE compliance.WasteDisposalEvent
ADD CONSTRAINT FK_WasteDisposalEvent_WasteType
FOREIGN KEY (WasteTypeLookupId) REFERENCES dbo.LookupValue(LookupValueId);
```

### Compact JSON Object

```json
{
  "entity": "compliance.WasteDisposalEvent",
  "purpose": "OPTIONAL: Waste tracking for compliance (booth sludge, waste paint, still bottoms, waste zinc, empties).",
  "rls": { "enabled": true, "plantIdColumn": "PlantId" },
  "temporal": { "enabled": false },
  "pk": "WasteDisposalEventId",
  "lookups": [
    { "table": "dbo.LookupValue", "type": "WASTE_TYPE", "values": ["BOOTH_SLUDGE", "WASTE_PAINT", "STILL_BOTTOMS", "WASTE_ZINC", "EMPTY_CONTAINERS"] }
  ],
  "evidenceGap": "Forms are blank templates; compliance-required fields (EPA/manifest requirements, units, vendor fields) must be confirmed with EHS process owner."
}
```
