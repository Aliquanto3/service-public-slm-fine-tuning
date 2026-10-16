// Zone de saisie (`composer`, UX-DR4) : Entrée envoie, Maj+Entrée passe à la ligne, Envoyer inactif
// si vide, « Préparation… » tant que le pont n'a pas signalé `pret`, « Arrêter » pendant la génération.

/**
 * @param {object} deps `{ bus, getPont, etat }` : `etat` porte `tache`, `pret`, `generation`.
 */
export function monterComposer({ bus, getPont, etat }) {
  const formulaire = document.getElementById("composer");
  const saisie = document.getElementById("saisie");
  const bouton = document.getElementById("envoyer");
  const brouillons = new Map(); // travail conservé par Tâche pendant la session (UX-DR3)
  let dernier = null;

  function rafraichir() {
    if (etat.generation) {
      bouton.textContent = "Arrêter";
      bouton.disabled = false;
    } else if (!etat.pret) {
      bouton.textContent = "Préparation…";
      bouton.disabled = true;
    } else {
      bouton.textContent = "Envoyer";
      bouton.disabled = saisie.value.trim() === "";
    }
  }

  function envoyerSaisie(texte = saisie.value) {
    if (etat.generation || !etat.pret || texte.trim() === "") return;
    dernier = { tache: etat.tache, texte };
    saisie.value = "";
    brouillons.delete(etat.tache);
    bus.emettre("envoi", dernier);
    appelSur(() => getPont().envoyer(dernier.tache, [{ role: "user", content: texte }], {}));
    rafraichir();
  }

  /** Un appel au pont qui échoue (rejet ou exception) devient `generation:erreur` : rien n'est perdu. */
  function appelSur(appel) {
    Promise.resolve()
      .then(appel)
      .catch(() => bus.emettre("generation:erreur", { tache: etat.tache }));
  }

  formulaire.addEventListener("submit", (e) => {
    e.preventDefault();
    if (etat.generation) appelSur(() => getPont().arreter());
    else envoyerSaisie();
  });
  saisie.addEventListener("input", rafraichir);
  saisie.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey && !e.ctrlKey && !e.altKey && !e.isComposing) {
      e.preventDefault();
      envoyerSaisie();
    }
  });

  return {
    rafraichir,
    /** Change de Tâche : sauve le brouillon de l'ancienne, restaure celui de la nouvelle. */
    changerTache(ancienne, nouvelle) {
      if (ancienne) brouillons.set(ancienne, saisie.value);
      saisie.value = brouillons.get(nouvelle) ?? "";
      rafraichir();
    },
    vider() {
      saisie.value = "";
      brouillons.delete(etat.tache);
      rafraichir();
    },
    /** Après une erreur interne : le texte envoyé est remis dans le champ s'il est vide. */
    restaurer() {
      if (dernier && saisie.value === "") saisie.value = dernier.texte;
      rafraichir();
    },
    reessayer() {
      if (dernier) envoyerSaisie(dernier.texte);
    },
    focus: () => saisie.focus(),
  };
}
