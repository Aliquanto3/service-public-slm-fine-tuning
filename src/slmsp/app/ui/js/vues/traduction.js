// Vue « traduction » : module vide déclaré d'avance (story 12.4).
// La story de la vue remplace ce fichier et css/traduction.css, sans toucher à index.html.

/**
 * Monte la vue dans son conteneur.
 * @param {HTMLElement} conteneur Élément réservé à la vue.
 * @param {object} pont Client du pont (appeler, envoyer, arreter).
 * @param {object} [contexte] `{ bus, tache }` : bus d'évènements et Tâche servie par ce conteneur.
 */
export function monter(conteneur, pont, contexte) {
  const p = document.createElement("p");
  p.className = "non-disponible";
  p.textContent = "non disponible";
  conteneur.replaceChildren(p);
}
