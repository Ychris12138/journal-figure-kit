# Journal Figure Kit bootstrap. Compatible with Windows PowerShell 5.1+.
# No arguments: Codex, user scope, isolated dependencies, backup before update.
# Optional overrides: JFK_PYTHON (executable), JFK_INSTALLER (local install.py).

& {
    param([string[]]$BootstrapArgs = @())
    $ErrorActionPreference = 'Stop'
    $jfkVersion = '0.11.0'
    $jfkProbe = 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)'
    $jfkPython = $null
    $jfkPrefix = @()

    if ($env:JFK_PYTHON) {
        $jfkCandidates = @(@{ Executable = $env:JFK_PYTHON; Prefix = @() })
    } else {
        $jfkCandidates = @(
            @{ Executable = 'py'; Prefix = @('-3.12') },
            @{ Executable = 'python'; Prefix = @() },
            @{ Executable = 'python3'; Prefix = @() },
            @{ Executable = 'py'; Prefix = @('-3') }
        )
    }
    foreach ($candidate in $jfkCandidates) {
        $command = Get-Command -Name $candidate.Executable -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
        if (-not $command -or $command.Source -match '[\\/]WindowsApps[\\/]') { continue }
        $prefix = @($candidate.Prefix)
        try {
            & $command.Source @prefix -c $jfkProbe *> $null
            if ($LASTEXITCODE -eq 0) {
                $jfkPython = $command.Source
                $jfkPrefix = $prefix
                break
            }
        } catch { continue }
    }
    if (-not $jfkPython) {
        throw 'Journal Figure Kit needs Python 3.12 or newer. Install Python, or set JFK_PYTHON to its executable path.'
    }

    Write-Host "Journal Figure Kit v$jfkVersion - using $jfkPython"
    if ($env:JFK_INSTALLER) {
        if (-not (Test-Path -LiteralPath $env:JFK_INSTALLER -PathType Leaf)) {
            throw 'JFK_INSTALLER must point to an existing local install.py.'
        }
        & $jfkPython @jfkPrefix $env:JFK_INSTALLER --quick @BootstrapArgs
    } else {
        $jfkUrl = "https://raw.githubusercontent.com/Ychris12138/journal-figure-kit/v$jfkVersion/install.py"
        $jfkCode = "from urllib.request import urlopen; exec(urlopen('$jfkUrl', timeout=60).read())"
        & $jfkPython @jfkPrefix -c $jfkCode --quick @BootstrapArgs
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Journal Figure Kit installation failed (Python exit code $LASTEXITCODE)."
    }
} -BootstrapArgs $args
