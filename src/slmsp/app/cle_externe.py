"""Clés des fournisseurs externes (story 17.4), chiffrées par DPAPI pour l'utilisateur Windows
courant.

Une clé par fournisseur (amendement 14) : fichier dédié `fournisseur-<id>.cle` du dossier de
données (jamais la table `reglages`), `id` étant l'identifiant de l'entrée du réglage
`fournisseurs_externes` (`CoffreCles`). La clé
n'est jamais journalisée ni renvoyée à l'interface : celle-ci ne sait que si une clé est
enregistrée. Tout échec de déchiffrement (fichier corrompu, autre utilisateur, DPAPI absente)
vaut « clé absente ».

Liaison (revue 17.4) : la clé d'une entrée est enregistrée avec l'hôte et le preset de
l'entrée (`{cle, hote, preset}` chiffré). Une lecture qui précise l'hôte et le preset ne rend la
clé que s'ils sont identiques : une clé n'est jamais envoyée à un autre hôte que celui pour
lequel elle a été saisie. Une clé sans liaison n'est jamais rendue par une lecture liée.

`Chiffreur` est un port : `ChiffreurDpapi` (`CryptProtectData` / `CryptUnprotectData` par
`ctypes`, portée utilisateur courant, sans interface) sous Windows ; les tests injectent un
chiffreur factice.
"""

from __future__ import annotations

import contextlib
import ctypes
import json
import logging
import re
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Final, Literal, Protocol

from pydantic import SecretStr

LOGGER: Final = logging.getLogger("slmsp.app.cle_externe")
NOM_FICHIER: Final = "modele-externe.cle"
MOTIF_ID: Final = re.compile(r"^[a-z0-9][a-z0-9-]{0,31}$")
"""Identifiant d'un fournisseur (nom de fichier sûr)."""
LONGUEUR_MAX: Final = 4096
CRYPTPROTECT_UI_FORBIDDEN: Final = 0x1
ENTROPIE: Final = b"AssistantSP/modele-externe"
EtatCle = Literal["absente", "liee", "autre-hote"]


class Chiffreur(Protocol):
    def proteger(self, donnees: bytes) -> bytes: ...

    def deproteger(self, donnees: bytes) -> bytes: ...


class _Blob(ctypes.Structure):
    _fields_ = [("cbData", ctypes.c_uint32), ("pbData", ctypes.POINTER(ctypes.c_char))]


def _blob(donnees: bytes) -> tuple[_Blob, Any]:
    tampon = ctypes.create_string_buffer(donnees, len(donnees))
    return _Blob(len(donnees), ctypes.cast(tampon, ctypes.POINTER(ctypes.c_char))), tampon


class ChiffreurDpapi:
    """DPAPI de l'utilisateur courant (Windows seulement)."""

    def __init__(self) -> None:
        if sys.platform != "win32":
            raise OSError("DPAPI : Windows seulement")
        self._crypt32 = ctypes.windll.crypt32  # type: ignore[attr-defined]
        self._kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]

    def _dpapi(self, fonction: Any, donnees: bytes) -> bytes:
        # Même forme pour les deux fonctions : entrée, description, entropie, réservé,
        # invite, drapeaux, sortie.
        entree, _t1 = _blob(donnees)
        entropie, _t2 = _blob(ENTROPIE)
        sortie = _Blob()
        ok = fonction(
            ctypes.byref(entree),
            None,
            ctypes.byref(entropie),
            None,
            None,
            CRYPTPROTECT_UI_FORBIDDEN,
            ctypes.byref(sortie),
        )
        if not ok:
            raise OSError("DPAPI : échec")
        try:
            return ctypes.string_at(sortie.pbData, sortie.cbData)
        finally:
            self._kernel32.LocalFree(sortie.pbData)

    def proteger(self, donnees: bytes) -> bytes:
        return self._dpapi(self._crypt32.CryptProtectData, donnees)

    def deproteger(self, donnees: bytes) -> bytes:
        return self._dpapi(self._crypt32.CryptUnprotectData, donnees)


class CoffreCle:
    """Lecture, écriture et effacement de la clé chiffrée."""

    def __init__(
        self, dossier: Path, chiffreur: Chiffreur | None = None, *, nom_fichier: str = NOM_FICHIER
    ) -> None:
        self.chemin = Path(dossier) / nom_fichier
        self._chiffreur = chiffreur

    def _chiffreur_actif(self) -> Chiffreur:
        if self._chiffreur is None:
            self._chiffreur = ChiffreurDpapi()
        return self._chiffreur

    def enregistrer(self, cle: str, *, hote: str | None = None, preset: str | None = None) -> None:
        """Chiffre et écrit `cle`, liée à `hote` et `preset` s'ils sont donnés ; `ValueError`
        si elle est vide, trop longue ou invalide."""
        if not isinstance(cle, str) or not cle.strip() or len(cle) > LONGUEUR_MAX:
            raise ValueError("clé vide ou trop longue")
        if any(c.isspace() for c in cle.strip()) or not cle.strip().isprintable():
            raise ValueError("clé invalide")
        if hote is None and preset is None:
            contenu = cle.strip()
        else:
            if not hote or not preset:
                raise ValueError("liaison incomplète")
            contenu = json.dumps({"cle": cle.strip(), "hote": hote, "preset": preset})
        chiffre = self._chiffreur_actif().proteger(contenu.encode("utf-8"))
        self.chemin.parent.mkdir(parents=True, exist_ok=True)
        temporaire = self.chemin.with_suffix(".tmp")
        temporaire.write_bytes(chiffre)
        temporaire.replace(self.chemin)

    def _contenu(self) -> tuple[SecretStr, tuple[str, str] | None] | None:
        """(clé, (hôte, preset) ou `None` si la clé n'est pas liée), ou `None`."""
        try:
            chiffre = self.chemin.read_bytes()
        except OSError:
            return None
        try:
            texte = self._chiffreur_actif().deproteger(chiffre).decode("utf-8")
        except Exception as exc:
            LOGGER.warning("clé du modèle externe illisible (%s)", type(exc).__name__)
            return None
        if texte.startswith("{"):
            try:
                donnees = json.loads(texte)
                cle, hote, preset = donnees["cle"], donnees["hote"], donnees["preset"]
            except (ValueError, KeyError, TypeError):
                LOGGER.warning("clé du modèle externe illisible (format)")
                return None
            if not all(isinstance(v, str) and v for v in (cle, hote, preset)):
                return None
            return SecretStr(cle), (hote, preset)
        return (SecretStr(texte), None) if texte else None

    def lire(self, *, hote: str | None = None, preset: str | None = None) -> SecretStr | None:
        """Clé déchiffrée, ou `None` (absente, illisible, autre utilisateur). Avec `hote` ou
        `preset` : `None` aussi si la clé n'est pas liée à ce couple exact."""
        contenu = self._contenu()
        if contenu is None:
            return None
        cle, liaison = contenu
        if (hote is not None or preset is not None) and liaison != (hote, preset):
            return None
        return cle

    def etat(self, hote: str, preset: str) -> EtatCle:
        """`absente`, `liee` (à ce couple hôte, preset) ou `autre-hote` (clé liée à un autre
        couple, ou sans liaison)."""
        contenu = self._contenu()
        if contenu is None:
            return "absente"
        return "liee" if contenu[1] == (hote, preset) else "autre-hote"

    def presente(self) -> bool:
        return self.lire() is not None

    def effacer(self) -> None:
        with contextlib.suppress(FileNotFoundError):
            self.chemin.unlink()


def id_valide(identifiant: object) -> bool:
    return isinstance(identifiant, str) and MOTIF_ID.fullmatch(identifiant) is not None


class CoffreCles:
    """Une clé chiffrée par fournisseur externe ; `ValueError` pour un identifiant invalide."""

    PREFIXE: Final = "fournisseur-"

    def __init__(self, dossier: Path, chiffreur: Chiffreur | None = None) -> None:
        self.dossier = Path(dossier)
        self._chiffreur = chiffreur

    def _chiffreur_partage(self) -> Chiffreur:
        if self._chiffreur is None:
            self._chiffreur = ChiffreurDpapi()
        return self._chiffreur

    def pour(self, identifiant: str) -> CoffreCle:
        if not id_valide(identifiant):
            raise ValueError("identifiant de fournisseur invalide")
        return CoffreCle(self.dossier, self, nom_fichier=f"{self.PREFIXE}{identifiant}.cle")

    # Chiffreur partagé (DPAPI créée à la première utilisation, dans le `try` de `lire`).
    def proteger(self, donnees: bytes) -> bytes:
        return self._chiffreur_partage().proteger(donnees)

    def deproteger(self, donnees: bytes) -> bytes:
        return self._chiffreur_partage().deproteger(donnees)

    def lire(
        self, identifiant: str, *, hote: str | None = None, preset: str | None = None
    ) -> SecretStr | None:
        """Clé déchiffrée, ou `None` (absente, illisible, identifiant invalide, ou liée à un
        autre couple hôte, preset que celui demandé)."""
        if not id_valide(identifiant):
            return None
        return self.pour(identifiant).lire(hote=hote, preset=preset)

    def presente(self, identifiant: str) -> bool:
        return self.lire(identifiant) is not None

    def etat(self, identifiant: str, hote: str, preset: str) -> EtatCle:
        if not id_valide(identifiant):
            return "absente"
        return self.pour(identifiant).etat(hote, preset)

    def enregistrer(
        self, identifiant: str, cle: str, *, hote: str | None = None, preset: str | None = None
    ) -> None:
        self.pour(identifiant).enregistrer(cle, hote=hote, preset=preset)

    def effacer_si_autre_hote(self, identifiant: str, hote: str, preset: str) -> None:
        """Efface la clé de `identifiant` si elle n'est pas liée à ce couple hôte, preset."""
        if self.etat(identifiant, hote, preset) == "autre-hote":
            self.effacer(identifiant)

    def effacer(self, identifiant: str) -> None:
        if id_valide(identifiant):
            self.pour(identifiant).effacer()

    def ne_garder_que(self, identifiants: Iterable[str]) -> None:
        """Efface les clés des fournisseurs retirés du réglage."""
        gardes = {f"{self.PREFIXE}{i}.cle" for i in identifiants}
        if not self.dossier.is_dir():
            return
        for fichier in self.dossier.glob(f"{self.PREFIXE}*.cle"):
            if fichier.name not in gardes:
                with contextlib.suppress(OSError):
                    fichier.unlink()


__all__ = ["Chiffreur", "ChiffreurDpapi", "CoffreCle", "CoffreCles", "EtatCle", "id_valide"]
