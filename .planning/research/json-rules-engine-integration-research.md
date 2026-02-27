# Research: json-rules-engine + React Hook Form + Zod + shadcn/ui Integration

**Domain:** Manufacturing Quality Management - Inspection Forms with Conditional Logic
**Researched:** 2026-02-27
**Overall Confidence:** MEDIUM-HIGH (library APIs verified via official docs; integration patterns synthesized from multiple sources but no single authoritative reference exists for this exact combination)

---

## Table of Contents

1. [json-rules-engine Fundamentals](#1-json-rules-engine-fundamentals)
2. [React Hook Form + json-rules-engine Integration](#2-react-hook-form--json-rules-engine-integration)
3. [Zod Schema Generation from Rules](#3-zod-schema-generation-from-rules)
4. [Field Registry Pattern with Conditional Logic](#4-field-registry-pattern-with-conditional-logic)
5. [Server-Side Rule Evaluation](#5-server-side-rule-evaluation)
6. [Manufacturing QMS-Specific Patterns](#6-manufacturing-qms-specific-patterns)
7. [Pitfalls and Risks](#7-pitfalls-and-risks)
8. [Recommended Architecture](#8-recommended-architecture)
9. [Sources](#9-sources)

---

## 1. json-rules-engine Fundamentals

**Confidence: HIGH** (verified via official GitHub docs)

### Package Overview

- **Package:** `json-rules-engine` (npm)
- **Latest version:** 7.3.1 (published ~early 2025)
- **Weekly downloads:** ~240K-310K (healthy adoption)
- **Bundle size:** ~17kb gzipped
- **Isomorphic:** Runs in Node.js AND browser -- critical for client/server shared evaluation
- **Security:** No `eval()` usage
- **Dependencies:** Minimal

### Rule Definition Format

A rule is a JSON object with `conditions` and an `event`. This format is inherently database-friendly -- store as a JSONB/NVARCHAR(MAX) column.

```typescript
// This entire object is JSON-serializable and can be stored in a database column
interface InspectionFormRule {
  conditions: {
    all?: Condition[];  // AND logic
    any?: Condition[];  // OR logic
    not?: Condition;    // Negation
  };
  event: {
    type: string;       // e.g., 'field-visibility', 'field-required', 'field-value-constraint'
    params: Record<string, unknown>;  // e.g., { fieldId: 'photo_attachment', visible: true }
  };
  name?: string;        // Human-readable identifier for audit
  priority?: number;    // Higher = evaluated first (default: 1)
}

interface Condition {
  fact: string;           // The data point to evaluate (e.g., 'severity', 'inspectionType')
  operator: string;       // Comparison operator
  value: unknown;         // Expected value
  path?: string;          // JSONPath for nested data (e.g., '$.responses.severity')
  params?: Record<string, unknown>;  // Passed to dynamic fact functions
}
```

### Built-in Operators

| Operator | Works On | Description |
|----------|----------|-------------|
| `equal` | string, number, boolean | Strict equality |
| `notEqual` | string, number, boolean | Strict inequality |
| `lessThan` | number | < |
| `lessThanInclusive` | number | <= |
| `greaterThan` | number | > |
| `greaterThanInclusive` | number | >= |
| `in` | any | Value exists in array |
| `notIn` | any | Value not in array |
| `contains` | string, array | String contains substring / array contains element |
| `doesNotContain` | string, array | Negation of contains |

### Operator Decorators

Operators can be composed with decorators using dot notation:
- `some.equal` -- at least one array element equals value
- `every.greaterThan` -- all array elements are greater than value
- `none.equal` -- no array element equals value

### Custom Operators for Forms

This is critical for our use case. Custom operators let us define form-specific comparisons:

```typescript
import { Engine } from 'json-rules-engine';

function createFormRulesEngine(): Engine {
  const engine = new Engine([], { allowUndefinedFacts: true });

  // Form-specific operators

  // Check if a field has a non-empty value (handles strings, arrays, null/undefined)
  engine.addOperator('isNotEmpty', (factValue: unknown) => {
    if (factValue === null || factValue === undefined) return false;
    if (typeof factValue === 'string') return factValue.trim().length > 0;
    if (Array.isArray(factValue)) return factValue.length > 0;
    return true;
  });

  engine.addOperator('isEmpty', (factValue: unknown) => {
    if (factValue === null || factValue === undefined) return true;
    if (typeof factValue === 'string') return factValue.trim().length === 0;
    if (Array.isArray(factValue)) return factValue.length === 0;
    return false;
  });

  // Numeric tolerance check: factValue is within +/- jsonValue of a target
  // Usage: { fact: 'measurement', operator: 'withinTolerance', value: { target: 2.5, tolerance: 0.1 } }
  engine.addOperator('withinTolerance', (factValue: number, jsonValue: { target: number; tolerance: number }) => {
    return Math.abs(factValue - jsonValue.target) <= jsonValue.tolerance;
  });

  // Check if value matches any of several patterns (useful for inspection type grouping)
  engine.addOperator('matchesAny', (factValue: string, jsonValue: string[]) => {
    return jsonValue.includes(factValue);
  });

  return engine;
}
```

### Rule Serialization for Database Storage

Rules serialize naturally to JSON. The `toJSON()` method on Rule instances produces a plain object or string:

```typescript
// Saving to database
const ruleDefinition = {
  conditions: {
    all: [
      { fact: 'severity', operator: 'equal', value: 'Critical' }
    ]
  },
  event: {
    type: 'field-required',
    params: { fieldId: 'photo_attachment' }
  },
  name: 'critical-severity-requires-photo',
  priority: 10
};

// This is already plain JSON -- store directly in database
// SQL Server: NVARCHAR(MAX) column with JSON validation
// The rule definition IS the database representation

// Loading from database
const rulesFromDb: RuleDefinition[] = await api.getFormRules(templateId);
const engine = createFormRulesEngine();
rulesFromDb.forEach(rule => engine.addRule(rule));
```

### Rule Versioning and Audit Trail Pattern

Since rules are just JSON, versioning is straightforward:

```sql
-- Database schema for rule storage (conceptual -- actual schema lives in sf-quality-db)
-- Rules are stored per template revision, not globally
-- When a template revision is published, its rules are frozen with it

-- The inspection.InspectionTemplateField already has criteria tables
-- Rules could live in a new table or as a JSON column on existing tables:
--   inspection.InspectionTemplateRevisionRules (RuleDefinitionJson NVARCHAR(MAX))
-- OR
--   inspection.InspectionTemplateFieldConditionalRule per field
```

**Key design decision:** Rules are bound to a template revision, not the template family. When a new revision is created, rules are copied and can be modified independently. This aligns with the existing "in-progress inspections complete under the old revision" pattern (Decision 1 from `00_key_decisions.md`).

---

## 2. React Hook Form + json-rules-engine Integration

**Confidence: MEDIUM** (synthesized from multiple sources; no canonical library exists for this exact integration)

### The Async Bridge Problem

This is the core engineering challenge identified in the research consolidation.

**The tension:**
- `engine.run(facts)` returns a `Promise` -- it is async
- React rendering is synchronous -- you cannot `await` inside a render function
- React Hook Form's `watch()` triggers synchronous re-renders

**The solution:** Treat rule evaluation results as React state. Evaluate rules in a `useEffect`, store results in state, and let the component re-render when results change.

### The `useFormRules` Hook

This is the recommended integration pattern. It bridges the async rule engine with synchronous React rendering.

```typescript
import { useEffect, useRef, useState, useMemo, useCallback } from 'react';
import { useWatch, type UseFormReturn, type FieldValues } from 'react-hook-form';
import { Engine, type EngineResult } from 'json-rules-engine';

// ---- Types ----

export interface FormRuleEffect {
  /** Fields that should be visible (by fieldId) */
  visibleFields: Set<string>;
  /** Fields that are required (by fieldId) */
  requiredFields: Set<string>;
  /** Field-level validation constraints (by fieldId) */
  fieldConstraints: Map<string, FieldConstraint>;
  /** Section visibility (by sectionId) */
  visibleSections: Set<string>;
  /** Custom messages to display (e.g., warnings) */
  messages: FormRuleMessage[];
}

export interface FieldConstraint {
  min?: number;
  max?: number;
  pattern?: string;
  customMessage?: string;
}

export interface FormRuleMessage {
  type: 'warning' | 'info' | 'error';
  fieldId?: string;
  sectionId?: string;
  message: string;
}

// Default state: everything visible, nothing conditionally required
const DEFAULT_EFFECTS: FormRuleEffect = {
  visibleFields: new Set(),       // empty = no override, show all
  requiredFields: new Set(),
  fieldConstraints: new Map(),
  visibleSections: new Set(),
  messages: [],
};

// ---- Event Type Constants ----

export const RULE_EVENTS = {
  FIELD_VISIBLE: 'field-visible',
  FIELD_HIDDEN: 'field-hidden',
  FIELD_REQUIRED: 'field-required',
  FIELD_OPTIONAL: 'field-optional',
  FIELD_CONSTRAINT: 'field-constraint',
  SECTION_VISIBLE: 'section-visible',
  SECTION_HIDDEN: 'section-hidden',
  SHOW_MESSAGE: 'show-message',
} as const;

// ---- Hook ----

interface UseFormRulesOptions<T extends FieldValues> {
  form: UseFormReturn<T>;
  engine: Engine | null;
  /** All field IDs in the form -- used to determine default visibility */
  allFieldIds: string[];
  /** All section IDs in the form */
  allSectionIds: string[];
  /** Debounce delay in ms (default: 150) */
  debounceMs?: number;
  /** Whether rules have loaded yet */
  enabled?: boolean;
}

interface UseFormRulesReturn {
  effects: FormRuleEffect;
  /** True while rule evaluation is in progress */
  evaluating: boolean;
  /** Error from last evaluation, if any */
  error: Error | null;
  /** Force re-evaluation */
  reEvaluate: () => void;
}

export function useFormRules<T extends FieldValues>({
  form,
  engine,
  allFieldIds,
  allSectionIds,
  debounceMs = 150,
  enabled = true,
}: UseFormRulesOptions<T>): UseFormRulesReturn {
  const [effects, setEffects] = useState<FormRuleEffect>(() => ({
    ...DEFAULT_EFFECTS,
    visibleFields: new Set(allFieldIds),
    visibleSections: new Set(allSectionIds),
  }));
  const [evaluating, setEvaluating] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // Watch ALL form values -- triggers re-render on any change
  const formValues = useWatch({ control: form.control });

  // Ref to track the latest evaluation request (for debounce cancellation)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const evaluate = useCallback(async () => {
    if (!engine || !enabled) return;

    // Cancel any in-flight evaluation
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setEvaluating(true);
    setError(null);

    try {
      // Run the engine with current form values as facts
      const result: EngineResult = await engine.run(formValues as Record<string, unknown>);

      // Check if this evaluation was cancelled
      if (controller.signal.aborted) return;

      // Process events into effects
      const newEffects = processEngineResults(result, allFieldIds, allSectionIds);
      setEffects(newEffects);
    } catch (err) {
      if (!controller.signal.aborted) {
        setError(err instanceof Error ? err : new Error(String(err)));
      }
    } finally {
      if (!controller.signal.aborted) {
        setEvaluating(false);
      }
    }
  }, [engine, enabled, formValues, allFieldIds, allSectionIds]);

  // Debounced evaluation on form value changes
  useEffect(() => {
    if (!engine || !enabled) return;

    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }

    timerRef.current = setTimeout(() => {
      evaluate();
    }, debounceMs);

    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, [evaluate, debounceMs, engine, enabled]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      abortRef.current?.abort();
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []);

  return { effects, evaluating, error, reEvaluate: evaluate };
}

// ---- Event Processing ----

function processEngineResults(
  result: EngineResult,
  allFieldIds: string[],
  allSectionIds: string[]
): FormRuleEffect {
  // Start with all fields/sections visible, nothing conditionally required
  const visibleFields = new Set(allFieldIds);
  const visibleSections = new Set(allSectionIds);
  const requiredFields = new Set<string>();
  const fieldConstraints = new Map<string, FieldConstraint>();
  const messages: FormRuleMessage[] = [];

  // Process successful rule events (conditions were met)
  for (const event of result.events) {
    const params = event.params as Record<string, unknown>;

    switch (event.type) {
      case RULE_EVENTS.FIELD_HIDDEN:
        visibleFields.delete(params.fieldId as string);
        break;

      case RULE_EVENTS.FIELD_REQUIRED:
        requiredFields.add(params.fieldId as string);
        break;

      case RULE_EVENTS.FIELD_CONSTRAINT:
        fieldConstraints.set(params.fieldId as string, params.constraint as FieldConstraint);
        break;

      case RULE_EVENTS.SECTION_HIDDEN:
        visibleSections.delete(params.sectionId as string);
        // Also hide all fields in the hidden section
        const sectionFieldIds = params.fieldIds as string[] | undefined;
        sectionFieldIds?.forEach(id => visibleFields.delete(id));
        break;

      case RULE_EVENTS.SHOW_MESSAGE:
        messages.push({
          type: params.messageType as 'warning' | 'info' | 'error',
          fieldId: params.fieldId as string | undefined,
          sectionId: params.sectionId as string | undefined,
          message: params.message as string,
        });
        break;

      // FIELD_VISIBLE and SECTION_VISIBLE are no-ops since default is visible
      // They exist so rules can be written in positive or negative form
    }
  }

  return { visibleFields, requiredFields, fieldConstraints, visibleSections, messages };
}
```

### Performance Considerations

**Rule evaluation timing (based on json-rules-engine benchmarks from GitHub issues):**
- 37 simple rules: ~49ms
- For a typical inspection form with 10-30 conditional rules: expect <20ms per evaluation
- This is well within the 150ms debounce window

**Optimization strategies:**

1. **Debounce at 150ms** -- prevents rapid-fire evaluations as users type. For dropdown/toggle changes (where the value changes discretely, not character-by-character), consider a shorter 50ms debounce or immediate evaluation.

2. **Engine instance reuse** -- Create the engine once when rules are loaded, not on every render. The engine caches fact computations within a single `run()` call.

3. **Selective re-evaluation** -- For very complex forms, you could split rules by section and only re-evaluate the section whose values changed. This is premature optimization for v1 but worth noting.

4. **`allowUndefinedFacts: true`** -- Critical setting. Without it, the engine throws if a fact (form field) doesn't exist yet (e.g., a field in a later section). With it, undefined facts simply fail their conditions gracefully.

```typescript
// Engine configuration for forms
const engine = new Engine([], {
  allowUndefinedFacts: true,  // REQUIRED: fields may not exist yet
});
```

### Real-World Usage Pattern

```typescript
// In an inspection form page component
function InspectionFillPage({ templateId }: { templateId: string }) {
  const { data: template } = useInspectionTemplate(templateId);
  const { data: rules } = useInspectionFormRules(templateId);

  const form = useForm<InspectionFormValues>({
    resolver: zodResolver(baseSchema),  // Base schema; dynamic schema built below
    defaultValues: buildDefaultValues(template),
  });

  // Create engine instance when rules load
  const engine = useMemo(() => {
    if (!rules) return null;
    const eng = createFormRulesEngine();
    rules.forEach(rule => eng.addRule(rule));
    return eng;
  }, [rules]);

  // Bridge: async rules -> sync React state
  const { effects, evaluating } = useFormRules({
    form,
    engine,
    allFieldIds: template?.fields.map(f => f.fieldId) ?? [],
    allSectionIds: template?.sections.map(s => s.sectionId) ?? [],
  });

  return (
    <FormProvider {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        {template?.sections.map(section => (
          <SectionRenderer
            key={section.sectionId}
            section={section}
            visible={effects.visibleSections.has(section.sectionId)}
            effects={effects}
          />
        ))}
      </form>
    </FormProvider>
  );
}
```

---

## 3. Zod Schema Generation from Rules

**Confidence: MEDIUM** (pattern synthesized from Zod docs + community patterns; no canonical approach exists)

### The Challenge

React Hook Form uses a Zod resolver for validation. When rules change which fields are required, the Zod schema must change too. But Zod schemas are typically static.

### Recommended Pattern: Base Schema + Dynamic Refinement

The recommended approach uses a **two-layer validation strategy**:

1. **Base Zod schema** -- All conditionally-required fields are `.optional()`. This schema is static and type-safe.
2. **Dynamic validation via `superRefine`** -- Uses rule evaluation results to enforce conditional requirements at validation time.

```typescript
import { z } from 'zod';

// ---- Base Schema ----
// All conditionally-visible/required fields are optional in the base schema
// This gives us the correct TypeScript type (all fields exist, some optional)

function buildBaseSchema(template: InspectionTemplate): z.ZodObject<any> {
  const shape: Record<string, z.ZodTypeAny> = {};

  for (const section of template.sections) {
    for (const field of section.fields) {
      switch (field.fieldTypeCode) {
        case 'NUMERIC':
          shape[field.fieldId] = z.number().optional().nullable();
          break;
        case 'ATTRIBUTE':
          shape[field.fieldId] = z.enum(['PASS', 'FAIL', 'NA']).optional().nullable();
          break;
        case 'TEXT':
          shape[field.fieldId] = z.string().optional().nullable();
          break;
        case 'DATETIME':
          shape[field.fieldId] = z.string().datetime().optional().nullable();
          break;
        case 'SELECTION_SINGLE':
          shape[field.fieldId] = z.string().optional().nullable();
          break;
        case 'SELECTION_MULTI':
          shape[field.fieldId] = z.array(z.string()).optional().nullable();
          break;
        case 'PHOTO_ATTACHMENT':
          shape[field.fieldId] = z.array(z.string()).optional().nullable(); // array of DocumentIds
          break;
      }
    }
  }

  return z.object(shape);
}

// ---- Dynamic Schema with Rule Effects ----

function buildDynamicSchema(
  baseSchema: z.ZodObject<any>,
  effects: FormRuleEffect
): z.ZodType<any> {
  return baseSchema.superRefine((data, ctx) => {
    // Enforce conditional required fields
    for (const fieldId of effects.requiredFields) {
      // Only validate if the field is also visible
      if (!effects.visibleFields.has(fieldId)) continue;

      const value = data[fieldId];
      if (value === null || value === undefined || value === '' ||
          (Array.isArray(value) && value.length === 0)) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: [fieldId],
          message: 'This field is required',
        });
      }
    }

    // Enforce dynamic constraints
    for (const [fieldId, constraint] of effects.fieldConstraints) {
      if (!effects.visibleFields.has(fieldId)) continue;

      const value = data[fieldId];
      if (value === null || value === undefined) continue;

      if (constraint.min !== undefined && typeof value === 'number' && value < constraint.min) {
        ctx.addIssue({
          code: z.ZodIssueCode.too_small,
          path: [fieldId],
          minimum: constraint.min,
          inclusive: true,
          type: 'number',
          message: constraint.customMessage ?? `Must be at least ${constraint.min}`,
        });
      }

      if (constraint.max !== undefined && typeof value === 'number' && value > constraint.max) {
        ctx.addIssue({
          code: z.ZodIssueCode.too_big,
          path: [fieldId],
          maximum: constraint.max,
          inclusive: true,
          type: 'number',
          message: constraint.customMessage ?? `Must be at most ${constraint.max}`,
        });
      }
    }

    // Strip hidden fields (so they don't fail validation for being empty)
    // This is handled by the custom resolver below
  });
}
```

### Custom Resolver That Prunes Hidden Fields

The key insight from the Zod + conditional logic community pattern: **prune hidden fields before validation** so they do not trigger required-field errors.

```typescript
import { zodResolver } from '@hookform/resolvers/zod';
import type { Resolver } from 'react-hook-form';

/**
 * Creates a React Hook Form resolver that:
 * 1. Strips values for hidden fields (so they don't fail validation)
 * 2. Validates using the dynamic schema (base + rule effects)
 */
function createRulesAwareResolver(
  baseSchema: z.ZodObject<any>,
  effectsRef: React.RefObject<FormRuleEffect>
): Resolver<any> {
  return async (values, context, options) => {
    const effects = effectsRef.current;

    // Prune hidden fields from validation data
    const prunedValues = { ...values };
    for (const key of Object.keys(prunedValues)) {
      if (effects && !effects.visibleFields.has(key)) {
        delete prunedValues[key];
      }
    }

    // Build dynamic schema from current effects
    const dynamicSchema = effects
      ? buildDynamicSchema(baseSchema, effects)
      : baseSchema;

    // Delegate to standard zodResolver
    const resolver = zodResolver(dynamicSchema);
    return resolver(prunedValues, context, options);
  };
}
```

### Sharing Validation Between Client and Server

```typescript
// shared/validation/inspection-form-validation.ts
// This file can be imported by both client and server

import { z } from 'zod';
import { Engine } from 'json-rules-engine';

export interface ValidationResult {
  success: boolean;
  errors: Array<{ fieldId: string; message: string }>;
}

/**
 * Validate inspection form data against rules -- works on client AND server.
 * The key: both environments use the same engine + rules + Zod schema.
 */
export async function validateInspectionForm(
  formData: Record<string, unknown>,
  ruleDefinitions: RuleDefinition[],
  template: InspectionTemplate
): Promise<ValidationResult> {
  // 1. Evaluate rules to get effects
  const engine = createFormRulesEngine();
  ruleDefinitions.forEach(rule => engine.addRule(rule));
  const result = await engine.run(formData);
  const effects = processEngineResults(
    result,
    template.fields.map(f => f.fieldId),
    template.sections.map(s => s.sectionId)
  );

  // 2. Build dynamic Zod schema
  const baseSchema = buildBaseSchema(template);
  const dynamicSchema = buildDynamicSchema(baseSchema, effects);

  // 3. Prune hidden fields
  const prunedData = { ...formData };
  for (const key of Object.keys(prunedData)) {
    if (!effects.visibleFields.has(key)) {
      delete prunedData[key];
    }
  }

  // 4. Validate
  const zodResult = dynamicSchema.safeParse(prunedData);

  if (zodResult.success) {
    return { success: true, errors: [] };
  }

  return {
    success: false,
    errors: zodResult.error.issues.map(issue => ({
      fieldId: issue.path[0] as string,
      message: issue.message,
    })),
  };
}
```

---

## 4. Field Registry Pattern with Conditional Logic

**Confidence: HIGH** (this pattern is well-established in the existing architecture docs at `04_frontend_form_builder_architecture.md`)

### Registry Definition

The field registry maps field type codes to shadcn/ui components. Rules determine WHICH fields appear; the registry determines HOW they render.

```typescript
import type { FieldValues, Path, UseFormReturn } from 'react-hook-form';

// ---- Field Component Props ----

export interface InspectionFieldProps<T extends FieldValues = FieldValues> {
  field: InspectionTemplateField;  // From API: label, helpText, criteria, etc.
  form: UseFormReturn<T>;
  name: Path<T>;                   // React Hook Form field name
  disabled?: boolean;
  required?: boolean;              // Driven by rule effects
  constraint?: FieldConstraint;    // Driven by rule effects
}

// ---- Registry ----

type FieldTypeCode = 'NUMERIC' | 'ATTRIBUTE' | 'TEXT' | 'DATETIME' | 'SELECTION_SINGLE' | 'SELECTION_MULTI' | 'PHOTO_ATTACHMENT';

const fieldRegistry: Record<FieldTypeCode, React.ComponentType<InspectionFieldProps>> = {
  NUMERIC: NumericMeasurementField,
  ATTRIBUTE: PassFailField,
  TEXT: TextField,
  DATETIME: DateTimeField,
  SELECTION_SINGLE: SelectField,
  SELECTION_MULTI: MultiSelectField,
  PHOTO_ATTACHMENT: PhotoAttachmentField,
};

// ---- Renderer ----

function FieldRenderer({ field, form, effects }: {
  field: InspectionTemplateField;
  form: UseFormReturn<any>;
  effects: FormRuleEffect;
}) {
  const Component = fieldRegistry[field.fieldTypeCode as FieldTypeCode];

  if (!Component) {
    console.warn(`No component registered for field type: ${field.fieldTypeCode}`);
    return null;
  }

  // Rule-driven visibility
  const isVisible = effects.visibleFields.has(field.fieldId);
  if (!isVisible) return null;

  // Rule-driven required status
  const isRequired = field.isRequired || effects.requiredFields.has(field.fieldId);

  // Rule-driven constraints
  const constraint = effects.fieldConstraints.get(field.fieldId);

  return (
    <FormField
      control={form.control}
      name={field.fieldId}
      render={({ field: rhfField }) => (
        <FormItem>
          <FormLabel>
            {field.label}
            {isRequired && <span className="text-destructive ml-1">*</span>}
          </FormLabel>
          <FormControl>
            <Component
              field={field}
              form={form}
              name={field.fieldId}
              required={isRequired}
              constraint={constraint}
            />
          </FormControl>
          {field.helpText && <FormDescription>{field.helpText}</FormDescription>}
          <FormMessage />
        </FormItem>
      )}
    />
  );
}
```

### Section-Level Conditional Logic

Rules can control entire section visibility. This is important for inspection forms where entire sections are contextual (e.g., "Supplier Information" only shown for Receiving inspections).

```typescript
function SectionRenderer({ section, form, effects }: {
  section: InspectionTemplateSection;
  form: UseFormReturn<any>;
  effects: FormRuleEffect;
}) {
  const isVisible = effects.visibleSections.has(section.sectionId);

  if (!isVisible) return null;

  // Get messages for this section
  const sectionMessages = effects.messages.filter(
    m => m.sectionId === section.sectionId
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle>{section.label}</CardTitle>
        {section.description && (
          <CardDescription>{section.description}</CardDescription>
        )}
        {sectionMessages.map((msg, i) => (
          <Alert key={i} variant={msg.type === 'error' ? 'destructive' : 'default'}>
            <AlertDescription>{msg.message}</AlertDescription>
          </Alert>
        ))}
      </CardHeader>
      <CardContent className="space-y-4">
        {section.fields
          .sort((a, b) => a.sortOrder - b.sortOrder)
          .map(field => (
            <FieldRenderer
              key={field.fieldId}
              field={field}
              form={form}
              effects={effects}
            />
          ))}
      </CardContent>
    </Card>
  );
}
```

### Example: NumericMeasurementField with shadcn/ui

```typescript
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';

function NumericMeasurementField({ field, form, name, required, constraint }: InspectionFieldProps) {
  const value = form.watch(name);
  const criteria = field.criteria as NumericCriteria | undefined;

  // Real-time courtesy evaluation (server is authoritative)
  const evaluation = useMemo(() => {
    if (!criteria || value === null || value === undefined) return null;
    const numVal = Number(value);
    if (isNaN(numVal)) return null;

    if (criteria.lsl !== null && numVal < criteria.lsl) return 'FAIL';
    if (criteria.usl !== null && numVal > criteria.usl) return 'FAIL';
    if (criteria.target !== null) {
      // Within tolerance of target
      const tolerance = constraint?.max ?? criteria.tolerance ?? Infinity;
      if (Math.abs(numVal - criteria.target) > tolerance) return 'WARN';
    }
    return 'PASS';
  }, [value, criteria, constraint]);

  return (
    <div className="flex items-center gap-2">
      <Input
        type="number"
        inputMode="decimal"   // numeric keypad on mobile (shop floor UX)
        step="any"
        placeholder={criteria?.target !== null ? `Target: ${criteria?.target}` : undefined}
        {...form.register(name, { valueAsNumber: true })}
        className="font-mono"
      />
      {criteria?.unitOfMeasure && (
        <span className="text-sm text-muted-foreground">{criteria.unitOfMeasure}</span>
      )}
      {evaluation && (
        <Badge variant={evaluation === 'PASS' ? 'default' : evaluation === 'WARN' ? 'outline' : 'destructive'}>
          {evaluation}
        </Badge>
      )}
    </div>
  );
}
```

---

## 5. Server-Side Rule Evaluation

**Confidence: HIGH** (json-rules-engine is isomorphic; server patterns are straightforward)

### Architecture: Client Evaluates for UX, Server Enforces

```
Client (browser)                          Server (Next.js API route / Server Action)
-------------------                       -------------------------------------------
1. User changes field value
2. useFormRules runs engine.run()
3. UI updates (show/hide fields)
4. User submits form
5. Client-side Zod validation
6. POST to /api/inspections/{id}/submit   7. Load rules from DB
                                          8. engine.run(submittedData) -- same rules
                                          9. Validate: all required fields present?
                                          10. Validate: no hidden fields submitted?
                                          11. Call inspection.usp_SubmitInspection
                                          12. Return result
```

### Server-Side Implementation (Next.js Server Action or API Route)

```typescript
// app/api/inspections/[id]/submit/route.ts
// OR as a Server Action

import { Engine } from 'json-rules-engine';
import { validateInspectionForm } from '@/shared/validation/inspection-form-validation';

export async function POST(
  request: Request,
  { params }: { params: { id: string } }
) {
  const inspectionId = params.id;
  const formData = await request.json();

  // 1. Load the inspection + template + rules from the API
  const inspection = await api.getInspection(inspectionId);
  const template = await api.getInspectionTemplate(inspection.templateRevisionId);
  const rules = await api.getInspectionFormRules(inspection.templateRevisionId);

  // 2. Server-side validation using SAME engine + rules
  const validation = await validateInspectionForm(formData, rules, template);

  if (!validation.success) {
    return Response.json(
      { errors: validation.errors },
      { status: 422 }
    );
  }

  // 3. Strip hidden fields before sending to DB
  // (Prevent client from injecting data into fields they shouldn't see)
  const engine = createFormRulesEngine();
  rules.forEach(rule => engine.addRule(rule));
  const result = await engine.run(formData);
  const effects = processEngineResults(result, /* ... */);

  const sanitizedData: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(formData)) {
    if (effects.visibleFields.has(key)) {
      sanitizedData[key] = value;
    }
    // Hidden fields are silently dropped -- not an error, just ignored
  }

  // 4. Submit to the actual API (which calls the stored procedure)
  const submitResult = await api.submitInspection(inspectionId, sanitizedData);

  return Response.json(submitResult);
}
```

### Security Considerations

**Why server re-evaluation is non-negotiable:**
- A user could modify the client JavaScript to skip rule evaluation
- A user could submit data for hidden fields (data injection)
- A user could omit required fields that rules say are mandatory
- The server is the only trustworthy enforcement point

**The constraint from `04_frontend_form_builder_architecture.md` (line 2):**
> No business logic in the UI. SQL gate procedures are authoritative; zod is courtesy UX validation only.

This aligns perfectly. The rule engine on the client is **courtesy UX** -- it makes the form responsive and user-friendly. The rule engine on the server is **enforcement** -- it prevents bypass. The stored procedure (`inspection.usp_SubmitInspection`) is **authoritative** -- it performs the final evaluation.

### Three-Layer Validation Stack

| Layer | Purpose | Technology | Failure Mode |
|-------|---------|------------|-------------|
| 1. Client Zod | Instant UX feedback | Zod + RHF zodResolver | Inline field errors |
| 2. Server Rules | Conditional enforcement | json-rules-engine + Zod safeParse | 422 with field-level errors |
| 3. Stored Procedure | Authoritative business rules | SQL (inspection.usp_SubmitInspection) | SQL error codes mapped to HTTP |

---

## 6. Manufacturing QMS-Specific Patterns

**Confidence: MEDIUM** (domain patterns synthesized from reference architecture docs; QMS-specific rule patterns are original design work)

### Inspection Checklist Rules

Common rule patterns for manufacturing quality inspections:

#### Pattern A: Severity-Driven Requirements

```json
{
  "name": "critical-severity-requires-photo",
  "priority": 10,
  "conditions": {
    "all": [
      { "fact": "severity", "operator": "equal", "value": "Critical" }
    ]
  },
  "event": {
    "type": "field-required",
    "params": { "fieldId": "photo_attachment" }
  }
}
```

#### Pattern B: Inspection Type Shows/Hides Sections

```json
{
  "name": "receiving-inspection-shows-supplier-section",
  "priority": 5,
  "conditions": {
    "all": [
      { "fact": "inspectionType", "operator": "notEqual", "value": "Receiving" }
    ]
  },
  "event": {
    "type": "section-hidden",
    "params": {
      "sectionId": "supplier_information",
      "fieldIds": ["supplier_name", "supplier_lot", "supplier_cert_number"]
    }
  }
}
```

Note: The rule hides the section when the type is NOT Receiving. This "hide when condition fails" pattern is cleaner than "show when condition passes" because the default state is "visible."

#### Pattern C: Measurement Tolerance Warning

```json
{
  "name": "thickness-near-limit-warning",
  "priority": 3,
  "conditions": {
    "all": [
      { "fact": "coating_thickness", "operator": "greaterThan", "value": 0 },
      { "fact": "coating_thickness", "operator": "lessThan", "value": 1.5 }
    ]
  },
  "event": {
    "type": "show-message",
    "params": {
      "fieldId": "coating_thickness",
      "messageType": "warning",
      "message": "Measurement is below 1.5 mil -- approaching lower spec limit"
    }
  }
}
```

#### Pattern D: Conditional Field Chaining

```json
[
  {
    "name": "fail-result-requires-disposition",
    "conditions": {
      "all": [
        { "fact": "overall_result", "operator": "equal", "value": "FAIL" }
      ]
    },
    "event": {
      "type": "field-required",
      "params": { "fieldId": "disposition_action" }
    }
  },
  {
    "name": "rework-disposition-requires-rework-instructions",
    "conditions": {
      "all": [
        { "fact": "overall_result", "operator": "equal", "value": "FAIL" },
        { "fact": "disposition_action", "operator": "equal", "value": "REWORK" }
      ]
    },
    "event": {
      "type": "field-required",
      "params": { "fieldId": "rework_instructions" }
    }
  }
]
```

### Escalation Rules (NCR Auto-Creation)

These rules are evaluated server-side only (not in the form UI). They determine whether submitting an inspection should auto-create an NCR.

```json
{
  "name": "auto-ncr-on-critical-fail",
  "priority": 100,
  "conditions": {
    "all": [
      { "fact": "overallResult", "operator": "equal", "value": "FAIL" },
      { "fact": "severity", "operator": "equal", "value": "Critical" },
      { "fact": "failedFieldCount", "operator": "greaterThan", "value": 0 }
    ]
  },
  "event": {
    "type": "auto-create-ncr",
    "params": {
      "ncrType": "CRITICAL_INSPECTION_FAILURE",
      "includePhotos": true,
      "requireImmediateContainment": true
    }
  }
}
```

**Important:** NCR auto-creation rules should NOT be evaluated client-side. They are a server-side concern handled by `inspection.usp_SubmitInspection`. The JSON format is useful for storing the trigger configuration in the database, but the actual NCR creation is a stored procedure responsibility.

### Approval Gate Rules

```json
{
  "name": "supervisor-signoff-for-critical",
  "conditions": {
    "all": [
      { "fact": "severity", "operator": "in", "value": ["Critical", "Major"] },
      { "fact": "overallResult", "operator": "equal", "value": "FAIL" }
    ]
  },
  "event": {
    "type": "require-approval",
    "params": {
      "approvalType": "supervisor-signoff",
      "message": "Critical/Major failures require supervisor review before submission"
    }
  }
}
```

### Rule Categories

For maintainability, categorize rules by their evaluation context:

| Category | Evaluated Where | Purpose |
|----------|----------------|---------|
| `form-visibility` | Client + Server | Show/hide fields and sections |
| `form-validation` | Client + Server | Required fields, value constraints |
| `form-ux` | Client only | Warning messages, helper text |
| `escalation` | Server only | NCR auto-creation, notification triggers |
| `approval` | Server only | Workflow gating, supervisor sign-off |

Store the category with each rule in the database so the client can filter and only load rules it needs.

---

## 7. Pitfalls and Risks

### Critical Pitfall: Stale Effects During Rapid Input

**What goes wrong:** User rapidly changes a field value. The debounced rule evaluation hasn't fired yet. The user sees stale visibility/required state and tries to submit.

**Prevention:**
- Show a subtle loading indicator when `evaluating` is true (e.g., a small spinner in the form header)
- On submit, force a synchronous-feeling validation: trigger rule evaluation, wait for it to complete, then validate
- The debounce is 150ms -- fast enough that this is rarely noticeable, but the submit handler should still await the latest evaluation

```typescript
const handleSubmit = async (data: any) => {
  // Force fresh evaluation before submit
  await reEvaluate();
  // Now validate with latest effects
  const validation = await validateInspectionForm(data, rules, template);
  if (!validation.success) {
    // Show errors
    return;
  }
  // Proceed with submit
};
```

### Critical Pitfall: Rule Conflicts

**What goes wrong:** Two rules contradict each other. Rule A says "show field X" when severity=Critical. Rule B says "hide field X" when inspectionType=Final. What happens when severity=Critical AND inspectionType=Final?

**Prevention:**
- Use the `priority` field. Higher priority rules win.
- Establish a convention: "hide" rules should have higher priority than "show" rules (safety-first: if in doubt, hide)
- Build a rule conflict detector as a validation tool for template authors

### Moderate Pitfall: TypeScript Type Safety Erosion

**What goes wrong:** Because fields are dynamically generated from template definitions, TypeScript cannot statically type the form values. You lose autocomplete and compile-time checks.

**Prevention:**
- Accept this trade-off for the dynamic form renderer. The form builder is inherently runtime-typed.
- Use runtime validation (Zod) as the safety net instead of compile-time types
- For non-dynamic parts of the app (e.g., the template builder itself), use strict TypeScript types

### Moderate Pitfall: Hidden Field Data Leakage

**What goes wrong:** A user fills in a field, then a rule hides it. The value persists in React Hook Form state. On submit, the hidden field's stale value is sent to the server.

**Prevention:**
- The server-side rule evaluation strips hidden fields (see Section 5)
- Optionally, the client can clear hidden field values when they become hidden:

```typescript
// In useFormRules, when a field transitions from visible to hidden:
useEffect(() => {
  const prevVisible = prevEffectsRef.current?.visibleFields;
  if (!prevVisible) return;

  for (const fieldId of prevVisible) {
    if (!effects.visibleFields.has(fieldId)) {
      // Field was visible, now hidden -- clear its value
      form.setValue(fieldId as any, null, { shouldValidate: false });
    }
  }
  prevEffectsRef.current = effects;
}, [effects, form]);
```

### Minor Pitfall: Rule Loading Race Condition

**What goes wrong:** The form renders before rules have loaded from the API. All fields are visible (default). Rules load, and suddenly fields disappear. Jarring UX.

**Prevention:**
- Show a loading skeleton until both template AND rules are loaded
- Only mount the form after rules are available:

```typescript
if (!template || !rules) return <InspectionFormSkeleton />;
```

### Minor Pitfall: json-rules-engine Bundle Size

**What goes wrong:** json-rules-engine is 17kb gzipped. Not huge, but worth noting for shop-floor devices with slow connections.

**Prevention:** This is a non-issue. 17kb is small. The shadcn/ui + React + React Hook Form bundle is already much larger.

---

## 8. Recommended Architecture

### Data Flow Diagram

```
Template Author (Quality Engineer)
    |
    v
Template Builder UI
    |  defines fields, sections, criteria
    |  defines conditional rules (JSON)
    v
Database
    |  inspection.InspectionTemplateRevision
    |  inspection.InspectionTemplateField
    |  inspection.InspectionTemplateFieldConditionalRule (rules as JSON)
    v
API (GET /v1/inspection-templates/{id})
    |  returns template definition + rules
    v
+-------------------------------------------+
| Inspection Fill Page (Client)             |
|                                           |
|  1. Load template + rules from API        |
|  2. Build base Zod schema from template   |
|  3. Create json-rules-engine Engine       |
|  4. Add rules to engine                   |
|  5. useFormRules() hook bridges            |
|     engine <-> React Hook Form            |
|  6. Field registry renders components     |
|     based on field type + rule effects    |
|  7. User fills form                       |
|  8. On submit: client Zod validation      |
|     (with rule-driven dynamic schema)     |
+-------------------------------------------+
    |
    v
Server (POST /v1/inspections/{id}/submit)
    |  1. Load same rules from DB
    |  2. Re-evaluate rules against submitted data
    |  3. Validate: required fields present, hidden fields stripped
    |  4. Call inspection.usp_SubmitInspection (authoritative)
    |  5. SP evaluates criteria, creates findings, optional NCR
    v
Response to Client
```

### File Structure Recommendation

```
sf-quality-app/src/
  lib/
    rules-engine/
      create-form-rules-engine.ts    # Engine factory with custom operators
      process-engine-results.ts       # Event -> FormRuleEffect converter
      types.ts                        # FormRuleEffect, FieldConstraint, etc.
      constants.ts                    # RULE_EVENTS enum
  hooks/
    use-form-rules.ts                # The async bridge hook
  features/
    inspections/
      components/
        inspection-fill-page.tsx
        section-renderer.tsx
        field-renderer.tsx
      fields/                        # Field registry components
        numeric-measurement-field.tsx
        pass-fail-field.tsx
        text-field.tsx
        datetime-field.tsx
        select-field.tsx
        multi-select-field.tsx
        photo-attachment-field.tsx
        index.ts                     # Registry export
      validation/
        build-base-schema.ts         # Template -> Zod base schema
        build-dynamic-schema.ts      # Effects -> Zod superRefine
        rules-aware-resolver.ts      # Custom RHF resolver
      hooks/
        use-inspection-form.ts       # Orchestrates form + rules + validation
  shared/
    validation/
      inspection-form-validation.ts  # Client + server shared validation
```

### Key Design Principles

1. **Rules describe effects, not implementation.** A rule says "field X is required" (event), not "add `.min(1)` to the Zod schema." The effect is interpreted by the UI layer and validation layer independently.

2. **Default is visible and optional.** All fields start visible and optional. Rules add constraints (hide, require). This is safer than the inverse.

3. **Three evaluation contexts.** Client (UX), Server (enforcement), Stored Procedure (authoritative). Each layer adds trust but also adds latency. The client layer is fastest but least trustworthy.

4. **Rules are versioned with templates.** A rule is bound to a template revision, not the global system. This supports audit trail requirements and controlled-document expectations.

5. **The engine is isomorphic.** The exact same `json-rules-engine` package and rule definitions run on both client and server. No translation layer needed.

---

## 9. Sources

### Official Documentation (HIGH confidence)
- [json-rules-engine GitHub - Rules Documentation](https://github.com/CacheControl/json-rules-engine/blob/master/docs/rules.md)
- [json-rules-engine GitHub - Engine Documentation](https://github.com/CacheControl/json-rules-engine/blob/master/docs/engine.md)
- [json-rules-engine GitHub - Walkthrough](https://github.com/CacheControl/json-rules-engine/blob/master/docs/walkthrough.md)
- [json-rules-engine GitHub - Custom Operators Example](https://github.com/CacheControl/json-rules-engine/blob/master/examples/06-custom-operators.js)
- [React Hook Form - watch API](https://react-hook-form.com/api/useform/watch/)
- [React Hook Form - useWatch](https://www.react-hook-form.com/api/usewatch/)
- [React Hook Form - Advanced Usage](https://www.react-hook-form.com/advanced-usage/)
- [shadcn/ui - Form Component](https://ui.shadcn.com/docs/components/form)
- [shadcn/ui - React Hook Form Integration](https://ui.shadcn.com/docs/forms/react-hook-form)

### Community Patterns (MEDIUM confidence)
- [Conditional Logic with Zod + React Hook Form](https://micahjon.com/2023/form-validation-with-zod/) - Key pattern for pruning hidden fields
- [Dynamically Modifying Validation Schemas in Zod](https://dev.to/yanagisawahidetoshi/dynamically-modifying-validation-schemas-in-zod-a-typescript-and-react-hook-form-example-3ho0) - superRefine pattern
- [Building Advanced React Forms Using React Hook Form, Zod and Shadcn](https://wasp.sh/blog/2025/01/22/advanced-react-hook-form-zod-shadcn) - Full stack integration
- [How I Built a Dynamic Rules Engine Without Writing a Single If-Else](https://javascript.plainenglish.io/how-i-built-a-dynamic-rules-engine-without-writing-a-single-if-else-my-discovery-of-426055901a86) - Real-world json-rules-engine usage

### Performance References (MEDIUM confidence)
- [json-rules-engine - Slow performance? (Issue #58)](https://github.com/CacheControl/json-rules-engine/issues/58) - 37 rules in ~49ms
- [json-rules-engine - Rule Evaluation for 10k rules (Issue #364)](https://github.com/CacheControl/json-rules-engine/issues/364) - Scale benchmarks

### Project-Internal References (HIGH confidence)
- `Reference_Architecture/Quality_Forms_Module/04_packages/quality-inspection-forms-module-package/docs/04_frontend_form_builder_architecture.md` - Field registry, component hierarchy, rendering pattern
- `Reference_Architecture/Quality_Forms_Module/04_packages/quality-inspection-forms-module-package/docs/00_key_decisions.md` - Template versioning, criteria types, workflow integration
- `Reference_Architecture/Quality_Forms_Module/04_packages/quality-inspection-forms-module-package/docs/05_integration_architecture.md` - Submit flow, NCR auto-creation, attachment handling
- `Reference_Architecture/Quality_Forms_Module/03_adjudication/quality-forms-module-final-authoritative-review.md` - Authoritative decisions on architecture
- `.planning/ROADMAP.md` - Phase 8 requirements for conditional field logic
