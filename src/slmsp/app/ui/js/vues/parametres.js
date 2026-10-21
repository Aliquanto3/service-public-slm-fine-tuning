// Vue « parametres » (story 12.10, UX-DR18) : trois onglets Général, Retours et À propos.
// Contrat du pont : voir `app/pont/reglages.py`. L'onglet Retours accueille le composant de la
// vue « retours » (monté par app.js dans `#ancre-retours`, déplacé ici).
import { annoncer } from "../socle/annonces.js";
import { CRANS_TAILLE } from "../socle/clavier.js";
import { memoire } from "../socle/pont-client.js";

const DELAI_ANNULATION_MS = 5000;
const ABSENT = "non disponible";

function el(nom, attributs = {}, texte) {
  const e = document.createElement(nom);
  for (const [cle, valeur] of Object.entries(attributs)) e.setAttribute(cle, valeur);
  if (texte !== undefined) e.textContent = texte;
  return e;
}

function ligne(libelle, valeur) {
  const bloc = el("div", { class: "parametres-ligne" });
  bloc.append(el("dt", {}, libelle), el("dd", {}, valeur ?? ABSENT));
  return bloc;
}

function section(titre, ...contenu) {
  const s = el("section", { class: "parametres-section" });
  s.append(el("h3", {}, titre), ...contenu);
  return s;
}

function formaterDate(iso) {
  const d = new Date(`${iso}T00:00:00`);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString("fr-FR", { dateStyle: "long" });
}

/**
 * Monte la vue dans son conteneur.
 * @param {HTMLElement} conteneur Élément réservé à la vue.
 * @param {object} pont Client du pont (appeler, envoyer, arreter).
 * @param {object} [contexte] `{ bus, delaiAnnulationMs }`.
 */
export function monter(conteneur, pont, contexte = {}) {
  const bus = contexte.bus;
  const delai = contexte.delaiAnnulationMs ?? DELAI_ANNULATION_MS;

  const onglets = [
    { id: "general", libelle: "Général" },
    { id: "retours", libelle: "Retours" },
    { id: "apropos", libelle: "À propos" },
  ];
  const racine = el("div", { class: "parametres" });
  const liste = el("div", { class: "parametres-onglets", role: "tablist", "aria-label": "Paramètres" });
  const panneaux = {};
  const boutons = {};
  for (const o of onglets) {
    const b = el("button", {
      type: "button",
      role: "tab",
      id: `parametres-onglet-${o.id}`,
      "aria-controls": `parametres-panneau-${o.id}`,
      class: "parametres-onglet",
    }, o.libelle);
    const p = el("div", {
      role: "tabpanel",
      id: `parametres-panneau-${o.id}`,
      "aria-labelledby": `parametres-onglet-${o.id}`,
      class: "parametres-panneau",
      tabindex: "0",
    });
    boutons[o.id] = b;
    panneaux[o.id] = p;
    liste.append(b);
  }

  function choisir(id, { focus = false } = {}) {
    for (const o of onglets) {
      const actif = o.id === id;
      boutons[o.id].setAttribute("aria-selected", String(actif));
      boutons[o.id].tabIndex = actif ? 0 : -1;
      panneaux[o.id].hidden = !actif;
    }
    if (focus) boutons[id].focus();
    if (id === "apropos") chargerAPropos();
  }
  liste.addEventListener("keydown", (e) => {
    const i = onglets.findIndex((o) => boutons[o.id] === document.activeElement);
    if (i < 0) return;
    let cible = null;
    if (e.key === "ArrowRight") cible = (i + 1) % onglets.length;
    else if (e.key === "ArrowLeft") cible = (i + onglets.length - 1) % onglets.length;
    else if (e.key === "Home") cible = 0;
    else if (e.key === "End") cible = onglets.length - 1;
    if (cible === null) return;
    e.preventDefault();
    choisir(onglets[cible].id, { focus: true });
  });
  for (const o of onglets) boutons[o.id].addEventListener("click", () => choisir(o.id));

  // -- Général : taille du texte, Mode, effacement ----------------------------------------
  const general = panneaux.general;

  const valeurTaille = el("output", { class: "parametres-taille-valeur", "aria-live": "off" });
  const reduire = el("button", { type: "button", class: "bouton-secondaire", "aria-label": "Réduire le texte" }, "A−");
  const agrandir = el("button", { type: "button", class: "bouton-secondaire", "aria-label": "Agrandir le texte" }, "A+");
  const normal = el("button", { type: "button", class: "bouton-secondaire" }, "100 %");
  const aideTaille = el("p", { class: "parametres-aide" }, "Raccourcis : Ctrl et +, Ctrl et −, Ctrl et 0.");
  const rangTaille = el("div", { class: "parametres-rang" });
  rangTaille.append(reduire, valeurTaille, agrandir, normal);

  function tailleCourante() {
    const lue = Number.parseInt(document.documentElement.style.getPropertyValue("--echelle"), 10);
    return CRANS_TAILLE.includes(lue) ? lue : memoire.lire("echelle", CRANS_TAILLE[0]);
  }
  function afficherTaille() {
    valeurTaille.textContent = `${tailleCourante()} %`;
  }
  function fixerTaille(pourcent) {
    document.documentElement.style.setProperty("--echelle", `${pourcent}%`);
    memoire.ecrire("echelle", pourcent);
    annoncer(`Taille du texte : ${pourcent} %`);
  }
  function pas(delta) {
    const i = Math.max(0, CRANS_TAILLE.indexOf(tailleCourante()));
    fixerTaille(CRANS_TAILLE[Math.min(CRANS_TAILLE.length - 1, Math.max(0, i + delta))]);
  }
  reduire.addEventListener("click", () => pas(-1));
  agrandir.addEventListener("click", () => pas(1));
  normal.addEventListener("click", () => fixerTaille(CRANS_TAILLE[0]));

  // La taille change aussi par les raccourcis du socle : on la mémorise côté pont à chaque cran.
  let enregistree = null;
  new MutationObserver(() => {
    const t = tailleCourante();
    afficherTaille();
    if (t === enregistree) return;
    enregistree = t;
    Promise.resolve(pont.appeler("reglages.ecrire", "taille_texte", t)).catch(() => {});
  }).observe(document.documentElement, { attributes: true, attributeFilter: ["style"] });

  // Même commande que la pastille (`mode.forcer_hors_ligne`, vues/mode.js) : le contrôle est
  // volontairement dupliqué (case à cocher d'un onglet, hors du menu de la pastille) ; les deux
  // sont relus depuis `mode.etat` à l'ouverture de la vue.
  const horsLigne = el("input", { type: "checkbox", id: "parametres-hors-ligne" });
  const etiquetteHL = el("label", { for: "parametres-hors-ligne" }, "Rester hors ligne");
  const aideHL = el(
    "p",
    { class: "parametres-aide" },
    "Aucune requête ne sort de cet ordinateur. Le Mode se règle aussi depuis la pastille en haut.",
  );
  const rangHL = el("div", { class: "parametres-rang" });
  rangHL.append(horsLigne, etiquetteHL);
  horsLigne.addEventListener("change", async () => {
    const cible = horsLigne.checked;
    try {
      const r = await pont.appeler("mode.forcer_hors_ligne", cible);
      if (!r || r.ok === false) throw new Error("refus");
      horsLigne.checked = Boolean(r.force);
    } catch {
      horsLigne.checked = !cible;
      annoncer("Le changement de mode a échoué.");
    }
  });
  bus?.abonner("evenement:mode", (e) => {
    horsLigne.checked = Boolean(e?.force);
  });

  const effacer = el("button", { type: "button", class: "bouton-secondaire", id: "parametres-effacer" }, "Effacer tout l'historique");
  const confirmation = el("div", { class: "parametres-confirmation", role: "status", hidden: "" });
  const messageConf = el("span");
  const annuler = el("button", { type: "button", class: "bouton-secondaire", id: "parametres-effacer-annuler" }, "Annuler");
  confirmation.append(messageConf, annuler);
  const aideEff = el(
    "p",
    { class: "parametres-aide" },
    "Supprime vos conversations et vos retours sur cet ordinateur. Vous pouvez annuler pendant 5 secondes.",
  );
  let minuteur = null;
  function arreterEffacement() {
    clearTimeout(minuteur);
    minuteur = null;
    confirmation.hidden = true;
    effacer.disabled = false;
  }
  effacer.addEventListener("click", () => {
    effacer.disabled = true;
    messageConf.textContent = `L'historique sera effacé dans ${Math.round(delai / 1000)} secondes.`;
    confirmation.hidden = false;
    annuler.focus();
    annoncer("Effacement de l'historique dans 5 secondes. Vous pouvez annuler.");
    minuteur = setTimeout(async () => {
      minuteur = null;
      try {
        const r = await pont.appeler("reglages.effacer_historique");
        if (!r || r.ok === false) throw new Error("refus");
        bus?.emettre("historique:efface", {});
        messageConf.textContent = "Historique effacé.";
        annoncer("Historique effacé.");
      } catch {
        messageConf.textContent = "L'historique n'a pas pu être effacé.";
        annoncer("L'historique n'a pas pu être effacé.");
      }
      annuler.hidden = true;
      effacer.focus(); // le bouton « Annuler » vient de disparaître
      setTimeout(() => {
        arreterEffacement();
        annuler.hidden = false;
      }, 3000);
    }, delai);
  });
  annuler.addEventListener("click", () => {
    arreterEffacement();
    effacer.focus();
    annoncer("Effacement annulé.");
  });

  // Modèle (story 12.15) : liste des modèles embarqués ; le choix vaut au prochain démarrage.
  const choixModele = el("select", { id: "parametres-modele", "aria-describedby": "parametres-modele-aide" });
  const etiquetteModele = el("label", { for: "parametres-modele" }, "Modèle");
  const aideModele = el("p", { class: "parametres-aide", id: "parametres-modele-aide", role: "status" });
  const rangModele = el("div", { class: "parametres-rang" });
  rangModele.append(etiquetteModele, choixModele);
  const MESSAGE_MODELE = "Le changement sera appliqué au prochain démarrage de l'assistant.";
  let modeleActif = null;
  function afficherAideModele(choisi) {
    aideModele.textContent = choisi && choisi !== modeleActif ? MESSAGE_MODELE : "";
  }
  async function chargerModeles() {
    try {
      const r = await pont.appeler("reglages.modeles");
      if (!r || r.ok === false || !Array.isArray(r.modeles)) throw new Error("refus");
      choixModele.replaceChildren(...r.modeles.map((m) => el("option", { value: m.slug }, m.nom ?? m.slug)));
      choixModele.value = r.choisi;
      modeleActif = r.actif;
      afficherAideModele(r.choisi);
    } catch {
      rangModele.hidden = true;
    }
  }
  choixModele.addEventListener("change", async () => {
    const cible = choixModele.value;
    try {
      const r = await pont.appeler("reglages.ecrire", "modele", cible);
      if (!r || r.ok === false) throw new Error("refus");
      afficherAideModele(cible);
      if (cible !== modeleActif) annoncer(MESSAGE_MODELE);
    } catch {
      aideModele.textContent = "Le changement de modèle a échoué.";
      annoncer("Le changement de modèle a échoué.");
      chargerModeles();
    }
  });
  chargerModeles();

  // Fournisseurs externes (story 17.4, amendement 14) : liste ordonnée (ordre d'essai), 3 au
  // plus ; chaque entrée a son preset (qui préremplit URL et modèle), sa clé masquée (jamais
  // relue : seul « clé enregistrée : oui/non » revient du pont) et son test de connexion.
  // Enregistrée par « Enregistrer les fournisseurs » ; appliquée au démarrage suivant.
  const MENTION_GRATUIT = "Accès gratuit OVH, limité à 2 requêtes par minute";
  const RAPPEL_EXTERNE =
    "Le texte de vos demandes est envoyé à ces hôtes ; l'Index et l'historique restent sur le poste.";
  const blocExterne = el("div", { class: "parametres-externes" });
  const listeExterne = el("ol", { class: "parametres-fournisseurs", "aria-label": "Fournisseurs externes, dans l'ordre d'essai" });
  const ajouterExterne = el("button", { type: "button", class: "bouton-secondaire", id: "parametres-externe-ajouter" }, "Ajouter un fournisseur");
  const enregistrerExterne = el("button", { type: "button", class: "bouton-secondaire", id: "parametres-externe-enregistrer" }, "Enregistrer les fournisseurs");
  const etatExterne = el("p", { class: "parametres-aide", id: "parametres-externe-etat", role: "status" });
  const rangExterne = el("div", { class: "parametres-rang" });
  rangExterne.append(ajouterExterne, enregistrerExterne);
  blocExterne.append(
    el("p", { class: "parametres-aide" }, RAPPEL_EXTERNE),
    el("p", { class: "parametres-aide" }, "Ils sont essayés dans l'ordre, puis le modèle local. " + MESSAGE_MODELE),
    listeExterne,
    rangExterne,
    etatExterne,
  );
  const sectionExterne = section("Fournisseurs externes (expérimental)", blocExterne);
  let presets = [];
  let maxExterne = 3;
  let entrees = [];

  function presetDe(nom) {
    return presets.find((p) => p.nom === nom) ?? presets[presets.length - 1];
  }
  function nouvelId() {
    return `f${Date.now().toString(36)}${Math.floor(Math.random() * 1296).toString(36)}`;
  }
  function libelleEntree(i) {
    return `Fournisseur ${i + 1}`;
  }

  function rendreExternes() {
    listeExterne.replaceChildren(
      ...entrees.map((entree, i) => {
        const pref = `parametres-externe-${entree.id}`;
        const li = el("li", { class: "parametres-fournisseur", "data-id": entree.id });
        const titre = el("h4", { id: `${pref}-titre` }, libelleEntree(i));
        li.setAttribute("aria-labelledby", `${pref}-titre`);

        const actif = el("input", { type: "checkbox", id: `${pref}-actif` });
        actif.checked = Boolean(entree.actif);
        actif.addEventListener("change", () => (entree.actif = actif.checked));
        const rangActif = el("div", { class: "parametres-rang" });
        rangActif.append(actif, el("label", { for: `${pref}-actif` }, "Activer"));

        const choixPreset = el("select", { id: `${pref}-preset` });
        choixPreset.replaceChildren(...presets.map((p) => el("option", { value: p.nom }, p.libelle)));
        choixPreset.value = entree.preset;
        const url = el("input", { type: "url", id: `${pref}-url`, inputmode: "url", spellcheck: "false" });
        url.value = entree.url_base ?? "";
        const listeModeles = el("datalist", { id: `${pref}-modeles` });
        const modele = el("input", { type: "text", id: `${pref}-modele`, list: `${pref}-modeles`, spellcheck: "false" });
        modele.value = entree.modele ?? "";
        function proposerModeles() {
          listeModeles.replaceChildren(...presetDe(choixPreset.value).modeles.map((m) => el("option", { value: m })));
        }
        proposerModeles();
        const parametres = el("textarea", { id: `${pref}-parametres`, rows: "2", spellcheck: "false" });
        // Saisie non enregistrée conservée quand la liste est redessinée (déplacement, retrait).
        parametres.value =
          entree._parametres ??
          (Object.keys(entree.parametres_supplementaires ?? {}).length
            ? JSON.stringify(entree.parametres_supplementaires)
            : "");
        const rangParametres = el("div", { class: "parametres-champ" });
        rangParametres.append(el("label", { for: `${pref}-parametres` }, "Paramètres supplémentaires (JSON)"), parametres);
        rangParametres.hidden = !presetDe(choixPreset.value).parametres_libres;

        // Tarif (obligatoire pour un hôte générique, story 17.6) et usage en fin de flux.
        const tarifEntree = el("input", { type: "number", id: `${pref}-tarif-entree`, min: "0", step: "0.01", inputmode: "decimal" });
        const tarifSortie = el("input", { type: "number", id: `${pref}-tarif-sortie`, min: "0", step: "0.01", inputmode: "decimal" });
        tarifEntree.value = entree._tarifEntree ?? (entree.tarif?.entree ?? "");
        tarifSortie.value = entree._tarifSortie ?? (entree.tarif?.sortie ?? "");
        tarifEntree.addEventListener("input", () => (entree._tarifEntree = tarifEntree.value));
        tarifSortie.addEventListener("input", () => (entree._tarifSortie = tarifSortie.value));
        const usageFlux = el("input", { type: "checkbox", id: `${pref}-usage` });
        usageFlux.checked = Boolean(entree.usage_flux);
        usageFlux.addEventListener("change", () => (entree.usage_flux = usageFlux.checked));
        const rangTarif = el("div", { class: "parametres-champ parametres-tarif" });
        const rangUsage = el("div", { class: "parametres-rang" });
        rangUsage.append(usageFlux, el("label", { for: `${pref}-usage` }, "Demander l'usage en fin de flux (stream_options)"));
        rangTarif.append(
          el("label", { for: `${pref}-tarif-entree` }, "Tarif d'entrée (€ par million de tokens, obligatoire)"),
          tarifEntree,
          el("label", { for: `${pref}-tarif-sortie` }, "Tarif de sortie (€ par million de tokens, obligatoire)"),
          tarifSortie,
          rangUsage,
        );
        rangTarif.hidden = !presetDe(choixPreset.value).parametres_libres;

        choixPreset.addEventListener("change", () => {
          const p = presetDe(choixPreset.value);
          entree.preset = p.nom;
          url.value = p.url_base ?? "";
          modele.value = p.modeles[0] ?? "";
          entree.url_base = url.value;
          entree.modele = modele.value;
          proposerModeles();
          rangParametres.hidden = !p.parametres_libres;
          rangTarif.hidden = !p.parametres_libres;
          if (!p.parametres_libres) {
            // Paramètres libres : preset générique seulement (refusés sinon par le pont).
            parametres.value = "";
            entree._parametres = "";
          }
        });
        url.addEventListener("input", () => (entree.url_base = url.value.trim()));
        modele.addEventListener("input", () => (entree.modele = modele.value.trim()));
        parametres.addEventListener("input", () => (entree._parametres = parametres.value));

        const champ = (libelle, controle, id) => {
          const bloc = el("div", { class: "parametres-champ" });
          bloc.append(el("label", { for: id }, libelle), controle);
          return bloc;
        };

        const cle = el("input", { type: "password", id: `${pref}-cle`, autocomplete: "off", spellcheck: "false" });
        // Clé saisie non enregistrée : gardée en mémoire de la page seulement (jamais envoyée
        // sans action), pour survivre au redessin de la liste.
        cle.value = entree._cle ?? "";
        cle.addEventListener("input", () => (entree._cle = cle.value));
        const etatCle = el("span", { class: "parametres-aide", id: `${pref}-cle-etat` }, `Clé enregistrée : ${entree.cle_enregistree ? "oui" : "non"}`);
        cle.setAttribute("aria-describedby", `${pref}-cle-etat`);
        const enregistrerCle = el("button", { type: "button", class: "bouton-secondaire" }, "Enregistrer la clé");
        const effacerCle = el("button", { type: "button", class: "bouton-secondaire" }, "Effacer la clé");
        const majCle = (r) => {
          entree.cle_enregistree = Boolean(r.cle_enregistree);
          etatCle.textContent = `Clé enregistrée : ${entree.cle_enregistree ? "oui" : "non"}`;
        };
        enregistrerCle.addEventListener("click", async () => {
          try {
            // Valeurs de l'entrée : la clé est liée à son hôte et à son preset.
            const r = await pont.appeler("reglages.enregistrer_cle", entree.id, cle.value, valeursEntree(entree));
            if (!r || r.ok === false) throw new Error(r?.erreur?.message ?? "refus");
            cle.value = "";
            entree._cle = "";
            majCle(r);
            annoncer("Clé enregistrée.");
          } catch {
            annoncer("La clé n'a pas pu être enregistrée.");
            etatCle.textContent = "La clé n'a pas pu être enregistrée.";
          }
        });
        effacerCle.addEventListener("click", async () => {
          try {
            const r = await pont.appeler("reglages.effacer_cle", entree.id);
            if (!r || r.ok === false) throw new Error("refus");
            majCle(r);
            annoncer("Clé effacée.");
          } catch {
            annoncer("La clé n'a pas pu être effacée.");
          }
        });
        const rangCle = el("div", { class: "parametres-rang" });
        rangCle.append(enregistrerCle, effacerCle, etatCle);

        // Accès gratuit OVH (story 17.4b) : sans clé, 2 requêtes par minute ; le champ clé est
        // masqué et remplacé par la mention.
        const gratuit = el("input", { type: "checkbox", id: `${pref}-gratuit` });
        gratuit.checked = Boolean(entree.acces_gratuit);
        const rangGratuit = el("div", { class: "parametres-rang" });
        rangGratuit.append(gratuit, el("label", { for: `${pref}-gratuit` }, "Utiliser l'accès gratuit (sans clé)"));
        rangGratuit.hidden = !presetDe(choixPreset.value).acces_gratuit;
        const mentionGratuit = el("p", { class: "parametres-aide", id: `${pref}-mention-gratuit` }, MENTION_GRATUIT);
        const champCle = champ("Clé d'accès", cle, `${pref}-cle`);
        const majGratuit = () => {
          const g = Boolean(entree.acces_gratuit) && Boolean(presetDe(choixPreset.value).acces_gratuit);
          champCle.hidden = g;
          rangCle.hidden = g;
          mentionGratuit.hidden = !g;
        };
        gratuit.addEventListener("change", () => {
          entree.acces_gratuit = gratuit.checked;
          majGratuit();
        });
        choixPreset.addEventListener("change", () => {
          const p = presetDe(choixPreset.value);
          if (!p.acces_gratuit) {
            entree.acces_gratuit = false;
            gratuit.checked = false;
          }
          rangGratuit.hidden = !p.acces_gratuit;
          majGratuit();
        });
        majGratuit();

        const tester = el("button", { type: "button", class: "bouton-secondaire" }, "Tester la connexion");
        const resultat = el("output", { class: "parametres-aide", id: `${pref}-test`, "aria-live": "polite" });
        tester.addEventListener("click", async () => {
          resultat.textContent = "Test en cours…";
          tester.disabled = true;
          try {
            const valeurs = valeursEntree(entree);
            if (cle.value && !entree.acces_gratuit) valeurs.cle = cle.value;
            const r = await pont.appeler("reglages.tester_modele_externe", valeurs);
            if (!r || r.ok === false) throw new Error(r?.erreur?.message ?? "Test impossible.");
            resultat.textContent = r.reussi
              ? `Connexion réussie (${r.latence_ms} ms).${r.debit_restant != null ? ` Débit restant : ${r.debit_restant} requête(s).` : ""}`
              : `Échec de la connexion (${r.motif}).${r.debit_restant != null ? ` Débit restant : ${r.debit_restant} requête(s).` : ""}`;
          } catch (e) {
            if (e instanceof SyntaxError) resultat.textContent = "Paramètres supplémentaires : JSON invalide.";
            else resultat.textContent = e instanceof Error && e.message !== "refus" ? e.message : "Test impossible.";
          } finally {
            tester.disabled = false;
          }
        });
        const rangTest = el("div", { class: "parametres-rang" });
        rangTest.append(tester, resultat);

        const monter_ = el("button", { type: "button", class: "bouton-secondaire", "aria-label": `Monter le ${libelleEntree(i).toLowerCase()}` }, "Monter");
        const descendre = el("button", { type: "button", class: "bouton-secondaire", "aria-label": `Descendre le ${libelleEntree(i).toLowerCase()}` }, "Descendre");
        const retirer = el("button", { type: "button", class: "bouton-secondaire", "aria-label": `Retirer le ${libelleEntree(i).toLowerCase()}` }, "Retirer");
        monter_.disabled = i === 0;
        descendre.disabled = i === entrees.length - 1;
        const deplacer = (j) => {
          [entrees[i], entrees[j]] = [entrees[j], entrees[i]];
          rendreExternes();
          listeExterne.children[j]?.querySelector("h4")?.focus?.();
          annoncer(`${libelleEntree(j)} : ${presetDe(entrees[j].preset).libelle}`);
        };
        monter_.addEventListener("click", () => deplacer(i - 1));
        descendre.addEventListener("click", () => deplacer(i + 1));
        retirer.addEventListener("click", () => {
          entrees.splice(i, 1);
          rendreExternes();
          annoncer("Fournisseur retiré. Enregistrez pour confirmer.");
          ajouterExterne.focus();
        });
        const rangOrdre = el("div", { class: "parametres-rang" });
        rangOrdre.append(monter_, descendre, retirer);

        titre.tabIndex = -1;
        li.append(
          titre,
          rangActif,
          champ("Fournisseur", choixPreset, `${pref}-preset`),
          champ("URL de base", url, `${pref}-url`),
          champ("Modèle", modele, `${pref}-modele`),
          listeModeles,
          rangParametres,
          rangTarif,
          rangGratuit,
          mentionGratuit,
          champCle,
          rangCle,
          rangTest,
          rangOrdre,
        );
        return li;
      }),
    );
    ajouterExterne.disabled = entrees.length >= maxExterne;
  }

  function valeursEntree(entree) {
    const valeurs = {
      id: entree.id,
      preset: entree.preset,
      url_base: entree.url_base ?? "",
      modele: entree.modele ?? "",
      actif: Boolean(entree.actif),
    };
    const texte = (entree._parametres ?? "").trim();
    if (entree._parametres === undefined) valeurs.parametres_supplementaires = entree.parametres_supplementaires ?? {};
    else if (texte) valeurs.parametres_supplementaires = JSON.parse(texte);
    else valeurs.parametres_supplementaires = {};
    if (presetDe(entree.preset).acces_gratuit) valeurs.acces_gratuit = Boolean(entree.acces_gratuit);
    if (presetDe(entree.preset).parametres_libres) {
      const lire = (saisie, enregistre) => (saisie === undefined ? enregistre : saisie === "" ? null : Number(saisie));
      const e = lire(entree._tarifEntree, entree.tarif?.entree ?? null);
      const so = lire(entree._tarifSortie, entree.tarif?.sortie ?? null);
      if (e != null && so != null) valeurs.tarif = { entree: e, sortie: so };
      valeurs.usage_flux = Boolean(entree.usage_flux);
    }
    return valeurs;
  }

  ajouterExterne.addEventListener("click", () => {
    if (entrees.length >= maxExterne || presets.length === 0) return;
    const p = presets[0];
    entrees.push({ id: nouvelId(), preset: p.nom, url_base: p.url_base ?? "", modele: p.modeles[0] ?? "", actif: false, parametres_supplementaires: {}, cle_enregistree: false });
    rendreExternes();
    listeExterne.lastElementChild?.querySelector("select")?.focus();
  });

  enregistrerExterne.addEventListener("click", async () => {
    let valeurs;
    try {
      valeurs = entrees.map(valeursEntree);
    } catch {
      etatExterne.textContent = "Paramètres supplémentaires : JSON invalide.";
      annoncer(etatExterne.textContent);
      return;
    }
    try {
      const r = await pont.appeler("reglages.ecrire", "fournisseurs_externes", valeurs);
      if (!r || r.ok === false) throw new Error(r?.erreur?.message ?? "refus");
      const saisies = new Map(entrees.map((e) => [e.id, e._cle]));
      entrees = (r.fournisseurs ?? entrees).map((e) => ({ ...e, _cle: saisies.get(e.id) }));
      rendreExternes();
      chargerDepense();
      etatExterne.textContent = `Fournisseurs enregistrés. ${MESSAGE_MODELE}`;
    } catch (e) {
      etatExterne.textContent = e instanceof Error && e.message !== "refus" ? e.message : "Les fournisseurs n'ont pas pu être enregistrés.";
    }
    annoncer(etatExterne.textContent);
  });

  async function chargerExternes() {
    try {
      const r = await pont.appeler("reglages.fournisseurs_externes");
      if (!r || r.ok === false || !Array.isArray(r.fournisseurs)) throw new Error("refus");
      presets = Array.isArray(r.presets) ? r.presets : [];
      maxExterne = r.max ?? 3;
      entrees = r.fournisseurs;
      rendreExternes();
      if (r.en_cours) {
        const n = r.en_cours.secours ?? 0;
        etatExterne.textContent = `En service depuis le démarrage : ${r.en_cours.tete}${n ? ` (+${n} en secours)` : ""}.`;
      }
    } catch {
      sectionExterne.hidden = true;
    }
  }
  chargerExternes();

  // -- Dépense et impact (story 17.6) : plafond mensuel par fournisseur, puissance du poste ---
  const listePlafonds = el("ul", { class: "parametres-plafonds" });
  const puissance = el("input", { type: "number", id: "parametres-puissance", min: "1", max: "500", step: "1", inputmode: "numeric" });
  const enregistrerPuissance = el("button", { type: "button", class: "bouton-secondaire" }, "Enregistrer la puissance");
  const rangPuissance = el("div", { class: "parametres-champ" });
  rangPuissance.append(el("label", { for: "parametres-puissance" }, "Puissance moyenne du processeur (W), pour l'impact du modèle local"), puissance, enregistrerPuissance);
  const etatDepense = el("output", { class: "parametres-aide", "aria-live": "polite" });
  const aideDepense = el(
    "p",
    { class: "parametres-aide" },
    "Plafond mensuel en euros par fournisseur externe (2 € par défaut ; 0 désactive le fournisseur), pris en compte dès l'appel suivant. Une demande qui risquerait de le dépasser n'est pas envoyée : le fournisseur suivant, puis le modèle local, répond.",
  );
  const sectionDepense = section("Dépense et impact", aideDepense, listePlafonds, rangPuissance, etatDepense);

  async function chargerDepense() {
    try {
      const r = await pont.appeler("observabilite.reglages");
      if (!r || r.ok === false) throw new Error("refus");
      puissance.value = r.puissance_cpu_w ?? "";
      listePlafonds.replaceChildren(
        ...(r.plafonds ?? []).map((f, i) => {
          const li = el("li", { class: "parametres-rang" });
          const champPlafond = el("input", { type: "number", id: `parametres-plafond-${i}`, min: "0", step: "0.5", inputmode: "decimal" });
          champPlafond.value = f.plafond_eur;
          const bouton = el("button", { type: "button", class: "bouton-secondaire" }, "Enregistrer");
          bouton.addEventListener("click", async () => {
            const rep = await pont.appeler("observabilite.ecrire_plafond", f.hote, Number(champPlafond.value));
            etatDepense.textContent = rep?.ok ? `Plafond enregistré : ${f.libelle}.` : rep?.erreur?.message ?? "Plafond refusé.";
            annoncer(etatDepense.textContent);
          });
          li.append(el("label", { for: `parametres-plafond-${i}` }, `${f.libelle} (€ par mois)`), champPlafond, bouton);
          return li;
        }),
      );
      if (!(r.plafonds ?? []).length) listePlafonds.replaceChildren(el("li", {}, "Aucun fournisseur externe."));
    } catch {
      sectionDepense.hidden = true;
    }
  }
  enregistrerPuissance.addEventListener("click", async () => {
    const rep = await pont.appeler("observabilite.ecrire_puissance", Number(puissance.value));
    etatDepense.textContent = rep?.ok ? "Puissance enregistrée." : rep?.erreur?.message ?? "Puissance refusée.";
    annoncer(etatDepense.textContent);
  });
  chargerDepense();

  general.append(
    section("Taille du texte", rangTaille, aideTaille),
    section("Modèle", rangModele, aideModele),
    sectionExterne,
    sectionDepense,
    section("Connexion", rangHL, aideHL),
    section("Historique", effacer, confirmation, aideEff),
  );

  // -- Retours : le composant de la vue « retours » s'y monte ------------------------------
  const ancreRetours = document.getElementById("ancre-retours");
  if (ancreRetours) panneaux.retours.append(ancreRetours);

  // -- À propos ----------------------------------------------------------------------------
  const apropos = panneaux.apropos;
  let charge = false;

  function rendreAPropos(r) {
    const app = r.application ?? {};
    const modele = r.modele;
    const index = r.index;
    const listeDl = (...lignes) => {
      const dl = el("dl", { class: "parametres-liste" });
      dl.append(...lignes);
      return dl;
    };
    const blocs = [];
    blocs.push(
      section(
        "Versions",
        listeDl(
          ligne("Application", app.version),
          ligne("Empreinte de l'application (SHA-256)", app.empreinte),
          ligne("Modèle embarqué", modele?.slug),
          ...(r.modele_externe
            ? [
                ligne(
                  "Modèle externe",
                  `${r.modele_externe.tete} (${r.modele_externe.hote})` +
                    (r.modele_externe.secours ? `, +${r.modele_externe.secours} en secours` : ""),
                ),
              ]
            : []),
          ligne("Empreinte attendue du modèle (SHA-256)", modele?.sha256_attendu),
          ligne("Index", index?.version),
          ligne("Date de l'Index", index ? formaterDate(index.date_snapshot) : null),
        ),
      ),
    );
    const hotes = Array.isArray(r.liste_blanche) ? r.liste_blanche : [];
    const ul = el("ul", { class: "parametres-hotes", "aria-label": "Sites que l'assistant peut contacter" });
    for (const h of hotes) ul.append(el("li", {}, h));
    blocs.push(
      section(
        "Sites que l'assistant peut contacter",
        el("p", { class: "parametres-aide" }, "Seulement si vous êtes connecté, et seulement ces sites :"),
        hotes.length ? ul : el("p", {}, "Liste non disponible."),
      ),
    );
    const hors = Array.isArray(r.hors_passerelle) ? r.hors_passerelle : [];
    if (hors.length) {
      const dl = el("dl", { class: "parametres-liste" });
      for (const h of hors) dl.append(ligne(h.composant, h.detail));
      blocs.push(section("Ce que l'assistant ne contrôle pas", dl));
    }
    const lic = r.licences ?? { composants: [] };
    const ulLic = el("ul", { class: "parametres-licences" });
    for (const c of lic.composants) ulLic.append(el("li", {}, `${c.nom} : ${c.licence}`));
    const blocLic = section("Licences des composants", lic.composants.length ? ulLic : el("p", {}, "Liste non disponible."));
    if (lic.statut === "provisoire") {
      blocLic.append(el("p", { class: "parametres-aide" }, "Liste provisoire, en cours de vérification."));
    }
    blocs.push(blocLic);
    const m = r.mentions ?? {};
    const mentions = [m.donnees, m.mise_a_jour, m.avertissement_juridique].filter(Boolean);
    blocs.push(section("À savoir", ...mentions.map((t) => el("p", {}, t))));
    apropos.replaceChildren(...blocs);
  }

  async function chargerAPropos() {
    if (charge) return;
    try {
      const r = await pont.appeler("reglages.a_propos");
      if (!r || r.ok === false) throw new Error("refus");
      rendreAPropos(r);
      charge = true;
    } catch {
      apropos.replaceChildren(el("p", { role: "alert" }, "Ces informations n'ont pas pu être lues."));
    }
  }

  racine.append(liste, panneaux.general, panneaux.retours, panneaux.apropos);
  conteneur.replaceChildren(racine);
  choisir("general");
  afficherTaille();

  // État initial : taille mémorisée côté application, et Mode.
  (async () => {
    try {
      const r = await pont.appeler("reglages.lire");
      const t = r?.reglages?.taille_texte;
      if (CRANS_TAILLE.includes(t) && memoire.lire("echelle", null) === null) fixerTaille(t);
      enregistree = tailleCourante();
    } catch {
      /* le pont ne répond pas : valeurs locales */
    }
    try {
      const e = await pont.appeler("mode.etat");
      horsLigne.checked = Boolean(e?.force);
    } catch {
      /* idem */
    }
  })();

  // Rouvrir « Paramètres » relit « À propos » (la Liste blanche peut avoir changé à la relance).
  document.getElementById("bouton-parametres")?.addEventListener("click", () => {
    charge = false;
    if (!panneaux.apropos.hidden) chargerAPropos();
  });
}
