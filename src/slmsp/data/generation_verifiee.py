"""Génération vérifiée, partie vérification (story O6a, méthodologie v2).

`Verificateur` est branché sur `lancer_generation` (`slmsp data generate --verifiee`) : chaque
session CR, LC, CT terminée par le Générateur passe, avant d'entrer dans `brut.jsonl` :

1. les **contrôles déterministes** (`slmsp.data.verification.verifier_cible`) ;
2. s'ils passent et sauf `sans_juge`, le **juge de données** O1
   (`JugeDonnees.juger_candidat`, DeepSeek via OpenRouter, cache par empreinte).

Acceptée : la session entre dans `brut.jsonl` (format `SessionBrute` inchangé). Refusée : elle
est **écartée** (`ecartees.jsonl`) et close par un `AbandonSession` de motif
`verification_refusee`, pour que la reprise ne la rejoue pas. En O6a, une session n'a qu'un
essai (la régénération par Mistral avec le motif du refus vient avec O6b).

Fichiers du run `data-generate` :

- `verification.jsonl` : une ligne par session vérifiée (essais, appels, motifs, candidat et
  clé du verdict O1, issue) ;
- `verdicts.jsonl` : lignes du juge O1 (même format que `data juger`, index du cache) ;
- `ecartees.jsonl` : sessions écartées avec leurs codes ;
- `interruptions-juge.jsonl` : verdicts `non-juge` ou `invalide` ; la session reste ouverte
  (rejouée à la reprise, sans repayer Mistral) jusqu'à `INTERRUPTIONS_MAX`, puis écartée ;
- à la fin d'un run `complet` : `rapport.json`, `echantillon.md` (cibles retenues et écartées
  tirées par graine, pour relecture) et `calibrage.md` (refus des contrôles tirés par graine,
  pour repérer les faux positifs avant tout appel payant).

Aucun texte n'est rédigé par l'outillage : les fichiers Markdown citent les cibles Mistral
journalisées et les motifs des contrôles (D1).
"""

from __future__ import annotations

import json
import random
from collections import Counter
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from pydantic import ValidationError

from slmsp.budget.tarifs import cout_pire_cas
from slmsp.core.artefacts import Run
from slmsp.core.canonique import json_canonique, sha256_hex
from slmsp.core.erreurs import ProvenanceInvalide, SlmspError
from slmsp.core.schemas.amorce import Amorce
from slmsp.core.schemas.session_donnees import AbandonSession, SessionBrute
from slmsp.data.config import VerificationConfig
from slmsp.data.juge_donnees import (
    INTERRUPTIONS_MAX,
    TENTATIVES_MAX,
    FileOrdonnee,
    JugeDonnees,
    PlafondEstimeDepasse,
    VerdictDonnees,
    source_session,
)
from slmsp.data.validate import LecteurGeneration
from slmsp.data.verification import TACHES_VERIFIEES, Motif, refusee, verifier_cible
from slmsp.fournisseurs.client import MODE
from slmsp.mistral.journal import JournalMistral

__all__ = [
    "MOTIF_ABANDON",
    "NOM_CALIBRAGE",
    "NOM_ECARTEES",
    "NOM_ECHANTILLON",
    "NOM_RAPPORT",
    "NOM_VERDICTS",
    "NOM_VERIFICATION",
    "Verificateur",
    "rapport_verification",
]

NOM_VERIFICATION: Final = "verification.jsonl"
NOM_VERDICTS: Final = "verdicts.jsonl"
NOM_ECARTEES: Final = "ecartees.jsonl"
NOM_INTERRUPTIONS: Final = "interruptions-juge.jsonl"
NOM_RAPPORT: Final = "rapport.json"
NOM_ECHANTILLON: Final = "echantillon.md"
NOM_CALIBRAGE: Final = "calibrage.md"
NOM_BILAN: Final = "bilan.jsonl"
NOM_AMORCES_DERIVEES: Final = "amorces-derivees.jsonl"
MOTIF_ABANDON: Final = "verification_refusee"
ENTREE_SESSION_TOKENS_PIRE: Final = 6000
"""Tokens d'entrée comptés par session, en plus de la grille, pour la source et la cible dans
l'estimation pire cas du juge (CR : transcription et compte rendu ≈ 3 000 tokens observés)."""
ESSAIS_O6A: Final = 1
"""Essais faits en O6a : la régénération (essais 2 et 3) vient avec O6b."""


def _motifs_juge(verdict: VerdictDonnees, seuils: Mapping[str, float]) -> list[Motif]:
    """Un motif par critère sous son seuil ; message et extraits du juge (extraits vérifiés)."""
    return [
        Motif(
            f"juge_{critere}",
            critere,
            True,
            verdict.motifs.get(critere, ""),
            tuple(verdict.extraits.get(critere, [])),
        )
        for critere, seuil in seuils.items()
        if verdict.notes.get(critere, 0.0) < seuil
    ]


@dataclass(frozen=True)
class _Preparation:
    """Session après les contrôles déterministes, en attente du juge (ou non)."""

    brut: SessionBrute
    essai: dict[str, Any]
    motifs: list[Motif]
    source: str
    cible: str
    a_juger: bool


class Verificateur:
    """Vérification des sessions CR, LC, CT d'un run `data-generate` (voir le module)."""

    taches: tuple[str, ...] = TACHES_VERIFIEES

    def __init__(
        self,
        config: VerificationConfig,
        *,
        plafonds_mots: Mapping[str, int] | None = None,
        juge: JugeDonnees | None = None,
        essais_max: int | None = None,
        plafond_estime_openrouter: float | None = None,
    ) -> None:
        self.config = config
        self.plafonds_mots = dict(plafonds_mots or {})
        self.juge = juge
        self.essais_max = essais_max if essais_max is not None else config.essais_max
        if not 1 <= self.essais_max <= 3:
            raise ValueError("essais_max dans [1, 3] attendu")
        if self.essais_max > ESSAIS_O6A:
            # Revue O6a : un run créé avec essais_max 3 annoncerait des régénérations absentes
            # et changerait de comportement à sa reprise après O6b.
            raise ValueError(
                f"essais_max {self.essais_max} : un seul essai tant que la régénération "
                "(story O6b) n'est pas livrée"
            )
        self._file: FileOrdonnee | None = None
        self.plafond_estime_openrouter = plafond_estime_openrouter
        self._run: Run | None = None
        self._lecteur: LecteurGeneration | None = None
        self._interruptions: Counter[str] = Counter()
        self._cout_depart = 0.0 if juge is None else juge.cout_total

    # --- Avant le run ------------------------------------------------------------------------

    def description(self) -> dict[str, Any]:
        """Réglages inscrits dans la config du run (relus à la reprise)."""
        regles = self.config.model_dump(mode="json")
        return {
            "taches": list(self.taches),
            "essais_max": self.essais_max,
            "essais_faits": ESSAIS_O6A,
            "sans_juge": self.juge is None,
            "regles_sha256": sha256_hex(json_canonique(regles)),
            "non_bloquants": list(self.config.non_bloquants),
            "plafonds_mots": self.plafonds_mots,
            "juge": None if self.juge is None else self.juge.description(),
        }

    def estimer_pire_cas(self, taches_sessions: Iterable[str]) -> float:
        """Coût OpenRouter pire cas (€) des sessions à vérifier, sans cache (la cible n'est pas
        connue avant la génération) : `TENTATIVES_MAX` appels par essai, au `max_tokens` du
        juge, entrée = grille + `ENTREE_SESSION_TOKENS_PIRE`."""
        if self.juge is None:
            return 0.0
        juge = self.juge
        registre = juge.client.registre
        registre.verifier_usage(juge.config.usage_budget)
        par_tache: dict[str, float] = {}
        total = 0.0
        for tache in taches_sessions:
            if tache not in self.taches:
                continue
            if tache not in par_tache:
                grille = juge.grilles[tache].texte
                entree = juge.tokens_entree(tache, grille) + ENTREE_SESSION_TOKENS_PIRE
                par_tache[tache] = TENTATIVES_MAX * cout_pire_cas(
                    registre.tarifs,
                    juge.config.modele,
                    MODE,
                    entree,
                    juge.config.max_tokens,
                    registre.config.majoration_entree,
                )
            total += par_tache[tache] * ESSAIS_O6A
        return total

    def borner(self, taches_sessions: Sequence[str], consigner: Callable[[str], None]) -> None:
        """Affiche l'estimation OpenRouter ; lève `PlafondEstimeDepasse` au-delà du plafond."""
        a_verifier = [t for t in taches_sessions if t in self.taches]
        if self.essais_max > ESSAIS_O6A:
            consigner(
                f"vérification : {ESSAIS_O6A} essai par session (régénération : story O6b), "
                f"essais_max {self.essais_max} consigné"
            )
        if self.juge is None:
            consigner(f"vérification sans juge : {len(a_verifier)} session(s), aucun appel")
            return
        pire = self.estimer_pire_cas(a_verifier)
        resume = f"juge de données : {len(a_verifier)} session(s), pire cas {pire:.2f} €"
        if self.plafond_estime_openrouter is not None and pire > self.plafond_estime_openrouter:
            raise PlafondEstimeDepasse(
                f"{resume}, au-dessus du plafond de {self.plafond_estime_openrouter:.2f} € ; "
                "aucun run créé, aucun appel fait"
            )
        consigner(f"Estimation : {resume} (cache non compté).")

    # --- Pendant le run ----------------------------------------------------------------------

    def ouvrir(self, run: Run, journal: JournalMistral, racine: Path) -> None:
        """Lecteur du run (plan écrit) et interruptions déjà consignées (reprise)."""
        self._run = run
        self._lecteur = LecteurGeneration(run, journal, racine)
        self._interruptions = Counter(
            str(ligne["session_id"])
            for ligne in run.lire_jsonl(NOM_INTERRUPTIONS)
            if isinstance(ligne, dict) and "session_id" in ligne
        )

    def _ouvert(self) -> tuple[Run, LecteurGeneration]:
        if self._run is None or self._lecteur is None:
            raise SlmspError("Verificateur.ouvrir doit précéder verifier")
        return self._run, self._lecteur

    def _rafraichir(self, lecteur: LecteurGeneration, brut: SessionBrute) -> None:
        """Ajoute au lecteur les amorces dérivées écrites depuis son ouverture."""
        if all(a in lecteur.amorces for a in brut.amorces_derivees):
            return
        for ligne in lecteur.run.lire_jsonl(NOM_AMORCES_DERIVEES):
            try:
                derivee = Amorce.model_validate(ligne)
            except ValidationError:
                raise ProvenanceInvalide("amorce dérivée non conforme") from None
            lecteur.amorces.setdefault(derivee.amorce_id, derivee)

    def verifier(self, brut: SessionBrute) -> SessionBrute | AbandonSession | None:
        """Session retenue (`brut` inchangé), écartée (`AbandonSession`), ou `None` si le juge
        n'a pas conclu (session rejouable à la reprise). Lève `BudgetEpuise`,
        `ErreurApiFournisseur` (session non écrite, rejouée à la reprise). Séquentiel ; la
        génération passe par `soumettre` et `resultats` (jugements en parallèle)."""
        preparation = self._preparer(brut)
        verdict = None
        if preparation.a_juger:
            assert self.juge is not None
            verdict = self.juge.juger_candidat(brut.tache, preparation.source, preparation.cible)
        return self._conclure(preparation, verdict)

    def soumettre(self, brut: SessionBrute, etiquette: Any) -> None:
        """Contrôles déterministes tout de suite ; jugement mis en file (`appels_paralleles`
        threads). Le résultat sort de `resultats`, dans l'ordre de soumission."""
        preparation = self._preparer(brut)
        appel: Callable[[], VerdictDonnees] | None = None
        if preparation.a_juger:
            juge = self.juge
            assert juge is not None

            def appel() -> VerdictDonnees:
                return juge.juger_candidat(brut.tache, preparation.source, preparation.cible)

        self._file_jugements().soumettre((preparation, etiquette), appel)

    def transmettre(self, resultat: Any, etiquette: Any) -> None:
        """Résultat non vérifié (autre Tâche, abandon) mis en file pour garder l'ordre."""
        self._file_jugements().soumettre((resultat, etiquette), None)

    def resultats(
        self, *, attendre: bool = False
    ) -> Iterator[tuple[Any, SessionBrute | AbandonSession | None, Exception | None]]:
        """`(etiquette, résultat de verifier ou transmis, erreur)` dans l'ordre de soumission.
        `erreur` (`BudgetEpuise`, `ErreurApiFournisseur`, `JugementAnnule`…) : session non
        écrite, rejouée à la reprise."""
        for (objet, etiquette), verdict, erreur in self._file_jugements().resultats(
            attendre=attendre
        ):
            if erreur is not None:
                yield etiquette, None, erreur
            elif isinstance(objet, _Preparation):
                yield etiquette, self._conclure(objet, verdict), None
            else:
                yield etiquette, objet, None

    def arreter(self) -> None:
        """Plus aucun jugement lancé (erreur, interruption) ; ceux en cours vont à leur terme."""
        if self._file is not None:
            self._file.arreter()

    def fermer(self, *, attendre: bool = True) -> None:
        if self._file is not None:
            self._file.fermer(attendre=attendre)
            self._file = None

    def _file_jugements(self) -> FileOrdonnee:
        if self._file is None:
            paralleles = 1 if self.juge is None else self.juge.config.appels_paralleles
            self._file = FileOrdonnee(paralleles)
        return self._file

    def _preparer(self, brut: SessionBrute) -> _Preparation:
        """Contrôles déterministes (fil appelant) ; `a_juger` si le juge doit conclure."""
        _run, lecteur = self._ouvert()
        essai: dict[str, Any] = {
            "essai": 1,
            "appel_ids": list(brut.appel_ids),
            "candidat_id": f"mistral:{brut.appel_ids[-1]}",
            "motifs": [],
            "refus_par": None,
            "cle_verdict": None,
            "verdict": None,
        }
        cible = source = ""
        try:
            self._rafraichir(lecteur, brut)
            cible = lecteur.reponse_finale(brut)
            source = source_session(lecteur, brut)
            fournis = lecteur.textes_amorces(brut)
        except (SlmspError, KeyError) as exc:
            motifs = [Motif("cible_illisible", "provenance", True, type(exc).__name__)]
        else:
            if brut.tache == "CR":
                fournis = [*fournis, source]
            motifs = verifier_cible(
                brut.tache,
                cible,
                source=source,
                fournis=fournis,
                config=self.config,
                plafonds_mots=self.plafonds_mots,
            )
        if refusee(motifs):
            essai["refus_par"] = "tests"
        a_juger = essai["refus_par"] is None and self.juge is not None
        return _Preparation(brut, essai, motifs, source, cible, a_juger)

    def _conclure(
        self, preparation: _Preparation, verdict: VerdictDonnees | None
    ) -> SessionBrute | AbandonSession | None:
        """Écrit les fichiers de vérification (fil appelant seulement) et rend l'issue."""
        run, _lecteur = self._ouvert()
        brut, essai, motifs = preparation.brut, preparation.essai, preparation.motifs
        candidat_id = essai["candidat_id"]
        if verdict is not None and self.juge is not None:
            seuils = self.juge.config.seuils[brut.tache]
            if verdict.verdict in ("non-juge", "invalide"):
                run.ajouter_jsonl(
                    NOM_INTERRUPTIONS,
                    {
                        "session_id": brut.session_id,
                        "candidat_id": candidat_id,
                        "cle": verdict.cle,
                        "verdict": verdict.verdict,
                        "motif": verdict.motif,
                        "cout_eur": verdict.cout_eur,
                        "appel_ids": list(verdict.appel_ids),
                    },
                )
                self._interruptions[brut.session_id] += 1
                if self._interruptions[brut.session_id] < INTERRUPTIONS_MAX:
                    return None
                essai["refus_par"] = "juge-non-conclusif"
            else:
                run.ajouter_jsonl(
                    NOM_VERDICTS,
                    {
                        "session_id": brut.session_id,
                        "candidat_id": candidat_id,
                        **verdict.ligne(),
                        "seuils": seuils,
                    },
                )
                essai["cle_verdict"], essai["verdict"] = verdict.cle, verdict.verdict
                if verdict.verdict == "refuse":
                    essai["refus_par"] = "juge"
                    motifs = [*motifs, *_motifs_juge(verdict, seuils)]
        essai["motifs"] = [m.ligne() for m in motifs]
        issue = "retenue" if essai["refus_par"] is None else "ecartee"
        run.ajouter_jsonl(
            NOM_VERIFICATION,
            {
                "schema_version": 1,
                "session_id": brut.session_id,
                "tache": brut.tache,
                "essais": [essai],
                "issue": issue,
            },
        )
        if issue == "retenue":
            return brut
        codes = sorted({m.code for m in motifs if m.bloquant}) or [str(essai["refus_par"])]
        run.ajouter_jsonl(
            NOM_ECARTEES,
            {
                "session_id": brut.session_id,
                "tache": brut.tache,
                "essais": 1,
                "refus_par": essai["refus_par"],
                "codes": codes,
            },
        )
        return AbandonSession(
            session_id=brut.session_id,
            tache=brut.tache,
            motif=MOTIF_ABANDON,
            detail=f"refus ({essai['refus_par']}) : {', '.join(codes)}",
            appel_ids=brut.appel_ids,
            cassettes=brut.cassettes,
        )

    # --- Fin du run --------------------------------------------------------------------------

    def clore(self, statut: str, cout_mistral_invocation: float) -> dict[str, Any] | None:
        """À la fin d'un run `complet` : `rapport.json`, `echantillon.md`, `calibrage.md`."""
        run, lecteur = self._ouvert()
        if statut != "complet":
            return None
        cout_mistral = cout_mistral_invocation + sum(
            float(ligne.get("cout_eur") or 0.0)
            for ligne in run.lire_jsonl(NOM_BILAN)
            if isinstance(ligne, dict)
        )
        cout_openrouter = sum(
            float(ligne.get("cout_eur") or 0.0)
            for nom in (NOM_VERDICTS, NOM_INTERRUPTIONS)
            for ligne in run.lire_jsonl(nom)
            if isinstance(ligne, dict)
        )
        lignes = [ligne for ligne in run.lire_jsonl(NOM_VERIFICATION) if isinstance(ligne, dict)]
        rapport = rapport_verification(lignes)
        rapport.update(
            {
                "sans_juge": self.juge is None,
                "essais_max": self.essais_max,
                "non_bloquants": list(self.config.non_bloquants),
                "cout_mistral_eur": round(cout_mistral, 6),
                "cout_openrouter_eur": round(cout_openrouter, 6),
            }
        )
        run.ecrire(NOM_RAPPORT, json_canonique(rapport) + b"\n")
        run.ecrire(NOM_ECHANTILLON, self._echantillon(lecteur, lignes))
        run.ecrire(NOM_CALIBRAGE, self._calibrage(lecteur, lignes, rapport))
        return rapport

    def _cible(self, lecteur: LecteurGeneration, ligne: Mapping[str, Any]) -> str:
        try:
            contenu = lecteur.message(ligne["essais"][-1]["appel_ids"][-1]).get("content")
        except (SlmspError, KeyError, IndexError):
            return "(cible illisible)"
        return contenu if isinstance(contenu, str) else "(cible illisible)"

    def _bloc(self, lecteur: LecteurGeneration, ligne: Mapping[str, Any]) -> str:
        essai = ligne["essais"][-1]
        motifs = "\n".join(
            f"- `{m['code']}` ({'bloquant' if m['bloquant'] else 'non bloquant'}, "
            f"{m['critere']}) : {m['message']}"
            + (
                f" ; extraits : {json.dumps(m['extraits'], ensure_ascii=False)}"
                if m["extraits"]
                else ""
            )
            for m in essai["motifs"]
        )
        return (
            f"### {ligne['tache']} · {ligne['session_id']} · {ligne['issue']}"
            f"{' (' + str(essai['refus_par']) + ')' if essai['refus_par'] else ''}\n\n"
            f"{motifs or '- aucun motif'}\n\n~~~~text\n{self._cible(lecteur, ligne)}\n~~~~\n"
        )

    def _echantillon(self, lecteur: LecteurGeneration, lignes: Sequence[Mapping[str, Any]]) -> str:
        n = self.config.echantillon
        alea = random.Random(self.config.graine)
        parties = [
            "# Échantillon de la génération vérifiée\n\n"
            f"Graine {self.config.graine} : {n} cible(s) retenue(s) par Tâche, puis {n} "
            "cible(s) écartée(s), avec leurs motifs. Cibles rédigées par Mistral (journal).\n"
        ]
        for tache in self.taches:
            retenues = [x for x in lignes if x["tache"] == tache and x["issue"] == "retenue"]
            parties.append(f"\n## {tache} : retenues ({len(retenues)})\n")
            parties += [
                self._bloc(lecteur, x) for x in alea.sample(retenues, min(n, len(retenues)))
            ]
        ecartees = [x for x in lignes if x["issue"] == "ecartee"]
        parties.append(f"\n## Écartées ({len(ecartees)})\n")
        tirees = alea.sample(ecartees, min(n, len(ecartees)))
        parties += [self._bloc(lecteur, x) for x in tirees]
        return "\n".join(parties)

    def _calibrage(
        self,
        lecteur: LecteurGeneration,
        lignes: Sequence[Mapping[str, Any]],
        rapport: Mapping[str, Any],
    ) -> str:
        n = self.config.calibrage
        refus = [x for x in lignes if x["essais"][-1]["refus_par"] == "tests"]
        tires = random.Random(self.config.graine).sample(refus, min(n, len(refus)))
        tableau = [
            "| Tâche | Vérifiées | Refus (tests) | Code | Sessions | Taux |",
            "|---|---|---|---|---|---|",
        ]
        for tache, bloc in rapport["taches"].items():
            for code, compte in bloc["codes_bloquants"].items():
                tableau.append(
                    f"| {tache} | {bloc['verifiees']} | {bloc['refus_tests']} | `{code}` | "
                    f"{compte} | {compte / bloc['verifiees']:.0%} |"
                )
        return (
            "# Calibrage des contrôles déterministes\n\n"
            f"Taux de refus par code (sessions qui portent le code bloquant), puis {len(tires)} "
            f"refus tirés (graine {self.config.graine}) parmi {len(refus)}. Pour chaque refus "
            "relu : vrai ou faux positif. Un code dont plus de 20 % des refus relus sont des faux "
            "positifs passe dans `[verification] non_bloquants` avant le run payant.\n\n"
            + "\n".join(tableau)
            + "\n\n## Refus tirés\n\n"
            + "\n".join(self._bloc(lecteur, x) for x in tires)
        )


_ACCEPTEES: Final = (
    "acceptees_emblee",
    "acceptees_apres_1_regeneration",
    "acceptees_apres_2_regenerations",
)
_REFUS: Final = {"tests": "refus_tests", "juge": "refus_juge"}


def rapport_verification(lignes: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Par Tâche : sessions vérifiées, acceptées d'emblée, après 1 ou 2 régénérations, écartées ;
    refus par tests ou par juge ; sessions par code bloquant et par code non bloquant."""
    taches: dict[str, dict[str, Any]] = {}
    for ligne in lignes:
        tache = str(ligne["tache"])
        bloc = taches.setdefault(
            tache,
            {
                "verifiees": 0,
                "acceptees_emblee": 0,
                "acceptees_apres_1_regeneration": 0,
                "acceptees_apres_2_regenerations": 0,
                "ecartees": 0,
                "refus_tests": 0,
                "refus_juge": 0,
                "refus_juge_non_conclusif": 0,
                "codes_bloquants": Counter(),
                "codes_non_bloquants": Counter(),
            },
        )
        bloc["verifiees"] += 1
        essais = ligne["essais"]
        if ligne["issue"] == "retenue":
            bloc[_ACCEPTEES[min(len(essais), 3) - 1]] += 1
        else:
            bloc["ecartees"] += 1
        refus_par = essais[0]["refus_par"]
        if refus_par is not None:
            bloc[_REFUS.get(refus_par, "refus_juge_non_conclusif")] += 1
        for nature, bloquant in (("codes_bloquants", True), ("codes_non_bloquants", False)):
            bloc[nature].update(
                {m["code"] for m in essais[0]["motifs"] if m["bloquant"] is bloquant}
            )
    for bloc in taches.values():
        bloc["taux_ecart"] = round(bloc["ecartees"] / bloc["verifiees"], 6)
        for nature in ("codes_bloquants", "codes_non_bloquants"):
            bloc[nature] = dict(bloc[nature].most_common())
    return {"schema_version": 1, "taches": dict(sorted(taches.items()))}
