"""`LlmPort` composite du mode hybride (story 17.4) : fournisseurs externes en cascade, modèle
local en secours.

Un échange (une réponse de l'Assistant, boucle d'outils et vérification comprises) est
représenté par un `EchangeHybride`, obtenu par `ClientHybride.echange()`. Règles :

- la décision se prend au **premier appel** de l'échange : les fournisseurs externes sont
  essayés dans l'ordre (amendement 14) ; un échec avant le premier évènement (connexion,
  délai, HTTP, clé absente, `HoteBloque`) fait passer au suivant ; tous en échec, ou Mode hors
  ligne (forcé ou détecté) : tout l'échange part vers le modèle local. `echecs` garde
  `(preset, code court)` de chaque échec, `motif_secours` leur résumé et `bandeau` le message
  affiché ;
- le fournisseur retenu sert tous les appels de l'échange ; un échec ultérieur lève
  `EchecAppel` : le Harnais termine l'échange en erreur (`modele-externe-interrompu`) ;
- `taille_contexte` et `compter_tokens` sont ceux du modèle local (passages bornés comme
  aujourd'hui) ;
- `modele_repondant` vaut `local:<slug>` ou `externe:<preset>/<modèle>`.

Le motif et la durée d'un échec partent au logger `slmsp.inference.hybride`, sans contenu.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator, Mapping, Sequence
from typing import Any, Final

from slmsp.core.ports import ModePort
from slmsp.inference.client_openai import ClientOpenAI, EchecAppel, Evenement

LOGGER: Final = logging.getLogger("slmsp.inference.hybride")
MODES_HORS_LIGNE: Final = frozenset({"hors-ligne-force", "hors-ligne-detecte"})


def identifiant_local(slug: str) -> str:
    return f"local:{slug}"


def _nom(client: Any) -> str:
    preset = getattr(client, "preset", None)
    return str(getattr(preset, "nom", None) or getattr(client, "hote", None) or "externe")


class EchangeHybride:
    """`LlmPort` d'un échange (voir le module)."""

    def __init__(self, hybride: ClientHybride, *, forcer_local: bool = False) -> None:
        self._hybride = hybride
        self.choix: str | None = "local" if forcer_local else None
        self.retenu: ClientOpenAI | None = None
        self.echecs: list[tuple[str, str]] = []
        self.modele_repondant: str | None = None
        self.externe_utilise = False

    @property
    def motif_secours(self) -> str | None:
        """Code court de l'échec (un seul fournisseur), sinon `preset : code ; …`."""
        if not self.echecs:
            return None
        if len(self._hybride.externes) <= 1 or self.echecs[0][0] == "":
            return self.echecs[0][1]
        return " ; ".join(f"{nom} : {code}" for nom, code in self.echecs)

    @property
    def bandeau(self) -> str | None:
        """Message du secours : qui a répondu, et pourquoi les précédents ont échoué."""
        motif = self.motif_secours
        if motif is None:
            return None
        if self.choix == "externe" and self.retenu is not None:
            return f"Réponse de {_nom(self.retenu)} en secours ({motif})"
        return f"Modèle externe indisponible ({motif}) : réponse du modèle local"

    @property
    def taille_contexte(self) -> int | None:
        return self._hybride.taille_contexte

    def compter_tokens(
        self,
        messages: Sequence[Mapping[str, Any]],
        tools: Sequence[Mapping[str, Any]] | None = None,
    ) -> int:
        return self._hybride.compter_tokens(messages, tools)

    def _local(
        self,
        messages: Sequence[Mapping[str, Any]],
        tools: Sequence[Mapping[str, Any]] | None,
        options: Mapping[str, Any] | None,
    ) -> Iterator[Evenement]:
        self.choix = "local"
        self.modele_repondant = self._hybride.identifiant_local
        return self._hybride.local.generer(messages, tools=tools, options=options)

    def _echec(self, nom: str, code: str, duree_ms: int | None) -> None:
        self.echecs.append((nom, code))
        LOGGER.warning(
            "fournisseur externe %s indisponible (%s, %s ms)",
            nom or "-",
            code,
            "?" if duree_ms is None else duree_ms,
        )

    def generer(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        tools: Sequence[Mapping[str, Any]] | None = None,
        options: Mapping[str, Any] | None = None,
    ) -> Iterator[Evenement]:
        if self.choix == "local" or not self._hybride.externes:
            return self._local(messages, tools, options)
        if self.choix == "externe" and self.retenu is not None:
            self.externe_utilise = True
            return self.retenu.generer(messages, tools=tools, options=options)
        if self._hybride.hors_ligne():
            self._echec("", "hors-ligne", None)
            return self._local(messages, tools, options)
        return self._cascade(messages, tools, options)

    def _cascade(
        self,
        messages: Sequence[Mapping[str, Any]],
        tools: Sequence[Mapping[str, Any]] | None,
        options: Mapping[str, Any] | None,
    ) -> Iterator[Evenement]:
        for externe in self._hybride.externes:
            nom = _nom(externe)
            try:
                flux = externe.generer(messages, tools=tools, options=options)
                premier = next(flux)
            except EchecAppel as exc:
                self._echec(nom, exc.code, getattr(externe, "derniere_duree_ms", None))
                continue
            except StopIteration:
                self._echec(nom, "reponse-invalide", getattr(externe, "derniere_duree_ms", None))
                continue
            self.choix = "externe"
            self.retenu = externe
            self.externe_utilise = True
            self.modele_repondant = externe.identifiant
            yield premier
            try:
                yield from flux
            except EchecAppel as exc:
                LOGGER.warning(
                    "fournisseur %s interrompu (%s) après le premier jeton", nom, exc.code
                )
                raise
            return
        LOGGER.warning("aucun fournisseur externe disponible : secours local")
        yield from self._local(messages, tools, options)


class ClientHybride:
    """Composite `LlmPort` : `externes` dans l'ordre d'essai, `local` en secours (voir le module).

    `externes` : un client, une séquence de clients (3 au plus côté réglages), ou `None`.
    """

    def __init__(
        self,
        local: Any,
        externes: ClientOpenAI | Sequence[ClientOpenAI] | None,
        mode: ModePort | None,
        *,
        slug_local: str,
    ) -> None:
        self.local = local
        if externes is None:
            self.externes: list[ClientOpenAI] = []
        elif isinstance(externes, Sequence):
            self.externes = list(externes)
        else:
            self.externes = [externes]
        self.mode = mode
        self.identifiant_local = identifiant_local(slug_local)

    @property
    def externe(self) -> ClientOpenAI | None:
        """Fournisseur de tête (indicateur de Mode), ou `None`."""
        return self.externes[0] if self.externes else None

    @property
    def taille_contexte(self) -> int | None:
        return getattr(self.local, "taille_contexte", None)

    def hors_ligne(self) -> bool:
        if self.mode is None:
            return False
        try:
            return self.mode.mode_courant() in MODES_HORS_LIGNE
        except Exception:
            return True

    def echange(self, *, forcer_local: bool = False) -> EchangeHybride:
        return EchangeHybride(self, forcer_local=forcer_local)

    def pour(self, modele_repondant: str | None) -> EchangeHybride:
        """Échange lié au modèle qui a répondu (vérification FR-12, amendement 6) :
        `local:…` -> modèle local ; `externe:…` d'un fournisseur actif -> ce fournisseur seul
        (son échec rend la vérification indisponible, sans autre fournisseur) ; sinon, nouvel
        échange en cascade."""
        if isinstance(modele_repondant, str) and modele_repondant.startswith("local:"):
            return self.echange(forcer_local=True)
        for externe in self.externes:
            if getattr(externe, "identifiant", None) == modele_repondant:
                echange = self.echange()
                echange.choix = "externe"
                echange.retenu = externe
                echange.modele_repondant = modele_repondant
                return echange
        LOGGER.info("vérification : modèle de la réponse inconnu, nouvel échange")
        return self.echange()

    def compter_tokens(
        self,
        messages: Sequence[Mapping[str, Any]],
        tools: Sequence[Mapping[str, Any]] | None = None,
    ) -> int:
        return self.local.compter_tokens(messages, tools)

    def generer(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        tools: Sequence[Mapping[str, Any]] | None = None,
        options: Mapping[str, Any] | None = None,
    ) -> Iterator[Evenement]:
        """Appel isolé (vérification FR-12) : un échange d'un seul appel."""
        return self.echange().generer(messages, tools=tools, options=options)

    def __getattr__(self, nom: str) -> Any:
        # Attributs propres au client local (`protocole_outils`, `fermer`…).
        if nom.startswith("__") or nom in {
            "local",
            "externes",
            "externe",
            "mode",
            "identifiant_local",
            "pour",
        }:
            raise AttributeError(nom)
        return getattr(self.local, nom)


__all__ = ["ClientHybride", "EchangeHybride", "identifiant_local"]
