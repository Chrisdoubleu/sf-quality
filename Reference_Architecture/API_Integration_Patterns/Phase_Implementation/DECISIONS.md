# API Integration Architecture — Architectural Decisions

Produced by running `../PERSONA_PROMPT.md` through a Senior API Platform Architect persona (February 2026).
Source AI output: `../AI Response.sql`
These decisions govern sf-quality-api phases 3.4 through 5.

---

## Decision 1: Delta Sync — EffectiveUpdatedAtUtc Pattern

**Decision:** Delta filter on `EffectiveUpdatedAtUtc = MAX(entity.ModifiedDateUtc, latest StatusHistory.ChangedDateUtc)`.
Delta list endpoints return IDs + `EffectiveUpdatedAtUtc` only (two-phase retrieval — not full detail).
Cursor is an opaque base64url token encoding `(AfterUpdatedAtUtc, AfterId)`.
RLS is not special-cased — session context filters first; delta filter is applied within that filtered set.

**Rationale:** `StatusHistory` alone misses field-level edits that don't transition state. `ModifiedDate` alone is incomplete if state transitions don't touch it. MAX of both is authoritative. Keeps the API thin — the DB owns what "updated" means.

**Prerequisite:** `ModifiedDate` must be reliably updated on every non-state edit (trigger or enforced proc convention). Verify before implementing delta endpoints — see Open Question 1.

**Scope change caution:** If a user gains plant access, they won't delta-discover older records that are newly visible. The app must trigger a full re-sync on scope change.

---

## Decision 2: Cursor Pagination — Keyset with Opaque Token

**Decision:** Keyset pagination (not offset). Opaque `nextCursor` token (base64url JSON). Standard response envelope:
```json
{ "data": [...], "paging": { "nextCursor": "...", "pageSize": 200 } }
```
Pagination logic lives in T-SQL stored procedures (wrap views with procs). Fetch `PageSize + 1` rows to detect `hasMore` without a COUNT query.

**Rationale:** Offset pagination is unstable in live operational queues — rows move between calls (SLA status changes, new NCRs appear). Keyset is stable and faster. Opaque cursors allow sort key changes later without breaking the frontend.

**Prerequisite:** Every paginated SP must have a deterministic sort order with a stable NcrId tie-breaker. Sort order must be explicit — not inferred from whatever order the view returns. See Open Question 2.

---

## Decision 3: Approval Workflow HTTP Surface — 202 Accepted

**Decision:** `50414` (APPROVAL_REQUIRED) → **HTTP 202 Accepted** (not 403, not 409).
Response body must include: `status = "ApprovalRequired"`, `approvalRecordId`, `entityType`, `entityId`, `toStatusCode`, `correlationId`.
Remove `50414` from `SqlErrorMapper` (or intercept it before the mapper in middleware).

**Endpoints:**
- `GET /workflow/pending-approvals` — approver queue, filterable by `?entityType=NCR&entityId=42`
- `POST /workflow/approvals/{approvalRecordId}/decision` — approve/reject

**DB contract:** `workflow.usp_TransitionState` must throw 50414 with a JSON message containing `approvalRecordId`. Pattern:
```sql
DECLARE @Msg nvarchar(4000) = (
    SELECT code = 50414, approvalRecordId = @ApprovalRecordId,
           entityType = @EntityType, entityId = @EntityId, toStatusCode = @ToStatusCode
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
);
THROW 50414, @Msg, 1;
```

**Rationale:** 403 means "you are forbidden." Approval-required is not forbidden — it is "accepted, pending." The frontend must receive a parseable outcome with `approvalRecordId` or it will scrape error strings. That destroys the contract.

**Compliance caution:** If you return 202, be consistent — 202 always means an approval record exists. Any deviation will confuse the frontend and auditors.

---

## Decision 4: Audit Call Logging Middleware

**Decision:** New `AuditApiCallLoggingMiddleware` placed **between `CorrelationId` and `ErrorHandling`** in the middleware chain.

**Middleware order:**
```
CorrelationId → AuditLogging → ErrorHandling → CORS → Auth → Authorization → SerilogRequestLogging → Endpoints
```

**Key behaviors:**
- Calls `_next(context)` (which runs `ErrorHandling` + the endpoint), then logs after — so `Response.StatusCode` is final
- Writes via `CreateForServiceAsync` (no session context — audit uses service identity)
- Logs every request including failures and SQL errors
- Never fails the API request if audit insert fails (catch + `_logger.LogError`)
- Entity extraction by convention: first path segment = `EntityType` (uppercase), route value `{id}` = `EntityId`
- Reads `context.Items["SqlErrorNumber"]` — populated by `ErrorHandlingMiddleware` (see Phase 3.4)

**GUID enforcement prerequisite:** Correlation IDs must be valid GUIDs before the audit table is created. The DB column is `uniqueidentifier NOT NULL`. Current `CorrelationIdMiddleware` accepts any string header.

**DB schema — `audit.ApiCallLog`:**

| Column | Type | Notes |
|--------|------|-------|
| `ApiCallLogId` | `bigint IDENTITY` PK | |
| `LoggedAtUtc` | `datetime2(7)` | DEFAULT `sysutcdatetime()` |
| `CorrelationId` | `uniqueidentifier NOT NULL` | |
| `RequestStartedUtc` | `datetime2(7) NOT NULL` | |
| `RequestEndedUtc` | `datetime2(7) NOT NULL` | |
| `DurationMs` | `int NOT NULL` | |
| `HttpMethod` | `nvarchar(10) NOT NULL` | |
| `Path` | `nvarchar(2048) NOT NULL` | |
| `QueryString` | `nvarchar(2048) NULL` | |
| `EndpointName` | `nvarchar(200) NULL` | from `endpoint.DisplayName` |
| `RoutePattern` | `nvarchar(400) NULL` | from `RouteEndpoint.RoutePattern.RawText` |
| `CallerAzureOid` | `uniqueidentifier NULL` | null for unauthenticated requests |
| `StatusCode` | `int NOT NULL` | |
| `EntityType` | `nvarchar(50) NULL` | first path segment, uppercase |
| `EntityId` | `int NULL` | route value `{id}` |
| `SqlErrorNumber` | `int NULL` | from `context.Items["SqlErrorNumber"]` |

**Retention caution:** This table grows fast. Plan for 180–365 day retention policy before the migration lands.

---

## Decision 5: Validate-Only Mode

**Decision:** Query parameter `?isValidateOnly=true` on **workflow/lifecycle transition endpoints only** — not every CRUD write.
Validate-only SPs must throw **identical business error codes** as the real SPs.
Success response:
```json
{ "validatedOnly": true, "canTransition": true, "approvalWouldBeRequired": false }
```
Validate-only must **never** create approval records.

**Rationale:** Validate-only for normal CRUD is wasted complexity for an internal single-tenant API. It's high-value specifically for workflow gate transitions where the risk of "accidentally submitting" is real. Identical error codes are critical — the frontend must be able to reuse the same error handling for both paths.

**Logic guard caution:** If the validate-only SP doesn't share the exact same guard logic as the real SP, you will get false positives ("validated OK" then the real submit fails). That destroys trust quickly.

---

## Revised Phase Sequence

| Phase | Scope | Key Deliverables | Hard Dependencies |
|-------|-------|------------------|-------------------|
| **3.4** *(new)* | sf-quality-api | GUID correlation IDs; 50414→202 handling + structured body; `SqlErrorNumber` stashing in `ErrorHandlingMiddleware`; remove 50414 from `SqlErrorMapper` | None — must precede 3.5 |
| **3.5** | sf-quality-db + api | `audit.ApiCallLog` table + `audit.usp_LogApiCall`; `AuditApiCallLoggingMiddleware` | 3.4 (GUID correlation IDs) |
| **4** | sf-quality-db + api | `CursorToken` helper; `PagedResponse<T>` envelope; delta-id list SPs + endpoints for NCR (then CAPA/SCAR/Complaint); paged queue SPs + endpoints | 3.5 |
| **4.5** *(can merge into 4)* | sf-quality-db + api | `usp_ValidateTransition` / per-entity validate SPs; `?isValidateOnly=true` on transition endpoints | 4 |
| **5** | sf-quality-db + api | `GET /workflow/pending-approvals`; `POST /workflow/approvals/{id}/decision`; filterable by entityType/entityId | 3.4 (50414 semantics), 4 (pagination) |
| **6** | sf-quality-db + api | CAPA/SCAR/Complaint/8D — reuse all patterns above | 4, 4.5, 5 |
| **9** | sf-quality-api | Internal notification endpoints | 5 |
| **10** | sf-quality-api | Rate limiting/quota — only if real perf issue | Last |

**Critical insight:** Phase 3.4 is a new phase that must be inserted before 3.5. The audit middleware depends on GUID-safe correlation IDs and on `ErrorHandlingMiddleware` exposing `SqlErrorNumber`. Without 3.4, the audit table will fail inserts on non-GUID correlation IDs.

---

## Three Open Questions (resolve before Phase 3.4 begins)

**Q1 — ModifiedDate reliability:** Is `ModifiedDate` truly updated on every non-state edit across NCR/CAPA/SCAR/Complaint?
If not, delta sync will silently miss changes. Options: add triggers, enforce proc convention, or use `rowversion`.
→ *Audit sf-quality-db migration history and `usp_Update*` proc bodies.*

**Q2 — Operational queue sort order:** What is the required business sort order for each queue (NCR queue, CAPA queue, pending approvals)?
Keyset pagination needs deterministic ordering locked in before the SP is written. Can't change it later without resetting cursors.
→ *Ask user/business before writing any queue SP.*

**Q3 — usp_TransitionState ApprovalRecordId surface:** How will `workflow.usp_TransitionState` surface `approvalRecordId` when throwing 50414?
Options: JSON message (recommended — see Decision 3 code sketch), result set with `approvalRequired + approvalRecordId`, or OUTPUT parameter.
→ *Check sf-quality-db Phase 27 spec and confirm approach before Phase 5.*
