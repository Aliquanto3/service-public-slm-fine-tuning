// Vue « mode » (story 12.9, UX-DR7 et UX-DR8) : pastille de Mode, menu à trois éléments et
// journal des Requêtes sortantes. Contrat du pont : voir `app/pont/mode.py`.
import { annoncer } from "../socle/annonces.js";

const PERIODE_MS = 30_000;
const LIMITE_JOURNAL = 200;
const LIBELLES = {
  connecte: "Connecté",
  hors_ligne: "Hors ligne",
  force: "Hors ligne (choisi)",
};
const STATUTS = {
  envoyee: "Envoyée",
  echouee: "Échouée",
  "bloquee-liste": "Bloquée (hôte hors liste)",
  "bloquee-mode": "Bloquée (hors ligne)",
};

function el(nom, attributs = {}, texte) {
  const e = document.createElement(nom);
  for (const [cle, valeur] of Object.entries(attributs)) e.setAttribute(cle, valeur);
  if (texte !== undefined) e.textContent = texte;
  return e;
}

/** Libellé de la pastille selon l'état poussé par le pont. */
export function libelle(etat) {
  if (etat.force) return LIBELLES.force;
  return etat.hors_ligne ? LIBELLES.hors_ligne : LIBELLES.connecte;
}

function formaterHeure(iso) {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return String(iso);
  return d.toLocaleString("fr-FR", { dateStyle: "short", timeStyle: "medium" });
}

/**
 * Monte la vue dans son conteneur.
 * @param {HTMLElement} conteneur Élément réservé à la vue.
 * @param {object} pont Client du pont (appeler, envoyer, arreter).
 * @param {object} [contexte] `{ bus, tache }` : bus d'évènements et Tâche servie par ce conteneur.
 */
export function monter(conteneur, pont, contexte = {}) {
  const bus = contexte.bus;
  let etat = { hors_ligne: true, force: false };
  let connu = false;

  const racine = el("div", { class: "mode" });
  const pastille = el("button", {
    type: "button",
    id: "mode-pastille",
    class: "mode-pastille",
    "aria-haspopup": "menu",
    "aria-expanded": "false",
    "aria-controls": "mode-menu",
  });
  const point = el("span", { class: "mode-point", "aria-hidden": "true" });
  const texte = el("span", { class: "mode-texte" });
  pastille.append(point, texte);

  const menu = el("div", { id: "mode-menu", class: "mode-menu", role: "menu", hidden: "" });
  menu.setAttribute("aria-label", "Mode de connexion");
  const statut = el("p", { class: "mode-statut", role: "none" });
  const basculer = el(
    "button",
    { type: "button", role: "menuitemcheckbox", "aria-checked": "false", class: "mode-element" },
    "Rester hors ligne",
  );
  const voirJournal = el(
    "button",
    { type: "button", role: "menuitem", class: "mode-element" },
    "Journal des requêtes sortantes",
  );
  menu.append(statut, basculer, voirJournal);

  const dialogue = el("dialog", { class: "mode-journal", "aria-labelledby": "mode-journal-titre" });
  const tete = el("div", { class: "dialogue-tete" });
  const titre = el("h2", { id: "mode-journal-titre" }, "Requêtes sortantes");
  const fermer = el("button", { type: "button", class: "bouton-secondaire" }, "Fermer");
  tete.append(titre, fermer);
  const aide = el(
    "p",
    { class: "mode-journal-aide" },
    "Ce que l'assistant a contacté sur le réseau pendant les 30 derniers jours.",
  );
  const zone = el("div", { class: "mode-journal-zone" });
  const effacer = el("button", { type: "button", class: "bouton-secondaire" }, "Effacer le journal");
  dialogue.append(tete, aide, zone, effacer);

  racine.append(pastille, menu, dialogue);
  conteneur.replaceChildren(racine);

  function afficher() {
    texte.textContent = connu ? libelle(etat) : "Mode…";
    racine.dataset.mode = !connu ? "inconnu" : etat.force ? "force" : etat.hors_ligne ? "hors-ligne" : "connecte";
    statut.textContent = connu ? `Mode actuel : ${libelle(etat)}` : "Mode en cours de lecture…";
    basculer.setAttribute("aria-checked", String(Boolean(etat.force)));
  }

  /** Applique un état venu du pont ; une seule annonce, et seulement s'il a changé. */
  function appliquer(nouveau) {
    if (!nouveau || typeof nouveau.hors_ligne !== "boolean") return;
    const avant = { ...etat };
    const etaitConnu = connu;
    etat = { hors_ligne: nouveau.hors_ligne, force: Boolean(nouveau.force) };
    connu = true;
    afficher();
    const change = !etaitConnu || avant.hors_ligne !== etat.hors_ligne || avant.force !== etat.force;
    if (!change) return;
    if (etaitConnu) annoncer(`Mode : ${libelle(etat)}`);
    if (!etaitConnu || avant.hors_ligne !== etat.hors_ligne) {
      bus?.emettre("mode:change", { hors_ligne: etat.hors_ligne });
    }
  }

  async function lire() {
    try {
      appliquer(await pont.appeler("mode.etat"));
    } catch {
      /* le pont ne répond pas : l'état précédent reste affiché */
    }
  }

  function ouvrirMenu(ouvert) {
    menu.hidden = !ouvert;
    pastille.setAttribute("aria-expanded", String(ouvert));
    if (ouvert) basculer.focus();
  }

  pastille.addEventListener("click", () => ouvrirMenu(menu.hidden));
  menu.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      ouvrirMenu(false);
      pastille.focus();
    } else if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      const items = [basculer, voirJournal];
      const i = items.indexOf(document.activeElement);
      items[(i + (e.key === "ArrowDown" ? 1 : items.length - 1)) % items.length].focus();
    }
  });
  document.addEventListener("click", (e) => {
    if (!menu.hidden && !racine.contains(e.target)) ouvrirMenu(false);
  });

  basculer.addEventListener("click", async () => {
    const cible = !etat.force;
    ouvrirMenu(false);
    pastille.focus();
    try {
      appliquer(await pont.appeler("mode.forcer_hors_ligne", cible));
    } catch {
      annoncer("Le changement de mode a échoué.");
    }
  });

  function rendreJournal(entrees) {
    if (entrees.length === 0) {
      zone.replaceChildren(el("p", { class: "mode-vide" }, "Aucune requête sortante sur les 30 derniers jours."));
      effacer.disabled = true;
      return;
    }
    effacer.disabled = false;
    const table = el("table", { class: "mode-table" });
    const entete = el("tr");
    for (const t of ["Heure", "Hôte", "Termes", "Statut"]) entete.append(el("th", { scope: "col" }, t));
    const thead = el("thead");
    thead.append(entete);
    const corps = el("tbody");
    for (const e of entrees) {
      const tr = el("tr");
      tr.append(
        el("td", {}, formaterHeure(e.horodatage)),
        el("td", {}, e.hote),
        el("td", {}, e.termes ?? "—"),
        el("td", {}, STATUTS[e.statut] ?? e.statut),
      );
      corps.append(tr);
    }
    table.append(thead, corps);
    zone.replaceChildren(table);
  }

  async function chargerJournal() {
    try {
      const r = await pont.appeler("mode.journal", LIMITE_JOURNAL);
      rendreJournal(Array.isArray(r?.entrees) ? r.entrees : []);
    } catch {
      zone.replaceChildren(el("p", { class: "mode-vide", role: "alert" }, "Le journal n'a pas pu être lu."));
    }
  }

  voirJournal.addEventListener("click", async () => {
    ouvrirMenu(false);
    await chargerJournal();
    dialogue.showModal();
    fermer.focus();
  });
  fermer.addEventListener("click", () => dialogue.close());
  dialogue.addEventListener("close", () => pastille.focus());
  effacer.addEventListener("click", async () => {
    try {
      await pont.appeler("mode.effacer_journal");
      rendreJournal([]);
      annoncer("Journal effacé.");
      fermer.focus();
    } catch {
      annoncer("Le journal n'a pas pu être effacé.");
    }
  });

  bus?.abonner("evenement:mode", (e) => appliquer(e));
  afficher();
  lire();
  setInterval(lire, PERIODE_MS);
}
