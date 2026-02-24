# BATCH B3: Section 3B–3C + Section 4

---

## B. SHIPPING / LOGISTICS FORMS

### B.1 Receiving Log (8.2.2.4.1)

**Structure:** 12 monthly tabs (Jan–Dec), identical layout per tab. Blank template — zero populated data.

**Fields captured:**

- Supplier/Customer
- PO / Packing Slip #
- Supplier Promise Date
- Date Received
- Time
- Accept (A) or Reject (R)
- Rejected Qty (if applicable)
- Initial (receiver)
- Distribution checkboxes: SUPPLY, QA/ENG
- Equipment Release Date

**Assessment:** This is a general-purpose intake log, not an incoming inspection form. The Accept/Reject field is binary with no defect classification, no reason code, and no dimensional check. There is no connection to incoming inspection criteria per IATF 16949 §8.4.2. The "DISTRIBUTE TO" columns (SUPPLY, QA/ENG) suggest a manual routing system — does the physical packing slip get photocopied and distributed? No lot number, no batch number, no material certificate reference.

**Traceability value:** LOW. The Receiving Log can tell you WHEN something arrived and WHO signed for it, but not WHAT condition it was in, not WHICH lot/batch it belongs to, and not WHERE it went after receipt. It cannot serve as a reliable traceability chain start point without significant enrichment.

**SCAR trigger mechanism:** NONE. A rejected incoming receipt has no escalation path. The Reject field has no link to Supplier SCAR, no defect code, and no follow-up tracking. Per the API, `v1/scar` exists as a thin placeholder — the receiving log would be the natural trigger point for SCAR initiation but currently provides zero structured data to populate one.

---

### B.2 Pack Slip Template Comparison

Seven pack slip templates were analyzed: 1 general + 6 customer-specific.

| Field | General (8.2.2.4.2) | Mytox (.11) | Rollstamp (.12) | Laval (.14) | KB Comp (.17) | Polycon (.18) | Metelix (.9) |
|---|---|---|---|---|---|---|---|
| SF Header (address, phone) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Customer Code (2-char) | PS | MY | RL | TK | BC | PYN | ME |
| Ship-To Address | Blank | ✓ (populated) | ✓ (populated) | ✓ (populated) | ✓ (populated) | ✓ (populated) | ✓ (populated) |
| Bill-To Address | Blank | Same | ✓ (different) | Same | Same | ✓ (different) | Same |
| PO # | Field exists | ✓ (B09852) | — | ✓ (63148) | ✓ (KB2004784) | ✓ (P206773-11) | ✓ (9697/9698) |
| Part Number | Field exists | ✓ (12+ parts) | ✓ (4 parts) | ✓ (10 parts) | ✓ (4 parts) | ✓ (2 parts) | ✓ (10 parts) |
| Part Description | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Colour | — | ✓ (embedded) | ✓ (column) | ✓ (column) | ✓ (column) | — | — |
| Additional Info field | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| # of Boxes/Skids | ✓ (Skids) | ✓ (Boxes) | ✓ (Boxes) | ✓ (Skids) | ✓ (Skids) | ✓ (Skids) | ✓ (Skids) |
| Total Parts Shipped | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Line # | — | — | ✓ | — | — | — | — |
| Short/Long designator | — | ✓ | — | — | — | — | — |
| Empties tracking | — | ✓ (2 EMPTIES) | ✓ (Blue/Green racks) | — | — | — | — |
| Date | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Ship Via | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Driver Print/Signature | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Shipper Initials | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Truck/Trailer # | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Total Weight | ✓ | — | — | ✓ | ✓ | — | — |
| Return Policy | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Quality hold/release | NO | NO | NO | NO | NO | NO | NO |
| Lot/Batch reference | NO | NO | NO | NO | NO | NO | NO |
| Inspection sign-off | NO | NO | NO | NO | NO | NO | NO |

**Structural verdict:** These are functionally identical. The core template is: SF header → Ship-To/Bill-To → Part table (Part #, Description, Qty, Boxes/Skids) → Totals → Shipping logistics (Date, Ship Via, Driver, Shipper). Customer-specific variants differ ONLY in:

1. Pre-populated customer address and part numbers
2. Container terminology (boxes vs skids)
3. Minor extra columns (Rollstamp has Line #; Mytox has Short/Long; Rollstamp and Mytox track empties/returnable racks)

These are **Tier 1 consolidation candidates** — one configurable PackSlip template with customer-specific address and part lookup, plus optional conditional columns for container type and empties tracking.

**Critical absence on ALL pack slips:** No lot/batch number. No production date reference. No inspection result reference. No quality release sign-off. A pack slip documents WHAT was shipped and HOW MANY, but provides zero link to WHEN it was produced, WHO inspected it, or WHETHER it passed inspection.

---

### B.3 Daily Shipping Report / Monthly Totals / Delivery Performance

#### Daily Shipping Report (8.2.2.4.3)

12 monthly tabs + 1 Totals tab. Monthly tabs contain: Packing Slip #, Date, Qty Shipped, Part#, Initial. Also includes a pivot table shell (Sum of Qty Shipped by Part#). Title says "P2 Metelix Daily Shipping Report" on most tabs but "P2 Laval Daily Shipping Report" on Dec tab — copy-paste error confirming this was adapted from another customer.

The Totals tab has monthly summaries (Jan–Dec) with annual total. Single data point visible: Jan 2024, initials "MH."

**KPI potential:** Can calculate monthly shipped qty per part. Cannot calculate on-time delivery (no due date), rejection rate (no return linkage), or quality-adjusted shipping.

#### Monthly Totals (8.2.2.4.4)

- **Sheet1:** Monthly matrix of Shipped / Returned / PPM by customer. Customers listed: Falcon Lakeside, Manterra, Metelix, Mitchell, Mytox, Rollstamp, Seastar Solutions, Laval Tools. PPM column labeled "Customer RPPM" (Return PPM).
- **Sheet2:** Historical volume ranking of 35 customers — many not in current Part B scope (Mark II, ABM, Presstran, Warren, FNG, Mercury, etc.). This is historical Plant 2 data predating current customer mix.

**KPI potential:** This is the ONLY form that calculates customer returns PPM. However, "Returned" is a raw count with no defect classification, no root cause, and no disposition. The PPM formula is Returns / Shipped × 1,000,000. This is customer-reported RPPM, not internal quality PPM.

#### Monthly Delivery Performance (8.2.2.4.5)

- **Monthly tab:** Weekly delivery % by customer (Manterra, Various System, BRP, Laval Tools, Mytox, Rollstamp-BMW, Rollstamp-Tesla). Columns: Quantity Due, Quantity Shipped, Delivery %. 5-week structure.
- **Daily tab:** Daily granularity for Mytox, Rollstamp-BMW, Rollstamp-Tesla only. Days 1–31, weekly subtotals.

**KPI potential:** This IS the delivery performance tracking system. Quantity Due vs Shipped per week = on-time delivery %. But "Quantity Due" is manually entered — not linked to customer releases or MRP. Customer scope is inconsistent with Monthly Totals (different customer lists). BRP appears here but has no inspection form. "Various System" is undefined.

**Connection to production and quality data:** NONE. Shipping reports reference packing slip numbers but not production run IDs, lot numbers, paint batch references, or inspection record numbers. Quality data (inspection pass rates, defect counts) exists in completely separate forms with no cross-reference key.

---

### B.4 Customer Demand/Production Trackers

Four customers have dedicated tracker workbooks: Polycon (8.2.2.4.19), Metelix (8.2.2.4.20), Laval (8.2.2.4.21), KB Components (8.2.2.4.22). These are the most sophisticated logistics tools in Plant 2.

**Common structure across all 4 trackers:**

| Sheet | Purpose | Data |
|---|---|---|
| Receiving | Inbound raw parts by week | Part #, Description, weekly qty received, running total |
| Shipping | Outbound finished goods by week | Packing Slip #, Date, Part #, Qty, Initial + weekly summaries |
| MRP | Demand vs shipped vs due | Part #, Line Type (demand/shipped/due/inv), daily or weekly grid |
| Releases | Customer release schedule | Release date, Part #, weekly cum demand, weekly totals |
| Waterfall | Release-over-release comparison | Multiple release dates stacked, showing demand changes over time |
| Parts Legend | Part number master | FG Part #, RAW Part #, Description, Part Pictures |

#### Tracker-specific unique features

**Metelix (8.2.2.4.20)** — Most comprehensive (9 sheets, 599 KB). Unique sheets:

- **Recovery:** Ship vs Release vs Owe tracking per date — explicit backlog visibility
- **RMA:** Return Material Authorization tracking with RMA numbers (ME228, ME238, ME255), dates, part states (Sanded RAW, Unsanded RAW, Painted). This is the ONLY form in the entire organization that tracks customer returns with any structure.
- **Summary:** Daily production totals by part with date-level granularity going back to Oct 2024
- Receiving includes MOLDED Part # → FG Part # mapping (raw-to-finished traceability at part master level)

**Laval (8.2.2.4.21)** — Has an Instructions sheet with step-by-step procedures for using the tracker, including password ("laval") for protected cells and a VBA button to export shipping log entries. Also unique: Shipping total aggregation tab. Shipping sheet has actual data: LT050 pack slips from Dec 2024 with specific quantities.

**KB Components (8.2.2.4.22)** — Releases sheet includes paint inventory management: Nippon Paint "Stoney Blue" consumption per set (1.8L per 10 sets), minimum stock levels, replenishment schedule with order dates. Also tracks masking tape consumption (GLT International supplier). This is rudimentary Bill of Materials tracking embedded in a shipping tracker.

**Polycon (8.2.2.4.19)** — Simplest of the 4. Only 2 parts (Tesla MS/MX Applique). Waterfall shows release-over-release for ~4 months. Clean template with active 2026 release data.

**Assessment:** These trackers are functioning as a **manual ERP system**. They integrate receiving, MRP, shipping, release management, and inventory tracking in a single Excel workbook per customer. The Metelix tracker even handles RMA (returns). This is operationally useful but creates critical platform design questions:

> **Are these quality-platform entities or ERP-domain entities?**
>
> - The MRP, Releases, and Waterfall sheets are demand planning tools — these belong in ERP/MRP, not quality.
> - The Receiving and Shipping sheets contain traceability-relevant data that DOES belong in the quality platform.
> - The Metelix RMA sheet bridges quality and logistics — returns are quality events that also have logistics implications.

**Recommendation:** The sf-quality platform should consume a subset of tracker data (receiving, shipping, RMA) via integration, NOT replicate the full tracker functionality. The MRP/Release/Waterfall sheets should remain in ERP or a dedicated planning tool.

---

### B.5 Shipping-Release Evidence

**Is there an explicit quality hold/release gate before shipping?**

**NO.** There is no form, field, checkbox, sign-off, or any documented mechanism that connects quality inspection results to shipping authorization across ANY of the 15 shipping forms. The evidence is comprehensive:

- Pack slips have no inspection reference field
- Daily Shipping Reports have no quality status column
- Customer trackers have Receiving and Shipping sheets but no Quality/Inspection sheet
- The Receiving Log has Accept/Reject but no outbound quality release equivalent
- No "Quality Release" or "Ship Authorization" form exists in the Part B package

Parts move from inspection → packing → shipping with no documented quality gate. The only implicit gate is the inspection form disposition itself (Good = can ship, Buff = hold for rework, Repaint = hold for rework), but there is no mechanism to verify that ONLY "Good" parts reach the shipping dock.

---

### B.6 Traceability Endpoint Assessment

**Can a shipment be traced back through: pack slip → production run → load record → paint batch → coating parameters?**

| Chain Link | Can Connect? | Evidence | Blocker |
|---|---|---|---|
| Pack Slip → Inspection Record | NO | No inspection reference on any pack slip | No shared key (no lot #, no production date on pack slip) |
| Pack Slip → Production Run | NO | No production run ID, no paint date, no line reference on pack slips | Part # is the only shared field — insufficient for date-level traceability |
| Inspection Record → Production Run | NO | Inspection forms have Paint Date and sometimes Line, but no run ID | Could reconstruct via (Line + Date + Part) composite key, but unreliable |
| Inspection Record → Load Record | PARTIAL | Mytox has Rack #; Metelix Hummer/Y2XX has Carrier Number | Only 3 of 16 inspection forms capture carrier/rack |
| Production Run → Paint Batch | NO (from Part A) | Paint batch tracked on separate tally sheet with no production run reference | Confirmed Part A finding |
| Paint Batch → Coating Parameters | NO (from Part A) | Parameters on Line 102 Operating Form, batch on Paint Tally, no cross-reference | Confirmed Part A finding |
| Pack Slip → Customer Tracker (Shipping) | YES | Pack slip # appears on customer tracker Shipping sheets | Laval tracker has actual PS# data (LT050) |
| Customer Tracker → Receiving (inbound) | YES | Trackers have Receiving sheets with weekly inbound quantities | Quantity-level only, not lot-level |

The traceability chain is **broken at every link except the logistics layer** (pack slip ↔ customer tracker). A customer complaint referencing a specific shipment (pack slip number) can identify WHAT was shipped and WHEN, but cannot trace back to which production run, which paint batch, which coating parameters, or which inspection record covers those parts.

**The single exception:** Metelix Hummer Spoiler Application Tracker (8.2.2.3.5.5) captures carrier-level spray parameters AND defect counts on the same form. For this one product, a carrier number can theoretically link process parameters to quality outcomes. But this form doesn't connect to the pack slip either.

---

### B.7 Packaging/Shipping Entity Discovery

Based on all 15 shipping forms, the following entities are needed:

#### `logistics.PackSlip` (quality-adjacent, not core quality)

- PackSlipId (PK), PackSlipNumber (generated per customer sequence), PlantId (FK, RLS), CustomerId (FK), ShipToAddressId (FK), BillToAddressId (FK), ShipDate, ShipVia, DriverName, TruckTrailerNumber, ShipperInitials, TotalBoxesOrSkids, TotalParts, TotalWeight (nullable), Notes
- **Child:** `PackSlipLineItem` — PackSlipLineItemId, PackSlipId (FK), PartId (FK), Quantity, ContainerCount, PurchaseOrderNumber, AdditionalInfo

#### `logistics.ReceivingLog` (quality-adjacent)

- ReceivingLogEntryId (PK), PlantId (FK, RLS), SupplierId (FK) or CustomerId (FK for returns), PackingSlipNumber, PurchaseOrderNumber (nullable), SupplierPromiseDate (nullable), DateReceived, TimeReceived, AcceptReject (A/R), RejectedQty (nullable), ReceiverInitials, DistributeToSupply (bool), DistributeToQAEng (bool), EquipmentReleaseDate (nullable)

#### `logistics.CustomerTracker`

NOT recommended as a platform entity. These are planning/logistics tools that should remain in Excel or migrate to ERP. The sf-quality platform should instead consume shipping and receiving events from these trackers via integration points, not replicate MRP/waterfall/release functionality.

#### `logistics.ReturnMaterialAuthorization` (quality entity — FROM Metelix RMA sheet)

- RmaId (PK), RmaNumber, PlantId (FK, RLS), CustomerId (FK), PartId (FK), RmaDate, PartState (Sanded RAW / Unsanded RAW / Painted), Quantity, NcrId (FK to `quality.NonConformanceReport` — for linking returns to quality events)

> This entity bridges the gap between customer returns (logistics) and quality investigation (NCR/CAPA).

---

## C. FORM CONSOLIDATION ANALYSIS

### Tier 1 — Identical (One configurable form replaces multiple)

| Group | Forms | Overlap % | Justification |
|---|---|---|---|
| Pack Slips | 8.2.2.4.2, 8.2.2.4.9, 8.2.2.4.11, 8.2.2.4.12, 8.2.2.4.14, 8.2.2.4.17, 8.2.2.4.18 | 95% | Identical structure: SF header → customer address → part table → shipping logistics → return policy. Differences are only pre-populated customer data and container terminology (boxes vs skids). One template with customer lookup replaces all 7. |
| Customer Trackers | 8.2.2.4.19, 8.2.2.4.21, 8.2.2.4.22 | 90% | Polycon, Laval, KB Components trackers have identical sheet structure (Receiving, Shipping, MRP, Releases, Waterfall, Parts Legend). Differences: Laval has Instructions + Shipping Total tabs; KB has paint inventory tracking rows. One configurable multi-sheet tracker per customer. |

**Tier 1 savings:** 7 pack slips → 1 template. 3 trackers → 1 template. **Net: 10 forms → 2.**

---

### Tier 2 — Minor Variants (One form with conditional sections)

| Group | Forms | Overlap % | Justification |
|---|---|---|---|
| Standard Paint Inspection | 8.2.2.3.4.1 (Laval), 8.2.2.3.6.1 (KB), 8.2.2.3.7.2 (Tesla), 8.2.2.2.16 (Misc) | 85% | All share: header (Date/Shift/Customer) → Part table → 4-section disposition (Good/Buff/Repaint/Molding) → per-defect count columns. Differences: defect list per customer, gate alarm thresholds, some have Painted Part # or Molding Date. One form with CustomerInspectionProfile-driven defect list and conditional fields. |
| Standard Buff Inspection | 8.2.2.3.4.2/Laval Tool sheet (Laval), 8.2.2.3.6.2 (KB), 8.2.2.3.7.1 (Tesla) | 85% | Identical 4-section layout with reduced defect list. KB sheet tab still named "Laval Tool." Differences: defect list, Tesla has 2 program sheets (MS/MX). One buff inspection form with customer-driven defect config. |
| Rollstamp + Mytox Inspection | 8.2.2.3.2.1, 8.2.2.3.3.2 | 80% | Same 4-section structure but with customer-specific fields: Rollstamp has Extrusion Date/Rack#/Assembly Date + extrusion-specific defects; Mytox has Rack#/Colour/Long-Short + e-coat substrate defect + separate Paint Date/Inspection Date. These are close enough to consolidate with conditional sections but have more unique fields than the Laval/KB/Tesla group. |

**Tier 2 savings:** 4 standard inspections → 1. 3 buff inspections → 1. 2 Rollstamp/Mytox → 1. **Net: 9 forms → 3.**

---

### Tier 3 — Genuinely Unique (Dedicated templates needed)

| Form | Why Unique |
|---|---|
| 8.2.2.3.5.1 Metelix Inspection | Sanding/Molding 5-defect section not on any other form; LINE field; multi-program (C223 + Y2XX components) |
| 8.2.2.3.5.2 Metelix Buff Inspection | Buffing-specific defects (Snowballs, Haze, Burn Through) unique to Metelix; Comments field |
| 8.2.2.3.5.3 Metelix Moulding-Sanding Inspection | Pre-paint inspection — entirely different purpose; raw/primed/painted tri-state; Inspector ID; Sander Inspection ID |
| 8.2.2.3.5.4 Metelix Hummer Painted Inspection | Per-carrier inspection with 20 defect categories, Carrier Number; single-product form |
| 8.2.2.3.5.5 Metelix Hummer Spoiler Application Tracker | Hybrid process+quality form; spray parameters per stage; environmental data; operator; unique in the entire organization |
| 8.2.2.3.5.6 Metelix Y2XX Highwing Painted Inspection | Per-carrier, external spec reference, single-product; structurally identical to Hummer but different product |
| 8.2.2.3.7.3 Tesla GP12 Inspection | Must remain separate even though structurally similar to buff inspection — GP-12 has regulatory/customer mandate significance and needs containment metadata added |
| 8.2.2.3.4.2/KANBAN (BRP Spyder) | Hidden BRP program form — different customer, different parts, should be reclassified |
| 8.2.2.4.20 Metelix Demand Tracker | 9 sheets including RMA and Recovery — significantly more complex than other trackers |
| 8.2.2.4.1 Receiving Log | Unique function (intake) |
| 8.2.2.4.3 Daily Shipping Report | Unique function (shipping log with pivot) |
| 8.2.2.4.4 Monthly Totals | Unique function (PPM tracking) |
| 8.2.2.4.5 Delivery Performance | Unique function (OTD tracking) |

**Tier 3 count:** 13 forms that need dedicated or significantly customized templates.

---

### Consolidation Summary

**31 forms → 18** (2 Tier 1 templates + 3 Tier 2 templates + 13 Tier 3). **42% reduction.** This compares to Plant 1's finding of 80%+ consolidation opportunity — Plant 2 has genuinely more complex customer requirements (primarily due to Metelix's 6 differentiated forms).

However, even the Tier 3 "unique" forms share a common digital backbone: `InspectionRecord` + `InspectionDefectCount` with `CustomerInspectionProfile`-driven configuration. The UI should render a single inspection workflow that dynamically adapts per customer/product, not 18 separate screens.

---

## 4. Critical Gap Analysis

### Gap 1: The Defect Taxonomy Gap

**Fragmentation assessment:** 42 unique defect strings across 16 customer inspection forms, normalizing to ~28 leaf DefectType entries. Fragmentation is moderate — lower than Plant 1's 97 strings because Plant 2 has fewer customers with more consistent naming (Metelix's RW/ prefix convention is actually systematic, even if conflated with disposition).

**Cross-customer inconsistency is the real problem:**

- **DIRT** appears on 11 of 11 form families but is split between buff-disposition and repaint-disposition with no distinction in the defect name itself
- **ORANGE PEEL** appears on 7 forms in buff context and repaint context — same defect, different severity thresholds
- Metelix uses prefixed names (RW/THIN CLEAR, BUFF/DIRT) that embed disposition in the defect code; all other customers separate defect from disposition structurally
- Three critical liquid paint defects are **ABSENT** from every form: dry spray, colour mismatch, gloss failure

**Compared to Plant 1:** Plant 2's 42 strings are cleaner than Plant 1's 97, but the normalized yield (~28 vs ~38) shows Plant 2 has less defect vocabulary coverage. The Metelix Hummer/Y2XX forms contribute 60% of the unique defect types — without Metelix, Plant 2 would have a dangerously thin taxonomy.

**Evidence:** All 16 inspection forms in 8.2.2.3.\*; taxonomy extraction in Section 3A.2. **Confidence: High.**

---

### Gap 2: The Inspection-to-NCR Gap

**When a defect is found on an inspection form, is there any mechanism to trigger an NCR?**

**NO.** Zero of 16 inspection forms have:

- An NCR reference field
- An escalation trigger (e.g., "if gate alarm exceeded, create NCR")
- A hold tag reference
- A quality alert reference
- Any linkage to the `quality.NonConformanceReport` entity

The gate alarm system (present on Rollstamp, Mytox, Laval, KB, Tesla forms) is the closest thing to an escalation trigger. Mytox's form includes the instruction: *"Quality Gate Alarms: Once Gate Alarm reached, STOP, Notify Quality Immediately."* But this is a printed instruction on paper — there is no structured mechanism to create, track, or close the resulting quality event. The notification presumably happens verbally, and any follow-up action exists only in memory.

**This is the single most critical gap for the digital platform.** The entire NCR lifecycle (DRAFT → OPEN → CONTAINED → INVESTIGATING → DISPOSED → PENDING_VERIFICATION → CLOSED) with its 25 API endpoints is useless if there's no mechanism to CREATE an NCR from the inspection process where defects are actually discovered.

**Evidence:** All 16 inspection forms examined for NCR-related fields; gate alarm instructions on 8.2.2.3.3.2/R20. **Confidence: High.**

---

### Gap 3: The Customer Requirements Gap

**Are customer-specific inspection requirements documented on the forms, or assumed knowledge?**

**Assumed knowledge.** The inspection forms have defect checklists but:

- No reference to customer-specific appearance standards or boundary samples
- No reference to customer engineering specifications
- No reference to customer PPAP acceptance criteria
- No dimensional check fields (no measurement values, no tolerances)
- No test method references (adhesion, film build, gloss, colour)
- **One exception:** Y2XX Highwing (8.2.2.3.5.6) references document "8.3.2.9.26 Y2XX High Wing Defect Inspection Grid" — which was NOT included in the package

Gate alarm thresholds (where present) are the only customer-specific acceptance criteria documented ON the form. But gate alarms are defect COUNT thresholds, not appearance or dimensional acceptance criteria.

The Part A colour verification form (8.2.2.26) with ΔEcmc data and pass/fail criteria exists but is completely disconnected from any customer inspection form. An inspector checking parts against a Rollstamp BMW inspection sheet has no link to the colour verification results for that batch.

**Evidence:** Structural comparison matrix in Section 3A.3; Y2XX reference at 8.2.2.3.5.6/Spoilers/R01. **Confidence: High.**

---

### Gap 4: The GP-12 Gap

**Beyond Polycon/Tesla, do other customers have GP-12 requirements?**

Unknown from forms alone, but likely **YES**. Rollstamp/BMW programs typically require GP-12 for launch and quality containment per BMW SQ standards. No Rollstamp GP-12 form exists. No Metelix GP-12 form exists despite Hummer (GM) programs that would normally require GP-12 per GM 1927 requirements. No Laval Tool GP-12 form exists.

The single Tesla GP12 form (8.2.2.3.7.3) lacks every essential GP-12 element as documented in Section 3A.5. GP-12 inspection results do NOT flow to shipping release decisions — there is no linkage between the GP12 form and any pack slip or shipping authorization.

**Evidence:** 8.2.2.3.7.3 analysis in Section 3A.5; absence of GP-12 forms for other customers confirmed by full inventory. **Confidence: High** (for Tesla gap); **Medium** (for inferred gaps at other customers).

---

### Gap 5: The Shipping-Quality Disconnect

**Is there any linkage between quality inspection results and shipping authorization?**

**NO.** Comprehensively documented in Section 3B.5. No quality hold/release gate exists. No pack slip references inspection status. No shipping report includes quality status. The customer trackers (Receiving/Shipping/MRP) operate in a completely separate data universe from inspection forms.

**The practical implication:** If an inspector rejects a batch of parts on the inspection form (dispositioned as "Requires Repaint"), there is no system-enforced mechanism to prevent those parts from being packed and shipped. The only control is physical — parts in the "repaint" area vs the "good" area on the shop floor. If parts are physically misrouted, the pack slip will record them as shipped with no quality flag.

**Evidence:** All 7 pack slip templates, 4 customer trackers, Daily Shipping Report, Delivery Performance analyzed in Section 3B. **Confidence: High.**

---

### Gap 6: The Cost Visibility Gap

**Can customer chargebacks, scrap costs, and rework costs be calculated from these forms?**

**NO for chargebacks and rework costs. PARTIAL for scrap.**

- **Chargebacks:** No chargeback tracking exists anywhere in Part B. The Metelix RMA sheet (8.2.2.4.20/RMA) tracks return quantities but not cost.
- **Scrap costs:** Rollstamp (8.2.2.3.2.1) has TOTAL SCRAP by part number. Mytox (8.2.2.3.3.2) has SCRAP count with gate alarm at 1. No other customer form has explicit scrap tracking. No cost per unit exists on any form.
- **Rework costs:** Buff/Repaint quantities are tracked on inspection forms but not costed. The Part A Buffing Summary (8.2.2.30) tracks daily KPIs but critical input fields are unpopulated.
- **Monthly Totals (8.2.2.4.4):** Tracks Returned PPM per customer but not return cost.

The NCR entity has `EstimatedCost` and `CostNotes` fields, plus the Part A proposal included `NcrCostLedger` concepts. But since no NCRs are being created from inspection data, the cost infrastructure has nothing to cost.

**Evidence:** Scrap fields on 8.2.2.3.2.1/BMW/R11, 8.2.2.3.3.2/102 Line Inspection/R03; RMA on 8.2.2.4.20/RMA; Monthly Totals on 8.2.2.4.4/Sheet1. **Confidence: High.**

---

### Gap 7: End-to-End Traceability Completeness Assessment

Combining Part A (operational) and Part B (customer/shipping) findings:

| Chain Segment | Score (0–5) | Status | Evidence |
|---|---|---|---|
| Raw Receipt → Loading | 1/5 | Receiving Log captures date and Accept/Reject. No lot/batch. No material linkage to production. | 8.2.2.4.1 |
| Loading → Coating | 2/5 | Load sheets exist (Part A). Line 102 has carrier tracking. Lines 101/103 have none. No link from load to paint batch. | Part A: 8.2.2.1.5, 8.2.2.2.7 |
| Coating → Inspection | 1/5 | Inspection has Paint Date and sometimes Line. No production run ID, no carrier link (except Mytox rack#, Metelix Hummer/Y2XX carrier#). | 8.2.2.3.\*.\* |
| Inspection → Post-Paint | 0/5 | Zero linkage. Inspection disposition "Requires Buffing" has no reference on buff inspection form. Rework cycles uncounted. | 8.2.2.3.\*.\* buff forms |
| Post-Paint → Packing | 0/5 | No documented quality release gate. | Absence of any release form |
| Packing → Shipping | 3/5 | Pack slip captures Part#, Qty, Date. Customer trackers link pack slip # to shipping records. But no lot/batch, no quality reference. | 8.2.2.4.\* pack slips and trackers |
| **End-to-End** | **7/30 = 23%** | **Broken at every internal link. Only logistics layer (pack slip ↔ tracker) has reliable connectivity.** | — |

**Comparison to Plant 1:** Plant 1 scored approximately 20% on traceability. Plant 2 scores marginally better (23%) due to the Metelix Application Tracker bridging process-to-quality for one product, and customer trackers providing pack-slip-to-shipping linkage. But the internal chain (receipt → coating → inspection → shipping) is equally broken.
