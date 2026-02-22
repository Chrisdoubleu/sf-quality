# Coding Conventions

**Analysis Date:** 2026-02-22

## Naming Patterns

**Migration Files:**
- Pattern: `{NNN}{suffix?}_{descriptive_name}.sql` where NNN is a 3-digit zero-padded number
- Optional single-letter suffix for forward-fix patches (e.g., `086a_fix_audit_trigger_rowversion.sql`)
- Suffix ordering: empty < 'a' < 'b' for tuple-based migration ordering
- Example: `070_fix_statuscode_column_references.sql`

**PowerShell Deploy Scripts:**
- Pattern: `Apply-Phase{NN}-Plan{NN}.ps1` for phase deployment scripts
- Pattern: `Deploy-Phase{NN}-Plan{NN}.ps1` for newer phase deployment scripts
- Pattern: `Test-{Feature}.ps1` for validation scripts
- Pattern: `Verify-Phase{NN}.sql` for verification queries
- Pattern: `Smoke-Phase{NN}.sql` for smoke tests
- Example: `c:\Users\chris\OneDrive - Select Finishing\Quality System Database\sf-quality-db\database\deploy\Apply-Phase07-Plan01.ps1`

**Stored Procedures:**
- Prefix by schema: `quality.usp_`, `workflow.usp_`, `rca.usp_`, `dbo.usp_`
- CRUD pattern: `usp_Create{Entity}`, `usp_Update{Entity}`, `usp_Delete{Entity}`
- Utility pattern: `usp_{VerbNoun}` (e.g., `usp_SetSessionContext`, `usp_GenerateDocumentNumber`)
- Example: `quality.usp_CreateNCR`, `workflow.usp_TransitionState`

**Database Objects:**
- Tables: PascalCase singular (e.g., `Plant`, `NonConformanceReport`)
- Columns: PascalCase (e.g., `PlantId`, `StatusCode`, `StatusName`)
- Schemas: lowercase (e.g., `quality`, `rca`, `workflow`, `audit`, `security`)
- History tables: `{TableName}History` in `audit` schema (e.g., `audit.PlantHistory`)
- Views: `vw_{DescriptiveName}` (e.g., `quality.vw_EffectivenessResults`)

**PowerShell Variables:**
- PascalCase for parameters and major variables: `$Environment`, `$MigrationsDir`, `$Connection`
- camelCase for local/temporary: `$configPath`, `$adapterTypeName`

## Code Style

**SQL Formatting:**
- UPPERCASE for SQL keywords: `CREATE OR ALTER PROCEDURE`, `SELECT`, `FROM`, `WHERE`, `BEGIN TRANSACTION`
- Table/column references preserve database case (PascalCase)
- N-prefix for all NVARCHAR literals: `N'NCR-DRAFT'`, `N'Description is required.'`
- Indentation: 4 spaces per level in stored procedures
- Column alignment in CREATE TABLE: align data types and constraints vertically

**PowerShell Formatting:**
- 4-space indentation
- K&R brace style (opening brace on same line)
- Parameter blocks use indented attribute notation
- Line continuation via natural PowerShell syntax (piping, parameter blocks)

**SQL Comments:**
- Multi-line header blocks use `/* ... */` format
- Migration files have structured headers with phase/plan/task, description, dependencies
- Single-line comments use `--` prefix
- Example header pattern:
  ```sql
  /*
      070_fix_statuscode_column_references.sql
      Phase 7, Plan 01 - Workstream 1

      Hotfix migration for StatusCode column-name mismatches.

      Fix pattern:
          - Code -> StatusCode
          - Name -> StatusName
  */
  ```

**PowerShell Comments:**
- Comment-based help blocks at script top: `.SYNOPSIS`, `.DESCRIPTION`, `.PARAMETER`
- Inline comments use `#` prefix
- Section dividers use repeated `#` or `-` characters

## Import Organization

**PowerShell Module Loading:**
- Dot-sourcing pattern: `. "$PSScriptRoot\Deploy-Common.ps1"`
- Assembly loading: `Add-Type -AssemblyName` for .NET types
- Fallback pattern: Try Microsoft.Data.SqlClient first, fallback to System.Data.SqlClient
- Location: `c:\Users\chris\OneDrive - Select Finishing\Quality System Database\sf-quality-db\database\deploy\Deploy-Common.ps1`

**SQL Dependencies:**
- Documented in migration file header comment block
- Migration ordering enforced by numeric prefix
- Forward-fix pattern for immutable migration corrections (e.g., `086a` fixes utility SP without editing `056`)

## Error Handling

**SQL Error Conventions:**
- Error numbers by category:
  - `50400` = Input validation failure
  - `50401` = Authentication failure
  - `50404` = Resource not found
  - `50700` = Test/smoke failure
  - `51000+` = Domain-specific validation (e.g., `51001` defect taxonomy validation)
- THROW syntax: `THROW {error_number}, N'{message}', 1;`
- Message parameter MUST be literal or variable, NOT concatenated expression
- Pre-compute dynamic messages: `DECLARE @msg NVARCHAR(200) = ...; THROW 50800, @msg, 1;`
- Location: `c:\Users\chris\OneDrive - Select Finishing\Quality System Database\sf-quality-db\database\migrations\058_crud_ncr_capa.sql`

**Stored Procedure Error Pattern:**
```sql
SET XACT_ABORT, NOCOUNT ON;
BEGIN TRY
    -- Step 1: Establish identity context
    EXEC dbo.usp_SetSessionContext @CallerAzureOid = @CallerAzureOid;

    -- Step 2: Input validation
    IF @RequiredParam IS NULL
        THROW 50400, N'RequiredParam is required.', 1;

    -- Step 3: Business logic
    BEGIN TRANSACTION;
    -- ... transactional work ...
    COMMIT TRANSACTION;

END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
    ;THROW
END CATCH
```

**PowerShell Error Handling:**
- `$ErrorActionPreference = "Stop"` at script top
- Try-catch blocks for cleanup operations
- `throw` with descriptive messages
- Transaction rollback in catch: `IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;`
- Location: `c:\Users\chris\OneDrive - Select Finishing\Quality System Database\sf-quality-db\database\deploy\Apply-Phase07-Plan01.ps1`

## Logging

**SQL Logging:**
- PRINT statements for smoke test progress: `PRINT N'SP-001: quality.usp_CreateNCR';`
- Result sets with `Result` column for verification: `SELECT 'PASS' AS Result` or `SELECT 'FAIL' AS Result`
- Location: `c:\Users\chris\OneDrive - Select Finishing\Quality System Database\sf-quality-db\database\deploy\Smoke-Phase07.sql`

**PowerShell Logging:**
- `Write-Host` with color coding:
  - Green for success: `Write-Host "Token acquired." -ForegroundColor Green`
  - Yellow for warnings: `Write-Host "WARNING: Using System.Data.SqlClient" -ForegroundColor Yellow`
  - Cyan for headers: `Write-Host "Apply Phase 07, Plan 01" -ForegroundColor Cyan`
  - Gray for metadata: `Write-Host "Environment: $Environment" -ForegroundColor Gray`
- Banner pattern with `========` dividers
- Location: `c:\Users\chris\OneDrive - Select Finishing\Quality System Database\sf-quality-db\database\deploy\Deploy-Common.ps1`

## Comments

**When to Comment:**
- Every migration file: header block with phase, plan, purpose, dependencies
- Every stored procedure: header comment with purpose and parameter description
- Multi-step procedures: step markers (e.g., `-- Step 1: Establish identity context`)
- Complex business logic: inline explanation of WHY, not WHAT
- Idempotency guards: explain why guard is needed

**SQL Documentation Pattern:**
- Structured header for migrations and stored procedures
- Inline comments for non-obvious WHERE clauses and validation logic
- Section dividers with repeated `=` or `-` characters

**PowerShell Documentation:**
- Comment-based help for every script
- Parameter descriptions in `.PARAMETER` blocks
- Function documentation with `.SYNOPSIS` and `.DESCRIPTION`

## Function Design

**Stored Procedure Signature:**
- FIRST parameter: `@CallerAzureOid UNIQUEIDENTIFIER` (mandatory for quality/workflow/rca schemas)
- OUTPUT parameters last
- Default values using `= NULL` or `= 0` syntax
- Example: `c:\Users\chris\OneDrive - Select Finishing\Quality System Database\sf-quality-db\database\migrations\058_crud_ncr_capa.sql`

**PowerShell Function Signature:**
- param block with typed parameters
- Common parameters: `[string]$Environment = "dev"`, `[switch]$WhatIf`
- Hashtable returns for config: `return @{ Key1 = Value1; Key2 = Value2 }`

**Procedure Structure:**
- SET options: `SET XACT_ABORT, NOCOUNT ON;` as first statement
- TRY/CATCH wrapper for all procedures
- Transaction pattern: `BEGIN TRANSACTION` ... `COMMIT TRANSACTION`
- Rollback in CATCH: `IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;`
- Re-throw with leading semicolon: `;THROW`

## Module Design

**PowerShell Modules:**
- Shared deployment logic in `Deploy-Common.ps1`
- Functions: `Get-DeployConfig`, `Connect-QualityDb`, `Invoke-Migration`, `Test-Deployment`
- Dot-sourced by deployment scripts
- Location: `c:\Users\chris\OneDrive - Select Finishing\Quality System Database\sf-quality-db\database\deploy\Deploy-Common.ps1`

**SQL Schema Organization:**
- `dbo`: Infrastructure tier (Plant, AppUser, Lookup, StatusCode)
- `quality`: Domain tier (NCR, CAPA, Complaint, etc.)
- `rca`: Root cause analysis (EightDReport, RootCause, Effectiveness)
- `workflow`: State machines (StatusHistory, WorkflowTransition, ActionItem)
- `audit`: System tier (AuditLog, temporal history tables)
- `security`: RLS predicates and security policies
- Location: `c:\Users\chris\OneDrive - Select Finishing\Quality System Database\sf-quality-db\database\migrations\001_schemas.sql`

**Idempotency Pattern:**
- Tables: `IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = N'TableName' AND schema_id = SCHEMA_ID(N'schema'))`
- Procedures: `CREATE OR ALTER PROCEDURE`
- Schemas: `IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = N'schema') EXEC(N'CREATE SCHEMA schema');`
- Constraints: Check before DROP, use OR REPLACE when available

## Special Patterns

**Migration Immutability:**
- Migrations 001-086 are immutable - never edit after deployment
- Use forward-fix pattern (e.g., `086a_`) to patch errors
- Preserves audit trail and deployment reproducibility
- Location: See MEMORY.md deployment pattern "Migration immutability enforcement"

**Batch Splitting:**
- GO delimiter splits batches (case-insensitive, must be on own line)
- Regex pattern: `(?im)^[\t ]*GO[\t ]*(?:--.*)?\r?$`
- Cast to string after split: `| ForEach-Object { [string]$_ }`
- Location: `c:\Users\chris\OneDrive - Select Finishing\Quality System Database\sf-quality-db\database\deploy\Deploy-Common.ps1` line 42

**Temporal Versioning:**
- Pattern: Create history table FIRST with clustered columnstore
- Current table uses HIDDEN period columns: `ValidFrom`, `ValidTo`
- Retention: `HISTORY_RETENTION_PERIOD = 7 YEARS`
- Location: `c:\Users\chris\OneDrive - Select Finishing\Quality System Database\sf-quality-db\database\migrations\002_plant_table.sql`

**RLS Policy Management:**
- Save existing predicates before DROP
- Rebuild from saved state after schema changes
- Delete new table predicates from temp table before cursor loop to avoid duplication on re-runs
- Location: See MEMORY.md "RLS policy rebuild idempotency"

**Column Name Consistency:**
- `dbo.StatusCode` uses `StatusCode` and `StatusName` (NOT `Code`/`Name`)
- `dbo.LayerType` uses `LayerTypeCode` (NOT `LayerCode`)
- Pattern: `{TableName}Code` for code columns in lookup tables
- Enforced by Test-SqlStaticRules.ps1 for migrations 070+

---

*Convention analysis: 2026-02-22*
