# Phase 28 — Event-Driven Chaining and Notifications

**Milestone:** v3.0 Architectural Hardening and Platform Maturation
**Track:** Main dependency chain (gate: Phases 25 + 27 complete)
**Requirements:** ARCH-06, ARCH-07
**Source patterns:** Pattern_Mapping.md #8, #13

---

## Reference Architecture Patterns

### Pattern #8 — Event-Driven Workflow Chaining + Outbox Generalization
- **Gap:** Outbox/pull-ack pattern is implemented for NCR transitions only (`quality.vw_NcrNotificationOutbox`, migration 121). CAPA, SCAR, Complaint, and Audit entities are not covered. Internal event-subscription metadata for automatic workflow chaining does not exist.
- **Scope:** Extend outbox to CAPA/SCAR/Complaint/Audit entities. Add `workflow.EventSubscription` for internal event subscription metadata.

### Pattern #13 — Notification Queue
- **Gap:** No internal user notification queue exists. The current model relies on the external outbox for downstream consumers but has no in-app notification inbox.
- **Scope:** Create `workflow.NotificationQueue` for internal user notifications. Add notification write hooks to transition and approval procedures.

---

## Existing Artifacts

This phase builds on:
- `quality.QualityEventLink` (migration 033) — quality event linking table
- `integration.NcrNotificationAck` (migration 119) — NCR outbox ack table
- `integration.usp_GetPendingNotifications`, `integration.usp_AcknowledgeNcrOutboxEvent` (migration 121) — NCR outbox pull/ack procedures
- `quality.vw_NcrNotificationOutbox` (migration 121) — NCR outbox view
- `workflow.usp_TransitionState` (migration 098) — extend with notification write hooks
- `workflow.NotificationTemplateKey` column (Phase 25 deliverable on `workflow.WorkflowTransition`)
- Presave rejection path (Phase 27 deliverable — uses notification queue once created)

---

## Recommended Approach (Distilled)

### Plan 28-01: Generalized Outbox Extension

Extend the outbox pattern to cover CAPA, SCAR, Complaint, and Audit entities:

```sql
-- Create generalized outbox table (or extend existing integration schema)
-- Option A: Generalize existing NCR outbox to a multi-entity outbox
ALTER TABLE integration.NcrNotificationAck RENAME TO integration.NotificationOutbox;  -- conceptually
-- More likely: create new generalized table alongside existing NCR-specific one for backwards compat

CREATE TABLE integration.NotificationOutbox (
    OutboxEventId      INT IDENTITY(1,1) PRIMARY KEY,
    EntityType         NVARCHAR(50)  NOT NULL,  -- 'NCR', 'CAPA', 'SCAR', 'Complaint', 'Audit'
    EntityId           INT           NOT NULL,
    EventType          NVARCHAR(100) NOT NULL,  -- e.g. 'state-transitioned', 'approval-completed'
    EventPayloadJson   NVARCHAR(MAX) NOT NULL,  -- JSON blob of relevant event data
    CorrelationId      NVARCHAR(50)  NULL,
    CreatedAtUtc       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    AcknowledgedAtUtc  DATETIME2     NULL,
    AcknowledgedByRef  NVARCHAR(100) NULL
);

CREATE INDEX IX_NotificationOutbox_Pending ON integration.NotificationOutbox (EntityType, AcknowledgedAtUtc)
    WHERE AcknowledgedAtUtc IS NULL;
```

Add outbox writes to CAPA, SCAR, Complaint entity transition procedures (or in `workflow.usp_TransitionState` via the `NotifyOnTransition` flag added in Phase 25).

**`workflow.EventSubscription` table:**
```sql
CREATE TABLE workflow.EventSubscription (
    EventSubscriptionId  INT IDENTITY(1,1) PRIMARY KEY,
    SourceEntityType     NVARCHAR(50)  NOT NULL,
    SourceEventType      NVARCHAR(100) NOT NULL,
    TargetWorkflowProcessId INT NULL REFERENCES workflow.WorkflowProcess(WorkflowProcessId),
    TargetAction         NVARCHAR(100) NOT NULL,  -- 'trigger-transition', 'notify-role', 'enqueue-job'
    IsActive             BIT NOT NULL DEFAULT 1
);
```

### Plan 28-02: Internal Notification Queue + Write Hooks

```sql
CREATE TABLE workflow.NotificationQueue (
    NotificationId       INT IDENTITY(1,1) PRIMARY KEY,
    TargetUserId         INT           NOT NULL REFERENCES dbo.[User](UserId),
    NotificationType     NVARCHAR(50)  NOT NULL,  -- 'approval-required', 'state-changed', 'presave-rejected'
    EntityType           NVARCHAR(50)  NOT NULL,
    EntityId             INT           NOT NULL,
    MessageText          NVARCHAR(1000) NOT NULL,
    IsRead               BIT NOT NULL DEFAULT 0,
    CreatedAtUtc         DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    ReadAtUtc            DATETIME2     NULL,
    CorrelationId        NVARCHAR(50)  NULL
);

CREATE INDEX IX_NotificationQueue_Unread ON workflow.NotificationQueue (TargetUserId, IsRead)
    WHERE IsRead = 0;
```

Add notification write hooks in:
- `workflow.usp_TransitionState` — write to `workflow.NotificationQueue` when `workflow.WorkflowTransition.NotifyOnTransition = 1`
- `workflow.usp_ProcessApprovalStep` — notify approver on pending approval creation; notify requester on decision
- Presave rejection path (Phase 27) — write rejection notification

---

## Cross-Repo Dependencies

| Dependency | Direction | Details |
|-----------|-----------|---------|
| Phase 25 | DB → this phase | `workflow.WorkflowTransition.NotifyOnTransition` column must exist |
| Phase 27 | DB → this phase | Presave rejection path writes to `workflow.NotificationQueue` — needs the table |
| `workflow.NotificationQueue` | DB → API Phase 7+ | API Phase 7 (workflow endpoints) will add notification inbox endpoint consuming this table |
| `integration.NotificationOutbox` | DB → API Phase 7 | API notification passthrough endpoints consume the generalized outbox |

## Entry Criteria

- Phase 25 COMPLETE (NotifyOnTransition column exists on WorkflowTransition)
- Phase 27 COMPLETE (presave rejection path needs NotificationQueue)

## Exit Criteria

1. `workflow.NotificationQueue` table exists with all specified columns and unread index
2. `workflow.EventSubscription` table exists
3. Outbox pattern generalized to cover CAPA and SCAR entities (at minimum)
4. At least one approval transition writes a notification row to `workflow.NotificationQueue`
5. `Invoke-CycleChecks.ps1` passes
6. Refresh `db-contract-manifest.json` to include Phase 25-28 additions (manifest refresh covers all of main chain Phases 25-28)
