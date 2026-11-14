"""Exporte les tables contrôlées vers une interface HTML/JS locale, sans réseau."""
from pathlib import Path
import json
import sys
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from libelles import SCENARIOS

EQUIPE = "EXX"
RACINE = Path(__file__).resolve().parent.parent


def construire_donnees(indicateurs, besoins, esu, geometries):
    provinces = set(indicateurs.province)
    if indicateurs.province.duplicated().any() or esu.province.duplicated().any():
        raise ValueError("Province dupliquée dans les tables d'export")
    if set(esu.province) != provinces or set(geometries) != provinces:
        raise ValueError("Couverture différente des provinces, ESU ou géométries")
    if besoins.duplicated(["province", "scenario"]).any():
        raise ValueError("Province/scénario dupliqué")
    for scenario, table in besoins.groupby("scenario"):
        if scenario not in SCENARIOS or set(table.province) != provinces:
            raise ValueError(f"Scénario incomplet ou inconnu : {scenario}")
    esu_index = esu.set_index("province")
    demandes = {(r.province, r.scenario): int(r.eleves_projetes) for r in besoins.itertuples()}
    ids = [s for s in SCENARIOS if s == "actuel" or s in set(besoins.scenario)]
    result = []
    for r in indicateurs.sort_values(["region", "province"]).itertuples():
        contexte = esu_index.loc[r.province]
        values = {}
        for key in ["ecoles_rouvertes", "ecoles_delocalisees", "eleves_deplaces"]:
            value = contexte.get(f"esu_{key}")
            values[key] = None if pd.isna(value) else int(value)
            values[key + "_statut"] = str(contexte.get(f"esu_{key}_statut", "non_renseigne"))
        result.append({"province": r.province, "region": r.region, "eleves": int(r.eleves),
                       "maitres": int(r.maitres), "salles": int(r.salles),
                       "groupes_pedagogiques": int(r.groupes_pedagogiques),
                       "inscriptions_region": str(r.inscriptions_region),
                       "demandes": {s: int(r.eleves) if s == "actuel" else demandes[(r.province, s)] for s in ids},
                       "esu": values})
    return {
        "meta": {"annee": "2024-2025", "horizon": "2029-2030", "date_esu": "2026-02-28",
                 "source": "DGESS / INSD", "version": "1",
                 "hypothese_2030": "Années civiles 2025/2030 rapprochées des années scolaires 2024/25 et 2029/30 ; stocks de maîtres et de salles conservés. Scénarios conditionnels, pas intervalle de confiance."},
        "scenarios": [{"id": s, "label": SCENARIOS[s][0], "description": SCENARIOS[s][1]} for s in ids],
        "provinces": result, "geometries": geometries,
        "sources": [
            {"titre": "Annuaire primaire 2024–2025", "producteur": "DGESS", "detail": "CNS530, tableau I.1, PDF p. 12–16 ; primaire public."},
            {"titre": "Projections démographiques 2020–2035", "producteur": "INSD", "detail": "RGPH2019, édition 2 de janvier 2023 ; 6–11 ans des 45 provinces en 2025 et 2030. Structure sexe/âge provinciale supposée identique à celle de la région."},
            {"titre": "Rapport ESU février 2026", "producteur": "DGESS / MEBAPLN", "detail": "Observation au 28 février 2026 ; public/privé non distingué. Sans correction des effectifs du diagnostic."},
            {"titre": "Limites COD-AB", "producteur": "IGB / OCHA", "detail": "Correspondance vers les 45 anciennes provinces. Soum et Tapoa affichées sur leurs composantes sans ventilation des valeurs."},
        ],
    }


def main():
    ind = pd.read_csv(RACINE / "03_transformation" / f"{EQUIPE}_03-transformation_D3_architect_indicateurs-provinces-public_v1.csv")
    ind = ind[ind.annee_scolaire == ind.annee_scolaire.max()]
    besoins = pd.read_csv(RACINE / "04_analyse" / f"{EQUIPE}_04-analyse_D3_scientist_besoins-provinces-2030_v1.csv")
    sortie = RACINE / "05_interpretation"
    esu = pd.read_csv(sortie / f"{EQUIPE}_05-interpretation_D3_analyst_contexte-esu-affectations_v1.csv")
    geometries = json.loads((sortie / f"{EQUIPE}_05-interpretation_D3_analyst_fond-de-carte-provinces-simplifie_v1.json").read_text())
    if len(ind) != 45:
        raise ValueError("Le tableau de bord attend les 45 provinces")
    data = construire_donnees(ind, besoins, esu, geometries)
    dossier = RACINE / "tableau_de_bord"
    dossier.mkdir(exist_ok=True)
    serialized = json.dumps(data, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
    (dossier / "donnees.js").write_text("window.DCB_DATA=" + serialized.replace("</", "<\\/") + ";\n", encoding="utf-8")
    print(f"Interface : {len(data['provinces'])} provinces, {len(data['scenarios'])} situations ; ouvrir tableau_de_bord/index.html")


if __name__ == "__main__":
    main()
