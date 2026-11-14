"""
ETAPES 1 et 2 — Nettoyage des séries régionales du classeur principal (2015/2016 à 2024/2025).

Feuil1  : effectifs du primaire par sexe et par région.
Feuil13 : nombre d'écoles primaires par statut et par région.

Sorties : deux tables longues propres, un tableau de contrôles et un journal (02_nettoyage).
Le script recoupe aussi ces séries avec le tableau I.1 des annuaires (script 01).

Lancer depuis le dossier DataChallenge :  python code/02_regions_series_10_ans.py
"""
from pathlib import Path
import sys

import openpyxl
import pandas as pd

EQUIPE = "EXX"
RACINE = Path(__file__).resolve().parent.parent
CLASSEUR = RACINE / "00_sources" / "DONNEES_STATISTQUES_ PRESCOLAIRE ET PRIMAIRE_2016_2025_DCB.xlsx"
ANNEES = [f"{a}-{a + 1}" for a in range(2015, 2025)]     # 2015-2016 ... 2024-2025 : colonnes C à L
DOSSIER = RACINE / "02_nettoyage"
F_EFFECTIFS = DOSSIER / f"{EQUIPE}_02-nettoyage_D3_engineer_primaire-effectifs-regions-sexe_v1.csv"
F_ECOLES = DOSSIER / f"{EQUIPE}_02-nettoyage_D3_engineer_primaire-ecoles-regions-statut_v1.csv"
F_CONTROLES = DOSSIER / f"{EQUIPE}_02-nettoyage_D3_engineer_controles-regions_v1.csv"
F_JOURNAL = DOSSIER / f"{EQUIPE}_02-nettoyage_D3_engineer_journal-nettoyage-regions_v1.md"
F_PROVINCES = DOSSIER / f"{EQUIPE}_02-nettoyage_D3_engineer_primaire-provinces-statut_v1.csv"

CORRECTIONS_REGIONS = {"HAUT-BASSINS": "HAUTS-BASSINS"}   # écriture fautive -> nom de référence (annuaire)

MODALITES = {"GARCONS": "Garcons", "FILLES": "Filles", "TOTAL": "Total",
             "PUBLIC": "Public", "PRIVÉ": "Prive", "PRIVE": "Prive"}


def lire_feuille(classeur, feuille, nom_modalite, nom_valeur):
    """Lit un tableau « région / modalité / 10 années » et le met au format long."""
    ws = classeur[feuille]
    lignes, region = [], None
    for r in range(3, ws.max_row + 1):                    # les données commencent à la ligne 3
        a, b = ws.cell(r, 1).value, ws.cell(r, 2).value
        if isinstance(a, str) and a.strip():
            region = " ".join(a.split()).upper()            # le nom de région n'est écrit qu'une fois : on le reporte
            region = CORRECTIONS_REGIONS.get(region, region)
        if not isinstance(b, str) or b.strip().upper() not in MODALITES or region is None:
            continue                                       # ligne vide ou qui n'est pas une donnée
        valeurs = [ws.cell(r, c).value for c in range(3, 13)]
        if not all(isinstance(v, (int, float)) for v in valeurs):
            continue
        for annee, valeur in zip(ANNEES, valeurs):
            lignes.append({"annee_scolaire": annee, "niveau": "national" if region == "NATIONAL" else "region",
                           "region": region, nom_modalite: MODALITES[b.strip().upper()], nom_valeur: int(valeur),
                           "source_feuille": feuille})
    return pd.DataFrame(lignes)


def controler(effectifs, ecoles, provinces):
    resultats = []

    def noter(controle, attendu, obtenu, detail=""):
        resultats.append({"controle": controle, "attendu": attendu, "obtenu": obtenu, "conforme": attendu == obtenu, "detail": detail})

    reference = set(provinces.loc[provinces.niveau == "region", "region"])      # les 13 noms de l'annuaire
    for nom, table in [("Effectifs", effectifs), ("Écoles", ecoles)]:
        inconnus = sorted(set(table.loc[table.niveau == "region", "region"]) - reference)
        noter(f"{nom} : noms de région hors référence", 0, len(inconnus), "; ".join(inconnus))

    for nom, table, modalite, valeur, parties in [("Effectifs", effectifs, "sexe", "eleves", ["Garcons", "Filles"]),
                                                  ("Écoles", ecoles, "statut", "ecoles", ["Public", "Prive"])]:
        reg = table[table.niveau == "region"]
        noter(f"{nom} : nombre de régions", 13, reg["region"].nunique())
        noter(f"{nom} : nombre d'années", 10, table["annee_scolaire"].nunique())
        noter(f"{nom} : lignes attendues", 14 * 3 * 10, len(table))
        large = table.pivot_table(index=["region", "annee_scolaire"], columns=modalite, values=valeur)
        ecart = large[parties[0]] + large[parties[1]] != large["Total"]
        noter(f"{nom} : {parties[0]} + {parties[1]} = Total (écarts)", 0, int(ecart.sum()),
              "; ".join(f"{r} {a}" for r, a in large.index[ecart])[:200])
        somme = reg.groupby(["annee_scolaire", modalite])[valeur].sum()
        national = table[table.niveau == "national"].set_index(["annee_scolaire", modalite])[valeur]
        ecart = somme != national.loc[somme.index]
        noter(f"{nom} : somme des régions = national (écarts)", 0, int(ecart.sum()),
              "; ".join(f"{a} {m}" for a, m in somme.index[ecart])[:200])

    # Recoupement avec le tableau I.1 des annuaires (totaux publiés par région)
    ref = provinces[(provinces.niveau == "region") & (provinces.statut == "Total")]
    for annee in sorted(ref["annee_scolaire"].unique()):
        r = ref[ref.annee_scolaire == annee].set_index("region")
        e = effectifs[(effectifs.annee_scolaire == annee) & (effectifs.sexe == "Total") & (effectifs.niveau == "region")].set_index("region")["eleves"]
        ecart = e != r.loc[e.index, "eleves"]
        noter(f"Effectifs {annee} : classeur = annuaire, par région (écarts)", 0, int(ecart.sum()), "; ".join(e.index[ecart]))
        s = ecoles[(ecoles.annee_scolaire == annee) & (ecoles.statut == "Total") & (ecoles.niveau == "region")].set_index("region")["ecoles"]
        ecart = s != r.loc[s.index, "ecoles"]
        noter(f"Écoles {annee} : classeur = annuaire, par région (écarts)", 0, int(ecart.sum()), "; ".join(s.index[ecart]))
    return pd.DataFrame(resultats)


def main():
    classeur = openpyxl.load_workbook(CLASSEUR, data_only=True)
    effectifs = lire_feuille(classeur, "Feuil1", "sexe", "eleves")
    ecoles = lire_feuille(classeur, "Feuil13", "statut", "ecoles")
    provinces = pd.read_csv(F_PROVINCES)
    controles = controler(effectifs, ecoles, provinces)

    effectifs.to_csv(F_EFFECTIFS, index=False, encoding="utf-8-sig")
    ecoles.to_csv(F_ECOLES, index=False, encoding="utf-8-sig")
    controles.to_csv(F_CONTROLES, index=False, encoding="utf-8-sig")

    journal = [
        "# Journal de nettoyage — séries régionales sur dix ans\n",
        "Produit par `code/02_regions_series_10_ans.py`. Ne pas modifier à la main : relancer le script.\n",
        "## Source\n",
        f"- `{CLASSEUR.name}` (DGESS / MENAPLN) : feuille `Feuil1` (effectifs par sexe et région) et `Feuil13` (écoles par statut et région).\n",
        "## Traitements\n",
        "| Problème dans la source | Traitement | Raison |\n|---|---|---|",
        "| Tableau « en largeur » : une colonne par année | Passage au format long : une ligne par région, modalité et année | Format exploitable pour les calculs et les graphiques |",
        "| Nom de région écrit une seule fois pour trois lignes | Report du nom sur les lignes suivantes | Chaque ligne doit être lisible seule |",
        "| Années écrites `2015-2016`, `2015/2016`, `2024/25` selon les feuilles | Libellé unique `2015-2016` ... `2024-2025`, d'après la position de la colonne | Pouvoir relier les tables |",
        "| Modalités écrites `GARCONS`, `Privé`, `PRIVE`... | Libellés uniques sans accent : `Garcons`, `Filles`, `Public`, `Prive`, `Total` | Homogénéité |",
        "| Région écrite `HAUT-BASSINS` dans la feuille des écoles | Corrigée en `HAUTS-BASSINS`, nom de l'annuaire | Pouvoir relier les tables entre elles |",
        "| Ligne `NATIONAL` mêlée aux régions | Conservée avec `niveau = national` | Sert aux contrôles ; ne pas l'additionner aux régions |",
        "| Lignes vides et cellules de texte hors tableau | Ignorées : seules les lignes dont les dix valeurs sont numériques sont lues | Ce ne sont pas des données |",
        "\nAucune valeur n'a été corrigée, estimée ou supprimée.\n",
        "## Résultat\n",
        f"- Effectifs : {len(effectifs)} lignes. Écoles : {len(ecoles)} lignes.",
        f"- Contrôles : {int(controles['conforme'].sum())} conformes sur {len(controles)}.\n",
        "## Contrôles\n",
        "| Contrôle | Attendu | Obtenu | Conforme | Détail |\n|---|---|---|---|---|",
        *[f"| {c.controle} | {c.attendu} | {c.obtenu} | {'oui' if c.conforme else 'NON'} | {c.detail} |" for c in controles.itertuples()],
    ]
    F_JOURNAL.write_text("\n".join(journal) + "\n", encoding="utf-8")

    print(f"Effectifs : {len(effectifs)} lignes -> {F_EFFECTIFS.name}")
    print(f"Écoles    : {len(ecoles)} lignes -> {F_ECOLES.name}")
    print(controles.to_string(index=False))
    if not controles["conforme"].all():
        print("\nATTENTION : au moins un contrôle n'est pas conforme.")
        sys.exit(1)
    print("\nTous les contrôles sont conformes.")


if __name__ == "__main__":
    main()
