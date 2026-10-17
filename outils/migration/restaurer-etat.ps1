# Restaure l'état hors git depuis la release du dépôt privé slmsp-etat (voir docs/reprise-deuxieme-pc.md).
# Usage, depuis le dépôt cloné :
#   powershell -NoProfile -ExecutionPolicy Bypass -File outils/migration/restaurer-etat.ps1
# Contenu : var (journaux Mistral, registre des budgets, verdicts), data/cache, data/train,
# mémoire Claude Code du projet, CLAUDE.md globaux (posés seulement s'ils manquent).
# N'écrase aucun fichier existant sans -Forcer. Le fichier .env n'est jamais dans l'archive.
param(
    [string]$Repo = 'Aliquanto3/slmsp-etat',
    [string]$Tag = 'etat-2026-10-17',
    [string]$Archive = 'etat-slmsp-2026-10-17.zip',
    [string]$Sha256 = '9D930AECB7A8669571B3B26A4CC7D528A9C951819D522ECF8CC2BEC926A267BB',
    [switch]$Forcer
)
$ErrorActionPreference = 'Stop'
$depot = (Resolve-Path "$PSScriptRoot\..\..").Path
$var = if ($env:SLMSP_VAR_DIR) { $env:SLMSP_VAR_DIR } else { Join-Path $env:LOCALAPPDATA 'slmsp\var' }
$cle = ($depot -replace '[:\\/ ]', '-')
$memoire = Join-Path $env:USERPROFILE ".claude\projects\$cle\memory"
$tmp = Join-Path $env:TEMP "slmsp-etat-$Tag"

if (Test-Path (Join-Path $var 'budget.sqlite')) {
    if (-not $Forcer) { throw "Un registre de budget existe déjà dans $var : restauration refusée (-Forcer pour passer outre)." }
}
if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
New-Item -ItemType Directory $tmp | Out-Null
& gh release download $Tag --repo $Repo --pattern $Archive --dir $tmp
if ($LASTEXITCODE -ne 0) { throw "gh release download a échoué ($LASTEXITCODE)" }
$zip = Join-Path $tmp $Archive
$h = (Get-FileHash $zip -Algorithm SHA256).Hash
if ($h -ne $Sha256) { throw "SHA-256 inattendu : $h" }
Expand-Archive $zip -DestinationPath (Join-Path $tmp 'x')
$x = Join-Path $tmp 'x'

function Copier([string]$de, [string]$vers) {
    $options = @('/E', '/R:1', '/W:1', '/NFL', '/NDL', '/NJH', '/NJS', '/NP')
    if (-not $Forcer) { $options += @('/XC', '/XN', '/XO') }
    & robocopy $de $vers @options | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy a échoué ($LASTEXITCODE) : $de" }
    Write-Host "ok  $vers"
}
Copier (Join-Path $x 'var') $var
Copier (Join-Path $x 'depot') $depot
Copier (Join-Path $x 'claude\memory') $memoire

$global = Join-Path $env:USERPROFILE '.claude\CLAUDE.md'
if (-not (Test-Path $global)) { Copy-Item (Join-Path $x 'claude\CLAUDE-global.md') $global; Write-Host "ok  $global" }
$github = Join-Path (Split-Path $depot -Parent) 'CLAUDE.md'
if (-not (Test-Path $github)) { Copy-Item (Join-Path $x 'claude\CLAUDE-GitHub.md') $github; Write-Host "ok  $github" }

Remove-Item $tmp -Recurse -Force
Write-Host "État restauré. Vérifier : uv run --no-sync slmsp budget etat"
