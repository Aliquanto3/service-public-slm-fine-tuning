"""Construit l'échantillon de calibrage (16 items, 2 par Tâche) du Jeu d'évaluation maison.

Usage (Windows, sans python dans le PATH) :

    uv run --python 3.12 --with openpyxl python -I eval/calibrage/build_calibrage.py \
        --sources data/raw/eval-sources --out eval/calibrage

Le script est déterministe : il lit uniquement des fichiers déjà téléchargés
(dossier --sources, gitignoré) et les cassettes MCP enregistrées (--out/cassettes).
Les sous-commandes facultatives `fetch` et `record` refont les téléchargements et
l'enregistrement des cassettes ; elles ne sont jamais appelées par défaut, afin
que l'échantillon figé reste rejouable à l'identique (FR-24, FR-40).

    ... build_calibrage.py fetch  --sources data/raw/eval-sources   # + --with duckdb
    ... build_calibrage.py record --out eval/calibrage               # réécrit les cassettes

Ce jeu sert UNIQUEMENT à l'évaluation. Il ne doit jamais entrer dans les Données
d'entraînement.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

CONSULTATION = "2026-10-12"
SP_PARQUET = ("https://huggingface.co/datasets/AgentPublic/service-public/resolve/"
              "refs%2Fconvert%2Fparquet/latest/train/0000.parquet")
LEGI_PARQUET_LIST = "https://huggingface.co/api/datasets/AgentPublic/legi/parquet/latest/train"
QUESTIONS_XLSX = ("https://huggingface.co/datasets/AgentPublic/assistant_ia_questions_corpus/"
                  "resolve/main/evaluation_qo_assistant_ia_v1.xlsx")
MCP_URL = "https://mcp.data.gouv.fr/mcp"
LIC_ETALAB = "Licence Ouverte / Etalab 2.0 (etalab-2.0, déclarée sur la carte du dataset Hugging Face)"
LIC_CREATION = "Création originale du projet (contenu fictif rédigé pour l'évaluation) ; pas de source tierce"
SP_FICHES = ["F1344", "F34440", "F1878", "F38187", "F2859"]
LEGI_ARTICLES = ["L112-3", "R112-5", "L231-1", "L112-6", "R112-4"]
GEODAE_DATASET = "61556e1e9d6adb2df86eb0fc"
GEODAE_CSV = "edb6a9e1-2f16-4bbf-99e7-c3eb6b90794c"


# ---------------------------------------------------------------------------
# Chargement des sources brutes (données non fiables : lecture seule, aucun eval)
# ---------------------------------------------------------------------------
def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def sp_doc(src: Path, doc_id: str) -> dict:
    d = load_json(src / "hf" / f"sp_{doc_id}.json")
    rows = sorted(d["rows"], key=lambda r: r["chunk_index"])
    assert rows and rows[0]["doc_id"] == doc_id, doc_id
    return {"title": rows[0]["title"], "url": rows[0]["url"], "audience": rows[0]["audience"],
            "chunks": {r["chunk_index"]: r for r in rows}}


def sp_text(doc: dict, idx: list[int]) -> str:
    return "\n".join(doc["chunks"][i]["text"].strip() for i in idx)


def legi_articles(src: Path) -> dict:
    d = load_json(src / "hf" / "legi_crpa.json")
    out = {}
    for r in d["rows"]:
        out[r["number"]] = {"doc_id": r["doc_id"], "text": "\n".join(re.sub(r"[ \t]+", " ", ln).strip()
                                                            for ln in r["text"].strip().splitlines()),
                            "start_date": r["start_date"], "full_title": r["full_title"]}
    return out


def legifrance_url(doc_id: str) -> str:
    return f"https://www.legifrance.gouv.fr/codes/article_lc/{doc_id}"


def question_seeds(src: Path) -> list[str]:
    import openpyxl  # dépendance déclarée dans l'en-tête
    wb = openpyxl.load_workbook(src / "hf" / "assistant_ia_questions.xlsx", read_only=True)
    ws = wb.worksheets[0]
    return [r[0] for r in ws.iter_rows(min_row=2, values_only=True)]


def mcp_text(cassette: dict, i: int) -> str:
    resp = cassette["interactions"][i]["response"]
    return resp["result"]["content"][0]["text"]


def words(t: str) -> int:
    return len(t.split())


# ---------------------------------------------------------------------------
# Tâche 5 : fautes injectées, positions calculées dans le texte fautif
# ---------------------------------------------------------------------------
def inject(correct: str, fautes: list[tuple[str, str, str, str]]) -> tuple[str, list[dict]]:
    """fautes = (ancre_correcte, correction, erreur, type). L'ancre est unique dans le texte."""
    faulty = correct
    for ancre, corr, err, _ in fautes:
        assert correct.count(ancre) == 1, f"ancre non unique : {ancre!r}"
        assert ancre.count(corr) >= 1, (ancre, corr)
        assert faulty.count(ancre) == 1, f"ancres qui se chevauchent : {ancre!r}"
        faulty = faulty.replace(ancre, ancre.replace(corr, err, 1), 1)
    out = []
    for ancre, corr, err, typ in fautes:
        fa = ancre.replace(corr, err, 1)
        assert faulty.count(fa) == 1, f"ancre fautive non unique : {fa!r}"
        start = faulty.index(fa) + fa.index(err)
        out.append({"debut": start, "fin": start + len(err), "erreur": err, "correction": corr,
                    "type": typ, "contexte_fautif": fa})
    out.sort(key=lambda f: f["debut"])
    return faulty, out


# ---------------------------------------------------------------------------
# Construction des items
# ---------------------------------------------------------------------------
def build_items(src: Path, cass_dir: Path) -> list[dict]:
    seeds = question_seeds(src)
    items: list[dict] = []

    # ---------------- Tâche 1 : Question ----------------
    seed_cni = next(s for s in seeds if s and "carte d" in s and "gratuite" in s)
    f1344 = sp_doc(src, "F1344")
    assert "25 €" in f1344["chunks"][4]["text"] and "3 mois" in f1344["chunks"][8]["text"]
    items.append({
        "id": "Q-001", "tache": "Question", "difficulte": "facile",
        "entree": ("Une usagère vient de perdre sa carte d'identité en France. Elle me demande si "
                   "la nouvelle carte est gratuite et ce qu'elle doit faire. Que dois-je lui répondre ?"),
        "amorce_usager": seed_cni,
        "reponse_reference": (
            "Non, le renouvellement d'une carte d'identité perdue n'est pas gratuit : il faut un timbre "
            "fiscal de 25 € (12,50 € en Guyane). Si elle refait sa carte tout de suite, la déclaration de "
            "perte se fait au guichet de la mairie au moment du dépôt du dossier (cerfa n°14011), sans "
            "passer par la police. Elle peut déposer sa demande dans n'importe quelle mairie équipée d'une "
            "station d'enregistrement, souvent sur rendez-vous, avec une photo de moins de 6 mois, un "
            "justificatif de domicile, la déclaration de perte et le timbre fiscal (plus son passeport s'il "
            "est valide ou périmé depuis moins de 5 ans). Sa présence est obligatoire pour les empreintes, et "
            "la carte doit être retirée dans les 3 mois. Ne vaut pas avis juridique."),
        "sources_attendues": [f1344["url"]],
        "elements_cles": [
            "Pas gratuit : timbre fiscal de 25 € (12,50 € en Guyane)",
            "Déclaration de perte faite en mairie lors du dépôt si nouvelle demande immédiate (sinon commissariat ou gendarmerie)",
            "Dépôt dans n'importe quelle mairie équipée d'une station d'enregistrement, souvent sur rendez-vous",
            "Pièces : photo de moins de 6 mois, justificatif de domicile, déclaration de perte (cerfa n°14011), timbre fiscal",
            "Présence obligatoire (empreintes) et retrait de la carte dans les 3 mois",
        ],
        "mention_obligatoire": "Ne vaut pas avis juridique",
        "provenance": [
            {"source": "AgentPublic/assistant_ia_questions_corpus (evaluation_qo_assistant_ia_v1.xlsx)",
             "url": QUESTIONS_XLSX, "role": "amorce de question usager, reformulée par un agent",
             "consulte_le": CONSULTATION},
            {"source": f"MediaTech AgentPublic/service-public, fiche F1344 « {f1344['title']} »",
             "url": f1344["url"], "role": "fiche de référence (chunks 2 à 8, cas « En France »)",
             "consulte_le": CONSULTATION},
        ],
        "licence_source": f"Amorce : MIT (carte du dataset). Fiche : {LIC_ETALAB}.",
    })

    seed_ppg = next(s for s in seeds if s and "PPG" in s)
    absence = load_json(src / "hf" / "absence_ppg.json")
    assert all(len(v) == 0 for k, v in absence["matches"].items() if "solidarit" not in k)
    items.append({
        "id": "Q-002", "tache": "Question", "difficulte": "difficile",
        "entree": ("Dans une note de la préfecture, on nous demande de suivre « l'avancement des PPG » "
                   "pour notre territoire. Qu'est-ce que les PPG et où trouver la liste officielle ?"),
        "amorce_usager": seed_ppg,
        "reponse_reference": (
            "Je ne trouve pas de source officielle sur les « PPG » dans les fiches dont je dispose. "
            "Je ne peux donc pas vous en donner une définition ni une liste sourcées. Je vous conseille "
            "de vous adresser au service de la préfecture qui a émis la note, ou de consulter les "
            "publications officielles du Gouvernement. Ne vaut pas avis juridique."),
        "comportement_attendu": "absence_de_source",
        "sources_attendues": [],
        "elements_cles": [
            "Dit explicitement qu'aucune source officielle de l'Index local ne traite des PPG",
            "N'invente aucune URL et ne cite aucune fiche service-public comme source",
            "Oriente vers le service émetteur de la note (préfecture) ou les publications officielles du Gouvernement",
            "Si un développement du sigle est proposé (p. ex. « politiques prioritaires du Gouvernement »), il est présenté comme non sourcé et à vérifier",
        ],
        "mention_obligatoire": "Ne vaut pas avis juridique",
        "verification_absence": {
            "corpus": "AgentPublic/service-public (config latest)",
            "motifs_recherches_regex_insensible_casse": [k for k in absence["matches"] if "solidarit" not in k],
            "resultat": "0 fiche trouvée pour chaque motif (contrôle positif « journée de solidarité » : 3 fiches)",
            "date": absence["checked"],
        },
        "provenance": [
            {"source": "AgentPublic/assistant_ia_questions_corpus (evaluation_qo_assistant_ia_v1.xlsx)",
             "url": QUESTIONS_XLSX, "role": "amorce « Qu'est-ce que les PPG ? »", "consulte_le": CONSULTATION},
            {"source": "Recherche plein texte dans le parquet MediaTech service-public", "url": SP_PARQUET,
             "role": "preuve d'absence de source", "consulte_le": CONSULTATION},
        ],
        "licence_source": f"Amorce : MIT. Corpus vérifié : {LIC_ETALAB}.",
    })

    # ---------------- Tâche 2 : Recherche de données ----------------
    c1 = load_json(cass_dir / "R-001.json")
    info = mcp_text(c1, 1)
    titre = re.search(r"Dataset Information: (.+)", info).group(1).strip()
    org = re.search(r"Organization: (.+)", info).group(1).strip()
    maj = re.search(r"Last updated: (\S+)", info).group(1)
    url = re.search(r"URL: (\S+)", info).group(1)
    lic = re.search(r"License: (\S+)", info).group(1)
    autres = re.findall(r"\n\d+\. (.+)\n\s+ID: \S+\n(?:.*\n)*?\s+Organization: (.+)", mcp_text(c1, 0))
    items.append({
        "id": "R-001", "tache": "Recherche de données", "difficulte": "facile",
        "entree": ("Je prépare une carte des défibrillateurs pour la commune. Quels jeux de données "
                   "existent sur data.gouv.fr ? Pour la base nationale, donne-moi le producteur et la date "
                   "de dernière mise à jour."),
        "appels_attendus": [
            {"outil": "search_datasets", "arguments": {"query": "défibrillateurs"},
             "regle": "query contient « défibrillateur » ou « DAE » (insensible à la casse et aux accents) ; autres paramètres optionnels"},
            {"outil": "get_dataset_info", "arguments": {"dataset_id": GEODAE_DATASET},
             "regle": "dataset_id exact"},
        ],
        "reponse_reference": {
            "jeu_principal": {"titre": titre, "producteur": org, "derniere_mise_a_jour": maj,
                              "url": url, "licence": lic},
            "autres_jeux_cites_possibles": [{"titre": t.strip(), "producteur": o.strip()} for t, o in autres[1:]],
            "texte": (f"La base nationale est « {titre} », produite par {org}, mise à jour le "
                      f"{maj[:10]} (licence {lic}) : {url}. D'autres jeux existent, par exemple ceux de "
                      + ", ".join(o.strip() for _, o in autres[1:4]) + "."),
        },
        "cassette": "cassettes/R-001.json",
        "provenance": [{"source": "Serveur MCP data.gouv (search_datasets, get_dataset_info)", "url": MCP_URL,
                        "role": "réponses enregistrées (Bac à sable MCP)", "consulte_le": c1["recorded_at"]}],
        "licence_source": f"Métadonnées data.gouv.fr ; licence du jeu déclarée : {lic} (Licence Ouverte v2).",
    })

    c2 = load_json(cass_dir / "R-002.json")
    q = mcp_text(c2, 2)
    total = int(re.search(r"Total rows \(Tabular API\): (\d+)", q).group(1))
    lignes = []
    for bloc in re.split(r"\n  Row \d+:\n", q)[1:]:
        champ = dict(re.findall(r"^\s{4}(\w+): ?(.*)$", bloc, flags=re.M))
        lignes.append({"c_nom": champ.get("c_nom", "").strip(),
                       "adresse": f"{champ.get('c_adr_num', '').strip()} {champ.get('c_adr_voie', '').strip()}".strip(),
                       "c_etat_valid": champ.get("c_etat_valid", "").strip()})
    assert total > 0 and len(lignes) == 5
    items.append({
        "id": "R-002", "tache": "Recherche de données", "difficulte": "difficile",
        "entree": ("Combien de défibrillateurs sont recensés dans la base nationale Géo'DAE pour Lorient "
                   "(code INSEE 56121) ? Donne le nombre et les 5 premiers lieux renvoyés, dans un tableau sourcé."),
        "appels_attendus": [
            {"outil": "search_datasets", "arguments": {"query": "défibrillateurs"},
             "regle": "query contient « défibrillateur », « DAE » ou « Géo'DAE » ; peut être omis si le modèle passe directement l'identifiant connu"},
            {"outil": "list_dataset_resources", "arguments": {"dataset_id": GEODAE_DATASET}, "regle": "dataset_id exact"},
            {"outil": "query_resource_data",
             "arguments": {"resource_id": GEODAE_CSV, "filter_column": "c_com_insee", "filter_value": "56121",
                           "filter_operator": "exact", "page_size": 5},
             "regle": "resource_id exact (ressource CSV, pas JSON) ; filtre c_com_insee = 56121 (exact) ; page_size >= 5"},
        ],
        "reponse_reference": {
            "nombre_total": total,
            "cinq_premiers": lignes,
            "precision": "Le total est celui de l'API tabulaire au moment de l'enregistrement ; il inclut des DAE « en attente de validation ».",
            "texte": f"La base Géo'DAE recense {total} défibrillateurs pour Lorient (56121), selon l'API tabulaire de data.gouv.fr.",
        },
        "criteres": ["Valeurs du tableau identiques à la cassette (FR-8)", "Lien vers le jeu ou la ressource cité",
                     "Ne pas confondre avec le nombre de pages ni filtrer sur c_com_nom (casse variable)"],
        "cassette": "cassettes/R-002.json",
        "provenance": [{"source": "Serveur MCP data.gouv (search_datasets, list_dataset_resources, query_resource_data)",
                        "url": MCP_URL, "role": "réponses enregistrées (Bac à sable MCP)",
                        "consulte_le": c2["recorded_at"]}],
        "licence_source": "Géo'DAE (Atlasanté) : Licence Ouverte v2 (lov2) selon get_dataset_info.",
    })

    # ---------------- Tâche 3 : Compte rendu ----------------
    items.append(cr_001())
    items.append(cr_002())

    # ---------------- Tâche 4 : Langage clair ----------------
    f34440 = sp_doc(src, "F34440")
    lc1 = sp_text(f34440, [5, 7, 8, 9, 10])
    items.append({
        "id": "LC-001", "tache": "Langage clair", "difficulte": "facile",
        "entree": {"consigne": "Réécris ce texte en langage clair pour un usager, sans perdre d'information.",
                   "texte": lc1, "nb_mots": words(lc1)},
        "informations_a_conserver": [
            "Le FPS se paie dans un délai de 3 mois à partir de la notification de l'avis de paiement",
            "La date limite figure sur l'avis de paiement",
            "Sans paiement dans les 3 mois : majoration, émission d'un titre exécutoire et envoi d'un avertissement",
            "Majoration = 20 % du FPS impayé restant dû, au minimum 50 €",
            "Payer FPS + majoration dans 1 mois après l'envoi de l'avertissement donne droit à une diminution de 20 % de la majoration",
            "Au-delà : le comptable public peut engager le recouvrement (biens, comptes bancaires, salaires, véhicules)",
            "Délai de paiement ou remise gracieuse : s'adresser à la trésorerie indiquée sur l'avertissement, seule compétente pour un délai",
        ],
        "termes_juridiques_a_conserver": ["forfait post-stationnement (FPS)", "avis de paiement", "titre exécutoire",
                                          "majoration", "avertissement", "comptable public", "remise gracieuse", "trésorerie"],
        "provenance": [{"source": f"MediaTech AgentPublic/service-public, fiche F34440 « {f34440['title']} » (chunks 5, 7, 8, 9, 10)",
                        "url": f34440["url"], "consulte_le": CONSULTATION}],
        "licence_source": LIC_ETALAB,
    })

    legi = legi_articles(src)
    arts = ["L112-3", "R112-5", "L112-6"]
    lc2 = "\n".join(f"Article {a[0]}. {a[1:]} : {legi[a]['text']}" for a in arts)
    items.append({
        "id": "LC-002", "tache": "Langage clair", "difficulte": "difficile",
        "entree": {"consigne": ("Réécris ces articles en langage clair pour expliquer à un usager ce qu'est un "
                                "accusé de réception et à quoi il sert. Signale les termes juridiques que tu ne simplifies pas."),
                   "texte": lc2, "nb_mots": words(lc2)},
        "informations_a_conserver": [
            "Toute demande adressée à l'administration fait l'objet d'un accusé de réception (L. 112-3)",
            "Exceptions : demandes abusives (nombre, caractère répétitif ou systématique) et demandes définies par décret en Conseil d'État (bref délai de réponse, ou simple prestation ou délivrance d'un document prévus par les textes)",
            "L'accusé de réception indique la date de réception de la demande et la date à laquelle, sans décision expresse, elle sera réputée acceptée ou rejetée",
            "Il indique le service chargé du dossier : désignation, adresse postale, le cas échéant électronique, et numéro de téléphone",
            "Il précise si le silence vaut rejet (et alors mentionne délais et voies de recours) ou acceptation (et alors la possibilité d'obtenir l'attestation prévue à l'article L. 232-3)",
            "Sans accusé de réception transmis ou complet, les délais de recours ne sont pas opposables au demandeur (L. 112-6)",
            "Exception : ils restent opposables si une décision expresse a été régulièrement notifiée avant la naissance de la décision implicite",
        ],
        "termes_juridiques_a_conserver": ["accusé de réception", "décision implicite d'acceptation", "décision implicite de rejet",
                                          "décision expresse", "délais et voies de recours", "opposables / inopposabilité",
                                          "décret en Conseil d'État", "notifiée"],
        "provenance": [{"source": f"MediaTech AgentPublic/legi, {legi[a]['full_title'] if legi[a]['full_title'] else 'CRPA'}, article {a} (en vigueur depuis {legi[a]['start_date']})",
                        "url": legifrance_url(legi[a]["doc_id"]),
                        "note": "URL Légifrance construite à partir de l'identifiant LEGIARTI (site non joignable en lecture automatique : HTTP 403)",
                        "consulte_le": CONSULTATION} for a in arts],
        "licence_source": LIC_ETALAB,
    })

    # ---------------- Tâche 5 : Correction ----------------
    items.extend(correction_items())

    # ---------------- Tâche 6 : Résumé ----------------
    f1878 = sp_doc(src, "F1878")
    rs1 = sp_text(f1878, [2, 3, 4, 5, 7])
    assert 400 <= words(rs1) <= 900, words(rs1)
    items.append({
        "id": "RS-001", "tache": "Résumé", "difficulte": "facile",
        "entree": {"consigne": "Fais un résumé court (3 à 5 phrases) de ce document pour un collègue d'accueil.",
                   "longueur_demandee": "courte (3 à 5 phrases)", "document": rs1, "nb_mots": words(rs1)},
        "points_cles_reference": [
            "L'ARS est soumise à un plafond de ressources (revenus 2024) : 28 956 € (1 enfant), 35 638 € (2 enfants), 42 320 € + 6 682 € par enfant supplémentaire (3 enfants ou plus) ; une allocation différentielle est possible en cas de léger dépassement",
            "L'enfant doit avoir entre 6 et 18 ans (né entre le 16 septembre 2008 et le 31 décembre 2020) et être scolarisé ou inscrit au Cned (pas d'ARS pour l'instruction en famille)",
            "Montants rentrée 2026 selon l'âge au 31 décembre 2025 : 426,87 € (6-10 ans), 450,41 € (11-14 ans), 466,02 € (15-18 ans), après CRDS",
            "Versement à partir du 18 août 2026 (4 août 2026 à La Réunion)",
        ],
        "provenance": [{"source": f"MediaTech AgentPublic/service-public, fiche F1878 « {f1878['title']} », cas général (chunks 2, 3, 4, 5, 7)",
                        "url": f1878["url"], "consulte_le": CONSULTATION}],
        "licence_source": LIC_ETALAB,
    })

    f38187 = sp_doc(src, "F38187")
    rs2 = sp_text(f38187, [2, 9, 12, 13, 14, 15])
    assert 400 <= words(rs2) <= 900, words(rs2)
    items.append({
        "id": "RS-002", "tache": "Résumé", "difficulte": "difficile",
        "entree": {"consigne": "Résume ce document en version moyenne (150 à 200 mots) pour les élus de la commission urbanisme.",
                   "longueur_demandee": "moyenne (150 à 200 mots)", "document": rs2, "nb_mots": words(rs2)},
        "points_cles_reference": [
            "Les parcs de stationnement extérieurs existants de plus de 1 500 m² (métropole, Guadeloupe, Martinique ; 1 000 m² à La Réunion, 2 500 m² en Guyane) doivent avoir des ombrières produisant de l'énergie renouvelable sur au moins la moitié de leur superficie",
            "L'obligation pèse sur le propriétaire, ou sur le concessionnaire, le délégataire ou le titulaire de l'autorisation d'occupation du domaine public",
            "Les propriétaires de parcs adjacents (même unité foncière) peuvent mutualiser l'obligation par un accord attesté",
            "Exceptions : parcs ombragés par des arbres sur la moitié de la surface (1 arbre pour 3 emplacements) ou produisant autrement une énergie renouvelable équivalente",
            "Calendrier hors concession : 1er juillet 2026 pour 10 000 m² et plus, 1er juillet 2028 entre 1 500 et 10 000 m² ; en concession, selon la date du contrat ; délai supplémentaire possible accordé par la préfecture",
            "Les ombrières intègrent des panneaux photovoltaïques sur toute leur partie supérieure",
            "Sanction jusqu'à 20 000 € (1 500 à 10 000 m²) ou 40 000 € (10 000 m² et plus), après procédure contradictoire, renouvelable chaque année jusqu'à la mise en conformité",
        ],
        "provenance": [{"source": f"MediaTech AgentPublic/service-public, fiche F38187 « {f38187['title']} » (chunks 2, 9, 12, 13, 14, 15)",
                        "url": f38187["url"], "consulte_le": CONSULTATION}],
        "licence_source": LIC_ETALAB,
    })

    # ---------------- Tâche 7 : Courrier type ----------------
    items.append({
        "id": "CT-001", "tache": "Courrier type", "difficulte": "facile",
        "entree": {
            "type": "demande de pièces",
            "objet": "Dossier d'inscription à l'accueil périscolaire incomplet",
            "elements_connus": {
                "destinataire": "Mme Sophie Lemaire",
                "date_reception_dossier": "2 octobre 2026",
                "pieces_manquantes": ["attestation d'assurance responsabilité civile",
                                      "justificatif de domicile de moins de 3 mois"],
                "delai_pour_fournir": "15 jours à compter de la réception du courrier",
                "service": "Service enfance-jeunesse de la mairie",
            },
            "consigne": "Rédige le courrier au format administratif français.",
        },
        "elements_obligatoires": [
            "En-tête de l'expéditeur (mairie, service enfance-jeunesse)", "Bloc destinataire (Mme Sophie Lemaire)",
            "Lieu et date", "Objet", "Référence du dossier (en emplacement)", "Formule d'appel « Madame, »",
            "Rappel de la réception du dossier le 2 octobre 2026", "Liste des 2 pièces manquantes, exactement",
            "Délai de 15 jours à compter de la réception du courrier", "Modalités de transmission (en emplacement si non fournies)",
            "Coordonnées du service pour toute question (en emplacement)", "Formule de politesse",
            "Signature : nom et qualité du signataire (en emplacement)",
        ],
        "champs_a_laisser_en_emplacement": [
            "[Adresse de l'usager]", "[Commune]", "[Référence du dossier]", "[Adresse, téléphone, courriel du service]",
            "[Nom et qualité du signataire]", "[Date du courrier]",
        ],
        "valeurs_interdites": ["toute adresse postale, tout numéro de téléphone ou courriel inventé",
                               "toute pièce supplémentaire non demandée", "tout nom de signataire inventé"],
        "provenance": [{"source": "Demande d'agent rédigée pour l'évaluation (scénario fictif)", "consulte_le": CONSULTATION}],
        "licence_source": LIC_CREATION,
    })
    items.append({
        "id": "CT-002", "tache": "Courrier type", "difficulte": "difficile",
        "entree": {
            "type": "accusé de réception",
            "objet": "Demande d'autorisation d'occupation temporaire du domaine public (terrasse de café)",
            "elements_connus": {
                "demandeur": "M. Karim Benali, gérant du café « Le Central »",
                "date_reception": "5 octobre 2026",
                "service_charge_du_dossier": "Service urbanisme et domaine public",
                "regime_du_silence": "selon le service, le silence gardé pendant 2 mois vaudra rejet de la demande",
            },
            "consigne": ("Rédige l'accusé de réception conforme au code des relations entre le public et "
                         "l'administration (article R. 112-5)."),
        },
        "elements_obligatoires": [
            "Date de réception de la demande : 5 octobre 2026",
            "Date à laquelle, à défaut de décision expresse, la demande sera réputée rejetée (5 décembre 2026, ou formulation équivalente « deux mois après la réception »)",
            "Désignation du service chargé du dossier : service urbanisme et domaine public",
            "Adresse postale, le cas échéant électronique, et numéro de téléphone du service (en emplacement)",
            "Mention que la demande est susceptible de donner lieu à une décision implicite de rejet",
            "Mention des délais et voies de recours contre la décision implicite de rejet (contenu en emplacement si non fourni)",
            "Format administratif : en-tête, destinataire, objet, référence, formule d'appel, formule de politesse, signature",
        ],
        "base_reglementaire": {"article": "CRPA R. 112-5", "url": legifrance_url(legi["R112-5"]["doc_id"]),
                               "texte": legi["R112-5"]["text"]},
        "champs_a_laisser_en_emplacement": [
            "[Adresse du demandeur]", "[Commune]", "[Référence du dossier]", "[Adresse postale du service]",
            "[Courriel du service]", "[Téléphone du service]", "[Nom et qualité du signataire]",
            "[Délais et voies de recours]",
        ],
        "valeurs_interdites": ["adresse, téléphone ou courriel du service inventés",
                               "annonce d'une décision implicite d'acceptation (le silence vaut rejet ici)",
                               "délai de recours chiffré présenté comme certain sans source fournie",
                               "mention de l'attestation de l'article L. 232-3 (réservée au cas d'acceptation implicite)"],
        "provenance": [
            {"source": "Demande d'agent rédigée pour l'évaluation (scénario fictif)", "consulte_le": CONSULTATION},
            {"source": "MediaTech AgentPublic/legi, CRPA article R112-5", "url": legifrance_url(legi["R112-5"]["doc_id"]),
             "role": "liste des mentions obligatoires", "consulte_le": CONSULTATION},
        ],
        "licence_source": f"Scénario : {LIC_CREATION}. Article R. 112-5 : {LIC_ETALAB}.",
    })

    # ---------------- Tâche 8 : Non-régression ----------------
    items.append({
        "id": "NR-001", "tache": "Non-régression", "difficulte": "facile",
        "entree": ("Une réunion commence à 9 h 45 et dure 2 h 50. Elle est suivie d'une pause déjeuner de "
                   "45 minutes. À quelle heure reprend le travail ? Explique ton calcul."),
        "reponse_reference": "13 h 20 (9 h 45 + 2 h 50 = 12 h 35 ; 12 h 35 + 45 min = 13 h 20).",
        "criteres": ["Résultat final : 13 h 20", "Étape intermédiaire juste (12 h 35)", "Réponse en français correct"],
        "provenance": [{"source": "Question rédigée pour l'évaluation (raisonnement, vérifiable par calcul)", "consulte_le": CONSULTATION}],
        "licence_source": LIC_CREATION,
    })
    items.append({
        "id": "NR-002", "tache": "Non-régression", "difficulte": "moyen",
        "entree": ("Reformule en une seule phrase, dans un registre soutenu adapté à un courrier administratif, "
                   "sans changer le sens : « On n'a pas pu traiter votre dossier parce qu'il manquait des papiers, "
                   "renvoyez-les vite. »"),
        "reponse_reference": ("Votre dossier n'a pas pu être traité, car il était incomplet ; nous vous remercions "
                              "de bien vouloir nous transmettre les pièces manquantes dans les meilleurs délais."),
        "criteres": [
            "Une seule phrase",
            "Registre soutenu : vouvoiement, pas de « on » familier, pas de « papiers » ni de « vite »",
            "Sens conservé : dossier non traité, cause = pièces manquantes, demande d'envoi rapide",
            "Aucun ajout : pas de délai chiffré, pas de liste de pièces, pas de nom de service inventés",
            "Orthographe et ponctuation correctes",
        ],
        "provenance": [{"source": "Consigne rédigée pour l'évaluation", "consulte_le": CONSULTATION}],
        "licence_source": LIC_CREATION,
    })

    order = ["Q-", "R-", "CR-", "LC-", "CO-", "RS-", "CT-", "NR-"]
    items.sort(key=lambda it: (order.index(re.match(r"[A-Z]+-", it["id"]).group(0)), it["id"]))
    return items


# ---------------------------------------------------------------------------
# Tâche 3 : notes de réunion fictives
# ---------------------------------------------------------------------------
CR1_NOTES = """COPIL France services itinérant – jeudi 08/10/2026 – 10h – salle du conseil, CC du Pays de Valmont
Présents : M. Garnier (vice-président CC, préside), Mme Okafor (DGS CC), Mme Ruiz (coordinatrice France services), M. Lambert (conseiller numérique), Mme Petit (CAF, partenaire), M. Diallo (préfecture, en visio la 1re heure seulement)
Excusée : Mme Roche (MSA), envoie ses chiffres par mail

Garnier ouvre, rappelle que c'est le 3e COPIL de l'année, ordre du jour envoyé la semaine dernière, pas d'ajout.

1. Bilan T3 (juillet-septembre)
- Ruiz : 1 412 accompagnements sur le trimestre, +18 % par rapport au T2. Été plus chargé que prévu, surtout fin août (rentrée).
- Top 3 des démarches : ANTS (cartes grises, titres d'identité), CAF (prime d'activité surtout), impôts (corrections de déclaration en ligne).
- Le bus passe dans 9 communes sur 11. Mornay et Les Essarts ne sont plus desservies depuis juin : à Mornay, plus de place pour stationner place de l'Église (marché déplacé) ; aux Essarts, travaux de voirie jusqu'à une date inconnue.
- Lambert : beaucoup de personnes âgées sans adresse mail, on en crée à chaque permanence, ça prend du temps. Il aimerait un support papier type pas-à-pas. Pas de suite donnée pour l'instant, Ruiz dit qu'elle en parlera en réunion d'équipe.
- Petit (CAF) : demande si on peut avoir un créneau de rendez-vous en visio avec un conseiller CAF dans le bus, une fois par mois. Ruiz : d'accord sur le principe, la CC aussi (Garnier : « oui allons-y »). Modalités et date de démarrage à caler entre Ruiz et Petit, pas de date fixée aujourd'hui.
- Garnier très satisfait du bilan. Il veut que le bilan annuel soit présenté au conseil communautaire de décembre. Tout le monde d'accord → Okafor l'inscrit à l'ordre du jour du conseil de décembre.

2. Tournée 2027
- Débat sur l'ajout d'un arrêt au hameau de Saint-Rémy. Lambert pour (demande de la mairie de Valmont, population âgée isolée). Okafor réservée : carburant + temps agent, et le bus est déjà plein le mardi. Garnier : on ne peut pas trancher sans chiffres.
→ pas de décision ; Ruiz sort la fréquentation par arrêt sur 2026 pour le prochain COPIL.
- Mornay : la mairie de Mornay propose le parking de la salle des fêtes (mail du maire du 2/10, lu en séance). DÉCISION : le bus revient à Mornay à partir du lundi 2 novembre 2026, stationnement sur le parking de la salle des fêtes, même créneau qu'avant (lundi matin).
- Les Essarts : on attend la fin des travaux, rien de décidé. Garnier demande qu'on garde l'info aux habitants à jour, mais personne n'est désigné.

3. Budget / matériel
- Okafor : le 2e ordinateur portable du bus est hors service (écran cassé, réparation plus chère que le neuf). DÉCISION : achat d'un poste de remplacement sur le budget 2026 (ligne équipement, environ 900 €). Okafor lance le bon de commande avant le vendredi 16 octobre.
- Lambert propose d'acheter aussi une imprimante portable pour éviter de renvoyer les gens en mairie pour imprimer. Okafor : pas de budget sur 2026, éventuellement à inscrire au budget primitif 2027 si le besoin est confirmé. Garnier ne se prononce pas. → pas décidé.
- Diallo (avant de quitter la visio vers 11h) rappelle que la labellisation France services sera réexaminée en 2027 : dossier à déposer avant le 31 mars 2027. Ruiz prépare le dossier, premier jet pour fin janvier 2027.

4. Communication
- Nouveaux horaires + retour à Mornay : Lambert fait un flyer, diffusion dans les 11 mairies avant le 1er novembre.
- Garnier souhaite un article sur le bus dans le magazine intercommunal de décembre. Okafor voit avec le service communication.
- Petit propose de relayer sur les réseaux de la CAF, « si on lui envoie le flyer ».

Divers
- Prochain COPIL fin janvier 2027, date à fixer par sondage (Ruiz l'envoie).
- Mme Roche (MSA) n'a pas encore envoyé ses chiffres, on les intégrera au bilan annuel s'ils arrivent.
Fin de séance 11h50."""

CR2_NOTES = """Commission Travaux – Cadre de vie — mardi 6/10/26, 18h30, mairie de Belcourt-sur-Vanne (salle 2)
pst : JP Morel (adjoint travaux, préside), C. Benoît, A. Haddad, L. Fontaine (conseillers maj.), N. Vidal (conseiller opposition), S. Marchal (DST), + M. Royer (asso Vivre à Belcourt) invité pour le pt 3 uniquement
abs. : F. Leclerc (excusé ; il voulait donner pouvoir à Morel → non, pas de pouvoir en commission, simple excuse)
secrétaire de séance : Fontaine (prend les notes, désolée pour le désordre)

pt 1 – école J. Ferry, réfection toiture (bât. B)
Marchal : consultation close le 25/09, 3 offres reçues. Moins-disante : Couverture Delmas 48 600 € HT, délai 10 semaines. Bati Ouest : 51 200 € HT, délai 6 semaines. 3e offre (Toitures du Val) 57 900 € HT, écartée (dossier incomplet ?? à confirmer par Marchal, je n'ai pas bien noté).
Discussion : on veut que ce soit fini avant l'hiver, les fuites dans la classe de CM1 empirent. Haddad demande si on peut mettre des pénalités de retard → Marchal : oui, déjà prévues au CCAP.
Benoît : Delmas a déjà travaillé pour la commune (salle des sports), bon souvenir. Mais le délai…
Le règlement de consultation pondère le délai à 40 %. Marchal : avec la grille, Bati Ouest arrive 1er.
AVIS de la commission : favorable à l'attribution à Bati Ouest – 5 pour, 1 abstention (Vidal, veut voir le rapport d'analyse complet avant de se prononcer).
Rappel Morel : la commission donne un avis, l'attribution sera votée au conseil municipal.
→ Marchal envoie le rapport d'analyse des offres à tous les membres avant vendredi (9/10).
→ inscription au conseil municipal du 22 octobre.

pt 2 – éclairage public / extinction nocturne
Proposition de départ de Morel : extinction de 23h à 5h dans tous les lotissements, maintien de l'éclairage dans le centre-bourg.
Fontaine : plutôt à partir de minuit, les gens rentrent tard du travail (gare). Benoît : et la sécurité ? Il faudrait l'avis de la gendarmerie avant. Vidal : d'accord pour économiser mais demande une évaluation.
Longue discussion, pas de consensus sur l'horaire ni sur le périmètre.
Morel propose alors une expérimentation : 6 mois, lotissement des Tilleuls seulement, 23h-5h, puis bilan en commission.
→ ACCORD de la commission à l'unanimité sur l'expérimentation (Tilleuls, 23h-5h, 6 mois).
Démarrage : dès que le SIEV (syndicat d'énergie) aura reprogrammé les horloges. Marchal demande une date au SIEV.
Consultation gendarmerie : Benoît s'en charge (courrier ou rendez-vous avec le commandant de brigade), avant fin octobre.
Réunion publique avec les habitants des Tilleuls : évoquée par Fontaine, « ce serait bien de les prévenir », tout le monde acquiesce mais personne ne prend le sujet. À revoir.
Haddad : et passer tout le parc en LED ? Marchal rappelle le chiffrage SIEV de 2024 (environ 380 k€). Pas à l'ordre du jour, renvoyé au débat budgétaire. Rien décidé.

pt 3 – place du Marché (avec M. Royer)
Royer présente une pétition (212 signatures) : plus de stationnement vélo + des bancs + « plus de vert ».
Morel : d'accord pour 2 arceaux vélo supplémentaires (10 places en plus), posés en régie par les services techniques, sur le budget fonctionnement voirie, avant fin novembre.
→ accord unanime.
Bancs : Vidal propose 4 bancs, Fontaine pense que 2 suffisent (passage des camions du marché). Marchal doit chiffrer les 2 options pour la prochaine commission. Pas de décision ce soir.
Végétalisation : hors du champ de ce soir, renvoyée au projet global de réaménagement de la place (2027-2028). Attention : l'étude n'est PAS lancée, ne pas annoncer de date aux habitants (Morel insiste).
Royer remercie et quitte la séance à 19h45.

pt 4 – divers
- Trottoir rue des Lavandières : chute d'une administrée signalée le 28/09. Marchal : reprise provisoire à l'enrobé à froid faite le 1/10. Réfection définitive : budget 2027 ? Morel voudrait plus tôt s'il reste du budget voirie 2026 → Marchal regarde le reliquat et revient vers Morel. Pas de date.
- Vidal : nids-de-poule chemin de la Garenne. Chemin rural donc commune ? Marchal pense que c'est la com com (voirie d'intérêt communautaire), à vérifier. Rien décidé.
- Haddad signale que le panneau d'affichage de l'école est cassé : Marchal le savait déjà, commande en cours (pas une décision de ce soir).
- Erratum Morel : le prochain conseil municipal est le 22 octobre (et pas le 20 comme dit en début de séance).
- Prochaine commission : mardi 17 novembre, 18h30.
Fin 20h20."""


def cr_001() -> dict:
    return {
        "id": "CR-001", "tache": "Compte rendu", "difficulte": "facile",
        "entree": {"consigne": "Rédige le compte rendu de cette réunion : participants, points abordés, décisions, actions (responsable, échéance).",
                   "notes": CR1_NOTES, "nb_mots": words(CR1_NOTES)},
        "participants_reference": ["M. Garnier (président de séance)", "Mme Okafor", "Mme Ruiz", "M. Lambert", "Mme Petit (CAF)",
                                   "M. Diallo (préfecture, en visio la 1re heure seulement)", "Excusée : Mme Roche (MSA)"],
        "decisions_reference": [
            "Le bus France services revient à Mornay à partir du lundi 2 novembre 2026, sur le parking de la salle des fêtes, le lundi matin",
            "Achat d'un ordinateur portable de remplacement sur le budget 2026 (environ 900 €)",
            "Accord de principe pour un créneau mensuel de rendez-vous en visio avec la CAF dans le bus",
            "Le bilan annuel sera présenté au conseil communautaire de décembre",
        ],
        "actions_reference": [
            {"action": "Lancer le bon de commande de l'ordinateur", "responsable": "Mme Okafor", "echeance": "avant le vendredi 16 octobre 2026"},
            {"action": "Inscrire le bilan à l'ordre du jour du conseil communautaire", "responsable": "Mme Okafor", "echeance": "conseil communautaire de décembre 2026"},
            {"action": "Fournir la fréquentation par arrêt sur 2026", "responsable": "Mme Ruiz", "echeance": "prochain COPIL (fin janvier 2027)"},
            {"action": "Caler les modalités et la date de démarrage du créneau visio CAF", "responsable": "Mme Ruiz et Mme Petit", "echeance": "non fixée"},
            {"action": "Préparer le dossier de labellisation France services", "responsable": "Mme Ruiz", "echeance": "premier jet fin janvier 2027 ; dépôt avant le 31 mars 2027"},
            {"action": "Réaliser et diffuser le flyer (nouveaux horaires, retour à Mornay) dans les 11 mairies", "responsable": "M. Lambert", "echeance": "avant le 1er novembre 2026"},
            {"action": "Voir avec le service communication pour un article dans le magazine intercommunal", "responsable": "Mme Okafor", "echeance": "magazine de décembre 2026"},
            {"action": "Envoyer le sondage pour fixer la date du prochain COPIL", "responsable": "Mme Ruiz", "echeance": "non précisée (COPIL fin janvier 2027)"},
        ],
        "pieges": [
            "Arrêt au hameau de Saint-Rémy : débattu, NON décidé",
            "Imprimante portable : proposée, NON décidée (éventuellement BP 2027)",
            "Les Essarts : aucune décision ; l'information des habitants n'a pas de responsable désigné",
            "Support papier pas-à-pas : simple idée, pas d'action ni de responsable",
            "Créneau visio CAF : aucune date de démarrage fixée, ne pas en inventer",
            "Relais de la CAF sur ses réseaux : proposition conditionnelle, pas une action actée",
            "M. Diallo n'a assisté qu'à la première heure",
        ],
        "provenance": [{"source": "Notes fictives rédigées pour l'évaluation (collectivité, personnes et chiffres imaginaires)", "consulte_le": CONSULTATION}],
        "licence_source": LIC_CREATION,
    }


def cr_002() -> dict:
    return {
        "id": "CR-002", "tache": "Compte rendu", "difficulte": "difficile",
        "entree": {"consigne": "Rédige le compte rendu de cette commission : participants, points abordés, décisions, actions (responsable, échéance).",
                   "notes": CR2_NOTES, "nb_mots": words(CR2_NOTES)},
        "participants_reference": ["J.-P. Morel (adjoint aux travaux, président)", "C. Benoît", "A. Haddad", "L. Fontaine (secrétaire de séance)",
                                   "N. Vidal (opposition)", "S. Marchal (DST)", "M. Royer (association Vivre à Belcourt, point 3 seulement)",
                                   "Excusé : F. Leclerc (sans pouvoir)"],
        "decisions_reference": [
            "Avis favorable à l'attribution de la réfection de la toiture de l'école Jules-Ferry à Bati Ouest (51 200 € HT, 6 semaines) : 5 pour, 1 abstention (N. Vidal). Il s'agit d'un AVIS ; l'attribution sera votée au conseil municipal du 22 octobre 2026",
            "Expérimentation d'extinction de l'éclairage public de 23 h à 5 h, pendant 6 mois, au seul lotissement des Tilleuls, avec bilan en commission (unanimité)",
            "Pose de 2 arceaux vélo supplémentaires (10 places) place du Marché, en régie, sur le budget de fonctionnement voirie, avant fin novembre (unanimité)",
        ],
        "actions_reference": [
            {"action": "Envoyer le rapport d'analyse des offres à tous les membres", "responsable": "S. Marchal", "echeance": "avant le vendredi 9 octobre 2026"},
            {"action": "Inscrire l'attribution du marché toiture au conseil municipal", "responsable": "non précisé", "echeance": "conseil municipal du 22 octobre 2026"},
            {"action": "Demander au SIEV une date de reprogrammation des horloges", "responsable": "S. Marchal", "echeance": "non fixée"},
            {"action": "Consulter la gendarmerie sur l'extinction nocturne", "responsable": "C. Benoît", "echeance": "avant fin octobre 2026"},
            {"action": "Poser les 2 arceaux vélo", "responsable": "services techniques (régie)", "echeance": "avant fin novembre 2026"},
            {"action": "Chiffrer les deux options de bancs (2 ou 4)", "responsable": "S. Marchal", "echeance": "prochaine commission, mardi 17 novembre 2026"},
            {"action": "Vérifier le reliquat du budget voirie 2026 pour le trottoir rue des Lavandières et revenir vers J.-P. Morel", "responsable": "S. Marchal", "echeance": "non fixée"},
            {"action": "Confirmer le motif d'éviction de la 3e offre (Toitures du Val)", "responsable": "S. Marchal", "echeance": "non fixée"},
        ],
        "pieges": [
            "L'attribution du marché n'est PAS décidée par la commission (avis seulement)",
            "Couverture Delmas, moins-disante, n'est pas retenue",
            "Extinction dans tous les lotissements (proposition initiale) : NON retenue, seulement les Tilleuls",
            "Extinction à partir de minuit : proposée par L. Fontaine, NON retenue",
            "Réunion publique avec les habitants des Tilleuls : évoquée, aucun responsable, non décidée",
            "Passage de tout le parc en LED (environ 380 k€) : renvoyé au débat budgétaire, rien décidé",
            "Nombre de bancs (2 ou 4) : non décidé",
            "Végétalisation de la place : renvoyée au projet 2027-2028 ; l'étude n'est pas lancée, aucune date ne doit apparaître",
            "Réfection définitive du trottoir rue des Lavandières : ni décidée ni datée",
            "Chemin de la Garenne : compétence à vérifier, rien décidé",
            "Panneau d'affichage de l'école : commande déjà en cours, pas une décision de la séance",
            "F. Leclerc n'a pas donné de pouvoir",
            "Le conseil municipal a lieu le 22 octobre, pas le 20 (erratum)",
        ],
        "provenance": [{"source": "Notes fictives rédigées pour l'évaluation (commune, personnes, entreprises et montants imaginaires)", "consulte_le": CONSULTATION}],
        "licence_source": LIC_CREATION,
    }


# ---------------------------------------------------------------------------
# Tâche 5 : Correction
# ---------------------------------------------------------------------------
CO1_CORRECT = """Madame, Monsieur,

Nous vous informons que la médiathèque municipale sera fermée du lundi 2 novembre au samedi 7 novembre 2026 inclus, afin de permettre la réalisation de travaux de mise en accessibilité. Pendant cette période, les documents empruntés pourront être déposés dans la boîte de retour située à l'entrée du bâtiment. Aucune pénalité de retard ne sera appliquée aux usagers concernés.

Durant la fermeture, l'espace numérique de l'hôtel de ville, au rez-de-chaussée, accueillera les personnes qui souhaitent consulter la presse ou accéder à internet, aux horaires habituels d'ouverture de la mairie.

Les réservations effectuées avant la fermeture seront conservées et mises à votre disposition dès la réouverture, le mardi 10 novembre à 10 heures. Les agents de la médiathèque restent joignables par courriel pour toute question relative à votre abonnement ou à vos prêts en cours.

Nous vous remercions de votre compréhension et vous prions d'agréer, Madame, Monsieur, l'expression de nos salutations distinguées.

La direction de la médiathèque"""

CO1_FAUTES = [
    ("sera fermée du lundi", "fermée", "fermé", "accord du participe passé"),
    ("réalisation de travaux de mise", "travaux", "travaus", "orthographe lexicale"),
    ("les documents empruntés", "empruntés", "emprunter", "confusion é/er"),
    ("pourront être déposés", "pourront", "pourrons", "conjugaison"),
    ("la boîte de retour située", "située", "situé", "accord du participe passé"),
    ("Aucune pénalité de retard", "pénalité", "pénalitée", "orthographe lexicale"),
    ("Les réservations effectuées avant", "effectuées", "effectués", "accord du participe passé"),
    ("disposition dès la réouverture", "dès", "des", "accent / homophone"),
]

CO2_CORRECT = """Objet : organisation des permanences d'accueil pendant les congés de fin d'année

Comme chaque année, les permanences d'accueil seront assurées par roulement entre le 21 décembre 2026 et le 1er janvier 2027. Les agents qui se sont portés volontaires lors de la réunion du 6 octobre recevront leur planning définitif au plus tard le 20 novembre. Quelles que soient les contraintes de chacun, il est indispensable que l'accueil soit ouvert tous les jours ouvrés de 9 heures à 12 heures.

Les demandes de congés que vous avez déposées avant le 15 octobre seront examinées en priorité. Au-delà de cette date, elles ne pourront être acceptées que si la continuité du service est garantie. Bien que le nombre de volontaires soit encore insuffisant, nous avons choisi de ne pas imposer de permanence aux agents à temps partiel.

Les responsables d'équipe veilleront à ce que leurs collaborateurs disposent des consignes nécessaires. Une fiche récapitulative, que nous vous avons transmise par courriel, précise les numéros d'astreinte et la conduite à tenir en cas d'incident. Nous vous remercions de bien vouloir la conserver et la consulter avant chaque permanence.

Pour toute question, vous pouvez vous adresser au secrétariat de la direction des ressources humaines."""

CO2_FAUTES = [
    ("qui se sont portés volontaires", "portés", "porté", "accord du participe passé (être)"),
    ("6 octobre recevront leur", "recevront", "recevrons", "conjugaison"),
    ("Quelles que soient les contraintes", "Quelles que soient", "Quelque soient", "quel que / quelque"),
    ("que l'accueil soit ouvert", "soit", "est", "subjonctif après « il est indispensable que »"),
    ("les jours ouvrés de", "ouvrés", "ouvrées", "accord de l'adjectif"),
    ("que vous avez déposées avant", "déposées", "déposé", "accord du participe passé (avoir, COD antéposé)"),
    ("seront examinées en priorité", "examinées", "examinés", "accord du participe passé"),
    ("Au-delà de cette date", "Au-delà", "Au delà", "trait d'union"),
    ("volontaires soit encore", "soit", "est", "subjonctif après « bien que »"),
    ("à ce que leurs collaborateurs", "leurs", "leur", "accord de « leur »"),
    ("nous vous avons transmise par", "transmise", "transmis", "accord du participe passé (avoir, COD antéposé)"),
    ("la conduite à tenir", "à", "a", "homophone a/à"),
]


def correction_items() -> list[dict]:
    out = []
    for iid, diff, correct, fautes, contexte in [
        ("CO-001", "facile", CO1_CORRECT, CO1_FAUTES, "Avis aux usagers d'une médiathèque municipale (texte fictif)"),
        ("CO-002", "difficile", CO2_CORRECT, CO2_FAUTES, "Note interne de service sur les permanences de fin d'année (texte fictif)"),
    ]:
        faulty, positions = inject(correct, fautes)
        assert 150 <= words(correct) <= 250, (iid, words(correct))
        assert 8 <= len(positions) <= 12
        out.append({
            "id": iid, "tache": "Correction", "difficulte": diff,
            "entree": {"consigne": "Corrige l'orthographe, la grammaire et la typographie de ce texte. Ne modifie rien d'autre.",
                       "texte": faulty, "nb_mots": words(faulty)},
            "fautes": positions,
            "nb_fautes": len(positions),
            "texte_corrige_reference": correct,
            "note_positions": "debut/fin = indices de caractères (Python, 0-indexé, fin exclue) dans entree.texte",
            "provenance": [{"source": contexte, "consulte_le": CONSULTATION}],
            "licence_source": LIC_CREATION,
        })
    return out


# ---------------------------------------------------------------------------
# Sortie Markdown lisible
# ---------------------------------------------------------------------------
def trunc(text: str, n: int = 15) -> str:
    lines = text.splitlines() or [""]
    wrapped: list[str] = []
    for ln in lines:
        while len(ln) > 160:
            cut = ln.rfind(" ", 0, 160)
            cut = cut if cut > 0 else 160
            wrapped.append(ln[:cut]); ln = ln[cut:].lstrip()
        wrapped.append(ln)
    if len(wrapped) <= n:
        return "\n".join(wrapped)
    return "\n".join(wrapped[:n]) + f"\n[… tronqué : {len(wrapped) - n} lignes de plus, texte complet dans le JSONL]"


def quote(text: str) -> str:
    return "\n".join("> " + ln if ln else ">" for ln in text.splitlines())


def md_value(v, indent=0) -> str:
    pad = "  " * indent
    if isinstance(v, list):
        def inline(x):
            if isinstance(x, dict):
                return " ; ".join(f"**{k}** : {inline(y)}" for k, y in x.items())
            if isinstance(x, list):
                return ", ".join(inline(y) for y in x)
            return str(x)
        return "\n".join(f"{pad}- {inline(x)}" for x in v)
    if isinstance(v, dict):
        return "\n".join(f"{pad}- **{k}** : " + (("\n" + md_value(x, indent + 1)) if isinstance(x, (dict, list)) else str(x)) for k, x in v.items())
    return f"{pad}{v}"


def to_markdown(items: list[dict], sha: str) -> str:
    out = ["# Échantillon de calibrage du Jeu d'évaluation maison", "",
           f"16 items (2 par Tâche). Construit le {CONSULTATION} par `build_calibrage.py`. "
           f"Empreinte SHA-256 du JSONL : `{sha}`.", "",
           "Usage : évaluation uniquement, jamais d'entraînement. Les textes longs sont tronqués à 15 lignes ; "
           "le JSONL fait foi.", "", "| id | Tâche | difficulté | sujet |", "|---|---|---|---|"]
    for it in items:
        out.append(f"| {it['id']} | {it['tache']} | {it['difficulte']} | {sujet(it)} |")
    skip = {"id", "tache", "difficulte", "entree", "provenance", "licence_source"}
    for it in items:
        out += ["", "---", "", f"## {it['id']} · {it['tache']} · {it['difficulte']}", "", "### Entrée", ""]
        e = it["entree"]
        if isinstance(e, str):
            out.append(quote(e))
        else:
            for k, v in e.items():
                if isinstance(v, str) and ("\n" in v or len(v) > 300):
                    out += ["", f"**{k}** :", "", "```text", trunc(v), "```", ""]
                else:
                    out.append(f"- **{k}** : " + (("\n" + md_value(v, 1)) if isinstance(v, (dict, list)) else str(v)))
        if "amorce_usager" in it:
            out += ["", f"*Amorce usager (AgentPublic) :* « {it['amorce_usager']} »"]
        out += ["", "### Référence", ""]
        for k, v in it.items():
            if k in skip or k == "amorce_usager":
                continue
            if k == "fautes":
                out += ["**fautes** :", "", "| # | position | erreur | correction | type |", "|---|---|---|---|---|"]
                out += [f"| {i+1} | {f['debut']}-{f['fin']} | {f['erreur']} | {f['correction']} | {f['type']} |" for i, f in enumerate(v)]
                continue
            if isinstance(v, str) and ("\n" in v or len(v) > 400):
                out += ["", f"**{k}** :", "", "```text", trunc(v), "```", ""]
            elif isinstance(v, (dict, list)):
                out += [f"**{k}** :", "", md_value(v), ""]
            else:
                out.append(f"- **{k}** : {v}")
        out += ["", "### Provenance", "", md_value(it["provenance"]), "", f"**Licence** : {it['licence_source']}"]
    return "\n".join(out) + "\n"


def sujet(it: dict) -> str:
    return {
        "Q-001": "Carte d'identité perdue : gratuité et démarche",
        "Q-002": "Sigle « PPG » : question sans source officielle",
        "R-001": "Jeux de données sur les défibrillateurs (Géo'DAE)",
        "R-002": "Nombre de DAE à Lorient via l'API tabulaire",
        "CR-001": "COPIL France services itinérant (intercommunalité)",
        "CR-002": "Commission travaux municipale, notes en désordre",
        "LC-001": "Forfait post-stationnement : délai et majoration",
        "LC-002": "CRPA : accusé de réception (L. 112-3, R. 112-5, L. 112-6)",
        "CO-001": "Avis de fermeture de médiathèque, 8 fautes",
        "CO-002": "Note interne permanences, 12 fautes",
        "RS-001": "Allocation de rentrée scolaire 2026 (résumé court)",
        "RS-002": "Ombrières des parkings de plus de 1 500 m² (résumé moyen)",
        "CT-001": "Demande de pièces, inscription périscolaire",
        "CT-002": "Accusé de réception d'une demande d'occupation du domaine public",
        "NR-001": "Calcul d'horaire",
        "NR-002": "Reformulation en registre soutenu",
    }[it["id"]]


# ---------------------------------------------------------------------------
# Sous-commandes facultatives : téléchargement et enregistrement des cassettes
# ---------------------------------------------------------------------------
def cmd_fetch(src: Path) -> None:
    """Retélécharge les sources (nécessite `--with duckdb --with openpyxl`)."""
    import urllib.request
    import duckdb
    hf = src / "hf"; hf.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(QUESTIONS_XLSX, hf / "assistant_ia_questions.xlsx")
    con = duckdb.connect(); con.execute("INSTALL httpfs; LOAD httpfs; SET threads=4;")
    cols = ("chunk_id,doc_id,chunk_index,audience,theme,title,surtitle,source,introduction,url,"
            "related_questions,context,text,chunk_text")
    cur = con.execute(f"SELECT {cols} FROM read_parquet('{SP_PARQUET}') WHERE doc_id IN "
                      f"({','.join('?' * len(SP_FICHES))}) ORDER BY doc_id, chunk_index", SP_FICHES)
    names = [d[0] for d in cur.description]; rows = [dict(zip(names, r)) for r in cur.fetchall()]
    for i in SP_FICHES:
        json.dump({"source": "hf://datasets/AgentPublic/service-public (latest)", "licence": "etalab-2.0",
                   "fetched": dt.date.today().isoformat(), "doc_id": i, "rows": [r for r in rows if r["doc_id"] == i]},
                  open(hf / f"sp_{i}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    files = json.loads(urllib.request.urlopen(LEGI_PARQUET_LIST).read())
    cur = con.execute(f"SELECT doc_id, number, title, full_title, status, start_date, end_date, chunk_index, text "
                      f"FROM read_parquet({files!r}) WHERE title LIKE 'Code des relations entre le public%' "
                      f"AND status='VIGUEUR' AND number IN ({','.join('?' * len(LEGI_ARTICLES))})", LEGI_ARTICLES)
    names = [d[0] for d in cur.description]
    json.dump({"source": "hf://datasets/AgentPublic/legi (latest)", "licence": "etalab-2.0",
               "fetched": dt.date.today().isoformat(), "rows": [dict(zip(names, r)) for r in cur.fetchall()]},
              open(hf / "legi_crpa.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    pats = ["politiques? prioritaires? du gouvernement", r"\bPPG\b", "baromètre de l.action publique", "journée de solidarité"]
    res = {p: [list(r) for r in con.execute(f"SELECT doc_id,title,url FROM read_parquet('{SP_PARQUET}') "
                                             f"WHERE regexp_matches(text, ?, 'i') GROUP BY ALL", [p]).fetchall()] for p in pats}
    json.dump({"corpus": SP_PARQUET, "checked": dt.date.today().isoformat(), "matches": res},
              open(hf / "absence_ppg.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def _mcp_session(calls: list) -> dict:
    import urllib.request

    def post(payload, sid=None):
        h = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream",
             "MCP-Protocol-Version": "2025-06-18"}
        if sid:
            h["Mcp-Session-Id"] = sid
        req = urllib.request.Request(MCP_URL, data=json.dumps(payload).encode(), headers=h, method="POST")
        with urllib.request.urlopen(req, timeout=90) as r:
            body = r.read().decode("utf-8"); ct = r.headers.get("Content-Type", ""); s = r.headers.get("Mcp-Session-Id")
        if "event-stream" in ct:
            msgs = [json.loads(l[5:].strip()) for l in body.splitlines() if l.startswith("data:") and l[5:].strip()]
            return (msgs[-1] if msgs else None), s
        return (json.loads(body) if body.strip() else None), s

    init, sid = post({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                      "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                                 "clientInfo": {"name": "calibrage-recorder", "version": "0.1"}}})
    post({"jsonrpc": "2.0", "method": "notifications/initialized"}, sid)
    cass = {"server": MCP_URL, "recorded_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            "initialize": init, "interactions": []}
    for i, c in enumerate(calls, start=2):
        req = ({"jsonrpc": "2.0", "id": i, "method": "tools/list", "params": {}} if c == "tools/list" else
               {"jsonrpc": "2.0", "id": i, "method": "tools/call", "params": {"name": c[0], "arguments": c[1]}})
        cass["interactions"].append({"request": req, "response": post(req, sid)[0]})
    return cass


def cmd_record(out: Path) -> None:
    sessions = {
        "tools-list": ["tools/list"],
        "R-001": [["search_datasets", {"query": "défibrillateurs", "page_size": 5}],
                  ["get_dataset_info", {"dataset_id": GEODAE_DATASET}]],
        "R-002": [["search_datasets", {"query": "défibrillateurs", "page_size": 5}],
                  ["list_dataset_resources", {"dataset_id": GEODAE_DATASET}],
                  ["query_resource_data", {"resource_id": GEODAE_CSV, "filter_column": "c_com_insee",
                                           "filter_value": "56121", "filter_operator": "exact", "page_size": 5}]],
    }
    (out / "cassettes").mkdir(parents=True, exist_ok=True)
    for name, calls in sessions.items():
        json.dump(_mcp_session(calls), open(out / "cassettes" / f"{name}.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="build", choices=["build", "fetch", "record"])
    ap.add_argument("--sources", type=Path, default=Path("data/raw/eval-sources"))
    ap.add_argument("--out", type=Path, default=Path("eval/calibrage"))
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    if a.cmd == "fetch":
        cmd_fetch(a.sources); return
    if a.cmd == "record":
        cmd_record(a.out); return
    items = build_items(a.sources, a.out / "cassettes")
    assert len(items) == 16 and len({i["id"] for i in items}) == 16
    for t in {i["tache"] for i in items}:
        diffs = [i["difficulte"] for i in items if i["tache"] == t]
        assert len(diffs) == 2 and "facile" in diffs and diffs != ["facile", "facile"], t
    jsonl = "".join(json.dumps(i, ensure_ascii=False) + "\n" for i in items)
    (a.out / "echantillon-calibrage.jsonl").write_text(jsonl, encoding="utf-8", newline="\n")
    sha = hashlib.sha256(jsonl.encode("utf-8")).hexdigest()
    (a.out / "echantillon-calibrage.md").write_text(to_markdown(items, sha), encoding="utf-8", newline="\n")
    for i in items:
        e = i["entree"]
        n = e.get("nb_mots") if isinstance(e, dict) else words(e)
        print(f"{i['id']:7} {i['tache']:22} {i['difficulte']:9} {n} mots")
    print("sha256", sha)


if __name__ == "__main__":
    main()
