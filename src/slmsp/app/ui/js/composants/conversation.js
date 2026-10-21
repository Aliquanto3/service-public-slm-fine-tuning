// Fil de conversation partagé par les vues Question et Recherche de données (story 12.7).
// Il consomme les évènements du bus (`evenement:<type>` : format `core.evenements.vers_dict`),
// tient le panneau Sources du socle et l'écran vide.

import { creerReponse } from "./reponse.js";
import { confirmer, copierTexte } from "./copie.js";
import { rendrePanneauSources } from "./sources.js";
import { creerVerification } from "../vues/verification.js";

function el(balise, classe, texte) {
  const e = document.createElement(balise);
  if (classe) e.className = classe;
  if (texte !== undefined) e.textContent = texte;
  return e;
}

/**
 * Lit un état de Mode : `true` hors ligne, `false` connecté, `null` si inconnu.
 * Formes reconnues : `mode.etat()` du pont 12.5 (`{ok, mode: "connecte"|"hors_ligne"}`) et
 * l'évènement de bus `mode:change` (`{hors_ligne: bool}`). Un refus (`ok: false`) est inconnu.
 */
export function lireMode(charge) {
  if (!charge || charge.ok === false) return null;
  if (typeof charge.hors_ligne === "boolean") return charge.hors_ligne;
  if (charge.mode === "hors_ligne") return true;
  if (charge.mode === "connecte") return false;
  return null;
}

/** Contrat 12.5 : un refus du pont (`{ok: false, erreur}`) devient un rejet. */
function exigerOk(reponse) {
  if (reponse && reponse.ok === false) {
    throw Object.assign(new Error(reponse.erreur?.message ?? "refus du pont"), { erreur: reponse.erreur });
  }
  return reponse;
}

/**
 * @param {HTMLElement} conteneur Conteneur de la vue.
 * @param {object} pont Client du pont.
 * @param {{bus: object, tache: string}} contexte
 * @param {object} options `titre`, `intro`, `exemples` (textes d'interface), `juridique` (bool),
 *   `infoHorsLigne` (texte affiché sous le titre en Mode hors ligne, ou absent), `verification`
 *   (bouton « Vérifier en ligne » sous les réponses, story 13.6).
 */
export function monterConversation(conteneur, pont, { bus, tache }, options) {
  const mode = { horsLigne: true }; // Mode hors ligne par défaut (EXPERIENCE.md)
  const horsLigne = () => mode.horsLigne;
  const racine = el("div", "conversation");
  racine.dataset.mode = "hors-ligne";

  const info = el("p", "info-mode", options.infoHorsLigne ?? "");
  info.setAttribute("role", "status");
  info.hidden = true;

  const vide = el("section", "vide");
  vide.setAttribute("aria-labelledby", `vide-titre-${tache}`);
  const titre = el("h2", null, options.titre);
  titre.id = `vide-titre-${tache}`;
  vide.append(titre);
  if (options.intro) vide.append(el("p", "vide-intro", options.intro));
  if (options.exemples?.length) {
    const liste = el("ul", "exemples");
    for (const [i, exemple] of options.exemples.entries()) {
      const item = document.createElement("li");
      const bouton = el("button", "exemple", exemple);
      bouton.type = "button";
      bouton.id = `exemple-${tache}-${i + 1}`;
      bouton.addEventListener("click", () => {
        const saisie = document.getElementById("saisie");
        if (!saisie) return;
        saisie.value = exemple; // l'Agent relit et envoie : rien ne part sans son geste
        saisie.dispatchEvent(new Event("input", { bubbles: true }));
        saisie.focus();
      });
      item.append(bouton);
      liste.append(item);
    }
    vide.append(liste);
  }

  const fil = el("ol", "fil");
  fil.setAttribute("aria-label", "Conversation");
  racine.append(info, vide, fil);
  conteneur.replaceChildren(racine);

  // { reponse, element, question, fin } ; `fin` : null pendant la génération, sinon la raison
  // de fin (`terminee`, `interrompue`, `longueur`…) ou `echec`.
  const tours = [];
  let enCours = false; // une génération de cette vue est en cours
  let remplacement = null; // réponse à remplacer sur place, vidée au premier évènement reçu
  let actif = !conteneur.hidden && !conteneur.closest("[hidden]");
  let selection = null; // { reponse, numero }

  const derniere = () => tours.at(-1)?.reponse ?? null;
  const tourDe = (r) => tours.find((t) => t.reponse === r) ?? null;

  /**
   * Modèle explicite des tours (question → réponse) publié sur le bus (`conversation:tours`) pour
   * l'Historique (story 12.11), qui enregistre la conversation sans suivre lui-même les évènements.
   * `origine` : `fin` (une réponse vient de se terminer) ou `rouverture`.
   */
  function publierTours(origine) {
    bus.emettre("conversation:tours", {
      tache,
      origine,
      tours: tours.map((t) => ({
        question: t.question,
        texte: t.reponse.brut,
        // La page « Vérifiée en ligne » (13.6) reste dans le panneau, hors de l'Historique.
        sources: t.reponse.sources.filter((s) => s.origine !== "verification"),
        fin: t.fin,
        modele: t.modele ?? null,
        element: t.reponse.el,
      })),
    });
  }

  function rafraichirPanneau() {
    if (!actif) return;
    const choisie = selection && tours.some((t) => t.reponse === selection.reponse) ? selection : null;
    const reponse = choisie?.reponse ?? [...tours].reverse().find((t) => t.reponse.sources.length)?.reponse;
    const corps = document.getElementById("sources-corps");
    if (!reponse || !reponse.sources.length) {
      corps?.replaceChildren();
      bus.emettre("sources:disponibles", false);
      return;
    }
    if (corps) rendrePanneauSources(corps, reponse.sources, { horsLigne, pont, numero: choisie?.numero ?? null });
    bus.emettre("sources:disponibles", true);
  }

  function majBoutons() {
    // Régénérer et Réessayer ne portent que sur la dernière réponse, qui a une question à rejouer.
    for (const t of tours) {
      const relancable = t.reponse === derniere() && t.question != null;
      t.reponse.regenerer.hidden = !relancable;
      t.reponse.reessayer.hidden = !relancable;
    }
    vide.hidden = tours.length > 0;
    majVerifications();
  }

  /** Le bouton « Vérifier en ligne » n'existe que Connecté, sur une réponse terminée (13.6). */
  function majVerifications() {
    for (const t of tours) t.verif?.rafraichir();
  }

  function creerTour(question) {
    const element = el("li", "tour");
    if (question != null) {
      const q = el("p", "message-utilisateur", question);
      element.append(q);
    }
    const reponse = creerReponse({
      pont,
      horsLigne,
      juridique: options.juridique,
      surPuce(r, numero) {
        selection = { reponse: r, numero };
        rafraichirPanneau();
        bus.emettre("sources:ouvrir");
      },
      surRegenerer: relancer,
      surReessayer: relancer,
      surReessayerLocal: () => relancer({ forcer_local: true }),
    });
    element.append(reponse.el);
    const verif = options.verification
      ? creerVerification({
          reponse,
          pont,
          horsLigne,
          eligible: () => {
            const fin = tourDe(reponse)?.fin;
            return fin != null && fin !== "echec" && fin !== "interrompue";
          },
          surSources: rafraichirPanneau, // la page vérifiée n'est pas enregistrée dans l'Historique
        })
      : null;
    if (verif) element.append(verif.el);
    fil.append(element);
    tours.push({ reponse, element, question, fin: null, verif });
    majBoutons();
    return reponse;
  }

  /**
   * Régénérer et Réessayer : renvoie la question du dernier tour par `envoyer` (même Tâche) et
   * remplace sa réponse sur place. `pont.regenerer()` n'est pas utilisé : il rejoue le dernier
   * envoi du pont, qui peut venir d'une autre Tâche. La réponse n'est vidée qu'au premier
   * évènement : un refus du pont la laisse intacte.
   */
  function relancer(optionsEnvoi = {}) {
    const tour = tours.at(-1);
    if (enCours || !tour || tour.question == null) return;
    remplacement = tour.reponse;
    Promise.resolve()
      .then(() => pont.envoyer(tache, [{ role: "user", content: tour.question }], optionsEnvoi))
      .then(exigerOk)
      .catch(() => bus.emettre("generation:erreur", { tache }));
  }

  function appliquerMode(hors) {
    mode.horsLigne = hors;
    racine.dataset.mode = hors ? "hors-ligne" : "connecte";
    info.hidden = !(hors && options.infoHorsLigne);
    majVerifications();
    rafraichirPanneau();
  }

  // -- Évènements du bus ---------------------------------------------------------------------

  bus.abonner("tache:active", ({ tache: t }) => {
    actif = t === tache;
    if (actif) rafraichirPanneau();
  });
  bus.abonner("mode:change", (charge) => {
    const hors = lireMode(charge);
    if (hors !== null) appliquerMode(hors);
  });
  bus.abonner("envoi", ({ tache: t, texte }) => {
    if (t !== tache) return;
    remplacement = null;
    creerTour(texte);
  });
  bus.abonner("generation:debut", ({ tache: t }) => {
    enCours = t === tache;
    if (!enCours) {
      remplacement = null;
      return;
    }
    if (remplacement && remplacement === derniere()) {
      remplacement.preparer(); // régénération : la réponse est vidée au premier évènement
    } else {
      remplacement = null;
      const r = derniere() ?? creerTour(null);
      r.debut();
      tourDe(r).fin = null;
      selection = null;
    }
    majBoutons();
    rafraichirPanneau();
  });

  /**
   * Réponse qui reçoit les évènements, ou `null`. Seule la vue qui a lancé la génération les
   * reçoit : aucun tour n'est créé pour un flux sans `generation:debut` (flux d'une autre Tâche,
   * évènements tardifs après « Nouvelle conversation »).
   */
  function courante() {
    if (!enCours) return null;
    const r = derniere();
    if (r && r === remplacement) {
      remplacement = null;
      r.debut();
      tourDe(r).fin = null;
      selection = null;
      rafraichirPanneau();
    }
    return r;
  }

  bus.abonner("evenement:jeton", (e) => courante()?.jeton(e.texte));
  bus.abonner("evenement:sources", (e) => {
    const r = courante();
    if (!r) return;
    r.fixerSources(e.sources ?? []);
    rafraichirPanneau();
  });
  bus.abonner("evenement:avertissement", (e) => courante()?.avertir(e.message));
  bus.abonner("evenement:repli", () => courante()?.signalerRepli());
  bus.abonner("evenement:resultat-outil", (e) => courante()?.outil(e));
  bus.abonner("evenement:fin", (e) => {
    const r = courante();
    if (!r) return;
    r.terminer(e);
    r.fixerModele(e?.modele_repondant);
    tourDe(r).fin = e?.raison ?? "terminee";
    tourDe(r).modele = typeof e?.modele_repondant === "string" ? e.modele_repondant : null;
    enCours = false;
    majBoutons();
    rafraichirPanneau();
    publierTours("fin");
  });
  bus.abonner("evenement:erreur", (e) => {
    const r = courante();
    if (!r) return;
    r.echec();
    if (e?.code === "modele-externe-interrompu") r.proposerLocal();
    tourDe(r).fin = "echec";
    enCours = false;
    majBoutons();
    rafraichirPanneau();
  });
  // L'appel au pont a échoué ou a été refusé (`generation-en-cours`…) : aucun évènement ne suivra.
  bus.abonner("generation:erreur", (charge) => {
    if (!enCours || (charge?.tache && charge.tache !== tache)) return;
    enCours = false;
    if (remplacement) {
      remplacement.retablir(); // la réponse précédente reste en place
      remplacement = null;
    } else if (derniere()) {
      derniere().echec();
      tours.at(-1).fin = "echec";
    }
    majBoutons();
    rafraichirPanneau();
  });

  bus.abonner("nouvelle", ({ tache: t }) => {
    if (t !== tache) return;
    const arreter = enCours;
    tours.length = 0;
    fil.replaceChildren();
    selection = null;
    remplacement = null;
    enCours = false; // les évènements tardifs de la génération arrêtée sont ignorés
    majBoutons();
    rafraichirPanneau();
    Promise.resolve()
      .then(() => (arreter ? pont.arreter() : null))
      .then(() => pont.appeler("nouvelle_conversation"))
      .catch(() => {}); // seul l'oubli du dernier envoi côté pont est en jeu : rien à montrer
  });
  // Rouverture depuis l'Historique (story 12.11) : le fil affiché est remplacé par la conversation
  // enregistrée. Chaque réponse reprend ses propres sources (à défaut, la dernière reçoit celles de
  // la conversation). Rien n'est annoncé ici : l'Historique annonce la rouverture une seule fois.
  bus.abonner("historique:rouvrir", ({ tache: t, messages, sources }) => {
    if (t !== tache) return;
    tours.length = 0;
    fil.replaceChildren();
    selection = null;
    remplacement = null;
    enCours = false;
    let question = null;
    const dernierIndex = messages.findLastIndex((m) => m.role === "assistant");
    for (const [i, m] of messages.entries()) {
      if (m.role === "user") {
        question = m.content;
        continue;
      }
      const r = creerTour(question);
      question = null;
      r.debut();
      r.jeton(m.content);
      if (Array.isArray(m.sources)) r.fixerSources(m.sources);
      else if (i === dernierIndex) r.fixerSources(sources ?? []);
      const raison = m.interrompue ? "interrompue" : "terminee";
      r.terminer({ raison }, { annonce: false });
      r.fixerModele(m.modele_repondant);
      tours.at(-1).fin = raison;
      tours.at(-1).modele = typeof m.modele_repondant === "string" ? m.modele_repondant : null;
    }
    majBoutons();
    rafraichirPanneau();
    publierTours("rouverture");
  });
  bus.abonner("copier-dernier", async ({ tache: t }) => {
    const r = derniere();
    if (t !== tache || !r?.brut) return;
    const ok = await copierTexte(r.brut);
    confirmer(r.el, ok ? "Copié" : "Copie impossible");
  });

  // Mode initial : `mode.etat()` du pont (contrat 12.5, bouchon jusqu'à 12.9), sinon hors ligne.
  Promise.resolve()
    .then(() => pont.appeler("mode.etat"))
    .then((valeur) => {
      const hors = lireMode(valeur);
      if (hors !== null) appliquerMode(hors);
    })
    .catch(() => {});

  appliquerMode(true);
  majBoutons();
}
