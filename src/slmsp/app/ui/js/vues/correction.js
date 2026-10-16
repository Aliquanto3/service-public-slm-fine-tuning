// Vue Correction (CO), story 13.1 (FR-17, UX-DR13) : volet de rédaction de 12.8 + différences
// visibles. Le calcul des différences est fait côté Python (`redaction_outils.differences`) ;
// ici on ne fait que les afficher, par `textContent` (jamais de HTML construit). Les marques
// `diff-insert` et `diff-delete` se lisent sans la couleur : soulignement, barré, et texte
// réservé aux lecteurs d'écran. Le presse-papiers reçoit toujours le texte corrigé brut.

import { monterRedaction } from "./redaction.js";

function el(balise, classe, texte) {
  const e = document.createElement(balise);
  if (classe) e.className = classe;
  if (texte !== undefined) e.textContent = texte;
  return e;
}

function pluriel(n, mot) {
  return `${n} ${mot}${n > 1 ? "s" : ""}`;
}

/** Rend les segments dans `zone` ; renvoie `{ajouts, suppressions}` (nombre de blocs). */
export function rendreSegments(zone, segments) {
  const noeuds = [];
  let ajouts = 0;
  let suppressions = 0;
  for (const s of segments) {
    if (s.type === "egal") {
      noeuds.push(document.createTextNode(s.texte));
      continue;
    }
    const insertion = s.type === "ajout";
    const marque = el(insertion ? "ins" : "del", insertion ? "diff-insert" : "diff-delete");
    marque.append(
      el("span", "sr-only", insertion ? "[ajout : " : "[suppression : "),
      document.createTextNode(s.texte),
      el("span", "sr-only", "]"),
    );
    if (insertion) ajouts += 1;
    else suppressions += 1;
    noeuds.push(marque);
  }
  zone.replaceChildren(...noeuds);
  return { ajouts, suppressions };
}

/**
 * @param {HTMLElement} conteneur Élément réservé à la vue.
 * @param {object} pont Client du pont (appeler, envoyer, arreter).
 * @param {{bus: object, tache: string}} contexte
 */
export function monter(conteneur, pont, contexte) {
  let jeton = 0; // un calcul de différences périmé (nouvelle génération) est ignoré
  const resume = el("p", "diff-resume");
  resume.setAttribute("role", "status");
  const oublier = () => {
    jeton += 1;
    resume.remove();
  };
  contexte.bus.abonner("generation:debut", ({ tache }) => {
    if (tache === contexte.tache) oublier();
  });
  contexte.bus.abonner("nouvelle", ({ tache }) => {
    if (tache === contexte.tache) oublier();
  });
  monterRedaction(conteneur, pont, contexte, {
    action: "Corriger",
    invite: "Collez le texte à corriger. Je corrige l'orthographe, la grammaire et la ponctuation, et je montre chaque modification.",
    etiquetteResultat: "Texte corrigé",
    rendreResultat(brut, zone, envoi, fin) {
      const avant = envoi?.messages?.[0]?.content;
      const mon = ++jeton;
      zone.textContent = brut; // texte brut en attendant (ou si le calcul échoue)
      // Un texte interrompu ou coupé n'est pas une correction complète : pas de différences.
      if (typeof avant !== "string" || (fin && fin.raison !== "terminee")) return brut;
      Promise.resolve()
        .then(() => pont.appeler("redaction_outils.differences", avant, brut))
        .then((r) => {
          if (mon !== jeton || !zone.isConnected || zone.textContent !== brut) return;
          if (!r || r.ok === false || !Array.isArray(r.segments)) throw new Error("refus");
          if (r.identiques) {
            resume.textContent = "Aucune correction";
          } else {
            const n = rendreSegments(zone, r.segments);
            resume.textContent = `${pluriel(n.ajouts, "ajout")}, ${pluriel(n.suppressions, "suppression")}.`;
          }
          zone.after(resume);
        })
        .catch(() => {
          if (mon !== jeton) return;
          resume.textContent = "Les différences n'ont pas pu être affichées : voici le texte corrigé.";
          zone.after(resume);
        });
      return brut;
    },
  });
}
