// Carte de jeu de données (`dataset-card`) : titre, producteur · date de mise à jour, « Ouvrir »,
// « Voir les données » (Mode connecté seulement). Les cartes viennent d'un `ResultatOutil`.

import { confirmer, dateLisible } from "./copie.js";
import { creerLienOuvrir, urlOuvrable } from "./sources.js";
import { creerTableau, extraireTableau, texteDuResultat } from "./tableau.js";

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
 * @param {object} deps `{ pont, horsLigne }` ; « Voir les données » appelle `pont.appeler("voir_donnees", id)`
 *   et attend `{resultat}` (un `ResultatOutil.resultat` tabulaire).
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
  if (jeu.url && urlOuvrable(jeu.url)) actions.append(creerLienOuvrir(jeu.url, horsLigne));
  const dessous = document.createElement("div");
  dessous.className = "dataset-donnees";
  if (jeu.id) {
    const voir = document.createElement("button");
    voir.type = "button";
    voir.className = "bouton-secondaire voir-donnees"; // masqué hors ligne par la feuille de style
    voir.textContent = "Voir les données";
    voir.addEventListener("click", async () => {
      voir.disabled = true;
      dessous.setAttribute("aria-busy", "true");
      let tableau = null;
      try {
        const reponse = await pont.appeler("voir_donnees", jeu.id);
        tableau = extraireTableau(reponse?.resultat ?? null);
      } catch {
        tableau = null;
      }
      dessous.removeAttribute("aria-busy");
      voir.disabled = false;
      if (tableau) dessous.replaceChildren(creerTableau(tableau));
      else confirmer(actions, "Les données ne sont pas disponibles pour le moment.", 6000);
    });
    actions.append(voir);
  }
  carte.append(titre, meta, actions, dessous);
  return carte;
}
