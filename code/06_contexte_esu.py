"""Contexte ESU daté, sans modification des effectifs ni des affectations simulées.

Source : rapport DGESS de février 2026, annexes 1, 2 et 4 (PDF p. 15–20).
Lecture du CSV texte du Data Pack ; contrôles des totaux ; passage 47 → 45 provinces.
Une ligne absente reste inconnue. Une ancienne province scindée n'a une valeur
que si toutes ses composantes sont renseignées pour l'indicateur considéré.

Lancer depuis DataChallenge : python code/06_contexte_esu.py
"""
from pathlib import Path
import csv
import json
import re
import unicodedata

import pandas as pd

EQUIPE = "EXX"
RACINE = Path(__file__).resolve().parent.parent
DOCUMENT = "Rapport_statistique_mensuel_ESU_Février_2026.pdf"
DOSSIER_PACK = RACINE / "01_collecte/datapack_extrait/DataPack_DCB_2026"
F_SOURCE = DOSSIER_PACK / "data/01_Education_MENAPLN_DGESS/ESU_Rapports_mensuels" / DOCUMENT.replace(".pdf", ".csv")
F_GEOJSON = RACINE / "01_collecte/limites_administratives/bfa_admin2.geojson"
DATE = "2026-02-28"
ANNEXES = {1: "ecoles_rouvertes", 2: "ecoles_delocalisees", 4: "eleves_deplaces"}
METADATA = {
    "date_observation": DATE,
    "annee_scolaire_esu": "2025-2026",
    "niveau_enseignement": "primaire",
    "statut_etablissement": "non distingue dans le tableau",
    "sexe": "ensemble",
    "source_document": DOCUMENT,
    "producteur": "DGESS / MEBAPLN",
    "methode_extraction": "texte du PDF extrait dans le Data Pack",
    "verification": "controles automatiques ; audit PDF separe par le script 08 ; conditions de terrain non certifiees",
}
LIMITES = (
    "Contexte au 28 février 2026 (année scolaire 2025–2026), distinct du diagnostic public 2024–2025. "
    "Le statut public/privé n'est pas distingué dans ces tableaux. Les écoles rouvertes sont celles "
    "rouvertes depuis le début de la crise et restant fonctionnelles à la date du rapport ; "
    "ce n'est ni le flux mensuel des réouvertures, ni un nombre d'écoles fermées. "
    "Les EDI sont les inscriptions/réinscriptions d'élèves déplacés recensées par le rapport ; "
    "aucun taux rapporté aux élèves de l'annuaire ni ajout aux effectifs n'est calculé. "
    "Une absence de ligne reste non renseignée ; une province partiellement couverte garde une valeur vide. "
    "Ces indicateurs ne mesurent pas l'accessibilité et ne déterminent aucune exclusion automatique."
)


def normaliser(texte):
    texte = unicodedata.normalize("NFD", texte.upper())
    return " ".join("".join(c for c in texte if unicodedata.category(c) != "Mn").replace("-", " ").split())


def charger_referentiel():
    """Correspondances du COD-AB, avec deux variantes d'orthographe explicites."""
    carte = json.loads(F_GEOJSON.read_text(encoding="utf-8"))
    anciens = {"BALE": "LES BALE", "KOMANDJARI": "KOMONDJARI"}
    ref = {}
    for entite in carte["features"]:
        p = entite["properties"]
        nom = normaliser(p["adm2_name"])
        if nom in ref:
            raise ValueError(f"Province en double dans le référentiel : {nom}")
        ref[nom] = {"code": p["adm2_pcode"], "province": p["adm2_name"],
                    "region": p["adm1_name"],
                    "province_annuaire": anciens.get(normaliser(p["adm2_name_old"]), normaliser(p["adm2_name_old"]))}
    # KOOSIN et KOMONDJARI sont les libellés du PDF, Kossin et Komandjari ceux du COD-AB.
    for variante, canonique in {"KOOSIN": "KOSSIN", "KOMONDJARI": "KOMANDJARI"}.items():
        ref[variante] = ref[canonique]
    return ref


def extraire_annexes(lignes, referentiel):
    """Lit les blocs d'annexes ; échoue sur doublon, nombre invalide ou nom inconnu."""
    observations, totaux, brutes, vus = [], [], [], set()
    annexe = None
    for ligne in lignes:
        cellules = [str(ligne.get(f"c{i}", "") or "").strip() for i in range(1, int(ligne["nb_cellules"]) + 1)]
        if not cellules:
            continue
        titre = re.match(r"Annexe\s+(\d+)\s*:", cellules[0], flags=re.I)
        if titre:
            annexe = int(titre.group(1))
        if annexe not in ANNEXES:
            continue
        brutes.append({k: v for k, v in ligne.items() if k in {"document", "page", "ligne", "nb_cellules"} or re.fullmatch(r"c\d+", k)})
        nb_valeurs = 3 if annexe == 4 else 4
        # Titres, en-têtes et noms de région seuls ne sont pas des observations.
        if cellules[0] == "REGION":
            continue
        if len(cellules) not in (nb_valeurs + 1, nb_valeurs + 2):
            provinciale = any(normaliser(c) in referentiel for c in cellules[:2])
            total = normaliser(cellules[0]).startswith("TOTAL ")
            if len(cellules) > 1 and (provinciale or total):
                raise ValueError(f"Largeur inattendue d'une ligne de données, page {ligne['page']}, ligne {ligne['ligne']} : {cellules}")
            continue
        libelle = cellules[-nb_valeurs-1]
        chiffres = cellules[-nb_valeurs:]
        if not all(re.fullmatch(r"\d[\d\s]*", n) for n in chiffres):
            raise ValueError(f"Nombre illisible à la page {ligne['page']}, ligne {ligne['ligne']} : {cellules}")
        nombres = [int("".join(n.split())) for n in chiffres]
        if sum(nombres[:-1]) != nombres[-1]:
            raise ValueError(f"Composantes différentes du total : {libelle}, annexe {annexe}")
        indicateur = ANNEXES[annexe]
        provenance = {"indicateur": indicateur, "annexe": annexe, "source_page": str(ligne["page"]),
                      "source_ligne": str(ligne["ligne"]), "composantes": nombres,
                      "valeur": nombres[-1] if annexe == 4 else nombres[2]}
        if normaliser(libelle).startswith("TOTAL "):
            totaux.append({**provenance, "territoire": normaliser(libelle)[6:]})
            continue
        nom = normaliser(libelle)
        if nom not in referentiel:
            raise ValueError(f"Province ESU sans correspondance : {libelle}")
        meta = referentiel[nom]
        cle = (meta["code"], indicateur)
        if cle in vus:
            raise ValueError(f"Observation ESU dupliquée : {cle}")
        vus.add(cle)
        observations.append({**meta, **provenance, "libelle_province_source": libelle})
    return observations, totaux, brutes


def construire_contexte(observations, referentiel):
    """Complète le référentiel et agrège uniquement les ensembles entièrement connus."""
    uniques = {r["code"]: r for r in referentiel.values()}
    index = {(r["code"], r["indicateur"]): r for r in observations}
    natif = []
    for code, province in sorted(uniques.items()):
        for annexe, indicateur in ANNEXES.items():
            obs = index.get((code, indicateur))
            natif.append({**METADATA, "code_province_esu": code, "province_esu": province["province"],
                          "region_esu": province["region"], "province_annuaire": province["province_annuaire"],
                          "indicateur": indicateur, "unite": "eleves" if annexe == 4 else "ecoles",
                          "valeur": obs["valeur"] if obs else None,
                          "statut_renseignement": "renseigne" if obs else "non_renseigne",
                          "source_annexe": annexe, "source_page": obs["source_page"] if obs else "",
                          "source_ligne": obs["source_ligne"] if obs else "",
                          "libelle_province_source": obs["libelle_province_source"] if obs else ""})
    anciens = []
    for province in sorted({p["province_annuaire"] for p in uniques.values()}):
        for annexe, indicateur in ANNEXES.items():
            groupe = [r for r in natif if r["province_annuaire"] == province and r["indicateur"] == indicateur]
            connus = [r for r in groupe if r["valeur"] is not None]
            complet = len(connus) == len(groupe)
            anciens.append({**METADATA, "province_annuaire": province, "indicateur": indicateur,
                            "unite": "eleves" if annexe == 4 else "ecoles",
                            "valeur": sum(r["valeur"] for r in connus) if complet else None,
                            "statut_renseignement": "renseigne" if complet else ("partiel" if connus else "non_renseigne"),
                            "codes_provinces_attendus": " | ".join(r["code_province_esu"] for r in groupe),
                            "codes_provinces_renseignes": " | ".join(r["code_province_esu"] for r in connus),
                            "source_annexe": annexe,
                            "source_page": " | ".join(sorted({r["source_page"] for r in connus}, key=int)),
                            "source_ligne": " | ".join(f"p{r['source_page']}:l{r['source_ligne']}" for r in connus)})
    return natif, anciens


def controler_totaux(observations, totaux):
    """Compare toutes les composantes aux totaux régionaux et nationaux du PDF."""
    controles, vus = [], set()
    for total in totaux:
        indicateur, territoire = total["indicateur"], total["territoire"]
        cle = (indicateur, territoire)
        if cle in vus:
            raise ValueError(f"Total dupliqué : {cle}")
        vus.add(cle)
        groupe = [r for r in observations if r["indicateur"] == indicateur and
                  (territoire == "GENERAL" or normaliser(r["region"]) == territoire)]
        obtenu = [sum(r["composantes"][i] for r in groupe) for i in range(len(total["composantes"]))]
        conforme = bool(groupe) and obtenu == total["composantes"]
        controles.append({"indicateur": indicateur, "territoire": territoire,
                          "attendu": str(total["composantes"]), "obtenu": str(obtenu),
                          "conforme": conforme, "source_page": total["source_page"]})
    if not all((i, "GENERAL") in vus for i in ANNEXES.values()):
        raise ValueError("Il manque un total national pour une des trois annexes ESU")
    return pd.DataFrame(controles)


def enregistrer_csv(lignes, dossier, nom):
    dossier.mkdir(exist_ok=True)
    table = pd.DataFrame(lignes)
    if "valeur" in table:
        table["valeur"] = table["valeur"].astype("Int64")
    table.to_csv(dossier / nom, index=False, encoding="utf-8-sig")
    return table


def main():
    ref = charger_referentiel()
    with F_SOURCE.open(encoding="utf-8-sig", newline="") as f:
        lignes = list(csv.DictReader(f, delimiter=";"))
    obs, totaux, brutes = extraire_annexes(lignes, ref)
    controles = controler_totaux(obs, totaux)
    net, trans, sortie = (RACINE / d for d in ["02_nettoyage", "03_transformation", "05_interpretation"])
    prefixe = f"{EQUIPE}_02-nettoyage_D3_engineer_"
    enregistrer_csv(controles, net, f"{prefixe}controles-esu_v1.csv")
    if not controles["conforme"].all():
        raise ValueError("Au moins un total ESU est non conforme ; voir controles-esu_v1.csv")
    natif, anciens = construire_contexte(obs, ref)
    if len(natif) != 47 * 3 or len(anciens) != 45 * 3:
        raise ValueError("Le référentiel doit couvrir 47 nouvelles et 45 anciennes provinces")
    enregistrer_csv(brutes, RACINE / "01_collecte", f"{EQUIPE}_01-collecte_D3_engineer_esu-annexes-lignes-brutes_v1.csv")
    enregistrer_csv(natif, net, f"{prefixe}esu-primaire-provinces-2026_v1.csv")
    contexte = enregistrer_csv(anciens, trans, f"{EQUIPE}_03-transformation_D3_architect_contexte-esu-provinces_v1.csv")

    # Une table de lecture côte à côte ; aucun effectif ni calcul de répartition n'est modifié.
    detail = pd.read_csv(RACINE / "04_analyse" / f"{EQUIPE}_04-analyse_D3_scientist_repartition-detail-provinces_v1.csv")
    ind = pd.read_csv(trans / f"{EQUIPE}_03-transformation_D3_architect_indicateurs-provinces-public_v1.csv")
    annee = ind["annee_scolaire"].max()
    if set(detail.province) != set(contexte.province_annuaire) or detail.province.duplicated().any():
        raise ValueError("La jointure ESU-affectations ne couvre pas exactement les 45 provinces")
    for indicateur in ANNEXES.values():
        part = contexte[contexte.indicateur == indicateur].set_index("province_annuaire")
        detail[f"esu_{indicateur}"] = detail.province.map(part.valeur).astype("Int64")
        detail[f"esu_{indicateur}_statut"] = detail.province.map(part.statut_renseignement)
        detail[f"esu_{indicateur}_pages"] = detail.province.map(part.source_page)
    detail["annee_scolaire_diagnostic"] = annee
    detail["date_observation_esu"] = DATE
    detail["statut_etablissement_esu"] = METADATA["statut_etablissement"]
    detail["source_esu"] = DOCUMENT
    detail["accessibilite_operationnelle"] = "non etablie par les sources exploitees"
    enregistrer_csv(detail, sortie, f"{EQUIPE}_05-interpretation_D3_analyst_contexte-esu-affectations_v1.csv")

    loroum = detail.set_index("province").loc["LOROUM"]
    edi_loroum = f"{int(loroum.esu_eleves_deplaces):,}".replace(",", " ")
    coverage = contexte.groupby(["indicateur", "statut_renseignement"]).size().unstack(fill_value=0)
    note = ["# Contexte ESU provincial — situation au 28 février 2026\n", LIMITES,
            "\n## Loroum : un contexte distinct du diagnostic\n",
            f"Le rapport ESU renseigne {edi_loroum} élèves déplacés du primaire, "
            f"{int(loroum.esu_ecoles_rouvertes)} écoles primaires rouvertes restant fonctionnelles et "
            f"{int(loroum.esu_ecoles_delocalisees)} écoles primaires délocalisées. " +
            "Ces valeurs ne sont pas un nombre d'écoles fermées. Elles ne sont ni ajoutées ni soustraites aux inscriptions de l'annuaire.",
            "\n## Couverture des 45 anciennes provinces\n",
            "| Indicateur | Renseigné | Partiel | Non renseigné |\n|---|---|---|---|",
            *[f"| {i} | {int(r.get('renseigne', 0))} | {int(r.get('partiel', 0))} | {int(r.get('non_renseigne', 0))} |" for i, r in coverage.iterrows()],
            "\nPour Soum et Tapoa, la valeur est la somme des deux nouvelles provinces uniquement si elles sont toutes deux renseignées. "
            "Une somme partielle n'est jamais publiée comme un total.\n",
            f"Contrôles : {len(controles)} rapprochements de totaux régionaux et nationaux conformes, "
            "en plus des égalités de composantes contrôlées à chaque ligne. Les totaux ne prouvent pas l'exactitude de chaque cellule.",
            "\nSource : DGESS/MEBAPLN, rapport statistique mensuel ESU de février 2026 (publié en mars 2026), "
            "annexes 1, 2 et 4, pages physiques PDF 15–20. Une observation conserve document, annexe, page et ligne du CSV source.",
            "\nVérification visuelle effectuée par Codex sur le PDF : p. 16 (Loroum : 40 écoles rouvertes et 10 délocalisées), "
            "p. 19 (Loroum : 6 228 garçons + 6 112 filles = 12 340 EDI ; Soum : 5 491 + 1 044 = 6 535 ; "
            "Tapoa : 2 367 + 5 035 = 7 402). L'audit documentaire exhaustif est reproductible avec "
            "`code/08_verifier_pdf_esu.py` ; voir `documentation/VERIFICATION_SOURCES_ET_ACCESSIBILITE.md` pour son résultat et sa portée."]
    (sortie / f"{EQUIPE}_05-interpretation_D3_analyst_note-contexte-esu_v1.md").write_text("\n".join(note) + "\n", encoding="utf-8")
    journal = ["# Préparation ESU — février 2026\n", "Produit par `code/06_contexte_esu.py`.\n", LIMITES,
               "\n## Traitements\n",
               "- Annexes 1, 2 et 4 uniquement ; les tableaux préscolaire et CEBNF ne deviennent pas des indicateurs primaires.",
               "- La colonne de remarques n'est pas reprise comme variable statistique ; les sources sont conservées sans modification.",
               "- En-têtes et titres ignorés ; composantes des lignes vérifiées contre le total ; noms inconnus, doublons et nombres illisibles bloquants.",
               "- Jointure sur les codes du COD-AB après normalisation des noms et variantes KOOSIN/Kossin, KOMONDJARI/Komandjari.",
               "- Anciennes provinces : Balé → LES BALE, Komandjari → KOMONDJARI ; regroupement des composantes de Soum et Tapoa.",
               "- Une absence reste une cellule vide, avec un statut explicite ; le zéro est réservé aux lignes explicitement nulles.",
               "- Aucun taux EDI/effectif, aucune correction des effectifs, aucune exclusion de province dans la simulation.\n",
               f"Observations explicites : {len(obs)}. Table native : {len(natif)} lignes. Table des anciennes provinces : {len(anciens)} lignes.",
               f"Totaux régionaux et nationaux : {len(controles)} conformes. Voir le CSV de contrôles et la note ESU pour les vérifications visuelles."]
    (net / f"{prefixe}journal-nettoyage-esu_v1.md").write_text("\n".join(journal) + "\n", encoding="utf-8")
    print(f"ESU : {len(obs)} observations explicites ; {len(controles)} totaux conformes ; jointure 47 → 45 provinces.")
    print(coverage.to_string())
    print("Loroum :", {i: int(loroum[f'esu_{i}']) for i in ANNEXES.values()}, "; affectations inchangées.")


if __name__ == "__main__":
    main()
