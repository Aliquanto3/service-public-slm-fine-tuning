// Copie dans le presse-papiers et confirmation en ligne (`inline-confirmation`, effacée après 3 s).

import { annoncer } from "../socle/annonces.js";

/** Copie un texte brut ; renvoie `true` si la copie a réussi. */
export async function copierTexte(texte) {
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(texte);
      return true;
    }
  } catch {
    /* repli ci-dessous */
  }
  try {
    const zone = document.createElement("textarea");
    zone.value = texte;
    zone.setAttribute("readonly", "");
    zone.style.cssText = "position:fixed;opacity:0;top:0;left:0";
    document.body.append(zone);
    zone.select();
    const ok = document.execCommand("copy");
    zone.remove();
    return ok;
  } catch {
    return false;
  }
}

/** Affiche un court message près de `parent` et l'annonce ; il s'efface après `delai` ms. */
export function confirmer(parent, message, delai = 3000) {
  let el = parent.querySelector(":scope > .inline-confirmation");
  if (!el) {
    el = document.createElement("span");
    el.className = "inline-confirmation";
    parent.append(el);
  }
  el.textContent = message;
  clearTimeout(el._minuteur);
  el._minuteur = setTimeout(() => el.remove(), delai);
  annoncer(message);
}

/** Date lisible en français (« 11 oct. 2026 ») ; une valeur illisible est rendue telle quelle. */
export function dateLisible(valeur) {
  if (!valeur) return "";
  const d = new Date(valeur);
  if (Number.isNaN(d.getTime())) return String(valeur);
  return d.toLocaleDateString("fr-FR", { day: "numeric", month: "short", year: "numeric" });
}
