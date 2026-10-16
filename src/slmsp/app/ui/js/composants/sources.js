// Panneau Sources : une `source-card` par source (origine, date de l'Index, extrait dépliable, « Ouvrir »).

import { confirmer, copierTexte, dateLisible } from "./copie.js";

/** Origine libellée sans jargon (DESIGN.md). */
export function libelleOrigine(source) {
  if (source.origine === "index") return "Documents installés";
  try {
    const hote = new URL(source.url).hostname;
    if (hote === "data.gouv.fr" || hote.endsWith(".data.gouv.fr")) return "data.gouv";
  } catch {
    /* URL illisible : « Page consultée » */
  }
  return "Page consultée";
}

/** Une URL n'est ouvrable que si elle est en https : tout le reste est ignoré. */
export function urlOuvrable(url) {
  try {
    return new URL(url).protocol === "https:";
  } catch {
    return false;
  }
}

/**
 * Bouton « Ouvrir » (Q1 : la WebView ne navigue jamais). C'est un bouton, pas un lien : ni clic
 * milieu, ni Ctrl+clic, ni glisser ne peuvent ouvrir l'URL dans l'application.
 * Connecté : `pont.appeler("ouvrir_lien", url)` confie l'URL au navigateur du système (contrôle
 * de la Liste blanche côté Python ; bouchon jusqu'à 12.6). Hors ligne, ou si le pont refuse :
 * copie le lien et le dit.
 * @param {() => boolean} horsLigne Lu au moment du clic.
 */
export function creerLienOuvrir(url, horsLigne, pont, libelle = "Ouvrir") {
  const bouton = document.createElement("button");
  bouton.type = "button";
  bouton.className = "bouton-secondaire";
  bouton.textContent = libelle;
  bouton.title = url;
  bouton.addEventListener("click", async () => {
    const parent = bouton.parentElement ?? bouton;
    const hors = horsLigne();
    if (!hors) {
      try {
        const reponse = await pont?.appeler("ouvrir_lien", url);
        if (reponse?.ok === true) {
          confirmer(parent, "Lien ouvert dans votre navigateur.");
          return;
        }
      } catch {
        /* repli : copie du lien */
      }
    }
    const ok = await copierTexte(url);
    let message = "Copie impossible : sélectionnez le lien à la main.";
    if (ok) {
      message = hors
        ? "Lien copié. Il s'ouvrira quand vous serez connecté."
        : "Lien copié. Collez-le dans votre navigateur.";
    }
    confirmer(parent, message);
  });
  return bouton;
}

function creerCarte(source, { horsLigne, pont, courante }) {
  const carte = document.createElement("article");
  carte.className = "source-card";
  if (source.numero != null) carte.dataset.numero = String(source.numero);
  if (courante) carte.setAttribute("aria-current", "true");
  const titre = document.createElement("h3");
  titre.textContent = source.numero != null ? `${source.numero}. ${source.titre}` : source.titre;
  const meta = document.createElement("p");
  meta.className = "source-meta";
  const date = dateLisible(source.date);
  const parties = [libelleOrigine(source)];
  if (date) parties.push(source.origine === "index" ? `Index du ${date}` : `Consultée le ${date}`);
  meta.textContent = parties.join(" · ");
  carte.append(titre, meta);
  if (source.extrait) {
    const detail = document.createElement("details");
    const resume = document.createElement("summary");
    resume.textContent = "Extrait";
    const extrait = document.createElement("p");
    extrait.className = "source-extrait";
    extrait.textContent = source.extrait;
    detail.append(resume, extrait);
    carte.append(detail);
  }
  if (urlOuvrable(source.url)) {
    const actions = document.createElement("div");
    actions.className = "source-actions";
    actions.append(creerLienOuvrir(source.url, horsLigne, pont));
    carte.append(actions);
  }
  return carte;
}

/**
 * Remplit le panneau.
 * @param {Array} sources Sources de la réponse sélectionnée.
 * @param {{horsLigne: () => boolean, pont: object, numero?: number|null}} options `numero` : source
 *   mise en avant.
 */
export function rendrePanneauSources(corps, sources, { horsLigne, pont, numero = null }) {
  const cartes = sources.map((s) =>
    creerCarte(s, { horsLigne, pont, courante: numero != null && s.numero === numero }),
  );
  corps.replaceChildren(...cartes);
  corps.querySelector("[aria-current]")?.scrollIntoView?.({ block: "nearest" });
}
