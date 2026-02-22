# App Implementation Notes

This folder is informational-only. The design package does not include a full Next.js project scaffold.

Use:
- `docs/04_frontend_form_builder_architecture.md` for the component hierarchy and state patterns.
- `docs/05_integration_architecture.md` for flows (template publish, due queue, submit + NCR).

Implementation constraints from the reference:
- Next.js App Router + Server Components
- shadcn/ui, Tailwind CSS 4
- TanStack Query for server state (no direct fetch from browser components)
- react-hook-form + zod for courtesy validation
