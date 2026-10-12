"""Modes de l'Assistant : `ModeSonde` (sonde du serveur MCP) et `ModeFixe` (FR-10, NFR-9).

`ModeSonde` implémente `ModePort` par la sonde `GET /health` de `slmsp.mcp.direct`
(`sonder_sante`), qui passe par la passerelle `net`, profil `assistant`, avec un Mode de
garde `ModeFixe("hors-ligne-detecte")` : seule la sonde peut sortir. Règles :

- le Mode est `connecte` seulement si la sonde répond 2xx en `delai_sonde_s` au plus
  (durée mesurée par l'horloge injectée) ; une exception, un statut non 2xx ou une
  réponse trop lente donnent `hors-ligne-detecte` (un doute laisse hors ligne) ;
- la sonde a lieu à la première lecture (démarrage), dès que `periode_sonde_s` est
  écoulée depuis la dernière, et à chaque appel de `sonder()` (avant chaque appel
  d'outil) ;
- en hors ligne forcé (`hors_ligne_force=True` ou `forcer(True)`), le Mode vaut
  `hors-ligne-force` et aucune requête n'est émise, sonde comprise ;
- au passage en `connecte`, `controle_schema()` (facultatif, par exemple
  `comparer_schema_serveur` sur le `tools/list` du serveur) est appelé :
  `SchemaOutilModifie` renseigne `ecarts_schema` et laisse une entrée de journal (logger
  `slmsp.harness`, WARNING) ; toute autre exception est un doute et le Mode reste hors
  ligne. Un outil inconnu du serveur est ignoré (règle de `comparer_schema_serveur`).

`ModeFixe(mode)` renvoie toujours `mode`, sans requête : il sert au banc et aux tests.
`mode_avant_appel` et `ecarts_schema` lisent n'importe quel `ModePort` (avec ou sans
`sonder`, avec ou sans `ecarts_schema`) pour la boucle d'outils de la Recherche de données.
"""

from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Final, get_args

from slmsp.core.erreurs import SchemaOutilModifie
from slmsp.core.ports import Mode, ModePort

if TYPE_CHECKING:
    from slmsp.core.ports import JournalRequetes
    from slmsp.harness.config import ConfigModes
    from slmsp.net.config import ConfigListeBlanche, ConfigReseau

LOGGER: Final = logging.getLogger("slmsp.harness")

MODES: Final[tuple[str, ...]] = get_args(Mode)
"""Valeurs de `Mode` : `connecte`, `hors-ligne-detecte`, `hors-ligne-force`."""

CONNECTE: Final = "connecte"
HORS_LIGNE_DETECTE: Final = "hors-ligne-detecte"
HORS_LIGNE_FORCE: Final = "hors-ligne-force"
PROFIL_SONDE: Final = "assistant"


class ModeFixe:
    """`ModePort` qui renvoie toujours le même Mode, sans aucune requête."""

    def __init__(self, mode: str) -> None:
        if mode not in MODES:
            raise ValueError(f"Mode inconnu : {mode!r} (attendu : {', '.join(MODES)})")
        self._mode: Mode = mode  # type: ignore[assignment]

    def mode_courant(self) -> Mode:
        return self._mode

    def sonder(self) -> Mode:
        return self._mode

    def __repr__(self) -> str:
        return f"ModeFixe({self._mode!r})"


class ModeSonde:
    """`ModePort` fondé sur la sonde `GET /health` du serveur MCP (voir le module).

    `config` : section `modes` de `ConfigHarnais` (`periode_sonde_s`, `delai_sonde_s`).
    `journal`, `transport_interne`, `config_reseau` et `liste_blanche` sont transmis à la
    passerelle (`sonder_sante`). `horloge` (secondes, monotone) mesure la période et la
    durée de la sonde. Les lectures sont protégées par un verrou : une seule sonde à la fois.
    """

    def __init__(
        self,
        config: ConfigModes,
        *,
        hors_ligne_force: bool = False,
        controle_schema: Callable[[], Any] | None = None,
        journal: JournalRequetes | None = None,
        transport_interne: Any = None,
        config_reseau: ConfigReseau | None = None,
        liste_blanche: ConfigListeBlanche | None = None,
        horloge: Callable[[], float] = time.monotonic,
    ) -> None:
        self.config = config
        self.controle_schema = controle_schema
        self.journal = journal
        self.transport_interne = transport_interne
        self.config_reseau = config_reseau
        self.liste_blanche = liste_blanche
        self.horloge = horloge
        self._verrou = threading.RLock()
        self._force = bool(hors_ligne_force)
        self._mode: Mode = HORS_LIGNE_FORCE if self._force else HORS_LIGNE_DETECTE
        self._derniere: float | None = None
        self._ecarts: tuple[str, ...] = ()

    # --- ModePort -------------------------------------------------------------------------

    def mode_courant(self) -> Mode:
        """Mode courant ; sonde d'abord si c'est la première lecture ou si la période est échue."""
        with self._verrou:
            if self._force:
                return HORS_LIGNE_FORCE
            if self._derniere is None or (
                self.horloge() - self._derniere >= self.config.periode_sonde_s
            ):
                return self.sonder()
            return self._mode

    def sonder(self) -> Mode:
        """Sonde maintenant (sauf hors ligne forcé) et renvoie le Mode qui en résulte."""
        with self._verrou:
            if self._force:
                return HORS_LIGNE_FORCE
            precedent = self._mode
            joignable = self._sonde()
            self._derniere = self.horloge()
            if not joignable:
                self._mode = HORS_LIGNE_DETECTE
            elif precedent == CONNECTE or self._controler():
                self._mode = CONNECTE
            else:
                self._mode = HORS_LIGNE_DETECTE
            return self._mode

    def forcer(self, hors_ligne: bool) -> Mode:
        """Active ou lève le hors ligne forcé ; le lever relance une sonde à la lecture suivante."""
        with self._verrou:
            self._force = bool(hors_ligne)
            self._derniere = None
            self._mode = HORS_LIGNE_FORCE if self._force else HORS_LIGNE_DETECTE
            return self._mode

    @property
    def hors_ligne_force(self) -> bool:
        return self._force

    @property
    def ecarts_schema(self) -> tuple[str, ...]:
        """Écarts du dernier contrôle de schéma (vide : schéma conforme ou non contrôlé)."""
        with self._verrou:
            return self._ecarts

    # --- Interne --------------------------------------------------------------------------

    def _config_reseau(self) -> ConfigReseau:
        from slmsp.net.config import charger_config_reseau

        base = self.config_reseau if self.config_reseau is not None else charger_config_reseau()
        delais = base.delais.model_copy(update={"sonde": self.config.delai_sonde_s})
        return base.model_copy(update={"delais": delais})

    def _sonde(self) -> bool:
        """Vrai seulement si la sonde répond 2xx dans le délai ; tout doute donne faux."""
        from slmsp.mcp.direct import sonder_sante

        debut = self.horloge()
        try:
            resultat = sonder_sante(
                PROFIL_SONDE,
                mode=ModeFixe(HORS_LIGNE_DETECTE),
                journal=self.journal,
                transport_interne=self.transport_interne,
                config=self._config_reseau(),
                liste_blanche=self.liste_blanche,
            )
        except Exception as exc:
            LOGGER.info("sonde du Mode en échec : %s : %s", type(exc).__name__, exc)
            return False
        duree = self.horloge() - debut
        if not resultat.joignable:
            LOGGER.info("sonde du Mode : serveur non joignable (%s)", resultat.detail)
            return False
        if duree > self.config.delai_sonde_s:
            LOGGER.info(
                "sonde du Mode : réponse trop lente (%.3f s > %.3f s)",
                duree,
                self.config.delai_sonde_s,
            )
            return False
        return True

    def _controler(self) -> bool:
        """Contrôle du schéma au passage en `connecte` ; faux si le contrôle laisse un doute."""
        if self.controle_schema is None:
            self._ecarts = ()
            return True
        try:
            self.controle_schema()
        except SchemaOutilModifie as exc:
            ecarts = getattr(exc, "ecarts", None) or (str(exc),)
            self._ecarts = tuple(str(e) for e in ecarts)
            LOGGER.warning("schéma des outils MCP modifié : %s", " ; ".join(self._ecarts))
            return True
        except Exception as exc:
            LOGGER.info("contrôle du schéma MCP en échec : %s : %s", type(exc).__name__, exc)
            return False
        self._ecarts = ()
        return True


def mode_courant(port: ModePort | None) -> Mode:
    """Mode lu par `mode_courant()` ; `None`, une exception ou une valeur inconnue : hors ligne."""
    if port is None:
        return HORS_LIGNE_DETECTE
    try:
        mode = port.mode_courant()
    except Exception as exc:
        LOGGER.info("lecture du Mode en échec : %s : %s", type(exc).__name__, exc)
        return HORS_LIGNE_DETECTE
    return mode if mode in MODES else HORS_LIGNE_DETECTE


def mode_avant_appel(port: ModePort | None) -> Mode:
    """Mode re-sondé avant un appel d'outil : `sonder()` si le port l'offre, sinon `mode_courant()`.

    `None`, une exception ou une valeur inconnue donnent `hors-ligne-detecte`.
    """
    sonder = getattr(port, "sonder", None)
    if port is None or not callable(sonder):
        return mode_courant(port)
    try:
        mode = sonder()
    except Exception as exc:
        LOGGER.info("sonde du Mode en échec : %s : %s", type(exc).__name__, exc)
        return HORS_LIGNE_DETECTE
    return mode if mode in MODES else HORS_LIGNE_DETECTE


def ecarts_schema(port: ModePort | None) -> tuple[str, ...]:
    """Écarts de schéma connus du port (`ecarts_schema`), vide s'il n'en porte pas."""
    ecarts = getattr(port, "ecarts_schema", None) if port is not None else None
    if not ecarts:
        return ()
    if isinstance(ecarts, str):
        return (ecarts,)
    return tuple(str(ecart) for ecart in ecarts)


__all__ = [
    "CONNECTE",
    "HORS_LIGNE_DETECTE",
    "HORS_LIGNE_FORCE",
    "MODES",
    "ModeFixe",
    "ModeSonde",
    "ecarts_schema",
    "mode_avant_appel",
    "mode_courant",
]
