---
name: Assistant IA local secteur public (nom de produit à trouver)
description: Assistant IA local et hors ligne pour les agents publics, application de bureau Windows. Identité visuelle Wavestone, adaptée à un outil de travail quotidien plutôt qu'à une page vitrine.
status: final
created: 2026-10-11
updated: 2026-10-11
colors:
  primary: '#451DC7'            # violet Wavestone, ancre de marque
  primary-hover: '#250F6B'      # violet profond, survol et état pressé
  primary-soft: '#EDE7FE'       # violet doux : sélection, survol de ligne, bulle de l'Agent
  on-primary: '#FFFFFF'
  accent: '#04F06A'             # vert Wavestone : seul accent secondaire, jamais en texte sur fond clair
  accent-soft: '#CAFEE0'        # vert clair : fond des états de succès
  ink: '#0A0A14'                # texte principal
  ink-soft: '#4A4A5E'           # texte secondaire (contraste AA sur blanc)
  gray: '#8A8A9E'               # décor, icônes inactives ; jamais pour du texte de moins de 18,66 px
  line: '#E6E6EC'               # bordures, séparateurs
  surface: '#FFFFFF'            # fond des zones de travail
  surface-alt: '#F6F5FA'        # fond de la colonne de gauche, du panneau Sources, des zones d'entrée
  warning: '#FFCA4A'            # jaune : avertissement juridique, mode dégradé (icône et bordure seulement)
  danger: '#FF2A49'             # rouge : erreur (icône et bordure seulement, le texte reste en ink)
  focus-ring: '#451DC7'
typography:
  # Toutes les tailles sont en rem. L'échelle globale (100 à 150 %) agit sur la taille racine.
  display:
    fontFamily: 'Aptos, Inter, Segoe UI, sans-serif'
    fontSize: 1.75rem
    fontWeight: '800'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  title:
    fontFamily: 'Aptos, Inter, Segoe UI, sans-serif'
    fontSize: 1.25rem
    fontWeight: '700'
    lineHeight: '1.3'
    letterSpacing: -0.01em
  body:
    fontFamily: 'Aptos, Inter, Segoe UI, sans-serif'
    fontSize: 1rem
    fontWeight: '400'
    lineHeight: '1.6'
  body-strong:
    fontFamily: 'Aptos, Inter, Segoe UI, sans-serif'
    fontSize: 1rem
    fontWeight: '600'
    lineHeight: '1.6'
  small:
    fontFamily: 'Aptos, Inter, Segoe UI, sans-serif'
    fontSize: 0.875rem
    fontWeight: '400'
    lineHeight: '1.5'
  label:
    fontFamily: 'Manrope, Inter, sans-serif'
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
    shadow: '0 8px 24px rgba(10,10,20,0.08)'
    scrim: 'rgba(10,10,20,0.32)'
  inline-confirmation:
    foreground: '{colors.ink-soft}'
    typography: '{typography.small}'
---

## Brand & Style

L'Assistant reprend l'identité Wavestone, transposée d'une page vitrine à un **outil de travail quotidien**. La marque se reconnaît au violet `{colors.primary}`, au rythme typographique serré des titres et aux étiquettes en Manrope capitales. Les effets de vitrine de la charte web sont exclus : animations au défilement, curseur personnalisé, compteurs animés, visuels en orbite. Un agent d'accueil l'ouvre vingt fois par jour, devant un usager. L'interface doit être calme, lisible et prévisible.

Posture : **sobre, digne de confiance, jamais officielle**. L'Assistant n'imite ni le Système de design de l'État (DSFR) ni la marque Marianne. Rien ne doit laisser croire à un outil de l'État.

Le logo Wavestone est placé en bas de la colonne de gauche, en petit, avec la mention du nom de produit. `[ASSUMPTION : nom et marquage définitifs à trancher lors du brainstorm « Wave… » ; à vérifier si la démo est montrée chez un client qui ne doit pas voir la marque]`

## Colors

- **Violet `{colors.primary}`.** C'est l'ancre de marque. Il sert aux actions principales, à la Tâche active, aux puces de citation, aux liens et à l'anneau de focus. Contraste d'environ 9:1 sur blanc, donc utilisable en texte.
- **Violet profond `{colors.primary-hover}`.** Réservé au survol et à l'état pressé des actions violettes.
- **Violet doux `{colors.primary-soft}`.** Sert de fond pour la sélection, la bulle de l'Agent et les puces de citation. Jamais en grand aplat décoratif.
- **Vert `{colors.accent}`.** Seul accent secondaire, avec deux usages : la pastille du Mode connecté et le fond des insertions en Correction (`{colors.accent-soft}`).
  - Il n'est **jamais utilisé en texte sur fond clair**, car son contraste est insuffisant.
- **Encres.**
  - `{colors.ink}` : texte principal.
  - `{colors.ink-soft}` : texte secondaire, contraste AA.
  - `{colors.gray}` : icônes inactives et décor uniquement.
- **Surfaces.**
  - `{colors.surface}` (blanc) : zones de travail.
  - `{colors.surface-alt}` (crème) : colonne de gauche, panneau Sources et zones de saisie.
- **États.** `{colors.warning}` (jaune) et `{colors.danger}` (rouge) colorent uniquement des icônes et des bordures. Le texte reste en `{colors.ink}`.
  - Le **Mode hors ligne est un état normal**, pas une alerte. Sa pastille est grise, jamais rouge ni jaune.

À éviter : magenta, rose, dégradés non violets, toute couleur inventée hors de cette liste.

## Typography

- **Polices.**
  - **Aptos** est la police de la marque, présente sur les postes Windows équipés de Microsoft 365.
  - **Inter**, embarquée dans l'application, sert de repli. Aucune police n'est chargée depuis Internet : l'application est hors ligne.
  - **Manrope**, également embarquée, est réservée aux `{typography.label}` : étiquettes de section en capitales, comme « TÂCHES », « HISTORIQUE » ou « SOURCES ».
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

Références visuelles : `mockups/question.html` et `mockups/compte-rendu.html`. En cas de conflit, les spines priment. Les maquettes chargent Inter et Manrope depuis Google Fonts, alors que l'application les embarque.

- **Navigation des Tâches** (`task-nav-item`). Liste verticale dans la colonne de gauche.
  - Les quatre Tâches prioritaires sont visibles. Les quatre secondaires sont repliées sous « Plus ».
  - L'élément actif reçoit un fond `{colors.primary-soft}`, un texte `{colors.primary}` et une barre de 3 px à gauche.
  - Chaque Tâche a une icône linéaire de 20 px, sans emoji.
- **Indicateur de Mode** (`mode-indicator-*`). Pastille arrondie dans la barre supérieure, avec un point coloré et un libellé (« Hors ligne » ou « Connecté »).
  - Le point est gris hors ligne, vert en Mode connecté.
  - Le libellé est toujours présent : la couleur seule ne porte jamais l'information.
- **Message** (`message-agent`, `message-assistant`).
  - Message de l'Agent : bulle alignée à droite sur fond violet doux.
  - Réponse de l'Assistant : bloc pleine largeur, bordé, avec trois éléments sous le texte :
    - la rangée de puces de citation ;
    - l'avertissement juridique ;
    - les actions Copier, Retour (pouce haut ou bas) et Régénérer.
- **Puce de citation** (`citation-chip`). Numéro + titre court de la source, sur une seule ligne tronquée. Un clic ouvre le panneau Sources sur cette source.
- **Avertissement juridique** (`legal-notice`). Bandeau discret avec une bordure gauche jaune et le texte « Ne vaut pas avis juridique ». Il n'est jamais rouge, car ce n'est pas une erreur.
- **Carte de source** (`source-card`). Elle contient :
  - le titre ;
  - l'origine, libellée sans jargon : « Documents installés », « data.gouv » ou « Page consultée » ;
  - la date (fraîcheur de l'Index local ou date de consultation) ;
  - l'extrait utilisé, dépliable ;
  - un bouton « Ouvrir » vers le lien.
- **Volets de rédaction** (`editor-pane`). Volet Entrée éditable et volet Résultat en lecture seule. La barre d'actions du Résultat contient Copier (bouton principal), Régénérer et Affiner (bouton secondaire).
- **Différences de Correction** (`diff-insert`, `diff-delete`).
  - Insertion : fond vert clair et soulignement.
  - Suppression : texte barré en `{colors.ink-soft}`.
  - Le marquage ne repose jamais sur la seule couleur.
- **Tableau de données** (`data-table`). Grille simple à lignes alternées `{colors.surface-alt}`, en-têtes en `{typography.body-strong}` et pied de tableau sourcé en `{typography.small}`.
- **Zone de saisie** (`composer`). Champ multiligne sur fond `{colors.surface-alt}`, bouton Envoyer (`button-primary`) aligné en bas à droite. Au focus, la bordure passe à 2 px `{colors.focus-ring}`.
- **Carte de jeu de données** (`dataset-card`). Même gabarit que la carte de source : titre en `{typography.body-strong}`, puis une ligne de métadonnées en `{typography.small}` `{colors.ink-soft}` (producteur · date de mise à jour), puis les actions « Ouvrir » et « Voir les données » (`button-secondary`).
- **Encarts d'état** (`callout-warning`, `callout-danger`). Même gabarit que l'avertissement juridique, en texte `{colors.ink}` : bordure gauche jaune pour le repli data.gouv, rouge pour l'erreur interne. Une icône linéaire précède le texte ; l'action « Réessayer » est un `button-secondary`.
- **Passage signalé** (`flagged-passage`, Langage clair). Fond `{colors.surface-alt}` et soulignement pointillé jaune de 2 px. Il se distingue ainsi des insertions de Correction (fond vert, soulignement plein).
- **Emplacement de courrier** (`letter-placeholder`, Courrier type). Texte entre crochets en `{colors.primary}` gras sur fond `{colors.primary-soft}`.
- **Boîte de dialogue** (`dialog`). Fond blanc, rayon `{rounded.lg}`, ombre douce, voile d'ink à 32 %. Largeur 640 px au plus, titre en `{typography.title}`, bouton × en haut à droite.
- **Confirmation discrète** (`inline-confirmation`). Texte `{typography.small}` `{colors.ink-soft}` affiché à côté de l'action qui l'a déclenchée (« Copié », « Merci, retour enregistré sur ce poste »), puis effacé après 3 s. Pas de toast flottant.

## Do's and Don'ts

| À faire | À ne pas faire |
|---|---|
| Garder `{colors.primary}` pour l'action principale et la sélection | Multiplier les aplats violets décoratifs |
| Réserver le vert à la pastille du Mode connecté et aux insertions | Mettre du texte vert sur fond clair |
| Traiter le Mode hors ligne comme un état normal (gris) | Afficher « Hors ligne » en rouge ou en jaune |
| Embarquer Inter et Manrope dans l'application | Charger des polices ou des icônes depuis Internet |
| Exprimer toutes les tailles en rem | Fixer des tailles en px qui cassent l'échelle de texte |
| Utiliser des icônes linéaires 24×24 qui héritent de la couleur du texte | Utiliser des emojis ou des illustrations décoratives |
| Garder une interface calme, sans animation au défilement | Reprendre les effets de la charte web (curseur, orbites, compteurs) |
| Rester sobre et neutre | Imiter le DSFR, Marianne ou tout signe de l'État |
