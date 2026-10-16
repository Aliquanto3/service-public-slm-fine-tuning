// Tableau de données (`data-table`) rendu depuis un `ResultatOutil`, jamais depuis le texte de la réponse.
// Formes acceptées : `{colonnes, lignes}` (ou `{columns, rows}`), et le texte MCP de `query_resource_data`
// (« Dataset: … », « Row n: », champs « clé: valeur » indentés de quatre espaces).

import { confirmer, copierTexte, dateLisible } from "./copie.js";

export const PLAFOND_LIGNES = 50;

/** Texte des éléments `text` d'un résultat MCP (`{content: [...]}`), ou chaîne telle quelle. */
export function texteDuResultat(resultat) {
  if (typeof resultat === "string") return resultat;
  if (!resultat || !Array.isArray(resultat.content)) return "";
  return resultat.content
    .filter((e) => e && e.type === "text" && typeof e.text === "string")
    .map((e) => e.text)
    .join("\n");
}

function depuisTexte(texte) {
  if (!/^\s*Row \d+:/m.test(texte)) return null;
  const jeu = /^Dataset: (.+?)(?: \(ID: [^)]*\))?\s*$/m.exec(texte)?.[1] ?? null;
  const lignes = [];
  let courante = null;
  for (const brut of texte.split("\n")) {
    if (/^\s*Row \d+:\s*$/.test(brut)) {
      courante = [];
      lignes.push(courante);
      continue;
    }
    const champ = courante && /^ {4}([^\s:][^:]*): ?(.*)$/.exec(brut);
    if (champ) courante.push([champ[1], champ[2]]);
    else if (courante && brut.trim() === "") courante = null;
  }
  if (!lignes.length) return null;
  const colonnes = lignes[0].map(([cle]) => cle);
  return {
    colonnes,
    lignes: lignes.map((ligne) => {
      const dict = new Map(ligne);
      return colonnes.map((c) => dict.get(c) ?? "");
    }),
    jeu,
    partiel: /More data available/.test(texte),
  };
}

/** Renvoie `{colonnes, lignes, jeu, partiel}` ou `null` si le résultat n'est pas tabulaire. */
export function extraireTableau(resultat) {
  if (typeof resultat === "string") return depuisTexte(resultat);
  if (!resultat || typeof resultat !== "object") return null;
  const colonnes = resultat.colonnes ?? resultat.columns;
  const lignes = resultat.lignes ?? resultat.rows;
  if (Array.isArray(colonnes) && Array.isArray(lignes) && colonnes.length) {
    return {
      colonnes: colonnes.map(String),
      lignes: lignes.map((l) => colonnes.map((c, i) => String((Array.isArray(l) ? l[i] : l?.[c]) ?? ""))),
      jeu: resultat.jeu ?? resultat.dataset ?? null,
      partiel: Boolean(resultat.partiel),
    };
  }
  return depuisTexte(texteDuResultat(resultat));
}

function nettoyer(cellule) {
  return String(cellule).replace(/[\t\r\n]+/g, " ");
}

/** Ligne de source du pied de tableau. */
export function ligneSource(jeu, maintenant = new Date()) {
  return `Source : data.gouv.fr, ${jeu || "jeu de données"}, consulté le ${dateLisible(maintenant)}`;
}

/** Texte tabulé (collable dans Excel ou Word) suivi de la ligne de source. */
export function texteTabule(tableau, lignes, source) {
  const corps = [tableau.colonnes, ...lignes].map((l) => l.map(nettoyer).join("\t"));
  return [...corps, source].join("\n");
}

/** Construit la figure du tableau : grille plafonnée à 50 lignes, mention d'extrait, « Copier le tableau ». */
export function creerTableau(tableau) {
  const figure = document.createElement("figure");
  figure.className = "tableau-donnees";
  const affichees = tableau.lignes.slice(0, PLAFOND_LIGNES);
  const source = ligneSource(tableau.jeu);
  const defilement = document.createElement("div");
  defilement.className = "data-table-defilement";
  defilement.tabIndex = 0; // défilement horizontal au clavier
  defilement.setAttribute("role", "region");
  defilement.setAttribute("aria-label", "Tableau de données");
  const table = document.createElement("table");
  table.className = "data-table";
  const tete = table.createTHead().insertRow();
  for (const c of tableau.colonnes) {
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = c;
    tete.append(th);
  }
  const corps = table.createTBody();
  for (const ligne of affichees) {
    const tr = corps.insertRow();
    for (const valeur of ligne) {
      const td = tr.insertCell();
      td.textContent = valeur;
      td.title = valeur;
    }
  }
  defilement.append(table);
  const pied = document.createElement("figcaption");
  pied.className = "data-table-pied";
  if (tableau.lignes.length > PLAFOND_LIGNES || tableau.partiel) {
    const mention = document.createElement("p");
    mention.className = "extrait-mention";
    mention.textContent = `Extrait : ${affichees.length} premières lignes`;
    pied.append(mention);
  }
  const ligneDeSource = document.createElement("p");
  ligneDeSource.className = "data-table-source";
  ligneDeSource.textContent = source;
  const actions = document.createElement("div");
  actions.className = "tableau-actions";
  const copier = document.createElement("button");
  copier.type = "button";
  copier.className = "bouton-secondaire";
  copier.textContent = "Copier le tableau";
  copier.addEventListener("click", async () => {
    const ok = await copierTexte(texteTabule(tableau, affichees, source));
    confirmer(actions, ok ? "Tableau copié" : "Copie impossible");
  });
  actions.append(copier);
  pied.append(ligneDeSource, actions);
  figure.append(defilement, pied);
  return figure;
}
