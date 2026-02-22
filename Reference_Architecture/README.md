# Reference Architecture

Architectural patterns reverse-engineered from a production enterprise SaaS platform, abstracted into platform-agnostic terms, and mapped to sf-quality's three-repo quality management system. This folder is the single source of truth for all reference architecture materials and the execution plan that translates them into GSD-actionable work.

---

## Folder Structure

```
Reference_Architecture/
├── README.md                          ← You are here
├── Execution_Plan.md                  ← 46 patterns → GSD phases across all 3 repos
├── Pattern_Mapping.md                 ← Gap audit: 46 patterns vs. current implementation
│
├── Specs/                             ← Platform-agnostic JSON specifications
│   ├── Platform_System_Architecture_Technical_Patterns.json
│   ├── Security_Role_Architecture_Agnostic.json
│   ├── Workflow_Engine_Architecture_Agnostic.json
│   └── API_Integration_Architecture_Agnostic.json
│
├── Briefings/                         ← Narrative orientation documents
│   ├── architectural_briefing.md      ← Narrative overview of Security and Workflow specs
│   └── Agent_Orientation_Revised.md   ← Agent orientation with reading order, constraints, per-repo guidance
│
├── Hidden_Patterns/                   ← Reverse-engineered implicit patterns
│   ├── Hidden_Architecture_Patterns_Reverse_Engineered.json  ← Original (baseline)
│   ├── Hidden_Architecture_Patterns_Refined.json             ← ★ Revised (authoritative)
│   ├── REFINEMENT_REVIEW.md           ← ★ Prose review: blind spots, resolved Qs, T-SQL recs
│   └── Phase_Implementation/          ← DB phase implementation context
│       ├── CODEBASE_REFERENCE.md
│       ├── HANDOFF_CONTEXT.md
│       └── REFINEMENT_PROMPT.md
│
├── API_Integration_Patterns/          ← API architecture refinement prompt + phase decisions
│   ├── PERSONA_PROMPT.md
│   ├── CODEBASE_REFERENCE.md
│   └── Phase_Implementation/          ← Locked decisions + implementation roadmap (phases 3.4-5)
│       ├── DECISIONS.md               ← 5 locked architectural decisions; 3 open questions blocking Phase 4+
│       └── HANDOFF_CONTEXT.md         ← Phase-by-phase deliverables for API phases 3.4, 3.5, 4, 4.5, 5
│
└── Quality_Forms_Module/              ← Inspection forms architecture design [FUTURE MILESTONE — post-v3.0; not yet sequenced into any repo roadmap]
    ├── PERSONA_PROMPT.md              ← Persona, context, deliverables, output format
    └── CODEBASE_REFERENCE.md          ← Verbatim DDL, SP signatures, API/frontend patterns
```

---

## Reading Order

| Order | File | What It Teaches |
|-------|------|-----------------|
| 1 | [Briefings/Agent_Orientation_Revised.md](Briefings/Agent_Orientation_Revised.md) | Context, stack maturity, constraints, pattern-by-repo guidance |
| 2 | [Specs/Platform_System_Architecture_Technical_Patterns.json](Specs/Platform_System_Architecture_Technical_Patterns.json) | Synthesized engineering patterns — design patterns, data structures, algorithms (no domain language) |
| 3 | [Specs/Security_Role_Architecture_Agnostic.json](Specs/Security_Role_Architecture_Agnostic.json) | 10-layer security: RBAC, feature gating, field-level access, org hierarchy scoping |
| 4 | [Specs/Workflow_Engine_Architecture_Agnostic.json](Specs/Workflow_Engine_Architecture_Agnostic.json) | DAG-based orchestration: typed nodes, expression DSL, dynamic routing, event chaining |
| 5 | [Specs/API_Integration_Architecture_Agnostic.json](Specs/API_Integration_Architecture_Agnostic.json) | REST API: entity model, delta sync, two-phase retrieval, rate limiting, event notifications |
| 6 | [Briefings/architectural_briefing.md](Briefings/architectural_briefing.md) | Narrative overview of the Security and Workflow specs (does not cover API or Hidden Patterns) |
| 7 | [Hidden_Patterns/Hidden_Architecture_Patterns_Refined.json](Hidden_Patterns/Hidden_Architecture_Patterns_Refined.json) | Three implicit patterns (refined): Guided Process Orchestration, Policy Resolution Engine, Data Staging/Edit Mode — with confidence ratings, alternative explanations, blind spots |
| 7a | [Hidden_Patterns/REFINEMENT_REVIEW.md](Hidden_Patterns/REFINEMENT_REVIEW.md) | Prose review: inference validation, quality-domain deepening, cross-pattern synthesis, concrete T-SQL recommendations |

---

## Key Documents

### [Pattern_Mapping.md](Pattern_Mapping.md)
Audit of all 46 reference architecture patterns against current sf-quality implementation. Each pattern is classified by repo (DB/API/App/Cross-Repo), impact level, and action type (Strengthen Existing, Net New, Inform Planning). Includes code evidence citations, gap descriptions, and recommended approaches.

- 24 DB patterns, 12 API patterns, 9 App patterns, 1 Cross-Repo pattern
- Appendix A lists 12 skipped patterns with rationale

### [Execution_Plan.md](Execution_Plan.md)
Translates all 46 patterns into GSD-executable work:

- **sf-quality-db:** New v3.0 milestone with Phases 25-33 (after v2.0 completes)
- **sf-quality-api:** Quick item Phase 3.4 (middleware plumbing) + Insert Phase 3.5 + expand Phases 4, 7, 9, 10
- **sf-quality-app:** 6 new requirements + context enrichment in Phases 3, 4, 7, 8, 9, 10
- Cross-repo dependency map, parallelization tracks, context seeding strategy, verification checklist

---

## How This Package Is Used

- **Workspace root:** This folder is the single source of truth. Do NOT copy into child repos.
- **Per-phase distillation:** When planning a GSD phase, distill only the relevant patterns into that phase's CONTEXT file. Reference patterns by number (e.g., "Implements Pattern #14").
- **Agent context:** GSD agents should read the specific patterns cited in their phase CONTEXT, not the entire package.
- **Cross-repo references:** Child repos reference this folder via relative paths from workspace root: `../Reference_Architecture/Pattern_Mapping.md`

---

## Constraints

These reflect architectural decisions and infrastructure realities. They are not negotiable.

- Business logic stays in T-SQL. Do not recommend moving stored procedure logic into C#.
- The API layer stays thin. Dapper, not Entity Framework. Pass-through, not domain service layer.
- Single-tenant system. Multi-tenant isolation patterns do not apply.
- Azure App Service deployment. No service bus, no message broker, no container orchestration.
- The quality domain's data model is well-defined. EAV / tenant-configurable schema patterns do not apply.

---

## File Manifest

| File | Size | Format |
|------|------|--------|
| `Execution_Plan.md` | ~25 KB | Markdown |
| `Pattern_Mapping.md` | ~63 KB | Markdown |
| `Specs/Platform_System_Architecture_Technical_Patterns.json` | ~49 KB | JSON |
| `Specs/Security_Role_Architecture_Agnostic.json` | ~61 KB | JSON |
| `Specs/Workflow_Engine_Architecture_Agnostic.json` | ~48 KB | JSON |
| `Specs/API_Integration_Architecture_Agnostic.json` | ~53 KB | JSON |
| `Briefings/architectural_briefing.md` | ~19 KB | Markdown |
| `Briefings/Agent_Orientation_Revised.md` | ~14 KB | Markdown |
| `Hidden_Patterns/Hidden_Architecture_Patterns_Reverse_Engineered.json` | ~39 KB | JSON |
| `Hidden_Patterns/Hidden_Architecture_Patterns_Refined.json` | ~18 KB | JSON |
| `Hidden_Patterns/REFINEMENT_REVIEW.md` | ~29 KB | Markdown |
| `Hidden_Patterns/Phase_Implementation/CODEBASE_REFERENCE.md` | ~42 KB | Markdown |
| `Hidden_Patterns/Phase_Implementation/HANDOFF_CONTEXT.md` | ~23 KB | Markdown |
| `Hidden_Patterns/Phase_Implementation/REFINEMENT_PROMPT.md` | ~51 KB | Markdown |
| `API_Integration_Patterns/PERSONA_PROMPT.md` | ~13 KB | Markdown |
| `API_Integration_Patterns/CODEBASE_REFERENCE.md` | ~25 KB | Markdown |
| `API_Integration_Patterns/Phase_Implementation/DECISIONS.md` | ~4 KB | Markdown |
| `API_Integration_Patterns/Phase_Implementation/HANDOFF_CONTEXT.md` | ~10 KB | Markdown |
| `Quality_Forms_Module/PERSONA_PROMPT.md` | ~28 KB | Markdown |
| `Quality_Forms_Module/CODEBASE_REFERENCE.md` | ~35 KB | Markdown |

**Total: ~635 KB of structured architectural knowledge + execution planning.**
