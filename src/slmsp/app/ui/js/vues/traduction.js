// Vue Traduction (TR), story 13.4 (FR-18, UX-DR15, Q9) : volet de rédaction de 12.8 + choix des
// langues. Les langues viennent de `config/application.toml` (`reglages.langues_traduction`) :
// retirer l'arabe se fait en une ligne de configuration. Le français est toujours une extrémité
// proposée. Les valeurs envoyées (`langue_source`, `langue_cible`) sont les noms en français
// utilisés par le banc (`benchmarks/moteurs/traduction.py`), donc les mêmes conditions que la mesure.
// Le texte collé ne sort pas du poste (FR-38). Tout contenu entre dans le DOM par `textContent`.

import { monterRedaction } from "./redaction.js";

export const NOMS = {
  fr: "français",
  en: "anglais",
  es: "espagnol",
  ar: "arabe",
  pt: "portugais",
  de: "allemand",
};
export const ERREUR_LANGUES = "Les langues de traduction n'ont pas pu être chargées : la traduction est indisponible.";
export const AUCUNE_CIBLE = "Aucune langue cible n'est configurée : la traduction est indisponible.";
export const MENTION = "Traduction automatique, à vérifier avant envoi";
const RTL = new Set(["ar", "he", "fa", "ur"]);

const nom = (code) => NOMS[code] ?? code;
const codeDe = (libelle) => Object.keys(NOMS).find((c) => NOMS[c] === libelle) ?? libelle;

function el(balise, classe, texte) {
  const e = document.createElement(balise);
  if (classe) e.className = classe;
  if (texte !== undefined) e.textContent = texte;
  return e;
}

/** Applique `lang` et `dir` d'une langue à un élément (arabe : `rtl`). */
function marquer(element, code) {
  element.lang = code;
  element.dir = RTL.has(code.split("-")[0]) ? "rtl" : "ltr";
}

/**
 * @param {HTMLElement} conteneur Élément réservé à la vue.
 * @param {object} pont Client du pont (appeler, envoyer, arreter).
 * @param {{bus: object, tache: string}} contexte
 */
export function monter(conteneur, pont, contexte) {
  const id = (n) => `traduction-${n}-${contexte.tache}`;
  const groupe = el("div", "choix-langues");
  const champ = (cle, libelle) => {
    const etiquette = el("label", "choix-langue", libelle);
    etiquette.htmlFor = id(cle);
    const select = el("select");
    select.id = id(cle);
    return [etiquette, select];
  };
  const [etiqSource, source] = champ("source", "Langue source");
  const [etiqCible, cible] = champ("cible", "Langue cible");
  const inverser = el("button", "bouton-secondaire", "Inverser");
  inverser.type = "button";
  inverser.setAttribute("aria-label", "Inverser les langues");
  const message = el("p", "message-langues");
  message.setAttribute("role", "alert");
  message.hidden = true;
  groupe.append(etiqSource, source, inverser, etiqCible, cible, message);

  // « Traduire » est désactivé tant qu'aucune langue cible n'est connue (pas de repli : Q9).
  let disponible = false;
  function majAction() {
    conteneur.querySelector(".redaction-saisie")?.dispatchEvent(new Event("input"));
  }
  function indisponible(texte) {
    disponible = false;
    message.textContent = texte;
    message.hidden = false;
    majAction();
  }

  function remplir(langues) {
    const cibles = langues.filter((c) => c !== "fr");
    const codes = ["fr", ...cibles];
    if (!cibles.length) {
      viderSelects();
      indisponible(AUCUNE_CIBLE);
      return;
    }
    disponible = true;
    message.hidden = true;
    const garder = [source.value || "fr", cible.value || langues[0]];
    for (const [select, voulu] of [
      [source, garder[0]],
      [cible, garder[1]],
    ]) {
      select.replaceChildren(
        ...codes.map((code) => {
          const o = el("option", undefined, nom(code));
          o.value = code;
          o.lang = code;
          return o;
        }),
      );
      select.value = codes.includes(voulu) ? voulu : codes[0];
    }
    if (source.value === cible.value) cible.value = codes.find((c) => c !== source.value);
    saisieLangue();
    majAction();
  }

  function viderSelects() {
    for (const select of [source, cible]) {
      select.replaceChildren(...["fr"].map((code) => Object.assign(el("option", undefined, nom(code)), { value: code })));
    }
  }

  // La langue de la saisie suit la langue source (arabe : saisie de droite à gauche).
  const saisie = () => conteneur.querySelector(".redaction-saisie");
  function saisieLangue() {
    const s = saisie();
    if (s) marquer(s, source.value);
  }
  // Un changement de langue rend l'entrée « modifiée » : « Traduire » revient après un résultat
  // (Régénérer rejouerait les anciennes langues).
  function changement() {
    precedents = { source: source.value, cible: cible.value };
    saisieLangue();
    saisie()?.dispatchEvent(new Event("input"));
  }
  // Deux sélecteurs jamais identiques : choisir la langue de l'autre les échange.
  let precedents = { source: "fr", cible: "en" };
  for (const [select, autre, cle] of [
    [source, cible, "source"],
    [cible, source, "cible"],
  ]) {
    select.addEventListener("change", () => {
      if (select.value === autre.value) autre.value = precedents[cle];
      changement();
    });
  }
  inverser.addEventListener("click", () => {
    [source.value, cible.value] = [cible.value, source.value];
    changement();
  });

  // Avant la réponse du pont : français seul, « Traduire » désactivé (aucune liste par défaut).
  viderSelects();
  disponible = false;
  Promise.resolve()
    .then(() => pont.appeler("reglages.langues_traduction"))
    .then((r) => {
      if (r?.ok !== true || !Array.isArray(r.langues)) throw new Error("langues");
      // Seules les langues connues de la vue (celles de la Tâche TR) sont proposées.
      remplir(r.langues.filter((c) => typeof c === "string" && Object.hasOwn(NOMS, c)));
      precedents = { source: source.value, cible: cible.value };
    })
    .catch(() => {
      viderSelects();
      indisponible(ERREUR_LANGUES);
    });

  monterRedaction(conteneur, pont, contexte, {
    action: "Traduire",
    invite: "Collez le texte à traduire, puis choisissez les langues. La traduction est automatique : relisez-la avant de l'envoyer.",
    etiquetteResultat: "Traduction",
    controles: [groupe],
    peutEnvoyer: () => disponible && (saisie()?.value.trim() ?? "") !== "",
    construireEnvoi: (texte) => {
      const zone = conteneur.querySelector(".resultat");
      if (zone) marquer(zone, cible.value);
      return {
        messages: [{ role: "user", content: texte }],
        options: {
          entree: { langue_source: nom(source.value), langue_cible: nom(cible.value), texte },
        },
      };
    },
    // Rendu final : traduction isolée dans son sens d'écriture, puis la mention en français.
    rendreResultat: (brut, zone, envoi) => {
      const code = codeDe(envoi?.options?.entree?.langue_cible ?? nom(cible.value));
      const texte = el("p", "traduction-texte", brut);
      marquer(texte, code);
      const mention = el("p", "mention-traduction", MENTION);
      mention.lang = "fr";
      mention.dir = "ltr";
      zone.replaceChildren(texte, mention);
      return `${brut}\n\n${MENTION}`;
    },
  });
  saisieLangue();
  majAction();
}
