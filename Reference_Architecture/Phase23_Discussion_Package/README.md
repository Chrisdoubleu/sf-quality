# Phase 23 Discussion Package

**Purpose:** Self-contained context bundle for an external AI to assist with `/gsd:discuss-phase 23` for `sf-quality-db`.

**When to delete:** After Phase 23 execution is verified complete (`23-VERIFICATION.md` all checks passing).

**Date created:** 2026-02-22

---

## How to Use This Package

1. Open `PERSONA_PROMPT.md` — paste the full content as the opening message in your AI conversation.
2. The AI will orient as Marcus Chen and begin asking targeted questions.
3. As Marcus asks questions, read answers from the files in this package and share relevant excerpts.
4. Work through the open questions in `02_phase_23_planning/23-ASSUMPTIONS-REDLINE.md` as the discuss-phase session.

---

## What the External AI Knows Nothing About

The persona has no codebase access. Everything it knows must come through this conversation. Key things to proactively share early:

- What the current `db-contract-manifest.json` actually contains vs. what it should contain (from `03_db_state/`)
- The exact drift findings from research (`02_phase_23_planning/23-RESEARCH.md`)
- The deferred scope boundary (Phase 22 stays deferred — share `04_recent_phase_history/22-DEFERRAL.md`)
- Current API and app state (`06_cross_repo_state/`)

---

## Package Contents

### `PERSONA_PROMPT.md`
The Marcus Chen persona prompt. Paste this as your first message in the external AI session.

### `01_system_context/`
| File | Content |
|------|---------|
| `SYSTEM_OVERVIEW.md` | What sf-quality is, the three repos, current state, who it's for |
| `ARCHITECTURE_CONSTRAINTS.md` | The 8 non-negotiable architecture decisions all plans must respect |

### `02_phase_23_planning/`
Authoritative Phase 23 planning artifacts — all copied directly from `sf-quality-db/.planning/phases/23-*`.

| File | Content |
|------|---------|
| `23-CONTEXT.md` | Phase goal, scope, mandatory deliverables, entry/exit criteria |
| `23-ASSUMPTIONS-FINAL.md` | Locked decisions and verification checks — governs plan scope |
| `23-ASSUMPTIONS-REDLINE.md` | Open questions for discuss-phase session |
| `23-RESEARCH.md` | Pre-verified artifact baseline: migration counts, drift findings, plan decomposition |
| `23-VERIFICATION.md` | Post-execute verification checklist |

### `03_db_state/`
Current authoritative state of the `sf-quality-db` repo.

| File | Content |
|------|---------|
| `DB-ROADMAP.md` | Full v2.0 milestone roadmap — all phases, current status |
| `DB-STATE.md` | Current position, accumulated decisions, deployment status |
| `DB-CONTRACT-MANIFEST.json` | The actual `db-contract-manifest.json` (currently at v1.0.0, 133 migrations) |

### `04_recent_phase_history/`
Context on what was just built and why Phase 22 was deferred.

| File | Content |
|------|---------|
| `22-DEFERRAL.md` | Exact rationale for deferring Phase 22 analytics — critical scope boundary |
| `PHASES_18_TO_21_SUMMARY.md` | What was built in the knowledge layer (Phases 18-21.1) — what Phase 23 must govern |

### `05_codebase_docs/`
Current codebase architecture documentation from `.planning/codebase/`.

| File | Content |
|------|---------|
| `DB-ARCHITECTURE.md` | Full architecture: layers, data flows, key abstractions |
| `DB-INTEGRATIONS.md` | External integrations, deployment infrastructure, CI/CD |
| `DB-CONCERNS.md` | Tech debt, known bugs, fragile areas, open test gaps |

### `06_cross_repo_state/`
State of sibling repos — critical for Phase 23 cross-repo contract sync work.

| File | Content |
|------|---------|
| `API-STATE.md` | API repo current position, decisions, contract versions |
| `API-ROADMAP.md` | Full API roadmap — what's built, what's next, what gates on DB phases |
| `APP-STATE.md` | App repo current position — planning only, no source code yet |

---

## Key Facts for the Discussion

| Item | Value |
|------|-------|
| Phase 23 goal | Close v2.0 governance before v3.0 begins — no new schema objects |
| Current DB migration count | 133 files |
| Manifest version | 1.0.0 (stale — needs refresh) |
| API contract version | 0.2.0 |
| App contract version | 0.2.0 (synced to API) |
| Phase 22 status | DEFERRED — do not re-open |
| Phase 23 plan count | 2-3 plans |
| Next phase after 23 | Phase 24 (Incoming Substrate) |
| v3.0 starts after | Phase 24 completes |
| Mandatory post-wave command | `pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly` |
