// Fil de conversation partagé par les vues Question et Recherche de données (story 12.7).
// Il consomme les évènements du bus (`evenement:<type>` : format `core.evenements.vers_dict`),
// tient le panneau Sources du socle et l'écran vide.

import { creerReponse } from "./reponse.js";
import { confirmer, copierTexte } from "./copie.js";
import { rendrePanneauSources } from "./sources.js";

function el(balise, classe, texte) {
  const e = document.createElement(balise);
  if (classe) e.className = classe;
  if (texte !== undefined) e.textContent = texte;
  return e;
}

/** Lit un état de Mode dans une charge : `true` hors ligne, `false` connecté, `null` si inconnu. */
export function lireMode(charge) {
  if (typeof charge?.hors_ligne === "boolean") return charge.hors_ligne;
  const mode = typeof charge?.mode === "string" ? charge.mode.toLowerCase() : "";
  if (mode.startsWith("hors")) return true;
  if (mode.startsWith("connect")) return false;
  return null;
}

/**
 * @param {HTMLElement} conteneur Conteneur de la vue.
 * @param {object} pont Client du pont.
 * @param {{bus: object, tache: string}} contexte
 * @param {object} options `titre`, `intro`, `exemples` (textes d'interface), `juridique` (bool),
 *   `infoHorsLigne` (texte affiché sous le titre en Mode hors ligne, ou absent).
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
    for (const exemple of options.exemples) {
      const item = document.createElement("li");
      const bouton = el("button", "exemple", exemple);
      bouton.type = "button";
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

  const tours = []; // { reponse, element }
  let enCours = false; // une génération de cette vue est en cours
  let actif = !conteneur.hidden && !conteneur.closest("[hidden]");
  let derniereQuestion = null;
  let selection = null; // { reponse, numero }

  const appel = (fonction) =>
    Promise.resolve()
      .then(fonction)
      .catch(() => bus.emettre("generation:erreur", { tache }));

  const derniere = () => tours.at(-1)?.reponse ?? null;

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
    if (corps) rendrePanneauSources(corps, reponse.sources, { horsLigne, numero: choisie?.numero ?? null });
    bus.emettre("sources:disponibles", true);
  }

  function majBoutons() {
    for (const t of tours) t.reponse.regenerer.hidden = t.reponse !== derniere();
    vide.hidden = tours.length > 0;
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
      surRegenerer: regenerer,
      surReessayer: reessayer,
    });
    element.append(reponse.el);
    fil.append(element);
    tours.push({ reponse, element });
    majBoutons();
    return reponse;
  }

  function regenerer() {
    if (enCours) return;
    bus.emettre("generation:debut", { tache });
    appel(() => pont.appeler("regenerer"));
  }

  function reessayer() {
    if (enCours) return;
    if (derniereQuestion == null) return regenerer();
    appel(() => pont.envoyer(tache, [{ role: "user", content: derniereQuestion }], {}));
  }

  function appliquerMode(hors) {
    mode.horsLigne = hors;
    racine.dataset.mode = hors ? "hors-ligne" : "connecte";
    info.hidden = !(hors && options.infoHorsLigne);
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
    derniereQuestion = texte;
    creerTour(texte);
  });
  bus.abonner("generation:debut", ({ tache: t }) => {
    enCours = t === tache;
    if (!enCours) return;
    let r = derniere();
    if (!r) r = creerTour(null);
    r.debut(); // une nouvelle réponse (état « attente ») ou une régénération sur place
    selection = null;
    majBoutons();
    rafraichirPanneau();
  });

  /** Réponse qui reçoit les évènements ; un flux sans `generation:debut` ouvre une réponse. */
  function courante() {
    if (!enCours) {
      if (!actif) return null;
      enCours = true;
      creerTour(null).debut();
    }
    return derniere();
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
    if (!enCours) return;
    derniere()?.terminer(e);
    enCours = false;
    majBoutons();
    rafraichirPanneau();
  });
  const surEchec = () => {
    if (!enCours) return;
    derniere()?.echec();
    enCours = false;
    majBoutons();
    rafraichirPanneau();
  };
  bus.abonner("evenement:erreur", surEchec);
  bus.abonner("generation:erreur", surEchec);

  bus.abonner("nouvelle", ({ tache: t }) => {
    if (t !== tache) return;
    tours.length = 0;
    fil.replaceChildren();
    selection = null;
    derniereQuestion = null;
    enCours = false;
    majBoutons();
    rafraichirPanneau();
    appel(() => pont.appeler("nouvelle_conversation"));
  });
  bus.abonner("copier-dernier", async ({ tache: t }) => {
    const r = derniere();
    if (t !== tache || !r?.brut) return;
    const ok = await copierTexte(r.brut);
    confirmer(r.el, ok ? "Copié" : "Copie impossible");
  });

  // Mode initial : lu auprès du pont s'il le sait (contrat de 12.5), sinon hors ligne.
  Promise.resolve()
    .then(() => pont.appeler("mode"))
    .then((valeur) => {
      const hors = lireMode(valeur);
      if (hors !== null) appliquerMode(hors);
    })
    .catch(() => {});

  appliquerMode(true);
  majBoutons();
}
