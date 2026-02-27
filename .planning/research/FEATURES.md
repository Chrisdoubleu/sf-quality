# Feature Landscape

**Domain:** Spring Boot API migration -- cross-cutting infrastructure concerns
**Researched:** 2026-02-27

## Table Stakes

Features the Spring Boot API MUST have to match the C# implementation. Missing = broken contract chain.

| Feature | Why Expected | Complexity | C# Equivalent |
|---------|--------------|------------|---------------|
| Easy Auth header parsing | Identity extraction for session context and permission checks | Medium | Custom middleware |
| Session context injection | `usp_SetSessionContext(@CallerAzureOid)` on every user-scoped connection -- RLS depends on it | High | Dapper connection wrapper |
| MyBatis stored procedure calls | All data access is via stored procedures -- this IS the data layer | Medium | Dapper `QueryAsync` / `ExecuteAsync` |
| SQL error code mapping | 50400->400, 50401->401, 50404->404, 52xxx->domain-specific | Low | Custom exception filter |
| Cursor-based pagination | `PagedResponse<T>{items, nextCursor}` envelope on all list endpoints | Low | Custom response wrapper |
| Correlation ID propagation | `X-Correlation-Id` header in -> MDC -> SQL -> response header out | Low | Custom middleware |
| Rate limiting | 120 req/60s fixed window per identity | Low | ASP.NET rate limiter |
| Transient SQL retry | 3 retries, exponential backoff + jitter | Low | Polly |
| Audit API call logging | Route/method/status/duration/oid logged on every request | Low | Custom middleware |
| Structured JSON logging | JSON log output with correlation ID, OID, request metadata | Low | Serilog + JSON sink |
| OpenAPI spec generation | springdoc produces identical route paths and response shapes | Medium | Swashbuckle |
| Static OpenAPI JSON export | `api-openapi.publish.json` checked into repo for contract chain | Medium | CI script |
| Permission gate | `security.usp_CheckPermission` on workflow submit routes | Low | Custom attribute/filter |
| CORS configuration | Allow app origin in dev/staging/prod | Low | ASP.NET CORS middleware |
| Health check endpoint | `GET /v1/diagnostics/health` returns 200 anonymously | Low | ASP.NET health checks |
| Azure App Service deployment | JAR deploys to App Service Java SE runtime | Low | dotnet publish |

## Differentiators

Improvements over the C# implementation that should be adopted.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Spring Boot 3.4 structured logging | Built-in JSON logging without external library (Serilog required third-party) | Low | Set `logging.structured.format.console=logstash` and done |
| Actuator metrics endpoint | HikariCP pool metrics, request metrics, JVM metrics out of the box | Low | Just include spring-boot-starter-actuator |
| MyBatis XML mappers | SQL separated from Java code in XML files -- easier to review and modify | Low | Dapper had inline SQL strings |
| Virtual threads (Java 21) | Better throughput for IO-bound stored-procedure calls | Low | `spring.threads.virtual.enabled=true` in application.properties |

## Anti-Features

Features to explicitly NOT build in the Spring Boot migration.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Spring Data JPA / Hibernate | Adds ORM layer, entity management, lazy loading -- all unnecessary for stored-proc API | Use MyBatis with CALLABLE statement type |
| Spring Security OAuth2 | Easy Auth handles auth at the App Service level -- adding Spring Security OAuth2 duplicates this | Parse X-MS-CLIENT-PRINCIPAL header in a simple servlet filter |
| Spring Cloud Gateway | No API gateway needed -- single API, single app service | Embed rate limiting and routing in the app itself |
| GraphQL endpoint | Contract chain requires REST with specific route paths | Maintain REST controllers matching existing OpenAPI contract |
| Flyway / Liquibase | Database migrations are managed in sf-quality-db repo | Do not manage DB schema from the API project |
| WebFlux / Reactive | Stored procedure calls are blocking by nature, reactive adds complexity for no benefit | Use Spring Web MVC (servlet-based) with virtual threads for concurrency |
| Spring Profiles for multi-tenancy | Single-tenant system by design | Use profiles only for environment config (dev/staging/prod) |

## Feature Dependencies

```
Easy Auth Filter -> Session Context Injection (needs OID from Easy Auth)
Session Context Injection -> All user-scoped MyBatis mapper calls (RLS depends on session context)
MyBatis Configuration -> Stored Procedure Mappers (mapper infrastructure must exist first)
HikariCP Configuration -> MyBatis Configuration (needs DataSource)
Controller layer -> OpenAPI spec generation (springdoc reads controller annotations)
OpenAPI spec generation -> Static JSON export (Maven plugin fetches from running app)
Resilience4j Configuration -> Retry on stored procedure calls (retry wraps service layer)
Bucket4j Configuration -> Rate limit filter (filter intercepts before controller)
```

## MVP Recommendation (Phase 2 Infrastructure)

Build in this order:

1. Maven project scaffold with all dependencies
2. HikariCP + Azure SQL DataSource configuration
3. MyBatis auto-configuration + first test mapper (health check)
4. Session context MyBatis interceptor
5. Easy Auth servlet filter
6. Error code mapping exception handler
7. Correlation ID filter + MDC
8. Structured JSON logging
9. Rate limiting filter (Bucket4j)
10. Resilience4j retry configuration
11. Audit logging filter
12. Pagination response wrapper
13. springdoc-openapi + Swagger UI
14. Static OpenAPI JSON export
15. GitHub Actions CI pipeline
16. Health check endpoint

Defer to Phase 3+: Actual domain endpoint controllers and their mapper XML files.

## Sources

- [PROJECT.md](../../.planning/PROJECT.md) - cross-cutting infrastructure requirements
- [ROADMAP.md](../../.planning/ROADMAP.md) - Phase 2 success criteria
