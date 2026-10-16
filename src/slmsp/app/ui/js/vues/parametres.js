// Vue « parametres » (story 12.10, UX-DR18) : trois onglets Général, Retours et À propos.
// Contrat du pont : voir `app/pont/reglages.py`. L'onglet Retours accueille le composant de la
// vue « retours » (monté par app.js dans `#ancre-retours`, déplacé ici).
import { annoncer } from "../socle/annonces.js";
import { CRANS_TAILLE } from "../socle/clavier.js";
import { memoire } from "../socle/pont-client.js";

const DELAI_ANNULATION_MS = 5000;
const ABSENT = "non disponible";

function el(nom, attributs = {}, texte) {
  const e = document.createElement(nom);
  for (const [cle, valeur] of Object.entries(attributs)) e.setAttribute(cle, valeur);
  if (texte !== undefined) e.textContent = texte;
  return e;
}

function ligne(libelle, valeur) {
  const bloc = el("div", { class: "parametres-ligne" });
  bloc.append(el("dt", {}, libelle), el("dd", {}, valeur ?? ABSENT));
  return bloc;
}

function section(titre, ...contenu) {
  const s = el("section", { class: "parametres-section" });
  s.append(el("h3", {}, titre), ...contenu);
  return s;
}

function formaterDate(iso) {
  const d = new Date(`${iso}T00:00:00`);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString("fr-FR", { dateStyle: "long" });
}

/**
 * Monte la vue dans son conteneur.
 * @param {HTMLElement} conteneur Élément réservé à la vue.
 * @param {object} pont Client du pont (appeler, envoyer, arreter).
 * @param {object} [contexte] `{ bus, delaiAnnulationMs }`.
 */
export function monter(conteneur, pont, contexte = {}) {
  const bus = contexte.bus;
  const delai = contexte.delaiAnnulationMs ?? DELAI_ANNULATION_MS;

  const onglets = [
    { id: "general", libelle: "Général" },
    { id: "retours", libelle: "Retours" },
    { id: "apropos", libelle: "À propos" },
  ];
  const racine = el("div", { class: "parametres" });
  const liste = el("div", { class: "parametres-onglets", role: "tablist", "aria-label": "Paramètres" });
  const panneaux = {};
  const boutons = {};
  for (const o of onglets) {
    const b = el("button", {
      type: "button",
      role: "tab",
      id: `parametres-onglet-${o.id}`,
      "aria-controls": `parametres-panneau-${o.id}`,
      class: "parametres-onglet",
    }, o.libelle);
    const p = el("div", {
      role: "tabpanel",
      id: `parametres-panneau-${o.id}`,
      "aria-labelledby": `parametres-onglet-${o.id}`,
      class: "parametres-panneau",
      tabindex: "0",
    });
    boutons[o.id] = b;
    panneaux[o.id] = p;
    liste.append(b);
  }

  function choisir(id, { focus = false } = {}) {
    for (const o of onglets) {
      const actif = o.id === id;
      boutons[o.id].setAttribute("aria-selected", String(actif));
      boutons[o.id].tabIndex = actif ? 0 : -1;
      panneaux[o.id].hidden = !actif;
    }
    if (focus) boutons[id].focus();
    if (id === "apropos") chargerAPropos();
  }
  liste.addEventListener("keydown", (e) => {
    const i = onglets.findIndex((o) => boutons[o.id] === document.activeElement);
    if (i < 0) return;
    let cible = null;
    if (e.key === "ArrowRight") cible = (i + 1) % onglets.length;
    else if (e.key === "ArrowLeft") cible = (i + onglets.length - 1) % onglets.length;
    else if (e.key === "Home") cible = 0;
    else if (e.key === "End") cible = onglets.length - 1;
    if (cible === null) return;
    e.preventDefault();
    choisir(onglets[cible].id, { focus: true });
  });
  for (const o of onglets) boutons[o.id].addEventListener("click", () => choisir(o.id));

  // -- Général : taille du texte, Mode, effacement ----------------------------------------
  const general = panneaux.general;

  const valeurTaille = el("output", { class: "parametres-taille-valeur", "aria-live": "off" });
  const reduire = el("button", { type: "button", class: "bouton-secondaire", "aria-label": "Réduire le texte" }, "A−");
  const agrandir = el("button", { type: "button", class: "bouton-secondaire", "aria-label": "Agrandir le texte" }, "A+");
  const normal = el("button", { type: "button", class: "bouton-secondaire" }, "100 %");
  const aideTaille = el("p", { class: "parametres-aide" }, "Raccourcis : Ctrl et +, Ctrl et −, Ctrl et 0.");
  const rangTaille = el("div", { class: "parametres-rang" });
  rangTaille.append(reduire, valeurTaille, agrandir, normal);

  function tailleCourante() {
    const lue = Number.parseInt(document.documentElement.style.getPropertyValue("--echelle"), 10);
    return CRANS_TAILLE.includes(lue) ? lue : memoire.lire("echelle", CRANS_TAILLE[0]);
  }
  function afficherTaille() {
    valeurTaille.textContent = `${tailleCourante()} %`;
  }
  function fixerTaille(pourcent) {
    document.documentElement.style.setProperty("--echelle", `${pourcent}%`);
    memoire.ecrire("echelle", pourcent);
    annoncer(`Taille du texte : ${pourcent} %`);
  }
  function pas(delta) {
    const i = Math.max(0, CRANS_TAILLE.indexOf(tailleCourante()));
    fixerTaille(CRANS_TAILLE[Math.min(CRANS_TAILLE.length - 1, Math.max(0, i + delta))]);
  }
  reduire.addEventListener("click", () => pas(-1));
  agrandir.addEventListener("click", () => pas(1));
  normal.addEventListener("click", () => fixerTaille(CRANS_TAILLE[0]));

  // La taille change aussi par les raccourcis du socle : on la mémorise côté pont à chaque cran.
  let enregistree = null;
  new MutationObserver(() => {
    const t = tailleCourante();
    afficherTaille();
    if (t === enregistree) return;
    enregistree = t;
    Promise.resolve(pont.appeler("reglages.ecrire", "taille_texte", t)).catch(() => {});
  }).observe(document.documentElement, { attributes: true, attributeFilter: ["style"] });

  const horsLigne = el("input", { type: "checkbox", id: "parametres-hors-ligne" });
  const etiquetteHL = el("label", { for: "parametres-hors-ligne" }, "Rester hors ligne");
  const aideHL = el(
    "p",
    { class: "parametres-aide" },
    "Aucune requête ne sort de cet ordinateur. Le Mode se règle aussi depuis la pastille en haut.",
  );
  const rangHL = el("div", { class: "parametres-rang" });
  rangHL.append(horsLigne, etiquetteHL);
  horsLigne.addEventListener("change", async () => {
    const cible = horsLigne.checked;
    try {
      const r = await pont.appeler("mode.forcer_hors_ligne", cible);
      if (!r || r.ok === false) throw new Error("refus");
      horsLigne.checked = Boolean(r.force);
    } catch {
      horsLigne.checked = !cible;
      annoncer("Le changement de mode a échoué.");
    }
  });
  bus?.abonner("evenement:mode", (e) => {
    horsLigne.checked = Boolean(e?.force);
  });

  const effacer = el("button", { type: "button", class: "bouton-secondaire", id: "parametres-effacer" }, "Effacer tout l'historique");
  const confirmation = el("div", { class: "parametres-confirmation", role: "status", hidden: "" });
  const messageConf = el("span");
  const annuler = el("button", { type: "button", class: "bouton-secondaire", id: "parametres-effacer-annuler" }, "Annuler");
  confirmation.append(messageConf, annuler);
  const aideEff = el(
    "p",
    { class: "parametres-aide" },
    "Supprime vos conversations et vos retours sur cet ordinateur. Vous pouvez annuler pendant 5 secondes.",
  );
  let minuteur = null;
  function arreterEffacement() {
    clearTimeout(minuteur);
    minuteur = null;
    confirmation.hidden = true;
    effacer.disabled = false;
  }
  effacer.addEventListener("click", () => {
    effacer.disabled = true;
    messageConf.textContent = `L'historique sera effacé dans ${Math.round(delai / 1000)} secondes.`;
    confirmation.hidden = false;
    annuler.focus();
    annoncer("Effacement de l'historique dans 5 secondes. Vous pouvez annuler.");
    minuteur = setTimeout(async () => {
      minuteur = null;
      try {
        const r = await pont.appeler("reglages.effacer_historique");
        if (!r || r.ok === false) throw new Error("refus");
        bus?.emettre("historique:efface", {});
        messageConf.textContent = "Historique effacé.";
        annoncer("Historique effacé.");
      } catch {
        messageConf.textContent = "L'historique n'a pas pu être effacé.";
        annoncer("L'historique n'a pas pu être effacé.");
      }
      annuler.hidden = true;
      setTimeout(() => {
        arreterEffacement();
        annuler.hidden = false;
      }, 3000);
    }, delai);
  });
  annuler.addEventListener("click", () => {
    arreterEffacement();
    effacer.focus();
    annoncer("Effacement annulé.");
  });

  general.append(
    section("Taille du texte", rangTaille, aideTaille),
    section("Connexion", rangHL, aideHL),
    section("Historique", effacer, confirmation, aideEff),
  );

  // -- Retours : le composant de la vue « retours » s'y monte ------------------------------
  const ancreRetours = document.getElementById("ancre-retours");
  if (ancreRetours) panneaux.retours.append(ancreRetours);

  // -- À propos ----------------------------------------------------------------------------
  const apropos = panneaux.apropos;
  let charge = false;

  function rendreAPropos(r) {
    const app = r.application ?? {};
    const modele = r.modele;
    const index = r.index;
    const listeDl = (...lignes) => {
      const dl = el("dl", { class: "parametres-liste" });
      dl.append(...lignes);
      return dl;
    };
    const blocs = [];
    blocs.push(
      section(
        "Versions",
        listeDl(
          ligne("Application", app.version),
          ligne("Empreinte de l'application (SHA-256)", app.empreinte),
          ligne("Modèle embarqué", modele?.slug),
          ligne("Empreinte attendue du modèle (SHA-256)", modele?.sha256_attendu),
          ligne("Index", index?.version),
          ligne("Date de l'Index", index ? formaterDate(index.date_snapshot) : null),
        ),
      ),
    );
    const hotes = Array.isArray(r.liste_blanche) ? r.liste_blanche : [];
    const ul = el("ul", { class: "parametres-hotes", "aria-label": "Sites que l'assistant peut contacter" });
    for (const h of hotes) ul.append(el("li", {}, h));
    blocs.push(
      section(
        "Sites que l'assistant peut contacter",
        el("p", { class: "parametres-aide" }, "Seulement si vous êtes connecté, et seulement ces sites :"),
        hotes.length ? ul : el("p", {}, "Liste non disponible."),
      ),
    );
    const hors = Array.isArray(r.hors_passerelle) ? r.hors_passerelle : [];
    if (hors.length) {
      const dl = el("dl", { class: "parametres-liste" });
      for (const h of hors) dl.append(ligne(h.composant, h.detail));
      blocs.push(section("Ce que l'assistant ne contrôle pas", dl));
    }
    const lic = r.licences ?? { composants: [] };
    const ulLic = el("ul", { class: "parametres-licences" });
    for (const c of lic.composants) ulLic.append(el("li", {}, `${c.nom} : ${c.licence}`));
    const blocLic = section("Licences des composants", lic.composants.length ? ulLic : el("p", {}, "Liste non disponible."));
    if (lic.statut === "provisoire") {
      blocLic.append(el("p", { class: "parametres-aide" }, "Liste provisoire, en cours de vérification."));
    }
    blocs.push(blocLic);
    const m = r.mentions ?? {};
    const mentions = [m.donnees, m.mise_a_jour, m.avertissement_juridique].filter(Boolean);
    blocs.push(section("À savoir", ...mentions.map((t) => el("p", {}, t))));
    apropos.replaceChildren(...blocs);
  }

  async function chargerAPropos() {
    if (charge) return;
    try {
      const r = await pont.appeler("reglages.a_propos");
      if (!r || r.ok === false) throw new Error("refus");
      rendreAPropos(r);
      charge = true;
    } catch {
      apropos.replaceChildren(el("p", { role: "alert" }, "Ces informations n'ont pas pu être lues."));
    }
  }

  racine.append(liste, panneaux.general, panneaux.retours, panneaux.apropos);
  conteneur.replaceChildren(racine);
  choisir("general");
  afficherTaille();

  // État initial : taille mémorisée côté application, et Mode.
  (async () => {
    try {
      const r = await pont.appeler("reglages.lire");
      const t = r?.reglages?.taille_texte;
      if (CRANS_TAILLE.includes(t) && memoire.lire("echelle", null) === null) fixerTaille(t);
      enregistree = tailleCourante();
    } catch {
      /* le pont ne répond pas : valeurs locales */
    }
    try {
      const e = await pont.appeler("mode.etat");
      horsLigne.checked = Boolean(e?.force);
    } catch {
      /* idem */
    }
  })();

  // Rouvrir « Paramètres » relit « À propos » (la Liste blanche peut avoir changé à la relance).
  document.getElementById("bouton-parametres")?.addEventListener("click", () => {
    charge = false;
    if (!panneaux.apropos.hidden) chargerAPropos();
  });
}
