[CmdletBinding()]
param(
    [switch]$SkipDocker,
    [switch]$SkipE2E,
    [switch]$SkipPreCommit,
    [int]$DockerMaxAttempts = 5,
    [int]$DockerRetryInitialDelaySeconds = 5,
    [int]$DockerRetryDelayStepSeconds = 2,
    [string]$AdminToken = ""
)

$ErrorActionPreference = "Continue"
$RepoRoot = $PSScriptRoot
Set-Location $RepoRoot

$RunTimestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$ReportRoot = Join-Path $RepoRoot "full-check-reports"
$ReportDir = Join-Path $ReportRoot $RunTimestamp
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$TranscriptPath = Join-Path $ReportDir "transcript.log"
$SummaryPath = Join-Path $ReportDir "summary.txt"

Start-Transcript -Path $TranscriptPath -Force | Out-Null

$StageResults = New-Object System.Collections.Generic.List[object]
$ScriptStartedAt = Get-Date

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host ("=" * 78) -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Cyan
    Write-Host ("=" * 78) -ForegroundColor Cyan
}

function Add-StageResult {
    param(
        [string]$Stage,
        [string]$Status,
        [string]$Detail = ""
    )
    $StageResults.Add([pscustomobject]@{
        Stage  = $Stage
        Status = $Status
        Detail = $Detail
    }) | Out-Null
    $color = "Green"
    if ($Status -eq "FAIL") { $color = "Red" }
    if ($Status -eq "SKIP") { $color = "Yellow" }
    if ($Status -eq "WARN") { $color = "Yellow" }
    Write-Host ("  [{0}] {1} {2}" -f $Status, $Stage, $Detail) -ForegroundColor $color
}

function Invoke-Native {
    param(
        [Parameter(Mandatory = $true)][string]$Command,
        [string[]]$ArgumentList = @()
    )
    & $Command @ArgumentList | Out-Host
    return $LASTEXITCODE
}

function Invoke-WithRetry {
    param(
        [Parameter(Mandatory = $true)][scriptblock]$ScriptBlock,
        [Parameter(Mandatory = $true)][string]$Description,
        [int]$MaxAttempts = 5,
        [int]$InitialDelaySeconds = 5,
        [int]$DelayStepSeconds = 2
    )
    $attempt = 1
    $delay = $InitialDelaySeconds
    while ($true) {
        Write-Host ("  attempt {0}/{1}: {2}" -f $attempt, $MaxAttempts, $Description)
        $exitCode = & $ScriptBlock
        if ($exitCode -eq 0) {
            return 0
        }
        if ($attempt -ge $MaxAttempts) {
            Write-Host ("  giving up after {0} attempts: {1}" -f $attempt, $Description) -ForegroundColor Red
            return $exitCode
        }
        Write-Host ("  attempt {0} failed (exit {1}), waiting {2}s before retry..." -f $attempt, $exitCode, $delay) -ForegroundColor Yellow
        Start-Sleep -Seconds $delay
        $delay = $delay + $DelayStepSeconds
        $attempt = $attempt + 1
    }
}

function Get-ToolVersionString {
    param(
        [string]$Command,
        [string[]]$ArgumentList,
        [string]$Pattern
    )
    $cmd = Get-Command $Command -ErrorAction SilentlyContinue
    if (-not $cmd) {
        return $null
    }
    try {
        $output = & $Command @ArgumentList 2>$null
    } catch {
        return $null
    }
    $joined = ($output | Out-String)
    $match = [regex]::Match($joined, $Pattern)
    if ($match.Success) {
        return $match.Groups[1].Value
    }
    return $null
}

function Compare-SemVer {
    param([string]$Actual, [string]$Required)
    try {
        $a = [version]$Actual
        $r = [version]$Required
        return $a.CompareTo($r)
    } catch {
        return [string]::Compare($Actual, $Required)
    }
}

function Test-ToolVersion {
    param(
        [string]$Name,
        [string]$Command,
        [string[]]$ArgumentList,
        [string]$Pattern,
        [string]$Required,
        [ValidateSet("min", "exact", "presence")][string]$Mode = "min",
        [bool]$Critical = $true
    )
    $version = Get-ToolVersionString -Command $Command -ArgumentList $ArgumentList -Pattern $Pattern
    if (-not (Get-Command $Command -ErrorAction SilentlyContinue)) {
        $status = if ($Critical) { "FAIL" } else { "WARN" }
        Add-StageResult -Stage $Name -Status $status -Detail "command not found: $Command"
        return -not $Critical
    }
    if ($Mode -eq "presence") {
        Add-StageResult -Stage $Name -Status "OK" -Detail "found ($Command), version=$version"
        return $true
    }
    if (-not $version) {
        $status = if ($Critical) { "FAIL" } else { "WARN" }
        Add-StageResult -Stage $Name -Status $status -Detail "could not parse version from $Command output"
        return -not $Critical
    }
    if ($Mode -eq "exact") {
        if ($version -eq $Required) {
            Add-StageResult -Stage $Name -Status "OK" -Detail "version=$version (exact match required by project)"
            return $true
        } else {
            $status = if ($Critical) { "FAIL" } else { "WARN" }
            Add-StageResult -Stage $Name -Status $status -Detail "version=$version, required EXACT=$Required (pinned in project manifest)"
            return -not $Critical
        }
    }
    $cmp = Compare-SemVer -Actual $version -Required $Required
    if ($cmp -ge 0) {
        Add-StageResult -Stage $Name -Status "OK" -Detail "version=$version (>= $Required)"
        return $true
    } else {
        $status = if ($Critical) { "FAIL" } else { "WARN" }
        Add-StageResult -Stage $Name -Status $status -Detail "version=$version, required >= $Required"
        return -not $Critical
    }
}

function Get-PyProjectExactPin {
    param([string]$PackageName)
    $content = Get-Content (Join-Path $RepoRoot "pyproject.toml") -Raw
    $pattern = "`"$PackageName==([0-9.]+)`""
    $match = [regex]::Match($content, $pattern)
    if ($match.Success) {
        return $match.Groups[1].Value
    }
    return $null
}

function Get-PackageJsonField {
    $json = Get-Content (Join-Path $RepoRoot "package.json") -Raw | ConvertFrom-Json
    return $json
}

function Get-GoModMinVersion {
    $content = Get-Content (Join-Path $RepoRoot "apps\notifier\go.mod") -Raw
    $match = [regex]::Match($content, "(?m)^go (\d+\.\d+(\.\d+)?)")
    if ($match.Success) {
        $v = $match.Groups[1].Value
        if (($v -split "\.").Count -eq 2) { $v = "$v.0" }
        return $v
    }
    return "1.25.0"
}

function Wait-ForHttpHealth {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 90
    )
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                return $true
            }
        } catch {
        }
        Start-Sleep -Seconds 2
    }
    return $false
}

Write-Section "Country Decision Atlas — full local check"
Write-Host "Report folder: $ReportDir"
Write-Host "Started at:    $ScriptStartedAt"

foreach ($staleDir in @(".pytest_cache", ".mypy_cache", ".ruff_cache")) {
    $staleDirPath = Join-Path $RepoRoot $staleDir
    if (Test-Path $staleDirPath) {
        Remove-Item $staleDirPath -Recurse -Force -ErrorAction SilentlyContinue
        if (Test-Path $staleDirPath) {
            Write-Host "WARNING: $staleDir exists and could not be removed (likely locked by another process)." -ForegroundColor Yellow
            Write-Host "         This can make 'pnpm quality' (prettier) or pytest fail with an unrelated-looking error." -ForegroundColor Yellow
            Write-Host "         Close any IDE/antivirus/leftover process holding it open, then re-run this script." -ForegroundColor Yellow
        }
    }
}

Write-Section "Phase 0 — System toolchain verification"

$packageJson = Get-PackageJsonField
$pnpmRequired = ($packageJson.packageManager -split "@")[1]
$playwrightRequired = ($packageJson.devDependencies.'@playwright/test' -replace '[\^~]', '')
$prettierRequired = ($packageJson.devDependencies.prettier -replace '[\^~]', '')
$openapiTsRequired = ($packageJson.devDependencies.'openapi-typescript' -replace '[\^~]', '')
$fastapiRequired = Get-PyProjectExactPin -PackageName "fastapi"
$pydanticRequired = Get-PyProjectExactPin -PackageName "pydantic"
$goRequired = Get-GoModMinVersion

$envOk = $true

$envOk = (Test-ToolVersion -Name "Git" -Command "git" -ArgumentList @("--version") -Pattern "(\d+\.\d+\.\d+)" -Required "2.55.0" -Mode "min" -Critical $true) -and $envOk
$envOk = (Test-ToolVersion -Name "Docker Engine" -Command "docker" -ArgumentList @("--version") -Pattern "(\d+\.\d+\.\d+)" -Required "29.5.3" -Mode "min" -Critical $true) -and $envOk
$envOk = (Test-ToolVersion -Name "Docker Compose" -Command "docker" -ArgumentList @("compose", "version") -Pattern "v?(\d+\.\d+\.\d+)" -Required "5.1.4" -Mode "min" -Critical $true) -and $envOk
$envOk = (Test-ToolVersion -Name "Python 3.12" -Command "py" -ArgumentList @("-3.12", "--version") -Pattern "(\d+\.\d+\.\d+)" -Required "3.12.0" -Mode "min" -Critical $true) -and $envOk
$envOk = (Test-ToolVersion -Name "Node.js" -Command "node" -ArgumentList @("--version") -Pattern "(\d+\.\d+\.\d+)" -Required "22.22.0" -Mode "min" -Critical $true) -and $envOk
$envOk = (Test-ToolVersion -Name "Corepack" -Command "corepack" -ArgumentList @("--version") -Pattern "(\d+\.\d+\.\d+)" -Required "0.34.0" -Mode "min" -Critical $false) -and $envOk
$envOk = (Test-ToolVersion -Name "pnpm" -Command "pnpm" -ArgumentList @("--version") -Pattern "(\d+\.\d+\.\d+)" -Required $pnpmRequired -Mode "min" -Critical $true) -and $envOk
$envOk = (Test-ToolVersion -Name "Go" -Command "go" -ArgumentList @("version") -Pattern "go(\d+\.\d+\.\d+)" -Required $goRequired -Mode "min" -Critical $true) -and $envOk
$envOk = (Test-ToolVersion -Name "protoc" -Command "protoc" -ArgumentList @("--version") -Pattern "(\d+\.\d+)" -Required "" -Mode "presence" -Critical $true) -and $envOk
$envOk = (Test-ToolVersion -Name "protoc-gen-go" -Command "protoc-gen-go" -ArgumentList @("--version") -Pattern "(\d+\.\d+\.\d+)" -Required "" -Mode "presence" -Critical $true) -and $envOk
$envOk = (Test-ToolVersion -Name "protoc-gen-go-grpc" -Command "protoc-gen-go-grpc" -ArgumentList @("--version") -Pattern "(\d+\.\d+\.\d+)" -Required "" -Mode "presence" -Critical $true) -and $envOk

if (-not $envOk) {
    Write-Section "ABORTED — system toolchain check failed"
    Write-Host "One or more critical tools are missing or below the required version." -ForegroundColor Red
    Write-Host "Fix the FAIL entries above and re-run this script." -ForegroundColor Red
    Stop-Transcript | Out-Null
    $StageResults | Format-Table -AutoSize | Out-File -FilePath $SummaryPath -Encoding utf8
    exit 1
}

Write-Section "Phase 1 — Dependency installation"

if ($AdminToken -eq "") {
    $AdminToken = "local-gate-" + ([guid]::NewGuid().ToString("N").Substring(0, 16))
}
$env:ADMIN_TOKEN = $AdminToken
Write-Host "Using ADMIN_TOKEN=$AdminToken for this run (API container and test runner share it)."

$pipInstallExit = Invoke-WithRetry -Description "py -3.12 -m pip install -e .[dev]" -MaxAttempts 3 -InitialDelaySeconds 5 -DelayStepSeconds 5 -ScriptBlock {
    Invoke-Native -Command "py" -ArgumentList @("-3.12", "-m", "pip", "install", "-e", ".[dev]")
}
Add-StageResult -Stage "pip install -e .[dev]" -Status $(if ($pipInstallExit -eq 0) { "OK" } else { "FAIL" })

$pnpmInstallExit = Invoke-WithRetry -Description "pnpm install" -MaxAttempts 3 -InitialDelaySeconds 5 -DelayStepSeconds 5 -ScriptBlock {
    Invoke-Native -Command "pnpm" -ArgumentList @("install")
}
Add-StageResult -Stage "pnpm install" -Status $(if ($pnpmInstallExit -eq 0) { "OK" } else { "FAIL" })

$playwrightInstallExit = Invoke-WithRetry -Description "pnpm exec playwright install chromium" -MaxAttempts 3 -InitialDelaySeconds 5 -DelayStepSeconds 5 -ScriptBlock {
    Invoke-Native -Command "pnpm" -ArgumentList @("exec", "playwright", "install", "chromium")
}
Add-StageResult -Stage "playwright install chromium" -Status $(if ($playwrightInstallExit -eq 0) { "OK" } else { "FAIL" })

Write-Section "Phase 2 — Project-pinned version verification"

Test-ToolVersion -Name "FastAPI (pip)" -Command "py" -ArgumentList @("-3.12", "-c", "import fastapi; print(fastapi.__version__)") -Pattern "(\d+\.\d+\.\d+)" -Required $fastapiRequired -Mode "exact" -Critical $true | Out-Null
Test-ToolVersion -Name "Pydantic (pip)" -Command "py" -ArgumentList @("-3.12", "-c", "import pydantic; print(pydantic.__version__)") -Pattern "(\d+\.\d+\.\d+)" -Required $pydanticRequired -Mode "exact" -Critical $true | Out-Null
Test-ToolVersion -Name "Next.js" -Command "pnpm" -ArgumentList @("--filter", "@country-decision-atlas/web", "exec", "next", "--version") -Pattern "(\d+\.\d+\.\d+)" -Required "15.0.0" -Mode "min" -Critical $false | Out-Null
Test-ToolVersion -Name "Playwright" -Command "pnpm" -ArgumentList @("exec", "playwright", "--version") -Pattern "(\d+\.\d+\.\d+)" -Required $playwrightRequired -Mode "min" -Critical $false | Out-Null
Test-ToolVersion -Name "Prettier" -Command "pnpm" -ArgumentList @("exec", "prettier", "--version") -Pattern "(\d+\.\d+\.\d+)" -Required $prettierRequired -Mode "min" -Critical $false | Out-Null
Test-ToolVersion -Name "openapi-typescript" -Command "pnpm" -ArgumentList @("exec", "openapi-typescript", "--version") -Pattern "(\d+\.\d+\.\d+)" -Required $openapiTsRequired -Mode "min" -Critical $false | Out-Null

Write-Section "Phase 3 — Static quality gate"

function Run-GateStep {
    param([string]$Name, [string]$Command, [string[]]$ArgumentList, [string]$WorkingDirectory = $RepoRoot)
    Push-Location $WorkingDirectory
    try {
        $exitCode = Invoke-Native -Command $Command -ArgumentList $ArgumentList
    } finally {
        Pop-Location
    }
    Add-StageResult -Stage $Name -Status $(if ($exitCode -eq 0) { "OK" } else { "FAIL" })
    return $exitCode
}

Run-GateStep -Name "ruff check" -Command "py" -ArgumentList @("-3.12", "-m", "ruff", "check", "apps", "packages", "scripts", "tests") | Out-Null
Run-GateStep -Name "ruff format --check" -Command "py" -ArgumentList @("-3.12", "-m", "ruff", "format", "--check", "apps", "packages", "scripts", "tests") | Out-Null
Run-GateStep -Name "mypy" -Command "py" -ArgumentList @("-3.12", "-m", "mypy", "apps", "packages", "scripts", "tests") | Out-Null
Run-GateStep -Name "sqlfluff lint" -Command "py" -ArgumentList @("-3.12", "-m", "sqlfluff", "lint", "database", "--dialect", "postgres") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $RepoRoot ".tmp\pytest") | Out-Null
Run-GateStep -Name "pytest" -Command "py" -ArgumentList @("-3.12", "-m", "pytest", "-p", "no:cacheprovider", "--basetemp=.tmp/pytest") | Out-Null
Run-GateStep -Name "pnpm contracts:generate" -Command "pnpm" -ArgumentList @("contracts:generate") | Out-Null
Run-GateStep -Name "pnpm quality" -Command "pnpm" -ArgumentList @("quality") | Out-Null

Write-Section "Phase 4 — Go notifier gate"

$notifierDir = Join-Path $RepoRoot "apps\notifier"
$protocExit = Run-GateStep -Name "protoc generate" -Command "protoc" -WorkingDirectory $notifierDir -ArgumentList @(
    "-I", ".",
    "--go_out=.", "--go_opt=module=github.com/country-decision-atlas/notifier",
    "--go-grpc_out=.", "--go-grpc_opt=module=github.com/country-decision-atlas/notifier",
    "proto/subscriptions.proto"
)
Run-GateStep -Name "go vet" -Command "go" -WorkingDirectory $notifierDir -ArgumentList @("vet", "./...") | Out-Null
Run-GateStep -Name "go test" -Command "go" -WorkingDirectory $notifierDir -ArgumentList @("test", "./...") | Out-Null

if (-not $SkipDocker) {
    Write-Section "Phase 5 — Docker stack, migrations, runtime smoke"

    $dockerInfoExit = Invoke-Native -Command "docker" -ArgumentList @("info")
    if ($dockerInfoExit -ne 0) {
        Add-StageResult -Stage "docker daemon reachable" -Status "SKIP" -Detail "Docker Desktop is not running; skipping all Docker-dependent steps"
    } else {
        Add-StageResult -Stage "docker daemon reachable" -Status "OK"

        $dockerUpExit = Invoke-WithRetry -Description "docker compose up --build -d api" -MaxAttempts $DockerMaxAttempts -InitialDelaySeconds $DockerRetryInitialDelaySeconds -DelayStepSeconds $DockerRetryDelayStepSeconds -ScriptBlock {
            Invoke-Native -Command "docker" -ArgumentList @("compose", "up", "--build", "-d", "api")
        }
        Add-StageResult -Stage "docker compose up --build -d api" -Status $(if ($dockerUpExit -eq 0) { "OK" } else { "FAIL" })

        if ($dockerUpExit -eq 0) {
            $apiHealthy = Wait-ForHttpHealth -Url "http://localhost:8000/health" -TimeoutSeconds 90
            Add-StageResult -Stage "API health endpoint reachable" -Status $(if ($apiHealthy) { "OK" } else { "FAIL" })

            if ($apiHealthy) {
                $mig1 = Invoke-Native -Command "docker" -ArgumentList @("compose", "exec", "-T", "api", "python", "scripts/apply_migrations.py")
                Add-StageResult -Stage "apply_migrations.py (first run)" -Status $(if ($mig1 -eq 0) { "OK" } else { "FAIL" })

                $mig2 = Invoke-Native -Command "docker" -ArgumentList @("compose", "exec", "-T", "api", "python", "scripts/apply_migrations.py")
                Add-StageResult -Stage "apply_migrations.py (idempotency rerun)" -Status $(if ($mig2 -eq 0) { "OK" } else { "FAIL" })

                $bootstrapExit = Invoke-Native -Command "docker" -ArgumentList @("compose", "exec", "-T", "api", "python", "scripts/bootstrap_runtime_read_models.py")
                Add-StageResult -Stage "bootstrap_runtime_read_models.py" -Status $(if ($bootstrapExit -eq 0) { "OK" } else { "FAIL" })

                $smokeUrls = @(
                    "http://localhost:8000/health",
                    "http://localhost:8000/ready",
                    "http://localhost:8000/api/v1/countries?locale=ru",
                    "http://localhost:8000/api/v1/countries/russia/trust?locale=ru",
                    "http://localhost:8000/api/v1/countries/uruguay/trust?locale=ru",
                    "http://localhost:8000/api/v1/countries/argentina/trust?locale=ru"
                )
                foreach ($url in $smokeUrls) {
                    try {
                        $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 10
                        Add-StageResult -Stage "smoke: $url" -Status $(if ($resp.StatusCode -eq 200) { "OK" } else { "FAIL" }) -Detail "HTTP $($resp.StatusCode)"
                    } catch {
                        Add-StageResult -Stage "smoke: $url" -Status "FAIL" -Detail $_.Exception.Message
                    }
                }

                if (-not $SkipE2E) {
                    Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
                    Run-GateStep -Name "pnpm web:mvp:check (Playwright E2E)" -Command "pnpm" -ArgumentList @("web:mvp:check") | Out-Null
                } else {
                    Add-StageResult -Stage "pnpm web:mvp:check (Playwright E2E)" -Status "SKIP" -Detail "-SkipE2E was set"
                }
            } else {
                Add-StageResult -Stage "migrations / bootstrap / smoke / E2E" -Status "SKIP" -Detail "API never became healthy"
            }
        } else {
            Add-StageResult -Stage "migrations / bootstrap / smoke / E2E" -Status "SKIP" -Detail "docker compose up failed after $DockerMaxAttempts attempts"
        }
    }
} else {
    Add-StageResult -Stage "Docker stack / migrations / runtime smoke / E2E" -Status "SKIP" -Detail "-SkipDocker was set"
}

if (-not $SkipPreCommit) {
    Write-Section "Phase 6 — pre-commit"
    Run-GateStep -Name "pre-commit run --all-files" -Command "py" -ArgumentList @("-3.12", "-m", "pre_commit", "run", "--all-files") | Out-Null
} else {
    Add-StageResult -Stage "pre-commit run --all-files" -Status "SKIP" -Detail "-SkipPreCommit was set"
}

Write-Section "Phase 7 — git status"
Invoke-Native -Command "git" -ArgumentList @("diff", "--check") | Out-Null
Invoke-Native -Command "git" -ArgumentList @("status", "--short") | Out-Null

$ScriptFinishedAt = Get-Date
$durationMinutes = [math]::Round(($ScriptFinishedAt - $ScriptStartedAt).TotalMinutes, 1)

Write-Section "Summary"
$StageResults | Format-Table -AutoSize

$failCount = @($StageResults | Where-Object { $_.Status -eq "FAIL" }).Count
$skipCount = @($StageResults | Where-Object { $_.Status -eq "SKIP" }).Count
$okCount = @($StageResults | Where-Object { $_.Status -eq "OK" }).Count

Write-Host ""
Write-Host ("OK: {0}   FAIL: {1}   SKIP: {2}   Duration: {3} min" -f $okCount, $failCount, $skipCount, $durationMinutes)

$summaryLines = New-Object System.Collections.Generic.List[string]
$summaryLines.Add("Country Decision Atlas — full-check.ps1 run")
$summaryLines.Add("Started:  $ScriptStartedAt")
$summaryLines.Add("Finished: $ScriptFinishedAt")
$summaryLines.Add("Duration: $durationMinutes minutes")
$summaryLines.Add("OK=$okCount FAIL=$failCount SKIP=$skipCount")
$summaryLines.Add("")
foreach ($r in $StageResults) {
    $summaryLines.Add(("[{0}] {1} {2}" -f $r.Status, $r.Stage, $r.Detail))
}
$summaryLines | Out-File -FilePath $SummaryPath -Encoding utf8

Write-Host ""
Write-Host "Full transcript: $TranscriptPath"
Write-Host "Summary:         $SummaryPath"

Stop-Transcript | Out-Null

if ($failCount -gt 0) {
    exit 1
} else {
    exit 0
}
