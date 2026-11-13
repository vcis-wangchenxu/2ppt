# Windows counterpart to run-python.sh. Forward every argument unchanged.
$ErrorActionPreference = 'Stop'
$skillRoot = Split-Path -Parent $PSScriptRoot
$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $skillRoot '../..'))
$pythonPath = $null

if ($env:PPT_MASTER_PYTHON) {
    $pythonPath = $env:PPT_MASTER_PYTHON
} else {
    $candidates = @(
        (Join-Path $repoRoot '.venv/Scripts/python.exe'),
        (Join-Path $skillRoot '.venv/Scripts/python.exe'),
        (Join-Path ([Environment]::GetFolderPath('UserProfile')) '.cache/ppt-master/venv/Scripts/python.exe')
    )
    if ($env:VIRTUAL_ENV) {
        $candidates += Join-Path $env:VIRTUAL_ENV 'Scripts/python.exe'
    }
    foreach ($name in @('python3', 'python')) {
        $command = Get-Command $name -CommandType Application -ErrorAction SilentlyContinue
        if ($command -and $command.Source -notmatch '[\\/]Microsoft[\\/]WindowsApps[\\/]') {
            $candidates += $command.Source
        }
    }
    $pythonPath = $candidates | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Select-Object -First 1
}

if (-not $pythonPath -or -not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
    [Console]::Error.WriteLine('PPT Master: create a Python 3.10+ venv or set PPT_MASTER_PYTHON to python.exe.')
    exit 2
}

$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
& $pythonPath -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)'
if ($LASTEXITCODE -ne 0) {
    [Console]::Error.WriteLine("PPT Master: Python 3.10+ is required; selected interpreter: $pythonPath")
    exit 2
}
& $pythonPath @args
exit $LASTEXITCODE
