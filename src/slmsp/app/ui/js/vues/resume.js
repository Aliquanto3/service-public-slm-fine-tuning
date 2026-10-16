// Vue Résumé (RE), story 13.2 (FR-15) : volet de rédaction de 12.8 + choix de la longueur.
// Les trois longueurs reprennent les valeurs du Jeu d'évaluation gelé (`courte`, `moyenne`,
// `detaillee`) pour garder les conditions du banc ; elles partent dans `longueur_demandee` de
// l'entrée du Harnais. Le texte collé ne sort pas du poste (FR-38) : la Tâche n'a aucun outil.

import { monterRedaction } from "./redaction.js";

// [valeur envoyée, libellé affiché]. Défaut : « moyenne ».
export const LONGUEURS = [
  ["courte", "Court"],
  ["moyenne", "Moyen"],
  ["detaillee", "Détaillé"],
];
// Plafond d'entrée : contexte de 8192 tokens des modèles (config/modeles/*.toml), moins ~1024 de
// sortie et la consigne, soit ~6000 tokens de document ; à ~1,5 token par mot français, 4000 mots.
// Le Harnais ne découpe pas pour RE (seul CR découpe) et ne refuse pas sur la longueur.
export const PLAFOND_MOTS = 4000;
const CODE_TROP_LONG = "entree-trop-longue";
const compterMots = (t) => (String(t).trim().match(/\S+/g) ?? []).length;
const MESSAGE_TROP_LONG =
  "Ce document est trop long pour être résumé tel quel. Raccourcissez-le, ou résumez-le en plusieurs parties.";

function el(balise, classe, texte) {
  const e = document.createElement(balise);
  if (classe) e.className = classe;
  if (texte !== undefined) e.textContent = texte;
  return e;
}

/**
 * @param {HTMLElement} conteneur Élément réservé à la vue.
 * @param {object} pont Client du pont (appeler, envoyer, arreter).
 * @param {{bus: object, tache: string}} contexte
 */
export function monter(conteneur, pont, contexte) {
  const nom = `resume-longueur-${contexte.tache}`;
  const groupe = el("fieldset", "choix-longueur");
  groupe.append(el("legend", "choix-titre", "Longueur du résumé"));
  const radios = LONGUEURS.map(([valeur, libelle]) => {
    const etiquette = el("label", "choix-option");
    const radio = el("input");
    radio.type = "radio";
    radio.name = nom;
    radio.value = valeur;
    radio.checked = valeur === "moyenne";
    etiquette.append(radio, el("span", undefined, libelle));
    groupe.append(etiquette);
    return radio;
  });
  const longueur = () => radios.find((r) => r.checked)?.value ?? "moyenne";

  // Message d'entrée trop longue (UX-DR19) : uniquement quand le document dépasse le plafond
  // contrôlé ici, avant l'envoi. Tout autre refus ou échec garde le message générique du volet.
  const trop = el("p", "mention-trop-longue", MESSAGE_TROP_LONG);
  trop.setAttribute("role", "status");
  trop.hidden = true;
  const pontEcoute = {
    appeler: (...a) => pont.appeler(...a),
    arreter: (...a) => pont.arreter(...a),
    envoyer: (tache, messages, options) => {
      const document = options?.entree?.document ?? "";
      if (compterMots(document) > PLAFOND_MOTS) {
        trop.hidden = false;
        return Promise.resolve({
          ok: false,
          erreur: { code: CODE_TROP_LONG, message: MESSAGE_TROP_LONG },
        });
      }
      trop.hidden = true;
      return pont.envoyer(tache, messages, options);
    },
  };
  contexte.bus.abonner("nouvelle", ({ tache }) => {
    if (tache === contexte.tache) trop.hidden = true;
  });

  monterRedaction(conteneur, pontEcoute, contexte, {
    action: "Résumer",
    invite: "Collez le document à résumer, puis choisissez la longueur. Je ne rapporte que ce qui figure dans le texte.",
    etiquetteResultat: "Résumé",
    controles: [groupe],
    construireEnvoi: (texte) => ({
      messages: [{ role: "user", content: texte }],
      options: { entree: { document: texte, longueur_demandee: longueur() } },
    }),
  });
  conteneur.append(trop);
}
