// Vue « retours » (story 12.11, FR-19, FR-20, UX-DR16, UX-DR19).
// Deux composants : les pouces sous une réponse (`creerPouces`, posés par la vue « historique »
// qui connaît la conversation enregistrée) et l'export des Retours dans l'onglet Retours des
// Paramètres (`monter`). Contrat du pont : voir `app/pont/retours.py`.
// Tout texte entre dans le DOM par `textContent` (jamais de HTML construit).

import { annoncer } from "../socle/annonces.js";

// Libellés : EXPERIENCE.md (confirmation, champ du pouce bas, aucun retour, aperçu, bouton).
// Les autres sont des propositions, à valider par Anaël (spec 12.11, « À confirmer »).
export const TEXTES = {
  merci: "Merci, retour enregistré sur ce poste",
  champ: "Qu'est-ce qui n'allait pas ?",
  facultatif: "(facultatif)",
  envoyer: "Envoyer mon retour",
  echec: "Le retour n'a pas pu être enregistré.",
  aucun: "Vous n'avez encore donné aucun retour.",
  exporter: "Exporter mes retours",
  enregistrer: "Enregistrer le fichier",
  fermer: "Fermer l'aperçu",
  intro:
    "Vos retours restent sur ce poste. Vous pouvez les exporter dans un fichier, que vous transmettez vous-même.",
};

function el(balise, classe, texte) {
  const e = document.createElement(balise);
  if (classe) e.className = classe;
  if (texte !== undefined) e.textContent = texte;
  return e;
}

const CHEMIN_POUCE =
  "M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-2z";

function iconePouce() {
  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg");
  svg.setAttribute("viewBox", "0 0 24 24");
  svg.setAttribute("width", "18");
  svg.setAttribute("height", "18");
  svg.setAttribute("aria-hidden", "true");
  const chemin = document.createElementNS(ns, "path");
  chemin.setAttribute("d", CHEMIN_POUCE);
  chemin.setAttribute("fill", "currentColor");
  svg.append(chemin);
  return svg;
}

/**
 * Pouces d'une réponse enregistrée. Pouce haut : enregistré tout de suite. Pouce bas : champ de
 * commentaire facultatif, puis enregistrement au clic sur « Envoyer mon retour ».
 * @param {object} pont Client du pont.
 * @param {{bus?: object, id: string, index: number}} cible Conversation enregistrée et indice du
 *   message de l'Assistant dans cette conversation.
 */
export function creerPouces(pont, { bus, id, index }) {
  const racine = el("div", "retour");
  racine.setAttribute("role", "group");
  racine.setAttribute("aria-label", "Votre avis sur cette réponse");

  const haut = el("button", "bouton-icone retour-pouce retour-haut");
  const bas = el("button", "bouton-icone retour-pouce retour-bas");
  for (const [b, libelle] of [
    [haut, "Réponse utile (pouce haut)"],
    [bas, "Réponse à améliorer (pouce bas)"],
  ]) {
    b.type = "button";
    b.setAttribute("aria-label", libelle);
    b.title = libelle;
    b.setAttribute("aria-pressed", "false");
    b.append(iconePouce());
  }
  const message = el("span", "retour-message");
  message.setAttribute("role", "status");

  const formulaire = el("form", "retour-commentaire");
  formulaire.hidden = true;
  const etiquette = el("label", null, `${TEXTES.champ} `);
  etiquette.append(el("span", "retour-facultatif", TEXTES.facultatif));
  const champ = document.createElement("textarea");
  champ.rows = 3;
  champ.maxLength = 2000;
  champ.id = `retour-commentaire-${id}-${index}`;
  etiquette.htmlFor = champ.id;
  const envoyer = el("button", "bouton-secondaire", TEXTES.envoyer);
  envoyer.type = "submit";
  formulaire.append(etiquette, champ, envoyer);
  racine.append(haut, bas, message, formulaire);

  let enCours = false;

  async function noter(jugement, commentaire) {
    if (enCours) return;
    enCours = true;
    haut.disabled = bas.disabled = true;
    try {
      const r = await pont.appeler("retours.noter", id, index, jugement, commentaire);
      if (r && r.ok === false) throw new Error("refus");
      (jugement === "pouce_haut" ? haut : bas).setAttribute("aria-pressed", "true");
      formulaire.hidden = true;
      message.textContent = TEXTES.merci;
      annoncer(TEXTES.merci);
      bus?.emettre("retours:change", {});
    } catch {
      haut.disabled = bas.disabled = false;
      message.textContent = TEXTES.echec;
      annoncer(TEXTES.echec);
    } finally {
      enCours = false;
    }
  }

  haut.addEventListener("click", () => noter("pouce_haut", null));
  bas.addEventListener("click", () => {
    formulaire.hidden = false;
    champ.focus();
  });
  formulaire.addEventListener("submit", (e) => {
    e.preventDefault();
    noter("pouce_bas", champ.value.trim() || null);
  });
  return racine;
}

/**
 * Monte l'export des Retours dans son conteneur (onglet Retours des Paramètres).
 * @param {HTMLElement} conteneur Élément réservé à la vue.
 * @param {object} pont Client du pont.
 * @param {{bus?: object}} [contexte]
 */
export function monter(conteneur, pont, contexte = {}) {
  const { bus } = contexte;
  const racine = el("div", "retours");
  const intro = el("p", "retours-intro", TEXTES.intro);
  const exporter = el("button", "bouton-secondaire", TEXTES.exporter);
  exporter.type = "button";
  exporter.id = "retours-exporter";
  exporter.disabled = true;
  const etat = el("p", "retours-etat");
  etat.id = "retours-etat";
  etat.setAttribute("role", "status");
  const apercu = el("section", "retours-apercu");
  apercu.setAttribute("aria-label", "Aperçu du fichier anonymisé");
  apercu.hidden = true;
  racine.append(intro, exporter, etat, apercu);
  conteneur.replaceChildren(racine);

  async function actualiser() {
    try {
      const r = await pont.appeler("retours.lister");
      const n = r && r.ok !== false && Number.isInteger(r.nombre) ? r.nombre : null;
      exporter.disabled = !n;
      etat.textContent = n === 0 ? TEXTES.aucun : "";
      if (!n) apercu.hidden = true;
    } catch {
      exporter.disabled = true;
    }
  }

  function fermerApercu({ focus = true } = {}) {
    apercu.hidden = true;
    apercu.replaceChildren();
    if (focus) exporter.focus();
  }

  async function ouvrirApercu() {
    etat.textContent = "";
    let r;
    try {
      r = await pont.appeler("retours.apercu_export");
    } catch {
      r = { ok: false };
    }
    if (!r || r.ok === false) {
      etat.textContent = r?.erreur?.code === "aucun-retour" ? TEXTES.aucun : "L'aperçu n'a pas pu être préparé.";
      return;
    }
    const titre = el("h3", null, `Aperçu : ${r.nom_fichier}`);
    const masques = Object.values(r.masques ?? {}).reduce((a, b) => a + b, 0);
    const resume = el(
      "p",
      "retours-resume",
      `${r.nombre} retour${r.nombre > 1 ? "s" : ""}, ${masques} élément${masques > 1 ? "s" : ""} masqué${masques > 1 ? "s" : ""}. Relisez avant d'enregistrer : rien n'est envoyé.`,
    );
    const avertissements = (r.avertissements ?? []).map((a) => {
      const p = el("p", "callout callout-warning", a);
      p.setAttribute("role", "note");
      return p;
    });
    const texte = el("pre", "retours-texte", r.apercu);
    texte.tabIndex = 0;
    texte.setAttribute("aria-label", "Contenu du fichier");
    const enregistrer = el("button", "bouton-primaire", TEXTES.enregistrer);
    enregistrer.type = "button";
    const fermer = el("button", "bouton-secondaire", TEXTES.fermer);
    fermer.type = "button";
    const actions = el("div", "retours-actions");
    actions.append(enregistrer, fermer);
    apercu.replaceChildren(titre, resume, ...avertissements, texte, actions);
    apercu.hidden = false;
    texte.focus();

    fermer.addEventListener("click", fermerApercu);
    enregistrer.addEventListener("click", async () => {
      enregistrer.disabled = true;
      let s;
      try {
        s = await pont.appeler("retours.exporter");
      } catch {
        s = { ok: false };
      }
      enregistrer.disabled = false;
      let message;
      const code = s?.erreur?.code;
      if (code === "fichier-existant") message = "Un fichier porte déjà ce nom. Choisissez un autre nom.";
      else if (code === "apercu-perime") message = "Vos retours ont changé : ouvrez de nouveau l'aperçu.";
      else if (s?.ok === false) message = "Le fichier n'a pas pu être enregistré.";
      else if (s?.enregistre) message = `Fichier enregistré : ${s.nom}.`;
      else message = "Enregistrement annulé. Rien n'a été écrit.";
      etat.textContent = message;
      annoncer(message);
      if (s?.enregistre || code === "apercu-perime") fermerApercu();
    });
  }

  exporter.addEventListener("click", ouvrirApercu);
  // L'aperçu affiché ne correspond plus aux Retours enregistrés : il est fermé (le pont le refuse
  // de toute façon, `apercu-perime`).
  const invalider = () => {
    if (!apercu.hidden) fermerApercu({ focus: false });
    actualiser();
  };
  bus?.abonner("retours:change", invalider);
  bus?.abonner("historique:efface", invalider);
  document.getElementById("bouton-parametres")?.addEventListener("click", actualiser);
  actualiser();
}
