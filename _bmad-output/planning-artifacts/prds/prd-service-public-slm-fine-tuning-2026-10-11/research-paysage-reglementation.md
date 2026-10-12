# Recherche : paysage, MCP data.gouv, réglementation (2026-10-11, passe unique, sources surtout secondaires)

## Solutions comparables
- Albert (DINUM/AgentPublic) : France Services depuis 2023, réponses sourcées ; janvier 2026, la DINUM annonce qu'il ne sera pas généralisé « dans sa forme actuelle » (erreurs, instabilité). Albert est aussi une API multi-modèles en SecNumCloud.
- Assistant IA de l'État : expérimentation en octobre 2025 (10 000 agents, modèle Mistral sur l'infrastructure Albert), généralisation annoncée en juin 2026, 43 000 utilisateurs en août 2026. Cloud souverain, pas d'exécution locale.
- LLaMandement (DGFiP + DINUM) : LLM affiné pour résumer les amendements, cas d'usage étroit.
- Non vérifiés : MirAI, outils des collectivités, assistants locaux grand public. Hypothèse : le créneau « local, hors ligne, en un clic, spécialisé secteur public » est peu occupé, puisque toutes les offres de l'État sont dans le cloud.

## Serveur MCP data.gouv (source primaire : github.com/datagouv/datagouv-mcp)
- URL https://mcp.data.gouv.fr/mcp (préproduction : mcp.preprod.data.gouv.fr), Streamable HTTP uniquement, GET /health, sans authentification, en lecture seule, auto-hébergeable (Docker/Python).
- Outils : search_datasets, get_dataset_info, list_dataset_resources, get_resource_info, query_resource_data, search_organizations, search_dataservices, get_dataservice_info, get_dataservice_openapi_spec, get_metrics (prod). La presse cite aussi download_and_parse_resource, donc la liste évolue.
- Statut « expérimental » : pas de garantie de stabilité ni de release. Il faut gérer la dérive des schémas. Attention aux faux serveurs MCP « data.gouv ».

## Réglementation
- AI Act, art. 50 (transparence) : applicable au 2 août 2026, calendrier à confirmer après le Digital Omnibus. Qualification a priori : risque limité, sauf usage décisionnel sur l'accès des usagers aux services publics essentiels (annexe III). Analyse non vérifiée par une source.
- ANSSI : recommandations de sécurité pour un système d'IA générative (29/04/2024, 35 recommandations).
- Non vérifiés : RGPD, doctrine de l'État, RGAA 4.1, homologation RGS.

## Sources
github.com/datagouv/datagouv-mcp ; data.gouv.fr/fr/posts/experimentation-autour-dun-serveur-mcp-pour-datagouv ; acteurspublics.fr (généralisation de l'Assistant IA, 43 000 utilisateurs) ; weka.fr/actualite/?p=209194 ; actuia.com (LLaMandement) ; cyber.gouv.fr (recommandations IA générative) ; cms.law et houthoff.com (Digital Omnibus).
