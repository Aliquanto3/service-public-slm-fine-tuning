// Vue « historique » (story 12.11, FR-4, UX-DR17) : liste groupée par jour dans la colonne de
// gauche, rouverture, suppression annulable 5 s. Cette vue est montée au démarrage : c'est aussi
// elle qui enregistre les conversations des Tâches de dialogue (Question, Recherche de données)
// à la fin de chaque réponse, d'après le modèle des tours publié par `composants/conversation.js`
// (`conversation:tours`), puis pose les pouces (vue « retours ») sous les réponses enregistrées.
// Contrat du pont : voir `app/pont/historique.py`. Tout texte entre dans le DOM par `textContent`.

import { annoncer } from "../socle/annonces.js";
import { creerPouces } from "./retours.js";

const DELAI_ANNULATION_MS = 5000;
// Libellés : EXPERIENCE.md (état vide, « Supprimer », « Annuler »). Les autres sont des
// propositions, à valider par Anaël (spec 12.11, « À confirmer »).
const VIDE = "Vos conversations apparaîtront ici. Elles restent sur ce poste.";
const ECHEC_ENREGISTREMENT = "Cette conversation n'a pas pu être enregistrée dans l'historique.";

/**
 * Messages à enregistrer d'après les tours d'une conversation. Un tour en cours ou en échec
 * (sans réponse) n'est pas enregistré ; une réponse interrompue l'est, marquée `interrompue`.
 * Rend aussi, pour chaque tour, l'indice de sa réponse dans `messages` (ou `null`).
 */
export function messagesDesTours(tours) {
  const messages = [];
  const indices = [];
  for (const t of tours) {
    if (!t.fin || t.fin === "echec" || !t.texte) {
      indices.push(null);
      continue;
    }
    if (t.question != null) messages.push({ role: "user", content: t.question });
    const m = { role: "assistant", content: t.texte, sources: t.sources ?? [] };
    if (t.fin === "interrompue") m.interrompue = true;
    if (typeof t.modele === "string" && t.modele) m.modele_repondant = t.modele;
    indices.push(messages.length);
    messages.push(m);
  }
  return { messages, indices };
}

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
  const echec = el("p", "historique-echec");
  echec.setAttribute("role", "status");
  echec.hidden = true;
  racine.append(liste, vide, annuler, echec);
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
    // La session reste liée à l'id : « Annuler » la rétablit ; sinon, le prochain enregistrement
    // crée une nouvelle conversation (id inconnu côté pont).
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
    sessions.set(c.tache, { id: c.id });
    window.slmsp?.activer?.(c.tache, { annonce: false });
    bus.emettre("historique:rouvrir", { id: c.id, tache: c.tache, messages: c.messages, sources: c.sources });
    const n = c.messages.filter((m) => m.role === "assistant").length;
    annoncer(`Conversation rouverte, ${n} échange${n > 1 ? "s" : ""}.`);
  }

  // -- Enregistrement des conversations ----------------------------------------------------------

  // Une session par Tâche de dialogue : `{ id }`, id de la conversation enregistrée (null avant le
  // premier enregistrement). Lu au moment de l'appel : les enregistrements sont sérialisés et le
  // second reprend l'id rendu au premier.
  const sessions = new Map();
  const poses = new WeakMap(); // pouces -> texte de la réponse notée
  let chaine = Promise.resolve();

  bus.abonner("conversation:tours", ({ tache, origine, tours }) => {
    const { messages, indices } = messagesDesTours(tours);
    const elements = tours.map((t) => t.element);
    if (origine === "rouverture") {
      const session = sessions.get(tache);
      if (session?.id) poserPouces(elements, indices, session.id, tours);
      return;
    }
    if (!messages.length) return;
    let session = sessions.get(tache);
    if (!session) {
      session = { id: null };
      sessions.set(tache, session);
    }
    const sources = messages.at(-1).sources;
    chaine = chaine
      .then(() => enregistrer(session, tache, messages, sources, { elements, indices, tours }))
      .catch(() => {});
  });
  bus.abonner("nouvelle", ({ tache }) => sessions.delete(tache));
  bus.abonner("historique:efface", () => {
    sessions.clear();
    actualiser();
  });

  async function enregistrer(session, tache, messages, sources, affichage) {
    let r;
    try {
      r = await pont.appeler("historique.enregistrer", tache, messages, sources, session.id);
    } catch {
      r = null;
    }
    if (!r || r.ok === false || typeof r.id !== "string") {
      // L'historique est une commodité : la réponse reste affichée, l'Agent est prévenu.
      echec.textContent = ECHEC_ENREGISTREMENT;
      echec.hidden = false;
      return;
    }
    echec.hidden = true;
    session.id = r.id;
    await actualiser();
    if (sessions.get(tache) === session) poserPouces(affichage.elements, affichage.indices, r.id, affichage.tours);
  }

  /** Pose les pouces sous chaque réponse enregistrée, sauf ceux déjà posés pour le même texte. */
  function poserPouces(elements, indices, id, tours) {
    for (const [k, element] of elements.entries()) {
      const index = indices[k];
      const actions = element?.querySelector(":scope > .reponse-actions");
      if (index == null || !actions) continue;
      const cle = `${id}:${index}`;
      const present = actions.querySelector(":scope > .retour");
      if (present && present.dataset.cle === cle && poses.get(present) === tours[k].texte) continue;
      present?.remove();
      const pouces = creerPouces(pont, { bus, id, index });
      pouces.dataset.cle = cle;
      poses.set(pouces, tours[k].texte);
      actions.append(pouces);
    }
  }
  actualiser();
}
