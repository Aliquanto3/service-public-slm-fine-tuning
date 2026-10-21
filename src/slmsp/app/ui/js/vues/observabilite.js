// Vue « Observabilité » (story 17.6, menu « Plus ») : pour la DSI, totaux du jour et du mois
// par modèle et par fournisseur, consommation des plafonds, derniers appels (sans contenu),
// export CSV et méthode des estimations. Lit `observabilite.synthese` et `observabilite.methode`
// ; toutes les valeurs passent par `textContent`.
import { annoncer } from "../socle/annonces.js";
import { texteCout, texteImpact } from "../composants/details-appel.js";

function el(nom, attributs = {}, texte) {
  const e = document.createElement(nom);
  for (const [cle, valeur] of Object.entries(attributs)) e.setAttribute(cle, valeur);
  if (texte !== undefined) e.textContent = texte;
  return e;
}

const nf = (v, d = 0) =>
  v == null || !Number.isFinite(Number(v))
    ? "—"
    : Number(v).toLocaleString("fr-FR", { minimumFractionDigits: d, maximumFractionDigits: d });

const COLONNES = [
  ["Fournisseur", (l) => l.fournisseur],
  ["Modèle", (l) => l.modele],
  ["Appels", (l) => nf(l.appels) + (l.sauts ? ` (+${l.sauts} sauté${l.sauts > 1 ? "s" : ""})` : "")],
  ["Tokens entrée", (l) => nf(l.tokens_entree) + (l.estime ? " (estimés en partie)" : "")],
  ["Tokens sortie", (l) => nf(l.tokens_sortie)],
  ["Coût", (l) => texteCout({ ...l, local: l.fournisseur === "local" })],
  ["Énergie", (l) => texteImpact(l.energie_wh, l.energie_wh_bas, l.energie_wh_haut, "Wh")],
  ["CO₂e", (l) => texteImpact(l.co2e_g, l.co2e_g_bas, l.co2e_g_haut, "g")],
  ["Débit moyen", (l) => (l.debit_tokens_s == null ? "—" : `${nf(l.debit_tokens_s, 1)} tokens/s`)],
];

function tableau(legende, lignes, colonnes = COLONNES) {
  if (!lignes.length) return el("p", { class: "observabilite-vide" }, `${legende} : aucun appel.`);
  const table = el("table", { class: "observabilite-table" });
  table.append(el("caption", {}, legende));
  const tete = el("tr");
  for (const [titre] of colonnes) tete.append(el("th", { scope: "col" }, titre));
  const thead = el("thead");
  thead.append(tete);
  table.append(thead);
  const corps = el("tbody");
  for (const l of lignes) {
    const tr = el("tr");
    for (const [, valeur] of colonnes) tr.append(el("td", {}, String(valeur(l))));
    corps.append(tr);
  }
  table.append(corps);
  return table;
}

const DERNIERS = [
  ["Heure (UTC)", (m) => String(m.horodatage ?? "").slice(0, 19).replace("T", " ")],
  ["Tâche", (m) => m.tache ?? "—"],
  ...COLONNES.slice(0, 2),
  ["Tokens", (m) => `${nf(m.tokens_entree)} / ${nf(m.tokens_sortie)}${m.estime ? " (estimés)" : ""}`],
  ["Durée", (m) => `${nf((m.duree_ms ?? 0) / 1000, 1)} s`],
  ["Coût", (m) => texteCout({ ...m, local: m.fournisseur === "local" })],
  ["CO₂e", (m) => texteImpact(m.co2e_g, null, null, "g")],
  ["État", (m) => m.motif ?? "terminé"],
];

function plafonds(liste) {
  if (!liste.length) return el("p", { class: "observabilite-vide" }, "Aucun fournisseur externe : aucun plafond à suivre.");
  const ul = el("ul", { class: "observabilite-plafonds" });
  for (const p of liste) {
    const li = el("li");
    const id = `plafond-${p.hote}`.replace(/[^a-zA-Z0-9-]/g, "-");
    const etiquette = el("span", { id }, `${p.libelle} : ${nf(p.cumul_eur, 4)} € sur ${nf(p.plafond_eur, 2)} €`);
    const barre = el("progress", { max: String(p.plafond_eur || 1), value: String(Math.min(p.cumul_eur, p.plafond_eur || 1)), "aria-labelledby": id });
    li.append(etiquette, barre);
    if (p.plafond_eur === 0) li.append(el("span", { class: "observabilite-alerte" }, " fournisseur désactivé (plafond 0 €)"));
    if (p.sauts) li.append(el("span", { class: "observabilite-alerte" }, ` ${p.sauts} appel${p.sauts > 1 ? "s" : ""} sauté${p.sauts > 1 ? "s" : ""} ce mois-ci (plafond ou tarif)`));
    ul.append(li);
  }
  return ul;
}

function rendreMethode(m) {
  if (!m?.disponible) return [el("p", {}, "Méthode indisponible.")];
  const blocs = [el("p", {}, m.version)];
  for (const [titre, textes] of [["Impact", m.formules], ["Coût", m.cout], ["Plafond", m.plafond]]) {
    blocs.push(el("h4", {}, titre));
    for (const t of textes ?? []) blocs.push(el("p", {}, t));
  }
  blocs.push(el("h4", {}, "Intensité carbone retenue"));
  const ul = el("ul");
  for (const z of m.zones ?? []) ul.append(el("li", {}, `${z.libelle} : ${nf(z.intensite_g_kwh)} g CO₂e/kWh (${z.source})`));
  blocs.push(ul);
  return blocs;
}

export function monter(conteneur, pont, contexte = {}) {
  const racine = el("div", { class: "observabilite" });
  const avis = el("p", { class: "callout observabilite-avis", role: "note" },
    "Les coûts et impacts environnementaux sont des estimations (méthode ci-dessous). Aucun contenu de demande ou de réponse n'est enregistré ici.");
  const actions = el("div", { class: "observabilite-actions" });
  const actualiser = el("button", { type: "button", class: "bouton-secondaire" }, "Actualiser");
  const exporter = el("button", { type: "button", class: "bouton-secondaire" }, "Exporter en CSV");
  const etat = el("output", { class: "observabilite-etat", "aria-live": "polite" });
  actions.append(actualiser, exporter, etat);
  const corps = el("div", { class: "observabilite-corps" });
  const methode = el("details", { class: "observabilite-methode" });
  methode.append(el("summary", {}, "Méthode et hypothèses"));
  const methodeCorps = el("div");
  methode.append(methodeCorps);
  racine.append(avis, actions, corps, methode);
  conteneur.replaceChildren(racine);

  async function charger() {
    etat.textContent = "Chargement…";
    try {
      const r = await pont.appeler("observabilite.synthese");
      if (!r || r.ok === false) throw new Error("refus");
      const s = r.synthese;
      corps.replaceChildren(
        el("h3", {}, "Plafonds de dépense du mois"),
        plafonds(s.plafonds ?? []),
        el("h3", {}, `Aujourd'hui (${s.jour}, UTC)`),
        tableau("Totaux du jour par modèle", s.par_modele_jour ?? []),
        el("h3", {}, `Mois en cours (${s.mois}, UTC)`),
        tableau("Totaux du mois par modèle", s.par_modele_mois ?? []),
        el("h3", {}, "Derniers appels"),
        tableau("Derniers appels (sans contenu)", s.derniers ?? [], DERNIERS),
      );
      etat.textContent = "";
    } catch {
      etat.textContent = "Mesures indisponibles.";
    }
    try {
      const m = await pont.appeler("observabilite.methode");
      methodeCorps.replaceChildren(...rendreMethode(m?.methode));
    } catch {
      methodeCorps.replaceChildren(el("p", {}, "Méthode indisponible."));
    }
  }

  actualiser.addEventListener("click", () => charger());
  exporter.addEventListener("click", async () => {
    try {
      const r = await pont.appeler("observabilite.exporter_csv");
      if (!r || r.ok === false) throw new Error(r?.erreur?.message ?? "refus");
      etat.textContent = r.enregistre ? `Mesures enregistrées : ${r.nom}.` : "Export annulé.";
    } catch (e) {
      etat.textContent = e instanceof Error && e.message !== "refus" ? e.message : "L'export a échoué.";
    }
    annoncer(etat.textContent);
  });
  // Rechargée à chaque ouverture de l'onglet (le socle émet `tache:active` après le montage).
  if (contexte.bus?.abonner) {
    contexte.bus.abonner("tache:active", ({ tache }) => {
      if (tache === contexte.tache) charger();
    });
  } else charger();
}
