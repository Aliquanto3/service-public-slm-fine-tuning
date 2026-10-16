// Carte de jeu de données (`dataset-card`) : titre, producteur · date de mise à jour, « Ouvrir ».
// Les cartes viennent d'un `ResultatOutil`. « Voir les données » n'est pas affiché : le pont 12.5
// n'expose aucune méthode pour lire les lignes d'un jeu (décision de revue 12.7). Les tableaux
// arrivent par les `ResultatOutil` tabulaires de la réponse (`tableau.js`).

import { dateLisible } from "./copie.js";
import { creerLienOuvrir, urlOuvrable } from "./sources.js";
import { texteDuResultat } from "./tableau.js";

const CHAMPS_DATE = ["Last update", "Last modified", "Updated", "Date"];

/** Renvoie la liste `[{id, titre, producteur, date, url}]` d'un résultat de recherche, ou `[]`. */
export function extraireJeux(resultat) {
  if (resultat && typeof resultat === "object" && Array.isArray(resultat.jeux)) {
    return resultat.jeux.filter((j) => j && j.titre).map((j) => ({ ...j }));
  }
  const texte = texteDuResultat(resultat);
  if (!/^Found \d+ dataset/m.test(texte)) return [];
  const jeux = [];
  let courant = null;
  for (const ligne of texte.split("\n")) {
    const debut = /^\d+\. (.+)$/.exec(ligne);
    if (debut) {
      courant = { titre: debut[1].trim(), id: null, producteur: null, date: null, url: null };
      jeux.push(courant);
      continue;
    }
    const champ = courant && /^\s+([A-Za-z ]+): (.*)$/.exec(ligne);
    if (!champ) continue;
    const [, cle, valeur] = champ;
    if (cle === "ID") courant.id = valeur.trim();
    else if (cle === "Organization") courant.producteur = valeur.trim();
    else if (cle === "URL") courant.url = valeur.trim();
    else if (CHAMPS_DATE.includes(cle)) courant.date = valeur.trim();
  }
  return jeux;
}

/**
 * Construit la carte d'un jeu.
 * @param {object} deps `{ pont, horsLigne }` (bouton « Ouvrir »).
 */
export function creerCarteJeu(jeu, { pont, horsLigne }) {
  const carte = document.createElement("article");
  carte.className = "dataset-card";
  const titre = document.createElement("h3");
  titre.textContent = jeu.titre;
  const meta = document.createElement("p");
  meta.className = "dataset-meta";
  meta.textContent = [jeu.producteur, jeu.date ? `mis à jour le ${dateLisible(jeu.date)}` : null]
    .filter(Boolean)
    .join(" · ");
  meta.hidden = !meta.textContent;
  const actions = document.createElement("div");
  actions.className = "dataset-actions";
  if (jeu.url && urlOuvrable(jeu.url)) actions.append(creerLienOuvrir(jeu.url, horsLigne, pont));
  carte.append(titre, meta, actions);
  return carte;
}
