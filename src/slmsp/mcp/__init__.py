"""Outils data.gouv : outils figés, cassettes, rejeu et client MCP en direct (AD-8, AD-10).

`slmsp.mcp.enregistrer(session, magasin)` est l'API unique d'enregistrement des cassettes.
Le client direct (`slmsp.mcp.direct`) n'est pas réexporté : `import slmsp.mcp` reste léger.
"""

from slmsp.mcp.enregistrement import SessionMcp, enregistrer

__all__ = ["SessionMcp", "enregistrer"]
