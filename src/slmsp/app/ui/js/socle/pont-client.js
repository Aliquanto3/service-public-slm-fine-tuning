// Client du pont : appelle les méthodes Python (pywebview `js_api`) et reçoit les évènements.
// L'interface ne parle qu'à ce module ; les évènements arrivent par `window.slmspRecevoir(lot)`,
// que Python appelle via `evaluate_js` (format `core.evenements.vers_dict`, plus `{type: "pret"}`).

// File d'attente : les évènements reçus avant le branchement du bus sont conservés dans l'ordre.
const file = [];
let sortie = null;

window.slmspRecevoir = (lot) => {
  for (const evenement of Array.isArray(lot) ? lot : [lot]) {
    if (sortie) sortie(evenement);
    else file.push(evenement);
  }
};

/** Branche le consommateur des évènements et lui rejoue la file. */
export function brancherReception(fonction) {
  sortie = fonction;
  while (file.length) fonction(file.shift());
}

/** Mémoire locale de l'interface (taille du texte, bienvenue, « Plus ») ; tolère son absence. */
export const memoire = {
  lire(cle, defaut = null) {
    try {
      const valeur = window.localStorage.getItem(`slmsp.${cle}`);
      return valeur === null ? defaut : JSON.parse(valeur);
    } catch {
      return defaut;
    }
  },
  ecrire(cle, valeur) {
    try {
      window.localStorage.setItem(`slmsp.${cle}`, JSON.stringify(valeur));
    } catch {
      /* stockage indisponible : l'interface fonctionne sans */
    }
  },
};

function attendrePywebview() {
  if (window.pywebview?.api) return Promise.resolve(window.pywebview.api);
  return new Promise((resolu) => {
    window.addEventListener("pywebviewready", () => resolu(window.pywebview.api), { once: true });
  });
}

/**
 * Ouvre le pont : factice si `?pont=factice`, sinon pywebview (attente indéfinie : tant que le pont
 * n'est pas là, l'interface reste dans l'état « Préparation… »).
 */
export async function ouvrirPont(bus) {
  const params = new URLSearchParams(window.location.search);
  let moteur;
  if (params.get("pont") === "factice") {
    const { creerPontFactice } = await import("./pont-factice.js");
    moteur = creerPontFactice(window.slmspRecevoir, params);
  } else {
    moteur = await attendrePywebview();
  }
  return {
    factice: Boolean(moteur.factice),
    /** Appel générique d'une méthode du pont (contrat fixé par la story 12.5). */
    appeler: (nom, ...args) => moteur.appeler?.(nom, ...args) ?? moteur[nom](...args),
    envoyer(tache, messages, options = {}) {
      bus.emettre("generation:debut", { tache });
      return moteur.envoyer(tache, messages, options);
    },
    arreter: () => moteur.arreter(),
  };
}
