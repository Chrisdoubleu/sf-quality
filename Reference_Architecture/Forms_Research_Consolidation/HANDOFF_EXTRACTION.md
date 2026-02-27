# Handoff: Forms Research Extraction (Stage 01)

**Created:** 2026-02-26
**Purpose:** Provide full context for a new chat session to execute the extraction stage of the Forms Research Consolidation pipeline.

---

## Your Task

Extract all 4 research sources into normalized format using the extraction template. This is Stage 01 of the pipeline defined in the design doc.

## What To Do

1. Read the design doc: `Reference_Architecture/Forms_Research_Consolidation/docs/plans/2026-02-26-forms-research-consolidation-design.md`
2. Read the extraction template: `Reference_Architecture/Forms_Research_Consolidation/01_extraction/EXTRACTION_TEMPLATE.md`
3. For each of the 4 sources in `Reference_Architecture/Forms_Research_Consolidation/00_sources/`, read the .md file (primary) and .json file (supplementary structured data), then produce an extracted file following the template exactly.
4. Write each extraction to `Reference_Architecture/Forms_Research_Consolidation/01_extraction/{source}-extracted.md`

## Sources To Extract

| Source | .md file | .json file | Output file |
|---|---|---|---|
| ChatGPT | `00_sources/chatgpt-deep-research.md` (30KB) | `00_sources/chatgpt-deep-research.json` (46KB) | `01_extraction/chatgpt-extracted.md` |
| Parallel | `00_sources/parallel-deep-research.md` (16KB) | `00_sources/parallel-deep-research.json` (534KB) | `01_extraction/parallel-extracted.md` |
| Gemini | `00_sources/gemini-deep-research.md` (56KB) | `00_sources/gemini-deep-research.json` (44KB) | `01_extraction/gemini-extracted.md` |
| Claude | `00_sources/claude-deep-research.md` (25KB) | `00_sources/claude-deep-research.json` (36KB) | `01_extraction/claude-extracted.md` |

## Critical Context For Extraction

The extraction is NOT just a reformatting exercise. You need to understand these key points:

### 1. Everything Is On The Table

The existing architecture (including the Quality_Forms_Module inspection template design with its typed-per-entity schema) is being reconsidered. The research may challenge or confirm existing constraints. Extract each source's position on fundamental architecture honestly — don't filter through existing assumptions.

### 2. Agent-Readiness Matters, Person-Weeks Don't

The team is one human + coding agents. When sources give person-week estimates, translate them into complexity/risk/agent-readiness assessments:
- **High agent-readiness** = well-documented, deterministic, can be specified as a clear prompt/plan for coding agents
- **Medium** = requires architectural decisions upfront, then agents can execute
- **Low** = requires significant human judgment during implementation

### 3. Existing Constraints Under Review

Pattern_Mapping.md has 5 non-negotiable constraints. The research may challenge them. When extracting, note each source's position on:
1. Business logic stays in T-SQL (no C# domain service layer)
2. API layer stays thin (Dapper, not Entity Framework)
3. Single-tenant system
4. Azure App Service deployment (no message brokers/orchestration)
5. Quality domain data model is well-defined (no EAV/configurable schema)

Pay special attention to #5 — multiple sources recommend metadata-driven/JSON-schema-driven forms which directly tensions with this constraint.

### 4. Section F (Extractor Notes) Is Critical

This is where you add YOUR assessment as the extractor:
- Overall quality of the source (Strong/Adequate/Weak)
- Unique insights not in other reports
- Red flags or questionable claims
- Agent-implementation considerations

Be honest and specific. This feeds the divergence log and adjudication.

### 5. Stack Context

The current stack is: Next.js 15 (App Router), React 19, TypeScript strict, shadcn/ui + Radix, React Hook Form + Zod, TanStack Query + Table, Tailwind CSS 4, Azure App Service, Azure SQL, Entra ID via Easy Auth.

When categorizing technologies as "stack-relevant" vs "stack-incompatible", use this as the baseline.

## After Extraction

Once all 4 extractions are complete:
1. Update the README.md status tracker (Stage 01_extraction -> Complete)
2. Note any early observations about cross-source consensus or divergence — these will seed the synthesis stage

## What NOT To Do

- Don't start synthesis (Stage 02) — that's a separate task
- Don't modify the source files in 00_sources/
- Don't modify the design doc or extraction template
- Don't skip the .json files — they often contain structured data that the .md summaries omit

## File Paths (All Relative to Workspace Root c:\Dev\sf-quality)

```
Reference_Architecture/Forms_Research_Consolidation/
  README.md                                          <- update status when done
  docs/plans/2026-02-26-forms-research-consolidation-design.md  <- read for full context
  00_sources/
    chatgpt-deep-research.md
    chatgpt-deep-research.json
    parallel-deep-research.md
    parallel-deep-research.json
    gemini-deep-research.md
    gemini-deep-research.json
    claude-deep-research.md
    claude-deep-research.json
  01_extraction/
    EXTRACTION_TEMPLATE.md                           <- the template to follow
    chatgpt-extracted.md                             <- you write this
    parallel-extracted.md                            <- you write this
    gemini-extracted.md                              <- you write this
    claude-extracted.md                              <- you write this
```
