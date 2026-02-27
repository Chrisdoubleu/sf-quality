# Architecture Patterns

**Domain:** Spring Boot thin API calling Azure SQL stored procedures
**Researched:** 2026-02-27

## Recommended Architecture

```
HTTP Request
    |
    v
[Servlet Filter Chain]
    |-- CorsFilter (Spring built-in)
    |-- CorrelationIdFilter (custom: extract/generate X-Correlation-Id -> MDC)
    |-- RateLimitFilter (custom: Bucket4j, keyed by Azure OID)
    |-- EasyAuthFilter (custom: parse X-MS-CLIENT-PRINCIPAL -> SecurityContext)
    |-- AuditLoggingFilter (custom: log route/method/status/duration/oid)
    |
    v
[Spring MVC DispatcherServlet]
    |
    v
[Controller] -- @RestController, route mapping, request/response DTOs
    |
    v
[Service] -- @Service, @Retry (Resilience4j), business orchestration
    |
    v
[MyBatis Mapper] -- @Mapper interface + XML, statementType=CALLABLE
    |
    v
[SessionContextInterceptor] -- MyBatis plugin, calls usp_SetSessionContext before each query
    |
    v
[HikariCP] -- Connection pool
    |
    v
[Azure SQL] -- Stored procedures, RLS enforced
```

### Component Boundaries

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| Servlet Filters | Cross-cutting: CORS, correlation ID, rate limit, auth, audit | Spring MVC DispatcherServlet |
| Controllers | HTTP routing, request validation, response shaping | Services |
| Services | Business orchestration, retry policy application | MyBatis Mappers |
| MyBatis Mappers | SQL execution via stored procedures | HikariCP (via SqlSession) |
| SessionContextInterceptor | Inject caller OID into SQL session before queries | MyBatis SqlSession |
| DTOs | Request/response data shapes | Controllers, Services, Mappers |
| Exception Handler | SQL error code -> HTTP status translation | Controllers (via @ControllerAdvice) |

### Data Flow

1. Request arrives with `X-MS-CLIENT-PRINCIPAL` and optional `X-Correlation-Id` headers
2. `CorrelationIdFilter` extracts or generates correlation ID, puts in MDC and response header
3. `RateLimitFilter` checks Bucket4j token for the caller's Azure OID
4. `EasyAuthFilter` base64-decodes the client principal header, extracts claims, stores in thread-local/SecurityContext
5. `AuditLoggingFilter` wraps the request to capture timing and status
6. Controller receives request, validates input, delegates to service
7. Service method (optionally wrapped by `@Retry`) calls MyBatis mapper
8. MyBatis opens a connection from HikariCP
9. `SessionContextInterceptor` fires before the SQL statement, calling `usp_SetSessionContext` with the caller's OID
10. MyBatis executes the stored procedure via CALLABLE statement
11. Result maps to DTO via MyBatis resultMap or resultType
12. Controller wraps in response envelope (or `PagedResponse` for lists)
13. `@ControllerAdvice` catches SQL exceptions, maps error codes to HTTP status
14. Response returns through filter chain (audit filter logs duration)

## Patterns to Follow

### Pattern 1: Easy Auth Filter

**What:** Servlet filter that parses the Azure App Service Easy Auth header
**When:** Every authenticated request
**Confidence:** MEDIUM (no Spring Boot library; custom implementation required)

```java
@Component
@Order(Ordered.HIGHEST_PRECEDENCE + 30)
public class EasyAuthFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                     HttpServletResponse response,
                                     FilterChain filterChain) throws ServletException, IOException {
        String principalHeader = request.getHeader("X-MS-CLIENT-PRINCIPAL");

        if (principalHeader != null && !principalHeader.isBlank()) {
            try {
                String decoded = new String(Base64.getDecoder().decode(principalHeader));
                // JSON structure: { "auth_typ": "aad", "claims": [{"typ": "...", "val": "..."}], ... }
                ClientPrincipal principal = objectMapper.readValue(decoded, ClientPrincipal.class);

                String oid = principal.findClaimValue(
                    "http://schemas.microsoft.com/identity/claims/objectidentifier");
                String name = principal.findClaimValue("name");
                String email = principal.findClaimValue(
                    "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress");

                // Store in thread-local for downstream use
                EasyAuthContext.set(new EasyAuthIdentity(oid, name, email, principal.getClaims()));
                MDC.put("callerOid", oid);
            } catch (Exception e) {
                logger.warn("Failed to parse X-MS-CLIENT-PRINCIPAL header", e);
            }
        }

        try {
            filterChain.doFilter(request, response);
        } finally {
            EasyAuthContext.clear();
            MDC.remove("callerOid");
        }
    }

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        // Allow anonymous access to health check and OpenAPI docs
        String path = request.getRequestURI();
        return path.startsWith("/v1/diagnostics/health")
            || path.startsWith("/v3/api-docs")
            || path.startsWith("/swagger-ui");
    }
}
```

**ClientPrincipal DTO:**
```java
public record ClientPrincipal(
    @JsonProperty("auth_typ") String authType,
    @JsonProperty("name_typ") String nameType,
    @JsonProperty("role_typ") String roleType,
    List<ClientClaim> claims
) {
    public String findClaimValue(String type) {
        return claims.stream()
            .filter(c -> type.equals(c.typ()))
            .map(ClientClaim::val)
            .findFirst()
            .orElse(null);
    }
}

public record ClientClaim(String typ, String val) {}
```

### Pattern 2: Session Context MyBatis Interceptor

**What:** MyBatis plugin that calls `usp_SetSessionContext` before each SQL statement
**When:** Every user-scoped query (not health checks or anonymous endpoints)
**Confidence:** MEDIUM (pattern is clear, needs validation that interceptor fires on correct connection)

```java
@Intercepts({
    @Signature(type = Executor.class, method = "update",
               args = {MappedStatement.class, Object.class}),
    @Signature(type = Executor.class, method = "query",
               args = {MappedStatement.class, Object.class, RowBounds.class, ResultHandler.class})
})
@Component
public class SessionContextInterceptor implements Interceptor {

    @Override
    public Object intercept(Invocation invocation) throws Throwable {
        EasyAuthIdentity identity = EasyAuthContext.get();
        if (identity != null && identity.oid() != null) {
            Executor executor = (Executor) invocation.getTarget();
            Connection connection = executor.getTransaction().getConnection();

            try (CallableStatement cs = connection.prepareCall("{call dbo.usp_SetSessionContext(?)}")) {
                cs.setString(1, identity.oid());
                cs.execute();
            }
        }
        return invocation.proceed();
    }

    @Override
    public Object plugin(Object target) {
        return Plugin.wrap(target, this);
    }
}
```

**Important:** This interceptor fires on EVERY query. For performance, consider caching whether session context has already been set on the current connection within the current request. One approach: use a request-scoped flag.

### Pattern 3: MyBatis Stored Procedure Mapper (XML)

**What:** XML mapper for calling Azure SQL stored procedures with IN/OUT parameters
**When:** Every data access call
**Confidence:** HIGH (verified via official MyBatis docs)

**Mapper interface:**
```java
@Mapper
public interface NcrMapper {

    NcrDetailDto getNcrById(@Param("ncrId") int ncrId);

    PagedResult<NcrSummaryDto> getNcrQueue(
        @Param("plantId") int plantId,
        @Param("statusFilter") String statusFilter,
        @Param("cursor") String cursor,
        @Param("pageSize") int pageSize
    );

    @Options(statementType = StatementType.CALLABLE)
    void createNcr(NcrCreateParams params);
}
```

**XML mapper (NcrMapper.xml):**
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
    "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.sfquality.api.mapper.NcrMapper">

    <!-- Simple stored procedure call returning a single result -->
    <select id="getNcrById" statementType="CALLABLE" resultType="NcrDetailDto">
        {call quality.usp_GetNcrById(
            #{ncrId, mode=IN, jdbcType=INTEGER}
        )}
    </select>

    <!-- Stored procedure with cursor-based pagination -->
    <select id="getNcrQueue" statementType="CALLABLE" resultMap="pagedNcrSummary">
        {call quality.usp_GetNcrQueue(
            #{plantId, mode=IN, jdbcType=INTEGER},
            #{statusFilter, mode=IN, jdbcType=VARCHAR},
            #{cursor, mode=IN, jdbcType=VARCHAR},
            #{pageSize, mode=IN, jdbcType=INTEGER}
        )}
    </select>

    <!-- Stored procedure with output parameter -->
    <select id="createNcr" statementType="CALLABLE" parameterType="NcrCreateParams">
        {call quality.usp_CreateNcr(
            #{plantId, mode=IN, jdbcType=INTEGER},
            #{title, mode=IN, jdbcType=NVARCHAR},
            #{description, mode=IN, jdbcType=NVARCHAR},
            #{ncrId, mode=OUT, jdbcType=INTEGER},
            #{ncrNumber, mode=OUT, jdbcType=VARCHAR}
        )}
    </select>

    <resultMap id="pagedNcrSummary" type="NcrSummaryDto">
        <result column="NcrId" property="ncrId"/>
        <result column="NcrNumber" property="ncrNumber"/>
        <result column="Title" property="title"/>
        <result column="Status" property="status"/>
        <!-- ... -->
    </resultMap>

</mapper>
```

**application.yml MyBatis config:**
```yaml
mybatis:
  mapper-locations: classpath:mapper/**/*.xml
  type-aliases-package: com.sfquality.api.dto
  configuration:
    map-underscore-to-camel-case: true
    call-setters-on-nulls: true
```

### Pattern 4: SQL Error Code Exception Handler

**What:** @ControllerAdvice that maps SQL error codes to HTTP status codes
**When:** Any stored procedure raises an error with a custom error code
**Confidence:** HIGH (standard Spring pattern)

```java
@ControllerAdvice
public class SqlErrorCodeExceptionHandler {

    private static final Map<Integer, HttpStatus> ERROR_CODE_MAP = Map.of(
        50400, HttpStatus.BAD_REQUEST,
        50401, HttpStatus.UNAUTHORIZED,
        50403, HttpStatus.FORBIDDEN,
        50404, HttpStatus.NOT_FOUND,
        50409, HttpStatus.CONFLICT,
        50422, HttpStatus.UNPROCESSABLE_ENTITY
    );

    @ExceptionHandler(PersistenceException.class)
    public ResponseEntity<ErrorResponse> handlePersistenceException(PersistenceException ex) {
        Throwable cause = ex.getCause();
        if (cause instanceof SQLException sqlEx) {
            int errorCode = sqlEx.getErrorNumber(); // MSSQL-specific
            HttpStatus status = ERROR_CODE_MAP.getOrDefault(errorCode, HttpStatus.INTERNAL_SERVER_ERROR);

            // For 52xxx domain-specific errors, extract the message
            if (errorCode >= 52000 && errorCode < 53000) {
                return ResponseEntity.status(HttpStatus.UNPROCESSABLE_ENTITY)
                    .body(new ErrorResponse(errorCode, sqlEx.getMessage()));
            }

            return ResponseEntity.status(status)
                .body(new ErrorResponse(errorCode, sqlEx.getMessage()));
        }
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(new ErrorResponse(0, "Internal server error"));
    }
}
```

### Pattern 5: Correlation ID Filter

**What:** Servlet filter that propagates correlation ID via MDC
**When:** Every request
**Confidence:** HIGH (well-documented Spring pattern)

```java
@Component
@Order(Ordered.HIGHEST_PRECEDENCE + 10)
public class CorrelationIdFilter extends OncePerRequestFilter {

    private static final String HEADER = "X-Correlation-Id";

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                     HttpServletResponse response,
                                     FilterChain filterChain) throws ServletException, IOException {
        String correlationId = request.getHeader(HEADER);
        if (correlationId == null || correlationId.isBlank()) {
            correlationId = UUID.randomUUID().toString();
        }

        MDC.put("correlationId", correlationId);
        response.setHeader(HEADER, correlationId);

        try {
            filterChain.doFilter(request, response);
        } finally {
            MDC.remove("correlationId");
        }
    }
}
```

### Pattern 6: Cursor-Based Pagination Response

**What:** Generic response envelope for paginated endpoints
**When:** All list endpoints
**Confidence:** HIGH

```java
public record PagedResponse<T>(
    List<T> items,
    @JsonInclude(JsonInclude.Include.NON_NULL)
    String nextCursor
) {
    public static <T> PagedResponse<T> of(List<T> items, String nextCursor) {
        return new PagedResponse<>(items, nextCursor);
    }

    public static <T> PagedResponse<T> empty() {
        return new PagedResponse<>(List.of(), null);
    }
}
```

### Pattern 7: Rate Limiting Filter (Bucket4j)

**What:** Per-identity rate limiting using token bucket algorithm
**When:** Every authenticated request
**Confidence:** HIGH

```java
@Component
@Order(Ordered.HIGHEST_PRECEDENCE + 20)
public class RateLimitFilter extends OncePerRequestFilter {

    private final Map<String, Bucket> buckets = new ConcurrentHashMap<>();

    private Bucket createBucket() {
        return Bucket.builder()
            .addLimit(BandwidthBuilder.builder()
                .capacity(120)
                .refillGreedy(120, Duration.ofSeconds(60))
                .build())
            .build();
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                     HttpServletResponse response,
                                     FilterChain filterChain) throws ServletException, IOException {
        EasyAuthIdentity identity = EasyAuthContext.get();
        if (identity != null && identity.oid() != null) {
            Bucket bucket = buckets.computeIfAbsent(identity.oid(), k -> createBucket());
            ConsumptionProbe probe = bucket.tryConsumeAndReturnRemaining(1);

            if (!probe.isConsumed()) {
                response.setStatus(HttpStatus.TOO_MANY_REQUESTS.value());
                response.setHeader("Retry-After",
                    String.valueOf(TimeUnit.NANOSECONDS.toSeconds(probe.getNanosToWaitForRefill())));
                return;
            }

            response.setHeader("X-Rate-Limit-Remaining", String.valueOf(probe.getRemainingTokens()));
        }

        filterChain.doFilter(request, response);
    }

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        String path = request.getRequestURI();
        return path.startsWith("/v1/diagnostics/health")
            || path.startsWith("/v3/api-docs")
            || path.startsWith("/swagger-ui");
    }
}
```

### Pattern 8: Resilience4j Retry Configuration

**What:** Transient SQL error retry with exponential backoff
**When:** Service layer methods calling stored procedures
**Confidence:** HIGH

```yaml
# application.yml
resilience4j:
  retry:
    instances:
      sqlRetry:
        max-attempts: 3
        wait-duration: 500ms
        enable-exponential-backoff: true
        exponential-backoff-multiplier: 2
        exponential-max-wait-duration: 5s
        retry-exceptions:
          - java.sql.SQLTransientConnectionException
          - java.sql.SQLTimeoutException
          - com.microsoft.sqlserver.jdbc.SQLServerException
        ignore-exceptions:
          - org.apache.ibatis.exceptions.PersistenceException
  circuitbreaker:
    instances:
      sqlCircuitBreaker:
        register-health-indicator: true
        sliding-window-size: 20
        failure-rate-threshold: 50
        wait-duration-in-open-state: 10s
        permitted-number-of-calls-in-half-open-state: 3
```

**Usage in service:**
```java
@Service
public class NcrService {

    private final NcrMapper ncrMapper;

    @Retry(name = "sqlRetry")
    public NcrDetailDto getNcrById(int ncrId) {
        return ncrMapper.getNcrById(ncrId);
    }
}
```

**IMPORTANT:** Resilience4j annotation execution order in Spring Boot 3.x defaults to Retry OUTSIDE CircuitBreaker, which inflates failure counts. Set explicit aspect order:
```yaml
resilience4j:
  circuitbreaker:
    circuit-breaker-aspect-order: 1
  retry:
    retry-aspect-order: 2
```
This ensures Retry runs first (inside), then CircuitBreaker evaluates the final result.

### Pattern 9: Structured JSON Logging (Spring Boot 3.4 built-in)

**What:** JSON-structured log output with MDC values auto-included
**When:** All environments (dev can use console, prod uses JSON)
**Confidence:** HIGH (verified via official Spring Boot docs)

```yaml
# application-prod.yml
logging:
  structured:
    format:
      console: logstash
    json:
      add:
        service: sf-quality-api
        environment: ${SPRING_PROFILES_ACTIVE:unknown}
```

MDC values (`correlationId`, `callerOid`) are automatically included in every JSON log line.
No logstash-logback-encoder dependency needed -- Spring Boot 3.4 handles this natively.

## Anti-Patterns to Avoid

### Anti-Pattern 1: Using Spring Data JPA alongside MyBatis
**What:** Adding JPA entities "just for simple queries"
**Why bad:** Two data access strategies = two transaction managers, confusion about which layer owns what, potential connection pool contention
**Instead:** Use MyBatis for ALL data access. Even simple lookups go through mapper XML.

### Anti-Pattern 2: Session Context in Controller or Service Layer
**What:** Calling `usp_SetSessionContext` manually before each mapper call
**Why bad:** Easy to forget, leads to RLS bypass bugs, verbose boilerplate
**Instead:** MyBatis Interceptor that fires automatically on every Executor.query/update

### Anti-Pattern 3: Catching Specific SQL Error Codes in Controllers
**What:** try/catch around mapper calls with error-code-specific handling
**Why bad:** Duplicated across every controller, inconsistent error responses
**Instead:** `@ControllerAdvice` global exception handler that maps error codes centrally

### Anti-Pattern 4: Reactive WebFlux for Stored Procedure Calls
**What:** Using WebFlux because "it's modern"
**Why bad:** Stored procedure calls are blocking JDBC operations. Wrapping blocking calls in Mono.fromCallable is worse than using servlet + virtual threads.
**Instead:** Spring Web MVC with `spring.threads.virtual.enabled=true` for Java 21 virtual threads

### Anti-Pattern 5: Connection-Per-Request Without Pooling
**What:** Creating new JDBC connections for each request
**Why bad:** Azure SQL has connection limits, creating connections is expensive
**Instead:** HikariCP manages the pool. Spring Boot auto-configures it. Configure max-pool-size for Azure App Service tier.

## Scalability Considerations

| Concern | At current load | At 10x load | At 100x load |
|---------|----------------|-------------|-------------|
| Connection pool | max-pool-size=10 sufficient | Increase to 20, monitor wait times | Multiple App Service instances behind load balancer |
| Rate limiting | In-memory Bucket4j per instance | Still fine -- each instance has own rate limit | Need Redis-backed distributed rate limiting |
| Session context | Interceptor per query, negligible overhead | Consider caching per connection | Same -- still negligible vs proc execution time |
| Logging | Console JSON to App Service log stream | Same, increase log level to WARN for noisy loggers | Azure Monitor integration, reduce log volume |

## Sources

- [MyBatis Mapper XML docs](https://mybatis.org/mybatis-3/sqlmap-xml.html) - CALLABLE statementType, parameter modes
- [MyBatis Spring Boot Starter](https://mybatis.org/spring-boot-starter/mybatis-spring-boot-autoconfigure/) - auto-configuration
- [Spring Boot logging](https://docs.spring.io/spring-boot/reference/features/logging.html) - structured logging 3.4
- [Azure App Service Easy Auth](https://learn.microsoft.com/en-us/azure/app-service/configure-authentication-user-identities) - X-MS-CLIENT-PRINCIPAL structure
- [Resilience4j Spring Boot 3](https://resilience4j.readme.io/docs/getting-started-3) - retry/circuit breaker config
- [Bucket4j](https://github.com/bucket4j/bucket4j) - token bucket rate limiting
- [HikariCP](https://github.com/brettwooldridge/HikariCP) - connection pool configuration
