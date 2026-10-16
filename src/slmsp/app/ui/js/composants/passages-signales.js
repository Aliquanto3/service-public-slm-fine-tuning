// Passages signalés du Langage clair (FR-16, UX-DR12, décision Q11).
// `LC.md` demande de signaler « après le texte réécrit » les passages gardés tels quels, sans
// format structuré, et il n'est pas modifié. On cherche donc, par une règle tolérante, une ligne
// d'introduction de cette section finale ; sans elle, le texte est affiché tel quel, sans erreur.
// Tout contenu entre dans le DOM par `textContent` (jamais de HTML construit).

export const INFOBULLE = "Terme juridique conservé tel quel";

const INTRO =
  /^(?:(?:les|des|ces|mes)\s+)?(?:passages?|termes?|expressions?|extraits?|mentions?|formulations?)\b.*\b(?:conserv|gard|laiss|inchang|non\s+simplifi|signal|tel\s+quel)/i;
const LONGUEUR_MAX_INTRO = 160;
const LONGUEUR_MIN_PASSAGE = 3;

function nettoyerLigne(ligne) {
  return ligne
    .trim()
    .replace(/^(?:>+|#{1,6})\s*/, "")
    .replace(/^[*_\s]+|[*_\s]+$/g, "")
    .trim();
}

function nettoyerPassage(ligne) {
  return ligne
    .trim()
    .replace(/^(?:[-*•–]|\d+[.)])\s+/, "")
    .replace(/^[*_\s]+|[*_\s]+$/g, "")
    .replace(/^(?:«|"|“|')\s*|\s*(?:»|"|”|')$/g, "")
    .replace(/[\s;,.]+$/, "")
    .trim();
}

function guillemets(texte) {
  return [...texte.matchAll(/«\s*([^»]+?)\s*»|“([^”]+)”/g)].map((m) => (m[1] ?? m[2]).trim());
}

/**
 * Sépare le texte réécrit de la section finale des passages signalés.
 * @returns {{corps: string, section: string|null, passages: string[]}} `section` est `null`
 *   quand aucune introduction n'est reconnue.
 */
export function extrairePassages(brut) {
  const lignes = String(brut ?? "").split(/\r?\n/);
  let debut = -1;
  for (let i = lignes.length - 1; i > 0; i--) {
    const propre = nettoyerLigne(lignes[i]);
    const avantDeuxPoints = propre.split(":")[0];
    if (propre && avantDeuxPoints.length <= LONGUEUR_MAX_INTRO && INTRO.test(avantDeuxPoints)) {
      if (lignes.slice(0, i).some((l) => l.trim())) debut = i;
      break;
    }
  }
  if (debut < 0) return { corps: String(brut ?? ""), section: null, passages: [] };

  const intro = nettoyerLigne(lignes[debut]);
  const reste = intro.includes(":") ? intro.slice(intro.indexOf(":") + 1) : "";
  const candidats = guillemets(reste);
  const suite = lignes.slice(debut + 1).filter((l) => l.trim());
  for (const ligne of suite) {
    const entre = guillemets(ligne);
    candidats.push(...(entre.length ? entre : [nettoyerPassage(ligne)]));
  }
  const passages = [...new Set(candidats.filter((p) => p.length >= LONGUEUR_MIN_PASSAGE))];
  return {
    corps: lignes.slice(0, debut).join("\n").replace(/\s+$/, ""),
    section: lignes.slice(debut).join("\n").trim(),
    passages,
  };
}

/** Plages `[début, fin)` de la première occurrence de chaque passage, sans chevauchement. */
function plages(corps, passages) {
  const brutes = [];
  const bas = corps.toLowerCase();
  for (const passage of passages) {
    const i = bas.indexOf(passage.toLowerCase());
    if (i >= 0) brutes.push([i, i + passage.length]);
  }
  brutes.sort((a, b) => a[0] - b[0] || b[1] - a[1]);
  const retenues = [];
  for (const p of brutes) {
    if (!retenues.length || p[0] >= retenues.at(-1)[1]) retenues.push(p);
  }
  return retenues;
}

let compteur = 0;

function creerPassage(texte, infobulle) {
  const marque = document.createElement("span");
  marque.className = "flagged-passage";
  marque.tabIndex = 0;
  const id = `infobulle-passage-${++compteur}`;
  marque.setAttribute("aria-describedby", id);
  marque.append(texte);
  const bulle = document.createElement("span");
  bulle.className = "infobulle";
  bulle.id = id;
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
