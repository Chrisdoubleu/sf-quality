<#
.SYNOPSIS
Outcome-gated slice finalization helper for sf-quality repos.

.DESCRIPTION
Detects the current repository (or an explicit RepoRoot), runs repo-specific
verification checks, stages/commits changes, pushes the branch, and optionally
creates a pull request. Commit/push/PR only execute after checks pass.

.PARAMETER RepoRoot
Path inside the target git repository. Defaults to current directory.

.PARAMETER ExpectedRepo
Optional safety gate. If set, detected repo name must match.

.PARAMETER ConfigPath
Path to JSON config describing repo-specific checks.

.PARAMETER Phase
Optional phase label used in default messages.

.PARAMETER Slice
Optional slice label used in default messages.

.PARAMETER BaseBranch
Target base branch for pull requests. Defaults from config.

.PARAMETER CommitTitle
Commit title. Required unless ValidateOnly is set.

.PARAMETER CommitBody
Optional second commit message paragraph.

.PARAMETER PrTitle
PR title. Defaults to CommitTitle.

.PARAMETER PrBody
PR body. Optional.

.PARAMETER Paths
Optional specific paths to stage. If omitted, stages all changes.

.PARAMETER RequiredPathPattern
Optional regex patterns that must match staged paths.

.PARAMETER SkipChecks
Skips configured verification commands.

.PARAMETER NoPush
Skips push.

.PARAMETER CreatePr
Creates a PR using GitHub CLI after push.

.PARAMETER ValidateOnly
Runs repo detection and checks only. Does not stage/commit/push/create PR.

.PARAMETER ForceProtectedBranch
Allows finalize actions on protected branches from config.
#>
[CmdletBinding()]
param(
    [Parameter()]
    [string]$RepoRoot = (Get-Location).Path,

    [Parameter()]
    [string]$ExpectedRepo,

    [Parameter()]
    [string]$ConfigPath = (Join-Path $PSScriptRoot 'slice-finalize.config.json'),

    [Parameter()]
    [string]$Phase,

    [Parameter()]
    [string]$Slice,

    [Parameter()]
    [string]$BaseBranch,

    [Parameter()]
    [string]$CommitTitle,

    [Parameter()]
    [string]$CommitBody,

    [Parameter()]
    [string]$PrTitle,

    [Parameter()]
    [string]$PrBody,

    [Parameter()]
    [string[]]$Paths,

    [Parameter()]
    [string[]]$RequiredPathPattern,

    [Parameter()]
    [switch]$SkipChecks,

    [Parameter()]
    [switch]$NoPush,

    [Parameter()]
    [switch]$CreatePr,

    [Parameter()]
    [switch]$ValidateOnly,

    [Parameter()]
    [switch]$ForceProtectedBranch
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-GitOutput {
    param(
        [string]$WorkingDirectory,
        [string[]]$Arguments,
        [switch]$AllowFailure
    )

    $output = & git -C $WorkingDirectory @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    if (-not $AllowFailure -and $exitCode -ne 0) {
        throw "Git command failed: git -C $WorkingDirectory $($Arguments -join ' ')`n$output"
    }

    if ($null -eq $output) { return @() }
    $lines = @(
        $output |
            ForEach-Object { [string]$_ } |
            Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
    )
    return ,$lines
}

function Expand-Template {
    param(
        [string]$Text,
        [hashtable]$Tokens
    )

    $expanded = $Text
    foreach ($key in $Tokens.Keys) {
        $expanded = $expanded.Replace("{$key}", [string]$Tokens[$key])
    }
    return $expanded
}

function Invoke-CheckCommand {
    param(
        [string]$WorkingDirectory,
        [string]$CommandText
    )

    Write-Host ("[check] {0}" -f $CommandText) -ForegroundColor Cyan
    Push-Location $WorkingDirectory
    try {
        Invoke-Expression $CommandText
    } finally {
        Pop-Location
    }
}

if (-not (Test-Path -Path $ConfigPath)) {
    throw "Missing config file: $ConfigPath"
}

$config = Get-Content -Path $ConfigPath -Raw | ConvertFrom-Json -AsHashtable

$resolvedInputRoot = (Resolve-Path -Path $RepoRoot).Path
$detectedRepoRootLines = Get-GitOutput -WorkingDirectory $resolvedInputRoot -Arguments @('rev-parse', '--show-toplevel')
$detectedRepoRoot = ($detectedRepoRootLines | Select-Object -First 1).Trim()
if ([string]::IsNullOrWhiteSpace($detectedRepoRoot)) {
    throw "Unable to detect repository root from '$resolvedInputRoot'."
}

$repoName = Split-Path -Path $detectedRepoRoot -Leaf
$repoConfig = $null
if ($config.ContainsKey('repos') -and $config['repos'].ContainsKey($repoName)) {
    $repoConfig = $config['repos'][$repoName]
}
if ($null -eq $repoConfig) {
    $supported = @()
    if ($config.ContainsKey('repos')) { $supported = @($config['repos'].Keys) }
    throw "Unsupported repo '$repoName'. Supported repos: $($supported -join ', ')"
}

if (-not [string]::IsNullOrWhiteSpace($ExpectedRepo) -and $ExpectedRepo -ne $repoName) {
    throw "Repo mismatch. Expected '$ExpectedRepo', detected '$repoName'."
}

$branchLines = Get-GitOutput -WorkingDirectory $detectedRepoRoot -Arguments @('rev-parse', '--abbrev-ref', 'HEAD')
$currentBranch = ($branchLines | Select-Object -First 1).Trim()
if ([string]::IsNullOrWhiteSpace($currentBranch) -or $currentBranch -eq 'HEAD') {
    throw "Detached HEAD is not supported for finalize workflow."
}

$protectedBranches = New-Object 'System.Collections.Generic.HashSet[string]'
if ($config.ContainsKey('defaults') -and $config['defaults'].ContainsKey('protectedBranches')) {
    foreach ($b in $config['defaults']['protectedBranches']) { [void]$protectedBranches.Add([string]$b) }
}
if ($repoConfig.ContainsKey('protectedBranches')) {
    foreach ($b in $repoConfig['protectedBranches']) { [void]$protectedBranches.Add([string]$b) }
}

$resolvedBaseBranch = $BaseBranch
if ([string]::IsNullOrWhiteSpace($resolvedBaseBranch)) {
    if ($repoConfig.ContainsKey('baseBranch') -and -not [string]::IsNullOrWhiteSpace([string]$repoConfig['baseBranch'])) {
        $resolvedBaseBranch = [string]$repoConfig['baseBranch']
    } elseif ($config.ContainsKey('defaults') -and $config['defaults'].ContainsKey('baseBranch')) {
        $resolvedBaseBranch = [string]$config['defaults']['baseBranch']
    } else {
        $resolvedBaseBranch = 'main'
    }
}

if (-not $ValidateOnly -and -not $ForceProtectedBranch -and $protectedBranches.Contains($currentBranch)) {
    throw "Refusing to finalize on protected branch '$currentBranch'."
}

Write-Host ("Detected repo: {0}" -f $repoName) -ForegroundColor Green
Write-Host ("Repo root: {0}" -f $detectedRepoRoot) -ForegroundColor Gray
Write-Host ("Current branch: {0}" -f $currentBranch) -ForegroundColor Gray
Write-Host ("Target base branch: {0}" -f $resolvedBaseBranch) -ForegroundColor Gray

$tokenMap = @{
    repoRoot = $detectedRepoRoot
    repoName = $repoName
    branch = $currentBranch
    baseBranch = $resolvedBaseBranch
    phase = $Phase
    slice = $Slice
}

if (-not $SkipChecks -and $repoConfig.ContainsKey('checks')) {
    foreach ($checkTemplate in $repoConfig['checks']) {
        $commandText = Expand-Template -Text ([string]$checkTemplate) -Tokens $tokenMap
        Invoke-CheckCommand -WorkingDirectory $detectedRepoRoot -CommandText $commandText
    }
}

if ($ValidateOnly) {
    Write-Host 'ValidateOnly complete. No git write actions performed.' -ForegroundColor Green
    return
}

$statusLines = Get-GitOutput -WorkingDirectory $detectedRepoRoot -Arguments @('status', '--porcelain')
if ($statusLines.Count -eq 0) {
    throw "No working tree changes detected."
}

if ($Paths -and $Paths.Count -gt 0) {
    $addArgs = @('add', '--')
    $addArgs += $Paths
    [void](Get-GitOutput -WorkingDirectory $detectedRepoRoot -Arguments $addArgs)
} else {
    [void](Get-GitOutput -WorkingDirectory $detectedRepoRoot -Arguments @('add', '-A'))
}

$stagedFiles = Get-GitOutput -WorkingDirectory $detectedRepoRoot -Arguments @('diff', '--cached', '--name-only')
if ($stagedFiles.Count -eq 0) {
    throw "No staged files detected after git add."
}

$patterns = @()
if ($RequiredPathPattern -and $RequiredPathPattern.Count -gt 0) {
    $patterns += $RequiredPathPattern
} elseif ($repoConfig.ContainsKey('requiredPathPatterns')) {
    foreach ($p in $repoConfig['requiredPathPatterns']) {
        if (-not [string]::IsNullOrWhiteSpace([string]$p)) { $patterns += [string]$p }
    }
}

$patternMode = 'all'
if ($repoConfig.ContainsKey('requiredPathPatternMode') -and -not [string]::IsNullOrWhiteSpace([string]$repoConfig['requiredPathPatternMode'])) {
    $patternMode = ([string]$repoConfig['requiredPathPatternMode']).ToLowerInvariant()
}

if ($patterns.Count -gt 0) {
    if ($patternMode -eq 'any') {
        $matchedAny = $false
        foreach ($pattern in $patterns) {
            if ($stagedFiles | Where-Object { $_ -match $pattern }) {
                $matchedAny = $true
                break
            }
        }
        if (-not $matchedAny) {
            throw "No staged files matched required path patterns (mode=any)."
        }
    } else {
        foreach ($pattern in $patterns) {
            if (-not ($stagedFiles | Where-Object { $_ -match $pattern })) {
                throw "No staged files matched required path pattern: $pattern"
            }
        }
    }
}

$resolvedCommitTitle = $CommitTitle
if ([string]::IsNullOrWhiteSpace($resolvedCommitTitle)) {
    if (-not [string]::IsNullOrWhiteSpace($Phase) -and -not [string]::IsNullOrWhiteSpace($Slice)) {
        $resolvedCommitTitle = "chore(phase$Phase): finalize slice $Slice"
    } elseif (-not [string]::IsNullOrWhiteSpace($Phase)) {
        $resolvedCommitTitle = "chore(phase$Phase): finalize"
    } else {
        $resolvedCommitTitle = "chore: finalize slice"
    }
}

$commitArgs = @('commit', '-m', $resolvedCommitTitle)
if (-not [string]::IsNullOrWhiteSpace($CommitBody)) {
    $commitArgs += @('-m', $CommitBody)
}
[void](Get-GitOutput -WorkingDirectory $detectedRepoRoot -Arguments $commitArgs)

if (-not $NoPush) {
    [void](Get-GitOutput -WorkingDirectory $detectedRepoRoot -Arguments @('push', '-u', 'origin', $currentBranch))
}

$prUrl = $null
if ($CreatePr) {
    if ($NoPush) {
        throw "Cannot create PR when -NoPush is set."
    }

    $null = Get-Command gh -ErrorAction Stop

    $resolvedPrTitle = $PrTitle
    if ([string]::IsNullOrWhiteSpace($resolvedPrTitle)) {
        $resolvedPrTitle = $resolvedCommitTitle
    }

    $resolvedPrBody = $PrBody
    if ([string]::IsNullOrWhiteSpace($resolvedPrBody)) {
        $resolvedPrBody = "Automated finalize for $repoName branch '$currentBranch'."
    }

    Push-Location $detectedRepoRoot
    try {
        $prOutput = & gh pr create --base $resolvedBaseBranch --head $currentBranch --title $resolvedPrTitle --body $resolvedPrBody 2>&1
        $exitCode = $LASTEXITCODE
        if ($exitCode -ne 0) {
            throw "gh pr create failed.`n$prOutput"
        }

        if ($prOutput -is [System.Array]) {
            $prUrl = ($prOutput | Select-Object -Last 1).ToString().Trim()
        } else {
            $prUrl = [string]$prOutput
        }
    } finally {
        Pop-Location
    }
}

Write-Host ''
Write-Host 'Finalize complete.' -ForegroundColor Green
Write-Host ("Repo: {0}" -f $repoName) -ForegroundColor Gray
Write-Host ("Branch: {0}" -f $currentBranch) -ForegroundColor Gray
if ($CreatePr -and -not [string]::IsNullOrWhiteSpace($prUrl)) {
    Write-Host ("PR: {0}" -f $prUrl) -ForegroundColor Gray
}
