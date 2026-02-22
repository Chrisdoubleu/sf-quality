# External Integrations

> **Architecture Note (2026-02):** Some sections reference Power Automate as a notification consumer. The consumption mechanism is now TBD. The frontend is Next.js 15 + ASP.NET Core 9 API, not Power Apps.

**Analysis Date:** 2026-02-22

## APIs & External Services

**Cloud Platform:**
- Azure - Database hosting, authentication, resource management
  - SDK/Client: Azure CLI (`az` commands)
  - Auth: Entra ID (Azure AD) authentication tokens

**No external API integrations:**
- This is a database-only project
- Application layer integration deferred to consuming applications
- Stored procedure layer serves as the API surface for external systems

## Data Storage

**Databases:**
- Azure SQL Database (primary)
  - Connection: Entra ID token-based authentication
  - Client: Microsoft.Data.SqlClient (preferred) or System.Data.SqlClient (fallback)
  - Servers:
    - Dev: `sql-sf-quality-0b1f-dev.database.windows.net` → `sqldb-quality-core-dev`
    - Staging: `sql-sf-quality-0b1f-staging.database.windows.net` → `sqldb-quality-core-staging`
    - Prod: `sql-sf-quality-0b1f-dev.database.windows.net` → `sqldb-quality-core-prod` (same server as dev)

**File Storage:**
- Local filesystem only
  - Migration SQL files: `database/migrations/*.sql` (133 files)
  - Deploy scripts: `database/deploy/*.ps1`
  - Verification/smoke tests: `database/deploy/Verify-*.sql`, `database/deploy/Smoke-*.sql`

**Caching:**
- None (database-level only)

## Authentication & Identity

**Auth Provider:**
- Azure Entra ID (Azure Active Directory)
  - Implementation: Token-based authentication for database connections
  - Token acquisition: `az account get-access-token --resource https://database.windows.net/`
  - User context: `chris.walsh@selectfinishing.ca`
  - Database-level: `SESSION_CONTEXT` with `CallerAzureOid` for row-level security

## Monitoring & Observability

**Error Tracking:**
- None (no external error tracking service)
- Errors surfaced via PowerShell script output and GitHub Actions logs

**Logs:**
- PowerShell script output (console logging with color-coded status)
- SQL Server query execution errors bubbled to PowerShell
- Audit trail: `audit.AuditLog` table tracks all data mutations
- Temporal history: System-versioned tables with 7-year retention in `audit.*History` tables

## CI/CD & Deployment

**Hosting:**
- Azure SQL Database (Serverless)
  - Resource Group: `rg-selectfinishing-apqp`
  - Subscription: `0b1ff71a-737c-4463-82d3-dc50d92dd8d0` (Select Finishing APQP)

**CI Pipeline:**
- GitHub Actions
  - Static validation job: Runs `Test-EnforcementRegistry.ps1` and `Test-SqlStaticRules.ps1`
  - Deploy job: Executes `Apply-Phase07-Plan01.ps1` (or current phase) to dev database
  - Verify/smoke job: Runs verification and smoke tests post-deployment
  - Authentication: Azure OIDC login with federated credentials
  - Secrets: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`

## Environment Configuration

**Required env vars:**
- None (configuration via `database/deploy/deploy-config.json` and Azure CLI context)

**Secrets location:**
- GitHub repository secrets (for CI/CD)
  - `AZURE_CLIENT_ID`
  - `AZURE_TENANT_ID`
  - `AZURE_SUBSCRIPTION_ID`
- Local: Azure CLI cached credentials (`az login` session)

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None (yet)
  - Note: Phase 16 planned to add notification outbox for Power Automate integration
  - Design: Database-driven outbox pattern (tables created, no external dispatch yet)

## Integration Surfaces in Current Program

**Primary active surfaces:**
- `sf-quality-api` as thin proc/view gateway over DB contract artifacts
- `sf-quality-app` consuming API OpenAPI contract snapshots
- Contract chain publication via planning artifacts (`db-contract-manifest.json`, API OpenAPI publish/snapshot files)

**Additional future integration points (deferred):**
- ERP systems via `quality.NcrExternalReference`
- MES systems via topology entities
- Customer portals via external reference tracking

---

*Integration audit: 2026-02-22*
