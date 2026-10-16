// Vue « Question » (story 12.7) : réponse au fil de l'eau, puces de citation, panneau Sources.

import { monterConversation } from "../composants/conversation.js";

// Textes d'interface de l'écran « Question vide » (UX-DR19). Ce ne sont pas des données
// d'entraînement (D1). Le premier vient d'EXPERIENCE.md ; les deux autres sont des emplacements
// à faire valider par Anaël (voir la section « À confirmer » de la spec 12.7).
export const EXEMPLES = [
  "Quelles pièces pour une demande d'APA ?",
  "<exemple-à-valider-2>",
  "<exemple-à-valider-3>",
];

/**
 * @param {HTMLElement} conteneur Élément réservé à la vue.
 * @param {object} pont Client du pont (appeler, envoyer, arreter).
 * @param {{bus: object, tache: string}} contexte
 */
export function monter(conteneur, pont, contexte) {
  monterConversation(conteneur, pont, contexte, {
    titre: "Posez votre question",
    intro: "Je réponds à partir des documents officiels et je cite mes sources.",
    exemples: EXEMPLES,
    juridique: true,
  });
}
