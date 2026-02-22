Below is a concrete, right‑sized design that fits the existing minimal API + Dapper + stored-proc‑centric pattern, and it explicitly accounts for what your current code actually does (middleware order, correlation ID storage, SQL error mapping, Easy Auth OID extraction). 

CODEBASE_REFERENCE

1) Delta sync design for quality entities
Concrete recommendation

Delta filter on an “EffectiveUpdatedAtUtc” value = MAX(entity.ModifiedDateUtc, latest StatusHistory.ChangedDateUtc).

Make ModifiedDateUtc authoritative for non-state edits and enforce that it updates on every write (triggers or proc convention).

Delta list endpoints return IDs + EffectiveUpdatedAtUtc (not full detail). Consumers then fetch details by IDs (two‑phase retrieval) when needed.

Use a cursor that is based on (EffectiveUpdatedAtUtc, EntityId) keyset, and return it as an opaque token.

RLS is not special-cased: session context + RLS filters first; delta filter is applied within that filtered set. If user scope changes, you must do a re-sync.

Rationale (sf-quality specific)

StatusHistory is not enough because it misses field edits that don’t transition state (your own problem statement). ModifiedDate alone is also risky if state transitions don’t always touch it. So you take the max and move on.

This keeps the API thin. The DB owns what “updated” means; the API just passes updatedSince and cursor.

Because you already enforce RLS by atomically setting session context on connection open (DbConnectionFactory.CreateForUserAsync), you don’t need any “restricted entity list” special behavior from the reference architecture. Delta sync is per-caller visibility, period. 

CODEBASE_REFERENCE

Code sketch
T‑SQL: effective updated timestamp + keyset delta filter (IDs only)
CREATE OR ALTER PROCEDURE quality.usp_ListNcrDeltaIds
    @CallerAzureOid       uniqueidentifier,
    @UpdatedSinceUtc      datetime2(7) = NULL,  -- exclusive
    @UpdatedUntilUtc      datetime2(7) = NULL,  -- inclusive (optional)
    @AfterUpdatedAtUtc    datetime2(7) = NULL,  -- cursor component
    @AfterNcrId           int          = NULL,  -- cursor component
    @PageSize             int          = 200
AS
BEGIN
    SET NOCOUNT ON;

    IF @PageSize IS NULL OR @PageSize <= 0 OR @PageSize > 1000
        SET @PageSize = 200;

    ;WITH LatestStateChange AS
    (
        SELECT sh.EntityId,
               MAX(sh.ChangedDate) AS LastStateChangedUtc
        FROM workflow.StatusHistory sh
        WHERE sh.EntityType = 'NCR'
        GROUP BY sh.EntityId
    ),
    Base AS
    (
        SELECT n.NcrId,
               EffectiveUpdatedAtUtc =
                   CASE
                       WHEN l.LastStateChangedUtc IS NULL THEN n.ModifiedDate
                       WHEN n.ModifiedDate IS NULL THEN l.LastStateChangedUtc
                       WHEN l.LastStateChangedUtc > n.ModifiedDate THEN l.LastStateChangedUtc
                       ELSE n.ModifiedDate
                   END
        FROM quality.Ncr n
        LEFT JOIN LatestStateChange l ON l.EntityId = n.NcrId
        -- RLS predicates apply automatically here based on session context.
    )
    SELECT TOP (@PageSize + 1)
           NcrId,
           EffectiveUpdatedAtUtc
    FROM Base
    WHERE (@UpdatedSinceUtc IS NULL OR EffectiveUpdatedAtUtc >  @UpdatedSinceUtc)
      AND (@UpdatedUntilUtc IS NULL OR EffectiveUpdatedAtUtc <= @UpdatedUntilUtc)
      AND (
            @AfterUpdatedAtUtc IS NULL
            OR EffectiveUpdatedAtUtc > @AfterUpdatedAtUtc
            OR (EffectiveUpdatedAtUtc = @AfterUpdatedAtUtc AND NcrId > @AfterNcrId)
          )
    ORDER BY EffectiveUpdatedAtUtc ASC, NcrId ASC;
END

Notes that matter:

Sort is ascending and uses (EffectiveUpdatedAtUtc, NcrId) as the deterministic tie-breaker.

We fetch PageSize + 1 to let the API detect hasMore without extra COUNT().

C#: minimal API handler + opaque cursor
public record DeltaListRequest(
    DateTimeOffset? UpdatedSinceUtc = null,
    DateTimeOffset? UpdatedUntilUtc = null,
    string? Cursor = null,
    int? PageSize = null);

public record DeltaIdRow(int NcrId, DateTimeOffset EffectiveUpdatedAtUtc);

public record PagedResponse<T>(
    IReadOnlyList<T> Data,
    PagingInfo Paging);

public record PagingInfo(string? NextCursor, int PageSize);

private static async Task<IResult> ListNcrDeltaIds(
    HttpContext context,
    IDbConnectionFactory db,
    [AsParameters] DeltaListRequest q,
    CancellationToken ct)
{
    var oid = EasyAuthHandler.GetCallerOid(context.User);
    if (oid is null) return Results.Unauthorized();

    var pageSize = Math.Clamp(q.PageSize ?? 200, 1, 1000);

    // Cursor is opaque: base64url JSON with afterUpdatedAtUtc + afterId
    var cursor = CursorToken.TryDecode<DeltaCursor>(q.Cursor, out var c) ? c : null;

    await using var conn = await db.CreateForUserAsync(oid, ct);

    var rows = (await conn.QueryAsync<DeltaIdRow>(
        "quality.usp_ListNcrDeltaIds",
        new
        {
            CallerAzureOid = oid,
            UpdatedSinceUtc = q.UpdatedSinceUtc?.UtcDateTime,
            UpdatedUntilUtc = q.UpdatedUntilUtc?.UtcDateTime,
            AfterUpdatedAtUtc = cursor?.AfterUpdatedAtUtc,
            AfterNcrId = cursor?.AfterId,
            PageSize = pageSize
        },
        commandType: CommandType.StoredProcedure)).ToList();

    var hasMore = rows.Count > pageSize;
    var page = rows.Take(pageSize).ToList();

    string? nextCursor = null;
    if (hasMore)
    {
        var last = page[^1];
        nextCursor = CursorToken.Encode(new DeltaCursor(
            AfterUpdatedAtUtc: last.EffectiveUpdatedAtUtc.UtcDateTime,
            AfterId: last.NcrId));
    }

    return Results.Ok(new PagedResponse<DeltaIdRow>(page, new PagingInfo(nextCursor, pageSize)));
}

public record DeltaCursor(DateTime AfterUpdatedAtUtc, int AfterId);

public static class CursorToken
{
    public static string Encode<T>(T value)
    {
        var json = JsonSerializer.Serialize(value);
        var bytes = Encoding.UTF8.GetBytes(json);
        return Base64UrlTextEncoder.Encode(bytes);
    }

    public static bool TryDecode<T>(string? token, out T? value)
    {
        value = default;
        if (string.IsNullOrWhiteSpace(token)) return false;

        try
        {
            var bytes = Base64UrlTextEncoder.Decode(token);
            value = JsonSerializer.Deserialize<T>(bytes);
            return value is not null;
        }
        catch { return false; }
    }
}
Cautions

If ModifiedDate is not reliably updated on every edit, your delta sync will silently miss updates. Fix that in DB first (trigger or enforced proc convention).

Scope changes break incremental sync semantics. If a user gains a plant, they won’t “delta‑discover” older records that are newly visible. The app must do a full sync on scope change (or at least a wide updatedSince backfill).

2) Cursor pagination design for operational queues
Concrete recommendation

Paginate operational queues (/ncr/queue, CAPA queue, pending approvals). Don’t ship 5,000 rows to a web UI by default.

Use keyset pagination with an opaque cursor token, not offset pagination.

Standardize a single response envelope for paged endpoints:
{"data":[...], "paging": {"nextCursor":"...", "pageSize": 200}}

Put pagination logic in T‑SQL stored procedures, even if the source today is a view (quality.vw_NcrOperationalQueue). Wrap the view.

Rationale (sf-quality specific)

Offset paging is cheap to implement but painful in live operational queues: rows move between calls (SLA status changes, new NCRs appear), and offsets get unstable. Keyset is stable and faster under load.

Opaque cursors are still useful internally because they prevent accidental coupling to sort keys and give you freedom to adjust ordering later without breaking the frontend.

You’re already stored‑proc oriented. A proc wrapper around the view is the cleanest place for keyset.

Code sketch
T‑SQL: paged operational queue wrapper

Define an explicit stable ordering and a stable cursor key. Don’t pretend you can keyset paginate on “whatever order the view currently returns”.

Example ordering:

breached first,

then due date,

then NcrId tie-breaker.

CREATE OR ALTER PROCEDURE quality.usp_GetNcrOperationalQueuePage
    @CallerAzureOid    uniqueidentifier,
    @AfterRank         tinyint      = NULL,
    @AfterDueUtc       datetime2(7) = NULL,
    @AfterNcrId        int          = NULL,
    @PageSize          int          = 200
AS
BEGIN
    SET NOCOUNT ON;

    IF @PageSize IS NULL OR @PageSize <= 0 OR @PageSize > 1000
        SET @PageSize = 200;

    ;WITH Q AS
    (
        SELECT
            NcrId,
            -- Example fields from the view (you’ll match real column names):
            DueUtc,
            IsBreached,
            SlaStatus,
            -- Stable sort rank:
            Rank = CASE
                WHEN IsBreached = 1 THEN CONVERT(tinyint, 0)
                WHEN SlaStatus = 'AT_RISK' THEN CONVERT(tinyint, 1)
                WHEN SlaStatus = 'ON_TRACK' THEN CONVERT(tinyint, 2)
                ELSE CONVERT(tinyint, 3)
            END,
            -- ... other queue columns ...
            *
        FROM quality.vw_NcrOperationalQueue
        -- RLS applies via session context.
    )
    SELECT TOP (@PageSize + 1) *
    FROM Q
    WHERE (
        @AfterRank IS NULL
        OR Rank > @AfterRank
        OR (Rank = @AfterRank AND ISNULL(DueUtc, '9999-12-31') > ISNULL(@AfterDueUtc, '0001-01-01'))
        OR (Rank = @AfterRank AND ISNULL(DueUtc, '9999-12-31') = ISNULL(@AfterDueUtc, '0001-01-01') AND NcrId > @AfterNcrId)
    )
    ORDER BY Rank ASC, ISNULL(DueUtc, '9999-12-31') ASC, NcrId ASC;
END
C#: same paging envelope + cursor token

Cursor JSON contains { afterRank, afterDueUtc, afterNcrId }. Same CursorToken helper from above.

Cautions

You must lock down a deterministic sort order (with a tie-breaker). If your sort order isn’t deterministic, your cursor is garbage.

Queues that change constantly will still show “shifting content” between pages. Keyset minimizes this, but it doesn’t eliminate real-world churn. The UI must tolerate it.

3) Approval workflow HTTP surface
Concrete recommendation

Treat “approval required” as HTTP 202 Accepted, not 403 or 409.

Provide both:

GET /workflow/pending-approvals (approver queue; canonical discovery)

POST /workflow/approvals/{approvalRecordId}/decision (approve/reject)

Add a targeted “lookup” endpoint for UI convenience without duplicating per-entity:

GET /workflow/pending-approvals?entityType=NCR&entityId=42

When approval is required, return a body that includes:

approvalRecordId

entityType, entityId, toStatusCode

correlationId

Rationale (sf-quality specific)

403 means “you’re forbidden”. Approval required is not forbidden. It’s “accepted, pending”. Your own codebase already flags this mismatch as an open design issue. 

CODEBASE_REFERENCE

Single-tenant internal API: you don’t need fancy hypermedia. You do need a clean outcome contract so the frontend can behave correctly without parsing error strings.

workflow.usp_GetPendingApprovals already filters by caller permissions, which is exactly what the queue endpoint should do. 

CODEBASE_REFERENCE

Code sketch
Middleware change: special-case 50414 into 202 with structured body

Right now 50414 is mapped to 403 in SqlErrorMapper, and ErrorHandlingMiddleware always returns {error, correlationId} for mapped SQL exceptions. 

CODEBASE_REFERENCE


That is incompatible with “approval required is not an error”.

Fix it like this:

catch (SqlException ex) when (ex.Number == 50414)
{
    // Store for audit middleware (see section 4)
    context.Items["SqlErrorNumber"] = ex.Number;

    context.Response.ContentType = "application/json";
    context.Response.StatusCode = StatusCodes.Status202Accepted;

    // Strong recommendation: DB throws JSON message that includes approvalRecordId.
    // Example message: {"code":50414,"approvalRecordId":12345,"entityType":"NCR","entityId":42,"toStatusCode":"OPEN"}
    var payload = TryParseJson(ex.Message) ?? new { code = 50414, message = "Approval required." };

    await context.Response.WriteAsJsonAsync(new
    {
        status = "ApprovalRequired",
        details = payload,
        correlationId = context.Items["CorrelationId"]?.ToString()
    });
    return;
}

And remove 50414 from SqlErrorMapper (or at least stop treating it as a 4xx). If you leave it mapped, someone will “fix” the middleware later and break semantics again.

Approval endpoints (minimal API + Dapper)
public record ProcessApprovalRequest(string Decision, string? Comments = null);

private static async Task<IResult> GetPendingApprovals(
    HttpContext context,
    IDbConnectionFactory db,
    string? entityType,
    int? entityId,
    string? cursor,
    int? pageSize,
    CancellationToken ct)
{
    var oid = EasyAuthHandler.GetCallerOid(context.User);
    if (oid is null) return Results.Unauthorized();

    await using var conn = await db.CreateForUserAsync(oid, ct);

    // Best: add optional filtering + paging in the SP itself.
    var rows = await conn.QueryAsync(
        "workflow.usp_GetPendingApprovals",
        new { CallerAzureOid = oid },
        commandType: CommandType.StoredProcedure);

    // Right-sized fallback (if SP can’t filter yet): filter in API.
    if (!string.IsNullOrWhiteSpace(entityType))
        rows = rows.Where(r => ((string)r.EntityType).Equals(entityType, StringComparison.OrdinalIgnoreCase));
    if (entityId.HasValue)
        rows = rows.Where(r => (int)r.EntityId == entityId.Value);

    return Results.Ok(rows);
}

private static async Task<IResult> ProcessApprovalDecision(
    int approvalRecordId,
    HttpContext context,
    IDbConnectionFactory db,
    ProcessApprovalRequest request,
    CancellationToken ct)
{
    var oid = EasyAuthHandler.GetCallerOid(context.User);
    if (oid is null) return Results.Unauthorized();

    await using var conn = await db.CreateForUserAsync(oid, ct);

    var result = await conn.QuerySingleAsync(
        "workflow.usp_ProcessApprovalStep",
        new
        {
            CallerAzureOid = oid,
            ApprovalRecordId = approvalRecordId,
            Decision = request.Decision,   // "APPROVE" / "REJECT"
            Comments = request.Comments
        },
        commandType: CommandType.StoredProcedure);

    return Results.Ok(result);
}
T‑SQL: make 50414 throw JSON with ApprovalRecordId

You already have a precedent for JSON error messages for 52xxx NCR gate codes. 

CODEBASE_REFERENCE


Do the same for 50414.

-- Inside workflow.usp_TransitionState when approval is created:
DECLARE @ApprovalRecordId int = SCOPE_IDENTITY();

DECLARE @Msg nvarchar(4000) =
    (SELECT
        code = 50414,
        approvalRecordId = @ApprovalRecordId,
        entityType = @EntityType,
        entityId = @EntityId,
        toStatusCode = @ToStatusCode
     FOR JSON PATH, WITHOUT_ARRAY_WRAPPER);

THROW 50414, @Msg, 1;
Cautions

Don’t make the frontend parse error strings to get approvalRecordId. If you do, you’ve created an unmaintainable contract.

Approval flows create compliance expectations. If you return 202, you must be consistent: 202 always means “approval record exists” (or “approval required”) and provides a stable way to fetch it.

4) Audit call logging middleware design
Concrete recommendation

Add a new middleware AuditApiCallLoggingMiddleware that logs every request (success and failure).

Write logs using service-scoped connection (CreateForServiceAsync), but record the caller’s OID from claims when available.

Make it synchronous but low-cost, and never fail the API request because the audit insert failed.

Middleware order should be:

CorrelationId → AuditLogging → ErrorHandling → CORS → Auth → Authorization → SerilogRequestLogging → Endpoints

Fix a real bug now: your correlation ID is currently an arbitrary string; your audit table requirement says CorrelationId UNIQUEIDENTIFIER NOT NULL. Enforce GUID correlation IDs in middleware.

Rationale (sf-quality specific)

Compliance-wise, you need attempted actions and failed actions too (especially permission denials, SoD violations, transition blocks).

You already have the plumbing to open a “service connection” (no session context). That’s exactly the right tool for audit writes. 

CODEBASE_REFERENCE

Placing audit middleware outside error handling lets it observe final HTTP status codes (because error handling converts exceptions into responses).

Code sketch
Fix correlation ID to be GUID-compatible

Right now you accept any incoming X-Correlation-Id and echo it. 

CODEBASE_REFERENCE


That will break your DB insert if the client sends “abc”.

var correlationId = context.Request.Headers.TryGetValue(HeaderName, out var existing)
    && Guid.TryParse(existing.ToString(), out var parsed)
        ? parsed.ToString()
        : Guid.NewGuid().ToString();

Keep header name same; just enforce validity.

Audit table DDL
CREATE TABLE audit.ApiCallLog
(
    ApiCallLogId        bigint IDENTITY(1,1) NOT NULL CONSTRAINT PK_ApiCallLog PRIMARY KEY,
    LoggedAtUtc         datetime2(7) NOT NULL CONSTRAINT DF_ApiCallLog_LoggedAtUtc DEFAULT (sysutcdatetime()),

    CorrelationId       uniqueidentifier NOT NULL,

    RequestStartedUtc   datetime2(7) NOT NULL,
    RequestEndedUtc     datetime2(7) NOT NULL,
    DurationMs          int NOT NULL,

    HttpMethod          nvarchar(10) NOT NULL,
    Path                nvarchar(2048) NOT NULL,
    QueryString         nvarchar(2048) NULL,

    EndpointName        nvarchar(200) NULL,
    RoutePattern        nvarchar(400) NULL,

    CallerAzureOid      uniqueidentifier NULL,
    StatusCode          int NOT NULL,

    EntityType          nvarchar(50) NULL,
    EntityId            int NULL,

    SqlErrorNumber      int NULL
);
GO

(You can add ClientIp and UserAgent later if you actually use them.)

Logging stored proc (keeps API insert stable)
CREATE OR ALTER PROCEDURE audit.usp_LogApiCall
    @CorrelationId      uniqueidentifier,
    @RequestStartedUtc  datetime2(7),
    @RequestEndedUtc    datetime2(7),
    @DurationMs         int,
    @HttpMethod         nvarchar(10),
    @Path               nvarchar(2048),
    @QueryString        nvarchar(2048) = NULL,
    @EndpointName       nvarchar(200)  = NULL,
    @RoutePattern       nvarchar(400)  = NULL,
    @CallerAzureOid     uniqueidentifier = NULL,
    @StatusCode         int,
    @EntityType         nvarchar(50) = NULL,
    @EntityId           int = NULL,
    @SqlErrorNumber     int = NULL
AS
BEGIN
    SET NOCOUNT ON;

    INSERT audit.ApiCallLog
    (
        CorrelationId, RequestStartedUtc, RequestEndedUtc, DurationMs,
        HttpMethod, Path, QueryString, EndpointName, RoutePattern,
        CallerAzureOid, StatusCode, EntityType, EntityId, SqlErrorNumber
    )
    VALUES
    (
        @CorrelationId, @RequestStartedUtc, @RequestEndedUtc, @DurationMs,
        @HttpMethod, @Path, @QueryString, @EndpointName, @RoutePattern,
        @CallerAzureOid, @StatusCode, @EntityType, @EntityId, @SqlErrorNumber
    );
END
Middleware: extracts entity context by convention, writes via service connection
public sealed class AuditApiCallLoggingMiddleware
{
    private readonly RequestDelegate _next;
    private readonly IDbConnectionFactory _db;
    private readonly ILogger<AuditApiCallLoggingMiddleware> _logger;

    public AuditApiCallLoggingMiddleware(
        RequestDelegate next,
        IDbConnectionFactory db,
        ILogger<AuditApiCallLoggingMiddleware> logger)
    {
        _next = next;
        _db = db;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        var started = DateTime.UtcNow;

        await _next(context); // ErrorHandlingMiddleware should be INSIDE this, so status code is final.

        var ended = DateTime.UtcNow;
        var durationMs = (int)Math.Max(0, (ended - started).TotalMilliseconds);

        var correlationIdString = context.Items["CorrelationId"]?.ToString();
        _ = Guid.TryParse(correlationIdString, out var correlationId);

        var oidString = EasyAuthHandler.GetCallerOid(context.User);
        Guid? callerOid = Guid.TryParse(oidString, out var parsedOid) ? parsedOid : null;

        var endpoint = context.GetEndpoint();
        var endpointName = endpoint?.DisplayName; // or read IEndpointNameMetadata if you want WithName()
        var routePattern = (endpoint as RouteEndpoint)?.RoutePattern?.RawText;

        // Entity extraction by convention:
        // - entityType = first path segment
        // - entityId = route value "id" if present
        var entityType = context.Request.Path.Value?
            .Split('/', StringSplitOptions.RemoveEmptyEntries)
            .FirstOrDefault()
            ?.ToUpperInvariant();

        int? entityId = null;
        if (context.Request.RouteValues.TryGetValue("id", out var idObj)
            && idObj is not null
            && int.TryParse(idObj.ToString(), out var id))
        {
            entityId = id;
        }

        // ErrorHandlingMiddleware should store SqlErrorNumber into Items when it handles SQL exceptions.
        int? sqlErrorNumber = context.Items.TryGetValue("SqlErrorNumber", out var numObj)
            && numObj is int n ? n : null;

        try
        {
            await using var conn = await _db.CreateForServiceAsync(context.RequestAborted);

            await conn.ExecuteAsync(
                "audit.usp_LogApiCall",
                new
                {
                    CorrelationId = correlationId,
                    RequestStartedUtc = started,
                    RequestEndedUtc = ended,
                    DurationMs = durationMs,
                    HttpMethod = context.Request.Method,
                    Path = context.Request.Path.Value ?? "",
                    QueryString = context.Request.QueryString.HasValue ? context.Request.QueryString.Value : null,
                    EndpointName = endpointName,
                    RoutePattern = routePattern,
                    CallerAzureOid = callerOid,
                    StatusCode = context.Response.StatusCode,
                    EntityType = entityType,
                    EntityId = entityId,
                    SqlErrorNumber = sqlErrorNumber
                },
                commandType: CommandType.StoredProcedure);
        }
        catch (Exception ex)
        {
            // Never fail the request because audit logging failed.
            _logger.LogError(ex, "Failed to write audit ApiCallLog");
        }
    }
}
Minimal change to ErrorHandlingMiddleware to expose SQL error number for audit
catch (SqlException ex) when (SqlErrorMapper.MapToHttpStatus(ex.Number) is int status)
{
    context.Items["SqlErrorNumber"] = ex.Number;
    ...
}
catch (SqlException ex)
{
    context.Items["SqlErrorNumber"] = ex.Number;
    ...
}
Cautions

Retention: this table will grow fast. If you don’t plan retention (e.g., 180–365 days) you’ll hate yourself later.

Correlation ID must be a GUID if the DB column is uniqueidentifier. Right now it isn’t guaranteed. Fix it before the first insert migration lands.

5) Validate-only mode
Concrete recommendation

Use query parameter:
POST /ncr/{id}/submit?isValidateOnly=true

Support validate-only on workflow/lifecycle transition endpoints (gate transitions), not every CRUD write. That’s where the risk and complexity are.

Validate-only must produce identical error behavior as the real operation:

same SQL business error numbers

same HTTP statuses via SqlErrorMapper

same { error, correlationId } envelope

For success, return 200 OK with a small explicit result:

{"validatedOnly": true, "canTransition": true, "approvalWouldBeRequired": false }

If approval would be required, return approvalWouldBeRequired: true (but do not create an approval record).

Rationale (sf-quality specific)

Query param requires zero DTO churn and matches the reference pattern. It also keeps the handler signature clean.

“Validate every write” is a SaaS/platform pattern. You’re building an internal API for one frontend. Validate-only for normal CRUD is mostly wasted work; validate-only for workflow transitions is high value.

Identical error behavior is easiest when SQL throws the same error codes in validate-only paths. Otherwise you force C# to interpret error codes (business logic leakage).

Code sketch
API handler: choose proc based on isValidateOnly
private static async Task<IResult> SubmitNcr(
    int id,
    HttpContext context,
    IDbConnectionFactory db,
    GateTransitionRequest? request,
    bool isValidateOnly,
    CancellationToken ct)
{
    var oid = EasyAuthHandler.GetCallerOid(context.User);
    if (oid is null) return Results.Unauthorized();

    var correlationId = context.Items["CorrelationId"]?.ToString();
    await using var conn = await db.CreateForUserAsync(oid, ct);

    if (isValidateOnly)
    {
        // Validate-only SP must throw the same business codes on failure.
        var validation = await conn.QuerySingleAsync(
            "quality.usp_ValidateSubmitNcr", // or workflow.usp_ValidateTransition + NCR-specific checks
            new { CallerAzureOid = oid, NcrId = id, CorrelationId = correlationId, Comments = request?.Comments },
            commandType: CommandType.StoredProcedure);

        return Results.Ok(new
        {
            validatedOnly = true,
            canTransition = true,
            approvalWouldBeRequired = (bool?)validation.ApprovalWouldBeRequired ?? false
        });
    }

    var result = await conn.QuerySingleOrDefaultAsync(
        "quality.usp_SubmitNcr",
        new { CallerAzureOid = oid, NcrId = id, CorrelationId = correlationId, Comments = request?.Comments },
        commandType: CommandType.StoredProcedure);

    return Results.Ok(result);
}
T‑SQL: validate-only transition pattern

Don’t return “IsValid = 0” rows. Throw business codes, same as the real proc.

CREATE OR ALTER PROCEDURE quality.usp_ValidateSubmitNcr
    @CallerAzureOid uniqueidentifier,
    @NcrId          int,
    @CorrelationId  uniqueidentifier = NULL,
    @Comments       nvarchar(2000) = NULL
AS
BEGIN
    SET NOCOUNT ON;

    -- Run the same guard checks as quality.usp_SubmitNcr would run.
    -- If a guard fails, THROW the same error numbers/messages.

    -- Example:
    IF NOT EXISTS (SELECT 1 FROM quality.Ncr WHERE NcrId = @NcrId)
        THROW 50404, 'NCR not found.', 1;

    -- If approval would be required, DO NOT create approval.
    -- Just return a hint.
    DECLARE @ApprovalWouldBeRequired bit = 0;
    -- ... compute based on approval config ...
    SELECT ApprovalWouldBeRequired = @ApprovalWouldBeRequired;
END
Cautions

If validate-only doesn’t share the exact same guard logic, you will get false positives (“validated OK” then real submit fails). That destroys trust fast.

If you create approval records in validate-only, you will spam approval queues during testing. Don’t.

6) Revised API phase sequence

Your earlier plan list has a mismatch with your prompt: you describe approvals as Phase 5, but the codebase reference lists approvals as Phase 7. I’m going to re-sequence based on dependencies, not the label numbers. 

CODEBASE_REFERENCE

Revised sequence (dependency-driven)

Phase 3.4 (new, small but mandatory): plumbing fixes

Enforce correlation IDs as GUIDs (or change audit schema type; GUID is better).

Decide and implement 50414 semantics (202 Accepted) + structured body.

Update ErrorHandlingMiddleware to stash SqlErrorNumber in HttpContext.Items for audit.

Phase 3.5: audit call logging

DB: audit.ApiCallLog + audit.usp_LogApiCall

API: AuditApiCallLoggingMiddleware placed between CorrelationId and ErrorHandling

Phase 4: paging + delta sync foundations

Shared cursor token helper

Paged response envelope standard

DB paging wrappers for queue/list endpoints

Delta ID list procs for NCR (then CAPA/SCAR/Complaint)

Phase 4.5 (can be part of Phase 4): validate-only for workflow transitions

Requires DB validate procs / validate pathways

Update OpenAPI for isValidateOnly query param on transition endpoints

Phase 5: approval workflow endpoints

GET /workflow/pending-approvals (paged)

POST /workflow/approvals/{id}/decision

Optional: filter by entityType/entityId

This depends on pagination patterns and 50414→202 behavior.

Phase 6: CAPA/SCAR/Complaint/8D entity groups

Implement using the now-standard paging/delta/validate/approval semantics

This avoids re-litigating design decisions per resource group.

Phase 9: internal notifications endpoints

Phase 10: rate limiting / quota

For a single-tenant internal API, do this last unless you have a real abuse/perf problem.

Key dependency you were missing: you can’t do audit logging cleanly until correlation IDs are GUID-safe and approval-required semantics are resolved (because you explicitly want 50414 logged as “successful”). 

CODEBASE_REFERENCE

7) Three open questions to resolve before implementation

Is ModifiedDate truly updated for every non-state edit across NCR/CAPA/SCAR/Complaint?
If not, delta sync will miss changes. You either need triggers, strict proc conventions, or a rowversion-based approach.

What is the stable, required sort order for each operational queue (NCR/CAPA/pending approvals)?
Keyset pagination needs deterministic ordering keys. If the business wants “sort by SLA, then priority, then due date”, you must encode that and include every ordering column in the cursor token.

How will workflow.usp_TransitionState surface the ApprovalRecordId when approval is required?
Options:

Throw 50414 with JSON message including approvalRecordId (recommended)

Return a normal result set with approvalRequired and approvalRecordId (bigger DB contract change)

Output parameter (clean but requires API changes to pass DynamicParameters)

You need one clean path or the frontend will end up scraping strings.

If you want one “starter set” to unblock Phase 3.4/3.5 quickly, do these first:

correlationId GUID enforcement

50414 → 202 handling + JSON payload

audit middleware + audit table/proc contract

Everything else builds on that cleanly.