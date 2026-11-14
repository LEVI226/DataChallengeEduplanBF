"""Objectif V5 : maximiser les franchissements du seuil, sans retirer de stock.

Sous les hypothèses d'ajouts entiers, de coût unitaire identique et d'éligibilité
de toutes les provinces, le tri des déficits entiers croissants est exact pour
le nombre de franchissements : toute sélection de k provinces coûte au moins
la somme des k plus petits déficits. Les égalités suivent l'ordre des entrées.
Le reliquat égalise ensuite les ratios ; ce départage n'est pas revendiqué
comme un optimum conjoint ou lexicographique des deux objectifs.
"""
import math
from fractions import Fraction
from numbers import Integral


def valider(eleves, existant, seuil):
    if len(eleves) == 0 or len(eleves) != len(existant):
        raise ValueError('Tableaux non vides de même longueur attendus')
    if not all(math.isfinite(v) and v >= 0 for v in eleves):
        raise ValueError('Effectifs invalides')
    if not all(math.isfinite(v) and v > 0 and int(v) == v for v in existant):
        raise ValueError('Stocks entiers strictement positifs attendus')
    if not math.isfinite(seuil) or seuil <= 0:
        raise ValueError('Seuil strictement positif attendu')


def unites_plafond(eleves, existant, plafond):
    valider(eleves, existant, plafond)
    return sum(max(0, math.ceil(Fraction(str(e))/Fraction(str(plafond))) - int(s)) for e, s in zip(eleves, existant))


def repartir_seuil(eleves, existant, budget, seuil=50):
    valider(eleves, existant, seuil)
    if isinstance(budget, bool) or not isinstance(budget, Integral) or budget < 0:
        raise ValueError('Budget entier positif ou nul attendu')
    # Les décimales saisies sont traitées exactement : 39420/43.8 exige
    # 900 postes, et non 901 malgré le quotient flottant 900.0000000000001.
    couts = [max(0, math.ceil(Fraction(str(e))/Fraction(str(seuil))) - int(s)) for e, s in zip(eleves, existant)]
    ordre = sorted((i for i, c in enumerate(couts) if c > 0), key=lambda i: (couts[i], i))
    ajout = [0]*len(eleves)
    reste = int(budget)
    completees = 0
    for i in ordre:
        if couts[i] > reste:
            break
        ajout[i] = couts[i]
        reste -= couts[i]
        completees += 1
    seuil_ajout = ajout.copy()
    reliquat = reste
    for _ in range(reste):
        i = max(range(len(eleves)), key=lambda i: eleves[i]/(existant[i]+ajout[i]))
        ajout[i] += 1
    suivant = sum(couts[i] for i in ordre[:completees+1]) if completees < len(ordre) else None
    return {'ajout': ajout, 'ajout_seuil': seuil_ajout,
            'ajout_reliquat': [a-s for a, s in zip(ajout, seuil_ajout)],
            'provinces_ramenees': completees, 'cout_franchissement': int(budget)-reliquat,
            'reliquat': reliquat, 'cout_province_supplementaire': suivant}


def lecture_demographique(inscriptions, population):
    """Rapport descriptif tous âges / population projetée 6–11, pas un TNS.

    L'indicateur reste distinct de la charge des seuls élèves du public.
    Jointure stricte ; aucune imputation, correction ou troncature à 100.
    """
    import pandas as pd
    if inscriptions.province.duplicated().any() or population.province.duplicated().any():
        raise ValueError('Clé province dupliquée')
    if set(inscriptions.province) != set(population.province):
        raise ValueError('Couverture démographique différente des inscriptions')
    d = inscriptions.merge(population, on='province', validate='one_to_one')
    for c in ['eleves_public', 'eleves_prive', 'maitres_public', 'population_6_11_2025']:
        if not pd.to_numeric(d[c], errors='coerce').map(math.isfinite).all() or (d[c] < 0).any():
            raise ValueError(f'Valeur invalide : {c}')
    if (d.population_6_11_2025 <= 0).any() or (d.maitres_public <= 0).any():
        raise ValueError('Population et maîtres strictement positifs attendus')
    d['eleves_total'] = d.eleves_public + d.eleves_prive
    d['inscrits_pour_100_enfants'] = 100*d.eleves_total/d.population_6_11_2025
    d['ratio_charge_public'] = d.eleves_public/d.maitres_public
    d['interpretation'] = 'Tous âges, public + privé / population projetée 6–11 ans ; pas un taux net de scolarisation ; déplacements récents non modélisés'
    return d
