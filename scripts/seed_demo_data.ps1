param(
    [switch]$Reset,
    [switch]$NoImages,
    [int]$Timeout = 20
)

$pythonBin = "python"
if (Test-Path "env\Scripts\python.exe") {
    $pythonBin = "env\Scripts\python.exe"
}

$args = @("manage.py", "seed_demo_data", "--timeout", "$Timeout")

if ($Reset) {
    $args += "--reset"
}

if ($NoImages) {
    $args += "--no-images"
}

Write-Host "Execution: $pythonBin $($args -join ' ')"
& $pythonBin @args

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

