"""
ETAPES 1 et 2 — Collecte et nettoyage du tableau I.1 des annuaires du primaire.

Tableau I.1 : nombre d'écoles, de salles de classe, de groupes pédagogiques, de maîtres
chargés de cours et d'élèves, par province et par statut (public, privé).

Entrée  : extractions CSV des annuaires CNS529 (2023-2024) et CNS530 (2024-2025) du Data Pack.
Sorties : lignes brutes du tableau (01_collecte), table propre (02_nettoyage),
          tableau des contrôles et journal de nettoyage (02_nettoyage).

Lancer depuis le dossier DataChallenge :  python code/01_provinces_tableau_I1.py
"""
from pathlib import Path
import sys

import pandas as pd

EQUIPE = "EXX"          # code de l'équipe (évaluation à l'aveugle : pas de nom)
RACINE = Path(__file__).resolve().parent.parent
ANNUAIRES = RACINE / "01_collecte/datapack_extrait/DataPack_DCB_2026/data/01_Education_MENAPLN_DGESS/CNS_DGESS/Annuaires"
SOURCES = {             # année scolaire -> fichier d'extraction
    "2023-2024": "CNS529_Annuaire_statistique_de_lenseignement_primaire_2023_2024.csv",
    "2024-2025": "CNS530_Annuaire_statistique_de_lenseignement_primaire_2024_2025.csv",
}
PAGES = range(12, 17)   # pages du PDF où se trouve le tableau I.1
STATUTS = {"Public": "Public", "Privé": "Prive", "Total": "Total"}
VARIABLES = ["ecoles", "salles", "groupes_pedagogiques", "maitres_charges_cours", "eleves"]

DOSSIER_COLLECTE = RACINE / "01_collecte"
DOSSIER_NETTOYAGE = RACINE / "02_nettoyage"
F_BRUT = DOSSIER_COLLECTE / f"{EQUIPE}_01-collecte_D3_engineer_tableau-I1-lignes-brutes_v1.csv"
F_PROPRE = DOSSIER_NETTOYAGE / f"{EQUIPE}_02-nettoyage_D3_engineer_primaire-provinces-statut_v1.csv"
F_CONTROLES = DOSSIER_NETTOYAGE / f"{EQUIPE}_02-nettoyage_D3_engineer_controles-provinces_v1.csv"
F_JOURNAL = DOSSIER_NETTOYAGE / f"{EQUIPE}_02-nettoyage_D3_engineer_journal-nettoyage-provinces_v1.md"


def nombre(texte):
    """'23 416' -> 23416.0 ; '62,6' -> 62.6. Les espaces sont des séparateurs de milliers."""
    propre = str(texte).replace(" ", "").replace(" ", "").replace(" ", "").replace(",", ".")
    return float(propre)


def lire_lignes_brutes(annee, fichier):
    """Garde les lignes des pages du tableau I.1 et les colonnes utiles, sans rien corriger."""
    brut = pd.read_csv(ANNUAIRES / fichier, sep=";", dtype=str, encoding="utf-8-sig")
    brut["page"] = brut["page"].astype(int)
    brut = brut[brut["page"].isin(PAGES)].copy()
    colonnes = ["document", "page", "ligne", "nb_cellules"] + [f"c{i}" for i in range(1, 9)]
    brut = brut[colonnes]                      # la colonne de remarques n'est pas une donnée : non reprise
    brut.insert(0, "annee_scolaire", annee)
    return brut


def structurer(brut):
    """Transforme les lignes de mise en page en une table : une ligne par (territoire, statut)."""
    lignes, region, territoire, dans_national = [], None, None, False
    for _, l in brut.iterrows():
        c1 = "" if pd.isna(l["c1"]) else l["c1"].strip()
        c2 = "" if pd.isna(l["c2"]) else l["c2"].strip()
        n = int(l["nb_cellules"])
        if c1 == "Total National":             # début du bloc national (suivi d'un rappel d'en-têtes)
            dans_national, territoire = True, "Total National"
            continue
        if n == 1:                             # une seule cellule : nom de région, ou bruit (n° de page, « cours »)
            if c1.isupper() and not c1.isdigit() and not c1.startswith(("I.", "BF/")):
                region, dans_national = c1, False
            continue
        if n == 8 and c2 == "Public":          # première ligne d'un territoire : le nom est en c1
            territoire, valeurs, statut = c1, [l[f"c{i}"] for i in range(3, 9)], "Public"
        elif n == 7 and c1 in STATUTS:         # lignes suivantes (Privé, Total), ou bloc national
            valeurs, statut = [l[f"c{i}"] for i in range(2, 8)], c1
        else:
            continue                           # en-têtes et titres
        if territoire == "Total National" or dans_national:
            niveau, nom_region, nom = "national", "NATIONAL", "NATIONAL"
        elif territoire == "Total Région":
            niveau, nom_region, nom = "region", region, region
        else:
            niveau, nom_region, nom = "province", region, territoire
        chiffres = [nombre(v) for v in valeurs]
        lignes.append({"annee_scolaire": l["annee_scolaire"], "niveau": niveau, "region": nom_region, "province": nom,
                       "statut": STATUTS[statut], **dict(zip(VARIABLES, (int(c) for c in chiffres[:5]))),
                       "ratio_eleves_maitre_publie": chiffres[5],
                       "source_document": l["document"], "source_page": l["page"]})
    return pd.DataFrame(lignes)


def controler(table):
    """Vérifie la table contre les totaux publiés dans le même tableau. Renvoie un tableau de contrôles."""
    resultats = []

    def noter(annee, controle, attendu, obtenu, detail=""):
        resultats.append({"annee_scolaire": annee, "controle": controle, "attendu": attendu, "obtenu": obtenu,
                          "conforme": attendu == obtenu, "detail": detail})

    for annee, t in table.groupby("annee_scolaire"):
        prov, reg, nat = t[t.niveau == "province"], t[t.niveau == "region"], t[t.niveau == "national"]
        noter(annee, "Nombre de provinces", 45, prov["province"].nunique())
        noter(annee, "Nombre de régions", 13, reg["region"].nunique())
        noter(annee, "Trois statuts par territoire", 3 * (45 + 13 + 1), len(t))
        # Public + Privé = Total, pour chaque territoire et chaque variable
        large = t.pivot_table(index=["niveau", "province"], columns="statut", values=VARIABLES)
        ecarts = sum(int((large[v]["Public"] + large[v]["Prive"] != large[v]["Total"]).sum()) for v in VARIABLES)
        noter(annee, "Public + Privé = Total (écarts)", 0, ecarts)
        # Somme des provinces = total publié de la région
        somme_prov = prov.groupby(["region", "statut"])[VARIABLES].sum()
        publie_reg = reg.set_index(["region", "statut"])[VARIABLES]
        diff = (somme_prov != publie_reg.loc[somme_prov.index])
        mauvais = [f"{r}/{s}/{v}" for (r, s), ligne in diff.iterrows() for v in VARIABLES if ligne[v]]
        noter(annee, "Somme des provinces = total de la région (écarts)", 0, len(mauvais), "; ".join(mauvais[:8]))
        # Somme des régions = total national publié
        somme_reg = reg.groupby("statut")[VARIABLES].sum()
        publie_nat = nat.set_index("statut")[VARIABLES]
        diff = (somme_reg != publie_nat.loc[somme_reg.index])
        mauvais = [f"{s}/{v}" for s, ligne in diff.iterrows() for v in VARIABLES if ligne[v]]
        noter(annee, "Somme des régions = total national (écarts)", 0, len(mauvais), "; ".join(mauvais[:8]))
        # Ratio élèves/maître recalculé = ratio publié (à 0,1 près)
        avec_maitres = t[t["maitres_charges_cours"] > 0]
        recalcul = (avec_maitres["eleves"] / avec_maitres["maitres_charges_cours"]).round(1)
        ecart = (recalcul - avec_maitres["ratio_eleves_maitre_publie"]).abs() > 0.11
        noter(annee, "Ratio élèves/maître recalculé = ratio publié (écarts)", 0, int(ecart.sum()),
              "; ".join(f"{p}/{s}" for p, s in zip(avec_maitres.loc[ecart, "province"], avec_maitres.loc[ecart, "statut"]))[:200])
        noter(annee, "Aucune valeur négative", 0, int((t[VARIABLES] < 0).sum().sum()))
    return pd.DataFrame(resultats)


def main():
    DOSSIER_NETTOYAGE.mkdir(exist_ok=True)
    brut = pd.concat([lire_lignes_brutes(a, f) for a, f in SOURCES.items()], ignore_index=True)
    brut.to_csv(F_BRUT, index=False, encoding="utf-8-sig")

    table = structurer(brut)
    controles = controler(table)
    table.to_csv(F_PROPRE, index=False, encoding="utf-8-sig")
    controles.to_csv(F_CONTROLES, index=False, encoding="utf-8-sig")

    journal = [
        "# Journal de nettoyage — tableau I.1 par province\n",
        "Produit par `code/01_provinces_tableau_I1.py`. Ne pas modifier à la main : relancer le script.\n",
        "## Sources\n",
        *[f"- {a} : `{f}`, pages {PAGES.start} à {PAGES.stop - 1} du PDF (DGESS, annuaire statistique de l'enseignement primaire)." for a, f in SOURCES.items()],
        "\n## Traitements\n",
        "| Problème dans la source | Traitement | Raison |\n|---|---|---|",
        "| Le fichier est une extraction de mise en page : une ligne par ligne de texte du PDF | Sélection des pages du tableau, puis lecture ligne à ligne | Reconstituer une vraie table |",
        "| Le nom de la province n'apparaît que sur la ligne « Public » | Report du nom sur les lignes « Privé » et « Total » | Chaque ligne doit être lisible seule |",
        "| Le nom de la région est sur une ligne à part | Report sur toutes les provinces qui suivent | Pouvoir regrouper par région |",
        "| Nombres écrits avec des espaces (« 23 416 ») et des virgules (« 62,6 ») | Suppression des espaces, virgule remplacée par un point | Obtenir des nombres |",
        "| En-têtes répétés à chaque page, numéros de page, mot « cours » isolé | Lignes ignorées | Ce ne sont pas des données |",
        "| Lignes « Total Région » et « Total National » mêlées aux provinces | Conservées avec une colonne `niveau` (province, region, national) | Servent aux contrôles ; ne jamais les additionner aux provinces |",
        "| Colonne de remarques de l'extraction | Non reprise | Ce n'est pas une donnée statistique |",
        "| Statut « Privé » | Écrit `Prive` | Pas d'accent dans les modalités |",
        "\nAucune valeur n'a été corrigée, estimée ou supprimée.\n",
        "## Résultat\n",
        f"- {len(table)} lignes : {table[table.niveau == 'province']['province'].nunique()} provinces, "
        f"{table[table.niveau == 'region']['region'].nunique()} régions, 1 national ; 3 statuts ; {table['annee_scolaire'].nunique()} années scolaires.",
        f"- Contrôles : {int(controles['conforme'].sum())} conformes sur {len(controles)}.\n",
        "## Contrôles\n",
        "| Année | Contrôle | Attendu | Obtenu | Conforme | Détail |\n|---|---|---|---|---|---|",
        *[f"| {c.annee_scolaire} | {c.controle} | {c.attendu} | {c.obtenu} | {'oui' if c.conforme else 'NON'} | {c.detail} |" for c in controles.itertuples()],
        "\n## Variables\n",
        "| Variable | Définition |\n|---|---|",
        "| `annee_scolaire` | Année scolaire de l'annuaire |",
        "| `niveau` | `province`, `region` (total publié) ou `national` (total publié) |",
        "| `region`, `province` | Découpage en 13 régions et 45 provinces de l'annuaire |",
        "| `statut` | `Public`, `Prive` ou `Total` |",
        "| `ecoles`, `salles`, `groupes_pedagogiques`, `eleves` | Nombres publiés |",
        "| `maitres_charges_cours` | Maîtres chargés de cours (ce n'est pas tout le personnel enseignant) |",
        "| `ratio_eleves_maitre_publie` | Ratio publié dans l'annuaire, gardé pour contrôle |",
        "| `source_document`, `source_page` | Document et page du PDF d'où vient la ligne |",
    ]
    F_JOURNAL.write_text("\n".join(journal) + "\n", encoding="utf-8")

    print(f"Lignes brutes : {len(brut)}  ->  {F_BRUT.name}")
    print(f"Table propre  : {len(table)} lignes  ->  {F_PROPRE.name}")
    print(controles.to_string(index=False))
    if not controles["conforme"].all():
        print("\nATTENTION : au moins un contrôle n'est pas conforme. Voir le tableau ci-dessus.")
        sys.exit(1)
    print("\nTous les contrôles sont conformes.")


if __name__ == "__main__":
    main()
