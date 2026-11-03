# Journal des modifications

## 0.3.2

- Charte graphique générique : bleu pétrole `#0B6B78` (primaire), orange brûlé `#B4500F` (accent), ambre `#E8A317` (avertissement), rouge `#B42318` (erreur), anneau de focus bleu `#1F5FD1`, encre `#141A1F`. Les jetons de `jetons.css`, le `DESIGN.md` de l'UX et les maquettes sont alignés ; les contrastes WCAG AA sont vérifiés par `tests/app/ui/test_socle_statique.py`.
- Polices : pile système (`system-ui`, Segoe UI, Roboto). Plus de police chargée depuis Internet dans les maquettes.
- Logotype : pictogramme à trois barres et nom en texte, à la place de l'ancien logo des maquettes.
- Retrait des mentions de l'ancienne charte et des informations internes dans la documentation de conception (`_bmad-output`).
- Le nom du dépôt, le paquet `slmsp`, la commande et les variables d'environnement ne changent pas.
- La capture de démonstration `docs/assets/demo-assistant.gif` montre encore l'ancienne palette : à régénérer avec `outils/capturer_demo.py` (elle lit des résultats de génération non suivis par git).
