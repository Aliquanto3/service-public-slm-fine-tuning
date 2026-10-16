// Vues de rédaction Compte rendu (CR) et Langage clair (LC), story 12.8 (UX-DR10 à DR12).
// `monterRedaction` est le volet de rédaction générique : l'Epic 13 (Correction, Résumé, Courrier
// type, Traduction) le réutilise en lui passant ses propres `options`. Le texte collé ne sort
// jamais du poste (FR-38) : la Tâche n'a aucun outil. Tout contenu venant de l'Agent ou du
// modèle entre dans le DOM par `textContent` (jamais de HTML construit).

import { annoncer } from "../socle/annonces.js";
import { confirmer, copierTexte } from "../composants/copie.js";
import { rendrePassagesSignales } from "../composants/passages-signales.js";

function el(balise, classe, texte) {
  const e = document.createElement(balise);
  if (classe) e.className = classe;
  if (texte !== undefined) e.textContent = texte;
  return e;
}

/** Nombre de mots d'un texte. */
export function compterMots(texte) {
  const mots = String(texte).trim().match(/\S+/g);
  return mots ? mots.length : 0;
}

/** Contrat 12.5 : un refus du pont (`{ok: false, erreur}`) devient un rejet. */
function exigerOk(reponse) {
  if (reponse && reponse.ok === false) {
    throw Object.assign(new Error(reponse.erreur?.message ?? "refus du pont"), { erreur: reponse.erreur });
  }
  return reponse;
}

/**
 * @param {HTMLElement} conteneur Conteneur de la vue.
 * @param {object} pont Client du pont (`envoyer`, `arreter`, `appeler`).
 * @param {{bus: object, tache: string, generationEnCours?: () => boolean}} contexte
 * @param {object} options
 *   `action` : libellé du bouton principal (« Rédiger ») ; `invite` : phrase d'aide du volet Entrée ;
 *   `etiquetteEntree`, `etiquetteResultat` : titres des volets (défaut « Entrée », « Résultat ») ;
 *   `controles` : éléments DOM ajoutés au volet Entrée avant la zone de saisie (choix de langue,
 *   de longueur…) ; `construireEnvoi(texte)` : `{messages, options}` envoyés au pont (défaut : le
 *   texte seul) ; `rendreResultat(brut, zone, envoi, fin)` : rend le Résultat final dans `zone` et renvoie le
 *   texte brut à copier (défaut : texte simple, copié tel quel) ; `dir` : `"rtl"` pour un volet
 *   de Résultat de droite à gauche.
 *   `peutEnvoyer()` : si fournie, remplace « la saisie n'est pas vide » comme condition d'envoi ;
 */
export function monterRedaction(conteneur, pont, { bus, tache, generationEnCours }, options) {
  const id = (nom) => `redaction-${nom}-${tache}`;
  const racine = el("div", "redaction");

  // -- Volet Entrée ---------------------------------------------------------------------------
  const entree = el("section", "editor-pane volet-entree");
  entree.setAttribute("aria-labelledby", id("titre-entree"));
  const titreEntree = el("h2", "volet-titre", options.etiquetteEntree ?? "Entrée");
  titreEntree.id = id("titre-entree");
  const invite = el("p", "volet-invite", options.invite ?? "");
  invite.id = id("invite");
  invite.hidden = !options.invite;
  const saisie = el("textarea", "redaction-saisie");
  saisie.id = id("saisie");
  saisie.rows = 12;
  saisie.setAttribute("aria-labelledby", id("titre-entree"));
  if (options.invite) saisie.setAttribute("aria-describedby", invite.id);
  const compteur = el("p", "compteur-mots", "0 mot");
  const principal = el("button", "bouton-primaire", options.action ?? "Rédiger");
  principal.type = "button";
  principal.disabled = true;
  const arreter = el("button", "bouton-secondaire", "Arrêter");
  arreter.type = "button";
  arreter.hidden = true;
  const pied = el("div", "volet-pied");
  pied.append(compteur, principal, arreter);
  // Refus local à la vue (autre génération en cours, effacement refusé) : l'état global n'est pas touché.
  const refus = el("p", "mention-refus");
  refus.setAttribute("role", "status");
  refus.hidden = true;
  entree.append(titreEntree, invite, ...(options.controles ?? []), saisie, pied, refus);

  // -- Volet Résultat -------------------------------------------------------------------------
  const sortie = el("section", "editor-pane volet-resultat");
  sortie.setAttribute("aria-labelledby", id("titre-resultat"));
  const titreResultat = el("h2", "volet-titre", options.etiquetteResultat ?? "Résultat");
  titreResultat.id = id("titre-resultat");
  const avancement = el("div", "avancement");
  const avisLong = el("p", "avancement-long", "Texte long : je le traite en plusieurs parties.");
  const etape = el("p", "avancement-etape");
  avancement.append(avisLong, etape);
  avancement.hidden = true;
  const zone = el("div", "resultat");
  zone.id = id("resultat");
  zone.tabIndex = 0;
  zone.setAttribute("data-reponse", ""); // Échap interrompt la génération quand le focus est ici
  zone.setAttribute("role", "region");
  zone.setAttribute("aria-label", options.etiquetteResultat ?? "Résultat");
  if (options.dir) zone.dir = options.dir;
  const attente = el("p", "resultat-vide", "Le résultat s'affichera ici.");
  const notes = el("div", "resultat-notes");
  const mention = el("p", "mention-interrompue", "Résultat interrompu");
  mention.hidden = true;
  const echec = el("p", "mention-echec", "Ce résultat n'a pas pu être produit.");
  echec.hidden = true;
  const actions = el("div", "resultat-actions");
  actions.hidden = true;
  const copier = el("button", "bouton-primaire", "Copier");
  copier.type = "button";
  const regenerer = el("button", "bouton-secondaire", "Régénérer");
  regenerer.type = "button";
  actions.append(copier, regenerer);
  sortie.append(titreResultat, avancement, zone, notes, mention, echec, actions);

  racine.append(entree, sortie);
  conteneur.replaceChildren(racine);

  // -- État -----------------------------------------------------------------------------------
  let brut = ""; // texte reçu
  let aCopier = ""; // texte brut final (sans surlignage ni marquage)
  let enCours = false; // une génération de cette vue est en cours
  let termine = false; // un résultat est affiché
  let dernierEnvoi = null; // { messages, options } du dernier envoi, rejoué par Régénérer
  let rejeu = null; // résultat précédent, rétabli si le pont refuse une régénération
  let sale = false; // l'entrée a changé depuis le dernier envoi
  let vide = true; // aucun évènement reçu pour la génération en cours
  let avant = null; // { dernierEnvoi, sale } avant l'envoi en cours, rétablis s'il est refusé
  let autre = false; // une génération d'une autre Tâche est en cours (le pont n'en admet qu'une)

  zone.replaceChildren(attente);

  function rafraichir() {
    const saisieVide = saisie.value.trim() === "";
    // Un seul bouton principal visible : « Rédiger » avant la génération (ou si l'entrée a
    // changé), « Arrêter » pendant, « Copier » ensuite.
    const peutRediger = !termine || sale;
    principal.hidden = enCours || !peutRediger;
    principal.disabled = options.peutEnvoyer ? !options.peutEnvoyer() : saisieVide;
    arreter.hidden = !enCours;
    copier.className = peutRediger ? "bouton-secondaire" : "bouton-primaire";
    regenerer.disabled = enCours || !dernierEnvoi;
    actions.hidden = !termine || enCours;
    entree.setAttribute("aria-busy", String(enCours));
    sortie.setAttribute("aria-busy", String(enCours));
  }

  function majCompteur() {
    const n = compterMots(saisie.value);
    compteur.textContent = `${n} mot${n > 1 ? "s" : ""}`;
  }

  function reinitialiserResultat() {
    brut = "";
    aCopier = "";
    termine = false;
    avancement.hidden = true;
    avisLong.hidden = true;
    etape.textContent = "";
    notes.replaceChildren();
    mention.hidden = true;
    echec.hidden = true;
    zone.replaceChildren(attente);
  }

  function signaler(message) {
    refus.textContent = message;
    refus.hidden = false;
    annoncer(message);
  }

  function lancer(envoi) {
    if (enCours) return;
    if (autre || generationEnCours?.() === true) {
      // Le pont refuserait (`generation-en-cours`) et l'état global passerait à tort à « libre » :
      // le refus est local, rien n'est envoyé et rien n'est modifié.
      signaler("Une génération est en cours.");
      return;
    }
    refus.hidden = true;
    avant = { dernierEnvoi, sale };
    rejeu = termine
      ? { brut, aCopier, contenu: [...zone.childNodes], notes: [...notes.childNodes] }
      : null;
    dernierEnvoi = envoi;
    sale = false;
    enCours = true;
    vide = true;
    termine = false;
    rafraichir();
    Promise.resolve()
      .then(() => pont.envoyer(tache, envoi.messages, envoi.options))
      .then(exigerOk)
      .catch(() => bus.emettre("generation:erreur", { tache }));
  }

  function envoyerSaisie() {
    const texte = saisie.value;
    const envoyable = options.peutEnvoyer ? options.peutEnvoyer() : texte.trim() !== "";
    if (enCours || !envoyable) return;
    lancer(
      options.construireEnvoi?.(texte) ?? {
        messages: [{ role: "user", content: texte }],
        options: {},
      },
    );
  }

  /** Premier évènement de la génération : le résultat précédent est remplacé. */
  function debutFlux() {
    if (!vide) return;
    vide = false;
    rejeu = null;
    reinitialiserResultat();
  }

  function terminer(fin) {
    enCours = false;
    termine = true;
    vide = true;
    aCopier = brut;
    if (brut) {
      const rendu = options.rendreResultat?.(brut, zone, dernierEnvoi, fin);
      if (typeof rendu === "string") aCopier = rendu;
      else zone.textContent = brut;
    }
    if (fin?.raison === "interrompue") mention.hidden = false;
    if (fin?.raison === "longueur") {
      notes.append(el("p", "avertissement", "Le résultat a été coupé : la longueur maximale est atteinte."));
    }
    copier.hidden = !aCopier;
    rafraichir();
    // On n'annonce pas le texte entier (long) : l'état et le nombre de passages signalés.
    const n = zone.querySelectorAll(".flagged-passage").length;
    const entete = fin?.raison === "interrompue" ? "Rédaction interrompue" : "Rédaction terminée";
    annoncer(n ? `${entete}. ${n} passage${n > 1 ? "s" : ""} signalé${n > 1 ? "s" : ""}.` : `${entete}.`);
  }

  // -- Actions --------------------------------------------------------------------------------
  principal.addEventListener("click", envoyerSaisie);
  arreter.addEventListener("click", () => {
    Promise.resolve()
      .then(() => pont.arreter())
      .then(exigerOk)
      .catch(() => bus.emettre("generation:erreur", { tache }));
  });
  regenerer.addEventListener("click", () => {
    if (dernierEnvoi) lancer(dernierEnvoi);
  });
  copier.addEventListener("click", async () => {
    if (!aCopier) return;
    const ok = await copierTexte(aCopier);
    confirmer(actions, ok ? "Copié" : "Copie impossible"); // effacée après 3 s
  });
  saisie.addEventListener("input", () => {
    majCompteur();
    if (termine) sale = true;
    rafraichir();
  });
  // Contrôles ajoutés par la vue (`options.controles`) : ils comptent comme une modification de l'entrée.
  entree.addEventListener("input", (e) => {
    if (e.target === saisie) return;
    if (termine) sale = true;
    rafraichir();
  });
  entree.addEventListener("change", (e) => {
    if (e.target === saisie) return;
    if (termine) sale = true;
    rafraichir();
  });
  saisie.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey) && !e.isComposing) {
      e.preventDefault();
      envoyerSaisie();
    }
  });

  // -- Évènements du bus (format `core.evenements.vers_dict`) ---------------------------------
  // Seule la vue qui a lancé la génération les reçoit.
  bus.abonner("generation:debut", ({ tache: t }) => {
    if (t !== tache) autre = true;
  });
  const liberer = () => {
    if (autre) refus.hidden = true;
    autre = false;
  };
  bus.abonner("evenement:fin", liberer);
  bus.abonner("evenement:erreur", liberer);
  bus.abonner("generation:erreur", (charge) => {
    if (charge?.tache && charge.tache !== tache) liberer();
  });
  bus.abonner("nouvelle", ({ tache: t }) => {
    if (t !== tache) liberer();
  });
  bus.abonner("evenement:progression", (e) => {
    if (!enCours) return;
    debutFlux();
    avancement.hidden = false;
    avisLong.hidden = !(e.total > 1);
    etape.textContent = e.etape ?? "";
    annoncer(e.etape ?? "");
  });
  bus.abonner("evenement:jeton", (e) => {
    if (!enCours) return;
    debutFlux();
    brut += e.texte;
    zone.textContent = brut; // pendant le flux : texte brut
  });
  bus.abonner("evenement:avertissement", (e) => {
    if (!enCours) return;
    const n = el("p", "avertissement", e.message);
    n.setAttribute("role", "note");
    notes.append(n);
  });
  bus.abonner("evenement:fin", (e) => {
    if (!enCours) return;
    debutFlux();
    avancement.hidden = true;
    terminer(e);
  });
  bus.abonner("evenement:erreur", () => {
    if (!enCours) return;
    debutFlux();
    enCours = false;
    vide = true;
    avancement.hidden = true;
    if (brut) zone.textContent = brut;
    echec.hidden = false;
    termine = brut !== ""; // sans texte reçu, « Rédiger » reste disponible
    aCopier = brut;
    copier.hidden = !brut;
    rafraichir();
  });
  // L'appel au pont a échoué ou a été refusé : aucun évènement ne suivra, l'état est rétabli.
  bus.abonner("generation:erreur", (charge) => {
    if (!enCours || (charge?.tache && charge.tache !== tache)) return;
    enCours = false;
    avancement.hidden = true;
    if (vide && avant) ({ dernierEnvoi, sale } = avant); // refus : rien n'a été accepté
    avant = null;
    if (vide && rejeu) {
      brut = rejeu.brut;
      aCopier = rejeu.aCopier;
      zone.replaceChildren(...rejeu.contenu);
      notes.replaceChildren(...rejeu.notes);
      termine = true;
      copier.hidden = !aCopier;
    } else {
      echec.hidden = false;
      termine = brut !== "";
      copier.hidden = !brut;
    }
    rejeu = null;
    vide = true;
    rafraichir();
  });
  bus.abonner("nouvelle", ({ tache: t }) => {
    if (t !== tache) return;
    const interrompre = enCours;
    enCours = false; // les évènements tardifs de la génération arrêtée sont ignorés
    saisie.value = "";
    dernierEnvoi = null;
    rejeu = null;
    sale = false;
    vide = true;
    reinitialiserResultat();
    majCompteur();
    rafraichir();
    refus.hidden = true;
    // D'abord l'arrêt, puis l'oubli du dernier envoi côté pont : un refus est signalé, pas ignoré.
    Promise.resolve()
      .then(() => (interrompre ? pont.arreter() : null))
      .then(exigerOk)
      .then(() => pont.appeler("nouvelle_conversation"))
      .then(exigerOk)
      .catch(() => signaler("L'effacement n'a pas abouti côté assistant. Réessayez."));
  });
  bus.abonner("copier-dernier", async ({ tache: t }) => {
    if (t !== tache || !aCopier) return;
    const ok = await copierTexte(aCopier);
    confirmer(actions, ok ? "Copié" : "Copie impossible");
  });

  majCompteur();
  rafraichir();
}

// Configuration des deux Tâches de cette story. La phrase d'aide du Compte rendu vient du
// document UX ; celle du Langage clair est une proposition à valider (voir la spec 12.8).
const TACHES = {
  CR: {
    action: "Rédiger",
    invite: "Collez vos notes de réunion. Je produis un compte rendu sans rien ajouter.",
    etiquetteResultat: "Compte rendu",
  },
  LC: {
    action: "Réécrire",
    invite: "Collez le texte à rendre plus clair. Les montants et les dates restent identiques.",
    etiquetteResultat: "Texte en langage clair",
    rendreResultat: (brut, zone) => rendrePassagesSignales(zone, brut),
  },
};

/**
 * @param {HTMLElement} conteneur Élément réservé à la vue.
 * @param {object} pont Client du pont (appeler, envoyer, arreter).
 * @param {{bus: object, tache: string}} contexte
 */
export function monter(conteneur, pont, contexte) {
  const options = TACHES[contexte.tache];
  if (!options) {
    conteneur.replaceChildren(el("p", "non-disponible", "non disponible"));
    return;
  }
  monterRedaction(conteneur, pont, contexte, options);
}
