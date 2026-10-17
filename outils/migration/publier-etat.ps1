# Construit l'archive de l'état hors git et la publie en release du dépôt PRIVÉ dédié
# (le dépôt du projet est public : l'état n'y est jamais joint). Voir docs/reprise-deuxieme-pc.md.
# Usage, sur le PC source :
#   powershell -NoProfile -ExecutionPolicy Bypass -File outils/migration/publier-etat.ps1 [-Date 2026-10-17] [-SansPublier]
# Contenu : var (bases SQLite copiées par l'API de sauvegarde, journaux), data/cache, data/train,
# mémoire Claude Code du projet, CLAUDE.md globaux. Refuse de publier si un secret est repéré.
param(
    [string]$Date = (Get-Date -Format 'yyyy-MM-dd'),
    [string]$Repo = 'Aliquanto3/slmsp-etat',
    [switch]$SansPublier
)
$ErrorActionPreference = 'Stop'
$depot = (Resolve-Path "$PSScriptRoot\..\..").Path
$var = if ($env:SLMSP_VAR_DIR) { $env:SLMSP_VAR_DIR } else { Join-Path $env:LOCALAPPDATA 'slmsp\var' }
$cle = ($depot -replace '[:\\/ ]', '-')
$memoire = Join-Path $env:USERPROFILE ".claude\projects\$cle\memory"
$tag = "etat-$Date"
$nom = "etat-slmsp-$Date.zip"
$travail = Join-Path $env:TEMP "slmsp-publier-$tag"
$x = Join-Path $travail 'x'
$zip = Join-Path $travail $nom

function Copier([string]$de, [string]$vers, [string[]]$exclureDossiers = @(), [string[]]$exclureFichiers = @()) {
    $arguments = @($de, $vers, '/E', '/R:1', '/W:1', '/NFL', '/NDL', '/NJH', '/NJS', '/NP')
    if ($exclureDossiers) { $arguments += '/XD'; $arguments += $exclureDossiers }
    if ($exclureFichiers) { $arguments += '/XF'; $arguments += $exclureFichiers }
    & robocopy @arguments | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy a échoué ($LASTEXITCODE) : $de" }
}

if (Test-Path $travail) { Remove-Item $travail -Recurse -Force }
New-Item -ItemType Directory -Force (Join-Path $x 'var'), (Join-Path $x 'claude') | Out-Null

# Bases SQLite : sauvegarde cohérente même si un processus slmsp écrit (pas de copie brute du WAL).
Copier $var (Join-Path $x 'var') @('pids', 'unsloth') @('*.sqlite', '*.sqlite-wal', '*.sqlite-shm', 'gpu.lock')
$sauvegarde = 'import sqlite3, sys; s = sqlite3.connect(sys.argv[1]); d = sqlite3.connect(sys.argv[2]); s.backup(d); d.close(); s.close()'
Get-ChildItem $var -Filter '*.sqlite' | ForEach-Object {
    & uv run --no-sync python -I -c $sauvegarde $_.FullName (Join-Path $x "var\$($_.Name)")
    if ($LASTEXITCODE -ne 0) { throw "sauvegarde SQLite échouée : $($_.Name)" }
}
Copier (Join-Path $depot 'data\cache') (Join-Path $x 'depot\data\cache')
Copier (Join-Path $depot 'data\train') (Join-Path $x 'depot\data\train')
Copier $memoire (Join-Path $x 'claude\memory')
Copy-Item (Join-Path $env:USERPROFILE '.claude\CLAUDE.md') (Join-Path $x 'claude\CLAUDE-global.md')
Copy-Item (Join-Path (Split-Path $depot -Parent) 'CLAUDE.md') (Join-Path $x 'claude\CLAUDE-GitHub.md')

# Garde-fou : aucun fichier d'environnement, aucune clé reconnaissable.
$fichiers = Get-ChildItem $x -Recurse -File
$interdits = $fichiers | Where-Object { $_.Name -match '^\.env|\.pem$|\.key$|credentials' }
if ($interdits) { throw "Fichiers interdits dans l'archive : $($interdits.FullName -join ', ')" }
$motifs = 'sk-ant-[A-Za-z0-9_-]{20,}|hf_[A-Za-z0-9]{30,}|(MISTRAL|ANTHROPIC)_API_KEY\s*=\s*\S|Bearer\s+[A-Za-z0-9_.-]{20,}'
$suspects = $fichiers | Where-Object {
    $texte = [System.Text.Encoding]::GetEncoding(28591).GetString([System.IO.File]::ReadAllBytes($_.FullName))
    $texte -match $motifs
}
if ($suspects) { throw "Secret probable dans : $($suspects.FullName -join ', ')" }

Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($x, $zip)
$sha = (Get-FileHash $zip -Algorithm SHA256).Hash
Write-Host "Archive : $zip ($([math]::Round((Get-Item $zip).Length / 1MB, 1)) Mo, $($fichiers.Count) fichiers)"
Write-Host "SHA-256 : $sha"
if ($SansPublier) { return }

& gh repo view $Repo --json name 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    & gh repo create $Repo --private --add-readme --description 'État machine hors git de slmsp (privé)'
    if ($LASTEXITCODE -ne 0) { throw "création du dépôt $Repo échouée" }
}
if ((& gh repo view $Repo --json visibility -q .visibility) -ne 'PRIVATE') { throw "$Repo n'est pas privé : publication refusée" }
& gh release create $tag $zip --repo $Repo --title "État machine $Date" `
    --notes "État hors git pour la reprise sur un autre PC (voir docs/reprise-deuxieme-pc.md du dépôt slmsp). SHA-256 : $sha. Ne pas utiliser comme version." `
    --latest=false
if ($LASTEXITCODE -ne 0) { throw "gh release create a échoué ($LASTEXITCODE)" }
Write-Host "Publié : $Repo@$tag. Reporter le SHA-256 dans restaurer-etat.ps1."
