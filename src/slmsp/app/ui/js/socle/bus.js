// Bus d'évènements interne de l'interface : abonnements par type, sans dépendance.

const abonnes = new Map();

/** S'abonne à un type ; renvoie la fonction de désabonnement. */
export function abonner(type, fonction) {
  if (!abonnes.has(type)) abonnes.set(type, new Set());
  abonnes.get(type).add(fonction);
  return () => abonnes.get(type)?.delete(fonction);
}

/** Émet un évènement ; une erreur d'un abonné n'empêche pas les suivants. */
export function emettre(type, charge) {
  for (const fonction of [...(abonnes.get(type) ?? [])]) {
    try {
      fonction(charge);
    } catch (erreur) {
      console.error(`bus : abonné de « ${type} » en échec`, erreur);
    }
  }
}
