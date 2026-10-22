# Campagne v11 (MiniCPM5-2B, Qwen3.5-2B, Qwen3.5-0.8B) : un run (TOML en argument) sous garde RAM, puis export cuda et notation
# (q4_k_m, jeu v1.1, comme la Baseline), avec garde-fou de coût Anthropic (4,5 EUR par notation).
param([string]$Toml, [string]$RunId, [switch]$SansNotation)
Set-Location C:\Users\Anael\dev\service-public-slm-fine-tuning
$env:PYTORCH_CUDA_ALLOC_CONF = "expandable_segments:True"
$env:GARDE_RAM_GO = "28"
$py = ".venv\Scripts\python.exe"
$garde = "$PSScriptRoot\garde_ram.py"
$filtre = '^(ok|erreur|train |run |Run |Statut|export|T.che|Q |RD |CR |LC |CO |RE |CT |NR |GARDE)|rreur|refus|budget|Traceback|occup|complet|interrompu|out of memory'
function DepenseAnthropic {
  $l = & $py -m slmsp budget etat 2>$null | Where-Object { $_ -match '^anthropic' }
  [double](($l -split '\s+')[2])
}
function Lancer($a) {
  & $py $garde @a 2>&1 | ForEach-Object { "$_" } | Where-Object { $_ -notmatch 'panne simul|it/s\]|s/it\]' } | Where-Object { $_ -match $filtre }
  "=== code $LASTEXITCODE $(Get-Date -Format HH:mm)"
}
if ($RunId) { $run = Get-Item (Join-Path (Get-Location) "runs\train\$RunId") } else {
  "=== train $Toml $(Get-Date -Format HH:mm)"
  $avantT = @(Get-ChildItem runs\train -Directory | ForEach-Object Name)
  Lancer @("train", "run", "--config", $Toml)
  $run = Get-ChildItem runs\train -Directory | Where-Object { $avantT -notcontains $_.Name } | Sort-Object Name | Select-Object -Last 1
}
if (-not $run) { "=== pas de run créé"; exit 1 }
# Statut courant : dernière ligne de etat.jsonl (run.json garde le statut initial).
$statut = ((Get-Content "$($run.FullName)\etat.jsonl" -Tail 1) | ConvertFrom-Json).statut
"=== run $($run.Name) : $statut"
if ($statut -ne "complet") { exit 1 }
$avantE = @(Get-ChildItem runs\export -Directory | ForEach-Object Name)
Lancer @("export", "--depuis", $run.Name, "--variante", "cuda")
$exp = Get-ChildItem runs\export -Directory | Where-Object { $avantE -notcontains $_.Name } | Sort-Object Name | Select-Object -Last 1
if (-not $exp) { "=== pas d'export"; exit 1 }
"=== export : $($exp.Name)"
if ($SansNotation) { exit 0 }
$avant = DepenseAnthropic
$avantN = @(Get-ChildItem runs\eval-notation -Directory | ForEach-Object Name)
& $py -m slmsp eval run --modele "ft:$($exp.Name)" --quantification q4_k_m --jeu v1.1 --variante cuda --plafond-estime 4.5 2>&1 | ForEach-Object { "$_" } | Where-Object { $_ -notmatch 'panne simul' } | Where-Object { $_ -match $filtre }
"=== code eval $LASTEXITCODE $(Get-Date -Format HH:mm)"
# C6 : coût lu dans scores.json du run de notation (juste même si deux notations se chevauchent),
# différence du registre seulement en repli.
$notation = Get-ChildItem runs\eval-notation -Directory | Where-Object { $avantN -notcontains $_.Name } | Sort-Object Name | Select-Object -Last 1
$scores = if ($notation) { Join-Path $notation.FullName "scores.json" } else { $null }
if ($scores -and (Test-Path $scores)) { $cout = [double]((Get-Content $scores -Raw | ConvertFrom-Json).cout_juge_total_eur) }
else { $cout = (DepenseAnthropic) - $avant }
"=== notation : $([math]::Round($cout,2)) EUR anthropic (dépense totale $(DepenseAnthropic))"
if ($cout -gt 4.5) { "=== GARDE-FOU COUT : $cout EUR > 4,5 ; ne plus noter" }
