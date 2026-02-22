# API Implementation Notes

This folder is informational-only. The design package does not include full C# source files by default.

Use:
- `docs/03_api_endpoint_design.md` for endpoint contracts (method/path/DTOs/SP mapping).
- `docs/02_stored_procedure_contracts.md` for the stored procedure signatures those endpoints call.

Implementation must follow existing patterns:
- Minimal APIs grouped by resource
- Dapper `CommandType.StoredProcedure`
- `DbConnectionFactory.CreateForUserAsync(...)` which calls `dbo.usp_SetSessionContext`
- SQL business errors mapped via `SqlErrorMapper`
