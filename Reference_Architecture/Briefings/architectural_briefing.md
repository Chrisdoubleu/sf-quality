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
