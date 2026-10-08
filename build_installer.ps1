[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"

function Invoke-Python {
    param(
        [Parameter(Mandatory = $true)]
        [string[]] $Arguments
    )

    if (Test-Path $venvPython) {
        & $venvPython @Arguments
        return
    }

    & py -3.12 @Arguments
}

function Resolve-InnoSetupCompiler {
    $command = Get-Command ISCC -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $candidates = @(@(
        (Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe"),
        (Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe"),
        (Join-Path $env:ProgramFiles "Inno Setup 6\ISCC.exe")
    ) | Where-Object { $_ -and (Test-Path $_) })

    if ($candidates.Count -gt 0) {
        return $candidates[0]
    }

    throw "No se encontró Inno Setup. Instale Inno Setup 6 y vuelva a ejecutar este script."
}

Push-Location $repoRoot
try {
    Write-Host "Verificando PyInstaller..."
    Invoke-Python -Arguments @("-m", "PyInstaller", "--version")

    $iscc = Resolve-InnoSetupCompiler

    Write-Host "Limpiando salidas anteriores..."
    foreach ($folder in @("build", "dist", "installer")) {
        $target = Join-Path $repoRoot $folder
        if (Test-Path $target) {
            Remove-Item $target -Recurse -Force
        }
    }

    Write-Host "Generando ejecutable con PyInstaller..."
    Invoke-Python -Arguments @("-m", "PyInstaller", "--noconfirm", "SisAlmacen.spec")

    $exePath = Join-Path $repoRoot "dist\SisAlmacen\SisAlmacen.exe"
    if (-not (Test-Path $exePath)) {
        throw "No se generó el ejecutable esperado en dist\SisAlmacen\SisAlmacen.exe."
    }

    Write-Host "Compilando instalador con Inno Setup..."
    & $iscc (Join-Path $repoRoot "SisAlmacenInstaller.iss")

    $installerDir = Join-Path $repoRoot "installer"
    if (-not (Test-Path $installerDir)) {
        throw "La carpeta installer no fue generada."
    }

    Write-Host ""
    Write-Host "Proceso completado."
    Write-Host "Ejecutable: $exePath"
    Write-Host "Instalador: $(Join-Path $installerDir 'SisAlmacen-Installer.exe')"
}
finally {
    Pop-Location
}
