# Quality Inspection Forms — Mermaid Diagrams Package

This is a **diagram-only companion package** to:

- `quality-inspection-forms-module-package.zip`

It extracts **every Mermaid diagram** from the module design docs and places them into individual files for:
- easy review
- embedding into other docs
- rendering with GitHub/Markdown or Mermaid CLI

---

## What’s included

- Individual diagram files in two formats:
  - `*.md` (recommended for GitHub rendering — contains a ` ```mermaid ` code fence)
  - `*.mmd` (raw Mermaid text for Mermaid CLI / tooling)
- `diagrams/source_map.json` mapping each diagram back to its source doc and heading.
- `reference/CODEBASE_REFERENCE.md` copied in for context.

---

## Render options

### GitHub / Markdown
Open any `diagrams/*.md` file — Mermaid will render automatically in most modern Markdown viewers that support Mermaid.

### Mermaid CLI (example)
```bash
mmdc -i diagrams/01_er_inspection_forms.mmd -o out/01_er_inspection_forms.svg
```

---

## Notes

- These diagrams are extracted verbatim from the architecture package to ensure consistency.
- If you add new Mermaid blocks to the main package docs later, regenerate this diagram package.
- Current sequence diagrams are aligned to versioned `/v1` routes and approval-required `202 Accepted` behavior.
