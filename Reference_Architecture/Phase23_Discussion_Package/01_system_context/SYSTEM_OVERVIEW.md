# sf-quality System Overview

**Context for external AI:** This document describes the sf-quality system that the discussion partner is advising on. The developer working in this system is Chris Walsh, the Quality Systems developer and architect at Select Finishing.

---

## What Is sf-quality?

sf-quality is a **quality management platform** for Select Finishing, an automotive tier-1 supplier specializing in industrial surface finishing (e-coat, powder coat, liquid paint). The system digitizes the quality workflow that currently lives in spreadsheets and paper forms.

**Real-world purpose:** When a painted part fails a quality check on a production line, an operator creates an NCR (Non-Conformance Report). That NCR triggers investigation (8D methodology), root cause analysis, corrective actions (CAPA), potential supplier escalation (SCAR), and finally closure with verified effectiveness. sf-quality enforces this entire lifecycle with a gate-based workflow that ensures no step can be skipped and no unauthorized person can approve a disposition.

**Extended purpose (v2.0):** The knowledge intelligence layer provides investigators with structured guidance — when a "fisheye" surface defect is detected on a liquid paint line, the system retrieves root causes, investigation steps, and containment guidance specific to liquid paint. This replaces tribal knowledge with structured reference data.

---

## The Three Repos

| Repo | Technology | Current State |
|------|-----------|--------------|
| `sf-quality-db` | T-SQL on Azure SQL Server | **Mature.** 133 migrations, 80+ procs, 36 views, 24+ phases shipped. RLS, workflow state machine, approval chains, audit logging, 1,894-row defect knowledge base all implemented. Phase 23 is the next executable phase. |
| `sf-quality-api` | C# / ASP.NET Core 9, Dapper | **Early.** Phase 3 of 10 complete. 25 NCR endpoints. Thin pass-through to stored procedures. No business logic in C#. |
| `sf-quality-app` | TypeScript / Next.js 15, React 19 | **Planning only.** No source code yet. Tech stack locked: shadcn/ui, TanStack Query/Table, react-hook-form + zod, Tailwind CSS 4. |

---

## The Contract Chain

```
sf-quality-db
  └── publishes: db-contract-manifest.json (v1.0.0, 133 migrations)
        │
        ▼
sf-quality-api
  ├── snapshots: db-contract-manifest.snapshot.json (mirrors DB manifest)
  └── publishes: api-openapi.publish.json (v0.2.0, 25 NCR endpoints)
        │
        ▼
sf-quality-app
  └── snapshots: api-openapi.snapshot.json (v0.2.0, synced to API publish)
```

**Rule:** Changes propagate forward only. DB must publish before API can consume. API must publish before App can consume. This is enforced by planning governance, not automated CI (yet — governance is advisory pre-v1).

---

## Production Environment

| Environment | Server | Database | Status |
|-------------|--------|----------|--------|
| Dev | `sql-sf-quality-0b1f-dev.database.windows.net` | `sqldb-quality-core-dev` | LIVE — v2.0 Phase 21.1 complete, migrations 125-130 deployed |
| Prod | Same server as dev | `sqldb-quality-core-prod` | LIVE — v1.0 schema (pre-v2.0 knowledge layer) |

**Note:** v2.0 knowledge layer (Phases 18-21.1) is deployed to dev only. Production still runs v1.0/v1.1 schema.

---

## Milestone History

| Milestone | Phases | Status |
|-----------|--------|--------|
| v1.0 Quality System Backend | 1-11 | SHIPPED 2026-02-15 |
| v1.1 NCR Disposition Operationalization | 12-17 | SHIPPED 2026-02-17 (GO WITH ACCEPTED WARNINGS) |
| v2.0 Quality Intelligence Platform | 18-24 | IN PROGRESS — Phase 21.1 complete, Phase 22 deferred, Phase 23 next |
| v3.0 Architectural Hardening | 25-33 | NOT STARTED — awaits v2.0 archive |

---

## What v2.0 Added (Knowledge Intelligence Layer)

The v2.0 milestone built a six-layer cascade:

```
L1: Taxonomy      — 82 active defect codes (e-coat, powder, liquid) after Phase 21.1 cleanup
L2: Classification — Bridge tables: DefectTypeProcessFamily, DefectTypeLineType, DefectTypeLineType
L3: Knowledge     — 9 knowledge extension tables, 1,894 seed rows across 68 defect codes
L4: Decision      — Advisory SP (usp_GetDefectKnowledge), pre-population SP, 9 retrieval views
L5: Transactions  — Existing gate SPs (unchanged) with gate-knowledge mapping documentation
L6: Analytics     — DEFERRED (Phase 22)
```

**Key principle:** Knowledge is advisory, never authoritative. Gate SPs enforce lifecycle rules. Knowledge retrieval happens alongside gates, not inside them.

---

## The Six-Layer Cascade (PLAT-01 Documentation Target)

One of Phase 23's deliverables is documenting this cascade as a repeatable operating model. The external AI should understand it:

- **Universal rows** (LineTypeId = NULL): Knowledge that applies to all coating processes. e.g., "Check bath pH" applies to e-coat, powder, and liquid. Authored to be process-agnostic.
- **Process-specific rows** (LineTypeId = ECOAT/POWDER/LIQUID): Knowledge specific to one process family. Retrieval precedence: process-specific FIRST, universal SECOND, merged without duplicates.
- **Extension model:** The same pattern applies to equipment domains, supplier domains, process parameter domains. Defect knowledge is the first implementation. Phase 23 must document how to extend it.

---

## Key Personnel Context

- **Chris Walsh** — Solo developer, Quality Systems architect at Select Finishing. Also the business owner who defines quality requirements. Commits daily to all three repos.
- No other developers on this project.
- All planning artifacts are written to enable autonomous GSD agent execution — the documentation standard is "a GSD agent could read this and execute without follow-up questions."
