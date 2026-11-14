"""
ETAPE 4 — Analyse : répartition d'un nombre donné de maîtres et de salles entre les provinces.

Trois règles sont comparées, à budget égal :
  - proportionnelle     : au prorata des élèves (règle administrative simple) ;
  - deficit_d_abord     : chaque unité va à la province où il manque le plus d'unités pour atteindre la norme ;
  - egalisation         : chaque unité va à la province où le ratio élèves par unité est le plus élevé.

Pourquoi pas de solveur ? Avec un seul budget et un critère par province, attribuer les unités une à une
à la province la plus mal placée donne exactement le meilleur résultat possible pour le critère visé
(somme des déficits pour « deficit_d_abord », pire ratio pour « egalisation »). Le calcul reste donc
vérifiable à la main. Un solveur ne devient nécessaire que si l'on ajoute des contraintes croisées.

Entrées : indicateurs par province (script 03), besoins 2030 (script 04).
Sorties : comparaison des règles, répartition détaillée par province (04_analyse).

Lancer depuis le dossier DataChallenge :  python code/05_repartition.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

EQUIPE = "EXX"
RACINE = Path(__file__).resolve().parent.parent
NORME = 50                                   # SEUIL DE SIMULATION (élèves par maître, et par salle) : hypothèse à sourcer
SEUILS_TESTES = [40, 45, 50, 55, 60]         # pour l'analyse de sensibilité
# « Budget » = nombre de postes ou de salles à répartir. Aucun chiffrage financier n'est fait.
BUDGETS_MAITRES = [500, 1000, 2000, 3000, 5000]
BUDGETS_SALLES = [500, 1000, 2000, 3000, 4000]
BUDGET_DE_REFERENCE = 2000                   # budget détaillé province par province
PROVINCES_NON_ACCESSIBLES = []               # à remplir par l'équipe si des affectations y sont impossibles
REGLES = ["proportionnelle", "deficit_d_abord", "egalisation"]

F_INDICATEURS = RACINE / "03_transformation" / f"{EQUIPE}_03-transformation_D3_architect_indicateurs-provinces-public_v1.csv"
F_BESOINS_2030 = RACINE / "04_analyse" / f"{EQUIPE}_04-analyse_D3_scientist_besoins-provinces-2030_v1.csv"
DOSSIER = RACINE / "04_analyse"
F_COMPARAISON = DOSSIER / f"{EQUIPE}_04-analyse_D3_scientist_repartition-comparaison-regles_v1.csv"
F_DETAIL = DOSSIER / f"{EQUIPE}_04-analyse_D3_scientist_repartition-detail-provinces_v1.csv"
F_2030 = DOSSIER / f"{EQUIPE}_04-analyse_D3_scientist_repartition-horizon-2030_v1.csv"
F_SENSIBILITE = DOSSIER / f"{EQUIPE}_04-analyse_D3_scientist_sensibilite-seuils_v1.csv"
F_PREUVE = DOSSIER / f"{EQUIPE}_04-analyse_D3_scientist_preuve-optimalite-egalisation_v1.csv"


def repartir(eleves, existant, budget, regle, norme=NORME, accessibles=None):
    """Répartit `budget` unités entières entre les provinces. Renvoie le tableau des unités ajoutées.

    eleves, existant : tableaux numpy (une valeur par province). accessibles : tableau de booléens.
    """
    eleves, existant = np.asarray(eleves, dtype=float), np.asarray(existant, dtype=float)
    n = len(eleves)
    accessibles = np.ones(n, dtype=bool) if accessibles is None else np.asarray(accessibles, dtype=bool)
    ajout = np.zeros(n, dtype=int)
    if regle == "proportionnelle":
        # Prorata des élèves, arrondi par la méthode du plus fort reste (le total fait exactement le budget)
        part = np.where(accessibles, eleves, 0.0)
        quota = budget * part / part.sum()
        ajout = np.floor(quota).astype(int)
        restes = quota - ajout
        for i in np.argsort(-restes)[: budget - ajout.sum()]:
            ajout[i] += 1
        return ajout
    for _ in range(budget):                               # une unité à la fois
        apres = existant + ajout
        if regle == "deficit_d_abord":
            critere = eleves / norme - apres              # unités encore manquantes
            critere = np.where(critere > 0, critere, -np.inf)
            if not np.isfinite(critere[accessibles]).any():   # plus aucun déficit : on égalise les ratios
                critere = eleves / np.maximum(apres, 1)
        else:                                             # egalisation
            critere = eleves / np.maximum(apres, 1)       # ratio élèves par unité
        critere = np.where(accessibles, critere, -np.inf)
        ajout[int(np.argmax(critere))] += 1
    return ajout


def mesurer(eleves, existant, ajout, norme=NORME):
    """Indicateurs de résultat d'une répartition."""
    apres = existant + ajout
    ratio = eleves / apres
    au_dessus = ratio > norme
    return {"provinces_au_dessus_norme": int(au_dessus.sum()),
            "eleves_en_province_au_dessus_norme": int(eleves[au_dessus].sum()),
            "ratio_max": round(float(ratio.max()), 1),
            "ratio_moyen": round(float(eleves.sum() / apres.sum()), 1),
            "ecart_type_ratios": round(float(ratio.std()), 1),
            "deficit_restant": int(np.clip(np.ceil(eleves / norme) - apres, 0, None).sum()),
            "unites_donnees_sous_la_norme": int(ajout[(eleves / np.maximum(existant, 1)) <= norme].sum())}


def unites_necessaires(eleves, existant, plafond):
    """Nombre minimal d'unités à ajouter pour que chaque province ait un ratio <= plafond."""
    return int(np.clip(np.ceil(eleves / plafond - 1e-9) - existant, 0, None).sum())


def prouver_optimalite(eleves, existant, ajout, budget):
    """Vérifie, indépendamment de l'algorithme, que le pire ratio obtenu ne peut pas être amélioré avec ce budget.

    Le pire ratio obtenu est r. On calcule le nombre d'unités nécessaires pour le plafond r (doit être <= budget)
    et pour un plafond juste en dessous de r (doit être > budget)."""
    r = float((eleves / (existant + ajout)).max())
    return {"budget": budget, "pire_ratio_obtenu": round(r, 4),
            "unites_pour_ce_plafond": unites_necessaires(eleves, existant, r),
            "unites_pour_un_plafond_plus_bas": unites_necessaires(eleves, existant, r - 1e-6)}


def main():
    ind = pd.read_csv(F_INDICATEURS)
    ind = ind[ind.annee_scolaire == ind["annee_scolaire"].max()].reset_index(drop=True)
    accessibles = ~ind["province"].isin(PROVINCES_NON_ACCESSIBLES).to_numpy()
    eleves = ind["eleves"].to_numpy(dtype=float)

    # ---- 1) Comparaison des trois règles, pour plusieurs budgets ----
    lignes = []
    for ressource, colonne, budgets in [("maitres", "maitres", BUDGETS_MAITRES), ("salles", "salles", BUDGETS_SALLES)]:
        existant = ind[colonne].to_numpy(dtype=float)
        lignes.append({"ressource": ressource, "budget": 0, "regle": "situation actuelle", **mesurer(eleves, existant, np.zeros(len(ind)))})
        for budget in budgets:
            for regle in REGLES:
                ajout = repartir(eleves, existant, budget, regle, accessibles=accessibles)
                assert ajout.sum() == budget and (ajout >= 0).all(), "la répartition doit distribuer exactement le budget"
                lignes.append({"ressource": ressource, "budget": budget, "regle": regle, **mesurer(eleves, existant, ajout)})
    comparaison = pd.DataFrame(lignes)
    comparaison.to_csv(F_COMPARAISON, index=False, encoding="utf-8-sig")

    # ---- 2) Détail par province pour le budget de référence ----
    detail = ind[["region", "province", "eleves", "maitres", "salles", "eleves_par_maitre", "eleves_par_salle",
                  "deficit_maitres", "deficit_salles", "inscriptions_region"]].copy()
    for regle in REGLES:
        m = repartir(eleves, ind["maitres"].to_numpy(float), BUDGET_DE_REFERENCE, regle, accessibles=accessibles)
        s = repartir(eleves, ind["salles"].to_numpy(float), BUDGET_DE_REFERENCE, regle, accessibles=accessibles)
        detail[f"maitres_ajoutes_{regle}"] = m
        detail[f"ratio_maitre_apres_{regle}"] = (eleves / (ind["maitres"] + m)).round(1)
        detail[f"salles_ajoutees_{regle}"] = s
        detail[f"ratio_salle_apres_{regle}"] = (eleves / (ind["salles"] + s)).round(1)
    # Cohérence maîtres-salles : un maître affecté a besoin d'une salle
    apres_m = ind["maitres"] + detail["maitres_ajoutes_egalisation"]
    apres_s = ind["salles"] + detail["salles_ajoutees_egalisation"]
    detail["maitres_sans_salle_apres_egalisation"] = (apres_m - apres_s).clip(lower=0)
    detail.insert(0, "budget_maitres_et_salles", BUDGET_DE_REFERENCE)
    detail = detail.sort_values("eleves_par_maitre", ascending=False)
    detail.to_csv(F_DETAIL, index=False, encoding="utf-8-sig")

    # ---- 3) Horizon 2030 : combien faut-il, et où, selon le scénario ? ----
    besoins = pd.read_csv(F_BESOINS_2030)
    horizon = besoins.groupby("scenario").agg(eleves_projetes=("eleves_projetes", "sum"), maitres_a_ajouter=("maitres_a_ajouter", "sum"),
                                              salles_a_ajouter=("salles_a_ajouter", "sum"),
                                              provinces_en_deficit_maitres=("maitres_a_ajouter", lambda s: int((s > 0).sum()))).reset_index()
    horizon["maitres_par_an_sur_5_ans"] = (horizon["maitres_a_ajouter"] / 5).round(0).astype(int)
    horizon["salles_par_an_sur_5_ans"] = (horizon["salles_a_ajouter"] / 5).round(0).astype(int)
    horizon.to_csv(F_2030, index=False, encoding="utf-8-sig")

    # ---- 4) Sensibilité : que deviennent les constats si le seuil change ? ----
    lignes = []
    for ressource, colonne in [("maitres", "maitres"), ("salles", "salles")]:
        existant = ind[colonne].to_numpy(dtype=float)
        for seuil in SEUILS_TESTES:
            ratio = eleves / existant
            lignes.append({"ressource": ressource, "seuil": seuil, "provinces_au_dessus": int((ratio > seuil).sum()),
                           "deficit_total": unites_necessaires(eleves, existant, seuil),
                           "marge_comptable": int(np.clip(existant - np.ceil(eleves / seuil), 0, None).sum())})
    sensibilite = pd.DataFrame(lignes)
    sensibilite.to_csv(F_SENSIBILITE, index=False, encoding="utf-8-sig")

    # ---- 5) Preuve d'optimalité de la règle d'égalisation, pour l'objectif « réduire le pire ratio » ----
    preuves = []
    for ressource, colonne, budgets in [("maitres", "maitres", BUDGETS_MAITRES), ("salles", "salles", BUDGETS_SALLES)]:
        existant = ind[colonne].to_numpy(dtype=float)
        for budget in budgets:
            ajout = repartir(eleves, existant, budget, "egalisation", accessibles=accessibles)
            p = prouver_optimalite(eleves, existant, ajout, budget)
            p["optimal"] = p["unites_pour_ce_plafond"] <= budget < p["unites_pour_un_plafond_plus_bas"]
            preuves.append({"ressource": ressource, **p})
    preuves = pd.DataFrame(preuves)
    preuves.to_csv(F_PREUVE, index=False, encoding="utf-8-sig")
    assert preuves["optimal"].all(), "La règle d'égalisation n'est pas optimale pour un des budgets : à examiner"

    pd.set_option("display.width", 220)
    print("Comparaison des règles — maîtres (primaire public, seuil de simulation", NORME, "élèves par maître)")
    print(comparaison[comparaison.ressource == "maitres"].drop(columns="ressource").to_string(index=False))
    print(f"\nDétail pour {BUDGET_DE_REFERENCE} maîtres, règle « egalisation » — 10 premières provinces :")
    print(detail[["region", "province", "eleves", "maitres", "eleves_par_maitre", "maitres_ajoutes_egalisation",
                  "ratio_maitre_apres_egalisation", "maitres_ajoutes_proportionnelle"]].head(10).to_string(index=False))
    print(f"\nMaîtres qui n'auraient pas de salle après {BUDGET_DE_REFERENCE} maîtres et {BUDGET_DE_REFERENCE} salles : "
          f"{int(detail['maitres_sans_salle_apres_egalisation'].sum())}")
    print("\nSensibilité au seuil :")
    print(sensibilite.to_string(index=False))
    print("\nPreuve d'optimalité de l'égalisation (pire ratio) :")
    print(preuves.to_string(index=False))
    print("\nHorizon 2029-2030 :")
    print(horizon.to_string(index=False))


if __name__ == "__main__":
    main()
