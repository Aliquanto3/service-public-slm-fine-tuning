"""Adaptateur de rejeu de `ToolPort` : le Bac à sable MCP (AD-10, FR-25, NFR-8).

`BacASable` charge les cassettes d'un item et répond à chaque appel sans réseau, de façon
déterministe. Il refuse au chargement une cassette dont `tools_list_sha256` diffère de
`config/outils-mcp.toml` (`SchemaOutilModifie`). Seules les interactions `tools/call`
servent ; leur rang suit l'ordre des cassettes passées, puis celui des interactions.

Appariement d'un appel validé (`valider_appel`, comme `McpEnDirect.appeler`) :

1. même outil et arguments égaux en JSON canonique : la réponse enregistrée ;
2. sinon, même outil avec le plus de paires (clé, valeur) égales (zéro permis), le premier
   rang départageant les égalités ;
3. sinon, la réponse vide normalisée (`texte_reponse_vide` de la config).

Les cas 2 et 3 signalent un `Avertissement` de code `appel-non-prevu`, sans effet sur la
réponse. Une interaction appariée qui porte `simulation` lève l'exception de transport du
client direct (`PAR_TYPE_SIMULATION`). L'`id` JSON-RPC de la réponse est `id_requete`.
L'adaptateur est sans état : rien ne change après `__init__`, chaque réponse est une copie.
"""

from __future__ import annotations

import copy
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final

from slmsp.core.canonique import json_canonique
from slmsp.core.erreurs import SchemaOutilModifie
from slmsp.core.evenements import Avertissement, Evenement
from slmsp.core.schemas.cassette import Cassette, Simulation
from slmsp.mcp.cassettes import lire_cassette
from slmsp.mcp.enregistrement import PREMIER_ID_APPEL
from slmsp.mcp.erreurs import PAR_TYPE_SIMULATION, CassetteInvalide, ErreurHttp
from slmsp.mcp.outils import charger_config, charger_outils, valider_appel

__all__ = ["CODE_APPEL_NON_PREVU", "BacASable", "reponse_vide"]

CODE_APPEL_NON_PREVU: Final = "appel-non-prevu"
"""Code de l'`Avertissement` émis quand un appel n'a pas d'équivalent exact enregistré."""


def reponse_vide(id_requete: Any, texte: str) -> dict[str, Any]:
    """Réponse vide normalisée (AD-10), à la forme JSON-RPC des réponses enregistrées."""
    return {
        "jsonrpc": "2.0",
        "id": id_requete,
        "result": {"content": [{"type": "text", "text": texte}], "isError": False},
    }


@dataclass(frozen=True)
class _Enregistre:
    """Une interaction `tools/call` enregistrée, prête à l'appariement."""

    rang: int
    origine: str
    nom: str
    canonique: bytes
    paires: frozenset[tuple[str, bytes]]
    reponse: Mapping[str, Any] | None
    simulation: Simulation | None


def _paires(arguments: Mapping[str, Any]) -> frozenset[tuple[str, bytes]]:
    return frozenset((cle, json_canonique(valeur)) for cle, valeur in arguments.items())


def _source(cassette: Cassette | str | Path, rang: int) -> tuple[Cassette, str]:
    """Cassette lue (ou copiée) et libellé citant son fichier, ou son rang."""
    if isinstance(cassette, Cassette):
        return cassette.model_copy(deep=True), f"cassette de rang {rang}"
    if isinstance(cassette, (str, Path)):
        return lire_cassette(cassette), str(cassette)
    raise TypeError(f"cassette attendue : Cassette ou chemin (reçu {type(cassette).__name__})")


class BacASable:
    """Bac à sable MCP (adaptateur de rejeu de `ToolPort`), sans réseau et sans état.

    `cassettes` : modèles `Cassette` ou chemins de fichiers (cassettes héritées du calibrage
    comprises). `chemin_outils` remplace `config/outils-mcp.toml`. `signaler` reçoit les
    évènements « appel non prévu ».

    Lève `ConfigurationInvalide` (config), `CassetteInvalide` (cassette illisible ou
    interaction `tools/call` malformée) ou `SchemaOutilModifie` (attribut `ecarts`, tuple
    citant chaque cassette refusée par son chemin ou son rang).
    """

    def __init__(
        self,
        cassettes: Sequence[Cassette | str | Path],
        *,
        chemin_outils: str | Path | None = None,
        signaler: Callable[[Evenement], None] | None = None,
    ) -> None:
        if isinstance(cassettes, (str, Path, Cassette)):
            raise TypeError("`cassettes` est une séquence de cassettes ou de chemins")
        config = charger_config(chemin_outils)
        self.chemin_outils = chemin_outils
        self.signaler = signaler
        self._texte_reponse_vide: str = config.texte_reponse_vide
        enregistres: list[_Enregistre] = []
        ecarts: list[str] = []
        for rang_cassette, source in enumerate(cassettes):
            cassette, libelle = _source(source, rang_cassette)
            if cassette.tools_list_sha256 != config.tools_list_sha256:
                ecarts.append(f"{libelle} : `tools_list_sha256` différent de la config")
                continue
            for rang_interaction, interaction in enumerate(cassette.interactions):
                requete = interaction.request
                if requete.get("method") != "tools/call":
                    continue
                params = requete.get("params")
                nom = params.get("name") if isinstance(params, Mapping) else None
                # `arguments` est facultatif en MCP : son absence vaut un objet vide.
                arguments = params.get("arguments", {}) if isinstance(params, Mapping) else None
                if not isinstance(nom, str) or not isinstance(arguments, Mapping):
                    raise CassetteInvalide(
                        f"{libelle} : interaction {rang_interaction} : `tools/call` malformé "
                        "(`params.name` chaîne et `params.arguments` objet attendus)"
                    )
                try:
                    canonique = json_canonique(dict(arguments))
                    paires = _paires(arguments)
                except (TypeError, ValueError):
                    raise CassetteInvalide(
                        f"{libelle} : interaction {rang_interaction} : arguments non sérialisables"
                    ) from None
                reponse = interaction.response
                enregistres.append(
                    _Enregistre(
                        rang=len(enregistres),
                        origine=f"{libelle}, interaction {rang_interaction}",
                        nom=nom,
                        canonique=canonique,
                        paires=paires,
                        reponse=None
                        if reponse is None
                        else MappingProxyType(copy.deepcopy(reponse)),
                        simulation=interaction.simulation,
                    )
                )
        if ecarts:
            erreur = SchemaOutilModifie(
                "cassette refusée, empreinte des outils différente : " + " ; ".join(ecarts)
            )
            erreur.ecarts = tuple(ecarts)  # type: ignore[attr-defined]
            raise erreur
        par_outil: dict[str, list[_Enregistre]] = {}
        for enregistre in enregistres:
            par_outil.setdefault(enregistre.nom, []).append(enregistre)
        self._par_outil: Mapping[str, tuple[_Enregistre, ...]] = MappingProxyType(
            {nom: tuple(liste) for nom, liste in par_outil.items()}
        )

    # --- ToolPort -------------------------------------------------------------------------

    def lister_outils(self) -> list[dict[str, Any]]:
        """Outils figés au format `tools` d'OpenAI."""
        return charger_outils(self.chemin_outils)

    def appeler(
        self, nom: str, arguments: Mapping[str, Any], *, id_requete: Any = PREMIER_ID_APPEL
    ) -> dict[str, Any]:
        """Rejoue l'appel `nom(arguments)` et renvoie la réponse JSON-RPC (copie).

        Lève `AppelNonConforme` si l'appel viole le schéma figé (rien n'est rejoué), et
        `DelaiDepasse`, `ErreurHttp` ou `Injoignable` si l'interaction appariée simule une
        panne.
        """
        valider_appel(nom, arguments, chemin=self.chemin_outils)
        candidats = self._par_outil.get(nom, ())
        canonique = json_canonique(dict(arguments))
        choisi = next((e for e in candidats if e.canonique == canonique), None)
        if choisi is None:
            paires = _paires(arguments)
            meilleur = -1
            for enregistre in candidats:
                score = len(paires & enregistre.paires)
                if score > meilleur:
                    choisi, meilleur = enregistre, score
            if choisi is None:
                self._signaler(
                    f"appel « {nom} » non prévu par les cassettes : réponse vide normalisée"
                )
                return reponse_vide(id_requete, self._texte_reponse_vide)
            self._signaler(
                f"appel « {nom} » non prévu par les cassettes : interaction la plus proche "
                f"rejouée ({choisi.origine}, {meilleur} paire(s) égale(s))"
            )
        if choisi.simulation is not None:
            raise _panne(choisi.simulation, nom)
        assert choisi.reponse is not None  # garanti par `Interaction`
        reponse = copy.deepcopy(dict(choisi.reponse))
        reponse["id"] = id_requete
        return reponse

    def _signaler(self, message: str) -> None:
        if self.signaler is not None:
            self.signaler(Avertissement(code=CODE_APPEL_NON_PREVU, message=message))


def _panne(simulation: Simulation, nom: str) -> Exception:
    classe = PAR_TYPE_SIMULATION[simulation.type]
    message = f"rejeu : panne simulée « {simulation.type} » pour l'appel « {nom} »"
    if classe is ErreurHttp:
        return ErreurHttp(message, statut=simulation.statut)
    return classe(message)
