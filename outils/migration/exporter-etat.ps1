# Exporte l'état hors git du projet vers un dossier de transfert (disque externe, partage).
# Usage : powershell -File outils\migration\exporter-etat.ps1 -Destination E:\slmsp-transfert [-AvecModeles]
# Voir docs/reprise-deuxieme-pc.md. Le fichier .env n'est jamais copié.
param(
    [Parameter(Mandatory = $true)][string]$Destination,
    [switch]$AvecModeles
)
$ErrorActionPreference = 'Stop'
$depot = (Resolve-Path "$PSScriptRoot\..\..").Path
$var = if ($env:SLMSP_VAR_DIR) { $env:SLMSP_VAR_DIR } else { Join-Path $env:LOCALAPPDATA 'slmsp\var' }
$memoire = Join-Path $env:USERPROFILE '.claude\projects\C--Users-Utilisateur-Documents-GitHub-service-public-slm-fine-tuning\memory'

# Aucun traitement ne doit écrire dans var pendant la copie (SQLite).
$actifs = Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='llama-server.exe'" |
    Where-Object { $_.CommandLine -and $_.CommandLine.Contains($depot) }
if ($actifs) { throw "Traitements slmsp en cours ($($actifs.Count)) : attendre leur fin avant d'exporter." }

function Copier([string]$source, [string]$cible, [string[]]$exclus = @()) {
    if (-not (Test-Path $source)) { Write-Warning "absent : $source"; return }
    $arguments = @($source, $cible, '/E', '/R:1', '/W:1', '/NFL', '/NDL', '/NJH', '/NP')
    if ($exclus) { $arguments += '/XD'; $arguments += $exclus }
    & robocopy @arguments | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy a échoué ($LASTEXITCODE) : $source" }
    Write-Host "ok  $source"
}

Copier $var (Join-Path $Destination 'var') @('pids', 'unsloth')
Copier (Join-Path $depot 'index') (Join-Path $Destination 'depot\index')
Copier (Join-Path $depot 'data\raw') (Join-Path $Destination 'depot\data\raw')
Copier (Join-Path $depot 'data\cache') (Join-Path $Destination 'depot\data\cache')
Copier (Join-Path $depot 'data\train') (Join-Path $Destination 'depot\data\train')
Copier $memoire (Join-Path $Destination 'claude\memory')
New-Item -ItemType Directory -Force (Join-Path $Destination 'claude') | Out-Null
if (Test-Path (Join-Path $env:USERPROFILE '.claude\CLAUDE.md')) {
    Copy-Item (Join-Path $env:USERPROFILE '.claude\CLAUDE.md') (Join-Path $Destination 'claude\CLAUDE-global.md') -Force
}
$parent = Split-Path $depot -Parent
if (Test-Path (Join-Path $parent 'CLAUDE.md')) {
    Copy-Item (Join-Path $parent 'CLAUDE.md') (Join-Path $Destination 'claude\CLAUDE-GitHub.md') -Force
}

if ($AvecModeles) {
    # Modèles de moins de 2B et embedding seulement (décision du 2026-10-17) ; le reste se
    # retélécharge avec `slmsp fetch modeles <slug>`.
    foreach ($slug in 'bge-m3', 'bge-m3-f16', 'granite-4.0-1b', 'minicpm5-1b', 'qwen3.5-0.8b', 'eurollm-1.7b', 'croissantllm-chat') {
        Copier (Join-Path $depot "models\$slug") (Join-Path $Destination "depot\models\$slug")
    }
}
Write-Host "Export terminé dans $Destination"
