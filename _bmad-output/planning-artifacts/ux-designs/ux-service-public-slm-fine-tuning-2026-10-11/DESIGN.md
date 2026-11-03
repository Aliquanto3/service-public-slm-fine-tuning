---
name: Assistant IA local secteur public (nom de produit à trouver)
description: Assistant IA local et hors ligne pour les agents publics, application de bureau Windows. Identité visuelle générique, adaptée à un outil de travail quotidien plutôt qu'à une page vitrine.
status: final
created: 2026-10-11
updated: 2026-10-11
colors:
  primary: '#0B6B78'            # bleu pétrole, ancre de marque
  primary-hover: '#084E58'      # bleu pétrole profond, survol et état pressé
  primary-soft: '#DCEFF1'       # bleu pétrole doux : sélection, survol de ligne, bulle de l'Agent
  on-primary: '#FFFFFF'
  accent: '#B4500F'             # orange brûlé : seul accent secondaire, marque non textuelle
  accent-soft: '#FBE7D7'        # orange clair : fond des insertions
  ink: '#141A1F'                # texte principal
  ink-soft: '#4B5560'           # texte secondaire (contraste AA sur blanc)
  gray: '#737E85'               # décor, icônes inactives ; jamais pour du texte de moins de 18,66 px
  line: '#C9D1D3'               # bordures, séparateurs
  surface: '#FFFFFF'            # fond des zones de travail
  surface-alt: '#EEF1F0'        # fond de la colonne de gauche, du panneau Sources, des zones d'entrée
  warning: '#E8A317'            # ambre : avertissement juridique, mode dégradé (icône et bordure seulement)
  danger: '#B42318'             # rouge : erreur (icône et bordure seulement, le texte reste en ink)
  focus-ring: '#1F5FD1'
typography:
  # Toutes les tailles sont en rem. L'échelle globale (100 à 150 %) agit sur la taille racine.
  display:
    fontFamily: 'system-ui, Segoe UI, Roboto, sans-serif'
    fontSize: 1.75rem
    fontWeight: '800'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  title:
    fontFamily: 'system-ui, Segoe UI, Roboto, sans-serif'
    fontSize: 1.25rem
    fontWeight: '700'
    lineHeight: '1.3'
    letterSpacing: -0.01em
  body:
    fontFamily: 'system-ui, Segoe UI, Roboto, sans-serif'
    fontSize: 1rem
    fontWeight: '400'
    lineHeight: '1.6'
  body-strong:
    fontFamily: 'system-ui, Segoe UI, Roboto, sans-serif'
    fontSize: 1rem
    fontWeight: '600'
    lineHeight: '1.6'
  small:
    fontFamily: 'system-ui, Segoe UI, Roboto, sans-serif'
    fontSize: 0.875rem
    fontWeight: '400'
    lineHeight: '1.5'
  label:
    fontFamily: 'system-ui, Segoe UI, Roboto, sans-serif'
    fontSize: 0.78rem
    fontWeight: '700'
    lineHeight: '1.4'
    letterSpacing: 0.12em
  mono:
    fontFamily: 'Cascadia Mono, Consolas, monospace'
    fontSize: 0.875rem
    fontWeight: '400'
    lineHeight: '1.5'
rounded:
  sm: 8px
  md: 12px
  lg: 16px
  full: 9999px
spacing:
  '1': 4px
  '2': 8px
  '3': 12px
  '4': 16px
  '5': 24px
  '6': 32px
  '7': 48px
  sidebar-width: 264px
  sources-width: 360px
  topbar-height: 56px
  content-max: 820px
components:
  button-primary:
    background: '{colors.primary}'
    foreground: '{colors.on-primary}'
    hover: '{colors.primary-hover}'
    radius: '{rounded.sm}'
    typography: '{typography.body-strong}'
  button-secondary:
    background: '{colors.surface}'
    foreground: '{colors.primary}'
    border: '1px solid {colors.line}'
    hover: '{colors.primary-soft}'
    radius: '{rounded.sm}'
  task-nav-item:
    foreground: '{colors.ink}'
    active-background: '{colors.primary-soft}'
    active-foreground: '{colors.primary}'
    active-indicator: '3px left bar {colors.primary}'
    radius: '{rounded.sm}'
  mode-indicator-offline:
    background: '{colors.surface-alt}'
    foreground: '{colors.ink}'
    dot: '{colors.gray}'
    radius: '{rounded.full}'
  mode-indicator-online:
    background: '{colors.surface-alt}'
    foreground: '{colors.ink}'
    dot: '{colors.accent}'
    radius: '{rounded.full}'
  message-agent:
    background: '{colors.primary-soft}'
    foreground: '{colors.ink}'
    radius: '{rounded.md}'
  message-assistant:
    background: '{colors.surface}'
    foreground: '{colors.ink}'
    border: '1px solid {colors.line}'
    radius: '{rounded.md}'
  citation-chip:
    background: '{colors.primary-soft}'
    foreground: '{colors.primary}'
    radius: '{rounded.full}'
    typography: '{typography.small}'
  legal-notice:
    background: '{colors.surface-alt}'
    foreground: '{colors.ink-soft}'
    border-left: '3px solid {colors.warning}'
    typography: '{typography.small}'
  source-card:
    background: '{colors.surface}'
    border: '1px solid {colors.line}'
    radius: '{rounded.md}'
  editor-pane:
    background: '{colors.surface-alt}'
    border: '1px solid {colors.line}'
    radius: '{rounded.md}'
  diff-insert:
    background: '{colors.accent-soft}'
    foreground: '{colors.ink}'
    decoration: 'underline'
  diff-delete:
    foreground: '{colors.ink-soft}'
    decoration: 'line-through'
  feedback-button:
    foreground: '{colors.ink-soft}'
    selected-foreground: '{colors.primary}'
  composer:
    background: '{colors.surface-alt}'
    border: '1px solid {colors.line}'
    focus-border: '2px solid {colors.focus-ring}'
    placeholder: '{colors.ink-soft}'
    radius: '{rounded.md}'
    typography: '{typography.body}'
  dataset-card:
    background: '{colors.surface}'
    border: '1px solid {colors.line}'
    radius: '{rounded.md}'
    title: '{typography.body-strong}'
    meta: '{typography.small} {colors.ink-soft}'
  data-table:
    background: '{colors.surface}'
    row-alt: '{colors.surface-alt}'
    header: '{typography.body-strong}'
    border: '1px solid {colors.line}'
    footer: '{typography.small} {colors.ink-soft}'
  callout-warning:
    background: '{colors.surface-alt}'
    foreground: '{colors.ink}'
    border-left: '3px solid {colors.warning}'
    radius: '{rounded.sm}'
  callout-danger:
    background: '{colors.surface-alt}'
    foreground: '{colors.ink}'
    border-left: '3px solid {colors.danger}'
    radius: '{rounded.sm}'
  flagged-passage:
    background: '{colors.surface-alt}'
    foreground: '{colors.ink}'
    decoration: 'underline dotted 2px {colors.warning}'
  letter-placeholder:
    background: '{colors.primary-soft}'
    foreground: '{colors.primary}'
    typography: '{typography.body-strong}'
    radius: '{rounded.sm}'
  dialog:
    background: '{colors.surface}'
    radius: '{rounded.lg}'
    shadow: '0 8px 24px rgba(20,26,31,0.08)'
    scrim: 'rgba(20,26,31,0.32)'
  inline-confirmation:
    foreground: '{colors.ink-soft}'
    typography: '{typography.small}'
---

## Brand & Style

L'Assistant suit une charte graphique générique, pensée pour un **outil de travail quotidien**. L'identité se reconnaît au bleu pétrole `{colors.primary}`, au rythme typographique serré des titres et aux étiquettes en capitales. Les effets de vitrine sont exclus : animations au défilement, curseur personnalisé, compteurs animés, visuels en orbite. Un agent d'accueil l'ouvre vingt fois par jour, devant un usager. L'interface doit être calme, lisible et prévisible.

Posture : **sobre, digne de confiance, jamais officielle**. L'Assistant n'imite ni le Système de design de l'État (DSFR) ni la marque Marianne. Rien ne doit laisser croire à un outil de l'État.

Le logotype (pictogramme à trois barres et nom affiché en texte) est placé en bas de la colonne de gauche, en petit, avec la mention du nom de produit.

## Colors

- **Bleu pétrole `{colors.primary}`.** C'est l'ancre de marque. Il sert aux actions principales, à la Tâche active, aux puces de citation et aux liens. Contraste de 6,2:1 sur blanc, donc utilisable en texte. L'anneau de focus a sa propre couleur, `{colors.focus-ring}` (bleu vif, 5,8:1 sur blanc).
- **Bleu pétrole profond `{colors.primary-hover}`.** Réservé au survol et à l'état pressé des actions principales.
- **Bleu pétrole doux `{colors.primary-soft}`.** Sert de fond pour la sélection, la bulle de l'Agent et les puces de citation. Jamais en grand aplat décoratif.
- **Orange brûlé `{colors.accent}`.** Seul accent secondaire, avec deux usages : la pastille du Mode connecté et le fond des insertions en Correction (`{colors.accent-soft}`).
  - Il n'est **jamais utilisé en texte** : c'est une marque non textuelle (3:1 requis, 5,1:1 sur blanc).
- **Encres.**
  - `{colors.ink}` : texte principal.
  - `{colors.ink-soft}` : texte secondaire, contraste AA.
  - `{colors.gray}` : icônes inactives et décor uniquement.
- **Surfaces.**
  - `{colors.surface}` (blanc) : zones de travail.
  - `{colors.surface-alt}` (gris clair) : colonne de gauche, panneau Sources et zones de saisie.
- **États.** `{colors.warning}` (ambre) et `{colors.danger}` (rouge) colorent uniquement des icônes et des bordures. Le texte reste en `{colors.ink}`.
  - Le **Mode hors ligne est un état normal**, pas une alerte. Sa pastille est grise, jamais rouge ni ambre.

À éviter : magenta, rose, dégradés, toute couleur inventée hors de cette liste.

## Typography

- **Polices.**
  - **Pile système** (`system-ui`, Segoe UI, Roboto) pour tout le texte : aucune police n'est embarquée ni chargée depuis Internet, l'application est hors ligne.
  - Les `{typography.label}` (étiquettes de section en capitales, comme « TÂCHES », « HISTORIQUE » ou « SOURCES ») utilisent la même pile, en graisse 700.
- **Rôles.**
  - `{typography.display}` : écran de bienvenue et en-tête vide d'une Tâche.
  - `{typography.title}` : titres de panneau.
  - `{typography.body}` : réponses et saisie. La taille de 1rem et l'interligne de 1,6 visent une lecture longue.
  - `{typography.small}` : métadonnées, puces de citation, avertissement juridique.
  - `{typography.mono}` : extraits de données tabulaires seulement.
- **Échelle de texte.** Toutes les tailles sont en rem. L'Agent règle l'échelle globale de 100 à 150 % (voir EXPERIENCE.md). La mise en page doit rester utilisable à 150 % dans une fenêtre de 1024×640.

## Layout & Spacing

- **Échelle de base 4.** Valeurs `{spacing.1}` à `{spacing.7}`.
- **Trois colonnes :**
  - colonne de gauche de `{spacing.sidebar-width}` ;
  - zone centrale fluide, dont le contenu textuel est limité à `{spacing.content-max}` ;
  - panneau Sources de `{spacing.sources-width}`, fermé par défaut.
- **Barre supérieure** de `{spacing.topbar-height}` : titre de la Tâche active à gauche, indicateur de Mode à droite.
- **Vue de rédaction.** Deux volets égaux, Entrée et Résultat, séparés par `{spacing.5}`. Sous 1 200 px de large, ils s'empilent verticalement.
- **Fenêtre minimale** de 1024×640. Sous 1 280 px, le panneau Sources recouvre la zone centrale au lieu de la pousser.

## Elevation & Depth

L'interface est presque plate. La hiérarchie vient des surfaces (`{colors.surface}` / `{colors.surface-alt}`) et des bordures `{colors.line}`. Deux éléments seulement portent une ombre, douce (0 8px 24px, à 8 % d'opacité de `{colors.ink}`) :
- le panneau Sources quand il recouvre la zone centrale ;
- les boîtes de dialogue.

## Shapes

- `{rounded.sm}` (8px) : boutons, champs, éléments de navigation.
- `{rounded.md}` (12px) : bulles de message, cartes de source, volets de rédaction.
- `{rounded.lg}` (16px) : boîtes de dialogue.
- `{rounded.full}` : puces de citation et indicateur de Mode.

Ces rayons sont un peu plus serrés que ceux de la charte web (12/16/22), pour un rendu d'outil plutôt que de site.

## Components

Références visuelles : `mockups/question.html` et `mockups/compte-rendu.html`. En cas de conflit, les spines priment. Les maquettes utilisent la même pile système que l'application.

- **Navigation des Tâches** (`task-nav-item`). Liste verticale dans la colonne de gauche.
  - Les quatre Tâches prioritaires sont visibles. Les quatre secondaires sont repliées sous « Plus ».
  - L'élément actif reçoit un fond `{colors.primary-soft}`, un texte `{colors.primary}` et une barre de 3 px à gauche.
  - Chaque Tâche a une icône linéaire de 20 px, sans emoji.
- **Indicateur de Mode** (`mode-indicator-*`). Pastille arrondie dans la barre supérieure, avec un point coloré et un libellé (« Hors ligne » ou « Connecté »).
  - Le point est gris hors ligne, orange en Mode connecté.
  - Le libellé est toujours présent : la couleur seule ne porte jamais l'information.
- **Message** (`message-agent`, `message-assistant`).
  - Message de l'Agent : bulle alignée à droite sur fond bleu pétrole doux.
  - Réponse de l'Assistant : bloc pleine largeur, bordé, avec trois éléments sous le texte :
    - la rangée de puces de citation ;
    - l'avertissement juridique ;
    - les actions Copier, Retour (pouce haut ou bas) et Régénérer.
- **Puce de citation** (`citation-chip`). Numéro + titre court de la source, sur une seule ligne tronquée. Un clic ouvre le panneau Sources sur cette source.
- **Avertissement juridique** (`legal-notice`). Bandeau discret avec une bordure gauche ambre et le texte « Ne vaut pas avis juridique ». Il n'est jamais rouge, car ce n'est pas une erreur.
- **Carte de source** (`source-card`). Elle contient :
  - le titre ;
  - l'origine, libellée sans jargon : « Documents installés », « data.gouv » ou « Page consultée » ;
  - la date (fraîcheur de l'Index local ou date de consultation) ;
  - l'extrait utilisé, dépliable ;
  - un bouton « Ouvrir » vers le lien.
- **Volets de rédaction** (`editor-pane`). Volet Entrée éditable et volet Résultat en lecture seule. La barre d'actions du Résultat contient Copier (bouton principal), Régénérer et Affiner (bouton secondaire).
- **Différences de Correction** (`diff-insert`, `diff-delete`).
  - Insertion : fond orange clair et soulignement.
  - Suppression : texte barré en `{colors.ink-soft}`.
  - Le marquage ne repose jamais sur la seule couleur.
- **Tableau de données** (`data-table`). Grille simple à lignes alternées `{colors.surface-alt}`, en-têtes en `{typography.body-strong}` et pied de tableau sourcé en `{typography.small}`.
- **Zone de saisie** (`composer`). Champ multiligne sur fond `{colors.surface-alt}`, bouton Envoyer (`button-primary`) aligné en bas à droite. Au focus, la bordure passe à 2 px `{colors.focus-ring}`.
- **Carte de jeu de données** (`dataset-card`). Même gabarit que la carte de source : titre en `{typography.body-strong}`, puis une ligne de métadonnées en `{typography.small}` `{colors.ink-soft}` (producteur · date de mise à jour), puis les actions « Ouvrir » et « Voir les données » (`button-secondary`).
- **Encarts d'état** (`callout-warning`, `callout-danger`). Même gabarit que l'avertissement juridique, en texte `{colors.ink}` : bordure gauche ambre pour le repli data.gouv, rouge pour l'erreur interne. Une icône linéaire précède le texte ; l'action « Réessayer » est un `button-secondary`.
- **Passage signalé** (`flagged-passage`, Langage clair). Fond `{colors.surface-alt}` et soulignement pointillé ambre de 2 px. Il se distingue ainsi des insertions de Correction (fond orange clair, soulignement plein).
- **Emplacement de courrier** (`letter-placeholder`, Courrier type). Texte entre crochets en `{colors.primary}` gras sur fond `{colors.primary-soft}`.
- **Boîte de dialogue** (`dialog`). Fond blanc, rayon `{rounded.lg}`, ombre douce, voile d'ink à 32 %. Largeur 640 px au plus, titre en `{typography.title}`, bouton × en haut à droite.
- **Confirmation discrète** (`inline-confirmation`). Texte `{typography.small}` `{colors.ink-soft}` affiché à côté de l'action qui l'a déclenchée (« Copié », « Merci, retour enregistré sur ce poste »), puis effacé après 3 s. Pas de toast flottant.

## Do's and Don'ts

| À faire | À ne pas faire |
|---|---|
| Garder `{colors.primary}` pour l'action principale et la sélection | Multiplier les aplats décoratifs de couleur primaire |
| Réserver l'orange à la pastille du Mode connecté et aux insertions | Mettre du texte orange sur fond clair |
| Traiter le Mode hors ligne comme un état normal (gris) | Afficher « Hors ligne » en rouge ou en ambre |
| Utiliser la pile de polices système | Charger des polices ou des icônes depuis Internet |
| Exprimer toutes les tailles en rem | Fixer des tailles en px qui cassent l'échelle de texte |
| Utiliser des icônes linéaires 24×24 qui héritent de la couleur du texte | Utiliser des emojis ou des illustrations décoratives |
| Garder une interface calme, sans animation au défilement | Reprendre des effets de vitrine (curseur, orbites, compteurs) |
| Rester sobre et neutre | Imiter le DSFR, Marianne ou tout signe de l'État |
