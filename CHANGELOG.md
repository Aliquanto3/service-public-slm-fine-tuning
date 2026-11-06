# Journal des modifications

## 0.4.0

Contenu

- Interface migrée vers la charte générique v2.1 : sombre par défaut, clair selon la préférence du système (ou `[data-theme="light"]`). Les jetons de `jetons.css` portent les noms de la charte (`fond`, `texte`, `primaire`, `bouton`, `trait-fort`, `focus`…) et sont choisis par usage dans chaque feuille de style.
- Bouton principal neutre (`bouton` / `sur-bouton`), bouton secondaire en contour `trait-fort`, focus `focus`. Le bleu n'est plus un aplat de bouton, ni au survol (puce de citation : liseré et soulignement).
- Polices servies localement (`src/slmsp/app/ui/charte/polices/`, licences OFL jointes) : Sora 600 pour les titres, Atkinson Hyperlegible pour le texte, JetBrains Mono pour le code. Favicon de la charte, pictogramme en ligne dans la marque, filet or sous le titre de l'accueil.
- Icônes SVG en `currentColor` ; points de mode et liserés d'alerte en `alerte-texte` ; infobulle en `encre-pleine`.
- Gabarit `outils/audit_verdicts.gabarit.html` : jetons v2.1, sombre d'abord, bouton actif neutre.
- Tests : `tests/app/ui/test_charte.py` (empreinte des jetons, contrastes dans les deux thèmes, bouton neutre, aucun hex hors des jetons, polices, gabarit) ; les anciens contrôles de contraste de `test_socle_statique.py` y sont repris.
- README : capture fixe (clair et sombre) à côté du GIF, dans `docs/media/charte-v2/`.

Limites

- `docs/assets/demo-assistant.gif` montre encore l'ancienne palette : à refaire avec `outils/capturer_demo.py` (il lit des résultats de génération non suivis par git).
- Pas de sélecteur de thème dans l'interface : le thème suit le système.
- Historique non migré : `_bmad/`, `_bmad-output/` (maquettes, `DESIGN.md`), notes de version précédentes de ce fichier.
- Le gabarit d'audit est un fichier autonome : les polices de la charte y figurent dans la pile de repli, sans fichier embarqué.
- Captures réalisées avec le pont factice (`?pont=factice`), sans modèle : seul l'écran d'accueil est montré.

## 0.3.2

- Charte graphique générique : bleu pétrole `#0B6B78` (primaire), orange brûlé `#B4500F` (accent), ambre `#E8A317` (avertissement), rouge `#B42318` (erreur), anneau de focus bleu `#1F5FD1`, encre `#141A1F`. Les jetons de `jetons.css`, le `DESIGN.md` de l'UX et les maquettes sont alignés ; les contrastes WCAG AA sont vérifiés par `tests/app/ui/test_socle_statique.py`.
- Polices : pile système (`system-ui`, Segoe UI, Roboto). Plus de police chargée depuis Internet dans les maquettes.
- Logotype : pictogramme à trois barres et nom en texte, à la place de l'ancien logo des maquettes.
- Retrait des mentions de l'ancienne charte et des informations internes dans la documentation de conception (`_bmad-output`).
- Le nom du dépôt, le paquet `slmsp`, la commande et les variables d'environnement ne changent pas.
- La capture de démonstration `docs/assets/demo-assistant.gif` montre encore l'ancienne palette : à régénérer avec `outils/capturer_demo.py` (elle lit des résultats de génération non suivis par git).
