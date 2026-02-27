# Forms Research Consolidation — Design Document

**Date:** 2026-02-26
**Author:** Chris Walsh + Claude Code (claude-opus-4-6)
**Status:** Approved

---

## Purpose

Systematically analyze and consolidate research from 4 independent AI researchers (ChatGPT, Parallel, Claude, Gemini) into a single authoritative architecture specification for forms and data input systems across the sf-quality multi-repo system.

This consolidation serves three purposes simultaneously:
1. **Decision document** — authoritative architecture rulings with evidence
2. **Options catalog** — structured alternatives with trade-offs for team reference
3. **Implementation guide** — agent-consumable specs, CLAUDE.md directives, and coding conventions

## Context

### Why This Exists

The current approach to forms across the quality domain is on the table for rethinking. This includes:
- The legacy system's forms
- The Quality_Forms_Module inspection template design (not yet built)
- The broader forms strategy for NCRs, CAPAs, 8Ds, SCARs, audits, and future form types

The research was commissioned to determine the right fundamental architecture, not just library choices.

### What's At Stake

The existing Pattern_Mapping.md constraint — "Quality domain data model is well-defined (no EAV/configurable schema)" — may need to be revisited. The research should challenge or confirm this constraint with evidence. The consolidation must surface this tension explicitly rather than assuming the constraint holds.

### Implementation Model

- **Team:** One human (Chris) + coding agents
- **Effort framing:** Complexity, risk, and agent-readiness — not person-weeks
- **Agent-readiness:** Can a pattern be specified precisely enough for a coding agent to implement without ambiguity?

### Source Inventory

| Source | .md | .json | Status |
|---|---|---|---|
| ChatGPT (deep research) | 29KB research output | 46KB structured | Complete |
| Parallel (ChatGPT parallel) | 16KB research output | 534KB structured | Complete |
| Google Gemini | Prompt echoed back (no output) | Empty `{}` | Not delivered |
| Claude | Not yet received | N/A | Pending |

Processing begins with the 2 complete sources. Gemini and Claude are slotted in when delivered.

---

## Design

### Directory Structure

```
Reference_Architecture/Forms_Research_Consolidation/
  README.md                              <- purpose, process, status tracker
  docs/
    plans/
      2026-02-26-forms-research-consolidation-design.md  <- this file
  00_sources/
    chatgpt-deep-research.md             <- copy from sf-quality-app
    chatgpt-deep-research.json
    parallel-deep-research.md            <- copy from sf-quality-app
    parallel-deep-research.json
    claude-deep-research.md              <- TBD
    gemini-deep-research.md              <- TBD (re-run needed)
  01_extraction/
    EXTRACTION_TEMPLATE.md               <- normalized schema for all sources
    chatgpt-extracted.md
    parallel-extracted.md
    claude-extracted.md                   <- TBD
    gemini-extracted.md                   <- TBD
  02_synthesis/
    A-technology-comparison.md           <- cross-source master matrix
    B-architecture-recommendations.md    <- layer-by-layer comparison
    C-pattern-deep-dives.md              <- deduplicated pattern catalog
    D-complexity-risk-matrix.md          <- tiered risk + agent-readiness
    E-sources-and-evidence.md            <- master source list + confidence
    DIVERGENCE_LOG.md                    <- disagreements + constraint challenges
  03_adjudication/
    FINAL_DECISIONS.md                   <- authoritative rulings
  04_deliverables/
    FORMS_ARCHITECTURE_SPEC.md           <- the implementation guide
    GSD_SEEDING_CONTENT.md               <- pre-drafted child repo content
    CODING_CONVENTIONS.md                <- patterns + anti-patterns
```

### Why This Structure

Mirrors the proven pipeline from `Reference_Architecture/Quality_Forms_Module/`:
```
00_ground_truth -> 01_reviews -> 02_synthesis -> 03_adjudication -> 04_packages
```

Adapted for research consolidation:
```
00_sources -> 01_extraction -> 02_synthesis -> 03_adjudication -> 04_deliverables
```

Key differences from Quality_Forms_Module:
- `00_sources/` replaces `00_ground_truth/` (input is external research, not codebase state)
- `01_extraction/` replaces `01_reviews/` (normalizing research into comparable format, not reviewing code)
- `04_deliverables/` replaces `04_packages/` (output is architecture spec + directives, not migration SQL)

---

## Stage Details

### 00_sources — Raw Research

Copies of research files from `sf-quality-app/docs/Forms Research/`. Copied (not symlinked) so Reference_Architecture stays self-contained.

### 01_extraction — Normalized Extraction

Each source is distilled into a common template enabling apples-to-apples comparison.

#### Extraction Template

```markdown
# Forms Research Extraction — [Source Name]

**Source:** [filename]
**Model/Platform:** [e.g., ChatGPT o3 Deep Research, Gemini 2.5 Pro]
**Date produced:** [YYYY-MM-DD]
**Extracted by:** [who/what did the extraction]

---

## A. Technology Recommendations

For each technology recommended by this source:

| Technology | Category | Maturity | Azure Fit | Rec. Level | Rationale (1-2 sentences) | Limitations Noted |
|---|---|---|---|---|---|---|

**Stack-relevant picks** (fit current Next.js/React/Azure stack):
- [bulleted list]

**Stack-incompatible picks** (comparison only):
- [bulleted list]

---

## B. Architecture Recommendation

**Primary stack summary:**
- Frontend: [technology + rationale]
- Validation: [technology + rationale]
- API layer: [technology + rationale]
- Database/persistence: [technology + rationale]
- Auth: [technology + rationale]
- AI services: [technology + rationale]

**Alternative stack:** [1-2 sentence summary + key trade-off]

**Unique architectural claims** (positions this source takes others may not):
- [bulleted list]

---

## C. Patterns Identified

For each pattern this source covers:

| Pattern Name | Description | When to Use | When to Avoid | Real-World Example |
|---|---|---|---|---|

---

## D. Complexity & Risk Assessment

| Tier (Simple/Moderate/Complex) | Recommended Pattern | Integration Points | Key Risks | Agent-Readiness |
|---|---|---|---|---|

**Agent-Readiness** ratings:
- **High** — well-documented, deterministic, can be specified as a clear
  prompt/plan for coding agents
- **Medium** — requires some architectural decisions upfront, then agents
  can execute
- **Low** — requires significant human judgment during implementation,
  ambiguous contracts, or novel integration with limited documentation

---

## E. Sources & Evidence Quality

**Total sources cited:** [N]
**Sources with URLs that resolve:** [N — spot-check 3-5]
**Recency range:** [oldest — newest]
**Notable gaps:** [topics this source didn't cover or covered weakly]

---

## F. Extractor Notes

**Overall quality assessment:** [Strong / Adequate / Weak — 1 sentence why]
**Unique insights not likely in other reports:**
- [bulleted list]
**Red flags or questionable claims:**
- [bulleted list]
**Agent-implementation considerations:**
- [anything particularly useful or problematic for agentic development]
```

### 02_synthesis — Cross-Source Comparison

Five topic files mapping to the original research prompt sections, plus a divergence log.

**A-technology-comparison.md**
- Master matrix merging all sources
- Consensus column: how many sources recommend each technology
- Recommendation variance: do sources agree on its role?
- Filtered to stack-relevant technologies (stack-incompatible in appendix)

**B-architecture-recommendations.md**
- Layer-by-layer comparison (frontend, validation, API, DB, auth, AI)
- Unanimous agreements flagged (near-automatic decisions)
- Contested positions flagged (need adjudication)
- Unique recommendations noted

**C-pattern-deep-dives.md**
- All patterns across all sources, deduplicated
- Multi-source patterns: compare descriptions, use/avoid criteria, agent-readiness
- Ranked by relevance to manufacturing QMS + Azure SQL + audit requirements

**D-complexity-risk-matrix.md**
- Overlay all sources' tiered recommendations
- Compare risk assessments and agent-readiness per tier
- Consolidated risk register (union of all risks, deduplicated)

**E-sources-and-evidence.md**
- Master source list, deduplicated
- Multi-researcher citations flagged (higher confidence)
- Single-researcher citations flagged (verify)
- Evidence gaps noted

**DIVERGENCE_LOG.md**

The most important synthesis artifact. Structure:

```markdown
# Divergence Log

## Cross-Source Disagreements

| ID | Topic | Position A (source) | Position B (source) | Impact | Resolution Needed |
|---|---|---|---|---|---|

Impact levels:
- **Blocking** — cannot proceed without resolving (architectural direction)
- **Significant** — affects implementation approach but not direction
- **Minor** — cosmetic or preference-level difference

## Challenges to Existing Constraints

For each Pattern_Mapping.md non-negotiable constraint, document whether
the research confirms, challenges, or is silent on it:

| Constraint | Research Position | Sources | Evidence | Recommendation |
|---|---|---|---|---|

Key constraints under review:
1. Business logic stays in T-SQL (no C# domain service layer)
2. API layer stays thin (Dapper, not Entity Framework)
3. Single-tenant system
4. Azure App Service deployment (no message brokers/orchestration)
5. Quality domain data model is well-defined (no EAV/configurable schema)

## Challenges to Quality_Forms_Module Design

For each aspect of the existing inspection template design, document
whether the research confirms, challenges, or offers alternatives:

| Design Aspect | Current Approach | Research Alternative | Sources | Trade-off |
|---|---|---|---|---|
```

### 03_adjudication — Authoritative Decisions

Follows the decision table format from `Quality_Forms_Module/03_adjudication/`.

```markdown
# Forms Research — Final Authoritative Decisions

## Foundational Architecture Decisions

These must be resolved FIRST — everything else depends on them.

| ID | Question | Decision | Ruling | Evidence | Impact |
|---|---|---|---|---|---|

Foundational questions:
- FA-1: Should form structure be fixed-schema (typed tables per entity) or
  metadata-driven (configurable at runtime)?
- FA-2: Should form data be stored as typed relational columns, JSON payloads,
  or a hybrid?
- FA-3: Who can change form structure — developers only, or quality managers
  via admin UI?
- FA-4: Does the existing Quality_Forms_Module inspection design hold, need
  modification, or need replacement?
- FA-5: Which Pattern_Mapping.md constraints hold, and which get scoped
  exceptions for the forms domain?

## Constraint Alignment

For each decision, verify against:
- Pattern_Mapping.md non-negotiable constraints (or document override)
- Execution_Plan.md Section H gates and wave structure
- Quality_Forms_Module adjudication (if design is retained or modified)

## Stack & Pattern Decisions

| ID | Topic | Decision | Ruling | Evidence | Agent-Readiness | Blocker? |
|---|---|---|---|---|---|---|

Categories:
1. Stack decisions — technologies at each layer
2. Pattern decisions — architectural patterns adopted
3. Convention decisions — implementation approach
4. Scope decisions — build vs. defer
5. AI integration decisions — capabilities and constraints
```

**Decision-making rules:**
- Unanimous agreement across sources -> ACCEPT unless project-specific override
- Majority agreement -> ACCEPT majority, note dissent and reasoning
- No consensus -> Human makes the call, documents reasoning
- Single-source unique insight -> MODIFY to incorporate if credible

### 04_deliverables — Implementation Outputs

**FORMS_ARCHITECTURE_SPEC.md**

The primary output. Must reference Execution_Plan.md Section H and align with
the existing wave structure (or document changes to it).

```
1. Foundational Decisions (from FA-1 through FA-5)
2. Stack Decisions (layer-by-layer with decision IDs)
3. Architectural Patterns (precise specs for agent implementation)
4. Data Model Approach (Azure SQL strategy)
5. Validation Architecture (Zod sharing, client/server split, rules)
6. AI Integration Strategy (Document Intelligence, OpenAI, constraints)
7. Agent Implementation Notes
   - What must be decided by human before agents run
   - What agents can execute directly from this spec
   - Sequencing and dependencies
8. Execution Plan Alignment
   - How this maps to Section H gates and waves
   - Any changes needed to existing phase numbering
```

**GSD_SEEDING_CONTENT.md**

Pre-drafted content for human application into child repos, following the
established GSD_Seeding/ directive flow pattern:

```
Reference_Architecture/ -> GSD_Seeding/ -> human applies to child repo
```

Sections:
- For sf-quality-app CLAUDE.md (enforcement rules)
- For sf-quality-app Phase CONTEXT enrichments
- For sf-quality-api CLAUDE.md (enforcement rules)
- For sf-quality-db CLAUDE.md (enforcement rules)

**CODING_CONVENTIONS.md**

Patterns and anti-patterns written as agent-consumable guidance:
- DO (specific patterns with examples)
- DO NOT (anti-patterns with reasoning)
- Decision records (links back to FINAL_DECISIONS.md)

---

## Process Flow

```
1. Copy raw sources into 00_sources/
2. Extract each source using template -> 01_extraction/
3. When 2+ extractions exist, start synthesis -> 02_synthesis/
   (don't wait for all 4)
4. When all delivered extractions exist, finalize synthesis
   and produce divergence log
5. Human reviews divergence log + constraint challenges,
   makes foundational calls -> 03_adjudication/
6. Generate deliverables from adjudicated decisions -> 04_deliverables/
7. Human applies GSD seeding content to child repos
   (separate sessions, separate repo contexts)
```

Steps 1-4 can be done by coding agents.
Step 5 requires human judgment (the foundational decisions).
Step 6 can be agent-assisted.
Step 7 is a separate task per child repo.

### Incremental Processing

- Process sources as they arrive (don't block on all 4)
- Synthesis is updated when new extractions are added
- Divergence log grows as more sources provide comparison points
- Adjudication happens once when sufficient evidence exists
  (minimum 3 of 4 sources, ideally all 4)

---

## Current Source Status

| Source | Status | Action Needed |
|---|---|---|
| ChatGPT | Complete | Ready for extraction |
| Parallel | Complete | Ready for extraction |
| Gemini | Failed (prompt echoed, empty output) | Re-run research |
| Claude | Pending | Awaiting delivery |

---

## Alignment Notes

### Execution_Plan.md Section H

The forms integration strategy already defines:
- 6 entry gates (DB 23-24 complete, API 3.5 complete, etc.)
- 3 contract-chain waves (QF-A/B/C)
- Phase numbering: DB 34-36, API 11-13, App 11-13

The consolidation deliverables must either:
- Align with this existing plan, OR
- Document specific changes needed (with reasoning from research evidence)

### Quality_Forms_Module

The existing inspection template design (typed-per-entity schema with
30 migrations, 29 SPs, 29 endpoints) is input to the consolidation,
not a given. The foundational decisions (FA-1 through FA-5) determine
whether this design holds, gets modified, or gets replaced.

### Pattern_Mapping.md Constraints

Five non-negotiable constraints are under review:
1. Business logic stays in T-SQL
2. API layer stays thin (Dapper, not EF)
3. Single-tenant
4. Azure App Service deployment
5. Quality domain data model is well-defined (no EAV/configurable schema)

The research may confirm, challenge, or propose scoped exceptions to any
of these. The adjudication must address each explicitly.
