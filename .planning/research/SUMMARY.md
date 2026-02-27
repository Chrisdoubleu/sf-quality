# Research Summary: Spring Boot Migration (sf-quality-api)

**Domain:** ASP.NET Core 9.0 / C# / Dapper to Spring Boot 3.x / Java 21 / MyBatis API migration
**Researched:** 2026-02-27
**Overall confidence:** HIGH

## Executive Summary

The Spring Boot 3.x + Java 21 + MyBatis stack is a well-established pattern for thin API layers that call stored procedures. Every cross-cutting concern from the C# implementation has a direct Java equivalent with mature library support. The migration is a language translation, not an architecture change -- the stored-procedure-first, thin-API pattern maps cleanly from Dapper to MyBatis.

Azure App Service has first-class Java SE support. Spring Boot deploys as an executable JAR (not WAR), runs on the embedded Tomcat server, and Azure handles JVM lifecycle. The MSSQL JDBC driver supports Azure SQL with connection-string-based auth, and HikariCP (Spring Boot's default pool) handles connection management. Easy Auth header parsing requires a custom servlet filter -- there is no Spring Boot library for this, but the implementation is straightforward (base64 decode + JSON parse).

MyBatis with `statementType="CALLABLE"` maps directly to Dapper's stored procedure pattern. Each proc call becomes a mapper method with XML configuration for IN/OUT parameters. The key difference: Dapper opens a connection per call; MyBatis manages connections through Spring's transaction infrastructure and HikariCP. Session context (`usp_SetSessionContext`) must be called on each connection before user queries -- this requires a MyBatis interceptor or a custom DataSource wrapper.

springdoc-openapi generates the OpenAPI 3.x spec at runtime and can export a static JSON file via a Maven plugin during the integration-test phase. This directly supports the contract chain validation requirement.

## Key Findings

**Stack:** Spring Boot 3.4.x + Java 21 + MyBatis 3.0.x + HikariCP + springdoc-openapi 2.8.x + Resilience4j + Bucket4j + Logback structured JSON
**Architecture:** Servlet filter chain (Easy Auth -> Correlation ID -> Rate Limit) -> Controller -> Service -> MyBatis Mapper -> Azure SQL stored procedures
**Critical pitfall:** Session context injection -- must call `usp_SetSessionContext` on EVERY user-scoped connection BEFORE any query executes; getting this wrong breaks RLS silently

## Implications for Roadmap

Based on research, the existing Phase 2 (Spring Boot Infrastructure) should be structured as follows:

1. **Project scaffold + build tooling** - Maven project, dependencies, CI pipeline
   - Addresses: SPRING-01, SPRING-14, SPRING-15
   - Low risk, standard patterns

2. **DataSource + MyBatis + Session Context** - HikariCP config, MyBatis mapper setup, session context interceptor
   - Addresses: SPRING-02, SPRING-03, SPRING-04
   - Avoids: Silent RLS bypass (most critical pitfall)
   - This is the hardest part -- get it right before anything else

3. **Easy Auth filter + Security** - X-MS-CLIENT-PRINCIPAL parsing, permission gate
   - Addresses: SPRING-05, SPRING-06
   - Must work before any user-scoped endpoint

4. **Cross-cutting concerns** - Error mapping, pagination, correlation IDs, rate limiting, retry, audit logging
   - Addresses: SPRING-07 through SPRING-13
   - Standard patterns, low risk

5. **OpenAPI + Contract validation** - springdoc setup, static JSON export, CI contract check
   - Addresses: SPRING-14 (partial), contract chain requirement
   - Must produce identical route paths and response shapes

**Phase ordering rationale:**
- DataSource/MyBatis/SessionContext first because every other feature depends on database access working correctly
- Easy Auth second because user identity is needed for session context and permission checks
- Cross-cutting concerns third because they are independent of each other and can be implemented in parallel
- OpenAPI last because it needs controllers to exist to generate the spec

**Research flags for phases:**
- Phase 2 Plan 2 (Session Context): Needs careful implementation -- MyBatis interceptor approach must be validated
- Phase 2 Plan 5 (OpenAPI): springdoc-openapi-maven-plugin starts the app during build -- may need test profile with mock DB
- Phase 3/4 (Endpoint porting): Standard translation work, unlikely to need research

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All libraries verified via official docs, well-established ecosystem |
| Features (cross-cutting) | HIGH | Direct 1:1 mapping from C# equivalents, verified with official sources |
| Architecture | HIGH | Thin API + stored procedure pattern is MyBatis's primary use case |
| MyBatis stored procedures | HIGH | Verified via official MyBatis docs -- CALLABLE statementType is well-documented |
| Session context injection | MEDIUM | Pattern is clear but implementation (interceptor vs DataSource wrapper) needs validation in practice |
| Easy Auth parsing | MEDIUM | No Spring Boot library exists; custom filter required, but pattern is straightforward |
| springdoc static export | HIGH | Maven plugin documented on springdoc.org, runs during integration-test phase |

## Gaps to Address

- Exact mybatis-spring-boot-starter version for Spring Boot 3.4.x (3.0.4 or 3.0.5 likely current -- verify at implementation time)
- Azure App Service startup command specifics for Spring Boot JAR (may need `java -jar /home/site/wwwroot/app.jar` or rely on default)
- Whether MyBatis interceptor or AOP-based approach is cleaner for session context injection -- needs prototyping
- Resilience4j aspect ordering with Spring Boot 3.x -- known issue with default ordering (retry outside circuit breaker)
