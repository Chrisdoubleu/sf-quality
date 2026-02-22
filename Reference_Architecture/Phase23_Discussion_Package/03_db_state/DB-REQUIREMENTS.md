# Requirements: SF Quality Intelligence Platform

**Defined:** 2026-02-17
**Core Value:** Structured knowledge that actively guides every decision in the quality lifecycle -- transforming workflow enforcement into quality intelligence

## v2.0 Requirements

Requirements for the Quality Intelligence Platform milestone. Each maps to roadmap phases.

### Knowledge Schema & Deployment (KNOW)

- [x] **KNOW-01**: 9-table defect knowledge schema deployed to migration chain (migration 125) with audit triggers (@PlantIdColumn=NULL), UNIQUE constraints on (DefectTypeId, LineTypeId, BusinessKeyCode), CHECK constraints on enum columns, filtered indexes, and no RLS enrollment — **COMPLETE 2026-02-18** (92/92 checks passing)
- [x] **KNOW-02**: Liquid paint FINAL seed data synthesized from Claude + ChatGPT drafts (27 codes: SURF-19, COLOR-8) with all 14 column remappings per synthesis spec, INSERT-only MERGE, and V01-V14 verification passing -- **COMPLETE 2026-02-18** (126c: 1740 lines, ~733 rows; deployed to dev; V01-V14 PASS for all 68 codes). **Further addressed by Phase 21.1**: taxonomy quality improved via v3 cleanup -- 112+ leaf codes consolidated to ~82 observable-defect-only codes, cause/test/crutch codes removed, AIAG-VDA severity rebaseline, migration 130 deployed 2026-02-20
- [x] **KNOW-03**: Powder FINAL retrofitted with NODETECT root causes for all 23 codes (IshikawaCategoryCode=MEASUREMENT, CauseLevelCode=ROOT) following e-coat NODETECT pattern — **COMPLETE 2026-02-18** (29 NODETECT rows deployed: 6 e-coat in 126a + 23 powder in 126b; V01 row counts verified)
- [x] **KNOW-04**: Powder FINAL retrofitted with SYSTEMIC root causes where governance failure is a realistic mechanism (IshikawaCategoryCode=METHOD, CauseLevelCode=ROOT) -- assessed per code — **COMPLETE 2026-02-18** (7 SYSTEMIC rows deployed in 126b for: CURE-GELTIME, CURE-UNDER, EQUIP-CALOUT, EQUIP-CONVEYOR, EQUIP-FILTER, THICK-FARADAY, THICK-LOW)
- [x] **KNOW-05**: E-coat verification upgraded from V1-V5 to V01-V13 format matching the unified verification framework — **COMPLETE 2026-02-18** (Verify-Phase19.sql implements V01-V13 unified for both e-coat + powder; V02A/V02B split enforced)
- [x] **KNOW-06**: V12 (line-type leakage) and V13 (scope leakage) verification checks added to all 3 process families -- **COMPLETE 2026-02-18** (Verify-Phase20.sql: V12+V13 PASS for all 68 codes across ECOAT/POWDER/LIQUID)
- [x] **KNOW-07**: E-coat seed data deployed (18 codes: ADHES-6, PRETR-3, CONTAM-4, GEN-5; ~462+ rows incl. 6 NODETECT retrofit) as migration 126a with pre-flight DefectCode/LineType existence validation — **COMPLETE 2026-02-18** (126a: 1131 lines, dimension pre-reqs, 6 MOTHER_NATURE corrections, 6 NODETECT retrofits; V01-V13 passing)
- [x] **KNOW-08**: Powder seed data deployed (23 codes: THICK-5, CURE-10, EQUIP-8; ~645+ rows incl. 23 NODETECT + ~7 SYSTEMIC retrofit) as migration 126b with pre-flight validation and NODETECT/SYSTEMIC retrofit included — **COMPLETE 2026-02-18** (126b: 1960 lines, 23 NODETECT + 7 SYSTEMIC retrofits; V01-V13 passing)
- [x] **KNOW-09**: Cross-process verification passes across all 68 codes -- V01-V14 unified, zero orphan FKs, zero duplicate natural keys, confusion pair bidirectionality complete (BLOCKER), no line-type or scope leakage, string domain validation -- **COMPLETE 2026-02-18** (Verify-Phase20.sql: reusable parameterized framework, all V01-V14 PASS)
- [x] **KNOW-10**: Cross-process knowledge harmonization -- consistent depth, naming convention inventory, universal content language review, knowledge ownership registry, CP- prefix analysis, ConfusionPair exception monitoring -- **COMPLETE 2026-02-18** (20-HARMONIZATION-AUDIT.md: 30-row language sample, 90% CLEAN / 10% REVIEW / 0% FIX, 1 forward-fix candidate identified)
- [x] **KNOW-11**: Content quality audit -- per-code completeness matrix (68 codes x 9 tables), maintenance workflow recommendation -- **COMPLETE 2026-02-18** (20-CONTENT-QUALITY-AUDIT.md). Note: attestation model and QE review process removed per project authority decision (2026-02-21). IsVerified is optional tracking only.
- [x] **KNOW-12**: Universal row ownership model -- code-family-based ownership: 126a owns universals for ADHES/PRETR/CONTAM/GEN, 126b owns universals for THICK/CURE/EQUIP, 126c owns universals for SURF/COLOR. Each migration provides universal rows (LineTypeId=NULL) for its code families plus process-specific overlay rows. MERGE idempotency prevents duplication regardless of execution order — **COMPLETE 2026-02-18 for Phases 18-19** (V10 confirms universal + process-specific split; 126a/126b deployed; Phase 20 extends to SURF/COLOR)
- [ ] **KNOW-13**: Naming convention enforcement -- formal code patterns (RC-, INV-, TM-, DG-, CG-, CP-, PC-, SR- prefixes with -EC-, -PW-, -LQ- process infixes for process-specific rows; no infix for universal) validated via pre-deployment compliance check across all 3 FINALs — *PARTIAL 2026-02-18: prefix patterns validated in V04; naming convention inventory documented in 20-HARMONIZATION-AUDIT.md (Section 1: -EC- for e-coat, no infix for powder (legacy), -LQ- for liquid); CP- dual-use retained (Section 4); -PW- infix is legacy, not retroactively changed. Phase 23 (PLAT-02) should lock convention for future process families. Formal pre-deployment compliance tooling not yet built.*
- [x] **KNOW-14**: Liquid paint containment guidance -- 99 rows in DefectTypeContainmentGuidance for all 27 liquid defect codes (SURF-19, COLOR-8); all universal (LineTypeId=NULL), 3-4 actions per defect ordered by urgency, using 7 ContainmentCodes; deployed via migration 127 Section A with INSERT-only MERGE -- **COMPLETE 2026-02-18** (127 deployed to dev, V14b ContainmentCode domain validated)
- [ ] **KNOW-15**: Incoming substrate sub-reason lookup -- new `dbo.IncomingSubstrateDefectReason` table with 10 seed values (SUB-SPLAY through SUB-SEAL) providing controlled picklist for DMG-SUB sub-categorization; SubstrateType column (MOLDED/FORMED/MACHINED/UNIVERSAL) enables process-agnostic filtering; deployed via migration 127 Section B
- [ ] **KNOW-16**: NCR incoming substrate FK -- nullable `IncomingSubstrateDefectReasonId` column on `quality.NonConformanceReport` with FK to `dbo.IncomingSubstrateDefectReason`; required when DefectTypeId resolves to DMG-SUB (enforced at application layer); temporal table ALTER choreography required; deployed via migration 127 Section C

### Knowledge Retrieval & Integration (INTEL)

- [x] **INTEL-01**: Advisory SP `quality.usp_GetDefectKnowledge` deployed -- accepts @DefectTypeId, @LineTypeId, @Sections, @SeverityRatingId; returns up to 9 result sets with retrieval precedence (process-specific first, universal second); supports @NcrId convenience overload that auto-resolves DefectTypeId + LineTypeId from NCR header -- **COMPLETE 2026-02-19** (migration 128: 925-line SP with Mode A/B, cursor-based @Sections parsing, severity band filter; V01-V13 verified)
- [x] **INTEL-02**: 9 per-table knowledge views deployed (dbo.vw_DefectKnowledge_RootCauses, _InvestigationSteps, _TestMethods, _DispositionGuidance, _ContainmentGuidance, _ConfusionPairs, _ParameterChecks, _StandardReferences, _ControlPoints) joining DefectType + LineType for human-readable output -- **COMPLETE 2026-02-19** (migration 128: unfiltered views per D21-08, ConfusionPairs double DefectType join exception; V01 confirms all 9 return rows)
- [x] **INTEL-03**: `quality.vw_NcrOperationalQueue` enhanced with DefectCode, DefectName, parent category name, and TypicalProcessZoneId -- operators can see defect classification in the triage queue -- **COMPLETE 2026-02-19** (migration 128: 5 new columns via LEFT JOIN per D21-09; V09 column existence confirmed)
- [x] **INTEL-04**: Gate SP knowledge integration documented -- gate-by-gate mapping of which knowledge sections surface at each of the 18 gate transitions (companion advisory pattern, gate SPs NOT modified) -- **COMPLETE 2026-02-18** (21-GATE-KNOWLEDGE-MAPPING.md: all 18 gates mapped with exact @Sections CSV strings, INTEL-05 trigger at GATE-15)
- [x] **INTEL-05**: RootCause pre-population from knowledge library -- when creating dbo.RootCause for a CAPA, IshikawaCategoryId, CauseLevelId, and CauseStatement pre-populated from DefectTypeRootCause hypothesis; HypothesisSource traceability column on dbo.RootCause -- **COMPLETE 2026-02-19** (migration 129: quality.usp_PrePopulateRootCauses resolves code-based FKs, CK_RootCause_HypothesisSource expanded to 7 values; V11-V13 verified)
- [ ] **INTEL-06**: Existing v1.0 KPI view assessment -- evaluate quality.vw_NCRPareto, vw_RootCauseDistribution, vw_EffectivenessResults, vw_CostOfQuality for enhancement or coexistence decision with new analytics views; document relationship and migration path

### Analytics Foundation (ANALYTICS)

- [ ] **ANALYTICS-01**: `analytics` schema created -- separates cross-process analytical views from operational views in quality schema
- [ ] **ANALYTICS-02**: Cross-process Pareto view (`analytics.vw_DefectPareto`) -- defect types by NCR count, scrap cost (from NcrCostEntry), total affected quantity; dimensions: DefectCode, LineType, ProcessFamily, Plant, TimePeriod
- [ ] **ANALYTICS-03**: Root cause Ishikawa distribution view (`analytics.vw_RootCauseDistribution`) -- enhanced from v1.0 with DefectType dimension (via CAPA -> QualityEventLink -> NCR -> DefectTypeId), LineType, CauseLevel, and time period
- [ ] **ANALYTICS-04**: Process zone defect concentration view (`analytics.vw_ProcessZoneConcentration`) -- where in the process line defects concentrate; dimensions: ProcessZoneCode, LineType, DefectCode, Plant, TimePeriod
- [ ] **ANALYTICS-05**: Recurrence tracking view (`analytics.vw_RecurrenceTracking`) -- detect repeat NCRs via QualityEventLink.RecurrenceOf; dimensions: DefectCode, Plant, RecurrenceCount, DaysBetween, CAPA exists/effectiveness status
- [ ] **ANALYTICS-06**: Effectiveness trending view (`analytics.vw_EffectivenessTrending`) -- CAPA pass/fail rates over time with DefectType linkage (via CAPA -> QualityEventLink -> NCR); running pass rate by time period
- [ ] **ANALYTICS-07**: Control point gap analysis view (`analytics.vw_ControlPointGapAnalysis`) -- recommended controls (from DefectTypeControlPoint) alongside count of CAPAs raised per defect type; COVERAGE approach (not text-matching); needs phase-specific research for semantic matching feasibility

### Platform Architecture (PLAT)

- [ ] **PLAT-01**: Six-layer cascade pattern documented as a repeatable model -- Taxonomy -> Classification -> Knowledge -> Decision Support -> Transactions -> Analytics; with layer contracts, retrieval precedence, and universal/process-specific layering rules
- [ ] **PLAT-02**: Process family onboarding template and checklist -- step-by-step for adding a new process family (e.g., ANODIZE): bridge table rows, seed file following 11-section template, V01-V13 verification, no schema changes needed
- [ ] **PLAT-03**: Extension model documentation -- how the cascade pattern extends to equipment reliability, supplier quality, and process control domains (v3.0 targets); taxonomy -> knowledge -> retrieval -> analytics progression
- [ ] **PLAT-04**: Deploy and verify framework -- standardized approach for knowledge schema verification (V01-V13), advisory SP smoke tests, analytics view validation, cross-cutting regression checks
- [ ] **PLAT-05**: Knowledge maintenance model -- how knowledge rows are corrected or updated over time; IsVerified as optional tracking flag (not a gate), update-via-migration workflow for content corrections, forward-fix migration pattern for post-deploy fixes
- [ ] **PLAT-06**: Internal data feedback loop -- how production NCR patterns (actual root causes, actual dispositions, recurrence data) improve knowledge base over time; likelihood ranking updates based on occurrence frequency, gap identification from unmatched root causes, knowledge coverage expansion triggers

### Security (SEC)

- [ ] **SEC-01**: Security grants for all currently deployed v2.0 objects -- GRANT SELECT on knowledge tables/views to dbrole_ncr_ops_read; GRANT EXECUTE on advisory SP to appropriate roles; preserve analytics grant notes for deferred Phase 22 artifacts; RLS exclusion assertion (zero knowledge tables in sys.security_predicates); follows existing 5-role model

### Deployment (DEPLOY)

- [ ] **DEPLOY-01**: v2.0 deploy orchestration -- master Apply-v2.0.ps1 script covering deployed migration surface through 130; cross-cutting verify suite; smoke tests for advisory SP and knowledge views; RLS exclusion check; migration ordering enforcement for deployed v2.0 chain; idempotent re-run safe

## Future Requirements (v3.0+)

Deferred to future milestones. Tracked but not in current roadmap.

### Carried from v1.0/v1.1

- **OPT-01..03**: Index optimization at representative dataset scale
- **OPT-02**: RLS predicate performance validation
- **MIG-01..02**: Migration staging and rollback/validation pack
- **TEST-01..05**: Full lifecycle and cross-entity integration testing
- **BACKFILL-01..02**: Supplier/Equipment FK backfill with production data
- **TEMPLATE-01**: 3 missing LineStageTemplate stage definitions

### Knowledge Domain Extensions

- **EXT-01**: Equipment reliability knowledge domain (EquipmentFailureMode, MaintenanceProcedure, SparePart)
- **EXT-02**: Supplier quality knowledge domain (QualityHistory, IncomingInspectionCriteria, RiskProfile)
- **EXT-03**: Process control knowledge domain (ParameterWindow, SPCRule, CapabilityTarget)
- **EXT-04**: AI/ML root cause prediction from production NCR data (requires 12-24 months of operational data)
- **EXT-05**: Real-time SPC integration / parameter alarm tables
- **EXT-06**: PFMEA-to-LineStageTemplate integration

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Automated disposition enforcement | Knowledge layer is ADVISORY, not ENFORCING. Humans make the final decision. Conflicts with disposition authority matrix. |
| AI/ML-based root cause prediction | No production NCR data exists yet. Structured likelihood rankings suffice. v4+ consideration. |
| Real-time SPC integration | Requires equipment/sensor integration not in current architecture. Deferred to v3. |
| Multi-defect per NCR modeling | Single DefectTypeId per NCR sufficient. Would break advisory SP contract. Revisit v3. |
| Knowledge editing via frontend CRUD | Content deployed via migrations, not user-editable. Bypasses verification framework. |
| Embedded knowledge in gate SPs | Gate SPs focus on mutations + authority + reconciliation. Knowledge retrieval is a companion call. |
| Separate knowledge tables per process family | Would fragment model into 27 tables. Universal/process-specific layering is the architecture. |
| Star schema / data warehouse | No performance justification at current scale (~2,000 knowledge rows, early NCR volume). |
| Temporal versioning on knowledge tables | Reference data changes through migrations (self-documenting). Audit triggers suffice. |
| Knowledge table RLS enrollment | Knowledge is universal reference data with no PlantId. Cross-plant by design. |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| KNOW-01 | Phase 18 | **Complete** |
| KNOW-02 | Phase 20, Phase 21.1 | **Complete** (taxonomy quality further improved via v3 cleanup) |
| KNOW-03 | Phase 19 | **Complete** |
| KNOW-04 | Phase 19 | **Complete** |
| KNOW-05 | Phase 19 | **Complete** |
| KNOW-06 | Phase 19, Phase 20 | **Complete** |
| KNOW-07 | Phase 19 | **Complete** |
| KNOW-08 | Phase 19 | **Complete** |
| KNOW-09 | Phase 20 | **Complete** |
| KNOW-10 | Phase 20 | **Complete** |
| KNOW-11 | Phase 20 | **Complete** |
| KNOW-12 | Phase 19 | **Complete** |
| KNOW-13 | Phase 19, Phase 20 | Partial (prefix patterns validated V04; naming convention inventory documented in 20-HARMONIZATION-AUDIT.md; -PW- infix legacy, -LQ- convention locked; formal enforcement tooling deferred to Phase 23 PLAT-02) |
| KNOW-14 | Phase 20 | **Complete** |
| KNOW-15 | Phase 24 | Pending |
| KNOW-16 | Phase 24 | Pending |
| INTEL-01 | Phase 21 | **Complete** |
| INTEL-02 | Phase 21 | **Complete** |
| INTEL-03 | Phase 21 | **Complete** |
| INTEL-04 | Phase 21 | **Complete** |
| INTEL-05 | Phase 21 | **Complete** |
| INTEL-06 | Phase 22 | Pending |
| ANALYTICS-01 | Phase 22 | Pending |
| ANALYTICS-02 | Phase 22 | Pending |
| ANALYTICS-03 | Phase 22 | Pending |
| ANALYTICS-04 | Phase 22 | Pending |
| ANALYTICS-05 | Phase 22 | Pending |
| ANALYTICS-06 | Phase 22 | Pending |
| ANALYTICS-07 | Phase 22 | Pending |
| PLAT-01 | Phase 23 | Pending |
| PLAT-02 | Phase 23 | Pending |
| PLAT-03 | Phase 23 | Pending |
| PLAT-04 | Phase 23 | Pending |
| PLAT-05 | Phase 23 | Pending |
| PLAT-06 | Phase 23 | Pending |
| SEC-01 | Phase 23 | Pending |
| DEPLOY-01 | Phase 23 | Pending |

**Coverage:**
- v2.0 requirements: 37 total
- Mapped to phases: 37
- Unmapped: 0

**Notes:**
- KNOW-06 (V12/V13 verification) spans Phases 19 and 20 -- e-coat/powder V12/V13 added in Phase 19, liquid V12/V13 added in Phase 20. Satisfied: all 3 process families have V12/V13 passing in Verify-Phase20.sql.
- KNOW-13 (naming convention enforcement) spans Phases 19 and 20 -- V04 validates prefix patterns, 20-HARMONIZATION-AUDIT.md documents naming conventions across all 3 process families. Still partial: formal pre-deployment compliance tooling deferred to Phase 23 (PLAT-02).
- KNOW-15/16 (incoming substrate) are in new Phase 24. The sub-reason picklist pattern (controlled vocabulary for a broad defect code) is documented as an extensibility path -- if other defect codes need sub-reasons in the future, Phase 24's architecture serves as the template.

---
*Requirements defined: 2026-02-17*
*Last updated: 2026-02-22 — Phase 23 preflight prep complete. SEC-01 remapped to Phase 23 inline closure due Phase 22 deferral. DEPLOY-01 wording aligned to deployed migration surface through 130. KNOW-13 still partial pending Phase 23 closure.*
