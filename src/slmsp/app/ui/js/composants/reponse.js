// Réponse de l'Assistant : texte au fil de l'eau, puces de citation et actions à la fin (UX-DR5, UX-DR11).
// Tout contenu venant du modèle entre dans le DOM par `textContent` (jamais de HTML construit).

import { annoncer } from "../socle/annonces.js";
import { rendreTexteAvecCitations } from "./citations.js";
import { confirmer, copierTexte } from "./copie.js";
import { creerCarteJeu, extraireJeux } from "./jeu-donnees.js";
import { creerTableau, extraireTableau } from "./tableau.js";

function el(balise, classe, texte) {
  const e = document.createElement(balise);
  if (classe) e.className = classe;
  if (texte !== undefined) e.textContent = texte;
  return e;
}

/**
 * @param {object} opts `pont`, `horsLigne()`, `juridique` (avertissement sous la réponse),
 *   `surPuce(reponse, numero)`, `surRegenerer()`, `surReessayer()`.
 */
export function creerReponse(opts) {
  const racine = el("article", "reponse");
  racine.dataset.reponse = ""; // Échap interrompt la génération quand le focus est ici
  racine.tabIndex = 0;
  racine.setAttribute("aria-label", "Réponse de l'Assistant");

  const repli = el("div", "callout callout-warning repli");
  repli.hidden = true;
  repli.append(el("span", "icone icone-attention"), el("p", null, "data.gouv ne répond pas. Réponse établie à partir du catalogue installé."));
  repli.firstChild.setAttribute("aria-hidden", "true");
  const reessayer = el("button", "bouton-secondaire", "Réessayer");
  reessayer.type = "button";
  reessayer.disabled = true; // actif une fois la génération terminée
  reessayer.addEventListener("click", () => opts.surReessayer());
  repli.append(reessayer);

  const attente = el("p", "attente", "…");
  attente.setAttribute("aria-hidden", "true");
  const texte = el("div", "reponse-texte");
  const notes = el("div", "reponse-notes");
  const pieces = el("div", "reponse-pieces");
  const mention = el("p", "mention-interrompue", "Réponse interrompue");
  mention.hidden = true;
  const echec = el("p", "mention-echec", "Cette réponse n'a pas pu être produite.");
  echec.hidden = true;
  const actions = el("div", "reponse-actions");
  actions.hidden = true;
  const copier = el("button", "bouton-secondaire", "Copier");
  copier.type = "button";
  const regenerer = el("button", "bouton-secondaire", "Régénérer");
  regenerer.type = "button";
  actions.append(copier, regenerer);
  racine.append(repli, attente, texte, notes, pieces, mention, echec, actions);

  const r = {
    el: racine,
    brut: "",
    sources: [],
    etat: "attente", // attente | en-cours | fini
    regenerer,
  };
  const vus = new Set(); // identifiants d'appels d'outil déjà rendus

  r.reinitialiser = () => {
    r.brut = "";
    r.sources = [];
    r.etat = "attente";
    vus.clear();
    texte.replaceChildren();
    notes.replaceChildren();
    pieces.replaceChildren();
    for (const e of racine.querySelectorAll(":scope > .legal-notice")) e.remove();
    for (const e of [repli, mention, echec, actions]) e.hidden = true;
    reessayer.disabled = true;
    copier.hidden = false;
    attente.hidden = false;
    racine.setAttribute("aria-busy", "false");
  };

  r.debut = () => {
    r.reinitialiser();
    r.etat = "en-cours";
    racine.setAttribute("aria-busy", "true");
  };

  r.jeton = (t) => {
    if (r.etat === "fini") return;
    r.etat = "en-cours";
    racine.setAttribute("aria-busy", "true");
    r.brut += t;
    attente.hidden = true;
    texte.textContent = r.brut; // pendant le flux : texte brut, sans puces
  };

  r.fixerSources = (liste) => {
    r.sources = liste.filter((s) => s && typeof s.titre === "string");
  };

  r.avertir = (message) => {
    const n = el("p", "avertissement", message);
    n.setAttribute("role", "note");
    notes.append(n);
  };

  r.signalerRepli = () => {
    repli.hidden = false;
    annoncer("data.gouv ne répond pas. Réponse établie à partir du catalogue installé.");
  };

  r.outil = (evenement) => {
    if (evenement.erreur || vus.has(evenement.id)) return;
    const tableau = extraireTableau(evenement.resultat);
    if (tableau) {
      vus.add(evenement.id);
      pieces.append(creerTableau(tableau));
      return;
    }
    const jeux = extraireJeux(evenement.resultat);
    if (jeux.length) {
      vus.add(evenement.id);
      const liste = el("div", "jeux");
      for (const jeu of jeux) liste.append(creerCarteJeu(jeu, { pont: opts.pont, horsLigne: opts.horsLigne }));
      pieces.append(liste);
    }
  };

  r.terminer = (fin) => {
    r.etat = "fini";
    attente.hidden = true;
    racine.setAttribute("aria-busy", "false");
    rendreTexteAvecCitations(texte, r.brut, r.sources, (n) => opts.surPuce(r, n));
    if (fin.raison === "interrompue") mention.hidden = false;
    if (fin.raison === "longueur") r.avertir("La réponse a été coupée : la longueur maximale est atteinte.");
    if (opts.juridique) {
      const avis = el("p", "legal-notice", "Ne vaut pas avis juridique");
      racine.insertBefore(avis, actions);
    }
    reessayer.disabled = false;
    actions.hidden = false;
    annoncer(fin.raison === "interrompue" ? "Réponse interrompue." : "Réponse terminée.");
  };

  r.echec = () => {
    r.etat = "fini";
    attente.hidden = true;
    racine.setAttribute("aria-busy", "false");
    if (r.brut) rendreTexteAvecCitations(texte, r.brut, r.sources, (n) => opts.surPuce(r, n));
    echec.hidden = false;
    reessayer.disabled = false;
    actions.hidden = false;
    copier.hidden = !r.brut;
  };

  r.copier = async () => {
    if (!r.brut) return;
    const ok = await copierTexte(r.brut);
    confirmer(actions, ok ? "Copié" : "Copie impossible");
  };
  copier.addEventListener("click", () => r.copier());
  regenerer.addEventListener("click", () => opts.surRegenerer());
  return r;
}
