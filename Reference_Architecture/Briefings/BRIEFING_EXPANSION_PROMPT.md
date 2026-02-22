# Architectural Briefing Expansion Prompt

**Purpose:** Self-contained prompt for an AI with no codebase access to expand an incomplete architectural briefing from 2-spec coverage to comprehensive 4-spec + hidden patterns coverage. The briefing should synthesize four JSON specifications and three reverse-engineered hidden patterns into a single accessible narrative that orients engineers and AI agents on the full platform architecture.

---

## The Prompt

You are a **Senior Technical Writer and Enterprise Systems Architect** with 20 years of experience producing architectural documentation for complex enterprise platforms. Your specialty is taking dense, structured technical specifications (JSON schemas, API docs, security models) and synthesizing them into clear, well-organized narrative documents that engineering teams actually read and reference. You have deep expertise in:

- REST API architecture and integration patterns (resource-oriented design, delta sync, pagination, rate limiting)
- Security architecture documentation (RBAC, layered authorization, field-level access control)
- Workflow and orchestration engine design (DAG-based workflows, typed node systems, expression DSLs)
- Enterprise integration patterns (event-driven, webhook, two-phase retrieval, validate-only)
- Making complex multi-system architectures accessible to both human engineers and AI coding agents
- Automotive quality management systems (IATF 16949, 8D methodology, CAPA, SCAR, NCR lifecycle)

You are reviewing an existing architectural briefing document that was written early in a project's lifecycle. At the time of writing, the project had only two reference specifications. Since then, two additional specifications and a reverse-engineered hidden patterns document have been added to the reference architecture package. The briefing is now incomplete — it covers only 2 of 4 core specifications and contains some implied patterns that contradict the project's architectural constraints.

Your job is to **expand and revise** the briefing into a comprehensive narrative that covers the full reference architecture, while:

1. **Preserving the tone and depth** of the existing Security and Workflow sections — they set the quality bar
2. **Adding equivalent coverage** for the API Integration Architecture spec
3. **Adding coverage** for the three Hidden Architecture Patterns (Guided Process Orchestration, Policy Resolution Engine, Data Staging / Edit Mode)
4. **Expanding the "How These Systems Interact" section** from a 2-system interaction model to a full 4-system + hidden patterns interaction model
5. **Fixing the "Database Architecture Patterns Implied" section** — removing patterns that conflict with constraints (multi-tenant schema isolation, polymorphic entity properties / EAV) and adding patterns implied by the API and Hidden Patterns specs
6. **Updating the "Summary for an Agentic Coding Agent" section** to reflect all specifications, not just Security and Workflow
7. **Grounding all new content** in the target system's quality management domain with concrete examples

### Output Format

Produce the expanded briefing as a complete Markdown document that could replace the existing one. Use the same section structure and style as the existing briefing, expanded to cover the full scope. The document should include:

```
# Architectural Briefing: Enterprise Platform Reference Architecture

## What These Files Are
[Updated to reference all 4 specs + hidden patterns]

## Document 1: Security & Role Architecture
[Preserve existing content — only minor edits for consistency]

## Document 2: Workflow Engine Architecture
[Preserve existing content — only minor edits for consistency]

## Document 3: API & Integration Architecture (NEW)
[Same depth and structure as Documents 1 and 2]

### What It Covers
### Software Engineering Domains Covered
  1. Resource-Oriented REST Design
  2. Entity Identification and Temporal Model
  3. Two-Phase Retrieval Pattern
  4. Delta Synchronization Architecture
  5. Write Operations and Validate-Only Mode
  6. Cursor-Based Pagination and Query Governor
  7. Event and Notification System
  8. Workflow Validation Integration
  9. Rate Limiting and Consumer Design
  10. Data Model Topology
### Cross-Cutting API Patterns

## Document 4: Hidden Architecture Patterns (NEW)
[Narrative synthesis of the three reverse-engineered patterns]

### What These Patterns Are and How They Were Discovered
### Pattern 1: Guided Process Orchestration
### Pattern 2: Policy Resolution Engine
### Pattern 3: Data Staging and Edit Mode Architecture
### The Cross-Pattern Pipeline

## How All Four Systems Interact
[Expanded from the current 2-system interaction model to show how Security + Workflow + API + Hidden Patterns form a complete platform architecture. Include quality management examples.]

## Database Architecture Patterns Implied
[Revised: remove multi-tenant schema and polymorphic entity properties (EAV). Add patterns implied by API spec (delta sync infrastructure, rate limiting, XRefCode dual-key identity) and hidden patterns (staging tables, policy resolution tables, guided process tracking). Keep patterns that remain valid.]

## Summary for an Agentic Coding Agent
[Expanded to cover all 4 specs + hidden patterns. 15-20 numbered principles, not just 10.]
```

---

## The Existing Briefing (Full Text)

Below is the current briefing document in its entirety. Preserve the quality and depth of the Security and Workflow sections. Fix the issues noted in the task description.

```markdown
# Architectural Briefing: Security & Workflow Engine Reference Documents

## What These Files Are

These two JSON documents are **platform-agnostic architectural specifications** — blueprints that describe, in complete detail, two foundational subsystems of a multi-tenant enterprise SaaS application. They were derived from a real-world HRIS platform but have been abstracted so the patterns are reusable in any domain.

Together they define **how users get access to things** and **how changes move through approval chains before they become real**. Almost every enterprise application needs both of these systems, and these documents describe them at production-grade depth.

---

## Document 1: Security & Role Architecture

### What It Covers

This is a **complete identity, authorization, and access control specification** spanning 10 distinct security layers that stack on top of each other. Think of it as the answer to the question: *"When a user clicks a button, what are ALL the things the system checks before allowing it?"*

### Software Engineering Domains Covered

**1. Identity & Authentication (IAM)**
- User account management with configurable username generation (token-based algorithms like `{FIRST}.{LAST}`)
- Three authentication modes: native (password), SSO (external IdP), and hybrid (SSO with native fallback)
- Password policy engine with complexity rules, rotation schedules, lockout thresholds, history tracking, and priority-based policy resolution when multiple policies apply
- Multi-factor authentication with ranked preference (TOTP > Email > Push > SMS) and failure mode configuration (open vs. closed when MFA provider is down)
- Self-service account recovery with forced verification prompts
- Lifecycle roles: pre-activation, self-service (ESS), and deactivation roles that auto-assign when accounts are terminated

**2. Role-Based Access Control (RBAC) with Hierarchical Inheritance**
- Roles organized in a **parent-child tree** — a child role can never exceed the permissions of its parent
- Each role is a composite of: feature access + data authorizations + API field access + organizational scope + password policy + parameterized behavior
- Role properties include flags for self-service, deactivation, delegation exclusion, SSO override, and record anonymization
- Operational hardening principles: least privilege, just-in-time access, separation of duties, periodic review, MFA for elevated roles

**3. Feature Access Control (UI Entitlements)**
- A **tree-structured whitelist** of application features (screens, tabs, modules, config panels)
- Two feature types: Navigation Panel Features (menu items/screens) and Feature Components (tabs, sections, toggles within a parent feature)
- Parent features must be enabled before children; empty containers are rejected by validation
- **Feature parameterization** — the same feature can behave differently per role (e.g., different default date ranges, result limits, lookback periods)
- Feature ordering is configurable per role (drag-and-drop reordering)
- Favorite features (up to 6 pinned to home screen per role)

**4. Data Authorization (CRUD Permissions)**
- CRUD-level permissions (Create, Read, Update, Delete) on **data categories**, independent of feature access
- A user may access a screen but be restricted from certain data types within it
- Two scope models: Administrator View (all records except own) and Supervisor View (only records under own position in hierarchy)
- Authorizations cascade through the role hierarchy — children can't exceed parents

**5. Field-Level API Access Control**
- A separate permission layer specifically for API/web-service channels
- Checkbox tree of every API-exposed data entity and field
- Allows fine-grained filtering so integration accounts only see the exact fields they need, even if their role has broader read authorization
- Critical for preventing data over-exposure through system-to-system channels

**6. Organizational Scoping (Multi-Level Entity Hierarchy)**
- A configurable **tree-structured organizational model** with levels: Root → Region → District → Site → Zone → Unit → On-Site Unit
- Custom levels can be added
- This hierarchy is the **backbone of data visibility** — users only see records within their assigned organizational entities
- Entity properties include: name, parent, effective dates, reference code, timezone, ledger code, clock code
- Entity lifecycle: opening (future-dated creation), closing (deactivate but retain), moving (re-parent), with validation guards against orphaning active assignments

**7. Structural Hierarchy Management (Positions & Business Units)**
- A **functional hierarchy** (reporting structure) separate from the organizational hierarchy (locations)
- Business units track headcount metrics (total, filled, vacant) with rollup aggregation
- Positions represent approved headcount slots with properties: FTE, pooled/single, interim support, frozen
- Occupancy models: primary (one per user), secondary (multiple), interim (temporary overlay), overfill (transition overlap), pooled (multi-occupant)
- Solid-line (direct supervisor) and dotted-line (alternate supervisor) relationships, all effective-dated
- Hybrid mode supports phased rollout where some users are in the structural model and others use flat role assignments

**8. Network Access Control**
- IP-based restrictions that limit which source addresses can access the platform
- Recommended for API/integration accounts (fixed IPs); cautioned for user access (remote workforce issues)

**9. Integration & Data Security**
- Dedicated non-human accounts and roles for each external integration
- Token-based auth preferred over username/password
- PGP encryption for outbound data
- SFTP account management with rotation policies
- Encryption at rest and in transit
- Data minimization tools: configurable retention periods, automated purging, anonymization capabilities
- Privacy compliance: GDPR, CCPA/CPRA, PIPEDA data subject request support

**10. Monitoring & Audit**
- Record-level audit trails (who changed what, when)
- Session overview reports with login/logout timestamps, IP addresses, applied policies
- Suspicious behavior indicators: failed login bursts followed by profile changes, simultaneous multi-IP sessions
- Recommended audit scope: security events, policy config changes, confidential data changes, privilege escalations

### Cross-Cutting Patterns

These patterns appear everywhere in the system and are important for an agent to understand:

- **Reference Codes**: Every configurable entity has a unique string identifier used for cross-system integration, import/export, and API interactions. No special characters, no spaces.
- **Effective Dating**: Most entities support `Effective From` / `Effective To` dates, enabling future-dated changes and historical views.
- **Localization**: Names and descriptions support per-language variants with fallback to organization default.
- **Audit Trail**: All modifications logged with actor, change, and timestamp.
- **Background Processes**: Async jobs for data sync, hierarchy integrity checks, auto-role reassignment on deactivation.
- **Import/Export Pattern**: CSV-based with strict header ordering, no deletes, reference code matching for relational fields.
- **Configuration Portability**: Role configs exportable as `.dat` files for promotion across environments (dev → staging → prod). Import creates or updates based on reference code matching.

### The Security Equation

The document culminates in a formal access equation:

```
Effective Access = Authentication
                 × Role Features
                 ∩ Data Authorizations
                 ∩ Organizational Scope
                 ∩ Field-Level API Filters
                 ∩ Network Restrictions
```

Security is **subtractive by default** — a user has zero access until each layer explicitly grants something. All layers must independently permit an action.

---

## Document 2: Workflow Engine Architecture

### What It Covers

This is a **complete specification for a graph-based, form-driven workflow orchestration engine** — the system that routes form submissions through approval chains, conditional branching, notifications, and data commits. It answers: *"When someone submits a change, who needs to approve it, what logic decides the routing, and what happens when it's done?"*

### Software Engineering Domains Covered

**1. Graph-Based Workflow Design (Directed Graph / State Machine)**
- Workflows are **directed acyclic graphs** (with controlled looping) composed of 9 typed node kinds and directional links
- Visual canvas-based editor with drag-and-drop, copy/paste, undo/redo, zoom, rotation
- Each node type has strict constraints on incoming/outgoing link counts and valid predecessor/successor types
- The graph is validated on save — the engine rejects invalid topologies

**Node Types (the complete vocabulary):**

| Node | Purpose | Pauses Execution? |
|------|---------|-------------------|
| **Start** | Single entry point; configures loop protection (max iterations) and error routing | No |
| **End** | Terminal node; marks completion | No |
| **Routing** | Resolves WHO receives the next action; traverses org/supervisory hierarchies | No |
| **Decision** | Human decision point (approve/reject/resubmit); pauses until response or timeout | **Yes** |
| **Process** | Commits the form data to the database; makes pending data real | No |
| **Notification** | Fire-and-forget message to recipients; no pause | No |
| **Condition** | Evaluates boolean expression; binary branching (True/False) | No |
| **Domain Event Trigger** | Fires a domain event to trigger downstream workflows (webhook/callback equivalent) | No |
| **Note** | Human-readable annotation; not part of execution | N/A |

**2. Dynamic Routing Engine (Hierarchy-Aware Resolution)**

The routing system is one of the most architecturally significant components. It resolves recipients **dynamically at runtime** by traversing organizational and supervisory hierarchies:

- **13 routing target types** including: specific user, submitter, affected record owner, authority type relative to record (hierarchy walk), role relative to record (supervisory or org hierarchy walk), supervisor at configurable relative level, future supervisor (resolves unrealized assignments), position supervisor
- **Early termination**: hierarchy traversal stops at the first level where a qualifying recipient is found
- **First-responder semantics**: when multiple recipients receive a decision, the first response wins; others are cancelled
- **Effective date routing**: can resolve recipients based on a future date on the form rather than current date
- **Fallback behavior**: configurable — continue to default recipient or error when no match found

**3. Expression Engine (Conditional Logic)**

A rich expression language embedded in Condition nodes:

- **Field references** via `<<FieldName>>` token syntax, including nested list access (`<<List_Entity.Item.Field>>`)
- **Operators**: Equals, NotEquals, GreaterThan, LessThan, Contains, StartsWith, AND, OR, NOT, IS NULL, COALESCE
- **List operations**: Filter, Any, All, None — can be chained for complex collection queries
- **Update status evaluation**: branch based on whether a record is being inserted, updated, or deleted
- **Named functions**: Coalesce, ConvertToDate, Count, Current, Today, GetEntityPropertyValue, HasRole, HasAuthorityType, IdFromXref (cross-reference lookup against 100+ data stores), LoadIfEmpty (evaluate system state not on the form), HasCurrentPrimaryChanged, HasFutureRecord, HasPositionPropertyChanged
- **100+ data providers** available for cross-reference lookups spanning organizational entities, roles, user properties, financial configs, policies, statuses, and documents

**4. Form Binding & Access Control**

- Forms are the data-entry artifacts; workflows define what happens after submission
- One form → one workflow binding, but the binding is **role-scoped** (same form can trigger different workflows for different roles)
- Decision nodes can **override the form** shown to approvers, auto-populating common fields
- Guided Processes bundle multiple forms into a step-by-step wizard with per-form workflow binding, skip support, and lifecycle tracking (open → completed)
- Form placement is configurable — admins choose which application module surfaces the form

**5. Event System (Workflow Chaining / Pub-Sub)**

- Domain events chain workflows together in a **pub-sub pattern**
- When a form is processed by one workflow, it can fire events that trigger secondary workflows
- Custom events are fully configurable; template events are system-provided with limited editability
- Execution is **sequential** (not parallel) when multiple workflows subscribe to the same event
- Events can also be triggered by bulk data imports, with configurable lookback periods and once-per-record deduplication

**6. Message Templates (Token-Based Notifications)**

- Decision requests, notifications, and error messages use `<<Token>>` syntax for dynamic data insertion
- `Lookup()` function resolves foreign key IDs to human-readable names
- Sensitive data masking by default with `Unmask()` override
- Rich text support (fonts, colors, hyperlinks)
- Full localization with per-language variants and recipient-preferred language delivery

**7. Timeout & Auto-Resolution (SLA Enforcement)**

- Decision nodes support configurable timeout values (in minutes) with up to 10 retries
- Three common timeout patterns: auto-approve, auto-reject, or reroute to escalated approver
- Prevents workflows from stalling indefinitely

**8. Electronic Signature Integration**

- External e-signature provider integration (envelope-based model)
- Multiple authentication methods: access code, SMS, KBA, ID verification, phone
- Template-based field definition (signature, initials, date fields)
- Supplemental document attachment

**9. Workflow Lifecycle & Immutability**

- Three states: **Draft** (fully editable), **Active** (graph frozen, properties mutable), **System** (read-only)
- Once a workflow has been executed even once, its topology (nodes, links, connections) is permanently frozen
- Only node properties (messages, routing targets, timeouts) can be modified after execution
- This immutability protects the integrity of approval chains that have already been used
- Copy operation creates a new draft that's fully editable

### Security Hardening Rules

- **Self-approval prevention**: Never route approval decisions back to the submitter
- **Post-approval notification**: Always notify the affected record owner after changes are committed
- **Form visibility control**: Use `can_see_self` flags and form overrides to mask sensitive data from approvers
- **Immutability protection**: Prevents retroactive tampering with used approval chains

---

## How These Two Systems Interact

The security architecture (Document 1) and the workflow engine (Document 2) are tightly integrated:

1. **Role-scoped form access**: Which forms a user can submit is controlled by the RBAC system
2. **Hierarchy-aware routing**: The workflow engine traverses the organizational and supervisory hierarchies defined in the security architecture to resolve approval targets
3. **Data authorization in forms**: What fields a user sees on a form is governed by their role's data authorizations
4. **Workflow-driven security changes**: Changes to the organizational structure itself (adding positions, modifying hierarchy) flow through approval workflows before taking effect
5. **Feature gating of workflow admin**: Access to the workflow designer and administration screens is itself gated by the role feature tree

---

## Database Architecture Patterns Implied

> **Scope note:** The patterns below are implied by the reference platform (a multi-tenant SaaS system). Several do not apply to sf-quality's single-tenant constraints — specifically multi-tenant schema isolation, polymorphic entity properties (EAV), and application-layer encryption. See `README.md` constraints and `Pattern_Mapping.md` Appendix A for the authoritative exclusion list. The remaining patterns (temporal modeling, tree structures, audit tables, reference codes, junction tables, graph storage, state machines) are directly applicable.

These documents imply a specific database architecture an agent should understand:

- **Multi-tenant schema** with tenant isolation at the organizational hierarchy level
- **Effective-dated records** throughout (temporal data modeling with `from`/`to` date columns on most tables)
- **Tree structures** stored relationally: organizational hierarchy, role hierarchy, business unit hierarchy, position/supervisory hierarchy, feature tree — all using parent-child references
- **Polymorphic entity properties**: positions, business units, and users support custom property definitions with multiple data types
- **Audit tables**: shadow/history tables tracking every change with actor, timestamp, and before/after values
- **Reference code pattern**: a user-defined string identifier on every entity, used as the stable cross-system key (separate from auto-generated primary keys)
- **Junction/bridge tables**: role-to-feature assignments, role-to-authorization mappings, role-to-API-field access, form-to-workflow bindings, event-to-workflow subscriptions
- **Graph storage**: workflow definitions stored as node records + link records with foreign keys to source/target nodes and typed properties per node type
- **State machines**: workflow execution instances with per-node status tracking and execution history

---

## Summary for an Agentic Coding Agent

If you are an AI coding agent being given these documents as context for building or extending a system, here is what you need to internalize:

1. **Security is layered and subtractive.** Don't build flat permission checks. Build a pipeline of independent authorization layers that all must pass. Start from zero access and add.

2. **Hierarchies are everywhere.** Organizational trees, role trees, supervisory trees, feature trees — master tree traversal algorithms with early termination, effective-date awareness, and fallback logic.

3. **Everything is effective-dated.** Don't model entities as static records. Every meaningful entity has a validity window. Queries must be time-aware.

4. **Reference codes are the integration key.** Internal auto-increment IDs are for joins. Reference codes are for cross-system identity, import/export, and API contracts.

5. **Workflows are graphs, not code.** The business logic for approval chains lives in a visual graph structure, not in procedural code. Your job is to build the execution engine and the designer, not hardcode approval logic.

6. **Immutability protects integrity.** Once a workflow has been used, its structure is frozen. Build versioning and copy mechanics, not in-place editing of production graphs.

7. **Routing is dynamic and hierarchy-aware.** Recipients aren't hardcoded. The engine walks organizational and supervisory trees at runtime to find the right approver. Build the traversal algorithms to be configurable (which hierarchy, what role/authority, what level, what date).

8. **First-responder wins.** Multi-recipient decisions resolve on the first response. Build cancellation logic for the remaining pending decisions.

9. **Audit everything.** Every change to every entity gets logged. Build this into your data layer, not as an afterthought.

10. **Build for multi-tenancy.** Organizational scoping isn't optional. Every query, every UI render, every API response must be filtered by the requesting user's organizational scope.
```

---

## Source Material: API & Integration Architecture

Below are the key sections from the API Integration Architecture specification. These have been extracted from the full 53 KB JSON document. Use these to write Document 3 at the same depth as Documents 1 and 2.

### Architecture Overview

```json
{
  "summary": "A RESTful (and legacy SOAP) API layer that exposes a multi-tenant HCM platform's data model for system-to-system integration. The architecture follows a resource-oriented design where every domain entity is addressable via a canonical URL pattern, identified by cross-reference codes (XRefCodes), and secured through the platform's existing RBAC and field-level access controls. The API is designed for high-frequency, low-volume incremental synchronization — not bulk data transfer.",
  "core_architectural_decisions": [
    "Resource-oriented REST with JSON payloads (SOAP/XML maintained as legacy, frozen — no new development)",
    "XRefCode as the universal entity identifier across all API boundaries — not internal auto-increment IDs",
    "Two-step retrieval pattern: list XRefCodes first (cheap), then fetch details per XRefCode (secured and filtered)",
    "Temporal queries via ContextDate parameter — all data retrieval is point-in-time aware",
    "Delta synchronization by design — consumers must track their last successful request timestamp and query only for changes since that point",
    "Symmetric read/write payloads — the JSON structure returned by GET is the same structure accepted by POST/PATCH",
    "Platform security model enforced at API boundary — no separate API permission system exists; the same roles, features, authorizations, and field-level access that govern the UI also govern the API"
  ],
  "design_philosophy": "The API is not a data warehouse extraction tool. It is optimized for frequent, small, incremental data exchanges (hourly or more) rather than infrequent bulk transfers."
}
```

### URL Architecture

- **Pattern:** `https://{domain}/api/{clientNamespace}/V1/{Resource}`
- **Sub-resources:** `https://{domain}/api/{clientNamespace}/V1/{Resource}/{XRefCode}/{SubResource}`
- Version segment (`V1`) in URL path enables future versioning without breaking consumers
- Client namespace segment isolates tenant data at the URL level
- Client metadata endpoint provides service version and base URI for connectivity verification

### Authentication and Authorization at the API Boundary

**Authentication:** OAuth 2.0 Resource Owner Password Credentials (ROPC) flow with JWT tokens (1-hour lifetime, non-revocable). Basic auth supported but not preferred.

**Authorization layers enforced at API boundary (same stack as UI):**
1. **Feature Gating** — Role must have 'Web Services' feature enabled with specific sub-features (Read Data, Write Data)
2. **Data Authorization (CRUD)** — Role's access authorization rights determine which data categories the API can read, create, update, or delete. Missing Read authorization = fields omitted from GET responses.
3. **Field-Level API Access** — A *separate* field-level access control layer specifically for API channels. Even with broad Read authorization, individual fields can be unchecked, causing them to be stripped from API responses. Most granular control — operates at individual field level within each entity.
4. **Organizational Scope** — Role's organizational unit assignments bound which records are visible. API user scoped to 'Plant 4' never sees 'Plant 5' data regardless of query parameters.
5. **IP Restriction** — IP address restrictions applied to API traffic, blocking requests from unauthorized network origins.

**Key insight:** Report data security is governed by the report's own access authorization configuration, NOT by the field-level API access settings. A consumer may see different fields through a report endpoint than through a direct entity endpoint.

### Data Model Topology

The API exposes the platform's domain model as a graph of interconnected entities:

- **Central entity: Employee** — composite aggregate with master record + 40+ subordinate resource collections
- **Subordinate resources** are child collections accessible via sub-resource URLs, organized into categories: identity/demographics, employment/assignment, compensation/payroll, tax, security/access, talent/development, organization, documents
- **Temporal model:** Most subordinate resources contain effective-dated records with EffectiveStart/EffectiveEnd. API returns records effective as of a ContextDate (defaults to current datetime). ContextDateRangeFrom/To for range queries.
- **Expand parameter:** Controls which subordinate collections are included in a single GET — optimizes response size
- **Other core entities:** OrgUnit (hierarchical, parent-child), Department, Job, Position, Document (binary, Base64-encoded, document-type-secured)
- **Workforce management entities:** EmployeePunch, EmployeeRawPunch (before policy rules applied), EmployeeSchedule (31-day max query window), TimeAway (status-filterable: APPROVED, PENDING, CANCELED, DENIED, CANCELPENDING)
- **Reference/lookup entities:** ContactInformationTypes, EmploymentStatuses, PayClasses, PayTypes — all follow two-step XRefCode retrieval pattern
- **Entity relationship graph:** Employee is the hub. All workforce entities reference Employee, Department, Job, Position, OrgUnit, and Project via XRefCodes. OrgUnit and Project have self-referential parent-child hierarchies.

### API Interaction Patterns

**1. Two-Step Retrieval:**
- Step 1 (cheap): `GET /Resource` → array of XRefCode strings only, no field-level security applied
- Step 2 (secured): `GET /Resource/{XRefCode}` → full entity with all security layers applied
- Expand parameter to request only specific subordinate resources

**2. Delta Synchronization:**
- Consumer records start timestamp of each request cycle
- Query with `FilterUpdatedStartDate` / `FilterUpdatedEndDate` window
- Platform returns only entities where records were modified, became effective, or ended within the window
- `filterUpdatedEntities` parameter narrows change detection to specific entity types
- Cross-data-model search: changes to restricted entities still surface the parent entity in XRefCode list

**3. Batch Retrieval for Large Datasets:**
- Query governor: 1,000 entities per detail request (XRefCode listing not subject to governor)
- Consumer splits XRefCode list into batches of ≤900, processes sequentially

**4. Write Operations:**
- POST: create with consumer-generated XRefCode (platform rejects duplicates)
- PATCH: partial update (only changed fields needed); can also create new effective-dated subordinate records
- Symmetric payloads: GET response structure = POST/PATCH request structure
- Validate-only mode (`isValidateOnly=true`): runs all server-side validations without committing. "ALWAYS use during development and testing."

**5. Cursor-Based Pagination:**
- PageSize parameter with opaque `Paging.Next` continuation URL
- Termination when Paging.Next is absent/null
- For large-collection endpoints (punches, schedules, reports, pay summaries)

**6. Point-in-Time Queries:**
- ContextDate: returns record effective as of that date (defaults to current)
- ContextDateRangeFrom/To: all records effective within a range
- Non-effective-dated entities always return current data regardless

### Event and Notification System

**Event Notifications (Push/Pull):**
- Subscription-based: subscriber + event type combinations
- Events only detected when at least one active subscription exists
- Publisher cadence: once per hour
- Push mode: platform sends to consumer's HTTPS endpoint; consumer must acknowledge; failure queues subsequent events for that subscriber
- Pull mode: consumer polls platform; must explicitly acknowledge
- Notification payload: basic (event type, time) + detail (retrieved separately per-subscriber with security filtering)
- Ordering guarantee per subscriber; independent across subscribers

**Supported events:** Hire, Hire Cancel, Rehire, Rehire Cancel, Terminate, Terminate Cancel, Workflow Validation, Workflow Validation Cancel

**Workflow Validation Integration:**
- External systems participate in approval chains
- Workflow pauses at validation node, sends transaction data (optionally full XML) to subscriber
- External system evaluates against its business rules
- External system responds with action (approve/reject) via PUT
- Workflow resumes along the path corresponding to the action
- Timeout/withdrawal sends cancel event
- Security: XML content is all-or-nothing (individual fields cannot be separately secured)

### Rate Limiting

- Enforced at tenant (client) level — all consuming applications share the same rate limit pool
- ~10 requests/second or ~100 requests/minute for detail retrieval; lower for heavy operations
- Exceeded requests are rejected (not queued)
- Consumer design requirements: client-side rate limiting, request queuing, sequential processing, logging, cross-application coordination

### Cross-System Integration Patterns

Common integration architectures supported:
1. **One-way employee sync** (Platform → External): delta sync with hire/terminate/change event triggers
2. **Payroll data extraction** (Platform → External): report-based with datetime parameters
3. **External hire provisioning** (External → Platform): POST Employee with consumer-generated XRefCode, PATCH-first-then-POST fallback
4. **Background screening loop** (Bidirectional): POST order → provider PATCHes results back
5. **Job board integration** (Bidirectional): GET postings → POST candidate applications
6. **Workflow validation loop** (Bidirectional): event notification → external evaluation → PUT validation action

### Architectural Summary

```json
{
  "api_style": "Resource-oriented RESTful (JSON) + legacy SOAP (XML, frozen)",
  "authentication": "OAuth 2.0 ROPC flow (JWT tokens, 1-hour lifetime) or Basic Auth",
  "entity_identification": "XRefCode (tenant-defined stable string identifier) — NOT auto-increment IDs",
  "temporal_model": "Point-in-time queries via ContextDate parameter; all effective-dated entities",
  "sync_model": "Delta synchronization by design; changes-since-timestamp pattern mandated for production use",
  "security_model": "Platform RBAC fully enforced at API boundary (features + data authorization + field-level API access + org scope + IP restrictions)",
  "write_model": "POST (create with consumer-generated XRefCode) + PATCH (partial update) with validate-only mode",
  "pagination": "Cursor-based (opaque next-page URL) with configurable page size",
  "rate_limiting": "Tenant-level rate limits (~10/sec for detail retrieval; lower for heavy operations)",
  "event_model": "Push (webhook to consumer) or Pull (consumer polls) notification system for lifecycle events",
  "data_model_breadth": "40+ employee subordinate resources, 8+ core entity types, 10+ workforce management entities"
}
```

---

## Source Material: Hidden Architecture Patterns

Below are the key sections from the Hidden Architecture Patterns document. These are patterns **not explicitly documented** by the reference platform — they were **reverse-engineered** from API surface behavior, configuration options, workflow node types, and expression engine functions. Use these to write Document 4.

### Pattern 1: Guided Process Orchestration

**Summary:** A multi-step, multi-form orchestration engine that bundles related data entry forms into a sequenced experience with per-step workflow binding, skip logic, lifecycle tracking, and a system-generated monitoring workflow that tracks completion of ALL forms as a unit.

**Key inferences:**
- The guided process is a SEPARATE orchestration layer above the workflow engine — it coordinates MULTIPLE independent workflow executions (saga coordinator pattern)
- Each step has its own independent state machine: Not Started → In Progress → Completed/Skipped (plus possible Rejected and Blocked states)
- The system-generated monitoring workflow acts as a join/barrier pattern — completion requires all non-skippable forms to reach terminal states
- Three modes (Read Only, Edit, New) control data layer behavior for all forms in the bundle
- Ordering is presentation-order, but sequential enforcement is an open question

**Quality management mapping:** 8D Investigation as a guided process. D1-D8 as steps, each with its own approval workflow. D8 (recognition) skippable. D3 (containment) may need immediate approval. Monitoring workflow tracks overall 8D completion and triggers escalation if deadline exceeded.

### Pattern 2: Policy Resolution Engine

**Summary:** A generalized engine that resolves "which configured rule set applies to this entity right now?" when multiple overlapping policies could match. Uses entity-to-policy assignment, effective dating, priority ranking, and hierarchy-derived context.

**Key inferences:**
- Single generalized pattern across all policy types (password, pay, time entry, entitlement, onboarding)
- Resolution is ALWAYS point-in-time (re-evaluated on every request based on evaluation date)
- Policy is a CONTAINER of rules applied as a unit — resolution determines which container, then rules within execute
- Assignment is INDIRECT through a hierarchy chain (employee → role → password policy; employee → pay group → pay policy)
- The raw-to-processed pipeline (EmployeeRawPunch → EmployeePunch) is a visible example of policy execution

**Resolution algorithm:**
1. IDENTIFY CANDIDATES: Query all policy assignments effective as of evaluation date
2. FILTER BY SCOPE: Narrow by entity's current context (org unit, work assignment, status, location)
3. RESOLVE CONFLICTS: Priority-ranked, most-specific-match, or most-recent-effective
4. RETURN EFFECTIVE POLICY: Single winning policy applied

**Quality management mapping:** CAPA escalation timelines (30/60/90 day by severity), inspection frequency by customer/part/defect type, supplier scoring thresholds per commodity.

### Pattern 3: Data Staging and Edit Mode Architecture

**Summary:** A transactional staging layer where form submissions create PENDING data in a separate state from committed data, flows through workflow approval, and only becomes "real" when a Process node fires. Multiple pending changes can coexist for the same entity. The expression engine can evaluate both pending AND committed state.

**Key inferences:**
- Data is NOT committed when form is submitted — it's committed when workflow reaches Process node
- Process node has three commit modes: Approved (post-approval), Presave (pre-approval immediate commit), Rejected (discard)
- Staged data is IMMUTABLE after submission — approvers can accept/reject but cannot modify
- Edit modes define WHICH FIELDS can be staged — each edit mode has its own workflow, enabling partial entity staging
- Two users can have pending changes to different fields of the same entity simultaneously
- Expression engine has dual data source: staged form data (priority) + committed database (fallback via LoadIfEmpty)
- IsValidateOnly parameter runs all validations against staging context without committing
- Multi-party staging: same record can be pending at different parties (e.g., I-9: PENDING EMPLOYER + PENDING EMPLOYEE)

**Quality management mapping:**
- NCR investigation staging (pessimistic/Approved mode): root cause analysis lives in staging until approved
- Containment actions (optimistic/Presave mode): quarantine visible immediately, approval in parallel
- SCAR cross-organizational staging: customer fills defect description, supplier fills root cause — each party has independent pending state
- Edit mode for NCR severity reclassification: different approval chain than containment updates, both can be pending simultaneously

### Cross-Pattern Pipeline

The three patterns form a layered processing pipeline:

```
GUIDED PROCESS (orchestration) → Defines sequence, tracks overall completion
    ↓ spawns per-step
DATA STAGING (transactional) → Each step creates staged data alongside committed data
    ↓ evaluated by
POLICY RESOLUTION (rules) → Determines which validation/routing/processing rules apply
    ↓ drives
WORKFLOW ENGINE (approval) → Routes staged data through approval chains
    ↓ triggers
COMMIT (persistence) → Process node moves staged data to committed store, fires hooks and events
```

---

## Target System Context and Constraints

The architectural briefing is being used as a narrative guide for building a **quality management system** for automotive manufacturing. These constraints are non-negotiable and must be reflected accurately in the revised briefing.

**Domain:** IATF 16949 quality management with core entities: NCR (Non-Conformance Report), CAPA (Corrective and Preventive Action), SCAR (Supplier Corrective Action Request), 8D Investigation, Audit Finding.

**Technology stack:**

| Layer | Technology | State |
|-------|-----------|-------|
| Database | T-SQL stored procedures on Azure SQL Server | Mature. 81 procedures, 45 views, 133 migrations. Row-level security, workflow state machine, approval chains, audit logging all implemented. |
| API | C# / ASP.NET Core 9, Dapper (thin pass-through) | Early development. 27 endpoints. The API calls stored procedures — no business logic in C#. |
| UI | TypeScript / Next.js 15, React 19 | Planning only. No source code yet. |

**Non-negotiable constraints:**
- Business logic lives in T-SQL stored procedures. Do not recommend moving logic to C#.
- Single-tenant system for one company. Multi-tenant isolation patterns do not apply.
- Azure App Service deployment. No service bus, no message broker, no container orchestration.
- The data model is strongly typed. No EAV / tenant-configurable schema.
- Dapper ORM (micro-ORM). No Entity Framework.

---

## Specific Issues to Address

When writing the expanded briefing, pay special attention to these known problems:

### 1. The "Database Architecture Patterns Implied" Section Is Contradictory

The current section lists "multi-tenant schema with tenant isolation" and "polymorphic entity properties" — both are explicitly excluded by the project's constraints. The scope note was added as a band-aid but the patterns themselves are still listed and will confuse agents. Your revision must:
- **Remove** multi-tenant schema and polymorphic entity properties entirely
- **Keep** the valid patterns (effective-dated records, tree structures, audit tables, reference codes, junction tables, graph storage, state machines)
- **Add new patterns** implied by the API spec: dual-key entity identity (surrogate ID + reference code), delta-sync change tracking infrastructure, cursor-based pagination state, validate-only transaction rollback pattern
- **Add new patterns** implied by the hidden patterns: data staging tables, policy resolution tables with priority/scope/effective-dating, guided process instance tracking, field-level change metadata, commit/rollback state machines

### 2. Summary Point #10 Says "Build for Multi-Tenancy"

This directly contradicts the single-tenant constraint. Replace with something relevant to the actual system — perhaps organizational scoping (which still applies within a single tenant) or role-based data visibility.

### 3. The "What These Files Are" Section References "Two JSON Documents"

The package now contains four JSON specifications plus a hidden patterns document. Update the framing.

### 4. The Security Equation Should Be Reframed for Single-Tenant

The equation itself is valid, but the narrative should acknowledge that the target system is single-tenant and explain which layers still apply and which simplify.

### 5. Quality Management Domain Examples Are Missing

The existing briefing uses HR/payroll examples because the reference platform is an HRIS. The expanded briefing should include quality management domain examples throughout — NCR approval routing, CAPA timeline policy resolution, containment action staging, SCAR multi-party workflows, 8D investigation orchestration. These help engineers and agents map the abstract patterns to the concrete domain.

### 6. The "How These Systems Interact" Section Must Cover All Systems

The current section has 5 interaction points between Security and Workflow. The expanded section needs to cover:
- Security ↔ Workflow (existing)
- Security ↔ API (how security manifests at the API boundary)
- Workflow ↔ API (workflow validation integration, event notification)
- API ↔ Hidden Patterns (how staged data surfaces through API, how validate-only works)
- Hidden Patterns ↔ Workflow (guided processes orchestrating workflows, policy resolution driving guard expressions)
- Hidden Patterns ↔ Security (edit mode permission sets, multi-party access control)
- The full pipeline: UI → API → Staging → Policy Resolution → Workflow → Commit → Events → API → External Systems

---

## Quality Criteria

The expanded briefing should:

1. **Be readable in 15-20 minutes** by an engineer who has never seen the specs
2. **Serve as a sufficient orientation** that agents can skip reading the full JSON specs for most tasks
3. **Not exceed ~40-50 KB** (current: ~19 KB, target: roughly 2-2.5x the current size)
4. **Use the same bullet-heavy, pattern-focused style** as the existing Security and Workflow sections
5. **Include concrete quality management examples** alongside or replacing the HR/payroll examples
6. **Be self-consistent** — no patterns that contradict the constraints, no multi-tenant assumptions
7. **Reference specific node types, functions, and patterns by name** so engineers can ctrl+F the source specs for details

Take your time. Be comprehensive but not verbose. The output will be the primary narrative orientation document for an engineering team building a quality management platform.
