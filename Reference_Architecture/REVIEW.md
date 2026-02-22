# Reference Architecture Package Review

**Date:** 2026-02-21
**Scope:** Deep-dive gap analysis of the `Reference_Architecture/` folder — structure, content accuracy, internal consistency, and execution readiness.
**Method:** Full read of all 10 files, cross-validation against actual child repo state (sf-quality-db, sf-quality-api, sf-quality-app), and internal consistency checks across documents.

---

## Overall Assessment

The package is strong. The 46-pattern mapping is thorough, the execution plan is well-structured with clear dependency graphs, and the claims about current repo state are accurate. The issues below are not "nice to have" suggestions — they are gaps that will cause concrete problems when agents or humans try to use these documents for execution.

---

## 1. Stale File Paths Will Break Agent Navigation

**Severity: High — directly impacts agent usability**

When the package was reorganized into `Specs/`, `Briefings/`, and `Hidden_Patterns/` subdirectories, several documents retained their original flat-directory path references.

### Pattern_Mapping.md (lines 10-16)

The "Method and Constraints" section references:
```
Reference_Architecture_Package/Platform_System_Architecture_Technical_Patterns.json
Reference_Architecture_Package/Security_Role_Architecture_Agnostic.json
Reference_Architecture_Package/Workflow_Engine_Architecture_Agnostic.json
Reference_Architecture_Package/API_Integration_Architecture_Agnostic.json
Reference_Architecture_Package/architectural_briefing.md
Reference_Architecture_Package/Hidden_Architecture_Patterns_Reverse_Engineered.json
```

Actual paths are:
```
Specs/Platform_System_Architecture_Technical_Patterns.json
Specs/Security_Role_Architecture_Agnostic.json
Specs/Workflow_Engine_Architecture_Agnostic.json
Specs/API_Integration_Architecture_Agnostic.json
Briefings/architectural_briefing.md
Hidden_Patterns/Hidden_Architecture_Patterns_Reverse_Engineered.json
```

Line 20 references `README_AGENT_ORIENTATION_COMBINED.md` — actual file is `Briefings/Agent_Orientation_Combined.md`.

### Agent_Orientation_Combined.md

File manifest (lines 89-96) lists filenames without subdirectory paths and references itself as `README_AGENT_ORIENTATION.md`. Reading order table (lines 63-68) references bare filenames like `Platform_System_Architecture_Technical_Patterns.json` without the `Specs/` prefix.

### Agent_Orientation_Revised.md

Same issue. File manifest (lines 176-183) uses bare filenames. Reading order (lines 31-37) omits subdirectory paths. References itself as `README_AGENT_ORIENTATION.md`.

### Why this matters

A GSD agent told to "read `Reference_Architecture_Package/Platform_System_Architecture_Technical_Patterns.json`" will fail to resolve the path. The README.md has correct paths with working relative links — but agents following the Pattern_Mapping or Briefing reading orders will hit dead references.

**Fix:** Update all path references in Pattern_Mapping.md, Agent_Orientation_Combined.md, and Agent_Orientation_Revised.md to use the current subdirectory structure.

---

## 2. architectural_briefing.md Covers 2 of 4 Specs

**Severity: Medium — misleading scope claim**

The README describes `architectural_briefing.md` as "Narrative overview connecting the three spec files" (reading order entry #6). The briefing itself opens with "These two JSON documents are platform-agnostic architectural specifications" and then covers only Security and Workflow.

It does not cover:
- `API_Integration_Architecture_Agnostic.json`
- `Hidden_Architecture_Patterns_Reverse_Engineered.json`

The briefing was written before the API spec and Hidden Patterns documents were added to the package. Its "Database Architecture Patterns Implied" section (lines 232-243) includes patterns like "Multi-tenant schema" and "Polymorphic entity properties" that are explicitly excluded in the README constraints and Appendix A — creating a contradiction an agent would have to resolve.

**Fix:** Either update the briefing to cover all 4 specs and align its implied patterns with the README constraints, or rename/redescribe it accurately (e.g., "Narrative overview of the Security and Workflow specs") so agents know its scope is limited.

---

## 3. No Contract Manifest Refresh Strategy Between Phases

**Severity: High — breaks the contract chain during execution**

The Execution Plan's cross-repo dependency map (Section C) defines gates:
```
DB Phase 29 (audit.ApiCallLog) → API Phase 3.5
DB Phase 32 (validate-only procs) → API Phase 7
DB Phase 28 (notification queue) → API Phase 7+
DB Phase 31 (SCAR party status) → API Phase 5
```

The db-contract-manifest.json is the mechanism by which API phases discover available DB procedures and views. Currently at v1.0.0, it's already stale — it doesn't reflect the 9 knowledge views and 1 procedure added in Phase 21.

The Execution Plan mentions updating the manifest once at the end (Section G, item 3: "Update db-contract-manifest.json to reflect all new procs/views from v3.0"). But each v3.0 phase adds new procs/views that downstream API phases depend on. If Phase 29 ships `audit.ApiCallLog` and the manifest isn't refreshed before API Phase 3.5 planning begins, the API planner won't see the new table in the contract manifest.

**Fix:** Add a manifest refresh step after each DB phase that introduces cross-repo-visible artifacts. At minimum, refresh after Phases 25, 28, 29, 31, and 32 (the phases with downstream API gates). This should be explicit in the GSD workflow sequence (Section E) — e.g., after each `/gsd:execute-phase`, run a `/gsd:quick "Refresh db-contract-manifest.json"`.

**Note:** The manifest is already stale from Phase 21. Should be refreshed to reflect Phase 21 additions before any v3.0 work begins.

---

## 4. No Per-Phase Verification Criteria

**Severity: Medium — no way to gate phase transitions**

Section G provides a post-completion verification checklist for after all 46 patterns are done. But the Execution Plan defines a strict dependency chain (Phase 25 → 26 → 27 → 28, etc.) with no guidance on how to verify a phase delivered what it promised before the dependent phase begins.

For example, Phase 26 depends on Phase 25's guard definitions. If Phase 25 is marked complete but the guard definitions are incomplete or wrong, Phase 26 will fail during execution. By then, the agent has already spent a full planning and execution cycle.

GSD has `/gsd:verify-work` for this purpose, but the Execution Plan doesn't integrate it into the workflow sequence. Section E's workflow shows:
```
/gsd:discuss-phase 25 → /gsd:plan-phase 25 → /gsd:execute-phase 25
```

But not:
```
/gsd:execute-phase 25 → /gsd:verify-work 25 → /gsd:discuss-phase 26
```

**Fix:** Add a verification step after each phase in the dependency chain (at minimum Phases 25, 26, 27, 29, 32 — the ones with downstream dependents). Define 2-3 concrete acceptance criteria per phase in the phase descriptions (Section B1). For example, Phase 25 could require: "Guard definitions table exists and is queryable; EightDStep has StepStatus column; vw_EightDCompletionStatus returns non-null results."

---

## 5. Phase CONTEXT File Authorship Is Unspecified

**Severity: Medium — execution ambiguity**

Section D is titled "Context Seeding Strategy" and provides a detailed template for per-phase CONTEXT files. Section D4 even lists specific column names and SQL patterns that must appear in context files. But the plan never says **who creates these files** or **when**.

Options:
1. The user manually creates them before running `/gsd:plan-phase`
2. A GSD agent creates them during `/gsd:discuss-phase`
3. A GSD agent creates them during `/gsd:plan-phase`
4. They're created as part of `/gsd:new-milestone`

This matters because Section D4's specificity (exact column names like `StepStatus TINYINT NOT NULL DEFAULT 0`) means the context files need to be high-fidelity. If a GSD planner agent creates them, it needs to be told to read Pattern_Mapping.md and distill — that instruction doesn't exist anywhere in the workflow sequence.

**Fix:** Add an explicit context seeding step to the GSD workflow sequence. The most natural fit is during `/gsd:discuss-phase`, which is already included for complex phases. The instruction should be: "During discuss-phase, the agent should read the relevant patterns from `Reference_Architecture/Pattern_Mapping.md` and create the phase CONTEXT file using the template in Section D2, including the specific schema content from Section D4."

---

## 6. App Requirements Naming Collision

**Severity: Low-Medium — will cause confusion during execution**

Section B3 defines 6 new requirements for sf-quality-app:
```
APP-AUTH-01, APP-AUTH-02, APP-WORKFLOW-03, APP-WORKFLOW-04, APP-FORM-01, APP-TRACE-01
```

The app's existing REQUIREMENTS.md already has 20 requirements using a different convention:
```
APP-INFRA-01 through APP-INFRA-04
APP-AUTH-01 through APP-AUTH-03
APP-WORKFLOW-01, APP-WORKFLOW-02
APP-FORM-01, APP-FORM-02
APP-KNOW-01
APP-TRACE-01
APP-DASH-01
APP-DEPLOY-01
```

The collision: `APP-AUTH-01` and `APP-AUTH-02` already exist in the app's REQUIREMENTS.md with different content than what Section B3 proposes. Same for `APP-FORM-01` and `APP-TRACE-01`.

**Fix:** Either renumber the new requirements to avoid collision (e.g., APP-AUTH-04, APP-AUTH-05, APP-FORM-03, APP-TRACE-02) or note that the existing requirements should be enriched/expanded with the new content rather than creating duplicate IDs. Section F's planning file update table should reflect whichever approach is chosen.

---

## 7. Quick Items Missing Timing and Dependency Context

**Severity: Low-Medium — could cause ordering issues**

Section B1 lists two Quick items:
```
Quick: Document Storage Contract (#23)
Quick: Composite Aggregate Expansion (#18)
```

Section E (Step 6) places them after all 9 numbered phases:
```
sf-quality-db: /gsd:quick "Formalize document storage contract (#23)"
sf-quality-db: /gsd:quick "Add expand parameters to NCR detail proc (#18)"
```

Issues:
- **Pattern #23 (Document Storage)** has an open decision dependency. The workspace memory notes: "SharePoint references: decision pending on document storage — do not clean up yet." If the storage decision hasn't been made by the time Step 6 arrives, this Quick item can't execute.
- **Pattern #18 (Composite Aggregate)** adds `expand` parameters to the NCR detail proc, but API Phase 4 (Step 8) already plans pagination and query infrastructure that would consume this parameter. If #18 ships after API Phase 4, the API won't know to use it. If it ships before, API Phase 4 can incorporate it.

**Fix:** Add a note to Pattern #23 Quick item acknowledging the pending storage decision as a prerequisite. Move Pattern #18 earlier — ideally before or concurrent with DB Phase 29 (which is already the first executed phase) since it has no dependencies and would be available for API Phase 4 planning.

---

## 8. Briefing File Redundancy

**Severity: Low — adds confusion but doesn't block execution**

The `Briefings/` folder contains three files with substantial content overlap:

| File | Size | Unique Value |
|------|------|-------------|
| `Agent_Orientation_Combined.md` | ~6 KB | Condensed version of Revised; nothing unique |
| `Agent_Orientation_Revised.md` | ~14 KB | Per-repo guidance, pattern quick-reference tables, design pattern cross-reference |
| `architectural_briefing.md` | ~19 KB | Deeper Security + Workflow narrative; database patterns implied section |

`Agent_Orientation_Combined.md` is a strict subset of `Agent_Orientation_Revised.md`. Every section in Combined exists in Revised with more detail. The README reading order starts with `Agent_Orientation_Revised.md` (entry #1) and places `architectural_briefing.md` at entry #6 — Combined isn't in the reading order at all.

An agent reading all three will process ~39 KB of overlapping narrative before reaching the actual specs, and may receive contradictory signals (e.g., Combined references "~240 KB of structured architectural knowledge" while README says "~377 KB").

**Fix:** Consider removing `Agent_Orientation_Combined.md` since it adds no content beyond what Revised provides. If it's kept for a specific use case (e.g., quick-load contexts where 14 KB is too much), note that use case in the README.

---

## 9. No Rollback Strategy for Cross-Repo Gate Failures

**Severity: Low — unlikely but high-impact if it occurs**

The Execution Plan defines 5 cross-repo gates (Section C). All assume forward-only execution: DB ships, then API consumes. But there's no guidance for the scenario where an API phase discovers that the DB schema shipped by a prerequisite phase needs modification.

For example: API Phase 3.5 starts building audit trail middleware and discovers that `audit.ApiCallLog` (from DB Phase 29) needs an additional column. The Execution Plan doesn't address whether this should be:
- A hotfix migration in the current DB milestone
- A new Quick item
- Deferred to a later DB phase
- Handled by amending the original Phase 29

This matters because the GSD workflow (with its atomic commits and verification steps) doesn't have a built-in pattern for cross-repo schema amendments.

**Fix:** Add a brief "Cross-Repo Amendment Protocol" subsection to Section C that defines the procedure: likely a `/gsd:quick` hotfix migration in the DB repo, followed by a manifest refresh, before the API phase continues.

---

## 10. Execution Plan Phase 22 Narrative Is Scattered

**Severity: Low — readability issue**

Phase 22's deferral is referenced in four places across the Execution Plan:
- Section B1 rationale paragraph (lines 51-53)
- Section B1 note about Pattern #5 (lines 53-54)
- Phase table DEFER row for Pattern #21 (line 68)
- Section E Step 0 (lines 366-371)

Each reference adds slightly different context. An agent trying to understand the full Phase 22 picture has to reconstruct it from 4 locations. The deferral rationale also partially contradicts itself: B1 says "SEC-01 grants ship inline with future migrations as needed" but doesn't clarify whether SEC-01 is part of Pattern #21 (which is DEFERRED in the table) or a separate concern.

**Fix:** Consolidate Phase 22 deferral context into one location (Step 0 is the natural home) and back-reference from other mentions. Clarify the SEC-01 relationship explicitly.

---

## Items Verified as Accurate (No Action Needed)

These claims were cross-checked and confirmed:

- 46-pattern count and per-repo distribution (24 DB, 12 API, 9 App, 1 Cross)
- DB state: 133 migrations, 80 procs/36 views in manifest, Phase 21.1 complete, Phase 22 deferred with deferral file present
- API state: 10 phases, Phase 3 complete, OpenAPI v0.2.0, 27 endpoints
- App state: 10 phases, Phase 1 not started, snapshot v0.1.0, 20 requirements
- Appendix A exclusions (12 patterns) with valid rationales
- Cross-repo dependency graph accuracy
- Parallelization track analysis
- Phase dependency ordering within DB v3.0
- README folder structure matches actual filesystem
- All file sizes are approximately correct

---

## Summary of Recommended Actions

| # | Action | Priority | Effort |
|---|--------|----------|--------|
| 1 | Fix stale file paths in Pattern_Mapping.md + both Agent_Orientation files | High | Small |
| 2 | Update architectural_briefing.md scope or redescribe it accurately | Medium | Medium |
| 3 | Add manifest refresh steps between DB phases with cross-repo gates | High | Small |
| 4 | Add per-phase verification criteria + integrate `/gsd:verify-work` into workflow | Medium | Medium |
| 5 | Specify CONTEXT file authorship in the GSD workflow sequence | Medium | Small |
| 6 | Resolve app requirement ID collisions | Low-Med | Small |
| 7 | Add timing/dependency notes to Quick items (#23, #18) | Low-Med | Small |
| 8 | Remove or justify Agent_Orientation_Combined.md | Low | Small |
| 9 | Add cross-repo amendment protocol | Low | Small |
| 10 | Consolidate Phase 22 deferral narrative | Low | Small |
