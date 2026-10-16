// Annonces au lecteur d'écran : région aria-live polie (UX-DR21).
// Les messages sont rendus l'un après l'autre : aucun n'est écrasé par le suivant.

const file = [];
let enCours = false;

function pomper() {
  const region = document.getElementById("annonces");
  if (enCours || !region || file.length === 0) return;
  enCours = true;
  region.textContent = ""; // le vidage préalable force la relecture d'un message identique
  setTimeout(() => {
    region.textContent = file.shift();
    setTimeout(() => {
      enCours = false;
      pomper();
    }, 150);
  }, 50);
}

/** Annonce un message à la suite de ceux déjà en attente. */
export function annoncer(message) {
  file.push(message);
  pomper();
}
