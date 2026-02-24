# Cross-Plant Gap Tracker

**Purpose:** Track every gap identified across all plant audits, with severity, cross-plant frequency, engineering action items, and cross-repo alignment status.

**Last Updated:** 2026-02-24 (Plant 1 + Plant 2 fully synthesized)

---

## Gap Registry

| Gap ID | Gap Name | Severity | Plant 1 | Plant 2 | Plant 3 | Plant 4 | Plant 5 | Plant 6 | Plant 7 | Frequency | Engineering Action | Target Repo | Cross-Repo Status |
|--------|----------|----------|---------|---------|---------|---------|---------|---------|---------|-----------|-------------------|-------------|-------------------|
| GAP-01 | No formal NCR process | CRITICAL | YES | YES | — | — | — | — | — | 2/7 | NCR entity already built (migration 028, 35+ fields, 7-state lifecycle); adoption is the fix | All | **CLOSED by DB** — NCR entity production-ready. API has 19 endpoints (Phase 3 complete). App not started. |
| GAP-02 | Traceability chain breaks (load→unload→inspect→ship) | CRITICAL | YES | YES | — | — | — | — | — | 2/7 | ProductionRun + LoadRecord entities needed; FK chain: LoadRecord→ProductionRun→InspectionRecord→NCR. Plant 2 adds Shipment→InspectionRecord link needed. | DB, API | **DESIGNED** — Quality Forms Module (migrations 131-160) includes `inspection.ProductionRun`. Entity proposals approved. Blocked by QFM adjudication (8 pre-implementation blockers). |
| GAP-03 | Defect taxonomy fragmented | HIGH | YES | YES | — | — | — | — | — | 2/7 | Plant 1: 97 form strings → 38 audit types → 35 DB leaves. Plant 2: 78 form strings → ~46 types. Combined: 5 new DB leaves needed (DAM-MLD, DAM-DEF, TEX-SPT, APP-MOT, SPC-SWL). See DEFECT_TAXONOMY_MASTER.csv | DB | **PARTIALLY CLOSED** — DB has 12/35 taxonomy (migration 020). Plant 2 adds 5 new liquid-specific leaves + 8 substrate defect types. Wait for Plants 3-7 for full leaf set. |
| GAP-04 | No PPM/yield calculation possible (missing denominators) | HIGH | YES | YES | — | — | — | — | — | 2/7 | InspectionRecord must enforce QuantityInspected; ProductionRun must capture QuantityLoaded. Plant 2: zero of 16 inspection forms have Total Inspected field. | App (UI) | **DESIGNED** — QFM InspectionInstance has response fields. ProductionRun has quantity fields. UI enforcement needed at app layer. |
| GAP-05 | Disposition decisions not formally captured | HIGH | YES | PARTIAL | — | — | — | — | — | 2/7 | DB has 11 DispositionCodes (migration 018). Plant 1: 3 codes used. Plant 2: 4 codes used implicitly via routing buckets (Good/Buff/Repaint/Scrap). 7 codes never appear on any form. | App | **CLOSED by DB** — All 11 codes seeded. API disposition endpoint exists. Plant 2 adds RTS (Return to Supplier) via KB/Tesla molding rejects. |
| GAP-06 | Stale forms in circulation | MEDIUM | YES | YES | — | — | — | — | — | 2/7 | Document entity (migration 024) has NO RevisionNumber or SupersededById columns. Plant 2 worse: 205 obsolete + 32/84 stale + 2 forms from 2016. See GAP-19. | DB, App | **OPEN** — Document table exists but lacks revision control fields. See GAP-19 for remediation. |
| GAP-07 | Digital readiness (free-text, merged cells, no IDs) | HIGH | YES | YES | — | — | — | — | — | 2/7 | Platform enforces structured input via dropdowns, FK lookups, and Zod validation (app). Plant 2 adds #REF! and #DIV/0! errors in active forms. | App | **DESIGNED** — QFM field criteria system provides structured input framework. App Phase 4. |
| GAP-08 | Zero cost data on any form | HIGH | YES | YES | — | — | — | — | — | 2/7 | NCR entity has EstimatedCost + CostNotes fields (migration 028). Plant 2: Paint Kitchen Inventory has per-unit CAD costs (only cost data at either plant) but not linked to quality events. | App | **CLOSED by DB** — Cost fields exist on NCR. App needs cost entry UI in NCR workflow. |
| GAP-09 | Operators identified by initials only (no employee linkage) | MEDIUM | YES | PARTIAL | — | — | — | — | — | 2/7 | AppUser table exists. Plant 2 has some full names (Daily Painter Schedule) and Inspector IDs (Metelix). Better than Plant 1 but still no structured linkage. | App | **CLOSED by DB** — AppUser entity exists. QFM uses operator assignment. Adoption requires badge/login enforcement. |
| GAP-10 | No calibration references on any form | MEDIUM | YES | YES | — | — | — | — | — | 2/7 | CalibrationRecord exists (DB Phase 10). Plant 2 implies spectrophotometer for colour verification but no instrument ID or calibration status captured. | DB, API, App | **PARTIALLY CLOSED** — CalibrationRecord entity exists. Missing: FK from test results to calibration records. |
| GAP-11 | No GP-12 exit gate | MEDIUM | YES | PARTIAL | — | — | — | — | — | 2/7 | GP12Program entity proposed. Plant 2: Tesla GP-12 form exists but lacks all lifecycle elements (no entry/exit criteria, no duration, no sample size). | DB, API, App | **DESIGNED** — Entity proposal approved. Not yet in any migration. |
| GAP-12 | No dedicated Inspection entity | HIGH | YES | YES | — | — | — | — | — | 2/7 | QFM defines full inspection system. Plant 2 adds need for count-based InspectionDefectCount (routing inspection, not measurement-based). | DB, API, App | **DESIGNED (NO-GO)** — QFM blocked by 8 adjudication items. Plant 2 confirms count-based inspection pattern needed alongside measurement-based. |
| GAP-13 | Process parameters decoupled from quality outcomes | HIGH | YES | PARTIAL | — | — | — | — | — | 2/7 | ProcessParameterLog + Reading proposed. Plant 2: Metelix Application Tracker is the ONE exception — bridges process-to-quality per carrier. All others decoupled. | DB, API | **DESIGNED** — Entity proposals approved. Metelix pattern should be productized as standard. |
| GAP-14 | No production run / load record tracking entity | CRITICAL | YES | YES | — | — | — | — | — | 2/7 | Plant 2: Line 102 has partial carrier tracking; Lines 101/103 have essentially none. | DB, API, App | **DESIGNED** — QFM has ProductionRun. Consolidated proposal recommends production schema. |
| GAP-15 | Lab chemistry not digitized | MEDIUM | YES | YES | — | — | — | — | — | 2/7 | LabAnalysis + Reading proposed. Plant 2 adds: PaintBatch + ColourVerification entities (discrete batch model fundamentally different from Plant 1 continuous bath). | DB, API, App | **DESIGNED** — Entity proposals approved. Plant 2 confirms need for BOTH bath and batch chemistry models. |
| GAP-16 | GP-12 forms siloed per customer | HIGH | YES | PARTIAL | — | — | — | — | — | 2/7 | Plant 1: 14 GP-12 forms. Plant 2: 1 GP-12 form (Tesla only). Rollstamp/BMW and Metelix/Hummer likely require GP-12 per OEM standards but have no forms. | App | **DESIGNED** — QFM template system enables per-customer configuration. |
| GAP-17 | Operators use cavity/location codes instead of defect counts | HIGH | YES | -- | — | — | — | — | — | 1/7 | Not observed in Plant 2. May be Plant 1-specific (die-cast substrate). | DB, App | **DESIGNED** — QFM InspectionFinding can capture location. |
| GAP-18 | Extreme merged-cell complexity blocks automated migration | MEDIUM | YES | YES | — | — | — | — | — | 2/7 | Plant 2 has merged cells but not as extreme as Plant 1 BASF PB Ratio (~69K merged ranges). | App (tooling) | **ACKNOWLEDGED** — Not a platform schema gap. Migration tooling decision. |
| GAP-19 | No document revision control | HIGH | YES | YES | — | — | — | — | — | 2/7 | Plant 2: only 2 of 31 inspection forms have revision tracking (both Tesla). 58 known superseded clusters. DocumentRevision entity confirmed as urgent need. | DB, App | **OPEN** — Confirmed gap at both plants. Document table verified — no revision control. |
| GAP-20 | No packaging hold / shipment release entity | HIGH | YES | YES | — | — | — | — | — | 2/7 | Plant 2: Approved Tag Tracking abandoned since Nov 2018. No quality release field on any of 7 pack slip templates. | DB, API, App | **DESIGNED** — CertificationRecord entity proposal approved. Plant 2 confirms with Shipment.QualityReleaseStatus. |
| GAP-21 | Out-of-spec readings disconnected from NCR creation | HIGH | YES | YES | — | — | — | — | — | 2/7 | Plant 2: colour verification has visual override ("Visual assessment will always override numerical measurement data"). No auto-trigger. | API, App | **DESIGNED** — QFM defines InspectionNcrLink. Needs API workflow rule + audit trail for visual overrides. |
| GAP-22 | **Post-paint rework black hole** | CRITICAL | -- | YES | — | — | — | — | — | 1/7 | Plant 2-specific: Sanding/buffing/deburring tally sheets capture time + qty only. No defect cause, no source run, no outcome closure. Buffing Summary has 272 days of data with empty quality-relevant fields. | DB, API, App | **DESIGNED** — PostPaintReworkEvent entity proposed with lifecycle (DRAFT→OPEN→COMPLETE→VERIFIED). Links to source ProductionRun + InspectionRecord. |
| GAP-23 | **Inspection-to-NCR disconnect** | CRITICAL | -- | YES | — | — | — | — | — | 1/7 | Zero of 16 Plant 2 inspection forms reference NCR. Gate alarms are paper-only annotations. No escalation mechanism. This makes the entire NCR system (19 endpoints) unreachable from inspection. | API, App | **DESIGNED** — POST /v1/inspection/{id}/escalate needed. InspectionNcrLink from QFM provides soft/hard linking pattern. |
| GAP-24 | **Shipping-quality gate absent** | CRITICAL | -- | YES | — | — | — | — | — | 1/7 | No quality hold/release field on any pack slip. Approved Tag Tracking abandoned 2018. Physical segregation is the only quality control preventing shipment of rejected parts. | DB, API, App | **DESIGNED** — Shipment/PackSlip entity with QualityReleaseStatus (NOT_VERIFIED/RELEASED/HELD). CK_ShipmentLine_TraceToken constraint. |
| GAP-25 | **Line asymmetry (102 vs 101/103)** | HIGH | -- | YES | — | — | — | — | — | 1/7 | Line 102 has carrier tracking, robot programs, TPM, structured operating form. Lines 101/103 have minimal data capture. Platform must enforce uniform minimum data capture. | App | **OPEN** — Not a schema gap; platform enforces via mandatory fields per ProductionLine configuration. Line-level config entity may be needed. |
| GAP-26 | **No spec limits on process parameters** | HIGH | -- | YES | — | — | — | — | — | 1/7 | Only colour delta-Ecmc has documented spec limits. All spray/viscosity/temperature params collected without targets. CQI-12 Section 8 major nonconformance. | DB, API | **DESIGNED** — ProcessParameterReading needs SpecMin/SpecMax/TargetValue columns. API must compute InSpec from these at write time. |
| GAP-27 | **Customer requirements not referenced on inspection forms** | HIGH | -- | YES | — | — | — | — | — | 1/7 | No appearance standards, boundary samples, dimensional checks, or test method references. Only Y2XX references an external grid document (not included). | DB, App | **DESIGNED** — CustomerInspectionProfile needs CustomerSpecReference field. App must display customer requirements during inspection. |
| GAP-28 | **BRP/Spyder hidden customer** | MEDIUM | -- | YES | — | — | — | — | — | 1/7 | Full inspection program for 14+ BRP Spyder parts hidden as secondary KANBAN tab in Laval Tool Buff Inspection. No dedicated forms, pack slips, or trackers. | Human | **OPEN** — Requires business decision: create dedicated BRP customer profile or formalize under existing Laval/Rollstamp relationship. |

---

## Severity Distribution (Plant 1 + Plant 2)

| Severity | Plant 1 Only | Plant 2 New | Total |
|----------|-------------|-------------|-------|
| CRITICAL | 3 | 3 | 6 |
| HIGH | 12 | 3 | 15 |
| MEDIUM | 6 | 1 | 7 |
| LOW | 0 | 0 | 0 |

---

## Cross-Repo Closure Summary (Updated)

| Status | Count | Gaps |
|--------|-------|------|
| **CLOSED by DB** | 4 | GAP-01, GAP-05, GAP-08, GAP-09 |
| **PARTIALLY CLOSED** | 2 | GAP-03, GAP-10 |
| **DESIGNED (in QFM or entity proposals)** | 15 | GAP-02, GAP-04, GAP-07, GAP-11, GAP-12, GAP-13, GAP-14, GAP-15, GAP-16, GAP-17, GAP-20, GAP-21, GAP-22, GAP-23, GAP-24, GAP-26, GAP-27 |
| **OPEN (needs new work)** | 4 | GAP-06, GAP-19, GAP-25, GAP-28 |
| **ACKNOWLEDGED (non-schema)** | 1 | GAP-18 |
| **BLOCKED** | 1 | GAP-12 (QFM adjudication NO-GO) |

---

## Cross-Plant Frequency Analysis

| Frequency | Count | Gaps | Significance |
|-----------|-------|------|-------------|
| **2/7 (both plants)** | 20 | GAP-01 through GAP-16, GAP-18 through GAP-21 | Strong candidates for Phase 1 platform requirements |
| **1/7 (Plant 1 only)** | 1 | GAP-17 | May be Plant 1-specific (die-cast substrate cavity codes) |
| **1/7 (Plant 2 only)** | 7 | GAP-22 through GAP-28 | May be Plant 2/liquid-paint-specific or may appear at other plants |

---

## Notes

- Gap frequency updated for Plant 2 audit (2026-02-24)
- 20 of 21 Plant 1 gaps confirmed at Plant 2 (GAP-17 is the only gap not observed)
- 7 new Plant 2-specific gaps added (GAP-22 through GAP-28)
- Gaps appearing in both plants are strong candidates for Phase 1 platform requirements
- GAP-22 (post-paint rework) and GAP-23 (inspection-to-NCR disconnect) are the highest-impact new findings
- GAP-17 through GAP-21 sourced from ChatGPT Pro partial audit (unique findings not in Claude's Plant 1 report)
- GAP-22 through GAP-28 sourced from combined Claude + ChatGPT Plant 2 audits
- QFM = Quality Forms Module (Reference_Architecture/Quality_Forms_Module/) — migrations 131-160, currently NO-GO pending 8 adjudication blockers
- Cross-repo status validated against: DB migrations 001-150, API v0.3.0 (19 NCR endpoints), App Phase 1 (not started)
