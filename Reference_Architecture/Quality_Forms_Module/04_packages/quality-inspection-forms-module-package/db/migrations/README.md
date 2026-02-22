# Inspection Module Migrations

These migrations are generated as a **package** and must be renumbered if your repo has advanced beyond migration 130.

Do not execute this set as-is until blocker fixes in the authoritative review are applied:
- `Reference_Architecture/Quality_Forms_Module/03_adjudication/quality-forms-module-final-authoritative-review.md`

After blocker closure, apply in order:

- 131_create_inspection_schema.sql
- 132_create_inspection_template_family.sql
- 133_create_inspection_template_revision.sql
- 134_create_inspection_template_section.sql
- 135_create_inspection_template_field.sql
- 136_create_inspection_template_field_option.sql
- 137_create_inspection_field_criteria.sql
- 138_create_inspection_criteria_numeric.sql
- 139_create_inspection_criteria_attribute.sql
- 140_create_inspection_criteria_selection.sql
- 141_create_inspection_criteria_allowed_option.sql
- 142_create_inspection_criteria_text.sql
- 143_create_inspection_assignment_rule.sql
- 144_create_inspection_schedule_rule.sql
- 145_create_production_run.sql
- 146_create_inspection_instance.sql
- 147_create_inspection_finding.sql
- 148_create_inspection_ncr_link.sql
- 149_create_inspection_response_numeric.sql
- 150_create_inspection_response_attribute.sql
- 151_create_inspection_response_text.sql
- 152_create_inspection_response_datetime.sql
- 153_create_inspection_response_selection.sql
- 154_create_inspection_response_attachment.sql
- 155_add_rls_predicates_inspection.sql
- 156_seed_lookup_inspection.sql
- 157_seed_document_types_inspection.sql
- 158_seed_status_codes_inspection.sql
- 159_workflow_allow_entity_types_inspection.sql
- 160_seed_workflow_inspection.sql
