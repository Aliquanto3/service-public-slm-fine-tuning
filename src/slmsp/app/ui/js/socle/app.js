// Routeur des vues et état global de l'interface (story 12.4).
// Aucun framework : modules ES natifs, aucune ressource externe (CSP `default-src 'self'`).

import * as bus from "./bus.js";
import { annoncer } from "./annonces.js";
import { CRANS_TAILLE, installerClavier } from "./clavier.js";
import { monterComposer } from "./composer.js";
import { brancherReception, memoire, ouvrirPont } from "./pont-client.js";
import * as correction from "../vues/correction.js";
import * as courrier from "../vues/courrier.js";
import * as historique from "../vues/historique.js";
import * as mode from "../vues/mode.js";
import * as parametres from "../vues/parametres.js";
import * as question from "../vues/question.js";
import * as recherche from "../vues/recherche.js";
import * as redaction from "../vues/redaction.js";
import * as resume from "../vues/resume.js";
import * as retours from "../vues/retours.js";
import * as traduction from "../vues/traduction.js";
import * as verification from "../vues/verification.js";

// Tâches de config/taches.toml. `dialogue` : la zone de saisie du socle sert la Tâche.
export const TACHES = [
  { id: "Q", libelle: "Question", icone: "question", vue: question, prioritaire: true, dialogue: true },
  { id: "RD", libelle: "Recherche de données", icone: "recherche", vue: recherche, prioritaire: true, dialogue: true },
  { id: "CR", libelle: "Compte rendu", icone: "compte-rendu", vue: redaction, prioritaire: true },
  { id: "LC", libelle: "Langage clair", icone: "langage-clair", vue: redaction, prioritaire: true },
  { id: "CO", libelle: "Correction", icone: "correction", vue: correction },
  { id: "RE", libelle: "Résumé", icone: "resume", vue: resume },
  { id: "CT", libelle: "Courrier type", icone: "courrier", vue: courrier },
  { id: "TR", libelle: "Traduction", icone: "traduction", vue: traduction },
];

const etat = { tache: "Q", pret: false, generation: false, sources: false, bienvenue: false };
const montees = new Set();
let pont = null;

const $ = (id) => document.getElementById(id);
const tache = (id = etat.tache) => TACHES.find((t) => t.id === id);

function contexteVue(t) {
  // `generationEnCours` : une génération (de n'importe quelle Tâche) est en cours côté pont.
  return { bus, tache: t.id, generationEnCours: () => etat.generation === true };
}

function construireNavigation() {
  for (const t of TACHES) {
    const item = document.createElement("li");
    const bouton = document.createElement("button");
    bouton.type = "button";
    bouton.className = "tache";
    bouton.id = `tache-${t.id}`;
    bouton.dataset.tache = t.id;
    bouton.title = t.libelle; // nom visible au survol quand la colonne se réduit aux icônes
    bouton.setAttribute("aria-label", t.libelle);
    const icone = document.createElement("span");
    icone.className = `icone icone-${t.icone}`;
    icone.setAttribute("aria-hidden", "true");
    const libelle = document.createElement("span");
    libelle.textContent = t.libelle;
    bouton.append(icone, libelle);
    bouton.addEventListener("click", () => activer(t.id));
    item.append(bouton);
    $(t.prioritaire ? "taches-prioritaires" : "taches-secondaires").append(item);
    const section = document.createElement("section");
    section.id = `vue-${t.id}`;
    section.className = "vue";
    section.setAttribute("aria-label", t.libelle);
    section.hidden = true;
    $("vues").append(section);
  }
}

function basculerPlus(ouvert = $("plus-bascule").getAttribute("aria-expanded") !== "true") {
  $("plus-bascule").setAttribute("aria-expanded", String(ouvert));
  $("taches-secondaires").hidden = !ouvert;
  memoire.ecrire("plus-ouvert", ouvert);
}

function activer(id, { annonce = true } = {}) {
  const t = tache(id);
  if (!t) return;
  const ancienne = etat.tache;
  etat.tache = id;
  if (!t.prioritaire && $("taches-secondaires").hidden) basculerPlus(true);
  for (const b of document.querySelectorAll(".tache[data-tache]")) {
    if (b.dataset.tache === id) b.setAttribute("aria-current", "true");
    else b.removeAttribute("aria-current");
  }
  for (const s of document.querySelectorAll("#vues > .vue")) s.hidden = s.id !== `vue-${id}`;
  if (pont && !montees.has(id)) {
    montees.add(id);
    t.vue.monter($(`vue-${id}`), pont, contexteVue(t));
  }
  $("titre-tache").textContent = t.libelle;
  $("bouton-nouvelle").textContent = t.dialogue ? "Nouvelle conversation" : "Effacer";
  composer.changerTache(ancienne, id);
  afficherZones();
  if (annonce) annoncer(`Tâche active : ${t.libelle}`);
  bus.emettre("tache:active", { tache: id });
}

function afficherZones() {
  const t = tache();
  $("bienvenue").hidden = !etat.bienvenue;
  $("vues").hidden = etat.bienvenue;
  $("composer").hidden = etat.bienvenue || !t.dialogue;
  $("bandeau-preparation").hidden = etat.pret;
}

function ouvrirSources(ouvert) {
  etat.sources = ouvert;
  $("sources").hidden = !ouvert;
  $("bouton-sources").setAttribute("aria-expanded", String(ouvert));
  if (ouvert) $("sources-fermer").focus();
  else if (!$("bouton-sources").hidden) $("bouton-sources").focus();
}

function appliquerTaille(pourcent) {
  document.documentElement.style.setProperty("--echelle", `${pourcent}%`);
  memoire.ecrire("echelle", pourcent);
}

function changerTaille(delta) {
  const actuelle = memoire.lire("echelle", 100);
  let i = CRANS_TAILLE.indexOf(actuelle);
  if (i < 0) i = 0;
  i = delta === 0 ? 0 : Math.min(CRANS_TAILLE.length - 1, Math.max(0, i + delta));
  appliquerTaille(CRANS_TAILLE[i]);
  annoncer(`Taille du texte : ${CRANS_TAILLE[i]} %`);
}

function ancrerVuesTransverses() {
  mode.monter($("ancre-mode"), pont, { bus });
  historique.monter($("ancre-historique"), pont, { bus });
  verification.monter($("ancre-verification"), pont, { bus });
  let parametresMontes = false;
  $("bouton-parametres").addEventListener("click", () => {
    if (!parametresMontes) {
      parametresMontes = true;
      parametres.monter($("ancre-parametres"), pont, { bus });
      retours.monter($("ancre-retours"), pont, { bus });
    }
    $("dialogue-parametres").showModal();
  });
  $("dialogue-fermer").addEventListener("click", () => $("dialogue-parametres").close());
}

function surEvenement(evenement) {
  bus.emettre("evenement", evenement);
  bus.emettre(`evenement:${evenement.type}`, evenement);
}

const composer = monterComposer({ bus, getPont: () => pont, etat });

bus.abonner("evenement:pret", () => {
  if (etat.pret) return;
  etat.pret = true;
  afficherZones();
  composer.rafraichir();
  annoncer("L'assistant est prêt.");
});
bus.abonner("generation:debut", () => {
  etat.generation = true;
  $("erreur-interne").hidden = true;
  composer.rafraichir();
});
bus.abonner("evenement:fin", () => {
  etat.generation = false;
  composer.rafraichir();
});
function signalerErreur() {
  etat.generation = false;
  $("erreur-interne").hidden = false;
  composer.restaurer();
  annoncer("Un problème est survenu. Votre texte est conservé.");
}
bus.abonner("evenement:erreur", signalerErreur);
bus.abonner("generation:erreur", signalerErreur); // l'appel au pont a lui-même échoué
bus.abonner("sources:ouvrir", () => ouvrirSources(true));
bus.abonner("sources:fermer", () => ouvrirSources(false));
bus.abonner("sources:disponibles", (disponibles) => {
  $("bouton-sources").hidden = !disponibles;
  if (!disponibles && etat.sources) ouvrirSources(false);
});

async function demarrer() {
  $("demarrage-echec").hidden = true; // garde de index.html : le JS a bien démarré
  construireNavigation();
  appliquerTaille(memoire.lire("echelle", 100));
  etat.bienvenue = !memoire.lire("bienvenue-vue", false);
  basculerPlus(memoire.lire("plus-ouvert", false));
  brancherReception(surEvenement);
  $("bienvenue-commencer").addEventListener("click", () => {
    memoire.ecrire("bienvenue-vue", true);
    etat.bienvenue = false;
    afficherZones();
    composer.focus();
  });
  $("plus-bascule").addEventListener("click", () => basculerPlus());
  $("bouton-nouvelle").addEventListener("click", () => nouvelle());
  $("bouton-sources").addEventListener("click", () => ouvrirSources(!etat.sources));
  $("sources-fermer").addEventListener("click", () => ouvrirSources(false));
  $("erreur-reessayer").addEventListener("click", () => {
    $("erreur-interne").hidden = true;
    composer.reessayer();
  });
  installerClavier({
    prioritaire: (i) => {
      const t = TACHES.filter((x) => x.prioritaire)[i];
      if (t) activer(t.id);
    },
    nouvelle: () => nouvelle(),
    copier: () => bus.emettre("copier-dernier", { tache: etat.tache }),
    taille: changerTaille,
    echap: () => {
      if ($("dialogue-parametres").open) return; // fermé nativement
      if (etat.sources) ouvrirSources(false);
      else if (etat.generation && document.activeElement?.closest("[data-reponse]")) {
        Promise.resolve().then(() => pont.arreter()).catch(signalerErreur);
      }
    },
  });
  // L'interface est utilisable (saisie, navigation) avant que le pont ne réponde.
  activer("Q", { annonce: false });
  try {
    pont = await ouvrirPont(bus);
  } catch {
    $("demarrage-echec").hidden = false; // pont introuvable : l'utilisateur le voit, sans détail
    return;
  }
  ancrerVuesTransverses();
  activer(etat.tache, { annonce: false }); // monte la vue active, maintenant que le pont existe
  window.slmsp = { bus, pont, etat, activer, ouvrirSources, TACHES };
  bus.emettre("pont:ouvert", { factice: pont.factice });
}

function nouvelle() {
  composer.vider();
  $("erreur-interne").hidden = true;
  bus.emettre("nouvelle", { tache: etat.tache });
}

demarrer().catch(() => {
  $("demarrage-echec").hidden = false;
});
