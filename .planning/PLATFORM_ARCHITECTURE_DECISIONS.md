# Platform Architecture Decisions: Spring Boot Migration + Rules/Decision Engine

**Date:** 2026-02-27
**For:** Chris Walsh + Java Colleague Review
**Purpose:** Comprehensive decision spec covering the Spring Boot/Java migration AND the rules/decision platform choice for Select Finishing's unified operations system. All research, options, trade-offs, and open questions in one place.

---

## Table of Contents

1. [Context: What We're Building](#1-context-what-were-building)
2. [Systems Landscape](#2-systems-landscape)
3. [Spring Boot Migration: Decided Architecture](#3-spring-boot-migration-decided-architecture)
4. [Rules & Decision Platform: The Core Decision](#4-rules--decision-platform-the-core-decision)
5. [Platform Comparison Matrix](#5-platform-comparison-matrix)
6. [Detailed Platform Evaluations](#6-detailed-platform-evaluations)
7. [Manufacturing & Compliance Context](#7-manufacturing--compliance-context)
8. [Forms Architecture Decisions (Phase 1 Adjudication)](#8-forms-architecture-decisions-phase-1-adjudication)
9. [Open Decisions for Discussion](#9-open-decisions-for-discussion)
10. [Recommended Architecture](#10-recommended-architecture)
11. [Validation Spike Proposal](#11-validation-spike-proposal)
12. [Sources](#12-sources)

---

## 1. Context: What We're Building

### The Immediate Project: sf-quality

A Quality Management System for Select Finishing (custom coating company, Tier 2 automotive supplier). Manages NCRs, CAPAs, 8Ds, SCARs, inspection workflows, and quality event triage.

**Current state:**
- `sf-quality-db` — Azure SQL, T-SQL, 99 stored procedures, 38 views, 8 schemas. Production v3.0.
- `sf-quality-api` — ASP.NET Core 9.0 / C# / Dapper. ~50% complete. **Migrating to Spring Boot / Java.**
- `sf-quality-app` — Next.js 15 / React 19 / TypeScript. Foundation in progress.
- Contract chain governance: DB manifest -> API OpenAPI -> App snapshot (CI-enforced).

### The Bigger Picture: Unified Operations Platform

sf-quality is the **first vertical** in a broader platform that will become the operational backbone of Select Finishing. The rules/decision engine chosen now becomes foundational infrastructure for the entire platform — not just quality.

### APQP-PPAP System (Migration Candidate)

A separate APQP/PPAP system currently built in Power Apps / Dataverse manages program launches, part approval, OEM spec tracking for 6 OEMs (Ford, GM, Toyota, HINO, Stellantis, Waymo). Currently ~30% mature (PPAP document analysis complete, APQP project tracking not yet implemented). **Open to migration** into the Spring Boot / rules platform.

---

## 2. Systems Landscape

| System | Owner | Domains |
|--------|-------|---------|
| **EPICOR** (implementing) | Vendor | Supply chain, EDI, finance |
| **Dayforce** | Vendor | HR, workforce management |
| **APQP-PPAP System** | Select Finishing | Program launches, part approval, OEM specs (currently Power Apps) |
| **This Platform** | Select Finishing | Everything else operational (see below) |

### Operational Domains This Platform Will Own

| Domain | What It Covers |
|--------|---------------|
| Quality Management | NCRs, CAPAs, 8D, SCAR, inspections, SPC, complaint management |
| APQP / PPAP | Program launches, part approval, control plans, PFMEA, customer specs |
| Production / Shop Floor | Job execution, process routing, operator data collection, cycle times |
| Process Control | Coating parameters, bath chemistry, oven/booth monitoring, recipe management |
| Lab & Testing | Adhesion, thickness, salt spray, color/gloss, test method management |
| Equipment & Maintenance | PM scheduling, calibration, downtime tracking |
| Customer Specs & Compliance | OEM spec management, certifications (Nadcap, IATF, AS9100), audit readiness |
| Environmental | Chemical inventory, SDS, waste, emissions |
| Document Control | Work instructions, controlled docs, revision management |
| Continuous Improvement | Lean/Kaizen tracking, cost of quality, OEE |

### Types of Rules Needed Across All Domains

| Rule Type | Examples | Complexity |
|-----------|----------|-----------|
| Form UX | Show/hide fields, conditional validation, wizard step gating | Simple conditions |
| Specification Matching | OEM X requires 18-25 um e-coat, 480 hr salt spray, ASTM B117 | Lookup + threshold |
| Process Control | Bath chemistry out of spec -> alert, oven temp deviation -> hold parts | Real-time threshold + escalation |
| Workflow Routing | NCR severity + plant + customer -> escalation path + required actions + SLA | Multi-factor decision tree |
| Compliance | Part X for OEM Y requires Nadcap cert + PPAP level + specific test methods | Multi-entity rule chains |
| APQP Gating | Phase transition requires: all deliverables complete, risks mitigated, customer sign-off | Checklist + state machine |
| Disposition | Defect type + severity + customer + part history -> recommend disposition | Complex multi-factor |
| Supplier Scoring | Delivery performance + quality metrics + corrective action history -> risk rating | Aggregation + scoring |
| SPC Alerting | Control chart violations (Western Electric / Nelson rules) -> notification + auto-hold | Statistical pattern detection |
| Cross-domain Orchestration | Program launch triggers: quality plan + inspection templates + calibration schedule + training | Multi-domain event chains |

**Key insight:** Rules don't stay within one domain. A critical NCR can trigger a CAPA, supplier corrective action, customer notification, production hold, and APQP re-evaluation — all from one event.

---

## 3. Spring Boot Migration: Decided Architecture

This section summarizes decisions already made and validated through research.

### Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Runtime | Spring Boot 3.4.x / Java 21 | Colleague's skills, agent-friendly, Azure App Service support |
| Build | Maven (not Gradle) | XML-based pom.xml more parseable for agents |
| Data Access | MyBatis 3.0.x | Closest Java analog to Dapper — thin, SQL-first, no ORM |
| Database Driver | MSSQL JDBC 12.x | Azure SQL |
| Connection Pool | HikariCP | Spring Boot default, tuned for Azure SQL |
| API Docs | springdoc-openapi 2.8.x | OpenAPI 3.x spec generation matching C# contract |
| Resilience | Resilience4j | Retry, circuit breaker (Polly equivalent) |
| Rate Limiting | Bucket4j + Caffeine | 120 req/60s per identity |
| Logging | Spring Boot 3.4 structured JSON | Built-in, no external library |
| Deployment | Azure App Service (Java SE, JAR) | Same target as current C# app |

### Architecture Pattern

```
HTTP Request
  -> Servlet Filter Chain (CorrelationId, EasyAuth, RateLimit, Audit)
    -> Spring MVC Controller (@RestController)
      -> Service Layer (@Service, @Retry)
        -> MyBatis Mapper (XML, CALLABLE stored procedures)
          -> SessionContextInterceptor (calls usp_SetSessionContext)
            -> HikariCP -> Azure SQL
```

### Critical Infrastructure to Replicate

All 14 cross-cutting concerns from the C# implementation are mapped to Spring Boot equivalents. Full code patterns documented in `.planning/research/ARCHITECTURE.md` and `.planning/research/spring-boot-migration-research.md`.

### What This Means for Rules Engine Choice

The Spring Boot migration is a **thin pass-through API** — receive HTTP, parse auth, call stored procedure, return JSON. The rules/decision engine would be an **additional layer** within this architecture, sitting between the controller and the data access layer (or alongside it as a separate service).

---

## 4. Rules & Decision Platform: The Core Decision

### Why This Matters

For a manufacturing quality system under IATF 16949 / ISO 9001:
- **Rules are auditable** — every decision must be traceable (who, what, when, why)
- **Rules change** — coating specs change per customer, new OEMs onboard, compliance requirements evolve
- **Rules span domains** — a program launch affects quality, production, maintenance, training simultaneously
- **Rules ARE the product** — the conditional logic controlling escalation, disposition, compliance, and workflow routing is the core value of the system

### The Three Tiers of Rules

| Tier | Where It Runs | Purpose | Latency Requirement |
|------|--------------|---------|---------------------|
| **Client-side (browser)** | Next.js app | Form UX: show/hide fields, conditional validation, wizard step gating | Instant (0ms) |
| **Server-side (API)** | Spring Boot | Business rules: escalation, disposition, compliance, workflow routing | Fast (<100ms) |
| **Data-side (database)** | Azure SQL | Data integrity: foreign keys, check constraints, RLS, status transitions | N/A (enforcement) |

**The client-side tier needs a JavaScript rules evaluator.** The server-side tier needs a Java rules/decision engine. The data-side tier stays in T-SQL stored procedures. This is a three-layer split, and the rules engine decision is about the **server-side tier** (with implications for the client tier).

---

## 5. Platform Comparison Matrix

Eight options evaluated. Research included current 2025-2026 documentation, release notes, and community status.

| Criterion | A. KIE Full (Kogito+Drools+jBPM) | B. Drools Standalone | C. Easy Rules | D. OpenL Tablets | E. Camunda 8 | F. Flowable | G. Spring Modulith (DDD) | H. GraalVM Polyglot |
|-----------|----------------------------------|---------------------|---------------|-----------------|-------------|------------|--------------------------|---------------------|
| **Spring Boot 3 Native** | Partial | Manual config | Manual config | Manual config | Starter | **Starter (best)** | Native | Manual config |
| **Deploys as JAR on App Service** | Partial | **Yes** | **Yes** | **Yes** | **No** (needs Zeebe cluster) | **Yes** | **Yes** | Risky |
| **Decision Tables (DMN)** | **Yes (best FEEL)** | **Yes** | No | Excel only | **Yes** | **Yes** | No | No |
| **Workflow Orchestration** | **Yes (jBPM/BPMN)** | No | No | No | **Yes (Zeebe/BPMN)** | **Yes (BPMN)** | Events only | No |
| **Case Management (CMMN)** | No | No | No | No | No | **Yes** | No | No |
| **Agent/AI Authorability** | Medium (DRL) | Good (DRL) | Good (Java) | Poor (Excel) | Medium (DMN XML) | Medium (DMN XML) | **Best (Java)** | Good (JSON) |
| **License** | Apache 2.0 | Apache 2.0 | MIT | LGPL 2.1 | **Commercial** (prod) | Apache 2.0 | Apache 2.0 | Permissive |
| **Community** | Large | **Largest** | Dead (maintenance) | Niche | Large (commercial) | Medium-Large | Growing | Small |
| **Maturity** | High | **Highest** | Low | Medium | High | High | Emerging | Experimental |
| **SPC/CEP Support** | **Yes (Drools CEP)** | **Yes (Drools CEP)** | No | No | No | No | No | No |

### Quick Eliminations

| Option | Reason to Eliminate |
|--------|-------------------|
| **C. Easy Rules** | Abandoned since 2020. Maintenance mode only. Not suitable for new projects. |
| **D. OpenL Tablets** | LGPL licensing. Excel-only rule format is poor for AI agents. Niche community. No workflow support. |
| **E. Camunda 8** | **Commercial license required for production.** Architecture requires Zeebe cluster (K8s/SaaS), not a simple JAR. Eliminated on licensing alone. |
| **H. GraalVM Polyglot** | Exotic. GraalVM Node.js deprecated in JDK 21, removed in JDK 23. Fragile coupling of two ecosystems. No decision tables or workflow. |

### Serious Contenders

**Four options remain:**

1. **A. KIE Full (Kogito + Drools + jBPM)** — Maximum power, full platform
2. **B. Drools Standalone** — Rules engine only, most mature
3. **F. Flowable** — Spring-native, BPMN + DMN + CMMN in one
4. **G. Spring Modulith (DDD)** — Rules as Java code, no external engine

---

## 6. Detailed Platform Evaluations

### Option A: Kogito + Drools + jBPM (Apache KIE Full Platform)

**Version:** Apache KIE 10.1.x (incubating). Active development.
**What it is:** Complete business automation platform — Drools for rules, jBPM for process orchestration, Kogito for cloud-native runtime with auto-generated REST APIs.

**Strengths for your use case:**
- Drools has the **most complete DMN/FEEL implementation** of any engine
- jBPM handles complex BPMN workflows (NCR lifecycle, CAPA flows, APQP phase gates)
- Drools CEP (Complex Event Processing) can handle SPC-style real-time stream evaluation
- Excel decision tables compile to DRL — quality engineers can author in Excel
- 20+ years of enterprise adoption via Red Hat
- DRL `when/then` syntax is LLM-friendly — active `droolsGPT` project by Drools lead (Mario Fusco)

**Concerns for your use case:**
- **Quarkus is the first-class runtime**, not Spring Boot. Spring Boot support exists but lags on features (live reload, dev UI, native compilation).
- Full Kogito platform (data index, management console, jobs service) needs containers. A stripped-down Drools+jBPM embedded approach works as a JAR.
- The Apache incubation transition has fragmented documentation.
- No CMMN support (quality investigations are case-based, not just sequential workflows).

**Deployment on Azure:**
- Drools/jBPM embedded in Spring Boot JAR -> Azure App Service: **Works**
- Full Kogito platform with ancillary services -> Needs Azure Container Apps or AKS

**Agent authorability:**
- DRL: Good — structured `when/then` text format, well-represented in LLM training data
- DMN XML: Parseable but verbose — better authored with visual tools
- BPMN XML: Not practical for AI authoring — use visual modeler

---

### Option B: Drools Standalone (No Kogito)

**Version:** Drools 9.44.x (kiegroup) or 10.x (Apache KIE). Both work standalone.
**What it is:** Just the rules engine, embedded in Spring Boot. No process orchestration, no platform.

**Strengths:**
- Most mature Java rules engine. Decades of production use. Largest community.
- Manual Spring Boot config is well-documented (Baeldung, multiple Medium tutorials).
- DMN decision tables + Excel decision tables + DRL rules — full authoring flexibility.
- Drools CEP for SPC pattern detection.
- Lightest dependency footprint of the "serious" options.
- Deploys trivially as a Spring Boot JAR on Azure App Service.

**Concerns:**
- **No workflow orchestration.** You'd need to build state machines yourself or add jBPM later (effectively becoming Option A piecemeal).
- No Spring Boot auto-configuration starter — manual `@Bean` setup for KieContainer.
- If you later need process orchestration, you'll wish you'd started with Flowable or KIE.

**When to choose this:** If you believe your workflow orchestration needs are simple enough for custom Java code or Spring State Machine, and you want the most mature, lightest rules engine.

---

### Option F: Flowable (NEW — Not Previously Discussed)

**Version:** Flowable 7.1.x. Spring Boot 3, Spring 6, Java 17+ baseline. Flowable 8 planned for Spring Boot 4.
**What it is:** BPM + Case Management + Decision engine. Forked from Activiti in 2016 by the original Activiti creators. **The most Spring-native option.**

**Strengths for your use case:**
- **Native Spring Boot starters** with full auto-configuration:
  - `flowable-spring-boot-starter` (BPMN + CMMN + DMN all-in-one)
  - `flowable-spring-boot-starter-dmn` (DMN only, lightweight)
  - Add dependency, engines auto-create. DMN files in `/dmn/` folder auto-deploy.
- **CMMN (Case Management) support** — this is unique and directly relevant:
  - NCR investigations are cases, not linear workflows
  - Customer complaints are cases with variable resolution paths
  - CMMN handles "this case needs these activities, in any order, triggered by events"
  - **No other option on the list supports CMMN**
- **BPMN 2.0** for structured workflows (approval chains, APQP phase gates)
- **DMN 1.3** for decision tables (quality disposition, escalation routing)
- All three engines run **embedded in a Spring Boot JAR** — no external services, no K8s
- Apache 2.0 license (fully open source community edition)
- ~8k GitHub stars, 350+ contributors, active development
- Flowable markets explicitly to manufacturing: "streamline supply chain operations, procurement, inventory, and quality assurance"

**Concerns:**
- DMN FEEL implementation may be less complete than Drools (subset of FEEL)
- No DRL equivalent — decision logic is DMN-only (no forward-chaining inference engine)
- No Complex Event Processing (CEP) — SPC rule evaluation would be custom code
- Smaller community than Drools/KIE (but larger than most alternatives)
- Enterprise edition (commercial) has governance features not in open-source

**Deployment on Azure:**
- Embeds in Spring Boot JAR -> Azure App Service: **Perfect fit**
- Uses any JDBC database (Azure SQL / SQL Server supported)

**Agent authorability:**
- DMN XML: Structured, parseable — agents can generate decision tables
- BPMN XML: Complex — use visual Flowable Modeler for process design
- CMMN XML: Structured but niche — less LLM training data

**Why this wasn't in the original discussion:** The prior research focused on json-rules-engine (JavaScript) because the API was C#. The Spring Boot migration opened the Java rules engine space, and the initial conversation focused on Kogito/Drools. Flowable emerged from the expanded research as potentially the best overall fit.

---

### Option G: Spring Modulith + jMolecules (DDD Approach)

**Version:** Spring Modulith 2.0 GA (Nov 2025), jMolecules 2.0 (Nov 2025).
**What it is:** Not a rules engine — an architectural approach where business rules are Java code organized as domain logic using DDD patterns. Spring Modulith enforces module boundaries; jMolecules provides DDD stereotypes.

**Strengths:**
- Rules are standard Java code — **best option for AI/agent authoring**
- No external DSL to learn (DRL, DMN, BPMN) — it's all Java
- Spring Modulith provides module boundary enforcement and event publication
- Perfect Spring Boot integration (it IS Spring Boot)
- jMolecules annotations make architectural intent explicit (`@AggregateRoot`, `@DomainEvent`, `@Service`)

**Concerns:**
- **Not a rules engine.** No externalized rules, no decision tables, no visual modeling.
- No audit trail of rule executions (you'd build this yourself)
- No process orchestration engine (choreography via events, not orchestration via BPMN)
- Rule changes require code deployment
- For 10+ operational domains with complex cross-domain rules, "rules as code" may become unwieldy

**When to choose this:** As a **complement** to a rules engine, not a replacement. Use Spring Modulith to structure your domain code and jMolecules for DDD annotations, then embed Drools or Flowable for externalized decision logic and workflow orchestration.

---

## 7. Manufacturing & Compliance Context

### What IATF 16949 Auditors Need from a Rules Engine

Based on IATF 16949:2016 requirements:

1. **Rule definitions must match control plans** — business rules executing in software must correspond to documented reaction plans
2. **Version control** — when rules change, documented change history with authorization
3. **Execution records** — evidence that rules fired when conditions were met (full audit trail with inputs + outputs)
4. **Retention** — rule execution records retained for production life + 1 calendar year minimum
5. **Traceability** — trace from a specific part/lot back to the rules evaluated and decisions made
6. **Temporary changes** — Clause 8.5.6.1.1 requires any temporary change to process controls be documented

**Assessment:** A formal decision engine (DMN-based) provides massive auditability advantages over hardcoded business logic. DMN decision tables are versionable, their execution is loggable with full input/output capture, and the tables themselves serve as human-readable documentation that matches control plan requirements.

### DataLyzer as Reference Architecture

DataLyzer (commercial SPC/FMEA tool) demonstrates the integrated chain that your platform aims to replicate:

**Process Flow -> PFMEA -> Control Plan -> Real-Time SPC -> Rules Evaluation -> Reaction Plan**

All in a single database with automatic linkage. Changes to process flow automatically reflect in PFMEA, sync with Control Plan. SPC control charts created directly from Control Plan. Western Electric + Wheeler + Nelson rules for real-time analysis.

This is the pattern to study. Your platform is building this chain across multiple systems.

### SPC Rules: Specialized, Not General-Purpose

SPC rule evaluation (Western Electric rules, Nelson rules) is a specialized algorithm, not a general business rule:
- Fixed set of pattern-detection algorithms against sliding windows of data points
- Rules are parameterized (how many points, how many sigma, which side)
- Real-world implementations (InfinityQS, Parsec TrakSYS, DataLyzer) use specialized engines, not general BRMS

**Recommendation:** Do NOT use Drools/Flowable for SPC rule evaluation. Build a specialized SPC module with the well-defined algorithms. Use Drools/Flowable for the **reaction** to SPC violations (escalation, holds, notifications).

### APQP/PPAP Automation Patterns

Commercial APQP tools (Omnex, AIAG CTS, DataLyzer) all follow the same pattern:
- **Phase-gate workflow** — APQP phases modeled as sequential gates with approval requirements
- **Document linkage** — PFMEA rows link to Control Plan characteristics link to SPC data collection points
- **Change propagation** — changes in one document trigger alerts to revisit linked documents
- **Submission workflow** — PPAP packages assembled from linked artifacts with approval routing

This maps directly to BPMN process orchestration + DMN decision gating. Flowable or jBPM can model this natively.

### Camunda in Automotive (Case Study)

Audi selected Camunda for process orchestration, starting with procure-to-pay. Rolling out to procurement, production, and HR across the Volkswagen Group. While this validates BPMN/DMN in automotive, Camunda 8's commercial licensing eliminates it for your stack. Flowable provides equivalent capabilities under Apache 2.0.

---

## 8. Forms Architecture Decisions (Phase 1 Adjudication)

These 11 decisions from `DECISION_BRIEF.md` need adjudication. The rules engine choice affects several of them. Updated with current context (Spring Boot migration + broader platform vision).

### Decision 1: Where Does Business Logic Live?

**Original options:** All T-SQL (A), Split form UX in TS + data integrity in T-SQL (B), All TypeScript (C)

**Updated with rules engine context:**
- **Option B-revised (RECOMMENDED):** Three-layer split:
  - **TypeScript (browser):** Form UX rules — show/hide fields, conditional validation, wizard step gating. Uses json-rules-engine or DMN client-side evaluator.
  - **Java (Spring Boot):** Business rules — escalation, disposition, compliance, workflow routing, APQP gating. Uses Drools or Flowable DMN.
  - **T-SQL (Azure SQL):** Data integrity — foreign keys, check constraints, RLS, status transitions, stored procedure validation.

### Decision 2: What Happens to C# API + Dapper?

**DECIDED:** Spring Boot / Java / MyBatis replaces C#. Full migration. Contract chain preserved.

**Implication:** The rules engine runs in Java on the Spring Boot API tier. This eliminates json-rules-engine as the *server-side* engine (it's JavaScript). The server-side engine must be Java-native.

### Decision 6: How Should Forms Handle Conditional Logic?

**Original options:** Hardcode in React (A), json-rules-engine (B), Structured TS module (C)

**Updated:**
- **Client-side:** json-rules-engine remains the best option for browser-side form UX rules. Isomorphic JS, JSON rule format, proven integration with React Hook Form.
- **Server-side:** The same conditional logic rules need enforcement on the server. Two sub-options:
  - **6B-i:** json-rules-engine rules stored in DB, evaluated client-side for UX + server-side for enforcement via a Java evaluator (custom or GraalVM polyglot)
  - **6B-ii:** DMN decision tables on the server (Flowable/Drools), json-rules-engine on the client, with rule intent shared but implementations separate
  - **6B-iii:** DMN everywhere — use `dmn-eval-js` in the browser for client-side DMN evaluation + Flowable/Drools on the server. One rule format, two runtimes. (Limitation: dmn-eval-js supports only Simple FEEL.)

### Decision 9: Which Business Rules Engine?

**Original options:** json-rules-engine (A), JsonLogic (B), Custom (C)

**Expanded options (server-side):**

| Option | Engine | Format | Strengths | Concerns |
|--------|--------|--------|-----------|----------|
| 9A | Drools standalone | DRL + DMN | Most mature, DRL is LLM-friendly, CEP for SPC reactions | No workflow orchestration, manual Spring config |
| 9B | Flowable (DMN only) | DMN | Spring-native starter, embeds in JAR, Apache 2.0 | Less complete FEEL than Drools, no CEP |
| 9C | Flowable (full) | BPMN + DMN + CMMN | Rules + workflow + case management in one | Larger dependency footprint |
| 9D | KIE Full (Kogito+Drools+jBPM) | DRL + DMN + BPMN | Maximum power, CEP | Quarkus-preferred, heavier platform |
| 9E | Drools + Flowable | DRL/DMN (rules) + BPMN/CMMN (workflow) | Best-of-breed combination | Two engines to maintain |

### Remaining Decisions (Unchanged)

| # | Decision | Recommended | Notes |
|---|----------|-------------|-------|
| 3 | Single-tenant? | Holds | No change |
| 4 | Azure Functions? | Scoped for AI/OCR | No change |
| 5 | JSON columns for form data? | Scoped exception (Option B) | Depends on checklist variability |
| 7 | Dynamic form complexity? | Field registry (Option B) | No full form engine in v1 |
| 8 | Audit depth? | Temporal + app events (Option B) | Rules engine adds rule execution audit trail |
| 10 | LLM role? | Both, scoped | Document Intelligence + Azure OpenAI |
| 11 | Quality Forms Module design? | Modify existing (Option B) or redesign hybrid (Option C) | Depends on Decision 5 |

---

## 9. Open Decisions for Discussion

### DECISION A: Which Rules/Decision Platform?

**The most important decision.** Determines the foundation for the entire operations platform.

| Option | Best For | Risk |
|--------|----------|------|
| **Flowable (full BPMN+DMN+CMMN)** | Spring-native, embedded JAR, workflow + rules + case management. Best fit for Azure App Service. | Less powerful DMN/FEEL than Drools. No CEP. |
| **Drools standalone + custom workflows** | Most powerful rules engine. Best DRL for agents. CEP for SPC reactions. | No workflow orchestration. You build what Flowable/jBPM give you. |
| **KIE Full (Drools+jBPM)** | Maximum power. Rules + workflows. CEP. | Quarkus-preferred. Heavier platform. |
| **Drools (rules) + Flowable (workflow)** | Best-of-breed. Drools power for rules, Flowable for orchestration+CMMN. | Two engines to learn and integrate. |

**Question for colleague:** Which of these aligns best with your Java experience? Have you worked with any of these?

### DECISION B: Quarkus vs Spring Boot?

If KIE Full (Option A) is chosen, Quarkus is the preferred runtime. This would mean the API is Quarkus-based, not Spring Boot.

| | Spring Boot | Quarkus |
|---|-------------|---------|
| KIE support | Secondary | Primary |
| Colleague familiarity | Likely higher | Unknown |
| Azure App Service | First-class | Needs custom runtime or containers |
| Community/ecosystem | Massive | Growing but smaller |
| Agent-generated code | More training data | Less training data |

**Question for colleague:** Are you comfortable with Quarkus, or is Spring Boot strongly preferred?

### DECISION C: Azure Deployment Model

| Model | When to Choose | Complexity |
|-------|---------------|-----------|
| Azure App Service (JAR) | Flowable, Drools standalone, Spring Modulith | Lowest |
| Azure Container Apps | KIE Full with ancillary services | Medium |
| AKS (Kubernetes) | Full Kogito platform | Highest |

User confirmed "anything Azure/Microsoft is on the table" — but simpler is better unless there's a compelling reason.

### DECISION D: Client-Side Rules Format

How to handle the browser-side form UX rules:

| Option | Format | Pros | Cons |
|--------|--------|------|------|
| json-rules-engine | JSON | Proven, lightweight, React integration documented | Different format than server-side DMN/DRL |
| dmn-eval-js | DMN | Same format as server-side | Only supports Simple FEEL, limited hit policies |
| Custom thin evaluator | JSON | Tailored to your needs | Custom code to maintain |

### DECISION E: APQP-PPAP Migration Timing

| Option | When | Risk |
|--------|------|------|
| v1.0 (now) | Include in current milestone | Scope creep. Already 8 phases. |
| v1.1 (next milestone) | After quality system is live | Power Apps continues as-is for 6+ months |
| v2.0 (later) | After platform proves out | Longest delay but lowest risk |

### DECISION F: Team Readiness

| Question | Why It Matters |
|----------|---------------|
| Does colleague know Drools/KIE? | If yes, strong signal toward KIE stack |
| Does colleague know Flowable/Activiti? | If yes, strong signal toward Flowable |
| Does colleague prefer Eclipse or IntelliJ? | Flowable has better IntelliJ plugins; KIE has Eclipse-based tooling |
| Is colleague comfortable with DRL syntax? | If not, DMN-only (Flowable) may be preferred |

---

## 10. Recommended Architecture

Pending discussion with colleague, here is the recommended starting position:

### Primary Recommendation: Flowable (Full Stack)

```
Client (Next.js / Browser)
  json-rules-engine — form UX rules (show/hide, validation, wizard gating)
  |
  v (HTTP/REST)
Server (Spring Boot / Java 21)
  Flowable BPMN Engine — workflow orchestration (NCR lifecycle, CAPA, APQP gates)
  Flowable DMN Engine — decision tables (disposition, escalation, compliance)
  Flowable CMMN Engine — case management (investigations, complaints)
  Drools (optional) — complex rule chains, CEP for SPC reactions
  MyBatis — stored procedure calls (data access)
  |
  v (JDBC)
Database (Azure SQL)
  T-SQL stored procedures — data integrity enforcement
  DMN/rule definitions stored as versioned records — audit trail
```

**Why Flowable as primary:**
1. Only option with BPMN + DMN + CMMN (quality investigations are cases)
2. Native Spring Boot starters — add dependency and it works
3. Embeds in a JAR — deploys on Azure App Service
4. Apache 2.0 — no licensing risk
5. Active development (7.1.x, Flowable 8 on the roadmap)

**Why Drools as optional complement:**
- If you need complex rule chaining beyond what DMN decision tables support
- If you need CEP for SPC-style real-time event processing
- Can be added later without replacing Flowable

### Alternative: If Colleague Prefers Drools/KIE

```
Same architecture, but replace Flowable with:
  Drools — rules (DRL + DMN)
  jBPM — workflow orchestration (BPMN)
  No CMMN — build case management patterns manually
```

This works. It's more powerful for rules. Less elegant for case management. Heavier platform commitment.

---

## 11. Validation Spike Proposal

Before committing to any platform, build a small proof-of-concept:

### Spike Scope

1. **Spring Boot 3.4 app** with chosen engine (Flowable recommended)
2. **One DMN decision table:** NCR severity (Critical/Major/Minor) + Customer type (Automotive/Commercial) -> Escalation path + Required actions + SLA hours
3. **One BPMN process:** Simplified NCR lifecycle (Created -> Under Review -> Disposition -> Closed) with a DMN decision node for escalation
4. **One CMMN case** (if Flowable): NCR investigation with optional activities (root cause analysis, containment, corrective action)
5. **Deploy to Azure App Service** as a JAR
6. **Test agent authorability:** Can Claude/agents generate valid DRL/DMN/BPMN definitions?

### Spike Success Criteria

- [ ] Engine starts within Spring Boot app without errors
- [ ] DMN decision table evaluates correctly with test inputs
- [ ] BPMN process advances through states correctly
- [ ] Audit trail captures decision inputs/outputs
- [ ] Deploys to Azure App Service and runs
- [ ] Agent can generate a new DMN decision table from a plain-English spec

### Spike Duration

2-3 days with agent-assisted development.

---

## 12. Sources

### Spring Boot Migration
- [Azure App Service Java deployment](https://learn.microsoft.com/en-us/azure/app-service/configure-language-java-deploy-run)
- [MyBatis Spring Boot Starter](https://mybatis.org/spring-boot-starter/mybatis-spring-boot-autoconfigure/)
- [springdoc-openapi](https://springdoc.org/)
- [Resilience4j Spring Boot 3](https://resilience4j.readme.io/docs/getting-started-3)

### Rules Engines
- [Apache KIE Kogito Documentation](https://kie.apache.org/docs/10.1.x/kogito/)
- [Apache Drools with Spring Boot 3](https://medium.com/@yangli136/apache-drools-with-spring-boot-3-84a0b2735ed0)
- [Drools Spring Integration (Baeldung)](https://www.baeldung.com/drools-spring-integration)
- [Drools DMN Documentation](https://docs.drools.org/latest/drools-docs/drools/DMN/index.html)
- [Drools-LLM Integration (GitHub)](https://github.com/mariofusco/quarkus-drools-llm)
- [Flowable Open Source](https://www.flowable.com/open-source)
- [Flowable Spring Boot Docs](https://www.flowable.com/open-source/docs/bpmn/ch05a-Spring-Boot)
- [Flowable GitHub (8k stars)](https://github.com/flowable/flowable-engine)
- [Flowable Manufacturing Solutions](https://www.flowable.com/solutions/manufacturing)
- [Flowable BPMN/CMMN/DMN](https://flowable.com/trilogy-of-bpmn-cmmn-and-dmn/)
- [Camunda 8 Licensing (Commercial)](https://camunda.com/blog/2024/04/licensing-update-camunda-8-self-managed/)
- [Easy Rules (Maintenance Mode)](https://github.com/j-easy/easy-rules)
- [OpenL Tablets](https://openl-tablets.org/)
- [Spring Modulith 2.0](https://spring.io/projects/spring-modulith/)
- [jMolecules 2.0](https://github.com/xmolecules/jmolecules)
- [json-rules-engine (npm)](https://www.npmjs.com/package/json-rules-engine)
- [dmn-eval-js (browser DMN)](https://www.npmjs.com/package/@hbtgmbh/dmn-eval-js)
- [Top Java Rule Engines 2026 (Nected)](https://www.nected.ai/blog/java-rule-engines)
- [Java Rule Engines (Baeldung)](https://www.baeldung.com/java-rule-engines)

### Manufacturing & Compliance
- [Audi Chooses Camunda](https://camunda.com/press_release/audi-chooses-camunda-to-boost-operational-efficiency/)
- [Camunda Manufacturing & Automotive](https://camunda.com/solutions/industry/manufacturing-automotive/)
- [IATF 16949 Record Retention](https://preteshbiswas.com/2023/07/13/iatf-169492016-clause-7-5-3-2-1-record-retention/)
- [IATF 16949 Control Plan](https://preteshbiswas.com/2023/07/31/iatf-169492016-clause-8-5-1-1-control-plan/)
- [IATF 16949 Mandatory Documents](https://advisera.com/16949academy/knowledgebase/list-of-mandatory-documents-required-by-iatf-16949-2016/)
- [Omnex APQP Manager](https://www.omnexsystems.com/products/apqp-ppap-manager-software)
- [AIAG Core Tools Software](https://www.aiag.org/expertise-areas/data/core-tools-software)
- [DataLyzer FMEA+SPC](https://datalyzer.com/)
- [InfinityQS SPC Alarm Rules](https://help.infinityqs.com/help/en/ProFicient/Content/SPCMI/AlarmRuleAssignments/ManagingAlarmRuleAssignments.htm)
- [Western Electric Rules](https://en.wikipedia.org/wiki/Western_Electric_rules)

---

*Created: 2026-02-27 — For review with Java colleague before Phase 1 adjudication*
*This document supersedes the narrower rules engine todo at `.planning/todos/pending/2026-02-27-rules-engine-*.md`*
