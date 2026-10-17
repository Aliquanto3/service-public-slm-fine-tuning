"""Étape `validate` : exemples validés contre leurs sources et le Bac à sable (story 9.5, FR-30).

`lancer_validation` produit `runs/data-validate/<run_id>/` à partir d'un run `data-generate`
terminé (`complet` ou `partiel-*` : seules les sessions de `brut.jsonl` sont jugées) :

- `valides.jsonl` : les lignes `SessionBrute` conservées, inchangées ;
- `rejets.jsonl` : `RejetExemple`, une ligne par session écartée, avec son motif ;
- `rapport.json` : par Tâche, nombre d'exemples, de rejets par motif et taux de rejet.

Contrôles, dans cet ordre ; le premier qui échoue donne le motif :

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
from decimal import Decimal
from pathlib import Path
from typing import Any, Final, Protocol

from pydantic import ValidationError

from slmsp.core.artefacts import Run, lire, nouveau_run, ouvrir_run
from slmsp.core.canonique import json_canonique
from slmsp.core.config import plafonds_re_evaluation, racine_projet
from slmsp.core.erreurs import (
    AppelNonConforme,
    BudgetEpuise,
    ManifesteInvalide,
    ProvenanceInvalide,
    SlmspError,
)
from slmsp.core.gabarits import GabaritValide, valider_gabarit
from slmsp.core.ports import Passage
from slmsp.core.schemas.amorce import Amorce
from slmsp.core.schemas.cassette import Cassette
from slmsp.core.schemas.rejet_donnees import RejetExemple
from slmsp.core.schemas.session_donnees import SessionBrute, SessionPlanifiee
from slmsp.core.texte import compter_mots, extraire_nombres
from slmsp.harness.citations import extraire_urls, urls_inventees
from slmsp.harness.taches.recherche import contenu_resultat
from slmsp.mcp.bac_a_sable import BacASable
from slmsp.mcp.outils import charger_config
from slmsp.mistral.client import ClientMistral, ErreurApiMistral, ModeleMistralRefuse
from slmsp.mistral.generateur import (
    _textes_resultat,
    message_assistant,
    raison_de_fin,
)
from slmsp.mistral.journal import JournalMistral, LigneAppel

__all__ = [
    "GABARIT_VALIDATION",
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
TACHES_A_VALEURS: Final = frozenset({"Q", "RD", "CR", "LC", "RE", "CT", "CO"})
"""Tâches dont la réponse doit rester appuyée par des valeurs de sa source."""
TACHES_VALEURS_CONSERVEES: Final = frozenset({"CO"})
"""Tâches dont la sortie doit garder toutes les valeurs notables de sa source (règle de
fidélité automatique : une correction ne change ni dates ni montants)."""
TACHES_CONTROLE_FIDELITE: Final = frozenset({"CR", "LC", "RE"})
"""Tâches dont la fidélité à la source peut être contrôlée par Mistral."""
ENTIER_IGNORE_MAX: Final = 9
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


def _nombres_notables(texte: str) -> set[Decimal]:
    return {
        abs(n)
        for n in extraire_nombres(texte)
        if not (n == n.to_integral_value() and abs(n) <= ENTIER_IGNORE_MAX)
    }


def _sans_urls(texte: str) -> str:
    for url in extraire_urls(texte):
        texte = texte.replace(url, " ")
    return texte


_MOIS: Final = {
    mois: numero
    for numero, mois in enumerate(
        (
            "janvier février mars avril mai juin juillet août septembre octobre novembre décembre"
        ).split(),
        start=1,
    )
}
_DATE: Final = re.compile(
    r"(?<![\w.,/-])(?:"
    r"(?P<iso_a>\d{4})-(?P<iso_m>\d{1,2})-(?P<iso_j>\d{1,2})"
    r"|(?P<num_j>\d{1,2})[/.-](?P<num_m>\d{1,2})[/.-](?P<num_a>\d{4})"
    r"|(?P<lit_j>\d{1,2})(?:er)?\s+(?P<lit_m>[A-Za-zéèêûôîàç]+)\s+(?P<lit_a>\d{4})"
    r")(?![\w,/-]|\.\d)",
    re.IGNORECASE,
)
_ANNOTATION_MOTS: Final = re.compile(
    r"(?<![\w,.])(?:\d{1,3}(?:[    ]\d{3})+|\d+)\s*mots?\b", re.IGNORECASE
)
"""Compte de mots écrit par le générateur (« (80 mots max.) », « de 200 mots au plus ») :
seul le nombre suivi de « mots » est retiré ; le reste d'une parenthèse reste contrôlé."""


def _dates(texte: str) -> list[tuple[re.Match[str], tuple[int, int, int]]]:
    """Dates du texte (ISO, jj/mm/aaaa, « 20 avril 2021 ») avec leur forme (année, mois, jour)."""
    trouvees = []
    for m in _DATE.finditer(texte):
        if m["iso_a"]:
            a, mois, j = m["iso_a"], m["iso_m"], m["iso_j"]
        elif m["num_a"]:
            a, mois, j = m["num_a"], m["num_m"], m["num_j"]
        else:
            mois = str(_MOIS.get(m["lit_m"].lower(), 0))
            a, j = m["lit_a"], m["lit_j"]
        if 1 <= int(mois) <= 12 and 1 <= int(j) <= 31:
            trouvees.append((m, (int(a), int(mois), int(j))))
    return trouvees


def _retirer_dates_connues(texte: str, connues: set[tuple[int, int, int]]) -> str:
    """Retire du texte les dates déjà présentes (sous une autre forme) dans les sources."""
    for m, forme in reversed(_dates(texte)):
        if forme in connues:
            texte = texte[: m.start()] + " " + texte[m.end() :]
    return texte


def _controler_sources(
    texte: str,
    tache: str,
    passages: Sequence[Passage],
    outils: Sequence[str],
    fournis: Sequence[str],
) -> None:
    inventees = urls_inventees(texte, passages, outils, fournis)
    if inventees:
        raise _Rejet("url_inventee", f"{len(inventees)} URL absente(s) des sources")
    if tache not in TACHES_A_VALEURS:
        return
    connus: set[Decimal] = set()
    dates_connues: set[tuple[int, int, int]] = set()
    for source in (*(p.titre for p in passages), *(p.texte for p in passages), *outils, *fournis):
        connus |= {abs(n) for n in extraire_nombres(source)}
        dates_connues |= {forme for _, forme in _dates(source)}
    controle = texte
    if tache == "RE":
        # Le compte de mots recopié du gabarit (« (80 mots max.) ») n'est pas une valeur du
        # résumé ; un plafond écrit comme valeur libre (« 200 euros ») reste contrôlé.
        controle = _ANNOTATION_MOTS.sub(" ", controle)
    sortie = _nombres_notables(_retirer_dates_connues(_sans_urls(controle), dates_connues))
    absents = sortie - connus
    if absents:
        raise _Rejet("valeur_absente", f"{len(absents)} valeur(s) absente(s) des sources")
    if tache in TACHES_VALEURS_CONSERVEES:
        perdues = set().union(*(_nombres_notables(_sans_urls(f)) for f in fournis)) - (
            _nombres_notables(_sans_urls(texte))
        )
        if perdues:
            raise _Rejet("infidele", f"{len(perdues)} valeur(s) de la source perdue(s)")


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


def valider_session(
    lecteur: LecteurGeneration,
    brut: SessionBrute,
    *,
    chemin_outils: Path,
    controle: ControleurFidelite | None = None,
) -> None:
    """Valide une session ; lève `_Rejet` (motif de `MOTIFS_VALIDATION`) si elle est écartée."""
    outils: list[str] = []
    if brut.tache == "RD":
        outils = _rejouer(lecteur, brut, chemin_outils)
    texte = lecteur.reponse_finale(brut)
    fournis = lecteur.textes_amorces(brut)
    if brut.tache == "CR":
        fournis = [*fournis, _source_fidelite(lecteur, brut)]
    _controler_sources(texte, brut.tache, lecteur.passages(brut), outils, fournis)
    if brut.tache == "RE":
        _controler_longueur(texte, lecteur.longueur_demandee(brut))
    if controle is not None and brut.tache in TACHES_CONTROLE_FIDELITE:
        fidele, detail = controle(brut.session_id, _source_fidelite(lecteur, brut), texte)
        if not fidele:
            raise _Rejet("infidele", detail)


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
    consigner: Callable[[str], None] = print,
) -> ResultatValidation:
    """Crée `runs/data-validate/<run_id>/` depuis le run `data-generate` `generate_run_id`.

    `journal` : journal Mistral ouvert en lecture (`lecteur="data"`). Lève, sans rien écrire,
    `ManifesteInvalide` (run absent, d'un autre type, en cours, sans `brut.jsonl`) ou
    `ProvenanceInvalide` (seed ou amorce dérivée illisible). Un appel ou une amorce introuvable
    pendant la validation lève `ProvenanceInvalide` après création du run, clos en
    `partiel-erreur`. `BudgetEpuise` pendant le contrôle de fidélité donne un run
    `partiel-budget` : les sessions non jugées sont absentes des deux fichiers et comptées
    dans `non_jugees`. Une erreur d'API donne `partiel-erreur`. Un run `generate` partiel
    rend le run `validate` partiel (`statut_herite`).
    """
    base = Path(racine).resolve()
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
    statut, motif = "complet", None
    try:
        for brut in sessions:
            try:
                valider_session(lecteur, brut, chemin_outils=outils, controle=controle)
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
    }
    run.ecrire(NOM_RAPPORT, json_canonique(rapport) + b"\n")
    run.terminer(statut, motif)
    consigner(f"validate : {rapport['taches']['total']['retenus']} exemples retenus")
    return ResultatValidation(run=run, statut=statut, rapport=rapport)
