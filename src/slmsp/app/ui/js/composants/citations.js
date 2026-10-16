// Puces de citation (`citation-chip`) : les renvois `[n]` du texte deviennent des boutons.
// Le texte vient du modèle : il n'entre dans le DOM que par des nœuds texte (jamais de HTML construit).

/**
 * Rend `texte` dans `cible`. Un renvoi `[n]` dont la source existe devient une puce lue
 * « Source n : titre » ; sinon il reste du texte.
 * @param {(numero: number) => void} surPuce Appelé à l'activation d'une puce.
 */
export function rendreTexteAvecCitations(cible, texte, sources, surPuce) {
  const parNumero = new Map(sources.filter((s) => s.numero != null).map((s) => [s.numero, s]));
  const noeuds = [];
  texte.split(/\[(\d+)\]/).forEach((morceau, i) => {
    if (i % 2 === 0) {
      if (morceau) noeuds.push(document.createTextNode(morceau));
      return;
    }
    const numero = Number(morceau);
    const source = parNumero.get(numero);
    if (!source) {
      noeuds.push(document.createTextNode(`[${morceau}]`));
      return;
    }
    const puce = document.createElement("button");
    puce.type = "button";
    puce.className = "citation-chip";
    puce.dataset.numero = String(numero);
    puce.setAttribute("aria-label", `Source ${numero} : ${source.titre}`);
    const num = document.createElement("span");
    num.className = "citation-numero";
    num.setAttribute("aria-hidden", "true");
    num.textContent = String(numero);
    const titre = document.createElement("span");
    titre.className = "citation-titre";
    titre.setAttribute("aria-hidden", "true");
    titre.textContent = source.titre;
    puce.append(num, titre);
    puce.addEventListener("click", () => surPuce(numero));
    noeuds.push(puce);
  });
  cible.replaceChildren(...noeuds);
}
