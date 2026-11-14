"""Audit structurel du pack : fichiers, catalogue, empreintes, CSV, OSM et jointures.

Aucune donnée du modèle n'est modifiée. Résultats dans documentation/audit_sources/.
Ce contrôle structurel ne valide pas toutes les valeurs des publications.
Lancer depuis DataChallenge : python code/09_audit_sources.py
"""
from pathlib import Path
import collections
import csv
import datetime
import hashlib
import json
import math
import re

import openpyxl

RACINE = Path(__file__).resolve().parent.parent
PACK = RACINE / "01_collecte/datapack_extrait/DataPack_DCB_2026"
SORTIE = RACINE / "documentation/audit_sources"
csv.field_size_limit(20_000_000)


def ecrire_csv(nom, lignes):
    if not lignes:
        return
    with (SORTIE / nom).open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(lignes[0]))
        writer.writeheader()
        writer.writerows(lignes)


def empreinte(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for bloc in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(bloc)
    return h.hexdigest()


def main():
    SORTIE.mkdir(parents=True, exist_ok=True)
    fichiers = sorted(p for p in PACK.rglob("*") if p.is_file() and p.name != ".DS_Store")
    inventaire = [{"chemin": str(p.relative_to(PACK)), "octets": p.stat().st_size,
                   "extension": p.suffix.lower(), "sha256": empreinte(p)} for p in fichiers]
    ecrire_csv("inventaire_fichiers.csv", inventaire)
    copies = collections.defaultdict(list)
    for f in inventaire:
        copies[f["sha256"]].append(f["chemin"])
    doublons = [{"sha256": h, "fichiers": " | ".join(paths)} for h, paths in copies.items() if len(paths) > 1]
    ecrire_csv("doublons_octet_identique.csv", doublons)

    workbook = openpyxl.load_workbook(PACK / "00_Documentation_et_Referentiels/Catalogue_sources_x_defis.xlsx", read_only=True, data_only=True)
    familles = {row[0]: row for row in list(workbook["Sources_x_Defis"].values)[1:] if row[0]}
    with (PACK / "00_Documentation_et_Referentiels/manifeste_telechargements.csv").open(encoding="utf-8-sig", newline="") as stream:
        manifeste = {(r["dossier"], r["fichier"]): r for r in csv.DictReader(stream, delimiter=";")}
    rows = list(workbook["Fichiers"].values)
    catalogue = []
    for row in rows[1:]:
        if not row[0]:
            continue
        source = PACK / row[2] / row[3]
        conversions = [s.strip() for s in re.split(r"[;\n]+", row[5] or "") if s.strip()]
        famille = familles[row[0]]
        meta = manifeste.get((row[2], row[3]), {})
        catalogue.append({"jeu": row[0], "famille": row[1], "source": str(source.relative_to(PACK)),
                          "producteur_catalogue": famille[3], "periode_annoncee_catalogue": famille[4],
                          "url_manifeste": meta.get("url", ""), "url_famille_catalogue": famille[13],
                          "source_presente": source.is_file(), "csv_annonces": len(conversions),
                          "csv_manquants": " | ".join(s for s in conversions if not (PACK / s).is_file())})
    ecrire_csv("rapprochement_catalogue.csv", catalogue)
    manquants = list(workbook["Non_collecte"].values)
    ecrire_csv("absences_declarees_catalogue.csv", [dict(zip(manquants[0], row)) for row in manquants[1:] if row[0]])
    workbook.close()

    profils = []
    for p in fichiers:
        if p.suffix.lower() != ".csv":
            continue
        n, irregulieres, premiere, erreur = 0, 0, None, ""
        try:
            with p.open(encoding="utf-8-sig", newline="") as stream:
                reader = csv.reader(stream, delimiter=";")
                premiere = next(reader)
                for row in reader:
                    n += 1
                    irregulieres += len(row) != len(premiere)
        except (OSError, UnicodeError, csv.Error, StopIteration) as exc:
            erreur = str(exc) or type(exc).__name__
        profils.append({"chemin": str(p.relative_to(PACK)), "lignes_apres_entete": n,
                        "colonnes": len(premiere or []), "largeurs_irregulieres": irregulieres,
                        "entetes_dupliques": len(premiere or []) - len(set(premiere or [])),
                        "erreur_lecture": erreur, "entetes": " | ".join(premiere or [])})
    ecrire_csv("profils_csv.csv", profils)

    osm_file = PACK / "data/04_Cartographie_SIG/Ecoles_OSM_HOTOSM/ecoles_osm_burkina.csv"
    with osm_file.open(encoding="utf-8-sig", newline="") as stream:
        osm = list(csv.DictReader(stream, delimiter=";"))
    admin = openpyxl.load_workbook(PACK / "04_Cartographie_SIG/COD-AB_limites_administratives/bfa_admin_boundaries.xlsx", read_only=True, data_only=True)
    sheet = admin["bfa_admin3"]
    raw = list(sheet.values)
    headers = raw[0]
    communes = [dict(zip(headers, row)) for row in raw[1:] if any(v is not None for v in row)]
    ancien = {str(r["adm3_pcode_old"]) for r in communes if r.get("adm3_pcode_old")}
    actuel = {str(r["adm3_pcode"]) for r in communes if r.get("adm3_pcode")}
    admin.close()
    pdi_sheets = []
    for fichier in sorted((PACK / "03_Conditions_de_Vie_et_Emploi/PDI_CONASUR").glob("*.xlsx")):
        classeur = openpyxl.load_workbook(fichier, read_only=True, data_only=True)
        for feuille in classeur:
            dates, n = [], 0
            for row in feuille.values:
                n += 1
                for valeur in row:
                    if isinstance(valeur, (datetime.datetime, datetime.date)):
                        dates.append(valeur.isoformat()[:10])
                    elif isinstance(valeur, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", valeur):
                        # Profil de dates ISO, sans interpréter les textes narratifs.
                        try:
                            dates.append(datetime.date.fromisoformat(valeur).isoformat())
                        except ValueError:
                            pass
            pdi_sheets.append({"fichier": fichier.name, "feuille": feuille.title, "lignes_physiques": n,
                               "colonnes": feuille.max_column, "date_min_cellules": min(dates) if dates else "",
                               "date_max_cellules": max(dates) if dates else "", "nombre_dates_distinctes": len(set(dates))})
        classeur.close()
    ecrire_csv("inventaire_pdi_feuilles.csv", pdi_sheets)
    invalides = 0
    coords = []
    for row in osm:
        try:
            lon, lat = float(row["longitude"]), float(row["latitude"])
            if not (math.isfinite(lon) and math.isfinite(lat) and -180 <= lon <= 180 and -90 <= lat <= 90):
                invalides += 1
            coords.append((lon, lat))
        except (KeyError, ValueError, TypeError):
            invalides += 1
    osm_stats = {
        "lignes": len(osm), "ids_distincts": len({r["id"] for r in osm}),
        "coordonnees_invalides": invalides,
        "doublons_coordonnees_exactes": len(coords) - len(set(coords)),
        "types": dict(collections.Counter(r.get("amenity") or "non_renseigne" for r in osm)),
        "champs_renseignes": {col: sum(bool((r.get(col) or "").strip()) for r in osm)
                               for col in ["name", "operator_type", "capacity_persons", "adm3_pcode"]},
        "codes_commune_distincts_osm": len({r["adm3_pcode"] for r in osm if r["adm3_pcode"]}),
        "lignes_code_absent": sum(not r["adm3_pcode"] for r in osm),
        "lignes_code_non_joint_ancien": sum(bool(r["adm3_pcode"]) and r["adm3_pcode"] not in ancien for r in osm),
        "lignes_code_non_joint_actuel": sum(bool(r["adm3_pcode"]) and r["adm3_pcode"] not in actuel for r in osm),
        "communes_referentiel": len(communes),
        "codes_anciens_uniques": len(ancien), "codes_actuels_uniques": len(actuel),
    }
    bilan = {"fichiers": len(fichiers), "octets": sum(f["octets"] for f in inventaire),
             "extensions": dict(collections.Counter(f["extension"] for f in inventaire)),
             "sources_catalogue": len(catalogue),
             "sources_manquantes": [r["source"] for r in catalogue if not r["source_presente"]],
             "conversions_manquantes": [r["csv_manquants"] for r in catalogue if r["csv_manquants"]],
             "csv_profiles": len(profils), "csv_dans_data": sum(p["chemin"].startswith("data/") for p in profils),
             "csv_erreurs": [r["chemin"] for r in profils if r["erreur_lecture"]],
             "csv_largeurs_irregulieres": [r["chemin"] for r in profils if r["largeurs_irregulieres"]],
             "groupes_doublons_exacts": len(doublons), "osm": osm_stats}
    bilan["feuilles_pdi_profilees"] = len(pdi_sheets)
    (SORTIE / "bilan_structurel.json").write_text(json.dumps(bilan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(bilan, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
