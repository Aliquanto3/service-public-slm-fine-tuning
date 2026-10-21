// Vue « Modèles » (story 17.5b) : comparatif en lecture seule des modèles, lu par le pont
// (`modeles.comparatif_modeles`, JSON embarqué, aucun réseau). Toutes les valeurs du JSON
// passent par `textContent`, jamais par affectation de HTML brut.
import { annoncer } from "../socle/annonces.js";

const TACHES = [
  ["Q", "Question"],
  ["RD", "Recherche de données"],
  ["CR", "Compte rendu"],
  ["LC", "Langage clair"],
  ["CO", "Correction"],
  ["RE", "Résumé"],
  ["CT", "Courrier type"],
  ["NR", "Non-régression"],
];
const EMPLACEMENTS = { poste: "Poste de l'Agent", cloud: "Cloud" };
const LIBELLE_ACTIF = "Modèle actif sur ce poste";
const LIBELLE_EXTERNE = "Fournisseur externe configuré";

function el(nom, attributs = {}, texte) {
  const e = document.createElement(nom);
  for (const [cle, valeur] of Object.entries(attributs)) e.setAttribute(cle, valeur);
  if (texte !== undefined) e.textContent = texte;
  return e;
}

const absent = (v) => v == null || !Number.isFinite(Number(v));
const nombre = (v, d = 1) =>
  absent(v) ? "non calculé" : Number(v).toLocaleString("fr-FR", { minimumFractionDigits: d, maximumFractionDigits: d });
const signe = (v, d = 1) => (!absent(v) && v > 0 ? "+" : "") + nombre(v, d);

export function texteQualite(m) {
  const q = m.qualite;
  if (!q || absent(q.score)) return "non mesurée";
  return absent(q.bruit_items) ? nombre(q.score) : `${nombre(q.score)} ± ${nombre(q.bruit_items)}`;
}

export function texteEcart(m) {
  if (m.reference) return "Référence";
  const e = m.ecart_reference?.qualite;
  if (!e) return "—";
  if (absent(e.ecart) || absent(e.ic_bas) || absent(e.ic_haut)) return "non calculé";
  return `${signe(e.ecart)} (IC 95 % : ${nombre(e.ic_bas)} à ${nombre(e.ic_haut)})`;
}

export function texteCout(m) {
  const c = m.cout ?? {};
  if (m.emplacement === "poste") return "0 € d'API";
  if (absent(c.eur_pour_1000_demandes)) return "non chiffré";
  return `${nombre(c.eur_pour_1000_demandes, 2)} € / 1 000 demandes, relances comprises`;
}

export function texteVitesse(m) {
  const v = m.vitesse;
  if (!v || absent(v.debit_tokens_s)) return "non mesurée";
  const premier = absent(v.premier_token_ms) ? "" : ` ; premier token ${nombre(v.premier_token_ms, 0)} ms`;
  const suffixe = v.origine === "cloud" ? " (via réseau)" : v.origine === "poste" ? " (poste de développement)" : "";
  return `${nombre(v.debit_tokens_s)} tokens/s${premier}${suffixe}`;
}

export function titreVitesse(m) {
  const o = m.vitesse?.origine;
  if (o === "cloud") return "Mesurée via le réseau depuis le poste de développement";
  if (o === "poste") return "Mesurée sur le poste de développement, pas sur le PC cible";
  return "";
}

export function texteRam(m) {
  const r = m.vitesse?.ram_max_go;
  return absent(r) ? "—" : `${nombre(r)} Go`;
}

/** Colonnes et valeurs de tri ; `null` passe toujours en fin de liste. */
export const COLONNES = [
  { id: "modele", titre: "Modèle", cle: (m) => m.libelle },
  { id: "emplacement", titre: "Où il tourne", cle: (m) => EMPLACEMENTS[m.emplacement] ?? m.emplacement },
  { id: "qualite", titre: "Qualité (± bruit)", cle: (m) => m.qualite?.score ?? null },
  { id: "ecart", titre: "Écart à la référence", cle: (m) => (m.reference ? 0 : (m.ecart_reference?.qualite?.ecart ?? null)) },
  { id: "cout", titre: "Coût", cle: (m) => (m.emplacement === "poste" ? 0 : (m.cout?.eur_pour_1000_demandes ?? null)) },
  { id: "vitesse", titre: "Vitesse", cle: (m) => m.vitesse?.debit_tokens_s ?? null },
  { id: "ram", titre: "RAM du poste", cle: (m) => m.vitesse?.ram_max_go ?? null },
  { id: "licence", titre: "Licence", cle: (m) => m.licence },
  { id: "hebergement", titre: "Hébergement", cle: (m) => m.hebergement },
];

/** Copie triée de `modeles` selon la colonne `id` (`sens` : 1 croissant, -1 décroissant). */
export function trier(modeles, id, sens) {
  const col = COLONNES.find((c) => c.id === id);
  if (!col) return [...modeles];
  return [...modeles].sort((a, b) => {
    const x = col.cle(a);
    const y = col.cle(b);
    if (x == null && y == null) return 0;
    if (x == null) return 1;
    if (y == null) return -1;
    const r = typeof x === "number" && typeof y === "number" ? x - y : String(x).localeCompare(String(y), "fr");
    return r * sens;
  });
}

/** Badges d'un modèle : modèle local actif, fournisseur externe configuré (lecture seule). */
export function badges(m, { actif, externes = [] }) {
  const liste = [];
  if (m.emplacement === "poste" && actif && m.id === actif) liste.push(LIBELLE_ACTIF);
  const modeleId = m.cout?.prix_mtok?.modele_id;
  if (m.emplacement === "cloud" && modeleId && externes.some((f) => f.modele === modeleId)) {
    liste.push(LIBELLE_EXTERNE);
  }
  return liste;
}

function barres(m) {
  const liste = el("ul", { class: "modeles-barres", "aria-label": `Scores de Tâche de ${m.libelle}` });
  for (const [id, nom] of TACHES) {
    const valeur = m.qualite?.taches?.[id];
    const item = el("li", { class: "modeles-barre" });
    item.append(el("span", { class: "modeles-barre-nom" }, `${nom} (${id})`));
    const piste = el("span", { class: "modeles-barre-piste", "aria-hidden": "true" });
    const rempli = el("span", { class: "modeles-barre-valeur" });
    rempli.style.width = valeur == null ? "0%" : `${Math.max(0, Math.min(100, valeur))}%`;
    piste.append(rempli);
    item.append(piste, el("span", { class: "modeles-barre-chiffre" }, valeur == null ? "non mesuré" : nombre(valeur)));
    liste.append(item);
  }
  return liste;
}

function detail(m) {
  const bloc = el("div", { class: "modeles-detail" });
  bloc.append(el("h3", {}, `Scores de Tâche : ${m.libelle}`), barres(m));
  if (m.note) bloc.append(el("p", { class: "modeles-note" }, m.note));
  if (m.cout?.mention) bloc.append(el("p", { class: "modeles-note" }, `Coût : ${m.cout.mention}.`));
  if (m.vitesse?.mention) bloc.append(el("p", { class: "modeles-note" }, `Vitesse : ${m.vitesse.mention}.`));
  if (m.vitesse?.machine) bloc.append(el("p", { class: "modeles-note" }, `Machine : ${m.vitesse.machine}.`));
  const runs = el("dl", { class: "modeles-runs" });
  const noms = { notation: "Run de notation", generation: "Run de génération", mesure: "Run de mesure" };
  for (const [cle, nom] of Object.entries(noms)) {
    const id = m.runs?.[cle];
    if (!id) continue;
    runs.append(el("dt", {}, nom), el("dd", {}, id));
  }
  bloc.append(runs);
  return bloc;
}

/**
 * Monte la vue dans son conteneur.
 * @param {HTMLElement} conteneur Élément réservé à la vue.
 * @param {object} pont Client du pont (`appeler`).
 */
export function monter(conteneur, pont) {
  const racine = el("div", { class: "modeles" });
  const etat = el("p", { class: "modeles-etat", role: "status" }, "Chargement du comparatif…");
  const corps = el("div", { class: "modeles-corps", hidden: "" });
  racine.append(etat, corps);
  conteneur.append(racine);

  let comparatif = null;
  const contexte = { actif: null, externes: [] };
  let tri = { id: null, sens: 1 };
  const ouverts = new Set();
  const refs = new Map();
  let guideOuvert = true;

  function guide() {
    const d = el("details", { class: "modeles-guide" });
    d.open = guideOuvert;
    d.addEventListener("toggle", () => {
      guideOuvert = d.open;
    });
    d.append(el("summary", {}, "Comment lire ce tableau"));
    const ul = el("ul");
    for (const a of comparatif.avertissements ?? []) ul.append(el("li", {}, a));
    ul.append(
      el("li", {}, "La Qualité ne se compare qu'entre modèles mesurés sur le même jeu et par le même juge."),
      el("li", {}, "Le choix dépend aussi de la confidentialité (le poste garde les données chez l'Agent) et de la disponibilité (le cloud dépend du réseau et de l'hébergeur)."),
    );
    d.append(ul);
    return d;
  }

  function tableau() {
    const t = el("table", { class: "modeles-table" });
    t.append(el("caption", { class: "visuellement-cache" }, "Comparatif des modèles"));
    const tr = el("tr");
    for (const col of COLONNES) {
      const th = el("th", { scope: "col" });
      if (tri.id === col.id) th.setAttribute("aria-sort", tri.sens === 1 ? "ascending" : "descending");
      const b = el("button", { type: "button", class: "modeles-tri", "data-colonne": col.id }, col.titre);
      b.addEventListener("click", () => {
        tri = { id: col.id, sens: tri.id === col.id ? -tri.sens : 1 };
        rendre();
        corps.querySelector(`[data-colonne="${col.id}"]`)?.focus();
        annoncer(`Tri par ${col.titre}, ${tri.sens === 1 ? "croissant" : "décroissant"}`);
      });
      th.append(b);
      tr.append(th);
    }
    const tete = el("thead");
    tete.append(tr);
    t.append(tete);
    const tb = el("tbody");
    refs.clear();
    const modeles = tri.id ? trier(comparatif.modeles, tri.id, tri.sens) : comparatif.modeles;
    for (const m of modeles) {
      const ouvert = ouverts.has(m.id);
      const ligne = el("tr", { class: "modeles-ligne", "data-modele": m.id });
      const detailId = `modeles-detail-${m.id}`;
      const premiere = el("th", { scope: "row" });
      const bascule = el(
        "button",
        { type: "button", class: "modeles-bascule", "aria-expanded": String(ouvert), "aria-controls": detailId },
        m.libelle,
      );
      bascule.addEventListener("click", () => {
        if (ouverts.has(m.id)) ouverts.delete(m.id);
        else ouverts.add(m.id);
        rendre();
        refs.get(m.id)?.focus();
      });
      refs.set(m.id, bascule);
      premiere.append(bascule);
      for (const b of badges(m, contexte)) premiere.append(el("span", { class: "modeles-badge" }, b));
      ligne.append(premiere);
      const cellules = [
        EMPLACEMENTS[m.emplacement] ?? m.emplacement,
        texteQualite(m),
        texteEcart(m),
        texteCout(m),
        texteVitesse(m),
        texteRam(m),
        m.licence,
        m.hebergement,
      ];
      for (const c of cellules) ligne.append(el("td", {}, c ?? "—"));
      const titre = titreVitesse(m);
      if (titre) ligne.children[5].title = titre;
      const sous = el("tr", { id: detailId, class: "modeles-sous" });
      if (!ouvert) sous.hidden = true;
      const td = el("td", { colspan: String(COLONNES.length) });
      td.append(detail(m));
      sous.append(td);
      tb.append(ligne, sous);
    }
    t.append(tb);
    const defilement = el("div", {
      class: "modeles-defilement",
      tabindex: "0",
      role: "region",
      "aria-label": "Tableau comparatif des modèles",
    });
    defilement.append(t);
    return defilement;
  }

  function statutJeu() {
    const s = comparatif.jeu_statut;
    if (!s) return "";
    return ` (${s === "relu-llm" ? "relu par deux LLM, pas encore par un humain" : s})`;
  }

  function rendre() {
    corps.replaceChildren();
    const date = String(comparatif.genere_le ?? "").slice(0, 10);
    const intro = el(
      "p",
      { class: "modeles-intro" },
      `Jeu ${comparatif.jeu_version}${statutJeu()}, juge ${comparatif.juge_principal}, données générées le ${date}. Cliquez sur un modèle pour voir ses Scores de Tâche.`,
    );
    corps.append(intro, guide(), tableau());
    corps.hidden = false;
  }

  async function charger() {
    let r;
    try {
      r = await pont.appeler("modeles.comparatif_modeles");
    } catch {
      r = null;
    }
    if (!r || r.ok === false || !r.comparatif) {
      etat.textContent = r?.erreur?.message ?? "Le comparatif des modèles n'a pas pu être chargé.";
      etat.setAttribute("role", "alert");
      return;
    }
    comparatif = r.comparatif;
    // Badges : informations facultatives, une erreur ne bloque pas le tableau.
    try {
      const m = await pont.appeler("reglages.modeles");
      if (m?.ok) contexte.actif = m.actif ?? null;
    } catch {
      /* sans badge */
    }
    try {
      const f = await pont.appeler("reglages.fournisseurs_externes");
      if (f?.ok) contexte.externes = (f.fournisseurs ?? []).filter((x) => x.actif);
    } catch {
      /* sans badge */
    }
    try {
      rendre();
      etat.hidden = true;
    } catch {
      corps.replaceChildren();
      corps.hidden = true;
      etat.hidden = false;
      etat.textContent = "Comparatif illisible";
      etat.setAttribute("role", "alert");
    }
  }

  charger();
}
