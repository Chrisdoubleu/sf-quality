# Phase 22: Analytics Foundation and Security — DEFERRED

**Decision date:** 2026-02-21
**Decided by:** Chris Walsh
**Status:** DEFERRED — preconditions not met

## Rationale

Phase 22 is deferred because all three of its deliverables depend on preconditions that are not yet satisfied:

1. **Analytics views (ANALYTICS-01..07):** Schema is still evolving. Every view creates a dependency on underlying table columns — future schema changes (column renames, FK restructuring, table additions) would break views and increase maintenance burden. Dev environment has zero NCR/CAPA transactional data, so views cannot be meaningfully tested. No consumer (API endpoint, reporting tool) exists to query them.

2. **Security grants (SEC-01):** The 5-role architecture from migration 123 was built for v1.0/v1.1 operational needs. The v2.0 knowledge layer introduces new access patterns that may not fit the existing roles. Granting to `dbrole_ncr_ops_read` now would lock in assumptions about the role model before API consumption patterns are clear.

3. **v1.0 KPI view assessment (INTEL-06):** Documentation-only deliverable with no urgency. Assessment is more valuable when the analytics views are being actively designed.

## What Is Deferred

| Requirement | Description | Status |
|-------------|-------------|--------|
| ANALYTICS-01 | `analytics` schema creation | DEFERRED |
| ANALYTICS-02 | vw_DefectPareto | DEFERRED |
| ANALYTICS-03 | vw_RootCauseDistribution (v2) | DEFERRED |
| ANALYTICS-04 | vw_ProcessZoneConcentration | DEFERRED |
| ANALYTICS-05 | vw_RecurrenceTracking | DEFERRED |
| ANALYTICS-06 | vw_EffectivenessTrending | DEFERRED |
| ANALYTICS-07 | vw_ControlPointGapAnalysis | DEFERRED |
| INTEL-06 | v1.0 KPI view assessment | DEFERRED |
| SEC-01 | Security grants for v2.0 objects | DEFERRED (grants ship inline — see below) |

## What Is NOT Deferred

**SEC-01 grants ship inline:** When an API endpoint is built that needs access to a v2.0 object, the required GRANT statement ships in whatever migration is current at that time. This avoids both premature role architecture lock-in and access-denied blockers during API development.

## Preconditions to Revisit

Phase 22 should be revisited when ALL of the following are true:

1. **Schema stable** — no further table/column changes expected for knowledge or transactional tables
2. **Real consumers exist** — API endpoints or reporting tools actively querying v2.0 objects
3. **Role architecture locked** — the 5-role model is confirmed as final, or a revised model is designed
4. **Transactional data available** — NCRs flowing through the system so analytics views return meaningful results and can be validated

## Impact on Phases 23 and 24

- **Phase 23** (Platform Governance, Documentation, and Deployment) proceeds next. Its Apply-v2.0.ps1 deploy orchestration covers migrations 125-130 (what's deployed today). Analytics migrations will be added when Phase 22 executes.
- **Phase 24** (Incoming Substrate and NCR Integration) has no dependency on Phase 22 and can proceed independently.
