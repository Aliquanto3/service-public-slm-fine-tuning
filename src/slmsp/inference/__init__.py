"""Inférence locale par llama.cpp (AD-6, AD-27), seul lanceur des binaires llama.cpp.

- `processus` : sous-processus dans un Job Object `KILL_ON_JOB_CLOSE`, registre
  `SLMSP_VAR_DIR/pids/`, nettoyage des orphelins ;
- `serveur` : binaires du tag figé, `version`, conversion et quantification,
  `ServeurLlama` (génération ou embedding) ;
- `client` : `ClientLlama`, implémentation de `LlmPort` (flux SSE, appels d'outils) ;
- `embedding` : `EmbedderLlama`, implémentation de `EmbedderPort`.

Les échanges HTTP passent uniquement par `slmsp.net.client_local(port)`. Ce paquet
n'exporte rien au chargement : importer les sous-modules.
"""
