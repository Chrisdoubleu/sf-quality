# Quality Event Triage Layer — Configuration Workbook

**Purpose:** Structured spreadsheets for team review of the triage layer configuration before implementation. Open in Excel, walk through with your team, edit the TeamNotes columns, and use the result as the source of truth for migration authoring.

**Source Spec:** [Quality_Event_Triage_Layer.md](../Quality_Event_Triage_Layer.md)

---

## Master Sheets — The Entire System

These two files contain **every node and every edge across all 8 workflow processes** (the 6 existing + 2 new). This is the complete state machine for the entire quality platform in two normalized CSVs.

| File | What It Is | Stats |
|------|-----------|-------|
| `00_MASTER_AllStates.csv` | **Every state in the system** — 60 rows across 8 processes | 8 NCR + 9 CAPA + 7 Complaint + 8 SCAR + 7 AuditFinding + 8 EightD + 7 QualityAlert + 6 ProcessDeviation |
| `00_MASTER_AllTransitions.csv` | **Every transition in the system** — 102 rows across 8 processes | 14 NCR + 14 CAPA + 12 Complaint + 14 SCAR + 14 AuditFinding + 14 EightD + 11 QualityAlert + 8 ProcessDeviation + TransitionType classification |

Each row has a `Source` column showing where the data comes from (`migration-018+047`, `migration-043+047`, or `triage-layer-spec`). The `TransitionType` column on transitions classifies each edge as Forward, Backward, Skip, Reopen, or Void.

---

## Triage Layer Sheets (open in order)

| # | File | What It Is | What Your Team Should Do |
|---|------|-----------|--------------------------|
| 01 | `01_EntityTypeRegistry.csv` | 2 new entity type rows | Confirm names and table locations |
| 02 | `02_StatusCode.csv` | 13 new status codes (IDs 48-60) | Review names, descriptions, colors. Add/remove states if needed. |
| 03 | `03_WorkflowProcess.csv` | 2 new workflow process rows | Confirm process codes and descriptions |
| 04 | `04_WorkflowState.csv` | 13 new workflow state rows | Confirm StateType mappings (Start/Normal/Terminal/Cancelled) |
| 05 | `05_WorkflowTransition_QualityAlert.csv` | 11 QualityAlert transitions | **THE KEY SHEET.** Walk through every transition with your team. Read the FloorScenario column. Edit TeamNotes. Challenge the guards and role requirements. |
| 06 | `06_WorkflowTransition_ProcessDeviation.csv` | 8 ProcessDeviation transitions | Same — walk through each one. Validate the 4hr SLA. |
| 07 | `07_AccumulationRules.csv` | 4 accumulation/escalation rules | Debate the thresholds (3 in 30 days? 15% rework rate?). These are configurable. |
| 08 | `08_QualityAlert_FieldDefinitions.csv` | Every field on the QualityAlert table | Review nullable/required, valid values, when each field gets populated. This is the entity contract. |
| 09 | `09_ProcessDeviation_FieldDefinitions.csv` | Every field on the ProcessDeviation table | Same as above for ProcDev. |
| 10 | `10_EscalationPaths.csv` | 6 cross-entity escalation paths | How entities spawn other entities. What fields get inherited. What gets linked. |
| 11 | `11_RoleGuardReference.csv` | Role-to-permission mapping | Who can do what. Challenge this — does Floor Supervisor - Initiate & Manage need more/less access? |
| 12 | `12_ValidValues_Reference.csv` | All enum/code values with descriptions | AlertSourceCode, FamiliarityCode, ResolutionActionCode, DeviationTypeCode, etc. Add values your plants need. |

## How to Use

1. **Open all CSVs in Excel** (or import into a single workbook as separate sheets)
2. **Start with Sheet 05** (QualityAlert transitions) — this is the state machine your floor supervisors will use every day
3. **Read the FloorScenario column** — each transition has a plain-English description of when it fires
4. **Edit the TeamNotes column** — capture your team's decisions, questions, and modifications
5. **Challenge the guards** — is `Severity IN (Minor, Observation) AND Familiarity = 'Known'` the right boundary for Resolve in Place?
6. **Challenge the thresholds** in Sheet 07 — is 3 alerts in 30 days the right trigger, or should it be 5?
7. **Add missing values** in Sheet 12 — do your plants have alert sources or deviation types not listed?
8. **When done**, the edited CSVs become the input spec for migration authoring

## Column Conventions

- **_Ref columns** (e.g., `StatusCode_Ref`, `FromState_Ref`) are human-readable cross-references — not stored in the DB, just for readability
- **FloorScenario** describes the real-world situation that triggers this row
- **TeamNotes** is your team's column — write whatever you need
- **IDs continue from existing maximums**: StatusCodeId from 48, WorkflowStateId from 48, WorkflowTransitionId from 84, WorkflowProcessId from 7

## Relationship to Existing Data

These sheets extend (not replace) the existing configuration:
- StatusCode IDs 1-47 already seeded (migrations 018 + 043)
- WorkflowProcess IDs 1-6 already seeded (migration 047)
- WorkflowState IDs 1-47 already seeded (migration 047)
- WorkflowTransition IDs 1-83 already seeded (migration 047)
- EntityTypeRegistry has 6 existing types (migration 055)
