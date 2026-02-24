# BATCH B5: Appendix A + Appendix B

---

## Appendix A: Complete Defect Taxonomy Mapping Table (Merged Part A + Part B)

| FormDefectName | ProposedParentCode\_L1 | ProposedParentName\_L1 | ProposedDefectCode\_L2 | ProposedDefectName\_L2 | LineTypeCode | DefaultSeverityId | SortOrderHint | Notes | EvidencePath | Confidence | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Fan pattern break | APP | Application Defects | FAN\_BREAK | Fan Pattern Break | LIQUID | 5 | 10 | Checklist item 14: observe fan breaks | 8.2.2.2.7/Option 2 | Medium | PartA |
| Part damage at blow-off | HAND | Handling Defects | PART\_DMG\_BLOWOFF | Part Damage at Blow-Off | LIQUID | 4 | 20 | Downtime category: PARTS HIT IN BLOW OFF | 8.2.2.28/Feb | Medium | PartA |
| Booth environmental feedback | ENV | Environmental Defects | BOOTH\_FEEDBACK | Booth Environmental Feedback | LIQUID | 6 | 30 | Downtime category: BOOTH FEEDBACK | 8.2.2.28/Feb | Medium | PartA |
| Colour out of tolerance | COLOUR | Colour Defects | COLOUR\_OOT | Colour Out of Tolerance | LIQUID | 7 | 40 | DEcmc > 2 or DL/Da/Db > 1.15 metallics | 8.2.2.26/Sheet1 | High | PartA |
| Viscosity out of tolerance | MIX | Paint Mix Defects | VISC\_OOT | Viscosity Out of Tolerance | LIQUID | 5 | 50 | Inferred from viscosity capture fields | 8.2.2.1.18/Paint Tally | Low | PartA |
| Catalyst issue | MIX | Paint Mix Defects | CATALYST\_ISSUE | Catalyst Check Failure | LIQUID | 7 | 60 | Catalyst Check column on production tracking | 8.2.2.2.1/Line Paint Production Tracking | Medium | PartA |
| Rack visual check failure | HAND | Handling Defects | RACK\_VISUAL\_FAIL | Rack Condition Failure | LIQUID | 3 | 70 | Rack Visual Check column | 8.2.2.2.1/Line Paint Production Tracking | Medium | PartA |
| Equipment issue - primer | EQUIP | Equipment Defects | EQUIP\_PRIME | Equipment Issue - Primer Stage | LIQUID | 6 | 80 | Downtime category: EQUIPMENT ISSUES PRIME | 8.2.2.28/Feb | Medium | PartA |
| Equipment issue - base | EQUIP | Equipment Defects | EQUIP\_BASE | Equipment Issue - Base Stage | LIQUID | 6 | 90 | Downtime category: EQUIPMENT ISSUES BASE | 8.2.2.28/Feb | Medium | PartA |
| Equipment issue - clear | EQUIP | Equipment Defects | EQUIP\_CLEAR | Equipment Issue - Clear Stage | LIQUID | 6 | 100 | Downtime category: EQUIPMENT ISSUES CLEAR | 8.2.2.28/Feb | Medium | PartA |
| DIRT | APP | Application Defects | DIRT | Dirt / Contamination | LIQUID | 4 | 110 | Universal — 11 of 11 customer form families. Buff and repaint contexts. | 8.2.2.3.*/all inspection forms | High | PartB |
| SAG / RUN | APP | Application Defects | SAG\_RUN | Sag / Run | LIQUID | 6 | 120 | Universal — 11 of 11 customer form families. | 8.2.2.3.*/all inspection forms | High | PartB |
| ORANGE PEEL | APP | Application Defects | ORANGE\_PEEL | Orange Peel | LIQUID | 5 | 130 | 7 of 11 form families. Buff and repaint contexts. | 8.2.2.3.4.1/8.2.2.3.6.1/8.2.2.3.7.2/etc | High | PartB |
| THIN PAINT | APP | Application Defects | THIN\_PAINT | Thin Paint / Insufficient Coverage | LIQUID | 6 | 140 | 9 of 11 form families. Gate alarms 5-20. | 8.2.2.3.*/most inspection forms | High | PartB |
| THIN CLEAR | APP | Application Defects | THIN\_CLEAR | Thin Clear Coat | LIQUID | 6 | 150 | 8 of 11 form families. Gate alarms 5-20. | 8.2.2.3.*/most inspection forms | High | PartB |
| FIBER | APP | Application Defects | FIBER | Fiber / Foreign Material in Film | LIQUID | 4 | 160 | 6 of 11 form families. Buff context only. | 8.2.2.3.4.1/8.2.2.3.5.1/8.2.2.3.6.1/8.2.2.3.7.2 | High | PartB |
| MOTTLING | APP | Application Defects | MOTTLING | Mottling / Metallic Orientation | LIQUID | 5 | 170 | 2 of 11 form families (Mytox + Misc). Metallic-specific. | 8.2.2.3.3.2/8.2.2.2.16 | High | PartB |
| POPPING / OUTGASSING | APP | Application Defects | POPPING | Popping / Outgassing | LIQUID | 6 | 180 | 3 form families (Rollstamp=POPPING; Tesla=OUTGASSING; KB=Outgassing Popping). Normalized. | 8.2.2.3.2.1/8.2.2.3.7.2/8.2.2.3.6.1 | High | PartB |
| BLISTERS / PITMARK | APP | Application Defects | BLISTERS | Blisters / Pit Marks | LIQUID | 6 | 190 | Rollstamp=BLISTERS (alarm 18); Tesla=BLISTERS/PITMARK. Normalized. | 8.2.2.3.2.1/8.2.2.3.7.2 | High | PartB |
| STRINGS | APP | Application Defects | STRINGS | Strings / Cobwebbing | LIQUID | 4 | 200 | Rollstamp only. Gate alarm 20. Liquid spray artifact. | 8.2.2.3.2.1/BMW | High | PartB |
| BAD MASKING | APP | Application Defects | BAD\_MASKING | Bad Masking / Masking Failure | LIQUID | 5 | 210 | Rollstamp only. Gate alarm 20. Process error not coating defect. | 8.2.2.3.2.1/BMW | High | PartB |
| PAINT SPITS | APP | Application Defects | PAINT\_SPITS | Paint Spits / Spatter | LIQUID | 4 | 220 | Mytox only. Gate alarm 10. Gun atomization issue. | 8.2.2.3.3.2/102 Line Inspection | High | PartB |
| OVERSPRAY | APP | Application Defects | OVERSPRAY | Overspray | LIQUID | 5 | 230 | Metelix Hummer + Y2XX only. RW/ prefix. | 8.2.2.3.5.4/8.2.2.3.5.6/Spoilers | High | PartB |
| MISSING PAINT | APP | Application Defects | MISSING\_PAINT | Missing Paint / Uncovered Area | LIQUID | 7 | 240 | Metelix Hummer + Y2XX only. RW/ prefix. | 8.2.2.3.5.4/8.2.2.3.5.6/Spoilers | High | PartB |
| FISH EYE | APP | Application Defects | FISH\_EYE | Fish Eye / Cratering | LIQUID | 6 | 250 | Metelix Hummer + Y2XX only. Contamination-induced. | 8.2.2.3.5.4/8.2.2.3.5.6/Spoilers | High | PartB |
| SOLVENT POP | APP | Application Defects | SOLVENT\_POP | Solvent Pop | LIQUID | 6 | 260 | Tesla GP12 only. Buff and repaint contexts. | 8.2.2.3.7.3/Spyder | High | PartB |
| E-COAT (substrate) | SUB | Substrate / Supplier Defects | ECOAT\_SUB | E-Coat Substrate Defect | LIQUID | 5 | 270 | Mytox only. Incoming e-coat quality — supplier defect. Gate alarm 30. | 8.2.2.3.3.2/102 Line Inspection | High | PartB |
| DELAMINATION | SUB | Substrate / Supplier Defects | DELAM | Delamination | LIQUID | 8 | 280 | Rollstamp only. Gate alarm 10. Extrusion defect category. | 8.2.2.3.2.1/BMW | High | PartB |
| ZIPPER LINE | SUB | Substrate / Supplier Defects | ZIPPER\_LINE | Zipper Line | LIQUID | 5 | 290 | Rollstamp only. Gate alarm 10. Extrusion defect. | 8.2.2.3.2.1/BMW | High | PartB |
| EXTRUSION LINE | SUB | Substrate / Supplier Defects | EXTRUSION\_LINE | Extrusion Line | LIQUID | 5 | 300 | Rollstamp + Tesla. Substrate/extrusion artifact. | 8.2.2.3.2.1/8.2.2.3.7.2 | High | PartB |
| SPLAY | SUB | Substrate / Supplier Defects | SPLAY | Splay / Silver Streaks | LIQUID | 6 | 310 | Tesla (std + GP12 + buff). Molding defect. Gate alarm 11. | 8.2.2.3.7.2/8.2.2.3.7.3/8.2.2.3.7.1 | High | PartB |
| GAS MARK | SUB | Substrate / Supplier Defects | GAS\_MARK | Gas Mark | LIQUID | 5 | 320 | Tesla std only. Molding defect. | 8.2.2.3.7.2/Spyder | High | PartB |
| CHATTER MARK | SUB | Substrate / Supplier Defects | CHATTER\_MARK | Chatter Mark | LIQUID | 5 | 330 | Tesla std only. Gate alarm 11. Molding/machining defect. | 8.2.2.3.7.2/Spyder | High | PartB |
| FLASH (molding) | SUB | Substrate / Supplier Defects | FLASH\_MOLD | Flash / Parting Line Flash | LIQUID | 3 | 340 | 5 form families. Molding defect — excess material at mold parting line. | 8.2.2.3.4.1/8.2.2.3.7.*/8.2.2.2.16 | High | PartB |
| DENT | SUB | Substrate / Supplier Defects | DENT | Dent / Impact Damage | LIQUID | 5 | 350 | 4 form families (Mytox + Metelix gen/Hummer/Y2XX). Handling or substrate. | 8.2.2.3.3.2/8.2.2.3.5.*/Spoilers | High | PartB |
| PARTING LINE | SAND | Sanding / Pre-Paint Defects | PARTING\_LINE | Parting Line (sanding) | LIQUID | 3 | 360 | Metelix gen + Hummer + Y2XX + Moulding-Sanding. Pre-paint substrate defect. | 8.2.2.3.5.1/8.2.2.3.5.3/8.2.2.3.5.4/8.2.2.3.5.6 | High | PartB |
| GOUGES | SAND | Sanding / Pre-Paint Defects | GOUGES | Gouges | LIQUID | 5 | 370 | Metelix gen + Hummer + Y2XX + Moulding-Sanding. | 8.2.2.3.5.1/8.2.2.3.5.3/8.2.2.3.5.4/8.2.2.3.5.6 | High | PartB |
| SANDING MARKS | SAND | Sanding / Pre-Paint Defects | SANDING\_MARKS | Sanding Marks / Scratch Pattern | LIQUID | 4 | 380 | Metelix gen + Hummer + Y2XX + Moulding-Sanding. | 8.2.2.3.5.1/8.2.2.3.5.3/8.2.2.3.5.4/8.2.2.3.5.6 | High | PartB |
| SINK MARKS | SUB | Substrate / Supplier Defects | SINK\_MARKS | Sink Marks | LIQUID | 4 | 390 | Metelix Hummer + Y2XX + Moulding-Sanding. Molding defect. | 8.2.2.3.5.3/8.2.2.3.5.4/8.2.2.3.5.6 | High | PartB |
| CRACKS | SUB | Substrate / Supplier Defects | CRACKS | Cracks / Fractures | LIQUID | 7 | 400 | Metelix gen + Hummer + Y2XX + Moulding-Sanding. Structural substrate defect. | 8.2.2.3.5.1/8.2.2.3.5.3/8.2.2.3.5.4/8.2.2.3.5.6 | High | PartB |
| THIN SUBSTRATE | SUB | Substrate / Supplier Defects | THIN\_SUB | Thin Substrate / Wall Thickness | LIQUID | 6 | 410 | Metelix Moulding-Sanding only. Raw material defect. | 8.2.2.3.5.3/Spoilers | High | PartB |
| SNOWBALLS | BUFF | Buffing Defects | SNOWBALLS | Snowballs / Compound Residue | LIQUID | 3 | 420 | Tesla buff + Metelix buff. Buffing compound buildup. | 8.2.2.3.7.1/8.2.2.3.5.2 | High | PartB |
| FOAM MARKS | BUFF | Buffing Defects | FOAM\_MARKS | Foam Marks / Pad Marks | LIQUID | 3 | 430 | Tesla buff + GP12. Buffing pad artifact. | 8.2.2.3.7.1/8.2.2.3.7.3 | High | PartB |
| HAZE | BUFF | Buffing Defects | HAZE | Haze / Swirl Marks | LIQUID | 4 | 440 | Metelix buff only. Over-buffing or compound residue. | 8.2.2.3.5.2/Spoilers | High | PartB |
| BURN THROUGH | BUFF | Buffing Defects | BURN\_THROUGH | Burn Through | LIQUID | 8 | 450 | Metelix buff only. Buffing through clear/base coat. Severe — requires recoat. | 8.2.2.3.5.2/Spoilers | High | PartB |
| SCRATCH (buff) | BUFF | Buffing Defects | SCRATCH\_BUFF | Scratch (Buffing-Induced) | LIQUID | 4 | 460 | Tesla buff + GP12 + Metelix buff. Scratch during buff process. | 8.2.2.3.7.1/8.2.2.3.7.3/8.2.2.3.5.2 | High | PartB |

---

### Taxonomy Summary

| L1 Parent Code | L1 Name | Leaf Count | Notes |
|---|---|---|---|
| APP | Application Defects | 17 | Core paint process defects |
| SUB | Substrate / Supplier Defects | 12 | Incoming material / molding / extrusion |
| SAND | Sanding / Pre-Paint Defects | 3 | Pre-paint surface prep |
| BUFF | Buffing Defects | 5 | Post-paint rework artifacts |
| MIX | Paint Mix Defects | 2 | Paint preparation (Part A only) |
| EQUIP | Equipment Defects | 3 | Equipment failure modes (Part A only) |
| HAND | Handling Defects | 2 | Physical damage during handling (Part A only) |
| COLOUR | Colour Defects | 1 | Colourimetry out-of-tolerance (Part A only) |
| ENV | Environmental Defects | 1 | Booth conditions (Part A only) |
| **TOTAL** | | **46** | **10 Part A + 36 Part B (some overlap acknowledged)** |

---

### Confirmed Gaps — Defects NOT Found on Any Form (LIQUID Line Type)

These 5 should be added to the taxonomy as recommended entries with **Confidence: INFERRED** when seeding the database:

| Defect Code | Description |
|---|---|
| DRY\_SPRAY | Insufficient atomization / low film at edges |
| COLOUR\_MISMATCH | Visual colour deviation — distinct from ΔE measurement |
| GLOSS\_FAILURE | Gloss out of spec — low or high |
| ADHESION\_FAILURE | Tape test failure |
| SOLVENT\_ENTRAPMENT | Related to but distinct from solvent pop |

---

## Appendix B: Form-to-Entity Field Mapping (All Part B Forms)

### 8.2.2.3.2.1 — BMW (Rollstamp)

| FormFieldName | SheetName | TargetSchema | TargetTable | TargetColumn | MappingType | Confidence | Notes |
|---|---|---|---|---|---|---|---|
| PAINT DATE | BMW | quality | InspectionRecord | PaintDate | DIRECT | High | Header field |
| SHIFT | BMW | quality | InspectionRecord | ShiftId | FK\_LOOKUP | High | Lookup to dbo.Shift |
| PAINTED PART # | BMW | quality | InspectionRecord | PartId | FK\_LOOKUP | High | Lookup to dbo.Part |
| EXTRUSION DATE & RACK # | BMW | quality | InspectionRecord | CarrierNumber | SPLIT\_FIELD | Medium | Composite field — needs parsing |
| ASSEMBLY DATE | BMW | NO CURRENT TABLE | | | | Low | No entity captures assembly date — INFERRED new field on InspectionRecord or Part |
| GOOD | BMW | quality | InspectionRecord | TotalGood | DIRECT | High | Summary column |
| DIRT (count) | BMW | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=DIRT; DispositionCodeId=REWORK |
| POPPING (count) | BMW | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=POPPING; DispositionCodeId=REWORK |
| ORANGE PEEL END CAP (count) | BMW | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=ORANGE\_PEEL; DispositionCodeId=REWORK; location-specific variant |
| ORANGE PEEL FACE (count) | BMW | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=ORANGE\_PEEL; DispositionCodeId=REWORK; location-specific variant |
| THIN PAINT (count) | BMW | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=THIN\_PAINT; DispositionCodeId=RECOAT |
| SAG / RUN (count) | BMW | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=SAG\_RUN; DispositionCodeId=RECOAT |
| BAD MASKING (count) | BMW | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=BAD\_MASKING; DispositionCodeId=RECOAT |
| STRINGS (count) | BMW | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=STRINGS; DispositionCodeId=RECOAT |
| BLISTERS (count) | BMW | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=BLISTERS; DispositionCodeId=RECOAT |
| DELAM. (count) | BMW | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=DELAM; DispositionCodeId=RTS |
| ZIPPER LINE (count) | BMW | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=ZIPPER\_LINE; DispositionCodeId=RTS |
| EXT. LINE (count) | BMW | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=EXTRUSION\_LINE; DispositionCodeId=RTS |
| TOTAL SCRAP -9008 | BMW | quality | InspectionRecord | TotalScrap | DIRECT | High | Scrap count by part number suffix |
| TOTAL SCRAP -9009 | BMW | quality | InspectionRecord | TotalScrap | DIRECT | High | Scrap count by part number suffix |

### 8.2.2.3.3.2 — Mytox (102 Line Inspection)

| FormFieldName | SheetName | TargetSchema | TargetTable | TargetColumn | MappingType | Confidence | Notes |
|---|---|---|---|---|---|---|---|
| PAINT DATE | 102 Line Inspection | quality | InspectionRecord | PaintDate | DIRECT | High | |
| INSPECTION DATE | 102 Line Inspection | quality | InspectionRecord | InspectionDate | DIRECT | High | Separate from paint date — unique to Mytox |
| SHIFT | 102 Line Inspection | quality | InspectionRecord | ShiftId | FK\_LOOKUP | High | |
| RACK # | 102 Line Inspection | quality | InspectionRecord | RackNumber | DIRECT | High | Carrier/rack traceability |
| COLOR | 102 Line Inspection | NO CURRENT TABLE | | | INFERRED | Medium | Could map to dbo.Part.ColourCode or new field |
| THIN CLEAR (count) | 102 Line Inspection | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=THIN\_CLEAR; DispositionCodeId=RECOAT; GateAlarm=20 |
| MOTTLING (count) | 102 Line Inspection | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=MOTTLING; DispositionCodeId=RECOAT; GateAlarm=20 |
| PAINT SPITS (count) | 102 Line Inspection | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=PAINT\_SPITS; DispositionCodeId=RECOAT; GateAlarm=10 |
| E-COAT (count) | 102 Line Inspection | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=ECOAT\_SUB; DispositionCodeId=RTS; GateAlarm=30 |
| DENT (count) | 102 Line Inspection | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=DENT; DispositionCodeId=RTS; GateAlarm=8 |
| SCRAP (count) | 102 Line Inspection | quality | InspectionRecord | TotalScrap | DIRECT | High | GateAlarm=1 — any scrap triggers notification |

### 8.2.2.3.4.1 — Laval Tool

| FormFieldName | SheetName | TargetSchema | TargetTable | TargetColumn | MappingType | Confidence | Notes |
|---|---|---|---|---|---|---|---|
| PAINT DATE | Laval Tool | quality | InspectionRecord | PaintDate | DIRECT | High | |
| SHIFT | Laval Tool | quality | InspectionRecord | ShiftId | FK\_LOOKUP | High | |
| Raw Incoming Part Number | Laval Tool | quality | InspectionRecord | INFERRED:RawPartNumber | INFERRED | Medium | Raw part # — no current column. FK to dbo.Part or new field. |
| PAINTED PART # | Laval Tool | quality | InspectionRecord | PartId | FK\_LOOKUP | High | Finished goods part number |
| COLOR | Laval Tool | NO CURRENT TABLE | | | INFERRED | Medium | Part attribute |
| FLASH (count) | Laval Tool | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=FLASH\_MOLD; DispositionCodeId=RTS; GateAlarm=1 |

### 8.2.2.3.5.4 — Metelix Hummer / Y2XX (Spoilers)

| FormFieldName | SheetName | TargetSchema | TargetTable | TargetColumn | MappingType | Confidence | Notes |
|---|---|---|---|---|---|---|---|
| Carrier Number | Spoilers | quality | InspectionRecord | CarrierNumber | DIRECT | High | Per-carrier tracking — critical for traceability |
| BUFF/DIRT (count) | Spoilers | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=DIRT; DispositionCodeId=REWORK; BUFF/ prefix = buff disposition |
| RW/THIN CLEAR (count) | Spoilers | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=THIN\_CLEAR; DispositionCodeId=RECOAT; RW/ prefix = recoat disposition |
| RW/FISH EYE (count) | Spoilers | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=FISH\_EYE; DispositionCodeId=RECOAT |
| RW/OVERSPRAY (count) | Spoilers | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=OVERSPRAY; DispositionCodeId=RECOAT |
| RW/MISSING PAINT (count) | Spoilers | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=MISSING\_PAINT; DispositionCodeId=RECOAT |
| Parting Line (count) | Spoilers | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=PARTING\_LINE; DispositionCodeId=RTS |
| Sink Marks (count) | Spoilers | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=SINK\_MARKS; DispositionCodeId=RTS |
| Cracks (count) | Spoilers | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=CRACKS; DispositionCodeId=RTS |

### 8.2.2.3.5.5 — Application Tracker

| FormFieldName | SheetName | TargetSchema | TargetTable | TargetColumn | MappingType | Confidence | Notes |
|---|---|---|---|---|---|---|---|
| Name | Sheet1 | quality | InspectionRecord | InspectorId | FK\_LOOKUP | Medium | Operator/inspector name — lookup to dbo.Employee |
| Temp At Start | Sheet1 | NO CURRENT TABLE | | | INFERRED | Medium | Environmental data — maps to proposed production.ProductionRun or new InspectionEnvironment child |
| Humidity At Start | Sheet1 | NO CURRENT TABLE | | | INFERRED | Medium | Environmental data |
| Booth Temp At Start | Sheet1 | NO CURRENT TABLE | | | INFERRED | Medium | Environmental data |
| Carrier # (row) | Sheet1 | quality | InspectionRecord | CarrierNumber | DIRECT | High | Per-carrier row — one InspectionRecord per carrier |
| RW Y/N | Sheet1 | quality | InspectionRecord | INFERRED:IsRework | INFERRED | Medium | Boolean — is this carrier a rework? No current field. |
| Roller Initial (Primer) | Sheet1 | NO CURRENT TABLE | | | INFERRED | Medium | Process data — maps to production.ProductionRunCarrier |
| Fluid/Atom/Fan/ml per 15sec (Primer) | Sheet1 | NO CURRENT TABLE | | | INFERRED | Medium | Spray parameters — maps to production.ProductionRunCarrier |
| Fluid/Atom/Fan/ml per 15sec (Base) | Sheet1 | NO CURRENT TABLE | | | INFERRED | Medium | Spray parameters |
| Fluid/Atom/Fan/ml per 15sec (Clear) | Sheet1 | NO CURRENT TABLE | | | INFERRED | Medium | Spray parameters |

### 8.2.2.3.5.3 — Metelix Moulding-Sanding (Spoilers)

| FormFieldName | SheetName | TargetSchema | TargetTable | TargetColumn | MappingType | Confidence | Notes |
|---|---|---|---|---|---|---|---|
| Part # | Spoilers | quality | InspectionRecord | PartId | FK\_LOOKUP | High | Hummer / Y2XX Wing designators |
| raw / primed / painted | Spoilers | quality | InspectionRecord | INFERRED:PartLifecycleState | INFERRED | Medium | Tri-state: when in lifecycle was defect found. No current field. |
| Inspector | Spoilers | quality | InspectionRecord | InspectorId | FK\_LOOKUP | Medium | Inspector name |
| Sander Inspection ID | Spoilers | quality | InspectionRecord | INFERRED:SanderInspectionId | INFERRED | Low | Secondary inspector for sanding — no current field |
| Sink Marks (count) | Spoilers | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=SINK\_MARKS; Pre-paint context |
| Thin Substrate (count) | Spoilers | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=THIN\_SUB; Pre-paint context |

### 8.2.2.3.6.1 — KB Components

| FormFieldName | SheetName | TargetSchema | TargetTable | TargetColumn | MappingType | Confidence | Notes |
|---|---|---|---|---|---|---|---|
| PAINT DATE | Laval Tool | quality | InspectionRecord | PaintDate | DIRECT | High | Tab misnamed — this is KB Components |
| MOLDING DATE | Laval Tool | quality | InspectionRecord | MoldingDate | DIRECT | High | Unique to KB + Tesla |
| Outgassing Popping (count) | Laval Tool | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=POPPING; DispositionCodeId=RTS; KB-specific molding defect label |

### 8.2.2.3.7.2 — Tesla Standard (Spyder)

| FormFieldName | SheetName | TargetSchema | TargetTable | TargetColumn | MappingType | Confidence | Notes |
|---|---|---|---|---|---|---|---|
| PAINT DATE | Spyder | quality | InspectionRecord | PaintDate | DIRECT | High | |
| MOLDING DATE | Spyder | quality | InspectionRecord | MoldingDate | DIRECT | High | |
| SPLAY (count) | Spyder | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=SPLAY; DispositionCodeId=RTS; GateAlarm=11 |
| GAS MARK (count) | Spyder | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=GAS\_MARK; DispositionCodeId=RTS |
| CHATTER MARK (count) | Spyder | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=CHATTER\_MARK; DispositionCodeId=RTS; GateAlarm=11 |
| BLISTERS/PITMARK (count) | Spyder | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=BLISTERS; DispositionCodeId=RTS |
| OTHER (DESCRIBE) | Spyder | quality | InspectionDefectCount | INFERRED:FreeTextNote | INFERRED | Low | Free text — destructive to taxonomy. Recommend: pick nearest DefectType + note field. |

### 8.2.2.3.7.3 — Tesla GP12 (Spyder)

| FormFieldName | SheetName | TargetSchema | TargetTable | TargetColumn | MappingType | Confidence | Notes |
|---|---|---|---|---|---|---|---|
| SOLVENT POP (buff count) | Spyder | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=SOLVENT\_POP; DispositionCodeId=REWORK; GP12 context |
| SOLVENT POP (repaint count) | Spyder | quality | InspectionDefectCount | Quantity | DIRECT | High | DefectTypeId=SOLVENT\_POP; DispositionCodeId=RECOAT; GP12 context |

### 8.2.2.4.1 — Receiving Log

| FormFieldName | SheetName | TargetSchema | TargetTable | TargetColumn | MappingType | Confidence | Notes |
|---|---|---|---|---|---|---|---|
| Supplier/Customer | Jan-Dec | logistics | ReceivingLogEntry | SupplierOrCustomerId | FK\_LOOKUP | High | |
| PO / Packing Slip# | Jan-Dec | logistics | ReceivingLogEntry | PackingSlipNumber | DIRECT | High | |
| Supplier Promise Date | Jan-Dec | logistics | ReceivingLogEntry | SupplierPromiseDate | DIRECT | High | |
| Date Rec. | Jan-Dec | logistics | ReceivingLogEntry | DateReceived | DIRECT | High | |
| Time | Jan-Dec | logistics | ReceivingLogEntry | TimeReceived | DIRECT | High | |
| Accept A or R | Jan-Dec | logistics | ReceivingLogEntry | AcceptReject | DIRECT | High | |
| Rejected Qty | Jan-Dec | logistics | ReceivingLogEntry | RejectedQuantity | DIRECT | High | |
| Initial | Jan-Dec | logistics | ReceivingLogEntry | ReceiverInitials | DIRECT | High | |
| SUPPLY / QA/ENG checkboxes | Jan-Dec | NO CURRENT TABLE | | | INFERRED | Low | Distribution routing — possibly workflow trigger not data field |
| Released (date) | Jan-Dec | logistics | ReceivingLogEntry | INFERRED:EquipmentReleaseDate | INFERRED | Medium | Equipment release date — unclear purpose |

### 8.2.2.4.2 — Packing Slip

| FormFieldName | SheetName | TargetSchema | TargetTable | TargetColumn | MappingType | Confidence | Notes |
|---|---|---|---|---|---|---|---|
| Part Number | Sheet1 | logistics | PackSlipLineItem | PartId | FK\_LOOKUP | High | Generic pack slip — all customer variants share this |
| ADDITIONAL INFO | Sheet1 | logistics | PackSlipLineItem | INFERRED:AdditionalInfo | DIRECT | Medium | PO# / Job# / Work Order |
| # of Skids | Sheet1 | logistics | PackSlipLineItem | ContainerCount | DIRECT | High | |
| Total Parts Shipped | Sheet1 | logistics | PackSlipLineItem | Quantity | DIRECT | High | |
| Date | Sheet1 | logistics | PackSlip | ShipDate | DIRECT | High | |
| Ship Via | Sheet1 | logistics | PackSlip | ShipVia | DIRECT | High | |
| Driver Print | Sheet1 | logistics | PackSlip | DriverName | DIRECT | High | |
| Truck/Trailer# | Sheet1 | logistics | PackSlip | TruckTrailerNumber | DIRECT | High | |
| Shipper Init | Sheet1 | logistics | PackSlip | ShipperInitials | DIRECT | High | |

### 8.2.2.4.4 — Customer RPPM (Reporting)

| FormFieldName | SheetName | TargetSchema | TargetTable | TargetColumn | MappingType | Confidence | Notes |
|---|---|---|---|---|---|---|---|
| Customer | Sheet1 | NO CURRENT TABLE | | | INFERRED | Medium | Monthly totals — reporting entity not transactional |
| Shipped (monthly) | Sheet1 | NO CURRENT TABLE | | | INFERRED | Medium | Aggregate — computed from PackSlip data |
| Returned (monthly) | Sheet1 | NO CURRENT TABLE | | | INFERRED | Medium | Aggregate — computed from RMA data |
| Customer RPPM | Sheet1 | NO CURRENT TABLE | | | INFERRED | Medium | Computed: Returns/Shipped × 1M — dashboard KPI not stored field |

### 8.2.2.4.5 — Delivery Performance (Reporting)

| FormFieldName | SheetName | TargetSchema | TargetTable | TargetColumn | MappingType | Confidence | Notes |
|---|---|---|---|---|---|---|---|
| Customer | Monthly | NO CURRENT TABLE | | | INFERRED | Medium | Delivery performance — reporting entity |
| Quantity Due (weekly) | Monthly | NO CURRENT TABLE | | | INFERRED | Medium | Customer release demand — ERP domain |
| Quantity Shipped (weekly) | Monthly | NO CURRENT TABLE | | | INFERRED | Medium | Computed from PackSlip aggregation |
| Delivery % | Monthly | NO CURRENT TABLE | | | INFERRED | Medium | Computed: Shipped/Due × 100 — dashboard KPI |

### 8.2.2.4.20 — Return Material Authorization (RMA)

| FormFieldName | SheetName | TargetSchema | TargetTable | TargetColumn | MappingType | Confidence | Notes |
|---|---|---|---|---|---|---|---|
| RMA Number | RMA | logistics | ReturnMaterialAuthorization | RmaNumber | DIRECT | High | e.g. ME228 ME238 ME255 |
| RMA Date | RMA | logistics | ReturnMaterialAuthorization | RmaDate | DIRECT | High | |
| Part# (FG) | RMA | logistics | RmaLineItem | PartId | FK\_LOOKUP | High | VG0240BL0PA etc. |
| Part State | RMA | logistics | RmaLineItem | PartState | DIRECT | High | Sanded RAW / Unsanded RAW / Painted |
| Quantity | RMA | logistics | RmaLineItem | Quantity | DIRECT | High | Per RMA per part per state |

---

## Mapping Summary

| Metric | Count | Percentage |
|---|---|---|
| Total field mappings | 96 | |
| DIRECT mappings | 62 | 65% |
| FK\_LOOKUP mappings | 16 | 17% |
| INFERRED mappings | 16 | 17% |
| NO CURRENT TABLE | 12 | Fields requiring new columns or entities |
| SPLIT\_FIELD | 1 | Rollstamp Extrusion Date & Rack # composite |

---

## Key INFERRED Gaps Requiring Architectural Decisions

1. **InspectionRecord.RawPartNumber** — Raw incoming part # vs finished goods part #. Need dual-part reference or Part entity supports raw→FG mapping.

2. **InspectionRecord.PartLifecycleState** — Metelix Moulding-Sanding tracks whether defect found on raw/primed/painted. Enum field or child table?

3. **InspectionRecord.IsRework** — Application Tracker has RW Y/N per carrier. Boolean on InspectionRecord or link to prior InspectionRecord?

4. **Environmental data (Temp, Humidity, Booth Temp)** — On Application Tracker only. Belongs on ProductionRun or InspectionRecord? Recommend ProductionRun since it's process context.

5. **Spray parameters (Fluid, Atom, Fan, ml/15sec per stage)** — Application Tracker. Definitively ProductionRunCarrier territory, not inspection.

6. **Colour field** — 6 forms capture colour but no current entity column. Recommend dbo.Part.ColourCode or a dbo.PartColour lookup.
