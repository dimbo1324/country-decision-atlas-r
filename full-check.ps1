[CmdletBinding()]
param(
    [switch]$SkipDocker,
    [switch]$SkipE2E,
    [switch]$SkipPreCommit,
    [switch]$Quiet,
    [int]$DockerMaxAttempts = 5,
    [int]$DockerRetryInitialDelaySeconds = 5,
    [int]$DockerRetryDelayStepSeconds = 2,
    [string]$AdminToken = "",
    [string]$ConfigPath = ""
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
$ReportJsonPath = Join-Path $ReportDir "report.json"
$RecommendationsPath = Join-Path $ReportDir "recommendations.txt"

try {
    Start-Transcript -Path $TranscriptPath -Force | Out-Null
} catch {
    Write-Host "WARNING: could not start transcript ($($_.Exception.Message)); continuing without it." -ForegroundColor Yellow
}

$StageResults = New-Object System.Collections.Generic.List[object]
$Recommendations = New-Object System.Collections.Generic.List[object]
$NetworkResults = New-Object System.Collections.Generic.List[object]
$ScriptStartedAt = Get-Date

function Write-Section {
    param([string]$Title)
    if ($Quiet) {
        Write-Host ">> $Title" -ForegroundColor Cyan
        return
    }
    Write-Host ""
    Write-Host ("=" * 78) -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Cyan
    Write-Host ("=" * 78) -ForegroundColor Cyan
}

function Add-Recommendation {
    param(
        [string]$Tool,
        [string]$Issue,
        [string]$Hint
    )
    $Recommendations.Add([pscustomobject]@{
        Tool  = $Tool
        Issue = $Issue
        Hint  = $Hint
    }) | Out-Null
}

function Add-StageResult {
    param(
        [string]$Stage,
        [string]$Status,
        [string]$Detail = "",
        [double]$DurationSeconds = 0
    )
    $StageResults.Add([pscustomobject]@{
        Stage           = $Stage
        Status          = $Status
        Detail          = $Detail
        DurationSeconds = [math]::Round($DurationSeconds, 1)
    }) | Out-Null
    $color = "Green"
    if ($Status -eq "FAIL") { $color = "Red" }
    if ($Status -eq "SKIP") { $color = "Yellow" }
    if ($Status -eq "WARN") { $color = "Yellow" }
    if ($Quiet -and $Status -eq "OK") {
        return
    }
    $durationText = ""
    if ($DurationSeconds -ge 1) {
        $durationText = " ({0}s)" -f [math]::Round($DurationSeconds, 1)
    }
    Write-Host ("  [{0}] {1} {2}{3}" -f $Status, $Stage, $Detail, $durationText) -ForegroundColor $color
}

function Invoke-Native {
    param(
        [Parameter(Mandatory = $true)][string]$Command,
        [string[]]$ArgumentList = @()
    )
    try {
        & $Command @ArgumentList | Out-Host
        return $LASTEXITCODE
    } catch {
        Write-Host ("  ERROR invoking '{0}': {1}" -f $Command, $_.Exception.Message) -ForegroundColor Red
        return -1
    }
}

function Invoke-NativeTimed {
    param(
        [Parameter(Mandatory = $true)][string]$Command,
        [string[]]$ArgumentList = @()
    )
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $exitCode = Invoke-Native -Command $Command -ArgumentList $ArgumentList
    $sw.Stop()
    return @{ ExitCode = $exitCode; DurationSeconds = $sw.Elapsed.TotalSeconds }
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
        $exitCode = -1
        try {
            $exitCode = & $ScriptBlock
        } catch {
            Write-Host ("  attempt {0} threw an exception: {1}" -f $attempt, $_.Exception.Message) -ForegroundColor Yellow
            $exitCode = -1
        }
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
    try {
        $cmd = Get-Command $Command -ErrorAction SilentlyContinue
        if (-not $cmd) {
            return $null
        }
        $output = & $Command @ArgumentList 2>$null
        $joined = ($output | Out-String)
        $match = [regex]::Match($joined, $Pattern)
        if ($match.Success) {
            return $match.Groups[1].Value
        }
        return $null
    } catch {
        return $null
    }
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
    <#
        Never blocks the script. A missing required tool or a version below the
        recommended baseline is reported (FAIL/WARN) and added to the
        recommendations list, but execution always continues.
    #>
    param(
        [string]$Name,
        [string]$Command,
        [string[]]$ArgumentList,
        [string]$Pattern,
        [string]$Recommended = "",
        [ValidateSet("min", "exact", "presence")][string]$Mode = "min",
        [ValidateSet("required", "optional")][string]$Severity = "required",
        [string]$InstallHint = ""
    )
    try {
        $found = [bool](Get-Command $Command -ErrorAction SilentlyContinue)
    } catch {
        $found = $false
    }
    if (-not $found) {
        $status = if ($Severity -eq "required") { "FAIL" } else { "WARN" }
        Add-StageResult -Stage $Name -Status $status -Detail "command not found: $Command"
        if ($InstallHint) {
            Add-Recommendation -Tool $Name -Issue "not installed" -Hint $InstallHint
        }
        return $false
    }

    $version = Get-ToolVersionString -Command $Command -ArgumentList $ArgumentList -Pattern $Pattern

    if ($Mode -eq "presence") {
        Add-StageResult -Stage $Name -Status "OK" -Detail "found ($Command), version=$version"
        return $true
    }
    if (-not $version) {
        Add-StageResult -Stage $Name -Status "WARN" -Detail "found ($Command) but could not parse a version string; assuming compatible"
        return $true
    }
    if ($Mode -eq "exact") {
        if (-not $Recommended -or $version -eq $Recommended) {
            Add-StageResult -Stage $Name -Status "OK" -Detail "version=$version"
            return $true
        }
        Add-StageResult -Stage $Name -Status "WARN" -Detail "version=$version, project manifest pins $Recommended (informational; pip/pnpm normally enforces this automatically)"
        Add-Recommendation -Tool $Name -Issue "installed version ($version) differs from the manifest pin ($Recommended)" -Hint "Re-run dependency install for this project; if it persists, check for a conflicting global/site-packages install."
        return $true
    }

    $cmp = Compare-SemVer -Actual $version -Required $Recommended
    if (-not $Recommended -or $cmp -ge 0) {
        Add-StageResult -Stage $Name -Status "OK" -Detail "version=$version"
        return $true
    }
    Add-StageResult -Stage $Name -Status "WARN" -Detail "version=$version is older than the verified baseline ($Recommended); likely still compatible"
    if ($InstallHint) {
        Add-Recommendation -Tool $Name -Issue "version $version is older than the recommended baseline $Recommended" -Hint $InstallHint
    }
    return $true
}

function Get-FullCheckConfig {
    param([string]$Path)
    $defaultConfig = [pscustomobject]@{
        tools             = @()
        networkChecks     = @()
        minFreeDiskSpaceGb = 5
    }
    if (-not $Path) {
        $Path = Join-Path $RepoRoot "full-check.config.json"
    }
    if (-not (Test-Path $Path)) {
        Write-Host "WARNING: config file not found at $Path; using built-in defaults (no static tool baselines)." -ForegroundColor Yellow
        return $defaultConfig
    }
    try {
        $raw = Get-Content $Path -Raw -ErrorAction Stop
        $parsed = $raw | ConvertFrom-Json -ErrorAction Stop
        return $parsed
    } catch {
        Write-Host ("WARNING: failed to parse {0}: {1}. Using built-in defaults." -f $Path, $_.Exception.Message) -ForegroundColor Yellow
        return $defaultConfig
    }
}

function Get-PyProjectExactPin {
    param([string]$PackageName)
    try {
        $content = Get-Content (Join-Path $RepoRoot "pyproject.toml") -Raw -ErrorAction Stop
        $pattern = "`"$PackageName==([0-9.]+)`""
        $match = [regex]::Match($content, $pattern)
        if ($match.Success) {
            return $match.Groups[1].Value
        }
    } catch {
    }
    return $null
}

function Get-RequiresPythonMinVersion {
    try {
        $content = Get-Content (Join-Path $RepoRoot "pyproject.toml") -Raw -ErrorAction Stop
        $match = [regex]::Match($content, "requires-python\s*=\s*`"[>=]+([0-9.]+)`"")
        if ($match.Success) {
            $v = $match.Groups[1].Value
            if (($v -split "\.").Count -eq 2) { $v = "$v.0" }
            return $v
        }
    } catch {
    }
    return "3.12.0"
}

function Get-PackageJsonField {
    try {
        $json = Get-Content (Join-Path $RepoRoot "package.json") -Raw -ErrorAction Stop | ConvertFrom-Json -ErrorAction Stop
        return $json
    } catch {
        return $null
    }
}

function Get-GoModMinVersion {
    try {
        $content = Get-Content (Join-Path $RepoRoot "apps\notifier\go.mod") -Raw -ErrorAction Stop
        $match = [regex]::Match($content, "(?m)^go (\d+\.\d+(\.\d+)?)")
        if ($match.Success) {
            $v = $match.Groups[1].Value
            if (($v -split "\.").Count -eq 2) { $v = "$v.0" }
            return $v
        }
    } catch {
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

function Test-PortReachable {
    param([string]$HostName, [int]$Port, [int]$TimeoutMs = 3000)
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $task = $client.ConnectAsync($HostName, $Port)
        $completed = $task.Wait($TimeoutMs)
        $result = $completed -and $client.Connected
        $client.Close()
        return $result
    } catch {
        return $false
    }
}

function Get-SystemDiagnostics {
    $diag = [ordered]@{
        hostname        = "unknown"
        osCaption       = "unknown"
        osArchitecture  = "unknown"
        processorCount  = 0
        totalMemoryGb   = $null
        freeMemoryGb    = $null
        repoDriveFreeGb = $null
        powerShellVersion = $PSVersionTable.PSVersion.ToString()
    }
    try { $diag.hostname = [System.Environment]::MachineName } catch { }
    try { $diag.processorCount = [System.Environment]::ProcessorCount } catch { }
    try {
        $os = Get-CimInstance -ClassName Win32_OperatingSystem -ErrorAction Stop
        $diag.osCaption = $os.Caption
        $diag.osArchitecture = $os.OSArchitecture
        $diag.totalMemoryGb = [math]::Round($os.TotalVisibleMemorySize / 1MB, 1)
        $diag.freeMemoryGb = [math]::Round($os.FreePhysicalMemory / 1MB, 1)
    } catch {
        try { $diag.osCaption = [System.Environment]::OSVersion.VersionString } catch { }
    }
    try {
        $qualifier = (Split-Path $RepoRoot -Qualifier)
        $drive = [System.IO.DriveInfo]::new($qualifier)
        $diag.repoDriveFreeGb = [math]::Round($drive.AvailableFreeSpace / 1GB, 1)
    } catch {
    }
    return [pscustomobject]$diag
}

function Get-GitContext {
    $ctx = [ordered]@{
        branch         = "unknown"
        commit         = "unknown"
        dirtyFileCount = $null
        aheadBehind    = "unknown"
    }
    try {
        $branchOut = git rev-parse --abbrev-ref HEAD 2>$null
        if ($LASTEXITCODE -eq 0) { $ctx.branch = ($branchOut | Out-String).Trim() }
    } catch {
    }
    try {
        $commitOut = git rev-parse --short HEAD 2>$null
        if ($LASTEXITCODE -eq 0) { $ctx.commit = ($commitOut | Out-String).Trim() }
    } catch {
    }
    try {
        $statusOut = git status --porcelain 2>$null
        $ctx.dirtyFileCount = @($statusOut | Where-Object { $_ -ne "" }).Count
    } catch {
    }
    try {
        $aheadBehindOut = git rev-list --left-right --count "origin/$($ctx.branch)...$($ctx.branch)" 2>$null
        if ($LASTEXITCODE -eq 0 -and $aheadBehindOut) {
            $parts = ($aheadBehindOut | Out-String).Trim() -split "\s+"
            if ($parts.Count -eq 2) {
                $ctx.aheadBehind = "behind=$($parts[0]) ahead=$($parts[1])"
            }
        }
    } catch {
    }
    return [pscustomobject]$ctx
}

try {
    Write-Section "Country Decision Atlas — full local check"
    Write-Host "Report folder: $ReportDir"
    Write-Host "Started at:    $ScriptStartedAt"

    Write-Section "Phase -1 — Diagnostics (system, git, network)"

    $systemInfo = Get-SystemDiagnostics
    Write-Host ("  host={0} os={1} ({2}) cpu={3} ram={4}GB free-ram={5}GB free-disk={6}GB ps={7}" -f `
        $systemInfo.hostname, $systemInfo.osCaption, $systemInfo.osArchitecture, $systemInfo.processorCount, `
        $systemInfo.totalMemoryGb, $systemInfo.freeMemoryGb, $systemInfo.repoDriveFreeGb, $systemInfo.powerShellVersion)

    $gitContext = Get-GitContext
    Write-Host ("  git branch={0} commit={1} dirty-files={2} {3}" -f $gitContext.branch, $gitContext.commit, $gitContext.dirtyFileCount, $gitContext.aheadBehind)

    $Config = Get-FullCheckConfig -Path $ConfigPath

    $minFreeDiskGb = 5
    if ($Config.minFreeDiskSpaceGb) { $minFreeDiskGb = $Config.minFreeDiskSpaceGb }
    if ($systemInfo.repoDriveFreeGb -ne $null -and $systemInfo.repoDriveFreeGb -lt $minFreeDiskGb) {
        Add-StageResult -Stage "Disk space" -Status "WARN" -Detail "only $($systemInfo.repoDriveFreeGb) GB free on the repo drive (recommended >= $minFreeDiskGb GB); Docker builds and node_modules installs may fail or behave unpredictably"
        Add-Recommendation -Tool "Disk space" -Issue "low free disk space ($($systemInfo.repoDriveFreeGb) GB)" -Hint "Free up disk space (Docker images/containers: 'docker system prune'; old node_modules; Windows Disk Cleanup) before running Docker-heavy phases."
    } else {
        Add-StageResult -Stage "Disk space" -Status "OK" -Detail "$($systemInfo.repoDriveFreeGb) GB free"
    }

    if ($Config.networkChecks -and @($Config.networkChecks).Count -gt 0) {
        foreach ($net in $Config.networkChecks) {
            $reachable = Test-PortReachable -HostName $net.host -Port $net.port -TimeoutMs 3000
            $NetworkResults.Add([pscustomobject]@{ Name = $net.name; Host = $net.host; Port = $net.port; Reachable = $reachable }) | Out-Null
            if ($reachable) {
                Add-StageResult -Stage "Network: $($net.name)" -Status "OK" -Detail "$($net.host):$($net.port) reachable"
            } else {
                Add-StageResult -Stage "Network: $($net.name)" -Status "WARN" -Detail "$($net.host):$($net.port) not reachable (timeout or blocked)"
                Add-Recommendation -Tool "Network: $($net.name)" -Issue "could not reach $($net.host):$($net.port)" -Hint "Check internet connection, VPN, proxy, or corporate firewall settings. Installs that need this host may fail or need more retries."
            }
        }
    }

    foreach ($staleDir in @(".pytest_cache", ".mypy_cache", ".ruff_cache")) {
        $staleDirPath = Join-Path $RepoRoot $staleDir
        if (Test-Path $staleDirPath) {
            Remove-Item $staleDirPath -Recurse -Force -ErrorAction SilentlyContinue
            if (Test-Path $staleDirPath) {
                Add-StageResult -Stage "Stale cache: $staleDir" -Status "WARN" -Detail "exists and could not be removed (likely locked by another process); may cause unrelated-looking prettier/pytest failures later"
                Add-Recommendation -Tool $staleDir -Issue "directory is locked and could not be cleaned" -Hint "Close any IDE, antivirus scan, or leftover process that may be holding '$staleDir' open, then re-run this script."
            }
        }
    }

    Write-Section "Phase 0 — System toolchain verification"

    $packageJson = Get-PackageJsonField
    $pnpmRequired = $null
    $playwrightRequired = $null
    $prettierRequired = $null
    $openapiTsRequired = $null
    if ($packageJson) {
        if ($packageJson.packageManager) { $pnpmRequired = ($packageJson.packageManager -split "@")[1] }
        if ($packageJson.devDependencies.'@playwright/test') { $playwrightRequired = ($packageJson.devDependencies.'@playwright/test' -replace '[\^~]', '') }
        if ($packageJson.devDependencies.prettier) { $prettierRequired = ($packageJson.devDependencies.prettier -replace '[\^~]', '') }
        if ($packageJson.devDependencies.'openapi-typescript') { $openapiTsRequired = ($packageJson.devDependencies.'openapi-typescript' -replace '[\^~]', '') }
    } else {
        Add-StageResult -Stage "package.json" -Status "WARN" -Detail "could not be read/parsed; pnpm/Next/Playwright/Prettier/openapi-typescript baselines unavailable this run"
    }
    $fastapiRequired = Get-PyProjectExactPin -PackageName "fastapi"
    $pydanticRequired = Get-PyProjectExactPin -PackageName "pydantic"
    $pythonRequired = Get-RequiresPythonMinVersion
    $goRequired = Get-GoModMinVersion

    Test-ToolVersion -Name "Python 3.12" -Command "py" -ArgumentList @("-3.12", "--version") -Pattern "(\d+\.\d+\.\d+)" -Recommended $pythonRequired -Mode "min" -Severity "required" -InstallHint "https://www.python.org/downloads/ (winget install --id Python.Python.3.12 -e)" | Out-Null
    Test-ToolVersion -Name "pnpm" -Command "pnpm" -ArgumentList @("--version") -Pattern "(\d+\.\d+\.\d+)" -Recommended $pnpmRequired -Mode "min" -Severity "required" -InstallHint "corepack enable && corepack prepare pnpm@latest --activate (https://pnpm.io/installation)" | Out-Null
    Test-ToolVersion -Name "Go" -Command "go" -ArgumentList @("version") -Pattern "go(\d+\.\d+\.\d+)" -Recommended $goRequired -Mode "min" -Severity "required" -InstallHint "https://go.dev/dl/" | Out-Null

    if ($Config.tools -and @($Config.tools).Count -gt 0) {
        foreach ($tool in $Config.tools) {
            Test-ToolVersion -Name $tool.name -Command $tool.command -ArgumentList $tool.versionArgs -Pattern $tool.versionPattern -Recommended $tool.recommendedMinVersion -Mode "min" -Severity $tool.severity -InstallHint $tool.installHint | Out-Null
        }
    } else {
        Add-StageResult -Stage "full-check.config.json" -Status "WARN" -Detail "no [tools] entries loaded; Docker/Docker Compose/protoc family checks were skipped this run"
    }

    $goToolingPresent = [bool](Get-Command "go" -ErrorAction SilentlyContinue) -and [bool](Get-Command "protoc" -ErrorAction SilentlyContinue) -and [bool](Get-Command "protoc-gen-go" -ErrorAction SilentlyContinue) -and [bool](Get-Command "protoc-gen-go-grpc" -ErrorAction SilentlyContinue)

    Write-Section "Phase 1 — Dependency installation"

    if ($AdminToken -eq "") {
        $AdminToken = "local-gate-" + ([guid]::NewGuid().ToString("N").Substring(0, 16))
    }
    $env:ADMIN_TOKEN = $AdminToken
    Write-Host "Using ADMIN_TOKEN=$($AdminToken.Substring(0,16))... for this run (API container and test runner share it)."

    $pipInstallResult = Invoke-WithRetry -Description "py -3.12 -m pip install -e .[dev]" -MaxAttempts 3 -InitialDelaySeconds 5 -DelayStepSeconds 5 -ScriptBlock {
        Invoke-Native -Command "py" -ArgumentList @("-3.12", "-m", "pip", "install", "-e", ".[dev]")
    }
    Add-StageResult -Stage "pip install -e .[dev]" -Status $(if ($pipInstallResult -eq 0) { "OK" } else { "FAIL" })
    if ($pipInstallResult -ne 0) {
        Add-Recommendation -Tool "pip install -e .[dev]" -Issue "install failed" -Hint "Check the transcript above for the pip error. Common causes: no internet, a locked virtualenv, or a Python version mismatch (project requires >= $pythonRequired)."
    }

    $pnpmInstallResult = Invoke-WithRetry -Description "pnpm install" -MaxAttempts 3 -InitialDelaySeconds 5 -DelayStepSeconds 5 -ScriptBlock {
        Invoke-Native -Command "pnpm" -ArgumentList @("install")
    }
    Add-StageResult -Stage "pnpm install" -Status $(if ($pnpmInstallResult -eq 0) { "OK" } else { "FAIL" })
    if ($pnpmInstallResult -ne 0) {
        Add-Recommendation -Tool "pnpm install" -Issue "install failed" -Hint "Check the transcript above. Common causes: no internet/registry access, or a stale pnpm-lock.yaml conflict (try 'pnpm install --no-frozen-lockfile')."
    }

    $playwrightInstallResult = Invoke-WithRetry -Description "pnpm exec playwright install chromium" -MaxAttempts 3 -InitialDelaySeconds 5 -DelayStepSeconds 5 -ScriptBlock {
        Invoke-Native -Command "pnpm" -ArgumentList @("exec", "playwright", "install", "chromium")
    }
    Add-StageResult -Stage "playwright install chromium" -Status $(if ($playwrightInstallResult -eq 0) { "OK" } else { "FAIL" })

    Write-Section "Phase 2 — Project-pinned version verification"

    Test-ToolVersion -Name "FastAPI (pip)" -Command "py" -ArgumentList @("-3.12", "-c", "import fastapi; print(fastapi.__version__)") -Pattern "(\d+\.\d+\.\d+)" -Recommended $fastapiRequired -Mode "exact" -Severity "optional" | Out-Null
    Test-ToolVersion -Name "Pydantic (pip)" -Command "py" -ArgumentList @("-3.12", "-c", "import pydantic; print(pydantic.__version__)") -Pattern "(\d+\.\d+\.\d+)" -Recommended $pydanticRequired -Mode "exact" -Severity "optional" | Out-Null
    Test-ToolVersion -Name "Next.js" -Command "pnpm" -ArgumentList @("--filter", "@country-decision-atlas/web", "exec", "next", "--version") -Pattern "(\d+\.\d+\.\d+)" -Recommended "15.0.0" -Mode "min" -Severity "optional" | Out-Null
    Test-ToolVersion -Name "Playwright" -Command "pnpm" -ArgumentList @("exec", "playwright", "--version") -Pattern "(\d+\.\d+\.\d+)" -Recommended $playwrightRequired -Mode "min" -Severity "optional" | Out-Null
    Test-ToolVersion -Name "Prettier" -Command "pnpm" -ArgumentList @("exec", "prettier", "--version") -Pattern "(\d+\.\d+\.\d+)" -Recommended $prettierRequired -Mode "min" -Severity "optional" | Out-Null
    Test-ToolVersion -Name "openapi-typescript" -Command "pnpm" -ArgumentList @("exec", "openapi-typescript", "--version") -Pattern "(\d+\.\d+\.\d+)" -Recommended $openapiTsRequired -Mode "min" -Severity "optional" | Out-Null

    Write-Section "Phase 3 — Static quality gate"

    function Run-GateStep {
        param([string]$Name, [string]$Command, [string[]]$ArgumentList, [string]$WorkingDirectory = $RepoRoot)
        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        $exitCode = -1
        try {
            Push-Location $WorkingDirectory -ErrorAction Stop
            try {
                $exitCode = Invoke-Native -Command $Command -ArgumentList $ArgumentList
            } finally {
                Pop-Location
            }
        } catch {
            Write-Host ("  ERROR running step '{0}': {1}" -f $Name, $_.Exception.Message) -ForegroundColor Red
            $exitCode = -1
        }
        $sw.Stop()
        Add-StageResult -Stage $Name -Status $(if ($exitCode -eq 0) { "OK" } else { "FAIL" }) -DurationSeconds $sw.Elapsed.TotalSeconds
        return $exitCode
    }

    try {
        Run-GateStep -Name "ruff check" -Command "py" -ArgumentList @("-3.12", "-m", "ruff", "check", "apps", "packages", "scripts", "tests") | Out-Null
        Run-GateStep -Name "ruff format --check" -Command "py" -ArgumentList @("-3.12", "-m", "ruff", "format", "--check", "apps", "packages", "scripts", "tests") | Out-Null
        Run-GateStep -Name "mypy" -Command "py" -ArgumentList @("-3.12", "-m", "mypy", "apps", "packages", "scripts", "tests") | Out-Null
        Run-GateStep -Name "sqlfluff lint" -Command "py" -ArgumentList @("-3.12", "-m", "sqlfluff", "lint", "database", "--dialect", "postgres") | Out-Null
        New-Item -ItemType Directory -Force -Path (Join-Path $RepoRoot ".tmp\pytest") -ErrorAction SilentlyContinue | Out-Null
        Run-GateStep -Name "pytest" -Command "py" -ArgumentList @("-3.12", "-m", "pytest", "-p", "no:cacheprovider", "--basetemp=.tmp/pytest") | Out-Null
        Run-GateStep -Name "pnpm contracts:generate" -Command "pnpm" -ArgumentList @("contracts:generate") | Out-Null
        Run-GateStep -Name "pnpm quality" -Command "pnpm" -ArgumentList @("quality") | Out-Null
    } catch {
        Add-StageResult -Stage "Phase 3 — Static quality gate" -Status "FAIL" -Detail "unexpected error: $($_.Exception.Message)"
    }

    Write-Section "Phase 4 — Go notifier gate"

    if (-not $goToolingPresent) {
        Add-StageResult -Stage "Go notifier gate" -Status "SKIP" -Detail "go/protoc/protoc-gen-go/protoc-gen-go-grpc not all present; see Phase 0 recommendations above"
    } else {
        try {
            $notifierDir = Join-Path $RepoRoot "apps\notifier"
            Run-GateStep -Name "protoc generate" -Command "protoc" -WorkingDirectory $notifierDir -ArgumentList @(
                "-I", ".",
                "--go_out=.", "--go_opt=module=github.com/country-decision-atlas/notifier",
                "--go-grpc_out=.", "--go-grpc_opt=module=github.com/country-decision-atlas/notifier",
                "proto/subscriptions.proto"
            ) | Out-Null
            Run-GateStep -Name "go vet" -Command "go" -WorkingDirectory $notifierDir -ArgumentList @("vet", "./...") | Out-Null
            Run-GateStep -Name "go test" -Command "go" -WorkingDirectory $notifierDir -ArgumentList @("test", "./...") | Out-Null
        } catch {
            Add-StageResult -Stage "Phase 4 — Go notifier gate" -Status "FAIL" -Detail "unexpected error: $($_.Exception.Message)"
        }
    }

    if (-not $SkipDocker) {
        Write-Section "Phase 5 — Docker stack, migrations, runtime smoke"
        try {
            $dockerPresent = [bool](Get-Command "docker" -ErrorAction SilentlyContinue)
            if (-not $dockerPresent) {
                Add-StageResult -Stage "Docker stack / migrations / runtime smoke / E2E" -Status "SKIP" -Detail "docker command not found; see Phase 0 recommendations"
            } else {
                $dockerInfoExit = Invoke-Native -Command "docker" -ArgumentList @("info")
                if ($dockerInfoExit -ne 0) {
                    Add-StageResult -Stage "docker daemon reachable" -Status "SKIP" -Detail "Docker Desktop is not running; skipping all Docker-dependent steps"
                } else {
                    Add-StageResult -Stage "docker daemon reachable" -Status "OK"

                    $dockerUpExit = Invoke-WithRetry -Description "docker compose up --build -d api" -MaxAttempts $DockerMaxAttempts -InitialDelaySeconds $DockerRetryInitialDelaySeconds -DelayStepSeconds $DockerRetryDelayStepSeconds -ScriptBlock {
                        Invoke-Native -Command "docker" -ArgumentList @("compose", "up", "--build", "-d", "api")
                    }
                    Add-StageResult -Stage "docker compose up --build -d api" -Status $(if ($dockerUpExit -eq 0) { "OK" } else { "FAIL" })
                    if ($dockerUpExit -ne 0) {
                        Add-Recommendation -Tool "Docker build" -Issue "docker compose up --build failed after $DockerMaxAttempts attempts" -Hint "Check Docker Desktop is running with enough resources (Settings > Resources), check disk space, and inspect the transcript for the underlying build error."
                    }

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
            }
        } catch {
            Add-StageResult -Stage "Phase 5 — Docker stack" -Status "FAIL" -Detail "unexpected error: $($_.Exception.Message)"
        }
    } else {
        Add-StageResult -Stage "Docker stack / migrations / runtime smoke / E2E" -Status "SKIP" -Detail "-SkipDocker was set"
    }

    if (-not $SkipPreCommit) {
        Write-Section "Phase 6 — pre-commit"
        try {
            Run-GateStep -Name "pre-commit run --all-files" -Command "py" -ArgumentList @("-3.12", "-m", "pre_commit", "run", "--all-files") | Out-Null
        } catch {
            Add-StageResult -Stage "pre-commit run --all-files" -Status "FAIL" -Detail "unexpected error: $($_.Exception.Message)"
        }
    } else {
        Add-StageResult -Stage "pre-commit run --all-files" -Status "SKIP" -Detail "-SkipPreCommit was set"
    }

    Write-Section "Phase 7 — git status"
    Invoke-Native -Command "git" -ArgumentList @("diff", "--check") | Out-Null
    Invoke-Native -Command "git" -ArgumentList @("status", "--short") | Out-Null

} catch {
    Add-StageResult -Stage "UNEXPECTED SCRIPT ERROR" -Status "FAIL" -Detail $_.Exception.Message
    Write-Host ""
    Write-Host "An unexpected error occurred. The script did not crash — see the report for details." -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor DarkRed
} finally {
    $ScriptFinishedAt = Get-Date
    $durationMinutes = [math]::Round(($ScriptFinishedAt - $ScriptStartedAt).TotalMinutes, 1)

    Write-Section "Summary"
    $StageResults | Format-Table -AutoSize

    $failCount = @($StageResults | Where-Object { $_.Status -eq "FAIL" }).Count
    $warnCount = @($StageResults | Where-Object { $_.Status -eq "WARN" }).Count
    $skipCount = @($StageResults | Where-Object { $_.Status -eq "SKIP" }).Count
    $okCount = @($StageResults | Where-Object { $_.Status -eq "OK" }).Count

    Write-Host ""
    Write-Host ("OK: {0}   WARN: {1}   FAIL: {2}   SKIP: {3}   Duration: {4} min" -f $okCount, $warnCount, $failCount, $skipCount, $durationMinutes)

    if ($Recommendations.Count -gt 0) {
        Write-Section "Recommendations"
        $recLines = New-Object System.Collections.Generic.List[string]
        $recLines.Add("Country Decision Atlas — full-check.ps1 recommendations")
        $recLines.Add("Generated: $ScriptFinishedAt")
        $recLines.Add("")
        foreach ($rec in $Recommendations) {
            $line = "- $($rec.Tool): $($rec.Issue)"
            Write-Host $line -ForegroundColor Yellow
            $recLines.Add($line)
            if ($rec.Hint) {
                $hintLine = "    -> $($rec.Hint)"
                Write-Host $hintLine -ForegroundColor Yellow
                $recLines.Add($hintLine)
            }
        }
        try {
            $recLines | Out-File -FilePath $RecommendationsPath -Encoding utf8
        } catch {
            Write-Host "WARNING: could not write recommendations.txt: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }

    $summaryLines = New-Object System.Collections.Generic.List[string]
    $summaryLines.Add("Country Decision Atlas — full-check.ps1 run")
    $summaryLines.Add("Started:  $ScriptStartedAt")
    $summaryLines.Add("Finished: $ScriptFinishedAt")
    $summaryLines.Add("Duration: $durationMinutes minutes")
    $summaryLines.Add("OK=$okCount WARN=$warnCount FAIL=$failCount SKIP=$skipCount")
    $summaryLines.Add("git: branch=$($gitContext.branch) commit=$($gitContext.commit) dirty=$($gitContext.dirtyFileCount) $($gitContext.aheadBehind)")
    $summaryLines.Add("")
    foreach ($r in $StageResults) {
        $durationText = ""
        if ($r.DurationSeconds -ge 1) { $durationText = " ($($r.DurationSeconds)s)" }
        $summaryLines.Add(("[{0}] {1} {2}{3}" -f $r.Status, $r.Stage, $r.Detail, $durationText))
    }
    if ($Recommendations.Count -gt 0) {
        $summaryLines.Add("")
        $summaryLines.Add("See recommendations.txt for $($Recommendations.Count) actionable suggestion(s).")
    }
    try {
        $summaryLines | Out-File -FilePath $SummaryPath -Encoding utf8
    } catch {
        Write-Host "WARNING: could not write summary.txt: $($_.Exception.Message)" -ForegroundColor Yellow
    }

    try {
        $report = [pscustomobject]@{
            startedAt       = $ScriptStartedAt
            finishedAt      = $ScriptFinishedAt
            durationMinutes = $durationMinutes
            counts          = [pscustomobject]@{ ok = $okCount; warn = $warnCount; fail = $failCount; skip = $skipCount }
            git             = $gitContext
            system          = $systemInfo
            network         = $NetworkResults
            stages          = $StageResults
            recommendations = $Recommendations
        }
        $reportJsonText = $report | ConvertTo-Json -Depth 6
        [System.IO.File]::WriteAllText($ReportJsonPath, $reportJsonText, (New-Object System.Text.UTF8Encoding($false)))
    } catch {
        Write-Host "WARNING: could not write report.json: $($_.Exception.Message)" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "Full transcript:  $TranscriptPath"
    Write-Host "Summary:          $SummaryPath"
    Write-Host "JSON report:      $ReportJsonPath"
    if ($Recommendations.Count -gt 0) {
        Write-Host "Recommendations:  $RecommendationsPath"
    }

    try { Stop-Transcript | Out-Null } catch { }
}

if ($failCount -gt 0) {
    exit 1
} else {
    exit 0
}
