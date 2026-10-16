// Vue « historique » (story 12.11, FR-4, UX-DR17) : liste groupée par jour dans la colonne de
// gauche, rouverture, suppression annulable 5 s. Cette vue est montée au démarrage : c'est aussi
// elle qui enregistre les conversations des Tâches de dialogue (Question, Recherche de données)
// à la fin de chaque réponse, puis pose les pouces (vue « retours ») sous la réponse enregistrée.
// Contrat du pont : voir `app/pont/historique.py`. Tout texte entre dans le DOM par `textContent`.

import { annoncer } from "../socle/annonces.js";
import { creerPouces } from "./retours.js";

const DELAI_ANNULATION_MS = 5000;
// Libellés : EXPERIENCE.md (état vide, « Supprimer », « Annuler »). Les autres sont des
// propositions, à valider par Anaël (spec 12.11, « À confirmer »).
const VIDE = "Vos conversations apparaîtront ici. Elles restent sur ce poste.";

function el(balise, classe, texte) {
  const e = document.createElement(balise);
  if (classe) e.className = classe;
  if (texte !== undefined) e.textContent = texte;
  return e;
}

function cleJour(date) {
  return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
}

/** Étiquette d'un jour : « Aujourd'hui », « Hier », sinon la date en toutes lettres. */
export function etiquetteJour(date, maintenant = new Date()) {
  const hier = new Date(maintenant);
  hier.setDate(hier.getDate() - 1);
  if (cleJour(date) === cleJour(maintenant)) return "Aujourd'hui";
  if (cleJour(date) === cleJour(hier)) return "Hier";
  return date.toLocaleDateString("fr-FR", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
}

/** Groupe des conversations (déjà triées, récentes d'abord) par jour local. */
export function grouperParJour(conversations, maintenant = new Date()) {
  const groupes = [];
  for (const c of conversations) {
    const d = new Date(c.date);
    if (Number.isNaN(d.getTime())) continue;
    const cle = cleJour(d);
    let g = groupes.at(-1);
    if (!g || g.cle !== cle) {
      g = { cle, etiquette: etiquetteJour(d, maintenant), conversations: [] };
      groupes.push(g);
    }
    g.conversations.push(c);
  }
  return groupes;
}

/**
 * @param {HTMLElement} conteneur Élément réservé à la vue.
 * @param {object} pont Client du pont.
 * @param {{bus: object}} contexte
 */
export function monter(conteneur, pont, contexte) {
  const { bus } = contexte;
  const racine = el("div", "historique-vue");
  const liste = el("div", "historique-liste");
  const vide = el("p", "historique-vide", VIDE);
  vide.hidden = true;
  const annuler = el("div", "historique-annuler");
  annuler.setAttribute("role", "status");
  annuler.hidden = true;
  racine.append(liste, vide, annuler);
  conteneur.replaceChildren(racine);

  // -- Liste -----------------------------------------------------------------------------------

  async function actualiser() {
    let r;
    try {
      r = await pont.appeler("historique.lister");
    } catch {
      return; // la liste précédente reste affichée
    }
    if (!r || r.ok === false) return;
    const conversations = Array.isArray(r.conversations) ? r.conversations : [];
    const groupes = grouperParJour(conversations);
    vide.hidden = groupes.length > 0;
    liste.replaceChildren(...groupes.map(rendreGroupe));
  }

  function rendreGroupe(groupe) {
    const section = el("section", "historique-jour");
    const titre = el("h3", "historique-jour-titre", groupe.etiquette);
    const ul = el("ul", "historique-entrees");
    for (const c of groupe.conversations) {
      const li = el("li", "historique-entree");
      const ouvrir = el("button", "historique-ouvrir", c.titre);
      ouvrir.type = "button";
      ouvrir.dataset.id = c.id;
      ouvrir.addEventListener("click", () => rouvrir(c.id));
      const supprimer = el("button", "historique-supprimer", "Supprimer");
      supprimer.type = "button";
      supprimer.setAttribute("aria-label", `Supprimer la conversation : ${c.titre}`);
      supprimer.addEventListener("click", () => supprimer_(c));
      li.append(ouvrir, supprimer);
      ul.append(li);
    }
    section.append(titre, ul);
    return section;
  }

  // -- Suppression annulable 5 s (UX-DR17) -------------------------------------------------------

  let minuteur = null;

  function masquerAnnulation() {
    clearTimeout(minuteur);
    minuteur = null;
    annuler.hidden = true;
    annuler.replaceChildren();
  }

  async function supprimer_(c) {
    let r;
    try {
      r = await pont.appeler("historique.supprimer", c.id);
    } catch {
      r = { ok: false };
    }
    if (r?.ok === false) {
      annoncer("La conversation n'a pas pu être supprimée.");
      return;
    }
    if (courant?.id === c.id) courant = null;
    await actualiser();
    if (!r?.supprimee) return;
    masquerAnnulation();
    const bouton = el("button", "historique-annuler-bouton", "Annuler");
    bouton.type = "button";
    bouton.addEventListener("click", async () => {
      masquerAnnulation();
      let a;
      try {
        a = await pont.appeler("historique.annuler_suppression", c.id);
      } catch {
        a = { ok: false };
      }
      await actualiser();
      annoncer(a?.restauree ? "Conversation rétablie." : "La conversation n'a pas pu être rétablie.");
    });
    annuler.append(el("span", null, "Conversation supprimée. "), bouton);
    annuler.hidden = false;
    annoncer("Conversation supprimée. Vous pouvez annuler pendant 5 secondes.");
    minuteur = setTimeout(masquerAnnulation, DELAI_ANNULATION_MS);
  }

  // -- Rouverture : active la Tâche d'origine et remplace le contenu affiché ----------------------

  async function rouvrir(id) {
    if (window.slmsp?.etat?.generation) {
      annoncer("Une réponse est en cours. Attendez sa fin ou arrêtez-la.");
      return;
    }
    let r;
    try {
      r = await pont.appeler("historique.ouvrir", id);
    } catch {
      r = { ok: false };
    }
    const c = r?.conversation;
    if (!c || r.ok === false) {
      annoncer("Cette conversation n'existe plus.");
      await actualiser();
      return;
    }
    suivi = null;
    courant = { id: c.id, tache: c.tache, messages: c.messages, sources: c.sources };
    window.slmsp?.activer?.(c.tache);
    bus.emettre("historique:rouvrir", { id: c.id, tache: c.tache, messages: c.messages, sources: c.sources });
    for (const [k, index] of indicesReponses(c.messages).entries()) poserPouces(c.tache, k, c.id, index);
  }

  // -- Enregistrement des conversations ----------------------------------------------------------

  let courant = null; // { id, tache, messages, sources } : conversation en cours d'enregistrement
  let suivi = null; // { texte, sources } : réponse en train d'arriver
  let chaine = Promise.resolve(); // sérialise les enregistrements (l'id du premier sert au suivant)

  const indicesReponses = (messages) =>
    messages.flatMap((m, i) => (m.role === "assistant" ? [i] : []));

  function retirerQuestionOrpheline() {
    if (courant && courant.messages.at(-1)?.role === "user") courant.messages.pop();
  }

  bus.abonner("envoi", ({ tache, texte }) => {
    if (!courant || courant.tache !== tache) courant = { id: null, tache, messages: [], sources: [] };
    courant.messages.push({ role: "user", content: texte });
  });
  bus.abonner("generation:debut", ({ tache }) => {
    suivi = null;
    if (!courant || courant.tache !== tache) return; // Tâche non enregistrée (rédaction…)
    if (courant.messages.at(-1)?.role === "assistant") courant.messages.pop(); // régénération
    if (courant.messages.at(-1)?.role === "user") suivi = { texte: "", sources: [] };
  });
  bus.abonner("evenement:jeton", (e) => {
    if (suivi) suivi.texte += e.texte ?? "";
  });
  bus.abonner("evenement:sources", (e) => {
    if (suivi) suivi.sources = Array.isArray(e.sources) ? e.sources : [];
  });
  bus.abonner("evenement:erreur", () => {
    suivi = null;
    retirerQuestionOrpheline();
  });
  bus.abonner("generation:erreur", () => {
    if (suivi) retirerQuestionOrpheline();
    suivi = null;
  });
  bus.abonner("evenement:fin", () => {
    if (!suivi || !courant) return;
    const { texte, sources } = suivi;
    suivi = null;
    if (!texte) {
      retirerQuestionOrpheline();
      return;
    }
    courant.messages.push({ role: "assistant", content: texte });
    courant.sources = sources;
    const instantane = { ...courant, messages: courant.messages.map((m) => ({ ...m })) };
    const cible = courant;
    chaine = chaine.then(() => enregistrer(instantane, cible)).catch(() => {});
  });
  bus.abonner("nouvelle", ({ tache }) => {
    if (courant?.tache === tache) courant = null;
    suivi = null;
  });
  bus.abonner("historique:efface", () => {
    courant = null;
    suivi = null;
    actualiser();
  });

  async function enregistrer(c, cible) {
    let r;
    try {
      r = await pont.appeler("historique.enregistrer", c.tache, c.messages, c.sources, c.id);
    } catch {
      return; // l'historique est une commodité : la réponse reste affichée
    }
    if (!r || r.ok === false || typeof r.id !== "string") return;
    if (courant === cible) cible.id = r.id;
    await actualiser();
    if (courant === cible) {
      const reponses = indicesReponses(c.messages);
      poserPouces(c.tache, reponses.length - 1, r.id, reponses.at(-1));
    }
  }

  /** Pose les pouces sous la `rang`-ième réponse affichée de la Tâche (la dernière si `rang` est -1). */
  function poserPouces(tache, rang, id, index) {
    const reponses = document.querySelectorAll(`#vue-${CSS.escape(tache)} article.reponse`);
    const reponse = reponses[rang];
    const actions = reponse?.querySelector(":scope > .reponse-actions");
    if (!actions) return;
    actions.querySelector(":scope > .retour")?.remove();
    actions.append(creerPouces(pont, { bus, id, index }));
  }

  actualiser();
}
