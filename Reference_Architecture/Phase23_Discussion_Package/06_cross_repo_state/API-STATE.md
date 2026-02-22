# Project State

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-02-19)

**Core value:** deterministic proc/view gateway with preserved identity-to-RLS chain  
**Current focus:** Phase 3 complete - NCR Lifecycle endpoints delivered
**Contract manifest version:** 1.0.0 (`.planning/contracts/db-contract-manifest.snapshot.json`)
**API contract version:** 0.2.0 (`.planning/contracts/api-openapi.publish.json`)
**Contract gate mode:** advisory (pre-v1)

## Current Position

Phase: 3 of 10 (COMPLETE)
Plan: 3 of 3 in current phase (COMPLETE)
Status: Phase 3 complete -- all 25 NCR endpoints delivered, OpenAPI artifact bumped to 0.2.0
Last activity: 2026-02-22 -- DB manifest snapshot migration count sync + app snapshot re-sync to API v0.2.0

Progress: [████████░░] 30% (9 of 30 plans)

## Decisions

- Pinned Microsoft.AspNetCore.OpenApi to 9.x (10.x source generators incompatible with net9.0)
- SqlErrorMapper uses Dictionary.GetValueOrDefault returning int? for clean pattern matching
- CORS configured with explicit origin array from config, never AllowAnyOrigin
- OID extraction uses full URI claim type, not short 'oid' form (Easy Auth maps to URI)
- DbConnectionFactory logs session context set without exposing OID value
- Connection factory disposes SqlConnection on failure to prevent leaks
- OpenAPI document transformer sets title "SF Quality API" and version 0.2.0 (pre-v1)
- Claims diagnostic endpoint dev-only (IsDevelopment guard), health endpoint AllowAnonymous
- Endpoint groups follow extension method pattern (MapXxxEndpoints on WebApplication)
- Contract validators add guards incrementally (title, paths-present) without restructuring existing checks
- Drift handling uses three-tier version increment: patch (additive), minor (response shape), major (breaking removal)
- App snapshot synced to v0.2.0 (2026-02-22) -- app contract baseline aligned with API publish artifact
- Pre-v1 contract gate mode is advisory; post-v1 flips to blocking CI failure
- NCR request DTOs use C# record types with default parameters for optional fields
- Delete handler uses ExecuteAsync (no result set); other CRUD handlers use QuerySingleOrDefaultAsync
- CorrelationId passed to all NCR procs including DeleteNCR for full traceability
- Gate transition handlers use anonymous objects (no DynamicParameters) since no OUTPUT params needed
- RecordNcrDisposition uses JSON wrapper proc (GATE-06) not TVP proc (GATE-07)
- RejectVerificationRequest and ReopenNcrRequest enforce required ReasonComment via non-nullable parameter
- ReinvestigateNcrRequest allows optional ReasonComment via nullable parameter
- NCR endpoints use thin proc gateway pattern with C# record DTOs for request bodies
- RecordNcrDisposition uses JSON wrapper proc (GATE-06), TVP proc excluded from API surface
- 52xxx gate error codes mapped in SqlErrorMapper (52061->400, 52101->403, 52201->409, 52202/52203->422, 52301/52401->409)
- Utility endpoints (containment, documents, notes) use DynamicParameters with OUTPUT params for created IDs
- OpenAPI publish artifact bumped to 0.2.0 with all 25 NCR endpoint paths

## Blockers/Concerns

- Easy Auth claim/header behavior must be validated in deployed App Service environment

## Performance Metrics

| Phase-Plan | Duration | Tasks | Files |
|------------|----------|-------|-------|
| 01-01      | 4min     | 2     | 8     |
| 01-02      | 2min     | 2     | 5     |
| 01-03      | 2min     | 2     | 3     |
| 02-01      | 2min     | 2     | 1     |
| 02-02      | 2min     | 2     | 2     |
| 03-01      | 2min     | 2     | 3     |
| 03-02      | 2min     | 2     | 1     |
| 03-03      | 2min     | 2     | 4     |

---
*Updated: 2026-02-22 -- Contract snapshot parity refresh (DB manifest count + app OpenAPI snapshot sync).*
