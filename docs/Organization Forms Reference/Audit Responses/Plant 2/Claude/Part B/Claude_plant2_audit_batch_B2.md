# BATCH B2: Section 3A — Detailed Analysis: Customer Inspection Forms

## 3. Detailed Analysis by Category

### A. CUSTOMER INSPECTION FORMS

---

### A.1 Defect Taxonomy Extraction

Every customer inspection form has been parsed. Below is the complete defect extraction organized by customer, with tracking method and linkage evidence.

---

#### ROLLSTAMP / BMW (8.2.2.3.2.1)

| Defect Name | Category | Tracking | Gate Alarm? | Linked To |
|---|---|---|---|---|
| DIRT | Buff Required | Count | Yes (36) | Part #, Shift, Date |
| POPPING | Buff Required | Count | Yes (10) | Part #, Shift, Date |
| ORANGE PEEL END CAP | Buff Required | Count | Yes (10) | Part #, Shift, Date |
| ORANGE PEEL FACE | Buff Required | Count | Yes (20) | Part #, Shift, Date |
| THIN PAINT | Repaint Required | Count | Yes (8) | Part #, Shift, Date |
| SAG / RUN | Repaint Required | Count | Yes (10) | Part #, Shift, Date |
| OTHER (Repaint) | Repaint Required | Count | No | Part #, Shift, Date |
| BAD MASKING | Repaint Required | Count | Yes (20) | Part #, Shift, Date |
| STRINGS | Repaint Required | Count | Yes (20) | Part #, Shift, Date |
| BLISTERS | Repaint Required | Count | Yes (18) | Part #, Shift, Date |
| DELAM. | Extrusion Defect | Count | Yes (10) | Part #, Shift, Date |
| ZIPPER LINE | Extrusion Defect | Count | Yes (10) | Part #, Shift, Date |
| EXT. LINE | Extrusion Defect | Count | Yes (10) | Part #, Shift, Date |
| OTHER (Extrusion) | Extrusion Defect | Count | No | Part #, Shift, Date |

**Unique fields:** EXTRUSION DATE & RACK #, ASSEMBLY DATE, TOTAL SCRAP -9008/-9009 (scrap by part number). 14 defect categories. Has disposition (Good / Buff / Repaint / Extrusion). Has scrap tracking with explicit part-number scrap totals. No line reference. No operator. No rack/load linkage to production run. Gate alarms are embedded as column header annotations — not calculated fields.

---

#### MYTOX (8.2.2.3.3.2)

| Defect Name | Category | Tracking | Gate Alarm? | Linked To |
|---|---|---|---|---|
| THIN CLEAR | Repaint Required | Count | Yes (20) | Part #, Rack #, Colour, Shift, Date |
| THIN PAINT | Repaint Required | Count | Yes (20) | Part #, Rack #, Colour, Shift, Date |
| MOTTLING | Repaint Required | Count | Yes (20) | Part #, Rack #, Colour, Shift, Date |
| SAG / RUN | Repaint Required | Count | Yes (10) | Part #, Rack #, Colour, Shift, Date |
| DIRT | Repaint Required | Count | Yes (10) | Part #, Rack #, Colour, Shift, Date |
| PAINT SPITS | Repaint Required | Count | Yes (10) | Part #, Rack #, Colour, Shift, Date |
| E-COAT | Repaint Required | Count | Yes (30) | Part #, Rack #, Colour, Shift, Date |
| OTHER (Repaint) | Repaint Required | Count | No | — |
| DENT | Substrate Defect | Count | Yes (8) | Part #, Rack #, Colour, Shift, Date |
| OTHER (Substrate) | Substrate Defect | Count | No | — |
| SCRAP | Scrap | Count | Yes (1) | — |
| BUFF (total) | Buff Required | Count | No | — |

**Unique fields:** RACK #, COLOUR, INSPECTION CRITERIA / SPEC reference, LONG/SHORT designator (per part orientation), Paint Date + Inspection Date (two separate dates). 12 defect categories. Has RACK # — the only form besides Metelix Hummer that captures a carrier/rack reference at inspection. Gate alarm at 1 for SCRAP is noteworthy — any single scrap triggers quality notification. Sheet name "102 Line Inspection" confirms this form is Line 102-specific. E-COAT defect is anomalous for a liquid spray plant — this is a substrate defect (incoming e-coat from supplier), not a Plant 2 process defect.

---

#### LAVAL TOOL — Inspection (8.2.2.3.4.1)

| Defect Name | Category | Tracking | Gate Alarm? |
|---|---|---|---|
| ORANGE PEEL | Buff Required | Count | No |
| DIRT | Buff Required | Count | No |
| FIBER | Buff Required | Count | No |
| OTHER (Buff) | Buff Required | Count | No |
| THIN CLEAR | Repaint Required | Count | Yes (5) |
| THIN PAINT | Repaint Required | Count | Yes (5) |
| ORANGE PEEL | Repaint Required | Count | Yes (5) |
| SAG / RUN | Repaint Required | Count | Yes (5) |
| DIRT | Repaint Required | Count | Yes (5) |
| OTHER (Repaint) | Repaint Required | Count | No |
| FLASH | Molding Defect | Count | Yes (1) |
| OTHER (Molding) | Molding Defect | Count | No |

12 defect categories. Has PAINTED PART # (separate from Raw Part #) — the only form with explicit raw-to-painted part number tracking. 10 pre-populated parts with colour. Uniform gate alarms at 5 for all repaint defects. No rack/carrier. No operator.

---

#### LAVAL TOOL — Buff Inspection (8.2.2.3.4.2)

Primary sheet ("Laval Tool") has a reduced defect set: ORANGE PEEL, DIRT (buff); THIN CLEAR, THIN PAINT, ORANGE PEEL, SAG/RUN, DIRT (repaint); FLASH (molding). 8 defect categories. No gate alarms. This is a re-inspection form — checking buff output quality.

**Hidden Program Discovery:** Second sheet ("KANBAN SHEET") is a completely different form labeled "SPYDER R66 - CHALK WHITE" with 14 part numbers for a BRP Spyder program. Different defect set includes MOTTLING. This is a hidden second customer program (BRP/Can-Am) embedded in a Laval Tool file. Evidence: part numbers 705014522, 705014526, etc. match BRP Spyder component patterns. **This form should be reclassified under a separate BRP/Spyder customer category.**

---

#### METELIX — Standard Inspection (8.2.2.3.5.1)

| Defect Name | Category | Tracking | Gate Alarm? |
|---|---|---|---|
| DIRT | Buff Required | Count | No |
| FIBER | Buff Required | Count | No |
| OTHER (Buff) | Buff Required | Count | No |
| THIN CLEAR | Repaint Required | Count | No |
| THIN PAINT | Repaint Required | Count | No |
| SAG/RUN | Repaint Required | Count | No |
| DIRT | Repaint Required | Count | No |
| OTHER (Repaint) | Repaint Required | Count | No |
| Parting Line | Sanding Defect | Count | No |
| GOUGES | Sanding Defect | Count | No |
| Sanding Marks | Sanding Defect | Count | No |
| Dents | Sanding Defect | Count | No |
| Cracks | Sanding Defect | Count | No |

13 defect categories. No gate alarms. Has LINE field in header — the only generic Metelix form referencing which paint line. Unique: Sanding/Molding defect section with 5 substrate/sanding-specific defects not found on any other customer form. 9 part numbers pre-populated (C223 Spoiler + Y2XX Highwing components). No rack/carrier. No operator.

---

#### METELIX — Buff Inspection (8.2.2.3.5.2)

| Defect Name | Category | Tracking | Gate Alarm? |
|---|---|---|---|
| Snowballs | Buff Defect | Count | No |
| Dirt | Buff Defect | Count | No |
| Scratches | Buff Defect | Count | No |
| Haze | Buff Defect | Count | No |
| Other (Buff) | Buff Defect | Count | No |
| Dirt (Rework) | Rework | Count | No |
| Scratch (Rework) | Rework | Count | No |
| Burn Through | Rework | Count | No |
| Moulding | Rework | Count | No |

9 defect categories. Unique defects: SNOWBALLS, HAZE, BURN THROUGH — all buffing-specific defects not found on any paint inspection form. Disposition is Good / Return To Buff / Send To Rework. Only 2 part numbers (C223 Spoiler + Hummer Spoiler). Comments field present.

---

#### METELIX — Moulding-Sanding Inspection (8.2.2.3.5.3)

| Defect Name | Category | Tracking | Gate Alarm? |
|---|---|---|---|
| Sink Marks | Moulding Defect | Count (per piece) | No |
| Dents | Moulding Defect | Count (per piece) | No |
| Cracks | Moulding Defect | Count (per piece) | No |
| Thin Substrate | Moulding Defect | Count (per piece) | No |
| Parting Line | Sanding Defect | Count (per piece) | No |
| Gouges | Sanding Defect | Count (per piece) | No |
| Sanding Marks | Sanding Defect | Count (per piece) | No |

7 defect categories. This is a **pre-paint inspection form** — tracking raw substrate condition before painting. Unique: records whether defect was found on raw, primed, or painted parts (tri-state lifecycle column). Has Inspector field and Sander Inspection ID — the only form in Part B with an operator/inspector identifier. Part #, Hummer, Y2XX Wing designators in header. Sequential numbering (1–12 rows) suggests per-part tracking, not per-rack.

---

#### METELIX — Hummer Painted Inspection (8.2.2.3.5.4)

| Defect Name | Category | Tracking | Gate Alarm? |
|---|---|---|---|
| BUFF/DIRT | Buff Required | Count | No |
| BUFF/FIBER | Buff Required | Count | No |
| BUFF/RUN | Buff Required | Count | No |
| RW HIT | Rework | Count | No |
| RW/THIN CLEAR | Rework | Count | No |
| RW/THIN PAINT | Rework | Count | No |
| RW/ORANGE PEEL | Rework | Count | No |
| RW/SAG-RUN | Rework | Count | No |
| RW/DIRT | Rework | Count | No |
| RW/OVERSPRAY | Rework | Count | No |
| RW/MISSING PAINT | Rework | Count | No |
| RW/GOUGE | Rework | Count | No |
| RW/FISH EYE | Rework | Count | No |
| Other (Rework) | Rework | Count | No |
| Parting Line | Sanding Defect | Count | No |
| GOUGES | Sanding Defect | Count | No |
| Sanding Marks | Sanding Defect | Count | No |
| Sink Marks | Sanding Defect | Count | No |
| Dents | Sanding Defect | Count | No |
| Cracks | Sanding Defect | Count | No |

20 defect categories — the most detailed defect vocabulary in the entire plant. Unique defects not found elsewhere: OVERSPRAY, MISSING PAINT, FISH EYE, RW HIT, BUFF/RUN. Has CARRIER NUMBER — critical for traceability. Prefixed defect names (RW/ and BUFF/) indicate disposition is embedded in the defect code itself — a naming convention that conflates defect type with disposition decision. Single-part form (VG0247BL0PA Hummer Spoiler only), 12 rows per carrier.

---

#### METELIX — Y2XX Highwing Painted Inspection (8.2.2.3.5.6)

Structurally identical to Hummer Painted Inspection (8.2.2.3.5.4). Same 20 defect categories including FISH EYE, OVERSPRAY, MISSING PAINT. Has Carrier Number. References external document **"8.3.2.9.26 Y2XX High Wing Defect Inspection Grid"** — the only form that references an external inspection standard document. Single part (VG0241CMOPA), 20 carrier rows. Fixed colour: Carbon Flash Metallic.

---

#### METELIX — Hummer Spoiler Application Tracker (8.2.2.3.5.5)

> **This is NOT an inspection form — it's a hybrid production tracking + inspection form.**

**Unique structure:**

**Production Data Section:** Carrier #, Rework Y/N, Roller Initial, then per-stage spray parameters (Primer: Fluid/Atom/Fan/ml per 15sec; Base: same; Clear: same) with Comments

**Defect Section:** BUFF/DIRT, BUFF/FIBER, BUFF/RUN, RW HIT, RW/THIN CLEAR, RW/THIN PAINT, RW/ORANGE PEEL, RW/SAG-RUN, RW/DIRT, RW/OVERSPRAY

**Environmental Data:** Temp at Start/End, Humidity at Start/End, Booth Temp at Start/End

**This is the single most valuable form in Part B for the digital platform.** It's the only form that captures process parameters (spray settings) and inspection results on the same sheet, per carrier. It also captures environmental conditions. 48 carrier rows. Named operator field ("Name:"). This form bridges the Part A process-quality disconnect for at least one product.

---

#### KB COMPONENTS — Inspection (8.2.2.3.6.1)

| Defect Name | Category | Tracking | Gate Alarm? |
|---|---|---|---|
| ORANGE PEEL | Buff Required | Count | No |
| DIRT | Buff Required | Count | No |
| FIBER | Buff Required | Count | No |
| OTHER (Buff) | Buff Required | Count | No |
| THIN CLEAR | Repaint Required | Count | Yes (5) |
| THIN PAINT | Repaint Required | Count | Yes (5) |
| ORANGE PEEL | Repaint Required | Count | Yes (5) |
| SAG / RUN | Repaint Required | Count | Yes (5) |
| DIRT | Repaint Required | Count | Yes (5) |
| OTHER (Repaint) | Repaint Required | Count | No |
| Outgassing Popping | Molding Defect | Count | No |
| OTHER (Molding) | Molding Defect | Count | No |

12 defect categories. Structurally near-identical to Laval Tool Inspection. Sheet tab still named "Laval Tool" — confirmed copy-paste origin. Added: MOLDING DATE field, "Outgassing Popping" replaces "FLASH" in molding category. Gate alarms identical at 5. 4 part numbers (all Stoney Blue).

---

#### KB COMPONENTS — Buffing Inspection (8.2.2.3.6.2)

Same structure as KB Inspection but disposition changes: "RETURN TO BUFF" replaces "REQUIRES BUFFING." Sheet tab still named "Laval Tool." 12 defect categories. No gate alarms on buff section. Identical part numbers.

---

#### POLYCON/TESLA — Standard Inspection (8.2.2.3.7.2)

| Defect Name | Category | Tracking | Gate Alarm? |
|---|---|---|---|
| DIRT | Buff Required | Count | No |
| FIBER | Buff Required | Count | No |
| OTHER (DESCRIBE) | Buff Required | Count | No |
| DIRT | Repaint Required | Count | Yes (24) |
| THIN CLEAR | Repaint Required | Count | Yes (12) |
| THIN PAINT | Repaint Required | Count | Yes (10) |
| ORANGE PEEL | Repaint Required | Count | Yes (6) |
| SAG / RUN | Repaint Required | Count | Yes (6) |
| OTHER (DESCRIBE) | Repaint Required | Count | No |
| SPLAY | Molding Defect | Count | Yes (11) |
| FLASH | Molding Defect | Count | No |
| GAS MARK | Molding Defect | Count | No |
| OUTGASSING | Molding Defect | Count | No |
| EXTRUSION LINE | Molding Defect | Count | No |
| BLISTERS/PITMARK | Molding Defect | Count | No |
| CHATTER MARK | Molding Defect | Count | Yes (11) |

16 defect categories. Most extensive molding defect vocabulary: SPLAY, GAS MARK, OUTGASSING, EXTRUSION LINE, BLISTERS/PITMARK, CHATTER MARK. Has MOLDING DATE. Has revision history sheet (Rev 1 created 2023-01-02). Variable gate alarm thresholds (6–24). 2 parts (MS 9405930P, MX 9405929P). "OTHER (DESCRIBE)" suggests free-text entry — destructive to taxonomy normalization.

---

#### POLYCON/TESLA — Buff Inspection (8.2.2.3.7.1)

Two sheets: MS Tesla and MX Tesla (identical structure, different part).

| Defect Name | Category |
|---|---|
| FOAM MARKS | Buff OK |
| SNOW BALL | Buff OK |
| DIRT | Buff OK |
| SCRATCH | Buff OK |
| SAG / RUN | Repaint Required |
| ORANGE PEEL | Repaint Required |
| DIRT | Repaint Required |
| SAG / RUN | Repaint Required |
| ORANGE PEEL | Repaint Required |
| OTHER | Repaint Required |
| SPLAY | Molding Defect |
| FLASH | Molding Defect |
| SCRATCHES | Molding Defect |

13 defect categories. Unique: FOAM MARKS (buffing tool artifact), SNOW BALL. No gate alarms on buff form. 10 identical rows per part (daily tracking?).

---

#### POLYCON/TESLA — GP12 Inspection (8.2.2.3.7.3)

| Defect Name | Category |
|---|---|
| FOAM MARKS | Buff |
| SNOW BALL | Buff |
| SOLVENT POP | Buff |
| DIRT | Buff |
| ORANGE PEEL | Buff |
| SCRATCH | Buff |
| SAG / RUN | Repaint |
| SOLVENT POP | Repaint |
| DIRT | Repaint |
| ORANGE PEEL | Repaint |
| SAG / RUN | Repaint |
| OTHER | Repaint |
| SPLAY | Molding |
| FLASH | Molding |
| SCRATCHES | Molding |

15 defect categories. Delta from standard Tesla Buff Inspection: adds SOLVENT POP in both buff and repaint categories. Revision history present (Rev 1 created 2023-01-02). No entry/exit criteria. No lot/batch linkage. No time-limited containment window. No trigger definition. No formal closure mechanism. **This is functionally a slightly expanded version of the buff inspection form relabeled as "GP12."**

---

#### MISC CUSTOMERS (8.2.2.2.16)

| Defect Name | Category |
|---|---|
| ORANGE PEEL | Buff Required |
| SAG / RUN | Buff Required |
| DIRT | Buff Required |
| OTHER (Buff) | Buff Required |
| THIN CLEAR | Repaint Required |
| THIN PAINT | Repaint Required |
| MOTTLING | Repaint Required |
| SAG / RUN | Repaint Required |
| DIRT | Repaint Required |
| OTHER (Repaint) | Repaint Required |
| FLASH | Molding Defect |
| Other (Molding) | Molding Defect |

12 defect categories. Blank customer field. Last modified 2020 — stale. Two sheets (Misc + KANBAN SHEET) are structurally identical. Has BUFFED PARTS section with Good/Returned/Rework. INSPECTION CRITERIA / SPEC referenced in header but not populated.

---

### A.2 Cross-Customer Defect Comparison Matrix

| Defect Name | Rollstamp | Mytox | Laval | Metelix-Gen | Metelix-Hummer | Metelix-Y2XX | Tesla-Std | Tesla-GP12 | Tesla-Buff | KB Comp | Misc | Count |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| DIRT | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 11 |
| SAG/RUN | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 11 |
| ORANGE PEEL | ✓ | — | ✓ | — | — | — | ✓ | ✓ | ✓ | ✓ | ✓ | 7 |
| THIN CLEAR | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | — | ✓ | ✓ | 8 |
| THIN PAINT | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | — | ✓ | ✓ | 9 |
| FIBER | — | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | — | ✓ | — | 6 |
| FLASH | — | — | ✓ | — | — | — | ✓ | ✓ | ✓ | — | ✓ | 5 |
| MOTTLING | — | ✓ | — | — | — | — | — | — | — | — | ✓ | 2 |
| POPPING/OUTGASSING | ✓ | — | — | — | — | — | ✓ | — | — | ✓ | — | 3 |
| SPLAY | — | — | — | — | — | — | ✓ | ✓ | ✓ | — | — | 3 |
| BLISTERS | ✓ | — | — | — | — | — | ✓ | — | — | — | — | 2 |
| STRINGS | ✓ | — | — | — | — | — | — | — | — | — | — | 1 |
| BAD MASKING | ✓ | — | — | — | — | — | — | — | — | — | — | 1 |
| PAINT SPITS | — | ✓ | — | — | — | — | — | — | — | — | — | 1 |
| E-COAT | — | ✓ | — | — | — | — | — | — | — | — | — | 1 |
| DELAMINATION | ✓ | — | — | — | — | — | — | — | — | — | — | 1 |
| ZIPPER LINE | ✓ | — | — | — | — | — | — | — | — | — | — | 1 |
| OVERSPRAY | — | — | — | — | ✓ | ✓ | — | — | — | — | — | 2 |
| MISSING PAINT | — | — | — | — | ✓ | ✓ | — | — | — | — | — | 2 |
| FISH EYE | — | — | — | — | ✓ | ✓ | — | — | — | — | — | 2 |
| BURN THROUGH | — | — | — | — | — | — | — | — | — | — | — | 1* |
| SNOWBALLS | — | — | — | — | — | — | — | — | ✓ | — | — | 1 |
| FOAM MARKS | — | — | — | — | — | — | — | ✓ | ✓ | — | — | 2 |
| HAZE | — | — | — | — | — | — | — | — | — | — | — | 1* |
| SOLVENT POP | — | — | — | — | — | — | — | ✓ | — | — | — | 1 |
| GAS MARK | — | — | — | — | — | — | ✓ | — | — | — | — | 1 |
| CHATTER MARK | — | — | — | — | — | — | ✓ | — | — | — | — | 1 |
| EXTRUSION LINE | ✓ | — | — | — | — | — | ✓ | — | — | — | — | 2 |
| Parting Line | — | — | — | ✓ | ✓ | ✓ | — | — | — | — | — | 3 |
| GOUGES | — | — | — | ✓ | ✓ | ✓ | — | — | — | — | — | 3 |
| Sanding Marks | — | — | — | ✓ | ✓ | ✓ | — | — | — | — | — | 3 |
| Sink Marks | — | — | — | — | ✓ | ✓ | — | — | — | — | — | 2 |
| Dents | — | ✓ | — | ✓ | ✓ | ✓ | — | — | — | — | — | 4 |
| Cracks | — | — | — | ✓ | ✓ | ✓ | — | — | — | — | — | 3 |
| Thin Substrate | — | — | — | — | — | — | — | — | — | — | — | 1* |
| SCRATCHES | — | — | — | — | — | — | — | ✓ | ✓ | — | — | 2 |

*(\*Burn Through, Haze, and Thin Substrate appear only on Metelix Buff Inspection or Moulding-Sanding forms.)*

**Summary counts:**

- **Total unique defect strings across all Part B forms:** 42
- **Normalized to unique DefectType leaf nodes:** ~28 (after collapsing: DIRT appears in buff + repaint contexts → same defect, different disposition; SAG/RUN buff vs repaint → same defect; POPPING = OUTGASSING = SOLVENT POP cluster; BLISTERS = BLISTERS/PITMARK)
- **Plant 1 comparison:** Plant 1 had 97 unique strings → 38 normalized. Plant 2 has fewer strings (42) but comparable normalized count (28) because Metelix's detailed forms contribute concentrated vocabulary. Combined Plant 2 (Part A 7 + Part B 28 minus ~3 overlaps) = ~32 unique leaf defects.
- **Liquid paint coverage:** Core liquid defects ARE present: runs/sags (✓ universal), orange peel (✓ 7 of 11), dry spray (✗ MISSING), color mismatch (✗ MISSING), gloss failure (✗ MISSING), solvent pop (✓ GP12 only), fish eyes (✓ Metelix only), mottling (✓ 2 of 11). **Dry spray, colour mismatch, and gloss failure are absent from every inspection form — a significant gap for a liquid spray operation.**
- **Non-liquid defects present:** E-COAT (Mytox — incoming substrate), EXTRUSION LINE (Rollstamp, Tesla — substrate), ZIPPER LINE (Rollstamp — substrate). These are correctly classified as substrate/supplier defects, not borrowed from powder/e-coat templates.

---

### A.3 Customer Form Structural Comparison

| Structural Element | Rollstamp | Mytox | Laval | KB Comp | Tesla | Metelix-Gen | Metelix-Hummer/Y2XX | Misc |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **HEADER** | | | | | | | | |
| Paint Date | ✓ | ✓ (+ Insp Date) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Shift | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Line | — | — (102 in tab name) | — | — | — | ✓ | ✓ | — |
| Customer Name | Header title | Header title | Header title | Header title | Header title | Header title | Header title | Fill-in blank |
| Operator/Inspector | — | — | — | — | — | — | — | — |
| **BODY** | | | | | | | | |
| Part # (raw) | ✓ | ✓ | ✓ | ✓ | ✓ | — | — | ✓ |
| Part # (painted/FG) | — | — | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Colour | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Rack/Carrier # | — | ✓ | — | — | — | — | ✓ | — |
| Molding Date | — | — | — | ✓ | ✓ | — | — | — |
| Defect Quantitative | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Gate Alarms | ✓ (variable) | ✓ (variable) | ✓ (uniform 5) | ✓ (uniform 5) | ✓ (variable) | — | — | — |
| **DISPOSITION** | | | | | | | | |
| Good | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Buff Required | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Repaint Required | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Molding/Substrate | ✓ (Extrusion) | ✓ (Substrate) | ✓ (Molding) | ✓ (Molding) | ✓ (Molding) | ✓ (Sanding/Molding) | ✓ (Sanding/Molding) | ✓ (Molding) |
| Scrap (explicit) | ✓ | ✓ | — | — | — | — | — | — |
| **FOOTER** | | | | | | | | |
| Supervisor Sign-off | — | — | — | — | — | — | — | — |
| Comments | — | — | — | — | — | — | — | — |
| Total Inspected | — | — | — | — | — | — | — | — |
| Gate Alarm Instructions | — | ✓ | — | — | — | — | — | — |
| **TEST METHODS** | | | | | | | | |
| Adhesion | — | — | — | — | — | — | — | — |
| Film Build | — | — | — | — | — | — | — | — |
| Gloss | — | — | — | — | — | — | — | — |
| Colour/ΔE | — | — | — | — | — | — | — | — |

**Critical findings from structural comparison:**

1. **No supervisor sign-off on ANY inspection form.** Zero of 16 forms have an approval/sign-off field. This means inspection is self-certified by the inspector with no management oversight.
2. **No Total Inspected/Total Loaded field on ANY form.** Without this denominator, PPM cannot be calculated from inspection data. The TOTAL GOOD column exists but total throughput does not.
3. **Zero test method references.** No adhesion, no film build, no gloss, no colour measurement referenced on any customer inspection form. The colour verification form (8.2.2.26 from Part A) exists but is completely disconnected from customer inspection. IATF 16949 §8.6 requires documented acceptance criteria — these forms have defect checklists but no measurable acceptance criteria.
4. **Y2XX Highwing (8.2.2.3.5.6) references external document 8.3.2.9.26** — the only form that references an external inspection standard. This document was not included in the package and should be retrieved.

---

### A.4 Buff Inspection Form Analysis

Five customers have dedicated buff inspection forms: Laval Tool (8.2.2.3.4.2), Metelix (8.2.2.3.5.2), KB Components (8.2.2.3.6.2), Tesla (8.2.2.3.7.1), and Tesla GP12 (8.2.2.3.7.3, dual-purpose).

**Buffing is a re-inspection after rework, not a separate quality gate.** Evidence:

- Buff forms have a "Return to Buff" or "Requires Buffing" disposition, meaning parts that fail buff inspection go back through buffing again
- Defect categories on buff forms include defects introduced BY buffing (Burn Through, Haze, Foam Marks, Scratches) alongside original paint defects that survive buffing (Dirt, Orange Peel)
- The buff form is downstream of the paint inspection form — parts that were dispositioned as "Requires Buffing" on the paint inspection sheet are then tracked on the buff sheet

**The buff inspection form creates a second quality record for the same part that is NOT linked to the first.** There is no reference field connecting a buff inspection entry back to the original paint inspection entry that sent the part to buffing. This means rework cycles cannot be counted.

---

### A.5 GP-12 / Containment Evidence (Tesla GP12 — 8.2.2.3.7.3)

| GP-12 Requirement | Present? | Evidence |
|---|:---:|---|
| Entry criteria defined | **NO** | No trigger definition, no initiating event reference |
| Exit criteria defined | **NO** | No closure criteria, no minimum sample size, no time limit |
| Lot/batch linkage | **NO** | No lot, batch, production run, or carrier reference |
| Time-limited containment | **NO** | No start date, no end date, no duration |
| What triggers GP-12 vs normal | **NO** | No documented distinction |
| Escalation to NCR | **NO** | No NCR reference field |
| Sample size definition | **NO** | No AQL, no sampling plan reference |
| Customer notification | **NO** | No customer communication field |

The Tesla GP12 form is the standard Tesla Buff Inspection (8.2.2.3.7.1) with SOLVENT POP added in both buff and repaint categories. It has the same 2 parts (MS/MX Applique), same layout, and identical revision history. **This form would not pass a customer audit for GP-12 compliance.** A legitimate GP-12 requires defined containment actions, inspection frequency escalation, lot segregation, and documented entry/exit gates per AIAG CQI requirements.

---

### A.6 Metelix Deep Dive — 6 Forms

| Form | Purpose | Program | Unique Data |
|---|---|---|---|
| 8.2.2.3.5.1 Metelix Inspection | Post-paint visual inspection | C223 Spoiler + Y2XX Highwing (multi-part) | LINE field, sanding/molding defects |
| 8.2.2.3.5.2 Metelix Buff Inspection | Re-inspection after buffing | C223 + Hummer (2 parts) | Snowballs, Haze, Burn Through |
| 8.2.2.3.5.3 Moulding-Sanding Inspection | Pre-paint substrate quality | Hummer + Y2XX Wing | Raw/primed/painted tri-state, Inspector ID |
| 8.2.2.3.5.4 Hummer Painted Inspection | Post-paint per-carrier inspection | Hummer Spoiler (single part) | Carrier Number, 20 defect categories |
| 8.2.2.3.5.5 Hummer Spoiler Application Tracker | Spray parameters + inspection hybrid | Hummer Spoiler (single part) | Process params, environmental data, operator |
| 8.2.2.3.5.6 Y2XX Highwing Painted Inspection | Post-paint per-carrier inspection | Y2XX Highwing (single part) | Carrier Number, external spec reference |

**Assessment:** These are genuinely different forms serving different purposes — NOT relabeled copies. Metelix is the only customer with:

- Pre-paint inspection (Moulding-Sanding)
- Post-paint inspection (Painted Inspection, per carrier)
- Post-buff re-inspection (Buff Inspection)
- Combined process+quality tracking (Application Tracker)

The Hummer Spoiler Application Tracker (8.2.2.3.5.5) is particularly important because it bridges the Part A gap of process-quality disconnect. However, this level of rigor applies to only 2 of 10 Metelix part numbers (Hummer Spoiler and Y2XX Highwing). The remaining parts (C223 Spoiler + 7 Y2XX small components) use the generic Metelix Inspection form with far less detail.

---

### A.8 Inspection Entity Discovery

Based on all 16 customer inspection forms, the proposed `InspectionRecord` entity requires:

#### Core Fields

- `InspectionRecordId` (PK)
- `PlantId` (FK, RLS)
- `ProductionLineId` (FK, nullable)
- `ShiftId` (FK)
- `CustomerId` (FK)
- `PartId` (FK)
- `InspectionDate`
- `PaintDate` (may differ from InspectionDate per Mytox)
- `InspectorId` (FK to Employee — only Metelix Moulding-Sanding captures this)
- `InspectionTypeCodeId` (FK to LookupValue: PAINT, BUFF, GP12, PRE_PAINT, APPLICATION_TRACKING)
- `CarrierNumber` (nullable — only Mytox, Metelix Hummer/Y2XX capture)
- `RackNumber` (nullable)
- `MoldingDate` (nullable — KB, Tesla)
- `TotalGood`
- `TotalBuff`
- `TotalRepaint`
- `TotalMolding`
- `TotalScrap` (nullable — Rollstamp, Mytox only)
- `ExternalDocReference` (nullable — Y2XX references 8.3.2.9.26)

#### Child Records — InspectionDefectCount

- `InspectionDefectCountId` (PK)
- `InspectionRecordId` (FK)
- `DefectTypeId` (FK to quality.DefectType)
- `DispositionCodeId` (FK — derived from form section: BUFF→REWORK, REPAINT→RECOAT, MOLDING→RTS or SCRAP)
- `Quantity`
- `GateAlarmThreshold` (nullable — customer-specific)
- `GateAlarmTriggered` (computed)

#### Relationships

- `InspectionRecord` → `quality.NonConformanceReport` (nullable FK, for escalation — currently not used but MUST be built)
- `InspectionRecord` → `production.ProductionRun` (nullable FK — cannot populate from current forms, but needed for traceability)
- `InspectionRecord` → `CustomerInspectionProfile` (FK — defines which defects appear per customer per part)

#### Customer-Specific Handling

The `CustomerInspectionProfile` entity handles per-customer configuration without hard-coding:

- `CustomerInspectionProfileId` (PK)
- `CustomerId` (FK)
- `PartId` (FK, nullable for customer-wide)
- `InspectionTypeCodeId`
- `DefectTypeId` (FK)
- `GateAlarmThreshold` (nullable)
- `IsActive`
- `SortOrder`

This allows the same UI form to dynamically render the correct defect checklist per customer per part, with customer-specific gate alarm thresholds, without creating new forms.
