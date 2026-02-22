# API Integration Architecture — Implementation Handoff

## Purpose

This document is the starting point for implementing sf-quality-api phases 3.4 through 5.

Read these files before writing any code:
1. `DECISIONS.md` (this folder) — 5 locked architectural decisions + revised phase sequence + 3 open questions
2. `../CODEBASE_REFERENCE.md` — verbatim current API source (Program.cs, all middleware, SqlErrorMapper, EasyAuthHandler, NcrEndpoints.cs)
3. `../PERSONA_PROMPT.md` — full design rationale and context

The raw AI analysis that produced these decisions: `../AI Response.sql`

---

## Current API State (Phase 3 / 10)

- 27 endpoints in `Endpoints/NcrEndpoints.cs` — this is the reference for all patterns
- Middleware chain (current): `CorrelationId → ErrorHandling → CORS → Auth → Authorization → SerilogRequestLogging → Endpoints`
- No audit logging yet
- No pagination — list endpoints return full datasets
- No delta sync — no `updatedSince` filtering
- No validate-only mode
- `50414` (APPROVAL_REQUIRED) currently maps to **HTTP 403** in `SqlErrorMapper` — this is wrong and must be fixed in Phase 3.4

---

## Phase 3.4 — Plumbing Fixes (sf-quality-api only)

Three changes to existing files. No new DB migration required.

### 1. `Middleware/CorrelationIdMiddleware.cs` — Enforce GUID correlation IDs

Current behavior: accepts any incoming `X-Correlation-Id` header value as-is.
Required: if incoming value is a valid GUID string, use it; otherwise generate `Guid.NewGuid()`.

```csharp
var correlationId = context.Request.Headers.TryGetValue(HeaderName, out var existing)
    && Guid.TryParse(existing.ToString(), out var parsed)
        ? parsed.ToString()
        : Guid.NewGuid().ToString();
```

**Why:** The `audit.ApiCallLog.CorrelationId` column is `uniqueidentifier NOT NULL`. Any non-GUID value will fail the insert.

### 2. `Middleware/ErrorHandlingMiddleware.cs` — Two changes

**Change A:** Stash `SqlErrorNumber` in `HttpContext.Items` for every caught `SqlException`:
```csharp
catch (SqlException ex) when (SqlErrorMapper.MapToHttpStatus(ex.Number) is int status)
{
    context.Items["SqlErrorNumber"] = ex.Number; // ADD THIS
    ...
}
catch (SqlException ex)
{
    context.Items["SqlErrorNumber"] = ex.Number; // ADD THIS
    ...
}
```

**Change B:** Add a new `catch` block before the mapped SQL handler to intercept `50414` and return HTTP 202:
```csharp
catch (SqlException ex) when (ex.Number == 50414)
{
    context.Items["SqlErrorNumber"] = ex.Number;
    context.Response.ContentType = "application/json";
    context.Response.StatusCode = StatusCodes.Status202Accepted;

    // usp_TransitionState throws 50414 with a JSON message body (see DECISIONS.md §3)
    // Parse it, or fall back to a generic body if parsing fails
    await context.Response.WriteAsJsonAsync(new
    {
        status = "ApprovalRequired",
        correlationId = context.Items["CorrelationId"]?.ToString()
        // approvalRecordId comes from the parsed JSON message — see DECISIONS.md §3
    });
}
```

### 3. `Infrastructure/SqlErrorMapper.cs` — Remove 50414

Remove the `50414 → 403` entry from the mapping dictionary. 50414 is now handled by the middleware before `SqlErrorMapper` is reached.

---

## Phase 3.5 — Audit Call Logging

### DB (sf-quality-db — new migration)

New file: `NNN_add_audit_api_call_log.sql`

Create `audit.ApiCallLog` table and `audit.usp_LogApiCall` stored procedure. Full column definition is in `DECISIONS.md §4`.

Key constraints:
- `CorrelationId uniqueidentifier NOT NULL` — must be a real GUID (enforced by Phase 3.4)
- Add a retention policy or note in the migration: this table needs row deletion after 180–365 days
- Use `audit` schema (existing — the audit schema is established)

### API (sf-quality-api — new file)

New file: `Middleware/AuditApiCallLoggingMiddleware.cs`

Register in `Program.cs` immediately after `CorrelationIdMiddleware`:
```csharp
app.UseMiddleware<CorrelationIdMiddleware>();
app.UseMiddleware<AuditApiCallLoggingMiddleware>(); // ADD HERE
app.UseMiddleware<ErrorHandlingMiddleware>();
```

Full middleware implementation in `../AI Response.sql` §4.

**Critical detail:** The middleware calls `await _next(context)` first, then reads `context.Response.StatusCode` and `context.Items["SqlErrorNumber"]` after. This is how it captures the final outcome including SQL errors that `ErrorHandlingMiddleware` converted to HTTP responses.

---

## Phase 4 — Pagination + Delta Sync

### New shared infrastructure (sf-quality-api)

**`Infrastructure/CursorToken.cs`** — opaque base64url cursor encoder/decoder:
- `CursorToken.Encode<T>(value)` → base64url JSON string
- `CursorToken.TryDecode<T>(token, out value)` → bool

Full implementation in `../AI Response.sql` §1.

**`Models/PagedResponse.cs`** — standard response envelope:
```csharp
public record PagedResponse<T>(IReadOnlyList<T> Data, PagingInfo Paging);
public record PagingInfo(string? NextCursor, int PageSize);
```

### New endpoints — NCR (sf-quality-api)

Add to `Endpoints/NcrEndpoints.cs`:
- `GET /ncr/delta-ids` → calls `quality.usp_ListNcrDeltaIds`
- `GET /ncr/queue` → calls `quality.usp_GetNcrOperationalQueuePage`

### New SPs (sf-quality-db — new migration)

- `quality.usp_ListNcrDeltaIds` — keyset delta list (see `../AI Response.sql` §1 for DDL sketch)
- `quality.usp_GetNcrOperationalQueuePage` — paged queue wrapper (see `../AI Response.sql` §2 for DDL sketch)

**Before writing queue SPs:** Answer Open Question 2 — confirm the business sort order for the NCR queue. The keyset cursor must encode every sort column.

---

## Phase 4.5 — Validate-Only Mode

### DB (sf-quality-db)

The Phase 32 DB plan includes `workflow.usp_ValidateTransition`. Verify it:
- Throws identical business error codes as `usp_TransitionState` on failure
- Returns `SELECT ApprovalWouldBeRequired = @bit` on success
- Does NOT create approval records

### API (sf-quality-api)

Add `bool isValidateOnly = false` to transition endpoint handlers. When true, call the validate SP and return:
```json
{ "validatedOnly": true, "canTransition": true, "approvalWouldBeRequired": false }
```

Full handler pattern in `../AI Response.sql` §5.

---

## Phase 5 — Approval Workflow Endpoints

### Prerequisite check

Before writing any endpoint code, verify in sf-quality-db that `workflow.usp_TransitionState` throws `50414` with a JSON message body containing `approvalRecordId`. If it doesn't, that DB change must land first.

See Open Question 3 and `DECISIONS.md §3` for the exact JSON THROW pattern.

### New file: `Endpoints/WorkflowEndpoints.cs`

- `GET /workflow/pending-approvals` — calls `workflow.usp_GetPendingApprovals`, supports `?entityType=&entityId=` filter, returns paged `PagedResponse<T>`
- `POST /workflow/approvals/{approvalRecordId}/decision` — calls `workflow.usp_ProcessApprovalStep` with `Decision` (APPROVE/REJECT) and `Comments`

Register in `Program.cs` (add `WorkflowEndpoints.MapWorkflowEndpoints(app)` after NCR endpoints).

Full handler sketches in `../AI Response.sql` §3.

---

## Files Changed by Phase

| File | Phase | Change |
|------|-------|--------|
| `Middleware/CorrelationIdMiddleware.cs` | 3.4 | Enforce GUID |
| `Middleware/ErrorHandlingMiddleware.cs` | 3.4 | Stash SqlErrorNumber; add 50414→202 handler |
| `Infrastructure/SqlErrorMapper.cs` | 3.4 | Remove 50414 entry |
| `Program.cs` | 3.5 | Register AuditApiCallLoggingMiddleware |
| `Middleware/AuditApiCallLoggingMiddleware.cs` | 3.5 | New |
| `Infrastructure/CursorToken.cs` | 4 | New |
| `Models/PagedResponse.cs` | 4 | New |
| `Endpoints/NcrEndpoints.cs` | 4, 4.5 | Add delta/queue/validate endpoints |
| `Endpoints/WorkflowEndpoints.cs` | 5 | New |

---

## Open Questions — Must Resolve First

See `DECISIONS.md` §"Three Open Questions":

1. **ModifiedDate reliability** — audit sf-quality-db `usp_Update*` proc bodies before writing `usp_ListNcrDeltaIds`
2. **Queue sort order** — ask user/business before writing any paged queue SP
3. **50414 message format** — check sf-quality-db Phase 27 spec; confirm `usp_TransitionState` throws JSON with `approvalRecordId` before Phase 5
