"""
ETAPE 3 — Transformation : indicateurs et déficits par province (primaire public).

Entrées : tables propres des scripts 01 et 02.
Sorties : table des indicateurs par province et par année, dictionnaire des variables (03_transformation).

Lancer depuis le dossier DataChallenge :  python code/03_indicateurs_provinces.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

EQUIPE = "EXX"
RACINE = Path(__file__).resolve().parent.parent

# ---- SEUILS DE SIMULATION : ce ne sont pas des normes établies tant que leur texte de référence n'est pas cité ----
NORME_ELEVES_PAR_MAITRE = 50      # seuil élèves par maître (valeur de la note d'intention, à sourcer)
NORME_ELEVES_PAR_SALLE = 50       # seuil élèves par salle, fixé séparément (hypothèse de travail, à sourcer)
SEUIL_FORTEMENT_TOUCHEE = 80      # effectifs de la région < 80 % de son maximum sur dix ans
SEUIL_TOUCHEE = 95

F_PROVINCES = RACINE / "02_nettoyage" / f"{EQUIPE}_02-nettoyage_D3_engineer_primaire-provinces-statut_v1.csv"
F_EFFECTIFS = RACINE / "02_nettoyage" / f"{EQUIPE}_02-nettoyage_D3_engineer_primaire-effectifs-regions-sexe_v1.csv"
DOSSIER = RACINE / "03_transformation"
F_INDICATEURS = DOSSIER / f"{EQUIPE}_03-transformation_D3_architect_indicateurs-provinces-public_v1.csv"
F_DICTIONNAIRE = DOSSIER / f"{EQUIPE}_03-transformation_D3_architect_dictionnaire-variables_v1.md"

DICTIONNAIRE = [
    ("annee_scolaire", "Année scolaire", "annuaire"),
    ("region, province", "13 régions et 45 provinces de l'annuaire", "annuaire"),
    ("ecoles, salles, groupes_pedagogiques, maitres, eleves", "Nombres du primaire PUBLIC", "annuaire, tableau I.1"),
    ("eleves_par_maitre", "eleves / maitres", "calcul"),
    ("eleves_par_salle", "eleves / salles", "calcul"),
    ("eleves_par_ecole", "eleves / ecoles", "calcul"),
    ("besoin_maitres", f"eleves / {NORME_ELEVES_PAR_MAITRE}, arrondi à l'entier supérieur", "calcul, norme"),
    ("deficit_maitres", "max(0, besoin_maitres − maitres) : maîtres manquants pour atteindre la norme", "calcul"),
    ("marge_comptable_maitres", "max(0, maitres − besoin_maitres) : écart comptable au seuil. Ce n'est PAS un sureffectif mobilisable : la moyenne provinciale masque les écoles, les distances et les groupes pédagogiques", "calcul"),
    ("besoin_salles", f"eleves / {NORME_ELEVES_PAR_SALLE}, arrondi à l'entier supérieur", "calcul, norme"),
    ("deficit_salles", "max(0, besoin_salles − salles)", "calcul"),
    ("groupes_sans_maitre", "max(0, groupes_pedagogiques − maitres) : groupes sans maître chargé de cours attitré", "calcul"),
    ("groupes_sans_salle", "max(0, groupes_pedagogiques − salles)", "calcul"),
    ("part_prive_pct", "Part des élèves de la province scolarisés dans le privé (%)", "calcul sur l'annuaire"),
    ("variation_eleves_pct", "Évolution des élèves du public par rapport à l'année précédente (%)", "calcul"),
    ("variation_ecoles", "Évolution du nombre d'écoles publiques par rapport à l'année précédente", "calcul"),
    ("region_niveau_vs_pic_pct", "Effectifs de la région (public + privé) en % de leur maximum sur 2015/2016–2024/2025", "classeur principal"),
    ("inscriptions_region", f"Niveau des inscriptions de la région : « très en dessous du maximum » si < {SEUIL_FORTEMENT_TOUCHEE} %, « en dessous du maximum » si < {SEUIL_TOUCHEE} %, sinon « proches du maximum ». Mesure les inscriptions, PAS la sécurité", "calcul"),
]


def main():
    DOSSIER.mkdir(exist_ok=True)
    brut = pd.read_csv(F_PROVINCES)
    prov = brut[brut.niveau == "province"]
    public = prov[prov.statut == "Public"].rename(columns={"maitres_charges_cours": "maitres"}).copy()
    total = prov[prov.statut == "Total"].set_index(["annee_scolaire", "province"])["eleves"]
    prive = prov[prov.statut == "Prive"].set_index(["annee_scolaire", "province"])["eleves"]

    t = public[["annee_scolaire", "region", "province", "ecoles", "salles", "groupes_pedagogiques", "maitres", "eleves"]].copy()
    t["eleves_par_maitre"] = (t["eleves"] / t["maitres"]).round(1)
    t["eleves_par_salle"] = (t["eleves"] / t["salles"]).round(1)
    t["eleves_par_ecole"] = (t["eleves"] / t["ecoles"]).round(0)
    t["besoin_maitres"] = np.ceil(t["eleves"] / NORME_ELEVES_PAR_MAITRE).astype(int)
    t["deficit_maitres"] = (t["besoin_maitres"] - t["maitres"]).clip(lower=0)
    t["marge_comptable_maitres"] = (t["maitres"] - t["besoin_maitres"]).clip(lower=0)
    t["besoin_salles"] = np.ceil(t["eleves"] / NORME_ELEVES_PAR_SALLE).astype(int)
    t["deficit_salles"] = (t["besoin_salles"] - t["salles"]).clip(lower=0)
    t["groupes_sans_maitre"] = (t["groupes_pedagogiques"] - t["maitres"]).clip(lower=0)
    t["groupes_sans_salle"] = (t["groupes_pedagogiques"] - t["salles"]).clip(lower=0)
    cle = list(zip(t["annee_scolaire"], t["province"]))
    t["part_prive_pct"] = (prive.loc[cle].to_numpy() / total.loc[cle].to_numpy() * 100).round(1)

    # Évolution d'une année sur l'autre (les deux années disponibles par province)
    t = t.sort_values(["province", "annee_scolaire"])
    t["variation_eleves_pct"] = (t.groupby("province")["eleves"].pct_change() * 100).round(1)
    t["variation_ecoles"] = t.groupby("province")["ecoles"].diff()

    # Contexte régional : où en sont les effectifs par rapport à leur maximum sur dix ans
    eff = pd.read_csv(F_EFFECTIFS)
    eff = eff[(eff.sexe == "Total") & (eff.niveau == "region")]
    pic = eff.groupby("region")["eleves"].max()
    dernier = eff[eff.annee_scolaire == eff["annee_scolaire"].max()].set_index("region")["eleves"]
    niveau = (dernier / pic * 100).round(1)
    t["region_niveau_vs_pic_pct"] = t["region"].map(niveau)
    t["inscriptions_region"] = np.select([t["region_niveau_vs_pic_pct"] < SEUIL_FORTEMENT_TOUCHEE, t["region_niveau_vs_pic_pct"] < SEUIL_TOUCHEE],
                                     ["très en dessous du maximum", "en dessous du maximum"], default="proches du maximum")
    t = t.sort_values(["annee_scolaire", "region", "province"]).reset_index(drop=True)
    t.to_csv(F_INDICATEURS, index=False, encoding="utf-8-sig")

    lignes = ["# Dictionnaire des variables — indicateurs par province (primaire public)\n",
              "Produit par `code/03_indicateurs_provinces.py`.\n",
              f"Seuils de simulation : {NORME_ELEVES_PAR_MAITRE} élèves par maître, {NORME_ELEVES_PAR_SALLE} élèves par salle. "
              "Ce sont des hypothèses de travail tant que leur texte de référence n'est pas cité ; les changer en tête du script, puis relancer.\n",
              "| Variable | Définition | Origine |\n|---|---|---|",
              *[f"| `{v}` | {d} | {o} |" for v, d, o in DICTIONNAIRE],
              "\n## Schéma des données\n",
              "```",
              "00_sources / Data Pack (annuaires CNS529, CNS530)        00_sources (classeur DGESS 2016-2025)",
              "        │ script 01                                              │ script 02",
              "        ▼                                                        ▼",
              "provinces × statut × année  ───────────────┐      régions × sexe × année ; régions × statut × année",
              "        │ script 03                         │              │ script 04",
              "        ▼                                   │              ▼",
              "indicateurs par province (public)  ◄────────┴──── contexte régional ; projection 2030",
              "        │ script 05",
              "        ▼",
              "répartition des maîtres et des salles  ──►  script 06 : contexte ESU daté  ──►  script 07 : graphiques, carte, fiche",
              "```",
              "\nClés de jointure : `annee_scolaire`, `region`, `province` (noms de l'annuaire, en majuscules, sans accent)."]
    F_DICTIONNAIRE.write_text("\n".join(lignes) + "\n", encoding="utf-8")

    a = t[t.annee_scolaire == t["annee_scolaire"].max()]
    print(f"Indicateurs : {len(t)} lignes -> {F_INDICATEURS.name}")
    print(f"Année {a['annee_scolaire'].iloc[0]}, primaire public, seuil de simulation {NORME_ELEVES_PAR_MAITRE} élèves par maître :")
    print(f"  provinces au-dessus du seuil : {(a['eleves_par_maitre'] > NORME_ELEVES_PAR_MAITRE).sum()} sur {len(a)}")
    print(f"  maîtres manquants (somme des déficits) : {int(a['deficit_maitres'].sum())}")
    print(f"  salles manquantes (somme des déficits) : {int(a['deficit_salles'].sum())}")
    print(f"  marge comptable au regard du seuil     : {int(a['marge_comptable_maitres'].sum())}")
    print(a.sort_values("eleves_par_maitre", ascending=False)[["region", "province", "eleves", "maitres", "eleves_par_maitre", "deficit_maitres", "inscriptions_region"]].head(8).to_string(index=False))


if __name__ == "__main__":
    main()
