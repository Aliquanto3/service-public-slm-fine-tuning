// Vue « verification » (story 13.6, FR-12, UX-DR24) : bouton secondaire « Vérifier en ligne » sous
// une réponse Question, en Mode connecté seulement, jamais lancé automatiquement.
// Contrat du pont : `verification.verifier(reponse, sources)` (voir `app/pont/verification.py`).
// Tout texte entre dans le DOM par `textContent`. Libellés d'interface : à confirmer par Anaël.

import { annoncer } from "../socle/annonces.js";
import { dateLisible } from "../composants/copie.js";
import { urlOuvrable } from "../composants/sources.js";

export const LIBELLES = {
  bouton: "Vérifier en ligne",
  enCours: "Vérification en cours…",
  extrait: "Passage de la page",
  impossible: "La vérification n'a pas pu être lancée.",
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

  const effacer = () => {
    essai += 1;
    enCours = false;
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
    if (enCours || !bouton) return;
    const mon = ++essai;
    enCours = true;
    const brut = reponse.brut;
    bouton.disabled = true;
    bouton.setAttribute("aria-busy", "true");
    const zone = el("div", "verification-resultat verification-attente");
    zone.setAttribute("role", "status");
    zone.textContent = LIBELLES.enCours;
    resultat?.zone.remove();
    racine.append(zone);
    resultat = { zone, brut };
    let charge = null;
    try {
      charge = await pont.appeler("verification.verifier", brut, reponse.sources);
    } catch {
      charge = null;
    }
    if (mon !== essai) return; // devenue sans objet : rien n'est affiché
    enCours = false;
    bouton.disabled = false;
    bouton.removeAttribute("aria-busy");
    const evenements = charge?.ok === true && Array.isArray(charge.evenements) ? charge.evenements : [];
    const verdict = evenements.find((e) => e?.type === "verification");
    zone.removeAttribute("role");
    zone.tabIndex = -1;
    if (verdict) {
      const texte = texteVerdict(verdict);
      afficher(zone, verdict, texte);
      ajouterSource(evenements);
      annoncer(texte);
    } else {
      afficher(zone, { verdict: "indisponible" }, LIBELLES.impossible);
      annoncer(LIBELLES.impossible);
    }
    zone.focus();
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
