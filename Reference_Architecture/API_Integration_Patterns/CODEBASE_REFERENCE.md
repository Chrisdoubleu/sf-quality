# sf-quality-api Codebase Reference

**Purpose:** Self-contained reference for an AI working on API Integration pattern refinement (Phases 3.5, 4, 5, 7, 9, 10) in `sf-quality-api`. Contains verbatim source code from the existing project so you can reason about patterns, extension points, and constraints without codebase access.

**Companion to:** `PERSONA_PROMPT.md` in this folder, and `../Hidden_Patterns/Phase_Implementation/CODEBASE_REFERENCE.md` for the DB layer.

---

## 1. Project Layout

```
sf-quality-api/
├── src/SfQualityApi/
│   ├── Program.cs
│   ├── Auth/
│   │   ├── EasyAuthHandler.cs
│   │   └── ClientPrincipal.cs
│   ├── Endpoints/
│   │   ├── NcrEndpoints.cs          ← 27 endpoints, THE reference for all patterns
│   │   └── DiagnosticEndpoints.cs
│   ├── Infrastructure/
│   │   ├── DbConnectionFactory.cs
│   │   ├── IDbConnectionFactory.cs
│   │   └── SqlErrorMapper.cs
│   └── Middleware/
│       ├── CorrelationIdMiddleware.cs
│       └── ErrorHandlingMiddleware.cs
├── .planning/
│   └── contracts/
│       ├── api-openapi.publish.json          ← OpenAPI contract (source of truth for API design)
│       └── db-contract-manifest.snapshot.json ← DB procs/views available to call
```

**Tech versions:** ASP.NET Core 9, C# 13, Dapper 2.x, Microsoft.Data.SqlClient, Serilog, Polly 8, Scalar (OpenAPI explorer)

---

## 2. Program.cs — Full Source

```csharp
using Microsoft.AspNetCore.Authentication;
using Microsoft.Data.SqlClient;
using Polly;
using Polly.Retry;
using Scalar.AspNetCore;
using Serilog;
using SfQualityApi.Auth;
using SfQualityApi.Infrastructure;
using SfQualityApi.Endpoints;
using SfQualityApi.Middleware;

var builder = WebApplication.CreateBuilder(args);

// Serilog: structured logging with correlation ID enrichment
builder.Host.UseSerilog((ctx, config) => config
    .ReadFrom.Configuration(ctx.Configuration)
    .Enrich.FromLogContext());

// CORS: explicit origins from configuration, never AllowAnyOrigin
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.WithOrigins(builder.Configuration.GetSection("Cors:Origins").Get<string[]>() ?? [])
              .AllowAnyHeader()
              .AllowAnyMethod()
              .AllowCredentials()
              .WithExposedHeaders("X-Correlation-Id", "Location");
    });
});

// Authentication: Easy Auth header parsing
builder.Services.AddAuthentication(EasyAuthHandler.SchemeName)
    .AddScheme<AuthenticationSchemeOptions, EasyAuthHandler>(EasyAuthHandler.SchemeName, null);
builder.Services.AddAuthorization();

// Connection factory: atomic open + session context for user connections
builder.Services.AddSingleton<IDbConnectionFactory>(sp =>
    new DbConnectionFactory(
        builder.Configuration.GetConnectionString("SqlDb")!,
        sp.GetRequiredService<ILogger<DbConnectionFactory>>()));

// Polly resilience pipeline: transient SQL retry with exponential backoff + jitter
builder.Services.AddResiliencePipeline("sql-transient", pipeline =>
{
    pipeline.AddRetry(new RetryStrategyOptions
    {
        ShouldHandle = new PredicateBuilder().Handle<SqlException>(ex => ex.IsTransient),
        MaxRetryAttempts = 3,
        Delay = TimeSpan.FromSeconds(1),
        BackoffType = DelayBackoffType.Exponential,
        UseJitter = true
    });
});

// OpenAPI document generation
builder.Services.AddOpenApi(options =>
{
    options.AddDocumentTransformer((document, context, ct) =>
    {
        document.Info.Title = "SF Quality API";
        document.Info.Version = "0.2.0";
        return Task.CompletedTask;
    });
});

var app = builder.Build();

// Middleware pipeline — ORDER MATTERS
app.UseMiddleware<CorrelationIdMiddleware>();
app.UseMiddleware<ErrorHandlingMiddleware>();
app.UseCors();
app.UseAuthentication();
app.UseAuthorization();
app.UseSerilogRequestLogging();

// Development-only: OpenAPI and Scalar API explorer
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
    app.MapScalarApiReference();
}

app.MapDiagnosticEndpoints();
app.MapNcrEndpoints();

app.Run();
```

---

## 3. Infrastructure — Full Sources

### DbConnectionFactory.cs

```csharp
using System.Data;
using Dapper;
using Microsoft.Data.SqlClient;

namespace SfQualityApi.Infrastructure;

/// <summary>
/// Creates SQL connections with atomic session context enforcement.
/// For user-scoped operations, the connection is opened and session context is set
/// before the connection is returned, preventing RLS leakage via connection pooling.
/// </summary>
public sealed class DbConnectionFactory : IDbConnectionFactory
{
    private readonly string _connectionString;
    private readonly ILogger<DbConnectionFactory> _logger;

    public DbConnectionFactory(string connectionString, ILogger<DbConnectionFactory> logger)
    {
        _connectionString = connectionString;
        _logger = logger;
    }

    /// <summary>Creates a user-scoped connection with session context set for RLS.</summary>
    public async Task<SqlConnection> CreateForUserAsync(string callerOid, CancellationToken ct = default)
    {
        if (string.IsNullOrWhiteSpace(callerOid))
            throw new ArgumentException("Caller OID must not be null or empty.", nameof(callerOid));

        var conn = new SqlConnection(_connectionString);
        try
        {
            await conn.OpenAsync(ct);
            await conn.ExecuteAsync(
                "dbo.usp_SetSessionContext",
                new { CallerAzureOid = callerOid },
                commandType: CommandType.StoredProcedure);
            _logger.LogDebug("Session context set for caller");
            return conn;
        }
        catch
        {
            await conn.DisposeAsync();
            throw;
        }
    }

    /// <summary>Creates a service-scoped connection without user session context (for background jobs).</summary>
    public async Task<SqlConnection> CreateForServiceAsync(CancellationToken ct = default)
    {
        var conn = new SqlConnection(_connectionString);
        try
        {
            await conn.OpenAsync(ct);
            return conn;
        }
        catch
        {
            await conn.DisposeAsync();
            throw;
        }
    }
}
```

### IDbConnectionFactory.cs

```csharp
using Microsoft.Data.SqlClient;

namespace SfQualityApi.Infrastructure;

public interface IDbConnectionFactory
{
    Task<SqlConnection> CreateForUserAsync(string callerOid, CancellationToken ct = default);
    Task<SqlConnection> CreateForServiceAsync(CancellationToken ct = default);
}
```

---

## 4. Middleware — Full Sources

### CorrelationIdMiddleware.cs

```csharp
using Serilog.Context;

namespace SfQualityApi.Middleware;

/// <summary>
/// Extracts or generates X-Correlation-Id on every request, propagates it to
/// response headers and Serilog LogContext for structured log enrichment.
/// </summary>
public class CorrelationIdMiddleware
{
    private const string HeaderName = "X-Correlation-Id";
    private readonly RequestDelegate _next;

    public CorrelationIdMiddleware(RequestDelegate next) => _next = next;

    public async Task InvokeAsync(HttpContext context)
    {
        var correlationId = context.Request.Headers.TryGetValue(HeaderName, out var existing)
            ? existing.ToString()
            : Guid.NewGuid().ToString();

        context.Items["CorrelationId"] = correlationId;
        context.Response.Headers[HeaderName] = correlationId;

        using (LogContext.PushProperty("CorrelationId", correlationId))
        {
            await _next(context);
        }
    }
}
```

### ErrorHandlingMiddleware.cs

```csharp
using Microsoft.Data.SqlClient;
using SfQualityApi.Infrastructure;

namespace SfQualityApi.Middleware;

/// <summary>
/// Global exception handler. Maps SqlException business codes to HTTP status via
/// SqlErrorMapper. Unmapped SQL errors and non-SQL exceptions return 500.
/// Always includes correlationId in error response body.
/// </summary>
public class ErrorHandlingMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<ErrorHandlingMiddleware> _logger;

    public ErrorHandlingMiddleware(RequestDelegate next, ILogger<ErrorHandlingMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        try
        {
            await _next(context);
        }
        catch (SqlException ex) when (SqlErrorMapper.MapToHttpStatus(ex.Number) is int status)
        {
            _logger.LogWarning("Business SQL error {SqlErrorNumber} mapped to HTTP {HttpStatus}: {Message}",
                ex.Number, status, ex.Message);

            context.Response.ContentType = "application/json";
            context.Response.StatusCode = status;
            await context.Response.WriteAsJsonAsync(new
            {
                error = ex.Message,
                correlationId = context.Items["CorrelationId"]?.ToString()
            });
        }
        catch (SqlException ex)
        {
            _logger.LogError(ex, "Unmapped SQL error {SqlErrorNumber}: {Message}", ex.Number, ex.Message);
            context.Response.ContentType = "application/json";
            context.Response.StatusCode = 500;
            await context.Response.WriteAsJsonAsync(new
            {
                error = "An internal error occurred.",
                correlationId = context.Items["CorrelationId"]?.ToString()
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unhandled exception: {Message}", ex.Message);
            context.Response.ContentType = "application/json";
            context.Response.StatusCode = 500;
            await context.Response.WriteAsJsonAsync(new
            {
                error = "An internal error occurred.",
                correlationId = context.Items["CorrelationId"]?.ToString()
            });
        }
    }
}
```

---

## 5. SqlErrorMapper — SQL Code → HTTP Status Mapping (Verbatim)

```csharp
public static class SqlErrorMapper
{
    // 50402-50409 are intentionally unmapped: not currently emitted by sf-quality-db;
    // unmapped codes fall through to 500 and trigger drift review.
    private static readonly Dictionary<int, int> BusinessErrorMap = new()
    {
        [50400] = 400, // Bad Request (validation)
        [50401] = 401, // Unauthorized
        [50404] = 404, // Not Found
        [50410] = 403, // Feature denied
        [50411] = 403, // Permission denied
        [50412] = 403, // Scope denied
        [50413] = 403, // Constraint denied (SoD violation)
        [50414] = 403, // Approval required         ← ALREADY MAPPED to 403
        [50415] = 403, // Approval config invalid
        [50416] = 403, // Approval apply expired
        [50417] = 403, // Approval duplicate request
        [50418] = 403, // Config conflict
        [50419] = 403, // Policy unavailable

        // 52xxx: NCR gate error codes (migrations 112-118)
        // Messages are JSON-structured: {"code":52201,"gate":"GATE-02",...}
        [52061] = 400, // Void without reason (validation)
        [52101] = 403, // Gate authority denied
        [52201] = 409, // Transition blocked (Conflict)
        [52202] = 422, // Completeness validation (Unprocessable Entity)
        [52203] = 422, // Under-commit reconciliation (Unprocessable Entity)
        [52301] = 409, // CAPA readiness blocking (Conflict)
        [52401] = 409, // Customer approval pending (Conflict)
    };

    public static int? MapToHttpStatus(int sqlErrorNumber)
        => BusinessErrorMap.GetValueOrDefault(sqlErrorNumber);

    public static bool IsBusinessError(int sqlErrorNumber)
        => BusinessErrorMap.ContainsKey(sqlErrorNumber);
}
```

**Critical note for Phase 5 design:** 50414 (APPROVAL_REQUIRED) is already mapped to HTTP **403**. The question in PERSONA_PROMPT.md section 3 is whether this mapping is semantically correct — 403 implies "you are forbidden", but 50414 means "transition request was accepted and approval created". This is the open design question to resolve before Phase 5 implementation.

---

## 6. Auth — EasyAuthHandler (Verbatim)

Azure Easy Auth injects claims via `X-MS-CLIENT-PRINCIPAL` header (Base64-encoded JSON).

```csharp
public sealed class EasyAuthHandler : AuthenticationHandler<AuthenticationSchemeOptions>
{
    public const string SchemeName = "EasyAuth";

    /// <summary>
    /// Full URI claim type for Azure AD OID.
    /// Easy Auth maps the short "oid" to this URI form. Using "oid" directly will NOT work.
    /// </summary>
    public const string OidClaimType =
        "http://schemas.microsoft.com/identity/claims/objectidentifier";

    private const string ClientPrincipalHeader = "X-MS-CLIENT-PRINCIPAL";

    protected override Task<AuthenticateResult> HandleAuthenticateAsync()
    {
        if (!Request.Headers.TryGetValue(ClientPrincipalHeader, out var headerValues)
            || string.IsNullOrWhiteSpace(headerValues.FirstOrDefault()))
            return Task.FromResult(AuthenticateResult.NoResult());

        byte[] decoded;
        try { decoded = Convert.FromBase64String(headerValues.First()!); }
        catch (FormatException) { return Task.FromResult(AuthenticateResult.Fail("Invalid client principal encoding")); }

        ClientPrincipal? principal;
        try { principal = JsonSerializer.Deserialize<ClientPrincipal>(Encoding.UTF8.GetString(decoded)); }
        catch (JsonException) { return Task.FromResult(AuthenticateResult.Fail("Invalid client principal")); }

        if (principal?.Claims is null || principal.Claims.Count == 0)
            return Task.FromResult(AuthenticateResult.Fail("Invalid client principal"));

        var identity = new ClaimsIdentity(
            principal.Claims.Select(c => new Claim(c.Type, c.Value)),
            principal.AuthenticationType,
            principal.NameClaimType,
            principal.RoleClaimType);

        var ticket = new AuthenticationTicket(new ClaimsPrincipal(identity), Scheme.Name);
        return Task.FromResult(AuthenticateResult.Success(ticket));
    }

    /// <summary>Extracts the caller's Azure AD OID from the authenticated principal.</summary>
    public static string? GetCallerOid(ClaimsPrincipal user) =>
        user.FindFirstValue(OidClaimType);
}
```

**Usage in every endpoint handler:**
```csharp
var oid = EasyAuthHandler.GetCallerOid(context.User);
if (oid is null) return Results.Unauthorized();
```

The OID is passed as `@CallerAzureOid UNIQUEIDENTIFIER` to all stored procedures. `dbo.usp_SetSessionContext` resolves it to an internal `AppUserId` for RLS and audit triggers.

---

## 7. Endpoint Pattern — Complete NCR Example

This is the full `NcrEndpoints.cs`. **Every new endpoint file must follow this exact pattern.** No deviations.

### Handler pattern (mutation with OUTPUT parameter):
```csharp
private static async Task<IResult> CreateNcrQuick(
    HttpContext context,
    IDbConnectionFactory db,
    CreateNcrQuickRequest request,
    CancellationToken ct)
{
    var oid = EasyAuthHandler.GetCallerOid(context.User);
    if (oid is null) return Results.Unauthorized();

    var correlationId = context.Items["CorrelationId"]?.ToString();
    await using var conn = await db.CreateForUserAsync(oid, ct);

    var p = new DynamicParameters();
    p.Add("CallerAzureOid", oid);
    p.Add("PlantId", request.PlantId);
    // ... other params ...
    p.Add("NewNcrId", dbType: DbType.Int32, direction: ParameterDirection.Output);

    var result = await conn.QuerySingleOrDefaultAsync(
        "quality.usp_CreateNcrQuick",
        p,
        commandType: CommandType.StoredProcedure);

    var newId = p.Get<int>("NewNcrId");
    return Results.Created($"/ncr/{newId}", result);
}
```

### Handler pattern (query, no OUTPUT parameter):
```csharp
private static async Task<IResult> SubmitNcr(
    int id,
    HttpContext context,
    IDbConnectionFactory db,
    GateTransitionRequest? request,
    CancellationToken ct)
{
    var oid = EasyAuthHandler.GetCallerOid(context.User);
    if (oid is null) return Results.Unauthorized();

    var correlationId = context.Items["CorrelationId"]?.ToString();
    await using var conn = await db.CreateForUserAsync(oid, ct);

    var result = await conn.QuerySingleOrDefaultAsync(
        "quality.usp_SubmitNcr",
        new { CallerAzureOid = oid, NcrId = id, CorrelationId = correlationId, Comments = request?.Comments },
        commandType: CommandType.StoredProcedure);

    return Results.Ok(result);
}
```

### Handler pattern (view query, no stored procedure):
```csharp
private static async Task<IResult> GetOpenNcrSummary(
    HttpContext context,
    IDbConnectionFactory db,
    CancellationToken ct)
{
    var oid = EasyAuthHandler.GetCallerOid(context.User);
    if (oid is null) return Results.Unauthorized();

    await using var conn = await db.CreateForUserAsync(oid, ct);
    var rows = await conn.QueryAsync(
        "SELECT * FROM quality.vw_OpenNCRSummary",
        commandType: CommandType.Text);

    return Results.Ok(rows);
}
```

### Endpoint registration pattern:
```csharp
public static WebApplication MapNcrEndpoints(this WebApplication app)
{
    var group = app.MapGroup("/ncr")
        .WithTags("NCR")
        .RequireAuthorization();

    group.MapPost("/", CreateNcrQuick)
        .WithName("CreateNcrQuick")
        .WithSummary("Create NCR with minimum required fields")
        .Produces<object>(201)
        .ProducesProblem(400);

    // ... more endpoints ...
    return app;
}
```

### DTO pattern (C# record):
```csharp
public record CreateNcrQuickRequest(
    int PlantId,
    int DefectTypeId,
    string Description,
    decimal QuantityAffected,
    string? Comments = null,
    int? PriorityLevelId = null,
    int? SeverityRatingId = null);

public record GateTransitionRequest(string? Comments = null);
```

---

## 8. Existing Endpoints (Phase 3 Complete)

### /ncr — NCR Endpoints (27 endpoints)

**CRUD:**
- `POST /ncr/` — CreateNcrQuick (min fields)
- `POST /ncr/full` — CreateNcr (all fields)
- `PUT /ncr/{id}` — UpdateNcr
- `DELETE /ncr/{id}` — DeleteNcr

**Lifecycle transitions (gate endpoints):**
- `POST /ncr/{id}/submit` — DRAFT → OPEN
- `POST /ncr/{id}/containment/complete` — OPEN → CONTAINED
- `POST /ncr/{id}/investigation/start` — CONTAINED → INVEST
- `POST /ncr/{id}/disposition` — Records disposition lines (JSON payload)
- `POST /ncr/{id}/verification/submit` — DISPOSED → PENDVERIF
- `POST /ncr/{id}/close` — Normal or fast-close
- `POST /ncr/{id}/void` — Void with reason

**Edge transitions (regressions):**
- `POST /ncr/{id}/verification/reject` — PENDVERIF → INVEST
- `POST /ncr/{id}/reopen` — CLOSED → OPEN
- `POST /ncr/{id}/reinvestigate` — DISPOSED → INVEST

**Sub-resources:**
- `POST /ncr/{id}/containment` — Create or update containment action
- `POST /ncr/{id}/documents` — Create and link document
- `POST /ncr/{id}/notes` — Add typed operational note

**Views (dashboard/reporting):**
- `GET /ncr/summary` — Open NCR summary
- `GET /ncr/queue` — Operational queue with SLA status
- `GET /ncr/{id}/linked-entities` — Linked CAPAs, SCARs, complaints
- `GET /ncr/pareto` — Defect type Pareto analysis
- `GET /ncr/{id}/disposition-balance` — Disposition vs quantity balance
- `GET /ncr/hold-aging` — Hold location aging
- `GET /ncr/customer-approval-aging` — Customer approval aging
- `GET /ncr/gate-audit` — Gate transition audit trail

---

## 9. Upcoming API Phases (Reference)

| Phase | Description | DB Dependency |
|-------|-------------|--------------|
| **Phase 3.5** | Audit call logging middleware → `audit.ApiCallLog` | DB Phase 29 (audit.ApiCallLog table) |
| **Phase 4** | Pagination + delta sync + validate-only on list/write endpoints | DB Phase 32 (validate-only procs) |
| **Phase 5** | CAPA, SCAR, Complaint, 8D endpoints (full entity groups) | DB current state |
| **Phase 7** | Approval workflow endpoints (pending approvals queue, process approval) | DB Phase 28 (notification queue) |
| **Phase 9** | Internal notification endpoints (approval notifications, SLA alerts) | DB Phase 30 (SLA batch jobs) |
| **Phase 10** | Rate limiting + quota enforcement at API layer | No DB dependency |

**Phase ordering note:** Phase 3.5 requires `audit.ApiCallLog` to exist in DB (Phase 29). Phase 4 requires validate-only procs (DB Phase 32). Phase 7 requires the approval workflow endpoints and notification queue (DB Phase 28).

---

## 10. DB Layer — Key Stored Procedures Available to Call

All procs callable from the API. Full DDL and signatures are in `../Hidden_Patterns/Phase_Implementation/CODEBASE_REFERENCE.md`.

### Workflow/transition procs:
```
workflow.usp_TransitionState(@CallerAzureOid, @EntityType, @EntityId, @ToStatusCode, @Comments, @TransitionReason)
    → Returns: StatusHistory row
    → Throws: 50400 (guard failed), 50401 (unauthorized), 50404 (not found), 50414 (APPROVAL_REQUIRED)

workflow.usp_ProcessApprovalStep(@CallerAzureOid, @ApprovalRecordId, @Decision, @Comments)
    → Returns: ApprovalRecord row with IsChainComplete flag
    → Throws: 50401 (not authorized approver), 50413 (SoD violation)

workflow.usp_GetPendingApprovals(@CallerAzureOid)
    → Returns: Table of pending ApprovalRecord rows filtered by caller's role/permission
    → No throws — returns empty set if no pending approvals
```

### NCR procs (sample — Phase 3 complete):
```
quality.usp_CreateNcrQuick(@CallerAzureOid, @PlantId, @DefectTypeId, @Description, @QuantityAffected, ...)
    → Output: @NewNcrId INT
    → Returns: NCR summary row

quality.usp_SubmitNcr(@CallerAzureOid, @NcrId, @CorrelationId, @Comments)
    → Returns: Updated NCR row

quality.usp_CloseNcr(@CallerAzureOid, @NcrId, @FastClose, @CorrelationId, @Comments)
    → Returns: Updated NCR row
```

### Views available (called directly with SELECT * FROM):
```
quality.vw_OpenNCRSummary
quality.vw_NcrOperationalQueue
quality.vw_NcrLinkedEntities
quality.vw_NCRPareto
quality.vw_NcrDispositionBalance
quality.vw_NcrHoldAging
quality.vw_NcrCustomerApprovalAging
quality.vw_NcrGateAudit
```

### Planned procs (not yet created — Phase 32 target):
```
workflow.usp_ValidateTransition(@CallerAzureOid, @EntityType, @EntityId, @ToStatusCode)
    → Returns: IsValid BIT, ErrorCode INT NULL, ErrorMessage NVARCHAR(500) NULL
    → Does NOT commit any changes
```

---

## 11. DB Schema for audit.ApiCallLog (to be designed)

This table does NOT yet exist. It is created in DB Phase 29. The API Phase 3.5 middleware will write to it on every request.

**What the reference spec says should be logged:**
- Calling user
- Operation type (HTTP method + endpoint)
- Primary key references (EntityType, EntityId where applicable)
- Outcome (HTTP status code)
- Timestamps

**Design it yourself.** Key constraints:
- Must be idempotent migration (IF NOT EXISTS guard)
- NOT temporal — it's an immutable log, not a configurable entity
- Must not block request completion (async fire-and-forget or inline low-cost write)
- `CorrelationId UNIQUEIDENTIFIER NOT NULL` — links to the API middleware correlation ID
- Must be writable by the API service account (not via user session context — the service account writes audit logs, not the user)
- Should capture 50414 (APPROVAL_REQUIRED) responses as successful, not errors

---

## 12. Contract Chain

```
sf-quality-db:
  .planning/db-contract-manifest.json         ← procs/views the API can call (currently stale)

sf-quality-api:
  .planning/contracts/api-openapi.publish.json   ← OpenAPI contract (governs API development)
  .planning/contracts/db-contract-manifest.snapshot.json ← snapshot of DB contract at API phase start
```

**The OpenAPI publish contract** (`api-openapi.publish.json`) is the source of truth for what the API must implement. New endpoints must be designed in the OpenAPI spec first, then implemented in code. The spec version is currently `0.2.0`.

**Manifest staleness note:** The `db-contract-manifest.json` is at v1.0.0 and reflects phases 1–20. It doesn't include Phase 21's 9 knowledge views and 1 procedure. Must be refreshed before Phase 4 API planning begins.
