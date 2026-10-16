// Passages signalés du Langage clair (FR-16, UX-DR12, décision Q11).
// `LC.md` demande de signaler « après le texte réécrit » les passages gardés tels quels, sans
// format structuré, et il n'est pas modifié. On cherche donc, par une règle tolérante mais
// prudente, une section finale : un intitulé reconnaissable suivi d'une liste. Sans elle, ou au
// moindre doute, le texte est affiché tel quel, sans erreur et sans rien couper.
// Tout contenu entre dans le DOM par `textContent` (jamais de HTML construit). L'infobulle fait
// partie du contenu du passage : pas d'`aria-describedby`, elle ne serait pas lue deux fois.

export const INFOBULLE = "Terme juridique conservé tel quel";

const INTRO =
  /^(?:(?:les|des|ces|mes)\s+)?(?:passages?|termes?|expressions?|extraits?|mentions?|formulations?)\b.*\b(?:conserv|gard|laiss|inchang|non\s+simplifi|signal|tel\s+quel)/i;
const LONGUEUR_MAX_INTRO = 160;
const LONGUEUR_MIN_PASSAGE = 3;
const PUCE = /^\s*(?:[-*•–]|\d+[.)])\s+/;
const DECOR = "*_ \t\r\n";

/** Retire les caractères de `retire` en fin de chaîne (boucle : pas de regex `x+$` quadratique). */
function rognerFin(texte, retire) {
  let fin = texte.length;
  while (fin > 0 && retire.includes(texte[fin - 1])) fin--;
  return texte.slice(0, fin);
}

function rognerDebut(texte, retire) {
  let debut = 0;
  while (debut < texte.length && retire.includes(texte[debut])) debut++;
  return texte.slice(debut);
}

function nettoyerLigne(ligne) {
  const sansTitre = ligne.trim().replace(/^(?:>+|#{1,6})\s*/, "");
  return rognerFin(rognerDebut(sansTitre, DECOR), DECOR).trim();
}

function nettoyerPassage(ligne) {
  let t = ligne.trim().replace(/^(?:[-*•–]|\d+[.)])\s+/, "");
  t = rognerFin(rognerDebut(t, DECOR), DECOR);
  t = t.replace(/^(?:«|"|“|')\s*/, "");
  t = rognerFin(t, " \t»\"”'");
  return rognerFin(t, " \t;,.").trim();
}

function guillemets(texte) {
  return [...texte.matchAll(/«\s*([^»]+?)\s*»|“([^”]+)”/g)].map((m) => (m[1] ?? m[2]).trim());
}

/** Une introduction ressemble à un intitulé : titre Markdown, gras, « … : » ou « … : « x » ». */
function ressembleAUnIntitule(brute, propre) {
  const ligne = brute.trim();
  if (/^#{1,6}\s/.test(ligne) || /^(?:\*\*|__)/.test(ligne)) return true;
  if (propre.endsWith(":")) return true;
  const i = propre.indexOf(":");
  return i >= 0 && guillemets(propre.slice(i + 1)).length > 0;
}

/**
 * Sépare le texte réécrit de la section finale des passages signalés.
 * La section doit être la dernière partie du texte : un intitulé reconnaissable, suivi seulement
 * d'une liste à puces ou numérotée (ou de passages entre guillemets sur la même ligne). Au
 * moindre doute, rien n'est coupé.
 * @returns {{corps: string, section: string|null, passages: string[]}} `section` est `null`
 *   quand aucune section n'est reconnue.
 */
export function extrairePassages(brut) {
  const texte = String(brut ?? "");
  const lignes = texte.split(/\r?\n/);
  let i = lignes.length - 1;
  let puces = 0;
  while (i >= 0 && (!lignes[i].trim() || PUCE.test(lignes[i]))) {
    if (lignes[i].trim()) puces++;
    i--;
  }
  const aucune = { corps: texte, section: null, passages: [] };
  if (i < 1) return aucune; // pas d'intitulé, ou rien avant lui
  const intro = nettoyerLigne(lignes[i]);
  const avantDeuxPoints = intro.split(":")[0];
  if (
    !intro ||
    avantDeuxPoints.length > LONGUEUR_MAX_INTRO ||
    !INTRO.test(avantDeuxPoints) ||
    !ressembleAUnIntitule(lignes[i], intro) ||
    !lignes.slice(0, i).some((l) => l.trim())
  ) {
    return aucune;
  }
  const reste = intro.includes(":") ? intro.slice(intro.indexOf(":") + 1) : "";
  const candidats = guillemets(reste);
  if (puces === 0 && candidats.length === 0) return aucune; // un intitulé sans rien derrière
  for (const ligne of lignes.slice(i + 1).filter((l) => l.trim())) {
    const entre = guillemets(ligne);
    candidats.push(...(entre.length ? entre : [nettoyerPassage(ligne)]));
  }
  const passages = [...new Set(candidats.filter((p) => p.length >= LONGUEUR_MIN_PASSAGE))];
  return {
    corps: lignes.slice(0, i).join("\n").trimEnd(),
    section: lignes.slice(i).join("\n").trim(),
    passages,
  };
}

/**
 * Plages `[début, fin)` de la première occurrence de chaque passage, sans chevauchement.
 * La recherche insensible à la casse passe par une RegExp et non par `toLowerCase`, qui peut
 * changer la longueur de la chaîne (« İ ») et décaler les indices.
 */
function plages(corps, passages) {
  const brutes = [];
  for (const passage of passages) {
    const m = new RegExp(passage.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "i").exec(corps);
    if (m) brutes.push([m.index, m.index + m[0].length]);
  }
  brutes.sort((a, b) => a[0] - b[0] || b[1] - a[1]);
  const retenues = [];
  for (const p of brutes) {
    if (!retenues.length || p[0] >= retenues.at(-1)[1]) retenues.push(p);
  }
  return retenues;
}

function creerPassage(texte, infobulle) {
  const marque = document.createElement("span");
  marque.className = "flagged-passage";
  marque.tabIndex = 0;
  marque.append(texte);
  const bulle = document.createElement("span");
  bulle.className = "infobulle";
  bulle.setAttribute("role", "tooltip");
  bulle.textContent = infobulle;
  marque.append(bulle);
  // WCAG 1.4.13 : Échap ferme l'infobulle sans déplacer le focus.
  marque.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && marque.matches(":focus-within")) {
      marque.dataset.ferme = "";
      e.stopPropagation();
    }
  });
  const rouvrir = () => delete marque.dataset.ferme;
  marque.addEventListener("blur", rouvrir);
  marque.addEventListener("mouseleave", rouvrir);
  return marque;
}

/**
 * Rend le Résultat de Langage clair dans `zone` : texte réécrit avec les passages surlignés
 * (`flagged-passage`, infobulle au survol et au focus), puis la section d'origine en note.
 * @returns {string} Le texte brut à copier : le texte réécrit seul, sans surlignage ni section
 *   de signalement ; le texte entier si aucune section n'est reconnue.
 */
export function rendrePassagesSignales(zone, brut, infobulle = INFOBULLE) {
  const { corps, section, passages } = extrairePassages(brut);
  if (section === null) {
    zone.textContent = corps;
    return corps;
  }
  const texte = document.createElement("div");
  texte.className = "resultat-texte";
  let curseur = 0;
  for (const [debut, fin] of plages(corps, passages)) {
    texte.append(corps.slice(curseur, debut), creerPassage(corps.slice(debut, fin), infobulle));
    curseur = fin;
  }
  texte.append(corps.slice(curseur));
  const note = document.createElement("div");
  note.className = "resultat-passages";
  note.textContent = section;
  zone.replaceChildren(texte, note);
  return corps;
}
