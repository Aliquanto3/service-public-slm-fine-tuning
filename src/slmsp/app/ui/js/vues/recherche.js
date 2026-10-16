// Vue « Recherche de données » (story 12.7) : cartes de jeux de données et tableaux sourcés,
// construits depuis les `ResultatOutil` (jamais depuis le texte de la réponse).

import { monterConversation } from "../composants/conversation.js";

/**
 * @param {HTMLElement} conteneur Élément réservé à la vue.
 * @param {object} pont Client du pont (appeler, envoyer, arreter).
 * @param {{bus: object, tache: string}} contexte
 */
export function monter(conteneur, pont, contexte) {
  monterConversation(conteneur, pont, contexte, {
    titre: "Recherchez des données publiques",
    intro: "Décrivez le sujet : je cherche dans le catalogue data.gouv.fr.",
    juridique: false,
    infoHorsLigne: "Hors ligne : catalogue installé uniquement, sans chiffres à jour.",
  });
}
