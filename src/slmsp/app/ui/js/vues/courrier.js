// Vue Courrier type (CT), story 13.3 (FR-14, UX-DR14) : volet de rédaction de 12.8 avec un petit
// formulaire (type de courrier, objet, éléments connus). Seuls les champs remplis sont envoyés.
// Les emplacements « [à compléter] » du courrier sont repérés côté Python
// (`redaction_outils.emplacements`) et rendus en `letter-placeholder` par `textContent`
// (jamais de HTML construit). Le presse-papiers reçoit toujours le courrier brut.

import { monterRedaction } from "./redaction.js";

// Types proposés (libellés de l'AC de la story, à confirmer par Anaël). Aucun objet ni élément
// connu prérempli : le formulaire démarre vide.
export const TYPES_COURRIER = [
  "accusé de réception",
  "demande de pièces",
  "convocation",
  "réponse d'information",
];

const INTITULES = { objet: "Objet", elements_connus: "Éléments connus" };

function el(balise, classe, texte) {
  const e = document.createElement(balise);
  if (classe) e.className = classe;
  if (texte !== undefined) e.textContent = texte;
  return e;
}

function pluriel(n, mot) {
  return `${n} ${mot}${n > 1 ? "s" : ""}`;
}

/** Rend les segments dans `zone` ; renvoie le nombre d'emplacements. */
export function rendreEmplacements(zone, segments) {
  let n = 0;
  const noeuds = segments.map((s) => {
    if (s.type !== "emplacement") return document.createTextNode(s.texte);
    n += 1;
    const marque = el("mark", "letter-placeholder");
    marque.tabIndex = 0;
    const visible = el("span", "", s.texte);
    visible.setAttribute("aria-hidden", "true");
    marque.append(visible, el("span", "sr-only", `à compléter : ${s.texte.slice(1, -1)}`));
    return marque;
  });
  zone.replaceChildren(...noeuds);
  return n;
}

function champ(id, libelleTexte, controle) {
  const etiquette = el("label", "courrier-etiquette", libelleTexte);
  etiquette.htmlFor = id;
  controle.id = id;
  const bloc = el("div", "courrier-champ");
  bloc.append(etiquette, controle);
  return bloc;
}

/**
 * @param {HTMLElement} conteneur Élément réservé à la vue.
 * @param {object} pont Client du pont (appeler, envoyer, arreter).
 * @param {{bus: object, tache: string}} contexte
 */
export function monter(conteneur, pont, contexte) {
  const { tache } = contexte;
  const type = el("select", "courrier-type");
  type.append(new Option("Choisir un type de courrier", ""));
  for (const t of TYPES_COURRIER) type.append(new Option(t, t));
  const objet = el("input", "courrier-objet");
  objet.type = "text";
  const blocType = champ(`courrier-type-${tache}`, "Type de courrier", type);
  const blocObjet = champ(`courrier-objet-${tache}`, "Objet (facultatif)", objet);

  const notes = el("div", "courrier-notes");
  notes.setAttribute("role", "status");
  let jeton = 0; // un contrôle périmé (nouvelle génération) est ignoré
  const oublier = () => {
    jeton += 1;
    notes.replaceChildren();
    notes.remove();
  };
  contexte.bus.abonner("generation:debut", ({ tache: t }) => {
    if (t === tache) oublier();
  });
  contexte.bus.abonner("nouvelle", ({ tache: t }) => {
    if (t === tache) {
      oublier();
      type.value = "";
      objet.value = "";
    }
  });

  // La zone de saisie (éléments connus) est créée par `monterRedaction`.
  const saisieRemplie = () => {
    const s = conteneur.querySelector(".redaction-saisie");
    return !!s && s.value.trim() !== "";
  };

  monterRedaction(conteneur, pont, contexte, {
    action: "Rédiger",
    etiquetteEntree: "Formulaire",
    invite:
      "Choisissez le type de courrier, puis renseignez seulement ce que vous savez (objet, éléments connus). Ce qui manque apparaît dans le courrier comme un emplacement à compléter.",
    etiquetteResultat: "Courrier",
    controles: [blocType, blocObjet],
    peutEnvoyer: () => type.value !== "" && (objet.value.trim() !== "" || saisieRemplie()),
    construireEnvoi(texte) {
      const remplis = { type_courrier: type.value };
      if (objet.value.trim()) remplis.objet = objet.value.trim();
      if (texte.trim()) remplis.elements_connus = texte.trim();
      const lignes = [`Type de courrier : ${remplis.type_courrier}`];
      for (const cle of ["objet", "elements_connus"]) {
        if (remplis[cle]) lignes.push(`${INTITULES[cle]} : ${remplis[cle]}`);
      }
      return { messages: [{ role: "user", content: lignes.join("\n") }], options: { entree: remplis } };
    },
    rendreResultat(brut, zone, envoi, fin) {
      const mon = ++jeton;
      zone.textContent = brut; // texte brut en attendant (ou si le contrôle échoue)
      const remplis = envoi?.options?.entree;
      // Un courrier interrompu ou coupé n'est pas complet : pas de contrôle.
      if (!remplis || (fin && fin.raison !== "terminee")) return brut;
      const absents = Object.keys(INTITULES).filter((c) => !(c in remplis));
      Promise.resolve()
        .then(() => pont.appeler("redaction_outils.emplacements", brut, absents))
        .then((r) => {
          if (mon !== jeton || !zone.isConnected || zone.textContent !== brut) return;
          if (!r || r.ok === false || !Array.isArray(r.segments)) throw new Error("refus");
          const n = rendreEmplacements(zone, r.segments);
          const lignes = [
            el(
              "p",
              "courrier-compte",
              n ? `${pluriel(n, "emplacement")} à compléter.` : "Aucun emplacement à compléter.",
            ),
          ];
          for (const c of r.champs_en_valeur ?? []) {
            const alerte = el("div", "callout callout-warning");
            alerte.append(
              el(
                "p",
                undefined,
                `« ${INTITULES[c] ?? c} » n'a pas été fourni, mais le courrier lui donne une valeur : vérifiez-la ou remplacez-la par un emplacement. Vérifié automatiquement.`,
              ),
            );
            lignes.push(alerte);
          }
          notes.replaceChildren(...lignes);
          zone.after(notes);
        })
        .catch(() => {
          if (mon !== jeton) return;
          notes.replaceChildren(
            el(
              "p",
              "courrier-compte",
              "Les emplacements n'ont pas pu être repérés : voici le courrier tel quel.",
            ),
          );
          zone.after(notes);
        });
      return brut;
    },
  });
}
