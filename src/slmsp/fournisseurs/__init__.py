"""Fournisseurs d'API compatibles OpenAI (Chat Completions), sous budget et journalisés (S3).

Seul fournisseur : OpenRouter (décision d'Anaël du 2026-10-19 ; GPT et Gemini sont exclus).
`slmsp.fournisseurs.client.ClientCompatibleOpenAI.appeler` est un appel générique
« messages → texte + usage » : les juges tiers (`slmsp.judge.tiers`) s'en servent, et la
comparaison des générateurs (story S4) pourra s'en servir avec son propre usage de budget et
son propre journal. Les requêtes passent par la passerelle réseau (`slmsp.net`, profil
`outillage`) ; aucun SDK.
"""
