# Roadmap: SF Quality API

## Phases

- [x] **Phase 1: Foundation Infrastructure** ✓
  - **Goal:** Implement API foundation infrastructure with identity/session-context safety and contract-chain awareness
  - **Plans:** 3 plans
    - [x] 01-01-PLAN.md — Project scaffold, middleware pipeline, Serilog, and SqlErrorMapper
    - [x] 01-02-PLAN.md — Easy Auth handler, atomic connection factory, and Polly resilience
    - [x] 01-03-PLAN.md — Diagnostic endpoints, OpenAPI artifact generation, and build verification
- [x] **Phase 2: Contract Publication and Sync Guardrails** ✓
  - **Goal:** Establish cross-repo contract publication and sync guardrails with validated DB manifest snapshot, hardened OpenAPI publication scripts, and documented drift handling policy
  - **Plans:** 2 plans
    - [x] 02-01-PLAN.md — Contract validation script hardening and OpenAPI artifact alignment
    - [x] 02-02-PLAN.md — Cross-repo research completion, drift policy, and requirements traceability
- [x] **Phase 3: NCR Lifecycle Endpoints** ✓
  - **Goal:** Deliver all NCR lifecycle REST endpoints as a thin proc/view gateway preserving identity-to-RLS chain, with expanded error mapping and OpenAPI contract sync
  - **Plans:** 3 plans
    - [x] 03-01-PLAN.md — NCR CRUD endpoints, summary views, SqlErrorMapper 52xxx expansion
    - [x] 03-02-PLAN.md — NCR lifecycle gate and edge transition endpoints
    - [x] 03-03-PLAN.md — NCR utility endpoints, remaining views, OpenAPI artifact update, contract sync
- [ ] **Phase 3.5: API Infrastructure Hardening**
  - **Goal:** Harden the API layer with URL versioning, audit trail middleware, and rate limiting before domain endpoint expansion
  - **Plans:** 2 plans
    - [ ] 03.5-01-PLAN.md — URL versioning: migrate all routes to `/v1` prefix via route groups; OpenAPI artifact → v0.3.0 (Pattern #32)
    - [ ] 03.5-02-PLAN.md — Audit trail middleware writing to `audit.ApiCallLog` via Dapper; rate limiter policies in Program.cs (Patterns #28, #30)
  - **DB Prerequisite:** `audit.ApiCallLog` table must exist (DB Phase 29)
  - **Pre-check:** Confirm Phase 3.4 middleware plumbing (GUID correlation, SqlErrorNumber stash, 50414→202) is complete first
- [ ] **Phase 4: CAPA, Complaint, and Pagination Infrastructure**
  - **Plans:** 3 plans (expanded to include cursor pagination + query governor per Patterns #31, #34)
- [ ] **Phase 5: SCAR, Audit, and 8D Endpoints**
  - **DB Prerequisite:** DB Phase 31 (SCAR party status columns) for SCAR endpoints
- [ ] **Phase 6: RCA Tools Endpoints**
- [ ] **Phase 7: Workflow, Action Items, Feature Gating, and Validate-Only**
  - **Plans:** Scope expanded to include feature gating (Pattern #25) and validate-only passthrough (Pattern #33)
  - **DB Prerequisite:** DB Phase 32 (validate-only on write procs)
- [ ] **Phase 8: Knowledge and Traceability Endpoints**
- [ ] **Phase 9: Dashboards and View Endpoints**
- [ ] **Phase 10: Integration Endpoints, App Service Deployment, and Governance Promotion**

## Execution Notes

- API accepts delegated user tokens forwarded from `sf-quality-app` server handlers.
- API remains client-agnostic; no frontend runtime assumptions in endpoint implementation.
- OpenAPI publication artifact is required in CI for downstream app snapshot sync.
- Governance checks are advisory pre-v1 and promoted to blocking post-v1.
- Every future phase plan/research cycle must include explicit cross-repo checks in both `sf-quality-db` and `sf-quality-app`.
- After each execute wave, run `pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly` and include the result in the wave summary.

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation Infrastructure | 3/3 | ✓ Complete | 2026-02-19 |
| 2. Contract Publication and Sync Guardrails | 2/2 | ✓ Complete | 2026-02-19 |
| 3. NCR Lifecycle Endpoints | 3/3 | ✓ Complete | 2026-02-19 |
| 3.5. API Infrastructure Hardening | 0/2 | Not started | - |
| 4. CAPA, Complaint, and Pagination Infrastructure | 0/3 | Not started | - |
| 5. SCAR, Audit, and 8D Endpoints | 0/2 | Not started | - |
| 6. RCA Tools Endpoints | 0/2 | Not started | - |
| 7. Workflow, Action Items, Feature Gating, and Validate-Only | 0/2 | Not started | - |
| 8. Knowledge and Traceability Endpoints | 0/2 | Not started | - |
| 9. Dashboards and View Endpoints | 0/3 | Not started | - |
| 10. Integration Endpoints, App Service Deployment, and Governance Promotion | 0/2 | Not started | - |

---
*Updated: 2026-02-22 — Phase 3.5 inserted; Phase 4 expanded to 3 plans; Phase 7 scope updated*
