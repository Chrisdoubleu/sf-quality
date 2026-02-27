# Spring Boot Migration Research: Practical Patterns and Code Snippets

**Project:** sf-quality-api (ASP.NET Core 9.0 / Dapper -> Spring Boot 3.x / Java 21 / MyBatis)
**Researched:** 2026-02-27
**Confidence:** HIGH -- all core patterns verified against official documentation

---

## 1. Spring Boot 3.x + Java 21 on Azure App Service

### Deployment: Executable JAR (not WAR)

Deploy as a **Java SE executable JAR**. Azure App Service runs it with the embedded Tomcat server.

- Azure App Service -> Runtime stack: **Java 21**, **Java SE**
- The JAR is uploaded to `/home/site/wwwroot/app.jar` -- Azure auto-renames the artifact
- No Tomcat WAR deployment needed. Spring Boot's embedded server handles everything.

**Azure deployment via Maven plugin:**
```xml
<plugin>
    <groupId>com.microsoft.azure</groupId>
    <artifactId>azure-webapp-maven-plugin</artifactId>
    <version>2.11.0</version>
    <configuration>
        <schemaVersion>v2</schemaVersion>
        <resourceGroup>sf-quality-rg</resourceGroup>
        <appName>sf-quality-api</appName>
        <pricingTier>B1</pricingTier>
        <region>centralus</region>
        <runtime>
            <os>Linux</os>
            <javaVersion>Java 21</javaVersion>
            <webContainer>Java SE</webContainer>
        </runtime>
        <deployment>
            <resources>
                <resource>
                    <directory>${project.basedir}/target</directory>
                    <includes>
                        <include>*.jar</include>
                    </includes>
                </resource>
            </resources>
        </deployment>
    </configuration>
</plugin>
```

**Startup command** (configure in Azure Portal -> Configuration -> General Settings):
```
java -jar /home/site/wwwroot/app.jar --server.port=80
```
Or let Azure detect it automatically -- the default behavior for Java SE apps is to run `app.jar`.

### JVM Configuration

Set via Azure App Service Application Settings:
```
JAVA_OPTS=-Xms512m -Xmx1024m -Dspring.profiles.active=prod
```

### Azure SQL Connection String

```yaml
# application-prod.yml
spring:
  datasource:
    url: jdbc:sqlserver://${AZURE_SQL_SERVER}.database.windows.net:1433;database=${AZURE_SQL_DATABASE};encrypt=true;trustServerCertificate=false;loginTimeout=30;
    username: ${AZURE_SQL_USER}
    password: ${AZURE_SQL_PASSWORD}
    driver-class-name: com.microsoft.sqlserver.jdbc.SQLServerDriver
```

**Gotcha:** Azure SQL enforces TLS. The JDBC URL must include `encrypt=true`. The `trustServerCertificate=false` ensures proper certificate validation.

---

## 2. MyBatis + Azure SQL Stored Procedures

### Maven Dependencies

```xml
<dependency>
    <groupId>org.mybatis.spring.boot</groupId>
    <artifactId>mybatis-spring-boot-starter</artifactId>
    <version>3.0.4</version>
</dependency>
<dependency>
    <groupId>com.microsoft.sqlserver</groupId>
    <artifactId>mssql-jdbc</artifactId>
    <scope>runtime</scope>
</dependency>
```

### MyBatis Configuration

```yaml
# application.yml
mybatis:
  mapper-locations: classpath:mapper/**/*.xml
  type-aliases-package: com.sfquality.api.dto
  configuration:
    map-underscore-to-camel-case: true
    call-setters-on-nulls: true
    default-statement-timeout: 30
```

### Calling Stored Procedures: XML Mapper Approach

Use XML mappers (not annotations) for stored procedures. XML provides clearer parameter mode declarations and resultMap definitions.

**Mapper Interface (Java):**
```java
package com.sfquality.api.mapper;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface NcrMapper {

    // Simple read -- returns single DTO
    NcrDetailDto getNcrById(@Param("ncrId") int ncrId);

    // Paginated list -- returns list, cursor handled in service layer
    List<NcrSummaryDto> getNcrQueue(@Param("params") NcrQueueParams params);

    // Create with OUT parameters -- uses mutable param object
    void createNcr(NcrCreateParams params);

    // Simple execute -- no result set
    void updateNcrStatus(NcrStatusParams params);
}
```

**Mapper XML (src/main/resources/mapper/NcrMapper.xml):**
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
    "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.sfquality.api.mapper.NcrMapper">

    <!-- ============================================================ -->
    <!-- Pattern A: Simple stored proc returning a single result set  -->
    <!-- Equivalent to: Dapper.QueryFirstOrDefaultAsync<NcrDetailDto> -->
    <!-- ============================================================ -->
    <select id="getNcrById" statementType="CALLABLE"
            resultMap="ncrDetailResultMap">
        {call quality.usp_GetNcrById(
            #{ncrId, mode=IN, jdbcType=INTEGER}
        )}
    </select>

    <resultMap id="ncrDetailResultMap" type="com.sfquality.api.dto.NcrDetailDto">
        <id     column="NcrId"          property="ncrId"/>
        <result column="NcrNumber"      property="ncrNumber"/>
        <result column="PlantId"        property="plantId"/>
        <result column="Title"          property="title"/>
        <result column="Description"    property="description"/>
        <result column="Status"         property="status"/>
        <result column="Severity"       property="severity"/>
        <result column="CreatedBy"      property="createdBy"/>
        <result column="CreatedDate"    property="createdDate"/>
        <result column="ModifiedDate"   property="modifiedDate"/>
    </resultMap>

    <!-- ============================================================ -->
    <!-- Pattern B: Paginated list via stored proc                    -->
    <!-- Equivalent to: Dapper.QueryAsync<NcrSummaryDto>              -->
    <!-- The stored proc returns rows + a nextCursor value            -->
    <!-- ============================================================ -->
    <select id="getNcrQueue" statementType="CALLABLE"
            resultMap="ncrSummaryResultMap">
        {call quality.usp_GetNcrQueue(
            #{params.plantId,      mode=IN, jdbcType=INTEGER},
            #{params.statusFilter, mode=IN, jdbcType=VARCHAR},
            #{params.cursor,       mode=IN, jdbcType=VARCHAR},
            #{params.pageSize,     mode=IN, jdbcType=INTEGER}
        )}
    </select>

    <resultMap id="ncrSummaryResultMap" type="com.sfquality.api.dto.NcrSummaryDto">
        <id     column="NcrId"        property="ncrId"/>
        <result column="NcrNumber"    property="ncrNumber"/>
        <result column="Title"        property="title"/>
        <result column="Status"       property="status"/>
        <result column="PlantName"    property="plantName"/>
        <result column="CreatedDate"  property="createdDate"/>
    </resultMap>

    <!-- ============================================================ -->
    <!-- Pattern C: Create with OUTPUT parameters                     -->
    <!-- Equivalent to: Dapper.QueryFirstAsync with OUTPUT params     -->
    <!-- CRITICAL: param class MUST be mutable (not a record)         -->
    <!--   MyBatis sets OUT values on the param object after exec     -->
    <!-- ============================================================ -->
    <select id="createNcr" statementType="CALLABLE"
            parameterType="com.sfquality.api.dto.NcrCreateParams">
        {call quality.usp_CreateNcr(
            #{plantId,     mode=IN,  jdbcType=INTEGER},
            #{title,       mode=IN,  jdbcType=NVARCHAR},
            #{description, mode=IN,  jdbcType=NVARCHAR},
            #{severityId,  mode=IN,  jdbcType=INTEGER},
            #{ncrId,       mode=OUT, jdbcType=INTEGER},
            #{ncrNumber,   mode=OUT, jdbcType=VARCHAR}
        )}
    </select>

    <!-- ============================================================ -->
    <!-- Pattern D: Execute-only (no result set)                      -->
    <!-- Equivalent to: Dapper.ExecuteAsync                           -->
    <!-- ============================================================ -->
    <update id="updateNcrStatus" statementType="CALLABLE"
            parameterType="com.sfquality.api.dto.NcrStatusParams">
        {call quality.usp_UpdateNcrStatus(
            #{ncrId,    mode=IN, jdbcType=INTEGER},
            #{statusId, mode=IN, jdbcType=INTEGER}
        )}
    </update>

</mapper>
```

**Mutable param class for OUT parameters:**
```java
// MUST be a class with setters, NOT a record (records are immutable)
public class NcrCreateParams {
    // IN parameters
    private Integer plantId;
    private String title;
    private String description;
    private Integer severityId;

    // OUT parameters -- MyBatis populates these after execution
    private Integer ncrId;
    private String ncrNumber;

    // Getters and setters for all fields
    public Integer getNcrId() { return ncrId; }
    public void setNcrId(Integer ncrId) { this.ncrId = ncrId; }
    public String getNcrNumber() { return ncrNumber; }
    public void setNcrNumber(String ncrNumber) { this.ncrNumber = ncrNumber; }
    // ... remaining getters/setters
}
```

**Service layer usage:**
```java
@Service
public class NcrService {
    private final NcrMapper ncrMapper;

    public NcrCreateResult createNcr(int plantId, String title, String description, int severityId) {
        NcrCreateParams params = new NcrCreateParams();
        params.setPlantId(plantId);
        params.setTitle(title);
        params.setDescription(description);
        params.setSeverityId(severityId);

        ncrMapper.createNcr(params);  // OUT params populated after this call

        return new NcrCreateResult(params.getNcrId(), params.getNcrNumber());
    }
}
```

### Connection Pooling: HikariCP for Azure SQL

```yaml
# application.yml
spring:
  datasource:
    hikari:
      pool-name: sf-quality-pool
      maximum-pool-size: 10       # Keep under 10 per App Service instance
      minimum-idle: 2
      idle-timeout: 600000        # 10 minutes
      max-lifetime: 1200000       # 20 minutes (MUST be less than Azure SQL's 30-min timeout)
      connection-timeout: 30000   # 30 seconds
      keepalive-time: 300000      # 5 minutes -- validates idle connections
      connection-test-query: SELECT 1
```

**Why these values:**
- `maximum-pool-size=10`: Azure App Service B1/S1 tier. Cloud best practice: keep pool small per instance.
- `max-lifetime=1200000`: Azure SQL kills idle connections at ~30 minutes. Set 10 minutes less to avoid resets.
- `keepalive-time=300000`: Periodically validates connections before they go stale.

---

## 3. Easy Auth Integration with Spring Boot

### The Header: X-MS-CLIENT-PRINCIPAL

Azure App Service Easy Auth injects this header on every authenticated request. It is a **Base64-encoded JSON** string.

**Decoded structure:**
```json
{
  "auth_typ": "aad",
  "name_typ": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name",
  "role_typ": "http://schemas.microsoft.com/ws/2008/06/identity/claims/role",
  "claims": [
    {
      "typ": "http://schemas.microsoft.com/identity/claims/objectidentifier",
      "val": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    },
    {
      "typ": "name",
      "val": "John Doe"
    },
    {
      "typ": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
      "val": "john.doe@company.com"
    },
    {
      "typ": "http://schemas.microsoft.com/ws/2008/06/identity/claims/role",
      "val": "QualityEngineer"
    }
  ]
}
```

### Servlet Filter Implementation

```java
package com.sfquality.api.security;

import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.*;
import jakarta.servlet.http.*;
import org.slf4j.MDC;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import java.util.Base64;

@Component
@Order(Ordered.HIGHEST_PRECEDENCE + 30)  // After CorrelationId (+10), after RateLimit (+20)
public class EasyAuthFilter extends OncePerRequestFilter {

    private static final String HEADER_CLIENT_PRINCIPAL = "X-MS-CLIENT-PRINCIPAL";
    private static final String HEADER_PRINCIPAL_NAME = "X-MS-CLIENT-PRINCIPAL-NAME";
    private static final String HEADER_PRINCIPAL_ID = "X-MS-CLIENT-PRINCIPAL-ID";
    private static final String CLAIM_OID =
        "http://schemas.microsoft.com/identity/claims/objectidentifier";
    private static final String CLAIM_EMAIL =
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress";

    private final ObjectMapper objectMapper;
    private final EasyAuthProperties properties;

    public EasyAuthFilter(ObjectMapper objectMapper, EasyAuthProperties properties) {
        this.objectMapper = objectMapper;
        this.properties = properties;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                     HttpServletResponse response,
                                     FilterChain filterChain)
            throws ServletException, java.io.IOException {

        EasyAuthIdentity identity = null;

        String principalHeader = request.getHeader(HEADER_CLIENT_PRINCIPAL);
        if (principalHeader != null && !principalHeader.isBlank()) {
            identity = parseClientPrincipal(principalHeader);
        } else if (properties.isMockEnabled()) {
            // Dev mode: use mock identity when no Easy Auth header present
            identity = new EasyAuthIdentity(
                properties.getMockOid(),
                properties.getMockName(),
                properties.getMockEmail()
            );
        }

        if (identity != null) {
            EasyAuthContext.set(identity);
            MDC.put("callerOid", identity.oid());
            MDC.put("callerName", identity.name());
        }

        try {
            filterChain.doFilter(request, response);
        } finally {
            EasyAuthContext.clear();
            MDC.remove("callerOid");
            MDC.remove("callerName");
        }
    }

    private EasyAuthIdentity parseClientPrincipal(String base64Header) {
        try {
            byte[] decoded = Base64.getDecoder().decode(base64Header);
            ClientPrincipal principal = objectMapper.readValue(decoded, ClientPrincipal.class);

            String oid = principal.findClaimValue(CLAIM_OID);
            String name = principal.findClaimValue("name");
            String email = principal.findClaimValue(CLAIM_EMAIL);

            if (oid == null) {
                logger.warn("X-MS-CLIENT-PRINCIPAL present but no OID claim found");
                return null;
            }

            return new EasyAuthIdentity(oid, name, email);
        } catch (Exception e) {
            logger.warn("Failed to parse X-MS-CLIENT-PRINCIPAL: {}", e.getMessage());
            return null;
        }
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

**Thread-local context holder:**
```java
public final class EasyAuthContext {
    private static final ThreadLocal<EasyAuthIdentity> HOLDER = new ThreadLocal<>();

    public static void set(EasyAuthIdentity identity) { HOLDER.set(identity); }
    public static EasyAuthIdentity get() { return HOLDER.get(); }
    public static void clear() { HOLDER.remove(); }

    private EasyAuthContext() {}
}

public record EasyAuthIdentity(String oid, String name, String email) {}
```

**Configuration properties:**
```java
@ConfigurationProperties(prefix = "app.easy-auth")
public class EasyAuthProperties {
    private boolean mockEnabled = false;
    private String mockOid;
    private String mockName;
    private String mockEmail;
    // getters, setters
}
```

```yaml
# application-dev.yml
app:
  easy-auth:
    mock-enabled: true
    mock-oid: "00000000-0000-0000-0000-000000000001"
    mock-name: "Dev User"
    mock-email: "dev@sfquality.local"

# application-prod.yml
app:
  easy-auth:
    mock-enabled: false
```

### Session Context: Calling usp_SetSessionContext

**MyBatis Interceptor (fires before every query/update):**
```java
package com.sfquality.api.mybatis;

import com.sfquality.api.security.EasyAuthContext;
import com.sfquality.api.security.EasyAuthIdentity;
import org.apache.ibatis.executor.Executor;
import org.apache.ibatis.mapping.MappedStatement;
import org.apache.ibatis.plugin.*;
import org.apache.ibatis.session.ResultHandler;
import org.apache.ibatis.session.RowBounds;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.sql.CallableStatement;
import java.sql.Connection;

@Intercepts({
    @Signature(type = Executor.class, method = "update",
               args = {MappedStatement.class, Object.class}),
    @Signature(type = Executor.class, method = "query",
               args = {MappedStatement.class, Object.class, RowBounds.class, ResultHandler.class})
})
@Component
public class SessionContextInterceptor implements Interceptor {

    private static final Logger log = LoggerFactory.getLogger(SessionContextInterceptor.class);

    @Override
    public Object intercept(Invocation invocation) throws Throwable {
        EasyAuthIdentity identity = EasyAuthContext.get();

        if (identity != null && identity.oid() != null) {
            Executor executor = (Executor) invocation.getTarget();
            Connection connection = executor.getTransaction().getConnection();

            log.debug("Setting session context: callerOid={}", identity.oid());

            try (CallableStatement cs = connection.prepareCall(
                    "{call dbo.usp_SetSessionContext(?)}")) {
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

**Register the interceptor in MyBatis config:**
```java
@Configuration
public class MyBatisConfig {

    @Bean
    public ConfigurationCustomizer mybatisConfigCustomizer(
            SessionContextInterceptor sessionContextInterceptor) {
        return configuration -> {
            configuration.addInterceptor(sessionContextInterceptor);
        };
    }
}
```

**CRITICAL NOTE:** This interceptor calls `usp_SetSessionContext` on EVERY query. For typical API request patterns (1-3 queries per request), this overhead is negligible (~1ms per call). If a request makes many queries, consider optimizing by tracking whether context has already been set on the current connection within the current request using a request-scoped flag.

### Permission Gate (for workflow submit routes)

```java
@Service
public class PermissionService {
    private final SecurityMapper securityMapper;

    public void checkPermission(String userId, String permissionCode, int plantId) {
        Boolean allowed = securityMapper.checkPermission(userId, permissionCode, plantId);
        if (!Boolean.TRUE.equals(allowed)) {
            throw new ForbiddenException(
                "User %s lacks permission %s for plant %d".formatted(userId, permissionCode, plantId));
        }
    }
}
```

```xml
<!-- SecurityMapper.xml -->
<select id="checkPermission" statementType="CALLABLE" resultType="boolean">
    {call security.usp_CheckPermission(
        #{userId, mode=IN, jdbcType=VARCHAR},
        #{permissionCode, mode=IN, jdbcType=VARCHAR},
        #{plantId, mode=IN, jdbcType=INTEGER}
    )}
</select>
```

---

## 4. springdoc-openapi

### Dependencies

```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.8.5</version>
</dependency>
```

**IMPORTANT:** For Spring Boot 3.x, use springdoc v2.x (`springdoc-openapi-starter-*`). springdoc v1.x is for Spring Boot 2.x only.

### Configuration

```yaml
# application.yml
springdoc:
  api-docs:
    path: /v3/api-docs
  swagger-ui:
    path: /swagger-ui.html
    enabled: true
  packages-to-scan: com.sfquality.api.controller
  default-produces-media-type: application/json
```

### Matching Exact Route Paths and Response Shapes

Use `@Operation` and `@Schema` annotations to control the OpenAPI spec precisely:

```java
@RestController
@RequestMapping("/v1/ncrs")
@Tag(name = "NCR", description = "Non-Conformance Reports")
public class NcrController {

    @GetMapping("/{ncrId}")
    @Operation(summary = "Get NCR by ID")
    @ApiResponse(responseCode = "200", description = "NCR found",
        content = @Content(schema = @Schema(implementation = NcrDetailDto.class)))
    @ApiResponse(responseCode = "404", description = "NCR not found")
    public ResponseEntity<NcrDetailDto> getNcrById(@PathVariable int ncrId) {
        return ResponseEntity.ok(ncrService.getNcrById(ncrId));
    }

    @GetMapping
    @Operation(summary = "Get NCR queue (paginated)")
    public ResponseEntity<PagedResponse<NcrSummaryDto>> getNcrQueue(
            @RequestParam int plantId,
            @RequestParam(required = false) String statusFilter,
            @RequestParam(required = false) String cursor,
            @RequestParam(defaultValue = "25") int pageSize) {
        return ResponseEntity.ok(ncrService.getNcrQueue(plantId, statusFilter, cursor, pageSize));
    }
}
```

**Control JSON property names with Jackson annotations:**
```java
public record NcrDetailDto(
    @Schema(description = "NCR unique identifier")
    @JsonProperty("ncrId") int ncrId,

    @Schema(description = "Human-readable NCR number")
    @JsonProperty("ncrNumber") String ncrNumber,

    @Schema(description = "NCR title")
    @JsonProperty("title") String title

    // ... match EXACTLY the property names from the C# API
) {}
```

### Publishing Static OpenAPI JSON for Contract Chain

**Maven plugin configuration (in pom.xml):**
```xml
<build>
    <plugins>
        <!-- Spring Boot starts/stops the app for integration test -->
        <plugin>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
            <configuration>
                <jvmArguments>-Dspring.application.admin.enabled=true</jvmArguments>
            </configuration>
            <executions>
                <execution>
                    <id>pre-integration-test</id>
                    <goals><goal>start</goal></goals>
                </execution>
                <execution>
                    <id>post-integration-test</id>
                    <goals><goal>stop</goal></goals>
                </execution>
            </executions>
        </plugin>

        <!-- springdoc grabs the spec from the running app -->
        <plugin>
            <groupId>org.springdoc</groupId>
            <artifactId>springdoc-openapi-maven-plugin</artifactId>
            <version>1.5</version>
            <executions>
                <execution>
                    <id>integration-test</id>
                    <goals><goal>generate</goal></goals>
                </execution>
            </executions>
            <configuration>
                <apiDocsUrl>http://localhost:8080/v3/api-docs</apiDocsUrl>
                <outputFileName>api-openapi.publish.json</outputFileName>
                <outputDir>${project.basedir}</outputDir>
            </configuration>
        </plugin>
    </plugins>
</build>
```

**Run with:** `mvn verify -Pci` (use a CI profile with mock DB so the app can start without Azure SQL)

**CI profile for spec generation:**
```yaml
# application-ci.yml -- used during mvn verify to generate OpenAPI spec
spring:
  datasource:
    url: jdbc:h2:mem:testdb;MODE=MSSQLServer
    driver-class-name: org.h2.Driver
  sql:
    init:
      mode: never
app:
  easy-auth:
    mock-enabled: true
    mock-oid: "ci-build-user"
    mock-name: "CI Build"
    mock-email: "ci@sfquality.local"
```

Add H2 as test dependency:
```xml
<dependency>
    <groupId>com.h2database</groupId>
    <artifactId>h2</artifactId>
    <scope>test</scope>
</dependency>
```

---

## 5. Cross-Cutting Concerns Translation

### C# to Java Mapping Table

| Concern | C# / ASP.NET Core | Java / Spring Boot | Library |
|---------|-------------------|-------------------|---------|
| Correlation ID | Custom middleware | OncePerRequestFilter + MDC | Built-in |
| Structured logging | Serilog + JSON sink | Spring Boot 3.4 structured logging | Built-in (3.4+) |
| Rate limiting | ASP.NET rate limiter middleware | Bucket4j servlet filter | bucket4j-core |
| Retry / circuit breaker | Polly | Resilience4j | resilience4j-spring-boot3 |
| Error mapping | IExceptionFilter | @ControllerAdvice + @ExceptionHandler | Built-in |
| Pagination | Custom PagedResponse<T> | Java record PagedResponse<T> | Custom |
| Request auditing | Custom middleware | OncePerRequestFilter | Built-in |
| CORS | UseCors() middleware | @CrossOrigin or WebMvcConfigurer | Built-in |
| Health check | MapHealthChecks() | Spring Boot Actuator | Built-in |

### Correlation ID Filter

```java
@Component
@Order(Ordered.HIGHEST_PRECEDENCE + 10)
public class CorrelationIdFilter extends OncePerRequestFilter {

    public static final String HEADER = "X-Correlation-Id";
    public static final String MDC_KEY = "correlationId";

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                     HttpServletResponse response,
                                     FilterChain filterChain)
            throws ServletException, IOException {

        String correlationId = request.getHeader(HEADER);
        if (correlationId == null || correlationId.isBlank()) {
            correlationId = UUID.randomUUID().toString();
        }

        MDC.put(MDC_KEY, correlationId);
        response.setHeader(HEADER, correlationId);

        try {
            filterChain.doFilter(request, response);
        } finally {
            MDC.remove(MDC_KEY);
        }
    }
}
```

### Structured JSON Logging (Spring Boot 3.4 -- NO external library needed)

```yaml
# application-prod.yml
logging:
  structured:
    format:
      console: logstash    # Options: ecs, logstash, gelf
    json:
      add:
        service: sf-quality-api
  level:
    com.sfquality: INFO
    org.mybatis: WARN
    com.zaxxer.hikari: WARN
```

MDC values (`correlationId`, `callerOid`) are **automatically included** in every JSON log line. No additional configuration needed.

**Example JSON log output:**
```json
{
  "@timestamp": "2026-02-27T10:15:00.123Z",
  "@version": "1",
  "message": "NCR created successfully",
  "logger_name": "com.sfquality.api.service.NcrService",
  "thread_name": "virtual-thread-42",
  "level": "INFO",
  "correlationId": "abc-123-def-456",
  "callerOid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "service": "sf-quality-api"
}
```

### Rate Limiting (Bucket4j -- 120 req/60s per identity)

```java
@Component
@Order(Ordered.HIGHEST_PRECEDENCE + 20)
public class RateLimitFilter extends OncePerRequestFilter {

    // Use Caffeine cache to auto-expire stale buckets
    private final Cache<String, Bucket> buckets = Caffeine.newBuilder()
        .expireAfterAccess(Duration.ofMinutes(10))
        .build();

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
                                     FilterChain filterChain)
            throws ServletException, IOException {

        EasyAuthIdentity identity = EasyAuthContext.get();
        if (identity != null && identity.oid() != null) {
            Bucket bucket = buckets.get(identity.oid(), k -> createBucket());
            ConsumptionProbe probe = bucket.tryConsumeAndReturnRemaining(1);

            if (!probe.isConsumed()) {
                response.setStatus(429);
                response.setHeader("Retry-After",
                    String.valueOf(TimeUnit.NANOSECONDS.toSeconds(probe.getNanosToWaitForRefill())));
                response.getWriter().write("{\"error\":\"Rate limit exceeded\",\"retryAfter\":" +
                    TimeUnit.NANOSECONDS.toSeconds(probe.getNanosToWaitForRefill()) + "}");
                return;
            }

            response.setHeader("X-Rate-Limit-Remaining",
                String.valueOf(probe.getRemainingTokens()));
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

Add Caffeine dependency for cache-backed buckets:
```xml
<dependency>
    <groupId>com.github.ben-manes.caffeine</groupId>
    <artifactId>caffeine</artifactId>
</dependency>
```

### Resilience4j (Polly equivalent)

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
        ignore-exceptions:
          - org.apache.ibatis.exceptions.PersistenceException
    retry-aspect-order: 2          # Retry runs INSIDE circuit breaker
  circuitbreaker:
    instances:
      sqlCircuitBreaker:
        register-health-indicator: true
        sliding-window-size: 20
        failure-rate-threshold: 50
        wait-duration-in-open-state: 10s
        permitted-number-of-calls-in-half-open-state: 3
    circuit-breaker-aspect-order: 1  # Circuit breaker wraps retry
```

**Usage:**
```java
@Service
public class NcrService {
    private final NcrMapper ncrMapper;

    @Retry(name = "sqlRetry")
    public NcrDetailDto getNcrById(int ncrId) {
        NcrDetailDto dto = ncrMapper.getNcrById(ncrId);
        if (dto == null) {
            throw new ResourceNotFoundException("NCR", ncrId);
        }
        return dto;
    }
}
```

### Audit Logging Filter

```java
@Component
@Order(Ordered.HIGHEST_PRECEDENCE + 40)  // After Easy Auth filter
public class AuditLoggingFilter extends OncePerRequestFilter {

    private static final Logger auditLog = LoggerFactory.getLogger("AUDIT");

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                     HttpServletResponse response,
                                     FilterChain filterChain)
            throws ServletException, IOException {

        long startTime = System.currentTimeMillis();

        try {
            filterChain.doFilter(request, response);
        } finally {
            long duration = System.currentTimeMillis() - startTime;
            String oid = MDC.get("callerOid");

            auditLog.atInfo()
                .addKeyValue("route", request.getRequestURI())
                .addKeyValue("method", request.getMethod())
                .addKeyValue("status", response.getStatus())
                .addKeyValue("durationMs", duration)
                .addKeyValue("callerOid", oid != null ? oid : "anonymous")
                .log("API call completed");
        }
    }

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        return request.getRequestURI().startsWith("/swagger-ui")
            || request.getRequestURI().startsWith("/v3/api-docs");
    }
}
```

---

## 6. Build Tooling

### Recommendation: Maven (not Gradle)

**Why Maven:**
- XML-based `pom.xml` is more parseable and predictable for coding agents than Gradle's Groovy/Kotlin DSL
- Spring Boot's primary documentation defaults to Maven
- Spring Initializr generates Maven projects by default
- Deterministic builds -- no build script is "code" that can have bugs
- The project is not large enough to benefit from Gradle's incremental build speed

### GitHub Actions CI Pipeline

```yaml
# .github/workflows/ci.yml
name: Spring Boot CI

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Java 21
        uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: 'microsoft'  # Microsoft OpenJDK for Azure compatibility

      - name: Cache Maven packages
        uses: actions/cache@v4
        with:
          path: ~/.m2/repository
          key: ${{ runner.os }}-maven-${{ hashFiles('**/pom.xml') }}
          restore-keys: ${{ runner.os }}-maven-

      - name: Build and test
        run: mvn clean verify -Pci

      - name: Validate OpenAPI contract
        run: |
          # Compare generated spec against C# baseline
          if [ -f api-openapi.publish.json ]; then
            # Use oasdiff or similar tool for structural comparison
            echo "OpenAPI spec generated successfully"
          else
            echo "ERROR: OpenAPI spec not generated"
            exit 1
          fi

      - name: Validate DB contract references
        run: |
          # Check that all stored procedure names referenced in mapper XML
          # exist in db-contract-manifest.snapshot.json
          python scripts/validate-db-contracts.py

      - name: Upload OpenAPI spec
        if: github.ref == 'refs/heads/main'
        uses: actions/upload-artifact@v4
        with:
          name: openapi-spec
          path: api-openapi.publish.json
```

### Project Structure

```
sf-quality-api/
  pom.xml
  api-openapi.publish.json              # Generated static OpenAPI spec
  db-contract-manifest.snapshot.json     # Pinned from sf-quality-db
  src/
    main/
      java/com/sfquality/api/
        SfQualityApiApplication.java
        config/
          MyBatisConfig.java
          WebMvcConfig.java              # CORS, interceptors
          OpenApiConfig.java             # springdoc customization
          EasyAuthProperties.java
        security/
          EasyAuthFilter.java
          EasyAuthContext.java
          EasyAuthIdentity.java
          ClientPrincipal.java
          PermissionService.java
        filter/
          CorrelationIdFilter.java
          RateLimitFilter.java
          AuditLoggingFilter.java
        mybatis/
          SessionContextInterceptor.java
        exception/
          SqlErrorCodeExceptionHandler.java
          ResourceNotFoundException.java
          ForbiddenException.java
          ErrorResponse.java
        dto/
          PagedResponse.java
          ncr/
            NcrDetailDto.java
            NcrSummaryDto.java
            NcrCreateParams.java         # Mutable -- has OUT params
            NcrCreateResult.java
            NcrStatusParams.java
            NcrQueueParams.java
          # ... other domain DTOs
        controller/
          DiagnosticsController.java     # Health check
          NcrController.java
          CapaController.java
          # ... other domain controllers
        service/
          NcrService.java
          CapaService.java
          # ... other domain services
        mapper/
          NcrMapper.java
          SecurityMapper.java
          # ... other domain mappers
      resources/
        application.yml
        application-dev.yml
        application-prod.yml
        application-ci.yml
        mapper/
          NcrMapper.xml
          SecurityMapper.xml
          # ... other domain mapper XMLs
    test/
      java/com/sfquality/api/
        # Mirror structure for tests
```

---

## Filter Execution Order Summary

| Order | Filter | Purpose |
|-------|--------|---------|
| +10 | CorrelationIdFilter | Extract/generate correlation ID, set MDC |
| +20 | RateLimitFilter | Check Bucket4j token (needs OID from next filter on subsequent requests) |
| +30 | EasyAuthFilter | Parse X-MS-CLIENT-PRINCIPAL, set EasyAuthContext + MDC |
| +40 | AuditLoggingFilter | Log request/response timing and metadata |

**Note:** RateLimitFilter at +20 runs before EasyAuthFilter at +30. On the first request, the identity will not yet be available for rate limiting. Two options:
1. Move RateLimitFilter to +35 (after EasyAuth) -- recommended
2. Use the `X-MS-CLIENT-PRINCIPAL-ID` header directly (Azure also provides this as a simple header)

**Recommended order adjustment:**
| Order | Filter | Purpose |
|-------|--------|---------|
| +10 | CorrelationIdFilter | Extract/generate correlation ID |
| +20 | EasyAuthFilter | Parse identity |
| +30 | RateLimitFilter | Rate limit by identity (now available) |
| +40 | AuditLoggingFilter | Log everything |

---

## Sources

- [Azure App Service Java deployment](https://learn.microsoft.com/en-us/azure/developer/java/migration/migrate-spring-boot-to-app-service) - JAR deployment, startup config
- [Azure App Service Java configuration](https://docs.azure.cn/en-us/app-service/configure-language-java-deploy-run) - JVM settings, startup command
- [MyBatis Mapper XML](https://mybatis.org/mybatis-3/sqlmap-xml.html) - CALLABLE statementType, IN/OUT parameters, resultSets
- [MyBatis Spring Boot Starter](https://mybatis.org/spring-boot-starter/mybatis-spring-boot-autoconfigure/) - auto-configuration, version 3.0.x for Spring Boot 3
- [MyBatis OUT parameter handling](https://dzhg.dev/posts/2020/09/how-to-handle-output-parameter-of-callable-statement-in-mybatis/) - mutable param objects for OUT params
- [Azure Easy Auth identities](https://learn.microsoft.com/en-us/azure/app-service/configure-authentication-user-identities) - X-MS-CLIENT-PRINCIPAL structure
- [sp_set_session_context](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-set-session-context-transact-sql) - session context API
- [springdoc-openapi](https://springdoc.org/) - Spring Boot 3 OpenAPI generation
- [springdoc Maven plugin](https://springdoc.org/plugins.html) - static spec generation during build
- [Spring Boot structured logging](https://docs.spring.io/spring-boot/reference/features/logging.html) - 3.4 built-in JSON logging
- [Resilience4j Spring Boot 3](https://resilience4j.readme.io/docs/getting-started-3) - retry, circuit breaker config
- [Resilience4j aspect order issue](https://github.com/resilience4j/resilience4j/issues/2383) - Spring Boot 3 default ordering bug
- [Bucket4j](https://github.com/bucket4j/bucket4j) - token bucket rate limiting
- [HikariCP](https://github.com/brettwooldridge/HikariCP) - connection pool best practices
- [Baeldung: HikariCP + Spring Boot](https://www.baeldung.com/spring-boot-hikari) - configuration guide
