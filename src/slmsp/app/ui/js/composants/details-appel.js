// Ligne « Détails » sous une réponse (story 17.6) : modèle, tokens, durée, coût, énergie et
// CO2e estimés de la réponse (`fin.details`, calculé par le pont, sans contenu). Repliée par
// défaut ; toutes les valeurs passent par `textContent`.

const nf = (v, min = 0, max = min) =>
  Number(v).toLocaleString("fr-FR", { minimumFractionDigits: min, maximumFractionDigits: max });
const connu = (v) => v != null && Number.isFinite(Number(v));

/** Coût en euros : « 0 € » en local, « inconnu » sans tarif. */
export function texteCout(d) {
  if (d.local) return "0 € (modèle local : pas de coût d'API)";
  if (d.mention_cout === "accès gratuit OVH" || String(d.fournisseur ?? "").endsWith("-gratuit")) return "0 € (accès gratuit OVH)";
  if (!connu(d.cout_eur)) return "inconnu (tarif absent)";
  const v = Number(d.cout_eur);
  return v > 0 && v < 0.0001 ? "< 0,0001 €" : `${nf(v, 4, 4)} €`;
}

/** Valeur centrale et fourchette ; « non estimé » sans paramètres du modèle. */
export function texteImpact(centre, bas, haut, unite) {
  if (!connu(centre)) return "non estimé";
  const f = (v) => (Math.abs(v) >= 1 ? nf(v, 1, 1) : nf(v, 0, 3));
  const fourchette = connu(bas) && connu(haut) ? ` (de ${f(bas)} à ${f(haut)})` : "";
  return `${f(centre)} ${unite}${fourchette}`;
}

export function creerDetails(d) {
  if (!d || typeof d !== "object") return null;
  const bloc = document.createElement("details");
  bloc.className = "details-appel";
  const resume = document.createElement("summary");
  resume.textContent = "Détails";
  const liste = document.createElement("dl");
  const estime = d.estime ? " (estimés)" : "";
  const lignes = [
    ["Modèle", (d.modeles ?? []).join(", ") || "—"],
    ["Tokens", `${nf(d.tokens_entree ?? 0)} en entrée, ${nf(d.tokens_sortie ?? 0)} en sortie${estime}`],
    ["Durée", `${nf((d.duree_ms ?? 0) / 1000, 1, 1)} s${d.appels > 1 ? ` (${d.appels} appels)` : ""}`],
    ["Coût", texteCout(d)],
    ["Énergie (estimation)", texteImpact(d.energie_wh, d.energie_wh_bas, d.energie_wh_haut, "Wh")],
    ["CO₂e (estimation)", texteImpact(d.co2e_g, d.co2e_g_bas, d.co2e_g_haut, "g")],
  ];
  if (d.motifs?.length) lignes.push(["Motifs", d.motifs.join(", ")]);
  for (const [terme, valeur] of lignes) {
    const dt = document.createElement("dt");
    dt.textContent = terme;
    const dd = document.createElement("dd");
    dd.textContent = valeur;
    liste.append(dt, dd);
  }
  const note = document.createElement("p");
  note.className = "details-note";
  note.textContent = d.local
    ? "Impact estimé à partir de la puissance moyenne du poste (non instrumenté). Méthode : onglet Observabilité."
    : "Estimations (méthode EcoLogits). Méthode : onglet Observabilité.";
  bloc.append(resume, liste, note);
  return bloc;
}
