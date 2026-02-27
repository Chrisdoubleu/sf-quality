---
created: 2026-02-27T13:15:26.732Z
title: Rules engine and decision platform architecture for unified operations system
area: planning
files:
  - .planning/ROADMAP.md
  - .planning/PROJECT.md
  - .planning/REQUIREMENTS.md
  - .planning/research/json-rules-engine-integration-research.md
  - .planning/research/spring-boot-migration-research.md
  - Reference_Architecture/Forms_Research_Consolidation/02_synthesis/DECISION_BRIEF.md
---

## Problem

The sf-quality project is the first vertical in a broader unified business operations platform for Select Finishing (custom coating company). The rules/decision engine choice made now becomes foundational infrastructure for the entire platform — not just quality forms conditional logic.

### Broader Platform Context

Select Finishing's systems landscape:
- **EPICOR** (in implementation) — supply chain, EDI, finance
- **Dayforce** — HR, workforce management
- **APQP-PPAP System** (currently Power Apps / Dataverse at `C:\Users\ChrisWalsh\OneDrive - Select Finishing\APQP-PPAP-System`) — program launch management, part approval, OEM spec tracking. **Candidate for migration** into the Spring Boot / rules platform.
- **This platform** — everything else operational

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

### Types of Rules Across All Domains

| Rule Type | Examples | Complexity |
|-----------|----------|-----------|
| Form UX | Show/hide fields, conditional validation, wizard step gating | Simple conditions |
| Specification Matching | OEM X requires 18-25 µm e-coat, 480 hr salt spray, ASTM B117 | Lookup + threshold |
| Process Control | Bath chemistry out of spec → alert, oven temp deviation → hold parts | Real-time threshold + escalation |
| Workflow Routing | NCR severity + plant + customer → escalation path + required actions + SLA | Multi-factor decision tree |
| Compliance | Part X for OEM Y requires Nadcap cert + specific PPAP level + these test methods | Multi-entity rule chains |
| APQP Gating | Phase transition requires: all deliverables complete, all risks mitigated, customer sign-off | Checklist + state machine |
| Disposition / Recommendation | Given defect type, severity, customer, part history → recommend disposition | Complex multi-factor with historical context |
| Supplier Scoring | Delivery performance + quality metrics + corrective action history → risk rating | Aggregation + scoring model |
| SPC Alerting | Control chart violations (Western Electric rules, Nelson rules) → notification + auto-hold | Statistical rules |
| Cross-domain Orchestration | New program launch triggers: quality plan creation, inspection template setup, equipment calibration schedule, training requirements | Orchestration across domains |

### Key Insight: Rules Don't Stay Within One Domain

A program launch touches quality, production, maintenance, training, and compliance simultaneously. A critical NCR might trigger a CAPA, a supplier corrective action, a customer notification, a production hold, and an APQP re-evaluation — all from one event. The rules engine must handle cross-domain orchestration.

## Three Approaches Evaluated

### Approach A: Kogito / Drools / jBPM (Full KIE Platform) — RECOMMENDED

The complete Apache KIE stack as the operational decision and process platform.

- **Drools** (DRL + DMN decision tables) — all business rules
- **jBPM** (BPMN 2.0) — all process orchestration (NCR lifecycle, CAPA workflows, APQP phase gates, program launches)
- **Kogito** — cloud-native runtime, auto-generated REST APIs
- **json-rules-engine** on the client — form UX only (show/hide fields, client-side validation)

Pros:
- Only option that natively handles both rules AND process orchestration
- DMN decision tables model OEM specification matrices perfectly
- jBPM handles cross-domain workflows natively
- Auditable by design — every rule evaluation and process step logged
- Active development (Apache KIE 10.x, 2026)
- APQP phase gating maps directly to BPMN process milestones

Cons:
- Platform commitment — becomes core infrastructure
- Spring Boot is supported but Quarkus is preferred runtime
- KIE ecosystem in Apache incubation — governance transition
- Needs validation spike for Spring Boot compatibility

### Approach B: Drools Standalone + Custom Orchestration

Drools embedded in Spring Boot for rules only. Workflow orchestration via Spring State Machine or custom code. json-rules-engine for client-side form UX.

Pros:
- Lower commitment than full KIE
- DMN decision tables still work
- Standard Spring Boot JAR deployment

Cons:
- You'll eventually build a process orchestration layer anyway
- Spring State Machine is limited for complex cross-domain workflows
- Building what Approach A gives you out of the box

### Approach C: json-rules-engine Everywhere (Lightweight)

json-rules-engine on client + server (via GraalVM polyglot or Java port). Rules as JSON in database.

Pros:
- Simplest architecture, one rule format
- No DRL/DMN learning curve

Cons:
- Doesn't scale to full decision automation (no forward chaining, no decision tables, no process orchestration)
- Would hit a ceiling with complex multi-entity decisions
- You'd end up building a rules engine and workflow engine — poorly

## Open Decisions

### 1. Kogito Spring Boot Compatibility (BLOCKING)
Kogito's preferred runtime is Quarkus, not Spring Boot. Need to validate that the Spring Boot experience is production-quality. Options if it's not:
- **Switch to Quarkus** instead of Spring Boot (colleague needs to weigh in)
- **Use Drools standalone** (no Kogito wrapper) on Spring Boot — lose auto-generated REST endpoints and process orchestration convenience

### 2. Quarkus vs Spring Boot
If Kogito works better on Quarkus, is the team willing to use Quarkus instead of Spring Boot? The colleague is Java-skilled; agents write the code. This may not be a blocker but needs a deliberate decision.

### 3. Azure Deployment Model
Kogito is Kubernetes-native. Deployment options on Azure:
- **Azure App Service** (JAR deployment) — simplest, currently planned
- **Azure Container Apps** (serverless containers) — middle ground
- **AKS** (Azure Kubernetes Service) — Kogito's sweet spot but more infrastructure

User confirmed "anything Azure/Microsoft is on the table."

### 4. Impact on Decision Brief Decisions 1, 2, 6, 9
The Spring Boot migration (already decided) plus Kogito/Drools changes the answers to several Phase 1 adjudication decisions:

- **Decision 1 (Where does business logic live?):** Split boundary still holds, but now it's TypeScript (form UX) / Drools (business rules + decisions) / T-SQL (data integrity). Three layers, not two.
- **Decision 2 (What happens to C# API?):** Already decided — Spring Boot replaces C#. Kogito/Drools adds a rules layer inside the Spring Boot app.
- **Decision 6 (Conditional logic approach?):** Becomes a dual-engine answer: json-rules-engine client-side for form UX + Drools/DMN server-side for business rules. Not either/or.
- **Decision 9 (Which rules engine?):** Drools/DMN (server) + json-rules-engine (client), not json-rules-engine alone.

### 5. APQP-PPAP System Migration
The APQP-PPAP system is currently Power Apps / Dataverse (knowledge base + JSONL seed data, ~30% mature). User is open to migrating it into the Spring Boot / Kogito platform. This needs scoping:
- When? (v1.0 or later milestone)
- What migrates? (Just the APQP tracking, or the knowledge base analysis workflow too?)
- Dataverse entities → Azure SQL tables mapping

### 6. Team & Agents
- User will use agents to write code — learning curve is not a human concern
- Colleague is Java-skilled, may or may not know KIE/Drools specifically — **needs confirmation**
- Agent-friendliness of DRL/DMN/BPMN is an open question worth validating

### 7. Recommended Next Step: Validation Spike
Before committing to Kogito/KIE as the platform, build a small spike:
1. Spring Boot app with Kogito Spring Boot starter
2. One DMN decision table (e.g., NCR severity + customer → escalation path)
3. One simple BPMN process (e.g., NCR lifecycle state machine)
4. Deploy to Azure (App Service or Container Apps)
5. Validate: Does it work? Is the developer experience acceptable? Do agents produce good DRL/DMN?

## Solution

**Recommended: Approach A (Kogito / Drools / jBPM) with validation spike before full commitment.**

Rationale:
- The platform scope (10+ operational domains, cross-domain orchestration, full decision automation) demands a real decision platform, not a lightweight rules library
- Kogito/KIE is the only option that provides rules + decisions + process orchestration in one stack
- The "rules are the product" framing for a manufacturing operations platform aligns with what KIE was built for
- Risk is mitigated by the validation spike — if Spring Boot experience is poor, fall back to Drools standalone (Approach B) or evaluate Quarkus

This todo captures the full discussion context. The next action is either:
1. Run the validation spike (could be a new phase or pre-phase task)
2. Discuss with colleague re: Quarkus vs Spring Boot preference and KIE experience
3. Continue with Phase 1 adjudication, updating Decisions 1/2/6/9 with this new context
