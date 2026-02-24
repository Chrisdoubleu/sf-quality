# Cross-Plant QSA Audit Consolidation Tracker

**Purpose:** Track and synthesize QSA audit findings across all 7 Select Finishing plants into actionable engineering requirements for sf-quality-db, sf-quality-api, and sf-quality-app.

**Last Updated:** 2026-02-24 (Plant 1 + Plant 2 FULLY SYNTHESIZED)

---

## Plant Audit Status

| Plant | Coating Lines | Audit Status | Claude Report | ChatGPT Report | Codebase Assessment | Synthesized |
|-------|--------------|-------------|---------------|----------------|---------------------|-------------|
| Plant 1 | Powder + E-Coat | **COMPLETE** | [Full Report](../Plant%201/Claude/Plant1_QSA_Audit_Report_Claude.md) (133 files, 5 phases) | [Partial](../Plant%201/ChatGPT/Plant1_ChatGPT_Partial_Assessment.md) + 4 CSVs | [Codebase Assessment](../Plant%201/Claude/Plant1_Codebase_Assessment.md) | **DONE** — See [PLANT1_SYNTHESIS.md](PLANT1_SYNTHESIS.md) |
| Plant 2 | Liquid Spray Paint (Lines 101, 102, 103) | **COMPLETE** | [Part A](../Plant%202/Claude/Part%20A/) (5 batches, 53 operational forms) + [Part B](../Plant%202/Claude/Part%20B/) (6 batches, 31 customer/shipping forms) | [3 Batches](../Plant%202/ChatGPT/) (84 forms + 7 obsolete exemplars, 4 appendices) | Not yet run | **DONE** — See [PLANT2_SYNTHESIS.md](PLANT2_SYNTHESIS.md) |
| Plant 3 | TBD | NOT STARTED | — | — | — | — |
| Plant 4 | TBD | NOT STARTED | — | — | — | — |
| Plant 5 | TBD | NOT STARTED | — | — | — | — |
| Plant 6 | TBD | NOT STARTED | — | — | — | — |
| Plant 7 | TBD | NOT STARTED | — | — | — | — |

---

## Consolidation Workflow

For each plant:
1. Run QSA audit prompt with forms package → get reports from Claude + ChatGPT
2. Run codebase-informed assessment (cross-reference findings against live DB schema)
3. Reconcile AI reports + codebase assessment into per-plant synthesis
4. After all plants audited → cross-plant normalization pass

After all plants:
5. Merge defect taxonomies → master DefectType seed data
6. Merge entity proposals → finalized DDL for new schemas
7. Merge gap analyses → prioritized requirements backlog
8. Merge UI screen inventories → app phase planning input

---

## Key Consolidation Artifacts

| Artifact | Path | Status | Purpose |
|----------|------|--------|---------|
| **Defect Taxonomy Master** | [defect_taxonomy/DEFECT_TAXONOMY_MASTER.csv](defect_taxonomy/DEFECT_TAXONOMY_MASTER.csv) | **COMPLETE (Plant 1 + Plant 2)** — 200+ rows, dual-plant reconciled | Merged L1/L2 defect types: form strings → audit proposals → live DB leaves |
| **Entity Proposal Tracker** | [entity_proposals/ENTITY_PROPOSALS.md](entity_proposals/ENTITY_PROPOSALS.md) | **COMPLETE (Plant 1 + Plant 2)** — 15 Plant 1 + 12 Plant 2 entities assessed | New entity definitions with cross-repo + QFM alignment |
| **Gap Tracker** | [gap_tracker/GAP_TRACKER.md](gap_tracker/GAP_TRACKER.md) | **COMPLETE (Plant 1 + Plant 2)** — 28 gaps with cross-plant frequency | All gaps with severity, cross-repo closure status, Plant 1+2 frequency |
| **Plant 1 Synthesis** | [PLANT1_SYNTHESIS.md](PLANT1_SYNTHESIS.md) | **COMPLETE** | Final consolidated Plant 1 output |
| **Plant 2 Synthesis** | [PLANT2_SYNTHESIS.md](PLANT2_SYNTHESIS.md) | **COMPLETE** | Final consolidated Plant 2 output |
| Cross-Plant Comparison | `CROSS_PLANT_COMPARISON.md` | NOT STARTED | Plant-by-plant pattern comparison (created after Plant 3+) |
| Requirements Output | `REQUIREMENTS_OUTPUT.md` | NOT STARTED | Final synthesized requirements for db/api/app repos |

---

## Scoring Summary (Updated Per Plant)

| Dimension | Plant 1 (Claude) | Plant 1 (ChatGPT) | Plant 1 (Consensus) | Plant 2 (Claude) | Plant 2 (ChatGPT) | Plant 2 (Consensus) | Plant 3 | Plant 4 | Plant 5 | Plant 6 | Plant 7 | Avg (1-2) |
|-----------|-----------------|-------------------|---------------------|-----------------|-------------------|---------------------|---------|---------|---------|---------|---------|-----------|
| NCR/Disposition | 15 | ~15 | **15** | 10 | ~12 | **10** | — | — | — | — | — | **13** |
| Defect Tracking | 35 | ~30 | **33** | 30 | ~28 | **28** | — | — | — | — | — | **31** |
| Inspection & Testing | 45 | ~40 | **43** | 30 | ~32 | **30** | — | — | — | — | — | **37** |
| Production Tracking | 40 | ~35 | **38** | 25 | ~28 | **25** | — | — | — | — | — | **32** |
| Process Control | 30 | ~45 | **38** | 35 | ~38 | **35** | — | — | — | — | — | **37** |
| Lab/Chemistry | 50 | ~45 | **48** | 40 | ~38 | **38** | — | — | — | — | — | **43** |
| Traceability | 20 | ~15 | **18** | 15 | ~18 | **15** | — | — | — | — | — | **17** |
| Document Control | 10 | ~15 | **13** | 15 | ~18 | **15** | — | — | — | — | — | **14** |
| **Overall** | **30** | **~30** | **30** | **25** | **~27** | **25** | — | — | — | — | — | **28** |

**Consensus methodology:** Weighted average (Claude 60%, ChatGPT 40%) adjusted for evidence quality. Plant 2: Claude scored Process Control higher (deeper form analysis); ChatGPT scored Traceability/Document Control higher (quantified obsolete ratios and revision evidence).

**Key cross-plant observations:**
- Plant 2 scores LOWER than Plant 1 overall (25 vs 30) due to worse traceability (15 vs 18), worse production tracking (25 vs 38), and worse NCR/disposition (10 vs 15)
- Plant 2 scores HIGHER on document control (15 vs 13) due to 7 forms with Rev Log tabs and more structured obsolete management
- Both plants converge near zero on traceability (15-18) and NCR (10-15) — these are the most critical company-wide gaps

---

## Cross-Repo Platform State (as of 2026-02-24)

| Repo | Version | Phase | Key Status |
|------|---------|-------|------------|
| **sf-quality-db** | v1.0.0 | Phase 34 (153 migrations) | 9 schemas, 150+ tables. NCR production-ready. QFM designed (migrations 131-160) but NO-GO. No production/inspection operational tables yet. |
| **sf-quality-api** | v0.3.0 | Phase 3 complete | 19 NCR endpoints fully implemented. SCAR/Audit/8D placeholders. CAPA in progress. No Inspection/Production/Lab endpoints. |
| **sf-quality-app** | 0% | Phase 1 not started | Tech stack locked (Next.js 15, React 19, shadcn/ui, TanStack Query). Planning complete. No code scaffolded. |
| **Reference Architecture** | v3.0 planned | 46 patterns mapped | Quality Forms Module adjudicated (NO-GO, 8 blockers). Execution Plan covers DB Phases 25-33, API Phases 3.5-10, App Phases 1-10. |

---

## Next Steps

1. **Plant 2 Codebase Assessment** — Cross-reference Plant 2 findings against live DB schema to validate 7-8% entity coverage estimate
2. **Plant 3 Audit** — Prepare forms package, run QSA prompt for Claude + ChatGPT
3. **QFM Blocker Resolution** — Clear 8 adjudication pre-implementation items to unblock inspection entity migrations
4. **App Phase 1 Kickoff** — Foundation scaffold (independent of plant audits)
5. **Repeat for Plants 3-7** — Each plant adds to gap frequency, defect taxonomy, and entity evidence
6. **Cross-Plant Normalization** — After all plants: produce final REQUIREMENTS_OUTPUT.md
7. **Entity Priority Decision** — With 2 plants confirming all 9 original entities + 12 new entities, decide which can proceed to migration immediately vs waiting for more plant evidence
