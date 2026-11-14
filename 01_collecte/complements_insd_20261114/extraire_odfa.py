"""Convertir les quatre réponses publiques ODFA en CSV sans dépendance tierce.
Depuis ce dossier : python3 extraire_odfa.py
Les dates restent les libellés annuels du portail ; aucune conversion en année
scolaire, correction de valeur ou imputation n'est effectuée.
"""
from pathlib import Path
import csv,json,collections,math
BASE=Path(__file__).resolve().parent
OUT=BASE/'tables';OUT.mkdir(exist_ok=True)
allrows=[];summary=[]
for path in sorted(BASE.glob('ODFA_*_donnees.json')):
    dataset=path.name.split('_')[1]
    obj=json.loads(path.read_text());cols=obj['columns'];raw=obj['data'];n=len(cols)
    assert n>0 and len(raw)%n==0,(dataset,len(raw),n)
    records=[]
    for offset in range(0,len(raw),n):
        cell=raw[offset:offset+n];dims=[];date=None;val=None
        for col,value in zip(cols,cell):
            if col['status']=='Dimension' and col.get('fieldId') is None:dims.append((col['dimensionId'],str(value)))
            elif col['status']=='Date':date=value
            elif col['status']=='Measure':val=value
        assert date and isinstance(date,dict) and date.get('frequency')=='A'
        assert val is None or isinstance(val,(float,int)) and math.isfinite(val)
        row=dict(dataset=dataset,indicateur=obj.get('datasetName',''),date_source=date['value'],annee_libelle=int(date['value'][-4:]),frequence=date['frequency'],dimensions_json=json.dumps(dict(dims),ensure_ascii=False,sort_keys=True),valeur='' if val is None else val,statut_valeur='manquante' if val is None else 'publiee',url='https://burkinafaso.opendataforafrica.org/'+dataset,recupere_le='2026-11-14',statut_validation='portail_public; periode_scolaire_et_definition_a_recouper')
        records.append(row)
    keys=[(r['date_source'],r['dimensions_json']) for r in records]
    assert len(keys)==len(set(keys)),f'Doublons dans {dataset}'
    with (OUT/f'ODFA_{dataset}.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    summary.append(dict(dataset=dataset,observations=len(records),annee_min=min(r['annee_libelle'] for r in records),annee_max=max(r['annee_libelle'] for r in records),valeurs_manquantes=sum(r['statut_valeur']=='manquante' for r in records),url=records[0]['url']))
    allrows+=records
with (OUT/'ODFA_inventaire_series.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
print(json.dumps({'observations':len(allrows),'series':summary},ensure_ascii=False,indent=2))
