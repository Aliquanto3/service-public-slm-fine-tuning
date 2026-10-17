# Importe sur le nouveau PC l'état exporté par exporter-etat.ps1.
# Usage, depuis le dépôt cloné : powershell -File outils\migration\importer-etat.ps1 -Source E:\slmsp-transfert
# N'écrase rien d'existant sans -Forcer. Le fichier .env reste à remplir à la main.
param(
    [Parameter(Mandatory = $true)][string]$Source,
    [switch]$Forcer
)
$ErrorActionPreference = 'Stop'
$depot = (Resolve-Path "$PSScriptRoot\..\..").Path
$var = if ($env:SLMSP_VAR_DIR) { $env:SLMSP_VAR_DIR } else { Join-Path $env:LOCALAPPDATA 'slmsp\var' }
$cle = ($depot -replace '[:\\/ ]', '-')
$memoire = Join-Path $env:USERPROFILE ".claude\projects\$cle\memory"

function Copier([string]$de, [string]$vers) {
    if (-not (Test-Path $de)) { Write-Warning "absent du transfert : $de"; return }
    $options = @('/E', '/R:1', '/W:1', '/NFL', '/NDL', '/NJH', '/NP')
    if (-not $Forcer) { $options += @('/XC', '/XN', '/XO') }  # ne remplace aucun fichier existant
    & robocopy $de $vers @options | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy a échoué ($LASTEXITCODE) : $de" }
    Write-Host "ok  $vers"
}

Copier (Join-Path $Source 'var') $var
Copier (Join-Path $Source 'depot') $depot
Copier (Join-Path $Source 'claude\memory') $memoire
if ($cle -ne 'C--Users-Utilisateur-Documents-GitHub-service-public-slm-fine-tuning') {
    Write-Warning "Chemin du dépôt différent de la tour : mémoire Claude copiée sous $memoire"
}
Write-Host "CLAUDE.md globaux à replacer à la main s'ils manquent : $Source\claude\"
Write-Host "Import terminé. Suite : docs/reprise-deuxieme-pc.md, étape « Vérifier »."
