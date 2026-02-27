# Remediation Plan — Pre-Execution Readiness

**Date:** 2026-02-27
**Purpose:** Fix all gaps and risks identified by the 4-agent research sweep before Phase 1 execution begins. Each item is a specific action with a clear owner (workspace or child repo).

---

## Priority 1: Blocking — Must Fix Before Any Phase Starts

### REM-01: Sync API's DB contract snapshot (sf-quality-api)

**Gap:** The API's `db-contract-manifest.snapshot.json` shows 133 migrations / 80 procedures / 36 views. The DB source has 151 migrations / 99 procedures / 38 views. The API is **19 procedures and 2 views behind**.

**Action:** Copy `sf-quality-db/.planning/contracts/db-contract-manifest.json` to `sf-quality-api/.planning/contracts/db-contract-manifest.snapshot.json`. Update API STATE.md to declare the refreshed contract version.

**Owner:** Execute from sf-quality-api context.
**When:** Before Phase 2 starts. Can be done now.

---

### REM-02: Add workspace milestone awareness to all child CLAUDE.md files (workspace bridge)

**Gap:** No child repo CLAUDE.md references the workspace-level milestone, the 8-phase ROADMAP, or the planning bridge pattern. Agents in child repos have zero awareness of the coordinated milestone.

**Action:** Add a section to each child repo's CLAUDE.md:

```markdown
## Cross-Repo Milestone Coordination
- This repo participates in workspace milestone v1.0 (Spring Pivot + Forms Foundation)
- Workspace-level ROADMAP, REQUIREMENTS, and STATE are at `../ROADMAP.md` (or `../../.planning/ROADMAP.md`)
- The workspace pushes phase CONTEXT.md files to `.planning/phases/*/CONTEXT.md` — these contain requirements, adjudication decisions, and success criteria from the workspace roadmap
- Milestone phases assigned to this repo: [list specific phases]
```

**Owner:** Execute from each child repo context (source code governance rules apply).
**When:** Before the first phase targeting each repo starts.

---

### REM-03: Document C# work stoppage decision (sf-quality-api)

**Gap:** The API STATE.md says the current focus is "API catch-up execution in canonical order: Phase 4, then Phase 6, then Phase 8/9" — referring to C# endpoint phases. The milestone ROADMAP says to replace the entire C# stack with Spring Boot. No decision point documents when to stop C# work.

**Action:** Add an ADR or decision record in sf-quality-api declaring: "C# development is suspended. All remaining API phases (4, 6, 8, 9, 10) will be implemented in Spring Boot under milestone v1.0. Existing C# code in phases 01-03.5/05/07 is reference material for the Spring Boot migration, not active development."

**Owner:** Execute from sf-quality-api context.
**When:** Before Phase 2 starts.

---

## Priority 2: Important — Must Fix Before the Affected Phase Starts

### REM-04: Plan CI pipeline migration for sf-quality-api (Phase 2 prerequisite)

**Gap:** `planning-contract-validation.yml` hardcodes `actions/setup-dotnet@v4`, `dotnet-version: "9.0.x"`, `dotnet build SfQualityApi.sln`, and triggers on `SfQualityApi.sln`. This breaks when the .sln is removed.

**Scripts that will break:**
- `Test-InlineSqlBoundaries.ps1` — scans `src/SfQualityApi/Endpoints/*.cs`
- `Start-LocalApiNonInteractive.ps1` — hardcoded `dotnet run --project .csproj`

**Scripts that are safe (language-agnostic):**
- `Test-DbContractReferences.ps1` — scans Markdown only
- `Test-OpenApiPublication.ps1` — validates JSON artifact structure
- `Test-ApiContractReferences.ps1` (sf-quality-app) — scans Markdown only

**Action:** Phase 2, Plan 01 must begin with:
1. Replace `actions/setup-dotnet` with `actions/setup-java@v4` (Java 21)
2. Replace `dotnet build SfQualityApi.sln` with `mvn package -DskipTests`
3. Replace `SfQualityApi.sln` trigger path with `pom.xml`
4. Rewrite `Test-InlineSqlBoundaries.ps1` for `*.java` files under `src/main/java/`
5. Rewrite `Start-LocalApiNonInteractive.ps1` for `./mvnw spring-boot:run`
6. Update CLAUDE.md and AGENTS.md: replace `dotnet build` with `mvn package`

**Owner:** Execute from sf-quality-api context during Phase 2.
**When:** First task in Phase 2.

---

### REM-05: Pre-approve DB Phase 35 blocker exception for Quality Forms (Phase 6 prerequisite)

**Gap:** sf-quality-db STATE.md says "blocker-only freeze — no new Phase 35 feature wave starts unless it directly unblocks API/App execution." Milestone Phase 6 is net-new Quality Forms feature work.

**Action:** Record a blocker exception in sf-quality-db (ADR or STATE.md addendum): "Quality Forms Database (milestone Phase 6) is approved as a blocker exception. It directly unblocks API Phase 7 and App Phase 8."

**Owner:** Execute from sf-quality-db context.
**When:** Before Phase 6 starts (after Phase 1 adjudication completes).

---

### REM-06: Update DB AGENTS.md schema conventions for inspection (Phase 6 prerequisite)

**Gap:** The DB AGENTS.md lists preserved schema conventions as `meta`, `ref`, `quality`, `integration`, `audit`, `security`. Phase 6 will add inspection-related objects. If agents follow the convention list literally, `inspection` is not recognized.

**Action:** Add the Quality Forms schema name to the AGENTS.md preserved schema conventions list. (Exact schema name depends on adjudication — likely `quality` sub-tables or a new `inspection` schema.)

**Owner:** Execute from sf-quality-db context.
**When:** Before Phase 6 starts.

---

### REM-07: Archive C# API phases and establish milestone phase mapping (Phase 2 prerequisite)

**Gap:** The API has phases 01-10 (C# plan). The milestone ROADMAP assigns Phases 2, 3, 4, 7 to the API. There is a naming collision risk — agents could confuse API internal "Phase 04 (CAPA)" with milestone "Phase 4 (Spring Boot Remaining Endpoints)."

**Action:** In sf-quality-api:
1. Create `.planning/phases/milestone-v1.0/` directory
2. Create a mapping file that links milestone phases to the legacy C# phases:
   - Milestone Phase 2 (Spring Infra) replaces C# phases 01 + 03.5
   - Milestone Phase 3 (Spring NCR) replaces C# phase 03
   - Milestone Phase 4 (Spring Remaining) replaces C# phases 04-09
   - Milestone Phase 7 (QF API) is new territory
3. Mark existing C# phases 01-10 as "archived — reference only"

**Owner:** Execute from sf-quality-api context.
**When:** Before Phase 2 starts.

---

## Priority 3: Recommended — Improves Workflow Quality

### REM-08: Add `validation_mode` to DB config.json for consistency

**Gap:** API and App config.json files have `validation_mode: "advisory"`, but the DB does not.

**Action:** Add `"validation_mode": "blocking"` to sf-quality-db `.planning/config.json`.

**Owner:** Execute from sf-quality-db context.
**When:** Anytime before Phase 6.

---

### REM-09: Push CONTEXT.md bridge files to child repos for parallel-start phases

**Gap:** The planning bridge pattern is defined but no CONTEXT.md files have been pushed yet. Phases 2 and 5 can start immediately but have no workspace context in the child repos.

**Action:** From workspace root, write:
- `sf-quality-api/.planning/phases/milestone-v1.0/phase-02-spring-infrastructure/CONTEXT.md` — Phase 2 requirements, success criteria, Spring Boot research findings summary
- `sf-quality-app/.planning/phases/milestone-v1.0/phase-05-app-foundation/CONTEXT.md` — Phase 5 requirements, success criteria

Phase 6 CONTEXT.md is written after Phase 1 adjudication completes (it depends on decisions).

**Owner:** Execute from sf-quality workspace root (planning bridge — allowed).
**When:** Before Phases 2 and 5 start.

---

### REM-10: OpenAPI route compatibility verification strategy

**Gap:** When moving from Swashbuckle/ASP.NET to springdoc-openapi, route paths must be byte-identical. Schema `$ref` names and `operationId` values may differ.

**Action:** During Phase 2, create a contract compatibility test:
1. Export the Spring Boot OpenAPI spec via springdoc-openapi-maven-plugin
2. Diff against the existing `api-openapi.publish.json` — assert all 29 path+method combinations match
3. Accept schema name changes but flag path/method divergence as a build failure

**Owner:** Execute from sf-quality-api context during Phase 2.
**When:** Part of Phase 2 CI setup.

---

## Execution Order

```
Now (before any phase):
  REM-01  Sync DB contract snapshot              [sf-quality-api]
  REM-03  Document C# work stoppage              [sf-quality-api]

Before Phase 2 (Spring Boot):
  REM-02  Add milestone awareness to API CLAUDE.md  [sf-quality-api]
  REM-04  Plan CI pipeline migration              [sf-quality-api, Phase 2 Plan 01]
  REM-07  Archive C# phases + milestone mapping   [sf-quality-api]
  REM-09  Push Phase 2 CONTEXT.md bridge          [sf-quality workspace]

Before Phase 5 (App Foundation):
  REM-02  Add milestone awareness to App CLAUDE.md  [sf-quality-app]
  REM-09  Push Phase 5 CONTEXT.md bridge          [sf-quality workspace]

Before Phase 6 (DB Quality Forms):
  REM-02  Add milestone awareness to DB CLAUDE.md   [sf-quality-db]
  REM-05  Pre-approve blocker exception           [sf-quality-db]
  REM-06  Update AGENTS.md schema conventions     [sf-quality-db]
  REM-08  Add validation_mode to config.json      [sf-quality-db]

During Phase 2:
  REM-04  Execute CI migration (first task)       [sf-quality-api]
  REM-10  OpenAPI route compatibility tests       [sf-quality-api]
```

---

## Research Artifacts Produced

| File | Contents | Consumed By |
|------|----------|-------------|
| `.planning/research/spring-boot-migration-research.md` | Complete Spring Boot + MyBatis + Azure patterns with code snippets | Phase 2 planning |
| `.planning/research/SUMMARY.md` | Executive summary — stack decisions, build order, open questions | Phase 2 CONTEXT.md |
| `.planning/research/STACK.md` | Technology decisions with Maven dependencies | Phase 2 implementation |
| `.planning/research/FEATURES.md` | Feature landscape — table stakes, differentiators, anti-features | Phase 2 planning |
| `.planning/research/ARCHITECTURE.md` | 9 code patterns (Easy Auth, session context, MyBatis, error handling, etc.) | Phase 2 implementation |
| `.planning/research/PITFALLS.md` | 14 pitfalls (4 critical, 6 moderate, 4 minor) | Phase 2-4 planning |
| `.planning/research/json-rules-engine-integration-research.md` | json-rules-engine + RHF + Zod integration patterns | Phase 8 planning |

---
*Created: 2026-02-27 from 4-agent parallel research sweep*
