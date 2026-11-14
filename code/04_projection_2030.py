"""
ETAPE 4 — Analyse : projection des effectifs à l'horizon 2029-2030, par scénario.

Méthode volontairement simple (dix points par région, avec une rupture due à la crise) :
trois scénarios de croissance régionale, testés sur le passé, puis appliqués aux provinces.
Trois simulations supplémentaires utilisent les projections INSD provinciales des 6–11 ans.

Entrées : effectifs régionaux (script 02), indicateurs par province (script 03).
Sorties : projections régionales, test sur le passé, besoins 2030 par province (04_analyse).

Lancer depuis le dossier DataChallenge :  python code/04_projection_2030.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

from demographie_insd import HYPOTHESE, SCENARIOS_INSD, produire_tables, projeter_provinces

EQUIPE = "EXX"
RACINE = Path(__file__).resolve().parent.parent
HORIZON = 5                                  # 2024-2025 -> 2029-2030
NORME_ELEVES_PAR_MAITRE = 50
NORME_ELEVES_PAR_SALLE = 50

F_EFFECTIFS = RACINE / "02_nettoyage" / f"{EQUIPE}_02-nettoyage_D3_engineer_primaire-effectifs-regions-sexe_v1.csv"
F_INDICATEURS = RACINE / "03_transformation" / f"{EQUIPE}_03-transformation_D3_architect_indicateurs-provinces-public_v1.csv"
DOSSIER = RACINE / "04_analyse"
F_REGIONS = DOSSIER / f"{EQUIPE}_04-analyse_D3_scientist_projection-regions-2030_v1.csv"
F_TEST = DOSSIER / f"{EQUIPE}_04-analyse_D3_scientist_projection-test-sur-le-passe_v1.csv"
F_PROVINCES = DOSSIER / f"{EQUIPE}_04-analyse_D3_scientist_besoins-provinces-2030_v1.csv"

SCENARIOS = {
    "tendance_longue": "Chaque région garde son rythme moyen observé depuis 2015-2016",
    "croissance_nationale": "Toutes les régions croissent au rythme national moyen",
    "retour_au_pic": "Les régions sous leur maximum y reviennent en 2029-2030 ; les autres suivent leur tendance longue",
}


def taux_annuel(debut, fin, annees):
    """Taux de croissance annuel moyen entre deux valeurs séparées de `annees` années."""
    return (fin / debut) ** (1 / annees) - 1


def projeter(serie_regions, serie_nationale, horizon):
    """serie_regions : tableau régions × années (colonnes triées). Renvoie les niveaux projetés par scénario."""
    annees = serie_regions.shape[1] - 1
    dernier = serie_regions.iloc[:, -1]
    taux_region = taux_annuel(serie_regions.iloc[:, 0], dernier, annees)
    taux_national = taux_annuel(serie_nationale.iloc[0], serie_nationale.iloc[-1], annees)
    tendance = dernier * (1 + taux_region) ** horizon
    return pd.DataFrame({
        "tendance_longue": tendance,
        "croissance_nationale": dernier * (1 + taux_national) ** horizon,
        "retour_au_pic": np.maximum(tendance, serie_regions.max(axis=1)),
        "dernier_niveau": dernier,                       # méthode naïve, pour comparaison
    })


def main():
    DOSSIER.mkdir(exist_ok=True)
    eff = pd.read_csv(F_EFFECTIFS)
    eff = eff[eff.sexe == "Total"]
    regions = eff[eff.niveau == "region"].pivot(index="region", columns="annee_scolaire", values="eleves").sort_index(axis=1)
    national = eff[eff.niveau == "national"].set_index("annee_scolaire")["eleves"].sort_index()
    annees = list(regions.columns)

    # ---- 1) Test sur le passé : aurait-on bien prévu, 3 ans à l'avance ? ----
    tests = []
    for i_origine in range(3, len(annees) - 3):          # au moins 4 années connues, et 3 années à prévoir
        connu, cible = annees[: i_origine + 1], annees[i_origine + 3]
        prevu = projeter(regions[connu], national[connu], horizon=3)
        for methode in prevu.columns:
            erreur = (prevu[methode] - regions[cible]).abs() / regions[cible] * 100
            tests.append({"origine": connu[-1], "annee_prevue": cible, "methode": methode,
                          "erreur_moyenne_pct": round(erreur.mean(), 1), "erreur_mediane_pct": round(erreur.median(), 1),
                          "erreur_max_pct": round(erreur.max(), 1), "region_erreur_max": erreur.idxmax()})
    tests = pd.DataFrame(tests)
    tests.to_csv(F_TEST, index=False, encoding="utf-8-sig")
    resume_test = tests.groupby("methode")[["erreur_moyenne_pct", "erreur_mediane_pct", "erreur_max_pct"]].mean().round(1)

    # ---- 2) Projection régionale à l'horizon ----
    proj = projeter(regions, national, HORIZON).drop(columns="dernier_niveau")
    annee_cible = f"{int(annees[-1][:4]) + HORIZON}-{int(annees[-1][:4]) + HORIZON + 1}"
    sortie = proj.round(0).astype(int).reset_index().melt(id_vars="region", var_name="scenario", value_name="eleves_projetes")
    sortie["annee_scolaire"] = annee_cible
    sortie["eleves_derniere_annee"] = sortie["region"].map(regions.iloc[:, -1])
    sortie["facteur"] = (sortie["eleves_projetes"] / sortie["eleves_derniere_annee"]).round(4)
    sortie["hypothese"] = sortie["scenario"].map(SCENARIOS)


    # ---- 3) Besoins par province en 2029-2030 (primaire public) ----
    # Hypothèses : chaque province évolue comme sa région ; la part du public reste celle de 2024-2025 ;
    # les maîtres et les salles d'aujourd'hui sont tous conservés (ni départs, ni retraites, ni salles perdues).
    # Les trois scénarios ne forment PAS un intervalle de confiance.
    ind = pd.read_csv(F_INDICATEURS)
    ind = ind[ind.annee_scolaire == ind["annee_scolaire"].max()]
    lignes = []
    for scenario in SCENARIOS:
        facteur = (proj[scenario] / regions.iloc[:, -1])
        p = ind[["region", "province", "eleves", "maitres", "salles"]].copy()
        p["scenario"], p["annee_scolaire"] = scenario, annee_cible
        p["eleves_projetes"] = (p["eleves"] * p["region"].map(facteur)).round(0).astype(int)
        p["besoin_maitres"] = np.ceil(p["eleves_projetes"] / NORME_ELEVES_PAR_MAITRE).astype(int)
        p["besoin_salles"] = np.ceil(p["eleves_projetes"] / NORME_ELEVES_PAR_SALLE).astype(int)
        p["maitres_a_ajouter"] = (p["besoin_maitres"] - p["maitres"]).clip(lower=0)
        p["salles_a_ajouter"] = (p["besoin_salles"] - p["salles"]).clip(lower=0)
        lignes.append(p.rename(columns={"eleves": "eleves_2024_2025"}))
    # INSD : rapport des inscrits publics aux 6–11 ans, maintenu ou ajusté de ±10 %.
    # Les scénarios historiques ci-dessus et leurs tests restent inchangés.
    table_facteurs = produire_tables(ind.province)
    for scenario, coefficient in SCENARIOS_INSD.items():
        lignes.append(projeter_provinces(ind, table_facteurs, scenario, coefficient,
                                        annee_cible, NORME_ELEVES_PAR_MAITRE, NORME_ELEVES_PAR_SALLE))
    besoins = pd.concat(lignes, ignore_index=True)
    besoins.to_csv(F_PROVINCES, index=False, encoding="utf-8-sig")
    # Agrégation des simulations provinciales pour cohérence avec la sortie régionale.
    nouveaux = besoins[besoins.scenario.isin(SCENARIOS_INSD)].groupby(
        ["region", "scenario"], as_index=False)["eleves_projetes"].sum()
    nouveaux["annee_scolaire"] = annee_cible
    nouveaux["eleves_derniere_annee"] = nouveaux.region.map(ind.groupby("region").eleves.sum())
    nouveaux["facteur"] = (nouveaux.eleves_projetes / nouveaux.eleves_derniere_annee).round(4)
    nouveaux["hypothese"] = nouveaux.scenario.map(
        {s: f"{HYPOTHESE} Coefficient du rapport : {c}. Agrégat du primaire public provincial ; "
            "dénominateur de la dernière année = primaire public provincial." for s, c in SCENARIOS_INSD.items()})
    pd.concat([sortie, nouveaux], ignore_index=True).to_csv(F_REGIONS, index=False, encoding="utf-8-sig")

    print("Test sur le passé (prévision à 3 ans, moyenne sur les origines possibles) :")
    print(resume_test.to_string())
    print(f"\nProjection {annee_cible}, total des régions par scénario :")
    print(proj.sum().round(0).astype(int).to_string(), f"\n(dernière année observée : {int(regions.iloc[:, -1].sum())})")
    print(f"\nPrimaire public, besoins {annee_cible} par scénario (norme {NORME_ELEVES_PAR_MAITRE}) :")
    print(besoins.groupby("scenario")[["eleves_projetes", "maitres_a_ajouter", "salles_a_ajouter"]].sum().to_string())


if __name__ == "__main__":
    main()
