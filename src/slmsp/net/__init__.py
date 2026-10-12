"""Passerelle réseau unique (AD-4) : seul paquet autorisé à importer un client HTTP.

`slmsp.net.client(profil, ...)` désigne la fonction fabrique (pas le module) ; importer les
autres symboles par `from slmsp.net.client import ...`.
"""

from slmsp.net.client import Passerelle, client, client_local, fabrique_hf, fabrique_hf_async

__all__ = ["Passerelle", "client", "client_local", "fabrique_hf", "fabrique_hf_async"]
