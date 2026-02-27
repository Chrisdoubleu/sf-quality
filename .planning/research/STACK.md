# Technology Stack

**Project:** sf-quality-api Spring Boot Migration
**Researched:** 2026-02-27

## Recommended Stack

### Core Framework
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Java | 21 (LTS) | Runtime | Current LTS, required by Spring Boot 3.x, virtual threads available |
| Spring Boot | 3.4.x | Application framework | Latest stable, built-in structured logging, Java 21 support |
| Spring Web MVC | (managed by Boot) | HTTP layer | Servlet-based, matches existing synchronous stored-proc pattern |

### Database Access
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| MyBatis Spring Boot Starter | 3.0.x | SQL mapper | Closest Java equivalent to Dapper -- thin, SQL-first, no ORM. statementType=CALLABLE for stored procs |
| Microsoft MSSQL JDBC | 12.x | JDBC driver | Official Microsoft driver, supports Azure SQL, Azure AD auth |
| HikariCP | (managed by Boot) | Connection pool | Spring Boot default, fastest JDBC pool, proven with Azure SQL |

### API Documentation
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| springdoc-openapi-starter-webmvc-ui | 2.8.x | OpenAPI generation | Runtime spec generation from Spring MVC controllers, Swagger UI included |
| springdoc-openapi-maven-plugin | 1.5 | Static spec export | Generates openapi.json during build for contract chain validation |

### Cross-Cutting Concerns
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Resilience4j | 2.x | Retry + circuit breaker | Direct Polly equivalent, Spring Boot 3 starter available, annotation-driven |
| Bucket4j | 8.x | Rate limiting | Token-bucket algorithm, works as servlet filter, no external infrastructure needed |
| Logback | (managed by Boot) | Structured logging | Spring Boot 3.4 built-in structured JSON logging (ECS/Logstash format), MDC auto-included |
| Micrometer | (managed by Boot) | Metrics | Auto-configured with Actuator, exposes connection pool and request metrics |

### Infrastructure
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Azure App Service (Java SE) | - | Hosting | Existing infrastructure, Java SE runtime for executable JAR |
| Maven | 3.9.x | Build tool | More predictable than Gradle for CI, XML-based config is more parseable by agents, Spring Boot's primary build tool |
| GitHub Actions | - | CI/CD | Existing CI infrastructure |

### Testing
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| JUnit 5 | (managed by Boot) | Unit tests | Spring Boot default test framework |
| Mockito | (managed by Boot) | Mocking | Standard Java mocking library |
| Spring Boot Test | (managed by Boot) | Integration tests | @SpringBootTest for full context, @WebMvcTest for controller layer |

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Data access | MyBatis | Spring Data JPA / Hibernate | Project requirement: thin SQL mapper only. JPA adds ORM complexity inappropriate for stored-proc-only API |
| Data access | MyBatis | Spring JDBC Template | MyBatis provides XML mapper files, type mapping, and interceptor infrastructure that JdbcTemplate lacks |
| Build tool | Maven | Gradle | Maven is more predictable in CI, XML is more parseable by coding agents, Spring Boot docs default to Maven. Gradle's speed advantage is negligible for this project size |
| Rate limiting | Bucket4j | Spring Cloud Gateway rate limiter | No API gateway in architecture -- Bucket4j works as embedded filter |
| Logging | Logback (built-in) | Log4j2 | Spring Boot 3.4 structured logging is Logback-first; no reason to switch |
| OpenAPI | springdoc-openapi | Swagger Core | springdoc-openapi is the standard for Spring Boot 3.x, Swagger Core requires manual configuration |
| Resilience | Resilience4j | Spring Retry | Resilience4j has circuit breaker + retry + rate limiter in one library, better metrics integration |

## Maven Dependencies (pom.xml)

```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.4.3</version>
</parent>

<properties>
    <java.version>21</java.version>
    <mybatis-spring-boot.version>3.0.4</mybatis-spring-boot.version>
    <springdoc.version>2.8.5</springdoc.version>
    <resilience4j.version>2.2.0</resilience4j.version>
    <bucket4j.version>8.14.0</bucket4j.version>
</properties>

<dependencies>
    <!-- Core -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-actuator</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-validation</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-aop</artifactId>
    </dependency>

    <!-- Database -->
    <dependency>
        <groupId>org.mybatis.spring.boot</groupId>
        <artifactId>mybatis-spring-boot-starter</artifactId>
        <version>${mybatis-spring-boot.version}</version>
    </dependency>
    <dependency>
        <groupId>com.microsoft.sqlserver</groupId>
        <artifactId>mssql-jdbc</artifactId>
        <scope>runtime</scope>
    </dependency>

    <!-- API Documentation -->
    <dependency>
        <groupId>org.springdoc</groupId>
        <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
        <version>${springdoc.version}</version>
    </dependency>

    <!-- Resilience -->
    <dependency>
        <groupId>io.github.resilience4j</groupId>
        <artifactId>resilience4j-spring-boot3</artifactId>
        <version>${resilience4j.version}</version>
    </dependency>

    <!-- Rate Limiting -->
    <dependency>
        <groupId>com.bucket4j</groupId>
        <artifactId>bucket4j-core</artifactId>
        <version>${bucket4j.version}</version>
    </dependency>

    <!-- Test -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>
    <dependency>
        <groupId>org.mybatis.spring.boot</groupId>
        <artifactId>mybatis-spring-boot-starter-test</artifactId>
        <version>${mybatis-spring-boot.version}</version>
        <scope>test</scope>
    </dependency>
</dependencies>
```

## Build Plugins

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
            <configuration>
                <jvmArguments>-Dspring.application.admin.enabled=true</jvmArguments>
            </configuration>
            <executions>
                <execution>
                    <goals>
                        <goal>start</goal>
                        <goal>stop</goal>
                    </goals>
                </execution>
            </executions>
        </plugin>
        <plugin>
            <groupId>org.springdoc</groupId>
            <artifactId>springdoc-openapi-maven-plugin</artifactId>
            <version>1.5</version>
            <executions>
                <execution>
                    <id>integration-test</id>
                    <goals>
                        <goal>generate</goal>
                    </goals>
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

## Sources

- [MyBatis Spring Boot Starter docs](https://mybatis.org/spring-boot-starter/mybatis-spring-boot-autoconfigure/) - version compatibility, auto-configuration
- [MyBatis Mapper XML docs](https://mybatis.org/mybatis-3/sqlmap-xml.html) - stored procedure CALLABLE syntax
- [springdoc-openapi](https://springdoc.org/) - Spring Boot 3 compatibility, version 2.8.x
- [springdoc plugins](https://springdoc.org/plugins.html) - Maven plugin for static spec generation
- [Spring Boot logging docs](https://docs.spring.io/spring-boot/reference/features/logging.html) - structured logging in 3.4
- [Microsoft MSSQL JDBC](https://learn.microsoft.com/en-us/sql/connect/jdbc/microsoft-jdbc-driver-for-sql-server) - Azure SQL connectivity
- [Resilience4j getting started](https://resilience4j.readme.io/docs/getting-started-3) - Spring Boot 3 integration
- [Bucket4j GitHub](https://github.com/bucket4j/bucket4j) - token-bucket rate limiting
