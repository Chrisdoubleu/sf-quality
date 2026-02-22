# Phase Packet Checklist (Discuss -> Plan -> Execute -> Verify)

**Purpose:** Define the minimum information packet each phase must carry so GSD agents have complete context and do not miss cross-repo dependencies.

Use this for every repo phase and quick item that affects contracts.

---

## 1) Pre-Phase Intake (Required Before `/gsd:discuss-phase`)

- [ ] Correct repo selected (`sf-quality-db`, `sf-quality-api`, or `sf-quality-app`)
- [ ] Target phase exists (or has been inserted/created)
- [ ] `ROADMAP.md` and `REQUIREMENTS.md` entries for this phase are present
- [ ] Phase `CONTEXT.md` exists and is not a generic stub
- [ ] Dependency gates checked in `OPERATIONS_DASHBOARD.md`
- [ ] Upstream contract artifacts are current (manifest/OpenAPI/snapshot)
- [ ] Source references are listed in phase context

Minimum source list to include in context:
- `Reference_Architecture/Execution_Plan.md`
- `Reference_Architecture/Pattern_Mapping.md`
- Relevant files under `Reference_Architecture/GSD_Seeding/`
- Any module package docs used by the phase (for example Quality Forms package docs)

---

## 2) Discuss Packet (Required Output of `/gsd:discuss-phase`)

The phase context must explicitly capture:

- [ ] Problem statement and why now
- [ ] In-scope patterns/requirements IDs
- [ ] Out-of-scope boundaries
- [ ] Dependency and gate status
- [ ] Data contract assumptions
- [ ] Open questions/blockers
- [ ] Acceptance criteria that can be verified immediately after execute

If this section is incomplete, do not proceed to `/gsd:plan-phase`.

---

## 3) Plan Packet (Required Output of `/gsd:plan-phase`)

- [ ] Concrete file-level plan with expected touched areas
- [ ] Contract changes called out explicitly
- [ ] Verification approach (tests, queries, scripts, or check commands)
- [ ] Rollback/amendment path documented
- [ ] Cross-repo follow-up tasks identified (if any)

If contract changes are introduced but follow-up artifact updates are missing, do not proceed to `/gsd:execute-phase`.

---

## 4) Execute Packet (Required Output of `/gsd:execute-phase`)

- [ ] Implementation completed for all in-scope plan items
- [ ] No silent scope expansion
- [ ] Required contract artifact updated:
  - [ ] DB: `db-contract-manifest.json` refreshed when needed
  - [ ] API: OpenAPI published when endpoint contracts change
  - [ ] App: API snapshot/types refreshed when API contract changes
- [ ] Phase notes capture any deviations from plan

---

## 5) Verify and Handoff (Required Before Next Dependent Phase)

- [ ] `/gsd:verify-work` run for phases with downstream dependencies
- [ ] Acceptance criteria from Discuss packet verified
- [ ] Gate status updated in `OPERATIONS_DASHBOARD.md`
- [ ] Execution log updated in `OPERATIONS_DASHBOARD.md`
- [ ] Next consumer phase context updated with new contract references

Do not open a dependent phase until all items above are complete.

---

## 6) Cross-Repo Amendment Protocol (When a Consumer Finds a Producer Gap)

If API/App discovers a missing or incorrect DB/API contract during execution:

1. Pause current phase execution at discovery point.
2. Switch to producer repo and create a targeted hotfix phase or quick item.
3. Execute and verify producer fix.
4. Refresh/publish producer contract artifact.
5. Resume consumer phase with updated contract context.

This keeps contract ownership in the correct repo and preserves traceability.

