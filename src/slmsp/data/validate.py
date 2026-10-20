"""Étape `validate` : exemples validés contre leurs sources et le Bac à sable (story 9.5, FR-30).

`lancer_validation` produit `runs/data-validate/<run_id>/` à partir d'un run `data-generate`
terminé (`complet` ou `partiel-*` : seules les sessions de `brut.jsonl` sont jugées) :

- `valides.jsonl` : les lignes `SessionBrute` conservées, inchangées ;
- `rejets.jsonl` : `RejetExemple`, une ligne par session écartée, avec son motif ;
- `rapport.json` : par Tâche, nombre d'exemples, de rejets par motif et taux de rejet ;
  `observations` : par Tâche, comptes des écarts non bloquants (`ct_sans_emplacement`).

Contrôles, dans cet ordre ; le premier qui échoue donne le motif :

0. **Provenance** : les règles de provenance de `build` (`LecteurGeneration.amorce_verifiee`,
   `appel_generation`, `data.extraction`), pour que `build` ne refuse aucune session validée.
   Une amorce issue d'une réponse tronquée donne `amorce_tronquee` ; une amorce introuvable,
   altérée (SHA, texte différent de sa réponse) ou d'un appel absent, non `generation`/`ok`
   ou sans texte seul donne `amorce_invalide`. Une réponse tronquée de la session donne
   `reponse_tronquee` ; un appel de la session absent du journal, non `generation`/`ok` ou sans
   gabarit journalisé donne `appel_invalide`.
1. **Rejeu (RD)** : chaque appel d'outil des réponses journalisées est rejoué sur `BacASable`
   avec les cassettes `data/cassettes/` de la session. Un appel hors schéma donne
   `appel_non_conforme` ; une cassette illisible ou d'une autre empreinte d'outils, un appel
   sans équivalent exact enregistré, ou un résultat différent de celui que Mistral a reçu
   donnent `trace_divergente`.
2. **URL** (toutes Tâches) : toute URL de la réponse finale doit figurer dans les passages
   (Q), les résultats d'outils (RD) ou les textes d'amorce (`harness.citations`) :
   `url_inventee`.
3. **Valeurs** (Q, RD, CR, LC, RE, CT, CO) : tout nombre de la réponse finale (`core.texte`,
   URL retirées) doit figurer dans les mêmes sources, en valeur absolue ; les entiers de 0 à 9
   (numérotation, petits comptes) sont ignorés : `valeur_absente`. Pour CO (texte à corriger),
   tout nombre notable du texte de départ doit aussi rester dans la sortie : `infidele`.
   La Tâche `generique` n'a aucune source de référence : ni valeurs ni fidélité.
3 bis. **Structure (CR, CT, LC, story S5)** : CR sans l'une des sections Participants, Points
   abordés, Décisions, Actions (titre en tête de ligne, suite libre) : `cr_sections_manquantes` ;
   CT sans ligne d'objet ou sans formule de politesse : `ct_format_incomplet` (un CT sans
   emplacement entre crochets n'est pas rejeté, il est compté dans `observations` du rapport) ;
   LC dont un nombre notable ou une date de l'entrée manque à la sortie, en chiffres comme en
   lettres courantes : `lc_valeur_perdue`.
4. **Longueur (RE)** : la sortie ne dépasse pas, en mots (`core.texte.compter_mots`), le plafond
   de la `longueur_demandee` de l'amorce (`[re.longueurs]` de `config/evaluation.toml`) :
   `longueur_depassee`.
5. **Fidélité (CR, LC, RE)** : si un contrôleur est fourni (`ControleMistral`, opt-in), Mistral
   compare le texte à sa source (`usage = validation`, gabarit `validation`) : `infidele`. Jamais
   le Juge Claude (AD-3 verrou 6) ; sans contrôleur, la règle automatique ci-dessus fait foi.

Aucun texte généré n'est écrit : `detail` ne porte que des comptes et des identifiants.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, Protocol

from pydantic import ValidationError

from slmsp.core.artefacts import Run, lire, nouveau_run, ouvrir_run
from slmsp.core.canonique import json_canonique, sha256_hex
from slmsp.core.config import plafonds_re_evaluation, racine_projet
from slmsp.core.erreurs import (
    AppelNonConforme,
    BudgetEpuise,
    ManifesteInvalide,
    ProvenanceInvalide,
    ReponseTronquee,
    SlmspError,
)
from slmsp.core.gabarits import GabaritValide, valider_gabarit
from slmsp.core.ports import Passage
from slmsp.core.schemas.amorce import Amorce, texte_mistral_conforme
from slmsp.core.schemas.cassette import Cassette
from slmsp.core.schemas.rejet_donnees import RejetExemple
from slmsp.core.schemas.session_donnees import SessionBrute, SessionPlanifiee
from slmsp.core.texte import compter_mots
from slmsp.data.extraction import extraire_contenu, extraire_message
from slmsp.data.verification import (
    SECTIONS_CR,
    TACHES_A_VALEURS,
    TACHES_VALEURS_CONSERVEES,
    ct_a_emplacement,
    ct_format_manques,
    lc_valeurs_perdues,
    sections_cr_manquantes,
    valeurs_absentes,
    valeurs_perdues,
)
from slmsp.harness.citations import urls_inventees
from slmsp.harness.taches import TableTaches, charger_taches
from slmsp.harness.taches.recherche import contenu_resultat
from slmsp.mcp.bac_a_sable import BacASable
from slmsp.mcp.outils import charger_config
from slmsp.mistral.client import ClientMistral, ErreurApiMistral, ModeleMistralRefuse
from slmsp.mistral.generateur import (
    _textes_resultat,
    message_assistant,
    raison_de_fin,
)
from slmsp.mistral.journal import USAGE_GENERATION, JournalMistral, LigneAppel

__all__ = [
    "GABARIT_VALIDATION",
    "SECTIONS_CR",
    "TACHES_A_VALEURS",
    "TACHES_CONTROLE_FIDELITE",
    "TACHES_VALEURS_CONSERVEES",
    "TYPE_RUN",
    "TYPE_RUN_GENERATE",
    "ControleMistral",
    "ControleurFidelite",
    "LecteurGeneration",
    "ResultatValidation",
    "lancer_validation",
    "statut_herite",
    "taux_par_tache",
]

TYPE_RUN: Final = "data-validate"
TYPE_RUN_GENERATE: Final = "data-generate"
GABARIT_VALIDATION: Final = "validation"
NOM_BRUT: Final = "brut.jsonl"
NOM_PLAN: Final = "plan.jsonl"
NOM_AMORCES: Final = "amorces.jsonl"
NOM_AMORCES_DERIVEES: Final = "amorces-derivees.jsonl"
NOM_VALIDES: Final = "valides.jsonl"
NOM_REJETS: Final = "rejets.jsonl"
NOM_RAPPORT: Final = "rapport.json"
TACHES_CONTROLE_FIDELITE: Final = frozenset({"CR", "LC", "RE"})
"""Tâches dont la fidélité à la source peut être contrôlée par Mistral."""
CARACTERES_PAR_TOKEN: Final = 3


class ControleurFidelite(Protocol):
    """Contrôle de fidélité d'un texte à sa source (Mistral, jamais le Juge Claude)."""

    def __call__(self, session_id: str, source: str, texte: str) -> tuple[bool, str]:
        """`(fidele, detail)` ; `detail` ne contient aucun texte."""
        ...


def _extraire_gabarit(dossier_gabarits: Path) -> GabaritValide:
    return valider_gabarit(
        dossier_gabarits / f"{GABARIT_VALIDATION}.md", cles_optionnelles=("max_tokens",)
    )


class ControleMistral:
    """Contrôle de fidélité par Mistral (`usage = validation`, gabarit `validation`).

    Un appel déjà journalisé pour la même requête est relu, jamais repayé. `BudgetEpuise`
    et les erreurs du client remontent à `lancer_validation`.
    """

    def __init__(
        self,
        client: ClientMistral,
        journal: JournalMistral,
        *,
        dossier_gabarits: str | Path | None = None,
    ) -> None:
        dossier = (
            Path(dossier_gabarits)
            if dossier_gabarits is not None
            else racine_projet() / "config" / "prompts" / "generateur"
        )
        self.client = client
        self.journal = journal
        self.gabarit = _extraire_gabarit(dossier)
        manquants = {"source", "texte"} - set(self.gabarit.emplacements)
        if manquants:
            raise ProvenanceInvalide("gabarit validation : emplacements source et texte requis")
        self.max_tokens = int(self.gabarit.front_matter.get("max_tokens", "1000"))

    def _messages(self, source: str, texte: str) -> list[dict[str, str]]:
        valeurs = {"source": source, "texte": texte}
        consigne = _remplir(self.gabarit.consigne, valeurs)
        return [{"role": "user", "content": consigne}]

    def _relu(self, session_id: str, messages: list[dict[str, str]]) -> str | None:
        if not self.journal.chemin.is_file():
            return None
        for ligne in self.journal.appels_session(session_id):
            if ligne.usage != "validation" or ligne.statut != "ok":
                continue
            try:
                if json.loads(ligne.requete)["messages"] == messages:
                    contenu = message_assistant(ligne.reponse_brute).get("content")
                    if isinstance(contenu, str) and raison_de_fin(ligne.reponse_brute) != "length":
                        return contenu
            except (ValueError, KeyError, TypeError, ProvenanceInvalide):
                continue
        return None

    def __call__(self, session_id: str, source: str, texte: str) -> tuple[bool, str]:
        messages = self._messages(source, texte)
        verdict = self._relu(f"validation-{session_id}", messages)
        if verdict is None:
            caracteres = len(json_canonique(messages))
            verdict = self.client.appeler(
                "validation",
                f"validation-{session_id}",
                messages,
                max_tokens=self.max_tokens,
                tokens_entree_estimes=math.ceil(caracteres / CARACTERES_PAR_TOKEN),
            ).texte
        premier = verdict.strip().split("\n", 1)[0].strip().upper()
        if premier == "FIDELE":
            return True, "contrôle Mistral : fidèle"
        if premier == "INFIDELE":
            return False, "contrôle Mistral : au moins une affirmation non appuyée"
        return False, "contrôle Mistral : verdict illisible"


def _remplir(consigne: str, valeurs: Mapping[str, str]) -> str:
    return re.sub(r"\{([a-z_]+)\}", lambda m: valeurs[m.group(1)], consigne)


# --- Lecture d'un run generate ---------------------------------------------------------------


class LecteurGeneration:
    """Accès en lecture au run `data-generate` et au journal : amorces, plan, réponses.

    Toutes les lectures de fichiers passent par `core.artefacts.lire` (AD-24).
    """

    def __init__(self, generate: Run, journal: JournalMistral, racine: Path) -> None:
        from slmsp.data.generate import _amorces, seed_du_run

        self.run = generate
        self.journal = journal
        self.racine = racine
        seed = ouvrir_run(seed_du_run(generate.run_id, racine=racine), racine=racine)
        self.amorces: dict[str, Amorce] = {a.amorce_id: a for a in _amorces(seed, racine)}
        for ligne in generate.lire_jsonl(NOM_AMORCES_DERIVEES):
            try:
                derivee = Amorce.model_validate(ligne)
            except ValidationError:
                raise ProvenanceInvalide(
                    f"run {generate.run_id} : amorce dérivée non conforme"
                ) from None
            self.amorces[derivee.amorce_id] = derivee
        try:
            plan = [
                SessionPlanifiee.model_validate(ligne) for ligne in generate.lire_jsonl(NOM_PLAN)
            ]
        except ValidationError:
            raise ManifesteInvalide(f"run {generate.run_id} : {NOM_PLAN} illisible") from None
        self.plan = {session.session_id: session for session in plan}
        self._lignes: dict[str, LigneAppel] = {}

    def sessions(self) -> list[SessionBrute]:
        bruts = []
        for ligne in self.run.lire_jsonl(NOM_BRUT):
            try:
                bruts.append(SessionBrute.model_validate(ligne))
            except ValidationError:
                raise ManifesteInvalide(f"run {self.run.run_id} : {NOM_BRUT} illisible") from None
        return bruts

    def appel(self, appel_id: str) -> LigneAppel:
        if appel_id not in self._lignes:
            ligne = self.journal.lire(appel_id)
            if ligne is None or ligne.reponse_brute is None:
                raise ProvenanceInvalide(f"appel {appel_id} absent du journal Mistral")
            self._lignes[appel_id] = ligne
        return self._lignes[appel_id]

    def message(self, appel_id: str) -> dict[str, Any]:
        return message_assistant(self.appel(appel_id).reponse_brute)

    def reponse_finale(self, brut: SessionBrute) -> str:
        contenu = self.message(brut.appel_ids[-1]).get("content")
        if not isinstance(contenu, str) or not contenu:
            raise ProvenanceInvalide(f"appel {brut.appel_ids[-1]} : réponse finale sans contenu")
        return contenu

    def appel_generation(self, appel_id: str) -> LigneAppel:
        """Ligne du journal d'un appel `generation`/`ok` (règle de `build`, AD-3 verrou 4).
        Lève `ProvenanceInvalide`."""
        ligne = self.appel(appel_id)
        if ligne.usage != USAGE_GENERATION:
            raise ProvenanceInvalide(
                f"appel {appel_id} : usage {ligne.usage!r}, {USAGE_GENERATION!r} seul admis"
            )
        if ligne.statut != "ok":
            raise ProvenanceInvalide(f"appel {appel_id} : statut {ligne.statut!r}, « ok » attendu")
        return ligne

    def amorce_verifiee(self, amorce_id: str) -> Amorce:
        """Amorce du seed ou dérivée dont le texte est vérifié (SHA, ou réponse journalisée si
        Mistral), règle de `build`. Lève `ProvenanceInvalide` (`ReponseTronquee` si tronquée)."""
        amorce = self.amorces.get(amorce_id)
        if amorce is None:
            raise ProvenanceInvalide(f"amorce {amorce_id} introuvable (seed ou dérivées)")
        if sha256_hex(amorce.texte) != amorce.sha_texte:
            raise ProvenanceInvalide(f"amorce {amorce_id} : sha_texte ne correspond pas au texte")
        if amorce.auteur_contenu == "mistral":
            assert amorce.appel_id is not None  # garanti par le schéma Amorce
            ligne = self.appel_generation(amorce.appel_id)
            if not texte_mistral_conforme(extraire_contenu(ligne.reponse_brute), amorce):
                raise ProvenanceInvalide(
                    f"amorce {amorce_id} : texte différent de la réponse journalisée "
                    f"{amorce.appel_id}"
                )
        elif amorce.auteur_contenu not in ("public", "config"):
            raise ProvenanceInvalide(
                f"amorce {amorce_id} : auteur_contenu {amorce.auteur_contenu!r}"
            )
        return amorce

    def controler_provenance(self, brut: SessionBrute) -> None:
        """Règles de provenance de `build` sur les amorces et les appels de la session ; lève
        `_Rejet` (`amorce_tronquee`, `amorce_invalide`, `reponse_tronquee`, `appel_invalide`)."""
        for amorce_id in [*brut.amorce_ids, *brut.amorces_derivees]:
            try:
                self.amorce_verifiee(amorce_id)
            except ReponseTronquee as exc:
                raise _Rejet("amorce_tronquee", f"amorce {amorce_id} : {exc}") from None
            except ProvenanceInvalide as exc:
                raise _Rejet("amorce_invalide", str(exc)) from None
        for appel_id in brut.appel_ids:
            try:
                ligne = self.appel_generation(appel_id)
                if ligne.gabarit_id is None or ligne.version_gabarit is None:
                    raise ProvenanceInvalide(f"appel {appel_id} : gabarit non journalisé")
                extraire_message(ligne.reponse_brute)
            except ReponseTronquee as exc:
                raise _Rejet("reponse_tronquee", f"appel {appel_id} : {exc}") from None
            except ProvenanceInvalide as exc:
                raise _Rejet("appel_invalide", str(exc)) from None

    def textes_amorces(self, brut: SessionBrute) -> list[str]:
        """Textes des amorces du seed et des amorces dérivées de la session."""
        textes = []
        for amorce_id in [*brut.amorce_ids, *brut.amorces_derivees]:
            amorce = self.amorces.get(amorce_id)
            if amorce is None:
                raise ProvenanceInvalide(f"amorce {amorce_id} introuvable (seed ou dérivées)")
            textes.append(amorce.texte)
        return textes

    def longueur_demandee(self, brut: SessionBrute) -> str | None:
        """Texte de l'amorce `longueur_demandee` de la session (RE), sinon `None`."""
        for amorce_id in brut.amorce_ids:
            amorce = self.amorces.get(amorce_id)
            if amorce is not None and amorce.emplacement == "longueur_demandee":
                return amorce.texte
        return None

    def entree(self, brut: SessionBrute) -> str:
        """Entrée de l'exemple : textes des amorces du seed (hors amorces dérivées)."""
        amorces = []
        for amorce_id in brut.amorce_ids:
            amorce = self.amorces.get(amorce_id)
            if amorce is None:
                raise ProvenanceInvalide(f"amorce {amorce_id} introuvable (seed)")
            amorces.append(amorce.texte)
        return "\n".join(amorces)

    def passages(self, brut: SessionBrute) -> list[Passage]:
        session = self.plan.get(brut.session_id)
        if session is None or session.passages is None:
            return []
        return [Passage(**p.model_dump()) for p in session.passages]


# --- Rejeu et contrôles ----------------------------------------------------------------------


class _Rejet(Exception):
    def __init__(self, motif: str, detail: str) -> None:
        super().__init__(detail)
        self.motif = motif
        self.detail = detail


def _decoder(arguments: Any) -> Any:
    if isinstance(arguments, str):
        try:
            return json.loads(arguments)
        except ValueError:
            return None
    return arguments


def _rejouer(lecteur: LecteurGeneration, brut: SessionBrute, chemin_outils: Path) -> list[str]:
    """Rejoue les appels d'outils de la session sur le Bac à sable ; renvoie les contenus
    d'outils (messages `tool`) reçus par Mistral. Lève `_Rejet`."""
    cassettes: list[Cassette] = []
    for chemin in brut.cassettes:
        try:
            cassettes.append(
                Cassette.model_validate_json(
                    lire(lecteur.racine / chemin, "data", racine=lecteur.racine)
                )
            )
        except (OSError, ValidationError, SlmspError):
            raise _Rejet("trace_divergente", f"cassette {Path(chemin).name} illisible") from None
    avertissements: list[Any] = []
    try:
        bac = BacASable(cassettes, chemin_outils=chemin_outils, signaler=avertissements.append)
    except SlmspError as exc:
        raise _Rejet(
            "trace_divergente", f"cassettes inutilisables ({type(exc).__name__})"
        ) from None
    resultats: list[str] = []
    for position, appel_id in enumerate(brut.appel_ids):
        appels = lecteur.message(appel_id).get("tool_calls")
        if not appels:
            continue
        if position + 1 >= len(brut.appel_ids):
            raise _Rejet("trace_divergente", "dernier appel avec des appels d'outils")
        suivant = lecteur.appel(brut.appel_ids[position + 1])
        try:
            messages = json.loads(suivant.requete)["messages"]
        except (ValueError, KeyError, TypeError):
            raise _Rejet("trace_divergente", "requête journalisée illisible") from None
        recus = {
            m.get("tool_call_id"): m.get("content")
            for m in messages
            if isinstance(m, Mapping) and m.get("role") == "tool"
        }
        for appel in appels:
            fonction = appel.get("function", {})
            nom, arguments = fonction.get("name"), _decoder(fonction.get("arguments"))
            if not isinstance(nom, str) or not isinstance(arguments, dict):
                raise _Rejet("appel_non_conforme", "appel d'outil mal formé")
            try:
                reponse = bac.appeler(nom, arguments)
            except AppelNonConforme as exc:
                raise _Rejet("appel_non_conforme", f"{nom} : {type(exc).__name__}") from None
            except SlmspError as exc:
                raise _Rejet(
                    "trace_divergente", f"{nom} : rejeu en échec ({type(exc).__name__})"
                ) from None
            if avertissements:
                raise _Rejet(
                    "trace_divergente", f"{nom} : aucune interaction identique enregistrée"
                )
            contenu = recus.get(appel.get("id"))
            formes = [contenu_resultat(reponse), *_textes_resultat(reponse.get("result"))]
            if not isinstance(contenu, str) or contenu not in formes:
                raise _Rejet("trace_divergente", f"{nom} : résultat différent de la cassette")
            resultats.append(contenu)
    if len(cassettes) != sum(1 for a in brut.appel_ids if lecteur.message(a).get("tool_calls")):
        raise _Rejet("trace_divergente", "nombre de cassettes différent du nombre de tours")
    return resultats


def _controler_sources(
    texte: str,
    tache: str,
    passages: Sequence[Passage],
    outils: Sequence[str],
    fournis: Sequence[str],
) -> None:
    """Règles partagées de `slmsp.data.verification` ; lève `_Rejet`."""
    inventees = urls_inventees(texte, passages, outils, fournis)
    if inventees:
        raise _Rejet("url_inventee", f"{len(inventees)} URL absente(s) des sources")
    absents = valeurs_absentes(texte, tache, passages, outils, fournis)
    if absents:
        raise _Rejet("valeur_absente", f"{len(absents)} valeur(s) absente(s) des sources")
    if tache in TACHES_VALEURS_CONSERVEES:
        perdues = valeurs_perdues(texte, fournis)
        if perdues:
            raise _Rejet("infidele", f"{len(perdues)} valeur(s) de la source perdue(s)")


OBSERVATION_CT_SANS_EMPLACEMENT: Final = "ct_sans_emplacement"
"""Observation (non bloquante) : CT sans emplacement entre crochets. La demande ne dit pas
quels champs sont inconnus : un courrier sans crochet n'est pas rejeté, il est compté dans
`observations` du rapport (revue S5)."""


def _controler_structure(texte: str, tache: str, fournis: Sequence[str]) -> list[str]:
    """Contrôles de structure de la story S5 (règles de `slmsp.data.verification`) ; lève
    `_Rejet`, rend les observations non bloquantes.

    CR : les quatre titres de `SECTIONS_CR`, chacun en tête de ligne
    (`cr_sections_manquantes`). CT : une ligne d'objet et une formule de politesse
    (`ct_format_incomplet`) ; sans emplacement entre crochets, observation
    `OBSERVATION_CT_SANS_EMPLACEMENT`. LC : chaque nombre notable et chaque date de l'entrée
    figure à la sortie, en chiffres ou en lettres courantes (`lc_valeur_perdue`) ; un nombre
    de la sortie absent de l'entrée est déjà refusé par `_controler_sources`
    (`valeur_absente`).
    """
    if tache == "CR":
        manquantes = sections_cr_manquantes(texte)
        if manquantes:
            raise _Rejet("cr_sections_manquantes", f"sections absentes : {', '.join(manquantes)}")
    elif tache == "CT":
        manques = ct_format_manques(texte)
        if manques:
            raise _Rejet("ct_format_incomplet", f"absents : {', '.join(manques)}")
        if not ct_a_emplacement(texte):
            return [OBSERVATION_CT_SANS_EMPLACEMENT]
    elif tache == "LC":
        nombres, dates_perdues = lc_valeurs_perdues(texte, fournis)
        if nombres or dates_perdues:
            raise _Rejet(
                "lc_valeur_perdue",
                f"{len(nombres)} nombre(s) et {len(dates_perdues)} date(s) de l'entrée perdus",
            )
    return []


def _controler_longueur(texte: str, longueur: str | None) -> None:
    """Rejette un résumé RE plus long que le plafond de sa `longueur_demandee`."""
    plafond = plafonds_re_evaluation().get(longueur or "")
    if plafond is None:
        raise ProvenanceInvalide(
            "Tâche RE : longueur_demandee absente ou inconnue de [re.longueurs]"
        )
    mots = compter_mots(texte)
    if mots > plafond:
        raise _Rejet("longueur_depassee", f"{mots} mots pour un plafond de {plafond}")


@dataclass(frozen=True)
class ResultatValidation:
    """Run produit, statut final et rapport."""

    run: Run
    statut: str
    rapport: dict[str, Any]


def _source_fidelite(lecteur: LecteurGeneration, brut: SessionBrute) -> str:
    if brut.tache == "CR":
        return lecteur.message(brut.appel_ids[0]).get("content", "") or ""
    return "\n".join(lecteur.textes_amorces(brut))


def _controler_derivation(
    lecteur: LecteurGeneration, taches: TableTaches, brut: SessionBrute
) -> None:
    """Refus de `build` indépendants de la licence : entrée de la Tâche, cassettes, conversation.

    Règle partagée avec `build` (`construire_conversation`, import différé : `build` importe
    ce module). Les licences et la variante restent propres à `build` (AD-17).
    """
    from slmsp.data.build import DerivationRefusee, construire_conversation

    try:
        construire_conversation(lecteur, taches, brut)
    except DerivationRefusee as exc:
        raise _Rejet(exc.motif, exc.detail) from None
    except ReponseTronquee as exc:
        raise _Rejet("reponse_tronquee", str(exc)) from None
    except ProvenanceInvalide as exc:
        raise _Rejet("appel_invalide", str(exc)) from None


def valider_session(
    lecteur: LecteurGeneration,
    brut: SessionBrute,
    *,
    chemin_outils: Path,
    controle: ControleurFidelite | None = None,
    taches: TableTaches | None = None,
) -> list[str]:
    """Valide une session ; lève `_Rejet` (motif de `MOTIFS_VALIDATION`) si elle est écartée,
    sinon rend ses observations non bloquantes (`OBSERVATION_CT_SANS_EMPLACEMENT`)."""
    lecteur.controler_provenance(brut)
    outils: list[str] = []
    if brut.tache == "RD":
        outils = _rejouer(lecteur, brut, chemin_outils)
    _controler_derivation(lecteur, taches if taches is not None else charger_taches(), brut)
    texte = lecteur.reponse_finale(brut)
    fournis = lecteur.textes_amorces(brut)
    if brut.tache == "CR":
        fournis = [*fournis, _source_fidelite(lecteur, brut)]
    _controler_sources(texte, brut.tache, lecteur.passages(brut), outils, fournis)
    observations = _controler_structure(texte, brut.tache, fournis)
    if brut.tache == "RE":
        _controler_longueur(texte, lecteur.longueur_demandee(brut))
    if controle is not None and brut.tache in TACHES_CONTROLE_FIDELITE:
        fidele, detail = controle(brut.session_id, _source_fidelite(lecteur, brut), texte)
        if not fidele:
            raise _Rejet("infidele", detail)
    return observations


def taux_par_tache(
    entrees: Mapping[str, int], rejets: Mapping[str, Mapping[str, int]]
) -> dict[str, Any]:
    """Rapport FR-30 : par Tâche, exemples, rejets par motif et taux de rejet, puis total."""
    rapport: dict[str, Any] = {}
    total_entrees, total_rejets = 0, 0
    total_motifs: Counter[str] = Counter()
    for tache in sorted(entrees):
        motifs = dict(sorted(rejets.get(tache, {}).items()))
        nb_rejets = sum(motifs.values())
        rapport[tache] = {
            "exemples": entrees[tache],
            "retenus": entrees[tache] - nb_rejets,
            "rejets": motifs,
            "taux_rejet": round(nb_rejets / entrees[tache], 6) if entrees[tache] else 0.0,
        }
        total_entrees += entrees[tache]
        total_rejets += nb_rejets
        total_motifs.update(motifs)
    rapport["total"] = {
        "exemples": total_entrees,
        "retenus": total_entrees - total_rejets,
        "rejets": dict(sorted(total_motifs.items())),
        "taux_rejet": round(total_rejets / total_entrees, 6) if total_entrees else 0.0,
    }
    return rapport


def statut_herite(parent: Run, statut: str, motif: str | None) -> tuple[str, str | None]:
    """Statut d'un run qui a traité tout son parent : un parent non `complet` le rend partiel.

    Le parent `partiel-*` transmet son statut ; un autre statut (`interrompu`) donne
    `partiel-erreur`. Un statut propre déjà partiel est gardé.
    """
    statut_parent = parent.statut_courant()
    if statut != "complet" or statut_parent == "complet":
        return statut, motif
    herite = statut_parent if statut_parent.startswith("partiel-") else "partiel-erreur"
    return herite, f"run parent {parent.run_id} {statut_parent}"


def ouvrir_generation(run_id: str, racine: Path) -> Run:
    """Run `data-generate` `run_id`, ou `ManifesteInvalide`."""
    run = ouvrir_run(run_id, racine=racine)
    if run.type != TYPE_RUN_GENERATE:
        raise ManifesteInvalide(f"run {run_id} : type {run.type!r}, {TYPE_RUN_GENERATE} attendu")
    if run.statut_courant() == "en_cours":
        raise ManifesteInvalide(f"run {run_id} encore en cours")
    return run


def lancer_validation(
    *,
    racine: str | Path,
    generate_run_id: str,
    journal: JournalMistral,
    controle: ControleurFidelite | None = None,
    chemin_outils: str | Path | None = None,
    taches: TableTaches | None = None,
    consigner: Callable[[str], None] = print,
) -> ResultatValidation:
    """Crée `runs/data-validate/<run_id>/` depuis le run `data-generate` `generate_run_id`.

    `journal` : journal Mistral ouvert en lecture (`lecteur="data"`). Lève, sans rien écrire,
    `ManifesteInvalide` (run absent, d'un autre type, en cours, sans `brut.jsonl`) ou
    `ProvenanceInvalide` (seed ou amorce dérivée illisible). Un appel ou une amorce introuvable
    pendant la validation rejette la session (`appel_invalide`, `amorce_invalide`).
    `BudgetEpuise` pendant le contrôle de fidélité donne un run
    `partiel-budget` : les sessions non jugées sont absentes des deux fichiers et comptées
    dans `non_jugees`. Une erreur d'API donne `partiel-erreur`. Un run `generate` partiel
    rend le run `validate` partiel (`statut_herite`).
    """
    base = Path(racine).resolve()
    if taches is None:
        taches = charger_taches()
    outils = Path(
        chemin_outils
        if chemin_outils is not None
        else racine_projet() / "config" / "outils-mcp.toml"
    ).resolve()
    charger_config(outils)  # ConfigurationInvalide avant tout run
    generate = ouvrir_generation(generate_run_id, base)
    if not (generate.dossier / NOM_BRUT).is_file():
        raise ManifesteInvalide(f"run {generate_run_id} : {NOM_BRUT} absent, rien à valider")
    lecteur = LecteurGeneration(generate, journal, base)
    sessions = lecteur.sessions()
    run = nouveau_run(
        TYPE_RUN,
        "validate",
        {"generate_run_id": generate_run_id, "controle_mistral": controle is not None},
        parents=[generate_run_id],
        entrees={"brut": generate.dossier / NOM_BRUT, "outils-mcp": outils},
        racine=base,
    )
    entrees: Counter[str] = Counter()
    rejets: dict[str, Counter[str]] = {}
    observations: dict[str, Counter[str]] = {}
    statut, motif = "complet", None
    try:
        for brut in sessions:
            try:
                vues = valider_session(
                    lecteur, brut, chemin_outils=outils, controle=controle, taches=taches
                )
            except _Rejet as rejet:
                run.ajouter_jsonl(
                    NOM_REJETS,
                    RejetExemple(
                        session_id=brut.session_id,
                        tache=brut.tache,
                        etape="validate",
                        motif=rejet.motif,  # type: ignore[arg-type]
                        detail=rejet.detail,
                    ).model_dump(mode="json"),
                )
                rejets.setdefault(brut.tache, Counter())[rejet.motif] += 1
            else:
                run.ajouter_jsonl(NOM_VALIDES, brut.model_dump(mode="json"))
                observations.setdefault(brut.tache, Counter()).update(vues)
            entrees[brut.tache] += 1
    except BudgetEpuise as exc:
        statut, motif = "partiel-budget", str(exc)
    except (ErreurApiMistral, ModeleMistralRefuse) as exc:
        statut, motif = "partiel-erreur", f"{type(exc).__name__} : {exc}"
    except KeyboardInterrupt:
        run.terminer("interrompu", "interruption clavier")
        raise
    except BaseException as exc:
        run.terminer("partiel-erreur", f"{type(exc).__name__} : {exc}")
        raise
    statut, motif = statut_herite(generate, statut, motif)
    rapport = {
        "schema_version": 1,
        "statut": statut,
        "motif": motif,
        "non_jugees": len(sessions) - sum(entrees.values()),
        "taches": taux_par_tache(entrees, rejets),
        "observations": {
            tache: dict(sorted(compte.items()))
            for tache, compte in sorted(observations.items())
            if compte
        },
    }
    run.ecrire(NOM_RAPPORT, json_canonique(rapport) + b"\n")
    run.terminer(statut, motif)
    consigner(f"validate : {rapport['taches']['total']['retenus']} exemples retenus")
    return ResultatValidation(run=run, statut=statut, rapport=rapport)
