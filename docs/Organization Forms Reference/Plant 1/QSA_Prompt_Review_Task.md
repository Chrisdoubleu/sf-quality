# Task: Review and Improve the QSA Plant Audit Prompt

## Context — What Was Asked

The owner of the **sf-quality** workspace needed to revise a prompt that will be used to audit physical Excel-based quality forms from a 7-plant automotive coating operation. The goal is to feed each plant's folder of forms (as a zip file) to an AI along with this prompt, and get back a structured report that directly informs the engineering team building a digital replacement system across three independent repositories.

The original prompt was a solid quality auditor persona ("QSA") that produced a general quality systems audit. The problem: **its output was not mapped to the existing platform architecture**, so the engineering team would have to manually translate audit findings into database schema changes, API endpoint requirements, and UI screen designs.

## Context — What Was Done

A deep cross-repo analysis was performed across the entire sf-quality workspace to understand exactly what exists today:

- **sf-quality-db** (SQL Server): 151 migrations, 99 stored procedures, 38 views, 7 schemas, full NCR/CAPA/SCAR/Complaint/Audit entity model with temporal versioning, RLS, defect taxonomy with 9 knowledge extension tables, workflow engine, and authorization pipeline. Currently in Phase 34 of v3.0.
- **sf-quality-api** (ASP.NET Core 9 / Dapper): 30 endpoints (25 NCR lifecycle + diagnostics + placeholder domain gateways), middleware pipeline (correlation IDs, error mapping, rate limiting, audit logging), OpenAPI v0.3.0 published. 50% complete (5/10 phases).
- **sf-quality-app** (Next.js 15 / React 19 / shadcn/ui): Zero source code. 100% planning — tech stack locked, architecture documented, 10 phases sequenced, API contract snapshot pinned. Phase 1 not started.

The revised prompt was then written to embed a self-contained architecture briefing (entities, fields, API endpoints, UI plans) directly into the prompt so the auditing AI can map every finding to the real system — without needing codebase access.

## Key Changes Made to the Prompt

1. **Added architecture briefing** — Full entity definitions, NCR lifecycle states, defect taxonomy structure, disposition codes, API endpoint inventory, and planned UI screens embedded as read-only context
2. **Added Platform Entity Map column** to the file inventory (Phase 1) so every form gets tagged to its target entity
3. **Added entity discovery subsections** to each Phase 2 deep-dive (taxonomy mapping for defects, field coverage for NCR forms, new entity proposals for inspection/production/lab/process domains)
4. **Enhanced Phase 3 gap analysis** to require mapping each gap to specific database entities and fields
5. **Replaced Phase 4** (generic app migration recs) with a three-part **Platform Impact Assessment** targeting DB, API, and App layers separately
6. **Added Phase 5** — Cross-Plant Normalization Assessment (plant-universal vs plant-specific vs customer-driven patterns, checklist for remaining 6 plant audits)
7. **Expanded appendices** to four structured deliverables: defect taxonomy seed table, form-to-entity field mapping, form consolidation tiers, and proposed new entity DDL

## Your Task

You are a prompt engineering reviewer. Your job is to read the revised prompt and evaluate whether it will produce the highest-quality, most actionable output when given to an AI along with a zip of ~130 Excel/Word files from a plant's quality forms folder.

### Files to Read

1. **The revised prompt** (the artifact you are evaluating):
   `c:\Dev\sf-quality\docs\Organization Forms Reference\QSA_Plant1_Audit_Prompt.md`

2. **Workspace structure and project overview** (to understand the multi-repo architecture):
   `c:\Dev\sf-quality\WORKSPACE-STRUCTURE.md`
   `c:\Dev\sf-quality\README.md`

3. **Reference Architecture** (the source of truth for all 46 patterns and execution plan):
   `c:\Dev\sf-quality\Reference_Architecture\Execution_Plan.md`
   `c:\Dev\sf-quality\Reference_Architecture\Pattern_Mapping.md`

4. **Database contract manifest** (what the DB publishes — 99 procs, 38 views):
   `c:\Dev\sf-quality-db\.planning\contracts\db-contract-manifest.json`

5. **Database entity documentation** (schema, conventions, concerns):
   `c:\Dev\sf-quality-db\.planning\codebase\ARCHITECTURE.md`
   `c:\Dev\sf-quality-db\.planning\codebase\CONVENTIONS.md`
   `c:\Dev\sf-quality-db\.planning\codebase\CONCERNS.md`

6. **Database requirements and roadmap** (what's planned, what's built, what's deferred):
   `c:\Dev\sf-quality-db\.planning\REQUIREMENTS.md`
   `c:\Dev\sf-quality-db\.planning\ROADMAP.md`

7. **API contract** (the OpenAPI spec the frontend consumes):
   `c:\Dev\sf-quality-api\.planning\contracts\api-openapi.publish.json`

8. **API architecture and conventions**:
   `c:\Dev\sf-quality-api\.planning\codebase\ARCHITECTURE.md`
   `c:\Dev\sf-quality-api\.planning\codebase\CONVENTIONS.md`
   `c:\Dev\sf-quality-api\.planning\REQUIREMENTS.md`

9. **App planning docs** (planned UI screens, tech stack, phase roadmap):
   `c:\Dev\sf-quality-app\.planning\PROJECT.md`
   `c:\Dev\sf-quality-app\.planning\ROADMAP.md`
   `c:\Dev\sf-quality-app\.planning\codebase\STRUCTURE.md`
   `c:\Dev\sf-quality-app\.planning\codebase\STACK.md`
   `c:\Dev\sf-quality-app\.planning\codebase\ARCHITECTURE.md`

10. **The actual forms folder** (to understand what the prompt will be analyzing):
    `c:\Dev\sf-quality\docs\Organization Forms Reference\Plant 1 Production Forms\`
    - Subfolders: `8.2.1.1 Powder Line Forms\`, `8.2.1.2 ECoat Line Forms\`, `8.2.1.3 Inspection and Testing Forms and Labels\`
    - ~130 files total (Excel, Word, a few scanned images)
    - 15+ customer-specific subfolders under Inspection and Testing

### Evaluation Criteria

Analyze the prompt against these dimensions and provide specific, actionable improvements:

1. **Completeness** — Does the architecture briefing embedded in the prompt accurately reflect the current state of all three repos? Is anything important missing or misleading? Cross-check against the actual planning docs and contract artifacts listed above.

2. **Actionability** — Will the output format (phases 1-5 + appendices A-D) actually produce artifacts the engineering team can use directly? Or are there structural gaps where the auditor will produce narrative instead of structured data?

3. **Specificity of Entity Mapping** — The prompt asks the auditor to map form fields to `entity.field` targets. Is the architecture briefing detailed enough for the auditor to do this accurately? Should more field-level detail be provided for entities beyond NCR?

4. **Defect Taxonomy Quality** — The prompt asks for a defect taxonomy mapping table. Does it give the auditor enough context about the existing DefectType hierarchy (L1 categories, L2 leaves, LineType junction, severity ratings) to produce seed data that's actually importable?

5. **Cross-Plant Scalability** — The Phase 5 cross-plant normalization section needs to produce a reusable checklist for Plants 2-7. Is the framing strong enough, or will it produce vague guidance?

6. **Prompt Length vs. Signal** — The architecture briefing is substantial. Is any of it unnecessary noise that might distract the auditor from the actual form analysis? Could any sections be trimmed without losing mapping accuracy?

7. **Missing Dimensions** — Are there aspects of the forms or the platform that the prompt doesn't ask about but should? Consider:
   - Cost tracking (scrap cost, rework cost, customer chargebacks)
   - Training/competency records linked to operators
   - Calibration records for test equipment
   - Customer-specific approval workflows (GP-12 exit criteria)
   - Document control / revision history on the forms themselves
   - Packaging and shipping holds

8. **Output Format Optimization** — Would the appendices be more useful in a different format? (e.g., CSV-ready tables, JSON schemas, Mermaid diagrams for entity relationships). Consider that the output will be consumed by engineers working in VS Code.

### Deliverable

Produce a revised version of the prompt at the same file path:
`c:\Dev\sf-quality\docs\Organization Forms Reference\QSA_Plant1_Audit_Prompt.md`

If you determine the prompt is already strong, make only surgical improvements and explain what you changed and why. Do not rewrite for the sake of rewriting. The existing tone, persona, and structure are intentional.

Include a summary section at the top of your response listing every change you made with a one-line rationale for each.
