<#
    Comprueba que todo está listo ANTES de lanzar el script de migración.
    Ejecútalo desde esta misma carpeta (scripts/ de la skill):
        .\validar-configuracion.ps1
    Devuelve código de salida 0 si todo es correcto, 1 si hay algún problema.
#>

$ErrorActionPreference = "Stop"
$problemas = @()

# 1. Python 3.10 o superior
try {
    $version = (& python --version 2>&1) -replace 'Python\s*', ''
    $partes = $version.Split('.')
    $major = [int]$partes[0]; $minor = [int]$partes[1]
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
        $problemas += "Python $version detectado. Se necesita 3.10 o superior."
    } else {
        Write-Host "[OK] Python $version" -ForegroundColor Green
    }
} catch {
    $problemas += "No se encontró Python. Instálalo desde https://www.python.org/downloads/"
}

# 2. Existe config.yml
if (Test-Path "config.yml") {
    Write-Host "[OK] config.yml encontrado" -ForegroundColor Green
} else {
    $problemas += "Falta config.yml. Cópialo desde config.example.yml y rellénalo."
}

# 3. Tokens definidos como variables de entorno
if ([string]::IsNullOrWhiteSpace($env:JIRA_API_TOKEN)) {
    $problemas += 'Falta la variable de entorno JIRA_API_TOKEN. Defínela con: $env:JIRA_API_TOKEN = "..."'
} else {
    Write-Host "[OK] JIRA_API_TOKEN definido" -ForegroundColor Green
}
if ([string]::IsNullOrWhiteSpace($env:GITHUB_TOKEN)) {
    $problemas += 'Falta la variable de entorno GITHUB_TOKEN. Defínela con: $env:GITHUB_TOKEN = "..."'
} else {
    Write-Host "[OK] GITHUB_TOKEN definido" -ForegroundColor Green
}

# Resumen
Write-Host ""
if ($problemas.Count -eq 0) {
    Write-Host "Todo listo. Puedes lanzar el dry-run." -ForegroundColor Green
    exit 0
} else {
    Write-Host "Hay que resolver estos puntos antes de continuar:" -ForegroundColor Yellow
    $problemas | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
    exit 1
}
