"""Sélection explicite des compléments V2 ; aucun parcours récursif du pack."""
from pathlib import Path
import csv,json
WEB='01_collecte/complements_web'
ODFA='01_collecte/complements_insd_20261114'
RAPP='01_collecte/rapprochement_20261114'

def fichiers_complements(root,exiger=True):
    paths={k:[] for k in ['sources','code','01_collecte','02_nettoyage','03_transformation','04_analyse','05_interpretation']}
    def add(group,*names):paths[group].extend(Path(root)/name for name in names)
    add('sources',*[f'{WEB}/INSD_{r}_annuaire2024.pdf' for r in ['CentreNord','CentreEst','Est']],
        f'{WEB}/registre_telechargements.json',f'{ODFA}/ODFA_requetes_selection.json',
        *[f'{ODFA}/ODFA_{s}_donnees.json' for s in ['iiyaoef','cvbkpse','cpjmkh','tyliupe']])
    add('01_collecte',f'{RAPP}/cellules_publiees.csv',f'{RAPP}/registre_sources.json')
    add('code',f'{WEB}/extraire_centre_nord.py',f'{ODFA}/extraire_odfa.py',f'{ODFA}/controler_odfa.py',
        *[f'{RAPP}/{n}.py' for n in ['extraire_annuaires','controler_annuaires','rapprocher_sources','qualifier_communes']])
    add('02_nettoyage',*[f'{WEB}/tables/{n}.csv' for n in ['INSD_CentreNord_primaire_2023_2024','INSD_CentreNord_controles']],
        *[f'{RAPP}/{n}.csv' for n in ['primaire_communes_provinces_2023_2024','controles_annuaires','CNS529_tous_enseignants_2023_2024']],
        *[f'{ODFA}/tables/ODFA_{s}.csv' for s in ['iiyaoef','cvbkpse','cpjmkh','tyliupe','inventaire_series']])
    add('03_transformation',f'{RAPP}/qualite_communes.csv')
    add('04_analyse',f'{RAPP}/rapprochement_ODFA_CNS529_2024.csv',f'{RAPP}/rapprochement_annuaires_regionaux_CNS529.csv',f'{ODFA}/tables/ODFA_controles.csv')
    add('05_interpretation','05_interpretation/EXX_05-interpretation_D3_analyst_synthese-audits_v2.md')
    if exiger:
        missing=[str(p.relative_to(root)) for values in paths.values() for p in values if not p.is_file()]
        if missing:raise ValueError(f'Compléments V2 absents : {missing}')
    return paths

def indicateurs_audit(root):
    def rows(name):return list(csv.DictReader((Path(root)/RAPP/name).open(encoding='utf-8-sig')))
    source=rows('cellules_publiees.csv');clean=rows('primaire_communes_provinces_2023_2024.csv');checks=rows('controles_annuaires.csv');match=rows('rapprochement_ODFA_CNS529_2024.csv');regional=rows('rapprochement_annuaires_regionaux_CNS529.csv')
    return dict(cellules_sources=len(source),cellules=len(clean),communes=len({(r['region'],r['province'],r['territoire']) for r in clean if r['niveau']=='commune'}),conformes=sum(r['resultat']=='conforme' for r in checks),alertes=sum(r['resultat']=='alerte' for r in checks),non_verifiables=sum(r['resultat']=='non_verifiable' for r in checks),rapprochements=len(match),rapprochements_conformes=sum(r['resultat']=='conforme' for r in match),ecarts=[r for r in regional if r['resultat']!='conforme'])

def preparer_synthese(root):
    a=indicateurs_audit(root)
    p=Path(root)/'05_interpretation/EXX_05-interpretation_D3_analyst_synthese-audits_v2.md'
    p.write_text(f'''# Synthèse des audits complémentaires — V2

Périmètre principal conservé : primaire public, 45 anciennes provinces, observations 2024-2025. Aucun complément n'est additionné aux effectifs ou stocks du simulateur.

- ODFA, libellé 2024 / DGESS 2023-2024 : {a['rapprochements_conformes']}/{a['rapprochements']} concordances régionales pour écoles, salles et tous enseignants. Publications pouvant reprendre la même collecte DGESS.
- Annuaire Centre-Est et Est : {a['communes']} communes, {a['cellules']} cellules de référence pour cinq indicateurs 2023-2024 ; {a['conformes']} contrôles conformes, {a['alertes']} alertes et {a['non_verifiables']} relations non vérifiables. La case privée de Bissiga reste vide.
- Trois divergences régionales documentées : salles et tous enseignants du Centre-Nord, total des élèves de l'Est. La DGESS reste la référence nationale.
- Fermetures pour insécurité : contexte historique ; aucun statut actuel de sécurité ni taux de fermeture déduit. Les communes de la Kompienga totalisent 64 contre 36 dans le récapitulatif provincial publié ; les valeurs ne sont pas corrigées.

Les preuves numériques et pages figurent dans les CSV de rapprochement et de contrôles. Les neuf alertes historiques ODFA de la collecte précédente restent non résolues ; le millésime récent ne les valide pas.

Reproduction après extraction des sept ZIP : `python code/12_verifier_complements.py`. Python 3 et Poppler (`pdftotext`) sont nécessaires ; aucune API ni clé. Les trois PDF régionaux sont dans le second ZIP de collecte. Le rapport, limité à 15 pages, porte les conclusions et leurs limites ; les tables conservent les preuves.
''',encoding='utf-8')
    return a
