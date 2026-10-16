// Raccourcis clavier globaux (UX-DR20). Entrée et Maj+Entrée sont gérés par la zone de saisie.

/** Crans de la taille du texte, en pourcentage (EXPERIENCE.md, « Taille du texte »). */
export const CRANS_TAILLE = [100, 112, 125, 137, 150];

/**
 * Installe les raccourcis.
 * @param {object} actions `prioritaire(i)`, `nouvelle()`, `copier()`, `taille(delta|0)`, `echap(evenement)`.
 */
export function installerClavier(actions) {
  document.addEventListener("keydown", (e) => {
    if (e.defaultPrevented) return;
    if (e.ctrlKey && !e.altKey && !e.metaKey) {
      const touche = e.key.length === 1 ? e.key.toLowerCase() : e.key;
      // Chiffres lus par `e.code` (position physique) : en AZERTY, Ctrl+1 donne `e.key === "&"`.
      const chiffre = /^(Digit|Numpad)([0-9])$/.exec(e.code ?? "")?.[2] ?? (/^[0-9]$/.test(touche) ? touche : null);
      if (!e.shiftKey && chiffre !== null && chiffre >= "1" && chiffre <= "4") {
        e.preventDefault();
        actions.prioritaire(Number(chiffre) - 1);
      } else if (!e.shiftKey && touche === "n") {
        e.preventDefault();
        actions.nouvelle();
      } else if (e.shiftKey && touche === "c") {
        e.preventDefault();
        actions.copier();
      } else if (touche === "+" || touche === "=") {
        e.preventDefault();
        actions.taille(1);
      } else if (touche === "-") {
        e.preventDefault();
        actions.taille(-1);
      } else if (!e.shiftKey && chiffre === "0") {
        e.preventDefault();
        actions.taille(0);
      }
    } else if (e.key === "Escape") {
      actions.echap(e);
    }
  });
}
