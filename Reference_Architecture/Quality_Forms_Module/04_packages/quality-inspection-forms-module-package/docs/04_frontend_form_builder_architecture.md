# Deliverable 4: Frontend Form Builder Architecture

Target stack (locked):
- Next.js App Router (v15)
- React 19
- Tailwind CSS 4
- shadcn/ui
- TanStack Query + Table
- react-hook-form + zod

Core constraints:
1. Browser components do **not** call the API directly. All API access goes through `src/lib/api.ts` (server-side) and TanStack Query hooks.
2. No business logic in the UI. SQL gate procedures are authoritative; zod is courtesy UX validation only.

---

## Route / Module Layout

Recommended route group:

- `src/app/(auth)/inspection-templates/*`
- `src/app/(auth)/inspections/*`
- `src/app/(auth)/production-runs/*`
- `src/app/(auth)/inspection-analytics/*` (later phase)

---

## Form Template Builder — Component Hierarchy

### Pages
- `/inspection-templates`
  - list families/current revisions, filters, create/clone actions
- `/inspection-templates/[templateId]`
  - draft editor + preview + publish panel
- `/inspection-templates/[templateId]/assignments`
  - assignment rules + schedule rules

### Core components
- `InspectionTemplateBuilderPage`
  - `TemplateHeaderForm`
  - `BuilderWorkspace`
    - `SectionNavigator`
    - `SectionCanvas`
      - `SectionCard`
        - `FieldList`
          - `FieldCard`
    - `FieldPalette`
  - `FieldEditorDrawer` (shadcn `Sheet`)
    - `FieldBasicsTab`
    - `CriteriaTab`
    - `OptionsTab` (selection fields only)
    - `AttachmentTab` (photo fields only)
    - `ConditionalLogicTab` (v2, keep simple in v1)
  - `TemplatePreviewPane`
  - `PublishBar` (save/validate/publish + approval banner)

### Drag & drop
- Use `@dnd-kit` for sortable sections/fields.
- Persist ordering via `SortOrder`.

---

## Builder State Management

### Local draft state
Use `react-hook-form` + `useFieldArray`:
- `sections[]`
- `sections[i].fields[]`
- `fields[j].options[]`

Zod schema validates:
- required labels
- numeric constraints formatting
- consistency rules (e.g., selection field must have options)

### Server state
TanStack Query hooks:
- `useInspectionTemplate(templateId)` → GET `/v1/inspection-templates/{id}`
- `useSaveInspectionTemplateDraftDefinition(templateId)` → PUT `/v1/inspection-templates/{id}`
- `usePublishInspectionTemplate(templateId)` → POST `/v1/inspection-templates/{id}/publish`
- `useAssignmentRules(familyId)` → list rules
- `useUpsertScheduleRule(ruleId)` → PUT schedule

Save strategy:
- v1: explicit “Save Draft”
- v2: optional autosave (debounced)

Approval-required publish/submit responses should handle `202 Accepted` as a pending-approval outcome, not a failure.

---

## Operator Form Fill Experience

### Pages
- `/inspections/due` — operator due queue
- `/inspections/[inspectionId]` — fill
- `/inspections/[inspectionId]/review` — supervisor review

### Due queue components
- `InspectionDueQueuePage`
  - `ProductionRunSelector`
  - `DueInspectionTable` (TanStack Table)
  - `StartInspectionDialog`

### Fill components
- `InspectionFillPage`
  - `InspectionContextHeader`
  - `InspectionFormRenderer` (dynamic)
    - `SectionRenderer`
      - `FieldRenderer` (registry)
        - `NumericMeasurementField`
        - `PassFailField`
        - `TextField`
        - `DateTimeField`
        - `SelectField`
        - `MultiSelectField`
        - `PhotoAttachmentField`
  - `SubmitBar` (save draft / submit)

---

## Dynamic Rendering Pattern

Backend delivers:
- Template revision definition (sections/fields/options/criteria)
- Field type identifiers (lookup values)

Frontend maps field type → component:

```ts
const registry: Record<FieldTypeCode, React.FC<FieldProps>> = {
  NUMERIC: NumericMeasurementField,
  ATTRIBUTE: PassFailField,
  TEXT: TextField,
  DATETIME: DateTimeField,
  SELECTION_SINGLE: SelectField,
  SELECTION_MULTI: MultiSelectField,
  PHOTO_ATTACHMENT: PhotoAttachmentField,
};
```

Real-time evaluation in UI is **courtesy only**:
- show pass/fail indicator for numeric fields using criteria limits
- final evaluation occurs server-side at submit

---

## Accessibility & Shop-Floor UX

Non-negotiable UX requirements:
- large touch targets
- numeric keypad for numeric input
- minimal typing (toggle/select over text)
- high-contrast support
- clear “saved” indicators
- safe draft autosave behavior (no surprise submissions)

Offline support is not in v1; instead:
- clearly detect and message connectivity loss
- keep local draft state until save succeeds
