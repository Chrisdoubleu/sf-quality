# Forms Research Consolidation

**Purpose:** Consolidate research from 4 independent AI researchers into an authoritative forms architecture specification for the sf-quality system.

**Design doc:** [docs/plans/2026-02-26-forms-research-consolidation-design.md](docs/plans/2026-02-26-forms-research-consolidation-design.md)

---

## Status Tracker

| Stage | Status | Notes |
|---|---|---|
| 00_sources | Complete | All 4 sources delivered and copied. |
| 01_extraction | Complete | All 4 sources extracted (2026-02-26). |
| 02_synthesis | Complete | All 6 artifacts produced (2026-02-26). |
| 03_adjudication | Not started | Requires synthesis + human review |
| 04_deliverables | Not started | Requires adjudication |

## Source Status

| Source | Model | .md | .json | Status |
|---|---|---|---|---|
| ChatGPT | o3 Deep Research | 29KB | 46KB | Complete |
| Parallel | ChatGPT Parallel | 16KB | 534KB | Complete |
| Gemini | Gemini 2.5 Pro | 56KB | 44KB | Complete |
| Claude | Claude | 25KB | 36KB | Complete |

## Reading Order

1. This README (status and navigation)
2. [Design doc](docs/plans/2026-02-26-forms-research-consolidation-design.md) (full process design)
3. [Extraction template](01_extraction/EXTRACTION_TEMPLATE.md) (normalization schema)
4. Stage folders in order: `00_sources/` -> `01_extraction/` -> `02_synthesis/` -> `03_adjudication/` -> `04_deliverables/`

## Process

```
00_sources/     Raw research files (copies from sf-quality-app/docs/Forms Research/)
01_extraction/  Normalized per-source data (common template)
02_synthesis/   Cross-source comparison matrices + divergence log
03_adjudication/ Authoritative decisions (ACCEPT/REJECT/MODIFY)
04_deliverables/ Architecture spec + GSD seeding content + coding conventions
```

Steps 1-4 (sources through synthesis): coding agents.
Step 5 (adjudication): human judgment required.
Step 6 (deliverables): agent-assisted.
Step 7 (apply to child repos): separate sessions per repo.
