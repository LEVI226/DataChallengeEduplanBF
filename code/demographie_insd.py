"""Extraction reproductible des 6–11 ans INSD et facteurs provinciaux 2025→2030.

Seul le CSV du pack original est lu : les preuves d'audit ne sont pas des entrées.
Les colonnes de commentaire de collecte ne sont jamais interprétées.
"""
import csv
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

RACINE = Path(__file__).resolve().parents[1]
SOURCE = RACINE / '01_collecte/datapack_extrait/DataPack_DCB_2026/data/02_Demographie_INSD/INSD_RGPH2019_Vol4_Projections_demographiques_2020-2035.csv'
PREFIXE = 'EXX'
F_POPULATION = RACINE / f'02_nettoyage/{PREFIXE}_02-nettoyage_D3_engineer_population-provinces-6-11-insd_v1.csv'
F_CONTROLES = RACINE / f'02_nettoyage/{PREFIXE}_02-nettoyage_D3_engineer_controles-demographie-insd_v1.csv'
F_JOURNAL = RACINE / f'02_nettoyage/{PREFIXE}_02-nettoyage_D3_engineer_journal-demographie-insd_v1.md'
F_FACTEURS = RACINE / f'03_transformation/{PREFIXE}_03-transformation_D3_architect_facteurs-demographiques-insd_v1.csv'
HYPOTHESE = (
    'Correspondance supposée année civile 2025 / scolaire 2024-2025 et 2030 / 2029-2030 ; '
    'rapport inscrits publics / population 6–11 ans constant ou sensibilité ±10 %, '
    'ce rapport ne constitue pas un taux net de scolarisation ; maîtres et salles conservés ; '
    'simulation, pas une prévision validée en contexte de crise.'
)
SCENARIOS_INSD = {'demographie_insd': 1.0, 'demographie_insd_moins10': 0.9, 'demographie_insd_plus10': 1.1}


def normaliser_province(titre):
    """Correspondance vers les libellés de l'annuaire (45 anciennes provinces)."""
    texte = ''.join(c for c in unicodedata.normalize('NFKD', titre.upper()) if not unicodedata.combining(c))
    texte = texte.replace('’', "'")
    texte = re.sub(r'^PROVINCE\s+(?:DE L\'|DE LA |DES |DU |DE )', '', texte)
    texte = ' '.join(texte.split())
    return {'BALES': 'LES BALE', 'KOMONDJOARI': 'KOMONDJARI', 'KOMANDJARI': 'KOMONDJARI',
            'KOURITENGA': 'KOURITTENGA'}.get(texte, texte)


def extraire(lignes, provinces):
    """Lit les triplets H/F/ensemble ; refuse toute perte ou ambiguïté 2025/2030."""
    attendues = set(provinces)
    observations, vues = [], set()
    province, annees, page_precedente = None, [], None
    for r in lignes:
        page = int(r['page'])
        if page < 219:
            continue
        if page != page_precedente:
            annees = []
            page_precedente = page
        cellules = [r.get(f'c{i}', '').strip() for i in range(1, 16)]
        titre = cellules[0]
        if titre.startswith('PROVINCE '):
            province = normaliser_province(titre)
            if province not in attendues:
                raise ValueError(f'Province INSD inconnue : {titre}')
            annees = []
            continue
        entete = [int(c) for c in cellules if re.fullmatch(r'20\d\d', c)]
        if entete and all(c == '' or re.fullmatch(r'20\d\d', c) or "âges" in c.lower() or c.lower() == "groupes" for c in cellules):
            annees = entete
            continue
        if not re.fullmatch(r'6\s*[-–]\s*11\s*ans', titre, flags=re.I):
            continue
        if province is None or not annees:
            raise ValueError(f'Ligne 6–11 sans province/en-tête : page {page}, ligne {r["ligne"]}')
        for i, annee in enumerate(annees):
            if annee not in (2025, 2030):
                continue
            cle = (province, annee)
            if cle in vues:
                raise ValueError(f'Doublon INSD : {cle}')
            valeurs = []
            for c in cellules[1 + 3*i:4 + 3*i]:
                propre = re.sub(r'\s', '', c)
                if not re.fullmatch(r'\d+', propre) or int(propre) <= 0:
                    raise ValueError(f'Population non positive/illisible : {cle}, {c!r}')
                valeurs.append(int(propre))
            if len(valeurs) != 3 or valeurs[0] + valeurs[1] != valeurs[2]:
                raise ValueError(f'Hommes + femmes != ensemble : {cle}')
            observations.append(dict(province=province, annee=annee, hommes=valeurs[0], femmes=valeurs[1],
                                     ensemble=valeurs[2], document=r['document'], page=page, ligne=int(r['ligne'])))
            vues.add(cle)
    manquantes = {(p, a) for p in attendues for a in (2025, 2030)} - vues
    if manquantes:
        raise ValueError(f'Observations INSD manquantes : {sorted(manquantes)}')
    return observations


def facteurs(observations):
    """Facteur sans arrondi intermédiaire et provenance pour chaque année."""
    population = pd.DataFrame(observations)
    if population.duplicated(['province', 'annee']).any() or (population.ensemble <= 0).any():
        raise ValueError('Population non positive ou doublon avant calcul des facteurs')
    morceaux = []
    for annee in (2025, 2030):
        p = population[population.annee == annee].drop(columns='annee').set_index('province')
        p = p.rename(columns={c: f'{c}_{annee}' for c in p.columns})
        morceaux.append(p)
    table = morceaux[0].join(morceaux[1], how='outer')
    if table.isna().any().any():
        raise ValueError('Paire 2025/2030 incomplète')
    table['facteur_demographique'] = table.ensemble_2030 / table.ensemble_2025
    table['hypothese'] = HYPOTHESE
    return table.reset_index()


def projeter_provinces(ind, table_facteurs, scenario, coefficient, annee_cible, seuil_maitres, seuil_salles):
    """Arrondi entier final seulement ; deux seuils de simulation indépendants."""
    if table_facteurs.province.duplicated().any() or set(ind.province) != set(table_facteurs.province):
        raise ValueError('Correspondance des provinces incomplète ou ambiguë')
    p = ind[['region', 'province', 'eleves', 'maitres', 'salles']].copy()
    f = table_facteurs.set_index('province').facteur_demographique
    if not np.isfinite(f).all() or (f <= 0).any():
        raise ValueError('Facteur démographique invalide')
    p['scenario'], p['annee_scolaire'] = scenario, annee_cible
    p['eleves_projetes'] = (p.eleves * p.province.map(f) * coefficient).round().astype(int)
    for ressource, seuil in [('maitres', seuil_maitres), ('salles', seuil_salles)]:
        p[f'besoin_{ressource}'] = np.ceil(p.eleves_projetes / seuil).astype(int)
        p[f'{ressource}_a_ajouter'] = (p[f'besoin_{ressource}'] - p[ressource]).clip(lower=0)
    return p.rename(columns={'eleves': 'eleves_2024_2025'})


def produire_tables(provinces):
    """Extrait le pack et écrit populations, contrôles, facteurs et journal de méthode."""
    with SOURCE.open(encoding='utf-8-sig', newline='') as stream:
        observations = extraire(csv.DictReader(stream, delimiter=';'), provinces)
    population = pd.DataFrame(observations)
    table = facteurs(observations)
    controles = []
    for annee, attendu in [(2025, 4328008), (2030, 4664547)]:
        selection = population[population.annee == annee]
        total = int(selection.ensemble.sum())
        if total != attendu:
            raise ValueError(f'Agrégat national INSD inattendu : {annee} {total} != {attendu}')
        controles.append(dict(controle='somme_provinces_vs_national', annee=annee,
                              observations=len(selection), valeur=total, attendu=attendu, ecart=total-attendu, statut='OK'))
    for chemin in (F_POPULATION, F_FACTEURS): chemin.parent.mkdir(exist_ok=True)
    population.to_csv(F_POPULATION, index=False, encoding='utf-8-sig')
    pd.DataFrame(controles).to_csv(F_CONTROLES, index=False, encoding='utf-8-sig')
    table.to_csv(F_FACTEURS, index=False, encoding='utf-8-sig')
    F_JOURNAL.write_text(
        '# Extraction démographique INSD\n\n'
        'Entrée : CSV UTF-8 du pack, projections RGPH 2019 volume 4, édition janvier 2023. '
        'Parcours à partir de la page PDF 219, titres PROVINCE et en-têtes variables ; '
        'triplets hommes/femmes/ensemble des 6–11 ans. Conservation document/page/ligne.\n\n'
        '90 observations, 45 provinces, années 2025 et 2030. Doublons, trous, provinces inconnues, '
        'valeurs non positives et incohérences H+F sont bloquants dans la sélection. '
        'Agrégats nationaux contrôlés : 4 328 008 et 4 664 547. '
        'L’anomalie connue Oudalan 2031 est hors sélection et ne modifie pas les facteurs.\n\n'
        + HYPOTHESE + '\n\nFormule : inscrits publics 2024-2025 × population 2030 / population 2025 '
        '× coefficient (1 ; 0,9 ; 1,1), arrondi entier final. '
        'Les sensibilités ne forment pas un intervalle de confiance.\n', encoding='utf-8')
    return table
