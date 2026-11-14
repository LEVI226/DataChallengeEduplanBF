"""Contrôles des séries ODFA ; les alertes ne corrigent jamais les sources."""
from pathlib import Path
import csv,json,collections
BASE=Path(__file__).resolve().parent/'tables'
checks=[]
def lire(id):
    return [dict(annee=int(r['annee_libelle']),dimensions=json.loads(r['dimensions_json']),valeur=float(r['valeur'])) for r in csv.DictReader((BASE/f'ODFA_{id}.csv').open())]
def control(id,year,type,group,computed,published,complet=True,tolerance=0):
    checks.append(dict(dataset=id,annee=year,controle=type,groupe=group,calcule=computed,publie=published,ecart=computed-published if computed is not None else '',statut='non_verifiable_couverture' if not complet else 'conforme' if abs(computed-published)<=tolerance else 'alerte'))
for id,geokey,otherkey in [('tyliupe','régions','sexe'),('cvbkpse','region','rubrique')]:
    records=lire(id);grouped=collections.defaultdict(list)
    for r in records:grouped[(r['annee'],r['dimensions'][otherkey])].append(r)
    for (year,other),rs in sorted(grouped.items()):
        national=[r for r in rs if r['dimensions'][geokey]=='Burkina Faso'];regional=[r for r in rs if r['dimensions'][geokey]!='Burkina Faso']
        if national:control(id,year,'somme_13_regions',other,sum(r['valeur'] for r in regional),national[0]['valeur'],len(regional)==13)
    if id=='tyliupe':
        sexes=collections.defaultdict(dict)
        for r in records:sexes[(r['annee'],r['dimensions'][geokey])][r['dimensions']['sexe']]=r['valeur']
        for (year,geo),values in sorted(sexes.items()):
            if all(k in values for k in ['Hommes','Femmes','Ensemble']):control(id,year,'hommes_femmes_ensemble',geo,values['Hommes']+values['Femmes'],values['Ensemble'])
quality=collections.defaultdict(dict)
for r in lire('cpjmkh'):quality[(r['annee'],r['dimensions']['niveau'])][r['dimensions']['taux']]=r['valeur']
for (year,level),values in sorted(quality.items()):
    if len(values)==3:control('cpjmkh',year,'promotion_redoublement_abandon',level,sum(values.values()),100,tolerance=0.2)
with (BASE/'ODFA_controles.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(checks[0]));w.writeheader();w.writerows(checks)
print(json.dumps({'controles':len(checks),'statuts':dict(collections.Counter(c['statut'] for c in checks)),'alertes_2024':[c for c in checks if c['annee']==2024 and c['statut']=='alerte']},ensure_ascii=False,indent=2))
