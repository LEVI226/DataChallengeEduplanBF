"""Préparer 20 lignes de contrôle humain, sans remplir leur validation."""
from pathlib import Path
import csv,hashlib

def preparer(root):
    root=Path(root);source=root/'02_nettoyage/EXX_02-nettoyage_D3_engineer_primaire-provinces-statut_v1.csv'
    out=root/'documentation/FICHE_CONTROLE_HUMAIN_v3.csv';notice=out.with_suffix('.md')
    if out.exists():return out  # Ne jamais écraser une fiche que l’équipe peut avoir remplie.
    rows=list(csv.DictReader(source.open(encoding='utf-8-sig')))
    selected=[];keys=set();regions=set()
    def add(r):
        k=(r['annee_scolaire'],r['province'],r['statut'])
        if k not in keys:keys.add(k);selected.append(r)
    for r in rows:
        if r['niveau']=='province' and r['annee_scolaire']=='2024-2025' and r['statut']=='Public' and r['region'] not in regions:
            regions.add(r['region']);add(r)
    for name in ['LOROUM','YAGHA','KADIOGO','BAM','SOUM','TAPOA']:
        add(next(r for r in rows if r['niveau']=='province' and r['annee_scolaire']=='2024-2025' and r['statut']=='Public' and r['province']==name))
    for r in rows:
        if len(selected)>=20:break
        if r['niveau']=='province' and (r['statut']!='Public' or r['annee_scolaire']=='2023-2024'):add(r)
    selected=selected[:20];assert len(selected)==20
    records=[]
    for i,r in enumerate(selected,1):
        record=dict(id_controle=f'C{i:02d}',annee_scolaire=r['annee_scolaire'],region=r['region'],province=r['province'],statut=r['statut'],document_pdf=r['source_document'],page_pdf=r['source_page'],tableau='I.1',ecoles_attendu=r['ecoles'],salles_attendu=r['salles'],maitres_charges_cours_attendu=r['maitres_charges_cours'],eleves_attendu=r['eleves'],ratio_eleves_maitre_attendu=r['ratio_eleves_maitre_publie'],statut_controle_humain='NON_VERIFIE',constat_pdf_a_remplir='',role_verificateur_a_remplir='',date_verification_a_remplir='',correction_ou_commentaire_a_remplir='')
        records.append(record)
    with out.open('x',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
    notice.write_text('''# Fiche de contrôle humain à compléter — V3

Cette fiche n’atteste aucune vérification réalisée. Les 20 lignes sont des références à comparer manuellement avec les PDF originaux des annuaires DGESS, tableau I.1. Elle couvre les 13 régions, les provinces à forte charge et quelques lignes d’autres statuts ou années.

1. Extraire les sept ZIP ; retrouver le PDF indiqué dans `01_collecte/datapack_extrait/DataPack_DCB_2026`.
2. Ouvrir la page physique indiquée, compter depuis 1 ; vérifier année, province et statut avant les chiffres.
3. Comparer écoles, salles, maîtres chargés de cours, élèves et ratio publié. Noter le constat réellement lu dans le PDF.
4. Remplacer NON_VERIFIE par CONFORME ou ECART uniquement après lecture. Indiquer un rôle ou « personne A/B », la date et les écarts ; aucun nom de membre dans le fichier à déposer.
5. Corriger les données ou expliquer les divergences avant toute affirmation de contrôle réussi ; relancer les contrôles concernés, puis reconstruire la livraison.

Déclaration à renseigner par l’équipe après exécution :
- Date : ___ ; rôles des deux personnes : ___
- Lignes réellement relues : ___ sur 20 ; cellules : ___
- Conformes : ___ ; écarts : ___ ; corrections et contrôles relancés : ___

La génération de cette fiche et les contrôles automatiques n’ont pas valeur de validation humaine. Le rapport et la déclaration IA ne seront actualisés sur ce point qu’après confirmation des contrôles réellement effectués.

Les versions internes _v1 désignent les calculs et données inchangés. V3 désigne la version du rapport et de la livraison ; ce n’est pas une nouvelle collecte.
''',encoding='utf-8')
    return out

if __name__=='__main__':print(preparer(Path(__file__).resolve().parents[1]).name)
