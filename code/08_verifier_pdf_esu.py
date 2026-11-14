"""Audit documentaire indépendant des 107 valeurs ESU retenues.

Relit le PDF original avec pdftotext (Poppler), sans utiliser le CSV du Data Pack
ni le parseur du script 06 pour construire les valeurs de référence.
Commande facultative après la chaîne principale : python code/08_verifier_pdf_esu.py
"""
from pathlib import Path
import csv
import hashlib
import re
import shutil
import subprocess
import unicodedata

EQUIPE = "EXX"
RACINE = Path(__file__).resolve().parent.parent
DOCUMENT = "Rapport_statistique_mensuel_ESU_Février_2026.pdf"
PDF = RACINE / "01_collecte/datapack_extrait/DataPack_DCB_2026/01_Education_MENAPLN_DGESS/ESU_Rapports_mensuels" / DOCUMENT
TABLE = RACINE / "02_nettoyage" / f"{EQUIPE}_02-nettoyage_D3_engineer_esu-primaire-provinces-2026_v1.csv"
SORTIE = RACINE / "02_nettoyage" / f"{EQUIPE}_02-nettoyage_D3_engineer_verification-esu-pdf_v1.csv"


def normaliser(texte):
    return " ".join("".join(c for c in unicodedata.normalize("NFD", texte.upper())
                             if unicodedata.category(c) != "Mn").split())


def lire_pdf(texte):
    """Lecture directe des colonnes séparées par au moins deux espaces du PDF."""
    annexe, lignes, vus = None, [], set()
    for page, contenu in enumerate(texte.split("\f"), 1):
        for ligne in contenu.splitlines():
            titre = re.match(r"\s*Annexe\s+(\d+)\s*:", ligne)
            if titre:
                annexe = int(titre[1])
            if annexe not in (1, 2, 4):
                continue
            cellules = re.split(r"\s{2,}", ligne.strip())
            n = 3 if annexe == 4 else 4
            if len(cellules) < n + 1 or not all(re.fullmatch(r"\d[\d ]*", v) for v in cellules[-n:]):
                continue
            nom = normaliser(cellules[-n-1])
            if nom.startswith("TOTAL "):
                continue
            chiffres = [int(v.replace(" ", "")) for v in cellules[-n:]]
            if sum(chiffres[:-1]) != chiffres[-1]:
                raise ValueError(f"Total incohérent dans le PDF : {nom}, page {page}")
            cle = (annexe, page, nom)
            if cle in vus:
                raise ValueError(f"Ligne PDF dupliquée : {cle}")
            vus.add(cle)
            lignes.append({"annexe": annexe, "page": page, "province": nom,
                           "valeur": chiffres[-1] if annexe == 4 else chiffres[2]})
    return lignes


def comparer(pdf, table):
    reference = {(r["annexe"], r["page"], r["province"]): r["valeur"] for r in pdf}
    index, audit = {}, []
    for r in table:
        cle = (int(r["source_annexe"]), int(r["source_page"]), normaliser(r["libelle_province_source"]))
        if cle in index:
            raise ValueError(f"Valeur de table dupliquée : {cle}")
        index[cle] = int(r["valeur"])
    if not reference or set(reference) != set(index):
        raise ValueError(f"Couverture PDF/table différente : absentes de la table {set(reference)-set(index)}, absentes du PDF {set(index)-set(reference)}")
    for cle in sorted(reference):
        audit.append({"annexe": cle[0], "page_pdf": cle[1], "province_source": cle[2],
                      "valeur_pdf": reference[cle], "valeur_table": index[cle],
                      "conforme": reference[cle] == index[cle]})
    return audit


def main():
    if not shutil.which("pdftotext"):
        raise SystemExit("Cet audit facultatif nécessite pdftotext (Poppler), en plus de la chaîne Python principale.")
    lecture = subprocess.run(["pdftotext", "-layout", str(PDF), "-"], capture_output=True, text=True, check=True)
    with TABLE.open(encoding="utf-8-sig", newline="") as f:
        table = [r for r in csv.DictReader(f) if r["valeur"] != ""]
    audit = comparer(lire_pdf(lecture.stdout), table)
    empreintes = {"sha256_pdf": hashlib.sha256(PDF.read_bytes()).hexdigest(),
                  "sha256_table": hashlib.sha256(TABLE.read_bytes()).hexdigest()}
    audit = [{**r, **empreintes} for r in audit]
    with SORTIE.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(audit[0]))
        writer.writeheader()
        writer.writerows(audit)
    if not all(r["conforme"] for r in audit):
        raise SystemExit(f"Écart entre le PDF et la table : voir {SORTIE.name}")
    print(f"Audit direct du PDF : {len(audit)}/{len(audit)} valeurs conformes, couverture identique.")
    print("Empreintes des deux entrées enregistrées dans", SORTIE.name)


if __name__ == "__main__":
    main()
