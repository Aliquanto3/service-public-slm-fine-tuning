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
 * Lien « Ouvrir ». Connecté : lien https que l'application confie au navigateur du système.
 * Hors ligne : copie le lien et affiche « Lien copié… ».
 * @param {() => boolean} horsLigne Lu au moment du clic.
 */
export function creerLienOuvrir(url, horsLigne, libelle = "Ouvrir") {
  const lien = document.createElement("a");
  lien.className = "bouton-secondaire";
  lien.textContent = libelle;
  lien.href = url;
  lien.target = "_blank";
  lien.rel = "noopener noreferrer";
  lien.addEventListener("click", async (e) => {
    if (!horsLigne()) return;
    e.preventDefault();
    const ok = await copierTexte(url);
    confirmer(
      lien.parentElement ?? lien,
      ok ? "Lien copié. Il s'ouvrira quand vous serez connecté." : "Copie impossible : sélectionnez le lien à la main.",
    );
  });
  return lien;
}

function creerCarte(source, { horsLigne, courante }) {
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
    actions.append(creerLienOuvrir(source.url, horsLigne));
    carte.append(actions);
  }
  return carte;
}

/**
 * Remplit le panneau.
 * @param {Array} sources Sources de la réponse sélectionnée.
 * @param {{horsLigne: () => boolean, numero?: number|null}} options `numero` : source mise en avant.
 */
export function rendrePanneauSources(corps, sources, { horsLigne, numero = null }) {
  const cartes = sources.map((s) => creerCarte(s, { horsLigne, courante: numero != null && s.numero === numero }));
  corps.replaceChildren(...cartes);
  corps.querySelector("[aria-current]")?.scrollIntoView?.({ block: "nearest" });
}
