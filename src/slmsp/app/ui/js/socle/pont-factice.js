// Pont factice : permet d'ouvrir l'interface dans un navigateur sans Python (`?pont=factice`).
// Toutes les chaînes sont des valeurs factices manifestes, jamais du contenu réaliste.

/**
 * @param {(lot: object|object[]) => void} recevoir Point d'entrée des évènements.
 * @param {URLSearchParams} params `pret=0` : le pont ne signale jamais `pret`.
 */
export function creerPontFactice(recevoir, params) {
  if (params.get("pret") !== "0") setTimeout(() => recevoir({ type: "pret" }), 30);
  const fin = (raison) => ({ type: "fin", raison, usage: null, urls_inventees: [] });
  return {
    factice: true,
    async envoyer() {
      setTimeout(() => recevoir([{ type: "jeton", texte: "<réponse-factice-1>" }, fin("terminee")]), 30);
      return { ok: true };
    },
    async arreter() {
      recevoir(fin("interrompue"));
      return { ok: true };
    },
    async appeler(nom) {
      return { ok: true, factice: true, methode: nom };
    },
  };
}
