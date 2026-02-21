#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Onboarding script for the sf-quality workspace.
.DESCRIPTION
    Clones all child repositories and runs their Git hook installers.
#>

$ErrorActionPreference = 'Stop'

$repos = @(
    'sf-quality-db',
    'sf-quality-api',
    'sf-quality-app'
)

$orgUrl = 'https://github.com/Chrisdoubleu'

foreach ($repo in $repos) {
    if (Test-Path $repo) {
        Write-Host "[$repo] Already exists — skipping clone." -ForegroundColor Yellow
    } else {
        Write-Host "[$repo] Cloning from $orgUrl/$repo.git ..." -ForegroundColor Cyan
        git clone "$orgUrl/$repo.git"
        if ($LASTEXITCODE -ne 0) { throw "Failed to clone $repo" }
        Write-Host "[$repo] Cloned successfully." -ForegroundColor Green
    }

    $hookScript = Join-Path $repo 'scripts/Install-GitHooks.ps1'
    if (Test-Path $hookScript) {
        Write-Host "[$repo] Running Install-GitHooks.ps1 ..." -ForegroundColor Cyan
        Push-Location $repo
        try {
            & pwsh -File $hookScript
            if ($LASTEXITCODE -ne 0) { throw "Git hook install failed for $repo" }
            Write-Host "[$repo] Git hooks installed." -ForegroundColor Green
        } finally {
            Pop-Location
        }
    } else {
        Write-Host "[$repo] No Install-GitHooks.ps1 found — skipping hooks." -ForegroundColor Yellow
    }

    Write-Host ""
}

Write-Host 'Setup complete. Open sf-quality.code-workspace in VS Code to get started.' -ForegroundColor Green
