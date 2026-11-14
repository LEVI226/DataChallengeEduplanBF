"""Normaliser sans imputation et vérifier les totaux des deux annuaires."""
from pathlib import Path
import csv,collections,json
BASE=Path(__file__).resolve().parent
rows=list(csv.DictReader((BASE/'cellules_publiees.csv').open()))
for r in rows:r['valeur']=int(r['valeur']) if r['valeur']!='' else None
checks=[]
def check(kind,rs,published,group,expected_count=None):
    available=all(r['valeur'] is not None for r in rs) and published['valeur'] is not None
    complete=expected_count is None or len(rs)==expected_count
    actual=sum(r['valeur'] for r in rs) if available and complete else None
    checks.append(dict(region=published['region'],indicateur=published['indicateur'],controle=kind,territoire=group,statut=published['statut'],calcule=actual if actual is not None else '',publie=published['valeur'] if published['valeur'] is not None else '',ecart=actual-published['valeur'] if actual is not None else '',resultat='non_verifiable' if actual is None else 'conforme' if actual==published['valeur'] else 'alerte',pages_calcul=','.join(sorted({r['page_pdf'] for r in rs},key=int)),page_total=published['page_pdf'],tableau_total=published['tableau']))
# Les cellules d'une même ligne ne sont pas fabriquées lorsqu'une case est vide.
groups=collections.defaultdict(list)
for r in rows:groups[(r['region'],r['indicateur'],r['tableau'],r['territoire'],r['niveau'])].append(r)
for key,rs in groups.items():
    assert len(rs)==3 and {r['statut'] for r in rs}=={'Public','Privé','Ensemble'},key
    check('public_prive_ensemble',[r for r in rs if r['statut']!='Ensemble'],next(r for r in rs if r['statut']=='Ensemble'),key[3],2)
# Les tableaux récapitulatifs donnent les valeurs provinciales de référence.
reference=[r for r in rows if r['niveau']=='commune' or r['portee_table']=='provinces']
keys=[(r['region'],r['indicateur'],r['niveau'],r['province'] if r['niveau']=='commune' else '',r['territoire'],r['statut']) for r in reference]
assert len(reference)==1005 and len(set(keys))==1005
for r in rows:
    if r['niveau']=='province' and r['portee_table']=='communes':
        official=next(x for x in reference if (x['region'],x['indicateur'],x['niveau'],x['territoire'],x['statut'])==(r['region'],r['indicateur'],'province',r['territoire'],r['statut']))
        check('total_province_repris',[r],official,r['territoire'],1)
for reg,expected,nprov in [('Centre-Est',30,3),('Est',27,5)]:
    for ind in ['ecoles','salles','eleves','enseignants','ecoles_fermees_insecurite']:
        subset=[r for r in reference if r['region']==reg and r['indicateur']==ind]
        communes={r['territoire'] for r in subset if r['niveau']=='commune'}
        assert len(communes)==expected,(reg,ind,len(communes))
        for statut in ['Public','Privé','Ensemble']:
            ps=[r for r in subset if r['niveau']=='province' and r['statut']==statut]
            total=next(r for r in subset if r['niveau']=='region' and r['statut']==statut)
            check('somme_provinces',ps,total,reg,nprov)
            for province in ps:
                cs=[r for r in subset if r['niveau']=='commune' and r['province']==province['territoire'] and r['statut']==statut]
                check('somme_communes',cs,province,province['territoire'])
for name,data in [('primaire_communes_provinces_2023_2024.csv',reference),('controles_annuaires.csv',checks)]:
    with (BASE/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
print(json.dumps({'cellules_sources':len(rows),'cellules_reference':len(reference),'communes':57,'controles':len(checks),'resultats':dict(collections.Counter(c['resultat'] for c in checks))},ensure_ascii=False,indent=2))
