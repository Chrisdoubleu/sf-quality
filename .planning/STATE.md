# STATE.md — sf-quality

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-26)

**Core value:** Manufacturing operators and quality engineers can initiate, route, track, and close quality events — with full audit trails — without leaving the system.
**Current focus:** Milestone v1.0 — Spring Pivot + Forms Foundation

## Current Position

Phase: Not started (defining requirements)
Plan: —
Status: Defining requirements
Last activity: 2026-02-26 — Milestone v1.0 started

## Accumulated Context

**Cross-repo execution model:**
Planning artifacts live in `sf-quality` workspace root. Each phase targets a specific child repo. To execute a phase, the user switches to that repo's Claude Code context:
- `sf-quality-api` — Spring Boot migration phases
- `sf-quality-app` — Forms architecture phases
- `sf-quality-db` — Database phases (if any)
- `sf-quality` — Adjudication / deliverables phases (workspace-level)

**Forms Research Consolidation state:**
- Stages 00-02 complete (sources → extraction → synthesis)
- Stage 03 (adjudication) not started — requires user decisions on 11 items in `Reference_Architecture/Forms_Research_Consolidation/02_synthesis/DECISION_BRIEF.md`
- Stage 04 (deliverables) blocked on adjudication

**Spring Boot migration context:**
- C# API is a thin pass-through: receive request → call stored proc via Dapper → return JSON
- Translation target: Spring Boot REST controllers + MyBatis mappers (NOT Spring Data JPA)
- OpenAPI contract shape must be preserved so sf-quality-app requires no changes
- Colleague (Java/Spring Boot) is advising; agentic coding implements

**Key architectural constraint from research:**
- Form UX logic (conditional fields, field visibility, client validation) → TypeScript in sf-quality-app
- Data integrity logic (foreign keys, status transitions, approval rules) → T-SQL stored procedures
- Spring Boot API stays thin — no business logic added to Java layer
