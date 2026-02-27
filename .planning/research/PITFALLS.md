# Domain Pitfalls

**Domain:** Spring Boot API migration from ASP.NET Core / Dapper
**Researched:** 2026-02-27

## Critical Pitfalls

Mistakes that cause silent data access bugs or require architectural rework.

### Pitfall 1: Session Context Not Set Before Query (Silent RLS Bypass)
**What goes wrong:** If `usp_SetSessionContext` is not called on the connection before a user query, Azure SQL's Row-Level Security has no caller identity. Queries may return all rows (no filtering) or fail silently depending on RLS policy.
**Why it happens:** MyBatis manages connections through HikariCP. A connection may be reused from the pool with stale session context from a previous request, or session context may never be set if the interceptor does not fire.
**Consequences:** Data leaked across users. RLS policies silently ineffective. Security audit failure.
**Prevention:** MyBatis Interceptor on Executor.query and Executor.update that calls `usp_SetSessionContext` BEFORE every SQL statement. Verify with integration test: two sequential requests with different OIDs must see different data.
**Detection:** Log the OID being set in session context at DEBUG level. Monitor for null OIDs in production. Write a canary test that asserts RLS filtering.

### Pitfall 2: HikariCP Connection Reuse With Stale Session Context
**What goes wrong:** HikariCP reuses connections across requests. Session context set by request A persists on the connection when request B gets it from the pool.
**Why it happens:** `sp_set_session_context` values persist for the lifetime of the SQL session (connection). HikariCP keeps connections alive.
**Consequences:** Request B executes with request A's identity. Data leakage.
**Prevention:** ALWAYS set session context at the start of each request's database interaction, not just "if not already set." The interceptor must set it unconditionally. Alternatively, call `sp_set_session_context` with `@read_only=0` to allow overwrite.
**Detection:** Integration test with alternating identities on the same connection.

### Pitfall 3: MyBatis Output Parameters Not Returned
**What goes wrong:** Stored procedures with OUT parameters (e.g., `@NewNcrId OUTPUT`) don't return values to Java code.
**Why it happens:** MyBatis requires OUT parameters to be properties on the parameter object. If using primitives or separate `@Param` annotations, the output value has nowhere to go.
**Consequences:** Create/update operations succeed in the database but the Java layer does not receive the generated ID or confirmation value.
**Prevention:** Use a mutable parameter class (not a record) for stored procedures with OUT parameters. After execution, MyBatis updates the property on the param object.
```java
// WRONG: record is immutable, OUT param has nowhere to go
public record NcrCreateParams(int plantId, String title, int ncrId) {}

// RIGHT: mutable class with setter for OUT param
public class NcrCreateParams {
    private int plantId;
    private String title;
    private Integer ncrId;      // OUT -- MyBatis sets this after execution
    private String ncrNumber;   // OUT -- MyBatis sets this after execution
    // getters and setters
}
```
**Detection:** Unit test that verifies OUT parameter values are populated after mapper call.

### Pitfall 4: OpenAPI Contract Drift (Breaking the Contract Chain)
**What goes wrong:** The Spring Boot API produces an OpenAPI spec with different route paths, parameter names, or response shapes than the C# version.
**Why it happens:** springdoc-openapi infers spec from Java annotations. Different annotation conventions (e.g., Jackson's `@JsonProperty` vs System.Text.Json) produce different JSON property names. Different controller method signatures produce different parameter serialization.
**Consequences:** sf-quality-app breaks because its TypeScript types (generated from the OpenAPI snapshot) no longer match the API.
**Prevention:**
1. Use `@JsonProperty` annotations on all DTOs to explicitly control JSON property names
2. Generate the static `api-openapi.publish.json` in CI
3. Add a CI step that diffs the new spec against the C# version's spec -- fail on breaking changes (removed routes, changed response shapes)
4. Use `@Operation`, `@ApiResponse`, `@Schema` annotations from springdoc to match exact response shapes
**Detection:** CI contract validation step. Diff tool that compares OpenAPI specs structurally (not textually).

## Moderate Pitfalls

### Pitfall 5: Resilience4j Aspect Ordering
**What goes wrong:** Default Spring Boot 3.x aspect ordering places @Retry OUTSIDE @CircuitBreaker, so every retry failure counts as a separate circuit breaker failure.
**Prevention:** Explicitly set aspect order in configuration:
```yaml
resilience4j:
  circuitbreaker:
    circuit-breaker-aspect-order: 1
  retry:
    retry-aspect-order: 2
```
This ensures retry completes first, then the final result is evaluated by the circuit breaker.

### Pitfall 6: Azure SQL Connection Timeout Mismatch
**What goes wrong:** HikariCP max-lifetime exceeds Azure SQL's connection timeout, causing connection reset errors.
**Prevention:** Set HikariCP `max-lifetime` to several minutes LESS than Azure SQL's connection timeout (default 30 minutes). Recommended: `max-lifetime=1200000` (20 minutes).
```yaml
spring:
  datasource:
    hikari:
      max-lifetime: 1200000
      connection-timeout: 30000
      idle-timeout: 600000
      maximum-pool-size: 10
      minimum-idle: 2
      keepalive-time: 300000
```

### Pitfall 7: Missing JDBC Driver for MSSQL in Spring Boot
**What goes wrong:** Spring Boot auto-configures DataSource but the MSSQL JDBC driver is not on the classpath, causing startup failure.
**Prevention:** Include `com.microsoft.sqlserver:mssql-jdbc` as a runtime dependency. Spring Boot manages the version via its BOM.

### Pitfall 8: springdoc-openapi-maven-plugin Requires Running Application
**What goes wrong:** The Maven plugin that generates the static OpenAPI JSON file needs to start the application during the integration-test phase. If the database is not available during build, the app fails to start.
**Prevention:** Use a Spring profile for CI builds that stubs the DataSource or uses an in-memory DB. OR use `spring.datasource.hikari.initialization-fail-timeout=-1` to allow the app to start without a database connection. The OpenAPI spec is generated from annotations, not from actual database calls.
```yaml
# application-ci.yml
spring:
  datasource:
    url: jdbc:h2:mem:testdb
    driver-class-name: org.h2.Driver
```
Add H2 as a test-scoped dependency for CI-only use.

### Pitfall 9: Virtual Threads + Synchronized Blocks
**What goes wrong:** Java 21 virtual threads can cause pinning when they encounter `synchronized` blocks, which reduces throughput.
**Prevention:** Avoid `synchronized` in application code. HikariCP and the MSSQL JDBC driver use `synchronized` internally -- monitor for pinning with `-Djdk.tracePinnedThreads=short`. If pinning is observed, disable virtual threads and use platform threads with a larger thread pool instead.

### Pitfall 10: Easy Auth Header Missing in Local Development
**What goes wrong:** The `X-MS-CLIENT-PRINCIPAL` header is only present when deployed to Azure App Service with Easy Auth enabled. Local development has no header.
**Prevention:** Create a development profile that injects a mock identity:
```yaml
# application-dev.yml
app:
  easy-auth:
    mock-enabled: true
    mock-oid: "00000000-0000-0000-0000-000000000001"
    mock-name: "Dev User"
    mock-email: "dev@sfquality.local"
```
The EasyAuthFilter checks this configuration and creates a mock identity when the header is absent.

## Minor Pitfalls

### Pitfall 11: Jackson vs MyBatis Naming Conventions
**What goes wrong:** Java uses camelCase, SQL Server columns use PascalCase. Without explicit mapping, properties are null.
**Prevention:** Enable `mybatis.configuration.map-underscore-to-camel-case=true` and use `<result>` elements in resultMaps for PascalCase columns.

### Pitfall 12: MDC Values Not Cleaned Up
**What goes wrong:** MDC values from one request leak into another request's logs on the same thread.
**Prevention:** Always clean MDC in a `finally` block in the filter. Spring Boot 3.4 structured logging includes MDC automatically, so leaked values corrupt ALL subsequent log lines.

### Pitfall 13: Bucket4j Memory Growth
**What goes wrong:** In-memory rate limit buckets grow unboundedly as new user OIDs are seen.
**Prevention:** Use a ConcurrentHashMap with a cleanup task that removes buckets not accessed in the last 10 minutes, or use Caffeine cache with expireAfterAccess.

### Pitfall 14: springdoc Version Mismatch with Spring Boot 3
**What goes wrong:** Using springdoc-openapi v1.x (for Spring Boot 2.x) with Spring Boot 3.x causes ClassNotFoundException.
**Prevention:** Spring Boot 3.x requires springdoc-openapi v2.x. Specifically `springdoc-openapi-starter-webmvc-ui` (note the `starter` prefix).

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Phase 2: DataSource setup | Pitfall 6 (timeout mismatch), Pitfall 7 (missing driver) | Copy HikariCP config from this research verbatim |
| Phase 2: Session context | Pitfall 1 (RLS bypass), Pitfall 2 (stale context) | Write integration test with alternating identities BEFORE writing any endpoints |
| Phase 2: OpenAPI export | Pitfall 8 (needs running app) | Set up CI profile with H2 database stub |
| Phase 3: NCR endpoints | Pitfall 3 (OUT params), Pitfall 4 (contract drift) | Use mutable param classes for creates; diff OpenAPI spec against C# version |
| Phase 3: NCR endpoints | Pitfall 11 (naming conventions) | Use explicit resultMap XML for all stored procedure results |
| Phase 4: Deployment | Pitfall 10 (no Easy Auth locally) | Dev profile with mock identity must already exist from Phase 2 |
| Phase 4: Virtual threads | Pitfall 9 (pinning) | Enable virtual threads but monitor; have fallback config ready |

## Sources

- [Resilience4j issue #2383](https://github.com/resilience4j/resilience4j/issues/2383) - aspect ordering bug in Spring Boot 3
- [HikariCP best practices](https://github.com/brettwooldridge/HikariCP) - max-lifetime configuration
- [MyBatis OUT parameters](https://dzhg.dev/posts/2020/09/how-to-handle-output-parameter-of-callable-statement-in-mybatis/) - parameter handling
- [Azure Easy Auth identities](https://learn.microsoft.com/en-us/azure/app-service/configure-authentication-user-identities) - header structure
- [springdoc-openapi Maven plugin](https://github.com/springdoc/springdoc-openapi-maven-plugin) - build-time spec generation
- [sp_set_session_context](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-set-session-context-transact-sql) - session context behavior
