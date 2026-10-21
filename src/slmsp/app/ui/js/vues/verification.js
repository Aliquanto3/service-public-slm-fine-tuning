// Vue « verification » (story 13.6, FR-12, UX-DR24) : bouton secondaire « Vérifier en ligne » sous
// une réponse Question, en Mode connecté seulement, jamais lancé automatiquement.
// Contrat du pont : `verification.verifier(reponse, sources[, modele_repondant])` (voir
// `app/pont/verification.py`) ; le modèle qui a répondu vérifie (story 17.4).
// Tout texte entre dans le DOM par `textContent`. Libellés d'interface : à confirmer par Anaël.

import { annoncer } from "../socle/annonces.js";
import { dateLisible } from "../composants/copie.js";
import { urlOuvrable } from "../composants/sources.js";

/** Même borne que le pont (`REPONSE_MAX_CARACTERES`, harnais) : au-delà, aucun appel. */
export const REPONSE_MAX_CARACTERES = 20000;
/** Délai minimal avant de vérifier de nouveau la même réponse. */
export const DELAI_REVERIFICATION_MS = 30000;

export const LIBELLES = {
  bouton: "Vérifier en ligne",
  enCours: "Vérification en cours…",
  extrait: "Passage de la page",
  impossible: "La vérification n'a pas pu être lancée.",
  generationEnCours: "Une réponse est en cours : réessayez à la fin de celle-ci.",
  tropLongue: "Cette réponse est trop longue pour être vérifiée en ligne.",
  pageParDefaut: "la page officielle",
};

/** Source de l'Index que la réponse cite par `[n]` et que l'on peut vérifier (https). */
export function sourceVerifiable(sources, brut) {
  return (sources ?? []).some(
    (s) =>
      s &&
      s.origine === "index" &&
      Number.isInteger(s.numero) &&
      urlOuvrable(s.url) &&
      String(brut ?? "").includes(`[${s.numero}]`),
  );
}

function el(nom, classe, texte) {
  const e = document.createElement(nom);
  if (classe) e.className = classe;
  if (texte !== undefined) e.textContent = texte;
  return e;
}

/** Texte du verdict affiché et annoncé. */
export function texteVerdict(v) {
  if (v.verdict === "concordant") {
    const date = dateLisible(v.date_consultation);
    return `Vérifié sur ${v.titre || LIBELLES.pageParDefaut}${date ? ` le ${date}` : ""} : concordant`;
  }
  if (v.verdict === "difference") return `Différence relevée : ${v.phrase}`;
  return v.phrase || LIBELLES.impossible;
}

/**
 * Bloc de vérification d'une réponse.
 * @param {object} o `reponse` (de `creerReponse`), `pont`, `horsLigne()`, `eligible()` (réponse
 *   terminée sans échec), `surSources()` (le panneau Sources doit être redessiné).
 * @returns {{el: HTMLElement, rafraichir: () => void}}
 */
export function creerVerification({ reponse, pont, horsLigne, eligible, surSources }) {
  const racine = el("div", "verification");
  let bouton = null;
  let resultat = null; // { zone, brut } : verdict affiché pour ce texte de réponse
  let essai = 0; // invalide une vérification devenue sans objet (Mode, nouvelle réponse)
  let enCours = false;
  let libreA = 0; // pas de nouvelle vérification avant cette date (ms)
  let minuteur = null;

  const effacer = () => {
    essai += 1;
    enCours = false;
    libreA = 0;
    clearTimeout(minuteur);
    resultat = null;
    bouton = null;
    racine.replaceChildren();
  };

  function ajouterSource(evenements) {
    const page = evenements.find((e) => e?.type === "sources")?.sources?.[0];
    if (!page || typeof page.titre !== "string") return;
    const autres = reponse.sources.filter((s) => !(s.origine === "verification" && s.url === page.url));
    reponse.fixerSources([...autres, page]);
    surSources?.();
  }

  function afficher(zone, verdict, texte) {
    zone.className = `verification-resultat verification-${verdict.verdict}`;
    if (verdict.verdict !== "concordant") zone.classList.add("callout", "callout-warning");
    const p = el("p", null, texte);
    zone.replaceChildren(p);
    if (verdict.extrait) {
      const detail = el("details");
      detail.append(el("summary", null, LIBELLES.extrait), el("p", "verification-extrait", verdict.extrait));
      zone.append(detail);
    }
  }

  async function lancer() {
    // `aria-disabled` (et non `disabled`) : le bouton garde le focus clavier pendant l'attente.
    if (enCours || !bouton || Date.now() < libreA) return;
    const mon = ++essai;
    const brut = reponse.brut;
    const bouton0 = bouton;
    resultat?.zone.remove();
    if (brut.length > REPONSE_MAX_CARACTERES) {
      const zone = el("div", "verification-resultat verification-indisponible callout callout-warning");
      zone.append(el("p", null, LIBELLES.tropLongue));
      racine.append(zone);
      resultat = { zone, brut };
      annoncer(LIBELLES.tropLongue);
      return;
    }
    enCours = true;
    bouton.setAttribute("aria-disabled", "true");
    bouton.setAttribute("aria-busy", "true");
    const zone = el("div", "verification-resultat verification-attente");
    zone.setAttribute("role", "status");
    zone.textContent = LIBELLES.enCours;
    racine.append(zone);
    resultat = { zone, brut };
    let charge = null;
    try {
      const args = ["verification.verifier", brut, reponse.sources];
      if (typeof reponse.modeleRepondant === "string") args.push(reponse.modeleRepondant);
      charge = await pont.appeler(...args);
    } catch {
      charge = null;
    }
    if (mon !== essai) return; // devenue sans objet : rien n'est affiché
    enCours = false;
    const surBouton = document.activeElement === bouton0;
    bouton0.removeAttribute("aria-busy");
    // Délai avant de revérifier la même page ; le bouton reste `aria-disabled` jusque-là.
    libreA = Date.now() + DELAI_REVERIFICATION_MS;
    minuteur = setTimeout(() => bouton0.removeAttribute("aria-disabled"), DELAI_REVERIFICATION_MS);
    const evenements = charge?.ok === true && Array.isArray(charge.evenements) ? charge.evenements : [];
    const verdict = evenements.find((e) => e?.type === "verification");
    zone.removeAttribute("role");
    zone.tabIndex = -1;
    let texte;
    if (verdict) {
      texte = texteVerdict(verdict);
      afficher(zone, verdict, texte);
      ajouterSource(evenements);
    } else {
      texte = charge?.erreur?.code === "generation-en-cours" ? LIBELLES.generationEnCours : LIBELLES.impossible;
      afficher(zone, { verdict: "indisponible" }, texte);
      libreA = 0; // rien n'a été consulté : on peut réessayer tout de suite
      clearTimeout(minuteur);
      bouton0.removeAttribute("aria-disabled");
    }
    // Une seule annonce : le focus sur le résultat (s'il était sur le bouton) ou la région `aria-live`.
    if (surBouton) zone.focus();
    else annoncer(texte);
  }

  function rafraichir() {
    const ok = !horsLigne() && eligible() && sourceVerifiable(reponse.sources, reponse.brut);
    if (!ok || (resultat && resultat.brut !== reponse.brut)) {
      if (bouton || resultat) effacer();
      if (!ok) return;
    }
    if (bouton) return;
    bouton = el("button", "bouton-secondaire", LIBELLES.bouton);
    bouton.type = "button";
    bouton.addEventListener("click", lancer);
    racine.prepend(bouton);
  }

  return { el: racine, rafraichir };
}

/** Le bloc est monté par la vue Question : l'ancre transverse reste vide. */
export function monter(conteneur) {
  conteneur.replaceChildren();
}
